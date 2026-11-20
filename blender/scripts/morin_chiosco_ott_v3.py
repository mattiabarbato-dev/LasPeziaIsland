"""morin_chiosco_ott_v3.py — chiosco-bar ottagonale del Blocco 2, v3 completo (2026-11-20).

Difetto della v2 (e della v1): il corpo era un guscio APERTO di quad singoli e pk._recalc (recalc_face_normals) su un
guscio aperto ha orientato verso l'INTERNO tutte le pareti del corpo (8 inferiori, 3 superiori, 5 fondi scuri): in UEFN,
con il backface culling, da fuori si vedevano solo le facce interne delle pareti opposte (i 3 lati chiusi verso il viale),
cioe' "1/3 della parete". I 5 lati verso il mare erano inoltre vani aperti senza vetro.

v3: ogni pezzo e' un solido chiuso (pareti con spessore, bancone, vetrine, porta, interni, tettoia chiusa, insegna) con
l'avvolgimento delle facce scelto per costruzione (normale verso l'esterno del pezzo), SENZA recalc globale; facce
nascoste a contatto omesse (niente facce coincidenti). Verifica: qa() con ray test dall'esterno su ogni lato.

Assi come la v1/v2 (si posa con rotZ 0): lati centrati a k*45 gradi; k = 5, 6, 7 verso il mare (-Y): bancone vetrato;
k = 2 verso il viale (+Y): porta di servizio; k = 0 e 4: pannelli con locandine; k = 1, 3: pannelli. Insegna sul colmo
rivolta a SO-mare (225 gradi) e, sul retro, a NE.
Nome inventato e scherzoso: "Il Gabbiano Ingordo" (regola dell'utente: niente nomi commerciali reali).

Esegui dentro blender/arte_blocco2.blend (sys.path con blender/scripts):
    import morin_chiosco_ott_v3 as c3; importlib.reload(c3)
    c3.make_textures(); c3.build_materials(); c3.build_all(); c3.qa(); c3.export_all()
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

import morin_pav_kit as pk
import morin_texphoto as tp

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/blocco2"
EXPDIR = "//../exports/blocco2"
KIT = "B2_Kit"
NAME = "SM_Morin_ChioscoOttagonale_v3"
NOME = "IL GABBIANO INGORDO"
SOTTO = "BAR  ·  GELATI  ·  FOCACCIA"
MAT_A, MAT_V = "M_Morin_ChioscoOtt_v3", "M_Morin_ChioscoOtt_v3_Vetro"
S = 2048

# --- misure (pianta OSM way 352041625, O 6,6 m; quote come la v2 e il chiosco del Blocco 1) ---
R0 = 2.95                         # corpo, raggio circoscritto (esterno parete)
T8 = math.tan(math.pi / 8)
A_OUT = R0 * math.cos(math.pi / 8)   # apotema esterno 2,725
WALL = 0.08
A_IN = A_OUT - WALL
L_SIDE = 2 * A_OUT * T8           # 2,258 m
Z0 = 0.12                         # zoccolo / pavimento interno
Z_BANCO, Z_BANCO1 = 1.00, 1.06    # piano del bancone
Z_V1 = 2.30                       # architrave vetrine
Z_C = 2.62                        # intradosso / soffitto
Z_PORTA = 2.12
RE = R0 + 0.90                    # gronda (raggio circoscritto)
Z_M0, Z_E, Z_T = 2.42, 2.72, 3.12  # fondo mantovana, gronda, colmo
TOPR = RE - 1.25
BANCO_OUT, BANCO_IN = 0.30, 0.25
FRONT, DOOR, POSTER = (5, 6, 7), 2, (0, 4)
SIGN_YAW = 225.0
SIGN_W, SIGN_Z0, SIGN_Z1, SIGN_T = 3.0, 3.22, 3.84, 0.14

# --- atlante 2048 (u0, v0, u1, v1) ---
REG = {
    "fac_banco": (0.00, 0.5, 0.25, 1.0), "fac_pann": (0.25, 0.5, 0.50, 1.0),
    "fac_poster": (0.50, 0.5, 0.75, 1.0), "fac_porta": (0.75, 0.5, 1.00, 1.0),
    "insegna": (0.00, 0.375, 0.50, 0.5), "mant_nome": (0.00, 0.3125, 0.50, 0.375), "mant": (0.00, 0.25, 0.50, 0.3125),
    "tetto": (0.50, 0.25, 0.75, 0.5), "bianco": (0.75, 0.375, 0.875, 0.5), "intradosso": (0.875, 0.375, 1.0, 0.5),
    "legno_banco": (0.75, 0.25, 1.0, 0.375),
    "scaffale": (0.00, 0.0, 0.25, 0.25), "frigo": (0.25, 0.0, 0.375, 0.25), "pavimento": (0.375, 0.125, 0.5, 0.25),
    "acciaio": (0.375, 0.0, 0.5, 0.125), "macchina": (0.5, 0.125, 0.625, 0.25), "scuro": (0.5, 0.0, 0.625, 0.125),
    "interno": (0.625, 0.0, 0.75, 0.125), "zoccolo": (0.625, 0.125, 0.75, 0.25), "cassetti": (0.75, 0.0, 1.0, 0.25),
}

# colori sRGB: legno, crema, bianco da ref/foto/vista/chiosco_2_fine_passegiata_morin.png [SV] (solo campioni di colore)
LEGNO = (150, 96, 58)
CREMA = (226, 214, 190)
BIANCO = (238, 238, 234)


# =============================================================================================================
# texture
# =============================================================================================================
def _c(c):
    return np.asarray(c, np.float32) / 255.0


def _noise(h, w, sigma, seed):
    r = np.random.default_rng(seed).standard_normal((h, w)).astype(np.float32)
    r = tp.blur(r, sigma)
    return r / (r.std() + 1e-6)


def _px(r):
    u0, v0, u1, v1 = r
    return int(round((1 - v1) * S)), int(round((1 - v0) * S)), int(round(u0 * S)), int(round(u1 * S))


class Atlas:
    def __init__(self, reg=None):
        self.reg = reg or REG
        self.D = np.zeros((S, S, 3), np.float32)
        self.H = np.zeros((S, S), np.float32)
        self.R = np.full((S, S), 0.6, np.float32)
        self.M = np.zeros((S, S), np.float32)

    def region(self, key, w_m, h_m):
        """Viste sulla regione + griglie in metri (U da sinistra, Z dal basso)."""
        y0, y1, x0, x1 = _px(self.reg[key])
        hh, ww = y1 - y0, x1 - x0
        U, Z = np.meshgrid((np.arange(ww) + 0.5) / ww * w_m, (hh - np.arange(hh) - 0.5) / hh * h_m)
        return (self.D[y0:y1, x0:x1], self.H[y0:y1, x0:x1], self.R[y0:y1, x0:x1], self.M[y0:y1, x0:x1], U, Z)

    def fill(self, key, col, rough, metal=0.0, seed=0, var=0.03, sigma=3.0):
        D, H, R, M, U, Z = self.region(key, 1, 1)
        hh, ww = D.shape[:2]
        n = _noise(hh, ww, sigma, seed) * var + _noise(hh, ww, sigma * 10, seed + 1) * var
        D[:] = _c(col)[None, None] * (1 + n)[..., None]
        R[:] = rough + n * 0.4
        M[:] = metal
        H[:] = 0
        return n

    def save(self, base, nstr=2.5):
        nrm = tp.normal_dx(self.H, nstr)
        ao = np.clip(1.0 - 5.0 * np.maximum(tp.blur(self.H, 5.0) - self.H, 0), 0.4, 1.0)
        os.makedirs(TEXDIR, exist_ok=True)
        tp.save(np.clip(self.D, 0, 1), f"{TEXDIR}/{base}_D.png")
        tp.save(nrm, f"{TEXDIR}/{base}_N.png")
        tp.save(np.dstack([ao, np.clip(self.R, 0.04, 1), self.M]), f"{TEXDIR}/{base}_ORM.png")


def _raster(polys, W, H, ss=3):
    """Maschera H x W (riga 0 in alto): unione di poligoni in pixel, ciascuno rasterizzato (pari-dispari) solo nel suo
    riquadro: veloce anche per le migliaia di triangoli del testo."""
    m = np.zeros((H, W), np.float32)
    for poly in polys:
        p = np.asarray(poly, np.float32)
        x0, y0 = np.floor(p.min(axis=0)).astype(int)
        x1, y1 = np.ceil(p.max(axis=0)).astype(int) + 1
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
        if x1 <= x0 or y1 <= y0:
            continue
        ys, xs = np.mgrid[y0 * ss:y1 * ss, x0 * ss:x1 * ss].astype(np.float32)
        X, Y = (xs + 0.5) / ss, (ys + 0.5) / ss
        ins = np.zeros(X.shape, bool)
        for (ax, ay), (bx, by) in zip(p, np.roll(p, -1, axis=0)):
            if ay == by:
                continue
            c = (ay > Y) != (by > Y)
            xint = ax + (Y - ay) * (bx - ax) / (by - ay)
            ins ^= c & (X < xint)
        cov = ins.reshape(y1 - y0, ss, x1 - x0, ss).mean(axis=(1, 3)).astype(np.float32)
        m[y0:y1, x0:x1] = np.maximum(m[y0:y1, x0:x1], cov)
    return m


def _mask_text(body, x0, y0, w, h, W, H, space=1.0):
    import morin_blocco2_v2 as v2
    return _raster(v2.text_polys(body, x0, y0, w, h, space), W, H)


def _poly_mask(polys, W, H):
    return _raster(polys, W, H)


def _paint(D, m, col):
    D[:] = D * (1 - m[..., None]) + _c(col)[None, None] * m[..., None]


def _planks(D, H, R, U, Z, sel, seed, w=0.12, col=LEGNO):
    """Doghe verticali verniciate (perline) con venatura, fughe e usura in basso."""
    rng = np.random.default_rng(seed)
    hh, ww = D.shape[:2]
    idx = np.floor(U / w).astype(int)
    tint = rng.uniform(0.82, 1.12, idx.max() + 2)[idx]
    grain = _noise(hh, ww, 1.0, seed + 1)
    grain = tp.blur(grain, 0.6) * 0.5 + np.sin((U * 37 + _noise(hh, ww, 30, seed + 2) * 0.6) * 9.0) * 0.5
    c = _c(col)[None, None] * (tint * (1 + 0.07 * grain))[..., None]
    D[sel] = c[sel]
    R[sel] = 0.42 + 0.05 * grain[sel]
    gr = sel & (np.abs(U / w - np.round(U / w)) * w < 0.004)
    D[gr] *= 0.45
    H[gr] -= 0.8
    H[sel] += 0.05 * grain[sel]


def _painted(D, H, R, U, Z, sel, col, seed, rough=0.5):
    hh, ww = D.shape[:2]
    n = _noise(hh, ww, 2.0, seed) * 0.02 + _noise(hh, ww, 25, seed + 1) * 0.03
    D[sel] = (_c(col)[None, None] * (1 + n)[..., None])[sel]
    R[sel] = rough + n[sel]


def _dirt(D, Z, z0, k=0.25, s=0.15):
    D *= (1 - k * np.exp(-np.maximum(Z - z0, 0) / s))[..., None]


def _tex_facade(A, key, kind, seed):
    """Facciata di un lato: L_SIDE x 2,5 m (z 0,12 -> 2,62)."""
    D, H, R, M, U, Zr = A.region(key, L_SIDE, Z_C - Z0)
    Z = Zr + Z0
    hh, ww = D.shape[:2]
    _painted(D, H, R, U, Z, np.ones_like(U, bool), CREMA, seed)
    low = Z < Z_BANCO
    _planks(D, H, R, U, Z, low & (Z > 0.24), seed + 3)
    kick = Z <= 0.24
    _painted(D, H, R, U, Z, kick, (88, 90, 92), seed + 4, 0.35)
    M[kick] = 0.8
    H[np.abs(Z - 0.24) < 0.006] -= 0.6
    # cornice superiore: fascia bianca con bordo
    fas = Z > Z_V1
    _painted(D, H, R, U, Z, fas, BIANCO, seed + 5, 0.4)
    H[np.abs(Z - Z_V1) < 0.008] -= 0.7
    if kind == "banco":
        _painted(D, H, R, U, Z, (Z >= Z_BANCO) & (Z <= Z_V1), BIANCO, seed + 6, 0.35)   # stipiti in acciaio verniciato
        m = _mask_text("FOCACCIA  ·  GELATI  ·  SPRITZ", ww * 0.06, hh * 0.035, ww * 0.88, hh * 0.06, ww, hh, 1.05)
        _paint(D, m, (24, 62, 104))
    else:
        up = (Z >= Z_BANCO) & (Z <= Z_V1)
        # pannelli crema con cornice in rilievo (due specchiature)
        for a, b in ((0.10, L_SIDE / 2 - 0.04), (L_SIDE / 2 + 0.04, L_SIDE - 0.10)):
            fr = up & (U > a) & (U < b) & (Z > Z_BANCO + 0.10) & (Z < Z_V1 - 0.10)
            ed = fr & ~((U > a + 0.025) & (U < b - 0.025) & (Z > Z_BANCO + 0.125) & (Z < Z_V1 - 0.125))
            H[ed] += 0.6
            D[ed] *= 1.04
        H[np.abs(Z - Z_BANCO) < 0.008] -= 0.6
        if kind == "poster":
            rng = np.random.default_rng(seed)
            # locandina gelati (sinistra) e lavagna del menu (destra), grafiche inventate
            pa = up & (U > 0.20) & (U < 1.0) & (Z > 1.25) & (Z < 2.15)
            _painted(D, H, R, U, Z, pa, (246, 236, 214), seed + 7, 0.3)
            for cx, cz, r, col in ((0.48, 1.86, 0.11, (236, 160, 186)), (0.70, 1.88, 0.11, (122, 78, 52)),
                                   (0.59, 2.00, 0.10, (246, 230, 150))):
                _paint(D, (((U - cx) ** 2 + (Z - cz) ** 2) < r * r).astype(np.float32) * pa, col)
            cone = _poly_mask([[((0.44 - 0) * ww / L_SIDE, (Z_C - 1.80) * hh / (Z_C - Z0)),
                                ((0.74) * ww / L_SIDE, (Z_C - 1.80) * hh / (Z_C - Z0)),
                                ((0.59) * ww / L_SIDE, (Z_C - 1.38) * hh / (Z_C - Z0))]], ww, hh)
            _paint(D, cone, (214, 170, 96))
            m = _mask_text("GELATI", 0.26 * ww / L_SIDE, (Z_C - 1.36) * hh / (Z_C - Z0), 0.68 * ww / L_SIDE,
                           0.08 * hh / (Z_C - Z0), ww, hh)
            _paint(D, m, (200, 40, 60))
            pb = up & (U > 1.26) & (U < 2.06) & (Z > 1.20) & (Z < 2.15)
            _painted(D, H, R, U, Z, pb, (34, 38, 36), seed + 8, 0.7)
            fb = pb & ~((U > 1.29) & (U < 2.03) & (Z > 1.23) & (Z < 2.12))
            _paint(D, fb.astype(np.float32), (140, 100, 60))
            H[fb] += 0.6
            m = _mask_text("MENU", 1.40 * ww / L_SIDE, (Z_C - 2.08) * hh / (Z_C - Z0), 0.52 * ww / L_SIDE,
                           0.09 * hh / (Z_C - Z0), ww, hh)
            _paint(D, m, (236, 232, 220))
            for i, row in enumerate(("FOCACCIA  2,00", "FARINATA  2,50", "PANIGACCI 4,00", "SPRITZ    5,00",
                                     "CAFFE'    1,20", "GELATO    2,50")):
                m = _mask_text(row, 1.36 * ww / L_SIDE, (Z_C - 1.92 + i * 0.105) * hh / (Z_C - Z0), 0.60 * ww / L_SIDE,
                               0.055 * hh / (Z_C - Z0), ww, hh)
                _paint(D, m * 0.9, (226, 222, 210))
        if kind == "porta":
            dh = 0.40
            door = (np.abs(U - L_SIDE / 2) < dh) & (Z < Z_PORTA)
            _painted(D, H, R, U, Z, door, (96, 112, 104), seed + 9, 0.35)
            M[door] = 0.6
            fr = door & ((np.abs(np.abs(U - L_SIDE / 2) - dh) < 0.03) | (Z > Z_PORTA - 0.03))
            _paint(D, fr.astype(np.float32), (70, 74, 72))
            lou = door & (Z > 0.25) & (Z < 0.62) & (np.abs(U - L_SIDE / 2) < 0.28) & (np.mod(Z, 0.045) < 0.02)
            D[lou] *= 0.55
            H[lou] -= 0.6
            han = (np.abs(U - L_SIDE / 2 - 0.30) < 0.012) & (np.abs(Z - 1.05) < 0.10)
            _paint(D, han.astype(np.float32), (200, 200, 196))
            M[han] = 1.0
            st = door & (np.abs(U - L_SIDE / 2) < 0.16) & (np.abs(Z - 1.55) < 0.05)
            _painted(D, H, R, U, Z, st, (236, 228, 60), seed + 10, 0.3)
            m = _mask_text("PRIVATO", (L_SIDE / 2 - 0.14) * ww / L_SIDE, (Z_C - 1.585) * hh / (Z_C - Z0), 0.28 * ww / L_SIDE,
                           0.05 * hh / (Z_C - Z0), ww, hh)
            _paint(D, m, (20, 20, 20))
            H[np.abs(Z - 0.24) < 0.006] += 0.6
    _dirt(D, Z, Z0, 0.28, 0.12)
    _dirt(D, Z_C + Z0 - Z, Z0, 0.10, 0.05)   # ombra sotto la gronda


def _seagull(cx, cy, s):
    """Gabbiano stilizzato (silhouette a M) in pixel, y verso il basso."""
    P = [(-1.0, 0.05), (-0.55, -0.32), (-0.18, -0.12), (0.0, 0.02), (0.18, -0.12), (0.55, -0.32), (1.0, 0.05),
         (0.55, -0.16), (0.2, 0.06), (0.0, 0.16), (-0.2, 0.06), (-0.55, -0.16)]
    return [(cx + x * s, cy - y * s) for x, y in P]


def make_tex_atlas():
    A = Atlas()
    _tex_facade(A, "fac_banco", "banco", 21)
    _tex_facade(A, "fac_pann", "pann", 22)
    _tex_facade(A, "fac_poster", "poster", 23)
    _tex_facade(A, "fac_porta", "porta", 24)
    # insegna: pannello bianco con bordo blu, nome e sottotitolo, gabbiano con la focaccia nel becco
    D, H, R, M, U, Z = A.region("insegna", SIGN_W, SIGN_Z1 - SIGN_Z0)
    hh, ww = D.shape[:2]
    _painted(D, H, R, U, Z, np.ones_like(U, bool), (246, 246, 242), 31, 0.3)
    bd = ~((U > 0.04) & (U < SIGN_W - 0.04) & (Z > 0.04) & (Z < SIGN_Z1 - SIGN_Z0 - 0.04))
    _paint(D, bd.astype(np.float32), (22, 70, 130))
    H[bd] += 0.5
    _paint(D, _mask_text(NOME, ww * 0.20, hh * 0.14, ww * 0.76, hh * 0.44, ww, hh, 1.02), (22, 70, 130))
    _paint(D, _mask_text(SOTTO, ww * 0.26, hh * 0.66, ww * 0.64, hh * 0.18, ww, hh, 1.1), (200, 60, 40))
    g = _poly_mask([_seagull(ww * 0.105, hh * 0.52, hh * 0.32)], ww, hh)
    _paint(D, g, (40, 44, 52))
    fo = _poly_mask([[(ww * 0.112, hh * 0.56), (ww * 0.15, hh * 0.60), (ww * 0.13, hh * 0.68), (ww * 0.10, hh * 0.64)]], ww, hh)
    _paint(D, fo, (226, 176, 80))
    # mantovane: tela bianca con orlo; quella dei lati verso il mare con il nome
    for key, txt in (("mant_nome", True), ("mant", False)):
        D, H, R, M, U, Z = A.region(key, 3.0, 0.30)
        hh, ww = D.shape[:2]
        _painted(D, H, R, U, Z, np.ones_like(U, bool), BIANCO, 32, 0.8)
        D *= (1 + 0.03 * np.sin(U * 2 * math.pi / 0.006))[..., None] * 1.0
        hem = (Z < 0.035) | (Z > 0.265)
        _paint(D, hem.astype(np.float32), (22, 70, 130))
        H[hem] += 0.3
        if txt:
            _paint(D, _mask_text(NOME, ww * 0.12, hh * 0.25, ww * 0.76, hh * 0.5, ww, hh, 1.05), (22, 70, 130))
        R[:] = 0.85
    # tetto: lamiera bianca grecata (greche lungo V)
    D, H, R, M, U, Z = A.region("tetto", 2.0, 2.0)
    hh, ww = D.shape[:2]
    _painted(D, H, R, U, Z, np.ones_like(U, bool), (232, 232, 228), 33, 0.45)
    rib = np.abs(np.mod(U, 0.25) - 0.125) > 0.105
    H[rib] += 1.0
    D[rib] *= 1.03
    D *= (1 - 0.06 * np.clip(_noise(hh, ww, 40, 34), 0, None))[..., None]    # sporco/colature
    M[:] = 0.3
    A.fill("bianco", BIANCO, 0.35, metal=0.5, seed=35, var=0.01)
    A.fill("intradosso", (226, 224, 218), 0.6, seed=36, var=0.015)
    D, H, R, M, U, Z = A.region("intradosso", 1.0, 1.0)
    H[np.mod(U, 0.10) < 0.004] -= 0.6            # perline del soffitto
    D[np.mod(U, 0.10) < 0.004] *= 0.85
    # piano del bancone: legno massello verniciato, doghe lungo U
    D, H, R, M, U, Z = A.region("legno_banco", 2.4, 0.6)
    _planks(D, H, R, Z, U, np.ones_like(U, bool), 37, w=0.15, col=(160, 104, 62))
    R[:] = 0.3
    # interni (si vedono dietro le vetrine)
    D, H, R, M, U, Z = A.region("scaffale", 1.7, 2.1)
    hh, ww = D.shape[:2]
    _painted(D, H, R, U, Z, np.ones_like(U, bool), (70, 52, 40), 38, 0.6)
    rng = np.random.default_rng(39)
    for zs in (0.9, 1.3, 1.7):
        sh = np.abs(Z - zs) < 0.015
        _paint(D, sh.astype(np.float32), (200, 196, 188))
        u = 0.05
        while u < 1.62:
            w, h = rng.uniform(0.05, 0.09), rng.uniform(0.18, 0.30)
            col = [(38, 92, 52), (150, 85, 25), (175, 185, 175), (120, 30, 35), (60, 60, 120), (210, 190, 90),
                   (230, 230, 225), (200, 60, 40)][rng.integers(0, 8)]
            b = (Z > zs + 0.015) & (Z < zs + h) & (np.abs(U - u - w / 2) < w / 2)
            b &= (Z < zs + h * 0.65) | (np.abs(U - u - w / 2) < w * 0.18)
            D[b] = _c(col) * (0.85 + 0.4 * (np.abs(U[b] - u - w * 0.3) < w * 0.1))[:, None]
            u += w + rng.uniform(0.01, 0.04)
    low = Z < 0.85
    _painted(D, H, R, U, Z, low, (210, 206, 198), 40, 0.4)
    H[low & (np.abs(np.mod(U, 0.567) - 0.28) < 0.004)] -= 0.5
    D, H, R, M, U, Z = A.region("frigo", 1.0, 1.8)
    _painted(D, H, R, U, Z, np.ones_like(U, bool), (230, 230, 228), 41, 0.3)
    gl = (U > 0.06) & (U < 0.94) & (Z > 0.25) & (Z < 1.72)
    _painted(D, H, R, U, Z, gl, (60, 76, 88), 42, 0.08)
    rng = np.random.default_rng(43)
    for zs in (0.35, 0.72, 1.09, 1.42):
        for k in range(10):
            uu = 0.10 + k * 0.08
            b = gl & (np.abs(U - uu) < 0.028) & (Z > zs) & (Z < zs + 0.22)
            D[b] = _c([(200, 40, 40), (240, 180, 40), (60, 140, 70), (230, 230, 230), (60, 90, 170)][rng.integers(0, 5)])
    _paint(D, _mask_text("BIBITE FRESCHE", 1.0 * 0.12 / 1.0 * D.shape[1], D.shape[0] * 0.03, D.shape[1] * 0.76,
                         D.shape[0] * 0.05, D.shape[1], D.shape[0]), (200, 40, 40))
    A.fill("pavimento", (178, 172, 160), 0.6, seed=44, var=0.04)
    D, H, R, M, U, Z = A.region("pavimento", 1.2, 1.2)
    j = (np.mod(U, 0.30) < 0.006) | (np.mod(Z, 0.30) < 0.006)
    D[j] *= 0.6
    H[j] -= 0.6
    A.fill("acciaio", (176, 178, 180), 0.28, metal=0.95, seed=45, var=0.02, sigma=1.0)
    D, H, R, M, U, Z = A.region("macchina", 1.0, 1.0)
    _painted(D, H, R, U, Z, np.ones_like(U, bool), (60, 60, 64), 46, 0.3)
    M[:] = 0.7
    for cx in (0.28, 0.72):
        b = (np.abs(U - cx) < 0.12) & (Z > 0.25) & (Z < 0.55)
        _painted(D, H, R, U, Z, b, (190, 192, 196), 47, 0.2)
        M[b] = 1.0
    _painted(D, H, R, U, Z, Z > 0.82, (160, 30, 30), 48, 0.3)
    A.fill("scuro", (56, 58, 60), 0.5, metal=0.4, seed=49, var=0.02)
    A.fill("interno", (214, 208, 196), 0.7, seed=50, var=0.02)
    A.fill("zoccolo", (120, 118, 112), 0.85, seed=51, var=0.06, sigma=1.5)
    D, H, R, M, U, Z = A.region("cassetti", 2.0, 0.85)
    _painted(D, H, R, U, Z, np.ones_like(U, bool), (200, 202, 204), 52, 0.3)
    M[:] = 0.85
    j = (np.abs(np.mod(U, 0.5) - 0.25) > 0.245) | (np.abs(Z - 0.42) < 0.004)
    H[j] -= 0.7
    D[j] *= 0.6
    hd = (np.abs(np.mod(U, 0.5) - 0.25) < 0.08) & ((np.abs(Z - 0.36) < 0.008) | (np.abs(Z - 0.78) < 0.008))
    D[hd] *= 0.7
    A.save("T_Morin_ChioscoOtt_v3")


def make_tex_vetro():
    s = 512
    rng_n = _noise(s, s, 18, 60)
    D = np.dstack([np.full((s, s), 0.30), np.full((s, s), 0.37), np.full((s, s), 0.41)]).astype(np.float32)
    yy = (np.arange(s)[:, None] + 0.5) / s * np.ones((1, s))           # riga 0 in alto
    smudge = np.clip(0.5 + 0.5 * rng_n, 0, 1)
    alpha = 0.16 + 0.10 * np.clip(yy - 0.6, 0, 1) * 2.5 * smudge + 0.04 * smudge
    D *= (1 - 0.08 * smudge)[..., None]
    rough = 0.04 + 0.10 * smudge * np.clip(yy - 0.5, 0, 1)
    tp.save(np.dstack([D, alpha]), f"{TEXDIR}/T_Morin_ChioscoOtt_v3_Vetro_D.png")
    tp.save(np.dstack([np.full((s, s), 0.5), np.full((s, s), 0.5), np.ones((s, s))]), f"{TEXDIR}/T_Morin_ChioscoOtt_v3_Vetro_N.png")
    tp.save(np.dstack([np.ones((s, s)), rough, np.zeros((s, s))]), f"{TEXDIR}/T_Morin_ChioscoOtt_v3_Vetro_ORM.png")


def make_textures():
    os.makedirs(TEXDIR, exist_ok=True)
    make_tex_atlas()
    make_tex_vetro()


def build_materials():
    b = f"{TEXDIR}/T_Morin_ChioscoOtt_v3"
    m = pk._pbr_material(MAT_A, b + "_D.png", b + "_N.png", b + "_ORM.png")
    v = pk._pbr_material(MAT_V, b + "_Vetro_D.png", b + "_Vetro_N.png", b + "_Vetro_ORM.png", alpha=True)
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(v, attr, val)
        except (AttributeError, TypeError):
            pass
    for im in bpy.data.images:
        if im.name.startswith("T_Morin_ChioscoOtt_v3"):
            im.reload()
    return m, v


# =============================================================================================================
# geometria: solidi chiusi con avvolgimento per costruzione
# =============================================================================================================
class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.info = {}        # faccia -> (regione, frame)

    def face(self, pts, out_dir, reg, frame=None):
        pts = [Vector(p) for p in pts]
        n = Vector((0, 0, 0))
        for a, b in zip(pts, pts[1:] + pts[:1]):
            n += a.cross(b)
        if n.length < 1e-9:
            return None
        if n.dot(Vector(out_dir)) < 0:
            pts.reverse()
        f = self.bm.faces.new([self.bm.verts.new(p) for p in pts])
        self.info[f] = (reg, frame)
        return f

    def solid(self, P, faces, regs, frame=None):
        """P: 8 vertici [b00,b10,b11,b01 (basso), t00,t10,t11,t01 (alto)]; facce scelte fra bot,top,f0,f1,f2,f3
        (f0 = P0-P1, f1 = P1-P2 ...). Normale verso l'esterno del solido (centroide)."""
        c = sum(P, Vector()) / 8
        Q = {"bot": [0, 1, 2, 3], "top": [4, 5, 6, 7], "f0": [0, 1, 5, 4], "f1": [1, 2, 6, 5], "f2": [2, 3, 7, 6],
             "f3": [3, 0, 4, 7]}
        out = {}
        for k in faces:
            pts = [P[i] for i in Q[k]]
            fc = sum(pts, Vector()) / 4
            reg = regs.get(k, regs.get("*"))
            fr = frame.get(k) if isinstance(frame, dict) else None
            out[k] = self.face(pts, fc - c, reg, fr)
        return out


