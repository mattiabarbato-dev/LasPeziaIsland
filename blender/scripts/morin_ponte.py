"""morin_ponte.py — Ponte Thaon di Revel v1 (2026-11-20), al posto di SM_Blockout_Ponte.

Scheda: ref/ponte.md. Foto: ref/foto/ponte/ponte1.png (dal calpestio verso il pennone 1), ponte_verso_passegiata.png
(dal calpestio verso la passeggiata), ringhiera_ponte.png (parapetto), ref/foto/vista/strada_cheProsegue_verso_il_ponte.png (F3).
Giacitura e quote = blockout (blender/blockout_blocco1.blend, docs/decisioni.md 2026-11-18):
    asse (0,0) -> (-1,92; -70) -> (-5,2; -179); calpestio Z 0 -> 4,3 (Y 0 -> -70), 4,3 fino a Y -136,1, poi 1,30 a Y -179;
    impalcato largo 6 m (deroga §3, reale 3,6 m), 8 m agli anelli dei pennoni; pennoni in (-2,2; -80,4) e (-3,7; -128,6) fino a Z 33,5.
Tutti i pezzi sono in coordinate di progetto (origine comune, si posano in 0,0,0). Parametro t = -Y (distanza lungo il ponte).

Esegui dentro blender/arte_ponte.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_ponte as mp; importlib.reload(mp)
    mp.make_textures()      # blender/textures/ponte/ T_Ponte_{Legno,Acciaio}_{D,N,ORM} 4096, T_Ponte_Cavo 1024
    mp.build_materials()
    mp.build_all()          # SM_Ponte_{Impalcato,Parapetti,Antenne,Stralli} LOD0/1/2 + UCX in PONTE_Kit
    mp.write_csv()          # exports/ponte/ponte_posizioni_v1.csv
    mp.export_all()         # FBX in exports/ponte/
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
TEXDIR = PROJ + "/blender/textures/ponte"
KIT = "PONTE_Kit"
EXPDIR = "//../exports/ponte"

# =============================================================================================================
# geometria (blockout; [S] dove indicato)
# =============================================================================================================
Z_TOP = 4.3                     # calpestio massimo [S] (decisioni 2026-11-18)
T_RAMP = 70.0                   # fine rampa lato Revel
T_DESC = 136.1                  # inizio discesa verso Mirabello
T_END = 179.0
Z_END = 1.30
FIL = 4.0                       # semi-lunghezza dei raccordi verticali (solo visivi: scarto <= 7 cm dal blockout)
CXP = [(0.0, 0.0), (70.0, -1.92), (179.0, -5.2)]             # (t, X dell'asse)
HWP = [(0.0, 3.0), (72.9, 3.0), (75.9, 4.0), (84.9, 4.0), (87.9, 3.0),
       (121.1, 3.0), (124.1, 4.0), (133.1, 4.0), (136.1, 3.0), (179.0, 3.0)]   # (t, semi-larghezza)
MAST_T = (80.4, 128.6)
HOLE_AX, HOLE_AY = 0.85, 3.2    # foro ellittico attorno al pennone (rami da 3,15 m)
DEPTH = 0.80                    # spessore impalcato (travi 0,70 + tavolato) [V] TP
KERB_W, KERB_H = 0.10, 0.06     # cordolo d'acciaio sul bordo
FASCIA = -0.55                  # fondo della fascia verticale, poi smusso verso l'intradosso
BOT_IN = 0.35
Z_MAST_TOP = 33.5               # 35 m s.l.m. [V] con acqua a -1,5
Z_PILE_BOT = -3.0
JOINTS = (102.6, 120.6)         # giunti del concio apribile da 18 m [S] (verso il pennone 2, TP)
FENCE = (13.0, 51.0)            # recinzione sotto la rampa dove l'altezza libera e' < 2,3 m
SPALLA_M = 167.0                # spalla Mirabello da t 167 a 179 (come il blockout)
WOOD_W = 6.0                    # metri coperti dalla texture del legno (larghezza = 6 m)
STEEL_TILE = 4.0

# parapetto (ringhiera_ponte.png): piatto sagomato, verticale in basso, inclinato verso l'esterno, corrimano tondo
POST_PROF = [(-0.05, 0.0), (-0.05, 0.25), (0.17, 0.88), (0.20, 1.05)]   # (fuori, su) dal cordolo
RAIL = (0.20, 1.10, 0.05)       # corrimano: fuori, su, raggio -> sommita' a 1,21 m dal calpestio
KICK = (-0.02, 0.145, 0.085)     # tubo bianco al piede
POST_STEP = 1.5                 # passo dei montanti = traversi (TP)
POST_W, POST_T = 0.11, 0.025

# stralli: 14 coppie per pennone (9 verso l'esterno, 5 verso la campata centrale), passo 3 m [S]
STAY_D0, STAY_DP = 9.0, 3.0     # primo ancoraggio a 9 m dal pennone (fuori dall'allargamento dell'anello)
STAY_OUT = 0.95                 # ancoraggio a mensola fuori dal corrimano
STAY_N = ((9, 5), (5, 9))       # (verso Revel, verso Mirabello) per pennone
STAY_Z0, STAY_Z1 = 15.0, 29.5   # quota d'attacco sul pennone, crescente con la distanza (semi-ventaglio) [S]

MATS_I = ["M_Ponte_Legno", "M_Ponte_Acciaio", "M_Banchina_Paramento"]
LODS = {
    0: dict(step=0.75, hole_n=14, rail_sides=10, kick_sides=8, ncab=8, cab_sides=3, mast_sides=24, stay_sides=6,
            fence_dx=0.12, pile_n=32, hole_posts=14, post_skip=1),
    1: dict(step=1.5, hole_n=8, rail_sides=5, kick_sides=4, ncab=3, cab_sides=3, mast_sides=12, stay_sides=4,
            fence_dx=0.36, pile_n=16, hole_posts=10, post_skip=1),
    2: dict(step=4.5, hole_n=4, rail_sides=4, kick_sides=0, ncab=0, cab_sides=0, mast_sides=8, stay_sides=3,
            fence_dx=None, pile_n=10, hole_posts=6, post_skip=2),
}


def _interp(pts, t):
    ts = [p[0] for p in pts]
    vs = [p[1] for p in pts]
    return float(np.interp(t, ts, vs))


def cx(t):
    return _interp(CXP, t)


def hw(t):
    return _interp(HWP, t)


def z_poly(t):
    if t <= T_RAMP:
        return Z_TOP * t / T_RAMP
    if t <= T_DESC:
        return Z_TOP
    return Z_TOP + (Z_END - Z_TOP) * (t - T_DESC) / (T_END - T_DESC)


def z(t):
    """Calpestio con raccordi parabolici di +-FIL ai due cambi di pendenza (stesse quote del blockout altrove)."""
    for tk in (T_RAMP, T_DESC):
        if abs(t - tk) < FIL:
            a = (z_poly(tk - 0.01) - z_poly(tk - 1.01))
            b = (z_poly(tk + 1.01) - z_poly(tk + 0.01))
            return z_poly(tk) + a * (t - tk) + (b - a) * (t - tk + FIL) ** 2 / (4 * FIL)
    return z_poly(t)


def a_hole(t):
    for tm in MAST_T:
        u = (t - tm) / HOLE_AY
        if abs(u) < 1.0:
            return HOLE_AX * math.sqrt(max(0.0, 1.0 - u * u))
    return 0.0


def stations(step, hole_n):
    s = set(np.round(np.arange(0.0, T_END + 1e-6, step), 4).tolist())
    s |= {p[0] for p in HWP}
    s |= {0.0, T_END, SPALLA_M, FENCE[0], FENCE[1]}
    for tk in (T_RAMP, T_DESC):
        s |= set(np.round(np.linspace(tk - FIL, tk + FIL, 5 if step < 2 else 3), 4).tolist())
    for tm in MAST_T:
        s |= set(np.round(tm + HOLE_AY * np.sin(np.linspace(-math.pi / 2, math.pi / 2, hole_n + 1)), 4).tolist())
    for tj in JOINTS:
        s |= {tj - 0.15, tj + 0.15}
    out = []
    for t in sorted(s):
        if not out or t - out[-1] > 0.05:
            out.append(t)
    out[-1] = T_END
    return out


def P(t, lat, dz=0.0):
    return Vector((cx(t) + lat, -t, z(t) + dz))


# =============================================================================================================
# texture (procedurali, colori dalle foto del ponte; FFT periodiche = tileable)
# =============================================================================================================
def _aniso_noise(h, w, sx, sy, seed):
    r = np.random.default_rng(seed).standard_normal((h, w)).astype(np.float32)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi ** 2) * ((sx * fx) ** 2 + (sy * fy) ** 2))
    a = np.real(np.fft.ifft2(np.fft.fft2(r) * g)).astype(np.float32)
    return a / (a.std() + 1e-6)


def _save_set(base, D, H, R, M, nstr):
    os.makedirs(TEXDIR, exist_ok=True)
    nrm, ao = mm._normal_ao(H.astype(np.float32), nstr)
    tp.save(np.clip(D, 0, 1), f"{TEXDIR}/{base}_D.png")
    tp.save(nrm, f"{TEXDIR}/{base}_N.png")
    tp.save(mm._orm(ao, np.clip(R, 0.04, 1), M), f"{TEXDIR}/{base}_ORM.png")


def make_tex_legno(S=4096, seed=13):
    """Tavolato 6 x 6 m: 44 doghe longitudinali (13,6 cm) di legno grigio invecchiato (foto: ~118,116,112 al sole),
    fughe scure, teste sfalsate, viti sui traversi ogni 1,5 m, due file di borchie metalliche a +-1,5 m dall'asse."""
    rng = np.random.default_rng(seed)
    ppm = S / WOOD_W
    NP = 44
    pw = WOOD_W / NP
    u = (np.arange(S, dtype=np.float32) + 0.5) / ppm          # colonne: trasversale
    v = (np.arange(S, dtype=np.float32) + 0.5) / ppm          # righe: lungo il ponte
    U, V = np.meshgrid(u, v)
    pi = np.floor(U / pw).astype(np.int32) % NP
    uin = U / pw - np.floor(U / pw)                           # 0..1 dentro la doga
    nb = rng.choice([2, 3], NP)
    off = rng.uniform(0, WOOD_W, NP).astype(np.float32)
    seg = WOOD_W / nb
    vp = np.mod(V - off[pi], WOOD_W)
    bi = np.floor(vp / seg[pi]).astype(np.int32)
    vin = vp - bi * seg[pi]
    bid = pi * 4 + bi
    tint = rng.normal(1.0, 0.05, NP * 4).astype(np.float32)
    warm = rng.normal(0.0, 0.015, NP * 4).astype(np.float32)
    shift = rng.integers(0, S, NP * 4)
    G = _aniso_noise(S, S, 1.2, 60.0, seed + 1)
    G2 = _aniso_noise(S, S, 0.6, 14.0, seed + 2)
    cols = (np.arange(S)[None, :]).repeat(S, 0)
    rows = (np.arange(S)[:, None] + shift[bid]) % S
    grain = G[rows, cols] * 0.7 + G2[rows, cols] * 0.3
    del rows
    low = mm._noise(S, S, 120, seed + 3) * 0.6 + mm._noise(S, S, 25, seed + 4) * 0.4
    base = np.array([118, 110, 100], np.float32) / 255.0
    t = tint[bid] * (1 + 0.07 * grain + 0.05 * low)
    D = base[None, None, :] * t[..., None]
    D[..., 0] *= 1 + warm[bid]
    D[..., 2] *= 1 - warm[bid]
    H = 0.15 * grain - 0.35 * ((uin - 0.5) * 2) ** 2
    R = 0.80 + 0.04 * grain - 0.03 * low
    M = np.zeros((S, S), np.float32)
    # fughe (6 mm) e teste (4 mm)
    gu = np.minimum(uin, 1 - uin) * pw
    gap = gu < 0.003
    gv = np.minimum(vin, seg[pi] - vin)
    endj = gv < 0.002
    edge = np.clip(1 - gu / 0.012, 0, 1) * 0.12
    D *= (1 - edge)[..., None]
    D[gap | endj] *= 0.28
    H[gap | endj] = -1.2
    R[gap | endj] = 0.92
    # viti sui traversi: ogni 1,5 m, due per doga
    for vt in np.arange(0.0, WOOD_W, 1.5) + 0.4:
        for du in (0.28, 0.72):
            cu = (np.arange(NP) + du) * pw
            for c in cu:
                y0, x0 = int(vt * ppm), int(c * ppm)
                r = 3
                yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
                m = (yy * yy + xx * xx) <= r * r
                ys, xs = (np.arange(y0 - r, y0 + r + 1) % S), (np.arange(x0 - r, x0 + r + 1) % S)
                sub = np.ix_(ys, xs)
                d = D[sub]; d[m] *= 0.55; D[sub] = d
                h = H[sub]; h[m] -= 0.3; H[sub] = h
    # borchie a +-1,5 m (u = 1,5 e 4,5): ogni 0,30 m
    for cu in (1.5, 4.5):
        for vt in np.arange(0.15, WOOD_W, 0.30):
            y0, x0 = int(vt * ppm), int(cu * ppm)
            r = 7
            yy, xx = np.ogrid[-r - 2:r + 3, -r - 2:r + 3]
            dd = np.sqrt(yy * yy + xx * xx)
            m = dd <= r
            ring = (dd > r) & (dd <= r + 2)
            ys, xs = (np.arange(y0 - r - 2, y0 + r + 3) % S), (np.arange(x0 - r - 2, x0 + r + 3) % S)
            sub = np.ix_(ys, xs)
            d = D[sub]; d[m] = np.array([172, 172, 166], np.float32) / 255.0; d[ring] *= 0.6; D[sub] = d
            h = H[sub]; h[m] = 0.6 * (1 - (dd[m] / r) ** 2) + 0.2; H[sub] = h
            rr = R[sub]; rr[m] = 0.38; R[sub] = rr
            mt = M[sub]; mt[m] = 0.85; M[sub] = mt
    _save_set("T_Ponte_Legno", D, H, R, M, 3.0)


