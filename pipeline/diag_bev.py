"""Diagnostic: bird's-eye view of what the AI saw as sidewalk vs the official sidewalk, in the camera's frame.

Usage: python diag_bev.py --area-dir ~/sidewalk-data/dc_adams_morgan --gt ../benchmark_dc/ground_truth/dc_sidewalks_2023.geojson --out sheet.png
"""
import argparse
import glob
import json
import math
import os

import geopandas as gpd
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from pyproj import Transformer

from measure import travel_bearings, utm_epsg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--gt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=6)
    a = ap.parse_args()
    area = os.path.expanduser(a.area_dir)
    meta = {f["properties"]["id"]: f for f in json.load(open(os.path.join(area, "imagery", "images.geojson")))["features"]}
    travel = travel_bearings(list(meta.values()))
    log = pd.read_csv(os.path.join(area, "outputs", "per_view.csv"), dtype={"image_id": str})
    ref_h = log.groupby("sequence").cam_height.median().to_dict()
    files = sorted(glob.glob(os.path.join(area, "outputs", "debug", "*.npz")))[: a.n]
    lon0, lat0 = next(iter(meta.values()))["geometry"]["coordinates"]
    epsg = utm_epsg(lon0, lat0)
    t = Transformer.from_crs(4326, epsg, always_xy=True)
    sw = gpd.read_file(a.gt).to_crs(epsg)
    S, R = 40, 12  # px per metre, half-size metres
    tiles = []
    for fpath in files:
        iid, view = os.path.basename(fpath)[:-4].rsplit("_", 1)
        f = meta[int(iid)] if int(iid) in meta else meta[iid]
        p = f["properties"]
        z = np.load(fpath)
        seq = p.get("sequence")
        k = ref_h.get(seq, float(z["cam_h"])) / float(z["cam_h"])
        tb = travel.get(p["id"], p.get("compass_angle"))
        h = math.radians((tb + (-90 if view == "left" else 90)) % 360)
        ce, cn = t.transform(*f["geometry"]["coordinates"])
        img = Image.new("RGB", (2 * R * S, 2 * R * S), "white")
        d = ImageDraw.Draw(img)
        P = lambda x, y: (R * S + x * S, 2 * R * S - (y + 0) * S - 10)
        for m in range(0, 2 * R + 1, 2):
            d.line([P(-R, m), P(R, m)], fill=(235, 235, 235))
        # official sidewalk polygons -> camera ground frame (x right, y forward)
        for g in sw.geometry:
            if g.distance(gpd.points_from_xy([ce], [cn])[0]) > 30:
                continue
            for poly in getattr(g, "geoms", [g]):
                pts = []
                for e, n in poly.exterior.coords:
                    de, dn = e - ce, n - cn
                    fwd = de * math.sin(h) + dn * math.cos(h)
                    rgt = de * math.cos(h) - dn * math.sin(h)
                    pts.append(P(rgt, fwd))
                d.polygon(pts, fill=(170, 225, 170), outline=(40, 140, 40))
        sx, sy = z["sx"] * k, z["sy"] * k
        sel = np.random.default_rng(0).choice(len(sx), min(6000, len(sx)), replace=False)
        for x, y in zip(sx[sel], sy[sel]):
            X, Y = P(x, y)
            d.point((X, Y), fill=(230, 120, 0))
        for w in json.loads(str(z["widths"])):
            X, Y = P(w["right_m"] * k, w["fwd_m"] * k)
            d.ellipse([X - 3, Y - 3, X + 3, Y + 3], fill=(200, 0, 0))
            d.text((X + 4, Y - 5), f"{w['width_m'] * k:.1f}", fill=(200, 0, 0))
        d.text((5, 5), f"{iid} {view}  cam_h={float(z['cam_h']):.2f} k={k:.2f}  (grid 2 m; camera at bottom centre)", fill=(0, 0, 0))
        tiles.append(img)
    W = 3
    sheet = Image.new("RGB", (W * tiles[0].width, math.ceil(len(tiles) / W) * tiles[0].height), "white")
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % W) * im.width, (i // W) * im.height))
    sheet.thumbnail((1500, 1500))
    sheet.save(a.out)
    print("saved", a.out)


if __name__ == "__main__":
    main()
