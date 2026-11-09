"""Step 1 of the AI pipeline: download Mapillary street photos + camera poses for an area.

Same code for the DC benchmark and for Lebanon. Standard library only.

Usage:
    python fetch_images.py --token "MLY|..." --area dc_adams_morgan
    python fetch_images.py --token "MLY|..." --area beirut_pilot
    python fetch_images.py --token "MLY|..." --bbox W S E N --out ../my_area

Writes into ~/sidewalk-data/<area>/imagery/ (outside OneDrive; set SIDEWALK_DATA to change):
    images.geojson      one point per photo with pose, camera and capture metadata
    jpg/<id>.jpg        the photo (2048 px wide, perspective or 360 equirectangular)
Mapillary imagery is CC BY-SA 4.0 (credit "Mapillary contributors"); derived data published outside OSM must be ODbL.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

# Photos are large (GBs), so they live OUTSIDE OneDrive. Override with the SIDEWALK_DATA variable.
DATA_ROOT = os.environ.get("SIDEWALK_DATA", os.path.join(os.path.expanduser("~"), "sidewalk-data"))
AREAS = {
    "dc_adams_morgan": ((-77.048, 38.914, -77.036, 38.926), os.path.join(DATA_ROOT, "dc_adams_morgan")),
    "beirut_pilot": ((35.508, 33.884, 35.530, 33.905), os.path.join(DATA_ROOT, "beirut_pilot")),
}
API = "https://graph.mapillary.com"
CELL = 0.0025  # degrees per request tile (keeps responses under the API's per-call limits)
FIELDS = ("id,captured_at,geometry,computed_geometry,compass_angle,computed_compass_angle,computed_rotation,"
          "altitude,computed_altitude,camera_type,camera_parameters,make,model,width,height,is_pano,"
          "sequence,creator,quality_score,thumb_2048_url,thumb_original_url")


def get(path, params, token, retries=5):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {token}"})
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise SystemExit(f"Mapillary rejected the token ({e.code}): {e.read()[:200]!r}")
            if i == retries - 1:
                raise
        except urllib.error.URLError:
            if i == retries - 1:
                raise
        time.sleep(2 ** i)


def cells(b):
    x = b[0]
    while x < b[2] - 1e-9:
        y = b[1]
        while y < b[3] - 1e-9:
            yield (round(x, 6), round(y, 6), round(min(x + CELL, b[2]), 6), round(min(y + CELL, b[3]), 6))
            y += CELL
        x += CELL


def tiles_for_bbox(b, z=14):
    def tx(lon): return int((lon + 180) / 360 * 2 ** z)
    def ty(lat):
        r = math.radians(lat)
        return int((1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** z)
    for x in range(tx(b[0]), tx(b[2]) + 1):
        for y in range(ty(b[3]), ty(b[1]) + 1):
            yield z, x, y


def tile_to_lonlat(z, x, y, px, py, extent=4096):
    """px, py in tile units with y pointing DOWN."""
    n = 2 ** z
    lon = (x + px / extent) / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + py / extent) / n))))
    return lon, lat


def discover(b, token, min_year):
    """Find photo IDs via Mapillary's coverage vector tiles (the bbox search endpoint can return nothing)."""
    import mapbox_vector_tile  # pip install mapbox-vector-tile (included in the AI environment)
    found = {}
    for z, x, y in tiles_for_bbox(b):
        url = f"https://tiles.mapillary.com/maps/vtp/mly1_public/2/{z}/{x}/{y}?access_token={token}"
        with urllib.request.urlopen(url, timeout=180) as r:
            layers = mapbox_vector_tile.decode(r.read(), default_options={"y_coord_down": True})
        for ft in layers.get("image", {}).get("features", []):
            p = ft["properties"]
            px, py = ft["geometry"]["coordinates"]
            lon, lat = tile_to_lonlat(z, x, y, px, py)
            if not (b[0] <= lon <= b[2] and b[1] <= lat <= b[3]):
                continue
            if dt.datetime.fromtimestamp(p["captured_at"] / 1000).year < min_year:
                continue
            found[p["id"]] = {"id": p["id"], "lon": lon, "lat": lat, "captured_at": p["captured_at"],
                              "is_pano": bool(p.get("is_pano")), "foot": bool(p.get("foot")),
                              "quality": p.get("quality_score") or 0, "sequence": p.get("sequence_id")}
    return list(found.values())


def priority(c):
    """Best photos for sidewalks first: 360 panoramas (see both sidewalks side-on), then photos taken
    on foot (camera is ON the sidewalk), then car photos. Within a group: better quality, then newer."""
    group = 0 if c["is_pano"] else (1 if c["foot"] else 2)
    return (group, -round(c["quality"], 1), -c["captured_at"])


def thin(cands, spacing_m, max_images, min_quality=0.0):
    """Keep the best photo per ~spacing_m grid cell, then the best overall up to max_images."""
    cells_ = {}
    for c in sorted((c for c in cands if c["quality"] >= min_quality), key=priority):
        k = (round(c["lon"] * 111320 * math.cos(math.radians(c["lat"])) / spacing_m),
             round(c["lat"] * 111320 / spacing_m))
        cells_.setdefault(k, c)
    keep = sorted(cells_.values(), key=priority)
    return keep[:max_images] if max_images else keep


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).isoformat() if ms else None