def make_tex_acciaio(S=4096, seed=29):
    """Acciaio verniciato bianco, 4 x 4 m: buccia d'arancia, colature grigie leggere, qualche puntino di ruggine."""
    rng = np.random.default_rng(seed)
    base = np.array([228, 230, 228], np.float32) / 255.0
    peel = mm._noise(S, S, 2.0, seed + 1)
    low = mm._noise(S, S, 90, seed + 2)
    streak = _aniso_noise(S, S, 4.0, 260.0, seed + 3)
    streak = np.clip(streak - 0.8, 0, None)
    dirt = 0.025 * np.clip(low, -2, 2) + 0.04 * streak
    D = base[None, None, :] * (1 - dirt)[..., None]
    D[..., 2] *= 1 - 0.25 * dirt                   # sporco leggermente caldo
    H = 0.25 * peel + 0.2 * mm._noise(S, S, 0.8, seed + 4)
    R = 0.40 + 0.05 * peel * 0.3 + 0.12 * np.clip(streak, 0, 1) + 0.03 * low
    M = np.zeros((S, S), np.float32)
    for _ in range(70):
        y0, x0 = rng.integers(0, S, 2)
        r = int(rng.integers(2, 6))
        yy, xx = np.ogrid[-r * 3:r * 3 + 1, -r * 3:r * 3 + 1]
        dd = np.sqrt(yy * yy + xx * xx)
        ys, xs = (np.arange(y0 - r * 3, y0 + r * 3 + 1) % S), (np.arange(x0 - r * 3, x0 + r * 3 + 1) % S)
        sub = np.ix_(ys, xs)
        core = dd <= r
        halo = np.clip(1 - (dd - r) / (2 * r), 0, 1) * (dd > r)
        d = D[sub]
        d[core] = np.array([120, 78, 52], np.float32) / 255.0
        d *= (1 - 0.12 * halo)[..., None]
        D[sub] = d
        rr = R[sub]; rr[core] = 0.85; R[sub] = rr
        h = H[sub]; h[core] += 0.5; H[sub] = h
    _save_set("T_Ponte_Acciaio", D, H, R, M, 1.5)


