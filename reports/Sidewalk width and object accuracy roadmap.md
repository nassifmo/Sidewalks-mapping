# Fix Scale and Occlusion, Then Certify Beirut

The Washington DC benchmark shows that our pipeline now puts sidewalks in the right place but measures them wrongly, and the cause is structural. Location is nearly solved: car panoramas place the sidewalk with a **median lateral offset of 0.14 m** after the GPS and heading fixes. Width is not. On-foot photos are almost unbiased (−0.03 m) but noisy, with an **MAE of 0.82 m**. Car panoramas underestimate width by **0.84 m on average**, because only **576 of 4,720 transects (12%)** see both sidewalk edges. Objects fail for reasons of taxonomy and geometry rather than detection quality. Street-light heads never touch the ground, so they are placed nowhere, and single-view placement has errors of several metres. Published work identifies the same three remedies: take metric scale from a known geometric quantity rather than from a depth network, measure only near the camera, and refuse to measure when an edge is hidden. Those three alone took one DC study from 1.57 m to **0.25 m MAE** ([UrbanVGGT](https://arxiv.org/html/2603.22531v1)). A fully automatic pipeline on archive Mapillary imagery can plausibly reach ≤0.5 m, but only on the fraction of sidewalk it chooses to measure, likely 30–50%, and it cannot prove its Beirut accuracy without some field data. The reliable route to ≤0.3–0.5 m everywhere is human-in-the-loop. It combines walking 360° capture at a measured camera height, about 150 laser-measured validation stations, and review of the riskiest 20% of segments. For the 160 block-face km pilot area this costs roughly **135–300 person-hours and under US$1,000 in equipment (about US$3,200–4,600 with an RTK receiver)** [C from A]. The next two weeks should go to diagnostic experiments on data we already have, not to new models.

*How to read the evidence.* **[T]** marks the team's own measured results, which are primary data. Linked figures are published evidence. **[I]** marks inference by this report. **[C]** marks arithmetic done here from cited or team inputs. **[A]** marks a planning assumption to be replaced by measurement. Every expected-accuracy figure for a step we have not yet run is **[I]**: it is a forecast to be checked on the benchmark, not a result.

## Our DC numbers point to occlusion and scale, not location or segmentation

### Location is already good enough; width error is a relative-geometry problem

The geolocation fixes work. After per-view heading corrections (needed on 2,114 views, median 3.4°) and per-sequence GPS shifts (21 of 93 sequences, median 3.9 m), car panoramas place detected sidewalk with a **median offset of 0.14 m, 87% within 3 m** [T]. On-foot photos reach 0.6 m [T]. Width is a *relative* quantity: the distance between two edges seen from the same camera. Absolute GPS error therefore largely cancels out of it [I]. GPS still matters for assigning a measurement to the right block face, but it is no longer what keeps width from the target. That moves the diagnosis to four things: metric scale inside each view, edges hidden by occluders, angular error growing with range, and what "width" means in the reference data.

### On-foot error is noise with no bias, which points at scale and pitch

On-foot photos give a fused same-station **MAE of 0.82 m, bias −0.03 m, median absolute error 0.70 m, and only 40% within 0.5 m** (n = 129) [T]. A near-zero mean with a large spread means the errors are random, not systematic. The pipeline sets scale per sequence from the median camera height that MoGe-2 estimates. That evens out scale between views of the same sequence, but each sequence still inherits whatever absolute error MoGe-2 makes for that sequence. Across many sequences those errors average to near zero bias, but they stay in the spread [I]. Phones are also held at 1.0–1.6 m and tilted. In the Seoul test of a very similar Mask2Former-Vistas recipe, **±2° of pitch changed width by ±10–16%**, a 10% camera-height error gave about a 10% width error, and assuming a level phone produced a −0.66 m bias ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)). The strongest external evidence is UrbanVGGT's ablation on DC Street View images: without camera-height calibration, MAE was **1.571 m and 0% of widths fell within 0.5 m**. With calibration it was 0.252 m. Most "native metric" depth models did poorly without calibration (DepthPro 0.77 m, Metric3DV2 1.36 m, DepthAnythingV2 1.71 m). UniDepthV2 was the exception at 0.289 m, and **MoGe-2 was never tested** ([UrbanVGGT](https://arxiv.org/html/2603.22531v1)). Our on-foot numbers sit where the Seoul single-view arm sat, which had a clear-width MAE of 0.77 m ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)). Our hypothesis is that per-sequence scale and pitch are the dominant on-foot error terms [I]. A direct test is to check whether errors cluster by sequence (high intra-sequence correlation). If they do, scale is the culprit.

The on-foot run also detects **only 31% of sidewalks narrower than 1.2 m** [T]. That is the most damaging failure for accessibility, because those are the sidewalks that matter most. It also biases every summary statistic towards the wider sidewalks the pipeline happens to see.

### Car panoramas lose half their accuracy to occlusion, and fusion makes it worse

