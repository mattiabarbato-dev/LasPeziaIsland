"""Mosaic Copernicus GLO-30 tiles, crop, project to Morin local frame, compute horizon profiles.
Usage: python -I horizon.py <scratch> <repo>
"""
import sys, os, math, struct, zlib, json
import numpy as np
sys.path.insert(0, sys.argv[1])
from tiff import read_geotiff

S, REPO = sys.argv[1], sys.argv[2]
DEM_DIR = os.path.join(REPO, 'ref', 'dem')
os.makedirs(DEM_DIR, exist_ok=True)

LAT0, LON0 = 44.1016154, 9.8252769
AZ = math.radians(41.3)
SA, CA = math.sin(AZ), math.cos(AZ)
phi = math.radians(LAT0)
MLAT = 111132.92 - 559.82 * math.cos(2 * phi) + 1.175 * math.cos(4 * phi)
MLON = 111412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi)
R_EARTH = 6371000.0
K_REFR = 0.13

# ---------- mosaic ----------
a9, m9 = read_geotiff(os.path.join(S, 'dl', 'cop_N44_E009.tif'))
a10, m10 = read_geotiff(os.path.join(S, 'dl', 'cop_N44_E010.tif'))
# E010 tile width may differ (lat 44-50 -> 2400 px?)
print('tiles', a9.shape, a10.shape, m10['scale'])
# resample E010 to 3600 columns if needed (nearest along lon)
if a10.shape[1] != 3600:
    idx = (np.arange(3600) * a10.shape[1] / 3600).astype(int)
    a10 = a10[:, idx]
mos = np.concatenate([a9, a10], axis=1)  # lat 45..44 (rows), lon 9..11 (cols)
DLAT = DLON = 1 / 3600.0
# Copernicus: tie point = upper-left corner of upper-left pixel; pixel centre at +0.5 px
def sample(lat, lon):
    r = (45.0 - lat) / DLAT - 0.5
    c = (lon - 9.0) / DLON - 0.5
    r0 = np.clip(np.floor(r).astype(int), 0, mos.shape[0] - 2)
    c0 = np.clip(np.floor(c).astype(int), 0, mos.shape[1] - 2)
    fr, fc = np.clip(r - r0, 0, 1), np.clip(c - c0, 0, 1)
    v = (mos[r0, c0] * (1 - fr) * (1 - fc) + mos[r0 + 1, c0] * fr * (1 - fc)
         + mos[r0, c0 + 1] * (1 - fr) * fc + mos[r0 + 1, c0 + 1] * fr * fc)
    outside = (lat < 44.0) | (lat > 45.0) | (lon < 9.0) | (lon > 11.0)
    return np.where(outside, 0.0, v)  # fuori dalle due tile: trattato come mare (vedi README)

def xy_to_ll(X, Y):
    E = X * SA - Y * CA
    N = X * CA + Y * SA
    return LAT0 + N / MLAT, LON0 + E / MLON

def ll_to_xy(lat, lon):
    N = (lat - LAT0) * MLAT
    E = (lon - LON0) * MLON
    return E * SA + N * CA, -E * CA + N * SA, E, N

# ---------- crop GeoTIFF (geographic) ----------
CROP = dict(lat_min=44.02, lat_max=44.19, lon_min=9.70, lon_max=9.97)
r0 = int(round((45.0 - CROP['lat_max']) * 3600)); r1 = int(round((45.0 - CROP['lat_min']) * 3600))
c0 = int(round((CROP['lon_min'] - 9.0) * 3600)); c1 = int(round((CROP['lon_max'] - 9.0) * 3600))
crop = np.ascontiguousarray(mos[r0:r1, c0:c1].astype('<f4'))

def write_geotiff(path, arr, ul_lon, ul_lat, dx, dy):
    H, W = arr.shape
    data = arr.tobytes()
    entries = []
    extra = bytearray()
    base = 8
    # layout: header(8) + data + extra + IFD
    data_off = base
    extra_off = data_off + len(data)
    def add_extra(b):
        off = extra_off + len(extra)
        extra.extend(b)
        if len(extra) % 2: extra.extend(b'\0')
        return off
    geokeys = [1, 1, 0, 3, 1024, 0, 1, 2, 1025, 0, 1, 1, 2048, 0, 1, 4326]
    asc = b'WGS 84|\0'
    tags = [
        (256, 4, 1, W), (257, 4, 1, H), (258, 3, 1, 32), (259, 3, 1, 1), (262, 3, 1, 1),
        (273, 4, 1, data_off), (277, 3, 1, 1), (278, 4, 1, H), (279, 4, 1, len(data)),
        (284, 3, 1, 1), (339, 3, 1, 3),
        (33550, 12, 3, add_extra(struct.pack('<3d', dx, dy, 0.0))),
        (33922, 12, 6, add_extra(struct.pack('<6d', 0, 0, 0, ul_lon, ul_lat, 0))),
        (34735, 3, len(geokeys), add_extra(struct.pack('<%dH' % len(geokeys), *geokeys))),
        (34737, 2, len(asc), add_extra(asc)),
        (42113, 2, 8, add_extra(b'-32767\0\0')),
    ]
    ifd_off = extra_off + len(extra)
    ifd = struct.pack('<H', len(tags))
    for tag, typ, cnt, val in tags:
        if typ == 3 and cnt == 1:
            ifd += struct.pack('<HHIHH', tag, typ, cnt, val, 0)
        else:
            ifd += struct.pack('<HHII', tag, typ, cnt, val)
    ifd += struct.pack('<I', 0)
    with open(path, 'wb') as f:
        f.write(b'II' + struct.pack('<HI', 42, ifd_off))
        f.write(data); f.write(extra); f.write(ifd)

