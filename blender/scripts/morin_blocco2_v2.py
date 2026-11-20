"""morin_blocco2_v2.py — correzioni v2 al Blocco 2 (2026-11-20, decisioni dell'utente in docs/decisioni.md).

1. REDAMARE -> lettere in corten "LA SPEZIA" (SM_Morin_ScrittaLaSpezia, stesso stile e posizione, T_Morin_Corten riusato).
2. Bandiere sulle 3 aste: SM_Morin_Bandiera_Italia / _Comune / _Aquile (atlante unico T_Morin_Bandiere 2048, card masked
   two-sided, griglia leggermente mossa). Stemma del Comune semplificato dalla blasonatura pubblica; aquila "FORZA AQUILE"
   disegnata ex novo (NON lo stemma della squadra, marchio registrato).
3. Chiosco ottagonale con la tettoia bianca a padiglione e mantovana del chiosco del Blocco 1 (SM_Morin_ChioscoOttagonale_v2).

Esegui dentro blender/arte_blocco2.blend, dopo b2.link_kit() e b2.build_materials():
    import morin_blocco2_v2 as v2; importlib.reload(v2)
    v2.build_v2(); v2.write_csv_nuovi_v2(); v2.context_v2(); v2.export_v2()
Nomi NUOVI: gli asset v1 (SM_Morin_Redamare, SM_Morin_ChioscoOttagonale) restano intatti in exports/ e in UEFN.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

import morin_blocco2 as b2
import morin_pav_kit as pk

PROJ = pk.PROJ
_sfx = b2._sfx

# =============================================================================================================
# 1. SM_Morin_ScrittaLaSpezia
# =============================================================================================================
LSP_W, LSP_H, LSP_D = 7.6, 1.30, 0.35       # stessa altezza e spessore di REDAMARE; larghezza sulla piastra da 8 m


def build_scritta_laspezia(coll, lod=0, name="SM_Morin_ScrittaLaSpezia"):
    """Lettere in corten scatolate su piastra sottile. Origine a terra al centro; con rotZ 0 si legge da +Y."""
    me = b2._text_mesh("LA SPEZIA", 1.0, 0.5, 0.06, resol=(3, 2, 1)[lod], space=1.12)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    sx = LSP_W / (max(xs) - min(xs)); sy = LSP_H / (max(ys) - min(ys)); sz = LSP_D / (max(zs) - min(zs))
    cx, cy0, cz = (max(xs) + min(xs)) / 2, min(ys), (max(zs) + min(zs)) / 2
    W, D, H = b2.RED_PLATE
    for v in bm.verts:
        x, y, z = (v.co.x - cx) * sx, (v.co.y - cy0) * sy, (v.co.z - cz) * sz
        v.co = Vector((-x, z, y + H))
    for f in bm.faces:
        f.material_index = 0
    pk._box(bm, -W / 2, W / 2, -D / 2, D / 2, 0.0, H, 0)
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="BEAUTY")
    pk._recalc(bm)
    o = pk._finish(name + _sfx(lod), bm, [b2.MAT_CORTEN], coll, uv="box", smooth_angle=30.0)
    if lod == 0:
        pk._ucx(name, [(-W / 2, W / 2, -D / 2, D / 2, 0.0, H),
                       (-LSP_W / 2, LSP_W / 2, -LSP_D / 2, LSP_D / 2, H, H + LSP_H)], coll)
    return o


# =============================================================================================================
# 2. bandiere: atlante 2048 (celle 2 x 2 da 1024), bandiera 3:2 in alto in ogni cella
# =============================================================================================================
FLAG_DIR = PROJ + "/blender/textures/blocco2"
FLAG_S = 2048
FLAG_CELL = {"Italia": (0, 1), "Comune": (1, 1), "Aquile": (0, 0)}     # (colonna, riga) dal basso
FLAG_L, FLAG_HH = 2.4, 1.6                 # 2,4 x 1,6 m su asta da 11,5 m [S]
FLAG_Z1 = 11.25                            # bordo alto, sotto il pomolo
FLAG_R0 = 0.06                             # distanza dall'asse dell'asta
FLAG_KINDS = ("Italia", "Comune", "Aquile")
FLAG_YAW = 70.0      # rotZ Blender: sventolano verso terra (brezza di mare del pomeriggio) [S]


def raster_polys(polys, W, H, ss=2):
    """Maschera H x W (riga 0 = alto) dei poligoni in pixel (y verso il basso), pari-dispari, con supersampling."""
    ys, xs = np.mgrid[0:H * ss, 0:W * ss].astype(np.float32)
    xs = (xs + 0.5) / ss
    ys = (ys + 0.5) / ss
    m = np.zeros(xs.shape, bool)
    for poly in polys:
        p = np.asarray(poly, np.float32)
        x0b, y0b = p.min(axis=0)
        x1b, y1b = p.max(axis=0)
        sel = (xs >= x0b) & (xs <= x1b) & (ys >= y0b) & (ys <= y1b)
        if not sel.any():
            continue
        X, Y = xs[sel], ys[sel]
        ins = np.zeros(X.shape, bool)
        for (ax, ay), (bx, by) in zip(p, np.roll(p, -1, axis=0)):
            if ay == by:
                continue
            c = (ay > Y) != (by > Y)
            xint = ax + (Y - ay) * (bx - ax) / (by - ay)
            ins ^= c & (X < xint)
        inside = np.zeros(xs.shape, bool)
        inside[sel] = ins
        m ^= inside
    return m.reshape(H, ss, W, ss).mean(axis=(1, 3)).astype(np.float32)


def text_polys(body, x0, y0, w, h, space=1.0):
    """Triangoli del testo (font interno di Blender, licenza libera) in pixel, centrati nel riquadro (x0, y0, w, h)."""
    cu = bpy.data.curves.new("_tmp_flagtxt", "FONT")
    cu.body = body
    cu.space_character = space
    cu.align_x = "CENTER"
    cu.resolution_u = 6
    ob = bpy.data.objects.new("_tmp_flagtxt", cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    me.calc_loop_triangles()
    tris = [[tuple(me.vertices[i].co[:2]) for i in t.vertices] for t in me.loop_triangles]
    bpy.data.meshes.remove(me)
    P = np.array([p for t in tris for p in t])
    mn, mx = P.min(axis=0), P.max(axis=0)
    s = min(w / (mx[0] - mn[0]), h / (mx[1] - mn[1]))
    ox = x0 + (w - (mx[0] - mn[0]) * s) / 2
    oy = y0 + (h - (mx[1] - mn[1]) * s) / 2
    return [[(ox + (x - mn[0]) * s, oy + (mx[1] - y) * s) for x, y in t] for t in tris]


def union_tris(tris, W, H):
    """Unione di triangoli (ciascuno rasterizzato da solo: niente annullamenti pari-dispari fra triangoli adiacenti)."""
    m = np.zeros((H, W), np.float32)
    for t in tris:
        m = np.maximum(m, raster_polys([t], W, H))
    return m


def eagle_polys(cx, cy, sc):
    """Aquila ORIGINALE del progetto, stilizzata ad ali spiegate, testa a sinistra. Unita' sc pixel, y del disegno in alto."""
    R = [(0.0, 0.40), (0.08, 0.37), (0.15, 0.25), (0.33, 0.37), (0.52, 0.52), (0.72, 0.63), (0.93, 0.68),
         (0.86, 0.56), (0.92, 0.45), (0.78, 0.47), (0.83, 0.33), (0.68, 0.37), (0.71, 0.21), (0.56, 0.27),
         (0.57, 0.11), (0.43, 0.18), (0.40, 0.03), (0.23, 0.07), (0.14, -0.06), (0.13, -0.30), (0.21, -0.36),
         (0.29, -0.46), (0.22, -0.47), (0.18, -0.42), (0.12, -0.44), (0.15, -0.66), (0.07, -0.60), (0.0, -0.71)]
    body = R + [(-x, y) for x, y in reversed(R[1:-1])]
    head = [(0.10 * math.cos(a), 0.47 + 0.10 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
    beak = [(-0.07, 0.51), (-0.20, 0.47), (-0.17, 0.42), (-0.12, 0.44), (-0.07, 0.43)]
    eye = [(-0.035 + 0.02 * math.cos(a), 0.49 + 0.02 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)]
    T = lambda poly: [(cx + x * sc, cy - y * sc) for x, y in poly]
    return [T(body)], [T(head), T(beak)], [T(eye)]


def _paint(img, mask, col):
    c = np.asarray(col, np.float32) / 255.0
    img[:] = img * (1 - mask[..., None]) + c[None, None] * mask[..., None]


def _eagle_mask(cx, cy, sc, W, H):
    b, h, e = eagle_polys(cx, cy, sc)
    m = np.maximum(raster_polys(b, W, H), np.maximum(raster_polys(h[:1], W, H), raster_polys(h[1:], W, H)))
    return m, raster_polys(e, W, H)


def make_tex_bandiere():
    """T_Morin_Bandiere_D (RGBA, A = maschera), _N, _ORM 2048, procedurali."""
    import morin_texphoto as tp
    S, C = FLAG_S, FLAG_S // 2
    fw, fh = C, int(round(C * 2 / 3))
    BI = (244, 244, 238)
    NE = (18, 18, 20)
    D = np.full((S, S, 3), 0.5, np.float32)
    A = np.zeros((S, S), np.float32)
    flags = {}
    # --- tricolore (verde all'asta, u = 0)
    f = np.zeros((fh, fw, 3), np.float32)
    f[:, :fw // 3] = np.array((0, 146, 70)) / 255.0
    f[:, fw // 3:2 * fw // 3] = np.array((244, 245, 240)) / 255.0
    f[:, 2 * fw // 3:] = np.array((206, 43, 55)) / 255.0
    flags["Italia"] = f
    # --- Comune della Spezia: drappo bianco con lo stemma civico semplificato (blasonatura: d'azzurro alla torre quadrata,
    #     aperta e finestrata, merlata alla ghibellina, su monte di tre cime di verde, sostenente un'aquila nera coronata d'oro;
    #     corona di citta'). Disposizione sul drappo [S].
    f = np.ones((fh, fw, 3), np.float32) * np.array(BI) / 255.0
    cx, top, sw, sh = fw / 2, fh * 0.22, fw * 0.30, fh * 0.62
    shield = ([(cx - sw / 2, top), (cx + sw / 2, top), (cx + sw / 2, top + sh * 0.62)] +
              [(cx + sw / 2 * math.cos(a), top + sh * 0.62 + sh * 0.38 * math.sin(a)) for a in np.linspace(0, math.pi, 18)[1:-1]] +
              [(cx - sw / 2, top + sh * 0.62)])
    bord = [(cx + (x - cx) * 1.07, top - 5 + (y - top) * 1.03) for x, y in shield]
    _paint(f, raster_polys([bord], fw, fh), (200, 158, 42))
    msh = raster_polys([shield], fw, fh)
    _paint(f, msh, (38, 92, 170))
    base = top + sh * 0.93
    mount = [(cx - sw * 0.5, base + 30), (cx - sw * 0.5, base - sh * 0.05), (cx - sw * 0.30, base - sh * 0.19),
             (cx - sw * 0.15, base - sh * 0.11), (cx, base - sh * 0.25), (cx + sw * 0.15, base - sh * 0.11),
             (cx + sw * 0.30, base - sh * 0.19), (cx + sw * 0.5, base - sh * 0.05), (cx + sw * 0.5, base + 30)]
    _paint(f, raster_polys([mount], fw, fh) * msh, (48, 138, 62))
    tw, t0, t1 = sw * 0.34, top + sh * 0.32, base - sh * 0.19
    tower = [(cx - tw / 2, t1), (cx - tw / 2, t0)]
    nm = 4
    for k in range(nm):   # merli a coda di rondine
        xa = cx - tw / 2 + k * tw / nm
        xb = xa + tw / nm * 0.62
        tower += [(xa, t0 - 12), (xa + (xb - xa) / 2, t0 - 6), (xb, t0 - 12), (xb, t0)]
    tower += [(cx + tw / 2 - tw / nm * 0.38, t0), (cx + tw / 2, t0 - 12), (cx + tw / 2, t1)]
    _paint(f, raster_polys([tower], fw, fh), (192, 186, 172))
    for wx, wy, ww, wh in ((cx - tw * 0.30, t0 + sh * 0.06, tw * 0.16, sh * 0.08), (cx + tw * 0.14, t0 + sh * 0.06, tw * 0.16, sh * 0.08),
                           (cx - tw * 0.15, t1 - sh * 0.15, tw * 0.30, sh * 0.15)):
        _paint(f, raster_polys([[(wx, wy), (wx + ww, wy), (wx + ww, wy + wh), (wx, wy + wh)]], fw, fh), (48, 42, 40))
    me, _ = _eagle_mask(cx, t0 - sh * 0.15, sw * 0.17, fw, fh)
    _paint(f, me, NE)
    ey = t0 - sh * 0.15 - 0.62 * sw * 0.17
    crown = [(cx - 9, ey + 4), (cx - 11, ey - 8), (cx - 4, ey - 2), (cx, ey - 11), (cx + 4, ey - 2), (cx + 11, ey - 8), (cx + 9, ey + 4)]
    _paint(f, raster_polys([crown], fw, fh), (215, 172, 45))
    ct = top - fh * 0.06
    cr = [(cx - sw * 0.40, top - 8), (cx - sw * 0.40, ct)]
    for k in range(5):
        xa = cx - sw * 0.40 + k * sw * 0.80 / 5
        cr += [(xa + sw * 0.03, ct), (xa + sw * 0.03, ct - fh * 0.05), (xa + sw * 0.13, ct - fh * 0.05), (xa + sw * 0.13, ct)]
    cr += [(cx + sw * 0.40, ct), (cx + sw * 0.40, top - 8)]
    _paint(f, raster_polys([cr], fw, fh), (200, 158, 42))
    flags["Comune"] = f
    # --- FORZA AQUILE: bianco, fasce nere, aquila originale nera, scritta nera
    f = np.ones((fh, fw, 3), np.float32) * np.array(BI) / 255.0
    band = int(fh * 0.07)
    f[:band] = np.array(NE) / 255.0
    f[-band:] = np.array(NE) / 255.0
    me, eye = _eagle_mask(fw * 0.5, fh * 0.36, fh * 0.34, fw, fh)
    _paint(f, me, NE)
    _paint(f, eye, BI)
    _paint(f, union_tris(text_polys("FORZA AQUILE", fw * 0.09, fh * 0.70, fw * 0.82, fh * 0.15), fw, fh), NE)
    flags["Aquile"] = f
    rng = np.random.default_rng(5)
    for k, img in flags.items():
        c, r = FLAG_CELL[k]
        y0 = int((1 - (r + 1) / 2) * S)
        x0 = int(c * C)
        n = tp.blur(rng.standard_normal((fh, fw)).astype(np.float32), 1.0) * 0.015
        D[y0:y0 + fh, x0:x0 + fw] = np.clip(img * (1 + n[..., None]), 0, 1)
        A[y0:y0 + fh, x0:x0 + fw] = 1.0
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    hgt = 0.5 + 0.25 * np.sin(xx * 1.3) * np.sin(yy * 1.3)
    nrm = tp.normal_dx(hgt, 0.5)
    os.makedirs(FLAG_DIR, exist_ok=True)
    tp.save(np.dstack([D, A]), f"{FLAG_DIR}/T_Morin_Bandiere_D.png")
    tp.save(nrm, f"{FLAG_DIR}/T_Morin_Bandiere_N.png")
    tp.save(np.dstack([np.ones_like(A), np.full_like(A, 0.85), np.zeros_like(A)]), f"{FLAG_DIR}/T_Morin_Bandiere_ORM.png")
    return [f"{FLAG_DIR}/T_Morin_Bandiere_{k}.png" for k in ("D", "N", "ORM")]


def build_material_bandiere():
    m = pk._pbr_material("M_Morin_Bandiere", f"{FLAG_DIR}/T_Morin_Bandiere_D.png", f"{FLAG_DIR}/T_Morin_Bandiere_N.png",
                         f"{FLAG_DIR}/T_Morin_Bandiere_ORM.png", alpha=True)
    m.use_backface_culling = False
    for im in bpy.data.images:
        if im.name.startswith("T_Morin_Bandiere_D"):
            im.reload()
    return m


def build_bandiera(coll, kind, lod=0):
    """Card a griglia mossa (onda che cresce dall'asta). Origine alla base dell'asta come SM_Morin_AstaBandiera: si posa
    nella stessa posizione dell'asta; lo yaw da' il verso del vento (asse locale +X)."""
    name = f"SM_Morin_Bandiera_{kind}"
    nu, nv = ((12, 4), (6, 2), (2, 1))[lod]
    c, r = FLAG_CELL[kind]
    u0, u1 = c * 0.5, c * 0.5 + 0.5
    v1 = r * 0.5 + 0.5
    v0 = v1 - 0.5 * (round(1024 * 2 / 3) / 1024)
    e = 1.5 / FLAG_S
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    V = {}
    for i in range(nu + 1):
        s = i / nu
        for j in range(nv + 1):
            t = j / nv
            amp = 0.16 * s ** 1.2
            x = FLAG_R0 + s * FLAG_L - 0.06 * s * s
            y = amp * math.sin(2 * math.pi * (1.15 * s - 0.15 * t) + 0.4)
            z = FLAG_Z1 - FLAG_HH * (1 - t) - 0.10 * s * s
            V[i, j] = (bm.verts.new((x, y, z)), (u0 + e + (u1 - u0 - 2 * e) * s, v0 + e + (v1 - v0 - 2 * e) * t))
    for i in range(nu):
        for j in range(nv):
            q = [V[i, j], V[i + 1, j], V[i + 1, j + 1], V[i, j + 1]]
            f = bm.faces.new([a for a, _ in q])
            for lp, (_, uv) in zip(f.loops, q):
                lp[uvl].uv = uv
    return pk._finish(name + _sfx(lod), bm, ["M_Morin_Bandiere"], coll, uv=None, smooth_angle=80.0)


# =============================================================================================================
# 3. chiosco ottagonale v2: tettoia bianca a padiglione con mantovana (quote del chiosco del Blocco 1)
# =============================================================================================================
OCT2_RE = b2.OCT_R + 0.70     # gronda (raggio circoscritto): ~1 m oltre il corpo, come la tettoia del Blocco 1
OCT2_ZI, OCT2_ZM0, OCT2_ZE, OCT2_ZT = 2.62, 2.42, 2.72, 3.12     # intradosso, fondo mantovana, gronda, colmo (= Blocco 1)
OCT2_TOPR = OCT2_RE - 1.25    # colmo piatto


def _atlas_face_v2(f, lay, reg, scale=0.25):
    """Come b2._atlas_face, ma le regioni a tinta unita non collassano piu' tutte le UV in un punto (causa delle tangenti
    degeneri della v1): proiezione planare compressa nel 30 % centrale della regione."""
    import morin_chiosco as mc
    u0, v0, u1, v1 = mc.RD["wood"] if reg == "wood" else mc.RC[reg]
    n = f.normal
    ax = max(range(3), key=lambda i: abs(n[i]))
    pts = [(lp.vert.co.y, lp.vert.co.z) if ax == 0 else (lp.vert.co.x, lp.vert.co.z) if ax == 1 else
           (lp.vert.co.x, lp.vert.co.y) for lp in f.loops]
    m0, mw = (0.35, 0.30) if reg in ("crema", "steel", "white", "dark") else (0.05, 0.90)
    a0, b0 = min(p[0] for p in pts), min(p[1] for p in pts)
    ext = max(max(p[0] for p in pts) - a0, max(p[1] for p in pts) - b0, 1e-3)
    for lp, (a, b) in zip(f.loops, pts):
        lp[lay].uv = (u0 + (u1 - u0) * (m0 + mw * (a - a0) / ext), v0 + (v1 - v0) * (m0 + mw * (b - b0) / ext))


def build_chiosco_ott_v2(coll, lod=0, name="SM_Morin_ChioscoOttagonale_v2"):
    _oct = b2._oct
    bm = bmesh.new()
    lay = bm.loops.layers.uv.verify()
    regs = {}

    def face(vs, reg):
        f = bm.faces.new([bm.verts.new(v) for v in vs])
        regs[f] = reg
        return f
    R0 = b2.OCT_R - 0.35
    B, Cc, Wt = _oct(R0, 0.0), _oct(R0, 1.10), _oct(R0, OCT2_ZI)
    for k in range(8):
        j = (k + 1) % 8
        back = ((B[k] + B[j]) / 2).y > 0.8          # lati verso il viale: chiusi
        face([B[k], B[j], Cc[j], Cc[k]], "wood" if not back else "crema")
        if back:
            face([Cc[k], Cc[j], Wt[j], Wt[k]], "crema")
        else:
            Ci, Wi = _oct(R0 - 0.6, 1.10), _oct(R0 - 0.6, OCT2_ZI)
            face([Ci[k], Ci[j], Wi[j], Wi[k]], "dark")
            face([Cc[k], Cc[j], Ci[j], Ci[k]], "wood")
            face([Wi[k], Wi[j], Wt[j], Wt[k]], "dark")
    if lod < 2:   # tende crema sotto la gronda (piu' corte della v1)
        T0, T1 = _oct(R0 - 0.02, OCT2_ZI - 0.05), _oct(R0 + 0.75, 2.20)
        for k in range(8):
            j = (k + 1) % 8
            face([T1[k], T1[j], T0[j], T0[k]], "crema")
    Elo, Ehi, Ei = _oct(OCT2_RE, OCT2_ZM0), _oct(OCT2_RE, OCT2_ZE), _oct(OCT2_RE, OCT2_ZI)
    Top, In = _oct(OCT2_TOPR, OCT2_ZT), _oct(R0, OCT2_ZI)
    Lo2, Hi2 = _oct(OCT2_RE - 0.012, OCT2_ZM0), _oct(OCT2_RE - 0.012, OCT2_ZI)
    for k in range(8):
        j = (k + 1) % 8
        face([Elo[k], Elo[j], Ehi[j], Ehi[k]], "white")          # mantovana, fronte
        if lod < 2:
            face([Lo2[j], Lo2[k], Hi2[k], Hi2[j]], "white")      # mantovana, retro
        face([Ehi[k], Ehi[j], Top[j], Top[k]], "white")          # falda
        face([Ei[j], Ei[k], In[k], In[j]], "white")              # intradosso
    face(Top, "white")
    # pulizia (avviso UEFN sulla v1: tangenti degeneri / normali quasi nulle): vertici fusi, facce ad area ~0 eliminate
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bad = [f for f in bm.faces if f.calc_area() < 1e-6]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    pk._recalc(bm)
    for f in bm.faces:
        reg = regs.get(f, "white")
        _atlas_face_v2(f, lay, reg)
        f.material_index = 1 if reg == "wood" else 0
    o = pk._finish(name + _sfx(lod), bm, ["M_Morin_Chiosco", "M_Morin_Dehors"], coll, uv=None, smooth_angle=None)
    o.data.uv_layers[0].name = "UVMap"          # bmesh verify() in Blender 5 lo chiama "Float2"
    if lod == 0:
        pk._ucx_hull(name, 0, [tuple(v) for v in _oct(R0, 0.0) + _oct(R0, OCT2_ZI)], coll)
        pk._ucx_hull(name, 1, [tuple(v) for v in _oct(OCT2_RE, OCT2_ZM0) + _oct(OCT2_TOPR, OCT2_ZT)], coll)
    return o


# =============================================================================================================
# 4. piazzale terminale v2 (trovato preparando il Blocco 3): la v1 aveva 3 triangoli rivolti verso il basso e sovrapposti al
#    camminamento (triangolazione EAR_CLIP sbagliata del poligono concavo). La v2 lo divide in 3 pezzi convessi.
# =============================================================================================================
def build_piazzale_v2(coll, name="SM_Pav_Piazzale_Fine_B2_v2"):
    poly = b2.piazzale_poly()
    ci, ei, _, _, _, _, p6, p7 = [Vector(p) for p in poly]
    x1 = b2.PIAZZALE_X1
    parts = [[(ci.x, ci.y), (ei.x, ei.y), (p7.x, ei.y), (p7.x, p7.y)],                 # trapezio sullo smusso
             [(p7.x, ei.y), (x1, ei.y), (x1, 121.0), (p7.x, 121.0)],                     # fascia X 559,2-566
             [(558.75, 88.45), (p7.x, 88.45), (p7.x, 121.0), (558.75, 121.0)]]           # striscia X 558,75-559,2
    bm = bmesh.new()
    for pts in parts:
        f = bm.faces.new([bm.verts.new((x, y, 0.0)) for x, y in pts])
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    for a, b in (((ei.x, ei.y), (x1, ei.y)), ((x1, ei.y), (x1, 121.0))):
        q = [bm.verts.new((a[0], a[1], -3.0)), bm.verts.new((b[0], b[1], -3.0)), bm.verts.new((b[0], b[1], 0.0)),
             bm.verts.new((a[0], a[1], 0.0))]
        bm.faces.new(q)
    o = pk._finish(name, bm, ["M_Pav_Cubetti"], coll, uv="world")
    for u in [x for x in bpy.data.objects if x.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)
    pk._ucx_hull(name, 0, [(x, y, z) for x, y in parts[0] for z in (-3.0, 0.0)], coll)
    pk._ucx(name, [(p7.x, x1, ei.y, 121.0, -3.0, 0.0), (558.75, p7.x, 88.45, 121.0, -3.0, 0.0)], coll, start=1)
    down = sum(1 for p in o.data.polygons if p.normal.z < -0.5)
    print(name, "facce verso il basso:", down, "tri", pk.tri_count(o))
    return o


def export_piazzale_v2(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    coll = pk._coll(b2.KIT)
    o = build_piazzale_v2(coll)
    for x in [o] + [u for u in coll.objects if u.name.startswith("UCX_SM_Pav_Piazzale_Fine_B2_v2_")]:
        x.hide_viewport = False
        x.hide_set(False)
    r = morin_export.export_fbx([o], f"{b2.EXPDIR}/SM_Pav_Piazzale_Fine_B2_v2.fbx", mode="asset", overwrite=overwrite,
                                include_ucx=True, verbose=False)
    b2._hide_kit(coll)
    return r


# =============================================================================================================
# build, CSV, contesto, export
# =============================================================================================================
V2_LODDED = {"SM_Morin_ScrittaLaSpezia": build_scritta_laspezia, "SM_Morin_ChioscoOttagonale_v2": build_chiosco_ott_v2}


def v2_names():
    return list(V2_LODDED) + [f"SM_Morin_Bandiera_{k}" for k in FLAG_KINDS]


def build_v2(textures=True):
    coll = pk._coll(b2.KIT)
    if textures:
        make_tex_bandiere()
    build_material_bandiere()
    rep = {}
    for nm, fn in V2_LODDED.items():
        rep[nm] = [pk.tri_count(fn(coll, l)) for l in range(3)]
    for k in FLAG_KINDS:
        rep[f"SM_Morin_Bandiera_{k}"] = [pk.tri_count(build_bandiera(coll, k, l)) for l in range(3)]
    b2._hide_kit(coll)
    for nm in rep:
        o = bpy.data.objects[nm]
        n_ucx = len([u for u in coll.objects if u.name.startswith(f"UCX_{nm}_")])
        rep[nm] = (rep[nm], tuple(round(d, 2) for d in o.dimensions), n_ucx)
        print(f"{nm:<34} tri {rep[nm][0]}  dim {rep[nm][1]}  UCX {n_ucx}")
    return rep


def rows_nuovi_v2():
    out = []
    for r in b2.layout_nuovi() + [x for x in b2.layout_fine() if x[7] == "nuovi"]:
        if r[0] == "SM_Morin_Redamare":
            r = ("SM_Morin_ScrittaLaSpezia", "B2_ScrittaLaSpezia") + tuple(r[2:])
        elif r[0] == "SM_Morin_ChioscoOttagonale":
            r = ("SM_Morin_ChioscoOttagonale_v2", "B2_ChioscoOttagonale_v2") + tuple(r[2:])
        elif r[0] == "SM_Pav_Piazzale_Fine_B2":
            r = ("SM_Pav_Piazzale_Fine_B2_v2", "B2_Pav_Piazzale_Fine_B2_v2") + tuple(r[2:])
        out.append(r)
    for k, (x, y) in zip(FLAG_KINDS, b2.aste_xy()):
        out.append((f"SM_Morin_Bandiera_{k}", f"B2_Bandiera_{k}", float(x), float(y), 0.0, FLAG_YAW, 1.0, "nuovi"))
    return out


def write_csv_nuovi_v2(rows=None):
    rows = rows or rows_nuovi_v2()
    path = f"{PROJ}/exports/blocco2/blocco2_nuovi_v2.csv"
    lines = ["asset,nome,x,y,z,yaw,scala"]
    for a, n, x, y, z, rz, s, _ in rows:
        yaw = -rz if abs(rz) > 1e-9 else 0.0
        lines.append(f"{a},{n},{b2._ue(x * 100)},{b2._ue(-y * 100)},{b2._ue(z * 100)},{yaw:.4f},{s:.3f}")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print(path, len(rows))
    return path


def context_v2(rows=None):
    rows = rows or rows_nuovi_v2()
    coll = pk._coll(b2.CTX)
    for o in coll.objects:
        if o.name in ("CTX_B2_Redamare", "CTX_B2_ChioscoOttagonale"):
            o.hide_render = True
            o.hide_viewport = True
    for a, n, x, y, z, rz, s, g in rows:
        if a not in v2_names():
            continue
        o = bpy.data.objects.get("CTX_" + n)
        if o is None:
            o = bpy.data.objects.new("CTX_" + n, bpy.data.objects[a].data)
            coll.objects.link(o)
        o.data = bpy.data.objects[a].data
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(rz))
    return coll


def export_v2(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    coll = bpy.data.collections[b2.KIT]
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in coll.objects}
    for o in coll.objects:
        o.hide_viewport = False
        o.hide_set(False)
    bpy.context.view_layer.update()
    reps = []
    try:
        for nm in v2_names():
            for lod in range(3):
                on = nm + _sfx(lod)
                reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{b2.EXPDIR}/{on}.fbx", mode="asset",
                                                    overwrite=overwrite, include_ucx=(lod == 0), bake_rotation=(lod > 0),
                                                    verbose=False))
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps
