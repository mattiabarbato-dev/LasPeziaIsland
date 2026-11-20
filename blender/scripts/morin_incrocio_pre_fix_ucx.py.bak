"""morin_incrocio.py — incrocio Viale Italia / strada del molo / parcheggio (v1, 2026-11-20) e parcheggio a pettine (v3).

Schede: ref/zona_parcheggio_chiosco.md ("Incrocio con Viale Italia"), ref/radice_molo.md §2, ref/sezione.md.
Foto: ref/foto/vista/vissta_entrata_parcheggio_e_passeggiata_da_viale_italia.png (cattura Street View, deroga [SV]: solo
forme, colori e proporzioni; texture procedurali, niente UI, persone, targhe, insegne; l'insegna reale del ristorante NON e'
riprodotta). Parcheggio: ref/foto/vista/parcheggio_iniziale.png (fila lato citta' sotto i pini = a pettine, correzione utente).
OSM (ref/osm/morin_bbox.osm, (c) OpenStreetMap contributors), coordinate di progetto:
  - strada del molo (way 238848818): asse X ~9, da Viale Italia (9,0; 129,3) a (9,1; 121,0) e giu' verso il molo;
  - strisce (node 3822323975, zebra) in (9,1; 121,0): attraversano l'imbocco della strada del molo;
  - attraversamento del viale (way 1486816240, footway=crossing) lungo X ~15,2 da Y 120,9 a 138,0;
  - semafori (1352945064, 7933688341) in (15,1; 129,3) e (15,0; 135,2); telecamera su palo (12,1; 125,6);
  - Viale Italia a senso unico per carreggiata: A (Y ~129) verso +X, B (Y ~135) verso -X; Viale Diaz parte a X 9 verso la citta'.
Camera della foto (stima [S], rettilinea, punti di fuga di X e Y + piede del semaforo): (8,0; 118,0; 2,7), azimut -32 gradi,
FOV orizzontale ~150 gradi, orizzonte a y 318 px su 530.

Decisioni [S] (docs/decisioni.md, 2026-11-20):
  - imbocco della strada del molo = asfalto X 6,5-9,55 fino a Viale Italia: nel modulo del viale il cordolo si abbassa al
    livello dell'asfalto in quel tratto (risolve "il cordolo attraversa l'innesto");
  - marciapiede in masselli grigi (Z 0,15) X 9,55-20, Y 113,95-120,85 fra la strada del molo, il ramo del parcheggio e
    Viale Italia (prima: lastre del blockout);
  - semaforo grande e cartelli "dare precedenza" + "obbligo a destra" sullo spartitraffico, di fronte allo sbocco;
  - spartitraffico con fiori rossi da X 9 verso NE, interrotto dall'attraversamento X 14-16,5;
  - dehors vetrato sulla pianta OSM B (-8,1..0,5; 111,4..116,7) al posto del tendone (SM_Molo_Tendone);
  - parcheggio: fila lato citta' a pettine a 60 gradi (Y 111,0-115,7), aiuola dei pini ristretta a Y 115,7-117,0.

Esegui dentro blender/arte_incrocio.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_incrocio as mi; importlib.reload(mi)
    mi.make_textures(); mi.build_materials(); mi.build_all()
    mi.write_all_csv(); mi.build_context()
    mi.export_all()
    mi.cameras(); mi.render_confronti()
"""
import csv
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_texphoto as tp
import morin_molo as mm
import morin_parcheggio as mp

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/incrocio"
KIT = "INCR_Kit"
EXPDIR = "//../exports/incrocio"
EXPDIR_PARK = "//../exports/parcheggio"
FOTO = PROJ + "/ref/foto/vista/vissta_entrata_parcheggio_e_passeggiata_da_viale_italia.png"
FOTO_PARK = PROJ + "/ref/foto/vista/parcheggio_iniziale.png"

# quote e piante [V] OSM / [S]
Y_VIALE = 120.85
Z_ASF_VIALE = 0.02
Z_MOLO = 0.01
X_MOUTH = (6.5, 9.55)          # strada del molo (asfalto molo X 6,5-9,55)
X_ZEBRA_V = (14.0, 16.5)       # attraversamento del viale (OSM X 15,2)
Y_SPART = (131.0, 132.0)
MOD_X0 = 3.0                   # il modulo sostituisce Viale_Strada_SO_00 (X 3-22)
MOD_L = 19.0
MARC = (9.55, 20.0, 113.95, Y_VIALE)
B_DEHORS = (-8.1, 0.5, 111.4, 116.7)

# parcheggio v3: fila lato citta' a pettine
PETT_ANG = 60.0
Y_PETT_C = (111.0, 115.7)
Y_AIU_V3 = (115.7, 117.0)
PETT_STALL = 2.5               # larghezza dello stallo (perpendicolare all'auto)
PETT_X = (26.0, 84.5)
Y_PINI_V3 = 116.35


def _c(c):
    return np.asarray(c, np.float32) / 255.0


def _save(a, name):
    os.makedirs(TEXDIR, exist_ok=True)
    tp.save(np.clip(a, 0, 1), f"{TEXDIR}/{name}.png")
    return f"{TEXDIR}/{name}.png"


# =============================================================================================================
# texture: atlante dei prop 1024 (4 x 4 celle), fiori 1024 (RGBA, masked), edificio di fondale 1024
# =============================================================================================================
N_AT = 1024
CS = N_AT // 4
CELL = {"cemento": (0, 0), "verde": (1, 0), "nero": (2, 0), "bianco": (3, 0),
        "lanterna": (0, 1), "precedenza": (1, 1), "obbligo": (2, 1), "retro": (3, 1),
        "scooter": (0, 2), "scooter2": (1, 2), "metallo": (2, 2), "vetro": (3, 2),
        "telaio": (0, 3), "mantovana": (1, 3), "gomma": (2, 3), "tessuto": (3, 3)}
# colore sRGB, roughness, metallic
CELL_PBR = {"cemento": ((150, 148, 142), 0.88, 0.0), "verde": ((28, 52, 40), 0.45, 0.0), "nero": ((22, 22, 23), 0.55, 0.0),
            "bianco": ((236, 236, 232), 0.40, 0.0), "lanterna": ((18, 18, 19), 0.35, 0.0), "precedenza": ((150, 150, 150), 0.35, 0.0),
            "obbligo": ((150, 150, 150), 0.35, 0.0), "retro": ((130, 132, 134), 0.45, 0.6), "scooter": ((226, 226, 222), 0.25, 0.0),
            "scooter2": ((70, 72, 76), 0.28, 0.0), "metallo": ((170, 172, 175), 0.25, 1.0), "vetro": ((52, 62, 70), 0.05, 0.0),
            "telaio": ((48, 49, 50), 0.40, 0.6), "mantovana": ((238, 236, 228), 0.80, 0.0), "gomma": ((26, 26, 27), 0.90, 0.0),
            "tessuto": ((232, 228, 216), 0.85, 0.0)}


def _cell_slice(name):
    c, r = CELL[name]
    return slice((3 - r) * CS, (4 - r) * CS), slice(c * CS, (c + 1) * CS)


def cell_uv(name, fu, fv, inset=0.06):
    """(fu, fv) in [0,1] dentro la cella -> UV dell'atlante."""
    c, r = CELL[name]
    i = inset / 4
    return (c / 4 + i + fu * (0.25 - 2 * i), r / 4 + i + fv * (0.25 - 2 * i))


def make_tex_atlas(seed=1501, name="T_Incrocio_Props"):
    rng = np.random.default_rng(seed)
    A = np.zeros((N_AT, N_AT, 3), np.float32)
    R = np.zeros((N_AT, N_AT), np.float32)
    M = np.zeros((N_AT, N_AT), np.float32)
    H = np.zeros((N_AT, N_AT), np.float32)
    yy, xx = np.mgrid[0:CS, 0:CS].astype(np.float32)
    fu, fv = (xx + 0.5) / CS, 1.0 - (yy + 0.5) / CS            # coordinate di cella (v verso l'alto)
    for k, (col, rough, met) in CELL_PBR.items():
        sy, sx = _cell_slice(k)
        n = mm._noise(CS, CS, 2.0, seed + len(k)) * 0.5 + 0.5 * mm._noise(CS, CS, 12.0, seed + 7 * len(k))
        amp = {"cemento": 0.10, "mantovana": 0.03, "tessuto": 0.04}.get(k, 0.025)
        A[sy, sx] = _c(col)[None, None, :] * (1 + amp * n)[..., None]
        R[sy, sx] = rough
        M[sy, sx] = met
        if k == "cemento":
            pits = (mm._noise(CS, CS, 0.8, seed + 3) > 2.2).astype(np.float32)
            A[sy, sx] *= (1 - 0.25 * pits)[..., None]
            H[sy, sx] = 0.4 * n - 0.6 * pits
    # lanterna semaforica: faccia 0,30 x 0,90 m sulla cella; tre lenti (r 0,10 m) e visiere
    sy, sx = _cell_slice("lanterna")
    for j, colr in enumerate(((200, 30, 24), (214, 150, 30), (30, 170, 90))):
        cy = 1 - (j + 0.5) / 3
        d = ((fu - 0.5) / (0.10 / 0.30)) ** 2 + ((fv - cy) / (0.10 / 0.90)) ** 2
        m = d < 1
        A[sy, sx][m] = _c(colr) * (0.55 + 0.45 * (1 - d[m]))[:, None]
        R[sy, sx][m] = 0.15
        ring = (d >= 1) & (d < 1.45)
        A[sy, sx][ring] = _c((8, 8, 8))
    # dare precedenza: triangolo con la punta in basso, bordo rosso, interno bianco
    sy, sx = _cell_slice("precedenza")
    def tri_d(u, v, pts=((0.05, 0.93), (0.5, 0.07), (0.95, 0.93))):
        # distanza (unita' di cella) dal bordo del triangolo antiorario, positiva dentro
        out = None
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            ex, ey = bx - ax, by - ay
            dd = (ex * (v - ay) - ey * (u - ax)) / math.hypot(ex, ey)
            out = dd if out is None else np.minimum(out, dd)
        return out
    d = tri_d(fu, fv)
    A[sy, sx][d > 0] = _c((196, 26, 30))
    A[sy, sx][d > 0.10] = _c((240, 240, 236))
    A[sy, sx][(d > 0) & (d < 0.012)] = _c((235, 235, 235))
    # obbligo a destra: disco blu con freccia bianca verso +u
    sy, sx = _cell_slice("obbligo")
    rr = np.hypot(fu - 0.5, fv - 0.5)
    A[sy, sx][rr < 0.48] = _c((16, 74, 160))
    A[sy, sx][(rr >= 0.46) & (rr < 0.48)] = _c((236, 236, 236))
    shaft = (np.abs(fv - 0.5) < 0.07) & (fu > 0.22) & (fu < 0.58)
    head = (fu >= 0.52) & (fu < 0.80) & (np.abs(fv - 0.5) < (0.80 - fu) * 0.85)
    A[sy, sx][shaft | head] = _c((240, 240, 240))
    # telaio del vetro con riflessi: gradiente del cielo
    sy, sx = _cell_slice("vetro")
    A[sy, sx] = (_c((40, 48, 56))[None, None, :] * (1 - fv[..., None]) + _c((120, 138, 150))[None, None, :] * fv[..., None] ** 2)
    # mantovana: bianca con onde (smerlo) in basso
    sy, sx = _cell_slice("mantovana")
    sc = (fv < 0.25 + 0.12 * np.abs(np.sin(fu * math.pi * 4))) & (fv < 0.35)
    A[sy, sx][sc] *= 0.82
    # scooter: linea di cintura scura
    for k in ("scooter", "scooter2"):
        sy, sx = _cell_slice(k)
        A[sy, sx][(fv > 0.46) & (fv < 0.50)] *= 0.4
    n, ao = mm._normal_ao(H, 1.0, 3, 0.4)
    return [_save(A, name + "_D"), _save(n, name + "_N"), _save(mm._orm(ao, R, M), name + "_ORM")]


