"""morin_parcheggio.py — parcheggio iniziale (X 20-95 m, fra la passeggiata e Viale Italia), v1 2026-11-20.
Correzioni al kit Viale v1 (CSV v2: strada fino a X 326, quote dei palazzi oltre X 330).

Schede: ref/zona_parcheggio_chiosco.md §1, ref/radice_molo.md §10.3 (ramo d'asfalto Y 109,25-113,75 fino a X 24, Z +0,01;
angolo in cubetti X 9,55-20, Y 89-109,25, Z +0,15), ref/sezione.md (fascia 6). OSM (ref/osm/morin_bbox.osm):
amenity=parking 850396611 (X 16,5-86,2 a Y 102, lato citta' fino a Y 122 e (106,6; 120,5)), parking_aisle 378872040
((8,9; 109,7) → (88,3; 109,1) → (110,5; 128,2)). Foto: ref/foto/vista/parcheggio_iniziale.png (cattura Street View, deroga
[SV]: grana dell'asfalto presa da una porzione senza UI, persone, targhe, marchi).

Sezione del parcheggio (Y, mondo) [F dalla foto + S]:
  102,00-102,25 cordolo in pietra chiara (top +0,15 = fascia palme)
  102,25-104,75 sosta in linea lato mare (auto a Y 103,5)
  104,75-111,00 corsia (6,25 m, a senso unico verso NE; OSM asse 109,4)
  111,00-113,40 sosta in linea lato citta' (foto: posteriori della 500 e della Suzuki)
  113,40-116,80 aiuola di terra rialzata (+0,12, cordoli in pietra) con le grandi latifoglie a Y 115,1 (OSM: filare a Y 113)
  116,80-120,85 seconda fila a pettine (90°, muso verso le aiuole), servita da Viale Italia (foto: auto rossa di fronte)
Asfalto a Z +0,02 (sopra blockout v5 a 0 e ramo del molo a +0,01; tacca X 20-24 / Y 109,25-114 sul ramo del molo).
Uscita verso Viale Italia in diagonale (OSM) fra X 87-106, a lato del tassello del chiosco (X 95-117, Y 102-113,5).

Esegui dentro blender/arte_parcheggio.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_parcheggio as mp; importlib.reload(mp)
    mp.make_textures(); mp.build_materials(); mp.build_all()
    rows = mp.layout(); mp.write_csv(rows); mp.build_context(rows)
    mp.export_all()
    mp.viale_csv_v2()
    mp.cameras(); mp.render_confronto()
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
TEXDIR = PROJ + "/blender/textures/parcheggio"
KIT = "PARK_Kit"
EXPDIR = "//../exports/parcheggio"
FOTO = PROJ + "/ref/foto/vista/parcheggio_iniziale.png"

Z_ASF = 0.02
Z_CORD = 0.15
Z_TERRA = 0.05
X0, X1 = 20.0, 95.0
Y_CORD0, Y_CORD1 = 102.0, 102.25
Y_SOSTA_MARE = (102.25, 104.75)
Y_CORSIA = (104.75, 111.0)
Y_SOSTA_CITTA = (111.0, 113.4)
Y_AIUOLA = (113.4, 116.8)
Y_PETTINE = (116.8, 120.85)
Y_VIALE = 120.85                              # ciglio di SM_Viale_Italia_Strada
Z_AIUOLA = 0.12
AIU_X = (26.0, 84.0)
NOTCH = (20.0, 24.0, 109.25, 114.0)          # ramo d'asfalto del molo (Z +0,01) con cordolo basso a nord
PETTINE_W = 2.5
PETTINE_X = (26.0, 86.0)
MARE_L = 5.5                                  # posto in linea
MARE_X = (25.0, 85.5)
CITTA_X = (28.0, 83.0)
ZEBRA_X = (25.0, 28.0)

pk.TILE.update({"M_Parcheggio_Asfalto": 8.0, "M_Viale_Segnaletica": 1.0, "M_Pav_Fascia": 1.0, "M_Pav_Terra": 2.0})


def _c(c):
    return np.asarray(c, np.float32) / 255.0


def _save(a, name):
    os.makedirs(TEXDIR, exist_ok=True)
    tp.save(np.clip(a, 0, 1), f"{TEXDIR}/{name}.png")
    return f"{TEXDIR}/{name}.png"


# =============================================================================================================
# texture
# =============================================================================================================
def _foto_detail(size, seed):
    """Grana dell'asfalto dalla foto [SV]: porzione x 300-520, y 560-680 (asfalto in ombra/luce, niente UI ne' targhe)."""
    a = tp.load(FOTO)[560:680, 300:520, :3]
    a = tp.resize(a, a.shape[1] * 3, a.shape[0] * 3)
    hp = np.clip(tp.highpass(tp.lum(a), 4.0), 0.75, 1.25)
    syn = tp.splat_synth(hp[..., None], size, 128, int((size / 128) ** 2 * 5), seed=seed)[..., 0]
    return syn / syn.mean()


def make_tex_asfalto(size=2048, seed=1201, name="T_Parcheggio_Asfalto"):
    """Asfalto scuro consumato (tile 8 m): crepe ramificate, rattoppi rettangolari piu' scuri e lisci, macchie d'olio,
    inerti chiari. Colore medio dalla foto (asfalto al sole ~ (92, 90, 88) sRGB, all'ombra molto piu' scuro)."""
    rng = np.random.default_rng(seed)
    ppm = size / 8.0
    det = _foto_detail(size, seed)
    fine = 1 + 0.08 * mm._noise(size, size, 0.7, seed + 1) + 0.05 * mm._noise(size, size, 2.0, seed + 2)
    base = _c((84, 83, 82))
    big = 1 + 0.06 * mm._noise(size, size, 120, seed + 3)
    alb = base[None, None, :] * (0.6 * det + 0.4 * fine)[..., None] * big[..., None]
    hgt = 0.4 * mm._noise(size, size, 0.8, seed + 6)
    # rattoppi: rettangoli (ruotati poco) di asfalto piu' nuovo, scuro e liscio, con bordo di bitume
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / ppm
    patch = np.zeros((size, size), np.float32)
    edge = np.zeros((size, size), np.float32)
    for _ in range(7):
        cx, cy = rng.uniform(0, 8, 2)
        w, h = rng.uniform(0.6, 2.4), rng.uniform(0.5, 1.6)
        a = math.radians(rng.uniform(-6, 6))
        dx = ((xx - cx + 4) % 8) - 4
        dy = ((yy - cy + 4) % 8) - 4
        u = dx * math.cos(a) + dy * math.sin(a)
        v = -dx * math.sin(a) + dy * math.cos(a)
        d = np.maximum(np.abs(u) - w / 2, np.abs(v) - h / 2)
        patch = np.maximum(patch, (d < 0).astype(np.float32))
        edge = np.maximum(edge, np.clip(1 - np.abs(d) / 0.025, 0, 1))
    patch = tp.blur(patch, 1.0)
    alb = alb * (1 - patch[..., None]) + (_c((58, 58, 60))[None, None, :] * fine[..., None]) * patch[..., None]
    alb *= (1 - 0.35 * edge)[..., None]
    hgt += -0.25 * patch + 0.15 * edge
    # crepe: linee di livello di un rumore a bassa frequenza (rete irregolare) + qualche crepa longitudinale
    cr = np.zeros((size, size), np.float32)
    for k, (sig, thr) in enumerate(((70, 0.035), (35, 0.03))):
        n = mm._noise(size, size, sig, seed + 10 + k)
        mask = np.clip((mm._noise(size, size, 90, seed + 20 + k) - 0.2) * 1.5, 0, 1)   # crepe solo in alcune zone
        line = np.clip(1 - np.abs(n) / thr, 0, 1) * mask
        cr = np.maximum(cr, line)
    wob = mm._noise(size, size, 2.0, seed + 30)
    cr = np.clip(cr * (0.8 + 0.3 * wob), 0, 1) * (1 - patch)
    alb *= (1 - 0.55 * cr)[..., None]
    hgt -= 0.6 * cr
    # macchie d'olio sotto le auto (piu' frequenti, scure, a chiazze) e inerti chiari
    oil = np.clip((mm._noise(size, size, 22, seed + 40) - 1.5) * 1.2, 0, 1)
    alb *= (1 - 0.25 * oil)[..., None]
    peb = np.clip((mm._noise(size, size, 0.9, seed + 41) - 2.2) * 2, 0, 1)
    alb = alb * (1 - 0.45 * peb[..., None]) + _c((160, 156, 148)) * 0.45 * peb[..., None]
    hgt += 0.3 * peb
    n, ao = mm._normal_ao(hgt, 1.2, 3, 0.5)
    rough = np.clip(0.9 - 0.12 * oil - 0.05 * patch + 0.04 * mm._noise(size, size, 6, seed + 42), 0, 1)
    return [_save(alb, name + "_D"), _save(n, name + "_N"), _save(mm._orm(ao, rough, np.zeros_like(ao)), name + "_ORM")]


def make_tex_cartelli(size=512, name="T_Morin_Cartelli"):
    """Atlante 512 dei cartelli (niente testi leggibili ne' marchi):
    [0-0,5 u, 0,5-1 v] P bianca su blu · [0,5-1 u, 0,5-1 v] divieto di sosta (disco blu, bordo e barra rossi)
    [0-0,5 u, 0-0,5 v] pannello integrativo bianco con righe grigie · [0,5-1 u, 0-0,5 v] lamiera zincata (palo, retro)."""
    H = size // 2
    img = np.ones((size, size, 3), np.float32)
    yy, xx = (np.mgrid[0:H, 0:H].astype(np.float32) + 0.5) / H     # 0-1 nel quadrante, riga 0 in alto
    blu, rosso, bianco = _c((22, 74, 156)), _c((196, 32, 38)), _c((238, 238, 234))
    # P (quadrante in alto a sinistra in immagine = v alto)
    q = np.ones((H, H, 3), np.float32) * bianco
    inner = (np.abs(xx - 0.5) < 0.44) & (np.abs(yy - 0.5) < 0.44)
    q[inner] = blu
    stem = (xx > 0.30) & (xx < 0.44) & (yy > 0.18) & (yy < 0.82)
    r = np.hypot((xx - 0.46) / 1.0, (yy - 0.38) / 1.0)
    bowl = (xx > 0.36) & (r < 0.22) & (r > 0.09) | ((xx > 0.30) & (xx < 0.47) & (np.abs(yy - 0.38) < 0.22) & ((np.abs(yy - 0.18) < 0.035) | (np.abs(yy - 0.58) < 0.035)))
    q[stem | bowl] = bianco
    img[0:H, 0:H] = q
    # divieto di sosta
    q = np.ones((H, H, 3), np.float32) * _c((200, 200, 196))
    d = np.hypot(xx - 0.5, yy - 0.5)
    q[d < 0.5] = rosso
    q[d < 0.40] = blu
    bar = (np.abs((xx - 0.5) - (yy - 0.5)) < 0.06) & (d < 0.42)
    q[bar] = rosso
    img[0:H, H:size] = q
    # pannello integrativo
    q = np.ones((H, H, 3), np.float32) * bianco
    q[(np.abs(xx - 0.5) > 0.47) | (np.abs(yy - 0.5) > 0.47)] = _c((40, 40, 40))
    for k in range(4):
        y0 = 0.22 + k * 0.16
        w = (0.70, 0.55, 0.62, 0.40)[k]
        q[(yy > y0) & (yy < y0 + 0.06) & (np.abs(xx - 0.5) < w / 2)] = _c((60, 60, 64))
    img[H:size, 0:H] = q
    # zincato
    g = 0.62 + 0.05 * mm._noise(H, H, 3, 7)[..., None] + 0.03 * mm._noise(H, H, 0.6, 8)[..., None]
    img[H:size, H:size] = np.clip(g * _c((205, 208, 210)) / 0.62, 0, 1)
    dirt = 1 - 0.06 * np.clip(mm._noise(size, size, 12, 9), 0, 2)[..., None]
    img *= dirt
    hgt = tp.lum(img) * 0.2
    n, ao = mm._normal_ao(hgt, 0.5, 2, 0.2)
    metal = np.zeros((size, size), np.float32)
    metal[H:size, H:size] = 0.8
    rough = np.full((size, size), 0.45, np.float32)
    rough[H:size, H:size] = 0.5
    return [_save(img, name + "_D"), _save(n, name + "_N"), _save(mm._orm(ao, rough, metal), name + "_ORM")]


def make_tex_newjersey(size=1024, seed=1301, name="T_Morin_NewJersey"):
    """Cemento chiaro (u = 2 m di lunghezza, v = perimetro del profilo 0-1 dal piede lato A al piede lato B):
    sporco e schizzi verso il piede, spigoli scheggiati, colature verticali."""
    vv, uu = (np.mgrid[0:size, 0:size].astype(np.float32) + 0.5) / size
    base = _c((196, 194, 186))
    det = 1 + 0.06 * mm._noise(size, size, 1.0, seed) + 0.05 * mm._noise(size, size, 6, seed + 1)
    alb = base[None, None, :] * det[..., None]
    foot = np.clip(1 - np.minimum(vv, 1 - vv) / 0.22, 0, 1) ** 1.5           # piedi del profilo (v=0 e v=1)
    dirt = foot * (0.6 + 0.4 * np.clip(mm._noise(size, size, 8, seed + 2) * 0.5 + 0.5, 0, 1))
    alb = alb * (1 - 0.45 * dirt[..., None]) + _c((96, 88, 74)) * 0.25 * dirt[..., None]
    streak = np.clip(mm._noise(size, 1, 3, seed + 3).repeat(size, 1) * 0.5, 0, 1) * np.clip(mm._noise(size, size, 40, seed + 4), 0, 1)
    alb *= (1 - 0.12 * streak)[..., None]
    chip = np.clip((mm._noise(size, size, 1.5, seed + 5) - 2.0) * 2, 0, 1)
    alb *= (1 - 0.25 * chip)[..., None]
    hgt = 0.3 * mm._noise(size, size, 0.8, seed + 6) - 0.5 * chip
    n, ao = mm._normal_ao(hgt, 1.0, 3, 0.4)
    rough = np.clip(0.88 + 0.05 * mm._noise(size, size, 5, seed + 7), 0, 1)
    return [_save(np.clip(alb, 0, 1), name + "_D"), _save(n, name + "_N"), _save(mm._orm(ao, rough, np.zeros_like(ao)), name + "_ORM")]


def make_textures():
    out = make_tex_asfalto() + make_tex_cartelli() + make_tex_newjersey()
    print("texture:", out)
    return out


def build_materials():
    t = TEXDIR + "/"
    for m, tx in (("M_Parcheggio_Asfalto", "T_Parcheggio_Asfalto"), ("M_Morin_Cartelli", "T_Morin_Cartelli"),
                  ("M_Morin_NewJersey", "T_Morin_NewJersey")):
        pk._pbr_material(m, t + tx + "_D.png", t + tx + "_N.png", t + tx + "_ORM.png")
    if "M_Pav_Terra" not in bpy.data.materials:
        pk.build_materials(make_textures=False)
    return True


# =============================================================================================================
# suolo: asfalto + strisce + cordoli + terra (pezzo unico in coordinate di progetto, origine 0,0,0)
# =============================================================================================================
OUTLINE = [(X0, Y_CORD1), (X1, Y_CORD1), (X1, 113.5), (106.0, Y_VIALE), (X0, Y_VIALE),
           (X0, NOTCH[3]), (NOTCH[1], NOTCH[3]), (NOTCH[1], NOTCH[2]), (X0, NOTCH[2])]


def _poly(bm, pts, z, mi):
    vs = [bm.verts.new((x, y, z)) for x, y in pts]
    f = bm.faces.new(vs)
    f.material_index = mi
    if f.normal.z < 0:
        f.normal_flip()
    return f


def _stripe(bm, a, b, w, z, mi):
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    n = Vector((-d.y, d.x)) * (w / 2)
    _poly(bm, [a + n, a - n, b - n, b + n], z, mi)


def _aiuola(bm, x0, x1, y0, y1, zc=0.14, zt=Z_AIUOLA, c=0.20):
    """Aiuola rialzata: cordolo in pietra (largo c, top zc) e terra incassata (zt)."""
    pk._box(bm, x0, x1, y0, y1, Z_ASF, zc, mi=2, faces=("yn", "yp", "xn", "xp"))
    i0, i1, j0, j1 = x0 + c, x1 - c, y0 + c, y1 - c
    for q in (((x0, y0), (x1, y0), (i1, j0), (i0, j0)), ((x1, y0), (x1, y1), (i1, j1), (i1, j0)),
              ((x1, y1), (x0, y1), (i0, j1), (i1, j1)), ((x0, y1), (x0, y0), (i0, j0), (i0, j1))):
        _poly(bm, q, zc, 2)
    pk._box(bm, i0, i1, j0, j1, zt, zc, mi=2, faces=("yn", "yp", "xn", "xp"))
    for f in bm.faces[-4:]:
        f.normal_flip()          # pareti interne rivolte verso la terra
    _poly(bm, [(i0, j0), (i1, j0), (i1, j1), (i0, j1)], zt, 3)


def build_suolo(coll, name="SM_Parcheggio_Asfalto"):
    bm = bmesh.new()
    mats = ["M_Parcheggio_Asfalto", "M_Viale_Segnaletica", "M_Pav_Fascia", "M_Pav_Terra"]
    f = _poly(bm, OUTLINE, Z_ASF, 0)
    bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.faces.ensure_lookup_table()
    zs = Z_ASF + 0.004
    w = 0.12
    # due file in linea (mare, citta'): linea continua verso la corsia + separatori ogni 5,5 m
    for (ya, yb, yl, xr) in ((Y_SOSTA_MARE[0] + 0.3, Y_SOSTA_MARE[1] - w / 2, Y_SOSTA_MARE[1], MARE_X),
                             (Y_SOSTA_CITTA[0] + w / 2, Y_SOSTA_CITTA[1] - 0.3, Y_SOSTA_CITTA[0], CITTA_X)):
        _stripe(bm, (xr[0], yl), (xr[1], yl), w, zs, 1)
        x = xr[0]
        while x <= xr[1] + 1e-6:
            _stripe(bm, (x, ya), (x, yb), w, zs, 1)
            x += MARE_L
    # seconda fila a pettine (90°), separatori ogni 2,5 m
    x = PETTINE_X[0]
    while x <= PETTINE_X[1] + 1e-6:
        _stripe(bm, (x, Y_PETTINE[0] + 0.25), (x, Y_PETTINE[1] - 0.3), w, zs, 1)
        x += PETTINE_W
    # strisce pedonali all'imbocco (foto): bande da 0,5 m lungo X, passo 1 m, attraverso la corsia
    y = Y_CORSIA[0] + 0.4
    while y + 0.5 <= Y_CORSIA[1] - 0.3:
        _poly(bm, [(ZEBRA_X[0], y), (ZEBRA_X[1], y), (ZEBRA_X[1], y + 0.5), (ZEBRA_X[0], y + 0.5)], zs, 1)
        y += 1.0
    # cordolo lato mare in pietra chiara (sopra: Z 0,15 come la fascia palme; fronte verso l'asfalto)
    pk._box(bm, X0, X1, Y_CORD0, Y_CORD1, Z_ASF, Z_CORD, mi=2, faces=("top", "yp", "xn", "xp"))
    # aiuola rialzata delle latifoglie
    _aiuola(bm, AIU_X[0], AIU_X[1], Y_AIUOLA[0], Y_AIUOLA[1])
    o = pk._finish(name, bm, mats, coll, uv="world")
    # UCX: solo la parte giocabile (Y < 118, Barriera_LatoCitta), box semplici
    for u in [x for x in bpy.data.objects if x.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)
    pk._ucx(name, [(NOTCH[1], X1, Y_CORD1, 118.0, -0.30, Z_ASF),          # asfalto oltre la tacca del ramo del molo
                   (X0, NOTCH[1], Y_CORD1, NOTCH[2], -0.30, Z_ASF),       # asfalto a X 20-24 verso mare
                   (X0, NOTCH[1], NOTCH[3], 118.0, -0.30, Z_ASF),         # asfalto a X 20-24 lato citta'
                   (X1, 101.7, 113.5, 118.0, -0.30, Z_ASF),               # imbocco dell'uscita
                   (X0, X1, Y_CORD0, Y_CORD1, -0.30, Z_CORD),             # cordolo lato mare
                   (AIU_X[0], AIU_X[1], Y_AIUOLA[0], Y_AIUOLA[1], -0.30, 0.14)], coll)   # aiuola
    return o




# =============================================================================================================
# cartelli su palo (origine alla base del palo, pannello rivolto verso -X)
# =============================================================================================================
def _cyl(bm, r, z0, z1, n, uvbox, cap=True):
    """Cilindro verticale con UV nel riquadro uvbox (u0, v0, u1, v1) dell'atlante."""
    layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uvbox
    ring0 = [bm.verts.new((r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), z0)) for k in range(n)]
    ring1 = [bm.verts.new((v.co.x, v.co.y, z1)) for v in ring0]
    for k in range(n):
        f = bm.faces.new([ring0[k], ring0[(k + 1) % n], ring1[(k + 1) % n], ring1[k]])
        for lp, (a, b) in zip(f.loops, ((k / n, 0), ((k + 1) / n, 0), ((k + 1) / n, 1), (k / n, 1))):
            lp[layer].uv = (u0 + (u1 - u0) * a, v0 + (v1 - v0) * b)
    if cap:
        f = bm.faces.new(list(reversed(ring0)) if False else ring1)
        for lp in f.loops:
            lp[layer].uv = (u0 + 0.5 * (u1 - u0), v0 + 0.5 * (v1 - v0))


def _panel_rect(bm, y0, y1, z0, z1, x_front, t, uv_front, uv_back):
    """Pannello piano: fronte verso -X a x_front, spessore t verso +X; uv (u0,v0,u1,v1)."""
    layer = bm.loops.layers.uv.verify()
    xf, xb = x_front, x_front + t

    def quad(pts, uvs):
        f = bm.faces.new([bm.verts.new(p) for p in pts])
        for lp, uv in zip(f.loops, uvs):
            lp[layer].uv = uv
    u0, v0, u1, v1 = uv_front
    # fronte (normale -X): guardando da -X, +Y e' a sinistra → u cresce verso -Y
    quad([(xf, y1, z0), (xf, y0, z0), (xf, y0, z1), (xf, y1, z1)], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    b0, c0, b1, c1 = uv_back
    quad([(xb, y0, z0), (xb, y1, z0), (xb, y1, z1), (xb, y0, z1)], [(b0, c0), (b1, c0), (b1, c1), (b0, c1)])
    for pts in (((xf, y0, z1), (xf, y0, z0), (xb, y0, z0), (xb, y0, z1)), ((xb, y1, z1), (xb, y1, z0), (xf, y1, z0), (xf, y1, z1)),
                ((xf, y1, z1), (xf, y0, z1), (xb, y0, z1), (xb, y1, z1))):
        quad(pts, [(b0, c0), (b1, c0), (b1, c1), (b0, c1)])


def _panel_disc(bm, r, zc, x_front, t, n, uv_front, uv_back):
    layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uv_front
    b0, c0, b1, c1 = uv_back
    ang = [2 * math.pi * k / n for k in range(n)]
    fr = [bm.verts.new((x_front, -r * math.cos(a), zc + r * math.sin(a))) for a in ang]
    bk = [bm.verts.new((x_front + t, -r * math.cos(a), zc + r * math.sin(a))) for a in ang]
    f = bm.faces.new(list(reversed(fr)))
    if f.normal.x > 0:
        f.normal_flip()
    for lp in f.loops:
        y, z = lp.vert.co.y, lp.vert.co.z - zc
        lp[layer].uv = (u0 + (u1 - u0) * (0.5 - y / (2 * r)), v0 + (v1 - v0) * (0.5 + z / (2 * r)))
    f = bm.faces.new(bk)
    if f.normal.x < 0:
        f.normal_flip()
    for lp in f.loops:
        lp[layer].uv = ((b0 + b1) / 2, (c0 + c1) / 2)
    for k in range(n):
        f = bm.faces.new([fr[k], fr[(k + 1) % n], bk[(k + 1) % n], bk[k]])
        for lp in f.loops:
            lp[layer].uv = ((b0 + b1) / 2, (c0 + c1) / 2)


UV_P, UV_DIV, UV_PLATE, UV_ZINC = (0.0, 0.5, 0.5, 1.0), (0.5, 0.5, 1.0, 1.0), (0.0, 0.0, 0.5, 0.5), (0.52, 0.02, 0.98, 0.48)
POLE_H = 2.70


def build_cartello(coll, kind, lod=0):
    name = {"P": "SM_Morin_CartelloP", "DIV": "SM_Morin_CartelloDivieto"}[kind]
    sfx = "" if lod == 0 else f"_LOD{lod}"
    bm = bmesh.new()
    n_pole = (10, 6, 4)[lod]
    _cyl(bm, 0.03, 0.0, POLE_H, n_pole, UV_ZINC)
    t = 0.02 if lod < 2 else 0.01
    xf = -0.035 - t
    if kind == "P":
        _panel_rect(bm, -0.30, 0.30, 2.05, 2.65, xf, t, UV_P, UV_ZINC)
    else:
        _panel_disc(bm, 0.30, 2.33, xf, t, (20, 12, 8)[lod], UV_DIV, UV_ZINC)
        _panel_rect(bm, -0.25, 0.25, 1.70, 1.98, xf, t, UV_PLATE, UV_ZINC)
    if lod < 2:   # fascette
        for z in ((2.15, 2.55) if kind == "P" else (2.2, 1.84)):
            _cyl(bm, 0.036, z - 0.02, z + 0.02, n_pole, UV_ZINC, cap=False)
    o = pk._finish(name + sfx, bm, ["M_Morin_Cartelli"], coll, uv=None)
    if lod == 0:
        pk._ucx(name, [(-0.04, 0.04, -0.04, 0.04, 0.0, POLE_H)], coll)
    return o


# =============================================================================================================
# new jersey in cemento (2 m, origine al centro della base, asse lungo X)
# =============================================================================================================
NJ_L = 2.0
NJ_PROF = [(-0.305, 0.0), (-0.305, 0.075), (-0.125, 0.33), (-0.075, 0.81), (0.075, 0.81), (0.125, 0.33), (0.305, 0.075), (0.305, 0.0)]


def build_newjersey(coll, name="SM_Morin_NewJersey", lod=0):
    sfx = "" if lod == 0 else f"_LOD{lod}"
    prof = NJ_PROF if lod < 2 else [NJ_PROF[0], NJ_PROF[2], NJ_PROF[3], NJ_PROF[4], NJ_PROF[5], NJ_PROF[7]]
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    per = [0.0]
    for a, b in zip(prof, prof[1:]):
        per.append(per[-1] + math.dist(a, b))
    P = per[-1]
    xs = (-NJ_L / 2, NJ_L / 2) if lod > 0 else (-NJ_L / 2, -NJ_L / 2 + 0.02, NJ_L / 2 - 0.02, NJ_L / 2)
    rings = []
    for x in xs:
        ins = 0.012 if (lod == 0 and abs(abs(x) - NJ_L / 2) < 1e-6) else 0.0   # testate smussate
        rings.append([bm.verts.new((x, y * (1 - ins * 4) if z > 0.3 else y, z - (ins if z > 0.8 else 0))) for y, z in prof])
    for i in range(len(rings) - 1):
        for k in range(len(prof) - 1):
            f = bm.faces.new([rings[i][k], rings[i + 1][k], rings[i + 1][k + 1], rings[i][k + 1]])
            for lp, (ri, kk) in zip(f.loops, ((i, k), (i + 1, k), (i + 1, k + 1), (i, k + 1))):
                lp[layer].uv = ((xs[ri] + NJ_L / 2) / NJ_L, per[kk] / P)
    for ring, flip in ((rings[0], False), (rings[-1], True)):
        f = bm.faces.new(list(reversed(ring)) if not flip else ring)
        for lp in f.loops:
            lp[layer].uv = (0.02 if not flip else 0.98, 0.15 + 0.7 * (lp.vert.co.y + 0.305) / 0.61)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)     # mesh chiusa: normali verso l'esterno
    o = pk._finish(name + sfx, bm, ["M_Morin_NewJersey"], coll, uv=None)
    if lod == 0:
        for u in [x for x in bpy.data.objects if x.name.startswith(f"UCX_{name}_")]:
            bpy.data.objects.remove(u)
        pts = [(x, y, z) for x in (-NJ_L / 2, NJ_L / 2) for y, z in NJ_PROF]
        pk._ucx_hull(name, 0, pts, coll)
    return o


