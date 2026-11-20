# Generatore layout marina Blocco 1 (geo-scout). Coordinate progetto in metri -> CSV UE (x*100, -y*100).
import math, random, sys, os
from collections import Counter, defaultdict

OUT = sys.argv[1]
random.seed(20261120)

def yq(x):  # ciglio banchina (dalle scalette v2)
    return 80.2663 - 0.002166 * (x - 44.0)

def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); return (dx / L, dy / L), L

def yaw_ue(d):  # direzione progetto -> yaw UE
    return math.degrees(math.atan2(-d[1], d[0]))

# ---------------- pontili (polilinee OSM, coordinate progetto) ----------------
GANG = 3.5  # passerella: il galleggiante parte 3,5 m dal ciglio
PONTILI = {
  # nome: (polilinea, larghezza, galleggiante, osm)
  "Spina":   ([(151.1, yq(151.1) - GANG), (150.3, -86.0), (165.1, -101.1), (195.5, -132.0), (197.1, -176.6)], 2.8, True, "149964057"),
  "Esterno": ([(197.1, -176.6), (295.5, -174.4)], 2.8, True, "149964057 (coda)"),
  "Esterno2":([(197.1, -176.6), (196.0, -213.1), (213.9, -229.7), (316.4, -228.6)], 2.8, True, "175935436"),
  "F1": ([(151.6, 62.8), (261.9, 62.9)], 2.8, True, "149964075"),
  "F2": ([(151.4, 43.2), (261.6, 41.8)], 2.8, True, "149964059"),
  "F3": ([(151.2, 17.6), (260.4, 17.0)], 2.8, True, "149964070"),
  "F4": ([(150.9, -11.7), (260.5, -10.8)], 2.8, True, "149964102"),
  "F5": ([(150.7, -40.6), (259.4, -38.9)], 2.8, True, "149964068"),
  "F6": ([(150.4, -66.9), (260.8, -69.1)], 2.8, True, "149964079"),
  "F7": ([(165.1, -101.1), (261.4, -99.9)], 2.8, True, "149964062"),
  "F8": ([(195.5, -132.0), (260.8, -131.0)], 2.8, True, "149964065"),
  "L_Gamba": ([(105.4, yq(105.4) - GANG), (106.3, 62.3), (106.7, 29.6)], 2.8, True, "175935435"),
  "L_Testa": ([(106.7, 29.6), (89.4, 29.5)], 2.8, True, "175935435 (testa)"),
  "L_Ramo":  ([(106.3, 62.3), (88.9, 61.6)], 2.8, True, "529818282"),
  "NE":      ([(289.6, yq(289.6) - GANG), (291.7, -6.5)], 2.8, True, "175935432"),
}
LARGO = ([(126.9, yq(126.9)), (127.1, 45.5)], 5.0)  # 175935434, fisso [S]

# fingers: partono dal bordo della spina (non dal suo asse)
for k in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"):
    p, w, f, o = PONTILI[k]
    d, L = unit(p[0], p[1])
    PONTILI[k] = ([(p[0][0] + d[0] * 1.4, p[0][1] + d[1] * 1.4), p[1]], w, f, o)
for k in ("L_Testa", "L_Ramo"):
    p, w, f, o = PONTILI[k]
    d, L = unit(p[0], p[1])
    PONTILI[k] = ([(p[0][0] + d[0] * 1.4, p[0][1] + d[1] * 1.4), p[1]], w, f, o)
p, w, f, o = PONTILI["Esterno"]; d, L = unit(p[0], p[1]); PONTILI["Esterno"] = ([(p[0][0] + d[0] * 1.4, p[0][1] + d[1] * 1.4), p[1]], w, f, o)

