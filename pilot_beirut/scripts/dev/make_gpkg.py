"""(Re)create the EMPTY survey GeoPackage schema. Developer tool.

WARNING: overwrites the layers in the target file. Only run on a new/empty file.
Needs: pip install geopandas pyogrio
Usage: python make_gpkg.py ../../survey/sidewalk_survey.gpkg
"""
import sys
import pandas as pd
import geopandas as gpd
import pyogrio

out = sys.argv[1]
CRS = "EPSG:32636"  # WGS84 / UTM 36N, metres

# Provenance: how each record was produced and whether a person checked it.
PROVENANCE = [
    ("data_method", "str"),        # manual_imagery | manual_mapillary | field | auto_model
    ("model_version", "str"),      # e.g. "yolo11s-lb-v0.2" when data_method = auto_model
    ("confidence", "float64"),     # 0-1 model score, or mapper's own confidence
    ("validation_status", "str"),  # unchecked | validated | corrected | rejected
    ("validated_by", "str"),
    ("validated_date", "str"),
]
COMMON_TAIL = [("mapper", "str"), ("date_mapped", "str"), ("notes", "str")]


def layer(name, geom, cols):
    for l in pyogrio.list_layers(out) if __import__("os").path.exists(out) else []:
        if l[0] == name and pyogrio.read_info(out, layer=name)["features"] > 0:
            raise SystemExit(f"Refusing: layer {name} in {out} already has data.")
    df = pd.DataFrame({c: pd.Series(dtype=t) for c, t in cols})
    g = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries([], crs=CRS), crs=CRS)
    pyogrio.write_dataframe(g, out, layer=name, geometry_type=geom, driver="GPKG", append=False)


layer("sidewalks", "Polygon", [
    ("sw_id", "str"), ("street_name", "str"), ("side", "str"), ("surface", "str"), ("condition", "str"),
    ("has_curb", "str"), ("curb_height_cm", "Int64"), ("curb_ramp", "str"), ("continuous", "str"),
    ("length_m", "float64"), ("area_m2", "float64"),
    ("source_imagery", "str"), ("mapillary_image_id", "str"),
    *PROVENANCE, *COMMON_TAIL])

layer("width_measurements", "LineString", [
    ("wm_id", "str"), ("sw_id", "str"), ("total_width_m", "float64"), ("clear_width_m", "float64"),
    ("pinch_point", "str"),  # yes = narrowest spot of the segment
    ("source_imagery", "str"), ("mapillary_image_id", "str"),
    ("camera_height_m", "float64"),  # for photo-based widths: camera height used for scale
    *PROVENANCE, *COMMON_TAIL])

layer("obstructions", "Point", [
    ("ob_id", "str"), ("sw_id", "str"), ("ob_type", "str"), ("permanence", "str"),
    ("occupied_width_m", "float64"),     # width of sidewalk the object takes up
    ("clear_width_left_m", "float64"),   # walkable width left beside it
    ("mapillary_image_id", "str"),
    ("observed_date", "str"), ("observed_time", "str"),  # HH:MM local time (photo capture time or field visit)
    ("time_of_day", "str"),              # morning | midday | afternoon | evening | night
    *PROVENANCE, *COMMON_TAIL])

for l in pyogrio.list_layers(out):
    print(l[0], list(pyogrio.read_info(out, layer=l[0])["fields"]))
