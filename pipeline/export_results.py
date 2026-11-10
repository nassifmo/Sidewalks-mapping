"""Step 4: package AI results for QGIS and add each object's position WITHIN the sidewalk.

- Objects seen in several photos are merged (same class within 1.5 m = one object); single sightings are
  kept but flagged (n_views = 1 is less certain).
- Each object is related to the nearest width transect on its sidewalk (within 3 m along the street):
    sidewalk_width_m     width of the sidewalk at that spot
    dist_from_curb_m     how far the object stands from the curb edge of the sidewalk
    clear_width_left_m   walkable width remaining beside the object (width - footprint, larger side)
    position             'on sidewalk' / 'curb edge' / 'off sidewalk'

Usage: python export_results.py --area-dir ~/sidewalk-data/beirut_pilot_foot --dest ../pilot_beirut/ai_results
"""
import argparse
import json
import os
import shutil

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point
from sklearn.cluster import DBSCAN


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--dest", required=True)
    a = ap.parse_args()
    out = os.path.join(os.path.expanduser(a.area_dir), "outputs")
    os.makedirs(a.dest, exist_ok=True)
    for f in ("sidewalks_ai.geojson", "width_transects.geojson", "sidewalk_map.tif"):
        if os.path.exists(os.path.join(out, f)):
            shutil.copy(os.path.join(out, f), os.path.join(a.dest, f))
    # widths from the two edges seen in each photo, bridging parked cars (view_edges.py)
    # (the _conf version adds pred_error_m + confidence from ml_widths.py --apply-rows, when it was run)
    for f in ("width_transects_views_conf.geojson", "width_transects_views.geojson"):
        if os.path.exists(os.path.join(out, f)):
            shutil.copy(os.path.join(out, f), os.path.join(a.dest, "width_edges.geojson"))
            break

    tr = gpd.read_file(os.path.join(out, "width_transects.geojson"))
    crs = tr.estimate_utm_crs()
    tr = tr.to_crs(crs)
    obj_file = "objects_raw_aligned.geojson" if os.path.exists(os.path.join(out, "objects_raw_aligned.geojson")) else "objects_raw.geojson"
    ob = gpd.read_file(os.path.join(out, obj_file)).to_crs(crs)
    ob = ob[~ob.cls.isin(["billboard", "truck"])]

    rows = []
    for cls, g in ob.groupby("cls"):
        xy = np.c_[g.geometry.x, g.geometry.y]
        lab = DBSCAN(eps=1.5, min_samples=1).fit_predict(xy)
        for k in np.unique(lab):
            m = g[lab == k]
            c = xy[lab == k].mean(0)
            rows.append({"cls": cls, "n_views": len(m), "on_sidewalk_frac": round(float(m.on_sidewalk.mean()), 2),
                         "footprint_m": round(float(m.footprint_m.median()), 2), "x": c[0], "y": c[1]})
    obj = pd.DataFrame(rows)

    # relate each object to its sidewalk transect
    mids = np.array([[g.interpolate(0.5, normalized=True).x, g.interpolate(0.5, normalized=True).y] for g in tr.geometry])
    tree = cKDTree(mids)
    sw_w, from_curb, clear, pos = [], [], [], []
    for r in obj.itertuples():
        d, idx = tree.query([r.x, r.y], k=min(6, len(mids)))
        best = None
        for dd, j in zip(np.atleast_1d(d), np.atleast_1d(idx)):
            if dd > 4:
                break
            (x0, y0), (x1, y1) = tr.geometry.iloc[j].coords[0], tr.geometry.iloc[j].coords[-1]
            L = max(1e-6, np.hypot(x1 - x0, y1 - y0))
            u = np.array([(x1 - x0) / L, (y1 - y0) / L])
            v = np.array([r.x - x0, r.y - y0])
            t = float(v @ u)                       # along the transect: 0 = curb edge, L = building side
            along = abs(float(v @ np.array([-u[1], u[0]])))   # distance along the street from this transect
            if along <= 3 and (best is None or along < best[0]):
                best = (along, L, t)
        if best is None:
            sw_w.append(None); from_curb.append(None); clear.append(None); pos.append("unknown")
            continue
        _, L, t = best
        sw_w.append(round(L, 2))
        from_curb.append(round(t, 2))
        if t < -0.3 or t > L + 0.3:
            pos.append("off sidewalk"); clear.append(None)
        else:
            fp = min(r.footprint_m, L) if r.cls in ("parked_car", "parked_motorcycle", "bench", "kiosk", "barrier", "bin") else 0.3
            left = max(0.0, t - fp / 2)
            right = max(0.0, L - (t + fp / 2))
            clear.append(round(max(left, right), 2))
            pos.append("curb edge" if t < 0.6 else "on sidewalk")
    obj["sidewalk_width_m"] = sw_w
    obj["dist_from_curb_m"] = from_curb
    obj["clear_width_left_m"] = clear
    obj["position"] = pos
    gdf = gpd.GeoDataFrame(obj.drop(columns=["x", "y"]), geometry=[Point(x, y) for x, y in zip(obj.x, obj.y)], crs=crs).to_crs(4326)
    gdf.to_file(os.path.join(a.dest, "objects.geojson"), driver="GeoJSON")
    print(f"exported {len(gdf)} objects; by class: {gdf.cls.value_counts().to_dict()}")
    print(f"position: {gdf.position.value_counts().to_dict()}")


if __name__ == "__main__":
    main()
