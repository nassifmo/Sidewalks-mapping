import sys, uuid
from xml.sax.saxutils import escape, quoteattr
from pyproj import CRS

OUT = sys.argv[1]

def srs(epsg):
    c = CRS.from_epsg(epsg)
    return f"""<spatialrefsys nativeFormat="Wkt">
  <wkt>{escape(c.to_wkt())}</wkt>
  <proj4>{escape(c.to_proj4())}</proj4>
  <authid>EPSG:{epsg}</authid>
  <description>{escape(c.name)}</description>
  <projectionacronym>{'utm' if epsg == 32636 else ('longlat' if epsg == 4326 else 'merc')}</projectionacronym>
  <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
  <geographicflag>{'true' if epsg == 4326 else 'false'}</geographicflag>
</spatialrefsys>"""

def opt(name, value):
    return f'<Option name={quoteattr(name)} value={quoteattr(str(value))} type="QString"/>'

def symbol(kind, **o):
    cls = {"fill": "SimpleFill", "line": "SimpleLine", "marker": "SimpleMarker"}[kind]
    opts = "".join(opt(k, v) for k, v in o.items())
    return f"""<renderer-v2 type="singleSymbol" symbollevels="0" enableorderby="0" forceraster="0" referencescale="-1">
  <symbols>
    <symbol type="{kind}" name="0" alpha="1" clip_to_extent="1" force_rhr="0" frame_rate="10" is_animated="0">
      <data_defined_properties><Option type="Map"><Option name="name" value="" type="QString"/><Option name="properties"/><Option name="type" value="collection" type="QString"/></Option></data_defined_properties>
      <layer class="{cls}" enabled="1" locked="0" pass="0">
        <Option type="Map">{opts}</Option>
      </layer>
    </symbol>
  </symbols>
  <rotation/><sizescale/>
</renderer-v2>"""

FILL = lambda fill, line, w=0.4: symbol("fill", color=fill, outline_color=line, outline_width=w, outline_width_unit="MM", style="solid", outline_style="solid", joinstyle="bevel")
LINE = lambda c, w, style="solid": symbol("line", line_color=c, line_width=w, line_width_unit="MM", line_style=style, capstyle="round", joinstyle="round")
DOT = lambda c, size, oc="35,35,35,255", shape="circle": symbol("marker", name=shape, color=c, outline_color=oc, outline_width=0.2, outline_width_unit="MM", size=size, size_unit="MM", outline_style="solid")

def valuemap(pairs):
    items = "".join(f'<Option type="Map">{opt(label, val)}</Option>' for label, val in pairs)
    return f'<editWidget type="ValueMap"><config><Option type="Map"><Option name="map" type="List">{items}</Option></Option></config></editWidget>'

