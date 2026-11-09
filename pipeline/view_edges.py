"""Step 2c: sidewalk width from the two EDGES seen in each photo, bridging parked cars.

Idea: a curb and a building line are straight along a block. Within one photo the camera sees ~15-20 m
of sidewalk; parked cars hide parts of it, but the curb edge is visible before and after each car (where
road shows next to the sidewalk), and the back edge is visible wherever a building / wall base or
other ground shows beyond the sidewalk. Each edge is therefore estimated from its SEEN pieces only, as
a straight line along the street, and the width is the distance between the two lines - also behind the
car. Working inside each photo (instead of on the fused map) keeps the two edges in the same camera
geometry, so GPS / heading errors between photos cannot smear them.

Then every 2 m station along each street side takes the median width over all photos that saw it.

Usage: python view_edges.py --area-dir ~/sidewalk-data/dc_adams_morgan_pano
Writes outputs/width_transects_views.geojson and width_samples_views.geojson
"""
import argparse
import glob
import json
import math
import os
from collections import defaultdict

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree

from fuse_map import STREET_TYPES, osm_streets, utm_epsg

BIN = 0.5          # metres along the street per edge sample
EDGE_BAND = 0.6    # how close the road / building evidence must be to call an edge "seen"


def street_segments(ways, to_utm):
    segs = []
    for wy in ways:
        if wy["highway"] not in STREET_TYPES:
            continue
        xy = np.array([to_utm.transform(*c) for c in wy["coords"]])
        s0 = 0.0
        for k, (p0, p1) in enumerate(zip(xy[:-1], xy[1:])):
            L = float(np.hypot(*(p1 - p0)))
            if L >= 2:
                segs.append({"way": wy, "k": k, "p0": p0, "u": (p1 - p0) / L, "L": L, "s0": s0})
            s0 += L
    mids = np.array([s["p0"] + s["u"] * s["L"] / 2 for s in segs])
    return segs, cKDTree(mids)


def view_edges(P_uv, codes, bld_dist_back, a):
    """P_uv: points in the street frame (u along street, v = signed offset from the centreline, already
    flipped so the sidewalk side is positive). Returns dict or None."""
    u, v = P_uv[:, 0], P_uv[:, 1]
    sw = codes == 1
    if sw.sum() < 150:
        return None
    ub = np.floor(u / BIN).astype(int)
    curb_s, back_s, u_seen = [], [], []
    for b in np.unique(ub[sw]):
        inb = ub == b
        vs = v[inb & sw]
        if len(vs) < 4:
            continue
        lo, hi = np.percentile(vs, 3), np.percentile(vs, 97)
        u_seen.append(b)
        # curb edge seen: road visible just street-side of the sidewalk in this bin
        road = v[inb & (codes == 2)]
        if np.any((road < lo) & (road >= lo - EDGE_BAND)):
            curb_s.append((b, lo))
        # back edge seen: a building / wall / fence base, or other ground, just beyond it
        beyond = v[inb & ((codes == 4) | (codes == 3) | (codes == 2))]
        if np.any((beyond > hi) & (beyond <= hi + EDGE_BAND)) or bld_dist_back(b, hi) <= 0.8:
            back_s.append((b, hi))
    if len(curb_s) < a.min_edge_bins or len(back_s) < a.min_edge_bins:
        return None
    curb_s, back_s = np.array(curb_s, float), np.array(back_s, float)
    # straight edge along the street: robust (median) offset; the seen pieces before and after a car
    # define where the edge runs behind it
    c = float(np.median(curb_s[:, 1]))
    bk = float(np.median(back_s[:, 1]))
    spread_c = float(np.median(np.abs(curb_s[:, 1] - c)))
    spread_b = float(np.median(np.abs(back_s[:, 1] - bk)))
    if spread_c > a.max_spread or spread_b > a.max_spread:
        return None                         # edge is not a straight line here (corner, driveway, bad view)
    w = bk - c
    if not (0.5 <= w <= 10):
        return None
    u_lo, u_hi = min(u_seen) * BIN, (max(u_seen) + 1) * BIN
    seen_frac = len(u_seen) / max(1, (max(u_seen) - min(u_seen) + 1))
    return {"curb": c, "back": bk, "width": w, "u_lo": u_lo, "u_hi": u_hi, "n_curb": len(curb_s), "n_back": len(back_s),
            "seen_frac": seen_frac, "spread": max(spread_c, spread_b)}


