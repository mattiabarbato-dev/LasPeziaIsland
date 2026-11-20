"""morin_marina_ingresso.py — ingresso della marina dalle foto dell'utente (2026-11-20).

Scheda: ref/foto_nuove_2026-11-20.md §8 (geo-scout) + decisioni dell'orchestratore 2026-11-20:
  portale blu a (151; 81,2) alla radice della spina; ufficio galleggiante a doghe ~10 x 6 x 3 m con terrazza a ~(158; 71) che
  SOSTITUISCE SM_Morin_Marina_Circolo; bitta arrugginita a (147,5; 80,4).
Foto (catture Street View dell'utente, deroga CLAUDE.md §5, marca [SV] in CREDITS):
  M1 nautica_marina.png  ufficio galleggiante, passerella, portale di lato
  M2 marina_nautica.png  portale di fronte, bitta arrugginita
Nomi in parodia (scheda §9, decisione dell'orchestratore): "ASSONNAUTICA" (logo tondo con una vela che sbadiglia) e
"Porto Turistico Vento Contrario"; "PORTO TURISTICO" e il cartello generico di videosorveglianza restano.
La foto d'epoca del pannello (due persone) e' sostituita da un'immagine d'epoca inventata senza persone.

Asset:
  SM_Morin_Marina_Ufficio        pontone 11 x 7 m + scatola 10 x 6 x 3 m a doghe, insegna, terrazza con candelieri e cavi,
                                 tendina bianca. Origine al centro sul piano del pontone; si posa a Z -0,5. UCX.
  SM_Morin_Marina_Portale        telaio blu 3,0 m, architrave con lettere in rilievo, due ante (una aperta), pilastri, pannello
                                 con foto d'epoca, citofono, lettore di badge, cartello. Origine al centro della base, fronte +Y. UCX.
  SM_Morin_Marina_Passerella_v2  come la v1 (3,5 x 2,8 m, dal ciglio Z 0 al galleggiante Z -0,45) con ringhiera blu a 3 correnti.
  SM_Banchina_Bitta_Ruggine      bitta a colonna 0,70 m, fusto Ø 0,30, anello in cima e collare; ruggine dalla foto M2.

Esegui dentro blender/arte_marina.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_atlas_v2 as av, morin_marina_ingresso as mg; importlib.reload(av); importlib.reload(mg)
    mg.make_textures(); mg.build_materials(); mg.build_all(); mg.check_all(); mg.write_csv(); mg.build_context(); mg.export_all()
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_texphoto as tp
import morin_imbarco as mi
import morin_atlas_v2 as av
from morin_atlas_v2 import Canvas, F_BOLD, F_SANS, F_SERIF, F_SERIF_B

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/marina_ingresso"
FOTO = PROJ + "/ref/foto/vista/"
KIT = "MARINA_Ingresso_Kit"
CTX = "MARINA_Ingresso_Contesto"
EXPDIR = "//../exports/marina"

NOME = "ASSONNAUTICA"
SOTTO = "La Spezia | Porto Turistico Vento Contrario"

MAT_A, MAT_D, MAT_B, MAT_W, MAT_R = ("M_Morin_Marina_Ingresso", "M_Morin_Marina_Doghe", "M_Morin_Marina_LamieraBlu",
                                     "M_Morin_Imbarco_Legno", "M_Banchina_Bitta_Ruggine")
TILE_D, TILE_B = 1.2, 1.0
MATS = [(MAT_A, "atlas", 0), (MAT_D, "world", TILE_D), (MAT_B, "world", TILE_B), (MAT_W, "world", 2.0)]
A_, D_, B_, W_ = range(4)

BLU = (0.09, 0.32, 0.70)            # scheda: #1B50AB in ombra, #3072C9 in luce

ATL = av.Atlas("T_Morin_Marina_Ingresso", 2048, 128)
CELLS = {
    "BLU": (BLU, 0.04, 0.40, 0.3), "BLU_OMBRA": ((0.06, 0.22, 0.52), 0.04, 0.45, 0.3),
    "ARGENTO": ((0.80, 0.81, 0.82), 0.03, 0.30, 0.9), "BIANCO": ((0.90, 0.90, 0.89), 0.02, 0.40, 0.0),
    "NERO": ((0.05, 0.05, 0.06), 0.02, 0.50, 0.0), "GRIGIO": ((0.45, 0.46, 0.47), 0.04, 0.60, 0.0),
    "GRIGIO_SCURO": ((0.22, 0.22, 0.22), 0.05, 0.75, 0.0), "VETRO": ((0.10, 0.13, 0.17), 0.02, 0.06, 0.5, "vetro"),
    "PONTONE": ((0.16, 0.17, 0.15), 0.08, 0.80, 0.2, "ruggine"), "INOX": ((0.70, 0.71, 0.72), 0.03, 0.25, 1.0),
    "TENDA": ((0.93, 0.93, 0.91), 0.03, 0.85, 0.0), "ROSSO": ((0.70, 0.10, 0.08), 0.03, 0.40, 0.0),
    "SCURO": ((0.12, 0.12, 0.13), 0.03, 0.50, 0.2), "CORDA": ((0.80, 0.77, 0.68), 0.06, 0.9, 0.0),
    "LEGNO_BORDO": ((0.42, 0.26, 0.15), 0.06, 0.6, 0.0, "venatura"), "CEMENTO": ((0.55, 0.54, 0.51), 0.05, 0.85, 0.0),
}
for i, k in enumerate(CELLS):
    ATL.add(k, i % 16, i // 16)
ATL.add("LOGO", 0, 2, 4, 4)            # logo tondo ASSONNAUTICA (parodia)
ATL.add("PILASTRO", 4, 2, 2, 12)       # scritta verticale PORTO TURISTICO / Vento Contrario (0,4 x 2,4)
ATL.add("FOTO", 6, 2, 4, 6)            # foto d'epoca inventata (1,4 x 2,1), senza persone
ATL.add("EMBLEMA", 10, 2, 3, 3)        # emblema tondo delle ante
ATL.add("CARTELLO_VS", 13, 2, 2, 3)    # cartello giallo "area videosorvegliata" (generico)
ATL.add("CITOFONO", 15, 2, 1, 2)       # citofono
ATL.add("BADGE", 15, 4, 1, 1)          # lettore di badge
ATL.add("FOTO_RETRO", 6, 8, 4, 2)      # retro del pannello: didascalia


def _cv(W, H, x0, x1, y0, y1, bg, rough=0.45):
    return Canvas(x0, x1, y0, y1, max(W / (x1 - x0), H / (y1 - y0)), bg, rough)


def p_logo(W, H):
    """Logo tondo in parodia: disco blu con corona bianca, cerchio rosso e una vela che sbadiglia (con le Zzz)."""
    cv = _cv(W, H, -1, 1, -1, 1, (0.92, 0.92, 0.9))
    cv.circle(0, 0, 0.98, (0.08, 0.20, 0.55))
    cv.circle(0, 0, 0.70, (0.72, 0.84, 0.95))
    cv.circle(-0.12, -0.05, 0.42, (0.80, 0.12, 0.10))
    cv.poly([(0.05, -0.45), (0.05, 0.55), (0.48, -0.45)], (0.95, 0.95, 0.93))            # vela
    cv.line([(0.05, -0.50), (0.05, 0.60)], 0.04, (0.08, 0.20, 0.55))                       # albero
    cv.ellipse(0.22, -0.12, 0.08, 0.05, (0.08, 0.20, 0.55))                               # bocca che sbadiglia
    cv.line([(0.13, 0.05), (0.21, 0.03)], 0.025, (0.08, 0.20, 0.55))                       # occhi chiusi
    cv.line([(0.25, 0.03), (0.33, 0.05)], 0.025, (0.08, 0.20, 0.55))
    cv.text("z", 0.35, 0.22, 0.50, 0.36, (0.08, 0.20, 0.55), font=F_BOLD)
    cv.text("Z", 0.45, 0.36, 0.66, 0.56, (0.08, 0.20, 0.55), font=F_BOLD)
    cv.text("ASSONNAUTICA", -0.66, 0.74, 0.66, 0.92, (1, 1, 1), font=F_BOLD)
    cv.text("LA SPEZIA", -0.45, -0.92, 0.45, -0.76, (1, 1, 1), font=F_BOLD)
    cv.grime(21, 0.02, 0.0)
    return cv.out(W, H)


def p_pilastro(W, H):
    """Scritta verticale dal basso in alto (M2): si dipinge in orizzontale e si ruota di 90 gradi."""
    cv = Canvas(0, 2.4, 0, 0.4, 600, BLU)
    cv.text("PORTO TURISTICO", 0.15, 0.17, 2.25, 0.36, (1, 1, 1), font=F_BOLD)
    cv.text("Vento Contrario", 0.15, 0.04, 2.25, 0.16, (1, 1, 1), font=F_BOLD)
    cv.grime(22, 0.04, 0.0)
    rgb, h, r, m = cv.rgb, cv.h, cv.r, cv.m
    rot = lambda a: np.rot90(a, -1).copy()          # testo che sale dal basso (array con la riga 0 in basso)
    rgb, h, r, m = rot(rgb), rot(h), rot(r), rot(m)
    rs = lambda a: tp.resize(a if a.ndim == 3 else a[..., None], W, H)
    return rs(rgb), rs(h)[..., 0], rs(r)[..., 0], rs(m)[..., 0]


def p_foto(W, H):
    """Foto d'epoca inventata (seppia): banchina, un veliero e il faro, nessuna persona. Cornice blu."""
    cv = _cv(W, H, 0, 1.4, 0, 2.1, BLU, 0.5)
    sep = lambda v: (0.30 + 0.62 * v, 0.27 + 0.56 * v, 0.22 + 0.45 * v)
    X, Y = cv.X, cv.Y
    inner = ((X > 0.08) & (X < 1.32) & (Y > 0.08) & (Y < 2.02)).astype(np.float32)
    sky = np.clip(0.55 + 0.25 * (Y - 1.0), 0, 1)
    img = np.dstack([0.30 + 0.62 * sky, 0.27 + 0.56 * sky, 0.22 + 0.45 * sky])
    cv.rgb = cv.rgb * (1 - inner[..., None]) + img * inner[..., None]
    cv.rect(0.08, 0.08, 1.32, 0.80, sep(0.35))                                    # mare
    cv.poly([(0.08, 0.80), (0.5, 0.95), (0.9, 0.86), (1.32, 0.98), (1.32, 0.80)], sep(0.25))   # colline
    cv.rect(0.08, 0.08, 0.65, 0.42, sep(0.5))                                     # banchina in pietra
    for k in range(6):
        cv.rect(0.08 + 0.1 * k, 0.41, 0.085 + 0.1 * k, 0.42, sep(0.3))
    cv.poly([(0.75, 0.62), (1.20, 0.62), (1.14, 0.54), (0.80, 0.54)], sep(0.12))   # scafo del veliero
    cv.line([(0.96, 0.62), (0.96, 1.45)], 0.012, sep(0.1))
    cv.poly([(0.97, 0.66), (0.97, 1.40), (1.18, 0.68)], sep(0.85))
    cv.poly([(0.95, 0.70), (0.95, 1.25), (0.78, 0.70)], sep(0.80))
    cv.rect(0.22, 0.42, 0.30, 0.95, sep(0.75))                                   # faro
    cv.rect(0.20, 0.95, 0.32, 1.02, sep(0.2))
    cv.paint(np.clip(av.fine(cv.H, cv.W, 23, 0.7) * 0.5, 0, 1) * 0.12 * inner, sep(0.1))   # grana
    cv.text("Il porto, primi del Novecento", 0.12, 0.12, 1.28, 0.20, sep(0.95), font=F_SERIF)
    return cv.out(W, H)