# =============================================================================================================
# auto del parcheggio con collisione (stesse mesh di SM_Morin_Auto_A/B/C, oggetti nuovi _Col + UCX)
# =============================================================================================================
AUTO = ("SM_Morin_Auto_A", "SM_Morin_Auto_B", "SM_Morin_Auto_C")


def build_auto_col(coll):
    out = []
    for a in AUTO:
        for lod in (0, 1, 2):
            src = a if lod == 0 else f"{a}_LOD{lod}"
            nm = f"{a}_Col" if lod == 0 else f"{a}_Col_LOD{lod}"
            o = bpy.data.objects.get(nm)
            if o is None:
                o = bpy.data.objects.new(nm, bpy.data.meshes[src])
                coll.objects.link(o)
            o.data = bpy.data.meshes[src]
            o.matrix_world = Matrix.Identity(4)
            out.append(o)
        vs = [v.co for v in bpy.data.meshes[a].vertices]
        L = max(v.x for v in vs); W = max(v.y for v in vs); H = max(v.z for v in vs)
        for u in [x for x in bpy.data.objects if x.name.startswith(f"UCX_{a}_Col_")]:
            bpy.data.objects.remove(u)
        # scocca fino alla linea di cintura + abitacolo piu' corto e stretto (2 box, il giocatore puo' salirci sopra)
        import morin_viale as mv
        st = mv.AUTO[a]["st"]                       # stazioni (s, ..., altezza, ...): abitacolo dove l'altezza > 1,1 m
        cab = [s[0] for s in st if s[3] > 1.1]
        cx0, cx1 = (min(cab) - 0.5) * 2 * L, (max(cab) - 0.5) * 2 * L
        belt = max(s[3] for s in st if s[3] <= 1.1)
        pk._ucx(f"{a}_Col", [(-L, L, -W, W, 0.12, belt), (cx0, cx1, -W + 0.08, W - 0.08, belt, H - 0.03)], coll)
    return out


