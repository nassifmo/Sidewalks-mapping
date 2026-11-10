"""Step 2b: fuse all photos into one overhead sidewalk map, then measure widths along every street.

1. Every view saved by measure.py (outputs/bev/*.npz) votes for 10 cm ground cells: sidewalk / road / grass.
   Votes are weighted by closeness to the camera (near = more reliable). Each sequence is scaled to its
   median estimated camera height.
2. A cell is sidewalk if sidewalk votes win clearly and enough views saw it.
3. Along every OSM street (residential and up), every 2 m on both sides, a transect is cast perpendicular
   to the street; the first sidewalk run it crosses gives the width. Transects whose run touches unseen
   cells are flagged (occluded / incomplete).

Usage (AI environment):
    python fuse_map.py --area-dir ~/sidewalk-data/dc_adams_morgan
Writes outputs/sidewalk_map.tif, sidewalks_ai.geojson, width_transects.geojson (+ width_samples_fused.geojson for scoring)
"""
import argparse
import glob
import json
import math
import os
import urllib.parse
import urllib.request
from collections import defaultdict

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy import ndimage

RES = 0.10
STREET_TYPES = {"primary", "secondary", "tertiary", "residential", "unclassified", "living_street",
                "primary_link", "secondary_link", "tertiary_link", "trunk", "service"}


def utm_epsg(lon, lat):
    return (32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1


def osm_streets(bbox, cache):
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf-8"))
    s, w, n, e = bbox[1], bbox[0], bbox[3], bbox[2]
    q = f'[out:json][timeout:120];way["highway"]({s},{w},{n},{e});out geom;'
    req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(),
                                 headers={"User-Agent": "sidewalk-research/1.0"})
    els = json.loads(urllib.request.urlopen(req, timeout=180).read())["elements"]
    ways = [{"id": el["id"], "highway": el["tags"].get("highway"), "name": el["tags"].get("name"),
             "coords": [[p["lon"], p["lat"]] for p in el["geometry"]]} for el in els if "geometry" in el]
    json.dump(ways, open(cache, "w", encoding="utf-8"))
    return ways


def pano_sequences(meta):
    """Sequences made of 360 panoramas (the parked-car calibration is used for these only)."""
    return {str(f["properties"].get("sequence")) for f in meta if f["properties"].get("is_pano")}


