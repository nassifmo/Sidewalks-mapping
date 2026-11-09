# Measuring Sidewalk Geometry (Width, Curb Height, Slope, Edges) from Street-Level Imagery: Methods, Code, Accuracy, and Fit for Mapillary in Beirut

Research date: 2026-11-06. About 20 search and fetch calls. Some primary PDFs (FHWA, ResearchGate, doi.org) returned HTTP 403 or were blocked, and those gaps are listed below.

## Q1. UrbanVGGT (arXiv 2026) and similar single-image width methods: method, code, licence, MAE, data needed

### Takeaway
UrbanVGGT is the strongest published single-image sidewalk-width result: MAE 0.252 m on about 300 Washington, D.C. GSV images. Its accuracy depends almost entirely on a known camera height; without it, MAE rises to 1.571 m. I found no public code or licence. It has been validated on one GSV benchmark only, never on Mapillary.

### Cited Findings
- UrbanVGGT, by Kaizhen Tan (CMU) and Fan Zhang (Peking University), arXiv 2603.22531, submitted 23 March 2026. It was also published in the ISPRS Archives XLIX-B2-2026, p. 559 (XXV ISPRS Congress). — [arXiv abs](https://arxiv.org/abs/2603.22531); [ISPRS Archives](https://isprs-archives.copernicus.org/articles/XLIX-B2-2026/559/2026/)
- Pipeline:
  - SegFormer-B5 fine-tuned on Cityscapes, keeping only the sidewalk and road classes.
  - VGGT in single-image mode, which outputs a per-pixel point map with arbitrary scale.
  - Ground-plane fit: SVD, then RANSAC with an adaptive MAD-based inlier threshold clipped to 0.005–0.05, then an SVD refit.
  - Scale: predicted camera height is matched to a fixed prior of 2.5 m for the GSV car.
  - Width: column-wise scan of the sidewalk mask in a central band, with boundary points projected onto the plane and robustly aggregated.
  - Source: [arXiv HTML](https://arxiv.org/html/2603.22531v1)
- Input: GSV perspective crops, 640×640 px with 90° FOV, so the intrinsics come from the FOV. It does not use panoramas or provider depth. — [arXiv HTML](https://arxiv.org/html/2603.22531v1)
- Accuracy on the D.C. benchmark (about 300 images, reference widths 0.56–3.94 m, ground truth from Lieu & Guhathakurta):
  - MAE 0.252 m, RMSE 0.293 m, bias −0.055 m.
  - 49.9% of estimates within 0.25 m and 95.5% within 0.50 m.
  - Ablations: no scale calibration gives MAE 1.571 m; pinhole only gives 1.096 m; using the full image width gives 0.265 m.
  - Source: [arXiv HTML](https://arxiv.org/html/2603.22531v1)
- Sensitivity to the camera-height prior (MAE): 2.00 m → 0.384 (bias −0.380); 2.25 m → 0.283; 2.50 m → 0.252; 2.75 m → 0.276; 3.00 m → 0.349 (bias +0.263). — [arXiv HTML](https://arxiv.org/html/2603.22531v1)
- Stated limitations:
  - Non-planar ground (driveway ramps, curb cuts, cross-slope) biases the fitted plane.
  - Parked cars, pedestrians, furniture, vegetation and poles hide the edges.
  - Narrow sidewalks are fragile.
  - Bulb-outs, parking bays and shared-space streets make the across-sidewalk direction ambiguous.
  - A fixed camera height may not hold across vehicles or providers.
  - The SV-SideWidth prototype (527 OSM segments in NYC, São Paulo and Nairobi) has no local ground truth, and street-view coverage per segment ranges from 7.6% (Nairobi) to 38.2% (NYC).
  - Source: [arXiv HTML](https://arxiv.org/html/2603.22531v1)
- No code repository, dataset URL or licence appears in the paper HTML. — [arXiv HTML](https://arxiv.org/html/2603.22531v1); author homepage [tantansir.github.io](https://tantansir.github.io/)
- Lieu & Guhathakurta, "A novel approach for estimating sidewalk width from street view images and computer vision", *Environment and Planning B* 53(5):1129–1144 (2026), DOI 10.1177/23998083251369602.
  - Method: two street-view images per point at different pitch angles, Canny edge detection, and trigonometry under a flat-ground assumption. It is sensitive to FOV settings.
  - No error numbers appear in the accessible abstract.
  - Sources: [RePEc/EconPapers](https://econpapers.repec.org/RePEc:sae:envirb:v:53:y:2026:i:5:p:1129-1144); method description in [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- A search-result summary attributes "mean width error 0.24 m for sidewalks 1–2 m wide" to a GSV sidewalk study. I could not trace this to a primary paper, so treat it as unverified. — [search result pointing to ResearchGate 394801929 (403 on fetch)](https://www.researchgate.net/publication/394801929_A_novel_approach_for_estimating_sidewalk_width_from_street_view_images_and_computer_vision)
- Morra et al. (MIT Senseable City Lab), "Sidewalk AI Scanner", Phil. Trans. R. Soc. A preprint (2024).
  - Method: smartphone video, PSPUNet segmentation, and a homography from a physical embedded grid of known size to a top-down view. The width is measured in that view.
  - Accuracy: average error 0.30 m overall across case studies. Per-case errors are 0.14, 0.58 and 0.05 m, and London had the highest error.
  - It requires a known-size reference grid in the frame, so it does not apply to archived Mapillary imagery.
  - Source: [MIT Senseable PDF](https://senseable.mit.edu/papers/pdf/20241110_Morra-etal_MappingSidewalks_RoyalSociety.pdf)
- Project Sidewalk / RampNet issue #217 (opened 29 Sep 2026 by jonfroehlich; PR #225 merged 1 Oct 2026, commit ec607c7) tested single-view, camera-height-scaled width on the Seoul dataset. Setup:
  - iPhone photos at 1.0 m camera height.
  - Mask2Former Mapillary-Vistas segmentation (`facebook/mask2former-swin-large-mapillary-vistas-semantic`).
  - EXIF intrinsics.
  - A vanishing-point horizon.
  - Source: [GitHub issue #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- Results of that test on a 254-photo held-out half:
  - Clear-width MAE 0.77 m (95% CI 0.50–1.06); total-width MAE 0.72 m; mean bias +0.29 m.
  - Recall for width below 1.2 m was 9/9, with precision 0.41.
  - Pitch is the dominant error term: ±2° of pitch equals ±10–16% of width. A level-horizon assumption gave a −0.66 m bias. A ±10% focal-length error changed width by under 0.1% when the horizon came from the image.
  - Worst failures came from a sidewalk touching the frame edge (+9.6 m) and from a bollard or pole truncating the span (−5.5 m).
  - Source: [GitHub issue #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- The same issue gives a geometry budget:
  - Width error scales with camera-height error: 10% height error gives about 10% width error, while pose error mostly cancels.
  - From 2.5 m height, 1° of angle is about 0.3 m of ground at 6 m and about 1.6 m at 15 m, so measure at the nearest point.
  - Fit the sidewalk plane, not the road plane: a 15 cm curb projected onto the road plane overstates width by about 6%.
  - Source: [GitHub issue #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- Seoul Sidewalk Accessibility Image Dataset (Lieu et al., MIT, arXiv 2609.17882). Zenodo DOI 10.5281/zenodo.22699523, CC0.
  - 514 iPhone photos with laser-measured effective width (0.9–10.2 m, mean 2.97 m), plus longitudinal slope, cross slope and pavement grade.
  - Its VLM baselines show width bias of +0.40 to +1.05 m, and the best calibrated 90% interval is about ±1.0 m (GPT-5.2).
  - Sources: [arXiv 2609.17882](https://arxiv.org/html/2609.17882); summarized in [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)

### Inferences
- The UrbanVGGT recipe (segmentation, point map, plane fit, camera-height scale) is the most transferable method for Beirut. On Mapillary, though, the camera height is not a fixed 2.5 m. It varies by contributor: handheld phones about 1.4–1.7 m, car-roof 360 rigs about 1.8–2.2 m, dashcams about 1.2–1.5 m. The camera-height table suggests a ±0.25 m height error adds roughly 0.03–0.13 m of MAE, while a ±0.5 m error adds about 0.1–0.3 m with a strong bias. Per-sequence height estimation, or Mapillary SfM scale, is therefore the critical sub-module.
- Mapillary Vistas-trained Mask2Former has sidewalk and curb classes, which makes it a better segmentation choice than the Cityscapes SegFormer for edge finding.
- The Project Sidewalk experiment (MAE about 0.7 m on phone photos) suggests UrbanVGGT's 0.25 m may not transfer to heterogeneous, non-GSV imagery without per-image pitch and horizon handling.

### Gaps
- UrbanVGGT code, licence and last commit: none found. Check the author homepage or contact the authors.
- Lieu & Guhathakurta's quantitative errors are behind a paywall (Environment and Planning B) and were not retrieved.
- No published evaluation of any of these methods on Mapillary imagery with ground truth was found.

## Q2. Monocular metric depth and 3D foundation models: which were evaluated for sidewalk or street metric measurement, errors, licences

### Takeaway
The only direct head-to-head on sidewalk width is the backbone table in UrbanVGGT. Native-scale metric depth is unreliable: DepthPro 0.77 m, Metric3Dv2 1.36 m and DepthAnythingV2 1.71 m MAE. UniDepthV2 is the exception at 0.29 m. Once camera-height scale calibration is added, most models fall to 0.25–0.7 m. Licences vary per checkpoint, and several of the best checkpoints are non-commercial.

### Cited Findings
- UrbanVGGT backbone comparison, sidewalk width MAE on the D.C. benchmark. — [arXiv HTML](https://arxiv.org/html/2603.22531v1)
  - **Native metric scale:** UniDepthV2 0.289 m; MapAnything 0.463; DepthPro 0.768; ZoeDepth 1.067; Metric3DV2 1.361; DepthAnythingV2 (metric) 1.712.
  - **Depth plus pinhole unprojection plus camera-height calibration:** Metric3DV2 0.417; UniDepthV2 0.436; ZoeDepth 0.583; DepthAnythingV2 0.628; DPT 0.701; DepthPro 0.718.
  - **Single-image point map plus camera-height calibration:** VGGT (UrbanVGGT) 0.252; π³ 0.324; MapAnything 0.334; CUT3R 0.672.
  - DUSt3R was excluded as a pairwise or multi-view model. MoGe and MASt3R were not tested.
- HeiGIT "HeiMeterStick" (blog by Maciej Adamiak, 18 Feb 2026).
  - Method: SAM3 text-prompted segmentation ("sidewalk") with Depth Anything V2 *Metric Indoor Large* depth. Intrinsics come from EXIF, falling back to GeoCalib. The point cloud is built, perpendicular widths are measured, and an Isolation Forest removes outliers.
  - Run on about 80k Mapillary images of central Łódź. The only result reported is that "the output has some anomalies".
  - No accuracy numbers, code URL or licence were published.
  - Source: [HeiGIT blog](https://heigit.org/measuring-what-you-never-notice-a-computer-vision-approach-to-accessible-paths/)
- Project Sidewalk found that MapAnything's gain came from the ground surface, not from pose. It plans MapAnything with GPS/compass poses (`mapa_posed_pair`) as the multi-view fallback for Mapillary, which lacks Google depth. — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- Licences:
  - **UniDepth V2:** CC BY-NC 4.0, non-commercial. — [Ultralytics overview](https://www.ultralytics.com/blog/best-depth-estimation-models)
  - **Depth Anything V2:** only Small is commercial-OK; Base and Large are CC BY-NC 4.0. The metric checkpoints are bounded to 20 m (indoor) and 80 m (outdoor). — [Ultralytics overview](https://www.ultralytics.com/blog/best-depth-estimation-models)
  - **Metric3D v2:** code BSD-2-Clause; check the checkpoint terms separately. — [Ultralytics overview](https://www.ultralytics.com/blog/best-depth-estimation-models)
  - **VGGT:** code under a commercial-friendly licence since 29 Jul 2025, with military use excluded. The VGGT-1B-Commercial checkpoint is commercial by application form; the original VGGT-1B remains non-commercial. The latest news is VGGT-Omega (18 May 2026) and a memory fix (15 May 2026). — [GitHub facebookresearch/vggt](https://github.com/facebookresearch/vggt)
  - **MASt3R:** code and checkpoints CC BY-NC-SA 4.0, and users must also accept the training-dataset licences (Map-free is "very restrictive"). The checkpoint `..._catmlpdpt_metric` is trained with metric regression. — [GitHub naver/mast3r](https://github.com/naver/mast3r)
  - **MoGe:** code MIT (DINOv2 part Apache-2.0). All MoGe-2 variants output metric scale. MoGe-3 was released 2026-08-18. The weight licence is not stated on the README. — [GitHub microsoft/MoGe](https://github.com/microsoft/MoGe); [MoGe-2 paper](https://arxiv.org/pdf/2507.02546)
  - **Depth Pro (Apple):** code and weights are released under a repo LICENSE file whose type the README does not name. — [GitHub apple/ml-depth-pro](https://github.com/apple/ml-depth-pro)
- A 2026 Geomatics review covers monocular depth for volunteered street-view imagery. Per the search summary, it says street-view computer-vision accuracy ranges from sub-metre to about 5 m, below sensor and UAV surveys. I could not fetch the full text. — [Geomatics 6(5):102 (DOI)](https://doi.org/10.3390/geomatics6050102)

### Inferences
- For a Beirut module, the strongest candidates are VGGT (Commercial checkpoint) or MoGe-2/3 (MIT code, metric output) with plane fitting and per-image camera-height scale. UniDepthV2 has the best native-scale result, but its non-commercial licence may matter if outputs feed commercial or government products. For academic or NGO use, CC BY-NC is likely acceptable; check with the project lead.
- HeiMeterStick's choice of an indoor metric Depth Anything checkpoint for outdoor scenes, with no published accuracy, is a weak foundation. UrbanVGGT's table shows that native Depth Anything V2 metric scale gives 1.7 m MAE on sidewalk width.
- At 5–15 m range, ground-plane angular resolution dominates: about 0.3 m/° at 6 m versus 1.6 m/° at 15 m from 2.5 m height ([RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)). Restrict measurements to the nearest 3–8 m in Beirut's narrow streets.

### Gaps
- No street-scene evaluations of MoGe, DUSt3R or MASt3R for width or curb were found.
- I found no per-distance error curves at 5–15 m for these models on sidewalk geometry. KITTI-style AbsRel benchmarks exist but were not retrieved in this pass.
- The Depth Pro licence wording and the MoGe and DUSt3R weight licences were not verified at source. From prior knowledge, which is unverified here, Depth Pro is released under a restrictive Apple research licence and DUSt3R under CC BY-NC-SA 4.0. Confirm both before use.
- Last-commit dates were not visible on the fetched GitHub pages.

## Q3. Using Mapillary's own SfM (sfm_cluster, mesh, computed poses) or running OpenSfM/COLMAP on Mapillary sequences for widths

### Takeaway
Mapillary exposes per-image `camera_parameters`, `computed_geometry`, `computed_compass_angle`, `computed_rotation`, `sfm_cluster` (point-cloud URL) and `mesh` (URL). The only open tool I found that measures widths from Mapillary poses is street-width-lab, an early, simulation-only prototype that uses parked-car wheelbases as scale bars. I found no peer-reviewed paper measuring sidewalk width from Mapillary sfm_cluster point clouds.

### Cited Findings
- Mapillary API v4 image fields (via the Mapillary Python SDK docs):
  - `sfm_cluster` – {id, url}, the URL to the point cloud.
  - `mesh` – {id, url}.
  - `computed_geometry` – a GeoJSON point, the location after processing.
  - `camera_parameters` – an array of floats with the intrinsics.
  - Fields must be requested explicitly.
  - Sources: [Mapillary Python SDK – entities](https://mapillary.github.io/mapillary-python-sdk/docs/mapillary.config.api/mapillary.config.api.entities); [Mapillary API v4 blog (2021)](https://blog.mapillary.com/update/2021/06/23/getting-started-with-the-new-mapillary-api-v4.html)
- Mapillary has historically added semantic labels to OpenSfM point clouds, colouring each 3D point by the segmentation class of its source pixels. — [Mapillary blog, "Denser 3D point clouds in OpenSfM" (2016)](https://blog.mapillary.com/update/2016/10/31/denser-3d-point-clouds-in-opensfm.html)
- kauevestena/street-width-lab:
  - **Method:** a browser tool plus Python. The user clicks the front and rear wheel hubs of parked cars, and a bundle adjustment solves poses, points and one global scale, using known wheelbases as scale bars.
  - **Mapillary inputs:** `computed_rotation` (an angle-axis vector mapping local ENU to the camera frame), `computed_geometry`, `computed_altitude` and `computed_compass_angle`. Mapillary scale is described as good to "a few percent".
  - **Simulated accuracy on an 8 m road:**
    - Forward camera within 22 m: 24 cm with Mapillary scale, 8 cm with wheelbase scale.
    - Forward camera within 12 m: 23 cm and 5 cm.
    - 360° at 2048 px: 24 cm and 1.4 cm.
    - 360° at full resolution: 24 cm and 0.5 cm.
  - **Status:** 4 commits, copyright 2026, no licence stated, real-data validation "pending". It does not use sfm_cluster or mesh.
  - Source: [GitHub kauevestena/street-width-lab](https://github.com/kauevestena/street-width-lab)
- ZenSVI (open-source SVI toolkit) includes a Mapillary downloader (MLYDownloader) and a workflow that turns panoramic imagery into point clouds via depth estimation. — [ZenSVI arXiv 2412.18641](https://arxiv.org/pdf/2412.18641); [ZenSVI docs](https://zensvi.readthedocs.io/en/stable/autoapi/zensvi/download/MLYDownloader.html)

### Inferences
- In Beirut, parked cars are everywhere and are often on the sidewalk. That makes the wheelbase-as-scale-bar idea from street-width-lab unusually attractive as a scale reference, because known car models give metric anchors. It still needs real-data validation.
- A practical Mapillary pipeline would work as follows:
  1. Pull sequences with `computed_*` poses and `camera_parameters`.
  2. Fetch sfm_cluster points.
  3. Label points by Vistas segmentation, the way Mapillary itself does.
  4. Fit the sidewalk and road planes.
  5. Measure the distance from the curb line to the building line.
  The sfm_cluster clouds are sparse, so a dense method (VGGT or MapAnything posed with Mapillary poses) is likely needed for edges.
- Because Mapillary scale is GPS-derived ("a few percent"), a 3% scale error on a 2 m sidewalk is only about 6 cm. Scale is less of a problem than edge detection and occlusion.

### Gaps
- No primary "HeiMeterStick" code, no "StreetMeasure" tool, and no peer-reviewed Mapillary sfm_cluster width paper were found.
- The density, coordinate frame and availability of sfm_cluster and mesh files for Beirut sequences were not checked. Test with the API.
- The official Mapillary developer documentation page did not appear in results. Field definitions above come from the SDK docs.

## Q4. Panorama-based geometry with known camera height; GSV-based width; Project Sidewalk measurement work

### Takeaway
Known camera height turns any image (perspective or 360) into a metric ground-plane ruler. That is the core of UrbanVGGT, Lieu & Guhathakurta, and Project Sidewalk's 2026 width track. Project Sidewalk now pulls per-panorama camera heights for 1.43M GSV panoramas, but Mapillary has no equivalent depth-plane data.

### Cited Findings
- Project Sidewalk's `sidewalk-panorama-tools` stores Google's depth-plane data, giving per-panorama camera height and ground tilt for 1.43M GSV panoramas across 54 cities. A per-rig constant height still beat per-panorama heights for placement (GSV placement error dropped from 6.09° to 3.92° with per-rig height). — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- Ground-truth sidewalk polygon sources Project Sidewalk identified, as of 2026-09-30:
  - São Paulo GeoSampa `calcada`: 491k block-face polygons with min, mean and max width.
  - Richmond: 114k polygons, plus VDOT integer-foot widths.
  - None of these sources distinguishes total width from clear width.
  - Source: [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- Lieu & Guhathakurta (2026) use two GSV views at different pitches with trigonometry under a flat-ground assumption. — [EconPapers](https://econpapers.repec.org/RePEc:sae:envirb:v:53:y:2026:i:5:p:1129-1144)
- UrbanVGGT samples GSV views about every 30 m along OSM road segments and takes the median width per segment. — [search-result summary of arXiv PDF](https://arxiv.org/pdf/2603.22531)

### Inferences
- For Mapillary 360 sequences, rectify the panorama to a downward-pitched virtual perspective crop (for example 90° FOV) facing the sidewalk. Then apply the UrbanVGGT plane-fit with camera height estimated per sequence, for example from the fitted road-plane distance in metric SfM. The geometry holds for any camera whose height is known.

### Gaps
- No paper evaluating width from Mapillary or KartaView 360 imagery with ground truth was found.

## Q5. Curb height and slope from images or smartphone LiDAR

### Takeaway
No validated curb-height-from-street-imagery method was found. Project Sidewalk explicitly calls slope and lip height out of scope for imagery, since running-slope checks need 2–3 cm of vertical accuracy. Smartphone LiDAR (iPhone/iPad Pro) is the realistic route for curb height and ramp slope in field sampling. iOSPointMapper does not yet report curb or slope metrics.

### Cited Findings
- Project Sidewalk: "Slope and lip height" are out of scope for street imagery. An 8.33% running slope over about 1.5 m needs 2–3 cm of vertical accuracy, and VLM slope intervals on the Seoul set are 7–10° wide against limits of 1.15–4.76°. — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- iOSPointMapper (Naidu, Zhang, Mehta, Caspi; arXiv 2512.22392, v1 26 Dec 2025, v2 28 Aug 2026; TRB 2026). — [arXiv abs](https://arxiv.org/abs/2512.22392); [arXiv HTML](https://arxiv.org/html/2512.22392v1)
  - Runs on iPhone/iPad with on-device segmentation, ARKit LiDAR depth and GPS/IMU fusion, and outputs to TDEI/OpenSidewalks.
  - **Sidewalk width error:** RMSE 1.31 m (Seattle), 1.18 m (Bellevue), 1.22 m (Redmond); mean error about 0.84–0.90 m.
  - **Sidewalk location error:** RMSE about 0.73–0.76 m.
  - **Object localization RMSE:** buildings 0.86–1.14 m, signs about 1.2 m, poles 1.7–2.2 m, traffic lights 3.9–4.4 m. Errors rise beyond 5 m because of LiDAR range; within 5 m RMSE is "often below 0.5 m".
  - Curb, slope and cross-slope are listed only as future work. No code URL or software licence is stated in the paper.
- FHWA "Pocket Lidar Curb Ramp Assessments" (FHWA-HRT-25-014): smartphone LiDAR apps showed good performance for curb-ramp slopes against a TLS reference (RMS 0.005 m), and two apps came close to that reference. Per the search snippet only; the PDF returned 403. — [FHWA PDF](https://highways.dot.gov/sites/fhwa.dot.gov/files/FHWA-HRT-25-014.pdf)
- Earlier mobile-LiDAR (vehicle) ADA work extracted curb elevation height, ramp slope and sidewalk width, but its accuracy numbers were not retrieved. — [ResearchGate: Automated Sidewalk Assessment … 3-D Mobile LiDAR](https://www.researchgate.net/publication/304492689_An_Automated_Sidewalk_Assessment_Method_for_the_Americans_with_Disabilities_Act_Compliance_Using_3-D_Mobile_LiDAR)
- The Seoul dataset includes laser-measured longitudinal and cross slope (CC0), which could benchmark slope estimators. — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217); [arXiv 2609.17882](https://arxiv.org/html/2609.17882)

### Inferences
- For Beirut, treat curb height and slope as field-sampled attributes, using an iPhone/iPad Pro LiDAR app at close range (under 5 m), not as imagery-derived ones. From imagery, at most a coarse "curb present / high / flush" class seems feasible, using Vistas curb-class segmentation plus a plane-offset estimate. That is unvalidated.

### Gaps
- No published curb-height MAE from monocular or SfM street imagery was found.
- The FHWA full numbers (per-app slope RMS, lip height) were not retrieved because of the 403.
- No iOSPointMapper code repository or licence was found.

## Q6. Fusing street-level measurements with overhead polygons and building footprints

### Takeaway
Fusion is mostly done with LiDAR plus cadastral data, as in Amsterdam, or as ground truth, as in São Paulo's polygons. The Zenodo study comparing street-view and spatial-data methods favoured spatial data for coverage and accuracy. A building-line plus street-level curb-line approach suits Beirut, where facades usually bound the sidewalk.

### Cited Findings
- Amsterdam-AI-Team/Urban_PointCloud_Sidewalk_Width measures sidewalk widths from urban point clouds plus cadastral (BGT) polygons, detecting static obstacles with M3C2 change detection. — [GitHub](https://github.com/Amsterdam-AI-Team/Urban_PointCloud_Sidewalk_Width); [arXiv 2211.04108](https://arxiv.org/pdf/2211.04108)
- A Zenodo study (v1, 9 Apr 2025), "Sidewalk width measurement using street view images and spatial data analysis", found that the spatial-data method gave broader coverage and more accurate widths than the street-view method, per the search summary. — [Zenodo 15182508](https://zenodo.org/records/15182508)
- Project Sidewalk notes that city polygons give total pavement width, not clear width. — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)

### Inferences
- A Beirut hybrid would work as follows:
  - Take the building-footprint edge (OSM or Microsoft/Google footprints) as the inner sidewalk edge.
  - Detect the curb line in Mapillary using Vistas curb or sidewalk segmentation, located with SfM or VGGT plus camera height.
  - Compute width as the curb-to-footprint distance.
  - Use street-level images mainly to locate the curb and to flag obstructions (parked cars, poles), giving clear versus total width.
- Footprint positional error, typically metre-level for global AI footprints, would dominate on narrow Beirut sidewalks. Register the footprints locally against Mapillary SfM facade points.

### Gaps
- Exact accuracy numbers from the Zenodo study were not retrieved.
- No paper explicitly combining Mapillary curb detection with building footprints for width was found.
