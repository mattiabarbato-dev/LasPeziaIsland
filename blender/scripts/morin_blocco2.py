"""morin_blocco2.py — Blocco 2: tratto centrale della Passeggiata Morin (X 251 -> 560), v1 2026-11-20.

Scheda: ref/blocco2.md (geo-scout 2026-11-20), ref/sezione.md, ref/palme.md, ref/banchina.md; OSM ref/osm/morin_blocchi23.osm
(© OpenStreetMap contributors, ODbL). Foto: ref/foto/arredi/cannone_*, scultura_*, giardini*, ref/foto/pavimentazione/scritta_*,
ref/foto/vista/banchina_vista_montagne_*, chiosco_2_*, incrocio_molo_italia_*, info_point_*.

Esegui dentro blender/arte_blocco2.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_blocco2 as b2; importlib.reload(b2)
    b2.link_kit()             # mesh e materiali dei kit esistenti, collegati (link) dai .blend sorgente: niente duplicati
    b2.make_textures()        # corten REDAMARE 1024 (da Poly Haven rusty_metal_02, CC0)
    b2.build_materials()
    b2.build_all()            # asset nuovi LOD0/1/2 + UCX (collezione B2_Kit)
    rows = b2.layout()        # posizioni del kit riusato e degli asset nuovi (coordinate Blender)
    b2.write_csvs(rows)       # exports/blocco2/*.csv in coordinate UE
    b2.build_context(rows)    # istanze per i render (B2_Contesto)
    b2.export_all()

Convenzioni come il Blocco 1: X lungo la passeggiata, Y verso la citta', Z su; UE = (X*100, -Y*100, Z*100), yaw UE = -rotZ.
"""
import math
import os
import xml.etree.ElementTree as ET

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk

PROJ = pk.PROJ
OSM = PROJ + "/ref/osm/morin_blocchi23.osm"
KIT = "B2_Kit"
CTX = "B2_Contesto"
EXPDIR = "//../exports/blocco2"
TEXDIR = PROJ + "/blender/textures/blocco2"
ZF = pk.ZF                       # 0,15: quota della fascia palme e dei cubetti

# =============================================================================================================
# OSM -> coordinate di progetto (stessa proiezione di ref/area.md; WGS84 locale: faro 678,95/-327,47, scheda 678,6/-327,1)
# =============================================================================================================
LAT0, LON0 = 44.1016154, 9.8252769
_PH = math.radians(LAT0)
KX = 111412.84 * math.cos(_PH) - 93.5 * math.cos(3 * _PH)
KY = 111132.954 - 559.822 * math.cos(2 * _PH) + 1.175 * math.cos(4 * _PH)
_S, _C = math.sin(math.radians(41.3)), math.cos(math.radians(41.3))
_OSM = None


def _osm():
    global _OSM
    if _OSM is None:
        r = ET.parse(OSM).getroot()
        nodes = {}
        for n in r.findall("node"):
            E = (float(n.get("lon")) - LON0) * KX
            N = (float(n.get("lat")) - LAT0) * KY
            nodes[n.get("id")] = (E * _S + N * _C, -E * _C + N * _S)
        ways = {}
        tags = {}
        for w in r.findall("way"):
            ways[w.get("id")] = [nodes[nd.get("ref")] for nd in w.findall("nd")]
            tags[w.get("id")] = {t.get("k"): t.get("v") for t in w.findall("tag")}
        _OSM = (nodes, ways, tags)
    return _OSM


def osm_way(i):
    return _osm()[1][str(i)]


def osm_node(i):
    return _osm()[0][str(i)]


# =============================================================================================================
# kit esistenti: collegati (link) dai .blend sorgente, solo per i render; in UEFN sono gia' importati
# =============================================================================================================
BL = PROJ + "/blender/"
KIT_SRC = {
    "arte_banchina_v2": ["SM_Banchina_Bitta_v2", "SM_Banchina_Mod4m_v2", "SM_Banchina_Mod4m_Nicchia", "SM_Banchina_Scaletta_v2",
                         "SM_Banchina_Testata_Fine", "SM_Morin_AncoraMonumento"],
    "arte_pavimentazione": ["SM_Pav_FasciaPalme_9m", "SM_Pav_Cordolo_9m", "SM_Pav_Camminamento_4m", "SM_Pav_Aiuola",
                            "SM_Morin_Tombino", "SM_Morin_Panchina", "SM_Morin_PalmaA", "SM_Morin_Lampione",
                            "SM_Blockout_PassPav_v5_Lastra", "SM_Blockout_PassPav_v5_Aiuole"],
    "arte_giardini": ["SM_Morin_OleandroAlberello_Bianco", "SM_Morin_OleandroAlberello_Rosa", "SM_Morin_PanchinaLunga_Mod",
                      "SM_Morin_Ombrellone", "SM_Morin_TavoloSet", "SM_Morin_Fioriera", "SM_Morin_FiorieraB",
                      "SM_Morin_Sgabello", "SM_Morin_Chiosco"],
    "arte_viale": ["SM_Viale_Italia_Strada_v2", "SM_Morin_Prato_Giardini", "SM_Morin_Aiuola_Bosso",
                   "SM_Fondale_Palazzo_A", "SM_Fondale_Palazzo_B", "SM_Fondale_Palazzo_C"],
    "arte_incrocio": ["SM_Viale_Spartitraffico_Fiori", "SM_Morin_Semaforo",
                      "SM_Morin_Auto_A_v2_Rosso", "SM_Morin_Auto_A_v2_Bianco", "SM_Morin_Auto_A_v2_Azzurro",
                      "SM_Morin_Auto_B_v2_GrigioScuro", "SM_Morin_Auto_B_v2_Argento", "SM_Morin_Auto_B_v2_Arancio",
                      "SM_Morin_Auto_C_v2_Nero", "SM_Morin_Auto_C_v2_BluScuro", "SM_Morin_Auto_C_v2_BiancoPerla"],
    "arte_imbarco": ["SM_Morin_Cestino", "SM_Morin_Battello"],
    "arte_molo": ["SM_Morin_PinoDomestico", "SM_Albero_LatifogliaA", "SM_Albero_LatifogliaB"],
    "arte_mirabello": ["SM_Mirabello_YachtA", "SM_Mirabello_YachtB_v2"],
    "blockout_blocco1": ["SM_Blockout_Fondale_v5_Terreno", "SM_Blockout_Fondale_v5_Edifici"],
}
KIT_MESH = {}


def link_kit():
    """Collega gli oggetti dei kit (dati mesh e materiali in sola lettura). Restituisce {asset: mesh}."""
    for f, names in KIT_SRC.items():
        with bpy.data.libraries.load(BL + f + ".blend", link=True) as (src, dst):
            dst.objects = [n for n in names if n in src.objects]
        for o in dst.objects:
            if o is not None:
                KIT_MESH[o.name] = o.data
    missing = [n for v in KIT_SRC.values() for n in v if n not in KIT_MESH]
    print("kit collegati:", len(KIT_MESH), "mancanti:", missing)
    return KIT_MESH


# =============================================================================================================
# geometria di riferimento
# =============================================================================================================
def line_y(x):
    """Retta dei moduli banchina (Blender): stessa del Blocco 1, Y_UE = -8036,16 + 0,0021664*X_UE."""
    return 80.3616 - 0.0021664 * x


ROTZ_B = -0.1241                 # rotZ Blender dei moduli banchina (yaw UE 0,1241)
X_B2 = 251.2                     # fine del modulo 57 del Blocco 1 (oggi Testata_Fine)
N_MOD = 74                       # moduli banchina 251,2 -> 547,2
X_ANG = X_B2 + 4 * N_MOD         # 547,2: inizio di SM_Banchina_Angolo_MoloItalia
CIGLIO_END = (548.8, None)       # spigolo del ciglio (OSM 548,8; 78,2); Y sulla retta dei moduli
FIANCO_END = (555.1, 41.7)       # fine dello smusso verso il fianco ovest del Molo Italia (OSM coastline 137121074)
NICCHIE_X = (300.0, 350.0, 400.0, 450.0, 500.0, 540.0)   # scalette ogni ~50 m [S] (scheda §4.2)
N_CAMM = 77                      # camminamento 251,2 -> 559,2
X_FASCIA = 252.75                # fine del modulo fascia/cordolo 26 del Blocco 1
N_FASCIA = 34                    # 252,75 -> 558,75 (l'ultimo modulo fascia e' la variante _Fine)
PALME_X = [255.0 + 9.0 * k for k in range(34)]        # griglia v3 del Blocco 1 (12 + 9k): 255 ... 552
FILARI_Y = (92.6, 99.6)
PANCH_X = [250.5 + 18.0 * k for k in range(17)]       # 16,5 + 18k (una ogni 2 palme): 250,5 ... 538,5
LAMP_X = [268.8 + 36.0 * k for k in range(8)]         # 16,8 + 36k (uno ogni 4 palme): 268,8 ... 520,8
CANNONI = [(249.08, 82.05), (259.33, 82.31)]           # OSM 5913835513 / 5913835504
REDAMARE_C = (254.2, 82.55)      # centro della piastra, fra i due cannoni (articolo 2022 + foto) [S]
ANCORA2 = (279.99, 82.57)        # OSM 5913835508: centro dell'ingombro
CHIOSCO_C = (550.0, 107.5)       # OSM way 352041625 (centroide), Ø ~6,6 m
SCRITTA_X = (553.6, 556.9)       # righe "PASSEGGIATA" e "MORIN" (asse delle lettere) [S] dalla foto
PRATO_X1 = 526.6                 # fine del prato OSM 850396610
Y_PRATO0, Y_VIALE = 101.9, 120.85
VIALETTO_Y = (115.45, 118.0)     # footway OSM 850396607 (asse 116,6-116,7), larghezza 2,55 m [S]
VIALETTO_X = (300.0, 558.75)          # OSM fino a 556,6; prolungato fino al piazzale
STRADA_X = [326.0 + 19.0 * k for k in range(13)]     # moduli SM_Viale_Italia_Strada_v2 326 -> 573
ISOLA_X = (396.0, 483.0)         # isola centrale fra le due carreggiate (OSM)
SEMAFORI_X = (506.4, 520.0)      # attraversamenti con semaforo (OSM)
CORSIE = {"A1": (123.80, 0.0), "A2": (128.60, 0.0), "B1": (133.75, 180.0), "B2": (136.85, 180.0)}
AUTO_V2 = ["SM_Morin_Auto_A_v2_Rosso", "SM_Morin_Auto_A_v2_Bianco", "SM_Morin_Auto_A_v2_Azzurro",
           "SM_Morin_Auto_B_v2_GrigioScuro", "SM_Morin_Auto_B_v2_Argento", "SM_Morin_Auto_B_v2_Arancio",
           "SM_Morin_Auto_C_v2_Nero", "SM_Morin_Auto_C_v2_BluScuro", "SM_Morin_Auto_C_v2_BiancoPerla"]
