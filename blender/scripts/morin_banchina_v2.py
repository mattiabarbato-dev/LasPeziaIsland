"""morin_banchina_v2.py — dettagli della banchina del Blocco 1 (v2, 2026-11-20).

Asset (nomi NUOVI, mai sopra quelli gia' in UEFN):
  SM_Banchina_Mod4m_v2       modulo da 4 m a grandi blocchi bianchi arrotondati (3 blocchi da 1,333 m [S])
  SM_Banchina_Mod4m_Nicchia  stesso modulo con la nicchia della scaletta (centro a X locale 0,80, come le 4 scalette posate)
  SM_Banchina_Scaletta_v2    scaletta a filo dentro la nicchia, geometria e UV puliti
  SM_Banchina_Bitta_v2       bitta v1 con UV degeneri corretti (avvisi normali/tangenti all'import)
  SM_Banchina_Testata        angolo verso il molo del ponte: smusso a 45 gradi (X 19,2 -> 10,2) e ritorno lungo il ciglio est del molo fino a Y 62
  SM_Banchina_Testata_Fine   chiusura dell'ultimo modulo (X 251,2)
  SM_Morin_AncoraMonumento   ancora ammiragliato nera adagiata (marra e un'estremita' del ceppo a terra) su basamento basso

Riferimenti: ref/banchina.md, ref/sezione.md, ref/elementi.md (ancora 1 X 226 Y 83, OSM 5913835511), ref/radice_molo.md;
foto ref/foto/vista/banchina_vista_montagne_verso_ponte.jpg (ciglio a blocchi e ancora).

Esegui dentro blender/arte_banchina_v2.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_banchina_v2 as bv; importlib.reload(bv)
    bv.make_textures(); bv.build_materials(); bv.build_all(); bv.write_csv(); bv.export_all()

Convenzioni: come il modulo v1 (origine sul ciglio lato mare in alto, X lungo la passeggiata, +Y verso la citta', Z 0 = piano
delle lastre). Il CSV e' in coordinate UE: (X*100, -Y*100, Z*100), yaw UE = -rotZ Blender.
"""
import math
import os
import shutil

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_texphoto as tp
import morin_molo as mm

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/banchina_v2"
OLDTEX = PROJ + "/blender/textures"
KIT = "BANCHINA_v2"
EXPDIR = "//../exports/banchina_v2"

# ---- sezione del ciglio (m) ---------------------------------------------------------------------------------------
L = 4.0          # modulo
D = 0.55         # larghezza in pianta del blocco (come v1: le lastre partono a 0,545)
HB = 0.50        # altezza del blocco sulla faccia a mare [S] (foto: rapporto lunghezza/altezza ~2,7)
R = 0.15         # raggio del toro sul lato mare [S] (foto: spigolo molto arrotondato)
SLOPE = 0.02     # pendenza della faccia superiore verso il mare (v1: 2,2 cm)
OV = 0.04        # aggetto del blocco sul paramento
ZB = -3.0        # piede del paramento
NBLK = 3         # blocchi per modulo -> 1,333 m [S]
JE, JW = 0.015, 0.02   # giunto: rientro e larghezza dello smusso alle teste dei blocchi
NX0, NX1, ND = 0.40, 1.20, 0.24   # nicchia: da X 0,40 a 1,20 (centro 0,80), profonda 0,24 dal ciglio
NCH = 0.03       # smusso del bordo della nicchia
TV = 2.5         # m per ripetizione della texture dei blocchi
MAT_B, MAT_P, MAT_G = "M_Banchina_Blocchi", "M_Banchina_Paramento", "M_Banchina_Ghisa"
ARC = {0: 6, 1: 2, 2: 2}          # segmenti del toro per LOD
JOINTS = {0: True, 1: True, 2: False}

# ---- posa in UE (docs/uefn_arte.md §4) ---------------------------------------------------------------------------
YAW_UE = 0.1241


def line_ue(x):
    """Retta dei moduli banchina in UE (8 uu verso il mare rispetto al ciglio del blockout)."""
    return -8036.16 + 0.0021664 * x


# =================================================================================================================
# texture e materiali
# =================================================================================================================
def make_textures(seed=20261120):
    """T_Banchina_Blocchi_D: la texture v1 del ciglio (foto utente + Poly Haven CC0) ritarata sul colore dei blocchi
    nella foto banchina_vista_montagne_verso_ponte.jpg (faccia al sole 206,208,205 sRGB; piano 187,187,185 -> albedo
    ~200,199,193), piu' contrasto e macchie larghe. N e ORM: quelli v1, copiati con il nuovo nome."""
    os.makedirs(TEXDIR, exist_ok=True)
    old = tp.load(f"{OLDTEX}/T_Banchina_Ciglio_D.png")[..., :3]
    lum = old.mean(2)
    rel = 1.0 + (lum / lum.mean() - 1.0) * 1.6
    h, w = lum.shape
    st = mm._noise(h, w, 70, seed)
    st2 = mm._noise(h, w, 18, seed + 1)
    f = 1.0 - 0.06 * np.clip(st, 0, 3) - 0.025 * np.clip(st2, 0, 3)
    target = np.array([200, 199, 193], np.float32) / 255.0
    d = np.clip(target[None, None, :] * (rel * f)[..., None], 0, 1)
    tp.save(d, f"{TEXDIR}/T_Banchina_Blocchi_D.png")
    for k in ("N", "ORM"):
        shutil.copyfile(f"{OLDTEX}/T_Banchina_Ciglio_{k}.png", f"{TEXDIR}/T_Banchina_Blocchi_{k}.png")
    print("texture:", sorted(os.listdir(TEXDIR)))


