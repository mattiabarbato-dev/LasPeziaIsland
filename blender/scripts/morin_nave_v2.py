"""morin_nave_v2.py — nave da crociera "Piccionissima" v2 (fondale del Molo Italia), 2026-11-20.

v1 (SM_MoloItalia_NaveCrociera): 250 x 32,3 m, 52 m sull'acqua, posata nel bacino a ~230 m dal faro con yaw 74:
troppo VICINA e di traverso, per questo sembrava enorme. v2: scala di una nave tipica (300 x 38 m, ~60 m sull'acqua),
ormeggiata alla posizione reale, sul fianco ovest del Molo Garibaldi (OSM: coastline 137121074, tratto da
(1350; -147) a (887; -574) in coordinate di progetto, nodo "Molo Garibaldi" 3701128402), prua verso la testata come
nelle foto faro_2 / molo_italia_6. Sagoma piu' credibile: scafo affusolato con prua slanciata e specchio di poppa,
ponte di passeggio rientrato con le scialuppe, sovrastruttura con fronte arrotondato e terrazze di poppa a gradoni
digradanti, alette di plancia, fumaiolo ellittico inclinato, albero radar; dettaglio (oblo', balconi, finestre, piscine,
livrea inventata, nome) in un atlante PBR 2048.

Origine: centro nave alla linea di galleggiamento; prua verso +X. Si posa a Z_W (-1,03 m).
Esegui dentro blender/arte_molo_italia.blend:
    import morin_nave_v2 as nv; importlib.reload(nv)
    nv.make_textures(); nv.build_material(); nv.build_all(); nv.qa(); nv.export_all(); nv.write_csv()
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

import morin_pav_kit as pk
import morin_texphoto as tp
import morin_chiosco_ott_v3 as c3        # Builder, rasterizzatore di testo

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/molo_italia"
EXPDIR = "//../exports/molo_italia"
KIT, CTX = "MI_Kit", "MI_Contesto"
NAME = "SM_MoloItalia_NaveCrociera_v2"
MAT = "M_MoloItalia_NaveCrociera_v2"
NOME = "PICCIONISSIMA"
S = 2048
Z_W = -1.03

L, B, T = 300.0, 38.0, 8.5          # lunghezza, larghezza, immersione
Z_H = 16.0                          # ponte di coperta (fine dello scafo bianco)
Z_P = 22.0                          # ponte di passeggio rientrato (scialuppe) 16 -> 22
DECK = 3.0
N_DECK = 9                          # 22 -> 49
Z_TOP = Z_P + N_DECK * DECK          # 49
X_SUP0, X_SUP1 = -L / 2 + 14.0, L / 2 - 62.0     # sovrastruttura (poppa, fronte)

# --- posizione (coordinate di progetto) ---
GARIBALDI_A, GARIBALDI_B = Vector((1350.0, -147.0)), Vector((887.0, -574.0))   # radice -> testata, fianco ovest
BERTH_T = 0.52                       # frazione lungo il fianco del centro nave
BERTH_GAP = 2.5                      # distanza dal ciglio

REG = {
    "scafo": (0.0, 0.75, 1.0, 1.0), "sovra": (0.0, 0.5, 1.0, 0.75),
    "piscine": (0.0, 0.25, 0.5, 0.5), "ponte": (0.5, 0.25, 0.75, 0.5), "fumaiolo": (0.75, 0.25, 1.0, 0.5),
    "scialuppa": (0.0, 0.0, 0.25, 0.25), "bianco": (0.25, 0.125, 0.375, 0.25), "scuro": (0.375, 0.125, 0.5, 0.25),
    "rosso": (0.25, 0.0, 0.375, 0.125), "vetro": (0.375, 0.0, 0.5, 0.125), "grigio": (0.5, 0.125, 0.625, 0.25),
}
Z_SC0, Z_SC1 = -T, Z_H               # fascia verticale della regione scafo
Z_SV0, Z_SV1 = Z_H, Z_TOP + 3.0      # regione sovrastruttura

BIANCO = (236, 238, 240)
BLU = (22, 40, 74)
TEAL = (0, 120, 140)


# =============================================================================================================
# texture
# =============================================================================================================
def _c(c):
    return np.asarray(c, np.float32) / 255.0


def _reg(A, key, w_m, h_m):
    return A.region(key, w_m, h_m)


def _set(D, R, M, sel, col, rough, metal=0.0):
    D[sel] = _c(col)
    R[sel] = rough
    M[sel] = metal


def make_textures():
    A = c3.Atlas(REG)
    rng = np.random.default_rng(7)
    # --- scafo: u = metri lungo la nave (0 = estremo di sinistra visto da fuori), v = z da -T a Z_H
    D, H, R, M, U, Z = A.region("scafo", L, Z_SC1 - Z_SC0)
    Z = Z + Z_SC0
    hh, ww = D.shape[:2]
    n = c3._noise(hh, ww, 2.0, 1)
    D[:] = _c(BIANCO)[None, None] * (1 + 0.012 * n)[..., None]
    R[:] = 0.35
    _set(D, R, M, Z < -0.6, (150, 40, 36), 0.7)                     # antivegetativa
    _set(D, R, M, (Z >= -0.6) & (Z < 1.4), BLU, 0.4)                 # bagnasciuga blu
    _set(D, R, M, (Z > 13.6) & (Z < 14.1), TEAL, 0.35)               # filetto
    for zr, step, r in ((5.0, 1.6, 0.22), (7.8, 1.6, 0.22), (10.6, 2.0, 0.3)):     # oblo' degli alloggi equipaggio
        ph = np.mod(U, step) - step / 2
        sel = (ph ** 2 + ((Z - zr) * 1.0) ** 2 < r * r) & (U > 30) & (U < L - 30)
        _set(D, R, M, sel, (40, 52, 62), 0.1)
    # colature di ruggine sotto gli ombrinali
    for u0 in rng.uniform(10, L - 10, 40):
        sel = (np.abs(U - u0) < 0.12) & (Z < 13.5) & (Z > 13.5 - rng.uniform(1, 4))
        D[sel] *= np.array([0.92, 0.86, 0.80], np.float32)
    # porte del portellone e cubie dell'ancora ai due estremi
    for ua in (14.0, L - 14.0):
        sel = ((U - ua) ** 2 + (Z - 11.5) ** 2) < 1.0
        _set(D, R, M, sel, (60, 60, 64), 0.5, 0.6)
    # nome a prua su entrambi i fianchi (a sinistra e a destra della regione) e porto di iscrizione
    for x0 in (0.06, 0.64):
        m = c3._mask_text(NOME, ww * x0, hh * (1 - (13.0 - Z_SC0) / (Z_SC1 - Z_SC0)), ww * 0.30, hh * 0.085, ww, hh, 1.05)
        D[:] = D * (1 - m[..., None]) + _c(BLU)[None, None] * m[..., None]
    # --- sovrastruttura: u = metri, v = z da Z_H a Z_TOP + 3
    D, H, R, M, U, Z = A.region("sovra", L, Z_SV1 - Z_SV0)
    Z = Z + Z_SV0
    hh, ww = D.shape[:2]
    D[:] = _c(BIANCO)
    R[:] = 0.35
    # ponte di passeggio (16-22): vetrate scure e montanti
    prom = (Z > Z_H + 1.2) & (Z < Z_P - 0.8)
    _set(D, R, M, prom & (np.mod(U, 4.0) > 0.35), (34, 46, 58), 0.08)
    _set(D, R, M, (Z > Z_P - 0.5) & (Z < Z_P - 0.2), TEAL, 0.3)
    # ponti con balconi (22 -> 40): porte vetrate scure, parapetto in vetro azzurrato, divisori bianchi ogni 3,6 m
    for k in range(6):
        z0 = Z_P + k * DECK
        door = (Z > z0 + 0.15) & (Z < z0 + 2.45)
        _set(D, R, M, door, (44, 58, 70), 0.06)
        rail = (Z > z0 + 0.10) & (Z < z0 + 1.15)
        D[rail] = D[rail] * 0.45 + _c((150, 178, 190)) * 0.55
        part = (np.mod(U, 3.6) < 0.18) & (Z > z0) & (Z < z0 + DECK)
        _set(D, R, M, part, BIANCO, 0.35)
        _set(D, R, M, (Z > z0 + 2.65) & (Z < z0 + DECK), (226, 228, 230), 0.4)      # soletta del ponte superiore
        _set(D, R, M, (Z > z0 + 1.12) & (Z < z0 + 1.18), (200, 204, 206), 0.3, 0.6)  # corrimano
    # ponti pubblici (40 -> 46): grandi vetrate
    for k in range(2):
        z0 = Z_P + (6 + k) * DECK
        _set(D, R, M, (Z > z0 + 0.5) & (Z < z0 + 2.5) & (np.mod(U, 6.0) > 0.4), (30, 44, 58), 0.05)
    # plancia / ponte sole (46 -> 49): fascia scura continua; sopra parapetto bianco
    z0 = Z_P + 8 * DECK
    _set(D, R, M, (Z > z0 + 0.6) & (Z < z0 + 2.2), (20, 26, 34), 0.05)
    D *= (1 - 0.06 * np.clip(c3._noise(hh, ww, 30, 3), 0, None))[..., None]
    # --- ponti: legno e grigio; con piscine e lettini
    for key, pools in (("piscine", True), ("ponte", False)):
        D, H, R, M, U, Z = A.region(key, 40.0, 30.0)
        hh, ww = D.shape[:2]
        D[:] = _c((176, 160, 138))
        R[:] = 0.6
        pl = np.mod(Z, 0.15) < 0.012
        D[pl] *= 0.8
        H[pl] -= 0.4
        _set(D, R, M, (U < 3) | (U > 37), (120, 126, 132), 0.6)
        if pools:
            for cx, cz, w, h in ((12.0, 15.0, 9.0, 6.0), (27.0, 15.0, 6.0, 5.0)):
                p = (np.abs(U - cx) < w / 2) & (np.abs(Z - cz) < h / 2)
                _set(D, R, M, p, (40, 150, 196), 0.05)
                e = p & ~((np.abs(U - cx) < w / 2 - 0.4) & (np.abs(Z - cz) < h / 2 - 0.4))
                _set(D, R, M, e, (230, 230, 225), 0.4)
            for k in range(14):
                lx = 4.5 + k * 2.2
                for lz in (6.0, 24.0):
                    _set(D, R, M, (np.abs(U - lx) < 0.35) & (np.abs(Z - lz) < 1.0), (240, 240, 236), 0.5)
                    _set(D, R, M, (np.abs(U - lx) < 0.9) & (np.abs(Z - lz - 2.0) < 0.06) & (k % 3 == 0),
                         (30, 120, 150), 0.5)
    # --- fumaiolo: bianco, fascia teal con gabbiano-piccione stilizzato (livrea inventata), cappello nero
    D, H, R, M, U, Z = A.region("fumaiolo", 1.0, 1.0)
    hh, ww = D.shape[:2]
    D[:] = _c(BIANCO)
    R[:] = 0.35
    _set(D, R, M, (Z > 0.45) & (Z < 0.78), TEAL, 0.35)
    _set(D, R, M, Z > 0.88, (24, 24, 26), 0.6)
    for cx in (0.25, 0.75):
        bird = c3._poly_mask([c3._seagull(ww * cx, hh * (1 - 0.615), hh * 0.12)], ww, hh)
        D[:] = D * (1 - bird[..., None]) + _c(BIANCO)[None, None] * bird[..., None]
    # --- scialuppe: arancio con tettuccio bianco e finestrini
    D, H, R, M, U, Z = A.region("scialuppa", 1.0, 1.0)
    D[:] = _c((236, 110, 30))
    R[:] = 0.45
    _set(D, R, M, Z > 0.62, (236, 236, 230), 0.4)
    _set(D, R, M, (Z > 0.66) & (Z < 0.74) & (np.mod(U, 0.12) < 0.07), (40, 50, 60), 0.1)
    for key, col, rough, met in (("bianco", BIANCO, 0.35, 0.0), ("scuro", (40, 44, 50), 0.4, 0.3),
                                 ("rosso", (150, 40, 36), 0.7, 0.0), ("vetro", (28, 40, 52), 0.05, 0.0),
                                 ("grigio", (150, 154, 158), 0.4, 0.6)):
        A.fill(key, col, rough, metal=met, seed=hash(key) % 1000, var=0.015)
    A.D = np.clip(A.D, 0, 1)
    os.makedirs(TEXDIR, exist_ok=True)
    nrm = tp.normal_dx(A.H, 2.0)
    tp.save(A.D, f"{TEXDIR}/T_MoloItalia_NaveCrociera_v2_D.png")
    tp.save(nrm, f"{TEXDIR}/T_MoloItalia_NaveCrociera_v2_N.png")
    tp.save(np.dstack([np.ones_like(A.R), np.clip(A.R, 0.04, 1), A.M]), f"{TEXDIR}/T_MoloItalia_NaveCrociera_v2_ORM.png")


def build_material():
    b = f"{TEXDIR}/T_MoloItalia_NaveCrociera_v2"
    m = pk._pbr_material(MAT, b + "_D.png", b + "_N.png", b + "_ORM.png")
    for im in bpy.data.images:
        if im.name.startswith("T_MoloItalia_NaveCrociera_v2"):
            im.reload()
    return m


# =============================================================================================================
# geometria
# =============================================================================================================
def _half_w(x, z):
    """Mezza larghezza dello scafo alla stazione x e quota z (prua affusolata e slanciata, poppa leggermente stretta)."""
    xb = L / 2 - 55.0
    rake = 14.0 * (Z_H - z) / (Z_H + T)                 # il dritto di prua arretra in basso
    tip = L / 2 - rake
    w = B / 2
    if x > xb:
        t = min(max((x - xb) / max(tip - xb, 1e-3), 0.0), 1.0)
        w *= math.sqrt(max(1.0 - t ** 2.2, 0.0)) * (0.9 + 0.1 * (z + T) / (Z_H + T))
    if x < -L / 2 + 25.0:
        w *= 0.93 + 0.07 * (x + L / 2) / 25.0
    if z < -2.0:                                          # sentina
        w *= 1.0 - 0.12 * ((-2.0 - z) / (T - 2.0)) ** 2
    return max(w, 0.15)


def _hull(B_):
    xs = list(np.linspace(-L / 2, L / 2 - 60, 12)) + list(L / 2 - 60 + (60.0 * np.linspace(0, 1, 12)[1:]) ** 1.0)
    zs = [-T, -T + 1.5, -4.0, -1.0, 2.0, 7.0, 12.0, Z_H]
    rows = []
    for x in xs:
        xb = L / 2 - 55.0
        row = []
        for z in zs:
            rake = 14.0 * (Z_H - z) / (Z_H + T)
            xx = x if x <= xb else xb + (x - xb) * (L / 2 - rake - xb) / (L / 2 - xb)
            row.append((xx, _half_w(x, z), z))
        rows.append(row)
    for s in (1, -1):
        for i in range(len(rows) - 1):
            for j in range(len(zs) - 1):
                a, b, c, d = rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1]
                pts = [(p[0], s * p[1], p[2]) for p in (a, b, c, d)]
                B_.face(pts, (0, s, 0), "scafo", ("hull", s))
    # chiglia piatta, coperta, specchio di poppa, dritto di prua
    for i in range(len(rows) - 1):
        a, b = rows[i][0], rows[i + 1][0]
        B_.face([(a[0], a[1], a[2]), (b[0], b[1], b[2]), (b[0], -b[1], b[2]), (a[0], -a[1], a[2])], (0, 0, -1), "rosso")
        a, b = rows[i][-1], rows[i + 1][-1]
        B_.face([(a[0], a[1], a[2]), (b[0], b[1], b[2]), (b[0], -b[1], b[2]), (a[0], -a[1], a[2])], (0, 0, 1), "ponte")
    for row, d in ((rows[0], -1), (rows[-1], 1)):
        pts = [(p[0], p[1], p[2]) for p in row] + [(p[0], -p[1], p[2]) for p in reversed(row)]
        for j in range(len(row) - 1):
            a, b = row[j], row[j + 1]
            B_.face([(a[0], a[1], a[2]), (b[0], b[1], b[2]), (b[0], -b[1], b[2]), (a[0], -a[1], a[2])], (d, 0, 0),
                    "scafo", ("end", d))


def _plan(x0, x1, hw, nose=0.0, n=6, tail=0.0):
    """Pianta della sovrastruttura in senso antiorario: poppa dritta (con smusso `tail`), fronte arrotondato di raggio
    `nose` (semi-ellisse)."""
    pts = [(x0 + tail, -hw), (x1 - nose, -hw)]
    for k in range(1, n):
        a = -math.pi / 2 + math.pi * k / n
        pts.append((x1 - nose + nose * math.cos(a), hw * math.sin(a)))
    pts += [(x1 - nose, hw), (x0 + tail, hw)]
    if tail > 0:
        pts += [(x0, hw - tail), (x0, -hw + tail)]
    return pts


def _prism(B_, plan, z0, z1, reg_side, reg_top, top=True, bottom=False):
    n = len(plan)
    c = Vector((sum(p[0] for p in plan) / n, sum(p[1] for p in plan) / n, 0))
    for i in range(n):
        a, b = plan[i], plan[(i + 1) % n]
        mid = Vector(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0))
        e = Vector((b[0] - a[0], b[1] - a[1], 0))
        out = Vector((e.y, -e.x, 0))
        if out.dot(mid - c) < 0:
            out = -out
        B_.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], out, reg_side, ("sup",))
    if top:
        B_.face([(p[0], p[1], z1) for p in plan], (0, 0, 1), reg_top)
    if bottom:
        B_.face([(p[0], p[1], z0) for p in plan], (0, 0, -1), "bianco")


def _boat(B_, cx, cy, z0, lod):
    """Scialuppa chiusa 10 x 3,8 x 3 m: sezione esagonale, estremi rastremati."""
    ln, bw, h = 10.0, 3.8, 3.0
    if lod >= 1:
        P = [Vector(p) for p in ((cx - ln / 2, cy - bw / 2, z0), (cx + ln / 2, cy - bw / 2, z0), (cx + ln / 2, cy + bw / 2, z0),
                                 (cx - ln / 2, cy + bw / 2, z0))]
        P += [p + Vector((0, 0, h)) for p in P]
        B_.solid(P, ["top", "bot", "f0", "f1", "f2", "f3"], {"*": "scialuppa"})
        return
    sec = [(0.0, -0.5), (0.45, -0.25), (0.5, 0.25), (0.35, 0.5), (-0.35, 0.5), (-0.5, 0.25), (-0.45, -0.25)]
    st = [(-0.5, 0.55), (-0.38, 0.95), (0.38, 0.95), (0.5, 0.6)]
    rings = []
    for fx, sc in st:
        rings.append([Vector((cx + fx * ln, cy + sy * bw * sc, z0 + h / 2 + sz * h)) for sy, sz in sec])
    for i in range(len(rings) - 1):
        for j in range(len(sec)):
            k = (j + 1) % len(sec)
            q = [rings[i][j], rings[i + 1][j], rings[i + 1][k], rings[i][k]]
            mid = sum(q, Vector()) / 4
            B_.face(q, mid - Vector((mid.x, cy, z0 + h / 2)) * 1.0 + Vector((0, 0, 0)), "scialuppa")
    for r, d in ((rings[0], -1), (rings[-1], 1)):
        B_.face(r, (d, 0, 0), "scialuppa")


def _funnel(B_, cx, z0, z1, a, b, rake, n):
    rings = []
    for z, sc in ((z0, 1.0), (z1, 0.85)):
        off = (z - z0) * math.tan(math.radians(rake))
        rings.append([Vector((cx - off + a * sc * math.cos(2 * math.pi * k / n), b * sc * math.sin(2 * math.pi * k / n), z))
                      for k in range(n)])
    for k in range(n):
        j = (k + 1) % n
        q = [rings[0][k], rings[0][j], rings[1][j], rings[1][k]]
        mid = sum(q, Vector()) / 4
        cen = Vector((cx - (mid.z - z0) * math.tan(math.radians(rake)), 0, mid.z))
        B_.face(q, mid - cen, "fumaiolo", ("funnel", cx, z0, z1, rake))
    B_.face(rings[1], (0, 0, 1), "scuro")


def build(coll, lod=0, name=NAME):
    Bd = c3.Builder()
    _hull(Bd)
    hw = B / 2 - 0.4
    # ponte di passeggio rientrato con le scialuppe
    _prism(Bd, _plan(-L / 2 + 22, L / 2 - 58, B / 2 - 3.0, nose=14.0, tail=4.0), Z_H, Z_P, "sovra", "ponte")
    if lod < 2 or True:
        xs = np.linspace(-L / 2 + 50, L / 2 - 80, 9)
        for s in (1, -1):
            for x in xs:
                _boat(Bd, float(x), s * (B / 2 - 1.6), Z_H + 1.4, lod if lod < 2 else 1)
    # sovrastruttura: un prisma per ponte; poppa a gradoni digradanti, fronte arretrato e arrotondato in alto
    for d in range(N_DECK):
        z0 = Z_P + d * DECK
        x0 = X_SUP0 + max(0, d - 3) ** 1.35 * 4.5                  # terrazze di poppa
        x1 = X_SUP1 - d * 1.6                                        # fronte inclinato
        nose = 16.0 + d * 0.6
        _prism(Bd, _plan(x0, x1, hw, nose=nose, n=(8, 6, 4)[lod], tail=3.0), z0, z0 + DECK, "sovra",
               "piscine" if d == N_DECK - 1 else "ponte", bottom=(d == 0))
    # alette di plancia (ponte 8) e frangivento
    zb = Z_P + 7 * DECK
    xbw = X_SUP1 - 7 * 1.6 - 16.0
    P = [Vector(p) for p in ((xbw - 6, -B / 2 - 0.6, zb), (xbw + 2, -B / 2 - 0.6, zb), (xbw + 2, B / 2 + 0.6, zb),
                             (xbw - 6, B / 2 + 0.6, zb))]
    P += [p + Vector((0, 0, DECK)) for p in P]
    Bd.solid(P, ["top", "bot", "f0", "f1", "f2", "f3"], {"f1": "vetro", "*": "sovra"},
             {"f0": ("sup",), "f2": ("sup",), "f3": ("sup",)})
    # sporting deck sopra la plancia e albero radar
    xs0 = X_SUP1 - 8 * 1.6 - 40.0
    _prism(Bd, _plan(xs0, xs0 + 26, 9.0, nose=6.0, n=(6, 4, 3)[lod]), Z_TOP, Z_TOP + 3.0, "sovra", "ponte")
    xm = xs0 + 16
    for (a0, a1, b0, b1, z0, z1, reg) in ((-0.6, 0.6, -0.6, 0.6, Z_TOP + 3, Z_TOP + 11, "bianco"),
                                         (-0.4, 0.4, -4.5, 4.5, Z_TOP + 9.0, Z_TOP + 9.6, "bianco")):
        P = [Vector((xm + a, b, z)) for z in (z0, z1) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
        Bd.solid(P, ["top", "bot", "f0", "f1", "f2", "f3"] if lod < 2 else ["top", "f0", "f1", "f2", "f3"], {"*": reg})
    # fumaiolo ellittico inclinato a poppa del ponte sole (sale fino a ~60 m sull'acqua)
    fx = X_SUP0 + 62.0
    _funnel(Bd, fx, Z_TOP, Z_TOP + 12.0, 9.5, 5.0, 14.0, (16, 10, 8)[lod])
    # scivolo/pergola sul ponte piscine (sagoma): due archi bassi
    if lod == 0:
        for xo in (-25.0, -8.0):
            P = [Vector((fx + 35 + xo + a, b, z)) for z in (Z_TOP, Z_TOP + 2.6)
                 for a, b in ((-4, -8), (4, -8), (4, 8), (-4, 8))]
            Bd.solid(P, ["top", "f0", "f1", "f2", "f3"], {"*": "bianco"})
    bm = Bd.bm
    bm.normal_update()
    for f in bm.faces:
        reg, fr = Bd.info[f]
        _uv(f, Bd.uv, reg, fr)
        f.material_index = 0
    o = pk._finish(name + ("" if lod == 0 else f"_LOD{lod}"), bm, [MAT], coll, uv=None, smooth_angle=None)
    for l in [l for l in o.data.uv_layers if l.name != "UVMap"]:
        o.data.uv_layers.remove(l)
    if lod == 0:
        pk._ucx(name, [(-L / 2, L / 2 - 15, -B / 2, B / 2, -T, Z_H)], coll)
        pk._ucx(name, [(X_SUP0, X_SUP1, -B / 2, B / 2, Z_H, Z_TOP)], coll, start=1)
    return o


def _uv(f, lay, reg, fr):
    r = REG[reg]
    n = f.normal

    def put(fn):
        for lp in f.loops:
            a, b = fn(lp.vert.co)
            lp[lay].uv = (r[0] + (r[2] - r[0]) * min(max(a, 0.0), 1.0), r[1] + (r[3] - r[1]) * min(max(b, 0.0), 1.0))
    if fr is not None and fr[0] == "hull":
        s = fr[1]
        # vista da fuori: fianco sinistro (+Y) ha la destra verso -X, fianco destro verso +X; prua all'estremo esterno
        put(lambda c: (((L / 2 - c.x) if s > 0 else (c.x + L / 2)) / L, (c.z - Z_SC0) / (Z_SC1 - Z_SC0)))
        return
    if fr is not None and fr[0] == "end":
        put(lambda c: (0.5 + 0.02 * c.y / (B / 2), (c.z - Z_SC0) / (Z_SC1 - Z_SC0)))
        return
    if fr is not None and fr[0] == "sup":
        if abs(n.y) >= abs(n.x):
            put(lambda c: ((L / 2 - c.x) / L if n.y > 0 else (c.x + L / 2) / L, (c.z - Z_SV0) / (Z_SV1 - Z_SV0)))
        else:
            put(lambda c: ((c.y + B / 2) / L + (0.3 if n.x > 0 else 0.6), (c.z - Z_SV0) / (Z_SV1 - Z_SV0)))
        return
    if fr is not None and fr[0] == "funnel":
        # proiezione cilindrica attorno all'asse inclinato; u = angolo / 2 pi, senza salto sulla cucitura
        _, cx, z0, z1, rake = fr
        us = []
        for lp in f.loops:
            c = lp.vert.co
            ax = cx - (c.z - z0) * math.tan(math.radians(rake))
            us.append((math.atan2(c.y, c.x - ax) / (2 * math.pi)) % 1.0)
        if max(us) - min(us) > 0.5:
            us = [u + 1.0 if u < 0.5 else u for u in us]
        for lp, u in zip(f.loops, us):
            lp[lay].uv = (r[0] + (r[2] - r[0]) * min(u / 1.13, 1.0),
                          r[1] + (r[3] - r[1]) * (lp.vert.co.z - z0) / (z1 - z0))
        return
    _fit(f, lay, r)


def _fit(f, lay, r):
    n = f.normal
    right = Vector((1, 0, 0)) if abs(n.z) > 0.95 else (-n).cross(Vector((0, 0, 1))).normalized()
    up = n.cross(right).normalized()
    pts = [(lp.vert.co.dot(right), lp.vert.co.dot(up)) for lp in f.loops]
    a0, a1 = min(p[0] for p in pts), max(p[0] for p in pts)
    b0, b1 = min(p[1] for p in pts), max(p[1] for p in pts)
    m = 0.01
    for lp, (a, b) in zip(f.loops, pts):
        lp[lay].uv = (r[0] + (r[2] - r[0]) * (m + (1 - 2 * m) * (a - a0) / max(a1 - a0, 1e-6)),
                      r[1] + (r[3] - r[1]) * (m + (1 - 2 * m) * (b - b0) / max(b1 - b0, 1e-6)))


# =============================================================================================================
# build, QA, posizione, export
# =============================================================================================================
def build_all():
    coll = pk._coll(KIT)
    rep = {}
    for lod in range(3):
        o = build(coll, lod)
        rep[o.name] = (pk.tri_count(o), tuple(round(d, 2) for d in o.dimensions))
    for o in coll.objects:
        if o.name.startswith(NAME) or o.name.startswith("UCX_" + NAME):
            hide = o.name.startswith("UCX") or "_LOD" in o.name
            o.hide_render = hide
            o.hide_viewport = hide
    for k, v in rep.items():
        print(k, "tri", v[0], "dim", v[1])
    return rep


def qa():
    from mathutils.bvhtree import BVHTree
    out = {}
    d0 = None
    for lod in range(3):
        nm = NAME + ("" if lod == 0 else f"_LOD{lod}")
        o = bpy.data.objects[nm]
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        bvh = BVHTree.FromBMesh(bm)
        bad = 0
        tot = 0
        for x in np.linspace(-L / 2 + 5, L / 2 - 5, 30):
            for z in np.linspace(-T + 0.5, Z_TOP + 8, 14):
                for s in (1, -1):
                    h = bvh.ray_cast(Vector((x, s * 60, z)), Vector((0, -s, 0)))
                    if h[0] is not None:
                        tot += 1
                        if bm.faces[h[2]].normal.dot(Vector((0, -s, 0))) > 0:
                            bad += 1
        for x in np.linspace(-L / 2 + 5, L / 2 - 5, 30):
            for y in np.linspace(-B / 2 + 1, B / 2 - 1, 8):
                h = bvh.ray_cast(Vector((x, y, 100)), Vector((0, 0, -1)))
                if h[0] is not None:
                    tot += 1
                    if bm.faces[h[2]].normal.z < 0:
                        bad += 1
        zero = sum(1 for f in bm.faces if f.calc_area() < 1e-6)
        bm.free()
        dims = tuple(round(v, 2) for v in o.dimensions)
        d0 = d0 or dims
        dev = max(abs(a - b) / b for a, b in zip(dims, d0)) * 100
        out[nm] = dict(tri=pk.tri_count(o), dim=dims, zmax=round(max((o.matrix_world @ Vector(c)).z for c in o.bound_box), 2),
                       rays=tot, back=bad, zero=zero, bbox_dev=round(dev, 2))
        print(nm, out[nm])
    return out


def berth():
    """Centro (x, y) e rotZ Blender all'ormeggio sul fianco ovest del Molo Garibaldi, prua verso la testata."""
    d = (GARIBALDI_B - GARIBALDI_A).normalized()
    p = GARIBALDI_A + (GARIBALDI_B - GARIBALDI_A) * BERTH_T
    nrm = Vector((-d.y, d.x))
    if nrm.dot(Vector((680.0, -330.0)) - p) < 0:          # verso il bacino del Molo Italia
        nrm = -nrm
    c = p + nrm * (B / 2 + BERTH_GAP)
    return c.x, c.y, math.degrees(math.atan2(d.y, d.x))