YESNO = [("Yes", "yes"), ("No", "no"), ("Partly", "partial"), ("Unknown", "unknown")]
VM = {
    "side": [("North", "N"), ("South", "S"), ("East", "E"), ("West", "W"), ("Left (direction of OSM way)", "left"), ("Right (direction of OSM way)", "right")],
    "surface": [("Tiles / pavers", "tiles"), ("Concrete", "concrete"), ("Asphalt", "asphalt"), ("Stone", "stone"), ("Gravel / dirt", "unpaved"), ("Mixed", "mixed"), ("Unknown", "unknown")],
    "condition": [("Good", "good"), ("Fair", "fair"), ("Poor (cracks, missing tiles)", "poor"), ("Very poor / impassable", "very_poor"), ("Unknown", "unknown")],
    "has_curb": YESNO, "curb_ramp": YESNO, "continuous": YESNO,
    "source_imagery": [("Esri World Imagery (current)", "esri_current"), ("Esri Wayback 2016 (0.31 m)", "esri_wayback_2016"), ("Esri Wayback 2014 (0.31 m)", "esri_wayback_2014"), ("OpenAerialMap drone 2020 (12 cm)", "oam_drone_2020"), ("Mapillary photo", "mapillary"), ("Field visit", "field")],
    "method": [("Measured on satellite imagery", "imagery"), ("Measured on Mapillary photo", "mapillary"), ("Tape / laser in the field", "field")],
    "ob_type": [("Parked car", "parked_car"), ("Parked motorcycle / scooter", "parked_motorcycle"), ("Generator", "generator"), ("Street vendor / stall", "vendor"),
                ("Shop goods on display", "shop_display"), ("Café / restaurant tables & chairs", "cafe_furniture"), ("Kiosk", "kiosk"),
                ("Utility / electricity pole", "utility_pole"), ("Street light", "street_light"), ("Tree / tree pit", "tree"), ("Sign post", "sign_post"),
                ("Bollard", "bollard"), ("Planter / flower box", "planter"), ("Bin / dumpster", "bin"), ("Electrical cabinet / meter box", "cabinet"),
                ("Hanging wires / cables (low)", "wires"), ("Steps / ramp into a building", "private_steps"), ("Barrier / fence / valet sign", "barrier"),
                ("Construction / scaffolding", "construction"), ("Hole / broken pavement", "damage"), ("Other", "other")],
    "permanence": [("Permanent (fixed)", "permanent"), ("Temporary / movable", "temporary")],
    "source": [("Mapillary photo", "mapillary"), ("Satellite / aerial imagery", "imagery"), ("Field visit", "field")],
    "data_method": [("Traced/measured by hand on imagery", "manual_imagery"), ("Coded by hand from Mapillary photo", "manual_mapillary"),
                    ("Field visit (tape / laser / LiDAR)", "field"), ("Automatic (model output)", "auto_model")],
    "validation_status": [("Not checked yet", "unchecked"), ("Checked – correct", "validated"), ("Checked – corrected", "corrected"), ("Checked – rejected", "rejected")],
    "pinch_point": [("Yes – narrowest point", "yes"), ("No", "no")],
    "time_of_day": [("Morning (05–11)", "morning"), ("Midday (11–14)", "midday"), ("Afternoon (14–18)", "afternoon"), ("Evening (18–21)", "evening"), ("Night (21–05)", "night")],
}
HOUR = "to_int(left(\"observed_time\", 2))"
TIME_OF_DAY = (f"CASE WHEN \"observed_time\" IS NULL OR \"observed_time\" = '' THEN NULL "
               f"WHEN {HOUR} < 5 THEN 'night' WHEN {HOUR} < 11 THEN 'morning' WHEN {HOUR} < 14 THEN 'midday' "
               f"WHEN {HOUR} < 18 THEN 'afternoon' WHEN {HOUR} < 21 THEN 'evening' ELSE 'night' END")
SID = "left(regexp_replace(uuid(),'[{}-]',''),8)"
TODAY = "format_date(now(),'yyyy-MM-dd')"
DEFAULTS = {
    "sidewalks": {"sw_id": (SID, 0), "length_m": ("round($perimeter/2, 1)", 1), "area_m2": ("round($area,1)", 1), "date_mapped": (TODAY, 0), "mapper": ("@user_full_name", 0),
                  "data_method": ("'manual_imagery'", 0), "validation_status": ("'unchecked'", 0)},
    "width_measurements": {"wm_id": (SID, 0), "total_width_m": ("round($length,2)", 1), "sw_id": ("array_first(overlay_intersects('sidewalks', \"sw_id\"))", 0), "date_mapped": (TODAY, 0), "mapper": ("@user_full_name", 0),
                           "pinch_point": ("'no'", 0), "data_method": ("'manual_imagery'", 0), "validation_status": ("'unchecked'", 0)},
    "obstructions": {"ob_id": (SID, 0), "sw_id": ("array_first(overlay_nearest('sidewalks', \"sw_id\", max_distance:=10))", 0), "observed_date": (TODAY, 0),
                     "observed_time": ("format_date(now(),'HH:mm')", 0), "time_of_day": (TIME_OF_DAY, 1),
                     "mapper": ("@user_full_name", 0), "date_mapped": (TODAY, 0), "data_method": ("'manual_mapillary'", 0), "validation_status": ("'unchecked'", 0)},
}
ALIASES = {
    "length_m": "Approx. length (m, auto = half perimeter)", "area_m2": "Area (m², auto)", "total_width_m": "Total width (m, auto from line)",
    "clear_width_m": "Clear walkable width (m)", "curb_height_cm": "Curb height (cm, field only)",
    "clear_width_left_m": "Clear width left beside object (m)", "ob_type": "Obstruction type", "sw_id": "Sidewalk ID",
    "occupied_width_m": "Width taken by object (m)", "observed_date": "Observed date (photo capture or visit)",
    "observed_time": "Observed time HH:MM (photo capture or visit)", "time_of_day": "Time of day (auto from time)",
    "pinch_point": "Narrowest point of this sidewalk?", "camera_height_m": "Camera height used for scale (m, photo widths)",
    "data_method": "How produced", "model_version": "Model version (if automatic)", "confidence": "Confidence (0–1)",
    "validation_status": "Validation status", "validated_by": "Validated by", "validated_date": "Validated date",
}
# Read-only summary fields on each sidewalk, computed live from its width lines and obstructions.
def _agg(layer, fn, expr, extra=""):
    flt = "\"sw_id\" = attribute(@parent, 'sw_id')" + extra
    return f"aggregate(layer:='{layer}', aggregate:='{fn}', expression:={expr}, filter:={flt})"