def build_materials():
    pk._pbr_material(MAT_B, f"{TEXDIR}/T_Banchina_Blocchi_D.png", f"{TEXDIR}/T_Banchina_Blocchi_N.png",
                     f"{TEXDIR}/T_Banchina_Blocchi_ORM.png")
    for m in (MAT_P, MAT_G):
        assert m in bpy.data.materials, m


# =================================================================================================================
# utilita bmesh
# =================================================================================================================
def _uvl(bm):
    return bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")


def _face(bm, verts, mi, uvs, want=None):
    """uvs: lista di (u, v) allineata a verts. want: direzione desiderata della normale."""
    f = bm.faces.new(verts)
    f.material_index = mi
    lay = _uvl(bm)
    m = {v: uv for v, uv in zip(verts, uvs)}
    if want is not None:
        f.normal_update()
        if f.normal.dot(Vector(want)) < 0:
            f.normal_flip()
    for lp in f.loops:
        lp[lay].uv = m[lp.vert]
    return f


def _ztop(n):
    return -SLOPE * (1.0 - n / D)


def profile(arc, notch=False):
    """Sezione del blocco [(n, z, s)]: n = distanza dal ciglio verso terra, s = ascissa curvilinea (per le UV).
    Dal bordo lato citta' in alto al piede lato mare, poi il dente dell'aggetto. Con notch=True include i punti
    a n = ND+NCH e ND sul piano (servono alla nicchia)."""
    pts = [(D, 0.0)]
    if notch:
        pts += [(ND + NCH, _ztop(ND + NCH)), (ND, _ztop(ND))]
    zc = _ztop(R) - R
    pts.append((R, _ztop(R)))
    for k in range(1, arc + 1):
        t = 0.5 * math.pi * k / arc
        pts.append((R - R * math.sin(t), zc + R * math.cos(t)))
    pts += [(0.0, -HB), (OV, -HB)]
    out, s = [], 0.0
    for i, (n, z) in enumerate(pts):
        if i:
            s += math.hypot(n - pts[i - 1][0], z - pts[i - 1][1])
        out.append((n, z, s))
    return out


def inset(prof, e=JE):
    """Profilo rientrato per lo smusso dei giunti (stesso numero di punti)."""
    zc = _ztop(R) - R
    out = []
    for n, z, s in prof:
        if n >= R - 1e-6 and z > -HB + 1e-6:         # piano superiore
            out.append((n, z - e, s))
        elif z > -HB + 1e-6:                          # toro: verso il centro
            dn, dz = R - n, zc - z
            l = math.hypot(dn, dz) or 1.0
            out.append((n + e * dn / l, z + e * dz / l, s))
        elif n < 1e-6:                                # piede sul ciglio
            out.append((e, z, s))
        else:
            out.append((n, z, s))
    return out


def truncated(prof):
    """Sezione del blocco dietro la nicchia: dal bordo citta' fino a n = ND con smusso, poi giu' fino a -HB."""
    head = [p for p in prof if p[0] >= ND + NCH - 1e-6]
    s0 = head[-1][2]
    return head + [(ND, _ztop(ND) - NCH, s0 + NCH * 1.414), (ND, -HB, s0 + NCH * 1.414 + HB)]


class Ring:
    def __init__(self, O, u, k, prof, blk, t, jit=(0.0, 0.0)):
        self.O, self.u, self.k, self.prof, self.blk, self.t = Vector(O), Vector(u), k, prof, blk, t
        dn, dz = jit
        self.pts = [Vector((self.O.x + (n + dn) * k * self.u.x, self.O.y + (n + dn) * k * self.u.y, z + dz))
                    for n, z, s in prof]
        self.verts = None

    def make(self, bm):
        self.verts = [bm.verts.new(p) for p in self.pts]
        return self


def _bridge(bm, A, B, mi, uoff, voff):
    """Quad fra due anelli con lo stesso numero di punti. UV: u = ascissa lungo il percorso, v = ascissa del profilo."""
    for i in range(len(A.verts) - 1):
        vs = [A.verts[i], A.verts[i + 1], B.verts[i + 1], B.verts[i]]
        if len({v.index for v in vs}) < 4 and any(v.index >= 0 for v in vs):
            pass
        uvs = [((A.t + uoff) / TV, A.prof[i][2] / TV + voff), ((A.t + uoff) / TV, A.prof[i + 1][2] / TV + voff),
               ((B.t + uoff) / TV, B.prof[i + 1][2] / TV + voff), ((B.t + uoff) / TV, B.prof[i][2] / TV + voff)]
        _face(bm, vs, mi, uvs)


def _blk_off(b):
    r = np.random.default_rng(1000 + b)
    return float(r.uniform(0, 7)), float(r.uniform(0, 3)), (float(r.uniform(-0.003, 0.003)), float(r.uniform(-0.004, 0.002)))


def _run(bm, rings, mi=0):
    """Crea i vertici e unisce anelli consecutivi; il blocco di ogni striscia e' quello dell'anello non rientrato."""
    for r in rings:
        r.make(bm)
    for a, b in zip(rings[:-1], rings[1:]):
        blk = b.blk if a.blk is None else a.blk
        uo, vo, _ = _blk_off(blk if blk is not None else 0)
        _bridge(bm, a, b, mi, uo, vo)


