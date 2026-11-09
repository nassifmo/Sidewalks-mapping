# Prove Sidewalk Mapping in Beirut, Then Scale

The most accurate nationwide method is to walk or drive a fixed-height 360° camera along every street in Lebanon's towns, measure width and obstructions automatically from that imagery, and send every value through a field-measured gate before it is published. The work starts with a benchmark of about **1,750 laser-measured stations on roughly 335 block faces** in four Beirut and Tripoli test areas, and no module scales until its error is known there **[C]**. The benchmark is needed because the best published street-level width method reaches **0.25 m mean absolute error only when the camera height is known**, and its error rises to 1.57 m without scale calibration ([UrbanVGGT](https://arxiv.org/html/2603.22531)). No method has been validated on Beirut's narrow, car-lined sidewalks. Lebanon has about **36,200–36,700 km of sidewalk-relevant street centreline**, and OSM records sidewalks on only about 167 km of it. The realistic target is the **42,700 block-face km in dense and urban-cluster areas where 93% of people live**. Of that, about **29,400 km (69%) lies in districts where field capture can proceed now**. The rest is south of the Litani, in the Bekaa/Baalbek-Hermel and Nabatieh, in Dahiyeh or in the camps, and needs deferral or partners **[C]** ([HDX HOT roads](https://data.humdata.org/dataset/hotosm_lbn_roads); [Overpass](https://overpass-api.de/api/interpreter)). With assumed Lebanese rates, the safe 69% takes about **30 months, a peak team of about 30 people and about US$1.2 million**. Fixed staff dominate the budget; cameras and GPUs cost little **[C from A]**. Three things decide whether the accuracy holds: a logged camera height within ±5 cm, positions post-processed against the Army's LEB-CORS network, and a production model stack whose licences permit an ODbL release. Ultralytics YOLO, the original VGGT-1B weights, MASt3R and UniDepthV2 do not meet that last test. One step cannot wait. Beirut begins enforcing against sidewalk occupation on **16 November 2026**, ten days from now, so a baseline capture of the pilot area's commercial frontages must happen before then ([Libnanews](https://en.libnanews.com/beirut-abboud-sets-violators-free-sidewalks-global-voices)).

Numbers in this report are tagged. Figures with a citation are **sourced**. **[C]** marks figures computed for this plan from sourced inputs, using the scripts in `research_notes/Nationwide sidewalk mapping plan Lebanon/scope_work/` or the formulas shown. **[A]** marks planning assumptions to be replaced by benchmark measurements. **[C from A]** marks figures computed from assumed inputs. "Block face" means one side of one street between intersections, the unit of the pilot's `sw_id`.

## The benchmark proves each module on about 1,750 measured stations before scale-up

### Four Lebanese test areas, five external benchmarks

The primary gold-standard area should be the existing pilot extent: **Mar Mikhael–Gemmayzeh–north Achrafieh** (lon 35.508–35.530, lat 33.884–33.905). It overlaps the MIT City Form Lab/AUB Community Streets study zones ([MIT City Form Lab](https://cityform.mit.edu/projects/beirut-community-streets)). Within about 4.6 km² it holds arterials, old-fabric lanes, public stairs, post-blast rebuilt frontages and nightlife terraces, and about **150–170 km of potential block-face sidewalk** (computed earlier from the pilot's `osm_streets.geojson`) **[C]**. Three more areas test generalisation. **Hamra/Ras Beirut** sits next to AUB and has a known reference retrofit: Jeanne d'Arc Street, where removing a parking lane created a 1.5 m obstacle-free sidewalk ([L'Orient Today](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html)). **Bourj Hammoud** is an in-Beirut stress test of dense informal occupation. **Tripoli** (Al-Mina grid, Mamluk old-city lanes, Tell and Azmi arterials) is the out-of-city transfer test. Its municipality is procuring GNSS RTK equipment, which makes it a plausible partner ([Tripoli tender, July 2026](https://tripoli.gov.lb/wp-content/uploads/2026/07/شراء-GNSS-RTK-دعوة-ثانية.pdf)).

External benchmarks serve a different purpose: they check that the software is correct before Beirut checks its accuracy. No verified MENA or Mediterranean city publishes open width plus obstacle data, so each external set tests one module.

- **Washington DC** offers CC BY 4.0 sidewalk polygons ([data.gov](https://catalog.data.gov/dataset/sidewalks-2021)) and the UrbanVGGT sample of about 300 Street View images with reference widths of 0.56–3.94 m. Re-running the team's width module there is the only like-for-like comparison with the published 0.252 m MAE ([UrbanVGGT](https://arxiv.org/html/2603.22531)).
- **Paris** publishes ODbL sidewalk footprint polygons and curb lines, updated about monthly. They test overhead geometry and polygon-derived total width, but the portal warns they are not survey-grade ([data.gouv.fr emprises](https://www.data.gouv.fr/datasets/plan-de-voirie-trottoirs-emprises); [trottoirs filaires](https://www.data.gouv.fr/datasets/plan-de-voirie-trottoirs-filaires)).
- **Project Sidewalk Mexico City** has CC0 geolocated obstacle, surface-problem and curb-ramp labels. It is the closest informal-street obstacle test ([Project Sidewalk CDMX API](https://sidewalk-cdmx.cs.washington.edu/api)).
- **Seoul** has 514 phone images taken at 1.0 m height, with laser-measured effective width, slopes and A–E pavement grade. It is the only field-measured pedestrian-level set ([arXiv 2609.17882](https://arxiv.org/html/2609.17882)).
- **PathwayBench** covers pedestrian-network routability across 8 cities ([arXiv 2407.16875](https://arxiv.org/pdf/2407.16875)).
- PEDESTRIAN (29 obstacle classes, 82,120 frames) and Roboflow SOD (22 classes) are secondary obstacle sets, both with licences unconfirmed ([PEDESTRIAN](https://arxiv.org/abs/2512.19190v1); [SOD](https://universe.roboflow.com/lamao/sod-enect)).

None of these sources contains curb-height ground truth, so curb height has to come from Lebanese fieldwork.

### The gold-standard protocol measures five widths, two slopes and the curb at fixed stations

**Step 1: frame and stratify.** Split OSM street segments into left and right faces with the pilot's `sw_id`. Stratify by street type (arterial, collector/commercial, local residential, old-fabric lane under 6 m right-of-way, stairs/pedestrian-only), crossed with Mapillary coverage (good/poor) and nominal width band (<1.2 m, 1.2–2.0 m, >2.0 m). Before selecting faces, run the pilot's `fetch_mapillary.py` with a token and compute images per km and the share of street length with a post-2022 image within 10 m. The benchmark note recommends this API query; it has not yet been run.

**Step 2: place stations.** Put stations every **20 m** along each face, matching the pilot's transect spacing, and add one at every pinch point (pole, tree, generator, ramp, step). The benchmark note proposed 10 m spacing. This plan deliberately uses fewer stations per face across more faces, for the statistical reason given below.

**Step 3: measure each station** into a QField form keyed to the station ID. QField is chosen because collectors must edit geometry offline ([QField](https://qfield.cloud/pricing)). Record:

- **total width** W_tot: building or property line to the top-back of the curb, perpendicular to the curb line;
- **clear width** W_clear: narrowest passage past *permanent* objects, measured obstacle-edge to obstacle-edge as PROWAG specifies ([Federal Register 2023-16149](https://www.govinfo.gov/content/pkg/FR-2023-08-08/html/2023-16149.htm));
- **operational width** W_op: the same as W_clear but also excluding temporary occupation, recorded once per time window;
- **curb height**: mean of two readings 0.5 m apart;
- **cross slope** over 0.6–1.0 m and **longitudinal slope** over 1–2 m, with a 0.1° digital level;
- **furniture-zone width**;
- **surface condition** on the Seoul A–E scale, cross-walked to the pilot's `condition` domain;
- flags for curb ramp, steps and driveway apron.

Each obstruction gets its class from the pilot's 21 types, an RTK point, laser footprint dimensions, its permanence and the clear width remaining beside it. Report widths against three thresholds: **1.22 m** (PROWAG minimum), **1.5 m** (UK Inclusive Mobility constrained minimum, also the Jeanne d'Arc target) and **2.0 m** (Inclusive Mobility preferred) ([DfT Inclusive Mobility](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1044542/inclusive-mobility-a-guide-to-best-practice-on-access-to-pedestrian-and-transport-infrastructure.pdf); [Edinburgh P3](https://www.edinburgh.gov.uk/downloads/file/24977/p3---footways---version-11)). The earlier research found no statutory minimum sidewalk width in Lebanese law.

**Step 4: instruments.**

| Instrument | Purpose | Accuracy |
|---|---|---|
| Laser distance meter (Sincon SD-70 class, as in Seoul, or DISTO class) | Widths, footprints | about ±1–3 mm **[A]** |
| 5 m steel tape | Curb height, short offsets | mm **[A]** |
| Measuring wheel | Chainage only | 0.5–1% of distance; too coarse for widths **[A]** |
| Digital level, 0.1° | Cross and longitudinal slope | — |
| Emlid Reach RS3 rover on LEB-CORS network RTK | Station and checkpoint positions | LEB-CORS advertises about 3 cm ([LEB-CORS](https://lebcors.army.gov.lb)); RS3 retail about US$2,519–3,647 ([Advexure](https://advexure.com/products/emlid-reach-rs3)) |
| iPhone Pro LiDAR | Pinch points and stairs (3D check) | about ±10 cm outdoors, with façade deviations up to 0.48 m reported ([Glasgow](https://eprints.gla.ac.uk/311292)) |
| The team's production 360° rig at its logged height | Benchmark imagery with known camera height | — |

Log the RTK fix status on every point and drop stations without a fixed solution; under balconies, fall back to chainage from the segment start. Smartphone LiDAR is a cross-check, not a reference, because its outdoor error is similar to the error of the method under test.

**Step 5: time windows.** Measure geometry once. Record W_op and temporary obstructions in at least three passes: weekday 09:00–11:00, weekday 18:00–21:00 (Mar Mikhael and Gemmayzeh nightlife terraces peak in the evening) and Saturday evening. Capture 360° imagery in the same windows so detections can be matched to field observations taken at the same time.

**Step 6: human repeatability.** A second team re-measures 15–20% of faces blind on a different day. Report ICC(2,1) for W_tot, W_clear and curb height, targeting above 0.9 ("excellent" under [Koo & Li 2016](https://doi.org/10.1016/j.jcm.2016.02.012)). Report Bland–Altman limits of agreement, and Cohen's κ for condition and obstruction class. Field repeatability sets the floor: if human limits of agreement exceed about ±5 cm, a ±5 cm model claim cannot be tested.

**Step 7: positional checkpoints.** Survey at least **30 well-defined checkpoints per stratum** (curb corners, ramp tops, manhole centres), following ASPRS Edition 2. ASPRS requires checkpoints at least twice as accurate as the product and requires checkpoint error to be included in the reported accuracy ([LiDAR Magazine on ASPRS Ed.2](https://lidarmag.com/?p=15999)). Spread them under the NSSDA rule: at least 20% of points in each quadrant, spaced at least 10% of the diagonal apart ([FGDC NSSDA](https://www.fgdc.gov/standards/projects/accuracy/part3/chapter3)). Thirty points are a minimum for pass/fail, not a precise estimate: with n = 30 the true RMSE lies between 0.80 and 1.34 times the observed value, so pinning RMSE to about ±15% needs about 100 points **[C]**.

**Step 8: overhead reference.** Digitise sidewalk polygons and curb lines from the RTK points, using the AUB 2010 1:2,000 curblines ([AUB catalogue](https://scholarworks.aub.edu.lb/server/api/core/bitstreams/71b5ddf4-a555-4cf2-a70c-4bf0fc19da4a/content)) as a prior. Field-verify any AUB curb line that conflicts by more than 0.3 m, because the layer predates the 2020 blast and the rebuilding that followed.

### Sample sizes: more faces, fewer stations per face

The notes conflict here, and the conflict changes the design. The benchmark note estimates that about 100 independent width pairs per reporting stratum would bound MAE within ±5 cm. Its recommended layout, 5 strata × 8 faces × 100 m with 10 m stations, gives only about 80 stations per stratum. Stations on the same face are correlated. With 10 stations per face and an assumed intra-face correlation of 0.3, the design effect is 3.7 **[A/C]**, so 80 stations carry about 22 effective samples. That gives roughly **±0.10 m per stratum, not ±0.05 m** **[C]**.

The required effective sample is n = (1.96·σ/0.05)², where σ is the standard deviation of absolute error ([NIST e-Handbook](https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm)). From UrbanVGGT's DC numbers, σ ≈ 0.149 m and n ≈ 34. For Beirut, assume σ = 0.25 m, which gives n ≈ 96 **[C]**. Cutting stations per face to 5 (20 m spacing) lowers the design effect to 2.2, so each stratum needs about **210 stations on about 42 faces** **[C]**.

| Test area | Faces | Stations | Face km | Width precision (σ = 0.25 m) |
|---|---|---|---|---|
| Mar Mikhael–Gemmayzeh–N. Achrafieh (5 strata × ~40 faces) | ~200 | ~1,000 | ~20 | ±0.05 m per stratum; ±0.023 m pooled **[C]** |
| Hamra/Ras Beirut | ~45 | ~250 | ~4.5 | ±0.046 m pooled **[C]** |
| Bourj Hammoud (stress test) | ~45 | ~250 | ~4.5 | ±0.046 m pooled **[C]** |
| Tripoli (transfer test) | ~45 | ~250 | ~4.5 | ±0.046 m pooled **[C]** |
| **Total** | **~335** | **~1,750** | **~33.5** | — |

The pooled primary sample, about 455 effective pairs **[C]**, also clears the roughly 264 effective pairs needed to detect a 0.05 m systematic bias at 80% power **[C]**. For obstructions, ±5% precision and recall needs 385 ground-truth positives (recall) and 385 detections (precision) at p = 0.5, or 246 each at p = 0.8, before a clustering inflation of 1.3–1.5 **[C]**. At an assumed one obstruction per 10–15 m of face **[A]**, the 33.5 km benchmark yields about **2,200–3,300 objects per pass** **[C]**. That is enough to report five super-classes at about ±5%: fixed furniture, vegetation, utilities and generators, vehicles, and commercial/temporary occupation. Each of the 21 fine classes gets only about ±10% (about 96 objects each); rare classes get counts with Wilson intervals. Before fieldwork, run **one pilot day on about 10 faces** to measure the real σ and the within-face correlation, then recompute these numbers. Every figure above depends on those two values.

### Metrics and go/no-go gates per module

The metric stack follows the evaluation literature.

- **Geometry:** buffer-based completeness, correctness and quality ([Wiedemann 2003](https://www.pia.tum.de/isprs/pia03/pub/pia03_s4p2.pdf)), at sidewalk-scale 1.0 m and 2.0 m buffers rather than the 5 m common in road work.
- **Network:** PathwayBench TraversabilitySimilarity, because Tile2Net scored edge F1 0.76–0.90 but routability of only 0.04–0.17 ([PathwayBench](https://arxiv.org/pdf/2407.16875)).
- **Width:** MAE, RMSE, bias, Bland–Altman limits, and the share within ±0.25 m and ±0.50 m.
- **Categorical attributes:** confusion matrices with user's and producer's accuracy ([Olofsson et al. 2014](https://doi.org/10.1016/j.rse.2014.02.015)) and κ. Condition uses quadratic-weighted κ.
- **Point objects:** one-to-one matching within 2–3 m.

No comparable programme has published numeric gates, so the thresholds below are proposals anchored to the best published results. Each gate is passed on the **lower 95% confidence bound**, not the point estimate, and separately per stratum.

| Gate / module | Pass condition (proposed) | External sanity check | If it fails |
|---|---|---|---|
| G0 Ground truth | Human ICC > 0.9 on widths and curb height; repeat SD ≤ 2 cm; κ ≥ 0.70 on categories; ≥ 30 RTK checkpoints per stratum | — | Retrain surveyors; tighten definitions |
| G1 Network and geometry | Completeness ≥ 0.85, correctness ≥ 0.90 at a 1.5 m buffer; TraversabilitySimilarity ≥ 0.50 after human edit (best published 0.48); ≥ 98% of transects on the correct face **[A]** | Paris and DC polygons | Manual tracing remains primary in that stratum |
| G2a Width, planning grade | MAE ≤ 0.30 m and ≥ 90% within ±0.50 m | Reproduce UrbanVGGT DC within 0.05 m of 0.252 m; Seoul effective width | Fix the scale or height module; field-measure the stratum |
| G2b Width, accessibility | Sensitivity ≥ 0.90 and specificity ≥ 0.80 for clear width < 1.2 m; values in 1.2 ± 0.25 m flagged "verify in field" | Seoul | Publish width classes only |
| G2c Width, engineering grade | RMSE ≤ 0.13 m (±0.25 m at 95%) | — | Expected to fail from imagery; use field measurement |
| G3 Scale and camera height | Rig height logged within ±5 cm; GNSS-derived and height-derived scale agree within 5% | DC ablation | Reject the sequence |
| G4 Obstruction detection | Pooled recall ≥ 0.80 and precision ≥ 0.85; each super-class recall ≥ 0.70 **[A]** | Project Sidewalk CDMX at a 5 m match radius; PEDESTRIAN | That class becomes human-verified only |
| G5 On-sidewalk test and occupied width | Occupied-width MAE ≤ 0.25 m; on/off-sidewalk accuracy ≥ 0.90 **[A]** | — | Human review of all vehicle and commercial classes |
| G6 Temporal occupation | Temporary-object recall ≥ 0.75 against field observations in the same window; occupied-length share within ±10 points **[A]** | — | Report occupation from sampled field passes only |
| G7 Curb | Raised/flush/absent κ ≥ 0.70 against field. Height from the road–sidewalk plane offset is experimental and is accepted only if MAE ≤ 3 cm **[A]** | — | Curb height stays field-only (expected) |
| G8 Surface condition | Sensitivity ≥ 0.80 for "poor/very poor"; weighted κ ≥ 0.60 **[A]** | Project Sidewalk surface labels | Screening flag only, with human rating |
| G9 Privacy | Missed faces or plates ≤ 1% in a 500-frame audit **[A]** | — | Re-blur; nothing is uploaded |
| G10 Human in the loop | AI-assisted lots pass LQAS (AQL 5%, LTPD 15%) at fewer minutes per km than manual mapping | — | Stay manual in that stratum |
| G11 Transfer (Tripoli) | All gated metrics within 5 percentage points of Beirut | — | Fine-tune before national rollout |

The width gates come from the validation note's use-case logic. Planning needs about ±0.5 m. Accessibility is a threshold decision, where missing a barrier is the costly error. Engineering-grade ±0.25 m at 95% implies an RMSE of 0.13 m, which no street-level method has shown. Curb height and condition carry the lowest expectations. Project Sidewalk found surface problems the weakest category, at **75.3% precision and 59.5% recall** ([Weld et al. 2019](https://makeabilitylab.cs.washington.edu/media/talks/Weld_DeepLearningForAutomaticallyDetectingSidewalkAccessibilityProblemsUsingStreetscapeImagery_2019.pdf)). Its RampNet experiments put slope and lip height out of reach of imagery, because an 8.33% running slope over 1.5 m needs 2–3 cm of vertical accuracy ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)).

## Capture runs at a fixed 2.3 m height, positioned against LEB-CORS, in five time windows

### Equipment and settings

The production camera should be the **GoPro MAX 2**. It costs US$499.99, records 8K30 360° video, has built-in GPS and native Mapillary `.360` support ([Imaging Resource](https://old.imaging-resource.com/news/2025/09/23/gopro-max-2-launched-price-8k-360-video-features-and-where-to-buy); [Mapillary forum](https://forum.mapillary.com/t/new-seamless-support-for-360-video-files-gopro-max2/10119)), and Mapillary names it its recommended consumer 360° camera ([Mapillary Help](https://help.mapillary.com/hc/en-us/sections/17261805417500-Our-favorite-cameras)). The Insta360 X5 has a sharper 72 MP still mode but no GPS of its own, and Mapillary does not recommend its interval-photo mode because geotags fail after the first frame ([Insta360 X5 specs](https://onlinemanual.insta360.com/x5/en-us/specs/shooting-specs); [Mapillary forum](https://forum.mapillary.com/t/insta-360-x5-camera/9516)). Shoot **8K**: one field tester found shop signs and house numbers hard to read at 5.6K and readable at 8K. The same tester reported that the camera fills a 64 GB card in about 2 hours, that the battery lasts about 2 hours or less, and that a file is left unclosed if power or card space runs out mid-recording ([OSM diary apm-wa](https://www.openstreetmap.org/user/apm-wa/diary/409291)). Each rig therefore carries 3–4 batteries and a 1 TB card, and crews stop recording before swapping. Survey-grade mobile mapping (the Trimble MX50 is a 23 kg, quote-only LiDAR rig) is unnecessary for this campaign and sees the sidewalk from behind parked cars ([Trimble](https://geospatial.trimble.com/en/products/hardware/trimble-mx50)). Drones are excluded because the Army suspended all drone permits on 1 March 2026 ([LBCI](https://v7cdn.lbcgroup.tv/news/lebanon-news/908645/lebanese-army-suspends-drone-permits-nationwide-amid-regional-tensions/en)).

**Camera height is the controlling accuracy parameter.** UrbanVGGT's sensitivity table shows MAE of 0.384 / 0.283 / 0.252 / 0.276 / 0.349 m when the assumed height is 2.00 / 2.25 / 2.50 / 2.75 / 3.00 m against a true 2.5 m, and the width bias follows the sign of the height error ([UrbanVGGT](https://arxiv.org/pdf/2603.22531)). Each 10 cm of height error at 2.5 m is a 4% scale error, about 8 cm on a 2 m sidewalk **[C]**. The walking rig is therefore a rigid backpack pole with the lens at about **2.3 m [A]**, at least 30 cm above the head as Mapillary advises ([Mapillary Help](https://help.mapillary.com/hc/en-us/articles/360012674619)). The GNSS antenna sits 60–80 cm below the camera to keep it out of the panorama, a documented GoPro–RTK setup ([OSM diary oldnab](https://api.openstreetmap.org/user/oldnab/diary/408535)). The car rig is a roof mast at about 2.5 m. Crews measure the lever arm and lens height with a tape at the start of every session and write it to `camera_height_m` and to the sequence record. Seoul's handheld 1.0 m capture is not copied: a hand-held phone does not hold a constant height.

| Item | Walking rig | Car rig |
|---|---|---|
| Camera | GoPro MAX 2, 8K30 360° video, original `.360` files kept | Same |
| Height | about 2.3 m on a rigid pole, logged ±5 cm **[A]** | about 2.5 m on a roof mast, logged **[A]** |
| Frame extraction | `mapillary_tools` time sampling, `--video_sample_distance -1 --video_sample_interval 2` (about 2.8 m at 5 km/h) | interval about 0.3–0.4 s (about 2–3 m at 20–30 km/h) **[C]** |
| GNSS | u-blox F9P-class or Emlid raw logger on the same pole, PPK | Same, on the mast |
| Speed and coverage | about 4–5 km/h; one pass per side where the street is wider than about 12 m, a centreline pass where narrower | 15–30 km/h; both sides in one pass |
| Daily output | about 15 km of track per walker-day **[A]** | about 60 km per car-day **[A]** |

Frame sampling must be time-based, because `mapillary_tools` can geotag video from an external GPX log only in interval mode. The original `.360` files must be kept: exporting to MP4 through GoPro Player has broken GPMF timestamp alignment ([mapillary_tools](https://github.com/mapillary/mapillary_tools); [Mapillary forum](https://forum.mapillary.com/t/from-mp4-to-mapillary/5311)). Mapillary recommends 2 s timelapse stills for walking and video for vehicles ([Mapillary Help](https://help.mapillary.com/hc/en-us/articles/360012674619)). This plan uses video for both, because structure-from-motion and occlusion recovery need 2–3 m spacing. The benchmark should test 2 s stills on a few faces as a cheaper-storage alternative.

### Walking versus driving

Walking is the default in dense cores. A car in the carriageway sees the curb from behind the parked cars that occupy it, which is UrbanVGGT's main failure mode. Driving suits arterials and suburban streets with visible curbs. The benchmark settles the split empirically: run both rigs over the same faces, and allow driving in a stratum only if the car rig's width MAE is within 0.05 m of the walking rig's and the curb is visible on at least 80% of faces **[A]**.

### Positioning against LEB-CORS

Phone and consumer-camera GNSS errs by about 5–10 m in urban canyons ([PolyU/ION](https://ira.lib.polyu.edu.hk/handle/10397/92730?mode=full)). That is enough to find the street but not the side of the street. LEB-CORS, run by the Army's Directorate of Geographic Affairs, has **13 stations offering network RTK at about 3 cm and RINEX for post-processing**. It was built in 2023 for US$700,000 ([LEB-CORS](https://lebcors.army.gov.lb); [LBCI](https://www.lbcgroup.tv/news/lebanon-news/691386/lebanese-army-launches-online-network-to-facilitat/en)). Its subscription terms and civilian access are unpublished.

The production workflow uses **PPK rather than live NTRIP**, so dropped connections in urban canyons do not lose data:

1. Log raw GNSS on the pole.
2. Post-process against LEB-CORS RINEX in RTKLIB or Emlid Studio.
3. Align to GoPro GPMF GPS time.
4. Apply the measured lever arm.
5. Refine poses in OpenSfM or COLMAP with GNSS priors.

A published GoPro MAX plus SparkFun RTK workflow for Panoramax shows the pattern works ([binnette tutorial](https://awesome.ecosyste.ms/projects/github.com%2Fbinnette%2Fgopro-max_sparkfun-rtk-express_panoramax)). If the Army refuses access, the fallback is a pair of RS3 units with one as a local base. The target is sub-decimetre accuracy where the solution is fixed and SfM-bridged positions elsewhere. That target is not measured; G1 tests it.

### Privacy

Blur faces and plates with **EgoBlur** on extracted frames before anything leaves the team. EgoBlur is Apache 2.0, reports face AP 0.99 and AR 0.998, and runs at about 0.5 s per 2 MP image on a GPU ([EgoBlur](https://arxiv.org/pdf/2308.13093v2.pdf)). Panoramax's SGBlur is lossless at the JPEG-coefficient level, but it is a custom-trained YOLOv8 ([SGBlur](https://github.com/cquest/sgblur)), so the Ultralytics licence question below applies to it too. Keep raw `.360` files encrypted, access-controlled, purpose-limited and on a fixed retention period.

Law 81/2018 covers personal data, but sources disagree on whether an enforcement authority exists ([DLA Piper](https://www.dlapiperdataprotection.com/?c=LB&t=law); [Euro-Med Monitor](https://euromedmonitor.org/ar/article/5630/Lebanon:-Data-protection-law-fails-to-protect-people%E2%80%99s-privacy-and-data)). Commission a short Lebanese legal opinion. Seek an AUB IRB exemption ruling ([AUB IRB](https://www.aub.edu.lb/irb/Pages/Aboutus.aspx)). Carry Arabic letters from the university and the Governor's office, and keep cameras off military and security sites.

### Time-of-day passes

Separate two products. The **geometry baseline** is captured once, at low occupancy: weekday 06:00–08:00, or Sunday morning in commercial districts. The **occupation layer** is a repeated sample on fixed routes, with the same rig, direction and GPX so frames match. In dense cores the sample is 10% of streets, in five windows: weekday 08:00, weekday 12:00–14:00, weekday 19:00–22:00, Friday or Saturday evening, and the geometry baseline. Repeat it in summer and winter for terrace furniture. Tier 2 towns get a 5% sample, captured once **[A]**.

The pilot's `time_of_day` classes put the night boundary at 21:00, so a 19:00–22:00 pass would split between "evening" and "night". Either move the boundary to 22:00 or add an explicit `pass_id`. Warning 11866/2026 also changes the experiment: obstruction rates in the benchmark area will shift after 16 November. A pre-enforcement pass and a post-enforcement pass become a before-and-after measurement, provided both are dated.

### Data volumes

At about 32 GB per hour of 8K video, walking produces about **6.5–8 GB/km** and city driving about **1.3–2.1 GB/km** **[C]**. The Bucket C programme below therefore generates about **160 TB of raw video [C from A]**, which is about three times the capture note's 30–50 TB estimate. That estimate assumed mostly driven capture. For scale, OSM-France's Panoramax instance runs about 400 TB on ZFS ([OSM Community](https://community.openstreetmap.org/t/a-panoramax-uk-instance/119989)). Upload extracted, blurred frames from an office fibre link, not over 4G. Limited internet was the main bottleneck in the World Bank's Zanzibar capture ([Mapillary blog](https://blog.mapillary.com/update/2023/08/11/Streetview-Photographer-Mapillary.html)).

## A licence-clean pipeline turns panoramas into per-block-face records

### Twelve processing stages

| # | Stage | Tools and models | Licence status |
|---|---|---|---|
| 1 | Ingest and QC | `mapillary_tools video_process` (GPMF), PPK merge, per-sequence report of fix rate, height and gaps | Open source |
| 2 | Anonymise | EgoBlur faces and plates; raw archive encrypted | Apache 2.0 |
| 3 | Reproject | Equirectangular to pinhole crops at yaw ±90°, 90° FOV, pitch −15° to −25°, 1024²; obliques at ±45°/±135° for obstructions; intrinsics f = W/(2·tan(FOV/2)) stored per crop (py360convert or Equirec2Perspec) | Unverified; check the LICENSE files |
| 4 | Poses and scale | OpenSfM, COLMAP or GLOMAP per sequence with GNSS priors, or VGGT-1B-Commercial on 20–100-frame chunks; Umeyama fit to PPK; check against rig height (≤ 5%) | BSD (unverified); VGGT-Commercial by application, no military use |
| 5 | Segmentation | Mask2Former Swin-L, which reaches 64.7 mIoU on Vistas ([Mask2Former](https://arxiv.org/pdf/2112.01527)), fine-tuned on 1–2k Lebanese crops; classes sidewalk, curb, curb cut, road, building, wall, fence | Architecture MIT (believed); **Vistas weights' licence conflicts** |
| 6 | Width geometry | Sidewalk-plane RANSAC per transect band with UrbanVGGT's MAD threshold; 5–10 cm bird's-eye grid; curb and building polylines; transects every 1–2 m; gross and clear width; nearest 3–8 m only; reject frames where the sidewalk touches the edge or a pole truncates the span | Own code (UrbanVGGT released no code) |
| 7 | Detection | RF-DETR-M/L or DEIM-D-FINE-L on the 21 pilot classes; pre-labels from SAM 3 or Grounding DINO in CVAT or Label Studio; active learning tracked in FiftyOne | RF-DETR N–L, D-FINE and DEIM Apache 2.0; SAM 3 custom Meta licence |
| 8 | Placement and deduplication | Ray from camera through the box's ground-contact point to the plane, or multi-view triangulation; class-wise DBSCAN at ε 1–2 m, splitting clusters by same-image-pair counts ([Krylov et al.](https://arxiv.org/pdf/1708.08417); [arXiv 2305.08232](https://arxiv.org/pdf/2305.08232)); on-sidewalk status from footprint ∩ sidewalk mask; `occupied_width_m` from the footprint | Own code |
| 9 | Surface | Rectified 1 m × 1 m patches classified by a DINOv2/v3 linear probe; material and condition labelled separately; hard negatives include patterned tiles, shadows and wet surfaces ([CACAIE](https://onlinelibrary.wiley.com/doi/10.1111/mice.70125?af=R)) | DINOv2 code believed Apache 2.0 (verify) |
| 10 | Curb | Raised/flush/absent from curb mask plus plane offset; height experimental under G7 | Own code |
| 11 | Archive Mapillary heights | Cascade: metadata, GeoCalib pitch, roll and focal, metric-depth plane distance, known objects (car about 1.45–1.5 m), rig clusters. Used for training and change detection, not for authoritative width | GeoCalib Apache 2.0 per a third-party index |
| 12 | Orchestration | Ray Data or Dask sharded by sequence; DVC; MLflow; pinned containers; `model_version` and crop parameters on every output row | Open source |

Stage 6 reimplements UrbanVGGT's method with two safeguards. Project Sidewalk's Seoul test of a similar recipe on phone photos produced **0.77 m clear-width MAE**, with pitch as the dominant error: ±2° of pitch gave ±10–16% width error. The same test showed that fitting the road plane instead of the sidewalk plane inflates width by about 6% at a 15 cm curb ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)).

Detector training follows the local-data evidence. When a Mexican city was removed from training, obstacle recall fell from 60.8% to 42.0% ([Duan et al. 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)). Plan about **1,000–1,500 instances per production class [A]**, roughly 25,000 boxes across the 21 classes. Mine generators, vendor carts, kiosks, low wires and construction specifically, since no dataset contains them. Use repeat-factor sampling and copy-paste augmentation for rare classes.

Compute is cheap relative to staff. Mask2Former Swin-L runs at 2.86 fps at 512×1024 on an A100 ([MMSeg](https://openi.pcl.ac.cn/open-mmlab/mmsegmentation/src/tag/v1.1.1/configs/mask2former)). A100 marketplace prices are about US$0.50–2/h ([CloudZero 2026](https://www.cloudzero.com/blog/cloud-gpu-pricing-comparison/)). At 333 frames per km and 4 crops per frame, one pass over Bucket C is about **39 million crops and US$2,400–18,000 of GPU time [C from A]**. That is several times the ML note's US$1k–5k, which assumed 1–3 million panoramas. Segmenting every second frame halves the cost.

### Licence flags

Five licence issues decide whether the output can be published under ODbL and reused by government.

1. **Ultralytics YOLO (YOLOv8, YOLO11, YOLO26) is AGPL-3.0.** Ultralytics says this covers custom-trained weights, including models trained from scratch or used only internally, unless an Enterprise licence is bought ([Ultralytics](https://ultralytics.com/license); [Roboflow](https://roboflow.com/ultralytics)). The earlier framework report recommended a "YOLO-class" detector while marking this as unverified; it is now verified. The ROD results quoted earlier were YOLO models, and SGBlur is YOLOv8. Use Apache-2.0 RF-DETR (N–L only; XL and 2XL are under Roboflow's PML), D-FINE or DEIM ([Roboflow](https://blog.roboflow.com/rf-detr-vs-alternatives/)). Use YOLO only if the entire codebase is released under AGPL.
2. **Non-commercial weights.** VGGT-1B is non-commercial; only VGGT-1B-Commercial, released on application with a military-use exclusion, is permitted ([VGGT](https://github.com/facebookresearch/vggt); [HF](https://huggingface.co/facebook/VGGT-1B-Commercial)). MASt3R/DUSt3R are CC BY-NC-SA ([MASt3R](https://github.com/naver/mast3r)). UniDepthV2, the best native-metric model at 0.289 m, is CC BY-NC, and Depth Anything V2 is commercial only in its Small size ([Ultralytics overview](https://www.ultralytics.com/blog/best-depth-estimation-models)). MoGe's weight licence is unstated ([MoGe](https://github.com/microsoft/MoGe)).
3. **Mapillary Vistas** is described as CC BY-SA in the ICCV paper, as CC BY-NC-SA by Dataset Ninja, and as needing a paid licence for commercial products by 2017 press coverage ([Neuhold et al.](https://openaccess.thecvf.com/content_ICCV_2017/papers/Neuhold_The_Mapillary_Vistas_ICCV_2017_paper.pdf); [Dataset Ninja](https://datasetninja.com/mapillary-vistas-dataset)). Get written clarification from Mapillary, or retrain Mask2Former from Cityscapes or COCO weights plus Lebanese labels.
4. **SAM 3** uses a custom gated Meta licence ([arXiv 2511.16719](https://arxiv.org/pdf/2511.16719)). Use it only as a pre-labelling aid whose outputs humans correct.
5. **Imagery sources.** Esri imagery is for manual tracing only, and Google content may not be used to create datasets at all ([ConductAtlas copy of GMP terms](https://conductatlas.com/platform/google-maps/google-maps-platform-terms-of-service/provision/CA-P-041128/prohibition-on-creating-content-from-google-maps-content/); [OSM wiki](https://wiki.openstreetmap.org/wiki/Google)).

Non-commercial models may still be used in research benchmarking, provided `model_version` records them and none of their outputs enters a release.

### Fusion writes into the pilot schema, extended by eight fields and two tables

Build block faces from OSM centrelines with sidewalkify or OSMnx offsets ([sidewalkify](https://github.com/AccessMap/sidewalkify)), clip them to Microsoft footprint frontage, and split them at intersections, carrying the pilot's `sw_id`. Assign each transect and detection to a face using the camera's side of the road and the crop yaw. Accept an assignment only within 15 m perpendicular distance and with matching heading.

Automated outputs then land in the existing GeoPackage layers (`survey/sidewalk_survey.gpkg`, EPSG:32636) as follows:

- **`width_measurements`**: one line per accepted transect, with `total_width_m` from geometry, `clear_width_m`, `pinch_point = yes` at the face minimum, `camera_height_m` from the rig log, the image key in `mapillary_image_id`, `data_method = auto_model`, `model_version` and `confidence`.
- **`obstructions`**: one point per deduplicated object, with `ob_type` from the 21 classes, `permanence`, `occupied_width_m`, `clear_width_left_m`, and `observed_date`/`observed_time` from the frame timestamp, so `time_of_day` is computed automatically.
- **`sidewalks`**: one polygon per face, built from the fused curb and building polylines, with `surface`, `condition`, `has_curb` and `curb_ramp`. `curb_height_cm` is written only from field data.

The live summary fields (`width_median_m`, `width_min_m`, `clear_width_min_m`, `obstructions_per_100m`) already aggregate these layers and already exclude rejected records. They are QGIS expressions, though, and will not scale to hundreds of thousands of faces. Production should compute them in PostGIS or GeoPandas with identical definitions **[A]**. EPSG:32636 can stay nationwide: at Lebanon's eastern edge (36.6°E, 34°N) the UTM 36N scale factor is about 1.001, so width error is about 1 mm per metre **[C]**.

The benchmark and fusion steps need the following schema additions (this plan's design):

- **On `width_measurements`:** `operational_width_m`, `pass_id`, `observed_date` and `observed_time`, so W_op can be stored per time window.
- **On `sidewalks`:** `slope_cross_pct`, `slope_long_pct`, `furniture_zone_m`, `width_p10_m`, `width_iqr_m`, `n_sequences`, `curb_present_ratio`, `surface_bad_ratio`, `qa_lot_id` and `last_verified`.
- **New `capture_sequences` table:** rig ID, logged height, height source (known or estimated), GNSS mode, fix rate and pass window.
- **New long `observations` table:** `sw_id`, attribute, value, method, date, model version and confidence.

Per-face values are chosen by method rank, not averaged. The order is field measurement, then validated automation from the team's own fixed-height capture, then manual tracing, then automation on archive Mapillary, then overhead output, then priors such as curbline-to-footprint distance. The confidence score combines the number of independent sequences (at least 2 preferred), agreement between single-view and multi-view widths, ground-plane residual, boundary segmentation confidence, camera-height certainty and occluded share. Low-confidence faces go to human review. Temporary obstructions remain dated observations and never become permanent attributes.

## Production QA runs on LQAS lots, double-coding and hidden gold items

Scaling replaces the benchmark's census with acceptance sampling. Lot quality assurance sampling (LQAS) inspects n items from a lot and rejects the lot when the defects exceed c ([PMC3931287](https://pmc.ncbi.nlm.nih.gov/articles/PMC3931287)). Binomial plans computed for this programme are below **[C]**.

| Plan | n | Accept if defects ≤ | Use |
|---|---|---|---|
| AQL 10%, LTPD 25% | 55 | 9 | First production month |
| **AQL 5%, LTPD 15%** | **77** | **7** | **Default** (P_accept 0.962 at 5%, 0.093 at 15%) |
| AQL 3%, LTPD 10% | 104 | 6 | Release-critical attributes (clear width, presence) |
| AQL 2%, LTPD 8% | 98 | 4 | Tightened inspection after a rejected lot |

A lot is one mapper-week or a batch of about 1,000 block faces within one district. A face is **defective** if any of the following holds: a missing or false sidewalk longer than 2 m, a width error above 0.5 m, a wrong surface class, a wrong curb class, a missed or false obstruction of a gated class, or broken connectivity at a crossing. A rejected lot gets 100% review, and its mapper moves to tightened inspection, in the ISO 2859 switching style. At an assumed 100 m average face length, Bucket C holds about 294,000 faces, or about 294 lots. That means about 22,600 faces audited, roughly 7.7% **[C from A]**.

Reviewers are certified before production. Each must reach **κ ≥ 0.70** and width MAE ≤ 0.15 m on a 30–50-item gold test drawn from the benchmark. During production, **5–10% hidden gold items** go into every batch, and a reviewer is recalibrated when their rolling κ falls below 0.60. **10% double-coding** feeds continuous κ and ICC tracking, and monthly sessions resolve disagreements. Percent agreement is reported alongside κ for rare classes, where κ misleads. Any attribute that falls below κ = 0.40 in the benchmark is merged or dropped.

The precedents support this design. Item-level reliability in MAPS audits was much weaker than subscale reliability: 50% of items were good or excellent and 11% low ([Millstein et al.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3728214/)). Simple QC raised crowd accuracy from 81% to 93% ([Hara et al. 2013](https://makeabilitylab.cs.washington.edu/media/publications/Hara_CombiningCrowdsourcingAndGoogleStreetViewToIdentifyStreetLevelAccessibilityProblems_CHI2013.pdf)). Five labellers per street lifted Project Sidewalk recall from 68% to 92% ([Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)). Washington State's statewide effort routes every automated task through interactive human QC ([arXiv 2410.19762](https://arxiv.org/abs/2410.19762)).

Field verification continues in production. Re-measure about **1% of block-face km [A]** each wave with the gold protocol, which also provides the national curb-height sample. Re-run G11-style checks whenever a new city or rig enters. Map the QA report onto ISO 19157 quality elements (completeness, positional, thematic and temporal accuracy) so it fits government spatial-data-infrastructure metadata ([IHO MSDIWG](https://iho.int/uploads/user/Inter-Regional%20Coordination/MSDIWG/MSDIWG14/MSDIWG14_11.2_DataQuality.pdf)).

## Lebanon needs 42,700 block-face km in its towns, 29,400 of them in safe districts

### National scope

The HOT/HDX "Roads of Lebanon" export (OSM snapshot of 2 November 2026) and a live Overpass query of 6 November 2026 agree within 3%. The difference comes from boundary handling. Lebanon has **47,100–48,400 km of `highway=*`**, of which **36,200–36,700 km** is sidewalk-relevant: trunk to tertiary, residential, unclassified, living street and pedestrian ways **[C]** ([HDX](https://data.humdata.org/dataset/hotosm_lbn_roads); [Overpass](https://overpass-api.de/api/interpreter)). HeiGIT's July 2024 extract gave 51,700 km ([HDX HeiGIT](https://data.humdata.org/dataset/lebanon-road-surface-data)).

Existing pedestrian data is close to zero. About **167 km carry any `sidewalk*` tag, 7.8 km are mapped as `footway=sidewalk`, and `width` appears on 0.03% of features** ([HOT quality report](https://production-raw-data-api.s3.amazonaws.com/ISO3/LBN/roads/hotosm_lbn_roads_report.html)). The earlier report's "32 `footway=sidewalk` ways" counts the same thing in ways rather than km. The programme therefore creates attributes rather than validating existing ones.

Each segment was assigned to the WorldPop 2020 1 km density class of its midpoint cell ([WorldPop](https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/LBN/lbn_ppp_2020_1km_Aggregated_UNadj.tif)), using GHSL thresholds without DEGURBA's contiguity rules. Dense cells (≥1,500/km²) hold 7,935 km of centreline and 4.93 million people. Urban-cluster cells (300–1,500/km²) hold 13,410 km and 1.39 million **[C]**. Population figures are indicative, because the raster sums to 6.83 million, including refugees, against a UN estimate of 5.85 million. The density classes are robust to that difference.

| Governorate (COD) | Dense | Urban-cluster | Rural | Very low | Dense+cluster block-face km |
|---|---|---|---|---|---|
| Mount Lebanon (incl. Keserwan-Jbeil) | 3,382 | 3,758 | 2,370 | 722 | 14,279 |
| South | 1,229 | 2,152 | 790 | 354 | 6,762 |
| Nabatieh | 891 | 2,134 | 1,212 | 740 | 6,051 |
| North | 809 | 1,773 | 1,179 | 367 | 5,165 |
| Bekaa | 595 | 1,293 | 1,273 | 856 | 3,774 |
| Baalbek-Hermel | 504 | 1,364 | 1,880 | 1,341 | 3,735 |
| Akkar | 69 | 929 | 1,564 | 608 | 1,995 |
| Beirut | 456 | 8 | 15 | 3 | 929 |
| **Total** | **7,935** | **13,410** | **10,291** | **5,077** | **42,690** |

*Sidewalk-relevant centreline km by WorldPop density class **[C]**. Block-face km = 2 × centreline.*

Tier 1 (dense) is about 15,900 block-face km and Tier 2 (urban cluster) about 26,800. Tier 3 (rural) adds 20,600 and is handled with a village-centre rule (300–500 m around the municipal centre or school) if at all **[C/A]**. Tracks (about 7,200–7,700 km), paths and most service roads are excluded, apart from dense service alleys and camp alleys that function as streets. About 300 km of dense-cell motorway, such as the Beirut–Jounieh autostrade, becomes a frontage and crossing layer rather than two-sided sidewalk.

Existing imagery barely helps. Roads with at least one Mapillary-based HeiGIT prediction total 2,571 km, or 4.9% of HeiGIT's segment km. Beirut has 31.7% and Nabatieh and Baalbek-Hermel 0%. Most of that imagery dates from 2017–2020, before the blast and two wars **[C]**. New capture is therefore needed for an estimated **95–98% of Tier 1–2 faces**. Archive Mapillary is useful only for training, for change-detection baselines and for choosing benchmark strata.

### Security buckets decide where fieldwork can happen

The March–April 2026 war displaced about 1.05 million people, and Israel declared an 8–10 km "security buffer zone" ([UK CPIN bulletin](https://assets.publishing.service.gov.uk/media/69fca0922a6137e93226b85c/LBN_Country_Bulletin_Security_situation.pdf)). By September, Israeli troops occupied swathes of the south, and strikes continued without warning north of the zone, including in Nabatieh ([Reuters via bdnews24](https://bdnews24.com/world/middle-east/11d1c0409895)). Under the June framework's "pilot zone" mechanism, residents returned only after survey and clearance ([Al Jazeera](https://www.aljazeera.com/news/2026/8/5/lebanon-and-israel-still-split-over-disarming-hezbollah-at-rome-talks)). Camp disarmament remains incomplete in Ein el-Hilweh ([L'Orient Today](https://today.lorientlejour.com/article/1489912/fatah-hands-over-its-last-heavy-weapons-to-the-lebanese-army-in-saidas-ain-al-hilweh-camp.html)).

| Bucket | Definition (district-level approximation) | Dense+cluster centreline km | Block-face km | Share |
|---|---|---|---|---|
| A: defer; remote prep only | Sour, Bent Jbeil, Marjaayoun, Hasbaya | 3,070 | 6,139 | 14% |
| B: conditional, partner-led | El Nabatieh district; Baalbek and Hermel; Dahiyeh proxy (Chiyah, Haret Hreik, Tahouitat el-Ghadir, 223 km) | 3,571 | 7,142 | 17% |
| C: proceed | All other districts | 14,704 | 29,409 | 69% |

*Security buckets **[C]**. Bucket assignments are a planning assumption: Sour city lies north of the Litani, and the occupied belt does not follow district lines.*

Every work package passes a security check before release rather than following a fixed map, because the 2026 strikes also reached central Beirut. Bucket B works through municipal unions, local universities and, in the 12 UNRWA camps, the popular committees, with daytime windows and a stop rule tied to evacuation warnings. In Bucket A, the OSM backbone is prepared remotely and destroyed villages are flagged. Capture waits for handovers, UXO clearance and reconstruction, since rebuilding will redesign those streets.

### Rollout waves

Within Bucket C, phasing follows density first and then a priority score. The proposed weights are population density 30%, schools, universities and hospitals within 400–800 m 25%, transit 20%, safety 15% and equity 10% **[A]**. Transit means the 11 public bus routes and the planned Tabarja–Beirut BRT corridor ([World Bank P160224](https://projects.worldbank.org/P160224?lang=en)). Safety matters because pedestrians were 43% of reported road deaths in WHO's 2015 profile ([WHO](https://cdn.who.int/media/docs/default-source/country-profiles/road-safety/road-safety-2015/road-safety-2015-lbn.pdf)). Delivery units are the 25–26 districts or unions of municipalities, not the 1,065 municipalities, which are too small and numerous ([UNDP](https://www.undp.org/lebanon/publications/2025-lebanese-municipal-and-mukhtar-elections-key-results)). Municipalities serve as QA and sign-off units.

| Wave | Area | Centreline km | Block-face km | Walk km incl. occupation passes | Drive km | Walker-days | Car-days | Raw video |
|---|---|---|---|---|---|---|---|---|
| 0 | Benchmark (4 areas) | — | ~34 faces | — | — | — | — | — |
| 1 | Beirut + Metn + Baabda dense, excluding Dahiyeh | 2,128 | 4,256 | 5,142 | 389 | 343 | 6 | 37 TB |
| 2 | Other Bucket C dense cores (Kesrouan, Saida, Zahle, Tripoli-Mina, Minieh, Aley, Chouf, Jbeil, Batroun, Koura, Zgharta and others) | 3,606 | 7,212 | 8,713 | 660 | 581 | 11 | 62 TB |
| 3 | Bucket C urban-cluster | 8,971 | 17,942 | 7,015 | 7,428 | 468 | 124 | 62 TB |
| 4 | Bucket B, conditional | 3,571 | 7,142 | 5,072 | 2,057 | 338 | 34 | 39 TB |
| 5 | Bucket A, deferred | 3,070 | 6,140 | 3,718 | 2,022 | 248 | 34 | 29 TB |

*Rollout waves **[C from A]**. Centreline km are sourced from the HOT export; capture km, days and volumes are computed from the assumptions below.*

The assumptions are these. In dense cores, trunk to secondary roads (13.3% of dense km) are driven at 1.2 passes and everything else is walked at 1.5 passes. Urban-cluster streets are 60% driven and 40% walked at 1.2 passes. Occupation passes add 0.8× centreline in dense cores and 0.2× in clusters, and 15% is re-captured. Throughput is 15 km per walker-day, 60 km per car-day and 7 / 1.7 GB per km.

If full coverage proves unaffordable, the scope note's stratified alternative maps all of Tier 1, about 10% of Tier 2 and about 3% of Tier 3: roughly **19,200 block-face km, 26% of the theoretical 73,400** **[C]**. It uses Neyman allocation over about 96 strata (governorate × density × road group) and still gives national indicators with confidence intervals.

## About thirty people, thirty months and US$1.2 million cover Bucket C

### Team

At peak the programme needs about 30 people **[A]**:

- **core team of eight:** project lead, GIS/data lead, two ML engineers, pipeline engineer, QA lead, field and security coordinator, and a part-time partnerships/legal liaison;
- **six to eight capture walkers;**
- **two car crews** of driver plus operator;
- **one two-person gold-standard survey team;**
- **eight reviewers and annotators.**

Eight walkers at 18 days a month supply about 1,700 walker-days a year against the 1,391 Bucket C needs, and two cars cover their 141 car-days in about four months **[C from A]**. Field capacity is therefore not the binding constraint. Review throughput and security windows are.

### Timeline

| Months from Nov 2026 | Step | Exit criterion |
|---|---|---|
| 0 (before 16 Nov 2026) | Run `fetch_mapillary.py` with a token; one walking 360° pre-enforcement pass of the pilot's commercial frontages at logged height; send data requests for the AUB curblines and the Community Streets table | Dated, blurred baseline archived |
| 0–2 | LEB-CORS access; legal opinion and IRB ruling; Governor's letter; security protocol; procurement; rig build and height calibration; 1-day σ/ICC pilot on 10 faces | Sample sizes recomputed; G0 protocol frozen |
| 1–4 | Benchmark gold standard in Mar Mikhael–Gemmayzeh, Hamra and Bourj Hammoud; capture in all windows; external runs (DC, Seoul, Paris, CDMX, PathwayBench) | G0 passed; error tables per stratum |
| 2–6 | Model development, Lebanese labelling, active learning; walk-versus-drive test | Gates G1–G10 reviewed at month 6 |
| 6–7 | Tripoli transfer test; summer occupation pass | G11 passed |
| 8 | First ODbL release of the benchmark area; OSM community proposal | OpenSidewalks validation passes |
| 7–12 | Wave 1 | LQAS lots accepted |
| 11–19 | Wave 2 | Same |
| 16–28 | Wave 3 | Same |
| 24–30+ | Waves 4–5 as security allows; national release | Bucket C complete |

Overlapping waves 2 and 3 is possible because walkers move to cluster towns while reviewers finish the dense cores. The benchmark spans the November 2026 enforcement start and the summer 2027 terrace season, which provides the seasonal contrast the occupation layer needs.

### Budget

| Line | Basis | US$ |
|---|---|---|
| Core team, 30 months | about $23,000/month **[A]** | 690,000 |
| Capture field days | 1,391 walker-days × $70 + 141 car-days × $150 **[A]** | 118,500 |
| Benchmark gold standard and Tripoli | about 260 team-hours, two people at $80/day, plus travel **[C from A]** | 10,000 |
| Production field verification (1% of block-face km) | about 980 team-hours at 300 m/h **[C from A]** | 26,000 |
| Annotation (about 25k boxes, 2k dense crops, 5k patches, 3 rounds) | assumed minutes per item at $40/day | 15,000 |
| Production review (flagged faces, LQAS audits, double-coding) | about 6,750 h at $50/day **[C from A]** | 42,000 |
| Equipment | 14 GoPro MAX 2 at $500; 10 GNSS loggers **[A]**; 2 RS3 at $2.5–3.6k; poles and masts, lasers, levels, 2 iPhone Pro, 2 GPU workstations **[A]** | 45,000 |
| Storage, about 250 TB usable × 2 copies | $50/TB **[A]** | 25,000 |
| Cloud GPU, one pass plus 2–4 reruns | from the stage costs **[C from A]** | 35,000 |
| Legal, permissions, insurance, security | **[A]** | 30,000 |
| LEB-CORS subscription | unpublished | TBD |
| **Subtotal** | | **≈1,036,000** |
| **With 20% contingency** | | **≈1,240,000** (about $42 per block-face km) |

Treat ±30% as the honest band. Waves 4 and 5 add about 590 walker-days and roughly 12 more months of core team, about US$0.35–0.45 million **[C from A]**. No source gives a cost per km for any comparable campaign. The Zanzibar and Mapillary grant programmes report output (699,000 images over 1,800 km; 8.5 million images from 40 cameras) but not cost ([Mapillary blog, Zanzibar](https://blog.mapillary.com/update/2023/08/11/Streetview-Photographer-Mapillary.html); [Mapillary blog, camera grants](https://blog.mapillary.com/update/2024/10/31/recapping-the-camera-grant-program)). These figures therefore need re-basing after the benchmark.

## Risks, mitigations and note conflicts the plan must carry

| Risk | Mitigation |
|---|---|
| Security escalation, or strikes reaching Bucket C | Security check before each work-package release; Lebanese-led crews; daylight sessions; evacuation-warning stop rule; partner-led capture in Bucket B |
| LEB-CORS access refused or unaffordable | PPK against an own RS3 base; SfM bridging; chainage referencing for audits |
| Camera-height drift | Rigid poles, per-session tape log, G3 rejection, plane-distance check |
| Parked-car occlusion of curbs | Walk dense cores; multi-sequence fusion; interpolate the curb across gaps; publish occluded share in confidence |
| Domain shift (US-trained models) | Lebanese labels with active learning; G11 Tripoli test; a pilot city in each new wave |
| Licence contamination | Licence-clean stack; `model_version` audit; no NC weights in releases |
| Privacy or legal challenge; shopkeeper hostility during enforcement | EgoBlur before upload; encrypted raw files; legal opinion; Governor's letter; no interviews without IRB |
| GoPro file corruption, battery or card failures | Stop before swaps; 1 TB cards; good card readers; daily checksum ingest |
| Bandwidth and power outages | Office-fibre upload; local ZFS staging |
| OSM community rejects bulk edits | Consult first; MapRoulette tasks; never auto-overwrite |
| Data goes stale (reconstruction, enforcement) | Dated observations; change detection; 3–5-year re-validation, annual in high-change zones **[A]** |

The notes conflict in seven places, and the plan resolves each one.

1. **ROD dataset.** The earlier framework notes cite a "ROD" obstacle dataset (arXiv 2611.00681, MIT licence, 25 classes, partly Tehran imagery, YOLO mAP@50 about 0.88). The benchmark note searched and found no such dataset. Until someone opens the arXiv page and the Kaggle/Hugging Face release, ROD is treated as unverified. Its numbers are excluded from gates, and PEDESTRIAN, SOD and Project Sidewalk take its place.
2. **Seoul dataset.** One note gives Zenodo DOI 10.5281/zenodo.22699523 with a CC0 licence. The paper page shows neither a repository URL nor a licence, and the DOI could not be verified. Email the authors before relying on it.
3. **Beirut obstruction baseline.** The Community Streets report says about **17% of sidewalks** have permanent obstructions ([report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)). Press coverage says nearly 20% (or 18%) of **street length** ([L'Orient Today](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html)). The denominators differ. Use 17% of sidewalks as the comparable baseline, and have the programme publish both bases.
4. **Ultralytics licensing.** The earlier report marked the AGPL question unverified; the new notes verify it.
5. **Benchmark sample sizes.** The benchmark note's 80-stations-per-stratum layout cannot deliver its own ±5 cm-per-stratum target. The redesign above fixes this.
6. **Compute and storage.** The earlier GPU and storage estimates (US$1k–5k; 30–50 TB) assumed mostly driven capture. Walking capture raises both several-fold.
7. **Walking capture mode.** Mapillary recommends 2 s stills for walking; this plan uses video for structure-from-motion, with stills to be tested in the benchmark.

Smaller discrepancies (Overpass versus HOT totals, 8 versus 9 governorates, population totals, the HeiGIT 2024 length) are documented in the scope tables and do not change any decision.

## Publish under ODbL in OpenSidewalks and enter OSM only by consent

The release licence is **ODbL** from the start. Mapillary's terms require ODbL for derived data published outside OSM ([Mapillary Help](https://help.mapillary.com/hc/en-us/articles/115001777705)), and ODbL is compatible with OSM and the Microsoft footprints. Each wave releases GeoPackage plus **OpenSidewalks v0.3** GeoJSON ([OpenSidewalks Schema](https://github.com/OpenSidewalks/OpenSidewalks-Schema)), validated with `python-osw-validation`:

- `sidewalks` become `highway=footway` + `footway=sidewalk` edges carrying `width`, `surface` and `incline`;
- curbs become `barrier=kerb` nodes with `kerb=raised|lowered|flush` ([OSM PWG Guide](https://wiki.openstreetmap.org/wiki/PWG_Guide));
- permanent obstructions become point features;
- Lebanese fields (clear width, operational width per window, obstruction class, permanence, occupied width, confidence, method) go under `ext:` keys.

Temporary occupation ships as a separate dated layer coded to the Warning 11866/2026 categories, so the dataset can evaluate enforcement. Blurred imagery goes back to Mapillary or a self-hosted Panoramax under CC BY-SA.

OSM is a slower and separate channel. Any bulk upload is an import that needs local community buy-in and an import-list review ([OSM Import Guidelines](https://wiki.openstreetmap.org/Import/Guidelines)). Agree the tagging choice with Lebanese mappers first: separate sidewalk ways or `sidewalk:left/right:*` tags, which an OSM tooling talk called "tricky and misleading" ([SotM 2022](https://2022.stateofthemap.org/attachments/JNJKYR_vestena_et_al_sotm2022_4FR9eti.pdf)). Contribute only reviewed, high-confidence permanent geometry through MapRoulette or Tasking Manager. Never overwrite existing OSM values automatically: a new value replaces an old tag only when they differ by more than about 0.5 m and the new value has two or more sequences behind it. Temporary obstructions never go into OSM.

## Conclusion

This plan changes where the accuracy work happens. Accuracy is not chosen by picking a model. It is manufactured on site through logged camera height, PPK positions and Lebanese labels, and it is proven on stations a person measured. Most of the decisive choices are cheap. A tape measure on the pole, a time-sampled frame extraction and an Apache-licensed detector cost almost nothing, while a misjudged height or an AGPL detector can invalidate the whole release. The budget follows the same logic: cameras and GPUs are under 10% of cost, so money spent on more benchmark faces, more reviewers or longer security windows buys more accuracy than any hardware upgrade.

Lebanon's sidewalk problem is also largely temporal and commercial, and 2026 provides a legal typology and an enforcement date to measure it against. A dated, per-window occupation layer coded to Warning 11866/2026 turns the inventory from a one-off map into a monitoring instrument. That matters more for Beirut's pedestrians than shaving another 5 cm off the width error. Three questions remain open and can be settled within the first six months rather than blocking the start: whether Beirut width error stays under 0.30 m on car-lined faces, whether curb height can be measured from imagery at all, and whether the Army will open LEB-CORS to a civilian programme.
