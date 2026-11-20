"""morin_viale.py — vista verso la citta' del Blocco 1 (v1, 2026-11-19): prato vero dei Giardini a Mare, aiuole bordate di
bosso, Viale Italia (strada modulare + auto generiche) e palazzi d'epoca di fondale.

Schede: ref/sezione.md (giardini Y 102-116, oleandri Y 119,5 [V], Viale Italia Y ~121-139, assi carreggiate Y ~128 e ~135 [V],
ciclabile Y 140-142,5 [V], Giardini pubblici da Y 145 [V]), ref/area.md (cortina vera oltre i Giardini pubblici),
ref/zona_parcheggio_chiosco.md §4. Foto: ref/foto/vista/prato con alberelli.png (cattura Street View, deroga [SV]:
dalla foto solo colori e proporzioni; texture procedurali, niente UI, persone, targhe, insegne).
Fronti dei palazzi: isole di SM_Blockout_Fondale_v2_Edifici (= sagome OSM, ref/dem/edifici_osm_footprint_1600m.json).

Esegui dentro blender/arte_viale.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_viale as mv; importlib.reload(mv)
    mv.make_textures()     # blender/textures/viale/ (prato 2048, bosso/segnaletica/auto 1024, palazzi A/B/C 1024)
    mv.build_materials()
    mv.build_all()         # mesh LOD0/1/2 (+ UCX solo prato e aiuole) nella collezione VIALE_Kit
    rows = mv.layout()
    mv.write_csv(rows)     # exports/viale/viale_posizioni_v1.csv (coordinate UE)
    mv.build_context(rows) # istanze per il render (VIALE_Contesto)
    mv.export_all()
    mv.cameras(); mv.render_confronto()

Convenzioni: palazzi con origine al centro del fronte a terra, fronte verso -Y (il mare), corpo verso +Y; strada a moduli da
19 m con origine all'inizio del modulo sul ciglio lato giardini (Y 120,85); auto con origine a terra al centro, muso verso +X.
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
TEXDIR = PROJ + "/blender/textures/viale"
MOLO_TEX = PROJ + "/blender/textures/molo"
KIT = "VIALE_Kit"
EXPDIR = "//../exports/viale"
ZF = pk.ZF
SCR = None

# ---------------------------------------------------------------------------------------------------------------
# quote e sezione [V] OSM dove indicato, il resto [S]
# ---------------------------------------------------------------------------------------------------------------
Z_PRATO = 0.08                 # sopra le aiuole del blockout v4 (Z 0,05) e il suolo del fondale (Z 0)
PRATO_X = (117.5, 250.0)
PRATO_Y = (101.9, 120.85)      # dal bordo dei cubetti al cordolo del viale (copre le fasce menta/lastre del blockout)
Y0_STRADA = 120.85
MOD_L = 19.0                   # modulo strada (7 moduli = X 117-250)
STRADA_X0, STRADA_N = 117.0, 7
TILE_ASF = 4.75                # 19 / 4: l'asfalto non ha cuciture fra i moduli
# fasce trasversali del viale (Y mondo, quota del piano, materiale)
BANDE = [(120.85, 121.00, 0.15, 1),   # cordolo lato giardini (granito)
         (121.00, 131.00, 0.02, 0),   # sosta in linea (121-123,3) + carreggiata A (asse ~127,2) [asse V ~128]
         (131.00, 132.00, 0.15, 1),   # spartitraffico in pietra [S]
         (132.00, 138.60, 0.02, 0),   # carreggiata B + sosta lato citta' (asse ~135,3) [asse V ~135]
         (138.60, 138.75, 0.15, 1),   # cordolo lato citta'
         (138.75, 145.00, 0.15, 0)]   # marciapiede e ciclabile (140-142,5 [V]) fino ai Giardini pubblici (145 [V])
STRISCE_CONT = [(123.30, 0.12, 0.02), (130.80, 0.12, 0.02), (132.20, 0.12, 0.02), (138.40, 0.12, 0.02),
                (140.00, 0.10, 0.15), (142.50, 0.10, 0.15)]
STRISCE_TRAT = [(127.00, 0.12), (134.50, 0.12)]     # tratteggio 4,5 m pieno / 5 m vuoto (periodo 9,5 = MOD_L / 2)
Y_SOSTA_A, Y_SOSTA_B = 122.15, 137.45                 # assi delle file di auto parcheggiate [S]

# colori sRGB (dalla foto [SV], riportati a luce piena)
C_PRATO = (92, 122, 50)
C_PRATO_SECCO = (128, 132, 68)
C_BOSSO = (46, 70, 36)
C_BOSSO_LUCE = (96, 124, 58)


def _c(c):
    return np.asarray(c, np.float32) / 255.0


def _save(a, name):
    os.makedirs(TEXDIR, exist_ok=True)
    tp.save(a, f"{TEXDIR}/{name}.png")
    return name


# =============================================================================================================
# texture tileable: prato, bosso, segnaletica
# =============================================================================================================
def _line_kernel(size, L, ang):
    k = np.zeros((size, size), np.float32)
    c = size // 2
    for t in np.linspace(-L / 2, L / 2, int(L * 2) + 1):
        x = int(round(c + t * math.cos(ang))) % size
        y = int(round(c + t * math.sin(ang))) % size
        k[y, x] = 1.0
    return np.fft.ifftshift(k / k.sum())


def _conv(a, k):
    return np.real(np.fft.ifft2(np.fft.fft2(a) * np.fft.fft2(k))).astype(np.float32)


def make_tex_prato(size=2048, seed=901, name="T_Morin_Prato"):
    """Erba rasata vista dall'alto, tile 4 m (512 px/m): fili orientati (rumore convoluto con segmenti a 4 angoli scelti
    da una mappa d'orientamento lenta), macchie di trifoglio piu' scure e zone appena ingiallite."""
    rng = np.random.default_rng(seed)
    base = rng.standard_normal((size, size)).astype(np.float32)
    orient = mm._noise(size, size, 70, seed + 1)
    angs = [0.3, 1.1, 1.9, 2.7]
    s = np.zeros((size, size), np.float32)
    wsum = np.zeros((size, size), np.float32)
    for i, a in enumerate(angs):
        st = _conv(base, _line_kernel(size, 14, a))
        w = np.exp(-((orient * 1.4 - (i - 1.5)) ** 2))
        s += st * w
        wsum += w
    s = s / np.maximum(wsum, 1e-3)
    s = s / (s.std() + 1e-6)
    fine = mm._noise(size, size, 0.7, seed + 2)
    blade = np.clip(0.5 + 0.20 * s + 0.16 * fine, 0, 1)
    clover = np.clip((mm._noise(size, size, 22, seed + 3) - 0.8) * 1.5, 0, 1)
    dry = np.clip((mm._noise(size, size, 140, seed + 4) - 0.6) * 1.2, 0, 1)
    big = mm._noise(size, size, 260, seed + 5)
    col = _c(C_PRATO)[None, None, :] * (0.55 + 0.85 * blade[..., None])
    col = col * (1 + 0.06 * big[..., None])
    col = col * (1 - 0.25 * clover[..., None]) + _c((52, 86, 40)) * 0.25 * clover[..., None]
    col = col * (1 - 0.35 * dry[..., None]) + _c(C_PRATO_SECCO) * (0.6 + 0.6 * blade[..., None]) * 0.35 * dry[..., None]
    # punte chiare (luce radente) e fondo scuro fra i fili
    tips = np.clip((blade - 0.78) * 4, 0, 1)
    col = col + _c((40, 44, 18)) * tips[..., None]
    col = np.clip(col, 0, 1)
    h = blade * 0.8 + 0.2 * clover
    n, ao = mm._normal_ao(h, 2.2, 3, 1.5)
    rough = np.clip(0.88 + 0.06 * fine * 0.3 - 0.05 * tips, 0, 1)
    out = [_save(col, name + "_D"), _save(n, name + "_N"),
           _save(mm._orm(ao, rough, np.zeros_like(ao)), name + "_ORM")]
    return out


def make_tex_bosso(size=1024, seed=911, name="T_Morin_Bosso"):
    """Siepe di bosso potata (tile 1,5 m): foglioline fitte a grappoli, piu' chiare sulle punte esposte."""
    leaf = mm._noise(size, size, 1.6, seed)
    clus = mm._noise(size, size, 7, seed + 1)
    big = mm._noise(size, size, 40, seed + 2)
    v = np.clip(0.5 + 0.22 * leaf + 0.28 * clus, 0, 1)
    holes = np.clip((-clus - 1.9) * 2, 0, 1)
    col = _c(C_BOSSO)[None, None, :] * (1 - v[..., None]) + _c(C_BOSSO_LUCE)[None, None, :] * v[..., None]
    col *= (1 + 0.05 * big[..., None])
    col *= (1 - 0.35 * holes[..., None])
    col = np.clip(col, 0, 1)
    h = v - 0.6 * holes
    n, ao = mm._normal_ao(h, 3.5, 4, 2.0)
    out = [_save(col, name + "_D"), _save(n, name + "_N"),
           _save(mm._orm(ao, np.full_like(ao, 0.8), np.zeros_like(ao)), name + "_ORM")]
    return out


