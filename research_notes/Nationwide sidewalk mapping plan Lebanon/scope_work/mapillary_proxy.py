"""Mapillary-coverage proxy per governorate from HeiGIT road-surface layer.
predicted_length = metres of each OSM way for which HeiGIT had Mapillary-image-based
surface predictions (imagery mostly 2017-2020). osm_length = way length. Ways are mapped
to governorates by joining osm_id to the HOT export (adm1 of the way).
Usage: python -I mapillary_proxy.py <hot_gpkg> <heigit_gpkg>
"""
import sqlite3, sys, collections
h = sqlite3.connect(sys.argv[1]); g = sqlite3.connect(sys.argv[2])
adm = {int(i[4:]): a for i, a in h.execute("select id, adm1_name from roads where id like 'way/%'")}
seen = {}
for oid, ol, pl, hw in g.execute('select osm_id, osm_length, predicted_length, highway from heigit_lbn_roadsurface_lines where osm_id is not null'):
    k = int(oid)
    ol = ol or 0; pl = pl or 0
    s = seen.setdefault(k, [0, 0, hw])
    s[0] = max(s[0], ol); s[1] = max(s[1], pl)
agg = collections.defaultdict(lambda: [0.0, 0.0])
for k, (ol, pl, hw) in seen.items():
    a = adm.get(k, 'unmatched'); agg[a][0] += ol; agg[a][1] += pl
print('| governorate | OSM way km (HeiGIT, <=2024-07) | km with Mapillary-based predictions | share |')
print('|---|---|---|---|')
T = [0, 0]
for a, (ol, pl) in sorted(agg.items(), key=lambda x: -x[1][1]):
    T[0] += ol; T[1] += pl
    print(f'| {a} | {ol/1000:,.0f} | {pl/1000:,.0f} | {100*pl/ol if ol else 0:.1f}% |')
print(f'| total | {T[0]/1000:,.0f} | {T[1]/1000:,.0f} | {100*T[1]/T[0]:.1f}% |')