def make_tex_cavo(S=1024, seed=31):
    """Fune spiroidale chiusa: fili inclinati grigio acciaio (u attorno, v lungo)."""
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    ph = (x + y * 0.6) / S * 2 * np.pi * 24
    s = 0.5 + 0.5 * np.sin(ph)
    n = mm._noise(S, S, 3, seed)
    D = (np.array([188, 190, 192], np.float32) / 255.0)[None, None, :] * (0.85 + 0.15 * s + 0.03 * n)[..., None]
    H = s * 0.8
    R = 0.32 + 0.1 * (1 - s) + 0.03 * n
    M = np.full((S, S), 0.6, np.float32)
    _save_set("T_Ponte_Cavo", D, H, R, M, 2.0)


def make_textures():
    make_tex_legno()
    make_tex_acciaio()
    make_tex_cavo()
    return sorted(os.listdir(TEXDIR))


def build_materials():
    t = TEXDIR + "/"
    for m, b in (("M_Ponte_Legno", "T_Ponte_Legno"), ("M_Ponte_Acciaio", "T_Ponte_Acciaio"), ("M_Ponte_Cavo", "T_Ponte_Cavo")):
        pk._pbr_material(m, t + b + "_D.png", t + b + "_N.png", t + b + "_ORM.png")
    if not any(m.name == "M_Banchina_Paramento" and m.library is None for m in bpy.data.materials):
        c = pk.TEXDIR + "/T_Banchina_Paramento"
        pk._pbr_material("M_Banchina_Paramento", c + "_D.png", c + "_N.png", c + "_ORM.png")
    return True


