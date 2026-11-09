# Free imagery data for mapping Lebanon's sidewalks

*Checked 6 November 2026 by querying each source directly (APIs, metadata services, coverage maps).*

## What's free and usable

| # | Source | Type | Resolution | Coverage in Lebanon | Date | Licence / can you use it? |
|---|---|---|---|---|---|---|
| 1 | **Esri World Imagery** | Satellite | 0.31–0.50 m | Whole country | 2020–2024 (see table below) | Free to view and **digitize/trace** in ArcGIS apps, and share the results. Not for bulk tile export or (most likely) AI training. |
| 2 | **Esri World Imagery Wayback** | Satellite archive | 0.31–0.50 m | Whole country | 2013 → 2026 releases | Same terms as #1. Useful for a sharper or less-shaded date. |
| 3 | **OpenAerialMap – Beirut port drone ortho** | Drone orthophoto | **0.12 m** | Port + edge of Mar Mikhael/Karantina (~0.6 km²) | 4 Aug 2020 | **CC BY 4.0**: download, measure, train AI freely. |
| 4 | **OpenAerialMap – Maxar/Planet** | Satellite | 0.42–0.84 m | Greater Beirut | Jun–Aug 2020 | CC BY-NC 4.0: OK for non-commercial research. |
| 5 | **Mapillary** | Street-level photos | Phone/360° photos | **Dense in Beirut**, Metn, Keserwan, coastal highway; Tripoli and Saida have almost none | 2019–2025 | **CC BY-SA 4.0**: download, measure, train AI (credit Mapillary; derived data published outside OSM must be ODbL). Free API token. |
| 6 | **Microsoft Global ML Building Footprints** | Vector (buildings) | — | Whole country | Release Feb 2026 | ODbL: free. Building edges = back edge of the sidewalk. |
| 7 | **OpenStreetMap (Geofabrik / HOT HDX)** | Vector (streets) | — | Whole country | Updated 4 Nov 2026 | ODbL: free. Street centrelines to organise your segments. |
| 8 | **HeiGIT road width & surface (HDX)** | Vector (AI-derived) | — | Arterial roads only | 2020 & 2024 | Free. Carriageway width, not sidewalk, but helps estimate leftover sidewalk space. |

