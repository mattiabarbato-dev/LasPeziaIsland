"""morin_ristorante_c.py — ristorante vicino al ponte (edificio C della radice del molo) con il dehors a righe (2026-11-20).

Scheda: ref/radice_molo.md §3.1 (pianta OSM 205840540: (-12,1; 42,1) (-7,7; 42,2) (-7,5; 24,8) (-11,9; 24,8)), §3.2 riga A5
(dehors lungo con tende a righe blu-bianche, gronda ~2,4 m, profondita' ~3 m, tende laterali bianche, ombrelloni bianchi con palo
in legno, tavoli in legno e sedie, lavagna a cavalletto), §7.1 D8 (dehors completi come in foto). Foto: F3
ref/foto/vista/strada_cheProsegue_verso_il_ponte.png (camera (4,45; 46,4; 2,3), azimut 213,4 gradi, FOV 92,5: §10.1 della scheda).
Dalle foto solo forme, proporzioni e colori campionati: texture procedurali (nessun pixel delle foto), niente UI, persone, targhe,
loghi, ne' il testo della lavagna. Insegna con nome inventato e scherzoso: "Al Muscolo Stanco" (muscoli = cozze in spezzino).

Esegui dentro blender/arte_molo.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_ristorante_c as rc; importlib.reload(rc)
    rc.make_textures(); rc.build_materials(); rc.build_all()
    rows = rc.layout(); rc.write_csv(rows); rc.build_context(rows)
    rc.check_all()          # bbox dei LOD, normali con ray test dall'esterno, tri
    rc.export_all()

Coordinate di progetto (metri, X lungo la passeggiata, Y verso la citta'). Edificio e dehors: pezzi unici con origine (0,0,0),
si posano in (0,0,0). Tavoli, ombrelloni, cavalletto, palme in vaso, fioriere: origine alla base, posa dal CSV.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_texphoto as tp

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/molo"
KIT = "MOLO_C_Kit"
EXPDIR = "//../exports/molo"
Z0 = 0.01                       # quota dei masselli del molo (morin_molo.Z_MOLO)

# ---------------------------------------------------------------------------------------------------------------
# pianta e quote
# ---------------------------------------------------------------------------------------------------------------
POLY_C = [(-12.1, 24.8), (-7.5, 24.8), (-7.7, 42.2), (-12.1, 42.2)]     # antiorario (OSM, lato ovest regolarizzato)
Z_WALL = 3.60                   # filo superiore del muro (sotto la copertina)
Z_TOP = 3.87                    # sommita' della copertina del parapetto (= v1)
Z_ROOF = 3.42                   # piano del tetto dentro il parapetto
PARA_T = 0.25                   # spessore del parapetto
COP_O = 0.045                   # sporto della copertina
REC = 0.16                      # rientro delle aperture
Y_BOX = 38.6                    # a nord di Y_BOX la parte in muratura con la finestra a griglia (F3); a sud il dehors
# tenda: dal muro (Z_ATT) alla trave frontale (Z_EAVE), profondita' AW_D, campate fra AW_Y0 e AW_Y1
AW_Y0, AW_Y1, AW_D = 26.6, 38.6, 3.10
Z_ATT, Z_EAVE, VAL_H = 3.02, 2.46, 0.28
N_BAYS = 4

PPM = 256
ATL = 2048                      # atlante 8 x 8 m


def x_wall(y):
    """X della facciata est alla quota Y (lato (-7,5; 24,8) -> (-7,7; 42,2))."""
    return -7.5 - 0.2 * (y - 24.8) / 17.4


# ---------------------------------------------------------------------------------------------------------------
# atlante T_Molo_RistoranteC (8 x 8 m, u verso destra, v verso l'alto, in metri)
# ---------------------------------------------------------------------------------------------------------------
R_PLASTER = (0.0, 4.0, 4.0, 8.0)          # intonaco bianco, periodico su 4 m in u; v = 4 + quota (zoccolo fino a 0,32)
R_GRID = (4.0, 6.6, 5.2, 8.0)             # finestra a griglia 1,2 x 1,4
R_GLASS = (5.2, 5.5, 7.1, 8.0)            # porta-vetrata 1,9 x 2,5
R_DOOR = (7.1, 5.8, 8.0, 8.0)             # porta di servizio 0,9 x 2,2
R_BAR = (4.0, 3.0, 7.0, 5.4)              # vano del bancone sotto la tenda 3,0 x 2,4
R_BOARD = (7.2, 3.0, 7.8, 3.9)            # lavagna 0,6 x 0,9 (scarabocchi illeggibili)
R_SIGNTXT = (0.0, 3.3, 4.0, 3.9)          # (riservato)
SW = {}                                    # tasselli 0,5 x 0,5 m: v 2,5-3,0 e 2,0-2,5
_SWN = [["copertina", "tetto", "ghiaia", "zincato", "antracite", "nero", "griglia_ac", "bianco_vern",
         "teak", "legno_chiaro", "seduta_blu", "seduta_rossa", "seduta_gialla", "seduta_verde", "vaso_bruno", "terra"],
        ["insegna", "insegna_blu", "cornice_lav", "vaso_bianco", "fibra_palma", "tela_bianca", "piano_bianco", "vetro",
         "alluminio", "cuscino_blu", "intonaco_liscio", "lamiera", "tronco_palma", "corda", "plastica_grigia", "lampada"]]
for _r, _row in enumerate(_SWN):
    for _i, _n in enumerate(_row):
        SW[_n] = (_i * 0.5, 2.5 - 0.5 * _r, _i * 0.5 + 0.5, 3.0 - 0.5 * _r)

COL = {  # sRGB
    "intonaco": (229, 227, 219), "zoccolo": (152, 151, 146), "copertina": (214, 210, 200), "tetto": (92, 92, 90),
    "ghiaia": (150, 146, 138), "zincato": (168, 172, 174), "antracite": (58, 60, 63), "nero": (28, 28, 30),
    "bianco_vern": (236, 236, 232), "teak": (150, 104, 66), "legno_chiaro": (186, 148, 104), "seduta_blu": (44, 82, 150),
    "seduta_rossa": (168, 48, 42), "seduta_gialla": (214, 168, 52), "seduta_verde": (70, 128, 84), "vaso_bruno": (88, 62, 48),
    "terra": (62, 50, 40), "insegna": (240, 240, 236), "insegna_blu": (36, 70, 140), "cornice_lav": (120, 84, 52),
    "vaso_bianco": (232, 232, 228), "fibra_palma": (110, 84, 58), "tela_bianca": (238, 237, 230), "piano_bianco": (232, 230, 224),
    "vetro": (40, 48, 56), "alluminio": (176, 178, 180), "cuscino_blu": (40, 74, 140), "intonaco_liscio": (229, 227, 219),
    "lamiera": (140, 142, 144), "tronco_palma": (124, 104, 82), "corda": (200, 190, 168), "plastica_grigia": (120, 122, 124),
    "lampada": (250, 236, 200),
}
SW_ROUGH = {"zincato": (0.45, 0.8), "antracite": (0.5, 0.6), "nero": (0.45, 0.5), "alluminio": (0.35, 0.9),
            "lamiera": (0.5, 0.7), "bianco_vern": (0.45, 0.0), "vaso_bianco": (0.35, 0.0), "piano_bianco": (0.35, 0.0),
            "vetro": (0.06, 0.0), "lampada": (0.3, 0.0), "insegna": (0.4, 0.0), "insegna_blu": (0.35, 0.0)}


def _c(rgb):
    return np.asarray(rgb, np.float32) / 255.0


def _noise(h, w, sigma, seed):
    r = np.random.default_rng(seed).standard_normal((h, w)).astype(np.float32)
    r = tp.blur(r, sigma)
    r -= r.mean()
    return r / (r.std() + 1e-6)


class _Atl:
    def __init__(self, n=ATL, ppm=PPM):
        self.n, self.ppm = n, ppm
        self.D = np.ones((n, n, 3), np.float32) * _c((205, 203, 196))   # fondo neutro: niente aloni scuri nelle mip
        self.H = np.zeros((n, n), np.float32)
        self.R = np.full((n, n), 0.8, np.float32)
        self.M = np.zeros((n, n), np.float32)

    def sl(self, u0, v0, u1, v1):
        p = self.ppm
        return slice(int(round((8 - v1) * p)), int(round((8 - v0) * p))), slice(int(round(u0 * p)), int(round(u1 * p)))

    def rect(self, u0, v0, u1, v1, col=None, h=None, r=None, m=None, mul=None):
        s = self.sl(u0, v0, u1, v1)
        if col is not None:
            self.D[s] = _c(col)
        if mul is not None:
            self.D[s] *= mul
        if h is not None:
            self.H[s] = h
        if r is not None:
            self.R[s] = r
        if m is not None:
            self.M[s] = m


def _plaster_tile(S, seed):
    """Intonaco bianco periodico (S x S px = 4 x 4 m): ondulazioni di frattazzo, grana, macchie leggere, cavillature."""
    low = _noise(S, S, 60, seed) * 0.025 + _noise(S, S, 14, seed + 1) * 0.02
    grain = _noise(S, S, 0.8, seed + 2) * 0.035
    hgt = _noise(S, S, 3.0, seed + 3) * 0.25 + _noise(S, S, 0.9, seed + 4) * 0.12
    return low + grain, hgt


def make_textures():
    A = _Atl()
    p = PPM
    # --- intonaco (periodico su 4 m in u; in v quote 0-4 m) ---
    S = 4 * p
    var, hgt = _plaster_tile(S, 71)
    base = _c(COL["intonaco"])[None, None] * (1 + var)[..., None]
    z = (np.arange(S, dtype=np.float32)[::-1] + 0.5) / p           # quota per riga (riga 0 = 4 m)
    zz = np.broadcast_to(z[:, None], (S, S))
    # zoccolo dipinto grigio (0-0,32 m) con bordo superiore irregolare di 1 cm
    zt = 0.32 + 0.006 * _noise(1, S, 6, 9)[0][None, :]
    zoc = zz < zt
    zc = _c(COL["zoccolo"])[None, None] * (1 + 0.6 * var)[..., None]
    base = np.where(zoc[..., None], zc, base)
    # schizzi di sporco sopra lo zoccolo e colature sotto la copertina (verticali, periodiche in u)
    spl = np.clip((0.75 - zz) / 0.45, 0, 1) * (zz >= zt) * np.clip(0.5 + 0.5 * _noise(S, S, 5, 12), 0, 1) * 0.18
    col1d = np.clip(_noise(1, S, 2.5, 13)[0] - 0.6, 0, None)
    drip = np.clip((zz - 2.7) / 0.9, 0, 1) ** 2 * col1d[None, :] * 0.22 * np.clip(0.6 + 0.4 * _noise(S, S, 20, 14), 0, 1)
    dirt = _c((150, 140, 124))[None, None]
    k = (spl + drip)[..., None]
    base = base * (1 - k) + dirt * k
    s = A.sl(*R_PLASTER)
    A.D[s] = np.clip(base, 0, 1)
    A.H[s] = hgt
    A.R[s] = np.clip(0.88 + 0.03 * _noise(S, S, 4, 15) - 0.1 * zoc, 0.6, 0.95)
    # --- finestra a griglia (telaio bianco, 3 x 4 vetri, vetro scuro con riflesso del cielo) ---
    u0, v0, u1, v1 = R_GRID
    _glass(A, u0, v0, u1, v1, seed=3, frame=_c(COL["bianco_vern"]), fw=0.065, cols=3, rows=4, mull=0.03, interior="tenda")
    # --- porta-vetrata in alluminio antracite con zoccolo pieno e sopraluce ---
    u0, v0, u1, v1 = R_GLASS
    _glass(A, u0, v0, u1, v1, seed=5, frame=_c(COL["antracite"]), fw=0.06, cols=2, rows=1, mull=0.05, interior="sala",
           kick=0.30, transom=2.08, metal=True)
    # --- porta di servizio (lamiera bianca a doghe orizzontali, maniglia) ---
    u0, v0, u1, v1 = R_DOOR
    A.rect(u0, v0, u1, v1, col=(226, 226, 222), h=0.0, r=0.5)
    for k_ in range(10):
        vv = v0 + 0.15 + k_ * 0.2
        A.rect(u0 + 0.05, vv, u1 - 0.05, vv + 0.012, mul=0.82, h=-0.4)
    A.rect(u0, v0, u0 + 0.04, v1, col=COL["antracite"], h=0.5, r=0.5, m=0.6)
    A.rect(u1 - 0.04, v0, u1, v1, col=COL["antracite"], h=0.5, r=0.5, m=0.6)
    A.rect(u0, v1 - 0.04, u1, v1, col=COL["antracite"], h=0.5, r=0.5, m=0.6)
    A.rect(u1 - 0.17, v0 + 1.0, u1 - 0.08, v0 + 1.04, col=COL["alluminio"], h=1.5, r=0.3, m=0.9)
    # --- vano del bancone: parete interna con mensole e bottiglie, bancone in legno con frontale blu ---
    _bar(A, *R_BAR)
    # --- lavagna (scarabocchi di gesso illeggibili e un pesce stilizzato) ---
    _board(A, *R_BOARD)
    # --- tasselli ---
    rng = np.random.default_rng(31)
    for name, (a, b, c, d) in SW.items():
        col = COL.get(name, (200, 200, 200))
        s = A.sl(a, b, c, d)
        h_, w_ = A.D[s].shape[:2]
        n1 = _noise(h_, w_, 6, int(rng.integers(1e6))) * 0.04 + _noise(h_, w_, 1, int(rng.integers(1e6))) * 0.025
        A.D[s] = np.clip(_c(col)[None, None] * (1 + n1)[..., None], 0, 1)
        r_, m_ = SW_ROUGH.get(name, (0.85, 0.0))
        A.R[s] = r_ + 0.05 * n1 / 0.05
        A.M[s] = m_
        A.H[s] = n1 * 3
    for name in ("teak", "legno_chiaro", "cornice_lav", "tronco_palma"):      # venatura lungo u
        s = A.sl(*SW[name])
        h_, w_ = A.D[s].shape[:2]
        g = tp.blur(np.random.default_rng(len(name)).standard_normal((h_, w_)).astype(np.float32), (0.4, 18)) if False else None
        rr = np.random.default_rng(len(name)).standard_normal((h_, 1)).astype(np.float32)
        rr = np.repeat(tp.blur(np.repeat(rr, 8, 1), 1.2)[:, :1], w_, 1)
        rr += 0.3 * _noise(h_, w_, 3, len(name) + 1)
        A.D[s] *= (1 + 0.10 * np.clip(rr, -2.5, 2.5))[..., None]
        A.H[s] = rr * 0.4
    s = A.sl(*SW["griglia_ac"])                                          # griglia del ventilatore
    h_, w_ = A.D[s].shape[:2]
    yy, xx = np.mgrid[0:h_, 0:w_]
    rr = np.hypot(yy - h_ / 2, xx - w_ / 2) / (h_ / 2)
    ring = (np.sin(rr * 40) > 0.3) & (rr < 0.9)
    A.D[s] = np.where(ring[..., None], _c((70, 72, 74)), _c((200, 202, 200)))
    A.H[s] = np.where(ring, -0.8, 0.0)
    A.M[s] = 0.3
    s = A.sl(*SW["fibra_palma"])                                         # fibre incrociate del tronco
    h_, w_ = A.D[s].shape[:2]
    yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32)
    f = np.sin((xx + yy) * 0.35) * np.sin((xx - yy) * 0.35)
    A.D[s] *= (1 + 0.18 * f + 0.1 * _noise(h_, w_, 1.5, 77))[..., None]
    A.H[s] = f
    # --- salvataggio ---
    D = np.clip(A.D, 0, 1)
    N = tp.normal_dx(tp.blur(A.H, 0.8), 1.2)
    ao = np.clip(1 - 0.4 * np.maximum(tp.blur(A.H, 6) - A.H, 0), 0.5, 1)
    ORM = np.dstack([ao, np.clip(A.R, 0.04, 1), np.clip(A.M, 0, 1)])
    os.makedirs(TEXDIR, exist_ok=True)
    out = []
    for k_, a in (("D", D), ("N", N), ("ORM", ORM)):
        pth = f"{TEXDIR}/T_Molo_RistoranteC_{k_}.png"
        tp.save(a, pth)
        out.append(pth)
    out += make_tex_tenda()
    return out


def _glass(A, u0, v0, u1, v1, seed, frame, fw, cols, rows, mull, interior, kick=0.0, transom=None, metal=False):
    rng = np.random.default_rng(seed)
    s = A.sl(u0, v0, u1, v1)
    h_, w_ = A.D[s].shape[:2]
    yy = np.linspace(1, 0, h_)[:, None]
    xx = np.linspace(0, 1, w_)[None, :]
    sky = _c((150, 170, 190)) * 0.55
    dark = _c((26, 30, 36))
    t = np.clip(yy * 0.9 + 0.15 * np.sin(xx * 3 + 1.0), 0, 1)
    g = dark[None, None] * (1 - t[..., None] * 0.6) + sky[None, None] * (t[..., None] * 0.6)
    g = np.broadcast_to(g, (h_, w_, 3)).copy()
    if interior == "tenda":            # tende chiare dietro i vetri, in basso
        cur = np.clip((0.55 - yy) / 0.1, 0, 1) * (0.5 + 0.5 * np.sin(xx * 60) ** 2)
        g = g * (1 - 0.45 * cur[..., None]) + _c((196, 186, 166))[None, None] * 0.45 * cur[..., None]
    else:                              # sala: luci calde sfocate e sagome di tavoli
        for _ in range(7):
            cx, cy, rr = rng.uniform(0.1, 0.9), rng.uniform(0.25, 0.8), rng.uniform(0.04, 0.1)
            m = np.exp(-(((xx - cx) / rr) ** 2 + ((yy - cy) / (rr * 0.6)) ** 2))
            g += _c((120, 90, 50))[None, None] * 0.5 * m[..., None]
        g *= (1 - 0.35 * ((yy < 0.35) & (np.sin(xx * 25) > 0.2)))[..., None]
    A.D[s] = np.clip(g, 0, 1)
    A.R[s] = 0.06
    A.M[s] = 0.0
    A.H[s] = -0.3
    W, H = u1 - u0, v1 - v0
    fr = dict(col=None, h=0.6, r=0.45 if not metal else 0.4, m=0.0 if not metal else 0.7)

    def bar(a, b, c, d):
        A.rect(a, b, c, d, **fr)
        A.D[A.sl(a, b, c, d)] = frame
    bar(u0, v0, u0 + fw, v1); bar(u1 - fw, v0, u1, v1); bar(u0, v1 - fw, u1, v1); bar(u0, v0, u1, v0 + max(fw, kick))
    ginner = (u0 + fw, u1 - fw)
    for k in range(1, cols):
        uc = ginner[0] + (ginner[1] - ginner[0]) * k / cols
        bar(uc - mull / 2, v0, uc + mull / 2, v1)
    top = v1 - fw if transom is None else v0 + transom
    if transom is not None:
        bar(u0, top - 0.03, u1, top + 0.03)
    bot = v0 + max(fw, kick)
    for k in range(1, rows):
        vc = bot + (top - bot) * k / rows
        bar(u0, vc - mull / 2, u1, vc + mull / 2)
    if metal:                          # maniglioni verticali
        um = (u0 + u1) / 2
        A.rect(um - 0.12, v0 + 0.9, um - 0.1, v0 + 1.4, col=COL["alluminio"], h=1.2, r=0.3, m=0.9)
        A.rect(um + 0.1, v0 + 0.9, um + 0.12, v0 + 1.4, col=COL["alluminio"], h=1.2, r=0.3, m=0.9)


def _bar(A, u0, v0, u1, v1):
    rng = np.random.default_rng(17)
    A.rect(u0, v0, u1, v1, col=(196, 186, 168), h=0.0, r=0.8)                 # parete interna
    A.rect(u0, v0, u1, v0 + 1.05, col=COL["cuscino_blu"], h=0.2, r=0.6)        # frontale del bancone (blu)
    A.rect(u0, v0 + 1.05, u1, v0 + 1.12, col=COL["teak"], h=0.4, r=0.5)        # piano
    for k in range(int((u1 - u0) / 0.25)):                                     # doghe del frontale
        uu = u0 + 0.125 + k * 0.25
        A.rect(uu, v0 + 0.05, uu + 0.01, v0 + 1.0, mul=0.8)
    for sh in (1.5, 1.8, 2.08):                                               # mensole con bottiglie
        A.rect(u0 + 0.2, v0 + sh, u1 - 0.2, v0 + sh + 0.03, col=COL["teak"], h=0.5)
        uu = u0 + 0.25
        while uu < u1 - 0.3:
            w = rng.uniform(0.05, 0.08)
            hh = rng.uniform(0.16, 0.24)
            col = [(40, 90, 50), (120, 60, 30), (200, 190, 170), (60, 40, 30), (150, 30, 40)][int(rng.integers(5))]
            A.rect(uu, v0 + sh + 0.03, uu + w, v0 + sh + 0.03 + hh, col=col, r=0.2, h=0.3)
            uu += w + rng.uniform(0.02, 0.06)
    A.rect(u0, v1 - 0.08, u1, v1, col=COL["antracite"], h=0.3)


def _board(A, u0, v0, u1, v1):
    rng = np.random.default_rng(23)
    A.rect(u0, v0, u1, v1, col=COL["cornice_lav"], h=0.6, r=0.7)
    fw = 0.035
    s = A.sl(u0 + fw, v0 + fw, u1 - fw, v1 - fw)
    h_, w_ = A.D[s].shape[:2]
    board = np.ones((h_, w_, 3), np.float32) * _c((38, 44, 42))
    board *= (1 + 0.06 * _noise(h_, w_, 10, 3))[..., None]
    chalk = np.zeros((h_, w_), np.float32)
    y = 14
    while y < h_ - 14:                                  # righe di "scrittura" a tratti, illeggibili
        x = 10 + int(rng.integers(0, 12))
        while x < w_ - 18:
            L = int(rng.integers(6, 22))
            for t in range(L):
                yy = y + int(2.5 * math.sin(t * 1.3 + x))
                if 0 <= yy < h_ and x + t < w_:
                    chalk[yy, x + t] = 1
                    chalk[min(yy + 1, h_ - 1), x + t] = 0.8
            x += L + int(rng.integers(4, 9))
        y += int(rng.integers(13, 18))
    chalk = tp.blur(chalk, 0.6)
    board = board * (1 - chalk[..., None]) + _c((228, 228, 220))[None, None] * chalk[..., None]
    A.D[s] = np.clip(board, 0, 1)
    A.R[s] = 0.9


def make_tex_tenda(S=1024):
    """T_Molo_TendaRighe: 1 m in u (periodica), v 0-0,5 tela bianca, v 0,5-1 righe blu-bianche verticali (passo 1/6 m)."""
    u = (np.arange(S) + 0.5) / S
    v = 1 - (np.arange(S) + 0.5) / S
    U = np.broadcast_to(u[None, :], (S, S)); V = np.broadcast_to(v[:, None], (S, S))
    weave = 0.03 * np.sin(U * S * math.pi * 0.5) * np.sin(V * S * math.pi * 0.5) + 0.03 * _noise(S, S, 0.7, 1)
    dirt = 0.05 * _noise(S, S, 60, 2) + 0.03 * _noise(S, S, 12, 3)
    white = _c(COL["tela_bianca"])
    blue = _c((48, 82, 152))
    ph = np.mod(U * 6.0, 1.0)
    stripe = np.clip((np.minimum(ph, 0.42 - ph) if False else (ph < 0.42)).astype(np.float32), 0, 1)
    stripe = tp.blur(stripe, 0.7)
    col = np.where((V < 0.5)[..., None], white[None, None], white[None, None] * (1 - stripe[..., None]) + blue[None, None] * stripe[..., None])
    col = col * (1 + weave + dirt)[..., None]
    # sporco verso il bordo della tela bianca (gronda: v vicino a 0) e verso il basso della mantovana (v vicino a 0,5)
    edge = np.clip(1 - V / 0.08, 0, 1) * (V < 0.5) + np.clip(1 - (V - 0.5) / 0.06, 0, 1) * (V >= 0.5)
    col = col * (1 - 0.12 * edge[..., None])
    D = np.clip(col, 0, 1)
    H = weave * 10
    N = tp.normal_dx(H, 0.6)
    R = np.full((S, S), 0.82, np.float32) + 0.03 * stripe
    ORM = np.dstack([np.ones_like(R), R, np.zeros_like(R)])
    out = []
    for k, a in (("D", D), ("N", N), ("ORM", ORM)):
        p = f"{TEXDIR}/T_Molo_TendaRighe_{k}.png"
        tp.save(a, p)
        out.append(p)
    return out


# ---------------------------------------------------------------------------------------------------------------
# materiali
# ---------------------------------------------------------------------------------------------------------------
MATS = ["M_Molo_RistoranteC", "M_Molo_TendaRighe", "M_Albero_Latifoglia_Chioma", "M_Morin_PalmaA_Fronde"]


def build_materials():
    t = TEXDIR + "/"
    pk._pbr_material("M_Molo_RistoranteC", t + "T_Molo_RistoranteC_D.png", t + "T_Molo_RistoranteC_N.png",
                     t + "T_Molo_RistoranteC_ORM.png")
    pk._pbr_material("M_Molo_TendaRighe", t + "T_Molo_TendaRighe_D.png", t + "T_Molo_TendaRighe_N.png",
                     t + "T_Molo_TendaRighe_ORM.png")
    if "M_Albero_Latifoglia_Chioma" not in bpy.data.materials:
        pk._pbr_material("M_Albero_Latifoglia_Chioma", t + "T_Albero_Latifoglia_Chioma_D.png",
                         t + "T_Albero_Latifoglia_Chioma_N.png", t + "T_Albero_Latifoglia_Chioma_ORM.png", alpha=True)
    if "M_Morin_PalmaA_Fronde" not in bpy.data.materials:
        b = PROJ + "/blender/textures/T_Morin_PalmaA_Fronde"
        pk._pbr_material("M_Morin_PalmaA_Fronde", b + "_D.png", b + "_N.png", b + "_ORM.png", alpha=True)
    return MATS


# ---------------------------------------------------------------------------------------------------------------
# helper geometrici (winding esplicito, normali verso l'esterno; nessun ricalcolo globale)
# ---------------------------------------------------------------------------------------------------------------
class _B:
    """bmesh con layer UV "UVMap"; ogni faccia riceve le UV quando viene creata."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cards = []

    def face(self, pts, uvs, mi=0):
        f = self.bm.faces.new([self.bm.verts.new(p) for p in pts])
        f.material_index = mi
        for lp, uv in zip(f.loops, uvs):
            lp[self.uv].uv = uv
        return f

    def quad_reg(self, pts, reg, mi=0, s=(0, 1), t=(0, 1)):
        """Quad (4 punti: in basso a sx, in basso a dx, in alto a dx, in alto a sx) mappato nella regione reg (metri
        dell'atlante) fra le frazioni s (u) e t (v)."""
        u0, v0, u1, v1 = reg
        a, b = u0 + (u1 - u0) * s[0], u0 + (u1 - u0) * s[1]
        c, d = v0 + (v1 - v0) * t[0], v0 + (v1 - v0) * t[1]
        return self.face(pts, [(a / 8, c / 8), (b / 8, c / 8), (b / 8, d / 8), (a / 8, d / 8)], mi)

    def sw(self, pts, name, mi=0):
        u0, v0, u1, v1 = SW[name]
        m = 0.06
        reg = (u0 + m, v0 + m, u1 - m, v1 - m)
        if len(pts) == 4:
            return self.quad_reg(pts, reg, mi)
        cs = [(reg[0] + (reg[2] - reg[0]) * (0.5 + 0.5 * math.cos(2 * math.pi * k / len(pts))),
               reg[1] + (reg[3] - reg[1]) * (0.5 + 0.5 * math.sin(2 * math.pi * k / len(pts)))) for k in range(len(pts))]
        return self.face(pts, [(x / 8, y / 8) for x, y in cs], mi)

    def box(self, x0, x1, y0, y1, z0, z1, name, M=None, faces=("top", "bot", "xn", "xp", "yn", "yp")):
        P = {
            "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
            "bot": [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
            "yn": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
            "yp": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
            "xn": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
            "xp": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        }
        out = []
        for k in faces:
            pts = P[k] if M is None else [tuple(M @ Vector(p)) for p in P[k]]
            out.append(self.sw(pts, name) if isinstance(name, str) else self.quad_reg(pts, name))
        return out

    def cyl(self, prof, n, name, M=Matrix(), cap_top=True, cap_bot=False, phase=0.0, mi=0):
        """Rivoluzione attorno a Z (profilo (r, z) dal basso), facce verso l'esterno, UV nel tassello."""
        u0, v0, u1, v1 = SW[name] if isinstance(name, str) else name
        m = 0.04
        rings = []
        for r, z in prof:
            rings.append([tuple(M @ Vector((r * math.cos(phase + 2 * math.pi * k / n), r * math.sin(phase + 2 * math.pi * k / n), z)))
                          for k in range(n)])
        nz = len(prof)
        for i in range(nz - 1):
            for k in range(n):
                k1 = (k + 1) % n
                pts = [rings[i][k], rings[i][k1], rings[i + 1][k1], rings[i + 1][k]]
                if prof[i][0] < 1e-6:
                    pts = [rings[i][k], rings[i + 1][k1], rings[i + 1][k]]
                elif prof[i + 1][0] < 1e-6:
                    pts = [rings[i][k], rings[i][k1], rings[i + 1][k]]
                fu0 = u0 + m + (u1 - u0 - 2 * m) * k / n
                fu1 = u0 + m + (u1 - u0 - 2 * m) * (k + 1) / n
                fv0 = v0 + m + (v1 - v0 - 2 * m) * i / (nz - 1)
                fv1 = v0 + m + (v1 - v0 - 2 * m) * (i + 1) / (nz - 1)
                uv = [(fu0, fv0), (fu1, fv0), (fu1, fv1), (fu0, fv1)]
                if len(pts) == 3:
                    uv = [(fu0, fv0), (fu1, fv1), (fu0, fv1)] if prof[i][0] < 1e-6 else [(fu0, fv0), (fu1, fv0), (fu0, fv1)]
                self.face(pts, [(a / 8, b / 8) for a, b in uv], mi)
        if cap_top and prof[-1][0] > 1e-6:
            self.sw(rings[-1], name if isinstance(name, str) else "bianco_vern", mi)
        if cap_bot and prof[0][0] > 1e-6:
            self.sw(list(reversed(rings[0])), name if isinstance(name, str) else "bianco_vern", mi)

    def tube(self, a, b, r, n, name, cap=True):
        a, b = Vector(a), Vector(b)
        d = (b - a)
        L = d.length
        z = d.normalized()
        x = z.orthogonal().normalized()
        y = z.cross(x)
        M = Matrix((
            (x.x, y.x, z.x, a.x), (x.y, y.y, z.y, a.y), (x.z, y.z, z.z, a.z), (0, 0, 0, 1)))
        self.cyl([(r, 0.0), (r, L)], n, name, M=M, cap_top=cap, cap_bot=cap)

    def write(self, name, coll, mats=None, smooth=False):
        mats = mats or MATS
        bm = self.bm
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bm.normal_update()
        used = sorted({f.material_index for f in bm.faces})
        remap = {m: i for i, m in enumerate(used)}
        for f in bm.faces:
            f.material_index = remap[f.material_index]
        mats = [mats[m] for m in used]
        bm.faces.index_update()
        card_out = {f.index: o for f, o in self.cards if f.is_valid}
        o = bpy.data.objects.get(name)
        if o is None:
            o = bpy.data.objects.new(name, bpy.data.meshes.new(name))
            coll.objects.link(o)
        me = o.data
        me.materials.clear()
        bm.to_mesh(me)
        bm.free()
        for m in mats:
            me.materials.append(bpy.data.materials[m])
        for p in me.polygons:
            p.use_smooth = p.index in card_out
        me.update()
        if card_out:
            normals = []
            for p in me.polygons:
                for li in p.loop_indices:
                    normals.append(tuple(card_out[p.index]) if p.index in card_out else tuple(p.normal))
            me.normals_split_custom_set(normals)
        for l in [l for l in me.uv_layers if l.name != "UVMap"]:
            me.uv_layers.remove(l)
        if coll not in o.users_collection:
            coll.objects.link(o)
        o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1)
        return o


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


