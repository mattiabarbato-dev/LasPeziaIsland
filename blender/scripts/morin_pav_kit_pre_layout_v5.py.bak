"""morin_pav_kit.py — kit di pavimentazione e arredi della fascia palme, Blocco 1 (Fase 3). Versione v3 (2026-11-19).

La v1 (commit 105067e) resta in Git e nel file blender/arte_pavimentazione_v1.blend; la v2 in arte_pavimentazione_v2.blend.
v3 [V-utente]: tetto del gazebo a piramide esagonale (falde a ~30 gradi) con lanternino e pinnacolo (h 5,12 m); un solo
gazebo fra la 2a e la 3a palma del filare 1 (X 25,5, Y 93); torna la palma F1_04 (X 39) con la sua aiuola: 54 palme.

Esegui dentro blender/arte_pavimentazione.blend:
    exec(open(r".../blender/scripts/morin_pav_kit.py", encoding="utf-8").read())
    build_all()            # mesh, LOD, UCX, materiali e texture procedurali (riscrive le mesh omonime, non cancella oggetti)
    rows = layout()        # istanze v3 (palme, aiuole, panchine, lampioni, tombini, gazebo) in coordinate Blender
    check_footprints(rows) # controllo impronte in pianta: conflitti fra istanze e uscite dalla fascia (deve dare 0)
    write_csv(rows)        # exports/pavimentazione/pav_posizioni_v3.csv e palme_posizioni_v3.csv
    build_context(rows)    # collezione PAV_Contesto_v3 per i render (oggetti collegati alle mesh del kit)

Dati confermati dall'utente il 2026-11-19 [V-utente]: filari allineati, strisce chiare sul bordo delle aiuole lato
corridoio + striscia trasversale a meta fra due palme, cordolo con gradino vero di 15 cm, panchina in lastra su 3 piedi
una ogni due palme (filare lato mare, spostata verso il mare), lampione in ghisa ogni 4 palme dietro una panchina,
coppie di tombini nel corridoio, un solo gazebo in ghisa dopo le prime due palme dal lato del ponte (X 25,5; OSM X ~40).

Asset (origine in (0,0,0); collezione PAV_Kit):
  SM_Pav_Camminamento_4m  invariato dalla v1 (si posa con le trasformazioni dei moduli banchina, Z 0).
  SM_Pav_Cordolo_9m       striscia tattile (Z 0) + cordolo in pietra chiara Y 88,85-89,15 con gradino di 15 cm
                          (faccia a vista verso le lastre da Z -0,15 a +0,15). Si posa a (X, 0, 0) come la v1.
  SM_Pav_FasciaPalme_9m   cubetti a Z +0,15 (Y 89,15-102) con strisce chiare 0,30 m: longitudinali sul bordo delle
                          aiuole lato corridoio (Y 93,8-94,1 e 98,1-98,4), trasversale a X locale 6,75 (a meta fra due
                          palme) solo nel corridoio. Bordi verticali fino a Z -0,15. Si posa a (X, 0, 0) come la v1.
  SM_Pav_Aiuola           aiuola rettangolare 3,6 x 3,0 m, bordo chiaro 0,30 m a +2 cm, terra a +1/+2 cm.
                          Origine al piede della palma, a quota fascia: si posa a Z +15 uu.
  SM_Morin_Panchina       lastra di pietra 2,8 x 0,5 m, seduta a 0,45 m, 3 piedi. Origine alla base, al centro.
  SM_Morin_Lampione       ghisa grigio-blu scura, 4,8 m, base svasata, fusto, 2 bracci a ricciolo con globi bianchi a
                          quote diverse. Origine alla base. UCX solo base e fusto.
  SM_Morin_Tombino        coppia di chiusini 0,84 x 0,58 m affiancati lungo X, a raso (+4 mm). Origine al centro.
  SM_Morin_Gazebo         pensilina esagonale in ghisa, colonne su raggio 1,6 m (Ø 3,2 m come OSM), tetto a piramide
                          esagonale (falde ~30 gradi) con lanternino a tenda e pinnacolo (h 5,12 m), fregio su texture con alfa, 3 panchine in pietra.
Ogni asset ha UCX_<nome>_NN (box o convessi). LOD1/LOD2 dove la geometria si puo ridurre.
UV: superfici di pavimentazione in "coordinate mondo" come il master UEFN M_Morin_Master_Pav (orizzontali (X,-Y)/tile,
verticali (X-Y, Z)/tile); arredi con proiezione a box (tile 1 m) o UV dedicate (tombino, fregio, globi).
"""
import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

PROJ = r"C:/Users/matti/Documents/LaSpeziaFortnite/LaSpezia-Fortnite"
TEXDIR = PROJ + "/blender/textures"
KIT = "PAV_Kit"

# --- quote e misure di progetto (metri, coordinate Blender) ------------------------------------------------
ZF = 0.15                      # quota della fascia palme: gradino del cordolo [V-utente 15 cm]
ZB = -0.15                     # quota del blockout ribassato sotto la pavimentazione
T0, T1 = 88.45, 88.85          # striscia tattile
K0, K1 = 88.85, 89.15          # cordolo
Y_END = 102.0                  # fine fascia palme (inizio giardini)
Y_F1, Y_F2 = 92.6, 99.6        # filari [V OSM]
AIU_X, AIU_Y, AIU_B = 3.6, 3.0, 0.30   # aiuola [S] dalle foto
STRIP = 0.30                   # larghezza strisce chiare [S]
Y_S1 = (Y_F1 + AIU_Y / 2 - AIU_B, Y_F1 + AIU_Y / 2)   # 93,8-94,1
Y_S2 = (Y_F2 - AIU_Y / 2, Y_F2 - AIU_Y / 2 + AIU_B)   # 98,1-98,4
X_TRASV = 6.75                 # X locale della striscia trasversale nel modulo da 9 m (= meta fra due palme)
X0_MOD, PASSO, N_MOD = 9.75, 9.0, 27
X_PALMA0 = 12.0                # prima palma del filare 1 (fermo dalla v1)
N_PALME = 27
GAZEBO = (25.5, 93.0)          # [V-utente] fra la 2a e la 3a palma del filare 1 (X 21 e 30); OSM way 626400743 dava X ~40
GAZ_R = 1.6                    # raggio delle colonne (Ø 3,2 m, coerente con OSM e con le foto) [S]
GAZ_RE = 2.0                   # raggio di gronda [S]
PANCH_DY = -0.5                # spostamento della panchina verso il mare rispetto al filare [S]
LAMP_DX, LAMP_DY = 0.3, 0.75   # lampione rispetto al centro panchina: verso +X e verso la citta [S]

