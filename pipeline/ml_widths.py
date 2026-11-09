"""Step 2d (experimental): classical ML on top of the per-photo edge widths, evaluated on the DC benchmark.

  1. Learned quality model: gradient boosting predicts each photo's width error from geometry / visibility
     features (no location, no street names -> transferable to Beirut).
  2. Inverse-variance weighting: each station combines its photos weighted by 1 / predicted error^2.
  3. Smoothing along the street: weighted running median of station widths along each block face.
  4. Conformal abstention: stations are ranked by predicted error; accuracy is reported when only the most
     confident share is published, plus an honest 90 % interval.

Everything is scored OUT-OF-FOLD with spatial cross-validation (250 m blocks): a station's prediction never
comes from a model that saw its neighbourhood.

Usage: python ml_widths.py --rows A/outputs/view_station_rows_X.csv [B/...csv] --gt ../benchmark_dc/ground_truth/gt_width_points.geojson
"""
import argparse
import json

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold

NUM = ["w", "c", "spread", "seen_frac", "k", "cam_ratio", "cam_h_scaled", "rng_med", "rng_min", "n_sw", "n_road", "n_bld",
       "n_terr", "heading_fix", "gps_shift", "corner_d", "u_span", "n_curb", "n_back", "station_u_off", "n_views_station"]
CAT = ["edge_method", "view_dir", "highway", "pano"]


def stats(err):
    err = np.asarray(err)
    a = np.abs(err)
    return {"n": int(len(a)), "mae": round(float(a.mean()), 3), "bias": round(float(err.mean()), 3),
            "median": round(float(np.median(a)), 3), "within_0.5": round(float((a <= 0.5).mean() * 100), 1)}


def gt_for_stations(st, gt_path, epsg):
    gt = gpd.read_file(gt_path).to_crs(epsg)
    tree = cKDTree(np.c_[gt.geometry.x, gt.geometry.y])
    gx, gy, gw = gt.geometry.x.values, gt.geometry.y.values, gt.gt_width_m.values
    tf = Transformer.from_crs(4326, epsg, always_xy=True)
    out = []
    for r in st.itertuples():
        x0, y0 = tf.transform(r.c_lon, r.c_lat)
        x1, y1 = tf.transform(r.b_lon, r.b_lat)
        L = max(1e-6, np.hypot(x1 - x0, y1 - y0))
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        line = LineString([(x0 - ux * 4, y0 - uy * 4), (x1 + ux * 4, y1 + uy * 4)])
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        best = None
        for j in tree.query_ball_point([mx, my], 7):
            p = Point(gx[j], gy[j])
            if p.distance(line) <= 0.75:
                dd = np.hypot(gx[j] - mx, gy[j] - my)
                if best is None or dd < best[0]:
                    best = (dd, gw[j])
        out.append(best[1] if best else np.nan)
    return np.array(out), tf