def make_tex_fiori(size=1024, seed=1511, name="T_Viale_Fiori"):
    """Card dei fiori dello spartitraffico: begonie/gerani rossi su fogliame verde scuro. RGBA (alpha = maschera).
    Fascia u = lunghezza (tileable), v = altezza (0 = terra, 1 = cima)."""
    rng = np.random.default_rng(seed)
    A = np.zeros((size, size, 4), np.float32)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    v = 1.0 - (yy + 0.5) / size
    def disc(cx, cy, r, col, a=1.0):
        x0, x1 = int(max(cx - r - 1, 0)), int(min(cx + r + 2, size))
        y0, y1 = int(max(cy - r - 1, 0)), int(min(cy + r + 2, size))
        if x1 <= x0 or y1 <= y0:
            return
        d = np.hypot(xx[y0:y1, x0:x1] - cx, yy[y0:y1, x0:x1] - cy) / r
        m = d < 1
        sh = (0.75 + 0.25 * (1 - d))[..., None]
        sub = A[y0:y1, x0:x1]
        sub[m, :3] = (np.asarray(col)[None, None, :] * sh)[m]
        sub[m, 3] = a
    # fogliame: denso in basso, profilo superiore ondulato
    top = 0.62 + 0.10 * np.sin(np.linspace(0, 6 * math.pi, size)) + 0.06 * mm._noise(1, size, 18, seed)[0]
    for _ in range(5200):
        cx = rng.uniform(0, size)
        t = rng.uniform(0, 1) ** 0.7
        cy = size * (1 - t * top[int(cx) % size])
        g = _c((38, 74, 34)) * rng.uniform(0.7, 1.25)
        for dx in (-size, 0, size):        # tileable in u
            disc(cx + dx, cy, rng.uniform(7, 16), g)
    # fiori: grappoli rossi nella parte alta
    for _ in range(2600):
        cx = rng.uniform(0, size)
        tt = top[int(cx) % size]
        cy = size * (1 - rng.uniform(0.35, 1.02) * tt)
        col = _c((196, 22, 30)) * rng.uniform(0.8, 1.15) if rng.uniform() > 0.12 else _c((226, 60, 70))
        for dx in (-size, 0, size):
            disc(cx + dx, cy, rng.uniform(4, 8), np.clip(col, 0, 1))
    A[..., :3] = np.clip(A[..., :3], 0, 1)
    A[v < 0.04, 3] = 1.0
    A[v < 0.04, :3] = _c((30, 46, 26))
    ao = np.clip(0.55 + 0.45 * v, 0, 1)
    A[..., :3] *= ao[..., None]
    nrm = np.zeros((size, size, 3), np.float32); nrm[..., 0] = 0.5; nrm[..., 1] = 0.5; nrm[..., 2] = 1.0
    orm = mm._orm(ao, np.full((size, size), 0.75, np.float32), np.zeros((size, size), np.float32))
    return [_save(A, name + "_D"), _save(nrm, name + "_N"), _save(orm, name + "_ORM")]


def make_tex_edificio(size=1024, seed=1521, name="T_Fondale_EdificioVetrate"):
    """Edificio pubblico basso oltre il viale: campata da 4 m (u 0-1) alta 7 m (v 0,25-1): pilastro in mattoni,
    vetrate con montanti scuri, fascia di coronamento in cemento. v 0-0,25: tetto (u 0-0,5) e muro cieco in mattoni (u 0,5-1)."""
    A = np.zeros((size, size, 3), np.float32)
    R = np.full((size, size), 0.85, np.float32)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = (xx + 0.5) / size
    v = 1.0 - (yy + 0.5) / size
    xm = u * 4.0                          # metri nella campata
    zm = (v - 0.25) / 0.75 * 7.0          # metri in altezza
    brick = _c((150, 82, 58)) * (1 + 0.08 * mm._noise(size, size, 1.0, seed))[..., None]
    mort = ((np.abs(((zm / 0.075) % 1) - 0.5) > 0.42) | (np.abs((((xm + 0.125 * (np.floor(zm / 0.075) % 2)) / 0.25) % 1) - 0.5) > 0.46))
    brick = np.where(mort[..., None], _c((178, 160, 140)), brick)
    A[:] = brick
    up = v >= 0.25
    glass = up & (xm > 0.6) & (zm > 0.45) & (zm < 5.9)
    sky = np.clip((zm - 0.45) / 5.4, 0, 1)
    gcol = _c((46, 56, 64))[None, None, :] * (1 - sky[..., None]) + _c((128, 146, 158))[None, None, :] * sky[..., None]
    trees = mm._noise(size, size, 20, seed + 4) > 0.3
    gcol = np.where((trees & (zm < 4.2))[..., None], gcol * 0.7 + _c((40, 60, 36)) * 0.3, gcol)
    A[glass] = gcol[glass]
    R[glass] = 0.08
    mull = glass & ((np.abs(((xm - 0.6) / (3.4 / 2)) % 1 - 0.0) < 0.025) | (np.abs(zm - 3.0) < 0.05))
    A[mull] = _c((40, 40, 42))
    A[up & (zm >= 5.9)] = _c((196, 192, 182)) * (1 + 0.05 * mm._noise(size, size, 3, seed + 5))[up & (zm >= 5.9)][..., None]
    A[up & (zm >= 5.9) & (np.abs(zm - 6.05) < 0.04)] = _c((120, 116, 108))
    A[up & (zm <= 0.45)] = _c((126, 124, 120))
    roof = (~up) & (u < 0.5)
    A[roof] = _c((118, 116, 112)) * (1 + 0.1 * mm._noise(size, size, 1.5, seed + 6))[roof][..., None]
    nrm = np.zeros((size, size, 3), np.float32); nrm[..., 0] = 0.5; nrm[..., 1] = 0.5; nrm[..., 2] = 1.0
    orm = mm._orm(np.ones((size, size), np.float32), R, np.zeros((size, size), np.float32))
    return [_save(np.clip(A, 0, 1), name + "_D"), _save(nrm, name + "_N"), _save(orm, name + "_ORM")]


def make_textures():
    out = make_tex_atlas() + make_tex_fiori() + make_tex_edificio()
    print("texture:", out)
    return out


MAT_PROPS, MAT_FIORI, MAT_EDI = "M_Incrocio_Props", "M_Viale_Fiori", "M_Fondale_EdificioVetrate"


def build_materials():
    t = TEXDIR + "/"
    pk._pbr_material(MAT_PROPS, t + "T_Incrocio_Props_D.png", t + "T_Incrocio_Props_N.png", t + "T_Incrocio_Props_ORM.png")
    pk._pbr_material(MAT_FIORI, t + "T_Viale_Fiori_D.png", t + "T_Viale_Fiori_N.png", t + "T_Viale_Fiori_ORM.png", alpha=True)
    pk._pbr_material(MAT_EDI, t + "T_Fondale_EdificioVetrate_D.png", t + "T_Fondale_EdificioVetrate_N.png",
                     t + "T_Fondale_EdificioVetrate_ORM.png")
    return True


# =============================================================================================================
# helper geometrici con UV d'atlante
# =============================================================================================================
def _uv_faces_cell(bm, faces, cell):
    """UV per faccia: proiezione sull'asse dominante, normalizzata alla cella (celle a tinta unita con rumore)."""
    layer = bm.loops.layers.uv.verify()
    for f in faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        cs = [(lp.vert.co[a], lp.vert.co[b]) for lp in f.loops]
        a0, a1 = min(c[0] for c in cs), max(c[0] for c in cs)
        b0, b1 = min(c[1] for c in cs), max(c[1] for c in cs)
        for lp, (p, q) in zip(f.loops, cs):
            lp[layer].uv = cell_uv(cell, (p - a0) / (a1 - a0 + 1e-9), (q - b0) / (b1 - b0 + 1e-9))


def _new_faces(bm, before):
    bm.faces.ensure_lookup_table()
    return [f for f in bm.faces if f.index < 0 or f.index >= before]


