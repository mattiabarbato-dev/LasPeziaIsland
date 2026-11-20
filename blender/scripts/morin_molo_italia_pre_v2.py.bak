"""morin_molo_italia.py — Blocco 3: Molo Italia v1 (2026-11-20).

Scheda: ref/molo_italia.md (geo-scout 2026-11-20, 17 foto [F]), ref/blocco2.md §4.5 (raccordo). OSM ref/osm/morin_blocchi23.osm
(© OpenStreetMap contributors, ODbL). Foto dell'utente in ref/foto/vista/ (Street View [SV] e vista satellitare: per decisione
dell'utente del 2026-11-20 tutte utilizzabili; nelle texture niente persone, targhe, interfaccia).

Esegui dentro blender/arte_molo_italia.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_molo_italia as mi; importlib.reload(mi)
    mi.link_kit()            # kit esistenti collegati (solo per i render; in UEFN sono gia' importati)
    mi.make_textures()       # blender/textures/molo_italia/ (D sRGB, N DirectX, ORM)
    mi.build_materials()
    rep = mi.build_all()     # asset nuovi LOD0/1/2 + UCX (collezione MI_Kit)
    rows = mi.layout()       # posizioni (coordinate Blender)
    mi.write_csv(rows)       # exports/molo_italia/molo_italia_posizioni_v1.csv (coordinate UE)
    mi.build_context(rows)   # istanze per i render (MI_Contesto) + fine del Blocco 2
    mi.export_all()

Convenzioni: X lungo la passeggiata verso NE, Y verso la citta', Z su; UE = (X*100, -Y*100, Z*100), yaw UE = -rotZ.
Quote: piano del molo Z 0 (come la banchina), marciapiede lato mare aperto Z +0,12, acqua (Acqua V2) Z -1,03.
Pezzi unici del suolo, edifici e monumento: geometria in coordinate di progetto, origine (0,0,0), si posano in (0,0,0).
Faro, ristorante, lampione, ringhiera, scogliera, dito, barche: origine alla base, si posano dal CSV.
Nomi parodia (decisione dell'utente 2026-11-20): ristorante "I Piccioni" (I Gabbiani), rimorchiatori "Tiramolla",
"Spingitutto", "Ostinato", nave da crociera "Piccionissima". Nomi pubblici reali tenuti: "GUARDIA COSTIERA".
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk

PROJ = pk.PROJ
KIT = "MI_Kit"
CTX = "MI_Contesto"
EXPDIR = "//../exports/molo_italia"
TEXDIR = PROJ + "/blender/textures/molo_italia"
BL = PROJ + "/blender/"
Z_W = -1.03                     # superficie dell'Acqua V2 in UEFN (docs/uefn_arte.md)
Z_MARC = 0.12                   # gradino del marciapiede [S] 10-15 cm
SEED = 20261121

# =============================================================================================================
# geometria OSM (coastline 137121074, ways 851135245, 205843153, 205839145, 205839033): coordinate di progetto
# =============================================================================================================
B_LINE = [(571.8, 41.6), (571.8, -198.9), (689.1, -322.0)]      # lato bacino (radice -> gomito -> testata)
O_LINE = [(555.1, 41.6), (556.4, -204.9), (677.5, -332.6)]      # lato mare aperto (scogliera)
TESTATA = ((677.5, -332.6), (689.1, -322.0))
Y_RADICE_B = 1.3                # da qui verso nord il lato est e' terraferma (calata, edifici)
DITA = {"D1": ((573.45, -111.4), (622.5, -110.7)), "D2": ((573.3, -156.8), (622.45, -155.35))}
DITO_L, DITO_W = 49.5, 6.0
RIST = (574.45, 593.85, -56.95, -46.65)       # chiatta (OSM 851135245): X 574,4-593,9, Y -57,0 … -46,6 [V]
FARO_XY = (678.6, -327.1)                      # OSM node 1327347929 [V]
CAPITANERIA = [(592.7, 80.3), (617.2, 80.5), (617.3, 67.9), (607.1, 67.8), (607.4, 44.4), (593.1, 44.2)]
EDIF_4P = [(579.2, 19.3), (593.6, 19.3), (593.5, 40.6), (579.2, 40.6)]
EDIF_EST = [(615.9, 19.6), (630.6, 19.9), (630.1, 41.1), (615.4, 40.8)]
INFOPOINT = [(584.95, 107.05), (603.45, 106.8), (620.95, 107.05)]
MONUMENTO_C = (552.6, 42.8)                    # lunetta con stele e busto [F] MO (~553; 46 ±5 m): bordo nord a Y 47,05 contro il piazzale B2
RADICE_X1 = 640.0                              # limite est del suolo giocabile della radice [S]
Y_VIALE = 120.85                               # inizio di Viale Italia / terreno del Blocco 2
PIAZZALE_X1 = 566.0                            # fine del piazzale in cubetti del Blocco 2 (SM_Pav_Piazzale_Fine_B2)


def _v2(p):
    return Vector((p[0], p[1]))


def seg_dir(a, b):
    return (_v2(b) - _v2(a)).normalized()


def _right(d):
    return Vector((d.y, -d.x))


def _left(d):
    return Vector((-d.y, d.x))


def offset_line(P, dist, side):
    """Offset con giunti a spigolo vivo (miter). side: 'r' o 'l' rispetto al verso della polilinea."""
    P = [_v2(p) for p in P]
    nrm = _right if side == "r" else _left
    out = []
    for i, p in enumerate(P):
        ds = []
        if i > 0:
            ds.append(nrm((p - P[i - 1]).normalized()))
        if i < len(P) - 1:
            ds.append(nrm((P[i + 1] - p).normalized()))
        if len(ds) == 1:
            out.append(p + ds[0] * dist)
        else:
            m = (ds[0] + ds[1]).normalized()
            out.append(p + m * (dist / m.dot(ds[0])))
    return out


def along(P, step, start=0.0, end_margin=0.0):
    """Punti (pos, dir, s) ogni `step` metri lungo la polilinea."""
    P = [_v2(p) for p in P]
    out, s0 = [], 0.0
    total = sum((P[i + 1] - P[i]).length for i in range(len(P) - 1))
    s = start
    while s <= total - end_margin + 1e-6:
        acc = 0.0
        for i in range(len(P) - 1):
            L = (P[i + 1] - P[i]).length
            if s <= acc + L + 1e-9:
                d = (P[i + 1] - P[i]).normalized()
                out.append((P[i] + d * (s - acc), d, s))
                break
            acc += L
        s += step
    return out, total


def yaw_of(d):
    return math.degrees(math.atan2(d.y, d.x))


# =============================================================================================================
# kit esistenti (link, sola lettura)
# =============================================================================================================
KIT_SRC = {
    "arte_banchina_v2": ["SM_Banchina_Mod4m_v2", "SM_Banchina_Bitta_v2"],
    "arte_pavimentazione": ["SM_Morin_Panchina", "SM_Morin_PalmaA", "SM_Morin_Lampione"],
    "arte_parcheggio": ["SM_Morin_NewJersey", "SM_Morin_Auto_A_Col_v2_Rosso", "SM_Morin_Auto_A_Col_v2_Bianco",
                        "SM_Morin_Auto_A_Col_v2_Azzurro", "SM_Morin_Auto_B_Col_v2_GrigioScuro", "SM_Morin_Auto_B_Col_v2_Argento",
                        "SM_Morin_Auto_B_Col_v2_Arancio", "SM_Morin_Auto_C_Col_v2_Nero", "SM_Morin_Auto_C_Col_v2_BluScuro",
                        "SM_Morin_Auto_C_Col_v2_BiancoPerla"],
    "arte_imbarco": ["SM_Morin_Battello", "SM_Morin_Cestino"],
    "arte_molo": ["SM_Morin_PinoDomestico"],
    "arte_blocco2": ["SM_Pav_Piazzale_Fine_B2_v2", "SM_Banchina_Angolo_MoloItalia", "SM_Morin_AstaBandiera",
                     "SM_Morin_Bandiera_Italia", "SM_Morin_Bandiera_Comune", "SM_Morin_Bandiera_Aquile",
                     "SM_Morin_ChioscoOttagonale_v2", "SM_Pav_Piazzetta_Chiosco_B2", "SM_Pav_Scritta_Morin",
                     "SM_Morin_ScrittaLaSpezia", "SM_Morin_Cannone"],
}
KIT_MAT_SRC = {"arte_pavimentazione": ["M_Morin_Ghisa", "M_Morin_Globo", "M_Pav_Fascia", "M_Pav_Cubetti"],
               "arte_molo": ["M_Molo_Asfalto"],
               "arte_banchina_v2": ["M_Banchina_Paramento", "M_Banchina_Blocchi"]}
AUTO_COL = KIT_SRC["arte_parcheggio"][1:]
KIT_MESH = {}


def link_kit():
    for f, names in KIT_SRC.items():
        with bpy.data.libraries.load(BL + f + ".blend", link=True) as (src, dst):
            dst.objects = [n for n in names if n in src.objects]
        for o in dst.objects:
            if o is not None:
                KIT_MESH[o.name] = o.data
    for f, names in KIT_MAT_SRC.items():
        with bpy.data.libraries.load(BL + f + ".blend", link=True) as (src, dst):
            dst.materials = [n for n in names if n in src.materials and n not in bpy.data.materials]
    missing = [n for v in KIT_SRC.values() for n in v if n not in KIT_MESH]
    print("kit collegati:", len(KIT_MESH), "mancanti:", missing)
    return KIT_MESH


# =============================================================================================================
# texture
# =============================================================================================================
SW_N = 8                         # atlante delle tinte: 8 x 8 campioni da 128 px (1024)
TINTE = {   # nome: (sRGB, rugosita', metallo)
    "giallo_vernice": ((228, 186, 38), 0.65, 0.0), "bianco_vernice": ((232, 232, 226), 0.65, 0.0),
    "rosso_faro": ((196, 28, 32), 0.42, 0.25), "nero": ((26, 26, 28), 0.55, 0.0), "vetro": ((38, 52, 62), 0.08, 0.3),
    "vetro_lanterna": ((205, 218, 218), 0.08, 0.1), "bianco": ((238, 238, 233), 0.5, 0.0), "blu_scafo": ((28, 52, 138), 0.4, 0.1),
    "giallo_rist": ((246, 206, 44), 0.6, 0.0), "metallo": ((150, 152, 155), 0.35, 0.9), "zincato": ((172, 174, 172), 0.4, 0.85),
    "legno": ((118, 80, 46), 0.75, 0.0), "bronzo": ((96, 72, 42), 0.4, 0.9), "pietra_chiara": ((204, 198, 182), 0.8, 0.0),
    "verde_acqua": ((86, 148, 138), 0.5, 0.0), "verde_scuro": ((38, 68, 48), 0.6, 0.2), "rosso_rimorch": ((150, 32, 30), 0.5, 0.0),
    "nero_scafo": ((30, 30, 33), 0.5, 0.0), "telo_bianco": ((232, 232, 226), 0.85, 0.0), "grigio_serranda": ((128, 130, 134), 0.5, 0.6),
    "arancio": ((228, 108, 32), 0.6, 0.0), "grigio_scuro": ((70, 72, 76), 0.6, 0.2), "cemento": ((176, 173, 166), 0.88, 0.0),
    "gomma": ((22, 22, 22), 0.9, 0.0), "blu_insegna": ((28, 76, 168), 0.5, 0.0), "rosso_insegna": ((188, 40, 40), 0.5, 0.0),
    "verde_prato": ((72, 108, 46), 0.92, 0.0), "luce_rossa": ((255, 46, 34), 0.2, 0.0), "antracite": ((52, 56, 58), 0.45, 0.6),
    "bianco_scafo": ((240, 241, 240), 0.35, 0.0), "grigio_chiaro": ((196, 198, 200), 0.5, 0.2), "mattone": ((168, 82, 58), 0.85, 0.0),
    "blu_scuro": ((20, 30, 60), 0.5, 0.0), "verde_tapparella": ((60, 110, 80), 0.6, 0.0), "fumaiolo": ((40, 40, 44), 0.5, 0.3),
}
SW_IDX = {k: i for i, k in enumerate(TINTE)}


def sw_rect(name):
    i = SW_IDX[name]
    c, r = i % SW_N, i // SW_N
    return c / SW_N, 1 - (r + 1) / SW_N, (c + 1) / SW_N, 1 - r / SW_N      # u0, v0, u1, v1 (v dal basso)


def _noise(h, w, sigma, seed):
    import morin_texphoto as tp
    r = np.random.default_rng(seed).standard_normal((h, w)).astype(np.float32)
    r = tp.blur(r, sigma)
    return r / (r.std() + 1e-6)


def _save_set(base, D, H, R, M, nstr=2.0, alpha=None):
    import morin_texphoto as tp
    os.makedirs(TEXDIR, exist_ok=True)
    n = tp.normal_dx(H.astype(np.float32), nstr)
    ao = np.clip(1.0 - 6.0 * np.maximum(tp.blur(H, 6.0) - H, 0), 0.35, 1.0)
    d = np.clip(D, 0, 1)
    if alpha is not None:
        d = np.dstack([d, alpha])
    tp.save(d, f"{TEXDIR}/{base}_D.png")
    tp.save(n, f"{TEXDIR}/{base}_N.png")
    tp.save(np.dstack([ao, np.clip(R, 0.04, 1), M]).astype(np.float32), f"{TEXDIR}/{base}_ORM.png")
    return base


def make_tex_tinte(S=1024):
    """Atlante di tinte piatte con un velo di rumore (vernici, lamiere, vetri)."""
    C = S // SW_N
    D = np.zeros((S, S, 3), np.float32)
    H = np.zeros((S, S), np.float32)
    R = np.zeros((S, S), np.float32)
    M = np.zeros((S, S), np.float32)
    for k, (col, rough, met) in TINTE.items():
        i = SW_IDX[k]
        c, r = i % SW_N, i // SW_N
        y0, x0 = r * C, c * C
        n = _noise(C, C, 2.0, i) * 0.03 + _noise(C, C, 14.0, i + 50) * 0.03
        D[y0:y0 + C, x0:x0 + C] = (np.asarray(col, np.float32) / 255.0)[None, None] * (1 + n[..., None])
        H[y0:y0 + C, x0:x0 + C] = 0.5 + 0.02 * n
        R[y0:y0 + C, x0:x0 + C] = rough + 0.05 * n
        M[y0:y0 + C, x0:x0 + C] = met
    return _save_set("T_MoloItalia_Tinte", D, H, R, M, nstr=1.0)


def make_tex_cemento(S=2048):
    """Cemento chiaro consumato del marciapiede e del coronamento, con riquadri di lastre rattoppate (molo_italia_2/4/7).
    Base Poly Haven concrete_floor_worn_001 (CC0) ritarata sul cemento delle foto."""
    import morin_texphoto as tp
    src = PROJ + "/blender/textures/src/concrete_floor_worn_001/concrete_floor_worn_001_"
    d = tp.load(src + "diff_2k.jpg")[..., :3] ** 2.2
    d = tp.resize(d, S, S) if d.shape[0] != S else d
    lum = d.mean(axis=2)
    lum = (lum - lum.mean()) / (lum.std() + 1e-6)
    base = np.array([0.43, 0.41, 0.375])                    # cemento chiaro (lineare) [F] molo_italia_2, _7
    rgb = base[None, None] * (1 + 0.10 * lum[..., None])
    rng = np.random.default_rng(3)
    H = 0.5 + 0.04 * lum
    for _ in range(9):                                       # riquadri di lastre di pietra chiara
        w, h = rng.integers(200, 520, 2)
        x, y = rng.integers(0, S - w), rng.integers(0, S - h)
        rgb[y:y + h, x:x + w] = rgb[y:y + h, x:x + w] * 0.6 + np.array([0.52, 0.49, 0.43]) * 0.4
        for k in range(0, w, 128):
            rgb[y:y + h, x + k:x + k + 4] *= 0.55
            H[y:y + h, x + k:x + k + 4] -= 0.08
        for k in range(0, h, 96):
            rgb[y + k:y + k + 4, x:x + w] *= 0.55
            H[y + k:y + k + 4, x:x + w] -= 0.08
    for _ in range(14):                                      # macchie e rattoppi
        r0 = rng.integers(40, 180)
        cx, cy = rng.integers(0, S, 2)
        yy, xx = np.ogrid[:S, :S]
        m = np.clip(1 - np.hypot(xx - cx, yy - cy) / r0, 0, 1) ** 1.5
        rgb *= (1 - 0.18 * m[..., None])
    n = tp.load(src + "nor_dx_2k.jpg")[..., :3]
    rough = 0.82 + 0.08 * _noise(S, S, 20, 4) * 0.5
    out = _save_set("T_MoloItalia_Cemento", rgb ** (1 / 2.2), H, rough, np.zeros_like(rough), nstr=1.5)
    tp.save(tp.resize(n, S, S) if n.shape[0] != S else n, f"{TEXDIR}/T_MoloItalia_Cemento_N.png")
    return out


def make_tex_scogliera(S=1024):
    """Massi grigio-ocra della scogliera con alghe scure nella parte bassa (v: 0 = acqua), procedurale [F] molo_italia_5/6."""
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    n1 = _noise(S, S, 3, 11)
    n2 = _noise(S, S, 18, 12)
    n3 = _noise(S, S, 60, 13)
    H = 0.5 + 0.12 * n1 + 0.25 * n2 + 0.2 * n3
    grey = np.array([0.22, 0.21, 0.19])
    ocra = np.array([0.33, 0.27, 0.18])
    t = np.clip(0.5 + 0.5 * n3, 0, 1)[..., None]
    rgb = grey * (1 - t) + ocra * t
    rgb = rgb * (1 + 0.12 * n1[..., None] + 0.08 * n2[..., None])
    v = 1 - yy / S                                       # 0 in basso
    alg = np.clip((0.22 - v) / 0.14 + 0.15 * n2, 0, 1)[..., None]
    rgb = rgb * (1 - alg) + np.array([0.05, 0.07, 0.04]) * alg
    crack = np.clip(1 - np.abs(_noise(S, S, 5, 14)) * 6, 0, 1)
    rgb *= (1 - 0.35 * crack[..., None])
    H -= 0.15 * crack
    R = 0.85 - 0.25 * alg[..., 0]
    return _save_set("T_Molo_Scogliera", np.clip(rgb, 0, 1) ** (1 / 2.2), H, R, np.zeros_like(R), nstr=3.0)


BAY_W, FLOOR_H = 3.6, 4.5          # campata e interpiano della facciata (atlante = 1 campata x 1 piano)


def make_tex_facciata(S=1024):
    """Mattoni rossi a vista con marcapiano chiaro e finestra alta con infissi verde acqua (Capitaneria, edificio a 4 piani)
    [F] guardia_costiera_molo_italia.png. Una tessera = una campata (3,6 m) x un piano (4,5 m)."""
    W, Hh = S, S
    ppm_x, ppm_y = W / BAY_W, Hh / FLOOR_H
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    zm = (Hh - yy) / ppm_y                             # quota nel piano (m), 0 in basso
    um = xx / ppm_x
    rng = np.random.default_rng(7)
    bh, bw = 0.075, 0.25                              # corso e mattone
    row = np.floor(zm / bh)
    off = (row % 2) * bw / 2
    col = np.floor((um + off) / bw)
    rnd = np.random.default_rng(8).random((int(row.max()) + 2, int(col.max()) + 3)).astype(np.float32)
    tone = rnd[row.astype(int), col.astype(int)]
    base = np.array([0.40, 0.13, 0.075])
    rgb = base[None, None] * (0.85 + 0.3 * tone[..., None])
    mort = ((zm % bh) < 0.010) | (((um + off) % bw) < 0.010)
    rgb[mort] = np.array([0.42, 0.38, 0.33])
    H = 0.55 - 0.12 * mort
    R = np.full((Hh, W), 0.88, np.float32)
    M = np.zeros((Hh, W), np.float32)
    band = zm < 0.30                                 # marcapiano chiaro
    rgb[band] = np.array([0.55, 0.52, 0.46])
    H[band] = 0.62
    wx0, wx1, wz0, wz1 = 1.15, 2.45, 1.10, 3.55        # finestra
    fr = 0.09
    win = (um > wx0) & (um < wx1) & (zm > wz0) & (zm < wz1)
    rgb[win] = np.array([0.10, 0.22, 0.20])           # infisso verde acqua (scuro in ombra)
    glass = (um > wx0 + fr) & (um < wx1 - fr) & (zm > wz0 + fr) & (zm < wz1 - fr) & \
            ~((np.abs(um - (wx0 + wx1) / 2) < 0.03)) & ~((np.abs(zm - 2.85) < 0.03))
    rgb[glass] = np.array([0.05, 0.07, 0.09])
    R[glass] = 0.08
    H[win] = 0.35
    H[glass] = 0.30
    sill = (um > wx0 - 0.08) & (um < wx1 + 0.08) & (zm > wz0 - 0.10) & (zm < wz0)
    rgb[sill] = np.array([0.55, 0.52, 0.46])
    H[sill] = 0.7
    rgb = rgb * (1 + 0.05 * _noise(Hh, W, 30, 9)[..., None])
    return _save_set("T_MoloItalia_Facciata", np.clip(rgb, 0, 1) ** (1 / 2.2), H, R, M, nstr=2.5)


def make_textures():
    return [make_tex_tinte(), make_tex_cemento(), make_tex_scogliera(), make_tex_facciata()]


MAT_TEX = {"M_MoloItalia_Tinte": "T_MoloItalia_Tinte", "M_MoloItalia_Cemento": "T_MoloItalia_Cemento",
           "M_Molo_Scogliera": "T_Molo_Scogliera", "M_MoloItalia_Facciata": "T_MoloItalia_Facciata",
           "M_MoloItalia_FaroLuce": "T_MoloItalia_Tinte"}
pk.TILE.update({"M_MoloItalia_Cemento": 4.0, "M_Molo_Scogliera": 2.5, "M_Molo_Asfalto": 4.0})


def build_materials():
    for m, t in MAT_TEX.items():
        pk._pbr_material(m, f"{TEXDIR}/{t}_D.png", f"{TEXDIR}/{t}_N.png", f"{TEXDIR}/{t}_ORM.png")
    # lanterna del faro: emissiva rossa (in UEFN una MI che lampeggia Fl R 4s: 1 s acceso, 3 s spento)
    mat = bpy.data.materials["M_MoloItalia_FaroLuce"]
    b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Emission Color"].default_value = (1.0, 0.05, 0.03, 1.0)
    b.inputs["Emission Strength"].default_value = 8.0
    for m in ("M_Morin_Ghisa", "M_Morin_Globo", "M_Molo_Asfalto", "M_Pav_Fascia", "M_Pav_Cubetti", "M_Banchina_Paramento"):
        assert m in bpy.data.materials, m
    return True


# =============================================================================================================
# costruttore di geometria con UV per faccia (tinta dell'atlante o proiezione "mondo" a piastrelle)
# =============================================================================================================
class G:
    def __init__(self, mats):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.mats = list(mats)

    def _mi(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    def _since(self, n0):
        self.bm.faces.ensure_lookup_table()
        return list(self.bm.faces)[n0:]

    def tag(self, faces, mat, sw=None, tile=None, uvfn=None):
        mi = self._mi(mat)
        for f in faces:
            f.material_index = mi
            f.normal_update()
            if uvfn is not None:
                for lp in f.loops:
                    lp[self.uv].uv = uvfn(lp.vert.co, f)
            elif sw is not None:
                self._uv_sw(f, sw)
            else:
                self._uv_tile(f, tile or pk.TILE.get(mat, 1.0))
        return faces

    def _proj(self, f):
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        return [(lp.vert.co[a], lp.vert.co[b]) for lp in f.loops]

    def _uv_sw(self, f, sw):
        u0, v0, u1, v1 = sw_rect(sw)
        cs = self._proj(f)
        mx, my = min(c[0] for c in cs), min(c[1] for c in cs)
        ext = max(max(c[0] for c in cs) - mx, max(c[1] for c in cs) - my, 1e-3)
        for lp, (x, y) in zip(f.loops, cs):
            lp[self.uv].uv = (u0 + (u1 - u0) * (0.2 + 0.6 * (x - mx) / ext), v0 + (v1 - v0) * (0.2 + 0.6 * (y - my) / ext))

    def _uv_tile(self, f, t):
        n = f.normal
        for lp in f.loops:
            c = lp.vert.co
            if abs(n.z) > 0.7:
                lp[self.uv].uv = (c.x / t, c.y / t)
            elif abs(n.x) > abs(n.y):
                lp[self.uv].uv = (c.y / t, c.z / t)
            else:
                lp[self.uv].uv = (c.x / t, c.z / t)

    def run(self, fn, *a, mat="M_MoloItalia_Tinte", sw=None, tile=None, uvfn=None, **k):
        n0 = len(self.bm.faces)
        fn(self.bm, *a, **k)
        return self.tag(self._since(n0), mat, sw, tile, uvfn)

    def quad(self, pts, mat="M_MoloItalia_Tinte", sw=None, tile=None, uvfn=None, face=None):
        """face: direzione verso cui deve guardare la normale (la faccia viene girata se serve)."""
        f = self.bm.faces.new([self.bm.verts.new(p) for p in pts])
        f.normal_update()
        if face is not None and f.normal.dot(Vector(face)) < 0:
            f.normal_flip()
        return self.tag([f], mat, sw, tile, uvfn)

    def quad2(self, pts, mat="M_MoloItalia_Tinte", sw=None, tile=None):
        """Quad a doppia faccia (teli, cartelli sottili)."""
        f = self.quad(pts, mat, sw, tile)[0]
        n = f.normal * -0.004
        return self.quad([tuple(Vector(p) + n) for p in pts[::-1]], mat, sw, tile)

    def poly(self, pts, z, mat, sw=None, tile=None, flip=False):
        vs = [self.bm.verts.new((p[0], p[1], z)) for p in pts]
        f = self.bm.faces.new(vs)
        f.normal_update()
        if (f.normal.z < 0) != flip:
            f.normal_flip()
        n0 = len(self.bm.faces) - 1
        res = bmesh.ops.triangulate(self.bm, faces=[f], quad_method="BEAUTY", ngon_method="EAR_CLIP")
        return self.tag(res["faces"], mat, sw, tile)

    def box(self, x0, x1, y0, y1, z0, z1, mat="M_MoloItalia_Tinte", sw=None, tile=None, M=None,
            faces=("top", "bot", "xn", "xp", "yn", "yp")):
        return self.run(pk._box, x0, x1, y0, y1, z0, z1, 0, faces, M, mat=mat, sw=sw, tile=tile)

    def lathe(self, prof, n, M=Matrix(), mat="M_MoloItalia_Tinte", sw=None, tile=None, cap_top=True, phase=0.0):
        return self.run(pk._lathe, prof, n, M, 0, cap_top, phase, mat=mat, sw=sw, tile=tile)

    def tube(self, pts, r, sides, mat="M_MoloItalia_Tinte", sw=None, cap=True):
        return self.run(pk._tube, pts, r, sides, 0, cap, mat=mat, sw=sw)

    def prism(self, poly, z0, z1, mat, sw=None, tile=None, top=True, bot=False, uv_wall=None):
        """Prisma verticale da poligono 2D (antiorario)."""
        bm = self.bm
        a = [bm.verts.new((x, y, z0)) for x, y in poly]
        b = [bm.verts.new((x, y, z1)) for x, y in poly]
        out = []
        for i in range(len(poly)):
            j = (i + 1) % len(poly)
            f = bm.faces.new([a[i], a[j], b[j], b[i]])
            f.normal_update()
            out.append(f)
            if uv_wall is not None:          # facciata: u = campate intere, v = piani
                L = (Vector(poly[j]) - Vector(poly[i])).length
                bw, fh = uv_wall
                nb = max(1, round(L / bw))
                f.material_index = self._mi(mat)
                for lp, (uu, zz) in zip(f.loops, ((0, z0), (nb, z0), (nb, z1), (0, z1))):
                    lp[self.uv].uv = (uu, zz / fh)
            else:
                self.tag([f], mat, sw, tile)
        if top:
            ft = bm.faces.new(b)
            self.tag([ft], mat, sw, tile)
            out.append(ft)
        if bot:
            fb = bm.faces.new(list(reversed(a)))
            self.tag([fb], mat, sw, tile)
        return out

    def text(self, body, size, depth, M, mat="M_MoloItalia_Tinte", sw="nero", resol=2, align="CENTER"):
        """Testo estruso (font interno di Blender): piano XY del font, spessore su +Z, poi trasformato con M."""
        cu = bpy.data.curves.new("_tmp_mi_txt", "FONT")
        cu.body = body
        cu.size = size
        cu.extrude = depth / 2
        cu.resolution_u = resol
        cu.align_x = align
        ob = bpy.data.objects.new("_tmp_mi_txt", cu)
        bpy.context.scene.collection.objects.link(ob)
        bpy.context.view_layer.update()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        me.transform(M @ Matrix.Translation((0, 0, depth / 2)))
        n0 = len(self.bm.faces)
        self.bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        fs = self._since(n0)
        ng = [f for f in fs if len(f.verts) > 4]
        if ng:
            bmesh.ops.triangulate(self.bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
        return self.tag(self._since(n0), mat, sw)

    def finish(self, name, coll, smooth=None):
        bm = self.bm
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bad = [f for f in bm.faces if f.calc_area() < 1e-7]
        if bad:
            bmesh.ops.delete(bm, geom=bad, context="FACES")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        for l in list(bm.loops.layers.uv.keys()):
            if l != "UVMap":
                bm.loops.layers.uv.remove(bm.loops.layers.uv[l])
        o = pk._finish(name, bm, self.mats, coll, uv=None, smooth_angle=smooth)
        for l in [l for l in o.data.uv_layers if l.name != "UVMap"]:
            o.data.uv_layers.remove(l)
        return o


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


def _clear_ucx(name):
    for u in [x for x in bpy.data.objects if x.name.startswith(f"UCX_{name}_")]:
        bpy.data.objects.remove(u)


def _ucx_hull(name, idx, pts, coll):
    pk._ucx_hull(name, idx, [tuple(p) for p in pts], coll)


def _ucx_obox(name, idx, p0, p1, w0, w1, z0, z1, coll):
    """Box orientato lungo il segmento p0-p1 (2D), da w0 a w1 a sinistra del verso, quote z0-z1."""
    d = seg_dir(p0, p1)
    n = _left(d)
    pts = []
    for p in (_v2(p0), _v2(p1)):
        for w in (w0, w1):
            q = p + n * w
            for z in (z0, z1):
                pts.append((q.x, q.y, z))
    _ucx_hull(name, idx, pts, coll)


# =============================================================================================================
# 1. suolo del molo: fasce della sezione (§2.2) lungo le due polilinee
# =============================================================================================================
OFF_MOD = 0.55        # coronamento coperto dal modulo banchina (bv.D)
OFF_CEM = 1.20        # fine del coronamento in cemento (lato bacino)
OFF_GIALLA = (1.75, 1.87)
W_MARC = 4.30         # marciapiede lato mare aperto [S] 4-4,5 m


def section_lines():
    B = [_v2(p) for p in B_LINE]
    O = [_v2(p) for p in O_LINE]
    # B va dalla radice alla testata con il bacino a sinistra: verso l'interno del molo = destra
    return {"B": B, "B1": offset_line(B, OFF_MOD, "r"), "B2": offset_line(B, OFF_CEM, "r"),
            "Y0": offset_line(B, OFF_GIALLA[0], "r"), "Y1": offset_line(B, OFF_GIALLA[1], "r"),
            "O3": offset_line(O, W_MARC, "l"), "O": O}


def _band(g, L0, L1, z0, z1, mat, sw=None, tile=None):
    for i in range(len(L0) - 1):
        g.quad([(L0[i].x, L0[i].y, z0), (L1[i].x, L1[i].y, z1), (L1[i + 1].x, L1[i + 1].y, z1), (L0[i + 1].x, L0[i + 1].y, z0)],
               mat, sw, tile)


def _wall(g, L, za, zb, mat, sw=None, tile=None, rev=False):
    for i in range(len(L) - 1):
        a, b = (L[i], L[i + 1]) if not rev else (L[i + 1], L[i])
        g.quad([(a.x, a.y, za), (b.x, b.y, za), (b.x, b.y, zb), (a.x, a.y, zb)], mat, sw, tile)


def build_suolo_molo(coll, name="SM_MoloItalia_Suolo"):
    """Ramo 1 + gomito + ramo 2 + testata (pezzo unico, coordinate di progetto). Dal bacino: coronamento in cemento
    (dopo i moduli banchina), carreggiata in asfalto con la linea gialla continua, gradino di 12 cm, marciapiede in cemento,
    parete esterna fino a -1 m sotto la scogliera. Testata: parete in cemento fino a -3 m."""
    S = section_lines()
    g = G(["M_MoloItalia_Cemento", "M_Molo_Asfalto", "M_MoloItalia_Tinte"])
    _band(g, S["B1"], S["B2"], 0.0, 0.0, "M_MoloItalia_Cemento")
    _band(g, S["B2"], S["O3"], 0.0, 0.0, "M_Molo_Asfalto")
    _wall(g, S["O3"], 0.0, Z_MARC, "M_MoloItalia_Cemento", rev=True)          # alzata del gradino
    _band(g, S["O3"], S["O"], Z_MARC, Z_MARC, "M_MoloItalia_Cemento")
    _wall(g, S["O"], -1.0, Z_MARC, "M_MoloItalia_Cemento")                     # parete esterna (sotto: scogliera)
    # linea gialla continua e mezzeria tratteggiata (ramo 1, radice -> Y -60)
    _band(g, S["Y0"], S["Y1"], 0.004, 0.004, "M_MoloItalia_Tinte", sw="giallo_vernice")
    mid0, mid1 = S["B2"][0].lerp(S["O3"][0], 0.5), S["B2"][1].lerp(S["O3"][1], 0.5)
    d = (mid1 - mid0).normalized()
    n = _left(d)
    s = 2.0
    while True:
        p = mid0 + d * s
        if p.y < -60.0:
            break
        a, b = p, p + d * 3.0
        g.quad([(a.x - n.x * 0.06, a.y - n.y * 0.06, 0.004), (b.x - n.x * 0.06, b.y - n.y * 0.06, 0.004),
                (b.x + n.x * 0.06, b.y + n.y * 0.06, 0.004), (a.x + n.x * 0.06, a.y + n.y * 0.06, 0.004)], sw="bianco_vernice", face=(0, 0, 1))
        s += 6.0
    # testata: parete in cemento da O a B1 fino a -3 m, e chiusura del gradino
    tO, tB = S["O"][-1], S["B1"][-1]
    t3 = S["O3"][-1]
    for a, b, zt in ((tO, t3, Z_MARC), (t3, S["B2"][-1], 0.0), (S["B2"][-1], tB, 0.0)):
        g.quad([(a.x, a.y, -3.0), (b.x, b.y, -3.0), (b.x, b.y, zt), (a.x, a.y, zt)], "M_MoloItalia_Cemento")
    # radice (Y 41,6): chiusura del marciapiede verso la lunetta
    r3, rO = S["O3"][0], S["O"][0]
    g.quad([(r3.x, r3.y, 0.0), (rO.x, rO.y, 0.0), (rO.x, rO.y, Z_MARC), (r3.x, r3.y, Z_MARC)], "M_MoloItalia_Cemento")
    o = g.finish(name, coll)
    _clear_ucx(name)
    # UCX: un box orientato per ciascuna fascia e ciascun ramo (+ cuneo del gomito)
    k = 0
    for i in range(2):
        a, b = S["B"][i], S["B"][i + 1]
        d = seg_dir(a, b)
        # carreggiata+coronamento: da B (0) a O3; il marciapiede rialzato a parte
        Lb = [S["B"][i], S["B"][i + 1]]
        Lo3 = [S["O3"][i], S["O3"][i + 1]]
        Lo = [S["O"][i], S["O"][i + 1]]
        pts = [(p.x, p.y, z) for p in Lb + Lo3 for z in (-3.0, 0.0)]
        _ucx_hull(name, k, pts, coll); k += 1
        pts = [(p.x, p.y, z) for p in Lo3 + Lo for z in (-1.0, Z_MARC)]
        _ucx_hull(name, k, pts, coll); k += 1
    return o


def build_suolo_radice(coll, name="SM_MoloItalia_Suolo_Radice"):
    """Largo Fiorillo, calata e parcheggio della Capitaneria (asfalto Z 0) fra il piazzale del Blocco 2 (X 566) e X 640,
    da Y 1,85 (dietro i moduli banchina della calata) a Y 120,85. Stalli a pettine gialli del parcheggio della Guardia
    Costiera e degli stalli lungo l'edificio a 4 piani. Il giardino della Capitaneria e' nell'asset dell'edificio."""
    g = G(["M_Molo_Asfalto", "M_MoloItalia_Tinte", "M_MoloItalia_Cemento"])
    yb = Y_RADICE_B + OFF_MOD
    xb = 571.8 - OFF_MOD
    poly = [(555.1, 41.6), (xb, 41.6), (xb, Y_RADICE_B), (571.8, Y_RADICE_B), (571.8, yb), (RADICE_X1, yb), (RADICE_X1, Y_VIALE),
            (PIAZZALE_X1, Y_VIALE), (PIAZZALE_X1, 47.0), (555.0, 47.0)]
    g.poly(poly, 0.0, "M_Molo_Asfalto")
    for a, b in ((poly[5], poly[6]), (poly[6], poly[7])):
        g.quad([(a[0], a[1], -3.0), (b[0], b[1], -3.0), (b[0], b[1], 0.0), (a[0], a[1], 0.0)], "M_MoloItalia_Cemento")
    # parete verso la lunetta (X 555, Y 41,6-47): sotto c'e' il monumento
    g.quad([(555.0, 47.0, -1.0), (555.1, 41.6, -1.0), (555.1, 41.6, 0.0), (555.0, 47.0, 0.0)], "M_MoloItalia_Cemento")
    # stalli a pettine (parcheggio della Guardia Costiera, X 580,5-586, Y 47-80)
    for k in range(14):
        y = 47.5 + 2.5 * k
        g.quad([(580.5, y - 0.06, 0.004), (586.0, y - 0.06, 0.004), (586.0, y + 0.06, 0.004), (580.5, y + 0.06, 0.004)],
               sw="giallo_vernice", face=(0, 0, 1))
    for k in range(14):
        y = 47.5 + 2.5 * k
        g.quad([(570.0, y - 0.06, 0.004), (575.5, y - 0.06, 0.004), (575.5, y + 0.06, 0.004), (570.0, y + 0.06, 0.004)],
               sw="giallo_vernice", face=(0, 0, 1))
    # stalli in linea lungo l'edificio a 4 piani (X 576,5-578,8, Y 4-40)
    g.quad([(576.4, 4.0, 0.004), (576.52, 4.0, 0.004), (576.52, 40.0, 0.004), (576.4, 40.0, 0.004)], sw="giallo_vernice", face=(0, 0, 1))
    for k in range(7):
        y = 4.0 + 6.0 * k
        g.quad([(576.4, y - 0.06, 0.004), (578.9, y - 0.06, 0.004), (578.9, y + 0.06, 0.004), (576.4, y + 0.06, 0.004)],
               sw="giallo_vernice", face=(0, 0, 1))
    # strisce pedonali verso il parcheggio dei taxi (Y ~88-92, X 566-575)
    for k in range(9):
        y = 87.5 + k * 1.0
        g.quad([(566.5, y, 0.004), (575.0, y, 0.004), (575.0, y + 0.5, 0.004), (566.5, y + 0.5, 0.004)], sw="bianco_vernice", face=(0, 0, 1))
    o = g.finish(name, coll)
    _clear_ucx(name)
    pk._ucx(name, [(PIAZZALE_X1, RADICE_X1, 47.0, Y_VIALE, -3.0, 0.0), (571.8, RADICE_X1, yb, 47.0, -3.0, 0.0),
                   (555.0, 571.8, 41.6, 47.0, -3.0, 0.0), (xb, 571.8, Y_RADICE_B, 41.6, -3.0, 0.0)], coll)
    return o


# =============================================================================================================
# 1b. scogliera: kit di 3 moduli da 8 m di massi istanziati a scarpata (lato mare aperto)
# =============================================================================================================
SC_L, SC_W = 8.0, 5.5           # modulo: 8 m lungo il ciglio, scarpata larga 5,5 m verso il mare [S] 4-6 m
SC_ZTOP, SC_ZBOT = -0.15, -3.2


def _slope_z(y):
    """y locale: 0 al piede del marciapiede, -SC_W in acqua."""
    t = min(max(-y / SC_W, 0.0), 1.0)
    return SC_ZTOP + (SC_ZBOT - SC_ZTOP) * t ** 0.9


def _rock(g, c, r, sc, rot, subdiv, rng, mat="M_Molo_Scogliera"):
    n0 = len(g.bm.faces)
    res = bmesh.ops.create_icosphere(g.bm, subdivisions=subdiv, radius=1.0)
    vs = res["verts"]
    for v in vs:
        p = v.co.copy()
        k = 1.0 + 0.18 * math.sin(3.1 * p.x + rot) * math.cos(2.7 * p.y) + 0.12 * math.sin(4.3 * p.z + 1.3 * rot)
        p = Vector((p.x * sc[0], p.y * sc[1], p.z * sc[2])) * (r * k)
        p.z = max(p.z, -r * sc[2] * 0.55)                      # base appiattita
        v.co = Matrix.Rotation(rot, 3, "Z") @ p + Vector(c)
    fs = g._since(n0)
    for f in fs:
        f.normal_update()
    # UV: proiezione con v legata alla quota (alghe in basso)
    def uvfn(co, f):
        n = f.normal
        a = co.x + co.y if abs(n.z) < 0.7 else co.x
        return (a / 2.5, (co.z - SC_ZBOT) / (SC_ZTOP + 1.2 - SC_ZBOT) if abs(n.z) < 0.7 else co.y / 2.5)
    g.tag(fs, mat, uvfn=uvfn)


def build_scogliera(coll, var="A", lod=0):
    """Origine sul ciglio esterno del marciapiede (quota 0), asse +X lungo il molo, mare verso -Y."""
    name = f"SM_Molo_Scogliera_{var}"
    rng = np.random.default_rng({"A": 1, "B": 2, "C": 3}[var] + 40)
    g = G(["M_Molo_Scogliera"])
    rocks = []
    tries = 0
    while len(rocks) < 18 and tries < 2000:
        tries += 1
        x = rng.uniform(0.3, SC_L - 0.3)
        y = rng.uniform(-SC_W + 0.4, -0.5)
        r = rng.uniform(0.65, 1.25)
        if any((x - a) ** 2 + (y - b) ** 2 < (0.75 * (r + rr)) ** 2 for a, b, rr, *_ in rocks):
            continue
        rocks.append((x, y, r, rng.uniform(0, 6.28), (rng.uniform(1.0, 1.5), rng.uniform(0.8, 1.2), rng.uniform(0.55, 0.85))))
    rocks.sort(key=lambda t: -t[2])
    keep = {0: len(rocks), 1: len(rocks), 2: 9}[lod]
    for x, y, r, rot, sc in rocks[:keep]:
        _rock(g, (x, y, _slope_z(y) + 0.15 * r), r, sc, rot, 2 if lod == 0 else 1, rng)
    # nucleo della scarpata sotto i massi (riempie le fessure)
    pts = [(0.0, -0.1), (SC_L, -0.1), (SC_L, -SC_W), (0.0, -SC_W)]
    g.quad([(SC_L, -SC_W, _slope_z(-SC_W)), (SC_L, -0.1, SC_ZTOP - 0.25), (0.0, -0.1, SC_ZTOP - 0.25), (0.0, -SC_W, _slope_z(-SC_W))],
           "M_Molo_Scogliera", tile=2.5, face=(0, 0, 1))
    o = g.finish(name + _sfx(lod), coll, smooth=60.0)
    if lod == 0:
        _clear_ucx(name)
        # cuneo calpestabile un po' sopra il piano medio dei massi
        _ucx_hull(name, 0, [(x, y, z) for x in (0.0, SC_L) for y, z in ((0.0, SC_ZTOP + 0.35), (0.0, SC_ZBOT - 0.5),
                                                                      (-SC_W, SC_ZBOT - 0.5), (-SC_W, SC_ZBOT + 0.4))], coll)
    return o


def scogliera_slots():
    """(x, y, rotZ, variante) lungo il lato esterno: dalla lunetta (Y ~41) al gomito, gomito, ramo 2 fino alla testata."""
    O = [_v2(p) for p in O_LINE]
    out = []
    var = "ABC"
    k = 0
    for i in range(2):
        a, b = O[i], O[i + 1]
        d = (b - a).normalized()
        L = (b - a).length
        s0 = 3.2 if i == 0 else 0.0            # il primo modulo parte sotto la lunetta del monumento
        n = math.ceil((L - s0) / SC_L)
        for j in range(n):
            p = a + d * (s0 + j * SC_L)
            if j == n - 1:
                p = b - d * SC_L                                  # l'ultimo finisce sullo spigolo
            out.append((p.x, p.y, yaw_of(d), var[k % 3])); k += 1
    # spigolo convesso del gomito: modulo sulla bisettrice
    d0, d1 = seg_dir(O[0], O[1]), seg_dir(O[1], O[2])
    m = (d0 + d1).normalized()
    p = O[1] - m * (SC_L / 2)
    out.append((p.x, p.y, yaw_of(m), "B"))
    # spigolo della testata (lato sud, dopo il faro): un modulo girato lungo la testata
    t0, t1 = _v2(TESTATA[0]), _v2(TESTATA[1])
    dt = (t0 - t1).normalized()
    p = t0 + seg_dir(O[1], O[2]) * 0.0 - dt * 0.0
    out.append((p.x, p.y, yaw_of(_right(dt)) + 0.0, "C"))
    return out


# =============================================================================================================
# 1c. moli a dito (pontili fissi in cemento su pilastri [S]: dalla vista dall'alto restano rettilinei e chiari)
# =============================================================================================================
def build_dito(coll, lod=0, name="SM_MoloItalia_Dito"):
    """Origine sul ciglio del ramo 1 al centro dell'attacco, +X verso il bacino. Impalcato a Z 0 (cemento), trave di bordo
    fino a -0,8, pilastri ogni ~6,2 m fino a -3,5."""
    g = G(["M_MoloItalia_Cemento"])
    w = DITO_W / 2
    g.box(0.0, DITO_L, -w, w, -0.8, 0.0, "M_MoloItalia_Cemento", faces=("top", "bot", "xp", "yn", "yp"))
    g.quad([(0.0, -w + 0.25, 0.006), (DITO_L - 0.3, -w + 0.25, 0.006), (DITO_L - 0.3, -w + 0.37, 0.006), (0.0, -w + 0.37, 0.006)],
           sw="giallo_vernice", face=(0, 0, 1))
    g.quad([(0.0, w - 0.37, 0.006), (DITO_L - 0.3, w - 0.37, 0.006), (DITO_L - 0.3, w - 0.25, 0.006), (0.0, w - 0.25, 0.006)],
           sw="giallo_vernice", face=(0, 0, 1))
    if lod < 2:
        for k in range(8):
            x = 1.5 + k * (DITO_L - 3.0) / 7
            for y in (-w + 0.5, w - 0.5):
                g.box(x - 0.25, x + 0.25, y - 0.25, y + 0.25, -3.5, -0.8, "M_MoloItalia_Cemento", faces=("xn", "xp", "yn", "yp"))
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(0.0, DITO_L, -w, w, -0.8, 0.0)], coll)
    return o


# =============================================================================================================
# 2. faro rosso (§4): zoccolo a campana, fusto tronco-conico, ballatoio, tamburo, lanterna emissiva, cupola
# =============================================================================================================
def build_faro(coll, lod=0, name="SM_MoloItalia_Faro"):
    """Origine alla base al centro; porta verso -X locale (si gira verso il molo con lo yaw del CSV)."""
    n = (32, 20, 12)[lod]
    g = G(["M_MoloItalia_Tinte", "M_MoloItalia_FaroLuce"])
    R = "rosso_faro"
    g.lathe([(2.05, 0.0), (2.05, 0.12), (1.95, 0.12)], n, sw="cemento", cap_top=False)          # piattaforma in cemento
    bell = [(1.70, 0.12), (1.68, 0.20), (1.55, 0.30), (1.40, 0.42), (1.27, 0.54), (1.21, 0.62)]
    if lod == 2:
        bell = [bell[0], bell[2], bell[5]]
    g.lathe(bell + [(1.0, 5.30), (1.30, 5.42), (1.30, 5.80), (0.80, 5.80), (0.80, 6.90), (0.76, 6.90)], n, sw=R, cap_top=False)
    g.lathe([(0.70, 6.90), (0.70, 7.50)], n, mat="M_MoloItalia_FaroLuce", sw="luce_rossa", cap_top=False)   # vetri
    g.lathe([(0.78, 7.50), (0.76, 7.56), (0.55, 7.72), (0.25, 7.88), (0.10, 7.94)] +
            ([(0.10, 8.0), (0.0, 8.02)] if lod == 2 else [(0.12, 7.98), (0.12, 8.04), (0.0, 8.07)]), n, sw=R, cap_top=False)
    if lod < 2:
        g.tube([(0.0, 0.0, 8.02), (0.0, 0.0, 8.40)], 0.012, 6, sw="nero")                       # parafulmine
        for k in range(8):                                                                     # montanti della lanterna
            a = 2 * math.pi * k / 8
            c = Vector((0.71 * math.cos(a), 0.71 * math.sin(a), 0))
            g.tube([(c.x, c.y, 6.90), (c.x, c.y, 7.50)], 0.03, 4, sw=R, cap=False)
        # ringhiera del ballatoio: montanti + 2 correnti
        nr = 24 if lod == 0 else 12
        for k in range(nr):
            a = 2 * math.pi * k / nr
            g.tube([(1.24 * math.cos(a), 1.24 * math.sin(a), 5.80), (1.24 * math.cos(a), 1.24 * math.sin(a), 6.80)], 0.02, 4, sw=R, cap=False)
        for z in (6.35, 6.80):
            ring = [(1.24 * math.cos(2 * math.pi * k / nr), 1.24 * math.sin(2 * math.pi * k / nr), z) for k in range(nr + 1)]
            g.tube(ring, 0.025, 5, sw=R, cap=False)
        # corrimano ad arco sul fianco della lanterna
        g.tube([(0.2, 0.86, 6.90), (0.2, 0.9, 7.35), (-0.2, 0.9, 7.35), (-0.2, 0.86, 6.90)], 0.018, 5, sw=R, cap=False)
    # porta (verso -X), targa nera, finestrella alta
    rx = lambda z: 1.21 - (1.21 - 1.0) * (z - 0.62) / (5.30 - 0.62)
    g.box(-rx(0.65) - 0.05, -rx(0.65) + 0.15, -0.40, 0.40, 0.62, 2.52, sw="rosso_faro")
    g.box(-rx(0.65) - 0.07, -rx(0.65) - 0.04, -0.33, 0.33, 0.70, 2.44, sw="rosso_insegna")
    M = Matrix.Rotation(math.radians(-35), 4, "Z") @ Matrix.Translation((-rx(2.6) + 0.01, 0, 0))
    g.box(-0.05, 0.0, -0.20, 0.20, 2.35, 2.85, sw="nero", M=M)
    if lod < 2:
        g.box(-rx(4.6) - 0.02, -rx(4.6) + 0.1, -0.15, 0.15, 4.4, 4.8, sw="vetro")
    o = g.finish(name + _sfx(lod), coll, smooth=40.0)
    if lod == 0:
        _clear_ucx(name)
        oc = lambda r, z: [(r * math.cos(2 * math.pi * k / 10), r * math.sin(2 * math.pi * k / 10), z) for k in range(10)]
        _ucx_hull(name, 0, oc(1.72, 0.0) + oc(1.25, 0.62), coll)
        _ucx_hull(name, 1, oc(1.21, 0.62) + oc(1.0, 5.30), coll)
        _ucx_hull(name, 2, oc(1.30, 5.30) + oc(1.30, 6.85), coll)
        _ucx_hull(name, 3, oc(0.80, 6.85) + oc(0.12, 8.05), coll)
    return o


# =============================================================================================================
# 3. ristorante galleggiante "I Piccioni" (parodia di "I Gabbiani"): chiatta 19,5 x 10,3, perpendicolare al molo
# =============================================================================================================
R_HULL0, R_DECK = -2.0, -0.20          # scafo: chiglia, coperta (linea d'acqua -1,03: bordo libero ~0,8 m [F])
R_TOP = 3.0                            # piano della terrazza (giallo alto 3,2 m [F])
R_COVER = 5.35                         # copertura leggera (h totale sull'acqua ~6,6-7 m [F])


def build_ristorante(coll, lod=0, name="SM_MoloItalia_RistorantePiccioni"):
    """Coordinate locali: origine al centro della chiatta a quota 0 (= piano del molo), +X verso il bacino (lato lungo),
    il fronte corto verso il molo e' a X = -L/2. Due accessi: rampa blu (nord, +Y) e passerella ad arco (sud) con la scala
    che sale alla terrazza. Calpestabile: coperta, terrazza, scala, rampa, passerella."""
    L, W = 19.5, 10.3
    x0, x1, y0, y1 = -L / 2, L / 2, -W / 2, W / 2
    g = G(["M_MoloItalia_Tinte"])
    # scafo blu con fianchi dritti e spigoli smussati
    ch = 0.5
    hull = [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch), (x0, y0 + ch)]
    g.prism(hull, R_HULL0, R_DECK, "M_MoloItalia_Tinte", sw="blu_scafo", top=False, bot=True)
    g.poly(hull, R_DECK, "M_MoloItalia_Tinte", sw="grigio_scuro")
    if lod < 2:   # oblo' tondi neri sui fianchi
        for k in range(8):
            x = x0 + 1.5 + k * (L - 3) / 7
            for s, y in ((1, y1 + 0.005), (-1, y0 - 0.005)):
                g.quad([(x - 0.15, y, -0.75), (x + 0.15, y, -0.75), (x + 0.15, y, -0.45), (x - 0.15, y, -0.45)], sw="nero", face=(0, s, 0))
    # piano principale giallo (con un passaggio di 2,4 m sul lato sud per la scala)
    bx0, bx1, by0, by1 = x0 + 0.4, x1 - 0.4, y0 + 2.4, y1 - 0.4
    g.box(bx0, bx1, by0, by1, R_DECK, R_TOP, sw="giallo_rist", faces=("xn", "xp", "yn", "yp"))
    g.box(x0 + 0.2, x1 - 0.2, y0 + 0.2, y1 - 0.2, R_TOP - 0.25, R_TOP, sw="bianco")         # solaio-terrazza (bordo bianco)
    # fronte verso il molo (-X): porta a vetri, finestra, serranda grigia; scritta RISTORANTE
    fx = bx0 - 0.02
    g.quad([(fx, 1.2, R_DECK + 0.05), (fx, 2.6, R_DECK + 0.05), (fx, 2.6, R_DECK + 2.25), (fx, 1.2, R_DECK + 2.25)], sw="vetro", face=(-1, 0, 0))
    g.quad([(fx, -0.6, 0.85), (fx, 0.6, 0.85), (fx, 0.6, 2.05), (fx, -0.6, 2.05)], sw="vetro", face=(-1, 0, 0))
    g.quad([(fx, -2.5, 0.5), (fx, -1.1, 0.5), (fx, -1.1, 2.4), (fx, -2.5, 2.4)], sw="grigio_serranda", face=(-1, 0, 0))
    g.box(fx - 0.06, fx, 0.9, 2.9, 2.25, 2.55, sw="bianco")                                    # tendina sopra la porta
    if lod < 2:
        g.text("RISTORANTE", 0.22, 0.02, Matrix.Translation((fx - 0.07, 1.9, 2.30)) @ Matrix.Rotation(math.radians(-90), 4, "Z") @
               Matrix.Rotation(math.radians(90), 4, "X"), sw="blu_insegna", resol=1)
    # lato nord (+Y): fila di 6 finestre con cornice bianca
    for k in range(6):
        x = bx0 + 1.6 + k * (bx1 - bx0 - 3.2) / 5
        y = by1 + 0.02
        g.quad([(x + 0.75, y, 1.05), (x - 0.75, y, 1.05), (x - 0.75, y, 2.35), (x + 0.75, y, 2.35)], sw="bianco", face=(0, 1, 0))
        g.quad([(x + 0.62, y + 0.01, 1.15), (x - 0.62, y + 0.01, 1.15), (x - 0.62, y + 0.01, 2.25), (x + 0.62, y + 0.01, 2.25)], sw="vetro", face=(0, 1, 0))
    # lato sud e testa est: finestre semplici
    for k in range(4):
        x = bx0 + 2.0 + k * (bx1 - bx0 - 4.0) / 3
        y = by0 - 0.02
        g.quad([(x - 0.6, y, 1.15), (x + 0.6, y, 1.15), (x + 0.6, y, 2.25), (x - 0.6, y, 2.25)], sw="vetro", face=(0, -1, 0))
    # terrazza: parapetto bianco fasciato dal telo (doppia faccia), copertura leggera su 6 pali, veranda sul lato nord
    tz = R_TOP
    rail = [(x0 + 0.25, y0 + 0.25), (x1 - 0.25, y0 + 0.25), (x1 - 0.25, y1 - 0.25), (x0 + 0.25, y1 - 0.25)]
    for i in range(4):
        a, b = rail[i], rail[(i + 1) % 4]
        if i == 0:   # varco della scala sul lato sud (X da x0+2,4 a x0+4,0)
            segs = [(a, (x0 + 5.6, a[1])), ((x0 + 7.2, a[1]), b)]
        else:
            segs = [(a, b)]
        for p, q in segs:
            g.quad2([(p[0], p[1], tz), (q[0], q[1], tz), (q[0], q[1], tz + 1.0), (p[0], p[1], tz + 1.0)], sw="telo_bianco")
            if lod < 2:
                g.tube([(p[0], p[1], tz + 1.03), (q[0], q[1], tz + 1.03)], 0.03, 5, sw="bianco")
    poles = [(x0 + 1.0, y0 + 1.0), (0.0, y0 + 1.0), (x1 - 1.0, y0 + 1.0), (x0 + 1.0, y1 - 1.0), (0.0, y1 - 1.0), (x1 - 1.0, y1 - 1.0)]
    for px, py in poles:
        g.box(px - 0.06, px + 0.06, py - 0.06, py + 0.06, tz, R_COVER, sw="bianco", faces=("xn", "xp", "yn", "yp"))
    cz0, cz1 = R_COVER, R_COVER + 0.35
    g.quad2([(x0 + 0.6, y0 + 0.6, cz0), (x1 - 0.6, y0 + 0.6, cz0), (x1 - 0.6, 0.0, cz1), (x0 + 0.6, 0.0, cz1)], sw="telo_bianco")
    g.quad2([(x0 + 0.6, 0.0, cz1), (x1 - 0.6, 0.0, cz1), (x1 - 0.6, y1 - 0.6, cz0), (x0 + 0.6, y1 - 0.6, cz0)], sw="telo_bianco")
    if lod < 2:   # veranda vetrata sul lato nord (meta' est), condizionatori, asta con bandiera
        g.box(1.5, x1 - 1.0, y1 - 3.2, y1 - 1.0, tz, tz + 2.3, sw="vetro", faces=("xn", "xp", "yn", "yp"))
        for k, x in enumerate((-4.5, -3.4)):
            g.box(x, x + 0.85, y1 - 2.0, y1 - 1.4, tz, tz + 0.6, sw="grigio_chiaro")
        g.tube([(x0 + 0.5, y1 - 0.5, tz), (x0 + 0.5, y1 - 0.5, tz + 3.0)], 0.03, 5, sw="bianco")
        g.quad2([(x0 + 0.5, y1 - 0.5, tz + 2.2), (x0 + 0.5, y1 + 0.7, tz + 2.2), (x0 + 0.5, y1 + 0.7, tz + 2.95),
                (x0 + 0.5, y1 - 0.5, tz + 2.95)], sw="bianco")   # bandierina (tinta neutra)
        # insegna parodia sul telo del fronte verso il molo
        g.text("I PICCIONI", 0.55, 0.03, Matrix.Translation((x0 + 0.20, 0.0, tz + 0.18)) @
               Matrix.Rotation(math.radians(-90), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X"), sw="blu_insegna", resol=2)
    # scala esterna sul passaggio sud: da coperta (x0+0,4) a terrazza (x0+7,2), larga 1,6 m
    sx0, sx1, sy0, sy1 = x0 + 0.6, x0 + 7.2, y0 + 0.5, y0 + 2.1
    nst = 16 if lod == 0 else (8 if lod == 1 else 1)
    for k in range(nst):
        xa = sx0 + (sx1 - sx0) * k / nst
        xb = sx0 + (sx1 - sx0) * (k + 1) / nst
        z = R_DECK + (tz - R_DECK) * (k + 1) / nst
        g.box(xa, xb, sy0, sy1, z - 0.06, z, sw="grigio_scuro", faces=("top", "xn", "yn", "yp"))
    if lod < 2:
        for y in (sy0, sy1):
            g.tube([(sx0, y, R_DECK + 1.0), (sx1, y, tz + 1.0)], 0.03, 5, sw="bianco")
    # accesso 1: rampa blu (nord) dal molo alla porta, con corrimano in legno
    gap = 2.65                                   # distanza dal ciglio del molo [V] ~2,6 m
    rx0, rx1, ry0, ry1 = x0 - gap - 0.4, x0 + 0.4, 1.0, 2.9
    g.quad([(rx0, ry0, 0.02), (rx1, ry0, R_DECK + 0.02), (rx1, ry1, R_DECK + 0.02), (rx0, ry1, 0.02)], sw="blu_scafo", face=(0, 0, 1))
    g.box(rx0, rx1, ry0, ry1, -0.25, -0.05, sw="blu_scuro", faces=("xn", "yn", "yp"))
    if lod < 2:
        for y in (ry0, ry1):
            g.tube([(rx0 + 0.1, y, 0.95), (rx1, y, R_DECK + 0.95)], 0.035, 5, sw="legno")
            g.tube([(rx0 + 0.1, y, 0.0), (rx0 + 0.1, y, 0.95)], 0.025, 4, sw="zincato")
    # accesso 2: passerella coperta ad archi in tubolare bianco con telo (sud), verso la scala
    px0, px1, py0, py1 = x0 - gap - 0.4, x0 + 0.6, y0 + 0.5, y0 + 2.1
    g.quad([(px0, py0, 0.02), (px1, py0, R_DECK + 0.02), (px1, py1, R_DECK + 0.02), (px0, py1, 0.02)], sw="blu_scafo", face=(0, 0, 1))
    narc = 4 if lod < 2 else 2
    ca = (py0 + py1) / 2
    rr = (py1 - py0) / 2 + 0.1
    nseg = 8 if lod == 0 else 4
    for k in range(narc):
        x = px0 + 0.1 + (px1 - px0 - 0.2) * k / (narc - 1)
        pts = [(x, ca - rr, 0.0)] + [(x, ca - rr * math.cos(math.pi * j / nseg), 2.0 + rr * math.sin(math.pi * j / nseg))
                                     for j in range(nseg + 1)] + [(x, ca + rr, 0.0)]
        if lod < 2:
            g.tube(pts, 0.035, 5, sw="bianco", cap=False)
    for j in range(nseg):                                   # telo della copertura ad arco
        a0, a1 = math.pi * j / nseg, math.pi * (j + 1) / nseg
        p0 = (ca - rr * math.cos(a0), 2.0 + rr * math.sin(a0))
        p1 = (ca - rr * math.cos(a1), 2.0 + rr * math.sin(a1))
        g.quad2([(px0, p0[0], p0[1]), (px1, p0[0], p0[1]), (px1, p1[0], p1[1]), (px0, p1[0], p1[1])], sw="telo_bianco")
    o = g.finish(name + _sfx(lod), coll, smooth=None)
    if lod == 0:
        _clear_ucx(name)
        boxes = [(x0, x1, y0, y1, R_HULL0, R_DECK),                                 # scafo + coperta
                 (bx0, bx1, by0, by1, R_DECK, R_TOP),                               # piano giallo
                 (x0 + 0.2, x1 - 0.2, y0 + 0.2, y1 - 0.2, R_TOP - 0.25, R_TOP),     # terrazza
                 (x0 + 0.2, x1 - 0.2, y1 - 0.35, y1 - 0.2, R_TOP, R_TOP + 1.05),    # parapetti
                 (x1 - 0.35, x1 - 0.2, y0 + 0.2, y1 - 0.2, R_TOP, R_TOP + 1.05),
                 (x0 + 0.2, x0 + 0.35, y0 + 0.2, y1 - 0.2, R_TOP, R_TOP + 1.05),
                 (x0 + 7.2, x1 - 0.2, y0 + 0.2, y0 + 0.35, R_TOP, R_TOP + 1.05),
                 (x0 + 0.6, x1 - 0.6, y0 + 0.6, y1 - 0.6, R_COVER, R_COVER + 0.35),  # copertura
                 (rx0, rx1, ry0, ry1, -0.3, 0.0),                                    # rampa blu
                 (px0, px1, py0, py1, -0.3, 0.0)]                                    # passerella
        pk._ucx(name, boxes, coll)
        # scala come rampa (convesso inclinato)
        _ucx_hull(name, len(boxes), [(sx0, y, R_DECK) for y in (sy0, sy1)] + [(sx1, y, tz) for y in (sy0, sy1)] +
                  [(sx1, y, R_DECK) for y in (sy0, sy1)], coll)
    return o


# =============================================================================================================
# 4. edifici della radice: Capitaneria/Guardia Costiera (2 piani), edificio a 4 piani, edificio est (fondale)
# =============================================================================================================
def _ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


def _building(g, poly, floors, fh, parapet=0.9, cornice=0.25, lod=0):
    poly = _ccw(poly)
    H = floors * fh
    g.prism(poly, 0.0, H, "M_MoloItalia_Facciata", uv_wall=(BAY_W, fh), top=False)
    # parapetto/cornicione chiaro sporgente
    outer = [tuple(p) for p in offset_line(poly + [poly[0]], cornice, "r")][:-1]
    # chiusura: per il poligono antiorario la destra e' l'esterno; ricalcolo del primo vertice con il giunto corretto
    P = [_v2(p) for p in poly]
    outer = []
    for i in range(len(P)):
        a, b, c = P[i - 1], P[i], P[(i + 1) % len(P)]
        n1, n2 = _right((b - a).normalized()), _right((c - b).normalized())
        m = (n1 + n2).normalized()
        q = b + m * (cornice / m.dot(n1))
        outer.append((q.x, q.y))
    g.prism(outer, H, H + parapet, "M_MoloItalia_Tinte", sw="pietra_chiara", top=False)
    g.prism(outer, H - 0.25, H, "M_MoloItalia_Tinte", sw="pietra_chiara", top=False)
    for i in range(len(poly)):      # sottogronda del cornicione
        j = (i + 1) % len(poly)
        g.quad([(outer[j][0], outer[j][1], H), (outer[i][0], outer[i][1], H), (poly[i][0], poly[i][1], H), (poly[j][0], poly[j][1], H)],
               sw="pietra_chiara", face=(0, 0, -1))
    g.poly(poly, H + 0.15, "M_MoloItalia_Tinte", sw="cemento")                      # tetto piano
    if lod < 2:   # faccia interna del parapetto
        for i in range(len(poly)):
            j = (i + 1) % len(poly)
            a, b = outer[i], outer[j]
            d = (Vector(b) - Vector(a))
            n = Vector((-d.y, d.x)).normalized() * 0.25
            g.quad([(b[0] + n.x, b[1] + n.y, H + 0.15), (a[0] + n.x, a[1] + n.y, H + 0.15), (a[0] + n.x, a[1] + n.y, H + parapet),
                    (b[0] + n.x, b[1] + n.y, H + parapet)], sw="pietra_chiara", face=(n.x, n.y, 0))
            g.quad([(a[0], a[1], H + parapet), (b[0], b[1], H + parapet), (b[0] + n.x, b[1] + n.y, H + parapet),
                    (a[0] + n.x, a[1] + n.y, H + parapet)], sw="pietra_chiara", face=(0, 0, 1))
    return H


def _antenna(g, x, y, z, h, lattice=True):
    if lattice:
        r = 0.35
        legs = [(x + r * math.cos(a), y + r * math.sin(a)) for a in (0.3, 2.4, 4.5)]
        for lx, ly in legs:
            g.tube([(lx, ly, z), (x + (lx - x) * 0.3, y + (ly - y) * 0.3, z + h)], 0.03, 4, sw="grigio_chiaro")
        for k in range(1, 5):
            zz = z + h * k / 5
            s = 1 - 0.7 * k / 5
            ring = [(x + (lx - x) * s, y + (ly - y) * s, zz) for lx, ly in legs + legs[:1]]
            g.tube(ring, 0.015, 3, sw="grigio_chiaro", cap=False)
    else:
        g.tube([(x, y, z), (x, y, z + h)], 0.04, 5, sw="grigio_chiaro")


def build_capitaneria(coll, lod=0, name="SM_MoloItalia_Capitaneria"):
    """Capitaneria di Porto / Guardia Costiera (OSM 205843153): pianta a L, 2 piani alti (~4,5 m) -> h ~10 m [S]; mattoni rossi a
    vista, marcapiani chiari, infissi verde acqua, tetto piano con cornicione [F]. Scritta "GUARDIA COSTIERA" (ente pubblico,
    nome reale) sul parapetto del fronte ovest. Giardino recintato con muretto davanti al fronte ovest. Coordinate di progetto."""
    g = G(["M_MoloItalia_Facciata", "M_MoloItalia_Tinte"])
    H = _building(g, CAPITANERIA, 2, FLOOR_H, parapet=1.0, lod=lod)
    # ingresso al centro del fronte ovest: portone e pensilina
    g.box(592.45, 592.75, 60.5, 63.5, 0.0, 3.0, sw="vetro", faces=("xn",))
    g.box(591.4, 592.75, 60.0, 64.0, 3.0, 3.25, sw="pietra_chiara")
    if lod < 2:
        # scritta sul parapetto ovest (letta da ovest, dal parcheggio); in LOD1 con meno suddivisioni
        g.text("GUARDIA COSTIERA", 0.62, 0.06, Matrix.Translation((592.2, 62.2, H + 0.18)) @ Matrix.Rotation(math.radians(-90), 4, "Z") @
               Matrix.Rotation(math.radians(90), 4, "X"), sw="blu_insegna", resol=2 - lod)
        _antenna(g, 600.0, 75.0, H + 0.15, 6.0, lattice=False)
        _antenna(g, 612.0, 75.0, H + 0.15, 4.5, lattice=False)
    # giardino davanti al fronte ovest: prato rialzato, muretto con recinzione verde (X 586,6-592,5, Y 45-80,3)
    gx0, gx1, gy0, gy1 = 586.6, 592.6, 45.0, 80.3
    g.box(gx0, gx1, gy0, gy1, 0.0, 0.25, sw="verde_prato", faces=("top",))
    g.box(gx0 - 0.3, gx0, gy0, gy1, 0.0, 0.55, sw="pietra_chiara", faces=("top", "xn", "xp", "yn", "yp"))
    g.box(gx0 - 0.3, gx1, gy0 - 0.3, gy0, 0.0, 0.55, sw="pietra_chiara", faces=("top", "xn", "yn", "yp"))
    g.box(gx0 - 0.3, gx1, gy1, gy1 + 0.3, 0.0, 0.55, sw="pietra_chiara", faces=("top", "xn", "yn", "yp"))
    for (a, b) in (((gx0 - 0.15, gy0), (gx0 - 0.15, gy1)),):
        g.quad2([(a[0], a[1], 0.55), (b[0], b[1], 0.55), (b[0], b[1], 1.55), (a[0], a[1], 1.55)], sw="verde_scuro")
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(592.7, 617.3, 67.8, 80.5, 0.0, H + 1.0), (593.0, 607.4, 44.2, 67.8, 0.0, H + 1.0),
                       (gx0 - 0.3, gx0, gy0 - 0.3, gy1 + 0.3, 0.0, 1.55)], coll)
    return o


def build_edificio4p(coll, lod=0, name="SM_MoloItalia_Edificio4P"):
    """Edificio a 4 piani della radice (OSM 205839145): piano terra + 3 -> h ~14,5 m [S], stesso mattone, due antenne a traliccio."""
    g = G(["M_MoloItalia_Facciata", "M_MoloItalia_Tinte"])
    H = _building(g, EDIF_4P, 4, 3.5, parapet=0.8, lod=lod)
    if lod < 2:
        _antenna(g, 583.0, 36.0, H + 0.15, 9.0)
        _antenna(g, 589.0, 24.0, H + 0.15, 7.0)
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(579.2, 593.6, 19.3, 40.6, 0.0, H + 0.8)], coll)
    return o


def build_edificio_est(coll, lod=0, name="SM_MoloItalia_EdificioEst"):
    """Edificio est della radice (OSM 205839033): non inquadrato dalle foto -> stesso mattone, 3 piani, h ~10,5 m [S]."""
    g = G(["M_MoloItalia_Facciata", "M_MoloItalia_Tinte"])
    H = _building(g, EDIF_EST, 3, 3.5, parapet=0.7, lod=lod)
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(615.4, 630.6, 19.6, 41.1, 0.0, H + 0.7)], coll)
    return o


def build_infopoint(coll, var="Blu", lod=0):
    """Casetta prefabbricata dell'info point / taxi, 3,5 x 3,5 x 3 m a facce piane [F]: pareti bianche, finestre con telai blu,
    fascia insegna blu o rossa (senza scritte reali). Origine a terra al centro."""
    name = f"SM_MoloItalia_InfoPoint_{var}"
    g = G(["M_MoloItalia_Tinte"])
    h = 1.75
    g.box(-h, h, -h, h, 0.0, 2.55, sw="bianco", faces=("xn", "xp", "yn", "yp"))
    g.box(-h - 0.1, h + 0.1, -h - 0.1, h + 0.1, 2.55, 3.0, sw="blu_insegna" if var == "Blu" else "rosso_insegna")
    for k, (n, t) in enumerate(((Vector((0, -1, 0)), Vector((1, 0, 0))), (Vector((1, 0, 0)), Vector((0, 1, 0))),
                                (Vector((-1, 0, 0)), Vector((0, -1, 0))), (Vector((0, 1, 0)), Vector((-1, 0, 0))))):
        c = n * (h + 0.01)
        w = 1.1 if k != 0 else 0.5
        pts = [c - t * w + Vector((0, 0, 0.9)), c + t * w + Vector((0, 0, 0.9)), c + t * w + Vector((0, 0, 2.3)), c - t * w + Vector((0, 0, 2.3))]
        g.quad([tuple(p) for p in pts], sw="blu_scuro", face=n)
        pts = [c + n * 0.005 - t * (w - 0.08) + Vector((0, 0, 0.98)), c + n * 0.005 + t * (w - 0.08) + Vector((0, 0, 0.98)),
               c + n * 0.005 + t * (w - 0.08) + Vector((0, 0, 2.22)), c + n * 0.005 - t * (w - 0.08) + Vector((0, 0, 2.22))]
        g.quad([tuple(p) for p in pts], sw="vetro", face=n)
        if k == 0:   # porta
            pts = [c + n * 0.005 + t * 0.7 + Vector((0, 0, 0.0)), c + n * 0.005 + t * 1.6 + Vector((0, 0, 0.0)),
                   c + n * 0.005 + t * 1.6 + Vector((0, 0, 2.1)), c + n * 0.005 + t * 0.7 + Vector((0, 0, 2.1))]
            g.quad([tuple(p) for p in pts], sw="blu_scuro", face=n)
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(-h - 0.1, h + 0.1, -h - 0.1, h + 0.1, 0.0, 3.0)], coll)
    return o


# =============================================================================================================
# 5. arredi nuovi: lampione a pastorale, modulo di ringhiera, monumenti
# =============================================================================================================
def build_lampione_pastorale(coll, lod=0, name="SM_Morin_LampionePastorale"):
    """Palo in ghisa con base modanata, braccio a pastorale con ricciolo e un globo bianco appeso; h ~5,2 m [F]/[S].
    Origine alla base; il braccio sporge verso +X (nel CSV verso la carreggiata)."""
    n = (12, 8, 6)[lod]
    g = G(["M_Morin_Ghisa", "M_Morin_Globo", "M_MoloItalia_Tinte"])
    prof = [(0.20, 0.0), (0.20, 0.08), (0.16, 0.12), (0.16, 0.30), (0.12, 0.38), (0.10, 0.70), (0.085, 0.80), (0.075, 0.95),
            (0.060, 4.60), (0.075, 4.66), (0.075, 4.74), (0.045, 4.80), (0.06, 4.90), (0.0, 5.05)]
    if lod == 2:
        prof = [prof[0], prof[3], prof[5], prof[8], prof[10], prof[13]]
    g.lathe(prof, n, mat="M_Morin_Ghisa", tile=1.0)
    arm = [(0.0, 0.0, 4.35), (0.10, 0.0, 4.70), (0.30, 0.0, 4.92), (0.55, 0.0, 4.98), (0.78, 0.0, 4.90), (0.90, 0.0, 4.72),
           (0.90, 0.0, 4.55)]
    if lod == 2:
        arm = [arm[0], arm[2], arm[4], arm[6]]
    g.tube(arm, 0.032, (8, 6, 4)[lod], mat="M_Morin_Ghisa", sw=None)
    if lod < 2:   # ricciolo decorativo sotto il braccio
        sp = [(0.08 + 0.18 * (1 - t) * math.cos(6.0 * t) * 0.6 + 0.2 * t, 0.0, 4.45 + 0.18 * (1 - t) * math.sin(6.0 * t) * 0.6 + 0.25 * t)
              for t in np.linspace(0, 1, 14 if lod == 0 else 8)]
        g.tube(sp, 0.012, 4, mat="M_Morin_Ghisa")
    # attacco del globo e globo bianco
    g.lathe([(0.0, 4.53), (0.06, 4.53), (0.09, 4.47), (0.09, 4.43), (0.0, 4.43)], n, Matrix.Translation((0.90, 0, 0)), mat="M_Morin_Ghisa", tile=1.0)
    gl = [(0.0, 3.98)] + [(0.23 * math.sin(math.pi * j / 8), 4.21 - 0.23 * math.cos(math.pi * j / 8)) for j in range(1, 8)] + [(0.06, 4.43)]
    if lod == 2:
        gl = [gl[0], gl[2], gl[4], gl[6], gl[-1]]
    g.lathe(gl, n, Matrix.Translation((0.90, 0, 0)), mat="M_Morin_Globo", tile=1.0, cap_top=False)
    o = g.finish(name + _sfx(lod), coll, smooth=50.0)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(-0.2, 0.2, -0.2, 0.2, 0.0, 0.95), (-0.08, 0.08, -0.08, 0.08, 0.95, 5.0)], coll)
    return o


def build_ringhiera(coll, lod=0, name="SM_MoloItalia_RinghieraModulo"):
    """Modulo staccato in tubolare zincato, 2 m, h 1,0 m, due correnti, montanti agli estremi, piastre a terra [F] faro_2/3.
    Origine a terra all'estremo sinistro, lungo +X."""
    g = G(["M_MoloItalia_Tinte"])
    s = (8, 6, 4)[lod]
    for x in (0.05, 1.95):
        g.tube([(x, 0, 0.0), (x, 0, 1.0)], 0.024, s, sw="zincato")
        g.box(x - 0.08, x + 0.08, -0.08, 0.08, 0.0, 0.012, sw="zincato", faces=("top", "xn", "xp", "yn", "yp"))
    for z in ((0.5, 1.0) if lod < 2 else (1.0,)):
        g.tube([(0.05, 0, z), (1.95, 0, z)], 0.024, s, sw="zincato")
    o = g.finish(name + _sfx(lod), coll, smooth=50.0)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(0.0, 2.0, -0.06, 0.06, 0.0, 1.03)], coll)
    return o


