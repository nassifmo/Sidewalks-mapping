"""Step 2a: correct GPS shifts per photo sequence by matching building fronts seen in the photos
to building outlines on the map (OpenStreetMap, falling back to Microsoft footprints). No human input,
and no sidewalk answer key is used, so the same step works in Lebanon.

For each sequence: all building-front points (code 4 in outputs/bev/*.npz) are placed on the map with the
sequence's camera-height scale, then a translation (dx, dy) is searched (+-6 m) that minimises a robust
distance to building outline edges. Shifts are accepted only if the match clearly improves.

Usage: python align.py --area-dir ~/sidewalk-data/dc_adams_morgan_foot
Writes outputs/sequence_shifts.csv
"""
import argparse
import csv
import glob
import gzip
import io
import json
import math
import os
import time
import urllib.parse
import urllib.request
from collections import defaultdict

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree

UA = {"User-Agent": "sidewalk-research/1.0"}


def utm_epsg(lon, lat):
    return (32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1


def osm_buildings(bbox, cache):
    if os.path.exists(cache):
        return json.load(open(cache))
    s, w, n, e = bbox[1], bbox[0], bbox[3], bbox[2]
    q = f'[out:json][timeout:180];way["building"]({s},{w},{n},{e});out geom;'
    for url in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
        for i in range(3):
            try:
                req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
                els = json.loads(urllib.request.urlopen(req, timeout=240).read())["elements"]
                rings = [[[p["lon"], p["lat"]] for p in el["geometry"]] for el in els if "geometry" in el]
                json.dump(rings, open(cache, "w"))
                return rings
            except Exception as ex:
                print(f"  overpass failed ({ex}); retrying")
                time.sleep(5 * (i + 1))
    return []


def ms_buildings(bbox, cache):
    if os.path.exists(cache):
        return json.load(open(cache))

    def qk(lon, lat, z=9):
        n = 2 ** z
        x = int((lon + 180) / 360 * n)
        r = math.radians(lat)
        y = int((1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * n)
        return "".join(str(((x >> (i - 1)) & 1) + 2 * ((y >> (i - 1)) & 1)) for i in range(z, 0, -1))
    keys = {qk(x, y) for x in (bbox[0], bbox[2]) for y in (bbox[1], bbox[3])}
    idx = urllib.request.urlopen(urllib.request.Request(
        "https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv", headers=UA)).read().decode()
    rows = list(csv.DictReader(io.StringIO(idx)))
    rings = []
    for r in rows:
        if r["QuadKey"] in keys:
            for line in gzip.decompress(urllib.request.urlopen(r["Url"]).read()).decode().splitlines():
                g = json.loads(line)["geometry"]
                ring = g["coordinates"][0]
                if any(bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3] for x, y in ring):
                    rings.append(ring)
    json.dump(rings, open(cache, "w"))
    return rings


def densify(rings, to_utm, step=0.25):
    pts = []
    for ring in rings:
        xy = np.array([to_utm.transform(x, y) for x, y in ring])
        for a, b in zip(xy[:-1], xy[1:]):
            L = np.hypot(*(b - a))
            n = max(1, int(L / step))
            t = np.linspace(0, 1, n, endpoint=False)[:, None]
            pts.append(a + t * (b - a))
    return np.vstack(pts) if pts else np.zeros((0, 2))


def robust_cost(tree, P, dx, dy, cap=3.0, keep=0.5, penalty=0.04):
    """Trimmed mean distance of the best-matching half of the points (fences / walls of front yards and
    stairs are not in building outlines), plus a small penalty on large shifts (GPS is usually off < 5 m)."""
    d, _ = tree.query(P + [dx, dy], distance_upper_bound=cap)
    d = np.sort(np.where(np.isfinite(d), d, cap))
    return float(np.mean(d[: max(1, int(len(d) * keep))])) + penalty * math.hypot(dx, dy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--search", type=float, default=6.0)
    ap.add_argument("--min-points", type=int, default=150)
    a = ap.parse_args()
    area = os.path.expanduser(a.area_dir)
    out = os.path.join(area, "outputs")
    meta = json.load(open(os.path.join(area, "imagery", "images.geojson")))["features"]
    lons = [f["geometry"]["coordinates"][0] for f in meta]
    lats = [f["geometry"]["coordinates"][1] for f in meta]
    bbox = (min(lons) - 0.0005, min(lats) - 0.0005, max(lons) + 0.0005, max(lats) + 0.0005)
    epsg = utm_epsg(np.mean(lons), np.mean(lats))
    to_utm = Transformer.from_crs(4326, epsg, always_xy=True)

    rings = osm_buildings(bbox, os.path.join(area, "osm_buildings.json"))
    src = "OpenStreetMap"
    if len(rings) < 20:
        rings = ms_buildings(bbox, os.path.join(area, "ms_buildings.json"))
        src = "Microsoft"
    ref = densify(rings, to_utm)
    print(f"reference: {len(rings)} {src} building outlines -> {len(ref)} edge points")
    tree = cKDTree(ref)

    log = pd.read_csv(os.path.join(out, "per_view.csv"))
    from fuse_map import sequence_heights
    est_h, ref_h = sequence_heights(out, log, not getattr(a, "no_calib", False))
    # ---- 1. heading correction per view: the sidewalk runs along the street, and the street's direction
    #         is known from OpenStreetMap. Compare the sidewalk's direction in the photo with the nearest
    #         street's direction and rotate the view by the difference (max +-25 deg).
    from fuse_map import osm_streets, STREET_TYPES
    ways = osm_streets(bbox, os.path.join(area, "osm_streets.json"))
    sp_, sb_ = [], []
    for wy in ways:
        if wy["highway"] not in STREET_TYPES:
            continue
        xy = np.array([to_utm.transform(*c) for c in wy["coords"]])
        for p0, p1 in zip(xy[:-1], xy[1:]):
            L = np.hypot(*(p1 - p0))
            if L < 2:
                continue
            brg = math.degrees(math.atan2(p1[0] - p0[0], p1[1] - p0[1])) % 180
            for t in np.arange(0, L, 2.0):
                sp_.append(p0 + (p1 - p0) * t / L)
                sb_.append(brg)
    st_tree, st_brg = cKDTree(np.array(sp_)), np.array(sb_)
    view_rot = {}
    for fp in glob.glob(os.path.join(out, "bev", "*.npz")):
        z = np.load(fp)
        P = z["pts"].astype(np.float32)
        P = P[P[:, 2] == 1]
        if len(P) < 300:
            continue
        r = np.hypot(P[:, 0], P[:, 1])
        P = P[(r >= 2) & (r <= 14)]
        if len(P) < 300:
            continue
        Q = P[:, :2] - P[:, :2].mean(0)
        ev, evec = np.linalg.eigh(np.cov(Q.T))
        elong = math.sqrt(ev[1] / max(ev[0], 1e-9))
        if elong < 2.5:
            continue
        ax_, ay_ = evec[:, 1]
        axis_brg = (float(z["h"]) + math.degrees(math.atan2(ax_, ay_))) % 180
        dist, j = st_tree.query([float(z["ce"]), float(z["cn"])])
        if dist > 25:
            continue
        delta = ((st_brg[j] - axis_brg + 90) % 180) - 90
        if abs(delta) <= 25:
            view_rot[os.path.basename(fp)[:-4]] = round(float(delta), 2)
    pd.DataFrame([{"view": k_, "heading_fix_deg": v_} for k_, v_ in view_rot.items()]).to_csv(
        os.path.join(out, "view_heading_fixes.csv"), index=False)
    if view_rot:
        vals = np.abs(list(view_rot.values()))
        print(f"heading fixes for {len(view_rot)} views: median |fix| {np.median(vals):.1f} deg, 90th pct {np.percentile(vals, 90):.1f} deg")

    # ---- 2. translation per sequence (building fronts vs building outlines), after heading fixes
    seq_pts = defaultdict(list)
    for fp in glob.glob(os.path.join(out, "bev", "*.npz")):
        z = np.load(fp)
        P = z["pts"].astype(np.float32)
        P = P[P[:, 2] == 4]
        cam_h = float(z["cam_h"])
        if len(P) == 0 or cam_h <= 0:
            continue
        seq = str(z["seq"])
        k = ref_h.get(seq, cam_h) / cam_h
        if not (0.75 <= est_h.get(seq, cam_h) / cam_h <= 1.33):
            continue
        hd = math.radians(float(z["h"]) + view_rot.get(os.path.basename(fp)[:-4], 0.0))
        x, y = P[:, 0] * k, P[:, 1] * k
        e = float(z["ce"]) + y * math.sin(hd) + x * math.cos(hd)
        n = float(z["cn"]) + y * math.cos(hd) - x * math.sin(hd)
        seq_pts[seq].append(np.c_[e, n])

    rows = []
    grid = np.arange(-a.search, a.search + 1e-6, 0.5)
    for seq, chunks in seq_pts.items():
        P = np.vstack(chunks)
        if len(P) < a.min_points:
            rows.append({"sequence": seq, "dx": 0.0, "dy": 0.0, "n_points": len(P), "cost_before": None, "cost_after": None, "accepted": False})
            continue
        if len(P) > 8000:
            P = P[np.random.default_rng(0).choice(len(P), 8000, replace=False)]
        c0 = robust_cost(tree, P, 0, 0)
        best = min(((robust_cost(tree, P, dx, dy), dx, dy) for dx in grid for dy in grid))
        c, bx, by = best
        for step in (0.25, 0.1, 0.05):
            improved = True
            while improved:
                improved = False
                for ddx, ddy in ((step, 0), (-step, 0), (0, step), (0, -step)):
                    cc = robust_cost(tree, P, bx + ddx, by + ddy)
                    if cc < c - 1e-4:
                        c, bx, by, improved = cc, bx + ddx, by + ddy, True
        accepted = c < 0.7 * c0 and math.hypot(bx, by) < a.search - 0.5
        rows.append({"sequence": seq, "dx": round(bx, 2) if accepted else 0.0, "dy": round(by, 2) if accepted else 0.0,
                     "n_points": len(P), "cost_before": round(c0, 3), "cost_after": round(c, 3), "accepted": accepted,
                     "shift_m": round(math.hypot(bx, by), 2)})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out, "sequence_shifts.csv"), index=False)
    acc = df[df.accepted]
    print(f"{len(df)} sequences; {len(acc)} shifted (median shift {acc.shift_m.median() if len(acc) else 0:.2f} m); "
          f"mean distance to buildings {df.cost_before.mean():.2f} -> {df.cost_after.mean():.2f} m")


if __name__ == "__main__":
    main()
