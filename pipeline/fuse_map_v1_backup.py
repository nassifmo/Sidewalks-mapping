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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--min-views", type=float, default=1.5, help="min total vote weight for a cell to count as observed")
    ap.add_argument("--station-m", type=float, default=2.0)
    ap.add_argument("--max-offset", type=float, default=20.0, help="how far from the street centreline to search (m)")
    ap.add_argument("--cam-height", type=float, default=0.0)
    ap.add_argument("--no-align", action="store_true", help="ignore sequence_shifts.csv")
    a = ap.parse_args()
    area = os.path.expanduser(a.area_dir)
    out = os.path.join(area, "outputs")
    files = sorted(glob.glob(os.path.join(out, "bev", "*.npz")))
    log = pd.read_csv(os.path.join(out, "per_view.csv"))
    ref_h = log.groupby("sequence").cam_height.median().to_dict()
    ref_h = {str(k): v for k, v in ref_h.items()}
    meta = json.load(open(os.path.join(area, "imagery", "images.geojson")))["features"]
    lons = [f["geometry"]["coordinates"][0] for f in meta]
    lats = [f["geometry"]["coordinates"][1] for f in meta]
    epsg = utm_epsg(np.mean(lons), np.mean(lats))
    to_utm = Transformer.from_crs(4326, epsg, always_xy=True)
    to_ll = Transformer.from_crs(epsg, 4326, always_xy=True)

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
        k = (a.cam_height or ref_h.get(str(z["seq"]), cam_h)) / cam_h
        if not (0.75 <= k <= 1.33):          # camera height far from its sequence's: unreliable view
            dropped += 1
            continue
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
        wgt = 1.0 / (1.0 + (np.hypot(x, y) / 6.0) ** 2)
        # each view contributes at most weight w per cell (pixels are denser near the camera)
        key = (c[ok] * H + row[ok]) * W + col[ok]
        uk, inv = np.unique(key, return_inverse=True)
        wmax = np.zeros(len(uk), np.float32)
        np.maximum.at(wmax, inv, wgt[ok])
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
    bbox = (min(lons), min(lats), max(lons), max(lats))
    ways = osm_streets(bbox, os.path.join(area, "osm_streets.json"))
    samples, transects = [], []
    step = RES / 2
    offsets = np.arange(1.0, a.max_offset, step)
    for wy in ways:
        if wy["highway"] not in STREET_TYPES:
            continue
        xy = np.array([to_utm.transform(*c) for c in wy["coords"]])
        for (x0, y0), (x1, y1) in zip(xy[:-1], xy[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 1:
                continue
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            for t in np.arange(a.station_m / 2, L, a.station_m):
                px, py = x0 + ux * t, y0 + uy * t
                for side_sign, side_name in ((1, "left"), (-1, "right")):
                    nx, ny = -uy * side_sign, ux * side_sign
                    ex, ey = px + nx * offsets, py + ny * offsets
                    cols = ((ex - E0) / RES).astype(int)
                    rows = ((N1 - ey) / RES).astype(int)
                    inside = (cols >= 0) & (cols < W) & (rows >= 0) & (rows < H)
                    if not inside.all():
                        continue
                    sw = sidewalk[rows, cols]
                    ob = observed[rows, cols]
                    if not sw.any():
                        continue
                    i0 = int(np.argmax(sw))                     # first sidewalk cell outward from the street
                    j = i0
                    gap = 0
                    while j + 1 < len(sw) and (sw[j + 1] or gap < 3):
                        gap = 0 if sw[j + 1] else gap + 1
                        j += 1
                    while j > i0 and not sw[j]:
                        j -= 1
                    width = (j - i0 + 1) * step
                    if width < 0.5:
                        continue
                    inner_ok = i0 > 0 and ob[i0 - 1] and not sw[i0 - 1]
                    outer_ok = j + 1 < len(sw) and ob[j + 1]
                    mid = (offsets[i0] + offsets[j]) / 2
                    mx, my = px + nx * mid, py + ny * mid
                    lon, lat = to_ll.transform(mx, my)
                    props = {"osm_way": wy["id"], "street": wy["name"], "highway": wy["highway"], "side": side_name,
                             "width_m": round(width, 2), "offset_from_centreline_m": round(float(offsets[i0]), 2),
                             "complete": bool(inner_ok and outer_ok), "filled_frac": 1.0, "dist_m": 0.0}
                    samples.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props})
                    a0 = to_ll.transform(px + nx * offsets[i0], py + ny * offsets[i0])
                    a1 = to_ll.transform(px + nx * offsets[j], py + ny * offsets[j])
                    transects.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": [a0, a1]}, "properties": props})
    json.dump({"type": "FeatureCollection", "features": samples}, open(os.path.join(out, "width_samples_fused.geojson"), "w"))
    json.dump({"type": "FeatureCollection", "features": transects}, open(os.path.join(out, "width_transects.geojson"), "w"))
    comp = sum(f["properties"]["complete"] for f in samples)
    print(f"wrote {len(samples)} width transects ({comp} complete, {len(samples) - comp} possibly cut by occlusion)")


if __name__ == "__main__":
    main()
