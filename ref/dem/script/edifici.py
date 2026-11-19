import json, math, sys
LAT0, LON0 = 44.1016154, 9.8252769
AZ = math.radians(41.3); SA, CA = math.sin(AZ), math.cos(AZ)
phi = math.radians(LAT0)
MLAT = 111132.92 - 559.82 * math.cos(2 * phi); MLON = 111412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi)
b = json.load(open(sys.argv[1], encoding='utf-8'))
seen = {}
for e in b['elements']:
    c = e['center']; t = e['tags']
    N = (c['lat'] - LAT0) * MLAT; E = (c['lon'] - LON0) * MLON
    X = E * SA + N * CA; Y = -E * CA + N * SA
    lv = t.get('building:levels'); h = t.get('height')
    try: lvn = float(lv) if lv else None
    except: lvn = None
    try: hn = float(h.split()[0]) if h else None
    except: hn = None
    est = hn if hn else (lvn * 3.2 + 1.3 if lvn else None)
    seen[e['id']] = (e['id'], round(X), round(Y), round(math.hypot(E, N)), round((math.degrees(math.atan2(E, N)) + 360) % 360), t.get('building'), lv, h, est, t.get('name', ''), (t.get('addr:street', '') + ' ' + t.get('addr:housenumber', '')).strip())
rows = sorted(seen.values(), key=lambda r: -(r[8] or 0))
print(len(rows))
import collections
print(collections.Counter(r[6] for r in rows).most_common(20))
for r in rows[:60]: print(r)
import numpy as np
g = np.load(sys.argv[2])
def dsm(X, Y):
    ci = int(round((X + 10020) / 30)); ri = int(round((10020 - Y) / 30))
    return float(g[ri-1:ri+2, ci-1:ci+2].max()), float(np.median(g[ri-5:ri+6, ci-5:ci+6]))
with open(sys.argv[3], 'w', encoding='utf-8') as f:
    f.write('osm_way,X,Y,dist_origine_m,az_origine_deg,building,levels,height_tag,altezza_stimata_m,dsm_max_m,dsm_mediana_330m,elev_dallo_spawn_deg\n')
    for r in rows:
        mx, md = dsm(r[1], r[2])
        hs = r[8] if r[8] else 0
        # elevazione dalla partenza: suolo ~ mediana DSM (approssimazione) + altezza
        dx, dy = r[1] - 240.0, r[2] - 84.5
        d = math.hypot(dx, dy)
        el = math.degrees(math.atan2(md + hs - 3.3, d)) if hs else ''
        f.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]},{r[6] or ''},{r[7] or ''},{round(r[8],1) if r[8] else ''},{mx:.1f},{md:.1f},{round(el,2) if el != '' else ''}\n")
lv = [float(r[6]) for r in rows if r[6] and r[6].replace('.','',1).isdigit()]
print('n', len(rows), 'levels>=6', sum(1 for x in lv if x >= 6), 'within 600 m', sum(1 for r in rows if r[3] <= 600))
for r in rows:
    if r[3] <= 600 and r[8]: print('near', r[:9])