def _stele(g, cx, cy, rotz, w=1.0, d=0.6, h=2.5, busto=True):
    M = Matrix.Translation((cx, cy, 0)) @ Matrix.Rotation(rotz, 4, "Z")
    g.box(-w / 2 - 0.35, w / 2 + 0.35, -d / 2 - 0.35, d / 2 + 0.35, 0.0, 0.25, mat="M_Pav_Fascia", tile=1.0, M=M)
    g.box(-w / 2, w / 2, -d / 2, d / 2, 0.25, 0.25 + h, mat="M_Pav_Fascia", tile=1.0, M=M)
    g.box(-w / 2 - 0.06, w / 2 + 0.06, -d / 2 - 0.06, d / 2 + 0.06, 0.25 + h, 0.35 + h, mat="M_Pav_Fascia", tile=1.0, M=M)
    g.box(-0.30, 0.30, -d / 2 - 0.03, -d / 2, 1.6, 2.2, sw="bronzo", M=M)                       # targa in bronzo
    g.box(-0.22, 0.22, -d / 2 - 0.05, -d / 2 - 0.02, h - 0.35, h + 0.05, sw="bronzo", M=M)      # emblema
    if busto:
        P = M @ Matrix.Translation((w / 2 + 0.9, -0.1, 0))
        g.box(-0.3, 0.3, -0.3, 0.3, 0.0, 1.2, mat="M_Pav_Fascia", tile=1.0, M=P)
        g.lathe([(0.24, 1.2), (0.26, 1.35), (0.2, 1.5), (0.09, 1.56), (0.1, 1.62), (0.13, 1.75), (0.12, 1.88), (0.06, 1.95), (0.0, 1.96)],
                10, P, sw="bronzo")