SIDEWALK_VIRTUAL = [
    ("n_width_lines", "int", _agg("width_measurements", "count", "\"wm_id\"", " AND coalesce(\"validation_status\", '') <> 'rejected'")),
    ("width_median_m", "double", _agg("width_measurements", "median", "\"total_width_m\"", " AND coalesce(\"validation_status\", '') <> 'rejected'")),
    ("width_min_m", "double", _agg("width_measurements", "min", "\"total_width_m\"", " AND coalesce(\"validation_status\", '') <> 'rejected'")),
    ("clear_width_min_m", "double", _agg("width_measurements", "min", "\"clear_width_m\"", " AND coalesce(\"validation_status\", '') <> 'rejected'")),
    ("n_obstructions", "int", _agg("obstructions", "count", "\"ob_id\"", " AND coalesce(\"validation_status\", '') <> 'rejected'")),
    ("n_permanent_obstructions", "int", _agg("obstructions", "count", "\"ob_id\"", " AND \"permanence\" = 'permanent' AND coalesce(\"validation_status\", '') <> 'rejected'")),
    ("obstructions_per_100m", "double",
     "CASE WHEN \"length_m\" > 0 THEN round(100 * coalesce(" + _agg("obstructions", "count", "\"ob_id\"", " AND coalesce(\"validation_status\", '') <> 'rejected'") + ", 0) / \"length_m\", 1) END"),
]

def expression_fields(vf):
    t = {"int": ("2", "integer"), "double": ("6", "double")}
    return "<expressionfields>" + "".join(
        f'<field name="{n}" expression={quoteattr(e)} type="{t[k][0]}" typeName="{t[k][1]}" length="0" precision="0" subType="0" comment=""/>'
        for n, k, e in vf) + "</expressionfields>"

def form(layer, fields):
    TEXT = '<editWidget type="TextEdit"><config><Option/></config></editWidget>'
    fc = "".join(f'<field name="{f}">{valuemap(VM[f]) if f in VM else TEXT}</field>' for f in fields)
    al = "".join(f'<alias field="{f}" index="{i}" name={quoteattr(ALIASES.get(f, ""))}/>' for i, f in enumerate(fields))
    df = "".join(f'<default field="{f}" expression={quoteattr(DEFAULTS.get(layer, {}).get(f, ("", 0))[0])} applyOnUpdate="{DEFAULTS.get(layer, {}).get(f, ("", 0))[1]}"/>' for f in fields)
    return f"<fieldConfiguration>{fc}</fieldConfiguration><aliases>{al}</aliases><defaults>{df}</defaults>"

layers, tree = [], {}