class Builder:
    """Accumula geometria in un bmesh; ogni parte riceve la sua cella d'atlante."""

    def __init__(self):
        self.bm = bmesh.new()
        self.layer = self.bm.loops.layers.uv.verify()

    def _mark(self):
        self.bm.faces.index_update()
        return set(self.bm.faces)

    def _cell(self, before, cell, mi=0):
        fs = [f for f in self.bm.faces if f not in before]
        self.bm.normal_update()
        for f in fs:
            f.material_index = mi
        if cell is not None:
            _uv_faces_cell(self.bm, fs, cell)
        return fs

    def box(self, x0, x1, y0, y1, z0, z1, cell, mat=None, faces=("top", "bot", "xn", "xp", "yn", "yp"), mi=0):
        b = self._mark()
        pk._box(self.bm, x0, x1, y0, y1, z0, z1, faces=faces, mat=mat)
        return self._cell(b, cell, mi)

    def lathe(self, prof, n, cell, mat=Matrix(), cap_top=True, mi=0):
        b = self._mark()
        pk._lathe(self.bm, prof, n, mat=mat, cap_top=cap_top)
        fs = self._cell(b, None, mi)
        # UV cilindriche nella cella
        for f in fs:
            for lp in f.loops:
                c = mat.inverted() @ lp.vert.co
                ang = (math.atan2(c.y, c.x) / (2 * math.pi)) % 1.0
                zmin, zmax = prof[0][1], prof[-1][1]
                lp[self.layer].uv = cell_uv(cell, ang, min(max((c.z - zmin) / (zmax - zmin + 1e-9), 0.0), 1.0))
        return fs

    def tube(self, pts, r, sides, cell, cap=True, mi=0):
        b = self._mark()
        pk._tube(self.bm, pts, r, sides, cap=cap)
        return self._cell(b, cell, mi)

    def poly(self, pts3, uvs, mi=0):
        vs = [self.bm.verts.new(p) for p in pts3]
        f = self.bm.faces.new(vs)
        f.material_index = mi
        for lp, uv in zip(f.loops, uvs):
            lp[self.layer].uv = uv
        return f

    def finish(self, name, coll, mats=(MAT_PROPS,), smooth=None):
        return pk._finish(name, self.bm, list(mats), coll, uv=None, smooth_angle=smooth)


def _ucx_boxes(name, boxes, coll):
    for u in [x for x in bpy.data.objects if x.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)
    pk._ucx(name, boxes, coll)


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


# =============================================================================================================
# prop: dissuasore, semaforo, cartelli, scooter
# =============================================================================================================
def build_dissuasore(coll, lod=0, name="SM_Morin_Dissuasore"):
    """Paracarro cilindrico in cemento grigio con testa arrotondata, h 0,65 m, Ø 0,24 (foto). Origine alla base."""
    n = (14, 10, 6)[lod]
    prof = [(0.125, 0.0), (0.125, 0.04), (0.115, 0.06), (0.115, 0.50)]
    if lod < 2:
        prof += [(0.108, 0.56), (0.088, 0.61), (0.055, 0.64), (0.0, 0.65)]
    else:
        prof += [(0.07, 0.62), (0.0, 0.65)]
    B = Builder()
    B.lathe(prof, n, "cemento", cap_top=False)
    o = B.finish(name + _sfx(lod), coll, smooth=40)
    if lod == 0:
        _ucx_boxes(name, [(-0.12, 0.12, -0.12, 0.12, 0.0, 0.65)], coll)
    return o


def _lanterna(B, x, y, z0, facing, lod, h=0.90, w=0.30, d=0.24):
    """Lanterna a tre luci con la faccia verso `facing` (+1 = +X, -1 = -X); centro della faccia in (x, y)."""
    xf = x + facing * d / 2
    B.box(min(x - facing * d / 2, xf), max(x - facing * d / 2, xf), y - w / 2, y + w / 2, z0, z0 + h, "nero",
          faces=("top", "bot", "yn", "yp", "xn" if facing > 0 else "xp"))
    # faccia con le lenti
    xs = xf + facing * 0.001
    pts = [(xs, y + facing * w / 2, z0), (xs, y - facing * w / 2, z0), (xs, y - facing * w / 2, z0 + h), (xs, y + facing * w / 2, z0 + h)]
    B.poly(pts, [cell_uv("lanterna", 0, 0, 0), cell_uv("lanterna", 1, 0, 0), cell_uv("lanterna", 1, 1, 0), cell_uv("lanterna", 0, 1, 0)])
    if lod == 0:   # visiere
        for j in range(3):
            zc = z0 + h * (1 - (j + 0.5) / 3) + 0.11
            B.box(min(xf, xf + facing * 0.16), max(xf, xf + facing * 0.16), y - 0.11, y + 0.11, zc, zc + 0.012, "nero")
        # pannello di contrasto
        xb = x - facing * d / 2
        B.box(min(xb, xb - facing * 0.01), max(xb, xb - facing * 0.01), y - 0.24, y + 0.24, z0 - 0.06, z0 + h + 0.06, "nero")


def build_semaforo(coll, lod=0, name="SM_Morin_Semaforo"):
    """Palo verde scuro h 4,6 m (Ø 0,12), lanterna a tre luci in alto e una ripetitrice a 2,3 m, entrambe verso -X
    (origine alla base del palo; ruotare per orientare). Foto: pali verde scuro con lanterne nere."""
    n = (10, 8, 6)[lod]
    B = Builder()
    B.lathe([(0.10, 0.0), (0.10, 0.25), (0.065, 0.30), (0.06, 4.60), (0.0, 4.66)], n, "verde", cap_top=False)
    _lanterna(B, -0.20, 0.0, 3.55, -1, lod)
    if lod < 2:
        _lanterna(B, -0.18, 0.0, 2.05, -1, lod, h=0.72, w=0.24, d=0.20)
        B.box(-0.10, -0.05, -0.04, 0.04, 3.70, 3.78, "verde")
        B.box(-0.10, -0.05, -0.04, 0.04, 4.30, 4.38, "verde")
    o = B.finish(name + _sfx(lod), coll)
    if lod == 0:
        _ucx_boxes(name, [(-0.10, 0.10, -0.10, 0.10, 0.0, 4.6), (-0.34, -0.06, -0.16, 0.16, 2.0, 2.8)], coll)
    return o


def _palo(B, h, n, r=0.032):
    B.lathe([(r, 0.0), (r, h), (0.0, h + 0.02)], n, "retro", cap_top=False)


def build_cartello_precedenza(coll, lod=0, name="SM_Morin_CartelloPrecedenza"):
    """Dare precedenza: triangolo (lato 0,90 m) con la punta in basso, bordo superiore a 2,90 m, su palo grigio.
    Pannello rivolto verso -X (come SM_Morin_CartelloP). Origine alla base del palo."""
    B = Builder()
    _palo(B, 2.92, (8, 6, 4)[lod])
    s, zt, x = 0.90, 2.90, -0.05
    h = s * math.sqrt(3) / 2
    tri = [(x, s / 2, zt), (x, -s / 2, zt), (x, 0.0, zt - h)]          # visto da -X: +Y a sinistra
    uvs = [cell_uv("precedenza", 0.05, 0.93, 0), cell_uv("precedenza", 0.95, 0.93, 0), cell_uv("precedenza", 0.5, 0.07, 0)]
    B.poly(tri, uvs)
    back = [(x + 0.015, -s / 2, zt), (x + 0.015, s / 2, zt), (x + 0.015, 0.0, zt - h)]
    B.poly(back, [cell_uv("retro", 0, 1), cell_uv("retro", 1, 1), cell_uv("retro", 0.5, 0)])
    if lod < 2:
        b = B._mark()
        for p, q in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            pk._quad(B.bm, [p, q, (q[0] + 0.015, q[1], q[2]), (p[0] + 0.015, p[1], p[2])])
        B._cell(b, "retro")
        B.box(-0.035, 0.0, -0.05, 0.05, zt - 0.62, zt - 0.56, "retro")
        B.box(-0.035, 0.0, -0.05, 0.05, zt - 0.12, zt - 0.06, "retro")
    o = B.finish(name + _sfx(lod), coll)
    if lod == 0:
        _ucx_boxes(name, [(-0.04, 0.04, -0.04, 0.04, 0.0, 2.9)], coll)
    return o


def build_cartello_obbligo(coll, lod=0, name="SM_Morin_CartelloObbligoDestra"):
    """Direzione obbligatoria a destra: disco blu Ø 0,60 m (centro a 1,95 m) su palo grigio, pannello verso -X.
    Freccia verso la destra di chi guarda il pannello (verso -Y). Origine alla base del palo."""
    B = Builder()
    _palo(B, 2.27, (8, 6, 4)[lod])
    n = (20, 14, 10)[lod]
    r, zc, x = 0.30, 1.95, -0.05
    ring = [(x, r * math.cos(2 * math.pi * k / n), zc + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    front = list(reversed(ring))          # normale verso -X
    uvs = [cell_uv("obbligo", 0.5 - p[1] / (2 * r) * 0.96, 0.5 + (p[2] - zc) / (2 * r) * 0.96, 0) for p in front]
    B.poly(front, uvs)
    back = [(x + 0.015, p[1], p[2]) for p in ring]
    B.poly(back, [cell_uv("retro", 0.5 + p[1], 0.5 + p[2] - zc) for p in back])
    if lod < 2:
        b = B._mark()
        for k in range(n):
            p, q = ring[k], ring[(k + 1) % n]
            pk._quad(B.bm, [q, p, (p[0] + 0.015, p[1], p[2]), (q[0] + 0.015, q[1], q[2])])
        B._cell(b, "retro")
    o = B.finish(name + _sfx(lod), coll)
    if lod == 0:
        _ucx_boxes(name, [(-0.04, 0.04, -0.04, 0.04, 0.0, 2.27)], coll)
    return o


def _wheel(B, x, r, w, n, cell="gomma"):
    m = Matrix.Translation((x, 0, r)) @ Matrix.Rotation(math.radians(90), 4, "X")
    B.lathe([(r * 0.55, -w / 2), (r, -w / 2), (r, w / 2), (r * 0.55, w / 2)], n, cell, mat=m, cap_top=False)
    B.lathe([(r * 0.56, -w / 2 + 0.004), (0.0, -w / 2 + 0.004)], n, "metallo", mat=m, cap_top=False)
    B.lathe([(0.0, w / 2 - 0.004), (r * 0.56, w / 2 - 0.004)], n, "metallo", mat=m, cap_top=False)


def _taper_box(B, x0, x1, w0, w1, z0, z1, ztop1, cell, wt=None):
    """Scatola a sezione variabile: in x0 larga w0 alta z0..z1, in x1 larga w1 alta z0..ztop1 (wt = larghezza in alto)."""
    wt = wt or (w0, w1)
    P = [(x0, -w0 / 2, z0), (x1, -w1 / 2, z0), (x1, w1 / 2, z0), (x0, w0 / 2, z0),
         (x0, -wt[0] / 2, z1), (x1, -wt[1] / 2, ztop1), (x1, wt[1] / 2, ztop1), (x0, wt[0] / 2, z1)]
    b = B._mark()
    vs = [B.bm.verts.new(p) for p in P]
    fs = [B.bm.faces.new([vs[i] for i in idx]) for idx in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))]
    bmesh.ops.recalc_face_normals(B.bm, faces=fs)
    B._cell(b, cell)


