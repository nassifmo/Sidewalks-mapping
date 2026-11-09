# Street-Level Imagery and Computer Vision for Mapping Sidewalk Width and Obstructions in Lebanon

Research date: 2026-11-06. About 20 search/fetch calls. Many coverage questions (exact Mapillary/KartaView/Panoramax image counts in Beirut) could not be checked without API tokens or interactive coverage maps; these are flagged in Gaps.

## Q1. Google Street View (GSV) in Lebanon: coverage, terms, pricing

### Takeaway
Lebanon got its first Google road (car) coverage only in April 2024. The imagery was captured 2021-2023 with a low-quality camera and covers parts of Beirut, Mount Lebanon and Beqaa. Before that, Google had only a 2018 Trekker "special collection" of 41 heritage sites and campuses. Google's Maps Platform terms restrict bulk download, deriving indices or datasets from imagery, and ML training. That makes GSV a poor legal basis for building a sidewalk dataset, even though the Static API is cheap ($7 per 1,000 after 10,000 free per month).

### Cited Findings
**Coverage**
- Sept 2018: Google launched a Lebanon Street View special collection. It covers 41 historical, cultural and archaeological sites (Jeita Grotto, Shouf Cedar Reserve, Baalbek, National Museum, AUB), captured with the backpack Trekker together with the Ministries of Culture and Tourism. No road-network coverage was mentioned. — [Beiruting](https://www.beiruting.com/news/10041/google-maps-opens-street-view-special-collection-in-lebanon); [The National](https://www.thenationalnews.com/arts/google-brings-lebanon-s-cultural-sites-to-the-world-in-immersive-360-1.769452); [Arabian Business](https://www.arabianbusiness.com/industries/technology/404221-google-street-view-launches-lebanon-collection)
- The 2018 collection also included universities such as AUB, Beirut Arab University and USJ, plus the Beirut Corniche. — [The961](https://www.the961.com/google-street-view-lebanons-landmarks)
- "In April 2024, Google added street view coverage in Lebanon." — [Wikipedia: Google Street View in Asia](https://en.wikipedia.org/wiki/Google_Street_View_in_Asia)
- VirtualStreets' 2024 review: "Lebanon receives its first road coverage ever, taken by the bad quality camera between 2021 and 2023." — [VirtualStreets.org](https://virtualstreets.org/index.php/2025/01/01/2024-in-google-street-view-a-look-back-and-forward/)
- The961: the 2021-2023 imagery covers the central region, including the Beirut, Mount Lebanon and Beqaa governorates. It was captured with a low-resolution camera, "resulting in distorted and pixelated images". Earlier coverage had been limited to universities and tourist sites (2018). — [The961](https://the961.com/google-street-view-is-working-in-lebanon/)
- A hobbyist blog lists Beirut imagery dated May 2021 to Apr 2023 and notes that some 2021 imagery is misplaced by GPS errors. This is low-reliability, unverified. — [muziyemi blog](https://muziyemi.blogspot.com/p/low-quality-coverage.html)

**Terms of use (ML / data extraction)**
- Helbich et al. (2024) found that Google's terms restrict bulk downloads of GSV images and the creation of image-based indices. They recommend academic licences, author statements and open imagery instead. — [arXiv 2402.11504](https://arxiv.org/abs/2402.11504)
- Secondary summaries of the Maps Platform ToS say customers may not scrape or export content, or "pre-fetch, index, store, reshare, or rehost" it. They may not "create content based on Google Maps Content"; Google's own example is a prohibition on building an index of tree locations from Street View. — [Moonlight review of Helbich et al.](https://www.themoonlight.io/review/to-use-or-not-to-use-proprietary-street-view-images-in-health-and-place-research-that-is-the-question); [ConductAtlas: no scraping](https://conductatlas.com/platform/google-maps/google-maps-platform-terms-of-service/no-scraping-or-content-extraction/)
- A third-party ToS tracker reports a clause prohibiting use of Google Maps Content to train, test, validate or fine-tune ML/AI models. — [ConductAtlas: AI/ML training prohibition](https://conductatlas.com/platform/google-maps/google-maps-platform-terms-of-service/ai-and-ml-training-data-prohibition/)
- Columbia's research methods page quotes Google's Geo Guidelines: "these restrictions apply to all academic, nonprofit, and commercial projects". It notes that enforceability is the subject of ongoing litigation. — [Columbia Public Health](https://beh.columbia.edu/2022/08/25/machine-learning-approaches-for-measuring-neighborhood-environments-in-epidemiologic-studies)

**Pricing**
- Street View Static API: 10,000 free events per month, then $7.00 per 1,000. Volume tiers fall to $5.60, $4.20, $2.10 and $0.53 per 1,000. Street View Metadata requests are free and unlimited. — [Google Maps Platform pricing](https://developers.google.com/maps/billing-and-pricing/pricing?hl=zh-cn); [Street View Static API usage & billing](https://developers.google.com/maps/documentation/streetview/usage-limits?authuser=1)
- The $200 monthly credit was replaced by per-SKU free usage thresholds from 1 March 2025. A key is required, plus a digital signature above 25,000 requests/day; the rate limit is 30,000 queries per minute. — [Street View Static API usage & billing](https://developers.google.com/maps/documentation/streetview/usage-limits?authuser=1)

### Inferences
- Project Sidewalk is the established, Google-tolerated way to use GSV for sidewalks (see Q4): humans label panoramas in an embedded viewer. Bulk downloading GSV frames to run segmentation or width extraction and storing a derived dataset would likely breach the ToS. Any GSV-based Lebanon work should therefore be human-in-the-loop labelling in an embedded viewer, or should go through a negotiated licence.
- The 2021-2023 Lebanese GSV imagery is low resolution and already 3-5 years old. Beirut street conditions change quickly (2020 port blast reconstruction, the 2024 conflict, informal occupation). So the imagery is less useful for fine measurement such as width in cm, but probably usable for presence/absence labelling.
- At $7 per 1,000 images, 100,000 frames would cost about $630 after the free tier. Cost is not the constraint; the licence is.

### Gaps
- Google's official current Service Specific Terms text could not be retrieved (the page rendered empty). The ML-training clause is cited only via a third-party tracker. Verify at https://cloud.google.com/maps-platform/terms/maps-service-terms before relying on it.
- No street-level list of which Lebanese roads have 2021-2023 car coverage, and no information on whether Tripoli, Saida, Tyre or the South are covered.

## Q2. Mapillary, KartaView and Panoramax in Lebanon: coverage, detections, licence, API

### Takeaway
Mapillary is the most practical open source of street-level imagery for Lebanon. Its images are CC BY-SA 4.0, and its API exposes machine-generated map features and detections (utility poles, benches, hydrants, signs, store signs, etc.). But Beirut coverage is community-dependent and unquantified, with known sequences from 2019 and from post-blast 2020 efforts. No evidence of KartaView or Panoramax coverage in Lebanon was found. Panoramax is still largely France-hosted, but it is a viable self-hostable open alternative.

### Cited Findings
**Coverage in Lebanon**
- The OSM wiki "Lebanon" page links to Mapillary imagery from a Lebanon drive, with a Beirut entry dated May 2019. — [OSM Wiki: Lebanon](https://wiki.openstreetmap.org/wiki/Lebanon); [WikiProject Lebanon](https://wiki.openstreetmap.org/wiki/WikiProject_Lebanon)
- After the August 2020 port explosion, the local OSM community focused on capturing Mapillary imagery in the field for damage mapping. — [HOT mailing list, Aug 2020](https://lists.openstreetmap.org/pipermail/hot/2020-August/015312.html)
- A 2025 arXiv paper on yield estimation for the 2020 Beirut explosion used Mapillary as its ground-level image source. This confirms that usable Mapillary imagery exists around the blast zone. — [arXiv 2511.16816](https://arxiv.org/pdf/2511.16816)
- Mapillary coverage is uneven because it depends on community contributions. — [Atlas: Mapillary](https://atlas.co/data-sources/mapillary)
- KartaView: crowdsourced, CC BY-SA, coverage uneven, with some regions having "few to no images". No Lebanon-specific data was found. — [Bellingcat toolkit: KartaView](https://bellingcat.gitbook.io/toolkit/more/all-tools/kartaview)
- Panoramax: open-source, federated street-view software. Its instances are currently hosted mainly by OpenStreetMap France and IGN (France). — [Wikipedia: List of street view services](https://en.wikipedia.org/wiki/List_of_street_view_services)

**Licence**
- Mapillary images are licensed CC BY-SA 4.0, with special permission to derive data for OpenStreetMap. Contributors grant Mapillary a broad commercial licence. The licence changed from CC BY-NC to CC BY-SA on 29 April 2014. — [OSM Wiki: Mapillary](https://wiki.openstreetmap.org/wiki/Mapillary)
- Mapillary-derived metadata may be published directly to OSM under the OSMF contributor terms. — [Mapillary ♡ OSM](https://mapillary.com/osm)
- An older (2019) Mapillary statement says map feature GeoJSON was provided under ODbL "for OSM editing only". Licensing of detections outside OSM is therefore ambiguous and should be checked. — [OSM Wiki: Mapillary](https://wiki.openstreetmap.org/wiki/Mapillary)

**API and automatic detections**
- Mapillary API v4 (graph.mapillary.com) needs an OAuth/client token. Image search by bbox is limited to areas under 0.01 degrees square, with up to 2,000 results per call. Radius search goes up to 50 m. `/map_features` takes `object_values` filters; detections are available at `/:image_id/detections` (base64 polygon geometry, normalised to extent 4096). — [Mapillary API docs](https://www.mapillary.com/developer/api-documentation)
- Example feature values: `object--support--utility-pole`, `object--bench`, `object--fire-hydrant`, `object--sign--advertisement`, `object--sign--store`, plus traffic-sign classes (`regulatory--stop--g1`, etc.) and `marking--discrete--other-marking`. Vector tiles: `mly1_public` (coverage), `mly_map_feature_point`, `mly_map_feature_traffic_sign`. — [Mapillary API docs](https://www.mapillary.com/developer/api-documentation)
- Rate limits: Entity API 60,000 requests/min, Search 10,000/min, Tiles 50,000/day. No usage fee is listed. — [Mapillary API docs](https://www.mapillary.com/developer/api-documentation)
- Mapillary uses CV to recognise map features ranging from traffic signs to "more experimental" object and line recognition (semantic segmentation). — [OSM Wiki: Mapillary](https://wiki.openstreetmap.org/wiki/Mapillary)

### Inferences
- In Lebanon, Mapillary's point features (utility poles, benches, hydrants, store signs, advertisement signs) could directly seed an obstruction inventory, at no cost. Classes specific to Lebanon (generators, cable bundles, street vendors, double-parked cars on sidewalks) are not among the documented feature types. They would need a custom detector run on downloaded Mapillary images, which is allowed under CC BY-SA with attribution and share-alike for the images.
- The main practical risk is sparse or old coverage, so plan for own collection (Q3) with upload to Mapillary and/or a self-hosted Panoramax instance.

### Gaps
- Number of Mapillary images or km of coverage in Beirut and other Lebanese cities: not retrievable without the interactive map or an API token. Recommend querying `mly1_public` vector tiles over Lebanon.
- Panoramax and KartaView Lebanon coverage: no sources found either way.
- Current Mapillary licence terms for computed detections and map features (ODbL vs CC BY-SA vs OSM-only): sources conflict.
- No accuracy figures found for Mapillary's own automatic detections (poles, benches).

## Q3. Collecting your own imagery: 360 cameras, mounting, cost, throughput

### Takeaway
Consumer 360 cameras cost about $300-$590 (GoPro MAX 2 at $499.99 launch, often $299-$399 on sale; Insta360 X5 at $549.99). Mapillary publishes per-camera capture settings for car, bike and walking. For driving, use 5.6K-8K 360 video at 24-25 fps, or a 0.1-0.2 s interval. No official km/day figure exists; throughput depends on speed, traffic and storage and upload (about 500 MB/min of video, roughly 10 GB/day reported by one mapper).

### Cited Findings
- GoPro MAX 2 launched Sept 2025 at $499.99 (US), $50 below the DJI Osmo 360 and Insta360 X5. It shoots 8K 360. — [Imaging Resource](https://old.imaging-resource.com/news/2025/09/23/gopro-max-2-launched-price-8k-360-video-features-and-where-to-buy); [Notebookcheck](https://www.notebookcheck.net/GoPro-Max-2-released-to-surpass-DJI-Osmo-360-and-Insta360-X5-as-only-true-8K-360-action-camera.1121741.0.html)
- GoPro MAX 2 sale prices: $299 at Amazon and $399 at B&H on Black Friday. — [TechRadar](https://techradar.com/cameras/360-cameras/ive-reviewed-all-the-major-360-cameras-from-insta360-and-dji-but-this-usd300-gopro-max-2-labor-day-deal-is-easily-the-best-value); [TechRadar Black Friday](https://www.techradar.com/cameras/360-cameras/gopro-max-2-vs-dji-osmo-360-heres-my-expert-pick-for-the-best-black-friday-360-camera-deal)
- Insta360 X5 list price is $549.99. In Europe, about €519.99 (GoPro MAX 2) vs €589.99 (X5). — [FrontDeskReview](https://frontdeskreview.com/gear/360-cameras/insta360-x5-vs-gopro-max-2/); [Mojogear](https://mojogear.eu/en/blogs/blog/gopro-max-2-vs-insta360-x5)
- Mapillary help centre: for driving, shoot 360 video at 24 fps and 5.6K; time-lapse is too sparse. For GoPro MAX, 25 fps at 5.6K (8K for MAX 2), about 500 MB per minute. For Ricoh Theta X, a 0.1 s interval while driving, since denser capture adds no positional accuracy. — [Mapillary Help Center](https://help.mapillary.com/hc/en-us/articles/360012674619); [Mapillary Help Center](https://help.mapillary.com/hc/en-us/articles/14978864052508)
- Insta360 X3 guide (secondary): 0.2 s interval at 8K for driving, about 13 hours on a 256 GB card. — [Yandex-hosted guide](https://portal.yandex.com.tr/yaozet/how_to/insta360-x3-usage-guide-for-mapillary-a8XJvzVx)
- Spacing maths: a 2 s interval at 50 km/h gives about 7 m between images, versus about 2.5 m considered ideal. — [Mapillary forum](https://forum.mapillary.com/t/what-is-the-best-360-camera-for-a-car-mapillary-camera-wiki/1311)
- One mapper reported about 10 GB/day of footage, which makes upload a practical constraint. — [Mapillary forum](https://forum.mapillary.com/t/buying-a-new-360-camera-for-mapillary-capture/3454/6)
- Bike-mounted 360 capture workflow guide (Martijn van Exel, 2023). — [mvexel.prose.sh](https://mvexel.prose.sh/20230226-capturing-360-with-mapillary-2-bike); [OSM diary](https://www.openstreetmap.org/user/mvexel/diary/401057)
- Mapillary's Ricoh Theta X contribution guidance thread. — [Mapillary forum](https://forum.mapillary.com/t/contributing-using-360-cameras-ricoh-theta-x/8192)

### Inferences
- For sidewalk width and obstructions, walking or a slow bike/scooter with a backpack- or pole-mounted 360 camera gives the best sidewalk view and camera-height consistency. Camera height is the key scale cue for width estimation (see UrbanVGGT in Q4). Car-roof capture is faster, but in Beirut, sidewalks are often occluded by parked cars, which a car on the road sees from outside the line of parked vehicles.
- Rough throughput (my estimate, not sourced): walking at about 4 km/h for 5-6 h gives about 20 km/day of one side of the street. Urban driving at about 15-20 km/h average in Beirut traffic for 5 h gives about 75-100 km/day. Storage at about 500 MB/min is roughly 150 GB for 5 h of video.
- Indicative kit budget: one camera ($300-$590), mount, spare batteries, 256 GB cards, and phone or GPS logging. About $600-$1,000 per capture team. Mapillary and Panoramax hosting is free.

### Gaps
- Ricoh Theta X/Z1 and Insta360 X4 current prices were not retrieved.
- No published km/day benchmark for Mapillary collection campaigns.
- Lebanese legal or privacy rules on street photography and drone/vehicle capture were not researched. Mapillary blurs faces and plates automatically, which was not verified here.

## Q4. Methods: crowdsourcing, segmentation, detection, depth, and width measurement accuracy

### Takeaway
There are three method families. (1) Crowdsourced virtual auditing (Project Sidewalk): about 92% label accuracy, deployed in 21-35 cities. (2) Semantic segmentation and object detection with off-the-shelf models trained on Cityscapes or Mapillary Vistas: classes include sidewalk, curb, pole, car, and for ramps YOLOv8 detectors as in ACAMAI. (3) Metric width estimation from a single image via segmentation plus 3D reconstruction or monocular metric depth. The best reported result is UrbanVGGT (2026): MAE 0.252 m, 95.5% within 0.5 m (Washington DC). A TU Wien thesis reached only 64% agreement on width classes. Obstruction detection is the weakest-studied area.

### Cited Findings
**Project Sidewalk (Univ. of Washington)**
- DC pilot: users virtually audited more than 3,000 miles of streets in GSV and labelled more than 255,000 sidewalk accessibility problems at 92% accuracy. — [arXiv 2206.13677](https://arxiv.org/pdf/2206.13677)
- Accuracy is computed from validations: agree / (agree + disagree). — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- ASSETS 2024: deployed in 21 cities across 8 countries, with over 1 million labels, 693k validations and 11k street miles. — [Project Sidewalk / NSF PAR](https://par.nsf.gov/servlets/purl/10644332)
- April 2025: 35 cities across 8 countries (US, Canada, Mexico, Ecuador, Netherlands, Switzerland, New Zealand, ...). — [PacTrans, Apr 2025](https://depts.washington.edu/pactrans/?p=8749)
- Seattle deployment: 1,608.3 km audited, 92,127 labels. Azcapotzalco (Mexico) was among the newer deployments. — [USDOT ROSAP report](https://rosap.ntl.bts.gov/view/dot/60317/dot_60317_DS1.pdf)
- Open-source codebase. — [GitHub ProjectSidewalk/SidewalkWebpage](https://github.com/ProjectSidewalk/SidewalkWebpage)
- Label types include curb ramp, missing curb ramp, obstacle in path, surface problem, and no sidewalk. Obstacle labels are only 6.4% of verified data, while curb ramps dominate. Obstruction detection is the weakest link. — [ArchUp (secondary)](https://archup.net/pedestrian-sidewalk-barriers/)
- Weld et al. (ASSETS 2019, best student paper) were the first to apply deep learning to assess sidewalks in GSV panoramas using Project Sidewalk labels. — [SIGACCESS](https://www.sigaccess.org/2019/11/2019-best-student-paper/)
- 2024 ACM fine-grained benchmark: 33 sidewalk-condition classes (cracks, uplifts, narrow, uneven, pole, sign, ...) on cropped streetscape images. — [ACM DOI 10.1145/3663548.3688531 via Unpaywall](https://unpaywall.org/10.1145%2F3663548.3688531)

**Object detection (YOLO)**
- ACAMAI (2025, IET Smart Cities): a YOLOv8 detector trained to recognise curb ramps, missing ramps, obstacles and surface problems, then applied to 360° GSV panoramas. Scanning panoramas improved coverage but produced redundant predictions that reduced precision. Per-class metrics could not be retrieved (bot-check page). — [UFP repository](https://bdigital.ufp.pt/entities/publication/efecff5b-a7d5-424b-bc5d-759ce53e732c)

**Semantic segmentation datasets**
- Mapillary Vistas v2.0 has 124 semantic categories (70 instance-annotated, 46 stuff, 8 void). Classes include Curb, Curb Cut, Sidewalk, Pole, Utility Pole, Bike Lane, Crosswalk, Barrier, etc. — [Mapillary blog: Vistas 2.0](https://blog.mapillary.com/update/2021/01/18/vistas-2-dataset.html); [mmseg Mapillary dataset classes](https://onedl-mmsegmentation.readthedocs.io/en/latest/_modules/mmseg/datasets/mapillary.html)
- Mask2Former was evaluated on Mapillary Vistas (along with COCO, Cityscapes and ADE20K). MaskFormer R50 on Vistas (65-class v1.2) scored 53.1 mIoU single-scale and 55.4 multi-scale. — [Mask2Former arXiv 2112.01527](https://arxiv.org/pdf/2112.01527v2); [MaskFormer arXiv 2107.06278](https://arxiv.org/pdf/2107.06278)

**Monocular metric depth**
- The Depth Anything V2 Metric-Outdoor models are fine-tuned on synthetic Virtual KITTI. — [Hugging Face model card](https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-Outdoor-Small-hf/blob/fd2c22027eaf20374204f14099b8341e1925ad39/README.md)
- DAv2 metric models are trained only in-domain (indoor or driving), while DAv3 metric models generalise across domains. — [LightlyTrain docs](https://docs.lightly.ai/train/stable/depth_estimation.html)
- Metric3Dv2 on a KITTI FoV-90 setting: δ1 about 0.81, AbsRel 0.147. It needs camera intrinsics. — [Depth Any Camera, arXiv 2501.02464](https://arxiv.org/pdf/2501.02464)

**Sidewalk width from street-level imagery**
- UrbanVGGT (Tan & Zhang, arXiv, March 2026) works from a single street-view image. The pipeline is segmentation, feed-forward 3D reconstruction (VGGT), ground-plane fitting, camera-height scale calibration, then directional width. Results: MAE 0.252 m on a Washington DC benchmark, 95.5% of estimates within 0.50 m. Metric scale calibration is the most critical component. The authors also released SV-SideWidth (527 OSM segments in 3 cities) and say cross-city validation is still needed. — [arXiv 2603.22531](https://arxiv.org/abs/2603.22531)
- Lieu & Guhathakurta (2026, *Environment and Planning B* 53(5):1129-1144) use street-view images at two pitch angles, CV sidewalk extraction, Canny edges and trigonometry. They pitch it as low-cost where aerial imagery is scarce. — [EconPapers/RePEc](https://econpapers.repec.org/RePEc:sae:envirb:v:53:y:2026:i:5:p:1129-1144)
- TU Wien thesis (Vienna) combines segmentation and monocular depth to classify width classes. It found 64% agreement on 8,525 images matched to reference data; it works best with a visible sidewalk, an identifiable curb and a suitable camera angle. — [TU Wien reposiTUm](https://repositum.tuwien.at/handle/20.500.12708/229239?mode=full)
- HeiGIT "HeiMeterStick" (Feb 2026) runs Depth Anything metric depth, EXIF or GeoCalib intrinsics, and SAM3 text-prompt segmentation ("sidewalk") to build a point cloud. It then fits a ground-plane alpha shape, measures centerline perpendicular width, and removes outliers with an Isolation Forest. Tested on about 80,000 Mapillary images in Łódź. No quantitative accuracy and no public code. — [HeiGIT blog](https://heigit.org/measuring-what-you-never-notice-a-computer-vision-approach-to-accessible-paths/)

### Inferences
- A realistic open pipeline for Lebanon: Mapillary or own 360 imagery, then Mask2Former, OneFormer or SegFormer trained on Mapillary Vistas v2 (sidewalk, curb, curb cut, pole, car, etc.), then a metric width step (UrbanVGGT-style camera-height calibration, or Depth Anything or Metric3D with intrinsics), then aggregation per OSM segment. Expect about ±0.25-0.5 m error at best, which separates "<1.2 m" from ">1.5 m" sidewalks but not finer distinctions.
- Own capture with a known, fixed camera height is a big advantage, because metric scale calibration dominates error.
- Lebanon-specific obstructions (generators, vendor stalls, chairs or merchandise from shops, cars parked on the sidewalk) are not standard dataset classes. Expect to fine-tune YOLO (v8-v11) on a few thousand locally labelled crops, possibly bootstrapped with open-vocabulary or text-prompt segmentation (SAM3, as used by HeiGIT).

### Gaps
- No per-class precision/recall for YOLO detection of poles, parked cars or bins on sidewalks; the ACAMAI full text was blocked.
- No published flat 124-class Vistas v2 mIoU for Mask2Former, OneFormer or SegFormer was retrieved, nor per-class IoU for "sidewalk", "curb" and "curb cut".
- The Lieu & Guhathakurta error figures were not retrieved; only the abstract is available.
- No head-to-head Depth Anything V2 vs Metric3D v2 comparison on street-view sidewalk width.
- Project Sidewalk per-city accuracy and current AI-assisted validation features were not retrieved.

## Q5. Applicability to Lebanon and MENA: informal sidewalk use, prior SVI studies

### Takeaway
Very little street-view CV research exists for Beirut. The only examples found are an AUB master's project that classifies building construction periods from street imagery, and a 2025 blast-yield study using Mapillary. No study of sidewalk width or obstruction mapping with SVI in Lebanon or MENA was found. Methods would transfer, but the local obstruction classes and the dense occlusion by parked cars need local training data and ground-truthing.

### Cited Findings
- AUB master's thesis: deep learning on street-view imagery to estimate the construction period of Beirut buildings. — [David Wardan, Beirut classifier](https://davidwardan.github.io/building/beirut-classifier)
- Trust-aware multimodal fusion for yield estimation of the 2020 Beirut explosion, using Mapillary ground-level images. — [arXiv 2511.16816](https://arxiv.org/pdf/2511.16816)
- Post-blast (2020) OSM/HOT community Mapillary capture in Beirut. — [HOT mailing list](https://lists.openstreetmap.org/pipermail/hot/2020-August/015312.html)
- Project Sidewalk has been deployed outside the Global North, for example in Azcapotzalco (Mexico City) and Ecuador. That shows the crowdsourced method can be adapted across sociocultural contexts. — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626); [PacTrans](https://depts.washington.edu/pactrans/?p=8749)
- Width-estimation accuracy degrades when sidewalks are occluded, when curbs are not identifiable, or with poor camera angles. — [TU Wien](https://repositum.tuwien.at/handle/20.500.12708/229239?mode=full); [arXiv 2603.22531](https://arxiv.org/abs/2603.22531)

### Inferences
- Beirut conditions break typical models in several ways. Cars parked on sidewalks hide the curb line. Sidewalk level changes and missing curbs are common. Shopfront spill-over and generator cabinets are frequent. Overhead wire tangles are not a ground obstruction but are visually dominant. All of these lower segmentation and width accuracy compared with US and European benchmarks, so a local ground-truth sample (tape-measured segments) is essential for calibration and error reporting.
- Low-cost hybrid for Lebanon: (a) collect walking 360 imagery at a fixed height and upload it to Mapillary or Panoramax (open, CC BY-SA); (b) run automatic segmentation, detection and width estimation; (c) have local volunteers or students validate in a Project Sidewalk-style interface. Project Sidewalk is open source, but it is built around GSV, so adapting it to Mapillary imagery would be engineering work (inferred, not verified).
- Using Lebanon's 2021-2023 GSV in a Project Sidewalk deployment is technically possible, but the imagery is low quality and dated.

### Gaps
- No MENA (Cairo, Amman, Istanbul, Gulf) sidewalk-width or obstruction SVI studies were found within the search budget. An Arabic-language and regional search is recommended.
- No data on whether Project Sidewalk has ever been deployed in an Arabic-speaking or MENA city.
- No studies quantifying informal sidewalk occupation (parking, vendors, generators) in Beirut using imagery.