# cortina di Viale Mazzini (fronte Y 206-208 [V] OSM, altezze [S]); ultima del Blocco 1: Palazzo_06 B a X 357,5
PALAZZI_B2 = [("SM_Fondale_Palazzo_A", 392.6, 207.0), ("SM_Fondale_Palazzo_B", 416.0, 207.0),
              ("SM_Fondale_Palazzo_C", 439.6, 207.0), ("SM_Fondale_Palazzo_B", 483.5, 207.0),
              ("SM_Fondale_Palazzo_A", 538.6, 207.0), ("SM_Fondale_Palazzo_C", 558.0, 208.0)]
# vialetti diagonali nel prato (OSM 183535305, 850396591, 850396598, 850396596): solo il tratto con Y >= 101,9
VIALETTI_DIAG = ["183535305", "850396591", "850396598", "850396596"]
VIALETTO_W = 2.5                 # [S]
ATTRAV_X = (300.7, 506.4, 520.0) # strisce su Viale Italia: varchi nel filare di oleandri


def panchina_lunga_gaps():
    """X dove i vialetti diagonali attraversano la panchina lunga (Y 101,7)."""
    xs = []
    for wid in VIALETTI_DIAG:
        p = osm_way(wid)
        for a, b in zip(p[:-1], p[1:]):
            if (a[1] - 101.7) * (b[1] - 101.7) < 0:
                t = (101.7 - a[1]) / (b[1] - a[1])
                xs.append(a[0] + t * (b[0] - a[0]))
    return sorted(xs)


# =============================================================================================================
# texture e materiali nuovi: solo il corten di REDAMARE (il resto e' riuso dei materiali collegati)
# =============================================================================================================
SRC_CORTEN = PROJ + "/blender/textures/src/rusty_metal_02/rusty_metal_02_"
MAT_CORTEN = "M_Morin_Corten"
MAT_LEGNO_CAN = "M_Morin_Cannone_Legno"          # = texture T_Morin_Imbarco_Legno (riuso) tinta scura: in UEFN una MI
IMB_TEX = PROJ + "/blender/textures/imbarco/T_Morin_Imbarco_Legno"


def make_textures():
    """T_Morin_Corten_D/N/ORM 1024 da rusty_metal_02 (Poly Haven, CC0): la maschera della ruggine diventa la variazione
    del corten (bruno scuro -> arancio), normal DirectX e AO dal set originale, rugosita' alta, metallo basso."""
    import morin_texphoto as tp
    os.makedirs(TEXDIR, exist_ok=True)

    def half(a):
        return 0.25 * (a[0::2, 0::2] + a[1::2, 0::2] + a[0::2, 1::2] + a[1::2, 1::2])
    d = half(tp.load(SRC_CORTEN + "diff_2k.jpg")[..., :3])
    d = d ** 2.2                                                  # load() legge in Non-Color: torna lineare
    sat = d.max(axis=2) - d.min(axis=2)
    m = np.clip(sat / max(1e-4, np.percentile(sat, 97)), 0, 1)     # 0 = vernice, 1 = ruggine
    m = tp.blur(m, 1.5)
    lumi = d.mean(axis=2)
    base = np.array([0.135, 0.050, 0.020])                        # bruno corten (lineare) [foto scultura_*]
    rust = np.array([0.300, 0.105, 0.035])                        # arancio della patina
    noise = (lumi - lumi.mean()) / (lumi.std() + 1e-6)
    rgb = base[None, None] * (1 - m[..., None]) + rust[None, None] * m[..., None]
    rgb *= (1.0 + 0.10 * noise[..., None])
    rgb = np.clip(rgb, 0, 1) ** (1 / 2.2)
    n = half(tp.load(SRC_CORTEN + "nor_dx_2k.jpg")[..., :3])
    ao = half(tp.load(SRC_CORTEN + "ao_2k.jpg")[..., 0])
    rough = np.clip(0.72 + 0.18 * m, 0, 1)
    metal = np.full_like(rough, 0.05)
    out = {}
    for k, a in (("D", rgb), ("N", n), ("ORM", np.dstack([ao, rough, metal]))):
        p = f"{TEXDIR}/T_Morin_Corten_{k}.png"
        tp.save(a, p)
        out[k] = p
    print("texture corten:", out)
    return out


def build_materials():
    pk._pbr_material(MAT_LEGNO_CAN, f"{IMB_TEX}_D.png", f"{IMB_TEX}_N.png", f"{IMB_TEX}_ORM.png", tint=(0.30, 0.22, 0.16))
    pk._pbr_material(MAT_CORTEN, f"{TEXDIR}/T_Morin_Corten_D.png", f"{TEXDIR}/T_Morin_Corten_N.png",
                     f"{TEXDIR}/T_Morin_Corten_ORM.png")
    if "M_Morin_Imbarco_Legno" not in bpy.data.materials:
        with bpy.data.libraries.load(BL + "arte_imbarco.blend", link=True) as (src, dst):
            dst.materials = ["M_Morin_Imbarco_Legno"]
    for m in ("M_Banchina_Ghisa", "M_Banchina_Blocchi", "M_Banchina_Paramento", "M_Pav_Lastre", "M_Pav_Cubetti",
              "M_Pav_Fascia", "M_Morin_Prato", "M_Blockout_Pietra", "M_Blockout_Verde", "M_Morin_Imbarco_Legno"):
        assert m in bpy.data.materials, m
    return True


# =============================================================================================================
# utilita'
# =============================================================================================================
def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


def _hide_kit(coll):
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide


def _prism(bm, poly, z0, z1, mi=0, top=True, bot=False, sides=True):
    """Prisma verticale da un poligono 2D antiorario."""
    a = [bm.verts.new((x, y, z0)) for x, y in poly]
    b = [bm.verts.new((x, y, z1)) for x, y in poly]
    if sides:
        for i in range(len(poly)):
            j = (i + 1) % len(poly)
            f = bm.faces.new([a[i], a[j], b[j], b[i]]); f.material_index = mi
    if top:
        f = bm.faces.new(b); f.material_index = mi
    if bot:
        f = bm.faces.new(list(reversed(a))); f.material_index = mi


def _side_prism(bm, poly_yz, x0, x1, mi=0):
    """Prisma lungo X da un poligono nel piano YZ (fianco dell'affusto)."""
    a = [bm.verts.new((x0, y, z)) for y, z in poly_yz]
    b = [bm.verts.new((x1, y, z)) for y, z in poly_yz]
    for i in range(len(poly_yz)):
        j = (i + 1) % len(poly_yz)
        f = bm.faces.new([a[i], a[j], b[j], b[i]]); f.material_index = mi
    f = bm.faces.new(list(reversed(a))); f.material_index = mi
    f = bm.faces.new(b); f.material_index = mi


def _cyl_x(bm, cx, cy, cz, r, w, n, mi=0):
    """Cilindro con asse X (ruote, orecchioni)."""
    M = Matrix.Translation((cx, cy, cz)) @ Matrix.Rotation(math.radians(90), 4, "Y") @ Matrix.Translation((0, 0, -w / 2))
    pk._lathe(bm, [(0.0, 0.0), (r, 0.0), (r, w), (0.0, w)], n, M, mi, cap_top=False)


# =============================================================================================================
# SM_Morin_Cannone: cannone ad avancarica su affusto navale a 4 ruote (foto cannone_*, scultura_*). Misure [S].
# Origine a terra al centro dell'affusto; la bocca punta verso -Y (il mare) con rotZ 0.
# =============================================================================================================
CAN_AX_Z = 0.86                 # quota dell'asse della canna
CAN_Y0 = 0.95                   # culatta (lato citta')
CAN_PROF = [(0.0, -0.17), (0.055, -0.165), (0.07, -0.13), (0.045, -0.09), (0.05, -0.05), (0.20, -0.04), (0.235, 0.0),
            (0.235, 0.10), (0.25, 0.12), (0.25, 0.18), (0.225, 0.20), (0.215, 0.80), (0.23, 0.82), (0.23, 0.88),
            (0.205, 0.90), (0.175, 1.85), (0.19, 1.87), (0.19, 1.91), (0.165, 1.94), (0.165, 2.12), (0.185, 2.22),
            (0.185, 2.38), (0.165, 2.40), (0.075, 2.40), (0.075, 2.25), (0.0, 2.25)]   # (r, ascissa dalla culatta)


def build_cannone(coll, lod=0, name="SM_Morin_Cannone"):
    bm = bmesh.new()
    n = (16, 10, 6)[lod]
    prof = CAN_PROF if lod < 2 else [p for i, p in enumerate(CAN_PROF) if i in (0, 5, 6, 10, 15, 21, 22, 23, 24, 25)]
    # canna: tornio attorno a Z, poi Z -> -Y (Rx +90), leggera alzata di 2 gradi
    M = (Matrix.Translation((0, CAN_Y0, CAN_AX_Z)) @ Matrix.Rotation(math.radians(2.0), 4, "X")
         @ Matrix.Rotation(math.radians(90), 4, "X"))
    pk._lathe(bm, prof, n, M, 0, cap_top=False)
    if lod < 2:   # orecchioni sui fianchi
        t = CAN_Y0 - 0.86
        for s in (-1, 1):
            _cyl_x(bm, s * 0.29, t, CAN_AX_Z, 0.065, 0.12, max(6, n // 2), 0)
    # affusto: due fianchi a gradini (legno), calastrello frontale, letto, assali (legno), ruote piene (ghisa)
    steps = [(-0.55, 0.16), (0.95, 0.16), (0.95, 0.42), (0.62, 0.42), (0.62, 0.56), (0.30, 0.56), (0.30, 0.70),
             (-0.02, 0.70), (-0.02, 0.80), (-0.40, 0.80), (-0.55, 0.62)]
    if lod == 2:
        steps = [(-0.55, 0.16), (0.95, 0.16), (0.95, 0.42), (-0.02, 0.80), (-0.40, 0.80), (-0.55, 0.62)]
    for s in (-1, 1):
        _side_prism(bm, steps, s * 0.33 - 0.06, s * 0.33 + 0.06, 1)
    pk._box(bm, -0.27, 0.27, -0.55, -0.42, 0.20, 0.62, 1)              # calastrello
    pk._box(bm, -0.27, 0.27, -0.45, 0.85, 0.18, 0.26, 1)               # letto
    for yc, r in ((-0.33, 0.21), (0.72, 0.18)):
        pk._box(bm, -0.50, 0.50, yc - 0.08, yc + 0.08, r - 0.07, r + 0.07, 1)   # assale
        for s in (-1, 1):
            _cyl_x(bm, s * 0.46, yc, r, r, 0.10, (14, 10, 6)[lod], 0)
    if lod < 2:   # cappe degli orecchioni (ghisa)
        for s in (-1, 1):
            pk._box(bm, s * 0.33 - 0.065, s * 0.33 + 0.065, CAN_Y0 - 0.95, CAN_Y0 - 0.77, 0.80, 0.86, 0)
    pk._recalc(bm)
    o = pk._finish(name + _sfx(lod), bm, ["M_Banchina_Ghisa", MAT_LEGNO_CAN], coll, uv="box",
                   smooth_angle=40.0)
    if lod == 0:
        pk._ucx(name, [(-0.52, 0.52, -0.58, 0.97, 0.0, 0.82),
                       (-0.20, 0.20, -1.50, -0.58, 0.68, 1.06)], coll)
    return o


# =============================================================================================================
# SM_Morin_Redamare: lettere in corten su piastra (solo la forma: opera di Sabrina D'Alessandro, 2022; decisioni.md).
# Origine a terra al centro della piastra; con rotZ 0 la scritta si legge da +Y (dal camminamento verso il mare).
# Font: quello incorporato in Blender (licenza libera), ingrossato con offset; proporzioni dalla foto scultura_*.
# =============================================================================================================
RED_W, RED_H, RED_D = 7.5, 1.30, 0.35     # [S] scheda §4.1
RED_PLATE = (8.0, 0.60, 0.05)


def _text_mesh(body, size, extrude, offset, resol=2, space=1.0, fill=True):
    cu = bpy.data.curves.new("_tmp_txt", "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.offset = offset
    cu.resolution_u = resol
    cu.space_character = space
    cu.align_x = "CENTER"
    ob = bpy.data.objects.new("_tmp_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    return me


def build_redamare(coll, lod=0, name="SM_Morin_Redamare"):
    me = _text_mesh("REDAMARE", 1.0, 0.5, 0.06, resol=(3, 2, 1)[lod], space=0.90)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    sx = RED_W / (max(xs) - min(xs)); sy = RED_H / (max(ys) - min(ys)); sz = RED_D / (max(zs) - min(zs))
    cx, cy0, cz = (max(xs) + min(xs)) / 2, min(ys), (max(zs) + min(zs)) / 2
    W, D, H = RED_PLATE
    for v in bm.verts:
        x, y, z = (v.co.x - cx) * sx, (v.co.y - cy0) * sy, (v.co.z - cz) * sz
        # testo nel piano XY con il fronte su +Z -> in piedi, fronte verso +Y, lettura verso -X
        v.co = Vector((-x, z, y + H))
    for f in bm.faces:
        f.material_index = 0
    pk._box(bm, -W / 2, W / 2, -D / 2, D / 2, 0.0, H, 0)
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="BEAUTY")
    pk._recalc(bm)
    o = pk._finish(name + _sfx(lod), bm, [MAT_CORTEN], coll, uv="box", smooth_angle=30.0)
    if lod == 0:
        pk._ucx(name, [(-W / 2, W / 2, -D / 2, D / 2, 0.0, H),
                       (-RED_W / 2, RED_W / 2, -RED_D / 2, RED_D / 2, H, H + RED_H)], coll)
    return o


# =============================================================================================================
# pavimentazione: camminamento allargato (segue il ciglio che deriva di 0,65 m) e ultimo modulo della fascia
# =============================================================================================================
def build_camminamento_b2(coll, name="SM_Pav_Camminamento_4m_B2"):
    """Come SM_Pav_Camminamento_4m ma fino a 9,40 m dal ciglio: nel Blocco 2 la retta del ciglio scende verso il mare
    (Y 79,82 -> 79,15) mentre il cordolo resta a Y 88,45; con 8,70 m resterebbe una fessura fino a 0,6 m."""
    return pk.build_camminamento(coll, name=name, y0=0.54, y1=9.40)


def build_fascia_fine(coll, name="SM_Pav_FasciaPalme_Fine"):
    """Ultimo modulo della fascia palme (X 549,75-558,75): strisce longitudinali solo fino all'aiuola dell'ultima palma, una
    striscia trasversale a X 554,05 e poi cubetti liberi per la scritta (foto scritta_*)."""
    L = 9.0
    ys = [pk.K1, pk.Y_S1[0], pk.Y_S1[1], pk.Y_S2[0], pk.Y_S2[1], pk.Y_END]
    bm = bmesh.new()
    xs = [0.0, 4.30, 4.30 + pk.STRIP, L]          # strisce lungo le aiuole dell'ultima palma, poi una trasversale [F] scritta_*
    grid = [[bm.verts.new((x, y, ZF)) for x in xs] for y in ys]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            f = bm.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
            f.material_index = 1 if (i == 1 or (i == 0 and j in (1, 3))) else 0
    pk._box(bm, 0, L, pk.K1, pk.Y_END, pk.ZB, ZF, 0, faces=("xn", "xp", "yp"))
    o = pk._finish(name, bm, ["M_Pav_Cubetti", "M_Pav_Fascia"], coll)
    pk._ucx(name, [(0, L, pk.K1, pk.Y_END, pk.ZB, ZF)], coll)
    return o


# =============================================================================================================
# Giardini a Mare B2: prato (pezzo unico in coordinate di progetto, origine 0,0,0) e vialetti
# =============================================================================================================
Z_PRATO = 0.08            # come SM_Morin_Prato_Giardini
Z_VIALETTO = 0.10


def _grid_face(bm, layer, x0, x1, y0, y1, z, T, step=12.0):
    nx = max(1, int(math.ceil((x1 - x0) / step)))
    xs = np.linspace(x0, x1, nx + 1)
    for i in range(nx):
        pts = [(xs[i], y0, z), (xs[i + 1], y0, z), (xs[i + 1], y1, z), (xs[i], y1, z)]
        vs = [bm.verts.new(p) for p in pts]
        f = bm.faces.new(vs)
        for lp in f.loops:
            lp[layer].uv = (lp.vert.co.x / T, lp.vert.co.y / T)


def _skirt(bm, layer, a, b, z0, z1):
    vs = [bm.verts.new((a[0], a[1], z0)), bm.verts.new((b[0], b[1], z0)), bm.verts.new((b[0], b[1], z1)),
          bm.verts.new((a[0], a[1], z1))]
    f = bm.faces.new(vs)
    for lp, uv in zip(f.loops, [(0, 0), (1, 0), (1, 0.03), (0, 0.03)]):
        lp[layer].uv = uv


PRATO_TRI = [(526.6, Y_PRATO0), (540.6, Y_PRATO0), (526.6, VIALETTO_Y[0])]   # triangolo verde OSM 850396608 [V]


def build_prato_b2(coll, name="SM_Morin_Prato_Giardini_B2"):
    """Prato dei Giardini a Mare X 250-540,6. Fino a X 300 arriva al cordolo del viale come la v1; da X 300 si ferma al
    vialetto (Y 115,45) e riprende dopo (striscia degli oleandri Y 118-120,85, fino a X 556,6). I vialetti diagonali
    sono mesh a parte 2 cm sopra il prato (niente fori nel prato: niente fessure)."""
    bm = bmesh.new()
    layer = bm.loops.layers.uv.verify()
    z, zb, T = Z_PRATO, -0.05, 4.0
    rects = [(250.0, 300.0, Y_PRATO0, Y_VIALE), (300.0, PRATO_X1, Y_PRATO0, VIALETTO_Y[0]),
             (300.0, VIALETTO_X[1], VIALETTO_Y[1], Y_VIALE)]
    for x0, x1, y0, y1 in rects:
        _grid_face(bm, layer, x0, x1, y0, y1, z, T)
    tri = [bm.verts.new((x, y, z)) for x, y in PRATO_TRI]
    f = bm.faces.new(tri)
    for lp in f.loops:
        lp[layer].uv = (lp.vert.co.x / T, lp.vert.co.y / T)
    # bordi verticali
    for a, b in (((250.0, Y_PRATO0), (PRATO_X1, Y_PRATO0)), ((PRATO_TRI[1]), (PRATO_TRI[2])),
                 ((300.0, VIALETTO_Y[0]), (PRATO_X1, VIALETTO_Y[0])), ((300.0, VIALETTO_Y[1]), (VIALETTO_X[1], VIALETTO_Y[1])),
                 ((VIALETTO_X[1], VIALETTO_Y[1]), (VIALETTO_X[1], Y_VIALE)), ((PRATO_X1, Y_PRATO0), PRATO_TRI[1])):
        _skirt(bm, layer, a, b, zb, z)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    pk._recalc(bm)
    for f in bm.faces:
        if abs(f.normal.z) > 0.5 and f.normal.z < 0:
            f.normal_flip()
    o = pk._finish(name, bm, ["M_Morin_Prato"], coll, uv=None)
    # collisione solo fino alla barriera lato citta' (Y 118), come la v1
    pk._ucx(name, [(250.0, 300.0, Y_PRATO0, 118.0, -0.30, z), (300.0, PRATO_X1, Y_PRATO0, VIALETTO_Y[0], -0.30, z)], coll)
    pk._ucx_hull(name, 2, [(x, y, zz) for x, y in PRATO_TRI for zz in (-0.30, z)], coll)
    return o


def _clip_poly_y(p, y0, y1):
    """Tratti della polilinea con y0 <= Y <= y1 (lista di polilinee)."""
    out, cur = [], []
    for a, b in zip(p[:-1], p[1:]):
        t0, t1 = 0.0, 1.0
        dy = b[1] - a[1]
        if abs(dy) < 1e-9:
            if not (y0 <= a[1] <= y1):
                t0, t1 = 1.0, 0.0
        else:
            ta, tb = (y0 - a[1]) / dy, (y1 - a[1]) / dy
            t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
        if t0 >= t1 - 1e-9:
            if cur:
                out.append(cur); cur = []
            continue
        s = (a[0] + t0 * (b[0] - a[0]), a[1] + t0 * dy)
        e = (a[0] + t1 * (b[0] - a[0]), a[1] + t1 * dy)
        if cur and math.hypot(cur[-1][0] - s[0], cur[-1][1] - s[1]) < 1e-6:
            cur.append(e)
        else:
            if cur:
                out.append(cur)
            cur = [s, e]
    if cur:
        out.append(cur)
    return out


def _ribbon(poly, w):
    """Contorno sinistro/destro di una polilinea con giunti a mitra."""
    P = [Vector(p) for p in poly]
    L, R = [], []
    for i, p in enumerate(P):
        ds = []
        if i > 0:
            ds.append((p - P[i - 1]).normalized())
        if i < len(P) - 1:
            ds.append((P[i + 1] - p).normalized())
        nrm = [Vector((-d.y, d.x)) for d in ds]
        m = (nrm[0] + nrm[-1]).normalized()
        k = 1.0 / max(0.35, m.dot(nrm[0]))
        L.append(p + m * (w / 2) * k)
        R.append(p - m * (w / 2) * k)
    return L, R


def vialetti_polys():
    polys = []
    for wid in VIALETTI_DIAG:
        polys += _clip_poly_y(osm_way(wid), Y_PRATO0, VIALETTO_Y[0] + 0.3)
    return polys


def build_vialetti(coll, name="SM_Pav_Vialetti_B2"):
    """Vialetto in cubetti lungo il viale (Y 115,45-118, X 300-556,6) e i diagonali nel prato (solo Y > 101,9: sulla fascia
    palme e sul camminamento il fondo e' gia' in cubetti/lastre). Quote leggermente sfalsate fra i tratti (niente z-fighting)."""
    bm = bmesh.new()
    x0, x1 = VIALETTO_X
    y0, y1 = VIALETTO_Y
    _box_faces = pk._box(bm, x0, x1, y0, y1, Z_PRATO - 0.03, Z_VIALETTO, 0, faces=("top", "yn", "yp", "xn", "xp"))
    ucx = [(x0, x1, y0, y1, -0.30, Z_VIALETTO)]
    for k, poly in enumerate(vialetti_polys()):
        z = Z_VIALETTO + 0.002 * (k + 1)
        L, R = _ribbon(poly, VIALETTO_W)
        for i in range(len(poly) - 1):
            q = [(L[i].x, L[i].y), (R[i].x, R[i].y), (R[i + 1].x, R[i + 1].y), (L[i + 1].x, L[i + 1].y)]
            vs = [bm.verts.new((x, y, z)) for x, y in q]
            f = bm.faces.new(vs)
            if f.normal.z < 0:
                f.normal_flip()
            ucx.append([(x, y, zz) for x, y in q for zz in (-0.30, z)])
    o = pk._finish(name, bm, ["M_Pav_Cubetti"], coll, uv="world")
    pk._ucx(name, [ucx[0]], coll)
    for i, pts in enumerate(ucx[1:]):
        pk._ucx_hull(name, i + 1, pts, coll)
    return o


# =============================================================================================================
# suolo del Blocco 2 (blockout, nomi nuovi): sotto il kit della passeggiata e lato citta' fino a X 580
# =============================================================================================================
Z_SOTTO = -0.15            # come Blockout_Passeggiata_Pav_v5 sotto le lastre e la fascia (UCX_02)
TERR_X = (330.0, 580.0)    # oltre X 330 il Blockout_Fondale_v5_Terreno non c'e'; da X 580 c'e' SM_Fondale_Citta_NE_01


def build_blockout_passeggiata(coll, name="SM_Blockout_Passeggiata_B2"):
    """Lastra sotto camminamento, fascia palme, prato e vialetti: X 250 -> 559,2, dal ciglio (retta dei moduli + 0,10)
    a Y 121; sommita' a Z -0,15 (tutto il kit sopra ha la sua collisione). Il raccordo verso il Molo Italia
    (X > 548,8, fuori dal kit) e' un pezzo a parte: build_blockout_raccordo()."""
    bm = bmesh.new()
    poly = [(250.0, line_y(250.0) + 0.10), (548.8, line_y(548.8) + 0.10), (559.2, line_y(559.2) + 0.50),
            (559.2, 88.45), (558.75, 88.45), (558.75, 121.0), (250.0, 121.0)]
    _prism(bm, poly, -3.0, Z_SOTTO, 0, top=True, bot=False, sides=True)
    pk._recalc(bm)
    o = pk._finish(name, bm, ["M_Blockout_Pietra"], coll, uv="world")
    hull = [(x, y, z) for x, y in (poly[0], poly[1], poly[2], (559.2, 121.0), poly[6]) for z in (-3.0, Z_SOTTO)]
    pk._ucx_hull(name, 0, hull, coll)
    return o


def build_blockout_terreno(coll, name="SM_Blockout_Fondale_B2_Terreno"):
    """Suolo lato citta' X 330-580, Y 120,85-300 a Z 0 (continua il Blockout_Fondale_v5_Terreno, che finisce a X 330)."""
    bm = bmesh.new()
    x0, x1 = TERR_X
    _prism(bm, [(x0, 120.85), (x1, 120.85), (x1, 300.0), (x0, 300.0)], -3.0, 0.0, 0, top=True, sides=True)
    pk._recalc(bm)
    o = pk._finish(name, bm, ["M_Blockout_Verde"], coll, uv="world")
    pk._ucx(name, [(x0, x1, 120.85, 300.0, -3.0, 0.0)], coll)
    return o


# =============================================================================================================
# disposizione (coordinate Blender): righe (asset, nome, X, Y, Z, rotZ, scala, gruppo CSV)
# =============================================================================================================
SEED = 20261120


def _xy_local_to_world(origin, rotz_deg, p):
    a = math.radians(rotz_deg)
    return (origin[0] + p[0] * math.cos(a) - p[1] * math.sin(a), origin[1] + p[0] * math.sin(a) + p[1] * math.cos(a))


def layout_kit():
    """Kit riusato, gia' in UEFN: solo posizioni."""
    rng = np.random.default_rng(SEED)
    R = []

    def add(g, a, n, x, y, z=0.0, rz=0.0, s=1.0):
        R.append((a, n, float(x), float(y), float(z), float(rz), float(s), g))
    # --- banchina: 74 moduli 251,2 -> 547,2 sulla retta del Blocco 1; nicchie+scalette ogni ~50 m; niente bitte
    nic = {int(round((xn - 0.8 - X_B2) / 4.0)) for xn in NICCHIE_X}
    for k in range(N_MOD):
        x = X_B2 + 4.0 * k
        a = "SM_Banchina_Mod4m_Nicchia" if k in nic else "SM_Banchina_Mod4m_v2"
        add("banchina", a, f"B2_Mod_{k:02d}", x, line_y(x), 0.0, ROTZ_B)
    for j, k in enumerate(sorted(nic)):
        x = X_B2 + 4.0 * k + 0.8
        add("banchina", "SM_Banchina_Scaletta_v2", f"B2_Scaletta_{j:02d}", x, line_y(x), 0.0, ROTZ_B)
    # --- ancora 2 (stessa mesh dell'ancora 1, ruotata di -25 gradi): centro dell'ingombro sul nodo OSM
    rz = -25.0
    off = _xy_local_to_world((0, 0), rz, (-0.6, -1.2))          # dall'origine (diamante) al centro dell'ingombro
    add("banchina", "SM_Morin_AncoraMonumento", "B2_Ancora_02", ANCORA2[0] - off[0], ANCORA2[1] - off[1], 0.0, rz)
    # --- pavimentazione
    for k in range(N_CAMM):
        x = X_B2 + 4.0 * k
        add("pav", "SM_Pav_Camminamento_4m_B2", f"B2_Camm_{k:02d}", x, line_y(x), 0.0, ROTZ_B)
    for k in range(N_FASCIA):
        x = X_FASCIA + 9.0 * k
        add("pav", "SM_Pav_Cordolo_9m", f"B2_Cordolo_{k:02d}", x, 0.0)
        add("pav", "SM_Pav_FasciaPalme_9m" if k < N_FASCIA - 1 else "SM_Pav_FasciaPalme_Fine", f"B2_Fascia_{k:02d}", x, 0.0)
    for f, y in zip((1, 2), FILARI_Y):
        for k, x in enumerate(PALME_X):
            add("pav", "SM_Pav_Aiuola", f"B2_Aiuola_F{f}_{k:02d}", x, y, ZF)
    # --- palme (yaw e scala casuali come nel Blocco 1: 0-360, 0,9-1,1)
    for f, y in zip((1, 2), FILARI_Y):
        for k, x in enumerate(PALME_X):
            add("palme", "SM_Morin_PalmaA", f"B2_Palma_F{f}_{k:02d}", x, y, ZF, rng.uniform(0, 360), rng.uniform(0.9, 1.1))
    # --- arredi della fascia
    for k, x in enumerate(PANCH_X):
        add("arredi", "SM_Morin_Panchina", f"B2_Panchina_{k:02d}", x, 92.1, ZF)
        if (k + 13) % 3 != 2:                                     # stesso ritmo dei cestini del Blocco 1
            add("arredi", "SM_Morin_Cestino", f"B2_Cestino_{k:02d}", x + 2.05, 92.1, ZF)
    for k, x in enumerate(LAMP_X):
        add("arredi", "SM_Morin_Lampione", f"B2_Lampione_{k:02d}", x, 92.85, ZF)
    tx = np.linspace(262.0, 540.0, 10) + rng.uniform(-3.0, 3.0, 10)
    for k, x in enumerate(tx):
        add("arredi", "SM_Morin_Tombino", f"B2_Tombino_{k:02d}", x, rng.uniform(95.1, 97.2), ZF, 0.0 if k % 2 == 0 else 180.0)
    # --- Giardini a Mare: oleandri (passo del Blocco 1, 5,5 m) e panchina lunga con i varchi dei vialetti
    for i, x in enumerate(np.arange(252.0, 556.1, 5.5)):
        if any(abs(x - xa) < 2.6 for xa in ATTRAV_X):
            continue
        a = ("SM_Morin_OleandroAlberello_Bianco", "SM_Morin_OleandroAlberello_Rosa")[i % 2]
        add("giardini", a, f"B2_Oleandro_{i:03d}", x, 119.5, 0.0, float((i * 47) % 360))
    gaps = panchina_lunga_gaps()
    k = 0
    for j in range(73):
        xc = 253.0 + 2.0 + 4.0 * j
        if xc + 2.0 > 540.6:
            break
        if any(abs(xc - g) < 3.4 for g in gaps):
            continue
        add("giardini", "SM_Morin_PanchinaLunga_Mod", f"B2_PanchinaLunga_{k:03d}", xc, 101.7, ZF)
        k += 1
    # --- Viale Italia: moduli strada v2, isola centrale con fiori, semafori, traffico (niente auto in sosta)
    for k, x in enumerate(STRADA_X):
        add("viale", "SM_Viale_Italia_Strada_v2", f"B2_Viale_Strada_{k:02d}", x, Y_VIALE)
    n_is = int(round((ISOLA_X[1] - ISOLA_X[0]) / 4.75))
    for k in range(n_is):
        add("viale", "SM_Viale_Spartitraffico_Fiori", f"B2_Isola_{k:02d}", ISOLA_X[0] + 4.75 * k, 131.5)
    for j, x in enumerate(SEMAFORI_X):
        add("viale", "SM_Morin_Semaforo", f"B2_Semaforo_{2 * j:02d}", x - 1.5, 120.45, ZF, 0.0)
        add("viale", "SM_Morin_Semaforo", f"B2_Semaforo_{2 * j + 1:02d}", x + 1.5, 139.10, ZF, 180.0)
    k = 0
    for lane, (y, rz) in CORSIE.items():
        x = 330.0 + rng.uniform(0, 15)
        while x < 568.0:
            if not any(abs(x - xs) < 6.0 for xs in SEMAFORI_X):
                a = AUTO_V2[int(rng.integers(0, len(AUTO_V2)))]
                add("viale", a, f"B2_Auto_{k:03d}", x, y + rng.uniform(-0.1, 0.1), 0.02, rz + rng.uniform(-1.0, 1.0))
                k += 1
            x += rng.uniform(14.0, 38.0)
    # --- fondale: cortina di Viale Mazzini e alberi dei giardini (Giardini pubblici X < 439, giardinetti oltre)
    for k, (a, x, y) in enumerate(PALAZZI_B2):
        add("fondale", a, f"B2_Palazzo_{k:02d}", x, y)
    pts = []
    zones = [(335.0, 439.0, 150.0, 200.0, 9), (458.0, 511.0, 152.0, 198.0, 4), (532.0, 578.0, 152.0, 198.0, 3)]
    names = ["SM_Morin_PinoDomestico", "SM_Albero_LatifogliaA", "SM_Albero_LatifogliaB"]
    for x0, x1, y0, y1, n in zones:
        got, tries = 0, 0
        while got < n and tries < 4000:
            tries += 1
            x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
            if any((x - p[0]) ** 2 + (y - p[1]) ** 2 < 12.5 ** 2 for p in pts):
                continue
            pts.append((x, y)); got += 1
    for i, (x, y) in enumerate(pts):
        a = names[int(rng.choice(3, p=[0.4, 0.3, 0.3]))]
        add("fondale", a, f"B2_GiardiniPubblici_{i:02d}", x, y, 0.0, rng.uniform(0, 360))
    for i, x in enumerate(np.arange(339.0, 440.0, 17.0)):
        add("fondale", "SM_Morin_PalmaA", f"B2_GiardiniPubblici_Palma_{i:02d}", x + rng.uniform(-3, 3), 147.5 + rng.uniform(0, 3),
            0.0, rng.uniform(0, 360))
    return R


def layout_nuovi():
    """Asset nuovi del Blocco 2 (posizioni)."""
    R = []

    def add(a, n, x, y, z=0.0, rz=0.0, s=1.0):
        R.append((a, n, float(x), float(y), float(z), float(rz), 1.0, "nuovi"))
    for k, (x, y) in enumerate(CANNONI):
        add("SM_Morin_Cannone", f"B2_Cannone_{k + 1:02d}", x, y, 0.0, (4.0, -6.0)[k])
    add("SM_Morin_Redamare", "B2_Redamare", REDAMARE_C[0], REDAMARE_C[1], 0.0, ROTZ_B)
    for a in ("SM_Morin_Prato_Giardini_B2", "SM_Pav_Vialetti_B2", "SM_Blockout_Passeggiata_B2", "SM_Blockout_Fondale_B2_Terreno"):
        add(a, a.replace("SM_", "B2_"), 0.0, 0.0)
    return R


def layout():
    return layout_kit() + layout_nuovi() + layout_fine()


# =============================================================================================================
# CSV (coordinate UE) e contesto per i render
# =============================================================================================================
def _ue(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0.0" if s in ("0", "-0", "") else (s if "." in s else s + ".0")


def write_csvs(rows, prefix="exports/blocco2/blocco2"):
    groups = {}
    for r in rows:
        groups.setdefault(r[7], []).append(r)
    os.makedirs(f"{PROJ}/exports/blocco2", exist_ok=True)
    out = {}
    for g, rr in groups.items():
        path = f"{PROJ}/{prefix}_{g}_v1.csv"
        lines = ["asset,nome,x,y,z,yaw,scala"]
        for a, n, x, y, z, rz, s, _ in rr:
            yaw = -rz if abs(rz) > 1e-9 else 0.0
            lines.append(f"{a},{n},{_ue(x * 100)},{_ue(-y * 100)},{_ue(z * 100)},{yaw:.4f},{s:.3f}")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
        out[g] = (path, len(rr))
    for g, (p, n) in out.items():
        print(f"{g:<10} {n:>4}  {p}")
    return out


def build_context(rows, name=CTX):
    """Istanze per i render: oggetti che usano le mesh collegate (kit) o le mesh nuove (B2_Kit)."""
    coll = pk._coll(name)
    for o in list(coll.objects):
        bpy.data.objects.remove(o)                      # solo istanze di contesto generate da questa funzione
    for a, n, x, y, z, rz, s, g in rows:
        me = KIT_MESH.get(a)
        if me is None and a in bpy.data.objects and bpy.data.objects[a].library is None:
            me = bpy.data.objects[a].data
        if me is None:
            print("manca la mesh", a)
            continue
        o = bpy.data.objects.new("CTX_" + n, me)
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(rz))
        o.scale = (s, s, s)
        coll.objects.link(o)
    print("contesto:", len(coll.objects))
    return coll


def link_contesto_b1(pav_csv="exports/pavimentazione/pav_posizioni_v3.csv",
                     palme_csv="exports/pavimentazione/palme_posizioni_v3.csv"):
    """Ultimo tratto del Blocco 1 (X >= 200) per le catture del raccordo: dalle CSV in exports/ (coordinate UE)."""
    import csv
    files = ["exports/banchina_v2/banchina_posizioni_v2.csv", pav_csv,
             "exports/giardini/giardini_posizioni_v1.csv", "exports/viale/viale_posizioni_v4.csv"]
    rows = []
    for f in files:
        with open(f"{PROJ}/{f}", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                x, y = float(r["x"]) / 100, -float(r["y"]) / 100
                if r["asset"] == "SM_Morin_Prato_Giardini":
                    pass
                elif x < 200 or r["asset"] in ("SM_Banchina_Testata", "SM_Banchina_Testata_Fine"):
                    continue
                a = {"SM_Viale_Italia_Strada": "SM_Viale_Italia_Strada_v2"}.get(r["asset"], r["asset"])
                rows.append((a, "B1_" + r["nome"], x, y, float(r["z"]) / 100, -float(r.get("yaw") or 0), 1.0, "b1"))
    with open(f"{PROJ}/{palme_csv}", encoding="utf-8") as fh:   # v5: palme_posizioni_v5.csv
        for r in csv.DictReader(fh):
            x, y = float(r["x"]) / 100, -float(r["y"]) / 100
            if x >= 200:
                rows.append(("SM_Morin_PalmaA", "B1_" + r["nome"], x, y, 0.15, (x * 37) % 360, 1.0, "b1"))
    return build_context(rows, "B1_Contesto")


# =============================================================================================================
# fine passeggiata e raccordo con il Molo Italia (scheda §4.5 aggiornata il 2026-11-20 con le foto I1, I2, A3, MO, C2, G2)
# =============================================================================================================
CHIOSCO_C = (552.06, 108.72)     # centroide della way OSM 352041625 (X 548,8-555,4; Y 105,3-112,1) [V]
SMUSSO_Y_END = 47.0              # la banchina a blocchi finisce a ~Y 47 contro la lunetta del monumento [F] MO, I1
ASTE_Y = (67.0, 63.5, 60.0)      # 3 aste bianche lungo lo smusso [S] ±5 m (I1, A3)
PIAZZALE_X1 = 566.0              # fine del piazzale in cubetti; oltre c'e' l'asfalto di Largo Fiorillo (X 565-580) [S]


def _world_to_ang(p):
    """Coordinate di progetto -> locali di SM_Banchina_Angolo_MoloItalia (origine X_ANG sulla retta, rotZ ROTZ_B)."""
    o = Vector((X_ANG, line_y(X_ANG)))
    a = -math.radians(ROTZ_B)
    d = Vector(p) - o
    return Vector((d.x * math.cos(a) - d.y * math.sin(a), d.x * math.sin(a) + d.y * math.cos(a)))


def smusso_pts():
    """Spigolo (sulla retta dei moduli a X 548,8) e fine dello smusso a blocchi (Y 47) in coordinate di progetto."""
    c = Vector((548.8, line_y(548.8)))
    e0 = Vector(FIANCO_END)
    t = (c.y - SMUSSO_Y_END) / (c.y - e0.y)
    return c, c + (e0 - c) * t


def build_angolo(coll, lod=0, name="SM_Banchina_Angolo_MoloItalia"):
    """Ultimo tratto del ciglio (1,6 m) + spigolo + smusso verso il fianco ovest del Molo Italia fino a ~Y 47, con lo stesso
    profilo a grandi blocchi della banchina v2 (morin_banchina_v2). Origine = fine del modulo 73 (X 547,2), come i moduli."""
    import morin_banchina_v2 as bv
    c, e = smusso_pts()
    P0, P1, P2 = Vector((0.0, 0.0)), _world_to_ang(c), _world_to_ang(e)
    path = [P0, P1, P2]
    d = [(path[i + 1] - path[i]).normalized() for i in range(2)]
    nrm = [bv._ccw(x) for x in d]
    lens = [(path[i + 1] - path[i]).length for i in range(2)]
    nb = [max(1, round(l / 1.333)) for l in lens]
    m1 = (nrm[0] + nrm[1]).normalized()
    k1 = 1.0 / m1.dot(nrm[0])
    P = bv.profile(bv.ARC[lod])
    Pi = bv.inset(P)
    bm = bmesh.new()
    bv._uvl(bm)
    blk = 300
    if bv.JOINTS[lod]:
        rings = [bv.Ring(P0, nrm[0], 1, Pi, None, 0.0)]
        t0 = 0.0
        for seg in range(2):
            for j in range(nb[seg]):
                a = lens[seg] * j / nb[seg]
                b = lens[seg] * (j + 1) / nb[seg]
                if not (seg == 1 and j == 0):
                    rings.append(bv.Ring(path[seg] + d[seg] * (a + bv.JW), nrm[seg], 1, P, blk, t0 + a + bv.JW))
                if seg == 0 and j == nb[0] - 1:
                    rings.append(bv.Ring(P1, m1, k1, P, blk, t0 + lens[0]))
                    continue
                if seg == 1 and j == nb[1] - 1:
                    rings.append(bv.Ring(P2, nrm[1], 1, P, blk, t0 + lens[1]))
                else:
                    rings.append(bv.Ring(path[seg] + d[seg] * (b - bv.JW), nrm[seg], 1, P, blk, t0 + b - bv.JW))
                    rings.append(bv.Ring(path[seg] + d[seg] * b, nrm[seg], 1, Pi, None, t0 + b))
                    blk += 1
            if seg == 0:
                t0 = lens[0]
    else:
        rings = [bv.Ring(P0, nrm[0], 1, P, blk, 0.0), bv.Ring(P1, m1, k1, P, blk, lens[0]),
                 bv.Ring(P2, nrm[1], 1, P, blk, lens[0] + lens[1])]
    bv._run(bm, rings)
    bv._cap(bm, rings[-1], tuple(d[1]) + (0,))
    pp = [P0 + nrm[0] * bv.OV, P1 + m1 * (bv.OV * k1), P2 + nrm[1] * bv.OV]
    tt = [0.0, lens[0], lens[0] + lens[1]]
    for i in range(2):
        a, b = pp[i], pp[i + 1]
        w = bv._ccw(b - a)
        bv._par_quad(bm, a, b, tt[i], tt[i + 1], bv.ZB, -bv.HB, (-w.x, -w.y, 0))
    bv._par_quad(bm, pp[2], P2 + nrm[1] * bv.D, 0, bv.D - bv.OV, bv.ZB, -bv.HB, tuple(d[1]) + (0,))
    o = bv._finish(name + _sfx(lod), bm, [bv.MAT_B, bv.MAT_P], coll)
    if lod == 0:
        D = bv.D
        segs = [(P0, P1 + d[0] * 0.3, nrm[0]), (P1 - d[1] * 0.3, P2, nrm[1])]
        for i, (a, b, n) in enumerate(segs):
            pts = [Vector((p.x, p.y, z)) for p in (a, b, a + n * D, b + n * D) for z in (bv.ZB, -0.005)]
            pk._ucx_hull(name, i, pts, coll)
    return o


def piazzale_poly():
    """Piazzale terminale in cubetti (Z 0): dal bordo interno dello smusso a X 566, da Y 47 fino al camminamento/fascia."""
    import morin_banchina_v2 as bv
    c, e = smusso_pts()
    dv = (e - c).normalized()
    n = Vector((-dv.y, dv.x))
    ci = c + n * bv.D + Vector((0.0, 0.0))
    # spigolo interno: retta del ciglio + D verso terra incontra lo smusso + D
    y_in = line_y(548.8) + bv.D
    t = (y_in - (c.y + n.y * bv.D)) / dv.y
    ci = c + n * bv.D + dv * t
    ei = e + n * bv.D
    return [(ci.x, ci.y), (ei.x, ei.y), (PIAZZALE_X1, ei.y), (PIAZZALE_X1, 121.0), (558.75, 121.0), (558.75, 88.45),
            (559.2, 88.45), (559.2, line_y(559.2) + 0.54)]


def build_piazzale(coll, name="SM_Pav_Piazzale_Fine_B2"):
    """Cubetti a coda di pavone (M_Pav_Cubetti) dal camminamento allo smusso e alla radice del molo; bordo verso il molo
    (Y 47, lunetta del monumento, Blocco 3) e verso Largo Fiorillo (X 566) chiusi con una gonna fino a -3 m."""
    import morin_banchina_v2 as bv
    poly = piazzale_poly()
    # il poligono non e' convesso: triangolazione con bmesh
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0.0)) for x, y in poly]
    f = bm.faces.new(vs)
    if f.normal.z < 0:
        f.normal_flip()
    bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="EAR_CLIP")
    for a, b in ((poly[1], poly[2]), (poly[2], poly[3])):
        q = [bm.verts.new((a[0], a[1], -3.0)), bm.verts.new((b[0], b[1], -3.0)), bm.verts.new((b[0], b[1], 0.0)),
             bm.verts.new((a[0], a[1], 0.0))]
        bm.faces.new(q)
    o = pk._finish(name, bm, ["M_Pav_Cubetti"], coll, uv="world")
    ci, ei = Vector(poly[0]), Vector(poly[1])
    pk._ucx_hull(name, 0, [(x, y, z) for x, y in (poly[0], poly[1], poly[2], (PIAZZALE_X1, poly[7][1]), poly[7])
                           for z in (-3.0, 0.0)], coll)
    pk._ucx(name, [(559.2, PIAZZALE_X1, poly[7][1], 88.45, -3.0, 0.0), (558.75, PIAZZALE_X1, 88.45, 121.0, -3.0, 0.0)], coll,
            start=1)
    return o


