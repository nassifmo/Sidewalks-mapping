# Overhead (satellite / aerial / drone) sidewalk extraction: methods, datasets, code, and reusability for Lebanon

Research date: 2026-11-06. Scope: work from 2019 to 2026 that extracts sidewalk polygons, centerlines, networks or widths from overhead imagery. The researcher read primary sources (paper PDFs, GitHub pages, Esri docs) wherever possible. Numbers come from those sources unless marked as inference.

---

## 1. Tile2Net (NYU VIDA lab): repo, licence, activity, how to run, GSD, retraining, failure modes, follow-ups and non-US use

### Takeaway
Tile2Net is the only maintained, end-to-end open-source pipeline that goes from tiles to sidewalk polygons to a sidewalk network. It is BSD-3-Clause and actively maintained (last commit 12 Sep 2026). Its model is HRNet-W48 + OCR with hierarchical multi-scale attention, trained only on US East-Coast orthophotos at about 19 cm/px. The repo still supports only inference: no training or fine-tuning module has been released, despite requests from non-US users (Brazil). Its out-of-box accuracy (sidewalk IoU 82.7%) applies to US cities at sub-30 cm GSD and should not be expected in Beirut.

### Cited Findings
**Repo and status**
- Repo: https://github.com/VIDA-NYU/tile2net. Licence BSD-3-Clause. About 234 stars, 35 forks, 371 commits, no tagged releases. Self-described as "early development", "not production-ready" and a "beta release". — [GitHub VIDA-NYU/tile2net](https://github.com/VIDA-NYU/tile2net)
- Latest commit: 12 Sep 2026 (merge of PR #94, Mary-h86). Commits from 3–5 Sep 2026 (hodczak) refactor geocoding (Nominatim/Photon) and tests. — [GitHub commits](https://github.com/VIDA-NYU/tile2net/commits/main)
- Requirements: Python 3.11 (README says 3.11–3.14), CUDA-compatible PyTorch, and at least one CUDA GPU for inference. — [GitHub README](https://github.com/VIDA-NYU/tile2net)

**How to run on a new city**
- `python -m tile2net generate --location "<bbox or address>" --name <project> --output <dir>`, then `python -m tile2net inference --city_info <project-info.json> --local --eval test --dump_percent 0`. The two steps can also be piped together. — [GitHub README](https://github.com/VIDA-NYU/tile2net)
- Built-in imagery sources cover the US only: whole DC, MA, NY, NJ, OR and VA, plus parts of CA (Alameda County, LA), TN (Spring Hill) and WA (King County). New regions are requested through issue #11. — [BASICS.md](https://github.com/VIDA-NYU/tile2net/blob/main/BASICS.md)
- Custom imagery is allowed if it is orthorectified and follows DATA_PREPARE.md. Tiles must be renamed to the convention `<project>\tiles\static\<size>_<zoom>`, e.g. `256_19`. — [BASICS.md](https://github.com/VIDA-NYU/tile2net/blob/main/BASICS.md)
- Closed issues about custom data include #42 "How to use self prepared raster?", #75 "Running the Trained Segmentation Model on Custom Data", #61 (CRS 3857 tiles), #71 (custom tiles on Colab) and #77 (CPU inference). — [Tile2Net issues](https://github.com/VIDA-NYU/tile2net/issues?q=is%3Aissue)

**Required zoom / GSD**
- BASICS.md: imagery "should be zoom 19 or higher if possible, and no less than 18". — [BASICS.md](https://github.com/VIDA-NYU/tile2net/blob/main/BASICS.md)
- The paper trained on zoom-20 256×256 tiles, which it says equal 0.19 m/px. It states the model "can work with resolutions 17 to 23" (zoom levels), and that sidewalks are "not visible from 3-m/pixel images". The best inference results came from stitched 1024×1024 tiles, compared with 512 and 2048. — [Hosseini et al. 2023, CEUS 101:101950 PDF](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- Esri's Living Atlas port of Tile2Net requires 8-bit RGB at "10–30 centimeters". — [Esri Pedestrian Infrastructure Classification doc](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)

**Model, training data, compute**
- Architecture: Hierarchical Multi-Scale Attention (Tao et al. 2020, NVIDIA) with an HRNet-W48 + OCR backbone. Inference scales are 0.5, 1, 1.5 and 2. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- Training data: 11,000 DC tiles (512 px) and 28,000 Cambridge tiles plus 8,000 NYC-park tiles (256 px), stitched to 512 px for about 20,000 training tiles. Split 60/20/20 (12,000 train / 4,000 val / 4,000 test). Labels came from city planimetric GIS. Because GIS and imagery dates did not match, the team hand-corrected 2,500 training, 1,620 validation and 1,500 test tiles. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- Compute: trained 310 epochs on 4× NVIDIA RTX8000 (48 GB each), batch 16, SGD, with colour, flip, scale (0.5–2.0×) and blur augmentation, and class-uniform sampling. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)

**Accuracy**
- Test set IoU (P/R): sidewalk 82.67% (0.90/0.92), road 86.04%, crosswalk 75.42% (0.86/0.86), background 93.94%; mIoU 84.51%. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf); same table in [Esri doc](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)
- Area overlap with official sidewalk polygons: Cambridge 85.9%, Boston 77.9%, DC 73.8%, Manhattan 87.5%. Boston was never seen in training (closest to a domain-shift test). DC was lowered by GIS/imagery mismatch and tree-covered footpaths. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- Network match (official segment centroid within 4 m of a detection): Cambridge 94.56% sidewalks, 91.01% crosswalks, 68.86% footpaths, 83.10% overall. Boston 90.78%, 89.56%, 64.76%, 78.49% overall. Manhattan park footpaths 85.09%. DC vs OSM 76.9%. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)

**Known failure modes**
- Polygon-to-centerline conversion (dense Voronoi) is "very sensitive" to the interpolation distance. Skeletons do not connect across polygons, so the network breaks at polygon boundaries and leaves redundant nodes at corners. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- Footpaths under tree canopy are detected poorly. Shadows and foliage were handled "surprisingly well" in Cambridge and Manhattan because the labels mapped sidewalks through occlusion. The model detects only sidewalk, crosswalk and footpath, so it does not suit cities where pedestrians share space without dedicated sidewalks. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- PathwayBench found Tile2Net "overpredicts disconnected edges". Its routability (TraversabilitySimilarity) was very low: Seattle 0.17, Portland 0.04, DC 0.35. Edge F1 was decent: Seattle 0.90, Portland 0.76, DC 0.84. — [PathwayBench, Zhang et al. 2024, arXiv:2407.16875](https://arxiv.org/html/2407.16875)
- The authors warn that differences "are bound to be bigger between international cities" (materials, crosswalk markings, dimensions). They also say retraining "can be initialized with our trained weights" and needs "significantly less data compared to the initial training". — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)

**Retraining procedure (status)**
- BASICS.md: "we only support inference" for now; a training tutorial is planned. — [BASICS.md](https://github.com/VIDA-NYU/tile2net/blob/main/BASICS.md)
- Issue #73 (4 Dec 2024) asked for training support for regions unlike the US. It got no substantive answer and was auto-closed for inactivity on 3–8 Jan 2025. — [Issue #73](https://github.com/VIDA-NYU/tile2net/issues/73)
- Issue #84 (28 Sep 2025, andrezasp) asked for a fine-tuning module for Brazilian imagery. The maintainer said "I will add it to our todo list!" and the issue was closed 10 Oct 2025 with no linked PR. — [Issue #84](https://github.com/VIDA-NYU/tile2net/issues/84)

**Follow-ups, derivatives and non-US use**
- Esri "Pedestrian Infrastructure Classification" (Living Atlas, first released Dec 2024) uses the Tile2Net architecture. It is proprietary and requires ArcGIS Image Analyst, Image Server or a Pro user type, plus a GPU of compute capability 6.0 or higher. Expected geographies are US states only. — [Esri doc](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)
- GeoSAM (2023–2025) uses Tile2Net's HMSA encoder and weights as a prompt generator for a fine-tuned SAM (see section 2). — [GeoSAM arXiv:2311.11319](https://arxiv.org/html/2311.11319v2)
- Brazil: the UrbanVGGT paper (2026) says the current Tile2Net "was not fine-tuned for the urban fabric of São Paulo". It mentions a São Miguel-borough study that aims to adapt and validate Tile2Net for Brazil. No accuracy figures were found. — [UrbanVGGT arXiv:2603.22531 (search-result snippet)](https://arxiv.org/html/2603.22531)
- A UC OSPO 2026 talk, "Unmapped Cities: Scaling Pedestrian Infrastructure Mapping with Tile2Net", is listed. The page could not be fetched (socket error), so its contents are unverified. — [UC OSPO talk page](https://ucospo.net/events/uc-open-2026/talks/unmapped-cities/)

### Inferences
- Web-Mercator GSD at Beirut (lat ≈ 33.9°, cos ≈ 0.83): z18 ≈ 0.50 m, z19 ≈ 0.25 m, z20 ≈ 0.12 m (computed by the researcher with 156543.03·cos(lat)/2^z). The paper's "z20 = 0.19 m" does not match this formula at Boston latitude (≈ 0.11 m). It probably reflects the native capture GSD resampled to z20, so the true training GSD was likely about 15–20 cm. Esri World Imagery and Maxar in Beirut (31–60 cm native) would sit at z18 or below in effective resolution even if served at z19. That is at or below Tile2Net's stated floor and well outside Esri's 10–30 cm requirement.
- Given no training module, fine-tuning for Beirut would mean extracting the HMSA/HRNet-OCR training code from NVIDIA's semantic-segmentation codebase, on which Tile2Net is built, and initialising from Tile2Net weights. This is an engineering task, not a configuration change.
- "Version 2" in practice means the 2025–2026 refactor: more training data including Manhattan, new US regions (Alameda County, Oregon) and a geocoding overhaul. No paper or release labelled Tile2Net v2 and no alternative-backbone release were found.

### Gaps
- No published accuracy of Tile2Net (raw or fine-tuned) in any non-US city was found, including Brazil.
- The exact backbone and weights of the "updated" 2025–2026 model are not documented in the README.
- The forks list was not enumerated. The README shows 35 forks, but none were confirmed to be non-US applications.
- Contents of DATA_PREPARE.md and the UC OSPO 2026 talk were not retrieved.

---

## 2. Other models and repos (Hosseini 2021, Ning 2021/22, Esri, SAM/SAMGeo/GeoSAM, graph methods, foundation models)

### Takeaway
Apart from Tile2Net, almost no maintained, licensed code exists for overhead sidewalk extraction. Papers either release no code (Hosseini 2021, Ning 2022, APE/Prophet, TraversRL) or are small proofs of concept (Bao et al. 2023 U-Net). The most interesting recent direction is fine-tuned SAM (GeoSAM: MIT/unspecified, RTX 4090). In the unseen city its sidewalk IoU was only 0.27, and zero-shot SAM is poor at separating sidewalks from roads. Geospatial foundation models (Prithvi, Clay, SatlasPretrain) are trained on 10–30 m or Sentinel-class data and have no published sidewalk results.

### Cited Findings
**Hosseini et al. 2021, "Sidewalk Measurements from Satellite Images: Preliminary Findings" (SDSS 2021)**
- Training data: 15,400 NYC 2018 orthotiles from Manhattan and Brooklyn, labelled from NYC planimetrics, split 60/20/20. Model: HMSA with HRNet-OCR (the Tile2Net predecessor).
- Accuracy: sidewalk IoU 79%, precision 91%; mIoU 83% over 4 classes; about 3,000-image test set. Inference ran on about 20,000 Manhattan tiles.
- Width method: skeleton by morphological thinning, with width at each skeleton point equal to twice the distance to the border. Angle uses a finite-difference slope and curvature uses an osculating circle.
- Width RMSE vs ground-truth masks by bin: 0–7 px 3.12 px (n=1,291); 7–14 px 1.85 px (n=11,045); 14+ px 6.07 px (n=529).
- No code URL is given.
- Source: [arXiv:2112.06120](https://arxiv.org/pdf/2112.06120)

**Ning, Ye, Chen, Liu, Cao, "Sidewalk extraction using aerial and street view images" (EPB: Urban Analytics & City Science 49(1):7–22, online Feb 2021)**
- Data and method: 0.3 m aerial imagery over four US counties. Neural-network aerial segmentation, then pre-trained street-view models restore occluded or missing sidewalks.
- Result: precision and recall about 0.9; street view links 20% of dangles. — [SAGE](https://journals.sagepub.com/doi/full/10.1177/2399808321995817); [PSU GIScience page](https://giscience.psu.edu/sidewalk-extraction-from-big-visual-data)
- Sidewalks span about 4–5 px at 0.3 m. Labels were made by buffering centerlines. Strict pixel precision and recall were 0.5508 and 0.7488 before a tolerance buffer was applied. Centerlines were re-derived in ArcGIS. This comes from search-engine summaries of the full text, not verified on the paper page (403). — [SAGE](https://journals.sagepub.com/doi/full/10.1177/2399808321995817)
- No code or data links. — [PSU GIScience page](https://giscience.psu.edu/sidewalk-extraction-from-big-visual-data)

**Bao, Lang, Lin (Ontario Tech), "Deep Learning-Based Sidewalk Extraction on Aerial Image" (CSME-CFD-SC 2023)**
- Plain U-Net: Dice 0.8064, pixel accuracy 99.27% after 10 epochs; ResUNet Dice 0.7851. The authors name occlusion-induced discontinuity as the main limitation. — [PDF](https://usherbrooke.scholaris.ca/server/api/core/bitstreams/ffaa0b71-450e-445c-8aed-02a90d7b46d5/content)

**Esri Pedestrian Infrastructure Classification (Dec 2024)**
- A Tile2Net-based .dlpk model requiring 10–30 cm RGB. It is proprietary, needs an ArcGIS Image Analyst licence and a GPU of CUDA compute capability 6.0 or higher, and is limited to US geographies. Fine-tuning is not mentioned in the doc. — [Esri doc](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)
- Esri's general transfer-learning workflow for retraining Living Atlas models is described in [this Esri blog](https://www.esri.com/arcgis-blog/products/arcgis-pro/imagery/repurposing-deep-learning-models-using-transfer-learning-in-arcgis).

**GeoSAM (Sultan et al., arXiv:2311.11319, v4 accepted ECAI 2025)**
- Method: fine-tunes SAM with sparse point prompts from Tile2Net's pretrained HMSA model and dense or zero-shot SAM prompts. The later version adds LLM text prompts.
- Data: DC train 560 images (1.97 km²), DC test 296 (1.04 km²), Cambridge unseen 2,380 images (30.18 km²); USGS orthos at zoom 20, 1024×1024 input.
- Pedestrian-infrastructure IoU:

  | Method | DC | Cambridge (unseen) |
  |---|---|---|
  | GeoSAM | 0.45 | 0.27 |
  | Tile2Net | 0.42 | excluded (training city) |
  | Zero-shot SAM | 0.24 | 0.12 |
  | UNet | 0.17 | 0.12 |
  | UNet++ | 0.30 | 0.08 |
  | Swin UNETR | 0.26 | 0.09 |

- Road IoU in DC: GeoSAM 0.76, Tile2Net 0.60.
- Compute: one RTX 4090 (24 GB), 100 epochs.
- Code: https://github.com/rafiibnsultan/GeoSAM
- Sources: [arXiv HTML v2](https://arxiv.org/html/2311.11319v2); [arXiv v4 abstract](https://arxiv.org/abs/2311.11319v4)
- The authors note zero-shot SAM "faces significant challenges, particularly in distinguishing sidewalks from roads in aerial imagery". — [GeoSAM](https://arxiv.org/html/2311.11319v2)
- Note: Tile2Net's IoU of 0.42 here is much lower than its self-reported 82.7%. The two use different label definitions (pedestrian = sidewalk+crosswalk) and different test data, so they are not directly comparable.

**segment-geospatial / SAMGeo (opengeos)**
- MIT licence, about 4.2k stars, 451 forks. Supports SAM, SAM 2, SAM 3, HQ-SAM and FastSAM, plus text prompts through Grounding DINO. Exports GeoPackage, Shapefile and GeoJSON; at least 8 GB GPU recommended.
- Repo: https://github.com/opengeos/segment-geospatial — [GitHub](https://github.com/opengeos/segment-geospatial)
- The README makes no mention of roads or sidewalks. No published sidewalk accuracy using SAMGeo was found.
- A related zero-shot study (Xia et al., J. Imaging 2024, New Brunswick NJ) tested SAM on satellite imagery and on mobile-LiDAR-derived views. Combining sources gave the most complete sidewalk extraction, and SAM "crashed multiple times". — [arXiv:2310.09918](https://arxiv.org/pdf/2310.09918); [J. Imaging 10(3):52](https://doi.org/10.3390/jimaging10030052)
- Zero-shot SAM on remote sensing tends to select shadows along with the target. — [Osco et al., arXiv:2306.16623](https://arxiv.org/abs/2306.16623)

**SAM-Road (Hetang et al., CVPRW 2024, SG2RL)**
- Fine-tunes the SAM encoder to output road and intersection masks, then a lightweight transformer GNN predicts edges. Accuracy is comparable to RNGDet++ on City-scale, about 40× faster. Code: https://github.com/htcr/sam_road
- It extracts road graphs, not sidewalks, but is a candidate architecture for sidewalk graph extraction. — [CVF open access](https://openaccess.thecvf.com/content/CVPR2024W/SG2RL/html/Hetang_Segment_Anything_Model_for_Road_Network_Graph_Extraction_CVPRW_2024_paper.html); [arXiv:2403.16051](https://arxiv.org/pdf/2403.16051)

**UW Taskar Center / Caspi group: APE, Prophet, PathwayBench, Skeptic**
- Prophet hypothesises a sidewalk graph from the existing street network, refines it with multi-input segmentation (satellite plus rasterised street map), and optimises the graph. Skeptic is a modified HOT Tasking Manager for human vetting at intersection scale. — [GeoConvention 2025 abstract, Zhang, Devalapalli, Gunti, Caspi](https://geoconvention.com/wp-content/uploads/abstracts/2025/114857-from-imagery-to-graphs-with-scalable-ai)
- PathwayBench (2024): Prophet with a ViT backbone reached edge F1 0.90/0.91 and TraversabilitySimilarity 0.43/0.48 (Seattle/Portland), versus Tile2Net at 0.90/0.76 and 0.17/0.04. No code URL was given. — [arXiv:2407.16875](https://arxiv.org/html/2407.16875)
- TraversRL (Han, Wolfe, Howe; ECCV 2026) grows a pedestrian graph from an aerial image using reinforcement learning with long-jump actions to cross occlusions. It "more than doubles connectivity metrics" over a segmentation baseline. No code URL was found. — [arXiv:2607.17479](https://arxiv.org/abs/2607.17479)

**Geospatial foundation models**
- Prithvi is pre-trained on Harmonized Landsat-Sentinel (30 m) data. Clay is trained on Sentinel-1/2 and DEM. A 2026 benchmark of Clay v1.5, Prithvi-EO-2.0 and AlphaEarth covers neighbourhood-level urban signals, not segmentation. — [arXiv:2604.03456 (search snippet)](https://arxiv.org/pdf/2604.03456)
- SatlasPretrain includes road labels and gives +6% average downstream gain, but has no sidewalk class. — [SatlasPretrain arXiv:2211.15660](https://ar5iv.labs.arxiv.org/html/2211.15660)

### Inferences
- For a team without large GPU budgets, the realistic open stack combines several pieces:
  - a standard segmentation model (HRNet-OCR / Tile2Net weights, or UNet/SegFormer) fine-tuned on local labels;
  - SAM/SAMGeo as an interactive labelling accelerator, not as the detector;
  - an OSM-street-graph-guided approach (Prophet-style) for topology.
- Foundation models built on 10–30 m data are irrelevant at sidewalk scale. Only SAM-family models (trained on natural imagery) and VHR-pretrained encoders are plausible.
- Ning et al.'s and APE's results show that fusing street-level or street-map priors gives larger gains than better aerial-only architectures.

### Gaps
- GeoSAM repo licence and last-commit date were not verified.
- No Microsoft, Google or NVIDIA research release specific to overhead sidewalks (2019–2026) was found. Microsoft's global road detections and Google Open Buildings have no sidewalk layer (not verified in this session).
- "RemoteSAM" returned no relevant results.
- No student "sidewalk-from-orthophoto" repo with documented accuracy was found.
- Code for Hosseini 2021, Ning 2022, APE/Prophet, PathwayBench and TraversRL was not located.

---

## 3. Datasets with sidewalk labels from overhead imagery

### Takeaway
No open, permissively licensed, multi-city overhead sidewalk dataset exists outside the Americas. The usable labelled sources are:
- US municipal planimetric GIS (the source of Tile2Net's labels, which are not redistributed as a packaged dataset);
- DLR SkyScapes (Munich, 13 cm, 31 classes including sidewalk; registration needed, licence unstated);
- UW's APE (6 cities including 4 in Latin America; Bing imagery; release status unclear);
- PathwayBench (8 cities, about 3,000 km²; graph labels in OpenSidewalks schema).

DeepGlobe and SpaceNet contain roads only, no sidewalks.

### Cited Findings
- **Tile2Net training data:** derived from MassGIS, DC GIS and NYC planimetrics plus city orthophotos, with 5,620 tiles hand-corrected in total. The paper and repo do not offer it as a packaged download. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- **NYC planimetrics (Hosseini 2021 labels):** https://github.com/CityOfNewYork/nyc-planimetrics — [Hosseini 2021](https://arxiv.org/pdf/2112.06120)
- **APE (Annotations for Pedestrian Environment):**
  - Coverage: Los Angeles, Bellevue, Quito, São Paulo, Santiago and Gran Valparaíso; 14,800 samples over about 2,700 km²; Bing Maps aerial imagery plus street-map tiles.
  - Classes: sidewalk, crossing, corner bulb.
  - Licence not stated. The data was "to be released upon publication".
  - Satellite-only FCN-8s baseline: sidewalk IoU 0.42; satellite + street map: 0.47.
  - South American imagery is lower resolution. — [arXiv:2303.02323](https://arxiv.org/html/2303.02323)
- **PathwayBench:** about 3,000 km² across 8 cities (Seattle, Portland, DC, Bellevue, Quito, São Paulo, Santiago, Valparaíso). Graphs in GeoJSON (OpenSidewalks schema) plus 3-class rasters; paper CC BY 4.0. No data URL found. — [arXiv:2407.16875](https://arxiv.org/html/2407.16875)
- **DLR SkyScapes:** helicopter imagery over Munich at about 13 cm GSD, 31 classes including sidewalk (merged into "human-area" in one benchmark). Access through https://eoc-datasets.dlr.de/registration; cite Azimi et al., ICCV 2019. — [DLR SkyScapes page](https://www.dlr.de/en/eoc/about-us/remote-sensing-technology-institute/photogrammetry-and-image-analysis/public-datasets/dlr-skyscapes)
- **Lane-level aerial benchmarks:** SkyScapes and the Waterloo Urban Scene dataset (12 cm) are used for lane-marking fine-tuning comparisons. — [arXiv:2410.05717](https://arxiv.org/pdf/2410.05717)
- **GeoSAM benchmark splits:** DC (856 images) and Cambridge (2,380 images) from USGS zoom-20 orthos plus city GIS. — [GeoSAM](https://arxiv.org/html/2311.11319v2)
- **SV-SideWidth (2026):** a street-view width prototype over 527 OSM segments in NYC, São Paulo and Nairobi. It is not overhead, and the authors call it unvalidated and "not authoritative". — [UrbanVGGT arXiv:2603.22531](https://arxiv.org/html/2603.22531)

### Inferences
- A Beirut project will have to create its own labels. The most licence-clean imagery for training is:
  - the 12 cm CC-BY port drone ortho (small area, atypical port streets);
  - CC-BY-NC Maxar 2020 OAM scenes (non-commercial use only).
- Esri World Imagery cannot be used for training or inference under the stated terms.
- OSM sidewalk ways and `sidewalk:width` tags in Beirut are probably sparse, but they could serve as weak labels and as a street graph prior. OSM documents the `sidewalk:width` key at [OSM wiki](https://wiki.openstreetmap.org/wiki/Key:sidewalk:width).

### Gaps
- No 2023–2026 overhead sidewalk dataset for the Middle East or North Africa, or for any Mediterranean city, was found.
- SkyScapes licence terms are unknown. Release status and licences of APE and PathwayBench data are unconfirmed.
- Whether DeepGlobe or SpaceNet ever added sidewalk classes was not re-verified this session; they are roads-only as far as known.

---

## 4. Converting polygons to centerlines, networks and widths

### Takeaway
Two families dominate:
- **Vector Voronoi / medial axis** on simplified polygons (Tile2Net: Douglas-Peucker, then dense Voronoi, then branch trimming; open source in the repo).
- **Raster skeletonisation plus distance transform** (Hosseini 2021: morphological thinning, width = 2 × distance to boundary).

Both are fragile at intersections and need topology post-processing: gap-closing with an R-tree, snapping, removal of dangles and isolated lines. Graph-first methods (Prophet, TraversRL) avoid skeletons altogether and give much better routability.

### Cited Findings
- **Tile2Net centerlines:**
  - Pipeline: Douglas-Peucker simplification, then dense Voronoi (Brandt & Algazi 1992) internal edges as the centerline, then trimming branches below a threshold.
  - Crosswalks: centerlines join the midpoints of the short edges of each polygon's minimum rotated rectangle and are connected to the nearest sidewalk line.
  - Topology fixes: remove false nodes and isolated lines; close gaps with an R-tree query.
  - Interpolation distance matters: d=0.2 gives a smooth line with extra branches, d=0.5 is clean, d=2 breaks the line.
  - Source: [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- **Hosseini 2021 width:** skeleton by morphological thinning, width = 2 × distance to the border at each skeleton point. Angle and curvature come from finite differences and an osculating circle, with scale controlled by the parameter h. Width RMSE is 1.85 px for 7–14 px sidewalks and 3.12 px for those under 7 px. — [arXiv:2112.06120](https://arxiv.org/pdf/2112.06120)
- **Ning et al.:** buffered centerlines served as labels, and segmentation output was converted back to polylines because of the 0.3 m resolution. — [PSU page](https://giscience.psu.edu/sidewalk-extraction-from-big-visual-data); [SAGE](https://journals.sagepub.com/doi/full/10.1177/2399808321995817)
- **Network evaluation:** Tile2Net matches centroids within a 4 m buffer (4 m = 95th-percentile Boston sidewalk width). — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf). PathwayBench argues edge F1 is a weak proxy for routability and proposes connected-component and traversability metrics over intersection-centred polygons. — [arXiv:2407.16875](https://arxiv.org/html/2407.16875)
- **Open tools:**
  - `centerline` (PyPI, MIT, v1.1.1; Voronoi-based; CLI `create_centerlines`) — [PyPI centerline](https://pypi.org/project/centerline)
  - `pygeoops.centerline` (medial axis with optional short-branch cleanup) — [PyPI pygeoops](https://pypi.org/project/pygeoops)
  - The Tile2Net repo itself (BSD-3) contains the polygon-to-network code. — [GitHub](https://github.com/VIDA-NYU/tile2net)

### Inferences
- For Beirut, width should be computed in vector space: take the medial axis of the cleaned polygon and sample orthogonal transects, or compute 2 × distance-to-edge along the skeleton, then aggregate per block-face segment (median and minimum clear width).
- At 0.3–0.5 m GSD, the Hosseini error figures (about 2–3 px RMSE) mean about ±0.6–1.5 m. That is comparable to the width itself (typical 1–2 m), so imagery-derived width at those resolutions is indicative only. At 12 cm (port drone ortho) the same error is about ±0.25–0.4 m.
- Width from imagery measures the paved or visible surface, not clear walking width. Parked cars, kiosks and trees cannot be resolved overhead.

### Gaps
- No paper validated overhead-derived sidewalk width in metres against field measurements. Hosseini 2021 compared prediction masks with planimetric masks, in pixels only.
- Skan and scikit-image medial_axis were not separately verified this session.

---

## 5. Fine-tuning for a new city: resolution, number of labelled tiles, domain-shift drops

### Takeaway
No paper reports a clean learning curve of "N labelled tiles gives X IoU" for sidewalks in a new city. The evidence:
- Tile2Net used about 12,000 training tiles (5,620 hand-corrected in total).
- GeoSAM fine-tuned on only 560 DC images (about 2 km²).
- Unseen-city drops are large. Tile2Net area overlap fell from 85.9% (Cambridge, seen) to 77.9% (Boston, unseen). GeoSAM pedestrian IoU fell from 0.45 to 0.27, and UNet++ from 0.30 to 0.08.
- In APE, sidewalk-graph F1 fell from 80.5 (LA) to 74.6 (Quito, lower-resolution imagery).

### Cited Findings
- Tile2Net: about 20,000 512-px tiles, 12,000 for training, 4× RTX8000, 310 epochs. Cambridge (in training) 85.9% vs Boston (never in training) 77.9% area overlap; network match 83.1% vs 78.5%. — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- Tile2Net authors: "Had we trained the algorithm on NYC alone, it could have resulted in systemic under-detection in Boston and Cambridge". They expect bigger gaps internationally and say transfer learning needs "significantly less data". — [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- GeoSAM: 560 training images (1.97 km², DC). Pedestrian IoU 0.45 on the DC test set and 0.27 on unseen Cambridge (30 km²); zero-shot SAM 0.24 and 0.12. One RTX 4090, 100 epochs. — [GeoSAM](https://arxiv.org/html/2311.11319v2)
- APE (trained on LA only), Pedestrianfer + segmentation sidewalk F1: LA 80.5, Bellevue 79.6, Quito 74.6. Crossing F1: 81.8, 73.6, 76.5. — [APE arXiv:2303.02323](https://arxiv.org/html/2303.02323)
- Tile2Net maintainers have not published a fine-tuning recipe. — [BASICS.md](https://github.com/VIDA-NYU/tile2net/blob/main/BASICS.md); [Issue #84](https://github.com/VIDA-NYU/tile2net/issues/84)

### Inferences
- Order-of-magnitude planning figures are inferred from GeoSAM and Tile2Net, not directly measured. Fine-tuning a pretrained sidewalk model for one city plausibly needs about 2–5 km² of carefully hand-labelled imagery, roughly 500–2,000 tiles of 512 px at 15–20 cm. Labels should cover sidewalks through occlusion, as Tile2Net's did. A single 24 GB GPU is sufficient; full Tile2Net-scale training needs 4× 48 GB.
- Beirut's differences from US cities are severe: no curbs, cars on sidewalks, narrow canyons with tall-building shadows, tile and stone paving. On top of that, the imagery is about 2–3× coarser. Expect drops larger than the Cambridge-to-Boston step, at least as large as APE's LA-to-Quito drop (about −6 F1 points), and probably much larger at 0.5 m.

### Gaps
- No systematic data-efficiency study was found (e.g., 100 / 500 / 1,000 labelled tiles) for sidewalk fine-tuning on overhead imagery.
- No domain-shift numbers were found for Middle-Eastern or other non-gridded dense cities.

---

## 6. Results at low resolution (30–50 cm)

### Takeaway
At 30 cm, sidewalks are only about 4–5 px wide, and evidence is thin: Ning et al. (0.3 m) reached about 0.9 precision and recall only with a tolerance buffer and street-view gap-filling, with strict pixel precision about 0.55. Tile2Net and Esri set their floor at about zoom 18 or 10–30 cm. No published study reports sidewalk segmentation accuracy on 40–50 cm satellite imagery (WorldView or Maxar) specifically. At 50 cm a 1.5 m sidewalk is 3 px. Polygon extraction and width measurement are then not reliable, though centerline presence may be partly detectable.

### Cited Findings
- Ning et al.: 0.3 m imagery; sidewalks about 4–5 px wide, hard to detect at lower resolution. Pixel-strict precision 0.5508 and recall 0.7488; about 0.9 with tolerance. — [SAGE](https://journals.sagepub.com/doi/full/10.1177/2399808321995817); [PSU](https://giscience.psu.edu/sidewalk-extraction-from-big-visual-data)
- Tile2Net: needs zoom 18 or higher, zoom 19+ preferred; trained at about 0.19 m; sidewalks invisible at 3 m. — [BASICS.md](https://github.com/VIDA-NYU/tile2net/blob/main/BASICS.md); [Tile2Net paper](https://fmiranda.me/publications/pdfs/tile2net.pdf)
- Esri's port requires 10–30 cm. — [Esri doc](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)
- APE and PathwayBench flag lower-resolution South American Bing imagery as a source of difficulty; Quito scored lowest. — [APE](https://arxiv.org/html/2303.02323); [PathwayBench](https://arxiv.org/html/2407.16875)
- UrbanVGGT: overhead methods work "in well-mapped cities with high-resolution ortho-imagery", and "suitable high-resolution imagery is often unavailable in lower-data settings". — [arXiv:2603.22531](https://arxiv.org/html/2603.22531)
- WorldView-2 panchromatic is about 0.46 m (context only; the cited study was on trees, not sidewalks). — [arXiv:2411.02009](https://arxiv.org/pdf/2411.02009)

### Inferences
- With Beirut's 0.4–0.6 m Maxar (CC-BY-NC), expect a model to detect presence of a sidewalk strip along wider arterials at best. Narrow (under 1.5 m) or curb-less sidewalks will be at or below the detection limit, and tall-building shadows will further reduce effective resolution.
- Overhead imagery at that resolution is best used as one prior in a fusion approach: an OSM street graph plus sidewalk-likelihood raster plus street-level (Mapillary/KartaView) checks, not as a standalone polygon or width source.

### Gaps
- No quantitative sidewalk IoU-versus-GSD curve (e.g., 15 / 30 / 50 cm on the same city) was found in any 2019–2026 paper.
- No study on Maxar or WorldView 0.3–0.5 m pan-sharpened satellite imagery for sidewalks was found.

---

## 7. Reusability judgement for Lebanon (Beirut)

### Takeaway
The pieces worth reusing are:
- Tile2Net's polygon-to-network code (BSD-3) and its HRNet-OCR weights as an initialisation;
- SAMGeo (MIT) as a labelling accelerator;
- the UW Prophet/Skeptic idea (OSM street graph prior plus human vetting in a HOT-style tasking manager);
- the skeleton and distance-transform width method.

Out-of-the-box inference of Tile2Net or Esri on Beirut's free imagery is not usable. Esri imagery terms forbid ML use. Maxar OAM at 0.4–0.6 m is below the model's resolution floor. Esri's model is proprietary and US-only. The only imagery fine enough for polygons and width (12 cm CC-BY) covers the port alone.

### Cited Findings
- Tile2Net is BSD-3 and active (Sep 2026), inference-only, needs a CUDA GPU, and expects zoom 18–19 or higher. — [GitHub](https://github.com/VIDA-NYU/tile2net); [BASICS.md](https://github.com/VIDA-NYU/tile2net/blob/main/BASICS.md)
- Esri model: proprietary licence, US geographies, 10–30 cm. — [Esri doc](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)
- SAMGeo: MIT, 8 GB GPU or more, exports vectors. — [GitHub](https://github.com/opengeos/segment-geospatial)
- GeoSAM: Tile2Net-prompted SAM fine-tune on one RTX 4090, small training set; code public. — [GeoSAM](https://arxiv.org/html/2311.11319v2)
- Graph-first, OSM-prior pipelines (Prophet) beat Tile2Net on routability. — [PathwayBench](https://arxiv.org/html/2407.16875); [GeoConvention 2025](https://geoconvention.com/wp-content/uploads/abstracts/2025/114857-from-imagery-to-graphs-with-scalable-ai)
- `centerline` (MIT) and `pygeoops` provide Voronoi or medial-axis centerlines. — [PyPI centerline](https://pypi.org/project/centerline); [PyPI pygeoops](https://pypi.org/project/pygeoops)

### Inferences (researcher's judgement)
| Component | Reusable for Beirut? | Notes |
|---|---|---|
| Tile2Net network code (polygon → centerline → topology) | Yes | BSD-3; works on any polygons, including manually traced ones. Tune Voronoi interpolation distance; add intersection snapping. |
| Tile2Net pretrained weights | As initialisation only | Out-of-domain (US, ~15–20 cm); requires fine-tuning code from NVIDIA HMSA base; zoom ≥18 floor. |
| Tile2Net zero-shot inference on Maxar OAM 0.4–0.6 m | Low value | Below floor; expect fragmented output; CC-BY-NC restricts outputs to non-commercial use (licence interpretation to be checked). |
| Tile2Net / any ML on Esri World Imagery | No | Licence (per project context) allows manual tracing only. |
| Esri Pedestrian Infrastructure Classification | No | Proprietary, US-only, 10–30 cm. |
| Fine-tune on 12 cm CC-BY port ortho | Pilot only | Proves width methodology; small and atypical area; domain gap to Maxar imagery. |
| SAMGeo / SAM 2 / SAM 3 | Yes, as labelling aid | Point/box-prompted tracing speeds manual digitising; zero-shot sidewalk vs road separation is poor (GeoSAM). |
| GeoSAM | Experimental | Small training set, single GPU; unseen-city IoU 0.27 even in the US. |
| Skeleton + distance-transform width (Hosseini 2021) | Yes, on traced or 12 cm polygons | Error ~2–3 px → unreliable at 0.3–0.5 m. |
| Prophet/Skeptic-style OSM-prior + human vetting | Yes (concept) | Code not located; replicate with OSM street graph + HOT Tasking Manager. |
| Prithvi / Clay / SatlasPretrain | No | 10–30 m pretraining; no sidewalk results. |

### Gaps
- Whether CC-BY-NC Maxar OAM imagery permits ML training, and what licence the derived data would carry, needs a legal check. It was outside this search.
- No source tested any overhead model in a Middle-Eastern city.