def build_monumento(coll, lod=0, name="SM_MoloItalia_Monumento"):
    """Lunetta alla radice (~553; 46) [F] MO: muretto semicircolare in pietra a vista (h 0,7, Ø ~8,5) che sporge sulla scogliera,
    pavimento in cubetti, stele in pietra chiara con targa ed emblema in bronzo, busto in bronzo, pilastrini con catene.
    Coordinate di progetto (origine 0,0,0)."""
    g = G(["M_Banchina_Paramento", "M_Pav_Cubetti", "M_Pav_Fascia", "M_MoloItalia_Tinte"])
    cx, cy = MONUMENTO_C
    R = 4.25
    nseg = (20, 14, 8)[lod]
    ang = [math.pi / 2 + math.pi * k / nseg for k in range(nseg + 1)]        # semicerchio verso -X (mare)
    ring_o = [(cx + R * math.cos(a), cy + R * math.sin(a)) for a in ang]
    ring_i = [(cx + (R - 0.4) * math.cos(a), cy + (R - 0.4) * math.sin(a)) for a in ang]
    g.poly([(cx, cy + R)] + ring_i[1:-1] + [(cx, cy - R)], 0.0, "M_Pav_Cubetti", tile=3.2)
    g.quad([(cx, cy - R, 0.0), (555.0, cy - R, 0.0), (555.0, cy + R, 0.0), (cx, cy + R, 0.0)], "M_Pav_Cubetti", tile=3.2, face=(0, 0, 1))
    g.quad([(cx, cy - R, -1.2), (555.0, cy - R, -1.2), (555.0, cy - R, 0.0), (cx, cy - R, 0.0)], "M_Banchina_Paramento", tile=2.0, face=(0, -1, 0))
    for i in range(nseg):
        a, b = ring_o[i], ring_o[i + 1]
        c, d = ring_i[i], ring_i[i + 1]
        out = ((a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy, 0.0)
        g.quad([(b[0], b[1], -1.2), (a[0], a[1], -1.2), (a[0], a[1], 0.7), (b[0], b[1], 0.7)], "M_Banchina_Paramento", tile=2.0, face=out)
        g.quad([(c[0], c[1], 0.0), (d[0], d[1], 0.0), (d[0], d[1], 0.7), (c[0], c[1], 0.7)], "M_Banchina_Paramento", tile=2.0,
               face=(-out[0], -out[1], 0.0))
        g.quad([(a[0], a[1], 0.7), (b[0], b[1], 0.7), (d[0], d[1], 0.7), (c[0], c[1], 0.7)], "M_Pav_Fascia", tile=1.0, face=(0, 0, 1))
    for p, q, fy in ((ring_o[0], ring_i[0], 1.0), (ring_o[-1], ring_i[-1], -1.0)):
        g.quad([(p[0], p[1], -1.2), (q[0], q[1], -1.2), (q[0], q[1], 0.7), (p[0], p[1], 0.7)], "M_Banchina_Paramento", tile=2.0,
               face=(1.0, 0.0, 0.0))
    _stele(g, cx - 1.2, cy, math.radians(90))
    # pilastrini e catene sul lato aperto verso il piazzale
    posts = [(554.6, cy - 3.4), (554.75, cy - 1.2), (554.75, cy + 1.2), (554.6, cy + 3.4)]
    for px, py in posts:
        g.box(px - 0.13, px + 0.13, py - 0.13, py + 0.13, 0.0, 0.6, mat="M_Pav_Fascia", tile=1.0)
    if lod < 2:
        for (ax, ay), (bx, by) in zip(posts, posts[1:]):
            mid = ((ax + bx) / 2, (ay + by) / 2)
            g.tube([(ax, ay, 0.5), (mid[0], mid[1], 0.32), (bx, by, 0.5)], 0.015, 4, sw="nero", cap=False)
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        k = 0
        for i in range(0, nseg, 2):
            a, b = ring_o[i], ring_o[min(i + 2, nseg)]
            c, d = ring_i[i], ring_i[min(i + 2, nseg)]
            _ucx_hull(name, k, [(p[0], p[1], z) for p in (a, b, c, d) for z in (-1.2, 0.7)], coll); k += 1
        pk._ucx(name, [(cx - 1.2 - 0.65, cx - 1.2 + 0.65, cy - 0.85, cy + 0.85, 0.0, 2.85), (cx, 555.0, cy - R, cy + R, -1.2, 0.0)], coll, start=k)
        _ucx_hull(name, k + 2, [(p[0], p[1], z) for p in ring_i for z in (-1.2, 0.0)], coll)
    return o


def build_monumento_alpini(coll, lod=0, name="SM_MoloItalia_MonumentoAlpini"):
    """Monumento sul ramo 2 [S] (etichetta della vista satellitare: "Monumento degli Alpini ai Marinai caduti"; nessuna foto):
    stele in pietra chiara su due gradini con targa in bronzo, senza busto. Origine a terra al centro, fronte verso -Y."""
    g = G(["M_Pav_Fascia", "M_MoloItalia_Tinte"])
    g.box(-1.1, 1.1, -0.8, 0.8, 0.0, 0.2, mat="M_Pav_Fascia", tile=1.0)
    _stele(g, 0.0, 0.0, 0.0, w=0.9, d=0.55, h=2.2, busto=False)
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(-1.1, 1.1, -0.8, 0.8, 0.0, 0.2), (-0.8, 0.8, -0.65, 0.65, 0.2, 2.6)], coll)
    return o