write_geotiff(os.path.join(DEM_DIR, 'cop30_golfo_spezia_wgs84.tif'), crop,
              CROP['lon_min'], CROP['lat_max'], DLON, DLAT)
print('crop', crop.shape, float(crop.min()), float(crop.max()))

# ---------- local grid in project frame ----------
STEP = 30.0
HALF = 10020.0
coords = np.arange(-HALF, HALF + 0.1, STEP)
GX, GY = np.meshgrid(coords, coords[::-1])  # row 0 = +Y (city side, NW)
la, lo = xy_to_ll(GX, GY)
grid = sample(la, lo).astype('<f4')
np.save(os.path.join(DEM_DIR, 'morin_local_30m.npy'), grid)
# 16-bit PNG: value = (h + 20 m) * 20  -> 0.05 m step, range -20..3256 m
def write_png16(path, arr16):
    H, W = arr16.shape
    raw = b''.join(b'\0' + arr16[i].astype('>u2').tobytes() for i in range(H))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 16, 0, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    open(path, 'wb').write(png)
h16 = np.clip((grid + 20.0) * 20.0, 0, 65535).round().astype(np.uint16)
write_png16(os.path.join(DEM_DIR, 'morin_local_30m_h16.png'), h16)
print('grid', grid.shape, float(grid.min()), float(grid.max()))

# ---------- horizon ----------
def drop(d):
    return d * d / (2 * R_EARTH) * (1 - K_REFR)

D = np.concatenate([np.arange(60, 3000, 10), np.arange(3000, 15000, 20), np.arange(15000, 70000, 40)]).astype(float)

def horizon(X0, Y0, eye_asl, dmin, step_deg=1.0):
    rows = []
    E0 = X0 * SA - Y0 * CA; N0 = X0 * CA + Y0 * SA
    for az in np.arange(0, 360, step_deg):
        a = math.radians(az)
        d = D[D >= dmin]
        E = E0 + d * math.sin(a); N = N0 + d * math.cos(a)
        lat = LAT0 + N / MLAT; lon = LON0 + E / MLON
        h = sample(lat, lon)
        h = np.where(h < 0.5, 0.0, h)  # sea level / water
        ang = np.degrees(np.arctan2(h - eye_asl - drop(d), d))
        i = int(np.argmax(ang))
        # first land along ray (distance of coast) and whether ray is "sea only" to 70 km
        land = np.nonzero(h > 2.0)[0]
        first_land = float(d[land[0]]) if len(land) else float('nan')
        sea_dip = -math.degrees(math.acos(R_EARTH / (R_EARTH + eye_asl)))
        top = float(ang[i])
        kind = 'terra'
        if h[i] <= 0.5 or top < sea_dip + 0.01:
            top = sea_dip; kind = 'mare'
        lat_i, lon_i = float(lat[i]), float(lon[i])
        rows.append(dict(az=float(az), elev=round(top, 3), dist=round(float(d[i])) if kind == 'terra' else round(math.sqrt(2 * R_EARTH * eye_asl)),
                         h=round(float(h[i]), 1) if kind == 'terra' else 0.0, kind=kind,
                         lat=round(lat_i, 5), lon=round(lon_i, 5), first_land=round(first_land) if first_land == first_land else ''))
    return rows

EYE = 1.5 + 1.8  # banchina ~+1.5 m s.l.m. [S] + eyes 1.8 m
POINTS = {
    'spawn': (240.0, 84.5),     # UE (24000,-8450) -> Blender X 240, Y +84.5
    'imbocco_ponte': (0.0, 0.0),
    'meta_blocco': (125.0, 84.5),
    'fine_passeggiata': (550.0, 84.5),
}
out = {}
for name, (X, Y) in POINTS.items():
    for label, dmin in (('colline', 1500.0), ('tutto', 250.0)):
        rows = horizon(X, Y, EYE, dmin, 1.0)
        out[(name, label)] = rows
        p = os.path.join(DEM_DIR, f'orizzonte_{name}_{label}.csv')
        with open(p, 'w', encoding='utf-8') as f:
            f.write('azimut_deg,elev_deg,dist_m,quota_cresta_m,tipo,lat,lon,prima_terra_m\n')
            for r in rows:
                f.write(f"{r['az']:.0f},{r['elev']:.3f},{r['dist']},{r['h']},{r['kind']},{r['lat']},{r['lon']},{r['first_land']}\n")
json.dump({f'{k[0]}|{k[1]}': v for k, v in out.items()}, open(os.path.join(S, 'horizon.json'), 'w'))

# finer (0.25 deg) for spawn hills, used for the plot
fine = horizon(240.0, 84.5, EYE, 1500.0, 0.25)
json.dump(fine, open(os.path.join(S, 'horizon_fine.json'), 'w'))
print('done')
