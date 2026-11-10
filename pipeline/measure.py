"""Step 2 of the AI pipeline: street photos -> sidewalk widths + objects on the map. No human input.

For each photo (360 panoramas are first cut into two side views, one facing each sidewalk):
  1. Mask2Former (Mapillary Vistas classes) labels every pixel: sidewalk, curb, road, pole, car, ...
  2. MoGe-2 estimates a metric 3D point for every pixel (metres, camera frame).
  3. RANSAC fits the ground plane on road+sidewalk pixels -> camera height (quality check).
  4. Sidewalk pixels are dropped onto the ground plane (bird's-eye grid). Each connected sidewalk
     patch is measured: its long axis = street direction; width = extent across it, per 1 m slice,
     only within 2-12 m of the camera (accuracy falls with distance).
  5. Objects (poles, lights, bins, cars, motorcycles, ...) = connected pixel blobs; their ground-contact
     point is projected to 3D and flagged on/off sidewalk.
  6. Camera position + heading from Mapillary place everything on the map (UTM).

Usage (AI environment):
    python measure.py --area-dir ~/sidewalk-data/dc_adams_morgan [--limit 50] [--debug 5]
Writes <area-dir>/outputs/width_samples.geojson, objects_raw.geojson, per_view.csv
"""
import argparse
import csv
import json
import math
import os
import sys
import time

import cv2
import numpy as np
import torch
from PIL import Image
from scipy import ndimage

SEG_MODEL = "facebook/mask2former-swin-large-mapillary-vistas-semantic"
DEPTH_MODEL = "Ruicheng/moge-2-vitl-normal"
WORK_W = 1024             # perspective photos are resized to this width
CROP = dict(w=1024, h=768, fov=100.0, pitch=-15.0)   # side views cut from panoramas
GRID = 0.05               # metres per bird's-eye cell
RANGE = (2.0, 12.0)       # measure only this close to the camera (metres, horizontal)
SLICE = 1.0               # metres per width slice
MIN_PATCH_M2 = 1.5        # ignore sidewalk patches smaller than this

# Mask2Former Vistas (v1.2, 65 classes) label names -> our classes
GROUND = {"Road", "Sidewalk", "Crosswalk - Plain", "Lane Marking - Crosswalk", "Curb Cut", "Parking",
          "Bike Lane", "Service Lane", "Pedestrian Area", "Lane Marking - General", "Manhole", "Catch Basin", "Pothole"}
SIDEWALK = {"Sidewalk", "Curb Cut", "Pedestrian Area"}
ROAD = {"Road", "Crosswalk - Plain", "Lane Marking - Crosswalk", "Parking", "Bike Lane", "Service Lane",
        "Lane Marking - General", "Manhole", "Catch Basin", "Pothole"}
CURB = {"Curb"}
SW_PLANE = "foot"         # sidewalk-plane tilt fix: "foot" = on-foot photos only (DC test: helps on-foot, hurts panoramas),
                          # "all" = every photo (--sw-plane-pano), "off" = never (--no-sw-plane)
OBJECTS = {  # model label -> pipeline object class (names match the pilot's obstruction types where possible)
    "Pole": "utility_pole", "Utility Pole": "utility_pole", "Street Light": "street_light",
    "Traffic Sign Frame": "sign_post", "Trash Can": "bin", "Bench": "bench", "Fire Hydrant": "fire_hydrant",
    "Junction Box": "cabinet", "Mailbox": "mailbox", "Phone Booth": "kiosk", "Bike Rack": "bike_rack",
    "Car": "parked_car", "Motorcycle": "parked_motorcycle", "Bicycle": "bicycle", "Truck": "truck",
    "Fence": "barrier", "Barrier": "barrier", "Billboard": "billboard",
}
THIN_OBJECTS = {"utility_pole", "street_light", "sign_post", "fire_hydrant", "bike_rack"}