def build_all():
    coll = pk._coll(KIT)
    objs = [build_suolo(coll)]
    for kind in ("P", "DIV"):
        for lod in (0, 1, 2):
            objs.append(build_cartello(coll, kind, lod))
    for lod in (0, 1, 2):
        objs.append(build_newjersey(coll, lod=lod))
    objs += build_auto_col(coll)
    for o in objs:
        print(o.name, pk.tri_count(o))
    return objs


# =============================================================================================================
# layout (coordinate di progetto, metri) e CSV (coordinate UE)
# =============================================================================================================
AUTO_L = {"SM_Morin_Auto_A": 3.96, "SM_Morin_Auto_B": 4.34, "SM_Morin_Auto_C": 4.44}


def _row_inline(rows, rng, k, xr, yc, gap):
    """Fila in linea, muso verso +X (senso unico verso NE, foto). Posti da 5,5 m."""
    x = xr[0]
    while x + MARE_L <= xr[1] + 1e-6:
        if rng.uniform() > gap:
            a = AUTO[int(rng.integers(0, 3))]
            rows.append((a + "_Col", f"ParkAuto_{k:03d}", x + MARE_L / 2 + rng.uniform(-0.3, 0.3),
                         yc + rng.uniform(-0.08, 0.08), Z_ASF, rng.uniform(-1.5, 1.5)))
            k += 1
        x += MARE_L
    return k


def layout(seed=20261120):
    rng = np.random.default_rng(seed)
    rows = [("SM_Parcheggio_Asfalto", "Parcheggio_Asfalto", 0.0, 0.0, 0.0, 0.0)]
    k = _row_inline(rows, rng, 0, MARE_X, (Y_SOSTA_MARE[0] + Y_SOSTA_MARE[1]) / 2 + 0.1, 0.15)
    k = _row_inline(rows, rng, k, CITTA_X, (Y_SOSTA_CITTA[0] + Y_SOSTA_CITTA[1]) / 2 + 0.1, 0.10)
    # seconda fila a pettine: muso verso le aiuole (-Y), retro verso Viale Italia
    x = PETTINE_X[0]
    while x + PETTINE_W <= PETTINE_X[1] + 1e-6:
        if rng.uniform() > 0.2:
            a = AUTO[int(rng.integers(0, 3))]
            rows.append((a + "_Col", f"ParkAuto_{k:03d}", x + PETTINE_W / 2 + rng.uniform(-0.12, 0.12),
                         Y_PETTINE[0] + 0.35 + AUTO_L[a] / 2 + rng.uniform(-0.1, 0.2), Z_ASF, -90.0 + rng.uniform(-2, 2)))
            k += 1
        x += PETTINE_W
    # cartelli: divieto e P all'imbocco (aiuola delle palme, foto), P sull'aiuola delle latifoglie, divieto all'uscita
    rows += [("SM_Morin_CartelloDivieto", "Cartello_Divieto_00", 22.6, 101.55, Z_CORD, 0.0),
             ("SM_Morin_CartelloP", "Cartello_P_00", 26.2, 101.55, Z_CORD, 0.0),
             ("SM_Morin_CartelloP", "Cartello_P_01", 55.5, 113.75, Z_AIUOLA, 0.0),
             ("SM_Morin_CartelloDivieto", "Cartello_Divieto_01", 89.0, 101.55, Z_CORD, 180.0)]
    # new jersey sul ciglio della banchina davanti al battello (foto): 3 in fila, corsia libera > 8 m (Y 80,9-89)
    for i in range(3):
        rows.append(("SM_Morin_NewJersey", f"NewJersey_{i:02d}", 62.0 + i * 2.05, 80.6, 0.0, rng.uniform(-1.5, 1.5)))
    # grandi latifoglie (decisione utente: non pini) nell'aiuola rialzata, Y 115,1 (OSM: filare a Y 113)
    for i, x in enumerate(np.arange(30.0, 84.0, 10.5)):
        a = "SM_Albero_LatifogliaA" if i % 2 == 0 else "SM_Albero_LatifogliaB"
        rows.append((a, f"Parcheggio_Latifoglia_{i:02d}", float(x + rng.uniform(-1.0, 1.0)),
                     float(115.1 + rng.uniform(-0.25, 0.25)), Z_AIUOLA, float(rng.uniform(0, 360))))
    return rows