def make_tex_segnaletica(size=512, seed=921, name="T_Viale_Segnaletica"):
    """Vernice bianca consumata (tile 1 m): dove e' consumata si vede l'asfalto scuro."""
    wear = mm._noise(size, size, 18, seed)
    fine = mm._noise(size, size, 1.0, seed + 1)
    m = np.clip(0.85 + 0.25 * wear + 0.15 * fine, 0, 1)
    col = _c((226, 226, 218))[None, None, :] * m[..., None] + _c((86, 86, 88))[None, None, :] * (1 - m[..., None])
    n, ao = mm._normal_ao(m * 0.5 + 0.1 * fine, 1.0, 3, 0.5)
    out = [_save(np.clip(col, 0, 1), name + "_D"), _save(n, name + "_N"),
           _save(mm._orm(ao, 0.55 + 0.3 * (1 - m), np.zeros_like(ao)), name + "_ORM")]
    return out


# =============================================================================================================
# palazzi d'epoca: atlante 1024 per variante (facciata intera, non a tile)
# =============================================================================================================
# V 0,125-1: facciata (u = metri lungo il fronte / W, v = 0,125 + 0,875 z / HT, HT = cima del cornicione)
# V 0-0,0625: coppi del tetto · V 0,0625-0,094: stucco chiaro (spallette, cornici) · V 0,094-0,125: muro liscio
PAL = {
    "SM_Fondale_Palazzo_A": dict(W=20.0, D=18.0, nb=5, floors=6, wall=(226, 192, 116), trim=(238, 230, 208),
                                 shut=(62, 98, 70), quoins=True, frieze=False, balcony=False, attic=True, seed=31),
    "SM_Fondale_Palazzo_B": dict(W=24.5, D=18.0, nb=6, floors=6, wall=(226, 166, 154), trim=(240, 232, 214),
                                 shut=(56, 92, 66), quoins=False, frieze=True, balcony=True, attic=False, seed=37),
    "SM_Fondale_Palazzo_C": dict(W=20.0, D=16.0, nb=5, floors=5, wall=(208, 150, 92), trim=(232, 218, 190),
                                 shut=(70, 102, 72), quoins=True, frieze=True, balcony=False, attic=False, seed=41),
}
G_H, F_H, CORN_H = 4.2, 3.35, 0.9
V_FAC, V_TRIM, V_WALL = 0.125, 0.0625, 0.09375


def _pal_dims(p):
    Hw = G_H + (p["floors"] - 1) * F_H
    return Hw, Hw + CORN_H