def p_foto_retro(W, H):
    cv = _cv(W, H, 0, 1.4, 0, 0.7, BLU)
    cv.text("PORTO TURISTICO", 0.1, 0.40, 1.3, 0.55, (1, 1, 1), font=F_BOLD)
    cv.text("Vento Contrario", 0.1, 0.20, 1.3, 0.34, (1, 1, 1), font=F_SANS)
    return cv.out(W, H)


def p_emblema(W, H):
    cv = _cv(W, H, -1, 1, -1, 1, BLU)
    cv.circle(0, 0, 0.92, (0.75, 0.80, 0.88), r_in=0.80)
    cv.poly([(0.0, -0.5), (0.0, 0.55), (0.42, -0.5)], (0.75, 0.80, 0.88))
    cv.poly([(-0.05, -0.5), (-0.05, 0.35), (-0.36, -0.5)], (0.75, 0.80, 0.88))
    cv.line([(-0.55, -0.62), (0.55, -0.62)], 0.06, (0.75, 0.80, 0.88))
    return cv.out(W, H)


def p_cartello(W, H):
    cv = _cv(W, H, 0, 0.25, 0, 0.375, (0.97, 0.80, 0.10), 0.5)
    cv.rect(0.01, 0.01, 0.24, 0.365, (0.97, 0.80, 0.10))
    cv.text("ATTENZIONE!", 0.02, 0.33, 0.23, 0.36, (0.05, 0.05, 0.05))
    cv.rect(0.06, 0.19, 0.19, 0.31, (0.05, 0.05, 0.05))
    cv.rect(0.08, 0.23, 0.15, 0.27, (0.97, 0.80, 0.10))
    cv.circle(0.165, 0.25, 0.018, (0.97, 0.80, 0.10))
    for i, t in enumerate(("AREA VIDEOSORVEGLIATA", "LA REGISTRAZIONE E'", "EFFETTUATA PER", "RAGIONI DI SICUREZZA")):
        cv.text(t, 0.02, 0.15 - 0.032 * i, 0.23, 0.175 - 0.032 * i, (0.05, 0.05, 0.05), font=F_BOLD)
    return cv.out(W, H)


def p_citofono(W, H):
    cv = _cv(W, H, 0, 0.12, 0, 0.24, (0.62, 0.63, 0.64), 0.35)
    cv.circle(0.06, 0.18, 0.025, (0.15, 0.15, 0.16))
    for k in range(3):
        cv.rect(0.03, 0.04 + 0.03 * k, 0.09, 0.06 + 0.03 * k, (0.80, 0.80, 0.80))
    return cv.out(W, H)


