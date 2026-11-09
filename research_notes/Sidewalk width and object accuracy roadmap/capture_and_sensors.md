# Capture approaches and sensors for guaranteed sidewalk-width (≤0.3–0.5 m) and object-position (≤0.5 m) accuracy in Beirut

Research note (Nov 2026). Scope: purpose-captured imagery, smartphone LiDAR, backpack/handheld LiDAR + RTK, VHR satellite/aerial, Lebanese open geodata, ground-truth sampling. Caveat on method: about 20 search/fetch calls. Several figures come from search-engine summaries of the source, not from reading the full text. These are marked "(summary)" and should be checked before anyone quotes them in a publication. Several primary PDFs could not be read (403 errors, compressed PDF, paywall, or a TLS certificate error on lebcors.army.gov.lb).

## 1. Purpose-captured walking imagery (360° cameras on a pole or helmet at a known height; Mapillary upload or local SfM)

### Takeaway
I found no peer-reviewed study that validates sidewalk *width* from a 360° walking capture. The evidence comes from two sides:
- Close-range 360° photogrammetry reaches mm to cm accuracy in controlled scenes such as tunnels and urban test sites.
- Single-view width estimation becomes sub-0.3 m MAE only once camera height (metric scale) is fixed. Pitch/horizon error is the next largest error source.

So a pole-mounted camera at a *measured* height, ideally processed multi-view (SfM), plausibly brings width MAE from about 0.85 m to about 0.25 m. This is an inference that the team would need to verify locally.

### Cited Findings
- **UrbanVGGT (arXiv 2603.22531, 2026), single-image pipeline.** SegFormer-B5 segmentation, VGGT 3D reconstruction, RANSAC ground plane, metric scale from a fixed 2.5 m camera-height prior. Tested on about 300 Google Street View crops in Washington, D.C. (640×640, 90° FOV), with ground-truth widths of 0.56–3.94 m taken from Lieu & Guhathakurta 2025. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
  - Calibrated full pipeline: MAE 0.252 m, RMSE 0.293 m; 49.9% of errors <0.25 m and 95.5% <0.50 m.
  - Without scale calibration: MAE 1.571 m, 0% of errors <0.5 m.
  - Pinhole-only variant: MAE 1.096 m.
- **UrbanVGGT camera-height sensitivity.** Assumed height of 2.00 m gives MAE 0.384 m (bias −0.38 m); 2.50 m gives MAE 0.252 m (bias −0.055 m); 3.00 m gives MAE 0.349 m (bias +0.263 m). Underestimating the height underestimates width. The listed failure modes include parked cars, pedestrians, poles and vegetation occluding the edges, driveway ramps and cross-slopes, very narrow sidewalks, and bulb-outs. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1)
- **ProjectSidewalk/RampNet issue #217, Seoul test.** iPhone photos at a fixed 1.0 m height, Mask2Former (Mapillary Vistas), sidewalk-plane fit, horizon taken from the vanishing point. Held-out set of 254 photos. — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
  - Clear-width MAE 0.77 m (95% CI 0.50–1.06); total-width MAE 0.72 m; bias +0.29 m.
  - Assuming a level horizon instead gave a bias of −0.66 m.
  - Every ±2° of pitch changes width by ±10–16%. A 10% camera-height error gives a 10% width error.
  - From a 2.5 m height, 1° of angular error is about 0.3 m of ground at 6 m range and about 1.6 m at 15 m. The author recommends measuring at the point nearest the camera.
  - Projecting a 15 cm curb onto the road plane overstates width by about 6%.
- **Public ground-truth dataset.** The Seoul Sidewalk Accessibility Image Dataset (MIT Senseable City Lab) has 514 iPhone photos with *laser-measured* effective width. Licence CC0, Zenodo 10.5281/zenodo.22699523. It is useful as an external benchmark and as a protocol template. — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- **360° photogrammetry in a tunnel.** The 360° camera model's distance error against a TLS reference was 0.0046 m. Acquisition was about 3× faster than with a DSLR. — [Remote Sensing 14(21):5494](https://www.mdpi.com/2072-4292/14/21/5494) (summary)
- **"Fast survey procedures in urban scenarios: some tests with 360° cameras".** With good lighting and non-homogeneous texture, spatial accuracy of "tens of mm" is achievable. — [ResearchGate](https://www.researchgate.net/publication/366134361_FAST_SURVEY_PROCEDURES_IN_URBAN_SCENARIOS_SOME_TESTS_WITH_360_CAMERAS) (summary; full text 403). Earlier assessment of low-cost 360° cameras for 3D models: [ISPRS Archives XLII-2 (2018)](https://isprs-archives.copernicus.org/articles/XLII-2/69/2018/isprs-archives-XLII-2-69-2018.pdf)
- **Vendor claim, not peer-reviewed.** Mosaic claims cm-level accuracy for GNSS/IMU-referenced 360° photogrammetry (ARX Geo 360). — [Mosaic51](https://www.mosaic51.com/featured/accurate-measurements-without-lidar-demystifying-360-photogrammetry-with-arx-geo-360o/)
- **Mapillary camera recommendation.** Mapillary recommends the GoPro MAX 2 as its consumer 360° camera because it has built-in GPS and native support in the Desktop Uploader and mapillary_tools. Insta360 X3/X4 need "manual, time-consuming steps". For walking, Mapillary suggests 360° time-lapse at 1 frame every 2 s (16 or 29 MP on the MAX 2) on a stick. — [Mapillary cameras](https://www.mapillary.com/cameras); [Mapillary help](https://help.mapillary.com/hc/en-us/articles/360012674619); [Mapillary forum](https://forum.mapillary.com/t/insta-360-x5-camera/9516)
- **Prices and image quality.** Insta360 X5 about $499–549; GoPro MAX 2 about $449–499. Reviewers rate the X5 better in low light and describe MAX 2 footage as noisy and underexposed in dim scenes. — [DroneXL](https://dronexl.co/2025/10/10/best-360-camera-gopro-max-2-dji-osmo-360-insta360-x5/); [TechRadar](https://www.techradar.com/cameras/360-cameras/black-friday-360-camera-deals-my-expert-picks-from-dji-gopro-insta360-and-more)
- **SfM software with 360° fisheye input (anecdotal).** One user's Insta360 X5 footage: Metashape aligned 110/300 images, COLMAP 260/300. Insta360's own consumer "spatial capture" splatting tool failed to reconstruct a staircase in a Paris street. — [r/GaussianSplatting](https://lr.in.psf.lt/r/GaussianSplatting/comments/1klqyuq/gaussian_splatting_with_the_insta360_x5); [radiancefields.com](https://radiancefields.com/insta360-launches-a-spatial-capture-challenge)

### Inferences
- **Why the current errors are what they are.** Car panoramas give about 1.9 m MAE and on-foot crowdsourced photos about 0.85 m. The research above lists three dominant error terms: unknown camera height, pitch, and occlusion. Purpose capture fixes the first two by design:
  - A pole of known length, with height measured to ±2 cm on 2.5 m (<1% scale error), removes the 10%-per-10% height term.
  - The 360° cameras' built-in IMU gravity vector, or vanishing-point horizon estimation, controls pitch.
  - Walking *on* the sidewalk puts both edges within about 1–4 m of the camera, where 1° of error costs only a few cm. This is well inside the regime where UrbanVGGT reached 0.25 m MAE.
- **Width needs no absolute accuracy, object positions do.** Width is a *relative* measurement, so GNSS error largely cancels; what matters is local scale plus edge localisation. Object positions ≤0.5 m are *absolute*. They need either RTK-tagged camera positions (see section 3, LEB-CORS) or SfM tied to a few RTK-surveyed ground control points. Phone or camera GNSS in Beirut street canyons (several metres of error) cannot meet 0.5 m on its own.
- **Per-edge error budget.** For width error ≤0.3 m at about 1σ, each edge must be located to about 0.21 m (0.3/√2), assuming independent edges. For ≤0.5 m, each edge needs about 0.35 m. Edge segmentation at 1–3 m range on a 5.7K–8K 360° frame gives roughly 1 cm per pixel, so segmentation boundary noise is not the bottleneck. Occlusion and edge definition are: curb face vs. top, building line vs. shop extensions.
- **Capture effort per km of street (estimated, not measured in any source).**
  - Both sides must be walked, so 1 km of street is about 2 km walked. At about 4 km/h plus crossings and pauses, that is roughly 35–60 min of capture per street-km for one person.
  - At 1 frame per 2 s, the frame spacing is about 2.2 m, about 450 frames per side-km. For SfM, video or 1 frame/s with ≥80% overlap is safer.
  - Car-occluded segments benefit from walking *on* the sidewalk with the pole held over the parked cars.
- **Processing on the laptop.** Local SfM (COLMAP/GLOMAP or OpenSfM; Metashape if licensed) of a few hundred 360° frames per block is feasible on an 8 GB GPU. Expect seconds to minutes per hundred images for GLOMAP; this is unverified. Gaussian splatting is not needed for measurement; SfM plus MVS or monocular depth with SfM scale suffices.

### Gaps
- No peer-reviewed, ground-truthed 360° *walking* capture → sidewalk-width accuracy study was found. Run a local pilot.
- Exact RMSE numbers and capture-time figures in the urban 360° tests paper (full text blocked).
- No independent numbers on Insta360 X4/X5 or MAX 2 GNSS accuracy in urban canyons. Ricoh Theta was not researched.

## 2. Smartphone LiDAR (iPhone Pro / ARKit apps) and Android ToF / ARCore depth

### Takeaway
iPhone LiDAR is accurate to about 1–3 cm for objects and short features. However, its effective range is only about 5 m, and drift accumulates with path length; reported errors are >25 cm for features longer than 4 m, and about 10 cm over a 130 m scene. That makes it fine for *spot* cross-section measurements (a cheap ground-truth tool), but not a reliable km-scale sidewalk mapper without loop closure or control points.

### Cited Findings
- **Indoor iPhone/iPad LiDAR vs. TLS.** Errors were 1–2 cm for short features but could exceed 25 cm once a feature exceeded about 4 m in length. — [Tandfonline 2024](https://www.tandfonline.com/doi/full/10.1080/16874048.2024.2408839) (summary)
- **Urban smartphone-LiDAR review.** A 130 m cliff scanned with an iPad Pro 2020 and an iPhone 12 Pro gave about 0.1 m accuracy. Bad scan closures were attributed to inertial drift. Accuracy is about 1–3 cm when no problems occur. — [MDPI Applied System Innovation 5(4):63](https://www.mdpi.com/2571-5577/5/4/63) (summary)
- **Free iPhone LiDAR apps (2026).** Some apps showed cumulative start-to-end drift on loops. In a long, feature-poor corridor one app lost trajectory consistency entirely and inverted a wall by 180°. — [Springer J. Geovis. Spatial Anal. 2026](https://link.springer.com/article/10.1007/s41651-026-00288-x) (summary; paywalled)
- **Medium-sized indoor/outdoor areas.** Errors were about 1 cm in some areas and about 10 cm in others. The apps with loop closure performed best. — [ResearchGate 2024](https://www.researchgate.net/publication/387064398_Assessing_the_effectiveness_of_LiDAR-based_apps_on_Apple_devices_to_survey_indoor_and_outdoor_medium_sized_areas) (summary)
- **Tamimi (iPhone 13 Pro).** The study stresses that drift scales with distance travelled. — [Tamimi PDF](https://pdfs.semanticscholar.org/cd99/5786566cc4690adcdf6e7bc55a13d9628b4b.pdf)
- **Outdoor forested streambed mapping with iPhone LiDAR.** — [Sensors 25(19):6141 (2025)](https://www.mdpi.com/1424-8220/25/19/6141) (accuracy figures not extracted)

### Inferences
- A sidewalk cross-section is typically 1–5 m, inside the range where iPhone LiDAR is at the cm level. A 10-second scan per cross-section in Polycam, 3d Scanner App or SiteScape gives a ground-truth width plus curb height. This is faster than tape in traffic and keeps a 3D record. Long continuous scans of whole blocks are not advisable.
- Absolute georeferencing is still needed for object positions; iPhone GNSS in canyons is metres off. An external RTK receiver is required (e.g. the Dot3D or SiteScape/Emlid workflows; not verified in this research).
- Android ToF and ARCore Depth API: no accuracy studies were found in this pass.

### Gaps
- No study of iPhone LiDAR along ≥100 m of urban street with RMSE against a survey reference.
- Android ToF/ARCore depth accuracy and range for street mapping.
- Accuracy of Dot3D, SiteScape and similar apps with RTK.

## 3. Backpack/handheld LiDAR SLAM and RTK GNSS (including correction availability in Lebanon)

### Takeaway
Two main findings:
- **LiDAR SLAM.** Commercial SLAM scanners (Leica BLK2GO, NavVis VLX) reach 1–6 cm in independent tests but cost tens of thousands of USD (quote-only). A DIY Livox Mid-360 plus FAST-LIO2 rig achieves about 6–11 cm trajectory RMSE in benchmarks and was judged suitable for backpack MLS. Either option easily meets the 0.3 m width target.
- **RTK corrections.** Lebanon has a national CORS network, LEB-CORS: 13 stations, NRTK with ±3 cm claimed accuracy, and RINEX download, run by the Army's Directorate of Geographic Affairs. RTK for absolute positions, or for GCPs, is therefore technically available.

### Cited Findings
- **LEB-CORS.** Run by the Directorate of Geographic Affairs (DAG, Lebanese Army). 13 stations, available 24/7. Real-time RTK/NRTK positioning at "±3 cm", and raw observations downloadable in RINEX, including virtual reference station RINEX for post-processing. Covers "all Lebanese territories on which there is internet". — [LEB-CORS portal](https://lebcors.army.gov.lb) (portal content via search summaries; direct fetch failed with a TLS certificate error)
- **Separate network, do not confuse.** CNRS runs 12 permanent geophysical stations (GRAL), which are not an RTK service. — [CNRS Lebanon](https://cnrs.edu.lb/site/SubPage.aspx?pageid=59)
- **NOAA "LEBA" station.** NOAA lists a station log and coordinates for a station "LEBA". It is unclear whether this is in Lebanon. — [NGS station log](https://www.ngs.noaa.gov/corsdata/station_log/leba.log.txt)
- **Municipal RTK procurement.** Tripoli municipality tendered GNSS RTK equipment with NTRIP support in July 2026, a sign that municipal RTK use is current practice. — [Tripoli tender PDF](https://tripoli.gov.lb/wp-content/uploads/2026/07/شراء-GNSS-RTK-دعوة-ثانية.pdf)
- **Livox Mid-360.** An ISPRS 2025 assessment of 35 Mid-360 units against TLS found accuracy within the manufacturer's specification. It concluded the sensor can be used for mapping and backpack mobile laser scanning. — [ISPRS Archives XLVIII-1-W6-2025-147](https://isprs-archives.copernicus.org/articles/XLVIII-1-W6-2025/147/2025/isprs-archives-XLVIII-1-W6-2025-147-2025.pdf) (summary; numeric values not extracted)
- **FAST-LIO2 on Mid-360 data.** Community benchmark, not peer-reviewed. — [Open Robotics Discourse](https://discourse.openrobotics.org/t/slam-benchmark-on-livox-mid-360-public-dataset-our-own-uav-flight-data-kiss-icp-dlio-fast-lio2-glim/57912)
  - TIERS public dataset vs. OptiTrack ground truth: APE RMSE 0.060 m for FAST-LIO2, 0.124 m for KISS-ICP, 0.025 m for GLIM.
  - The author's own UAV flights: 0.112 m for FAST-LIO2.
- **Mid-360 360° FOV.** It gives FAST-LIO2 enough geometric constraints. — [Swarm-LIO, arXiv 2209.06628](https://arxiv.org/pdf/2209.06628)
- **BLK2GO vs. NavVis VLX, independent comparison.** Gharineiat et al. 2024 (Remote Sensing 16:3256) found outdoor/indoor errors of 10–60 mm. — [USQ repository PDF](https://research.usq.edu.au/download/eb1c0ea8835e970a28490f9f3277ad583c07f60af72082e5b4840952f9e74bf5/3433394/remotesensing-16-03256%20%281%29.pdf) (summary)
- **BLK2GO vs. NavVis VLX, vendor specs.** BLK2GO about 6–15 mm relative (older sheet ±3/±10 mm). VLX3 5 mm local and 10 mm 3D point accuracy. VLX3 weighs 8.5 kg, BLK2GO 775 g. — [thefuture3d comparison](https://www.thefuture3d.com/equipment/compare/leica-blk2go-vs-navvis-vlx3/); [ATG USA](https://atgusa.com/?p=16408)
- **Price.** Both are quote-only. A competitor's page claims BLK2GO total cost of ownership is ">$120k" and also "less than half of VLX3"; the two claims contradict each other and should not be relied on. — [thefuture3d](https://www.thefuture3d.com/equipment/compare/navvis-vlx3-vs-leica-blk2go)

### Inferences
- **A DIY rig is the realistic option.** At university budget, a Mid-360 (a few hundred USD; price not verified here) plus a small single-board computer or the laptop running FAST-LIO2, GLIM or LIO-SAM is the realistic LiDAR path. A trajectory RMSE of about 0.06–0.11 m implies width error well under 0.3 m, because width is measured within a single scan where relative accuracy is cm-level. Cars parked on sidewalks still occlude; a 360° LiDAR at head height sees over car roofs better than a car-mounted camera.
- **Absolute object positions.** Tie the SLAM map to a few points surveyed with a ZED-F9P or Emlid receiver on LEB-CORS NRTK, every 100–200 m in open spots such as intersections (rule of thumb, not sourced). This yields ≤0.1–0.2 m absolute accuracy, well within 0.5 m.
- **Security and permit risk.** LEB-CORS is Army-operated. Registration, fees and eligibility of foreign or university users were not confirmed. Carrying survey GNSS or LiDAR equipment in Beirut may draw security questions, given the March 2026 heightened-security context (drone permits suspended nationwide; see section 4). Letters from the university or municipality are advisable. These are inferences.

### Gaps
- LEB-CORS registration process, fees, NTRIP mountpoints, and the datum/projection used (likely the Lebanese Stereographic grid and/or ITRF; not confirmed).
- Peer-reviewed accuracy of a backpack Mid-360 rig in an *urban street canyon*.
- Mid-360, ZED-F9P and Emlid Reach RS3/RX prices and Lebanon import availability; not researched in this pass.
- RTK fix availability and multipath in Beirut street canyons; no Beirut-specific data found.

## 4. Very-high-resolution satellite or aerial imagery for curb and sidewalk edges

### Takeaway
30 cm satellite imagery (Pléiades Neo) is cheap for Beirut, roughly $560–$2,100 for a 25 km² archive minimum depending on licence tier. However, no study was found that demonstrates curb-line or width accuracy ≤0.3–0.5 m from 30 cm satellite data. Sidewalk segmentation from aerial orthophotos reaches about 83% mIoU. Tree cover, building lean and parked cars are the limiting factors. Drones, the obvious alternative, are currently barred: all drone permits were suspended nationwide from 1 March 2026 "until further notice".

### Cited Findings
- **Pléiades Neo archive pricing (LandInfo, Jan 2026).**
  - 30 cm panchromatic: $22.50 and $32.50 per km².
  - A higher tier: $55.00 and $82.50 per km² (probably a different product or licence level).
  - Archive pricing applies only to imagery ≥90 days old; minimum archive order 25 km² per contiguous area.
  - Apollo Mapping also gives a 25 km² archive minimum. SkyWatch lists a 1 km² minimum AOI with a 5 km² minimum billable area, and HD15 (15 cm, an enhanced product) at $25/km² with a 25 km² minimum. Airbus OneAtlas states there is no minimum order.
  - Sources: [LandInfo pricing](https://landinfo.com/satellite-imagery-pricing.html); [LandInfo PDF Jan 2026](https://landinfo.com/wp-content/uploads/Imagery_LandInfo_202601-1.pdf); [Apollo Mapping](https://apollomapping.com/pleiades-neo-satellite); [SkyWatch](https://skywatch.com/geospatial-data-providers/airbus/); [UP42 Pléiades Neo](https://docs.up42.com/data/pleiades-neo); [Airbus OneAtlas](https://api.oneatlas.airbus.com/guides/oneatlas-data-pay-per-order/g-odp-pleiade-neo-archive/) (summary; minimums conflict between vendors)
- **Sidewalk segmentation from orthoimages (NYC, 2021).** 83% mIoU on held-out data, with width, angle and curvature computed from the masks. Sidewalks are a small share of pixels and are often occluded by trees and bridges. — [Hosseini et al., arXiv 2112.06120](https://arxiv.org/pdf/2112.06120)
- **Sidewalk networks from aerial imagery plus street view.** Street-view imagery links 20% of dangling segments. The reference standard used was aerial imagery better than 0.3 m. — [SAGE EPB 2021](https://https-sage-cnpereading-com-443.webvpn1.xju.edu.cn/doi/10.1177/2399808321995817) (summary)
- **Aerial sidewalk, crossing and corner-bulb dataset.** — [arXiv 2303.02323](https://arxiv.org/pdf/2303.02323)
- **Other recent Lebanese imagery used in published studies.** A Ministry of Environment/UNDP study used 40–80 cm satellite imagery covering 2020–2023. Another study used Airbus Vision-1 imagery at 87 cm (June–July 2023). — [MoE Lebanon](https://climatechange.moe.gov.lb/viewfile.aspx?id=345) (summary)
- **Beirut basemap.** The Beirut Urban Lab, with CNRS, produced a municipal Beirut basemap from land-registry and municipal maps plus "high-resolution aerial images". The date and resolution are not stated. — [Beirut Built Environment Database storymap](https://storymaps.arcgis.com/stories/19bc244c14ac44aca83a630e4637bfae) (summary)
- **Mapping agency.** The Directorate of Geographic Affairs is responsible for geodetic, topographic, cadastral and aerial surveying and official mapping. — [Lebanese Army DAG page](https://www.lebarmy.gov.lb/en/node/3984)
- **Drone permit suspension.** The Lebanese Army suspended all drone flight permits issued by its command nationwide, effective 1 March 2026, until further notice. An earlier 24-hour Beirut-only suspension took place in February 2025. Permit authorisation comes from military intelligence; municipalities only handle applications. — [LBCI](https://www.lbcgroup.tv/news/lebanon-news/908645/lebanese-army-suspends-drone-permits-nationwide-amid-regional-tensions/en); [Lebanese Army](https://www.lebarmy.gov.lb/en/node/136053); [L'Orient Today](https://today.lorientlejour.com/article/1478009/ghada-ayoub-welcomes-jezzine-drone-ban-reversal.html)

### Inferences
- **Edge accuracy limit.** At 30 cm GSD, a ±1-pixel edge error per side gives width σ ≈ 0.42 m (0.3·√2). That alone exceeds the 0.3 m target and only marginally meets 0.5 m, before counting:
  - off-nadir building lean, which hides the sidewalk against façades in Beirut's narrow streets;
  - tree canopy;
  - parked cars on sidewalks.
  Satellite imagery suits curb-line *topology* and wide-boulevard checks, not a *guaranteed* width product. HD15 (15 cm) is a resampled enhancement, so its edge accuracy should not be assumed to be 15 cm.
- **Licence.** Airbus/Maxar end-user licences generally allow derived vector products, but the terms vary by tier, which likely explains the price tiers. This must be confirmed in the specific EULA before use as ML training data or before publishing derivatives (not verified here).
- **Cost.** Beirut's administrative area is about 20 km², under the 25 km² minimum (area figure from general knowledge, not sourced here). At $22.50–$82.50/km² × 25 km², a one-off purchase is roughly $560–$2,100.

### Gaps
- No paper reports curb-line RMSE or width accuracy from 30–50 cm *satellite* (rather than aerial) imagery.
- No Lebanese national orthophoto release for 2024–2026 was found. DAG/CDR orthophoto resolution, date, access and licence are unknown; enquire directly.
- SkySat 50 cm and Maxar/Vantor 30 cm pricing and licence for Beirut were not researched.
- Whether the drone suspension has been lifted after March 2026; nothing found.

## 5. Open existing Lebanese geodata on curbs and sidewalks (AUB, Beirut Urban Lab, UN-Habitat, OCHA, municipality)

### Takeaway
No open, georeferenced curb or sidewalk-width dataset for Beirut released since 2024 was found. The most relevant prior work is the MIT–AUB "Community Streets" survey, which reports statistics but no public width dataset, plus older AUB walkability shapefiles (2013).

### Cited Findings
- **MIT–AUB Beirut survey statistics.** About 6% of street length lacked sidewalks and about 17–18% had sidewalks with permanent obstructions. About 20% of sidewalks were narrower than the 1.2 m comfortable passing width. — [L'Orient Today](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html); [MIT City Form Lab](https://cityform.mit.edu/projects/beirut-community-streets); [Dar/Sevtsuk report PDF](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)
- **MIT DUSP news (Oct 2022).** Mentions only a "comprehensive survey of street networks" used to calibrate a pedestrian-flow model. No width method, licence or download is given; a working paper is linked. — [MIT DUSP](https://dusp.mit.edu/news/increasing-sidewalk-accessibility)
- **AUB walkability study.** A repository item includes GIS shapefiles from a 2013 walkability study of the AUB neighbourhood (Hamra/Ras Beirut). — [AUB ScholarWorks](https://scholarworks.aub.edu.lb/items/6b068c29-e48b-4304-aee4-c2a1581b0bd3/full)
- **UCL Institute for Global Prosperity (2025).** Open-access walkability report on Ras El Nabaa (Toufic Salem Street). — [UCL Discovery](https://discovery.ucl.ac.uk/id/eprint/10211185)
- **AUB pedestrian-safety project.** Covers older adults in Beirut neighbourhoods; qualitative (photovoice). — [AUB](https://www.aub.edu.lb/Neighborhood/Pages/pedestriansafety.aspx)
- **Beirut Urban Lab / CNRS municipal basemap.** — [storymap](https://storymaps.arcgis.com/stories/19bc244c14ac44aca83a630e4637bfae)

### Inferences
- The MIT–AUB Community Streets team (Sevtsuk) probably holds segment-level sidewalk-width data for central Beirut. Contacting them, or the Beirut Urban Lab for the basemap, is the fastest route to a Beirut benchmark with existing ground truth. This fits the team's "benchmark on area with existing ground truth" goal.
- The AUB 2013 shapefiles may give a small, dated benchmark around Hamra. Many sidewalks have since been rebuilt, notably after the 2020 blast, so they should be re-checked in the field.

### Gaps
- No UN-Habitat, OCHA/HDX or Beirut municipality sidewalk or curb layers were found in this pass. HDX was not searched directly.
- Licence and availability of the MIT–AUB survey data and the Beirut Urban Lab basemap.

## 6. Ground-truthing: a statistically sufficient tape/laser validation set and field protocol

### Takeaway
The required sample size depends on the spread of the absolute errors. To estimate MAE within ±0.1 m at 95% confidence you need about (1.96·SD|e| / 0.1)² cross-sections: about 35 if SD|e| = 0.3 m, about 96 if 0.5 m, about 190 if 0.7 m. To *guarantee* that ≥95% of widths fall within tolerance at 95% confidence, a zero-failure test needs 59 consecutive in-tolerance checks. A stratified set of about 100–150 laser-measured cross-sections is therefore a defensible target. The sample-size figures are derived from standard statistics; no domain-specific source was found.

### Cited Findings
- **Existing protocol template.** Seoul dataset: 514 photos with *laser-measured effective width*, CC0. — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- **Measurement definitions matter.** No ground-truth source states whether it measures total or clear width, and clear-width and total-width MAE differ (0.77 m vs. 0.72 m in the Seoul test). — [RampNet #217](https://github.com/ProjectSidewalk/RampNet/issues/217)
- **Reference accuracies.** UrbanVGGT's D.C. reference widths (0.56–3.94 m) came from a prior study; the paper does not describe the collection protocol. iPhone LiDAR is accurate to about 1–2 cm for features under 4 m, adequate for reference widths. — [UrbanVGGT](https://arxiv.org/html/2603.22531v1); [Tandfonline 2024](https://www.tandfonline.com/doi/full/10.1080/16874048.2024.2408839)

### Inferences
- **Sample size for MAE ±0.1 m (95%).** n = (z·s/E)², with s = SD of the absolute errors from a pilot of about 20–30 sections. The team's current errors (MAE 0.85 m, so SD likely about 0.6–0.9 m) imply about 140–310 samples to pin MAE to ±0.1 m. Once errors drop to about 0.25 m MAE (SD about 0.2–0.3 m), 15–35 samples suffice. Report a bootstrap 95% CI rather than relying on the normal approximation, because error distributions are heavy-tailed (the Seoul 5th–95th percentile spread was 3.89 m).
- **Proving a tolerance, not just an MAE.** The test is a non-parametric success-run: if n consecutive checks are all within tolerance, then with 95% confidence at least 95% of the population is within it, when 0.95ⁿ ≤ 0.05, i.e. n ≥ 59. For 90% coverage, n ≥ 29. For object positions ≤0.5 m, apply the same logic to horizontal radial error against RTK-surveyed points.
- **Proposed field protocol.**
  1. **Draw the sample.** Randomly sample street segments, stratified by width class (<1.2, 1.2–2.5, >2.5 m), by street type, and by obstruction or parked-car presence. Pick 1–2 cross-sections per segment, placed at random distances along the segment and marked with paint or a photo.
  2. **Measure.** Use a laser distance meter (±2–3 mm class) perpendicular to the curb, or an iPhone LiDAR spot scan. Record two quantities: total width (curb face or top to building line or property edge) and clear width (narrowest unobstructed passage, with the obstacle type noted).
  3. **Record.** Curb height, surface type, and photos in both directions.
  4. **Georeference.** Take an RTK fix (LEB-CORS) at the curb end of each section so it can be matched to predictions and used for object-position checks. Survey 20–60 fixed objects (poles, trees, hydrants, kiosks) the same way.
  5. **Quality control.** Have two people take independent repeat measurements on about 10% of sections to quantify reference error. That error should be ≪0.1 m.
  6. **Effort.** About 3–5 minutes per cross-section with laser and photos, so about 100–150 sections is 1–2 field days for a pair (an estimate).

### Gaps
- No published sidewalk-specific sample-size guidance was found. ASPRS positional-accuracy standards (e.g. the minimum of 20–30 checkpoints) were not checked in this pass.
- No Lebanese field-safety or permitting guidance for street measurement work was found.