def _cards(B, rng, centers, lod, base_z, mi=2, size=(0.30, 0.55)):
    """Card di fogliame (atlante della chioma latifoglia, 4 quadranti) attorno a cespi (x, y, z_top, raggio, n)."""
    k = (1.0, 0.45, 0.16)[lod]
    for cx, cy, top, r, n in centers:
        n = max(3, int(round(n * k)))
        sz = 1.0 / max(k, 0.16) ** 0.4
        for _ in range(n):
            t = rng.uniform(0.15, 1.0) ** 0.7
            hz = base_z + (top - base_z) * t
            rr = r * (0.35 + 0.65 * math.sin(math.pi * min(t, 0.95) * 0.9 + 0.3)) * rng.uniform(0.6, 1.1)
            a = rng.uniform(0, 2 * math.pi)
            c = Vector((cx + rr * math.cos(a), cy + rr * math.sin(a), hz))
            out = Vector((math.cos(a), math.sin(a), 0.5 * t)).normalized()
            w = rng.uniform(*size) * sz
            h = min(rng.uniform(size[0] * 1.2, size[1] * 1.2) * sz, max(top - base_z, 0.3) * 0.9)
            e1 = Vector((-math.sin(a + rng.normal(0, 0.5)), math.cos(a + rng.normal(0, 0.5)), 0)) * w / 2
            tilt = rng.uniform(0.0, 0.5)
            e2 = (Vector((0, 0, 1)) * (1 - tilt) + out * tilt).normalized() * h / 2
            if c.z + e2.z > top:
                c.z = top - e2.z
            q = int(rng.integers(0, 4))
            u0, v0 = (q % 2) * 0.5, 0.5 - (q // 2) * 0.5
            f = B.face([c - e1 - e2, c + e1 - e2, c + e1 + e2, c - e1 + e2],
                       [(u0, v0), (u0 + 0.5, v0), (u0 + 0.5, v0 + 0.5), (u0, v0 + 0.5)], mi)
            B.cards.append((f, out))


# ---------------------------------------------------------------------------------------------------------------
# edificio C v2
# ---------------------------------------------------------------------------------------------------------------
# tratti di facciata per lato (dal primo vertice al secondo): (tipo, lunghezza); "p" = muro pieno (si allunga)
OPEN = {"grid": (1.2, 1.05, 2.45, R_GRID, "finestra"), "glass": (1.9, 0.0, 2.5, R_GLASS, "porta"),
        "door": (0.9, 0.0, 2.2, R_DOOR, "porta"), "bar": (3.0, 0.0, 2.4, R_BAR, "vano")}
WALLS = [
    [("p", 1.4), ("grid", 1.2), ("p", 2.0)],                                                        # sud (Y 24,8)
    [("p", 1.9), ("p", 0.6), ("glass", 1.9), ("p", 0.6), ("bar", 3.0), ("p", 0.6), ("glass", 1.9), ("p", 0.5), ("glass", 1.9),
     ("p", 0.55), ("p", 1.0), ("grid", 1.2), ("p", 1.25)],                                          # est (facciata sul molo)
    [("p", 1.3), ("grid", 1.2), ("p", 0.6), ("door", 0.9), ("p", 0.4)],                              # nord (Y 42,2)
    [("p", 4.0), ("grid", 1.2), ("p", 6.0), ("grid", 1.2), ("p", 5.0)],                              # ovest (retro)
]


def _fit(segs, L):
    fixed = sum(l for k, l in segs if k != "p")
    plain = sum(l for k, l in segs if k == "p")
    s = (L - fixed) / plain
    return [(k, l * s if k == "p" else l) for k, l in segs]


def _wall_quad(B, a, b, d, nrm, s0, s1, z0, z1, ustart, inset=0.0):
    """Muro piano fra le ascisse s0-s1 del lato (a, direzione d), quote z0-z1, UV intonaco periodico (4 m)."""
    if s1 - s0 < 1e-4 or z1 - z0 < 1e-4:
        return
    # spezza dove l'intonaco ricomincia (multipli di 4 m in u)
    cuts = [s0]
    u = ustart + s0
    k = math.floor(u / 4.0 + 1e-6) + 1
    while k * 4.0 - ustart < s1 - 1e-4:
        cuts.append(k * 4.0 - ustart)
        k += 1
    cuts.append(s1)
    for p0, p1 in zip(cuts[:-1], cuts[1:]):
        q0 = a + d * p0 - nrm * inset
        q1 = a + d * p1 - nrm * inset
        uu0 = (ustart + p0) % 4.0
        uu1 = uu0 + (p1 - p0)
        if uu1 > 4.0 + 1e-4:
            uu0, uu1 = 0.0, p1 - p0
        B.face([(q0.x, q0.y, z0), (q1.x, q1.y, z0), (q1.x, q1.y, z1), (q0.x, q0.y, z1)],
               [(uu0 / 8, (4 + z0) / 8), (uu1 / 8, (4 + z0) / 8), (uu1 / 8, (4 + z1) / 8), (uu0 / 8, (4 + z1) / 8)])


def _opening(B, a, d, nrm, s0, kind, ustart, lod):
    w, h0, h1, reg, typ = OPEN[kind]
    s1 = s0 + w
    rec = REC if kind != "bar" else 0.55
    # muro sotto e sopra
    _wall_quad(B, a, a, d, nrm, s0, s1, 0.0, h0, ustart)
    _wall_quad(B, a, a, d, nrm, s0, s1, h1, Z_WALL, ustart)
    P = lambda s, z, i=0.0: tuple(a + d * s - nrm * i) + (z,)
    P = (lambda s, z, i=0.0: (*(a + d * s - nrm * i).to_tuple(), z))
    if lod == 2:   # niente rientro: l'apertura e' dipinta sul piano della facciata
        B.quad_reg([P(s0, h0), P(s1, h0), P(s1, h1), P(s0, h1)], reg)
        return
    B.quad_reg([P(s0, h0, rec), P(s1, h0, rec), P(s1, h1, rec), P(s0, h1, rec)], reg)
    # spallette (intonaco liscio), orientate verso l'apertura
    B.sw([P(s0, h1, rec), P(s1, h1, rec), P(s1, h1), P(s0, h1)], "intonaco_liscio")           # architrave (giu')
    if h0 > 1e-3:
        B.sw([P(s0, h0), P(s1, h0), P(s1, h0, rec), P(s0, h0, rec)], "copertina")             # davanzale interno (su)
    B.sw([P(s0, h0), P(s0, h0, rec), P(s0, h1, rec), P(s0, h1)], "intonaco_liscio")           # sinistra
    B.sw([P(s1, h0, rec), P(s1, h0), P(s1, h1), P(s1, h1, rec)], "intonaco_liscio")           # destra
    if lod == 0 and typ == "finestra":     # davanzale sporgente in pietra
        x0, x1, o = s0 - 0.06, s1 + 0.06, 0.06
        B.box(0, 1, 0, 1, 0, 1, "copertina", M=_frame(a, d, nrm, x0, h0 - 0.05, x1 - x0, o, 0.05),
              faces=("top", "bot", "xn", "xp", "yp"))
    if lod == 0 and kind == "bar":         # bancone sporgente nel vano
        B.box(0, 1, 0, 1, 0, 1, "teak", M=_frame(a, d, nrm, s0 + 0.05, 1.05, w - 0.1, -rec + 0.05, 0.07, depth_in=True),
              faces=("top", "bot", "xn", "xp", "yp"))


def _frame(a, d, nrm, s, z, L, depth, H, depth_in=False):
    """Matrice che porta il box unitario (x: lungo il muro, y: verso l'esterno, z) in posizione: x in [s, s+L],
    y in [0, depth] fuori dal filo muro (depth negativo = dentro), z in [z, z+H]."""
    o = a + d * (s + L)
    if depth < 0:
        o = o + nrm * depth
        depth = -depth
    return Matrix(((-d.x * L, nrm.x * depth, 0, o.x), (-d.y * L, nrm.y * depth, 0, o.y), (0, 0, H, z), (0, 0, 0, 1)))


def _det(M):
    return M.to_3x3().determinant()


def build_C(coll, lod=0, name="SM_Molo_Edificio_C_v2"):
    B = _B()
    n = len(POLY_C)
    ustart = 0.0
    for i in range(n):
        a, b = Vector(POLY_C[i]), Vector(POLY_C[(i + 1) % n])
        L = (b - a).length
        d = (b - a) / L
        nrm = Vector((d.y, -d.x))
        s = 0.0
        for kind, l in _fit(WALLS[i], L):
            if kind == "p":
                _wall_quad(B, a, a, d, nrm, s, s + l, 0.0, Z_WALL, ustart)
            else:
                _opening(B, a, d, nrm, s, kind, ustart, lod)
            s += l
        ustart += L
    # parapetto: copertina (fronte, sopra, sotto lo sporto), faccia interna, tetto
    outer = _offset(POLY_C, COP_O)
    inner = _offset(POLY_C, -PARA_T)
    for i in range(n):
        j = (i + 1) % n
        w0, w1 = POLY_C[i], POLY_C[j]
        o0, o1 = outer[i], outer[j]
        i0, i1 = inner[i], inner[j]
        B.sw([(*o0, Z_WALL - 0.02), (*o1, Z_WALL - 0.02), (*o1, Z_TOP), (*o0, Z_TOP)], "copertina")       # fronte
        B.sw([(*w0, Z_WALL - 0.02), (*w1, Z_WALL - 0.02), (*o1, Z_WALL - 0.02), (*o0, Z_WALL - 0.02)], "copertina")  # sotto
        B.sw([(*o0, Z_TOP), (*o1, Z_TOP), (*i1, Z_TOP), (*i0, Z_TOP)], "copertina")                       # sopra
        B.sw([(*i1, Z_ROOF), (*i0, Z_ROOF), (*i0, Z_TOP), (*i1, Z_TOP)], "intonaco_liscio")               # interno
    _roof_fill(B, inner)
    rng = np.random.default_rng(42)
    # --- tetto: macchine del clima, canna fumaria della cucina, sfiati, fioriere con verde, verde che ricade ---
    ac = [(-10.6, 28.0, 0.0), (-10.7, 33.2, 0.0), (-11.0, 39.4, 90.0)]
    for x, y, yaw in (ac if lod < 2 else ac[:2]):
        M = Matrix.Translation((x, y, Z_ROOF)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
        B.box(-0.45, 0.45, -0.18, 0.18, 0.08, 0.72, "lamiera", M=M, faces=("top", "xn", "xp", "yp"))
        B.box(-0.45, 0.45, -0.18, 0.18, 0.08, 0.72, (SW["griglia_ac"][0] + 0.05, SW["griglia_ac"][1] + 0.05,
                                                     SW["griglia_ac"][2] - 0.05, SW["griglia_ac"][3] - 0.05), M=M, faces=("yn",))
        if lod == 0:
            for sx in (-0.38, 0.38):
                B.box(sx - 0.03, sx + 0.03, -0.15, 0.15, 0.0, 0.08, "zincato", M=M, faces=("top", "xn", "xp", "yn", "yp"))
    # canna fumaria (la quota massima dell'edificio: uguale in tutti i LOD)
    cx, cy = -11.3, 30.6
    B.box(cx - 0.22, cx + 0.22, cy - 0.22, cy + 0.22, Z_ROOF, 4.55, "zincato", faces=("xn", "xp", "yn", "yp"))
    B.box(cx - 0.32, cx + 0.32, cy - 0.32, cy + 0.32, 4.55, 4.75, "zincato")
    if lod < 2:
        B.box(cx - 0.25, cx + 0.25, cy - 0.25, cy + 0.25, 4.75, 4.85, "zincato", faces=("top", "xn", "xp", "yn", "yp"))
    if lod == 0:
        for x, y in ((-9.0, 26.2), (-9.2, 35.5)):
            B.cyl([(0.055, Z_ROOF), (0.055, Z_ROOF + 0.55), (0.09, Z_ROOF + 0.6), (0.0, Z_ROOF + 0.68)], 8, "zincato",
                  M=Matrix.Translation((x, y, 0)), cap_top=False)
    # fioriere sul tetto lungo il parapetto est e nord (F3: verde sopra il parapetto)
    pots = [(-8.55, 36.6, 1.6, 90), (-8.55, 39.6, 1.6, 90), (-9.8, 41.25, 1.8, 0), (-8.5, 27.0, 1.4, 90)]
    for x, y, L, yaw in (pots if lod < 2 else pots[:3]):
        M = Matrix.Translation((x, y, Z_ROOF)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
        B.box(-L / 2, L / 2, -0.25, 0.25, 0.0, 0.45, "vaso_bruno", M=M, faces=("top", "xn", "xp", "yn", "yp"))
        c = M @ Vector((0, 0, 0))
        dx, dy = (L / 2 - 0.3, 0) if yaw == 0 else (0, L / 2 - 0.3)
        cen = [(c.x - dx, c.y - dy, Z_ROOF + rng.uniform(1.15, 1.4), 0.38, 22), (c.x + dx, c.y + dy, Z_ROOF + rng.uniform(1.0, 1.3), 0.36, 20),
               (c.x, c.y, Z_ROOF + rng.uniform(1.2, 1.45), 0.34, 18)]
        _cards(B, rng, cen, lod, Z_ROOF + 0.42)
    # verde che ricade oltre il parapetto (angolo NE, sopra la finestra a griglia di F3)
    if lod < 2:
        for k in range(int(14 * (1.0 if lod == 0 else 0.5))):
            y = rng.uniform(37.8, 42.0)
            xw = x_wall(y)
            q = int(rng.integers(0, 4))
            u0, v0 = (q % 2) * 0.5, 0.5 - (q // 2) * 0.5
            w, h = rng.uniform(0.5, 0.8), rng.uniform(0.5, 0.9)
            top = Z_TOP + rng.uniform(0.15, 0.4)
            xo = xw + COP_O + rng.uniform(0.02, 0.09)
            f = B.face([(xo, y - w / 2, top - h), (xo, y + w / 2, top - h), (xo - 0.25, y + w / 2, top), (xo - 0.25, y - w / 2, top)],
                       [(u0, v0), (u0 + 0.5, v0), (u0 + 0.5, v0 + 0.5), (u0, v0 + 0.5)], 2)
            B.cards.append((f, Vector((1, 0, 0.4)).normalized()))
    # --- facciata: applique, pluviali, insegna ---
    lamps = [(39.3, 2.55), (41.4, 2.55)] if lod < 2 else []
    for y, z in lamps:
        xw = x_wall(y)
        B.box(xw, xw + 0.11, y - 0.12, y + 0.12, z - 0.07, z + 0.07, "nero", faces=("top", "bot", "xp", "yn", "yp"))
        if lod == 0:
            B.box(xw + 0.111, xw + 0.112, y - 0.09, y + 0.09, z - 0.015, z + 0.015, "lampada", faces=("xp",))
    for x, y in ((-7.42, 24.95), (-7.62, 42.05)):
        B.cyl([(0.05, 0.0), (0.05, Z_WALL - 0.05), (0.07, Z_WALL - 0.02)], 8 if lod < 2 else 4, "zincato",
              M=Matrix.Translation((x + 0.03, y, 0)), cap_top=True)
    _insegna(B, lod)
    o = B.write(name + _sfx(lod), coll)
    if lod == 0:
        pts = [(x, y, z) for x, y in _offset(POLY_C, COP_O) for z in (0.0, Z_TOP)]
        pk._ucx_hull(name, 0, pts, coll)
        pk._ucx(name, [(cx - 0.32, cx + 0.32, cy - 0.32, cy + 0.32, Z_TOP, 4.75)], coll, start=1)
        for i, (x, y, yaw) in enumerate(ac):
            hw, hd = (0.45, 0.18) if yaw == 0 else (0.18, 0.45)
            pk._ucx(name, [(x - hw, x + hw, y - hd, y + hd, Z_ROOF, Z_ROOF + 0.72)], coll, start=2 + i)
    return o


SIGN = "AL MUSCOLO STANCO"
SIGN_Y = 32.6
SIGN_Z = (3.10, 3.52)


def _insegna(B, lod):
    """Pannello bianco sopra la tenda con lettere blu in rilievo (testo inventato). LOD2: solo il pannello."""
    y0, y1 = SIGN_Y - 2.35, SIGN_Y + 2.35
    z0, z1 = SIGN_Z
    xa, xb = x_wall(y0), x_wall(y1)
    t = 0.04
    # pannello: fronte, sopra, sotto, fianchi (normale verso +X = fuori dalla facciata est)
    B.sw([(xa + t, y0, z0), (xb + t, y1, z0), (xb + t, y1, z1), (xa + t, y0, z1)], "insegna")
    B.sw([(xa, y0, z1), (xa + t, y0, z1), (xb + t, y1, z1), (xb, y1, z1)], "insegna")
    B.sw([(xa, y0, z0), (xb, y1, z0), (xb + t, y1, z0), (xa + t, y0, z0)], "insegna")
    B.sw([(xa, y0, z0), (xa + t, y0, z0), (xa + t, y0, z1), (xa, y0, z1)], "insegna")
    B.sw([(xb + t, y1, z0), (xb, y1, z0), (xb, y1, z1), (xb + t, y1, z1)], "insegna")
    if lod == 2:
        return
    # lettere: testo di Blender convertito in mesh, estruso 1,5 cm (LOD1: estrusione 0, solo la faccia)
    cu = bpy.data.curves.new("TMP_InsegnaC", "FONT")
    cu.body = SIGN
    cu.size = 0.30
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = 0.0075 if lod == 0 else 0.0
    cu.resolution_u = 2 if lod == 0 else 1
    cu.fill_mode = "BOTH"
    ob = bpy.data.objects.new("TMP_InsegnaC", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    # piano XY del testo -> facciata est: x testo -> +Y, y testo -> +Z, z testo -> +X
    xm = (xa + xb) / 2 + t + 0.0075 + 0.002
    M = Matrix(((0, 0, 1, xm), (1, 0, 0, SIGN_Y), (0, 1, 0, (z0 + z1) / 2), (0, 0, 0, 1)))
    u0, v0, u1, v1 = SW["insegna_blu"]
    vmap = {}
    for p in me.polygons:
        pts = [M @ me.vertices[vi].co for vi in p.vertices]
        if lod == 1 and p.normal.z < 0.5:      # LOD1: solo le facce verso chi guarda
            continue
        B.face([tuple(q) for q in pts], [((u0 + 0.1 + 0.3 * (q.y - y0) / (y1 - y0)) / 8, (v0 + 0.25) / 8) for q in pts])
    bpy.data.meshes.remove(me)


def _offset(poly, d):
    """Offset del poligono antiorario (d > 0 verso l'esterno), spigoli vivi."""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e0 = (p1 - p0).normalized(); e1 = (p2 - p1).normalized()
        n0 = Vector((e0.y, -e0.x)); n1 = Vector((e1.y, -e1.x))
        m = (n0 + n1).normalized()
        k = d / max(m.dot(n0), 0.3)
        q = p1 + m * k
        out.append((q.x, q.y))
    return out


def _roof_fill(B, inner):
    xs = [p[0] for p in inner]; ys = [p[1] for p in inner]
    x0, y0 = min(xs), min(ys)
    pts = [(x, y, Z_ROOF) for x, y in inner]
    u0, v0, u1, v1 = SW["tetto"]
    f = B.face(pts, [((u0 + 0.05 + 0.4 * (x - x0) / (max(xs) - x0)) / 8, (v0 + 0.05 + 0.4 * (y - y0) / (max(ys) - y0)) / 8)
                     for x, y, _ in pts])
    return f


# ---------------------------------------------------------------------------------------------------------------
# dehors a righe
# ---------------------------------------------------------------------------------------------------------------
def _canvas_uv(s, v):
    """UV della tela (texture T_Molo_TendaRighe, 1 m in u): s = metri lungo Y, v in [0, 1] della texture."""
    return (s, v)


def _bay_posts():
    return [AW_Y0 + (AW_Y1 - AW_Y0) * k / N_BAYS for k in range(N_BAYS + 1)]


def build_dehors(coll, lod=0, name="SM_Molo_DehorsRighe"):
    B = _B()
    ys = _bay_posts()
    xf = lambda y: x_wall(y) + AW_D               # filo esterno (trave frontale)
    PW = 0.045                                    # mezzo lato dei montanti (9 cm)
    # --- montanti, trave frontale, correnti, mensola al muro (antracite) ---
    for k, y in enumerate(ys):
        x = xf(y) - PW
        B.box(x - PW, x + PW, y - PW, y + PW, 0.0, Z_EAVE - 0.02, "antracite", faces=("top", "xn", "xp", "yn", "yp"))
        if lod < 2:
            B.box(x - 0.11, x + 0.11, y - 0.11, y + 0.11, 0.0, 0.012, "antracite", faces=("top", "xn", "xp", "yn", "yp"))
            # corrente inclinato dal muro alla trave
            xw = x_wall(y) + 0.02
            p0, p1 = Vector((xw, y, Z_ATT - 0.13)), Vector((x, y, Z_EAVE - 0.09))
            _beam(B, p0, p1, 0.03, 0.05, "antracite")
    # trave frontale (box lungo la gronda)
    _beam(B, Vector((xf(ys[0]) - PW, ys[0] - 0.08, Z_EAVE - 0.07)), Vector((xf(ys[-1]) - PW, ys[-1] + 0.08, Z_EAVE - 0.07)),
          0.05, 0.065, "antracite", horiz=True)
    # mensola a muro
    _beam(B, Vector((x_wall(ys[0]) + 0.04, ys[0] - 0.05, Z_ATT - 0.03)), Vector((x_wall(ys[-1]) + 0.04, ys[-1] + 0.05, Z_ATT - 0.03)),
          0.04, 0.05, "antracite", horiz=True)
    # --- tela: sopra e sotto (due facce), mantovane frontale e laterali (fuori e dentro) ---
    nseg = N_BAYS * (2 if lod == 0 else 1)
    yv = [ys[0] - 0.1 + (ys[-1] - ys[0] + 0.2) * k / nseg for k in range(nseg + 1)]
    sag = 0.035 if lod < 2 else 0.0
    for k in range(nseg):
        ya, yb = yv[k], yv[k + 1]
        # profilo della falda: muro (Z_ATT) -> gronda (Z_EAVE), leggera pancia a meta'
        prof = [(0.0, Z_ATT + 0.01), (0.5, (Z_ATT + Z_EAVE) / 2 - sag), (1.0, Z_EAVE + 0.01)] if lod < 2 else \
            [(0.0, Z_ATT + 0.01), (1.0, Z_EAVE + 0.01)]
        for (t0, z0), (t1, z1) in zip(prof[:-1], prof[1:]):
            xa0, xa1 = x_wall(ya) + 0.02 + (AW_D - 0.02) * t0, x_wall(ya) + 0.02 + (AW_D - 0.02) * t1
            xb0, xb1 = x_wall(yb) + 0.02 + (AW_D - 0.02) * t0, x_wall(yb) + 0.02 + (AW_D - 0.02) * t1
            sa, sb = ya - ys[0], yb - ys[0]
            va0, va1 = 0.47 - 0.44 * t0, 0.47 - 0.44 * t1
            # sopra (normale in su-fuori): ordine muro_a, gronda_a, gronda_b, muro_b
            B.face([(xa0, ya, z0), (xa1, ya, z1), (xb1, yb, z1), (xb0, yb, z0)],
                   [(sa, va0), (sa, va1), (sb, va1), (sb, va0)], mi=1)
            # sotto (1 cm piu' in basso, normale in giu')
            B.face([(xa0, ya, z0 - 0.012), (xa1, ya, z1 - 0.012), (xb1, yb, z1 - 0.012), (xb0, yb, z0 - 0.012)][::-1],
                   [(sa, va0), (sa, va1), (sb, va1), (sb, va0)][::-1], mi=1)
    # mantovana frontale: prima campata a nord bianca (F3), le altre a righe
    yb_white = ys[-2]
    for k in range(nseg):
        ya, yb = yv[k], yv[k + 1]
        xa, xb = x_wall(ya) + AW_D + 0.012, x_wall(yb) + AW_D + 0.012
        white = ya >= yb_white - 1e-3
        v0, v1 = (0.05, 0.30) if white else (0.53, 0.97)
        za, zb = Z_EAVE + 0.01, Z_EAVE + 0.01 - VAL_H
        sa, sb = ya - ys[0], yb - ys[0]
        B.face([(xa, ya, zb), (xb, yb, zb), (xb, yb, za), (xa, ya, za)], [(sa, v0), (sb, v0), (sb, v1), (sa, v1)], mi=1)  # fuori (+X)
        B.face([(xa - 0.01, ya, zb), (xb - 0.01, yb, zb), (xb - 0.01, yb, za), (xa - 0.01, ya, za)][::-1],
               [(sa, v0), (sb, v0), (sb, v1), (sa, v1)][::-1], mi=1)                                                                       # dentro
    for y, sgn in ((yv[0], -1), (yv[-1], 1)):     # mantovane laterali (triangolo della falda + striscia)
        xw, xe = x_wall(y) + 0.02, x_wall(y) + AW_D + 0.012
        top = [(xw, y, Z_ATT + 0.01), (xe, y, Z_EAVE + 0.01), (xe, y, Z_EAVE + 0.01 - VAL_H), (xw, y, Z_ATT + 0.01 - VAL_H)]
        uv = [(0.0, 0.97), (AW_D, 0.97), (AW_D, 0.53), (0.0, 0.53)]
        if sgn < 0:   # lato sud: fuori verso -Y, dentro verso +Y
            B.face(top[::-1], uv[::-1], mi=1)
            B.face([(p[0], p[1] + 0.01, p[2]) for p in top], uv, mi=1)
        else:
            B.face(top, uv, mi=1)
            B.face([(p[0], p[1] - 0.01, p[2]) for p in top][::-1], uv[::-1], mi=1)
    # --- tende laterali bianche raccolte ai montanti (fuori dai montanti verso il molo) ---
    nside = (8, 5, 4)[lod]
    for k, y in enumerate(ys):
        if lod == 2 and k % 2:
            continue
        x = xf(y) - PW
        prof = [(0.17, 0.02), (0.13, 0.55), (0.07, 1.15), (0.11, 1.45), (0.09, 2.0), (0.06, Z_EAVE - 0.05)]
        if lod > 0:
            prof = [(0.15, 0.02), (0.07, 1.15), (0.08, Z_EAVE - 0.05)]
        M = Matrix.Translation((x + 0.03, y + (0.13 if k < len(ys) - 1 else -0.13), 0))
        B.cyl(prof, nside, (0.1, 0.05 * 8, 0.9, 0.3 * 8), M=M, cap_top=False, mi=1)
        if lod == 0:   # laccio
            B.cyl([(0.075, 1.12), (0.075, 1.18)], 8, "corda", M=M, cap_top=False)
    # --- panca a muro con cuscini blu (sotto la tenda, fra le due porte-vetrate) ---
    if False:     # panca a muro: tolta (davanti alle porte-vetrate)
        for y0, y1 in ((26.9, 29.7), (32.6, 35.2)):
            xw = x_wall((y0 + y1) / 2)
            B.box(xw, xw + 0.48, y0, y1, 0.0, 0.40, "teak", faces=("top", "xn", "xp", "yn", "yp"))
            B.box(xw + 0.02, xw + 0.48, y0 + 0.02, y1 - 0.02, 0.40, 0.47, "cuscino_blu", faces=("top", "xp", "yn", "yp"))
            B.box(xw, xw + 0.09, y0 + 0.02, y1 - 0.02, 0.47, 0.92, "cuscino_blu", faces=("top", "xn", "xp", "yn", "yp"))
    o = B.write(name + _sfx(lod), coll)
    if lod == 0:
        boxes = []
        for y in ys:
            x = xf(y) - PW
            boxes.append((x - 0.2, x + 0.2, y - 0.2, y + 0.2, 0.0, Z_EAVE))
        pk._ucx(name, boxes, coll)
        roof = []
        for y in (ys[0] - 0.1, ys[-1] + 0.1):
            for t, z in ((0.0, Z_ATT + 0.02), (1.0, Z_EAVE + 0.02)):
                x = x_wall(y) + AW_D * t
                roof += [(x, y, z), (x, y, z - 0.12 - (VAL_H if t == 1.0 else 0.0))]
        pk._ucx_hull(name, len(boxes), roof, coll)
    return o


def _beam(B, p0, p1, hw, hh, name, horiz=False):
    """Trave a sezione rettangolare (mezza larghezza hw, mezza altezza hh) da p0 a p1."""
    d = (p1 - p0)
    L = d.length
    x = d.normalized()
    z = Vector((0, 0, 1))
    y = z.cross(x).normalized()
    z = x.cross(y)
    M = Matrix(((x.x, y.x, z.x, p0.x), (x.y, y.y, z.y, p0.y), (x.z, y.z, z.z, p0.z), (0, 0, 0, 1)))
    B.box(0, L, -hw, hw, -hh, hh, name, M=M)


# ---------------------------------------------------------------------------------------------------------------
# arredi del dehors
# ---------------------------------------------------------------------------------------------------------------
SEATS = ["seduta_blu", "seduta_rossa", "seduta_gialla", "seduta_verde"]


def _chair(B, M, seat, lod):
    """Sedia in legno chiaro con seduta colorata. Chi siede guarda verso -Y locale; schienale a +Y.
    LOD1: niente traversi; LOD2: un blocco (gambe + telaio) con la seduta sopra e lo schienale come lastra."""
    if lod == 2:
        B.box(-0.215, 0.215, -0.215, 0.215, 0.0, 0.45, "legno_chiaro", M=M, faces=("xn", "xp", "yn", "yp"))
        B.box(-0.215, 0.215, -0.215, 0.215, 0.0, 0.47, seat, M=M, faces=("top",))
        B.box(-0.215, 0.215, 0.17, 0.215, 0.47, 0.86, "legno_chiaro", M=M, faces=("top", "yn", "yp"))
        return
    lw = 0.022
    leg_f = ("top", "xn", "xp", "yn", "yp") if lod == 0 else ("xn", "xp", "yn", "yp")
    for sx in (-0.19, 0.19):
        for sy in (-0.19, 0.19):
            hgt = 0.44 if sy < 0 else 0.86
            B.box(sx - lw, sx + lw, sy - lw, sy + lw, 0.0, hgt, "legno_chiaro", M=M, faces=leg_f)
    B.box(-0.215, 0.215, -0.215, 0.215, 0.42, 0.45, "legno_chiaro", M=M,
          faces=("top", "bot", "xn", "xp", "yn", "yp") if lod == 0 else ("bot", "xn", "xp", "yn", "yp"))
    B.box(-0.205, 0.205, -0.205, 0.195, 0.45, 0.49, seat, M=M, faces=("top", "xn", "xp", "yn", "yp"))
    B.box(-0.19, 0.19, 0.18, 0.21, 0.62, 0.84, "legno_chiaro", M=M,
          faces=("top", "bot", "xn", "xp", "yn", "yp") if lod == 0 else ("top", "yn", "yp"))
    if lod == 0:
        for z in (0.15,):
            B.box(-0.19, 0.19, -0.19 - 0.01, -0.19 + 0.01, z, z + 0.025, "legno_chiaro", M=M, faces=("top", "bot", "yn", "yp"))
            B.box(-0.19, 0.19, 0.19 - 0.01, 0.19 + 0.01, z, z + 0.025, "legno_chiaro", M=M, faces=("top", "bot", "yn", "yp"))



def build_set(coll, lod=0, name="SM_Molo_SetLegno"):
    """Tavolo in legno 1,2 x 0,7 m (lungo X locale) con 4 sedie in legno a sedute colorate, leggermente fuori squadra."""
    B = _B()
    B.box(-0.6, 0.6, -0.35, 0.35, 0.715, 0.75, "teak")
    lw = 0.03
    for sx in (-0.54, 0.54):
        for sy in (-0.29, 0.29):
            B.box(sx - lw, sx + lw, sy - lw, sy + lw, 0.0, 0.715, "teak", faces=("xn", "xp", "yn", "yp") if lod < 2 else ("xn", "yn"))
    if lod < 2:
        B.box(-0.54, 0.54, -0.31, -0.29, 0.62, 0.70, "teak", faces=("bot", "yn", "yp"))
        B.box(-0.54, 0.54, 0.29, 0.31, 0.62, 0.70, "teak", faces=("bot", "yn", "yp"))
    chairs = [(-0.3, -0.62, 0.0, 4.0, 0), (0.3, -0.62, 0.0, -5.0, 1), (-0.3, 0.62, 180.0, 6.0, 2), (0.32, 0.64, 180.0, -3.0, 3)]
    for x, y, yaw, jit, si in chairs:
        M = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(yaw + 180 + jit), 4, "Z")
        _chair(B, M, SEATS[si], lod)
    o = B.write(name + _sfx(lod), coll)
    if lod == 0:
        pk._ucx(name, [(-0.62, 0.62, -0.9, 0.9, 0.0, 0.76)], coll)
    return o


OMB_R, OMB_ZE, OMB_ZA = 1.5, 2.30, 2.78


def build_ombrellone(coll, lod=0, name="SM_Molo_OmbrelloneLegno"):
    """Ombrellone da mercato bianco, ottagonale, diametro 3 m, palo e stecche in legno (F3), base in ghisa a disco."""
    B = _B()
    n = 8
    rib = [Vector((OMB_R * math.cos(math.pi / 8 + 2 * math.pi * k / n), OMB_R * math.sin(math.pi / 8 + 2 * math.pi * k / n), OMB_ZE))
           for k in range(n)]
    apex = Vector((0, 0, OMB_ZA))
    mids = (2 if lod == 0 else 1) if lod < 2 else 1
    for k in range(n):
        a, b = rib[k], rib[(k + 1) % n]
        # spicchio con leggera concavita' (punto a meta' del bordo piu' basso di 4 cm)
        m = (a + b) / 2
        m.z -= 0.04 if lod < 2 else 0.0
        for top in (True, False):
            dz = 0.0 if top else -0.012
            pts = [apex + Vector((0, 0, dz)), a + Vector((0, 0, dz)), m + Vector((0, 0, dz)), b + Vector((0, 0, dz))]
            uv = [(0.5, 0.45), (0.0, 0.05), (0.5, 0.05), (1.0, 0.05)]
            if top:
                B.face([pts[0], pts[1], pts[2]], [uv[0], uv[1], uv[2]], mi=1)
                B.face([pts[0], pts[2], pts[3]], [uv[0], uv[2], uv[3]], mi=1)
            else:
                B.face([pts[0], pts[2], pts[1]], [uv[0], uv[2], uv[1]], mi=1)
                B.face([pts[0], pts[3], pts[2]], [uv[0], uv[3], uv[2]], mi=1)
        if lod < 2:   # mantovana corta
            for (p, q, inn) in ((a, m, 0), (m, b, 0)):
                B.face([p - Vector((0, 0, 0.16)), q - Vector((0, 0, 0.16)), q, p], [(0, 0.05), (0.5, 0.05), (0.5, 0.2), (0, 0.2)], mi=1)
                if lod > 0:
                    continue
                pi_, qi = p * 0.995, q * 0.995
                pi_.z, qi.z = p.z, q.z
                B.face([qi - Vector((0, 0, 0.16)), pi_ - Vector((0, 0, 0.16)), pi_, qi], [(0.5, 0.05), (0, 0.05), (0, 0.2), (0.5, 0.2)], mi=1)
    # palo e cappello
    ns = (8, 6, 4)[lod]
    B.cyl([(0.024, 0.06), (0.024, OMB_ZA + 0.02)], ns, "teak", cap_top=False)
    B.cyl([(0.12, OMB_ZA - 0.01), (0.12, OMB_ZA + 0.03), (0.0, OMB_ZA + 0.14)], ns, (0.0, 0.05 * 8, 0.9, 0.3 * 8), mi=1, cap_top=False)
    B.cyl([(0.24, 0.0), (0.24, 0.025), (0.06, 0.06), (0.03, 0.08)], max(ns, 8) if lod < 2 else 6, "nero", cap_top=True)
    if lod < 2:
        for k in range(n):   # stecche
            r = rib[k]
            B.tube(Vector((0, 0, OMB_ZA - 0.05)), Vector((r.x * 0.98, r.y * 0.98, OMB_ZE - 0.03)), 0.011, 4, "teak", cap=False)
            if lod == 0:
                B.tube(Vector((0, 0, 1.95)), Vector((r.x * 0.5, r.y * 0.5, (OMB_ZA + OMB_ZE) / 2 - 0.08)), 0.008, 4, "teak", cap=False)
        B.cyl([(0.045, 1.9), (0.045, 2.0)], ns, "teak")
    o = B.write(name + _sfx(lod), coll)
    if lod == 0:
        pk._ucx(name, [(-0.24, 0.24, -0.24, 0.24, 0.0, 0.08), (-0.03, 0.03, -0.03, 0.03, 0.08, OMB_ZA)], coll)
        pk._ucx_hull(name, 2, [tuple(r) for r in rib] + [tuple(r - Vector((0, 0, 0.16))) for r in rib] + [(0, 0, OMB_ZA + 0.14)], coll)
    return o


def build_cavalletto(coll, lod=0, name="SM_Molo_CavallettoMenu"):
    """Lavagna a cavalletto (A) 0,6 x 0,9 m per faccia, telaio in legno; scritte di gesso illeggibili."""
    B = _B()
    H, W, open_ = 1.05, 0.62, 0.20
    ang = math.atan2(open_, H)
    for side in (-1, 1):
        R = Matrix.Translation((0, side * open_, 0)) @ Matrix.Rotation(side * ang, 4, "X")
        # pannello: faccia esterna con la lavagna (verso fuori), retro in legno 1,5 cm piu' dentro
        pts = [R @ Vector((-W / 2, 0.0, 0.12)), R @ Vector((W / 2, 0.0, 0.12)), R @ Vector((W / 2, 0.0, H)), R @ Vector((-W / 2, 0.0, H))]
        back = [p + R.to_3x3() @ Vector((0, -side * 0.015, 0)) for p in pts]
        if side < 0:      # lavagna verso -Y (ordine x, z), retro verso +Y
            B.quad_reg([tuple(p) for p in pts], R_BOARD)
            B.sw([tuple(p) for p in (back[1], back[0], back[3], back[2])], "cornice_lav")
        else:             # lavagna verso +Y, retro verso -Y
            B.quad_reg([tuple(p) for p in (pts[1], pts[0], pts[3], pts[2])], R_BOARD)
            B.sw([tuple(p) for p in back], "cornice_lav")
        if True:      # gambe del telaio (anche nel LOD2: stessa sagoma)
            for sx in (-W / 2 - 0.02, W / 2 + 0.02):
                M = R @ Matrix.Translation((sx, -side * 0.0075, 0))
                B.box(-0.02, 0.02, -0.015, 0.015, 0.0, H + 0.03, "cornice_lav", M=M, faces=("top", "xn", "xp", "yn", "yp"))
    if True:
        B.box(-0.05, 0.05, -open_, open_, H, H + 0.04, "cornice_lav", faces=("top", "xn", "xp", "yn", "yp"))
        B.box(-W / 2 - 0.02, W / 2 + 0.02, -0.035, 0.035, H - 0.02, H + 0.035, "cornice_lav", faces=("top", "xn", "xp", "yn", "yp"))
    o = B.write(name + _sfx(lod), coll)
    if lod == 0:
        pk._ucx_hull(name, 0, [(sx * (W / 2 + 0.04), sy * open_ * 1.08, 0.0) for sx in (-1, 1) for sy in (-1, 1)] +
                     [(sx * (W / 2 + 0.04), sy * 0.03, H + 0.04) for sx in (-1, 1) for sy in (-1, 1)], coll)
    return o


def build_palma_vaso(coll, lod=0, name="SM_Molo_PalmaVaso"):
    """Vaso tondo bianco (diam. 1,1 m, h 0,9) con palma giovane (Phoenix): tronco corto a squame e ~16 fronde su card."""
    B = _B()
    ns = (20, 12, 8)[lod]
    B.cyl([(0.42, 0.0), (0.55, 0.86), (0.57, 0.88), (0.57, 0.92)], ns, "vaso_bianco", cap_top=False)
    # bordo interno e terra
    rin = [(0.53 * math.cos(2 * math.pi * k / ns), 0.53 * math.sin(2 * math.pi * k / ns)) for k in range(ns)]
    rout = [(0.57 * math.cos(2 * math.pi * k / ns), 0.57 * math.sin(2 * math.pi * k / ns)) for k in range(ns)]
    for k in range(ns):
        k1 = (k + 1) % ns
        B.sw([(*rout[k], 0.92), (*rout[k1], 0.92), (*rin[k1], 0.92), (*rin[k], 0.92)], "vaso_bianco")
        B.sw([(*rin[k], 0.92), (*rin[k1], 0.92), (*rin[k1], 0.84), (*rin[k], 0.84)], "vaso_bianco")
    B.sw([(*p, 0.84) for p in rin], "terra")
    # tronco corto (squame: fibra_palma)
    th = 1.25
    nt = (10, 7, 5)[lod]
    B.cyl([(0.15, 0.84), (0.16, 1.0), (0.135, th * 0.6 + 0.84), (0.15, th + 0.84), (0.08, th + 1.0)], nt, "fibra_palma", cap_top=False,
          phase=0.2)
    # fronde: card arcuate a 2-3 segmenti, atlante delle fronde (3 colonne)
    rng = np.random.default_rng(5)
    nf = 18
    segs = (3, 2, 1)[lod]
    top = Vector((0, 0, th + 0.95))
    for i in range(nf):
        az = 2 * math.pi * i / nf + rng.normal(0, 0.12)
        el = math.radians(rng.uniform(25, 60) if i % 3 else rng.uniform(55, 75))
        L = rng.uniform(1.5, 2.0)
        col = int(rng.integers(0, 3)) if i % 5 else 2 * (rng.random() < 0.3)
        w = rng.uniform(0.55, 0.7)
        dirv = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        side = Vector((-math.sin(az), math.cos(az), 0))
        pts = []
        for s in range(segs + 1):
            t = s / segs
            p = top + dirv * L * t
            p.z -= 0.55 * L * t * t * (1.0 - 0.6 * math.sin(el))      # la fronda ricade
            pts.append(p)
        u0, u1 = col / 3 + 0.02, (col + 1) / 3 - 0.02
        for s in range(segs):
            p0, p1 = pts[s], pts[s + 1]
            ww0 = w * (0.45 + 0.55 * math.sin(math.pi * (0.15 + 0.85 * s / segs)))
            ww1 = w * (0.45 + 0.55 * math.sin(math.pi * (0.15 + 0.85 * (s + 1) / segs))) if s + 1 < segs else w * 0.25
            tw = side.copy()
            tw.z = 0.25 * (1 if i % 2 else -1)
            tw.normalize()
            v0, v1 = 0.02 + 0.96 * s / segs, 0.02 + 0.96 * (s + 1) / segs
            f = B.face([p0 - tw * ww0 / 2, p0 + tw * ww0 / 2, p1 + tw * ww1 / 2, p1 - tw * ww1 / 2],
                       [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], mi=3)
            nn = (p1 - p0).cross(tw).normalized()
            if nn.z < 0:
                nn = -nn
            B.cards.append((f, (nn + Vector((0, 0, 0.6))).normalized()))
    o = B.write(name + _sfx(lod), coll)
    if lod == 0:
        pk._ucx_hull(name, 0, [(0.57 * math.cos(2 * math.pi * k / 8), 0.57 * math.sin(2 * math.pi * k / 8), z)
                               for k in range(8) for z in (0.0, 0.92)], coll)
    return o


# ---------------------------------------------------------------------------------------------------------------
# build, posa, controlli, export
# ---------------------------------------------------------------------------------------------------------------
ASSETS = {"SM_Molo_Edificio_C_v2": build_C, "SM_Molo_DehorsRighe": build_dehors, "SM_Molo_SetLegno": build_set,
          "SM_Molo_OmbrelloneLegno": build_ombrellone, "SM_Molo_CavallettoMenu": build_cavalletto,
          "SM_Molo_PalmaVaso": build_palma_vaso}


def build_all():
    coll = pk._coll(KIT)
    out = []
    for nm, f in ASSETS.items():
        for lod in range(3):
            out.append(f(coll, lod=lod, name=nm))
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    return [(o.name, pk.tri_count(o), tuple(round(d, 2) for d in o.dimensions)) for o in out]


def layout():
    """Posizioni (coordinate Blender/progetto, metri): (asset, nome, x, y, z, yaw_gradi)."""
    rows = [("SM_Molo_Edificio_C_v2", "Molo_Edificio_C_v2", 0.0, 0.0, 0.0, 0.0),
            ("SM_Molo_DehorsRighe", "Molo_DehorsRighe", 0.0, 0.0, 0.0, 0.0)]
    z = Z0
    # tavoli sotto la tenda (lungo Y, fra panca e montanti) e fila esterna verso il molo (F3)
    k = 0
    for y in (31.5, 37.0):
        rows.append(("SM_Molo_SetLegno", f"SetLegno_{k:02d}", round(x_wall(y) + 1.55, 2), y, z, 90.0)); k += 1
    for i, y in enumerate((36.6, 33.6, 30.6, 27.6, 24.6, 21.6, 18.6, 15.6)):
        rows.append(("SM_Molo_SetLegno", f"SetLegno_{k:02d}", -3.15 + (0.04 if i % 2 else -0.03), y, z, 90.0 + (2.0 if i % 2 else -1.5))); k += 1
    for i, y in enumerate((35.1, 29.1, 23.1, 17.1)):
        rows.append(("SM_Molo_OmbrelloneLegno", f"OmbrelloneLegno_{i:02d}", -3.15, y, z, 22.5 * (i % 2)))
    rows.append(("SM_Molo_CavallettoMenu", "CavallettoMenu_00", -2.55, 38.9, z, 35.0))
    # fioriere del chiosco davanti alla parte in muratura (F3: fila di vasi con arbusti) e ai capi del dehors
    fio = [("SM_Morin_Fioriera", -6.3, 39.4, 0.0), ("SM_Morin_FiorieraB", -6.3, 40.75, 90.0), ("SM_Morin_FiorieraC", -6.3, 42.1, 180.0),
           ("SM_Morin_FiorieraB", -4.0, 25.9, 0.0), ("SM_Morin_Fioriera", -4.0, 13.9, 270.0)]
    for i, (a, x, y, yaw) in enumerate(fio):
        rows.append((a, f"FiorieraC_{i:02d}", x, y, z, yaw))
    # palme in vaso: ai capi del dehors e fila lungo il ciglio est del molo (scheda §2.4, X 7-9, Y 30-75 [S])
    palme = [(-3.4, 41.0), (-3.4, 12.6)] + [(8.0, y) for y in (31.0, 40.0, 49.0, 58.0, 67.0)]
    for i, (x, y) in enumerate(palme):
        rows.append(("SM_Molo_PalmaVaso", f"PalmaVaso_{i:02d}", x, y, z, (i * 47.0) % 360))
    # palme alte dietro i tavoli verso il ponte (F3: 3-4 Phoenix oltre lo spigolo sud di C) [S]: riuso SM_Morin_PalmaA
    for i, (x, y, yaw) in enumerate(((-10.4, 22.4, 30.0), (-10.0, 17.3, 150.0), (-9.8, 11.9, 260.0))):
        rows.append(("SM_Morin_PalmaA", f"PalmaAlta_Molo_{i:02d}", x, y, z, yaw))
    return rows


def write_csv(rows, path="exports/molo/molo_posizioni_v2.csv"):
    def ue(v):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return "0.0" if s in ("0", "-0", "") else (s if "." in s else s + ".0")
    lines = ["asset,nome,x,y,z,yaw"]
    for a, n, x, y, z, yaw in rows:
        lines.append(f"{a},{n},{ue(x * 100)},{ue(-y * 100)},{ue(z * 100)},{ue(-yaw if yaw else 0.0)}")
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(lines) - 1


def build_context(rows, name="MOLO_C_Contesto"):
    coll = pk._coll(name)
    for a, n, x, y, z, yaw in rows:
        if x == 0.0 and y == 0.0:
            continue
        nm = "CTXC_" + n
        src = bpy.data.objects.get(a)
        if src is None:
            print("manca", a)
            continue
        o = bpy.data.objects.get(nm)
        if o is None:
            o = bpy.data.objects.new(nm, src.data)
            coll.objects.link(o)
        o.data = src.data
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(yaw))
    for a in {r[0] for r in rows if not (r[2] == 0.0 and r[3] == 0.0)}:
        if a in ASSETS:
            bpy.data.objects[a].hide_render = True
            bpy.data.objects[a].hide_viewport = True
    return coll


def ray_test(o, n_dirs=400, skip_mats=None):
    """Normali: raggi da una sfera esterna verso l'oggetto; conta i primi impatti su facce viste dal retro
    (dot(normale, direzione) > 0). Le card (materiali in skip_mats) si saltano: sono two-sided e masked."""
    from mathutils.bvhtree import BVHTree
    me = o.data
    if skip_mats is None:
        skip_mats = {i for i, m in enumerate(me.materials) if m and ("Chioma" in m.name or "Fronde" in m.name)}
    bvh = BVHTree.FromPolygons([v.co for v in me.vertices], [p.vertices for p in me.polygons])
    c = Vector(o.bound_box[0]).lerp(Vector(o.bound_box[6]), 0.5)
    R = (Vector(o.bound_box[6]) - Vector(o.bound_box[0])).length
    rng = np.random.default_rng(1)
    back, hits, skipped = 0, 0, 0
    bad = set()
    for _ in range(n_dirs):
        v = Vector(rng.normal(size=3)).normalized()
        if v.z < 0.05:          # origini sempre sopra il suolo (le mesh non hanno fondo)
            v.z = abs(v.z) + 0.05
            v.normalize()
        org = c + v * R * 1.5
        for jx in np.linspace(-0.4, 0.4, 5):
            for jy in np.linspace(-0.4, 0.4, 5):
                t1 = v.orthogonal().normalized()
                t2 = v.cross(t1)
                target = c + t1 * jx * R + t2 * jy * R
                if target.z < 0.05:          # niente raggi diretti sotto il suolo (le mesh non hanno fondo)
                    continue
                d = (target - org).normalized()
                p = org
                for _k in range(4):             # attraversa le card
                    loc, nrm, idx, dist = bvh.ray_cast(p, d)
                    if loc is None:
                        break
                    if me.polygons[idx].material_index in skip_mats:
                        p = loc + d * 1e-3
                        skipped += 1
                        continue
                    hits += 1
                    if me.polygons[idx].normal.dot(d) > 0:
                        back += 1
                        bad.add(idx)
                    break
    return hits, back, len(bad), skipped


def check_all():
    res = []
    for nm in ASSETS:
        o0 = bpy.data.objects[nm]
        d0 = Vector(o0.dimensions)
        bb0 = [Vector(o0.bound_box[0]), Vector(o0.bound_box[6])]
        line = [nm, pk.tri_count(o0), tuple(round(x, 2) for x in d0)]
        for lod in (1, 2):
            o = bpy.data.objects[f"{nm}_LOD{lod}"]
            bb = [Vector(o.bound_box[0]), Vector(o.bound_box[6])]
            dev = max(max(abs(bb[i][k] - bb0[i][k]) / max(d0[k], 1e-3) for k in range(3)) for i in range(2))
            line += [pk.tri_count(o), round(dev * 100, 2)]
        hits, back, nbad, sk = ray_test(o0)
        line += [f"ray {back}/{hits} retro ({nbad} facce)"]
        res.append(line)
    return res


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    reps = []
    coll = bpy.data.collections[KIT]
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in bpy.context.scene.objects}
    for o in coll.objects:
        o.hide_viewport = False
        o.hide_set(False)
        o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1)
    bpy.context.view_layer.update()
    try:
        for nm in ASSETS:
            for lod in (0, 1, 2):
                on = nm if lod == 0 else f"{nm}_LOD{lod}"
                r = morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset", overwrite=overwrite,
                                            include_ucx=(lod == 0), bake_rotation=(lod > 0), verbose=False)
                reps.append(r)
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps
