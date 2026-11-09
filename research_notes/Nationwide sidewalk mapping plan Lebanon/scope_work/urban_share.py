"""Share of Lebanon road km in dense/urban population cells (pure stdlib).

Method (documented proxy for GHSL Degree of Urbanisation, *cell-level only*):
  * WorldPop 2020 1 km UN-adjusted population (lbn_ppp_2020_1km_Aggregated_UNadj.tif,
    https://hub.worldpop.org/geodata/summary?id=...; file from data.worldpop.org).
  * Cell density classes follow GHSL DEGURBA thresholds: >=1,500 inh/km2 ("urban-centre
    density"), 300-1,500 ("urban-cluster density", towns/suburbs), 50-300 (low-density
    rural), <50 (very low). Contiguity and minimum-population rules of DEGURBA are NOT
    applied (so small dense villages count as dense cells; isolated cells may be
    misclassified). Cell area is ~0.008333 deg; real area ~0.77 km2 at 34N, so density is
    computed as pop / true cell area.
  * Each road segment (vertex pair) of the HOT OSM export is assigned to the cell holding
    its midpoint; lengths by haversine.
Usage: python -I urban_share.py <worldpop_tif> <hot_roads_gpkg> <outdir>
"""
import struct, zlib, sys, math, sqlite3, json, os, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpkg_lengths import hav  # noqa: E402


def lzw_decode(data):
    # TIFF LZW (MSB-first, early change)
    out = bytearray()
    dic = [bytes([i]) for i in range(256)] + [b'', b'']
    bitpos, nbits, prev = 0, 9, None
    total = len(data) * 8
    while bitpos + nbits <= total:
        byte = bitpos >> 3
        chunk = int.from_bytes(data[byte:byte + 4].ljust(4, b'\0'), 'big')
        code = (chunk >> (32 - (bitpos & 7) - nbits)) & ((1 << nbits) - 1)
        bitpos += nbits
        if code == 256:
            dic = dic[:258]; nbits = 9; prev = None; continue
        if code == 257:
            break
        if prev is None:
            entry = dic[code]
        elif code < len(dic):
            entry = dic[code]; dic.append(prev + entry[:1])
        else:
            entry = prev + prev[:1]; dic.append(entry)
        out += entry
        prev = entry
        n = len(dic)
        if n + 1 >= 4096:
            nbits = 12
        elif n + 1 >= 2048:
            nbits = 12
        elif n + 1 >= 1024:
            nbits = 11
        elif n + 1 >= 512:
            nbits = 10
    return bytes(out)


def read_tiff(path):
    b = open(path, 'rb').read()
    bo = '<' if b[:2] == b'II' else '>'
    big = struct.unpack_from(bo + 'H', b, 2)[0] == 43
    TS = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8, 16: 8, 17: 8}
    TF = {1: 'B', 3: 'H', 4: 'I', 11: 'f', 12: 'd', 16: 'Q', 2: 's'}
    if big:
        off = struct.unpack_from(bo + 'Q', b, 8)[0]
        n = struct.unpack_from(bo + 'Q', b, off)[0]; p = off + 8; esz, inl = 20, 8
    else:
        off = struct.unpack_from(bo + 'I', b, 4)[0]
        n = struct.unpack_from(bo + 'H', b, off)[0]; p = off + 2; esz, inl = 12, 4
    tags = {}
    for i in range(n):
        e = p + i * esz
        if big:
            tag, typ, cnt = struct.unpack_from(bo + 'HHQ', b, e); vo = e + 12
        else:
            tag, typ, cnt = struct.unpack_from(bo + 'HHI', b, e); vo = e + 8
        sz = TS.get(typ, 1) * cnt
        if sz > inl:
            vo = struct.unpack_from(bo + ('Q' if big else 'I'), b, vo)[0]
        if typ == 2:
            tags[tag] = b[vo:vo + cnt]
        else:
            tags[tag] = struct.unpack_from(bo + TF[typ] * cnt, b, vo)
    W, H = tags[256][0], tags[257][0]
    comp = tags.get(259, (1,))[0]; pred = tags.get(317, (1,))[0]
    bps = tags[258][0]; fmt = tags.get(339, (1,))[0]
    sf = {(3, 32): 'f', (3, 64): 'd', (1, 8): 'B', (1, 16): 'H', (2, 16): 'h', (1, 32): 'I', (2, 32): 'i'}[(fmt, bps)]
    bpp = bps // 8
    tiled = 322 in tags
    if tiled:
        tw, th = tags[322][0], tags[323][0]; offs, cnts = tags[324], tags[325]
    else:
        tw, th = W, tags.get(278, (H,))[0]; offs, cnts = tags[273], tags[279]
    grid = [[0.0] * W for _ in range(H)]
    tiles_across = (W + tw - 1) // tw
    for k, (o, c) in enumerate(zip(offs, cnts)):
        raw = b[o:o + c]
        if comp == 5:
            raw = lzw_decode(raw)
        elif comp in (8, 32946):
            raw = zlib.decompress(raw)
        rows = len(raw) // (tw * bpp)
        if pred == 2:
            # libtiff horizontal differencing operates on integer words of size bps
            itf = {8: 'B', 16: 'H', 32: 'I', 64: 'Q'}[bps]; mod = 1 << bps
            ivals = list(struct.unpack(bo + itf * (tw * rows), raw[:tw * rows * bpp]))
            for r in range(rows):
                for x in range(1, tw):
                    ivals[r * tw + x] = (ivals[r * tw + x] + ivals[r * tw + x - 1]) % mod
            vals = struct.unpack(bo + sf * len(ivals), struct.pack(bo + itf * len(ivals), *ivals))
        elif pred == 3:
            arr = bytearray(raw)
            for r in range(rows):
                rs = r * tw * bpp
                for i in range(1, tw * bpp):
                    arr[rs + i] = (arr[rs + i] + arr[rs + i - 1]) & 0xFF
            vals = []
            for r in range(rows):
                rs = r * tw * bpp
                row = arr[rs:rs + tw * bpp]
                for x in range(tw):
                    by = bytes(row[j * tw + x] for j in range(bpp))  # big-endian byte planes
                    vals.append(struct.unpack('>' + sf, by)[0])
        else:
            vals = struct.unpack(bo + sf * (tw * rows), raw[:tw * rows * bpp])
        ty, tx = (k // tiles_across) * th, (k % tiles_across) * tw
        for r in range(rows):
            yy = ty + r
            if yy >= H:
                break
            for x in range(tw):
                xx = tx + x
                if xx < W:
                    grid[yy][xx] = vals[r * tw + x]
    scale = tags[33550]; tie = tags[33922]
    nodata = float(tags[42113].strip(b'\0')) if 42113 in tags else None
    return grid, W, H, tie[3], tie[4], scale[0], scale[1], nodata


def gpkg_coords(blob):
    flags = blob[3]
    env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(flags >> 1) & 7]
    off = 8 + env
    lines = []

    def rec(off):
        bo = '<' if blob[off] == 1 else '>'
        t = struct.unpack_from(bo + 'I', blob, off + 1)[0] % 1000; off += 5
        if t == 2:
            n = struct.unpack_from(bo + 'I', blob, off)[0]; off += 4
            pts = struct.unpack_from(bo + 'd' * (2 * n), blob, off); off += 16 * n
            lines.append(pts); return off
        if t == 5:
            ng = struct.unpack_from(bo + 'I', blob, off)[0]; off += 4
            for _ in range(ng):
                off = rec(off)
            return off
        return None
    rec(off)
    return lines


def main(tif, hot, outdir):
    grid, W, H, x0, y0, dx, dy, nod = read_tiff(tif)
    classes = [(1500, 'dense >=1500/km2'), (300, 'urban-cluster 300-1500/km2'),
               (50, 'rural 50-300/km2'), (-1e9, 'very low <50/km2')]

    def cls_of(lon, lat):
        c = int((lon - x0) / dx); r = int((y0 - lat) / dy)
        if 0 <= r < H and 0 <= c < W:
            v = grid[r][c]
            if nod is not None and (v == nod or v < -1e30):
                return 'very low <50/km2', 0
            area = (dx * 111.32 * math.cos(math.radians(lat))) * (dy * 110.57)
            d = v / area
            for th, name in classes:
                if d >= th:
                    return name, d
        return 'outside raster', 0
    # population by class
    popc = collections.defaultdict(float); cellc = collections.Counter()
    for r in range(H):
        for c in range(W):
            v = grid[r][c]
            if nod is not None and (v == nod or v < -1e30) or v <= 0:
                continue
            lat = y0 - (r + 0.5) * dy; lon = x0 + (c + 0.5) * dx
            n, _ = cls_of(lon, lat)
            popc[n] += v; cellc[n] += 1
    con = sqlite3.connect(hot)
    res = collections.defaultdict(lambda: collections.defaultdict(float))
    res_adm1 = collections.defaultdict(lambda: collections.defaultdict(float))
    res_adm2 = collections.defaultdict(lambda: collections.defaultdict(float))
    SW = {'trunk', 'trunk_link', 'primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary',
          'tertiary_link', 'residential', 'unclassified', 'living_street', 'pedestrian', 'road'}
    for geom, hw, a1, a2 in con.execute('select geom,highway,adm1_name,adm2_name from roads'):
        for pts in gpkg_coords(geom):
            for i in range(1, len(pts) // 2):
                lo1, la1, lo2, la2 = pts[2 * i - 2], pts[2 * i - 1], pts[2 * i], pts[2 * i + 1]
                L = hav(lo1, la1, lo2, la2)
                n, _ = cls_of((lo1 + lo2) / 2, (la1 + la2) / 2)
                res[n][hw] += L
                if hw in SW:
                    res_adm1[a1][n] += L
                    res_adm2[f"{a1} / {a2}"][n] += L
    out = {'pop_by_class': dict(popc), 'cells_by_class': dict(cellc),
           'road_km_by_density_class_and_highway': {k: dict(v) for k, v in res.items()},
           'sidewalk_relevant_km_by_adm1_and_class': {k: dict(v) for k, v in res_adm1.items()},
           'sidewalk_relevant_km_by_adm2_and_class': {k: dict(v) for k, v in res_adm2.items()},
           'raster': {'W': W, 'H': H, 'x0': x0, 'y0': y0, 'dx': dx, 'dy': dy, 'nodata': nod}}
    json.dump(out, open(os.path.join(outdir, 'urban_share.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('pop total', round(sum(popc.values())), {k: round(v) for k, v in popc.items()})


if __name__ == '__main__':
    main(*sys.argv[1:4])
