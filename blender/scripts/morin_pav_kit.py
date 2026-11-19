"""morin_pav_kit.py — costruisce il kit di pavimentazione del Blocco 1 (Fase 3).

Esegui dentro blender/arte_pavimentazione.blend:
    exec(open(r".../blender/scripts/morin_pav_kit.py", encoding="utf-8").read()); build_all()

Asset (tutti con origine in (0,0,0), collezione PAV_Kit):
  SM_Pav_Camminamento_4m   lastre lato mare. Origine sul ciglio come SM_Banchina_Mod4m: si posa con le STESSE
                           trasformazioni dei moduli banchina (X 0..4, Y locale 0,54..8,70, Z 0).
  SM_Pav_Cordolo_9m        striscia tattile a righe (Y 88,45-88,85, +0,6/1,4 cm) + cordolo in pietra chiara
                           (Y 88,85-89,15, +3 cm, smussi 1 cm). Coordinate Y di progetto: si posa a (X, 0, 0).
  SM_Pav_FasciaPalme_9m    cubetti + fasce chiare da 0,25 m (longitudinali a Y 92,6 e 99,6, trasversali a X 2,25
                           e 6,75 del modulo = posizione delle palme). Y 89,15..102. Si posa a (X, 0, 0).
  SM_Pav_Aiuola            aiuola quadrata 2,2 m, bordo in pietra chiara 0,25 m a +6 cm, terra a +2,5..4 cm.
                           Origine al centro della palma.
  SM_Morin_Panchina        panchina in pietra a blocchi senza schienale 2,2 x 0,5 x 0,45 m. Origine alla base, al centro.
Ogni asset ha UCX_<nome>_00 (box). LOD1/LOD2 dove la geometria si puo ridurre.
UV in "coordinate mondo" come il master UEFN M_Morin_Master_Pav: orizzontali (X, -Y)/tile, verticali (X-Y, Z)/tile.
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

TILE = {"M_Pav_Lastre": 3.2, "M_Pav_Cubetti": 3.2, "M_Pav_Fascia": 1.0, "M_Pav_Terra": 2.0}
KIT = "PAV_Kit"


def _coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def _replace_obj(name):
    o = bpy.data.objects.get(name)
    if o is not None:
        me = o.data
        bpy.data.objects.remove(o)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)


def _finish(name, bm, mats, coll, uv=True, smooth=False):
    _replace_obj(name)
    me = bpy.data.meshes.new(name)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    if uv:
        layer = bm.loops.layers.uv.verify()
        for f in bm.faces:
            t = TILE.get(mats[f.material_index], 1.0) if mats else 1.0
            n = f.normal
            for lp in f.loops:
                c = lp.vert.co
                if abs(n.z) > 0.7:
                    lp[layer].uv = (c.x / t, -c.y / t)
                else:
                    lp[layer].uv = ((c.x - c.y) / t, c.z / t)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(bpy.data.materials[m] if m else None)
    for p in me.polygons:
        p.use_smooth = smooth
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    return o


def _quad(bm, pts, mi=0):
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    f.material_index = mi
    return f


def _box(bm, x0, x1, y0, y1, z0, z1, mi=0, faces=("top", "bot", "xn", "xp", "yn", "yp")):
    P = {
        "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "bot": [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
        "yn": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        "yp": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        "xn": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        "xp": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
    }
    return [_quad(bm, P[k], mi) for k in faces]


def _ucx(name, boxes, coll):
    """boxes: lista di (x0,x1,y0,y1,z0,z1). Crea UCX_<name>_NN."""
    for i, b in enumerate(boxes):
        n = f"UCX_{name}_{i:02d}"
        bm = bmesh.new()
        _box(bm, *b)
        o = _finish(n, bm, [], coll, uv=False)
        o.display_type = "WIRE"
        o.hide_render = True


# ------------------------------------------------------------------------------------------------
def build_camminamento(coll, name="SM_Pav_Camminamento_4m", y0=0.54, y1=8.70, L=4.0):
    bm = bmesh.new()
    _quad(bm, [(0, y0, 0), (L, y0, 0), (L, y1, 0), (0, y1, 0)], 0)
    o = _finish(name, bm, ["M_Pav_Lastre"], coll)
    _ucx(name, [(0, L, y0, y1, -0.30, 0.0)], coll)
    return o


def build_cordolo(coll, name="SM_Pav_Cordolo_9m", L=9.0, lod=0):
    """lod 0: righe tattili + smussi; 1: striscia piatta + smussi; 2: striscia e cordolo a box."""
    T0, T1, K0, K1 = 88.45, 88.85, 88.85, 89.15
    tz, kz, zb = 0.006, 0.03, -0.15
    bm = bmesh.new()
    if lod == 2:
        tz = 0.010
    # striscia tattile (base)
    _box(bm, 0, L, T0, T1, zb, tz, 0, faces=("top", "yn", "xn", "xp"))
    if lod == 0:
        for i in range(5):
            yc = T0 + 0.04 + i * 0.08
            _box(bm, 0, L, yc - 0.0175, yc + 0.0175, tz, 0.014, 0, faces=("top", "yn", "yp", "xn", "xp"))
    # cordolo
    if lod == 2:
        _box(bm, 0, L, K0, K1, -0.05, kz, 0, faces=("top", "yn", "yp", "xn", "xp"))
    else:
        c = 0.01
        prof = [(K0, -0.05), (K0, kz - c), (K0 + c, kz), (K1 - c, kz), (K1, kz - c), (K1, -0.05)]
        a = [bm.verts.new((0, y, z)) for y, z in prof]
        b = [bm.verts.new((L, y, z)) for y, z in prof]
        for i in range(len(prof) - 1):
            f = bm.faces.new([a[i], b[i], b[i + 1], a[i + 1]])
        f0 = bm.faces.new(list(reversed(a)))
        f1 = bm.faces.new(b)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _finish(name + sfx, bm, ["M_Pav_Fascia"], coll)
    if lod == 0:
        _ucx(name, [(0, L, T0, T1, zb, 0.012), (0, L, K0, K1, zb, kz)], coll)
    return o


def build_fascia(coll, name="SM_Pav_FasciaPalme_9m", L=9.0, w=0.25):
    xs = [0, 2.25 - w / 2, 2.25 + w / 2, 6.75 - w / 2, 6.75 + w / 2, L]
    ys = [89.15, 92.6 - w / 2, 92.6 + w / 2, 99.6 - w / 2, 99.6 + w / 2, 102.0]
    bm = bmesh.new()
    grid = [[bm.verts.new((x, y, 0)) for x in xs] for y in ys]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            f = bm.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
            band = i in (1, 3) or j in (1, 3)
            f.material_index = 1 if band else 0
    o = _finish(name, bm, ["M_Pav_Cubetti", "M_Pav_Fascia"], coll)
    _ucx(name, [(0, L, ys[0], ys[-1], -0.30, 0.0)], coll)
    return o


def build_aiuola(coll, name="SM_Pav_Aiuola", lod=0, seed=7):
    a, b = 1.10, 0.85          # semilato esterno / interno
    zt, zo, ze = 0.06, -0.03, 0.025
    c = 0.01 if lod == 0 else 0.0
    bm = bmesh.new()
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def ring(h, z):
        return [bm.verts.new((sx * h, sy * h, z)) for sx, sy in corners]

    out_lo = ring(a, zo)
    out_hi = ring(a, zt - c)
    if c:
        out_top = ring(a - c, zt)
    else:
        out_top = out_hi
    in_top = ring(b, zt)
    in_lo = ring(b, 0.0) if lod < 2 else None

    def band(r1, r2, mi=0):
        for i in range(4):
            j = (i + 1) % 4
            f = bm.faces.new([r1[i], r1[j], r2[j], r2[i]])
            f.material_index = mi

    band(out_lo, out_hi)
    if c:
        band(out_hi, out_top)
    band(out_top, in_top)
    if lod < 2:
        band(in_top, in_lo)
    # terra
    rnd = random.Random(seed)
    n = 4 if lod == 0 else 1
    pts = []
    for j in range(n + 1):
        row = []
        for i in range(n + 1):
            x = -b + 2 * b * i / n
            y = -b + 2 * b * j / n
            edge = i in (0, n) or j in (0, n)
            if lod == 0 and not edge:
                r = math.hypot(x, y)
                z = ze + 0.012 * max(0.0, 1 - r / b) + rnd.uniform(-0.004, 0.004)
            else:
                z = ze if lod < 2 else zt - 0.02
            row.append(bm.verts.new((x, y, z)))
        pts.append(row)
    for j in range(n):
        for i in range(n):
            f = bm.faces.new([pts[j][i], pts[j][i + 1], pts[j + 1][i + 1], pts[j + 1][i]])
            f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish(name + sfx, bm, ["M_Pav_Fascia", "M_Pav_Terra"], coll)
    if lod == 0:
        _ucx(name, [(-a, a, -a, a, -0.10, 0.045)], coll)
    return o


def build_panchina(coll, name="SM_Morin_Panchina", lod=0):
    L, W, H, T = 2.2, 0.5, 0.45, 0.12
    lx, ly, lc = 0.30, 0.40, 0.70
    bm = bmesh.new()
    _box(bm, -L / 2, L / 2, -W / 2, W / 2, H - T, H)
    for s in (-1, 1):
        _box(bm, s * lc - lx / 2, s * lc + lx / 2, -ly / 2, ly / 2, 0.0, H - T, faces=("top", "xn", "xp", "yn", "yp", "bot"))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    if lod < 2:
        seg = 2 if lod == 0 else 1
        # smusso sugli spigoli di ogni blocco (non sugli appoggi a terra)
        edges = [e for e in bm.edges if not all(abs(v.co.z) < 1e-6 for v in e.verts)]
        bmesh.ops.bevel(bm, geom=edges, offset=0.015, segments=seg, profile=0.5, affect="EDGES",
                        clamp_overlap=True)
    # elimina le facce di appoggio a terra (invisibili)
    bot = [f for f in bm.faces if f.normal.z < -0.9 and all(abs(v.co.z) < 1e-6 for v in f.verts)]
    bmesh.ops.delete(bm, geom=bot, context="FACES")
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish(name + sfx, bm, ["M_Pav_Fascia"], coll, smooth=False)
    if lod == 0:
        _ucx(name, [(-L / 2, L / 2, -W / 2, W / 2, 0.0, H)], coll)
    return o


def build_all():
    coll = _coll(KIT)
    out = [
        build_camminamento(coll),
        build_cordolo(coll), build_cordolo(coll, lod=1), build_cordolo(coll, lod=2),
        build_fascia(coll),
        build_aiuola(coll), build_aiuola(coll, lod=1), build_aiuola(coll, lod=2),
        build_panchina(coll), build_panchina(coll, lod=1), build_panchina(coll, lod=2),
    ]
    dg = bpy.context.evaluated_depsgraph_get()
    for o in out:
        me = o.data
        me.calc_loop_triangles()
        print(f"{o.name:<32} tri {len(me.loop_triangles):>5}  dim {tuple(round(d, 3) for d in o.dimensions)}")
    return out
