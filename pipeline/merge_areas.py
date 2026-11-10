"""Combine the per-photo AI outputs of several runs (e.g. on-foot photos + car panoramas of the same area)
into one area folder, so align.py / fuse_map.py / export_results.py treat them as a single photo set.
Photos are not copied: only metadata, per-view outputs and the OSM caches.

Usage: python merge_areas.py --out ~/sidewalk-data/beirut_pilot_all ~/sidewalk-data/beirut_pilot_foot ~/sidewalk-data/beirut_pilot_car
"""
import argparse
import json
import os
import shutil

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("areas", nargs="+")
    a = ap.parse_args()
    out = os.path.expanduser(a.out)
    os.makedirs(os.path.join(out, "imagery"), exist_ok=True)
    bev = os.path.join(out, "outputs", "bev")
    if os.path.isdir(bev):
        shutil.rmtree(bev)
    os.makedirs(bev)
    feats, logs, scales, layers = {}, [], [], {"width_samples": [], "objects_raw": []}
    for src in map(os.path.expanduser, a.areas):
        for f in json.load(open(os.path.join(src, "imagery", "images.geojson")))["features"]:
            feats[str(f["properties"]["id"])] = f
        o = os.path.join(src, "outputs")
        logs.append(pd.read_csv(os.path.join(o, "per_view.csv")))
        if os.path.exists(os.path.join(o, "sequence_scale.csv")):          # parked-car calibration (calib_scale.py)
            scales.append(pd.read_csv(os.path.join(o, "sequence_scale.csv"), dtype={"sequence": str}))
        for name in layers:
            p = os.path.join(o, f"{name}.geojson")
            if os.path.exists(p):
                layers[name] += json.load(open(p))["features"]
        n = 0
        for fn in os.listdir(os.path.join(o, "bev")):
            shutil.copy(os.path.join(o, "bev", fn), os.path.join(bev, fn))
            n += 1
        for cache in ("osm_streets.json", "osm_buildings.json", "ms_buildings.json"):
            if os.path.exists(os.path.join(src, cache)) and not os.path.exists(os.path.join(out, cache)):
                shutil.copy(os.path.join(src, cache), os.path.join(out, cache))
        print(f"{src}: {len(logs[-1])} views, {n} bird's-eye files")
    json.dump({"type": "FeatureCollection", "features": list(feats.values())}, open(os.path.join(out, "imagery", "images.geojson"), "w"))
    pd.concat(logs).to_csv(os.path.join(out, "outputs", "per_view.csv"), index=False)
    sp = os.path.join(out, "outputs", "sequence_scale.csv")
    if scales:
        pd.concat(scales).drop_duplicates("sequence").to_csv(sp, index=False)
    elif os.path.exists(sp):
        os.remove(sp)
    for name, fs in layers.items():
        json.dump({"type": "FeatureCollection", "features": fs}, open(os.path.join(out, "outputs", f"{name}.geojson"), "w"))
    print(f"merged {len(feats)} photos -> {out}")


if __name__ == "__main__":
    main()