def sequence_heights(out_dir, log, use_calib=True, pano_seqs=None):
    """Per-sequence reference camera height.
    est: median of the depth model's own per-view estimates (used to reject inconsistent views).
    scale: the height used to set metric scale = parked-car calibration (calib_scale.py) when available,
    else est. pano_seqs: when given, calibration is applied to these (panorama) sequences only (DC test:
    on-foot sequences rarely show enough whole cars, and the few calibrations made widths worse)."""
    est = {str(k): float(v) for k, v in log.groupby("sequence").cam_height.median().items()}
    scale = dict(est)
    p = os.path.join(out_dir, "sequence_scale.csv")
    if use_calib and os.path.exists(p):
        cal = pd.read_csv(p, dtype={"sequence": str}).dropna(subset=["rig_height_m"])
        if pano_seqs is not None:
            cal = cal[cal.sequence.isin(pano_seqs)]
        n = 0
        for r in cal.itertuples():
            if r.sequence in est and est[r.sequence] > 0:
                # calibration gives the TRUE rig height; scale views so their sequence median lands on it
                scale[r.sequence] = float(r.rig_height_m)
                n += 1
        print(f"camera heights: {n} sequences calibrated from parked cars, {len(est) - n} use the depth-model estimate")
    return est, scale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--min-views", type=float, default=1.5, help="min total vote weight for a cell to count as observed")
    ap.add_argument("--station-m", type=float, default=2.0)
    ap.add_argument("--max-offset", type=float, default=20.0, help="how far from the street centreline to search (m)")
    ap.add_argument("--cam-height", type=float, default=0.0)
    ap.add_argument("--no-align", action="store_true", help="ignore sequence_shifts.csv")
    ap.add_argument("--no-calib", action="store_true", help="ignore sequence_scale.csv (parked-car calibration)")
    ap.add_argument("--fill-m", type=float, default=0.4, help="close gaps up to this size inside each view's ground patch (0 = old point voting)")
    ap.add_argument("--max-gap",type=float, default=20.0, help="longest hidden stretch (m) bridged between seen edges")
    ap.add_argument("--smooth-m", type=float, default=6.0, help="running-median window (m) for seen edges; 0 = off")
    ap.add_argument("--default-variant", default="raw", choices=["raw", "filled"])
    ap.add_argument("--reuse-grid", action="store_true", help="skip voting; reuse outputs/grid_cache.npz (edge/width tuning)")
    a = ap.parse_args()
    area = os.path.expanduser(a.area_dir)
    out = os.path.join(area, "outputs")
    files = sorted(glob.glob(os.path.join(out, "bev", "*.npz")))
    log = pd.read_csv(os.path.join(out, "per_view.csv"))
    meta = json.load(open(os.path.join(area, "imagery", "images.geojson")))["features"]
    est_h, ref_h = sequence_heights(out, log, not a.no_calib, pano_sequences(meta))
    lons = [f["geometry"]["coordinates"][0] for f in meta]
    lats = [f["geometry"]["coordinates"][1] for f in meta]
    epsg = utm_epsg(np.mean(lons), np.mean(lats))
    to_utm = Transformer.from_crs(4326, epsg, always_xy=True)
    to_ll = Transformer.from_crs(epsg, 4326, always_xy=True)

    if a.reuse_grid:
        z = np.load(os.path.join(out, "grid_cache.npz"))
        E0_, N1_, W_, H_, epsg_ = z["geo"]
        measure_streets(area, out, z["sidewalk"], z["observed"], E0_, N1_, int(W_), int(H_), int(epsg_), lons, lats, a)
        return
    # ---------------- 1. accumulate votes
    E0, N0 = to_utm.transform(min(lons) - 0.0003, min(lats) - 0.0003)
    E1, N1 = to_utm.transform(max(lons) + 0.0003, max(lats) + 0.0003)
    W, H = int((E1 - E0) / RES) + 1, int((N1 - N0) / RES) + 1
    print(f"{len(files)} views -> grid {W} x {H} cells at {RES} m")
    # per-sequence GPS correction from align.py (building fronts vs building outlines)
    shifts = {}
    sp = os.path.join(out, "sequence_shifts.csv")
    if os.path.exists(sp) and not a.no_align:
        sdf = pd.read_csv(sp, dtype={"sequence": str})
        shifts = {r.sequence: (r.dx, r.dy) for r in sdf.itertuples() if r.accepted}
        print(f"applying GPS corrections to {len(shifts)} sequences")
    view_rot = {}
    hp = os.path.join(out, "view_heading_fixes.csv")
    if os.path.exists(hp) and not a.no_align:
        view_rot = dict(pd.read_csv(hp).itertuples(index=False, name=None))
        print(f"applying heading fixes to {len(view_rot)} views")
    votes = np.zeros((4, H, W), np.float32)   # 0 unused, 1 sidewalk, 2 road, 3 grass
    dropped = 0
    for i, fp in enumerate(files):
        z = np.load(fp)
        cam_h = float(z["cam_h"])
        if cam_h <= 0:
            continue
        if not (0.75 <= est_h.get(str(z["seq"]), cam_h) / cam_h <= 1.33):   # inconsistent with its sequence
            dropped += 1
            continue
        k = (a.cam_height or ref_h.get(str(z["seq"]), cam_h)) / cam_h
        dx, dy = shifts.get(str(z["seq"]), (0.0, 0.0))
        P = z["pts"].astype(np.float32)
        x, y, c = P[:, 0] * k, P[:, 1] * k, P[:, 2].astype(int)
        hd = math.radians(float(z["h"]) + view_rot.get(os.path.basename(fp)[:-4], 0.0))
        keep_c = c <= 3                        # building fronts (code 4) are for alignment only
        x, y, c = x[keep_c], y[keep_c], c[keep_c]
        e = float(z["ce"]) + dx + y * math.sin(hd) + x * math.cos(hd)
        n = float(z["cn"]) + dy + y * math.cos(hd) - x * math.sin(hd)
        col = ((e - E0) / RES).astype(int)
        row = ((N1 - n) / RES).astype(int)
        ok = (col >= 0) & (col < W) & (row >= 0) & (row < H)
        if not ok.any():
            continue
        wgt = (1.0 / (1.0 + (np.hypot(x, y) / 6.0) ** 2))[ok]
        col, row, c = col[ok], row[ok], c[ok]
        if a.fill_m > 0:
            # draw this view as a continuous patch: the saved points are every 2nd pixel row, which far from
            # the camera leaves 0.2-0.4 m stripes between rows. Empty cells within fill_m of a point take the
            # nearest point's class; larger holes (parked cars, unseen ground) stay empty.
            c0, r0 = col.min(), row.min()
            lr, lc = row - r0, col - c0
            lab = np.zeros((lr.max() + 1, lc.max() + 1), np.int8)
            wl = np.zeros(lab.shape, np.float32)
            o = np.argsort(wgt)                 # nearer (heavier) points written last = win the cell
            lab[lr[o], lc[o]] = c[o]
            wl[lr[o], lc[o]] = wgt[o]
            empty = lab == 0
            dist_, (ir, ic) = ndimage.distance_transform_edt(empty, return_indices=True)
            fill = empty & (dist_ <= a.fill_m / RES)
            lab[fill] = lab[ir[fill], ic[fill]]
            wl[fill] = wl[ir[fill], ic[fill]]
            rr, cl = np.nonzero(lab)
            votes[lab[rr, cl], rr + r0, cl + c0] += wl[rr, cl]
        else:
            # each view contributes at most weight w per cell (pixels are denser near the camera)
            key = (c * H + row) * W + col
            uk, inv = np.unique(key, return_inverse=True)
            wmax = np.zeros(len(uk), np.float32)
            np.maximum.at(wmax, inv, wgt)
            cc, rem = np.divmod(uk, H * W)
            rr, cl = np.divmod(rem, W)
            np.add.at(votes, (cc, rr, cl), wmax)
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(files)} views fused")
    print(f"dropped {dropped} views with implausible camera height")
    # apply the same corrections / filters to the per-photo widths and objects
    cam_xy = {str(f["properties"]["id"]): to_utm.transform(*f["geometry"]["coordinates"]) for f in meta}
    for name in ("width_samples", "objects_raw"):
        src_p = os.path.join(out, f"{name}.geojson")
        if not os.path.exists(src_p):
            continue
        fc = json.load(open(src_p))
        kept = []
        for f in fc["features"]:
            pr = f["properties"]
            if not (0.75 <= pr.get("scale_k", 1.0) <= 1.33):
                continue
            dx, dy = shifts.get(str(pr.get("sequence")), (0.0, 0.0))
            ex, ny = to_utm.transform(*f["geometry"]["coordinates"])
            rot = view_rot.get(f"{pr.get('image_id')}_{pr.get('view')}", 0.0)
            if rot and str(pr.get("image_id")) in cam_xy:
                cx_, cy_ = cam_xy[str(pr.get("image_id"))]
                t_ = math.radians(rot)
                ve, vn = ex - cx_, ny - cy_
                ex, ny = cx_ + ve * math.cos(t_) + vn * math.sin(t_), cy_ - ve * math.sin(t_) + vn * math.cos(t_)
            f["geometry"]["coordinates"] = list(to_ll.transform(ex + dx, ny + dy))
            pr["gps_shift_m"] = round(math.hypot(dx, dy), 2)
            kept.append(f)
        json.dump({"type": "FeatureCollection", "features": kept}, open(os.path.join(out, f"{name}_aligned.geojson"), "w"))
        print(f"wrote {name}_aligned.geojson ({len(kept)} of {len(fc['features'])} kept)")
    # spread votes slightly (points are sparse far from the camera)
    if a.fill_m <= 0:
        for c in (1, 2, 3):
            votes[c] = ndimage.uniform_filter(votes[c], size=3) * 9
    total = votes[1] + votes[2] + votes[3]
    observed = total >= a.min_views
    sidewalk = observed & (votes[1] >= 0.6 * total)
    sidewalk = ndimage.binary_opening(sidewalk, iterations=1)
    sidewalk = ndimage.binary_closing(sidewalk, iterations=2)
    print(f"observed area {observed.sum() * RES * RES:.0f} m2, sidewalk {sidewalk.sum() * RES * RES:.0f} m2")

    # save raster (GeoTIFF) for QGIS
    try:
        import rasterio
        from rasterio.transform import from_origin
        tr = from_origin(E0, N1, RES, RES)
        lab = np.where(sidewalk, 1, np.where(observed & (votes[2] >= votes[3]), 2, np.where(observed, 3, 0))).astype(np.uint8)
        with rasterio.open(os.path.join(out, "sidewalk_map.tif"), "w", driver="GTiff", width=W, height=H, count=1, dtype="uint8",
                           crs=f"EPSG:{epsg}", transform=tr, compress="deflate", nodata=0) as dst:
            dst.write(lab, 1)
        from rasterio import features
        polys = [{"type": "Feature", "geometry": geom, "properties": {"class": "sidewalk"}}
                 for geom, v in features.shapes(sidewalk.astype(np.uint8), mask=sidewalk, transform=tr) if v == 1]
        from shapely.geometry import shape, mapping
        from shapely.ops import transform as stransform
        feats = []
        for f in polys:
            g = shape(f["geometry"])
            if g.area < 1.0:
                continue
            g = g.simplify(0.15)
            feats.append({"type": "Feature", "properties": {"area_m2": round(g.area, 1)},
                          "geometry": mapping(stransform(lambda x, y, z=None: to_ll.transform(x, y), g))})
        json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(out, "sidewalks_ai.geojson"), "w"))
        print(f"wrote sidewalk_map.tif and sidewalks_ai.geojson ({len(feats)} polygons)")
    except ImportError:
        print("rasterio not installed: skipping GeoTIFF/polygon export")

    # ---------------- 3. width transects along OSM streets
    np.savez_compressed(os.path.join(out, "grid_cache.npz"), sidewalk=sidewalk, observed=observed,
                        geo=np.array([E0, N1, W, H, epsg], dtype=np.float64))
    measure_streets(area, out, sidewalk, observed, E0, N1, W, H, epsg, lons, lats, a)