TILE = {"M_Pav_Lastre": 3.2, "M_Pav_Cubetti": 3.2, "M_Pav_Fascia": 1.0, "M_Pav_Terra": 2.0,
        "M_Morin_Ghisa": 1.0, "M_Morin_Globo": 1.0}


# =============================================================================================================
# utilita
# =============================================================================================================
def _coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def _uv_world(bm, mats):
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


def _uv_box(bm, mats, keep=()):
    """Proiezione a box per gli arredi (asse dominante della normale). Le facce con materiale in keep non si toccano."""
    layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        m = mats[f.material_index] if mats else None
        if m in keep:
            continue
        t = TILE.get(m, 1.0)
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
            lp[layer].uv = (uv[0] / t, uv[1] / t)


def _finish(name, bm, mats, coll, uv="world", smooth_angle=None, keep_uv=()):
    """Scrive bm nella mesh dell'oggetto `name`. Se l'oggetto esiste ne riscrive la geometria (nessun oggetto cancellato)."""
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    if uv == "world":
        _uv_world(bm, mats)
    elif uv == "box":
        _uv_box(bm, mats, keep_uv)
    o = bpy.data.objects.get(name)
    if o is None:
        me = bpy.data.meshes.new(name)
        o = bpy.data.objects.new(name, me)
        coll.objects.link(o)
    me = o.data
    me.materials.clear()          # prima di to_mesh: clear() azzera gli indici materiale dei poligoni
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(bpy.data.materials[m] if m else None)
    for p in me.polygons:
        p.use_smooth = smooth_angle is not None
    if smooth_angle is not None:
        me.set_sharp_from_angle(angle=math.radians(smooth_angle))
    me.update()
    if coll not in o.users_collection:
        coll.objects.link(o)
    o.location = (0, 0, 0)
    o.rotation_euler = (0, 0, 0)
    o.scale = (1, 1, 1)
    return o


def _quad(bm, pts, mi=0):
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    f.material_index = mi
    return f


def _box(bm, x0, x1, y0, y1, z0, z1, mi=0, faces=("top", "bot", "xn", "xp", "yn", "yp"), mat=None):
    P = {
        "top": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "bot": [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
        "yn": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        "yp": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        "xn": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        "xp": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
    }
    out = []
    for k in faces:
        pts = P[k] if mat is None else [tuple(mat @ Vector(p)) for p in P[k]]
        out.append(_quad(bm, pts, mi))
    return out


def _ucx_mesh(name, bm, coll):
    o = _finish(name, bm, [], coll, uv=None)
    o.display_type = "WIRE"
    o.hide_render = True
    return o


def _ucx(name, boxes, coll, start=0):
    """boxes: (x0,x1,y0,y1,z0,z1) oppure (x0,x1,y0,y1,z0,z1, Matrix). Crea UCX_<name>_NN."""
    for i, b in enumerate(boxes):
        bm = bmesh.new()
        if len(b) == 7:
            _box(bm, *b[:6], mat=b[6])
        else:
            _box(bm, *b)
        _ucx_mesh(f"UCX_{name}_{start + i:02d}", bm, coll)


def _ucx_hull(name, idx, pts, coll):
    bm = bmesh.new()
    for p in pts:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    _ucx_mesh(f"UCX_{name}_{idx:02d}", bm, coll)


def _lathe(bm, prof, n, mat=Matrix(), mi=0, cap_top=True, phase=0.0):
    """Superficie di rivoluzione attorno a Z. prof: [(r, z), ...] dal basso. r=0 chiude a punta."""
    rings = []
    for r, z in prof:
        if r < 1e-6:
            rings.append([bm.verts.new(mat @ Vector((0, 0, z)))])
        else:
            rings.append([bm.verts.new(mat @ Vector((r * math.cos(phase + 2 * math.pi * k / n),
                                                     r * math.sin(phase + 2 * math.pi * k / n), z)))
                          for k in range(n)])
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        for k in range(n):
            k1 = (k + 1) % n
            if len(b) == 1:
                vs = [a[k], a[k1], b[0]]
            elif len(a) == 1:
                vs = [a[0], b[k1], b[k]]
            else:
                vs = [a[k], a[k1], b[k1], b[k]]
            f = bm.faces.new(vs)
            f.material_index = mi
    if cap_top and len(rings[-1]) > 2:
        f = bm.faces.new(rings[-1])
        f.material_index = mi
    return rings


def _tube(bm, pts, radius, sides, mi=0, cap=True):
    """Tubo lungo una polilinea 3D (trasporto parallelo del riferimento)."""
    pts = [Vector(p) for p in pts]
    tang = []
    for i in range(len(pts)):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        tang.append((b - a).normalized())
    up = Vector((0, 1, 0)) if abs(tang[0].y) < 0.9 else Vector((1, 0, 0))
    nrm = tang[0].cross(up).normalized()
    rings = []
    for i, p in enumerate(pts):
        if i > 0:
            nrm = (nrm - tang[i] * nrm.dot(tang[i])).normalized()
        bin_ = tang[i].cross(nrm)
        rings.append([bm.verts.new(p + radius * (math.cos(2 * math.pi * k / sides) * nrm +
                                                 math.sin(2 * math.pi * k / sides) * bin_))
                      for k in range(sides)])
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(sides):
            k1 = (k + 1) % sides
            f = bm.faces.new([a[k], a[k1], b[k1], b[k]])
            f.material_index = mi
    if cap:
        for r, rev in ((rings[0], True), (rings[-1], False)):
            f = bm.faces.new(list(reversed(r)) if rev else r)
            f.material_index = mi
    vs = {v for r in rings for v in r}
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if all(v in vs for v in f.verts)])


def _sphere(bm, c, r, seg, rings_, mi=0):
    prof = [(r * math.sin(math.pi * j / rings_), c[2] - r * math.cos(math.pi * j / rings_)) for j in range(rings_ + 1)]
    prof[0] = (0.0, prof[0][1])
    prof[-1] = (0.0, prof[-1][1])
    _lathe(bm, prof, seg, Matrix.Translation((c[0], c[1], 0)), mi, cap_top=False)


