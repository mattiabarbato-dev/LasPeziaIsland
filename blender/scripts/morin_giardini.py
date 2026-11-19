"""morin_giardini.py — Giardini a Mare: oleandri ad alberello e panchina lunga in pietra (v1, 2026-11-19).

Schede: ref/zona_parcheggio_chiosco.md §4 (prato con alberelli), ref/palme.md (filare di oleandri Y 119,5, X 131-556 [V] OSM
way 850406862), ref/sezione.md (fascia palme Y 89-102 a Z +0,15, giardini Y 102-116).
Foto: ref/foto/vista/prato con alberelli.png (cattura Street View, deroga [SV] CLAUDE.md §5: dalla foto solo i colori
campionati; texture procedurali, niente UI, persone, targhe).

Esegui dentro blender/arte_giardini.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_giardini as mg; importlib.reload(mg)
    mg.make_textures()      # blender/textures/giardini/ (chioma 2048 RGBA, fusto 1024; D sRGB, N DirectX, ORM)
    mg.build_materials()    # M_Morin_Oleandro_Chioma (masked, two-sided), M_Morin_Oleandro_Fusto (+ M_Pav_Fascia riusato)
    mg.build_all()          # mesh LOD0/1/2 + UCX nella collezione GIARDINI_Kit (riscrive le mesh omonime)
    rows = mg.layout()      # posizioni (coordinate Blender)
    mg.write_csvs(rows)     # exports/giardini/giardini_posizioni_v1.csv (Blocco 1, X <= 250) + _blocco2.csv (X > 250)
    mg.build_context(rows)  # istanze per il render (GIARDINI_Contesto)
    mg.export_all()         # FBX in exports/giardini/ (LOD1/LOD2 con bake_rotation=True)
    mg.cameras()            # CAM_Giardini_F1 (punto di presa stimato della foto)

Oleandri: origine al piede, si posano a Z 0 (suolo del blockout lato viale [S]). v2: le due varianti hanno chiome di forma diversa
(OL_SHAPE) e lo stesso atlante: quadranti in alto = fiori bianchi, in basso = rosa.
Panchina: modulo da 4 m con origine al centro della base, asse lungo X; si posa a quota cubetti Z +0,15 (pk.ZF).
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
TEXDIR = PROJ + "/blender/textures/giardini"
KIT = "GIARDINI_Kit"
EXPDIR = "//../exports/giardini"
ZF = pk.ZF

# colori sRGB (albedo) stimati dalla foto [SV] (campioni in ombra/controluce: bianco 176,173,171; rosa 99-114,47-68,64-83;
# foglie 45,56,44) riportati a luce piena
C_FOGLIA = (54, 74, 46)
C_FOGLIA_RETRO = (92, 108, 70)
C_BIANCO = (232, 229, 220)
C_ROSA_SCURO = (222, 34, 120)      # v2: fucsia come in foto
C_ROSA_CHIARO = (238, 92, 160)
C_CENTRO = (238, 222, 160)

# oleandro ad alberello v2 [S]: fusto Ø 12-10 cm fino a 1,9 m, chioma Ø ~3,1-3,3 m schiacciata e a lobi, h totale ~4 m
# (proporzioni dalla foto: chiome grandi e piene, ~3 volte l'altezza delle auto parcheggiate dietro).
# Due forme di chioma diverse, una per variante (seme, raggi x/y/z, quota centro, n lobi).
OL_FUSTO = 1.90                # v2
OL_SHAPE = {"SM_Morin_OleandroAlberello_Bianco": (41, (1.62, 1.50, 1.02), 2.92, 7),
            "SM_Morin_OleandroAlberello_Rosa": (73, (1.50, 1.66, 1.00), 2.90, 8)}
OL_VAR = {"SM_Morin_OleandroAlberello_Bianco": (0, 1), "SM_Morin_OleandroAlberello_Rosa": (2, 3)}

# panchina lunga v2 [S] dalla foto: lastra 0,45 x 0,07 su pilastrini 0,14 x 0,30 ogni 1,0 m, seduta a 0,45 m
PL = dict(L=4.0, W=0.45, H=0.45, T=0.07, legs=(-1.5, -0.5, 0.5, 1.5), lx=0.14, ly=0.30)
PL_Y = 101.70           # asse della panchina: bordo dei cubetti verso il prato (lastra Y 101,475-101,925)
OL_Y = 119.5            # filare OSM [V]
OL_X0, OL_X1, OL_PASSO = 131.0, 550.0, 5.5


# =============================================================================================================
# texture
# =============================================================================================================
def _c(c):
    return np.asarray(c, np.float32) / 255.0


def _paint(Q, y0, x0, m, col, h, ao):
    sz_y, sz_x = m.shape
    S = Q["a"].shape[0]
    if y0 < 0 or x0 < 0 or y0 + sz_y > S or x0 + sz_x > S:
        return
    sl = (slice(y0, y0 + sz_y), slice(x0, x0 + sz_x))
    mk = m[..., None]
    Q["c"][sl] = Q["c"][sl] * (1 - mk) + col * mk
    Q["a"][sl] = np.maximum(Q["a"][sl], m)
    Q["h"][sl] = Q["h"][sl] * (1 - m) + h * m
    Q["ao"][sl] = Q["ao"][sl] * (1 - m) + ao * m
    Q["r"][sl] = Q["r"][sl] * (1 - m) + Q["_rough"] * m


def _leaf(rng, L, W):
    """Foglia lanceolata (oleandro): lunga e stretta, appuntita, con nervatura centrale chiara."""
    sz = int(L) + 4
    y, x = np.mgrid[0:sz, 0:sz].astype(np.float32) - sz / 2
    th = rng.uniform(0, 2 * np.pi)
    xr = x * np.cos(th) + y * np.sin(th)
    yr = -x * np.sin(th) + y * np.cos(th)
    t = np.clip(xr / (L / 2), -1, 1)
    half = W / 2 * np.clip(1 - t ** 2, 0, 1) ** 0.75 * (1 + 0.15 * t)
    m = ((np.abs(yr) < half) & (np.abs(xr) < L / 2)).astype(np.float32)
    rib = np.clip(1 - np.abs(yr) / 1.6, 0, 1) * m
    side = np.sign(yr) * 0.08
    return m, rib, side


def _flower(rng, D, petals=5):
    sz = int(D) + 2
    y, x = np.mgrid[0:sz, 0:sz].astype(np.float32) - sz / 2
    r = np.sqrt(x ** 2 + y ** 2) / (D / 2)
    ang = np.arctan2(y, x) + rng.uniform(0, 2 * np.pi)
    lim = 0.55 + 0.45 * np.abs(np.cos(petals / 2 * ang)) ** 0.6
    m = (r < lim).astype(np.float32)
    return m, r


def _crown_quadrant(seed, kind):
    """Quadrante 1024: ciuffo di foglie lanceolate con trusses (corimbi) di fiori bianchi o rosa sopra."""
    S = 1024
    rng = np.random.default_rng(seed)
    Q = {"c": np.zeros((S, S, 3), np.float32), "a": np.zeros((S, S), np.float32), "h": np.zeros((S, S), np.float32),
         "ao": np.ones((S, S), np.float32), "r": np.full((S, S), 0.6, np.float32)}
    leaf_c, back_c = _c(C_FOGLIA), _c(C_FOGLIA_RETRO)
    if kind == "bianco":
        fl_cols = [_c(C_BIANCO)]
    else:
        fl_cols = [_c(C_ROSA_SCURO), _c(C_ROSA_CHIARO)] if seed % 2 == 0 else [_c(C_ROSA_CHIARO), _c(C_ROSA_SCURO)]
    R0 = S * 0.37
    trusses = []
    for _ in range(46 if kind == "bianco" else 44):
        rr = R0 * 0.95 * np.sqrt(rng.uniform(0, 1))
        a = rng.uniform(0, 2 * np.pi)
        trusses.append((S / 2 + rr * np.cos(a), S / 2 + rr * np.sin(a), rng.uniform(60, 100)))
    n_leaf, n_round = 760, 3
    per_round = n_leaf // n_round
    for rnd in range(n_round):
        # foglie (il giro piu' tardo e' davanti: piu' chiaro)
        Q["_rough"] = 0.5
        for i in range(per_round):
            depth = (rnd * per_round + i) / n_leaf
            rr = R0 * np.sqrt(rng.uniform(0, 1))
            a = rng.uniform(0, 2 * np.pi)
            cx, cy = S / 2 + rr * np.cos(a), S / 2 + rr * np.sin(a)
            L = rng.uniform(120, 185)
            m, rib, side = _leaf(rng, L, L * rng.uniform(0.13, 0.17))
            base = back_c if rng.uniform() < 0.12 else leaf_c
            col = base * rng.uniform(0.78, 1.22) * (0.70 + 0.40 * depth)
            col = np.clip(col[None, None, :] * (1 + side[..., None]) + rib[..., None] * 0.12, 0, 1)
            _paint(Q, int(cy - m.shape[0] / 2), int(cx - m.shape[1] / 2), m, col,
                   0.35 + 0.35 * depth + 0.1 * rib, 0.50 + 0.40 * depth)
        # fiori: ogni giro aggiunge una parte dei corimbi (fiori anche "dentro" la chioma)
        Q["_rough"] = 0.8
        for (tx, ty, tr) in trusses[rnd::n_round] + (trusses[(rnd + 1) % n_round::n_round][:3] if rnd else []):
            nfl = int(rng.integers(13, 21))
            for k in range(nfl):
                rr = tr * np.sqrt(rng.uniform(0, 1))
                a = rng.uniform(0, 2 * np.pi)
                fx, fy = tx + rr * np.cos(a), ty + rr * np.sin(a)
                D = rng.uniform(64, 90)
                m, r = _flower(rng, D)
                depth = 0.55 + 0.45 * (rnd + k / nfl) / n_round
                base = fl_cols[int(rng.uniform() < 0.25)] if len(fl_cols) > 1 else fl_cols[0]
                shade = (0.80 + 0.20 * depth) * rng.uniform(0.92, 1.05)
                col = base[None, None, :] * shade * (1 - 0.18 * np.clip(r - 0.5, 0, 1)[..., None])
                ctr = np.clip(1 - r / 0.22, 0, 1)[..., None]
                cc = _c(C_CENTRO) if kind == "bianco" else base * 0.75
                col = np.clip(col * (1 - ctr) + cc * ctr, 0, 1)
                _paint(Q, int(fy - m.shape[0] / 2), int(fx - m.shape[1] / 2), m, col,
                       0.75 + 0.25 * depth - 0.15 * np.clip(r, 0, 1), 0.70 + 0.30 * depth)
    return Q


def make_tex_chioma(name="T_Morin_Oleandro_Chioma", seed=501):
    S = 1024
    D = np.zeros((2 * S, 2 * S, 4), np.float32)
    H = np.zeros((2 * S, 2 * S), np.float32)
    AO = np.ones((2 * S, 2 * S), np.float32)
    RO = np.ones((2 * S, 2 * S), np.float32)
    for q in range(4):     # 0,1 (riga in alto) bianco; 2,3 (riga in basso) rosa
        Q = _crown_quadrant(seed + q * 13, "bianco" if q < 2 else "rosa")
        r0, c0 = (q // 2) * S, (q % 2) * S
        D[r0:r0 + S, c0:c0 + S, :3] = Q["c"]
        D[r0:r0 + S, c0:c0 + S, 3] = Q["a"]
        H[r0:r0 + S, c0:c0 + S] = Q["h"]
        AO[r0:r0 + S, c0:c0 + S] = Q["ao"]
        RO[r0:r0 + S, c0:c0 + S] = Q["r"]
    a = D[..., 3]
    col = D[..., :3]
    bl = tp.blur(col * a[..., None], 6)
    wa = tp.blur(a, 6)[..., None]
    D[..., :3] = np.where(a[..., None] > 0.5, col, np.clip(bl / np.maximum(wa, 1e-3), 0, 1))
    n = tp.normal_dx(tp.blur(H, 1.0), 1.6)
    os.makedirs(TEXDIR, exist_ok=True)
    tp.save(D, f"{TEXDIR}/{name}_D.png")
    tp.save(n, f"{TEXDIR}/{name}_N.png")
    tp.save(mm._orm(np.clip(AO, 0, 1), RO, np.zeros_like(AO)), f"{TEXDIR}/{name}_ORM.png")
    return [name + s for s in ("_D", "_N", "_ORM")]


def make_tex_fusto(name="T_Morin_Oleandro_Fusto", seed=611, size=1024):
    """Corteccia liscia grigio-bruna con lenticelle orizzontali e venature verticali leggere."""
    base = _c((112, 102, 88))
    nz = mm._noise(size, size, 24, seed)
    vert = tp.resize(mm._noise(size, size // 16, 2, seed + 1)[:, :, None], size, size)[..., 0]
    alb = base[None, None, :] * (1 + 0.10 * nz[..., None] + 0.06 * vert[..., None])
    rng = np.random.default_rng(seed)
    h = 0.5 + 0.15 * vert
    for _ in range(900):     # lenticelle
        y, x = int(rng.integers(2, size - 2)), int(rng.integers(6, size - 6))
        w = int(rng.integers(4, 10))
        alb[y:y + 2, x - w:x + w] *= 0.78
        h[y:y + 2, x - w:x + w] -= 0.25
    alb = np.clip(alb, 0, 1)
    n, ao = mm._normal_ao(h, 2.5, 4, 1.5)
    os.makedirs(TEXDIR, exist_ok=True)
    tp.save(alb, f"{TEXDIR}/{name}_D.png")
    tp.save(n, f"{TEXDIR}/{name}_N.png")
    tp.save(mm._orm(ao, np.full_like(ao, 0.85), np.zeros_like(ao)), f"{TEXDIR}/{name}_ORM.png")
    return [name + s for s in ("_D", "_N", "_ORM")]


def make_textures():
    out = make_tex_chioma() + make_tex_fusto()
    print("texture:", out)
    return out


def build_materials():
    t = TEXDIR + "/"
    pk._pbr_material("M_Morin_Oleandro_Chioma", t + "T_Morin_Oleandro_Chioma_D.png", t + "T_Morin_Oleandro_Chioma_N.png",
                     t + "T_Morin_Oleandro_Chioma_ORM.png", alpha=True)
    pk._pbr_material("M_Morin_Oleandro_Fusto", t + "T_Morin_Oleandro_Fusto_D.png", t + "T_Morin_Oleandro_Fusto_N.png",
                     t + "T_Morin_Oleandro_Fusto_ORM.png")
    if "M_Pav_Fascia" not in bpy.data.materials:
        pk.build_materials(make_textures=False)
    return True


# =============================================================================================================
# oleandro ad alberello
# =============================================================================================================
def _cards(bm, centers, rng, n, size, crown_c, crown_r, quads, mi=1):
    """Come mm._cards ma con i quadranti dell'atlante limitati a `quads` (variante di colore)."""
    layer = bm.loops.layers.uv.verify()
    faces = []
    for i in range(n):
        c, cr = centers[rng.integers(0, len(centers))]
        d = Vector(rng.normal(0, 1, 3)).normalized()
        p = Vector(c) + d * cr * rng.uniform(0.5, 0.95)
        out = Vector(((p.x - crown_c[0]) / crown_r[0] ** 2, (p.y - crown_c[1]) / crown_r[1] ** 2,
                      (p.z - crown_c[2]) / crown_r[2] ** 2)).normalized()
        nrm = (d * 0.40 + out * 0.60 + Vector(rng.normal(0, 0.15, 3))).normalized()
        s = rng.uniform(*size)
        t1 = nrm.cross(Vector((0, 0, 1)) if abs(nrm.z) < 0.9 else Vector((1, 0, 0))).normalized()
        t2 = nrm.cross(t1)
        a = rng.uniform(0, 2 * math.pi)
        e1 = (t1 * math.cos(a) + t2 * math.sin(a)) * s / 2
        e2 = nrm.cross(e1)
        vs = [bm.verts.new(p + sx * e1 + sy * e2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        f = bm.faces.new(vs)
        f.material_index = mi
        q = quads[int(rng.integers(0, len(quads)))]
        u0, v0 = (q % 2) * 0.5, 0.5 - (q // 2) * 0.5
        for lp, (uu, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            lp[layer].uv = (u0 + 0.5 * uu, v0 + 0.5 * vv)
        faces.append((f, out))
    return faces


def build_oleandro(coll, name, lod=0):
    """v2: chioma grande, schiacciata e a lobi (forma diversa per variante), ciuffi sporgenti, card fitte; fusto Ø 12 cm."""
    quads = OL_VAR[name]
    seed, R, cz, nlobi = OL_SHAPE[name]
    rng = np.random.default_rng(seed)
    bm = bmesh.new()
    sides = (10, 7, 5)[lod]
    fusto = mm._curve((0, 0, 0), Vector((0.03, 0.015, 1)), OL_FUSTO + 0.15, 0.02, 4, rng)
    mm._branch(bm, fusto, 0.060, 0.050, sides, 0, uv_tile=(0.5, 1.0))
    top = fusto[-1]
    C = Vector((0.0, 0.0, cz))
    # lobi: sotto-ellissoidi attorno al centro, piu' larghi che alti (chioma irregolare, base piatta)
    lobi = []
    for i in range(nlobi):
        a = 2 * math.pi * i / nlobi + rng.uniform(-0.35, 0.35)
        el = rng.uniform(-0.40, 0.40)
        f = rng.uniform(0.38, 0.55)
        p = C + Vector((math.cos(a) * math.cos(el) * R[0] * f, math.sin(a) * math.cos(el) * R[1] * f, math.sin(el) * R[2] * f))
        lobi.append((p, rng.uniform(0.62, 0.85)))
    lobi.append((C + Vector((0, 0, R[2] * 0.25)), 0.85))
    # rami principali dal fusto verso i lobi
    for p, r in lobi[:(nlobi if lod < 2 else 4)]:
        d = (p - top)
        br = mm._curve(top, d, d.length * 0.8, 0.12, 3, rng)
        mm._branch(bm, br, 0.034, 0.012, max(sides - 4, 4), 0, uv_tile=(0.5, 1.0))
    # tutore (paletto) legato al fusto [S]: solo LOD0 e LOD1
    if lod < 2:
        pk._box(bm, 0.085, 0.115, -0.015, 0.015, 0.0, 2.0, 0, faces=("xn", "xp", "yn", "yp", "top"))
        for z in (0.7, 1.6):
            pk._box(bm, 0.045, 0.12, -0.022, 0.022, z, z + 0.03, 0, faces=("xn", "xp", "yn", "yp"))
    # ciuffi sulla superficie dei lobi (base dei lobi tagliata: chioma schiacciata sotto)
    centers = []
    zmin = cz - R[2] * 0.92
    for i in range(70):
        p, r = lobi[int(rng.integers(0, len(lobi)))]
        d = Vector(rng.normal(0, 1, 3)).normalized()
        q = p + d * r * rng.uniform(0.55, 0.95)
        q.z = max(q.z, zmin + rng.uniform(0, 0.15))
        centers.append((tuple(q), rng.uniform(0.30, 0.42)))
    for i in range(10):            # ciuffi sporgenti
        p, r = lobi[int(rng.integers(0, len(lobi)))]
        d = Vector(rng.normal(0, 1, 3)).normalized()
        d.z = abs(d.z) * 0.6
        centers.append((tuple(p + d * r * rng.uniform(1.05, 1.25)), rng.uniform(0.24, 0.32)))
    for i in range(8):             # nucleo scuro: niente cielo attraverso la chioma
        d = Vector(rng.normal(0, 1, 3)).normalized()
        centers.append((tuple(C + Vector((d.x * R[0] * 0.3, d.y * R[1] * 0.3, d.z * R[2] * 0.25))), 0.45))
    ncard = (1150, 520, 140)[lod]
    size = ((0.55, 0.82), (0.72, 1.05), (1.05, 1.45))[lod]
    cards = _cards(bm, centers, rng, ncard, size, tuple(C), R, quads)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = mm._finish_tree(name + sfx, bm, cards, ["M_Morin_Oleandro_Fusto", "M_Morin_Oleandro_Chioma"], coll)
    if lod == 0:
        pk._ucx(name, [(-0.08, 0.12, -0.08, 0.08, 0.0, OL_FUSTO)], coll)
    return o


# =============================================================================================================
# panchina lunga in pietra (modulo 4 m)
# =============================================================================================================
def build_panchina_lunga(coll, lod=0, name="SM_Morin_PanchinaLunga_Mod"):
    bm = bmesh.new()
    pk._panchina_bm(bm, lod=lod, **PL)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = pk._finish(name + sfx, bm, ["M_Pav_Fascia"], coll, uv="box")
    if lod == 0:
        L, W, H = PL["L"], PL["W"], PL["H"]
        pk._ucx(name, [(-L / 2, L / 2, -W / 2, W / 2, 0.0, H)], coll)
    return o


LODDED = ["SM_Morin_OleandroAlberello_Bianco", "SM_Morin_OleandroAlberello_Rosa", "SM_Morin_PanchinaLunga_Mod"]


def build_all():
    coll = pk._coll(KIT)
    out = []
    for l in range(3):
        for nm in OL_VAR:
            out.append(build_oleandro(coll, nm, l))
        out.append(build_panchina_lunga(coll, l))
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    for o in sorted(out, key=lambda o: o.name):
        print(f"{o.name:<40} tri {pk.tri_count(o):>6}  dim {tuple(round(d, 2) for d in o.dimensions)}")
    return out


# =============================================================================================================
# disposizione (coordinate Blender) e CSV in coordinate UE
# =============================================================================================================
# Panchina: tratti continui lungo il bordo dei cubetti, interrotti ai varchi del blockout v3 (aiuole Y 102-107:
# X 122-178, 182-228, 232-250) [S]: in X 250-550 tratti da 12 moduli con varchi da 4 m [S].
PL_TRATTI = [(122.0, 14), (183.0, 11), (233.0, 4)]
PL_TRATTI_B2 = [(253.0 + k * 52.0, 12) for k in range(5)] + [(513.0, 9)]


def layout():
    rows = []
    n = int(round((OL_X1 - OL_X0) / OL_PASSO)) + 1
    for i in range(n):
        x = OL_X0 + i * OL_PASSO
        a = ("SM_Morin_OleandroAlberello_Bianco", "SM_Morin_OleandroAlberello_Rosa")[i % 2]
        rows.append((a, f"Oleandro_{i:03d}", x, OL_Y, 0.0, float((i * 47) % 360)))
    k = 0
    for x0, nmod in PL_TRATTI + PL_TRATTI_B2:
        for j in range(nmod):
            rows.append(("SM_Morin_PanchinaLunga_Mod", f"PanchinaLunga_{k:03d}", x0 + 2.0 + 4.0 * j, PL_Y, ZF, 0.0))
            k += 1
    return rows


def write_csvs(rows, base="exports/giardini/giardini_posizioni_v1"):
    b1 = [r for r in rows if r[2] <= 250.0]
    b2 = [r for r in rows if r[2] > 250.0]
    return mm.write_csv(b1, base + ".csv"), mm.write_csv(b2, base + "_blocco2.csv")


def build_context(rows, name="GIARDINI_Contesto"):
    return mm.build_context(rows, name)


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in bpy.context.scene.objects}
    for o in bpy.data.collections[KIT].objects:
        o.hide_viewport = False
        o.hide_set(False)
        o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1)
        o.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.update()
    reps = []
    try:
        for nm in LODDED:
            for lod in (0, 1, 2):
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
# camera dal punto di presa stimato della foto (corridoio fra i filari, guarda verso la citta')
# =============================================================================================================
CAMS = {"CAM_Giardini_F1": ((158.2, 92.4, ZF + 1.9), 0.0, -3.5, 100.0, (1727, 446))}


def cameras():
    mm.CAMS.update(CAMS)
    coll = pk._coll("GIARDINI_Camere")
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