# =============================================================================================================
# 6. barche: rimorchiatori (3 nomi parodia), motovedetta della Guardia Costiera, nave da crociera e gru (fondale)
# =============================================================================================================
def _hull(g, L, B, z_keel, z_deck, bow=0.25, sw_side="nero_scafo", sw_band=None, band=(0.0, 0.6), n=10, sheer=0.5):
    """Scafo a sezioni: pianta con prua tonda (ultimo `bow` della lunghezza), fianchi verticali con leggero rientro sotto."""
    def half_w(t):          # t: 0 poppa -> 1 prua
        if t < 1 - bow:
            return B / 2 * (0.92 + 0.08 * min(t / 0.1, 1))
        u = (t - (1 - bow)) / bow
        return B / 2 * math.sqrt(max(1 - u * u, 0.0)) + 0.05
    ts = [k / n for k in range(n + 1)]
    rings = []
    for t in ts:
        x = -L / 2 + L * t
        w = half_w(t)
        zd = z_deck + sheer * max(t - 0.6, 0) / 0.4
        rings.append([(x, -w * 0.8, z_keel), (x, -w, z_deck * 0.3), (x, -w, zd), (x, w, zd), (x, w, z_deck * 0.3), (x, w * 0.8, z_keel)])
    for i in range(n):
        a, b = rings[i], rings[i + 1]
        for k in (0, 1, 3, 4):
            g.quad([a[k], b[k], b[k + 1], a[k + 1]], sw=sw_side, face=(0, -1 if k < 3 else 1, 0))
        g.quad([a[5], b[5], b[0], a[0]], sw=sw_side, face=(0, 0, -1))
        g.quad([a[2], a[3], b[3], b[2]], sw="grigio_scuro", face=(0, 0, 1))                # coperta
        if sw_band:
            for s in (-1, 1):
                k = 2 if s < 0 else 3
                za, zb = a[k][2] - band[1], a[k][2] - band[0]
                zc, zd2 = b[k][2] - band[1], b[k][2] - band[0]
                ya, yb = a[k][1] + s * 0.01, b[k][1] + s * 0.01
                q = [(a[k][0], ya, za), (b[k][0], yb, zc), (b[k][0], yb, zd2), (a[k][0], ya, zb)]
                g.quad(q, sw=sw_band, face=(0, s, 0))
    g.quad([rings[0][k] for k in (0, 1, 2, 3, 4, 5)], sw=sw_side, face=(-1, 0, 0))          # specchio di poppa
    return half_w


