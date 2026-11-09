# ML / Computer-Vision Pipeline Engineering: Street-Level Imagery to Mapped Sidewalk Attributes (Lebanon)

Scope note: These notes cover how to build each stage of the pipeline: 360° handling, geometry and scale, detection and segmentation training, surface condition, compute and cost, map fusion, and accuracy. The research budget was 17 tool calls, so some sub-questions are only partly sourced. Anything without an inline citation sits under Inferences (engineering judgement) or Gaps. It is not presented as fact.

---

## 1. 360° handling: equirectangular to perspective crops

### Takeaway
Reproject equirectangular panoramas into pinhole perspective crops before running models trained on pinhole data (Cityscapes, Mapillary Vistas, COCO). For sidewalks, keep only the side-facing and lower, ground-facing views. One recent pipeline uses only the bottom half of each panorama and gives each crop a compass angle rotated by its yaw. The best-validated width method (UrbanVGGT) was built on 90° FOV, 640×640 pinhole crops, so 90° crops are the safest choice for transferring published accuracy.

### Cited Findings
- UrbanVGGT used Google Street View images at 640×640 px with a 90° field of view. Its ablation showed that a "pinhole only" variant degraded MAE to 1.096 m, against 0.252 m for the full pipeline. That 1.096 m figure belongs to the camera-model ablation inside their pipeline, not to crop geometry. — [UrbanVGGT, arXiv 2603.22531](https://arxiv.org/html/2603.22531v1)
- UrbanVGGT measured width within a **central band** of the image rather than across its full width. Using the full width raised MAE from 0.252 to 0.265 m and cut the share within 0.50 m from 95.5% to 88.5%. Edge-of-crop pixels are less reliable. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- A TU Delft pipeline reprojects panoramas into perspective crops and then segments them (binary sidewalk masks with DINOv3). Each crop inherits the panorama's GPS position but gets a compass angle rotated by its relative yaw. Only the bottom half of each image is used, because the upper half is mostly sky and facades. This comes from a search-result summary; I did not read the full document. — [TU Delft repository](https://repository.tudelft.nl/file/File_8c22a933-e468-4cb9-a69e-dad11b7d050a)
- A citizen-science toolkit cuts 4:3 sub-images from Mapillary panoramas to avoid "distorted and overly large raw panoramic images". Mapillary panoramas are generally normalised so the left edge points north. — [arXiv 2403.00174](https://arxiv.org/pdf/2403.00174)
- Mapillary notes that in equirectangular images the distortion comes from the representation itself, whereas perspective and fisheye distortion is radial. — [Mapillary blog, polygon triangulation on the sphere](https://blog.mapillary.com/update/2019/06/11/polygon-triangulation.html)
- Domain-adaptation research finds that equirectangular panoramic layout differs from standard pinhole data, which lowers accuracy for models trained on pinhole images. — [arXiv 2207.11860](https://arxiv.org/pdf/2207.11860.pdf)

### Inferences
- **Suggested crop set per panorama** (engineering recommendation). Two side crops at yaw ±90° relative to travel direction, FOV 90°, pitch −15° to −25° (tilted down so the curb, sidewalk and building base fill the frame). Optionally add two oblique crops at ±45° and ±135° for obstruction detection and multi-view triangulation. Skip forward/back crops for width; they look along the sidewalk, where width is foreshortened. Use ~1024×1024 per crop for Mask2Former and match UrbanVGGT's 640×640 at 90° when reusing its calibration. If needed, tilt the virtual camera's principal axis rather than its horizon, and record the virtual intrinsics (f = W / (2·tan(FOV/2))) and rotation, so every crop is an exact pinhole camera sharing the panorama's optical centre. That makes crops directly usable in SfM and triangulation.
- py360convert (e2p, e2c) and Equirec2Perspec do this reprojection. I did not verify their licences in this session (see Gaps).
- Mapillary panorama "compass angle" plus the north-left convention gives the absolute yaw of each crop. Where the sequence is reconstructed in SfM (Section 2), refine it with the SfM rotation; compass angles from phones are noisy.
- Cubemaps (six 90° faces) are convenient but split sidewalks at face seams. Custom-yaw crops centred on the side directions are better for width measurement.

### Gaps
- I could not verify the licences of py360convert or Equirec2Perspec. Check each repo's LICENSE file.
- I found no published ablation comparing crop FOV/pitch choices for sidewalk segmentation accuracy specifically.

---

## 2. Multi-view geometry: SfM, metric scale, ground plane, curb/building lines, object triangulation and deduplication

### Takeaway
Two complementary routes work:
- **Single-image feed-forward 3D plus a camera-height scale.** UrbanVGGT reports MAE 0.252 m and 95.5% within 0.5 m in DC.
- **Multi-frame sequence reconstruction** with VGGT (exports to COLMAP with optional BA), COLMAP/GLOMAP or OpenSfM, with GNSS as a scale/georeference prior.

Point objects (poles, generators, kiosks) should be triangulated from multiple detections and clustered. Deduplication typically uses about 1 m clustering radii, with a correction to avoid merging adjacent same-class objects. Camera-height scale is the single most important accuracy factor for width: without it, MAE jumps to 1.57 m.

### Cited Findings
**UrbanVGGT single-image geometry (key numbers)**
- Pipeline: SegFormer-B5 (Cityscapes) keeps the sidewalk and road classes, with small-region removal and hole filling. VGGT in single-image mode outputs a per-pixel point map and pose, up to scale. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- Ground-plane fitting: coarse SVD plane, then MAD-based dispersion. RANSAC inlier threshold τ = clip(2.5 × 1.4826 × MAD, 0.005, 0.05), followed by an SVD refit on the inliers. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- Scale: s = h_cam / h_pred, where h_pred is the camera-to-plane distance. The prior is h_cam = 2.5 m for Google Street View cars. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- Width: column-wise scan within a central band. For each column, the inner and outer sidewalk boundaries are projected onto the plane and measured along the estimated across-sidewalk direction, then aggregated with robust statistics and plausibility filters. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- Accuracy (DC, ~300 images, reference widths 0.56–3.94 m): MAE 0.252 m, RMSE 0.293 m, 49.9% within 0.25 m, 95.5% within 0.50 m, bias −0.055 m. Without scale calibration: MAE 1.571 m. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- Alternative backbones in the same pipeline, MAE in m:

  | Model | Native metric | Pinhole unprojection + height calibration | Point-cloud + height calibration |
  |---|---|---|---|
  | DepthAnythingV2 | 1.712 (-m) | 0.628 (-r) | — |
  | ZoeDepth | 1.067 | 0.583 | — |
  | DepthPro | 0.768 | 0.718 | — |
  | Metric3DV2 | 1.361 | 0.417 | — |
  | UniDepthV2 | 0.289 | 0.436 | — |
  | MapAnything | 0.463 | — | 0.334 |
  | CUT3R | — | — | 0.672 |
  | π³ | — | — | 0.324 |
  | VGGT (UrbanVGGT) | — | — | 0.252 |

  MoGe was not evaluated. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- Camera-height sensitivity: with a true prior of 2.5 m, assuming 2.0 / 2.25 / 2.75 / 3.0 m gives MAE 0.384 / 0.283 / 0.276 / 0.349 m and within-0.5 m shares of 65.5% / 82.4% / 85.0% / 69.1%. Height error biases width in the same direction, roughly proportionally. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- Coverage caveat: in the NYC, São Paulo and Nairobi prototypes, only 1,931 valid image-level measurements covered 527 of 3,958 OSM segments (7.6–38.2% per city). Filtering discards many images. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)

**Multi-frame reconstruction tools and licences**
- VGGT reconstructs a scene "in less than 1 second". `demo_colmap.py` exports COLMAP `cameras.bin`, `images.bin` and `points3D.bin`, with optional bundle adjustment (`--use_ba`). A May 2026 memory fix lets it process about 2–3× more frames on the same GPU. VGGT-Omega was released on 18 May 2026. — [facebookresearch/vggt README](https://github.com/facebookresearch/vggt)
- VGGT licence: since 29 July 2025 the code allows commercial use, excluding military applications. **Only the `VGGT-1B-Commercial` checkpoint** may be used commercially, and it requires an access application. The original VGGT-1B remains non-commercial. — [VGGT README](https://github.com/facebookresearch/vggt); [HF VGGT-1B-Commercial](https://huggingface.co/facebook/VGGT-1B-Commercial)
- MASt3R/DUSt3R are reported as CC BY-NC-SA 4.0 (non-commercial). This is a secondary source; verify in the repo. — [arXiv 2506.09883](https://arxiv.org/pdf/2506.09883)
- OpenSfM is Mapillary's open-source Python SfM library. It reconstructs camera poses and 3D scenes and can use GPS and accelerometer data for georeferenced alignment. — [OpenSfM fork README](https://github.com/Geo-fortune/OpenSfM); [Mapillary help](https://help.mapillary.com/hc/en-us/articles/360003021152-Types-of-map-data)

**Object triangulation and deduplication**
- Mapillary map features are point data extracted with computer vision. Objects detected in several images are triangulated to 3D lat/lon using SfM plus semantic segmentation. Accuracy depends mainly on the capture device's GPS quality, and more images of a point improve it. Mapillary supports 42 point-feature classes and over 1,500 traffic-sign classes. — [Mapillary help: types of map data](https://help.mapillary.com/hc/en-us/articles/360003021152-Types-of-map-data)
- Krylov et al. (2017) geotag recurring stationary objects (GSV, Bing, Mapillary) by triangulating detections. Triangulation suppresses duplicates and false positives. Hierarchical clustering uses a maximum intra-cluster distance of 1 m. — [arXiv 1708.08417](https://arxiv.org/pdf/1708.08417)
- Combining geolocation and height estimation (2023): clustering can merge distinct nearby same-class objects. They split clusters by counting nodes originating from the same image pair. — [arXiv 2305.08232](https://arxiv.org/pdf/2305.08232)
- Position noise makes geolocation less accurate on crowdsourced Mapillary imagery than on Google Street View. — [EUSIPCO 2024, roadside object geolocation with reduced supervision](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000641.pdf)
- Object tracking plus geolocalisation from street images is an alternative to per-frame triangulation. — [Remote Sensing 14(11):2575](https://doi.org/10.3390/rs14112575)

### Inferences
- **Recommended geometry design:**
  1. Per sequence of roughly 20–100 frames, run VGGT-1B-Commercial (or COLMAP/GLOMAP or OpenSfM for longer sequences) to get relative poses and a dense point map.
  2. Fit a similarity transform (Umeyama/RANSAC) from SfM camera centres to GNSS positions in a local ENU/UTM frame. This sets scale and georeference.
  3. Check scale independently: fit a RANSAC road or sidewalk plane and compare the camera-to-plane distance against the known rig height. If GNSS-derived and height-derived scales disagree by more than ~5%, trust height for width and GNSS for position.
  4. Rasterise ground-labelled points (sidewalk, curb, road from Mask2Former labels) into a 5–10 cm bird's-eye grid per street.
  5. Extract the curb line as the sidewalk/road boundary (or the curb class), and the building line as the sidewalk/building, wall or fence boundary. Fit polylines (RANSAC lines or splines).
  6. Cast transects every 1–2 m perpendicular to the curb polyline to measure gross width (curb to building line) and clear width (minus obstruction footprints).
- With phone GNSS at ~3–10 m error (an assumption, not cited here), GNSS-only scale over short sequences is weak. Camera height is the more reliable scale for width, consistent with UrbanVGGT's ablation. Position (where the sidewalk is) still needs GNSS or OSM snapping.
- For point obstructions, cast a ray from each crop's camera centre through the detection's bottom-centre (ground contact point). Intersect it with the fitted ground plane for single-view position, or triangulate ≥2 rays for multi-view. Then cluster by class (DBSCAN or agglomerative, ε ≈ 1–2 m) and apply the same-image-pair split rule from arXiv 2305.08232 so adjacent motorcycles or café chairs are not merged.
- Licence-safe stack for commercial or government use: OpenSfM (BSD-2, unverified), COLMAP (BSD, unverified), GLOMAP (BSD, unverified) and VGGT-1B-Commercial. Avoid MASt3R/DUSt3R and the original VGGT-1B weights for production. UniDepthV2 is non-commercial, per prior research context.

### Gaps
- I did not verify the LICENSE files of COLMAP, GLOMAP, hloc, OpenSfM or MASt3R-SfM directly. The licences above are unverified recollection or secondary sources.
- I found no published per-sequence VGGT runtime or VRAM table, for example frames vs GB on an H100.
- I found no quantitative accuracy for Mapillary's own map-feature positions, such as a median error in metres.

---

## 3. Camera height estimation when unknown (archive Mapillary photos)

### Takeaway
Width error scales almost linearly with camera-height error: ±0.25 m height error at 2.5 m costs about 10–13 percentage points of the within-0.5 m share. Archive Mapillary images from unknown phones, helmets and car mounts need height estimated per sequence. Single-image calibration such as GeoCalib (gravity/roll/pitch plus focal) fixes orientation and intrinsics but **not** metric height. Height has to come from metric depth/point-map priors, known-size objects, or multi-view SfM with GNSS.

### Cited Findings
- GeoCalib (ECCV 2024) is a single-image calibration method that learns with geometric optimisation and estimates camera intrinsics and gravity direction. Code and trained models are public. The licence is listed as Apache-2.0 by a third-party index; I did not read the LICENSE file. Its training and evaluation code lives in a separate library, siclib. — [arXiv 2409.06704](https://arxiv.org/abs/2409.06704); [GitHub cvg/GeoCalib](https://github.com/cvg/geocalib); [ecosyste.ms index](https://awesome.ecosyste.ms/projects/github.com%2Fcvg%2Fgeocalib)
- UrbanVGGT warns that a fixed camera height can bias results across vehicle generations, and that other providers need their own height priors. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- UniDepthV2 achieved 0.289 m MAE *natively metric*, without height calibration, in the UrbanVGGT benchmark. A good metric depth model can therefore estimate camera height itself, as the camera-to-fitted-ground-plane distance in metric units. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)

### Inferences
- **Height estimation cascade for unknown sequences** (recommendation):
  1. Use EXIF/Mapillary metadata. If the image comes from a known rig (e.g. a GoPro Max on a car roof), use that rig's height prior.
  2. Run GeoCalib for pitch, roll and focal length.
  3. Run a commercially licensed metric model (MoGe-2, DepthPro, or MapAnything; check each licence) and fit a ground plane. Metric h_cam is the plane distance; take the median over all frames in the sequence, since height is constant within a sequence.
  4. Sanity-check against known-size objects in Lebanon: standard lane width, kerb height (~15 cm), car height (~1.45–1.5 m), and door height.
  5. Classify the sequence into a rig cluster (pedestrian handheld ≈ 1.4–1.7 m, car roof ≈ 1.8–2.5 m) and reject sequences whose estimated height is unstable.

  These height ranges are typical values I have not sourced.
- Mapillary's SfM-derived "computed altitude" is generally too noisy for this (unverified).
- Perspective Fields (Jin et al., CVPR 2023) is an alternative for up-vector and latitude fields. I did not verify its licence.

### Gaps
- I found no benchmark of camera-*height* estimation accuracy (in metres) from single street-level images.
- I did not check the GeoCalib LICENSE file, or the licences of siclib and Perspective Fields.

---

## 4. Detector and segmenter training: model choices, licences, labelling, active learning, imbalance, domain adaptation

### Takeaway
For commercial or government deployment, prefer Apache-2.0 detectors: RF-DETR Nano–Large, D-FINE and DEIM. Ultralytics YOLO (including YOLO11 and YOLO26) is AGPL-3.0. Ultralytics states this extends to custom-trained weights, even from scratch or for internal use, unless an Enterprise licence is bought. Use Mask2Former (Swin-L, Mapillary Vistas, 64.7 mIoU) for stuff classes (sidewalk, curb, road, curb cut). Pre-label new Lebanon classes with SAM 3 or other open-vocabulary models in CVAT or Label Studio. Surface problems are consistently the hardest class.

### Cited Findings
**Licences**
- Ultralytics says trained models fall under AGPL-3.0 by default, including custom models trained from scratch, without pretrained weights, or used only internally or for R&D. An Enterprise licence is required to avoid open-sourcing the project. — [Ultralytics license page](https://ultralytics.com/license); [Roboflow Ultralytics licensing](https://roboflow.com/ultralytics)
- Roboflow is an authorised licensor of Ultralytics models and states that custom-trained versions remain AGPL-3.0. — [Roboflow](https://roboflow.com/ultralytics)
- RF-DETR Nano through Large are Apache-2.0; XL and 2XL are under Roboflow's PML licence. — [Roboflow: RF-DETR vs alternatives](https://blog.roboflow.com/rf-detr-vs-alternatives/); [RF-DETR README](https://cdn.jsdelivr.net/gh/roboflow/rf-detr@develop/README.md)
- D-FINE and DEIM are Apache-2.0. — [Roboflow RF-DETR vs alternatives](https://blog.roboflow.com/rf-detr-vs-alternatives/)
- SAM 3 (Meta, released 19 November 2025) does "Promptable Concept Segmentation": it detects, segments and tracks all instances of a concept given a short text phrase or image exemplars. It is under a custom Meta licence with gated checkpoint access. A third-party mirror says commercial use is permitted with military, nuclear and espionage exclusions; verify in the official repo. — [arXiv 2511.16719](https://arxiv.org/pdf/2511.16719); [Roboflow: what is SAM 3](https://blog.roboflow.com/what-is-sam3/); [HF mirror README](https://huggingface.co/AEmotionStudio/sam3/blob/main/README.md)

**Accuracy and speed**
- RF-DETR (arXiv 2511.09554): latency is measured on a T4 with TensorRT 10.4 FP16. RF-DETR-N reaches 48.4 COCO AP50:95 and 67.6 AP50 in 2.3 ms at 384×384. The nano model beats D-FINE-N by more than 5 AP, at 2.1 ms for D-FINE-N. D-FINE-M reaches 55.0 AP in 5.4 ms; the paper reports 5.62 ms for the same model, a discrepancy between sources. — [RF-DETR paper](https://arxiv.org/pdf/2511.09554); [RF-DETR README](https://cdn.jsdelivr.net/gh/roboflow/rf-detr@develop/README.md)
- DEIM-D-FINE-L and DEIM-D-FINE-X reach 54.7 and 56.5 AP at 124 and 78 FPS on a T4. — [Roboflow comparison](https://playground.roboflow.com/models/compare/deim-vs-rf-detr)
- Mask2Former Swin-L (multi-scale) reaches 64.7 mIoU on Mapillary Vistas val. — [Mask2Former, arXiv 2112.01527](https://arxiv.org/pdf/2112.01527); [paperswithcode listing](https://astro.paperswithcode.com/paper/masked-attention-mask-transformer-for)

**Sidewalk-specific priors**
- Project Sidewalk's validation model (ResNet-18, ~300k crowdsourced labels from DC) reached 81.3% average precision and 77.2% recall. It did best on curb ramps (93.2% precision, 96.8% recall) and worst on surface problems (75.3% precision, 59.5% recall). Adding non-image context raised surface-problem recall from 48.5% to 56.7%. — [Weld et al. 2019](https://makeabilitylab.cs.washington.edu/media/talks/Weld_DeepLearningForAutomaticallyDetectingSidewalkAccessibilityProblemsUsingStreetscapeImagery_2019.pdf)
- ASSETS 2024 (Liu et al.) classifies 33 fine-grained tags across curb ramp, crosswalk, obstacle and surface problem with DINOv2 and ViT-CLIP, and releases an open dataset. — [Liu et al. ASSETS 2024](https://makeabilitylab.cs.washington.edu/media/publications/Liu_TowardsFineGrainedSidewalkAccessibilityAssessmentWithDeepLearningInitialBenchmarksAndAnOpenDataset_ASSETS2024.pdf)
- A 2025 IET Smart Cities framework trained YOLOv8 on Project Sidewalk data plus a local Porto dataset. Curb ramps reached 91% recall and 85% precision, which shows that adding local data transfers well. — [UFP repository](https://bdigital.ufp.pt/entities/publication/efecff5b-a7d5-424b-bc5d-759ce53e732c/full)
- RampNet (2025) is a two-stage pipeline that bootstraps curb-ramp detection labels from open government metadata, a model for auto-generating labels from existing GIS. — [arXiv 2508.09415](https://arxiv.org/pdf/2508.09415)
- Pedestrian-level VLM assessment of sidewalk accessibility attributes (2026) evaluates how reliable VLMs are on this task. — [arXiv 2609.17882](https://arxiv.org/html/2609.17882)

### Inferences
- **Model split.**
  - Semantic stuff (sidewalk, curb, road, curb cut, terrain, building, wall, fence): Mask2Former Swin-L pretrained on Vistas, fine-tuned on ~1–2k densely labelled Lebanese crops. Lebanese sidewalks are often tiled, broken, very narrow or merged with shopfronts, which differs from Vistas.
  - Thing obstructions (car-on-sidewalk, motorcycle, generator, vendor cart, shop goods, café furniture, kiosk, pole, step, construction barrier, low wire): RF-DETR-M/L or DEIM-D-FINE-L (Apache-2.0).
  - "On-sidewalk" status: decide geometrically. Intersect the object's footprint on the ground plane with the sidewalk mask or polygon, rather than training a separate "car on sidewalk" class.
- **Label budget heuristic** (not sourced). About 300–500 instances per new thing class for a usable first model, and about 1,000–1,500 for production. Rare classes (low wires, steps) need targeted mining. Use SAM 3 or Grounding DINO text prompts ("generator", "plastic chairs", "motorcycle on sidewalk") to pre-label, then correct in CVAT (SAM-assisted) or Label Studio.
- **Active learning loop.** Each round:
  1. Run the current model on an unlabelled pool.
  2. Rank by uncertainty or entropy, plus disagreement between the open-vocabulary model and the detector.
  3. Send the top ~500 crops to annotators.
  4. Retrain.
  5. Track the evaluation slices (city, rig type, time of day) in FiftyOne.
- **Class imbalance.** Repeat-factor sampling (LVIS-style), copy-paste augmentation of rare objects onto sidewalk regions, and focal or varifocal loss (already in DETR-family losses).
- **Domain adaptation.** Fine-tune on mixed data (Vistas, ROD with its Tehran images (MIT), and local Lebanese data). Include Mapillary phone imagery with motion blur and low light. Use photometric augmentation and test-time augmentation (flip, multi-scale) for final mapping runs; latency matters less than accuracy offline.
- **Ultralytics.** If the project's code is open-sourced under AGPL (e.g. a public-good NGO repo), YOLO remains viable. Otherwise budget for an Enterprise licence or use RF-DETR, D-FINE or DEIM.

### Gaps
- I found no published per-class label-budget curves for sidewalk obstruction classes.
- I did not verify the licences of Grounding DINO, YOLO-World, Florence-2 (believed MIT), OneFormer or Mask2Former (believed MIT) in this session.
- I found no Lebanon- or Middle-East-specific sidewalk obstruction dataset beyond ROD (noted in prior research context).

---

## 5. Surface condition classification (cracks, broken tiles)

### Takeaway
No public dataset targets **sidewalk** surface condition from street view. Road-damage datasets (SVRDD street-view, RDD2020, PaveDistress) and StreetSurfaceVis (surface type) are the nearest proxies. Project Sidewalk's labels and the ASSETS 2024 tags are the most sidewalk-relevant. Expect surface condition to be the least accurate attribute: in Project Sidewalk, surface-problem recall was about 60%.

### Cited Findings
- SVRDD (Scientific Data, April 2024) is a public street-view road damage dataset from five Beijing districts, with ten detectors benchmarked. Classes include longitudinal, transverse and alligator cracks, potholes and patches. — [PubMed 38649712](https://pubmed.ncbi.nlm.nih.gov/38649712/)
- A 2026 Scientific Reports paper presents a road-damage dataset (potholes, cracks, manholes). It notes that wide-angle distortion in street-view datasets reduces geometric fidelity. It cites StreetSurfaceVis as a crowdsourced, mainly German street-level dataset annotated by surface type. — [Nature Sci Rep 2026](https://www.nature.com/articles/s41598-026-46679-4)
- PaveDistress (Data in Brief, 2024) uses highway inspection-vehicle imagery from China with cracks, patches and potholes, so it is not street-view. — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2352340924010734); [Mendeley Data](https://data.mendeley.com/datasets/f46zt2g83x/1)
- A CACAIE paper augments RDD2020 with street-view examples. Its hard negatives include shadows, **pedestrian road tiles**, concrete ditches, walls and slip-prevention pavements, which are relevant confounders for tiled Lebanese sidewalks. — [Yamaguchi et al., CACAIE](https://onlinelibrary.wiley.com/doi/10.1111/mice.70125?af=R)
- StructDamage (2026) is a large unified crack and surface-defect dataset. — [arXiv 2603.10484](https://arxiv.org/pdf/2603.10484)
- Vision-language foundation models have been applied to comprehensive pavement condition assessment. — [arXiv 2604.08212](https://arxiv.org/pdf/2604.08212)
- Project Sidewalk surface-problem detection is the weakest category: 75.3% precision and 59.5% recall. — [Weld et al. 2019](https://makeabilitylab.cs.washington.edu/media/talks/Weld_DeepLearningForAutomaticallyDetectingSidewalkAccessibilityProblemsUsingStreetscapeImagery_2019.pdf)

### Inferences
- **Recommended approach.** Treat condition as a **patch classification** task on ground-rectified sidewalk patches, not as box detection:
  1. Use the sidewalk mask and ground-plane homography to warp the sidewalk into a top-down metric patch of about 1 m × 1 m.
  2. Classify each patch as good / cracked / broken-missing tiles / uneven / unpaved with a DINOv2 or DINOv3 linear probe, or a small fine-tuned ViT. This mirrors Project Sidewalk's sidewalk-validator-ai (DINOv2).
  3. Aggregate the share of bad patches per segment.
- Rectification removes perspective, so patch scale is consistent and rules like "more than X% broken over Y m" become measurable.
- Surface material (tile, asphalt, concrete, unpaved) is easier than condition, so label it separately; StreetSurfaceVis-style taxonomy helps here.
- Low-cost labelling: about 3–5k patches with SAM-assisted region labels, plus hard negatives (patterned tiles, shadows, wet surfaces).

### Gaps
- I found no sidewalk-specific crack or broken-tile public dataset with a licence suitable for training. I did not read the licences for SVRDD, StreetSurfaceVis or StructDamage.

---

## 6. Compute: throughput, GPU prices, cost per million images, storage, orchestration

### Takeaway
Mask2Former Swin-L at 1024 resolution is the throughput bottleneck: about 3 to 14 images/s depending on implementation and GPU. Real-time DETR detectors run at hundreds of images/s on a T4 with TensorRT. GPU-hours dominate cost, at roughly **$25–$200 per million perspective crops** for segmentation on A100-class marketplace GPUs. Cloud GPU prices in 2026 are about $0.50–$2/h for an A100 and about $0.5–0.8/h for an L4.

### Cited Findings
- MMSegmentation Mask2Former Swin-L (in22k), A100: 2.86 fps at 512×1024 (Cityscapes, 83.65 mIoU) and 8.81 fps at 640×640 (ADE20K, 56.01 mIoU). — [MMSeg mask2former configs](https://openi.pcl.ac.cn/open-mmlab/mmsegmentation/src/tag/v1.1.1/configs/mask2former)
- A third-party table lists Mask2Former Swin-L at 1024×2048 at 83.3 mIoU and 14 FPS, without naming the GPU. — [iFAN, arXiv 2608.03216](https://arxiv.org/pdf/2608.03216)
- RF-DETR-N takes 2.3 ms on a T4 (TensorRT FP16, 384×384), roughly 430 images/s of pure model time. DEIM-D-FINE-L runs at 124 FPS on a T4. — [RF-DETR README](https://cdn.jsdelivr.net/gh/roboflow/rf-detr@develop/README.md); [Roboflow DEIM vs RF-DETR](https://playground.roboflow.com/models/compare/deim-vs-rf-detr)
- VGGT reconstructs a scene in under 1 s. — [VGGT README](https://github.com/facebookresearch/vggt)
- 2026 GPU prices (aggregators; verify live):

  | GPU | Vast.ai | RunPod | Lambda |
  |---|---|---|---|
  | H100 | $1.49–2.27/h | PCIe $2.89/h, SXM $3.49/h | $3.29–4.29/h |
  | A100 80GB | $0.50–0.80/h | community A100 PCIe ~$1.19/h | ~$1.99/h |
  | L4 24GB | — | $0.49/h (Secure) | not offered |

  Northflank lists the L4 at $0.80/h. Lambda has a 99.9% uptime SLA, RunPod 99%, and Vast.ai none. — [CloudZero 2026](https://www.cloudzero.com/blog/cloud-gpu-pricing-comparison/); [Spheron RunPod vs Vast 2026](https://www.spheron.network/blog/gpu-cloud-pricing-comparison-runpod-vs-vastai-2026/); [Northflank](https://northflank.com/blog/cheapest-cloud-gpu-providers); [DEV Community guide](https://dev.to/abdulrahman_maslmany/cloud-gpu-pricing-guide-2026-runpod-vs-lambda-vs-aws-vs-vastai-29e4). Several are vendor blogs with differing snapshot dates.

### Inferences
- **Cost per million crops.** These are my calculations, not published figures.
  - Mask2Former Swin-L at 3 img/s means 1M images take ≈ 92.6 GPU-h. On an A100 at $0.80–1.99/h that is **≈ $75–185**. At 14 img/s (an optimised FP16 or TensorRT pipeline) it is ≈ 19.8 GPU-h, or **≈ $16–40**.
  - RF-DETR-M or DEIM-L at about 100 img/s end-to-end on an L4 takes ≈ 2.8 GPU-h, **≈ $1.5–2.5**.
  - VGGT single-image passes at an assumed ~0.2–0.5 s/image on an A100 would take ≈ 55–140 GPU-h, **≈ $45–280**. This rate is an assumption; benchmark it.
  - Panoramas multiply cost by the number of crops (2–4).
  - **Order of magnitude for Lebanon:** 1–3 million panoramas × 3 crops ≈ 3–9M crops, so **~$1k–5k of GPU time** for one full pass of segmentation, detection and geometry, plus 2–4× that for experimentation and reruns.
- **Storage.** Assuming ~1–3 MB per Mapillary JPEG (unverified), 3M images are about 3–9 TB of raw imagery. Store masks as PNG or RLE (small) and point maps as float16 only for retained ground pixels, or discard them after width extraction. Object storage (S3, R2, B2) suits this; Cloudflare R2 has no egress fees (verify).
- **Orchestration.**
  - Ray Data, or Dask with GPU workers, sharded by Mapillary sequence ID so SfM stays sequence-local.
  - DVC for dataset and label versions; MLflow for training runs and model registry.
  - Pin container images (CUDA, torch) and model checksums, and record model version and crop parameters in every output row for reproducibility.
  - Use spot or marketplace GPUs (Vast, RunPod community) for idempotent, checkpointed batch inference, and reliable instances for training.
- **Hardware.** For a single team, an RTX 4090 (24 GB) can run all inference models. VGGT multi-frame batches need more VRAM; an A100 or H100 80 GB is preferable for long sequences.

### Gaps
- I found no published Mask2Former throughput on an RTX 4090 or L4, no published VGGT single-image latency, and no AWS or GCP 2026 on-demand prices with a primary-source page fetched. Check aws.amazon.com/ec2/pricing and cloud.google.com/compute/gpus-pricing.
- Storage size per Mapillary image is unverified.

---

## 7. Fusion into a map: OSM block-face snapping, aggregation, confidence, conflict rules, OpenSidewalks/OSM publishing

### Takeaway
Aggregate image-level measurements onto OSM-derived block-face (sidewalk side) segments, and report robust statistics: median width, plus a low percentile or pinch-point width for accessibility. The publishing targets are the OpenSidewalks schema (fields include width, surface, incline, tactile_paving) and OSM tags. Encode width and surface as `sidewalk:left/right:width/surface` or on separate `footway=sidewalk` ways, and curbs as `barrier=kerb` nodes with `kerb=*`.

### Cited Findings
- The OpenSidewalks schema fields include incline, surface, length, width, tactile_paving, crossing:markings, step_count and climb. Positive incline means uphill in the direction of travel. — [OpenSidewalks Schema index](https://awesome.ecosyste.ms/projects/github.com%2FOpenSidewalks%2FOpenSidewalks-Schema)
- OSM form: `sidewalk(:left|:right):width=* [m]`, with matching surface and incline keys. — [Heidelberg tag list](https://www.uni-heidelberg.de/md/chemgeo/geog/gis/tagliste.pdf)
- OSM PWG guide: curbs are nodes tagged `barrier=kerb` with a `kerb=*` type. Crossings are nodes tagged `highway=crossing`. — [OSM PWG Guide](https://wiki.openstreetmap.org/wiki/PWG_Guide); [OSM Proposal: Sidewalk schema](https://wiki.openstreetmap.org/wiki/Proposal:Sidewalk_schema)
- Left/right sidewalk keys can be "tricky and misleading" (SidewalKreator, SotM 2022). — [SotM 2022 slides](https://2022.stateofthemap.org/attachments/JNJKYR_vestena_et_al_sotm2022_4FR9eti.pdf)
- UrbanVGGT matched measurements to OSM segments: 527 of 3,958 segments covered, with median widths of 2.28–2.64 m by city. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- UrbanVGGT's authors say broader cross-city validation and local ground-truth audits are needed before the data can serve as authoritative planning data. — [UrbanVGGT](https://arxiv.org/abs/2603.22531)

### Inferences
- **Block-face segmentation.**
  1. Generate block faces from OSM `highway=*` centrelines by offsetting each side and splitting at intersections. Use tools like SidewalKreator or OSMnx plus shapely.
  2. Assign each transect measurement to the nearest block face on the correct side, using the camera's side-of-road relative to the centreline and the crop's yaw.
  3. Gate assignment by perpendicular distance (e.g. ≤ 15 m) and heading agreement.
- **Per-segment aggregation:**
  - `width_median` (robust central value)
  - `width_p10` or `width_min_clear` (pinch point, computed after subtracting obstruction footprints)
  - `n_transects`, `n_images`, `n_sequences` (independent evidence count)
  - `width_IQR` (dispersion)
  - `curb_present_ratio`
  - `surface_bad_ratio`
  - `obstruction_count_per_100m`, broken down by class
- **Confidence score**, for example a logistic or heuristic combination of:
  - number of independent sequences (≥2 preferred)
  - agreement between single-view and multi-view widths
  - ground-plane residual
  - segmentation confidence on boundary pixels
  - camera-height certainty (known rig vs estimated)
  - occlusion share (parked cars covering the curb)

  Publish only segments above a threshold, and flag the rest for human review (Project Sidewalk-style).
- **Conflict rules.**
  - Manual field survey beats automated output.
  - A recent automated value with high confidence and ≥2 sequences beats older OSM tags only if the difference exceeds measurement uncertainty (~0.5 m).
  - Never overwrite OSM values automatically. Produce MapRoulette-style challenges or reviewed changesets.
  - Follow the OSM Automated Edits code of conduct and import guidelines; OSM community consultation is required for bulk imports (not fetched here).
- **Transient obstructions** (parked cars, vendors, café furniture) are time-variant. Store them as observations with a timestamp in a separate layer, not as permanent OSM features. Map permanent ones (poles, kiosks, steps, generators if fixed) as OSM nodes (e.g. `highway=street_lamp`, `amenity=*`) or as OpenSidewalks obstacle points.

### Gaps
- I did not retrieve the OpenSidewalks schema's exact mapping to OSM keys, or whether it has a curb or obstacle entity. Read the GitHub OpenSidewalks/OpenSidewalks-Schema README.
- I did not fetch the OSM import and automated-edit policy text.

---

## 8. Reported end-to-end accuracies of similar pipelines; main error sources and mitigations

### Takeaway
The best published street-view width accuracy is UrbanVGGT's MAE 0.25 m, 95.5% within 0.5 m. That result comes from a single city (DC) on ~300 curated images with a known camera height. Expect worse results on crowdsourced Mapillary imagery in Lebanon: unknown height, noisy GNSS, narrow and occluded sidewalks. The main errors are scale and camera height, non-planar ground, occlusion by parked vehicles, narrow-sidewalk segmentation error, and complex curb geometry. Detection of accessibility problems reaches roughly 80–95% precision for curb ramps but only about 60% recall for surface problems.

### Cited Findings
- UrbanVGGT: MAE 0.252 m, RMSE 0.293 m, 95.5% within 0.5 m (DC, ~300 images). Without scale calibration: MAE 1.571 m with 0% within 0.5 m. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- UrbanVGGT failure modes:
  - non-planar ground (driveway ramps, curb cuts, cross-slopes)
  - occlusion by parked vehicles, pedestrians, street furniture, vegetation and poles
  - very narrow sidewalks, where small segmentation errors cause large relative errors
  - complex curb geometry (bulb-outs, slip lanes, parking bays, shared spaces)

  — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- A GISRUK 2025 comparison found that a spatial-data analysis method gave broader coverage and more accurate sidewalk width than the street-view method. — [Zenodo 15182508](https://zenodo.org/records/15182508)
- LiDAR-based obstacle-free (clear) width estimation for accessibility: [arXiv 2211.04108](https://arxiv.org/pdf/2211.04108). Sidewalk-robot point-cloud width: [arXiv 2507.12148](https://arxiv.org/html/2507.12148v2).
- Project Sidewalk AI validation: 81.3% average precision and 77.2% recall overall; curb ramps 93.2% precision and 96.8% recall; surface problems 75.3% precision and 59.5% recall. — [Weld et al. 2019](https://makeabilitylab.cs.washington.edu/media/talks/Weld_DeepLearningForAutomaticallyDetectingSidewalkAccessibilityProblemsUsingStreetscapeImagery_2019.pdf)
- Crowdsourced Mapillary imagery gives less accurate object geolocation than Google Street View because of position noise. — [EUSIPCO 2024](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000641.pdf)
- Mapillary map-feature accuracy is mainly limited by capture-device GPS quality and improves with more images per object. — [Mapillary help](https://help.mapillary.com/hc/en-us/articles/360003021152-Types-of-map-data)
- ZenSVI is open-source software for acquiring, processing and analysing street-view imagery at scale (Mapillary download, segmentation, etc.), a candidate scaffolding layer. — [arXiv 2412.18641](https://arxiv.org/pdf/2412.18641)

### Inferences
Error sources and mitigations (my recommendations):

| Error source | Mitigation |
|---|---|
| Wrong camera height (≈ proportional width bias) | Estimate height per sequence (Section 3); use own captures with a known rig height for a calibration subset. |
| Non-planar ground (Lebanon has many steps, ramps and level changes at shopfronts) | Fit a local plane per transect band, not one global plane. Use multi-view point clouds and reject transects with high plane residuals. |
| Parked cars and motorcycles occluding the curb (endemic in Lebanon) | Multi-frame and multi-sequence fusion (see the curb from other viewpoints). Interpolate the curb polyline across occluded gaps from visible portions; flag the occluded share in confidence. |
| Narrow-sidewalk relative error | Use higher resolution crops (≥1024 px) and boundary-refinement or test-time augmentation; report absolute ± uncertainty. |
| Building-line ambiguity (shop goods, awnings, stairs encroaching) | Separate "gross width" (curb to property line) from "clear width" (minus obstructions), and store both. |
| GNSS position error placing measurements on the wrong block face | SfM pose refinement, map-matching to the OSM centreline, side-of-road logic. |
| Domain shift (Vistas/US to Lebanon) | Local fine-tuning with active learning (Section 4). |

- **Validation plan.** Collect field ground truth (tape or laser measure) at about 200–500 transects stratified by city (Beirut, Tripoli, Saida, Zahle), sidewalk type, and capture source (own rig vs archive Mapillary). Report MAE, P90 error and within-0.5 m share per stratum before publishing.

### Gaps
- I found no published end-to-end accuracies for curb presence classification or obstruction mapping as positional accuracy in metres from street-level pipelines.
- I found no results from Middle East or North Africa cities.