def place_context():
    x, y, rz = berth()
    src = bpy.data.objects.get("CTX_MI_NaveCrociera")
    if src is not None:
        src.hide_viewport = True
        src.hide_render = True
    o = bpy.data.objects.get("CTX_MI_NaveCrociera_v2")
    if o is None:
        o = bpy.data.objects.new("CTX_MI_NaveCrociera_v2", bpy.data.objects[NAME].data)
        pk._coll(CTX).objects.link(o)
    o.location = (x, y, Z_W)
    o.rotation_euler = (0, 0, math.radians(rz))
    return o


def write_csv(path="exports/molo_italia/molo_italia_posizioni_v2.csv"):
    """Solo la riga della nave (nuovo asset e nuova posizione)."""
    import morin_blocco2 as b2
    x, y, rz = berth()
    yaw = -rz
    lines = ["asset,nome,x,y,z,yaw,scala,gruppo",
             f"{NAME},MI_NaveCrociera_v2,{b2._ue(x * 100)},{b2._ue(-y * 100)},{b2._ue(Z_W * 100)},{yaw:.4f},1.000,fondale"]
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print(path, lines[1])
    return path


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    coll = bpy.data.collections[KIT]
    objs = [o for o in coll.objects if o.name.startswith(NAME) or o.name.startswith("UCX_" + NAME)]
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in objs}
    for o in objs:
        o.hide_viewport = False
        o.hide_set(False)
    bpy.context.view_layer.update()
    reps = []
    try:
        for lod in range(3):
            on = NAME + ("" if lod == 0 else f"_LOD{lod}")
            reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                                overwrite=overwrite, include_ucx=(lod == 0), bake_rotation=(lod > 0),
                                                verbose=False))
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps
