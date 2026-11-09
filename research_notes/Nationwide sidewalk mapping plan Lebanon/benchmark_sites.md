# Benchmark sites and gold-standard protocol for a Lebanese sidewalk-mapping pipeline

Scope: where to benchmark (external and Beirut), which ML benchmarks to reuse, a field protocol for a Beirut gold standard, and how large it must be. Research date: 2026-11-06. About 33 tool calls. Several portals could not be opened directly; those points are flagged as gaps. Sample-size numbers are computed here; the formulas and inputs are shown.

## Q1. External ground truth: which cities publish open sidewalk geometry, width or obstacle data usable as a benchmark?

### Takeaway
No Mediterranean or MENA city that I could verify publishes an open *width* attribute together with obstacle inventories. The strongest open benchmarks split by what they test:
- **Geometry and curb lines:** Paris (ODbL, curb lines plus sidewalk footprint polygons, updated monthly).
- **Polygons and published width-model benchmarks:** NYC and DC planimetrics. The UrbanVGGT DC benchmark is the only published width benchmark built with a pipeline like the team's.
- **Explicit width attributes:** Amsterdam (2017) and the City of London.
- **Obstacle labels (CC0):** Project Sidewalk, including Mexico City.
- **Field-measured effective width, slope and condition from pedestrian-level phones:** Seoul (514 images).

Barcelona, Madrid, Tel Aviv and Istanbul did not have a verifiable open sidewalk-width layer.

