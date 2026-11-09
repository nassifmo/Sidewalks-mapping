# Sidewalk / Pedestrian-Infrastructure Mapping from Imagery in the Global South, MENA and Dense Mediterranean Cities (2015-2026): Lessons for Lebanon

Research notes compiled 2026-11-06. Scope: case studies in contexts similar to Beirut (dense, informal sidewalk use, cars parked on sidewalks, vendors, missing curbs, weak official data). Every claim has an inline source; unverified items are under "Gaps". Main finding up front: imagery/AI sidewalk mapping in MENA cities is very thin in the published literature. The best evidence comes from (a) Beirut's own MIT-AUB work, which used Mapillary because Google Street View (GSV) is limited in Beirut; (b) Project Sidewalk deployments in Mexico and India; and (c) a few cross-city and domain-shift experiments with hard numbers.

## Q1. Case studies in comparable Global South / MENA / Mediterranean cities that mapped sidewalks or encroachment with street view, satellite imagery or crowdsourcing

### Takeaway
Few peer-reviewed studies map sidewalk occupation from imagery in MENA or Mediterranean cities; most work there is field audits or perception surveys. The most transferable imagery-based precedents are:
- Project Sidewalk in Mexico City (Azcapotzalco) and San Pedro Garza García (Mexico), and in Chandigarh (India): remote crowdsourcing on GSV, with label sets adapted to local conditions.
- Mapillary-based segmentation in Kolkata.
- Low-cost body-worn smartphone video in São Paulo state (SideSeeing).
- Sidewalk width from street view tested in São Paulo and Nairobi (UrbanVGGT).
- Small encroachment-classification datasets from Bangladesh (FootpathVision).

### Cited Findings