def add_vector(group, name, source, geom, wkb, renderer, epsg=4326, fields=None, lname=None, extra=""):
    lid = f"{(lname or name).replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
    f = form(lname, fields) if fields else ""
    layers.append(f"""<maplayer type="vector" geometry="{geom}" wkbType="{wkb}" autoRefreshMode="Disabled" hasScaleBasedVisibilityFlag="0" readOnly="0" refreshOnNotifyEnabled="0" styleCategories="AllStyleCategories">
  <id>{lid}</id>
  <datasource>{escape(source)}</datasource>
  <layername>{escape(name)}</layername>
  <srs>{srs(epsg)}</srs>
  <provider encoding="UTF-8">ogr</provider>
  {renderer}
  {f}
  {extra}
  <blendMode>0</blendMode><featureBlendMode>0</featureBlendMode><layerOpacity>1</layerOpacity>
</maplayer>""")
    tree.setdefault(group, []).append((lid, name, source, "ogr", True))

def add_xyz(group, name, url, zmax, visible):
    lid = f"{name.split(' (')[0].replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
    enc = url.replace("{", "%7B").replace("}", "%7D")
    src = f"type=xyz&url={enc}&zmax={zmax}&zmin=0"
    layers.append(f"""<maplayer type="raster" autoRefreshMode="Disabled" hasScaleBasedVisibilityFlag="0" refreshOnNotifyEnabled="0" styleCategories="AllStyleCategories">
  <id>{lid}</id>
  <datasource>{escape(src)}</datasource>
  <layername>{escape(name)}</layername>
  <srs>{srs(3857)}</srs>
  <provider>wms</provider>
  <pipe>
    <rasterrenderer type="singlebandcolordata" band="1" opacity="1" alphaBand="-1" nodataColor=""><rasterTransparency/><minMaxOrigin><limits>None</limits><extent>WholeRaster</extent><statAccuracy>Estimated</statAccuracy><cumulativeCutLower>0.02</cumulativeCutLower><cumulativeCutUpper>0.98</cumulativeCutUpper><stdDevFactor>2</stdDevFactor></minMaxOrigin></rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation saturation="0" grayscaleMode="0" invertColors="0" colorizeOn="0" colorizeRed="255" colorizeGreen="128" colorizeBlue="128" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2" zoomedInResampler="bilinear"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</maplayer>""")
    tree.setdefault(group, []).append((lid, name, src, "wms", visible))

def add_tif(group, name, path):
    lid = f"drone_ortho_{uuid.uuid4().hex[:8]}"
    layers.append(f"""<maplayer type="raster" autoRefreshMode="Disabled" hasScaleBasedVisibilityFlag="0" refreshOnNotifyEnabled="0" styleCategories="AllStyleCategories">
  <id>{lid}</id>
  <datasource>{escape(path)}</datasource>
  <layername>{escape(name)}</layername>
  <srs>{srs(32636)}</srs>
  <provider>gdal</provider>
  <pipe>
    <rasterrenderer type="multibandcolor" redBand="1" greenBand="2" blueBand="3" alphaBand="4" opacity="1" nodataColor=""><rasterTransparency/><minMaxOrigin><limits>None</limits><extent>WholeRaster</extent><statAccuracy>Estimated</statAccuracy><cumulativeCutLower>0.02</cumulativeCutLower><cumulativeCutUpper>0.98</cumulativeCutUpper><stdDevFactor>2</stdDevFactor></minMaxOrigin></rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation saturation="0" grayscaleMode="0" invertColors="0" colorizeOn="0" colorizeRed="255" colorizeGreen="128" colorizeBlue="128" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2" zoomedInResampler="bilinear"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</maplayer>""")
    tree.setdefault(group, []).append((lid, name, path, "gdal", True))

GPKG = "./survey/sidewalk_survey.gpkg"
PROV = ["data_method","model_version","confidence","validation_status","validated_by","validated_date"]
TAIL = ["mapper","date_mapped","notes"]
F_SW = ["sw_id","street_name","side","surface","condition","has_curb","curb_height_cm","curb_ramp","continuous","length_m","area_m2","source_imagery","mapillary_image_id"] + PROV + TAIL
F_WM = ["wm_id","sw_id","total_width_m","clear_width_m","pinch_point","source_imagery","mapillary_image_id","camera_height_m"] + PROV + TAIL
F_OB = ["ob_id","sw_id","ob_type","permanence","occupied_width_m","clear_width_left_m","mapillary_image_id","observed_date","observed_time","time_of_day"] + PROV + TAIL

def graduated_lines(field, classes):
    """classes: list of (lower, upper, rgba, label)"""
    ranges = "".join(f'<range lower="{lo}" upper="{hi}" symbol="{i}" label={quoteattr(lab)} render="true"/>' for i, (lo, hi, c, lab) in enumerate(classes))
    syms = "".join(f"""<symbol type="line" name="{i}" alpha="1" clip_to_extent="1" force_rhr="0" frame_rate="10" is_animated="0"><layer class="SimpleLine" enabled="1" locked="0" pass="0"><Option type="Map">{opt("line_color", c)}{opt("line_width", 1.0)}{opt("line_width_unit", "MM")}{opt("line_style", "solid")}{opt("capstyle", "flat")}</Option></layer></symbol>""" for i, (lo, hi, c, lab) in enumerate(classes))
    return f"""<renderer-v2 type="graduatedSymbol" attr="{field}" graduatedMethod="GraduatedColor" symbollevels="0" enableorderby="0" forceraster="0" referencescale="-1"><ranges>{ranges}</ranges><symbols>{syms}</symbols><mode name="manual"/><rotation/><sizescale/></renderer-v2>"""


def add_paletted(group, name, path, entries, opacity=0.6):
    lid = f"ai_map_{uuid.uuid4().hex[:8]}"
    pal = "".join(f'<paletteEntry value="{v}" color="{c}" label={quoteattr(lab)} alpha="255"/>' for v, c, lab in entries)
    layers.append(f"""<maplayer type="raster" autoRefreshMode="Disabled" hasScaleBasedVisibilityFlag="0" refreshOnNotifyEnabled="0" styleCategories="AllStyleCategories">
  <id>{lid}</id>
  <datasource>{escape(path)}</datasource>
  <layername>{escape(name)}</layername>
  <srs>{srs(32636)}</srs>
  <provider>gdal</provider>
  <pipe>
    <rasterrenderer type="paletted" band="1" opacity="{opacity}" alphaBand="-1" nodataColor=""><rasterTransparency/><minMaxOrigin><limits>None</limits><extent>WholeRaster</extent><statAccuracy>Estimated</statAccuracy><cumulativeCutLower>0.02</cumulativeCutLower><cumulativeCutUpper>0.98</cumulativeCutUpper><stdDevFactor>2</stdDevFactor></minMaxOrigin><colorPalette>{pal}</colorPalette></rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation saturation="0" grayscaleMode="0" invertColors="0" colorizeOn="0" colorizeRed="255" colorizeGreen="128" colorizeBlue="128" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</maplayer>""")
    tree.setdefault(group, []).append((lid, name, path, "gdal", True))