**Not usable:** Google Maps / Street View / Earth (terms forbid tracing and building datasets), Bing (tracing only inside OSM editors), Panoramax and KartaView (almost no Lebanon coverage), Maxar Open Data Program (no Lebanon event), Google Open Buildings (doesn't cover Lebanon).

### Esri imagery currently shown per city (from Esri's own metadata service)

| City | Date | Resolution | Satellite |
|---|---|---|---|
| Beirut – Hamra | 26 Aug 2024 | 0.46 m | GeoEye-1 |
| Beirut – Achrafieh | 14 Nov 2024 | 0.50 m | WorldView-2 |
| Jounieh / Byblos | 23 Nov 2024 | **0.34 m** | Legion |
| Saida | 23 Sep 2023 | **0.31 m** | WorldView-3 |
| Tripoli | 2 Jan 2024 | 0.46 m | GeoEye-1 |
| Tyre | 7 Apr 2023 | 0.50 m | WorldView-2 |
| Zahle | 7 Oct 2020 | 0.46 m | GeoEye-1 |

**Wayback tip for Beirut:** older Wayback releases show sharper **0.31 m WorldView-3** imagery of Beirut (30 Sep 2014 and 8 Nov 2016) and Saida (13 May 2017). Use the [Wayback app](https://livingatlas.arcgis.com/wayback/) to pick the sharpest, least-shaded date for each area. Older imagery may predate changes, especially around the 2020 blast zone.

## What each source can give you

| Data you need | Best free source | Expected accuracy |
|---|---|---|
| **Sidewalk location (polygons)** | Digitize over Esri imagery (#1/#2), guided by OSM streets (#7) and building footprints (#6) | Shape is good; absolute position can be off 5–8 m (Esri's stated accuracy), so align to OSM/buildings |
| **Sidewalk width** | (a) Distance from building edge to curb on imagery; (b) measure from Mapillary photos | (a) ±0.5–1 m at 0.3–0.5 m pixels: good for classes like "<1.2 m / 1.2–2 m / >2 m"; (b) ~0.25 m with modern depth methods (tested in the US, not Lebanon) |
| **Sidewalk length** | Digitized geometry | Good (±1 m) |
| **Curb height** | Not possible from free imagery. Estimate roughly from Mapillary photos, or measure in the field | — |
| **Condition / surface** | Mapillary photos (manual rating or AI) | Good where photos exist |
| **Objects (poles, signs, trees, bins, benches)** | Mapillary's free **auto-detected map features** via API | Good for poles/signs; check by eye |
| **Parked cars, generators, vendors, shop goods** | Run your own detector (e.g. YOLO) on Mapillary photos | Needs a few hundred hand-labelled Lebanese examples |
| **Trees, kiosks, large obstructions from above** | Esri imagery (visual) | Visible at 0.3–0.5 m; poles and bollards are not |

## Recommended workflow (free tools)

1. **Set up QGIS** (free) or ArcGIS (AUB and other Lebanese universities usually have campus licences; Esri's terms explicitly allow digitizing in ArcGIS apps).
2. **Load the base layers:** OSM streets for your study area (Geofabrik `lebanon-latest.osm.pbf` or HOT "Roads of Lebanon" on HDX), Microsoft building footprints for Lebanon, and Esri World Imagery.
3. **Digitize sidewalks** as polygons street by street. Record width at regular points (e.g. every 20 m) as the shortest distance from building edge to curb.
4. **Get a free Mapillary token** (mapillary.com → Dashboard → Developers). Pull image locations, map features (poles, signs, benches, hydrants) and object detections for your area through API v4. Bounding boxes must stay under 0.01 square degrees, so split the area into tiles.
5. **Audit sidewalks in Mapillary photos:** rate condition, check width, and tag obstructions such as cars, generators, vendors and shop displays. Use a simple form (KoboToolbox or a QGIS attribute form).
6. **Optional AI step:** train a detector or segmentation model on Mapillary photos, plus the 12 cm OpenAerialMap drone ortho for overhead sidewalk segmentation. Both are openly licensed for this. Don't train on Esri or Google imagery.
7. **Validate:** pick 30–50 segments and compare against a tape measure or laser meter if anyone can visit them. Otherwise compare imagery-based and photo-based widths against each other.

### Where to start

**Beirut** (Hamra, Achrafieh, Mar Mikhael, Gemmayzeh): it is the only city where all three layers overlap (recent satellite, dense Mapillary, the 12 cm drone ortho at the port edge), and there are published MIT/AUB results to compare against. For Tripoli, Saida, Tyre and Zahle, free imagery gives location and approximate width only. Objects and condition there would need new street-level photos, e.g. one person walking with a $300–550 360° camera and uploading to Mapillary.

## Download links

- Esri World Imagery: https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9 · Wayback: https://livingatlas.arcgis.com/wayback/
- OpenAerialMap Beirut 12 cm ortho (GeoTIFF): https://oin-hotosm-temp.s3.amazonaws.com/5f2bd274b0052e00067dbaed/0/5f2bd274b0052e00067dbaee.tif · browse all: https://map.openaerialmap.org/
- Mapillary map: https://www.mapillary.com/app/?lat=33.8938&lng=35.5018&z=13 · API docs: https://www.mapillary.com/developer/api-documentation
- Microsoft buildings index (filter rows for "Lebanon"): https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv
- OSM Lebanon extract: https://download.geofabrik.de/asia/lebanon.html · HOT roads: https://data.humdata.org/dataset/hotosm_lbn_roads
- HeiGIT road width/surface: https://data.humdata.org/dataset/lebanon-planet-road-surface-data

## Caveats

- **Esri and AI:** Esri's licence allows data collection and editing in ArcGIS apps but says nothing explicit about AI training. An Esri staff forum reply says automated inference on the basemap is disabled and against the terms. Treat Esri imagery as **manual digitizing only** unless Esri confirms otherwise.
- **Esri positional accuracy** is 5–10 m per Esri's metadata. Shapes and widths are reliable, but align the layer to OSM/buildings before measuring.
- **Mapillary coverage** was checked visually on the coverage map, not counted. Capture dates vary by street, so check each image's date.
- **Widths from 0.3–0.5 m imagery** are approximate. Parked cars and building shadows hide curbs, especially in narrow streets.