def p_badge(W, H):
    cv = _cv(W, H, 0, 0.1, 0, 0.1, (0.2, 0.2, 0.22), 0.3)
    cv.rect(0.02, 0.02, 0.08, 0.08, (0.08, 0.08, 0.1))
    cv.circle(0.05, 0.05, 0.012, (0.1, 0.6, 0.2))
    return cv.out(W, H)


# ---- texture ripetibili dalle foto -----------------------------------------------------------------------------------
def make_tex_doghe(size=1024, seed=41):
    """Doghe orizzontali da 12 cm (10 per ripetizione da 1,2 m). Tinte delle doghe e venatura dalla fascia sotto la scritta
    dell'ufficio in M1 (x 160-700, y 300-365, scheda §10), raddrizzata: logo e scritte esclusi."""
    img = tp.load(FOTO + "nautica_marina.png")[..., :3]
    crop = tp.warp(img, [(162, 300), (698, 302), (698, 364), (162, 362)], 1080, 124)
    crop = tp.delight(crop, 25.0, 0.8)
    rows = crop.mean(1)                               # colore medio per riga: alterna doghe e fughe
    L = tp.lum(rows[None])[0]
    lit = rows[L > np.percentile(L, 40)]
    base = np.median(lit, 0) * 0.95
    tints = lit / np.maximum(base, 1e-3)
    rng = np.random.default_rng(seed)
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    NS = 10
    idx = np.minimum((yy * NS).astype(int), NS - 1)
    v = (yy * NS) % 1.0
    pick = tints[rng.integers(0, len(tints), NS)].astype(np.float32)
    gap = (v < 0.05)
    g = tp.blur(rng.standard_normal((n, n)).astype(np.float32), 1.0)   # venatura lungo le doghe (la foto ha 5 px per doga:
    g = tp.resize(tp.resize(g[..., None], n // 16, n), n, n)[..., 0]    # troppo pochi per una venatura vera)
    hp = 1.0 + 0.06 * g / (g.std() + 1e-6)
    off = rng.uniform(0, 1, NS)
    seg = (xx + off[idx]) % 1.0
    joint = seg < 0.002
    rgb = base[None, None, :] * pick[idx] * hp[..., None] * (1 + 0.04 * av.noise(n, n, 6, seed)[..., None])
    rgb[gap | joint] = rgb[gap | joint] * 0.25
    h = 0.6 - 0.5 * (gap | joint) + 0.03 * (hp - 1)
    R = np.full((n, n), 0.62, np.float32)
    return av.save_set("T_Morin_Marina_Doghe", np.clip(rgb, 0, 1), h, R, np.zeros_like(R), TEXDIR, 6.0)


def make_tex_lamiera(size=1024, seed=43):
    """Acciaio verniciato blu (1 m): tinta dal montante in M2 (x 685-700, y 300-400, scheda §10), graffi e sporco."""
    img = tp.load(FOTO + "marina_nautica.png")[..., :3]
    patch = img[300:400, 685:700].reshape(-1, 3)
    base = np.median(patch, 0) * 0.85
    n = size
    rng = np.random.default_rng(seed)
    big = av.noise(n, n, 5, seed)
    f = av.fine(n, n, seed + 1, 0.7)
    rgb = base[None, None, :] * (1 + 0.04 * big + 0.02 * f)[..., None]
    scr = np.zeros((n, n), np.float32)
    for _ in range(60):
        x0, y0 = rng.uniform(0, n, 2)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(10, 60)
        for t in np.linspace(0, 1, int(L)):
            x, y = int(x0 + t * L * math.cos(a)) % n, int(y0 + t * L * math.sin(a)) % n
            scr[y, x] = 1.0
    scr = np.clip(tp.blur(scr, 0.6) * 3, 0, 1)
    rgb = rgb * (1 - 0.5 * scr[..., None]) + np.array((0.55, 0.57, 0.60)) * 0.5 * scr[..., None]
    h = 0.5 - 0.1 * scr + 0.01 * f
    R = np.clip(0.50 + 0.08 * big + 0.3 * scr, 0, 1)
    M = 0.2 * scr
    return av.save_set("T_Morin_Marina_LamieraBlu", np.clip(rgb, 0, 1), h, R, M.astype(np.float32), TEXDIR, 3.0)


def make_tex_ruggine(W=512, H=1024):
    """Ruggine della bitta dalla foto M2 (x 955-1025, y 380-505, scheda §10): fascia centrale del fusto (meno scorcio),
    tolte le luci larghe, resa ripetibile in orizzontale (u = mezzo giro)."""
    img = tp.load(FOTO + "marina_nautica.png")[..., :3]
    crop = img[383:503, 968:1012]
    crop = tp.delight(crop, 12.0, 0.7)
    a = tp.resize(crop, W, H)
    a = tp.tileable(a)
    L = tp.lum(a)
    h = 0.5 + 0.4 * (tp.highpass(L, 4.0) - 1)
    R = np.full((H, W), 0.88, np.float32)
    M = np.full((H, W), 0.15, np.float32)
    return av.save_set("T_Banchina_Bitta_Ruggine", np.clip(a * 0.95, 0, 1)[::-1].copy(), h[::-1].copy(), R, M, TEXDIR, 5.0)


def make_textures():
    painters = {k: av.color_cell(v, 300 + i) for i, (k, v) in enumerate(CELLS.items())}
    painters.update({"LOGO": p_logo, "PILASTRO": p_pilastro, "FOTO": p_foto, "EMBLEMA": p_emblema,
                     "CARTELLO_VS": p_cartello, "CITOFONO": p_citofono, "BADGE": p_badge, "FOTO_RETRO": p_foto_retro})
    return {"atlas": ATL.bake(painters, TEXDIR, 4.0), "doghe": make_tex_doghe(), "lamiera": make_tex_lamiera(),
            "ruggine": make_tex_ruggine()}


def build_materials():
    t = f"{TEXDIR}/"
    for m, n in ((MAT_A, "T_Morin_Marina_Ingresso"), (MAT_D, "T_Morin_Marina_Doghe"), (MAT_B, "T_Morin_Marina_LamieraBlu"),
                 (MAT_R, "T_Banchina_Bitta_Ruggine")):
        mat = bpy.data.materials.get(m)
        if mat is not None and mat.library is not None:
            mat = None
        pk._pbr_material(m, t + n + "_D.png", t + n + "_N.png", t + n + "_ORM.png")
    if bpy.data.materials.get(MAT_W) is None:      # legno dei galleggianti: stesso materiale (e MI in UEFN) della marina
        d = PROJ + "/blender/textures/imbarco/T_Morin_Imbarco_Legno"
        pk._pbr_material(MAT_W, d + "_D.png", d + "_N.png", d + "_ORM.png")


def G():
    return av.G2(ATL, MATS)


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


def _local_mats(o):
    """Gli slot puntano ai materiali locali (mai a quelli collegati da altri .blend)."""
    for s in o.material_slots:
        m = s.material
        if m is not None and m.library is not None:
            loc = next((x for x in bpy.data.materials if x.name == m.name and x.library is None), None)
            if loc is not None:
                s.material = loc
    return o


def _text(g, body, size, M, cell, font=F_SERIF_B, extrude=0.0, align="CENTER", mi_=A_, res=2):
    cu = bpy.data.curves.new("_tmp_txt", "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.resolution_u = res
    cu.extrude = extrude
    f = av._font(font)
    if f is not None:
        cu.font = f
    ob = bpy.data.objects.new("_tmp_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    me.transform(M)
    g.new_faces(lambda bm: bm.from_mesh(me), cell, mi_)
    bpy.data.meshes.remove(me)


def _front(x, y, z):
    """Matrice per testo nel piano XZ leggibile da +Y (vista verso -Y: +X a sinistra)."""
    return Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))


# =================================================================================================================
# ufficio galleggiante (origine al centro sul piano del pontone, posa a Z -0,5)
# =================================================================================================================
UFF_POS = (158.3, 71.0, -0.5)
PONT = (5.5, 3.5, -0.60)            # semilarghezze e fondo del pontone
BOX = (5.0, 3.0, 3.0)               # semilarghezze e altezza della scatola
Z_TER = BOX[2] + 0.12               # calpestio della terrazza


def build_ufficio(coll, lod=0, name="SM_Morin_Marina_Ufficio"):
    g = G()
    px, py, pz = PONT
    bx, by, bh = BOX
    g.box(-px, px, -py, py, pz, 0.0, "PONTONE", faces=("xn", "xp", "yn", "yp"))
    g.box(-px, px, -py, py, pz, 0.0, "GRIGIO_SCURO", faces=("top",))
    if lod < 2:   # bordo in gomma/legno del pontone
        g.box(-px - 0.05, px + 0.05, -py - 0.05, py + 0.05, -0.12, 0.0, "LEGNO_BORDO", faces=("xn", "xp", "yn", "yp", "top"))
    # scatola a doghe orizzontali (UV mondo, 12 cm)
    for (x0, x1, y, o) in ((-bx, bx, by, 1), (-bx, bx, -by, -1)):
        g.quad([(x0, y, 0), (x1, y, 0), (x1, y, bh), (x0, y, bh)], None, D_, out=(0, o, 0))
    for (y0, y1, x, o) in ((-by, by, bx, 1), (-by, by, -bx, -1)):
        g.quad([(x, y0, 0), (x, y1, 0), (x, y1, bh), (x, y0, bh)], None, D_, out=(o, 0, 0))
    g.box(-bx - 0.04, bx + 0.04, -by - 0.04, by + 0.04, bh, Z_TER, "LEGNO_BORDO", faces=("xn", "xp", "yn", "yp", "bot"))
    g.box(-bx - 0.04, bx + 0.04, -by - 0.04, by + 0.04, bh, Z_TER, "GRIGIO", faces=("top",))
    # insegna sul fronte (+Y): logo tondo a sinistra (vista) e lettere bianche in rilievo
    e = 0.012
    M = Matrix.Translation((3.55, by + 0.03, 1.95)) @ Matrix.Rotation(math.radians(-90), 4, "X")
    g.lathe([(0.55, 0.0), (0.55, 0.03), (0.0, 0.03)], (32, 20, 12)[lod], "BLU_OMBRA", mat=M, cap_top=False)
    M2 = Matrix.Translation((3.55, by + 0.075, 1.95)) @ Matrix.Rotation(math.radians(-90), 4, "X")

    def disc(bm, M2=M2, n=(32, 20, 12)[lod]):
        f = bm.faces.new([bm.verts.new(M2 @ Vector((0.55 * math.cos(2 * math.pi * k / n), 0.55 * math.sin(2 * math.pi * k / n),
                                                    0))) for k in range(n)])
        f.normal_update()
        if f.normal.y < 0:
            f.normal_flip()
    g.new_faces(disc, "LOGO")
    _text(g, NOME, 0.62, _front(-0.55, by + e, 2.05), "BIANCO", F_SERIF_B, res=(2, 1, 1)[lod])
    if lod < 2:
        _text(g, SOTTO, 0.24, _front(-0.55, by + e, 1.48), "BIANCO", F_SERIF_B, res=(2, 1, 1)[lod])
    # lato mare e fianchi [S]: finestre, porta verso la passerella (-X)
    for x in (-3.0, 0.0, 3.0):
        g.quad([(x + 0.7, -by - e, 0.9), (x - 0.7, -by - e, 0.9), (x - 0.7, -by - e, 2.2), (x + 0.7, -by - e, 2.2)], "VETRO",
               out=(0, -1, 0))
    g.quad([(-bx - e, -0.45, 0.0), (-bx - e, 0.45, 0.0), (-bx - e, 0.45, 2.1), (-bx - e, -0.45, 2.1)], "VETRO", out=(-1, 0, 0))
    g.quad([(bx + e, -0.8, 1.0), (bx + e, 0.8, 1.0), (bx + e, 0.8, 2.1), (bx + e, -0.8, 2.1)], "VETRO", out=(1, 0, 0))
    # terrazza: candelieri inox ogni ~1 m, due cavi, tendina bianca a punta
    sides = (6, 4, 3)[lod]
    rx, ry = bx - 0.08, by - 0.08
    per = [(-rx, -ry), (rx, -ry), (rx, ry), (-rx, ry), (-rx, -ry)]
    step = 1.0 if lod < 2 else 2.5
    for (xa, ya), (xb, yb) in zip(per[:-1], per[1:]):
        L = math.hypot(xb - xa, yb - ya)
        n = max(1, int(round(L / step)))
        for k in range(n):
            t = k / n
            x, y = xa + (xb - xa) * t, ya + (yb - ya) * t
            g.tube([(x, y, Z_TER), (x, y, Z_TER + 1.0)], 0.02, sides, "INOX", cap=False)
    for z in ((Z_TER + 0.98, Z_TER + 0.55) if lod < 2 else (Z_TER + 0.98,)):
        g.tube([(x, y, z) for x, y in per], 0.008 if lod < 2 else 0.015, 3, "CORDA" if z < Z_TER + 0.9 else "INOX")
    tx, ty, ts = 3.2, -1.3, 0.8
    g.hull([(tx - ts, ty - ts, Z_TER), (tx + ts, ty - ts, Z_TER), (tx + ts, ty + ts, Z_TER), (tx - ts, ty + ts, Z_TER),
            (tx, ty, Z_TER + 1.6)], "TENDA")
    # catene d'ormeggio
    if True:   # anche nei LOD: definiscono la sagoma (bbox)
        for x, y in ((-px + 0.2, -py + 0.2), (px - 0.2, -py + 0.2)):
            g.tube([(x, y, -0.1), (x * 1.08, y * 1.3, -1.6)], 0.02, 3, "SCURO", cap=False)
    return _local_mats(g.finish(name + _sfx(lod), coll))


def ucx_ufficio(coll, name="SM_Morin_Marina_Ufficio"):
    px, py, pz = PONT
    bx, by, bh = BOX
    boxes = [(-px, px, -py, py, pz, 0.0), (-bx - 0.04, bx + 0.04, -by - 0.04, by + 0.04, 0.0, Z_TER),
             (-bx, bx, by - 0.12, by - 0.04, Z_TER, Z_TER + 1.0), (-bx, bx, -by + 0.04, -by + 0.12, Z_TER, Z_TER + 1.0),
             (bx - 0.12, bx - 0.04, -by, by, Z_TER, Z_TER + 1.0), (-bx + 0.04, -bx + 0.12, -by, by, Z_TER, Z_TER + 1.0),
             (2.4, 4.0, -2.1, -0.5, Z_TER, Z_TER + 1.2)]
    pk._ucx(name, boxes, coll)
    return len(boxes)


# =================================================================================================================
# portale d'ingresso (origine al centro della base, fronte verso la citta' +Y)
# =================================================================================================================
POR_POS = (151.0, 81.2, 0.0)
UP_X, UP_W, UP_H = 1.10, 0.18, 3.0          # montanti: filo interno a +-0,92 (luce 1,84 + spessori ~ 2,2 tra gli assi)
ARCH = (2.25, 2.95)
LEAF_H = (0.05, 2.05)
PIL_P = (1.10, 1.50, 0.12, 2.40)            # pilastro +X: x0, x1, semiprofondita', altezza
PIL_M = (-1.70, -1.10, 0.15, 2.40)          # pilastro -X
FOTO_W = (-0.12, -1.62)                     # pannello con la foto d'epoca: y da/a, sul fianco del pilastro +X
ANTA_APERTA = 70.0                          # anta -X aperta verso il mare (si entra nella marina: pontili calpestabili)


def _leaf(g, M, lod):
    """Anta 0,92 x 2,0: pannello pieno in basso (0,8) con emblema, sbarre in alto. Riferimento: cerniera in (0,0), anta
    lungo +x, piano y = 0."""
    w, z0, z1 = 0.90, LEAF_H[0], LEAF_H[1]
    t = 0.05
    for b in ((0, t, -0.03, 0.03, z0, z1), (w - t, w, -0.03, 0.03, z0, z1), (t, w - t, -0.03, 0.03, z1 - t, z1),
              (t, w - t, -0.03, 0.03, 0.85, 0.85 + t)):
        g.box(*b, None, B_, mat=M)
    g.box(t, w - t, -0.015, 0.015, z0, 0.85, None, B_, faces=("yn", "yp", "bot"), mat=M)
    nb = 8 if lod < 2 else 4
    for k in range(nb):
        x = t + (w - 2 * t) * (k + 0.5) / nb
        g.box(x - 0.012, x + 0.012, -0.012, 0.012, 0.85 + t, z1 - t, "BLU", faces=("xn", "xp", "yn", "yp"), mat=M)
    n = (20, 12, 8)[lod]
    for o in (1, -1):
        def disc(bm, o=o):
            pts = [M @ Vector((w / 2 + 0.25 * math.cos(2 * math.pi * k / n), 0.016 * o, 0.45 + 0.25 * math.sin(2 * math.pi * k / n)))
                   for k in range(n)]
            f = bm.faces.new([bm.verts.new(p) for p in pts])
            f.normal_update()
            if f.normal.dot(M.to_3x3() @ Vector((0, o, 0))) < 0:
                f.normal_flip()
        g.new_faces(disc, "EMBLEMA")


def _ante_v1():
    xi = UP_X - UP_W
    return [Matrix.Translation((0.0, 0.0, 0.0)),
            Matrix.Translation((-xi, 0.0, 0.0)) @ Matrix.Rotation(math.radians(-ANTA_APERTA), 4, "Z")]


# v2 (2026-11-20, correzione da docs/uefn_arte.md par. 43.E): ENTRAMBE le ante aperte a 90 gradi verso il mare, cerniere 3,5 cm
# dentro il filo dei montanti; ogni anta occupa x = +-(0,855..0,915) e lascia una luce libera di 1,71 m per tutta l'altezza.
ANTA_V2 = 90.0
HINGE_V2 = 0.035


def _ante_v2():
    xh = UP_X - UP_W - HINGE_V2
    R = Matrix.Rotation(math.radians(-ANTA_V2), 4, "Z")     # +x dell'anta -> -Y (verso il mare)
    return [Matrix.Translation((xh, 0.0, 0.0)) @ R, Matrix.Translation((-xh, 0.0, 0.0)) @ R]


def build_portale(coll, lod=0, name="SM_Morin_Marina_Portale", ante=None):
    g = G()
    hw = UP_W / 2
    for x in (-UP_X + hw, UP_X - hw):
        g.box(x - hw, x + hw, -hw, hw, 0.0, UP_H, None, B_, faces=("xn", "xp", "yn", "yp", "top"))
    g.box(-UP_X, UP_X, -0.06, 0.06, ARCH[1], UP_H, None, B_, faces=("yn", "yp", "bot", "top"))
    g.box(-UP_X + UP_W, UP_X - UP_W, -0.05, 0.05, ARCH[0], ARCH[1], None, B_, faces=("yn", "yp", "bot", "top"))
    g.box(-UP_X + UP_W, UP_X - UP_W, -0.04, 0.04, LEAF_H[1] + 0.02, LEAF_H[1] + 0.10, None, B_)   # traverso sopra le ante
    _text(g, NOME, 0.30, _front(0.0, 0.052, (ARCH[0] + ARCH[1]) / 2 - 0.02), "ARGENTO", F_BOLD,
          extrude=0.01 if lod == 0 else 0.0)
    # ante: +X chiusa, -X aperta verso il mare
    for M in (ante if ante is not None else _ante_v1()):
        _leaf(g, M, lod)
    # pilastro +X con la scritta verticale, pannello con la foto d'epoca verso il mare
    x0, x1, d, h = PIL_P
    g.box(x0, x1, -d, d, 0.0, h, None, B_, faces=("xn", "xp", "yn", "top"))
    g.quad([(x0, d, 0.0), (x1, d, 0.0), (x1, d, h), (x0, d, h)], "PILASTRO", out=(0, 1, 0))
    fy0, fy1 = FOTO_W
    fx = x1 - 0.03
    g.box(fx - 0.03, fx + 0.03, fy1, fy0, 0.05, 2.25, None, B_, faces=("xn", "yn", "top", "bot"))
    g.quad([(fx + 0.031, fy0, 0.10), (fx + 0.031, fy1 + 0.05, 0.10), (fx + 0.031, fy1 + 0.05, 2.20), (fx + 0.031, fy0, 2.20)],
           "FOTO", out=(1, 0, 0))
    g.quad([(fx + 0.03, fy0, 0.05), (fx + 0.03, fy1, 0.05), (fx + 0.03, fy1, 0.10), (fx + 0.03, fy0, 0.10)], None, B_,
           out=(1, 0, 0))
    g.quad([(fx + 0.03, fy0, 2.20), (fx + 0.03, fy1, 2.20), (fx + 0.03, fy1, 2.25), (fx + 0.03, fy0, 2.25)], None, B_,
           out=(1, 0, 0))
    g.quad([(fx + 0.03, fy1, 0.10), (fx + 0.03, fy1 + 0.05, 0.10), (fx + 0.03, fy1 + 0.05, 2.20), (fx + 0.03, fy1, 2.20)],
           None, B_, out=(1, 0, 0))
    g.quad([(fx - 0.031, fy1, 0.6), (fx - 0.031, fy0, 0.6), (fx - 0.031, fy0, 1.3), (fx - 0.031, fy1, 1.3)], "FOTO_RETRO",
           out=(-1, 0, 0))
    # pilastro -X: citofono, lettore di badge, cartello; pannello laterale blu verso il mare
    x0, x1, d, h = PIL_M
    g.box(x0, x1, -d, d, 0.0, h, None, B_, faces=("xn", "xp", "yn", "yp", "top"))
    e = 0.01
    for (xa, xb, za, zb, cell) in ((-1.55, -1.30, 1.70, 2.075, "CARTELLO_VS"), (-1.50, -1.38, 1.05, 1.29, "CITOFONO"),
                                   (-1.50, -1.40, 1.36, 1.46, "BADGE")):
        if cell != "CARTELLO_VS":
            g.box(min(xa, xb), max(xa, xb), d, d + 0.04, za, zb, "GRIGIO", faces=("xn", "xp", "top", "bot"))
        yy = d + (0.041 if cell != "CARTELLO_VS" else e)
        g.quad([(xa, yy, za), (xb, yy, za), (xb, yy, zb), (xa, yy, zb)], cell, out=(0, 1, 0))
    g.box(x0, x0 + 0.05, -1.15, -d, 0.0, h, None, B_, faces=("xn", "xp", "yn", "top"))
    # piastre di base
    g.box(-1.75, 1.55, -0.20, 0.20, 0.0, 0.015, "GRIGIO_SCURO", faces=("top", "yn", "yp", "xn", "xp"))
    return _local_mats(g.finish(name + _sfx(lod), coll))


def ucx_portale(coll, name="SM_Morin_Marina_Portale"):
    hw = UP_W / 2
    xi = UP_X - UP_W
    boxes = [(-UP_X, -UP_X + UP_W, -hw, hw, 0.0, UP_H), (UP_X - UP_W, UP_X, -hw, hw, 0.0, UP_H),
             (-UP_X, UP_X, -0.06, 0.06, ARCH[0], UP_H),
             (0.0, xi, -0.04, 0.04, 0.0, LEAF_H[1] + 0.1),                       # anta chiusa
             (PIL_P[0], PIL_P[1], -PIL_P[2], PIL_P[2], 0.0, PIL_P[3]),
             (PIL_P[1] - 0.06, PIL_P[1], FOTO_W[1], FOTO_W[0], 0.0, 2.25),
             (PIL_M[0], PIL_M[1], -PIL_M[2], PIL_M[2], 0.0, PIL_M[3]),
             (PIL_M[0], PIL_M[0] + 0.05, -1.15, -PIL_M[2], 0.0, PIL_M[3])]
    pk._ucx(name, boxes, coll)
    i = len(boxes)
    M = Matrix.Translation((-xi, 0.0, 0.0)) @ Matrix.Rotation(math.radians(-ANTA_APERTA), 4, "Z")
    pk._ucx_hull(name, i, [M @ Vector((x, y, z)) for x in (0.0, 0.9) for y in (-0.03, 0.03) for z in (0.0, 2.05)], coll)
    return i + 1


def ucx_portale_v2(coll, name="SM_Morin_Marina_Portale_v2"):
    """Come ucx_portale ma senza l'anta chiusa: un convesso per ciascuna anta aperta (stesse matrici della mesh)."""
    hw = UP_W / 2
    boxes = [(-UP_X, -UP_X + UP_W, -hw, hw, 0.0, UP_H), (UP_X - UP_W, UP_X, -hw, hw, 0.0, UP_H),
             (-UP_X, UP_X, -0.06, 0.06, ARCH[0], UP_H),
             (PIL_P[0], PIL_P[1], -PIL_P[2], PIL_P[2], 0.0, PIL_P[3]),
             (PIL_P[1] - 0.06, PIL_P[1], FOTO_W[1], FOTO_W[0], 0.0, 2.25),
             (PIL_M[0], PIL_M[1], -PIL_M[2], PIL_M[2], 0.0, PIL_M[3]),
             (PIL_M[0], PIL_M[0] + 0.05, -1.15, -PIL_M[2], 0.0, PIL_M[3])]
    pk._ucx(name, boxes, coll)
    i = len(boxes)
    for M in _ante_v2():
        pk._ucx_hull(name, i, [M @ Vector((x, y, z)) for x in (0.0, 0.9) for y in (-0.03, 0.03) for z in (0.0, 2.05)], coll)
        i += 1
    return i


def capsule_test(name="SM_Morin_Marina_Portale_v2", r=0.34, h=1.76, z0=0.02, xs=(-1.2, 1.2, 0.01), ys=(1.2, -1.6, 0.02)):
    """Capsula (raggio r, altezza totale h, base a z0) spinta lungo -Y (citta' -> mare) attraverso il portale, per ogni X.
    Collisione = distanza di un punto dell'asse della capsula (campionato ogni ~4 cm) da un convesso UCX < r.
    Distanza esatta: 0 dentro il convesso, altrimenti minimo sui triangoli delle facce. Ritorna le X dei centri che passano
    e la luce libera equivalente (estensione dei centri + 2 r)."""
    from mathutils.geometry import closest_point_on_tri
    hulls = []
    for o in bpy.data.objects:
        if not o.name.startswith(f"UCX_{name}_"):
            continue
        b = bmesh.new()
        b.from_mesh(o.data)
        b.transform(o.matrix_world)
        b.normal_update()
        planes = [(f.normal.copy(), f.normal.dot(f.verts[0].co)) for f in b.faces]
        tris = []
        for f in b.faces:
            vs = [v.co.copy() for v in f.verts]
            tris += [(vs[0], vs[k], vs[k + 1]) for k in range(1, len(vs) - 1)]
        lo = Vector([min(v.co[i] for v in b.verts) for i in range(3)])
        hi = Vector([max(v.co[i] for v in b.verts) for i in range(3)])
        b.free()
        hulls.append((o.name, planes, tris, lo, hi))

    def dist_conv(p, planes, tris):
        if max(n.dot(p) - d for n, d in planes) <= 0:
            return 0.0
        return min((closest_point_on_tri(p, *t) - p).length for t in tris)

    nz = int((h - 2 * r) / 0.04) + 1
    zc = [z0 + r + (h - 2 * r) * k / (nz - 1) for k in range(nz)]
    ok, hit_by = [], {}
    nx = int(round((xs[1] - xs[0]) / xs[2])) + 1
    ny = int(round((ys[0] - ys[1]) / ys[2])) + 1
    for ix in range(nx):
        x = xs[0] + ix * xs[2]
        blocked = None
        for iy in range(ny):
            y = ys[0] - iy * ys[2]
            for z in zc:
                p = Vector((x, y, z))
                for nm, planes, tris, lo, hi in hulls:
                    if any(p[i] < lo[i] - r or p[i] > hi[i] + r for i in range(3)):
                        continue
                    if dist_conv(p, planes, tris) < r:
                        blocked = nm
                        break
                if blocked:
                    break
            if blocked:
                break
        if blocked:
            hit_by[round(x, 3)] = blocked
        else:
            ok.append(round(x, 3))
    if not ok:
        return dict(passa=False, centri=None, luce=0.0)
    return dict(passa=True, centri=(ok[0], ok[-1]), n=len(ok), luce=round(ok[-1] - ok[0] + 2 * r, 3),
                bordo_sx=hit_by.get(round(ok[0] - xs[2], 3)), bordo_dx=hit_by.get(round(ok[-1] + xs[2], 3)))


def build_portale_v2(lod_target=(1.0, 0.5, 0.15)):
    """Costruisce SM_Morin_Marina_Portale_v2 (+LOD1/2, UCX) accanto alla v1, che resta intatta."""
    nm = "SM_Morin_Marina_Portale_v2"
    coll = pk._coll(KIT)
    for o in list(bpy.data.objects):
        if o.name.startswith(f"UCX_{nm}_"):
            bpy.data.objects.remove(o)
    o0 = build_portale(coll, 0, nm, ante=_ante_v2())
    t0 = pk.tri_count(o0)
    objs = [o0]
    for lod in (1, 2):
        o = build_portale(coll, lod, nm, ante=_ante_v2())
        t = pk.tri_count(o)
        want = t0 * lod_target[lod]
        if t > want * 1.15:
            ratio = max(0.05, want / t)
            o = mi._decimate(o, ratio, o.name, coll)
            while av.bbox_dev(o0, o) > 0.019:
                o = build_portale(coll, lod, nm, ante=_ante_v2())
                ratio *= 1.3
                if ratio >= 0.95:
                    break
                o = mi._decimate(o, ratio, o.name, coll)
        objs.append(o)
    nucx = ucx_portale_v2(coll, nm)
    for o in coll.objects:
        if o.name.startswith(f"UCX_{nm}") or o.name.startswith(f"{nm}_LOD"):
            o.hide_render = True
            o.hide_viewport = True
    lo, hi = av.vbox(o0)
    return dict(tri=[pk.tri_count(o) for o in objs], ucx=nucx, dim=tuple(round(d, 2) for d in (hi - lo)),
                bbox_dev_pct=[round(av.bbox_dev(o0, o) * 100, 2) for o in objs[1:]])


def export_portale_v2(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    nm = "SM_Morin_Marina_Portale_v2"
    reps = []
    objs = [bpy.data.objects[nm + _sfx(l)] for l in range(3)] + \
           [o for o in bpy.data.objects if o.name.startswith(f"UCX_{nm}_")]
    state = {o.name: (o.hide_viewport, o.hide_get()) for o in objs}
    for o in objs:
        o.hide_viewport = False
        o.hide_set(False)
    bpy.context.view_layer.update()
    try:
        for lod in range(3):
            on = nm + _sfx(lod)
            reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                                overwrite=overwrite, include_ucx=(lod == 0), bake_rotation=(lod > 0),
                                                verbose=False))
    finally:
        for n, (hv, hg) in state.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps


# =================================================================================================================
# passerella v2 (stessa geometria e origine della v1: sul lato a terra, +X scende verso il galleggiante)
# =================================================================================================================
PASS_W = 2.8


def z_pass(x):
    return 0.02 - (min(max(x, 0.05), 3.55) - 0.05) * (0.45 / 3.5)


def build_passerella(coll, lod=0, name="SM_Morin_Marina_Passerella_v2"):
    g = G()
    w = PASS_W / 2
    g.box(-0.35, 0.05, -w, w, 0.0, 0.02, "GRIGIO", faces=("top", "xn", "yn", "yp"))
    g.box(3.55, 3.95, -w, w, -0.45, -0.43, "GRIGIO", faces=("top", "xp", "yn", "yp"))
    x0, x1 = 0.05, 3.55
    z0, z1 = z_pass(x0), z_pass(x1)
    yi = w - 0.10
    g.quad([(x0, -yi, z0), (x1, -yi, z1), (x1, yi, z1), (x0, yi, z0)], None, W_, out=(0, 0, 1))
    g.quad([(x0, -yi, z0 - 0.04), (x1, -yi, z1 - 0.04), (x1, yi, z1 - 0.04), (x0, yi, z0 - 0.04)], "GRIGIO", out=(0, 0, -1))
    sides = (6, 4, 3)[lod]
    for s in (-1, 1):
        ya, yb = s * yi, s * w
        for (p, q, out) in (((ya, z0 + 0.10), (ya, z0 - 0.15), (0, -s, 0)), ((yb, z0 + 0.10), (yb, z0 - 0.15), (0, s, 0))):
            g.quad([(x0, p[0], p[1]), (x1, p[0], p[1] - (z0 - z1)), (x1, q[0], q[1] - (z0 - z1)), (x0, q[0], q[1])],
                   "BLU", out=out)
        g.quad([(x0, ya, z0 + 0.10), (x1, ya, z1 + 0.10), (x1, yb, z1 + 0.10), (x0, yb, z0 + 0.10)], "BLU", out=(0, 0, 1))
        g.quad([(x0, ya, z0 - 0.15), (x1, ya, z1 - 0.15), (x1, yb, z1 - 0.15), (x0, yb, z0 - 0.15)], "BLU", out=(0, 0, -1))
        for xe, d in ((x0, -1), (x1, 1)):
            ze = z_pass(xe)
            g.quad([(xe, ya, ze - 0.15), (xe, yb, ze - 0.15), (xe, yb, ze + 0.10), (xe, ya, ze + 0.10)], "BLU", out=(d, 0, 0))
        # ringhiera blu: 3 correnti orizzontali (h 1,1), montanti
        yr = s * (w - 0.05)
        for hz in ((1.10, 0.70, 0.35) if lod < 2 else (1.10,)):
            g.tube([(0.10, yr, z_pass(0.10) + hz), (3.50, yr, z_pass(3.50) + hz)], 0.025 if hz > 1 else 0.018, sides, "BLU")
        for xp in ((0.10, 1.25, 2.40, 3.50) if lod < 2 else (0.10, 3.50)):
            g.tube([(xp, yr, z_pass(xp) + 0.10), (xp, yr, z_pass(xp) + 1.10)], 0.024, sides, "BLU", cap=False)
    return _local_mats(g.finish(name + _sfx(lod), coll))


def ucx_passerella(coll, name="SM_Morin_Marina_Passerella_v2"):
    w = PASS_W / 2
    top = [(-0.35, 0.02), (0.05, 0.02), (3.55, -0.43), (3.95, -0.43)]
    pk._ucx_hull(name, 0, [Vector((x, s * w, z)) for x, z in top for s in (-1, 1)] +
                 [Vector((x, s * w, z - 0.15)) for x, z in top for s in (-1, 1)], coll)
    for i, s in enumerate((-1, 1)):
        ya, yb = s * (w - 0.10), s * w
        pk._ucx_hull(name, 1 + i, [Vector((x, y, z_pass(x) + dz)) for x in (0.05, 3.55) for y in (ya, yb)
                                   for dz in (0.0, 1.15)], coll)
    return 3


# =================================================================================================================
# bitta a colonna arrugginita
# =================================================================================================================
BITTA_POS = (147.5, 80.4, 0.0)
PROF_BITTA = [(0.20, 0.0), (0.20, 0.05), (0.155, 0.08), (0.15, 0.32), (0.175, 0.335), (0.175, 0.375), (0.15, 0.39),
              (0.15, 0.61), (0.19, 0.63), (0.19, 0.69), (0.17, 0.70), (0.0, 0.71)]


def build_bitta(coll, lod=0, name="SM_Banchina_Bitta_Ruggine"):
    n = (16, 12, 8)[lod]
    prof = PROF_BITTA if lod < 2 else [PROF_BITTA[i] for i in (0, 2, 3, 7, 8, 9, 11)]
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    rings = []
    for r, z in prof:
        ring = [bm.verts.new((r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), z)) for k in range(n)]
        rings.append(ring)
    vt = [z / 0.71 for _, z in prof]
    for j in range(len(rings) - 1):
        a, b = rings[j], rings[j + 1]
        for k in range(n):
            k1 = (k + 1) % n
            f = bm.faces.new([a[k], a[k1], b[k1], b[k]])
            us = (2.0 * k / n, 2.0 * (k + 1) / n)
            for lp, (u, v) in zip(f.loops, ((us[0], vt[j]), (us[1], vt[j]), (us[1], vt[j + 1]), (us[0], vt[j + 1]))):
                lp[uv].uv = (u, v)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)   # anello in cima con r=0: si chiude a punta
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = pk._finish(name + _sfx(lod), bm, [MAT_R], coll, uv=None, smooth_angle=40.0)
    return _local_mats(o)


