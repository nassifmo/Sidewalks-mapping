"""Offline length statistics for Lebanon roads (pure stdlib).

Inputs (downloaded 2026-11-06):
  data_hot/roads.gpkg  - HOT/HDX "Roads of Lebanon" export, OSM snapshot 2026-11-02
                         (https://data.humdata.org/dataset/hotosm_lbn_roads); every feature
                         carries adm1/adm2/adm3 P-codes (fieldmaps.io COD edge-matched).
  data_heigit/heigit_lbn_roadsurface_lines.gpkg - HeiGIT road-surface dataset
                         (https://data.humdata.org/dataset/lebanon-road-surface-data) with
                         `urban` flag (GHS-SMOD/GHS urban layer 2019), `urban_area` name and
                         `n_of_predictions_used` (# Mapillary images used => proxy for
                         Mapillary coverage at HeiGIT processing time).
Lengths: haversine sum over vertices, R = 6371.0088 km. Polygons (area:highway, pedestrian
squares) are ignored for length. Ways are clipped by HOT to the country polygon only.

Usage: python -I gpkg_lengths.py <hot_gpkg> <heigit_gpkg> <outdir>
"""
import sqlite3, struct, math, sys, json, os, collections

R = 6371.0088


def hav(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def wkb_len(b, off=0):
    """return (length_km, new_offset) for WKB geometry at offset."""
    bo = '<' if b[off] == 1 else '>'
    (t,) = struct.unpack_from(bo + 'I', b, off + 1)
    off += 5
    dims = 2
    base = t % 1000
    if t >= 1000:
        dims = 3 if (t // 1000) in (1, 2) else 4
    if t & 0x80000000:
        dims = 3
        base = t & 0xFF
    if base == 1:
        return 0.0, off + 8 * dims
    if base == 2:
        (n,) = struct.unpack_from(bo + 'I', b, off); off += 4
        pts = struct.unpack_from(bo + 'd' * (n * dims), b, off); off += 8 * n * dims
        L = 0.0
        for i in range(1, n):
            L += hav(pts[(i - 1) * dims], pts[(i - 1) * dims + 1], pts[i * dims], pts[i * dims + 1])
        return L, off
    if base == 3:  # polygon: skip
        (nr,) = struct.unpack_from(bo + 'I', b, off); off += 4
        for _ in range(nr):
            (n,) = struct.unpack_from(bo + 'I', b, off); off += 4 + 8 * n * dims
        return 0.0, off
    if base in (4, 5, 6, 7):
        (ng,) = struct.unpack_from(bo + 'I', b, off); off += 4
        L = 0.0
        for _ in range(ng):
            l, off = wkb_len(b, off)
            L += l
        return L, off
    raise ValueError(t)


def gpkg_len(blob):
    flags = blob[3]
    env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(flags >> 1) & 7]
    return wkb_len(blob, 8 + env)[0]


def nested():
    return collections.defaultdict(lambda: collections.defaultdict(float))


def main(hot, heig, outdir):
    out = {}
    # ---------- HOT export ----------
    c = sqlite3.connect(hot)
    by_cls = collections.defaultdict(float)
    by_adm1 = nested(); by_adm2 = nested(); by_adm3 = nested()
    adm2_parent = {}
    way_adm = {}
    for geom, oid, hw, a1, a2, a2p, a3, a3p in c.execute(
            "select geom,id,highway,adm1_name,adm2_name,adm2_pcode,adm3_name,adm3_pcode from roads"):
        L = gpkg_len(geom)
        by_cls[hw] += L
        by_adm1[a1][hw] += L
        by_adm2[f"{a2} ({a2p})"][hw] += L
        adm2_parent[f"{a2} ({a2p})"] = a1
        by_adm3[f"{a3}|{a3p}|{a2}"][hw] += L
        if oid and oid.startswith('way/'):
            way_adm[int(oid[4:])] = a1
    out['hot_by_class'] = dict(by_cls)
    out['hot_by_adm1'] = {k: dict(v) for k, v in by_adm1.items()}
    out['hot_by_adm2'] = {k: dict(v) for k, v in by_adm2.items()}
    out['adm2_parent'] = adm2_parent
    out['hot_by_adm3'] = {k: dict(v) for k, v in by_adm3.items()}

    # ---------- HeiGIT (urban flag + Mapillary predictions) ----------
    c = sqlite3.connect(heig)
    urb = nested()          # urban flag -> class -> km
    urb_adm1 = nested()     # adm1|urban -> class -> km
    ua = nested()           # urban_area -> class -> km
    mly = nested()          # class|urban -> {'km','km_mly'}
    mly_adm1 = nested()
    mly_ua = nested()
    dl_ts = collections.Counter()
    for geom, u, uan, oid, hw, npred, ts in c.execute(
            'select geom,urban,urban_area,osm_id,highway,n_of_predictions_used,DL_mean_timestamp '
            'from heigit_lbn_roadsurface_lines'):
        L = gpkg_len(geom)
        uk = 'urban' if (u or 0) >= 1 else 'rural'
        a1 = way_adm.get(int(oid)) if oid is not None else None
        a1 = a1 or 'unmatched'
        urb[uk][hw] += L
        urb_adm1[f"{a1}|{uk}"][hw] += L
        if uk == 'urban':
            ua[uan or 'none'][hw] += L
        has = (npred or 0) > 0
        mly[f"{hw}|{uk}"]['km'] += L
        mly_adm1[f"{a1}|{uk}"]['km'] += L
        if has:
            mly[f"{hw}|{uk}"]['km_mly'] += L
            mly_adm1[f"{a1}|{uk}"]['km_mly'] += L
            if ts:
                dl_ts[ts[:4]] += L
        if uk == 'urban':
            mly_ua[uan or 'none']['km'] += L
            if has:
                mly_ua[uan or 'none']['km_mly'] += L
    out['heigit_urban'] = {k: dict(v) for k, v in urb.items()}
    out['heigit_urban_adm1'] = {k: dict(v) for k, v in urb_adm1.items()}
    out['heigit_urban_area'] = {k: dict(v) for k, v in ua.items()}
    out['heigit_mly'] = {k: dict(v) for k, v in mly.items()}
    out['heigit_mly_adm1'] = {k: dict(v) for k, v in mly_adm1.items()}
    out['heigit_mly_ua'] = {k: dict(v) for k, v in mly_ua.items()}
    out['heigit_mly_year_km'] = dict(dl_ts)
    json.dump(out, open(os.path.join(outdir, 'gpkg_lengths.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('done')


if __name__ == '__main__':
    main(*sys.argv[1:4])
