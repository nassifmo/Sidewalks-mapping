# Sidewalk width fixes, tested one at a time (DC Adams Morgan benchmark)

Date: 2026-11-10. Method: per-photo straight-edge widths (`view_edges.py`), scored against the DC ground-truth width points at the same station.

## How the tests were scored

Each fix was switched on **alone**. Everything else was kept at the baseline.

A fix can also change *which* stations get a width at all. Some gain stations, others lose them. So the main comparison is **paired**: baseline vs fix on exactly the stations both measured. The unpaired totals are shown too, because coverage matters.

Re-running the AI pass with no change moves on-foot MAE by about 0.01 m. Smaller differences than that are noise.

- **MAE:** mean absolute width error (m).
- **≤0.5 m:** share of stations within 0.5 m of the truth.

## Results

### Car 360 panoramas (baseline 575 stations, MAE 1.45 m, median 1.13 m, 26 % ≤0.5 m)

| Fix (alone) | Paired stations | Baseline MAE | Fix MAE | Change | Coverage effect | Verdict |
|---|---|---|---|---|---|---|
| A. Camera height from parked cars | 459 | 1.36 | **1.32** | **−0.04** (bias +0.42 → +0.29) | +10 stations | **Keep** |
| B. Tilt from the sidewalk's own plane | 444 | 1.45 | 1.47 | +0.02 | +28 stations | Drop for panoramas |
| C. Curb/back edge as a line fitted in the image | 508 | 1.50 | 1.57 | +0.07 (bias grows) | +235, but worse ones | **Drop** |
| D. Skip stations within 8 m of an intersection | 539 | 1.43 | 1.43 | 0 on kept stations | −36 stations (the worse corners) | Keep (small) |
| E. Near side of the street only (≤8 m) | 85 | 1.41 | 1.39 | −0.02 (bias +0.63 → −0.03) | **−73 %** stations | Drop |

### On-foot photos (baseline 98 stations, MAE 0.48 m, median 0.27 m, 66 % ≤0.5 m)

| Fix (alone) | Paired stations | Baseline MAE | Fix MAE | Change | Coverage effect | Verdict |
|---|---|---|---|---|---|---|
| A. Camera height from parked cars | 74 | 0.36 | 0.45 | **+0.09 worse** | −9 stations | Drop for on-foot (only 6 of 36 sequences had enough cars) |
| B. Tilt from the sidewalk's own plane | 97 | 0.48 | **0.45** | **−0.03**, ≤0.5 m 67 → 72 % | **+20 stations** (118 total, MAE 0.47) | **Keep** |
| C. Curb/back edge as a line fitted in the image | 90 | 0.48 | 0.51 | +0.04 | +4 | **Drop** |
| D. Skip stations within 8 m of an intersection | 92 | 0.48 | 0.48 | 0 | −6 stations | Neutral, keep for consistency |
| E. Near side of the street only (≤8 m) | 37 | 0.34 | 0.37 | +0.03 | −53 % stations | Drop |

### Classical ML experiments (from the earlier hour)

| Idea | Result | Verdict |
|---|---|---|
| Learned quality weighting of photos | No gain: most stations have only one usable photo | Drop |
| Smoothing along the block face (6–10 m) | Negligible | Drop |
| Learned error correction (gradient boosting, spatial cross-validation) | Panoramas 1.45 → 1.32 m and on-foot worse when the model cannot see the width itself. The bigger apparent gains come from pulling widths toward DC's typical width, which would not carry over to Beirut. | Only with Beirut tape measurements |
| Confidence ranking / abstention | Top 25 % most-confident panorama stations: MAE 0.74 m | Keep as a "confidence" field, not a width change |
| 90 % error intervals (conformal) | Coverage is honest, but intervals are about ±2.3 m wide | Optional |

## What we learned

1. **Scale is still the problem for car panoramas.**
   - Fix A is the only one that moved panorama accuracy, and only by 0.04 m paired. That is because only 47 of 103 sequences could be calibrated.
   - The calibrated rig height is 2.22 m, versus the depth model's 2.79 m. The depth model clearly over-estimates scale. Calibrated sequences improve; the rest are untouched.
2. **The tilt fix (B) helps on-foot photos and slightly hurts panoramas.**
   - On-foot photos are taken from the sidewalk itself, so its plane is close and well seen.
   - From a car the sidewalk is a thin, far strip. Its fitted plane is noisier than the road plane.
3. **Fitting edges as straight lines in the image (C) made things worse.** The segmentation boundary pixels it fits are already the problem (shadows, parked-car bottoms, wall bases). A straight line through bad pixels is still bad. The bin-based edges stay.
4. **Corners (D) are only slightly worse than mid-block.** Skipping them is a small clean-up, not a fix.
5. **Near side only (E) removes the panorama bias but throws away most stations.** It is not worth it.

## Proposed merge (for your confirmation)

| Photo source | Fixes switched on | Expected (estimate from the paired tests, not yet measured) |
|---|---|---|
| Car 360 panoramas | **A** (camera height from cars) + **D** (skip corners) | MAE ≈ 1.30–1.33 m, ~550 stations |
| On-foot photos | **B** (sidewalk plane) + **D** (skip corners); **no A** | MAE ≈ 0.45–0.47 m, ~110–118 stations, ≈72 % within 0.5 m |
| Both | Confidence field from the ML ranking (no width change) | Lets QGIS show "most reliable" stations |

Not merged: C, E, ML width correction (until there are Beirut measurements), smoothing, quality weighting.

## Implementation (what I will change if you confirm)

1. **`measure.py`:** apply the sidewalk-plane tilt fix only to non-panorama photos (on-foot/phone). Panoramas keep the road plane. This replaces the global `SW_PLANE` switch with a per-photo rule; `--no-sw-plane` stays as an override.
2. **`view_edges.py`:**
   - Use the parked-car camera heights (`sequence_scale.csv`) only for panorama sequences, ignored for on-foot sequences.
   - Default `--corner-m 8`.
   - Remove nothing else. `--use-lines` stays as an option but off by default.
3. **`calib_scale.py`:** no change. It already runs per sequence; on-foot results will simply be ignored.
4. **`ml_widths.py`:** add an option to write a per-station `confidence` (predicted error from the model *without* width features) into the width layer. Scoring will report the top-confidence share.
5. **Test the merge on DC:**
   - Panoramas: the base folder, calibration on, corners 8 m.
   - On-foot: the tilt AI pass already exists, so this is a CPU run of a few minutes.
   - Score it both unpaired and paired against the baseline.
6. **If DC confirms it, apply the merge to Beirut.** This needs the calibration pass plus an on-foot AI re-run on the GPU (≈1–2 h). Then refresh the QGIS layers and push to GitHub.

## Next levers for car panoramas (beyond these five)

The five image fixes together are worth about 0.1–0.15 m on panoramas. Their error stays at about 1.3 m because of scale and edge noise. Larger levers from the roadmap:
- Calibrate more sequences: relax the car filter, or add other rulers such as standard door heights or lane widths.
- Multi-photo structure from motion, to fix scale per sequence from the known GPS travel distance.
- Rely on on-foot imagery where it exists. Beirut has some on-foot coverage.

Files: results table `benchmark_dc/ablation/ablation.tsv`. Scripts: `benchmark_dc/ablation/ve_eval.sh` (run + score one setting), `benchmark_dc/ablation/paired.py` (paired comparison).
