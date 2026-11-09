# Detecting Sidewalk Obstructions, Accessibility Barriers and Surface Condition from Street-Level Imagery (2019-2026): Models, Datasets, Audit Tools, and Transferability to Lebanon

Research cut-off: 2026-11-06. About 24 search/fetch calls. Several figures come from search-result summaries rather than full-text reads; these are marked "(snippet-level)". Lebanese target classes are: cars and motorcycles parked on sidewalks, diesel generators, street vendors, shop goods and cafe furniture, kiosks, utility poles, low tangled wires, trees, steps or ramps into buildings, construction debris, broken tiles, and missing sidewalks.

## 1. Project Sidewalk (UW Makeability Lab): label types, API, code licence, ML models, deployments, and whether Beirut could be added

### Takeaway
Project Sidewalk is the most mature open audit tool and data pipeline here. The code is MIT, the data is CC0, it has a public API, and a city can be onboarded "in an afternoon" by emailing the team. It already runs in Global South cities (Mexico, Chile, Ecuador, Brazil, India) but nowhere in the Middle East. Its coarse label types (Obstacle, Surface Problem, No Sidewalk) cover the Lebanese problems only at a high level. Its AI validators lose accuracy in non-US deployments, so Beirut would need local labels and re-validation.

### Cited Findings
**Label types and tags**
- Label types: Curb Ramp and Crosswalk (positive); Missing Curb Ramp, Obstacle and Surface Problem (negative); Pedestrian Signal and No Sidewalk (presence-only). Tags can be customised per city through a Label Tags API (`/v3/api-docs/labelTags`). — [Project Sidewalk API docs](https://sidewalk-dc.cs.washington.edu/api)
- The tagger dataset defines 33 fine-grained "classes" (tags). The abstract names bumpy, brick/cobblestone, cracks, height difference (uplifts), narrow, uneven/slanted, pole, sign, missing tactile warnings on curb ramps, and grass on sidewalks. — [sidewalk-tagger-ai GitHub](https://github.com/ProjectSidewalk/sidewalk-tagger-ai)

**Open data API and licences**
- Data is dedicated to the public domain under CC0 1.0. Source imagery (GSV or Mapillary, per the `pano_source` field) is not included and stays under the provider's terms. — [API docs](https://sidewalk-dc.cs.washington.edu/api)
- The v3 API is a "preview", so breaking changes are possible. Endpoints include:
  - Metadata: Cities, Label Types, Label Tags, Street Types.
  - Data: Raw Labels, Label Clusters (recommended), Streets, Sidewalk Presence, Street Grade, Regions, Validations, Label Edits.
  - AccessScore: Streets, Intersections, Regions.
  - Stats.
  - Output formats: GeoJSON (default), CSV, shapefile, GeoPackage. — [API docs](https://sidewalk-dc.cs.washington.edu/api)
- Code: the main web app (SidewalkWebpage) is MIT-licensed. — [SidewalkWebpage GitHub](https://github.com/ProjectSidewalk/SidewalkWebpage)
- A GitHub issue reports that `/v3/api/cities` publishes the URLs of about 19 deployments that are not publicly launched. — [Issue #5259](https://github.com/ProjectSidewalk/SidewalkWebpage/issues/5259)

**Deployments**
- The README says "50+ cities across 10 countries" and names the US, Canada, Chile, India, Mexico, Ecuador, the Netherlands, Switzerland and New Zealand. — [SidewalkWebpage GitHub](https://github.com/ProjectSidewalk/SidewalkWebpage)
- The API city list as fetched includes 33 US cities plus:
  - Washington DC
  - São Paulo (Brazil)
  - Burnaby (Canada)
  - Rancagua and Santiago (Chile)
  - Cuenca (Ecuador)
  - Bayonne (France)
  - Chandigarh (India)
  - Mexico City, La Piedad and San Pedro Garza García (Mexico)
  - Amsterdam (Netherlands)
  - Auckland (New Zealand)
  - Source: [API docs](https://sidewalk-dc.cs.washington.edu/api)
- Neither source lists Taiwan, and I found no Middle East or North Africa deployment. — [README](https://github.com/ProjectSidewalk/SidewalkWebpage); [API docs](https://sidewalk-dc.cs.washington.edu/api)
- A 2024 article cited "20 cities across eight countries", which conflicts with the README's 50+/10. The README is probably newer. — [Tandfonline 2024](https://www.tandfonline.com/doi/full/10.1080/10790268.2024.2341553)

**Adding a new city such as Beirut**
- The "Onboarding a city" doc builds streets and regions from open data, which can be done "in an afternoon". To get a hosted server, read the wiki page "Considerations when Preparing for and Deploying to New Cities" and email sidewalk@cs.uw.edu. Self-hosting is also possible. — [README](https://github.com/ProjectSidewalk/SidewalkWebpage)
- `pano_source` can be `gsv` or `mapillary`, so the tool can use Mapillary imagery as well as Google Street View. — [API docs](https://sidewalk-dc.cs.washington.edu/api)

**ML models trained on Project Sidewalk labels**
- **Weld et al., ASSETS 2019 (Best Student Paper).**
  - Approach: a modified ResNet-18 using image plus non-image (geographic) features, trained on more than 300,000 DC crowd labels. It covered two tasks: validating crowd labels and auto-labeling new panoramas. Classes were curb ramp, missing curb ramp, obstruction and surface problem. — [SIGACCESS](https://www.sigaccess.org/2019/11/2019-best-student-paper/)
  - Auto-labeling results: 47.0% overall precision and 41.2% recall; curb ramp best at 89.8% precision and 48.9% recall. These figures come from a third-party review page, so they are unverified against the PDF. — [a11y-paradise review](https://a11y-paradise.onrender.com/reviews/69bc12412846a9204f821b87)
  - Code: `ProjectSidewalk/sidewalk-cv-assets19`. — [Makeability project page](https://makeabilitylab.cs.washington.edu/project/deeplearningforsidewalks/)
- **Follow-up papers.** These are listed on the project page; I did not read their results.
  - Hosseini et al. 2022, CVPR AVA workshop: "Towards Global-Scale Crowd+AI Techniques…" (arXiv 2206.13677).
  - Duan et al. 2022, ASSETS: tests larger noisy training sets against smaller crowd-validated sets, and cross-city generalization; a snippet says cross-city looks "promising".
  - Liu et al. 2024, ASSETS. — [Makeability project page](https://makeabilitylab.cs.washington.edu/project/deeplearningforsidewalks/); [Duan PDF](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **Liu et al., ASSETS 2024** ("Towards Fine-Grained Sidewalk Accessibility Assessment with Deep Learning", DOI 10.1145/3663548.3688531).
  - Fine-tunes DINOv2 and CLIP-ViT for multi-label tag classification.
  - Data: about 24k cleaned images and about 87k uncleaned crowd images, both on Hugging Face.
  - Findings: high precision and recall for some tags (missing tactile warnings, grass); noisier, larger data hurt performance. Per-tag numbers appear only in an image.
  - Licence: Apache-2.0. — [sidewalk-tagger-ai](https://github.com/ProjectSidewalk/sidewalk-tagger-ai)
- **sidewalk-validator-ai** (production AI validation; no paper yet).
  - Method: one DINOv2-Large classifier per label type, with Depth Anything V2 for crop sizing. It predicts whether a crowd label is correct.
  - Round-3 models in production since 2026-10-27. AUC on 13,144 held-out crops: CurbRamp 0.953, NoCurbRamp 0.920, Obstacle 0.873, SurfaceProblem 0.855, Crosswalk 0.972; macro-AUC 0.915.
  - Transfer: on unseen deployments SurfaceProblem drops to 0.710, and the non-US deployment is the weakest for every type except Crosswalk.
  - VLM baseline: the best open VLM (Gemma 4 31B, 8-shot) reached macro-AUC 0.775.
  - Licences: code MIT; dataset and model licences unsettled (issue #2); the HF CurbRamp dataset upload is mistakenly a copy of Crosswalk. — [sidewalk-validator-ai](https://github.com/ProjectSidewalk/sidewalk-validator-ai)
- **RampNet** (O'Meara et al., ICCV 2025 CV4A11y workshop, arXiv 2508.09415).
  - Converts government curb-ramp location data into more than 210k auto-labeled GSV panoramas, then trains a modified ConvNeXt V2 detector.
  - Results (snippet-level): dataset 94.0% precision and 92.5% recall; detector AP 0.9236.
  - Code: ProjectSidewalk/RampNet. — [arXiv](https://arxiv.org/abs/2508.09415v1); [ICCVW](https://openaccess.thecvf.com/content/ICCV2025W/CV4A11y/html/OMeara_RampNet_A_Two-Stage_Pipeline_for_Bootstrapping_Curb_Ramp_Detection_in_ICCVW_2025_paper.html)
- **LabelAId** (2024): just-in-time AI interventions to improve crowd labeling quality. It notes the most common Project Sidewalk error is labeling driveways as curb ramps. — [arXiv 2403.09810](https://arxiv.org/pdf/2403.09810)

### Inferences
- **Beirut is technically feasible.** The tooling is open (MIT/CC0), can use Mapillary imagery (useful where GSV is sparse or outdated), and the team accepts new-city requests by email. Whether GSV coverage in Beirut is adequate is not verified here.
- **Lebanese classes need local tags.** Under the per-city tag system, the Obstacle type could carry tags such as `parked car`, `parked motorcycle`, `generator`, `vendor/kiosk`, `shop goods/café furniture`, `low wires`, `construction debris`, `steps into building`, and Surface Problem could carry `broken tiles`. That would generate CC0 labels usable for training detectors.
- **Expect lower AI accuracy initially.** Validator AUC is already lower for Obstacle and Surface Problem than for curb ramps and crosswalks, and drops further outside the US. Beirut will likely need a local validation set before AI votes are enabled.
- **Low priority for Lebanon:** curb-ramp work (RampNet), since Beirut has no equivalent government curb-ramp inventory to bootstrap from.

### Gaps
- Exact per-class Weld 2019 metrics are not verified from the PDF.
- Duan 2022 cross-city numbers and Liu 2024 per-tag scores were not retrieved.
- The full standard tag list for Obstacle and Surface Problem was not retrieved.
- I could not confirm whether a Taiwan deployment exists or which Swiss city is deployed.
- No information on GSV coverage or recency in Lebanon.

## 2. Labelled datasets: sidewalk scenes, obstacles, curb ramps, surface damage, informal streets

### Takeaway
No public dataset covers Lebanese-style obstructions (generators, vendors, spilled shop goods, low wires, cars parked on sidewalks) as explicit classes. The closest options are:
- Mapillary Vistas v2 (124 classes, including curb cut, utility pole and street furniture).
- The new ROD dataset (25 pedestrian-view obstacle classes, MIT licence, partly from Tehran).
- Project Sidewalk's CC0 labels and Hugging Face crops.
- SideGuide (Korea, non-commercial).
- SideSeeing (Brazil/US video).

Surface-damage datasets are almost all road-asphalt rather than sidewalk tiles.

### Cited Findings
**Street-scene segmentation**
- **Mapillary Vistas v2.0:** 25,000 high-resolution images, 124 semantic classes (70 instance-annotated), up from 66 in v1.2. — [Mapillary blog: Vistas 2.0](https://blog.mapillary.com/update/2021/01/18/vistas-2-dataset.html); [Dataset Ninja](https://datasetninja.com/mapillary-vistas-dataset)
  - Classes include 'Curb Cut' and 'Utility Pole', alongside 'Traffic Sign Frame', 'Crosswalk - Plain' and 'Parking'. The source is the mmseg class list, which is secondary. — [HF mmseg mapillary.py](https://huggingface.co/spaces/KyanChen/TTP/blob/refs%2Fpr%2F1/mmseg/datasets/mapillary.py)
  - Licence sources conflict:
    - The ICCV 2017 paper says CC-BY-SA. — [Neuhold ICCV 2017](https://openaccess.thecvf.com/content_ICCV_2017/papers/Neuhold_The_Mapillary_Vistas_ICCV_2017_paper.pdf)
    - Dataset Ninja says CC BY-NC-SA 4.0. — [Dataset Ninja](https://datasetninja.com/mapillary-vistas-dataset)
    - TechCrunch 2017 says it is free for academic and commercial research, but commercial products need a paid licence. — [TechCrunch](https://techcrunch.com/2017/05/03/mapillary-open-sources-25k-street-level-images-to-train-automotive-ai-systems)
- **PathwayBench (2024):** segmentation of corner bulb, sidewalk and crossing (other annotated classes such as road, building and tree are folded into background), plus OpenSidewalks pathway graphs in GeoJSON. Covers Seattle, Portland, DC and others. Related: the APE dataset uses the same three classes. — [arXiv 2407.16875](https://arxiv.org/html/2407.16875v1); [APE arXiv 2303.02323](https://arxiv.org/pdf/2303.02323)

**Pedestrian-view obstacle detection**
- **ROD-Dataset (arXiv 2611.00681, 2026).**
  - Size: 24,326 images and 40,195 boxes (19,186 train / 3,511 val / 1,629 test), YOLO format.
  - 25 classes: Bike, Building, Car, Person, Stairs, Traffic sign, Electrical Pole, Road, Motorcycle, Dustbin, Dog, Manhole, Tree, Guard rail, Pedestrian crosswalk, Truck, Bus, Bench, Traffic Cone, Fire hydrant, Traffic Barrel, Plant Pot, Electrical Box, Chair, Bicycle Rack.
  - Sources: merged from 29 Roboflow Universe sets (mostly CC BY 4.0) plus original eye-level imagery from Tehran (Iran) and Toronto.
  - Licence: MIT, on Kaggle and HF. No vendor or construction class. — [ROD arXiv](https://arxiv.org/html/2611.00681)
- **PEDESTRIAN (arXiv 2512.19190):** egocentric phone-video dataset, 29 obstacle types, 340 videos. — [arXiv](https://arxiv.org/html/2512.19190)
- **OOD dataset (Springer):** 10,000 images and 29,779 instances across 22 outdoor obstacle classes (bench, trash can, fire hydrant, etc.); YOLOv5/v8 trained. — [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-031-48573-2_57) (snippet-level)
- **WOTR:** 13,928 images, 15 obstacle classes plus 5 road-judging classes (blind walking). — [Academia.edu](https://www.academia.edu/115136569/A_dataset_for_the_visually_impaired_walk_on_the_road) (snippet-level)
- **TFP-YOLO:** Beijing sidewalks, 8 classes (pedestrian, car, pole, traffic cone, etc.), released on GitHub. — [PMC12473299](https://pmc.ncbi.nlm.nih.gov/articles/PMC12473299/) (snippet-level)
- **SideGuide (KAIST, IROS 2020).**
  - Size: about 350K images with boxes, 100K with polygon masks, 180K stereo pairs. Target classes were chosen by interviewing people with impairments.
  - Access: gated, non-commercial research only, under Korean law.
  - A 2024 paper cites more than 490K images, which conflicts with the 2020 figures. — [KAIST EE](https://ee.kaist.ac.kr/en/ai-in-signal/18498/); [project page](https://ytaek-oh.github.io/sideguide); [arXiv 2409.11164](https://arxiv.org/pdf/2409.11164)
- **SideSeeing (2024, USP/UIC/MIT).** Chest-mounted phone video plus IMU and GPS: about 12 km around 9 hospitals in Brazil and the USA, about 3 h and 325k frames. Includes a 68-element sidewalk-scene taxonomy. Public at sites.usp.br/sideseeing. — [arXiv 2407.06464](https://arxiv.org/html/2407.06464v2)

**Project Sidewalk-derived image data**
- Tagger data: about 24k validated and about 87k unvalidated crops on HF, Apache-2.0. — [sidewalk-tagger-ai](https://github.com/ProjectSidewalk/sidewalk-tagger-ai)
- Validator crops on HF (2025-08 uploads), licence unsettled. — [sidewalk-validator-ai](https://github.com/ProjectSidewalk/sidewalk-validator-ai)
- Field-measured accessibility data: 514 Seoul sidewalk images with measured effective width, longitudinal and cross slope, and pavement grade (A–E), from the 2026 VLM paper. The authors say they release the data; no licence stated. — [arXiv 2609.17882](https://arxiv.org/abs/2609.17882)

**Surface damage**
- Found only road-pavement datasets:
  - PaveDistress (2024, Chinese highway; cracks, patches, potholes). — [Mendeley](https://data.mendeley.com/datasets/f46zt2g83x)
  - A 2024 set of 7,099 images with 13 defect types. — [search summary, Construction and Building Materials 2024 via Mendeley](https://data.mendeley.com/datasets/yb65trwbd8) (snippet-level)
  - PavementDamagesG-7 (Colombia). — [Data in Brief / DOAJ](https://doaj.org/article/6e3bb294385f4d5e9dbdb95b186797c0) (snippet-level)
- I found no sidewalk-tile damage dataset. Project Sidewalk Surface Problem tags (cracks, height difference, bumpy, brick/cobblestone, uneven) are the closest sidewalk-specific source. — [sidewalk-tagger-ai](https://github.com/ProjectSidewalk/sidewalk-tagger-ai)

**Parked on sidewalk**
- No street-view sidewalk-parking dataset found. Related work:
  - In-vehicle camera illegal-parking detection with a dataset of more than 10k images in 7 categories. — [Glasgow eprint](https://eprints.gla.ac.uk/272004/1/272004.pdf)
  - CCTV SSD-based detection reporting 99% accuracy. — [arXiv 1710.02546](https://arxiv.org/pdf/1710.02546)
  - A patent on detecting e-scooters obstructing the middle of a sidewalk. — [USPTO 11783574](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11783574)

### Inferences
- **For Lebanon, a hybrid works best:**
  - Vistas-trained segmentation to get the sidewalk, curb, pole and vehicle masks.
  - COCO or ROD detectors for car, motorcycle, chair, plant pot, electrical box, stairs, tree and pole.
  - Mask–box overlap logic for "car or motorcycle on sidewalk" and "chair or plant pot or goods on sidewalk".
  - Generator, vendor cart, kiosk, low wires, construction debris and broken tiles will need new labels.
- **ROD is the most transferable obstacle set:** permissive MIT licence, Middle Eastern imagery from Tehran, and classes such as Electrical Box, Chair, Plant Pot and Stairs.
- **Licence caution:** Vistas (licence ambiguous, possibly NC) and SideGuide (non-commercial) may restrict a commercial or municipal product. Vistas' licence must be checked on the official page.

### Gaps
- The full official Vistas v2 class list and licence could not be fetched (the official page returned an empty render; the blog fetch failed).
- SideGuide's class list was not retrieved.
- Cityscapes and ADE20K class lists and licences were not researched in this pass. Cityscapes includes sidewalk, pole and vehicles, but that is not sourced here.
- Roboflow Universe "sidewalk" and "curb ramp" datasets (for example ACAMAI) were not individually verified.
- No datasets found for Indian, Brazilian or Chinese informal-street obstacles beyond those above, and none for an "ALLEY" informal-street dataset.
- No dataset with diesel generators, street vendors or overhead low wires as classes was found.

## 3. Models: detectors, segmenters, open-vocabulary detectors and VLMs used for sidewalk auditing, with accuracy vs human or ground truth

### Takeaway
- Fine-tuned, task-specific models clearly beat zero-shot ones on sidewalk tasks:
  - RampNet F1 0.855 vs Gemini 0.634 vs OWLv2 0.184 on curb ramps.
  - DINOv2 validators macro-AUC 0.915 vs best open VLM 0.775.
- VLMs are not yet reliable for measured attributes. In a 2026 Seoul study, no attribute reached compliance-grade precision, and pavement-condition predictions were uninformative.
- Small YOLO models reach about 0.88 mAP@50 on the ROD pedestrian-view obstacle set.

### Cited Findings
**YOLO family on obstacles (ROD test split)**
- mAP@50 and mAP@50:95:

  | Model | mAP@50 | mAP@50:95 |
  |---|---|---|
  | YOLOv8n | 0.876 | 0.718 |
  | YOLOv9t | 0.882 | 0.750 |
  | YOLOv10n | 0.871 | 0.726 |
  | YOLO11n | 0.880 | 0.735 |
  | YOLO12n | 0.878 | 0.739 |
  | YOLO26n | 0.874 | 0.742 |

- Per-class recall across the six models: Car 0.794–0.842, Motorcycle 0.676–0.784, Electrical Pole 0.881–0.929, Tree 0.837–0.860, Stairs 0.798–0.907. — [ROD arXiv](https://arxiv.org/html/2611.00681)

**Project Sidewalk models** (details in section 1)
- DINOv2-Large validators: Obstacle AUC 0.873, SurfaceProblem 0.855, falling to 0.710 for SurfaceProblem on unseen cities. — [sidewalk-validator-ai](https://github.com/ProjectSidewalk/sidewalk-validator-ai)
- RampNet ConvNeXt V2: AP 0.9236 (snippet-level). — [arXiv 2508.09415](https://arxiv.org/abs/2508.09415v1)

**Open-vocabulary detectors**
- **On curb ramps (Project Sidewalk RampNet issue #52, an internal log, not peer-reviewed):**
  - Best-sweep F1: RampNet 0.855, Gemini 0.634, OWLv2 0.184. Grounding DINO did worse than the chat VLMs.
  - OWLv2 produced 36–128 false positives per recovered ramp.
  - Conclusion: "text-prompted open-vocab models weren't selective enough".
  - YOLOE was not tested. — [RampNet issue #52](https://github.com/ProjectSidewalk/RampNet/issues/52)
- **Other domains (indirect):**
  - Roadside infrastructure (Wuhan): MM-Grounding DINO beat YOLO-World in zero-shot mAP@50. — [arXiv 2601.10551](https://arxiv.org/pdf/2601.10551)
  - Aerial imagery throughput: Grounding DINO about 3.2 FPS, OWLv2 about 8.5, YOLO-World about 52.1. — [arXiv 2601.22164](https://arxiv.org/pdf/2601.22164) (snippet-level)

**VLMs**
- **Lieu, Morra, Cadoni, Song, Mazzarello, Ratti (MIT Senseable), arXiv 2609.17882, Sept 2026.**
  - Setup: four VLMs (names not in the abstract) on 514 Seoul images against field-measured values, using conformal prediction.
  - Width: the most informative attribute; best mean interval half-width about 1.0 m; all models overestimated width.
  - Slopes: longitudinal slope marginally informative; cross-slope unresolvable.
  - Pavement condition: for 3 of 4 models, prediction sets included all five grades.
  - Uncalibrated intervals covered only 17–47% of true values at a nominal 90%.
  - Quote: "Response self-consistency is therefore not evidence of accuracy." — [arXiv 2609.17882](https://arxiv.org/abs/2609.17882)
- **Street Quality Indicators (arXiv 2608.20026):** LLaVA v1.6 Mistral-7B on Nice and Vienna suburbs. Urban–rural classification 92% accuracy, storefront detection 64%, sidewalk width 54%. — [arXiv 2608.20026](https://arxiv.org/pdf/2608.20026) (snippet-level)
- **GPT-4o vs human walkability perceptions:** GPT-4o and participants were aligned on overall walkability, feasibility, accessibility and safety. This measures perceived agreement, not object-level accuracy. — [ResearchGate](https://www.researchgate.net/publication/391278958_Urban_walkability_through_different_lenses_A_comparative_study_of_GPT-4o_and_human_perceptions)
- **Other related VLM and accessibility work, results not retrieved:**
  - "Do VLMs See What Sensors Feel?" (wheelchair accessibility from street view). — [arXiv 2606.07642](https://arxiv.org/pdf/2606.07642)
  - OmniAcc. — [arXiv 2509.07220](https://arxiv.org/pdf/2509.07220)
  - SAGAI. — [ResearchGate](https://www.researchgate.net/publication/391057888_Streetscape_Analysis_with_Generative_AI_SAGAI_Vision-Language_Assessment_and_Mapping_of_Urban_Scenes)
  - ChatGPT plus GSV walkability. — [ResearchGate](https://www.researchgate.net/publication/402705589_From_images_to_insights_ChatGPT_and_Google_Street_View_for_walkability_assessments)
- **Gemma 4 31B (8-shot) as a label validator:** macro-AUC 0.775 vs 0.915 for fine-tuned DINOv2. — [sidewalk-validator-ai](https://github.com/ProjectSidewalk/sidewalk-validator-ai)

### Inferences
- **Recommended pipeline for Lebanon:**
  1. Fine-tune a YOLO11/YOLO26 or RT-DETR detector on ROD plus locally labeled Beirut images.
  2. Use a Vistas-trained segmenter for the sidewalk mask.
  3. Use open-vocabulary detectors or VLMs only for pre-labeling and candidate mining (e.g., "diesel generator", "street vendor cart"), with human verification. Evidence shows they over-fire (OWLv2) or are imprecise on attributes (VLMs).
- **VLMs suit coarse, segment-level screening** ("is the sidewalk blocked: yes/no", "sidewalk present: yes/no") better than measurement (width, slope) or condition grading. Any VLM audit should be calibrated against a local human-labeled sample.
- **Motorcycles are the weakest Lebanon-relevant class in ROD** (recall as low as 0.676). Motorcycles parked on Beirut sidewalks are frequent, so extra local labels are warranted.

### Gaps
- No per-class Mask2Former, OneFormer or SegFormer Vistas metrics (for example IoU on curb cut, sidewalk or utility pole) were retrieved in this pass.
- No paper found testing Grounding DINO, YOLO-World, Florence-2 or SAM 2/3 on sidewalk obstacles with reported numbers, beyond the curb-ramp log.
- No GPT-4o, Claude or Qwen-VL accuracy numbers vs human auditors on obstacle detection were found. The VLM model names in 2609.17882 were not retrieved.

## 4. Mapillary's own object detections and map features

### Takeaway
Mapillary publishes automatic detections and derived "map features" (about 40–42 point-feature classes plus about 1,500 traffic-sign classes), including utility poles, street lights, benches, fire hydrants and similar. I found no independent accuracy evaluation of these detections. Positional accuracy depends on image GPS and on multi-image triangulation.

### Cited Findings
- Mapillary supports 42 point features and 1,500 traffic-sign classes, with examples including utility poles, fire hydrants, benches, lane markings and street lights. — [Mapillary help](https://help.mapillary.com/hc/en-us/articles/115002332165)
- Another Mapillary help article mentions 40 point features and 150 object-detection classes, an inconsistency with the figures above. — [Mapillary help: What is an object detection?](https://help.mapillary.com/hc/en-us/articles/115000967191)
- In 2019 Mapillary added 42 new object classes as map features. — [Mapillary blog 2019](https://blog.mapillary.com/update/2019/01/23/updating-maps-with-cameras-42-new-point-features.html)
- Map features require detection in at least 2 images (traffic signs) or 3 images (other point features). Accuracy depends on image-location accuracy; denser capture helps. — [Mapillary help](https://help.mapillary.com/hc/en-us/articles/115002332165)
- Closest quantitative analogue, not on Mapillary data: telegraph-pole detection from street view in Ireland reached pixel recall 0.936 and precision 0.822, with confusion against electricity poles. — [arXiv 1708.08417](https://arxiv.org/pdf/1708.08417)

### Inferences
- Mapillary map features could seed a utility-pole and street-furniture inventory for Beirut without training, if capture density is adequate.
- They do not cover parked-on-sidewalk vehicles, generators, vendors or surface condition.
- Coverage in Lebanon is unverified.

### Gaps
- The full current Mapillary detection class list was not retrieved.
- No independent precision or recall study of Mapillary detections was found.
- No research papers were found that use Mapillary detections specifically for sidewalk obstruction mapping.

## 5. Labelling tools, active learning, and the labels needed to add classes such as "generator"

### Takeaway
Project Sidewalk is the proven crowdsourcing model, and LabelAId shows that AI-in-the-loop interventions improve crowd label quality. Label quality matters more than raw volume: noisy, larger data hurt the Liu 2024 models. Weak-supervision bootstrapping from existing location data (RampNet) can generate hundreds of thousands of labels cheaply. I found no source giving a sourced label count for adding a new class like "generator".

### Cited Findings
- Project Sidewalk's crowdsourcing has users label panoramas, others validate, and the validator AI adds calibrated votes. The AI is not yet gated per deployment. — [sidewalk-validator-ai](https://github.com/ProjectSidewalk/sidewalk-validator-ai)
- **LabelAId (2024):** just-in-time AI interventions improve crowd labeling quality and domain knowledge. The most common error is driveways labeled as curb ramps. — [arXiv 2403.09810](https://arxiv.org/pdf/2403.09810)
- **Quality vs quantity:** a cleaned 24k set outperformed a noisier 87k crowd set (a "detrimental effect"). — [sidewalk-tagger-ai](https://github.com/ProjectSidewalk/sidewalk-tagger-ai)
- Duan 2022 likewise studied noisy-large vs validated-small training data and cross-city transfer. — [Duan PDF](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **RampNet bootstrapping:** converted open government curb-ramp locations into more than 210k labeled panoramas automatically. — [arXiv 2508.09415](https://arxiv.org/abs/2508.09415v1)
- **ROD construction:** built by merging 29 Roboflow Universe datasets, showing Roboflow Universe as a practical source for seed classes. — [ROD arXiv](https://arxiv.org/html/2611.00681)

### Inferences
- **For a "generator" class**, a plausible workflow is:
  1. Mine candidates with an open-vocabulary detector or VLM over Beirut imagery.
  2. Verify them in CVAT, Label Studio or Roboflow, or as Project Sidewalk Obstacle tags.
  3. Fine-tune.
  4. Iterate with active learning on low-confidence detections.
- **Label counts:** practitioner rules of thumb (often a few hundred to about 1,500 instances per class for YOLO) are not sourced here and should be treated as unverified.
- **Bootstrapping options for Lebanon:**
  - Municipal permits for café terraces or kiosks, or OSM tags, could bootstrap labels the way RampNet used government ramp data.
  - Generator locations are less likely to be in official datasets.

### Gaps
- No sourced comparison of CVAT, Label Studio and Roboflow for this domain.
- No sourced study of label-count vs accuracy curves for adding a new obstacle class.
- No Roboflow Universe "generator", "street vendor" or "kiosk" dataset verified.
