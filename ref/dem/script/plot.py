"""SVG of horizon profile from spawn -> rendered to PNG with Edge headless.
Usage: python -I plot.py <scratch> <repo>
"""
import sys, os, math, json, csv
S, REPO = sys.argv[1], sys.argv[2]
DEM = os.path.join(REPO, 'ref', 'dem')
LAT0 = 44.1016154
AZ = math.radians(41.3); SA, CA = math.sin(AZ), math.cos(AZ)

def read(name):
    with open(os.path.join(DEM, name), encoding='utf-8') as f:
        return list(csv.DictReader(f))

fine = json.load(open(os.path.join(S, 'horizon_fine.json'), encoding='utf-8'))
tutto = read('orizzonte_spawn_tutto.csv')
ponte = read('orizzonte_imbocco_ponte_colline.csv')
peaks = read('cime_osm.csv')

W, H = 2400, 900
L, R, T, B = 70, 30, 60, 110
E_MIN, E_MAX = -1.0, 12.0
def px(az): return L + az / 360.0 * (W - L - R)
def py(el): return T + (E_MAX - el) / (E_MAX - E_MIN) * (H - T - B)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#f7f7f4"/>']
# grid
for el in range(-1, 13):
    y = py(el)
    svg.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#ddd" stroke-width="1"/>')
    svg.append(f'<text x="{L-8}" y="{y+4:.1f}" font-size="13" text-anchor="end" fill="#555">{el}°</text>')
for az in range(0, 361, 15):
    x = px(az)
    svg.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{H-B}" stroke="{"#bbb" if az % 45 == 0 else "#e4e4e4"}" stroke-width="1"/>')
    lab = {0: 'N', 45: 'NE', 90: 'E', 135: 'SE', 180: 'S', 225: 'SO', 270: 'O', 315: 'NO', 360: 'N'}.get(az, '')
    svg.append(f'<text x="{x:.1f}" y="{H-B+18}" font-size="13" text-anchor="middle" fill="#444">{az}° {lab}</text>')
y0 = py(0)
svg.append(f'<line x1="{L}" y1="{y0:.1f}" x2="{W-R}" y2="{y0:.1f}" stroke="#7aa" stroke-width="1.5"/>')
# filled horizon (colline, d>=1.5 km)
pts = [(px(r['az']), py(r['elev'])) for r in fine] + [(px(359.99), py(fine[0]['elev']))]
poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
svg.append(f'<polygon points="{px(0):.1f},{py(E_MIN):.1f} {poly} {px(359.99):.1f},{py(E_MIN):.1f}" fill="#7c9a6a" fill-opacity="0.55" stroke="#3d5a2e" stroke-width="2"/>')
# sea segments
for r in fine:
    if r['kind'] == 'mare':
        x = px(r['az'])
        svg.append(f'<rect x="{x-1.5:.1f}" y="{py(0.6):.1f}" width="3.2" height="{py(-1)-py(0.6):.1f}" fill="#4f86a8" fill-opacity="0.5"/>')
# tutto (d>=250 m, includes city DSM)
pt2 = ' '.join(f'{px(float(r["azimut_deg"])):.1f},{py(float(r["elev_deg"])):.1f}' for r in tutto)
svg.append(f'<polyline points="{pt2}" fill="none" stroke="#b5651d" stroke-width="1.4" stroke-dasharray="5,3"/>')
# imbocco ponte
pt3 = ' '.join(f'{px(float(r["azimut_deg"])):.1f},{py(float(r["elev_deg"])):.1f}' for r in ponte)
svg.append(f'<polyline points="{pt3}" fill="none" stroke="#5b4b9a" stroke-width="1.2" stroke-opacity="0.8"/>')
# passeggiata axis & ponte antenna
for az, lab in ((41.3, 'asse passeggiata → NE (41,3°)'), (221.3, 'asse passeggiata → SO (221,3°)')):
    x = px(az)
    svg.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{H-B}" stroke="#c03" stroke-width="1.5" stroke-dasharray="8,4"/>')
    svg.append(f'<text x="{x+5:.1f}" y="{T+14}" font-size="13" fill="#c03">{lab}</text>')
