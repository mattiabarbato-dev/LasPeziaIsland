"""morin_molo.py — radice del molo del ponte (incrocio con la strada di servizio, ristoranti, alberi). Tranche 1, v1 (2026-11-19).

Scheda di riferimento: ref/radice_molo.md (§2 planimetria, §3 edifici, §4 alberi, §5 lampione, §7.1 risposte dell'utente,
§8 porzioni di foto per le texture, §9 asset). Foto F1/F2/F3/F4 in ref/foto/ (catture Street View: deroga [SV] di CLAUDE.md §5,
solo colori, tessitura e proporzioni; niente UI, persone, targhe, loghi o scritte nelle texture).

Esegui dentro blender/arte_molo.blend (il contesto della passeggiata e del ponte e' gia' appeso in CTX_Contesto):
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_molo as mm; importlib.reload(mm)
    mm.make_textures()     # texture in blender/textures/molo/ (D sRGB, N DirectX, ORM)
    mm.build_materials()
    mm.build_all()         # mesh LOD0/1/2 + UCX in collezione MOLO_Kit (riscrive le mesh omonime, non cancella oggetti)
    rows = mm.layout()     # posizioni (coordinate Blender)
    mm.write_csv(rows)     # exports/molo/molo_posizioni_v1.csv
    mm.build_context(rows) # istanze per i render (collezione MOLO_Contesto)
    mm.export_all()        # FBX in exports/molo/ con morin_export.py (LOD1/LOD2 con bake_rotation=True)
    mm.cameras()           # camere CAM_Molo_F1/F2/F3 dai punti di presa della scheda §1

Quote (coordinate di progetto, metri): molo, strada e masselli a Z +0,01 (1 cm sopra il blockout del molo a Z 0, per non avere
facce complanari finche' il blockout non viene ribassato in UEFN); angolo in cubetti a Z +0,15 come la fascia palme (cordolo 15 cm).
Asset unici del suolo (strada, masselli, angolo): geometria gia' in coordinate di progetto, origine in (0,0,0), si posano in (0,0,0).
Edifici e tendone: geometria in coordinate di progetto, origine (0,0,0), si posano in (0,0,0) (pezzi unici, CLAUDE.md §4).
Lampione, alberi, pino: origine alla base, si posano dal CSV.
"""
import math
import os
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_texphoto as tp

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/molo"
REF = PROJ + "/ref/foto"
F1P = REF + "/vista/inizio_passegiata_ristoranti_che_vanno_verso_il_ponte.png"
F2P = REF + "/vista/ristoranti_visti_da_di_fronte.png"
F3P = REF + "/vista/strada_cheProsegue_verso_il_ponte.png"
F4P = REF + "/pavimentazione/pavimento verso il ponte.png"
KIT = "MOLO_Kit"
EXPDIR = "//../exports/molo"

Z_MOLO = 0.01        # masselli e asfalto (1 cm sopra il blockout del molo)
ZF = pk.ZF           # 0,15: quota della fascia palme e dell'angolo in cubetti
ZB = pk.ZB           # -0,15: fondo dei bordi verticali
X_CURB0, X_CURB1 = 9.55, 9.75     # cordolo della strada lungo l'angolo (faccia sull'asfalto a 9,55)
X_STR0 = 6.5                       # bordo ovest dell'asfalto [S] F1 (6-7,5 nella scheda; 8,1-8,5 dalla camera ricalcolata, vedi §10)
Y_STR0, Y_STR1 = 86.0, 121.0       # asfalto da Y 86 (stima scheda D3) a Viale Italia
Y_RAMO0, Y_RAMO1, X_RAMO1 = 109.25, 113.75, 24.0   # ramo d'asfalto verso il parcheggio [S]
Y_ANG1 = Y_RAMO0                   # lato nord dell'angolo in cubetti (cordolo lungo Y 109)
X_ANG1 = 20.0
R_ANG = 1.6                        # raggio dello spigolo smussato dell'angolo (10,3; 108) [S] F1

# tile in metri delle UV "mondo" dei materiali nuovi (stessa convenzione del kit pavimentazione)
pk.TILE.update({"M_Molo_Masselli": 2.8, "M_Molo_Masselli_Grigio": 2.8, "M_Molo_Asfalto": 4.0})
MASSELLI_GRIGIO_TINTA = (0.36, 0.37, 0.40)    # v2: piu' scuro (F1, F2); moltiplica il colore lineare

PPM = 256            # atlante facciate: px per metro
ATL = 2048           # lato dell'atlante (8 x 8 m)


# =============================================================================================================
# foto
# =============================================================================================================
_PH = {}


def photo(key):
    if key not in _PH:
        _PH[key] = tp.load({"F1": F1P, "F2": F2P, "F3": F3P, "F4": F4P}[key])
    return _PH[key]


def _srgb(c):
    return np.asarray(c, np.float32) / 255.0


def _noise(h, w, sigma, seed):
    r = np.random.default_rng(seed).standard_normal((h, w)).astype(np.float32)
    r = tp.blur(r, sigma)
    return r / (r.std() + 1e-6)


def _photo_detail(key, box, size, sigma=6.0, seed=0, patch=None, n=None, clip=(0.6, 1.4)):
    """Dettaglio fine (alta frequenza, media 1) preso da una porzione di foto e reso tileable a `size`."""
    y0, y1, x0, x1 = box
    a = photo(key)[y0:y1, x0:x1, :3]
    a = tp.resize(a, (x1 - x0) * 3, (y1 - y0) * 3)
    g = tp.lum(a)
    hp = tp.highpass(g, sigma)
    hp = np.clip(hp, clip[0], clip[1])
    patch = patch or min(hp.shape[0], hp.shape[1], 160)
    syn = tp.splat_synth(hp[..., None], size, patch, n or int((size / patch) ** 2 * 5), seed=seed)[..., 0]
    return syn / syn.mean()


def _save(a, name):
    os.makedirs(TEXDIR, exist_ok=True)
    tp.save(a, f"{TEXDIR}/{name}.png")
    return f"{TEXDIR}/{name}.png"


def _normal_ao(height, strength, ao_sigma=6.0, ao_k=6.0):
    n = tp.normal_dx(height, strength)
    ao = np.clip(1.0 - ao_k * np.maximum(tp.blur(height, ao_sigma) - height, 0), 0.35, 1.0)
    return n, ao


def _orm(ao, rough, metal):
    return np.dstack([ao, rough, metal]).astype(np.float32)


# =============================================================================================================
# texture: masselli del molo (F4 + F3), asfalto (F1)
# =============================================================================================================
def make_tex_masselli(size=2048, seed=3):
    """Masselli rettangolari 28 x 14 cm a correre, lato lungo lungo X (corsi trasversali all'asse del molo, F3),
    giunti 8 mm con erba e terra (F4). Tile 2,8 m: 10 x 20 masselli. Colore e grana dalla foto F4 (intera) e F3."""
    rng = np.random.default_rng(seed)
    T = 2.8
    ppm = size / T
    bw, bh = 0.28, 0.14
    nx, ny = int(T / bw), int(T / bh)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / ppm   # metri, riga 0 in alto
    row = np.floor(yy / bh).astype(int)
    off = (row % 2) * (bw / 2)
    xs = (xx + off) % T
    col = np.floor(xs / bw).astype(int)
    lx = xs - col * bw
    ly = yy - row * bh
    d = np.minimum(np.minimum(lx, bw - lx), np.minimum(ly, bh - ly))   # distanza dal bordo del massello
    bid = (row % ny) * nx + (col % nx)
    joint = 0.004
    # altezza: massello con bordo smussato (1 cm), giunto incassato
    hgt = np.clip((d - joint) / 0.012, 0, 1) ** 0.6
    # colore per massello
    base = _srgb((186, 180, 165))
    var = rng.normal(1.0, 0.04, nx * ny).astype(np.float32)
    hue = rng.normal(0, 0.006, (nx * ny, 3)).astype(np.float32)
    det = _photo_detail("F4", (10, 190, 10, 380), size, sigma=5, seed=seed, patch=128, clip=(0.88, 1.12))
    det3 = _photo_detail("F3", (700, 895, 0, 380), size, sigma=4, seed=seed + 1, patch=96, clip=(0.85, 1.15))
    big = 1 + 0.05 * _noise(size, size, 60, seed + 2) + 0.035 * _noise(size, size, 1.0, seed + 9)
    alb = base[None, None, :] * (var[bid][..., None] + hue[bid]) * (0.65 * det + 0.35 * det3)[..., None] * big[..., None]
    # usura: bordi un po' piu' scuri, qualche macchia
    edge = np.clip(1 - d / 0.02, 0, 1)
    alb *= (1 - 0.12 * edge)[..., None]
    stain = np.clip(_noise(size, size, 25, seed + 3) - 1.3, 0, 1)
    alb *= (1 - 0.07 * stain)[..., None]
    # giunti: terra scura con erba a tratti (F4)
    jm = np.clip(1 - (d - joint * 0.3) / (joint * 1.2), 0, 1)
    grass = np.clip(_noise(size, size, 6, seed + 4) * 0.9 - 0.2, 0, 1)
    gcol = _srgb((92, 112, 52)) * (0.8 + 0.4 * np.clip(_noise(size, size, 2, seed + 5) * 0.5 + 0.5, 0, 1))[..., None]
    dirt = _srgb((88, 82, 70))
    jcol = dirt[None, None, :] * (1 - grass[..., None]) + gcol * grass[..., None]
    alb = alb * (1 - jm[..., None]) + jcol * jm[..., None]
    alb = np.clip(alb, 0, 1)
    h = hgt * 0.9 + 0.1 * (det - 1)
    n, ao = _normal_ao(h, 3.0, 5, 3)
    rough = np.clip(0.82 + 0.08 * jm + 0.05 * _noise(size, size, 10, seed + 6), 0, 1)
    out = {
        "T_Molo_Masselli_D": alb,
        "T_Molo_Masselli_N": n,
        "T_Molo_Masselli_ORM": _orm(ao, rough, np.zeros_like(ao)),
    }
    for k, v in out.items():
        _save(v, k)
    return list(out)


def make_tex_asfalto(size=2048, seed=5):
    """Asfalto scuro con inerti e rattoppi. Grana dalla foto F1 (x 950-1250, y 690-800, lontano dalla croce di UI)."""
    det = _photo_detail("F1", (690, 800, 950, 1250), size, sigma=3, seed=seed, patch=150)
    fine = 1 + 0.10 * _noise(size, size, 0.7, seed + 1) + 0.06 * _noise(size, size, 2.0, seed + 2)
    base = _srgb((70, 70, 72))
    alb = base[None, None, :] * (0.7 * det + 0.3 * fine)[..., None]
    # rattoppi e zone lisce
    patch = np.clip((_noise(size, size, 90, seed + 3) - 0.9) * 3, 0, 1)
    alb *= (1 - 0.12 * patch)[..., None]
    wear = np.clip((_noise(size, size, 50, seed + 4) - 0.5) * 2, 0, 1)
    alb = alb * (1 - 0.15 * wear[..., None]) + _srgb((96, 95, 92)) * 0.15 * wear[..., None]
    # qualche inerte chiaro
    pebble = np.clip((_noise(size, size, 0.9, seed + 5) - 2.3) * 2, 0, 1)
    alb = alb * (1 - pebble[..., None] * 0.5) + _srgb((150, 146, 138)) * pebble[..., None] * 0.5
    alb = np.clip(alb, 0, 1)
    h = 0.5 * _noise(size, size, 0.8, seed + 6) + 0.3 * pebble - 0.4 * patch
    n, ao = _normal_ao(h, 0.9, 3, 0.4)
    rough = np.clip(0.88 - 0.1 * wear + 0.04 * _noise(size, size, 6, seed + 7), 0, 1)
    out = {"T_Molo_Asfalto_D": alb, "T_Molo_Asfalto_N": n, "T_Molo_Asfalto_ORM": _orm(ao, rough, np.zeros_like(ao))}
    for k, v in out.items():
        _save(v, k)
    return list(out)


# =============================================================================================================
# texture: atlante delle facciate (trim sheet 8 x 8 m, 256 px/m)
# =============================================================================================================
# Righe in metri dal basso dell'immagine (= coordinata V delle UV x 8):
#   R1  V 4,6-8,0  facciata A1/A2 da terra (h 0) a 3,4 m:
#       U 0-2 giallo con scudo generico (U 0-0,9 giallo liscio) · U 2-4,5 giallo con porta-finestra a due ante ·
#       U 4,5-6 giallo con porta singola · U 6-8 rosa con finestra e insegna liscia (U 6-6,45 rosa liscio)
#   R2  V 1,2-4,6  facciata A3/A4/A5/C da terra a 3,4 m:
#       U 0-2 giallo A3 con finestrella e zoccolo (U 0-0,8 liscio) · U 2-4 bianco con vetrata in legno e fascia gialla ·
#       U 4-6 bianco con porta rosso scuro e zoccolo · U 6-8 bianco con finestra a grata e zoccolo (U 6-6,7 liscio)
#   R3  V 0,75-1,20 cornicione rosso-bruno (0,87-1,20) con cornice bianca (0,75-0,87) · V 0,40-0,75 tenda crema ·
#       V 0,15-0,40 copertura del tetto (guaina grigia) · V 0-0,15: U 0-4 vernice rosso-bruna (ringhiera), U 4-8 metallo grigio
ROW1, ROW2 = 4.6, 1.2
SEG = {   # nome: (u0, u1, base_v)
    "G_scudo": (0.0, 2.0, ROW1), "G_liscio": (0.05, 0.85, ROW1), "G_portafin": (2.0, 4.5, ROW1),
    "G_porta": (4.5, 6.0, ROW1), "P_finestra": (6.0, 8.0, ROW1), "P_liscio": (6.05, 6.40, ROW1),
    "Y_finestrella": (0.0, 2.0, ROW2), "Y_liscio": (0.05, 0.75, ROW2), "W_vetrata": (2.0, 4.0, ROW2), "WY_liscio": (2.02, 2.32, ROW2),
    "W_porta": (4.0, 6.0, ROW2), "W_grata": (6.0, 8.0, ROW2), "W_liscio": (6.05, 6.65, ROW2),
}
TRIM = {"cornicione": (0.75, 1.20), "cornicione_rosso": (0.87, 1.20), "cornice_bianca": (0.75, 0.87), "tenda": (0.40, 0.75), "tetto": (0.15, 0.40),
        "vernice": (0.0, 0.15)}
