# Beirut sidewalk pilot – QGIS project

Pilot area: **Mar Mikhael – Gemmayzeh – north Achrafieh – Karantina edge**
(lon 35.508–35.530, lat 33.884–33.905, about 2 × 2.3 km).

## 1. Install QGIS (one time)

Download **QGIS LTR** (free) from https://qgis.org/download/ → Windows → "QGIS Standalone Installer" (long-term release). Install it with the defaults.

## 2. Open the project

Double-click `Beirut_sidewalk_pilot.qgs`. You'll see four layer groups:

| Group | Layers | Use |
|---|---|---|
| **1. Survey layers (edit these)** | `sidewalks` (polygons), `width_measurements` (lines), `obstructions` (points) | Where you record your data. Stored in `survey/sidewalk_survey.gpkg`, in metres (UTM 36N). |
| **2. Mapillary street photos** | Photo points, detected objects | Empty until you run `fetch_mapillary.py` (step 4). |
| **3. Reference data** | OSM streets, OSM street features (lamps, trees, crossings, shops), Microsoft and OSM building footprints, HeiGIT road widths | Guides for drawing. |
| **4. Imagery** | Esri current (2024, 0.46–0.5 m), Esri Wayback 2016 and 2014 (0.31 m, sharper but older), 12 cm drone photo (2020), OSM map | Backgrounds to trace over. Switch between Esri layers to find the clearest view. |

> The 12 cm drone photo covers **only the port area** (taken the day of the blast), so it shows almost no city sidewalks. Use the Esri layers for the streets.

## 3. How to map

**Before you start:** Settings → Options → Map Tools, or the snapping toolbar (magnet icon): snapping is already on for all layers at 12 px. Check that the **Esri imagery lines up with the building footprints**. Esri's positional error can be 5–8 m. If they're offset, trust the imagery for shapes and measure widths on the imagery itself.

**Sidewalks:** select `sidewalks` → toggle editing (pencil) → Add Polygon. Trace one sidewalk per block face, from building edge to curb. The form opens when you finish:
- `sw_id`, `length_m` (≈ half the perimeter), `area_m2`, `date_mapped` and `mapper` fill in automatically.
- Choose surface, condition, curb, ramp, continuity and imagery source from the dropdowns.
- **Width is not taken from the polygon.** It comes from the width lines below. Each sidewalk shows live summary fields: `width_median_m`, `width_min_m`, `clear_width_min_m`, `n_width_lines`, `n_obstructions`, `n_permanent_obstructions` and `obstructions_per_100m`. These are read-only and update as you add lines and points.