def write_csv(rows, path="exports/parcheggio/parcheggio_posizioni_v1.csv"):
    return mm.write_csv(rows, path)


def build_context(rows, name="PARK_Contesto_Istanze"):
    coll = pk._coll(name)
    for a, n, x, y, z, yaw in rows:
        src = bpy.data.objects.get(a)
        me = src.data if src is not None else bpy.data.meshes.get(a)
        if me is None:
            print("manca la mesh", a)
            continue
        nm = "CTXP_" + n
        o = bpy.data.objects.get(nm)
        if o is None:
            o = bpy.data.objects.new(nm, me)
            coll.objects.link(o)
        o.data = me
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(yaw))
    for o in bpy.data.collections[KIT].objects:
        if o.name != "SM_Parcheggio_Asfalto":
            o.hide_render = True
            o.hide_viewport = True
    return coll


SINGLE = ["SM_Parcheggio_Asfalto"]
LODDED = ["SM_Morin_CartelloP", "SM_Morin_CartelloDivieto", "SM_Morin_NewJersey",
          "SM_Morin_Auto_A_Col", "SM_Morin_Auto_B_Col", "SM_Morin_Auto_C_Col"]


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    state = {o.name: (o.hide_viewport, o.hide_get(), o.matrix_world.copy()) for o in bpy.data.collections[KIT].objects}
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
        for n, (hv, hg, mw) in state.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps


# =============================================================================================================
# Viale v2: CSV corretto (strada fino a X 326, auto sui moduli nuovi, quote oltre il blockout)
# =============================================================================================================
def _ground_min(x0, x1, y0, y1, step=1.0, ignore=("CTXV_", "CTXP_", "V3_", "CTXM_", "REF_")):
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene
    zs = []
    for x in np.arange(x0, x1 + 1e-6, step):
        for y in np.arange(y0, y1 + 1e-6, step):
            o = Vector((x, y, 200.0))
            for _ in range(400):
                r = sc.ray_cast(dg, o, Vector((0, 0, -1)))
                if not r[0]:
                    break
                if r[4].name.startswith(ignore) or r[4].hide_render:
                    o = r[1] - Vector((0, 0, 0.001))
                    continue
                zs.append(r[1].z)
                break
    return min(zs), max(zs)


def viale_csv_v2(src="exports/viale/viale_posizioni_v1.csv", dst="exports/viale/viale_posizioni_v2.csv", seed=20261120):
    import csv
    with open(f"{PROJ}/{src}", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    head, body = rows[0], rows[1:]
    notes = []
    # 1) palazzi e latifoglia oltre il blockout (X > 330): appoggio sul minimo del suolo (colline N) sotto l'impronta
    foot = {"SM_Fondale_Palazzo_A": (10.6, 0.0, 19.2), "SM_Fondale_Palazzo_B": (12.85, 0.0, 19.6), "SM_Albero_LatifogliaA": (0.5, -0.5, 0.5),
            "SM_Albero_LatifogliaB": (0.5, -0.5, 0.5)}
    for r in body:
        a, n, x, y = r[0], r[1], float(r[2]) / 100, -float(r[3]) / 100
        if a in foot and x + foot[a][0] > 330.0:
            hx, ylo, yhi = foot[a]
            zmin, zmax = _ground_min(x - hx, x + hx, y + ylo, y + yhi, 1.0)
            if zmin < -0.01 or zmin > 0.05:      # mai sospeso; base del palazzo sul punto piu basso del colle
                r[4] = f"{zmin * 100:.1f}"
            notes.append((n, a, round(x, 2), round(y, 2), round(zmin, 2), round(zmax, 2), r[4]))
    # 2) strada: 4 moduli oltre X 250 (fino a X 326, il blockout Fondale finisce a X 330)
    import morin_viale as mv
    for k in range(7, 11):
        body.append(["SM_Viale_Italia_Strada", f"Viale_Strada_{k:02d}", f"{(117.0 + 19.0 * k) * 100:.1f}", "-12085.0", "0.0", "0.0"])
    # 3) strada anche verso SO, davanti al parcheggio (OSM: Viale Italia dritto a Y ~129-135 da X -26 a 110): X 3-117
    for k in range(6):
        body.append(["SM_Viale_Italia_Strada", f"Viale_Strada_SO_{k:02d}", f"{(3.0 + 19.0 * k) * 100:.1f}", "-12085.0", "0.0", "0.0"])
    rng = np.random.default_rng(seed)
    k = 41
    names = list(mv.AUTO)
    # sosta lato giardini libera davanti all'uscita del parcheggio (X 94-110) e all'incrocio con il molo (X < 14)
    for (y, yaw, x0, x1, gap) in ((mv.Y_SOSTA_A, 180.0, 251.0, 324.0, 0.10), (mv.Y_SOSTA_B, 0.0, 251.0, 324.0, 0.25),
                                  (mv.Y_SOSTA_A, 180.0, 14.0, 93.0, 0.10), (mv.Y_SOSTA_B, 0.0, 16.0, 116.0, 0.25)):
        x = x0 + rng.uniform(0, 2)
        while True:
            a = names[int(rng.integers(0, 3))]
            Lc = mv.AUTO[a]["L"]
            if x + Lc > x1:
                break
            if rng.uniform() > gap:
                body.append([a, f"Auto_{k:03d}", f"{(x + Lc / 2) * 100:.2f}", f"{-(y + rng.uniform(-0.08, 0.08)) * 100:.2f}",
                             "2.0", f"{-(yaw + rng.uniform(-1.5, 1.5)):.2f}"])
                k += 1
            x += Lc + rng.uniform(0.8, 1.6)
    with open(f"{PROJ}/{dst}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(",".join(r) for r in [head] + body) + "\n")
    return notes, len(body)


# =============================================================================================================
# camera e confronto
# =============================================================================================================
# punto di presa stimato dalla foto: davanti alle strisce pedonali, sul bordo della corsia lato mare, guardando lungo X
CAMS = {"CAM_Park_F1": ((21.5, 106.6, Z_ASF + 2.1), 82.0, -6.0, 78.0, (1375, 783))}


def cameras():
    coll = pk._coll("PARK_Camere")
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
    return list(CAMS)


def render_confronto(cam="CAM_Park_F1", out="docs/qa/arte_parcheggio_v1_confronto.png", tmp=None):
    tmp = tmp or os.path.join(os.environ.get("TEMP", PROJ), "morin_parcheggio_render.png")
    mm.render(cam, tmp, width=1375)
    a = tp.load(FOTO)[..., :3]
    b = tp.load(tmp)[..., :3]
    if b.shape[1] != a.shape[1]:
        b = tp.resize(b, a.shape[1], int(round(b.shape[0] * a.shape[1] / b.shape[1])))
    sep = np.ones((6, a.shape[1], 3), np.float32)
    tp.save(np.concatenate([a, sep, b], 0), f"{PROJ}/{out}")
    return out, tmp
