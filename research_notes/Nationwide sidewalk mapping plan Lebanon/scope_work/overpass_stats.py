"""Compute OSM highway lengths for Lebanon by class, governorate and city.

Method: server-side Overpass `make stat ... sum(length())` (length in metres of
way geometry, geodesic). Ways crossing an area boundary are counted in full in
each area they touch (small double counting at borders). City figures use a
circular buffer (around:) around the city centre, since municipal boundaries in
OSM are incomplete.

Run: python -I overpass_stats.py   -> writes results_*.json/csv in this folder.
"""
import json, sys, time, urllib.parse, urllib.request, os

HERE = os.path.dirname(os.path.abspath(__file__))
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
]
UA = "sidewalk-scope-research/1.0"

CLASSES = ["motorway", "motorway_link", "trunk", "trunk_link", "primary",
           "primary_link", "secondary", "secondary_link", "tertiary",
           "tertiary_link", "residential", "unclassified", "living_street",
           "service", "pedestrian", "footway", "steps", "path", "track",
           "road", "cycleway"]


def run(q, tries=8):
    data = urllib.parse.urlencode({"data": q}).encode()
    wait = 10
    for i in range(tries):
        for ep in ENDPOINTS:
            try:
                req = urllib.request.Request(ep, data=data, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=650) as r:
                    txt = r.read().decode("utf-8")
                if txt.lstrip().startswith("{"):
                    return json.loads(txt), ep
                print("non-json from", ep, txt[:200], file=sys.stderr)
            except Exception as e:  # noqa
                print("err", ep, e, file=sys.stderr)
            time.sleep(3)
        time.sleep(wait)
        wait *= 2
    raise RuntimeError("all endpoints failed")


def stat_block(area_filter):
    """Overpass body: per-class length stats within an area/around filter."""
    parts = []
    for c in CLASSES:
        parts.append(
            f'way[highway={c}]{area_filter};'
            f'make stat cls="{c}",n=count(ways),m=sum(length());out;'
        )
    # sidewalk tagging baseline
    parts.append(f'way[highway][sidewalk]{area_filter};make stat cls="tag:sidewalk=*",n=count(ways),m=sum(length());out;')
    parts.append(f'way[highway][~"^sidewalk:(left|right|both)$"~"."]{area_filter};make stat cls="tag:sidewalk:side=*",n=count(ways),m=sum(length());out;')
    parts.append(f'way[highway=footway][footway=sidewalk]{area_filter};make stat cls="footway=sidewalk",n=count(ways),m=sum(length());out;')
    parts.append(f'way[highway=footway][footway=crossing]{area_filter};make stat cls="footway=crossing",n=count(ways),m=sum(length());out;')
    return "".join(parts)


def parse(res):
    out = {}
    for el in res.get("elements", []):
        t = el.get("tags", {})
        out[t["cls"]] = {"n": int(float(t.get("n", 0) or 0)),
                         "km": round(float(t.get("m", 0) or 0) / 1000, 1)}
    return out


def main():
    results = {}
    # 1. list governorates (admin_level 3 or 4)
    q = ('[out:json][timeout:180];area["ISO3166-1"="LB"][admin_level=2]->.lb;'
         'rel[boundary=administrative][admin_level~"^(3|4)$"](area.lb);out tags;')
    res, ep = run(q)
    govs = [(el["id"], el["tags"].get("name:en", el["tags"].get("name")), el["tags"].get("admin_level"))
            for el in res["elements"]]
    json.dump(govs, open(os.path.join(HERE, "governorates.json"), "w"), indent=1, ensure_ascii=False)
    print("governorates", govs, ep)

    # 2. national
    q = '[out:json][timeout:600];area["ISO3166-1"="LB"][admin_level=2]->.a;' + stat_block("(area.a)")
    res, ep = run(q)
    results["LEBANON"] = parse(res)
    print("national done", ep)
    json.dump(results, open(os.path.join(HERE, "results_lengths.json"), "w"), indent=1)

    # 3. per governorate
    for rid, name, lvl in govs:
        aid = 3600000000 + rid
        q = f'[out:json][timeout:600];area({aid})->.a;' + stat_block("(area.a)")
        try:
            res, ep = run(q)
            results[f"GOV:{name}"] = parse(res)
            print("gov done", name, ep)
        except Exception as e:
            print("gov fail", name, e)
        json.dump(results, open(os.path.join(HERE, "results_lengths.json"), "w"), indent=1)
        time.sleep(5)

    # 4. cities: circular buffers around centre (lat, lon, radius m)
    cities = {
        "Beirut (admin)": None,
        "Greater Beirut r=8km": (33.8886, 35.4955, 8000),
        "Tripoli r=5km": (34.4367, 35.8497, 5000),
        "Saida r=3km": (33.5606, 35.3756, 3000),
        "Jounieh r=3km": (33.9808, 35.6178, 3000),
        "Zahle r=3km": (33.8463, 35.9020, 3000),
        "Tyre r=2.5km": (33.2704, 35.2038, 2500),
        "Byblos r=2km": (34.1230, 35.6519, 2000),
        "Nabatieh r=2.5km": (33.3772, 35.4836, 2500),
        "Baalbek r=2.5km": (34.0047, 36.2110, 2500),
        "Batroun r=1.5km": (34.2553, 35.6581, 1500),
        "Aley r=2km": (33.8106, 35.5972, 2000),
        "Chtaura r=1.5km": (33.8167, 35.8500, 1500),
    }
    for name, v in cities.items():
        if v is None:
            q = ('[out:json][timeout:600];rel[boundary=administrative][name="بيروت"][admin_level~"^(4|8)$"];'
                 'map_to_area->.a;' + stat_block("(area.a)"))
        else:
            lat, lon, r = v
            q = '[out:json][timeout:600];' + stat_block(f"(around:{r},{lat},{lon})")
        try:
            res, ep = run(q)
            results[f"CITY:{name}"] = parse(res)
            print("city done", name, ep)
        except Exception as e:
            print("city fail", name, e)
        json.dump(results, open(os.path.join(HERE, "results_lengths.json"), "w"), indent=1)
        time.sleep(5)

    # CSV
    keys = list(results.keys())
    rows = ["class," + ",".join(f'"{k}"' for k in keys)]
    allc = CLASSES + ["tag:sidewalk=*", "tag:sidewalk:side=*", "footway=sidewalk", "footway=crossing"]
    for c in allc:
        rows.append(c + "," + ",".join(str(results[k].get(c, {}).get("km", "")) for k in keys))
    open(os.path.join(HERE, "results_lengths_km.csv"), "w", encoding="utf-8").write("\n".join(rows))
    print("ALL DONE")


if __name__ == "__main__":
    main()
