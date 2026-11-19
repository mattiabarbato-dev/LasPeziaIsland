"""morin_chiosco.py — chiosco-bar della passeggiata con il dehors (v1, 2026-11-19).

Scheda: ref/zona_parcheggio_chiosco.md (§3 chiosco, §2 pavimento), ref/elementi.md (chiosco X ~100, Y ~106 [V] OSM 4512137289).
Foto: ref/foto/vista/chiosco_con_ombrelloni_e_tavolini(_2).png (catture Street View, deroga [SV] di CLAUDE.md §5: dalle foto
solo i colori campionati; texture procedurali, niente UI, persone, targhe; insegna con nome inventato "Chiosco del Golfo").

Esegui dentro blender/arte_chiosco.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_chiosco as mc; importlib.reload(mc)
    mc.make_textures()      # blender/textures/chiosco/ (D sRGB, N DirectX, ORM), 2048
    mc.build_materials()    # M_Morin_Chiosco, M_Morin_Dehors (+ M_Pav_Cubetti, M_Albero_Latifoglia_Chioma riusati)
    mc.build_all()          # mesh LOD0/1/2 + UCX nella collezione CHIOSCO_Kit (riscrive le mesh omonime)
    rows = mc.layout()      # posizioni (coordinate Blender)
    mc.write_csv(rows)      # exports/chiosco/chiosco_posizioni_v1.csv
    mc.build_context(rows)  # istanze per il render (CHIOSCO_Contesto)
    mc.export_all()         # FBX in exports/chiosco/ (LOD1/LOD2 con bake_rotation=True)

Assi: chiosco con il bancone verso -Y (mare, passeggiata), insegna sul lato -X (verso il ponte).
Tutti i prop hanno origine alla base e si posano a quota cubetti Z +0,15 (pk.ZF). SM_Pav_Chiosco e' in coordinate di
progetto (origine 0,0,0) e si posa in (0,0,0) come gli altri pezzi Pav.
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
TEXDIR = PROJ + "/blender/textures/chiosco"
KIT = "CHIOSCO_Kit"
EXPDIR = "//../exports/chiosco"
ZF = pk.ZF                      # 0,15 quota cubetti
S = 2048
NOME = "Chiosco del Golfo"      # inventato (CLAUDE.md §5)

# colori sRGB 0-255 campionati dalle foto [SV] (mediane, corrette per ombra/sole) e stimati
CREMA = (222, 203, 170)        # corpo al sole: 217,185,152 (foto 1, lato -X); in ombra 124,122,123
BIANCO = (236, 236, 232)       # tettoia e mantovana
TELA = (234, 230, 222)         # ombrelloni (foto 2: 182,174,172 sopra in controluce)
FIBRA = (60, 57, 59)           # fioriere (foto 2: 46,45,52 / 56,49,49)

# regioni degli atlanti (u0, v0, u1, v1)
RC = {"front": (0.0, 0.5, 0.5, 1.0), "back": (0.5, 0.5, 1.0, 1.0), "white": (0.0, 0.25, 0.5, 0.5),
      "steel": (0.5, 0.25, 0.75, 0.5), "counter": (0.75, 0.25, 1.0, 0.5), "sign": (0.0, 0.0, 0.25, 0.25),
      "crema": (0.25, 0.0, 0.5, 0.25), "dark": (0.5, 0.0, 0.75, 0.25)}
RD = {"canvas": (0.0, 0.5, 0.5, 1.0), "fiber": (0.5, 0.75, 1.0, 1.0), "rattan": (0.0, 0.0, 0.5, 0.5),
      "metal": (0.5, 0.5, 0.75, 0.75), "top": (0.75, 0.5, 1.0, 0.75), "wood": (0.5, 0.25, 0.75, 0.5),
      "soil": (0.75, 0.25, 1.0, 0.5), "steel": (0.5, 0.0, 0.75, 0.25)}
REGKEYS = sorted(set(RC) | set(RD))

# chiosco: misure [S] dalle foto (camera stimata, vedi CAM)
CH_HW = 2.0                     # meta' lato corpo (4 x 4 m)
CH_H = 2.6                      # altezza corpo
Z_BANCO, Z_VETRO0, Z_VETRO1 = 1.05, 1.11, 2.30
REC = 0.05                      # rientro della vetrina
BANCO_P = 0.32                  # sporgenza del bancone
EAVE = (-2.7, 2.7, -2.95, 2.7)  # gronda (x0, x1, y0, y1): sporge 0,95 m sul bancone
Z_MANT0, Z_EAVE, Z_TOP = 2.42, 2.72, 3.12
TOP_IN = 0.9                    # rientro del colmo piatto
OMB = 2.0                       # meta' lato ombrellone (4 x 4 m)


# =============================================================================================================
# texture
# =============================================================================================================
def _c(c):
    return np.asarray(c, np.float32) / 255.0


def _px(r):
    u0, v0, u1, v1 = r
    return int((1 - v1) * S), int((1 - v0) * S), int(u0 * S), int(u1 * S)


class Atlas:
    def __init__(self):
        self.D = np.zeros((S, S, 3), np.float32)
        self.H = np.zeros((S, S), np.float32)
        self.R = np.full((S, S), 0.6, np.float32)
        self.M = np.zeros((S, S), np.float32)

    def fill(self, r, col, rough, metal=0.0, seed=0, var=0.04, sigma=3.0, h=None):
        y0, y1, x0, x1 = _px(r)
        hh, ww = y1 - y0, x1 - x0
        n = mm._noise(hh, ww, sigma, seed) * var + mm._noise(hh, ww, sigma * 12, seed + 1) * var
        self.D[y0:y1, x0:x1] = _c(col)[None, None, :] * (1 + n)[..., None]
        self.R[y0:y1, x0:x1] = rough + n * 0.5
        self.M[y0:y1, x0:x1] = metal
        if h is not None:
            self.H[y0:y1, x0:x1] = h(hh, ww)
        return y0, y1, x0, x1

    def save(self, base, nstr=2.0):
        self.H = self.H.astype(np.float32)
        nrm, ao = mm._normal_ao(self.H, nstr)
        os.makedirs(TEXDIR, exist_ok=True)
        tp.save(np.clip(self.D, 0, 1), f"{TEXDIR}/{base}_D.png")
        tp.save(nrm, f"{TEXDIR}/{base}_N.png")
        tp.save(mm._orm(ao, np.clip(self.R, 0.04, 1), self.M), f"{TEXDIR}/{base}_ORM.png")


def _facade(A, r, seed, back=False):
    """Facciata 4 m x 2,6 m nella regione r: zoccolo, pannelli crema, vetrina (o porta sul retro), fascia."""
    y0, y1, x0, x1 = A.fill(r, CREMA, 0.75, seed=seed, var=0.025)
    hh, ww = y1 - y0, x1 - x0
    ux = (np.arange(ww) + 0.5) / ww * 4.0
    z = (hh - 1 - np.arange(hh) + 0.5) / hh * CH_H
    U, Z = np.meshgrid(ux, z)
    D = A.D[y0:y1, x0:x1]
    H = A.H[y0:y1, x0:x1]
    R = A.R[y0:y1, x0:x1]
    rng = np.random.default_rng(seed)
    # sporco in basso e sotto la fascia, zoccolo
    D *= (1 - 0.22 * np.exp(-Z / 0.18))[..., None]
    D *= (1 - 0.10 * np.exp(-(CH_H - Z) / 0.08))[..., None]
    zoc = Z < 0.12
    D[zoc] = _c((150, 141, 126)) * (1 + 0.05 * mm._noise(hh, ww, 2, seed + 3)[zoc])[:, None]
    H[zoc] += 0.4
    # fughe dei pannelli (verticali ogni metro sotto il bancone, orizzontale a z 0,12 e 2,3)
    pw = 4.0 / ww * 1.5
    seam = ((np.abs(U - np.round(U)) < pw) & (Z < Z_BANCO)) | (np.abs(Z - 0.12) < 0.006) | (np.abs(Z - Z_VETRO1) < 0.006)
    D[seam] *= 0.72
    H[seam] -= 0.6
    if back:
        door = (np.abs(U - 2.0) < 0.5) & (Z < 2.1)
        D[door] = _c((128, 134, 128))
        R[door] = 0.45
        fr = door & ((np.abs(np.abs(U - 2.0) - 0.5) < 0.02) | (np.abs(Z - 2.1) < 0.02))
        D[fr] = _c((90, 92, 90))
        slat = door & (Z > 0.15) & (Z < 0.5) & (np.mod(Z, 0.04) < 0.018) & (np.abs(U - 2.0) < 0.38)
        D[slat] *= 0.6
        H[slat] -= 0.5
        han = (np.abs(U - 2.38) < 0.012) & (np.abs(Z - 1.05) < 0.1)
        D[han] = _c((190, 190, 190))
        win = (np.abs(U - 3.3) < 0.3) & (np.abs(Z - 1.7) < 0.3)
        D[win] = _c((150, 160, 165)) * (1 + 0.03 * mm._noise(hh, ww, 6, seed)[win])[:, None]
        R[win] = 0.15
        wfr = win & ((np.abs(np.abs(U - 3.3) - 0.3) < 0.025) | (np.abs(np.abs(Z - 1.7) - 0.3) < 0.025))
        D[wfr] = _c((205, 200, 190))
        H[win & ~wfr] -= 0.5
        return
    # vetrina
    v = (Z > Z_VETRO0) & (Z < Z_VETRO1) & (U > 0.16) & (U < 3.84)
    zz = (Z - Z_VETRO0) / (Z_VETRO1 - Z_VETRO0)
    inside = _c((52, 40, 33))[None, None, :] * (0.7 + 0.8 * zz)[..., None]
    D[v] = inside[v]
    R[v] = 0.06
    H[v] -= 0.3
    # mensole con bottiglie
    for zs in (1.45, 1.86):   # v2: due mensole, meno bottiglie, piu fondo
        sh = v & (np.abs(Z - zs) < 0.012)
        D[sh] = _c((176, 170, 160))
        u = 0.2
        while u < 3.76:
            w = rng.uniform(0.045, 0.08)
            hgt = rng.uniform(0.15, 0.26)
            if rng.random() < 0.3 and abs(u - 4 / 3) > 0.1 and abs(u - 8 / 3) > 0.1:
                col = _c([(38, 92, 52), (150, 85, 25), (175, 185, 175), (120, 30, 35), (60, 60, 120), (210, 190, 90)]
                         [rng.integers(0, 6)])
                neck = hgt * 0.35
                b = v & (Z > zs + 0.012) & (Z < zs + hgt) & (np.abs(U - u - w / 2) < w / 2)
                b &= (Z < zs + hgt - neck) | (np.abs(U - u - w / 2) < w * 0.18)
                D[b] = col[None, :] * (0.8 + 0.6 * (np.abs(U[b] - u - w * 0.3) < w * 0.12))[:, None]
                lab = b & (np.abs(Z - zs - hgt * 0.35) < hgt * 0.12)
                D[lab] = _c((225, 215, 195)) * rng.uniform(0.8, 1.0)
            u += w + rng.uniform(0.02, 0.06)
    # insegna-menu luminosa in alto (lilla, come in foto) con righe di testo astratte
    mb = v & (Z > 2.12) & (Z < 2.25)
    D[mb] = _c((226, 186, 220))
    txt = mb & (np.abs(np.mod(Z - 2.12, 0.04) - 0.02) < 0.005) & (np.mod(U * 7.3 + np.floor(Z * 25) * 0.37, 1.0) < 0.7)
    D[txt] = _c((120, 70, 110))
    # riflesso del cielo sul vetro
    refl = 0.5 + 0.5 * np.sin((U + Z * 0.9) * 2.4)
    D[v] = D[v] * 0.85 + _c((150, 165, 180))[None, :] * (0.18 * refl[v])[:, None]
    # telaio della vetrina
    fr = (Z > Z_VETRO0 - 0.01) & (Z < Z_VETRO1) & ~((Z > Z_VETRO0 + 0.03) & (Z < Z_VETRO1 - 0.03) & (U > 0.19) & (U < 3.81))
    D[fr] = _c((205, 200, 190))
    R[fr] = 0.4


def make_tex_chiosco():
    A = Atlas()
    _facade(A, RC["front"], 11)
    _facade(A, RC["back"], 12, back=True)
    A.fill(RC["white"], BIANCO, 0.55, seed=13, var=0.015)
    y0, y1, x0, x1 = _px(RC["white"])
    A.D[y0:y1, x0:x1] *= (1 + 0.02 * mm._noise(1, x1 - x0, 1.5, 5))[..., None]   # striature verticali
    A.fill(RC["steel"], (168, 170, 172), 0.32, metal=0.9, seed=14, var=0.02, sigma=1.0)
    A.fill(RC["counter"], (208, 205, 198), 0.35, seed=15, var=0.05, sigma=1.0)
    A.fill(RC["sign"], (246, 246, 243), 0.3, seed=16, var=0.01)
    A.fill(RC["crema"], CREMA, 0.75, seed=17, var=0.025)
    A.fill(RC["dark"], (60, 62, 65), 0.5, metal=0.6, seed=18, var=0.02)
    A.save("T_Morin_Chiosco")


def make_tex_dehors():
    A = Atlas()

    def weave(p):
        return lambda hh, ww: 0.25 * (np.sin(np.arange(hh)[:, None] * 2 * np.pi / p) * np.sin(np.arange(ww)[None, :] * 2 * np.pi / p))

    A.fill(RD["canvas"], TELA, 0.85, seed=21, var=0.02, h=weave(4))

    def basket(hh, ww):
        y, x = np.mgrid[0:hh, 0:ww]
        cell = 24
        c = ((x // cell) + (y // cell)) % 2
        s1 = np.abs(np.sin(np.pi * (y % cell) / cell))
        s2 = np.abs(np.sin(np.pi * (x % cell) / cell))
        return np.where(c == 0, s1, s2) * 0.8
    y0, y1, x0, x1 = A.fill(RD["rattan"], (128, 94, 60), 0.7, seed=22, var=0.06, h=basket)
    A.D[y0:y1, x0:x1] *= (0.7 + 0.35 * A.H[y0:y1, x0:x1])[..., None]
    A.fill(RD["fiber"], FIBRA, 0.8, seed=23, var=0.07, sigma=1.5, h=lambda hh, ww: 0.15 * mm._noise(hh, ww, 2, 9))
    A.fill(RD["metal"], (55, 57, 60), 0.45, metal=0.7, seed=24, var=0.02)
    A.fill(RD["top"], (232, 230, 225), 0.4, seed=25, var=0.015)
    y0, y1, x0, x1 = A.fill(RD["wood"], (150, 104, 64), 0.6, seed=26, var=0.03)
    A.D[y0:y1, x0:x1] *= (1 + 0.12 * tp.blur(mm._noise(y1 - y0, 1, 1, 4), 1)).repeat(x1 - x0, 1)[..., None]
    A.fill(RD["soil"], (58, 42, 31), 0.95, seed=27, var=0.12, sigma=1.2, h=lambda hh, ww: 0.4 * mm._noise(hh, ww, 1.5, 8))
    A.fill(RD["steel"], (170, 172, 175), 0.3, metal=0.9, seed=28, var=0.02)
    A.save("T_Morin_Dehors", nstr=1.5)


def make_textures():
    make_tex_chiosco()
    make_tex_dehors()
    return sorted(os.listdir(TEXDIR))


def build_materials():
    t = TEXDIR + "/"
    for m, base in (("M_Morin_Chiosco", "T_Morin_Chiosco"), ("M_Morin_Dehors", "T_Morin_Dehors")):
        pk._pbr_material(m, t + base + "_D.png", t + base + "_N.png", t + base + "_ORM.png")
    if "M_Pav_Cubetti" not in bpy.data.materials:
        c = pk.TEXDIR + "/T_Pav_Cubetti"
        pk._pbr_material("M_Pav_Cubetti", c + "_D.png", c + "_N.png", c + "_ORM.png")
    if "M_Albero_Latifoglia_Chioma" not in bpy.data.materials:
        tm = PROJ + "/blender/textures/molo/T_Albero_Latifoglia_Chioma"
        pk._pbr_material("M_Albero_Latifoglia_Chioma", tm + "_D.png", tm + "_N.png", tm + "_ORM.png", alpha=True)
    if not any(m.name == "M_Morin_PinoDomestico_Chioma" and m.library is None for m in bpy.data.materials):
        tm = PROJ + "/blender/textures/molo/T_Morin_PinoDomestico_Chioma"
        pk._pbr_material("M_Morin_PinoDomestico_Chioma", tm + "_D.png", tm + "_N.png", tm + "_ORM.png", alpha=True)
    return True


# =============================================================================================================
# utilita' geometriche
# =============================================================================================================
def _reg_layer(bm):
    _uvl(bm)
    return bm.faces.layers.int.get("reg") or bm.faces.layers.int.new("reg")


def _uvl(bm):
    """Layer UV unico "UVMap" (bmesh verify() in Blender 5 crea "Float2", e il testo porta un suo "UVMap")."""
    return bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")


def _clean_attrs(o):
    me = o.data
    a = me.attributes.get("reg")
    if a is not None:
        me.attributes.remove(a)
    for l in [l for l in me.uv_layers if l.name != "UVMap"]:
        me.uv_layers.remove(l)
    if me.uv_layers:
        me.uv_layers["UVMap"].active = True
        me.uv_layers["UVMap"].active_render = True


def _tag(faces, bm, key):
    lay = _reg_layer(bm)
    for f in faces:
        f[lay] = REGKEYS.index(key) + 1
    return faces


def _uv_regions(bm, regions, scale=1.0, margin=0.03):
    """Facce con tag 'reg' > 0: proiezione a box (asse dominante) dentro la regione dell'atlante, senza ripetizione."""
    lay = _reg_layer(bm)
    uvl = _uvl(bm)
    for f in bm.faces:
        k = f[lay]
        if k <= 0:
            continue
        u0, v0, u1, v1 = regions[REGKEYS[k - 1]]
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        cs = [(lp.vert.co[a], lp.vert.co[b]) for lp in f.loops]
        mx, my = min(c[0] for c in cs), min(c[1] for c in cs)
        ext = max(max(c[0] for c in cs) - mx, max(c[1] for c in cs) - my, scale)
        du, dv = (u1 - u0) * (1 - 2 * margin), (v1 - v0) * (1 - 2 * margin)
        for lp, (x, y) in zip(f.loops, cs):
            lp[uvl].uv = (u0 + (u1 - u0) * margin + (x - mx) / ext * du, v0 + (v1 - v0) * margin + (y - my) / ext * dv)


