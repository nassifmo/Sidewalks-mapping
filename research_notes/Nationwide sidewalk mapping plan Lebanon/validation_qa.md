# Validation, Accuracy Assessment and QA Design for a National Sidewalk Inventory (Lebanon)

Scope note: notes cover metrics, standards, sampling/sample-size math, inter-rater reliability, go/no-go gates, temporal validity and ground-truth instrument accuracy. Worked numbers marked "computed" were calculated by the researcher in this session (Python/scipy) from the cited standard formulas; they are not quoted from a source.

---

## 1. Metrics per attribute (geometry, topology, width, categorical, objects, condition)

### Takeaway
Use a layered metric stack: (a) buffer-based length metrics (completeness/correctness/quality, Wiedemann/Heipke) for "is the sidewalk there"; (b) graph routability metrics (PathwayBench TraversabilitySimilarity, connected components) because edge-matching F1 can be high while the network is unroutable; (c) MAE/RMSE/bias + Bland–Altman + "% within tolerance" for width; (d) confusion matrices + kappa for categorical attributes, weighted kappa for ordinal condition; (e) match-radius precision/recall/F1 for point objects.

### Cited Findings
**Geometry (buffer-based, length-weighted)**
- The standard road-extraction evaluation scheme (Wiedemann, Heipke, Mayer et al., TU München) combines completeness, correctness, quality, redundancy and planimetric RMS differences; reference centerlines are buffered and extracted length within the buffer is "matched" — [Wiedemann et al., ISPRS 1997 / TU München](https://www.unibw.de/visual-computing/publikationen-vortraege/publikationen-1/pdf-dateien-publikationen/isprs-1997-xxxii-part3-4w2.pdf/@@download/file/ISPRS-1997-XXXII-part3-4W2.pdf); [Wiedemann 2003, "External evaluation of road networks", PIA03](https://www.pia.tum.de/isprs/pia03/pub/pia03_s4p2.pdf); [Heipke et al., IEEE 1997](https://www.unibw.de/visual-computing/publikationen-vortraege/publikationen-1/pdf-dateien-publikationen/ieee-1997.pdf/@@download/file/IEEE-1997.pdf)
- Definitions (length-based, optimum = 1): completeness = length of reference matched by extraction / total reference length; correctness = length of extraction matched to reference / total extraction length; quality = matched extraction / (total extraction + unmatched reference) — [Wiedemann 2003](https://www.pia.tum.de/isprs/pia03/pub/pia03_s4p2.pdf); [Heipke et al. 1997](https://www.unibw.de/visual-computing/publikationen-vortraege/publikationen-1/pdf-dateien-publikationen/ieee-1997.pdf/@@download/file/IEEE-1997.pdf). Equivalent in TP/FP/FN length terms: Compl = TP/(TP+FN), Corr = TP/(TP+FP), Quality = TP/(TP+FP+FN) (this is the line analogue of IoU/Jaccard).
- Buffer width is a key parameter: typically about the road's average width (e.g., 5 px each side) or a fixed metric buffer (e.g., 5 m in one study); performance depends on the chosen constant buffer, which motivated using each feature's actual width as buffer — [Hinz/Bacher ISPRS O_15](https://www.isprs.org/proceedings/XXXVI/part3/singlepapers/O_15.pdf); [arXiv 2410.02250](https://arxiv.org/pdf/2410.02250); [US patent 8340360](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8340360)
- Example trade-off: in Wiedemann & Ebner's network-completion study, completeness rose 80.7%→85.8% while correctness fell 92.7%→90.5% — [TIB goobi, Wiedemann](https://goobi.tib.eu/viewer/fulltext/1663186316/433)

**Network topology / routability (PathwayBench)**
- PathwayBench (Zhang, Howe, Mehta, Bolten, Caspi, 2024): >3,000 km² from 8 cities with manually vetted ground truth; argues pixel-wise and edge-counting metrics miss routability because one gap can arbitrarily reroute a pedestrian — [arXiv 2407.16875](https://arxiv.org/pdf/2407.16875)
- Count-based metric critique: Tile2Net-style "edge-retrieval" = proportion of ground-truth edges within 4 m of a predicted edge; "can generate high scores even when there is little connectivity" — [PathwayBench](https://arxiv.org/pdf/2407.16875)
- Method: tessellate test area into Tessellating Intersection Polygons (TIP) = Voronoi polygons around road intersections; for each polygon compute degree centrality, betweenness centrality, number of connected components, and traversability — [PathwayBench](https://arxiv.org/pdf/2407.16875)
- Traversability formula: a boundary pair (g[i], g[j]) is traversable if some terminating node on g[i] is reachable from some terminating node on g[j] within the polygon graph; TraversabilitySimilarity(g,G,P) = |TraversablePairs(g,G) ∩ TraversablePairs(g,P)| / |TraversablePairs(g,G) ∪ TraversablePairs(g,P)| (Jaccard), averaged over polygons — [PathwayBench](https://arxiv.org/pdf/2407.16875)
- Results (Table 2): Tile2Net edge-retrieval F1 0.76 (Portland)/0.90 (Seattle)/0.84 (DC) but TraversabilitySimilarity only 0.04 (Portland) and 0.17 (Seattle); avg connected components per polygon 2.77–5.77 vs ground truth 1.45–1.65; best model Prophet (ViT) TraversabilitySimilarity 0.48 (Portland), 0.43 (Seattle) with F1 ~0.87–0.91 — [PathwayBench](https://arxiv.org/pdf/2407.16875)
- Authors' conclusion: F1 "does not reflect how travelers navigate the environment"; TraversabilitySimilarity better aligns with routing needs — [PathwayBench](https://arxiv.org/pdf/2407.16875)
- Related statewide work (Washington State) pairs automated extraction of paths/crossings/curb ramps with interactive QC tools, uses road topology for connectivity, and splits project regions into intersection-scale tasks with assignment/progress/feedback tracking — [arXiv 2410.19762](https://arxiv.org/abs/2410.19762)

**Width**
- Street-view width estimation (UrbanVGGT, Tan & Zhang, ISPRS Archives 2026): MAE 0.252 m, 95.5% of estimates within ±0.50 m on a Washington D.C. ground-truth benchmark; metric scale calibration was the most critical component; authors say cross-city validation and local ground-truth auditing are needed before authoritative use — [arXiv 2603.22531](https://arxiv.org/abs/2603.22531)
- Aerial-segmentation width via skeleton: RMSE 3.12 px (0–7 px widths), 1.85 px (7–14 px), 6.07 px (>14 px) — i.e. reported in pixels; must be converted via GSD — [arXiv 2112.06120](https://arxiv.org/pdf/2112.06120)
- Bland–Altman: plot difference vs mean of the two methods; bias = mean difference d̄; 95% limits of agreement = d̄ ± 1.96·SD(d) — [Bland–Altman plot (reference)](https://en.wikipedia.org/wiki/Bland%E2%80%93Altman_plot)

**Categorical attributes and condition**
- Landis & Koch (1977) kappa scale: <0 poor, 0–0.20 slight, 0.21–0.40 fair, 0.41–0.60 moderate, 0.61–0.80 substantial, 0.81–1.00 almost perfect; ≥0.70 often treated as acceptable, 0.80 preferred in applied settings (a convention, not part of Landis & Koch) — [MetricGate kappa](https://metricgate.com/docs/cohens-kappa/); [Cambridge MRC CBU statswiki](https://imaging.mrc-cbu.cam.ac.uk/statswiki/FAQ/kappa/magnitude?action=raw)
- Kappa paradox: kappa can be low despite high % agreement when one category is very common or rare (relevant: e.g. "obstruction present" is rare) — [MetricGate kappa](https://metricgate.com/docs/cohens-kappa/)
- Cohen's κ = (p_o − p_e)/(1 − p_e); weighted κ (linear/quadratic weights) credits near-misses on ordinal scales such as condition 1–5 — [Cohen's kappa (reference)](https://en.wikipedia.org/wiki/Cohen%27s_kappa)
- Remote-sensing good practice: summarize in an error matrix, report user's/producer's accuracy and confidence intervals, use probability sampling, and evaluate error in the reference data itself — [Olofsson et al. 2014, RSE 148:42–57](https://doi.org/10.1016/j.rse.2014.02.015); [Nottingham repository](https://eprints.nottingham.ac.uk/44846/)

**Objects (curb ramps, obstacles, crossings)**
- Combined aerial + street-view sidewalk detection reached precision and recall ~0.9 in four US counties (Ning et al. 2022) — [NJIT record](https://researchwith.njit.edu/en/publications/sidewalk-extraction-using-aerial-and-street-view-images/)
- Most common Project Sidewalk error: mislabeling driveways as curb ramps — [Project Sidewalk / LabelAId arXiv 2403.09810](https://arxiv.org/pdf/2403.09810)

### Inferences
- Recommended metric set (computed on benchmark):
  - Geometry: Completeness, Correctness, Quality at two buffers (e.g., 1.0 m and 2.0 m around reference sidewalk centerline — sidewalks are narrow, so the road-literature 5 m buffer is too lax); report by stratum. Polygon IoU if sidewalks are mapped as areas. Hausdorff (worst-case) and discrete Fréchet (shape/order-aware) distance for matched segment pairs — use the 95th percentile, not mean, as Hausdorff is outlier-driven ([Hausdorff](https://en.wikipedia.org/wiki/Hausdorff_distance), [Fréchet](https://en.wikipedia.org/wiki/Fr%C3%A9chet_distance)).
  - Topology: PathwayBench TraversabilitySimilarity per TIP, Δ(avg connected components) vs reference, % of crossings connected to sidewalks on both sides, dangling-node count per km.
  - Width: bias, MAE, RMSE, Bland–Altman LoA, % within ±0.25 m and ±0.50 m, and — for accessibility — a binary classification "clear width < 1.2 m" scored with sensitivity/specificity (the use-case question is the threshold decision, not the mean error).
  - Categorical (surface, presence, side, type): confusion matrix, overall accuracy, per-class user's/producer's accuracy, Cohen's κ (2 raters) or Fleiss' κ (>2).
  - Condition (ordinal): quadratic-weighted κ + % exact and % within one category.
  - Point objects: one-to-one Hungarian matching within radius r (e.g., 2–3 m for curb ramps/poles, ~5 m for crossings), precision/recall/F1, count error per 100 m of sidewalk.
- Count/edge-F1 alone should not be a scale-up gate; include a routability metric.

### Gaps
- No primary source found specifying sidewalk-specific buffer widths; the 1–2 m values above are researcher judgment.
- Seoul sidewalk dataset and MIT (e.g., Tile2Net) reliability/kappa numbers were not retrieved in this session.

---

## 2. Positional accuracy standards (ASPRS 2023/2024, NSSDA, ISO 19157, OSM)

### Takeaway
ASPRS Edition 2 (2023; V2 2024) is the current reference: RMSE-only reporting, ≥30 checkpoints (max 120 for large projects), checkpoints at least 2× more accurate than the product, and checkpoint survey error must be included in product accuracy. NSSDA (1998) remains common: ≥20 checkpoints, report at 95% as 1.7308·RMSE_r.

### Cited Findings
- ASPRS Edition 2 V1 (Aug 2023) raised the minimum checkpoints from 20 to 30, citing the Central Limit Theorem (n ≥ 30); maximum 120 for large projects; Edition 2 V2 published 24 June 2024 relaxed ground-control/checkpoint accuracy requirements — [ASPRS Ed.2 announcement](https://www.asprs.org/?p=27154); [LiDAR Magazine, Ed.2](https://lidarmag.com/?p=14176); [Geo Week News V2](https://www.geoweeknews.com/?p=40274); [USGS adopt updated standards](https://www.usgs.gov/ngp-standards-and-specifications/adopt-updated-accuracy-standards)
- Edition 2 V2: "a minimum of 30 independent checkpoints clearly visible on the map"; 30 checkpoints for project areas up to 1000 km², more for larger areas (Table 4); checkpoints "at least twice as much as the expected accuracy of the tested product" (2:1); GCP for planimetric AT: RMSE_H(GCP) ≤ ½·RMSE_H(MAP) — [LiDAR Magazine overview](https://lidarmag.com/?p=15999)
- Edition 2 uses RMSE as the only accuracy measure (95% confidence reporting dropped); accuracy classes are open-ended (e.g., a 5 cm requirement = "5 cm RMSE_H class") — [LiDAR Magazine overview](https://lidarmag.com/?p=15999)
- Product accuracy has two components: fit to checkpoints (RMSE_H1) and survey error of checkpoints (RMSE_H2); both must be reported/combined — [LiDAR Magazine overview](https://lidarmag.com/?p=15999). (The combining equation, RMSE_H = √(RMSE_H1² + RMSE_H2²), is the root-sum-square form; the formula text was not retrieved from the standard itself in this session — verify in the [ASPRS standard](https://publicdocuments.asprs.org/PositionalAccuracyStd-Ed2-V2).)
- Fewer than 30 checkpoints: not endorsed, but reduced-checkpoint reporting statements are provided (section 7.16) — [LiDAR Magazine overview](https://lidarmag.com/?p=15999)
- NSSDA (FGDC-STD-007.3-1998): test against "an independent source of higher accuracy"; "A minimum of 20 check points shall be tested"; with 20 points the 95% level allows one point to fail; if <20 points, use alternative means (deductive estimate, internal evidence, comparison to source) — [FGDC NSSDA](https://www.fgdc.gov/standards/projects/accuracy/part3/chapter3)
- NSSDA formulas: RMSE_r = √(RMSE_x² + RMSE_y²); if RMSE_x = RMSE_y, Accuracy_r = 2.4477·RMSE_x = 1.7308·RMSE_r; if 0.6 < RMSE_min/RMSE_max < 1.0, Accuracy_r ≈ 2.4477·0.5·(RMSE_x + RMSE_y); vertical Accuracy_z = 1.9600·RMSE_z — [FGDC NSSDA](https://www.fgdc.gov/standards/projects/accuracy/part3/chapter3); [Esri SERUG paper](https://proceedings.esri.com/library/userconf/serug07/papers/data_quality/1022_how_accurate_your_data-conkling.pdf)
- NSSDA reporting statements: "Tested ___ (meters) horizontal accuracy at 95% confidence level" or "Compiled to meet ___ ..." — [FGDC NSSDA](https://www.fgdc.gov/standards/projects/accuracy/part3/chapter3)
- NSSDA distribution guideline: points spaced at ≥10% of the dataset diagonal and ≥20% of points in each quadrant — [FGDC NSSDA](https://www.fgdc.gov/standards/projects/accuracy/part3/chapter3)
- The "3× more accurate checkpoint" rule does not appear in the NSSDA text (only "higher accuracy"); it is commonly attributed to ASPRS 2014 Ed.1, which Ed.2 relaxed to 2× — NSSDA text checked via [FGDC](https://www.fgdc.gov/standards/projects/accuracy/part3/chapter3); 2× rule per [LiDAR Magazine](https://lidarmag.com/?p=15999)
- Example specification of comparable planimetric product: 7.5 cm GSD imagery with 0.22 m RMSE_XY horizontal accuracy (Cape Cod planimetrics) — [Cape Cod Commission layer](https://gis-services.capecodcommission.org/arcgis/rest/services/Transportation/Route6A/MapServer/9)
- ISO 19157 quality elements: completeness (commission = excess, omission = missing), logical consistency, positional accuracy (absolute and relative), thematic accuracy (classification correctness, quantitative attribute accuracy), temporal quality (consistency, validity/currency) — [IHO MSDIWG data quality](https://iho.int/uploads/user/Inter-Regional%20Coordination/MSDIWG/MSDIWG14/MSDIWG14_11.2_DataQuality.pdf); [OS Code-Point data measures](https://docs.os.uk/os-downloads/addressing-and-location/code-point-open/code-point-open-getting-started-guide/data-measures); [ISO 19157-1 sample](https://cdn.standards.iteh.ai/samples/78900/bc399b1d1a65486e9cfcf3fd5a4ca3e0/ISO-19157-1.pdf)

### Inferences
- Worked example (computed): to claim "0.25 m horizontal at 95%" under NSSDA requires RMSE_r ≤ 0.25/1.7308 = 0.144 m. Under ASPRS Ed.2, state "Tested to meet 0.15 m RMSE_H class" instead.
- Worked example (computed): if product fit RMSE_H1 = 0.10 m and checkpoints (e.g., RTK) have RMSE_H2 = 0.02 m, combined RMSE_H = √(0.10² + 0.02²) = 0.102 m — checkpoint error is negligible when ≥5× better; at 2× it inflates RMSE by ~12% (√(1+0.25)=1.118).
- For Lebanon: ≥30 well-defined checkpoints (curb corners, ramp tops, manhole centres) per benchmark area, spread per NSSDA quadrant/10%-diagonal rule, and per stratum (dense Beirut core vs mountain towns, where imagery occlusion and relief displacement differ).
- Map the inventory's QA report onto ISO 19157 element names so it is interoperable with government SDI metadata.

### Gaps
- Exact ASPRS Ed.2 V2 Table 4 (checkpoints vs area) and verbatim combining formula: official PDF returned 403 in this session.
- OSM sidewalk quality studies (e.g., Haklay-type completeness comparisons for footways) not retrieved.

---

## 3. Sample size formulas and worked examples (MAE/RMSE, proportions, stratified, cluster, acceptance sampling/LQAS)

### Takeaway
~140–390 matched units per stratum give ±5% on precision/recall; ~60–140 width measurements give ±5 cm on mean error; RMSE from 30 checkpoints is only known to within about −20%/+34%; cluster sampling of street segments inflates n by the design effect 1+(m−1)ρ. For production batches, a binomial LQAS plan such as n=77, accept if ≤7 defects (AQL 5%, LTPD 15%) is a practical default.

### Cited Findings
- Sample size for estimating a mean to ±E: n = (z·σ/E)² — [NIST/SEMATECH e-Handbook, sample sizes](https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm)
- Proportion: n = z²·p(1−p)/E²; finite population correction n = n₀/(1 + (n₀−1)/N) — [Sample size determination (reference)](https://en.wikipedia.org/wiki/Sample_size_determination)
- Confidence interval for a standard deviation (RMSE when bias ≈ 0) uses chi-square: √(n·s²/χ²_{0.975,n}) ≤ σ ≤ √(n·s²/χ²_{0.025,n}) — [NIST e-Handbook chi-square test for SD](https://www.itl.nist.gov/div898/handbook/eda/section3/eda358.htm)
- Design effect for cluster samples: Deff = 1 + (m−1)·ρ (m = cluster size, ρ = intra-cluster correlation) — [Design effect (reference)](https://en.wikipedia.org/wiki/Design_effect)
- Olofsson et al. recommend probability (often stratified) sampling, error matrices of estimated area proportions, and CIs for accuracy — [Olofsson et al. 2014](https://doi.org/10.1016/j.rse.2014.02.015); [FAO toolbox summary](https://www.fao.org/sustainable-forest-management/toolbox/tools/tool-detail/en/c/411863)
- LQAS logic: sample n items; if d or more are defective reject the lot; n and d are chosen from upper/lower thresholds and maximum α/β misclassification risks; common health plan n = 19 with decision rule (e.g., d = 9 or >12); small n (≤19) gives flat OC curves and high misclassification near the threshold — [PMC3931287](https://pmc.ncbi.nlm.nih.gov/articles/PMC3931287); [MetricGate LQAS](https://metricgate.com/docs/lot-quality-assurance-sampling/); [LSTM LQAS generic DIP](https://www.lstmed.ac.uk/sites/default/files/images/about-us-page/lqas%20generic%20dip%20v1.0%20jun%202012.docx)
- Geospatial acceptance sampling exists: a two-rank acceptance sampling plan (TRASP) based on AQL inspects map sheets (rank 1) then features within sheets (rank 2) — [TRASP record](https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_proquest_miscellaneous_919936667)
- Acceptance sampling / ISO 2859-1 (attributes, AQL-indexed plans with inspection levels and switching rules) background — [Acceptance sampling (reference)](https://en.wikipedia.org/wiki/Acceptance_sampling)

### Inferences (all numbers computed this session, z = 1.96)
- **Proportions (precision, recall, attribute accuracy):**
  - p = 0.5, ±5% → n = 385 (worst case); p = 0.90, ±5% → 139; p = 0.85, ±5% → 196; p = 0.90, ±3% → 385; p = 0.95, ±2% → 457.
  - With N = 2,000 segments in a benchmark, FPC reduces 385 → 323.
  - Precision is estimated over predicted features, recall over reference features — size each sample separately.
- **Mean bias/MAE of width (±E):** σ = 0.20 m, E = 0.05 m → n = 62; σ = 0.30, E = 0.05 → 139; σ = 0.15, E = 0.03 → 97; σ = 0.20, E = 0.03 → 171. (Use a pilot of ~30 to estimate σ, then size.)
- **RMSE precision (chi-square, relative 95% CI for true RMSE):** n = 20: 0.77–1.44× observed; n = 30: 0.80–1.34×; n = 60: 0.85–1.22×; n = 100: 0.88–1.16×; n = 200: 0.91–1.11×; n = 400: 0.94–1.07×. So "30 checkpoints" is a minimum for a pass/fail, not a precise RMSE; for width RMSE ±~15% use ≥100.
- **Cluster sampling of segments** (sample blocks/TIPs, measure all segments inside): with m = 10 segments/cluster and ρ = 0.05, Deff = 1.45 → 385 becomes 559; ρ = 0.10 → 732; m = 20, ρ = 0.10 → Deff 2.9 → 1,117. Prefer more, smaller clusters.
- **Stratification:** strata = street type (arterial/collector/local) × urban form (dense Beirut/Tripoli core, suburban, mountain village, coastal) × imagery condition (occlusion high/low). Allocate ≥ minimum n per stratum (e.g., ≥60 width points, ≥139 features for ±5% at ~90%) when stratum-level claims are needed; use Neyman allocation (n_h ∝ N_h·S_h) for national estimates.
- **Zero-defect demonstration:** to show error rate < 5% with 95% confidence observing 0 errors, n = ln(0.05)/ln(0.95) ≈ 59.
- **LQAS / acceptance plans for production batches (binomial, producer risk α ≤ 5%, consumer risk β ≤ 10%):**
  - AQL 2%, LTPD 8% → n = 98, accept if ≤ 4 defective (P_accept 0.953 at 2%, 0.099 at 8%).
  - AQL 3%, LTPD 10% → n = 104, c = 6.
  - AQL 5%, LTPD 15% → n = 77, c = 7 (P_accept 0.962 / 0.093). Recommended default.
  - AQL 5%, LTPD 10% → n = 233, c = 17 (tight discrimination is costly).
  - AQL 10%, LTPD 25% → n = 55, c = 9 (early pilot).
  - Define "defective segment" explicitly, e.g., missing/false sidewalk >2 m, width error >0.5 m, wrong surface class, or broken connectivity at a crossing.
  - Lot = one mapper-week or one cadastral district/tile batch; rejected lots get 100% review and the mapper's next lots get tightened inspection (ISO 2859-style switching).

### Gaps
- No source found that prescribes a specific AQL for sidewalk/GIS feature data; AQL/LTPD values above are design choices.
- ICC/ρ values for sidewalk errors within blocks are unknown; estimate from the benchmark.

---

## 4. Inter-rater reliability protocols in sidewalk audits

### Takeaway
Published sidewalk audit tools achieve good-to-excellent reliability at the subscale/overall level (ICC ~0.81–0.93) but item-level reliability varies widely (MAPS: 50% of items good/excellent, 11% low). Crowdsourced image labeling of sidewalk accessibility gives kappa 0.48–0.96 by feature, and simple QC raises accuracy from 81% to 93%. Target κ ≥ 0.70 per attribute before production, with gold-standard items embedded in every batch.

### Cited Findings
- MAPS (Millstein et al. 2013): reliability sample 290 route pairs, 516 segment pairs, 319 crossing pairs, 53 cul-de-sac pairs; 80 items (50.0%) good/excellent, 41 (25.6%) moderate, 18 (11.3%) low; 17 of 20 route subscale/overall scores (85%) good/excellent — [PMC3728214](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3728214/); [BMC Public Health PDF](https://link.springer.com/content/pdf/10.1186/1471-2458-13-403.pdf)
- Online (Street View) MAPS: route overall score ICC 0.832, fair-to-substantial reliability between raters familiar and unfamiliar with the region — [eScholarship](https://escholarship.org/uc/item/25w671r0)
- MAPS-Global (five countries): 114 items (95.8%) good/excellent, 5 (4.2%) fair; on-street vs Google Street View ICC 0.813 (route), 0.929 (segment), 0.885 (crossing) — [eScholarship MAPS-Global](https://www.escholarship.org/uc/item/1446r781)
- Hara et al. 2012 (crowdsourcing + GSV for sidewalk accessibility): Fleiss' κ at image level 0.48–0.96 (moderate to substantial) — [ASSETS 2012 PDF](https://makeabilitylab.cs.washington.edu/media/publications/Hara_AFeasibilityStudyOfCrowdsourcingAndGoogleStreetViewToDetermineSidewalkAccessibility_ASSETS2012.pdf)
- Hara et al. 2013: simple quality-control methods raised accuracy from 81% to 93% — [CHI 2013 PDF](https://makeabilitylab.cs.washington.edu/media/publications/Hara_CombiningCrowdsourcingAndGoogleStreetViewToIdentifyStreetLevelAccessibilityProblems_CHI2013.pdf)
- Project Sidewalk: label accuracy defined as agree/(agree + disagree) from community validations; Seattle pilot reported ~150k validations, 76.1% agreement; validations API exposes Agree/Disagree/Unsure for computing inter-rater reliability; expert ground truth built by two researchers reaching unanimous agreement — [Seattle sidewalk equity pilot arXiv 2211.11545](https://arxiv.org/pdf/2211.11545); [Project Sidewalk Validations API](https://sidewalk-chicago.cs.washington.edu/v3/api-docs/validations); [LabelAId arXiv 2403.09810](https://arxiv.org/pdf/2403.09810)
- LabelAId: just-in-time AI interventions to improve crowd labeler quality and domain knowledge in Project Sidewalk — [arXiv 2403.09810](https://arxiv.org/pdf/2403.09810)

### Inferences
- Protocol: (1) written codebook with photo examples per class (Lebanese cases: parked cars on sidewalk, generators, stairs, informal ramps); (2) training set of ~50 segments with expert answers; (3) certification: each mapper must reach κ ≥ 0.70 (categorical) and width MAE ≤ 0.15 m vs gold on a 30–50 item test before production; (4) 5–10% gold-standard items silently injected in every batch, with recalibration if rolling κ < 0.60; (5) 10% double-coding throughout production for Fleiss' κ/ICC tracking; (6) monthly calibration sessions on disagreements.
- Report percent agreement alongside κ for rare classes (kappa paradox), and use prevalence-adjusted measures if needed.
- Because MAPS shows item-level reliability is much worse than subscale reliability, drop or merge attributes that fail κ ≥ 0.40 in the benchmark.

### Gaps
- Seoul sidewalk dataset and MIT sidewalk-audit kappa values not found in this session.
- No published Project Sidewalk Cohen's/Fleiss' κ was found (only validation-agreement rates).

---

## 5. Go/no-go gates before scaling automation; use-case-linked thresholds

### Takeaway
No comparable program published formal numeric go/no-go gates that were found; gates must be set by the team, anchored to (a) published state-of-the-art (edge F1 ~0.85–0.90, precision/recall ~0.9, width MAE ~0.25 m, TraversabilitySimilarity ≤0.48) and (b) use-case tolerances (accessibility <1.2 m threshold decisions vs engineering ±0.25 m).

### Cited Findings
- State-of-the-art reference points: sidewalk detection precision/recall ~0.9 ([Ning et al. 2022](https://researchwith.njit.edu/en/publications/sidewalk-extraction-using-aerial-and-street-view-images/)); edge-retrieval F1 0.76–0.93 and TraversabilitySimilarity 0.04–0.48 ([PathwayBench](https://arxiv.org/pdf/2407.16875)); width MAE 0.252 m, 95.5% within ±0.5 m ([UrbanVGGT](https://arxiv.org/abs/2603.22531))
- UrbanVGGT authors explicitly state local ground-truth auditing is needed before authoritative planning use — [arXiv 2603.22531](https://arxiv.org/abs/2603.22531)
- Statewide Washington approach: automation reduces human vetting time but every task still passes through interactive human QC — [arXiv 2410.19762](https://arxiv.org/abs/2410.19762)

### Inferences (proposed gates; researcher design)
- **Gate 0 — Benchmark ground truth ready:** ≥30 RTK checkpoints per stratum; reference widths measured with laser/tape (§7); inter-rater κ ≥ 0.70 on reference attributes.
- **Gate 1 — Model on held-out Lebanese tiles (spatially separated, not random pixels):** sidewalk presence completeness ≥ 0.85 and correctness ≥ 0.90 at 1.5 m buffer; TraversabilitySimilarity ≥ 0.50 (≥ the best published 0.48) after human editing; CI lower bound (not point estimate) must clear threshold.
- **Gate 2 — Width fitness by use-case:**
  - Planning/inventory: MAE ≤ 0.30 m and ≥ 90% within ±0.50 m.
  - Accessibility (flag widths < 1.2 m): sensitivity ≥ 0.90 for "narrow" segments (missing a barrier is the costly error), specificity ≥ 0.80; given MAE ~0.25 m, apply an uncertainty band (e.g., 1.2 ± 0.25 m → "verify in field").
  - Engineering-grade (±0.25 m at 95%): requires ~RMSE ≤ 0.13 m (0.25/1.96); unlikely from imagery alone — require field measurement.
- **Gate 3 — Human-in-the-loop throughput/cost:** AI-assisted mapping must reach equal quality (LQAS lot acceptance at AQL 5%/LTPD 15%) at lower minutes per km than manual; otherwise remain manual in that stratum.
- **Gate 4 — Pilot region outside benchmark (e.g., a second governorate):** metrics within 5 percentage points of benchmark; if not, retrain/fine-tune before national roll-out.
- Gates should be stratum-specific: automation may pass in suburban areas yet fail in dense old cores with tree/balcony occlusion.

### Gaps
- No published go/no-go gate documents from comparable national sidewalk programs were found.
- No authoritative source retrieved for 1.2 m minimum clear width (common in accessibility codes, e.g., ADA uses 36 in/0.915 m minimum; other codes use 1.2–1.5 m) — the Lebanese code value should be confirmed by the code-review researcher.

---

## 6. Temporal validity, change detection, versioning and metadata

### Takeaway
ISO 19157 treats currency ("temporal validity") as a quality element and ISO 19115 lineage documents sources and processing steps; no source found prescribing a sidewalk refresh interval, so refresh must be risk-based.

### Cited Findings
- ISO 19157 temporal quality includes temporal consistency (ordering of events) and temporal validity (currency) — [OS data measures](https://docs.os.uk/os-downloads/addressing-and-location/code-point-open/code-point-open-getting-started-guide/data-measures); [IHO MSDIWG](https://iho.int/uploads/user/Inter-Regional%20Coordination/MSDIWG/MSDIWG14/MSDIWG14_11.2_DataQuality.pdf)
- Lineage metadata (ISO 19115) documents data source and transformation history — [Module notes (low authority)](https://www.scribd.com/document/1039679057/Module-4)
- Olofsson et al.: document deviations from good practice and reference-data error — [Olofsson 2014](https://doi.org/10.1016/j.rse.2014.02.015)

### Inferences
- Per-feature provenance fields: source imagery ID + capture date, GSD, method (AI model version / manual / field), mapper ID, QA status (unreviewed/reviewed/field-verified), QA lot ID, last-verified date, attribute-level confidence, width-measurement method and its instrument accuracy.
- Dataset-level ISO 19115 lineage: process steps (imagery ingest → model inference vN → human edit → LQAS lot result → release), with release versioning (semantic versioning + change logs, immutable snapshots).
- Refresh: full re-validation every 3–5 years in stable areas; annual change detection in high-construction areas (Beirut port blast-reconstruction zones, municipal projects) by re-running the model on new imagery and flagging segments whose predicted geometry/width differs beyond tolerance; ingest municipal permits as change triggers.

### Gaps
- No source found giving empirical sidewalk change rates or recommended refresh intervals.
- Full ISO 19115-1 lineage element names (LI_Lineage, LI_ProcessStep, LI_Source) not verified from the standard text in this session.

---

## 7. Accuracy of ground-truth instruments (benchmark must be much better than method under test)

### Takeaway
ASPRS Ed.2 requires checkpoints ≥2× more accurate than the product; to avoid inflating measured error, aim for ≥3–5×. For width (target method MAE ~0.25 m), a laser distance meter or tape is ample; smartphone LiDAR is acceptable only for short spans and must itself be validated; RTK GNSS is suitable for positional checkpoints but not under heavy urban canyon/tree cover.

### Cited Findings
- ASPRS Ed.2: checkpoints at least 2× the expected accuracy of the tested product; survey error of checkpoints must be included in product accuracy — [LiDAR Magazine](https://lidarmag.com/?p=15999)
- NSSDA: independent source "shall be the highest accuracy feasible" and acquired separately from production data — [FGDC NSSDA](https://www.fgdc.gov/standards/projects/accuracy/part3/chapter3)
- iPhone LiDAR: stationary close-range accurate to ±1 cm, cannot report sub-cm; could not define a 15.2 cm ruler start point at 4 m — [AAPM 2021 abstract](https://w4.aapm.org/meetings/2021AM/programInfo/programAbs.php?aid=58217)
- iPhone LiDAR outdoor/large objects: about ±10 cm absolute accuracy for cliff scanning; façade deviations up to 0.478 m; accuracy depends on object size, texture, reflectivity — [Glasgow eprints 311292](https://eprints.gla.ac.uk/311292); [Geodetski vestnik Yanchuk](https://geodetski-vestnik.com/arhiv/70/1/47_Yanchuk.pdf); [JCSI Pollub](https://ph.pollub.pl/index.php/jcsi/article/download/6234/4617/27555)
- iPhone 13 Pro LiDAR engineering-application accuracy assessment exists (UNB TCRC) — [UNB conference](https://conferences.lib.unb.ca/tcrc/article/view/645)
- River topography: iPhone LiDAR/SfM achieved mm-level precision on measured surfaces, but complex terrain may differ — [par.nsf.gov 10439784](https://par.nsf.gov/servlets/purl/10439784)

### Inferences
- Error budget: if the method's expected width RMSE is ~0.30 m, a reference with 0.02 m error inflates observed RMSE by <0.3% (√(0.30²+0.02²)=0.3007); with 0.10 m reference error, inflation is ~5% (0.316) — so tape/laser (mm–cm) is ideal; smartphone LiDAR (~1–10 cm) is acceptable for planning-grade but not for validating an engineering ±0.25 m claim without its own calibration.
- Typical instrument classes (manufacturer datasheets should be cited per device; not verified in this session): handheld laser distance meters ~±1–3 mm; steel tape ~mm; measuring wheel ~0.5–1% of distance (poor for 1–3 m widths); RTK GNSS ~1–2 cm horizontal in open sky, degraded in urban canyons; total station mm-level.
- Define "clear width" operationally (curb face to obstruction/building line, measured at narrowest point within segment, perpendicular) and have two field staff measure 10% of points twice to estimate reference repeatability (target SD ≤ 2 cm).
- Use RTK checkpoints at well-defined features (curb corners) for positional tests; use laser/tape for widths; never use the same imagery as both the production source and the reference.

### Gaps
- Manufacturer accuracy specs for laser meters, wheels and RTK receivers were not fetched in this session; numbers above are typical ranges and must be verified against specific devices' datasheets.
- No study found validating smartphone LiDAR specifically for sidewalk width.
