"""morin_marina.py — marina del Blocco 1: barche, pontili, passerella, colonnina, circolo nautico (v1, 2026-11-20).

Scheda: ref/marina_blocco1.md (geometria OSM, layout, tipi, misure [S]). Decisioni dell'utente 2026-11-20:
pontili e passerelle calpestabili (UCX semplici), barche senza collisione (scenografia).

Asset nuovi
  SM_Morin_Barca_<Tipo>_<Variante>[_Prua]   Gommone 5 m, Gozzo 6 m, Motoscafo 7,5 m, Vela9 9 m. 3 varianti per tipo
        (colore / tela / nome sullo specchio di poppa), stessa geometria, cambiano solo le UV nell'atlante unico
        T_Morin_Marina (2048, 8 x 8 celle da 256 px) -> un solo materiale M_Morin_Marina, HISM per mesh in UEFN.
        Gommone e Gozzo hanno anche la versione _Prua (ormeggio di prua: cime verso prua). Origine al galleggiamento
        al centro, +X = prua. LOD0/1/2 costruiti per sezioni (non decimati), stessa sagoma. Nessun UCX.
  SM_Morin_Marina_Pontile12     galleggiante 12 x 2,8 m, calpestio a Z 0 locale (posa a Z -0,45). UCX. LOD.
  SM_Morin_Marina_PontileLargo  pontile fisso 34,7 x 5 m su pali, calpestio a Z 0. UCX.
  SM_Morin_Marina_Passerella    rampa 2,8 m dal ciglio (Z 0) al galleggiante (Z -0,45): pendenza nella mesh. UCX. LOD.
  SM_Morin_Marina_Colonnina     colonnina acqua/luce 1,16 m. UCX. LOD.
  SM_Morin_Marina_Circolo       sede del circolo su palafitta ~16 x 10 m + terrazza, insegna inventata. UCX.
  SM_Mirabello_Pontile_Col      il modulo da 48 m di Mirabello (geometria identica, morin_mirabello.build_pontile)
                                con UCX sul calpestio e sulle colonnine.
  SM_Morin_Marina_Raccordo      galleggiante tondo di giunzione (16-gono, apotema 1,42 m) per gomiti e nodi. UCX. LOD.

Layout pontili v3 (radici sul bordo reale della spina, raccordi, segmenti coperti fino in fondo):
    mr.write_csv_v3(); prow, info = mr.pontili_rows_v3(); mr.verify_v3(prow); mr.boats_clearance_v3(prow)

Esegui dentro blender/arte_marina.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_marina as mr; importlib.reload(mr)
    mr.make_textures(); mr.build_materials(); mr.build_all(); mr.report()
    mr.write_csv(); mr.build_context(); mr.export_all()

Convenzioni: Blender in metri, CSV in coordinate UE (X*100, -Y*100, Z*100), yaw UE = -rotZ Blender.
"""
import math
import os
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import morin_pav_kit as pk
import morin_texphoto as tp
import morin_molo as mm
import morin_imbarco as mi
import morin_mirabello as mb

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/marina"
KIT = "MARINA_Kit"
CTX = "MARINA_Contesto"
EXPDIR = "//../exports/marina"
TEX = "T_Morin_Marina"
MAT = "M_Morin_Marina"
MAT_W = "M_Morin_Imbarco_Legno"
NPX, NG = 2048, 8
CPX = NPX // NG
INS = 5.0 / CPX                 # margine interno della cella (in unita' di cella)
Z_ACQUA = -1.03                 # pelo dell'acqua (scheda §5.2)
Z_DECK = -0.45                  # calpestio dei galleggianti [S]
PONT_W = 2.8
BOTT = 0.08                     # bottazzo in gomma sui fianchi del pontile
D_PONT = 0.45                   # distacco fra l'estremo della barca e il fianco del pontile (bottazzo)

# =================================================================================================================
# atlante
# =================================================================================================================
W = (0.90, 0.91, 0.90)
NAVY = (0.07, 0.12, 0.28)
BLU = (0.10, 0.20, 0.42)
BEIGE = (0.78, 0.71, 0.56)
GRIGIO_T = (0.56, 0.57, 0.58)
TXT_NAVY = (0.05, 0.09, 0.22)

# cella: (rgb sRGB, variazione, rugosita', metallo, motivo)
SHARED = {
    "BIANCO": (W, 0.02, 0.30, 0.0, "gelcoat"),
    "ANTIVEG": ((0.40, 0.10, 0.08), 0.05, 0.75, 0.0, None),
    "ACCIAIO": ((0.72, 0.73, 0.74), 0.04, 0.28, 1.0, None),
    "GOMMA": ((0.05, 0.05, 0.05), 0.02, 0.85, 0.0, None),
    "VETRO": ((0.10, 0.14, 0.18), 0.02, 0.06, 0.5, "vetro"),
    "TEAK": ((0.50, 0.34, 0.19), 0.06, 0.65, 0.0, "teak"),
    "ANTISCIVOLO": ((0.84, 0.84, 0.82), 0.03, 0.70, 0.0, "diamante"),
    "CUSCINO": ((0.87, 0.85, 0.79), 0.03, 0.80, 0.0, "cuscino"),
    "LEGNO": ((0.46, 0.24, 0.11), 0.06, 0.35, 0.0, "venatura"),
    "CIMA": ((0.88, 0.88, 0.84), 0.04, 0.85, 0.0, "cima"),
    "MOTORE_NERO": ((0.06, 0.06, 0.07), 0.02, 0.35, 0.0, None),
    "MOTORE_BIANCO": ((0.93, 0.93, 0.93), 0.02, 0.30, 0.0, None),
    "SCURO": ((0.08, 0.08, 0.09), 0.02, 0.45, 0.2, None),
    "ALLUMINIO": ((0.76, 0.77, 0.79), 0.03, 0.40, 1.0, None),
    "VELA": ((0.88, 0.88, 0.85), 0.04, 0.85, 0.0, "tela"),
    "PARETE": ((0.20, 0.14, 0.10), 0.06, 0.70, 0.0, "doghe_v"),
    "TETTO": ((0.74, 0.74, 0.72), 0.04, 0.85, 0.0, None),
    "CEMENTO": ((0.56, 0.55, 0.53), 0.06, 0.90, 0.0, "cemento"),
    "FINESTRA": ((0.10, 0.13, 0.16), 0.02, 0.10, 0.4, "finestra"),
    "PORTA": ((0.10, 0.13, 0.16), 0.02, 0.10, 0.4, "porta"),
    "LUCE": ((0.25, 0.80, 0.35), 0.02, 0.20, 0.0, None),
    "GRIGIO": ((0.32, 0.33, 0.34), 0.04, 0.55, 0.0, None),
    "BANNER": ((0.10, 0.30, 0.62), 0.02, 0.55, 0.0, "testo"),
}
INSEGNA = dict(cells=(0, 7, 4), bg=(0.68, 0.08, 0.06), fg=(0.97, 0.96, 0.92), size=(9.0, 1.0),
               righe=[("CIRCOLO NAUTICO VENTO CONTRARIO", 0.46, 0.62), ("SOCI, VELE E MUGUGNI DAL 1972", 0.17, 0.22)])
BANNER = dict(size=(2.0, 1.2), righe=[("SCUOLA", 0.30, 0.68), ("VELA", 0.30, 0.30)])

# tipi di barca: varianti (nome, celle proprie, alias verso celle comuni, nome sullo specchio, colore testo)
TELA_S = lambda c: (c, 0.04, 0.80, 0.0, "tela")
SCAFO_S = lambda c: (c, 0.02, 0.30, 0.0, "gelcoat")
TIPI = {
    "Gommone": dict(
        base=dict(SCAFO="BIANCO", FASCIA="BIANCO", DECK="ANTISCIVOLO", MOTORE="MOTORE_NERO", TUGA="BIANCO"),
        nome_wh=(0.42, 0.18),
        var=[("Grigio", dict(TUBO=((0.42, 0.43, 0.45), 0.03, 0.55, 0.0, "tubo")), {}, "SGABEO", W, TXT_NAVY),
             ("Nero", dict(TUBO=((0.07, 0.07, 0.08), 0.02, 0.55, 0.0, "tubo")), {}, "BOLLICINA", W, TXT_NAVY),
             ("Rosso", dict(TUBO=((0.60, 0.10, 0.08), 0.03, 0.55, 0.0, "tubo")), {}, "MUGUGNO", W, TXT_NAVY)]),
    "Gozzo": dict(
        base=dict(GUNWALE="LEGNO", INTERNO="BIANCO", DECK="TEAK", FLOOR="TEAK", TUGA="BIANCO"),
        nome_wh=(0.80, 0.20),
        var=[("FasciaAzzurra", dict(SCAFO=SCAFO_S(W), FASCIA=SCAFO_S((0.22, 0.52, 0.78)), TELA=TELA_S(BLU)), {},
              "MESCIUA", W, TXT_NAVY),
             ("FasciaVerde", dict(SCAFO=SCAFO_S(W), FASCIA=SCAFO_S((0.08, 0.40, 0.24)), TELA=TELA_S(BEIGE)), {},
              "ZIA PINA", W, TXT_NAVY),
             ("Legno", dict(SCAFO=((0.55, 0.31, 0.14), 0.06, 0.35, 0.0, "venatura"), FASCIA=SCAFO_S(W),
                            TELA=TELA_S(BLU)), dict(INTERNO="LEGNO"), "MUSCOLO FELICE", (0.55, 0.31, 0.14),
              (0.96, 0.92, 0.80))]),
    "Motoscafo": dict(
        base=dict(FASCIA="SCAFO", DECK="ANTISCIVOLO", GUNWALE="BIANCO", INTERNO="BIANCO", FLOOR="TEAK",
                  MOTORE="MOTORE_BIANCO", TUGA="BIANCO"),
        nome_wh=(1.10, 0.25),
        var=[("TelaBlu", dict(SCAFO=SCAFO_S(W), TELA=TELA_S(BLU)), {}, "FOCACCINA", W, TXT_NAVY),
             ("TelaBeige", dict(SCAFO=SCAFO_S(W), TELA=TELA_S(BEIGE)), {}, "NON CI PENSO", W, TXT_NAVY),
             ("Blu", dict(SCAFO=SCAFO_S(NAVY), TELA=TELA_S(GRIGIO_T)), {}, "ACCIUGA RAZZO", NAVY, W)]),
    "Vela9": dict(
        base=dict(FASCIA="SCAFO", DECK="ANTISCIVOLO", GUNWALE="BIANCO", INTERNO="BIANCO", FLOOR="TEAK",
                  TUGA="BIANCO"),
        nome_wh=(1.60, 0.38),
        var=[("CoprirandaBlu", dict(SCAFO=SCAFO_S(W), TELA=TELA_S(BLU)), {}, "CALMA PIATTA", W, TXT_NAVY),
             ("CoprirandaGrigio", dict(SCAFO=SCAFO_S(W), TELA=TELA_S(GRIGIO_T)), {}, "SCIROCCO PIGRO", W, TXT_NAVY),
             ("Blu", dict(SCAFO=SCAFO_S(NAVY), TELA=TELA_S(BLU)), {}, "PESTO E VELA", NAVY, W)]),
}
PRUA_TIPI = ("Gommone", "Gozzo")      # tipi che nel layout possono stare di prua al pontile


def _cell_list():
    """nome cella -> (col, riga dal basso, larghezza in celle) e specifica."""
    specs = dict(SHARED)
    for t, d in TIPI.items():
        for vn, cells, _al, nome, bg, fg in d["var"]:
            for k, s in cells.items():
                specs[f"{t}_{vn}_{k}"] = s
            specs[f"{t}_{vn}_NOME"] = ("nome", nome, bg, fg, d["nome_wh"])
    pos = {"INSEGNA": INSEGNA["cells"]}
    busy = {(c, INSEGNA["cells"][1]) for c in range(INSEGNA["cells"][0], INSEGNA["cells"][0] + INSEGNA["cells"][2])}
    free = [(c, r) for r in range(NG) for c in range(NG) if (c, r) not in busy]
    if len(specs) > len(free):
        raise RuntimeError(f"atlante pieno: {len(specs)} celle > {len(free)}")
    for (name, _s), (c, r) in zip(specs.items(), free):
        pos[name] = (c, r, 1)
    return pos, specs


CELLS, SPECS = _cell_list()


def variant_map(tipo, vn):
    d = TIPI[tipo]
    mp = dict(d["base"])
    for vname, cells, alias, *_ in d["var"]:
        if vname != vn:
            continue
        for k in cells:
            mp[k] = f"{tipo}_{vn}_{k}"
        mp["NOME"] = f"{tipo}_{vn}_NOME"
        mp.update(alias)
    return mp


def _res(name, mp):
    for _ in range(6):
        if name in mp:
            name = mp[name]
        elif name in CELLS:
            return name
        else:
            break
    if name in CELLS:
        return name
    raise KeyError(f"cella logica non risolta: {name}")


# ---------------------------------------------------------------------------------------------------------------
# pittura delle celle
# ---------------------------------------------------------------------------------------------------------------
def _text_mask(righe, W_, H_, ss=2):
    """Maschera (H_, W_) riga 0 = basso con il testo (font interno di Blender) rasterizzato. righe: (testo, h, yc)."""
    Wp, Hp = W_ * ss, H_ * ss
    mask = np.zeros((Hp, Wp), np.float32)
    yy, xx = np.mgrid[0:Hp, 0:Wp].astype(np.float32) + 0.5
    for body, hfrac, yc in righe:
        cu = bpy.data.curves.new("_tmp_txt", "FONT")
        cu.body = body
        cu.size = 1.0
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.resolution_u = 4
        ob = bpy.data.objects.new("_tmp_txt", cu)
        bpy.context.scene.collection.objects.link(ob)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        me.calc_loop_triangles()
        co = np.array([v.co[:2] for v in me.vertices], np.float64)
        tris = np.array([t.vertices[:] for t in me.loop_triangles], np.int64)
        bpy.data.meshes.remove(me)
        if len(tris) == 0:
            continue
        (x0, y0), (x1, y1) = co.min(0), co.max(0)
        s = hfrac * Hp / max(y1 - y0, 1e-6)
        if (x1 - x0) * s > 0.92 * Wp:
            s = 0.92 * Wp / (x1 - x0)
        px = (co[:, 0] - (x0 + x1) / 2) * s + Wp / 2
        py = (co[:, 1] - (y0 + y1) / 2) * s + yc * Hp
        for t in tris:
            ax, bx, cx = px[t]
            ay, by, cy = py[t]
            i0, i1 = int(max(min(ax, bx, cx) - 1, 0)), int(min(max(ax, bx, cx) + 2, Wp))
            j0, j1 = int(max(min(ay, by, cy) - 1, 0)), int(min(max(ay, by, cy) + 2, Hp))
            if i1 <= i0 or j1 <= j0:
                continue
            X = xx[j0:j1, i0:i1]
            Y = yy[j0:j1, i0:i1]
            d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(d) < 1e-12:
                continue
            l1 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / d
            l2 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / d
            ins = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
            mask[j0:j1, i0:i1] = np.maximum(mask[j0:j1, i0:i1], ins.astype(np.float32))
    return mask.reshape(H_, ss, W_, ss).mean(axis=(1, 3))


def _squeeze(mask_wide, n=CPX, w_cells=1):
    """Ricampiona la maschera larga (n, n*aspetto) nella cella (n, n*w_cells)."""
    return tp.resize(mask_wide[..., None], n * w_cells, n)[..., 0]