def _recalc(bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def tri_count(o):
    me = o.data
    me.calc_loop_triangles()
    return len(me.loop_triangles)


# =============================================================================================================
# materiali e texture procedurali
# =============================================================================================================
def _principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def _img(name, path, noncolor):
    im = bpy.data.images.get(name)
    if im is None:
        im = bpy.data.images.load(path, check_existing=True)
        im.name = name
    else:
        im.reload()
    if noncolor:
        im.colorspace_settings.name = "Non-Color"
    return im


def _pbr_material(name, d, n, orm, tint=None, alpha=False):
    """Materiale PBR come gli altri M_* del progetto: D (sRGB), N (DirectX, G invertito), ORM (R=AO, G=Rough, B=Metal)."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for nd in list(nt.nodes):
        if nd.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(nd)  # nodi del materiale ricostruiti (nessun dato utente: materiale generato da script)
    out = next(nd for nd in nt.nodes if nd.type == "OUTPUT_MATERIAL")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    td = nt.nodes.new("ShaderNodeTexImage"); td.image = _img(os.path.basename(d), d, False)
    col = td.outputs["Color"]
    if tint is not None:
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.inputs[7].default_value = (*tint, 1.0)
        nt.links.new(col, mix.inputs[6])
        col = mix.outputs[2]
    nt.links.new(col, bsdf.inputs["Base Color"])
    if alpha:
        nt.links.new(td.outputs["Alpha"], bsdf.inputs["Alpha"])
        for attr, val in (("surface_render_method", "DITHERED"), ("blend_method", "CLIP")):
            try:
                setattr(mat, attr, val)
            except (AttributeError, TypeError):
                pass
        mat.use_backface_culling = False
    to = nt.nodes.new("ShaderNodeTexImage"); to.image = _img(os.path.basename(orm), orm, True)
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(to.outputs["Color"], sep.inputs[0])
    nt.links.new(sep.outputs[1], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs[2], bsdf.inputs["Metallic"])
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = _img(os.path.basename(n), n, True)
    sepn = nt.nodes.new("ShaderNodeSeparateColor")
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    comb = nt.nodes.new("ShaderNodeCombineColor")
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tn.outputs["Color"], sepn.inputs[0])
    nt.links.new(sepn.outputs[0], comb.inputs[0])
    nt.links.new(sepn.outputs[1], inv.inputs[1])
    nt.links.new(inv.outputs[0], comb.inputs[1])
    nt.links.new(sepn.outputs[2], comb.inputs[2])
    nt.links.new(comb.outputs[0], nm.inputs["Color"])
    nt.links.new(nm.outputs[0], bsdf.inputs["Normal"])
    return mat


def _save_png(name, arr, alpha=False):
    """arr: float32 HxWx(3|4) in [0,1], riga 0 = basso dell'immagine (convenzione Blender)."""
    import numpy as np
    h, w = arr.shape[:2]
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.ones((h, w, 1), np.float32)], axis=2)
    im = bpy.data.images.get(name + "_gen")
    if im is None:
        im = bpy.data.images.new(name + "_gen", w, h, alpha=True, float_buffer=False)
    im.scale(w, h)
    im.pixels.foreach_set(np.clip(arr, 0, 1).astype(np.float32).ravel())
    path = f"{TEXDIR}/{name}.png"
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    return path


def _normal_from_height(h, strength):
    import numpy as np
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx * strength, -gy * strength, np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    # DirectX (G = -Y) come le altre texture del progetto
    return np.stack([nx / l * 0.5 + 0.5, -ny / l * 0.5 + 0.5, nz / l * 0.5 + 0.5], axis=2).astype(np.float32)


def _blur(a, k):
    import numpy as np
    for ax in (0, 1):
        c = np.cumsum(np.pad(a, [(k, k) if i == ax else (0, 0) for i in range(a.ndim)], mode="edge"), axis=ax)
        a = (np.take(c, range(2 * k, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * k), axis=ax)) / (2 * k)
    return a


def make_tex_tombino(size=1024, seed=11):
    """Chiusino in ghisa: telaio + piastra con bugne rettangolari (disegno comune nei chiusini italiani). Procedurale."""
    import numpy as np
    rng = np.random.default_rng(seed)
    v, u = np.mgrid[0:size, 0:size].astype(np.float32) / size
    h = np.zeros((size, size), np.float32)
    fr = 0.05
    frame = (u < fr) | (u > 1 - fr) | (v < fr) | (v > 1 - fr)
    groove = ((u > fr) & (u < fr + 0.012)) | ((u < 1 - fr) & (u > 1 - fr - 0.012)) | \
             ((v > fr) & (v < fr + 0.012)) | ((v < 1 - fr) & (v > 1 - fr - 0.012))
    h[frame] = 0.8
    # bugne: griglia di rettangoli 14 x 10, ruotati a righe alterne
    nu, nv = 14, 10
    iu = (u - fr - 0.02) / (1 - 2 * fr - 0.04) * nu
    iv = (v - fr - 0.02) / (1 - 2 * fr - 0.04) * nv
    inside = (iu > 0) & (iu < nu) & (iv > 0) & (iv < nv)
    fu, fv = iu % 1.0, iv % 1.0
    alt = (np.floor(iu) + np.floor(iv)) % 2 == 0
    lug = np.where(alt, (np.abs(fu - 0.5) < 0.36) & (np.abs(fv - 0.5) < 0.14),
                   (np.abs(fu - 0.5) < 0.14) & (np.abs(fv - 0.5) < 0.36))
    h[inside & lug] = 1.0
    h[groove] = 0.0
    h = _blur(h, 2)
    noise = _blur(rng.random((size, size)).astype(np.float32), 6)
    noise = (noise - noise.mean()) / (noise.std() + 1e-6)
    fine = rng.random((size, size)).astype(np.float32)
    base = np.array([0.105, 0.100, 0.095], np.float32)
    worn = np.array([0.30, 0.285, 0.26], np.float32)
    rust = np.array([0.20, 0.12, 0.07], np.float32)
    t = np.clip(h * 0.9 + noise[..., None][..., 0] * 0.08, 0, 1)
    col = base[None, None] * (1 - t[..., None]) + worn[None, None] * t[..., None]
    rmask = np.clip((noise - 1.0) * 0.6, 0, 0.5) * (1 - h)
    col = col * (1 - rmask[..., None]) + rust[None, None] * rmask[..., None]
    col *= (0.92 + 0.08 * fine)[..., None]
    nrm = _normal_from_height(h * 0.004 * size, 1.0)
    ao = np.clip(0.55 + 0.45 * _blur(h, 6) + 0.2 * h, 0, 1)
    rough = np.clip(0.82 - 0.35 * h + 0.05 * noise, 0.3, 1)
    metal = np.clip(0.15 + 0.35 * h, 0, 1)
    orm = np.stack([ao, rough, metal], axis=2)
    return [_save_png("T_Morin_Tombino_D", col), _save_png("T_Morin_Tombino_N", nrm), _save_png("T_Morin_Tombino_ORM", orm)]


