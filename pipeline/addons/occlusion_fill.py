"""Step 2c: fill sidewalk widths where parked cars (or anything else) hid the sidewalk from every photo.

Sidewalks are regular: along a block side, the curb line and the building/property line are smooth.
For each street side we take the stations where an edge was actually SEEN (inner edge = curb side,
outer edge = building side), fit each edge as a robust local line along the street, and predict both
edges at every 2 m station - including stations nobody could see. Width = outer - inner.

Every output value is labelled:
  seen      both edges observed at that station
  partial   one edge observed, the other predicted
  inferred  both edges predicted (sidewalk hidden at that station)
with gap_m = distance to the nearest station where that edge was seen, and a confidence that falls with gap.

--holdout N   self-test: hide random runs of SEEN stations (N% of them), infer them, report the error
              against the values that were actually seen (and score.py scores against the answer key).

ADD-ON: runs AFTER the main pipeline (measure.py -> fuse_map.py) and does not change it.
Reads only the finished outputs: outputs/sidewalk_map.tif and osm_streets.json.

Usage (AI environment):
    python addons/occlusion_fill.py --area-dir ~/sidewalk-data/dc_adams_morgan [--holdout 30]
Writes outputs/addon_occlusion/width_samples_completed[_holdout].geojson
"""
import argparse
import json
import math
import os
from collections import defaultdict

import numpy as np
from pyproj import Transformer

WINDOW = 15.0     # metres either side used to fit an edge locally
MAX_GAP = 25.0    # do not infer further than this from any seen edge
STEP = 2.0