def line_edges(U, V, c, swm):
    """Edges from the straight lines fitted in the image (codes 5 = curb side, 6 = back side)."""
    m5, m6 = c == 5, c == 6
    if m5.sum() < 8 or m6.sum() < 8:
        return None

    def fit(m):
        sl, ic = np.linalg.lstsq(np.c_[U[m], np.ones(int(m.sum()))], V[m], rcond=None)[0]
        return sl, ic
    s5, i5 = fit(m5)
    s6, i6 = fit(m6)
    a5, a6 = math.degrees(math.atan(s5)), math.degrees(math.atan(s6))
    if abs(a5 - a6) > 8 or abs(a5) > 20:          # edges must run along the street and be parallel
        return None
    lo = max(U[m5].min(), U[m6].min(), U[swm].min())
    hi = min(U[m5].max(), U[m6].max(), U[swm].max())
    if hi - lo < 2.0:
        return None
    um = (lo + hi) / 2
    cv, bv = s5 * um + i5, s6 * um + i6
    w = bv - cv
    if not (0.5 <= w <= 10) or cv < 0.5:
        return None
    ub = np.unique(np.floor(U[swm & (U >= lo) & (U <= hi)] / BIN).astype(int))
    seen_frac = len(ub) / max(1.0, (hi - lo) / BIN)
    return {"curb": float(cv), "back": float(bv), "width": float(w), "u_lo": float(lo), "u_hi": float(hi),
            "n_curb": int(m5.sum()), "n_back": int(m6.sum()), "seen_frac": float(min(1.0, seen_frac)), "spread": 0.0}


def intersections(ways, to_utm):
    """OSM street nodes shared by two or more street ways (or repeated) = intersections."""
    from collections import Counter
    cnt = Counter()
    for wy in ways:
        if wy["highway"] not in STREET_TYPES:
            continue
        for i, cc in enumerate(wy["coords"]):
            key = (round(cc[0], 7), round(cc[1], 7))
            cnt[key] += 2 if 0 < i < len(wy["coords"]) - 1 else 1
    pts = [to_utm.transform(*k) for k, v in cnt.items() if v >= 3]
    return cKDTree(np.array(pts)) if pts else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--min-edge-bins", type=int, default=3, help="seen samples (x0.5 m) needed for each edge")
    ap.add_argument("--max-spread", type=float, default=0.35, help="max median deviation of an edge from a straight line (m)")
    ap.add_argument("--max-range", type=float, default=12.0)
    ap.add_argument("--station-m", type=float, default=2.0)
    ap.add_argument("--no-align", action="store_true")
    ap.add_argument("--no-calib", action="store_true", help="ignore sequence_scale.csv")
    ap.add_argument("--use-lines", action="store_true", help="use the straight edge lines fitted in the image (codes 5/6)")
    ap.add_argument("--corner-m", type=float, default=0.0, help="skip views whose sidewalk is within this distance of an intersection")
    ap.add_argument("--out-suffix", default="", help="suffix for the output files (experiments)")
    a = ap.parse_args()
    area = os.path.expanduser(a.area_dir)
    out = os.path.join(area, "outputs")
    meta = json.load(open(os.path.join(area, "imagery", "images.geojson")))["features"]
    lons = [f["geometry"]["coordinates"][0] for f in meta]
    lats = [f["geometry"]["coordinates"][1] for f in meta]
    epsg = utm_epsg(np.mean(lons), np.mean(lats))
    to_utm = Transformer.from_crs(4326, epsg, always_xy=True)
    to_ll = Transformer.from_crs(epsg, 4326, always_xy=True)
    ways = osm_streets(None, os.path.join(area, "osm_streets.json"))
    segs, seg_tree = street_segments(ways, to_utm)
    corner_tree = intersections(ways, to_utm) if a.corner_m > 0 else None
    any_corner = intersections(ways, to_utm)
    bld_tree = None
    if os.path.exists(os.path.join(area, "osm_buildings.json")):
        from align import densify
        ref = densify(json.load(open(os.path.join(area, "osm_buildings.json"))), to_utm)
        bld_tree = cKDTree(ref) if len(ref) else None

    log = pd.read_csv(os.path.join(out, "per_view.csv"))
    from fuse_map import sequence_heights
    est_h, ref_h = sequence_heights(out, log, not getattr(a, "no_calib", False))
    shifts, view_rot = {}, {}
    if not a.no_align:
        sp = os.path.join(out, "sequence_shifts.csv")
        if os.path.exists(sp):
            sdf = pd.read_csv(sp, dtype={"sequence": str})
            shifts = {r.sequence: (r.dx, r.dy) for r in sdf.itertuples() if r.accepted}
        hp = os.path.join(out, "view_heading_fixes.csv")
        if os.path.exists(hp):
            view_rot = dict(pd.read_csv(hp).itertuples(index=False, name=None))

    per_station = defaultdict(list)
    is_pano = {str(f["properties"]["id"]): bool(f["properties"].get("is_pano")) for f in meta}
    view_log = []
    n_views = n_ok = 0
    for fp in sorted(glob.glob(os.path.join(out, "bev", "*.npz"))):
        z = np.load(fp)
        cam_h = float(z["cam_h"])
        if cam_h <= 0:
            continue
        k = ref_h.get(str(z["seq"]), cam_h) / cam_h
        if not (0.75 <= est_h.get(str(z["seq"]), cam_h) / cam_h <= 1.33):
            continue
        n_views += 1
        P = z["pts"].astype(np.float32)
        x, y, c = P[:, 0] * k, P[:, 1] * k, P[:, 2].astype(int)
        r = np.hypot(x, y)
        keep = (r <= a.max_range) | (c >= 4)
        x, y, c = x[keep], y[keep], c[keep]
        dx, dy = shifts.get(str(z["seq"]), (0.0, 0.0))
        hd = math.radians(float(z["h"]) + view_rot.get(os.path.basename(fp)[:-4], 0.0))
        e = float(z["ce"]) + dx + y * math.sin(hd) + x * math.cos(hd)
        n = float(z["cn"]) + dy + y * math.cos(hd) - x * math.sin(hd)
        swm = c == 1
        if swm.sum() < 150:
            continue
        cen = np.array([np.median(e[swm]), np.median(n[swm])])
        _, j = seg_tree.query(cen)
        sg = segs[j]
        ux, uy = sg["u"]
        rel = np.c_[e, n] - sg["p0"]
        U = rel @ np.array([ux, uy])
        V = rel @ np.array([-uy, ux])                  # + = left of the street direction
        side = 1.0 if np.median(V[swm]) >= 0 else -1.0
        V = V * side
        if np.median(V[swm]) > 20:
            continue

        def bld_dist_back(b, v_back, sg=sg, side=side):
            if bld_tree is None:
                return 99.0
            uu = (b + 0.5) * BIN
            px = sg["p0"] + sg["u"] * uu + np.array([-uy, ux]) * side * v_back
            return bld_tree.query(px)[0]

        if corner_tree is not None and corner_tree.query(cen)[0] < a.corner_m:
            continue
        res = line_edges(U, V, c, swm) if a.use_lines else None
        used = "line" if res is not None else "bins"
        if res is None:
            res = view_edges(np.c_[U, V], c, bld_dist_back, a)
        if res is None:
            continue
        n_ok += 1
        view_log.append({"view": os.path.basename(fp)[:-4], "width": round(res["width"], 2), "curb": round(res["curb"], 2),
                         "back": round(res["back"], 2), "seg": j, "side": side, "seen_frac": round(res["seen_frac"], 2)})
        # contribute to every station this view's seen sidewalk spans
        side_name = "left" if side > 0 else "right"
        s_lo, s_hi = max(0.0, res["u_lo"]), min(sg["L"], res["u_hi"])
        for st in np.arange(math.floor(s_lo / a.station_m), math.ceil(s_hi / a.station_m)):
            t = (st + 0.5) * a.station_m
            if t > sg["L"]:
                continue
            rr_sw = np.hypot(x, y)[swm]
            feats = {"view": os.path.basename(fp)[:-4], "sequence": str(z["seq"]), "k": float(k),
                     "cam_ratio": float(cam_h / est_h.get(str(z["seq"]), cam_h)), "cam_h_scaled": float(cam_h * k),
                     "rng_med": float(np.median(rr_sw)), "rng_min": float(np.percentile(rr_sw, 5)),
                     "n_sw": int(swm.sum()), "n_road": int((c == 2).sum()), "n_bld": int((c == 4).sum()), "n_terr": int((c == 3).sum()),
                     "heading_fix": abs(float(view_rot.get(os.path.basename(fp)[:-4], 0.0))), "gps_shift": float(math.hypot(dx, dy)),
                     "corner_d": float(any_corner.query(cen)[0]) if any_corner is not None else 99.0,
                     "u_span": float(res["u_hi"] - res["u_lo"]), "n_curb": int(res.get("n_curb", 0)), "n_back": int(res.get("n_back", 0)),
                     "edge_method": used, "highway": sg["way"]["highway"], "view_dir": os.path.basename(fp)[:-4].rsplit("_", 1)[1],
                     "station_u_off": float(abs(t - (res["u_lo"] + res["u_hi"]) / 2))}
            per_station[(sg["way"]["id"], sg["k"], side_name, int(st))].append(
                {"w": res["width"], "c": res["curb"], "b": res["back"], "seg": j, "side": side, "t": t, "feats": feats,
                 "spread": res["spread"], "seen_frac": res["seen_frac"],
                 "pano": bool(is_pano.get(os.path.basename(fp)[:-4].rsplit("_", 1)[0], False))})

    samples, transects, rows_out = [], [], []
    for (wid, kseg, side_name, st), L in per_station.items():
        sg = segs[L[0]["seg"]]
        ws = np.array([d["w"] for d in L])
        w = float(np.median(ws))
        c = float(np.median([d["c"] for d in L]))
        b = c + w
        t = L[0]["t"]
        side = L[0]["side"]
        nrm = np.array([-sg["u"][1], sg["u"][0]]) * side
        base = sg["p0"] + sg["u"] * t
        p_c, p_b = base + nrm * c, base + nrm * b
        props = {"osm_way": wid, "street": sg["way"]["name"], "highway": sg["way"]["highway"], "side": side_name,
                 "width_m": round(w, 2), "n_views": len(L), "width_spread_m": round(float(np.median(np.abs(ws - w))), 2),
                 "seen_frac": round(float(np.median([d["seen_frac"] for d in L])), 2),
                 "method": "edges_bridged" if np.median([d["seen_frac"] for d in L]) < 0.95 else "edges_seen",
                 "source": {(True,): "car 360", (False,): "on-foot"}.get(tuple(set(d["pano"] for d in L)), "mixed"),
                 "complete": True, "filled_frac": 1.0, "dist_m": 0.0, "offset_from_centreline_m": round(c, 2)}
        mid = (p_c + p_b) / 2
        skey = f"{wid}_{kseg}_{side_name}_{st}"
        lc, lb = to_ll.transform(*p_c), to_ll.transform(*p_b)
        s_along = sg["s0"] + t
        for d in L:
            rows_out.append({"station": skey, "osm_way": wid, "side_name": side_name, "s_along": s_along,
                             "c_lon": lc[0], "c_lat": lc[1], "b_lon": lb[0], "b_lat": lb[1],
                             "w": d["w"], "c": d["c"], "spread": d["spread"], "seen_frac": d["seen_frac"],
                             "pano": d["pano"], "n_views_station": len(L), **d["feats"]})
        samples.append({"type": "Feature", "properties": props, "geometry": {"type": "Point", "coordinates": list(to_ll.transform(*mid))}})
        transects.append({"type": "Feature", "properties": props, "geometry": {"type": "LineString", "coordinates": [
            list(to_ll.transform(*p_c)), list(to_ll.transform(*p_b))]}})
    sfx = a.out_suffix
    pd.DataFrame(rows_out).to_csv(os.path.join(out, f"view_station_rows{sfx}.csv"), index=False)
    pd.DataFrame(view_log).to_csv(os.path.join(out, f"view_edges_log{sfx}.csv"), index=False)
    json.dump({"type": "FeatureCollection", "features": samples}, open(os.path.join(out, f"width_samples_views{sfx}.geojson"), "w"))
    json.dump({"type": "FeatureCollection", "features": transects}, open(os.path.join(out, f"width_transects_views{sfx}.geojson"), "w"))
    print(f"{n_ok} of {n_views} views gave both edges -> {len(transects)} stations "
          f"(median {np.median([len(v) for v in per_station.values()]) if per_station else 0:.0f} views each)")


if __name__ == "__main__":
    main()