def _cap(bm, ring, want, mi=0):
    """Testa piena di un anello (profilo + spigolo in basso lato citta')."""
    extra = Vector((ring.O.x + D * ring.k * ring.u.x, ring.O.y + D * ring.k * ring.u.y, -HB))
    vs = list(ring.verts) + [bm.verts.new(extra)]
    # il dente dell'aggetto (ultimo punto) e' gia' sul piano -HB: va bene nel poligono
    uvs = [(((p.xy - ring.O.xy).length) / TV, (p.z + 3) / TV) for p in [v.co for v in vs]]
    return _face(bm, vs, mi, uvs, want)


def _par_quad(bm, a, b, ta, tb, z0, z1, want=None, mi=1):
    """Paramento fra i punti in pianta a e b (2D), da z0 a z1. UV come v1: u = ascissa/4, v = (z+3)/2,65."""
    vs = [bm.verts.new((a.x, a.y, z0)), bm.verts.new((b.x, b.y, z0)), bm.verts.new((b.x, b.y, z1)), bm.verts.new((a.x, a.y, z1))]
    uvs = [(ta / 4, (z0 + 3) / 2.65), (tb / 4, (z0 + 3) / 2.65), (tb / 4, (z1 + 3) / 2.65), (ta / 4, (z1 + 3) / 2.65)]
    return _face(bm, vs, mi, uvs, want)


def _finish(name, bm, mats, coll, smooth=40.0):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    o = pk._finish(name, bm, mats, coll, uv=None, smooth_angle=smooth)
    me = o.data
    for l in [l for l in me.uv_layers if l.name != "UVMap"]:
        me.uv_layers.remove(l)
    return o


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


# =================================================================================================================
# moduli dritti (v2 e nicchia) e testata finale
# =================================================================================================================
def _straight_rings(x0, x1, nblk, lod, blk0=0, end_inset=True):
    """Anelli di una fila dritta di blocchi da x0 a x1 (inward +Y)."""
    P = profile(ARC[lod])
    Pi = inset(P)
    rings = []
    bx = [x0 + (x1 - x0) * i / nblk for i in range(nblk + 1)]
    if not JOINTS[lod]:
        return [Ring((x0, 0), (0, 1), 1.0, P, blk0, x0), Ring((x1, 0), (0, 1), 1.0, P, blk0, x1)]
    for j in range(nblk):
        b = blk0 + j
        jit = _blk_off(b)[2] if lod == 0 else (0.0, 0.0)
        a0, a1 = bx[j], bx[j + 1]
        if j == 0:
            rings.append(Ring((a0, 0), (0, 1), 1.0, Pi if end_inset else P, None, a0))
        rings.append(Ring((a0 + JW, 0), (0, 1), 1.0, P, b, a0 + JW, jit))
        rings.append(Ring((a1 - JW, 0), (0, 1), 1.0, P, b, a1 - JW, jit))
        rings.append(Ring((a1, 0), (0, 1), 1.0, Pi, None, a1))
    return rings


def build_mod(coll, lod=0, name="SM_Banchina_Mod4m_v2"):
    bm = bmesh.new()
    _uvl(bm)
    _run(bm, _straight_rings(0.0, L, NBLK, lod))
    _par_quad(bm, Vector((0, OV)), Vector((L, OV)), 0, L, ZB, -HB, (0, -1, 0))
    return _finish(name + _sfx(lod), bm, [MAT_B, MAT_P], coll)


def build_nicchia(coll, lod=0, name="SM_Banchina_Mod4m_Nicchia"):
    """Modulo con la nicchia (X 0,40-1,20, profonda 0,24) intagliata nel primo blocco e nel paramento."""
    bm = bmesh.new()
    _uvl(bm)
    arc = ARC[lod]
    P = profile(arc, notch=True)
    Pi = inset(P)
    T = truncated(P)
    bl = L / NBLK
    jit = _blk_off(0)[2] if lod == 0 else (0.0, 0.0)
    # blocco 0 con la nicchia
    front_a = [Ring((0, 0), (0, 1), 1, Pi, None, 0.0), Ring((JW, 0), (0, 1), 1, P, 0, JW, jit), Ring((NX0, 0), (0, 1), 1, P, 0, NX0, jit)]
    front_b = [Ring((NX1, 0), (0, 1), 1, P, 0, NX1, jit), Ring((bl - JW, 0), (0, 1), 1, P, 0, bl - JW, jit),
               Ring((bl, 0), (0, 1), 1, Pi, None, bl)]
    if not JOINTS[lod]:
        front_a = [Ring((0, 0), (0, 1), 1, P, 0, 0.0), Ring((NX0, 0), (0, 1), 1, P, 0, NX0)]
        front_b = [Ring((NX1, 0), (0, 1), 1, P, 0, NX1)]
    back = [Ring((NX0, 0), (0, 1), 1, T, 0, NX0, jit), Ring((NX1, 0), (0, 1), 1, T, 0, NX1, jit)]
    _run(bm, front_a)
    _run(bm, back)
    if JOINTS[lod]:
        _run(bm, front_b)
        _run(bm, _straight_rings(bl, L, NBLK - 1, lod, blk0=1))
    else:
        _run(bm, front_b + [Ring((L, 0), (0, 1), 1, P, 0, L)])
    # fianchi della nicchia nel blocco: parte del profilo con n <= ND+NCH, chiusa sul retro della nicchia
    for x, want, ring in ((NX0, (1, 0, 0), front_a[-1]), (NX1, (-1, 0, 0), front_b[0])):
        i0 = 1  # punto (ND+NCH) nel profilo con notch
        pts = [p for p in ring.pts[i0:]] + [Vector((x, ND, -HB)), Vector((x, ND, _ztop(ND) - NCH))]
        vs = [bm.verts.new(p) for p in pts]
        _face(bm, vs, 0, [(p.y / TV, (p.z + 3) / TV) for p in pts], want)
    # paramento: fronte, fondo e fianchi della nicchia
    _par_quad(bm, Vector((0, OV)), Vector((NX0, OV)), 0, NX0, ZB, -HB, (0, -1, 0))
    _par_quad(bm, Vector((NX1, OV)), Vector((L, OV)), NX1, L, ZB, -HB, (0, -1, 0))
    _par_quad(bm, Vector((NX0, ND)), Vector((NX1, ND)), NX0, NX1, ZB, -HB, (0, -1, 0))
    _par_quad(bm, Vector((NX0, OV)), Vector((NX0, ND)), NX0, NX0 + ND - OV, ZB, -HB, (1, 0, 0))
    _par_quad(bm, Vector((NX1, OV)), Vector((NX1, ND)), NX1, NX1 + ND - OV, ZB, -HB, (-1, 0, 0))
    return _finish(name + _sfx(lod), bm, [MAT_B, MAT_P], coll)


def build_fine(coll, lod=0, name="SM_Banchina_Testata_Fine"):
    """Testa di chiusura da 0,25 m dopo l'ultimo modulo (origine = fine del modulo 57, X 251,2)."""
    bm = bmesh.new()
    _uvl(bm)
    P = profile(ARC[lod])
    Pi = inset(P)
    E = 0.25
    if JOINTS[lod]:
        rings = [Ring((0, 0), (0, 1), 1, Pi, None, 0), Ring((JW, 0), (0, 1), 1, P, 99, JW),
                 Ring((E - JW, 0), (0, 1), 1, P, 99, E - JW), Ring((E, 0), (0, 1), 1, Pi, None, E)]
    else:
        rings = [Ring((0, 0), (0, 1), 1, P, 99, 0), Ring((E, 0), (0, 1), 1, P, 99, E)]
    _run(bm, rings)
    _cap(bm, rings[-1], (1, 0, 0))
    _par_quad(bm, Vector((0, OV)), Vector((E, OV)), 0, E, ZB, -HB, (0, -1, 0))
    _par_quad(bm, Vector((E, OV)), Vector((E, D)), 0, D - OV, ZB, -HB, (1, 0, 0))
    return _finish(name + _sfx(lod), bm, [MAT_B, MAT_P], coll)


# =================================================================================================================
# testata verso il molo del ponte
# =================================================================================================================
# Coordinate locali = modulo 00 (origine progetto X 19,2, Y 80,32). Blockout: smusso a 45 gradi da (19,2; 80,4) a
# (10,2; 71,4) e ciglio est del molo da (10,2; 71,4) a (9,99; 62,0). La testata sta 6-8 cm verso il mare, come i moduli.
TP2 = Vector((10.05 - 19.2, 62.0 - 80.32))     # piede sul molo (Y 62)
TP1 = Vector((-8.94, -8.94))                   # angolo smusso/molo (Y 71,38)
TP0 = Vector((0.0, 0.0))                       # attacco al modulo 00


def _ccw(d):
    return Vector((-d.y, d.x))


def build_testata(coll, lod=0, name="SM_Banchina_Testata"):
    bm = bmesh.new()
    _uvl(bm)
    P = profile(ARC[lod])
    Pi = inset(P)
    path = [TP2, TP1, TP0]
    d = [(path[i + 1] - path[i]).normalized() for i in range(2)]
    nrm = [_ccw(x) for x in d]
    lens = [(path[i + 1] - path[i]).length for i in range(2)]
    nb = [max(1, round(l / 1.333)) for l in lens]

    def miter(n1, n2):
        m = (n1 + n2).normalized()
        return m, 1.0 / m.dot(n1)

    m1, k1 = miter(nrm[0], nrm[1])
    m0, k0 = miter(nrm[1], Vector((0, 1)))
    rings = []
    blk = 100
    if JOINTS[lod]:
        rings.append(Ring(TP2, nrm[0], 1, Pi, None, 0.0))
        t0 = 0.0
        for seg in range(2):
            for j in range(nb[seg]):
                a = lens[seg] * j / nb[seg]
                b = lens[seg] * (j + 1) / nb[seg]
                if not (seg == 1 and j == 0):        # il blocco d'angolo attraversa il vertice TP1
                    rings.append(Ring(path[seg] + d[seg] * (a + JW), nrm[seg], 1, P, blk, t0 + a + JW))
                if seg == 0 and j == nb[0] - 1:
                    rings.append(Ring(TP1, m1, k1, P, blk, t0 + lens[0]))
                    continue
                last = seg == 1 and j == nb[1] - 1
                if last:
                    rings.append(Ring(TP0, m0, k0, P, blk, t0 + lens[1]))
                    rings.append(Ring(TP0, Vector((0, 1)), 1, Pi, None, t0 + lens[1] + 0.1))
                else:
                    rings.append(Ring(path[seg] + d[seg] * (b - JW), nrm[seg], 1, P, blk, t0 + b - JW))
                    rings.append(Ring(path[seg] + d[seg] * b, nrm[seg], 1, Pi, None, t0 + b))
                    blk += 1
            if seg == 0:
                blk += 1
                t0 = lens[0]
    else:
        rings = [Ring(TP2, nrm[0], 1, P, blk, 0.0), Ring(TP1, m1, k1, P, blk, lens[0]),
                 Ring(TP0, m0, k0, P, blk, lens[0] + lens[1]), Ring(TP0, Vector((0, 1)), 1, P, blk, lens[0] + lens[1] + 0.1)]
    _run(bm, rings)
    _cap(bm, rings[0], tuple(-d[0]) + (0,))
    # paramento lungo il percorso (a OV verso terra), con i raccordi d'angolo
    pp = [TP2 + nrm[0] * OV, TP1 + m1 * (OV * k1), TP0 + m0 * (OV * k0), TP0 + Vector((0, OV))]
    tt = [0.0, lens[0], lens[0] + lens[1], lens[0] + lens[1] + 0.1]
    for i in range(3):
        a, b = pp[i], pp[i + 1]
        want = _ccw(b - a)
        _par_quad(bm, a, b, tt[i], tt[i + 1], ZB, -HB, (-want.x, -want.y, 0))
    _par_quad(bm, pp[0], TP2 + nrm[0] * D, 0, D - OV, ZB, -HB, tuple(-d[0]) + (0,))
    return _finish(name + _sfx(lod), bm, [MAT_B, MAT_P], coll)