def build_rimorchiatore(coll, nome="Tiramolla", lod=0):
    """Rimorchiatore portuale [F] molo_italia_3-6: scafo nero con fascia rossa, sovrastruttura bianca, plancia vetrata,
    albero, parabordi di pneumatici a prua. Nome parodia, nessuna livrea reale. 30 x 10 m. Origine sulla linea d'acqua."""
    name = f"SM_MoloItalia_Rimorchiatore_{nome}"
    g = G(["M_MoloItalia_Tinte"])
    L, B = 30.0, 10.0
    hw = _hull(g, L, B, -3.6, 2.0, bow=0.3, sw_band="rosso_rimorch", band=(0.0, 0.7), n=(10, 6, 4)[lod])
    g.box(-6.0, 6.0, -3.6, 3.6, 2.0, 4.6, sw="bianco_scafo")
    g.box(-1.0, 4.5, -2.8, 2.8, 4.6, 7.0, sw="bianco_scafo")
    g.box(-1.02, 4.52, -2.82, 2.82, 5.9, 6.7, sw="vetro", faces=("xn", "xp", "yn", "yp"))
    g.box(-1.3, 4.8, -3.1, 3.1, 7.0, 7.2, sw="grigio_chiaro")
    g.box(-4.5, -2.5, -0.9, 0.9, 4.6, 8.0, sw="fumaiolo")
    if lod < 2:
        g.tube([(2.0, 0.0, 7.2), (2.0, 0.0, 12.5)], 0.12, 6, sw="bianco_scafo")
        g.tube([(2.0, -1.4, 11.0), (2.0, 1.4, 11.0)], 0.06, 4, sw="bianco_scafo")
        g.box(-13.5, -11.5, -0.6, 0.6, 2.0, 3.0, sw="grigio_scuro")                         # gancio di traino
        for k in range(7 if lod == 0 else 4):                                               # pneumatici a prua
            t = 0.74 + 0.04 * k
            x = -L / 2 + L * t
            for s in (-1, 1):
                y = s * (hw(t) + 0.25)
                ring = [(x + 0.45 * math.cos(a), y, 1.0 + 0.45 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)]
                g.tube(ring, 0.15, 5, sw="gomma", cap=False)
        tz = 1.3
        for s in (-1, 1):   # nome sulle mascone
            M = Matrix.Translation((L / 2 - 6.5, s * (hw(0.8) + 0.03), tz)) @ Matrix.Rotation(math.radians(0 if s < 0 else 180), 4, "Z") @ \
                Matrix.Rotation(math.radians(90), 4, "X")
            g.text(nome.upper(), 0.55, 0.02, M, sw="bianco_scafo", resol=1)
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(-L / 2, L / 2 - 2.0, -B / 2 + 0.3, B / 2 - 0.3, -2.0, 2.0), (-6.0, 6.0, -3.6, 3.6, 2.0, 7.2)], coll)
    return o