def build_piazzetta(coll, name="SM_Pav_Piazzetta_Chiosco_B2"):
    """Piazzetta del chiosco X 540,6-558,75, Y 102-115,45 a quota cubetti (Z 0,15): cubetti grigi con fasce di lastre bianche
    da 0,45 m che incorniciano i riquadri [F] C2. Il lato verso il prato segue l'ipotenusa del triangolo verde."""
    bm = bmesh.new()
    x1, y0, y1 = 558.75, 102.0, VIALETTO_Y[0]
    tri = PRATO_TRI
    poly = [(tri[1][0], y0), (x1, y0), (x1, y1), (tri[2][0], y1)]
    # il lato -X segue l'ipotenusa (540,6; 101,9) -> (526,6; 115,45)
    _prism(bm, poly, ZF - 0.08, ZF, 0, top=True, sides=True)
    # fasce bianche (+2 mm): bordo verso la fascia palme, bordo verso il vialetto, due trasversali [S]
    for (a0, a1, b0, b1) in ((tri[1][0], x1, y0, y0 + 0.45), (tri[2][0] + 2.0, x1, y1 - 0.45, y1),
                             (544.0, 544.45, y0, y1), (558.3, x1, y0, y1)):
        pk._box(bm, a0, a1, b0, b1, ZF, ZF + 0.002, 1, faces=("top",))
    pk._recalc(bm)
    o = pk._finish(name, bm, ["M_Pav_Cubetti", "M_Pav_Fascia"], coll, uv="world")
    pk._ucx_hull(name, 0, [(x, y, z) for x, y in poly for z in (ZF - 0.30, ZF)], coll)
    return o