def make_tex_fregio(w=2048, hgt=512):
    """Fregio della pensilina: traverso alto, tre anelli con riccioli, gocce pendenti. Alfa = forma (materiale masked)."""
    import numpy as np
    y, x = np.mgrid[0:hgt, 0:w].astype(np.float32)
    yy = hgt - 1 - y                      # 0 = alto dell'immagine
    m = np.zeros((hgt, w), np.float32)
    m[(yy < 46)] = 1.0                    # traverso superiore (sotto l'architrave)
    m[(yy > 300) & (yy < 322)] = 1.0      # traverso inferiore
    cols = 3
    for i in range(cols):
        cx = (i + 0.5) * w / cols
        cy = 175.0
        d = np.hypot(x - cx, yy - cy)
        m[(d > 108) & (d < 128)] = 1.0    # anello
        m[(d > 48) & (d < 60)] = 1.0      # anello interno
        a = np.arctan2(yy - cy, x - cx)
        for k in range(8):                # raggi
            ang = k * math.pi / 4
            dd = np.abs(np.sin(a - ang)) * d
            m[(dd < 7) & (d > 60) & (d < 108) & (np.cos(a - ang) > 0)] = 1.0
        # gocce pendenti sotto il traverso inferiore
        for dx in (-140, 0, 140):
            px, py = cx + dx, 322.0
            m[(np.abs(x - px) < 6) & (yy > py) & (yy < py + 70)] = 1.0
            m[np.hypot(x - px, yy - (py + 92)) < 24] = 1.0
    # riccioli a S tra gli anelli
    for i in range(cols + 1):
        cx = i * w / cols
        for sy, sgn in ((110.0, 1), (240.0, -1)):
            d = np.hypot(x - cx - sgn * 34, yy - sy)
            m[(d > 34) & (d < 46) & ((x - cx) * sgn < 30)] = 1.0
    m[:, :18] = 1.0
    m[:, -18:] = 1.0                      # montanti laterali (vicino alle colonne)
    soft = _blur(m, 5)
    h = soft * m
    col = np.zeros((hgt, w, 4), np.float32)
    base = np.array([0.075, 0.085, 0.095], np.float32)
    col[..., :3] = base[None, None] * (0.75 + 0.5 * h[..., None])
    col[..., 3] = m
    col = col[::-1]                       # Blender: riga 0 in basso
    nrm = _normal_from_height((h * 6.0)[::-1], 1.0)
    orm = np.stack([0.6 + 0.4 * h[::-1], np.full_like(h, 0.6), np.full_like(h, 0.6)], axis=2)
    return [_save_png("T_Morin_Gazebo_Fregio_D", col, alpha=True), _save_png("T_Morin_Gazebo_Fregio_N", nrm),
            _save_png("T_Morin_Gazebo_Fregio_ORM", orm)]


def build_materials(make_textures=True):
    if make_textures:
        make_tex_tombino()
        make_tex_fregio()
    g = TEXDIR + "/T_Banchina_Ghisa_"
    # ghisa grigio-blu scura (lampioni, gazebo): stesse texture CC0 della bitta, con tinta
    _pbr_material("M_Morin_Ghisa", g + "D.png", g + "N.png", g + "ORM.png", tint=(0.42, 0.50, 0.60))
    t = TEXDIR + "/T_Morin_Tombino_"
    _pbr_material("M_Morin_Tombino", t + "D.png", t + "N.png", t + "ORM.png")
    f = TEXDIR + "/T_Morin_Gazebo_Fregio_"
    _pbr_material("M_Morin_Gazebo_Fregio", f + "D.png", f + "N.png", f + "ORM.png", tint=(0.42, 0.50, 0.60), alpha=True)
    # globo: bianco opalino con emissione debole (in UEFN: MI bianca, emissivo opzionale ~0,5)
    mat = bpy.data.materials.get("M_Morin_Globo") or bpy.data.materials.new("M_Morin_Globo")
    mat.use_nodes = True
    b = _principled(mat)
    b.inputs["Base Color"].default_value = (0.92, 0.92, 0.90, 1)
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Emission Color"].default_value = (1.0, 0.95, 0.85, 1)
    b.inputs["Emission Strength"].default_value = 0.5
    b.inputs["Transmission Weight"].default_value = 0.0


# =============================================================================================================
# mesh del kit
# =============================================================================================================
def build_camminamento(coll, name="SM_Pav_Camminamento_4m", y0=0.54, y1=8.70, L=4.0):
    bm = bmesh.new()
    _quad(bm, [(0, y0, 0), (L, y0, 0), (L, y1, 0), (0, y1, 0)], 0)
    o = _finish(name, bm, ["M_Pav_Lastre"], coll)
    _ucx(name, [(0, L, y0, y1, -0.30, 0.0)], coll)
    return o


def build_cordolo(coll, name="SM_Pav_Cordolo_9m", L=9.0, lod=0):
    """Striscia tattile a Z 0 + cordolo con gradino di 15 cm (faccia a vista verso le lastre, smusso 1,5 cm)."""
    tz = 0.006 if lod < 2 else 0.010
    bm = bmesh.new()
    _box(bm, 0, L, T0, T1, ZB, tz, 0, faces=("top", "yn", "xn", "xp"))
    if lod == 0:
        for i in range(5):
            yc = T0 + 0.04 + i * 0.08
            _box(bm, 0, L, yc - 0.0175, yc + 0.0175, tz, 0.014, 0, faces=("top", "yn", "yp", "xn", "xp"))
    c = 0.015 if lod < 2 else 0.0
    prof = [(K0, ZB), (K0, ZF - c), (K0 + c, ZF), (K1, ZF)] if c else [(K0, ZB), (K0, ZF), (K1, ZF)]
    prof = prof + [(K1, ZB)]          # profilo chiuso: solido manifold, normali affidabili
    a = [bm.verts.new((0, y, z)) for y, z in prof]
    b = [bm.verts.new((L, y, z)) for y, z in prof]
    for i in range(len(prof)):
        j = (i + 1) % len(prof)
        bm.faces.new([a[i], b[i], b[j], a[j]])
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    _recalc(bm)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish(name + sfx, bm, ["M_Pav_Fascia"], coll)
    if lod == 0:
        _ucx(name, [(0, L, T0, T1, ZB, 0.012), (0, L, K0, K1, ZB, ZF)], coll)
    return o


