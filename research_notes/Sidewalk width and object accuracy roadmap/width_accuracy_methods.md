# Methods for accurate automatic sidewalk width measurement from street-level imagery (and complementary data), with focus on occlusion by parked cars

Team baseline, for comparison: Washington DC on-foot Mapillary photos give MAE about 0.85 m (median 0.5 m, 49% within 0.5 m). Car-roof 360° panoramas give MAE about 1.9 m. The pipeline is Mask2Former-Vistas segmentation, then MoGe-2 metric depth, a RANSAC ground plane, inverse perspective mapping (IPM), BEV vote fusion and OSM transects. The target is MAE ≤0.3–0.5 m.

## Q1. Reported sidewalk-width accuracies (2019–2026) and how they were validated

### Takeaway
The best published street-level result is UrbanVGGT: MAE 0.252 m and 95.5% within 0.5 m, on about 300 GSV images of Washington DC. Older provider-depth GSV work reports a mean error of 0.24 m for 1–2 m sidewalks, and smartphone homography reports an average error of 0.30 m over 30 images. All of these are small, curated, near-range samples with images rejected when edges are not visible. Crowdsourced Mapillary pipelines report about 0.7–1.4 m, which is close to the team's numbers. The gap between the two groups is mostly about scale calibration, sample curation and near-range measurement, not better segmentation.

### Cited Findings
- **UrbanVGGT** (Tan, CMU and Zhang, PKU; arXiv 2603.22531, Mar 2026; published in ISPRS Archives XLIX-B2-2026, p.559). Benchmark of about 300 Google Street View images (640×640, 90° FoV) in Washington DC, with reference widths from 0.56–3.94 m. The references come from the dataset of Lieu & Guhathakurta. Full pipeline: MAE 0.252 m, RMSE 0.293 m, 49.9% within 0.25 m, 95.5% within 0.50 m. — [arXiv HTML](https://arxiv.org/html/2603.22531v1); [ISPRS Archives PDF](https://isprs-archives.copernicus.org/articles/XLIX-B2-2026/559/2026/isprs-archives-XLIX-B2-2026-559-2026.pdf)
  - The pipeline has five steps:
    1. SegFormer-B5 (Cityscapes) segmentation, keeping only the sidewalk and road classes. Images with too little sidewalk or road are discarded.
    2. VGGT in single-image mode gives a point map without metric scale.
    3. Ground plane: SVD gives a coarse plane, then a MAD-adaptive RANSAC threshold τ = clip(2.5×1.4826×MAD, 0.005, 0.05).
    4. Scale: s = h_cam / h_pred, with a fixed h_cam = 2.5 m for the GSV car.
    5. Width: a column-wise scan inside a central image band. Inner and outer edges are projected onto the plane and aggregated robustly, with plausibility and consistency rejection. — [arXiv](https://arxiv.org/html/2603.22531v1)
  - Ablation results:
    - Without camera-height scale calibration: MAE 1.571 m, 0% within 0.5 m.
    - Pinhole-only geometry: MAE 1.096 m.
    - Full image width instead of the central band: MAE 0.265 m, but only 88.5% within 0.5 m. — [arXiv](https://arxiv.org/html/2603.22531v1)
  - Camera-height sensitivity:

    | Assumed h | MAE | Bias | Within 0.5 m |
    |---|---|---|---|
    | 2.00 m | 0.384 m | −0.38 m | 65.5% |
    | 2.25 m | 0.283 m | n/a | 82.4% |
    | 2.50 m | 0.252 m | −0.055 m | 95.5% |
    | 2.75 m | 0.276 m | n/a | 85.0% |
    | 3.00 m | 0.349 m | +0.263 m | 69.1% |

    — [arXiv](https://arxiv.org/html/2603.22531v1)
  - The authors call the margin over the strongest baseline "modest". There is no occlusion-specific method. Parked vehicles are listed as a failure class and handled by "conservative rejection". Coverage in the unvalidated NYC, São Paulo and Nairobi prototype was only 38.2%, 13.2% and 7.6% of OSM segments. — [arXiv](https://arxiv.org/html/2603.22531v1)
  - The paper does not mention code or a licence. — [arXiv](https://arxiv.org/html/2603.22531v1)
- **Ning et al. 2022, CEUS** ("Converting street view images to land cover maps for metric mapping…", Penn State and South Carolina). GSV panoramas plus Google's provider depth maps were turned into metric land-cover maps in Washington DC. For sidewalks 1–2 m wide, the mean width error was 0.24 m. Slope mean error was 0.638° (another abstract gives 0.676°). The extracted network was about 2,500 km, with precision 0.8662 and recall 0.8525. — [PSU Pure](https://pure.psu.edu/en/publications/converting-street-view-images-to-land-cover-maps-for-metric-mappi/); [PSU GIScience](https://giscience.psu.edu/sidewalk-extraction-from-big-visual-data)
- **Lieu & Guhathakurta** (Environment and Planning B, 2026, vol. 53(5) pp.1129–1144, doi 10.1177/23998083251369602). Two GSV images at different pitch angles, Canny edges, then trigonometry under a flat-ground assumption, in Washington DC. Later work notes it needs two images per measurement and accurate FoV metadata. I could not find this paper's own error figures. — [RePEc](https://econpapers.repec.org/RePEc:sae:envirb:v:53:y:2026:i:5:p:1129-1144); [UrbanVGGT related work](https://arxiv.org/html/2603.22531v1)
- **MIT Senseable City Lab, "Sidewalk AI Scanner"** (Morra et al., Phil. Trans. R. Soc. A, 2024). Smartphone video with an overlaid 25 cm grid, homography to a top-down view, and PSPUNet segmentation. Accuracy "starts to lower significantly" beyond 5 m from the camera, and the stated high-accuracy range is 0.5–5 m. Across 30 images in further case studies, the average error was 0.30 m, with per-city averages of 0.14, 0.58 and 0.05 m. London was the 0.58 m case, and its errors were attributed to segmentation. — [MIT Senseable PDF](https://senseable.mit.edu/papers/pdf/20241110_Morra-etal_MappingSidewalks_RoyalSociety.pdf)
- **Project Sidewalk / RampNet issue #217** (GitHub; not peer-reviewed, but the setup is close to the team's). Mask2Former-Vistas segmentation, single-view back-projection using camera height, and width measured at the point nearest the camera. Tested on the Seoul Sidewalk Accessibility Image Dataset: 514 iPhone photos at 1.0 m camera height, with laser-measured effective width of 0.9–10.2 m. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
  - Held-out set (254 photos): clear-width MAE 0.77 m (95% CI 0.50–1.06), with bias +0.29 m mean and +0.13 m median. Total-width MAE was 0.72 m. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
  - The "below 1.2 m" flag had recall 9/9 and precision 0.41. Three-class accuracy was 0.87. Relative error by width bin was 19–30%. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
  - Assuming a level phone gave a bias of −0.66 m. Using the vanishing-point horizon of the two sidewalk edges fixed most of it. ±2° of pitch equals ±10–16% of width, while ±10% focal length changes width by less than 0.1%. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
- **Singh, TU Delft thesis (2026)** on crowdsourced Mapillary imagery. A search snippet reports width MAE of about 1.18–1.40 m, attributed to compounding segmentation, depth and GPS errors. I could not open the full text to verify this. — [TU Delft repository record](https://repository.tudelft.nl/record/uuid:47f57012-2d9b-4bca-8d72-c31ffd2db163)
- **Allahbakhshi & Harrafamoughin, GISRUK 2025** (University of Zurich). Compared street-view-based width with spatial-data-analysis width and concluded that "the spatial data analysis method provides broader coverage and more accurate width information". The landing page gives no numbers. — [Zenodo 15182508](https://zenodo.org/records/15182508)
- **Tile2Net** (Hosseini et al., CEUS 2023; aerial imagery). Detected 90% or more of sidewalks and crosswalks in Boston and Cambridge. That is a detection figure; I found no published width-error validation. — [EVL/UIC](https://www.evl.uic.edu/pubs/2703); [MIT News](https://news.mit.edu/index%2ephp/2023/open-source-tool-mapping-sidewalks-0315)
  - Amsterdam work found that training on North American data reduces transfer to other cities. — [BNAIC 2024](https://bnaic2024.sites.uu.nl/wp-content/uploads/sites/986/2024/11/Where-Not-to-Cross-the-Street.pdf)
  - UrbanVGGT notes that aerial methods need high-resolution orthorectified imagery, and that trees and overhangs occlude sidewalks from above. — [ISPRS PDF](https://isprs-archives.copernicus.org/articles/XLIX-B2-2026/559/2026/isprs-archives-XLIX-B2-2026-559-2026.pdf)
- **Mobile LiDAR.** A 3D mobile LiDAR method automatically measured sidewalk width, cross slope, grade and ramp slope against field survey on the Georgia Tech campus, reported as "accurate". I did not retrieve its numbers. — [record](https://vufind-test.katalog.k.utb.cz/SummonRecord/FETCH-LOGICAL-c282t-2a17c1b2dc59d635b068dbf678e3a420364d922a8135731343787da71c93ad983)
  - Point-cloud-based obstacle-free width (arXiv 2211.04108) found large discrepancies between full width and obstacle-free width. — [arXiv 2211.04108](https://arxiv.org/pdf/2211.04108)

### Inferences
- The team's on-foot MAE of 0.85 m and median of 0.5 m match the error level of the Seoul single-view RampNet arm (0.72–0.77 m) and of Mapillary-based theses (about 1.2–1.4 m). The sub-0.3 m results all share three things:
  1. A metric scale fixed by a known geometric quantity (camera height or provider depth), not a network's metric depth.
  2. Measurement restricted to the near field or a central band.
  3. Aggressive rejection of frames where both edges are not visible.
- Most of the published improvement is likely available by adopting these three, before any new model.
- In UrbanVGGT, MoGe-like "native metric" depth models did poorly without camera-height calibration: DepthPro 0.77 m and Metric3DV2 1.36 m. UniDepthV2 was the exception at 0.289 m. This suggests the team's MoGe-2 metric scale may be a major error source. A direct test is to rescale each frame's point map so the RANSAC plane sits at the known camera height.
- Published benchmarks report MAE on accepted images only, and UrbanVGGT's prototype covered only 8–38% of segments. When comparing to the team's numbers, coverage and rejection rate should be reported alongside MAE.

### Gaps
- I found no paper reporting Tile2Net-derived width error against surveyed widths, and no Lieu & Guhathakurta error figures (full text not accessed).
- The Singh (TU Delft) Mapillary numbers come from a search snippet only, because the fetch failed.
- The Zurich GISRUK numbers are not on the landing page.
- I found no peer-reviewed Project Sidewalk width-accuracy study. Project Sidewalk crowdsources point labels, not widths.
- I did not find accessible full texts for SideSeeing, Sidewalk Scout or Kim et al. width accuracy within the search budget.

## Q2. Occlusion handling (parked cars), and which approaches give the biggest gains

### Takeaway
No published sidewalk-width paper evaluates a dedicated parked-car occlusion method; the best systems simply reject occluded frames. The most promising remedies are aggregation across many views or capture dates, amodal or BEV layout completion trained with priors, and two-edge geometry (curb line plus building frontage) instead of counting visible pixels. Aggregation and two-edge geometry suit Beirut best, where cars sit on the sidewalk itself.

### Cited Findings
- UrbanVGGT lists parked vehicles, pedestrians, furniture, vegetation and poles as occluders that cause "boundary drift or unreliable measurement". Its only mitigations are conservative rejection, a central measurement band and plausibility checks. — [arXiv](https://arxiv.org/html/2603.22531v1)
- In the RampNet/Seoul arm, a parked truck hiding most of a sidewalk produced a false "narrow" flag. A bollard and pole cut the clear span on a 6.9 m sidewalk, giving a −5.5 m error. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
- The worst over-estimates (+9.6 m and +6.0 m) came from sidewalk pixels touching the frame edge in every near row. The near rows were then dropped, and the measurement band landed 10–14 m out, past the sidewalk. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
- In the same arm, the Vistas "sidewalk" class included paving the surveyor excluded, such as shop frontages. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
- **Amodal top-view layout** (Schulter et al., ECCV 2018, "Learning to Look around Objects"). A CNN predicts semantics and depth behind cars and pedestrians and maps them to a top-down road/sidewalk layout. It needs no labels for hidden pixels, and a refinement network trained on simulated data supplies road-layout priors. — [ECCV paper](https://openaccess.thecvf.com/content_ECCV_2018/papers/Samuel_Schulter_Learning_to_Look_ECCV_2018_paper.pdf); [arXiv 1803.10870](https://arxiv.org/pdf/1803.10870)
- **MonoLayout** (amodal BEV layout from one image) is reported to beat prior art by more than 20% on hallucinating occluded regions. This comes from a secondary summary, not the paper. — [search summary of arXiv 2208.01166 context](https://arxiv.org/pdf/2208.01166.pdf)
- **Amodal datasets:**
  - AmodalSynthDrive (synthetic) has amodal labels for 17 classes including road and sidewalk, explicitly segmented behind cars and trucks. — [arXiv 2309.06547](https://arxiv.org/pdf/2309.06547)
  - The Freiburg KITTI-360-APS and BDD100K-APS benchmarks label only "thing" classes amodally. Road and sidewalk are visible-only. — [amodal-panoptic.cs.uni-freiburg.de](https://amodal-panoptic.cs.uni-freiburg.de/)
- **Repeated traversals.** Ithaca365 notes that amodal labels for background classes such as road are easy to obtain from repeated routes, because parked cars move between passes. — [search summary](https://amodal-panoptic.cs.uni-freiburg.de/) (Ithaca365 statement from search snippet; primary not fetched)
- **Street view filling aerial occlusion.** Combining street-view with aerial detections restored occluded sidewalks and linked 20% of dangling segments (Ning et al. 2021). — [MTU Digital Commons](https://digitalcommons.mtu.edu/michigantech-p/14686)
- **Beirut context:**
  - On one street (Salah Labaki, Al Hikmeh), about 25 cars were parked on a 315 m sidewalk, one every 12.6 m. — [L'Orient Today](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html)
  - The MIT/AUB Community Streets study estimated that about 17% of sidewalks had permanent obstructions and about 20% were narrower than 1.2 m. Their sidewalk data came from Mapillary, prior studies and in-person observation, because GSV is very limited in Beirut. — [Community Streets report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf); [MIT LCAU](https://lcau.mit.edu/node/80)

### Inferences
- **Two-edge formulation.** Width = distance from the curb line (road/sidewalk height step) to the building frontage or back-of-walk. The team already aligns OSM building outlines, which supplies the inner edge. This turns the problem into locating one curb line per block face. A curb line is a long straight feature that can be fitted by robust 1-D regression along the transect from the few unoccluded gaps between cars, then interpolated. With cars every 12.6 m in Beirut, gaps of a few metres should usually exist (an untested assumption).
  - For Beirut, where cars sit on the sidewalk, the car footprint should be counted as sidewalk area, not obstacle. That is one more reason to measure between edges rather than counting visible sidewalk pixels.
- **Occlusion-aware BEV fusion.** In the BEV vote grid, cells hidden by a car (ray passes through a car pixel before reaching the ground) should be "unknown", not "not sidewalk", so votes from other frames and dates can fill them. The DaF-BEVSeg-style per-cell occlusion probability (from search results) is a learned version of this.
- **Multi-date fusion** is the cheapest real fix (Ithaca365 logic): parked cars move between capture dates, the curb does not.
- **Opposite-side panoramas** see the far sidewalk's curb face and the car roofs, not the ground behind cars. They likely help locate the curb line and frontage but not the ground behind cars. This is an inference only; I found no study.
- **Learned amodal BEV completion** (Schulter, MonoLayout) has evidence only on driving datasets and synthetic priors. It would need fine-tuning to irregular Beirut layouts and risks hallucinating regular widths. I would rank it after the geometric fixes.

### Gaps
- I found no quantitative study of sidewalk-width error versus parked-car occlusion rate, and no published comparison of multi-year fusion, opposite-side views or amodal completion for width.
- I found no amodal dataset with sidewalk-class completion on real (not synthetic) imagery.

## Q3. Better geometry: SfM, feed-forward reconstruction, camera-height and curb scale cues, licences and hardware

### Takeaway
The single biggest documented gain is metric-scale calibration from known camera height. In UrbanVGGT it cut MAE from 1.571 m to 0.252 m, and width error scales roughly linearly with height error. Among backbones on the same DC benchmark, VGGT (0.252), π³ (0.324), MapAnything (0.334) and UniDepthV2 native metric (0.289) clearly beat native-metric DepthPro, Metric3DV2, ZoeDepth and DepthAnythingV2 (0.77–1.71 m). MoGe was not tested. Mapillary's own SfM point clouds are downloadable via the API, but their format and accuracy are poorly documented.

### Cited Findings
- **Scale calibration from camera height** (UrbanVGGT): MAE drops from 1.571 m to 0.252 m. A ±0.5 m height error (2.0 or 3.0 m instead of 2.5 m) raises MAE to 0.38/0.35 m and bias to −0.38/+0.26 m. — [arXiv](https://arxiv.org/html/2603.22531v1)
- RampNet issue notes:
  - A 10% camera-height error gives roughly a 10% width error, and pose error mostly cancels.
  - Range along the ray is poorly resolved: at 2.5 m camera height, 1° of pitch is about 0.3 m of ground at 6 m range and about 1.6 m at 15 m.
  - Projecting a 15 cm curb onto the road plane instead of the sidewalk plane overstates width by about 6%, so fit the sidewalk plane, not the road plane.
  - Per-rig GSV camera height improved placement error from 6.09° to 3.92°.
  — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
- **Backbone comparison on the UrbanVGGT DC benchmark**, same downstream pipeline, MAE / within 0.5 m — [arXiv](https://arxiv.org/html/2603.22531v1):
  - Native metric, no calibration: UniDepthV2 0.289 m / 83.3%; MapAnything 0.463 m / 60.5%; DepthPro 0.768 m; ZoeDepth 1.067 m; Metric3DV2 1.361 m; DepthAnythingV2-metric 1.712 m.
  - Monocular depth with pinhole unprojection and camera-height calibration: Metric3DV2 0.417 m; UniDepthV2 0.436 m; ZoeDepth 0.583 m; DepthAnythingV2 0.628 m; DPT 0.701 m; DepthPro 0.718 m.
  - Point-map models with calibration: VGGT 0.252 m / 95.5%; π³ 0.324 m / 79.6%; MapAnything 0.334 m / 78.0%; CUT3R 0.672 m.
- **Mapillary API v4 3D data:**
  - `sfm_cluster` is an object {id, url}. The URL serves zlib-compressed point-cloud data that a user decompressed into a readable PLY. — [Mapillary forum](https://forum.mapillary.com/t/api-mesh-and-point-cloud-format/6664); [Mapillary API v4 blog](https://blog.mapillary.com/update/2021/06/23/getting-started-with-the-new-mapillary-api-v4.html)
  - `mesh` has no official format description. The mapillary-js typings describe faces and vertices, read by a protobuf reader. — [forum](https://forum.mapillary.com/t/api-mesh-and-point-cloud-format/6664); [mapillary-js typings](https://app.unpkg.com/mapillary-js@4.1.2/files/dist/mapillary.d.ts)
  - `computed_geometry` is the SfM-refined position. `atomic_scale` is the "scale of atomic reconstruction". Both are absent for images without 3D processing. — [API v4 blog](https://blog.mapillary.com/update/2021/06/23/getting-started-with-the-new-mapillary-api-v4.html); [mapillary-js typings](https://app.unpkg.com/mapillary-js@4.1.2/files/dist/mapillary.d.ts)
  - Forum users also ask how to identify images whose geometry was optimized together. — [forum thread](https://forum.mapillary.com/t/api-identify-images-whose-geometry-was-optimized-together/10070)
- **Licences:**
  - VGGT code was relicensed on 29 Jul 2025 to allow commercial use, excluding military use. Only the VGGT-1B-Commercial checkpoint (gated by an application form) allows commercial use; the original VGGT-1B weights remain non-commercial. — [facebookresearch/vggt](https://github.com/facebookresearch/vggt)
  - VGGT runtime: under 1 s per scene. A May 2026 update lets it run 2–3× more frames in the same GPU memory. bf16 on Ampere+ GPUs, fp16 otherwise. — [facebookresearch/vggt](https://github.com/facebookresearch/vggt)
  - MapAnything's pre-trained model is released under Apache 2.0. — [MapAnything arXiv 2509.13414](https://arxiv.org/pdf/2509.13414v3)
  - Depth Anything 3 licensing differs by checkpoint. DA3-Giant and DA3-Large are CC BY-NC 4.0 (non-commercial); DA3-Base (0.12B) is Apache 2.0. — [awesome.ecosyste.ms DA3 listing](https://awesome.ecosyste.ms/projects/github.com%2FByteDance-Seed%2FDepth-Anything-3); [DA3 arXiv](https://arxiv.org/pdf/2511.10647v1)
- **Curb height as a scale cue.** Curbs are usually lower than 0.25 m. — [arXiv 1610.04673](https://arxiv.org/pdf/1610.04673)
- **UAV-SfM curb mapping** reached 2 cm RMSE on check points (manholes, not curb lines), which shows multi-view photogrammetry can reach centimetre level. — [ISPRS 2024](https://isprs-archives.copernicus.org/articles/XLVIII-2-W8-2024/483/2024/isprs-archives-XLVIII-2-W8-2024-483-2024.pdf)

### Inferences
- **Highest-value change:** replace MoGe-2's absolute scale with scale = known camera height / fitted-plane distance.
  - For car-roof panoramas the mount height is roughly constant per sequence. It can be estimated once per sequence from a few frames with a reliable ground plane, or from Mapillary `atomic_scale` plus SfM.
  - For on-foot phones, height varies (about 1.0–1.6 m). There, per-sequence self-calibration is needed, for example from the median plane distance under an assumed 1.4 m, or from known-size objects.
  - Pitch from the vanishing point of the sidewalk edges also matters for phones (RampNet).
- **Measure near the camera.** Restrict IPM votes to about 2–8 m ground range (Senseable: 0.5–5 m high-accuracy range; 1° ≈ 0.3 m at 6 m versus 1.6 m at 15 m). Weight votes by inverse range uncertainty, rather than taking all sidewalk pixels into the 10 cm BEV.
- **Multi-view.** Feed-forward point maps over short sequences (VGGT-1B-Commercial or MapAnything Apache-2.0), registered with OpenSfM poses and GPS, should beat per-frame monocular IPM. UrbanVGGT used single-image mode only, and I found no published multi-view width benchmark.
- **8 GB GPU:** VGGT-1B in bf16/fp16 should fit a handful of 518-px frames (a weights-size estimate, not a published figure). MapAnything and DA3-Base are lighter options with permissive licences. DA3-Large/Giant and the original VGGT-1B weights are non-commercial. UniDepthV2's licence was not verified here (commonly reported as CC BY-NC; verify).

### Gaps
- I found no published accuracy assessment of Mapillary `sfm_cluster` or `mesh` geometry, or of `atomic_scale`, for metric measurement.
- I found no published multi-view (VGGT, MASt3R, MapAnything sequences) sidewalk-width benchmark, and MoGe-2 is absent from all width benchmarks found.
- I did not retrieve exact VRAM figures for VGGT or MapAnything at N frames, or the UniDepthV2 and MASt3R/DUSt3R licences (MASt3R/DUSt3R are believed CC BY-NC-SA, unverified this session).

## Q4. Curb detection specifically (images and aerial)

### Takeaway
Curb-line detection is well studied for LiDAR and autonomous driving, and partly for aerial orthoimagery, but there is almost no public street-level image dataset for curb lines. I found no published centimetre-level curb-line position error from deep learning on aerial or street imagery. Curb ramps, not curb lines, have the best street-level image data (Project Sidewalk, RampNet).

### Cited Findings
- **RampNet** (arXiv 2508.09415, 2025). Curb-ramp detection data was auto-generated from GSV panoramas using government ramp locations. Labels reached 94.0% precision and 92.5% recall against manual labels, and the ConvNeXt V2 detector reached 0.9236 AP. Project Sidewalk is described as one of the only public sources for image-based curb-ramp detection. — [arXiv 2508.09415](https://arxiv.org/html/2508.09415v1)
- **CurbNet** (arXiv 2403.16794, 2024). Introduces the 3D-Curb LiDAR dataset on SemanticKITTI (7,100 frames). It notes that nuScenes, KITTI and SemanticKITTI have no curb annotations, and post-processing gave +4.5 points precision. — [arXiv 2403.16794](https://arxiv.org/pdf/2403.16794)
- **Semi-automatic curb labelling in LiDAR sequences** (Bai et al., arXiv 2110.03968). — [arXiv](https://arxiv.org/pdf/2110.03968)
- **Mobile-LiDAR curb extraction** (Xu et al., 2016). Completeness 78.62% and correctness 83.29%. Curb-to-curb width checked against Google Earth with a "mean square error 2.67", units unclear in the snippet. — [arXiv 1610.04673](https://arxiv.org/pdf/1610.04673)
- **Aerial:**
  - DLR (Brunswick) trained a Swin transformer for curbstone segmentation on airborne imagery fused with reference curb data, then vectorized it. The cited ~10 cm accuracy refers to the bundle adjustment, not to the curb lines. — [DLR elib PDF](https://elib.dlr.de/196561/1/DP169-latex.pdf)
  - iCurb (imitation learning) outputs a curb graph from orthoimages. — [arXiv 2103.17118](https://arxiv.org/pdf/2103.17118)
  - An aerial dataset with sidewalk, crossing and corner annotations exists (arXiv 2303.02323). — [arXiv 2303.02323](https://arxiv.org/pdf/2303.02323)
- **Mapillary Vistas segmentation:** the RampNet arm used Mask2Former-Vistas, which has a curb class. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
  - The Vistas sidewalk class may include frontage paving. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)

### Inferences
- With Vistas classes the team can take the curb edge from the visible "Curb" pixels (curb tops and faces), or from the sidewalk–road boundary in the 3D point map. In 3D the curb is a height step of about 0.1–0.25 m, and the vertical resolution of feed-forward point maps at 3–8 m may resolve it.
- A curb line fitted per block face from the unoccluded fragments (Q2), then intersected with transects, is likely more robust than per-pixel sidewalk votes.
- For Beirut, where no ground truth exists, a small field-measured validation set (tape or laser at about 100 transects) is needed, because no published curb or sidewalk model has been validated in the region.

### Gaps
- I found no public street-level image dataset with curb-line annotations and no reported curb-line position RMSE from images.
- I found no OpenSidewalks curb-accuracy publication within the search budget.

## Q5. Measurement definition (total vs clear vs through-zone) and standards

### Takeaway
Standards define the critical quantity as clear width of the pedestrian access route, excluding the curb: PROWAG 1.2 m minimum, and UK practice 2 m desirable with 1.2 m minimum clear between obstacles. Most ground-truth datasets (planimetric polygons) are total paved width and rarely say which. Width papers rarely specify the definition either. This makes cross-study MAE comparisons loose.

### Cited Findings
- **PROWAG (US Access Board):** continuous clear width of pedestrian access routes is 48 in (1220 mm) minimum, "exclusive of the width of any curb". Where clear width is under 60 in, a 60×60 in (1525 mm) passing space is required at most every 200 ft (61 m). Section numbering differs between the NPRM and the final rule (R302.3 versus R302.2). — [Corada R302.3](https://www.corada.com/documents/36-cfr-part-1190-NPRM/r302-3); [Federal Register 2023-16149](https://public-inspection.federalregister.gov/2023-16149.pdf); [Access Board](https://www.access-board.gov/prowag/proposed/planning-and-design-for-alterations/chapter5/)
- **UK guidance:** 2 m lets two wheelchair users pass, and 1.2 m is the minimum path width. — [Sensory Trust](https://www.sensorytrust.org.uk/resources/guidance/paths-and-routes)
  - A UK planning document requires at least 1.2 m clear between street furniture and obstacles, with 2 m total width for the P1/P2 categories up to 30 mph. — [St Albans CD10 document](https://stalbans.gov.uk/sites/default/files/documents/publications/planning-building-control/Bricket%20Wood%20Inquiry/CD10/10.3.2%20pd-3.-chapter-3-planning-walking-infrastructure.pdf)
- **NYC Street Design Manual** defines a "clear path". — [NYC Street Design](https://www.nycstreetdesign.info/node/1888)
- **Project Sidewalk / Seoul data:**
  - Total-width and clear-width MAEs were about equal (0.72 versus 0.77 m), so subtracting obstacle classes added no information. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
  - None of the candidate ground-truth sources say whether width is total or clear: São Paulo GeoSampa (491k block-face polygons with min/mean/max width), Richmond planimetrics, Bend and Annapolis. — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
  - The Seoul set uses laser-measured "effective width". — [GitHub issue](https://github.com/ProjectSidewalk/RampNet/issues/217)
- **Sidewalk AI Scanner** defines width as "the measure of space available for pedestrian traffic", with obstructions and temporary obstacles as separate features that reduce it. — [MIT Senseable PDF](https://senseable.mit.edu/papers/pdf/20241110_Morra-etal_MappingSidewalks_RoyalSociety.pdf)
- **Beirut:** Community Streets used 1.2 m as the "minimum comfortable passing width" and found about 20% of sidewalks below it. — [Community Streets report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)

### Inferences
- The DC planimetric polygons are most likely total paved width, from curb face to back-of-walk. The team's "longest contiguous sidewalk run" is a visible-pixel width that falls between total and clear. Matching DC ground truth needs curb-to-back-of-walk (two-edge) geometry. Beirut accessibility reporting should output two figures:
  - total width (curb line to frontage);
  - clear width, after subtracting permanent obstacles (trees, poles, stairs/ramps encroaching) and, as a separate attribute, typical parked-car encroachment.
- PROWAG excludes the curb itself from clear width. A 0.15–0.20 m curb top counted as sidewalk is a systematic bias at the target ±0.3 m level.

### Gaps
- I found no Lebanese or Arab-region sidewalk width standard (Lebanese DGU or Beirut municipality, or Gulf guidelines such as the Abu Dhabi Urban Street Design Manual) within the budget. This remains unverified.
- I did not retrieve the exact wording of the UK Inclusive Mobility (2021) footway definition.
- The DC planimetric sidewalk polygon definition (total versus clear, curb inclusion) was not checked against DC GIS metadata.