# =============================================================================================================
# utilita'
# =============================================================================================================
def _face(bm, vs, mi, want):
    try:
        f = bm.faces.new(vs)
    except ValueError:
        return None
    f.material_index = mi
    f.normal_update()
    if want is not None and f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def _box_world(bm, c, ax, ay, az, hx, hy, hz, mi):
    """Parallelepipedo con assi (ax, ay, az) e semi-lati; normali verso l'esterno."""
    c, ax, ay, az = Vector(c), Vector(ax), Vector(ay), Vector(az)
    V = {}
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                V[i, j, k] = bm.verts.new(c + ax * hx * i + ay * hy * j + az * hz * k)
    quads = [((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)), ((-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)),
             ((-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)), ((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)),
             ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)), ((-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1))]
    out = []
    for q in quads:
        n = Vector(q[0]) + Vector(q[2])
        want = ax * n.x + ay * n.y + az * n.z
        out.append(_face(bm, [V[k] for k in q], mi, want))
    return out


def _bar(bm, p0, p1, w, d, mi, side_dir=None):
    """Barra a sezione rettangolare da p0 a p1 (w lungo side_dir, d nell'altra direzione), senza tappi."""
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0)
    L = ax.length
    ax.normalize()
    s = Vector(side_dir) if side_dir is not None else Vector((1, 0, 0))
    s = (s - ax * s.dot(ax)).normalized()
    o = ax.cross(s)
    c = (p0 + p1) / 2
    fs = _box_world(bm, c, s, o, ax, w / 2, d / 2, L / 2, mi)
    for f in fs[4:]:
        if f is not None:
            bm.faces.remove(f)


def _uv(bm, mats, wood_fn=None):
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        m = mats[f.material_index]
        if m == "M_Ponte_Legno" and wood_fn is not None:
            for lp in f.loops:
                lp[uvl].uv = wood_fn(lp.vert.co)
            continue
        tile = STEEL_TILE if m != "M_Ponte_Cavo" else 0.5
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for lp in f.loops:
            c = lp.vert.co
            if ax == 2:
                uv = (c.x, c.y)
            elif ax == 0:
                uv = (c.y, c.z)
            else:
                uv = (c.x, c.z)
            lp[uvl].uv = (uv[0] / tile, uv[1] / tile)


def _wood_uv(co):
    t = -co.y
    return ((co.x - cx(t)) / WOOD_W + 0.5, t / WOOD_W)


def _tube(bm, pts, r, sides, mi, cap=True):
    pk._tube(bm, [tuple(p) for p in pts], r, sides, mi, cap=cap)


def _write(name, bm, mats, coll, wood=False):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.normal_update()
    _uv(bm, mats, _wood_uv if wood else None)
    o = pk._finish(name, bm, mats, coll, uv=None, smooth_angle=35.0)
    me = o.data
    for l in [l for l in me.uv_layers if l.name != "UVMap"]:
        me.uv_layers.remove(l)
    return o


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


# =============================================================================================================
# impalcato: tavolato, cordoli, fascia, intradosso, fori ai pennoni, giunti, mensole degli stralli,
# pile a scafo, spalla Mirabello, recinzione sotto la rampa
# =============================================================================================================
def _deck(bm, L):
    ts = stations(L["step"], L["hole_n"])
    prof = lambda t: [(a_hole(t), 0.0), (hw(t) - KERB_W, 0.0), (hw(t) - KERB_W, KERB_H), (hw(t), KERB_H),
                      (hw(t), FASCIA), (hw(t) - BOT_IN, -DEPTH), (a_hole(t), -DEPTH)]
    for side in (-1, 1):
        rows = []
        for t in ts:
            pts = []
            for lat, dz in prof(t):
                p = P(t, side * lat, dz)
                if dz < 0:
                    p.z = max(p.z, -0.05)
                pts.append(bm.verts.new(p))
            rows.append(pts)
        wants = [(0, 0, 1), (-side, 0, 0), (0, 0, 1), (side, 0, 0), (side, 0, -1), (0, 0, -1)]
        for i in range(len(ts) - 1):
            A, B = rows[i], rows[i + 1]
            tm = (ts[i] + ts[i + 1]) / 2
            for k in range(6):
                mi = 0 if k == 0 else 1
                if k == 0 and any(abs(tm - tj) < 0.15 for tj in JOINTS):
                    mi = 1
                _face(bm, [A[k], A[k + 1], B[k + 1], B[k]], mi, wants[k])
            if a_hole(ts[i]) > 1e-4 or a_hole(ts[i + 1]) > 1e-4:
                _face(bm, [A[6], A[0], B[0], B[6]], 1, (-side, 0, 0))
        for idx, want in ((0, (0, 1, 0)), (-1, (0, -1, 0))):
            vs = rows[idx]
            if (vs[0].co - vs[6].co).length > 1e-3 or True:
                _face(bm, list(vs), 1, want)
    return ts


def _brackets(bm):
    for tm, (n_rev, n_mir) in zip(MAST_T, STAY_N):
        for d, n in ((+1, n_rev), (-1, n_mir)):
            for k in range(n):
                ta = tm - d * (STAY_D0 + STAY_DP * k)
                for side in (-1, 1):
                    h = hw(ta)
                    c = P(ta, side * (h + STAY_OUT / 2 + 0.05), -0.25)
                    _box_world(bm, c, (side, 0, 0), (0, 1, 0), (0, 0, 1), STAY_OUT / 2 + 0.05, 0.09, 0.10, 1)


def _joint_ribs(bm):
    for tj in JOINTS:
        for side in (-1, 1):
            h = hw(tj)
            c = P(tj, side * (h + 0.015), (FASCIA + KERB_H) / 2)
            _box_world(bm, c, (side, 0, 0), (0, 1, 0), (0, 0, 1), 0.02, 0.10, (KERB_H - FASCIA) / 2 + 0.01, 1)