# =================================================================================================================
# build, verifiche, CSV, contesto, export
# =================================================================================================================
ASSETS = ["SM_Morin_Marina_Ufficio", "SM_Morin_Marina_Portale", "SM_Morin_Marina_Passerella_v2", "SM_Banchina_Bitta_Ruggine"]
BUILDERS = {"SM_Morin_Marina_Ufficio": build_ufficio, "SM_Morin_Marina_Portale": build_portale,
            "SM_Morin_Marina_Passerella_v2": build_passerella, "SM_Banchina_Bitta_Ruggine": build_bitta}
UCX = {"SM_Morin_Marina_Ufficio": ucx_ufficio, "SM_Morin_Marina_Portale": ucx_portale,
       "SM_Morin_Marina_Passerella_v2": ucx_passerella,
       "SM_Banchina_Bitta_Ruggine": lambda coll, name="SM_Banchina_Bitta_Ruggine":
       pk._ucx(name, [(-0.2, 0.2, -0.2, 0.2, 0.0, 0.71)], coll)}


def build_all(lod_target=(1.0, 0.5, 0.15)):
    coll = pk._coll(KIT)
    for o in list(coll.objects):
        if o.name.startswith("UCX_"):
            bpy.data.objects.remove(o)
    rep = {}
    for nm in ASSETS:
        o0 = BUILDERS[nm](coll, 0)
        t0 = pk.tri_count(o0)
        objs = [o0]
        for lod in (1, 2):
            o = BUILDERS[nm](coll, lod)
            t = pk.tri_count(o)
            want = t0 * lod_target[lod]
            if t > want * 1.15:
                ratio = max(0.05, want / t)
                o = mi._decimate(o, ratio, o.name, coll)
                while av.bbox_dev(o0, o) > 0.019:
                    o = BUILDERS[nm](coll, lod)
                    ratio *= 1.3
                    if ratio >= 0.95:
                        break
                    o = mi._decimate(o, ratio, o.name, coll)
            objs.append(o)
        UCX[nm](coll)
        lo, hi = av.vbox(o0)
        rep[nm] = [pk.tri_count(o) for o in objs] + [tuple(round(d, 2) for d in (hi - lo))]
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    return rep


def check_all():
    res = {}
    for nm in ASSETS:
        o0 = bpy.data.objects[nm]
        devs = [round(av.bbox_dev(o0, bpy.data.objects[f"{nm}_LOD{l}"]) * 100, 2) for l in (1, 2)]
        zmin = -0.1 if "Ufficio" in nm else (-0.5 if "Passerella" in nm else 0.0)
        hits, back, bad = av.ray_test(o0, zmin=zmin)
        nucx = len([o for o in bpy.data.objects if o.name.startswith(f"UCX_{nm}_")])
        lo, hi = av.vbox(o0)
        res[nm] = dict(tri=[pk.tri_count(bpy.data.objects[nm + _sfx(l)]) for l in range(3)], bbox_dev_pct=devs,
                       ray=(back, hits), bad=bad[:10], ucx=nucx, dim=tuple(round(d, 2) for d in (hi - lo)))
    return res


def yq(x):
    return 80.2663 - 0.002166 * (x - 44.0)


PASSERELLE = (("Spina", 151.1), ("L_Gamba", 105.4), ("NE", 289.6))


def layout():
    rows = [("SM_Morin_Marina_Portale", "Marina_Portale", *POR_POS, 0.0),
            ("SM_Morin_Marina_Ufficio", "Marina_Ufficio", *UFF_POS, 0.0),
            ("SM_Banchina_Bitta_Ruggine", "Bitta_Ruggine_00", *BITTA_POS, 0.0)]
    for nm, x in PASSERELLE:
        rows.append(("SM_Morin_Marina_Passerella_v2", f"Marina_Passerella_v2_{nm}", x, yq(x), 0.0, -90.0))
    return rows


def write_csv(path="exports/marina/marina_ingresso_v1.csv"):
    lines = ["asset,nome,x,y,z,yaw,pitch,roll"]
    for a, n, x, y, z, rz in layout():
        yaw = -rz if rz else 0.0
        lines.append(f"{a},{n},{x * 100:.1f},{-y * 100:.1f},{z * 100:.1f},{yaw:.2f},0.00,0.00")
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return lines


def build_context():
    coll = pk._coll(CTX)
    for a, n, x, y, z, rz in layout():
        on = f"MIN_{n}"
        o = bpy.data.objects.get(on)
        if o is None:
            o = bpy.data.objects.new(on, bpy.data.objects[a].data)
            coll.objects.link(o)
        o.data = bpy.data.objects[a].data
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(rz))
    return len(coll.objects)


def export_all(overwrite=False):
    import importlib
    import morin_export
    importlib.reload(morin_export)
    coll = bpy.data.collections[KIT]
    hidden = {o.name: (o.hide_viewport, o.hide_get()) for o in bpy.context.scene.objects}
    for o in coll.objects:
        o.hide_viewport = False
        o.hide_set(False)
    bpy.context.view_layer.update()
    reps = []
    try:
        for nm in ASSETS:
            for lod in range(3):
                on = nm + _sfx(lod)
                reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                                    overwrite=overwrite, include_ucx=(lod == 0), bake_rotation=(lod > 0),
                                                    verbose=False))
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps
