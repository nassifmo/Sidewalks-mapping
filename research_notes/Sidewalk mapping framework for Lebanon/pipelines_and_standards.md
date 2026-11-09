# End-to-end sidewalk inventory pipelines, data models/standards, and network-generation tools (2019-2026)

Scope note: These notes come from about 17 searches and fetches, done on 2026-11-06. GitHub pages often did not show commit dates. Where a page gave no maintenance date, that is stated rather than guessed.

## Q1. OpenSidewalks (TCAT/UW): schema, tooling, TDEI, Workspaces, AccessMap

### Takeaway
OpenSidewalks (OSW) is a GeoJSON network schema built on OSM tags. It covers nodes, edges and zones, plus adjacent and custom features. Versions are 0.1 (Aug 2023), 0.2 (Jan 2024) and 0.3 (27 Jan 2026). The USDOT-funded TDEI wraps it in validators, OSW<->OSM converters, incline tagging, quality metrics and a "Workspaces" editing stack (Rapid editor plus an OSW Tasking Manager plus a GoInfoGame mobile app). It is the most complete open reference architecture for the ingest-to-publish chain. Lebanon could adopt OSW as its internal exchange format while keeping full OSM tag compatibility.

### Cited Findings
- **Schema versions.** 0.3 was released 2026-01-27 and is the latest. 0.2 came out 2024-01-30 and 0.1 on 2023-08-11. Version 0.3 added custom entities, tree/wood features, and leaf type/leaf cycle fields. — [OpenSidewalks-Schema GitHub](https://github.com/OpenSidewalks/OpenSidewalks-Schema)
- **A network schema.** The schema is described as "explicitly a _network schema_". It has three groups of entities:
  - core network entities: Nodes (Points), Edges (LineStrings) and Zones (Polygons);
  - "adjacent" non-network entities, such as hydrants, fences and buildings;
  - custom Points, Lines and Polygons (new in 0.3).
  — [OpenSidewalks-Schema](https://github.com/OpenSidewalks/OpenSidewalks-Schema)
- **Key tags.** The schema reuses OSM tags directly:
  - Sidewalk = `highway=footway` + `footway=sidewalk`.
  - Crossing = `footway=crossing`.
  - Curb = `barrier=kerb` with `kerb=raised|rolled|lowered|flush`.
  - `width` is numeric, in metres.
  - `incline` is numeric; positive means uphill.
  - `surface` is an enumeration (asphalt, concrete, ...).
  - Also used: `foot`, `crossing:markings`, `tactile_paving`, `opening_hours`.
  — [OpenSidewalks-Schema](https://github.com/OpenSidewalks/OpenSidewalks-Schema)
- **Format.** Data is GeoJSON in WGS-84, with no `crs` member (per RFC 7946). There is a reference JSON Schema, and a PostgreSQL schema is mentioned. The README text does not name the schema licence; it links to a LICENSE file that was not read. ODbL appears only in an example dataSource block for OSM-derived data. — [OpenSidewalks-Schema](https://github.com/OpenSidewalks/OpenSidewalks-Schema)
- **Validation.** Validation is available two ways:
  - the `python-osw-validation` PyPI package (TaskarCenterAtUW repo);
  - the "OSW - Validate" job on the TDEI Portal (`TDEI-python-osw-validation`).
  Sample metadata also references an "OSWDataPipeline" project. — [OpenSidewalks-Schema](https://github.com/OpenSidewalks/OpenSidewalks-Schema)
- **TDEI components.** The deployment repo lists:
  - **Validators:** OSW, GTFS Pathways, GTFS Flex, and the MobilityData canonical GTFS validator.
  - **Conversion:** an OSW<->OSM converter (`TDEI-python-osw-formatter`).
  - **Other jobs:** a quality-metric job, an ETL job (`TDEI-extract-load-service`), a confidence-metric job (stub only), and DEM-based incline tagging (`TDEI-python-osw-incline`).
  - **Platform:** gateway and data service, user management, a quality dashboard, a Walkshed Analysis tool, GoInfoGame (iOS/Android), and Audiom (third party).
  — [TDEI-Deployment-Project](https://github.com/TaskarCenterAtUW/TDEI-Deployment-Project)
- **Workspaces.** The `TaskarCenterAtUW/workspaces-stack` monorepo bundles a frontend, backend APIs, a reverse proxy, the Rapid editor, a GTFS Pathways Editor, an OSW Tasking Manager and debug tooling. — [TDEI-Deployment-Project](https://github.com/TaskarCenterAtUW/TDEI-Deployment-Project)
- **AccessMap Multimodal** (`TaskarCenterAtUW/AccessMap`) is a trip planner. Users set sidewalk preferences (for example incline limits and curb needs) and get suitable routes. — [TDEI-Deployment-Project](https://github.com/TaskarCenterAtUW/TDEI-Deployment-Project)
- **Funding and timeline.** TDEI is a USDOT ITS4US deployment run through UW. It aims to give cities "detailed, accurate, and standardized data" on footpaths, sidewalks and crossings, and its portal covers six demonstration counties (e.g., King County WA, Multnomah County OR). Data is delivered as zipped OSW files. A TRB 2025 presentation says Phase II funding ran to March 2025 and that Phases II/III continue into 2026. — [data.gov ITS4US TDEI](https://catalog.data.gov/dataset/its4us-uw-transportation-data-exchange-initiative-tdei); [TCAT TRB 2025 slides](https://tcat.cs.washington.edu/wp-content/uploads/TDEI/TRB2025TDEI.pdf) (both from search snippets; not fetched in full)
- **Earlier AccessMap paper.** The original paper on sidewalk visualization and routing for people with limited mobility is a precursor of AccessMap/OSW. — [arXiv 1602.04281](https://arxiv.org/pdf/1602.04281)

### Inferences
- OSW's tags are OSM tags, so a Lebanon dataset in OSW form can be pushed to OSM with the TDEI formatter. It can also be validated with `python-osw-validation` before publishing, at no extra schema-design cost.
- The team's GeoPackage (sidewalk polygons, width lines, obstruction points) maps roughly onto OSW:
  - polygons become Zones or adjacent polygons;
  - sidewalk centrelines must be derived as Edges carrying `width`;
  - obstructions become adjacent Points or barrier Nodes.
  The polygon-first model will therefore need a centreline/network derivation step.
- The DEM incline job could run on a Lebanese DEM. Beirut's hilly terrain (Achrafieh) makes incline a high-value attribute.

### Gaps
- The exact licence of the OSW schema repo, the TDEI repos, Workspaces and AccessMap was not confirmed. The pages showed LICENSE files but no licence names. Check each repo's LICENSE before reuse.
- Commit dates and maintenance cadence were not visible. OSW 0.3 (Jan 2026) shows the schema is active, and TDEI funding continues into 2026.
- Whether TDEI/Workspaces can be self-hosted outside the US demonstration regions was not documented in the sources read.
- The content of "OSWDataPipeline" (the pipeline that generates OSW from sources) was not found.

## Q2. Tools that generate sidewalk networks or polygons from centerlines, buildings or imagery; sidewalk-width map projects

### Takeaway
There are three families of tools:
- **Centreline offset (rule-based):** AccessMap sidewalkify plus crossify. Rough, but needs only OSM streets and side/offset attributes.
- **Imagery segmentation to polygons plus network:** Tile2Net (NYU, BSD-3, beta). Needs a GPU and sub-metre orthophotos.
- **Polygon to centreline to width:** Meli Harvey's sidewalk-widths code, reused by many "sidewalk widths" maps.

None is a turnkey building-footprint-to-curb tool. Lebanon's polygons-plus-footprints setup is closest to the sidewalk-widths workflow.

### Cited Findings
- **sidewalkify (AccessMap).** A Python CLI/library "for extrapolating sidewalk lines from annotated streets".
  - **Input:** any GeoPandas-readable file with `sw_left`/`sw_right` offset columns (a negative value means no sidewalk).
  - **Method:** Shapely `parallel_offset`, then graph-based cleanup that trims overshoots and joins undershoots.
  - **Output:** GeoJSON lines.
  - **Licence:** dual MIT/Apache-2.0.
  - **Activity:** 57 commits, 16 stars, 1 open issue, 2 open PRs. Last-commit date not shown.
  - **Requirements:** Python 3.7+; click, networkx, geopandas.
  — [AccessMap/sidewalkify](https://github.com/AccessMap/sidewalkify)
- **crossify (AccessMap)** draws first-order approximations of street crossings to complete a minimal pedestrian network from labelled streets. — [AccessMap/crossify](https://github.com/AccessMap/crossify)
- **Caveat from OpenSidewalks.** On the OSM accessibility list, an OpenSidewalks maintainer said that estimating sidewalks from centrelines gives only rough results. The real pipeline relies on "a fairly sophisticated ETL process" combining GIS, graph-theoretic and tabular techniques. — [OSM accessibility mailing list, Jan 2021](https://lists.openstreetmap.org/pipermail/accessibility/2021-January/000446.html)
- **Tile2Net (VIDA-NYU).** An "end-to-end tool for automated mapping of pedestrian infrastructure from aerial imagery".
  - **What it does:** segments roads, sidewalks, footpaths and crosswalks, then produces polygons plus a pedestrian centreline network.
  - **Output:** GeoParquet by default (Shapefile optional), in EPSG:4326.
  - **Licence:** BSD-3-Clause.
  - **Activity:** 371 commits, 234 stars, 35 forks, no tagged releases. The README calls it a "Beta Version" that is "not yet ready for production use".
  - **Requirements:** a CUDA GPU and Python 3.11-3.14.
  - **Coverage:** named regions are Boston, Cambridge, NYC, DC, Alameda County and Oregon. Custom imagery is accepted via DATA_PREPARE.md.
  — [VIDA-NYU/tile2net](https://github.com/VIDA-NYU/tile2net)
- **Tile2Net paper.** Hosseini, Sevtsuk, Miranda, Cesar, Silva (2023), "Mapping the walk: A scalable computer vision approach for generating sidewalk network datasets from aerial imagery", *CEUS*, doi:10.1016/j.compenvurbsys.2023.101950. The model was trained on Cambridge MA, DC and NYC imagery and piloted in Manhattan, DC, Boston and Cambridge. — [EVL/UIC PDF](https://www.evl.uic.edu/documents/ceus_mappingthewalk_miranda.pdf); [NSF PAR](https://par.nsf.gov/biblio/10493942-mapping-walk-scalable-computer-vision-approach-generating-sidewalk-network-datasets-from-aerial-imagery)
- **Sidewalk Widths NYC (Meli Harvey).**
  - **Method:** takes planimetric sidewalk polygons; dissolves adjacent polygons; extracts and simplifies centrelines; measures the distance from centreline to polygon edge to get width.
  - **Data:** NYC's 2024 Sidewalk dataset, covering 5 boroughs. Notebooks and GeoJSON output are in the repo.
  - **No-polygon cities:** the README notes these may need another way to build polygons, e.g. "curbs to parcel boundaries".
  — [meliharvey/sidewalkwidths-nyc](https://github.com/meliharvey/sidewalkwidths-nyc/blob/master/README.md)
- **Toronto fork.** sharedstreets/sidewalkwidths-toronto adapts the same pipeline to Toronto's open sidewalk dataset. — [sharedstreets/sidewalkwidths-toronto](https://github.com/sharedstreets/sidewalkwidths-toronto)
- **The global index.** meliharvey/sidewalkwidths (sidewalkwidths.com) indexes worldwide maps made "by grassroots cartographers ... in response to COVID-19". Each was created independently but shares NYC source code. No LICENSE file was visible in the index repo. — [meliharvey/sidewalkwidths](https://github.com/meliharvey/sidewalkwidths); [La Fabrique des Mobilités wiki](https://wiki.lafabriquedesmobilites.fr/wiki/Sidewalk_widths_-_Sharedstreet)
- **Paris.**
  - The City's "Trottoirs - données géographiques" vector dataset is ODbL, last updated 5 Nov 2014. A separate "Plan de voirie - Trottoirs - emprises" layer also exists. — [data.gouv.fr Trottoirs](https://www.data.gouv.fr/en/datasets/trottoirs-donnees-geographiques-prs/)
  - The `laem/trottoirs-de-paris` project computes sidewalk shapes from city building polygons plus sidewalk lines. This is a building-to-curb style method, but its README was not read. — [laem/trottoirs-de-paris](https://github.com/laem/trottoirs-de-paris)
  - A data.gouv.fr dataset of Paris pedestrian paths derived from OSM also exists. — [Cheminements piétons dans Paris d'après OSM](https://www.data.gouv.fr/datasets/65f05eaa403de89de3503083)
- **French width norms.** The regulatory absolute minimum is 1.40 m and the recommended width is 1.80 m. These are useful thresholds for classification. — [Wallonie mobilité QC09](https://mobilite-waf.wallonie.be/files/eDocsMobilite/Conseiller%20en%20mobilit%c3%a9/question%20de%20cem/QC09_largeur-trottoir.pdf)

### Inferences
- **Recommended Beirut generation path.** Run sidewalkify on OSM streets to get a seed network. Snap or clip it against the Microsoft building-footprint frontage and the manually traced polygons. Then use the Harvey centreline/width approach on the traced polygons to fill `width` automatically.
- **Footprints as a proxy.** Footprints stand in for the property line in a building-to-curb width, but only where buildings sit on the lot line. That is common in old Beirut, but less so in newer setback developments.
- **Tile2Net in Lebanon.** It would need fine-tuning on locally labelled Esri/orthophoto tiles. The licence for using Esri World Imagery as ML input should be checked separately.

### Gaps
- No dedicated building-footprint-plus-centreline "sidewalk polygon generator" with published code was found.
- No source was read for "osm-sidewalks", for OSMnx-specific sidewalk generation (OSMnx itself is a graph tool, not a sidewalk generator), or for osm2streets.
- The Amsterdam "Stoepbreedte", Madrid, Barcelona, Brussels and Montreal width maps were not individually verified. Their methods, code and licences remain unconfirmed; the sidewalkwidths.com index would list them.
- Tile2Net accuracy figures were not extracted from the paper.

## Q3. Fusing overhead and street-level imagery, and validation/QA methods

### Takeaway
The canonical fusion design is Ning et al. 2022: aerial segmentation first, then street-view imagery (SVI) to restore occluded or missing segments. Newer SVI-only width estimators reach about 0.25 m MAE on one benchmark (UrbanVGGT, 2026). For QA, Project Sidewalk shows that multiple independent labellers per street raise recall sharply, from 68% to 92% with five labellers, while precision stays around 70%. That argues for redundant labelling plus expert validation of a stratified sample.

### Cited Findings
- **Ning et al. 2022.** Ning, Ye, Chen, Liu, Cao, "Sidewalk extraction using aerial and street view images", *Environment and Planning B* 49(1):7-22, doi:10.1177/2399808321995817. Neural networks extract sidewalks from aerial imagery, and pre-trained models applied to street-view images restore occluded or missing sidewalks. The authors warn that public SVI may not cover the whole area and may be out of date. — [IDEAS/RePEc](https://ideas.repec.org/a/sae/envirb/v49y2022i1p7-22.html); [NJIT record](https://researchwith.njit.edu/en/publications/sidewalk-extraction-using-aerial-and-street-view-images/)
- **Ning et al. (CEUS 2022), SVI only.** "Converting street view images to land cover maps for metric mapping: a case study on sidewalk network extraction for the wheelchair users" uses SVI plus depth to make metric sidewalk maps. — [PSU Pure](https://pure.psu.edu/en/publications/converting-street-view-images-to-land-cover-maps-for-metric-mappi/)
- **UrbanVGGT (Tan and Zhang, arXiv 2603.22531 / ISPRS Archives 2026).**
  - **Pipeline:** SVI semantic segmentation; feed-forward 3D reconstruction; ground-plane fitting; camera-height scale calibration; directional width measurement.
  - **Accuracy:** MAE 0.252 m, with 95.5% of estimates within 0.50 m, on a Washington DC benchmark.
  - **Dataset:** produced SV-SideWidth, covering 527 OSM segments in three cities.
  - **Authors' caveat:** outputs are provisional and need local ground-truth audits.
  - **Gap they quantify:** 0 sidewalk-width tags among 461 NYC Midtown and 1,958 Nairobi CBD drivable segments.
  — [ISPRS Archives paper](https://isprs-archives.copernicus.org/articles/XLIX-B2-2026/559/2026/); [author poster](https://tantansir.github.io/assets/poster.pdf)
- **Other recent width work** (from snippets only, no figures verified):
  - A Zurich GISRUK 2025 comparison found spatial-data analysis gave broader coverage and more accurate widths than the SVI approach.
  - A 2026 Vienna thesis reported 64% overall agreement with a reference dataset.
  — [Zenodo record](https://zenodo.org/records/15182508); [TU Wien repositum](https://repositum.tuwien.at/handle/20.500.12708/229239?mode=full)
- **Project Sidewalk (UW Makeability Lab), CHI 2019, DC deployment.**
  - Precision was about 70% across paid and volunteer groups.
  - Recall was 68% for paid workers, versus 61% for registered and 49% for anonymous volunteers.
  - With five labellers per street, recall rose from 68% to 92%.
  - Weak spots: missing curb ramps (20.5% precision) and surface problems (27.1% recall).
  — [Saha et al. CHI 2019 PDF](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf)
- **Crowd+AI (2022).** A model trained on DC achieved 81.3% average precision and 77.2% recall for auto-validation, with curb ramps best at 93.2% P and 96.8% R. Cross-city results were 76-81% P and 83-90% R in Seattle and Newberg, OR. — [arXiv 2206.13677](https://arxiv.org/pdf/2206.13677); [Duan et al. ASSETS 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **Project Sidewalk scale.** It had expanded to 20 cities by 2024. Its Sidewalk Presence API reports tiered precision/recall for "no sidewalk" labels: 69% P / 79% R at one or more labels, and 80% P / 67% R at two or more. Amsterdam is one deployment. — [arXiv 2403.09810](https://arxiv.org/html/2403.09810v1); [Project Sidewalk Amsterdam API docs](https://sidewalk-amsterdam.cs.washington.edu/v3/api-docs/sidewalkPresence)

### Inferences
- **Fusion sequence for Lebanon.**
  1. Trace or segment from overhead imagery (polygons).
  2. Use Mapillary SVI to fill under-canopy or under-balcony occlusions and to attribute obstructions, kerbs and surface.
  3. Field-audit a stratified random sample of segments (stratify by district or street class) to measure accuracy.
- **Metrics to report:**
  - geometry: completeness (recall) and correctness (precision) by length, with a buffer-matching tolerance; IoU for polygons;
  - width: MAE and the share within ±0.5 m;
  - attributes: Cohen's kappa for inter-rater agreement.
  This follows standard practice; the specific metric set is a recommendation, not taken from one source.
- **Redundant labelling.** Project Sidewalk's results suggest at least 3 independent validators per segment for attribute labels in the crowdsourcing phase.

### Gaps
- No HeiGIT sidewalk/OSM-enrichment project, Urban Institute pipeline or World Bank pipeline was located in the searches done.
- No formal published sampling-design guidance specific to sidewalk inventories was found.
- No published IoU or completeness figures for Tile2Net were extracted.

## Q4. Publishing: OSM tagging, import policy, crowdsourced validation, licence compatibility

### Takeaway
OSM supports two schemes: `sidewalk=*` tags on the street, or separate `highway=footway`+`footway=sidewalk` ways. Detailed accessibility data favours the separate-way scheme, with `kerb=*` nodes at crossings and `width`, `surface` and `smoothness` tags. Any bulk upload counts as an import. That needs local community buy-in, an import-list/forum review and ODbL-compatible sources. Mapillary explicitly permits deriving data from its imagery into OSM, which settles the CC BY-SA concern for OSM. Republishing Mapillary-derived data outside OSM requires ODbL.

### Cited Findings
- **Street-tag scheme.** Uses `sidewalk=both|left|right|separate|no` on the road, with sub-tags such as `sidewalk:left:width=3`, `sidewalk:left:kerb=raised` and `sidewalk:both:surface=paving_stones`. Geometry is approximate and not rendered on the standard map. — [OSM wiki: Sidewalks](https://wiki.openstreetmap.org/wiki/Sidewalks)
- **Separate-way scheme.** Uses `highway=footway`+`footway=sidewalk`, with the road tagged `sidewalk:*=separate` and optionally `foot=use_sidepath`. It allows precise geometry plus `barrier`, `tactile_paving`, `kerb` and `surface`.
  - Crossings use `footway=crossing` ways with `kerb=*` nodes at the kerb position.
  - Separate ways are recommended where a barrier or verge prevents continuous access, or where the sidewalk meanders.
  - Strips that are not safe for walking should not be tagged as sidewalks.
  - Mappers should follow local conventions and consult the local community before switching scheme. Separate ways dominate in North America and Eastern Europe; road tags dominate in the UK, Western Europe and South America.
  — [OSM wiki: Sidewalks](https://wiki.openstreetmap.org/wiki/Sidewalks)
- **Width tagging.** The OSM wiki recommends `sidewalk:<side>:width` for sidewalk width, and notes that street-width definitions vary. — [OSM wiki FR:Key:width](https://wiki.openstreetmap.org/wiki/FR:Key:width)
- **Import Guidelines.** An import must not proceed without local community buy-in. It needs a review post on the community forum or imports list, tagged `import` and `import-proposal`. Importers must obtain proper permission or licence from the data owner and be able to agree to the Contributor Terms (ODbL since 2012). The Data Working Group can stop non-compliant imports and block accounts. — [OSM wiki: Import/Guidelines](https://wiki.openstreetmap.org/Import/Guidelines)
- **Precedent for a footprint import.** The Microsoft building footprint import in Orlando, FL is documented on the OSM wiki. — [OSM wiki: Orlando Microsoft Building Import](https://wiki.openstreetmap.org/wiki/Orlando,_Florida_Microsoft_Building_Import)
- **Mapillary licence and permission.**
  - Images are CC BY-SA 4.0.
  - Mapillary's help centre says all images and derived metadata may be used to edit OSM, freely and permanently, under the OSMF contributor terms.
  - Derived data may be published elsewhere only if it is publicly accessible and ODbL-licensed.
  - Attribution is requested, e.g. `source=Mapillary`.
  - The permission excludes logos and map tiles.
  — [Mapillary Help Center](https://help.mapillary.com/hc/en-us/articles/115001777705); [OSM wiki: Mapillary](https://wiki.openstreetmap.org/wiki/Mapillary)
- **Forum caveat.** A Mapillary forum thread (older) describes the OSM permission as a narrower exception to CC BY-SA. — [Mapillary forum](https://forum.mapillary.com/t/opening-up-for-3rd-party-cc-by-content/739)

### Inferences
- **Two release channels for Lebanon.**
  1. OSM, via manual or semi-automated editing in a tasking workflow. This needs Lebanese OSM community consultation, and the street-tag vs separate-way choice should be agreed locally.
  2. An ODbL open-data release (GeoPackage/OSW GeoJSON) for planners.
- **Licence check on traced geometry.** Before any OSM contribution, confirm that Esri World Imagery tracing is permitted for OSM. Esri has granted OSM tracing permission for World Imagery in editors, but this was not verified in this research. Also confirm the Microsoft footprint licence (ODbL, per prior imports) before deriving sidewalks from them.
- **Tasking split.** Tasking Manager or MapRoulette challenges suit validating generated candidates one by one rather than bulk upload. The guidelines still apply to any automated or bulk part. This is an inference; no MapRoulette-specific sidewalk policy was found.

### Gaps
- No MapRoulette or HOT Tasking Manager sidewalk-specific workflow documentation was retrieved.
- The current Lebanese OSM community conventions on the sidewalk scheme were not researched.
- The Esri World Imagery OSM tracing permission and the Microsoft Global ML Building Footprints licence (2026 release) were not verified in this session.

## Q5. Accessibility routing and analysis on the result

### Takeaway
The OSW/TDEI ecosystem already includes AccessMap Multimodal for preference-based routing (incline, curbs) and a Walkshed Analysis tool. Feeding an OSW-conformant Lebanese dataset into these is the lowest-friction route to routing and analysis.

### Cited Findings
- **AccessMap Multimodal.** A trip planner where users set sidewalk preferences and get suitable routes. — [TDEI-Deployment-Project](https://github.com/TaskarCenterAtUW/TDEI-Deployment-Project)
- **Supporting jobs.** TDEI includes a WalkshedTool, a DEM incline-tagging job (incline feeds routing cost) and quality/confidence metric jobs. — [TDEI-Deployment-Project](https://github.com/TaskarCenterAtUW/TDEI-Deployment-Project)
- **Original AccessMap work.** Covers sidewalk visualization and routing for individuals with limited mobility. — [arXiv 1602.04281](https://arxiv.org/pdf/1602.04281)
- **Routing robustness.** Separate-way OSM mapping gives better crossings for routing. Routing breaks at unmapped informal crossings unless crossings or `footway=link` connectors are mapped. — [OSM wiki: Sidewalks](https://wiki.openstreetmap.org/wiki/Sidewalks)

### Inferences
- The minimum attribute set for useful accessibility routing in Beirut is:
  - width (with obstruction-reduced "effective width");
  - incline;
  - `kerb` at every crossing node;
  - surface/smoothness;
  - obstruction points (cars, generators, kiosks).
- The network must be topologically connected via crossing edges; crossify can seed these.

### Gaps
- OpenTripPlanner pedestrian routing configuration, pedestrian level-of-service indices (e.g., HCM-style PLOS) and walkability indices were not researched in this session. No citations were collected, and the report writer should not make claims about them from these notes.