def _side(k):
    a = math.radians(45.0 * k)
    n = Vector((math.cos(a), math.sin(a), 0.0))
    t = Vector((-n.y, n.x, 0.0))
    return n, t


def _P(k, s, d, z):
    """Punto del lato k: s = frazione (-1..1) della mezza lunghezza alla distanza d (spigoli a 45 gradi: mitre)."""
    n, t = _side(k)
    return n * d + t * (s * d * T8) + Vector((0, 0, z))


def _Pu(k, u, d, z):
    """Come _P ma con u assoluto in metri lungo il lato."""
    n, t = _side(k)
    return n * d + t * u + Vector((0, 0, z))


def _seg(k, s0, s1, d0, d1, z0, z1, absu=False):
    f = _Pu if absu else _P
    return [f(k, s0, d0, z0), f(k, s1, d0, z0), f(k, s1, d1, z0), f(k, s0, d1, z0),
            f(k, s0, d0, z1), f(k, s1, d0, z1), f(k, s1, d1, z1), f(k, s0, d1, z1)]
# nel solido di _seg: f0 = faccia interna (d0), f1 = estremo s1, f2 = esterna (d1), f3 = estremo s0


def _facade_key(k):
    return "fac_banco" if k in FRONT else "fac_porta" if k == DOOR else "fac_poster" if k in POSTER else "fac_pann"


