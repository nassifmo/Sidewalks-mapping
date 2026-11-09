# Detecting and localizing street/sidewalk objects from street-level imagery (poles, lights, signs, furniture, obstructions) — accuracy, localization, and a recommended approach for Beirut

Context being targeted: the current pipeline (Mask2Former Mapillary-Vistas semantic segmentation, connected components, single-view ground-contact inverse perspective mapping (IPM) with MoGe-2 depth, DBSCAN 1.5 m merge, nearest-transect sidewalk position) scores pole precision about 25% and recall about 10% in Washington DC, almost never detects street lights, and leaves 69% of Beirut objects with "unknown" position. The target is 80% or better precision and recall for fixed objects, 0.5–1 m or better position error, and correct on-sidewalk, curb-edge or off-sidewalk classification.

---

## 1. Detection: which detectors and segmenters reach high accuracy for poles, street furniture and Lebanon-specific classes, and what are their licences?

### Takeaway
The strongest recent evidence for street-furniture inventory is an **open-vocabulary detector (Grounding DINO) fine-tuned with LoRA on about 1.3–1.7k local panoramas**. It reached **74–80% mean precision and 81–84% mean recall over 11 classes**, with street lights at 63–85% precision and 88–90% recall. Older task-specific CNN pipelines hit **92–97% precision and recall for telegraph poles and traffic lights** when detection is combined with multi-view reasoning. Zero-shot open-vocabulary models are a good way to bootstrap Lebanon-specific classes (generators, vendor stalls, shop goods, motorcycles on the sidewalk), but they need local fine-tuning to reach the 80% target. Licences: Apache-2.0 options are Grounding DINO (original), RF-DETR N–L and OWLv2 (OWLv2 not verified here). SAM 3 uses a custom SAM License that allows commercial use. YOLO-World is GPL-3.0. DINO-X and Grounding DINO 1.5/1.6 Pro are accessed through a gated API.

### Cited Findings
**Fine-tuned open-vocabulary detection for roadside inventory (best recent numbers)**
- SVII-3D (arXiv 2601.10535, 2026) fine-tunes **Grounding DINO with LoRA** (applied to the query and value projections) on **1,746 panoramas (Wuhan) and 1,308 (Shanghai)** from a mobile mapping system covering 20.1 km and 21.8 km of road. It evaluates on 229 and 290 images. The 11 classes are traffic sign, street light, signal light, surveillance camera, barrier bollard, safety bollard, fire hydrant, trash bin, manhole, traffic cone and spherical bollard — [SVII-3D, arXiv HTML](https://arxiv.org/html/2601.10535)
- SVII-3D per-class precision/recall at IoU 0.5:

  | Class | Wuhan P | Wuhan R | Shanghai P | Shanghai R |
  |---|---|---|---|---|
  | Street light | 63.0 | 89.6 | 84.8 | 88.3 |
  | Traffic sign | 78.9 | 74.4 | 81.7 | 90.1 |
  | Bollards | 72–78 | 81–87 | 87–95 | 83–93 |
  | Trash bin | 86.8 | 88.1 | 79.8 | 74.9 |
  | Manhole | 67.0 | 71.6 | 59.9 | 69.1 |
  | **Mean** | **74.5** | **80.6** | **80.2** | **84.2** |

  — [SVII-3D](https://arxiv.org/html/2601.10535)
- SVII-3D's zero-shot Grounding DINO baseline was clearly worse than the LoRA-fine-tuned model. For example, localization error was 0.225 m zero-shot vs 0.118 m fine-tuned in Wuhan. No code or licence is released — [SVII-3D](https://arxiv.org/html/2601.10535)

**Classic CNN pipelines (single class, multi-view)**
- Krylov, Kenny & Dahyot (Remote Sensing 2018) used a segmentation FCN plus a monocular depth FCN on Google Street View (GSV) images (four 90° views of 640×640 px per location, captured every 5–10 m). Results:
  - Traffic lights, Regent St: **recall 0.940, precision 0.922** (47 TP, 4 FP, 3 FN)
  - Telegraph poles, Rathmines: **recall 0.935, precision 0.960**
  - Telegraph poles, County Mayo (120 km, 13,500 panoramas, 2,696 poles): **recall 0.926, precision 0.973**
  - Pole segmentation at pixel level: recall 0.936, precision 0.822. At object level within 25 m: recall 0.979, precision 0.927.

  — [Krylov et al. 2018 (ar5iv)](https://ar5iv.arxiv.org/html/1708.08417)
- Zhang et al. (Sensors 2018) detected utility poles with crossarms in GSV using RetinaNet: **AP of about 0.78** at IoU > 0.3 on 500 test images (937 objects) — [Zhang et al. 2018, MDPI](https://mdpi.com/1424-8220/18/8/2484); [DOAJ record](https://doaj.org/article/57905c55ee274155a8b52f5213b9db8c)
- Ahmad & Krylov (EUSIPCO 2024) trained a ResNet-34 image classifier with Grad-CAM and watershed localization, using only binary presence labels:
  - Traffic lights from Vistas: instance precision 92.4%, recall 78.0%, detection rate 79.4%, vs Mask R-CNN at 83.0%, 83.7% and 81.4%.
  - Public bins in Dublin: 65% precision and 92% recall.
  - **Confusers responsible for more than 2/3 of bin false positives: bollards, street-light bases and cabinets.**

  — [Ahmad & Krylov, EUSIPCO 2024](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000641.pdf)
- A hybrid YOLOv5x and triangulation streetlight pipeline in Hong Kong reported about **90% detection accuracy**. This figure comes from a search-result summary; the full text was not read — [Renewable Energy 2025, ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0960148125026151)

**Open-vocabulary models and licences**
- **SAM 3** (Meta) does promptable concept segmentation from text, exemplar or visual prompts:
  - **848M parameters**; a detector and a tracker share one vision encoder.
  - Reaches 75–80% of human performance on the SA-Co benchmark (270K concepts).
  - Released under the **SAM License**. SAM 3.1 "Object Multiplex" was released 27 Mar 2026.
  - Requires Python 3.12+, PyTorch 2.7+ and CUDA 12.6+.

  — [facebookresearch/sam3 GitHub](https://github.com/facebookresearch/sam3)
- The SAM License is a custom licence, not an OSI licence, unlike SAM and SAM 2 (Apache-2.0). It is royalty-free and allows commercial use. Redistribution must include the licence; military, weapons and ITAR uses are excluded; Meta may change the terms. SAM 3 is listed at 47.0 mask AP zero-shot on LVIS — [Roboflow SAM 3 licence page](https://roboflow.com/model-licenses/segment-anything-3); [HF LICENSE](https://huggingface.co/facebook/sam3/blob/main/LICENSE); [Roboflow best free CV models](https://blog.roboflow.com/best-free-computer-vision-models/)
- **RF-DETR**: Nano through Large models and code are **Apache-2.0**. The XL and 2XL checkpoints use the "Platform Model License 1.0" — [Roboflow: RF-DETR is free to use commercially](https://blog.roboflow.com/rf-detr-is-free-to-use-commercially/)
- **YOLO-World** is listed as **GPL-3.0** (copyleft); the original **Grounding DINO** is listed as **Apache-2.0**. Both come from a vendor comparison page — [Roboflow RF-DETR vs YOLO-World](https://playground.roboflow.com/models/compare/rf-detr-vs-yolo-world); [Grounding DINO vs RF-DETR](https://playground.roboflow.com/models/compare/grounding-dino-vs-rf-detr)
- **DINO-X Pro** (IDEA Research, 2024):
  - 56.0 AP on COCO zero-shot, 59.8 on LVIS-minival, 52.4 on LVIS-val.
  - **Rare classes: 63.3 AP on LVIS-minival and 56.5 AP on LVIS-val**, which is +5.8 and +5.0 AP over Grounding DINO 1.6 Pro and +7.2 and +11.9 AP over 1.5 Pro.
  - Same architecture as Grounding DINO 1.5, trained on 100M grounding samples.

  — [DINO-X paper](https://arxiv.org/html/2411.14347v3); [HF papers](https://huggingface.co/papers/2411.14347)
- DINO-X is used through the `dds-cloudapi-sdk`, with an API token obtained by application. The V1 API is deprecated — [IDEA-Research/dino-x-api](https://github.com/idea-research/dino-x-api)
- VLMs consistently struggle with fine-grained traffic-sign category discrimination on the Mapillary Vistas Validation (MVV) set (ICCV 2025 workshop) — [Garg et al., ICCVW 2025](https://openaccess.thecvf.com/content/ICCV2025W/DataCV/papers/Garg_Mapillary_Vistas_Validation_for_Fine-Grained_Traffic_Signs_A_Benchmark_Revealing_ICCVW_2025_paper.pdf)
- The Mapillary Traffic Sign Dataset is a global dataset for sign detection and classification — [Ertler et al., arXiv 1909.04422](https://arxiv.org/pdf/1909.04422)

### Inferences
- **Likely cause of "street lights almost never detected" (inference):**
  - In the Vistas taxonomy the *street-light* class covers the luminaire head, while the post is a separate *support--pole* class (see also the separate Mapillary point classes `object--street-light`, `object--support--pole` and `object--support--utility-pole` in section 3).
  - A connected component of the lamp head has no ground contact, so ground-plane IPM projects it far away or rejects it.
  - Likewise, pole components are thin. They get fragmented by occluders (parked cars, motorcycles), merge with adjacent poles or signs, and their base is often hidden. This fits the low pole recall (10%).
  - Fix: detect **instances** (boxes or masks) rather than semantic connected components. Associate the lamp head with its supporting pole instance, and localize by triangulating the vertical axis of the pole rather than relying on a visible base.
- A **fine-tuned instance detector or segmenter** is the realistic route to 80% or better. SVII-3D shows that about 1.3–1.7k labelled panoramas per city give a mean of about 80% P/R across 11 classes. Krylov shows that per-class models plus multi-view reasoning give more than 92%. Zero-shot use is a bootstrap step, not the end state.
- Candidate stack under the permissive-licence constraint:
  - Labelling: SAM 3 (text prompts such as "electric generator", "street vendor cart", "parked motorcycle on sidewalk") to auto-propose masks, then human correction.
  - Training: RF-DETR (Apache-2.0, N–L sizes) or LoRA-tuned Grounding DINO (Apache-2.0) as the production detector.
  - Avoid Ultralytics or YOLO-World (GPL/AGPL) if a closed or commercial deployment is possible.
  - DINO-X is cloud and API only, so it is unsuitable for bulk processing without a budget.
- 8 GB GPU (inference): SAM 3 at 848M parameters is roughly 1.7 GB of weights in fp16 (arithmetic), so inference on one image at a time should fit in 8 GB. RF-DETR N–L and Grounding DINO Swin-T are lighter. LoRA fine-tuning of Grounding DINO on 8 GB is plausible with small batches, but no source confirms it.
- **Beirut confusers to include as hard negatives:** cabinets, street-light bases and bollards were the main false positives for bins in Dublin (Ahmad & Krylov). Beirut adds generator housings, AC units, shop displays and informal fences.

### Gaps
- No per-class Mask2Former or OneFormer Mapillary-Vistas IoU or AP for "pole", "street light" or "utility pole" was retrieved. The likely low IoU for thin classes is unquantified.
- No published zero-shot AP for OWLv2, Florence-2, YOLO-World or SAM 3 on street-furniture classes specifically.
- OWLv2 (believed Apache-2.0) and Florence-2 (believed MIT) licences, Grounding DINO 1.5/1.6 weight availability, and Ultralytics AGPL-3.0 were not verified against primary sources in this session.
- No source reports detectors trained or evaluated on Lebanese or other Middle-East street imagery, or on classes such as generators, vendor stalls or shop goods.

---

## 2. Localization: multi-view triangulation vs monocular depth, and reported errors in metres

### Takeaway
**Single-view monocular-depth localization is several times worse than multi-view triangulation.**
- Krylov: depth-only gives a mean error of 3.2 m (95% CI 6.8 m) vs **0.98 m (95% CI 2.07 m)** with MRF triangulation.
- A 2025 benchmark of Depth Anything, UniDepth, Depth Pro and Metric3D on Mapillary/Cyclomedia signs found mean errors of **4.4–7.3 m**, with depth MAE of 1.3–1.7 m below 5 m and more than 11 m beyond 20 m.
- Decimeter accuracy (0.12–0.14 m) has been shown only with survey-grade mobile-mapping poses plus learned cross-view association and ray triangulation.
- With crowdsourced phone imagery, **camera GPS error (mean 5.5 m measured on Mapillary) dominates**. Camera poses must be corrected, for example with SfM, before 0.5–1 m is achievable.

### Cited Findings
- **Krylov et al. 2018**:
  - Positional error on 41 telegraph poles: **MRF triangulation mean 0.98 m, median 1.04 m, 95% CI 2.07 m**, vs **depth-FCN only: mean 3.2 m, median 2.9 m, 95% CI 6.8 m**.
  - Depth is unreliable beyond 25 m, so farther objects are excluded.
  - In 35% of pole scenes in County Mayo, visual-matching triangulation fails because identical poles appear together. The MRF instead resolves ray intersections using depth-consistency, false-positive and single-occupancy energy terms.
  - Camera GPS noise is the main remaining error. The result is comparable to a single-frequency GPS receiver (95% about 1.89 m).

  — [Krylov et al. 2018](https://ar5iv.arxiv.org/html/1708.08417); [arXiv PDF](https://arxiv.org/pdf/1708.08417)
- **SVII-3D (2026)**:
  - Mean localization error for correctly localized objects: **0.118 m (Wuhan) and 0.137 m (Shanghai)**.
  - Baselines: local-association chaining 0.144 and 0.160 m; zero-shot Grounding DINO 0.225 and 0.234 m.
  - Association uses a spatial-attention transformer that sees only geometry (exposure position, viewing direction, 2D box size, category; **appearance discarded**). It then applies Hungarian matching, energy-minimized ray triangulation (BFGS), and geometry-guided split/merge.
  - The imagery comes from a mobile mapping system (high-accuracy poses).

  — [SVII-3D](https://arxiv.org/html/2601.10535)
- **MapAnything / monocular metric-depth benchmark (arXiv 2509.14839, 2025)**:
  - Depth MAE against LiDAR, overall: Metric3D-ViT 5.6 m, UniDepth-B 5.7 m, Depth Anything-B 9.0 m, Depth Pro 13.7–16.3 m.
  - By range: **below 5 m: 1.3–2.9 m; 5–10 m: 1.4–4.3 m; 10–20 m: 3.5–15.5 m; above 20 m: 11–32 m**.
  - Traffic-sign location error: UniDepth-B 4.4 m (Cyclomedia) and 5.7 m (Mapillary); Depth Pro 4.8 and 6.0 m; Metric3D 7.3 and 6.6 m.
  - UniDepth found 87% of expected signs with Cyclomedia (225/258) but only **59% with Mapillary** (51/86). Mapillary covered about 28% of streets vs 100% for Cyclomedia.
  - **Mapillary camera coordinates deviated a mean 5.5 m** on 12 measured images.
  - Recommendations: use only within about 20 m; remove duplicates within 3 m; match within 10 m. MoGe was not evaluated.

  — [arXiv 2509.14839 HTML](https://arxiv.org/html/2509.14839v3)
- **Zhang et al. 2018** (utility poles, GSV, brute-force line-of-bearing): only **2.6% of poles within 1 m**, 47% within 5 m and 79% within 10 m — [Zhang et al., Sensors 2018](https://mdpi.com/1424-8220/18/8/2484)
- **Ahmad & Krylov 2024** (bins, Dublin, survey imagery every about 3 m with 6 views): found 63 of 82 recorded bins, at a mean distance of **5.45 m** from the city records. On manual GSV check, the MRF location was more accurate in 40 cases and the city record in 22. The method also found 43 genuine bins missing from the records, with 46 false positives — [EUSIPCO 2024](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000641.pdf)
- **Hong Kong streetlights** (YOLOv5x plus triangulation): 93% localized within 2 m; mean error of 1.43, 1.66 and 1.99 m at 3, 5 and 10 m range. These figures come from a search snippet; the full text was not read — [ScienceDirect 2025](https://www.sciencedirect.com/science/article/abs/pii/S0960148125026151)
- **Nassar, Lefèvre & Wegner**:
  - ICCV 2019: learned geometric soft constraints for multi-view instance detection, with a geo-coded tree re-ID dataset.
  - ISPRS IJGI 2020: Siamese CNN with camera metadata.
  - ECCV 2020 (GeoGraph): a GNN that takes images and approximate poses and outputs detections, re-ID and geo-positions. It reports 2–6% AP gains and about 8× faster training.
  - The 2019 paper reportedly gives mean errors of **about 3.13 m (Pasadena trees) and 4.36 m (Mapillary signs)**, but that figure comes from a secondary summary, not verified.

  — [ICCV 2019 paper](https://openaccess.thecvf.com/content_ICCV_2019/papers/Nassar_Simultaneous_Multi-View_Instance_Detection_With_Learned_Geometric_Soft-Constraints_ICCV_2019_paper.pdf); [GeoGraph ECCV 2020](https://www.ecva.net/papers/eccv_2020/papers_ECCV/html/292_ECCV_2020_paper.php); [IJGI 2020](https://mdpi.com/2220-9964/9/11/687)
- **Stochastic birth-and-death street-furniture geolocation** (Murphy, Krylov et al., IMVIP 2025): uses geopositioned energy maps that can include GIS priors (road maps, placement constraints), tested on a simulation informed by Dublin street-lighting records. Code is planned at GitHub EMurphy0108/SBD_Street_Furniture — [arXiv 2509.10310](https://arxiv.org/pdf/2509.10310)
- The Mapillary-image pipeline in Berlin found traffic-light positions only "roughly estimated" and attributed part of the error to the **lack of camera intrinsics in Mapillary EXIF** — [Automated detecting and placing road objects, arXiv 1909.05621](https://arxiv.org/pdf/1909.05621); [Springer version](https://link.springer.com/article/10.1007/s43762-021-00019-6)

### Inferences
- Single-view IPM with monocular depth (the current method) is bounded at roughly 1–3 m error even at short range, and is much worse beyond 10–20 m. On top of that comes the camera-pose error (several metres for phone or Mapillary GPS). A DBSCAN eps of 1.5 m then splits one object into several clusters (lower precision) or merges neighbours. This is consistent with the observed 25% pole precision.
- **To reach 0.5–1 m:**
  1. **Correct camera poses first**: SfM or bundle adjustment over each sequence (e.g., Mapillary's SfM-computed positions and headings, or a local COLMAP/OpenSfM run), anchored to imagery or road geometry.
  2. **Triangulate rays** from 3 or more views per object, using the bearing of the object's vertical axis, which needs no visible base.
  3. Use **depth only as a soft prior** (Krylov-style MRF or SVII-3D-style energy minimization) and only within 20 m.
  4. Associate views by **geometry, not appearance**: poles look identical to each other.
  5. Add **priors that poles and lights sit near the curb line**, in the style of the birth-and-death energy maps.
- Expected error budget with corrected poses and 3+ views at 5–15 m range is about 0.5–1 m, based on Krylov's 0.98 m with GSV poses. The 0.1 m results need survey-grade poses, so they are not expected for Beirut crowdsourced imagery.

### Gaps
- No direct evaluation of MoGe-2 for object geolocation was found.
- GeoGraph's own geolocation error (m) was not retrieved.
- No study quantifies the localization gain from SfM-refined Mapillary poses vs raw GPS.

---

## 3. Mapillary API v4 map_features and detections as a free source: classes, accuracy, Beirut coverage

### Takeaway
Mapillary map features are free, triangulated point objects. They include **street-light, pole, utility-pole, bench, trash-can, junction-box (cabinet), phone-booth, fire-hydrant, bike-rack, CCTV, signs and traffic lights**, plus about 1,500 traffic-sign classes. There are **no classes for trees, bollards, parked vehicles, generators or stalls**. No published accuracy benchmark exists; position accuracy depends on contributor GPS and capture density. Beirut coverage exists (2019–2023 sequences are mentioned) but is uneven and must be queried directly. Use map features as a prior or candidate source and a benchmark comparison, not as ground truth.

### Cited Findings
- **Point map-feature classes (27)**:
  - Signage: `object--banner`, `object--sign--advertisement`, `object--sign--information`, `object--sign--store`
  - Poles and lights: `object--street-light`, `object--support--pole`, `object--support--traffic-sign-frame`, `object--support--utility-pole`
  - Street furniture: `object--bench`, `object--bike-rack`, `object--cctv-camera`, `object--fire-hydrant`, `object--junction-box`, `object--mailbox`, `object--parking-meter`, `object--phone-booth`, `object--traffic-cone`, `object--trash-can`
  - Ground fixtures: `object--catch-basin`, `object--manhole`, `object--water-valve`
  - Traffic lights: `object--traffic-light--*` (6 variants)

  — [Mapillary API docs, points](https://www.mapillary.com/developer/api-documentation/points)
- The detection vocabulary has about 150 classes, of which a subset generates map features (point features and traffic signs). Help pages give 40 or 42 point features and "1,500+" traffic-sign classes; the counts are inconsistent across pages — [Mapillary help: types of map data](https://help.mapillary.com/hc/en-us/articles/360003021152-Types-of-map-data); [What is an object detection?](https://help.mapillary.com/hc/en-us/articles/115000967191); [42 new point features blog 2019](https://blog.mapillary.com/update/2019/01/23/updating-maps-with-cameras-42-new-point-features.html)
- **Accuracy**: Mapillary states that map-feature position accuracy is influenced by the accuracy of image locations (device GPS), and that more images give more points to triangulate. No quantitative benchmark is published — [Mapillary help: exploring object detections](https://help.mapillary.com/hc/en-us/articles/360003021312-Exploring-object-detections); [Mapillary API FAQ](https://mapillary.com/developer/api-documentation/faq)
- **Access**:
  - The `map_features` endpoint takes fields such as `id`, `object_value` and `geometry`, with a `bbox` filter.
  - Detections can be fetched per image ID or per map-feature ID.

  — [Mapillary API FAQ](https://mapillary.com/developer/api-documentation/faq); [Getting started with API v4](https://blog.mapillary.com/update/2021/06/23/getting-started-with-the-new-mapillary-api-v4.html); [Map data via API blog](https://blog.mapillary.com/update/2020/08/28/map-data-mapillary-api.html)
- Community input: Mapillary used community verification to improve recognition — [Mapillary blog 2020](https://blog.mapillary.com/update/2020/06/09/improving-object-recognition-with-communitys-input.html)
- Forum reports from 2021–2024 note limited or no detections on older imagery and missing detection types after the v4 transition — [Mapillary forum: limited detections in older imagery](https://forum.mapillary.com/t/limited-no-detections-available-in-older-imagery/6163); [API v4 timeline thread](https://forum.mapillary.com/t/mapillary-api-v4-timeline-what-is-going-on/4936)
- Independent evidence on Mapillary-based placement (via third-party pipelines on Mapillary imagery, not Mapillary's own map features):
  - Mean camera GPS deviation is 5.5 m.
  - Signs localized from Mapillary had 5.7–6.6 m mean error, with 59% of expected signs found.
  - Berlin traffic lights from Mapillary imagery were "roughly estimated", with no official ground truth available.

  — [arXiv 2509.14839](https://arxiv.org/html/2509.14839v3); [arXiv 1909.05621](https://arxiv.org/pdf/1909.05621)
- Mapillary imagery has been used to source training images for objects, e.g. public bins via image flags, matched within 15 m of city bin records — [Ahmad & Krylov 2024](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000641.pdf)
- **Beirut coverage**: the OSM wiki Lebanon page links Mapillary imagery from a Lebanon drive and a Beirut set dated May 2019. An unofficial blog lists Beirut coverage dates from May 2021 to Apr 2023 (low reliability). Coverage depends on community contributions — [OSM wiki Lebanon](https://wiki.openstreetmap.org/wiki/Lebanon); [unofficial coverage blog](https://muziyemi.blogspot.com/p/low-quality-coverage.html); [atlas.co Mapillary overview](https://atlas.co/data-sources/mapillary/)

### Inferences
- **Practical use**: pull `map_features` for the Beirut bbox (roughly 35.46–35.54 E, 33.86–33.91 N) for the street-light, pole, utility-pole, junction-box, trash-can, bench and sign classes. Compare them with the team's own triangulated objects.
  - Where both agree within about 2 m, treat as high-confidence.
  - Mapillary-only points become candidates to re-check in imagery.
  - Mapillary's per-feature detections (image ID plus mask) can serve as extra rays for the team's own triangulation.
- Mapillary classes do not cover the Beirut-specific obstructions (vehicles and motorcycles on the sidewalk, generators, stalls, goods, trees, bollards). Those need the team's own detector.
- Because Mapillary feature positions inherit contributor GPS error (likely several metres), they are insufficient alone for curb-relative placement at 0.5–1 m.

### Gaps
- No published precision, recall or positional error for Mapillary map features against an official inventory was found, for any city.
- The current count of Beirut images or map features, and capture dates, were not retrieved. A direct API or coverage-tile query is required.
- Whether v4 exposes SfM-refined image positions (e.g., `computed_geometry`) and how accurate they are in Beirut was not verified in this session.

---

## 4. Computing object position relative to curb and building line, and clear walkable width (PROWAG/ADA, obstruction definitions)

### Takeaway
US guidance (PROWAG) defines the **pedestrian access route as a 1.2 m (4 ft) minimum continuous clear width excluding the curb**, which street furniture must not reduce. It also limits **protrusions to 100 mm (4 in) for objects between 685 and 2,030 mm (27–80 in) above the surface**. Project Sidewalk's experience is that whether an object is an "obstacle" depends on spatial context (is it actually in the path?), which classifiers struggle with from imagery alone (obstacle precision 51–68%). Clear width should therefore be computed geometrically: the object footprint is placed in a continuous sidewalk polygon split into curb edge and building edge, rather than inferred by a classifier or a sparse transect.

### Cited Findings
- **Clear width**: the continuous clear width of pedestrian access routes, exclusive of the curb, is **1.2 m (4 ft) minimum**, or **1.5 m (5 ft) at medians and refuge islands**. Street furniture and other objects shall not reduce the required clear width. This is from the proposed-rule preamble; the final-rule wording was not retrieved — [US Access Board PROWAG preamble](https://www.access-board.gov/prowag/preamble.html); [shared-use preamble](https://www.access-board.gov/prowag/proposed/preamble-shared-use/)
- **Protruding objects**: objects between 27 and 80 in (685–2,030 mm) above the walking surface may protrude at most 4 in (100 mm) into the circulation path. Objects at or below 27 in may extend into the area provided the remaining width complies.
  - A protruding object is "any obstacle that reduces the clearance width and/or the clearance height within a pedestrian area", and the pedestrian area is not limited to the designed route.

  — [US Access Board ADA guide ch.3 protruding objects](https://www.access-board.gov/ada/guides/chapter-3-protruding-objects); [Iowa DOT SUDAS 12A-3](https://iowadot.gov/design-manual/chapter-12-pedestrian-and-bicycle-facilities/12a-3-protruding-objects-sudas)
- Local standards are stricter: NYC requires pedestrian access routes of at least 5 ft, with greater clear paths on most corridors — [NYC Street Design Manual](https://www.nycstreetdesign.info/geometry/accessibility-pedestrian-mobility-plan-pedestrian-access-routes); [Broward MPO PROWAG training](https://www.browardmpo.org/images/CSMP/BMPO_ADA_Transition_Plan_Training_1_TP_Roadmap_PROWAG_FINAL-accessible.pdf)
- A Street View–based study converted images to land-cover maps to measure sidewalk clear width. In Washington DC, most sidewalks met the 0.9 m minimum but 20% exceeded slope limits. This comes from a search summary — [ScienceDirect via search: Developing sidewalk inventory data using street view images](https://www.researchgate.net/publication/351465518_Developing_Sidewalk_Inventory_Data_Using_Street_View_Images)
- Project Sidewalk on obstacles:
  - Obstacles "require spatial contextualization (i.e., is the object actually blocking the path?), which is often difficult to assess with only panoramic imagery."
  - Common errors include labelling features that are not on a sidewalk as obstacles.
  - About 25% of false negatives for the other classes involved an obstacle blocking the view.

  — [Duan et al., ASSETS 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- Aerial or orthophoto sidewalk models capture the paved extent but miss objects on the sidewalk, such as barriers or low branches (secondary source) — [ArchUp](https://archup.net/pedestrian-sidewalk-barriers/)
- Energy-map priors from GIS layers (road maps, placement constraints) can be fused into street-furniture geolocation — [arXiv 2509.10310](https://arxiv.org/pdf/2509.10310)

### Inferences
- **Fixing the 69% "unknown position" in Beirut (inference):**
  1. Replace nearest-transect lookup with a **continuous sidewalk polygon**, from Tile2Net, OSM or own segmentation, whose boundary is labelled as *curb edge* (adjacent to roadway) or *frontage/building edge*.
  2. For each localized object point (or footprint polygon, e.g., a 0.3 m disc for a pole or the projected mask for a car or stall), compute:
     - the signed perpendicular distance to the curb-edge line
     - the distance to the building-edge line
     - the local sidewalk width, measured along the normal through the object
  3. Then:
     - remaining clear width = max(curb-side gap, building-side gap)
     - "on sidewalk" if the footprint intersects the polygon
     - "curb edge" if the distance to the curb is under about 0.6 m (furniture zone)
     - "off sidewalk" otherwise, with a buffer equal to the 1σ localization error
  4. Report "uncertain" when the localization error ellipse straddles a boundary.
- With localization error of about 1 m, curb-edge vs mid-sidewalk classification is only reliable for sidewalks wider than about 2–3 m. On narrow Beirut sidewalks, **image-space reasoning** helps: test whether the object's ground-contact pixels lie on "sidewalk" vs "curb" vs "road" pixels in the same image's segmentation. It is more robust than metric projection because it is error-free relative to the local curb, and can be combined with the metric estimate.
- Obstruction class should follow the PROWAG height bands:
  - Ground-level objects (cars, motorcycles, goods, generators) reduce width directly.
  - Wall-mounted objects at 685–2,030 mm count only if they protrude more than 100 mm.
  - Overhead objects below 2,030 mm (80 in) reduce headroom.
  - The **1.2 m clear-width threshold** (1.5 m preferred) is a defensible benchmark for Beirut in the absence of a Lebanese standard.

### Gaps
- The PROWAG final-rule (2023) text and its 1.2 m / passing-space wording were not retrieved directly. The OpenSidewalks schema and its obstruction or width attributes were not researched in this session.
- No paper was found that measures remaining clear width around individual detected obstacles from street-level imagery with reported metric error.
- No Lebanese or Beirut sidewalk width standard was found.

---

## 5. Datasets for sidewalk obstacles and how many local labels are needed to fine-tune to a new city

### Takeaway
Project Sidewalk offers more than 700,000 image labels and 400,000 validations across 10 cities. These are point labels on GSV, used for classification, not instance masks. Obstacle classifiers trained on them reach only **51–68% precision and 61–82% recall**, and they degrade when transferred to a non-US city (terraced sidewalks in San Pedro Garza García, Mexico). Fine-tuning evidence suggests **on the order of 1.3–1.7k labelled panoramas per city** for an 11-class detector at about 80% P/R (SVII-3D). Small local fine-tuning sets also recover 76–81% precision and 83–90% recall for Project Sidewalk classes (Weld 2019). Beirut-specific classes need local labelling, ideally bootstrapped with SAM 3 or Grounding DINO proposals.

### Cited Findings
- Project Sidewalk's open dataset has more than **700,000 image-based labels and 400,000 validations across 10 cities**. Its classes are curb ramp, missing curb ramp, obstacle and surface problem — [Duan et al., ASSETS 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf); [Project Sidewalk](https://makeabilitylab.cs.washington.edu/project/sidewalk/)
- **Duan et al. 2022** trained HRNet-W48 binary classifiers on crops, starting from CitySurfaces weights:
  - **Obstacle precision 53.0% (Seattle), 68.1% (SPGG, Mexico), 57.0% (Columbus)**; recall 77.4%, 60.8% and 73.7%.
  - For comparison, curb-ramp precision was 79.6–89.1%.
  - Training only on validated labels did not uniformly help. In SPGG, 53,361 obstacle labels shrank to 5,764 validated ones (10.8%).
  - Excluding the target city reduced performance across all types, e.g. terraced sidewalks in SPGG were missed by models trained on US cities.

  — [Duan et al., ASSETS 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **Weld et al., ASSETS 2019** (ResNet-18 on Project Sidewalk DC labels; best student paper), via a secondary review:
  - Auto-validation: about 81.3% precision and 77.2% recall on average.
  - Auto-labelling of unlabelled panoramas: 47.0% precision and 41.2% recall overall, comparable to crowdworkers (37% / 46%).
  - **Pre-training on DC and fine-tuning on small Seattle or Newberg sets gave about 76–81% precision and 83–90% recall.**

  — [a11y-paradise review of Weld et al.](https://a11y-paradise.onrender.com/reviews/69bc12412846a9204f821b87); [Makeability Lab news](https://makeabilitylab.cs.washington.edu/news/deep-learning-for-sidewalk-accessibility-awarded-best-student-paper-at-assets19); [talk slides](https://makeabilitylab.cs.washington.edu/media/talks/Weld_DeepLearningForAutomaticallyDetectingSidewalkAccessibilityProblemsUsingStreetscapeImagery_2019.pdf)
- Project Sidewalk's 2021 CV repo revisits the approach to integrate into the validation interface — [ProjectSidewalk/sidewalk-cv-2021](https://github.com/ProjectSidewalk/sidewalk-cv-2021)
- RampNet (2025) bootstraps curb-ramp detection from open government metadata in a two-stage pipeline. It is an example of using existing inventories to auto-generate training labels — [RampNet arXiv 2508.09415](https://arxiv.org/pdf/2508.09415)
- Label budget for a multi-class street-furniture detector: about **1,746 or 1,308 panoramas per city** reached a mean of 74.5–80.2% precision and 80.6–84.2% recall (SVII-3D) — [SVII-3D](https://arxiv.org/html/2601.10535)
- Weak supervision with existing records:
  - A binary image-level classifier with Grad-CAM, trained on 9,827 positive Mapillary images near city bin records, found 63 of 82 bins plus 43 unrecorded ones.
  - Classification tolerates 10% label noise with only a few points' drop.

  — [Ahmad & Krylov 2024](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000641.pdf)
- Large-scale roadside facility detection has been trained on Mapillary data — [ResearchGate: Roadside facility detection model based on Mapillary dataset](https://www.researchgate.net/publication/366416809_Development_of_a_Large-Scale_Roadside_Facility_Detection_Model_Based_on_the_Mapillary_Dataset)

### Inferences
- **Label budget estimate for Beirut (inference):**
  - About 1,000–2,000 labelled images (instance boxes or masks) covering about 15–20 classes, with at least 200–300 instances per rare class (generators, stalls, goods, bollards), should be enough to fine-tune a pre-trained open-vocabulary or Vistas detector to about 80% P/R. This follows SVII-3D's 1.3–1.7k panoramas for 11 classes.
  - To minimize human work: run SAM 3 or Grounding DINO with text prompts to pre-label, correct them, and use active learning (label the frames with most disagreement).
  - Also use DC's official inventories, and Mapillary map features in Beirut, as weak or automatic labels, as Ahmad & Krylov and RampNet did.
- Project Sidewalk labels are useful for DC benchmarking but are weak for training a Beirut obstacle detector: they are points, US-centric, and give low obstacle precision.

#### Recommended approach (synthesis; inference from the findings above)
1. **Detector**:
   - Replace semantic connected components with an instance detector or segmenter.
   - Start with SAM 3 or Grounding DINO zero-shot proposals for the full class list. Hand-correct about 1–2k Beirut frames plus DC frames.
   - Fine-tune RF-DETR (Apache-2.0, fits 8 GB) or LoRA Grounding DINO (Apache-2.0).
   - Treat street light as luminaire plus pole, and add hard negatives (cabinets, bases, bollards, AC units).
2. **Poses**: SfM-refine camera positions and headings per sequence (Mapillary computed poses or own OpenSfM/COLMAP run). Without this, GPS error of about 5 m swamps everything.
3. **Multi-view localization**:
   - Associate detections across 3 or more frames with geometry-only matching (rays plus box size plus class, as in SVII-3D).
   - Triangulate the pole axis or object centre by ray least-squares or MRF.
   - Use MoGe-2 or UniDepth depth only as a prior within 20 m.
   - Use single-view IPM only as a fallback, flagged low confidence.
   - Merge with a class-aware radius tied to estimated covariance, not a fixed 1.5 m.
4. **Sidewalk placement**:
   - Compute curb and building offsets and clear width against a continuous sidewalk polygon with labelled edges.
   - Cross-check with image-space "ground contact on sidewalk, curb or road" pixels.
   - Apply the PROWAG 1.2 m clear-width and 27–80 in / 4 in protrusion rules.
5. **Free priors and benchmarking**: ingest Mapillary map features (street-light, pole, utility-pole, junction-box, trash-can, bench) as candidates and as a sanity check. In DC, report per-class P/R at 2 m and 5 m match radii, plus median error.

### Gaps
- Obstacle-specific numbers from Weld 2019 were not retrieved; the figures above come from a secondary review site.
- No public instance-level dataset of sidewalk obstacles with masks was confirmed in this session. SideSeeing, OpenSurfaces and other sidewalk-obstacle datasets were not researched due to the tool budget.
- No study directly measures fine-tuning label budget vs accuracy curves for street furniture in a new city.
