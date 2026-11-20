"""morin_imbarco.py — imbarco dei battelli del Blocco 1 (v1, 2026-11-20).

Asset (nomi nuovi):
  SM_Morin_Battello        battello turistico a due ponti, 32 x 7 m [S], scafo bianco con fascia blu, tuga finestrata,
                           ponte superiore aperto con parapetti pieni, panche e salvagenti, timoniera, scala di poppa,
                           nome di fantasia "STELLA DEL GOLFO". Origine sulla linea di galleggiamento al centro dello scafo,
                           +X = prua, +Y = murata verso il pontile. Si posa a Z -1,0 (acqua).
  SM_Morin_PontileImbarco  pontile d'imbarco a X 70,5-73,5, da Y 80,2 (ciglio) a Y 51,7: piattaforma di radice a quota
                           banchina (X 70,5-77,5), rampa, impalcato in legno su travi e pali d'acciaio (ref/banchina.md §1,
                           La Nazione 11-01-2026: pontile su tubi d'acciaio, non galleggiante), ringhiera sul lato marina,
                           bittini e bottazzo in gomma sul lato battello. Origine sul ciglio all'asse del pontile (X 72).
  SM_Morin_Biglietteria    chiosco 3 x 2 m [S] sulla piattaforma di radice, senza marchi (insegna "BIGLIETTERIA").
  SM_Morin_Cestino         cestino in lamiera a doghe verde scuro su colonnina [S].
  SM_Morin_Rastrelliera    portabici "a onda" in tubo zincato, 2,4 m, 5 posti [S].
  SM_Banchina_Parabordo    parabordo verticale in gomma a D sul paramento, X 55-90 (ref/banchina.md §3) [S].

Materiali: M_Morin_Imbarco (atlante 2048, 4 x 4 celle a tinta con rumore, UV per faccia dentro la cella) e
M_Morin_Imbarco_Legno (tavolato 2048 ripetibile, UV mondo). Testi in geometria (font di Blender).

Esegui dentro blender/arte_imbarco.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_imbarco as mi; importlib.reload(mi)
    mi.make_textures(); mi.build_materials(); mi.build_all(); mi.write_csv(); mi.build_context(); mi.export_all()

Convenzioni: Blender in metri, CSV in coordinate UE (X*100, -Y*100, Z*100), yaw UE = -rotZ Blender.
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
TEXDIR = PROJ + "/blender/textures/imbarco"
KIT = "IMBARCO_Kit"
EXPDIR = "//../exports/imbarco"
MAT_A, MAT_W = "M_Morin_Imbarco", "M_Morin_Imbarco_Legno"
NAME = "STELLA DEL GOLFO"          # nome di fantasia (CLAUDE.md §5)

# ---- atlante: celle 4 x 4 (colonna, riga dal basso) ---------------------------------------------------------------
C = dict(BIANCO=(0, 0), BLU=(1, 0), ROSSO=(2, 0), VETRO=(3, 0),
         PONTE=(0, 1), ACCIAIO=(1, 1), GOMMA=(2, 1), DOGHE=(3, 1),
         ANTIVEG=(0, 2), SCURO=(1, 2), PANNELLO=(2, 2), TEAK=(3, 2),
         RUGGINE=(0, 3), LETTERE=(1, 3), CREMA=(2, 3), GRIGIO=(3, 3))
CELL_PX, ATLAS = 512, 2048
INSET = 10 / ATLAS

# ---- posa (coordinate progetto, metri) ---------------------------------------------------------------------------
YAW_BANCHINA = 0.1241   # yaw UE dei moduli banchina (morin_banchina_v2.YAW_UE)
Z_ACQUA = -1.0          # ref/sezione.md


def ciglio_y(x):
    """Y Blender del ciglio dei moduli banchina v2 (morin_banchina_v2.line_ue)."""
    return -(-8036.16 + 0.0021664 * x * 100) / 100.0


PONT_X = 72.0
PONT_ORIG = (PONT_X, ciglio_y(PONT_X), 0.0)
BATT_POS = (66.56, 62.0, Z_ACQUA)      # centro scafo; 66,7 -> 66,56 (2026-11-20): in UEFN i parabordi toccavano il pontile, X 6656 uu
BATT_ROTZ = -90.0                       # prua verso il mare (-Y)
BIGL_LOCAL = (3.8, -2.6, 0.01)          # nel riferimento del pontile


# =================================================================================================================
# texture
# =================================================================================================================
def _smooth_noise(h, w, cells, seed):
    r = np.random.default_rng(seed).standard_normal((cells, cells)).astype(np.float32)
    r = tp.resize(r[..., None], w, h)[..., 0]
    return r / (r.std() + 1e-6)


def _fine(h, w, seed, sigma=1.2):
    r = np.random.default_rng(seed).standard_normal((h, w)).astype(np.float32)
    r = tp.blur(r, sigma)
    return r / (r.std() + 1e-6)


def _cell(name, seed):
    """Ritorna (rgb, height, rough, metal) per una cella 512 x 512 (riga 0 = basso)."""
    n = CELL_PX
    big = _smooth_noise(n, n, 6, seed)
    fine = _fine(n, n, seed + 1)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    spec = {  # colore sRGB, variazione, rugosita, metallo
        "BIANCO": ((0.86, 0.87, 0.86), 0.025, 0.35, 0.0), "BLU": ((0.06, 0.18, 0.43), 0.03, 0.33, 0.0),
        "ROSSO": ((0.66, 0.08, 0.06), 0.03, 0.38, 0.0), "VETRO": ((0.10, 0.14, 0.18), 0.02, 0.08, 0.6),
        "PONTE": ((0.47, 0.50, 0.49), 0.04, 0.80, 0.0), "ACCIAIO": ((0.62, 0.63, 0.64), 0.05, 0.42, 1.0),
        "GOMMA": ((0.045, 0.045, 0.045), 0.02, 0.85, 0.0), "DOGHE": ((0.10, 0.19, 0.14), 0.03, 0.50, 0.0),
        "ANTIVEG": ((0.36, 0.09, 0.07), 0.05, 0.75, 0.0), "SCURO": ((0.13, 0.13, 0.14), 0.03, 0.50, 0.3),
        "PANNELLO": ((0.84, 0.82, 0.76), 0.03, 0.55, 0.0), "TEAK": ((0.45, 0.29, 0.16), 0.06, 0.60, 0.0),
        "RUGGINE": ((0.26, 0.18, 0.13), 0.10, 0.85, 0.4), "LETTERE": ((0.92, 0.92, 0.92), 0.01, 0.40, 0.0),
        "CREMA": ((0.80, 0.76, 0.66), 0.03, 0.70, 0.0), "GRIGIO": ((0.40, 0.41, 0.42), 0.04, 0.60, 0.0),
    }[name]
    base, var, rough, metal = spec
    k = 1.0 + var * (0.7 * big + 0.3 * fine)
    rgb = np.dstack([np.full((n, n), c, np.float32) for c in base]) * k[..., None]
    h = 0.5 + 0.02 * fine
    R = np.full((n, n), rough, np.float32) + 0.04 * big
    M = np.full((n, n), metal, np.float32)
    if name == "VETRO":   # riflesso del cielo: piu' chiaro in alto
        rgb *= (0.75 + 0.6 * yy)[..., None]
    if name in ("BIANCO", "BLU"):   # colature leggere verso il basso
        streak = np.clip(_smooth_noise(n, n, 24, seed + 5) * 0.5, 0, None) * (1 - yy)
        rgb *= (1.0 - 0.05 * streak)[..., None]
    if name == "DOGHE":   # 8 feritoie verticali per faccia
        slot = (np.abs(((xx * 8) % 1.0) - 0.5) < 0.16) & (yy > 0.08) & (yy < 0.92)
        rgb[slot] *= 0.25
        h = h - 0.3 * slot
        R[slot] = 0.9
    if name == "PANNELLO":   # 3 giunti verticali dei pannelli
        j = np.abs(((xx * 3) % 1.0) - 0.5) > 0.49
        rgb[j] *= 0.6
        h = h - 0.2 * j
    if name == "TEAK":   # doghe della panca
        j = np.abs(((yy * 4) % 1.0) - 0.5) > 0.47
        rgb *= (1.0 + 0.06 * _smooth_noise(n, n, 40, seed + 7))[..., None]
        rgb[j] *= 0.45
        h = h - 0.3 * j
    if name == "PONTE":   # antisdrucciolo
        h = h + 0.05 * _fine(n, n, seed + 9, 0.6)
    if name == "RUGGINE":
        rgb = rgb * (1 + 0.15 * big[..., None])
    return np.clip(rgb, 0, 1), h, np.clip(R, 0.02, 1), M


def make_tex_atlas(seed=20261120):
    A = np.zeros((ATLAS, ATLAS, 3), np.float32)
    H = np.zeros((ATLAS, ATLAS), np.float32)
    RO = np.zeros((ATLAS, ATLAS), np.float32)
    ME = np.zeros((ATLAS, ATLAS), np.float32)
    for i, (name, (c, r)) in enumerate(C.items()):
        rgb, h, ro, me = _cell(name, seed + 17 * i)
        sl = (slice(r * CELL_PX, (r + 1) * CELL_PX), slice(c * CELL_PX, (c + 1) * CELL_PX))
        A[sl], H[sl], RO[sl], ME[sl] = rgb, h, ro, me
    N, ao = mm._normal_ao(H, 6.0, 3.0, 4.0)
    # array costruiti con riga 0 = basso (UV): tp.save vuole riga 0 = alto
    out = {}
    out["D"] = _save(A[::-1], "T_Morin_Imbarco_D")
    out["N"] = _save(N[::-1], "T_Morin_Imbarco_N")
    out["ORM"] = _save(mm._orm(ao, RO, ME)[::-1], "T_Morin_Imbarco_ORM")
    return out


def make_tex_legno(size=2048, seed=4711):
    """Tavolato grigio-bruno stagionato, 2 m per ripetizione: 14 tavole lungo U (passo 14,3 cm, fuga 1 cm),
    venatura lungo V, teste sfalsate. Riga 0 = basso."""
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    rng = np.random.default_rng(seed)
    NT = 14
    idx = np.minimum((xx * NT).astype(int), NT - 1)
    u = (xx * NT) % 1.0
    tint = rng.uniform(0.82, 1.12, NT).astype(np.float32)
    off = rng.uniform(0, 1, NT).astype(np.float32)
    seg = ((yy + off[idx]) * 2.0) % 1.0          # due tavole per ripetizione in lunghezza
    gap = (u < 0.035) | (u > 0.965) | (seg < 0.004)
    grain = tp.blur(rng.standard_normal((n, n)).astype(np.float32), 1.0)
    grain = tp.resize(tp.resize(grain[..., None], n, n // 16), n, n)[..., 0]   # liscia lungo V: venatura lungo le tavole
    grain /= grain.std() + 1e-6
    big = _smooth_noise(n, n, 8, seed + 1)
    base = np.array((0.50, 0.43, 0.35), np.float32)
    k = tint[idx] * (1 + 0.07 * grain + 0.05 * big)
    rgb = base[None, None, :] * k[..., None]
    rgb[gap] = (0.08, 0.07, 0.06)
    h = 0.6 + 0.03 * grain - 0.5 * gap
    N, ao = mm._normal_ao(h, 8.0, 3.0, 4.0)
    R = np.clip(0.78 + 0.05 * big, 0, 1)
    out = {"D": _save(np.clip(rgb, 0, 1)[::-1], "T_Morin_Imbarco_Legno_D"),
           "N": _save(N[::-1], "T_Morin_Imbarco_Legno_N"),
           "ORM": _save(mm._orm(ao, R, np.zeros_like(R))[::-1], "T_Morin_Imbarco_Legno_ORM")}
    return out


def _save(a, name):
    os.makedirs(TEXDIR, exist_ok=True)
    tp.save(a, f"{TEXDIR}/{name}.png")
    return f"{TEXDIR}/{name}.png"


def make_textures():
    return make_tex_atlas(), make_tex_legno()


def build_materials():
    t = f"{TEXDIR}/T_Morin_Imbarco"
    pk._pbr_material(MAT_A, t + "_D.png", t + "_N.png", t + "_ORM.png")
    t = f"{TEXDIR}/T_Morin_Imbarco_Legno"
    pk._pbr_material(MAT_W, t + "_D.png", t + "_N.png", t + "_ORM.png")
    pk.TILE[MAT_W] = 2.0
    return MAT_A, MAT_W


# =================================================================================================================
# utilita' di geometria: ogni faccia porta la cella dell'atlante in un attributo (tag) e riceve UV alla fine
# =================================================================================================================
class Geo:
    """bmesh + cella per faccia. mi 0 = atlante, mi 1 = legno (UV mondo)."""

    def __init__(self, ref=None):
        self.bm = bmesh.new()
        self.tag = self.bm.faces.layers.int.new("cella")
        self.ref = None if ref is None else Vector(ref)   # punto interno: i quad isolati guardano lontano da qui

    def _set(self, faces, cell, mi=0):
        code = -1 if cell is None else C[cell][0] + 4 * C[cell][1]
        for f in faces:
            f.material_index = mi
            f[self.tag] = code
        return faces

    def box(self, x0, x1, y0, y1, z0, z1, cell, mi=0, faces=("top", "bot", "xn", "xp", "yn", "yp"), mat=None):
        return self._set(pk._box(self.bm, x0, x1, y0, y1, z0, z1, faces=faces, mat=mat), cell, mi)

    def quad(self, pts, cell, mi=0, out=None):
        f = pk._quad(self.bm, pts)
        f.normal_update()
        if out is None and self.ref is not None:
            out = f.calc_center_median() - self.ref
        if out is not None and f.normal.dot(Vector(out)) < 0:
            f.normal_flip()
        return self._set([f], cell, mi)

    def new_faces(self, fn, cell, mi=0):
        before = set(self.bm.faces)
        fn(self.bm)
        return self._set([f for f in self.bm.faces if f not in before], cell, mi)

    def tube(self, pts, r, sides, cell, cap=True):
        return self.new_faces(lambda bm: pk._tube(bm, pts, r, sides, cap=cap), cell)

    def lathe(self, prof, n, cell, mat=Matrix(), cap_top=True):
        return self.new_faces(lambda bm: pk._lathe(bm, prof, n, mat, cap_top=cap_top), cell)

    def hull(self, pts, cell):
        def fn(bm):
            vs = [bm.verts.new(p) for p in pts]
            res = bmesh.ops.convex_hull(bm, input=vs)
            for g in res.get("geom_interior", []) + res.get("geom_unused", []):
                if isinstance(g, bmesh.types.BMVert) and g.is_valid and not g.link_faces:
                    bm.verts.remove(g)
        return self.new_faces(fn, cell)

    def text(self, body, size, mat, cell, align="CENTER"):
        """Testo piatto (senza estrusione) nel piano XY locale, trasformato da mat."""
        cu = bpy.data.curves.new("_tmp_txt", "FONT")
        cu.body = body
        cu.size = size
        cu.align_x = align
        cu.align_y = "CENTER"
        cu.resolution_u = 2
        cu.fill_mode = "BOTH"
        ob = bpy.data.objects.new("_tmp_txt", cu)
        bpy.context.scene.collection.objects.link(ob)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        me.transform(mat)

        def fn(bm):
            bm.from_mesh(me)
        out = self.new_faces(fn, cell)
        bpy.data.meshes.remove(me)
        return out

    def finish(self, name, coll, smooth=None):
        bm = self.bm
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
        ngons = [f for f in bm.faces if len(f.verts) > 4]
        if ngons:
            bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
        bm.normal_update()
        uv = bm.loops.layers.uv.verify()
        for f in bm.faces:
            code = f[self.tag]
            n = f.normal
            ax = max(range(3), key=lambda i: abs(n[i]))
            a, b = [(1, 2), (0, 2), (0, 1)][ax]
            if code < 0:       # legno: UV mondo, tavole lungo Y
                t = pk.TILE.get(MAT_W, 2.0)
                for lp in f.loops:
                    c = lp.vert.co
                    lp[uv].uv = (c.x / t, c.y / t) if ax == 2 else ((c.x + c.y) / t, c.z / t)
                continue
            cx, cy = code % 4, code // 4
            pts = [(lp.vert.co[a], lp.vert.co[b]) for lp in f.loops]
            u0, u1 = min(p[0] for p in pts), max(p[0] for p in pts)
            v0, v1 = min(p[1] for p in pts), max(p[1] for p in pts)
            du, dv = max(u1 - u0, 1e-6), max(v1 - v0, 1e-6)
            flip = (ax == 0 and n[0] < 0) or (ax == 1 and n[1] > 0)
            for lp, (pu, pv) in zip(f.loops, pts):
                s = (pu - u0) / du
                s = 1 - s if flip else s
                t_ = (pv - v0) / dv
                lp[uv].uv = ((cx + INSET * 4 + s * (1 - 8 * INSET)) / 4, (cy + INSET * 4 + t_ * (1 - 8 * INSET)) / 4)
        bm.faces.layers.int.remove(self.tag)
        mats = [MAT_A, MAT_W]
        o = pk._finish(name, bm, mats, coll, uv=None, smooth_angle=smooth)
        me = o.data
        for l in [l for l in me.uv_layers if l.name != "UVMap"]:
            me.uv_layers.remove(l)
        if not any(p.material_index == 1 for p in me.polygons):
            me.materials.pop(index=1)
        return o


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


def _hull_ucx(name, idx, pts, coll):
    pk._ucx_hull(name, idx, [Vector(p) for p in pts], coll)


def _box_pts(x0, x1, y0, y1, z0, z1, mat=Matrix()):
    return [mat @ Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


# =================================================================================================================
# battello
# =================================================================================================================
LOA, HB = 32.0, 3.5
X_ST, X_BO = -16.0, 16.0
STATIONS = [-16.0, -15.4, -12.0, -6.0, 0.0, 5.0, 8.0, 10.5, 12.5, 14.0, 15.0, 15.6, 16.0]
Z_FONDO = -1.4
TUGA = (-12.0, 7.5, 3.1, 1.0, 3.2)             # x0, x1, semi-larghezza, z0, z1
SUP = (-12.6, 8.2, 3.4, 3.15, 3.3)             # ponte superiore: x0, x1, semilarghezza, z0, z1 (calpestio)
TIM = (4.0, 8.0, 1.7, 3.3, 5.0)                # timoniera
PAR_H = 1.0                                    # parapetti del ponte superiore
SCALA = (-15.6, -12.6, -2.8, -1.8)             # scala di poppa: x0 (piede), x1 (sbarco), y0, y1
VARCO = (-14.2, -12.4)                         # varco della battagliola di poppa sul lato pontile (+Y)


def half_b(x):
    if x <= 5.0:
        return HB - 0.15 * max(0.0, (-x - 12.0) / 4.0)
    t = min((x - 5.0) / (X_BO - 5.0), 1.0)
    return max(HB * math.sqrt(max(1.0 - t * t, 0.0)), 0.04)


def z_keel(x):
    if x < -10.0:
        return Z_FONDO + (x + 10.0) / -6.0 * (-0.55 - Z_FONDO) * 1.0
    if x > 8.0:
        return Z_FONDO + ((x - 8.0) / 8.0) ** 1.5 * (0.35 - Z_FONDO)
    return Z_FONDO


def z_sheer(x):
    return 1.0 + 0.5 * max(0.0, (x - 6.0) / 10.0) ** 2


def _section(x):
    b, zk, zs = half_b(x), z_keel(x), z_sheer(x)
    z1 = max(-0.3, zk + 0.02)
    z2 = max(0.55, z1 + 0.02)
    zm = zk + 0.55 * (z1 - zk)
    return [(0.0, zk), (0.72 * b, zm), (0.93 * b, z1), (0.985 * b, z2), (b, zs)]


ROW_CELLS = ["ANTIVEG", "ANTIVEG", "BLU", "BIANCO"]


def _hull(g, lod):
    st = STATIONS if lod == 0 else [s for i, s in enumerate(STATIONS) if i % 2 == 0 or s in (16.0,)]
    secs = [(x, _section(x)) for x in st]
    rings = []
    for x, sec in secs:
        port = [g.bm.verts.new((x, -y, z)) for y, z in sec]
        stb = [g.bm.verts.new((x, y, z)) for y, z in sec]
        rings.append((port, stb))
    for (pa, sa), (pb, sb) in zip(rings[:-1], rings[1:]):
        for r in range(4):
            g._set([g.bm.faces.new([pa[r + 1], pa[r], pb[r], pb[r + 1]])], ROW_CELLS[r])
            g._set([g.bm.faces.new([sa[r], sa[r + 1], sb[r + 1], sb[r]])], ROW_CELLS[r])
        g._set([g.bm.faces.new([pa[4], pb[4], sb[4], sa[4]])], "PONTE")      # coperta = cappello dello scafo
    # specchio di poppa e punta di prua
    p, s = rings[0]
    for r in range(4):
        g._set([g.bm.faces.new([p[r], p[r + 1], s[r + 1], s[r]])], ROW_CELLS[r] if r < 3 else "BIANCO")
    p, s = rings[-1]
    for r in range(4):
        g._set([g.bm.faces.new([p[r + 1], p[r], s[r], s[r + 1]])], ROW_CELLS[r])
    pk._recalc(g.bm)
    # bottazzo (fascia paracolpi) scuro sotto la falchetta
    if lod < 2:
        for sgn in (-1, 1):
            pts = [(x, sgn * (half_b(x) + 0.03), z_sheer(x) - 0.12) for x in st if x < 15.7]
            g.tube(pts, 0.06, 4 if lod == 0 else 3, "SCURO")


def _tuga(g, lod):
    x0, x1, w, z0, z1 = TUGA
    g.box(x0, x1, -w, w, z0, z1, "BIANCO", faces=("xn", "xp", "yn", "yp"))
    # finestre: quad di vetro staccati 1,5 cm dalla parete
    e = 0.015
    nwin = 9
    span = (x1 - 0.6) - (x0 + 0.6)
    pitch = span / nwin
    for i in range(nwin):
        a = x0 + 0.6 + i * pitch + 0.15
        b = a + pitch - 0.3
        g.quad([(a, -w - e, 1.8), (b, -w - e, 1.8), (b, -w - e, 2.8), (a, -w - e, 2.8)], "VETRO")
        g.quad([(b, w + e, 1.8), (a, w + e, 1.8), (a, w + e, 2.8), (b, w + e, 2.8)], "VETRO")
    for i in range(3):   # fronte
        a = -w + 0.4 + i * (2 * w - 0.8) / 3 + 0.1
        b = a + (2 * w - 0.8) / 3 - 0.2
        g.quad([(x1 + e, a, 1.8), (x1 + e, b, 1.8), (x1 + e, b, 2.8), (x1 + e, a, 2.8)], "VETRO")
    # poppa: porta centrale e due finestre
    g.quad([(x0 - e, 0.55, z0), (x0 - e, -0.55, z0), (x0 - e, -0.55, 2.4), (x0 - e, 0.55, 2.4)], "SCURO")
    for a, b in ((-2.6, -1.0), (1.0, 2.6)):
        g.quad([(x0 - e, b, 1.8), (x0 - e, a, 1.8), (x0 - e, a, 2.8), (x0 - e, b, 2.8)], "VETRO")
    # zoccolo blu della tuga
    g.box(x0 - 0.01, x1 + 0.01, -w - 0.01, w + 0.01, z0, z0 + 0.25, "BLU", faces=("xn", "xp", "yn", "yp"))


def _ponte_sup(g, lod):
    x0, x1, w, z0, z1 = SUP
    g.box(x0, x1, -w, w, z0, z1, "BIANCO", faces=("bot", "xn", "xp", "yn", "yp"))
    g.box(x0, x1, -w, w, z1 - 0.001, z1, "PONTE", faces=("top",))
    t = 0.06
    zt = z1 + PAR_H
    sx0, sx1, sy0, sy1 = SCALA
    tx0, tx1, tw = TIM[0], TIM[1], TIM[2]
    panels = [  # x0, x1, y0, y1
        (x0, x1, -w, -w + t), (x0, x1, w - t, w),
        (x0, x0 + t, -w + t, sy0), (x0, x0 + t, sy1, w - t),
        (x1 - t, x1, -w + t, -tw), (x1 - t, x1, tw, w - t),
    ]
    for a, b, c, d in panels:
        g.box(a, b, c, d, z1, zt, "BIANCO", faces=("xn", "xp", "yn", "yp", "top"))
    # corrimano tubolare sopra i parapetti laterali, fascia blu esterna
    if lod == 0:
        for sgn in (-1, 1):
            g.tube([(x0, sgn * (w - t / 2), zt + 0.04), (x1, sgn * (w - t / 2), zt + 0.04)], 0.035, 6, "ACCIAIO")
    for sgn in (-1, 1):
        y = sgn * (w + 0.004)
        pts = [(x0, y, zt - 0.22), (x1, y, zt - 0.22), (x1, y, zt - 0.08), (x0, y, zt - 0.08)]
        g.quad(pts if sgn > 0 else pts[::-1], "BLU")
    # nome sui parapetti (entrambe le murate)
    xc = (x0 + x1) / 2 - 2.0
    for sgn in (-1, 1):
        y = sgn * (w + 0.008)
        if sgn < 0:   # lato -Y: testo leggibile da fuori, X crescente
            M = Matrix(((1, 0, 0, xc), (0, 0, -1, y), (0, 1, 0, z1 + 0.5), (0, 0, 0, 1)))
        else:
            M = Matrix(((-1, 0, 0, xc), (0, 0, 1, y), (0, 1, 0, z1 + 0.5), (0, 0, 0, 1)))
        g.text(NAME, 0.55, M, "BLU")
    # panche longitudinali (schiena al parapetto) e doppia panca centrale
    sx = (x0 + 0.8, TIM[0] - 0.6) if lod < 2 else None
    if sx:
        for sgn in (-1, 1):
            yb = sgn * (w - t - 0.25)
            g.box(sx[0], sx[1], yb - 0.22, yb + 0.22, z1 + 0.40, z1 + 0.46, "TEAK", faces=("top", "yn", "yp", "xn", "xp"))
            for xl in np.linspace(sx[0] + 0.3, sx[1] - 0.3, 5 if lod == 0 else 3):
                g.box(xl - 0.04, xl + 0.04, yb - 0.18, yb + 0.18, z1, z1 + 0.40, "SCURO", faces=("xn", "xp", "yn", "yp"))
        cx0, cx1 = x0 + 3.0, TIM[0] - 2.0
        for sgn in (-1, 1):
            g.box(cx0, cx1, sgn * 0.08, sgn * 0.52, z1 + 0.40, z1 + 0.46, "TEAK", faces=("top", "yn", "yp", "xn", "xp"))
        g.box(cx0, cx1, -0.05, 0.05, z1 + 0.40, z1 + 0.95, "TEAK", faces=("top", "yn", "yp", "xn", "xp"))
        for xl in np.linspace(cx0 + 0.3, cx1 - 0.3, 4 if lod == 0 else 2):
            g.box(xl - 0.05, xl + 0.05, -0.45, 0.45, z1, z1 + 0.40, "SCURO", faces=("xn", "xp", "yn", "yp"))
    # salvagenti rossi sui parapetti (esterno)
    if lod < 2:
        for sgn in (-1, 1):
            for xs in (x0 + 1.5, x1 - 5.5):
                M = Matrix.Translation((xs, sgn * (w + 0.09), z1 + 0.5)) @ Matrix.Rotation(math.radians(90), 4, "X")
                ns = 6 if lod == 0 else 4
                prof = [(0.27 + 0.065 * math.cos(2 * math.pi * k / ns), 0.065 * math.sin(2 * math.pi * k / ns))
                        for k in range(ns + 1)]
                g.lathe(prof, 10 if lod == 0 else 6, "ROSSO", mat=M, cap_top=False)


def _timoniera(g, lod):
    x0, x1, w, z0, z1 = TIM
    g.box(x0, x1, -w, w, z0, z1, "BIANCO", faces=("xn", "xp", "yn", "yp"))
    g.box(x0 - 0.15, x1 + 0.35, -w - 0.15, w + 0.15, z1, z1 + 0.12, "BIANCO")
    e = 0.015
    g.quad([(x1 + e, -w + 0.15, 4.05), (x1 + e, w - 0.15, 4.05), (x1 + e, w - 0.15, 4.8), (x1 + e, -w + 0.15, 4.8)], "VETRO")
    for sgn in (-1, 1):
        y = sgn * (w + e)
        pts = [(x0 + 0.3, y, 4.05), (x1 - 0.2, y, 4.05), (x1 - 0.2, y, 4.8), (x0 + 0.3, y, 4.8)]
        g.quad(pts if sgn > 0 else pts[::-1], "VETRO")
        dp = [(x0 + 0.3, y, z0), (x0 + 1.1, y, z0), (x0 + 1.1, y, 3.95), (x0 + 0.3, y, 3.95)]
        g.quad(dp if sgn > 0 else dp[::-1], "SCURO")
    # insegna rossa sul tetto con il nome
    zb = z1 + 0.12
    g.box(x1 - 0.2, x1 - 0.12, -1.6, 1.6, zb + 0.05, zb + 0.6, "ROSSO")
    for xl in (-1.2, 1.2):
        g.box(x1 - 0.22, x1 - 0.18, xl - 0.03, xl + 0.03, zb, zb + 0.05, "SCURO")
    M = Matrix(((0, 0, 1, x1 - 0.115), (1, 0, 0, 0.0), (0, 1, 0, zb + 0.325), (0, 0, 0, 1)))
    g.text(NAME, 0.30, M, "LETTERE")
    # albero con fanali e radar
    if lod < 2:
        g.tube([(x0 + 1.0, 0, zb), (x0 + 1.0, 0, zb + 1.6)], 0.05, 6 if lod == 0 else 4, "ACCIAIO")
        g.box(x0 + 0.95, x0 + 1.05, -0.55, 0.55, zb + 1.2, zb + 1.26, "SCURO")
        g.box(x0 + 0.9, x0 + 1.1, -0.06, 0.06, zb + 1.6, zb + 1.75, "LETTERE")


def _battagliola(g, pts, lod, gaps=()):
    """Battagliola (montanti + corrimano + filo intermedio) lungo una polilinea a quota coperta."""
    sides = 6 if lod == 0 else 4
    top = [(p[0], p[1], p[2] + 1.0) for p in pts]
    mid = [(p[0], p[1], p[2] + 0.5) for p in pts]
    g.tube(top, 0.03, sides, "ACCIAIO")
    if lod < 2:
        g.tube(mid, 0.015, 4, "ACCIAIO")
    for p in pts:
        g.tube([p, (p[0], p[1], p[2] + 1.0)], 0.022, 4, "ACCIAIO", cap=False)


def _rails_main(g, lod):
    # prua: dalla tuga (x 7,5) alla punta, lungo la falchetta rientrata di 8 cm
    xs = [7.6, 9.5, 11.5, 13.0, 14.2, 15.1, 15.7]
    for sgn in (-1, 1):
        pts = [(x, sgn * max(half_b(x) - 0.08, 0.05), z_sheer(x)) for x in xs]
        _battagliola(g, pts, lod)
    # poppa: lato -Y intero, specchio, lato +Y con varco verso il pontile
    xa, xb = -15.9, TUGA[0] - 0.1
    yb = half_b(-14.0) - 0.08
    _battagliola(g, [(xb, -yb, 1.0), (-14.0, -yb, 1.0), (xa, -yb + 0.05, 1.0)], lod)
    _battagliola(g, [(xa, -yb + 0.05, 1.0), (xa, 0.0, 1.0), (xa, yb - 0.05, 1.0)], lod)
    _battagliola(g, [(xa, yb - 0.05, 1.0), (VARCO[0], yb, 1.0)], lod)
    _battagliola(g, [(VARCO[1], yb, 1.0), (xb, yb, 1.0)], lod)


def _scala(g, lod):
    x0, x1, y0, y1 = SCALA
    z0, z1 = 1.0, SUP[4]
    n = 10 if lod < 2 else 0
    for i in range(n):
        xa = x0 + (x1 - x0) * i / n
        za = z0 + (z1 - z0) * (i + 1) / n
        g.box(xa, xa + (x1 - x0) / n + 0.02, y0 + 0.05, y1 - 0.05, za - 0.05, za, "PONTE", faces=("top", "xn", "xp"))
    for y in (y0, y1 - 0.05):   # cosciali
        g.hull([(x0, y, z0), (x0 + 0.25, y, z0), (x1, y, z1 + 0.05), (x1, y, z1 - 0.3),
                (x0, y + 0.05, z0), (x0 + 0.25, y + 0.05, z0), (x1, y + 0.05, z1 + 0.05), (x1, y + 0.05, z1 - 0.3)],
               "BIANCO")
    if n == 0:
        g.quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z1), (x1, y0, z1)], "PONTE", out=(-1, 0, 1))
    for y in (y0, y1):
        g.tube([(x0, y, z0 + 0.9), (x1, y, z1 + 0.9)], 0.025, 4, "ACCIAIO")


def _parabordi_battello(g, lod):
    if lod == 2:
        return
    for sgn in (-1, 1):
        for x in (-10.0, -5.0, 0.0, 5.0):
            y = sgn * (HB + 0.14)
            g.lathe([(0.0, 0.25), (0.11, 0.30), (0.13, 0.45), (0.13, 0.80), (0.11, 0.95), (0.0, 1.0)],
                    8 if lod == 0 else 5, "BIANCO", mat=Matrix.Translation((x, y, 0.0)), cap_top=False)
            g.tube([(x, y, 1.0), (x, sgn * (HB - 0.05), z_sheer(x) + 0.02)], 0.012, 3, "SCURO", cap=False)


def _bitte_battello(g, lod):
    for x in (-15.0, 14.5):
        for sgn in (-1, 1):
            y = sgn * (half_b(x) - 0.4)
            g.lathe([(0.12, 0.0), (0.09, 0.05), (0.07, 0.25), (0.11, 0.28), (0.11, 0.32), (0.0, 0.33)],
                    8 if lod == 0 else 5, "SCURO", mat=Matrix.Translation((x, y, z_sheer(x))))


def build_battello(coll, lod=0, name="SM_Morin_Battello"):
    g = Geo(ref=(0.0, 0.0, 2.0))
    _hull(g, lod)
    _tuga(g, lod)
    _ponte_sup(g, lod)
    _timoniera(g, lod)
    _rails_main(g, lod)
    _scala(g, lod)
    _parabordi_battello(g, lod)
    _bitte_battello(g, lod)
    return g.finish(name + _sfx(lod), coll, smooth=35.0)


def ucx_battello(coll, name="SM_Morin_Battello"):
    hull_pts = []
    for x in STATIONS:
        for y, z in _section(x):
            hull_pts += [(x, -y, z), (x, y, z)]
    _hull_ucx(name, 0, hull_pts, coll)                                     # scafo fino alla coperta
    x0, x1, w, z0, z1 = TUGA
    i = 1
    pk._ucx(name, [(x0, x1, -w, w, z0, SUP[3])], coll, start=i); i += 1   # ponte inferiore (tuga)
    sx0, sx1, sw, sz0, sz1 = SUP
    pk._ucx(name, [(sx0, sx1, -sw, sw, sz0, sz1)], coll, start=i); i += 1  # ponte superiore (calpestio)
    tx0, tx1, tw, tz0, tz1 = TIM
    pk._ucx(name, [(tx0 - 0.15, tx1 + 0.35, -tw - 0.15, tw + 0.15, tz0, tz1 + 0.12)], coll, start=i); i += 1  # timoniera
    t, zt = 0.06, sz1 + PAR_H
    ya, yb = SCALA[2], SCALA[3]
    boxes = [(sx0, sx1, -sw, -sw + t, sz1, zt), (sx0, sx1, sw - t, sw, sz1, zt),
             (sx0, sx0 + t, -sw + t, ya, sz1, zt), (sx0, sx0 + t, yb, sw - t, sz1, zt),
             (sx1 - t, sx1, -sw + t, -tw, sz1, zt), (sx1 - t, sx1, tw, sw - t, sz1, zt)]
    pk._ucx(name, boxes, coll, start=i); i += len(boxes)                  # parapetti del ponte superiore
    x0s, x1s, y0s, y1s = SCALA                                             # scala di poppa come rampa
    _hull_ucx(name, i, [(x0s, y0s, 1.0), (x0s, y1s, 1.0), (x1s, y0s, sz1), (x1s, y1s, sz1),
                        (x1s, y0s, 1.0), (x1s, y1s, 1.0)], coll); i += 1
    # battagliole: prua (due convessi per lato) e poppa
    for sgn in (-1, 1):
        for xa, xb in ((7.6, 12.5), (12.5, 15.7)):
            pts = []
            for x in (xa, xb):
                y = sgn * max(half_b(x) - 0.08, 0.05)
                for dy in (0.0, -sgn * 0.05):
                    pts += [(x, y + dy, z_sheer(x)), (x, y + dy, z_sheer(x) + 1.0)]
            _hull_ucx(name, i, pts, coll); i += 1
    yb2 = half_b(-14.0) - 0.08
    pk._ucx(name, [(-15.95, TUGA[0] - 0.1, -yb2 - 0.03, -yb2 + 0.03, 1.0, 2.0),
                   (-15.95, -15.85, -yb2, yb2, 1.0, 2.0),
                   (-15.95, VARCO[0], yb2 - 0.03, yb2 + 0.03, 1.0, 2.0),
                   (VARCO[1], TUGA[0] - 0.1, yb2 - 0.03, yb2 + 0.03, 1.0, 2.0)], coll, start=i)
    i += 4
    return i


# =================================================================================================================
# pontile d'imbarco (riferimento: origine sul ciglio all'asse del pontile, X/Y come il mondo)
# =================================================================================================================
PW = 1.5                    # semilarghezza dell'impalcato (3 m [S])
PLAT = (-1.5, 5.5, -4.0, 0.12, 0.01)   # piattaforma di radice: x0, x1, y0, y1, quota di calpestio
RAMPA = (-4.0, -7.0)        # y di inizio e fine della rampa
Z_IMP = -0.34               # calpestio dell'impalcato (0,66 m sull'acqua) [S]
Y_TESTA = 51.7 - PONT_ORIG[1]   # -28,51
PALI_Y = (-6.8, -12.3, -17.8, -23.2, -28.2)


def build_pontile(coll, lod=0, name="SM_Morin_PontileImbarco"):
    g = Geo()
    px0, px1, py0, py1, pz = PLAT
    # piattaforma: tavolato sopra, fascia d'acciaio scuro sui lati
    g.box(px0, px1, py0, py1, pz - 0.001, pz, None, mi=1, faces=("top",))
    g.box(px0, px1, py0, py1, pz - 0.40, pz - 0.001, "SCURO", faces=("xn", "xp", "yn", "bot"))
    # rampa
    ya, yb = RAMPA
    g.quad([(-PW, yb, Z_IMP), (PW, yb, Z_IMP), (PW, ya, pz), (-PW, ya, pz)], None, mi=1, out=(0, 0, 1))
    for x in (-PW, PW):
        g.quad([(x, yb, Z_IMP - 0.25), (x, ya, pz - 0.40), (x, ya, pz), (x, yb, Z_IMP)], "SCURO", out=(x, 0, 0))
    g.quad([(-PW, yb, Z_IMP - 0.25), (PW, yb, Z_IMP - 0.25), (PW, ya, pz - 0.40), (-PW, ya, pz - 0.40)], "SCURO",
           out=(0, 0, -1))
    # impalcato: tavolato 12 cm, travi longitudinali e traversi
    g.box(-PW, PW, Y_TESTA, yb, Z_IMP - 0.001, Z_IMP, None, mi=1, faces=("top",))
    g.box(-PW, PW, Y_TESTA, yb, Z_IMP - 0.12, Z_IMP - 0.001, "TEAK", faces=("xn", "xp", "yn", "bot"))
    for x in (-1.15, 1.15):
        g.box(x - 0.1, x + 0.1, Y_TESTA + 0.1, yb, Z_IMP - 0.50, Z_IMP - 0.12, "RUGGINE",
              faces=("xn", "xp", "bot", "yn"))
    if lod < 2:
        for y in PALI_Y:
            g.box(-PW + 0.05, PW - 0.05, y - 0.1, y + 0.1, Z_IMP - 0.45, Z_IMP - 0.12, "RUGGINE",
                  faces=("yn", "yp", "bot"))
    # pali d'acciaio riempiti di calcestruzzo
    for y in PALI_Y:
        for x in (-1.3, 1.3):
            g.lathe([(0.25, -4.0), (0.25, Z_IMP - 0.45), (0.27, Z_IMP - 0.42)], 8 if lod == 0 else 6, "RUGGINE",
                    mat=Matrix.Translation((x, y, 0)))
    for y in (-2.2,):
        for x in (-0.8, 2.0, 4.6):
            g.lathe([(0.25, -4.0), (0.25, pz - 0.40)], 8 if lod == 0 else 6, "RUGGINE", mat=Matrix.Translation((x, y, 0)),
                    cap_top=False)
    # bottazzo in gomma sul lato battello (ovest) e bittini
    g.box(-PW - 0.10, -PW, Y_TESTA, yb, Z_IMP - 0.45, Z_IMP - 0.05, "GOMMA", faces=("xn", "top", "bot", "yn", "yp"))
    for y in (-9.0, -16.0, -23.0, -28.0):
        g.lathe([(0.10, 0.0), (0.07, 0.04), (0.06, 0.22), (0.09, 0.25), (0.09, 0.29), (0.0, 0.30)],
                8 if lod == 0 else 5, "SCURO", mat=Matrix.Translation((-PW + 0.2, y, Z_IMP)))
    # ringhiera sul lato marina (est) e sui bordi liberi della piattaforma
    sides = 6 if lod == 0 else 4
    def ringhiera(pts):
        top = [(p[0], p[1], p[2] + 1.0) for p in pts]
        g.tube(top, 0.03, sides, "ACCIAIO")
        if lod < 2:
            g.tube([(p[0], p[1], p[2] + 0.12) for p in pts], 0.02, 4, "ACCIAIO")
        for a, b in zip(pts[:-1], pts[1:]):
            L = (Vector(b) - Vector(a)).length
            n = max(1, int(round(L / 1.8)))
            for k in range(n + 1 if b is pts[-1] else n):
                p = Vector(a).lerp(Vector(b), k / n)
                g.tube([tuple(p), (p.x, p.y, p.z + 1.0)], 0.025, 4, "ACCIAIO", cap=False)
            if lod == 0:   # tondini verticali ogni 12 cm sostituiti da 2 correnti intermedi
                for z in (0.45, 0.75):
                    g.tube([(a[0], a[1], a[2] + z), (b[0], b[1], b[2] + z)], 0.012, 4, "ACCIAIO")
    xr = PW - 0.06
    ringhiera([(xr, Y_TESTA + 0.1, Z_IMP), (xr, yb, Z_IMP), (xr, ya, pz)])
    ringhiera([(xr + 0.06, ya + 0.06, pz), (px1 - 0.06, ya + 0.06, pz), (px1 - 0.06, py1 - 0.25, pz)])
    ringhiera([(-PW + 0.06, Y_TESTA + 0.06, Z_IMP), (PW - 0.06, Y_TESTA + 0.06, Z_IMP)])
    return g.finish(name + _sfx(lod), coll, smooth=None)


def ucx_pontile(coll, name="SM_Morin_PontileImbarco"):
    px0, px1, py0, py1, pz = PLAT
    ya, yb = RAMPA
    boxes = [(px0, px1, py0, py1, pz - 0.40, pz),                         # piattaforma
             (-PW - 0.10, PW, Y_TESTA, yb, Z_IMP - 0.50, Z_IMP),            # impalcato
             (PW - 0.09, PW - 0.03, Y_TESTA, yb, Z_IMP, Z_IMP + 1.03),       # ringhiera est
             (PW - 0.03, px1, ya, ya + 0.12, pz, pz + 1.03),                 # ringhiera piattaforma sud
             (px1 - 0.09, px1 - 0.03, ya, py1 - 0.25, pz, pz + 1.03),        # ringhiera piattaforma est
             (-PW, PW, Y_TESTA, Y_TESTA + 0.09, Z_IMP, Z_IMP + 1.03)]        # ringhiera di testa
    pk._ucx(name, boxes, coll)
    i = len(boxes)
    _hull_ucx(name, i, [(-PW, ya, pz), (PW, ya, pz), (-PW, yb, Z_IMP), (PW, yb, Z_IMP),
                        (-PW, ya, pz - 0.40), (PW, ya, pz - 0.40), (-PW, yb, Z_IMP - 0.25), (PW, yb, Z_IMP - 0.25)],
              coll); i += 1
    _hull_ucx(name, i, [(PW - 0.09, ya, pz), (PW - 0.03, ya, pz), (PW - 0.09, yb, Z_IMP), (PW - 0.03, yb, Z_IMP),
                        (PW - 0.09, ya, pz + 1.03), (PW - 0.03, ya, pz + 1.03),
                        (PW - 0.09, yb, Z_IMP + 1.03), (PW - 0.03, yb, Z_IMP + 1.03)], coll); i += 1
    for y in PALI_Y:   # pali (visibili sopra l'acqua: si urtano nuotando)
        for x in (-1.3, 1.3):
            pk._ucx(name, [(x - 0.25, x + 0.25, y - 0.25, y + 0.25, -4.0, Z_IMP - 0.45)], coll, start=i); i += 1
    return i


# =================================================================================================================
# biglietteria (origine al centro della base, fronte con lo sportello verso +Y = banchina)
# =================================================================================================================
BIG = (1.5, 1.0, 2.5)   # semilarghezza X, semiprofondita' Y, altezza pareti


def build_biglietteria(coll, lod=0, name="SM_Morin_Biglietteria"):
    g = Geo(ref=(0.0, 0.0, 1.2))
    hx, hy, h = BIG
    g.box(-hx, hx, -hy, hy, 0.0, 0.25, "SCURO", faces=("xn", "xp", "yn", "yp"))
    g.box(-hx, hx, -hy, hy, 0.25, h, "PANNELLO", faces=("xn", "xp", "yn", "yp"))
    g.box(-hx - 0.2, hx + 0.2, -hy - 0.15, hy + 0.45, h, h + 0.18, "BIANCO")
    e = 0.015
    # sportello: vetrata, banco, mensola
    g.quad([(hx - 0.3, hy + e, 1.0), (-hx + 0.3, hy + e, 1.0), (-hx + 0.3, hy + e, 2.15), (hx - 0.3, hy + e, 2.15)],
           "VETRO")
    g.box(-hx + 0.25, hx - 0.25, hy, hy + 0.28, 0.94, 1.0, "SCURO")
    if lod < 2:
        g.box(-hx + 0.3, hx - 0.3, hy + e, hy + 0.03, 1.55, 1.58, "ACCIAIO")
    # porta sul lato ovest (verso la rampa) e finestra sul retro
    g.quad([(-hx - e, 0.45, 0.25), (-hx - e, -0.45, 0.25), (-hx - e, -0.45, 2.1), (-hx - e, 0.45, 2.1)], "SCURO")
    g.quad([(0.8, -hy - e, 1.3), (-0.8, -hy - e, 1.3), (-0.8, -hy - e, 2.0), (0.8, -hy - e, 2.0)][::-1], "VETRO")
    g.quad([(hx + e, -0.5, 1.3), (hx + e, 0.5, 1.3), (hx + e, 0.5, 2.0), (hx + e, -0.5, 2.0)], "VETRO")
    # insegna blu sul tetto, scritta generica
    zt = h + 0.18
    g.box(-1.35, 1.35, hy + 0.15, hy + 0.25, zt, zt + 0.42, "BLU")
    M = Matrix(((-1, 0, 0, 0), (0, 0, 1, hy + 0.255), (0, 1, 0, zt + 0.21), (0, 0, 0, 1)))
    g.text("BIGLIETTERIA", 0.26, M, "LETTERE")
    M2 = Matrix(((1, 0, 0, 0), (0, 0, -1, hy + 0.145), (0, 1, 0, zt + 0.21), (0, 0, 0, 1)))
    if lod == 0:
        g.text("BIGLIETTERIA", 0.26, M2, "LETTERE")
    # orari: pannellino chiaro accanto allo sportello
    g.quad([(-hx + 0.05, hy + e, 1.1), (-hx + 0.25, hy + e, 1.1), (-hx + 0.25, hy + e, 1.8), (-hx + 0.05, hy + e, 1.8)],
           "LETTERE")
    return g.finish(name + _sfx(lod), coll)


# =================================================================================================================
# arredi minori
# =================================================================================================================
def build_cestino(coll, lod=0, name="SM_Morin_Cestino"):
    """Cestino cilindrico in lamiera a doghe su colonnina, h 0,95 m, Ø 0,42 [S]. Origine alla base."""
    g = Geo()
    n = (12, 8, 6)[lod]
    g.lathe([(0.09, 0.0), (0.09, 0.03), (0.045, 0.05), (0.04, 0.30)], n, "SCURO", cap_top=False)
    g.lathe([(0.0, 0.30), (0.20, 0.30), (0.21, 0.32), (0.21, 0.90)], n, "DOGHE", cap_top=False)
    g.lathe([(0.21, 0.90), (0.225, 0.905), (0.225, 0.95), (0.19, 0.95), (0.19, 0.60)], n, "SCURO", cap_top=False)
    g.lathe([(0.19, 0.60), (0.0, 0.60)], n, "GOMMA", cap_top=False)   # fondo interno (sacco)
    if lod < 2:
        g.box(-0.08, 0.08, 0.205, 0.215, 0.70, 0.80, "LETTERE")       # targhetta (raccolta)
    return g.finish(name + _sfx(lod), coll, smooth=40.0)


def build_rastrelliera(coll, lod=0, name="SM_Morin_Rastrelliera"):
    """Portabici a onda in tubo zincato Ø 5 cm, 2,4 m, 5 posti, h 0,80 m [S]. Origine al centro della base."""
    g = Geo()
    L, H, NW = 2.4, 0.80, 5
    npts = (60, 30, 14)[lod]
    sides = (6, 5, 4)[lod]
    r = L / (2 * NW)
    pts = []
    for k in range(npts + 1):
        t = k / npts
        x = -L / 2 + t * L
        ph = (t * NW) % 1.0 if t < 1 else 1.0
        # profilo a "U rovesciate" in serie: gamba - arco - gamba
        if ph < 0.12:
            zz = 0.05 + (H - r - 0.05) * (ph / 0.12)
        elif ph > 0.88:
            zz = 0.05 + (H - r - 0.05) * ((1 - ph) / 0.12)
        else:
            zz = (H - r) + r * math.sin(math.pi * (ph - 0.12) / 0.76)
        pts.append((x, 0.0, zz))
    g.tube(pts, 0.025, sides, "ACCIAIO")
    for y in (-0.25, 0.25):
        g.box(-L / 2 - 0.05, L / 2 + 0.05, y - 0.02, y + 0.02, 0.0, 0.04, "ACCIAIO", faces=("top", "yn", "yp", "xn", "xp"))
    for x in (-L / 2, L / 2):
        g.box(x - 0.02, x + 0.02, -0.25, 0.25, 0.0, 0.05, "ACCIAIO", faces=("top", "yn", "yp", "xn", "xp"))
    return g.finish(name + _sfx(lod), coll, smooth=50.0)


def build_parabordo(coll, lod=0, name="SM_Banchina_Parabordo"):
    """Parabordo verticale a D in gomma nera, 0,30 x 0,22 x 0,90 m [S]. Origine in alto sul dorso (contro il paramento),
    sporge verso -Y (mare)."""
    g = Geo()
    n = (8, 5, 3)[lod]
    R, D, Lz = 0.15, 0.22, 0.90
    ring = [(R * math.cos(math.pi * k / n), -(D - R) - R * math.sin(math.pi * k / n)) for k in range(n + 1)]
    prof = [(R, 0.0)] + ring + [(-R, 0.0)]
    top = [g.bm.verts.new((x, y, 0.0)) for x, y in prof]
    bot = [g.bm.verts.new((x, y, -Lz)) for x, y in prof]
    for a in range(len(prof) - 1):
        b = a + 1
        g._set([g.bm.faces.new([bot[a], bot[b], top[b], top[a]])], "GOMMA")
    g._set([g.bm.faces.new(top[::-1])], "GOMMA")
    g._set([g.bm.faces.new(bot)], "GOMMA")
    pk._recalc(g.bm)
    if lod < 2:
        for z in (-0.12, -0.78):
            g.box(-0.05, 0.05, -(D + 0.005), -D + 0.02, z - 0.04, z + 0.04, "ACCIAIO", faces=("yn", "top", "bot", "xn", "xp"))
    return g.finish(name + _sfx(lod), coll, smooth=50.0)


# =================================================================================================================
# build, UCX, CSV
# =================================================================================================================
ASSETS = ["SM_Morin_Battello", "SM_Morin_PontileImbarco", "SM_Morin_Biglietteria", "SM_Morin_Cestino",
          "SM_Morin_Rastrelliera", "SM_Banchina_Parabordo"]
BUILDERS = {"SM_Morin_Battello": build_battello, "SM_Morin_PontileImbarco": build_pontile,
            "SM_Morin_Biglietteria": build_biglietteria, "SM_Morin_Cestino": build_cestino,
            "SM_Morin_Rastrelliera": build_rastrelliera, "SM_Banchina_Parabordo": build_parabordo}


def _decimate(src, ratio, name, coll):
    """LOD per decimazione (collapse, bordi UV e spigoli preservati) quando la versione ricostruita non basta."""
    o = bpy.data.objects.get(name)
    tmp = src.copy()
    tmp.data = src.data.copy()
    coll.objects.link(tmp)
    m = tmp.modifiers.new("dec", "DECIMATE")
    m.decimate_type = "COLLAPSE"
    m.ratio = ratio
    m.use_collapse_triangulate = True
    try:
        m.delimit = {"UV", "SHARP", "MATERIAL"}
    except TypeError:
        pass
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    old = tmp.data
    bpy.data.objects.remove(tmp)
    if old.users == 0:
        bpy.data.meshes.remove(old)
    if o is None:
        o = bpy.data.objects.new(name, me)
        coll.objects.link(o)
    else:
        prev = o.data
        o.data = me
        if prev.users == 0:
            bpy.data.meshes.remove(prev)
    me.name = name
    return o


def build_all(lod_target=(1.0, 0.5, 0.15)):
    coll = pk._coll(KIT)
    out = {}
    for nm in ASSETS:
        objs = []
        o0 = BUILDERS[nm](coll, 0)
        t0 = pk.tri_count(o0)
        objs.append(o0)
        for lod in (1, 2):
            o = BUILDERS[nm](coll, lod)
            t = pk.tri_count(o)
            want = t0 * lod_target[lod]
            if t > want * 1.15:   # la versione semplificata a mano e' ancora troppo pesante: decimo
                o = _decimate(o, max(0.05, want / t), o.name, coll)
            objs.append(o)
        out[nm] = objs
    ucx_battello(coll)
    ucx_pontile(coll)
    pk._ucx("SM_Morin_Biglietteria", [(-BIG[0] - 0.2, BIG[0] + 0.2, -BIG[1] - 0.15, BIG[1] + 0.45, 0.0, BIG[2] + 0.6)],
            coll)
    pk._ucx("SM_Morin_Cestino", [(-0.225, 0.225, -0.225, 0.225, 0.0, 0.95)], coll)
    pk._ucx("SM_Morin_Rastrelliera", [(-1.25, 1.25, -0.06, 0.06, 0.0, 0.80), (-1.25, 1.25, -0.27, 0.27, 0.0, 0.05)], coll)
    pk._ucx("SM_Banchina_Parabordo", [(-0.15, 0.15, -0.22, 0.0, -0.90, 0.0)], coll)
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    rep = {}
    for nm, objs in out.items():
        rep[nm] = [pk.tri_count(o) for o in objs] + [tuple(round(d, 3) for d in objs[0].dimensions)]
        print(f"{nm:<28} tri {rep[nm][:3]}  dim {rep[nm][3]}")
    return rep


# ---- disposizione -------------------------------------------------------------------------------------------------
PANCHINE_X = [16.5 + 18 * k for k in range(13)]
CESTINI_PANCH = (16.5, 34.5, 70.5, 88.5, 124.5, 142.5, 178.5, 196.5, 232.5)   # passo medio 27 m [S]; OSM: X 18 e 42
RASTR_X = (61.5, 79.5, 97.5)        # nei varchi del filare 1 senza panchina, vicino a imbarco e chiosco
PARAB_X = (56.0, 60.0, 64.0, 68.0, 80.0, 84.0, 88.0)   # ogni 4 m in X 55-90, libero il pontile (X 70,5-77,5)


def layout():
    """Righe (asset, nome, X, Y, Z, rotZ_deg) in coordinate Blender."""
    rows = []
    bx, by, bz = BATT_POS
    rows.append(("SM_Morin_Battello", "Battello_01", bx, by, bz, BATT_ROTZ))
    ox, oy, oz = PONT_ORIG
    rows.append(("SM_Morin_PontileImbarco", "Pontile_Imbarco", ox, oy, oz, 0.0))
    lx, ly, lz = BIGL_LOCAL
    rows.append(("SM_Morin_Biglietteria", "Biglietteria", ox + lx, oy + ly, oz + lz, 0.0))
    for k, x in enumerate(CESTINI_PANCH):
        rows.append(("SM_Morin_Cestino", f"Cestino_{k:02d}", x + 2.05, 92.1, 0.15, 0.0))
    for k, x in enumerate(RASTR_X):
        rows.append(("SM_Morin_Rastrelliera", f"Rastrelliera_{k:02d}", x, 92.6, 0.15, 0.0))
    for k, x in enumerate(PARAB_X):
        rows.append(("SM_Banchina_Parabordo", f"Parabordo_{k:02d}", x, ciglio_y(x) + 0.04, -0.52, 0.0))
    return rows


def rows_ue():
    out = []
    for a, n, x, y, z, rz in layout():
        yaw = -rz
        if a in ("SM_Banchina_Parabordo", "SM_Morin_PontileImbarco", "SM_Morin_Biglietteria"):
            yaw = YAW_BANCHINA   # stessa rotazione dei moduli banchina v2
        out.append((a, n, x * 100, -y * 100, z * 100, yaw, 0.0, 0.0))
    return out


def write_csv(path="exports/imbarco/imbarco_posizioni_v1.csv"):
    def f(v, nd=2):
        s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
        return "0.0" if s in ("0", "-0", "") else (s if "." in s else s + ".0")
    os.makedirs(os.path.dirname(f"{PROJ}/{path}"), exist_ok=True)
    lines = ["asset,nome,x,y,z,yaw,pitch,roll"] + [
        f"{a},{n},{f(x)},{f(y)},{f(z)},{f(w, 4)},{f(p)},{f(r)}" for a, n, x, y, z, w, p, r in rows_ue()]
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(lines) - 1


def build_context(name="IMBARCO_Contesto"):
    """Istanze (linked duplicates) delle LOD0 nelle posizioni del CSV, per i render."""
    coll = pk._coll(name)
    for a, n, x, y, z, rz in layout():
        on = f"IMB_{n}"
        o = bpy.data.objects.get(on)
        if o is None:
            o = bpy.data.objects.new(on, bpy.data.objects[a].data)
            coll.objects.link(o)
        o.data = bpy.data.objects[a].data
        o.location = (x, y, z)
        rz2 = rz if a not in ("SM_Banchina_Parabordo", "SM_Morin_PontileImbarco", "SM_Morin_Biglietteria") \
            else -YAW_BANCHINA
        o.rotation_euler = (0, 0, math.radians(rz2))
    return len(coll.objects)


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in bpy.context.scene.objects}
    for o in bpy.data.collections[KIT].objects:
        o.hide_viewport = False
        o.hide_set(False)
    bpy.context.view_layer.update()
    reps = []
    try:
        for nm in ASSETS:
            for lod in range(3):
                on = nm + _sfx(lod)
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


# =================================================================================================================
# confronto con la foto del parcheggio (lato battelli)
# =================================================================================================================
FOTO = PROJ + "/ref/foto/vista/parcheggio_iniziale.png"


def render_confronto(cam="CAM_Park_F1", out="docs/qa/arte_imbarco_v1_confronto.png", tmp=None):
    tmp = tmp or os.path.join(os.environ.get("TEMP", PROJ), "morin_imbarco_render.png")
    for o in bpy.data.collections[KIT].objects:   # le LOD0 stanno nell'origine: nel render solo le istanze
        o.hide_render = True
    mm.render(cam, tmp, width=1375)
    a = tp.load(FOTO)[..., :3]
    b = tp.load(tmp)[..., :3]
    if b.shape[1] != a.shape[1]:
        b = tp.resize(b, a.shape[1], int(round(b.shape[0] * a.shape[1] / b.shape[1])))
    sep = np.ones((6, a.shape[1], 3), np.float32)
    tp.save(np.concatenate([a, sep, b], 0), f"{PROJ}/{out}")
    return out, tmp
