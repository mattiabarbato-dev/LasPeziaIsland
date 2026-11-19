"""CORINE 2018 on Morin local grid + viewshed from spawn + summary per azimuth band.
Usage: python -I landcover.py <scratch> <repo>
"""
import sys, os, math, json, struct, zlib
import numpy as np

S, REPO = sys.argv[1], sys.argv[2]
DEM = os.path.join(REPO, 'ref', 'dem')
LAT0, LON0 = 44.1016154, 9.8252769
AZ = math.radians(41.3); SA, CA = math.sin(AZ), math.cos(AZ)
phi = math.radians(LAT0)
MLAT = 111132.92 - 559.82 * math.cos(2 * phi) + 1.175 * math.cos(4 * phi)
MLON = 111412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi)
STEP, HALF = 30.0, 10020.0
grid = np.load(os.path.join(DEM, 'morin_local_30m.npy'))
n = grid.shape[0]
coords = np.arange(-HALF, HALF + 0.1, STEP)
GX, GY = np.meshgrid(coords, coords[::-1])

def ll_to_xy(lat, lon):
    N = (lat - LAT0) * MLAT; E = (lon - LON0) * MLON
    return E * SA + N * CA, -E * CA + N * SA

# ---- rasterize CLC (even-odd over all rings of each polygon) ----
clc = json.load(open(os.path.join(S, 'clc', 'clc.json')))
cls = np.zeros(grid.shape, np.int16)
for ft in clc['features']:
    code = int(ft['properties']['Code_18'])
    rings = [np.array(r) for r in ft['geometry']['coordinates']]
    rxy = [np.stack(ll_to_xy(r[:, 1], r[:, 0]), 1) for r in rings]
    allp = np.concatenate(rxy)
    x0, y0 = allp.min(0); x1, y1 = allp.max(0)
    ci0 = max(0, int((x0 + HALF) / STEP)); ci1 = min(n - 1, int((x1 + HALF) / STEP) + 1)
    ri0 = max(0, int((HALF - y1) / STEP)); ri1 = min(n - 1, int((HALF - y0) / STEP) + 1)
    if ci0 > ci1 or ri0 > ri1:
        continue
    # scanline: per ogni riga, intersezioni con tutti i lati (vettoriale), riempimento a coppie (pari-dispari)
    xa = np.concatenate([r[:-1, 0] for r in rxy]); ya = np.concatenate([r[:-1, 1] for r in rxy])
    xb = np.concatenate([r[1:, 0] for r in rxy]); yb = np.concatenate([r[1:, 1] for r in rxy])
    for ri in range(ri0, ri1 + 1):
        yc = HALF - ri * STEP
        cond = (ya > yc) != (yb > yc)
        if not cond.any():
            continue
        xs = np.sort(xa[cond] + (yc - ya[cond]) * (xb[cond] - xa[cond]) / (yb[cond] - ya[cond]))
        for k in range(0, len(xs) - 1, 2):
            c_a = max(0, int(math.ceil((xs[k] + HALF) / STEP)))
            c_b = min(n - 1, int(math.floor((xs[k + 1] + HALF) / STEP)))
            if c_b >= c_a:
                cls[ri, c_a:c_b + 1] = code
# celle senza poligono (fuori bbox CLC) = 0
np.save(os.path.join(DEM, 'morin_local_30m_clc.npy'), cls)

COL = {111: (176, 146, 120), 112: (186, 160, 132), 121: (150, 148, 142), 122: (120, 118, 112), 123: (140, 140, 136),
       132: (150, 140, 120), 142: (120, 145, 85), 141: (110, 140, 80), 211: (150, 145, 95), 221: (130, 130, 85),
       223: (118, 124, 86), 241: (125, 128, 82), 242: (122, 126, 80), 243: (104, 116, 70), 311: (62, 86, 48),
       312: (48, 70, 44), 313: (55, 78, 46), 323: (88, 98, 60), 324: (95, 105, 65), 331: (200, 190, 160),
       334: (90, 85, 70), 332: (150, 140, 120), 333: (140, 135, 110), 411: (90, 110, 80), 511: (40, 70, 90),
       523: (40, 70, 90), 0: (40, 70, 90)}