def build_scritta(coll, name="SM_Pav_Scritta_Morin"):
    """'PASSEGGIATA' / 'MORIN' in pietre bianche nei cubetti (foto scritta_*): lettere piatte a +3 mm sulla fascia.
    Origine (0,0,0) in coordinate di progetto; si legge guardando verso SO (-X)."""
    bm = bmesh.new()
    for body, xc, width in (("PASSEGGIATA", 555.0, 7.0), ("MORIN", 557.7, 4.0)):
        me = _text_mesh(body, 1.0, 0.0, 0.0, resol=3, space=1.25)
        b2 = bmesh.new()
        b2.from_mesh(me)
        bpy.data.meshes.remove(me)
        xs = [v.co.x for v in b2.verts]; ys = [v.co.y for v in b2.verts]
        sx, sy = width / (max(xs) - min(xs)), 0.65 / (max(ys) - min(ys))
        cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        for v in b2.verts:
            u, w = (v.co.x - cx) * sx, (v.co.y - cy) * sy
            v.co = Vector((xc - w, 96.1 + u, ZF + 0.003))       # testo: +u -> +Y, alto -> -X
        tmp = bpy.data.meshes.new("_tmp_scr")
        b2.to_mesh(tmp); b2.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="BEAUTY")
    for f in bm.faces:
        f.material_index = 0
        if f.normal.z < 0:
            f.normal_flip()
    o = pk._finish(name, bm, ["M_Pav_Fascia"], coll, uv="world")
    pk._ucx(name, [(554.5, 558.1, 92.5, 99.7, ZF - 0.05, ZF + 0.003)], coll)
    return o