WALL_H = 3.4
COL = {   # sRGB, dalle foto (mediane delle porzioni §8, corrette a mano per togliere ombra/sole)
    "giallo": (222, 200, 140), "rosa": (214, 152, 136), "bianco": (232, 230, 222), "giallo_A3": (226, 204, 132),
    "zoccolo": (128, 126, 120), "legno": (98, 58, 36), "legno_chiaro": (150, 100, 62), "rosso_porta": (112, 40, 34),
    "cornicione": (120, 62, 48), "cornice": (214, 210, 196), "tenda": (222, 216, 196), "tetto": (112, 110, 106),
    "vetro": (38, 44, 50), "tenda_int": (196, 180, 150), "scudo": (170, 32, 36), "scudo_banda": (214, 96, 40),
    "insegna": (238, 238, 232), "insegna_blu": (52, 104, 168), "grata": (236, 236, 232), "metallo": (150, 152, 154),
}


class _Atlas:
    def __init__(self, n=ATL, ppm=PPM, seed=1):
        self.n, self.ppm = n, ppm
        self.alb = np.zeros((n, n, 3), np.float32)
        self.h = np.zeros((n, n), np.float32)
        self.r = np.full((n, n), 0.85, np.float32)
        self.m = np.zeros((n, n), np.float32)
        self.seed = seed

    def sl(self, u0, u1, v0, v1):
        """Fetta di pixel per il rettangolo in metri (u da sinistra, v dal basso)."""
        n, p = self.n, self.ppm
        r0 = int(round(n - v1 * p)); r1 = int(round(n - v0 * p))
        c0 = int(round(u0 * p)); c1 = int(round(u1 * p))
        return slice(max(r0, 0), min(r1, n)), slice(max(c0, 0), min(c1, n))

    def fill(self, u0, u1, v0, v1, col=None, h=None, r=None, m=None, det=None, mask=None):
        rs, cs = self.sl(u0, u1, v0, v1)
        if rs.stop <= rs.start or cs.stop <= cs.start:
            return
        if mask is None:
            mask = np.ones((rs.stop - rs.start, cs.stop - cs.start), np.float32)
        mk = mask[..., None]
        if col is not None:
            c = np.broadcast_to(_srgb(col) if not isinstance(col, np.ndarray) else col,
                                (mask.shape[0], mask.shape[1], 3)).astype(np.float32)
            if det is not None:
                c = c * det[rs, cs][..., None]
            self.alb[rs, cs] = self.alb[rs, cs] * (1 - mk) + c * mk
        if h is not None:
            self.h[rs, cs] = self.h[rs, cs] * (1 - mask) + h * mask
        if r is not None:
            self.r[rs, cs] = self.r[rs, cs] * (1 - mask) + r * mask
        if m is not None:
            self.m[rs, cs] = self.m[rs, cs] * (1 - mask) + m * mask

    def frame(self, u0, u1, v0, v1, w, col, h=0.6, r=0.55, det=None):
        """Telaio rettangolare di spessore w (m)."""
        for a in ((u0, u1, v0, v0 + w), (u0, u1, v1 - w, v1), (u0, u0 + w, v0, v1), (u1 - w, u1, v0, v1)):
            self.fill(*a, col=col, h=h, r=r, det=det)


def _glass(A, u0, u1, v0, v1, seed, curtain=False):
    """Vetro scuro con riflesso del cielo in alto e interno sfumato."""
    rs, cs = A.sl(u0, u1, v0, v1)
    hh, ww = rs.stop - rs.start, cs.stop - cs.start
    t = np.linspace(0, 1, hh)[:, None] * np.ones((1, ww))
    sky = _srgb((120, 136, 150)) * (1 - t[..., None]) * 0.55
    base = _srgb(COL["vetro"])[None, None, :] + sky
    rng = np.random.default_rng(seed)
    inside = 1 + 0.25 * tp.blur(rng.standard_normal((hh, ww)).astype(np.float32), 6)
    c = base * inside[..., None]
    if curtain:
        cur = _srgb(COL["tenda_int"]) * (0.85 + 0.15 * np.sin(np.linspace(0, 30, ww))[None, :, None])
        c = c * 0.25 + cur * 0.75
    A.alb[rs, cs] = np.clip(c, 0, 1)
    A.h[rs, cs] = 0.15
    A.r[rs, cs] = 0.12 if not curtain else 0.7


def _door(A, u0, u1, v0, v1, col, seed, leaves=2, kick=0.45, glass=True, transom=0.0):
    fw = 0.08
    A.fill(u0, u1, v0, v1, col=col, h=0.55, r=0.55)
    A.frame(u0, u1, v0, v1, fw, col, h=0.8)
    lw = (u1 - u0 - 2 * fw) / leaves
    for i in range(leaves):
        a0 = u0 + fw + i * lw
        a1 = a0 + lw
        A.frame(a0, a1, v0 + fw, v1 - fw - transom, 0.06, col, h=0.75)
        if glass:
            _glass(A, a0 + 0.07, a1 - 0.07, v0 + fw + kick, v1 - fw - transom - 0.07, seed + i)
        # pannello basso con bordino
        if kick > 0.25:
            A.fill(a0 + 0.12, a1 - 0.12, v0 + fw + 0.08, v0 + fw + kick - 0.08, col=np.asarray(_srgb(col) * 0.88), h=0.5)
        # maniglia
        hu = a1 - 0.10 if i % 2 == 0 else a0 + 0.06
        A.fill(hu, hu + 0.04, v0 + 1.0, v0 + 1.12, col=(170, 170, 165), h=0.95, r=0.35, m=1.0)
    if transom > 0:
        _glass(A, u0 + fw + 0.05, u1 - fw - 0.05, v1 - fw - transom + 0.04, v1 - fw - 0.04, seed + 7)


def _window(A, u0, u1, v0, v1, frame_col, seed, sill=True, curtain=False, grille=False):
    fw = 0.07
    A.fill(u0 - 0.04, u1 + 0.04, v0 - 0.04, v1 + 0.04, col=(140, 136, 128), h=0.1, r=0.8)   # spalletta in ombra
    _glass(A, u0, u1, v0, v1, seed, curtain=curtain)
    A.frame(u0, u1, v0, v1, fw, frame_col, h=0.7)
    A.fill((u0 + u1) / 2 - 0.03, (u0 + u1) / 2 + 0.03, v0, v1, col=frame_col, h=0.7, r=0.5)
    if grille:
        for k in range(1, 4):
            uu = u0 + (u1 - u0) * k / 4
            A.fill(uu - 0.015, uu + 0.015, v0, v1, col=COL["grata"], h=0.95, r=0.45, m=0.6)
        for k in range(1, 5):
            vv = v0 + (v1 - v0) * k / 5
            A.fill(u0, u1, vv - 0.015, vv + 0.015, col=COL["grata"], h=0.95, r=0.45, m=0.6)
    if sill:
        A.fill(u0 - 0.08, u1 + 0.08, v0 - 0.07, v0, col=(226, 224, 216), h=0.9, r=0.6)


def _shield(A, uc, vb, w, hgt):
    """Scudo generico inventato (rosso, banda arancio, pesce bianco stilizzato): sostituisce l'insegna reale."""
    rs, cs = A.sl(uc - w / 2, uc + w / 2, vb, vb + hgt)
    hh, ww = rs.stop - rs.start, cs.stop - cs.start
    y, x = np.mgrid[0:hh, 0:ww].astype(np.float32)
    xn = (x / ww - 0.5) * 2           # -1..1
    yn = y / hh                       # 0 in alto
    halfw = np.where(yn < 0.55, 1.0, np.sqrt(np.clip(1 - ((yn - 0.55) / 0.45) ** 2, 0, 1)) * (1 - 0.15 * (yn - 0.55)))
    inside = (np.abs(xn) < halfw * 0.98).astype(np.float32)
    inner = (np.abs(xn) < halfw * 0.86).astype(np.float32) * (yn > 0.05) * (yn < 0.96)
    band = inner * (yn < 0.24)
    fish = ((((xn + 0.05) / 0.5) ** 2 + ((yn - 0.55) / 0.13) ** 2) < 1).astype(np.float32)
    tail = ((xn > 0.38) & (xn < 0.62) & (np.abs(yn - 0.55) < (xn - 0.38) * 0.8)).astype(np.float32)
    fish = np.maximum(fish, tail) * inner
    c = np.zeros((hh, ww, 3), np.float32)
    c[:] = _srgb(COL["scudo"]) * 0.75
    c = np.where(inner[..., None] > 0, _srgb(COL["scudo"]), c)
    c = np.where(band[..., None] > 0, _srgb(COL["scudo_banda"]), c)
    c = np.where(fish[..., None] > 0, _srgb((236, 232, 222)), c)
    m = tp.blur(inside, 0.8)
    A.alb[rs, cs] = A.alb[rs, cs] * (1 - m[..., None]) + c * m[..., None]
    A.h[rs, cs] = A.h[rs, cs] * (1 - m) + 0.7 * m
    A.r[rs, cs] = A.r[rs, cs] * (1 - m) + 0.45 * m


def _wall(A, u0, u1, base, col, det, top_col=None, top_from=None, zoccolo=None, dirt=True):
    A.fill(u0, u1, base, base + WALL_H, col=col, h=0.3, r=0.88, det=det)
    if top_col is not None:
        A.fill(u0, u1, base + top_from, base + WALL_H, col=top_col, h=0.3, r=0.88, det=det)
    if zoccolo:
        A.fill(u0, u1, base, base + zoccolo, col=COL["zoccolo"], h=0.45, r=0.8, det=det)
        A.fill(u0, u1, base + zoccolo - 0.02, base + zoccolo, col=np.asarray(_srgb(COL["zoccolo"]) * 1.15), h=0.5)
    if dirt:
        rs, cs = A.sl(u0, u1, base, base + WALL_H)
        hh = rs.stop - rs.start
        z = (1 - np.linspace(0, 1, hh))[:, None] * WALL_H     # quota in m (riga 0 = in alto)
        g = 1 - 0.10 * np.clip(1 - z / 0.6, 0, 1) - 0.06 * np.clip((z - (WALL_H - 0.35)) / 0.35, 0, 1)
        A.alb[rs, cs] *= g[..., None]


def make_tex_facciate(seed=21):
    A = _Atlas(seed=seed)
    n = ATL
    # grana dell'intonaco: F2 x 800-840, y 430-500 (giallo fra scudo e porta) e F2 x 150-182, y 400-445 (bianco di A4)
    det = (0.75 * _photo_detail("F2", (430, 500, 800, 840), n, sigma=4, seed=seed, patch=96) +
           0.25 * _photo_detail("F2", (400, 445, 150, 182), n, sigma=4, seed=seed + 1, patch=90))
    det = 1 + (det - 1) * 0.6 + 0.025 * _noise(n, n, 40, seed + 2)
    # ---- riga 1: A1 giallo, A2 rosa
    _wall(A, 0.0, 6.0, ROW1, COL["giallo"], det)
    _wall(A, 6.0, 8.0, ROW1, COL["rosa"], det)
    _shield(A, 1.35, ROW1 + 1.45, 0.95, 1.15)
    _door(A, 2.25, 4.25, ROW1 + 0.0, ROW1 + 2.55, COL["legno"], seed + 10, leaves=2, kick=0.12)
    _door(A, 4.75, 5.75, ROW1 + 0.0, ROW1 + 2.45, COL["legno"], seed + 11, leaves=1, kick=0.12)
    _window(A, 6.65, 7.55, ROW1 + 1.0, ROW1 + 2.35, COL["legno"], seed + 12, curtain=True)
    A.fill(6.70, 7.50, ROW1 + 0.86, ROW1 + 1.0, col=(150, 60, 70), h=0.8, r=0.8)     # fioriera della finestra
    A.fill(6.45, 7.75, ROW1 + 2.62, ROW1 + 3.05, col=COL["insegna"], h=0.75, r=0.5)  # insegna liscia
    A.frame(6.45, 7.75, ROW1 + 2.62, ROW1 + 3.05, 0.025, (90, 110, 150), h=0.8)
    # ---- riga 2: A3 giallo e bianco, A4/A5 bianco
    _wall(A, 0.0, 2.0, ROW2, COL["giallo_A3"], det, zoccolo=0.25)
    _window(A, 1.0, 1.55, ROW2 + 1.5, ROW2 + 2.25, COL["legno"], seed + 13, curtain=False)
    _wall(A, 2.0, 4.0, ROW2, COL["bianco"], det, top_col=COL["giallo_A3"], top_from=2.85)
    _door(A, 2.35, 3.65, ROW2 + 0.0, ROW2 + 2.6, COL["legno_chiaro"], seed + 14, leaves=2, kick=0.1, transom=0.45)
    A.fill(2.4, 3.6, ROW2 + 2.68, ROW2 + 2.80, col=COL["insegna_blu"], h=0.7, r=0.5)  # fascia blu liscia
    _wall(A, 4.0, 8.0, ROW2, COL["bianco"], det, zoccolo=0.35)
    A.fill(4.0, 4.25, ROW2, ROW2 + WALL_H, col=COL["giallo_A3"], h=0.35, det=det)    # lesena gialla (A4)
    A.fill(5.75, 6.0, ROW2, ROW2 + WALL_H, col=COL["giallo_A3"], h=0.35, det=det)
    _door(A, 4.5, 5.5, ROW2 + 0.0, ROW2 + 2.35, COL["rosso_porta"], seed + 15, leaves=1, kick=2.1, glass=False)
    for k in range(5):  # doghe della porta rossa
        uu = 4.62 + k * 0.17
        A.fill(uu, uu + 0.02, ROW2 + 0.15, ROW2 + 2.2, col=np.asarray(_srgb(COL["rosso_porta"]) * 0.7), h=0.4)
    _window(A, 6.85, 7.75, ROW2 + 1.0, ROW2 + 2.2, COL["grata"], seed + 16, grille=True)
    A.fill(7.95, 8.0, ROW2, ROW2 + WALL_H, col=COL["bianco"], det=det)
    # ---- riga 3: trim
    v0, v1 = TRIM["cornicione"]
    mattoni = 1 + 0.07 * _noise(n, n, 1.2, seed + 3)
    A.fill(0, 8, 0.87, v1, col=COL["cornicione"], h=0.8, r=0.75, det=mattoni * det)
    A.fill(0, 8, 1.17, v1, col=COL["cornice"], h=0.9, r=0.6, det=det)           # scossalina chiara in cima
    A.fill(0, 8, v0, 0.87, col=COL["cornice"], h=0.7, r=0.7, det=det)
    A.fill(0, 8, 0.85, 0.87, col=(150, 146, 136), h=0.6)
    t0, t1 = TRIM["tenda"]
    rs, cs = A.sl(0, 8, t0, t1)
    pieg = 0.94 + 0.06 * np.sin(np.linspace(0, 2 * np.pi * 8 / 0.11, cs.stop - cs.start))[None, :]
    A.fill(0, 8, t0, t1, col=COL["tenda"], h=0.5, r=0.9, det=np.ones((n, n), np.float32))
    A.alb[rs, cs] *= pieg[..., None] * np.linspace(1.0, 0.82, rs.stop - rs.start)[:, None, None]
    A.fill(0, 8, t0, t0 + 0.04, col=np.asarray(_srgb(COL["tenda"]) * 0.8), h=0.55)
    g0, g1 = TRIM["tetto"]
    # guaina a teli da 1 m con sormonti: variazione solo lungo U, cosi' la banda si puo' stirare in V sui tetti
    u = np.arange(n, dtype=np.float32) / PPM
    strip = 1 + 0.05 * np.sin(u * 2 * np.pi * 0.37) + 0.04 * np.random.default_rng(seed + 4).standard_normal(n).astype(np.float32) * 0.3
    strip *= 1 - 0.22 * ((u % 1.0) < 0.03)
    A.fill(0, 8, g0, g1, col=COL["tetto"], h=0.3, r=0.9, det=np.broadcast_to(strip[None, :], (n, n)))
    A.fill(0, 4, 0, 0.15, col=COL["cornicione"], h=0.5, r=0.5)
    A.fill(4, 8, 0, 0.15, col=COL["metallo"], h=0.5, r=0.45, m=0.8)
    alb = np.clip(A.alb, 0, 1)
    n_, ao = _normal_ao(A.h, 6.0, 3, 1.2)
    out = {"T_Molo_Facciate_D": alb, "T_Molo_Facciate_N": n_, "T_Molo_Facciate_ORM": _orm(ao, A.r, A.m)}
    for k, v in out.items():
        _save(v, k)
    return list(out)