def build_scooter(coll, lod=0, name="SM_Morin_Scooter", body="scooter"):
    """Scooter generico a ruote alte (~1,95 x 0,70 x 1,30 m), senza marchi; muso verso +X, origine a terra al centro."""
    n = (14, 10, 6)[lod]
    B = Builder()
    _wheel(B, 0.68, 0.27, 0.10, n)
    _wheel(B, -0.62, 0.26, 0.11, n)
    # pedana, scudo anteriore, codone, sella
    _taper_box(B, -0.30, 0.42, 0.34, 0.36, 0.30, 0.40, 0.40, body)
    _taper_box(B, 0.42, 0.62, 0.40, 0.30, 0.30, 0.95, 1.05, body, wt=(0.40, 0.26))
    _taper_box(B, -0.92, -0.25, 0.22, 0.40, 0.42, 0.62, 0.70, body, wt=(0.20, 0.40))
    _taper_box(B, -0.80, -0.08, 0.26, 0.30, 0.70, 0.80, 0.80, "nero")
    if lod < 2:
        B.box(-0.98, -0.88, -0.10, 0.10, 0.55, 0.66, "lanterna" if False else "nero")    # fanale posteriore
        _taper_box(B, 0.52, 0.80, 0.18, 0.12, 0.55, 0.70, 0.62, body)                    # parafango anteriore
    # forcella e manubrio
    B.tube([(0.68, 0.0, 0.27), (0.58, 0.0, 1.02)], 0.03, (6, 5, 4)[lod], "metallo")
    B.tube([(0.56, -0.36, 1.10), (0.56, 0.36, 1.10)], 0.02, (6, 5, 4)[lod], "nero")
    _taper_box(B, 0.50, 0.66, 0.22, 0.18, 1.02, 1.14, 1.12, body)                        # coprimanubrio
    if lod == 0:
        B.box(0.64, 0.68, -0.08, 0.08, 1.05, 1.12, "bianco")                            # faro
        for s in (-1, 1):                                                                # specchietti
            B.tube([(0.56, s * 0.24, 1.12), (0.54, s * 0.30, 1.30)], 0.008, 4, "nero")
            B.box(0.52, 0.56, s * 0.30 - 0.05, s * 0.30 + 0.05, 1.28, 1.34, "nero")
        B.tube([(0.80, 0.0, 1.16), (0.72, 0.0, 1.28)], 0.003, 3, "nero")
        B.box(0.58, 0.62, -0.16, 0.16, 1.14, 1.32, "vetro")                              # parabrezza basso
        B.tube([(-0.35, 0.12, 0.10), (-0.28, 0.16, 0.30)], 0.012, 4, "metallo")          # cavalletto laterale
    o = B.finish(name + _sfx(lod), coll)
    if lod == 0:
        _ucx_boxes(name, [(-0.95, 0.90, -0.22, 0.22, 0.0, 0.85), (0.45, 0.70, -0.36, 0.36, 0.85, 1.20)], coll)
    return o


# =============================================================================================================
# spartitraffico con fiori (modulo 4,75 m)
# =============================================================================================================
SPART_L = 4.75


def build_spartitraffico(coll, lod=0, name="SM_Viale_Spartitraffico_Fiori"):
    """Aiuola rialzata sullo spartitraffico (Y 131-132, piano in pietra a Z 0,15): cordolo bianco 0,12 m alto fino a Z 0,27,
    terra a Z 0,23, fiori rossi su card masked a due facce (h 0,32). Origine all'inizio del modulo (X), Y 131,5, Z 0."""
    B = Builder()
    L, hw, c, z0, zc, zt = SPART_L, 0.50, 0.12, 0.15, 0.27, 0.23
    mats = ["M_Pav_Fascia", "M_Pav_Terra", MAT_FIORI]
    b = B._mark()
    for (xa, xb, ya, yb) in ((0, L, -hw, -hw + c), (0, L, hw - c, hw), (0, c, -hw + c, hw - c), (L - c, L, -hw + c, hw - c)):
        pk._box(B.bm, xa, xb, ya, yb, z0, zc, faces=("top", "xn", "xp", "yn", "yp"))
    fs = B._cell(b, None, 0)
    pk._uv_box(B.bm, ["M_Pav_Fascia"])
    b = B._mark()
    pk._quad(B.bm, [(c, -hw + c, zt), (L - c, -hw + c, zt), (L - c, hw - c, zt), (c, hw - c, zt)])
    fs = B._cell(b, None, 1)
    for f in fs:
        for lp in f.loops:
            lp[B.layer].uv = (lp.vert.co.x / 2.0, lp.vert.co.y / 2.0)
    # card dei fiori: 2 file longitudinali + card trasversali (LOD0), una fila al LOD2
    rows = (-0.18, 0.18) if lod < 2 else (0.0,)
    nseg = (3, 2, 1)[lod]
    hc = 0.50
    for yr in rows:
        for i in range(nseg):
            xa, xb = c + (L - 2 * c) * i / nseg, c + (L - 2 * c) * (i + 1) / nseg
            for s in (1, -1):
                pts = [(xa, yr + s * 0.10, zt - 0.02), (xb, yr - s * 0.10, zt - 0.02), (xb, yr - s * 0.10, zt + hc), (xa, yr + s * 0.10, zt + hc)]
                uvs = [(xa / 1.2, 0.0), (xb / 1.2, 0.0), (xb / 1.2, 1.0), (xa / 1.2, 1.0)]
                B.poly(pts, uvs, mi=2)
    if lod == 0:
        for xc in np.arange(0.40, L - 0.3, 0.55):
            pts = [(xc - 0.08, -0.36, zt - 0.02), (xc + 0.08, 0.36, zt - 0.02), (xc + 0.08, 0.36, zt + hc * 0.9), (xc - 0.08, -0.36, zt + hc * 0.9)]
            B.poly(pts, [(0.1 + xc, 0), (0.7 + xc, 0), (0.7 + xc, 0.95), (0.1 + xc, 0.95)], mi=2)
    o = B.finish(name + _sfx(lod), coll, mats=mats)
    return o


# =============================================================================================================
# modulo strada dell'incrocio (sostituisce Viale_Strada_SO_00, X 3-22)
# =============================================================================================================
def build_incrocio(coll, lod=0, name="SM_Viale_Italia_Incrocio"):
    """Come SM_Viale_Italia_Strada (origine all'inizio del modulo, sul ciglio Y 120,85) con:
    cordolo lato giardini abbassato sull'imbocco della strada del molo (X 6,5-9,55), spartitraffico a raso
    nell'attraversamento (X 14-16,5), strisce pedonali sul viale, linee d'arresto, frecce di corsia, niente stalli
    davanti all'imbocco e alle strisce."""
    import morin_viale as mv
    y0 = mv.Y0_STRADA
    L = MOD_L
    T = mv.TILE_ASF
    B = Builder()
    lay = B.layer
    mouth = (X_MOUTH[0] - MOD_X0, X_MOUTH[1] - MOD_X0)
    zeb = (X_ZEBRA_V[0] - MOD_X0, X_ZEBRA_V[1] - MOD_X0)
    xs = sorted(set([0.0, mouth[0], mouth[1], zeb[0], zeb[1], L] + ([4.75, 9.5, 14.25] if lod < 2 else [])))
    segs = list(zip(xs[:-1], xs[1:]))

    def zband(k, xa, xb):
        ya, yb, z, mi_ = mv.BANDE[k]
        xc = (xa + xb) / 2
        if k == 0 and mouth[0] <= xc <= mouth[1]:
            return Z_ASF_VIALE, 0
        if abs(ya - Y_SPART[0]) < 1e-3 and zeb[0] <= xc <= zeb[1]:
            return Z_ASF_VIALE, 0
        return z, mi_

    def face(pts, mi_, uvmode):
        f = B.poly(pts, [(0, 0)] * len(pts), mi=mi_)
        t = T if mi_ == 0 else 1.0
        for lp in f.loops:
            c = lp.vert.co
            if uvmode == "top":
                lp[lay].uv = ((c.x + MOD_X0) / t, (c.y + y0) / t)
            else:
                lp[lay].uv = ((c.x + c.y) / 1.0, c.z / 1.0)
        return f

    prev = [(0.0, 0) for _ in segs]
    for k, (ya, yb, z, mi_) in enumerate(mv.BANDE):
        a, b = ya - y0, yb - y0
        cur = []
        for (xa, xb), (pz, _) in zip(segs, prev):
            zz, mm_ = zband(k, xa, xb)
            cur.append((zz, mm_))
            face([(xa, a, zz), (xb, a, zz), (xb, b, zz), (xa, b, zz)], mm_, "top")
            if abs(zz - pz) > 1e-3 and (lod < 2 or k == 0):
                z0_, z1_ = min(zz, pz), max(zz, pz)
                if zz > pz:
                    face([(xa, a, z0_), (xb, a, z0_), (xb, a, z1_), (xa, a, z1_)], 1, "side")
                else:
                    face([(xb, a, z0_), (xa, a, z0_), (xa, a, z1_), (xb, a, z1_)], 1, "side")
        # gradini lungo X dentro la banda (bordi dell'imbocco e del varco nello spartitraffico)
        for i in range(len(segs) - 1):
            za, zb = cur[i][0], cur[i + 1][0]
            if abs(za - zb) > 1e-3 and lod < 2:
                x = segs[i][1]
                if za > zb:   # faccia verso +X
                    face([(x, a, zb), (x, b, zb), (x, b, za), (x, a, za)], 1, "side")
                else:
                    face([(x, b, za), (x, a, za), (x, a, zb), (x, b, zb)], 1, "side")
        prev = cur
    a = mv.BANDE[-1][1] - y0
    face([(L, a, -0.05), (0, a, -0.05), (0, a, prev[0][0]), (L, a, prev[0][0])], 1, "side")
    # segnaletica (5 mm sopra il piano), materiale 2
    dz = 0.005

    def rect(xa, xb, ya, yb, z):
        face([(xa, ya - y0, z + dz), (xb, ya - y0, z + dz), (xb, yb - y0, z + dz), (xa, yb - y0, z + dz)], 2, "top")

    def cut(xa, xb, holes):
        out = [(xa, xb)]
        for ha, hb in holes:
            nxt = []
            for p, q in out:
                if hb <= p or ha >= q:
                    nxt.append((p, q))
                    continue
                if ha > p:
                    nxt.append((p, ha))
                if hb < q:
                    nxt.append((hb, q))
            out = nxt
        return [s for s in out if s[1] - s[0] > 0.05]

    for yc, w, z in mv.STRISCE_CONT:
        if lod == 2 and z > 0.1:
            continue
        holes = [zeb] if z < 0.1 else []
        if abs(yc - 123.30) < 1e-3:
            holes = [(zeb[0] - 1.0, zeb[1] + 0.5)]
        for xa, xb in cut(0.0, L, holes):
            rect(xa, xb, yc - w / 2, yc + w / 2, z)
    for yc, w in mv.STRISCE_TRAT:
        for xa in (0.25, 0.25 + L / 2):
            for p, q in cut(xa, xa + 4.5, [(zeb[0] - 1.2, zeb[1] + 1.2)]):
                rect(p, q, yc - w / 2, yc + w / 2, 0.02)
    # strisce pedonali del viale: barre 0,5 m (lungo Y) x 2,5 m (lungo X), passo 1 m, su entrambe le carreggiate
    for (ya, yb) in ((121.25, 130.85), (132.15, 138.55)):
        y = ya
        while y + 0.5 <= yb + 1e-6:
            rect(zeb[0], zeb[1], y, y + 0.5, 0.02)
            y += 1.0
    if lod < 2:
        # linee d'arresto (0,5 m) prima delle strisce: carreggiata A (verso +X) e B (verso -X)
        rect(zeb[0] - 1.6, zeb[0] - 1.1, 123.40, 130.75, 0.02)
        rect(zeb[1] + 1.1, zeb[1] + 1.6, 132.25, 138.30, 0.02)
        # frecce dritte nelle corsie (A verso +X, B verso -X)
        for (xc, yc, s) in ((zeb[0] - 5.5, 125.15, 1), (zeb[0] - 5.5, 128.95, 1), (zeb[1] + 3.4, 134.4, -1),
                            (zeb[1] + 3.4, 136.65, -1)):
            if not (0.3 < min(xc - s * 2.0, xc + s * 1.6) and max(xc - s * 2.0, xc + s * 1.6) < L - 0.05):
                continue
            x0, x1 = xc - s * 2.0, xc + s * 0.6
            rect(min(x0, x1), max(x0, x1), yc - 0.08, yc + 0.08, 0.02)
            tip = xc + s * 1.6
            f = face([(xc + s * 0.6, yc - 0.40 - y0 + y0 - y0, 0.02 + dz), (tip, yc - y0, 0.02 + dz), (xc + s * 0.6, yc + 0.40 - y0, 0.02 + dz)], 2, "top")
            if s < 0:
                f.normal_flip()
    if lod == 0:    # stalli lato giardini, ma non davanti all'imbocco e alle strisce
        for xa in np.arange(0.0, L - 0.01, 4.75):
            if mouth[0] - 1.0 <= xa <= mouth[1] + 1.0 or zeb[0] - 1.6 <= xa <= zeb[1] + 1.0:
                continue
            rect(xa, xa + 0.1, 121.05, 123.24, 0.02)
    B.bm.normal_update()
    for f in B.bm.faces:   # tutte le facce orizzontali verso l'alto
        if abs(f.normal.z) > 0.5 and f.normal.z < 0:
            f.normal_flip()
    o = pk._finish(name + _sfx(lod), B.bm, ["M_Molo_Asfalto", "M_Pav_Fascia", "M_Viale_Segnaletica"], coll, uv=None)
    return o


