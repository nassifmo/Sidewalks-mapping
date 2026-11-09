"""Paired comparison: each test vs baseline on the stations BOTH measured (removes station-count effects)."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, r"C:/Users/nassi/OneDrive/Desktop/Sidewalks mapping/pipeline")
from ml_widths import gt_for_stations
H = os.path.expanduser("~/sidewalk-data")
GT = r"C:/Users/nassi/OneDrive/Desktop/Sidewalks mapping/benchmark_dc/ground_truth/gt_width_points.geojson"
def load(d, sfx):
    r = pd.read_csv(f"{H}/{d}/outputs/view_station_rows{sfx}.csv", dtype={"sequence": str})
    r["key"] = r.station.astype(str)
    s = r.groupby("key").agg(w=("w", "median"), c_lon=("c_lon", "first"), c_lat=("c_lat", "first"),
                             b_lon=("b_lon", "first"), b_lat=("b_lat", "first"))
    return s
def st(e):
    a = np.abs(e); return f"n={len(a):4d}  MAE {a.mean():.3f}  median {np.median(a):.3f}  within0.5 {100*(a<=.5).mean():5.1f}%  bias {e.mean():+.3f}"
tests = {"A scale from cars": ("{t}", "_A_scale_from_cars_"), "B tilt sidewalk plane": ("{t}_tilt", "_B_tilt_sidewalk_plane_"),
         "C curb as image line": ("{t}_lines", "_C_curb_as_image_line_"), "C rerun no lines (noise)": ("{t}_lines", "_C_lines_measured_"), "D corners 8m": ("{t}", "_D_corners_8m_recheck_"), "E near-side 8m": ("{t}", "_E_near_side_8m_recheck_")}
for t in ("foot", "pano"):
    base = load(f"dc_adams_morgan_{t}", "_0_baseline_recheck_")
    base["truth"], _ = gt_for_stations(base, GT, 32618)
    print(f"== {t}: baseline (all its stations) {st((base.w-base.truth).dropna().values)}")
    for name, (d, sfx) in tests.items():
        x = load(f"dc_adams_morgan_" + d.format(t=t).replace(f"{t}", t, 1) if False else "dc_adams_morgan_" + d.format(t=t), sfx)
        j = base.join(x[["w"]], rsuffix="_t", how="inner").dropna(subset=["truth"])
        print(f"  {name:26s} common: base {st((j.w-j.truth).values)}\n  {'':26s}         test {st((j.w_t-j.truth).values)}   | only-in-test stations {len(x.index.difference(base.index))}")