def _faces_since(bm, n0):
    bm.faces.ensure_lookup_table()
    return list(bm.faces)[n0:]


def _add(bm, key, fn, *a, **k):
    n0 = len(bm.faces)
    fn(bm, *a, **k)
    fs = _faces_since(bm, n0)
    _tag(fs, bm, key)
    return fs


def _tube(bm, pts, r, sides, M=Matrix()):
    pk._tube(bm, [tuple(M @ Vector(p)) for p in pts], r, sides)


def _write(name, bm, mats, coll, regions, scale=1.0):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    _uv_regions(bm, regions, scale)
    o = pk._finish(name, bm, mats, coll, uv=None)
    _clean_attrs(o)
    return o


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


# =============================================================================================================
# chiosco
# =============================================================================================================
def _side_frame(n):
    n = Vector(n)
    t = (-n).cross(Vector((0, 0, 1)))
    return n, t


def _wall_quad(bm, uvl, n, t, u0, u1, z0, z1, off, reg_rect, flip=False):
    """Quad verticale sul lato con normale n: u lungo t (0..4 m), z quota; UV nella regione facciata (4 x 2,6 m)."""
    P = lambda u, z: n * (CH_HW + off) + t * (u - CH_HW) + Vector((0, 0, z))
    pts = [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]
    if flip:
        pts = pts[::-1]
    f = bm.faces.new([bm.verts.new(P(u, z)) for u, z in pts])
    ru0, rv0, ru1, rv1 = reg_rect
    for lp, (u, z) in zip(f.loops, pts):
        lp[uvl].uv = (ru0 + (ru1 - ru0) * u / 4.0, rv0 + (rv1 - rv0) * z / CH_H)
    return f


