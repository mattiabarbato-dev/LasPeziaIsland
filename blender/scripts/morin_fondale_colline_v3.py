"""morin_fondale_colline_v3.py — SM_Fondale_Colline_NE_v3 (2026-11-20, docs/uefn_arte.md §35.A).

La v2 lasciava sopra o appena sotto la superficie dell'Acqua V2 (Z -1,0 m) dei vertici del DEM sul lato mare:
X 340-380 / 519-580 (fino a +0,2 m sull'acqua) e una fascia di ~2 ha a X 577-971 fra -1 e +0,05 m, visibili come macchie
e velo verdi. v3: la mesh v2 (e i suoi LOD) viene tagliata lungo la linea di costa che delimita i volumi d'acqua, con un
secondo taglio 0,5 m all'interno della terra, e tutti i vertici dal lato mare (piu' quelli sulla linea) vanno a
min(z, -5 m). I vertici a terra non si muovono: il profilo delle colline resta quello della v2.

Costa (coordinate Blender di progetto) = bordo dei volumi Acqua V2 (docs/uefn_arte.md):
  X 250-548,7: ciglio della banchina, Y = 80,3616 - 0,0021664 X        (B1/B2: acqua dal lato Y minore)
  smusso (548,7; 78,3) -> (555,0; 41,9)                                  (mare a ovest)
  X 555-725: Y = 1,3                                                     (Acqua_Golfo_Device_B3)
  X 725-971: Y = -60,1                                                   (Acqua_Golfo_Device_B3_Est)

Esegui in blender/arte_fondale.blend:  import morin_fondale_colline_v3 as cv; cv.build(); cv.verify(); cv.export()
"""
import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SRC = "SM_Fondale_Colline_NE_v2"
DST = "SM_Fondale_Colline_NE_v3"
Z_SEA = -5.0
INLAND = 0.5
EPS = 0.06
MARGIN = 200.0                 # facce candidate al taglio: centro entro 200 m dal segmento (celle dei LOD fino a ~120 m)


def line_y(x):
    return 80.3616 - 0.0021664 * x


# segmenti di costa: (punto A, punto B, direzione "terra" unitaria)
def _segments():
    s = [((250.0, line_y(250.0)), (548.7, line_y(548.7)), (0.0021664, 1.0)),
         ((548.7, 78.3), (555.0, 41.9), None),
         ((555.0, 41.9), (555.0, 1.3), (1.0, 0.0)),
         ((555.0, 1.3), (725.0, 1.3), (0.0, 1.0)),
         ((725.0, 1.3), (725.0, -60.1), (1.0, 0.0)),
         ((725.0, -60.1), (971.0, -60.1), (0.0, 1.0)),
         ((971.0, -60.1), (971.0, -600.0), (1.0, 0.0))]          # bordo est dei volumi d acqua
    out = []
    for a, b, land in s:
        a, b = Vector(a), Vector(b)
        d = (b - a).normalized()
        n = Vector((-d.y, d.x))
        if land is None:
            n = n if n.x > 0 else -n                 # smusso: terra verso +X
        else:
            n = Vector(land).normalized()
        out.append((a, b, n))
    return out


def sea(x, y):
    if x < 250.0 or x > 971.0:
        return False
    if x < 548.7:
        return y < line_y(x) - EPS
    if x < 555.0:
        if y >= 78.3:
            return False
        if y < 41.9:
            return True
        return x < 548.7 + (78.3 - y) / (78.3 - 41.9) * 6.3 - EPS
    if x < 725.0:
        return y < 1.3 - EPS
    return y < -60.1 - EPS


def on_coast(x, y):
    for a, b, n in _segments():
        p = Vector((x, y))
        d = b - a
        t = (p - a).dot(d) / d.length_squared
        if -0.001 <= t <= 1.001 and abs((p - a).dot(n)) < EPS:
            return True
    return False