def _pal_windows(p, L):
    """Aperture del fronte lungo L (metri lungo la facciata, quota): (u0, u1, z0, z1, prof, tipo)."""
    W, nb, Hw = p["W"], p["nb"], _pal_dims(p)[0]
    bay = W / nb
    out = []
    i = 0
    while True:
        uc = (i + 0.5) * bay
        if uc + 1.1 > L - 0.5:
            break
        # piano terra: portone al centro del fronte, vetrine/finestre ad arco ribassato sugli altri
        out.append((uc - 0.9, uc + 0.9, 0.0 if i == nb // 2 else 0.55, 3.15, 0.30, "terra"))
        for k in range(1, p["floors"]):
            zf = G_H + (k - 1) * F_H
            if k == 1 and p["balcony"] and abs(uc - W / 2) < bay * 1.1:
                out.append((uc - 0.62, uc + 0.62, zf + 0.12, zf + 2.85, 0.22, "porta"))
            else:
                out.append((uc - 0.62, uc + 0.62, zf + 0.85, zf + 2.70, 0.22, "fin"))
        i += 1
    return out


class _Fac:
    def __init__(self, p, n=1024):
        self.p, self.n = p, n
        self.Hw, self.HT = _pal_dims(p)
        self.alb = np.zeros((n, n, 3), np.float32)
        self.h = np.full((n, n), 0.5, np.float32)
        self.r = np.full((n, n), 0.9, np.float32)

    def px(self, u, z):
        """metri -> (colonna, riga)."""
        c = u / self.p["W"] * self.n
        v = V_FAC + (1 - V_FAC) * z / self.HT
        return c, (1 - v) * self.n

    def sl(self, u0, u1, z0, z1):
        c0, r1 = self.px(u0, z0)
        c1, r0 = self.px(u1, z1)
        r0, r1 = int(round(r0)), int(round(r1))
        c0, c1 = int(round(c0)), int(round(c1))
        return slice(max(r0, 0), min(max(r1, r0 + 1), self.n)), slice(max(c0, 0), min(max(c1, c0 + 1), self.n))

    def rect(self, u0, u1, z0, z1, col, h=None, r=None, mul=None):
        rs, cs = self.sl(u0, u1, z0, z1)
        c = _c(col) if not isinstance(col, np.ndarray) else col
        if mul is not None:
            self.alb[rs, cs] = self.alb[rs, cs] * mul
        else:
            self.alb[rs, cs] = c
        if h is not None:
            self.h[rs, cs] = h
        if r is not None:
            self.r[rs, cs] = r


def _persiana(F, u0, u1, z0, z1, col, rng):
    F.rect(u0, u1, z0, z1, col, h=0.62, r=0.6)
    rs, cs = F.sl(u0, u1, z0, z1)
    hh = rs.stop - rs.start
    lines = (np.arange(hh) % 4 == 0).astype(np.float32)[:, None]      # lamelle ogni ~0,1 m
    F.alb[rs, cs] *= (1 - 0.30 * lines)[..., None]
    F.h[rs, cs] -= 0.08 * lines
    F.rect(u0, u1, z0, z0 + 0.06, np.asarray(_c(col) * 0.8), h=0.66)
    F.rect(u0, u1, z1 - 0.06, z1, np.asarray(_c(col) * 0.8), h=0.66)
    F.alb[rs, cs] *= rng.uniform(0.9, 1.08)


def _vetro(F, u0, u1, z0, z1, rng, tenda=False):
    rs, cs = F.sl(u0, u1, z0, z1)
    hh, ww = rs.stop - rs.start, cs.stop - cs.start
    t = np.linspace(0, 1, hh)[:, None, None]
    c = _c((34, 38, 44)) + _c((110, 124, 138)) * (1 - t) * 0.45
    c = np.broadcast_to(c, (hh, ww, 3)).copy()
    if tenda:
        c = c * 0.3 + _c((206, 196, 172)) * 0.7 * (0.9 + 0.1 * np.sin(np.linspace(0, 25, ww)))[None, :, None]
    F.alb[rs, cs] = c
    F.h[rs, cs] = 0.25
    F.r[rs, cs] = 0.15 if not tenda else 0.7


def make_tex_palazzo(name, p):
    rng = np.random.default_rng(p["seed"])
    F = _Fac(p)
    n = F.n
    W, Hw, HT = p["W"], F.Hw, F.HT
    wall, trim, shut = p["wall"], p["trim"], p["shut"]
    det = 1 + 0.035 * mm._noise(n, n, 2.0, p["seed"]) + 0.04 * mm._noise(n, n, 30, p["seed"] + 1)
    # muro
    F.rect(0, W, 0, HT, wall, h=0.5, r=0.9)
    # basamento: zoccolo in pietra e bugnato del piano terra
    F.rect(0, W, 0, G_H, np.asarray(_c(wall) * 0.97 if not p["frieze"] else _c(trim) * 0.95), h=0.5)
    for z in np.arange(0.6, G_H, 0.45):
        F.rect(0, W, z - 0.03, z, None, mul=0.78)
        rs, cs = F.sl(0, W, z - 0.03, z)
        F.h[rs, cs] = 0.35
    F.rect(0, W, 0, 0.6, (150, 146, 136), h=0.55, r=0.85)
    F.rect(0, W, G_H - 0.05, G_H + 0.30, trim, h=0.75, r=0.8)          # marcapiano
    F.rect(0, W, G_H - 0.05, G_H, None, mul=0.75)
    # cantonali
    if p["quoins"]:
        for k, z in enumerate(np.arange(G_H + 0.3, Hw - 0.6, 0.42)):
            w = 0.75 if k % 2 == 0 else 0.5
            for (a, b) in ((0, w), (W - w, W)):
                F.rect(a, b, z + 0.03, z + 0.39, trim, h=0.62)
    else:   # lesene chiare
        for (a, b) in ((0, 0.55), (W - 0.55, W)):
            F.rect(a, b, G_H + 0.3, Hw, trim, h=0.6)
    # aperture (le stesse coordinate usate dalla geometria)
    wins = _pal_windows(p, W)
    for (u0, u1, z0, z1, prof, kind) in wins:
        uc = (u0 + u1) / 2
        if kind == "terra":
            F.rect(u0 - 0.18, u1 + 0.18, z0 - (0.0 if z0 == 0 else 0.1), z1 + 0.25, trim, h=0.7)
            if z0 == 0.0:   # portone in legno
                F.rect(u0, u1, z0, z1, (88, 56, 36), h=0.35, r=0.6)
                for k in range(1, 6):
                    zz = z0 + k * (z1 - z0) / 6
                    F.rect(u0 + 0.08, u1 - 0.08, zz - 0.03, zz, None, mul=0.7)
                F.rect(uc - 0.02, uc + 0.02, z0, z1, None, mul=0.6)
            else:
                _vetro(F, u0, u1, z0, z1, rng, tenda=rng.uniform() < 0.3)
                F.rect(u0, u1, z0 + 0.0, z0 + 0.08, trim, h=0.7)
                # serranda mezza abbassata a volte
                if rng.uniform() < 0.35:
                    zz = z1 - rng.uniform(0.6, 1.8)
                    F.rect(u0, u1, zz, z1, (120, 118, 112), h=0.4, r=0.5)
                    rs, cs = F.sl(u0, u1, zz, z1)
                    F.alb[rs, cs] *= (1 - 0.25 * (np.arange(rs.stop - rs.start) % 3 == 0))[:, None, None]
            continue
        # cornice della finestra, davanzale, timpano/cornice sopra
        F.rect(u0 - 0.16, u1 + 0.16, z0 - 0.06, z1 + 0.16, trim, h=0.68)
        F.rect(u0 - 0.24, u1 + 0.24, z0 - 0.16, z0 - 0.04, trim, h=0.8)
        piano = int((z0 - G_H) // F_H) + 1
        if piano <= 2:
            F.rect(u0 - 0.26, u1 + 0.26, z1 + 0.22, z1 + 0.38, trim, h=0.8)
            F.rect(u0 - 0.26, u1 + 0.26, z1 + 0.18, z1 + 0.22, None, mul=0.7)
            if piano == 1:      # timpano triangolare
                rs, cs = F.sl(u0 - 0.26, u1 + 0.26, z1 + 0.38, z1 + 0.78)
                hh, ww = rs.stop - rs.start, cs.stop - cs.start
                yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
                tri = (yy / max(hh, 1)) >= np.abs(xx / max(ww - 1, 1) * 2 - 1)
                F.alb[rs, cs] = np.where(tri[..., None], _c(trim) * 0.97, F.alb[rs, cs])
                F.h[rs, cs] = np.where(tri, 0.78, F.h[rs, cs])
        # sgocciolature sotto il davanzale
        rs, cs = F.sl(u0 - 0.1, u1 + 0.1, z0 - 1.0, z0 - 0.16)
        g = np.linspace(0.92, 1.0, rs.stop - rs.start)[::-1][:, None]
        g = 1 - (1 - np.linspace(0.90, 1.0, rs.stop - rs.start))[:, None] * (0.5 + 0.5 * rng.uniform(size=(1, cs.stop - cs.start)))
        F.alb[rs, cs] *= g[..., None]
        _vetro(F, u0, u1, z0, z1, rng, tenda=rng.uniform() < 0.35)
        # telaio bianco a due ante
        F.rect(u0, u1, z0, z0 + 0.06, (232, 230, 222), h=0.4)
        F.rect(u0, u1, z1 - 0.06, z1, (232, 230, 222), h=0.4)
        F.rect(uc - 0.03, uc + 0.03, z0, z1, (232, 230, 222), h=0.4)
        if kind == "porta":     # ringhiera del balcone dipinta davanti alla porta-finestra
            F.rect(u0, u1, z0 + 0.95, z0 + 1.0, (40, 40, 40), h=0.7, r=0.5)
            rs, cs = F.sl(u0, u1, z0, z0 + 0.95)
            bars = (np.arange(cs.stop - cs.start) % 4 == 0).astype(np.float32)[None, :]
            F.alb[rs, cs] = F.alb[rs, cs] * (1 - bars[..., None]) + _c((40, 40, 40)) * bars[..., None]
        # persiane verdi: aperte (sul muro ai lati), chiuse (nel vano) o socchiuse
        st = rng.choice(["aperte", "chiuse", "mezze"], p=[0.5, 0.35, 0.15])
        hw = (u1 - u0) / 2
        if st == "aperte":
            _persiana(F, u0 - 0.16 - hw, u0 - 0.16, z0, z1, shut, rng)
            _persiana(F, u1 + 0.16, u1 + 0.16 + hw, z0, z1, shut, rng)
        elif st == "chiuse":
            _persiana(F, u0, uc, z0, z1, shut, rng)
            _persiana(F, uc, u1, z0, z1, shut, rng)
            F.rect(uc - 0.015, uc + 0.015, z0, z1, None, mul=0.6)
        else:
            _persiana(F, u0, uc, z0, z1, shut, rng)
            _persiana(F, u1 + 0.16, u1 + 0.16 + hw, z0, z1, shut, rng)
    # balcone del piano nobile (lastra in ombra sotto)
    if p["balcony"]:
        F.rect(W / 2 - W / p["nb"] * 1.05, W / 2 + W / p["nb"] * 1.05, G_H - 0.25, G_H + 0.12, None, mul=0.8)
    # attico: fascia di finestrelle sotto il cornicione (A)
    if p["attic"]:
        F.rect(0, W, Hw - 0.75, Hw, trim, h=0.6)
        for i in range(p["nb"] * 2):
            uc = (i + 0.5) * W / (p["nb"] * 2)
            F.rect(uc - 0.3, uc + 0.3, Hw - 0.62, Hw - 0.18, (60, 58, 56), h=0.3)
    # fregio sotto il cornicione (B, C)
    if p["frieze"]:
        F.rect(0, W, Hw - 0.8, Hw, trim, h=0.62)
        k = 0
        for uc in np.arange(0.4, W, 0.8):
            F.rect(uc - 0.22, uc + 0.22, Hw - 0.65, Hw - 0.15, np.asarray(_c(p["wall"]) * 0.92), h=0.55)
            k += 1
    # cornicione: chiaro, in ombra in basso, mensole
    F.rect(0, W, Hw, HT, trim, h=0.85, r=0.8)
    rs, cs = F.sl(0, W, Hw, HT)
    hh = rs.stop - rs.start
    F.alb[rs, cs] *= np.linspace(1.0, 0.62, hh)[:, None, None]
    for uc in np.arange(0.3, W, 0.6):
        F.rect(uc - 0.08, uc + 0.08, Hw, Hw + 0.35, None, mul=0.75)
    # sporco: base piu' scura, colature dal cornicione, grana dell'intonaco
    rs, cs = F.sl(0, W, 0, HT)
    zz = np.linspace(HT, 0, rs.stop - rs.start)[:, None]
    g = 1 - 0.10 * np.clip(1 - zz / 1.5, 0, 1) - 0.07 * np.clip((zz - (Hw - 2.5)) / 2.5, 0, 1) * (zz < Hw)
    streak = 1 - 0.05 * np.clip(mm._noise(n, n, 3, p["seed"] + 5)[rs, cs] * tp.resize(
        mm._noise(64, n, 2, p["seed"] + 6)[:, :, None], n, n)[rs, cs, 0], 0, 3)
    F.alb[rs, cs] *= (g * streak)[..., None]
    F.alb *= det[..., None]
    # strisce di servizio in basso: coppi, stucco chiaro, muro liscio
    r_roof = slice(int(n * (1 - V_TRIM)), n)
    r_trim = slice(int(n * (1 - V_WALL)), int(n * (1 - V_TRIM)))
    r_wall = slice(int(n * (1 - V_FAC)), int(n * (1 - V_WALL)))
    u = np.arange(n, dtype=np.float32) / n * W
    ch = 0.5 + 0.5 * np.cos(2 * np.pi * u / 0.22)
    coppo = _c((150, 86, 62))[None, :] * (0.72 + 0.28 * ch[:, None]) * (1 + 0.08 * rng.standard_normal((n, 1)))
    rr = r_roof.stop - r_roof.start
    F.alb[r_roof] = coppo[None, :, :] * (0.92 + 0.08 * (np.arange(rr) % 12 < 2))[:, None, None]
    F.alb[r_roof] *= (1 + 0.1 * mm._noise(n, n, 6, p["seed"] + 7)[r_roof])[..., None]
    F.h[r_roof] = 0.5 + 0.3 * ch[None, :]
    F.r[r_roof] = 0.8
    F.alb[r_trim] = _c(trim) * det[r_trim][..., None] * 0.92
    F.h[r_trim] = 0.5
    F.alb[r_wall] = _c(wall) * det[r_wall][..., None]
    F.h[r_wall] = 0.5
    alb = np.clip(F.alb, 0, 1)
    nrm, ao = mm._normal_ao(F.h, 4.0, 2.5, 1.2)
    out = [_save(alb, name + "_D"), _save(nrm, name + "_N"),
           _save(mm._orm(ao, F.r, np.zeros_like(ao)), name + "_ORM")]
    return out


# =============================================================================================================
# auto generiche (atlante condiviso)
# =============================================================================================================
AUTO_COL = {"bianco": (228, 230, 230), "grigio": (138, 142, 148), "blu": (40, 60, 108)}
AUTO_COLS = ["bianco", "grigio", "blu"]     # colonna dell'atlante (terzi di U)


def _auto_cap(A, c0, c1, r0, r1, col, front):
    """Faccia frontale/posteriore in coordinate normalizzate (yn -1..1 su U, zn 0..1 su V)."""
    hh, ww = r1 - r0, c1 - c0
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    zn = 1 - yy / (hh - 1)
    yn = xx / (ww - 1) * 2 - 1
    c = np.broadcast_to(_c(col), (hh, ww, 3)).copy()
    c *= (0.85 + 0.15 * zn)[..., None]
    bump = zn < 0.22
    c[bump] = c[bump] * 0.55 + _c((30, 30, 32)) * 0.45
    if front:
        grille = (np.abs(yn) < 0.45) & (zn > 0.28) & (zn < 0.55)
        c[grille] = _c((24, 25, 27))
        lamp = (np.abs(yn) > 0.55) & (np.abs(yn) < 0.92) & (zn > 0.55) & (zn < 0.78)
        c[lamp] = _c((214, 218, 222))
    else:
        lamp = (np.abs(yn) > 0.58) & (np.abs(yn) < 0.95) & (zn > 0.55) & (zn < 0.80)
        c[lamp] = _c((150, 20, 22))
        plate_area = (np.abs(yn) < 0.32) & (zn > 0.30) & (zn < 0.45)     # vano targa vuoto (niente targa)
        c[plate_area] = c[plate_area] * 0.8
    A[r0:r1, c0:c1] = c


def make_tex_auto(n=1024, seed=931, name="T_Morin_Auto"):
    A = np.zeros((n, n, 3), np.float32)
    R = np.full((n, n), 0.35, np.float32)
    M = np.zeros((n, n), np.float32)
    q = n // 4
    t3 = [0, n // 3, 2 * n // 3, n]
    for i, k in enumerate(AUTO_COLS):
        c0, c1 = t3[i], t3[i + 1]
        g = np.linspace(1.0, 0.82, q)[:, None, None]       # carrozzeria: piu' chiara in alto (riga 0 = alto)
        A[0:q, c0:c1] = _c(AUTO_COL[k]) * g
        R[0:q, c0:c1] = 0.28
        M[0:q, c0:c1] = 0.5 if k != "bianco" else 0.0
        _auto_cap(A, c0, c1, q, 2 * q, AUTO_COL[k], True)
        _auto_cap(A, c0, c1, 2 * q, 3 * q, AUTO_COL[k], False)
        R[q:3 * q, c0:c1] = 0.35
    # riga bassa: vetro | plastica | ruota | luci
    r0 = 3 * q
    t = np.linspace(0, 1, q)[:, None, None]
    A[r0:n, 0:q] = _c((30, 36, 44)) + _c((130, 146, 160)) * (1 - t) * 0.5
    R[r0:n, 0:q] = 0.08
    A[r0:n, q:2 * q] = _c((32, 32, 34))
    R[r0:n, q:2 * q] = 0.7
    yy, xx = np.mgrid[0:q, 0:q].astype(np.float32)
    rr = np.hypot(xx - q / 2, yy - q / 2) / (q / 2)
    ang = np.arctan2(yy - q / 2, xx - q / 2)
    spokes = (np.cos(ang * 5) > 0.3) & (rr > 0.16) & (rr < 0.58)
    wc = np.empty((q, q, 3), np.float32)
    wc[:] = _c((26, 26, 28))                           # gomma
    wc[rr < 0.62] = _c((44, 44, 46))                   # fondo del cerchio
    wc[spokes] = _c((150, 152, 156))                   # razze
    wc[(rr >= 0.58) & (rr < 0.62)] = _c((150, 152, 156))
    wc[rr <= 0.16] = _c((160, 162, 166))               # mozzo
    A[r0:n, 2 * q:3 * q] = wc
    R[r0:n, 2 * q:3 * q] = np.where(rr < 0.62, 0.35, 0.85)
    M[r0:n, 2 * q:3 * q] = np.where(rr < 0.62, 0.8, 0.0)
    A[r0:n, 3 * q:n] = _c((150, 20, 22))
    A = np.clip(A * (1 + 0.02 * mm._noise(n, n, 3, seed)[..., None]), 0, 1)
    h = np.full((n, n), 0.5, np.float32)
    nrm = tp.normal_dx(h, 1.0)
    out = [_save(A, name + "_D"), _save(nrm, name + "_N"), _save(mm._orm(np.ones_like(R), R, M), name + "_ORM")]
    return out


def make_textures():
    out = make_tex_prato() + make_tex_bosso() + make_tex_segnaletica() + make_tex_auto()
    for k, p in PAL.items():
        out += make_tex_palazzo(k.replace("SM_Fondale_", "T_Fondale_"), p)
    print("texture:", out)
    return out


def build_materials():
    t = TEXDIR + "/"
    for m, tx in (("M_Morin_Prato", "T_Morin_Prato"), ("M_Morin_Bosso", "T_Morin_Bosso"),
                  ("M_Viale_Segnaletica", "T_Viale_Segnaletica"), ("M_Morin_Auto", "T_Morin_Auto")):
        pk._pbr_material(m, t + tx + "_D.png", t + tx + "_N.png", t + tx + "_ORM.png")
    for k in PAL:
        tx = k.replace("SM_Fondale_", "T_Fondale_")
        pk._pbr_material(k.replace("SM_", "M_"), t + tx + "_D.png", t + tx + "_N.png", t + tx + "_ORM.png")
    if "M_Molo_Asfalto" not in bpy.data.materials or bpy.data.materials["M_Molo_Asfalto"].library:
        m = MOLO_TEX + "/"
        pk._pbr_material("M_Molo_Asfalto", m + "T_Molo_Asfalto_D.png", m + "T_Molo_Asfalto_N.png", m + "T_Molo_Asfalto_ORM.png")
    if "M_Pav_Fascia" not in bpy.data.materials:
        pk.build_materials(make_textures=False)
    return True


# =============================================================================================================
# geometria: utilita'
# =============================================================================================================
def _face(bm, layer, pts, uvs, mi=0):
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    f.material_index = mi
    for lp, uv in zip(f.loops, uvs):
        lp[layer].uv = uv
    return f


def _finish(name, bm, mats, coll):
    return pk._finish(name, bm, mats, coll, uv=None)


# =============================================================================================================
# prato e aiuole
# =============================================================================================================
def build_prato(coll, name="SM_Morin_Prato_Giardini"):
    """Suolo del prato (pezzo unico, origine all'angolo X 117,5 / Y 101,9): copre le aiuole provvisorie e le lastre del
    blockout v4 fra panchina e viale. UV in metri / 4 (tile della texture)."""
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    L, Wd = PRATO_X[1] - PRATO_X[0], PRATO_Y[1] - PRATO_Y[0]
    T = 4.0
    nx, ny = 10, 2          # griglia rada: niente triangoli lunghi 130 m (precisione delle ombre/nebbia)
    xs = np.linspace(0, L, nx + 1)
    ys = np.linspace(0, Wd, ny + 1)
    z = Z_PRATO
    for i in range(nx):
        for j in range(ny):
            pts = [(xs[i], ys[j], z), (xs[i + 1], ys[j], z), (xs[i + 1], ys[j + 1], z), (xs[i], ys[j + 1], z)]
            _face(bm, layer, pts, [((PRATO_X[0] + p[0]) / T, (PRATO_Y[0] + p[1]) / T) for p in pts])
    # bordi verticali: lato panchina e lato chiosco fino a -0,05 (niente fessure), lato viale sotto il cordolo
    zb = -0.05
    for (a, b) in (((0, 0), (L, 0)), ((L, Wd), (0, Wd)), ((0, Wd), (0, 0)), ((L, 0), (L, Wd))):
        pts = [(a[0], a[1], zb), (b[0], b[1], zb), (b[0], b[1], z), (a[0], a[1], z)]
        _face(bm, layer, pts, [(0, 0), (1, 0), (1, 0.03), (0, 0.03)])
    o = _finish(name, bm, ["M_Morin_Prato"], coll)
    pk._ucx(name, [(0.0, L, 0.0, 118.0 - PRATO_Y[0], -0.30, z)], coll)   # solo fino alla barriera (Y 118)
    return o


AIU_PTS = [(-6.0, 0.0), (-4.4, -1.5), (4.4, -1.5), (6.0, 0.0), (4.4, 1.5), (-4.4, 1.5)]   # esagono allungato 12 x 3 m [S]
AIU_W, AIU_H = 0.35, 0.36


def _inset(pts, d):
    P = [Vector((x, y)) for x, y in pts]
    n = len(P)
    out = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        e1 = (b - a).normalized(); e2 = (c - b).normalized()
        n1 = Vector((-e1.y, e1.x)); n2 = Vector((-e2.y, e2.x))     # normali interne (poligono antiorario)
        m = (n1 + n2).normalized()
        out.append(b + m * (d / max(m.dot(n1), 0.2)))
    return [(v.x, v.y) for v in out]


def build_aiuola(coll, name="SM_Morin_Aiuola_Bosso", lod=0):
    """Aiuola geometrica bordata di bosso (foto: prato con aiuole bordate di siepi basse). Origine al centro, a terra
    (si posa a Z_PRATO). Bordura 0,35 x 0,36 m smussata in cima; dentro arbusti bassi (stesso materiale, piu' bassi)."""
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    out = AIU_PTS
    inn = _inset(out, AIU_W)
    T = 1.5
    sm = 0.07 if lod == 0 else 0.0
    out_t = _inset(out, sm) if sm else out
    inn_t = _inset(out, AIU_W - sm) if sm else inn
    n = len(out)
    zc = 0.18                                   # riempimento interno
    def wall(a, b, z0, z1, s0):
        L = (Vector(b) - Vector(a)).length
        pts = [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]
        _face(bm, layer, pts, [(s0 / T, z0 / T), ((s0 + L) / T, z0 / T), ((s0 + L) / T, z1 / T), (s0 / T, z1 / T)])
        return L
    s = 0.0
    for i in range(n):
        a, b = out[i], out[(i + 1) % n]
        if sm:
            wall(a, b, -0.03, AIU_H - sm, s)
            at, bt = out_t[i], out_t[(i + 1) % n]
            pts = [(a[0], a[1], AIU_H - sm), (b[0], b[1], AIU_H - sm), (bt[0], bt[1], AIU_H), (at[0], at[1], AIU_H)]
            _face(bm, layer, pts, [(p[0] / T, p[1] / T) for p in pts])
        else:
            wall(a, b, -0.03, AIU_H, s)
        s += (Vector(b) - Vector(a)).length
    # cima della bordura
    for i in range(n):
        a, b = out_t[i], out_t[(i + 1) % n]
        c, d = inn_t[(i + 1) % n], inn_t[i]
        pts = [(a[0], a[1], AIU_H), (b[0], b[1], AIU_H), (c[0], c[1], AIU_H), (d[0], d[1], AIU_H)]
        _face(bm, layer, pts, [(p[0] / T, p[1] / T) for p in pts])
    # lato interno della bordura (verso il riempimento)
    for i in range(n):
        a, b = inn[(i + 1) % n], inn[i]
        if sm:
            ti, tj = inn_t[i], inn_t[(i + 1) % n]
            pts = [(ti[0], ti[1], AIU_H), (tj[0], tj[1], AIU_H), (a[0], a[1], AIU_H - sm), (b[0], b[1], AIU_H - sm)]
            _face(bm, layer, pts, [(p[0] / T, p[1] / T) for p in pts])
        if lod < 2:
            wall(a, b, zc, AIU_H - sm, 0.0)
    # riempimento: arbusti bassi (leggermente bombato al centro in LOD0)
    if lod == 0:
        mid = [(x * 0.5, y * 0.5) for x, y in inn]
        for i in range(n):
            a, b = inn[i], inn[(i + 1) % n]
            c, d = mid[(i + 1) % n], mid[i]
            pts = [(a[0], a[1], zc), (b[0], b[1], zc), (c[0], c[1], zc + 0.06), (d[0], d[1], zc + 0.06)]
            _face(bm, layer, pts, [(p[0] / T * 1.6, p[1] / T * 1.6) for p in pts])
        pts = [(x, y, zc + 0.06) for x, y in mid]
        _face(bm, layer, pts, [(p[0] / T * 1.6, p[1] / T * 1.6) for p in pts])
    else:
        z = zc if lod == 1 else AIU_H
        pts = [(x, y, z) for x, y in inn]
        _face(bm, layer, pts, [(p[0] / T * 1.6, p[1] / T * 1.6) for p in pts])
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish(name + sfx, bm, ["M_Morin_Bosso"], coll)
    if lod == 0:
        pk._ucx(name, [(-6.0, 6.0, -1.5, 1.5, -0.05, AIU_H)], coll)
    return o


# =============================================================================================================
# Viale Italia: modulo da 19 m
# =============================================================================================================
def build_strada(coll, name="SM_Viale_Italia_Strada", lod=0):
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    L = MOD_L
    y0 = Y0_STRADA
    T = TILE_ASF
    nseg = 4 if lod < 2 else 1      # 4 tratti da 4,75 m: niente triangoli troppo lunghi
    xs = np.linspace(0, L, nseg + 1)
    prev_z = 0.0
    for k, (ya, yb, z, mi) in enumerate(BANDE):
        a, b = ya - y0, yb - y0
        t = T if mi == 0 else 1.0
        for i in range(nseg):
            pts = [(xs[i], a, z), (xs[i + 1], a, z), (xs[i + 1], b, z), (xs[i], b, z)]
            _face(bm, layer, pts, [(p[0] / t, (p[1] + y0) / t) for p in pts], mi)
        # gradino verso la fascia precedente (o verso il prato/suolo per la prima)
        if abs(z - prev_z) > 1e-3 and (lod < 2 or k == 0):
            z0, z1 = min(z, prev_z), max(z, prev_z)
            if z > prev_z:      # faccia rivolta a -Y
                pts = [(0, a, z0), (L, a, z0), (L, a, z1), (0, a, z1)]
            else:               # faccia rivolta a +Y
                pts = [(L, a, z0), (0, a, z0), (0, a, z1), (L, a, z1)]
            _face(bm, layer, pts, [(p[0] / 1.0, p[2] / 1.0) for p in pts], 1)
        prev_z = z
    # bordo lato Giardini pubblici (Y 145) giu' fino al suolo
    a = BANDE[-1][1] - y0
    pts = [(L, a, -0.05), (0, a, -0.05), (0, a, prev_z), (L, a, prev_z)]
    _face(bm, layer, pts, [(p[0], p[2]) for p in pts], 1)
    # segnaletica (5 mm sopra il piano)
    dz = 0.005
    def stripe(xa, xb, yc, w, z):
        pts = [(xa, yc - w / 2 - y0, z + dz), (xb, yc - w / 2 - y0, z + dz), (xb, yc + w / 2 - y0, z + dz),
               (xa, yc + w / 2 - y0, z + dz)]
        _face(bm, layer, pts, [(p[0], p[1]) for p in pts], 2)
    for yc, w, z in STRISCE_CONT:
        if lod == 2 and z > 0.1:
            continue
        stripe(0.0, L, yc, w, z)
    for yc, w in STRISCE_TRAT:
        for xa in (0.25, 0.25 + L / 2):
            stripe(xa, xa + 4.5, yc, w, 0.02)
    if lod == 0:    # stalli di sosta lato giardini, uno ogni 4,75 m
        for xa in np.arange(0.0, L - 0.01, 4.75):
            pts = [(xa, 121.05 - y0, 0.02 + dz), (xa + 0.1, 121.05 - y0, 0.02 + dz), (xa + 0.1, 123.24 - y0, 0.02 + dz),
                   (xa, 123.24 - y0, 0.02 + dz)]
            _face(bm, layer, pts, [(p[0], p[1]) for p in pts], 2)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    return _finish(name + sfx, bm, ["M_Molo_Asfalto", "M_Pav_Fascia", "M_Viale_Segnaletica"], coll)


# =============================================================================================================
# auto generiche
# =============================================================================================================
# stazioni lungo X (t 0 = retro, 1 = muso): (t, z basso, z cintura, z tetto, scala larghezza, scala tetto)
AUTO = {
    "SM_Morin_Auto_A": dict(L=3.95, W=1.74, H=1.50, r=0.31, wb=2.50, col=0, st=[    # utilitaria a 5 porte
        (0.00, 0.34, 0.86, 0.86, 0.93, 0.0), (0.03, 0.28, 0.92, 1.16, 0.97, 0.80), (0.12, 0.26, 0.95, 1.46, 1.0, 0.84),
        (0.40, 0.25, 0.95, 1.50, 1.0, 0.86), (0.60, 0.25, 0.94, 1.47, 1.0, 0.85), (0.70, 0.26, 0.92, 1.24, 1.0, 0.83),
        (0.80, 0.28, 0.88, 0.94, 0.99, 0.0), (0.95, 0.32, 0.80, 0.82, 0.96, 0.0), (1.00, 0.40, 0.72, 0.73, 0.90, 0.0)]),
    "SM_Morin_Auto_B": dict(L=4.35, W=1.82, H=1.64, r=0.34, wb=2.64, col=1, st=[    # SUV compatto
        (0.00, 0.40, 0.98, 0.98, 0.94, 0.0), (0.03, 0.34, 1.02, 1.36, 0.98, 0.82), (0.10, 0.32, 1.04, 1.60, 1.0, 0.86),
        (0.45, 0.32, 1.04, 1.64, 1.0, 0.87), (0.62, 0.32, 1.03, 1.60, 1.0, 0.86), (0.72, 0.33, 1.00, 1.30, 1.0, 0.84),
        (0.80, 0.34, 0.98, 1.02, 1.0, 0.0), (0.96, 0.38, 0.92, 0.94, 0.97, 0.0), (1.00, 0.46, 0.84, 0.85, 0.92, 0.0)]),
    "SM_Morin_Auto_C": dict(L=4.45, W=1.76, H=1.45, r=0.31, wb=2.62, col=2, st=[    # berlina a 3 volumi
        (0.00, 0.36, 0.82, 0.83, 0.92, 0.0), (0.04, 0.30, 0.90, 0.93, 0.97, 0.0), (0.18, 0.28, 0.92, 0.98, 1.0, 0.0),
        (0.26, 0.27, 0.93, 1.38, 1.0, 0.84), (0.50, 0.27, 0.93, 1.45, 1.0, 0.86), (0.63, 0.27, 0.92, 1.40, 1.0, 0.85),
        (0.74, 0.28, 0.89, 0.97, 0.99, 0.0), (0.95, 0.32, 0.80, 0.82, 0.96, 0.0), (1.00, 0.40, 0.72, 0.73, 0.90, 0.0)]),
}


def _auto_section(L, W, s):
    t, lo, belt, top, ws, wr = s
    x = -L / 2 + t * L
    w = W / 2 * ws
    cab = wr > 0
    wt = w * (wr if cab else 0.92)
    ztop = top if cab else max(top, belt + 0.03)
    pts = [(-w * 0.90, lo), (-w, lo + 0.14), (-w, belt), (-wt, ztop), (wt, ztop), (w, belt), (w, lo + 0.14), (w * 0.90, lo)]
    return x, pts, cab


def build_auto(coll, name, lod=0):
    a = AUTO[name]
    L, W = a["L"], a["W"]
    st = a["st"]
    if lod == 1:
        st = [st[i] for i in (0, 2, 3, 5, 6, 8)]
    elif lod == 2:
        st = [st[i] for i in (0, 3, 6, 8)]
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    secs = [_auto_section(L, W, s) for s in st]
    rows = []
    for x, pts, cab in secs:
        rows.append([bm.verts.new((x, y, z)) for (y, z) in pts])
    col = a["col"]
    u0, u1 = col / 3, (col + 1) / 3
    BODY = (u0 + 0.02, 0.77, u1 - 0.02, 0.98)
    GLASS = (0.02, 0.02, 0.23, 0.23)
    PLAST = (0.27, 0.02, 0.48, 0.23)
    def uvr(rect, f, gx, gz):
        # proiezione semplice dentro il rettangolo (x lungo, z alto)
        for lp in f.loops:
            c = lp.vert.co
            fu = (c.x + L / 2) / L
            fv = c.z / a["H"]
            lp[layer].uv = (rect[0] + (rect[2] - rect[0]) * min(max(fu, 0), 1), rect[1] + (rect[3] - rect[1]) * min(max(fv, 0), 1))
    nseg = 8
    for i in range(len(rows) - 1):
        A, B = rows[i], rows[i + 1]
        cab = secs[i][2] and secs[i + 1][2]
        for k in range(nseg):
            k2 = (k + 1) % nseg
            f = bm.faces.new((A[k], A[k2], B[k2], B[k]))
            f.normal_update()
            if k == 7:
                rect = PLAST
            elif k in (2, 4) and cab:
                rect = GLASS
            elif k == 3 and abs(f.normal.x) > 0.45 and (secs[i][2] or secs[i + 1][2]):
                rect = GLASS
            elif k in (2, 4) and (secs[i][2] or secs[i + 1][2]) and abs(f.normal.x) > 0.3:
                rect = GLASS
            else:
                rect = BODY
            uvr(rect, f, 0, 0)
    # tappi retro e muso
    for idx, front in ((0, False), (len(rows) - 1, True)):
        vs = rows[idx] if front else list(reversed(rows[idx]))
        f = bm.faces.new(vs)
        ys = [v.co.y for v in vs]; zs = [v.co.z for v in vs]
        y0, y1, z0, z1 = min(ys), max(ys), min(zs), max(zs)
        rv = (0.5, 0.73) if front else (0.27, 0.48)
        for lp in f.loops:
            c = lp.vert.co
            fu = (c.y - y0) / (y1 - y0)
            if not front:
                fu = fu
            fv = (c.z - z0) / max(z1 - z0, 1e-3)
            lp[layer].uv = (u0 + 0.01 + (u1 - u0 - 0.02) * fu, rv[0] + (rv[1] - rv[0]) * fv)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))     # solo la scocca (chiusa); le ruote sono orientate a mano
    # ruote
    sides = (16, 10, 6)[lod]
    r = a["r"]
    for sx in (-a["wb"] / 2, a["wb"] / 2):
        for sy in (-1, 1):
            yo = sy * (W / 2 + 0.01)
            yi = sy * (W / 2 - 0.21)
            ring_o, ring_i = [], []
            for j in range(sides):
                ang = 2 * math.pi * j / sides
                x, z = sx + r * math.cos(ang), r + r * math.sin(ang)
                ring_o.append(bm.verts.new((x, yo, z)))
                ring_i.append(bm.verts.new((x, yi, z)))
            for j in range(sides):
                j2 = (j + 1) % sides
                f = bm.faces.new((ring_o[j], ring_o[j2], ring_i[j2], ring_i[j]) if sy > 0 else
                                 (ring_i[j], ring_i[j2], ring_o[j2], ring_o[j]))
                for lp in f.loops:
                    lp[layer].uv = (0.30, 0.10)
            f = bm.faces.new(ring_o if sy < 0 else list(reversed(ring_o)))
            for lp in f.loops:
                c = lp.vert.co
                lp[layer].uv = (0.5 + 0.25 * (0.5 + 0.5 * (c.x - sx) / r), 0.0 + 0.25 * (0.5 + 0.5 * (c.z - r) / r))
    sfx = "" if lod == 0 else f"_LOD{lod}"
    return _finish(name + sfx, bm, ["M_Morin_Auto"], coll)


# =============================================================================================================
# palazzi d'epoca
# =============================================================================================================
def _uv_fac(p, s, z):
    Hw, HT = _pal_dims(p)
    return (s / p["W"], V_FAC + (1 - V_FAC) * min(max(z, 0.0), HT) / HT)


def _facade(bm, layer, p, P0, t, nrm, L, Hw, wins, recess=True, mi=0):
    """Facciata rettangolare da P0 lungo t (lunghezza L, quota 0..Hw) con le aperture `wins` incassate."""
    P0, t, nrm = Vector(P0), Vector(t), Vector(nrm)
    flip = t.cross(Vector((0, 0, 1))).dot(nrm) < 0
    def V(s, z, d=0.0):
        return P0 + t * s + Vector((0, 0, z)) - nrm * d
    def quad(pts3, uvs):
        if flip:
            pts3 = pts3[::-1]; uvs = uvs[::-1]
        _face(bm, layer, pts3, uvs, mi)
    if not recess or not wins:
        quad([V(0, 0), V(L, 0), V(L, Hw), V(0, Hw)], [_uv_fac(p, 0, 0), _uv_fac(p, L, 0), _uv_fac(p, L, Hw), _uv_fac(p, 0, Hw)])
        return
    xs = sorted({0.0, L} | {w[0] for w in wins} | {w[1] for w in wins})
    zs = sorted({0.0, Hw} | {w[2] for w in wins} | {w[3] for w in wins})
    def owner(s, z):
        for i, w in enumerate(wins):
            if w[0] - 1e-6 <= s <= w[1] + 1e-6 and w[2] - 1e-6 <= z <= w[3] + 1e-6:
                return i
        return -1
    nx, nz = len(xs) - 1, len(zs) - 1
    own = [[owner((xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2) for j in range(nz)] for i in range(nx)]
    for i in range(nx):
        for j in range(nz):
            s0, s1, z0, z1 = xs[i], xs[i + 1], zs[j], zs[j + 1]
            o = own[i][j]
            d = wins[o][4] if o >= 0 else 0.0
            quad([V(s0, z0, d), V(s1, z0, d), V(s1, z1, d), V(s0, z1, d)],
                 [_uv_fac(p, s0, z0), _uv_fac(p, s1, z0), _uv_fac(p, s1, z1), _uv_fac(p, s0, z1)])
            if o < 0:
                continue
            tr = (0.5, V_WALL - 0.002)
            tu = [(0.0, V_TRIM + 0.002), (0.25, V_TRIM + 0.002), (0.25, V_WALL - 0.002), (0.0, V_WALL - 0.002)]
            # spallette sui lati del vano che confinano con il muro
            if i == 0 or own[i - 1][j] != o:
                quad([V(s0, z0, 0), V(s0, z0, d), V(s0, z1, d), V(s0, z1, 0)], tu)
            if i == nx - 1 or own[i + 1][j] != o:
                quad([V(s1, z0, d), V(s1, z0, 0), V(s1, z1, 0), V(s1, z1, d)], tu)
            if j == 0 or own[i][j - 1] != o:
                quad([V(s0, z0, 0), V(s1, z0, 0), V(s1, z0, d), V(s0, z0, d)], tu)
            if j == nz - 1 or own[i][j + 1] != o:
                quad([V(s0, z1, d), V(s1, z1, d), V(s1, z1, 0), V(s0, z1, 0)], tu)


def _ring(bm, layer, p, W, D, prof, mi=0, trim_under=True):
    """Anello di modanatura attorno al rettangolo (x -W/2..W/2, y 0..D): prof = [(sporgenza, z), ...] dal basso."""
    corners = [Vector((-W / 2, 0)), Vector((W / 2, 0)), Vector((W / 2, D)), Vector((-W / 2, D))]
    outs = [Vector((-1, -1)), Vector((1, -1)), Vector((1, 1)), Vector((-1, 1))]
    sides = [(0, 1), (1, 2), (2, 3), (3, 0)]
    for (ia, ib) in sides:
        A, B = corners[ia], corners[ib]
        L = (B - A).length
        for k in range(len(prof) - 1):
            (oa, za), (ob, zb) = prof[k], prof[k + 1]
            pa0 = A + outs[ia] * oa; pb0 = B + outs[ib] * oa
            pa1 = A + outs[ia] * ob; pb1 = B + outs[ib] * ob
            pts = [(pa0.x, pa0.y, za), (pb0.x, pb0.y, za), (pb1.x, pb1.y, zb), (pa1.x, pa1.y, zb)]
            vert = abs(zb - za) > abs(ob - oa)
            if vert:
                uvs = [_uv_fac(p, 0, za), _uv_fac(p, L, za), _uv_fac(p, L, zb), _uv_fac(p, 0, zb)]
            else:
                uvs = [(0.0, V_TRIM + 0.004), (L / p["W"], V_TRIM + 0.004), (L / p["W"], V_WALL - 0.004), (0.0, V_WALL - 0.004)]
            f = _face(bm, layer, pts, uvs, mi)
            f.normal_update()
            # orientamento: le facce dell'anello guardano verso l'esterno o verso il basso/alto
            c = sum((Vector(q) for q in pts), Vector()) / 4
            mid = Vector(((A.x + B.x) / 2, (A.y + B.y) / 2, c.z))
            outward = Vector((c.x - mid.x, c.y - mid.y, 0))
            side_out = Vector((outs[ia].x + outs[ib].x, outs[ia].y + outs[ib].y, 0)).normalized()
            want = side_out if vert else (Vector((0, 0, -1)) if zb > za and ob > oa else Vector((0, 0, 1)))
            if f.normal.dot(want) < 0:
                f.normal_flip()


def _roof(bm, layer, W, D, z, ov, pitch=22.0):
    x0, x1, y0, y1 = -W / 2 - ov, W / 2 + ov, -ov, D + ov
    hd = (y1 - y0) / 2
    hr = hd * math.tan(math.radians(pitch))
    rx0, rx1 = x0 + hd, x1 - hd
    ym = (y0 + y1) / 2
    zr = z + hr
    sl = math.hypot(hd, hr)
    def uvr(pt, along, up):
        return (along / W, (up / sl) * (V_TRIM - 0.004))
    # falda anteriore e posteriore
    _face(bm, layer, [(x0, y0, z), (x1, y0, z), (rx1, ym, zr), (rx0, ym, zr)],
          [uvr(0, 0, 0), uvr(0, x1 - x0, 0), uvr(0, rx1 - x0, sl), uvr(0, rx0 - x0, sl)])
    _face(bm, layer, [(x1, y1, z), (x0, y1, z), (rx0, ym, zr), (rx1, ym, zr)],
          [uvr(0, 0, 0), uvr(0, x1 - x0, 0), uvr(0, x1 - rx0, sl), uvr(0, x1 - rx1, sl)])
    # padiglioni laterali
    _face(bm, layer, [(x0, y1, z), (x0, y0, z), (rx0, ym, zr)], [uvr(0, 0, 0), uvr(0, y1 - y0, 0), uvr(0, hd, sl)])
    _face(bm, layer, [(x1, y0, z), (x1, y1, z), (rx1, ym, zr)], [uvr(0, 0, 0), uvr(0, y1 - y0, 0), uvr(0, hd, sl)])
    # sottogronda (chiude il cornicione dall'alto)
    return zr


def build_palazzo(coll, name, lod=0):
    p = PAL[name]
    W, D = p["W"], p["D"]
    Hw, HT = _pal_dims(p)
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    wf = _pal_windows(p, W)
    ws = _pal_windows(p, D)
    rec_front = lod <= 1
    rec_side = lod == 0
    _facade(bm, layer, p, (-W / 2, 0, 0), (1, 0, 0), (0, -1, 0), W, Hw, wf, rec_front)          # fronte
    _facade(bm, layer, p, (W / 2, 0, 0), (0, 1, 0), (1, 0, 0), D, Hw, ws, rec_side)             # fianco destro
    _facade(bm, layer, p, (-W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), D, Hw, ws, rec_side)           # fianco sinistro
    _facade(bm, layer, p, (W / 2, D, 0), (-1, 0, 0), (0, 1, 0), W, Hw, wf, False)               # retro (piatto)
    if lod == 0:
        _ring(bm, layer, p, W, D, [(0.0, G_H - 0.05), (0.12, G_H - 0.02), (0.12, G_H + 0.28), (0.0, G_H + 0.30)])
        _ring(bm, layer, p, W, D, [(0.0, Hw), (0.18, Hw + 0.06), (0.18, Hw + 0.35), (0.62, Hw + 0.52), (0.62, HT)])
    elif lod == 1:
        _ring(bm, layer, p, W, D, [(0.0, Hw), (0.62, Hw + 0.5), (0.62, HT)])
    else:
        _ring(bm, layer, p, W, D, [(0.0, Hw), (0.0, HT)])
    ov = 0.62 if lod < 2 else 0.0
    _roof(bm, layer, W, D, HT, ov)
    if lod < 2:
        # comignoli
        rng = np.random.default_rng(p["seed"])
        for k in range(3 if lod == 0 else 2):
            cx = rng.uniform(-W / 2 + 3, W / 2 - 3)
            cy = rng.uniform(D * 0.3, D * 0.7)
            hz = HT + (D / 2 + ov - abs(cy - D / 2)) * math.tan(math.radians(22.0))
            for f in pk._box(bm, cx - 0.35, cx + 0.35, cy - 0.3, cy + 0.3, HT, hz + 1.2,
                             faces=("top", "xn", "xp", "yn", "yp")):
                for lp in f.loops:
                    lp[layer].uv = (0.1 + 0.05 * (lp.vert.co.x - cx), V_WALL + 0.01)
    if p["balcony"] and lod < 2:
        bw = W / p["nb"] * 1.05
        faces = pk._box(bm, -bw, bw, -0.95, 0.0, G_H + 0.02, G_H + 0.20, faces=("top", "bot", "xn", "xp", "yn"))
        faces += pk._box(bm, -bw, bw, -0.95, -0.83, G_H + 0.20, G_H + 1.15, faces=("top", "xn", "xp", "yn", "yp"))
        faces += pk._box(bm, -bw, -bw + 0.12, -0.83, 0.0, G_H + 0.20, G_H + 1.15, faces=("top", "xp", "yn"))
        faces += pk._box(bm, bw - 0.12, bw, -0.83, 0.0, G_H + 0.20, G_H + 1.15, faces=("top", "xn", "yn"))
        for f in faces:
            for lp in f.loops:
                c = lp.vert.co
                lp[layer].uv = (0.3 + 0.02 * (c.x + c.y), V_TRIM + 0.005 + 0.02 * (c.z - G_H) / 1.2)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    return _finish(name + sfx, bm, [name.replace("SM_", "M_")], coll)


# =============================================================================================================
# kit
# =============================================================================================================
LODDED = ["SM_Viale_Italia_Strada", "SM_Morin_Aiuola_Bosso"] + list(AUTO) + list(PAL)
SINGLE = ["SM_Morin_Prato_Giardini"]


def build_all():
    coll = pk._coll(KIT)
    out = [build_prato(coll)]
    for l in range(3):
        out.append(build_strada(coll, lod=l))
        out.append(build_aiuola(coll, lod=l))
        for nm in AUTO:
            out.append(build_auto(coll, nm, l))
        for nm in PAL:
            out.append(build_palazzo(coll, nm, l))
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    for o in sorted(out, key=lambda o: o.name):
        print(f"{o.name:<36} tri {pk.tri_count(o):>6}  dim {tuple(round(d, 2) for d in o.dimensions)}")
    return out


# =============================================================================================================
# disposizione (coordinate Blender) e CSV in coordinate UE
# =============================================================================================================
# Palazzi sui fronti delle isole di SM_Blockout_Fondale_v2_Edifici (= sagome OSM). Fronte su Y del lato verso il mare.
PALAZZI = [
    # fronte su Viale Mazzini (Y ~206-208) [V OSM]
    ("SM_Fondale_Palazzo_C", 159.0, 207.0),   # isola 49 (X 149-169)
    ("SM_Fondale_Palazzo_A", 188.0, 206.0),   # isola 16 (X 178-198): il palazzo giallo della foto
    ("SM_Fondale_Palazzo_C", 239.0, 208.0),   # isola 15 (X 230-248)
    ("SM_Fondale_Palazzo_B", 272.3, 207.0),   # isola 10 (X 260-309): il lungo palazzo rosa a destra nella foto
    ("SM_Fondale_Palazzo_B", 296.7, 207.0),
    ("SM_Fondale_Palazzo_A", 330.0, 207.0),   # OSM 205844171 (X 320-370)
    ("SM_Fondale_Palazzo_B", 357.5, 207.0),
    # seconda fila (Y ~253-266), visibile nei varchi delle vie trasversali
    ("SM_Fondale_Palazzo_B", 190.0, 254.0),   # isola 5 (X 178-199): il palazzo rosa al centro della foto
    ("SM_Fondale_Palazzo_A", 158.5, 263.0),   # isola 29 (X 149-168)
    ("SM_Fondale_Palazzo_C", 216.0, 266.0),   # isole 14/39 (X 205-241)
    ("SM_Fondale_Palazzo_A", 239.0, 253.0),   # isole 33/37 (X 229-249)
    ("SM_Fondale_Palazzo_C", 271.0, 254.0),   # isola 50 (X 260-308)
    ("SM_Fondale_Palazzo_A", 296.0, 254.0),
]
# isole di SM_Blockout_Fondale_v2_Edifici sostituite dai palazzi (tolte nel Blockout_Fondale_v3)
ISOLE_V3 = (5, 9, 10, 14, 15, 16, 29, 33, 34, 37, 39, 45, 49, 50)
AIU_X = [128.0 + 16.0 * k for k in range(8)]       # X 128-240, Y 110 [S]
AIU_Y = 110.0


def _auto_rows(rng):
    rows = []
    names = list(AUTO)
    k = 0
    for (y, yaw, x0, x1, gap_p) in ((Y_SOSTA_A, 180.0, 118.5, 249.0, 0.10), (Y_SOSTA_B, 0.0, 118.5, 249.0, 0.25)):
        x = x0 + rng.uniform(0, 2)
        while x < x1:
            a = names[int(rng.integers(0, 3))]
            Lc = AUTO[a]["L"]
            if rng.uniform() > gap_p:
                rows.append((a, f"Auto_{k:03d}", x + Lc / 2, y + rng.uniform(-0.08, 0.08), Z_STRADA_AUTO,
                             yaw + rng.uniform(-1.5, 1.5)))
                k += 1
            x += Lc + rng.uniform(0.8, 1.6)
    return rows


Z_STRADA_AUTO = 0.02


def _alberi_rows(rng):
    """Giardini pubblici (Y 147-200): alberi alti gia' in UEFN (latifoglie A/B, pino domestico) e palme, a gruppi con radure."""
    rows = []
    pts = []
    tries = 0
    while len(pts) < 24 and tries < 5000:
        tries += 1
        x, y = rng.uniform(112, 335), rng.uniform(150, 200)
        if any((x - a) ** 2 + (y - b) ** 2 < 12.5 ** 2 for a, b in pts):
            continue
        # radure lungo il viale davanti ai palazzi visti in foto (dal punto di presa X ~218): niente alberi alti
        if 170 < x < 207 or 252 < x < 312 or (207 <= x < 228 and y < 178):
            continue
        pts.append((x, y))
    names = ["SM_Morin_PinoDomestico", "SM_Albero_LatifogliaA", "SM_Albero_LatifogliaB"]
    for i, (x, y) in enumerate(pts):
        a = names[int(rng.choice(3, p=[0.4, 0.3, 0.3]))]
        rows.append((a, f"GiardiniPubblici_{i:02d}", x, y, 0.0, float(rng.uniform(0, 360))))
    # palme alte sul bordo dei Giardini pubblici (foto)
    for i, x in enumerate(np.arange(122, 330, 17.0)):
        rows.append(("SM_Morin_PalmaA", f"GiardiniPubblici_Palma_{i:02d}", float(x + rng.uniform(-3, 3)),
                     float(147.5 + rng.uniform(0, 3)), 0.0, float(rng.uniform(0, 360))))
    return rows


def layout(seed=20261119):
    rng = np.random.default_rng(seed)
    rows = [("SM_Morin_Prato_Giardini", "Prato_Giardini", PRATO_X[0], PRATO_Y[0], 0.0, 0.0)]
    for k in range(STRADA_N):
        rows.append(("SM_Viale_Italia_Strada", f"Viale_Strada_{k:02d}", STRADA_X0 + k * MOD_L, Y0_STRADA, 0.0, 0.0))
    for k, x in enumerate(AIU_X):
        rows.append(("SM_Morin_Aiuola_Bosso", f"Aiuola_{k:02d}", x, AIU_Y, Z_PRATO, 0.0 if k % 2 == 0 else 180.0))
    rows += _auto_rows(rng)
    for k, (a, x, y) in enumerate(PALAZZI):
        rows.append((a, f"Palazzo_{k:02d}", x, y, 0.0, 0.0))
    rows += _alberi_rows(rng)
    return rows


def write_csv(rows, path="exports/viale/viale_posizioni_v1.csv"):
    return mm.write_csv(rows, path)


def build_context(rows, name="VIALE_Contesto"):
    """Istanze per il render. Gli asset esterni (alberi, palma) usano le mesh collegate da arte_molo / contesto."""
    coll = pk._coll(name)
    for a, n, x, y, z, yaw in rows:
        src = bpy.data.objects.get(a)
        me = src.data if src is not None else bpy.data.meshes.get(a) or next(
            (m for m in bpy.data.meshes if m.name.startswith(a + ".") or m.name == a), None)
        if me is None:
            print("manca la mesh", a)
            continue
        nm = "CTXV_" + n
        o = bpy.data.objects.get(nm)
        if o is None:
            o = bpy.data.objects.new(nm, me)
            coll.objects.link(o)
        o.data = me
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(yaw))
    for a in {r[0] for r in rows}:
        o = bpy.data.objects.get(a)
        if o is not None and o.library is None and o.name in bpy.data.collections[KIT].objects:
            o.hide_render = True
            o.hide_viewport = True
    return coll


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in bpy.context.scene.objects}
    for o in bpy.data.collections[KIT].objects:
        o.hide_viewport = False
        o.hide_set(False)
        o.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.update()
    reps = []
    try:
        for nm in SINGLE:
            reps.append(morin_export.export_fbx([bpy.data.objects[nm]], f"{EXPDIR}/{nm}.fbx", mode="asset",
                                                overwrite=overwrite, include_ucx=True, verbose=False))
        for nm in LODDED:
            for lod in (0, 1, 2):
                on = nm if lod == 0 else f"{nm}_LOD{lod}"
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


# =============================================================================================================
# camera e confronto con la foto
# =============================================================================================================
# punto di presa della foto stimato dagli angoli dei palazzi (giallo X 178-198, rosa X 178-199 in 2a fila, lungo rosa
# X 260-309): X ~222, fra i filari (tronchi a X 219 e 228 ai bordi come in foto) di palme, occhi a ~1,9 m sopra i cubetti [S]
CAMS = {"CAM_Viale_F1": ((221.8, 93.4, ZF + 1.9), 0.0, -3.0, 100.0, (1727, 446))}


def cameras():
    mm.CAMS.update(CAMS)
    coll = pk._coll("VIALE_Camere")
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
        cam.data.clip_end = 6000
        cam["res"] = res
        out.append(cam)
    return out


def render_confronto(cam="CAM_Viale_F1", out="docs/qa/arte_viale_v1_confronto.png",
                     foto="ref/foto/vista/prato con alberelli.png", tmp=None):
    tmp = tmp or os.path.join(os.environ.get("TEMP", PROJ), "morin_viale_render.png")
    mm.render(cam, tmp, width=1727)
    a = tp.load(f"{PROJ}/{foto}")[..., :3]
    b = tp.load(tmp)[..., :3]
    if b.shape[1] != a.shape[1]:
        b = tp.resize(b, a.shape[1], int(round(b.shape[0] * a.shape[1] / b.shape[1])))
    sep = np.ones((6, a.shape[1], 3), np.float32)
    tp.save(np.concatenate([a, sep, b], 0), f"{PROJ}/{out}")
    return out, tmp