def build_fascia(coll, name="SM_Pav_FasciaPalme_9m", L=9.0):
    xs = [0, X_TRASV - STRIP / 2, X_TRASV + STRIP / 2, L]
    ys = [K1, Y_S1[0], Y_S1[1], Y_S2[0], Y_S2[1], Y_END]
    bm = bmesh.new()
    grid = [[bm.verts.new((x, y, ZF)) for x in xs] for y in ys]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            f = bm.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
            band = j in (1, 3) or (j == 2 and i == 1)
            f.material_index = 1 if band else 0
    # bordi verticali (testate del modulo e lato giardini) fino alla quota del blockout ribassato
    _box(bm, 0, L, K1, Y_END, ZB, ZF, 0, faces=("xn", "xp", "yp"))
    o = _finish(name, bm, ["M_Pav_Cubetti", "M_Pav_Fascia"], coll)
    _ucx(name, [(0, L, K1, Y_END, ZB, ZF)], coll)
    return o


def build_aiuola(coll, name="SM_Pav_Aiuola", lod=0, seed=7):
    ax, ay = AIU_X / 2, AIU_Y / 2
    bx, by = ax - AIU_B, ay - AIU_B
    zt, zo, ze = 0.02, -0.03, 0.008
    c = 0.008 if lod == 0 else 0.0
    bm = bmesh.new()
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def ring(hx, hy, z):
        return [bm.verts.new((sx * hx, sy * hy, z)) for sx, sy in corners]

    out_lo = ring(ax, ay, zo)
    out_hi = ring(ax, ay, zt - c)
    out_top = ring(ax - c, ay - c, zt) if c else out_hi
    in_top = ring(bx, by, zt)
    in_lo = ring(bx, by, ze) if lod < 2 else None

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
    rnd = random.Random(seed)
    n = 4 if lod == 0 else 1
    pts = []
    for j in range(n + 1):
        row = []
        for i in range(n + 1):
            x = -bx + 2 * bx * i / n
            y = -by + 2 * by * j / n
            edge = i in (0, n) or j in (0, n)
            if lod == 0 and not edge:
                r = math.hypot(x / bx, y / by)
                z = ze + 0.008 * max(0.0, 1 - r) + rnd.uniform(-0.002, 0.002)
            else:
                z = ze if lod < 2 else zt - 0.008
            row.append(bm.verts.new((x, y, z)))
        pts.append(row)
    for j in range(n):
        for i in range(n):
            f = bm.faces.new([pts[j][i], pts[j][i + 1], pts[j + 1][i + 1], pts[j + 1][i]])
            f.material_index = 1
    _recalc(bm)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish(name + sfx, bm, ["M_Pav_Fascia", "M_Pav_Terra"], coll)
    if lod == 0:
        _ucx(name, [(-ax, ax, -ay, ay, -0.10, zt)], coll)
    return o


def _panchina_bm(bm, L, W, H, T, legs, lx, ly, lod, mat=Matrix(), mi=0):
    """Lastra di seduta + piedi (lastre verticali), aggiunti a bm e trasformati con mat. Smusso sugli spigoli alti."""
    before = set(bm.verts)
    _box(bm, -L / 2, L / 2, -W / 2, W / 2, H - T, H, mi)
    for x in legs:
        _box(bm, x - lx / 2, x + lx / 2, -ly / 2, ly / 2, 0.0, H - T, mi, faces=("xn", "xp", "yn", "yp", "bot", "top"))
    bmesh.ops.remove_doubles(bm, verts=[v for v in bm.verts if v not in before], dist=1e-6)
    nv = {v for v in bm.verts if v not in before}
    if lod < 2:
        edges = [e for e in bm.edges if e.verts[0] in nv and e.verts[1] in nv
                 and not all(abs(v.co.z) < 1e-6 for v in e.verts)]
        bmesh.ops.bevel(bm, geom=edges, offset=0.012, segments=2 if lod == 0 else 1, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    nv = {v for v in bm.verts if v not in before}
    bm.normal_update()
    bot = [f for f in bm.faces if all(v in nv for v in f.verts) and f.normal.z < -0.9
           and all(abs(v.co.z) < 1e-6 for v in f.verts)]
    bmesh.ops.delete(bm, geom=bot, context="FACES")
    bmesh.ops.transform(bm, matrix=mat, verts=[v for v in bm.verts if v not in before])


PANCH = dict(L=2.8, W=0.5, H=0.45, T=0.10, legs=(-1.15, 0.0, 1.15), lx=0.14, ly=0.42)


def build_panchina(coll, name="SM_Morin_Panchina", lod=0):
    bm = bmesh.new()
    _panchina_bm(bm, lod=lod, **PANCH)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish(name + sfx, bm, ["M_Pav_Fascia"], coll, uv="box")
    if lod == 0:
        L, W, H = PANCH["L"], PANCH["W"], PANCH["H"]
        _ucx(name, [(-L / 2, L / 2, -W / 2, W / 2, 0.0, H)], coll)
    return o


# --- lampione -----------------------------------------------------------------------------------------------
LAMP_PROF = [(0.17, 0.0), (0.17, 0.06), (0.15, 0.08), (0.15, 0.14), (0.13, 0.20), (0.10, 0.40), (0.085, 0.65),
             (0.10, 0.70), (0.10, 0.76), (0.075, 0.80), (0.065, 1.20), (0.06, 2.40), (0.07, 2.45), (0.07, 2.52),
             (0.055, 2.56), (0.05, 4.40), (0.06, 4.45), (0.06, 4.52), (0.045, 4.55), (0.045, 4.62), (0.05, 4.64),
             (0.06, 4.68), (0.05, 4.73), (0.02, 4.76), (0.0, 4.82)]
LAMP_ARMS = ((+1, 4.30), (-1, 3.90))   # (lato X, quota d'attacco): globi a quote diverse come nelle foto [V foto]


def _arm_paths(side, z0, npts):
    ox = 0.045
    arch = []
    for k in range(npts + 1):          # arco a pastorale: centro (0,30; z0), r 0,25, da 180° a 0°
        a = math.pi - math.pi * k / npts
        arch.append((side * (0.30 + 0.25 * math.cos(a)), 0.0, z0 + 0.25 * math.sin(a)))
    arch[0] = (side * ox, 0.0, z0)
    arch.append((side * 0.55, 0.0, z0 - 0.10))
    spiral = []
    ns = int(npts * 1.5)
    for k in range(ns + 1):            # ricciolo sotto l'arco: 1,25 giri, r 0,13 -> 0,03
        t = k / ns
        a = math.pi + t * 2.5 * math.pi * -1
        r = 0.13 - 0.10 * t
        spiral.append((side * (0.20 + r * math.cos(a)), 0.0, z0 - 0.10 + r * math.sin(a)))
    spiral[0] = (side * ox, 0.0, spiral[0][2])
    return arch, spiral


def build_lampione(coll, name="SM_Morin_Lampione", lod=0):
    sides = (16, 10, 6)[lod]
    asides = (6, 4, 3)[lod]
    npts = (16, 8, 5)[lod]
    sseg, sring = ((16, 10), (10, 6), (6, 4))[lod]
    bm = bmesh.new()
    prof = LAMP_PROF if lod < 2 else [(0.17, 0.0), (0.15, 0.10), (0.085, 0.65), (0.10, 0.73), (0.065, 0.80),
                                      (0.055, 2.5), (0.05, 4.5), (0.06, 4.6), (0.0, 4.82)]
    _lathe(bm, prof, sides, mi=0, cap_top=False)
    for side, z0 in LAMP_ARMS:
        arch, spiral = _arm_paths(side, z0, npts)
        _tube(bm, arch, 0.018, asides, 0)
        if lod < 2:
            _tube(bm, spiral, 0.012, asides, 0)
        # portalampada + globo Ø 0,38 m
        _lathe(bm, [(0.05, z0 - 0.19), (0.05, z0 - 0.12), (0.02, z0 - 0.10)], max(asides, 6),
               Matrix.Translation((side * 0.55, 0, 0)), 0)
        _sphere(bm, (side * 0.55, 0.0, z0 - 0.19 - 0.185), 0.19, sseg, sring, 1)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish(name + sfx, bm, ["M_Morin_Ghisa", "M_Morin_Globo"], coll, uv="box", smooth_angle=50)
    if lod == 0:
        _ucx(name, [(-0.17, 0.17, -0.17, 0.17, 0.0, 0.80), (-0.07, 0.07, -0.07, 0.07, 0.80, 4.60)], coll)
    return o


# --- tombino ------------------------------------------------------------------------------------------------
TOMB = dict(w=0.84, d=0.58, gap=0.06, z=0.004, c=0.012)


def build_tombino(coll, name="SM_Morin_Tombino", lod=0):
    w, d, gap, z, c = TOMB["w"], TOMB["d"], TOMB["gap"], TOMB["z"], TOMB["c"]
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.verify()
    for s in (-1, 1):
        cx = s * (w + gap) / 2
        top = [(cx - w / 2, -d / 2, z), (cx + w / 2, -d / 2, z), (cx + w / 2, d / 2, z), (cx - w / 2, d / 2, z)]
        f = _quad(bm, top)
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)] if s < 0 else [(1, 1), (0, 1), (0, 0), (1, 0)]
        for lp, uv in zip(f.loops, uvs):
            lp[uvl].uv = uv
        if lod == 0:   # smusso perimetrale fino a -1 cm (raccordo con i cubetti)
            lo = [(cx - w / 2 - c, -d / 2 - c, -0.01), (cx + w / 2 + c, -d / 2 - c, -0.01),
                  (cx + w / 2 + c, d / 2 + c, -0.01), (cx - w / 2 - c, d / 2 + c, -0.01)]
            for i in range(4):
                j = (i + 1) % 4
                g = _quad(bm, [lo[i], lo[j], top[j], top[i]])
                for lp in g.loops:
                    lp[uvl].uv = (0.02, 0.5)
    o = _finish(name + ("" if lod == 0 else f"_LOD{lod}"), bm, ["M_Morin_Tombino"], coll, uv=None)
    if lod == 0:
        W = w + gap / 2 + c
        _ucx(name, [(-W, W, -d / 2 - c, d / 2 + c, -0.05, 0.0)], coll)
    return o