def _process(src, dst):
    o = bpy.data.objects[src]
    mw = o.matrix_world
    inv = mw.inverted()
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n0 = len(bm.faces)
    for a, b, n in _segments():
        for off in (0.0, INLAND):
            pa = a + n * off
            # solo le facce vicine al segmento (niente tagli infiniti su tutta la collina)
            lo = Vector((min(a.x, b.x) - MARGIN, min(a.y, b.y) - MARGIN))
            hi = Vector((max(a.x, b.x) + MARGIN, max(a.y, b.y) + MARGIN))
            faces = []
            for f in bm.faces:
                c = mw @ f.calc_center_median()
                if lo.x <= c.x <= hi.x and lo.y <= c.y <= hi.y:
                    faces.append(f)
            if not faces:
                continue
            geom = list({e for f in faces for e in f.edges}) + faces + list({v for f in faces for v in f.verts})
            co = inv @ Vector((pa.x, pa.y, 0.0))
            no = (inv.to_3x3() @ Vector((n.x, n.y, 0.0))).normalized()
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-4, plane_co=co, plane_no=no)
    # i tagli fuori dal tratto del segmento non servono ma non fanno danno (restano dentro i 35 m di margine)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    moved = 0
    for v in bm.verts:
        p = mw @ v.co
        if (sea(p.x, p.y) or on_coast(p.x, p.y)) and p.z > Z_SEA:
            q = inv @ Vector((p.x, p.y, Z_SEA))
            v.co.z = q.z
            moved += 1
    me = bpy.data.meshes.get(dst) or bpy.data.meshes.new(dst)
    me.clear_geometry()
    bm.to_mesh(me)
    bm.free()
    for m in o.data.materials:
        me.materials.append(m)
    ob = bpy.data.objects.get(dst)
    if ob is None:
        ob = bpy.data.objects.new(dst, me)
        o.users_collection[0].objects.link(ob)
    ob.data = me
    ob.matrix_world = mw.copy()
    for p in me.polygons:
        p.use_smooth = o.data.polygons[0].use_smooth if len(o.data.polygons) else True
    me.update()
    me.calc_loop_triangles()
    o.data.calc_loop_triangles()
    print(dst, "facce", n0, "->", len(me.polygons), "tri", len(o.data.loop_triangles), "->", len(me.loop_triangles),
          "vertici abbassati", moved)
    return ob


def build():
    out = []
    for sfx in ("", "_LOD1", "_LOD2"):
        out.append(_process(SRC + sfx, DST + sfx))
    return out


def verify(step=2.0):
    """Griglia ogni `step` m sul lato mare X 250-971, Y -600..90: quota della superficie (ray dall'alto) <= Z_SEA."""
    res = {}
    for sfx in ("", "_LOD1", "_LOD2"):
        o = bpy.data.objects[DST + sfx]
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.transform(o.matrix_world)
        bvh = BVHTree.FromBMesh(bm)
        n = hit = 0
        worst = (-1e9, None)
        for x in np.arange(250.0, 971.0 + 1e-6, step):
            for y in np.arange(-600.0, 90.0, step):
                if not sea(x, y):
                    continue
                n += 1
                h = bvh.ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)))
                if h[0] is None:
                    continue
                hit += 1
                if h[0].z > worst[0]:
                    worst = (h[0].z, (round(x, 1), round(y, 1)))
        vmax = max(((v.co.z, (round(v.co.x, 1), round(v.co.y, 1))) for v in bm.verts if sea(v.co.x, v.co.y)),
                   default=(None, None))
        bm.free()
        res[DST + sfx] = dict(punti=n, colpiti=hit, z_max_superficie=round(worst[0], 3), dove=worst[1],
                              z_max_vertici_mare=round(vmax[0], 3) if vmax[0] is not None else None)
        print(DST + sfx, res[DST + sfx])
    return res


def land_unchanged():
    """Confronto v2/v3 sui vertici a terra (lontani piu' di 1 m dalla costa): scarto massimo in Z."""
    for sfx in ("", "_LOD1", "_LOD2"):
        a, b = bpy.data.objects[SRC + sfx], bpy.data.objects[DST + sfx]
        bma = bmesh.new(); bma.from_mesh(a.data); bma.transform(a.matrix_world)
        bmb = bmesh.new(); bmb.from_mesh(b.data); bmb.transform(b.matrix_world)
        bvh = BVHTree.FromBMesh(bmb)
        dz = 0.0
        for v in bma.verts:
            if sea(v.co.x, v.co.y) or any(sea(v.co.x + dx, v.co.y + dy) for dx in (-1.1, 1.1) for dy in (-1.1, 1.1)):
                continue
            h = bvh.ray_cast(Vector((v.co.x, v.co.y, 1000)), Vector((0, 0, -1)))
            if h[0] is not None:
                dz = max(dz, abs(h[0].z - v.co.z))
        bma.free(); bmb.free()
        print(DST + sfx, "scarto max a terra (m)", round(dz, 4))


def export(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    reps = []
    objs = [bpy.data.objects[DST + s] for s in ("", "_LOD1", "_LOD2")]
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in objs}
    for o in objs:
        o.hide_viewport = False
        o.hide_set(False)
    try:
        for lod, o in enumerate(objs):
            loc = o.location.copy()          # come morin_fondale.export: origine in 0 per l'export, attore a (5180; -480)
            o.location = (0.0, 0.0, 0.0)
            bpy.context.view_layer.update()
            try:
                reps.append(morin_export.export_fbx([o], f"//../exports/fondale/{o.name}.fbx", mode="asset",
                                                    overwrite=overwrite, include_ucx=False, bake_rotation=(lod > 0),
                                                    verbose=False))
            finally:
                o.location = loc
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects[n]
            o.hide_viewport = hv
            o.hide_set(hg)
    return reps