# =============================================================================================================
# marciapiede dell'angolo + strisce sull'imbocco della strada del molo (pezzo unico, coordinate di progetto)
# =============================================================================================================
def build_marciapiede(coll, name="SM_Viale_Incrocio_Marciapiede"):
    """Marciapiede in masselli grigi (Z 0,15) X 9,55-20, Y 113,75-120,85 fra la strada del molo, il ramo del parcheggio
    e Viale Italia; cordolo in pietra chiara (0,20) verso la strada del molo e verso il parcheggio, raccordo smussato
    all'imbocco. Strisce pedonali (OSM zebra (9,1; 121,0)) sull'asfalto della strada del molo, Y 117,9-120,4."""
    B = Builder()
    lay = B.layer
    x0, x1, y0, y1 = MARC
    zf, c = 0.15, 0.20
    R = 1.2
    # piano dei masselli (dentro i cordoli), con smusso a NO
    top = [(x0 + c, y0 - 0.2), (x1 - c, y0 - 0.2), (x1 - c, y1), (x0 + c + R, y1), (x0 + c, y1 - R)]
    f = B.poly([(x, y, zf) for x, y in top], [(x / 2.8, y / 2.8) for x, y in top], mi=0)
    # cordoli: lato strada del molo (con smusso), lato parcheggio
    def curb(p, q):
        p, q = Vector(p), Vector(q)
        d = (q - p).normalized()
        nrm = Vector((d.y, -d.x))
        b = B._mark()
        P = [p, q, q + nrm * c, p + nrm * c]
        # sopra
        pk._quad(B.bm, [(v.x, v.y, zf) for v in P])
        # faccia esterna verso l'asfalto
        pk._quad(B.bm, [(q.x, q.y, 0.0), (p.x, p.y, 0.0), (p.x, p.y, zf), (q.x, q.y, zf)])
        B._cell(b, None, 1)
    curb((x0, y0 - 0.2), (x0, y1 - R))
    curb((x0, y1 - R), (x0 + R, y1))
    curb((x1, y1), (x1, y0 - 0.2))
    # cordolo del bordo sul ramo (Y 113,75) gia' nel molo: qui solo il fianco verso il ramo fra X 9,55 e 10,15
    pk._quad(B.bm, [(x1 - c, y0 - 0.2, 0.0), (x1 - c, y0 - 0.2, zf), (x0 + c, y0 - 0.2, zf), (x0 + c, y0 - 0.2, 0.0)])
    # lato viale: faccia verso +Y fino alla quota dell'asfalto del viale
    pk._quad(B.bm, [(x1, y1, 0.0), (x0 + R, y1, 0.0), (x0 + R, y1, zf), (x1, y1, zf)])
    B.bm.normal_update()
    for f in B.bm.faces:
        if f.material_index == 1 or abs(f.normal.z) < 0.5:
            f.material_index = 1
    pk._uv_box(B.bm, ["M_Molo_Masselli_Grigio", "M_Pav_Fascia", "M_Viale_Segnaletica"], keep=("M_Molo_Masselli_Grigio",))
    # strisce sull'imbocco: barre lungo Y (2,5 m), larghe 0,5 m, passo 1 m lungo X
    for xa in (6.70, 7.70, 8.70):
        pts = [(xa, 117.9, Z_MOLO + 0.004), (xa + 0.5, 117.9, Z_MOLO + 0.004), (xa + 0.5, 120.4, Z_MOLO + 0.004), (xa, 120.4, Z_MOLO + 0.004)]
        B.poly(pts, [(p[0], p[1]) for p in pts], mi=2)
    # linea d'arresto per chi esce dalla strada del molo (prima delle strisce)
    pts = [(6.6, 117.2, Z_MOLO + 0.004), (9.45, 117.2, Z_MOLO + 0.004), (9.45, 117.5, Z_MOLO + 0.004), (6.6, 117.5, Z_MOLO + 0.004)]
    B.poly(pts, [(p[0], p[1]) for p in pts], mi=2)
    B.bm.normal_update()
    for f in B.bm.faces:
        if abs(f.normal.z) > 0.5 and f.normal.z < 0:
            f.normal_flip()
    o = pk._finish(name, B.bm, ["M_Molo_Masselli_Grigio", "M_Pav_Fascia", "M_Viale_Segnaletica"], coll, uv=None)
    _ucx_boxes(name, [(x0, x1, y0 - 0.2, y1 - R, -0.30, zf), (x0 + R, x1, y1 - R, y1, -0.30, zf)], coll)
    return o


# =============================================================================================================
# dehors vetrato del ristorante d'angolo (pianta OSM B), tavoli e sedie bianchi
# =============================================================================================================
def _sedia(B, x, y, yaw, lod):
    m = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    B.box(-0.22, 0.22, -0.22, 0.22, 0.44, 0.48, "bianco", mat=m)                            # seduta
    B.box(-0.22, -0.18, -0.22, 0.22, 0.48, 0.86, "bianco", mat=m)                           # schienale
    if lod == 0:
        for sx in (-0.19, 0.19):
            for sy in (-0.19, 0.19):
                B.box(sx - 0.02, sx + 0.02, sy - 0.02, sy + 0.02, 0.0, 0.44, "bianco", mat=m,
                      faces=("xn", "xp", "yn", "yp"))
    else:
        B.box(-0.19, 0.19, -0.19, 0.19, 0.0, 0.44, "bianco", mat=m, faces=("xn", "xp", "yn", "yp"))


def _tavolo(B, x, y, lod, s=0.70):
    B.box(x - s / 2, x + s / 2, y - s / 2, y + s / 2, 0.72, 0.75, "bianco")
    B.box(x - 0.03, x + 0.03, y - 0.03, y + 0.03, 0.0, 0.72, "metallo", faces=("xn", "xp", "yn", "yp"))
    if lod == 0:
        B.box(x - 0.22, x + 0.22, y - 0.22, y + 0.22, 0.0, 0.03, "metallo")


DEHORS_TAVOLI_EST = [(1.55, 112.6), (3.65, 112.6), (1.55, 114.7), (3.65, 114.7), (2.6, 116.6)]
DEHORS_TAVOLI_INT = [(-6.6, 113.0), (-4.4, 113.0), (-2.2, 113.0), (-6.6, 115.2), (-4.4, 115.2), (-2.2, 115.2)]
OMBRELLONE = (4.7, 116.9)