def wmedian(v, w):
    o = np.argsort(v)
    v, w = np.asarray(v)[o], np.asarray(w)[o]
    cw = np.cumsum(w)
    return float(v[np.searchsorted(cw, cw[-1] / 2)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", nargs="+", required=True)
    ap.add_argument("--gt", required=True)
    ap.add_argument("--smooth-m", type=float, nargs="+", default=[6.0, 10.0])
    ap.add_argument("--no-width-features", action="store_true", help="do not let the model see the measured width / curb offset")
    ap.add_argument("--group-by", default="block", choices=["block", "sequence"], help="what is held out in cross-validation")
    ap.add_argument("--out", default=None, help="write the comparison as JSON here")
    a = ap.parse_args()
    df = pd.concat([pd.read_csv(p, dtype={"sequence": str}).assign(dataset=p) for p in a.rows], ignore_index=True)
    df["station"] = df["dataset"].str.slice(-40) + "|" + df["station"].astype(str)
    st = df.groupby("station").first()[["c_lon", "c_lat", "b_lon", "b_lat", "osm_way", "side_name", "s_along", "dataset"]]
    epsg = 32618 if st.c_lon.mean() < -72 else 32636
    st["gt_w"], tf = gt_for_stations(st, a.gt, epsg)
    xy = np.array([tf.transform(lo, la) for lo, la in zip(st.c_lon, st.c_lat)])
    st["block"] = [f"{int(x // 250)}_{int(y // 250)}" for x, y in xy]
    df = df.join(st[["gt_w", "block"]], on="station")
    df["err"] = df.w - df.gt_w

    X = df[[f for f in NUM if not (a.no_width_features and f in ("w", "c"))]].copy()
    for c in CAT:
        X = X.join(pd.get_dummies(df[c].astype(str), prefix=c).astype(float))
    has = df.gt_w.notna().values
    pred_abs = np.full(len(df), np.nan)
    pred_sig = np.full(len(df), np.nan)
    groups = (df.block if a.group_by == "block" else df.sequence).astype(str).values
    gkf = GroupKFold(n_splits=5)
    lab_idx = np.nonzero(has)[0]
    for tr, te in gkf.split(lab_idx, groups=groups[lab_idx]):
        tr_i, te_blocks = lab_idx[tr], set(groups[lab_idx[te]])
        m_abs = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
                                              loss="absolute_error").fit(X.values[tr_i], np.abs(df.err.values[tr_i]))
        m_sig = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
                                              loss="absolute_error").fit(X.values[tr_i], df.err.values[tr_i])
        te_all = np.isin(groups, list(te_blocks))          # every row in the held-out blocks (labelled or not)
        pred_abs[te_all] = m_abs.predict(X.values[te_all])
        pred_sig[te_all] = m_sig.predict(X.values[te_all])
    df["pred_abs"] = np.clip(pred_abs, 0.05, None)
    df["pred_sig"] = pred_sig
    df = df[df.pred_abs.notna()]

    # ---- station aggregation variants
    def aggregate(g, mode):
        if mode == "median":
            return float(np.median(g.w)), float(np.median(g.pred_abs))
        wts = 1.0 / g.pred_abs.values ** 2
        w = g.w.values - (g.pred_sig.values if mode == "weighted+bias" else 0.0)
        return float(np.sum(wts * w) / wts.sum()), float(1.0 / np.sqrt(wts.sum()))
    res = {}
    station_tables = {}
    for mode in ("median", "weighted", "weighted+bias"):
        rows = []
        for sk, g in df.groupby("station"):
            w, pe = aggregate(g, mode)
            rows.append((sk, w, pe))
        t = pd.DataFrame(rows, columns=["station", "w", "pred_err"]).set_index("station").join(st)
        station_tables[mode] = t
        lab = t[t.gt_w.notna()]
        res[mode] = stats(lab.w - lab.gt_w)
        for ds, g in lab.groupby("dataset"):
            res[f"{mode} [{'pano' if 'pano' in ds else 'foot'}]"] = stats(g.w - g.gt_w)
    # ---- smoothing along each block face (weighted running median, weights = 1/pred_err^2)
    for base in ("weighted", "weighted+bias"):
        for L in a.smooth_m:
            t = station_tables[base].copy()
            sm = np.full(len(t), np.nan)
            for _, g in t.groupby(["dataset", "osm_way", "side_name"]):
                s, w, pe = g.s_along.values, g.w.values, g.pred_err.values
                for i, (si, ix) in enumerate(zip(s, g.index)):
                    m = np.abs(s - si) <= L / 2
                    sm[t.index.get_loc(ix)] = wmedian(w[m], 1.0 / pe[m] ** 2)
            t["w"] = sm
            station_tables[f"{base} + smooth {L:g} m"] = t
            lab = t[t.gt_w.notna()]
            res[f"{base} + smooth {L:g} m"] = stats(lab.w - lab.gt_w)
    # ---- abstention: publish only the most confident share of stations (ranked by predicted error)
    best_name = min((k for k in res if "[" not in k), key=lambda k: res[k]["mae"])
    t = station_tables[best_name]
    lab = t[t.gt_w.notna()].sort_values("pred_err")
    abst = {}
    for keep in (1.0, 0.75, 0.5, 0.25):
        sub = lab.iloc[: max(1, int(len(lab) * keep))]
        abst[f"keep {int(keep * 100)}%"] = stats(sub.w - sub.gt_w)
    # conformal 90 % interval: half-width = q * pred_err with q from half the stations, checked on the other half
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(lab))
    cal, chk = lab.iloc[idx[: len(idx) // 2]], lab.iloc[idx[len(idx) // 2:]]
    q = float(np.quantile(np.abs(cal.w - cal.gt_w) / cal.pred_err, 0.9))
    cover = float((np.abs(chk.w - chk.gt_w) <= q * chk.pred_err).mean())
    half = q * chk.pred_err
    report = {"view_rows": int(len(df)), "stations_with_truth": int(st.gt_w.notna().sum()), "variants": res, "best": best_name,
              "abstention_on_best": abst,
              "conformal_90": {"empirical_coverage": round(cover, 3), "median_half_width_m": round(float(half.median()), 2),
                               "share_with_half_width_le_0.5m": round(float((half <= 0.5).mean()), 3)}}
    print(json.dumps(report, indent=1))
    if a.out:
        json.dump(report, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