**Width measurements (transects):** select `width_measurements` → Add Line. Draw a line across the sidewalk, from building face to curb edge, perpendicular to the street. Do this every ~20 m, plus one at each pinch point.
- `total_width_m` is calculated from the line, and `sw_id` is filled from the sidewalk the line crosses.
- Type the **clear walkable width** (what's left after poles, trees, steps, etc.) in `clear_width_m`.
- Set `pinch_point` = Yes for the narrowest spot of each sidewalk.
- For widths measured on a photo, record the photo in `mapillary_image_id` and the camera height used for scale in `camera_height_m`.

**Obstructions:** select `obstructions` → Add Point on each object. Pick its type (parked car, generator, vendor, shop display, café furniture, pole, tree, bin, steps, etc.) and whether it's permanent. Then record:
- `occupied_width_m`: how much of the sidewalk width the object takes up.
- `clear_width_left_m`: the walkable width left beside it.
- `observed_date` and `observed_time` (HH:MM): **when the object was there**. They default to now, which is right for field visits. When coding from a Mapillary photo, copy the photo's `captured` date and `captured_time` instead. `time_of_day` (morning / midday / afternoon / evening / night) is calculated from the time. Cars, café tables and vendors change through the day, so this matters.
- `sw_id` is filled from the nearest sidewalk within 10 m.
- Most obstructions are only visible in street photos, so use Mapillary (step 4).

**Provenance and checking (all three layers):**
- `data_method`: how the record was made: hand-traced on imagery (default for sidewalks and widths), hand-coded from a Mapillary photo (default for obstructions), field visit, or automatic model output. For model output, also fill `model_version` and `confidence` (0–1).
- `validation_status` starts as *Not checked yet*. A second person reviews records and sets *validated*, *corrected* or *rejected*, plus `validated_by` and `validated_date`.
- Rejected records are left out of the sidewalk summary fields automatically.
- Aim to double-check at least 10% of segments and to field-measure a sample. These checks are what tell you how much to trust the imagery and photo measurements.

Save edits often (disk icon). All three layers are in `survey/sidewalk_survey.gpkg`: back that file up.

## 4. Add Mapillary street photos (free token needed)

1. Create a free account at https://www.mapillary.com.
2. Go to https://www.mapillary.com/dashboard/developers → **Register application** (any name, e.g. "sidewalk research"; tick "Read" access) → copy the **Client Token** (starts `MLY|`).
3. Open a terminal in `pilot_beirut\scripts` and run:
   ```
   python fetch_mapillary.py --token "MLY|your-token-here"
   ```
4. Re-open the project. Green dots are photos; purple squares are objects Mapillary detected automatically (poles, signs, benches, hydrants...).
5. **To view a photo:** Identify tool (i) → click a green dot → right-click the result → **Open photo in Mapillary**. Or use the Actions toolbar button, then click a dot.

Record the photo's `image_id` in `mapillary_image_id` when you use it as evidence. Each photo point also carries:
- `captured` (date) and `captured_time` (Beirut local HH:MM), to copy into an obstruction's observed date and time;
- camera details (`make`, `model`, `camera_parameters`, `altitude`, `computed_altitude`), for later automatic width measurement.

## 5. Map another area

```
python scripts/download_base_data.py --bbox W S E N --skip-ortho
python scripts/fetch_mapillary.py --token "MLY|..." --bbox W S E N
```
Example for Hamra: `--bbox 35.475 33.890 35.492 33.902`.

This **overwrites** the reference files in `data/`. Your survey layers are not touched. Zoom to the new area in QGIS.

## Folder contents

```
Beirut_sidewalk_pilot.qgs        QGIS project
survey/sidewalk_survey.gpkg      YOUR DATA (sidewalks, width_measurements, obstructions)
data/                            reference layers (GeoJSON, downloaded 6 Nov 2026)
imagery/beirut_port_2020-08-04_12cm.tif   drone photo (8-bit copy of the OpenAerialMap original)
scripts/download_base_data.py    re-downloads data/ (standard Python, no extra packages)
scripts/fetch_mapillary.py       downloads Mapillary photo points + detected objects
scripts/dev/make_gpkg.py         developer tool: recreates the EMPTY survey schema (refuses if layers have data)
scripts/dev/make_qgs.py          developer tool: rebuilds the .qgs project (forms, dropdowns, summary fields)
```

The dev tools need `pip install geopandas pyogrio pyproj`. Rebuilding the `.qgs` resets any styling changes you made in QGIS, so only do it to change the schema.

## Licences and credits

| Data | Licence | Credit line |
|---|---|---|
| OpenStreetMap | ODbL | © OpenStreetMap contributors |
| Microsoft building footprints | ODbL | Microsoft |
| HeiGIT road width/surface | HDX "Other" licence | HeiGIT / HDX |
| Drone orthophoto | CC BY 4.0 | Rabih El Zein (@rabzthecopter), ortho @GeoConor, via OpenAerialMap |
| Mapillary | Images CC BY-SA 4.0; derived data published outside OSM must be ODbL (source=Mapillary) | Mapillary contributors |
| Esri World Imagery / Wayback | Esri terms | Esri, Vantor (Maxar), Earthstar Geographics |

**Esri imagery:** viewing and manually tracing/measuring is allowed, and you may share the results. Do **not** bulk-download tiles or use them to train AI models. Use the drone photo and Mapillary images for any AI work.