def _frame(k):
    """Frame UV continuo della facciata del lato k (esterno, apotema A_OUT)."""
    return ("side", k)


def build(coll, lod=0, name=NAME):
    B = Builder()
    dS = 0.40 / (A_OUT * T8)                                 # mezza porta (0,40 m) come frazione
    for k in range(8):
        fk = _facade_key(k)
        ext = {"f2": _frame(k)}
        regs = {"f0": "interno", "f2": fk, "*": "bianco"}
        if k in FRONT:
            B.solid(_seg(k, -1, 1, A_IN, A_OUT, Z0, Z_BANCO), ["f0", "f2"], regs, ext)
            jam = 0.92
            if lod < 2:
                B.solid(_seg(k, -1, -jam, A_IN, A_OUT, Z_BANCO1, Z_V1), ["f0", "f2", "f1"], regs, ext)
                B.solid(_seg(k, jam, 1, A_IN, A_OUT, Z_BANCO1, Z_V1), ["f0", "f2", "f3"], regs, ext)
                B.solid(_seg(k, -1, 1, A_IN, A_OUT, Z_V1, Z_C), ["f0", "f2", "bot"], regs, ext)
            else:
                B.solid(_seg(k, -1, 1, A_IN, A_OUT, Z_V1, Z_C), ["f0", "f2", "bot"], regs, ext)
                B.solid(_seg(k, -1, -jam, A_IN, A_OUT, Z_BANCO1, Z_V1), ["f2"], regs, ext)
                B.solid(_seg(k, jam, 1, A_IN, A_OUT, Z_BANCO1, Z_V1), ["f2"], regs, ext)
            # vetro (materiale 1), leggermente arretrato
            dg = A_OUT - 0.035
            g = [_P(k, -jam * A_OUT / dg, dg, Z_BANCO1), _P(k, jam * A_OUT / dg, dg, Z_BANCO1),
                 _P(k, jam * A_OUT / dg, dg, Z_V1), _P(k, -jam * A_OUT / dg, dg, Z_V1)]
            n, _ = _side(k)
            B.face(g, n, "vetro")
            if lod == 0:   # montanti
                for um in (-L_SIDE / 6, L_SIDE / 6):
                    P = _seg(k, um - 0.022, um + 0.022, A_OUT - 0.06, A_OUT - 0.005, Z_BANCO1, Z_V1, absu=True)
                    B.solid(P, ["f1", "f2", "f3"], {"*": "bianco"})
            # piano del bancone (mitre fra i lati del fronte; estremi chiusi solo verso i lati senza bancone)
            faces = ["top", "bot", "f2"]
            if k == FRONT[0]:
                faces.append("f3")
            if k == FRONT[-1]:
                faces.append("f1")
            if lod < 2:
                faces.append("f0")
            B.solid(_seg(k, -1, 1, A_IN - BANCO_IN, A_OUT + BANCO_OUT, Z_BANCO, Z_BANCO1), faces,
                    {"top": "legno_banco", "bot": "scuro", "*": "legno_banco"})
        elif k == DOOR:
            B.solid(_seg(k, -1, -dS * A_OUT / A_OUT, A_IN, A_OUT, Z0, Z_C), ["f0", "f2", "f1"], regs, ext)
            B.solid(_seg(k, dS, 1, A_IN, A_OUT, Z0, Z_C), ["f0", "f2", "f3"], regs, ext)
            B.solid(_seg(k, -dS, dS, A_IN, A_OUT, Z_PORTA, Z_C), ["f0", "f2", "bot"], regs, ext)
            dd = A_OUT - 0.04
            B.solid(_seg(k, -dS * A_OUT / dd, dS * A_OUT / dd, dd - 0.04, dd, Z0, Z_PORTA), ["f0", "f2"],
                    {"f2": fk, "f0": "acciaio"}, ext)
        else:
            B.solid(_seg(k, -1, 1, A_IN, A_OUT, Z0, Z_C), ["f0", "f2"], regs, ext)
    # zoccolo: prisma ottagonale (pavimento interno sopra, fascia in pietra ai lati)
    RZ = R0 + 0.06
    bot = [_P(k, -1, RZ * math.cos(math.pi / 8), 0.0) for k in range(8)]
    top = [_P(k, -1, RZ * math.cos(math.pi / 8), Z0) for k in range(8)]
    B.face(top, (0, 0, 1), "pavimento")
    for k in range(8):
        j = (k + 1) % 8
        n, _ = _side(k)
        # gli spigoli dell'ottagono sono a s = -1 del lato k e a s = +1 del lato k-1
        pa, pb = _P(k, -1, RZ * math.cos(math.pi / 8), 0.0), _P(k, 1, RZ * math.cos(math.pi / 8), 0.0)
        B.face([pa, pb, pb + Vector((0, 0, Z0)), pa + Vector((0, 0, Z0))], n, "zoccolo")
    # pilastrini d'angolo
    if lod < 2:
        for k in range(8):
            c = _P(k, -1, A_OUT, 0.0)
            rd = Vector((c.x, c.y, 0)).normalized()
            tg = Vector((-rd.y, rd.x, 0))
            P = []
            for z in (Z0, Z_C):
                for a, b in ((-0.04, -0.05), (-0.04, 0.05), (0.035, 0.05), (0.035, -0.05)):
                    P.append(c + rd * a + tg * b + Vector((0, 0, z)))
            B.solid(P, ["f0", "f1", "f2", "f3"], {"*": "bianco"})
    # interni
    if lod < 2:
        for k in FRONT:          # piano di lavoro sotto il bancone, lungo le vetrine
            faces = ["top", "f0"] + (["f3"] if k == FRONT[0] else []) + (["f1"] if k == FRONT[-1] else [])
            B.solid(_seg(k, -1, 1, A_IN - 0.60, A_IN, Z0, 0.92), faces, {"f0": "cassetti", "top": "acciaio", "*": "acciaio"})
        for k in (1, 3):         # scaffali con bottiglie
            B.solid(_seg(k, -0.85, 0.85, A_IN - 0.38, A_IN, Z0, 2.15), ["f0", "top", "f1", "f3"],
                    {"f0": "scaffale", "*": "scuro"})
        for k in POSTER:         # frigoriferi a vetrina
            B.solid(_seg(k, -0.55, 0.55, A_IN - 0.68, A_IN, Z0, 1.95), ["f0", "top", "f1", "f3"],
                    {"f0": "frigo", "*": "bianco"})
    if lod == 0:                 # macchina del caffe' e registratore di cassa sul piano di lavoro
        B.solid(_seg(6, -0.62, -0.08, A_IN - 0.52, A_IN - 0.08, 0.92, 1.40, absu=True), ["f0", "top", "f1", "f3"],
                {"f0": "macchina", "*": "acciaio"})
        B.solid(_seg(6, 0.30, 0.62, A_IN - 0.45, A_IN - 0.15, 0.92, 1.10, absu=True), ["f0", "top", "f1", "f3"],
                {"*": "scuro"})
    # tettoia chiusa: soffitto (giu'), mantovana interna, orlo, mantovana esterna, falde, colmo
    rin = RE - 0.012
    Ci = [_P(k, -1, rin * math.cos(math.pi / 8), Z_C) for k in range(8)]
    B.face(Ci, (0, 0, -1), "intradosso")
    for k in range(8):
        j = (k + 1) % 8
        n, _ = _side(k)
        ao, ai = RE * math.cos(math.pi / 8), rin * math.cos(math.pi / 8)
        o0, o1 = _P(k, -1, ao, Z_M0), _P(k, 1, ao, Z_M0)
        i0, i1 = _P(k, -1, ai, Z_M0), _P(k, 1, ai, Z_M0)
        mk = "mant_nome" if k in FRONT else "mant"
        B.face([o0, o1, o1 + Vector((0, 0, Z_E - Z_M0)), o0 + Vector((0, 0, Z_E - Z_M0))], n, mk)
        if lod < 2:
            B.face([i0, i1, i1 + Vector((0, 0, Z_C - Z_M0)), i0 + Vector((0, 0, Z_C - Z_M0))], -n, "mant")
            B.face([i0, i1, o1, o0], (0, 0, -1), "mant")
        else:
            # LOD2: niente spessore della mantovana; il soffitto scende a chiudere sull'orlo
            B.face([i0, i1, i1 + Vector((0, 0, Z_C - Z_M0)), i0 + Vector((0, 0, Z_C - Z_M0))], -n, "mant")
        t0, t1 = _P(k, -1, TOPR * math.cos(math.pi / 8), Z_T), _P(k, 1, TOPR * math.cos(math.pi / 8), Z_T)
        e0, e1 = o0 + Vector((0, 0, Z_E - Z_M0)), o1 + Vector((0, 0, Z_E - Z_M0))
        B.face([e0, e1, t1, t0], n + Vector((0, 0, 3)), "tetto")
    B.face([_P(k, -1, TOPR * math.cos(math.pi / 8), Z_T) for k in range(8)], (0, 0, 1), "tetto")
    # insegna sul colmo (pannello bifacciale) con due ritti
    a = math.radians(SIGN_YAW)
    ns = Vector((math.cos(a), math.sin(a), 0))
    ts = Vector((-ns.y, ns.x, 0))

    def sp(u, d, z):
        return ts * u + ns * d + Vector((0, 0, z))
    hw, ht = SIGN_W / 2, SIGN_T / 2
    P = [sp(-hw, -ht, SIGN_Z0), sp(hw, -ht, SIGN_Z0), sp(hw, ht, SIGN_Z0), sp(-hw, ht, SIGN_Z0),
         sp(-hw, -ht, SIGN_Z1), sp(hw, -ht, SIGN_Z1), sp(hw, ht, SIGN_Z1), sp(-hw, ht, SIGN_Z1)]
    B.solid(P, ["bot", "top", "f0", "f1", "f2", "f3"], {"f0": "insegna", "f2": "insegna", "*": "bianco"})
    for u in (-hw * 0.6, hw * 0.6):
        P = [sp(u - 0.04, -0.04, Z_T), sp(u + 0.04, -0.04, Z_T), sp(u + 0.04, 0.04, Z_T), sp(u - 0.04, 0.04, Z_T),
             sp(u - 0.04, -0.04, SIGN_Z0), sp(u + 0.04, -0.04, SIGN_Z0), sp(u + 0.04, 0.04, SIGN_Z0),
             sp(u - 0.04, 0.04, SIGN_Z0)]
        B.solid(P, ["f0", "f1", "f2", "f3"], {"*": "bianco"})
    # UV e materiali
    bm = B.bm
    bm.normal_update()
    for f in bm.faces:
        reg, fr = B.info[f]
        _uv(f, B.uv, reg, fr)
        f.material_index = 1 if reg == "vetro" else 0
    o = pk._finish(name + ("" if lod == 0 else f"_LOD{lod}"), bm, [MAT_A, MAT_V], coll, uv=None, smooth_angle=None)
    for l in [l for l in o.data.uv_layers if l.name != "UVMap"]:
        o.data.uv_layers.remove(l)
    if lod == 0:
        body = [tuple(_P(k, -1, A_OUT, z)) for k in range(8) for z in (0.0, Z_C)]
        pk._ucx_hull(name, 0, body, coll)
        roof = [tuple(_P(k, -1, RE * math.cos(math.pi / 8), Z_M0)) for k in range(8)] + \
               [tuple(_P(k, -1, TOPR * math.cos(math.pi / 8), Z_T)) for k in range(8)]
        pk._ucx_hull(name, 1, roof, coll)
        cnt = []
        for k in FRONT:
            for s in (-1, 1):
                for z in (Z_BANCO, Z_BANCO1):
                    cnt.append(tuple(_P(k, s, A_OUT + BANCO_OUT, z)))
        cnt += [(0.0, 0.0, Z_BANCO), (0.0, 0.0, Z_BANCO1)]
        pk._ucx_hull(name, 2, cnt, coll)
        pk._ucx_hull(name, 3, [tuple(sp(u, d, z)) for u in (-hw, hw) for d in (-ht, ht)
                                                            for z in (Z_T, SIGN_Z1)], coll)
    return o


