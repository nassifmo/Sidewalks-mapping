# Existing datasets on sidewalk geometry, dimensions and obstructions in Lebanon

Research date: 2026-11-06. Scope: Lebanon, with emphasis on Beirut, Tripoli, Saida, Jounieh, Zahle and Tyre.

Main finding: no public, citywide sidewalk dataset (polygons or centrelines with width, kerb height or condition) was found for any Lebanese city. The best existing material is:
- (a) a 2010 curbline layer for Municipal Beirut held by AUB;
- (b) a per-street estimate of sidewalk presence, width and obstruction for parts of Beirut, from MIT and AUB (2022-2023), based on Mapillary imagery;
- (c) building and open-space damage surveys made after the 2020 blast;
- (d) very sparse OpenStreetMap tagging.

---

## Q1. What is the actual sidewalk coverage in OpenStreetMap for Lebanon, and who maps it?

### Takeaway
Sidewalk data in OSM for Lebanon is close to non-existent:
- only 32 ways are tagged `footway=sidewalk` nationwide;
- only 211 of about 112,000 drivable road ways carry any `sidewalk*` tag, and most of those say "no";
- there is no `width` on any sidewalk way, and only 2 kerb nodes.

OSM gives a usable road centreline network, but for this project it is effectively a blank sheet. Mapping in Lebanon is driven by humanitarian activations (HOT) and a handful of individual mappers.

### Cited Findings