### Cited Findings
**Paris (best European geometry and curb benchmark; dense historic fabric)**
- "Plan de voirie – Trottoirs – emprises" holds sidewalk footprint polygons ("surface of road space reserved in priority for pedestrians"). Licence ODbL. Last updated 10 Oct 2026; resources updated about monthly. Formats: CSV (68.8 MB), JSON (89.2 MB), ZIP (19.7 MB). CRS: Lambert 93 (EPSG:2154) and Web Mercator. Publisher: Direction de la Voirie et des Déplacements. The page warns the data "cannot be used for topographic work" and that exhaustive updating is not guaranteed. A forum post reports one block's sidewalks missing. There is no width or obstacle attribute. — [data.gouv.fr Trottoirs-emprises](https://www.data.gouv.fr/datasets/plan-de-voirie-trottoirs-emprises)
- "Plan de voirie – Trottoirs filaires" holds sidewalk curbs (bordures), stair and bike-path edges, and quays. It is updated monthly and belongs to the 60-layer Plan de Voirie de Paris (PVP). Contact: pvp.dvd@paris.fr. — [data.gouv.fr Trottoirs filaires](https://www.data.gouv.fr/datasets/plan-de-voirie-trottoirs-filaires)
- Related PVP layers on the same portal: pedestrian crossings (Passages piétons), Terre-pleins and Chaussées (carriageways). — [Passages piétons](https://www.data.gouv.fr/datasets/plan-de-voirie-passages-pietons); [Chaussées](https://www.data.gouv.fr/datasets/plan-de-voirie-chaussees)
- A prior open project ("trottoirs de paris") computed widths from the curb-line GeoJSON and building polygons. This shows width must be derived from geometry rather than read from an attribute. — [GitHub laem/trottoirs-de-paris](https://github.com/laem/trottoirs-de-paris)

**New York City and Washington DC (polygons, plus the only published width-model benchmark)**
- "NYC Planimetric Database: Sidewalk" is a sidewalk polygon layer on data.cityofnewyork.us (ID 52n9-sdep), last modified 2025-12-10. NYC also publishes a "Pavement Edge" layer (curb or edge of pavement). — [data.gov NYC Sidewalk](https://catalog.data.gov/dataset/nyc-planimetric-database-sidewalk); [Pavement Edge](https://catalog.data.gov/dataset/nyc-planimetric-database-pavement-edge)
- An open project derived NYC sidewalk widths from these polygons. — [meliharvey/sidewalkwidths-nyc](https://www.github.com/meliharvey/sidewalkwidths-nyc)
- "Sidewalks 2021" (DC OCTO) covers all public walkways; individual resident sidewalks are not captured. Licence CC BY 4.0, formats GeoJSON and SHP. The same features appear as "Sidewalks and Stairs" in the Planimetrics_2021 map service. Catalog dates conflict (modified 2022-02-04, issued 2024-03-25). — [data.gov Sidewalks 2021](https://catalog.data.gov/dataset/sidewalks-2021); [DC GIS Planimetrics_2021 layer 11](https://maps2.dcgis.dc.gov/DCGIS/rest/services/DCGIS_DATA/Planimetrics_2021/MapServer/11/iteminfo)
- **UrbanVGGT** (Tan & Zhang, arXiv 2603.22531, Mar 2026; ISPRS Archives XLIX-B2-2026) is the published method closest to the team's pipeline: segmentation, feed-forward 3D (VGGT), ground-plane fit and camera-height scale.
  - DC benchmark: about 300 Google Street View images (640×640, 90° FOV) taken from the Lieu & Guhathakurta (2025) dataset, with reference widths of 0.56–3.94 m and a fixed 2.5 m camera height.
  - Results: MAE 0.252 m, RMSE 0.293 m, bias −0.055 m; 49.9% within 0.25 m and 95.5% within 0.50 m.
  - Ablations (MAE): no scale calibration 1.571 m; pinhole only 1.096 m; camera height 2.0 m gives 0.384 m (bias −0.380); 3.0 m gives 0.349 m (bias +0.263).
  - Failure modes: occlusion by parked cars and poles, narrow sidewalks, driveway ramps and curb cuts, bulb-outs and bus stops, shared-space streets.
  - SV-SideWidth: 527 OSM segments from NYC, São Paulo and Nairobi, explicitly *not validated*. The paper states no code or data release. — [arXiv HTML 2603.22531](https://arxiv.org/html/2603.22531); [ISPRS Archives](https://isprs-archives.copernicus.org/articles/XLIX-B2-2026/559/2026/)
- **Tile2Net** (Hosseini et al., CEUS 2023, DOI 10.1016/j.compenvurbsys.2023.101950) was piloted in Manhattan, DC, Boston and Cambridge MA. It uses official network and polygon data as reference and outputs sidewalk, crosswalk and footpath polygons plus centerlines. I could not extract the per-city metric values from the PDF. — [EVL UIC PDF](https://www.evl.uic.edu/documents/ceus_mappingthewalk_miranda.pdf); [NSF PAR copy](https://par.nsf.gov/servlets/purl/10493942)

**Amsterdam and City of London (explicit width attributes)**
- Amsterdam "Voetpaden breedte" (Open Geodata k=299): about 4,615 features, GeoJSON and XLSX, published by Verkeer en Openbare Ruimte, version notes 2017, public access. — [CKAN mirror](https://ckan.bertha.geodan.nl/dataset/amsterdam-open-geodata-299-voetpaden-breedte)
- The "Voetgangerskaart – indicatoren" dataset includes "stoepbreedtes_bruto" (gross sidewalk width classes per pedestrian segment). Licence CC BY 4.0, updated Jan 2022; geographic extent unconfirmed. — [dataplatform.nl](https://ckan-dataplatform-nl.dataplatform.nl/en/dataset/voetgangerskaart/resource/cf8a3832-5bfe-40cb-bb09-0b1f81f2e0b1)
- City of London "Pavement Widths Line" (INSPIRE service, based on OS mapping): each line carries a local pavement-width value, with a caveat that it may not reflect recent changes. — [City of London ArcGIS layer 98](https://www.mapping.cityoflondon.gov.uk/arcgis/rest/services/INSPIRE/MapServer/98)

**Barcelona (Mediterranean form; no verified width layer)**
- "ampliacio-voreres-bici-bcn" covers tactical COVID-era sidewalk widenings, CC BY 4.0. Updates stopped 4 Oct 2022 and only the historical series has been kept since 31 Mar 2023. It is not a width inventory. — [Open Data BCN](https://opendata-ajuntament.barcelona.cat/data/en/dataset/ampliacio-voreres-bici-bcn)
- "accessibilitat-via-publica" provides geolocated accessibility parameters for public space (2022_Accessibilitat_barris.csv). Its fields could not be confirmed. — [Open Data BCN accessibilitat](https://opendata-ajuntament.barcelona.cat/data/en/dataset/accessibilitat-via-publica/resource/ab4beb40-f945-421f-92c0-0cc1efcac93b)
- Barcelona also publishes a topographic base map, from which curb geometry could be derived (unverified). — [datos.gob.es BCN topographic base map](https://datos.gob.es/en/catalogo/l01080193-mapa-base-topografico-de-la-ciduad-de-barcelona)

**Madrid (no open width layer found)**
- Since 2010 the municipal Cartography Department has computed sidewalk width at addresses with registered vados (driveway permits) for the tax agency. The method is documented in a June 2021 technical annex, but the output is not shown as open data. — [Madrid transparency annex](https://transparencia.madrid.es/FWProjects/transparencia/InformacionJuridica/HuellaNormativa/Fiscales/2022/Dominio/Ficheros/Anexo1_InformeTecnicoEconomico.pdf)
- The "Distanciamiento peatonal" app (INSPIDE) shows sidewalk width at every point in Madrid city; its code is MIT-licensed. It is built on 1:1000 municipal cartography. — [datos.gob.es app](https://datos.gob.es/en/aplicaciones/distanciamiento-peatonal-inspide); [Cartografía 1:1000](https://datos.gob.es/en/catalogo/l01280796-cartografia-actualizada-1-10001)

**Obstacle and accessibility labels: Project Sidewalk (includes Mexico City)**
- Project Sidewalk data are CC0 1.0; source imagery is excluded and stays under the provider's terms. Downloads come as CSV, GeoJSON or SHP, or through an API with four sections (metadata, labels and validations, accessibility scores, stats). Datasets: raw geolocated labels, plus a version aggregated by street, plus validations. Deployments cover 56 cities in 11 countries, with 1.5M+ labels, 2M+ validations and 30,000+ km explored. — [Project Sidewalk CDMX API](https://sidewalk-cdmx.cs.washington.edu/api); [About](https://sidewalk-cdmx.cs.washington.edu/about)
- Amsterdam and Pittsburgh deployments expose the same API. — [Amsterdam API stats](https://sidewalk-amsterdam.cs.washington.edu/v3/api-docs/overall-stats); [Pittsburgh streets API](https://sidewalk-pittsburgh.cs.washington.edu/v3/api-docs/streets)

**Seoul (field-measured pedestrian-level benchmark)**
- arXiv 2609.17882, "Can VLMs Reliably Assess Sidewalk Accessibility Attributes from Pedestrian-Level Imagery?":
  - Sites: 514 images from 4 Seoul sites — Seoul Senior Tower, Eunpyeong-gu (99); Yonsei Severance Hospital, Seodaemun-gu (197); Sinchon Montessori Kindergarten, Seodaemun-gu (100); Siloam Center for the Blind, Mapo-gu (118). About 11 h of fieldwork in July 2026.
  - Capture: iPhone 17 (26 mm equivalent) and iPhone 16 Pro (24 mm), held 1.0 m above ground and centred on the path. Width measured with a Sincon SD-70 laser distance meter.
  - Attributes: effective width (excludes street facilities and fixed obstacles), longitudinal slope, cross slope, and pavement grade A–E. Grade D means hazards on ≥50% of the surface; grade E means ≥75%. One rater graded condition.
  - Results: VLMs overestimate width by a median +0.40 m (GPT-5.2) to +1.05 m (InternVL3.5-8B). Calibrated 90% intervals have half-widths of about ±1.0–1.5 m.
  - The authors say images and field values are released, but the page gives no repository URL or licence. — [arXiv abs](https://arxiv.org/abs/2609.17882); [arXiv HTML](https://arxiv.org/html/2609.17882)

**Cities without a verified layer**
- Tel Aviv–Yafo: the open-data portal exists (opendata.tel-aviv.gov.il), but searches found no sidewalk layer. — [dataportals.org listing](https://dataportals.org/portal/tel-aviv-municipality-open-data)
- Istanbul: no İBB sidewalk-width dataset was found. Kadıköy district publishes a 2024 list of streets with sidewalk and road works (quantities of asphalt, pavers and curbs), but no widths. — [Kadıköy açık veri](https://acikveri.kadikoy.bel.tr/en/dataset/2024-yili-kaldirim-ve-yol-duzenlemesi-yapilan-sokaklar/resource/34aadb5d-4bac-4bef-9ea1-abffa05b1503)
- San Francisco has a "Sidewalk Widths (2014)" layer generated from an AECOM study. — [data.gov](https://catalog.data.gov/dataset/sidewalk-widths-2014)

### Inferences
Suitability ranking for a Beirut-like pipeline (my judgement, from the findings above):
1. **Paris.** Authoritative curb lines plus polygons, ODbL, monthly updates, dense pre-modern and Haussmannian fabric with narrow sidewalks. Derive the reference width as the polygon's medial-axis width, or the curb-line-to-building distance. Use it for overhead and geometry tests, and for total width only, since it has no obstacles or clear width.
2. **Washington DC.** Sidewalk polygons (CC BY 4.0) plus a published UrbanVGGT width benchmark with directly comparable metrics (MAE 0.252 m). Running the team's VGGT/MoGe module on the same Lieu & Guhathakurta sample, if obtainable, gives an apples-to-apples score. Urban form is unlike Beirut's.
3. **NYC.** Polygons, a pavement-edge layer and derived widths; large and well documented, and it is also the SV-SideWidth city.
4. **Project Sidewalk, especially Mexico City.** The only open, CC0, multi-city *obstacle* label set. CDMX has informal and Latin-American conditions closer to Beirut than US cities. Use it for obstruction recall and precision on comparable classes: Obstacle, SurfaceProblem, NoSidewalk, CurbRamp.
5. **Seoul.** The only open *field-measured* effective width, slope and condition set, from 1.0 m phone imagery — the same capture mode as a walking 360° rig. It is small (514 images), and the release URL needs confirming. The Zenodo DOI given in the brief (10.5281/zenodo.22699523) was not verifiable in this session.
6. **Amsterdam and City of London.** Width attributes are available, but Amsterdam's are 2017 vintage and both urban forms differ from Beirut.
7. **Barcelona and Madrid.** Most Mediterranean, but width is only derivable (Madrid through the INSPIDE app or 1:1000 cartography; Barcelona through its topographic base map). Worth asking the cities directly.

None of these sources gives a curb-height ground truth. Curb height must come from local fieldwork (Q4).

Mapillary coverage: Paris, NYC, DC, Amsterdam and Barcelona are generally well covered on Mapillary, but I could not quantify this without an API token. The team should verify per test polygon as described in the Q3 inferences.

### Gaps
- I could not open the Open Data BCN, Lisbon, Athens, Milan, Valencia, Jerusalem or İBB catalogues directly. Their sidewalk layers, if any, remain unconfirmed.
- Tile2Net per-city IoU, F1 and recall values: the PDF could not be text-extracted.
- I could not obtain Mapillary images-per-km for any benchmark city. The coverage map and API need a token, and no public statistics were found.
- Field schemas and positional accuracy for the NYC, DC and Paris layers were not verified. Paris gives no accuracy figure.
- Whether the Seoul data and the Lieu & Guhathakurta DC reference widths are downloadable.

## Q2. Existing ML benchmarks to reuse per module

### Takeaway
- **Width:** reuse the UrbanVGGT DC protocol and metrics (MAE, RMSE, bias, % within 0.25 m and 0.50 m), and the Seoul field set for pedestrian-level effective width.
- **Overhead:** PathwayBench (OpenSidewalks labels, 8 cities) and Tile2Net cities.
- **Obstacles:** Project Sidewalk (CC0), PEDESTRIAN (29 classes, 82k frames) and Roboflow SOD (22 classes).
- No dataset named "ROD" was found.

### Cited Findings
- **PathwayBench** (Zhang, Howe, Mehta, Bolten, Caspi; arXiv 2407.16875, 2024): a benchmark for extracting pedestrian pathway graphs from aerial imagery, focused on routability. It covers 3,000 km² across regions of 8 cities. The main evaluation is in Seattle, Portland and DC, using OpenSidewalks annotations validated by independent mappers. — [arXiv 2407.16875](https://arxiv.org/pdf/2407.16875)
- **UrbanVGGT DC benchmark:** about 300 GSV images, MAE 0.252 m (details in Q1). No release URL is stated. — [arXiv HTML 2603.22531](https://arxiv.org/html/2603.22531)
- **Seoul pedestrian-level set:** 514 images with effective width, slopes and A–E condition. — [arXiv 2609.17882](https://arxiv.org/html/2609.17882)
- **PEDESTRIAN** (arXiv 2512.19190, Dec 2025): an egocentric phone-video dataset of 29 common sidewalk obstacles. It has 340 videos and 82,120 extracted frames, with faces, plates and identifying signs blurred for GDPR. The authors state it is publicly available. — [arXiv 2512.19190](https://arxiv.org/abs/2512.19190v1)
- **Sidewalk Obstacle Detection (SOD)** on Roboflow Universe: 10,000 images, 30,834 instances, 22 classes (e.g., person, car, tree, curb). — [Roboflow SOD](https://universe.roboflow.com/lamao/sod-enect)
- **Project Sidewalk labels:** CC0, multi-city, including Mexico City and Amsterdam (details in Q1). — [Project Sidewalk API](https://sidewalk-cdmx.cs.washington.edu/api)
- **Tile2Net:** sidewalk, crosswalk and footpath polygons from orthophotos, with pilot cities Manhattan, DC, Boston and Cambridge. — [EVL UIC](https://www.evl.uic.edu/pubs/2703)

### Inferences
| Module | External benchmark | Metric to report |
|---|---|---|
| Overhead polygons and network | Paris PVP polygons and curbs; DC and NYC planimetrics; PathwayBench splits; Tile2Net cities | IoU, boundary F-score at 0.5 m and 1 m, PathwayBench routability metrics |
| Width (street-level 3D) | UrbanVGGT DC sample, Seoul effective width, Paris and NYC polygon-derived widths | MAE, RMSE, bias, % within 0.25 m and 0.50 m; same metrics as UrbanVGGT for comparability |
| Obstruction detection | Project Sidewalk CDMX (geolocated point labels), PEDESTRIAN, SOD | per-class AP50 on images; point-level precision and recall within a 5 m match radius against Project Sidewalk |

Map the team's 21 Lebanese classes onto PEDESTRIAN's 29 and SOD's 22 classes before scoring. Keep Lebanon-specific classes (generators, diesel tanks, vendor stalls, informal ramps) for the local set.

UrbanVGGT's ±1 m camera-height error raised MAE by about 0.1–0.13 m. For Mapillary and 360° imagery the team should log camera height per sequence (helmet, car roof or pole) or estimate it from the ground plane. In practice this is the largest controllable width error.

### Gaps
- No dataset named "ROD" (road and sidewalk obstacle) was found; the user's name may refer to a different dataset.
- Licences for PEDESTRIAN and SOD were not confirmed.
- I could not determine whether the Tile2Net test tiles or the PathwayBench splits are downloadable, or under which licence.

## Q3. Beirut local benchmark: which area, and which transfer-test area?

### Takeaway
Make **Mar Mikhael–Gemmayzeh–north Achrafieh** (the existing QGIS pilot) the primary gold-standard area, adding a **Hamra/Ras Beirut** stratum next to AUB. This combination:
- overlaps the MIT/AUB Community Streets study zones;
- covers arterial, local, stair, old-fabric and post-blast-rebuilt streets;
- has a known retrofit reference (Jeanne d'Arc Street, 1.5 m clear sidewalk).

Use **Tripoli** (Al-Mina, old city and Tell) as the out-of-city transfer test. The municipality is procuring GNSS RTK equipment (2026), and its urban form is distinct from Beirut's.

Bourj Hammoud serves as an in-Beirut stress test (dense, informal occupation).

### Cited Findings
- The MIT City Form Lab worked with AUB Civil Engineering (co-PI Prof. Maya Abou-Zeid; AUB team incl. Jawad Haddad, Mohamad Halabi, Rawad Makhlouf) on walkability after the 2020 blast. They compiled built-environment and land-use data, built a pedestrian model for morning, lunch and evening peaks, ran calibration counts, and held a June 2022 AUB workshop that produced 6 scenarios. Funded by DAR Group; published as Sevtsuk et al. 2024, *Cities*, DOI 10.1016/j.cities.2024.104927. — [MIT City Form Lab](https://cityform.mit.edu/projects/beirut-community-streets)
- The study areas listed are Hamra, Karantina, Mar Mikhael, Gemmayzeh and Jeitaoui. — [LCAU MIT Community Streets](https://lcau.mit.edu/node/80); [Venice 2023 catalogue](https://media.voog.com/0000/0036/2451/files/BeirutCommunityStreets_catalog_Venice2023.pdf)
- Findings reported in L'Orient Today:
  - A joint MIT-AUB study found nearly 20% of Beirut street length had sidewalks blocked by permanent fixtures (poles, trees, meters).
  - About 25 parked vehicles were counted on one 315 m street in Al Hikmeh.
  - An AUB-backed project removed a parking lane on Jeanne d'Arc Street (Hamra) to create a 1.5 m obstacle-free sidewalk; it took about 3 years.
  — [L'Orient Today, "Sidewalk struggles"](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html)
- After the 2020 blast, 220 OSM contributors made 516,553 edits, including 54,155 buildings, by early September 2020. This suggests detailed OSM in the blast zone (Mar Mikhael and Gemmayzeh). — [OSM wiki 2020 Beirut Port Explosion](https://wiki.openstreetmap.org/wiki/2020_Beirut_Port_Explosion)
- The OSM Lebanon wiki links Mapillary imagery from a "Lebanon drive" and a May 2019 Kaart ground survey of Beirut. — [OSM wiki Lebanon](https://wiki.openstreetmap.org/wiki/Lebanon)
- Mapillary images are openly licensed (CC BY-SA), and derived metadata may be used in OSM. — [Mapillary OSM page](https://mapillary.com/osm)
- An OSM wiki page exists for the October 2024 conflict mapping in Lebanon. Southern Beirut suburbs and the south were affected, which is relevant to security and access. — [OSM wiki Lebanon Conflict Oct 2024](https://wiki.openstreetmap.org/wiki/FR:Lebanon:_Conflict_-_October_2024)
- Tripoli municipality published a second call to purchase GNSS RTK equipment (July 2026). — [tripoli.gov.lb tender PDF](https://tripoli.gov.lb/wp-content/uploads/2026/07/شراء-GNSS-RTK-دعوة-ثانية.pdf)
- An AUB thesis on Hamra found many alleys and open spaces unused by pedestrians because of infrastructure, walls and parking. — [AUB ScholarWorks](https://scholarworks.aub.edu.lb/handle/10938/10036)

### Inferences
Comparison of candidate areas (qualitative; the Mapillary column should be confirmed with the API query described at the end of this list):

| Area | Existing reference data | Street-type diversity | Access and security | AUB proximity | Verdict |
|---|---|---|---|---|---|
| Mar Mikhael–Gemmayzeh–N. Achrafieh | MIT/AUB study zone; AUB 2010 curblines (on request); dense post-blast OSM; existing QGIS pilot | High: arterials (Armenia St, Charles Helou edge), old-fabric lanes, public stairs, post-blast rebuilt fronts, nightlife terraces (temporary occupation) | Good (central, East Beirut) | ~3 km | **Primary** |
| Hamra / Ras Beirut | MIT/AUB study zone; Jeanne d'Arc 1.5 m retrofit as known reference; AUB curblines | Medium–high: commercial grid, steep side streets, campus edge | Good | Adjacent | **Second stratum** (calibration, easy logistics) |
| Achrafieh / Sassine | AUB curblines; OSM good | Medium: residential towers, roundabouts, slopes | Good | ~4 km | Optional |
| Badaro | AUB curblines | Medium: tree-lined local grid, cafés | Good | ~3 km | Optional (trees and occlusion test) |
| Mazraa | AUB curblines | Arterials and dense mixed use | Moderate | ~2 km | Optional |
| Bourj Hammoud | Outside Municipal Beirut, so no AUB curblines | Very dense, informal occupation, narrow lanes | Moderate | ~5 km | **Stress test** (out-of-distribution) |

- **Transfer test:** use **Tripoli** (Al-Mina grid, Mamluk old city lanes, Tell and Azmi arterials). It differs in fabric, materials and imagery availability from Beirut, and municipal interest in RTK equipment suggests a potential partner. Saida (old souk plus modern corniche) or Jounieh (coastal linear strip, slopes) are alternatives.
- **Choosing the strata in Mapillary:** pull image density per stratum before choosing segments:
  - API v4 `https://graph.mapillary.com/images?fields=id,captured_at,computed_geometry,is_pano,camera_type&bbox=35.508,33.884,35.530,33.905` with a token, tiling the bbox into small cells.
  - Or use coverage vector tiles at z14.
  - Compute (i) images per km of OSM highway, (ii) % of street length with an image captured since 2022 within 10 m, and (iii) % panoramic.
  - Use these to stratify segments into well-covered and poorly covered. Reference: [Mapillary API docs](https://www.mapillary.com/developer/api-documentation).
- **Getting the AUB 2010 curblines (1:2,000):** request them early. At 1:2,000 they are a useful independent check on curb position, nominally about 0.5–1 m planimetric. Their 2010 date predates post-blast rebuilding, so field-verify them before treating them as truth.

### Gaps
- No Mapillary density figures for any Beirut neighbourhood were obtainable (API token needed; no published stats).
- The MIT/AUB per-street sidewalk data (presence, width, obstructions) and the survey methodology were not readable: the Dar report and catalogue PDFs did not text-extract.
- No sources were found on OSM sidewalk-tag completeness (sidewalk=*, width=*, kerb=*) by Beirut neighbourhood.
- Current security conditions per area could not be sourced; check with AUB or the municipality before fieldwork.

## Q4. Gold-standard field protocol (instruments, definitions, spacing, QA, throughput)

### Takeaway
Measure at fixed 10 m stations plus every pinch point, on both sides of each sampled segment:
- **Total width:** building or property line to the top of the curb face.
- **Clear (effective) width:** narrowest unobstructed passage; compare against 1.2 m (PROWAG), 1.5 m (Inclusive Mobility "constrained" minimum, Beirut's Jeanne d'Arc target) and 2.0 m (Inclusive Mobility preferred).
- **Curb height, cross slope, longitudinal slope.**
- **Condition:** A–E, using the Seoul scheme.
- **Obstruction inventory:** permanent versus temporary.

Geolocate stations with LEB-CORS network RTK (about ±3 cm). Double-measure 15–20% of segments for inter-rater reliability. Repeat obstruction passes in two to three time windows.

### Cited Findings
**Reference thresholds**
- PROWAG (Final Rule, Federal Register 8 Aug 2023, effective 7 Sep 2023):
  - Pedestrian access route continuous clear width of 48 in (1,220 mm) minimum; obstructions such as bollards must not reduce it below 1,220 mm, measured from the edge of the obstruction.
  - Where clear width is under 60 in (1,525 mm), 60×60 in passing spaces are required at ≤200 ft (61 m) intervals.
  - Cross slope outside crosswalks 1:48 (2.1%) max.
  - Enforcement depends on adoption by USDOT and DOJ.
  — [Federal Register 2023-16149](https://www.govinfo.gov/content/pkg/FR-2023-08-08/html/2023-16149.htm); [Access Board PDF](https://www.Access-board.Gov/files/prowag/2023-16149.pdf); [Kittelson summary](https://kittelson.com/ideas/the-final-rule-on-public-right-of-way-accessibility-guidelines-prowag-is-out-heres-what-you-need-to-know)
- UK Inclusive Mobility (DfT, Dec 2021):
  - Preferred minimum clear footway 2,000 mm; 1,500 mm acceptable where constrained (as summarised by Edinburgh's design guidance, which adapts the DfT guide).
  - DfT flags clear footway width under 1 m as a critical safety issue.
  — [DfT Inclusive Mobility PDF](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1044542/inclusive-mobility-a-guide-to-best-practice-on-access-to-pedestrian-and-transport-infrastructure.pdf); [Edinburgh P3 Footways](https://www.edinburgh.gov.uk/downloads/file/24977/p3---footways---version-11); [DfT critical safety issues](https://www.gov.uk/government/publications/critical-safety-issues-for-walking-wheeling-and-cycling/critical-safety-issues-for-walking-wheeling-and-cycling)
- Kerb heights:
  - Edinburgh standard kerb is 75–100 mm above the carriageway. — [Edinburgh P3](https://www.edinburgh.gov.uk/downloads/file/24977/p3---footways---version-11)
  - DfT tactile guidance references a 25 mm minimum kerb upstand for visually impaired users, a figure that was challenged in court. — [Highways Magazine](https://www.highwaysmagazine.co.uk/news/dft/dft-court-appeal-challenge-kerb-heights)
  - Transport Scotland's study calculated an equitable upstand of 40–50 mm. — [Transport Scotland Inclusive Kerb Study Phase 2](https://www.transport.gov.scot/media/bvlnk4xt/inclusive-kerb-study-phase-2.pdf)

**Precedent protocol (Seoul 2026)**
- Images taken with phones held at 1.0 m and centred on the walking path; width measured with a Sincon SD-70 laser meter; effective width excludes street facilities and fixed obstacles.
- Cross slope measured from the right edge to the left edge of the walking surface; longitudinal slope along the walking direction.
- One rater gave A–E condition grades; repeatability was not reported.
- Throughput: 514 images in about 11 field hours. — [arXiv 2609.17882](https://arxiv.org/html/2609.17882)

**Georeferencing**
- LEB-CORS (Directorate of Geographic Affairs, Lebanese Army): 13 stations, 24/7, network RTK at about ±3 cm, static processing, RINEX downloads. Coverage depends on internet connectivity. Cost about $700k, funded by USAID and the DGA budget. — [lebcors.army.gov.lb](https://lebcors.army.gov.lb); [LBCI news](https://www.lbcgroup.tv/news/lebanon-news/691386/lebanese-army-launches-online-network-to-facilitat/en)

**Inter-rater statistics**
- ICC guideline (Koo & Li 2016): ICC <0.5 poor, 0.5–0.75 moderate, 0.75–0.9 good, >0.9 excellent. — [Koo & Li 2016, J Chiropr Med](https://doi.org/10.1016/j.jcm.2016.02.012)

### Inferences
The protocol below is my design. Numbers not tied to a citation are planning estimates to validate in a pilot day.

**1. Sampling unit**
- An OSM street segment (intersection to intersection), split into sidewalk "faces" (left and right).
- Stations every 10 m along the face, measured from the segment start with a measuring wheel or chainage.
- Add a station at every pinch point: the narrowest point at a pole, tree, generator, ramp or step.

**2. Definitions per station** (record in a QField/ODK form tied to the station ID)
- **Total width (W_tot):** from the building face or property line to the top-back of the curb, perpendicular to the curb line.
- **Clear width (W_clear):** narrowest unobstructed passage at the station, ignoring *temporary* items. Measured from obstacle edge to obstacle edge, matching the PROWAG measurement rule.
- **Operational width (W_op):** like W_clear but including temporary occupation (parked cars, café furniture, vendor goods), recorded per time window.
- **Curb height (h_c):** top of curb to the carriageway or gutter surface at the curb face; mean of 2 readings 0.5 m apart.
- **Cross slope:** over a 0.6–1.0 m digital level across the walking zone, in %.
- **Longitudinal slope:** over 1–2 m along the path, in %.
- **Surface condition:** A–E, using the Seoul criteria.
- **Furniture-zone width.**
- **Presence flags:** curb ramp, steps or stairs, driveway apron.

**3. Obstruction inventory**
- For each object inside the sidewalk: class (the team's 21 Lebanese classes), RTK point, footprint dimensions (laser), whether permanent or temporary, and remaining clear width beside it.

**4. Instruments**
- Laser distance meter (Sincon SD-70-class or Leica DISTO-class).
- 5 m steel tape for curb height and short offsets.
- Measuring wheel for chainage.
- Digital level or inclinometer (0.1° resolution).
- RTK GNSS rover on LEB-CORS NRTK (about ±3 cm). Log fix status and drop any station without a fixed solution.
- Smartphone LiDAR (iPhone Pro, 3D Scanner or Polycam) at pinch points and stairs, for an independent 3D check.
- The team's own 360° camera on a pole at a known height (e.g., 2.0 m), captured along the same faces. This gives benchmark imagery with *known camera height*, which removes the UrbanVGGT camera-height error source.

**5. Photo documentation**
- One geotagged photo per station looking along the path, plus one perpendicular photo showing the measured span with the tape or laser visible.
- Blur faces and plates before any release.

**6. Time windows**
- At least two passes for temporary occupation: weekday 09:00–11:00 and weekday 18:00–21:00. Mar Mikhael and Gemmayzeh nightlife terraces and parking peak in the evening.
- Optionally a Saturday pass.
- Geometry (W_tot, h_c, slopes) is measured once. W_op and the temporary-obstruction inventory are recorded per pass.
- Capture the 360° imagery in the same windows so detections can be matched in time.

**7. Inter-rater reliability**
- 15–20% of faces are re-measured blind by a second team on another day.
- Report ICC(2,1) for W_tot, W_clear and h_c, aiming for >0.9 (excellent per Koo & Li). Also report Bland–Altman bias and limits of agreement.
- Report Cohen's κ for condition and for obstruction presence and class.
- If the human limits of agreement exceed about ±0.05 m, the model target of ±0.05 m is not resolvable. Field repeatability bounds the benchmark.

**8. Team and throughput (estimate)**
- 2-person teams: one measures, one records and handles RTK. At about 2 minutes per station (4 width readings, curb, 2 slopes, photo, RTK fix), expect about 30 stations/h, roughly 300 m of sidewalk face per hour.
- This is consistent with the Seoul pace of 514 images in 11 h, about 47 per hour, for simpler per-image records.
- Obstruction-only repeat passes run faster, perhaps 600–1,000 m/h.
- With 2 teams, about 20 km of faces takes about 35 team-hours, or 4–5 field days, plus repeat passes.

**9. Overhead ground truth**
- Digitise sidewalk polygons and curb lines from field RTK points, combined with the AUB 2010 curblines.
- Field-verify any AUB curbline that conflicts by more than 0.3 m.

### Gaps
- Protocols for MAPS, PEDS, ITDP Pedestrians First, and the "Morra/MIT scanner" were not retrieved in this session, so no cited details are available. Review them separately for item definitions.
- I could not verify the exact Inclusive Mobility 2021 wording (absolute minimum 1,000 mm over short lengths) from the primary PDF.
- No published field-throughput (m/hour) figures for sidewalk audits were found. The throughput above is an estimate.
- The accuracy of the Seoul SD-70 measurements and their repeatability were not reported.

## Q5. How big must the benchmark be?

### Takeaway
- **Width MAE within ±0.05 m (95%):** needs about 35 *independent* paired measurements if errors behave like UrbanVGGT's in DC. Beirut is likely harder, so plan for about 100 independent segments per reporting stratum. After clustering, that is roughly 400–600 station measurements per stratum.
- **Obstruction precision and recall within ±5%:** needs up to 385 ground-truth positives (recall) and 385 predicted positives (precision) per reported unit. This is feasible pooled, or for 4–5 super-classes, but not for each of the 21 classes (use ±10%, about 96 per class).

### Cited Findings
- UrbanVGGT DC error statistics: MAE 0.252 m, RMSE 0.293 m, bias −0.055 m. — [arXiv HTML 2603.22531](https://arxiv.org/html/2603.22531)

### Inferences
**Width MAE.** Required n = (z·σ_|e| / d)², with z = 1.96 and d = 0.05 m.
- From the DC numbers: SD(|e|) = √(RMSE² − MAE²) = √(0.0858 − 0.0635) ≈ 0.149 m. This gives n ≈ (1.96 × 0.149 / 0.05)² ≈ **34–35**.
- If Beirut errors are larger (SD(|e|) ≈ 0.25 m): n ≈ **96**. At 0.30 m: n ≈ **138**.
- Clustering: stations within a face are correlated. Design effect = 1 + (m − 1)·ICC. With m = 10 stations per 100 m face and an assumed ICC of 0.3, DEFF ≈ 3.7. About 100 effective samples therefore need about 370 stations, spread over at least 30–40 faces.

**Stratification** by street type (strata are reported separately):
1. Arterial
2. Collector/commercial
3. Local residential
4. Old-fabric lane (<6 m right-of-way)
5. Stairs and pedestrian-only

Two further crossed factors:
- Mapillary coverage: good versus poor.
- Sidewalk width: <1.2 m, 1.2–2.0 m and >2.0 m. Narrow sidewalks show the largest relative error.

**Recommended size.** 5 strata × 8 faces × about 100 m gives about 4 km of faces and about 400 stations per area. Hamra adds about 2 km, and the Tripoli transfer test about 2 km. In total about 8–10 km of sidewalk faces and about 1,000 stations. This takes about 30–35 team-hours of geometry work, plus repeat obstruction passes.

**Bias detection.** Detecting a systematic bias of 0.05 m with a paired test (α = 0.05, power 0.8) needs n ≈ ((1.96 + 0.84)·σ_e / 0.05)². With σ_e ≈ 0.29 m, n ≈ 264 effective pairs. Bias is harder to pin down than MAE.

**Obstruction precision and recall.** Required n = z²·p(1 − p) / d², with d = 0.05:
- p = 0.5 gives **385**; p = 0.8 gives **246**; p = 0.9 gives **139**.
- Recall's denominator is ground-truth objects; precision's is detections.
- Images cluster objects, so apply DEFF ≈ 1.3–1.5. That means about 500–580 GT objects pooled.
- Group the 21 classes into about 5 super-classes (fixed street furniture, vegetation, utilities and generators, vehicles, commercial and temporary occupation), each at about 100–385 objects.
- For rare classes, report counts with Wilson confidence intervals rather than claiming ±5%.

**Expected yield.** If Beirut has roughly 1 obstruction per 10–15 m of face (an assumption, consistent with ~20% of street length blocked by permanent fixtures per MIT/AUB), the 8–10 km benchmark yields about 600–1,000 GT objects per pass. That is enough for pooled ±5%.

**Overhead (polygon IoU and boundary F1).** Report per stratum. About 30–40 faces per stratum gives stable means, but this is not separately computed here.

### Gaps
- There are no Beirut-specific error variance or ICC values yet. Run a 1-day pilot of about 10 faces to estimate SD(|e|) and the within-face ICC, then recompute n.
- The obstruction density per km in Beirut is not published: the MIT/AUB data are not public.
