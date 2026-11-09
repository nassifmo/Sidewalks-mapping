# National Scope of Sidewalk Mapping in Lebanon (as of 6 November 2026)

All computed numbers come from scripts and data in `scope_work/` (same folder as this file). Methods are summarised in each section. The full tables are in `scope_work/summary_tables.md`, `scope_work/results_lengths_km.csv` / `results_lengths.json` (Overpass), and `scope_work/mapillary_proxy_table.md`.

**Data sources used for computation**
- HOT/HDX "Roads of Lebanon" export: OSM snapshot of 2026-11-02 with 162,668 features. Each feature carries adm1/adm2/adm3 P-codes (99.96% tagged to adm3). Built from Geofabrik LBN, with fieldmaps.io edge-matched COD boundaries — [HDX dataset](https://data.humdata.org/dataset/hotosm_lbn_roads); [quality report](https://production-raw-data-api.s3.amazonaws.com/ISO3/LBN/roads/hotosm_lbn_roads_report.html)
- Live Overpass API, queried on 2026-11-06 at osm_base 2026-11-06T13:33Z. It uses server-side `make stat n=count(ways), m=sum(length())` per highway class, run on the Lebanon admin_level=2 area, each OSM admin_level=4 governorate area, and circular buffers around city centres — [Overpass API](https://overpass-api.de/api/interpreter); script `scope_work/overpass_stats.py`
- HeiGIT "Lebanon: Road Surface Data". It covers OSM ways up to July 2024 and gives a Mapillary-prediction length per way — [HDX](https://data.humdata.org/dataset/lebanon-road-surface-data)
- WorldPop 2020 1 km UN-adjusted population raster (`lbn_ppp_2020_1km_Aggregated_UNadj.tif`) — [WorldPop data](https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/LBN/lbn_ppp_2020_1km_Aggregated_UNadj.tif)
- Lengths are geodesic: haversine with R = 6,371.0088 km, computed in pure-Python stdlib scripts (`gpkg_lengths.py`, `urban_share.py`, `summarize.py`, `mapillary_proxy.py`).

---

## 1. Lebanon road network length from OSM by highway class, by governorate and by main city

### Takeaway
OSM holds about **47,000–48,500 km** of `highway=*` ways in Lebanon as of November 2026. HeiGIT's count, based on OSM data up to July 2024, was 51,700 km. Of the 2026 total, about **36,200–36,700 km** is "sidewalk-relevant" street centreline: trunk, primary, secondary and tertiary roads, residential and unclassified streets, living streets, and pedestrian streets. Residential streets alone are 20,400 km (about 43%). Mount Lebanon holds about 28% of the sidewalk-relevant network and Beirut only about 470–480 km. Existing sidewalk tagging in OSM is close to zero: about 167 km of roads carry any `sidewalk*` tag and 7.8 km are mapped as `footway=sidewalk`. The plan is effectively greenfield.

### Cited Findings
- HeiGIT/HDX: "Approximately 0.0517 million km of roads are mapped in OSM in this region". In the same dataset, 76.95% of road length has no surface information — [HDX HeiGIT road surface](https://data.humdata.org/dataset/lebanon-road-surface-data). My recomputation of the summed `osm_length` gives 51,740 km. The OSM changesets in that file run up to 2024-07-17.
- The HOT export (2026-11-02) has 162,668 features. Its most common highway values by feature count are residential (88,650), track (22,372), service (16,091), unclassified (12,783) and tertiary (5,459). Only 12% of features have `surface` and 0.03% have `width` — [HOT quality report](https://production-raw-data-api.s3.amazonaws.com/ISO3/LBN/roads/hotosm_lbn_roads_report.html)

**Computed: national length by class (km)**

Overpass figures are from 2026-11-06, for ways within the Lebanon area. HOT figures are from the 2026-11-02 export, clipped to the country.

| class | Overpass (km) | HOT export (km) |
|---|---|---|
| motorway (+link) | 441 + 121 | 475 + 124 |
| trunk (+link) | 873 + 44 | 871 + 44 |
| primary (+link) | 1,022 + 9 | 1,058 + 9 |
| secondary (+link) | 2,179 + 9 | 2,263 + 9 |
| tertiary (+link) | 3,819 + 8 | 3,906 + 8 |
| residential | 20,407 | 20,503 |
| unclassified | 7,756 | 8,027 |
| living_street | 20 | 20 |
| service | 2,016 | 2,075 |
| pedestrian (linear ways only) | 66 | 42 |
| footway | 188 | 192 |
| steps | 11 | 11 |
| path | 977 | 1,039 |
| track | 7,150 | 7,660 |
| **total of listed classes** | **47,116** | **48,442 (all highway=*)** |
| sidewalk-relevant subset (trunk–tertiary + links, residential, unclassified, living_street, pedestrian, road) | **36,211** | **36,713** |
| ways with any `sidewalk`/`sidewalk:left/right/both` tag | 167 km (20 + 147; may overlap) | – |
| `footway=sidewalk` ways | 7.8 km | – |
| `footway=crossing` ways | 1.9 km | – |

Method: `make stat` per class (see `overpass_stats.py`). The ~3% gap between the two sources comes from boundary handling (Overpass counts any way inside the area, while HOT clips to an h3-buffered boundary) and from the four-day snapshot difference.

**Computed: by governorate (sidewalk-relevant centreline km, HOT export, COD 8-governorate set)**

COD boundaries merge Keserwan-Jbeil into Mount Lebanon.

| governorate | motorway | trunk | primary | secondary | tertiary | residential | unclassified | service | track | all highway | sidewalk-relevant |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mount Lebanon (incl. Keserwan-Jbeil) | 337 | 213 | 243 | 1,034 | 1,136 | 5,911 | 1,688 | 815 | 2,179 | 13,961 | 10,231 |
| Baalbek-Hermel | 0 | 196 | 54 | 95 | 620 | 2,675 | 1,447 | 78 | 1,798 | 7,452 | 5,089 |
| Nabatieh | 0 | 70 | 185 | 194 | 474 | 2,898 | 1,166 | 229 | 558 | 5,827 | 4,978 |
| Bekaa | 60 | 134 | 52 | 160 | 414 | 2,143 | 1,108 | 245 | 1,233 | 5,623 | 4,016 |
| South | 68 | 146 | 185 | 221 | 386 | 2,595 | 985 | 259 | 499 | 5,401 | 4,525 |
| North | 92 | 77 | 253 | 360 | 416 | 2,227 | 790 | 210 | 535 | 5,090 | 4,128 |
| Akkar | 0 | 23 | 68 | 137 | 331 | 1,788 | 820 | 150 | 809 | 4,240 | 3,169 |
| Beirut | 34 | 56 | 16 | 39 | 83 | 233 | 21 | 88 | 0 | 639 | 483 |

Link classes are merged into their parent class. Beirut also has 33 km of pedestrian ways, 21 km of footway and 5 km of steps. About 210 km of features carry no adm1 (sea or border slivers).

The Overpass per-governorate results (OSM's own 9 governorates, including Keserwan-Jbeil) are in `summary_tables.md` table T5. For example, sidewalk-relevant km are Beirut 469, North 4,171, Bekaa 4,104, Mount Lebanon (without Keserwan-Jbeil) 7,162 and South 4,678.

**Computed: main cities** (Overpass, 2026-11-06)

These are circular `around:` buffers at the stated radius around each city centre, not municipal limits. A way is counted in full if any part of it touches the buffer, so totals are slight overestimates. Sidewalk-relevant has the same definition as above. Block-face km = 2 × sidewalk-relevant.

| city (buffer) | motorway | trunk | primary | secondary | tertiary | residential | unclassified | service | pedestrian+footway+steps | sidewalk-relevant km | block-face km | km with sidewalk tags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Beirut Governorate (admin area) | 43 | 54 | 14 | 37 | 78 | 215 | 21 | 76 | 74 | 469 | 938 | 0.2 (+1.8 footway=sidewalk) |
| Greater Beirut r=8 km (incl. Dahiyeh, Metn coast, Baabda) | 122 | 122 | 27 | 102 | 262 | 716 | 95 | 235 | 100 | 1,380 | 2,760 | 5.0 |
| Tripoli + Mina r=5 km | 41 | 39 | 28 | 30 | 48 | 336 | 74 | 63 | 10 | 560 | 1,120 | 2.2 |
| Saida r=3 km | 2 | 29 | 22 | 19 | 23 | 127 | 22 | 32 | 19 | 244 | 488 | 0.4 (+4.7 footway=sidewalk) |
| Jounieh r=3 km | 21 | 6 | 12 | 42 | 39 | 85 | 5 | 24 | 3 | 190 | 380 | 12.9 |
| Zahle r=3 km | 0 | 30 | 0 | 16 | 31 | 214 | 56 | 18 | 1 | 348 | 696 | 0 |
| Tyre (Sour) r=2.5 km | 0 | 7 | 10 | 16 | 6 | 40 | 8 | 17 | 11 | 88 | 176 | 0 |
| Byblos (Jbeil) r=2 km | 15 | 0 | 17 | 26 | 15 | 72 | 10 | 14 | 5 | 140 | 280 | 3.5 |
| Nabatieh r=2.5 km | 0 | 44 | 11 | 10 | 18 | 157 | 30 | 9 | 0 | 270 | 540 | 0 |
| Baalbek r=2.5 km | 0 | 0 | 0 | 12 | 20 | 167 | 37 | 3 | 2 | 236 | 472 | 0 |
| Batroun r=1.5 km | 13 | 0 | 7 | 2 | 2 | 36 | 2 | 5 | 0 | 50 | 100 | 0.3 |
| Aley r=2 km | 11 | 0 | 5 | 35 | 11 | 130 | 16 | 8 | 0 | 196 | 392 | 0 |
| Chtaura r=1.5 km | 4 | 26 | 2 | 13 | 16 | 50 | 12 | 8 | 0 | 120 | 240 | 0 |

Buffer centres (lat, lon) are in `overpass_stats.py`. Notes on individual cities:
- Tyre's 2.5 km buffer is partly sea, as the city sits on a peninsula.
- Beirut has the only meaningful mapped pedestrian network: 49 km of pedestrian ways, 20 km of footway and 5 km of steps.
- The "Beirut (admin)" name query returned 0, so the Beirut Governorate admin area is used instead.

These 12 city buffers together hold about **3,800 km of sidewalk-relevant centreline, about 7,600 block-face km**, counting Greater Beirut r=8 km rather than Beirut Governorate. That is about 18% of the Tier 1–2 envelope in section 2.

### Inferences
- **The sidewalk-relevant centreline is about 36,000–37,000 km nationally.** Mapping both sides gives a theoretical maximum of about **73,000 block-face km**. Dense and urban-cluster areas (section 2) cut this to about 42,700 block-face km, and dense cores alone to about 15,900 block-face km.
- **Track (about 7,200–7,700 km), path (about 1,000 km) and most service roads (about 2,000 km) should be out of scope.** Service roads are driveways and parking aisles. The exception is dense urban service alleys, which act as streets; that includes alleys in Palestinian camps.
- **Motorways cannot be excluded blindly.** About 300 km of motorway lies in dense cells, such as the Beirut–Jounieh "autostrade" and the Dora/Jal el-Dib corridors. Lebanese motorways often have frontage, bus stops and informal pedestrian crossings. Handle these as a special "pedestrian crossing/frontage" layer rather than as two-sided sidewalks.
- **OSM in Lebanon carries almost no pedestrian-infrastructure attributes.** The 167 km tagged with sidewalks is about 0.5% of the sidewalk-relevant network. `width` is filled on 0.03% of features. A national program will have to create these attributes, not just validate them.

### Gaps
- OSM tags a large share of urban streets as `residential` or `unclassified`, and some urban streets are not yet mapped, especially in informal areas and camps. True street length in dense areas may be higher. I found no published OSM completeness estimate specific to Lebanon.
- City figures use buffers, not municipal or urban-extent polygons. Lebanon's municipal boundaries are not consistently in OSM, and the COD adm3 cadastres split cities into several units, for example Zahle into 4 or 5 cadastres and Saida into 3 or more. A follow-up could sum COD adm3 cadastres per city using `hot_by_adm3` in `gpkg_lengths.json`.
- The OSM governorate set (9, including Keserwan-Jbeil, from Overpass) and the COD set (8, from the HOT export) differ. Both are provided: OSM Keserwan-Jbeil has 3,203 km sidewalk-relevant and OSM Mount Lebanon has 7,162 km, which together roughly match COD Mount Lebanon at 10,231 km.

---

## 2. Urban extent: how much road length lies where sidewalks are expected, and block-face km to map

### Takeaway
I classified each road segment by the WorldPop 2020 density of the 1 km cell it falls in, using GHSL Degree-of-Urbanisation density thresholds. Results:
- **About 7,900 km** of sidewalk-relevant centreline lies in dense cells (≥1,500 inhabitants/km²), where 4.93 M people (72%) live.
- **Another 13,400 km** lies in urban-cluster-density cells (300–1,500/km²), with 1.39 M people.

Together that is **about 21,300 km of centreline, or about 42,700 block-face km (two sides)**, serving about 93% of the population. This is the realistic sizing envelope for a national program. A dense-core-only phase is about 15,900 block-face km.

### Cited Findings
- Lebanon has 1,065 municipalities (MOIM, 2025). Elections were held in 1,064 of them in May 2025. Over 70% of municipalities have fewer than 4,000 registered voters, so the municipal map is highly fragmented — [UNDP 2025 municipal elections key results](https://www.undp.org/lebanon/publications/2025-lebanese-municipal-and-mukhtar-elections-key-results); [Arab Reform Initiative](https://www.arab-reform.net/publication/empowering-lebanons-municipalities-amid-crisis/); [Wikipedia: 2025 Lebanese municipal elections](https://en.wikipedia.org/wiki/2025_Lebanese_municipal_elections)
- Mount Lebanon alone has 333 municipalities, of which 70 were elected by acclamation in 2025 — [LBCI](https://www.lbcgroup.tv/news/lebanon-news/852265/70-municipalities-and-187-mukhtars-win-unopposed-in-mount-lebanon/en)
- Unions of municipalities share resources and run projects that individual municipalities cannot. I found no authoritative current count of unions — [Executive Magazine explainer](https://www.executive-magazine.com/explainer-2/municipalities-in-lebanon-understanding-their-history-structure-and-function)
- Under national definitions, about 89–91% of Lebanon's population is urban. The World Bank series gives 90.7% for 2024. No census has been held since 1932 — [Springer study](https://link.springer.com/10.1007/s12517-022-09520-6); [World Bank series via statisticsoftheworld](https://statisticsoftheworld.com/country/lebanon/urban-population)
- The GHSL Urban Centre Database (GHS-UCDB R2024A) defines urban centres as contiguous cells at ≥1,500 inhabitants/km². An example derived from it gives the Zahle urban centre a 2020 population of 119,318 — [sprawlmap.org Zahle](https://sprawlmap.org/places-bsdr/lebanon/bekaa/zahle/geographic-context.html)
- Lebanon's population is about 5.85 M (2025, UN) on 10,452 km² — [InforMEA](https://www.informea.org/fr/countries/lb/party-summary). The UK Home Office bulletin uses 5.88 M — [UK CPIN bulletin](https://assets.publishing.service.gov.uk/media/69fca0922a6137e93226b85c/LBN_Country_Bulletin_Security_situation.pdf). The WorldPop 2020 UN-adjusted raster sums to 6.83 M, because it includes refugees. Treat the absolute numbers as indicative and the density classes as robust.
- **HeiGIT's `urban` attribute is unusable for this purpose.** It is set to 1 only on about 1,700 km of ways, all of them ways with Mapillary predictions. It does not reflect the GHS urban extent — computed from the [HeiGIT dataset](https://data.humdata.org/dataset/lebanon-road-surface-data).

**Computed: road km by WorldPop-density class** (HOT export; `urban_share.py`)

| class | sidewalk-relevant centreline km | all highway km | population (WorldPop 2020) | block-face km (×2 of sidewalk-relevant) |
|---|---|---|---|---|
| dense ≥1,500/km² ("urban-centre density") | 7,935 | 9,181 | 4.93 M | 15,870 |
| urban-cluster density 300–1,500/km² | 13,410 | 15,675 | 1.39 M | 26,820 |
| rural 50–300/km² | 10,291 | 13,721 | 0.43 M | 20,580 |
| very low <50/km² | 5,077 | 9,800 | 0.08 M | 10,150 |
| **total** | **36,713** | **48,377** | 6.83 M | 73,430 |

Within dense cells, sidewalk-relevant km by class are residential 5,130, tertiary 939, unclassified 766, secondary 480, trunk 343, primary 229 and pedestrian 37. Dense cells also contain 304 km of motorway and 598 km of service roads.

**Computed: by governorate.** Sidewalk-relevant centreline km by density class, with block-face km for dense plus cluster cells.

| governorate | dense | urban-cluster | rural | very low | dense+cluster block-face km |
|---|---|---|---|---|---|
| Mount Lebanon (incl. Keserwan-Jbeil) | 3,382 | 3,758 | 2,370 | 722 | 14,279 |
| South | 1,229 | 2,152 | 790 | 354 | 6,762 |
| Nabatieh | 891 | 2,134 | 1,212 | 740 | 6,051 |
| North | 809 | 1,773 | 1,179 | 367 | 5,165 |
| Bekaa | 595 | 1,293 | 1,273 | 856 | 3,774 |
| Baalbek-Hermel | 504 | 1,364 | 1,880 | 1,341 | 3,735 |
| Akkar | 69 | 929 | 1,564 | 608 | 1,995 |
| Beirut | 456 | 8 | 15 | 3 | 929 |

**Computed: top districts by dense centreline km.** The full list is in `summary_tables.md` table T3.

| district | dense | dense + cluster |
|---|---|---|
| Meten | 1,067 | 1,571 |
| Baabda | 828 | 1,142 |
| Nabatieh | 668 | 1,480 |
| Sour | 583 | 1,525 |
| Saida | 573 | 1,419 |
| Zahle | 555 | 1,264 |
| Chouf | 529 | 1,619 |
| Aley | 468 | 1,303 |
| Baalbek | 457 | 1,664 |
| Beirut | 456 | 464 |
| Kesrwane | 402 | 1,210 |
| Minieh-Dennie | 358 | 702 |
| Tripoli | 183 | 297 |

Method caveats:
- These are WorldPop 1 km cell-level density thresholds only. DEGURBA's contiguity and minimum-population rules (urban centre ≥50,000; urban cluster ≥5,000) were not applied.
- Each segment is assigned to the cell containing its midpoint.
- Cell area is corrected for latitude (about 0.77 km² per cell).
- Tripoli's small dense figure comes partly from the COD "Tripoli" district being only the city proper. The al-Mina cadastre, for example, is separate.

### Inferences
- **Recommended sizing tiers:**
  - **Tier 1:** dense cores, about 7,900 km of centreline and about 15,900 block-face km.
  - **Tier 2:** urban-cluster towns and suburbs, adding about 13,400 km and about 26,800 block-face km.
  - **Tier 3:** rural village cores. These are optional, about 10,300 km, and should be handled with a "village-centre only" rule, for example 300–500 m around the municipal centre or school.
- Tiers 1 and 2 together come to about **42,700 block-face km**.
- About 72% of residents live in about 22% of the sidewalk-relevant network (the dense cells). That argues strongly for density-weighted phasing.
- **The 1,065 municipalities should not be the delivery unit.** They are too small and too numerous. Use the 25–26 districts (qadas) or the unions of municipalities as work packages. Treat a municipality as the unit for QA and sign-off.

### Gaps
- I did not compute an exact GHSL-SMOD (R2023A) or GHS-BUILT-S overlay. Downloading and reading the JRC rasters was beyond the stdlib tooling used here. A follow-up should rerun `urban_share.py` logic on GHS-SMOD 2025, for which [GHSL](https://ghsl.jrc.ec.europa.eu) is the source.
- I found no published GHSL Lebanon "country fact sheet" figures, such as built-up km² or the list of urban centres.
- The count of unions of municipalities is unconfirmed.

---

## 3. Existing street-level imagery coverage and areas needing new capture

### Takeaway
Open street-level imagery covers only a small, old and Beirut/Mount Lebanon-centric slice of the network:
- HeiGIT's Mapillary-based surface model had imagery for about 0.4–0.8 thousand km of road. Ways touched by at least one prediction total about 2.6 thousand km, about 5% of OSM ways.
- The imagery is mostly from 2017–2020.
- It covers nothing in Nabatieh or Baalbek-Hermel and almost nothing in Bekaa or Akkar.

Google added Street View road coverage in Lebanon in April 2024, but its terms bar building derived datasets. **Plan new capture for practically the whole Tier 1–2 network.** The exception is Beirut and the coastal Metn/Keserwan/Baabda corridor, where existing Mapillary imagery can support a pilot or a change-detection baseline.

### Cited Findings
- HeiGIT's road-surface dataset says the Mapillary-derived predictions add only 0.2769% of the missing surface information. It derives predictions from "Mapillary street-level imagery" — [HDX HeiGIT](https://data.humdata.org/dataset/lebanon-road-surface-data)
- Wikipedia's Street View timeline says: "In April 2024, Google added street view coverage in Lebanon." It gives no areas — [Wikipedia: Google Street View in Asia](https://en.wikipedia.org/wiki/Google_Street_View_in_Asia)
- Google's 2018 Lebanon Street View "Special Collection" covered 41 heritage and cultural sites, captured by Trekker backpack. It was not road coverage — [Arabian Business](https://www.arabianbusiness.com/industries/technology/404221-google-street-view-launches-lebanon-collection); [the961](https://www.the961.com/google-street-view-lebanons-landmarks)
- The OSM wiki Lebanon page references Mapillary imagery from a "Lebanon drive" and a Beirut capture from May 2019 — [OSM wiki Lebanon](https://wiki.openstreetmap.org/wiki/Lebanon)
- HeiGIT's newer "Lebanon: Planet Road Surface, Width, and Passability" dataset uses PlanetScope imagery from 2020 and 2024. It covers only arterial roads (motorway, trunk, primary and secondary), and provides AI road width and passability, but not sidewalks — [HDX package search (HeiGIT)](https://data.humdata.org/dataset/lebanon-planet-road-surface-data)

**Computed: Mapillary-coverage proxy by governorate** (`gpkg_lengths.py`, `mapillary_proxy.py`, joined to HOT adm1 via osm_id)

| governorate | ways with ≥1 Mapillary prediction (km of HeiGIT segments) | share of HeiGIT segment km |
|---|---|---|
| Mount Lebanon | 1,556 | 9.3% |
| Beirut | 400 | 31.7% |
| North | 367 | 6.5% |
| South | 197 | 3.5% |
| Bekaa | 25 | 0.4% |
| Akkar | 18 | 0.4% |
| Nabatieh | 0 | 0% |
| Baalbek-Hermel | 0 | 0% |
| **total** | **2,571** | **4.9%** |

- Summed `predicted_length`, the length actually covered by imagery-based predictions, is 821 km nationally. If each way is counted once (maximum per osm_id), it is 425 km: Mount Lebanon 277, Beirut 76, North 40, South 27, Bekaa 3. HeiGIT splits ways into segments, so the true value is between these two figures.
- The mean image timestamp of these predictions, weighted by km, falls in: 2014 (31 km), 2017 (388), 2018 (872), 2019 (691), 2020 (531), 2021–2024 (55 in total). The imagery is 6–9 years old.
- HeiGIT's `urban_area` labels for the covered ways are "Beirut; Antelias; Aley" (743 km), Saida (58), Tripoli (31) and Tyre (8).

### Inferences
- **Mapillary coverage is concentrated in Beirut and the coastal Metn, Baabda, Kesrouan and Aley corridors**, consistent with the brief's expectation. It is also stale (mostly before 2020), so it predates the 2020 port blast, the 2024 war and the 2026 war. It is useful as a historical baseline and for training or validating detection models, not as the mapping source.
- **New capture is needed for an estimated 95–98% of Tier 1–2 block-faces.** This includes all of Nabatieh, Baalbek-Hermel, Bekaa, Akkar and most of the North and South.
- **Google Street View cannot legally be a source for the sidewalk dataset, even for manual tracing** (see Gaps for the clause). At most, staff can use it as general situational awareness for planning capture routes, and nothing derived from it may enter the data.
- Capture options are vehicle- or e-bike-mounted 360° cameras uploaded to Mapillary or Panoramax, which keeps an open licence. Use foot or backpack capture for old-city souks (Tripoli, Saida, Byblos, Batroun) and for camps.

### Gaps
- Mapillary's own coverage statistics for Lebanon, from the live map or API, need an access token, so I did not query them. The HeiGIT proxy may undercount: it only uses images that passed their pipeline and only OSM ways up to 2024.
- Google's own terms page did not render, so the exact current clause on dataset building is not verified. Secondary copies of the Google Maps Platform ToS say the customer "will not create content based on Google Maps Content, including tracing, digitizing, or creating other datasets". The copies give building an index of tree locations from Street View imagery as an example of a prohibited use — [ConductAtlas copy of GMP ToS](https://conductatlas.com/platform/google-maps/google-maps-platform-terms-of-service/provision/CA-P-041128/prohibition-on-creating-content-from-google-maps-content/); [Cesium terms for Google](https://cesium.com/legal/terms-for-google/). OSM's policy also forbids using Google map data or Street View to create OSM content — [OSM wiki: Google](https://wiki.openstreetmap.org/wiki/Google). Check the live text at [cloud.google.com/maps-platform/terms](https://cloud.google.com/maps-platform/terms) before the final report.
- The extent of the April 2024 Street View road coverage (which cities or roads) is not documented in the sources found.

---

## 4. Access and security constraints by region (late 2026) and how to treat them

### Takeaway
After the March–April 2026 war and a June 2026 ceasefire and framework deal, the following areas remain high-risk:
- Israel still holds a self-declared "security zone" in southern Lebanon. It was 8–10 km deep in April and expanded later, with reports of about a fifth of Lebanon held and 47 of 62 "buffer zone" villages occupied.
- Strikes continue in the south, the Bekaa/Baalbek and, intermittently, Dahiyeh.

The plan should treat these as follows:
- **Defer** field capture south of the Litani (Bucket A: Sour, Bint Jbeil, Marjayoun, Hasbaya).
- Run **conditional or partner-led** capture in Nabatieh district, Baalbek-Hermel, Dahiyeh and the 12 Palestinian camps (Bucket B).
- Proceed normally elsewhere (Bucket C), which holds about 69% of the Tier 1–2 workload.

### Cited Findings
- On 2 March 2026, Hezbollah fired at northern Israel after US-Israeli strikes on Iran. Israel launched air strikes across Lebanon and ground operations in the south. By 6 April the IDF had struck over 3,500 targets, "mainly in the Hezbollah strongholds of Beirut's southern suburbs, southern Lebanon and the eastern Bekaa Valley". Some strikes reached northern Lebanon, Mount Lebanon and central Beirut. A 10-day ceasefire took effect on 16–17 April 2026. Israel said its troops would stay in a "security buffer zone… 8 to 10 kilometres inside southern Lebanon". About 1.05 M people (about 18% of the population) were displaced — [UK Home Office CPIN bulletin, covering 2 Mar–17 Apr 2026](https://assets.publishing.service.gov.uk/media/69fca0922a6137e93226b85c/LBN_Country_Bulletin_Security_situation.pdf)
- Israeli evacuation orders affected 14% of Lebanon by mid-March 2026, citing Reuters of 13 March 2026, as quoted in the [UK CPIN bulletin](https://assets.publishing.service.gov.uk/media/69fca0922a6137e93226b85c/LBN_Country_Bulletin_Security_situation.pdf).
- Israel's defence minister said Israel would control the area up to the Litani River. He said more than 600,000 displaced residents would be barred from returning south of the Litani. One count shows Israel occupying 47 of the 62 villages in its "buffer zone", with a "yellow line" marking its edge — [Al-Monitor, Mar 2026](https://www.al-monitor.com/originals/2026/03/israel-establish-buffer-zone-south-lebanon-litani-river-defence-minister-says); [L'Orient Today maps](https://today.lorientlejour.com/article/1504502/what-we-know-in-maps-about-the-buffer-zone-israel-is-claiming-in-south-lebanon.html); [L'Orient Today residents](https://today.lorientlejour.com/article/1504254/stories-of-south-lebanese-residents-now-in-the-israeli-buffer-zone.html)
- On 20 April 2026, the Israeli military told residents to stay out of a belt along the whole border and listed more than 50 further villages not to return to — [Tribune/AFP](https://tribune.com.pk/story/2603743/israeli-military-urges-south-lebanon-residents-to-avoid-restricted-areas)
- In June 2026 a ceasefire "decrease[d] dramatically" the violence. By September, however, Israeli troops occupied "swathes of southern Lebanon" and were razing villages in a "self-declared security zone". Strikes continued inside and north of it, "mostly without evacuation warnings", for example in Kfar Rumman and Arab Salim (Nabatieh) on 6–7 Sep 2026. More than 4,300 people had been killed since 2 March — [Reuters via bdnews24, 7 Sep 2026](https://bdnews24.com/world/middle-east/11d1c0409895)
- Israeli troops have seized around a fifth of Lebanon, deeper than at any time since the 1982–2000 occupation. This is a search-result summary of a wire report; verify against the primary article — [search-summarised report, 2026](https://www.arabnews.pk/node/2619627/middle-east)
- A US-brokered Israel–Lebanon framework was signed in Washington in June 2026. Rome talks in August remained split over Hezbollah disarmament. Under the "pilot zone" mechanism, the Lebanese army takes over sites in exchange for limited Israeli pullbacks: Zawtar al-Gharbiyeh was done, and Ali Taher Hill near Nabatieh, Khiam and Bint Jbeil were proposed. Residents returned to Zawtar only after survey and clearance work. Lebanese authorities count 4,333 killed since March and more than 1 M displaced. Israel holds Beaufort Castle — [Al Jazeera, 5 Aug 2026](https://www.aljazeera.com/news/2026/8/5/lebanon-and-israel-still-split-over-disarming-hezbollah-at-rome-talks); [Times of Israel](https://www.timesofisrael.com/lebanon-israel-agree-on-countries-that-could-verify-hezbollah-disarmament-official/)
- Dahiyeh was the main target in Beirut in March 2026. Israel ordered further strikes on Beirut's southern suburbs in June 2026 — [Africanews/AP, Mar 2026](https://www.africanews.com/amp/2026/03/17/lebanon-beiruts-southern-suburbs-bombarded-by-israeli-strikes); [Maryland MCAC repost, Jun 2026](https://mcac.maryland.gov/2026/06/israel-orders-strikes-on-beiruts-southern-suburbs-as-hezbollah-rockets-hit-northern-israel/)
- Damage to water systems across the South, Bekaa and Baalbek-Hermel affected more than 2.6 M people. In March, displaced people were directed to the North, Akkar and parts of Bekaa — [search-summarised UNHCR/IOM reporting](https://data.unhcr.org/en/documents/download/122170); [IOM via Asharq al-Awsat](https://english.aawsat.com/node/5258284)
- **Palestinian camps.** There are 12 UNRWA official camps: Beddawi, Burj el-Barajneh, Burj el-Shemali, Dbayeh, Ein el-Hilweh, El Buss, Mar Elias, Mieh Mieh, Nahr el-Bared, Rashidieh, Shatila and Wavel. About 45% of Palestine refugees in Lebanon live in them — [This is Beirut](https://thisisbeirut.com.lb/articles/1316380/what-are-the-12-palestinian-camps-in-lebanon); [Wikipedia list](https://en.wikipedia.org/wiki/Palestinian_refugee_camps)
- **Camp security.** Weapons handovers began in September 2025 from Ein el-Hilweh and Beddawi, and Fatah handed over its last heavy weapons in Ein el-Hilweh in December 2025. The Lebanese army still stays outside the camps, and hardline groups on two streets of Ein el-Hilweh reject disarmament — [L'Orient Today](https://today.lorientlejour.com/article/1489912/fatah-hands-over-its-last-heavy-weapons-to-the-lebanese-army-in-saidas-ain-al-hilweh-camp.html); [The New Arab](https://www.newarab.com/news/palestinians-lebanon-hand-over-weapons-what-happens-next); [Arab News](https://www.arabnews.com/node/2615153)
- A Hamas member and his wife were killed in an Israeli strike in Beddawi camp near Tripoli in March 2026 — [UK CPIN bulletin](https://assets.publishing.service.gov.uk/media/69fca0922a6137e93226b85c/LBN_Country_Bulletin_Security_situation.pdf)

**Computed: workload by security bucket** (sidewalk-relevant centreline km; `summarize.py`, table T4)

| bucket | definition (planning assumption) | dense | urban-cluster | dense+cluster | block-face km (×2) | share of Tier 1–2 |
|---|---|---|---|---|---|---|
| A: defer, remote-only | districts Sour, Bent Jbeil, Marjaayoun, Hasbaya (south of the Litani or border belt) | 806 | 2,264 | 3,070 | 6,139 | 14% |
| B: conditional or partner-led | El Nabatieh district; Baalbek and Hermel districts; Dahiyeh proxy (Chiyah [Baabda part], Haret Hreik, Tahouitat el-Ghadir cadastres, 223 km, all counted dense) | 1,395 | 2,176 | 3,571 | 7,142 | 17% |
| C: proceed | all other districts | 5,734 | 8,971 | 14,704 | 29,409 | 69% |

Caveats:
- The buckets are district-level approximations. Sour city and parts of Sour district lie north of the Litani, and the occupied belt does not follow district lines.
- The Dahiyeh proxy is approximate. COD adm3 units in Baabda are aggregated: Ghobeiry and Burj el-Barajneh have no separate adm3 polygon and appear to fall within these units.
- The camps are not separated out, because they are not admin units. They are small in road-km terms.

### Inferences
- **Bucket A (about 6,100 block-face km).** Capture no new field imagery while the occupation and "yellow line" restrictions persist. Instead:
  - prepare the OSM centreline backbone remotely from imagery;
  - flag destroyed or bulldozed villages;
  - schedule capture to follow army "pilot zone" handovers and UXO clearance, as Zawtar al-Gharbiyeh shows clearance comes first.
- **Post-war reconstruction will redesign many streets in Bucket A.** Mapping pre-war sidewalks there has low value, so defer to reconstruction-era surveys.
- **Bucket B (about 7,100 block-face km).**
  - Capture through local partners with municipal and community clearance: municipal unions, Lebanese Red Cross or Civil Defence, and local universities.
  - Use short daytime windows, and include a stop rule tied to evacuation warnings.
  - Dahiyeh needs permission from local authorities. Pre-conflict Mapillary imagery is partial and stale.
  - For the camps, partner with UNRWA and the popular committees, and treat them as their own stratum (foot capture, alleys as `service`/`footway`).
- **Bucket C (about 29,400 block-face km).** Standard capture. Start with Beirut, Metn, Baabda (non-Dahiyeh), Kesrouan, Tripoli-Mina, Saida, Zahle-Chtaura and Jbeil-Batroun.
- **Plan for re-tasking.** The March 2026 war showed that strikes can reach Beirut, Mount Lebanon and the North. Keep a security-gating step in each work-package release, rather than a fixed map.

### Gaps
- I found no authoritative map or km² figure for the Israeli-held area as of November 2026, and no reports from October or November 2026. The "fifth of Lebanon" figure comes from a search summary of a wire report and needs verification.
- Military zones (LAF and UNIFIL bases, and the restricted areas around them) are not quantified. UNIFIL's mandate status at end-2026 was not checked.
- I found no current UNRWA figures on camp area or road length.
- I found no current IOM DTM figure for November 2026. The latest figures found are from March to August 2026.

---

## 5. Prioritization criteria from comparable programs, and a stratified-sampling alternative

### Takeaway
Comparable sidewalk programs score segments on several criteria: proximity to schools, transit, demand generators and destinations; population or pedestrian demand; crash history or safety; equity; and road functional class. In Lebanon the data support:
- density from WorldPop;
- schools and hospitals (OSM or HeiGIT accessibility layers);
- the Greater Beirut bus and BRT corridors;
- coarse crash concentration (North and Mount Lebanon).

If full coverage is not affordable, a stratified probability sample of 1 km cells or block-faces gives statistically valid national estimates for roughly 5–10% of the effort.

### Cited Findings
- **Comparable program criteria:**
  - Braintree (MA) scores condition, functional class, a pedestrian-usage score (schools, parks, municipal buildings, transit, commercial areas, community centres) and width — [Braintree](https://www.braintreema.gov/DocumentCenter/View/14586)
  - Dunwoody (GA) weights school walk routes at about a quarter of the score — [Dunwoody](https://dunwoodyga.gov/home/showpublisheddocument/718/637353634289630000)
  - Tallahassee (FL) scores transit, parks, disadvantaged housing and employment, and puts missing sidewalks in the top tier — [Tallahassee](https://www.talgov.com/you/you-sidewalk-prioritization)
  - Ann Arbor (MI) uses schools, transit, equity, road class, requests and safety, plus a demand index — [Ann Arbor write-up](https://mark.stosberg.com/how-ann-arbor-used-spatial-analysis-for-sidewalk-prioritization/)
  - Seattle builds a demand network from frequent transit and school walksheds, weighted 60/40 safety/equity — [Seattle SPAB minutes](https://www.seattle.gov/Documents/Departments/SeattlePedestrianAdvisoryBoard/SPABFebruary16MeetingMinutes.pdf)
  - Honolulu ranks by cost-to-demand and safety, then applies equity — [Oahu Pedestrian Plan](https://www8.honolulu.gov/completestreets/wp-content/uploads/sites/37/2024/01/Oahu_Pedestrian_Final_Report_appendices_reduced.pdf)
  - Pioneer Valley inventories arterials and collectors first, then scores gaps by density and destinations — [PVPC](https://pvpc.org/wp-content/uploads/2025/10/Appendix-B-Sidewalk-Inventory.pdf)
- **Pedestrian share of road deaths.** Pedestrians were 43% of reported road deaths in WHO GSRRS 2015, based on 649 fatalities in 2013 from ISF/TMC data — [WHO 2015 Lebanon profile](https://cdn.who.int/media/docs/default-source/country-profiles/road-safety/road-safety-2015/road-safety-2015-lbn.pdf). Other estimates are about 40% (WHO estimate) — [L'Orient Today](https://today.lorientlejour.com/article/1305531/behind-the-numbers-how-lebanons-crisis-is-felt-on-the-roads.html); 39% in 2024 official TCC figures — [LBCI](https://lbcgroup.tv/news/news-bulletin-reports/794385/traffic-fatalities-on-the-rise-in-lebanon-the-urgent-need-for-road-saf/en); and about 30% of casualties in a 2025 report — [This is Beirut](https://thisisbeirut.com.lb/articles/1323029/when-roads-become-death-traps).
- **2025 road deaths conflict by source:**
  - ISF: 162 deaths from January to May 2025.
  - YASA: 346 deaths through August.
  - Full year: about 530 (ISF, cited by L'Orient Today) versus 451 (LBCI; 389 in 2024).
  - The ISF records only cases that reach court.
  - Red Cross data put North Lebanon and Mount Lebanon at over 65% of crashes since early 2023.
  - Sources: [L'Orient Today](https://today.lorientlejour.com/article/1474598/road-safety-a-deadly-summer-on-lebanons-roads.html); [LBCI](https://www.lbcgroup.tv/news/news-bulletin-reports/874433/lebanons-road-accidents-casualties-near-annual-record-in-seven-months/en)
- **WHO's estimated road-death rate** is about 18.1 per 100,000 (GSRRS 2018), roughly double official counts because registration is incomplete — [Save the Children summary](https://www.childhealthinitiative.org/blog/2019/july/new-save-the-children-report-exposes-risks-facing-children-on-the-roads-of-lebanon); [L'Orient Today](https://today.lorientlejour.com/article/1305531/behind-the-numbers-how-lebanons-crisis-is-felt-on-the-roads.html)
- **Transit corridors.**
  - The World Bank Greater Beirut Public Transport Project planned BRT trunk lines on the northern (Tabarja–Beirut), southern and eastern approaches. It also planned about 20 feeder routes with 850–900 buses. The project is listed as closed — [World Bank P160224](https://projects.worldbank.org/P160224?lang=en)
  - A new public bus fleet ran 11 routes in 2025, mostly in Greater Beirut but also reaching the north, south and east — [Arab News/AFP](https://www.arabnews.com/node/2608217/amp); [Asharq al-Awsat](https://english.aawsat.com/arab-world/5150324-lebanon-bumpy-road-public-transport-revival)
- **Accessibility data.** HeiGIT publishes Lebanon accessibility indicators (travel time to health and education, combined with WorldPop). These can feed school and hospital weighting — [HDX HeiGIT accessibility](https://data.humdata.org/dataset/lebanon-accessibility-indicators)

### Inferences
- **Proposed Lebanese priority score per block-face or 250 m street segment:**

  | criterion | weight | data |
  |---|---|---|
  | population density | 30% | WorldPop or GHS-POP |
  | proximity to schools, universities and hospitals within 400–800 m | 25% | OSM POIs; HeiGIT accessibility |
  | transit | 20% | within 400 m of the 11 bus routes, the planned Tabarja–Beirut BRT corridor and van routes |
  | crash or safety | 15% | ISF/YASA/Red Cross geolocated crashes where available; otherwise road class, i.e. trunk or primary through dense cells |
  | equity | 10% | poverty, displaced-hosting municipalities, camps and informal areas |

  Security gating (section 4) is applied as a filter, not a weight.
- **Phasing:**
  1. Beirut plus the coastal Metn and Baabda dense core, about 2,800 dense km including Dahiyeh. Use the BRT/bus corridors and Beirut as the pilot, because existing Mapillary imagery supports model training.
  2. Secondary cities: Tripoli-Mina, Saida, Jounieh/Kesrouan, Zahle-Chtaura, Jbeil, Batroun and Aley.
  3. Urban-cluster towns in Bucket C.
  4. Buckets B and A as conditions allow.
- **Stratified-sampling alternative**, if full coverage is infeasible:
  - Frame: 1 km WorldPop cells containing sidewalk-relevant roads, or block-faces.
  - Strata: governorate (8) × density class (4) × road class group (arterial: trunk to secondary; collector/local: tertiary, residential, unclassified). That is about 96 strata.
  - Allocation: Neyman, proportional to stratum km × expected variance. Oversample dense cells and arterials.
  - Mapping 100% of Beirut and the Tier 1 cores, plus about 10% of Tier 2 and about 2–5% of Tier 3 block-faces, gives national indicators: % of block-faces with any sidewalk, % ≥1.5 m clear width, obstruction rate, ramp presence. Each would have a confidence interval.
  - Rough effort at those rates: 15,870 + 0.10 × 26,820 + 0.03 × 20,580 ≈ 19,200 block-face km, about 26% of the theoretical 73,400.
  - Sampling clusters of 1 km cells reduces travel cost for field capture.
- **Validate sampling against a fully mapped pilot.** Use the Beirut pilot to estimate between-segment variance, then set sample sizes.

### Gaps
- I found no geolocated national crash dataset that is public (ISF/TMC or YASA blackspots). I also found no governorate breakdown of road deaths. Red Cross crash shares are the only regional split found.
- I found no Lebanese or regional national-scale sidewalk program with published criteria. All comparators found are US city or regional programs.
- Weights and sampling rates above are proposals (inference) and have not been tested.
- I did not verify the current routes and status of the BRT, and found no 2026 project update.