def build_dehors(coll, lod=0, name="SM_Molo_DehorsVetrato"):
    """Dehors vetrato 8,6 x 5,3 m (pianta OSM B): pareti in vetro su telaio in metallo scuro (montanti ogni ~1,45 m,
    zoccolo e traverso), tetto piano a 2,75 m con tettoia/mantovana bianca sporgente 0,6 m; dentro e fuori (verso la
    strada del molo, X 1-5) tavoli quadrati e sedie bianche, un ombrellone chiuso. Coordinate di progetto, posa (0,0,0)."""
    x0, x1, y0, y1 = B_DEHORS
    H = 2.75
    B = Builder()
    s = 0.04
    # montanti
    nx = max(2, int(round((x1 - x0) / 1.45)))
    ny = max(2, int(round((y1 - y0) / 1.45)))
    xs = np.linspace(x0, x1, nx + 1)
    ys = np.linspace(y0, y1, ny + 1)
    posts = [(x, y0) for x in xs] + [(x, y1) for x in xs] + [(x0, y) for y in ys[1:-1]] + [(x1, y) for y in ys[1:-1]]
    for (px, py) in posts:
        if lod == 2 and not (px in (x0, x1) and py in (y0, y1)):
            continue
        B.box(px - s, px + s, py - s, py + s, 0.0, H, "telaio", faces=("xn", "xp", "yn", "yp"))
    # zoccolo e traverso
    for (za, zb) in ((0.0, 0.25), (2.25, 2.32)) if lod < 2 else ((0.0, 0.25),):
        for (xa, xb, ya, yb) in ((x0, x1, y0 - s, y0 + s), (x0, x1, y1 - s, y1 + s), (x0 - s, x0 + s, y0, y1), (x1 - s, x1 + s, y0, y1)):
            B.box(xa, xb, ya, yb, za, zb, "telaio", faces=("top", "xn", "xp", "yn", "yp"))
    # vetri (due facce)
    def glass(p, q):
        for a, b in ((p, q), (q, p)):
            pts = [(a[0], a[1], 0.25), (b[0], b[1], 0.25), (b[0], b[1], H - 0.05), (a[0], a[1], H - 0.05)]
            B.poly(pts, [cell_uv("vetro", 0, 0), cell_uv("vetro", 1, 0), cell_uv("vetro", 1, 1), cell_uv("vetro", 0, 1)])
    glass((x0, y0), (x1, y0)); glass((x1, y0), (x1, y1)); glass((x1, y1), (x0, y1)); glass((x0, y1), (x0, y0))
    # tetto e tettoia sporgente (mantovana)
    ov = 0.6
    B.box(x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, H, H + 0.18, "bianco")
    tx0, tx1, ty0, ty1 = x0 - ov * 0.3, x1 + ov, y0 - ov * 0.3, y1 + ov
    zt0, zt1 = H + 0.12, H - 0.10
    b = B._mark()
    # falde inclinate verso l'esterno (lato est e nord, che danno sulla strada e sul viale)
    pk._quad(B.bm, [(x1, y0, zt0), (tx1, ty0, zt1), (tx1, ty1, zt1), (x1, y1, zt0)])
    pk._quad(B.bm, [(x1, y1, zt0), (tx1, ty1, zt1), (tx0, ty1, zt1), (x0, y1, zt0)])
    B._cell(b, "bianco")
    if lod < 2:
        md = 0.28
        for p, q in (((tx1, ty0), (tx1, ty1)), ((tx1, ty1), (tx0, ty1))):
            for (a, bb) in ((p, q), (q, p)):
                pts = [(a[0], a[1], zt1 - md), (bb[0], bb[1], zt1 - md), (bb[0], bb[1], zt1), (a[0], a[1], zt1)]
                L = math.dist(a, bb)
                B.poly(pts, [cell_uv("mantovana", 0, 0), cell_uv("mantovana", 1, 0), cell_uv("mantovana", 1, 1), cell_uv("mantovana", 0, 1)])
    # tavoli e sedie
    for (tx, ty) in DEHORS_TAVOLI_EST + (DEHORS_TAVOLI_INT if lod < 2 else []):
        _tavolo(B, tx, ty, lod)
        if lod < 2:
            for k, (dx, dy, yaw) in enumerate(((-0.62, 0, 0), (0.62, 0, 180), (0, -0.62, 90), (0, 0.62, -90))):
                if (tx, ty) in DEHORS_TAVOLI_INT and k > 1:
                    continue
                _sedia(B, tx + dx, ty + dy, yaw, lod)
    # ombrellone chiuso (palo e telo raccolto)
    ox, oy = OMBRELLONE
    B.lathe([(0.03, 0.0), (0.03, 2.5), (0.0, 2.55)], (6, 5, 4)[lod], "metallo", mat=Matrix.Translation((ox, oy, 0)), cap_top=False)
    B.lathe([(0.04, 1.0), (0.16, 1.55), (0.12, 2.2), (0.04, 2.5)], (8, 6, 4)[lod], "tessuto", mat=Matrix.Translation((ox, oy, 0)))
    B.box(ox - 0.25, ox + 0.25, oy - 0.25, oy + 0.25, 0.0, 0.08, "cemento")
    o = B.finish(name + _sfx(lod), coll)
    if lod == 0:
        boxes = [(x0 - s, x1 + s, y0 - s, y1 + s, 0.0, H + 0.18)]
        for (tx, ty) in DEHORS_TAVOLI_EST:
            boxes.append((tx - 0.35, tx + 0.35, ty - 0.35, ty + 0.35, 0.0, 0.75))
        boxes.append((ox - 0.12, ox + 0.12, oy - 0.12, oy + 0.12, 0.0, 2.5))
        _ucx_boxes(name, boxes, coll)
    return o


# =============================================================================================================
# edificio basso con vetrate oltre il viale (fondale, niente UCX)
# =============================================================================================================
def build_edificio(coll, lod=0, name="SM_Fondale_EdificioVetrate"):
    """Edificio pubblico basso 32 x 12 x 7 m, mattoni e grandi vetrate (foto, a destra oltre il viale). Origine al centro
    del fronte a terra, fronte verso -Y (il viale), come i palazzi di fondale."""
    W, D, Hh = 32.0, 12.0, 7.0
    B = Builder()
    lay = B.layer
    nb = int(W / 4)

    def fac(p, q, bays):
        # p, q: estremi a terra (x, y); u = metri / 4, v da 0,25 a 1
        L = math.dist(p, q)
        f = B.poly([(p[0], p[1], 0), (q[0], q[1], 0), (q[0], q[1], Hh), (p[0], p[1], Hh)],
                   [(0, 0.25), (L / 4.0, 0.25), (L / 4.0, 1.0), (0, 1.0)])
        return f
    xs = np.linspace(-W / 2, W / 2, (nb if lod < 2 else 1) + 1)
    for a, b in zip(xs[:-1], xs[1:]):
        fac((a, 0), (b, 0), 1)
    fac((W / 2, 0), (W / 2, D), 3)
    fac((-W / 2, D), (-W / 2, 0), 3)
    fac((W / 2, D), (-W / 2, D), 8)
    B.poly([(-W / 2, 0, Hh), (W / 2, 0, Hh), (W / 2, D, Hh), (-W / 2, D, Hh)], [(0, 0), (0.5, 0), (0.5, 0.25), (0, 0.25)])
    if lod < 2:
        # pensilina d'ingresso e parapetto del coronamento
        b0 = len(B.bm.faces)
        B.box(-3.0, 3.0, -2.2, 0.0, 3.1, 3.3, None)
        B.box(-W / 2 - 0.1, W / 2 + 0.1, -0.1, 0.0, Hh - 1.0, Hh + 0.4, None, faces=("top", "yn", "xn", "xp"))
        for f in list(B.bm.faces)[b0:]:
            for lp in f.loops:
                lp[lay].uv = (0.25 + 0.1 * (lp.vert.co.x % 1), 0.98)
    o = B.finish(name + _sfx(lod), coll, mats=(MAT_EDI,))
    return o


# =============================================================================================================
# parcheggio v3: asfalto con la fila a pettine e aiuola ristretta
# =============================================================================================================
def _pettine_stalls():
    """Linee di separazione degli stalli a 60 gradi: (punto sulla linea Y 111,0, direzione)."""
    a = math.radians(PETT_ANG)
    d = Vector((math.cos(a), math.sin(a)))
    pitch = PETT_STALL / math.sin(a)          # passo lungo X
    xs = list(np.arange(PETT_X[0], PETT_X[1] - pitch + 1e-6, pitch))
    return xs, d, pitch


def build_asfalto_v2(coll, name="SM_Parcheggio_Asfalto_v2"):
    bm = bmesh.new()
    mats = ["M_Parcheggio_Asfalto", "M_Viale_Segnaletica", "M_Pav_Fascia", "M_Pav_Terra"]
    f = mp._poly(bm, mp.OUTLINE, mp.Z_ASF, 0)
    bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    zs = mp.Z_ASF + 0.004
    w = 0.12
    # fila in linea lato mare (invariata)
    ya, yb, yl, xr = mp.Y_SOSTA_MARE[0] + 0.3, mp.Y_SOSTA_MARE[1] - w / 2, mp.Y_SOSTA_MARE[1], mp.MARE_X
    mp._stripe(bm, (xr[0], yl), (xr[1], yl), w, zs, 1)
    x = xr[0]
    while x <= xr[1] + 1e-6:
        mp._stripe(bm, (x, ya), (x, yb), w, zs, 1)
        x += mp.MARE_L
    # fila lato citta' a pettine (60 gradi): linea d'ingresso continua + separatori inclinati
    xs, d, pitch = _pettine_stalls()
    y0, y1 = Y_PETT_C[0] + w / 2, Y_PETT_C[1] - 0.15
    Ls = (y1 - y0) / d.y
    mp._stripe(bm, (xs[0], Y_PETT_C[0]), (xs[-1] + pitch, Y_PETT_C[0]), w, zs, 1)
    for x in xs + [xs[-1] + pitch]:
        p = Vector((x, y0))
        mp._stripe(bm, tuple(p), tuple(p + d * Ls), w, zs, 1)
    # seconda fila a pettine (90 gradi) lato viale: invariata
    x = mp.PETTINE_X[0]
    while x <= mp.PETTINE_X[1] + 1e-6:
        mp._stripe(bm, (x, mp.Y_PETTINE[0] + 0.25), (x, mp.Y_PETTINE[1] - 0.3), w, zs, 1)
        x += mp.PETTINE_W
    y = mp.Y_CORSIA[0] + 0.4
    while y + 0.5 <= mp.Y_CORSIA[1] - 0.3:
        mp._poly(bm, [(mp.ZEBRA_X[0], y), (mp.ZEBRA_X[1], y), (mp.ZEBRA_X[1], y + 0.5), (mp.ZEBRA_X[0], y + 0.5)], zs, 1)
        y += 1.0
    pk._box(bm, mp.X0, mp.X1, mp.Y_CORD0, mp.Y_CORD1, mp.Z_ASF, mp.Z_CORD, mi=2, faces=("top", "yp", "xn", "xp"))
    mp._aiuola(bm, mp.AIU_X[0], mp.AIU_X[1], Y_AIU_V3[0], Y_AIU_V3[1], c=0.15)
    o = pk._finish(name, bm, mats, coll, uv="world")
    N = mp.NOTCH
    _ucx_boxes(name, [(N[1], mp.X1, mp.Y_CORD1, 118.0, -0.30, mp.Z_ASF),
                      (mp.X0, N[1], mp.Y_CORD1, N[2], -0.30, mp.Z_ASF),
                      (mp.X0, N[1], N[3], 118.0, -0.30, mp.Z_ASF),
                      (mp.X1, 101.7, 113.5, 118.0, -0.30, mp.Z_ASF),
                      (mp.X0, mp.X1, mp.Y_CORD0, mp.Y_CORD1, -0.30, mp.Z_CORD),
                      (mp.AIU_X[0], mp.AIU_X[1], Y_AIU_V3[0], Y_AIU_V3[1], -0.30, 0.14)], coll)
    return o


