"""Derive planning tables from gpkg_lengths.json + urban_share.json (+ results_lengths.json).
Usage: python -I summarize.py <scope_work_dir>   -> writes summary_tables.md
Security buckets are planning assumptions (see national_scope.md), at district (qada) level:
  A  south-of-Litani / border belt districts: Sour, Bent Jbeil, Marjaayoun, Hasbaya
  B  high-risk / conditional: El Nabatieh district, Baalbek, El Hermel districts,
     Dahiyeh proxy (cadastres Chiyah[Baabda], Haret Hreik, Tahouitat El Ghadir)
  C  all other districts
"""
import json, sys, os

d = sys.argv[1]
U = json.load(open(os.path.join(d, 'urban_share.json'), encoding='utf-8'))
G = json.load(open(os.path.join(d, 'gpkg_lengths.json'), encoding='utf-8'))
C = ['dense >=1500/km2', 'urban-cluster 300-1500/km2', 'rural 50-300/km2', 'very low <50/km2']
SW = ['trunk', 'trunk_link', 'primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary',
      'tertiary_link', 'residential', 'unclassified', 'living_street', 'pedestrian', 'road']
A = {'Sour', 'Bent Jbeil', 'Marjaayoun', 'Hasbaya'}
B = {'El Nabatieh', 'Baalbek', 'El Hermel'}
lines = []
P = lines.append

# 1 density class x highway (all classes)
P('## T1 Road km by WorldPop-density class and highway class (HOT export 2026-11-02)')
hw_show = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'unclassified',
           'living_street', 'service', 'pedestrian', 'footway', 'steps', 'path', 'track']
P('| class | ' + ' | '.join(C) + ' | total |')
P('|---' * (len(C) + 2) + '|')
R = U['road_km_by_density_class_and_highway']
for h in hw_show:
    vals = [R.get(c, {}).get(h, 0) + R.get(c, {}).get(h + '_link', 0) for c in C]
    P(f'| {h} | ' + ' | '.join(f'{v:,.0f}' for v in vals) + f' | {sum(vals):,.0f} |')
sw_by = [sum(R.get(c, {}).get(h, 0) for h in SW) for c in C]
P('| **sidewalk-relevant (trunk..tertiary+links, residential, unclassified, living, pedestrian, road)** | '
  + ' | '.join(f'{v:,.0f}' for v in sw_by) + f' | {sum(sw_by):,.0f} |')
allk = [sum(R.get(c, {}).values()) for c in C]
P('| all highway=* | ' + ' | '.join(f'{v:,.0f}' for v in allk) + f' | {sum(allk):,.0f} |')
P('')
P('Population (WorldPop 2020 UNadj) by class: ' + ', '.join(f"{c}: {U['pop_by_class'].get(c,0)/1e6:.2f} M" for c in C))
P('')

# 2 adm1
P('## T2 Sidewalk-relevant centreline km by governorate (COD 8-governorate set) and density class')
P('| governorate | dense | urban-cluster | rural | very low | total | dense+cluster block-face km (x2) |')
P('|---|---|---|---|---|---|---|')
for k, v in sorted(U['sidewalk_relevant_km_by_adm1_and_class'].items(), key=lambda x: -sum(x[1].values())):
    vals = [v.get(c, 0) for c in C]
    P(f'| {k} | ' + ' | '.join(f'{x:,.0f}' for x in vals) + f' | {sum(vals):,.0f} | {2*(vals[0]+vals[1]):,.0f} |')
P('')