def _uv(f, lay, reg, fr):
    n = f.normal
    if fr is not None and fr[0] == "side":
        k = fr[1]
        sn, st = _side(k)
        u0, u1, v0, v1 = -L_SIDE / 2, L_SIDE / 2, Z0, Z_C
        pts = [(lp.vert.co.dot(st), lp.vert.co.z) for lp in f.loops]
        # vista da fuori (guardando verso il centro) la destra e' +t
        key = reg
        r = REG[key]
        for lp, (a, b) in zip(f.loops, pts):
            lp[lay].uv = (r[0] + (r[2] - r[0]) * np.clip((a - u0) / (u1 - u0), 0, 1),
                          r[1] + (r[3] - r[1]) * np.clip((b - v0) / (v1 - v0), 0, 1))
        return
    if reg == "vetro":
        r = (0.0, 0.0, 1.0, 1.0)
    else:
        r = REG[reg]
    if abs(n.z) > 0.95:
        right = Vector((1, 0, 0))
    else:
        right = (-n).cross(Vector((0, 0, 1))).normalized()
    up = n.cross(right).normalized()
    pts = [(lp.vert.co.dot(right), lp.vert.co.dot(up)) for lp in f.loops]
    a0, a1 = min(p[0] for p in pts), max(p[0] for p in pts)
    b0, b1 = min(p[1] for p in pts), max(p[1] for p in pts)
    m = 0.015
    for lp, (a, b) in zip(f.loops, pts):
        fa = (a - a0) / max(a1 - a0, 1e-6)
        fb = (b - b0) / max(b1 - b0, 1e-6)
        lp[lay].uv = (r[0] + (r[2] - r[0]) * (m + (1 - 2 * m) * fa), r[1] + (r[3] - r[1]) * (m + (1 - 2 * m) * fb))


# =============================================================================================================
# build, QA, export
# =============================================================================================================
def build_all():
    coll = pk._coll(KIT)
    rep = {}
    for lod in range(3):
        o = build(coll, lod)
        rep[o.name] = (pk.tri_count(o), tuple(round(d, 3) for d in o.dimensions))
    for o in coll.objects:
        if o.name.startswith(NAME) or o.name.startswith("UCX_" + NAME):
            hide = o.name.startswith("UCX") or "_LOD" in o.name
            o.hide_render = hide
            o.hide_viewport = hide
    for k, v in rep.items():
        print(k, "tri", v[0], "dim", v[1])
    return rep


def qa(names=None, verbose=True):
    """Ray test dall'esterno (8 lati x 6 quote + dall'alto), facce coincidenti, area/UV degeneri, slot materiali."""
    from mathutils.bvhtree import BVHTree
    names = names or [NAME, NAME + "_LOD1", NAME + "_LOD2"]
    out = {}
    for nm in names:
        o = bpy.data.objects[nm]
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        bvh = BVHTree.FromBMesh(bm)
        uvl = bm.loops.layers.uv.get("UVMap")
        bad_ray, miss = [], 0
        for k in range(16):
            a = math.radians(22.5 * k)
            d = Vector((math.cos(a), math.sin(a), 0))
            for z in (0.06, 0.6, 1.03, 1.6, 2.5, 2.6, 2.9, 3.5):
                h = bvh.ray_cast(d * 12 + Vector((0, 0, z)), -d)
                if h[0] is None:
                    miss += 1
                    continue
                if bm.faces[h[2]].normal.dot(-d) > 0:
                    bad_ray.append((round(22.5 * k, 1), z))
        for x in np.linspace(-3.5, 3.5, 8):
            for y in np.linspace(-3.5, 3.5, 8):
                h = bvh.ray_cast(Vector((x, y, 10)), Vector((0, 0, -1)))
                if h[0] is not None and bm.faces[h[2]].normal.z < 0:
                    bad_ray.append(("top", round(x, 1), round(y, 1)))
        # facce coincidenti (stesso piano e centri vicini)
        cen = {}
        dup = 0
        for f in bm.faces:
            key = tuple(round(c, 3) for c in f.calc_center_median())
            if key in cen and abs(abs(cen[key].normal.dot(f.normal)) - 1) < 1e-3:
                dup += 1
            cen[key] = f
        zero = sum(1 for f in bm.faces if f.calc_area() < 1e-6)
        uvdeg = 0
        for f in bm.faces:
            p = [l[uvl].uv.copy() for l in f.loops]
            ar = sum(abs((p[i] - p[0]).cross(p[i + 1] - p[0])) for i in range(1, len(p) - 1)) / 2
            if ar < 1e-8:
                uvdeg += 1
        slots = [m.name if m else None for m in o.data.materials]
        used = sorted({p.material_index for p in o.data.polygons})
        out[nm] = dict(tri=pk.tri_count(o), dim=tuple(round(x, 3) for x in o.dimensions), bad_ray=len(bad_ray),
                       miss=miss, dup=dup, zero_area=zero, uv_degen=uvdeg, slots=slots, used=used)
        if verbose:
            print(nm, out[nm], bad_ray[:6])
        bm.free()
    d0 = out[names[0]]["dim"]
    for nm in names[1:]:
        dev = max(abs(a - b) / b for a, b in zip(out[nm]["dim"], d0))
        out[nm]["bbox_dev"] = round(dev * 100, 3)
        if verbose:
            print(nm, "scarto bbox vs LOD0 %", out[nm]["bbox_dev"])
    return out


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