# =============================================================================================================
# build
# =============================================================================================================
LODDED = ["SM_Morin_Dissuasore", "SM_Morin_Semaforo", "SM_Morin_CartelloPrecedenza", "SM_Morin_CartelloObbligoDestra",
          "SM_Morin_Scooter", "SM_Viale_Spartitraffico_Fiori", "SM_Viale_Italia_Incrocio", "SM_Molo_DehorsVetrato",
          "SM_Fondale_EdificioVetrate"]
SINGLE = ["SM_Viale_Incrocio_Marciapiede"]
SINGLE_PARK = ["SM_Parcheggio_Asfalto_v2"]


def build_all():
    coll = pk._coll(KIT)
    for lod in (0, 1, 2):
        build_dissuasore(coll, lod)
        build_semaforo(coll, lod)
        build_cartello_precedenza(coll, lod)
        build_cartello_obbligo(coll, lod)
        build_scooter(coll, lod)
        build_spartitraffico(coll, lod)
        build_incrocio(coll, lod)
        build_dehors(coll, lod)
        build_edificio(coll, lod)
    build_marciapiede(coll)
    build_asfalto_v2(coll)
    return report()


def report():
    out = {}
    for nm in LODDED:
        out[nm] = [pk.tri_count(bpy.data.objects[nm + _sfx(l)]) for l in (0, 1, 2)]
    for nm in SINGLE + SINGLE_PARK:
        out[nm] = [pk.tri_count(bpy.data.objects[nm])]
    ucx = {}
    for o in bpy.data.objects:
        if o.name.startswith("UCX_"):
            base = o.name[4:].rsplit("_", 1)[0]
            ucx[base] = ucx.get(base, 0) + 1
    for k, v in out.items():
        b = bpy.data.objects[k]
        print(k, v, "UCX", ucx.get(k, 0), "dim", tuple(round(d, 2) for d in b.dimensions))
    return out, ucx