def _paint(spec, seed, w=CPX, h=CPX):
    rgb0, var, rough, metal, pat = spec
    big = mi._smooth_noise(h, w, 6, seed)
    fine = mi._fine(h, w, seed + 1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    yy, xx = (yy + 0.5) / h, (xx + 0.5) / w
    k = 1.0 + var * (0.7 * big + 0.3 * fine)
    rgb = np.dstack([np.full((h, w), c, np.float32) for c in rgb0]) * k[..., None]
    H = 0.5 + 0.02 * fine
    R = np.full((h, w), rough, np.float32) + 0.04 * big
    M = np.full((h, w), metal, np.float32)
    if pat == "gelcoat":
        streak = np.clip(mi._smooth_noise(h, w, 24, seed + 5) * 0.5, 0, None) * (1 - yy)
        rgb *= (1.0 - 0.04 * streak)[..., None]
    elif pat == "vetro":
        rgb *= (0.70 + 0.70 * yy)[..., None]
    elif pat == "teak":
        j = np.abs(((yy * 7) % 1.0) - 0.5) > 0.45
        rgb *= (1.0 + 0.08 * mi._smooth_noise(h, w, 30, seed + 7))[..., None]
        rgb[j] *= 0.22
        H = H - 0.3 * j
        R[j] = 0.9
    elif pat == "diamante":
        d = (np.abs(((xx * 20) % 1) - 0.5) + np.abs(((yy * 20) % 1) - 0.5)) < 0.25
        H = H + 0.12 * d
        rgb *= (1 - 0.05 * d)[..., None]
    elif pat == "cuscino":
        e = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))
        rgb *= (0.86 + 0.14 * np.clip(e / 0.12, 0, 1))[..., None]
        seam = (e < 0.025) | (np.abs(((xx * 3) % 1) - 0.5) > 0.485)
        rgb[seam] *= 0.78
        H = H + 0.15 * np.clip(e / 0.12, 0, 1) - 0.2 * seam
    elif pat == "venatura":
        g = np.sin((yy * 38 + 2.5 * mi._smooth_noise(h, w, 5, seed + 3)) * 2 * np.pi)
        rgb *= (1.0 + 0.07 * g)[..., None]
        H = H + 0.03 * g
    elif pat == "cima":
        s = np.sin((xx + yy) * 2 * np.pi * 18)
        rgb *= (0.92 + 0.08 * s)[..., None]
        H = H + 0.1 * s
    elif pat == "tela":
        fold = mi._smooth_noise(h, w, 4, seed + 11)
        rgb *= (1.0 + 0.10 * fold)[..., None]
        H = H + 0.25 * fold
    elif pat == "tubo":
        rgb *= (0.88 + 0.12 * np.sin(np.pi * yy))[..., None]
        seam = np.abs(yy - 0.5) < 0.012
        rgb[seam] *= 0.7
    elif pat == "doghe_v":
        nb = 8
        idx = np.floor(xx * nb).astype(int)
        tone = np.random.default_rng(seed).uniform(-0.08, 0.08, nb + 1)[idx]
        rgb *= (1 + tone)[..., None]
        j = np.abs(((xx * nb) % 1.0) - 0.5) > 0.46
        rgb[j] *= 0.35
        H = H - 0.3 * j
    elif pat == "cemento":
        spots = np.clip(mi._smooth_noise(h, w, 18, seed + 4) - 1.2, 0, None)
        rgb *= (1 - 0.12 * spots)[..., None]
        H = H + 0.05 * fine
    elif pat in ("finestra", "porta"):
        fr = 0.07 if pat == "finestra" else 0.06
        e = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))
        frame = (e < fr) | (np.abs(xx - 0.5) < 0.018 if pat == "finestra" else (np.abs(yy - 0.45) < 0.02))
        glass = ~frame
        rgb[glass] *= (0.75 + 0.6 * yy[glass])[..., None]
        rgb[frame] = (0.60, 0.61, 0.62)
        M[frame] = 0.8
        R[frame] = 0.4
        H = H - 0.25 * glass
        if pat == "porta":
            hdl = (np.abs(xx - 0.16) < 0.015) & (yy > 0.38) & (yy < 0.62)
            rgb[hdl] = (0.80, 0.80, 0.80)
            M[hdl] = 1.0
    return np.clip(rgb, 0, 1), H, np.clip(R, 0.02, 1), M


def _paint_text(bg, fg, righe, size, w_cells=1, border=False, seed=0):
    """Cella (o fascia di w_cells celle) con testo. size = (larghezza, altezza) in metri del quad che la porta."""
    asp = size[0] / size[1]
    hh = CPX
    m = _text_mask(righe, int(round(hh * asp)), hh)
    m = np.clip(_squeeze(m, CPX, w_cells), 0, 1)
    w = CPX * w_cells
    rgb, H, R, M = _paint((bg, 0.02, 0.45, 0.0, None), seed, w, hh)
    if border:
        yy, xx = np.mgrid[0:hh, 0:w].astype(np.float32)
        e = np.minimum(np.minimum(xx, w - 1 - xx) / asp * w_cells, np.minimum(yy, hh - 1 - yy))
        m = np.maximum(m, ((e > 6) & (e < 10)).astype(np.float32))
    fgc = np.array(fg, np.float32)
    rgb = rgb * (1 - m[..., None]) + fgc * m[..., None]
    H = H + 0.06 * m
    return rgb, H, R, M


def make_textures(seed=20261120):
    A = np.zeros((NPX, NPX, 3), np.float32)
    H = np.zeros((NPX, NPX), np.float32)
    RO = np.zeros((NPX, NPX), np.float32)
    ME = np.zeros((NPX, NPX), np.float32)

    def put(c, r, wc, layers):
        sl = (slice(r * CPX, (r + 1) * CPX), slice(c * CPX, (c + wc) * CPX))
        A[sl], H[sl], RO[sl], ME[sl] = layers

    for i, (name, spec) in enumerate(SPECS.items()):
        c, r, wc = CELLS[name]
        if spec[0] == "nome":
            _, txt, bg, fg, wh = spec
            put(c, r, 1, _paint_text(bg, fg, [(txt, 0.50, 0.64), ("LA SPEZIA", 0.17, 0.18)], wh, seed=seed + i))
        elif name == "BANNER":
            put(c, r, 1, _paint_text(spec[0], (0.97, 0.97, 0.97), BANNER["righe"], BANNER["size"], seed=seed + i))
        else:
            put(c, r, 1, _paint(spec, seed + 17 * i))
    c, r, wc = INSEGNA["cells"]
    put(c, r, wc, _paint_text(INSEGNA["bg"], INSEGNA["fg"], INSEGNA["righe"], INSEGNA["size"], wc, border=True,
                              seed=seed + 999))
    N, ao = mm._normal_ao(H, 5.0, 3.0, 4.0)
    os.makedirs(TEXDIR, exist_ok=True)
    out = {}
    for k, a in (("D", A), ("N", N), ("ORM", mm._orm(ao, RO, ME))):
        p = f"{TEXDIR}/{TEX}_{k}.png"
        tp.save(a[::-1], p)
        out[k] = p
    return out


def build_materials():
    t = f"{TEXDIR}/{TEX}"
    pk._pbr_material(MAT, t + "_D.png", t + "_N.png", t + "_ORM.png")
    for n in mb.MATS:
        mb._lmat(n)
    mi.MAT_A, mi.MAT_W = "M_Morin_Imbarco", "M_Morin_Imbarco_Legno"
    bpy.data.materials[MAT].use_fake_user = True
    return MAT


# =================================================================================================================
# geometria: facce con cella logica, UV per variante alla fine
# =================================================================================================================
ALL6 = ("top", "bot", "xn", "xp", "yn", "yp")


class G:
    def __init__(self):
        self.bm = bmesh.new()
        self.tag = self.bm.faces.layers.int.new("cella")
        self.names = []

    def _set(self, faces, cell):
        if cell not in self.names:
            self.names.append(cell)
        c = self.names.index(cell)
        for f in faces:
            f[self.tag] = c
        return faces

    def box(self, x0, x1, y0, y1, z0, z1, cell, faces=ALL6, mat=None):
        return self._set(pk._box(self.bm, x0, x1, y0, y1, z0, z1, faces=faces, mat=mat), cell)

    def quad(self, pts, cell, out):
        f = pk._quad(self.bm, [tuple(p) for p in pts])
        f.normal_update()
        if f.normal.dot(Vector(out)) < 0:
            f.normal_flip()
        return self._set([f], cell)

    def tube(self, pts, r, sides, cell, cap=True):
        """Tubo lungo una polilinea, raggio costante o lista; normali orientate esplicitamente (niente ricalcolo)."""
        bm = self.bm
        pts = [Vector(p) for p in pts]
        n = len(pts)
        radii = list(r) if isinstance(r, (list, tuple)) else [r] * n
        tang = []
        for i in range(n):
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
            tang.append((b - a).normalized())
        up = Vector((0, 0, 1)) if abs(tang[0].z) < 0.9 else Vector((1, 0, 0))
        nrm = tang[0].cross(up).normalized()
        rings = []
        for i, p in enumerate(pts):
            if i > 0:
                nrm = (nrm - tang[i] * nrm.dot(tang[i])).normalized()
            bi = tang[i].cross(nrm)
            rings.append([bm.verts.new(p + radii[i] * (math.cos(2 * math.pi * k / sides) * nrm +
                                                       math.sin(2 * math.pi * k / sides) * bi))
                          for k in range(sides)])
        faces = []
        for i in range(n - 1):
            a, b = rings[i], rings[i + 1]
            mid = (pts[i] + pts[i + 1]) / 2
            for k in range(sides):
                k1 = (k + 1) % sides
                f = bm.faces.new([a[k], a[k1], b[k1], b[k]])
                f.normal_update()
                if f.normal.dot(f.calc_center_median() - mid) < 0:
                    f.normal_flip()
                faces.append(f)
        if cap:
            for ring, d in ((rings[0], -tang[0]), (rings[-1], tang[-1])):
                f = bm.faces.new(ring)
                f.normal_update()
                if f.normal.dot(d) < 0:
                    f.normal_flip()
                faces.append(f)
        return self._set(faces, cell)

    def solid(self, pts, cell):
        """Inviluppo convesso dei punti, normali verso l'esterno rispetto al baricentro."""
        bm = self.bm
        vs = [bm.verts.new(p) for p in pts]
        res = bmesh.ops.convex_hull(bm, input=vs)
        for g_ in res.get("geom_interior", []) + res.get("geom_unused", []):
            if isinstance(g_, bmesh.types.BMVert) and g_.is_valid and not g_.link_faces:
                bm.verts.remove(g_)
        faces = [g_ for g_ in res["geom"] if isinstance(g_, bmesh.types.BMFace)]
        c = sum((Vector(p) for p in pts), Vector()) / len(pts)
        for f in faces:
            f.normal_update()
            if f.normal.dot(f.calc_center_median() - c) < 0:
                f.normal_flip()
        return self._set(faces, cell)

    def lens(self, x0, x1, y, z0, crown, t, cell, nx=1):
        """Tela tesa (bimini/telo): guscio sottile chiuso, bombato al centro."""
        pts = []
        for x in (x0, x1):
            for zz in (0.0, t):
                pts += [(x, -y, z0 + zz), (x, y, z0 + zz), (x, 0.0, z0 + crown + zz)]
        return self.solid(pts, cell)

    def finish(self, name, coll, mp=None, smooth=None):
        mp = mp or {}
        bm = self.bm.copy()
        tag = bm.faces.layers.int.get("cella")
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
        ngons = [f for f in bm.faces if len(f.verts) > 4]
        if ngons:
            bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
        bm.normal_update()
        uv = bm.loops.layers.uv.new("UVMap")
        use_w = False
        tw = pk.TILE.get(MAT_W, 2.0)
        for f in bm.faces:
            logical = self.names[f[tag]]
            n = f.normal
            ax = max(range(3), key=lambda i: abs(n[i]))
            if logical == "LEGNO_W":
                use_w = True
                f.material_index = 1
                for lp in f.loops:
                    c = lp.vert.co
                    lp[uv].uv = (c.x / tw, c.y / tw) if ax == 2 else ((c.x + c.y) / tw, c.z / tw)
                continue
            f.material_index = 0
            cx, cy, wc = CELLS[_res(logical, mp)]
            a, b = [(1, 2), (0, 2), (0, 1)][ax]
            pts = [(lp.vert.co[a], lp.vert.co[b]) for lp in f.loops]
            u0, u1 = min(p[0] for p in pts), max(p[0] for p in pts)
            v0, v1 = min(p[1] for p in pts), max(p[1] for p in pts)
            du, dv = max(u1 - u0, 1e-6), max(v1 - v0, 1e-6)
            flip = (ax == 0 and n[0] < 0) or (ax == 1 and n[1] > 0)
            for lp, (pu, pv) in zip(f.loops, pts):
                s = (pu - u0) / du
                s = 1 - s if flip else s
                t = (pv - v0) / dv
                lp[uv].uv = ((cx + INS + s * (wc - 2 * INS)) / NG, (cy + INS + t * (1 - 2 * INS)) / NG)
        bm.faces.layers.int.remove(tag)
        mats = [MAT, MAT_W] if use_w else [MAT]
        o = pk._finish(name, bm, mats, coll, uv=None, smooth_angle=smooth)
        if use_w:
            o.data.materials[1] = mb._lmat(MAT_W)
        for l in [l for l in o.data.uv_layers if l.name != "UVMap"]:
            o.data.uv_layers.remove(l)
        return o


# =================================================================================================================
# scafo per sezioni
# =================================================================================================================
def _bl(u, ft, um):
    """semilarghezza relativa: specchio di poppa (ft) -> massimo a um -> punta di prua."""
    if u <= um:
        return ft + (1 - ft) * math.sin(math.pi / 2 * u / um)
    return max(0.03, math.sqrt(max(0.0, 1 - ((u - um) / (1 - um)) ** 2)))