**National counts.** These come from my own Overpass API query against the Lebanon admin area (`area["ISO3166-1"="LB"][admin_level=2]`), run 2026-11-06 with OSM data timestamp 2026-11-06T07:51Z. Source: [Overpass API](https://overpass-api.de/api/interpreter).

| OSM feature (Lebanon, whole country) | Count |
|---|---|
| `way[footway=sidewalk]` (separately mapped sidewalks) | **32** |
| `way[footway=sidewalk][width]` | **0** |
| `way[~"sidewalk:width"]` | **0** |
| `way[highway=footway]` (all footways) | 1,956 |
| Drivable road ways (`highway` = trunk/primary/secondary/tertiary/residential/unclassified/living_street) | 111,794 |
| Road ways with any `sidewalk*` key | 211 (about 0.19% of road ways) |
| ...of which `sidewalk:both=no` / `sidewalk=no` | 114 / 52 |
| ...of which positive (`sidewalk=both/left/right/separate`, `sidewalk:*=yes`) | about 45 |
| `sidewalk:*:surface` tags | 2 (both `paving_stones`) |
| `way[highway][width]` (any highway with width) | 45 |
| `node[kerb]` / `way[kerb]` | **2 / 4** |
| `node[highway=crossing]` | 339 |
| `way[footway=crossing]` | 123 |
| `node[highway=street_lamp]` | 284 |
| `node[amenity=bench]` | 27 |
| `node[amenity=waste_basket]` | 29 |
| `node[barrier=bollard]` | 10 |
| `node[natural=tree]` | 4,698 (mostly orchards/rural, not street trees, by inference) |
| `way[smoothness]` | 257 |
| `way[highway=footway][wheelchair]` | 9 |

**City counts.** These are approximate rectangular bounding boxes around each city core, not municipal boundaries, from the same Overpass run ([Overpass API](https://overpass-api.de/api/interpreter)). Roads include `service`.

| City (bbox) | Road ways | Road ways with `sidewalk*` tag | `footway=sidewalk` | `highway=footway` | Crossing nodes |
|---|---|---|---|---|---|
| Beirut (33.862,35.465–33.910,35.545) | 5,417 | 3 | 8 | 378 | 181 |
| Tripoli (34.40,35.80–34.47,35.87) | 2,121 | 3 | 2 | 32 | 1 |
| Saida (33.54,35.35–33.585,35.40) | 1,210 | 1 | 15 | 251 | 3 |
| Jounieh (33.955,35.60–34.00,35.66) | 1,512 | 17 | 0 | 30 | 0 |
| Zahle (33.83,35.88–33.87,35.93) | 1,260 | 0 | 0 | 4 | 0 |
| Tyre (33.255,35.185–33.29,35.23) | 565 | 0 | 0 | 65 | 1 |

**Who edits sidewalks.** The 32 `footway=sidewalk` ways were last edited by about 10 different accounts:
- CherryMonster (10 ways), Peter Maris (4), ChaireMobiliteGeorgio (3), StephanyGA (2), lunakhayat (2), and others with 1 each;
- last-edit years run from 2017 to 2026, with 9 edits in 2026.

This points to scattered individual efforts, not an organised campaign ([Overpass API](https://overpass-api.de/api/interpreter), `out meta` query).

**Humanitarian mapping.** The OSM wiki has an activation page, "Lebanon: Conflict – October 2024", which documents organised HOT-style mapping during the 2024 war. That kind of activation usually targets buildings and roads, not pedestrian detail ([OSM Wiki](https://wiki.openstreetmap.org/wiki/ES:Lebanon:_Conflict_-_October_2024)).

**OSM exports on HDX.** HOT publishes regular OpenStreetMap exports for Lebanon on HDX (e.g. `hotosm_lbn_sea_ports`, `hotosm_lbn_waterways`). A "Lebanon Roads (OpenStreetMap Export)" is also listed on the ReliefWeb Lebanon data page in 2026. Sources: [HDX Sea Ports](https://data.humdata.org/m/dataset/hotosm_lbn_sea_ports), [Waterways mirror](https://cloud.csiss.gmu.edu/uddi/dataset/hotosm_lbn_waterways), [ReliefWeb Lebanon data](https://response.reliefweb.int/lebanon/data).

**WFP road extracts.** WFP published OSM-derived extracts split into "Lebanon Road Network (main roads)" and "Lebanon streets and pathways" ([AmeriGEOSS main roads](https://data.amerigeoss.org/dataset/lebanon-road-network-main-roads), [AmeriGEOSS streets and pathways](https://data.amerigeoss.org/dataset/lebanon-streets-and-pathways)).

**OSM as a base network.** The MIT/AUB "Community Streets" team built its Beirut pedestrian network from OSM road centrelines. Wide arterials were turned into two parallel sidewalk segments joined by crosswalks, and footbridges were added by hand. So OSM supplies topology but no sidewalk geometry ([Sevtsuk, Community Streets report, Dar Urban Research Seed Fund, 2023](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)).

**Query used** (national; each statement is followed by `out count;`):

```
[out:json][timeout:300];
area["ISO3166-1"="LB"][admin_level=2]->.lb;
way[footway=sidewalk](area.lb); out count;
way[highway][~"^sidewalk"~"."](area.lb); out tags;   // tag value tally
...
```

### Inferences
- About 0.03% of road ways (32 of 111,794) have a separately mapped sidewalk. Any OSM-based sidewalk layer for Lebanon would have to be made almost from scratch.
- The tags that do exist are mostly `sidewalk=no` / `sidewalk:both=no`. They look like the work of a few mappers recording missing sidewalks, possibly in Jounieh (17 tagged ways there).
- The 181 crossing nodes in the Beirut bbox are the only pedestrian element with somewhat meaningful density, and even that is low for a city of more than 5,400 road ways.
- The street furniture counts (284 street lamps and 27 benches nationally) are far below reality. Compare 943 street-light poles in the 2010 AUB/Municipal Beirut layer for Beirut alone (see Q2). OSM street furniture is not a usable obstruction inventory.

### Gaps
- I did not pull taginfo country statistics or the HOT Tasking Manager project list for Lebanon. The Tasking Manager would confirm whether any HOT project ever targeted sidewalks; I found no evidence one did.
- I did not run a contributor analysis for all Lebanon road edits, so I cannot name the main local OSM community (e.g. an "OSM Lebanon" group). I found no source for one.
- The city counts use bounding boxes, not official municipal boundaries, so they are approximate.

---

## Q2. What do Lebanese public bodies hold?

Bodies asked about: Municipality of Beirut, CDR, DGU, Directorate of Geographic Affairs (DGA/DAG), Ministry of Public Works and Transport (MoPWT), Ministry of Interior, Cadastre.

### Takeaway
The only confirmed public-sector layer close to "sidewalk geometry" is a 2010 Municipal Beirut **curbline** layer: 6,805 polylines at 1:2,000. It was digitised by AUB's Faculty of Engineering and Architecture (FEA) and is held in AUB's GIS catalogue. Alongside it are 2010 street-light-pole and 2011 road-centreline layers.

I found no published sidewalk layer from CDR, DGU, MoPWT, the Cadastre or any municipality other than Beirut. Any such data exists only on request and on paper or CAD, if it exists at all. The DGA sells topographic maps; the only series surfaced is historical (1963–74).

### Cited Findings

**AUB Neighborhood Initiative "Ras Beirut & Ain El Mreisseh GIS Basemap Catalog" (21 March 2014).** It lists:
- **Roads Curblines**: polyline; coverage "Municipal Beirut"; 6,805 features; original scale 1/2,000; Local Stereographic projection; source and updater "AUB – FEA"; updated 2010; no attributes beyond OBJECTID.
- **Street Light Poles**: points; Municipal Beirut; 943 features; 1/1,000; source "Team International"; updated by AUB, 2010.
- **Roads Centerlines**: neighbourhood study area only; 1,474 features; 1/2,000; source "GIS Transport", 2011. Attributes are ROAD_USAGE (paved/unpaved), CLASS, ONE_WAY and Roads_Name.

The catalogue says the data are "made available for academic and research purposes" and warns that accuracy varies because some layers are student work. Several base layers are attributed to "Municipal Beirut" ([AUB ScholarWorks bitstream](https://scholarworks.aub.edu.lb/server/api/core/bitstreams/71b5ddf4-a555-4cf2-a70c-4bf0fc19da4a/content); also referenced at [AUB ScholarWorks 10938/10283](https://scholarworks.aub.edu.lb/handle/10938/10283?show=full)).

**Other AUB GIS records.** An AUB ScholarWorks GIS roads record has a licence restricted to AUB-affiliated members, so it is not public ([AUB ScholarWorks 10938/23907](https://scholarworks.aub.edu.lb/handle/10938/23907?show=full)).

**Municipality of Beirut and the 2020 blast.** With UN-Habitat support, the municipality ran a rapid **building-level** damage assessment after the 4 Aug 2020 blast. It was an exterior visual survey within 2 km of the port with five damage categories, and GIS/IM work was done by UN-Habitat Lebanon. Buildings were the unit of survey, not streets or sidewalks ([UN-Habitat / Municipality of Beirut rapid assessment report, Oct 2020](https://unhabitat.org/sites/default/files/2020/10/municipality_of_beirut_-_beirut_explosion_rapid_assessment_report.pdf); [UN-Habitat project page](https://unhabitat.org/beirut-port-explosions-response-beirut-municipality-rapid-building-level-damage-assessment)).

**UN-Habitat GIS support.** UN-Habitat placed staff in the Beirut and Bourj Hammoud municipalities and digitised building damage data with a mobile app and the Geopal platform ([UN-Habitat news, Aug 2020](https://unhabitat.org/news/12-aug-2020/un-habitat-responds-immediately-to-support-families-following-explosions-in); [UN-Habitat six-months-on, Feb 2021](https://unhabitat.org/news/23-feb-2021/beirut-explosion-six-months-on-un-habitats-response-and-what-lies-ahead)).

**Directorate of Geographic Affairs (DAG/DGA).** DAG is Lebanon's national mapping agency, set up in 1962. East View Geospatial resells a historical DAG 1:20,000 topographic series (1963–1974, 121 sheets) ([East View Geospatial – Lebanon country profile](https://geospatial.com/country_profiles/lebanon/)). In 2023 the directorate was launching a 13-station online geodetic (CORS-type) network, which is useful for survey-grade GNSS fieldwork ([LBCI, 2023](https://www.lbcgroup.tv/news/lebanon-news/691386/lebanese-army-launches-online-network-to-facilitate-geographical-surve/en)).

**Solidere and the Beirut Central District.** Solidere's Urban Management Department prepared the UN design manual for a barrier-free environment, which sets sidewalk, ramp and kerb standards. The search summary dated it 2010; I could not verify the date ([UN DESA Enable – design manual](https://www.un.org/esa/socdev/enable/designm/); [preface](https://static.un.org/esa/socdev/enable/designm/preface.htm)). Solidere's own BCD as-built infrastructure GIS/CAD is not public. I found no source describing it.

**Accessibility standards.** The Lebanese Union for People with Physical Disabilities (LUPD) has been working with the Lebanese Standards Institution (LIBNOR) on accessibility specifications for public roads and sidewalks. Progress is reportedly slow because of an "overlap of powers". Law 220/2000 is the disability-access law (it appears as "2002" in some sources) ([Mashallah News, "Beware of sidewalks"](https://mashallahnews.com/beware-of-sidewalks/); attribution came via a search summary, so treat it as moderate confidence).

### Inferences
- The 2010 curbline layer is the most valuable "cheap" public-origin dataset. Curblines give the road-sidewalk edge. Combined with building footprints or parcel lines, they let you estimate sidewalk width across all of Municipal Beirut.
  - It is 16 years old and pre-dates the 2020 blast and later street works.
  - Access is "academic and research purposes", so it would need to be requested through AUB (Neighborhood Initiative or Beirut Urban Lab). Redistribution rights are unclear.
- Municipal engineering departments (Beirut, Tripoli, Saida, Jounieh, Zahle, Tyre) and CDR probably hold CAD as-built drawings for specific street rehabilitation projects. I found no public evidence of this, so it is a lead to pursue by direct request, not a confirmed dataset.

### Gaps
- **CDR, DGU, MoPWT, Ministry of Interior/municipal GIS, Cadastre:** no source found describing a sidewalk, curb or street furniture layer. Their holdings (cadastral parcels, road projects, as-builts) are undocumented online.
- **DGA orthophotos:** I found no current product list, price or licence terms for recent orthophotos. Only the historical 1:20,000 topo series (1963–74) was confirmed.
- **Other cities:** no confirmed municipal GIS for Tripoli, Saida, Jounieh, Zahle or Tyre in my sources.
- **Beirut municipality today:** I did not verify whether it maintains an up-to-date GIS today, or whether the "Municipal Beirut" layers in the AUB catalogue came from a municipal GIS unit.

---

## Q3. Academic and NGO work

Sources asked about: AUB Beirut Urban Lab, AUB Neighborhood Initiative, USJ, LAU, ALBA, Public Works Studio, walkability audits, LUPD, and post-blast assessments.

### Takeaway
The strongest dataset is the MIT City Form Lab and AUB "Community Streets" street-level estimate for central and blast-affected Beirut (2022–2023). It records per street:
- sidewalk presence, width and quality, estimated from Mapillary imagery and field checks;
- pedestrian counts;
- a calibrated pedestrian-flow model.

It is not published as open data.

The Beirut Urban Lab's Beirut Built Environment Database (BBED) and Beirut Urban Observatory hold building and damage layers, not sidewalks. Smaller audits exist for Hamra, Jeanne d'Arc Street, Ras El Nabaa, Geitawi and Karm el Zeitoun, mostly as PDF reports.

### Cited Findings

**MIT/AUB "Community Streets" (Dar Urban Research Seed Fund report, c. 2023).** Authors are Andres Sevtsuk (MIT) and team with AUB co-authors (Maya Abou-Zeid and others).
- **Method:** "For each street, the research team approximated sidewalk presence, width, and quality based on open street-view imagery analysis from Mapillary (Google Street View is very limited in Beirut), prior studies, and in-person observation."
- **Results:** 6% of streets had no sidewalk; about 17% of existing sidewalks had permanent obstructions; about 20% of sidewalks were narrower than 1.2 m.
- **Study area:** the blast-affected neighbourhoods of Karantina, Mar Mikhael, Gemmayzeh and Rmeil (Jeitaoui in the scenarios), expanded to include Hamra and Raouché.
- **Pedestrian counts:** weekday 4:30–5:30 pm counts ranged from 7 to 416 per hour, average 69.8, highest in Hamra.
- **Other inputs:** building footprints came from the Beirut Urban Lab, which assembled them after the blast. Land uses came from local studies, OSM, Google Places, video analysis and field visits.

Source: [Community Streets report PDF](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf); also [Sidara Collaborative – Community Streets](https://sidaracollaborative.com/Insights/Community-Streets), [MIT LCAU](https://lcau.mit.edu/node/80), [Venice 2023 exhibition catalogue](https://media.voog.com/0000/0036/2451/files/BeirutCommunityStreets_catalog_Venice2023.pdf).

**MIT DUSP working paper "Walkability and Pedestrian Conditions in Beirut" (21 Oct 2022).** Authors are Sevtsuk, Basu, Chancey, Kollar and Pratama (MIT) with Haddad, Halabi, Makhlouf and Abou-Zeid (AUB). It uses a "comprehensive survey of street networks" to model peak-hour pedestrian flows on all streets. It is hosted on Dropbox, and the data is not stated as public ([MIT DUSP news](https://dusp.mit.edu/news/increasing-sidewalk-accessibility)).

**Press coverage of the same study.** L'Orient Today reported that about 6% of street length in the study area had no sidewalk and 18% had sidewalks with permanent obstructions (streetlights, signposts, trees, parking meters). It also reported about 25 cars parked on the 315 m sidewalk of Salah Labaki Street, Al Hikmeh ([L'Orient Today, "Sidewalk struggles"](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html); content via search snippet, page returned 403 on fetch).
- Note the slight discrepancy: the report gives 17% of *sidewalks*, the press gives 18% of *street length*. The bases differ.

**Hamra street redesign study.** A natural-experiment study of a Hamra street redesign (wider sidewalk, parking lane removed, raised junctions) found mainly safer pedestrian movement and a better walking experience, not more foot traffic ([TRID record](https://trid.trb.org/view/1714144)).

**AUB walking-environment study (2015).** Said, Abou-Zeid and Kaysi modelled satisfaction with the walking environment around AUB. Key attributes were ease of crossing, sidewalk blockage and sidewalk cleanliness. Data came from a survey of pedestrians, not a geometric inventory ([AUB PDF](https://www.aub.edu.lb/Neighborhood/Documents/mahersaid-mayaabouzeid2015.pdf); [AUB ScholarWorks](https://scholarworks.aub.edu.lb/items/ed447a0d-b1be-40ae-a4ee-0623f638d59f); [TRID](https://trid.trb.org/view/1416010)).

**AUB theses on Hamra.**
- Dana Balaa (2014) found that many Hamra streets, alleys and open spaces are blocked to pedestrians by infrastructure, walls and parking ([AUB ScholarWorks 10938/10036](https://scholarworks.aub.edu.lb/handle/10938/10036)).
- Related theses: "Enhancing walkability through urban connectivity: the case of Hamra" ([link](https://scholarworks.aub.edu.lb/items/1d00c3e1-e0d1-41b2-8793-7ebd3076a8b1/full)) and "...through open spaces" ([link](https://scholarworks.aub.edu.lb/items/066298fa-97eb-44cc-99e9-340044fb2e70/full)).

**Jeanne d'Arc Street.** The "Improving Walkability in Beirut: Lessons from the Jeanne d'Arc Street Case" report (Daleel Madani) covers sidewalk conditions and design workshops, including wheelchair users ([PDF](https://daleel-madani.org/sites/default/files/Resources/6.Improving_Walkability_Beirut_Lessons_from_Jeanne_dArc_Street%5B1%5D.pdf); [page](https://daleel-madani.org/node/103777)).

**Ras El Nabaa citizen consultation (UCL, 2024, amended 2025).** A participatory report on Toufic Salem Street with recommendations to the municipality ([UCL Discovery PDF](https://discovery.ucl.ac.uk/id/eprint/10211185/1/EN-%20Ras%20El%20Nabaa%20Report.pdf)).

**UCL public-space study (2023).** Dabaj, Maassarani, Rigon and Conti, "Rebuilding communities through public space interventions", covers post-blast Beirut ([UCL Discovery PDF](https://discovery.ucl.ac.uk/10189523/7/Dabaj_Maassarani_Rigon_Conti_2023_Rebuilding_communities_through_public_space_interventionsRED.pdf)).

**Dar "Beirut Open Space Damage Report" (Sept 2020).** GIS work was by Kanj Madi and Assem Daaboul. It covers post-blast damage and pre-blast conditions of open space, and records problems such as total absence of sidewalks and informal parking on sidewalks ([Dar PDF](https://dar.com/Content/Publications/PUD/Beirut-Open%20space%20damage%20report.pdf); the file is over 10 MB and I could not fetch it, so details come from the search summary).

**ACTED / REACH "urban snapshots" (June 2021).** Area-based profiles of Geitawi and Karm el Zeitoun (post-blast), which typically include street and public-space conditions ([Geitawi PDF](https://www.acted.org/wp-content/uploads/2021/08/urban-snapshot-geitawi-2021-06-02-final.pdf); [Karm el Zeitoun PDF](https://www.acted.org/wp-content/uploads/2021/08/urban-snapshot-karm-el-zeitoun-2021-06-02-final-1.pdf)).

**Beirut Urban Lab platforms.**
- The **Beirut Built Environment Database (BBED)** gathers geolocated social, environmental and economic data on building activity in Greater Beirut ([civictech.guide](https://directory.civictech.guide/listing/beirut-built-environment-database)).
- The **Beirut Urban Observatory** launched in Aug 2021 on ArcGIS Hub and builds on BBED. It includes Order of Engineers and Architects (OEA) damage assessments and BBED baseline layers ([civictech.guide](https://civictech.guide/listing/beirut-urban-observatory)).
- A Dateno registry entry lists an AUB-owned ArcGIS Hub "Beirut Urban Observatory (old)" with open access ([Dateno](https://dateno.io/registry/catalog/cdi00003253)).
- AUB also runs an ArcGIS Server, ICIL GIS, with historical and atlas layers ([icilgis.aub.edu.lb](https://icilgis.aub.edu.lb/server/rest/services/Atlas_Land_AOI_In_Time/MapServer)).
- No sidewalk layer is listed in any of these sources.

**Beirut Arab University.** A BAU pilot on women's health and neighbourhood walkability (50-person survey) exists ([BAU Digital Commons](https://digitalcommons.bau.edu.lb/hwbjournal/vol1/iss3/10)).

**Abandoned pedestrian plan.** A 2013 French-funded plan for pedestrian corridors in Beirut was reportedly never implemented ([L'Orient Today](https://today.lorientlejour.com/article/1312987/sidewalk-struggles-beirut-streets-pose-challenge-to-pedestrians.html), via search snippet).

### Inferences
- The MIT/AUB per-street attribute table is the closest thing to a sidewalk inventory: presence, approximate width class, quality and obstruction flag per street segment, for central and eastern Beirut. It may be obtainable by request from MIT City Form Lab / AUB (Abou-Zeid). Its licence is unknown.
- Mapillary is the proven imagery source for Beirut sidewalk assessment. Google Street View coverage is limited.
- BBED/Observatory building footprints plus the 2010 curblines could produce sidewalk-width estimates for Municipal Beirut cheaply.

### Gaps
- **Public Works Studio, USJ, LAU, ALBA:** I found no sidewalk datasets. Public Works Studio focuses on housing, land and public-space policy, but that comes from my background knowledge; I found no source for it here.
- **LUPD accessibility audits:** no published street or sidewalk audit dataset found.
- **AUB Beirut Urban Lab:** no sidewalk or street-furniture layer found. I could not get the current Observatory layer list.
- **Order of Engineers and World Bank RDNA:** I did not confirm whether the OEA blast assessments or the World Bank RDNA (2020) recorded street, sidewalk or kerb damage.
- **Exact study-area extent:** the street-km of the MIT/AUB survey is not stated in what I could read.

---

## Q4. International sources

Sources asked about: UN-Habitat, World Bank, ITDP/WRI, Overture, Microsoft/Google open data, HDX.

### Takeaway
International sources give context and base layers (OSM exports, building damage, neighbourhood profiles), but none publishes a sidewalk inventory for Lebanon.
- UN-Habitat/UNICEF neighbourhood profiles exist for Tripoli, Saida and Tyre, but their sidewalk content is unverified.
- The World Bank Greater Beirut Public Transport Project (BRT) closed in 2023. Its pedestrian material is mainly footbridge design in the ESIA.

### Cited Findings

**UN-Habitat/UNICEF neighbourhood profiles.**
- Joint profiling covered municipalities including Baalbek, Beirut, Tripoli, Saida and Sour/Tyre ([UN-Habitat news, Apr 2021](https://unhabitat.org/news/15-apr-2021/joint-profiling-work-by-un-habitat-and-unicef-informs-evidence-based-urban); [UN Lebanon press release](https://lebanon.un.org/sites/default/files/2021-05/ENG-PR.pdf)).
- Published profiles include:
  - Old Saida (Dec 2019; 0.18 km²) ([PDF](https://unhabitat.org/sites/default/files/2020/11/un-habitat-unicef_old_saida_neighbourhood_profile.pdf));
  - Tabbaneh, Tripoli (Aug 2018) ([UN-Habitat](https://unhabitat.org/tabbaneh-neighbourhood-profile-2018-tripoli-lebanon); [UNHCR](https://data.unhcr.org/en/documents/details/66267));
  - Maachouk, Tyre ([UNHCR](https://data.unhcr.org/fr/documents/details/59498));
  - a Tyre city profile ([ALNAP](https://alnap.org/help-library/resources/tyre-city-profile/)).
- These typically include area-level maps and infrastructure sections. I did not verify street-by-street sidewalk mapping in them.

**UN-Habitat Japan-funded blast recovery (2023 brochure).** Interventions included improving pedestrian accessibility by removing obstructions and enhancing sidewalks ([UN-Habitat brochure](https://new.unhabitat.org/sites/default/files/2023/01/japan_brochure_3_digital.pdf)). The project-level designs and drawings are not public.

**UNDP "Building Lebanon Forward: Inclusive and Accessible".** Aimed at accessible reconstruction of blast-affected areas; it cites an estimate that 10–15% of Lebanon's population has a disability ([UNDP Lebanon](https://www.undp.org/lebanon/building-lebanon-forward-inclusive-and-accessible)).

**World Bank Greater Beirut Public Transport Project (P160224).**
- US$295M; Category A safeguards; closing date 31 Dec 2023 ([World Bank project page](https://projects.worldbank.org/P160224?lang=en)).
- The ESIA for the Tabarja–Beirut BRT describes stations reached by pedestrian bridges with stairs and elevators, about every 1 km ([ESIA PDF via Rights in Development EWS](https://ewsdata.rightsindevelopment.org/files/documents/24/WB-P160224_dLl8Rsm.pdf); [World Bank press release, Mar 2018](https://www.worldbank.org/en/news/press-release/2018/03/15/world-bank-supports-lebanons-public-transport-to-improve-mobility-spur-growth)).
- I found no sidewalk survey published from this project.

**UNOSAT damage assessment (2024 conflict).** UNOSAT runs a "UNOSAT_CCD_Lebanon" ArcGIS MapServer of comprehensive damage assessment layers. These are building and structure damage, useful for south Lebanon and Tyre areas ([UNOSAT REST services](https://unosatgis.cern.ch/h/rest/services/CE20240621LBN/UNOSAT_CCD_Lebanon/MapServer/layers)).

**HDX.**
- HOT OSM exports for Lebanon (roads, waterways, sea ports and others) ([HDX](https://data.humdata.org/m/dataset/hotosm_lbn_sea_ports)).
- An HDX "Lebanon: Administrative level 4 (Beirut Neighborhoods) Boundary" dataset ([BTAA Geoportal record](https://geo.btaa.org/catalog/817f63dc-740c-4ab8-8929-f886af76e559)).
- Roads, Lebanon, 2012 (Stanford-held) ([UWM GeoDiscovery](https://geodiscovery.uwm.edu/catalog/stanford-nc560zt6820)).
- None contains sidewalks.

**Commercial vector maps.** Vendors such as vectormap.net sell "Urban Plan Beirut" products (CAD/vector, paid). Their content and accuracy are unverified ([vectormap.net](https://vectormap.net/product-tag/urban-plan-beirut-lebanon/)).

### Inferences
- The UN-Habitat neighbourhood profiles (Tabbaneh, El-Qobbeh, Old Saida, Maachouk, and others) are the most likely existing documents with sidewalk or street-condition observations for Tripoli, Saida and Tyre. The format is PDF maps, so the data would need digitising.
- Overture Maps' transportation layer for Lebanon is derived mainly from OSM, so by inference it would show the same near-absence of sidewalk data. This is not verified.

### Gaps
- **Overture Maps, Microsoft/Google open data:** not checked within my budget. Microsoft/Google building footprints and Overture transportation segments in Lebanon are not described here. I found no evidence of any sidewalk-specific open data from these providers for Lebanon.
- **ITDP/WRI:** no Lebanon sidewalk work found in my searches.
- **World Bank RDNA (2020) and the BRT ESIA annexes:** not checked in detail for sidewalk surveys.

---

## Q5. Summary inventory: access, format, date and quality

### Takeaway
Everything with real sidewalk attributes is either restricted (academic or on request) or locked in PDFs. The only open sources (OSM, HDX) have almost no sidewalk content. Cheapest paths:
- request the AUB 2010 curblines and the MIT/AUB per-street sidewalk table;
- reuse Mapillary imagery;
- treat OSM as the base network to be enriched.

### Cited Findings

| # | Dataset | Holder | Content relevant to sidewalks | Coverage | Date | Format | Access | Quality notes |
|---|---|---|---|---|---|---|---|---|
| 1 | OSM sidewalk tags | OSM contributors | 32 `footway=sidewalk` ways; 211 roads with `sidewalk*` tags; 0 widths; 2 kerb nodes ([Overpass](https://overpass-api.de/api/interpreter)) | Lebanon | 2017–2026 edits | OSM/PBF/GeoJSON | Open (ODbL) | Negligible coverage |
| 2 | HOT/WFP OSM road exports | HOT, WFP on HDX/AmeriGEOSS ([HDX](https://data.humdata.org/m/dataset/hotosm_lbn_sea_ports), [WFP](https://data.amerigeoss.org/dataset/lebanon-streets-and-pathways)) | Road centrelines only | Lebanon | Recurring | SHP/GeoJSON/GPKG | Open | Base network only |
| 3 | Roads Curblines | AUB FEA / AUB Neighborhood Initiative; Municipal Beirut coverage ([AUB catalogue](https://scholarworks.aub.edu.lb/server/api/core/bitstreams/71b5ddf4-a555-4cf2-a70c-4bf0fc19da4a/content)) | 6,805 curbline polylines, 1:2,000 | Municipal Beirut | 2010 | Vector (likely SHP/GDB), Local Stereographic | Academic/research use; on request | Old; no attributes; pre-blast |
| 4 | Street Light Poles | Team International / AUB (same catalogue) | 943 points (potential obstructions) | Municipal Beirut | 2010 | Vector points, 1:1,000 | As above | Old |
| 5 | Roads Centerlines | GIS Transport / AUB (same catalogue) | Paved/unpaved, class, one-way, name; 1,474 features | AUB neighbourhood (Ras Beirut/Ain el Mreisseh) | 2011 | Vector | As above | Local only |
| 6 | Community Streets per-street sidewalk estimates | MIT City Form Lab + AUB ([report](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf), [MIT DUSP](https://dusp.mit.edu/news/increasing-sidewalk-accessibility)) | Sidewalk presence, width, quality, permanent obstructions; pedestrian counts; flow model | Karantina, Mar Mikhael, Gemmayzeh, Rmeil, Jeitaoui, Hamra, Raouché | 2022–2023 | Report PDF; underlying GIS not published | Request from authors | Estimated from Mapillary plus field work, not surveyed widths |
| 7 | BBED / Beirut Urban Observatory | AUB Beirut Urban Lab ([civictech](https://civictech.guide/listing/beirut-urban-observatory), [Dateno](https://dateno.io/registry/catalog/cdi00003253)) | Building footprints, damage (OEA), baseline layers; no sidewalks found | Greater/Municipal Beirut | 2020–2021+ | ArcGIS Hub layers | Listed as open access | Useful for frontage lines |
| 8 | Municipality of Beirut building damage assessment | Municipality + UN-Habitat ([report](https://unhabitat.org/sites/default/files/2020/10/municipality_of_beirut_-_beirut_explosion_rapid_assessment_report.pdf)) | Building-level damage | Within 2 km of port | Aug–Oct 2020 | Report; Geopal GIS | Report public; GIS on request | Not sidewalk-specific |
| 9 | Dar Beirut Open Space Damage Report | Dar Al-Handasah ([PDF](https://dar.com/Content/Publications/PUD/Beirut-Open%20space%20damage%20report.pdf)) | Open-space and street conditions incl. missing sidewalks, sidewalk parking | Blast-affected area | Sep 2020 | PDF maps | Public PDF | Details unverified (file too large to fetch) |
| 10 | ACTED urban snapshots | ACTED/REACH ([Geitawi](https://www.acted.org/wp-content/uploads/2021/08/urban-snapshot-geitawi-2021-06-02-final.pdf)) | Neighbourhood conditions | Geitawi, Karm el Zeitoun | Jun 2021 | PDF | Public | Qualitative |
| 11 | UN-Habitat/UNICEF neighbourhood profiles | UN-Habitat ([Old Saida](https://unhabitat.org/sites/default/files/2020/11/un-habitat-unicef_old_saida_neighbourhood_profile.pdf), [Tabbaneh](https://unhabitat.org/tabbaneh-neighbourhood-profile-2018-tripoli-lebanon)) | Neighbourhood infrastructure (sidewalk content unverified) | Tripoli, Saida, Tyre, Beirut and others | 2018–2021 | PDF | Public | Digitising needed |
| 12 | Ras El Nabaa citizen report | UCL ([PDF](https://discovery.ucl.ac.uk/id/eprint/10211185/1/EN-%20Ras%20El%20Nabaa%20Report.pdf)) | Street-level resident input | Toufic Salem St., Beirut | 2024/2025 | PDF | Public | Qualitative |
| 13 | AUB walking satisfaction study and Hamra theses | AUB ([2015 PDF](https://www.aub.edu.lb/Neighborhood/Documents/mahersaid-mayaabouzeid2015.pdf), [Balaa 2014](https://scholarworks.aub.edu.lb/handle/10938/10036)) | Sidewalk blockage perceptions; blocked-route mapping | Hamra / AUB area | 2014–2015 | PDF (thesis maps) | Public | Old, local |
| 14 | DAG topographic maps | Lebanese Army DAG; resold by East View ([profile](https://geospatial.com/country_profiles/lebanon/)) | Historical 1:20,000 topo | Lebanon (121 sheets) | 1963–1974 | Paper/scanned | Paid | Too coarse and old for sidewalks |
| 15 | UNOSAT CCD Lebanon | UNOSAT ([REST](https://unosatgis.cern.ch/h/rest/services/CE20240621LBN/UNOSAT_CCD_Lebanon/MapServer/layers)) | Structure damage | South Lebanon / conflict areas | 2024 | ArcGIS MapServer | Open view | Not sidewalk-specific |
| 16 | Mapillary street imagery | Mapillary (Meta) (named as the main imagery source by [Community Streets](https://edge.sitecorecloud.io/daralhandas9921-dargroupcor87ce-prod-3847/media/Project/dargroup/dargroup/Insights/Report_Community-Streets_Prof-Sevtsuk.pdf)) | Imagery for desk audits of width and obstructions | Beirut (coverage extent elsewhere unverified) | Various | Images plus API | Open (CC-BY-SA) | Google Street View is limited in Beirut |

### Inferences
- **Beirut:** usable inputs exist (curblines 2010; MIT/AUB street estimates 2022–23; BBED footprints; Mapillary), but all need permission, updating or assembly.
- **Tripoli, Saida, Jounieh, Zahle, Tyre:** effectively no sidewalk data exists beyond OSM fragments and qualitative UN-Habitat profiles. A primary survey would be needed.

### Gaps
- Licence terms for the AUB curblines and the MIT/AUB data are unverified; both need direct enquiry.
- I found nothing on kerb height or sidewalk surface condition anywhere in Lebanon, apart from 2 OSM `sidewalk:*:surface` tags.
