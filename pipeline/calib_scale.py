"""Step 1b: calibrate each photo sequence's camera height using parked cars as a ruler.

The depth model's metric scale drifts between sequences (camera height estimated anywhere from 1.3 to
3.3 m on the same kind of car rig), and every width inherits that error. Inside a single photo, however,
the RATIO between the camera height and a parked car's height does not depend on the scale. Cars are
everywhere in DC and Beirut and their roof height is fairly standard, so for each sequence:

    true camera height = CAR_HEIGHT x median over cars of (estimated camera height / estimated car height)

Only whole cars standing on the ground are used (component not touching the image border, bottom within
0.35 m of the ground plane, height 0.9-2.6 m in estimated units after scaling).

Usage: python calib_scale.py --area-dir ~/sidewalk-data/dc_adams_morgan_pano [--views-per-seq 12] [--car-height 1.5]
Writes outputs/sequence_scale.csv (sequence, rig_height_m, n_cars, ...). fuse_map.py / view_edges.py / align.py
use it automatically when present.
"""
import argparse
import json
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
import torch
from scipy import ndimage

from measure import GROUND, ROAD, Models, fit_plane, travel_bearings, views_for, CROP


def car_ratios(img, lab, pts, valid, M):
    """Return (cam_h, [car roof heights]) in the depth model's own units for one view."""
    ground = np.isin(lab, M.ids(GROUND)) & valid
    road = np.isin(lab, M.ids(ROAD)) & valid
    if ground.sum() < 2000:
        return None, []
    g = pts[road] if road.sum() > 3000 else pts[ground]
    if len(g) > 20000:
        g = g[np.random.default_rng(1).choice(len(g), 20000, replace=False)]
    pl = fit_plane(g)
    if pl is None:
        return None, []
    n, d, _ = pl
    if not (0.8 <= d <= 4.0):
        return None, []
    car = np.isin(lab, M.ids({"Car"})) & valid
    comp, nc = ndimage.label(car)
    H, W = lab.shape
    out = []
    for ci, sl in enumerate(ndimage.find_objects(comp), start=1):
        if sl is None:
            continue
        r0, r1, c0, c1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if r0 <= 2 or c0 <= 2 or c1 >= W - 2 or r1 >= H - 2:      # cut by the image border -> roof may be missing
            continue
        m = comp[sl] == ci
        if m.sum() < 1500:
            continue
        P = pts[sl][m]
        h = P @ n + d                                              # height above the ground plane
        dist = np.median(np.linalg.norm(P, axis=1))
        if dist > 15:
            continue
        lo, hi = np.percentile(h, 2), np.percentile(h, 98)
        if lo > 0.35 * d / 2.0:                                    # bottom not on the ground (hidden / far)
            continue
        out.append(float(hi))
    return float(d), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area-dir", required=True)
    ap.add_argument("--views-per-seq", type=int, default=12, help="photos sampled per sequence")
    ap.add_argument("--car-height", type=float, default=1.5, help="typical parked-car roof height (m)")
    ap.add_argument("--min-cars", type=int, default=3)
    a = ap.parse_args()
    area = os.path.expanduser(a.area_dir)
    out = os.path.join(area, "outputs")
    meta = json.load(open(os.path.join(area, "imagery", "images.geojson")))["features"]
    meta = [f for f in meta if os.path.exists(os.path.join(area, "imagery", "jpg", f"{f['properties']['id']}.jpg"))]
    travel = travel_bearings(meta)
    by_seq = defaultdict(list)
    for f in meta:
        by_seq[f["properties"].get("sequence")].append(f)
    import zlib
    M = Models("cuda" if torch.cuda.is_available() else "cpu")
    # resumable: per-sequence results go to a partial file (the laptop GPU driver can reset mid-run)
    part = os.path.join(out, "sequence_scale.partial.csv")
    rows = pd.read_csv(part, dtype={"sequence": str}).to_dict("records") if os.path.exists(part) else []
    done = {str(r["sequence"]) for r in rows}
    for si, (seq, fs) in enumerate(by_seq.items()):
        if str(seq) in done:
            continue
        rng = np.random.default_rng(zlib.crc32(str(seq).encode()))
        pick = [fs[i] for i in rng.choice(len(fs), min(a.views_per_seq, len(fs)), replace=False)]
        ratios, cam_hs = [], []
        for f in pick:
            p = f["properties"]
            h = p.get("computed_compass_angle") if p.get("computed_compass_angle") is not None else p.get("compass_angle")
            if h is None:
                continue
            for vname, img, vd in views_for(os.path.join(area, "imagery", "jpg", f"{p['id']}.jpg"), p.get("is_pano"), h,
                                            travel.get(p["id"], h)):
                lab = M.segment(img)
                pts, valid, K = M.points(img, fov_x=CROP["fov"] if vname in ("left", "right") else None)
                d, cars = car_ratios(img, lab, pts, valid, M)
                del pts
                torch.cuda.empty_cache()
                if d is None:
                    continue
                cam_hs.append(d)
                ratios += [d / c for c in cars if c > 0.3]
        ratios = np.array(ratios)
        # keep plausible cars: implied car height must be 0.9-2.6 m given the median ratio
        if len(ratios):
            med = np.median(ratios)
            ratios = ratios[(ratios > med * 0.6) & (ratios < med * 1.6)]
        rig = a.car_height * float(np.median(ratios)) if len(ratios) >= a.min_cars else None
        rows.append({"sequence": seq, "n_cars": int(len(ratios)), "rig_height_m": round(rig, 3) if rig else None,
                     "est_height_median": round(float(np.median(cam_hs)), 3) if cam_hs else None,
                     "ratio_spread": round(float(np.median(np.abs(ratios / np.median(ratios) - 1))), 3) if len(ratios) else None})
        pd.DataFrame(rows).to_csv(part, index=False)
        sys.stdout.write(f"\r{si + 1}/{len(by_seq)} sequences")
        sys.stdout.flush()
    print()
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out, "sequence_scale.csv"), index=False)
    os.remove(part)
    ok = df.dropna(subset=["rig_height_m"])
    print(f"calibrated {len(ok)} of {len(df)} sequences from parked cars; rig height median {ok.rig_height_m.median():.2f} m "
          f"(IQR {ok.rig_height_m.quantile(.25):.2f}-{ok.rig_height_m.quantile(.75):.2f}); depth-model estimate median "
          f"{ok.est_height_median.median():.2f} m; car-ratio spread {ok.ratio_spread.median():.2f}")


if __name__ == "__main__":
    main()
