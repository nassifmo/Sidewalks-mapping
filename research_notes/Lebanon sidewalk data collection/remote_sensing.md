# Remote sensing (satellite / aerial imagery + deep learning) for sidewalk geometry, width and objects: applicability to Lebanon

Research date: 2026-11-06. About 18 tool calls. Wherever a source did not give a number, I say so rather than estimate one. Points marked "Inference" are my own reasoning, not sourced facts.

## Q1. Tile2Net and successor models: how they work, the resolution they need, accuracy, cities tested, and whether they can be retrained for Beirut

### Takeaway
Tile2Net (Hosseini et al., CEUS 2023) is the reference open-source pipeline. It segments aerial tiles into sidewalk, crosswalk, road and background (HRNet-W48 + OCR with hierarchical multi-scale attention). It then turns the masks into polygons and a routable centerline network. It was trained at about 19 cm GSD (zoom 20) on US cities. On test data it reaches 82.7% IoU for sidewalks, and on cities it never saw in training, about 74-88% of the official polygon area is covered. It supports retraining, but needs labelled masks for the new city. No Middle East or Mediterranean test exists. Newer options include a SAM-based fine-tune (GeoSAM, ECAI 2025) and Esri's packaged Tile2Net model. All of them are US-trained.

### Cited Findings
- **Pipeline.** Tile2Net is an end-to-end open-source Python tool. It downloads orthorectified slippy-map tiles, detects roads, sidewalks, crosswalks and footpaths, creates georeferenced polygons, and generates a topologically connected pedestrian network. — [Hosseini et al. 2023 (NSF PAR copy)](https://par.nsf.gov/servlets/purl/10493942); [GitHub VIDA-NYU/tile2net](https://github.com/VIDA-NYU/tile2net)
- **Model.** Hierarchical Multi-Scale Attention (Tao et al. 2020) with an HRNet-W48 + Object-Contextual Representations backbone. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- **Resolution used.** "We choose zoom level 20 for the 256x256-pixel tiles, where each pixel of the image represents 0.19 m." Four neighbouring tiles were stitched into 512x512 inputs, which gave about 12% higher mIoU, for about 20,000 training images. Each 512x512 image covers about 9,500 m². — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- **Training data.** 11,000 tiles from Washington DC, 28,000 from Cambridge MA and 8,000 from NYC parks. Orthoimagery came from MassGIS 2018, DC GIS 2020 and NYC GIS 2018. Labels came from existing municipal planimetric GIS layers. The split was 60/20/20 train/validation/test, with class-uniform sampling. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- **Test-set accuracy.** mIoU 84.51%. Sidewalk IoU 82.67% (precision 0.90, recall 0.92). Crosswalk IoU 75.42% (precision 0.86, recall 0.86). Road IoU 86.04%. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942); [Esri model documentation](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)
- **City-scale polygon overlap with official GIS.** Cambridge 85.9%, Boston 77.9% (Boston was never used in training), Washington DC 73.8% (reduced by mismatched reference data and tree-covered footpaths), Manhattan 87.5%. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- **Temporal mismatch in reference data.** Cambridge reference GIS reflected 2010 conditions, while the imagery was from 2018. Sidewalk polygons changed by 9.2% and crosswalks by 23% between those dates, so part of the apparent "error" is reference-data drift. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- **Generalisation claim.** The authors say the model can be used "in the North American context, or other cities with similar urban fabrics, without needing any further training", and that "TILE2NET also allows users to retrain the feature detection model in new contexts". — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- **Width.** The paper says polygons "can be used to measure the width of each sidewalk segment" using the method of Hosseini et al. (2021). That method skeletonises the mask and takes width as twice the distance from the skeleton to the border. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942); [Hosseini et al. 2021, arXiv 2112.06120](https://arxiv.org/pdf/2112.06120)
- **Centerline weakness.** The Dense Voronoi skeleton is "very sensitive to the interpolation distance parameter". At d=0.2 it produces extra branches; at d=2 the line breaks. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- **Current status.** The README describes a beta that is "not ready for production" and needs a CUDA GPU. The model has been retrained on more data, the code moved to PyTorch 2 / Shapely 2, and the default output is GeoParquet or Shapefile in EPSG:4326. Supported regions listed are Boston, Cambridge, NYC, DC, Alameda County and Oregon. — [GitHub VIDA-NYU/tile2net](https://github.com/VIDA-NYU/tile2net)
- **Esri packaged model.** Esri's "Pedestrian Infrastructure Classification" model (ArcGIS Living Atlas) is based on Tile2Net. It expects 8-bit RGB at 10-30 cm. Esri expects it to work well statewide only in DC, MA, NY, NJ, OR and VA. It requires the ArcGIS Image Analyst extension (Pro) or Image Server, and a GPU with CUDA compute capability 6.0 or higher is recommended. — [Esri documentation](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)
- **Third-party test at 30 cm.** Wherobots ran Tile2Net on 30 cm NAIP imagery over College Park, MD. It attributed gaps to "lower resolution imagery (30cm resolution) than what it was trained on (19cm)", to changed geographic context, and to tree occlusion. Inference took about 30 min and vectorisation about 5 min for that area. No accuracy was reported. — [Wherobots RasterFlow Tile2Net notebook](https://docs.wherobots.com/tutorials/example-notebooks/rasterflow-tile2net)
- **GeoSAM.** Fine-tunes Segment Anything with point prompts from a task-specific model plus LLM text prompts. It reports at least 5% mIoU improvement over existing mobility-infrastructure segmentation methods, in both familiar and unseen regions. arXiv 2311.11319, v4 August 2025, ECAI 2025, code at rafiibnsultan/GeoSAM. — [arXiv 2311.11319](https://arxiv.org/abs/2311.11319v4)
- **Zero-shot SAM.** Off-the-shelf SAM performs poorly on aerial and satellite pedestrian infrastructure because it was trained on natural images. A related study combines SAM with LiDAR and satellite data. — [par.nsf.gov 10545494](https://par.nsf.gov/biblio/10545494)
- **Earlier baselines.** Prior aerial-only crosswalk detection reached 55.59% accuracy and 15.41% recall (Luttrell 2022). Ning et al. (2022) combined aerial and street-view imagery for sidewalk extraction. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942); [Ning et al., NJIT](https://researchwith.njit.edu/en/publications/sidewalk-extraction-using-aerial-and-street-view-images/)
- **Zero-shot SAM for road width.** Xu et al. (2023) validated road widths from aerial imagery against VicRoads records. — [Xu et al. 2023](https://mothlight.github.io/Publications/Xu2023LeveragingSAM.pdf)

### Inferences
- Beirut has none of the municipal planimetric sidewalk layers Tile2Net used as labels. Retraining would require hand-labelling a few hundred to a few thousand tiles. The paper does not state a minimum label count.
- A pragmatic path for Beirut: run the pretrained Tile2Net or Esri model, manually correct a sample of districts, then fine-tune on the corrected masks.
- The US models' output on Beirut should be treated as a draft. Beirut's urban fabric differs from US grids: narrow, irregular, often curb-less streets, lots of parking on sidewalks, and stone/tile paving that looks like road.
- For width, Tile2Net does not output width natively. The skeleton/distance-transform method from Hosseini et al. 2021 has to be added as a post-processing step.

### Gaps
- I found no published test of Tile2Net or GeoSAM in any Middle Eastern, North African or dense Mediterranean city.
- The GeoSAM benchmark tables (absolute mIoU, datasets) were not retrieved.
- I did not verify whether the "90% accuracy" figure in press coverage matches any metric in the paper. Use the paper's IoU and overlap figures instead.
- I found no 2024-2026 paper that measures sidewalk width from satellite (not aerial) imagery with reported width error. Geospatial foundation models (e.g., Prithvi, Clay, SatMAE) were not researched in depth. I found no sidewalk-specific benchmarks for them.

## Q2. What GSD is needed to measure sidewalk width reliably, and what goes wrong in dense Mediterranean cities

### Takeaway
Tile2Net's accuracy figures are for about 19 cm aerial imagery. Esri says 10-30 cm is acceptable, and a 30 cm test showed visible gaps. Width measurement accuracy is bounded by pixel size at both edges. At 30 cm satellite GSD, a 1.5 m Beirut sidewalk is only about 5 pixels wide. Sub-metre width classes (for example, under 0.9 m versus 1.2-1.5 m) therefore realistically need aerial or drone imagery at 5-10 cm. Tree canopy, shadows, parked cars and off-nadir satellite lean are the main failure modes.

### Cited Findings
- Tile2Net was trained at 0.19 m per pixel (zoom 20). — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- Esri's derived model expects "high-resolution (10 - 30 centimeters)" RGB. — [Esri documentation](https://doc.arcgis.com/en/pretrained-models/latest/imagery/introduction-to-pedestrian-infrastructure-classification-model.htm)
- At 30 cm, prediction gaps appear, attributed to resolution, context and tree occlusion. — [Wherobots notebook](https://docs.wherobots.com/tutorials/example-notebooks/rasterflow-tile2net)
- Detection accuracy is lower under tree cover. However, because labels came from planimetric GIS data, which contains sidewalks regardless of obstruction, the model "performed surprisingly well in occluded areas". It mapped sidewalks as continuous under heavy shadow in Cambridge and under foliage in Manhattan. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- Automated gap-filling under trees and shadows risks creating segments that do not exist. This matters especially for wheelchair-routing datasets. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- Orthorectification is required. Raw imagery has displacement and scaling errors from sensor orientation and terrain relief, which make distance and area measurements inaccurate. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- A 2026 street-view width study notes that aerial methods need high-resolution orthorectified imagery and are limited by occlusions such as tree canopy. — [Lieu & Guhathakurta 2026, EPB](https://econpapers.repec.org/RePEc:sae:envirb:v:53:y:2026:i:5:p:1129-1144)
- Vantor (formerly Maxar) "15 cm HD" is not native 15 cm capture. It is produced by applying proprietary HD processing to native 30 cm imagery. — [SatNews 2020](https://news.satnews.com/2020/11/12/maxar-debuts-15-cm-hd-offering-high-clarity-from-commercial-satellite-imagery/); [Geoimage](https://geoimage.com.au/blog/15cm-hd-imagery-highest-clarity-imagery-available)
- PPK fixed-wing drone mapping of Beirut in 2020 achieved geolocation "precision to within 3cm". — [GIM International](https://www.gim-international.com/content/news/the-beirut-explosion-uav-mapping-as-a-first-step-to-recovery)

### Inferences (not sourced; arithmetic and domain reasoning)
- **Pixel arithmetic.** At ±1 pixel per edge, width uncertainty is about ±0.6 m at 30 cm GSD, about ±0.3 m at 15 cm, and about ±0.1-0.15 m at 5-7.5 cm. Beirut sidewalks are often 0.8-2 m wide, so:
  - 30 cm satellite is usable for presence/absence and rough polygons on wide sidewalks and corniche promenades.
  - 15 cm HD is marginal for width classes.
  - Drone or aerial imagery at ≤7.5 cm is needed for width measurements suitable for accessibility analysis.
- **Building lean.** In dense Beirut neighbourhoods with 8-20 storey buildings, off-nadir satellite captures make façades lean over the sidewalk, and long winter shadows hide it. Lebanon is about 34°N. Ordering near-nadir (low off-nadir angle) scenes with high sun elevation (summer, around midday) is important. A true orthophoto (a DSM-based ortho correction) from drone or aerial survey removes lean; standard satellite ortho products do not fully remove it.
- **Parked cars.** Cars parked on or half on Beirut sidewalks will usually read as "road" or as obstruction. Imagery shows the sidewalk's effective clear width at that moment, not its built width. Built width needs curb-line detection, which is often hidden under the cars.
- **Visual confusion.** Curb-less shared streets in old quarters (Gemmayzeh, Mar Mikhael, Tripoli's old city, Saida) may have no visible sidewalk/road boundary in overhead imagery.

### Gaps
- I found no study that quantifies sidewalk width error (in cm) versus GSD. The thresholds above are reasoning, not measured results.
- I found no Mediterranean-city study quantifying shadow or occlusion losses.

## Q3. Imagery availability and cost for Lebanon

### Takeaway
Commercial 30 cm satellite archive imagery of Beirut and other Lebanese cities can be bought from resellers. Prices run about $19-25/km² for 30 cm archive (SkyWatch) and $22.50/km² for Pléiades Neo archive (LandInfo, Jan 2026). Tasking runs about $29-32.50/km². Minimums range from 1 km² (SkyWatch, SkyFi) to 25-100 km² (LandInfo, UP42).

Free open imagery is limited. OpenAerialMap holds a 12 cm drone orthomosaic of the Beirut port blast area (CC-BY 4.0), 0.4-0.8 m Maxar/Planet post-blast scenes (CC BY-NC), and two 2025 drone sets of 3-4 cm that may not be in Lebanon.

The Lebanese Army Directorate of Geographic Affairs does carry out aerial photography, but I found no public specification or access route. Google imagery cannot be used for tracing or ML. Esri World Imagery is licensed for tracing to create vector data; ML use is unverified.

### Cited Findings

**Commercial satellite prices**
- **SkyWatch tiered list prices.** "HD Optical 15 cm": $25/km² archive, $30/km² tasking, 1 km² minimum. "Very High-Res 30-49 cm": $19/km² archive, $29/km² tasking, 1 km² minimum. "High-Res 50-99 cm": $10/km² archive, $12/km² tasking, 25 km² tasking minimum. Licensing and volume may change the final price. — [SkyWatch data page](https://skywatch.com/data)
- SkyWatch requires a minimum AOI width of 2 km for Pléiades, Pléiades Neo and Vantor. A 2 km² AOI may be billed as 5 km². — [SkyWatch AOI help](https://intercom.help/skywatch-ab92e82e1a0a/en/articles/9917241-aoi-size-and-cost-requirements-hub); [SkyWatch min/max AOI](https://intercom.help/skywatch-ab92e82e1a0a/en/articles/9151497-maximum-and-minimum-aoi-sizes)
- **LandInfo (Jan 2026 price list).** Pléiades Neo 30 cm: $22.50/km² archive, $32.50/km² new collection. Pléiades minimums: 25 km² archive, 100 km² new collection. Vantor mono archive minimum: 25 km² per contiguous area. These figures come from a search snippet; the PDF returned 403 when fetched, so verify the table. — [LandInfo price list PDF, Jan 2026](https://landinfo.com/wp-content/uploads/Imagery_LandInfo_202601-1.pdf); [LandInfo pricing page](https://landinfo.com/satellite-imagery-pricing/)
- **UP42 tasking minimums.** Pléiades Neo 100 km²; Maxar/Vantor 50 km² (64 km² in high-demand areas). UP42 offers WorldView Legion including an HD 15 cm product. — [UP42 tasking minimum charges](https://docs.up42.com/data/tasking-min-charges); [UP42 Vantor](https://docs.up42.com/data/vantor)
- SkyFi offers ordering from Vantor's 20+ year archive with a 1 km² minimum AOI. — [SkyFi blog](https://skyfi.com/en/blog/vantor-high-resolution-satellite-imagery-on-demand-skyfi)
- A generic market guide puts sub-metre archive at about $15-30/km² and new tasking from about $40-60/km². This is a secondary estimate, not a vendor price. — [ONGEO pricing guide](https://ongeo-intelligence.com/blog/satellite-imagery-pricing-guide)
- LandInfo has a Lebanon country page for satellite imagery and topographic map data. — [LandInfo Lebanon](https://landinfo.com/?p=4039)

**Open imagery on OpenAerialMap (queried live via the OAM API, bbox 35.09-36.63E, 33.05-34.69N, on 2026-11-06)**
- 11 records found. — [OpenAerialMap API query](https://api.openaerialmap.org/meta?bbox=35.09,33.05,36.63,34.69&limit=100)
  - UAV orthoimage "Beirut Port Explosion 4-8-2020", GSD 0.121 m, CC-BY 4.0. Supplied by Rabih El Zein, orthoimage by @GeoConor.
  - Maxar scenes from 2020-06-09 to 2020-08-05 at GSD 0.42-0.84 m, and Planet scenes from 2020-08-05 (0.5 m and 3 m). All are CC BY-NC 4.0.
  - Two recent UAV sets: "Douma pilot, Local Council area" (2025-12-24, GSD 0.029 m, CC-BY 4.0) and "ZA'URA" (2025-02-03, GSD 0.038 m, CC BY-SA 4.0). The bbox also covers parts of Syria, so these may be Douma and Za'ura in Syria. Check their footprints before treating them as Lebanese.
- Maxar donated post-blast imagery through its Open Data Program. — [Maxar blog](https://blog.maxar.com/open-data-program/2020/open-data-response-to-the-beirut-lebanon-explosion); [HOT mailing list Aug 2020](https://lists.openstreetmap.org/pipermail/hot/2020-August/015312.html); [OSM wiki: 2020 Beirut Port Explosion](https://wiki.openstreetmap.org/wiki/2020_Beirut_Port_Explosion)

**Drone campaigns in Beirut**
- After the August 2020 blast, Augment (with Pix4D) flew an eBee X fixed-wing drone over the blast area, producing 4,306 images, in coordination with Kickstart Aid, Live Love Beirut and others. Flights needed official permission. — [Pix4D blog](https://www.pix4d.com/blog/beirut-disaster-response); [Pix4D community](https://community.pix4d.com/t/the-beirut-explosion-drone-mapping-for-recovery/18592); [EENA](https://eena.org/blog/drone-mapping-in-the-beirut-explosion/)
- PPK accuracy for that campaign was given as within 3 cm. — [GIM International](https://www.gim-international.com/content/news/the-beirut-explosion-uav-mapping-as-a-first-step-to-recovery)
- UNESCO, the Directorate General of Antiquities and Iconem produced a georeferenced 3D drone model of Gemmayzeh, Mar Mikhael and Karantina, starting December 2020. — [UNESCO via India Education Diary](https://indiaeducationdiary.in/?p=143233)
- CIPA ran a separate volunteer photogrammetric documentation of Beirut heritage. — [CIPA Documenting Beirut](https://www.cipaheritagedocumentation.org/documentingbeirut/)

**National aerial photography**
- The Lebanese Army Directorate of Geographic Affairs (established 1962) is responsible for geodesy, triangulation, "aerial filming and photography, and photographic transformation". — [Lebanese Army DGA page](https://www.lebarmy.gov.lb/en/node/3984)
- In 2023 the Directorate was launching a 13-station GNSS (CORS) network, funded by USAID and its own budget. — [LBCI 2023](https://www.lbcgroup.tv/news/lebanon-news/691386/lebanese-army-launches-online-network-to-facilitate-geographical-surve/en)
- A 2005 national satellite imagery project was funded by the Arab Fund and run under the Directorate. — [Via Satellite 2005](https://www.satellitetoday.com/uncategorized/2005/10/17/space-imaging-middle-east-to-provide-satellite-imagery-of-lebanon/)

**Licence limits of basemap imagery**
- **Esri World Imagery.** Esri and its contributors grant "the non-exclusive right to use the World Imagery map to trace features and validate edits in the creation of vector data". Other uses fall under Esri's terms. — [OSM wiki Template:Esri image](https://wiki.openstreetmap.org/wiki/Template:Esri_image); [Geoawesome](https://geoawesome.com/esri-world-imagery-comes-to-openstreetmap/)
- **Bing.** Tracing rights are limited to aerial imagery used as a background in a non-commercial online editor application of OpenStreetMap. — [OSM wiki: Bing](https://wiki.openstreetmap.org/wiki/Bing)
- **Google Maps Platform.** Customers may not trace or digitise from Google Maps Content, for example building outlines or utility posts from Satellite map type. Using Google Maps Content to "train, test, validate or fine-tune" ML/AI models is prohibited. — [Google Maps Platform Analytics Service Terms](https://cloud.google.com/archive/terms/maps-platform/maps-analytics-service-terms-20251204); [ConductAtlas summary](https://conductatlas.com/platform/google-maps/google-maps-platform-terms-of-service/ai-and-ml-training-data-prohibition/); [Workspot reproduction of the GMP terms](https://www.workspot.com/legal/google-map-platform-provider-terms/)

### Inferences
- **Indicative costs.** Greater Beirut is about 70-100 km²; this is my own approximate figure and is not sourced. At $19-25/km², one 30 cm archive coverage would cost about $1,500-2,500. Several Lebanese cities (Beirut, Tripoli, Saida, Tyre, Zahle, Jounieh) at a few hundred km² total would be roughly $5,000-10,000 at archive rates, before multi-user or derived-product licence uplifts.
- **Drone versus satellite.** Drone surveys give 3-12 cm GSD, which is far better for width. However, Lebanon requires official flight permission, as the 2020 Beirut campaign showed. Drones are realistic for pilot neighbourhoods, not whole cities.
- **Licence choice.** For ML training and published derived data, licensed commercial imagery (with derived-product rights confirmed) or CC-BY drone imagery is safer than web basemaps. Google is excluded. Esri permits tracing to create vector data, but its ML terms should be checked before training. Maxar/Planet OAM imagery is CC BY-NC, so it is unsuitable for commercial work.

### Gaps
- I could not find the Directorate of Geographic Affairs' orthophoto GSD, acquisition years, price or access procedure. I also found nothing on whether CDR (Council for Development and Reconstruction) or Beirut Municipality hold recent orthophotos. These require direct contact.
- The Planet SkySat 50 cm price for Lebanon was not retrieved. It probably falls in SkyWatch's $10-12/km² "50-99 cm" tier, but that is unconfirmed.
- The Esri and Bing terms on ML training were not confirmed from primary licence text.
- I did not confirm whether the Augment/Pix4D or UNESCO/Iconem Beirut outputs are downloadable, or at what GSD.
- I did not check imagery from the 2024 conflict period (South Lebanon, Dahiyeh) or later Maxar Open Data releases.

## Q4. Can remote sensing detect sidewalk objects (trees, poles, kiosks, parked cars)?

### Takeaway
From overhead imagery, large or distinctive objects are feasible: tree crowns, parked cars, kiosks or large street furniture, and wide sidewalk cafés. Thin vertical objects such as poles, signposts, bollards and hydrants are generally not reliably detectable at 30 cm. They need ≤5-10 cm drone imagery or, better, street-level imagery or LiDAR. The core sources I found do not report object-level accuracy for sidewalk furniture from satellites.

### Cited Findings
- Tile2Net outputs only four classes (sidewalk/footpath, crosswalk, road, background). It has no object classes. The authors suggest adding "tree" or "shadow" classes in future work to help close network gaps. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- Tree foliage and shadow occlude sidewalks. Tile2Net partly bridges these occlusions, but bridging risks false segments. — [Hosseini et al. 2023](https://par.nsf.gov/servlets/purl/10493942)
- Ning et al. combine aerial and street-view images because overhead-only extraction misses detail. — [Ning et al., NJIT](https://researchwith.njit.edu/en/publications/sidewalk-extraction-using-aerial-and-street-view-images/)

### Inferences
- **Tree crowns.** Easily detected in 30-50 cm imagery. Trunk position, and therefore the actual obstruction on the sidewalk, is not visible from above.
- **Parked cars.** Detectable at 30 cm (a car is about 6x15 pixels). With 15 cm HD or drone imagery they can be classified as on-sidewalk or on-road, given a curb line.
- **Poles and signs.** These may appear as shadows rather than objects, so detection is unreliable at satellite resolutions. This is better handled by street-view or mobile mapping, which is covered by other researchers.
- **Kiosks and café terraces.** Detectable when roofed and larger than about 2x2 m.
- **Single snapshot.** Satellite imagery shows one moment; parked cars and vendors change constantly.

### Gaps
- I found no source with quantitative detection rates for poles, kiosks or other sidewalk furniture from satellite or aerial imagery. This would need a targeted literature search on "street furniture detection aerial" or "pole detection UAV".

## Q5. Airborne LiDAR or a DEM for Lebanon

### Takeaway
The only documented airborne LiDAR in Lebanon I found is a 2018 archaeological survey, described as the "first ever scientific LiDAR data acquisition in Lebanon", in a coastal region north of Beirut. I found no city-scale airborne LiDAR of Beirut. Drone photogrammetry (Augment 2020, UNESCO/Iconem 2020) provides 3D models for parts of blast-affected Beirut.

### Cited Findings
- The "first ever scientific LiDAR data acquisition in Lebanon was conducted in autumn 2018" and produced a high-resolution DEM for an archaeological landscape survey. The DEM was later compared with 1962 aerial imagery to measure about 56 years of surface change. — [Rom et al. 2020, Open Archaeology 6(1):248-268](https://edoc.ku.de/id/eprint/25372/1/Rom_etal_2020.pdf); [EGU2020-22519](https://meetingorganizer.copernicus.org/EGU2020/EGU2020-22519.html)
- The search engine's summary placed the survey in the Chekka region (Batroun/Koura coast). It flagged that this came from the model's own knowledge, not the documents, so verify it in the paper.
- UNESCO/Iconem produced a georeferenced 3D model from drone surveys (not LiDAR) of Gemmayzeh, Mar Mikhael and Karantina. Iconem described it as "medium resolution". — [India Education Diary / UNESCO](https://indiaeducationdiary.in/?p=143233)
- Lebanon's 1962 aerial imagery exists (used in the Rom et al. change analysis), indicating a historic national aerial photo archive. — [EGU2020-22519](https://meetingorganizer.copernicus.org/EGU2020/EGU2020-22519.html)

### Inferences
- Without LiDAR, the practical 3D alternatives are tri-stereo satellite DSMs (for example Pléiades or Pléiades Neo tri-stereo, at extra cost) or drone photogrammetry DSMs. Either could support true-ortho correction of building lean and curb-height estimation in pilot areas.
- Mobile or terrestrial LiDAR (vehicle or backpack) is more relevant than airborne LiDAR for sidewalk width and curb height. It is outside this note's scope.

### Gaps
- No information was found on any national DEM or LiDAR programme by the Directorate of Geographic Affairs or CNRS-L (Lebanese National Council for Scientific Research), or on any LiDAR held by private Lebanese survey firms.
- I did not check global DEMs (Copernicus GLO-30, ALOS). At 30 m resolution they are irrelevant for sidewalks.