Panoramas give a same-station **MAE of 1.58 m with a bias of −0.84 m, median absolute error 1.21 m, and 22% within 0.5 m** (n = 2,995) [T]. Three facts together identify occlusion as the main cause.

First, the error is one-sided. A sidewalk partly hidden by parked cars can only look narrower than it is, and the −0.84 m bias is more than half of the MAE.

Second, only **12% of transects are "complete"**, meaning both edges were observed [T]. The other 88% may be cut short by an occluder, and the longest contiguous run of sidewalk pixels then measures a fragment.

Third, error grows with range, but there is a floor. Per-view MAE is **1.15 m at 2–5 m, 1.26 m at 5–8 m and 1.87 m at 8–12 m** [T]. The rise beyond 8 m matches published geometry: at 2.5 m camera height, 1° of angular error moves the ground point about 0.3 m at 6 m range but about 1.6 m at 15 m ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)). The 1.15 m floor at 2–5 m, however, cannot be a range effect. It is occlusion plus scale plus edge definition [I].

Correcting the bias alone would not be enough. Under a normal approximation, an MAE of 1.58 m with a −0.84 m bias implies an error standard deviation of about 1.8 m [C]. The observed median of 1.21 m indicates heavy tails rather than a uniformly wide spread.

One comparison deserves immediate attention. The fused station width (MAE 1.58 m) is *worse* than single views at 2–5 m (1.15 m). Pixel-vote fusion at 0.10 m appears to import far-range votes and residual misregistration instead of averaging them out [I]. A heading error left after correction shifts a point 8 m ahead by about 0.47 m at 3.4° [C], which smears edges in the bird's-eye grid. Part of the gap may also be selection, because views with both edges at 2–5 m are easier cases. This should be measured, not assumed.

### Definition and edge segmentation set a floor of about 0.1–0.3 m