def build_motovedetta(coll, lod=0, name="SM_MoloItalia_Motovedetta"):
    """Motovedetta della Guardia Costiera (livrea istituzionale ammessa): scafo bianco con banda diagonale rossa, scritta
    "GUARDIA COSTIERA", sovrastruttura bianca, albero. 16 x 4,6 m. Origine sulla linea d'acqua."""
    g = G(["M_MoloItalia_Tinte"])
    L, B = 16.0, 4.6
    hw = _hull(g, L, B, -1.3, 1.4, bow=0.35, sw_side="bianco_scafo", n=(10, 6, 4)[lod], sheer=0.4)
    g.box(-3.5, 2.5, -1.7, 1.7, 1.4, 3.3, sw="bianco_scafo")
    g.box(-3.52, 2.52, -1.72, 1.72, 2.5, 3.1, sw="vetro", faces=("xn", "xp", "yn", "yp"))
    if lod < 2:
        g.tube([(0.0, 0.0, 3.3), (0.0, 0.0, 6.0)], 0.06, 5, sw="bianco_scafo")
        for s in (-1, 1):
            y = s * (B / 2 + 0.012)
            # banda diagonale rossa (parallelogramma) a prua
            q = [(3.2, y, -0.3), (4.2, y, -0.3), (2.9, y, 1.38), (1.9, y, 1.38)]
            g.quad(q, sw="rosso_insegna", face=(0, s, 0))
            M = Matrix.Translation((-2.0, y + s * 0.01, 0.55)) @ Matrix.Rotation(math.radians(0 if s < 0 else 180), 4, "Z") @ \
                Matrix.Rotation(math.radians(90), 4, "X")
            g.text("GUARDIA COSTIERA", 0.32, 0.01, M, sw="blu_insegna", resol=1)
    o = g.finish(name + _sfx(lod), coll)
    if lod == 0:
        _clear_ucx(name)
        pk._ucx(name, [(-L / 2, L / 2 - 1.5, -B / 2 + 0.2, B / 2 - 0.2, -1.0, 1.4), (-3.5, 2.5, -1.7, 1.7, 1.4, 3.3)], coll)
    return o