def main():
    ap = argparse.ArgumentParser()
    tok_file = os.path.join(DATA_ROOT, "mapillary_token.txt")
    default_tok = os.environ.get("MLY_TOKEN") or (open(tok_file).read().strip() if os.path.exists(tok_file) else None)
    ap.add_argument("--token", default=default_tok, help="defaults to MLY_TOKEN or ~/sidewalk-data/mapillary_token.txt")
    ap.add_argument("--area", choices=AREAS)
    ap.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"))
    ap.add_argument("--out")
    ap.add_argument("--min-year", type=int, default=2016, help="skip older photos")
    ap.add_argument("--max-images", type=int, default=3000, help="cap (0 = all)")
    ap.add_argument("--spacing", type=float, default=4.0, help="keep ~one photo per this many metres")
    ap.add_argument("--pano-only", action="store_true", help="only 360 panoramas")
    ap.add_argument("--foot-only", action="store_true", help="only photos taken on foot (camera on the sidewalk)")
    ap.add_argument("--min-quality", type=float, default=0.0, help="Mapillary quality_score threshold (0-1)")
    ap.add_argument("--no-download", action="store_true", help="metadata only")
    a = ap.parse_args()
    if not a.token:
        sys.exit("Give --token or set MLY_TOKEN.")
    if a.area:
        bbox, out = AREAS[a.area]
        out = a.out or out          # --out overrides the area's default folder
    elif a.bbox and a.out:
        bbox, out = tuple(a.bbox), a.out
    else:
        sys.exit("Give --area, or --bbox and --out.")
    img_dir = os.path.join(out, "imagery")
    jpg_dir = os.path.join(img_dir, "jpg")
    os.makedirs(jpg_dir, exist_ok=True)

    cands = discover(bbox, a.token, a.min_year)
    if a.foot_only:
        cands = [c for c in cands if c["foot"]]
    if a.pano_only:
        cands = [c for c in cands if c["is_pano"]]
    print(f"{len(cands)} photos in the area (year >= {a.min_year})")
    n_p = sum(c["is_pano"] for c in cands); n_f = sum(c["foot"] and not c["is_pano"] for c in cands)
    print(f"  of which 360 panoramas: {n_p}, on-foot photos: {n_f}, car/other: {len(cands) - n_p - n_f}")
    cands = thin(cands, a.spacing, a.max_images, a.min_quality)
    print(f"{len(cands)} kept after thinning to one photo per ~{a.spacing} m (newest first)")

    def details(c):
        try:
            return get(str(c["id"]), {"fields": FIELDS}, a.token)
        except SystemExit:
            raise
        except Exception:
            return None
    imgs = []
    with ThreadPoolExecutor(8) as ex:
        for n, d in enumerate(ex.map(details, cands), 1):
            if d and "id" in d:
                imgs.append(d)
            if n % 100 == 0 or n == len(cands):
                sys.stdout.write(f"\rfetching photo details: {n}/{len(cands)}")
                sys.stdout.flush()
    print()
    if not imgs:
        sys.exit("Mapillary returned no photo details (token permissions?).")

    feats = []
    for im in imgs:
        g = im.get("computed_geometry") or im["geometry"]
        p = {k: im.get(k) for k in ("id", "sequence", "camera_type", "make", "model", "width", "height", "is_pano",
                                    "compass_angle", "computed_compass_angle", "altitude", "computed_altitude", "quality_score")}
        p["captured_at"] = iso(im.get("captured_at"))
        p["camera_parameters"] = im.get("camera_parameters")
        p["computed_rotation"] = im.get("computed_rotation")
        p["has_computed_pose"] = im.get("computed_geometry") is not None
        p["creator"] = (im.get("creator") or {}).get("username")
        feats.append({"type": "Feature", "geometry": g, "properties": p})
    with open(os.path.join(img_dir, "images.geojson"), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f)
    print("wrote imagery/images.geojson")

    if a.no_download:
        return

    def dl(im):
        path = os.path.join(jpg_dir, f"{im['id']}.jpg")
        url = im.get("thumb_original_url") if im.get("is_pano") else im.get("thumb_2048_url")
        url = url or im.get("thumb_2048_url")
        if os.path.exists(path) or not url:
            return 0
        for i in range(4):
            try:
                with urllib.request.urlopen(url, timeout=180) as r, open(path, "wb") as f:
                    f.write(r.read())
                return 1
            except Exception:
                time.sleep(2 ** i)
        return 0

    done = 0
    with ThreadPoolExecutor(8) as ex:
        for n, ok in enumerate(ex.map(dl, imgs), 1):
            done += ok
            if n % 50 == 0 or n == len(imgs):
                sys.stdout.write(f"\rdownloading: {n}/{len(imgs)}")
                sys.stdout.flush()
    print(f"\n{done} new photos saved to imagery/jpg/")


if __name__ == "__main__":
    main()