DC planimetric polygons most likely record *total paved width*. Our "longest contiguous sidewalk run" lies somewhere between total and clear width. The Mapillary Vistas sidewalk class can also include frontage paving that a surveyor excludes ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)). US accessibility rules measure clear width **"exclusive of the width of any curb"** ([Federal Register 2023-16149](https://public-inspection.federalregister.gov/2023-16149.pdf)). A curb top of 0.15–0.20 m counted as sidewalk is therefore a systematic bias at the scale of our target [I]. Projecting onto the road plane rather than the sidewalk plane overstates width by about 6% at a 15 cm curb ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)). We raise the plane by an assumed 0.12 m, so a wrong assumed curb height contributes a smaller version of the same error [I]. Skeleton-derived reference widths also misbehave at corners, driveways and tree boxes. Each of these is small, but at a 0.3 m target the small terms add up.

### Object failures come from taxonomy and single-view geometry

On panoramas, utility poles score **43% precision and 26% recall**, street lights **0.1% recall**, sign posts **0%**, and cabinets **5% precision** [T]. Earlier on-foot runs scored poles at about 25% precision and 10% recall [T].

The street-light failure has a mechanical explanation. In the Vistas taxonomy the street-light class is the luminaire head, and the post is a separate support-pole class. A head component has no ground contact, so ground-plane projection sends it nowhere [I, consistent with Mapillary's separate `object--street-light`, `object--support--pole` and `object--support--utility-pole` classes ([Mapillary points](https://www.mapillary.com/developer/api-documentation/points))]. The same mechanism probably affects pole precision too. If light posts, sign posts and signal posts are detected as "poles" and then matched only against the utility-pole inventory, every one of them counts as a false positive [I]. Sign faces, like lamp heads, float above the ground.

Recall suffers because thin poles fragment under occluders and their bases are hidden behind parked cars [I].

Localization from one view is fundamentally weak. Depth-only placement of telegraph poles had a mean error of **3.2 m (95% interval 6.8 m), against 0.98 m with multi-view triangulation** ([Krylov et al. 2018](https://ar5iv.arxiv.org/html/1708.08417)). Monocular metric-depth models placed traffic signs **4.4–7.3 m** from their true position, and Mapillary camera positions alone deviated by a mean of **5.5 m** ([arXiv 2509.14839](https://arxiv.org/html/2509.14839v3)). A fixed 1.5 m DBSCAN radius cannot reconcile errors that large. It leaves duplicates, which lowers precision, and merges neighbours, which lowers recall [I].

Part of the low cabinet precision may also be reference error rather than our error. In Dublin, an image-based bin detector found **43 genuine bins missing from the city's records** ([Ahmad & Krylov 2024](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000641.pdf)). A manual check of 50 "false positives" per class will tell us how much.

### The Beirut pilot inherits every DC weakness and adds its own

Beirut produced **10,902 m² of sidewalk, 4,553 transects (592 complete), a median width of 1.25 m, 45% of widths under 1.2 m, and 8,236 objects, of which 69% have unknown position within the sidewalk** [T]. Three points follow.

First, the 45% figure is almost certainly too high. The MIT–AUB Community Streets survey estimated that about **20% of Beirut sidewalks are narrower than 1.2 m** ([Community Streets report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)). That is consistent with the occlusion bias measured in DC, although the two studies cover different areas and use different definitions [I].

Second, the 69% unknown share is a design artefact. An object gets a within-sidewalk position only if a width transect exists nearby. Object placement therefore inherits every width failure, including occlusion [I].

Third, coverage is the hidden third KPI. The 4,553 transects at 2 m spacing span about **9.1 km, of which about 1.2 km is complete** [C]. The pilot extent holds about 150–170 km of potential block-face sidewalk (computed earlier from the pilot's OSM streets) [C]. Some of that gap is imagery coverage and some is occlusion. Both should be reported alongside accuracy.

Beirut is also harder than DC on exactly the axes that hurt us. On one Beirut street, about **25 cars were parked on a 315 m sidewalk, one every 12.6 m** ([L'Orient Today](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html)). Segmentation models trained on Europe lose accuracy elsewhere mainly through *classification* errors. Motorcycle IoU, for example, fell from 0.46 in Europe to 0.24 in Africa ([arXiv 2412.11061](https://arxiv.org/html/2412.11061v1)). And our Beirut imagery dates from 2019–2020, partly before the 2020 port blast and the rebuilding that followed.

| Error source | What our numbers show [T] | External evidence | Likely size on a 2–3 m sidewalk | Decisive test on DC data |
|---|---|---|---|---|
| Metric scale (MoGe-2 absolute, per-sequence median) | On-foot bias ≈0 but MAE 0.82 m | No calibration: 1.571 m vs 0.252 m ([UrbanVGGT](https://arxiv.org/html/2603.22531v1)) | 0.2–0.6 m [I] | Oracle scale per sequence fitted to DC curb lines; error clustering by sequence |
| Occlusion by parked cars | Bias −0.84 m; 12% of transects complete | Best systems reject occluded frames ([UrbanVGGT](https://arxiv.org/html/2603.22531v1)) | 0.5–1.0 m, one-sided [I] | MAE on complete vs incomplete transects |
| Range and pitch | 1.15 → 1.26 → 1.87 m by range | 1° ≈ 0.3 m at 6 m, 1.6 m at 15 m ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)) | 0.1–0.7 m beyond 8 m [I] | Restrict to 2–8 m |
| Fusion misregistration | Fused 1.58 m worse than near single view 1.15 m | — | 0.1–0.4 m [I] | Fuse per-view widths instead of pixels |
| Edge definition, curb, plane | — | Curb excluded by rule; road plane +6% | 0.1–0.3 m [I] | Per-edge error against DC curb lines and the polygon's inner boundary |
| Narrow sidewalks missed | 31% detected under 1.2 m | Seoul arm caught 9/9 narrow cases, precision 0.41 ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)) | Missing data, not error | Recall by width class |
| Object taxonomy | Lights 0.1%, sign posts 0% | Vistas separates luminaire from support | Dominant for lights and signs [I] | Class-agnostic pole metric against the union of DC inventories |
| Single-view object placement | Poles P 43% / R 26% | 3.2 m depth-only vs 0.98 m triangulated ([Krylov](https://ar5iv.arxiv.org/html/1708.08417)) | 1–5 m absolute [I] | Position error distribution of matched poles |
| Transect-linked placement | 69% unknown in Beirut | — | Coverage, not error | Share placed after switching to block-face polygons |

## A fully automatic pipeline reaches the target only where it is allowed to abstain

The published sub-0.3 m results all share three ingredients. Scale comes from a known geometric quantity. Measurement is restricted to the near field. And any frame where both edges are not clearly visible is rejected. These numbers are reported on the accepted images only. UrbanVGGT's unvalidated prototype measured only **38.2%, 13.2% and 7.6% of OSM segments** in New York, São Paulo and Nairobi ([UrbanVGGT](https://arxiv.org/html/2603.22531v1)). Older provider-depth work on DC panoramas reports a mean width error of 0.24 m for 1–2 m sidewalks ([Ning et al. 2022](https://pure.psu.edu/en/publications/converting-street-view-images-to-land-cover-maps-for-metric-mappi/)). That work used Google's depth maps, which we cannot use.

The honest framing for a zero-human pipeline is therefore *selective prediction*. It meets the accuracy target on the stations it accepts, and it reports coverage as a separate, equally visible number. Processing cost is not a constraint: at 0.8–1 s per panorama [T], the whole pilot runs in about an hour. Heavier models costing 5–10× more remain affordable [I].

### Width: seven steps, each with a forecast to be tested

| Step | Change | Evidence | Forecast for DC car panoramas: accepted MAE / share of length measured [I] |
|---|---|---|---|
| A0 | Current pipeline | — | 1.58 m [T] / all transects |
| A1 | Abstain: keep complete transects with both edges 2–8 m from the camera, no sidewalk touching the image border, occluder share below a threshold | Sub-0.3 m studies reject aggressively; worst Seoul errors (+9.6 m) came from sidewalk touching the frame edge ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)) | 0.8–1.0 m / 10–15% |
| A2 | Geometric scale replaces MoGe-2's absolute scale: similarity-fit each sequence's SfM trajectory to GNSS over ≥200 m; enforce one constant rig height per car sequence; test VGGT-1B-Commercial or MapAnything point maps under height calibration | Height calibration 1.571 → 0.252 m; VGGT 0.252, MapAnything 0.334, π³ 0.324 m ([UrbanVGGT](https://arxiv.org/html/2603.22531v1)) | 0.5–0.7 m / 10–15% |
| A3 | Measure, then fuse: compute width per view in the camera frame, where heading errors do not matter, then take a range-weighted median per station | Near single views already beat the fused result [T] | 0.4–0.6 m / 15–25% |
| A4 | Two-edge geometry: fit one curb line per block face from visible curb pixels and the road–sidewalk height step using robust 1-D regression over the gaps between cars; take the inner edge from GPS-shifted OSM building outlines or the building-base line seen in images; width = curb line to frontage | No paper tests this; Beirut has cars every 12.6 m, so gaps exist ([L'Orient Today](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html)) | 0.4–0.5 m / 35–55% |
| A5 | Occlusion-aware, multi-date bird's-eye grid: cells hidden behind a car become "unknown", not "not sidewalk", so other dates fill them | Parked cars move between passes; curbs do not ([Freiburg amodal benchmarks](https://amodal-panoptic.cs.uni-freiburg.de/)) | Coverage +5–15 points |
| A6 | Definitions: fit the sidewalk plane, measure the curb step instead of assuming 0.12 m, exclude the curb top, report total and clear width separately | Road plane +6%; curb excluded by rule | −0.05 to −0.1 m |
| A7 | Confidence score from edge entropy, view agreement, plane residual, occluder share and range, calibrated on DC with a risk–coverage curve; publish only accepted stations | Uncertainty must rank errors before it is trusted ([Cai et al. 2025](https://arxiv.org/pdf/2507.17367) for the active-selection analogue) | Sets the operating point |

The likely end state on archive DC panoramas is an accepted-station **MAE of about 0.35–0.5 m over 30–50% of sidewalk length**. On-foot imagery should reach about 0.3–0.4 m [I]. A2 and A4 carry most of the expected gain.

A2 is the single most important change. Its preferred form uses geometry we already have: SfM camera motion fitted to GNSS over long baselines. GNSS errors of a few metres shrink to a few percent of scale over a few hundred metres [I]. Mapillary also exposes `computed_geometry` (SfM-refined positions), `atomic_scale` and downloadable `sfm_cluster` point clouds through its API ([Mapillary API v4](https://blog.mapillary.com/update/2021/06/23/getting-started-with-the-new-mapillary-api-v4.html)). No published study assesses their metric accuracy, so they must be validated on DC before use.

A4 matters most for Beirut. There, a car parked on the sidewalk sits *on* sidewalk area. Measuring between two edges treats its footprint as sidewalk for total width and as an obstruction for clear width, whereas counting visible pixels simply loses that area [I]. Learned amodal layout completion is a later option. It can predict the ground behind cars without labels for hidden pixels ([Schulter et al. 2018](https://openaccess.thecvf.com/content_ECCV_2018/papers/Samuel_Schulter_Learning_to_Look_ECCV_2018_paper.pdf)), but it has evidence only on driving datasets and risks inventing regular widths on irregular Beirut streets [I].

### Objects: instances, rays and curb-relative offsets

| Step | Change | Evidence | Forecast on DC [I] |
|---|---|---|---|
| B1 | Fix taxonomy: score a class-agnostic "vertical pole" against the union of DC pole, light, sign and signal inventories; attach each luminaire or sign face to the pole instance beneath it | Vistas separates heads from supports | Street-light recall rises close to pole recall |
| B2 | Replace semantic connected components with an instance detector: SAM 3 or Grounding DINO zero-shot proposals, then fine-tune RF-DETR (N–L, Apache-2.0) on weak labels made by projecting DC inventories into images | Auto-labels from government metadata reached 94.0% precision and 92.5% recall ([RampNet](https://arxiv.org/html/2508.09415v1)); LoRA-tuned Grounding DINO reached 74.5–80.2% mean precision and 80.6–84.2% mean recall over 11 furniture classes ([SVII-3D](https://arxiv.org/html/2601.10535)) | Poles and lights at 70–85% P/R |
| B3 | Multi-view triangulation of the pole axis from 3 or more views, associating views by geometry rather than appearance, with depth only as a soft prior within 20 m | 0.98 m triangulated vs 3.2 m depth-only; identical poles defeat appearance matching in 35% of scenes ([Krylov](https://ar5iv.arxiv.org/html/1708.08417)) | About 1 m absolute |
| B4 | Compute curb offset and remaining clear width in the local reconstruction, where curb and object share one frame and GPS error cancels; cross-check by the segmentation class (sidewalk, curb or road) under the object's ground-contact pixels | Inference from width being relative | 0.3–0.5 m curb-offset error |
| B5 | Place objects against a continuous block-face polygon with labelled curb and frontage edges, not the nearest transect | — | Unknown position falls from 69% to under 15% |
| B6 | Use Mapillary `map_features` (street light, pole, utility pole, junction box, trash can, bench, signs) as extra candidates; agreement within 2 m means high confidence | Free and triangulated, but no published accuracy, and no classes for trees, bollards, vehicles, generators or stalls ([Mapillary points](https://www.mapillary.com/developer/api-documentation/points)) | Recall gain on standard classes |
| B7 | Clear width = the larger of the curb-side and building-side gaps; apply height bands, where wall-mounted objects between 685 and 2,030 mm count only if they protrude more than 100 mm | [US Access Board](https://www.access-board.gov/ada/guides/chapter-3-protruding-objects) | Rule-consistent clear width |

The decimetre-level object results in the literature, **0.118–0.137 m** ([SVII-3D](https://arxiv.org/html/2601.10535)), rely on survey-grade mobile-mapping poses. We should not expect them from crowdsourced imagery.

The key design choice is B4. Our target is the object's position *within the sidewalk*, not its absolute coordinates. Distance from the curb therefore behaves like width: it is relative, and it can be solved locally before anything is georeferenced [I].

For Beirut-specific obstructions (generators, vendor stalls, spilled goods, motorcycles on the sidewalk), a fully automatic path has only zero-shot detection. Trained obstacle classifiers from Project Sidewalk reached only **53–68% precision**, and models trained without the target city missed local forms such as terraced sidewalks ([Duan et al. 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)). Without local labels, expect those classes to stay below 70% [I].

### What stays uncertain without humans

Four uncertainties remain even if every step succeeds on DC.

First, nothing certifies the Beirut numbers. DC accuracy transfers only if Beirut segmentation, curbs and occlusion behave like DC's, and the evidence on geographic bias says they will not exactly ([arXiv 2412.11061](https://arxiv.org/html/2412.11061v1)).

Second, the accuracy and availability of Mapillary SfM for 2019–2020 Beirut sequences are unknown.

Third, the quality of OSM building frontages in Beirut is unmeasured. Shop extensions and terraces blur where a sidewalk ends.

Fourth, licences constrain the stack:

- MoGe's weight licence is unstated ([MoGe](https://github.com/microsoft/MoGe)).
- The licence of the Vistas training data is described inconsistently ([Neuhold et al.](https://openaccess.thecvf.com/content_ICCV_2017/papers/Neuhold_The_Mapillary_Vistas_ICCV_2017_paper.pdf)).
- The original VGGT-1B weights are non-commercial; only the gated VGGT-1B-Commercial checkpoint permits commercial use ([VGGT](https://github.com/facebookresearch/vggt)).
- MapAnything is Apache 2.0 ([MapAnything](https://arxiv.org/pdf/2509.13414v3)).
- Ultralytics YOLO is AGPL-3.0, including custom-trained weights ([Ultralytics](https://ultralytics.com/license)).

The practical conclusion is that "surely" cannot be delivered at zero human effort. The minimum human input that makes any claim checkable is a field validation sample of one to two days.

## Roughly 135–300 person-hours turn the pilot into a certified map

The human-in-the-loop paths differ in what they buy. Light QA *measures* accuracy without changing it. Targeted review *repairs* the worst segments. Purpose-built capture *removes* the main error sources at their origin. Field ground truth makes everything *provable*. Local labels *transfer* the detector to Beirut.

Hours below are for the pilot extent of about 160 block-face km (about 80 km of street centreline) and about 8,236 candidate objects. Cash assumes a student-assistant rate of **US$5–10/h [A]**, which should be replaced with the actual rate.

| Path | What humans do | What it fixes | Expected effect | Hours (pilot) | Cash |
|---|---|---|---|---|---|
| H1 Light QA | Audit 77 random block faces per lot of about 1,000 faces in imagery, at about 3 min each; accept or reject the lot | Nothing; it certifies | Defensible pass/fail per lot | ≈8 h for 2 lots [C from A] | ≈US$40–80 |
| H2 Targeted review | Review the riskiest 20% of stations by clicking the curb and frontage points in a near-range image (about 30 s per station); accept, reject or nudge object candidates (3–10 s each); one discovery pass over 10% of length | Occlusion and edge errors where the model is least sure; object false positives | Reviewed stations reach human-click accuracy; precision of verified objects over 90% [I] | ≈13 h widths + 7–23 h objects + ≈7 h discovery = **27–43 h** [C from A] | ≈US$140–430 |
| H3 Purpose capture at known height | Walk both sides with a 360° camera on a rigid pole at a tape-measured height; the camera's IMU gives pitch | Scale, pitch and most occlusion, by design | Width MAE about 0.25–0.4 m [I] | **47–80 h** at 35–60 min per street-km [I] | Camera about US$450–550; pole ≈US$100 [A]; optional RTK receiver US$2,519–3,647 |
| H4 Field ground truth | Laser-measure about 150 stations and the curb offsets of about 100 objects; 10% repeat measurements | Makes accuracy provable | Bootstrap confidence intervals on MAE; see the validation plan | **≈32–48 h** (2–3 field days for a pair) | Laser meter ≈US$100–300 [A] |
| H5 Local labels | Correct SAM-proposed masks on 200–500 Beirut images, chosen by active learning | Beirut classes and sidewalk-versus-parking confusion | Fixed classes towards 80% P/R; local obstacle classes become measurable | **20–120 h** | — |

Adding H1 through H5 gives roughly **134–299 person-hours** [C]. That is about US$0.7–3k of labour plus US$0.65–0.95k of equipment, or US$3.2–4.6k of equipment with RTK [C from A].

### Targeted review should correct edges in images, not on overhead tiles

The best measured throughput for virtual sidewalk auditing is Project Sidewalk's **1.74 street-miles per hour** per labeller, about 21 min/km ([Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)). That study also shows that humans are weak at *discovering* obstacles unaided: single-labeller obstacle recall was **39.9% at 47.5% precision**. Taking the union of five labellers raised overall recall from 67.8% to 91.7%, but cost precision ([Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)). The productive human role is therefore *verifying* machine candidates, as in the RapiD pattern, plus a thin discovery pass.

Edge correction should happen in the near-range street image, where one pixel is about a centimetre, rather than by tracing on Esri tiles. Esri tracing is licence-permitted but has its own unquantified 0.3–1 m edge uncertainty under trees and cars [I].

Human review of automatic sidewalk networks has a measured payoff. Intersection-scale tasks of a few minutes each raised routability similarity from **0.31–0.47 to 0.84–0.88** ([Prophet/Skeptic](https://arxiv.org/html/2410.19762v1)). The analogous Beirut repair is curb lines at corners, driveways and occluded stretches.

Reviewing only the top 10–20% by risk is efficient if the risk score ranks errors. In segmentation, region-based active learning reaches about 95% of full supervision with **5–9% of pixels labelled** ([Cai et al. 2025](https://arxiv.org/pdf/2507.17367)). No study has quantified the review budget needed for a given width error, so the risk–coverage curve must first be checked on DC [I].

### Purpose capture is the only path that removes occlusion at its source

A camera walked *on* the sidewalk on a pole at a measured height fixes three things by design. The height measured to ±2 cm on about 2.5 m removes the 10%-per-10% scale term. The IMU gravity vector or the vanishing-point horizon controls pitch. Both edges sit within about 1–4 m of the camera, where 1° of error costs a few centimetres [I]. The camera also sees over parked cars instead of from behind them.

Mapillary recommends the **GoPro MAX 2** for its built-in GPS and native upload support, at about US$449–499. The Insta360 X5 is better in low light at about US$499–549 ([Mapillary cameras](https://www.mapillary.com/cameras); [DroneXL](https://dronexl.co/2025/10/10/best-360-camera-gopro-max-2-dji-osmo-360-insta360-x5/)).

Known height alone is not sufficient. The Seoul phone set, captured at a fixed 1.0 m, still produced a 0.77 m MAE through a single-view pipeline in which pitch was the dominant error ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)). The forecast of 0.25–0.4 m therefore assumes IMU-controlled pitch and multi-view processing [I]. No peer-reviewed study has validated sidewalk width from walking 360° capture, so the pilot itself is the experiment.

Absolute object coordinates within 0.5 m would additionally need RTK or post-processed positioning. LEB-CORS, run by the Army's Directorate of Geographic Affairs, advertises **13 stations and ±3 cm network RTK**, but civilian access terms are unpublished ([LEB-CORS](https://lebcors.army.gov.lb)). An Emlid RS3 receiver costs US$2,519–3,647 ([Advexure](https://advexure.com/products/emlid-reach-rs3)). Our within-sidewalk targets do not need absolute accuracy, so RTK is optional for this research question [I].

### Higher-assurance and rejected options

A DIY backpack LiDAR rig is a fallback if imagery stalls. A Livox Mid-360 running FAST-LIO2 had **0.060 m trajectory RMSE** on a public benchmark ([Open Robotics Discourse](https://discourse.openrobotics.org/t/slam-benchmark-on-livox-mid-360-public-dataset-our-own-uav-flight-data-kiss-icp-dlio-fast-lio2-glim/57912)), far inside the width target. iPhone LiDAR is accurate to **1–2 cm for features under about 4 m** but drifts beyond that ([Tandfonline 2024](https://www.tandfonline.com/doi/full/10.1080/16874048.2024.2408839)). It makes a fast ground-truth tool for single cross-sections, not a mapper.

Two options should not be used to guarantee width. The first is 30 cm satellite imagery. A Beirut archive purchase costs only about US$560–2,100 ([LandInfo](https://landinfo.com/satellite-imagery-pricing.html)), but a one-pixel error at each edge already gives σ ≈ 0.42 m [C], before counting building lean, tree canopy and cars. The second is drones: all permits have been suspended since **1 March 2026** ([LBCI](https://www.lbcgroup.tv/news/lebanon-news/908645/lebanese-army-suspends-drone-permits-nationwide-amid-regional-tensions/en)).

## About 150 measured stations decide whether Beirut numbers can be trusted

Beirut has no official sidewalk data, so its accuracy can only be proven by measuring a sample. The sample size depends on the spread of the absolute errors, σ|e|. To estimate MAE within ±0.1 m at 95% confidence takes n ≈ (1.96·σ|e|/0.1)²: **about 35 stations if σ|e| = 0.3 m, 96 if 0.5 m, and 246 if 0.8 m** [C].

Stations along the same block face are correlated. The sample should therefore be spread across faces, one or two stations each, rather than packed along a few. With 150 stations on about 100 faces and an assumed within-face correlation of 0.3, the effective sample is about 115. That pins MAE to ±0.1 m as long as σ|e| ≤ 0.55 m [C from A].

To claim a tolerance rather than an average, binomial acceptance applies. If **150 stations show at most 8 outside ±0.5 m**, we can state with 95% confidence that at least 90% of widths are within ±0.5 m. At most 2 failures supports "at least 95%". Fifty-nine consecutive passes with zero failures also supports a 95%/95% claim [C].

For absolute positions, ASPRS recommends **at least 30 checkpoints** ([LiDAR Magazine on ASPRS Ed. 2](https://lidarmag.com/?p=15999)).

| Quantity | Metric | Sample | Basis | Field effort |
|---|---|---|---|---|
| Pilot σ and within-face correlation | σ\|e\|, within-face correlation | 10 faces × 5 stations = 50 | Recompute all sample sizes from measured σ | 0.5 day for a pair |
| Total width (curb face to frontage) and clear width | MAE, bias, % within ±0.3/±0.5 m, bootstrap CI | ≈150 stations on ≈100 faces, stratified by width class (<1.2, 1.2–2.5, >2.5 m), parked-car presence, street type and image source | ±0.1 m if σ\|e\| ≤ 0.55 m; ≤8 failures → ≥90% within tolerance | 3–5 min per station → 1.5 days |
| Narrow-sidewalk flag | Sensitivity and specificity for <1.2 m | All sampled stations in the <1.2 m stratum, at least 40 | Accessibility decision | Included above |
| Object precision | Share of predictions correct | ≈100 random predictions per super-class | ±10% at 95% | Desk check in imagery |
| Object recall | Share of real objects found | Full census of ≈20 faces (≈2 km) | Hundreds of objects at one object per 10–15 m [A] | 0.5 day |
| Curb offset and remaining clear width | MAE in metres | ≈100 objects, laser-measured from the curb face | ±0.1 m if σ ≤ 0.5 m | 1–2 min each |
| Absolute position (optional) | RMSE, radial | ≥30 RTK checkpoints | ASPRS minimum | If LEB-CORS access is granted |
| Reference error | Repeat SD | 10% re-measured blind by a second pair | Must be well below 0.1 m | Included |

Each station records total width from the curb face to the building or property line, clear width past permanent objects, curb height, photographs in both directions, and parked-car presence. This separates the definitional bias from the model error (Section 1).

Three remote cross-checks cost nothing. The first is the AUB 2010 1:2,000 curb lines, which predate the blast, so field-check any conflict over 0.3 m ([AUB catalogue](https://scholarworks.aub.edu.lb/server/api/core/bitstreams/71b5ddf4-a555-4cf2-a70c-4bf0fc19da4a/content)). The second is the Community Streets distribution, about 20% of sidewalks under 1.2 m ([Community Streets report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)). The third is Mapillary map features for standard objects.

Temporary occupation needs dated observations. Beirut begins enforcing against sidewalk occupation on **16 November 2026**, one week from now ([Libnanews](https://en.libnanews.com/beirut-abboud-sets-violators-free-sidewalks-global-voices)). A walking capture of the pilot's commercial frontages before that date, repeated after it, turns the enforcement into a before-and-after measurement [I]. Obstruction counts measured after enforcement will not describe the earlier city.

## The roadmap diagnoses for two weeks, rebuilds for two months, then certifies

Order matters. The ablation ladder below answers, on data we already hold, which error term dominates. Every later investment depends on that answer. Each horizon ends in a go/no-go gate measured on the DC benchmark, and the 3–6-month gate adds Beirut field data. Thresholds are proposals anchored to published results, judged on the bootstrap 95% bound rather than the point estimate.

| Horizon | Work (priority order) | Go/no-go gate on DC | If no-go |
|---|---|---|---|
| **Next 2 weeks** (to about 23 Nov 2026) | (1) Split DC width error by complete/incomplete transect, range band, occluder share and sequence. (2) Oracle scale: fit each sequence's scale to DC curb lines and report the remaining MAE. (3) Per-edge error: our curb edge against the 1,211 DC curb lines, our inner edge against the polygon boundary. (4) Check the DC polygon definition (curb, tree boxes, total vs clear). (5) "Fuse widths, not pixels" re-run. (6) First risk–coverage curve. (7) Objects: class-agnostic pole score; luminaire-to-pole attachment; manual check of 50 false positives per class; DC Mapillary map-features baseline. (8) Beirut: block-face polygon placement. (9) Pre-enforcement walking capture of pilot frontages before 16 Nov, if feasible | At least 70% of panorama MAE is attributed to named causes. **Go to the automatic route if** complete-transect, 2–8 m, oracle-scale MAE is ≤0.5 m. Objects: class-agnostic pole precision ≥0.6 | If oracle-scale MAE stays above 0.7 m, edge definition or segmentation dominates: prioritise curb-line fitting, local fine-tuning and H3 |
| **1–2 months** (Dec 2026–Jan 2027) | Width v2: steps A2–A7 (geometric scale, near-range per-view widths, two-edge curb lines, occlusion-aware multi-date grid, confidence score); depth backbone bake-off under fixed scale (MoGe-2, VGGT-1B-Commercial, MapAnything, DA3-Base); known-height path tested on the Seoul CC0 set. Objects v2: steps B2–B6 with DC inventory weak labels. Beirut: pilot field day (σ), 10-face purpose-capture pilot, LEB-CORS enquiry, ethics/IRB letter | **Panoramas, fully automatic:** accepted MAE ≤0.50 m, \|bias\| ≤0.15 m, ≥65% within 0.5 m, coverage ≥35% of DC sidewalk length in the imaged area, risk score rank-correlated with \|error\| at ρ ≥ 0.4. **On-foot:** MAE ≤0.40 m; detection under 1.2 m ≥70%. **Seoul:** MAE ≤0.40 m. **Objects:** class-agnostic poles P ≥0.75, R ≥0.60 at 2 m; lights R ≥0.50; median position error ≤1.0 m; curb-offset MAE ≤0.40 m against DC curb lines | Archive results become screening only (width classes, not metres); shift effort to H2 + H3 |
| **3–6 months** (Feb–May 2027) | Purpose capture of the full pilot extent at known height (≈47–80 h); 200–500 SAM-assisted Beirut labels by active learning; image-based two-click review tool; full Beirut validation sample (H4); targeted review of the riskiest 20%; v1 release with per-station confidence and coverage | **Beirut field sample:** total-width MAE ≤0.30 m (upper bound ≤0.35 m), ≤8 of 150 stations outside ±0.5 m, sensitivity ≥0.90 for <1.2 m; fixed-object P and R ≥0.80; curb-offset MAE ≤0.30 m; clear-width MAE ≤0.40 m; unknown position ≤10%. **DC regression:** no metric worse than the 1–2-month gate | Publish only stations that passed, label the rest "measure in field", and extend H2 review to 40% |

The two-week work is cheap and decisive. Items 1–4 need no new code beyond joins against data already in the benchmark. The oracle-scale experiment is the most informative single run we can do. If perfect scale leaves the error large, no depth model will fix it, and edge definition and occlusion become the whole agenda [I].

The 1–2-month gate is designed so that passing it justifies the fully automatic claim for archive imagery *at the stated coverage*. Failing it is still useful: it shows that archive Mapillary can screen streets but not measure them, and redirects effort to capture.

The 3–6-month gate is the first point at which a statement such as "Beirut widths are within 0.3 m" can be supported, because it rests on Beirut measurements rather than on DC transfer.

## Conclusion

The research question has changed shape. We started by asking which model measures sidewalks best, but the benchmark shows that the binding constraints are geometric and observational: where the metric scale comes from, and whether both edges are visible at all. Width and position-within-sidewalk are both *relative* measurements. Once each is solved in a local frame, GPS shrinks to a book-keeping problem. That is good news, because local geometry is exactly what a calibrated camera at known height, walked on the sidewalk, delivers cheaply.

In Beirut, occlusion is not noise to be filtered. Cars parked on the sidewalk are a feature of the street itself, which is why camera placement beats algorithms there and why a car that hides the sidewalk should count as both sidewalk area and an obstruction. The guarantee the targets ask for will not come from any network. It comes from abstaining where the edges are not seen and from a field sample of roughly 150 stations that turns a forecast into a confidence interval. The practical next step is two weeks of ablations on data we already have, which will tell us how much of that guarantee automation can carry and how much has to come from people.