Z_DECK = -45.0
rows_p = []
seg_rects = []  # per collisioni barche: (centro, dir, mezza lunghezza, mezza larghezza)
mod_count = Counter(); lengths = {}
for name, (pts, w, flo, osm) in PONTILI.items():
    tot = 0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d, L = unit(a, b); tot += L
        seg_rects.append(((a[0] + d[0] * L / 2, a[1] + d[1] * L / 2), d, L / 2 + 0.2, w / 2 + 0.1))
        n48 = int(L // 48); rem = L - 48 * n48
        mods = [("SM_Mirabello_Pontile", 48.0 * k, 48.0, Z_DECK, "base") for k in range(n48)]
        if rem > 0.6:
            n12 = max(1, math.ceil((rem - 0.6) / 12.0))  # fino a 0,6 m di scarto in punta
            for k in range(n12):
                s = 48.0 * n48 + 12.0 * k
                z = Z_DECK
                var = "nuovo_fallback_SM_Mirabello_Pontile_scalaX_0.25"
                if s + 12.0 > L:  # ultimo modulo arretrato: sovrapposto, 1 cm piu' basso
                    s = L - 12.0; z = Z_DECK - 1.0
                    if s < 0: s = 0.0
                mods.append(("SM_Morin_Marina_Pontile12", s, 12.0, z, var))
        for j, (asset, s, ml, z, var) in enumerate(mods):
            x, y = a[0] + d[0] * s, a[1] + d[1] * s
            nm = f"Marina_{name}_s{i}_m{j:02d}"
            rows_p.append((asset, nm, x * 100, -y * 100, z, yaw_ue(d), 0.0, 0.0, var))
            mod_count[asset] += 1
    lengths[name] = tot
# pontile largo fisso
(a, b), wl = LARGO[0], LARGO[1]
d, L = unit(a, b)
rows_p.append(("SM_Morin_Marina_PontileLargo", "Marina_Largo_m00", a[0] * 100, -a[1] * 100, 0.0, yaw_ue(d), 0.0, 0.0,
               "nuovo_35x5m_fallback_2_file_SM_Mirabello_Pontile_a_pm1.45m"))
seg_rects.append(((a[0] + d[0] * L / 2, a[1] + d[1] * L / 2), d, L / 2 + 0.2, wl / 2 + 0.1))
lengths["Largo"] = L
# passerelle (galleggianti -> ciglio)
for nm, x in (("Spina", 151.1), ("L_Gamba", 105.4), ("NE", 289.6)):
    pitch = -math.degrees(math.atan2(0.45, GANG))
    rows_p.append(("SM_Morin_Marina_Passerella", f"Marina_Passerella_{nm}", x * 100, -yq(x) * 100, 0.0, yaw_ue((0, -1)), round(pitch, 2), 0.0, "nuovo"))
    seg_rects.append(((x, yq(x) - GANG / 2), (0, -1), GANG / 2, 0.8))
# circolo nautico (fondale) [S]
rows_p.append(("SM_Morin_Marina_Circolo", "Marina_Circolo", 161.0 * 100, -72.0 * 100, 0.0, 0.0, 0.0, 0.0, "nuovo_16x10m_su_palafitta"))

# ---------------- zone riservate ----------------
def rect_aabb(x0, x1, y0, y1):
    return (((x0 + x1) / 2, (y0 + y1) / 2), (1.0, 0.0), (x1 - x0) / 2, (y1 - y0) / 2)
RESERVED = [rect_aabb(55, 90, -120, 82)]                     # imbarco + battello
for xs in (92, 140, 188, 300):                               # scalette (300 = Blocco 2)
    RESERVED.append(rect_aabb(xs - 4, xs + 4, 66, 82))
RESERVED.append(rect_aabb(151.5, 171, 64, 82))               # circolo nautico [S]
FERRY = [[(80.0, -36.9), (110.2, -86.5), (188.4, -241.7)], [(80.1, 1.0), (135.1, -107.5), (199.4, -231.7)]]
FERRY_BUF = 12.0

def corners(c, d, hl, hw):
    n = (-d[1], d[0])
    return [(c[0] + d[0] * sx * hl + n[0] * sy * hw, c[1] + d[1] * sx * hl + n[1] * sy * hw) for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]

def sat(r1, r2):
    c1, c2 = corners(*r1), corners(*r2)
    for r in (r1, r2):
        d = r[1]; n = (-d[1], d[0])
        for ax in (d, n):
            p1 = [p[0] * ax[0] + p[1] * ax[1] for p in c1]; p2 = [p[0] * ax[0] + p[1] * ax[1] for p in c2]
            if max(p1) < min(p2) or max(p2) < min(p1): return False
    return True

def dist_pt_seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

def near_ferry(rect):
    for pl in FERRY:
        for i in range(len(pl) - 1):
            for p in corners(*rect) + [rect[0]]:
                if dist_pt_seg(p, pl[i], pl[i + 1]) < FERRY_BUF: return True
    return False

# ---------------- tipi di barca ----------------
# L, B, stern(x locale), bow, z, asset
T = {
  "G":  dict(asset="SM_Morin_Barca_Gommone",   L=5.0,  B=2.2, xs=-2.5,  xb=2.5,  z=-103.0, cat="gommone"),
  "Z":  dict(asset="SM_Morin_Barca_Gozzo",     L=6.0,  B=2.3, xs=-3.0,  xb=3.0,  z=-103.0, cat="motore"),
  "M":  dict(asset="SM_Morin_Barca_Motoscafo", L=7.5,  B=2.7, xs=-3.75, xb=3.75, z=-103.0, cat="motore"),
  "V9": dict(asset="SM_Morin_Barca_Vela9",     L=9.0,  B=3.0, xs=-4.5,  xb=4.5,  z=-103.0, cat="vela"),
  "V11":dict(asset="SM_Mirabello_YachtB_v2",   L=11.0, B=3.6, xs=-5.5,  xb=5.5,  z=-103.0, cat="vela"),
  "Y13":dict(asset="SM_Mirabello_YachtA",      L=13.2, B=4.0, xs=-6.95, xb=6.25, z=-103.0, cat="yacht"),
}
COLORI = {
  "G": [("Tubolari_Grigio", 50), ("Tubolari_Nero", 35), ("Tubolari_Rosso", 15)],
  "Z": [("Bianco_FasciaAzzurra", 35), ("Bianco_FasciaVerde", 20), ("Bianco_FasciaRossa", 15), ("Legno", 15), ("Azzurro", 15)],
  "M": [("Bianco_TelaBlu", 45), ("Bianco", 30), ("Blu", 15), ("Bianco_TelaBeige", 10)],
  "V9": [("Bianco_CoprirandaBlu", 50), ("Bianco", 30), ("Blu", 20)],
  "V11": [("base", 1)], "Y13": [("base", 1)],
}
def wpick(lst):
    tot = sum(w for _, w in lst); r = random.uniform(0, tot)
    for v, w in lst:
        r -= w
        if r <= 0: return v
    return lst[-1][0]

MIX_6   = [("G", 45), ("Z", 55)]
MIX_75  = [("G", 20), ("Z", 35), ("M", 45)]
MIX_9   = [("G", 8), ("Z", 12), ("M", 50), ("V9", 30)]
MIX_11  = [("Z", 5), ("M", 40), ("V9", 25), ("V11", 30)]
MIX_13  = [("M", 15), ("V11", 30), ("Y13", 55)]
MIX_VELA= [("V9", 50), ("V11", 50)]

# lato: (pontile, segmento, lato +1 = normale sinistra, Lmax, mix, riempimento, t0, t1)
SIDES = [
  ("L_Testa", 0, +1, 11.0, MIX_VELA, 0.9),   # sud (dir -X -> sinistra = -Y)
  ("L_Testa", 0, -1, 6.0, MIX_6, 0.85),      # nord
  ("L_Ramo", 0, +1, 6.0, MIX_6, 0.85),       # sud
  ("L_Ramo", 0, -1, 6.0, MIX_6, 0.85),       # nord
  ("L_Gamba", 0, +1, 7.5, MIX_75, 0.85),     # est (dir -Y -> sinistra = +X)
  ("L_Gamba", 1, +1, 7.5, MIX_75, 0.85),
  ("L_Gamba", 0, -1, 6.0, MIX_6, 0.85),      # ovest
  ("L_Gamba", 1, -1, 6.0, MIX_6, 0.85),
  ("F1", 0, +1, 6.0, MIX_6, 0.85), ("F1", 0, -1, 6.0, MIX_6, 0.85),
  ("F2", 0, +1, 6.0, MIX_6, 0.85), ("F2", 0, -1, 7.5, MIX_75, 0.85),
  ("F3", 0, +1, 7.5, MIX_75, 0.85), ("F3", 0, -1, 9.0, MIX_9, 0.85),
  ("F4", 0, +1, 9.0, MIX_9, 0.85), ("F4", 0, -1, 9.0, MIX_9, 0.85),
  ("F5", 0, +1, 9.0, MIX_9, 0.85), ("F5", 0, -1, 9.0, MIX_9, 0.85),
  ("F6", 0, +1, 9.0, MIX_9, 0.85), ("F6", 0, -1, 11.0, MIX_11, 0.85),
  ("F7", 0, +1, 10.0, MIX_11, 0.85), ("F7", 0, -1, 11.0, MIX_11, 0.85),
  ("F8", 0, +1, 9.0, MIX_9, 0.85), ("F8", 0, -1, 13.2, MIX_13, 0.85),
  ("Esterno", 0, +1, 13.2, MIX_13, 0.8), ("Esterno", 0, -1, 13.2, MIX_13, 0.7),
  ("Esterno2", 2, +1, 13.2, MIX_13, 0.7),
  ("Spina", 0, -1, 13.2, MIX_13, 0.5),       # ovest (dir -Y -> destra = -X)
  ("Spina", 1, -1, 11.0, MIX_11, 0.5), ("Spina", 2, -1, 11.0, MIX_11, 0.5), ("Spina", 3, -1, 13.2, MIX_13, 0.5),
  ("NE", 0, -1, 11.0, MIX_11, 0.85),         # ovest
  ("NE", 0, +1, 7.5, MIX_75, 0.7),           # est
]

boats = []; placed = []
stats = Counter(); per_side = []
GAP = 0.4
for (pn, si, side, Lmax, mix, fill) in SIDES:
    pts, w, flo, osm = PONTILI[pn]
    a, b = pts[si], pts[si + 1]
    d, L = unit(a, b)
    nL = (-d[1], d[0]); n = (nL[0] * side, nL[1] * side)
    allowed = [(k, wt) for k, wt in mix if T[k]["L"] <= Lmax]
    t = 1.0; cnt = 0
    while True:
        k = wpick(allowed); ty = T[k]
        pitch = ty["B"] + 0.7
        if t + pitch > L - 0.5: break
        tc = t + pitch / 2; t += pitch
        if random.random() > fill: continue
        jit = random.uniform(-0.15, 0.25)
        edge = (a[0] + d[0] * tc + n[0] * (w / 2 + GAP + jit), a[1] + d[1] * tc + n[1] * (w / 2 + GAP + jit))
        bowto = (k in ("G", "Z") and random.random() < 0.3)
        if not bowto:
            bd = n; org = (edge[0] - bd[0] * ty["xs"], edge[1] - bd[1] * ty["xs"])
        else:
            bd = (-n[0], -n[1]); org = (edge[0] + n[0] * ty["xb"], edge[1] + n[1] * ty["xb"])
        cx = (ty["xs"] + ty["xb"]) / 2
        rect = ((org[0] + bd[0] * cx, org[1] + bd[1] * cx), bd, ty["L"] / 2 + 0.2, ty["B"] / 2 + 0.1)
        if any(sat(rect, r) for r in seg_rects): stats["scarto_pontile_"+pn+str(si)+("+" if side>0 else "-")] += 1; continue
        if any(sat(rect, r) for r in RESERVED): stats["scarto_zona_riservata"] += 1; continue
        if near_ferry(rect): stats["scarto_rotta_traghetti"] += 1; continue
        if any(sat(rect, r) for r in placed): stats["scarto_barca"] += 1; continue
        placed.append(rect)
        yaw = yaw_ue(bd) + random.uniform(-2.0, 2.0)
        boats.append((k, org, yaw, wpick(COLORI[k]), pn, bowto))
        cnt += 1
    per_side.append((pn, si, side, Lmax, cnt))

rows_b = []
for i, (k, org, yaw, var, pn, bowto) in enumerate(boats):
    ty = T[k]
    rows_b.append((ty["asset"], f"Barca_{pn}_{i:03d}", org[0] * 100, -org[1] * 100, ty["z"], yaw, 0.0, 0.0, var + ("_prua" if bowto else "")))

def write(path, rows):
    with open(path, "w", newline="\n") as f:
        f.write("asset,nome,x,y,z,yaw,pitch,roll,variante\n")
        for r in rows:
            f.write(f"{r[0]},{r[1]},{r[2]:.1f},{r[3]:.1f},{r[4]:.1f},{r[5]:.2f},{r[6]:.2f},{r[7]:.2f},{r[8]}\n")
write(os.path.join(OUT, "marina_pontili_v1.csv"), rows_p)
write(os.path.join(OUT, "marina_barche_v1.csv"), rows_b)

print("LUNGHEZZE", {k: round(v, 1) for k, v in lengths.items()})
print("MODULI", dict(mod_count), "righe pontili", len(rows_p))
c = Counter(b[0] for b in boats); print("BARCHE", len(boats), dict(c))
cat = Counter(T[b[0]]["cat"] for b in boats); print("CATEGORIE", {k: f"{v} ({100*v/len(boats):.0f}%)" for k, v in cat.items()})
print("SCARTI", dict(stats))
print("BOW-TO", sum(1 for b in boats if b[5]))
for s in per_side: print("  LATO", s)
var = Counter((b[0], b[3]) for b in boats); print("VARIANTI", dict(var))