def build_nave_crociera(coll, lod=0, name="SM_MoloItalia_NaveCrociera"):
    """Sagoma da fondale (porto commerciale, [S] posizione): nave da crociera bianca ~250 m, 10 ponti, fumaiolo.
    Nome parodia "PICCIONISSIMA", nessuna livrea reale. Niente collisione (fuori dall'area giocabile)."""
    g = G(["M_MoloItalia_Tinte"])
    L, B = 250.0, 32.0
    _hull(g, L, B, -8.0, 10.0, bow=0.12, sw_side="bianco_scafo", sw_band="blu_scuro", band=(8.5, 10.5), n=(12, 8, 4)[lod], sheer=1.0)
    z = 10.0
    for k in range(5):
        x0, x1 = -L / 2 + 20 + k * 3, L / 2 - 45 - k * 6
        g.box(x0, x1, -B / 2 + 1 + k * 0.6, B / 2 - 1 - k * 0.6, z, z + 6.0, sw="bianco_scafo",
              faces=("top", "xn", "xp", "yn", "yp"))
        if lod < 2:
            for s in (-1, 1):
                y = s * (B / 2 - 1 - k * 0.6 + 0.02)
                q = [(x0 + 2, y, z + 2.2), (x1 - 2, y, z + 2.2), (x1 - 2, y, z + 4.2), (x0 + 2, y, z + 4.2)]
                g.quad(q, sw="vetro", face=(0, s, 0))
        z += 6.0
    g.box(-60.0, -40.0, -6.0, 6.0, z, z + 12.0, sw="fumaiolo")
    if lod < 2:
        for s in (-1, 1):
            M = Matrix.Translation((L / 2 - 30.0, s * (B / 2 + 0.05), 6.0)) @ Matrix.Rotation(math.radians(0 if s < 0 else 180), 4, "Z") @ \
                Matrix.Rotation(math.radians(90), 4, "X")
            g.text("PICCIONISSIMA", 3.0, 0.1, M, sw="blu_scuro", resol=1)
    return g.finish(name + _sfx(lod), coll)


def build_gru(coll, lod=0, name="SM_MoloItalia_GruPortuale"):
    """Gru a cavalletto da container, sagoma da fondale bianco-rossa: portale 30 x 16 m, h ~45 m, braccio sollevato."""
    g = G(["M_MoloItalia_Tinte"])
    for x in (-8.0, 8.0):
        for y in (-12.0, 12.0):
            g.box(x - 0.8, x + 0.8, y - 0.8, y + 0.8, 0.0, 40.0, sw="bianco", faces=("xn", "xp", "yn", "yp"))
    for x in (-8.0, 8.0):
        g.box(x - 1.0, x + 1.0, -13.0, 13.0, 30.0, 32.0, sw="rosso_insegna")
    g.box(-9.0, 9.0, -13.0, 13.0, 40.0, 44.0, sw="bianco")
    M = Matrix.Translation((0, -13.0, 42.0)) @ Matrix.Rotation(math.radians(-70), 4, "X")
    g.box(-1.2, 1.2, 0.0, 2.4, 0.0, 50.0, sw="rosso_insegna", M=M)
    g.box(-1.2, 1.2, 13.0, 40.0, 41.0, 43.4, sw="bianco")
    return g.finish(name + _sfx(lod), coll)


# =============================================================================================================
# build
# =============================================================================================================
LODDED = {
    "SM_MoloItalia_Faro": build_faro, "SM_MoloItalia_RistorantePiccioni": build_ristorante,
    "SM_MoloItalia_Capitaneria": build_capitaneria, "SM_MoloItalia_Edificio4P": build_edificio4p,
    "SM_MoloItalia_EdificioEst": build_edificio_est, "SM_Morin_LampionePastorale": build_lampione_pastorale,
    "SM_MoloItalia_RinghieraModulo": build_ringhiera, "SM_MoloItalia_Monumento": build_monumento,
    "SM_MoloItalia_MonumentoAlpini": build_monumento_alpini, "SM_MoloItalia_Dito": build_dito,
    "SM_MoloItalia_Motovedetta": build_motovedetta, "SM_MoloItalia_NaveCrociera": build_nave_crociera,
    "SM_MoloItalia_GruPortuale": build_gru,
}
for _v in "ABC":
    LODDED[f"SM_Molo_Scogliera_{_v}"] = (lambda v: (lambda coll, lod=0: build_scogliera(coll, v, lod)))(_v)
for _n in ("Tiramolla", "Spingitutto", "Ostinato"):
    LODDED[f"SM_MoloItalia_Rimorchiatore_{_n}"] = (lambda n: (lambda coll, lod=0: build_rimorchiatore(coll, n, lod)))(_n)
for _v in ("Blu", "Rosso"):
    LODDED[f"SM_MoloItalia_InfoPoint_{_v}"] = (lambda v: (lambda coll, lod=0: build_infopoint(coll, v, lod)))(_v)
SINGLE = {"SM_MoloItalia_Suolo": build_suolo_molo, "SM_MoloItalia_Suolo_Radice": build_suolo_radice}
BUDGET = {"SM_MoloItalia_Suolo": 2000, "SM_MoloItalia_Suolo_Radice": 2000, "SM_Molo_Scogliera": 2000, "SM_MoloItalia_Faro": 8000,
          "SM_MoloItalia_RistorantePiccioni": 20000, "SM_MoloItalia_Capitaneria": 5000, "SM_MoloItalia_Edificio4P": 5000,
          "SM_MoloItalia_EdificioEst": 5000, "SM_Morin_LampionePastorale": 3000, "SM_MoloItalia_Rimorchiatore": 15000,
          "SM_MoloItalia_NaveCrociera": 5000, "SM_MoloItalia_GruPortuale": 1000}


def _hide_kit(coll):
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide


def build_all(only=None):
    coll = pk._coll(KIT)
    rep = {}
    for nm, fn in LODDED.items():
        if only and nm not in only:
            continue
        rep[nm] = [pk.tri_count(fn(coll, lod=l)) for l in range(3)]
    for nm, fn in SINGLE.items():
        if only and nm not in only:
            continue
        rep[nm] = [pk.tri_count(fn(coll))]
    _hide_kit(coll)
    for nm in rep:
        o = bpy.data.objects[nm]
        n_ucx = len([u for u in coll.objects if u.name.startswith(f"UCX_{nm}_")])
        rep[nm] = (rep[nm], tuple(round(d, 2) for d in o.dimensions), n_ucx)
        print(f"{nm:<40} tri {rep[nm][0]}  dim {rep[nm][1]}  UCX {n_ucx}")
    return rep