# ----------------------------------------------------------------------------- edges & widths
def station_profiles(ways, sidewalk, observed, E0, N1, W, H, to_utm, a, bld_tree):
    """For every street, every station_m and both sides: where the sidewalk run starts/ends along the
    perpendicular, and whether each end is a REAL edge (something else seen beyond it) or a HIDDEN one
    (the run stops at unseen cells - typically a parked car)."""
    step = RES / 2
    offsets = np.arange(1.0, a.max_offset, step)
    chains = {}
    for wy in ways:
        if wy["highway"] not in STREET_TYPES:
            continue
        xy = np.array([to_utm.transform(*c) for c in wy["coords"]])
        s0 = 0.0
        for (x0, y0), (x1, y1) in zip(xy[:-1], xy[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 1:
                s0 += L
                continue
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            for t in np.arange(a.station_m / 2, L, a.station_m):
                px, py = x0 + ux * t, y0 + uy * t
                for side_sign, side_name in ((1, "left"), (-1, "right")):
                    nx, ny = -uy * side_sign, ux * side_sign
                    ex, ey = px + nx * offsets, py + ny * offsets
                    cols = ((ex - E0) / RES).astype(int)
                    rows = ((N1 - ey) / RES).astype(int)
                    if not ((cols >= 0) & (cols < W) & (rows >= 0) & (rows < H)).all():
                        continue
                    sw, ob = sidewalk[rows, cols], observed[rows, cols]
                    st = {"s": s0 + t, "px": px, "py": py, "nx": nx, "ny": ny, "way": wy, "side": side_name,
                          "i0": None, "j": None, "curb_real": False, "back_real": False, "road_only": False}
                    if sw.any():
                        i0 = int(np.argmax(sw))                     # first sidewalk cell outward from the street
                        j, gap = i0, 0
                        while j + 1 < len(sw) and (sw[j + 1] or gap < 3):
                            gap = 0 if sw[j + 1] else gap + 1
                            j += 1
                        while j > i0 and not sw[j]:
                            j -= 1
                        st["i0"], st["j"] = float(offsets[i0]), float(offsets[j])
                        # curb edge is real if the cells just street-side of it were seen and are not sidewalk
                        st["curb_real"] = bool(i0 >= 3 and ob[i0 - 3:i0].all() and not sw[i0 - 3:i0].any())
                        # back edge is real if a building outline is right there, or the cells beyond were seen as non-sidewalk
                        bx, by = px + nx * offsets[j], py + ny * offsets[j]
                        near_bld = bld_tree is not None and bld_tree.query([bx, by])[0] <= 0.8
                        seen_beyond = j + 4 < len(sw) and ob[j + 1:j + 4].all() and not sw[j + 1:j + 4].any()
                        st["back_real"] = bool(near_bld or seen_beyond)
                    else:
                        # no sidewalk at all here: genuinely absent if the band was clearly seen as road/other
                        st["road_only"] = bool(ob[: int(6 / step)].mean() > 0.6)
                    chains.setdefault((wy["id"], side_name), []).append(st)
            s0 += L
    for k in chains:
        chains[k].sort(key=lambda d: d["s"])
    return chains


def interp_edge(s, vals, real, max_gap, smooth_win):
    """Edge offset along one street side. Seen edges are lightly smoothed (curbs and building lines are
    straight); hidden stretches are bridged by a straight line between the seen edges before and after
    them (both sides required, gap <= max_gap). Returns (offset, source) per station."""
    s, vals, real = np.asarray(s, float), np.asarray(vals, float), np.asarray(real, bool)
    out = np.full(len(s), np.nan)
    src = np.array(["none"] * len(s), dtype=object)
    rs, rv = s[real], vals[real]
    if len(rs) == 0:
        return out, src
    sm = np.array([np.median(rv[np.abs(rs - x) <= smooth_win / 2]) for x in rs]) if smooth_win > 0 else rv
    for i, x in enumerate(s):
        if real[i]:
            out[i] = sm[np.searchsorted(rs, x)]
            src[i] = "seen"
            continue
        k = np.searchsorted(rs, x)
        if 0 < k < len(rs) and rs[k] - rs[k - 1] <= max_gap:
            lo_i, hi_i = slice(max(0, k - 3), k), slice(k, min(len(rs), k + 3))   # up to 3 seen edges per side
            sl, vl = np.median(rs[lo_i]), np.median(sm[lo_i])
            sh, vh = np.median(rs[hi_i]), np.median(sm[hi_i])
            w = min(1.0, max(0.0, (x - sl) / max(1e-6, sh - sl)))
            out[i] = vl + w * (vh - vl)
            src[i] = "bridged"
    return out, src


def measure_streets(area, out, sidewalk, observed, E0, N1, W, H, epsg, lons, lats, a):
    to_utm = Transformer.from_crs(4326, epsg, always_xy=True)
    to_ll = Transformer.from_crs(epsg, 4326, always_xy=True)
    bbox = (min(lons), min(lats), max(lons), max(lats))
    ways = osm_streets(bbox, os.path.join(area, "osm_streets.json"))
    bld_tree = None
    bp = os.path.join(area, "osm_buildings.json")
    if os.path.exists(bp):
        from scipy.spatial import cKDTree
        from align import densify
        ref = densify(json.load(open(bp)), to_utm)
        bld_tree = cKDTree(ref) if len(ref) else None
    chains = station_profiles(ways, sidewalk, observed, E0, N1, W, H, to_utm, a, bld_tree)

    variants = {"raw": [], "filled": []}
    for (wid, side), sts in chains.items():
        s = [d["s"] for d in sts]
        curb, csrc = interp_edge(s, [d["i0"] if d["i0"] is not None else np.nan for d in sts],
                                 [d["curb_real"] for d in sts], a.max_gap, a.smooth_m)
        back, bsrc = interp_edge(s, [d["j"] if d["j"] is not None else np.nan for d in sts],
                                 [d["back_real"] for d in sts], a.max_gap, a.smooth_m)
        for i, d in enumerate(sts):
            wy = d["way"]
            base = {"osm_way": wy["id"], "street": wy["name"], "highway": wy["highway"], "side": side,
                    "filled_frac": 1.0, "dist_m": 0.0}
            # raw: the longest visible run (previous method)
            if d["i0"] is not None and d["j"] - d["i0"] + RES / 2 >= 0.5:
                variants["raw"].append((d, d["i0"], d["j"] + RES / 2, {**base, "method": "observed",
                                        "complete": bool(d["curb_real"] and d["back_real"])}))
            # filled: each edge is either seen (smoothed) or bridged from the seen edges before/after the gap
            if d["road_only"]:
                continue
            c, b = curb[i], back[i]
            if np.isnan(c) or np.isnan(b):
                continue
            b = b + RES / 2
            if not (0.5 <= b - c <= 12):
                continue
            m = "seen" if csrc[i] == "seen" and bsrc[i] == "seen" else "bridged"
            variants["filled"].append((d, c, b, {**base, "method": m, "complete": True,
                                                 "curb_edge": csrc[i], "back_edge": bsrc[i]}))

    for name, rows in variants.items():
        samples, transects = [], []
        for d, c, b, props in rows:
            props = {**props, "width_m": round(float(b - c), 2), "offset_from_centreline_m": round(float(c), 2)}
            px, py, nx, ny = d["px"], d["py"], d["nx"], d["ny"]
            mid = (c + b) / 2
            samples.append({"type": "Feature", "properties": props, "geometry": {
                "type": "Point", "coordinates": list(to_ll.transform(px + nx * mid, py + ny * mid))}})
            transects.append({"type": "Feature", "properties": props, "geometry": {"type": "LineString", "coordinates": [
                list(to_ll.transform(px + nx * c, py + ny * c)), list(to_ll.transform(px + nx * b, py + ny * b))]}})
        suffix = "" if name == a.default_variant else f"_{name}"
        json.dump({"type": "FeatureCollection", "features": samples}, open(os.path.join(out, f"width_samples_fused{suffix}.geojson"), "w"))
        json.dump({"type": "FeatureCollection", "features": transects}, open(os.path.join(out, f"width_transects{suffix}.geojson"), "w"))
        meth = pd.Series([r[3]["method"] for r in rows], dtype=object).value_counts().to_dict()
        print(f"{name}: {len(rows)} width transects {meth}" + ("  -> width_transects.geojson" if not suffix else f"  -> width_transects{suffix}.geojson"))


if __name__ == "__main__":
    main()