# ----------------------------------------------------------------------------- image helpers
def equirect_to_persp(eq, yaw_deg, pitch_deg, fov_deg, out_w, out_h):
    """Cut a pinhole view out of an equirectangular panorama. yaw 0 = panorama centre, +90 = right."""
    H, W = eq.shape[:2]
    f = out_w / 2 / math.tan(math.radians(fov_deg) / 2)
    u, v = np.meshgrid(np.arange(out_w) - out_w / 2 + 0.5, np.arange(out_h) - out_h / 2 + 0.5)
    d = np.stack([u / f, v / f, np.ones_like(u)], -1)            # x right, y down, z forward
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    p, y = math.radians(pitch_deg), math.radians(yaw_deg)
    Rx = np.array([[1, 0, 0], [0, math.cos(p), math.sin(p)], [0, -math.sin(p), math.cos(p)]])  # pitch down = negative
    Ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    d = d @ (Ry @ Rx).T
    lon = np.arctan2(d[..., 0], d[..., 2])
    lat = np.arcsin(np.clip(-d[..., 1], -1, 1))
    mx = ((lon / (2 * math.pi) + 0.5) * W).astype(np.float32)
    my = ((0.5 - lat / math.pi) * H).astype(np.float32)
    return cv2.remap(eq, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)


def views_for(img_path, is_pano, center_deg=None, travel_deg=None):
    """Yield (view_name, PIL image, compass direction of the view) for one photo.
    Panoramas: the image centre faces center_deg (Mapillary computed_compass_angle); two side views are cut
    at travel +-90 deg so each looks straight at one sidewalk."""
    im = Image.open(img_path).convert("RGB")
    if is_pano:
        eq = np.asarray(im)
        for name, off in (("left", -90.0), ("right", 90.0)):
            view_dir = (travel_deg + off) % 360
            yaw = (view_dir - center_deg + 180) % 360 - 180
            yield name, Image.fromarray(equirect_to_persp(eq, yaw, CROP["pitch"], CROP["fov"], CROP["w"], CROP["h"])), view_dir
    else:
        if im.width > WORK_W:
            im = im.resize((WORK_W, round(im.height * WORK_W / im.width)), Image.BILINEAR)
        yield "front", im, center_deg


# ----------------------------------------------------------------------------- geometry helpers
def utm_epsg(lon, lat):
    return (32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1


def fit_plane(pts, iters=300, thresh=0.04, rng=np.random.default_rng(0)):
    """RANSAC plane n.x + d = 0, oriented so the camera (origin) is on the positive side."""
    if len(pts) < 200:
        return None
    pts = np.asarray(pts, dtype=np.float64)
    sub = pts[rng.choice(len(pts), 20000, replace=False)] if len(pts) > 20000 else pts   # hypothesis scoring
    best_n, best_c, best_in = None, None, 0
    for _ in range(iters):
        s = sub[rng.integers(0, len(sub), 3)]
        n = np.cross(s[1] - s[0], s[2] - s[0])
        nn = np.linalg.norm(n)
        if nn < 1e-6:
            continue
        n /= nn
        cnt = int((np.abs(sub @ n - n @ s[0]) < thresh).sum())
        if cnt > best_in:
            best_in, best_n, best_c = cnt, n, s[0]
    if best_n is None:
        return None
    best = np.abs(pts @ best_n - best_n @ best_c) < thresh
    p = pts[best]
    c = p.mean(0)
    n = np.linalg.eigh(np.cov((p - c).T))[1][:, 0]        # smallest-variance direction = plane normal
    d = -n @ c
    if d < 0:
        n, d = -n, -d
    return n, d, best.sum() / len(pts)


def fit_image_line(us, vs, iters=200, tol=2.5, min_inliers=60, min_span=120, rng=np.random.default_rng(3)):
    """RANSAC straight line through boundary pixels; returns its two end points (u, v) spanning the inliers."""
    if len(us) < min_inliers:
        return None
    P = np.c_[us, vs]
    if len(P) > 6000:
        P = P[rng.choice(len(P), 6000, replace=False)]
    best, best_n = None, 0
    for _ in range(iters):
        a, b = P[rng.integers(0, len(P), 2)]
        dv = b - a
        L = np.hypot(*dv)
        if L < 20:
            continue
        nrm = np.array([-dv[1], dv[0]]) / L
        inl = np.abs((P - a) @ nrm) < tol
        cnt = int(inl.sum())
        if cnt > best_n:
            best_n, best = cnt, inl
    if best is None or best_n < min_inliers:
        return None
    Q = P[best]
    c = Q.mean(0)
    _, _, vt = np.linalg.svd(Q - c, full_matrices=False)
    dirv = vt[0]
    t = (Q - c) @ dirv
    if t.max() - t.min() < min_span:
        return None
    return tuple(c + dirv * t.min()), tuple(c + dirv * t.max())


def sidewalk_widths(x, y, prior_deg):
    """x = right, y = forward (metres on the ground plane, camera at 0,0).
    Returns width samples for each connected sidewalk patch."""
    if len(x) < 100:
        return []
    gx = np.floor(x / GRID).astype(int)
    gy = np.floor(y / GRID).astype(int)
    ox, oy = gx.min(), gy.min()
    grid = np.zeros((gy.max() - oy + 1, gx.max() - ox + 1), bool)
    grid[gy - oy, gx - ox] = True
    grid = ndimage.binary_closing(grid, iterations=3)          # fill gaps from sparse far points
    lab, k = ndimage.label(ndimage.binary_dilation(grid, iterations=4))
    out = []
    for ci in range(1, k + 1):
        cy, cx = np.nonzero((lab == ci) & grid)
        if len(cx) * GRID * GRID < MIN_PATCH_M2:
            continue
        P = np.c_[(cx + ox + 0.5) * GRID, (cy + oy + 0.5) * GRID]   # (x, y) cell centres
        c = P.mean(0)
        ev, evec = np.linalg.eigh(np.cov((P - c).T))
        major = evec[:, 1]
        elong = math.sqrt(ev[1] / max(ev[0], 1e-9))
        prior = np.array([math.sin(math.radians(prior_deg)), math.cos(math.radians(prior_deg))])
        ang = math.degrees(math.acos(min(1.0, abs(major @ prior))))
        axis = prior        # street direction = direction of travel (known); wedge-shaped patches seen
                            # between parked cars would mislead a shape-based estimate
        perp = np.array([axis[1], -axis[0]])
        u = (P - c) @ axis
        v = (P - c) @ perp
        ub = np.floor(u / SLICE).astype(int)
        for b in np.unique(ub):
            sel = ub == b
            vs = v[sel]
            if len(vs) < 20:
                continue
            # occupied cells across the street axis; keep the longest contiguous run (gaps <= 0.15 m bridged)
            cells_v = np.unique(np.floor(vs / GRID).astype(int))
            runs, start, prev = [], cells_v[0], cells_v[0]
            for cv_ in cells_v[1:]:
                if cv_ - prev > 3:
                    runs.append((start, prev))
                    start = cv_
                prev = cv_
            runs.append((start, prev))
            lo, hi = max(runs, key=lambda r: r[1] - r[0])
            v_lo, v_hi = lo * GRID, (hi + 1) * GRID
            width = v_hi - v_lo
            if not (0.4 <= width <= 10):
                continue
            n_in = np.sum((cells_v >= lo) & (cells_v <= hi))
            filled = n_in * GRID / width
            mid = c + ((b + 0.5) * SLICE) * axis + ((v_lo + v_hi) / 2) * perp
            dist = float(np.hypot(*mid))
            if not (RANGE[0] <= dist <= RANGE[1]):
                continue
            out.append({"right_m": round(float(mid[0]), 3), "fwd_m": round(float(mid[1]), 3), "width_m": round(float(width), 3),
                        "filled_frac": round(float(filled), 3), "n_runs": len(runs), "dist_m": round(dist, 2),
                        "patch_elong": round(elong, 2), "axis_from_prior_deg": round(ang, 1)})
    return out


# ----------------------------------------------------------------------------- models
class Models:
    def __init__(self, device):
        from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation
        from moge.model.v2 import MoGeModel
        self.device = device
        self.seg_proc = AutoImageProcessor.from_pretrained(SEG_MODEL)
        self.seg = Mask2FormerForUniversalSegmentation.from_pretrained(SEG_MODEL).to(device).eval().half()
        self.id2label = {int(k): v for k, v in self.seg.config.id2label.items()}
        self.depth = MoGeModel.from_pretrained(DEPTH_MODEL).to(device).eval()

    def ids(self, names):
        return [i for i, n in self.id2label.items() if n in names]

    @torch.inference_mode()
    def segment(self, img):
        inp = self.seg_proc(images=img, return_tensors="pt").to(self.device)
        inp["pixel_values"] = inp["pixel_values"].half()
        out = self.seg(**inp)
        return self.seg_proc.post_process_semantic_segmentation(out, target_sizes=[img.size[::-1]])[0].cpu().numpy()

    @torch.inference_mode()
    def points(self, img, fov_x=None):
        t = torch.tensor(np.asarray(img) / 255.0, dtype=torch.float32, device=self.device).permute(2, 0, 1)
        out = self.depth.infer(t, fov_x=fov_x)
        K = out["intrinsics"].cpu().numpy().astype(np.float64).copy()   # normalised -> pixels
        K[0] *= img.width
        K[1] *= img.height
        return out["points"].cpu().numpy(), out["mask"].cpu().numpy().astype(bool), K


# ----------------------------------------------------------------------------- per-view measurement
def measure_view(img, lab, pts, valid, M, K, debug_path=None, prior_deg=0.0, sw_plane=True):
    """prior_deg: street direction in the view (0 = straight ahead, 90 = left-right).
    Geometry: the depth model only provides the ground plane's orientation and the camera height;
    every ground pixel is then placed exactly by intersecting its viewing ray with that plane
    (inverse perspective mapping). Sidewalk pixels use the sidewalk plane (raised by the curb height)."""
    ground = np.isin(lab, M.ids(GROUND)) & valid
    road = np.isin(lab, M.ids(ROAD)) & valid
    side = np.isin(lab, M.ids(SIDEWALK)) & valid
    res = {"widths": [], "objects": [], "cam_height": None, "curb_h": None, "status": "ok"}
    if ground.sum() < 2000:
        res["status"] = "little_ground_visible"
        return res
    g = pts[road] if road.sum() > 3000 else pts[ground]
    if len(g) > 20000:
        g = g[np.random.default_rng(1).choice(len(g), 20000, replace=False)]
    pl = fit_plane(g)
    if pl is None:
        res["status"] = "no_plane"
        return res
    n, d, _ = pl
    res["cam_height"] = round(float(d), 3)
    if not (0.8 <= d <= 4.0):
        res["status"] = "implausible_camera_height"
        return res
    curb = 0.12
    if side.sum() > 1500:
        est = d - float(np.median(-(pts[side] @ n)))
        if 0.02 <= est <= 0.30:
            curb = est
    res["curb_h"] = round(curb, 3)
    d_sw = d - curb
    n_sw = n
    if sw_plane and side.sum() > 3000:
        # fit the sidewalk's own plane: the road is crowned / the street may slope, so the road plane
        # raised by the curb height can be tilted relative to the sidewalk. Accept only a plausible plane.
        sp = pts[side]
        sp = sp[np.linalg.norm(sp, axis=1) < 12]
        if len(sp) > 2000:
            if len(sp) > 20000:
                sp = sp[np.random.default_rng(2).choice(len(sp), 20000, replace=False)]
            pl2 = fit_plane(sp, thresh=0.03)
            if pl2 is not None:
                n2, d2, frac2 = pl2
                ang = math.degrees(math.acos(min(1.0, abs(float(n2 @ n)))))
                if ang <= 6.0 and frac2 >= 0.5 and 0.7 * d <= d2 <= d:
                    n_sw, d_sw = n2, float(d2)
                    res["sw_tilt_deg"] = round(ang, 2)
    fwd = np.array([0.0, 0.0, 1.0]) - n[2] * n
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, n)
    fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]

    def ipm(vs, us, dist):
        """pixels -> (right, forward) metres on the plane at distance `dist` below the camera
        (the sidewalk plane uses its own normal when one was fitted)."""
        nn = n_sw if (dist == d_sw and dist != d) else n
        R = np.stack([(us + 0.5 - cx) / fx, (vs + 0.5 - cy) / fy, np.ones(len(us))], -1)
        den = R @ nn
        ok = den < -1e-3
        t = np.where(ok, -dist / np.where(ok, den, -1), np.nan)
        X = R * t[:, None]
        return X @ right, X @ fwd, ok

    if side.sum() >= 800:
        vs, us = np.nonzero(side)
        sx, sy, ok = ipm(vs, us, d_sw)
        r = np.hypot(sx, sy)
        k = ok & (r < RANGE[1] + 3)
        res["widths"] = sidewalk_widths(sx[k], sy[k], prior_deg)
        if debug_path:
            np.savez_compressed(debug_path.replace(".jpg", ".npz"), sx=sx[k].astype(np.float32), sy=sy[k].astype(np.float32),
                                cam_h=d, widths=json.dumps(res["widths"]))
    if not res["widths"] and side.sum() < 800:
        res["status"] = "no_sidewalk_visible"

    # semantic ground points for multi-view fusion: 1 sidewalk, 2 road, 3 grass/soil (every 2nd pixel)
    terrain = np.isin(lab, M.ids({"Terrain"})) & valid
    bev = []
    for code, mask, dist in ((1, side, d_sw), (2, road, d), (3, terrain, d_sw)):
        vs, us = np.nonzero(mask[::2, ::2])
        if len(vs) == 0:
            continue
        bx, by, ok = ipm(vs * 2.0, us * 2.0, dist)
        rr = np.hypot(bx, by)
        keep = ok & (rr >= 1.5) & (rr <= 14)
        bev.append(np.c_[bx[keep], by[keep], np.full(keep.sum(), code)])
    # building fronts: where a building / wall / fence meets the ground (code 4) -> used to correct GPS shifts
    bld = np.isin(lab, M.ids({"Building", "Wall", "Fence"})) & valid
    sup = np.isin(lab, M.ids(SIDEWALK | {"Terrain", "Curb"})) & valid
    base = bld[:-3] & sup[3:]
    rows_b, cols_b = [], []
    for c in range(0, lab.shape[1], 3):
        rr = np.nonzero(base[:, c])[0]
        if len(rr):
            rows_b.append(rr.max())
            cols_b.append(c)
    if rows_b:
        bx, by, ok = ipm(np.array(rows_b, float), np.array(cols_b, float), d_sw)
        rr = np.hypot(bx, by)
        keep = ok & (rr >= 1.5) & (rr <= 20)
        bev.append(np.c_[bx[keep], by[keep], np.full(keep.sum(), 4)])
    # straight sidewalk edges fitted in the IMAGE: a straight edge on the ground is a straight line in the
    # photo, so the pieces seen on both sides of a parked car define one line (5 = curb side, 6 = back side)
    if side.sum() > 1500:
        roadlike = np.isin(lab, M.ids(ROAD | CURB)) & valid
        backlike = np.isin(lab, M.ids({"Building", "Wall", "Fence", "Terrain"})) & valid
        for code, other in ((5, roadlike), (6, backlike)):
            bnd = side & ndimage.binary_dilation(other, iterations=2)
            vs, us = np.nonzero(bnd)
            line = fit_image_line(us.astype(float), vs.astype(float))
            if line is None:
                continue
            (u0, v0), (u1, v1) = line
            tt = np.linspace(0, 1, 25)
            lx, ly, ok = ipm(v0 + (v1 - v0) * tt, u0 + (u1 - u0) * tt, d_sw)
            rr = np.hypot(lx, ly)
            keep = ok & (rr >= 1.0) & (rr <= 15)
            if keep.sum() >= 8:
                bev.append(np.c_[lx[keep], ly[keep], np.full(keep.sum(), code)])
    res["bev"] = np.concatenate(bev).astype(np.float32) if bev else np.zeros((0, 3), np.float32)

    support = np.isin(lab, M.ids(GROUND | CURB | {"Terrain"}))
    for vname, cls in OBJECTS.items():
        ids = M.ids({vname})
        mask = np.isin(lab, ids) & valid
        if mask.sum() < 120:
            continue
        comp, nc = ndimage.label(mask)
        for ci, sl in enumerate(ndimage.find_objects(comp), start=1):
            if sl is None:
                continue
            ys, xs = np.nonzero(comp[sl] == ci)
            if len(ys) < 120:
                continue
            ys = ys + sl[0].start
            xs = xs + sl[1].start
            ymax = ys.max()
            base_cols = xs[ys >= ymax - 3]
            u0 = float(np.median(base_cols))
            # base must touch the ground: pixels just below it are ground/curb/terrain, not a car or the image edge
            y_below = min(lab.shape[0] - 1, ymax + 4)
            xa, xb = int(base_cols.min()), int(base_cols.max()) + 1
            if ymax >= lab.shape[0] - 3 or support[y_below, xa:xb].mean() < 0.5:
                continue
            y0, y1 = min(lab.shape[0] - 1, ymax + 2), min(lab.shape[0], ymax + 25)
            x0, x1 = max(0, xs.min() - 10), min(lab.shape[1], xs.max() + 10)
            on_sw = bool(side[y0:y1, x0:x1].size and side[y0:y1, x0:x1].mean() > 0.3)
            ox, oy, ok = ipm(np.array([ymax]), np.array([u0]), d_sw if on_sw else d)
            if not ok[0] or not (1.0 < math.hypot(ox[0], oy[0]) < 20):
                continue
            bx, by, bok = ipm(np.full(len(base_cols), ymax), base_cols.astype(float), d_sw if on_sw else d)
            res["objects"].append({"cls": cls, "right_m": round(float(ox[0]), 2), "fwd_m": round(float(oy[0]), 2),
                                   "on_sidewalk": on_sw, "pixels": int(len(ys)),
                                   "footprint_m": round(float(np.hypot(np.ptp(bx[bok]), np.ptp(by[bok]))) if bok.any() else 0.0, 2)})
    if debug_path:
        a = np.asarray(img).astype(float)
        a[side] = a[side] * 0.4 + np.array([255, 200, 0]) * 0.6
        road = np.isin(lab, M.ids(ROAD)) & valid
        a[road] = a[road] * 0.6 + np.array([80, 80, 255]) * 0.4
        obj = np.isin(lab, M.ids(set(OBJECTS))) & valid
        a[obj] = a[obj] * 0.4 + np.array([255, 0, 0]) * 0.6
        im = Image.fromarray(a.astype(np.uint8))
        from PIL import ImageDraw
        dr = ImageDraw.Draw(im)
        dr.text((10, 10), f"cam h={res['cam_height']}  widths: " + ", ".join(f"{w['width_m']:.2f}" for w in res["widths"][:8]), fill=(255, 255, 255))
        im.save(debug_path)
    return res