# =============================================================================================================
# disposizione (coordinate Blender): righe (asset, nome, X, Y, Z, rotZ, scala, gruppo)
# =============================================================================================================
def layout():
    rng = np.random.default_rng(SEED)
    R = []

    def add(g, a, n, x, y, z=0.0, rz=0.0, s=1.0):
        R.append((a, n, float(x), float(y), float(z), float(rz), float(s), g))
    S = section_lines()
    # --- suolo e pezzi unici in coordinate di progetto
    for a in ("SM_MoloItalia_Suolo", "SM_MoloItalia_Suolo_Radice", "SM_MoloItalia_Monumento", "SM_MoloItalia_Capitaneria",
              "SM_MoloItalia_Edificio4P", "SM_MoloItalia_EdificioEst"):
        add("suolo", a, a.replace("SM_", "MI_"), 0.0, 0.0)
    # --- ciglio d'ormeggio (moduli banchina v2): bacino a destra del verso di posa -> si percorre B al contrario
    B = [_v2(p) for p in B_LINE]
    k = 0
    dita_y = [(-115.3, -107.5), (-160.9, -152.0)]

    def on_dito(p):
        return abs(p.x - 571.8) < 1.0 and any(y0 - 0.5 < p.y < y1 + 0.5 for y0, y1 in dita_y)
    segs = [(B[2], B[1]), (B[1], _v2((571.8, Y_RADICE_B)))]
    bitte = []
    for a, b in segs:
        d = (b - a).normalized()
        L = (b - a).length
        n = math.ceil(L / 4.0)
        for j in range(n):
            p = a + d * min(4.0 * j, L - 4.0)
            q = p + d * 2.0
            if on_dito(q):
                continue
            add("banchina", "SM_Banchina_Mod4m_v2", f"MI_Mod_{k:03d}", p.x, p.y, 0.0, yaw_of(d)); k += 1
            if j % 4 == 1 and not on_dito(q) and not (RIST[2] - 2.0 < q.y < RIST[3] + 2.0 and q.x < 575.0):
                c = q + _left(d) * 0.38
                bitte.append((c, yaw_of(d)))
    # calata della radice (Y 1,3, da X 571,8 a 640): mare a sud
    a, b = _v2((571.8, Y_RADICE_B)), _v2((RADICE_X1, Y_RADICE_B))
    for j in range(math.ceil((b - a).length / 4.0)):
        p = a + Vector((min(4.0 * j, (b - a).length - 4.0), 0))
        add("banchina", "SM_Banchina_Mod4m_v2", f"MI_Mod_{k:03d}", p.x, p.y, 0.0, 0.0); k += 1
        if j % 4 == 2:
            bitte.append((p + Vector((2.0, 0.38)), 0.0))
    for i, (c, rz) in enumerate(bitte):
        add("banchina", "SM_Banchina_Bitta_v2", f"MI_Bitta_{i:02d}", c.x, c.y, -0.012, rz)
    # --- scogliera
    for i, (x, y, rz, v) in enumerate(scogliera_slots()):
        add("scogliera", f"SM_Molo_Scogliera_{v}", f"MI_Scogliera_{i:03d}", x, y, 0.0, rz)
    # --- moli a dito e battelli "Stella del Golfo"
    for k2, (nm, (p0, p1)) in enumerate(DITA.items()):
        d = seg_dir(p0, p1)
        add("dita", "SM_MoloItalia_Dito", f"MI_Dito_{nm}", p0[0] - 2.2 * d.x, p0[1] - 2.2 * d.y, 0.0, yaw_of(d))
        for j in range(4):
            c = _v2(p0) + d * (6.0 + 12.0 * j)
            for s in (-1, 1):
                q = c + _left(d) * s * (DITO_W / 2 - 0.4)
                add("dita", "SM_Banchina_Bitta_v2", f"MI_Dito_{nm}_Bitta_{j}{'S' if s < 0 else 'N'}", q.x, q.y, -0.012, yaw_of(d))
    for nm, side in (("D1", -1), ("D2", 1)):
        p0, p1 = DITA[nm]
        d = seg_dir(p0, p1)
        c = _v2(p0) + d * 25.0 + _left(d) * side * (DITO_W / 2 + 3.77 + 0.6)
        add("barche", "SM_Morin_Battello", f"MI_Battello_{nm}", c.x, c.y, Z_W + 0.03, yaw_of(d) + 180.0)
    # --- faro (porta verso il molo: -X locale contro il verso del ramo 2) e ringhiere della testata
    d2 = seg_dir(O_LINE[1], O_LINE[2])
    add("landmark", "SM_MoloItalia_Faro", "MI_Faro", FARO_XY[0], FARO_XY[1], Z_MARC, yaw_of(d2))
    t0, t1 = _v2(TESTATA[0]), _v2(TESTATA[1])
    dt = (t1 - t0).normalized()
    nt = int((t1 - t0).length // 2.0)
    for j in range(nt):
        p = t0 + dt * (0.3 + 2.0 * j) - _right(dt) * 0.0 + _left(dt) * 0.35
        add("arredi", "SM_MoloItalia_RinghieraModulo", f"MI_Ringhiera_T{j:02d}", p.x, p.y, Z_MARC if j < 2 else 0.0, yaw_of(dt))
    for j in range(7):   # lato sud degli ultimi ~15 m (bordo esterno del marciapiede)
        p = _v2(O_LINE[2]) - d2 * (2.2 + 2.2 * (j + 1)) + _left(d2) * 0.35
        add("arredi", "SM_MoloItalia_RinghieraModulo", f"MI_Ringhiera_S{j:02d}", p.x, p.y, Z_MARC, yaw_of(d2))
    # --- ristorante "I Piccioni" (chiatta perpendicolare al molo, lato est del ramo 1)
    cx, cy = (RIST[0] + RIST[1]) / 2, (RIST[2] + RIST[3]) / 2
    add("landmark", "SM_MoloItalia_RistorantePiccioni", "MI_RistorantePiccioni", cx, cy, 0.0, 0.0)
    # --- lampioni a pastorale sul bordo esterno del marciapiede (braccio verso la carreggiata), ogni ~27 m [S]
    O = [_v2(p) for p in O_LINE]
    pts, tot = along(O, 27.0, start=6.0, end_margin=8.0)
    lamp = []
    for i, (p, d, s) in enumerate(pts):
        q = p + _left(d) * 0.45
        lamp.append((q, d, s))
        add("arredi", "SM_Morin_LampionePastorale", f"MI_Pastorale_{i:02d}", q.x, q.y, Z_MARC, yaw_of(_left(d)))
    add("arredi", "SM_Morin_LampionePastorale", "MI_Pastorale_Monumento", 556.6, 49.5, 0.0, 0.0)
    add("arredi", "SM_Morin_LampionePastorale", "MI_Pastorale_Raccordo_00", 563.5, 60.0, 0.0, 180.0)
    add("arredi", "SM_Morin_LampionePastorale", "MI_Pastorale_Raccordo_01", 563.5, 80.0, 0.0, 180.0)
    # --- panchine fra un lampione e l'altro, sul marciapiede verso il bordo esterno
    for i in range(len(lamp) - 1):
        if i % 2 == 1:
            continue
        p, d, s = lamp[i]
        q = p + d * 13.5 + _left(d) * 0.4
        add("arredi", "SM_Morin_Panchina", f"MI_Panchina_{i:02d}", q.x, q.y, Z_MARC, yaw_of(d))
    # --- New Jersey sul marciapiede del ramo 2, ultimi ~60 m prima della testata
    for j in range(5):
        p = O[2] - d2 * (24.0 + 11.0 * j) + _left(d2) * 1.2
        add("arredi", "SM_Morin_NewJersey", f"MI_NewJersey_{j:02d}", p.x, p.y, Z_MARC, yaw_of(d2))
    # --- monumento sul ramo 2 [S]: a ~97 m dal gomito, sul marciapiede
    p = O[1] + d2 * 97.0 + _left(d2) * 2.3
    add("landmark", "SM_MoloItalia_MonumentoAlpini", "MI_MonumentoAlpini", p.x, p.y, Z_MARC, yaw_of(d2))
    # --- info point / taxi (3 casette a facce piane)
    for i, (x, y) in enumerate(INFOPOINT):
        add("radice", "SM_MoloItalia_InfoPoint_" + ("Blu" if i != 1 else "Rosso"), f"MI_InfoPoint_{i}", x, y, 0.0, 0.0)
    # --- auto parcheggiate (_Col v2: il molo e' giocabile)
    k = 0
    for row_x, rz in ((583.2, 0.0), (572.8, 180.0)):          # parcheggio della Guardia Costiera a pettine
        for j in range(13):
            if rng.random() < 0.25:
                continue
            y = 48.75 + 2.5 * j
            add("auto", AUTO_COL[int(rng.integers(0, len(AUTO_COL)))], f"MI_Auto_{k:02d}", row_x, y, 0.0, rz + rng.uniform(-2, 2)); k += 1
    for j in range(6):                                          # in linea lungo l'edificio a 4 piani
        if rng.random() < 0.2:
            continue
        add("auto", AUTO_COL[int(rng.integers(0, len(AUTO_COL)))], f"MI_Auto_{k:02d}", 577.65, 7.0 + 6.0 * j, 0.0, 90.0); k += 1
    d1 = seg_dir(O_LINE[0], O_LINE[1])                           # lato ovest del ramo 1, accanto al marciapiede (Y 38 -> -10)
    for j in range(8):
        if rng.random() < 0.3:
            continue
        p = O[0] + d1 * (4.0 + 6.0 * j) + _left(d1) * (W_MARC + 1.3)
        add("auto", AUTO_COL[int(rng.integers(0, len(AUTO_COL)))], f"MI_Auto_{k:02d}", p.x, p.y, 0.0, yaw_of(d1)); k += 1
    # --- giardino della Capitaneria: palme e un pino
    for i, y in enumerate((48.5, 55.0, 61.5, 68.0, 74.5)):
        add("radice", "SM_Morin_PalmaA", f"MI_Giardino_Palma_{i}", 589.6, y, 0.25, rng.uniform(0, 360), rng.uniform(0.75, 0.9))
    add("radice", "SM_Morin_PinoDomestico", "MI_Giardino_Pino", 600.5, 41.2, 0.0, 40.0, 0.8)
    for i, x in enumerate((588.0, 600.0, 612.0)):               # pini del parcheggio taxi
        add("radice", "SM_Morin_PinoDomestico", f"MI_Taxi_Pino_{i}", x, 97.0, 0.0, 70.0 * i, 0.75)
    # --- barche ormeggiate
    e1 = seg_dir(B_LINE[0], B_LINE[1])                         # ramo 1 verso il gomito (bacino a sinistra)
    for i, (nm, y) in enumerate((("Tiramolla", -172.0), ("Spingitutto", -186.0))):
        x = 571.8 + 5.0 + 0.6
        add("barche", f"SM_MoloItalia_Rimorchiatore_{nm}", f"MI_Rimorchiatore_{nm}", x, y + 0.0, Z_W, -90.0 if i == 0 else 90.0)
    e2 = seg_dir(B_LINE[1], B_LINE[2])
    p = _v2(B_LINE[1]) + e2 * 60.0 + _left(e2) * (5.0 + 0.6)
    add("barche", "SM_MoloItalia_Rimorchiatore_Ostinato", "MI_Rimorchiatore_Ostinato", p.x, p.y, Z_W, yaw_of(e2))
    for i, x in enumerate((606.0, 626.0)):
        add("barche", "SM_MoloItalia_Motovedetta", f"MI_Motovedetta_{i}", x, Y_RADICE_B - 2.3 - 0.4, Z_W, 180.0 * i)
    # --- fondale: nave da crociera e gru del porto commerciale [S]
    add("fondale", "SM_MoloItalia_NaveCrociera", "MI_NaveCrociera", 900.0, -260.0, Z_W, 74.0)
    for i in range(5):
        add("fondale", "SM_MoloItalia_GruPortuale", f"MI_Gru_{i}", 800.0 + 30.0 * i, 30.0 + 4.0 * i, 0.0, 0.0)
    return R


def write_csv(rows, path="exports/molo_italia/molo_italia_posizioni_v1.csv"):
    import morin_blocco2 as b2
    os.makedirs(f"{PROJ}/exports/molo_italia", exist_ok=True)
    lines = ["asset,nome,x,y,z,yaw,scala,gruppo"]
    for a, n, x, y, z, rz, s, g in rows:
        yaw = -rz if abs(rz) > 1e-9 else 0.0
        lines.append(f"{a},{n},{b2._ue(x * 100)},{b2._ue(-y * 100)},{b2._ue(z * 100)},{yaw:.4f},{s:.3f},{g}")
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print(path, len(rows))
    return path


def build_context(rows, name=CTX):
    coll = pk._coll(name)
    for o in list(coll.objects):
        bpy.data.objects.remove(o)
    for a, n, x, y, z, rz, s, g in rows:
        me = KIT_MESH.get(a) or (bpy.data.objects[a].data if a in bpy.data.objects else None)
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
    # fine del Blocco 2 (dal CSV v2 dei nuovi: piazzale, angolo, aste, bandiere, chiosco)
    import csv
    with open(f"{PROJ}/exports/blocco2/blocco2_nuovi_v2.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            me = KIT_MESH.get(r["asset"]) or (bpy.data.objects[r["asset"]].data if r["asset"] in bpy.data.objects else None)
            x = float(r["x"]) / 100
            if me is None or (x < 500 and r["asset"] not in ("SM_Pav_Piazzale_Fine_B2_v2", "SM_Pav_Piazzetta_Chiosco_B2", "SM_Pav_Scritta_Morin")):
                continue
            o = bpy.data.objects.new("CTX_B2_" + r["nome"], me)
            o.location = (x, -float(r["y"]) / 100, float(r["z"]) / 100)
            o.rotation_euler = (0, 0, math.radians(-float(r["yaw"])))
            coll.objects.link(o)
    print("contesto:", len(coll.objects))
    return coll


def setup_world():
    """Acqua di riferimento (solo render), sole radente da ovest, cielo."""
    sc = bpy.context.scene
    if "REF_Acqua_MI" not in bpy.data.objects:
        bm = bmesh.new()
        pk._box(bm, 400.0, 1200.0, -450.0, 50.0, Z_W, Z_W, 0, ("top",))
        me = bpy.data.meshes.new("REF_Acqua_MI")
        bm.to_mesh(me)
        o = bpy.data.objects.new("REF_Acqua_MI", me)
        sc.collection.objects.link(o)
        m = bpy.data.materials.new("REF_Acqua_MI")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (0.02, 0.10, 0.12, 1)
        b.inputs["Roughness"].default_value = 0.08
        me.materials.append(m)
    if "Sole_MI" not in bpy.data.objects:
        ld = bpy.data.lights.new("Sole_MI", "SUN")
        ld.energy = 4.0
        ld.angle = math.radians(1.0)
        o = bpy.data.objects.new("Sole_MI", ld)
        o.rotation_euler = (math.radians(55), 0, math.radians(-115))
        sc.collection.objects.link(o)
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.45, 0.62, 0.85, 1)
    bg.inputs[1].default_value = 0.9


def export_all(overwrite=False, only=None):
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
            if only and nm not in only:
                continue
            for lod in range(3):
                on = nm + _sfx(lod)
                reps.append(morin_export.export_fbx([bpy.data.objects[on]], f"{EXPDIR}/{on}.fbx", mode="asset",
                                                    overwrite=overwrite, include_ucx=(lod == 0), bake_rotation=(lod > 0),
                                                    verbose=False))
        for nm in SINGLE:
            if only and nm not in only:
                continue
            reps.append(morin_export.export_fbx([bpy.data.objects[nm]], f"{EXPDIR}/{nm}.fbx", mode="asset",
                                                overwrite=overwrite, include_ucx=True, verbose=False))
    finally:
        for n, (hv, hg) in hidden.items():
            o = bpy.data.objects.get(n)
            if o is not None:
                o.hide_viewport = hv
                o.hide_set(hg)
    return reps