rgb = np.zeros(grid.shape + (3,), np.uint8)
for c, v in COL.items():
    rgb[cls == c] = v
rgb[(cls == 0) | (grid < 0.5) & np.isin(cls, [0, 523])] = COL[523]

def write_png(path, img):
    H, W = img.shape[:2]
    ct = 2 if img.ndim == 3 else 0
    raw = b''.join(b'\0' + img[i].tobytes() for i in range(H))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, ct, 0, 0, 0))
                           + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
write_png(os.path.join(DEM, 'morin_local_30m_colore_clc.png'), rgb)

# ---- viewshed from spawn ----
R, K = 6371000.0, 0.13
EYE = 3.3
X0, Y0 = 240.0, 84.5
E0 = X0 * SA - Y0 * CA; N0 = X0 * CA + Y0 * SA
vis = np.zeros(grid.shape, np.uint8)
d = np.arange(30.0, 14000.0, 15.0)
for azd in np.arange(0, 360, 0.2):
    a = math.radians(azd)
    E = E0 + d * math.sin(a); N = N0 + d * math.cos(a)
    X = E * SA + N * CA; Y = -E * CA + N * SA
    ci = np.round((X + HALF) / STEP).astype(int); ri = np.round((HALF - Y) / STEP).astype(int)
    ok = (ci >= 0) & (ci < n) & (ri >= 0) & (ri < n)
    ci, ri, dd = ci[ok], ri[ok], d[ok]
    h = grid[ri, ci]
    ang = np.arctan2(h - EYE - dd * dd / (2 * R) * (1 - K), dd)
    runmax = np.maximum.accumulate(np.concatenate([[-1.0], ang[:-1]]))
    v = ang >= runmax
    vis[ri[v], ci[v]] = 255
write_png(os.path.join(DEM, 'morin_local_30m_visibile_spawn.png'), vis)

# ---- summary per 15 deg band (visible land cells, d >= 1500 m) ----
dist = np.hypot(GX - X0, GY - Y0)
Ec = (GX - X0) * SA - (GY - Y0) * CA; Nc = (GX - X0) * CA + (GY - Y0) * SA
azc = (np.degrees(np.arctan2(Ec, Nc)) + 360) % 360
GROUPS = {'urbano': [111, 112], 'industria/porto': [121, 122, 123, 132, 142, 141], 'terrazze/coltivi/oliveti': [211, 221, 223, 241, 242, 243],
          'bosco latifoglie': [311], 'bosco conifere/misto': [312, 313], 'macchia/arbusti': [323, 324], 'roccia/spiaggia/bruciato': [331, 332, 333, 334]}
rows = []
for b0 in range(0, 360, 15):
    m = (vis > 0) & (dist >= 1500) & (azc >= b0) & (azc < b0 + 15) & (grid > 2) & (cls > 0) & (cls != 523)
    tot = m.sum()
    row = {'az_da': b0, 'az_a': b0 + 15, 'celle_visibili': int(tot)}
    for g, codes in GROUPS.items():
        row[g] = round(100.0 * np.isin(cls[m], codes).sum() / tot, 1) if tot else 0.0
    if tot:
        row['dist_min_m'] = int(dist[m].min()); row['dist_max_m'] = int(dist[m].max())
        row['quota_max_m'] = int(grid[m].max())
    else:
        row['dist_min_m'] = row['dist_max_m'] = row['quota_max_m'] = ''
    rows.append(row)
keys = list(rows[0].keys())
with open(os.path.join(DEM, 'copertura_per_azimut_spawn.csv'), 'w', encoding='utf-8') as f:
    f.write(','.join(keys) + '\n')
    for r in rows:
        f.write(','.join(str(r[k]) for k in keys) + '\n')
for r in rows:
    print(r)
# overall visible stats for proposal
m = (vis > 0) & (grid > 2)
print('visible land cells', int(m.sum()), 'area km2', m.sum() * 0.0009)
for lim in (1500, 3000, 5000, 8000, 10000):
    print(lim, int((m & (dist <= lim)).sum()))
