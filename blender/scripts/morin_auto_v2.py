"""morin_auto_v2.py — auto generiche v2 (2026-11-20): utilitaria 5 porte (A), SUV compatto (B), station wagon (C).

Sostituisce nei CSV nuovi le SM_Morin_Auto_A/B/C (v1, troppo squadrate e solo blu/bianche/grigie). Le v1 restano in UEFN.
Riferimento: ref/foto/vista/parcheggio_iniziale.png (colori: bianco, grigio, nero, argento, rosso, qualche colore acceso).
Niente marchi, loghi o targhe leggibili: la targa e' un rettangolo bianco vuoto.

Geometria: scocca "loft" di sezioni trasversali (11 punti per mezza sezione al LOD0) lungo X, con profili laterali
smussati (tetto, linea di cintura, fondo con passaruota), ruote cilindriche, specchietti. Origine a terra al centro,
muso verso +X (come le v1: le posizioni dei CSV restano valide).

Colori: UNA sola texture (atlante 2048, T_Morin_Auto_v2_D/N/ORM, un materiale M_Morin_Auto_v2) divisa in 3x3 celle
(colonna = modello, riga = colore). Ogni cella contiene i pannelli dipinti di quel modello in quel colore
(fianco, pianta, fronte, retro, ruota, gomma, plastica). Le varianti di colore sono mesh distinte che differiscono
solo per lo spostamento delle UV di una cella: in UEFN nessun materiale in piu', nessun parametro, HISM come prima.

Esegui dentro blender/arte_parcheggio.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_auto_v2 as av; importlib.reload(av)
    av.make_textures(); av.build_material(); av.build_all()
    av.export_all()
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_texphoto as tp
import morin_molo as mm

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/auto"
TEX = "T_Morin_Auto_v2"
MAT = "M_Morin_Auto_v2"
KIT = "AUTO_v2_Kit"
EXPDIR = "//../exports/auto"

NPX = 2048
CELL = 682              # 3 x 682 = 2046 px
S = 116.0               # px per metro nei pannelli
XM, ZM, YM = 2.25, 1.70, 0.95       # semi-lunghezza, altezza e semi-larghezza massime dei pannelli
# pannelli nella cella (colonna0, riga0) in px; riga 0 = alto dell'immagine
P_SIDE = (4, 4)                     # 522 x 197  (x, z)
P_TOP = (4, 209)                    # 522 x 220  (x, y)
P_FRONT = (4, 437)                  # 220 x 197  (y, z)
P_BACK = (232, 437)                 # 220 x 197  (y, z)
P_RIM = (460, 440, 216)             # disco ruota (col0, riga0, diametro)
P_TREAD = (536, 10, 140, 120)       # battistrada (col0, riga0, w, h)
P_PLAST = (536, 140, 140, 100)      # plastica nera / sottoscocca
P_BODY = (536, 250, 140, 80)        # tinta unita (specchietti)
P_GLASS = (536, 340, 140, 80)       # vetro dello specchietto

# -------------------------------------------------------------------------------------------------------------
# modelli: profili laterali (t 0 = retro, 1 = muso) [S da proporzioni di auto europee tipiche, misure v1]
# -------------------------------------------------------------------------------------------------------------
MODELS = {
    "A": dict(  # utilitaria 5 porte
        L=3.95, W=1.74, r=0.30, tw=(0.157, 0.790),
        top=[(0, 1.00), (0.02, 1.16), (0.05, 1.36), (0.10, 1.47), (0.16, 1.50), (0.50, 1.50), (0.57, 1.46),
             (0.75, 0.98), (0.88, 0.92), (0.96, 0.84), (1.0, 0.70)],
        belt=[(0, 0.97), (0.10, 0.95), (0.70, 0.90), (0.80, 0.88), (0.96, 0.82), (1.0, 0.69)],
        bot=[(0, 0.38), (0.05, 0.28), (0.95, 0.26), (1.0, 0.36)],
        w=[(0, 0.90), (0.03, 0.96), (0.10, 1.0), (0.86, 1.0), (0.95, 0.96), (1.0, 0.86)],
        wr=[(0, 0.70), (0.5, 0.78), (0.75, 0.84), (1.0, 0.80)],
        ws=(0.57, 0.75), rwin_top=(0.02, 0.10), rwin=(1.03, 1.40, 0.82),
        doors=[0.255, 0.48, 0.745], pillars=[(0.47, 0.495, "nero"), (0.0, 0.255, "corpo")],
        lamp_f=(0.62, 0.75), lamp_r=(0.82, 0.96), cladding=False, rails=False, rim_spokes=5, rim_col=(168, 170, 174)),
    "B": dict(  # SUV compatto
        L=4.35, W=1.82, r=0.34, tw=(0.179, 0.786),
        top=[(0, 1.10), (0.02, 1.30), (0.05, 1.52), (0.10, 1.62), (0.16, 1.64), (0.55, 1.63), (0.62, 1.58),
             (0.77, 1.10), (0.88, 1.05), (0.96, 0.98), (1.0, 0.84)],
        belt=[(0, 1.07), (0.10, 1.05), (0.75, 1.01), (0.86, 0.99), (0.96, 0.95), (1.0, 0.83)],
        bot=[(0, 0.46), (0.05, 0.38), (0.95, 0.37), (1.0, 0.44)],
        w=[(0, 0.92), (0.03, 0.97), (0.10, 1.0), (0.86, 1.0), (0.95, 0.97), (1.0, 0.89)],
        wr=[(0, 0.74), (0.5, 0.80), (0.77, 0.86), (1.0, 0.84)],
        ws=(0.62, 0.77), rwin_top=(0.02, 0.10), rwin=(1.13, 1.52, 0.80),
        doors=[0.265, 0.495, 0.755], pillars=[(0.485, 0.51, "nero"), (0.20, 0.265, "nero"), (0.0, 0.07, "corpo")],
        lamp_f=(0.80, 0.92), lamp_r=(0.94, 1.06), cladding=True, rails=True, rim_spokes=10, rim_col=(120, 122, 126)),
    "C": dict(  # station wagon
        L=4.45, W=1.78, r=0.32, tw=(0.191, 0.787),
        top=[(0, 0.97), (0.02, 1.18), (0.05, 1.38), (0.09, 1.45), (0.15, 1.47), (0.52, 1.47), (0.60, 1.43),
             (0.76, 0.96), (0.88, 0.90), (0.96, 0.82), (1.0, 0.68)],
        belt=[(0, 0.94), (0.10, 0.93), (0.74, 0.89), (0.86, 0.86), (0.96, 0.80), (1.0, 0.67)],
        bot=[(0, 0.36), (0.05, 0.27), (0.95, 0.25), (1.0, 0.33)],
        w=[(0, 0.90), (0.03, 0.96), (0.10, 1.0), (0.86, 1.0), (0.95, 0.96), (1.0, 0.86)],
        wr=[(0, 0.72), (0.5, 0.78), (0.76, 0.84), (1.0, 0.80)],
        ws=(0.60, 0.76), rwin_top=(0.02, 0.09), rwin=(1.00, 1.38, 0.80),
        doors=[0.285, 0.50, 0.755], pillars=[(0.495, 0.52, "nero"), (0.255, 0.285, "nero"), (0.0, 0.065, "corpo")],
        lamp_f=(0.60, 0.72), lamp_r=(0.80, 0.94), cladding=False, rails=True, rim_spokes=6, rim_col=(70, 72, 76)),
}
MODEL_IDX = {"A": 0, "B": 1, "C": 2}
# tre colori per modello (riga della cella): nome, sRGB, metallic, roughness
COLORI = {
    "A": [("Bianco", (236, 237, 235), 0.0, 0.30), ("Rosso", (152, 20, 24), 0.25, 0.28), ("Azzurro", (38, 118, 186), 0.45, 0.28)],
    "B": [("GrigioScuro", (68, 71, 76), 0.6, 0.30), ("Argento", (172, 175, 178), 0.75, 0.30), ("Arancio", (206, 96, 28), 0.3, 0.28)],
    "C": [("Nero", (16, 17, 19), 0.45, 0.24), ("BluScuro", (24, 36, 72), 0.6, 0.28), ("BiancoPerla", (224, 222, 214), 0.2, 0.30)],
}
# frequenze nei CSV (foto: molti bianchi/grigi/neri, pochi colori accesi)
PESI = {"A": (0.5, 0.3, 0.2), "B": (0.45, 0.40, 0.15), "C": (0.45, 0.30, 0.25)}


def asset_name(m, colore, col=False):
    return f"SM_Morin_Auto_{m}{'_Col' if col else ''}_v2_{colore}"


# -------------------------------------------------------------------------------------------------------------
# profili smussati
# -------------------------------------------------------------------------------------------------------------
_TF = np.linspace(0.0, 1.0, 801)


def _smooth(keys, sigma=5.0):
    k = np.asarray(keys, np.float64)
    v = np.interp(_TF, k[:, 0], k[:, 1])
    r = int(3 * sigma)
    g = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    g /= g.sum()
    vp = np.pad(v, r, mode="edge")
    return np.convolve(vp, g, mode="valid")


class Prof:
    def __init__(self, m):
        p = MODELS[m]
        self.m, self.p = m, p
        self.L, self.W, self.r = p["L"], p["W"], p["r"]
        self.top = _smooth(p["top"], 4.0)
        self.belt = np.minimum(_smooth(p["belt"], 4.0), self.top - 0.03)
        self.bot = _smooth(p["bot"], 6.0)
        self.w = _smooth(p["w"], 6.0) * self.W / 2
        self.wr = _smooth(p["wr"], 6.0) * self.W / 2
        self.xw = [-self.L / 2 + t * self.L for t in p["tw"]]
        self.R = self.r + 0.07

    def x(self, t):
        return -self.L / 2 + np.asarray(t) * self.L

    def t(self, x):
        return (np.asarray(x) + self.L / 2) / self.L

    def f(self, arr, x):
        return np.interp(self.t(x), _TF, arr)

    def zb(self, x):
        """fondo della scocca con i passaruota."""
        x = np.asarray(x, np.float64)
        z = self.f(self.bot, x)
        for xw in self.xw:
            dx = np.abs(x - xw)
            arch = np.where(dx < self.R, self.r + np.sqrt(np.maximum(self.R ** 2 - dx ** 2, 0)), 0.0)
            z = np.maximum(z, arch)
        return z

    def section(self, x, lod):
        zb = float(self.zb(x))
        zt = float(self.f(self.top, x))
        belt = float(self.f(self.belt, x))
        w = float(self.f(self.w, x))
        wr = min(float(self.f(self.wr, x)), 0.93 * w)
        e = min(0.12, 0.3 * (belt - zb))
        zm = max(zb + e + 0.02, belt - 0.30)
        d = min(0.08, 0.45 * (zt - belt))
        P = [(0.0, zb), (0.82 * w, zb), (0.97 * w, zb + 0.35 * e), (w, zb + e), (w, zm), (0.985 * w, belt),
             (0.955 * w, belt + 0.025), (wr, zt - d), (0.93 * wr, zt - 0.35 * d), (0.60 * wr, zt - 0.04 * d), (0.0, zt)]
        keep = {0: range(11), 1: (0, 1, 3, 4, 5, 7, 9, 10), 2: (0, 3, 5, 7, 10)}[lod]
        return [P[i] for i in keep]

    def stations(self, lod):
        p = self.p
        base = {0: [0, .01, .03, .06, .10, .15, .22, .30, .38, .46, .54, .60, .66, .72, .80, .86, .91, .95, .975, .99, 1.0],
                1: [0, .02, .07, .15, .30, .46, .60, .72, .86, .95, .99, 1.0],
                2: [0, .5, 1.0]}[lod]
        keys = [k[0] for k in p["top"]] if lod < 2 else [p["ws"][0], p["ws"][1], p["rwin_top"][1], 0.96]
        ts = sorted(set([round(v, 4) for v in base + keys]))
        xs = [self.x(t) for t in ts]
        na = {0: 9, 1: 5, 2: 3}[lod]
        arch = []
        for xw in self.xw:
            xs = [x for x in xs if abs(x - xw) > self.R + 0.03]
            arch += [xw - self.R * math.cos(a) for a in np.linspace(0, math.pi, na)]
        xs = sorted(xs + arch)
        out = [xs[0]]
        for x in xs[1:]:
            if x - out[-1] > 0.015:
                out.append(x)
        return out

    def greenhouse(self):
        """intervallo x del tetto (top - belt > 0,25)."""
        g = self.top - self.belt
        idx = np.where(g > 0.25)[0]
        return float(self.x(_TF[idx[0]])), float(self.x(_TF[idx[-1]]))


# -------------------------------------------------------------------------------------------------------------
# texture
# -------------------------------------------------------------------------------------------------------------
def _c(c):
    return np.asarray(c, np.float32) / 255.0


def _cell_origin(m, ci):
    return MODEL_IDX[m] * CELL, ci * CELL


GLASS = (20, 24, 30)
TRIM = (14, 14, 16)
PLAST = (30, 31, 33)
LENS_F = (150, 158, 168)
LENS_R = (150, 16, 20)
PLATE = (238, 238, 236)


class Canvas:
    def __init__(self, n=NPX):
        self.A = np.zeros((n, n, 3), np.float32)
        self.R = np.full((n, n), 0.5, np.float32)
        self.M = np.zeros((n, n), np.float32)
        self.H = np.full((n, n), 0.5, np.float32)

    def put(self, r0, c0, A, R, M, H):
        h, w = R.shape
        self.A[r0:r0 + h, c0:c0 + w] = A
        self.R[r0:r0 + h, c0:c0 + w] = R
        self.M[r0:r0 + h, c0:c0 + w] = M
        self.H[r0:r0 + h, c0:c0 + w] = H


def _layers(shape, col, metal, rough):
    A = np.empty(shape + (3,), np.float32)
    A[:] = _c(col)
    return A, np.full(shape, rough, np.float32), np.full(shape, metal, np.float32), np.full(shape, 0.5, np.float32)


def _paint(L, mask, col, rough, metal, h=None):
    A, R, M, H = L
    A[mask] = _c(col)
    R[mask] = rough
    M[mask] = metal
    if h is not None:
        H[mask] = h


def _line(coord, pos, half):
    return np.abs(coord - pos) < half


def _paint_side(pr, col, metal, rough):
    w, h = int(2 * XM * S), int(ZM * S)
    cc, rr = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    x = cc / S - XM
    z = ZM - rr / S
    L = _layers((h, w), col, metal, rough)
    A = L[0]
    A *= (0.86 + 0.16 * np.clip((z - 0.3) / 1.0, 0, 1))[..., None]            # luce dall'alto
    p = pr.p
    t = pr.t(x)
    belt = pr.f(pr.belt, x)
    zt = pr.f(pr.top, x)
    zb = pr.zb(x)
    # vetri laterali: tra cintura e tetto, erosi per montanti A e posteriori
    ztop_g = np.minimum(pr.f(pr.top, x - 0.10), pr.f(pr.top, x + 0.10)) - 0.075
    glass = (z > belt + 0.035) & (z < ztop_g)
    frame = (z > belt + 0.015) & (z < ztop_g + 0.022) & ~glass
    frame &= (z > belt + 0.015) & (zt - belt > 0.12)
    for (t0, t1, kind) in p["pillars"]:
        band = (t >= t0) & (t < t1)
        if kind == "corpo":
            glass &= ~band
            frame &= ~band
    _paint(L, frame, TRIM, 0.2, 0.0, 0.45)
    shade = np.clip((z - belt) / np.maximum(zt - belt, 0.1), 0, 1)
    _paint(L, glass, GLASS, 0.04, 0.2, 0.47)
    A[glass] += (_c((60, 70, 82)) * (1 - shade[glass])[..., None] * 0.6)        # riflesso del cielo in basso
    for (t0, t1, kind) in p["pillars"]:
        band = (t >= t0) & (t < t1) & (z > belt + 0.02) & (z < zt - 0.02)
        if kind == "nero":
            _paint(L, band, TRIM, 0.08, 0.1, 0.47)
    # fiancata: commenti di porta, maniglie
    for td in p["doors"]:
        xd = pr.x(td)
        seam = _line(x, xd, 0.006) & (z > zb + 0.06) & (z < belt + 0.01)
        _paint(L, seam, (20, 20, 22), 0.6, 0.0, 0.2)
    d = p["doors"]
    for xr in (pr.x(d[0]) + 0.07, pr.x(d[1]) + 0.07):
        hz = belt - 0.085
        hnd = (x > xr) & (x < xr + 0.19) & (np.abs(z - hz) < 0.018)
        A[hnd] *= 0.82
        L[3][hnd] = 0.62
        under = (x > xr + 0.02) & (x < xr + 0.17) & (np.abs(z - (hz - 0.024)) < 0.006)
        _paint(L, under, (25, 25, 27), 0.7, 0.0, 0.35)
    # linea di cintura (leggera piega) e sottoporta piu' scuro
    crease = _line(z, belt - 0.16, 0.012) & (t > 0.06) & (t < 0.94)
    A[crease] *= 0.93
    L[3][crease] = 0.55
    sill = z < zb + 0.07
    A[sill] *= 0.6
    if p["cladding"]:
        clad = z < pr.f(pr.bot, x) + 0.17
        for xw in pr.xw:
            dd = np.hypot(x - xw, z - pr.r)
            clad |= (dd < pr.R + 0.09)
        _paint(L, clad, PLAST, 0.75, 0.0, 0.52)
    # gruppi ottici che girano sul fianco
    lr = (t < 0.03) & (z > p["lamp_r"][0]) & (z < p["lamp_r"][1])
    _paint(L, lr, LENS_R, 0.1, 0.0, 0.53)
    lf = (t > 0.978) & (z > p["lamp_f"][0] + 0.02) & (z < p["lamp_f"][1] - 0.01)
    _paint(L, lf, LENS_F, 0.08, 0.3, 0.53)
    # paraurti: separazione in basso
    for tt in (0.035, 0.965):
        bs = _line(t, tt, 0.0015) & (z < belt - 0.05)
        _paint(L, bs, (22, 22, 24), 0.6, 0.0, 0.25)
    return L


def _paint_top(pr, col, metal, rough):
    w, h = int(2 * XM * S), int(2 * YM * S)
    cc, rr = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    x = cc / S - XM
    y = YM - rr / S
    L = _layers((h, w), col, metal, rough)
    A = L[0]
    A *= 1.04
    p = pr.p
    t = pr.t(x)
    wr = pr.f(pr.wr, x)
    ay = np.abs(y)
    xs0, xs1 = pr.x(p["ws"][0]), pr.x(p["ws"][1])
    ws = (x > xs0 + 0.04) & (x < xs1 - 0.03) & (ay < wr * 0.86)
    xr0, xr1 = pr.x(p["rwin_top"][0]), pr.x(p["rwin_top"][1])
    rw = (x > xr0 + 0.02) & (x < xr1 - 0.02) & (ay < wr * 0.80)
    fr = ((x > xs0) & (x < xs1 + 0.01) & (ay < wr * 0.92)) | ((x > xr0) & (x < xr1) & (ay < wr * 0.87))
    _paint(L, fr & ~ws & ~rw, TRIM, 0.2, 0.0, 0.47)
    _paint(L, ws | rw, GLASS, 0.04, 0.2, 0.47)
    A[ws] += _c((70, 80, 92)) * 0.5
    # cofano: linee di chiusura
    hood = _line(x, xs1 + 0.05, 0.005) & (ay < pr.f(pr.w, x) * 0.80)
    hood |= (x > xs1 + 0.05) & _line(ay, pr.f(pr.w, x) * 0.80, 0.005)
    _paint(L, hood, (22, 22, 24), 0.6, 0.0, 0.25)
    # portellone
    tg = _line(x, xr0 - 0.01, 0.005) & (ay < wr * 0.85)
    _paint(L, tg, (22, 22, 24), 0.6, 0.0, 0.25)
    if p["rails"]:
        gh0, gh1 = pr.greenhouse()
        rails = (x > gh0 + 0.12) & (x < gh1 - 0.10) & _line(ay, wr * 0.86, 0.02)
        _paint(L, rails, (40, 41, 44), 0.35, 0.4, 0.6)
    # angoli dei fari/fanali visti dall'alto
    lf = (t > 0.978) & (ay > 0.52 * pr.W / 2) & (ay < 0.93 * pr.W / 2)
    _paint(L, lf, LENS_F, 0.08, 0.3, 0.53)
    lr = (t < 0.018) & (ay > 0.60 * pr.W / 2)
    _paint(L, lr, LENS_R, 0.1, 0.0, 0.53)
    return L


def _paint_end(pr, col, metal, rough, front):
    w, h = int(2 * YM * S), int(ZM * S)
    cc, rr = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    y = cc / S - YM
    z = ZM - rr / S
    L = _layers((h, w), col, metal, rough)
    A = L[0]
    A *= (0.86 + 0.14 * np.clip((z - 0.3) / 1.0, 0, 1))[..., None]
    p = pr.p
    ay = np.abs(y)
    hw = pr.W / 2
    xe = pr.L / 2 if front else -pr.L / 2
    zb = float(pr.f(pr.bot, xe))
    if front:
        z0, z1 = p["lamp_f"]
        lamp = (ay > 0.50 * hw) & (ay < 0.93 * hw) & (z > z0) & (z < z1) & (z - z0 > (ay - 0.50 * hw) * 0.12)
        _paint(L, lamp, LENS_F, 0.06, 0.3, 0.55)
        drl = lamp & (np.abs(z - (z0 + 0.025)) < 0.008)
        A[drl] = _c((250, 250, 248))
        grille = (ay < 0.40 * hw) & (z > z0 - 0.10) & (z < z0 + 0.06)
        _paint(L, grille, (24, 25, 27), 0.5, 0.0, 0.42)
        slats = grille & (np.mod((z - z0) * 100, 3.0) < 1.0)
        A[slats] *= 1.8
        L[3][slats] = 0.46
        low = (ay < 0.62 * hw) & (z > zb + 0.04) & (z < zb + 0.17)
        _paint(L, low, (22, 23, 25), 0.55, 0.0, 0.42)
        pz = zb + 0.21
    else:
        z0, z1 = p["lamp_r"]
        lamp = (ay > 0.58 * hw) & (ay < 0.95 * hw) & (z > z0) & (z < z1)
        _paint(L, lamp, LENS_R, 0.08, 0.0, 0.55)
        inner = lamp & (np.abs(z - (z0 + z1) / 2) < 0.012)
        A[inner] = _c((210, 40, 40))
        g0, g1, gf = p["rwin"]
        rwin = (z > g0) & (z < g1) & (ay < gf * hw * (1 - 0.15 * (z - g0) / (g1 - g0)))
        frame = (z > g0 - 0.03) & (z < g1 + 0.03) & (ay < gf * hw * 1.06) & ~rwin
        _paint(L, frame, TRIM, 0.2, 0.0, 0.47)
        _paint(L, rwin, GLASS, 0.04, 0.2, 0.47)
        A[rwin] += _c((60, 70, 82)) * 0.4
        tg = (_line(z, z0 - 0.17, 0.005) & (ay < 0.56 * hw)) | (_line(ay, 0.56 * hw, 0.005) & (z > z0 - 0.17) & (z < g0 - 0.03))
        _paint(L, tg, (22, 22, 24), 0.6, 0.0, 0.25)
        low = (z > zb) & (z < zb + 0.10)
        _paint(L, low, (24, 25, 27), 0.6, 0.0, 0.45)
        pz = z0 - 0.10
    if p["cladding"]:
        _paint(L, (z > zb) & (z < zb + 0.14), PLAST, 0.75, 0.0, 0.5)
    # targa bianca vuota (nessun testo) con vano
    vano = (ay < 0.29) & (np.abs(z - pz) < 0.075)
    _paint(L, vano, (40, 40, 42), 0.6, 0.0, 0.42)
    plate = (ay < 0.26) & (np.abs(z - pz) < 0.055)
    _paint(L, plate, PLATE, 0.45, 0.0, 0.5)
    return L


def _paint_rim(pr, d):
    cc, rr = np.meshgrid(np.arange(d) + 0.5, np.arange(d) + 0.5)
    u = (cc - d / 2) / (d / 2)
    v = (rr - d / 2) / (d / 2)
    rho = np.hypot(u, v)
    ang = np.arctan2(v, u)
    L = _layers((d, d), (26, 26, 28), 0.0, 0.85)
    A, R, M, H = L
    tyre_in = 0.68
    side = (rho > tyre_in) & (rho < 1.0)
    A[side] *= (0.85 + 0.3 * np.clip((rho[side] - tyre_in) / 0.3, 0, 1))[..., None]
    H[side] = 0.5 + 0.2 * np.sin(np.clip((rho[side] - tyre_in) / 0.32, 0, 1) * math.pi)
    rim = rho <= tyre_in
    _paint(L, rim, (40, 40, 42), 0.5, 0.2, 0.3)                       # fondo del cerchio (in ombra)
    n = pr.p["rim_spokes"]
    rc = pr.p["rim_col"]
    spokes = rim & (rho > 0.16) & (np.cos(ang * n) > (0.55 if n >= 10 else 0.35))
    lip = (rho > tyre_in - 0.06) & (rho <= tyre_in)
    hub = rho < 0.18
    _paint(L, spokes | lip | hub, rc, 0.3, 0.85, 0.65)
    nuts = (np.abs(rho - 0.11) < 0.025) & (np.cos(ang * 5) > 0.92)
    _paint(L, nuts, (80, 80, 84), 0.3, 0.9, 0.7)
    return L


def _paint_tread(w, h):
    cc, rr = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    L = _layers((h, w), (28, 28, 30), 0.0, 0.9)
    groove = (np.abs(rr / h - 0.35) < 0.03) | (np.abs(rr / h - 0.65) < 0.03) | (np.mod(cc + rr * 0.5, 9) < 1.5)
    A, R, M, H = L
    A[groove] *= 0.6
    H[groove] = 0.3
    return L


def make_textures():
    C = Canvas()
    C.A[:] = _c(PLAST)
    for m in MODELS:
        pr = Prof(m)
        for ci, (cn, col, metal, rough) in enumerate(COLORI[m]):
            c0, r0 = _cell_origin(m, ci)
            for (pc, pr0), L in ((P_SIDE, _paint_side(pr, col, metal, rough)), (P_TOP, _paint_top(pr, col, metal, rough)),
                                 (P_FRONT, _paint_end(pr, col, metal, rough, True)),
                                 (P_BACK, _paint_end(pr, col, metal, rough, False))):
                C.put(r0 + pr0, c0 + pc, *L)
            C.put(r0 + P_RIM[1], c0 + P_RIM[0], *_paint_rim(pr, P_RIM[2]))
            C.put(r0 + P_TREAD[1], c0 + P_TREAD[0], *_paint_tread(P_TREAD[2], P_TREAD[3]))
            C.put(r0 + P_PLAST[1], c0 + P_PLAST[0], *_layers((P_PLAST[3], P_PLAST[2]), PLAST, 0.0, 0.8))
            C.put(r0 + P_BODY[1], c0 + P_BODY[0], *_layers((P_BODY[3], P_BODY[2]), col, metal, rough))
            C.put(r0 + P_GLASS[1], c0 + P_GLASS[0], *_layers((P_GLASS[3], P_GLASS[2]), (90, 96, 104), 0.9, 0.05))
    noise = mm._noise(NPX, NPX, 2, 4401)
    A = np.clip(C.A * (1 + 0.012 * noise[..., None]), 0, 1)
    R = np.clip(C.R + 0.03 * mm._noise(NPX, NPX, 20, 4402), 0.02, 1)
    nrm, ao = mm._normal_ao(C.H, 3.0, 2.0, 2.0)
    os.makedirs(TEXDIR, exist_ok=True)
    tp.save(A, f"{TEXDIR}/{TEX}_D.png")
    tp.save(nrm, f"{TEXDIR}/{TEX}_N.png")
    tp.save(mm._orm(ao, R, C.M), f"{TEXDIR}/{TEX}_ORM.png")
    return [f"{TEX}_D", f"{TEX}_N", f"{TEX}_ORM"]


def build_material():
    t = TEXDIR + "/" + TEX
    return pk._pbr_material(MAT, t + "_D.png", t + "_N.png", t + "_ORM.png")


# -------------------------------------------------------------------------------------------------------------
# UV (coordinate nella cella 0,0; le varianti spostano di una cella)
# -------------------------------------------------------------------------------------------------------------
def _uv(col, row):
    return (col / NPX, 1.0 - row / NPX)


def uv_side(x, z):
    return _uv(P_SIDE[0] + (x + XM) * S, P_SIDE[1] + (ZM - z) * S)


def uv_top(x, y):
    return _uv(P_TOP[0] + (x + XM) * S, P_TOP[1] + (YM - y) * S)


def uv_end(y, z, front):
    p = P_FRONT if front else P_BACK
    return _uv(p[0] + (y + YM) * S, p[1] + (ZM - z) * S)


def uv_rect(rect, fu, fv):
    c0, r0, w, h = rect
    return _uv(c0 + 6 + (w - 12) * fu, r0 + 6 + (h - 12) * fv)


# -------------------------------------------------------------------------------------------------------------
# mesh
# -------------------------------------------------------------------------------------------------------------
def _assign_body_uv(bm, layer, faces):
    for f in faces:
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for lp in f.loops:
            c = lp.vert.co
            if az >= ax and az >= ay:
                uv = uv_top(c.x, c.y) if n.z > 0 else uv_rect(P_PLAST, 0.5, 0.5)
            elif ay >= ax:
                uv = uv_side(c.x, c.z)
            else:
                uv = uv_end(c.y if n.x > 0 else -c.y, c.z, n.x > 0)
            lp[layer].uv = uv


def build_mesh(m, lod):
    pr = Prof(m)
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    xs = pr.stations(lod)
    rings = []
    for x in xs:
        half = pr.section(x, lod)
        pts = half + [(-y, z) for (y, z) in reversed(half[1:-1])]
        rings.append([bm.verts.new((x, y, z)) for (y, z) in pts])
    n = len(rings[0])
    body = []
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        for k in range(n):
            k2 = (k + 1) % n
            body.append(bm.faces.new((A[k], B[k], B[k2], A[k2])))
    body.append(bm.faces.new(rings[0]))
    body.append(bm.faces.new(list(reversed(rings[-1]))))
    bmesh.ops.recalc_face_normals(bm, faces=body)
    for f in body:
        f.normal_update()
    _assign_body_uv(bm, layer, body)
    # ruote
    sides = (20, 12, 8)[lod]
    r = pr.r
    tw = 0.205
    for xw in pr.xw:
        wout = float(pr.f(pr.w, xw)) - 0.025
        for sy in (-1, 1):
            yo, yi = sy * wout, sy * (wout - tw)
            ro, ri = [], []
            for j in range(sides):
                a = 2 * math.pi * j / sides
                cx, cz = xw + r * math.cos(a), r + r * math.sin(a)
                ro.append(bm.verts.new((cx, yo, cz)))
                ri.append(bm.verts.new((cx, yi, cz)))
            for j in range(sides):
                j2 = (j + 1) % sides
                q = (ro[j], ro[j2], ri[j2], ri[j]) if sy < 0 else (ri[j], ri[j2], ro[j2], ro[j])
                f = bm.faces.new(q)
                f.normal_update()
                cm = f.calc_center_median()
                if f.normal.x * (cm.x - xw) + f.normal.z * (cm.z - r) < 0:
                    f.normal_flip()
                for lp in f.loops:
                    jj = j if lp.vert in (ro[j], ri[j]) else j + 1
                    fu = (jj / sides) % 1.0001
                    fv = 0.0 if lp.vert in ro else 1.0
                    lp[layer].uv = uv_rect(P_TREAD, fu, fv)
            caps = [(ro, True)] + ([(ri, False)] if lod < 2 else [])
            for ring, outer in caps:
                f = bm.faces.new(ring)
                f.normal_update()
                if f.normal.y * (sy if outer else -sy) < 0:
                    f.normal_flip()
                for lp in f.loops:
                    c = lp.vert.co
                    if outer:
                        du = (c.x - xw) / r * (1 if sy > 0 else -1)
                        dv = -(c.z - r) / r
                        lp[layer].uv = _uv(P_RIM[0] + P_RIM[2] / 2 * (1 + 0.98 * du), P_RIM[1] + P_RIM[2] / 2 * (1 + 0.98 * dv))
                    else:
                        lp[layer].uv = uv_rect(P_PLAST, 0.5, 0.5)
    # specchietti (non al LOD2)
    if lod < 2:
        xm = pr.x(pr.p["ws"][1]) - 0.10
        belt = float(pr.f(pr.belt, xm))
        w = float(pr.f(pr.w, xm))
        for sy in (-1, 1):
            y0, y1 = sorted((sy * (w - 0.02), sy * (w + 0.19)))
            z0, z1 = belt + 0.04, belt + 0.16
            x0, x1 = xm - 0.07, xm + 0.05
            vs = [bm.verts.new(v) for v in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
            quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7)]
            for qi, q in enumerate(quads):
                f = bm.faces.new([vs[i] for i in q])
                f.normal_update()
                if f.normal.dot(f.calc_center_median() - Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))) < 0:
                    f.normal_flip()
                rect = P_GLASS if qi == 5 else P_BODY
                for lp, (fu, fv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
                    lp[layer].uv = uv_rect(rect, fu, fv)
    return bm


def _shift_uv(me, ci):
    dv = ci * CELL / NPX
    lay = me.uv_layers.active.data
    arr = np.empty(len(lay) * 2, np.float32)
    lay.foreach_get("uv", arr)
    arr[1::2] -= dv
    lay.foreach_set("uv", arr)


def build_all():
    coll = pk._coll(KIT)
    out = []
    for m in MODELS:
        mi = MODEL_IDX[m]
        for lod in (0, 1, 2):
            for ci, (cn, *_r) in enumerate(COLORI[m]):
                bm = build_mesh(m, lod)
                layer = bm.loops.layers.uv.active
                du = mi * CELL / NPX
                for f in bm.faces:
                    for lp in f.loops:
                        u, v = lp[layer].uv
                        lp[layer].uv = (u + du, v)
                sfx = "" if lod == 0 else f"_LOD{lod}"
                nm = asset_name(m, cn) + sfx
                o = pk._finish(nm, bm, [MAT], coll, uv=None, smooth_angle=50)
                _shift_uv(o.data, ci)
                out.append(o)
                # versione con collisione: stessa mesh, oggetto distinto
                nc = asset_name(m, cn, True) + sfx
                oc = bpy.data.objects.get(nc)
                if oc is None:
                    oc = bpy.data.objects.new(nc, o.data)
                    coll.objects.link(oc)
                oc.data = o.data
                oc.matrix_world = Matrix.Identity(4)
                out.append(oc)
                if lod == 0:
                    _ucx_col(pr=Prof(m), name=asset_name(m, cn, True), coll=coll)
    return out


def _ucx_col(pr, name, coll):
    """2 box: scocca fino alla cintura + abitacolo (come le v1)."""
    for u in [x for x in bpy.data.objects if x.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)    # solo collisioni rigenerate da questo script
    belt = float(np.max(pr.belt[(_TF > 0.2) & (_TF < 0.8)]))
    gh0, gh1 = pr.greenhouse()
    H = float(pr.top.max())
    W = pr.W / 2
    pk._ucx(name, [(-pr.L / 2, pr.L / 2, -W, W, 0.12, belt),
                   (gh0, gh1, -float(pr.wr.max()) - 0.04, float(pr.wr.max()) + 0.04, belt, H - 0.03)], coll)


def report():
    rows = []
    for m in MODELS:
        cn = COLORI[m][0][0]
        tris = [pk.tri_count(bpy.data.objects[asset_name(m, cn) + ("" if l == 0 else f"_LOD{l}")]) for l in (0, 1, 2)]
        o = bpy.data.objects[asset_name(m, cn)]
        dims = tuple(round(v, 2) for v in o.dimensions)
        rows.append((m, tris, dims))
    return rows


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    objs = list(bpy.data.collections[KIT].objects)
    state = {o.name: (o.hide_viewport, o.hide_get()) for o in objs}
    for o in objs:
        o.hide_viewport = False
        o.hide_set(False)
    bpy.context.view_layer.update()
    reps = []
    try:
        for m in MODELS:
            for (cn, *_r) in COLORI[m]:
                for col in (False, True):
                    base = asset_name(m, cn, col)
                    for lod in (0, 1, 2):
                        on = base if lod == 0 else f"{base}_LOD{lod}"
                        reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                                            overwrite=overwrite, include_ucx=(lod == 0 and col),
                                                            bake_rotation=(lod > 0), verbose=False))
    finally:
        for n, (hv, hg) in state.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps


# =============================================================================================================
# CSV: parcheggio v2 (auto v2, pini domestici, new jersey spostato) e viale v3 (auto v2)
# =============================================================================================================
def _pick_colore(m, rng):
    i = int(rng.choice(3, p=PESI[m]))
    return COLORI[m][i][0]


def _v2_of(asset, rng):
    """SM_Morin_Auto_X[_Col] -> variante v2 con colore estratto (pesi PESI)."""
    m = asset.split("_")[3]
    return asset_name(m, _pick_colore(m, rng), asset.endswith("_Col"))


# pini: filare nell'aiuola rialzata (X 26-84, Y 113,4-116,8; OSM filare a Y 113, X 18-85). Varco a X ~55,5 per il
# cartello P_01. Tronco inclinato verso la corsia del parcheggio (-Y, foto): yaw e inclinazione variabili.
PINI_X = (27.8, 37.2, 46.4, 58.4, 67.2, 75.8, 83.0)
PINO_LEAN_LOCAL = -22.6     # direzione (gradi, piano XY Blender) dell'inclinazione propria della mesh (morin_molo.build_pino)


def pini_rows(seed=20261120):
    rng = np.random.default_rng(seed)
    out = []
    for i, x in enumerate(PINI_X):
        phi = -90.0 + rng.uniform(-30, 30)                 # direzione dell'inclinazione (Blender): verso la corsia
        yaw_b = phi - PINO_LEAN_LOCAL * 0.5
        tilt = rng.uniform(3.0, 8.0)                       # inclinazione aggiunta (gradi) oltre ai ~7 della mesh
        out.append(("SM_Morin_PinoDomestico", f"Parcheggio_Pino_{i:02d}", float(x + rng.uniform(-0.6, 0.6)),
                    float(115.2 + rng.uniform(-0.35, 0.35)), 0.12, yaw_b, tilt))
    return out


def _ue(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0.0" if s in ("0", "-0", "") else (s if "." in s else s + ".0")


NJ00_DX = -1.3      # m: NewJersey_00 (lungo 2,0 m) via dalla bitta 3 (UE 6200; -8052,7)


def parcheggio_csv_v2(src="exports/parcheggio/parcheggio_posizioni_v1.csv",
                      dst="exports/parcheggio/parcheggio_posizioni_v2.csv", seed=20261121):
    import csv
    with open(f"{PROJ}/{src}", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    rng = np.random.default_rng(seed)
    out = ["asset,nome,x,y,z,yaw,pitch,roll"]
    ctx = []
    for r in rows[1:]:
        a, n, x, y, z, yaw = r[:6]
        if a.startswith("SM_Albero_Latifoglia"):
            continue
        if a.startswith("SM_Morin_Auto_"):
            a = _v2_of(a, rng)
        if n == "NewJersey_00":
            x = _ue(float(x) + NJ00_DX * 100)
        out.append(",".join([a, n, x, y, z, yaw, "0.0", "0.0"]))
        ctx.append((a, n, float(x) / 100, -float(y) / 100, float(z) / 100, -float(yaw), 0.0))
    for a, n, x, y, z, yaw_b, tilt in pini_rows():
        out.append(",".join([a, n, _ue(x * 100), _ue(-y * 100), _ue(z * 100), _ue(-yaw_b), _ue(-tilt), "0.0"]))
        ctx.append((a, n, x, y, z, yaw_b, tilt))
    with open(f"{PROJ}/{dst}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    return ctx


def viale_csv_v3(src="exports/viale/viale_posizioni_v2.csv", dst="exports/viale/viale_posizioni_v3.csv", seed=20261122):
    import csv
    with open(f"{PROJ}/{src}", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    rng = np.random.default_rng(seed)
    out = [",".join(rows[0])]
    ctx = []
    for r in rows[1:]:
        if r[0].startswith("SM_Morin_Auto_"):
            r = [_v2_of(r[0], rng)] + r[1:]
            ctx.append((r[0], r[1]))
        out.append(",".join(r))
    with open(f"{PROJ}/{dst}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    return ctx


def context_v2(park_ctx, viale_ctx):
    """Aggiorna le istanze di render: auto -> mesh v2, latifoglie del parcheggio nascoste (non cancellate), pini nuovi."""
    coll = pk._coll("PARK_Contesto_Istanze")
    for a, n, x, y, z, yaw_b, tilt in park_ctx:
        nm = "CTXP_" + n
        src = bpy.data.objects.get(a)
        me = src.data if src is not None else bpy.data.meshes.get(a)
        o = bpy.data.objects.get(nm)
        if o is None:
            o = bpy.data.objects.new(nm, me)
            coll.objects.link(o)
        o.data = me
        o.hide_render = False
        o.hide_viewport = False
        o.matrix_world = (Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw_b), 4, "Z")
                          @ Matrix.Rotation(math.radians(tilt), 4, "Y"))
    for o in bpy.data.objects:
        if o.name.startswith("CTXP_Parcheggio_Latifoglia_"):
            o.hide_render = True
            o.hide_viewport = True
    for a, n in viale_ctx:
        o = bpy.data.objects.get("CTXV_" + n)
        if o is not None:
            o.data = bpy.data.objects[a].data
    return True