**Latin America: Project Sidewalk Mexico (crowdsourced GSV auditing)**
- Liga Peatonal, a Mexican pedestrian NGO, contacted the University of Washington team in 2019. The team translated the interface into Spanish, added locale-specific label tags and co-branded logos, then piloted in Azcapotzalco, a Mexico City municipality of over 400,000 people across 33.6 km². — [Froehlich et al., "Towards Mapping and Assessing Sidewalk Accessibility Across Sociocultural and Geographic Contexts" (arXiv 2207.13626)](https://arxiv.org/pdf/2207.13626)
- Azcapotzalco throughput: 222 users audited 80.2 km and placed 5,864 labels. US comparisons: Seattle had 1,576 users, 1,608.3 km and 92,127 labels; Columbus had 263 users, 185.7 km and 16,277 labels; Newberg had 203 users, 224.6 km and 16,076 labels. — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- Severity (1-5, 5 worst) was consistently higher in Azcapotzalco than in the three US cities:

  | Label type | Azcapotzalco | Seattle | Columbus | Newberg |
  |---|---|---|---|---|
  | Curb ramp | 2.8 | 1.5 | 1.4 | 1.5 |
  | Missing curb ramp | 4.7 | 3.8 | 3.9 | 3.9 |
  | No sidewalk | 4.6 | 4.0 | 4.3 | 3.9 |
  | Obstacle | 4.1 | 3.2 | 2.2 | 3.1 |
  | Surface problem | 3.6 | 2.9 | 2.1 | 2.7 |

  — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- Label density per 100 m: Azcapotzalco had 1.8 obstacles and 2.5 surface problems, against 0.3-1.2 obstacles and 0.6-1.4 surface problems in US cities. It also had fewer curb ramps (1.0 per 100 m vs 1.9-4.3). — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- An earlier combined figure for Azcapotzalco and San Pedro Garza García was 10,313 labels across 115.9 km. A 2026 paper says the tool has been used in about 40-44 cities in roughly 10 countries. — [arXiv 2206.13677](https://arxiv.org/pdf/2206.13677); [Lalwani et al. 2026, arXiv 2602.09216](https://arxiv.org/html/2602.09216v1)
- The authors acknowledge that the labels record *usage* only in a limited way: imagery shows vending stands and café seating, but the authors say a full assessment needs ethnography, interviews and surveys. — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)

**South Asia: Project Sidewalk Chandigarh, India (2026)**
- The team audited about 40 km of streets in three sectors (12 institutional, 34 commercial, 45 residential) and linked results to POI access (about 10,128 unique POIs from Google Places). Gemini 2.5 Flash gave annotators "mission guidance" only; humans made every labeling decision. — [Lalwani et al., AI4UP 2026, arXiv 2602.09216](https://arxiv.org/html/2602.09216v1)
- Label set adapted for India:
  - "Curb Ramp" was replaced by "Curb Style" (sloped, stepped, broken, drainage-gap).
  - Obstacle tags added: "parked car", "carts", "drainage", "electric box". Removed: fire hydrant, mailbox, recycling bin.
  - Surface tag added: "sand/gravel/mud".
  - No Sidewalk tag added: "too dirty/cluttered".
  - Tooltip example images were replaced with Chandigarh street views.
  — [arXiv 2602.09216](https://arxiv.org/html/2602.09216v1)
- Headline result: "1,644 of 2,913 locations" where improvements could help. The paper does not define the denominator clearly. — [arXiv 2602.09216](https://arxiv.org/html/2602.09216v1)
- Raters scored the VLM guidance (50 segments, 3 raters, 1-5 scale): relevance 4.97, accuracy 4.40, usefulness 4.61. Inter-rater agreement on accuracy was weak (quadratic-weighted κ from −0.11 to 0.49). — [arXiv 2602.09216](https://arxiv.org/html/2602.09216v1)

**India: Mapillary walkability (Kolkata, 2025)**
- Ghose & Rai used Mapillary imagery and deep-learning semantic segmentation on selected Kolkata footpaths. They scored walkability (0-1) on greenery, openness, pavement and crowdedness, and found inadequate footpath widths and unsafe walking spaces, especially in the CBD. The abstract does not report image counts or accuracy. — [ISPRS Annals X-5-W2-2025, p.209](https://isprs-annals.copernicus.org/articles/X-5-W2-2025/209/2025/)
- A Delhi (Batla House) study ran pre-trained YOLOv3 on GSV imagery along 82 streets and reported 94.2% detection and 91.4% classification accuracy for street objects. It did not target encroachment. — [IIT Delhi repository](https://ir.iitd.ac.in/bitstreams/67ebc1af-4944-41ba-a521-877500f6829a/download) (as summarized in search results; full text not verified)

**Bangladesh: footpath encroachment classification**
- FootpathVision is described as an image dataset for detecting obstructions on pedestrian walkways, including street vendors and illegally parked vehicles. It is used in a 2026 paper training a custom CNN across five datasets. — [Tabassum et al., arXiv 2601.04727](https://arxiv.org/pdf/2601.04727)
- A related Bangladesh lightweight-CNN paper reports about 83.5% validation accuracy for classifying images as encroached or unencroached, vs ResNet-50 at 86.9% and VGG-19 at 86.1%. — [arXiv 2601.11911](https://arxiv.org/pdf/2601.11911) (search summary; full text not verified)
- Community datasets for footpath encroachment exist on Roboflow Universe (e.g., CC BY 4.0). — [Roboflow "Footpath encorachment"](https://universe.roboflow.com/gbc-t3bax/footpath-encorachment)

**Southeast Asia: motorbikes on sidewalks**
- A Jakarta traffic-video pipeline (YOLOv3 plus optical flow plus road/sidewalk segmentation) explicitly targets questions like "is this motorcycle illegally parked on a sidewalk?" (2018 preprint). — [arXiv 1812.01106](https://arxiv.org/pdf/1812.01106)
- A Bangkok YOLO pipeline detects motorcycles on sidewalks plus license plates, with average confidence of 0.80 (motorcycle) and 0.84 (plate). — [JCCT journal](https://so13.tci-thaijo.org/index.php/jcct/article/view/3827)
- Indonesian work on parked motorbikes reports AP above 90%, but notes that dense, irregular parking is hard to detect. — [search summary of Indonesian study](https://independent.academia.edu/asepharyono2)
- No Hanoi, Dhaka or Manila sidewalk-parking detection studies were found.

**Brazil: low-cost collection and width estimation**
- SideSeeing (USP and partners) used a chest-mounted smartphone running an open-source Android app, with the camera tilted about 70° toward the ground. Coverage:
  - 46-47 routes between transit stops and 9 hospitals in Santos, Jundiaí, São Paulo and Chicago.
  - About 12 km, about 3 hours of video, about 325,883 frames, plus IMU and GPS data.
  - A 68-element sidewalk taxonomy.
  - Segmentation accuracy is not yet reported.
  — [SideSeeing, arXiv 2407.06464](https://ar5iv.labs.arxiv.org/html/2407.06464)
- A USP study in São Miguel (a flood-prone São Paulo borough) tests Tile2Net and segmentation tools for sidewalk and flood analysis. — [SIBGRAPI 2025 extended](https://sol.sbc.org.br/index.php/sibgrapi_estendido/article/view/38280)
- UrbanVGGT (2026) estimates sidewalk width from a single GSV image.
  - On a DC benchmark of about 300 images, mean absolute error was 0.252 m, with 95.5% of estimates within 0.50 m.
  - Prototype deployment produced 1,931 valid measurements covering 527 OSM segments.
  - Segment coverage was 38.2% in NYC, 13.2% in São Paulo (Jardins/Paulista) and only 7.6% in Nairobi CBD/Westlands, attributed to sparser GSV and quality-control filtering.
  - None of Nairobi's 1,958 CBD segments had an OSM sidewalk-width tag.
  - The prototype has not been validated against ground truth in São Paulo or Nairobi.
  — [Tan & Zhang, arXiv 2603.22531](https://arxiv.org/pdf/2603.22531)

**Africa: Lagos**
- MIT DUSP's "Waka Lagos" evaluated pedestrian access to metro stations. It argues that Western walkability models miss factors like street vendors and pavement quality, which AI analysis of GSV cannot fully capture, and it relied on stakeholder workshops and on-the-ground data instead. — [MIT DUSP, Waka Lagos](https://dusp.mit.edu/node/1297) (page fetch failed; based on search snippet)

**MENA field-based studies (not imagery-based)**
- Cairo: a 2016 AUC thesis (observation and interviews) found safety and cleanliness dominate the walking experience. It recommended enforcing street-occupancy rules. — [CORE / AUC](https://core.ac.uk/works/88927372)
- Cairo: a 2023 Springer chapter covers shop-owner vs pedestrian perceptions of sidewalk territory. — [Springer](https://link.springer.com/10.1007/978-3-031-36640-6_1)
- Egypt: a 2019 paper attributes pathway damage to property owners, shopkeepers and vendors who remove or add components. — [EKB journals](https://journals.ekb.eg/article_43390.html)
- Amman: a 2024 study (resident surveys and focus groups in 3 neighborhoods) found inadequate infrastructure and weak enforcement to be the main problems. A conference paper calls for context-specific walkability tools. — [OUCI: Sidewalk Challenges in Amman](https://ouci.dntb.gov.ua/works/42nnWwm4); [Jordan Times](https://jordantimes.com/news/local/sidewalks-some-amman-areas-unwalkable-say-residents)
- Dubai: a 2021 study used Walk Score, Space Syntax, PLOS and pedestrian simulation (Palm Jumeirah, city core), with no deep learning. — [Journal of Public Space](https://journalpublicspace.org/index.php/jps/article/download/1326/842/4119)
- Riyadh: an Al-Falah case study used observed indicators (furniture, shading, connectivity). — [Sustainability 16(18):8073](https://p.gyb.elementfx.com/2071-1050/16/18/8073)
- Tehran: a 2015 image-processing study of the 17th-Shahrivar pedestrian street used field photos, not street view. — [Armanshahr](https://www.armanshahrjournal.com/93.126.25.7/index.php/fa/صفحه-اصلی/84-چکیده-پایان-نامه-های-دانشگاه-هنر/article_33001_803961fd566d61538e66d5c9d1fe920b.pdf?lang=en)
- Tehran: an objective Global Walkability Index assessment scored 54 ("moderate"). — [ASCE library](https://ascelibrary.com/doi/10.1061/40961%28319%2919) (search summary)
- Istanbul (Şişli): a wheelchair-suitability study across 20 neighborhoods used fieldwork recorded on paper maps, then GIS. — [ProQuest](https://www.proquest.com/docview/3211858736) (search summary)

**Mediterranean (Athens)**
- In 12 days in January 2025, Athens municipality recorded 5,270 traffic violations in the centre: 2,119 for parking on sidewalks and 209 on pedestrian streets. The city said 44% of violations involved sidewalks or pedestrian streets. Athens car ownership is cited at 816 vehicles per 1,000 people. — [Proto Thema](https://en.protothema.gr/2025/01/31/athens-municipality-recorded-5270-traffic-violations-in-the-city-center-over-12-days/); [Greek City Times](https://greekcitytimes.com/2024/04/14/athens-obstacle-course-for-pedestrians/)

**Global datasets usable for MENA**
- NUS Global Streetscapes contains about 10 million Mapillary and KartaView images from 688 cities in 210 countries and territories, with 300+ (346) attributes. It is CC-BY-SA-4.0 on Hugging Face, about 6 TB. — [NUS UAL](https://ual.sg/publication/2024-global-streetscapes/); [Hugging Face](https://huggingface.co/datasets/NUS-UAL/global-streetscapes)
- Tile2Net (aerial sidewalk segmentation) was trained on about 20,000 aerial tiles from Boston, Cambridge, NYC and DC. It recognised 90% or more of sidewalks and crosswalks in Boston and Cambridge, which were in its training data; transfer is claimed best for "similar environments". — [MIT News 2023](https://news.mit.edu/index%2ephp/2023/open-source-tool-mapping-sidewalks-0315); [AESOP proceedings](https://proceedings.aesop-planning.eu/index.php/aesopro/article/download/39/32)

### Inferences
- For Beirut, Project Sidewalk-style remote labeling and label-set localisation (Mexico, India) is the best-documented model. Beirut likely needs tags such as "parked car on sidewalk", "motorbike", "vendor/kiosk", "shop goods/café tables", "generator/electric box", "planters/bollards (private)", "ramp/step to building" and "no curb / curb level with street".
- Single-image width estimation (UrbanVGGT) and aerial methods (Tile2Net) are designed for US-like streets. Their documented failure modes are parked-car occlusion, very narrow sidewalks and non-planar ramps, which are exactly Beirut's dominant conditions. They should be treated as screening tools, not inventories.
- The Athens enforcement data suggests Mediterranean cities track sidewalk parking through violations rather than imagery. Beirut's municipal guard fine records could serve as a validation layer.

### Gaps
- No peer-reviewed imagery- or AI-based sidewalk-occupation study was found for Cairo, Amman, Istanbul, Tehran, Tunis, Casablanca, Riyadh/Jeddah, Dubai, Naples/Palermo, Bogotá, Lagos, Nairobi, Dhaka, Hanoi or Manila. Searches were English-only; Arabic, Turkish, Persian, French and Spanish literature was not searched.
- FootpathVision's size, classes and accuracy could not be confirmed (paper body not readable).
- ITDP/WRI city audit numbers were not retrieved. ITDP's "Pedestrians First" (2018) has 11 indicators, including block density (Manila 37 blocks/km², best; Nairobi 5, lowest), per [Eco-Business](https://www.eco-business.com/news/how-walkable-is-your-city-tool-aims-to-make-pedestrians-safer-and-happier/) and [ITDP Indonesia](https://itdp-indonesia.org/2018/10/pedestrians-first-a-new-tool-for-walkable-cities/).
- The "Urban Visual Intelligence" and "Global walkability from street view" papers were not retrieved, so no numbers are reported for them.

## Q2. Existing Lebanon/Beirut work on walkability and sidewalks using imagery or computer vision (incl. MIT City Form Lab "Beirut Community Streets")

### Takeaway
The MIT City Form Lab plus AUB "Community Streets" project (2021-2023) is the key precedent. It approximated sidewalk presence, width and quality for every street in central Beirut from Mapillary imagery, prior studies and in-person observation, because GSV is "very limited in Beirut". It then fed these into a pedestrian-flow model calibrated with counts at 90 locations. No Beirut study using automated computer vision on sidewalks was found.

### Cited Findings
- **Network:** a pedestrian network for central Beirut was built from OSM centerlines. Wide arterials were modeled as two parallel sidewalk segments joined by crosswalks; footbridges were added; highways and ramps were removed. — [Dar Urban Research Seed Fund Report 05, Community Streets (Sevtsuk)](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)
- **Sidewalk data method:** "the research team approximated sidewalk presence, width, and quality based on open street-view imagery analysis from Mapillary (Google Street View is very limited in Beirut), prior studies, and in-person observation." — [Dar/Sevtsuk report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)
- **Results:** 6% of streets lacked sidewalks completely; about 17% of existing sidewalks had permanent obstructions; about 20% of sidewalks were narrower than the 1.2 m minimum comfortable passing width. — [Dar/Sevtsuk report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf). Press coverage instead says "nearly 20 percent of Beirut's total street length had sidewalks with permanent obstructions such as streetlights, signposts, trees and parking meters", citing an unpublished MIT-AUB working paper covering Karantina and Mar Mikhael through downtown to Raouche. — [L'Orient Today](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html) (article blocked, HTTP 403; figure from search summary). **The two figures differ (17% of sidewalks vs ~20% of street length); flag this.**
- **Pedestrian counts:** taken at 90 locations between December 2021 and May 2022, at weekday AM (7:30-8:30), noon (12:30-1:30) and PM (4:30-5:30) peaks, each on at least three different days. Hamra and Raouche were added as unaffected calibration areas. PM hourly counts ranged from 7 to 416 (mean 69.8), highest in Hamra. — [Dar/Sevtsuk report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)
- **Model:** Urban Network Analysis with "perceived" route lengths. Sidewalk width, traffic volume, speed and amenities modify segment lengths, using coefficients borrowed from San Francisco data (e.g., −83.7 m per 3 m of sidewalk width per 690.2 m segment). The PM model explained 46% of variance in counts (adjusted R² 0.46), "somewhat lower than previous UNA model calibrations, likely due to lack of official built environment, population and employment data in Beirut." — [Dar/Sevtsuk report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)
- **Participation:** about 60 stakeholders took part in a two-day workshop at AUB (June 22-23, 2022), producing 3 scenarios:
  1. Footbridges, lower speeds and wider sidewalks.
  2. Removing a parking lane on Gouraud/Pasteur, widening sidewalks and adding ground-floor amenities.
  3. Converting the Charles Helou highway to a boulevard, a Karantina promenade and a park.
  The project also produced a whitepaper, "Walkability and Pedestrian Conditions in Beirut: A Background Study". — [Dar/Sevtsuk report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf); [MIT City Form Lab](https://cityform.mit.edu/projects/beirut-community-streets)
- **Publication:** Sevtsuk et al. (2024), "Pedestrian-oriented development in Beirut: A framework for estimating urban design impacts on pedestrian flows through modeling, participatory design, and scenario analysis", *Cities* 149, DOI 10.1016/j.cities.2024.104927. — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/156355)
- **Other Beirut and AUB work:**
  - Said, Abou-Zeid & Kaysi (2015) surveyed pedestrians around AUB/Hamra. Sidewalk blockage and ease of crossing shaped satisfaction; sidewalk width was not significant. — [AUB PDF](https://www.aub.edu.lb/Neighborhood/Documents/mahersaid-mayaabouzeid2015.pdf)
  - Said, Geha & Abou-Zeid ran a natural experiment on Jeanne d'Arc Street. Difference-in-differences showed interventions mainly improved safety and experience, not pedestrian counts; business reactions were mixed. — [TRID](https://trid.trb.org/view/1714144)
  - An AUB ScholarWorks community-mapping item exists for Jeanne d'Arc. — [AUB ScholarWorks](https://scholarworks.aub.edu.lb/items/37572356-2ee5-4d58-a3f8-4284638ee541)
  - A 2014 AUB thesis on Hamra walkability. — [AUB ScholarWorks](https://scholarworks.aub.edu.lb/handle/10938/10036)
  - UCL's 2024 Ras El Nabaa citizen consultation on Toufic Salem Street. — [UCL Discovery](https://discovery.ucl.ac.uk/id/eprint/10211185)
- **Policy context:**
  - The Beirut Municipality reports ongoing removal of encroachments under Governor Marwan Abboud's directives (item undated). — [Ground News](https://ground.news/article/beirut-municipality-continues-to-remove-encroachments_549f46)
  - A Municipal Guard fines list targets sidewalk parking (undated). — [Beirut.com](https://www.beirut.com/en/?p=771293)
  - A nationwide campaign removed illegal roadside "newelne" structures. — [LBCI](https://www.lbcgroup.tv/news/news-bulletin-reports/887746/lebanon-launches-nationwide-campaign-to-remove-illegal-newelne-roadsid/en)

### Inferences
- The Community Streets method is a proven, Beirut-validated "manual imagery audit plus field check" baseline. A new framework could automate its three variables (presence, effective width, obstruction) and add *temporary* occupation (cars, vendors, café tables, generators), which the MIT-AUB work flagged only as "permanent obstructions".
- The R² of 0.46, attributed to missing official data, is an argument that better sidewalk data would directly improve Beirut pedestrian modeling.
- Mapillary is the practical imagery backbone for Lebanon. Fresh pedestrian-level capture would also catch occupation that car-mounted imagery misses.

### Gaps
- The exact Mapillary coding protocol (categories, how width was estimated, number of images, time spent) is not public in the report. The *Cities* paper full text and the "Background Study" whitepaper were not retrieved.
- No AUB, LAU or USJ thesis applying computer vision or deep learning to Lebanese sidewalks was found. Nor was any public Arabic-region annotated sidewalk dataset.
- The governor's specific 2026 warning on sidewalk occupation was not found in English search. Arabic search ("إشغال الأرصفة" plus Abboud) is recommended.

## Q3. Domain shift: how models trained on US/European data perform in Global South streets; reported drops; local fine-tuning sizes

### Takeaway
Hard numbers show large drops when sidewalk models are applied to a Mexican city without local data. In San Pedro Garza García, missing-curb-ramp recall fell from 88.4% to 46.6% and obstacle recall from 60.8% to 42.0%. Training with local data restores most performance. Unsupervised domain adaptation (UDA) has not helped for US-to-India shift. Open-vocabulary detectors (Grounding DINO) do poorly zero-shot on local infrastructure but recover with light LoRA fine-tuning.

### Cited Findings
- **Duan et al. (ASSETS 2022), Project Sidewalk crops from GSV:**
  - Baseline in-city models averaged 73.9% precision, 72.1% recall and 84.1% accuracy across Seattle, Columbus, DC and San Pedro Garza García (SPGG, Mexico).
  - When SPGG was *excluded* from training:
    - Curb-ramp precision fell from 79.6% to 64.0%.
    - Missing-curb-ramp recall fell from 88.4% to 46.6%.
    - Obstacle recall fell from 60.8% to 42.0%.
    - Missing-curb-ramp accuracy fell from 89.5% to 78.1%.
  - The authors attribute this to differing urban fabrics. Example: terraced and stepped sidewalks are frequent obstacles in SPGG, but US-trained models miss them "because most sidewalk obstacles in US cities are not stairs".
  — [Duan et al. 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **Training-set sizes (unfiltered labels):**
  - SPGG: 4,528 curb ramps, 23,202 missing ramps, 53,361 obstacles, 24,967 surface problems (100,033 crops).
  - Seattle: 171,349 crops.
  - DC: 233,029 crops.
  - Test sets: about 250 crops per type per city.
  - Restricting SPGG to crowd-validated labels cut obstacles to 5,764 (about 10.8%) and *lowered* obstacle recall (60.8% to 47.6%). Larger noisy data beat smaller validated data for obstacles.
  — [Duan et al. 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **Pooling cities helps when local data is small.** Columbus (28,934 crops) did better with pooled multi-city training than with its own data alone. Pooling raised recall but lowered precision. — [Duan et al. 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **Error sources (Duan et al.):**
  - About 25% of false negatives for curb ramps, missing ramps and surface problems involved an obstacle blocking the view or nearby.
  - Obstacles "require spatial contextualization (is the object actually blocking the path?)", which is hard to judge from panoramas.
  - Driveways were confused with curb ramps.
  — [Duan et al. 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **Weld et al. (ASSETS 2019):** pre-training on DC and fine-tuning on small city datasets (Seattle, Newberg) reportedly gave 76-81% precision and 83-90% recall. — [secondary summary](https://a11y-paradise.onrender.com/reviews/69bc12412846a9204f821b87); [Weld slides](https://makeabilitylab.cs.washington.edu/media/talks/Weld_DeepLearningForAutomaticallyDetectingSidewalkAccessibilityProblemsUsingStreetscapeImagery_2019.pdf) (secondary; not verified against the paper)
- **Geographic bias in street-scene segmentation (Nair, Tseng, Rolf, 2024):**
  - Cityscapes-trained (Eurocentric) models were evaluated on about 10,547 Mapillary Vistas images.
  - Geo-bias is concentrated in *classification*, not localisation: for geo-biased classes, classification errors explain 19-88% of the disparity in detection and 10-90% in segmentation.
  - The paper cites GeoNet (Kalluri et al., CVPR 2023): UDA models "performed equal to or worse than" source-only baselines for USA-to-India shift.
  — [arXiv 2412.11061](https://ar5iv.labs.arxiv.org/html/2412.11061)
- **Roadside infrastructure (China):** zero-shot Grounding DINO reached only 25.4% (Wuhan) and 26.5% (Shanghai) AP@0.5; lightweight LoRA fine-tuning raised this to about 73-78%. — [SVII-3D, arXiv 2601.10535](https://arxiv.org/pdf/2601.10535)
- **UrbanVGGT width estimation:** validated only on about 300 DC images. The authors warn that this is "not for broad claims of cross-domain robustness". Failure modes: occlusion by parked vehicles, pedestrians, furniture and poles; very narrow sidewalks; ramps and curb cuts. — [arXiv 2603.22531](https://arxiv.org/pdf/2603.22531)
- **Tile2Net:** headline accuracy (90% or more) is on training cities; transfer is claimed for "similar environments" with optional fine-tuning. — [AESOP](https://proceedings.aesop-planning.eu/index.php/aesopro/article/download/39/32)
- **Context the models miss:** Waka Lagos stresses that vendors and pavement quality are not well captured by GSV/AI walkability models. — [MIT DUSP](https://dusp.mit.edu/node/1297)

### Inferences
- Expect "obstacle" and "missing curb / no sidewalk" classes to degrade most when US/EU models are used in Beirut. Curb ramps and generic objects (cars, people) transfer better, because localisation is robust and classification is biased.
- Off-the-shelf detectors (COCO/Cityscapes YOLO, Mask2Former) can find cars and people. The Beirut-specific step is deciding *whether the object is on the sidewalk and blocks clear width*. That needs sidewalk-polygon segmentation fine-tuned locally, plus geometric reasoning.
- Plausible minimum local fine-tuning set, inferred from SPGG and Columbus: thousands of labeled crops per class. Columbus had about 29k crops and benefited from pooling. LoRA results suggest a few hundred to a few thousand annotated instances can lift open-vocabulary detectors substantially.

### Gaps
- No study reported mIoU drops for the "sidewalk" class specifically when moving from Cityscapes or Mapillary to MENA cities.
- The GeoNet USA-to-India numbers were not retrieved.
- No MENA fine-tuning study was found.

## Q4. Participatory / crowdsourced approaches: throughput and data quality

### Takeaway
Remote crowdsourcing on street view is cheap and fast in absolute terms (tens to hundreds of km per city with a few hundred volunteers). But quality depends on local knowledge, label-set localisation and validation. Partner NGOs (Liga Peatonal) and paper forms helped reach non-digital users. Mapillary/HOT campaigns generate imagery at scale, but documented sidewalk-specific outputs in the Global South are scarce.

### Cited Findings
- **Washington DC pilot:** users virtually audited 3,000+ miles and placed 255,000+ labels "with 92% accuracy". — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- **Azcapotzalco throughput:** 222 users covered 80.2 km and placed 5,864 labels, about 26 users per 10 km. — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- **Project Sidewalk scale:** 700,000+ image labels and 400,000 validations across 10 cities by 2022. — [Duan et al. 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **Remote users lack local knowledge.** "Users in Europe audit sidewalks in Azcapotzalco… may lack local knowledge and cultural awareness." Liga Peatonal asked for paper audit forms for members without technology access. — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- **Dependence on Google Street View.** Project Sidewalk depends on GSV, which notably lacks coverage in northern and central Africa and large parts of Asia. Recency and frequency of capture may be biased by socio-economic factors. — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- **Validated labels did not uniformly improve models.** Crowd validations are noisy, which argues for annotator training and user-reputation weighting. — [Duan et al. 2022](https://makeabilitylab.cs.washington.edu/media/publications/Duan_ScalingCrowdAiSidewalkAccessibilityAssessmentsInitialExperimentsExaminingLabelQualityAndCrossCityTrainingOnPerformance_ASSETS222022.pdf)
- **VLM-guided crowdsourcing (Chandigarh):** a VLM pre-screens segments and guides annotators, while humans label. Guidance was rated high on relevance (4.97/5) but lower and less consistently on accuracy (4.40/5, weak κ). Segments were kept only if at least 75% overlapped GSV coverage. — [arXiv 2602.09216](https://arxiv.org/html/2602.09216v1)
- **HOT plus Mapillary #map2020:** 28 groups uploaded 550,000+ images and made 3,230 OSM changesets. Project of the year was SIGenBici in Medellín (190 changesets from Mapillary imagery). Sidewalk-specific output is not reported. — [Mapillary blog](https://blog.mapillary.com/update/2020/06/16/map2020-results.html)
- **OSM pedestrian data:** often neglected because of satellite-imagery limits and lack of commercial incentive (State of the Map 2021 talk covering 5 cities incl. Stone Town). — [SotM 2021](https://app.media.ccc.de/v/sotm2021-10029-openstreetmap-and-the-neglected-pedestrian)
- **Organised pedestrian-mapping activities** (e.g., Meta Walkabout using Mapillary) are mostly in US cities. — [OSM Wiki](https://wiki.openstreetmap.org/wiki/Organised_Editing/Activities/Meta/Pedestrian_Mapping)
- **Lebanon participatory precedents:** about 60 stakeholders in the AUB Community Streets workshop. — [Dar/Sevtsuk report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf). Also the UCL Ras El Nabaa resident and shop-owner consultation. — [UCL Discovery](https://discovery.ucl.ac.uk/id/eprint/10211185/1/EN-%20Ras%20El%20Nabaa%20Report.pdf)
- **Low-cost pedestrian capture:** a chest-mounted smartphone (SideSeeing) yielded about 12 km and about 326k frames with IMU and GPS. — [arXiv 2407.06464](https://ar5iv.labs.arxiv.org/html/2407.06464)

### Inferences
- For Beirut: (1) partner with a local NGO and universities (AUB, LAU, USJ, LU) for student mapathons, using a Beirut-tagged label set; (2) have local students capture imagery on foot with phones and upload to Mapillary, including occupation at different times of day; (3) prioritise a local-validator stage over remote volunteers.
- Since GSV is limited in Beirut, Project Sidewalk would need its imagery back-end switched to Mapillary or Panoramax. The authors say their techniques "should work with any streetscape imagery dataset", but no Mapillary deployment was documented.

### Gaps
- No per-hour labeling throughput or cost per km figures were found for Project Sidewalk or Mapillary campaigns.
- No Mapillary or HOT sidewalk campaign in Lebanon or MENA was found.
- No published Project Sidewalk deployment in a MENA city was found.

## Q5. Indicators and indices for summarising sidewalk quality that suit Lebanon's policy context

### Takeaway
The most policy-ready indicators found are simple, image-measurable ones:
- Share of streets with no sidewalk.
- Share of sidewalks with permanent obstructions.
- Share of sidewalks narrower than 1.2 m.
- Labels or obstacles per 100 m, with 1-5 severity.

Beirut already has baselines for the first three from MIT-AUB (6%, ~17%, ~20%). Composite indices (Global Walkability Index, ITDP Pedestrians First, PLOS) exist but need field data.

### Cited Findings
- **Beirut baseline indicators:** % of streets with no sidewalk (6%), % of sidewalks with permanent obstructions (~17%), % of sidewalks below 1.2 m comfortable passing width (~20%). — [Dar/Sevtsuk report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)
- **"Perceived length" model indicators:** Beirut's UNA model converts sidewalk width, traffic volume and speed, and amenities into perceived route length, a single unit usable in accessibility and flow analysis. — [Dar/Sevtsuk report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)
- **Labels per 100 m and severity (Project Sidewalk):** e.g., obstacles per 100 m (Azcapotzalco 1.8 vs US 0.3-1.2) and mean severity on a 1-5 scale. — [arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)
- **Segment access score (Chandigarh):** segment scores are aggregated to POI accessibility within a 1 km walkable buffer, on 60-80 m grid cells. — [arXiv 2602.09216](https://arxiv.org/html/2602.09216v1)
- **Global Walkability Index (Krambeck, World Bank / MIT 2006):** designed for developing-country pedestrian issues; includes "Are there walking obstructions?". Field-tested in Beijing, Hanoi, Bangkok, Manila and Karachi, with a pilot in Ahmedabad. Used in Tehran (score 54, moderate). — [MIT News](https://news.mit.edu/2006/walkability); [MIT DSpace](https://dspace.mit.edu/handle/1721.1/34409)
- **ITDP Pedestrians First (2018):** 11 indicators including crossings, block size (block density), shade and driveway density. — [ITDP Indonesia](https://itdp-indonesia.org/2018/10/pedestrians-first-a-new-tool-for-walkable-cities/); [Eco-Business](https://www.eco-business.com/news/how-walkable-is-your-city-tool-aims-to-make-pedestrians-safer-and-happier/)
- **Image-derived walkability scores:** Kolkata (Mapillary) used a 0-1 score from greenery, openness, pavement and crowdedness. — [ISPRS Annals 2025](https://isprs-annals.copernicus.org/articles/X-5-W2-2025/209/2025/)
- **Obstruction-to-sidewalk ratio:** a Segment Anything Model approach on construction-site imagery computes obstruction-to-sidewalk area ratios, which is close to an "occupation share" metric. — [search summary of Environment and Planning B / preprints](https://www.preprints.org/manuscript/202605.0233) (not verified in full text)
- **Width as a candidate segment attribute:** median segment widths of 2.58 m (NYC), 2.64 m (São Paulo) and 2.28 m (Nairobi), but unvalidated. — [arXiv 2603.22531](https://arxiv.org/pdf/2603.22531)
- **Enforcement-oriented metrics:** Athens counted violations by type (sidewalk parking 2,119 of 5,270 in 12 days). — [Proto Thema](https://en.protothema.gr/2025/01/31/athens-municipality-recorded-5270-traffic-violations-in-the-city-center-over-12-days/). The Bombay High Court urged a hawker repeat-offender database and called a clear footpath a fundamental right. — [Free Press Journal](https://www.freepressjournal.in/amp/mumbai/bombay-hc-slams-bmc-for-illegal-hawkers-urges-database-and-swift-action-on-footpath-encroachment)
- **Enforcement fatigue:** Mumbai is short of 36 inspectors and 125 labourers, and Pune hawkers return within days of drives. This argues for repeat monitoring. — [Free Press Journal (Mumbai)](https://www.freepressjournal.in/amp/mumbai/bombay-hc-slams-bmc-for-illegal-hawkers-urges-database-and-swift-action-on-footpath-encroachment); [Free Press Journal (Pune)](https://www.freepressjournal.in/pune/footpaths-in-pune-blocked-by-hawkers-and-parked-vehicles-causing-major-hassles-for-pedestrians)
- **What Beirut pedestrians care about:** sidewalk *blockage* (not width) significantly affected satisfaction around AUB. — [Said & Abou-Zeid 2015](https://www.aub.edu.lb/Neighborhood/Documents/mahersaid-mayaabouzeid2015.pdf)

### Inferences
- Recommended core set for Lebanon, mapped to municipal enforcement:
  1. Sidewalk presence (% of street length).
  2. Effective clear width (m, after subtracting permanent obstructions), and % below 1.2 m. Optionally also below 1.5 m and 2.0 m.
  3. Permanent obstructions per 100 m (poles, trees, meters, kiosks, private planters or bollards).
  4. Temporary occupation per 100 m by type (parked car or motorbike, vendor, café tables, shop goods, generator, construction), with time-of-day repeat surveys.
  5. Curb and continuity (missing curb, curb level with road, steps or ramps into buildings).
  6. Severity 1-5, as in Project Sidewalk.
  These can roll up into a segment-level score and a PLOS-style A-F grade.
- Splitting *permanent* (infrastructure or design) from *temporary* (enforcement) occupation matches the Beirut municipality's encroachment-removal and fines instruments. It also mirrors the Athens violation-type counts.
- Because blockage, not width, drove satisfaction in Beirut, obstruction and occupation density should be weighted more heavily than nominal width in any composite index.

### Gaps
- No HCM/PLOS effective-width application in a MENA city with image-derived inputs was found.
- No published cost per km for imagery-based vs field audits in comparable cities was found. Project Sidewalk only states it is "far more scalable and inexpensive" than on-the-ground audits ([arXiv 2207.13626](https://arxiv.org/pdf/2207.13626)). UrbanVGGT GSV API costs were self-funded and not quantified ([arXiv 2603.22531](https://arxiv.org/pdf/2603.22531)).
- No full indicator list or obstruction scoring rules for the Global Walkability Index were retrieved.
