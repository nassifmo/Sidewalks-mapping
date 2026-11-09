"""Download the Washington DC "answer key" for the benchmark area.

The AI pipeline is scored against these official layers. It never trains on them,
so the score is an honest estimate of how the pipeline will do in Lebanon.

Standard library only. Writes GeoJSON (EPSG:4326) to ../ground_truth/

Usage:
    python download_ground_truth.py                    # Adams Morgan default
    python download_ground_truth.py --bbox W S E N
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

# Adams Morgan, Washington DC: dense, mixed-use, cafés and shops at the sidewalk (~1.0 x 1.3 km)
DEFAULT_BBOX = (-77.048, 38.914, -77.036, 38.926)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "ground_truth")
UA = {"User-Agent": "sidewalk-research-benchmark/1.0"}
DC = "https://maps2.dcgis.dc.gov/dcgis/rest/services"

# name -> (service path, layer id, what it is used to score)
LAYERS = {
    # geometry
    "dc_sidewalks_2023":        ("DCGIS_DATA/Planimetrics_2023/MapServer", 11, "sidewalk polygons -> location, width, length"),
    "dc_curb_2023":             ("DCGIS_DATA/Planimetrics_2023/MapServer", 3, "curb lines -> curb presence, sidewalk outer edge"),
    "dc_buildings_2023":        ("DCGIS_DATA/Planimetrics_2023/MapServer", 1, "building footprints -> sidewalk inner edge"),
    "dc_roads_2023":            ("DCGIS_DATA/Planimetrics_2023/MapServer", 10, "road polygons"),
    "dc_obscured_areas_2023":   ("DCGIS_DATA/Planimetrics_2023/MapServer", 7, "areas where the official mapping itself is uncertain (exclude from scoring)"),
    "dc_street_blockfaces":     ("DCGIS_DATA/Transportation_WebMercator/MapServer", 164, "block faces -> per-side evaluation units"),
    # objects on / beside the sidewalk
    "dc_street_trees":          ("DDOT/UFATrees2/MapServer", 0, "tree"),
    "dc_street_lights":         ("DCGIS_DATA/Transportation_Signs_Signals_Lights_WebMercator/MapServer", 90, "street_light"),
    "dc_traffic_poles":         ("DCGIS_DATA/Transportation_Signs_Signals_Lights_WebMercator/MapServer", 94, "utility_pole / sign_post"),
    "dc_signal_cabinets":       ("DCGIS_DATA/Transportation_Signs_Signals_Lights_WebMercator/MapServer", 27, "cabinet"),
    "dc_sign_supports":         ("DDOT/Signworks/MapServer", 0, "sign_post"),
    "dc_parking_meters":        ("DDOT/DdotAssets/MapServer", 7, "parking meter (post)"),
    "dc_ada_barriers":          ("DCGIS_DATA/Transportation_ADA_WebMercator/MapServer", 1, "barriers in the public right of way"),
    "dc_ada_curb_ramps":        ("DCGIS_DATA/Transportation_ADA_WebMercator/MapServer", 3, "curb ramps"),
    "dc_ada_driveways":         ("DCGIS_DATA/Transportation_ADA_WebMercator/MapServer", 4, "driveways"),
    "dc_bus_stops":             ("DCGIS_DATA/Transportation_ADA_WebMercator/MapServer", 2, "bus stops"),
}

PROJECT_SIDEWALK = "https://sidewalk-dc.cs.washington.edu/v3/api/rawLabels"


def fetch_json(url, params=None, retries=4):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return json.loads(r.read())
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(2 ** i)


def arcgis_layer(service, layer_id, bbox):
    """All features of one ArcGIS REST layer intersecting bbox, paged, as GeoJSON features."""
    url = f"{DC}/{service}/{layer_id}/query"
    feats, offset = [], 0
    while True:
        res = fetch_json(url, {
            "where": "1=1", "geometry": ",".join(map(str, bbox)), "geometryType": "esriGeometryEnvelope",
            "inSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "outSR": 4326,
            "returnGeometry": "true", "f": "geojson", "resultOffset": offset, "resultRecordCount": 1000,
        })
        page = res.get("features", [])
        feats += page
        if len(page) < 1000 and not res.get("exceededTransferLimit") and not res.get("properties", {}).get("exceededTransferLimit"):
            break
        offset += len(page)
        if not page:
            break
    return feats


def save(name, feats, meta=None):
    with open(os.path.join(OUT, f"{name}.geojson"), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": feats, **({"metadata": meta} if meta else {})}, f)
    print(f"  {name:28s} {len(feats):6d} features")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"), default=DEFAULT_BBOX)
    b = tuple(ap.parse_args().bbox)
    os.makedirs(OUT, exist_ok=True)
    print("Benchmark area (W S E N):", b)

    manifest = {"bbox": b, "downloaded": time.strftime("%Y-%m-%d"), "layers": {}}
    for name, (service, lid, use) in LAYERS.items():
        try:
            feats = arcgis_layer(service, lid, b)
            save(name, feats)
            manifest["layers"][name] = {"source": f"{DC}/{service}/{lid}", "use": use, "count": len(feats)}
        except Exception as e:
            print(f"  {name:28s} FAILED: {e}")
            manifest["layers"][name] = {"source": f"{DC}/{service}/{lid}", "use": use, "error": str(e)}

    # Project Sidewalk crowd labels (obstacles, surface problems, curb ramps, no sidewalk)
    ps = fetch_json(PROJECT_SIDEWALK, {"bbox": ",".join(map(str, b)), "filetype": "geojson"})
    save("project_sidewalk_labels", ps.get("features", []))
    manifest["layers"]["project_sidewalk_labels"] = {"source": PROJECT_SIDEWALK, "use": "obstacles, surface problems, curb ramps, missing sidewalks", "count": len(ps.get("features", []))}

    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("Done. Licences: DC GIS open data (CC BY 4.0); Project Sidewalk data (see project terms).")


if __name__ == "__main__":
    main()