# 3 adm2 + buckets
P('## T3 Sidewalk-relevant centreline km by district (qada) and density class, with security bucket')
P('| governorate / district | bucket | dense | urban-cluster | rural | very low | total |')
P('|---|---|---|---|---|---|---|')
buck = {'A': [0] * 4, 'B': [0] * 4, 'C': [0] * 4}
for k, v in sorted(U['sidewalk_relevant_km_by_adm2_and_class'].items(), key=lambda x: -(x[1].get(C[0], 0) + x[1].get(C[1], 0))):
    dist = k.split(' / ')[-1]
    b = 'A' if dist in A else 'B' if dist in B else 'C'
    vals = [v.get(c, 0) for c in C]
    for i in range(4):
        buck[b][i] += vals[i]
    P(f'| {k} | {b} | ' + ' | '.join(f'{x:,.0f}' for x in vals) + f' | {sum(vals):,.0f} |')
P('')
# Dahiyeh proxy (no density split available at adm3 -> centreline totals)
dah = ['Chiyah|21111|Baabda', 'Haret Hreik|21144|Baabda', 'Tahouitat El Ghadir|21188|Baabda']
dk = sum(sum(G['hot_by_adm3'][x].get(h, 0) for h in SW) for x in dah)
P(f'Dahiyeh proxy (cadastres {", ".join(x.split("|")[0] for x in dah)}): {dk:,.0f} km sidewalk-relevant centreline (all assumed dense; moved from C to B below).')
buck['C'][0] -= dk; buck['B'][0] += dk
P('')
P('## T4 Security buckets: sidewalk-relevant centreline km')
P('| bucket | dense | urban-cluster | rural | very low | dense+cluster | dense+cluster block-face (x2) |')
P('|---|---|---|---|---|---|---|')
for b, v in buck.items():
    P(f'| {b} | ' + ' | '.join(f'{x:,.0f}' for x in v) + f' | {v[0]+v[1]:,.0f} | {2*(v[0]+v[1]):,.0f} |')
P('')

# 5 Overpass results if present
rp = os.path.join(d, 'results_lengths.json')
if os.path.exists(rp):
    O = json.load(open(rp))
    keys = list(O.keys())
    cls = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'unclassified',
           'living_street', 'service', 'pedestrian', 'footway', 'steps', 'path', 'track']
    P('## T5 Overpass live counts (km) by area (ways touching area counted in full; links merged)')
    P('| area | ' + ' | '.join(cls) + ' | sidewalk-relevant | ways w/ sidewalk tags (km) | footway=sidewalk km |')
    P('|---' * (len(cls) + 4) + '|')
    for k in keys:
        v = O[k]
        g = lambda c: v.get(c, {}).get('km', 0)
        row = [g(c) + g(c + '_link') for c in cls]
        swk = sum(g(c) for c in SW)
        tagk = g('tag:sidewalk=*') + g('tag:sidewalk:side=*')
        P(f'| {k} | ' + ' | '.join(f'{x:,.0f}' for x in row) + f' | {swk:,.0f} | {tagk:,.1f} | {g("footway=sidewalk"):,.1f} |')
    P('')

# 6 Mapillary proxy
P('## T6 HeiGIT road-surface dataset: km of OSM roads with >=1 Mapillary-based prediction')
P('| governorate | km in HeiGIT layer | km with Mapillary predictions | share |')
P('|---|---|---|---|')
agg = {}
for k, v in G['heigit_mly_adm1'].items():
    a = k.split('|')[0]
    t = agg.setdefault(a, [0, 0]); t[0] += v.get('km', 0); t[1] += v.get('km_mly', 0)
for a, (km, m) in sorted(agg.items(), key=lambda x: -x[1][1]):
    P(f'| {a} | {km:,.0f} | {m:,.0f} | {100*m/km if km else 0:.1f}% |')
tot = [sum(x[0] for x in agg.values()), sum(x[1] for x in agg.values())]
P(f'| **total** | {tot[0]:,.0f} | {tot[1]:,.0f} | {100*tot[1]/tot[0]:.1f}% |')
P('')
P('Mapillary-prediction km by year of mean image timestamp: ' + ', '.join(f'{y}: {v:,.0f}' for y, v in sorted(G['heigit_mly_year_km'].items())))
open(os.path.join(d, 'summary_tables.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
