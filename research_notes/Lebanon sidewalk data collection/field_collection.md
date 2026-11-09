# Field Data Collection Methods for Sidewalk Geometry, Dimensions and Obstruction Inventories (Lebanon)

Scope: comparison of field methods (manual audit, GNSS, mobile apps, smartphone LiDAR, handheld/backpack/vehicle mobile LiDAR, crowdsourcing) on accuracy, speed, cost and skills, plus a recommended data model. Research done 2026-11-06. Vendor specs are manufacturer claims unless stated otherwise. Where a number could not be found, it is listed under Gaps rather than estimated.

## 1. Mobile data collection platforms (KoboToolbox, ODK, QField, ArcGIS Field Maps, Mergin Maps, OSM editors)

### Takeaway
For a Lebanese research team, the low-cost choice is either (a) KoboToolbox or ODK for form-based segment audits, which handle point geometry well and support Arabic/English forms, or (b) QField with QFieldCloud or Mergin Maps (QGIS-based) when you need to draw or edit sidewalk lines and polygons offline. ArcGIS Field Maps only makes sense if the institution already has an Esri licence. OSM editors (StreetComplete, MapComplete, Every Door, Vespucci) suit open crowdsourcing but not a controlled research protocol.

### Cited Findings
- KoboToolbox Community Plan (free for nonprofits): 5,000 submissions per month, 1 GB file storage, unlimited projects, forms, data collectors and collaborators. The Professional Plan gives 25,000 per month or 300,000 per year — [KoboToolbox blog](https://www.kobotoolbox.org/blog/supporting-future-growth-and-accessibility-introducing-kobotoolboxs-new-plan-model); the submission limit is counted per month and storage per account — [Kobo community forum](https://community.kobotoolbox.org/t/update-about-limits-for-free-accounts/44198); official pricing page — [kobotoolbox.org/pricing](https://kobotoolbox.org/pricing). A third-party listing cites a 1,000-submission "Starter" tier, which conflicts with the official blog — [SpotSaaS](https://www.spotsaas.com/product/kobotoolbox/pricing).
- KoboToolbox supports translated forms, added in the web UI or in XLSForm. When a form has several languages, KoboCollect and Enketo show a language selector in the top-right corner — [Kobo support: language dashboard](https://support.kobotoolbox.org/language_dashboard.html); [Kobo support: XLSForm translations](https://support.kobotoolbox.org/language_xls.html).
- Arabic right-to-left layout in Kobo forms depends on the script of the first visible text. If the first label or hint is in a Latin script, the form may render left-to-right. Users report mixed behaviour — [Kobo forum: Arabic alignment](https://community.kobotoolbox.org/t/language-alignment-to-be-in-right-arabic-language/47322); [Kobo forum: AR/EN multi-language survey](https://community.kobotoolbox.org/t/multi-language-ar-en-survey/3080).
- In older ODK Collect versions, right-to-left alignment was tied to the app's UI language — [ODK forum](https://forum.getodk.org/t/putting-option-bubbles-on-right/4737). The ODK team fixed RTL navigation arrows and animations in Collect beta 2023.2 — [ODK forum](https://forum.getodk.org/t/when-using-a-rtl-language-in-collect-arrows-for-back-and-next-buttons-point-in-the-wrong-direction/40659). The Collect UI is translated through Transifex — [ODK forum: Arabic translation](https://forum.getodk.org/t/odk-collect-arabic-translation/3016).
- QFieldCloud: the free Community plan includes unlimited public and private projects, but only 100 MB of hosted data and 3 file versions. Pro costs EUR 12 per month (adds offline PostGIS layers and versioning). Organization costs EUR 16 per user per month, minimum 2 users — [qfield.cloud pricing](https://qfield.cloud/pricing). The docs describe Flat (fixed price per user) and Flex (pay per active user) plans — [QField docs: storage](https://docs.qfield.org/get-started/storage-qfc). A third-party review quotes EUR 18 (Flat) and EUR 28 (Flex) per user per month, which conflicts with the official page — [europeanpurpose.com](https://europeanpurpose.com/tool/qfield). Third-party self-hosted QFieldCloud VMs cost USD 59 to 145 per month — [AcuGIS](https://acugis.com/qfieldcloud-hosting.html).
- Mergin Maps Premium costs EUR 15.80 per contributor per month billed annually, or EUR 19.50 billed monthly, with a 14-day trial — [merginmaps.com/pricing](https://merginmaps.com/pricing); tier changes are described at [Mergin Maps blog](https://merginmaps.com/blog/updating-the-subscription-tiers-for-mergin-maps).
- ArcGIS Field Maps has no published per-user price; buyers must request a quote — [G2](https://www.g2.com/products/arcgis-field-maps/pricing); [Capterra listing](https://www.capterra.com/p/10018922/Mergin-Maps/alternatives/).
- MapComplete has a sidewalks layer that asks for width on each side (`sidewalk:left:width` / `sidewalk:right:width`) — [MapComplete sidewalks layer doc](https://source.mapcomplete.org/loviuz/MapComplete/src/commit/4f7f93e9c1015aea3201e3653dd87fd1f55347db/Docs/Layers/sidewalks.md). Its kerbs layer stores `kerb:height` with options such as flush (~0 cm) and lowered (~3 cm) — [MapComplete kerbs layer](https://source.mapcomplete.org/elgaard/MapComplete/blame/branch/build/velopark/Docs/Layers/kerbs.md).
- StreetMeasure is a companion app that measures widths and heights with the camera. It integrates with StreetComplete v51 and later — [OSM wiki Key:width](https://wiki.openstreetmap.org/Key:width).
- OSM Lebanon has a WikiProject and a talk-lb mailing list (2017 "mapping Beirut" thread), plus a documented Beirut mapping party — [WikiProject Lebanon](https://wiki.openstreetmap.org/wiki/WikiProject_Lebanon); [talk-lb list](https://lists.openstreetmap.org/pipermail/talk-lb/2017-April/000010.html); [Beirut Mapping Party](https://wiki.OpenStreetMap.org/wiki/Lebanon/Beirut_Mapping_Party).

### Inferences
- Kobo, ODK and QField all work offline: forms and data are cached on the device and synced later. This is important for Lebanon, where mobile data and power are unreliable. Offline capability is standard for these tools, but these notes did not fetch a specific doc page confirming it.
- Suggested hybrid workflow: draw the sidewalk centreline or polygon geometry in QGIS from orthophotos or OSM beforehand; collect attributes and obstruction points in the field with QField or Kobo/ODK; use the segment ID as the join key.
- A Kobo team of up to about 20 students doing about 10 segments per day each is roughly 4,000 to 6,000 submissions per month. That fits the free 5,000 per month only if each segment is one submission with obstructions as repeat groups, not separate submissions.
- Arabic: put an Arabic label first in the XLSForm and test on the deployed Collect/KoboCollect version.

### Gaps
- ODK Cloud pricing was not retrieved (getodk.org/pricing redirects to the home page and was not fetched). Self-hosted ODK Central is open source, but no cost source was captured.
- No source found on Arabic UI localisation for QField, Mergin Maps, Every Door or Vespucci.
- No source found confirming a StreetComplete-native sidewalk-width or kerb-height quest. Only the MapComplete layers and the StreetMeasure integration were found.

## 2. Positioning accuracy: phone GNSS vs low-cost RTK, and Lebanese correction services

### Takeaway
Phone GNSS typically gives about 5 to 10 m error in urban canyons. That is enough to say which segment a point is on, but not which side of the street or where along a 50 m segment. Low-cost RTK rovers (USD 2,200 to 3,000) give 1 to 2 cm with a fix. Lebanon has a national network-RTK service, LEB-CORS, run by the Lebanese Army: 13 stations with about 3 cm real-time accuracy. Subscription terms and fees are not published online.

### Cited Findings
- LEB-CORS (Lebanese Army) runs 13 stations, available 24/7/365, offering network RTK for "3-centimeter" real-time positioning. Another version of the site says 3 to 4 cm; the French page says ±3 cm. Users need RTK-capable GNSS, a controller with RTK field software, and internet access (Wi-Fi, mobile phone or modem) — [lebcors.army.gov.lb](https://lebcors.army.gov.lb); [French version](https://lebcors.army.gov.lb/?Lang=fr-FR). (WebFetch of the site failed with a TLS certificate error, so these details come from the search-indexed text.)
- Smartphone dual-frequency 3D-mapping-aided GNSS in Hong Kong urban canyons achieved about 10 m on average; multipath remains a problem — [Ng et al. 2021 via ION/PolyU repository](https://ira.lib.polyu.edu.hk/handle/10397/92730?mode=full). A PolyU summary says the method can robustly achieve under 5 m — [PolyU PAIR](https://polyu.edu.hk/pair/publications/issue-3/kt3---urban-positioning).
- In DXOMARK/Geoflex tests, the best phones had horizontal RMS errors under 5 m. Some phones were off by up to 450 m at a tunnel exit — [DXOMARK](https://www.dxomark.com/gps-on-your-smartphone-why-youre-not-always-there-when-it-says-youre-there/).
- A 2026 study found that the operating environment, more than the phone hardware, is the main driver of smartphone GNSS error — [arXiv 2603.26706](https://arxiv.org/pdf/2603.26706).
- In urban-canyon tests in Torino, the iPhone was more affected by multipath than the Samsung, especially vertically — [InsideGNSS](https://insidegnss.com/what-are-the-actual-performances-of-gnss-positioning-using-smartphone-technology/).
- Emlid Reach RS3: USD 2,999 on Emlid's store; resellers range from about USD 2,519 to 3,600. It has tilt compensation up to 60 degrees within 20 mm, and a built-in LTE modem for NTRIP — [Advexure](https://advexure.com/collections/emlid-rtk-gnss-receivers-and-surveying-tools/products/emlid-reach-rs3); [reach.dog](https://reach.dog/shop/e38-survey-solutions/products/emlid-reach-rs3).
- Emlid Reach RX (network-RTK-only rover): USD 2,199 at a US reseller. RTK spec is 7 mm + 1 ppm horizontal and 14 mm + 1 ppm vertical, with a fix typically in under 5 s. It accepts RTCM3 corrections from any NTRIP service — [reach.dog / Advexure](https://reach.dog/shop/advexure/products/emlid-reach-rx); [RobotShop](https://ca.robotshop.com/products/emlid-reach-rx-lightweight-rtk-gnss-receiver). The Reach RX2 is USD 2,399 — [Emlid store](https://store.emlid.com/product/reachrx).
- Emlid's own VRS correction service advertises 1 to 2 cm, at about USD 699 per year (the listing wording is ambiguous) — [Emlid store](https://store.emlid.com/product/reachrx).
- Saudi Arabia's KSA-CORS is a regional example of a government CORS with a published user guide — [KSA-CORS Getting Started](https://ksacors.geosa.gov.sa/WelcomePage/Getting%20Started%20with%20KSA-CORS%20Network_v.1.0.pdf).

### Inferences
- The Reach RX's main constraint is that it needs an NTRIP caster in Lebanon. LEB-CORS is the obvious candidate if it offers NTRIP/RTCM3 access to civilian or academic users; this must be confirmed directly with the Army Geographic Affairs directorate. Emlid's VRS coverage in Lebanon is unverified.
- Fallback without CORS access: one Reach RS3 as a local base on a known or averaged point, plus a rover. Two RS3 units cost about USD 6,000. Absolute accuracy then depends on how well the base coordinate is known, but relative accuracy within a few km stays at cm level.
- Even RTK loses its fix under balconies, in narrow old-city streets and near tall buildings, all common in Beirut and Tripoli. Expect float or no-fix periods; record fix status as a field.
- For a pure audit (widths and obstructions), segment-level referencing (segment ID plus distance from the start node, measured with a wheel) is cheaper and more robust than RTK for every point.

### Gaps
- LEB-CORS subscription process, fees, NTRIP/RTCM formats and whether universities can access it: not found online.
- No private RTK/NTRIP providers in Lebanon were found.
- No published smartphone GNSS accuracy test specific to Beirut.
- ArduSimple pricing was not retrieved.

## 3. Measurement tools: laser distance meter, measuring wheel, smartphone LiDAR

### Takeaway
Tape, wheel and laser measurements remain the reference for clear width and curb height. iPhone/iPad Pro LiDAR gives 3 to 6 cm relative accuracy on small objects and can flag ADA-type compliance issues, but it is inconsistent on ramp slopes, degrades beyond about 5 m, and is blocked by parked cars, which are pervasive on Lebanese sidewalks. It is a good speed-up for documentation, not a replacement for direct measurement of critical dimensions.

### Cited Findings
- Mountain-Plains Consortium / UC Denver report (2024, iPhone 13 Pro): iPhone LiDAR was compared against a Trimble TX8 terrestrial scanner and field measurements. It is "generally effective" at detecting minor ADA compliance issues, with some inconsistency on curb ramp slopes. Vegetation and parked cars caused significant data gaps when scanning from the street — [ROSAP research brief dot/87091](https://rosap.ntl.bts.gov/view/dot/87091); [ROSAP full report dot/87088](https://rosap.ntl.bts.gov/view/dot/87088); [MPC project page](https://www.mountain-plains.org/research/details.php?id=574).
- Ohio State (ISPRS 2022, iPhone 12 Pro): the LiDAR shows "strong potential" for mapping small objects at 3 to 6 cm accuracy, but absolute accuracy is limited; combining it with IMU data was suggested — [ISPRS Archives XLIII-B2-2022-303](https://isprs-archives.copernicus.org/articles/XLIII-B2-2022-303/2022/isprs-archives-XLIII-B2-2022-303-2022.pdf).
- iOSPointMapper (arXiv, Dec 2025, Univ. of Washington / TCAT group): real-time iPhone pipeline for sidewalk and accessibility mapping. Sidewalk width estimates were "within acceptable bounds"; errors grew in complex ground geometry. For objects within 5 m, localisation and sidewalk measurement errors were often below 0.5 m RMSE — [arXiv 2512.22392](https://arxiv.org/pdf/2512.22392). (Table values could not be extracted from the PDF.)

### Inferences
- In practice: use a laser distance meter (or folding rule) for clear width and curb height at fixed stations (for example the narrowest point of each segment plus every pinch point), a measuring wheel for segment length and obstruction positions, and a digital level or phone inclinometer for slopes.
- iPhone Pro scanning apps (Polycam, SiteScape, 3d Scanner App) are useful for spot-scanning complex corners and ramps for later measurement in the office. Scaling to city level is limited by short range (about 5 m), drift over long scans and occlusion.

### Gaps
- No peer-reviewed numbers found specifically for iPhone LiDAR sidewalk width or curb height error in cm. The UC Denver report PDF (over 10 MB) could not be fetched.
- Laser distance meter (for example Leica DISTO) and measuring wheel accuracy specs and prices were not retrieved. Typical vendor specs are about ±1 to 2 mm for laser meters, but this was not verified here.
- No sources retrieved for SiteScape, Dot3D or Polycam accuracy.

## 4. Mobile LiDAR / SLAM (handheld, backpack, vehicle)

### Takeaway
Handheld SLAM scanners now range from about EUR 3,000 to 50,000. Top units (Stonex X200GO, CHCNAV RS10, FARO Orbis) give mm to low-cm relative accuracy. Mid-range RTK-capable units (XGRIDS Lixel L2 Pro, CHCNAV RS10) give about 1 cm relative and 3 to 5 cm absolute. A 2026 comparison for sidewalk HD mapping found handheld SLAM most robust where GNSS is weak, and push-cart systems the most stable where occlusion is heavy. Vehicle systems (Trimble MX50, Leica Pegasus) give 2 cm horizontal positioning but cannot see the sidewalk behind parked cars. No independent km/day throughput figure for sidewalk SLAM, and no Lebanese mobile-mapping provider, was found.

### Cited Findings
- 3Dsurvey's late-2025 test of 7 handheld SLAM scanners (Slovenian market prices, EUR) — [3dsurvey.si](https://3dsurvey.si/7-slam-scanners-put-to-the-test/):

  | Scanner | Price | Accuracy | Range | Notes |
  |---|---|---|---|---|
  | Stonex X200GO | ~EUR 35,000 | ~5 mm spec | ≤300 m | About 0.5% drift on long corridors without RTK; RTK lock can take time; rated one of the most balanced |
  | CHCNAV RS10 | ~EUR 24,000 | <5 cm absolute, <1 cm relative | 120 m | Integrated RTK, IP64, ~1.9 kg, handheld/pole/vehicle mount |
  | Leica BLK2GO | EUR 45,000–50,000 | 6–15 mm relative, ~20 mm absolute indoors | ≤25 m | No GNSS/RTK, mainly indoor; authors "not impressed" for the price |
  | FARO Orbis | ~EUR 50,000 | 5 mm in SLAM mode | 120 m | No built-in GNSS, ~6 kg |
  | FJD Trion P1 | EUR 8,000–10,000 | ~2 cm relative | ≤70 m | Fine for GIS-grade work, not cm-level |
  | 3DMakerPro Eagle | EUR 3,000–6,000 | ~2 cm at 10 m | — | Noisy, "barely usable" for professional work |
  | XGRIDS LixelKity K1 | ~EUR 12,000 | ~2 cm relative | 40–70 m | ~1 kg, RTK connection bugs, mainly indoor |

  The authors' professional picks were the X200GO, RS10 and Orbis.
- XGRIDS Lixel L2 Pro: processed accuracy about 1 cm relative and 3 cm absolute RMSE with RTK, 0.5 cm point-cloud thickness — [Radiance Fields](https://radiancefields.com/xgrids/lixel-l2-pro). About ±3 cm without RTK — [Goodio](https://goodio.be/en/product/284443-scanner-3d-manuel-xgrids-lixel-l2-pro). The RTK module is specified at 0.8 cm + 1 ppm horizontal and 1.5 cm + 1 ppm vertical, and sells for EUR 1,034 to 1,634 — [aio.lv](https://aio.lv/en/product--xgrids-cz02020003--11616199); [arvutitark.ee](https://arvutitark.ee/en/pcs-and-accessories/printers-and-scanners/skannerid/xgrids-lixel-l2-pro-rtk-mootmismoodul-1516016). XGRIDS does not publish a fixed price. One US listing at USD 35,000 may be a bundle or markup — [Radiance Fields](https://radiancefields.com/xgrids/lixel-l2-pro); [aifitlab](https://aifitlab.com/products/xgrids-lixel-l2-pro-lidar). Heliguy compares the L3 and L2 Pro — [Heliguy](https://www.heliguy.com/blogs/posts/xgrids-l3-vs-xgrids-l2-pro/).
- A vendor-affiliated comparison notes that the XGRIDS K2 has Multi-SLAM with integrated RTK, while the BLK2GO has single-sensor SLAM and no RTK — [Veesus](https://www.veesus.com/hardware/xgrids-vs-leica-blk2go) (vendor bias).
- Land (2024) forestry study: GeoSLAM ZEB Horizon performed better over longer distances than the Stonex X120GO; the Stonex had low positional error but more noise — [UCL Discovery PDF](https://discovery.ucl.ac.uk/id/eprint/10189040/1/land-13-00093.pdf).
- Sensors 26(5), 2026, "Comparative Performance Evaluation of Multi-Type LiDAR Sensors and Their Applicability to Sidewalk HD Mapping":
  - Platforms: TLS, a push-cart MMS, GNSS/INS-aided and SLAM backpacks, and GNSS/INS-aided and SLAM handhelds.
  - Sites: a park and a dense downtown corridor, routes about 3.4 km.
  - Reference accuracy: planimetric RMSE 0.017 to 0.049 m, vertical 0.009 to 0.014 m.
  - Findings: the cart was most stable under heavy occlusion; SLAM handheld was more robust where GNSS is degraded; backpack SLAM depended on loop closures and how dynamic the scene was.
  - Sources: [GNU ScholarWorks](https://scholarworks.gnu.ac.kr/item/3fb9a9f1-d3cf-4df2-8522-8ff5535ea8cb); [MDPI](https://www.mdpi.com/1424-8220/26/5/1480).
- Trimble MX50 vehicle MMS: post-processed positioning of 0.020 m horizontal and 0.050 m vertical with no GNSS outages; scanner accuracy/precision about 2 mm / 2.5 mm at 30 m (table column mapping ambiguous); 23 kg sensor unit; marketed as "mid-range" — [Trimble MX product comparison PDF](https://www.monsenengineering.com/wp-content/uploads/2024/02/022516-715-en-US_Trimble_MobileMappingSolutions_ProductComparison_USL_0224_LRsec.pdf); [Geo Week News](https://www.geoweeknews.com/articles/trimble-adds-new-mid-range-mx50-to-mobile-mapping-portfolio/).
- Emesent Hovermap spec sheet — [Emesent PDF](https://emesent.com/wp-content/uploads/2022/09/HOVERMAP-ST-SPEC-SHEET-ENG-2202.pdf) (fetched only as a search result).
- A vendor listing claims a backpack LiDAR operator can map 1 to 2 km² per day. This is unverified marketing — [Alibaba](https://electronics.alibaba.com/product/lidar-backpack).
- Lebanon/region providers: General Surveying Services (GSS, est. 1996, offices in Lebanon and KSA) lists 3D laser scanning and BIM. White Line Engineering lists 3D laser scanning and LiDAR-plus-photogrammetry point clouds across Lebanon (credentials unverified). MAPSGEO (Beirut, since 1974) offers geospatial data. None confirmed vehicle or backpack mobile mapping — [search results incl. White Line](https://whiteline-web.vercel.app/en/services); [MAPSGEO ZoomInfo](https://www.zoominfo.com/c/mapsgeo-sarl/481332233). UNDP did a building-level damage assessment of Beirut and Mount Lebanon after 2020 (the method was not reviewed here) — [UNDP Lebanon](https://www.undp.org/lebanon/publications/building-level-damage-assessment-beirut-and-mount-lebanon).

### Inferences
- For Lebanese streets (narrow, cluttered, many parked cars on sidewalks, poor GNSS), a handheld SLAM unit walked along the sidewalk beats a vehicle system. A vehicle in the carriageway is occluded by the very obstructions you want to inventory.
- Mid-range RTK-capable handhelds (EUR 12,000 to 24,000) are the plausible purchase tier for a university. Ground control or LEB-CORS RTK can georeference them.
- Throughput: walking speed is about 3 to 5 km/h. Allowing for loop closures, data management and battery swaps, both sides of a street might give about 5 to 15 km of sidewalk per day. This is an inference; no source was found. Office processing and extraction of widths and obstructions from point clouds is likely the real bottleneck.
- Renting through regional dealers (GCC, Cyprus, Türkiye) is probably more realistic than buying for a pilot. Rental rates were not found.

### Gaps
- No independent, sidewalk-specific km/day throughput data for any SLAM or MMS system. The full Sensors 2026 paper (403 on fetch) may contain survey times.
- No purchase prices for Leica Pegasus TRK, Trimble MX50, NavVis VLX, GeoSLAM ZEB Horizon/Go, or Emesent Hovermap. No rental prices.
- No confirmed vehicle or backpack mobile mapping provider in Lebanon.
- Processing software costs (for example FARO Connect/GeoSLAM Hub, Lixel Studio, NavVis IVION, 3Dsurvey) not retrieved.

## 5. Sidewalk audit protocols and data standards; attributes to record

### Takeaway
Use the OpenSidewalks schema v0.3 (Jan 2026) as the core network model. It is OSM-compatible: sidewalks, crossings and curbs as nodes and edges, with width, incline, surface and tactile_paving, plus adjacent point features (bollard, pole, tree, bench and so on). Extend it with `ext:` fields for Lebanon-specific obstructions such as parked cars, generators, shop displays, stairs and ramps into buildings, and with measured clear and effective width. Project Sidewalk's 5 to 7 label types and MAPS segment-crossing auditing are good templates for the qualitative and severity side.

### Cited Findings
- OpenSidewalks Schema v0.3, released 2026-01-27 (v0.2 2024-01-30, v0.1 2023-08-11) — [GitHub OpenSidewalks-Schema](https://github.com/OpenSidewalks/OpenSidewalks-Schema):
  - Nodes: bare node; generic curb (`barrier=kerb`); raised, rolled, lowered (curb ramp) and flush curbs (`kerb=*`), all accepting `tactile_paving`.
  - Edges: footway; sidewalk (`highway=footway`+`footway=sidewalk`); crossing (`footway=crossing`, with `crossing:markings`); traffic island; pedestrian road; steps (`step_count`, `climb`); living street; road classes and service roads.
  - Zones: pedestrian zone.
  - Adjacent points: power pole, fire hydrant, bench, bollard, manhole, street lamp, waste basket, tree. Adjacent lines: fence, tree row. Adjacent polygons: building, wood.
  - Custom entities and extra attributes must use the `ext:` prefix.
- OpenSidewalks field definitions — same source:
  - `incline`: rise over run, dimensionless, positive uphill.
  - `width`: meters.
  - `length`: meters, Haversine.
  - `surface`: asphalt, concrete, gravel, grass, paved, paving_stones, unpaved, dirt, grass_paver.
  - `tactile_paving`: yes, no, contrasted (≥70% contrast), primitive.
  - `foot`, `description`, `name`.
- OSM sidewalk tagging has two schemes — [OSM wiki: Sidewalks](https://wiki.openstreetmap.org/wiki/Sidewalks):
  - (1) `sidewalk=both|left|right|separate|no` on the road, with side sub-tags such as `sidewalk:left:width`, `sidewalk:left:kerb`, `sidewalk:both:surface`.
  - (2) A separate way, `highway=footway`+`footway=sidewalk`, with `sidewalk:*=separate` on the road.
  - Extra tags: `width`, `surface`, `smoothness`, `incline`, `kerb`, `tactile_paving`, `barrier`, `wheelchair`.
  - Unusable sidewalks: `disused:sidewalk=*` plus a `note`; construction via `highway=construction`.
  - Separate ways dominate in North America and Eastern Europe, road attributes in the UK and Western Europe. The page advises following the local convention.
- OSM accessibility drafts use `width` (m), `incline` (%) and `incline:across` (cross slope) — [OSM wiki Mapping4Accessibility](https://wiki.openstreetmap.org/wiki/User:LorenzoStucchi/Mapping4Accessibility). `sidewalk:<side>:width` applies to sidewalks mapped on the roadway — [OSM Key:width](https://wiki.openstreetmap.org/Key:width).
- Project Sidewalk (Google Street View crowdsourcing):
  - Five main label types: curb ramp, missing curb ramp, obstacle, surface problem, no sidewalk. Later versions describe seven, adding pedestrian signal and crosswalk. Severity is rated on a scale.
  - Validation by agree, disagree or unsure votes; label accuracy = agree / (agree + disagree).
  - Sources: [Saha et al. CHI 2019](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf); [NSF PAR paper](https://par.nsf.gov/servlets/purl/10644332); [LabelAId arXiv 2403.09810](https://arxiv.org/pdf/2403.09810).
- MAPS (Microscale Audit of Pedestrian Streetscapes):
  - Structure: route, segments, crossings and cul-de-sacs. A new segment and crossing section starts whenever the rater crosses the street, including detours forced by an obstruction.
  - Reliability: tested on 516 segment pairs; 75% of subscales showed good or excellent inter-rater reliability.
  - Source: [Millstein et al. 2013, PMC3728214](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3728214/).
  - Time: route audits take 5 to 120 min; training is 3 days — [NCCOR measures registry](https://tools.nccor.org/measures/measure/1044).
- ArcGIS open-data sidewalk layers, for example the OpenSidewalks_edges feature service, carry `surface` and `width` on line features — [ArcGIS REST: OpenSidewalks_edges](https://services8.arcgis.com/zYl11YnKhZxe1aGP/ArcGIS/rest/services/OpenSidewalks_edges/FeatureServer/layers). The UAE National Geospatial Feature Catalogue also defines a sidewalk feature class (regional precedent) — [UAE FGIC catalogue](https://geoportal.fgic.gov.ae/ebook/files/basic-html/page557.html).

### Inferences: recommended data model (OpenSidewalks-compatible, with `ext:` extensions)

**A. `sidewalk_segment`** (LineString, one per side of the street between intersections or crossings, following MAPS segmentation)
- `seg_id` (PK), `street_id`, `side` (L/R relative to the street way direction), `osm_way_id`
- `highway=footway`, `footway=sidewalk` (or `sidewalk_present` = yes / no / disused)
- `length` (m)
- `width` (m): total kerb-to-building-line width
- `ext:clear_width_min` (m): narrowest unobstructed path along the segment
- `ext:clear_width_typ` (m): typical clear width
- `ext:effective_width` (m): total width minus edge and shy zones and permanent furniture
- `surface` (OSM enum); `smoothness`; `ext:surface_condition` (good / fair / poor / broken)
- `incline` (rise/run); `ext:cross_slope` (%) (OSM `incline:across`)
- `ext:kerb_height_avg` (cm); `ext:continuity` (count of level breaks or driveways)
- `lit`; `ext:shade` (none / partial / full)
- `ext:parking_encroachment` (none / occasional / persistent); `ext:frontage_type` (shops / residential / wall / vacant)
- QA fields: `ext:method` (manual / RTK / SLAM / smartphone-LiDAR / remote), `ext:observer_id`, `ext:date`, `ext:time_of_day`, `ext:gnss_fix` (none / float / fix), `ext:photo_ids`, `ext:qa_status`

**B. `curb_node`** (Point at segment ends and crossings)
- `kerb` (raised / rolled / lowered / flush)
- `kerb:height` (cm)
- `tactile_paving`
- `ext:ramp_width` (m), `ext:ramp_slope` (%), `ext:flare_slope` (%)
- `ext:ramp_lip` (cm)
- `ext:obstructed` (yes / no)

**C. `crossing`** (edge)
- `footway=crossing`, `crossing:markings`
- `crossing` (traffic_signals / uncontrolled / unmarked)
- `ext:refuge_island`, `length`

**D. `obstruction`** (Point, or Polygon for large items; linked by `seg_id` plus `ext:chainage_m` along the segment)
- `obs_id`, `seg_id`, `ext:chainage_m`
- `type`, using OSM tags where they exist, otherwise `ext:`:
  - poles and lamps (`power=pole`, `highway=street_lamp`)
  - signs
  - trees and tree pits (`natural=tree`)
  - bollards (`barrier=bollard`)
  - benches (`amenity=bench`)
  - bins and waste skips (`amenity=waste_basket`)
  - manholes (`man_made=manhole`)
  - hydrants (`emergency=fire_hydrant`)
  - parked car or motorbike
  - generator or electrical cabinet
  - shop goods or display, café seating
  - A/C condensate or drain
  - construction debris
  - steps, ramps or planters intruding from a building
  - kiosk
  - level change or hole or broken slab
  - vegetation
- `ext:permanence` (permanent / semi-permanent / temporary)
- `ext:width_occupied` (m), `ext:length_occupied` (m), `ext:height_clearance` (m, for overhangs)
- `ext:remaining_clear_width` (m)
- `ext:severity` (1–5, as in Project Sidewalk)
- `ext:passable_wheelchair` (yes / no)
- `ext:photo_id`, `ext:observed_at`

**E. `zone`** (Polygon) for pedestrian zones or plazas (`highway=pedestrian`).

Recording clear width and remaining clear width at each obstruction lets you compute effective-width profiles without full 3D scanning. Export to GeoPackage for QGIS and QField, or to OSW GeoJSON for OpenSidewalks tooling and OSM upload.

### Gaps
- PEDS, other walkability index tools, UN-Habitat street audit tools and ADA PROWAG checklists (thresholds such as a 1.2 m / 4 ft minimum clear width, 2% cross slope and 8.33% ramp) were not retrieved with citations in this pass. The report writer should not quote these thresholds without a source.
- No Lebanese national sidewalk design standard (for example from the Directorate General of Urban Planning) was found.

## 6. Sampling designs, crowdsourcing with students/volunteers, and QA

### Takeaway
Where full coverage is too costly, audit stratified random samples of segments (MAPS-style segment and crossing units), for example stratified by street class, neighbourhood and land use. Double-code a subsample to measure inter-rater reliability, and use remote Street View or online audits only for the qualitative attributes. Crowdsourced labels need consensus validation: Project Sidewalk single-labeller precision can be low for some types (about 20% for missing curb ramps), while majority vote improves it.

### Cited Findings
- MAPS-Global compared on-street and online (Street View) audits in 5 countries. Mean assessment time was the same for both (22 ± 12 min), and reliability was reported per subscale — [MAPS-Global PMC7844998](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7844998/).
- Phoenix study of remote MAPS raters: 16 of 20 segment and crossing scores had fair to substantial reliability (ICC 0.448 to 0.897) — [QxMD / Phillips et al.](https://read.qxmd.com/read/29170571/reliability-between-online-raters-with-varying-familiarities-of-a-region-microscale-audit-of-pedestrian-streetscapes-maps).
- MAPS School Routes: 36 schools audited by pairs, mean 77.8 min per school (SD 29.5) — [UTHealth Dell Center slides](https://sph.uth.edu/research/centers/dell/resources/ALC25_O1.3_Burford.pdf).
- Project Sidewalk CHI 2019 validation (single-labeller):

  | Label type | Precision | Recall |
  |---|---|---|
  | Missing curb ramp | 20.5% | 69.3% |
  | Surface problem | 72.6% | 27.1% |
  | Obstacle | 47.5% | 39.9% |

  Accuracy was studied by label type, severity and majority vote, and paid workers were compared with volunteers — [Saha et al. 2019 slides](https://makeabilitylab.cs.washington.edu/media/talks/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_2019.pdf); [CHI 2019 paper](https://makeabilitylab.cs.washington.edu/media/publications/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_CHI2019.pdf).
- The most common Project Sidewalk error is labelling driveways as curb ramps. Just-in-time AI interventions (LabelAId) improved label quality — [LabelAId arXiv 2403.09810](https://arxiv.org/pdf/2403.09810).
- A course project reports over 90% precision for 4 of 5 Project Sidewalk label types using ML. This is not peer-reviewed — [UW CSE547](https://courses.cs.washington.edu/courses/cse547/24sp/old_projects/23wi/Sidewalk_Accessibility.pdf).
- Early feasibility work showed crowd workers can identify sidewalk accessibility problems from Street View — [Hara et al. ASSETS 2012](https://makeabilitylab.cs.washington.edu/media/publications/Hara_AFeasibilityStudyOfCrowdsourcingAndGoogleStreetViewToDetermineSidewalkAccessibility_ASSETS2012.pdf).
- The OSM Lebanon community and past Beirut mapping parties exist as a volunteer base — [WikiProject Lebanon](https://wiki.openstreetmap.org/wiki/WikiProject_Lebanon); [Beirut Mapping Party](https://wiki.OpenStreetMap.org/wiki/Lebanon/Beirut_Mapping_Party).

### Inferences: suggested Lebanon design
- **Sampling frame:** all street segments from OSM (centreline split at intersections).
- **Strata:** municipality or cadastral zone × street class (primary / secondary / local) × dominant frontage (commercial / residential / mixed).
- **Sample:** a random sample of about 5 to 15% of segments per stratum. Census-audit all segments in a few high-priority pilot neighbourhoods (for example Hamra, Mar Mikhael, Tripoli old souks) to calibrate.
- **QA:**
  - Double-audit about 10% of segments by an independent team and report ICC or kappa for each attribute.
  - Run a training day using MAPS-style training (MAPS reports 3 days).
  - Use photo evidence on every obstruction record.
  - Use mandatory and constrained fields in Kobo/QField (ranges for width 0 to 10 m and curb height 0 to 40 cm).
  - Apply validation rules: clear width ≤ total width; remaining clear width ≤ clear width.
  - Re-measure a random 5% with RTK or SLAM as ground truth.
- **Tiered method:**
  - Tier 1: Street View or remote audit for presence and type, with majority vote from 3 or more labellers. Street View coverage and recency in Lebanon must be checked.
  - Tier 2: field Kobo/QField audit with wheel and laser for dimensions on sampled segments.
  - Tier 3: SLAM or RTK on a calibration subsample.
- **Comparative summary:** see the table below. Cells marked [unsourced] are inferences, not sourced figures.

| Method | Accuracy | Speed | Equipment cost | Skills |
|---|---|---|---|---|
| Manual audit (tape, wheel, laser, Kobo/ODK) | mm–cm on measured dims; location at phone-GPS level of about 5–10 m ([Ng 2021](https://ira.lib.polyu.edu.hk/handle/10397/92730?mode=full)) | About 22 min per audit unit ([MAPS-Global](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7844998/)); km/day not found [unsourced: a few km/day per pair] | Very low; Kobo free for nonprofits ([Kobo](https://www.kobotoolbox.org/blog/supporting-future-growth-and-accessibility-introducing-kobotoolboxs-new-plan-model)) | Low; MAPS training 3 days ([NCCOR](https://tools.nccor.org/measures/measure/1044)) |
| RTK GNSS survey (Emlid plus LEB-CORS) | 1–3 cm with fix ([LEB-CORS](https://lebcors.army.gov.lb); [Emlid RX specs](https://reach.dog/shop/advexure/products/emlid-reach-rx)) | Not found | USD 2,199–3,000 per rover ([Advexure](https://advexure.com/collections/emlid-rtk-gnss-receivers-and-surveying-tools/products/emlid-reach-rs3)) | Moderate |
| Smartphone LiDAR (iPhone/iPad Pro) | 3–6 cm relative on small objects ([ISPRS 2022](https://isprs-archives.copernicus.org/articles/XLIII-B2-2022-303/2022/isprs-archives-XLIII-B2-2022-303-2022.pdf)); under 0.5 m within 5 m for an automated pipeline ([iOSPointMapper](https://arxiv.org/pdf/2512.22392)) | Not found | Device cost only (not sourced) | Low–moderate |
| Handheld SLAM | ~1 cm relative / 3–5 cm absolute with RTK ([3Dsurvey](https://3dsurvey.si/7-slam-scanners-put-to-the-test/); [Radiance Fields](https://radiancefields.com/xgrids/lixel-l2-pro)) | Not found [unsourced: about 5–15 km/day] | EUR 3,000–50,000 ([3Dsurvey](https://3dsurvey.si/7-slam-scanners-put-to-the-test/)) | High (processing) |
| Vehicle MMS | 2 cm H / 5 cm V positioning, post-processed ([Trimble](https://www.monsenengineering.com/wp-content/uploads/2024/02/022516-715-en-US_Trimble_MobileMappingSolutions_ProductComparison_USL_0224_LRsec.pdf)); sidewalks occluded by parked cars ([MPC](https://rosap.ntl.bts.gov/view/dot/87091)) | Not found | Not published | High |
| Crowdsourcing (Street View / OSM) | Single-labeller precision 20–73% depending on type ([Saha 2019](https://makeabilitylab.cs.washington.edu/media/talks/Saha_ProjectSidewalkAWebBasedCrowdsourcingToolForCollectingSidewalkAccessibilityDataAtScale_2019.pdf)) | High (remote) | Near zero | Low, but needs validation |

### Gaps
- No published km/day figures for any of the field methods. All throughput numbers above marked [unsourced] are reasoned estimates only.
- No source on Google Street View coverage or recency for Lebanese cities, or on Mapillary or KartaView coverage in Lebanon.
- No published Lebanese sidewalk audit or university mapathon on sidewalks was found. AUB, LAU and USJ urban labs may have unpublished work.
- No sample-size calculations specific to sidewalk-width estimation were found.