# antenna 1 of bridge (35 m s.l.m.) from spawn
dX, dY = -2.3 - 240.0, -80.1 - 84.5
E = dX * SA - dY * CA; N = dX * CA + dY * SA
aaz = (math.degrees(math.atan2(E, N)) + 360) % 360; ad = math.hypot(E, N)
ael = math.degrees(math.atan2(35 - 3.3, ad))
x = px(aaz)
svg.append(f'<line x1="{x:.1f}" y1="{py(0):.1f}" x2="{x:.1f}" y2="{py(ael):.1f}" stroke="#222" stroke-width="3"/>')
svg.append(f'<text x="{x+6:.1f}" y="{py(ael)-6:.1f}" font-size="13" fill="#222">antenna ponte ({aaz:.0f}°, {ael:.1f}°, {ad:.0f} m)</text>')
# peaks visible
labs = []
for p in peaks:
    if p['visibile'] not in ('si (cresta)',) or p['tipo'] != 'peak' or not p['nome'].strip('"'):
        continue
    if float(p['dist_spawn']) > 16000:
        continue
    az = float(p['az_spawn']); el = float(p['elev_spawn'])
    labs.append((az, el, p['nome'].strip('"'), p['ele_osm'] or p['dem'], float(p['dist_spawn'])))
labs.sort()
# tieni una sola etichetta per gruppo (la piu' alta in elevazione entro 4 gradi)
kept = []
for item in sorted(labs, key=lambda t: -t[1]):
    if all(abs(item[0] - k[0]) > 4 for k in kept):
        kept.append(item)
labs = sorted(kept)
last_x, lvl = -999, 0
for az, el, nm, ele, d in labs:
    x, y = px(az), py(el)
    lvl = lvl + 1 if x - last_x < 120 else 0
    last_x = x
    ty = y - 14 - 16 * (lvl % 3)
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#222"/>')
    svg.append(f'<text x="{x:.1f}" y="{ty:.1f}" font-size="12" text-anchor="middle" fill="#111">{nm} {ele} m · {d/1000:.1f} km</text>')
# legend & title
svg.append(f'<text x="{L}" y="30" font-size="20" font-weight="600" fill="#222">Profilo dell\'orizzonte dalla partenza del giocatore (X 240, Y 84,5; occhi a 3,3 m s.l.m.)</text>')
svg.append(f'<text x="{L}" y="50" font-size="13" fill="#555">Copernicus DEM GLO-30 (DSM), terreno oltre 1,5 km, curvatura e rifrazione (k 0,13) incluse. Elevazione in gradi sopra l\'orizzontale; scala verticale esagerata ~10×.</text>')
ly = H - 60
items = [('#3d5a2e', 'cresta colline (d ≥ 1,5 km), dalla partenza', ''), ('#b5651d', 'tutto oltre 250 m (DSM: include città e alberi)', '5,3'),
         ('#5b4b9a', 'colline dall\'imbocco del ponte (0,0)', ''), ('#4f86a8', 'mare aperto (orizzonte marino a ~6,5 km)', '')]
x = L
for col, txt, dash in items:
    svg.append(f'<line x1="{x}" y1="{ly}" x2="{x+40}" y2="{ly}" stroke="{col}" stroke-width="4" {"stroke-dasharray=%s" % chr(34)+dash+chr(34) if dash else ""}/>')
    svg.append(f'<text x="{x+48}" y="{ly+5}" font-size="14" fill="#333">{txt}</text>')
    x += 520
svg.append(f'<text x="{L}" y="{H-25}" font-size="12" fill="#666">produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved. Cime: © OpenStreetMap contributors (ODbL).</text>')
svg.append('</svg>')
out = os.path.join(S, 'profilo.svg')
open(out, 'w', encoding='utf-8').write('\n'.join(svg))
print(out, aaz, ad, ael)