class Hull:
    def __init__(self, **H):
        self.__dict__.update(H)
        self.L = self.x1 - self.x0

    def X(self, u):
        return self.x0 + u * self.L

    def shift(self, u, z):
        dx = 0.0
        ur = getattr(self, "ur", 0.8)
        if u > ur:
            dx -= self.rake * ((u - ur) / (1 - ur)) ** 1.5 * (self.zs(u) - z)
        if getattr(self, "double", False):
            us = 1 - getattr(self, "ur_s", 0.85)
            if u < us:
                dx += self.rake_s * ((us - u) / us) ** 1.5 * (self.zs(u) - z)
        return dx

    def section(self, u, lod):
        b, s, k = self.hb(u), self.zs(u), self.zk(u)
        fa, fh = getattr(self, "fascia", (0.05, 0.10))
        flo, fhi = s - fa - fh, s - fa
        if lod == 0:
            P = [(0, k), (0.5 * b, 0.45 * k), (0.87 * b, -0.03), (0.93 * b, 0.07), (0.955 * b, 0.14),
                 (0.99 * b, flo), (b, fhi), (b, s)]
            C = ["ANTIVEG", "ANTIVEG", "ANTIVEG", "SCURO", "SCAFO", "FASCIA", "SCAFO"]
        elif lod == 1:
            P = [(0, k), (0.87 * b, -0.03), (0.93 * b, 0.07), (0.99 * b, flo), (b, fhi), (b, s)]
            C = ["ANTIVEG", "ANTIVEG", "SCAFO", "FASCIA", "SCAFO"]
        else:
            P = [(0, k), (0.9 * b, 0.0), (b, s)]
            C = ["ANTIVEG", "SCAFO"]
        return P, C

    def pt(self, u, y, z, side):
        return Vector((self.X(u) + self.shift(u, z), side * y, z))

    def stations(self, lod):
        ns = {0: getattr(self, "ns", 12), 1: getattr(self, "ns1", 7), 2: 4}[lod]
        keys = self.ukeys if lod < 2 else (self.cockpit[0], self.cockpit[1]) + tuple(getattr(self, "ukeys2", ()))
        us = {round(i / ns, 4) for i in range(ns + 1)} | {round(k, 4) for k in keys if 0 < k < 1}
        out = []
        for u in sorted(us):
            if out and u - out[-1] < 0.012 and u not in self.ukeys:
                continue
            out.append(u)
        return out

    def build(self, g, lod):
        us = self.stations(lod)
        self.us = us
        for side in (-1, 1):
            secs = [self.section(u, lod) for u in us]
            for i in range(len(us) - 1):
                (Pa, C), (Pb, _) = secs[i], secs[i + 1]
                for j in range(len(Pa) - 1):
                    q = [self.pt(us[i], *Pa[j], side), self.pt(us[i + 1], *Pb[j], side),
                         self.pt(us[i + 1], *Pb[j + 1], side), self.pt(us[i], *Pa[j + 1], side)]
                    g.quad(q, C[j], (0, side, 0.0))
            P0, C0 = secs[0]
            if not getattr(self, "double", False):          # specchio di poppa
                for j in range(len(P0) - 1):
                    a, b = self.pt(0, *P0[j], side), self.pt(0, *P0[j + 1], side)
                    g.quad([a, b, Vector((b.x, 0, b.z)), Vector((a.x, 0, a.z))], C0[j], (-1, 0, 0))
        # coperta, falchetta, pozzetto
        u0, u1, zf, t = self.cockpit
        cam = 0.03
        for ua, ub in zip(us[:-1], us[1:]):
            inside = ua >= u0 - 1e-6 and ub <= u1 + 1e-6
            ya, yb = max(self.hb(ua) - t, 0.03), max(self.hb(ub) - t, 0.03)
            for s in (-1, 1):
                Pa, Pb = self.pt(ua, self.hb(ua), self.zs(ua), s), self.pt(ub, self.hb(ub), self.zs(ub), s)
                if inside:
                    Ia, Ib = Vector((Pa.x, s * ya, Pa.z)), Vector((Pb.x, s * yb, Pb.z))
                    g.quad([Pa, Pb, Ib, Ia], "GUNWALE", (0, 0, 1))
                    Fa, Fb = Vector((Pa.x, s * ya, zf)), Vector((Pb.x, s * yb, zf))
                    g.quad([Ia, Ib, Fb, Fa], "INTERNO", (0, -s, 0))
                else:
                    g.quad([Pa, Pb, Vector((Pb.x, 0, Pb.z + cam)), Vector((Pa.x, 0, Pa.z + cam))], "DECK", (0, 0, 1))
            if inside:
                xa, xb = self.X(ua), self.X(ub)
                g.quad([(xa, -ya, zf), (xb, -yb, zf), (xb, yb, zf), (xa, ya, zf)], "FLOOR", (0, 0, 1))
        for u, d in (((u0, 1), (u1, -1)) if u1 > u0 else ()):   # paratie alle estremita' del pozzetto
            x, y, z = self.X(u), max(self.hb(u) - t, 0.03), self.zs(u)
            for s in (-1, 1):
                g.quad([(x, 0, zf), (x, s * y, zf), (x, s * y, z), (x, 0, z + cam)], "INTERNO", (d, 0, 0))

    def side_y(self, u, z, lod):
        """semilarghezza della faccia di murata alla quota z (tratto lineare della sezione)."""
        P, _ = self.section(u, lod)
        for (y0, z0), (y1, z1) in zip(P[:-1], P[1:]):
            if z0 <= z <= z1 and z1 > z0:
                return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
        return P[-1][0]

    def name_side(self, g, ua, ub, z0, z1, lod, off=0.012):
        if lod == 2:          # nel LOD2 le stazioni del nome non esistono: niente nome (illeggibile a quella distanza)
            return
        for s in (-1, 1):
            q = [self.pt(ua, self.side_y(ua, z0, lod), z0, s), self.pt(ub, self.side_y(ub, z0, lod), z0, s),
                 self.pt(ub, self.side_y(ub, z1, lod), z1, s), self.pt(ua, self.side_y(ua, z1, lod), z1, s)]
            nrm = (q[1] - q[0]).cross(q[3] - q[0]).normalized()
            if nrm.y * s < 0:
                nrm = -nrm
            g.quad([p + nrm * off for p in q], "NOME", (0, s, 0))

    def name_transom(self, g, w, z0, z1, off=0.012):
        x = self.X(0) - off
        g.quad([(x, -w / 2, z0), (x, w / 2, z0), (x, w / 2, z1), (x, -w / 2, z1)], "NOME", (-1, 0, 0))


# ---------------------------------------------------------------------------------------------------------------
# dettagli comuni
# ---------------------------------------------------------------------------------------------------------------
def _fuoribordo(g, xt, zt, s, lod):
    """Fuoribordo sullo specchio (xt, zt = quota del bordo). Ritorna l'estremo poppiero."""
    xf, xr = xt - 0.12, xt - 0.12 - 0.5 * s
    zb, ztop = zt + 0.02, zt + 0.02 + 0.60 * s
    w = 0.21 * s
    pts = [(xf, -w, zb), (xf, w, zb), (xr + 0.05 * s, -w * 0.9, zb), (xr + 0.05 * s, w * 0.9, zb),
           (xf - 0.02, -w * 0.9, ztop - 0.05 * s), (xf - 0.02, w * 0.9, ztop - 0.05 * s),
           (xr, -w * 0.75, ztop - 0.12 * s), (xr, w * 0.75, ztop - 0.12 * s)]
    if lod == 0:
        pts += [(xf - 0.15 * s, -w * 0.6, ztop), (xf - 0.15 * s, w * 0.6, ztop),
                (xr + 0.12 * s, -w * 0.5, ztop - 0.02 * s), (xr + 0.12 * s, w * 0.5, ztop - 0.02 * s)]
    g.solid(pts, "MOTORE")
    g.box(xf - 0.30 * s, xf - 0.14 * s, -0.05 * s, 0.05 * s, -0.42 * s, zb, "MOTORE",
          faces=("xn", "xp", "yn", "yp", "bot"))                                               # gamba
    if lod < 2:
        g.box(xt - 0.12, xt, -0.10, 0.10, zt - 0.28, zt + 0.06, "SCURO", faces=("xn", "yn", "yp", "top", "bot"))
        g.box(xr + 0.05, xf - 0.08, -0.12 * s, 0.12 * s, -0.24 * s, -0.21 * s, "MOTORE")      # piastra anticavitazione
    return xr


def _bitta(g, x, y, z, lod, along=True):
    if lod > 1:
        return
    if along:
        g.box(x - 0.10, x + 0.10, y - 0.025, y + 0.025, z, z + 0.06, "ACCIAIO", faces=("top", "xn", "xp", "yn", "yp"))
    else:
        g.box(x - 0.025, x + 0.025, y - 0.10, y + 0.10, z, z + 0.06, "ACCIAIO", faces=("top", "xn", "xp", "yn", "yp"))


def _cime(g, a_pts, x_end, y_end, z_end, lod, sag=0.10):
    """Cime d'ormeggio dalle bitte (a_pts) al fianco del pontile (x_end). Restano in tutti i LOD (bbox)."""
    sides = {0: 4, 1: 3, 2: 3}[lod]
    for (xa, ya, za) in a_pts:
        ye = math.copysign(y_end, ya) if abs(ya) > 1e-3 else 0.0
        if lod == 0:
            m = Vector(((xa + x_end) / 2, (ya + ye) / 2, (za + z_end) / 2 - sag))
            g.tube([(xa, ya, za), tuple(m), (x_end, ye, z_end)], 0.012, sides, "CIMA", cap=False)
        else:
            g.tube([(xa, ya, za), (x_end, ye, z_end)], 0.014, sides, "CIMA", cap=False)


def _trappa(g, xa, za, x_end, lod):
    """Cima verso il corpo morto (lato opposto al pontile): scende in acqua, solo LOD0."""
    if lod == 0:
        g.tube([(xa, 0.0, za), (x_end, 0.0, za - 0.1), (x_end + math.copysign(0.05, x_end), 0.0, -0.35)], 0.012, 4,
               "CIMA", cap=False)


Z_CIMA = 0.52        # quota locale della cima sul fianco del pontile (calpestio a +0,58 sul pelo dell'acqua)


# =================================================================================================================
# barche
# =================================================================================================================
def gommone(lod, prua=False):
    g = G()
    H = Hull(x0=-2.15, x1=2.30, hb=lambda u: 0.80 * _bl(u, 0.86, 0.45),
             zs=lambda u: 0.32 + 0.10 * max(0.0, (u - 0.6) / 0.4) ** 2,
             zk=lambda u: -0.30 * (1 - max(0.0, (u - 0.55) / 0.45) ** 1.5) + 0.04 * (1 - u) ** 2,
             rake=1.0, ur=0.75, fascia=(0.03, 0.05), ns=10, ns1=6, ukeys=(0.45,), ukeys2=(0.45,),
             cockpit=(0.0, 0.0, 0.32, 0.0))
    H.build(g, lod)
    # tubolari: U dalla poppa (coni oltre lo specchio) attorno alla prua
    yt = lambda u: H.hb(u) + 0.06
    zt = lambda u: 0.50 + 0.12 * max(0.0, (u - 0.6) / 0.4) ** 2
    us = {0: [0.0, 0.12, 0.28, 0.45, 0.62, 0.76], 1: [0.0, 0.25, 0.45, 0.76], 2: [0.0, 0.45, 0.76]}[lod]
    na = {0: 7, 1: 5, 2: 3}[lod]
    side_pts = [(H.X(u), yt(u), zt(u)) for u in us]
    xc, ry, zc = H.X(0.76), yt(0.76), zt(0.76)
    rx = H.x1 + 0.12 - xc
    arc = [(xc + rx * math.cos(a), ry * math.sin(a), zc + 0.10 * math.cos(a)) for a in
           np.linspace(-math.pi / 2, math.pi / 2, na + 2)[1:-1]]
    xcone = H.x0 - 0.40
    path = [(xcone, -yt(0.0) + 0.02, zt(0) + 0.03)] + [(x, -y, z) for x, y, z in side_pts] + \
           [(x, y, z) for x, y, z in arc] + [(x, y, z) for x, y, z in reversed(side_pts)] + \
           [(xcone, yt(0.0) - 0.02, zt(0) + 0.03)]
    r = [0.17] + [0.24] * (len(path) - 2) + [0.17]
    g.tube(path, r, {0: 8, 1: 6, 2: 4}[lod], "TUBO")
    # consolle, parabrezza, sedile, prendisole
    g.solid([(0.05, -0.30, 0.32), (0.60, -0.30, 0.32), (0.05, 0.30, 0.32), (0.60, 0.30, 0.32),
             (0.05, -0.30, 1.00), (0.05, 0.30, 1.00), (0.45, -0.30, 0.95), (0.45, 0.30, 0.95)], "TUGA")
    g.solid([(0.44, -0.31, 0.95), (0.46, -0.31, 0.95), (0.44, 0.31, 0.95), (0.46, 0.31, 0.95),
             (0.29, -0.29, 1.24), (0.31, -0.29, 1.24), (0.29, 0.29, 1.24), (0.31, 0.29, 1.24)], "VETRO")
    g.box(-0.72, -0.12, -0.33, 0.33, 0.32, 0.74, "CUSCINO", faces=("top", "xn", "xp", "yn", "yp"))
    if lod < 2:
        g.solid([(1.05, -0.45, 0.32), (1.05, 0.45, 0.32), (1.95, -0.18, 0.36), (1.95, 0.18, 0.36),
                 (1.05, -0.43, 0.43), (1.05, 0.43, 0.43), (1.92, -0.16, 0.46), (1.92, 0.16, 0.46)], "CUSCINO")
    if lod == 0:
        g.tube([(-0.74, -0.30, 0.70), (-0.74, -0.30, 0.95), (-0.74, 0.30, 0.95), (-0.74, 0.30, 0.70)], 0.015, 4,
               "ACCIAIO", cap=False)                                                                  # tientibene
        g.tube([(0.02, -0.12, 1.00), (-0.04, -0.12, 1.12)], 0.17, 8, "SCURO")                     # volante
        for s in (-1, 1):                                                                           # cima tientibene
            g.tube([(H.X(u), s * (yt(u) + 0.19), zt(u) + 0.12) for u in (0.04, 0.2, 0.36, 0.52, 0.66)], 0.011, 3,
                   "CIMA", cap=False)
    xr = _fuoribordo(g, H.x0, 0.32, 0.9, lod)
    for s in (-1, 1):
        _bitta(g, H.x0 + 0.12, s * 0.55, 0.32, lod, along=False)
    zt0 = zt(0.0) + 0.20
    if not prua:
        _cime(g, [(xcone + 0.05, -(yt(0) - 0.05), zt0), (xcone + 0.05, yt(0) - 0.05, zt0)], xr - D_PONT - 0.03,
              0.85, Z_CIMA, lod)
        _trappa(g, H.x1 + 0.05, 0.62, H.x1 + 0.08, lod)
    else:
        _cime(g, [(H.x1 - 0.05, -0.12, 0.70), (H.x1 - 0.05, 0.12, 0.70)], H.x1 + 0.12 + 0.24 + D_PONT + 0.03,
              0.6, Z_CIMA, lod, sag=0.06)
        _trappa(g, xcone + 0.05, zt0, xcone - 0.10, lod)
    for s in (-1, 1):                                           # nome sui fianchi della consolle
        y = s * 0.312
        g.quad([(0.08, y, 0.62), (0.50, y, 0.62), (0.50, y, 0.80), (0.08, y, 0.80)], "NOME", (0, s, 0))
    return g


def gozzo(lod, prua=False):
    g = G()
    H = Hull(x0=-2.95, x1=2.95,
             hb=lambda u: 1.15 * max(0.03, math.sin(math.pi * (u ** 0.92)) ** 0.62),
             zs=lambda u: 0.80 + (0.22 * ((u - 0.5) / 0.5) ** 2 if u > 0.5 else 0.14 * ((0.5 - u) / 0.5) ** 2),
             zk=lambda u: min(-0.04, -0.42 * (1 - abs((u - 0.5) / 0.5) ** 4)),
             rake=0.35, ur=0.82, double=True, rake_s=0.25, ur_s=0.85, fascia=(0.05, 0.12), ns=12, ns1=7,
             ukeys=(0.14, 0.50, 0.66, 0.80), ukeys2=(0.50,), cockpit=(0.14, 0.80, 0.28, 0.06))
    H.build(g, lod)
    zb, zp = H.zs(1.0), H.zs(0.0)
    g.solid([(H.x1 - 0.12, -0.035, zb - 0.18), (H.x1 + 0.03, -0.035, zb - 0.18), (H.x1 - 0.12, 0.035, zb - 0.18),
             (H.x1 + 0.03, 0.035, zb - 0.18), (H.x1 - 0.08, -0.035, zb + 0.28), (H.x1 - 0.01, -0.035, zb + 0.28),
             (H.x1 - 0.08, 0.035, zb + 0.28), (H.x1 - 0.01, 0.035, zb + 0.28)], "GUNWALE")         # ruota di prua
    g.solid([(H.x0 - 0.02, -0.035, zp - 0.12), (H.x0 + 0.10, -0.035, zp - 0.12), (H.x0 - 0.02, 0.035, zp - 0.12),
             (H.x0 + 0.10, 0.035, zp - 0.12), (H.x0 + 0.0, -0.035, zp + 0.14), (H.x0 + 0.08, -0.035, zp + 0.14),
             (H.x0 + 0.0, 0.035, zp + 0.14), (H.x0 + 0.08, 0.035, zp + 0.14)], "GUNWALE")         # dritto di poppa
    g.box(-0.85, -0.05, -0.32, 0.32, 0.28, 0.72, "INTERNO", faces=("top", "xn", "xp", "yn", "yp"))   # cassa motore
    g.box(-0.82, -0.08, -0.30, 0.30, 0.72, 0.80, "CUSCINO", faces=("top", "xn", "xp", "yn", "yp"))
    for xa, xb in ((0.45, 0.75), (-1.95, -1.62)):                                                    # banchi
        u = (xa - H.x0) / H.L
        y = min(H.hb(u), H.hb((xb - H.x0) / H.L)) - 0.07
        g.box(xa, xb, -y, y, 0.56, 0.62, "GUNWALE", faces=("top", "bot", "xn", "xp", "yn", "yp"))
    # tendalino
    g.lens(-1.55, 0.15, 0.98, 1.66, 0.10, 0.04, "TELA")
    if lod < 2:
        for x in (-1.45, 0.05):
            u = (x - H.x0) / H.L
            for s in (-1, 1):
                g.tube([(x, s * (H.hb(u) - 0.04), H.zs(u)), (x, s * 0.95, 1.67)], 0.016, {0: 4, 1: 3}[lod],
                       "ACCIAIO", cap=False)
    for x, y in ((2.35, 0.12), (-2.35, 0.22)):
        for s in (-1, 1):
            u = (x - H.x0) / H.L
            _bitta(g, x, s * y, H.zs(u) + 0.02, lod)
    xs_eff, xb_eff = H.x0 - 0.02, H.x1 + 0.03
    zc = H.zs(0.08) + 0.08
    if not prua:
        _cime(g, [(-2.35, -0.22, zc), (-2.35, 0.22, zc)], xs_eff - D_PONT - 0.03, 0.75, Z_CIMA, lod)
        _trappa(g, 2.35, H.zs(0.9) + 0.08, H.x1 - 0.05, lod)
    else:
        _cime(g, [(2.35, -0.12, H.zs(0.9) + 0.08), (2.35, 0.12, H.zs(0.9) + 0.08)], xb_eff + D_PONT + 0.03, 0.75,
              Z_CIMA, lod)
        _trappa(g, -2.35, zc, H.x0 + 0.05, lod)
    H.name_side(g, 0.66, 0.80, 0.40, 0.62, lod)
    return g