# ----------------------------------------------------------------------------- georeferencing
def travel_bearings(meta):
    """Direction of travel per photo = bearing to the next (or from the previous) photo in its sequence."""
    from collections import defaultdict
    seqs = defaultdict(list)
    for f in meta:
        seqs[f["properties"].get("sequence")].append(f)
    out = {}
    for fs in seqs.values():
        fs.sort(key=lambda f: f["properties"]["captured_at"] or "")
        for i, f in enumerate(fs):
            for a, b in ((f, fs[i + 1] if i + 1 < len(fs) else None), (fs[i - 1] if i else None, f)):
                if a is None or b is None:
                    continue
                (x1, y1), (x2, y2) = a["geometry"]["coordinates"], b["geometry"]["coordinates"]
                dx = (x2 - x1) * math.cos(math.radians(y1)) * 111320
                dy = (y2 - y1) * 111320
                if 2 < math.hypot(dx, dy) < 60:
                    out[f["properties"]["id"]] = math.degrees(math.atan2(dx, dy)) % 360
                    break
    return out


def to_world(cam_e, cam_n, heading_deg, fwd, right):
    h = math.radians(heading_deg)  # compass: 0 = north, clockwise
    return cam_e + fwd * math.sin(h) + right * math.cos(h), cam_n + fwd * math.cos(h) - right * math.sin(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--debug", type=int, default=0, help="save overlay images for the first N views")
    ap.add_argument("--panos-only", action="store_true")
    ap.add_argument("--no-sw-plane", action="store_true", help="sidewalk = road plane raised by the curb (old behaviour)")
    ap.add_argument("--sw-plane-pano", action="store_true", help="also apply the sidewalk-plane tilt fix to panoramas")
    ap.add_argument("--cam-height", type=float, default=0.0, help="known rig height in metres (0 = use per-sequence median estimate)")
    a = ap.parse_args()
    global SW_PLANE
    SW_PLANE = "off" if a.no_sw_plane else ("all" if a.sw_plane_pano else "foot")
    from pyproj import Transformer

    area = os.path.expanduser(a.area_dir)
    meta = json.load(open(os.path.join(area, "imagery", "images.geojson"), encoding="utf-8"))["features"]
    meta = [f for f in meta if os.path.exists(os.path.join(area, "imagery", "jpg", f"{f['properties']['id']}.jpg"))]
    if a.panos_only:
        meta = [f for f in meta if f["properties"].get("is_pano")]
    if a.limit:
        meta = meta[: a.limit]
    out_dir = os.path.join(area, "outputs")
    dbg_dir = os.path.join(out_dir, "debug")
    bev_dir = os.path.join(out_dir, "bev")
    os.makedirs(dbg_dir, exist_ok=True)
    os.makedirs(bev_dir, exist_ok=True)
    lon0, lat0 = meta[0]["geometry"]["coordinates"]
    epsg = utm_epsg(lon0, lat0)
    fwd_t = Transformer.from_crs(4326, epsg, always_xy=True)
    inv_t = Transformer.from_crs(epsg, 4326, always_xy=True)

    travel = travel_bearings(meta)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{len(meta)} photos ({sum(bool(f['properties'].get('is_pano')) for f in meta)} panoramas) | {dev} | EPSG:{epsg}")
    M = Models(dev)
    widths, objects, log = [], [], []
    t0, n_views = time.time(), 0
    from concurrent.futures import ThreadPoolExecutor

    def prep(f):
        p_ = f["properties"]
        h_ = p_.get("computed_compass_angle") if p_.get("computed_compass_angle") is not None else p_.get("compass_angle")
        if h_ is None:
            return None
        tb_ = travel.get(p_["id"], p_.get("compass_angle") if p_.get("compass_angle") is not None else h_)
        return list(views_for(os.path.join(area, "imagery", "jpg", f"{p_['id']}.jpg"), p_.get("is_pano"), h_, tb_))

    pool = ThreadPoolExecutor(2)
    futures = [pool.submit(prep, f) for f in meta[:3]]
    for i, f in enumerate(meta):
        if i + 3 < len(meta):
            futures.append(pool.submit(prep, meta[i + 3]))
        prepared = futures[i].result()
        p = f["properties"]
        heading = p.get("computed_compass_angle") if p.get("computed_compass_angle") is not None else p.get("compass_angle")
        lon, lat = f["geometry"]["coordinates"]
        ce, cn = fwd_t.transform(lon, lat)
        path = os.path.join(area, "imagery", "jpg", f"{p['id']}.jpg")
        if heading is None:
            continue
        tb = travel.get(p["id"], p.get("compass_angle") if p.get("compass_angle") is not None else heading)
        for vname, img, view_dir in (prepared or []):
            n_views += 1
            try:
                lab = M.segment(img)
                pts, valid, K = M.points(img, fov_x=CROP["fov"] if vname in ("left", "right") else None)
                r = measure_view(img, lab, pts, valid, M, K,
                                 os.path.join(dbg_dir, f"{p['id']}_{vname}.jpg") if n_views <= a.debug else None,
                                 prior_deg=90.0 if vname in ("left", "right") else 0.0,
                                 sw_plane=SW_PLANE == "all" or (SW_PLANE == "foot" and not p.get("is_pano")))
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                r = {"status": "oom", "widths": [], "objects": [], "cam_height": None}
            common = {"image_id": p["id"], "view": vname, "is_pano": bool(p.get("is_pano")), "sequence": p.get("sequence"),
                      "captured_at": p.get("captured_at"), "cam_height_est": r.get("cam_height")}
            for items, store in ((r["widths"], widths), (r["objects"], objects)):
                for it in items:
                    store.append({"ce": ce, "cn": cn, "h": view_dir, "common": common, "it": it})
            if r.get("bev") is not None and len(r["bev"]):
                np.savez_compressed(os.path.join(bev_dir, f"{p['id']}_{vname}.npz"), pts=r["bev"].astype(np.float16),
                                    ce=ce, cn=cn, h=view_dir, cam_h=r.get("cam_height") or 0.0, seq=str(p.get("sequence")))
            log.append({"image_id": p["id"], "sequence": p.get("sequence"), "view": vname, "status": r["status"], "cam_height": r.get("cam_height"),
                        "n_widths": len(r["widths"]), "n_objects": len(r["objects"])})
        if (i + 1) % 5 == 0 or i + 1 == len(meta):
            sys.stdout.write(f"\r{i + 1}/{len(meta)} photos  {(time.time() - t0) / (i + 1):.2f} s/photo  "
                             f"widths {len(widths)}  objects {len(objects)}")
            sys.stdout.flush()
    print()
    # Scale correction: the camera rig height is constant within a sequence, so each view's 3D scale is
    # rescaled to the sequence's median estimated camera height (or a known rig height via --cam-height).
    from collections import defaultdict
    hs = defaultdict(list)
    for row in log:
        if row["cam_height"]:
            hs[row["sequence"]].append(row["cam_height"])
    ref_h = {s_: (a.cam_height or float(np.median(v))) for s_, v in hs.items()}

    def finish(recs):
        feats = []
        for rec in recs:
            cmn, it = rec["common"], dict(rec["it"])
            k = ref_h.get(cmn["sequence"], cmn["cam_height_est"]) / cmn["cam_height_est"] if cmn["cam_height_est"] else 1.0
            for key in ("fwd_m", "right_m", "width_m", "dist_m", "footprint_m"):
                if key in it:
                    it[key + "_raw"] = it[key]
                    it[key] = round(it[key] * k, 3)
            it["scale_k"] = round(k, 3)
            e, nn = to_world(rec["ce"], rec["cn"], rec["h"], it["fwd_m"], it["right_m"])
            x, y = inv_t.transform(e, nn)
            feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [x, y]}, "properties": {**cmn, **it}})
        return feats
    widths, objects = finish(widths), finish(objects)
    for name, feats in (("width_samples", widths), ("objects_raw", objects)):
        with open(os.path.join(out_dir, f"{name}.geojson"), "w", encoding="utf-8") as fh:
            json.dump({"type": "FeatureCollection", "features": feats}, fh)
    with open(os.path.join(out_dir, "per_view.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(log[0].keys()))
        wr.writeheader()
        wr.writerows(log)
    print(f"wrote outputs to {out_dir}")


if __name__ == "__main__":
    main()
