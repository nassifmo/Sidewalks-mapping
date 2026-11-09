"""Step 3: score the AI output against an answer key (DC official data). No human input.

Widths:   each AI width sample is matched to the nearest official width point (within --match-m).
          Reports bias, MAE, RMSE and % within +-0.25 / 0.5 m, overall and by distance from camera.
Location: share of AI sidewalk samples that fall on/near an official sidewalk polygon.
Objects:  AI detections are de-duplicated (same class within 1.5 m = one object), then matched to official
          assets of the same family within --obj-match-m. Precision = matched AI objects / AI objects;
          recall = matched official assets / official assets that a camera actually looked at.

Usage (AI environment):
    python score.py --area-dir ~/sidewalk-data/dc_adams_morgan --gt-dir ../benchmark_dc/ground_truth --out ../benchmark_dc/results
"""
import argparse
import json
import os

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.cluster import DBSCAN

# AI object class -> official DC layers that count as a correct match
OBJECT_FAMILIES = {
    "utility_pole": ["dc_traffic_poles", "dc_street_lights", "dc_sign_supports", "dc_parking_meters"],
    "street_light": ["dc_street_lights", "dc_traffic_poles"],
    "sign_post": ["dc_sign_supports", "dc_traffic_poles", "dc_parking_meters"],
    "cabinet": ["dc_signal_cabinets"],
}


def load(path, crs):
    g = gpd.read_file(path)
    return g.to_crs(crs) if len(g) else g.set_crs(4326, allow_override=True).to_crs(crs)