def motoscafo(lod, prua=False):
    g = G()
    H = Hull(x0=-3.45, x1=3.65, hb=lambda u: 1.35 * _bl(u, 0.85, 0.45),
             zs=lambda u: 0.98 + 0.30 * max(0.0, (u - 0.5) / 0.5) ** 1.6,
             zk=lambda u: -0.48 * (1 - max(0.0, (u - 0.55) / 0.45) ** 1.5) + 0.06 * (1 - u) ** 2,
             rake=0.8, ur=0.78, fascia=(0.05, 0.10), ns=12, ns1=7, ukeys=(0.02, 0.06, 0.22, 0.45, 0.56), ukeys2=(0.45,),
             cockpit=(0.02, 0.56, 0.48, 0.10))
    H.build(g, lod)
    zf = 0.48
    # parabrezza avvolgente (lastre sottili chiuse)
    for s in (-1, 1):
        g.solid([(0.58, s * 0.55, 1.02), (0.60, s * 0.55, 1.02), (0.10, s * 1.20, 0.99), (0.12, s * 1.20, 0.99),
                 (0.33, s * 0.52, 1.42), (0.35, s * 0.52, 1.42), (-0.05, s * 1.12, 1.36), (-0.03, s * 1.12, 1.36)],
                "VETRO")
    g.solid([(0.58, -0.55, 1.02), (0.60, -0.55, 1.02), (0.58, 0.55, 1.02), (0.60, 0.55, 1.02),
             (0.33, -0.52, 1.42), (0.35, -0.52, 1.42), (0.33, 0.52, 1.42), (0.35, 0.52, 1.42)], "VETRO")
    if lod == 0:
        g.tube([(-0.05, -1.12, 1.37), (0.34, -0.52, 1.43), (0.34, 0.52, 1.43), (-0.05, 1.12, 1.37)], 0.016, 4,
               "ACCIAIO", cap=False)
    # consolle, volante, sedili, divanetto di poppa, prendisole
    g.solid([(-0.35, -0.85, zf), (0.40, -0.85, zf), (-0.35, -0.25, zf), (0.40, -0.25, zf),
             (-0.35, -0.85, 1.12), (-0.35, -0.25, 1.12), (0.40, -0.85, 0.98), (0.40, -0.25, 0.98)], "TUGA")
    if lod == 0:
        g.tube([(-0.28, -0.55, 1.08), (-0.36, -0.55, 1.20)], 0.18, 8, "SCURO")
    for y0, y1 in ((-0.85, -0.30), (0.25, 0.80)):
        g.box(-1.05, -0.55, y0, y1, zf, 0.95, "CUSCINO", faces=("top", "xn", "xp", "yn", "yp"))
        if lod < 2:
            g.box(-1.12, -0.98, y0, y1, 0.95, 1.32, "CUSCINO", faces=("top", "xn", "xp", "yn", "yp"))
    xb0 = H.X(0.02)
    g.box(xb0, xb0 + 0.48, -1.0, 1.0, zf, 0.86, "CUSCINO", faces=("top", "xp", "yn", "yp"))
    if lod < 2:
        g.box(xb0, xb0 + 0.14, -1.0, 1.0, 0.86, 1.16, "CUSCINO", faces=("top", "xp", "yn", "yp"))
        g.solid([(1.0, -0.85, 1.02), (1.0, 0.85, 1.02), (2.3, -0.50, 1.13), (2.3, 0.50, 1.13),
                 (1.0, -0.83, 1.12), (1.0, 0.83, 1.12), (2.27, -0.48, 1.22), (2.27, 0.48, 1.22)], "CUSCINO")
    # capottina (bimini) e archetti
    g.lens(-2.30, -0.20, 1.08, 1.94, 0.10, 0.05, "TELA")
    if lod < 2:
        for x in (-2.2, -0.3):
            u = (x - H.x0) / H.L
            for s in (-1, 1):
                g.tube([(x, s * (H.hb(u) - 0.05), H.zs(u)), (x, s * 1.05, 1.95)], 0.017, {0: 4, 1: 3}[lod],
                       "ACCIAIO", cap=False)
    # pulpito di prua (tientibene)
    if lod < 2:
        ur = [0.62, 0.72, 0.82, 0.90]
        rail = [(H.X(u), -(H.hb(u) - 0.08), H.zs(u) + 0.55) for u in ur] + \
               [(H.X(0.96), 0.0, H.zs(0.96) + 0.55)] + [(H.X(u), H.hb(u) - 0.08, H.zs(u) + 0.55) for u in reversed(ur)]
        g.tube(rail, 0.016, {0: 4, 1: 3}[lod], "ACCIAIO", cap=False)
        if lod == 0:
            for u in (0.62, 0.76, 0.90):
                for s in (-1, 1):
                    y = s * (H.hb(u) - 0.08)
                    g.tube([(H.X(u), y, H.zs(u)), (H.X(u), y, H.zs(u) + 0.55)], 0.013, 4, "ACCIAIO", cap=False)
    # plancette ai lati del motore
    g.box(H.x0 - 0.40, H.x0, 0.40, 1.05, 0.24, 0.31, "FLOOR")
    g.box(H.x0 - 0.40, H.x0, -1.05, -0.40, 0.24, 0.31, "FLOOR")
    xr = _fuoribordo(g, H.x0, 0.98, 1.2, lod)
    for x, y in ((-3.2, 1.0), (3.0, 0.25)):
        for s in (-1, 1):
            u = (x - H.x0) / H.L
            _bitta(g, x, s * y, H.zs(u), lod)
    if not prua:
        _cime(g, [(-3.2, -1.0, H.zs(0.03) + 0.05), (-3.2, 1.0, H.zs(0.03) + 0.05)], xr - D_PONT - 0.03, 1.0, Z_CIMA, lod)
        _trappa(g, 3.0, H.zs(0.94) + 0.05, H.x1 - 0.05, lod)
    H.name_side(g, 0.06, 0.22, 0.40, 0.68, lod)
    return g


def vela9(lod, prua=False):
    g = G()
    H = Hull(x0=-4.40, x1=4.55, hb=lambda u: 1.50 * _bl(u, 0.83, 0.55),
             zs=lambda u: 0.92 + 0.20 * max(0.0, (u - 0.4) / 0.6) ** 1.8,
             zk=lambda u: min(-0.05, -0.40 * (1 - max(0.0, (u - 0.6) / 0.4) ** 1.5)),
             rake=0.45, ur=0.82, fascia=(0.05, 0.10), ns=12, ns1=7, ukeys=(0.03, 0.30, 0.55), ukeys2=(0.55,),
             cockpit=(0.03, 0.30, 0.55, 0.12))
    H.build(g, lod)
    xm = 0.70
    # tuga con oblo'
    g.solid([(-1.69, -0.95, 0.90), (-1.69, 0.95, 0.90), (1.9, -0.55, 0.98), (1.9, 0.55, 0.98),
             (-1.60, -0.88, 1.40), (-1.60, 0.88, 1.40), (1.6, -0.50, 1.30), (1.6, 0.50, 1.30)], "TUGA")
    if lod < 2:
        def tside(x, z, s):            # punto sulla murata della tuga (interpolazione bilineare) + scostamento
            t = (x + 1.69) / 3.59
            yb = 0.95 + (0.55 - 0.95) * t
            yt_ = 0.88 + (0.50 - 0.88) * ((x + 1.60) / 3.2)
            zb_, zt_ = 0.90 + 0.08 * t, 1.40 - 0.10 * ((x + 1.60) / 3.2)
            w = (z - zb_) / (zt_ - zb_)
            return (x, s * (yb + (yt_ - yb) * w + 0.03), z)
        for xa, xb in ((-1.2, 0.1), (0.45, 1.2)):
            for s in (-1, 1):
                g.quad([tside(xa, 1.10, s), tside(xb, 1.10, s), tside(xb, 1.24, s), tside(xa, 1.24, s)], "SCURO",
                       (0, s, 0))
        g.solid([(-1.75, -0.85, 1.38), (-0.90, -0.80, 1.38), (-1.75, 0.85, 1.38), (-0.90, 0.80, 1.38),
                 (-1.55, -0.70, 2.00), (-1.10, -0.62, 1.98), (-1.55, 0.70, 2.00), (-1.10, 0.62, 1.98)], "TELA")
    sides = {0: 8, 1: 6, 2: 4}[lod]
    g.tube([(xm, 0, 1.30), (xm, 0, 13.0)], 0.075, sides, "ALLUMINIO")                     # albero
    g.tube([(xm - 0.05, 0, 2.15), (-3.0, 0, 2.05)], 0.06, max(4, sides - 2), "ALLUMINIO")  # boma
    g.tube([(xm - 0.15, 0, 2.36), (-1.2, 0, 2.34), (-2.85, 0, 2.28)], [0.20, 0.17, 0.11], sides, "TELA")  # copriranda
    g.tube([(H.x1 - 0.20, 0, 1.30), (xm + 0.12, 0, 12.2)], [0.09, 0.03], max(4, sides - 2), "VELA")  # fiocco avvolto
    if lod < 2:
        thin = {0: 3, 1: 3}[lod]
        g.tube([(xm, 0, 12.9), (H.x0 + 0.15, 0, H.zs(0.0) + 0.05)], 0.010, thin, "ACCIAIO", cap=False)  # paterazzo
        for s in (-1, 1):
            g.tube([(xm, 0, 12.4), (xm, s * 0.95, 6.6), (xm - 0.15, s * (H.hb(0.58) - 0.05), H.zs(0.58))], 0.010,
                   thin, "ACCIAIO", cap=False)                                                              # sartie
            g.tube([(xm, s * 0.06, 6.6), (xm, s * 0.95, 6.6)], 0.02, thin, "ALLUMINIO", cap=False)          # crocette
    if lod == 0:
        for s in (-1, 1):                                                                        # draglie e candelieri
            ul = [0.06, 0.25, 0.45, 0.65, 0.84]
            g.tube([(H.X(u), s * (H.hb(u) - 0.06), H.zs(u) + 0.60) for u in ul], 0.008, 3, "ACCIAIO", cap=False)
            for u in ul:
                y = s * (H.hb(u) - 0.06)
                g.tube([(H.X(u), y, H.zs(u)), (H.X(u), y, H.zs(u) + 0.62)], 0.012, 4, "ACCIAIO", cap=False)
        ub = [0.84, 0.92]
        g.tube([(H.X(u), -(H.hb(u) - 0.06), H.zs(u) + 0.62) for u in ub] + [(H.X(0.97), 0, H.zs(0.97) + 0.62)] +
               [(H.X(u), H.hb(u) - 0.06, H.zs(u) + 0.62) for u in reversed(ub)], 0.016, 4, "ACCIAIO", cap=False)
    for x, y in ((-4.10, 1.10), (4.10, 0.25)):
        for s in (-1, 1):
            u = (x - H.x0) / H.L
            _bitta(g, x, s * y, H.zs(u), lod)
    xs_eff = H.x0
    if not prua:
        _cime(g, [(-4.10, -1.10, H.zs(0.0) + 0.06), (-4.10, 1.10, H.zs(0.0) + 0.06)], xs_eff - D_PONT - 0.03, 1.2,
              Z_CIMA, lod)
        _trappa(g, 4.10, H.zs(0.97) + 0.06, H.x1 - 0.08, lod)
    H.name_transom(g, 1.60, 0.27, 0.65)
    return g


BUILDERS = {"Gommone": gommone, "Gozzo": gozzo, "Motoscafo": motoscafo, "Vela9": vela9}


def barca_name(tipo, vn, prua=False, lod=0):
    return f"SM_Morin_Barca_{tipo}_{vn}{'_Prua' if prua else ''}{mi._sfx(lod)}"


def build_barche(coll):
    out = {}
    for tipo, fn in BUILDERS.items():
        for prua in ((False, True) if tipo in PRUA_TIPI else (False,)):
            for lod in range(3):
                g = fn(lod, prua)
                for vn, *_ in TIPI[tipo]["var"]:
                    o = g.finish(barca_name(tipo, vn, prua, lod), coll, variant_map(tipo, vn), smooth=40)
                    out[o.name] = o
                g.bm.free()
    return out


# =================================================================================================================
# pontili, passerella, colonnina (atlante M_Morin_Imbarco come SM_Mirabello_Pontile), circolo
# =================================================================================================================
def build_pontile12(coll, lod=0, name="SM_Morin_Marina_Pontile12", L=12.0):
    """Galleggiante 12 x 2,8 m: origine alla radice sul calpestio, +X verso la punta (come SM_Mirabello_Pontile)."""
    g = mb.Geo(ref=(L / 2, 0, -0.3))
    w = PONT_W / 2
    g.box(0.0, L, -w, w, -0.55, 0.0, "GRIGIO", faces=("xn", "xp", "yn", "yp"))
    g.box(0.0, L, -w, w, -0.05, 0.0, None, mi=1, faces=("top",))
    for x in ((1.5, 4.5, 7.5, 10.5) if lod < 2 else (1.5, 10.5)):     # gallocce ogni 3 m sui due lati
        for s in (-1, 1):
            g.box(x - 0.15, x + 0.15, s * w - 0.06 * s - 0.05, s * w - 0.06 * s + 0.05, 0.0, 0.12, "ACCIAIO",
                  faces=("top", "xn", "xp", "yn", "yp"))
    g.box(0.0, L, -w - BOTT, -w, -0.35, -0.05, "GOMMA", faces=("yn", "top"))          # bottazzo
    g.box(0.0, L, w, w + BOTT, -0.35, -0.05, "GOMMA", faces=("yp", "top"))
    if lod == 0:
        for x in (3.0, 9.0):                                  # anelli d'ormeggio sul bottazzo
            for s in (-1, 1):
                y = s * (w + BOTT + 0.015)
                g.new_faces(lambda bm, x=x, y=y: _torus(bm, (x, y, -0.20), 0.07, 0.012, 6, 3), "ACCIAIO")
        for x in (0.02, L - 0.02):                            # giunti fra i moduli
            g.box(x - 0.02, x + 0.02, -w, w, -0.01, 0.005, "GOMMA", faces=("top",))
    o = g.finish(name + mi._sfx(lod), coll)
    if lod == 0:
        pk._ucx(name, [(0.0, L, -w, w, -0.55, 0.0)], coll)
    return mb._localize(o)


def build_mirabello_col(coll, lod=0, name="SM_Mirabello_Pontile_Col"):
    """LOD0 identica a SM_Mirabello_Pontile (morin_mirabello.build_pontile). LOD1/LOD2 rifatte qui perche' quelle
    di Mirabello perdono bottazzo e colonnine (bbox fuori del 2 %): stessa sezione, meno dettagli."""
    if lod == 0:
        o = mb._localize(mb.build_pontile(coll, 0, name=name))
    else:
        L, w = mb.PONT_L, mb.PONT_W / 2
        g = mb.Geo(ref=(L / 2, 0, -0.3))
        g.box(0.0, L, -w, w, -0.55, 0.0, "GRIGIO", faces=("xn", "xp", "yn", "yp"))
        g.box(0.0, L, -w, w, -0.05, 0.0, None, mi=1, faces=("top",))
        if lod == 1:
            for x in np.arange(3.0, L - 1.0, 5.0):
                for s in (-1, 1):
                    g.box(x - 0.15, x + 0.15, s * w - 0.06 * s - 0.05, s * w - 0.06 * s + 0.05, 0.0, 0.12, "ACCIAIO",
                          faces=("top", "xn", "xp", "yn", "yp"))
        for x in np.arange(5.5, L - 1.0, 10.0):
            g.box(x - 0.15, x + 0.15, -0.15, 0.15, 0.0, 1.0, "BIANCO",
                  faces=("top", "xn", "xp", "yn", "yp") if lod == 1 else ("top", "yn", "yp"))
        g.box(0.0, L, -w - 0.08, -w, -0.35, -0.05, "GOMMA", faces=("yn", "top"))
        g.box(0.0, L, w, w + 0.08, -0.35, -0.05, "GOMMA", faces=("yp", "top"))
        o = mb._localize(g.finish(name + mi._sfx(lod), coll))
    if lod == 0:
        w = mb.PONT_W / 2
        boxes = [(0.0, mb.PONT_L, -w, w, -0.55, 0.0)]
        boxes += [(x - 0.15, x + 0.15, -0.15, 0.15, 0.0, 1.0) for x in np.arange(5.5, mb.PONT_L - 1.0, 10.0)]
        pk._ucx(name, boxes, coll)
    return o