def _reveal(bm, n, t, u0, u1, z0, z1, kind):
    """Facce del rientro della vetrina (dal filo muro a -REC)."""
    P = lambda u, z, o: tuple(n * (CH_HW + o) + t * (u - CH_HW) + Vector((0, 0, z)))
    if kind == "bot":
        vs = [P(u0, z0, 0), P(u1, z0, 0), P(u1, z0, -REC), P(u0, z0, -REC)]
    elif kind == "top":
        vs = [P(u0, z1, -REC), P(u1, z1, -REC), P(u1, z1, 0), P(u0, z1, 0)]
    elif kind == "left":
        vs = [P(u0, z0, 0), P(u0, z0, -REC), P(u0, z1, -REC), P(u0, z1, 0)]
    else:
        vs = [P(u1, z1, 0), P(u1, z1, -REC), P(u1, z0, -REC), P(u1, z0, 0)]
    return bm.faces.new([bm.verts.new(v) for v in vs])


def _text_bm(lod):
    """Mesh dell'insegna: testo estruso (font interno di Blender), letto da chi guarda verso +X dal lato -X."""
    cu = bpy.data.curves.new("_tmp_insegna", "FONT")
    cu.body = NOME
    cu.align_x = "CENTER"
    cu.extrude = 0.025
    cu.resolution_u = (3, 1, 1)[lod]
    cu.offset = 0.0
    ob = bpy.data.objects.new("_tmp_insegna", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    tb = bmesh.new()
    tb.from_mesh(me)
    ev.to_mesh_clear()
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    xs = [v.co.x for v in tb.verts]
    w = max(xs) - min(xs)
    s = 4.0 / w
    zmin = min(v.co.y for v in tb.verts)
    # piano XY del font -> verticale rivolto a -X, lettura verso -Y
    M = (Matrix.Translation((-1.76, 0, 3.26)) @ Matrix.Rotation(math.radians(-90), 4, "Z") @
         Matrix.Rotation(math.radians(90), 4, "X") @ Matrix.Scale(s, 4) @ Matrix.Translation((0, -zmin, 0)))
    bmesh.ops.transform(tb, matrix=M, verts=tb.verts)
    bmesh.ops.triangulate(tb, faces=tb.faces)
    return tb


def build_chiosco(coll, lod=0, name="SM_Morin_Chiosco"):
    bm = bmesh.new()
    lay = _reg_layer(bm)
    uvl = _uvl(bm)
    fr, bk = RC["front"], RC["back"]
    u_open0, u_open1 = 0.16, 3.84   # v2: montanti d'angolo crema piu larghi (foto C1)
    for n_ in ((0, -1, 0), (-1, 0, 0), (1, 0, 0)):
        n, t = _side_frame(n_)
        _wall_quad(bm, uvl, n, t, 0, 4, 0, Z_BANCO, 0, fr)
        _wall_quad(bm, uvl, n, t, 0, 4, Z_VETRO1, CH_H, 0, fr)
        _wall_quad(bm, uvl, n, t, 0, 4, Z_BANCO, Z_VETRO0, 0, fr)
        _wall_quad(bm, uvl, n, t, 0, u_open0, Z_VETRO0, Z_VETRO1, 0, fr)
        _wall_quad(bm, uvl, n, t, u_open1, 4, Z_VETRO0, Z_VETRO1, 0, fr)
        if lod < 2:
            _wall_quad(bm, uvl, n, t, u_open0, u_open1, Z_VETRO0, Z_VETRO1, -REC, fr)
            fs = [_reveal(bm, n, t, u_open0, u_open1, Z_VETRO0, Z_VETRO1, k) for k in ("bot", "top", "left", "right")]
            _tag(fs, bm, "crema")
        else:
            _wall_quad(bm, uvl, n, t, u_open0, u_open1, Z_VETRO0, Z_VETRO1, 0, fr)
        # montanti in acciaio
        if lod < 2:
            for um in (4 / 3, 8 / 3):
                c = n * (CH_HW - REC / 2 + 0.005) + t * (um - CH_HW)
                hw = t * 0.06 + n * (REC / 2 + 0.01)
                x0, x1 = sorted((c.x - abs(hw.x), c.x + abs(hw.x)))
                y0, y1 = sorted((c.y - abs(hw.y), c.y + abs(hw.y)))
                _add(bm, "crema", pk._box, x0, x1, y0, y1, Z_VETRO0, Z_VETRO1, faces=("xn", "xp", "yn", "yp"))
    n, t = _side_frame((0, 1, 0))
    _wall_quad(bm, uvl, n, t, 0, 4, 0, CH_H, 0, bk)
    # banconi: -Y prolungato oltre gli spigoli, -X e +X da filo a filo
    h = CH_HW
    for x0, x1, y0, y1 in ((-h - BANCO_P, h + BANCO_P, -h - BANCO_P, -h), (-h - BANCO_P, -h, -h, h), (h, h + BANCO_P, -h, h)):
        fs = _add(bm, "counter", pk._box, x0, x1, y0, y1, Z_BANCO, Z_VETRO0)
        for f in fs:
            if abs(f.normal.z) < 0.5:
                f[lay] = REGKEYS.index("steel") + 1
    # tettoia: intradosso, mantovana (doppia faccia), falde a padiglione e colmo piatto
    ex0, ex1, ey0, ey1 = EAVE
    _add(bm, "white", pk._quad, [(ex0, ey1, 2.62), (ex1, ey1, 2.62), (ex1, ey0, 2.62), (ex0, ey0, 2.62)])
    ring = [(ex0, ey0), (ex1, ey0), (ex1, ey1), (ex0, ey1)]
    for i in range(4):
        a, b = ring[i], ring[(i + 1) % 4]
        _add(bm, "white", pk._quad, [(a[0], a[1], Z_MANT0), (b[0], b[1], Z_MANT0), (b[0], b[1], Z_EAVE), (a[0], a[1], Z_EAVE)])
        if lod < 2:
            d = Vector((b[1] - a[1], -(b[0] - a[0]), 0)).normalized() * -0.012
            _add(bm, "white", pk._quad, [(b[0] + d.x, b[1] + d.y, Z_MANT0), (a[0] + d.x, a[1] + d.y, Z_MANT0),
                                         (a[0] + d.x, a[1] + d.y, Z_EAVE), (b[0] + d.x, b[1] + d.y, Z_EAVE)])
    top = [(ex0 + TOP_IN, ey0 + TOP_IN), (ex1 - TOP_IN, ey0 + TOP_IN), (ex1 - TOP_IN, ey1 - TOP_IN), (ex0 + TOP_IN, ey1 - TOP_IN)]
    for i in range(4):
        a, b, c, d = ring[i], ring[(i + 1) % 4], top[(i + 1) % 4], top[i]
        _add(bm, "white", pk._quad, [(a[0], a[1], Z_EAVE), (b[0], b[1], Z_EAVE), (c[0], c[1], Z_TOP), (d[0], d[1], Z_TOP)])
    _add(bm, "white", pk._quad, [(p[0], p[1], Z_TOP) for p in top])
    # insegna: barra di supporto + lettere in rilievo
    _add(bm, "dark", pk._box, -1.78, -1.66, -2.0, 2.0, Z_TOP, 3.26, faces=("top", "xn", "xp", "yn", "yp"))
    if lod < 2:
        tb = _text_bm(lod)
        zt = max(v.co.z for v in tb.verts)
        # pannello scuro fra le due scritte (cosi' da ogni lato si legge una sola scritta)
        _add(bm, "dark", pk._box, -1.735, -1.705, -2.05, 2.05, 3.26, zt + 0.04)
        me = bpy.data.meshes.new("_tmp_txt")
        tb.to_mesh(me)
        tb.free()
        # due scritte schiena contro schiena: leggibili dal lato ponte (-X) e dal lato dehors (+X)
        for rot in (False, True):
            n0 = len(bm.faces)
            bm.from_mesh(me)
            fs = _faces_since(bm, n0)
            if rot:
                vs = list({v for f in fs for v in f.verts})
                bmesh.ops.transform(bm, matrix=Matrix.Translation((-1.72, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @
                                    Matrix.Translation((1.72, 0, 0)), verts=vs)
            _tag(fs, bm, "sign")
        bpy.data.meshes.remove(me)
    o = _write(name + _sfx(lod), bm, ["M_Morin_Chiosco"], coll, RC, scale=0.6)
    if lod == 0:
        pk._ucx(name, [(-h, h, -h, h, 0, CH_H), (ex0, ex1, ey0, ey1, Z_MANT0, Z_TOP),
                       (-h - BANCO_P, h + BANCO_P, -h - BANCO_P, -h, Z_BANCO, Z_VETRO0)], coll)
    return o


# =============================================================================================================
# prop del dehors
# =============================================================================================================
def _sgabello(bm, M, lod):
    sides = (12, 8, 6)[lod]
    _add(bm, "wood", pk._lathe, [(0, 0.71), (0.17, 0.71), (0.19, 0.735), (0.18, 0.76), (0, 0.76)], sides, M, cap_top=False)
    ls = (4, 4, 3)[lod]
    feet = [(0.21 * math.cos(a), 0.21 * math.sin(a)) for a in (math.pi / 4 + k * math.pi / 2 for k in range(4))]
    for fx, fy in feet:
        _add(bm, "metal", _tube, [(fx * 0.55, fy * 0.55, 0.71), (fx, fy, 0.0)], 0.012, ls, M)
    if lod < 2:
        ring = [(fx * (0.55 + 0.45 * (1 - 0.28 / 0.71)), fy * (0.55 + 0.45 * (1 - 0.28 / 0.71)), 0.28) for fx, fy in feet]
        for i in range(4):
            _add(bm, "metal", _tube, [ring[i], ring[(i + 1) % 4]], 0.009, ls, M)


def _tavolino(bm, M, lod):
    sides = (24, 14, 8)[lod]
    _add(bm, "top", pk._lathe, [(0, 0.715), (0.35, 0.715), (0.35, 0.75), (0, 0.75)], sides, M, cap_top=False)
    _add(bm, "metal", pk._lathe, [(0.03, 0.04), (0.03, 0.715)], max(sides // 3, 4), M, cap_top=False)
    _add(bm, "metal", pk._lathe, [(0, 0), (0.22, 0.0), (0.22, 0.015), (0.06, 0.04), (0, 0.045)], max(sides // 2, 6), M, cap_top=False)


def _sedia(bm, M, lod):
    """Sedia da bistro: chi siede guarda verso -Y; schienale verso +Y."""
    ls = (5, 4, 3)[lod]
    for sx in (-1, 1):
        _add(bm, "metal", _tube, [(sx * 0.19, -0.19, 0.0), (sx * 0.19, -0.19, 0.44)], 0.012, ls, M)
        _add(bm, "metal", _tube, [(sx * 0.19, 0.21, 0.0), (sx * 0.19, 0.19, 0.44), (sx * 0.19, 0.25, 0.88)], 0.012, ls, M)
    _add(bm, "rattan", pk._box, -0.215, 0.215, -0.22, 0.21, 0.43, 0.47, mat=M)
    R = Matrix.Translation((0, 0.22, 0.56)) @ Matrix.Rotation(math.radians(-8), 4, "X")
    _add(bm, "rattan", pk._box, -0.19, 0.19, -0.015, 0.015, 0.0, 0.30, mat=M @ R,
         faces=("top", "xn", "xp", "yn", "yp") if lod < 2 else ("top", "yn", "yp"))
    if lod == 0:
        _add(bm, "metal", _tube, [(-0.19, -0.19, 0.2), (0.19, -0.19, 0.2)], 0.008, 3, M)
        _add(bm, "metal", _tube, [(-0.19, 0.195, 0.2), (0.19, 0.195, 0.2)], 0.008, 3, M)


SET_SEDIE = [(0.0, 0.62, 4.0), (0.62, 0.0, -6.0), (0.0, -0.62, 3.0), (-0.62, 0.0, 5.0)]   # (x, y, disordine in gradi)


def build_prop(coll, kind, lod=0):
    names = {"sgabello": "SM_Morin_Sgabello", "tavolino": "SM_Morin_Tavolino", "sedia": "SM_Morin_Sedia",
             "set": "SM_Morin_TavoloSet"}
    name = names[kind]
    bm = bmesh.new()
    _reg_layer(bm)
    I = Matrix()
    if kind == "sgabello":
        _sgabello(bm, I, lod)
        ucx = [(-0.22, 0.22, -0.22, 0.22, 0, 0.76)]
    elif kind == "tavolino":
        _tavolino(bm, I, lod)
        ucx = [(-0.35, 0.35, -0.35, 0.35, 0, 0.75)]
    elif kind == "sedia":
        _sedia(bm, I, lod)
        ucx = [(-0.22, 0.22, -0.23, 0.27, 0, 0.88)]
    else:
        _tavolino(bm, I, lod)
        for x, y, jit in SET_SEDIE:
            # sedia rivolta verso il tavolo: lo schienale (+Y locale) sta lontano dal centro, piu' un piccolo disordine
            a = math.atan2(-x, y) + math.radians(jit)
            _sedia(bm, Matrix.Translation((x, y, 0)) @ Matrix.Rotation(a, 4, "Z"), lod)
        ucx = [(-0.95, 0.95, -0.95, 0.95, 0, 0.8)]
    o = _write(name + _sfx(lod), bm, ["M_Morin_Dehors"], coll, RD, scale=0.5)
    if lod == 0:
        pk._ucx(name, ucx, coll)
    return o


OMB_X, OMB_Y = 2.5, 2.0            # v2: tela 5 x 4 m (foto C2: tele grandi che coprono tutto il dehors)
Z_OMB_APEX, Z_OMB_EDGE = 2.92, 2.36  # v2: bordo tela basso (foto C2), mantovana fino a 2,16


def _canopy_z(x, y):
    d = max(abs(x) / OMB_X, abs(y) / OMB_Y)
    if d < 1e-6:
        return Z_OMB_APEX
    ax, ay = abs(x) / OMB_X, abs(y) / OMB_Y
    ridge = min(ax, ay) / max(ax, ay)
    return Z_OMB_APEX - (Z_OMB_APEX - Z_OMB_EDGE) * d - 0.10 * math.sin(math.pi * d) * (1 - ridge) ** 1.5


def build_ombrellone(coll, lod=0, name="SM_Morin_Ombrellone"):
    bm = bmesh.new()
    _reg_layer(bm)
    N = (12, 6, 4)[lod]
    g = [[None] * (N + 1) for _ in range(N + 1)]
    gb = [[None] * (N + 1) for _ in range(N + 1)]
    for i in range(N + 1):
        for j in range(N + 1):
            x, y = -OMB_X + 2 * OMB_X * i / N, -OMB_Y + 2 * OMB_Y * j / N
            z = _canopy_z(x, y)
            g[i][j] = bm.verts.new((x, y, z))
            gb[i][j] = bm.verts.new((x, y, z - 0.012))
    fs = []
    for i in range(N):
        for j in range(N):
            fs.append(bm.faces.new([g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]]))
            fs.append(bm.faces.new([gb[i][j + 1], gb[i + 1][j + 1], gb[i + 1][j], gb[i][j]]))
    _tag(fs, bm, "canvas")
    # mantovana perimetrale (due facce)
    per = [(i, 0) for i in range(N)] + [(N, j) for j in range(N)] + [(i, N) for i in range(N, 0, -1)] + [(0, j) for j in range(N, 0, -1)]
    for k in range(len(per)):
        a, b = g[per[k][0]][per[k][1]].co, g[per[(k + 1) % len(per)][0]][per[(k + 1) % len(per)][1]].co
        drop = 0.2
        fs = [pk._quad(bm, [(a.x, a.y, a.z - drop), (b.x, b.y, b.z - drop), (b.x, b.y, b.z), (a.x, a.y, a.z)])]
        if lod < 2:
            fs.append(pk._quad(bm, [(b.x, b.y, b.z - drop), (a.x, a.y, a.z - drop), (a.x, a.y, a.z - 0.002), (b.x, b.y, b.z - 0.002)]))
            # le due facce coincidono: quella interna rientra di 1 cm verso il centro
            for v in fs[-1].verts:
                v.co.x *= 0.996
                v.co.y *= 0.995
        _tag(fs, bm, "canvas")
    # cappello di sfiato
    za = Z_OMB_APEX
    _add(bm, "canvas", pk._lathe, [(0.40, za - 0.03), (0.40, za), (0, za + 0.14)], 4, Matrix(), cap_top=False, phase=math.pi / 4)
    ts = (6, 5, 4)[lod]
    _add(bm, "metal", pk._lathe, [(0.04, 0.08), (0.04, za - 0.02)], ts, Matrix(), cap_top=False)
    _add(bm, "metal", pk._box, -0.4, 0.4, -0.4, 0.4, 0.0, 0.09, faces=("top", "xn", "xp", "yn", "yp"))
    if lod < 2:
        for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            _add(bm, "steel", _tube, [(0, 0, za - 0.07), (sx * OMB_X * 0.97, sy * OMB_Y * 0.97, Z_OMB_EDGE - 0.06)], 0.016,
                 4 if lod == 0 else 3)
            if lod == 0:
                _add(bm, "steel", _tube, [(0, 0, 1.95), (sx * OMB_X * 0.5, sy * OMB_Y * 0.5, (za + Z_OMB_EDGE) / 2 - 0.08)], 0.011, 3)
        for sx in (-1, 1):   # stecche di mezzo sui lati lunghi
            if lod == 0:
                _add(bm, "steel", _tube, [(0, 0, za - 0.08), (sx * OMB_X * 0.97, 0, Z_OMB_EDGE - 0.05)], 0.013, 3)
        if lod == 0:
            _add(bm, "steel", pk._lathe, [(0.055, 1.93), (0.055, 2.01)], 6, Matrix(), cap_top=False)
    o = _write(name + _sfx(lod), bm, ["M_Morin_Dehors"], coll, RD, scale=0.6)
    if lod == 0:
        pk._ucx(name, [(-0.4, 0.4, -0.4, 0.4, 0, 0.09), (-0.045, 0.045, -0.045, 0.045, 0.09, za - 0.05)], coll)
        pk._ucx_hull(name, 2, [(sx * OMB_X, sy * OMB_Y, z) for sx in (-1, 1) for sy in (-1, 1)
                               for z in (Z_OMB_EDGE - 0.2, Z_OMB_EDGE)] + [(0, 0, za + 0.14)], coll)
    return o


FIO_B, FIO_T, FIO_H = 0.29, 0.37, 1.0     # v2: vaso un po' piu' alto (foto C2: ~1 m)

# v2: arbusti misti a cespi su card verticali. Varianti: (nome, seme, cespi [(dx, dy, altezza, raggio, n_card, materiale)])
# materiale 1 = latifoglia (foglia larga), 2 = pino (fine, piu' scuro). Altezze dal suolo fino a ~1,8 m.
FIO_VAR = {
    "SM_Morin_Fioriera": (5, [(0.0, 0.05, 1.78, 0.30, 46, 1), (-0.18, -0.15, 1.40, 0.30, 30, 1), (0.2, -0.12, 1.30, 0.26, 22, 2)]),
    "SM_Morin_FiorieraB": (7, [(0.0, 0.0, 1.62, 0.45, 60, 1), (0.22, 0.2, 1.35, 0.25, 18, 2)]),
    "SM_Morin_FiorieraC": (9, [(-0.1, 0.1, 1.80, 0.22, 34, 2), (0.15, -0.1, 1.55, 0.32, 36, 1), (-0.15, -0.2, 1.25, 0.25, 20, 1)]),
}


def _shrub_cards(bm, rng, base_z, cespi, lod, card_out):
    """Card verticali o inclinate attorno all'asse di ogni cespo, rivolte verso l'esterno: sagoma irregolare, non a sfera."""
    uvl = _uvl(bm)
    k = (1.0, 0.45, 0.16)[lod]
    for dx, dy, top, r, n, mi in cespi:
        n = max(4, int(round(n * k)))
        sz = 1.0 / math.sqrt(max(k, 0.16)) ** 0.8
        for _ in range(n):
            t = rng.uniform(0.15, 1.0) ** 0.7                     # quota relativa nel cespo (piu' card in alto)
            hz = base_z + (top - base_z) * t
            rr = r * (0.35 + 0.65 * math.sin(math.pi * min(t, 0.95) * 0.9 + 0.3)) * rng.uniform(0.6, 1.1)
            a = rng.uniform(0, 2 * math.pi)
            c = Vector((dx + rr * math.cos(a), dy + rr * math.sin(a), hz))
            out = Vector((math.cos(a), math.sin(a), 0.5 * t)).normalized()
            w = rng.uniform(0.22, 0.38) * sz
            h = rng.uniform(0.30, 0.50) * sz
            h = min(h, (top - base_z) * 0.9)
            e1 = Vector((-math.sin(a + rng.normal(0, 0.5)), math.cos(a + rng.normal(0, 0.5)), 0)) * w / 2
            tilt = rng.uniform(0.0, 0.5)
            e2 = (Vector((0, 0, 1)) * (1 - tilt) + out * tilt).normalized() * h / 2
            if c.z + e2.z > top:
                c.z = top - e2.z
            vs = [bm.verts.new(c + sx * e1 + sy * e2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            f = bm.faces.new(vs)
            f.material_index = mi
            q = int(rng.integers(0, 4))
            u0, v0 = (q % 2) * 0.5, 0.5 - (q // 2) * 0.5
            for lp, (uu, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
                lp[uvl].uv = (u0 + 0.5 * uu, v0 + 0.5 * vv)
            card_out.append((f, out))


def build_fioriera(coll, lod=0, name="SM_Morin_Fioriera"):
    bm = bmesh.new()
    _reg_layer(bm)
    b, t, H, w = FIO_B, FIO_T, FIO_H, 0.03
    ob = [(-b, -b), (b, -b), (b, b), (-b, b)]
    ot = [(-t, -t), (t, -t), (t, t), (-t, t)]
    it = [(-(t - w), -(t - w)), (t - w, -(t - w)), (t - w, t - w), (-(t - w), t - w)]
    fs = []
    for i in range(4):
        j = (i + 1) % 4
        fs.append(pk._quad(bm, [(*ob[i], 0), (*ob[j], 0), (*ot[j], H), (*ot[i], H)]))
        fs.append(pk._quad(bm, [(*ot[i], H), (*ot[j], H), (*it[j], H), (*it[i], H)]))
        if lod < 2:
            fs.append(pk._quad(bm, [(*it[i], H), (*it[j], H), (*it[j], H - 0.07), (*it[i], H - 0.07)]))
    _tag(fs, bm, "fiber")
    zs = H - (0.07 if lod < 2 else 0.0)
    _tag([pk._quad(bm, [(*p, zs) for p in it])], bm, "soil")
    _uv_regions(bm, RD, 0.5)
    seed, cespi = FIO_VAR[name]
    rng = np.random.default_rng(seed)
    cards = []
    _shrub_cards(bm, rng, zs, cespi, lod, cards)
    o = mm._finish_tree(name + _sfx(lod), bm, cards,
                        ["M_Morin_Dehors", "M_Albero_Latifoglia_Chioma", "M_Morin_PinoDomestico_Chioma"], coll)
    _clean_attrs(o)
    if lod == 0:
        pk._ucx(name, [(-t, t, -t, t, 0, H)], coll)
    return o


def build_pav(coll, name="SM_Pav_Chiosco"):
    """Cubetti attorno al chiosco e al dehors (continua SM_Pav_FasciaPalme_9m oltre Y 102), Z +0,15, bordi fino a -0,15."""
    x0, x1, y0, y1 = PAV_RECT
    bm = bmesh.new()
    pk._box(bm, x0, x1, y0, y1, pk.ZB, ZF, faces=("top", "xn", "xp", "yp"))
    o = pk._finish(name, bm, ["M_Pav_Cubetti"], coll, uv="world")
    pk._ucx(name, [(x0, x1, y0, y1, pk.ZB, ZF)], coll)
    return o


PAV_RECT = (95.0, 117.0, 102.0, 113.5)


def build_all():
    coll = pk._coll(KIT)
    out = []
    for l in range(3):
        out.append(build_chiosco(coll, l))
        out.append(build_ombrellone(coll, l))
        for fn in FIO_VAR:
            out.append(build_fioriera(coll, l, fn))
        for k in ("tavolino", "sedia", "set", "sgabello"):
            out.append(build_prop(coll, k, l))
    out.append(build_pav(coll))
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    for o in sorted(out, key=lambda o: o.name):
        print(f"{o.name:<30} tri {pk.tri_count(o):>6}  dim {tuple(round(d, 2) for d in o.dimensions)}")
    return out


# =============================================================================================================
# disposizione (coordinate Blender) e CSV in coordinate UE
# =============================================================================================================
CH_POS = (100.0, 106.0)
DEHORS = (103.5, 113.9, 104.45, 112.6)   # assi delle fioriere: x0 (aperto verso il chiosco), x1, y mare, y citta'


def layout():
    rows = [("SM_Pav_Chiosco", "Pav_Chiosco", 0.0, 0.0, 0.0, 0.0),
            ("SM_Morin_Chiosco", "Chiosco_00", CH_POS[0], CH_POS[1], ZF, 0.0)]
    cx, cy = CH_POS
    sg = [(cx - 1.1, cy - CH_HW - 0.55), (cx, cy - CH_HW - 0.55), (cx + 1.1, cy - CH_HW - 0.55),
          (cx - CH_HW - 0.55, cy - 0.6), (cx - CH_HW - 0.55, cy + 0.6)]
    for i, (x, y) in enumerate(sg):
        rows.append(("SM_Morin_Sgabello", f"Sgabello_{i:02d}", x, y, ZF, 17.0 * i))
    for i, (x, y) in enumerate([(106.1, 106.4), (111.3, 106.4), (106.1, 110.6), (111.3, 110.6)]):   # v2: tele 5 x 4 m
        rows.append(("SM_Morin_Ombrellone", f"Ombrellone_{i:02d}", x, y, ZF, 0.0))
    tav = [(x, y) for y in (105.8, 108.5, 111.25) for x in (104.3, 108.7, 112.55)]   # v2: 9 tavoli, fra i pali
    for i, (x, y) in enumerate(tav):
        rows.append(("SM_Morin_TavoloSet", f"TavoloSet_{i:02d}", x, y, ZF, float((i * 37) % 31 - 15)))
    x0, x1, ym, yc = DEHORS
    fio = [(x, ym) for x in (104.0, 105.2, 106.4, 110.3, 111.5, 112.7, x1)]          # varco d'ingresso X 107-109,7
    fio += [(x1, y) for y in (105.7, 106.95, 108.2, 109.45, 110.7, 111.95)]
    fio += [(x, yc) for x in (x1, 112.7, 111.5, 110.3, 109.1, 107.9, 106.7, 105.5, 104.3)]
    for i, (x, y) in enumerate(fio):
        rows.append((("SM_Morin_Fioriera", "SM_Morin_FiorieraB", "SM_Morin_FiorieraC")[(i * 7) % 3], f"Fioriera_{i:02d}", x, y, ZF, (0.0, 90.0, 180.0, 270.0)[i % 4]))
    return rows


def write_csv(rows, path="exports/chiosco/chiosco_posizioni_v1.csv"):
    return mm.write_csv(rows, path)


def build_context(rows, name="CHIOSCO_Contesto"):
    return mm.build_context(rows, name)


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    lodded = ["SM_Morin_Chiosco", "SM_Morin_Ombrellone", "SM_Morin_Fioriera", "SM_Morin_FiorieraB", "SM_Morin_FiorieraC", "SM_Morin_Tavolino", "SM_Morin_Sedia",
              "SM_Morin_TavoloSet", "SM_Morin_Sgabello"]
    names = ["SM_Pav_Chiosco"]
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in bpy.context.scene.objects}
    for o in bpy.data.collections[KIT].objects:
        o.hide_viewport = False
        o.hide_set(False)
        o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1)
        o.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.update()
    reps = []
    try:
        for nm in names + lodded:
            for lod in ((0,) if nm in names else (0, 1, 2)):
                on = nm if lod == 0 else f"{nm}_LOD{lod}"
                r = morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                            overwrite=overwrite, include_ucx=(lod == 0), bake_rotation=(lod > 0),
                                            verbose=False)
                reps.append(r)
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps


# =============================================================================================================
# camera dal punto di presa della foto 1 (stima a occhio: fuga dei filari, scala del chiosco)
# =============================================================================================================
CAMS = {"CAM_Chiosco_F1": ((94.4, 95.4, ZF + 2.1), 56.0, -1.0, 100.0, (1273, 583)),
        "CAM_Chiosco_F2": ((103.0, 96.0, ZF + 2.2), 8.0, 1.0, 100.0, (1253, 393))}


def cameras():
    mm.CAMS.update(CAMS)
    s = bpy.context.scene
    coll = pk._coll("CHIOSCO_Camere")
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
