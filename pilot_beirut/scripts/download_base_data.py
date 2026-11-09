"""Download free base data for a sidewalk-mapping study area.

Uses only the Python standard library. Writes GeoJSON files (EPSG:4326) to ../data
and the OpenAerialMap drone orthophoto to ../imagery.

Usage:
    python download_base_data.py                       # default Beirut pilot area
    python download_base_data.py --bbox W S E N        # any other area (lon/lat)
    python download_base_data.py --skip-ortho          # skip the 200 MB drone image
"""
import argparse
import csv
import gzip
import io
import json
import math
import os
import sys
import urllib.parse
import urllib.request

# Mar Mikhael - Gemmayzeh - north Achrafieh - Karantina edge (about 2 x 2.3 km)
DEFAULT_BBOX = (35.508, 33.884, 35.530, 33.905)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
IMAGERY = os.path.join(HERE, "..", "imagery")
UA = {"User-Agent": "sidewalk-research-download/1.0"}

OVERPASS = "https://overpass-api.de/api/interpreter"
MS_INDEX = "https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv"
HEIGIT_ROADS = "https://hot.storage.heigit.org/heigit-hdx-public/planet_road_data/heigit_LB_planet_roadsurface_lines.geojson"
OAM_ORTHO = "https://oin-hotosm-temp.s3.amazonaws.com/5f2bd274b0052e00067dbaed/0/5f2bd274b0052e00067dbaee.tif"


def fetch(url, data=None, timeout=300):
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def in_bbox(coords, b):
    """True if any coordinate of a (nested) coordinate list falls in the bbox."""
    if isinstance(coords[0], (int, float)):
        return b[0] <= coords[0] <= b[2] and b[1] <= coords[1] <= b[3]
    return any(in_bbox(c, b) for c in coords)


def write_fc(name, features):
    path = os.path.join(DATA, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False)
    print(f"  wrote {name}: {len(features)} features")


# ---------------------------------------------------------------- OpenStreetMap
def osm(b):
    s, w, n, e = b[1], b[0], b[3], b[2]
    q = f"""
[out:json][timeout:180];
(
  way["highway"]({s},{w},{n},{e});
  way["building"]({s},{w},{n},{e});
  node["highway"~"street_lamp|crossing|traffic_signals|bus_stop|stop"]({s},{w},{n},{e});
  node["barrier"]({s},{w},{n},{e});
  node["kerb"]({s},{w},{n},{e});
  node["natural"="tree"]({s},{w},{n},{e});
  node["amenity"~"bench|waste_basket|waste_disposal|recycling|parking_entrance|vending_machine|telephone"]({s},{w},{n},{e});
  node["power"~"pole|tower"]({s},{w},{n},{e});
  node["man_made"~"utility_pole|street_cabinet"]({s},{w},{n},{e});
  node["shop"]({s},{w},{n},{e});
  node["amenity"~"cafe|restaurant|bar|fast_food"]({s},{w},{n},{e});
);
out geom;
"""
    print("OpenStreetMap (Overpass)...")
    els = json.loads(fetch(OVERPASS, urllib.parse.urlencode({"data": q}).encode()))["elements"]
    streets, buildings, points = [], [], []
    for el in els:
        tags = el.get("tags", {})
        props = {"osm_id": f"{el['type']}/{el['id']}", **tags}
        if el["type"] == "node":
            points.append({"type": "Feature", "properties": props,
                           "geometry": {"type": "Point", "coordinates": [el["lon"], el["lat"]]}})
        elif el["type"] == "way" and "geometry" in el:
            coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
            if "building" in tags:
                if len(coords) >= 4 and coords[0] == coords[-1]:
                    buildings.append({"type": "Feature", "properties": props,
                                      "geometry": {"type": "Polygon", "coordinates": [coords]}})
            elif "highway" in tags:
                streets.append({"type": "Feature", "properties": props,
                                "geometry": {"type": "LineString", "coordinates": coords}})
    write_fc("osm_streets.geojson", streets)
    write_fc("osm_buildings.geojson", buildings)
    write_fc("osm_street_features.geojson", points)


# ------------------------------------------------- Microsoft building footprints
def quadkey(lon, lat, z=9):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    lr = math.radians(lat)
    y = int((1 - math.log(math.tan(lr) + 1 / math.cos(lr)) / math.pi) / 2 * n)
    return "".join(str(((x >> (i - 1)) & 1) + 2 * ((y >> (i - 1)) & 1)) for i in range(z, 0, -1))


def ms_buildings(b):
    print("Microsoft building footprints...")
    keys = {quadkey(x, y) for x in (b[0], b[2]) for y in (b[1], b[3])}
    rows = list(csv.DictReader(io.StringIO(fetch(MS_INDEX).decode())))
    urls = [r["Url"] for r in rows if r["Location"] == "Lebanon" and r["QuadKey"] in keys]
    feats = []
    for url in urls:
        print(f"  tile {url.split('quadkey=')[1].split('/')[0]}")
        for line in gzip.decompress(fetch(url)).decode().splitlines():
            ft = json.loads(line)
            if in_bbox(ft["geometry"]["coordinates"], b):
                feats.append({"type": "Feature", "properties": ft.get("properties", {}), "geometry": ft["geometry"]})
    write_fc("ms_buildings.geojson", feats)


# ----------------------------------------------- HeiGIT AI road width / surface
def heigit(b):
    print("HeiGIT road width & surface (arterial roads)...")
    fc = json.loads(fetch(HEIGIT_ROADS))
    feats = [f for f in fc["features"] if f.get("geometry") and in_bbox(f["geometry"]["coordinates"], b)]
    write_fc("heigit_road_width.geojson", feats)


# ------------------------------------------------- OpenAerialMap drone ortho
def ortho():
    path = os.path.join(IMAGERY, "beirut_port_2020-08-04_12cm_original_16bit.tif")
    if os.path.exists(os.path.join(IMAGERY, "beirut_port_2020-08-04_12cm.tif")) or (
            os.path.exists(path) and os.path.getsize(path) > 200_000_000):
        print("Drone orthophoto already downloaded.")
        return
    print("OpenAerialMap 12 cm drone orthophoto (~207 MB)...")
    req = urllib.request.Request(OAM_ORTHO, headers=UA)
    with urllib.request.urlopen(req, timeout=600) as r, open(path, "wb") as f:
        total = int(r.headers.get("Content-Length", 0))
        done = 0
        while chunk := r.read(1 << 20):
            f.write(chunk)
            done += len(chunk)
            if total:
                sys.stdout.write(f"\r  {done / total:6.1%}")
                sys.stdout.flush()
    print(f"\n  wrote {os.path.basename(path)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"), default=DEFAULT_BBOX)
    ap.add_argument("--skip-ortho", action="store_true")
    a = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(IMAGERY, exist_ok=True)
    b = tuple(a.bbox)
    print("Area (W S E N):", b)
    osm(b)
    ms_buildings(b)
    heigit(b)
    if not a.skip_ortho:
        ortho()
    print("Done.")


if __name__ == "__main__":
    main()