def width_stats(err):
    a = np.abs(err)
    return {"n": int(len(err)), "bias_m": round(float(np.mean(err)), 3), "mae_m": round(float(np.mean(a)), 3),
            "rmse_m": round(float(np.sqrt(np.mean(err ** 2))), 3), "median_abs_m": round(float(np.median(a)), 3),
            "within_0.25m_pct": round(100 * float(np.mean(a <= 0.25)), 1), "within_0.5m_pct": round(100 * float(np.mean(a <= 0.5)), 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--gt-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--match-m", type=float, default=1.5)
    ap.add_argument("--obj-match-m", type=float, default=3.0)
    ap.add_argument("--widths", default="width_samples.geojson", help="AI width file in outputs/ (e.g. width_samples_fused.geojson)")
    ap.add_argument("--objects", default="objects_raw.geojson")
    ap.add_argument("--transects", default="width_transects.geojson", help="fused transect file in outputs/")
    ap.add_argument("--station-window", type=float, default=4.0, help="metres searched beyond the AI run along the transect")
    ap.add_argument("--complete-only", action="store_true", help="score only transects not cut by occlusion")
    ap.add_argument("--min-filled", type=float, default=0.0, help="ignore AI widths whose patch is less filled than this")
    a = ap.parse_args()
    area = os.path.expanduser(a.area_dir)
    os.makedirs(a.out, exist_ok=True)

    sw = gpd.read_file(os.path.join(a.gt_dir, "dc_sidewalks_2023.geojson"))
    crs = sw.estimate_utm_crs()
    sw = sw.to_crs(crs)
    gtw = load(os.path.join(a.gt_dir, "gt_width_points.geojson"), crs)
    aiw = load(os.path.join(area, "outputs", a.widths), crs)
    if a.complete_only and "complete" in aiw.columns:
        aiw = aiw[aiw["complete"].astype(bool)]
    report = {}

    # ---------------- widths
    if len(aiw):
        aiw = aiw[aiw["filled_frac"] >= a.min_filled].copy()
        sw_union = sw.geometry.union_all()
        aiw["dist_to_gt_sidewalk_m"] = aiw.geometry.distance(sw_union)
        report["location"] = {
            "ai_samples": int(len(aiw)),
            "on_official_sidewalk_pct": round(100 * float((aiw.dist_to_gt_sidewalk_m <= 0.01).mean()), 1),
            "within_1m_pct": round(100 * float((aiw.dist_to_gt_sidewalk_m <= 1.0).mean()), 1),
            "within_3m_pct": round(100 * float((aiw.dist_to_gt_sidewalk_m <= 3.0).mean()), 1),
            "median_offset_m": round(float(aiw.dist_to_gt_sidewalk_m.median()), 2),
        }
        tree = cKDTree(np.c_[gtw.geometry.x, gtw.geometry.y])
        d, idx = tree.query(np.c_[aiw.geometry.x, aiw.geometry.y], distance_upper_bound=a.match_m)
        ok = np.isfinite(d)
        m = aiw[ok].copy()
        m["gt_width_m"] = gtw.gt_width_m.values[idx[ok]]
        m["err_m"] = m.width_m - m.gt_width_m
        report["width_all"] = width_stats(m.err_m.values) if len(m) else {"n": 0}
        report["width_matched_share_pct"] = round(100 * ok.mean(), 1)
        by = {}
        for lo, hi in ((2, 5), (5, 8), (8, 12)):
            if "dist_m" not in m or m.dist_m.max() == 0:
                break
            s = m[(m.dist_m >= lo) & (m.dist_m < hi)]
            if len(s):
                by[f"{lo}-{hi} m from camera"] = width_stats(s.err_m.values)
        report["width_by_distance"] = by
        for lo, hi in ((0, 0.7), (0.7, 0.9), (0.9, 1.01)):
            s = m[(m.filled_frac >= lo) & (m.filled_frac < hi)]
            if len(s):
                report.setdefault("width_by_filled", {})[f"filled {lo}-{hi}"] = width_stats(s.err_m.values)
        # per-location aggregation: many views see the same spot -> median of samples within 2 m of each GT point
        m["gt_idx"] = idx[ok]
        agg = m.groupby("gt_idx").agg(ai_w=("width_m", "median"), gt_w=("gt_width_m", "first"), n=("width_m", "size"))
        report["width_aggregated_per_location"] = width_stats((agg.ai_w - agg.gt_w).values) if len(agg) else {"n": 0}
        # accessibility: can the AI flag sidewalks narrower than 1.2 m?
        if len(agg):
            narrow_gt, narrow_ai = agg.gt_w < 1.2, agg.ai_w < 1.2
            report["flag_under_1.2m"] = {"gt_narrow": int(narrow_gt.sum()),
                                         "sensitivity_pct": round(100 * float((narrow_ai & narrow_gt).sum() / max(1, narrow_gt.sum())), 1),
                                         "precision_pct": round(100 * float((narrow_ai & narrow_gt).sum() / max(1, narrow_ai.sum())), 1)}
        m.drop(columns="geometry").to_csv(os.path.join(a.out, "width_matches.csv"), index=False)

    # ---------------- widths compared at the same street station and side (tolerates GPS shift)
    tp = os.path.join(area, "outputs", a.transects)
    if os.path.exists(tp):
        from shapely.geometry import LineString
        tr = load(tp, crs)
        gt_tree = cKDTree(np.c_[gtw.geometry.x, gtw.geometry.y])
        rows = []
        meth = tr["method"] if "method" in tr.columns else pd.Series(["observed"] * len(tr))
        for g, w, mt in zip(tr.geometry, tr.width_m, meth):
            (x0, y0), (x1, y1) = g.coords[0], g.coords[-1]
            L = max(1e-6, np.hypot(x1 - x0, y1 - y0))
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            win = a.station_window
            line = LineString([(x0 - ux * win, y0 - uy * win), (x1 + ux * win, y1 + uy * win)])
            # official width = the official centreline width point closest to the AI sidewalk along this transect
            # (polygon cuts are unreliable here: DC polygons include lead walks running along the transect)
            mid = g.interpolate(0.5, normalized=True)
            near = gt_tree.query_ball_point([mid.x, mid.y], win + 3)
            cand = [(gtw.geometry.iloc[j].distance(mid), gtw.gt_width_m.iloc[j]) for j in near
                    if gtw.geometry.iloc[j].distance(line) <= 0.75]
            if not cand:
                rows.append((w, np.nan, np.nan, mt))
                continue
            dist_, gw = min(cand)
            rows.append((w, gw, dist_, mt))
        t = pd.DataFrame(rows, columns=["ai_w", "gt_w", "shift_m", "method"]).dropna()
        if len(t):
            report["width_same_station"] = {**width_stats((t.ai_w - t.gt_w).values), "transects_with_official_sidewalk": int(len(t)),
                                            "transects_total": int(len(tr)), "median_lateral_shift_m": round(float(t["shift_m"].median()), 2)}
            report["width_same_station_by_method"] = {k: {**width_stats((g.ai_w - g.gt_w).values)} for k, g in t.groupby("method")}
            t.to_csv(os.path.join(a.out, "width_same_station.csv"), index=False)

    # ---------------- objects
    obj_path = os.path.join(area, "outputs", a.objects)
    if os.path.exists(obj_path):
        ob = load(obj_path, crs)
        cams = gpd.read_file(os.path.join(area, "imagery", "images.geojson")).to_crs(crs)
        done_ids = set(pd.read_csv(os.path.join(area, "outputs", "per_view.csv"), dtype=str).image_id)
        cams = cams[cams["id"].astype(str).isin(done_ids)]   # only photos the AI actually processed
        cam_tree = cKDTree(np.c_[cams.geometry.x, cams.geometry.y])
        res = {}
        for cls, layers in OBJECT_FAMILIES.items():
            o = ob[ob.cls == cls]
            gt = pd.concat([load(os.path.join(a.gt_dir, f"{l}.geojson"), crs) for l in layers if os.path.exists(os.path.join(a.gt_dir, f"{l}.geojson"))])
            gt = gt[gt.geometry.notna() & (gt.geometry.geom_type == "Point")]
            if len(o) == 0 or len(gt) == 0:
                res[cls] = {"ai_objects": int(len(o)), "note": "nothing to match"}
                continue
            xy = np.c_[o.geometry.x, o.geometry.y]
            lab = DBSCAN(eps=1.5, min_samples=1).fit_predict(xy)
            cent = np.array([xy[lab == k].mean(0) for k in np.unique(lab)])
            gxy = np.c_[gt.geometry.x, gt.geometry.y]
            d_ai, _ = cKDTree(gxy).query(cent, distance_upper_bound=a.obj_match_m)
            # official assets a camera actually looked at (within 12 m of a processed photo)
            seen = cam_tree.query(gxy, distance_upper_bound=12.0)[0] < np.inf
            d_gt, _ = cKDTree(cent).query(gxy[seen], distance_upper_bound=a.obj_match_m)
            res[cls] = {"ai_objects_dedup": int(len(cent)), "precision_pct": round(100 * float(np.isfinite(d_ai).mean()), 1),
                        "official_assets_in_view": int(seen.sum()), "recall_pct": round(100 * float(np.isfinite(d_gt).mean()), 1) if seen.sum() else None}
        report["objects"] = res
        report["objects_without_answer_key"] = ob[~ob.cls.isin(list(OBJECT_FAMILIES))].cls.value_counts().to_dict()

    with open(os.path.join(a.out, "score.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