# --- gazebo -------------------------------------------------------------------------------------------------
GAZ_COL = [(0.16, 0.45), (0.16, 0.52), (0.13, 0.58), (0.10, 0.75), (0.085, 0.95), (0.10, 1.0), (0.10, 1.05),
           (0.075, 1.10), (0.065, 2.55), (0.08, 2.60), (0.08, 2.66), (0.11, 2.76), (0.13, 2.84), (0.13, 2.90)]
# v3: gronda 8 cm, falde dritte da r 2,0 (Z 3,12) a r 0,52 (Z 3,96) = 29,6 gradi [S dalle foto; V-utente "ben inclinate"],
# collarino, lanternino esagonale (base Ø ~0,9 m) a tenda concava con cappello, pinnacolo con sfera.
GAZ_ROOF = [(GAZ_RE, 3.04), (GAZ_RE, 3.12), (0.52, 3.96), (0.52, 4.00), (0.45, 4.02), (0.45, 4.12),
            (0.30, 4.24), (0.18, 4.40), (0.11, 4.56), (0.08, 4.66), (0.10, 4.68), (0.10, 4.72), (0.04, 4.75)]
GAZ_CEIL = [(0.0, 3.88), (0.48, 3.88), (GAZ_RE, 3.04)]
GAZ_FIN = [(0.04, 4.75), (0.03, 4.77), (0.055, 4.81), (0.065, 4.85), (0.055, 4.89), (0.025, 4.92), (0.018, 5.04),
           (0.0, 5.12)]
GAZ_ROOF_L2 = [(GAZ_RE, 3.04), (GAZ_RE, 3.12), (0.52, 3.96), (0.45, 4.12), (0.11, 4.56), (0.04, 4.75), (0.0, 5.12)]


def _hex(i, r=GAZ_R):
    a = math.radians(60 * i)
    return Vector((r * math.cos(a), r * math.sin(a), 0))