G0 = "0. AI results (automatic)"
import os as _os
_HERE = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
if _os.path.exists(_os.path.join(_HERE, "ai_results", "width_transects.geojson")):
    add_vector(G0, "AI objects on/near sidewalks", "./ai_results/objects.geojson", "Point", "Point", DOT("255,0,200,255", 2.4, "255,255,255,255", "triangle"))
    _W = [(0, 1.2, "215,25,28,255", "< 1.2 m"), (1.2, 1.5, "253,174,97,255", "1.2–1.5 m"),
          (1.5, 2.0, "255,255,140,255", "1.5–2.0 m"), (2.0, 99, "26,150,65,255", "> 2.0 m")]
    if _os.path.exists(_os.path.join(_HERE, "ai_results", "width_edges.geojson")):
        add_vector(G0, "Widths, edge method, on-foot photos (most reliable)", "./ai_results/width_edges.geojson|subset=\"source\" = 'on-foot'",
                   "Line", "LineString", graduated_lines("width_m", _W))
        add_vector(G0, "Widths, edge method, car 360 photos (scale uncertain)", "./ai_results/width_edges.geojson|subset=\"source\" <> 'on-foot'",
                   "Line", "LineString", graduated_lines("width_m", _W))
        if '"confidence"' in open(_os.path.join(_HERE, "ai_results", "width_edges.geojson"), encoding="utf-8").read(4000):
            add_vector(G0, "Widths, high confidence only (predicted error is lowest)",
                       "./ai_results/width_edges.geojson|subset=\"confidence\" = 'high'",
                       "Line", "LineString", graduated_lines("width_m", _W))
    add_vector(G0, "AI sidewalk widths (every 2 m)", "./ai_results/width_transects.geojson", "Line", "LineString",
               graduated_lines("width_m", [(0, 1.2, "215,25,28,255", "< 1.2 m"), (1.2, 1.5, "253,174,97,255", "1.2–1.5 m"),
                                           (1.5, 2.0, "255,255,140,255", "1.5–2.0 m"), (2.0, 99, "26,150,65,255", "> 2.0 m")]))
    add_vector(G0, "AI sidewalk outlines", "./ai_results/sidewalks_ai.geojson", "Polygon", "Polygon", FILL("0,0,0,0", "255,140,0,255", 0.6))
    add_paletted(G0, "AI ground map (sidewalk / road / grass)", "./ai_results/sidewalk_map.tif",
                 [(1, "#ffaa00", "sidewalk"), (2, "#7f7fff", "road"), (3, "#7fcf6f", "grass / soil")])

G1, G2, G3, G4 = "1. Survey layers (edit these)", "2. Mapillary street photos", "3. Reference data", "4. Imagery"
add_vector(G1, "obstructions", f"{GPKG}|layername=obstructions", "Point", "Point", DOT("230,30,30,255", 3.2, "255,255,255,255", "diamond"), 32636, F_OB, "obstructions")
add_vector(G1, "width_measurements", f"{GPKG}|layername=width_measurements", "Line", "LineString", LINE("0,170,255,255", 0.8), 32636, F_WM, "width_measurements")
add_vector(G1, "sidewalks", f"{GPKG}|layername=sidewalks", "Polygon", "Polygon", FILL("255,200,0,90", "255,140,0,255", 0.5), 32636, F_SW, "sidewalks",
           extra=expression_fields(SIDEWALK_VIRTUAL))

ACTION = """<attributeactions><defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
<actionsetting type="5" name="Open photo in Mapillary" shortTitle="Open in Mapillary" action="[% &quot;open_url&quot; %]" capture="0" icon="" notificationMessage="" isEnabledOnlyWhenEditable="0" id="{ACTIONID}"><actionScope id="Feature"/><actionScope id="Canvas"/><actionScope id="Field"/></actionsetting></attributeactions>""".replace("ACTIONID", str(uuid.uuid4()))
add_vector(G2, "Mapillary detected objects", "./data/mapillary_map_features.geojson", "Point", "Point", DOT("170,0,255,255", 2.2, "255,255,255,255", "square"))
add_vector(G2, "Mapillary photo points", "./data/mapillary_images.geojson", "Point", "Point", DOT("5,203,99,255", 1.6, "255,255,255,255"), extra=ACTION)

add_vector(G3, "OSM street features (lamps, trees, crossings, shops)", "./data/osm_street_features.geojson", "Point", "Point", DOT("255,255,255,255", 1.4, "60,60,60,255"))
add_vector(G3, "OSM streets", "./data/osm_streets.geojson", "Line", "LineString", LINE("255,255,255,200", 0.35, "dash"))
add_vector(G3, "HeiGIT road width (arterials)", "./data/heigit_road_width.geojson", "Line", "LineString", LINE("0,255,255,160", 0.6))
add_vector(G3, "Microsoft building footprints (2026)", "./data/ms_buildings.geojson", "Polygon", "Polygon", FILL("0,0,0,0", "255,80,180,255", 0.3))
add_vector(G3, "OSM buildings", "./data/osm_buildings.geojson", "Polygon", "Polygon", FILL("0,0,0,0", "120,200,255,200", 0.25))

add_tif(G4, "Drone orthophoto 12 cm – Beirut port, 4 Aug 2020 (CC BY, OpenAerialMap)", "./imagery/beirut_port_2020-08-04_12cm.tif")
add_xyz(G4, "Esri World Imagery – current (Beirut: Aug–Nov 2024, 0.46–0.5 m)", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", 19, True)
add_xyz(G4, "Esri Wayback 2018-06 release (Beirut: Nov 2016, 0.31 m WorldView-3)", "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/11334/{z}/{y}/{x}", 19, False)
add_xyz(G4, "Esri Wayback 2017-01 release (Beirut: Sep 2014, 0.31 m WorldView-3)", "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/9486/{z}/{y}/{x}", 19, False)
add_xyz(G4, "OpenStreetMap basemap", "https://tile.openstreetmap.org/{z}/{y}/{x}.png", 19, False)

def tree_xml():
    out = []
    for g in ([G0] if G0 in tree else []) + [G1, G2, G3, G4]:
        items = "".join(f'<layer-tree-layer id="{lid}" name={quoteattr(n)} source={quoteattr(s)} providerKey="{p}" checked="{"Qt::Checked" if v else "Qt::Unchecked"}" expanded="0" legend_exp=""><customproperties><Option/></customproperties></layer-tree-layer>' for lid, n, s, p, v in tree[g])
        out.append(f'<layer-tree-group name={quoteattr(g)} checked="Qt::Checked" expanded="1" groupLayer=""><customproperties><Option/></customproperties>{items}</layer-tree-group>')
    return "".join(out)

# pilot bbox in UTM 36N
from pyproj import Transformer
t = Transformer.from_crs(4326, 32636, always_xy=True)
x0, y0 = t.transform(35.508, 33.884); x1, y1 = t.transform(35.530, 33.905)

qgs = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="Beirut sidewalk pilot" version="3.34.0-Prizren" saveUserFull="" saveUser="" saveDateTime="">
  <homePath path=""/>
  <title>Beirut sidewalk pilot</title>
  <transaction mode="Disabled"/>
  <projectFlags set=""/>
  <projectCrs>{srs(32636)}</projectCrs>
  <layer-tree-group><customproperties><Option/></customproperties>{tree_xml()}</layer-tree-group>
  <snapping-settings enabled="1" mode="2" type="1" tolerance="12" unit="1" intersection-snapping="0" self-snapping="0" scaleDependencyMode="0" minScale="0" maxScale="0"><individual-layer-settings/></snapping-settings>
  <relations/>
  <mapcanvas name="theMapCanvas" annotationsVisible="1">
    <units>meters</units>
    <extent><xmin>{x0:.1f}</xmin><ymin>{y0:.1f}</ymin><xmax>{x1:.1f}</xmax><ymax>{y1:.1f}</ymax></extent>
    <rotation>0</rotation>
    <destinationsrs>{srs(32636)}</destinationsrs>
    <rendermaptile>0</rendermaptile>
    <expressionContextScope/>
  </mapcanvas>
  <projectlayers>
{chr(10).join(layers)}
  </projectlayers>
  <properties>
    <Paths><Absolute type="bool">false</Absolute></Paths>
    <Measure><Ellipsoid type="QString">EPSG:7030</Ellipsoid></Measure>
    <Measurement><DistanceUnits type="QString">meters</DistanceUnits><AreaUnits type="QString">m2</AreaUnits></Measurement>
    <Digitizing><AvoidIntersectionsMode type="int">0</AvoidIntersectionsMode></Digitizing>
  </properties>
  <ellipsoid>EPSG:7030</ellipsoid>
</qgis>
"""
open(OUT, "w", encoding="utf-8").write(qgs)
print("wrote", OUT, len(qgs))
