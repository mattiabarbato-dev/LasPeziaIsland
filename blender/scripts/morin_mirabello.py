"""morin_mirabello.py — testata di Porto Mirabello (arrivo del Ponte Thaon di Revel), v1 2026-11-20.

Sostituisce il blockout `SM_Blockout_Mirabello` (rampa 7 %, spalla, testata 30 x 49,4 m).

Dati (ref/osm/morin_bbox.osm, coordinate di progetto, metri) [V]:
  fine ponte (-5,2; -178,7) · scala 14 gradini (way 850283512) verso O fino a X -15,8 poi verso S fino a Y -186,9 ·
  passerella in legno sopraelevata (way 1120598342, layer 1, wheelchair=yes) da (-5,2; -178,7) a (46,1; -176,9) ·
  costa (9,7; -167,1) (-5,0; -167,9) (-25,7; -169,0) · siepe (851093571) (-1,5; -175,8) (-14,4; -176,6) (-63,7; -180,5) ·
  recinzione metallica (850283513) (-1,5; -175,8) -> (113,5; -168,4) · strada di servizio a senso unico (379766628)
  asse (-49; -188,7) (-15,8; -186,9) (22,6; -184,7) e ritorno (-48,4; -204,1) (24,4; -201,4) · parcheggio a raso
  (379766626) · multipiano (175935357, 2 livelli, tetto a parcheggio 379778073 con muretto h 1) fronte nord a Y -208 ·
  pontili 912795085..089 · fanale rosso (1327347935) (109,7; -165,6) luce a 6 m · prati 175935420/421/422.
Stime [S]: quota del suolo = banchina (Z 0), larghezze di passerella (3,8 m), pianerottolo, scala (3,6 m), carreggiate,
stalli 2,5 x 4,6 m, materiali (nessuna foto ravvicinata di Mirabello), altezze del multipiano (3,5 m a piano), yacht.

Asset nuovi (tutti senza texture nuove: riusano materiali gia' in UEFN):
  SM_Mirabello_Suolo         scene  asfalto, stalli, strisce, quai in masselli, marciapiede, siepe. UCX
  SM_Mirabello_Pianerottolo  scene  pianerottolo in legno a Z 1,30 + scala in cemento + ringhiere. UCX
  SM_Mirabello_Passerella    scene  passerella in legno a Z 1,30 -> 0 (X -0,6 -> 46,1) con ringhiere. UCX
  SM_Mirabello_Multipiano    scene  multipiano di fondale (atlante M_Morin_Imbarco). 1 UCX sul fronte raggiungibile
  SM_Mirabello_Fondale       scene  suolo di fondale fuori dal box giocabile (Z +0,02), ciglio, recinzione, prati. no UCX
  SM_Mirabello_Pontile       asset  pontile galleggiante 48 x 2,8 m, LOD 50/15 %. no UCX
  SM_Mirabello_YachtA/B      asset  motoryacht 12,5 m / barca a vela 11 m, LOD 50/15 %. no UCX
  SM_Mirabello_Fanale        asset  fanale rosso h 6 m. no UCX

Esegui dentro blender/arte_mirabello.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_mirabello as mb; importlib.reload(mb)
    mb.build_materials(); mb.build_all(); mb.write_csv(); mb.build_context(); mb.export_all()
    mb.cameras(); mb.render_all()

Convenzioni: Blender in metri, CSV in coordinate UE (X*100, -Y*100, Z*100), yaw UE = -rotZ Blender.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_imbarco as mi

PROJ = pk.PROJ
KIT = "MIRABELLO_Kit"
CTX = "MIRABELLO_Contesto"
EXPDIR = "//../exports/mirabello"
TEX = PROJ + "/blender/textures"

# ---- quote e piante [V OSM + S] ------------------------------------------------------------------------------------
Z_DECK = 1.30                      # fine del calpestio del ponte (arte_ponte.blend, Y -179)
BOX = (-20.2, 9.8, -217.4)         # area giocabile (barriere Mirabello: X -2020..980, Y fino a 21740 uu)
LAND = (-17.8, 3.0, -182.6, -179.0)       # pianerottolo x0 x1 y0 y1
HEAD = (-0.6, 3.0, -179.0, -176.6)        # testa piana della passerella
PASS = (3.0, 46.1, -180.4, -176.6)        # passerella in discesa
STAIR = (-17.8, -14.2, -186.6, -182.6)    # scala (8 alzate da 16,25 cm)
N_RISE = 8
SPALLA_X = (-8.73, -0.63)          # spalla del ponte (arte_ponte.blend)
ROAD_N = (-191.25, -186.75)        # corsia nord (senso unico) [S: asse OSM -186,9 spostato 2 m a S per la scala]
ROW1 = (-195.875, -191.25)
ROW2 = (-200.5, -195.875)
ROAD_S = (-204.6, -200.5)          # corsia sud (OSM asse -202,3 a X 0)
SIDEW = (-218.0, -204.6)           # marciapiede h 0,15 fino sotto il multipiano
Z_SIDEW = 0.15
WALK_X = (-18.5, -13.5)            # passaggio pedonale scala -> multipiano (niente stalli)
STALL_X0, STALL_W = -13.5, 2.5
HEDGE = [(-8.73, -176.15), (-14.4, -176.6), (-20.2, -177.06), (-60.0, -180.2)]
HEDGE_W, HEDGE_H = 0.8, 1.0
FENCE = [(-0.4, -175.73), (113.5, -168.4)]
COAST_E = [(9.8, -167.09), (28.0, -166.0), (56.4, -164.5), (92.1, -162.5), (116.0, -161.2), (114.8, -169.5),
           (116.1, -175.4), (116.8, -250.0)]
COAST_W = [(-20.2, -168.70), (-25.7, -169.0), (-54.9, -170.6), (-60.0, -170.9)]
MP = [(27.9, -207.7), (-81.4, -212.1), (-100.3, -214.0), (-121.0, -236.5), (-121.0, -248.6), (-136.0, -266.7),
      (-95.5, -302.8), (-37.3, -299.0), (-37.3, -293.6), (-1.6, -292.4), (8.9, -294.3), (7.2, -265.3), (31.5, -264.6),
      (30.7, -252.7), (24.1, -252.5), (24.2, -241.0), (29.6, -241.5)]
MP_Z = (0.3, 3.0, 4.3, 6.2, 7.1, 8.1)     # zoccolo, fine vetrine, fascia, fine piano 1, tetto, muretto (h 1 m [V])
PRATI = [[(87.9, -184.8), (82.5, -190.8), (101.6, -208.0), (107.1, -201.8)],
         [(91.1, -181.7), (99.2, -181.3), (103.8, -183.0), (107.5, -186.4), (109.8, -190.7), (110.4, -194.9),
          (109.5, -198.4)],
         [(29.4, -203.8), (36.7, -203.5), (44.3, -213.6), (29.6, -241.5), (27.9, -207.7)]]
PONTILI = {"085": ((-54.9, -170.6), (-57.7, -115.2)), "086": ((-25.7, -169.0), (-27.9, -125.0)),
           "087": ((28.0, -166.0), (25.4, -117.5)), "088": ((56.4, -164.5), (54.4, -116.8)),
           "089": ((92.1, -162.5), (89.9, -113.8))}
PONT_L, PONT_W, PONT_Z = 48.0, 2.8, -0.45
Z_ACQUA = -1.0
FANALE = (109.7, -165.6)


def coast(x):
    """Y del ciglio fra X -25,7 e 9,8 (retta per i nodi OSM della costa)."""
    return -167.1 + (x - 9.7) * 0.05367


COAST_ROT = 180.0 + math.degrees(math.atan(0.05367))     # moduli banchina: +Y locale verso terra (-Y mondo)

# ---- materiali (tutti gia' in UEFN) ---------------------------------------------------------------------------------
MATS = {
    "M_Parcheggio_Asfalto": (TEX + "/parcheggio/T_Parcheggio_Asfalto", None, 8.0),
    "M_Viale_Segnaletica": (TEX + "/viale/T_Viale_Segnaletica", None, 1.0),
    "M_Molo_Masselli": (TEX + "/molo/T_Molo_Masselli", None, 2.8),
    "M_Molo_Masselli_Grigio": (TEX + "/molo/T_Molo_Masselli", (0.36, 0.37, 0.40), 2.8),
    "M_Morin_Bosso": (TEX + "/viale/T_Morin_Bosso", None, 1.5),
    "M_Morin_Prato": (TEX + "/viale/T_Morin_Prato", None, 4.0),
    "M_Ponte_Legno": (TEX + "/ponte/T_Ponte_Legno", None, 6.0),
    "M_Ponte_Acciaio": (TEX + "/ponte/T_Ponte_Acciaio", None, 4.0),
    "M_Banchina_Paramento": (TEX + "/T_Banchina_Paramento", None, 2.0),
    "M_Pav_Fascia": (TEX + "/T_Pav_Fascia", None, 1.0),
    "M_Morin_Imbarco": (TEX + "/imbarco/T_Morin_Imbarco", None, 1.0),
    "M_Morin_Imbarco_Legno": (TEX + "/imbarco/T_Morin_Imbarco_Legno", None, 2.0),
}


def _limg(path, noncolor):
    name = os.path.basename(path)
    im = bpy.data.images.get((name, None))
    if im is None:
        im = bpy.data.images.load(path, check_existing=False)
        im.name = name
    if noncolor:
        im.colorspace_settings.name = "Non-Color"
    return im


def _lmat(name):
    """Materiale LOCALE con il nome esatto (puo' coesistere con l'omonimo collegato dal contesto)."""
    m = bpy.data.materials.get((name, None))
    if m is not None:
        return m
    base, tint, _ = MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(nd)
    out = next(nd for nd in nt.nodes if nd.type == "OUTPUT_MATERIAL")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    td = nt.nodes.new("ShaderNodeTexImage")
    td.image = _limg(base + "_D.png", False)
    col = td.outputs["Color"]
    if tint is not None:
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.inputs[7].default_value = (*tint, 1.0)
        nt.links.new(col, mix.inputs[6])
        col = mix.outputs[2]
    nt.links.new(col, bsdf.inputs["Base Color"])
    to = nt.nodes.new("ShaderNodeTexImage")
    to.image = _limg(base + "_ORM.png", True)
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(to.outputs["Color"], sep.inputs[0])
    nt.links.new(sep.outputs[1], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs[2], bsdf.inputs["Metallic"])
    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = _limg(base + "_N.png", True)
    sepn = nt.nodes.new("ShaderNodeSeparateColor")
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    comb = nt.nodes.new("ShaderNodeCombineColor")
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tn.outputs["Color"], sepn.inputs[0])
    nt.links.new(sepn.outputs[0], comb.inputs[0])
    nt.links.new(sepn.outputs[1], inv.inputs[1])
    nt.links.new(inv.outputs[0], comb.inputs[1])
    nt.links.new(sepn.outputs[2], comb.inputs[2])
    nt.links.new(comb.outputs[0], nm.inputs["Color"])
    nt.links.new(nm.outputs[0], bsdf.inputs["Normal"])
    m.use_fake_user = True
    return m


def build_materials():
    return [_lmat(n).name for n in MATS]


def _localize(o):
    """Gli slot puntano sempre ai materiali locali (mai a quelli collegati dal contesto)."""
    for s in o.material_slots:
        if s.material is not None and s.material.library is not None:
            s.material = _lmat(s.material.name)
    return o


class Geo(mi.Geo):
    """mi.Geo con il layer UV chiamato esplicitamente "UVMap" (in Blender 5.3 verify() crea un nome diverso e
    mi.Geo.finish lo scarterebbe: mesh senza UV)."""

    def finish(self, name, coll, smooth=None):
        if not self.bm.loops.layers.uv:
            self.bm.loops.layers.uv.new("UVMap")
        return mi.Geo.finish(self, name, coll, smooth)


# =================================================================================================================
# utilita' di geometria per le mesh PBR (UV mondo)
# =================================================================================================================
class PB:
    def __init__(self, mats):
        self.bm = bmesh.new()
        self.mats = mats

    def mi(self, m):
        return self.mats.index(m)

    def face(self, pts, m, out=None):
        vs = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(vs)
        f.material_index = self.mi(m)
        f.normal_update()
        if out is not None and f.normal.dot(Vector(out)) < 0:
            f.normal_flip()
        return f

    def poly(self, pts2, z, m, up=True):
        f = self.face([(x, y, z) for x, y in pts2], m, out=(0, 0, 1 if up else -1))
        res = bmesh.ops.triangulate(self.bm, faces=[f], quad_method="BEAUTY", ngon_method="EAR_CLIP")
        return res

    def wall(self, a, b, z0a, z1a, z0b, z1b, m, out):
        """Parete verticale fra i punti 2D a e b (quote per estremo)."""
        return self.face([(a[0], a[1], z0a), (b[0], b[1], z0b), (b[0], b[1], z1b), (a[0], a[1], z1a)], m, out=out)

    def box(self, x0, x1, y0, y1, z0, z1, m, faces=("top", "xn", "xp", "yn", "yp")):
        fs = pk._box(self.bm, x0, x1, y0, y1, z0, z1, mi=self.mi(m), faces=faces)
        for f in fs:
            f.normal_update()
        return fs

    def beam(self, p0, p1, w, h, m, caps=False):
        """Trave a sezione rettangolare w x h fra due punti 3D (asse orizzontale in pianta)."""
        p0, p1 = Vector(p0), Vector(p1)
        d = (p1 - p0)
        dh = Vector((d.x, d.y, 0)).normalized()
        s = Vector((-dh.y, dh.x, 0)) * (w / 2)
        u = Vector((0, 0, h / 2))
        c0 = [p0 - s - u, p0 + s - u, p0 + s + u, p0 - s + u]
        c1 = [p1 - s - u, p1 + s - u, p1 + s + u, p1 - s + u]
        mid = (p0 + p1) / 2
        out = []
        for k in range(4):
            k1 = (k + 1) % 4
            q = [c0[k], c0[k1], c1[k1], c1[k]]
            cen = sum(q, Vector()) / 4
            out.append(self.face(q, m, out=cen - mid - d.normalized() * (cen - mid).dot(d.normalized())))
        if caps:
            out.append(self.face(c0, m, out=-d))
            out.append(self.face(c1, m, out=d))
        return out

    def post(self, x, y, z0, z1, r, m):
        return self.box(x - r, x + r, y - r, y + r, z0, z1, m)

    def finish(self, name, coll, wood_along_x=True):
        bm = self.bm
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bm.normal_update()
        uv = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            m = self.mats[f.material_index]
            t = MATS[m][2]
            n = f.normal
            for lp in f.loops:
                c = lp.vert.co
                if abs(n.z) > 0.7:
                    if m == "M_Ponte_Legno" and wood_along_x:
                        lp[uv].uv = (-c.y / t, c.x / t)      # tavole lungo X (come il ponte lungo la sua direzione)
                    else:
                        lp[uv].uv = (c.x / t, -c.y / t)
                else:
                    ax = 0 if abs(n.x) > abs(n.y) else 1
                    lp[uv].uv = ((c.y if ax == 0 else c.x) / t, c.z / t)
        o = pk._finish(name, bm, self.mats, coll, uv=None)
        return _localize(o)


def _rail(g, pts, z0s, m="M_Ponte_Acciaio", h=1.15, step=1.5, bars=(0.15, 0.40, 0.65, 0.90), lod=0):
    """Ringhiera bianca (ref/foto/ponte/ringhiera_ponte.png): montanti ogni <= 1,5 m, corrimano, traversi orizzontali.
    pts: polilinea 2D, z0s: quota del piano di calpestio a ogni punto."""
    P = [Vector((p[0], p[1], z)) for p, z in zip(pts, z0s)]
    for a, b in zip(P[:-1], P[1:]):
        L = (Vector((b.x, b.y)) - Vector((a.x, a.y))).length
        n = max(1, math.ceil(L / step - 1e-6))
        for k in range(n + 1):
            if k == 0 and a is not P[0]:
                continue
            t = k / n
            p = a.lerp(b, t)
            g.post(p.x, p.y, p.z, p.z + h - 0.03, 0.03, m)
        g.beam(a + Vector((0, 0, h - 0.025)), b + Vector((0, 0, h - 0.025)), 0.07, 0.05, m)
        if lod == 0:
            for zb in bars:
                g.beam(a + Vector((0, 0, zb)), b + Vector((0, 0, zb)), 0.02, 0.02, m)


# =================================================================================================================
# suolo della testata (pezzo unico, coordinate di progetto)
# =================================================================================================================
def build_suolo(coll, name="SM_Mirabello_Suolo"):
    M = ["M_Parcheggio_Asfalto", "M_Viale_Segnaletica", "M_Molo_Masselli", "M_Molo_Masselli_Grigio", "M_Morin_Bosso",
         "M_Pav_Fascia"]
    g = PB(M)
    x0, x1 = BOX[0], BOX[1]
    c = lambda x: coast(x) - 0.55        # dietro i blocchi del ciglio (SM_Banchina_Mod4m_v2, profondi 0,55 m)
    hn = [(x, y + HEDGE_W / 2) for x, y in HEDGE[:3]]
    hs = [(x, y - HEDGE_W / 2) for x, y in HEDGE[:3]]
    # quai della marina (masselli) a nord della siepe e a est della spalla
    g.poly([(x0, c(x0)), (SPALLA_X[0], c(SPALLA_X[0])), hn[0], hn[1], hn[2]], 0.0, "M_Molo_Masselli")
    g.poly([(SPALLA_X[1], c(SPALLA_X[1])), (x1, c(x1)), (x1, HEAD[3]), (SPALLA_X[1], HEAD[3])], 0.0, "M_Molo_Masselli")
    # siepe di bosso (h 1 m [S])
    for a, b, an, bn, as_, bs in zip(HEDGE[:2], HEDGE[1:3], hn[:2], hn[1:], hs[:2], hs[1:]):
        g.face([(*an, HEDGE_H), (*bn, HEDGE_H), (*bs, HEDGE_H), (*as_, HEDGE_H)], "M_Morin_Bosso", out=(0, 0, 1))
        g.wall(an, bn, 0, HEDGE_H, 0, HEDGE_H, "M_Morin_Bosso", out=(0, 1, 0))
        g.wall(as_, bs, 0, HEDGE_H, 0, HEDGE_H, "M_Morin_Bosso", out=(0, -1, 0))
    g.wall(hn[2], hs[2], 0, HEDGE_H, 0, HEDGE_H, "M_Morin_Bosso", out=(-1, 0, 0))
    # asfalto: dalla siepe al marciapiede (sotto pianerottolo e passerella resta nascosto)
    g.poly([hs[2], hs[1], hs[0], (SPALLA_X[0], HEAD[3]), (x1, HEAD[3]), (x1, ROAD_S[0]), (x0, ROAD_S[0])], 0.0,
           "M_Parcheggio_Asfalto")
    # marciapiede del multipiano (masselli grigi) con cordolo in pietra
    g.box(x0, x1, SIDEW[0], ROAD_S[0] - 0.30, 0.0, Z_SIDEW, "M_Molo_Masselli_Grigio", faces=("top", "xn", "xp"))
    g.box(x0, x1, ROAD_S[0] - 0.30, ROAD_S[0], 0.0, Z_SIDEW, "M_Pav_Fascia", faces=("top", "yp", "xn", "xp"))
    # segnaletica orizzontale (Z +0,005)
    zs, w = 0.005, 0.12
    S = "M_Viale_Segnaletica"

    def stripe(xa, xb, ya, yb):
        g.face([(xa, ya, zs), (xb, ya, zs), (xb, yb, zs), (xa, yb, zs)], S, out=(0, 0, 1))
    x = STALL_X0
    while x <= x1 - 0.3:
        for (ya, yb) in (ROW1, ROW2):
            stripe(x - w / 2, x + w / 2, ya + (0.3 if ya == ROW2[0] else 0.0), yb - (0.3 if yb == ROW1[1] else 0.0))
        x += STALL_W
    stripe(STALL_X0, x1, ROW1[0] - w / 2, ROW1[0] + w / 2)                  # linea di mezzeria fra le due file
    for ya, yb in ((ROAD_N[0] + 0.25, ROAD_N[1] - 0.25), (ROAD_S[0] + 0.25, ROAD_S[1] - 0.25)):
        xz = -18.0
        while xz < -13.6:                                                      # strisce pedonali (bande da 0,5 m)
            stripe(xz, xz + 0.5, ya, yb)
            xz += 1.0
    for ya in (ROAD_N[0], ROAD_S[1]):                                          # linee di margine delle corsie
        stripe(STALL_X0, x1, ya - w / 2, ya + w / 2)
    o = g.finish(name, coll)
    for u in [u for u in bpy.data.objects if u.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)
    pts = [Vector((x, y, z)) for x, y in ((x0, c(x0)), (x1, c(x1)), (x1, SIDEW[0]), (x0, SIDEW[0])) for z in (-0.3, 0.0)]
    pk._ucx_hull(name, 0, pts, coll)
    pk._ucx(name, [(x0, x1, SIDEW[0], ROAD_S[0], -0.3, Z_SIDEW)], coll, start=1)
    for i, (a, b) in enumerate(zip(HEDGE[:2], HEDGE[1:3])):
        pts = [Vector((p[0], p[1] + s, z)) for p in (a, b) for s in (-HEDGE_W / 2, HEDGE_W / 2) for z in (0.0, HEDGE_H)]
        pk._ucx_hull(name, 2 + i, pts, coll)
    return o


# =================================================================================================================
# pianerottolo + scala (spalla Mirabello -> suolo)
# =================================================================================================================
def build_pianerottolo(coll, name="SM_Mirabello_Pianerottolo"):
    M = ["M_Ponte_Legno", "M_Ponte_Acciaio", "M_Banchina_Paramento", "M_Pav_Fascia"]
    g = PB(M)
    x0, x1, y0, y1 = LAND
    zf = Z_DECK - 0.30          # fascia d'acciaio sotto il tavolato
    g.box(x0, x1, y0, y1, Z_DECK - 0.05, Z_DECK, "M_Ponte_Legno", faces=("top",))
    # fianchi: basamento in pietra (come la spalla) + fascia in acciaio bianco
    sides = [((x0, y1), (SPALLA_X[0], y1), (0, 1, 0)),           # nord, fino alla spalla
             ((x0, y0), (x0, y1), (-1, 0, 0)),                     # ovest
             ((STAIR[1], y0), (x1, y0), (0, -1, 0)),               # sud (a est della scala)
             ((x1, y0), (x1, PASS[2]), (1, 0, 0))]                 # est, sotto la passerella
    for a, b, out in sides:
        g.wall(a, b, 0.0, zf, 0.0, zf, "M_Banchina_Paramento", out)
        g.wall(a, b, zf, Z_DECK, zf, Z_DECK, "M_Ponte_Acciaio", out)
    # scala: 8 alzate da 16,25 cm, pedate in pietra, cosciali in cemento larghi 0,15
    sx0, sx1, sy0, sy1 = STAIR
    ix0, ix1 = sx0 + 0.15, sx1 - 0.15
    dz = Z_DECK / N_RISE
    dy = (sy1 - sy0) / (N_RISE - 1)
    for k in range(1, N_RISE):
        ya = sy1 - dy * (k - 1)
        yb = sy1 - dy * k
        z = Z_DECK - dz * k
        g.face([(ix0, yb, z), (ix1, yb, z), (ix1, ya, z), (ix0, ya, z)], "M_Pav_Fascia", out=(0, 0, 1))
        g.face([(ix0, ya, z), (ix1, ya, z), (ix1, ya, z + dz), (ix0, ya, z + dz)], "M_Pav_Fascia", out=(0, -1, 0))
    g.face([(ix0, sy0, 0), (ix1, sy0, 0), (ix1, sy0, dz), (ix0, sy0, dz)], "M_Pav_Fascia", out=(0, -1, 0))
    zt = lambda y: 0.25 + (Z_DECK + 0.10 - 0.25) * (y - (sy0 - 0.0)) / (sy1 - sy0)     # sommita' dei cosciali
    for xa, xb in ((sx0, ix0), (ix1, sx1)):
        for xx, out in ((xa, (-1, 0, 0)), (xb, (1, 0, 0))):
            g.face([(xx, sy0, 0), (xx, sy1, 0), (xx, sy1, zt(sy1)), (xx, sy0, zt(sy0))], "M_Banchina_Paramento",
                   out=out)
        g.face([(xa, sy0, zt(sy0)), (xb, sy0, zt(sy0)), (xb, sy1, zt(sy1)), (xa, sy1, zt(sy1))], "M_Pav_Fascia",
               out=(0, 0, 1))
        g.face([(xa, sy0, 0), (xb, sy0, 0), (xb, sy0, zt(sy0)), (xa, sy0, zt(sy0))], "M_Banchina_Paramento",
               out=(0, -1, 0))
    # ringhiere (h 1,15 dal calpestio, come il ponte)
    r = 0.04
    _rail(g, [(x0 + r, y1 - r), (SPALLA_X[0] + 0.25, y1 - r)], [Z_DECK] * 2)
    _rail(g, [(x0 + r, y1 - r), (x0 + r, y0 + r)], [Z_DECK] * 2)
    _rail(g, [(sx1 - 0.075, y0 + r), (x1 - r, y0 + r), (x1 - r, PASS[2])], [Z_DECK] * 3)
    for xx in (sx0 + 0.075, sx1 - 0.075):
        _rail(g, [(xx, sy1), (xx, sy0 + 0.1)], [zt(sy1), zt(sy0 + 0.1)], step=1.4)
    o = g.finish(name, coll)
    for u in [u for u in bpy.data.objects if u.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)
    boxes = [(x0, x1, y0, y1, 0.0, Z_DECK),
             (x0, SPALLA_X[0] + 0.25, y1 - 0.10, y1, Z_DECK, Z_DECK + 1.15),        # ringhiera nord
             (x0, x0 + 0.10, y0, y1, Z_DECK, Z_DECK + 1.15),                        # ovest
             (sx1 - 0.15, x1, y0, y0 + 0.10, Z_DECK, Z_DECK + 1.15),                # sud
             (x1 - 0.10, x1, y0, PASS[2], Z_DECK, Z_DECK + 1.15)]                   # est
    pk._ucx(name, boxes, coll)
    wedge = [Vector((x, y, z)) for x in (sx0, sx1) for (y, z) in ((sy1, 0.0), (sy1, Z_DECK), (sy0, 0.0))]
    pk._ucx_hull(name, len(boxes), wedge, coll)
    for i, xx in enumerate((sx0, sx1 - 0.15)):
        pts = [Vector((x, y, z)) for x in (xx, xx + 0.15) for (y, z) in ((sy1, 0), (sy1, zt(sy1) + 1.0), (sy0, 0),
                                                                          (sy0, zt(sy0) + 1.0))]
        pk._ucx_hull(name, len(boxes) + 1 + i, pts, coll)
    return o


# =================================================================================================================
# passerella in legno verso NE (OSM 1120598342), da Z 1,30 a 0 [pendenza 3 %]
# =================================================================================================================
def z_pass(x):
    if x <= PASS[0]:
        return Z_DECK
    return max(0.0, Z_DECK * (1 - (x - PASS[0]) / (PASS[1] - PASS[0])))


def build_passerella(coll, name="SM_Mirabello_Passerella"):
    M = ["M_Ponte_Legno", "M_Ponte_Acciaio", "M_Banchina_Paramento"]
    g = PB(M)
    hx0, hx1, hy0, hy1 = HEAD
    px0, px1, py0, py1 = PASS
    g.face([(hx0, hy0, Z_DECK), (hx1, hy0, Z_DECK), (hx1, hy1, Z_DECK), (hx0, hy1, Z_DECK)], "M_Ponte_Legno",
           out=(0, 0, 1))
    xs = [px0 + (px1 - px0) * k / 6 for k in range(7)]
    for a, b in zip(xs[:-1], xs[1:]):
        g.face([(a, py0, z_pass(a)), (b, py0, z_pass(b)), (b, py1, z_pass(b)), (a, py1, z_pass(a))], "M_Ponte_Legno",
               out=(0, 0, 1))
    # fianchi: pietra + fascia d'acciaio da 0,30 (che si assottiglia verso terra)
    for (ya, out, xa) in ((py1, (0, 1, 0), hx0), (py0, (0, -1, 0), px0)):
        pts = [xa] + xs if xa < px0 else xs
        for a, b in zip(pts[:-1], pts[1:]):
            za, zb = z_pass(a), z_pass(b)
            fa, fb = max(0.0, za - 0.30), max(0.0, zb - 0.30)
            if fa > 0 or fb > 0:
                g.wall((a, ya), (b, ya), 0.0, fa, 0.0, fb, "M_Banchina_Paramento", out)
            g.wall((a, ya), (b, ya), fa, za, fb, zb, "M_Ponte_Acciaio", out)
    g.wall((hx0, hy1), (hx0, hy0), 0.0, Z_DECK - 0.3, 0.0, Z_DECK - 0.3, "M_Banchina_Paramento", (-1, 0, 0))
    g.wall((hx0, hy1), (hx0, hy0), Z_DECK - 0.3, Z_DECK, Z_DECK - 0.3, Z_DECK, "M_Ponte_Acciaio", (-1, 0, 0))
    r = 0.04
    north = [hx0 + r] + xs
    _rail(g, [(x, py1 - r) for x in north], [z_pass(x) for x in north])
    _rail(g, [(x, py0 + r) for x in xs], [z_pass(x) for x in xs])
    _rail(g, [(hx0 + r, hy0 + 0.1), (hx0 + r, hy1 - r)], [Z_DECK] * 2)
    o = g.finish(name, coll)
    for u in [u for u in bpy.data.objects if u.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)
    pk._ucx(name, [(hx0, hx1, hy0, hy1, 0.0, Z_DECK), (hx0, hx0 + 0.10, hy0, hy1, Z_DECK, Z_DECK + 1.15)], coll)
    slope = [Vector((x, y, z)) for y in (py0, py1) for (x, z) in ((px0, 0.0), (px0, Z_DECK), (px1, 0.0))]
    pk._ucx_hull(name, 2, slope, coll)
    for i, (ya, yb) in enumerate(((py1 - 0.10, py1), (py0, py0 + 0.10))):
        x_a = hx0 if i == 0 else px0
        pts = [Vector((x, y, z)) for y in (ya, yb) for (x, z) in ((x_a, Z_DECK), (x_a, Z_DECK + 1.15), (px0, Z_DECK),
                                                                  (px0, Z_DECK + 1.15), (px1, 0.0), (px1, 1.15))]
        pk._ucx_hull(name, 3 + i, pts, coll)
    return o


# =================================================================================================================
# multipiano di fondale (atlante M_Morin_Imbarco)
# =================================================================================================================
def _inset(poly, d):
    """Poligono rientrato di d (antiorario o orario: rientra verso l'interno)."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n)) / 2
    sgn = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e1 = (p1 - p0).normalized()
        e2 = (p2 - p1).normalized()
        n1 = Vector((-e1.y, e1.x)) * sgn      # normale interna
        n2 = Vector((-e2.y, e2.x)) * sgn
        m = (n1 + n2)
        k = d / max(0.25, (1 + n1.dot(n2)) / 1.0) * 1.0
        out.append(tuple(p1 + m * (d / max(0.3, 1 + n1.dot(n2)))))
    return out


def build_multipiano(coll, name="SM_Mirabello_Multipiano"):
    g = Geo()
    P = MP
    n = len(P)
    I6 = _inset(P, 0.6)      # vetrine e piano aperto rientrati di 0,6 m
    I2 = _inset(P, 0.25)     # muretto del tetto (spessore 0,25)
    z0, z1, z2, z3, z4, z5 = MP_Z
    area = sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)) / 2
    sgn = 1.0 if area > 0 else -1.0
    cen = Vector((sum(p[0] for p in P) / n, sum(p[1] for p in P) / n, 4.0))
    for i in range(n):
        a, b = Vector(P[i]), Vector(P[(i + 1) % n])
        ai, bi = Vector(I6[i]), Vector(I6[(i + 1) % n])
        a2, b2 = Vector(I2[i]), Vector(I2[(i + 1) % n])
        e = (b - a).normalized()
        nout = -Vector((-e.y, e.x)) * sgn
        o3 = (nout.x, nout.y, 0)

        def q(p, r, za, zb, cell, out=o3):
            g.quad([(p.x, p.y, za), (r.x, r.y, za), (r.x, r.y, zb), (p.x, p.y, zb)], cell, out=out)

        def h(p, r, pi, ri, z, cell, up):
            g.quad([(p.x, p.y, z), (r.x, r.y, z), (ri.x, ri.y, z), (pi.x, pi.y, z)], cell, out=(0, 0, 1 if up else -1))
        q(a, b, 0.0, z0, "GRIGIO")                      # zoccolo
        q(ai, bi, z0, z1, "VETRO")                      # vetrine del piano terra [S]
        h(a, b, ai, bi, z0, "GRIGIO", True)
        h(a, b, ai, bi, z1, "GRIGIO", False)
        q(a, b, z1, z2, "BIANCO")                       # fascia del solaio
        q(ai, bi, z2, z3, "SCURO")                      # piano 1 aperto (parcheggio) [S]
        h(a, b, ai, bi, z2, "BIANCO", True)
        h(a, b, ai, bi, z3, "GRIGIO", False)
        q(a, b, z3, z5, "BIANCO")                       # solaio del tetto + muretto (h 1 m)
        h(a, b, a2, b2, z5, "BIANCO", True)
        q(a2, b2, z4, z5, "BIANCO", out=(-nout.x, -nout.y, 0))
        # pilastri ogni ~7,5 m nella fascia rientrata
        L = (b - a).length
        m = int(L // 7.5)
        for k in range(1, m + 1):
            t = k / (m + 1)
            pc = a.lerp(b, t) - nout.to_2d() * 0.35 if False else a.lerp(b, t)
            c3 = Vector((pc.x, pc.y, 0)) - Vector(o3) * 0.35
            M = Matrix.Translation(c3) @ Matrix.Rotation(math.atan2(e.y, e.x), 4, "Z")
            for (za, zb) in ((z0, z1), (z2, z3)):
                g.box(-0.25, 0.25, -0.25, 0.25, za, zb, "BIANCO", faces=("xn", "xp", "yn", "yp"), mat=M)
    # tetto (asfalto grigio dell'atlante) + due torri scala/ascensore [S]
    f = pk._quad(g.bm, [(x, y, z4) for x, y in I2]) if False else None
    vs = [g.bm.verts.new((x, y, z4)) for x, y in I2]
    face = g.bm.faces.new(vs)
    face.normal_update()
    if face.normal.z < 0:
        face.normal_flip()
    g._set([face], "GRIGIO")
    res = bmesh.ops.triangulate(g.bm, faces=[face], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    g._set(res["faces"], "GRIGIO")
    for (cx, cy, w, d) in ((-45.0, -262.0, 5.0, 7.0), (5.0, -232.0, 5.0, 6.0)):
        g.box(cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z4, z4 + 3.2, "BIANCO",
              faces=("top", "xn", "xp", "yn", "yp"))
        g.box(cx - w / 2 + 0.6, cx - w / 2 + 2.0, cy + d / 2, cy + d / 2 + 0.02, z4, z4 + 2.3, "VETRO", faces=("yp",))
    # ristorante a un piano accanto (379803221, h 4 [S])
    for (bx0, bx1, by0, by1) in ((8.0, 35.5, -292.8, -265.3),):
        g.box(bx0, bx1, by0, by1, 0.0, 0.5, "GRIGIO", faces=("xn", "xp", "yn", "yp"))
        g.box(bx0 + 0.3, bx1 - 0.3, by0 + 0.3, by1 - 0.3, 0.5, 3.4, "VETRO", faces=("xn", "xp", "yn", "yp"))
        g.box(bx0, bx1, by0, by1, 3.4, 4.0, "BIANCO", faces=("top", "xn", "xp", "yn", "yp"))
    o = g.finish(name, coll)
    _localize(o)
    for u in [u for u in bpy.data.objects if u.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)
    # collisione minima: solo il fronte raggiungibile dalla testata (X -25..15), fino al muretto
    yN = lambda x: -207.7 + (x - 27.9) * (4.4 / 109.3)
    pts = [Vector((x, y, z)) for x in (-25.0, 15.0) for y in (yN(x), -219.0) for z in (0.0, z5)]
    pk._ucx_hull(name, 0, pts, coll)
    return o


# =================================================================================================================
# fondale: suolo fuori dal box, ciglio, recinzione metallica, prati
# =================================================================================================================
def build_fondale(coll, name="SM_Mirabello_Fondale"):
    M = ["M_Parcheggio_Asfalto", "M_Molo_Masselli", "M_Banchina_Paramento", "M_Morin_Prato", "M_Morin_Bosso",
         "M_Ponte_Acciaio"]
    g = PB(M)
    zf = 0.02
    fy = lambda x: FENCE[0][1] + (x - FENCE[0][0]) * (FENCE[1][1] - FENCE[0][1]) / (FENCE[1][0] - FENCE[0][0])
    # est: quai in masselli fino alla recinzione, poi asfalto fino al multipiano
    g.poly(COAST_E[:6] + [FENCE[1], (BOX[1], fy(BOX[1]))], zf, "M_Molo_Masselli")
    g.poly([(BOX[1], fy(BOX[1])), FENCE[1], (114.8, -169.5), (116.1, -175.4), (116.8, -250.0), (29.8, -250.0),
            (29.6, -241.5), (27.9, -207.7), (BOX[1], -208.43)], zf, "M_Parcheggio_Asfalto")
    for pr in PRATI:
        g.poly(pr, zf + 0.03, "M_Morin_Prato")
    # ovest: quai, siepe, asfalto
    hw = HEDGE[2:]
    g.poly(COAST_W + [(hw[1][0], hw[1][1] + HEDGE_W / 2), (hw[0][0], hw[0][1] + HEDGE_W / 2)], zf, "M_Molo_Masselli")
    g.poly([(hw[0][0], hw[0][1] - HEDGE_W / 2), (hw[1][0], hw[1][1] - HEDGE_W / 2), (-60.0, -211.24),
            (BOX[0], -209.6)], zf, "M_Parcheggio_Asfalto")
    an, bn = (hw[0][0], hw[0][1] + HEDGE_W / 2), (hw[1][0], hw[1][1] + HEDGE_W / 2)
    as_, bs = (hw[0][0], hw[0][1] - HEDGE_W / 2), (hw[1][0], hw[1][1] - HEDGE_W / 2)
    g.face([(*an, HEDGE_H), (*bn, HEDGE_H), (*bs, HEDGE_H), (*as_, HEDGE_H)], "M_Morin_Bosso", out=(0, 0, 1))
    g.wall(an, bn, 0, HEDGE_H, 0, HEDGE_H, "M_Morin_Bosso", out=(0, 1, 0))
    g.wall(as_, bs, 0, HEDGE_H, 0, HEDGE_H, "M_Morin_Bosso", out=(0, -1, 0))
    # paramento del ciglio (da +0,02 a -1,6) fuori dal box
    for pts, side in ((COAST_E, 1), (COAST_W, -1)):
        for a, b in zip(pts[:-1], pts[1:]):
            d = Vector((b[0] - a[0], b[1] - a[1])).normalized()
            out = Vector((d.y, -d.x)) * side
            g.wall(a, b, -1.6, zf, -1.6, zf, "M_Banchina_Paramento", (out.x, out.y, 0))
    # recinzione metallica h 1,2 m [S] (montanti ogni 2,5 m, 3 correnti)
    a, b = Vector(FENCE[0]), Vector(FENCE[1])
    L = (b - a).length
    nseg = math.ceil(L / 2.5)
    for k in range(nseg + 1):
        p = a.lerp(b, k / nseg)
        g.post(p.x, p.y, zf, 1.2, 0.03, "M_Ponte_Acciaio")
    for zr in (0.12, 0.62, 1.17):
        g.beam((a.x, a.y, zr), (b.x, b.y, zr), 0.03, 0.04, "M_Ponte_Acciaio")
    return g.finish(name, coll)


# =================================================================================================================
# asset istanziati (atlante M_Morin_Imbarco): pontile, yacht, fanale
# =================================================================================================================
def build_pontile(coll, lod=0, name="SM_Mirabello_Pontile"):
    """Pontile galleggiante: origine alla radice sul piano di calpestio, +X verso la punta, largo 2,8 m."""
    g = Geo(ref=(PONT_L / 2, 0, -0.3))
    w = PONT_W / 2
    g.box(0.0, PONT_L, -w, w, -0.55, 0.0, "GRIGIO", faces=("xn", "xp", "yn", "yp"))
    g.box(0.0, PONT_L, -w, w, -0.05, 0.0, None, mi=1, faces=("top",))
    if lod <= 1:
        for x in np.arange(3.0, PONT_L - 1.0, 5.0):          # bitte / gallocce in acciaio, entrambi i lati
            for s in (-1, 1):
                g.box(x - 0.15, x + 0.15, s * w - 0.06 * s - 0.05, s * w - 0.06 * s + 0.05, 0.0, 0.12, "ACCIAIO",
                      faces=("top", "xn", "xp", "yn", "yp"))
        for x in np.arange(5.5, PONT_L - 1.0, 10.0):         # colonnine acqua/luce
            g.box(x - 0.15, x + 0.15, -0.15, 0.15, 0.0, 1.0, "BIANCO", faces=("top", "xn", "xp", "yn", "yp"))
    if lod == 0:
        g.box(0.0, PONT_L, -w - 0.08, -w, -0.35, -0.05, "GOMMA", faces=("yn", "top"))     # bottazzo
        g.box(0.0, PONT_L, w, w + 0.08, -0.35, -0.05, "GOMMA", faces=("yp", "top"))
    return g.finish(name + mi._sfx(lod), coll)


def _hull_loft(g, L, B, sheer, keel, lod, deck_cell="TEAK", top_cell="BIANCO", boot="BLU"):
    """Scafo per sezioni: origine al galleggiamento al centro, +X prua. Ritorna le quote della coperta per x."""
    ns = {0: 14, 1: 8, 2: 5}[lod]
    xs = [-L / 2 + L * (k / ns) ** 1.0 for k in range(ns + 1)]

    def hb(x):
        u = (x + L / 2) / L
        return B / 2 * (0.86 + 0.14 * math.sin(math.pi * min(u, 0.6) / 1.2)) if u < 0.55 else \
            B / 2 * max(0.04, math.sqrt(max(0.0, 1 - ((u - 0.55) / 0.45) ** 2)))

    def zs(x):
        u = (x + L / 2) / L
        return sheer[0] + (sheer[1] - sheer[0]) * u ** 2

    def zk(x):
        u = (x + L / 2) / L
        return keel * (1 - 0.7 * max(0.0, (u - 0.6) / 0.4))

    def sec(x, side):
        b = hb(x)
        z_s, z_k = zs(x), zk(x)
        pts = [(0.0, z_k), (0.55 * b, z_k * 0.35), (0.93 * b, 0.0), (0.97 * b, 0.20), (b, z_s)]
        if lod == 2:
            pts = [(0.0, z_k), (0.93 * b, 0.0), (b, z_s)]
        return [Vector((x, side * y, z)) for y, z in pts]
    cells = (["ANTIVEG", "ANTIVEG", boot, top_cell] if lod < 2 else ["ANTIVEG", top_cell])
    for side in (-1, 1):
        S = [sec(x, side) for x in xs]
        for a, b in zip(S[:-1], S[1:]):
            for j in range(len(a) - 1):
                q = [a[j], b[j], b[j + 1], a[j + 1]]
                g.quad([tuple(v) for v in q], cells[j], out=(0, side, 0.0))
        # specchio di poppa
        t = S[0]
        for j in range(len(t) - 1):
            q = [t[j], t[j + 1], Vector((t[j + 1].x, 0, t[j + 1].z)), Vector((t[j].x, 0, t[j].z))]
            g.quad([tuple(v) for v in q], cells[j] if j < len(cells) else top_cell, out=(-1, 0, 0))
        # coperta
        for a, b in zip(xs[:-1], xs[1:]):
            pa, pb = sec(a, side)[-1], sec(b, side)[-1]
            g.quad([tuple(pa), tuple(pb), (b, 0, pb.z), (a, 0, pa.z)], deck_cell, out=(0, 0, 1))
    return hb, zs


def build_yacht_a(coll, lod=0, name="SM_Mirabello_YachtA"):
    """Motoryacht ~12,5 x 4,0 m, scafo bianco, fascia blu, tuga con vetrate scure e flybridge con bimini [S]."""
    L, B = 12.5, 4.0
    g = Geo()
    hb, zs = _hull_loft(g, L, B, (1.25, 1.55), -0.85, lod)
    zd = 1.32
    # tuga: pianta a trapezio, fronte inclinato
    xr, xf, xt = -4.6, 2.6, 1.5
    w0 = 0.40 * B
    pts = [(xr, -w0, zd), (xr, w0, zd), (xf, -w0 * 0.8, zd), (xf, w0 * 0.8, zd),
           (xr, -w0, 2.45), (xr, w0, 2.45), (xt, -w0 * 0.75, 2.45), (xt, w0 * 0.75, 2.45)]
    g.hull(pts, "BIANCO")
    if lod < 2:
        for s in (-1, 1):                   # vetrate laterali e parabrezza
            yy = s * (w0 + 0.012)
            g.quad([(-3.9, yy, 1.75), (0.9, yy, 1.75), (0.9, yy, 2.25), (-3.9, yy, 2.25)], "VETRO", out=(0, s, 0))
        g.quad([(xf - 0.12, -w0 * 0.7, 1.80), (xf - 0.12, w0 * 0.7, 1.80), (xt + 0.05, w0 * 0.68, 2.38),
                (xt + 0.05, -w0 * 0.68, 2.38)], "VETRO", out=(1, 0, 0.6))
    # flybridge + bimini
    g.box(-4.2, 0.8, -0.36 * B, 0.36 * B, 2.45, 2.62, "BIANCO")
    g.box(-1.2, -0.6, -0.5, 0.5, 2.62, 3.05, "SCURO")                          # consolle
    g.box(-4.0, -0.6, -0.34 * B, 0.34 * B, 3.45, 3.50, "BLU")                  # tendalino
    if lod < 2:
        for x in (-3.9, -0.7):
            for s in (-1, 1):
                g.box(x - 0.02, x + 0.02, s * 0.33 * B - 0.02, s * 0.33 * B + 0.02, 2.62, 3.45, "ACCIAIO",
                      faces=("xn", "xp", "yn", "yp"))
    # plancetta di poppa
    g.box(-L / 2 - 0.7, -L / 2, -0.44 * B, 0.44 * B, 0.20, 0.30, "TEAK")
    if lod == 0:                             # battagliola sui passavanti
        for s in (-1, 1):
            rail = [(x, s * (hb(x) - 0.08), zs(x) + 0.6) for x in np.linspace(-3.5, L / 2 - 0.4, 8)]
            g.tube(rail, 0.018, 4, "ACCIAIO", cap=False)
            for x in np.linspace(-3.5, L / 2 - 0.4, 6):
                y = s * (hb(x) - 0.08)
                g.box(x - 0.015, x + 0.015, y - 0.015, y + 0.015, zs(x) - 0.02, zs(x) + 0.6, "ACCIAIO",
                      faces=("xn", "xp", "yn", "yp"))
    return g.finish(name + mi._sfx(lod), coll)


def build_yacht_b(coll, lod=0, name="SM_Mirabello_YachtB"):
    """Barca a vela ~11 x 3,6 m: scafo bianco, tuga bassa, albero 15 m, boma con vela avvolta blu [S]."""
    L, B = 11.0, 3.6
    g = Geo()
    hb, zs = _hull_loft(g, L, B, (0.95, 1.15), -0.7, lod, boot="BLU")
    # tuga bassa con oblo' scuri
    pts = [(-2.4, -0.33 * B, 0.95), (-2.4, 0.33 * B, 0.95), (2.6, -0.22 * B, 1.0), (2.6, 0.22 * B, 1.0),
           (-2.2, -0.30 * B, 1.42), (-2.2, 0.30 * B, 1.42), (2.0, -0.18 * B, 1.32), (2.0, 0.18 * B, 1.32)]
    g.hull(pts, "BIANCO")
    if lod < 2:
        for s in (-1, 1):
            yy = s * (0.315 * B + 0.01)
            g.quad([(-1.6, yy, 1.12), (1.2, s * (0.27 * B + 0.01), 1.12), (1.2, s * (0.27 * B + 0.01), 1.27),
                    (-1.6, yy, 1.27)], "SCURO", out=(0, s, 0))
    # pozzetto: battente
    g.box(-4.6, -2.4, -0.38 * B, 0.38 * B, 0.95, 1.20, "BIANCO", faces=("top", "xn", "yn", "yp"))
    sides = {0: 8, 1: 5, 2: 4}[lod]
    xm = 0.6
    g.tube([(xm, 0, 1.2), (xm, 0, 15.5)], 0.085, sides, "BIANCO")                      # albero
    g.tube([(xm, 0, 2.35), (-4.2, 0, 2.30)], 0.06, sides, "BIANCO")                    # boma
    g.tube([(xm - 0.2, 0, 2.55), (-4.0, 0, 2.50)], 0.20, sides, "BLU")                 # vela avvolta (copriranda)
    if lod < 2:
        g.tube([(xm, 0, 15.3), (L / 2 - 0.1, 0, zs(L / 2) + 0.05)], 0.012, 3, "ACCIAIO", cap=False)   # strallo
        g.tube([(xm, 0, 15.3), (-L / 2 + 0.2, 0, zs(-L / 2) + 0.05)], 0.012, 3, "ACCIAIO", cap=False)  # paterazzo
        g.tube([(L / 2 - 0.1, 0, 1.4), (xm + 0.05, 0, 14.0)], 0.10, 4, "BLU", cap=True)            # genoa avvolto
        for s in (-1, 1):
            g.tube([(xm, 0, 13.5), (xm - 0.3, s * (hb(xm) - 0.1), zs(xm))], 0.01, 3, "ACCIAIO", cap=False)
    if lod == 0:
        for s in (-1, 1):
            rail = [(x, s * (hb(x) - 0.06), zs(x) + 0.55) for x in np.linspace(-L / 2 + 0.3, L / 2 - 0.6, 8)]
            g.tube(rail, 0.012, 3, "ACCIAIO", cap=False)
    return g.finish(name + mi._sfx(lod), coll)


def build_fanale(coll, lod=0, name="SM_Mirabello_Fanale"):
    """Fanale rosso (OSM 1327347935, luce a 6 m): torretta cilindrica rossa, lanterna e cupolino [S]."""
    g = Geo()
    n = {0: 12, 1: 8, 2: 6}[lod]
    g.lathe([(0.55, 0.0), (0.55, 0.4)], n, "GRIGIO", cap_top=False)
    g.lathe([(0.40, 0.4), (0.36, 5.2)], n, "ROSSO", cap_top=False)
    g.lathe([(0.36, 5.2), (0.6, 5.25), (0.6, 5.35), (0.0, 5.36)], n, "ROSSO")
    g.lathe([(0.22, 5.36), (0.22, 6.0)], n, "VETRO", cap_top=False)
    g.lathe([(0.28, 6.0), (0.0, 6.3)], n, "ROSSO")
    return g.finish(name + mi._sfx(lod), coll)


ASSETS_SCENE = ["SM_Mirabello_Suolo", "SM_Mirabello_Pianerottolo", "SM_Mirabello_Passerella",
                "SM_Mirabello_Multipiano", "SM_Mirabello_Fondale"]
ASSETS_LOD = {"SM_Mirabello_Pontile": build_pontile, "SM_Mirabello_YachtA": build_yacht_a,
              "SM_Mirabello_YachtB": build_yacht_b, "SM_Mirabello_Fanale": build_fanale}


def build_all(lod_target=(1.0, 0.5, 0.15)):
    for n in MATS:
        _lmat(n)
    mi.MAT_A, mi.MAT_W = "M_Morin_Imbarco", "M_Morin_Imbarco_Legno"
    coll = pk._coll(KIT)
    build_suolo(coll)
    build_pianerottolo(coll)
    build_passerella(coll)
    build_multipiano(coll)
    build_fondale(coll)
    rep = {}
    for nm in ASSETS_SCENE:
        o = bpy.data.objects[nm]
        rep[nm] = [pk.tri_count(o), tuple(round(d, 2) for d in o.dimensions)]
    for nm, fn in ASSETS_LOD.items():
        objs = [_localize(fn(coll, 0))]
        t0 = pk.tri_count(objs[0])
        for lod in (1, 2):
            o = _localize(fn(coll, lod))
            t = pk.tri_count(o)
            want = t0 * lod_target[lod]
            if t > want * 1.15:
                o = _localize(mi._decimate(o, max(0.05, want / t), o.name, coll))
                for s in o.material_slots:
                    pass
            objs.append(o)
        rep[nm] = [pk.tri_count(o) for o in objs] + [tuple(round(d, 2) for d in objs[0].dimensions)]
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    for k, v in rep.items():
        print(f"{k:<28} {v}")
    return rep


# =================================================================================================================
# disposizione (riuso + nuovi istanziati)
# =================================================================================================================
CARS_COL = ["SM_Morin_Auto_A_Col_v2_Bianco", "SM_Morin_Auto_B_Col_v2_Argento", "SM_Morin_Auto_C_Col_v2_Nero",
            "SM_Morin_Auto_A_Col_v2_Rosso", "SM_Morin_Auto_C_Col_v2_BiancoPerla", "SM_Morin_Auto_B_Col_v2_GrigioScuro",
            "SM_Morin_Auto_A_Col_v2_Azzurro", "SM_Morin_Auto_C_Col_v2_BluScuro", "SM_Morin_Auto_B_Col_v2_Arancio"]


def _pontile_frame(key):
    r, t = Vector(PONTILI[key][0]), Vector(PONTILI[key][1])
    d = (t - r).normalized()
    root = r + d * 1.0
    return root, d, Vector((d.y, -d.x))      # radice, direzione, normale verso est


def layout(seed=20261120):
    """Righe (asset, nome, X, Y, Z, rotZ_deg) in coordinate Blender."""
    rng = np.random.default_rng(seed)
    rows = []
    for nm in ASSETS_SCENE:
        rows.append((nm, nm.replace("SM_", ""), 0.0, 0.0, 0.0, 0.0))
    # ciglio: moduli banchina v2 ruotati (+Y locale verso terra), ai lati della spalla
    ca = math.radians(COAST_ROT)
    dx = Vector((math.cos(ca), math.sin(ca)))          # +X locale (verso ovest)
    k = 0
    for xs in (11.4, 7.4, 3.4, SPALLA_X[0], SPALLA_X[0] - 4, SPALLA_X[0] - 8, SPALLA_X[0] - 12):
        rows.append(("SM_Banchina_Mod4m_v2", f"Mod_{k:02d}", xs, coast(xs), 0.0, COAST_ROT))
        k += 1
    for j, xb in enumerate((-15.2, 5.4)):
        inland = Vector((-dx.y, dx.x))
        p = Vector((xb, coast(xb))) + inland * 0.38
        rows.append(("SM_Banchina_Bitta_v2", f"Bitta_{j:02d}", p.x, p.y, -0.012, COAST_ROT))
    # arredi sul marciapiede del multipiano [S]
    for j, x in enumerate((-19.0, -6.0, 7.0)):
        rows.append(("SM_Morin_Lampione", f"Lampione_{j:02d}", x, -205.3, Z_SIDEW, 180.0))
    for j, x in enumerate((-10.0, 2.0)):
        rows.append(("SM_Morin_Panchina", f"Panchina_{j:02d}", x, -207.0, Z_SIDEW, 180.0))
    for j, x in enumerate((-12.4, 4.4)):
        rows.append(("SM_Morin_Cestino", f"Cestino_{j:02d}", x, -205.4, Z_SIDEW, 0.0))
    # palme sui prati a est (foto ponte1.png: palme vicino all'edificio basso bianco) [S]
    for j, (x, y) in enumerate(((95.0, -193.0), (101.0, -199.5), (108.5, -195.5))):
        rows.append(("SM_Morin_PalmaA", f"Palma_{j:02d}", x, y, 0.05, float(rng.uniform(0, 360))))
    # auto negli stalli (con collisione nel box giocabile, senza fuori)
    kc = 0
    for (row, rz) in ((ROW1, -90.0), (ROW2, 90.0)):
        yc = (row[0] + row[1]) / 2
        for xc in np.arange(-58.75, 45.0, STALL_W):
            if WALK_X[0] - 1.0 < xc < WALK_X[1] + 1.0 or abs(xc - 47.0) < 3.0:
                continue
            if rng.uniform() > 0.62:
                continue
            inside = BOX[0] + 1.3 < xc < BOX[1] - 1.3
            a = CARS_COL[int(rng.integers(len(CARS_COL)))]
            if not inside:
                a = a.replace("_Col_v2", "_v2")
            rows.append((a, f"Auto_{kc:03d}", float(xc + rng.uniform(-0.1, 0.1)), float(yc + rng.uniform(-0.15, 0.15)),
                         0.0, rz + float(rng.uniform(-2, 2))))
            kc += 1
    # pontili + yacht da fondale ormeggiati di poppa
    kp = ky = 0
    for key in PONTILI:
        root, d, ne = _pontile_frame(key)
        rz = math.degrees(math.atan2(d.y, d.x))
        rows.append(("SM_Mirabello_Pontile", f"Pontile_{key}", root.x, root.y, PONT_Z, rz))
        kp += 1
        sides = {"085": (1,), "086": (1,), "087": (-1, 1), "088": (1,), "089": (1,)}[key]
        for s in sides:
            for sb in np.arange(8.0, PONT_L - 1.0, 5.0):
                if rng.uniform() > 0.72:
                    continue
                a = "SM_Mirabello_YachtA" if rng.uniform() < 0.55 else "SM_Mirabello_YachtB"
                Lb = 12.5 if a.endswith("A") else 11.0
                c = root + d * float(sb) + ne * s * (PONT_W / 2 + 1.0 + Lb / 2 + (0.7 if a.endswith("A") else 0.0))
                nn = ne * s
                rows.append((a, f"Yacht_{ky:03d}", c.x, c.y, Z_ACQUA, math.degrees(math.atan2(nn.y, nn.x))
                             + float(rng.uniform(-1.5, 1.5))))
                ky += 1
    rows.append(("SM_Mirabello_Fanale", "Fanale", FANALE[0], FANALE[1], 0.02, 0.0))
    return rows


def _yaw(rz):
    y = -rz
    while y <= -180.0:
        y += 360.0
    while y > 180.0:
        y -= 360.0
    return y


def write_csv(path="exports/mirabello/mirabello_posizioni_v1.csv"):
    def f(v, nd=2):
        s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
        return "0.0" if s in ("0", "-0", "") else (s if "." in s else s + ".0")
    os.makedirs(os.path.dirname(f"{PROJ}/{path}"), exist_ok=True)
    lines = ["asset,nome,x,y,z,yaw,pitch,roll"]
    for a, n, x, y, z, rz in layout():
        lines.append(f"{a},{n},{f(x * 100)},{f(-y * 100)},{f(z * 100)},{f(_yaw(rz), 4)},0.0,0.0")
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(lines) - 1


def build_context():
    """Istanze (linked duplicates) nelle posizioni del CSV, per i render. Le mesh di scena restano dove sono."""
    coll = pk._coll(CTX)
    for a, n, x, y, z, rz in layout():
        if a in ASSETS_SCENE:
            continue
        src = bpy.data.objects.get(a)
        if src is None:
            print("manca", a)
            continue
        on = f"MIR_{n}"
        o = bpy.data.objects.get(on)
        if o is None:
            o = bpy.data.objects.new(on, src.data)
            coll.objects.link(o)
        o.data = src.data
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(rz))
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
        for nm in ASSETS_SCENE:
            reps.append(morin_export.export_fbx([bpy.data.objects[nm]], f"{EXPDIR}/{nm}.fbx", mode="scene",
                                                overwrite=overwrite, include_ucx=True, verbose=False))
        for nm in ASSETS_LOD:
            for lod in range(3):
                on = nm + mi._sfx(lod)
                reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                                    overwrite=overwrite, include_ucx=(lod == 0),
                                                    bake_rotation=(lod > 0), verbose=False))
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps


# =================================================================================================================
# camere e catture
# =================================================================================================================
CAMS = {
    # nome: (posizione, punto guardato, FOV orizzontale)
    "CAM_Mir_A": ((-5.0, -150.0, 3.33 + 1.65), (-6.0, -205.0, 1.0), 72.0),     # dal calpestio del ponte verso l'arrivo
    "CAM_Mir_B": ((-16.0, -202.0, 1.75), (-7.0, -150.0, 7.0), 78.0),             # dalla testata verso il ponte
    "CAM_Mir_C": ((-40.0, -232.0, 18.0), (-4.0, -185.0, 0.0), 70.0),            # dall'alto (verifica pianta)
}


def cameras():
    coll = pk._coll("MIRABELLO_Camere")
    for name, (pos, tgt, fov) in CAMS.items():
        cam = bpy.data.objects.get(name)
        if cam is None:
            cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
            coll.objects.link(cam)
        cam.location = pos
        cam.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        cam.data.sensor_fit = "HORIZONTAL"
        cam.data.angle = math.radians(fov)
        cam.data.clip_start = 0.1
        cam.data.clip_end = 6000
        cam["res"] = (1600, 900)
    return list(CAMS)


def render(cam, path, width=1600):
    s = bpy.context.scene
    s.camera = bpy.data.objects[cam]
    rx, ry = bpy.data.objects[cam]["res"]
    s.render.resolution_x = width
    s.render.resolution_y = int(round(width * ry / rx))
    s.render.resolution_percentage = 100
    s.render.filepath = path
    s.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    return path