def _pile(bm, tm, n):
    """Pila a scafo stilizzato (TP): 8 x 3 m in pianta, appuntita alle due estremita', svasata verso l'alto."""
    x0, y0 = cx(tm), -tm
    ztop = Z_TOP - DEPTH + 0.02
    levels = [(Z_PILE_BOT, 0.80), (-1.0, 0.86), (0.8, 0.92), (2.2, 0.97), (ztop, 1.0)]
    rings = []
    for zz, sc in levels:
        ring = []
        for i in range(n):
            th = 2 * math.pi * i / n
            cs, sn = math.cos(th), math.sin(th)
            ly = 4.0 * sc * (abs(cs) ** 0.75) * (1 if cs >= 0 else -1)
            lx = 1.5 * sc * (abs(sn) ** 0.55) * (1 if sn >= 0 else -1)
            ring.append(bm.verts.new((x0 + lx, y0 + ly, zz)))
        rings.append(ring)
    for A, B in zip(rings[:-1], rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            c = (A[i].co + B[j].co) / 2
            _face(bm, [A[i], A[j], B[j], B[i]], 1, (c.x - x0, c.y - y0, 0))
    _face(bm, rings[-1], 1, (0, 0, 1))


def _spalla_m(bm):
    t0, t1 = SPALLA_M, T_END
    h = 3.25
    zb = -2.5
    V = {}
    for t in (t0, t1):
        for s in (-1, 1):
            p = P(t, s * h)
            V[t, s, 0] = bm.verts.new((p.x, p.y, zb))
            V[t, s, 1] = bm.verts.new((p.x, p.y, z(t) - DEPTH + 0.02))
    _face(bm, [V[t0, -1, 0], V[t0, 1, 0], V[t0, 1, 1], V[t0, -1, 1]], 2, (0, 1, 0))
    _face(bm, [V[t1, -1, 0], V[t1, 1, 0], V[t1, 1, 1], V[t1, -1, 1]], 2, (0, -1, 0))
    for s in (-1, 1):
        _face(bm, [V[t0, s, 0], V[t1, s, 0], V[t1, s, 1], V[t0, s, 1]], 2, (s, 0, 0))
    _face(bm, [V[t0, -1, 1], V[t0, 1, 1], V[t1, 1, 1], V[t1, -1, 1]], 2, (0, 0, 1))


def _fence(bm, L):
    """Recinzione bianca a montanti sotto la rampa (F3: 'cancello/recinzione bianca a montanti ai lati')."""
    t0, t1 = FENCE
    dx = L["fence_dx"]
    for side in (-1, 1):
        lat = side * (hw(t0) - BOT_IN - 0.08)
        if dx is None:
            ts = np.linspace(t0, t1, 9)
            for a, b in zip(ts[:-1], ts[1:]):
                pa, pb = P(a, lat), P(b, lat)
                va = [bm.verts.new((pa.x, pa.y, 0.0)), bm.verts.new((pb.x, pb.y, 0.0)),
                      bm.verts.new((pb.x, pb.y, z(b) - DEPTH)), bm.verts.new((pa.x, pa.y, z(a) - DEPTH))]
                _face(bm, va, 1, (side, 0, 0))
            continue
        for t in np.arange(t0, t1, dx):
            p = P(t, lat)
            top = z(t) - DEPTH
            if top < 0.1:
                continue
            _bar(bm, (p.x, p.y, 0.0), (p.x, p.y, top), 0.05, 0.015, 1, side_dir=(0, 1, 0))
        for zz in (0.12,):
            pa, pb = P(t0, lat), P(t1, lat)
            _bar(bm, (pa.x, pa.y, zz), (pb.x, pb.y, zz), 0.06, 0.04, 1, side_dir=(0, 0, 1))
    # chiusura trasversale a t1
    h = hw(t1) - BOT_IN - 0.08
    top = z(t1) - DEPTH
    if dx is None:
        a, b = P(t1, -h), P(t1, h)
        va = [bm.verts.new((a.x, a.y, 0.0)), bm.verts.new((b.x, b.y, 0.0)), bm.verts.new((b.x, b.y, top)), bm.verts.new((a.x, a.y, top))]
        _face(bm, va, 1, (0, -1, 0))
    else:
        for l in np.arange(-h, h + 1e-6, dx):
            p = P(t1, l)
            _bar(bm, (p.x, p.y, 0.0), (p.x, p.y, top), 0.05, 0.015, 1, side_dir=(1, 0, 0))


def build_impalcato(coll, lod=0):
    L = LODS[lod]
    bm = bmesh.new()
    _deck(bm, L)
    if lod < 2:
        _brackets(bm)
        _joint_ribs(bm)
    for tm in MAST_T:
        _pile(bm, tm, L["pile_n"])
    _spalla_m(bm)
    _fence(bm, L)
    return _write("SM_Ponte_Impalcato" + _sfx(lod), bm, MATS_I, coll, wood=True)


# =============================================================================================================
# parapetti: montanti a piatto sagomato, corrimano, cavi orizzontali, tubo al piede; ringhiere attorno ai fori
# =============================================================================================================
def _post(bm, pts3, tang, mi=0):
    """Piatto sagomato lungo la polilinea pts3 (nel piano trasversale), larghezza POST_W, spessore POST_T lungo tang."""
    T = Vector(tang).normalized()
    pts = [Vector(p) for p in pts3]
    rings = []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        D = (b - a).normalized()
        N = D.cross(T).normalized()
        rings.append([bm.verts.new(p + N * sx * POST_W / 2 + T * sy * POST_T / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for A, B, pa, pb in zip(rings[:-1], rings[1:], pts[:-1], pts[1:]):
        c = (pa + pb) / 2
        for k in range(4):
            j = (k + 1) % 4
            fc = (A[k].co + A[j].co + B[j].co + B[k].co) / 4
            _face(bm, [A[k], A[j], B[j], B[k]], mi, fc - c)
    _face(bm, rings[0], mi, pts[0] - pts[1])
    _face(bm, rings[-1], mi, pts[-1] - pts[-2])


def _prof_out(up):
    """Sporgenza del parapetto alla quota `up` (interpolazione sul profilo del montante)."""
    ups = [p[1] for p in POST_PROF]
    outs = [p[0] for p in POST_PROF]
    return float(np.interp(up, ups, outs))


def post_ts():
    brk = [p[0] for p in HWP[1:-1]]
    reg = list(np.arange(0.6, T_END - 0.05, POST_STEP))
    ts = [t for t in reg if all(abs(t - b) > 0.6 for b in brk)] + brk + [T_END - 0.08]
    return sorted(ts)


def _edge_pt(t, side, out, up):
    return P(t, side * (hw(t) + out), KERB_H + up)


def _rails(bm, L):
    brk = {p[0] for p in HWP[1:-1]}
    ts = [t for i, t in enumerate(post_ts()) if i % L["post_skip"] == 0 or t in brk or i == len(post_ts()) - 1]
    for side in (-1, 1):
        for t in ts:
            t2 = min(t + 0.3, T_END)
            t1 = max(t - 0.3, 0.0)
            tang = P(t2, side * hw(t2)) - P(t1, side * hw(t1))
            tang.z = 0
            _post(bm, [_edge_pt(t, side, o, u) for o, u in POST_PROF], tang, 0)
        # corrimano (con terminale ricurvo all'imbocco, QA 2026-11-18)
        o, u, r = RAIL
        path = []
        R0 = 0.55
        t_first = ts[0]
        for k in range(7, 0, -1):
            ph = math.pi / 2 * k / 7
            path.append(_edge_pt(t_first - R0 * math.sin(ph), side, o, u - R0 + R0 * math.cos(ph)))
        path.insert(0, _edge_pt(t_first - R0, side, o, 0.05))
        path += [_edge_pt(t, side, o, u) for t in ts]
        _tube(bm, path, r, L["rail_sides"], 0)
        # tubo al piede
        if L["kick_sides"]:
            o, u, r = KICK
            _tube(bm, [_edge_pt(t, side, o, u) for t in ts], r, L["kick_sides"], 0)
        # cavi
        for i in range(L["ncab"]):
            up = 0.32 + (1.00 - 0.32) * i / max(1, (L["ncab"] - 1))
            ou = _prof_out(up) + 0.0
            _tube(bm, [_edge_pt(t, side, ou, up) for t in ts], 0.006, L["cab_sides"], 1, cap=False)


def _hole_rails(bm, L):
    for tm in MAST_T:
        x0, y0 = cx(tm), -tm
        n = L["hole_posts"]
        ax, ay = HOLE_AX + 0.10, HOLE_AY + 0.10

        def ept(th, up):
            return Vector((x0 + ax * math.cos(th), y0 + ay * math.sin(th), Z_TOP + up))
        for i in range(n):
            th = 2 * math.pi * (i + 0.5) / n
            tang = Vector((-ax * math.sin(th), ay * math.cos(th), 0))
            _post(bm, [ept(th, 0.0), ept(th, 1.05)], tang, 0)
        m = max(n * 3, 16)
        loop = lambda up: [ept(2 * math.pi * k / m, up) for k in range(m + 1)]
        _tube(bm, loop(1.10), RAIL[2], L["rail_sides"], 0, cap=False)
        if L["kick_sides"]:
            _tube(bm, loop(0.10), 0.06, L["kick_sides"], 0, cap=False)
        for i in range(max(0, L["ncab"] - 2)):
            up = 0.30 + 0.70 * i / max(1, L["ncab"] - 3)
            _tube(bm, loop(up), 0.006, L["cab_sides"], 1, cap=False)


def build_parapetti(coll, lod=0):
    L = LODS[lod]
    bm = bmesh.new()
    _rails(bm, L)
    _hole_rails(bm, L)
    return _write("SM_Ponte_Parapetti" + _sfx(lod), bm, ["M_Ponte_Acciaio", "M_Ponte_Cavo"], coll)


# =============================================================================================================
# antenne (pennoni): sezione ellittica rastremata, punta affusolata
# =============================================================================================================
MAST_RINGS = [(Z_TOP - DEPTH, 0.70, 0.45), (Z_TOP, 0.70, 0.45), (Z_TOP, 0.78, 0.52), (Z_TOP + 0.35, 0.78, 0.52),
              (Z_TOP + 0.35, 0.69, 0.445)] + [(z_, 0.69 - (0.69 - 0.28) * (z_ - 4.65) / (30.5 - 4.65),
                                                0.445 - (0.445 - 0.18) * (z_ - 4.65) / (30.5 - 4.65))
                                               for z_ in (8.0, 12.0, 16.0, 20.0, 24.0, 28.0, 30.5)] + \
             [(31.5, 0.20, 0.13), (32.5, 0.09, 0.06), (33.3, 0.025, 0.018), (Z_MAST_TOP, 0.0, 0.0)]


def mast_r(zz):
    zs = [r[0] for r in MAST_RINGS[4:]]
    return (float(np.interp(zz, zs, [r[1] for r in MAST_RINGS[4:]])), float(np.interp(zz, zs, [r[2] for r in MAST_RINGS[4:]])))


def build_antenne(coll, lod=0):
    L = LODS[lod]
    n = L["mast_sides"]
    bm = bmesh.new()
    rings_def = MAST_RINGS if lod == 0 else [MAST_RINGS[0]] + MAST_RINGS[4:]
    for tm in MAST_T:
        x0, y0 = cx(tm), -tm
        rings = []
        for zz, ry, rx in rings_def:
            if ry <= 0:
                rings.append([bm.verts.new((x0, y0, zz))])
            else:
                rings.append([bm.verts.new((x0 + rx * math.sin(2 * math.pi * k / n), y0 + ry * math.cos(2 * math.pi * k / n), zz))
                              for k in range(n)])
        for A, B in zip(rings[:-1], rings[1:]):
            for k in range(n):
                j = (k + 1) % n
                if len(B) == 1:
                    vs = [A[k], A[j], B[0]]
                    c = (A[k].co + A[j].co) / 2
                else:
                    vs = [A[k], A[j], B[j], B[k]]
                    c = (A[k].co + A[j].co + B[j].co + B[k].co) / 4
                if len({v.index for v in vs}) < len(vs) or (len(B) > 1 and (A[k].co - B[k].co).length < 1e-6):
                    pass
                _face(bm, vs, 0, (c.x - x0, c.y - y0, 0.0001))
        _face(bm, rings[0], 0, (0, 0, -1))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    return _write("SM_Ponte_Antenne" + _sfx(lod), bm, ["M_Ponte_Acciaio"], coll)


# =============================================================================================================
# stralli
# =============================================================================================================
def stays():
    """[(A deck, M mast)]: 2 pennoni x 14 coppie (9 verso l'esterno, 5 verso la campata centrale) = 56 funi [S]."""
    out = []
    dmax = STAY_D0 + STAY_DP * (max(max(n) for n in STAY_N) - 1)
    for tm, (n_rev, n_mir) in zip(MAST_T, STAY_N):
        for d, n in ((+1, n_rev), (-1, n_mir)):
            for k in range(n):
                off = STAY_D0 + STAY_DP * k
                ta = tm - d * off
                zm = STAY_Z0 + (STAY_Z1 - STAY_Z0) * (off - STAY_D0) / (dmax - STAY_D0)
                ry, rx = mast_r(zm)
                for side in (-1, 1):
                    A = P(ta, side * (hw(ta) + STAY_OUT), -0.22)
                    M = Vector((cx(tm) + side * rx * 0.8, -tm + d * ry * 0.45, zm))
                    out.append((A, M, side, d))
    return out


def check_stays():
    """Distanza minima orizzontale fra ogni strallo e il corrimano (deve restare > 0,1 m)."""
    worst = 99.0
    for A, M, side, d in stays():
        for s in np.linspace(0, 0.3, 200):
            p = A + (M - A) * s
            t = -p.y
            if t < 0 or t > T_END:
                continue
            up = p.z - z(t) - KERB_H
            if up < 0 or up > RAIL[1] + 0.1:
                continue
            lat_rail = hw(t) + _prof_out(min(up, 1.05)) + (RAIL[2] if up > 1.0 else POST_W / 2)
            lat = side * (p.x - cx(t))
            worst = min(worst, lat - lat_rail)
    return worst


def build_stralli(coll, lod=0):
    L = LODS[lod]
    bm = bmesh.new()
    for A, M, side, d in stays():
        D = (M - A).normalized()
        if lod < 2:
            _tube(bm, [A, A + D * 0.9], 0.055, L["stay_sides"], 0)
            _tube(bm, [M - D * 0.6, M], 0.045, L["stay_sides"], 0)
        _tube(bm, [A + D * (0.85 if lod < 2 else 0.0), M - D * (0.55 if lod < 2 else 0.0)], 0.026, L["stay_sides"], 0)
    o = _write("SM_Ponte_Stralli" + _sfx(lod), bm, ["M_Ponte_Cavo"], coll)
    return o


# =============================================================================================================
# collisioni UCX (solo convessi semplici)
# =============================================================================================================
def _slab_pts(t0, t1, lat0, lat1, dz0, dz1, poly=True):
    zf = z_poly if poly else z
    pts = []
    for t in (t0, t1):
        for lat in (lat0, lat1):
            for dz in (dz0, dz1):
                pts.append((cx(t) + lat, -t, zf(t) + dz))
    return pts


def _deck_segments():
    br = [0.0, 51.0, T_RAMP] + [p[0] for p in HWP[1:-1]] + [SPALLA_M, T_END]
    return sorted(set(br))


def build_ucx(coll):
    # impalcato
    i = 0
    for t0, t1 in zip(_deck_segments()[:-1], _deck_segments()[1:]):
        pts = []
        for t in (t0, t1):
            h = hw(t)
            zt = z_poly(t)
            if t1 <= 51.0:
                zb = -0.10                                          # rampa piena fino al molo (recinzione)
            elif t0 >= SPALLA_M:
                zb = -2.5                                           # spalla Mirabello
            else:
                zb = zt - DEPTH
            for s in (-1, 1):
                pts += [(cx(t) + s * h, -t, zt), (cx(t) + s * h, -t, zb)]
        pk._ucx_hull("SM_Ponte_Impalcato", i, pts, coll)
        i += 1
    for tm in MAST_T:                                               # pile
        x0, y0 = cx(tm), -tm
        pts = [(x0 + sx * 1.5, y0 + sy * 4.0, zz) for sx in (-1, 1) for sy in (-1, 1) for zz in (Z_PILE_BOT, Z_TOP - DEPTH)]
        pk._ucx_hull("SM_Ponte_Impalcato", i, pts, coll)
        i += 1
    # parapetti: una lastra per lato e per tratto, dal cordolo a 1,2 m
    i = 0
    segs = [0.0, T_RAMP] + [p[0] for p in HWP[1:-1]] + [T_END]
    segs = sorted(set(segs))
    for side in (-1, 1):
        for t0, t1 in zip(segs[:-1], segs[1:]):
            pts = []
            for t in (t0, t1):
                for lat in (hw(t) - 0.10, hw(t) + RAIL[0] + RAIL[2]):
                    for up in (0.0, KERB_H + RAIL[1] + RAIL[2]):
                        pts.append((cx(t) + side * lat, -t, z_poly(t) + up))
            pk._ucx_hull("SM_Ponte_Parapetti", i, pts, coll)
            i += 1
    for tm in MAST_T:                                               # ringhiere dei fori (prisma ellittico)
        x0, y0 = cx(tm), -tm
        pts = [(x0 + (HOLE_AX + 0.15) * math.cos(a), y0 + (HOLE_AY + 0.15) * math.sin(a), Z_TOP + up)
               for a in np.linspace(0, 2 * math.pi, 16, endpoint=False) for up in (0.0, 1.16)]
        pk._ucx_hull("SM_Ponte_Parapetti", i, pts, coll)
        i += 1
    # antenne
    for j, tm in enumerate(MAST_T):
        x0, y0 = cx(tm), -tm
        pts = []
        for zz, ry, rx in (MAST_RINGS[0], MAST_RINGS[7], MAST_RINGS[-4]):
            pts += [(x0 + rx * math.sin(a), y0 + ry * math.cos(a), zz) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        pts.append((x0, y0, Z_MAST_TOP))
        pk._ucx_hull("SM_Ponte_Antenne", j, pts, coll)


# =============================================================================================================
# insieme
# =============================================================================================================
PIECES = ("SM_Ponte_Impalcato", "SM_Ponte_Parapetti", "SM_Ponte_Antenne", "SM_Ponte_Stralli")


def build_all():
    coll = pk._coll(KIT)
    out = []
    for lod in range(3):
        out.append(build_impalcato(coll, lod))
        out.append(build_parapetti(coll, lod))
        out.append(build_antenne(coll, lod))
        out.append(build_stralli(coll, lod))
    build_ucx(coll)
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    return report()


def report():
    rows = []
    tot = [0, 0, 0]
    for nm in PIECES:
        r = [nm]
        for lod in range(3):
            o = bpy.data.objects.get(nm + _sfx(lod))
            n = pk.tri_count(o) if o else 0
            tot[lod] += n
            r.append(n)
        o = bpy.data.objects[nm]
        r.append(tuple(round(d, 2) for d in o.dimensions))
        r.append(len([u for u in bpy.data.objects if u.name.startswith("UCX_" + nm + "_")]))
        rows.append(r)
    rows.append(["TOTALE"] + tot)
    for r in rows:
        print(r)
    return rows


def write_csv(path="exports/ponte/ponte_posizioni_v1.csv"):
    rows = [(nm, nm[3:], 0.0, 0.0, 0.0, 0.0) for nm in PIECES]
    return mm.write_csv(rows, path)


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
        for nm in PIECES:
            for lod in (0, 1, 2):
                on = nm + _sfx(lod)
                r = morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="scene",
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
# contesto e camere per i confronti
# =============================================================================================================
def link_context():
    out = []
    libs = ((PROJ + "/blender/arte_molo.blend", ["CTX_Contesto", "MOLO_Contesto"], ["REF_Acqua2"]),
            (PROJ + "/blender/arte_imbarco.blend", ["VIALE_CtxFondale", "IMBARCO_Contesto"], []))
    for path, colls, objs in libs:
        need_c = [c for c in colls if c not in bpy.data.collections]
        need_o = [o for o in objs if o not in bpy.data.objects]
        if need_c or need_o:
            with bpy.data.libraries.load(path, link=True) as (src, dst):
                dst.collections = [c for c in src.collections if c in need_c]
                dst.objects = [o for o in src.objects if o in need_o]
        for c in colls:
            cc = bpy.data.collections.get(c)
            if cc is not None and cc.name not in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.link(cc)
                out.append(c)
        for o in objs:
            oo = bpy.data.objects.get(o)
            if oo is not None and oo.name not in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.link(oo)
    # il blockout del ponte resta collegato ma escluso dal layer (non cancellato)
    def find(lc, name):
        if lc.name == name:
            return lc
        for ch in lc.children:
            r = find(ch, name)
            if r:
                return r
    for nm in ("CTX_Blockout_Ponte",):
        lc = find(bpy.context.view_layer.layer_collection, nm)
        if lc is not None:
            lc.exclude = True
    return out


CAMS = {
    # nome: (posizione, azimut (gradi da +Y verso +X), pitch, FOV orizzontale, risoluzione)
    "CAM_Ponte_F1": ((-1.2, -43.0, 2.6 + 1.65), 180.0, 4.0, 62.0, (628, 762)),        # ponte1.png, dal calpestio verso il pennone 1
    "CAM_Ponte_F2": ((-3.0, -114.0, Z_TOP + 1.6), 0.0, 6.0, 84.0, (801, 804)),         # ponte_verso_passegiata.png
    "CAM_Ponte_Partenza": ((240.0, 84.0, 1.8), 0.0, 4.0, 70.0, (1600, 900)),           # dalla partenza (linea di vista §3)
}


def cameras():
    mm.CAMS.update(CAMS)
    coll = pk._coll("PONTE_Camere")
    out = []
    for name, (pos, az, pitch, fov, res) in CAMS.items():
        cam = bpy.data.objects.get(name)
        if cam is None:
            cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
            coll.objects.link(cam)
        cam.location = pos
        if name == "CAM_Ponte_Partenza":
            tgt = Vector((-3.0, -104.0, 18.0))
            fwd = (tgt - Vector(pos)).normalized()
        else:
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


FOTO = {"CAM_Ponte_F1": PROJ + "/ref/foto/ponte/ponte1.png",
        "CAM_Ponte_F2": PROJ + "/ref/foto/ponte/ponte_verso_passegiata.png",
        "CAM_Molo_F3": PROJ + "/ref/foto/vista/strada_cheProsegue_verso_il_ponte.png"}


def render_confronto(cam, out, width=None):
    """Foto e render affiancati (stessa altezza)."""
    tmp = os.path.join(os.environ.get("TEMP", PROJ), f"morin_ponte_{cam}.png")
    a = tp.load(FOTO[cam])[..., :3]
    mm.render(cam, tmp, width=width or a.shape[1])
    b = tp.load(tmp)[..., :3]
    if b.shape[0] != a.shape[0]:
        b = tp.resize(b, int(round(b.shape[1] * a.shape[0] / b.shape[0])), a.shape[0])
    sep = np.ones((a.shape[0], 6, 3), np.float32)
    tp.save(np.concatenate([a, sep, b], 1), f"{PROJ}/{out}")
    return out