# =============================================================================================================
# texture: alberi (chiome a card con alfa ricostruita, cortecce)
# =============================================================================================================
def _crown_palette(n=4096, seed=0):
    """Colori delle foglie presi dai pixel della chioma in F2 (x 330-900, y 130-330), scartando il cielo."""
    a = photo("F2")[130:330, 330:900, :3].reshape(-1, 3)
    g = a[:, 1]
    ok = (g > a[:, 2] + 0.06) & (a.sum(1) > 0.25) & (a.sum(1) < 2.0)
    a = a[ok]
    rng = np.random.default_rng(seed)
    return a[rng.integers(0, len(a), n)]


def _leaf_mask(sz, kind, rng):
    y, x = np.mgrid[0:sz, 0:sz].astype(np.float32)
    x = (x - sz / 2) / (sz / 2)
    y = (y - sz / 2) / (sz / 2)
    th = rng.uniform(0, 2 * np.pi)
    xr = x * np.cos(th) - y * np.sin(th)
    yr = x * np.sin(th) + y * np.cos(th)
    ang = np.arctan2(yr, xr)
    r = np.sqrt(xr ** 2 + yr ** 2)
    # foglia palmata a 5 lobi (platano)
    lim = 0.62 + 0.30 * np.abs(np.cos(2.5 * (ang + np.pi / 2))) ** 0.7
    lim = lim * np.where(np.sin(ang) > 0.6, 0.7, 1.0)
    m = (r < lim * rng.uniform(0.85, 1.0)).astype(np.float32)
    d = [np.abs(xr * np.sin(a_) - yr * np.cos(a_)) for a_ in (np.pi / 2, np.pi / 2 + 0.9, np.pi / 2 - 0.9)]
    vein = np.clip(1 - np.minimum(np.minimum(d[0], d[1]), d[2]) / 0.04, 0, 1) * m
    return m, vein, th


def _line(Q, x0, y0, x1, y1, w, col, h, ao):
    S = Q["a"].shape[0]
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    xs = np.linspace(x0, x1, n).astype(int)
    ys = np.linspace(y0, y1, n).astype(int)
    ok = (xs >= w) & (xs < S - w) & (ys >= w) & (ys < S - w)
    for dx in range(-w + 1, w):
        for dy in range(-w + 1, w):
            Q["c"][ys[ok] + dy, xs[ok] + dx] = col
            Q["a"][ys[ok] + dy, xs[ok] + dx] = 1
            Q["h"][ys[ok] + dy, xs[ok] + dx] = h
            Q["ao"][ys[ok] + dy, xs[ok] + dx] = ao


def _cluster(Q, kind, seed, pal):
    """Riempie un quadrante 1024 x 1024 con un ciuffo di foglie (platano) o di aghi (pino) attorno al centro."""
    rng = np.random.default_rng(seed)
    S = Q["a"].shape[0]
    twig = _srgb((64, 52, 40))
    for k in range(9 if kind == "platano" else 6):
        ang = rng.uniform(0, 2 * np.pi)
        L = rng.uniform(0.25, 0.46) * S * (1 if kind == "platano" else 0.6)
        cx, cy = S / 2 + rng.normal(0, S * 0.04), S / 2 + rng.normal(0, S * 0.04)
        _line(Q, cx, cy, cx + np.cos(ang) * L, cy + np.sin(ang) * L, 3, twig, 0.3, 0.5)
    if kind == "platano":
        nleaf = 4200
        subs = [(S / 2 + rng.normal(0, S * 0.10), S / 2 + rng.normal(0, S * 0.10), rng.uniform(0.17, 0.25) * S)
                for _ in range(8)]
        for i in range(nleaf):
            sx, sy, sr = subs[rng.integers(0, len(subs))]
            r = sr * np.sqrt(rng.uniform(0, 1))
            a = rng.uniform(0, 2 * np.pi)
            cx = int(sx + r * np.cos(a)); cy = int(sy + r * np.sin(a))
            sz = int(rng.uniform(46, 78))
            m, vein, th = _leaf_mask(sz, kind, rng)
            y0, x0 = cy - sz // 2, cx - sz // 2
            if y0 < 0 or x0 < 0 or y0 + sz > S or x0 + sz > S:
                continue
            depth = i / nleaf                       # foglie disegnate dopo = davanti, piu' chiare
            # v2: tinta piu' uniforme e piu' verde (niente macchie gialle), luce gestita dalle normali della chioma
            base_c = 0.5 * PAL_MED + 0.5 * np.array([0.235, 0.314, 0.141], np.float32)
            col = (0.2 * pal[rng.integers(0, len(pal))] + 0.8 * base_c) * (0.72 + 0.38 * depth) * rng.uniform(0.95, 1.05)
            yy = np.linspace(-1, 1, sz)[:, None]
            xx = np.linspace(-1, 1, sz)[None, :]
            shade = 1 + 0.12 * (np.cos(th) * yy - np.sin(th) * xx)
            c = np.clip(col[None, None, :] * shade[..., None] * (1 + 0.15 * vein[..., None]), 0, 1)
            sl = (slice(y0, y0 + sz), slice(x0, x0 + sz))
            mk = m[..., None]
            Q["c"][sl] = Q["c"][sl] * (1 - mk) + c * mk
            Q["a"][sl] = np.maximum(Q["a"][sl], m)
            Q["h"][sl] = Q["h"][sl] * (1 - m) + (0.4 + 0.6 * depth + 0.1 * vein) * m
            Q["ao"][sl] = Q["ao"][sl] * (1 - m) + (0.55 + 0.45 * depth) * m
    else:
        ntuft = 420
        for i in range(ntuft):
            r = S * 0.40 * np.sqrt(rng.uniform(0, 1))
            a = rng.uniform(0, 2 * np.pi)
            tx, ty = S / 2 + r * np.cos(a), S / 2 + r * np.sin(a) * 0.8
            depth = i / ntuft
            for k in range(30):
                ang = rng.uniform(0, 2 * np.pi)
                L = rng.uniform(30, 52)
                col = np.clip(pal[rng.integers(0, len(pal))] * (0.6 + 0.5 * depth), 0, 1)
                _line(Q, tx + np.cos(ang) * 4, ty + np.sin(ang) * 4, tx + np.cos(ang) * L, ty + np.sin(ang) * L, 1,
                      col, 0.4 + 0.6 * depth, 0.6 + 0.4 * depth)