def utm_epsg(lon, lat):
    return (32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1


def fit_edge(ch, off, at):
    """Robust local line fit of edge offset vs chainage, evaluated at chainage `at`."""
    sel = np.abs(ch - at) <= WINDOW
    if sel.sum() < 2:
        sel = np.argsort(np.abs(ch - at))[:3]
    c, o = ch[sel], off[sel]
    if len(c) >= 3 and np.ptp(c) > 1.0:
        # Theil-Sen style: median slope, median intercept (resists outliers)
        i, j = np.triu_indices(len(c), 1)
        dc = c[j] - c[i]
        ok = np.abs(dc) > 0.5
        slope = float(np.median((o[j] - o[i])[ok] / dc[ok])) if ok.any() else 0.0
        slope = float(np.clip(slope, -0.15, 0.15))   # edges run nearly parallel to the street
        icpt = float(np.median(o - slope * c))
        return icpt + slope * at
    return float(np.median(o))


def complete_side(st, hide=None):
    """st: list of station dicts for one street side. hide: set of indices treated as unseen (self-test)."""
    hide = hide or set()
    ch = np.array([s["chain_m"] for s in st])
    inn_seen = np.array([s["inner_seen"] and i not in hide for i, s in enumerate(st)])
    out_seen = np.array([s["outer_seen"] and i not in hide for i, s in enumerate(st)])
    inner = np.array([s["inner_m"] for s in st], float)
    outer = np.array([s["outer_m"] for s in st], float)
    if inn_seen.sum() < 2 or out_seen.sum() < 2:
        return []
    lo, hi = min(ch[inn_seen].min(), ch[out_seen].min()), max(ch[inn_seen].max(), ch[out_seen].max())
    grid = np.arange(math.floor(lo / STEP) * STEP + STEP / 2, hi + 1e-6, STEP)
    res = []
    for g in grid:
        k = int(np.argmin(np.abs(ch - g)))
        here = abs(ch[k] - g) < STEP / 2
        gi = float(np.min(np.abs(ch[inn_seen] - g)))
        go = float(np.min(np.abs(ch[out_seen] - g)))
        if min(gi, go) > MAX_GAP:
            continue
        if here and inn_seen[k]:
            i_v, i_src = inner[k], "seen"
        else:
            i_v, i_src = fit_edge(ch[inn_seen], inner[inn_seen], g), "inferred"
        if here and out_seen[k]:
            o_v, o_src = outer[k], "seen"
        else:
            o_v, o_src = fit_edge(ch[out_seen], outer[out_seen], g), "inferred"
        w = o_v - i_v
        if not (0.4 <= w <= 12):
            continue
        status = "seen" if (i_src == o_src == "seen") else ("partial" if "seen" in (i_src, o_src) else "inferred")
        gap = max(gi if i_src == "inferred" else 0.0, go if o_src == "inferred" else 0.0)
        conf = 1.0 if status == "seen" else round(max(0.1, 1.0 - gap / MAX_GAP) * (0.9 if status == "partial" else 0.75), 2)
        res.append({"chain_m": round(float(g), 2), "inner_m": round(float(i_v), 3), "outer_m": round(float(o_v), 3),
                    "width_m": round(float(w), 3), "status": status, "gap_m": round(gap, 1), "confidence": conf, "k": k})
    return res


STREET_TYPES = {"primary", "secondary", "tertiary", "residential", "unclassified", "living_street",
                "primary_link", "secondary_link", "tertiary_link", "trunk", "service"}


def stations_from_map(area):
    """Own transects over the finished sidewalk map (1 sidewalk, 2 road, 3 grass, 0 not seen)."""
    import rasterio
    out = os.path.join(area, "outputs")
    with rasterio.open(os.path.join(out, "sidewalk_map.tif")) as src:
        lab = src.read(1)
        tr = src.transform
        epsg = src.crs.to_epsg()
    res = tr.a
    E0, N1 = tr.c, tr.f
    H, W = lab.shape
    sidewalk, observed = lab == 1, lab > 0
    ways = json.load(open(os.path.join(area, "osm_streets.json"), encoding="utf-8"))
    to_utm = Transformer.from_crs(4326, epsg, always_xy=True)
    step = res / 2
    offsets = np.arange(1.0, 20.0, step)
    st = []
    for wy in ways:
        if wy["highway"] not in STREET_TYPES:
            continue
        xy = np.array([to_utm.transform(*c) for c in wy["coords"]])
        chain = 0.0
        for (x0, y0), (x1, y1) in zip(xy[:-1], xy[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 1:
                chain += L
                continue
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            for t in np.arange(STEP / 2, L, STEP):
                px, py = x0 + ux * t, y0 + uy * t
                for sgn, side in ((1, "left"), (-1, "right")):
                    nx, ny = -uy * sgn, ux * sgn
                    cols = ((px + nx * offsets - E0) / res).astype(int)
                    rows = ((N1 - (py + ny * offsets)) / res).astype(int)
                    if not ((cols >= 0) & (cols < W) & (rows >= 0) & (rows < H)).all():
                        continue
                    sw, ob = sidewalk[rows, cols], observed[rows, cols]
                    rec = {"osm_way": wy["id"], "street": wy.get("name"), "side": side, "chain_m": round(chain + float(t), 2),
                           "sx": px, "sy": py, "nx": nx, "ny": ny, "ux": ux, "uy": uy,
                           "inner_seen": False, "outer_seen": False, "inner_m": np.nan, "outer_m": np.nan, "width_m": np.nan}
                    if sw.any():
                        i0 = int(np.argmax(sw))
                        j, gap = i0, 0
                        while j + 1 < len(sw) and (sw[j + 1] or gap < 3):
                            gap = 0 if sw[j + 1] else gap + 1
                            j += 1
                        while j > i0 and not sw[j]:
                            j -= 1
                        rec["inner_m"], rec["outer_m"] = float(offsets[i0]), float(offsets[j]) + step
                        rec["width_m"] = rec["outer_m"] - rec["inner_m"]
                        # an edge counts as SEEN only if the cell beyond it was observed as non-sidewalk
                        rec["inner_seen"] = bool(i0 > 0 and ob[i0 - 1] and not sw[i0 - 1])
                        rec["outer_seen"] = bool(j + 1 < len(sw) and ob[j + 1])
                    st.append(rec)
            chain += L
    return st, epsg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--holdout", type=float, default=0.0, help="percent of seen stations to hide for a self-test")
    a = ap.parse_args()
    area = os.path.expanduser(a.area_dir)
    out_dir = os.path.join(area, "outputs", "addon_occlusion")
    os.makedirs(out_dir, exist_ok=True)
    allst, epsg = stations_from_map(area)
    to_ll = Transformer.from_crs(epsg, 4326, always_xy=True)
    sides = defaultdict(list)
    for p in allst:
        sides[(p["osm_way"], p["side"])].append(p)
    rng = np.random.default_rng(42)
    feats, test = [], []
    for key, st in sides.items():
        st.sort(key=lambda s: s["chain_m"])
        hide = set()
        if a.holdout:
            # hide runs of 2-5 consecutive fully-seen stations (4-10 m), like a parked car or two
            seen_idx = [i for i, s in enumerate(st) if s["inner_seen"] and s["outer_seen"]]
            target = int(len(seen_idx) * a.holdout / 100)
            tries = 0
            while len(hide) < target and tries < 200:
                tries += 1
                i0 = int(rng.choice(seen_idx))
                hide.update(range(i0, min(len(st), i0 + int(rng.integers(2, 6)))))
        for r in complete_side(st, hide):
            s = st[r["k"]]
            px = s["sx"] + (r["chain_m"] - s["chain_m"]) * s["ux"]
            py = s["sy"] + (r["chain_m"] - s["chain_m"]) * s["uy"]
            mid = (r["inner_m"] + r["outer_m"]) / 2
            lon, lat = to_ll.transform(px + s["nx"] * mid, py + s["ny"] * mid)
            props = {"osm_way": s["osm_way"], "street": s["street"], "side": s["side"], **{k: v for k, v in r.items() if k != "k"},
                     "complete": True, "filled_frac": 1.0, "dist_m": 0.0, "held_out": r["k"] in hide and abs(s["chain_m"] - r["chain_m"]) < 1}
            feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props})
            if props["held_out"]:
                test.append(r["width_m"] - s["width_m"])
    name = "width_samples_completed" + ("_holdout" if a.holdout else "") + ".geojson"
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(out_dir, name), "w"))
    from collections import Counter
    c = Counter(f["properties"]["status"] for f in feats)
    print(f"wrote {name}: {len(feats)} stations -> seen {c['seen']}, partial {c['partial']}, inferred {c['inferred']}")
    if test:
        e = np.array(test)
        print(f"self-test on {len(e)} hidden stations: bias {e.mean():+.2f} m, MAE {np.abs(e).mean():.2f} m, "
              f"within 0.25 m {100 * (np.abs(e) <= .25).mean():.0f}%, within 0.5 m {100 * (np.abs(e) <= .5).mean():.0f}%")


if __name__ == "__main__":
    main()
