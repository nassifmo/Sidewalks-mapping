# Human-in-the-loop (HITL) and QA workflows for reliable automated sidewalk width + object inventory (Beirut)

Context: the pipeline goes street-level photos → segmentation → depth → BEV → widths every 2 m, plus sidewalk objects relative to the curb. On the DC benchmark, width MAE is about 0.85 m from on-foot photos and about 1.9 m from car panoramas. Poles have about 25% precision and 10% recall. Targets are width error ≤0.3–0.5 m and correctly placed objects. Research window is 2018–2026. Lines marked "(not fetched this session)" use well-known documents that were not re-opened during this research. Verify them before quoting.

## 1. Human verification and correction tools, and their throughput (minutes per km or per label)

### Takeaway
The best measured HITL throughput is Project Sidewalk's virtual audit, at about 1.74 street-miles per hour per labeler, or roughly 21 min/km for one pass. It produces point labels, not widths, and one person finds only about 63% of issues at about 71% precision. Obstacle recall for one person is about 40%, close to the pipeline's pole weakness. Five labelers per street raise recall to about 92%, at the cost of precision. Intersection-scale review of automatic sidewalk networks (Prophet/Skeptic) roughly doubled routability, from about 0.3–0.47 to about 0.84–0.88, with "a few minutes" per intersection. SAM-assisted polygon labelling cuts interaction time per mask by roughly 40–80%. No public source gives minutes per km for RapiD, MapRoulette or Tile2Net QA.

### Cited Findings
**Project Sidewalk (Saha et al., CHI 2019, Best Paper; Washington DC deployment)**
- An 18-month DC deployment produced 205,385 labels over 2,941 street-miles, from 797 online users. — [Saha et al. 2019 (PDF)](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf); [UW News](https://washington.edu/news/2019/04/18/project-sidewalk)
- The measured labelling rate is about 1.74 miles/hr per user. Turkers were paid $4.17/mile, set from the US federal minimum wage of $7.25/hr, and actually earned $8.21/hr on average (SD $5.99). — [Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- In one subgroup comparison in the paper, faster users audited 1.93 mi/hr against 1.22 mi/hr. Onboarding has 37 parts and is designed to take under 4 minutes. — [Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- About 23–28% of users in each group were filtered out as low quality. Examples: anonymous 23.7%, registered 22.6%, turkers 28.2%, researchers 25.0%. — [Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- Ground truth was built from an ADA-based codebook and contains 4,617 clusters: 3,212 curb ramps, 1,023 surface problems, 295 obstacles and 87 missing curb ramps. Accuracy was scored at street-segment level. — [Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- Single-user accuracy: on average users found 63% of issues at 71% precision. By group, recall was 67.8% (turkers), 61.4% (registered) and 48.8% (anonymous), with precision of 68.8%, 72.2% and 74.5%. — [Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- Multiple labelers: taking the union of 5 turkers raised recall from 67.8% to 91.7% and lowered precision from 68.8% to 55.0%. Majority vote of 5 lowered recall to 59.5% and raised precision. — [Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- Results by label type:
  - Curb ramps: recall 86.0%, precision 95.4%.
  - Obstacles: recall 39.9%, precision 47.5%.
  - Surface problems: recall 27.1%, precision 72.6%.
  - High-severity problems had higher recall (M = 83.3%) than low-severity ones.
  - Source: [Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- Cost model: auditing all of DC with 100 paid workers would cost about $34,000 and take 8 days, assuming 5 labelers per street, 8 h/day and 72 of 100 workers "good". If volunteers covered one third, the cost would fall below $25,000. — [Saha et al. 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- Validation design: users vote agree, disagree or unsure on other users' labels. By 2024 the project was deployed in 21 cities in 8 countries, with more than 1M labels and 693k validations across 11k street-miles. Earlier (ASSETS 2022) it had 700k labels and 400k validations in 10 cities. — [Liu et al. ASSETS 2024](https://makeabilitylab.cs.washington.edu/media/publications/Liu_TowardsFineGrainedSidewalkAccessibilityAssessmentWithDeepLearningInitialBenchmarksAndAnOpenDataset_ASSETS2024.pdf); [Duan et al. ASSETS 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- Known weakness: the same crowd that mislabels also validates. LabelAId (CHI 2024) gives just-in-time AI feedback on labels and significantly raised label precision without slowing labelling. — [Li et al. CHI 2024 LabelAId](https://makeabilitylab.cs.washington.edu/media/publications/Li_LabelaidJustInTimeAiInterventionsForImprovingHumanLabelingQualityAndDomainKnowledgeInCrowdsourcingSystems_CHI2024.pdf)
- A 2024 study cited by CMAP reported 93.1% label accuracy, from 12,191 labels over 35.9 miles with 19,396 validations. This is agreement by peer validation, not agreement with field truth. — [CMAP, Measuring sidewalk accessibility](https://cmap.illinois.gov/news-updates/measuring-sidewalk-accessibility/)
- CMAP notes that Project Sidewalk cannot measure widths, running slopes or cross slopes. — [CMAP](https://cmap.illinois.gov/news-updates/measuring-sidewalk-accessibility/)

**CMAP comparison of self-evaluation methods (Chicago region municipalities)**
- Accuracy ratings: LiDAR "High" (about 300–372 features captured); manual "High" (about 100 features); Ecopia (aerial AI) "Low" (about 20 features); Project Sidewalk "Low" (about 20 features). — [CMAP](https://cmap.illinois.gov/news-updates/measuring-sidewalk-accessibility/)
- Ecopia "tends to overestimate the width of sidewalks". — [CMAP](https://cmap.illinois.gov/news-updates/measuring-sidewalk-accessibility/)
- Cost: manual about $1,600/mile on average, and manual plus Project Sidewalk about $64/mile ("96 percent savings"). Labour hours per mile, computed from CMAP's Table 3:
  - LiDAR: about 5.9 h/mi, about 3.7 h/km.
  - Manual: about 22.8 h/mi, about 14.2 h/km.
  - Manual plus Project Sidewalk: about 5.3–10.5 h/mi, about 3.3–6.5 h/km.
  - The table also contains internal inconsistencies.
  - Source: [CMAP](https://cmap.illinois.gov/news-updates/measuring-sidewalk-accessibility/)

**Prophet/Skeptic (automatic pedestrian graph plus human QA; Washington State / King County pilot)**
- TraversabilitySimilarity against ground truth (ground truth = 1.0) in three areas:

  | Area | Tile2Net | Prophet (automatic) | Prophet + Skeptic (human QA) |
  |---|---|---|---|
  | Argyle | 0.32 | 0.47 | 0.84 |
  | Bertha Pitts | 0.39 | 0.44 | 0.88 |
  | Burbridge | 0.31 | 0.31 | 0.84 |

  - Edge-retrieval F1 is already about 0.96–0.98 for automatic output. The authors note that this metric hides routability failures.
  - Source: [arXiv 2410.19762](https://arxiv.org/html/2410.19762v1)
- Skeptic tasks are intersection-scale and designed to take "just a few minutes (in some cases, seconds)". This is a design target, not a measured average.
  - Operators were 5 undergraduate interns with 2 hours of training, plus an industry annotation team (ORISSA) and community "Deep Dive" teams.
  - Each intern got 150 intersection tasks with one week to finish them.
  - The authors say manual repair "remains sensitive to the training and experience of operators".
  - Source: [arXiv 2410.19762](https://arxiv.org/html/2410.19762v1)
- Tile2Net is open-source sidewalk, crosswalk and footpath segmentation from aerial imagery, evaluated in Manhattan, DC, Boston and Cambridge. Follow-up work says it ignores connectivity. — [arXiv 2410.19762](https://export.arxiv.org/pdf/2410.19762)
- An Atlanta sidewalk-network QA/QC study tracked error-finding and correction times to estimate labour cost. Gaps between tax parcels and misplaced intersection centroids significantly increased QA/QC labour. No per-km figure was retrieved. — [NCST UC Davis, Atlanta sidewalk networks](https://ncst.ucdavis.edu/research-product/economic-sustainability-sidewalk-networks-and-funding-scenario-cost-distributions)

**RapiD / Map with AI (human review of AI features)**
- The AI proposes roads. A human mapper confirms, rejects or slightly adjusts each one, and every AI feature is added only by explicit mapper choice. Before upload, mappers must resolve issues in the iD/RapiD validation panel. — [OSM Wiki: AI-Assisted Road Tracing](https://wiki.openstreetmap.org/wiki/AI-Assisted_Road_Tracing); [VentureBeat](https://venturebeat.com/ai/facebook-speeds-up-mapping-data-validation-with-machine-learning-tools-map-with-ai-and-rapid); [Meta tech blog 2019](https://tech.facebook.com/artificial-intelligence/2019/7/ai-is-supercharging-the-creation-of-maps-around-the-world/)
- Even with AI roads, Facebook's internal team took about 1.5 years to map all of Thailand. No per-km review rate was published. — [OSM Wiki](https://wiki.openstreetmap.org/wiki/AI-Assisted_Road_Tracing)

**SAM-assisted labelling (CVAT / Label Studio-type tools)**
- Agricultural study (14 experts):
  - Manual polygon drawing took 9.7 s per mask.
  - SAM-1 pre-labels cut this to 2.1 s per mask on single images.
  - SAM-2 on image sequences cut it to 1.6 s per mask.
  - Source: [Frontiers in AI 2025/26 (ARAMSAM)](https://public-pages-files-2025.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1748468/epub)
- Grounding-DINO + SAM annotation using CVAT saved 33–94% of annotation time, depending heavily on the dataset. — [arXiv 2406.19057](https://arxiv.org/pdf/2406.19057)
- BoxCell: manual LabelMe polygons took 17.8 s per object, and SAM saved 7.9 s (−44%). — [arXiv 2311.17960](https://arxiv.org/pdf/2311.17960)
- Medical images: SAM gave about 25% faster labelling, about 0.2 min saved per object. — [arXiv 2304.14660](https://arxiv.org/pdf/2304.14660)
- SAM data engine: time per mask fell from 34 s to 14 s as the model improved. — [Kirillov et al., arXiv 2304.02643](https://arxiv.org/pdf/2304.02643)
- SAM 2 video engine: time per frame fell from 37.8 s to 4.5 s (8.4×). — [arXiv 2408.00714](https://arxiv.org/pdf/2408.00714)
- CVAT supports SAM-based interactive and automatic annotation. Its benchmark post claims time savings but gives no retrievable numbers. — [CVAT blog](https://www.cvat.ai/blog/benchmark-segment-anything-model)

### Inferences
- One reviewer pass over street-level imagery costs about 20–30 min per km of street, based on Project Sidewalk's 2.8 km/h. Five-fold redundancy costs about 1.5–2 h/km. Point checks such as "is this a pole and is it on the sidewalk" are a better fit for this rate than width correction.
- Field manual inventory costs about 14 h/km (CMAP). Imagery-assisted hybrid workflows cost about 3–6 h/km.
- A realistic HITL "accept, reject or nudge" workflow over the pipeline's own outputs is probably 10–30 min/km for objects plus width-edge correction. Width-edge correction would be done on BEV tiles or Esri imagery in the QGIS survey GeoPackage. This estimate extrapolates from Project Sidewalk and Skeptic; no direct measurement exists.
- Crowd-only obstacle labelling is weak (about 40% recall). The pipeline's own pole detection (10% recall) is far below even that. Human verification of AI candidates combined with human discovery is therefore needed for objects unless the detector is retrained. Using AI as a candidate generator and humans as validators follows the RapiD pattern.
- Skeptic shows the largest gains come from fixing topology and edge errors at intersections and segment junctions. The Beirut equivalent is fixing curb lines at corners, driveways and parked-car occlusions.
- SAM-assisted correction (click to refine a sidewalk mask) is likely 3–5× faster than polygon tracing. This is the cheapest way to create Beirut fine-tuning labels.

### Gaps
- No published minutes per km were found for RapiD/Map with AI review, MapRoulette challenges, the OpenSidewalks Tasking Manager, or Tile2Net human QA.
- No published study of time to manually trace sidewalk edges or width in QGIS from orthoimagery was found.
- No independent field-truth accuracy for Project Sidewalk widths was found, because the tool does not measure widths.
- The Saha 2019 paper gives "street miles". Whether this means one or both sides was not verified for converting per-km cost.

## 2. Active learning and uncertainty-driven review (send only low-confidence segments to humans)

### Takeaway
On Cityscapes-type data, region-based active learning reaches about 94–98% of fully supervised segmentation with only about 5–15% of pixels or regions labelled. This means a small, well-chosen review budget recovers most of the accuracy. No paper was found that quantifies how many human reviews of predicted sidewalk widths or depth are needed to reach a given MAE. That must be measured on the project's own calibration data.

### Cited Findings
- Spatial-diversity region-based AL reached about 95% of fully supervised performance with 5–9% of labelled pixels (Cityscapes, PASCAL VOC). — [Cai et al. 2025, arXiv 2507.17367](https://arxiv.org/pdf/2507.17367)
- S4AL (semi-supervised active learning) started from 10% labels and exceeded 95% of full-dataset performance with 15% of labelled pixels on Cityscapes. Pseudo-labels came from predictions above 0.7 confidence. — [arXiv 2210.08403](https://arxiv.org/pdf/2210.08403)
- Kasarla et al. 2019 reached 93.8% of full-label performance by labelling 10% of pixels with region selection. — [IITH publication](https://publications.iith.ac.in/publication/region-based-active-learning-for-efficient-labeling-in-semantic)
- Reinforced active learning (Casanova et al., ICLR 2020) needed about 30% less additional labelled data than the best baseline on Cityscapes. — [ICLR 2020 poster](https://iclr.cc/virtual_2020/poster_SkgC6TNFvr.html)
- RIPU (region impurity and prediction uncertainty, CVPR 2022) targets domain-adaptive AL with few labelled regions. Numbers were not retrieved. — [arXiv 2111.12940](https://www.arxiv.org/pdf/2111.12940); [GitHub BIT-DA/RIPU](https://www.github.com/BIT-DA/RIPU)
- MetaBox+ uses region-based AL with priority maps for segmentation. — [Papers with Code](https://physics.paperswithcode.com/paper/metabox-a-new-region-based-active-learning)
- Cross-country traffic-sign detection on Mapillary imagery: smart selection of target-domain images matched random sampling using about half the target data. — [arXiv 2602.01836](https://arxiv.org/pdf/2602.01836v1)

### Inferences
- A practical triage for Beirut could run as follows. This is an inference, not a cited protocol.
  1. Compute a per-2 m-segment risk score. Inputs could include segmentation entropy at the curb and building-edge pixels, disagreement between overlapping photos or test-time augmentation, depth uncertainty (ensemble or variance), BEV edge straightness, and occlusion fraction (parked cars).
  2. Send the top 10–20% riskiest segments to humans.
  3. Accept the rest after a random-sample audit (Section 4).
- The AL literature says the first 5–15% of well-chosen labels deliver most of the gain. Uncertainty-based review should therefore be a deliberate share, not 100%.
- Calibration is the key risk. The DC benchmark should be used to check that the risk score actually ranks width errors, with a reliability plot of predicted risk against |error|, before relying on it in Beirut.

### Gaps
- No paper was found that quantifies review budget against width or depth error for sidewalk mapping specifically.
- No literature on uncertainty estimation for monocular depth or BEV width was retrieved in this session.

## 3. Fine-tuning segmentation and detection on a few hundred local (Beirut) labelled images

### Takeaway
Geographic domain shift is real and comes mostly from classification errors, not localisation. Small labelled target sets help substantially: 50 labels gave +6.9 mIoU over unsupervised adaptation, and 481 images gave +13.8 mIoU over target-only. Unsupervised adaptation alone can fail. A few hundred SAM-assisted Beirut labels, chosen by active selection, is a defensible plan. No Middle East–specific numbers were found.

### Cited Findings
- Eurocentric models tested on Mapillary Vistas images from six continents (Swin-L, segmentation IoU):

  | Class | Europe | Africa | Africa after class-merging |
  |---|---|---|---|
  | bus | 0.43 | 0.17 | 0.52 |
  | motorcycle | 0.46 | 0.24 | 0.34 |
  | rider | 0.46 | 0.29 | 0.43 |

  - Car stays stable (0.75 vs 0.71).
  - Classification errors cause 10–90% of segmentation geo-bias.
  - Merging to coarser classes cuts disparity, for example −90% for bus and −47% for rider.
  - Sidewalk, pole and sign were not evaluated, and the Middle East was not studied separately.
  - Source: [arXiv 2412.11061](https://arxiv.org/html/2412.11061v1)
- Semi-supervised domain adaptation with only 50 target labels gave +6.9 mIoU over unsupervised domain adaptation (GTA→Cityscapes). — [arXiv 2411.18728](https://arxiv.org/pdf/2411.18728v1)
- A supervised domain-adaptation method using 481 labelled target images improved mIoU by +13.8 over target-only and +2.4 over naive fine-tuning on source plus target. The domain is rural, not urban. — [APSIPA 2025 P572](https://webdev.apsipa.org/proceedings/2025/papers/APSIPA2025_P572.pdf)
- Chen et al. adapted road-scene segmenters to new cities using only unlabelled images, and annotated 100 images per city for evaluation. — [ICCV 2017](https://openaccess.thecvf.com/content_ICCV_2017/papers/Chen_No_More_Discrimination_ICCV_2017_paper.pdf)
- Mapillary Vistas has 25,000 images and 66 categories with global coverage. — [Neuhold et al. ICCV 2017](https://mlanthology.org/iccv/2017/neuhold2017iccv-mapillary)
- Street-view segmentation has been trained and tested mostly on Global North cities, with little evidence for Southeast Asian streets (Phnom Penh case). — [SUTD poster](https://www.sutd.edu.sg/wp-content/uploads/2026/03/MRP-Poster_Darren-Ho.pdf)
- Cross-city training in Project Sidewalk (ASSETS 2022) examined how label quality and training on other cities affect AI performance. Specific numbers were not retrieved. — [Duan et al. ASSETS 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)

### Inferences
- Beirut differs from DC in ways likely to cause class confusion:
  - informal street vending and kiosks
  - generator cables and poles
  - very narrow or absent sidewalks
  - cars parked on sidewalks
  - bollards and planters
  - mixed curb heights
- Expect the biggest gains from local fine-tuning on sidewalk vs road vs parking-on-sidewalk and on pole/bollard classes.
- Labelling budget: 200–500 images with SAM assist at about 2–10 s per mask and roughly 10–30 masks per image is about 5–15 min per image. That totals roughly 20–120 person-hours. This is an inference from the SAM timing studies.
- Merging to coarse task classes (sidewalk surface, obstacle, pole-like) should reduce geo-bias, as the coarse-class result suggests.

### Gaps
- No published fine-tuning result was found for Beirut or any Middle East street-view segmentation.
- No direct "N images → mIoU" curve for sidewalk or pole classes in a new city was retrieved.
- The finding that unsupervised adaptation sometimes performed no better than source-only appeared in search results without a confirmed source. Treat it as unverified.

## 4. Statistical QA design (sampling, sample size, positional-accuracy standards, agency criteria, vendor accuracy)

### Takeaway
No standard written for sidewalk width exists. Borrow NSSDA/ASPRS for positions (at least 20 or at least 30 checkpoints, RMSE-based) and use classical sample-size formulas for width MAE. Certifying MAE to ±0.1 m at 95% confidence needs about 35–250 independent checks, depending on error spread. Commercial vendors (Cyvl, Ecopia and others) publish no independent width accuracy. CMAP's independent comparison rated AI aerial and crowd tools "Low" accuracy and found Ecopia overestimates widths.

### Cited Findings
- NSSDA horizontal accuracy at 95% confidence = 1.7308 × RMSE_r, where RMSE_r = sqrt(RMSE_x² + RMSE_y²). — [arXiv 2205.01969](https://arxiv.org/pdf/2205.01969)
- The NSSDA (FGDC-STD-007.3-1998) requires a minimum of 20 checkpoints (not fetched this session). — [FGDC NSSDA](https://www.fgdc.gov/standards/projects/accuracy/part3/chapter3)
- ASPRS Positional Accuracy Standards Edition 2 (2023):
  - Uses RMSE as the sole accuracy measure and drops separate 95% confidence reporting.
  - Recommends at least 30 checkpoints.
  - Gives guidance on checkpoint distribution and reporting statements when fewer are used.
  - Sources: [LiDAR Mag overview](https://lidarmag.com/?p=15999); [PSU GEOG 892](https://courses.ems.psu.edu/geog892/book/export/html/709); [ASPRS 2023 PDF](https://www.asprs.org/wp-content/uploads/2024/03/October2023_HLA-Positional_Accuracy_Standards.pdf)
- CMAP: only manual measurement captures every feature, and municipalities typically combine tools. Ecopia should not be relied on for width compliance. — [CMAP](https://cmap.illinois.gov/news-updates/measuring-sidewalk-accessibility/)
- Cyvl in Buffalo, NY (2026): about a $400k contract using sub-inch LiDAR, 360° imagery and RTK GNSS. It feeds the ADA transition plan, which had not been updated in 12 years. No validation results have been published. — [Kurrant news](https://kurrant.com/kurrantly-news/buffalo-deploys-ai-lidar-platform-to-overhaul-road-prioritization-with-cyvl/)
- A "12× faster than manual" claim for Cyvl is marketing only. — [datadrivenaec](https://datadrivenaec.com/tools/cyvl-ai)
- Independent research found iPhone LiDAR generally effective for small ADA issues, with variability in slope readings. Vegetation and parked cars cause data gaps when scanning from the street. — [Caltrans research note](https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/research-notes/task4099-rns-05-25-a11y.pdf); [Route Fifty](https://www.route-fifty.com/digital-government/2025/08/cities-turn-tech-make-curb-ramps-ada-accessible/407054)
- An aerial-point-cloud framework reached 81.0% accuracy classifying PROWAG compliance for curb ramps and crosswalks. — [ISPRS Annals 2026](https://isprs-annals.copernicus.org/articles/XI-4-2026/303/2026/isprs-annals-XI-4-2026-303-2026.pdf)
- The Champaign-Urbana ADA inventory QA combined automated geodatabase checks with manual checks. No sampling rate or tolerance was stated. — [UIUC ADA Transition Plan App. D](https://oae.illinois.edu/wp-content/uploads/2023/04/ADA_Transition_Plan_Supplement_2018-12-12_Appendix-D.pdf)
- Field sidewalk assessment guidance measures design width, minimum clear width and cross slope with a measuring wheel or tape. No tolerance is given. — [govdocs sidewalk assessment guide](https://corpora.tika.apache.org/base/docs/govdocs1/234/234083.pdf)
- A study comparing street-view imagery audits with government field data exists (NSF PAR 10644331). Its numbers could not be retrieved because of a connection error. — [NSF PAR](https://par.nsf.gov/biblio/10644331-validating-pedestrian-infrastructure-data-how-well-do-street-view-imagery-audits-compare-government-field-data)

### Inferences (sample-size arithmetic; standard formulas, computed here)
- Certifying a mean error (MAE) within ±E at 95% uses n ≈ (1.96·σ_|e| / E)², where σ_|e| is the SD of absolute errors. Values for E = 0.1 m:

  | σ_\|e\| | Checks needed |
  |---|---|
  | 0.3 m | ≈35 |
  | 0.5 m | ≈96 |
  | 0.8 m | ≈246 |

  - Width errors at 2 m stations along one block are strongly autocorrelated. Sample independent units, such as one random station per block-face (or per 50–100 m), not consecutive stations.
  - Stratify by street type, sidewalk-width class, occlusion level and image source (on-foot vs car).
- Certifying a proportion (for example, "% of objects correctly placed within 0.5 m"):
  - ±5% at 95% confidence needs about 385 objects (worst case p = 0.5).
  - ±10% needs about 97 objects.
  - Measure object precision and recall separately: verify a random sample of predicted objects for precision, and fully census a sample of block-faces for recall.
- To claim "≤0.3 m" with confidence, the upper 95% bound of MAE (or RMSE, ASPRS-style) must be ≤0.3 m. With the current 0.85 m MAE, no amount of sampling certifies this. Sampling only measures accuracy; correction or retraining is needed to change it.
- Proposed reference data for checks:
  - Field tape or measuring-wheel width at sampled stations: highest trust, roughly 2–5 min per station plus travel.
  - Manual QGIS tracing on Esri imagery: cheaper, but has its own about 0.3–1 m edge uncertainty under trees and parked cars. This is unquantified.
- Acceptance-sampling idea, borrowed from QA practice rather than a sidewalk-specific source:
  1. Accept a district if the sampled MAE upper bound is at or below target.
  2. Otherwise route the district's high-risk segments to review and resample.

### Gaps
- No agency or RFP width tolerance (for example ±1 in or ±0.1 ft) was found, nor any required field-verification percentage for sidewalk inventories.
- No published independent accuracy figures were found for DeepWalk, Sidewalk Scout, Mobility Explorer, Woolpert or Bentley sidewalk products. The DAXBOT accuracy page returned 404.
- The NSSDA 20-checkpoint rule is cited from knowledge of the FGDC text and was not re-fetched.

## 5. Engaging local volunteers and students in Lebanon, and ethics/IRB for street photography

### Takeaway
Lebanon has an active OSM/HOT ecosystem: mapathons with Beirut Arab University and the Lebanon Reforestation Initiative, a Beirut Urban Lab link, about 200k buildings mapped in South Lebanon, and 54k buildings in the 2020 Beirut response. No sidewalk-specific mapping effort was found. Law 81/2018 covers personal data but has no independent regulator. The research team should rely on its university IRB plus blurring of faces and plates.

### Cited Findings
- HOT volunteers mapped about 200,000 buildings in South Lebanon and Nabatieh over about six months to guide reconstruction and aid. — [Harvard SPH, Mapping hope](https://hsph.harvard.edu/atrocity-prevention-lab/news/mapping-hope-rebuilding-lebanon-after-conflict)
- AUB's Beirut Urban Lab invited HOT to City Debates and expressed interest in hosting a mapathon. — [Harvard SPH](https://hsph.harvard.edu/atrocity-prevention-lab/news/mapping-hope-rebuilding-lebanon-after-conflict)
- A HOT local consultant's diary reports mapathons with the Lebanon Reforestation Initiative and Beirut Arab University, with one planned at Beirut Urban Lab. This is a slightly different account from the HSPH article. — [OSM diary SaidAbouKharroub](https://api.openstreetmap.org/user/SaidAbouKharroub/diary/406863)
- In the 2020 Beirut explosion response, mappers digitised more than 54,000 buildings in greater Beirut. — [HOT mailing list, Sept 2020](https://lists.openstreetmap.org/pipermail/hot/2020-September/015348.html)
- The first Beirut mapping party was held in 2009 by OSM Lebanon with SMEX. — [OSM Wiki Beirut Mapping Party](https://wiki.openstreetmap.org/wiki/Lebanon/Beirut_Mapping_Party); [talk-lb](https://lists.openstreetmap.org/pipermail/talk-lb/2009-September/000005.html)
- The OSM Lebanon wiki lists Beirut as work in progress, with missing geometry on the outskirts and no sidewalk focus. — [OSM Wiki Lebanon](https://wiki.openstreetmap.org/wiki/Lebanon); [WikiProject Lebanon](https://wiki.openstreetmap.org/wiki/WikiProject_Lebanon)
- Law 81/2018 (Electronic Transactions and Personal Data) was effective in 2019. Part V covers personal data, and the law establishes no independent data-protection authority. — [UN ESCWA legislation DB](https://alp.unescwa.org/legislations/law-81-2018-electronic-transactions-and-personal-data); [DLA Piper](https://www.dlapiperdataprotection.com/index.html?t=law&c=LB); [SMEX/Medium commentary](https://medium.com/data-and-society/the-lebanese-e-transaction-law-in-relation-with-personal-data-protection-26e6112322f1)
- Project Sidewalk's model (online volunteers plus paid crowd plus validation) has been deployed in 21 cities in 8 countries. — [Liu et al. 2024](https://makeabilitylab.cs.washington.edu/media/publications/Liu_TowardsFineGrainedSidewalkAccessibilityAssessmentWithDeepLearningInitialBenchmarksAndAnOpenDataset_ASSETS2024.pdf)

### Inferences
- Likely partners are Beirut Urban Lab (AUB), Beirut Arab University, OSM Lebanon/HOT local consultants, LAU and USJ urban planning and architecture departments, and disability organisations.
- Student "validation sprints" could each cover about 2–3 km/h of point verification at Project Sidewalk-like rates, in 2-hour trained sessions as in the Skeptic interns' training.
- Ethics measures:
  - IRB or ethics review at the host university. Photographing public space is usually low-risk but involves identifiable people and plates.
  - Automatic face and plate blurring before any sharing.
  - No publication of raw images near sensitive sites (military, religious, security).
  - Field teams carry a university letter.
  - Data minimisation consistent with Law 81/2018's purpose limitation.
- These recommendations are inferred; no Lebanon-specific street-photography guidance was found.

### Gaps
- No source was found on Lebanese rules for photographing public space or for research street photography, nor on AUB, LAU or USJ IRB policies for street-view imagery.
- No sidewalk or accessibility mapping project in Lebanon was found.
- MapRoulette or Tasking Manager use in Lebanon was not documented.