# =================================================================================================================
# scaletta v2 e bitta v2
# =================================================================================================================
def _tube_r(bm, pts, radii, sides, mi=0, cap=True, uvs=0.25):
    """Tubo a raggio variabile lungo una polilinea (trasporto parallelo). UV: u = giro, v = lunghezza / (uvs*4)."""
    pts = [Vector(p) for p in pts]
    tang = []
    for i in range(len(pts)):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tang.append((b - a).normalized())
    up = Vector((0, 0, 1)) if abs(tang[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tang[0].cross(up).normalized()
    rings, acc = [], [0.0]
    for i in range(1, len(pts)):
        acc.append(acc[-1] + (pts[i] - pts[i - 1]).length)
    for i, p in enumerate(pts):
        if i > 0:
            nrm = (nrm - tang[i] * nrm.dot(tang[i])).normalized()
        bi = tang[i].cross(nrm)
        rings.append([bm.verts.new(p + radii[i] * (math.cos(2 * math.pi * k / sides) * nrm + math.sin(2 * math.pi * k / sides) * bi))
                      for k in range(sides)])
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(sides):
            k1 = (k + 1) % sides
            u0, u1 = k / sides * uvs * 4, (k + 1) / sides * uvs * 4
            _face(bm, [a[k], a[k1], b[k1], b[k]], mi, [(u0, acc[i]), (u1, acc[i]), (u1, acc[i + 1]), (u0, acc[i + 1])])
    if cap:
        for ring, sgn in ((rings[0], -1), (rings[-1], 1)):
            t = tang[0] if sgn < 0 else tang[-1]
            _face(bm, list(ring), mi, [(0.5 + 0.5 * math.cos(2 * math.pi * k / sides), 0.5 + 0.5 * math.sin(2 * math.pi * k / sides))
                                       for k in range(sides)], tuple(t * sgn))
    return rings


def _arc_pts(c, r, a0, a1, n, plane="yz", x=0.0):
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        out.append((x, c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return out


SC_X = 0.25      # meta' interasse dei montanti
SC_Y = 0.035     # asse dei montanti: 1,5 cm dentro il ciglio (a filo)
SC_Z0 = -2.85


def build_scaletta(coll, lod=0, name="SM_Banchina_Scaletta_v2"):
    """Scaletta alla marinara dentro la nicchia: montanti a filo del ciglio, pioli ogni 0,30 m, 3 staffe al fondo
    della nicchia, maniglioni che escono di 0,45 m e scendono sul blocco dietro la nicchia (Y 0,40)."""
    bm = bmesh.new()
    _uvl(bm)
    sides = {0: 8, 1: 5, 2: 3}[lod]
    arcn = {0: 6, 1: 3, 2: 2}[lod]
    zt, rr = 0.30, 0.185
    for sx in (-SC_X, SC_X):
        pts = [(sx, SC_Y, SC_Z0), (sx, SC_Y, zt)]
        pts += _arc_pts((SC_Y + rr, zt), rr, math.pi, 0.0, arcn, x=sx)[1:]
        pts += [(sx, SC_Y + 2 * rr, -0.03)]
        _tube_r(bm, pts, [0.021] * len(pts), sides, 0)
    step = 0.30 if lod < 2 else 0.60
    z = SC_Z0 + 0.15
    while z < -0.10:
        _tube_r(bm, [(-SC_X, SC_Y, z), (SC_X, SC_Y, z)], [0.015, 0.015], max(3, sides - 2), 0, cap=False)
        z += step
    if lod < 2:
        for zb in (-2.55, -1.55, -0.65):
            for sx in (-SC_X, SC_X):
                _tube_r(bm, [(sx, SC_Y, zb), (sx, ND + 0.02, zb)], [0.014, 0.014], max(3, sides - 3), 0, cap=False)
    return _finish(name + _sfx(lod), bm, [MAT_G], coll, smooth=50.0)


def _clean_copy(src_name, dst_name, coll):
    """Copia valutata di una mesh v1 con UV delle facce degeneri riproiettati (box) e normali ricalcolate."""
    src = bpy.data.objects[src_name]
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(src.evaluated_get(dg))
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    uv = bm.loops.layers.uv.active
    fixed = 0
    for f in bm.faces:
        pts = [l[uv].uv.copy() for l in f.loops]
        a = sum(pts[i].x * pts[(i + 1) % len(pts)].y - pts[(i + 1) % len(pts)].x * pts[i].y for i in range(len(pts)))
        if abs(a) < 2e-9:
            n = f.normal
            ax = max(range(3), key=lambda i: abs(n[i]))
            for l in f.loops:
                c = l.vert.co
                l[uv].uv = ((c.y, c.z), (c.x, c.z), (c.x, c.y))[ax]
            fixed += 1
    mats = [m.name if m else None for m in src.data.materials]
    o = pk._finish(dst_name, bm, mats, coll, uv=None, smooth_angle=None)
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.set_sharp_from_angle(angle=math.radians(45))
    return o, fixed


def build_bitta(coll):
    """Le LOD v1 hanno il Decimate: la collezione sorgente deve essere attiva nel view layer per valutarlo."""
    lc = bpy.context.view_layer.layer_collection.children.get("Banchina")
    was = lc.exclude if lc else None
    if lc:
        lc.exclude = False
        bpy.context.view_layer.update()
    out = []
    for lod in range(3):
        o, fx = _clean_copy("SM_Banchina_Bitta" + _sfx(lod), "SM_Banchina_Bitta_v2" + _sfx(lod), coll)
        print(o.name, "UV corretti:", fx)
        out.append(o)
    u = bpy.data.objects["UCX_SM_Banchina_Bitta_00"]
    bm = bmesh.new()
    bm.from_mesh(u.data)
    pk._ucx_mesh("UCX_SM_Banchina_Bitta_v2_00", bm, coll)
    if lc:
        lc.exclude = was
    return out


# =================================================================================================================
# ancora monumentale
# =================================================================================================================
AN_LS = 3.0        # fusto [S]
AN_RA = 1.0        # raggio delle marre [S]
AN_ST = 2.8        # ceppo [S]
AN_BASE = 0.04       # basamento basso [S] (in foto quasi a raso)
AN_PLAN = (-0.45, -0.89)   # pianta: diamante (lato citta') -> cicala (verso il mare e un po' verso il ponte), dalla foto [S]


def _palm(bm, tip, tang, side, mi):
    """Patta: lastra a punta di lancia, piano = (tangente del braccio, Y), spessore 4 cm."""
    t = tang.normalized()
    w = Vector((0, 1, 0))
    nn = t.cross(w).normalized()
    shape = [(0.10, 0.0), (-0.06, 0.24), (-0.42, 0.11), (-0.55, 0.0), (-0.42, -0.11), (-0.06, -0.24)]
    rings = []
    for off in (-0.022, 0.022):
        rings.append([bm.verts.new(tip + t * a + w * b + nn * off) for a, b in shape])
    uvs = [(0.5 + a, 0.5 + b) for a, b in shape]
    _face(bm, rings[0], mi, uvs, tuple(-nn))
    _face(bm, rings[1], mi, uvs, tuple(nn))
    for k in range(len(shape)):
        k1 = (k + 1) % len(shape)
        mid = (rings[0][k].co + rings[0][k1].co) / 2 - tip
        _face(bm, [rings[0][k], rings[0][k1], rings[1][k1], rings[1][k]], mi, [(0, 0), (0.1, 0), (0.1, 0.05), (0, 0.05)],
              tuple(mid - nn * mid.dot(nn)))


def _anchor_bm(lod):
    """Ancora ammiragliato in posizione 'da nave': fusto lungo +X dal diamante (x 0) alla cicala, marre nel piano XZ,
    ceppo lungo Y. Restituisce bmesh e i punti d'appoggio."""
    bm = bmesh.new()
    _uvl(bm)
    sd = {0: 14, 1: 9, 2: 4}[lod]
    an = {0: 14, 1: 8, 2: 3}[lod]
    Ls = AN_LS
    xs = [-0.08, 0.6, 1.4, Ls - 0.42, Ls - 0.40, Ls - 0.16, Ls - 0.14, Ls]
    rs = [0.115, 0.10, 0.09, 0.08, 0.105, 0.105, 0.075, 0.07]
    _tube_r(bm, [(x, 0, 0) for x in xs], rs, sd, 0)
    # marre: arco di cerchio con centro sul fusto
    c = Vector((AN_RA, 0, 0))
    tips = []
    for sgn in (1, -1):
        a0, a1 = math.pi, math.pi - sgn * math.radians(58)
        pts = [c + AN_RA * Vector((math.cos(a0 + (a1 - a0) * i / an), 0, math.sin(a0 + (a1 - a0) * i / an))) for i in range(an + 1)]
        radii = [0.11 - 0.045 * i / an for i in range(an + 1)]
        _tube_r(bm, pts, radii, max(4, sd - 2), 0)
        tang = pts[-1] - pts[-2]
        tip = pts[-1]
        _palm(bm, tip + tang.normalized() * 0.02, tang, sgn, 0)
        tips.append(tip + tang.normalized() * 0.12)
    pk._sphere(bm, (0.0, 0.0, 0.0), 0.15, max(6, sd - 2), {0: 5, 1: 4, 2: 3}[lod])
    # ceppo con le palle alle estremita'
    xst = Ls - 0.28
    _tube_r(bm, [(xst, -AN_ST / 2, 0), (xst, 0, 0), (xst, AN_ST / 2, 0)], [0.055, 0.075, 0.055], max(4, sd - 2), 0)
    ends = []
    for sy in (-1, 1):
        pk._sphere(bm, (xst, sy * AN_ST / 2, -0.085), 0.085, max(6, sd - 2), {0: 5, 1: 4, 2: 3}[lod])
        ends.append(Vector((xst, sy * (AN_ST / 2 + 0.04), 0)))
    # cicala (anello) nel piano XZ
    if lod < 2:
        cr, rr_ = 0.16, 0.032
        n1, n2 = {0: 14, 1: 8}[lod], {0: 6, 1: 4}[lod]
        ring = [[bm.verts.new((Ls + cr + (cr + rr_ * math.cos(2 * math.pi * j / n2)) * math.cos(2 * math.pi * i / n1) - cr,
                                rr_ * math.sin(2 * math.pi * j / n2),
                                (cr + rr_ * math.cos(2 * math.pi * j / n2)) * math.sin(2 * math.pi * i / n1)))
                 for j in range(n2)] for i in range(n1)]
        for i in range(n1):
            for j in range(n2):
                a, b = ring[i], ring[(i + 1) % n1]
                j1 = (j + 1) % n2
                f = bm.faces.new([a[j], b[j], b[j1], a[j1]])
                f.material_index = 0
        for f in bm.faces:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm, tips, ends


def _rest_matrix():
    """Rotazione che appoggia diamante, punta della marra bassa e un'estremita' del ceppo sul piano, piu' l'imbardata."""
    bm, tips, ends = _anchor_bm(2)
    pts = [v.co.copy() for v in bm.verts]
    bm.free()
    up_tip, lo_tip = tips[0], tips[1]   # tips[0] ha z > 0
    C = Vector((-0.20, 0, 0))
    best = None
    for S in ends:
        n = (lo_tip - C).cross(S - C).normalized()
        if n.dot(up_tip - C) < 0:
            n = -n
        # tutto il resto deve stare sopra il piano
        dmin = min((p - C).dot(n) for p in pts)
        if best is None or dmin > best[0]:
            best = (dmin, n, S)
    _, n, S = best
    rot = n.rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4()
    # imbardata: proiezione del fusto (dal diamante alla cicala) lungo AN_PLAN
    sh = (rot @ Vector((1, 0, 0)))
    ang = math.atan2(AN_PLAN[1], AN_PLAN[0]) - math.atan2(sh.y, sh.x)
    M = Matrix.Rotation(ang, 4, "Z") @ rot
    zmin = min((M @ p).z for p in pts)
    return Matrix.Translation((0, 0, AN_BASE - zmin + 0.005)) @ M


def build_ancora(coll, lod=0, name="SM_Morin_AncoraMonumento", M=None, base=None):
    M = M or _rest_matrix()
    bm, tips, ends = _anchor_bm(lod)
    bm.transform(M)
    pk._uv_box(bm, [MAT_G], ())
    # basamento: lastra bassa sotto l'impronta in pianta, 0,12 m di margine
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    m = 0.12
    x0, x1, y0, y1 = base or (min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m)
    n0 = len(bm.faces)
    pk._box(bm, x0, x1, y0, y1, 0.0, AN_BASE, mi=1, faces=("top", "xn", "xp", "yn", "yp"))
    bm.faces.ensure_lookup_table()
    lay = _uvl(bm)
    for f in list(bm.faces)[n0:]:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            c = l.vert.co
            l[lay].uv = ((c.y / TV, c.z / TV), (c.x / TV, c.z / TV), (c.x / TV, c.y / TV))[ax]
    o = _finish(name + _sfx(lod), bm, [MAT_G, MAT_B], coll, smooth=50.0)
    return o, M, (x0, x1, y0, y1)


def _ucx_ancora(coll, M, base):
    bm, tips, ends = _anchor_bm(2)
    bm.transform(M)
    pts = [v.co.copy() for v in bm.verts]
    bm.free()
    sh0, sh1 = M @ Vector((-0.2, 0, 0)), M @ Vector((AN_LS + 0.35, 0, 0))
    xst = AN_LS - 0.28
    st0, st1 = M @ Vector((xst, -AN_ST / 2 - 0.1, 0)), M @ Vector((xst, AN_ST / 2 + 0.1, 0))

    def capsule_box(a, b, r):
        d = (b - a).normalized()
        u = d.cross(Vector((0, 0, 1)))
        u = u.normalized() if u.length > 1e-3 else Vector((1, 0, 0))
        w = d.cross(u).normalized()
        return [p + su * r * u + sw * r * w for p in (a, b) for su in (-1, 1) for sw in (-1, 1)]

    name = "SM_Morin_AncoraMonumento"
    pk._ucx_hull(name, 0, capsule_box(sh0, sh1, 0.12), coll)
    pk._ucx_hull(name, 1, capsule_box(st0, st1, 0.10), coll)
    arms = [p for p in pts if (M.inverted() @ p).x < AN_RA * 1.05 and abs((M.inverted() @ p).y) < 0.3]
    pk._ucx_hull(name, 2, arms, coll)
    x0, x1, y0, y1 = base
    pk._ucx(name, [(x0, x1, y0, y1, -0.01, AN_BASE)], coll, start=3)


# =================================================================================================================
# collisioni
# =================================================================================================================
def build_ucx(coll):
    for nm in ("SM_Banchina_Mod4m_v2", "SM_Banchina_Mod4m_Nicchia"):
        pk._ucx(nm, [(0.0, L, 0.0, D, ZB, -0.005)], coll)
    pk._ucx("SM_Banchina_Testata_Fine", [(0.0, 0.25, 0.0, D, ZB, -0.005)], coll)
    # scaletta: box nella nicchia (sporge 3 cm come appiglio) + maniglioni
    pk._ucx("SM_Banchina_Scaletta_v2", [(-0.30, 0.30, -0.03, ND, SC_Z0, -0.02),
                                        (-SC_X - 0.025, -SC_X + 0.025, 0.0, SC_Y + 0.40, -0.02, 0.50),
                                        (SC_X - 0.025, SC_X + 0.025, 0.0, SC_Y + 0.40, -0.02, 0.50)], coll)
    # testata: un convesso per tratto
    nm = "SM_Banchina_Testata"
    d0 = (TP1 - TP2).normalized(); d1 = (TP0 - TP1).normalized()
    segs = [(TP2, TP1 + d0 * 0.3, _ccw(d0)), (TP1 - d1 * 0.3, TP0, _ccw(d1))]
    for i, (a, b, n) in enumerate(segs):
        pts = [Vector((p.x, p.y, z)) for p in (a, b, a + n * D, b + n * D) for z in (ZB, -0.005)]
        pk._ucx_hull(nm, i, pts, coll)
    pk._ucx_hull(nm, 2, [Vector((p[0], p[1], z)) for p in ((0, 0), (0, D), (-0.4, D), (-0.4, -0.4)) for z in (ZB, -0.005)], coll)


# =================================================================================================================
# build, CSV, export
# =================================================================================================================
LODDED = ["SM_Banchina_Mod4m_v2", "SM_Banchina_Mod4m_Nicchia", "SM_Banchina_Scaletta_v2", "SM_Banchina_Bitta_v2",
          "SM_Banchina_Testata", "SM_Banchina_Testata_Fine", "SM_Morin_AncoraMonumento"]


def build_all():
    coll = pk._coll(KIT)
    out = []
    M = _rest_matrix()
    base0 = None
    for lod in range(3):
        out += [build_mod(coll, lod), build_nicchia(coll, lod), build_scaletta(coll, lod), build_testata(coll, lod),
                build_fine(coll, lod)]
        o, _, base = build_ancora(coll, lod, M=M, base=base0)
        out.append(o)
        base0 = base0 or base
    out += build_bitta(coll)
    build_ucx(coll)
    _ucx_ancora(coll, M, base0)
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    rep = {}
    for o in sorted(out, key=lambda o: o.name):
        rep[o.name] = (pk.tri_count(o), tuple(round(d, 3) for d in o.dimensions))
        print(f"{o.name:<34} tri {rep[o.name][0]:>5}  dim {rep[o.name][1]}")
    return rep


ANCORA_XY = (226.6, 84.5)     # origine (diamante); centro dell'ingombro a (226,0; 83,3) = OSM 5913835511 (226; 83), basamento a 1,9 m dal ciglio
NICCHIA_IDX = (6, 18, 30, 42)  # moduli con le scalette X 44/92/140/188


def rows_ue():
    """Righe CSV in coordinate UE (uu, yaw UE)."""
    rows = []
    for i in range(58):
        x = 1920 + 400 * i
        a = "SM_Banchina_Mod4m_Nicchia" if i in NICCHIA_IDX else "SM_Banchina_Mod4m_v2"
        rows.append((a, f"Mod_{i:02d}", x, line_ue(x), 0.0, YAW_UE))
    for k, x in enumerate((4400, 9200, 14000, 18800)):
        rows.append(("SM_Banchina_Scaletta_v2", f"Scaletta_{k:02d}", x, line_ue(x), 0.0, YAW_UE))
    for k in range(18):
        x = 2600 + 1200 * k
        rows.append(("SM_Banchina_Bitta_v2", f"Bitta_{k:02d}", x, line_ue(x) - 38.0, -1.2, YAW_UE))
    rows.append(("SM_Banchina_Testata", "Testata_Molo", 1920, line_ue(1920), 0.0, YAW_UE))
    rows.append(("SM_Banchina_Testata_Fine", "Testata_Fine", 25120, line_ue(25120), 0.0, YAW_UE))
    rows.append(("SM_Morin_AncoraMonumento", "Ancora_01", ANCORA_XY[0] * 100, -ANCORA_XY[1] * 100, 0.0, 0.0))
    return rows


def write_csv(path="exports/banchina_v2/banchina_posizioni_v2.csv"):
    def f(v, nd=2):
        s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
        return "0.0" if s in ("0", "-0", "") else (s if "." in s else s + ".0")
    os.makedirs(os.path.dirname(f"{PROJ}/{path}"), exist_ok=True)
    lines = ["asset,nome,x,y,z,yaw"] + [f"{a},{n},{f(x)},{f(y)},{f(z)},{f(w, 4)}" for a, n, x, y, z, w in rows_ue()]
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(lines) - 1


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
        for nm in LODDED:
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