# ---- chiosco-bar ottagonale ([V] pianta OSM; aspetto [F] C2, I2: tetto in lamiera grigia, tende crema, bancone in legno) ---
OCT_R = 3.30                    # raggio del cerchio circoscritto (Ø 6,6 m OSM)
OCT_H = 2.75                    # gronda
OCT_TOP = 3.45                  # colmo [F] 3,3-3,6
OCT_PHASE = math.radians(22.5)


def _oct(r, z, phase=OCT_PHASE):
    return [Vector((r * math.cos(phase + k * math.pi / 4), r * math.sin(phase + k * math.pi / 4), z)) for k in range(8)]


def _atlas_face(f, lay, reg, scale=0.25):
    """UV dentro una regione dell'atlante di M_Morin_Chiosco (proiezione planare compressa nella regione)."""
    import morin_chiosco as mc
    u0, v0, u1, v1 = mc.RD["wood"] if reg == "wood" else mc.RC[reg]
    n = f.normal
    ax = max(range(3), key=lambda i: abs(n[i]))
    pts = [(lp.vert.co.y, lp.vert.co.z) if ax == 0 else (lp.vert.co.x, lp.vert.co.z) if ax == 1 else
           (lp.vert.co.x, lp.vert.co.y) for lp in f.loops]
    for lp, (a, b) in zip(f.loops, pts):
        fa, fb = (a * scale) % 1.0, (b * scale) % 1.0
        lp[lay].uv = (u0 + 0.05 * (u1 - u0) + 0.9 * (u1 - u0) * 0.5, v0 + 0.05 * (v1 - v0) + 0.9 * (v1 - v0) * 0.5) \
            if reg in ("crema", "steel", "white", "dark") else (u0 + (u1 - u0) * (0.05 + 0.9 * fa), v0 + (v1 - v0) * (0.05 + 0.9 * fb))


def build_chiosco_ott(coll, lod=0, name="SM_Morin_ChioscoOttagonale"):
    """Origine a terra al centro; bancone su 5 lati (verso mare e passeggiata), retro chiuso su 3 lati (verso il viale, +Y)."""
    bm = bmesh.new()
    lay = bm.loops.layers.uv.verify()
    regs = {}

    def face(vs, reg):
        f = bm.faces.new([bm.verts.new(v) for v in vs])
        regs[f] = reg
        return f
    R0 = OCT_R - 0.35                       # corpo (sotto la gronda e le tende)
    zb, zc, zw = 0.0, 1.10, OCT_H - 0.05
    B, C, Wt = _oct(R0, zb), _oct(R0, zc), _oct(R0, zw)
    for k in range(8):
        j = (k + 1) % 8
        mid = (B[k] + B[j]) / 2
        back = mid.y > 0.8                  # lati verso il viale: chiusi
        face([B[k], B[j], C[j], C[k]], "wood" if not back else "crema")
        if back:
            face([C[k], C[j], Wt[j], Wt[k]], "crema")
        else:
            # vano di servizio: arretrato di 0,6 m (scuro), piano del bancone sporgente
            Ci, Wi = _oct(R0 - 0.6, zc), _oct(R0 - 0.6, zw)
            face([Ci[k], Ci[j], Wi[j], Wi[k]], "dark")
            face([C[k], C[j], Ci[j], Ci[k]], "wood")            # piano del bancone
            face([Wi[k], Wi[j], Wt[j], Wt[k]], "crema")         # architrave sotto la gronda (fascia)
    # tende a falda crema su tutti i lati (sporgono 0,9 m, scendono a 2,15 m)
    if lod < 2:
        T0, T1 = _oct(R0 - 0.02, zw - 0.10), _oct(R0 + 1.05, 2.05)
        for k in range(8):
            j = (k + 1) % 8
            face([T1[k], T1[j], T0[j], T0[k]], "crema")
            if lod == 0:   # mantovana
                M1 = _oct(R0 + 1.05, 1.80)
                face([M1[k], M1[j], T1[j], T1[k]], "crema")
    # tetto: gronda sporgente, falde basse in lamiera fino a un colmo ottagonale piccolo
    G0, G1 = _oct(OCT_R, OCT_H), _oct(OCT_R, OCT_H + 0.12)
    Top = _oct(0.6, OCT_TOP)
    for k in range(8):
        j = (k + 1) % 8
        face([G0[k], G0[j], G1[j], G1[k]], "steel")
        face([G1[k], G1[j], Top[j], Top[k]], "steel")
        face([G0[j], G0[k], Wt[k], Wt[j]], "dark")            # intradosso
    face(list(reversed(Top)), "steel").normal_flip()
    pk._recalc(bm)
    for f, reg in regs.items():
        _atlas_face(f, lay, reg)
        f.material_index = 1 if reg == "wood" else 0
    o = pk._finish(name + _sfx(lod), bm, ["M_Morin_Chiosco", "M_Morin_Dehors"], coll, uv=None, smooth_angle=None)
    if lod == 0:
        pk._ucx_hull(name, 0, [tuple(v) for v in _oct(R0, 0.0) + _oct(R0, OCT_H)], coll)
        pk._ucx_hull(name, 1, [tuple(v) for v in _oct(OCT_R, OCT_H) + _oct(0.6, OCT_TOP)], coll)
    return o


def build_asta(coll, lod=0, name="SM_Morin_AstaBandiera"):
    """Asta portabandiera bianca h 11,5 m [F] I1/A3 (stima ±1,5 m) su piccolo basamento; bandiere non modellate."""
    bm = bmesh.new()
    n = (10, 8, 5)[lod]
    pk._lathe(bm, [(0.0, 0.0), (0.22, 0.0), (0.22, 0.12), (0.075, 0.12), (0.07, 0.6), (0.045, 11.4), (0.06, 11.42),
                   (0.06, 11.5), (0.0, 11.52)], n, Matrix(), 0)
    o = pk._finish(name + _sfx(lod), bm, ["M_Pav_Fascia"], coll, uv="box", smooth_angle=50.0)
    if lod == 0:
        pk._ucx(name, [(-0.22, 0.22, -0.22, 0.22, 0.0, 0.12), (-0.07, 0.07, -0.07, 0.07, 0.12, 11.5)], coll)
    return o


def aste_xy():
    c, e = smusso_pts()
    dv = (e - c).normalized()
    n = Vector((-dv.y, dv.x))
    out = []
    for y in ASTE_Y:
        t = (y - c.y) / dv.y
        p = c + dv * t + n * 2.2
        out.append((p.x, p.y))
    return out


def layout_fine():
    R = []

    def add(g, a, n, x, y, z=0.0, rz=0.0):
        R.append((a, n, float(x), float(y), float(z), float(rz), 1.0, g))
    add("nuovi", "SM_Banchina_Angolo_MoloItalia", "B2_Angolo_MoloItalia", X_ANG, line_y(X_ANG), 0.0, ROTZ_B)
    for a in ("SM_Pav_Piazzale_Fine_B2", "SM_Pav_Piazzetta_Chiosco_B2", "SM_Pav_Scritta_Morin"):
        add("nuovi", a, a.replace("SM_", "B2_"), 0.0, 0.0)
    add("nuovi", "SM_Morin_ChioscoOttagonale", "B2_ChioscoOttagonale", CHIOSCO_C[0], CHIOSCO_C[1], ZF, 0.0)
    for k, (x, y) in enumerate(aste_xy()):
        add("nuovi", "SM_Morin_AstaBandiera", f"B2_Asta_{k:02d}", x, y, 0.0)
    # dehors (kit del chiosco del Blocco 1) verso SO e verso il mare [F] C2, disposizione [S]
    cx, cy = CHIOSCO_C
    for k, (dx, dy) in enumerate(((-9.5, -1.5), (-9.5, 3.6), (-4.0, -5.6), (4.5, -5.6))):
        add("chiosco", "SM_Morin_Ombrellone", f"B2_Ombrellone_{k:02d}", cx + dx, cy + dy, ZF)
        add("chiosco", "SM_Morin_TavoloSet", f"B2_TavoloSet_{k:02d}", cx + dx, cy + dy, ZF, 15.0 * k)
    for k, (dx, dy) in enumerate(((-5.6, -3.6), (-5.8, 2.4), (0.3, -5.0), (5.6, -2.6))):
        add("chiosco", "SM_Morin_Sgabello", f"B2_Sgabello_{k:02d}", cx + dx, cy + dy, ZF, 30.0 * k)
    for k, (dx, dy, a) in enumerate(((-11.0, -4.8, "SM_Morin_Fioriera"), (-11.0, 1.0, "SM_Morin_FiorieraB"),
                                     (-0.5, -6.2, "SM_Morin_Fioriera"), (6.0, -6.2, "SM_Morin_FiorieraB"))):
        add("chiosco", a, f"B2_Fioriera_{k:02d}", cx + dx, cy + dy, ZF, 90.0 * (k % 2))
    for k, (dx, dy) in enumerate(((-6.5, -5.8), (6.2, 0.5))):
        add("chiosco", "SM_Morin_Lampione", f"B2_Lampione_Dehors_{k:02d}", cx + dx, cy + dy, ZF)
    return R