# =============================================================================================================
# layout e CSV (coordinate di progetto -> UE: x*100, -y*100, z*100, yaw UE = -yaw)
# =============================================================================================================
def _ue(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0.0" if s in ("0", "-0", "") else (s if "." in s else s + ".0")


def _row_ue(a, n, x, y, z, yaw, pitch=0.0, roll=0.0):
    return ",".join([a, n, _ue(x * 100), _ue(-y * 100), _ue(z * 100), _ue(-yaw), _ue(pitch), _ue(roll)])


def layout_incrocio(seed=20261123):
    """Righe (asset, nome, x, y, z, yaw_blender) in coordinate di progetto."""
    rng = np.random.default_rng(seed)
    R = [("SM_Viale_Incrocio_Marciapiede", "Incrocio_Marciapiede", 0.0, 0.0, 0.0, 0.0),
         ("SM_Molo_DehorsVetrato", "Molo_DehorsVetrato", 0.0, 0.0, 0.0, 0.0)]
    # spartitraffico con fiori: X 9,05-13,8 e da 16,7 fino a 116,45 (Y 131,5 sul piano in pietra)
    xs = [9.05] + [16.7 + SPART_L * k for k in range(21)]
    for k, x in enumerate(xs):
        R.append(("SM_Viale_Spartitraffico_Fiori", f"Spartitraffico_Fiori_{k:02d}", x, 131.5, 0.0, 0.0))
    # semafori: sullo spartitraffico prima delle strisce (carreggiata A), sul marciapiede lato citta' (carreggiata B),
    # sul marciapiede dell'angolo (ripetitore verso -X per chi arriva sulla carreggiata A)
    R += [("SM_Morin_Semaforo", "Semaforo_00", 13.55, 131.5, 0.15, 0.0),
          ("SM_Morin_Semaforo", "Semaforo_01", 17.0, 139.1, 0.15, 180.0),
          ("SM_Morin_Semaforo", "Semaforo_02", 13.2, 120.45, 0.15, 0.0),
          ("SM_Morin_Semaforo", "Semaforo_03", 16.95, 131.5, 0.15, 180.0)]
    # cartelli sullo spartitraffico di fronte allo sbocco della strada del molo, rivolti verso -Y (yaw 90)
    R += [("SM_Morin_CartelloPrecedenza", "Cartello_Precedenza_00", 12.6, 131.35, 0.15, 90.0),
          ("SM_Morin_CartelloObbligoDestra", "Cartello_ObbligoDestra_00", 11.9, 131.35, 0.15, 90.0),
          ("SM_Morin_CartelloP", "Cartello_P_Incrocio_00", -1.2, 120.55, Z_MOLO, 90.0),
          ("SM_Morin_CartelloP", "Cartello_P_Incrocio_01", 3.4, 120.55, Z_MOLO, 90.0)]
    # dissuasori: lungo il bordo dei masselli verso il viale (Y 118,6) e sul ciglio della strada del molo (X 6,2)
    k = 0
    for x in np.arange(-3.2, 5.0, 2.05):
        R.append(("SM_Morin_Dissuasore", f"Dissuasore_{k:02d}", float(x), 118.6, Z_MOLO, 0.0)); k += 1
    for y in (118.6, 116.4, 114.2, 112.0):
        R.append(("SM_Morin_Dissuasore", f"Dissuasore_{k:02d}", 6.15, y, Z_MOLO, 0.0)); k += 1
    # scooter sui masselli fra i dissuasori e il viale, perpendicolari al viale (muso verso +Y)
    for i, x in enumerate((-6.9, -6.0, -5.1, -3.9, 0.2, 1.1)):
        R.append(("SM_Morin_Scooter", f"Scooter_{i:02d}", x + rng.uniform(-0.1, 0.1), 119.85 + rng.uniform(-0.1, 0.1),
                  Z_MOLO, 90.0 + rng.uniform(-8, 8)))
    # fondale oltre il viale: edificio con vetrate (area OSM 205843492, X 23-95, Y 149-191) e platani dei Giardini pubblici
    R.append(("SM_Fondale_EdificioVetrate", "Fondale_EdificioVetrate_00", 46.0, 151.0, 0.0, 0.0))
    for i, (x, y) in enumerate(((-22.0, 150.5), (-9.0, 152.0), (4.0, 149.5), (19.5, 148.0), (-15.0, 166.0), (8.0, 168.0),
                                (72.0, 147.5), (92.0, 148.5), (106.0, 149.0))):
        a = "SM_Albero_LatifogliaA" if i % 2 == 0 else "SM_Albero_LatifogliaB"
        R.append((a, f"GiardiniPubblici_Platano_{i:02d}", x + rng.uniform(-1, 1), y + rng.uniform(-1, 1), 0.0, float(rng.uniform(0, 360))))
    return R


def write_incrocio_csv(rows, path="exports/incrocio/incrocio_posizioni_v1.csv"):
    os.makedirs(os.path.dirname(f"{PROJ}/{path}"), exist_ok=True)
    out = ["asset,nome,x,y,z,yaw,pitch,roll"] + [_row_ue(*r) for r in rows]
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    return len(out) - 1


def viale_csv_v4(src="exports/viale/viale_posizioni_v3.csv", dst="exports/viale/viale_posizioni_v4.csv"):
    """v3 con: modulo SO_00 -> SM_Viale_Italia_Incrocio; nuovo modulo SO_m1 (X -16..3, il viale verso SO in foto);
    tolte le auto in sosta sull'imbocco della strada del molo e sulle strisce."""
    import morin_viale as mv
    with open(f"{PROJ}/{src}", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    head, body = rows[0], rows[1:]
    out, removed = [], []
    for r in body:
        a, n = r[0], r[1]
        if n == "Viale_Strada_SO_00":
            r = ["SM_Viale_Italia_Incrocio"] + r[1:]
        if a.startswith("SM_Morin_Auto_"):
            x = float(r[2]) / 100
            Lh = 2.3
            if (X_ZEBRA_V[0] - 2.0 < x + Lh and x - Lh < X_ZEBRA_V[1] + 1.8) or (X_MOUTH[0] - 1.0 < x + Lh and x - Lh < X_MOUTH[1] + 1.0
                                                                                 and -float(r[3]) / 100 < 125):
                removed.append(n)
                continue
        out.append(r)
    out.append(["SM_Viale_Italia_Strada", "Viale_Strada_SO_m1", "-1600.0", "-12085.0", "0.0", "0.0"])
    with open(f"{PROJ}/{dst}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(",".join(r) for r in [head] + out) + "\n")
    return removed


AUTO_L = {"A": 3.95, "B": 4.35, "C": 4.45}
AUTO_W = {"A": 1.74, "B": 1.82, "C": 1.76}


def parcheggio_csv_v3(src="exports/parcheggio/parcheggio_posizioni_v2.csv", dst="exports/parcheggio/parcheggio_posizioni_v3.csv",
                      seed=20261124):
    """v2 con: asfalto -> SM_Parcheggio_Asfalto_v2; fila in linea lato citta' (Y ~112,3) -> fila a pettine a 60 gradi;
    pini nell'aiuola ristretta (Y 116,35); cartello P_01 sull'aiuola nuova."""
    with open(f"{PROJ}/{src}", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    head, body = rows[0], rows[1:]
    rng = np.random.default_rng(seed)
    out, ctx, removed = [], [], []
    city_cars = []
    for r in body:
        a, n = r[0], r[1]
        y = -float(r[3]) / 100
        if n == "Parcheggio_Asfalto":
            r = ["SM_Parcheggio_Asfalto_v2"] + r[1:]
        elif a.startswith("SM_Morin_Auto_") and 111.0 < y < 113.5:
            city_cars.append(a)
            removed.append(n)
            continue
        elif a == "SM_Morin_PinoDomestico":
            r = r[:3] + [_ue(-(Y_PINI_V3 + (y - 115.2) * 0.4) * 100)] + r[4:]
        elif n == "Cartello_P_01":
            r = r[:3] + [_ue(-(Y_AIU_V3[0] + Y_AIU_V3[1]) / 2 * 100)] + r[4:]
        out.append(r)
    # fila a pettine: stalli da 2,5 m a 60 gradi, muso verso l'aiuola dei pini; ~15 % di posti liberi
    xs, d, pitch = _pettine_stalls()
    a = math.radians(PETT_ANG)
    pool = city_cars + city_cars
    k = 0
    for i, x in enumerate(xs):
        if rng.uniform() < 0.15:
            continue
        asset = pool[int(rng.integers(0, len(pool)))]
        m = asset.split("_")[3]
        Lc, Wc = AUTO_L[m], AUTO_W[m]
        half_dy = Lc / 2 * math.sin(a) + Wc / 2 * math.cos(a)
        cy = Y_PETT_C[1] - 0.08 - half_dy
        cx = x + pitch / 2 + (cy - Y_PETT_C[0]) / math.tan(a) + rng.uniform(-0.08, 0.08)
        yaw = PETT_ANG + rng.uniform(-1.5, 1.5)
        out.append(_row_ue(asset, f"ParkAuto_Pettine_{k:02d}", cx, cy, mp.Z_ASF, yaw).split(","))
        k += 1
    with open(f"{PROJ}/{dst}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(",".join(r) for r in [head] + out) + "\n")
    return removed, k


def write_all_csv():
    rows = layout_incrocio()
    n = write_incrocio_csv(rows)
    rem_v = viale_csv_v4()
    rem_p, k = parcheggio_csv_v3()
    print("incrocio", n, "viale v4 auto tolte", rem_v, "parcheggio: tolte", len(rem_p), "pettine", k)
    return rows


# =============================================================================================================
# contesto per il render (istanze CTXI_ lette dai CSV nuovi; le istanze sostituite vengono nascoste, non cancellate)
# =============================================================================================================
def _mesh_for(a):
    o = bpy.data.objects.get(a)
    if o is not None and o.type == "MESH":
        return o.data
    return bpy.data.meshes.get(a)


def _inst(coll, nm, a, x, y, z, yaw, pitch=0.0):
    me = _mesh_for(a)
    if me is None:
        print("manca la mesh", a)
        return None
    o = bpy.data.objects.get(nm)
    if o is None:
        o = bpy.data.objects.new(nm, me)
        coll.objects.link(o)
    o.data = me
    o.hide_render = o.hide_viewport = False
    o.matrix_world = (Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
                      @ Matrix.Rotation(math.radians(pitch), 4, "Y"))
    return o


def _read_ue_csv(path):
    with open(f"{PROJ}/{path}", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    out = []
    for r in rows[1:]:
        p = float(r[6]) if len(r) > 6 else 0.0
        out.append((r[0], r[1], float(r[2]) / 100, -float(r[3]) / 100, float(r[4]) / 100, -float(r[5]), -p))
    return out


def link_molo_edifici():
    """Edifici del molo (A1A2, A3) e lampione a due globi dal file del molo, collegati (link) per il render."""
    need = ["SM_Molo_Edificio_A1A2", "SM_Molo_Edificio_A3", "SM_Molo_Lampione2Globi", "SM_Molo_Tendone"]
    path = PROJ + "/blender/arte_molo.blend"
    miss = [n for n in need if n not in bpy.data.objects]
    if miss:
        with bpy.data.libraries.load(path, link=True) as (src, dst):
            dst.objects = [n for n in src.objects if n in miss]
    coll = pk._coll("INCR_Molo_Link")
    for n in need:
        o = bpy.data.objects.get(n)
        if o is not None and o.name not in coll.objects:
            coll.objects.link(o)
    lamp = bpy.data.objects.get("SM_Molo_Lampione2Globi")
    if lamp is not None:
        coll.objects.unlink(lamp)
        _inst(coll, "CTXI_Lampione2Globi_00", "SM_Molo_Lampione2Globi", 13.0, 106.0, 0.15, 0.0)
    t = bpy.data.objects.get("SM_Molo_Tendone")
    if t is not None:
        t.hide_render = True          # sostituito dal dehors vetrato
    return [n for n in need if n in bpy.data.objects]


def build_context():
    coll = pk._coll("INCR_Contesto")
    link_molo_edifici()
    for path, pre in (("exports/incrocio/incrocio_posizioni_v1.csv", "CTXI_"), ("exports/parcheggio/parcheggio_posizioni_v3.csv", "CTXI_P_")):
        for a, n, x, y, z, yaw, pitch in _read_ue_csv(path):
            if pre == "CTXI_P_" and not (n.startswith("ParkAuto_Pettine") or "Pino" in n or n == "Cartello_P_01" or n == "Parcheggio_Asfalto"):
                continue
            _inst(coll, pre + n, a, x, y, z, yaw, pitch)
    # incrocio al posto del modulo SO_00, nuovo modulo SO_m1
    _inst(coll, "CTXI_Viale_Strada_SO_00", "SM_Viale_Italia_Incrocio", 3.0, 120.85, 0.0, 0.0)
    _inst(coll, "CTXI_Viale_Strada_SO_m1", "SM_Viale_Italia_Strada", -16.0, 120.85, 0.0, 0.0)
    # sostituiti: nascosti, non cancellati
    hide = ["CTXV_Viale_Strada_SO_00", "CTXP_Parcheggio_Asfalto", "SM_Parcheggio_Asfalto", "CTXP_Cartello_P_01"]
    removed_viale = viale_removed_names()
    hide += ["CTXV_" + n for n in removed_viale]
    for o in bpy.data.objects:
        if o.name in hide or o.name.startswith("CTXP_Parcheggio_Pino_"):
            o.hide_render = o.hide_viewport = True
        if o.name.startswith("CTXP_ParkAuto_"):
            y = o.location.y
            if 111.0 < y < 113.5:
                o.hide_render = o.hide_viewport = True
    for nm in LODDED + SINGLE + SINGLE_PARK:
        for l in (0, 1, 2):
            o = bpy.data.objects.get(nm + _sfx(l))
            if o is not None:
                o.hide_render = o.hide_viewport = True
    for o in bpy.data.collections[KIT].objects:
        if o.name.startswith("UCX_"):
            o.hide_render = True
    return coll


def viale_removed_names():
    with open(f"{PROJ}/exports/viale/viale_posizioni_v3.csv", encoding="utf-8") as fh:
        a = {r[1] for r in csv.reader(fh)}
    with open(f"{PROJ}/exports/viale/viale_posizioni_v4.csv", encoding="utf-8") as fh:
        b = {r[1] for r in csv.reader(fh)}
    return sorted(a - b)


# =============================================================================================================
# export
# =============================================================================================================
def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    objs = bpy.data.collections[KIT].objects
    state = {o.name: (o.hide_viewport, o.hide_get(), o.hide_render) for o in objs}
    for o in objs:
        o.hide_viewport = False
        o.hide_set(False)
    bpy.context.view_layer.update()
    reps = []
    try:
        for nm in SINGLE:
            reps.append(morin_export.export_fbx([bpy.data.objects[nm]], f"{EXPDIR}/{nm}.fbx", mode="asset",
                                                overwrite=overwrite, include_ucx=True, verbose=False))
        for nm in SINGLE_PARK:
            reps.append(morin_export.export_fbx([bpy.data.objects[nm]], f"{EXPDIR_PARK}/{nm}.fbx", mode="asset",
                                                overwrite=overwrite, include_ucx=True, verbose=False))
        for nm in LODDED:
            for lod in (0, 1, 2):
                on = nm + _sfx(lod)
                reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                                    overwrite=overwrite, include_ucx=(lod == 0), bake_rotation=(lod > 0),
                                                    verbose=False))
    finally:
        for n, (hv, hg, hr) in state.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
                o.hide_render = hr
    return reps


# =============================================================================================================
# camere e confronti (foto sopra, render sotto)
# =============================================================================================================
CAMS = {
    # nome: (posizione, azimut di progetto (gradi da +Y verso +X), pitch, FOV orizzontale, risoluzione, shift_y)
    "CAM_Incrocio_F1": ((8.0, 118.0, 2.7), -32.0, 0.0, 150.0, (1903, 530), 0.028),
    "CAM_Park_F1_v3": ((21.5, 106.6, mp.Z_ASF + 2.1), 82.0, -6.0, 78.0, (1375, 783), 0.0),
}


def cameras():
    coll = pk._coll("INCR_Camere")
    for name, (pos, az, pitch, fov, res, sh) in CAMS.items():
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
        cam.data.shift_y = sh
        cam.data.clip_start = 0.1
        cam.data.clip_end = 6000
        cam["res"] = res
    return list(CAMS)


def render_confronto(cam, foto, out, width):
    tmp = os.path.join(os.environ.get("TEMP", PROJ), f"morin_incrocio_{cam}.png")
    mm.render(cam, tmp, width=width)
    a = tp.load(foto)[..., :3]
    b = tp.load(tmp)[..., :3]
    if b.shape[1] != a.shape[1]:
        b = tp.resize(b, a.shape[1], int(round(b.shape[0] * a.shape[1] / b.shape[1])))
    sep = np.ones((6, a.shape[1], 3), np.float32)
    tp.save(np.concatenate([a, sep, b], 0), f"{PROJ}/{out}")
    return out


def render_confronti():
    return [render_confronto("CAM_Incrocio_F1", FOTO, "docs/qa/arte_incrocio_v1_confronto.png", 1903),
            render_confronto("CAM_Park_F1_v3", FOTO_PARK, "docs/qa/arte_parcheggio_v3_confronto.png", 1375)]
