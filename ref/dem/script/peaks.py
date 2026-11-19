import sys, os, math, json
import numpy as np
S, REPO = sys.argv[1], sys.argv[2]
DEM = os.path.join(REPO, 'ref', 'dem')
LAT0, LON0 = 44.1016154, 9.8252769
AZ = math.radians(41.3); SA, CA = math.sin(AZ), math.cos(AZ)
phi = math.radians(LAT0)
MLAT = 111132.92 - 559.82 * math.cos(2 * phi) + 1.175 * math.cos(4 * phi)
MLON = 111412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi)
R, K, EYE = 6371000.0, 0.13, 3.3
grid = np.load(os.path.join(DEM, 'morin_local_30m.npy')); n = grid.shape[0]; HALF, STEP = 10020.0, 30.0
fine = json.load(open(os.path.join(S, 'horizon_fine.json'), encoding='utf-8'))
haz = np.array([r['az'] for r in fine]); hel = np.array([r['elev'] for r in fine])
hdist = np.array([r['dist'] for r in fine])

def local(lat, lon):
    N = (lat - LAT0) * MLAT; E = (lon - LON0) * MLON
    return E, N, E * SA + N * CA, -E * CA + N * SA

def dem_at(X, Y):
    ci = int(round((X + HALF) / STEP)); ri = int(round((HALF - Y) / STEP))
    if 0 <= ci < n and 0 <= ri < n:
        # max in 3x3 (the peak node may be off by a cell)
        return float(grid[max(0, ri - 1):ri + 2, max(0, ci - 1):ci + 2].max())
    return float('nan')

d = json.load(open(os.path.join(S, 'osm', 'peaks.json'), encoding='utf-8'))
sx, sy = 240.0, 84.5
sE = sx * SA - sy * CA; sN = sx * CA + sy * SA
rows = []
for e in d['elements']:
    t = e['tags']
    if 'natural' not in t:
        continue
    E, N, X, Y = local(e['lat'], e['lon'])
    az0 = (math.degrees(math.atan2(E, N)) + 360) % 360
    d0 = math.hypot(E, N)
    dE, dN = E - sE, N - sN
    az = (math.degrees(math.atan2(dE, dN)) + 360) % 360
    ds = math.hypot(dE, dN)
    ele_osm = t.get('ele')
    hd = dem_at(X, Y)
    h = float(ele_osm.replace(',', '.').split()[0]) if ele_osm and ele_osm.replace(',', '.').split()[0].replace('.', '', 1).isdigit() else hd
    ang = math.degrees(math.atan2(h - EYE - ds * ds / (2 * R) * (1 - K), ds))
    i = int(np.argmin(np.abs(((haz - az + 180) % 360) - 180)))
    vis = 'si (cresta)' if ang >= hel[i] - 0.15 else ('nascosta' if ang < hel[i] - 0.4 else 'al limite')
    rows.append(dict(id=e['id'], tipo=t['natural'], nome=t.get('name', ''), ele_osm=ele_osm or '', dem=round(hd, 0) if hd == hd else '',
                     lat=e['lat'], lon=e['lon'], az_origine=round(az0, 1), dist_origine=round(d0), X=round(X), Y=round(Y),
                     az_spawn=round(az, 1), dist_spawn=round(ds), elev_spawn=round(ang, 2), orizz_spawn=round(float(hel[i]), 2),
                     visibile=vis))
rows.sort(key=lambda r: r['az_spawn'])
keys = list(rows[0].keys())
with open(os.path.join(DEM, 'cime_osm.csv'), 'w', encoding='utf-8') as f:
    f.write(','.join(keys) + '\n')
    for r in rows:
        f.write(','.join('"%s"' % r[k] if k == 'nome' else str(r[k]) for k in keys) + '\n')
for r in rows:
    if r['dist_spawn'] < 16000:
        print(r['az_spawn'], r['dist_spawn'], r['tipo'], r['nome'], r['ele_osm'], r['dem'], r['elev_spawn'], r['orizz_spawn'], r['visibile'], r['X'], r['Y'])