def build_gazebo(coll, name="SM_Morin_Gazebo", lod=0):
    csides = (12, 6, 4)[lod]
    bm = bmesh.new()
    # plinti in pietra 0,40 x 0,40 x 0,45 e colonne in ghisa
    for i in range(6):
        p = _hex(i)
        rot = Matrix.Translation(p) @ Matrix.Rotation(math.radians(60 * i), 4, "Z")
        _box(bm, -0.20, 0.20, -0.20, 0.20, 0.0, 0.45, 2, faces=("top", "xn", "xp", "yn", "yp"), mat=rot)
        if lod < 2:
            _lathe(bm, GAZ_COL, csides, Matrix.Translation(p), 0, cap_top=False)
        else:
            _lathe(bm, [(0.13, 0.45), (0.08, 1.0), (0.07, 2.6), (0.13, 2.90)], csides,
                   Matrix.Translation(p), 0, cap_top=False)
    # architrave esagonale 0,14 x 0,16 (Z 2,88-3,04)
    for i in range(6):
        a, b = _hex(i), _hex(i + 1)
        mid = (a + b) / 2
        L = (b - a).length + 0.10
        ang = math.atan2((b - a).y, (b - a).x)
        m = Matrix.Translation(mid) @ Matrix.Rotation(ang, 4, "Z")
        _box(bm, -L / 2, L / 2, -0.07, 0.07, 2.88, 3.04, 0, faces=("top", "bot", "yn", "yp"), mat=m)
    # fregio (piano con alfa) tra le colonne, Z 2,43-2,88, sul filo esterno delle colonne
    uvl = bm.loops.layers.uv.verify()
    for i in range(6):
        a, b = _hex(i), _hex(i + 1)
        d = (b - a).normalized()
        a2, b2 = a + d * 0.07, b - d * 0.07
        f = _quad(bm, [(a2.x, a2.y, 2.43), (b2.x, b2.y, 2.43), (b2.x, b2.y, 2.88), (a2.x, a2.y, 2.88)], 1)
        for lp, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            lp[uvl].uv = uv
    # tetto: falde a piramide + lanternino (esagonali), soffitto sotto, pinnacolo; LOD2 con profilo ridotto e punta
    if lod < 2:
        _lathe(bm, GAZ_ROOF, 6, mi=0, cap_top=False)
        _lathe(bm, GAZ_CEIL, 6, mi=0, cap_top=False)   # dal centro verso la gronda: normali verso il basso
        _lathe(bm, GAZ_FIN, (8, 6)[lod], mi=0, cap_top=False)
    else:
        _lathe(bm, GAZ_ROOF_L2, 6, mi=0, cap_top=False)
        _lathe(bm, [(0.0, 3.88), (GAZ_RE, 3.04)], 6, mi=0, cap_top=False)
    # tre panchine in pietra sui lati 0, 2, 4, verso l'interno
    ap = GAZ_R * math.cos(math.radians(30))
    for i in (0, 2, 4):
        ang = math.radians(60 * i + 30)
        c = Vector((math.cos(ang), math.sin(ang), 0)) * (ap - 0.28)
        m = Matrix.Translation(c) @ Matrix.Rotation(ang + math.pi / 2, 4, "Z")
        _panchina_bm(bm, L=1.20, W=0.38, H=0.45, T=0.09, legs=(-0.45, 0.45), lx=0.12, ly=0.32, lod=lod + 1, mat=m, mi=2)
    sfx = "" if lod == 0 else f"_LOD{lod}"
    o = _finish(name + sfx, bm, ["M_Morin_Ghisa", "M_Morin_Gazebo_Fregio", "M_Pav_Fascia"], coll, uv="box",
                smooth_angle=50, keep_uv=("M_Morin_Gazebo_Fregio",))
    if lod == 0:
        boxes = []
        for i in range(6):
            p = _hex(i)
            rot = Matrix.Translation(p) @ Matrix.Rotation(math.radians(60 * i), 4, "Z")
            boxes.append((-0.20, 0.20, -0.20, 0.20, 0.0, 0.45, rot))
            boxes.append((-0.13, 0.13, -0.13, 0.13, 0.45, 2.90, rot))
        for i in (0, 2, 4):
            ang = math.radians(60 * i + 30)
            c = Vector((math.cos(ang), math.sin(ang), 0)) * (ap - 0.28)
            m = Matrix.Translation(c) @ Matrix.Rotation(ang + math.pi / 2, 4, "Z")
            boxes.append((-0.60, 0.60, -0.19, 0.19, 0.0, 0.45, m))
        _ucx(name, boxes, coll)
        # tetto: un solo convesso (piramide dall'architrave al lanternino), nessun incavo dove incastrarsi
        roof = ([_hex(i, GAZ_RE) + Vector((0, 0, z)) for i in range(6) for z in (2.88, 3.12)] +
                [_hex(i, 0.52) + Vector((0, 0, 4.00)) for i in range(6)] + [Vector((0, 0, 4.72))])
        _ucx_hull(name, len(boxes), roof, coll)
    return o


# =============================================================================================================
def build_all(make_textures=True):
    coll = _coll(KIT)
    build_materials(make_textures)
    out = [build_camminamento(coll)]
    out += [build_cordolo(coll, lod=l) for l in range(3)]
    out += [build_fascia(coll)]
    out += [build_aiuola(coll, lod=l) for l in range(3)]
    out += [build_panchina(coll, lod=l) for l in range(3)]
    out += [build_lampione(coll, lod=l) for l in range(3)]
    out += [build_tombino(coll, lod=l) for l in range(3)]
    out += [build_gazebo(coll, lod=l) for l in range(3)]
    for o in out:
        print(f"{o.name:<28} tri {tri_count(o):>5}  dim {tuple(round(d, 3) for d in o.dimensions)}")
    return out


# =============================================================================================================
# disposizione (coordinate Blender, metri). Regola UE: (X*100, -Y*100, Z*100), yaw UE = -rotZ Blender.
# =============================================================================================================
def _gazebo_hit(x, y, margin):
    gx, gy = GAZEBO
    return abs(x - gx) < GAZ_RE + margin and abs(y - gy) < GAZ_RE + margin


def layout(seed_tombini=20261119):
    rows = []   # (asset, nome, x, y, z, yaw_blender_deg)
    # palme: filare 1 fermo (X 12 + 9k), filare 2 allineato; via le palme che cadono sotto la pensilina
    palme = []
    for fil, y in ((1, Y_F1), (2, Y_F2)):
        for k in range(N_PALME):
            x = X_PALMA0 + PASSO * k
            if _gazebo_hit(x, y, AIU_X / 2 - 0.2):
                continue
            palme.append((f"Palma_F{fil}_{k + 1:02d}", x, y))
    for n, x, y in palme:
        rows.append(("SM_Morin_PalmaA", n, x, y, ZF, 0.0))
        rows.append(("SM_Pav_Aiuola", n.replace("Palma", "Aiuola"), x, y, ZF, 0.0))
    # panchine: una ogni due palme, nel varco fra due palme del filare 1, spostate verso il mare
    panch = []
    for k in range(0, N_PALME - 1, 2):
        x = X_PALMA0 + PASSO * (k + 0.5)
        panch.append((x, Y_F1 + PANCH_DY))
    for i, (x, y) in enumerate(panch):
        rows.append(("SM_Morin_Panchina", f"Panchina_{i:02d}", x, y, ZF, 0.0))
    # lampioni: uno ogni 4 palme, subito dietro (lato citta) a una panchina su due
    for i, (x, y) in enumerate(panch[::2]):
        rows.append(("SM_Morin_Lampione", f"Lampione_{i:02d}", x + LAMP_DX, y + LAMP_DY, ZF, 0.0))
    # tombini: coppie nel corridoio, circa una ogni 3-4 palme, intervalli irregolari ma deterministici
    rnd = random.Random(seed_tombini)
    k = rnd.randint(0, 2)
    i = 0
    while k < N_MOD:
        x0 = X0_MOD + PASSO * k + X_TRASV + STRIP / 2      # campata del corridoio fra due strisce trasversali
        x = x0 + rnd.uniform(1.3, PASSO - STRIP - 1.3)
        y = rnd.uniform(Y_S1[1] + 0.9, Y_S2[0] - 0.9)
        if not _gazebo_hit(x, y, 1.0) and x < X0_MOD + PASSO * N_MOD - 1.0:
            rows.append(("SM_Morin_Tombino", f"Tombino_{i:02d}", round(x, 2), round(y, 2), ZF, rnd.choice((0.0, 180.0))))
            i += 1
        k += rnd.choice((3, 3, 4, 4, 5))
    rows.append(("SM_Morin_Gazebo", "Gazebo_00", GAZEBO[0], GAZEBO[1], ZF, 0.0))
    return rows


# impronte in pianta (semi-lati X, Y in metri) per il controllo dei conflitti; per il gazebo vale la gronda
# (un lampione alto 4,8 m non puo stare sotto il tetto)
FOOT = {"SM_Pav_Aiuola": (AIU_X / 2, AIU_Y / 2), "SM_Morin_Panchina": (1.4, 0.25), "SM_Morin_Lampione": (0.2, 0.2),
        "SM_Morin_Tombino": (0.88, 0.30), "SM_Morin_Gazebo": (GAZ_RE, GAZ_RE * math.sqrt(3) / 2)}


def check_footprints(rows, margin=0.0, verbose=True):
    """Controllo impronte: coppie di istanze con rettangoli in pianta sovrapposti (+ margine) e istanze che escono
    dalla fascia palme (X 9,75-252,75, Y 89,15-102). Ritorna (conflitti, distanze nette dei vicini del gazebo)."""
    items = [(a, n, x, y) + FOOT[a] for a, n, x, y, z, yaw in rows if a in FOOT]
    bad, near = [], {}
    x_lo, x_hi = X0_MOD, X0_MOD + PASSO * N_MOD
    for a, n, x, y, hx, hy in items:
        if x - hx < x_lo or x + hx > x_hi or y - hy < K1 or y + hy > Y_END:
            bad.append(("fuori fascia", n))
    for i in range(len(items)):
        a1, n1, x1, y1, hx1, hy1 = items[i]
        for j in range(i + 1, len(items)):
            a2, n2, x2, y2, hx2, hy2 = items[j]
            gap = max(abs(x1 - x2) - hx1 - hx2, abs(y1 - y2) - hy1 - hy2)
            if gap < margin:
                bad.append((n1, n2, round(gap, 2)))
            if ("Gazebo" in n1 or "Gazebo" in n2) and gap < 3.0:
                near[n2 if "Gazebo" in n1 else n1] = round(gap, 2)
    if verbose:
        print(f"controllo impronte: {len(items)} istanze, {len(bad)} conflitti", bad[:20])
        print("  vicini del gazebo (distanza netta in pianta, m):", near)
    return bad, near


def _camm_rows():
    """Camminamento: stesse 58 istanze della v1 (dalle trasformazioni dei moduli banchina)."""
    import csv
    out = []
    with open(PROJ + "/exports/pavimentazione/pav_posizioni.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["asset"] == "SM_Pav_Camminamento_4m":
                out.append(r)
    return out


def write_csv(rows, pav="exports/pavimentazione/pav_posizioni_v3.csv",
              palme="exports/pavimentazione/palme_posizioni_v3.csv"):
    def ue(v):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return "0.0" if s in ("0", "-0") else (s if "." in s else s + ".0")

    lines = ["asset,nome,x,y,z,yaw"]
    for r in _camm_rows():
        lines.append(",".join([r["asset"], r["nome"], r["x"], r["y"], r["z"], r["yaw"]]))
    for k in range(N_MOD):
        x = ue((X0_MOD + PASSO * k) * 100)
        lines.append(f"SM_Pav_Cordolo_9m,Cordolo_{k:02d},{x},0.0,0.0,0.0")
        lines.append(f"SM_Pav_FasciaPalme_9m,Fascia_{k:02d},{x},0.0,0.0,0.0")
    for a, n, x, y, z, yaw in rows:
        if a == "SM_Morin_PalmaA":
            continue
        lines.append(f"{a},{n},{ue(x * 100)},{ue(-y * 100)},{ue(z * 100)},{ue(-yaw if yaw else 0.0)}")
    with open(f"{PROJ}/{pav}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    pl = ["nome,x,y,z,yaw"]
    for a, n, x, y, z, yaw in rows:
        if a == "SM_Morin_PalmaA":
            pl.append(f"{n},{ue(x * 100)},{ue(-y * 100)},{ue(z * 100)},0.0")
    with open(f"{PROJ}/{palme}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(pl) + "\n")
    return len(lines) - 1, len(pl) - 1


def build_context(rows, name="PAV_Contesto_v3", prefix="V3_"):
    """Contesto per i render: oggetti collegati (stessa mesh) alle mesh del kit, banchina e palma."""
    coll = _coll(name)
    mesh_of = {a: bpy.data.objects[a].data for a in
               ("SM_Pav_Aiuola", "SM_Morin_Panchina", "SM_Morin_Lampione", "SM_Morin_Tombino", "SM_Morin_Gazebo",
                "SM_Morin_PalmaA", "SM_Pav_Cordolo_9m", "SM_Pav_FasciaPalme_9m", "SM_Pav_Camminamento_4m",
                "SM_Banchina_Mod4m")}

    def put(n, me, loc, rotz=0.0):
        o = bpy.data.objects.get(n)
        if o is None:
            o = bpy.data.objects.new(n, me)
            coll.objects.link(o)
        o.data = me
        o.location = loc
        o.rotation_euler = (0, 0, math.radians(rotz))
        return o

    rnd = random.Random(20261119)
    for a, n, x, y, z, yaw in rows:
        rz = rnd.uniform(0, 360) if a == "SM_Morin_PalmaA" else yaw
        put(prefix + n, mesh_of[a], (x, y, z), rz)
    for k in range(N_MOD):
        x = X0_MOD + PASSO * k
        put(f"{prefix}Cordolo_{k:02d}", mesh_of["SM_Pav_Cordolo_9m"], (x, 0, 0))
        put(f"{prefix}Fascia_{k:02d}", mesh_of["SM_Pav_FasciaPalme_9m"], (x, 0, 0))
    for r in _camm_rows():
        x, y, yaw = float(r["x"]) / 100, -float(r["y"]) / 100, -float(r["yaw"])
        put(prefix + r["nome"], mesh_of["SM_Pav_Camminamento_4m"], (x, y, 0), yaw)
        put(prefix + "Banchina_" + r["nome"][5:], mesh_of["SM_Banchina_Mod4m"], (x, y, 0), yaw)
    return coll