LARGO_L, LARGO_W = 34.7, 5.0


def build_largo(coll, name="SM_Morin_Marina_PontileLargo"):
    """Pontile fisso 34,7 x 5 m su pali (forse fisso: scheda §2.3 [S]); origine sul ciglio, calpestio Z 0."""
    g = mb.Geo(ref=(LARGO_L / 2, 0, -0.2))
    L, w = LARGO_L, LARGO_W / 2
    g.box(0.0, L, -w, w, -0.40, 0.0, "GRIGIO", faces=("xp", "yn", "yp", "bot"))
    g.box(0.0, L, -w, w, -0.05, 0.0, None, mi=1, faces=("top",))
    for x in np.arange(2.0, L, 4.2):
        for s in (-1, 1):
            g.new_faces(lambda bm, x=x, s=s: _tube_simple(bm, [(x, s * (w - 0.35), -0.40), (x, s * (w - 0.35), -2.2)],
                                                        0.18, 8), "GRIGIO")
    for x in np.arange(3.0, L - 1.0, 8.0):                     # bitte
        for s in (-1, 1):
            y = s * (w - 0.30)
            g.lathe([(0.12, 0.0), (0.10, 0.30), (0.16, 0.36), (0.0, 0.38)], 8, "SCURO", mat=Matrix.Translation((x, y, 0)))
    for x in np.arange(1.5, L - 0.5, 3.0):                     # gallocce
        for s in (-1, 1):
            g.box(x - 0.15, x + 0.15, s * w - 0.06 * s - 0.05, s * w - 0.06 * s + 0.05, 0.0, 0.10, "ACCIAIO",
                  faces=("top", "xn", "xp", "yn", "yp"))
    o = g.finish(name, coll)
    pk._ucx(name, [(0.0, L, -w, w, -0.40, 0.0)], coll)
    return mb._localize(o)


def _torus(bm, c, R, r, nmaj, nmin):
    """Anello nel piano XZ (asse Y), normali verso l'esterno del tubo."""
    c = Vector(c)
    rings = []
    for i in range(nmaj):
        a = 2 * math.pi * i / nmaj
        ctr = c + Vector((R * math.cos(a), 0, R * math.sin(a)))
        rad = Vector((math.cos(a), 0, math.sin(a)))
        rings.append((ctr, [bm.verts.new(ctr + r * (math.cos(2 * math.pi * k / nmin) * rad +
                                                    math.sin(2 * math.pi * k / nmin) * Vector((0, 1, 0))))
                            for k in range(nmin)]))
    for i in range(nmaj):
        (ca, a), (cb, b) = rings[i], rings[(i + 1) % nmaj]
        for k in range(nmin):
            k1 = (k + 1) % nmin
            f = bm.faces.new([a[k], a[k1], b[k1], b[k]])
            f.normal_update()
            if f.normal.dot(f.calc_center_median() - (ca + cb) / 2) < 0:
                f.normal_flip()


def _tube_simple(bm, pts, r, sides):
    """Tubo chiuso con normali esplicite (per mb.Geo)."""
    pts = [Vector(p) for p in pts]
    d = (pts[1] - pts[0]).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    nrm = d.cross(up).normalized()
    bi = d.cross(nrm)
    rings = [[bm.verts.new(p + r * (math.cos(2 * math.pi * k / sides) * nrm + math.sin(2 * math.pi * k / sides) * bi))
              for k in range(sides)] for p in pts]
    mid = (pts[0] + pts[1]) / 2
    for k in range(sides):
        k1 = (k + 1) % sides
        f = bm.faces.new([rings[0][k], rings[0][k1], rings[1][k1], rings[1][k]])
        f.normal_update()
        if f.normal.dot(f.calc_center_median() - mid) < 0:
            f.normal_flip()
    for ring, dd in ((rings[0], -d), (rings[1], d)):
        f = bm.faces.new(ring)
        f.normal_update()
        if f.normal.dot(dd) < 0:
            f.normal_flip()


PASS_L, PASS_W = 3.5, 2.8       # dal ciglio al galleggiante (scheda §2.3 [S]); larghezza = pontile


def z_pass(x):
    return 0.02 - (min(max(x, 0.05), 3.55) - 0.05) * (0.45 / 3.5)


def build_passerella(coll, lod=0, name="SM_Morin_Marina_Passerella"):
    """Rampa in alluminio con calpestio in legno dal ciglio (Z 0, x 0) al galleggiante (Z -0,45, x 3,5)."""
    g = mb.Geo(ref=(1.8, 0, -0.5))
    w = PASS_W / 2
    g.box(-0.35, 0.05, -w, w, 0.0, 0.02, "PONTE", faces=("top", "xn", "yn", "yp"))           # piastra a terra
    g.box(3.55, 3.95, -w, w, -0.45, -0.43, "PONTE", faces=("top", "xp", "yn", "yp"))         # piastra sul galleggiante
    x0, x1 = 0.05, 3.55
    z0, z1 = z_pass(x0), z_pass(x1)
    yi = w - 0.10
    # calpestio inclinato
    g.quad([(x0, -yi, z0), (x1, -yi, z1), (x1, yi, z1), (x0, yi, z0)], None, mi=1, out=(0, 0, 1))
    g.quad([(x0, -yi, z0 - 0.04), (x1, -yi, z1 - 0.04), (x1, yi, z1 - 0.04), (x0, yi, z0 - 0.04)], "ACCIAIO",
           out=(0, 0, -1))
    for s in (-1, 1):                                          # longheroni
        ya, yb = s * yi, s * w
        for (p, q, out) in (((ya, z0 + 0.10), (ya, z0 - 0.15), (0, -s, 0)), ((yb, z0 + 0.10), (yb, z0 - 0.15), (0, s, 0))):
            g.quad([(x0, p[0], p[1]), (x1, p[0], p[1] - (z0 - z1)), (x1, q[0], q[1] - (z0 - z1)), (x0, q[0], q[1])],
                   "ACCIAIO", out=out)
        g.quad([(x0, ya, z0 + 0.10), (x1, ya, z1 + 0.10), (x1, yb, z1 + 0.10), (x0, yb, z0 + 0.10)], "ACCIAIO",
               out=(0, 0, 1))
        g.quad([(x0, ya, z0 - 0.15), (x1, ya, z1 - 0.15), (x1, yb, z1 - 0.15), (x0, yb, z0 - 0.15)], "ACCIAIO",
               out=(0, 0, -1))
        for xe, d in ((x0, -1), (x1, 1)):
            ze = z_pass(xe)
            g.quad([(xe, ya, ze - 0.15), (xe, yb, ze - 0.15), (xe, yb, ze + 0.10), (xe, ya, ze + 0.10)], "ACCIAIO",
                   out=(d, 0, 0))
        # corrimano
        yr = s * (w - 0.05)
        sides = {0: 6, 1: 4, 2: 3}[lod]
        xs_post = (0.10, 1.25, 2.40, 3.50) if lod < 2 else (0.10, 3.50)
        g.new_faces(lambda bm, yr=yr, sides=sides: _tube_simple(bm, [(0.10, yr, z_pass(0.10) + 1.0),
                                                                     (3.50, yr, z_pass(3.50) + 1.0)], 0.025, sides),
                    "ACCIAIO")
        if lod < 2:
            g.new_faces(lambda bm, yr=yr: _tube_simple(bm, [(0.10, yr, z_pass(0.10) + 0.5),
                                                            (3.50, yr, z_pass(3.50) + 0.5)], 0.015, 4), "ACCIAIO")
        for xp in xs_post:
            g.new_faces(lambda bm, xp=xp, yr=yr: _tube_simple(bm, [(xp, yr, z_pass(xp) + 0.10),
                                                                   (xp, yr, z_pass(xp) + 1.0)], 0.022,
                                                              4 if lod < 2 else 3), "ACCIAIO")
    o = mb._localize(g.finish(name + mi._sfx(lod), coll))
    if lod == 0:
        top = [(-0.35, 0.02), (0.05, 0.02), (3.55, -0.43), (3.95, -0.43)]
        pk._ucx_hull(name, 0, [Vector((x, s * w, z)) for x, z in top for s in (-1, 1)] +
                     [Vector((x, s * w, z - 0.15)) for x, z in top for s in (-1, 1)], coll)
        for i, s in enumerate((-1, 1)):
            ya, yb = s * (w - 0.10), s * w
            pts = [Vector((x, y, z_pass(x) + dz)) for x in (0.05, 3.55) for y in (ya, yb) for dz in (0.0, 1.05)]
            pk._ucx_hull(name, 1 + i, pts, coll)
    return o


def build_colonnina(coll, lod=0, name="SM_Morin_Marina_Colonnina"):
    """Colonnina acqua/luce ~0,32 x 0,26 x 1,16 m: corpo bianco, cappello grigio, luce verde [S]."""
    g = G()
    g.solid([(-0.15, -0.12, 0.0), (0.15, -0.12, 0.0), (-0.15, 0.12, 0.0), (0.15, 0.12, 0.0),
             (-0.13, -0.10, 1.0), (0.13, -0.10, 1.0), (-0.13, 0.10, 1.0), (0.13, 0.10, 1.0)], "BIANCO")
    g.box(-0.16, 0.16, -0.13, 0.13, 1.0, 1.08, "GRIGIO")
    g.tube([(0, 0, 1.08), (0, 0, 1.16)], 0.06, {0: 8, 1: 6, 2: 4}[lod], "LUCE")
    if lod < 2:
        for s in (-1, 1):                                          # pannelli prese sui due fianchi
            g.quad([(-0.10, s * 0.112, 0.55), (0.10, s * 0.112, 0.55), (0.10, s * 0.106, 0.85), (-0.10, s * 0.106, 0.85)],
                   "SCURO", (0, s, 0))
    g.box(-0.04, 0.04, 0.10, 0.16, 0.30, 0.38, "ACCIAIO", faces=("top", "bot", "xn", "xp", "yp"))      # rubinetto
    o = g.finish(name + mi._sfx(lod), coll)
    if lod == 0:
        pk._ucx(name, [(-0.16, 0.16, -0.13, 0.13, 0.0, 1.16)], coll)
    return o


CIRC_C = (161.0, 72.0)          # centro in coordinate di progetto (scheda §5.1)


def build_circolo(coll, name="SM_Morin_Marina_Circolo"):
    """Sede del circolo su palafitta: terrazza 17 x 14,5 m a quota banchina, edificio 16 x 10 x 3,5 m a pareti scure,
    tetto piano chiaro, insegna rossa e striscione SCUOLA VELA (nomi inventati). Origine al centro (X 161, Y 72), Z 0."""
    g = G()
    yq = 80.27 - 0.00217 * (CIRC_C[0] - 44.0) - CIRC_C[1]          # ciglio in locale (~ +8,0)
    px0, px1, py0, py1 = -8.5, 8.5, -6.5, yq - 0.02
    g.box(px0, px1, py0, py1, -0.35, 0.0, "CEMENTO", faces=("xn", "xp", "yn", "bot"))
    g.box(px0, px1, py0, py1, -0.02, 0.0, "LEGNO_W", faces=("top",))
    for x in np.arange(px0 + 0.6, px1, 3.3):                         # pali
        for y in np.arange(py0 + 0.6, py1 - 0.5, 3.4):
            g.tube([(x, y, -0.35), (x, y, -2.2)], 0.15, 6, "CEMENTO")
    bx0, bx1, by0, by1, zt = -8.0, 8.0, -5.0, 5.0, 3.5
    # pareti a doghe scure: segmenti da ~2 m (la cella ha 8 doghe)
    for (a, b, y, out) in ((bx0, bx1, by0, (0, -1, 0)), (bx0, bx1, by1, (0, 1, 0))):
        n = 8
        for i in range(n):
            xa, xb = a + (b - a) * i / n, a + (b - a) * (i + 1) / n
            g.quad([(xa, y, 0), (xb, y, 0), (xb, y, zt), (xa, y, zt)], "PARETE", out)
    for (a, b, x, out) in ((by0, by1, bx0, (-1, 0, 0)), (by0, by1, bx1, (1, 0, 0))):
        n = 5
        for i in range(n):
            ya, yb = a + (b - a) * i / n, a + (b - a) * (i + 1) / n
            g.quad([(x, ya, 0), (x, yb, 0), (x, yb, zt), (x, ya, zt)], "PARETE", out)
    # tetto con gronda e cornice bianca
    g.box(bx0 - 0.35, bx1 + 0.35, by0 - 0.35, by1 + 0.35, zt, zt + 0.25, "BIANCO", faces=("xn", "xp", "yn", "yp", "bot"))
    g.box(bx0 - 0.35, bx1 + 0.35, by0 - 0.35, by1 + 0.35, zt + 0.25, zt + 0.25, "TETTO", faces=("top",))
    # finestre (mare, sud e lati), porte (terra, nord), insegne
    o_ = 0.012
    for x in (-6.0, -3.0, 0.0, 3.0, 6.0):
        g.quad([(x - 1.0, by0 - o_, 0.9), (x + 1.0, by0 - o_, 0.9), (x + 1.0, by0 - o_, 2.5), (x - 1.0, by0 - o_, 2.5)],
               "FINESTRA", (0, -1, 0))
    for y in (-2.5, 0.0, 2.5):
        for x, d in ((bx0 - o_, -1), (bx1 + o_, 1)):
            g.quad([(x, y - 0.9, 0.9), (x, y + 0.9, 0.9), (x, y + 0.9, 2.3), (x, y - 0.9, 2.3)], "FINESTRA", (d, 0, 0))
    for x in (-5.5, 5.5):
        g.quad([(x - 0.9, by1 + o_, 0.9), (x + 0.9, by1 + o_, 0.9), (x + 0.9, by1 + o_, 2.3), (x - 0.9, by1 + o_, 2.3)],
               "FINESTRA", (0, 1, 0))
    for x in (-1.6, 1.6):
        g.quad([(x - 0.9, by1 + o_, 0.0), (x + 0.9, by1 + o_, 0.0), (x + 0.9, by1 + o_, 2.4), (x - 0.9, by1 + o_, 2.4)],
               "PORTA", (0, 1, 0))
    iw, ih = INSEGNA["size"]
    g.box(-iw / 2, iw / 2, by1 + 0.36, by1 + 0.40, zt - 0.05, zt - 0.05 + ih, "BIANCO",
          faces=("xn", "xp", "top", "bot", "yn"))
    g.quad([(-iw / 2, by1 + 0.405, zt - 0.05), (iw / 2, by1 + 0.405, zt - 0.05), (iw / 2, by1 + 0.405, zt - 0.05 + ih),
            (-iw / 2, by1 + 0.405, zt - 0.05 + ih)], "INSEGNA", (0, 1, 0))
    for (x, d) in ((bx1 + 0.40, 1), (bx0 - 0.40, -1)):                  # insegna anche sui lati corti (est e ovest)
        hw = 3.2
        g.box(min(x, x - 0.04 * d), max(x, x - 0.04 * d), -hw, hw, zt - 0.05, zt + 0.45, "BIANCO",
              faces=("yn", "yp", "top", "bot", "xn" if d > 0 else "xp"))
        g.quad([(x + 0.005 * d, -hw, zt - 0.05), (x + 0.005 * d, hw, zt - 0.05), (x + 0.005 * d, hw, zt + 0.45),
                (x + 0.005 * d, -hw, zt + 0.45)], "INSEGNA", (d, 0, 0))
    bw, bh = BANNER["size"]
    g.quad([(bx1 + 0.02, 3.6 - bw / 2, 0.6), (bx1 + 0.02, 3.6 + bw / 2, 0.6), (bx1 + 0.02, 3.6 + bw / 2, 0.6 + bh),
            (bx1 + 0.02, 3.6 - bw / 2, 0.6 + bh)], "BANNER", (1, 0, 0))
    # ringhiera sui lati verso il mare (ovest, sud, est), aperta verso la banchina
    rail = [(px0 + 0.1, py1 - 0.6), (px0 + 0.1, py0 + 0.1), (px1 - 0.1, py0 + 0.1), (px1 - 0.1, py1 - 0.6)]
    g.tube([(x, y, 1.05) for x, y in rail], 0.03, 6, "ACCIAIO", cap=True)
    g.tube([(x, y, 0.55) for x, y in rail], 0.018, 4, "ACCIAIO", cap=True)
    for (xa, ya), (xb, yb) in zip(rail[:-1], rail[1:]):
        L = math.hypot(xb - xa, yb - ya)
        for k in range(int(L // 1.6) + 1):
            t = k / max(int(L // 1.6), 1)
            g.tube([(xa + (xb - xa) * t, ya + (yb - ya) * t, 0.0), (xa + (xb - xa) * t, ya + (yb - ya) * t, 1.05)],
                   0.025, 4, "ACCIAIO", cap=False)
    # condizionatore e asta bandiera (senza bandiera)
    g.box(4.0, 5.0, by1 + 0.02, by1 + 0.45, 2.6, 3.2, "BIANCO")
    g.tube([(px1 - 0.6, py0 + 0.6, 0.0), (px1 - 0.6, py0 + 0.6, 7.0)], 0.04, 6, "ALLUMINIO")
    o = g.finish(name, coll)
    boxes = [(px0, px1, py0, py1, -0.35, 0.0), (bx0, bx1, by0, by1, 0.0, zt + 0.25)]
    boxes += [(px0, px0 + 0.2, py0, py1 - 0.6, 0.0, 1.1), (px0, px1, py0, py0 + 0.2, 0.0, 1.1),
              (px1 - 0.2, px1, py0, py1 - 0.6, 0.0, 1.1)]
    pk._ucx(name, boxes, coll)
    return o


RACC_R = 1.42          # apotema del raccordo: copre il giunto tondo (raggio 1,40 = mezza larghezza del calpestio)
RACC_BOTT = 0.08


def _ngon(n, apothem, z, phase=None):
    """Vertici CCW di un n-gono regolare con l'apotema dato (un lato piatto verso -Y)."""
    R = apothem / math.cos(math.pi / n)
    ph = -math.pi / 2 + math.pi / n if phase is None else phase
    return [(R * math.cos(ph + 2 * math.pi * k / n), R * math.sin(ph + 2 * math.pi * k / n), z) for k in range(n)]


def build_raccordo(coll, lod=0, name="SM_Morin_Marina_Raccordo"):
    """Galleggiante di giunzione tondo (16-gono, apotema 1,42 m) per i gomiti e i nodi dei pontili (layout v3).
    Origine al centro sul calpestio (Z 0 locale), posa 2 cm sotto il calpestio dei moduli (Z -0,47): resta sotto le
    teste dei moduli e riempie la tacca sul lato esterno del gomito. Stessa sezione di SM_Morin_Marina_Pontile12."""
    n = 16 if lod < 2 else 8
    g = mb.Geo(ref=(0, 0, -0.3))
    top = _ngon(n, RACC_R if lod < 2 else RACC_R + RACC_BOTT, 0.0)     # LOD2: senza bottazzo, stessa impronta
    bot = [(x, y, -0.55) for x, y, _ in top]

    def body(bm):
        vt = [bm.verts.new(p) for p in top]
        vb = [bm.verts.new(p) for p in bot]
        for k in range(n):
            k1 = (k + 1) % n
            bm.faces.new([vb[k], vb[k1], vt[k1], vt[k]])
    g.new_faces(body, "GRIGIO")
    g.new_faces(lambda bm: bm.faces.new([bm.verts.new(p) for p in top]), None, mi=1)
    if lod < 2:
        bi = _ngon(n, RACC_R, -0.05)
        bo = _ngon(n, RACC_R + RACC_BOTT, -0.05)
        bl = [(x, y, -0.35) for x, y, _ in bo]

        def bott(bm):
            vi = [bm.verts.new(p) for p in bi]
            vo = [bm.verts.new(p) for p in bo]
            vl = [bm.verts.new(p) for p in bl]
            for k in range(n):
                k1 = (k + 1) % n
                bm.faces.new([vl[k], vl[k1], vo[k1], vo[k]])          # fianco esterno
                if lod == 0:
                    bm.faces.new([vi[k], vo[k], vo[k1], vi[k1]][::-1])  # anello superiore (normale in alto)
        g.new_faces(bott, "GOMMA")
    o = g.finish(name + mi._sfx(lod), coll)
    for f in o.data.polygons:                       # normali: tutte verso l'esterno / l'alto
        c = f.center
        out = Vector((c.x, c.y, 0.0)) if abs(f.normal.z) < 0.5 else Vector((0, 0, 1))
        if f.normal.dot(out) < 0:
            f.flip()
    o.data.update()
    if lod == 0:
        pk._ucx_hull(name, 0, top + bot, coll)
    return mb._localize(o)


ASSETS_LOD = {"SM_Morin_Marina_Pontile12": build_pontile12, "SM_Morin_Marina_Passerella": build_passerella,
              "SM_Morin_Marina_Colonnina": build_colonnina, "SM_Mirabello_Pontile_Col": build_mirabello_col,
              "SM_Morin_Marina_Raccordo": build_raccordo}
ASSETS_ONE = {"SM_Morin_Marina_PontileLargo": build_largo, "SM_Morin_Marina_Circolo": build_circolo}


def build_all():
    build_materials()
    coll = pk._coll(KIT)
    build_barche(coll)
    for nm, fn in ASSETS_LOD.items():
        for lod in range(3):
            fn(coll, lod)
    for nm, fn in ASSETS_ONE.items():
        fn(coll)
    for o in coll.objects:
        o.hide_render = True
    return len(coll.objects)


# =================================================================================================================
# verifiche: triangoli, bbox dei LOD, normali (ray test dall'esterno)
# =================================================================================================================
def _bbox(o):
    vs = np.array([v.co[:] for v in o.data.vertices])
    return vs.min(0), vs.max(0)


def ray_test(o, n_dir=60, grid=7, from_below=None, faces=None):
    """Raggi da fuori verso l'oggetto: la prima faccia colpita deve guardare il raggio (dot < 0).
    from_below=False ignora i raggi che salgono da sotto il pelo dell'acqua (gusci aperti sotto: pontili)."""
    bvh = BVHTree.FromPolygons([v.co.copy() for v in o.data.vertices], [p.vertices[:] for p in o.data.polygons])
    lo, hi = _bbox(o)
    c = Vector(((lo + hi) / 2).tolist())
    R = float(np.linalg.norm(hi - lo)) / 2 + 0.5
    if from_below is None:
        from_below = not any(k in o.name for k in ("Pontile", "Passerella", "Circolo"))
    bad = tot = 0
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n_dir):
        z = 1 - 2 * (i + 0.5) / n_dir
        r = math.sqrt(1 - z * z)
        d = -Vector((r * math.cos(ga * i), r * math.sin(ga * i), z))
        if not from_below and d.z > 0.05:
            continue
        a = d.orthogonal().normalized()
        b = d.cross(a)
        for p in np.linspace(-1, 1, grid):
            for q in np.linspace(-1, 1, grid):
                org = c - d * R * 2 + a * (p * R) + b * (q * R)
                loc, nrm, idx, dist = bvh.ray_cast(org, d)
                if loc is None:
                    continue
                tot += 1
                if nrm.dot(d) > 0:
                    bad += 1
                    if faces is not None:
                        faces.append(idx)
    return bad, tot


def report(do_ray=True):
    coll = bpy.data.collections[KIT]
    rows = []
    base = {}
    for o in sorted(coll.objects, key=lambda o: o.name):
        if o.type != "MESH" or o.name.startswith("UCX_"):
            continue
        t = pk.tri_count(o)
        lo, hi = _bbox(o)
        root = o.name.rsplit("_LOD", 1)[0]
        if "_LOD" not in o.name:
            base[root] = (t, lo, hi)
        rows.append((o.name, t, lo, hi))
    out = []
    for name, t, lo, hi in rows:
        root = name.rsplit("_LOD", 1)[0]
        t0, lo0, hi0 = base[root]
        size0 = hi0 - lo0
        dev = float(np.max(np.abs(np.concatenate([lo - lo0, hi - hi0])) / np.tile(np.maximum(size0, 1e-6), 2)))
        ucx = [u.name for u in coll.objects if u.name.startswith(f"UCX_{name}_")]
        bad, tot = ray_test(bpy.data.objects[name]) if do_ray else (0, 0)
        out.append(dict(name=name, tri=t, ratio=round(t / t0, 3), size=tuple(round(float(v), 2) for v in hi - lo),
                        bbox_dev=round(dev, 4), ucx=len(ucx), ray_bad=bad, ray_tot=tot))
    for r in out:
        print(f"{r['name']:<52} {r['tri']:>6} tri  {r['ratio']:>5}  size {r['size']}  dLOD {r['bbox_dev']:.3f}  "
              f"UCX {r['ucx']}  ray {r['ray_bad']}/{r['ray_tot']}")
    return out


# =================================================================================================================
# layout v2 (porting di exports/marina/gen_marina_v1.py con le sagome reali e le varianti definitive)
# =================================================================================================================
def yq(x):
    return 80.2663 - 0.002166 * (x - 44.0)


def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    return (dx / L, dy / L), L


def _yaw_ue_dir(d):
    return math.degrees(math.atan2(-d[1], d[0]))


GANG = 3.5
PONTILI = {
    "Spina": [(151.1, yq(151.1) - GANG), (150.3, -86.0), (165.1, -101.1), (195.5, -132.0), (197.1, -176.6)],
    "Esterno": [(197.1, -176.6), (295.5, -174.4)],
    "Esterno2": [(197.1, -176.6), (196.0, -213.1), (213.9, -229.7), (316.4, -228.6)],
    "F1": [(151.6, 62.8), (261.9, 62.9)], "F2": [(151.4, 43.2), (261.6, 41.8)], "F3": [(151.2, 17.6), (260.4, 17.0)],
    "F4": [(150.9, -11.7), (260.5, -10.8)], "F5": [(150.7, -40.6), (259.4, -38.9)],
    "F6": [(150.4, -66.9), (260.8, -69.1)], "F7": [(165.1, -101.1), (261.4, -99.9)],
    "F8": [(195.5, -132.0), (260.8, -131.0)],
    "L_Gamba": [(105.4, yq(105.4) - GANG), (106.3, 62.3), (106.7, 29.6)],
    "L_Testa": [(106.7, 29.6), (89.4, 29.5)], "L_Ramo": [(106.3, 62.3), (88.9, 61.6)],
    "NE": [(289.6, yq(289.6) - GANG), (291.7, -6.5)],
}
for _k in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "L_Testa", "L_Ramo", "Esterno"):
    _p = PONTILI[_k]
    _d, _L = _unit(_p[0], _p[1])
    PONTILI[_k] = [(_p[0][0] + _d[0] * 1.4, _p[0][1] + _d[1] * 1.4)] + _p[1:]
LARGO = [(126.9, yq(126.9)), (127.1, 45.5)]
PASSERELLE = (("Spina", 151.1), ("L_Gamba", 105.4), ("NE", 289.6))


def _rect_aabb(x0, x1, y0, y1):
    return (((x0 + x1) / 2, (y0 + y1) / 2), (1.0, 0.0), (x1 - x0) / 2, (y1 - y0) / 2)


RESERVED = [_rect_aabb(55, 90, -120, 82)]
for _xs in (92, 140, 188, 300):
    RESERVED.append(_rect_aabb(_xs - 4, _xs + 4, 66, 82))
RESERVED.append(_rect_aabb(151.5, 171, 64, 82))
FERRY = [[(80.0, -36.9), (110.2, -86.5), (188.4, -241.7)], [(80.1, 1.0), (135.1, -107.5), (199.4, -231.7)]]
FERRY_BUF = 12.0


def _corners(r):
    c, d, hl, hw = r
    n = (-d[1], d[0])
    return [(c[0] + d[0] * sx * hl + n[0] * sy * hw, c[1] + d[1] * sx * hl + n[1] * sy * hw)
            for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def _sat(r1, r2):
    c1, c2 = _corners(r1), _corners(r2)
    for r in (r1, r2):
        d = r[1]
        n = (-d[1], d[0])
        for ax in (d, n):
            p1 = [p[0] * ax[0] + p[1] * ax[1] for p in c1]
            p2 = [p[0] * ax[0] + p[1] * ax[1] for p in c2]
            if max(p1) < min(p2) or max(p2) < min(p1):
                return False
    return True


def _dist_pt_seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _poly_dist(r1, r2):
    """distanza minima fra due rettangoli orientati (0 se si toccano o compenetrano)."""
    if _sat(r1, r2):
        return 0.0
    c1, c2 = _corners(r1), _corners(r2)
    best = 1e9
    for P, Q in ((c1, c2), (c2, c1)):
        for p in P:
            for i in range(4):
                best = min(best, _dist_pt_seg(p, Q[i], Q[(i + 1) % 4]))
    return best


def _near_ferry(rect):
    for pl in FERRY:
        for i in range(len(pl) - 1):
            for p in _corners(rect) + [rect[0]]:
                if _dist_pt_seg(p, pl[i], pl[i + 1]) < FERRY_BUF:
                    return True
    return False


# sagome (dal LOD0 senza cime, misurate da footprints()); yacht di Mirabello dai file esistenti
FOOT = {}
T = {
    "G": dict(tipo="Gommone"), "Z": dict(tipo="Gozzo"), "M": dict(tipo="Motoscafo"), "V9": dict(tipo="Vela9"),
    "V11": dict(asset="SM_Mirabello_YachtB_v2"), "Y13": dict(asset="SM_Mirabello_YachtA"),
}
PESI_VAR = {"G": (0.45, 0.35, 0.20), "Z": (0.45, 0.30, 0.25), "M": (0.50, 0.30, 0.20), "V9": (0.50, 0.30, 0.20)}
MIX_6 = [("G", 45), ("Z", 55)]
MIX_75 = [("G", 20), ("Z", 35), ("M", 45)]
MIX_9 = [("G", 8), ("Z", 12), ("M", 50), ("V9", 30)]
MIX_11 = [("Z", 5), ("M", 40), ("V9", 25), ("V11", 30)]
MIX_13 = [("M", 15), ("V11", 30), ("Y13", 55)]
MIX_VELA = [("V9", 50), ("V11", 50)]
SIDES = [
    ("L_Testa", 0, +1, 11.0, MIX_VELA, 0.9), ("L_Testa", 0, -1, 6.0, MIX_6, 0.85),
    ("L_Ramo", 0, +1, 6.0, MIX_6, 0.85), ("L_Ramo", 0, -1, 6.0, MIX_6, 0.85),
    ("L_Gamba", 0, +1, 7.5, MIX_75, 0.85), ("L_Gamba", 1, +1, 7.5, MIX_75, 0.85),
    ("L_Gamba", 0, -1, 6.0, MIX_6, 0.85), ("L_Gamba", 1, -1, 6.0, MIX_6, 0.85),
    ("F1", 0, +1, 6.0, MIX_6, 0.85), ("F1", 0, -1, 6.0, MIX_6, 0.85),
    ("F2", 0, +1, 6.0, MIX_6, 0.85), ("F2", 0, -1, 7.5, MIX_75, 0.85),
    ("F3", 0, +1, 7.5, MIX_75, 0.85), ("F3", 0, -1, 9.0, MIX_9, 0.85),
    ("F4", 0, +1, 9.0, MIX_9, 0.85), ("F4", 0, -1, 9.0, MIX_9, 0.85),
    ("F5", 0, +1, 9.0, MIX_9, 0.85), ("F5", 0, -1, 9.0, MIX_9, 0.85),
    ("F6", 0, +1, 9.0, MIX_9, 0.85), ("F6", 0, -1, 11.0, MIX_11, 0.85),
    ("F7", 0, +1, 10.0, MIX_11, 0.85), ("F7", 0, -1, 11.0, MIX_11, 0.85),
    ("F8", 0, +1, 9.0, MIX_9, 0.85), ("F8", 0, -1, 13.2, MIX_13, 0.85),
    ("Esterno", 0, +1, 13.2, MIX_13, 0.8), ("Esterno", 0, -1, 13.2, MIX_13, 0.7),
    ("Esterno2", 2, +1, 13.2, MIX_13, 0.7),
    ("Spina", 0, -1, 13.2, MIX_13, 0.5), ("Spina", 1, -1, 11.0, MIX_11, 0.5), ("Spina", 2, -1, 11.0, MIX_11, 0.5),
    ("Spina", 3, -1, 13.2, MIX_13, 0.5),
    ("NE", 0, -1, 11.0, MIX_11, 0.85), ("NE", 0, +1, 7.5, MIX_75, 0.7),
]


def footprints():
    """xmin, xmax, ymax delle LOD0 senza cime (sagoma) e lunghezza nominale per il riempimento."""
    nominal = {"G": 5.0, "Z": 6.0, "M": 7.5, "V9": 9.0, "V11": 11.0, "Y13": 13.2}
    link_yachts()
    for k, d in T.items():
        if "tipo" in d:
            g = BUILDERS[d["tipo"]](0, False)
            keep = [f for f in g.bm.faces if g.names[f[g.tag]] != "CIMA"]
            vs = np.array([v.co[:] for f in keep for v in f.verts])
            g.bm.free()
        else:
            o = bpy.data.objects[d["asset"]]
            vs = np.array([v.co[:] for v in o.data.vertices])
        FOOT[k] = dict(xmin=float(vs[:, 0].min()), xmax=float(vs[:, 0].max()),
                       ymax=float(np.abs(vs[:, 1]).max()), L=nominal[k])
    return FOOT


def _wpick(rng, lst):
    tot = sum(w for _, w in lst)
    r = rng.uniform(0, tot)
    for v, w in lst:
        r -= w
        if r <= 0:
            return v
    return lst[-1][0]


def _pontile_rects():
    rects = []
    hw = PONT_W / 2 + BOTT
    for name, pts in PONTILI.items():
        for a, b in zip(pts[:-1], pts[1:]):
            d, L = _unit(a, b)
            rects.append(((a[0] + d[0] * L / 2, a[1] + d[1] * L / 2), d, L / 2, hw))
    a, b = LARGO
    d, L = _unit(a, b)
    rects.append(((a[0] + d[0] * L / 2, a[1] + d[1] * L / 2), d, L / 2, LARGO_W / 2))
    for nm, x in PASSERELLE:
        rects.append(((x, yq(x) - GANG / 2), (0.0, -1.0), GANG / 2 + 0.45, PASS_W / 2))
    cx, cy = CIRC_C
    rects.append(_rect_aabb(cx - 8.5, cx + 8.5, cy - 6.5, yq(cx)))
    return rects


MARGIN = 0.30


def layout_v2(seed=20261120):
    """Barche: lista di dict (codice, tipo, variante, prua, origine, direzione +X, yaw UE, pontile)."""
    if not FOOT:
        footprints()
    rng = random.Random(seed)
    prects = _pontile_rects()
    boats, placed = [], []
    stats = {}
    hw = PONT_W / 2 + BOTT
    for (pn, si, side, Lmax, mix, fill) in SIDES:
        pts = PONTILI[pn]
        a, b = pts[si], pts[si + 1]
        d, L = _unit(a, b)
        nL = (-d[1], d[0])
        n = (nL[0] * side, nL[1] * side)
        allowed = [(k, w) for k, w in mix if FOOT[k]["L"] <= Lmax]
        t = 1.0
        while True:
            k = _wpick(rng, allowed)
            F = FOOT[k]
            pitch = 2 * F["ymax"] + 0.7
            if t + pitch > L - 0.5:
                break
            tc = t + pitch / 2
            t += pitch
            if rng.random() > fill:
                continue
            bowto = k in ("G", "Z") and rng.random() < 0.3
            edge = (a[0] + d[0] * tc + n[0] * (hw + D_PONT), a[1] + d[1] * tc + n[1] * (hw + D_PONT))
            if not bowto:
                bd = n
                org = (edge[0] - bd[0] * F["xmin"], edge[1] - bd[1] * F["xmin"])
            else:
                bd = (-n[0], -n[1])
                org = (edge[0] - bd[0] * F["xmax"], edge[1] - bd[1] * F["xmax"])
            jit = math.radians(rng.uniform(-1.5, 1.5))
            # rotazione attorno all'estremo verso il pontile (la cima resta al suo posto)
            c, s_ = math.cos(jit), math.sin(jit)
            bd2 = (bd[0] * c - bd[1] * s_, bd[0] * s_ + bd[1] * c)
            xe = F["xmax"] if bowto else F["xmin"]
            org = (edge[0] - bd2[0] * xe, edge[1] - bd2[1] * xe)
            cx = (F["xmin"] + F["xmax"]) / 2
            rect = ((org[0] + bd2[0] * cx, org[1] + bd2[1] * cx), bd2, (F["xmax"] - F["xmin"]) / 2, F["ymax"])
            infl = (rect[0], rect[1], rect[2] + MARGIN / 2, rect[3] + MARGIN / 2)
            if any(_poly_dist(rect, r) < MARGIN for r in prects):
                stats["scarto_pontile"] = stats.get("scarto_pontile", 0) + 1
                continue
            if any(_sat(rect, r) for r in RESERVED):
                stats["scarto_zona_riservata"] = stats.get("scarto_zona_riservata", 0) + 1
                continue
            if _near_ferry(rect):
                stats["scarto_rotta_battelli"] = stats.get("scarto_rotta_battelli", 0) + 1
                continue
            if any(_sat(infl, r) for r in placed):
                stats["scarto_barca"] = stats.get("scarto_barca", 0) + 1
                continue
            placed.append(infl)
            if "tipo" in T[k]:
                tipo = T[k]["tipo"]
                vn = _wpick(rng, [(v[0], w) for v, w in zip(TIPI[tipo]["var"], PESI_VAR[k])])
                asset = barca_name(tipo, vn, bowto)
            else:
                tipo, vn, asset = None, "base", T[k]["asset"]
            boats.append(dict(k=k, tipo=tipo, var=vn, prua=bowto, org=org, dir=bd2, pontile=pn, side=n,
                              asset=asset, rect=rect))
    return boats, stats


def check_layout(boats):
    """Verifiche richieste: distanze >= 0,3 m da pontili e fra barche, verso del +X, zone libere."""
    prects = _pontile_rects()
    res = dict(min_pontile=1e9, min_barca=1e9, verso_err=0, riservate=0, battelli=0)
    rects = [b["rect"] for b in boats]
    for i, b in enumerate(boats):
        res["min_pontile"] = min(res["min_pontile"], min(_poly_dist(b["rect"], r) for r in prects))
        for j in range(i + 1, len(boats)):
            r2 = rects[j]
            if math.hypot(b["rect"][0][0] - r2[0][0], b["rect"][0][1] - r2[0][1]) > 20:
                continue
            res["min_barca"] = min(res["min_barca"], _poly_dist(b["rect"], r2))
        dot = b["dir"][0] * b["side"][0] + b["dir"][1] * b["side"][1]
        if (not b["prua"] and dot < 0.99) or (b["prua"] and dot > -0.99):
            res["verso_err"] += 1
        if any(_sat(b["rect"], r) for r in RESERVED):
            res["riservate"] += 1
        if _near_ferry(b["rect"]):
            res["battelli"] += 1
    return res


def pontili_rows():
    """Righe (asset, nome, X, Y, Z, rotZ, pitch, variante) in coordinate di progetto (metri, gradi Blender)."""
    rows = []
    col_rows = []
    for name, pts in PONTILI.items():
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            d, L = _unit(a, b)
            rz = math.degrees(math.atan2(d[1], d[0]))
            n48 = int(L // 48)
            rem = L - 48 * n48
            mods = [("SM_Mirabello_Pontile_Col", 48.0 * k, Z_DECK) for k in range(n48)]
            if rem > 0.6:
                n12 = max(1, math.ceil((rem - 0.6) / 12.0))
                for k in range(n12):
                    s = 48.0 * n48 + 12.0 * k
                    z = Z_DECK
                    if s + 12.0 > L:
                        s, z = max(L - 12.0, 0.0), Z_DECK - 0.01
                    mods.append(("SM_Morin_Marina_Pontile12", s, z))
            for j, (asset, s, z) in enumerate(mods):
                x, y = a[0] + d[0] * s, a[1] + d[1] * s
                rows.append((asset, f"Marina_{name}_s{i}_m{j:02d}", x, y, z, rz, 0.0, "base"))
                if asset == "SM_Morin_Marina_Pontile12" and z == Z_DECK:
                    cx, cy = x + d[0] * 6.0, y + d[1] * 6.0
                    col_rows.append(("SM_Morin_Marina_Colonnina", f"Marina_Colonnina_{name}_s{i}_m{j:02d}", cx, cy,
                                     Z_DECK, rz, 0.0, "base"))
    a, b = LARGO
    d, L = _unit(a, b)
    rows.append(("SM_Morin_Marina_PontileLargo", "Marina_Largo_m00", a[0], a[1], 0.0,
                 math.degrees(math.atan2(d[1], d[0])), 0.0, "base"))
    for nm, x in PASSERELLE:
        rows.append(("SM_Morin_Marina_Passerella", f"Marina_Passerella_{nm}", x, yq(x), 0.0, -90.0, 0.0, "base"))
    rows.append(("SM_Morin_Marina_Circolo", "Marina_Circolo", CIRC_C[0], CIRC_C[1], 0.0, 0.0, 0.0, "base"))
    return rows + col_rows


def _yaw(rz):
    y = -rz
    while y <= -180.0:
        y += 360.0
    while y > 180.0:
        y -= 360.0
    return y


def write_csv(seed=20261120):
    boats, stats = layout_v2(seed)
    chk = check_layout(boats)
    prow = pontili_rows()
    hdr = "asset,nome,x,y,z,yaw,pitch,roll,variante\n"
    with open(f"{PROJ}/exports/marina/marina_pontili_v2.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(hdr)
        for a, n, x, y, z, rz, pitch, var in prow:
            fh.write(f"{a},{n},{x * 100:.1f},{-y * 100:.1f},{z * 100:.1f},{_yaw(rz):.2f},{pitch:.2f},0.00,{var}\n")
    with open(f"{PROJ}/exports/marina/marina_barche_v2.csv", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(hdr)
        for i, b in enumerate(boats):
            rz = math.degrees(math.atan2(b["dir"][1], b["dir"][0]))
            var = b["var"] + ("_prua" if b["prua"] else "")
            fh.write(f"{b['asset']},Barca_{b['pontile']}_{i:03d},{b['org'][0] * 100:.1f},{-b['org'][1] * 100:.1f},"
                     f"{Z_ACQUA * 100:.1f},{_yaw(rz):.2f},0.00,0.00,{var}\n")
    from collections import Counter
    cnt = Counter(b["asset"] for b in boats)
    tipi = Counter(b["k"] for b in boats)
    pcnt = Counter(r[0] for r in prow)
    print("BARCHE", len(boats), dict(tipi), "PRUA", sum(b["prua"] for b in boats))
    print("ASSET", dict(cnt))
    print("PONTILI", dict(pcnt), "righe", len(prow))
    print("SCARTI", stats)
    print("VERIFICHE", chk)
    return boats, prow, chk


# =================================================================================================================
# contesto per i render (istanze delle LOD0) e catture
# =================================================================================================================
def link_yachts():
    B = PROJ + "/blender/arte_mirabello.blend"
    need = [n for n in ("SM_Mirabello_YachtA", "SM_Mirabello_YachtB_v2") if n not in bpy.data.objects]
    if need:
        with bpy.data.libraries.load(B, link=True) as (src, dst):
            dst.objects = need
    return [bpy.data.objects[n] for n in ("SM_Mirabello_YachtA", "SM_Mirabello_YachtB_v2")]


def build_context(seed=20261120):
    link_yachts()
    coll = pk._coll(CTX)
    for o in list(coll.objects):
        coll.objects.unlink(o)
        if o.users == 0:
            bpy.data.objects.remove(o)
    boats, _ = layout_v2(seed)
    items = [(r[0], "MAR_" + r[1], r[2], r[3], r[4], r[5], r[6]) for r in pontili_rows()]
    for i, b in enumerate(boats):
        items.append((b["asset"], f"MAR_Barca_{i:03d}", b["org"][0], b["org"][1], Z_ACQUA,
                      math.degrees(math.atan2(b["dir"][1], b["dir"][0])), 0.0))
    for a, n, x, y, z, rz, pitch in items:
        src = bpy.data.objects[a]
        o = bpy.data.objects.new(n, src.data)
        coll.objects.link(o)
        o.location = (x, y, z)
        o.rotation_euler = (0, math.radians(-pitch), math.radians(rz))
    # acqua di riferimento (solo render)
    w = bpy.data.objects.get("REF_Acqua_Marina")
    if w is None:
        me = bpy.data.meshes.new("REF_Acqua_Marina")
        bm = bmesh.new()
        pk._box(bm, -300, 900, -700, 80.0, Z_ACQUA, Z_ACQUA, faces=("top",))
        bm.to_mesh(me)
        bm.free()
        w = bpy.data.objects.new("REF_Acqua_Marina", me)
        coll.objects.link(w)
        m = bpy.data.materials.get("REF_Acqua_Marina") or bpy.data.materials.new("REF_Acqua_Marina")
        m.use_nodes = True
        bs = next(nd for nd in m.node_tree.nodes if nd.type == "BSDF_PRINCIPLED")
        bs.inputs["Base Color"].default_value = (0.02, 0.10, 0.12, 1)
        bs.inputs["Roughness"].default_value = 0.06
        me.materials.append(m)
    elif w.name not in coll.objects:
        coll.objects.link(w)
    return len(coll.objects)


CAMS = {
    # nome: (posizione, punto guardato, FOV orizzontale)
    # come banchina_vista_montagne_verso_ponte.jpg; X 300 (non 282) come la cattura UEFN di confronto (uefn_arte §39),
    # stessa direzione di prima (yaw UE 173,5, pitch -0,2)
    "CAM_Mar_Banchina": ((300.0, 81.0, 1.70), (168.0, 66.0, 1.2), 64.0),
    "CAM_Mar_Alto": ((75.0, 175.0, 110.0), (185.0, 10.0, 0.0), 62.0),       # vista aerea obliqua (vista_dall_alto_2)
    "CAM_Mar_Finger": ((156.0, 18.8, Z_DECK + 1.65), (215.0, 18.0, -0.4), 70.0),   # sul finger F3 verso la punta
    "CAM_Mar_Passeggiata": ((140.0, 86.0, 1.70), (175.0, 30.0, 0.0), 75.0),        # dalla passeggiata verso la marina
}


def cameras():
    coll = pk._coll("MARINA_Camere")
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
    return list(CAMS)


def render(cam, path, width=1500, height=1000):
    s = bpy.context.scene
    s.camera = bpy.data.objects[cam]
    s.render.resolution_x, s.render.resolution_y = width, height
    s.render.resolution_percentage = 100
    s.render.filepath = path
    s.render.image_settings.file_format = "PNG"
    for o in bpy.data.collections[KIT].objects:
        o.hide_render = True
    bpy.ops.render.render(write_still=True)
    return path


def confronto(photo, render_path, out):
    a = tp.load(photo)[..., :3]
    b = tp.load(render_path)[..., :3]
    b = tp.resize(b, a.shape[1], int(round(b.shape[0] * a.shape[1] / b.shape[1])))
    sep = np.ones((6, a.shape[1], 3), np.float32)
    tp.save(np.concatenate([a, sep, b], 0), out)
    return out


# =================================================================================================================
# export
# =================================================================================================================
def export_list():
    names = []
    for tipo in BUILDERS:
        for prua in ((False, True) if tipo in PRUA_TIPI else (False,)):
            for vn, *_ in TIPI[tipo]["var"]:
                names.append((barca_name(tipo, vn, prua), True))
    for nm in ASSETS_LOD:
        names.append((nm, True))
    for nm in ASSETS_ONE:
        names.append((nm, False))
    return names


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
        for nm, lods in export_list():
            for lod in (range(3) if lods else (0,)):
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
# layout pontili v3 (2026-11-20): radici dei fingers sull'asse reale della spina, raccordi nei gomiti e nei nodi,
# angolo del pontile a L chiuso, segmenti coperti fino in fondo. La v2 (pontili_rows/write_csv) resta com'e'.
# Quote: moduli -0,45 · radici dei rami -0,455 · ultimo modulo prima di un gomito/nodo -0,46 · raccordi -0,47
# (le parti sovrapposte non sono mai complanari; gradino massimo 2 cm).
# =================================================================================================================
Z_ROOT, Z_ELB, Z_RACC = Z_DECK - 0.005, Z_DECK - 0.01, Z_DECK - 0.02
HW = PONT_W / 2
TRUNKS_V3 = ("Spina", "Esterno2", "L_Gamba", "NE")                 # partono dalla passerella o da un nodo, in ordine
BRANCHES_V3 = ("Esterno", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "L_Testa", "L_Ramo")
EXT_END_V3 = {"L_Gamba": HW + 0.05}                                  # la gamba della L arriva al bordo sud della testa


def _raw_start(k):
    """Partenza OSM del ramo (sull'asse del tronco), prima dello spostamento di 1,4 m della v2."""
    p = PONTILI[k]
    d, _ = _unit(p[0], p[1])
    return (p[0][0] - d[0] * 1.4, p[0][1] - d[1] * 1.4)


def _axis_v3():
    """Polilinee dei calpestii v3 (tronchi con eventuale prolungamento in fondo, rami dalla partenza OSM)."""
    ax = {}
    for k in TRUNKS_V3:
        pts = list(PONTILI[k])
        if k in EXT_END_V3:
            d, _ = _unit(pts[-2], pts[-1])
            e = EXT_END_V3[k]
            pts[-1] = (pts[-1][0] + d[0] * e, pts[-1][1] + d[1] * e)
        ax[k] = pts
    for k in BRANCHES_V3:
        ax[k] = [_raw_start(k)] + list(PONTILI[k][1:])
    return ax


def _joints_v3():
    """Raccordi: ogni vertice interno dei tronchi + il nodo in fondo alla spina (Esterno / Esterno 2)."""
    out = []
    for k in TRUNKS_V3:
        pts = PONTILI[k]
        for i in range(1, len(pts) - 1):
            d0, _ = _unit(pts[i - 1], pts[i])
            d1, _ = _unit(pts[i], pts[i + 1])
            ang = math.degrees(math.acos(max(-1.0, min(1.0, d0[0] * d1[0] + d0[1] * d1[1]))))
            out.append((f"{k}_v{i}", pts[i], ang))
    out.append(("Spina_fine", PONTILI["Spina"][-1], None))
    return out


def _shape_exit(shape, p, d):
    """Parametro t>=0 a cui il raggio p + t d esce dalla forma (None se p e' fuori)."""
    if shape[0] == "rect":
        _, c, u, hl, hw = shape
        n = (-u[1], u[0])
        t_out = 1e9
        for ax, h in ((u, hl), (n, hw)):
            o = (p[0] - c[0]) * ax[0] + (p[1] - c[1]) * ax[1]
            v = d[0] * ax[0] + d[1] * ax[1]
            if abs(o) > h + 1e-9:
                return None
            if abs(v) > 1e-12:
                t_out = min(t_out, ((h if v > 0 else -h) - o) / v)
        return max(t_out, 0.0)
    _, c, r = shape
    ox, oy = p[0] - c[0], p[1] - c[1]
    if ox * ox + oy * oy > r * r + 1e-12:
        return None
    b = ox * d[0] + oy * d[1]
    cc = ox * ox + oy * oy - r * r
    return -b + math.sqrt(max(b * b - cc, 0.0))


def _union_exit(shapes, p, d):
    t = 0.0
    for _ in range(200):
        q = (p[0] + d[0] * t, p[1] + d[1] * t)
        best = None
        for s in shapes:
            e = _shape_exit(s, q, d)
            if e is not None and e > 1e-7 and (best is None or e > best):
                best = e
        if best is None:
            return t
        t += best + 1e-7
    return t


def _seg_modules(L):
    """Moduli (asset, s, z) che coprono tutto il segmento: 48 m + 12 m, l'ultimo arretrato 1 cm piu' basso."""
    n48 = int((L + 0.02) // 48)
    rem = L - 48 * n48
    mods = [["SM_Mirabello_Pontile_Col", 48.0 * k, Z_DECK] for k in range(n48)]
    if rem > 0.02:
        n12 = max(1, math.ceil((rem - 0.02) / 12.0))
        for k in range(n12):
            s, z = 48.0 * n48 + 12.0 * k, Z_DECK
            if s + 12.0 > L + 0.02:
                s, z = max(L - 12.0, 0.0), Z_DECK - 0.01
            mods.append(["SM_Morin_Marina_Pontile12", s, z])
    return mods


def pontili_rows_v3():
    """Righe come pontili_rows() (coordinate di progetto) + info per le verifiche."""
    ax = _axis_v3()
    joints = _joints_v3()
    shapes = []                    # calpestio dei tronchi (per le radici dei rami)
    rows, col_rows, info = [], [], dict(radici={}, raccordi=[])
    junction_end = {"Spina", "L_Gamba"}

    def emit(name, pts, root_z=None):
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            d, L = _unit(a, b)
            rz = math.degrees(math.atan2(d[1], d[0]))
            mods = _seg_modules(L)
            if i == 0 and root_z is not None:
                mods[0][2] = min(mods[0][2], root_z)
            if i < len(pts) - 2 or name in junction_end:
                mods[-1][2] = min(mods[-1][2], Z_ELB)
            for j, (asset, s, z) in enumerate(mods):
                x, y = a[0] + d[0] * s, a[1] + d[1] * s
                rows.append((asset, f"Marina_{name}_s{i}_m{j:02d}", x, y, round(z, 4), rz, 0.0, "base"))
                if asset == "SM_Morin_Marina_Pontile12" and abs(z - Z_DECK) < 1e-6:
                    col_rows.append(("SM_Morin_Marina_Colonnina", f"Marina_Colonnina_{name}_s{i}_m{j:02d}",
                                     x + d[0] * 6.0, y + d[1] * 6.0, Z_DECK, rz, 0.0, "base"))
            shapes.append(("rect", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), d, L / 2, HW))

    for k in TRUNKS_V3:
        emit(k, ax[k])
    for nm, c, ang in joints:
        shapes.append(("circle", c, RACC_R))
        rows.append(("SM_Morin_Marina_Raccordo", f"Marina_Raccordo_{nm}", c[0], c[1], Z_RACC, 0.0, 0.0, "base"))
        info["raccordi"].append((nm, c, ang))
    for k in BRANCHES_V3:
        p0 = ax[k][0]
        d, _ = _unit(p0, ax[k][1])
        n = (-d[1], d[0])
        ex = [_union_exit(shapes, (p0[0] + n[0] * l, p0[1] + n[1] * l), d) for l in np.linspace(-HW, HW, 57)]
        s0 = min(ex) - 0.01
        root = (p0[0] + d[0] * s0, p0[1] + d[1] * s0)
        old = PONTILI[k][0]
        info["radici"][k] = dict(root=root, s_min=min(ex), s_max=max(ex), gap_v2=1.4 - min(ex),
                                 sposta=math.hypot(root[0] - old[0], root[1] - old[1]))
        emit(k, [root] + ax[k][1:], root_z=Z_ROOT)
    a, b = LARGO
    d, L = _unit(a, b)
    rows.append(("SM_Morin_Marina_PontileLargo", "Marina_Largo_m00", a[0], a[1], 0.0,
                 math.degrees(math.atan2(d[1], d[0])), 0.0, "base"))
    for nm, x in PASSERELLE:
        rows.append(("SM_Morin_Marina_Passerella", f"Marina_Passerella_{nm}", x, yq(x), 0.0, -90.0, 0.0, "base"))
    rows.append(("SM_Morin_Marina_Circolo", "Marina_Circolo", CIRC_C[0], CIRC_C[1], 0.0, 0.0, 0.0, "base"))
    return rows + col_rows, info


def write_csv_v3(path=None):
    prow, info = pontili_rows_v3()
    path = path or f"{PROJ}/exports/marina/marina_pontili_v3.csv"
    if os.path.exists(path):
        raise RuntimeError(f"esiste gia': {path}")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("asset,nome,x,y,z,yaw,pitch,roll,variante\n")
        for a, n, x, y, z, rz, pitch, var in prow:
            fh.write(f"{a},{n},{x * 100:.1f},{-y * 100:.1f},{z * 100:.1f},{_yaw(rz):.2f},{pitch:.2f},0.00,{var}\n")
    return path, prow, info


# ---------------------------------------------------------------------------------------------------------------
# verifica v3: ray test su griglia di 10 cm (collisioni UCX e calpestio visibile) + distanza delle barche v2
# ---------------------------------------------------------------------------------------------------------------
def _placed_bvh(prow, mode):
    """BVH dei pezzi posati. mode 'ucx': solo gli UCX di calpestio (zmax locale <= 3 cm, niente colonnine/corrimano);
    'vis': facce LOD0 rivolte in alto con z locale <= 6 cm (niente gallocce, bitte, colonnine)."""
    verts, polys = [], []
    for a, n, x, y, z, rz, pitch, var in prow:
        if a in ("SM_Morin_Marina_Colonnina", "SM_Morin_Marina_Circolo"):
            continue
        M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ \
            Matrix.Rotation(math.radians(-pitch), 4, "Y")
        if mode == "ucx":
            srcs = [o for o in bpy.data.objects if o.name.startswith(f"UCX_{a}_")]
            srcs = [o for o in srcs if max(v.co.z for v in o.data.vertices) <= 0.03]
        else:
            srcs = [bpy.data.objects[a]]
        for o in srcs:
            me = o.data
            base = len(verts)
            verts += [M @ v.co for v in me.vertices]
            for p in me.polygons:
                if mode == "vis" and (p.normal.z < 0.5 or p.center.z > 0.06):
                    continue
                polys.append([base + i for i in p.vertices])
    return BVHTree.FromPolygons(verts, polys)


def _region_v3(step=0.10, inset=0.05, inset_vis=0.15):
    """Punti della griglia globale (passo 10 cm) dentro i calpestii attesi, con l'etichetta della catena.
    Ritorna dict (ix, iy) -> [x, y, catena, bordo]: bordo = True se il punto e' entro inset_vis dal bordo."""
    ax = _axis_v3()
    segs = []           # (catena, a, b, hw, giunto tondo in a, giunto tondo in b)
    for k, pts in ax.items():
        for i in range(len(pts) - 1):
            segs.append((k, pts[i], pts[i + 1], HW, i > 0, i < len(pts) - 2 or k == "Spina"))
    for nm, x in PASSERELLE:
        segs.append((f"Passerella_{nm}", (x, yq(x)), (x, yq(x) - GANG), HW, False, False))
    a, b = LARGO
    segs.append(("Largo", a, b, LARGO_W / 2, False, False))
    pts = {}
    for k, a, b, hw, ca, cb in segs:
        d, L = _unit(a, b)
        n = (-d[1], d[0])
        lim = hw - inset
        x0, x1 = min(a[0], b[0]) - hw, max(a[0], b[0]) + hw
        y0, y1 = min(a[1], b[1]) - hw, max(a[1], b[1]) + hw
        gx = np.arange(math.floor(x0 / step), math.ceil(x1 / step) + 1)
        gy = np.arange(math.floor(y0 / step), math.ceil(y1 / step) + 1)
        GX, GY = np.meshgrid(gx, gy)
        X, Y = GX * step, GY * step
        u = (X - a[0]) * d[0] + (Y - a[1]) * d[1]
        v = (X - a[0]) * n[0] + (Y - a[1]) * n[1]
        ins = (np.abs(v) <= lim) & (u >= 0) & (u <= L)
        if ca:
            ins |= np.hypot(X - a[0], Y - a[1]) <= lim
        if cb:
            ins |= np.hypot(X - b[0], Y - b[1]) <= lim
        edge = (np.abs(v) > hw - inset_vis) | (u < 0) | (u > L)
        for ix, iy, e in zip(GX[ins], GY[ins], edge[ins]):
            key = (int(ix), int(iy))
            if key not in pts:
                pts[key] = [float(ix) * step, float(iy) * step, k, bool(e)]
            elif not e:
                pts[key][3] = False
    return pts


def verify_v3(prow, step=0.10, max_step=0.05):
    pts = _region_v3(step)
    res = {}
    for mode in ("ucx", "vis"):
        bvh = _placed_bvh(prow, mode)
        Z = {}
        holes = []
        for key, (x, y, k, edge) in pts.items():
            if mode == "vis" and edge:
                continue
            hit = bvh.ray_cast(Vector((x, y, 2.0)), Vector((0, 0, -1)), 4.0)
            if hit[0] is None or hit[0].z < -0.60:
                holes.append((round(x, 2), round(y, 2), k))
            else:
                Z[key] = hit[0].z
        steps = []
        dzmax = 0.0
        for (ix, iy), z in Z.items():
            for nb in ((ix + 1, iy), (ix, iy + 1)):
                if nb in Z:
                    dz = abs(Z[nb] - z)
                    dzmax = max(dzmax, dz)
                    if dz > max_step:
                        steps.append((round(ix * step, 2), round(iy * step, 2), round(dz, 3), pts[(ix, iy)][2]))
        zs = np.array(list(Z.values()))
        per = {}
        for key in Z:
            per[pts[key][2]] = per.get(pts[key][2], 0) + 1
        res[mode] = dict(punti=len(Z) + len(holes), buchi=len(holes), buchi_es=holes[:12], gradini=len(steps),
                         gradini_es=steps[:12], dz_max=round(dzmax, 4), z_min=round(float(zs.min()), 3),
                         z_max=round(float(zs.max()), 3), per_catena=per)
    return res


def _deck_rects_v3(prow):
    """Impronte (con bottazzo) dei pezzi posati v3: rettangoli orientati e cerchi."""
    out = []
    for a, n, x, y, z, rz, pitch, var in prow:
        d = (math.cos(math.radians(rz)), math.sin(math.radians(rz)))
        if a in ("SM_Mirabello_Pontile_Col", "SM_Morin_Marina_Pontile12"):
            L = 48.0 if a == "SM_Mirabello_Pontile_Col" else 12.0
            out.append(("r", ((x + d[0] * L / 2, y + d[1] * L / 2), d, L / 2, HW + BOTT)))
        elif a == "SM_Morin_Marina_Raccordo":
            out.append(("c", ((x, y), RACC_R + RACC_BOTT)))
    return out


def boats_clearance_v3(prow, seed=20261120):
    """Distanza minima fra le barche v2 (stesso seme: stesso layout del CSV v2) e i pezzi v3."""
    boats, _ = layout_v2(seed)
    deck = _deck_rects_v3(prow)
    worst = (1e9, None)
    under = []
    for b in boats:
        r = b["rect"]
        for kind, s in deck:
            if kind == "r":
                if math.hypot(r[0][0] - s[0][0], r[0][1] - s[0][1]) > 40:
                    continue
                dd = _poly_dist(r, s)
            else:
                c, rad = s
                if math.hypot(r[0][0] - c[0], r[0][1] - c[1]) > 20:
                    continue
                cs = _corners(r)
                inside = _sat(r, ((c[0], c[1]), (1.0, 0.0), 1e-6, 1e-6))
                dd = 0.0 if inside else min(_dist_pt_seg(c, cs[i], cs[(i + 1) % 4]) for i in range(4)) - rad
                dd = max(dd, 0.0)
            if dd < worst[0]:
                worst = (dd, b["pontile"])
            if dd < MARGIN - 1e-6:
                under.append((b["pontile"], round(dd, 3)))
    return dict(barche=len(boats), min_dist=round(worst[0], 3), pontile=worst[1], sotto_margine=under[:10],
                n_sotto=len(under))