# =============================================================================================================
# build ed export
# =============================================================================================================
LODDED = {"SM_Morin_Cannone": build_cannone, "SM_Morin_Redamare": build_redamare,
          "SM_Banchina_Angolo_MoloItalia": build_angolo, "SM_Morin_ChioscoOttagonale": build_chiosco_ott,
          "SM_Morin_AstaBandiera": build_asta}
SINGLE = {"SM_Pav_Camminamento_4m_B2": build_camminamento_b2, "SM_Pav_FasciaPalme_Fine": build_fascia_fine,
          "SM_Morin_Prato_Giardini_B2": build_prato_b2, "SM_Pav_Vialetti_B2": build_vialetti,
          "SM_Pav_Piazzale_Fine_B2": build_piazzale, "SM_Pav_Piazzetta_Chiosco_B2": build_piazzetta,
          "SM_Pav_Scritta_Morin": build_scritta}
BLOCKOUT = {"SM_Blockout_Passeggiata_B2": build_blockout_passeggiata, "SM_Blockout_Fondale_B2_Terreno": build_blockout_terreno}
EXP_SUB = {"SM_Blockout_Passeggiata_B2": "//../exports/blockout", "SM_Blockout_Fondale_B2_Terreno": "//../exports/blockout"}


def build_all():
    coll = pk._coll(KIT)
    rep = {}
    for nm, fn in LODDED.items():
        rep[nm] = [pk.tri_count(fn(coll, l)) for l in range(3)]
    for nm, fn in list(SINGLE.items()) + list(BLOCKOUT.items()):
        rep[nm] = [pk.tri_count(fn(coll))]
    _hide_kit(coll)
    for nm in rep:
        o = bpy.data.objects[nm]
        n_ucx = len([u for u in coll.objects if u.name.startswith(f"UCX_{nm}_")])
        rep[nm] = (rep[nm], tuple(round(d, 2) for d in o.dimensions), n_ucx)
        print(f"{nm:<34} tri {rep[nm][0]}  dim {rep[nm][1]}  UCX {n_ucx}")
    return rep


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    coll = bpy.data.collections[KIT]
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in coll.objects}
    for o in coll.objects:
        o.hide_viewport = False
        o.hide_set(False)
    bpy.context.view_layer.update()
    reps = []
    try:
        for nm in LODDED:
            for lod in range(3):
                on = nm + _sfx(lod)
                reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                                    overwrite=overwrite, include_ucx=(lod == 0), bake_rotation=(lod > 0),
                                                    verbose=False))
        for nm in list(SINGLE) + list(BLOCKOUT):
            d = EXP_SUB.get(nm, EXPDIR)
            reps.append(morin_export.export_fbx([bpy.data.objects[nm]], f"{d}/{nm}.fbx", mode="asset",
                                                overwrite=overwrite, include_ucx=True, verbose=False))
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps



# =============================================================================================================
# LAYOUT v5 (2026-11-20): passo delle palme 8 m, prima coppia a X 20,4 (ref/palme.md §6). Le costanti e le funzioni v1
# qui sopra restano invariate (PALME_X, PANCH_X, LAMP_X, X_FASCIA, N_FASCIA, build_fascia_fine, write_csvs).
# Il layout v5 e' calcolato in un solo punto per i due blocchi: pk.layout_v5() (morin_pav_kit.py).
#     b2.build_fascia_fine_v5(pk._coll(b2.KIT))     # SM_Pav_FasciaPalme_Fine_v2 (+ UCX)
#     rows = pk.layout_v5(); pk.check_layout_v5(rows + b2.scritta_rows_v5())
#     b2.write_csvs_v5(rows)                        # exports/blocco2/blocco2_{palme,pav,arredi}_v5.csv
# =============================================================================================================
PALME_X_V5 = [x for x in pk.v5_palme_x() if x > pk.V5_X_B1_END]                    # 260,4 ... 556,4 (38 per filare)
PANCH_X_V5 = [pk.V5_PANCH[0] + pk.V5_PANCH[1] * k for k in range(pk.V5_PANCH[2])
              if pk.V5_PANCH[0] + pk.V5_PANCH[1] * k > pk.V5_X_B1_END]              # 256,4 ... 544,4 (19)
LAMP_X_V5 = [pk.V5_LAMP[0] + pk.V5_LAMP[1] * k for k in range(pk.V5_LAMP[2])
             if pk.V5_LAMP[0] + pk.V5_LAMP[1] * k > pk.V5_X_B1_END]                 # 256,7 ... 544,7 (10)
X_FASCIA_V5 = pk.V5_X_B1_END                    # 256,4: primo modulo 8 m del Blocco 2
N_FASCIA_V5 = pk.V5_N_MOD - pk.V5_N_MOD_B1 + 1  # 37 moduli da 8 m + SM_Pav_FasciaPalme_Fine_v2 (552,4 -> 558,75)
# La scritta "PASSEGGIATA / MORIN" (mesh in coordinate di progetto, X 554,7-558,0) cade sulle aiuole dell'ultima palma
# (556,4: aiuole X 554,6-558,2). La scheda la mette "prima della prima palma da NE" [F]: si sposta l'attore di +4,2 m in X
# (lettere X 558,9-562,2, sul piazzale in cubetti), senza toccare la mesh.
SCRITTA_DX_V5 = 4.2


def build_fascia_fine_v5(coll, name="SM_Pav_FasciaPalme_Fine_v2", L=pk.V5_L_FINE):
    """Coda della fascia v5, X 552,4 -> 558,75 (L 6,35 m): mezza striscia trasversale all'inizio (chiude quella del modulo
    da 8 m precedente), strisce longitudinali lungo le aiuole dell'ultima palma (X locale 0 -> 5,8 = fine aiuola a 558,2),
    una striscia trasversale piena (5,8 -> 6,1) e cubetti liberi fino a 558,75 (poi il piazzale della scritta)."""
    h = pk.V5_STRIP_H
    a1 = 4.0 + pk.AIU_X / 2                       # 5,8: fine dell'aiuola dell'ultima palma (palma a X locale 4,0)
    xs = [0.0, h, a1, a1 + pk.STRIP, L]
    bm = bmesh.new()
    pk._fascia_grid(bm, xs, lambda i, j: (j == 2 and i == 0) or (j in (1, 3) and i in (0, 1)) or i == 2)
    pk._box(bm, 0, L, pk.K1, pk.Y_END, pk.ZB, ZF, 0, faces=("xn", "xp", "yp"))
    o = pk._finish(name, bm, ["M_Pav_Cubetti", "M_Pav_Fascia"], coll)
    pk._ucx(name, [(0, L, pk.K1, pk.Y_END, pk.ZB, ZF)], coll)
    return o


def scritta_rows_v5():
    """Impronte (statiche) della scritta spostata, per pk.check_layout_v5(statics=...)."""
    d = SCRITTA_DX_V5
    return [("SM_Pav_Scritta_Morin", "Scritta_PASSEGGIATA", 555.0 + d, 96.1, 0.33, 3.5),
            ("SM_Pav_Scritta_Morin", "Scritta_MORIN", 557.7 + d, 96.1, 0.33, 2.0)]


def write_csvs_v5(rows=None, prefix="exports/blocco2/blocco2"):
    """CSV v5 del Blocco 2 (palme, pav, arredi) con nomi nuovi; i v1 restano intatti. Camminamento e cordolo copiati dal v1
    (invariati); la riga SM_Pav_Scritta_Morin in pav e' lo spostamento dell'attore (offset +420 uu in X)."""
    import csv
    rows = pk.layout_v5() if rows is None else rows
    paths = {g: f"{PROJ}/{prefix}_{g}_v5.csv" for g in ("palme", "pav", "arredi")}
    for p in paths.values():
        if os.path.exists(p):
            raise RuntimeError(f"esiste gia, non lo sovrascrivo: {p}")
    out = {g: ["asset,nome,x,y,z,yaw,scala"] for g in paths}
    with open(f"{PROJ}/{prefix}_pav_v1.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["asset"] in ("SM_Pav_Camminamento_4m_B2", "SM_Pav_Cordolo_9m"):
                out["pav"].append(",".join(r[k] for k in ("asset", "nome", "x", "y", "z", "yaw", "scala")))
    for a, n, x, y, z, rz, s, b, g in rows:
        if b != "B2":
            continue
        yaw = -rz if abs(rz) > 1e-9 else 0.0
        out[g].append(f"{a},{n},{_ue(x * 100)},{_ue(-y * 100)},{_ue(z * 100)},{yaw:.4f},{s:.3f}")
    out["pav"].append(f"SM_Pav_Scritta_Morin,B2_Pav_Scritta_Morin,{_ue(SCRITTA_DX_V5 * 100)},0.0,0.0,0.0000,1.000")
    for g, p in paths.items():
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(out[g]) + "\n")
        print(f"{g:<8} {len(out[g]) - 1:>4}  {p}")
    return {g: len(out[g]) - 1 for g in out}