def _make_crown_atlas(kind, name, seed):
    S = 1024
    global PAL_MED
    if kind == "platano":
        pal = _crown_palette(seed=seed)
        PAL_MED = np.median(pal, 0)
    else:   # pino domestico: verde scuro e freddo (chioma a destra di F2, x 955-1030, y 250-330: tinta media)
        rng = np.random.default_rng(seed)
        base = np.array([0.20, 0.27, 0.15], np.float32)
        pal = base[None, :] * rng.uniform(0.75, 1.35, (2048, 1)) + rng.normal(0, 0.015, (2048, 3))
    D = np.zeros((2 * S, 2 * S, 4), np.float32)
    H = np.zeros((2 * S, 2 * S), np.float32)
    AO = np.ones((2 * S, 2 * S), np.float32)
    for q in range(4):
        Q = {"c": np.zeros((S, S, 3), np.float32), "a": np.zeros((S, S), np.float32),
             "h": np.zeros((S, S), np.float32), "ao": np.ones((S, S), np.float32)}
        _cluster(Q, kind, seed + q * 17, pal)
        r0, c0 = (q // 2) * S, (q % 2) * S
        D[r0:r0 + S, c0:c0 + S, :3] = Q["c"]
        D[r0:r0 + S, c0:c0 + S, 3] = Q["a"]
        H[r0:r0 + S, c0:c0 + S] = Q["h"]
        AO[r0:r0 + S, c0:c0 + S] = Q["ao"]
    # dilatazione del colore sotto l'alfa (niente aloni scuri nei mip)
    a = D[..., 3]
    col = D[..., :3]
    bl = tp.blur(col * a[..., None], 6)
    wa = tp.blur(a, 6)[..., None]
    fill = bl / np.maximum(wa, 1e-3)
    D[..., :3] = np.where(a[..., None] > 0.5, col, np.clip(fill, 0, 1))
    n = tp.normal_dx(tp.blur(H, 1.0), 1.5)
    orm = _orm(np.clip(AO, 0, 1), np.full_like(AO, 0.85), np.zeros_like(AO))
    _save(D, name + "_D"); _save(n, name + "_N"); _save(orm, name + "_ORM")
    return [name + s for s in ("_D", "_N", "_ORM")]


def _make_bark(name, kind, seed, size=1024):
    if kind == "platano":   # corteccia a placche mimetiche (crema, grigio-oliva, bruno)
        cols = [_srgb((178, 170, 140)), _srgb((128, 126, 104)), _srgb((96, 92, 78)), _srgb((150, 146, 118))]
        alb = np.zeros((size, size, 3), np.float32) + cols[0]
        h = np.zeros((size, size), np.float32)
        for i, c in enumerate(cols[1:]):
            nz = _noise(size, size, 18 + 6 * i, seed + i)
            m = np.clip((nz - 0.2 - 0.25 * i) * 4, 0, 1)
            alb = alb * (1 - m[..., None]) + c * m[..., None]
            h += m * 0.3
        alb *= (1 + 0.06 * _noise(size, size, 1.2, seed + 9))[..., None]
    else:                   # pino: placche bruno-rossicce allungate in verticale con fessure scure
        nz = tp.resize(_noise(size, size // 4, 3, seed)[:, :, None], size, size)[..., 0]
        plates = np.clip(nz * 0.8 + 0.5, 0, 1)
        fz = tp.resize(_noise(size // 2, size // 4, 3, seed + 1)[:, :, None], size, size)[..., 0]
        fiss = np.clip(1 - np.abs(fz) * 2.2, 0, 1) ** 3
        alb = _srgb((122, 80, 58))[None, None, :] * (0.75 + 0.35 * plates[..., None])
        alb = alb * (1 - fiss[..., None] * 0.7) + _srgb((40, 30, 26)) * fiss[..., None] * 0.7
        h = plates * 0.6 - fiss
    alb = np.clip(alb, 0, 1)
    n, ao = _normal_ao(h, 3.0, 4, 1.5)
    rough = np.full((size, size), 0.9, np.float32)
    _save(alb, name + "_D"); _save(n, name + "_N"); _save(_orm(ao, rough, np.zeros_like(ao)), name + "_ORM")
    return [name + s for s in ("_D", "_N", "_ORM")]


def make_tex_alberi():
    out = _make_crown_atlas("platano", "T_Albero_Latifoglia_Chioma", 101)
    out += _make_bark("T_Albero_Platano_Corteccia", "platano", 202)
    out += _make_crown_atlas("pino", "T_Morin_PinoDomestico_Chioma", 303)
    out += _make_bark("T_Morin_PinoDomestico_Corteccia", "pino", 404)
    return out


def make_textures():
    out = make_tex_masselli() + make_tex_asfalto() + make_tex_facciate() + make_tex_alberi()
    print("texture:", out)
    return out


# =============================================================================================================
# materiali
# =============================================================================================================
def build_materials():
    t = TEXDIR + "/"
    for m, base, alpha in (("M_Molo_Masselli", "T_Molo_Masselli", False), ("M_Molo_Asfalto", "T_Molo_Asfalto", False),
                           ("M_Molo_Facciate", "T_Molo_Facciate", False),
                           ("M_Albero_Latifoglia_Chioma", "T_Albero_Latifoglia_Chioma", True),
                           ("M_Albero_Platano_Corteccia", "T_Albero_Platano_Corteccia", False),
                           ("M_Morin_PinoDomestico_Chioma", "T_Morin_PinoDomestico_Chioma", True),
                           ("M_Morin_PinoDomestico_Corteccia", "T_Morin_PinoDomestico_Corteccia", False)):
        pk._pbr_material(m, t + base + "_D.png", t + base + "_N.png", t + base + "_ORM.png", alpha=alpha)
    # radice e fronte dei ristoranti: stessi masselli piu' scuri e freddi (F1, F2: grigio; F3/F4 sul molo: chiari) [S]
    pk._pbr_material("M_Molo_Masselli_Grigio", t + "T_Molo_Masselli_D.png", t + "T_Molo_Masselli_N.png",
                     t + "T_Molo_Masselli_ORM.png", tint=MASSELLI_GRIGIO_TINTA)
    for m in ("M_Pav_Cubetti", "M_Pav_Fascia", "M_Morin_Ghisa", "M_Morin_Globo"):
        if m not in bpy.data.materials:   # appesi dal contesto (arte_pavimentazione.blend); altrimenti dal kit
            pk.build_materials(make_textures=False)
            break
    return True


# =============================================================================================================
# utilita' geometriche
# =============================================================================================================
def _uv_set(face, uvs, layer):
    for lp, uv in zip(face.loops, uvs):
        lp[layer].uv = uv


def _poly_fill(bm, pts, z, mi, uvf=None):
    """Poligono orizzontale (lista XY in senso antiorario) triangolato con bmesh; uvf(x, y) -> (u, v) opzionale."""
    vs = [bm.verts.new((x, y, z)) for x, y in pts]
    f = bm.faces.new(vs)
    f.material_index = mi
    res = bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
    faces = res["faces"]
    if uvf is not None:
        layer = bm.loops.layers.uv.verify()
        for fc in faces:
            for lp in fc.loops:
                lp[layer].uv = uvf(lp.vert.co.x, lp.vert.co.y)
    return faces


def _strip(xl, xr, y0, y1, n=1):
    """Quadrilatero fra due bordi lineari: xl/xr = (x a y0, x a y1). Ritorna i vertici XY antiorari."""
    return [(xl[0], y0), (xr[0], y0), (xr[1], y1), (xl[1], y1)]


def _lerp_x(p, q, y):
    return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])


def _skirt(bm, a, b, z1, z0, mi):
    f = pk._quad(bm, [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], mi)
    return f


# =============================================================================================================
# suolo: strada, masselli, angolo in cubetti
# =============================================================================================================
MOLO_E = ((6.8, -79.4), (9.99, 62.0))       # ciglio est del molo (blockout, da OSM)
MOLO_E2 = ((10.2, 71.4), (9.75, 88.45))     # radice del molo verso la banchina
MOLO_W = ((-12.1, 42.2), (-12.3, -89.8))    # ciglio ovest
FAC_A = ((0.3, 79.9), (0.6, 102.6))         # facciata di A1/A2 (OSM)
A_BACK = ((-6.3, 62.0), (-5.7, 102.6))      # muro posteriore di A
C_RECT = (-12.1, -7.6, 24.8, 42.2)          # edificio C (x0, x1, y0, y1), facciata est a X -7,5/-7,7


def _east(y):
    return _lerp_x(*MOLO_E, y) if y <= 62.0 else (_lerp_x((9.99, 62.0), (10.2, 71.4), y) if y <= 71.4 else _lerp_x(*MOLO_E2, y))


def _corner_arc(n=10):
    """Spigolo arrotondato NE di A1: quarto d'ellisse tangente alla facciata (0,6; 102,6) e al muro nord (-4,1; 106,9)."""
    cx, cy, ax, ay = -4.1, 102.6, 4.7, 4.3
    return [(cx + ax * math.cos(math.pi / 2 * k / n), cy + ay * math.sin(math.pi / 2 * k / n)) for k in range(n + 1)]


def build_strada(coll, name="SM_Molo_Pav_Strada"):
    bm = bmesh.new()
    z = Z_MOLO
    R = R_ANG
    yc = Y_ANG1 - R
    # carreggiata principale X 6-9,55, Y 86-121 (spezzata per condividere i vertici col ramo)
    ys = [Y_STR0, yc, Y_RAMO0, Y_RAMO1, Y_STR1]
    for a, b in zip(ys[:-1], ys[1:]):
        pk._quad(bm, [(X_STR0, a, z), (X_CURB0, a, z), (X_CURB0, b, z), (X_STR0, b, z)], 0)
    # spicchio d'angolo fra la curva del cordolo e lo spigolo vivo (9,55; 109,25)
    cx = X_CURB0 + R
    arc = [(cx - R * math.cos(math.pi / 2 * k / 8), yc + R * math.sin(math.pi / 2 * k / 8)) for k in range(9)]
    corner = bm.verts.new((X_CURB0, Y_ANG1, z))
    av = [bm.verts.new((x, y, z)) for x, y in arc]
    for p, q in zip(av[:-1], av[1:]):
        bm.faces.new([corner, p, q]).material_index = 0
    # ramo verso est
    pk._quad(bm, [(X_CURB0, Y_RAMO0, z), (X_RAMO1, Y_RAMO0, z), (X_RAMO1, Y_RAMO1, z), (X_CURB0, Y_RAMO1, z)], 0)
    # cordolo lato nord del ramo (pietra chiara, h 15 cm, largo 0,20)
    pk._box(bm, X_CURB0 + 0.6, X_RAMO1, Y_RAMO1, Y_RAMO1 + 0.20, ZB, ZF, 1, faces=("top", "yn", "yp", "xn", "xp"))
    # bordi verticali dove non c'e' altro suolo
    _skirt(bm, (X_CURB0, Y_STR1), (X_STR0, Y_STR1), z, ZB, 0)
    _skirt(bm, (X_RAMO1, Y_RAMO0), (X_RAMO1, Y_RAMO1), z, ZB, 0)
    # orientamento esplicito delle facce (niente recalc: mesh aperta)
    o = pk._finish(name, bm, ["M_Molo_Asfalto", "M_Pav_Fascia"], coll)
    pk._ucx(name, [(X_STR0, X_CURB0, Y_STR0, Y_STR1, -0.30, Z_MOLO),
                   (X_CURB0, X_RAMO1, Y_RAMO0, Y_RAMO1, -0.30, Z_MOLO),
                   (X_CURB0 + 0.6, X_RAMO1, Y_RAMO1, Y_RAMO1 + 0.20, -0.30, ZF)], coll)
    return o


def _masselli_regions():
    """Moduli dei masselli (poligoni XY antiorari). 01 = radice e fronte dei ristoranti, 02 = Y 31-62, 03 = Y 0-31."""
    z = {}
    fa = lambda y: _lerp_x(*FAC_A, y)
    r01 = []
    r01.append(_strip((0.1, 0.2), (_east(62.0), _east(68.1)), 62.0, 68.1))
    r01.append(_strip((1.2, 1.2), (_east(68.1), _east(71.4)), 68.1, 71.4))
    r01.append(_strip((1.2, 1.4), (_east(71.4), _east(79.9)), 71.4, 79.9))
    r01.append(_strip((fa(79.9), fa(Y_STR0)), (_east(79.9), _east(Y_STR0)), 79.9, Y_STR0))
    r01.append(_strip((fa(Y_STR0), fa(89.15)), (X_STR0, X_STR0), Y_STR0, 89.15))
    r01.append([(X_CURB0, Y_STR0), (_east(Y_STR0), Y_STR0), (_east(88.45), 88.45), (X_CURB0, 88.45)])
    r01.append([(X_CURB0, 88.45), (X_CURB1, 88.45), (X_CURB1, 89.15), (X_CURB0, 89.15)])
    r01.append(_strip((fa(89.15), 0.6), (X_STR0, X_STR0), 89.15, 102.6))
    r01.append(("ARC", [(-4.1, 102.6), (X_STR0, 102.6), (X_STR0, 106.9), (-4.1, 106.9)]))
    r01.append([(-8.1, 106.9), (X_STR0, 106.9), (X_STR0, Y_STR1), (-8.1, Y_STR1)])
    z["SM_Molo_Pav_Masselli_01"] = r01
    w2 = ((-12.1, 42.2), (-6.3, 62.0))
    z["SM_Molo_Pav_Masselli_02"] = [
        _strip((-7.6, -7.6), (_east(31.0), _east(42.2)), 31.0, 42.2),
        _strip((-12.1, -6.3), (_east(42.2), _east(62.0)), 42.2, 62.0),
    ]
    xw = lambda y: _lerp_x(*MOLO_W, y)
    z["SM_Molo_Pav_Masselli_03"] = [
        _strip((xw(0.0), xw(24.8)), (_east(0.0), _east(24.8)), 0.0, 24.8),
        _strip((-7.5, -7.6), (_east(24.8), _east(31.0)), 24.8, 31.0),
    ]
    return z


def build_masselli(coll):
    out = []
    for name, regs in _masselli_regions().items():
        bm = bmesh.new()
        for pts in regs:
            if pts[0] == "ARC":      # spicchio attorno allo spigolo curvo: ventaglio
                arc = _corner_arc(10)
                apex = bm.verts.new((X_STR0, 106.9, Z_MOLO))
                av = [bm.verts.new((x, y, Z_MOLO)) for x, y in arc]
                b = bm.verts.new((X_STR0, 102.6, Z_MOLO))
                bm.faces.new([av[0], b, apex])
                for p, q in zip(av[:-1], av[1:]):
                    bm.faces.new([q, p, apex])
                continue
            _poly_fill(bm, pts, Z_MOLO, 0)
        pk._recalc(bm)
        for f in bm.faces:          # tutte verso l'alto
            if f.normal.z < 0:
                f.normal_flip()
        o = pk._finish(name, bm, ["M_Molo_Masselli_Grigio" if name.endswith("_01") else "M_Molo_Masselli"], coll)
        # collisione: un box per regione (inviluppo), sottile, sotto la superficie
        boxes = []
        for pts in regs:
            if pts[0] == "ARC":
                pts = pts[1]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            boxes.append((min(xs), max(xs), min(ys), max(ys), -0.30, Z_MOLO))
        pk._ucx(name, boxes, coll)
        out.append(o)
    return out


def build_angolo(coll, name="SM_Pav_AngoloMolo"):
    """Angolo in cubetti fra la strada e la fascia palme: cordolo X 9,55-9,75 da Y 89,15 alla curva (raggio 1,6 m)
    e lungo Y 109,05-109,25 fino a X 20; cubetti a Z +0,15 in X 9,75-20, Y 102-109,05 (la fascia palme copre Y < 102)."""
    bm = bmesh.new()
    R = R_ANG
    W = X_CURB1 - X_CURB0
    cx, cy = X_CURB0 + R, Y_ANG1 - R
    n = 10
    c = 0.015
    outer = [(cx - R * math.cos(math.pi / 2 * k / n), cy + R * math.sin(math.pi / 2 * k / n)) for k in range(n + 1)]
    inner = [(cx - (R - W) * math.cos(math.pi / 2 * k / n), cy + (R - W) * math.sin(math.pi / 2 * k / n)) for k in range(n + 1)]
    path_o = [(X_CURB0, 89.15)] + outer + [(X_ANG1, Y_ANG1)]
    path_i = [(X_CURB1, 89.15)] + inner + [(X_ANG1, Y_ANG1 - W)]
    # cordolo: faccia a vista sull'asfalto (Z_MOLO -> ZF - smusso), smusso, piano superiore
    vo_lo = [bm.verts.new((x, y, ZB)) for x, y in path_o]
    vo_hi = [bm.verts.new((x, y, ZF - c)) for x, y in path_o]
    path_c = [(x + (xi - x) * c / W, y + (yi - y) * c / W) for (x, y), (xi, yi) in zip(path_o, path_i)]
    vc = [bm.verts.new((x, y, ZF)) for x, y in path_c]
    vi = [bm.verts.new((x, y, ZF)) for x, y in path_i]
    for i in range(len(path_o) - 1):
        bm.faces.new([vo_lo[i + 1], vo_lo[i], vo_hi[i], vo_hi[i + 1]]).material_index = 1
        bm.faces.new([vo_hi[i + 1], vo_hi[i], vc[i], vc[i + 1]]).material_index = 1
        bm.faces.new([vc[i + 1], vc[i], vi[i], vi[i + 1]]).material_index = 1
    # testate del cordolo
    bm.faces.new([bm.verts.new((X_CURB1, 89.15, ZB)), vi[0], vc[0], vo_hi[0], vo_lo[0]]).material_index = 1
    bm.faces.new([vo_hi[-1], vc[-1], vi[-1], bm.verts.new((X_ANG1, Y_ANG1 - W, ZB)), vo_lo[-1]]).material_index = 1
    # cubetti: dal bordo interno del cordolo (tratto Y >= 102) a X 20
    pts = [(X_CURB1, 102.0), (X_ANG1, 102.0), (X_ANG1, Y_ANG1 - W)] + [p for p in inner[::-1]]
    pts = [p for p in pts if p[1] >= 102.0 - 1e-6]
    if pts[-1][0] > X_CURB1 + 1e-6:
        pts.append((X_CURB1, max(102.0, cy)))
    _poly_fill(bm, pts, ZF, 0)
    # bordo est (X 20) fino alla quota del blockout ribassato
    _skirt(bm, (X_ANG1, 102.0), (X_ANG1, Y_ANG1 - W), ZF, ZB, 1)
    # orientamento esplicito delle facce (niente recalc: mesh aperta)
    o = pk._finish(name, bm, ["M_Pav_Cubetti", "M_Pav_Fascia"], coll)
    pk._ucx(name, [(X_CURB0, X_CURB1, 89.15, cy, -0.30, ZF),
                   (X_CURB0 + 0.3, X_ANG1, 102.0, Y_ANG1, -0.30, ZF),
                   (X_CURB0, X_CURB1 + 0.3, cy - 0.01, Y_ANG1 - 0.3, -0.30, ZF)], coll)
    return o


# =============================================================================================================
# edifici (pianta OSM, scheda §3). Poligoni in senso antiorario visti dall'alto; UV sull'atlante facciate.
# =============================================================================================================
def _auv(u, base, h):
    return (u / 8.0, (base + h) / 8.0)


def _offset_poly(poly, d):
    """Offset verso l'esterno (poligono antiorario) con raccordo a spigolo vivo (miter)."""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e0 = (p1 - p0).normalized(); e1 = (p2 - p1).normalized()
        n0 = Vector((e0.y, -e0.x)); n1 = Vector((e1.y, -e1.x))
        m = (n0 + n1)
        if m.length < 1e-6:
            m = n0
        m.normalize()
        k = d / max(m.dot(n0), 0.3)
        out.append(tuple(p1 + m * k))
    return out


def _fit_segs(segs, length):
    """Adatta la lista (chiave, lunghezza) alla lunghezza del muro allungando i tratti lisci; spezza i lisci lunghi."""
    fixed = sum(L for k, L in segs if not k.endswith("liscio"))
    plain = sum(L for k, L in segs if k.endswith("liscio"))
    if plain > 1e-6:
        s = max(length - fixed, 0.05) / plain
        segs = [(k, L * s if k.endswith("liscio") else L) for k, L in segs]
    else:
        s = length / max(fixed, 1e-6)
        segs = [(k, L * s) for k, L in segs]
    out = []
    for k, L in segs:
        if k.endswith("liscio"):
            u0, u1, _ = SEG[k]
            mx = 2.2 * (u1 - u0)
            nn = max(1, int(math.ceil(L / mx - 1e-6)))
            out += [(k, L / nn)] * nn
        else:
            out.append((k, L))
    return out


def _wall_edge(bm, layer, p0, p1, segs, z0, z1, h_map=None, mi=0):
    """Muro sul lato p0->p1 da z0 a z1, a tratti secondo `segs`. h_map(z) -> quota nell'atlante (default z)."""
    p0, p1 = Vector(p0), Vector(p1)
    L = (p1 - p0).length
    d = (p1 - p0) / L
    s = 0.0
    hm = h_map or (lambda z: z)
    faces = []
    for k, l in _fit_segs(segs, L):
        a = p0 + d * s
        b = p0 + d * (s + l)
        u0, u1, base = SEG[k]
        _wall_piece(bm, layer, a, b, z0, z1, u0, u1, base, k, hm, mi)
        s += l
    return faces


def _trim_uv(v0, v1):
    return lambda u, t: (u / 8.0, (v0 + (v1 - v0) * t) / 8.0)


def _cornice(bm, layer, poly, z0, z1, prot, kind="cornicione", roof=True, closed=True):
    """Cornicione/bordo del tetto: fascia esterna (offset `prot`) da z0 a z1, sottogronda a z0, tetto a z1."""
    off = _offset_poly(poly, prot)
    n = len(poly)
    v0, v1 = TRIM[kind]
    c0, c1 = TRIM["cornice_bianca"]
    per = 0.0
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        a, b = Vector(off[i]), Vector(off[j])
        L = (b - a).length
        f = pk._quad(bm, [(a.x, a.y, z0), (b.x, b.y, z0), (b.x, b.y, z1), (a.x, a.y, z1)], 0)
        _uv_set(f, [(per / 8, v0 / 8), ((per + L) / 8, v0 / 8), ((per + L) / 8, v1 / 8), (per / 8, v1 / 8)], layer)
        # sottogronda
        w0, w1 = poly[i], poly[j]
        f = pk._quad(bm, [(w0[0], w0[1], z0), (w1[0], w1[1], z0), (b.x, b.y, z0), (a.x, a.y, z0)], 0)   # verso il basso
        _uv_set(f, [(per / 8, (c0 + 0.02) / 8), ((per + L) / 8, (c0 + 0.02) / 8), ((per + L) / 8, (c1 - 0.02) / 8),
                    (per / 8, (c1 - 0.02) / 8)], layer)
        per += L
    if roof:
        xs = [p[0] for p in off]; ys = [p[1] for p in off]
        y0, y1 = min(ys), max(ys)
        t0, t1 = TRIM["tetto"]
        _poly_fill(bm, off, z1, 0, uvf=lambda x, y: (x / 8.0, (t0 + 0.01 + (t1 - t0 - 0.02) * (y - y0) / max(y1 - y0, 1e-3)) / 8.0))
    return off


def _box_uv(bm, layer, x0, x1, y0, y1, z0, z1, uv_rect, mat=None):
    """Box con tutte le facce mappate nello stesso rettangolo UV (u0, v0, u1, v1) dell'atlante (metri)."""
    fs = pk._box(bm, x0, x1, y0, y1, z0, z1, 0, mat=mat)
    u0, v0, u1, v1 = uv_rect
    for f in fs:
        _uv_set(f, [(u0 / 8, v0 / 8), (u1 / 8, v0 / 8), (u1 / 8, v1 / 8), (u0 / 8, v1 / 8)], layer)
    return fs


UV_METAL = (4.2, 0.02, 7.8, 0.13)
UV_VERNICE = (0.2, 0.02, 3.8, 0.13)
UV_TENDA = (0.0, 0.42, 8.0, 0.73)
UV_TETTO = (0.0, 0.17, 8.0, 0.38)


def _tenda(bm, layer, p0, p1, z_top, depth, drop, lod=0):
    """Tenda da sole avvolgibile crema: cassonetto, telo inclinato (sopra e sotto) e mantovana."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    nrm = Vector((d.y, -d.x))
    L = (p1 - p0).length
    a0, a1 = p0 + nrm * 0.02, p1 + nrm * 0.02
    b0, b1 = p0 + nrm * depth, p1 + nrm * depth
    zt, zb = z_top, z_top - drop
    u0, v0, u1, v1 = UV_TENDA
    top = pk._quad(bm, [(a0.x, a0.y, zt), (b0.x, b0.y, zb), (b1.x, b1.y, zb), (a1.x, a1.y, zt)], 0)
    _uv_set(top, [(0, v1 / 8), (0, v0 / 8), (L / 8, v0 / 8), (L / 8, v1 / 8)], layer)
    bot = pk._quad(bm, [(a0.x, a0.y, zt - 0.01), (a1.x, a1.y, zt - 0.01), (b1.x, b1.y, zb - 0.01), (b0.x, b0.y, zb - 0.01)], 0)
    _uv_set(bot, [(0, v1 / 8), (L / 8, v1 / 8), (L / 8, v0 / 8), (0, v0 / 8)], layer)
    if lod < 2:
        val = pk._quad(bm, [(b0.x, b0.y, zb - 0.22), (b1.x, b1.y, zb - 0.22), (b1.x, b1.y, zb), (b0.x, b0.y, zb)], 0)
        _uv_set(val, [(0, v0 / 8), (L / 8, v0 / 8), (L / 8, (v0 + 0.2) / 8), (0, (v0 + 0.2) / 8)], layer)
        # cassonetto: box allineato al muro
        fr = Matrix(((d.x, -d.y, 0, p0.x), (d.y, d.x, 0, p0.y), (0, 0, 1, 0), (0, 0, 0, 1)))   # colonne: lungo, verso l'interno
        _box_uv(bm, layer, 0, L, -0.2, 0.0, zt, zt + 0.2, (0.2, 0.43, 7.8, 0.72), mat=fr)


def _ac_units(bm, layer, spots, z):
    for x, y, w, dd, h in spots:
        _box_uv(bm, layer, x - w / 2, x + w / 2, y - dd / 2, y + dd / 2, z, z + h, UV_METAL)


def _ringhiera(bm, layer, poly, z, h=0.95, step=1.2, closed=True, lod=0):
    n = len(poly)
    for i in (range(n) if closed else range(n - 1)):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        L = (b - a).length
        d = (b - a) / L
        nrm = Vector((d.y, -d.x))
        fr = Matrix(((d.x, -d.y, 0, a.x), (d.y, d.x, 0, a.y), (0, 0, 1, 0), (0, 0, 0, 1)))
        _box_uv(bm, layer, 0, L, -0.03, 0.03, z + h - 0.05, z + h, UV_VERNICE, mat=fr)           # corrimano
        if lod < 2:
            _box_uv(bm, layer, 0, L, -0.015, 0.015, z + 0.12, z + 0.16, UV_VERNICE, mat=fr)      # traverso basso
        k = max(1, int(round(L / step)))
        for j in range(k + (0 if closed else 1)):
            s = L * j / k
            _box_uv(bm, layer, s - 0.025, s + 0.025, -0.025, 0.025, z, z + h - 0.05, UV_VERNICE, mat=fr)
        if lod < 2:   # bacchette verticali fitte (LOD1: una su due)
            m = int(L / (0.13 if lod == 0 else 0.26))
            for j in range(1, m):
                s = L * j / m
                if min(abs(s - L * q / k) for q in range(k + 1)) < 0.06:
                    continue
                _box_uv(bm, layer, s - 0.008, s + 0.008, -0.008, 0.008, z + 0.16, z + h - 0.05, UV_VERNICE, mat=fr)


def _building(name, coll, poly, walls, z_wall, cornice, extras=None, lod=0, upper=None):
    """walls: per ogni lato i (poly[i] -> poly[i+1]) una lista di tratti (chiave, m) oppure None (muro nascosto).
    Un lato puo' essere ((t0, t1), tratti) per costruire solo la parte da t0 a t1 (metri dall'inizio del lato).
    upper: (z0, z1, chiave_liscia) fascia di muro sopra 3,4 m mappata sul liscio.
    cornice: (z0, z1, sporto, tipo)."""
    bm = bmesh.new()
    _DET["lod"] = lod
    layer = bm.loops.layers.uv.verify()
    n = len(poly)
    for i in range(n):
        spec = walls[i]
        if spec is None:
            continue
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        if isinstance(spec, tuple):
            (t0, t1), segs = spec
            d = (b - a).normalized()
            a, b = a + d * t0, a + d * t1
        else:
            segs = spec
        if lod == 2:   # LOD2: un solo tratto liscio per lato, colore del primo tratto
            k0 = segs[0][0]
            plain = {"G": "G_liscio", "P": "P_liscio", "Y": "Y_liscio", "W": "W_liscio"}[k0[0]]
            segs = [(plain, 1.0)]
            seglist = [(plain, (b - a).length)]
            u0, u1, base = SEG[plain]
            f = pk._quad(bm, [(a.x, a.y, 0), (b.x, b.y, 0), (b.x, b.y, z_wall), (a.x, a.y, z_wall)], 0)
            _uv_set(f, [_auv(u0, base, 0.3), _auv(u1, base, 0.3), _auv(u1, base, min(z_wall, 3.4)), _auv(u0, base, min(z_wall, 3.4))], layer)
        else:
            _wall_edge(bm, layer, a, b, segs, 0.0, min(z_wall, WALL_H), mi=0)
        if upper is not None and z_wall > WALL_H:
            _wall_edge(bm, layer, a, b, [(upper, 1.0)], WALL_H, z_wall, h_map=lambda z: 2.4 + (z - WALL_H), mi=0)
    z0, z1, prot, kind = cornice
    if kind == "cornicione" and lod == 0:
        # v2: cornicione a due gradini: cornice bianca (sporto 7 cm) e fascia rosso-bruna piu' sporgente
        _cornice(bm, layer, poly, z0, z0 + 0.12, 0.07, kind="cornice_bianca", roof=False)
        off = _cornice(bm, layer, poly, z0 + 0.12, z1, prot, kind="cornicione_rosso")
    else:
        off = _cornice(bm, layer, poly, z0, z1, prot if lod < 2 else 0.0, kind=kind)
    if extras:
        extras(bm, layer, lod)
    # orientamento esplicito delle facce (niente recalc: mesh aperta)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = pk._finish(name + sfx, bm, ["M_Molo_Facciate"], coll, uv=None)
    return o, off


def _ucx_poly(name, poly, z1, coll, idx=0):
    """Collisione: inviluppo convesso del prisma della pianta (poligono convesso o quasi)."""
    pts = [(x, y, z) for x, y in poly for z in (0.0, z1)]
    pk._ucx_hull(name, idx, pts, coll)


# --- muro su una polilinea (arco dello spigolo) con i tratti dell'atlante continui sugli spigoli --------------
def _wall_polyline(bm, layer, pts, segs, z0, z1, mi=0):
    P = [Vector(p) for p in pts]
    cum = [0.0]
    for a, b in zip(P[:-1], P[1:]):
        cum.append(cum[-1] + (b - a).length)
    total = cum[-1]
    fs = _fit_segs(segs, total)
    bounds = [0.0]
    for k, l in fs:
        bounds.append(bounds[-1] + l)
    cuts = sorted(set([round(c, 6) for c in cum] + [round(b, 6) for b in bounds]))

    def at(s):
        for i in range(len(P) - 1):
            if s <= cum[i + 1] + 1e-9:
                t = (s - cum[i]) / max(cum[i + 1] - cum[i], 1e-9)
                return P[i] + (P[i + 1] - P[i]) * t
        return P[-1]

    for s0, s1 in zip(cuts[:-1], cuts[1:]):
        if s1 - s0 < 1e-5:
            continue
        sm = (s0 + s1) / 2
        j = max(i for i in range(len(fs)) if bounds[i] <= sm + 1e-9)
        k, l = fs[j]
        u0, u1, base = SEG[k]
        ua = u0 + (u1 - u0) * (s0 - bounds[j]) / l
        ub = u0 + (u1 - u0) * (s1 - bounds[j]) / l
        a, b = at(s0), at(s1)
        _wall_piece(bm, layer, a, b, z0, z1, ua, ub, base, k, (lambda z: z), mi)
    return total


def _polyline_at(pts, s):
    P = [Vector(p) for p in pts]
    acc = 0.0
    for a, b in zip(P[:-1], P[1:]):
        L = (b - a).length
        if s <= acc + L:
            return a + (b - a) * ((s - acc) / L)
        acc += L
    return P[-1]


# --- A1 + A2: ristorante d'angolo (giallo, spigolo arrotondato) + pescheria (rosa) -------------------------
# Revisione dopo il confronto con F1/F2 (vedi ref/radice_molo.md §10): la parte rosa e' l'ultimo tratto piatto della
# facciata est prima della curva; il muro giallo con lo scudo, la tenda e la porta-finestra e' sull'arco; la porta
# singola sul muro nord. A3 (bianco e giallo) arriva fino a Y 98,8.
Y_A3_A2 = 98.8
ARC_N = 12


def _poly_A1A2(n_arc=None):
    fa = lambda y: _lerp_x(*FAC_A, y)
    bk = lambda y: _lerp_x(*A_BACK, y)
    arc = _corner_arc(n_arc or ARC_N)
    return [(bk(Y_A3_A2), Y_A3_A2), (fa(Y_A3_A2), Y_A3_A2)] + arc + [(-7.9, 106.7), (-7.9, 102.7), (-5.7, 102.6)]


A1_CURVE_SEGS = [("G_liscio", 0.35), ("G_scudo", 2.0), ("G_liscio", 0.5), ("G_portafin", 2.5), ("G_liscio", 0.6),
                 ("G_liscio", 0.6), ("G_porta", 1.5), ("G_liscio", 0.5), ("G_liscio", 0.5)]


def build_A1A2(coll, lod=0, name="SM_Molo_Edificio_A1A2"):
    n_arc = (ARC_N, 6, 4)[lod]                                                       # v2: arco piu' rado nei LOD
    poly = _poly_A1A2(n_arc)
    n = len(poly)
    walls = [None] * n
    walls[0] = [("G_liscio", 1.0)]                                                  # muro sud (sopra il tetto di A3)
    walls[1] = [("P_liscio", 0.6), ("P_finestra", 2.0), ("P_liscio", 0.6)]           # A2 rosa, Y 98,8-102,6
    for i in (n - 3, n - 2, n - 1):                                                 # rientro nord-ovest e retro
        walls[i] = [("G_liscio", 1.0)]
    curve = poly[2:2 + n_arc + 1] + [(-7.9, 106.7)]                                 # arco + muro nord
    zc0, zc1 = 3.35, 3.80

    def extras(bm, layer, lod):
        if lod < 2:
            _wall_polyline(bm, layer, curve, A1_CURVE_SEGS, 0.0, zc0)
        else:
            pts = curve[::3] if (len(curve) - 1) % 3 == 0 else curve[::3] + [curve[-1]]
            _wall_polyline(bm, layer, pts, [("G_liscio", 1.0)], 0.0, zc0)
        if lod < 2:
            # tenda crema sopra la porta-finestra (sull'arco: due tratti di corda)
            L = sum((Vector(b) - Vector(a)).length for a, b in zip(curve[:-1], curve[1:]))
            fs = _fit_segs(A1_CURVE_SEGS, L)
            s = 0.0
            for k, l in fs:
                if k == "G_portafin":
                    s0, s1 = s - 0.15, s + l + 0.15
                    break
                s += l
            q = [_polyline_at(curve, s0 + (s1 - s0) * t) for t in (0, 0.5, 1)]
            for a, b in zip(q[:-1], q[1:]):
                _tenda(bm, layer, tuple(a), tuple(b), 3.05, 1.1, 0.36, lod)
            # tendina sopra la finestra rosa
            fa = lambda y: _lerp_x(*FAC_A, y)
            _tenda(bm, layer, (fa(Y_A3_A2 + 1.1), Y_A3_A2 + 1.1), (fa(Y_A3_A2 + 2.7), Y_A3_A2 + 2.7), 2.95, 0.4, 0.22, lod)
        if lod == 0:
            _ac_units(bm, layer, [(-1.6, 103.0, 1.3, 0.75, 0.85), (-3.3, 103.4, 1.0, 0.7, 0.75),
                                  (-2.6, 100.6, 1.1, 0.8, 0.7)], zc1)
    o, off = _building(name, coll, poly, walls, zc0, (zc0, zc1, 0.18, "cornicione"), extras, lod)
    if lod == 0:
        fa = lambda y: _lerp_x(*FAC_A, y)
        bk = lambda y: _lerp_x(*A_BACK, y)
        _ucx_poly(name, [(bk(Y_A3_A2), Y_A3_A2), (fa(Y_A3_A2), Y_A3_A2), (0.6, 102.6), (-5.7, 102.6)], zc1, coll, 0)
        _ucx_poly(name, [(-5.7, 102.6)] + _corner_arc(6) + [(-5.7, 106.85)], zc1, coll, 1)
        _ucx_poly(name, [(-7.9, 102.7), (-5.6, 102.6), (-5.6, 106.85), (-7.9, 106.7)], zc1, coll, 2)
    return o


# --- A3: sezione gialla (Y 68-79,9) e bianca con vetrate (Y 79,9-98,8) -----------------------------------
def _poly_A3():
    fa = lambda y: _lerp_x(*FAC_A, y)
    bk = lambda y: _lerp_x(*A_BACK, y)
    return [(bk(68.0), 68.0), (1.2, 68.0), (1.4, 79.9), (0.3, 79.9), (fa(Y_A3_A2), Y_A3_A2), (bk(Y_A3_A2), Y_A3_A2)]


def build_A3(coll, lod=0, name="SM_Molo_Edificio_A3"):
    poly = _poly_A3()
    L0 = (Vector(poly[1]) - Vector(poly[0])).length
    walls = [((L0 - 1.0, L0), [("Y_liscio", 1.0)]),                                   # moncone sud (oltre A4)
             [("Y_liscio", 0.9), ("Y_finestrella", 2.0), ("Y_liscio", 0.5), ("Y_finestrella", 2.0), ("Y_liscio", 0.5),
              ("Y_finestrella", 2.0), ("Y_liscio", 0.9), ("Y_liscio", 0.9)],          # Y 68-79,9: giallo
             [("WY_liscio", 1.0)],                                                          # risvolto a Y 79,9
             [("WY_liscio", 0.9), ("W_vetrata", 2.0), ("WY_liscio", 0.9), ("WY_liscio", 0.9), ("W_vetrata", 2.0),
              ("WY_liscio", 0.9), ("W_vetrata", 2.0), ("WY_liscio", 0.9), ("WY_liscio", 0.9), ("W_vetrata", 2.0),
              ("WY_liscio", 0.9), ("WY_liscio", 0.9)],                                      # Y 79,9-98,8: bianco
             None,                                                                          # lato nord: muro di A1A2
             [("Y_liscio", 1.0)]]                                                           # retro
    zc0, zc1 = 3.15, 3.40

    def extras(bm, layer, lod):
        if lod == 0:
            _ac_units(bm, layer, [(-2.5, 75.0, 1.0, 0.7, 0.7), (-3.0, 92.0, 1.1, 0.7, 0.75)], zc1)
    o, off = _building(name, coll, poly, walls, zc0, (zc0, zc1, 0.06, "cornice_bianca"), extras, lod)
    if lod == 0:
        _ucx_poly(name, [poly[0], poly[1], poly[2], (poly[5][0] + 0.4, 79.9)], zc1, coll, 0)
        _ucx_poly(name, [(poly[5][0] + 0.2, 79.9), (0.3, 79.9), poly[4], poly[5]], zc1, coll, 1)
    return o


# --- A4/A5: blocco sud con terrazza e ringhiera (Y 62-68), facciata bianca verso il ponte ------------------
def _poly_A4():
    bk = lambda y: _lerp_x(*A_BACK, y)
    return [(-6.3, 62.0), (0.1, 62.1), (0.2, 68.0), (bk(68.0), 68.0)]


def build_A4A5(coll, lod=0, name="SM_Molo_Edificio_A4A5"):
    poly = _poly_A4()
    walls = [[("W_liscio", 0.6), ("W_grata", 2.0), ("W_liscio", 1.2), ("W_grata", 2.0), ("W_liscio", 0.6)],   # sud
             [("W_porta", 2.0), ("W_porta", 2.0), ("W_porta", 2.0)],                                          # est
             [("W_liscio", 1.0)], [("W_liscio", 1.0)]]
    zw, zc0, zc1 = 3.9, 3.9, 4.02

    def extras(bm, layer, lod):
        inner = _offset_poly(poly, -0.05)
        _ringhiera(bm, layer, inner, zc1, 0.95, 1.3, True, lod)
        if lod == 0:
            _ac_units(bm, layer, [(-3.8, 66.5, 1.1, 0.7, 0.75)], zc1)
    o, off = _building(name, coll, poly, walls, zw, (zc0, zc1, 0.06, "cornice_bianca"), extras, lod, upper="W_liscio")
    if lod == 0:
        _ucx_poly(name, poly, zc1 + 0.95, coll, 0)
    return o


# --- C: casa/ristorante sul molo (Y 24,8-42,2) --------------------------------------------------------------
def _poly_C():
    return [(-12.1, 24.8), (-7.5, 24.8), (-7.7, 42.2), (-12.1, 42.2)]


def build_C(coll, lod=0, name="SM_Molo_Edificio_C"):
    poly = _poly_C()
    walls = [[("W_liscio", 1.0)],
             [("W_liscio", 1.0), ("W_grata", 2.0), ("W_liscio", 2.0), ("W_grata", 2.0), ("W_liscio", 2.0), ("W_grata", 2.0),
              ("W_liscio", 2.0), ("W_grata", 2.0), ("W_liscio", 1.0)],   # F3: bianco, finestre con grata, niente porte rosse
             [("W_liscio", 1.2), ("W_grata", 2.0), ("W_liscio", 1.2)],
             [("W_liscio", 1.0)]]
    zw, zc0, zc1 = 3.75, 3.75, 3.87

    def extras(bm, layer, lod):
        if lod == 0:
            _ac_units(bm, layer, [(-10.0, 30.0, 1.1, 0.7, 0.75), (-10.2, 38.0, 1.0, 0.7, 0.7)], zc1)
    o, off = _building(name, coll, poly, walls, zw, (zc0, zc1, 0.08, "cornice_bianca"), extras, lod, upper="W_liscio")
    if lod == 0:
        _ucx_poly(name, poly, zc1, coll, 0)
    return o


# --- B: tendone/pergola scura a nord del ristorante d'angolo --------------------------------------------------
def build_tendone(coll, lod=0, name="SM_Molo_Tendone"):
    """Pergola metallica 8,6 x 5,3 m (pianta OSM B) con telo scuro a una falda: alto 3,1 m sul lato ovest, 2,6 m a est."""
    x0, x1, y0, y1 = -8.1, 0.5, 111.4, 116.7
    zw, ze = 3.1, 2.6
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    s = 0.06 if lod < 2 else 0.08
    zt = lambda x: zw + (ze - zw) * (x - x0) / (x1 - x0)
    posts = [(x, y) for x in (x0 + 0.1, (x0 + x1) / 2, x1 - 0.1) for y in (y0 + 0.1, y1 - 0.1)]
    for x, y in posts:
        _box_uv(bm, layer, x - s, x + s, y - s, y + s, 0.0, zt(x) - 0.02, UV_METAL)
    if lod < 2:   # travi longitudinali
        for y in (y0 + 0.1, y1 - 0.1):
            a, b = Vector((x0, y, zt(x0) - 0.1)), Vector((x1, y, zt(x1) - 0.1))
            pk._tube(bm, [a, b], 0.05, 4, 0)
    # telo: lastra sottile inclinata con orlo
    t = 0.03
    ov = 0.25
    pts = [(x0 - ov, y0 - ov), (x1 + ov, y0 - ov), (x1 + ov, y1 + ov), (x0 - ov, y1 + ov)]
    top = [bm.verts.new((x, y, zt(x) + t)) for x, y in pts]
    bot = [bm.verts.new((x, y, zt(x))) for x, y in pts]
    ft = bm.faces.new(top)
    fb = bm.faces.new(bot[::-1])
    u0, v0, u1, v1 = UV_TETTO
    for f in (ft, fb):
        for lp in f.loops:
            lp[layer].uv = ((lp.vert.co.y - y0) / 8.0, (v0 + (v1 - v0) * (lp.vert.co.x - x0 + ov) / (x1 - x0 + 2 * ov)) / 8.0)
    for i in range(4):   # orlo / mantovana
        j = (i + 1) % 4
        drop = 0.25 if lod < 2 else t
        f = bm.faces.new([bm.verts.new((pts[i][0], pts[i][1], zt(pts[i][0]) - drop)),
                          bm.verts.new((pts[j][0], pts[j][1], zt(pts[j][0]) - drop)), top[j], top[i]])
        _uv_set(f, [(0, v0 / 8), (2 / 8, v0 / 8), (2 / 8, (v0 + 0.1) / 8), (0, (v0 + 0.1) / 8)], layer)
    # tende laterali arrotolate sul lato nord (a est in F1), solo LOD0
    if lod == 0:
        pk._tube(bm, [(x0, y1 + ov - 0.05, zt(x0) - 0.35), (x1, y1 + ov - 0.05, zt(x1) - 0.35)], 0.07, 6, 0)
    # orientamento esplicito delle facce (niente recalc: mesh aperta)
    for f in bm.faces:
        if not f.loops[0][layer].uv.length:
            for lp in f.loops:
                lp[layer].uv = (UV_METAL[0] / 8 + 0.01, UV_METAL[1] / 8 + 0.005)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = pk._finish(name + sfx, bm, ["M_Molo_Facciate"], coll, uv=None)
    if lod == 0:
        boxes = [(x - s, x + s, y - s, y + s, 0.0, zt(x)) for x, y in posts]
        boxes.append((x0 - ov, x1 + ov, y0 - ov, y1 + ov, ze - 0.25, zw + t))
        pk._ucx(name, boxes, coll)
    return o


# =============================================================================================================
# render di controllo: cielo, sole, camere dai punti di presa delle foto (scheda §1)
# =============================================================================================================
# Est geografico nelle coordinate di progetto = (0,660; -0,751) (asse X ad azimut 41,3°). Nelle foto F1/F2/F3 le facciate
# est sono al sole: luce del mattino da est-sud-est, sole a ~38° [S].
SUN_AZ_GEO = 110.0
SUN_EL = 38.0
CAMS = {
    # nome: (posizione, azimut di progetto della direzione di vista in gradi da +Y verso +X, pitch, FOV orizzontale, risoluzione)
    # F1 e F2: camere ricalcolate ai minimi quadrati su punti OSM riconoscibili nelle foto (palma d'angolo, spigoli di A4,
    # gradino di A3 a Y 79,9, inizio e fine della parte rosa, antenne del ponte); scarto massimo 27 px su 1886 (F1), 6 px (F2).
    "CAM_Molo_F1": ((13.65, 118.43, 2.84), 199.7, -2.92, 87.0, (1886, 811)),
    "CAM_Molo_F1_scheda": ((12.5, 117.0, 2.8), 180.0 + 23.0, -2.9, 100.0, (1886, 811)),
    "CAM_Molo_F1_occhi": ((13.65, 118.43, 1.6), 199.7, -1.0, 87.0, (1886, 811)),
    "CAM_Molo_F2": ((31.37, 134.18, 2.76), 217.9, 2.92, 37.0, (1030, 667)),
    "CAM_Molo_F3": ((4.45, 46.4, 2.3), 213.4, -6.7, 92.5, (975, 895)),     # ricalcolata: scarto max 15 px
}


def _geo_to_proj(az_deg):
    a = math.radians(az_deg - 41.3)        # azimut geografico -> angolo rispetto all'asse +X di progetto (in senso orario)
    return Vector((math.cos(a), -math.sin(a), 0.0))


def setup_world():
    s = bpy.context.scene
    w = bpy.data.worlds.get("W_Molo") or bpy.data.worlds.new("W_Molo")
    s.world = w
    w.use_nodes = True
    nt = w.node_tree
    for nd in list(nt.nodes):
        if nd.type != "OUTPUT_WORLD":
            nt.nodes.remove(nd)
    out = next(nd for nd in nt.nodes if nd.type == "OUTPUT_WORLD")
    sky = nt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA"):
        try:
            sky.sky_type = t
            break
        except TypeError:
            continue
    d = _geo_to_proj(SUN_AZ_GEO)
    sky.sun_elevation = math.radians(SUN_EL)
    sky.sun_rotation = math.atan2(d.x, d.y)
    try:
        sky.altitude = 10.0
    except AttributeError:
        pass
    sky.sun_disc = False
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.22
    nt.links.new(sky.outputs[0], bg.inputs[0])
    nt.links.new(bg.outputs[0], out.inputs[0])
    sun = bpy.data.objects.get("SUN_Molo")
    if sun is None:
        ld = bpy.data.lights.new("SUN_Molo", "SUN")
        sun = bpy.data.objects.new("SUN_Molo", ld)
        s.collection.objects.link(sun)
    sun.data.energy = 6.0
    sun.data.angle = math.radians(1.0)
    sun.data.color = (1.0, 0.93, 0.84)
    to_sun = Vector((d.x * math.cos(math.radians(SUN_EL)), d.y * math.cos(math.radians(SUN_EL)), math.sin(math.radians(SUN_EL))))
    sun.rotation_euler = (-to_sun).to_track_quat("-Z", "Y").to_euler()
    ref = bpy.data.objects.get("REF_Sole")
    if ref is not None:
        ref.hide_render = True
        ref.hide_viewport = True
    try:
        s.view_settings.view_transform = "AgX"
        s.view_settings.exposure = -0.6   # v2: esposizione vicina alle foto (asfalto ~80/255 in F1)
    except TypeError:
        pass
    s.render.engine = s.render.engine
    try:
        s.eevee.use_shadows = True
    except AttributeError:
        pass
    return sun


def cameras():
    s = bpy.context.scene
    coll = pk._coll("MOLO_Camere")
    out = []
    for name, (pos, az, pitch, fov, res) in CAMS.items():
        cam = bpy.data.objects.get(name)
        if cam is None:
            cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
            coll.objects.link(cam)
        cam.location = pos
        a = math.radians(az)
        fwd = Vector((math.sin(a), math.cos(a), math.tan(math.radians(pitch)))).normalized()
        cam.rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
        cam.data.sensor_fit = "HORIZONTAL"
        cam.data.angle = math.radians(fov)
        cam.data.clip_start = 0.1
        cam.data.clip_end = 3000
        cam["res"] = res
        out.append(cam)
    return out


def render(cam_name, path, width=1400):
    s = bpy.context.scene
    cam = bpy.data.objects[cam_name]
    s.camera = cam
    rx, ry = cam["res"]
    s.render.resolution_x = width
    s.render.resolution_y = int(round(width * ry / rx))
    s.render.resolution_percentage = 100
    s.render.filepath = path
    s.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    return path


def hide_context_for_render():
    """Nel contesto della v3 le prime palme sono a X 12 (F1_01, F2_01) ma l'utente ha deciso di spostare i filari (D4):
    per i render di confronto le nascondo (non le cancello). Anche il blockout del giardino nell'angolo resta sotto."""
    hidden = []
    for n in ("V3_Palma_F1_01", "V3_Palma_F2_01", "V3_Aiuola_F1_01", "V3_Aiuola_F2_01", "SM_Blockout_PassPav_SiepeLimite"):
        o = bpy.data.objects.get(n)
        if o is not None:
            o.hide_render = True
            o.hide_viewport = True
            hidden.append(n)
    return hidden


# =============================================================================================================
# lampione a due globi sovrapposti (scheda §5), origine alla base, si posa a quota cubetti (Z +0,15)
# =============================================================================================================
L2G_PROF = [  # (raggio, quota) del fusto in ghisa, dal basso: base svasata scanalata (~1,2 m), fusto, collari
    (0.24, 0.00), (0.24, 0.05), (0.21, 0.08), (0.21, 0.14), (0.19, 0.18), (0.15, 0.30), (0.125, 0.55), (0.11, 0.85),
    (0.10, 1.05), (0.12, 1.10), (0.12, 1.18), (0.085, 1.24), (0.075, 1.6), (0.068, 2.4), (0.08, 2.45), (0.08, 2.52),
    (0.065, 2.56), (0.058, 4.6), (0.07, 4.65), (0.07, 4.72), (0.055, 4.76), (0.05, 5.10), (0.07, 5.14), (0.11, 5.20),
    (0.11, 5.24), (0.05, 5.27)]
L2G_GLOBI = ((5.55, 0.29), (6.38, 0.35))      # (quota del centro, raggio): inferiore Ø 0,58, superiore Ø 0,70 [S] F1
L2G_COLLO = [(0.05, 5.84), (0.06, 5.88), (0.10, 5.95), (0.10, 6.0), (0.05, 6.04)]
L2G_CIMA = [(0.06, 6.72), (0.07, 6.76), (0.04, 6.80), (0.035, 6.95), (0.05, 7.0), (0.05, 7.04), (0.02, 7.08),
            (0.012, 7.22), (0.0, 7.28)]
L2G_BASE = 0.9   # lastra quadrata di base [S] F1


def build_lampione2globi(coll, lod=0, name="SM_Molo_Lampione2Globi"):
    sides = (16, 10, 6)[lod]
    sseg, sring = ((20, 12), (12, 8), (8, 5))[lod]
    bm = bmesh.new()
    prof = L2G_PROF if lod < 2 else [(0.24, 0.0), (0.2, 0.14), (0.11, 0.85), (0.12, 1.15), (0.075, 1.6), (0.058, 4.7),
                                     (0.11, 5.2), (0.05, 5.27)]
    rings = pk._lathe(bm, prof, sides, mi=0, cap_top=False)
    if lod == 0:   # scanalature della base: anelli alterni rientrati (8 coste)
        for ring in rings[4:10]:
            for k, v in enumerate(ring):
                if k % 2 == 1:
                    v.co.x *= 0.93
                    v.co.y *= 0.93
    for zc, r in L2G_GLOBI:
        pk._sphere(bm, (0, 0, zc), r, sseg, sring, 1)
    pk._lathe(bm, L2G_COLLO if lod < 2 else [(0.05, 5.84), (0.10, 5.97), (0.05, 6.04)], max(sides // 2, 6), mi=0)
    pk._lathe(bm, L2G_CIMA if lod < 2 else [(0.06, 6.72), (0.035, 6.95), (0.0, 7.28)], max(sides // 2, 6), mi=0)
    # lastra di base in pietra chiara (2 cm)
    h = L2G_BASE / 2
    pk._box(bm, -h, h, -h, h, -0.01, 0.02, 2, faces=("top", "xn", "xp", "yn", "yp"))
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = pk._finish(name + sfx, bm, ["M_Morin_Ghisa", "M_Morin_Globo", "M_Pav_Fascia"], coll, uv="box", smooth_angle=50)
    if lod == 0:
        pk._ucx(name, [(-0.24, 0.24, -0.24, 0.24, 0.0, 1.2), (-0.08, 0.08, -0.08, 0.08, 1.2, 5.25)], coll)
    return o


# =============================================================================================================
# alberi: due latifoglie (platano, 15-20 m) e pino domestico, chioma a card masked two-sided, origine al piede
# =============================================================================================================
def _branch(bm, pts, r0, r1, sides, mi=0, uv_tile=(1.0, 2.0)):
    """Ramo/tronco rastremato lungo una polilinea, UV cilindriche (U attorno, V lungo, in metri / tile)."""
    pts = [Vector(p) for p in pts]
    layer = bm.loops.layers.uv.verify()
    n = len(pts)
    rings = []
    up = Vector((0, 0, 1))
    acc = [0.0]
    for a, b in zip(pts[:-1], pts[1:]):
        acc.append(acc[-1] + (b - a).length)
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        ref = up if abs(t.dot(up)) < 0.95 else Vector((1, 0, 0))
        nx = t.cross(ref).normalized()
        ny = t.cross(nx)
        r = r0 + (r1 - r0) * (acc[i] / acc[-1])
        rings.append([bm.verts.new(p + r * (math.cos(2 * math.pi * k / sides) * nx + math.sin(2 * math.pi * k / sides) * ny))
                      for k in range(sides)])
    for i in range(n - 1):
        for k in range(sides):
            k1 = (k + 1) % sides
            f = bm.faces.new([rings[i][k], rings[i][k1], rings[i + 1][k1], rings[i + 1][k]])
            f.material_index = mi
            circ = 2 * math.pi * max(r0, 0.05)
            for lp, (kk, ii) in zip(f.loops, ((k, i), (k + 1, i), (k + 1, i + 1), (k, i + 1))):
                lp[layer].uv = (kk / sides * circ / uv_tile[0], acc[ii] / uv_tile[1])
    f = bm.faces.new(list(reversed(rings[0])))
    f.material_index = mi
    return rings


def _curve(p0, d, L, bend, nseg, rng):
    """Polilinea da p0 lungo d (Vector) lunga L, piegata verso l'alto/fuori."""
    pts = [Vector(p0)]
    d = d.normalized()
    for i in range(nseg):
        d = (d + Vector((rng.uniform(-bend, bend), rng.uniform(-bend, bend), rng.uniform(-bend * 0.5, bend)))).normalized()
        pts.append(pts[-1] + d * (L / nseg))
    return pts


def _cards(bm, centers, rng, n, size, crown_c, crown_r, flat=0.0, mi=1, quad_uv=True):
    """Card di chioma: quadrati di lato `size` (min, max) attorno ai centri dei ciuffi; normale verso l'esterno della
    chioma (piu' rumore); UV su uno dei 4 ciuffi dell'atlante. Ritorna le facce (per le normali personalizzate)."""
    layer = bm.loops.layers.uv.verify()
    faces = []
    for i in range(n):
        c, cr = centers[rng.integers(0, len(centers))]
        d = Vector(rng.normal(0, 1, 3)).normalized()
        # v2: card sul guscio del ciuffo, tangenti al ciuffo e rivolte verso l'esterno (mai di taglio a chi guarda da fuori)
        p = Vector(c) + d * cr * rng.uniform(0.72, 1.0)
        out = Vector(((p.x - crown_c[0]) / crown_r[0] ** 2, (p.y - crown_c[1]) / crown_r[1] ** 2,
                      (p.z - crown_c[2]) / crown_r[2] ** 2)).normalized()
        nrm = (d * 0.55 + out * 0.45 + Vector(rng.normal(0, 0.12, 3))).normalized()
        if flat:
            nrm = (nrm * (1 - flat) + Vector((0, 0, 1)) * flat).normalized()
        s = rng.uniform(*size)
        t1 = nrm.cross(Vector((0, 0, 1)) if abs(nrm.z) < 0.9 else Vector((1, 0, 0))).normalized()
        t2 = nrm.cross(t1)
        a = rng.uniform(0, 2 * math.pi)
        e1 = (t1 * math.cos(a) + t2 * math.sin(a)) * s / 2
        e2 = nrm.cross(e1)
        vs = [bm.verts.new(p + sx * e1 + sy * e2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        f = bm.faces.new(vs)
        f.material_index = mi
        q = int(rng.integers(0, 4))
        u0, v0 = (q % 2) * 0.5, 0.5 - (q // 2) * 0.5     # quadrante dell'atlante (riga 0 in alto -> V alto)
        for lp, (uu, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            lp[layer].uv = (u0 + 0.5 * uu, v0 + 0.5 * vv)
        faces.append((f, out))
    return faces


def _finish_tree(name, bm, card_faces, mats, coll):
    """Scrive la mesh; normali personalizzate delle card = direzione esterna della chioma (luce morbida e uniforme)."""
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    bm.faces.index_update()
    out_by_face = {}
    for f, out in card_faces:
        if f.is_valid:
            out_by_face[f.index] = out
    o = bpy.data.objects.get(name)
    if o is None:
        me = bpy.data.meshes.new(name)
        o = bpy.data.objects.new(name, me)
        coll.objects.link(o)
    me = o.data
    me.materials.clear()
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(bpy.data.materials[m])
    for p in me.polygons:
        p.use_smooth = True
    me.update()
    normals = []
    for p in me.polygons:
        for li in p.loop_indices:
            if p.index in out_by_face:
                normals.append(tuple(out_by_face[p.index]))
            else:
                normals.append(tuple(me.vertices[me.loops[li].vertex_index].normal))
    try:
        me.normals_split_custom_set(normals)
    except Exception as e:  # noqa
        print("normali personalizzate non impostate:", e)
    if coll not in o.users_collection:
        coll.objects.link(o)
    o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1)
    return o


LATIF = {
    # nome: (seme, altezza, raggi chioma (x, y, z), quota centro chioma, altezza della biforcazione, n rami)
    "SM_Albero_LatifogliaA": (11, 19.5, (7.6, 7.0, 7.2), 11.4, 4.0, 4),
    "SM_Albero_LatifogliaB": (23, 16.5, (6.4, 6.6, 6.2), 9.6, 3.3, 3),
}


def build_latifoglia(coll, name, lod=0):
    seed, H, cr, cz, hfork, nlimb = LATIF[name]
    rng = np.random.default_rng(seed)
    bm = bmesh.new()
    sides = (10, 7, 5)[lod]
    trunk = _curve((0, 0, 0), Vector((0.05, 0.03, 1)), hfork + 0.6, 0.06, 4, rng)
    _branch(bm, trunk, 0.42 * H / 18, 0.30 * H / 18, sides, 0)
    centers = []
    top = trunk[-2]
    for i in range(nlimb):
        ang = 2 * math.pi * i / nlimb + rng.uniform(-0.4, 0.4)
        d = Vector((math.cos(ang) * 0.55, math.sin(ang) * 0.55, 1.0))
        L = rng.uniform(0.8, 1.0) * (cz - hfork + cr[2] * 0.3)
        limb = _curve(top, d, L, 0.12, 4, rng)
        _branch(bm, limb, 0.24 * H / 18, 0.07, max(sides - 3, 4), 0)
        if lod < 2:
            for j in range(2 if lod == 0 else 1):
                p0 = limb[2 + j]
                dd = (limb[-1] - limb[1]).normalized() + Vector(rng.normal(0, 0.6, 3))
                dd.z = abs(dd.z) * 0.6 + 0.2
                sub = _curve(p0, dd, rng.uniform(2.5, 4.0), 0.15, 3, rng)
                _branch(bm, sub, 0.09, 0.03, 4, 0)
                centers.append((tuple(sub[-1]), 2.4))
        centers.append((tuple(limb[-1]), 2.8))
    # ciuffi sulla superficie dell'ellissoide della chioma (sagoma irregolare)
    for i in range(48):
        d = Vector(rng.normal(0, 1, 3)).normalized()
        if d.z < -0.75:
            d.z = -0.75
        # v2: sagoma irregolare: ciuffi interni grandi + ciuffi sporgenti piu' piccoli sul bordo
        if i < 36:
            f, rr = rng.uniform(0.5, 0.95), rng.uniform(2.2, 3.2)
        else:
            f, rr = rng.uniform(1.0, 1.18), rng.uniform(1.4, 2.0)
        centers.append(((d.x * cr[0] * f, d.y * cr[1] * f, cz + d.z * cr[2] * f), rr))
    ncard = (3500, 1700, 500)[lod]
    size = ((2.2, 3.2), (2.8, 4.0), (3.8, 5.4))[lod]
    cards = _cards(bm, centers, rng, ncard, size, (0, 0, cz), cr)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish_tree(name + sfx, bm, cards, ["M_Albero_Platano_Corteccia", "M_Albero_Latifoglia_Chioma"], coll)
    if lod == 0:
        r = 0.42 * H / 18
        pk._ucx(name, [(-r, r, -r, r, 0.0, hfork)], coll)
    return o


PINO = dict(seed=37, H=16.5, cz=14.0, cr=(7.0, 6.5, 2.2))


def build_pino(coll, lod=0, name="SM_Morin_PinoDomestico"):
    rng = np.random.default_rng(PINO["seed"])
    cz, cr = PINO["cz"], PINO["cr"]
    bm = bmesh.new()
    sides = (10, 7, 5)[lod]
    trunk = _curve((0, 0, 0), Vector((0.12, -0.05, 1)), 11.0, 0.05, 6, rng)
    _branch(bm, trunk, 0.36, 0.22, sides, 0, uv_tile=(1.0, 2.0))
    centers = []
    top = trunk[-1]
    for i in range(5):
        ang = 2 * math.pi * i / 5 + rng.uniform(-0.3, 0.3)
        d = Vector((math.cos(ang), math.sin(ang), 0.9))
        limb = _curve(top, d, rng.uniform(5.0, 6.5), 0.10, 4, rng)
        _branch(bm, limb, 0.16, 0.05, max(sides - 4, 4), 0)
        centers.append((tuple(limb[-1]), 2.4))
        centers.append((tuple(limb[2]), 2.2))
    for i in range(30):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0.2, 1.0) ** 0.5
        centers.append(((math.cos(a) * cr[0] * rr, math.sin(a) * cr[1] * rr, cz + rng.uniform(-0.8, 1.2) * (1 - rr * 0.6)),
                        rng.uniform(1.6, 2.4)))
    ncard = (1500, 700, 220)[lod]
    size = ((1.8, 2.8), (2.4, 3.6), (3.4, 5.0))[lod]
    cards = _cards(bm, centers, rng, ncard, size, (0, 0, cz), cr, flat=0.45)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish_tree(name + sfx, bm, cards, ["M_Morin_PinoDomestico_Corteccia", "M_Morin_PinoDomestico_Chioma"], coll)
    if lod == 0:
        pk._ucx(name, [(-0.36, 0.36, -0.36, 0.36, 0.0, 6.0)], coll)
    return o


# =============================================================================================================
# costruzione, posa, CSV, export
# =============================================================================================================
EDIFICI = ("SM_Molo_Edificio_A1A2", "SM_Molo_Edificio_A3", "SM_Molo_Edificio_A4A5", "SM_Molo_Edificio_C", "SM_Molo_Tendone")


def build_all():
    coll = pk._coll(KIT)
    out = [build_strada(coll)] + build_masselli(coll) + [build_angolo(coll)]
    for f in (build_A1A2, build_A3, build_A4A5, build_C, build_tendone, build_lampione2globi):
        out += [f(coll, lod=l) for l in range(3)]
    for nm in LATIF:
        out += [build_latifoglia(coll, nm, lod=l) for l in range(3)]
    out += [build_pino(coll, lod=l) for l in range(3)]
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    for o in out:
        print(f"{o.name:<34} tri {pk.tri_count(o):>6}  dim {tuple(round(d, 2) for d in o.dimensions)}")
    return out


# posizioni (coordinate Blender, metri): (asset, etichetta, x, y, z, yaw_gradi_blender)
ALBERI = [("SM_Albero_LatifogliaA", (-13.0, 104.0), 10.0), ("SM_Albero_LatifogliaB", (-12.5, 91.0), 75.0),
          ("SM_Albero_LatifogliaA", (-19.0, 82.0), 160.0), ("SM_Albero_LatifogliaB", (-14.0, 70.0), 230.0),
          ("SM_Albero_LatifogliaA", (-24.0, 60.0), 300.0), ("SM_Albero_LatifogliaB", (-20.0, 48.0), 120.0),
          ("SM_Albero_LatifogliaA", (-28.0, 36.0), 200.0)]
PINI = [((-12.0, 118.0), 40.0)]
LAMP2G = (13.0, 106.0)


def layout():
    rows = []
    for a in ("SM_Molo_Pav_Strada", "SM_Molo_Pav_Masselli_01", "SM_Molo_Pav_Masselli_02", "SM_Molo_Pav_Masselli_03",
              "SM_Pav_AngoloMolo") + EDIFICI:
        rows.append((a, a.replace("SM_", "").replace("Molo_", "Molo_", 1), 0.0, 0.0, 0.0, 0.0))
    rows.append(("SM_Molo_Lampione2Globi", "Lampione2Globi_00", LAMP2G[0], LAMP2G[1], ZF, 0.0))
    for i, (a, (x, y), yaw) in enumerate(ALBERI):
        rows.append((a, f"Latifoglia_{i:02d}", x, y, 0.0, yaw))
    for i, ((x, y), yaw) in enumerate(PINI):
        rows.append(("SM_Morin_PinoDomestico", f"PinoDomestico_{i:02d}", x, y, 0.0, yaw))
    return rows


def write_csv(rows, path="exports/molo/molo_posizioni_v1.csv"):
    def ue(v):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return "0.0" if s in ("0", "-0", "") else (s if "." in s else s + ".0")
    os.makedirs(os.path.dirname(f"{PROJ}/{path}"), exist_ok=True)
    lines = ["asset,nome,x,y,z,yaw"]
    for a, n, x, y, z, yaw in rows:
        lines.append(f"{a},{n},{ue(x * 100)},{ue(-y * 100)},{ue(z * 100)},{ue(-yaw if yaw else 0.0)}")
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(lines) - 1


def build_context(rows, name="MOLO_Contesto"):
    """Istanze per i render (oggetti collegati alle mesh LOD0); gli asset in (0,0,0) sono gia' al loro posto."""
    coll = pk._coll(name)
    for a, n, x, y, z, yaw in rows:
        if x == 0.0 and y == 0.0:
            continue
        nm = "CTXM_" + n
        o = bpy.data.objects.get(nm)
        if o is None:
            o = bpy.data.objects.new(nm, bpy.data.objects[a].data)
            coll.objects.link(o)
        o.data = bpy.data.objects[a].data
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(yaw))
    # gli originali dei pezzi posati altrove restano in (0,0,0): nascondo quelli che hanno un'istanza
    for a in {r[0] for r in rows if not (r[2] == 0.0 and r[3] == 0.0)}:
        bpy.data.objects[a].hide_render = True
        bpy.data.objects[a].hide_viewport = True
    return coll


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    reps = []
    names = ["SM_Molo_Pav_Strada", "SM_Molo_Pav_Masselli_01", "SM_Molo_Pav_Masselli_02", "SM_Molo_Pav_Masselli_03",
             "SM_Pav_AngoloMolo"]
    lodded = list(EDIFICI) + ["SM_Molo_Lampione2Globi", "SM_Albero_LatifogliaA", "SM_Albero_LatifogliaB",
                              "SM_Morin_PinoDomestico"]
    hidden = {}
    for o in bpy.context.scene.objects:
        hidden[o.name] = (o.hide_viewport, o.hide_get())
    # gli UCX nascosti (hide_viewport) non vengono valutati: la loro matrix_world puo' restare quella ruotata di un
    # export precedente. Li rendo visibili e riallineo le matrici (tutti i pezzi del kit hanno trasformazione identita').
    for o in bpy.data.collections[KIT].objects:
        o.hide_viewport = False
        o.hide_set(False)
        o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1)
        o.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.update()
    try:
        for nm in names + lodded:
            for lod in ((0,) if nm in names else (0, 1, 2)):
                on = nm if lod == 0 else f"{nm}_LOD{lod}"
                o = bpy.data.objects[on]
                o.hide_viewport = False
                o.hide_set(False)
                r = morin_export.export_fbx([o], f"{EXPDIR}/{on}.fbx", mode="asset", overwrite=overwrite,
                                            include_ucx=(lod == 0), bake_rotation=(lod > 0), verbose=False)
                reps.append(r)
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps


# =============================================================================================================
# v2: rilievo delle facciate (rientri di porte e finestre, davanzali, cornici) sull'atlante esistente
# =============================================================================================================
# Aperture disegnate nell'atlante: chiave -> lista di (u0, u1, h0, h1, tipo) in metri dell'atlante (h dal piede del muro).
# tipo: "porta" (rientro, niente davanzale), "finestra" (rientro + davanzale + cornice), "vetrata" (rientro + cornice).
OPEN = {
    "G_portafin": [(2.25, 4.25, 0.0, 2.55, "porta")],
    "G_porta": [(4.75, 5.75, 0.0, 2.45, "porta")],
    "P_finestra": [(6.65, 7.55, 1.0, 2.35, "finestra")],
    "Y_finestrella": [(1.0, 1.55, 1.5, 2.25, "finestra")],
    "W_vetrata": [(2.35, 3.65, 0.0, 2.6, "vetrata")],
    "W_porta": [(4.5, 5.5, 0.0, 2.35, "porta")],
    "W_grata": [(6.85, 7.75, 1.0, 2.2, "finestra")],
}
RIENTRO = 0.13          # profondita' dei rientri [S] (muri intonacati di 25-30 cm)
_DET = {"lod": 0}       # livello di dettaglio corrente (impostato da _building)
UV_SOGLIA = (6.57, ROW1 + 0.93, 7.63, ROW1 + 1.0)       # davanzale bianco dipinto sotto la finestra rosa
UV_CORNICE = (0.1, 0.76, 7.9, 0.86)                     # banda della cornice bianca


def _uvq(f, layer, rect):
    u0, v0, u1, v1 = rect
    _uv_set(f, [(u0 / 8, v0 / 8), (u1 / 8, v0 / 8), (u1 / 8, v1 / 8), (u0 / 8, v1 / 8)][:len(f.loops)], layer)


def _wall_piece(bm, layer, a, b, z0, z1, ua, ub, base, key, hm, mi=0):
    """Pezzo di muro piano da a a b (XY), quota z0-z1, UV u in [ua, ub] della chiave `key`. Se nel pezzo cade
    un'apertura dell'atlante la parete viene forata e l'apertura rientra di RIENTRO con le spallette."""
    a, b = Vector(a), Vector(b)
    ident = hm(1.0) == 1.0 and hm(2.0) == 2.0
    ops = []
    if ident and _DET["lod"] < 2 and key in OPEN:
        for ou0, ou1, oh0, oh1, kind in OPEN[key]:
            c0, c1 = max(ou0, min(ua, ub)), min(ou1, max(ua, ub))
            if c1 - c0 > 0.02 and oh1 > z0 and oh0 < z1:
                ops.append((c0, c1, max(oh0, z0), min(oh1, z1), kind, ou0, ou1))
    sgn = 1.0 if ub >= ua else -1.0

    def P(u, z, inset=0.0):
        t = (u - ua) / (ub - ua)
        p = a + (b - a) * t
        d = (b - a).normalized()
        inn = Vector((-d.y, d.x))          # verso l'interno (poligono antiorario)
        q = p + inn * inset
        return (q.x, q.y, z)

    def quad(u0, u1, h0, h1, inset=0.0):
        if u1 - u0 < 1e-5 or h1 - h0 < 1e-5:
            return None
        f = pk._quad(bm, [P(u0, h0, inset), P(u1, h0, inset), P(u1, h1, inset), P(u0, h1, inset)], mi)
        _uv_set(f, [_auv(u0, base, hm(h0)), _auv(u1, base, hm(h0)), _auv(u1, base, hm(h1)), _auv(u0, base, hm(h1))], layer)
        return f

    if not ops:
        quad(ua, ub, z0, z1)
        return
    c0, c1, h0, h1, kind, ou0, ou1 = ops[0]
    lo, hi = min(ua, ub), max(ua, ub)
    # muro attorno all'apertura (4 pannelli)
    quad(lo, c0, z0, z1)
    quad(c1, hi, z0, z1)
    quad(c0, c1, z0, h0)
    quad(c0, c1, h1, z1)
    # fondo dell'apertura, rientrato
    quad(c0, c1, h0, h1, RIENTRO)
    r = RIENTRO
    e = 0.05       # le spallette prendono il colore del telaio dipinto al bordo dell'apertura
    # spalletta superiore (guarda in basso) e inferiore (guarda in alto)
    f = pk._quad(bm, [P(c0, h1, r), P(c1, h1, r), P(c1, h1, 0), P(c0, h1, 0)], mi)
    _uv_set(f, [_auv(c0, base, h1 - e), _auv(c1, base, h1 - e), _auv(c1, base, h1), _auv(c0, base, h1)], layer)
    if h0 > z0 + 1e-4:
        f = pk._quad(bm, [P(c0, h0, 0), P(c1, h0, 0), P(c1, h0, r), P(c0, h0, r)], mi)
        _uv_set(f, [_auv(c0, base, h0), _auv(c1, base, h0), _auv(c1, base, h0 + e), _auv(c0, base, h0 + e)], layer)
    # spallette laterali solo dove l'apertura finisce davvero dentro questo pezzo
    if abs(c0 - ou0) < 1e-4:
        f = pk._quad(bm, [P(c0, h0, 0), P(c0, h0, r), P(c0, h1, r), P(c0, h1, 0)], mi)
        _uv_set(f, [_auv(c0, base, h0), _auv(c0 + e, base, h0), _auv(c0 + e, base, h1), _auv(c0, base, h1)], layer)
    if abs(c1 - ou1) < 1e-4:
        f = pk._quad(bm, [P(c1, h0, r), P(c1, h0, 0), P(c1, h1, 0), P(c1, h1, r)], mi)
        _uv_set(f, [_auv(c1 - e, base, h0), _auv(c1, base, h0), _auv(c1, base, h1), _auv(c1 - e, base, h1)], layer)
    if _DET["lod"] > 0:
        return
    # davanzale sporgente (finestre) e cornice (finestre e vetrate) in rilievo
    if kind == "finestra" and h0 > 0.3:
        x0, x1 = c0 - (0.08 if abs(c0 - ou0) < 1e-4 else 0), c1 + (0.08 if abs(c1 - ou1) < 1e-4 else 0)
        fs = [pk._quad(bm, [P(x0, h0, -0.06), P(x1, h0, -0.06), P(x1, h0, 0.02), P(x0, h0, 0.02)], mi),        # piano
              pk._quad(bm, [P(x0, h0 - 0.05, -0.06), P(x1, h0 - 0.05, -0.06), P(x1, h0, -0.06), P(x0, h0, -0.06)], mi),  # fronte
              pk._quad(bm, [P(x0, h0 - 0.05, 0.0), P(x1, h0 - 0.05, 0.0), P(x1, h0 - 0.05, -0.06), P(x0, h0 - 0.05, -0.06)], mi)]  # sotto
        for f in fs:
            _uvq(f, layer, (UV_SOGLIA[0], UV_SOGLIA[1], UV_SOGLIA[2], UV_SOGLIA[3]))
        ends = ([(x0, True)] if x0 < c0 else []) + ([(x1, False)] if x1 > c1 else [])
        for xx, left in ends:
            if left:
                f = pk._quad(bm, [P(xx, h0 - 0.05, 0.0), P(xx, h0 - 0.05, -0.06), P(xx, h0, -0.06), P(xx, h0, 0.0)], mi)
            else:
                f = pk._quad(bm, [P(xx, h0 - 0.05, -0.06), P(xx, h0 - 0.05, 0.0), P(xx, h0, 0.0), P(xx, h0, -0.06)], mi)
            _uvq(f, layer, UV_SOGLIA)
    if kind in ("finestra", "vetrata"):
        w, t = 0.07, 0.025      # cornice: fascia di 7 cm sporgente 2,5 cm sopra e ai lati
        segs = [(c0 - (w if abs(c0 - ou0) < 1e-4 else 0), c1 + (w if abs(c1 - ou1) < 1e-4 else 0), h1, h1 + w)]
        if abs(c0 - ou0) < 1e-4:
            segs.append((c0 - w, c0, h0, h1))
        if abs(c1 - ou1) < 1e-4:
            segs.append((c1, c1 + w, h0, h1))
        for u0_, u1_, v0_, v1_ in segs:
            fr = pk._quad(bm, [P(u0_, v0_, -t), P(u1_, v0_, -t), P(u1_, v1_, -t), P(u0_, v1_, -t)], mi)
            _uvq(fr, layer, UV_CORNICE)
            top = pk._quad(bm, [P(u0_, v1_, -t), P(u1_, v1_, -t), P(u1_, v1_, 0), P(u0_, v1_, 0)], mi)
            _uvq(top, layer, UV_CORNICE)
            for uu, left in ((u0_, True), (u1_, False)):
                if left:
                    f = pk._quad(bm, [P(uu, v0_, 0), P(uu, v0_, -t), P(uu, v1_, -t), P(uu, v1_, 0)], mi)
                else:
                    f = pk._quad(bm, [P(uu, v0_, -t), P(uu, v0_, 0), P(uu, v1_, 0), P(uu, v1_, -t)], mi)
                _uvq(f, layer, UV_CORNICE)
