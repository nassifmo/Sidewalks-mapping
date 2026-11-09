"""Download Mapillary street-level image points and auto-detected map features.

Needs a free Mapillary access token:
  1. Sign up / log in at https://www.mapillary.com
  2. Go to https://www.mapillary.com/dashboard/developers -> "Register application"
  3. Copy the "Client Token" (starts with MLY|...)

Usage (standard library only):
    python fetch_mapillary.py --token "MLY|..."
    python fetch_mapillary.py --token "MLY|..." --bbox 35.475 33.890 35.492 33.902   # e.g. Hamra
    (or set the environment variable MLY_TOKEN instead of --token)

Writes to ../data:
    mapillary_images.geojson        one point per photo, with capture date and a link to open it
    mapillary_map_features.geojson  poles, signs, benches, hydrants, bins... detected by Mapillary

Mapillary imagery is CC BY-SA 4.0: credit "Mapillary contributors". Derived data published outside OSM must be ODbL.
"""
import argparse
import datetime as dt
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BBOX = (35.508, 33.884, 35.530, 33.905)  # same pilot area as download_base_data.py
CELL = 0.005  # degrees; keeps each request well under Mapillary's per-request limits
API = "https://graph.mapillary.com"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def get(path, params, token, retries=4):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {token}"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:300]
            if e.code in (401, 403):
                raise SystemExit(f"Mapillary rejected the token ({e.code}): {body}")
            if attempt == retries - 1:
                raise SystemExit(f"Mapillary error {e.code}: {body}")
        except urllib.error.URLError:
            if attempt == retries - 1:
                raise
        time.sleep(2 ** attempt)


def cells(b):
    x = b[0]
    while x < b[2]:
        y = b[1]
        while y < b[3]:
            yield (round(x, 6), round(y, 6), round(min(x + CELL, b[2]), 6), round(min(y + CELL, b[3]), 6))
            y += CELL
        x += CELL


try:
    from zoneinfo import ZoneInfo
    BEIRUT = ZoneInfo("Asia/Beirut")
except Exception:  # Windows without the tzdata package: fall back to UTC
    BEIRUT = None


def local_hhmm(ms):
    """Capture time as HH:MM Beirut local time (for the obstructions 'observed_time' field)."""
    if not ms:
        return None
    t = dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)
    return t.astimezone(BEIRUT).strftime("%H:%M") if BEIRUT else t.strftime("%H:%M UTC")


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d") if ms else None


def fetch_all(path, fields, b, token):
    out = {}
    cs = list(cells(b))
    for i, c in enumerate(cs, 1):
        print(f"  {path}: cell {i}/{len(cs)}", end="\r")
        res = get(path, {"fields": fields, "bbox": ",".join(map(str, c)), "limit": 2000}, token)
        for item in res.get("data", []):
            out[item["id"]] = item
    print(f"  {path}: {len(out)} found{' ' * 20}")
    return list(out.values())


def save(name, feats):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f)
    print(f"  wrote {name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=os.environ.get("MLY_TOKEN"))
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"), default=DEFAULT_BBOX)
    a = ap.parse_args()
    if not a.token:
        raise SystemExit("Give your Mapillary client token with --token or the MLY_TOKEN variable (see top of file).")
    os.makedirs(DATA, exist_ok=True)
    b = tuple(a.bbox)
    print("Area (W S E N):", b)

    imgs = fetch_all("images", "id,captured_at,compass_angle,computed_compass_angle,geometry,"
                     "computed_geometry,camera_type,is_pano,sequence,creator,"
                     "altitude,computed_altitude,camera_parameters,make,model,width,height", b, a.token)
    save("mapillary_images.geojson", [{
        "type": "Feature",
        "geometry": i.get("computed_geometry") or i["geometry"],
        "properties": {
            "image_id": i["id"],
            "captured": iso(i.get("captured_at")),
            "year": int(iso(i["captured_at"])[:4]) if i.get("captured_at") else None,
            "compass": i.get("computed_compass_angle", i.get("compass_angle")),
            "captured_time": local_hhmm(i.get("captured_at")),
            "camera_type": i.get("camera_type"),
            "make": i.get("make"),
            "model": i.get("model"),
            "img_width": i.get("width"),
            "img_height": i.get("height"),
            "camera_parameters": ",".join(f"{v:.6g}" for v in i["camera_parameters"]) if i.get("camera_parameters") else None,
            "altitude": i.get("altitude"),
            "computed_altitude": i.get("computed_altitude"),
            "is_pano": i.get("is_pano"),
            "sequence": i.get("sequence"),
            "creator": (i.get("creator") or {}).get("username"),
            "open_url": f"https://www.mapillary.com/app/?pKey={i['id']}&focus=photo",
        }} for i in imgs])

    feats = fetch_all("map_features", "id,object_value,object_type,geometry,first_seen_at,last_seen_at", b, a.token)
    save("mapillary_map_features.geojson", [{
        "type": "Feature",
        "geometry": f["geometry"],
        "properties": {
            "feature_id": f["id"],
            "object_value": f.get("object_value"),
            "object_type": f.get("object_type"),
            "first_seen": iso(f.get("first_seen_at")),
            "last_seen": iso(f.get("last_seen_at")),
        }} for f in feats])
    print("Done. Reload the Mapillary layers in QGIS (or reopen the project).")


if __name__ == "__main__":
    main()
