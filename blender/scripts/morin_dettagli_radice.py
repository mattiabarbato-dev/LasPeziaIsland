"""morin_dettagli_radice.py — dettagli della radice del molo dalle foto nuove dell'utente (2026-11-20).

Scheda: ref/foto_nuove_2026-11-20.md (geo-scout) §2 dehors fila A, §3 cestini, §4 cartelli e new jersey, §5 Sirena, §6 pescherecci,
§9 nomi parodia, §10 porzioni di foto per le texture, §11 posizioni.
Foto (deroga CLAUDE.md §5, marca [SV] in CREDITS): R2 ristoranti_visti_da_di_fronte_2.png, K cestino.png,
G cartelli_inizio_passegiata.png, S scultura_donna_con_pinne_su_sedia.png.
Nomi in parodia (decisione dell'utente): "RISTO LISCHERIA", "DAI PESCATORI PIGRI" (polpo che dorme sull'amaca),
"CONSORZIO RETI BUCATE — Sapori di Mare e di Tera"; pescherecci "MUGUGNO II", "ACCIUGA FELICE", "NON CE N'E'".
Testi pubblici che restano: "banchina G. Thaon di Revel", "banchina Costantino Morin", avviso dei bambini,
"La Sirena del Golfo dei Poeti — Aidyn Zeinalov" (opera pubblica, forma ricreata stilizzata).

Esegui dentro blender/arte_dettagli_radice.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_atlas_v2 as av, morin_dettagli_radice as dr; importlib.reload(av); importlib.reload(dr)
    dr.make_textures(); dr.build_materials(); dr.build_all(); dr.check_all()
    dr.write_csv(); dr.build_context(); dr.export_all()

Origini: arredi alla base (Z 0 = pavimento), pescherecci alla linea di galleggiamento con la prua verso +X locale,
insegne al centro del pannello con il fronte verso +Y locale, pontiletto in coordinate mondo (si posa in (0,0,0)).
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
TEXDIR = PROJ + "/blender/textures/dettagli"
FV = PROJ + "/ref/foto/vista/"
FA = PROJ + "/ref/foto/arredi/"
KIT = "DETT_Kit"
CTX = "DETT_Contesto"
EXPDIR = "//../exports/dettagli"
F_SCRIPT, F_PRINT = "segoescb.ttf", "segoepr.ttf"

MAT_A, MAT_W, MAT_AR, MAT_AC = ("M_Molo_Dettagli", "M_Morin_Imbarco_Legno", "M_Molo_Arbusto", "M_Molo_Arbusto_Card")
MATS = [(MAT_A, "atlas", 0), (MAT_W, "world", 2.0), (MAT_AR, "world", 0.5), (MAT_AC, "fit", 0)]
A_, W_, AR_, AC_ = range(4)

ATL = av.Atlas("T_Molo_Dettagli", 2048, 128)
CELLS = {
    "BIANCO": ((0.90, 0.90, 0.88), 0.02, 0.45, 0.0), "BIANCO_PALO": ((0.86, 0.86, 0.84), 0.02, 0.35, 0.3),
    "NERO": ((0.045, 0.045, 0.05), 0.03, 0.45, 0.0), "NERO_MET": ((0.06, 0.06, 0.065), 0.03, 0.40, 0.6),
    "GRANITO": ((0.62, 0.60, 0.57), 0.08, 0.80, 0.0), "CEMENTO": ((0.70, 0.68, 0.64), 0.06, 0.85, 0.0),
    "TERRA": ((0.20, 0.15, 0.11), 0.12, 0.95, 0.0), "LEGNO_LAV": ((0.58, 0.32, 0.14), 0.06, 0.60, 0.0, "venatura"),
    "BRONZO": ((0.30, 0.29, 0.27), 0.12, 0.45, 0.85, "ruggine"), "BRONZO_LUCE": ((0.40, 0.35, 0.27), 0.08, 0.35, 0.9),
    "GRAFITE": ((0.29, 0.29, 0.28), 0.06, 0.55, 0.3), "ZINCO": ((0.66, 0.67, 0.68), 0.04, 0.40, 0.85),
    "NJ_BIANCO": ((0.88, 0.89, 0.90), 0.03, 0.30, 0.0), "SCAFO": ((0.90, 0.90, 0.88), 0.03, 0.35, 0.0),
    "FASCIA_AZZ": ((0.10, 0.36, 0.68), 0.03, 0.35, 0.0), "FASCIA_ROSSA": ((0.62, 0.10, 0.08), 0.03, 0.35, 0.0),
    "FASCIA_VERDE": ((0.08, 0.40, 0.24), 0.03, 0.35, 0.0), "ANTIVEG": ((0.45, 0.12, 0.08), 0.08, 0.70, 0.0),
    "LEGNO_CHIARO": ((0.62, 0.47, 0.30), 0.06, 0.55, 0.0, "venatura"), "COPERTA": ((0.60, 0.60, 0.56), 0.08, 0.80, 0.0),
    "VETRO": ((0.10, 0.13, 0.17), 0.02, 0.06, 0.5, "vetro"), "ARANCIO": ((0.95, 0.42, 0.08), 0.04, 0.50, 0.0),
    "CASSETTA_BLU": ((0.12, 0.30, 0.62), 0.04, 0.55, 0.0), "GOMMA": ((0.05, 0.05, 0.05), 0.03, 0.90, 0.0, "battistrada"),
    "INOX": ((0.70, 0.71, 0.72), 0.03, 0.25, 1.0), "ACCIAIO_SCURO": ((0.16, 0.17, 0.18), 0.06, 0.60, 0.5, "ruggine"),
    "GIALLO": ((0.95, 0.78, 0.10), 0.03, 0.50, 0.0), "ROSSO": ((0.75, 0.08, 0.06), 0.03, 0.40, 0.0),
    "BORDEAUX": ((0.42, 0.08, 0.10), 0.03, 0.45, 0.0), "BLU": ((0.08, 0.30, 0.62), 0.03, 0.40, 0.0),
    "LAVAGNA_NERA": ((0.07, 0.08, 0.08), 0.05, 0.85, 0.0), "CORDA": ((0.80, 0.77, 0.68), 0.06, 0.90, 0.0),
}
for _i, _k in enumerate(CELLS):
    ATL.add(_k, _i % 16, _i // 16)
REG = {   # pannelli dipinti e porzioni di foto: (cx, cy, w, h) in celle da 128 px
    "CEST_BANDA": (0, 2, 1, 4), "CAVALLETTO": (1, 2, 2, 4), "LAVAGNA": (3, 2, 2, 3), "SIGLA": (3, 5, 2, 1),
    "SCUDO": (5, 2, 3, 4), "PANN_CONS": (8, 2, 6, 2), "RETE": (14, 2, 2, 2),
    "NJ_BLU": (8, 4, 2, 2), "FIORIERA": (10, 4, 4, 2), "SEDIA_TRAMA": (14, 4, 2, 2),
    "TARGA_THAON": (0, 6, 4, 1), "TARGA_MORIN": (4, 6, 4, 1), "TARGHETTA": (8, 6, 4, 1), "CEST_TARGHETTA": (12, 6, 1, 1),
    "NOME_A": (0, 7, 4, 1), "NOME_B": (4, 7, 4, 1), "NOME_C": (8, 7, 4, 1),
    "PANN_BIMBI": (0, 8, 2, 3), "SIRENA_TARGA": (2, 8, 3, 2), "BASAM_FR": (5, 8, 4, 2), "BASAM_LAT": (9, 8, 3, 2),
    "BRONZO_RIL": (12, 8, 4, 4), "TELO": (0, 11, 4, 4),
}
for _k, _v in REG.items():
    ATL.add(_k, *_v)

NOMI = {"A": "MUGUGNO II", "B": "ACCIUGA FELICE", "C": "NON CE N'È"}


def _cv(W, H, x0, x1, y0, y1, bg, rough=0.45, metal=0.0):
    return Canvas(x0, x1, y0, y1, max(W / (x1 - x0), H / (y1 - y0)), bg, rough, metal)


def _photo(path, quad, W, H, sigma=None, strength=0.8):
    """Porzione raddrizzata della foto (quad TL, TR, BR, BL in pixel) -> array riga 0 = basso."""
    img = tp.load(path)[..., :3]
    a = tp.warp(img, quad, W, H)
    if sigma:
        a = tp.delight(a, sigma, strength)
    return np.clip(a, 0, 1)[::-1].copy()


def _rhm(rgb, rough, metal, hs=0.35, hsig=3.0):
    L = tp.lum(rgb)
    h = 0.5 + hs * (tp.highpass(L, hsig) - 1)
    return rgb, h.astype(np.float32), np.full(L.shape, rough, np.float32), np.full(L.shape, metal, np.float32)


# ---- pannelli dipinti (testi vettoriali, nessun pixel di foto) -------------------------------------------------------
def p_cavalletto(W, H):
    """Cavalletto bianco: RISTO LISCHERIA (parodia di Risto Pescheria), una lisca di pesce, motti generici."""
    cv = _cv(W, H, 0, 0.55, 0, 1.0, (0.95, 0.95, 0.93), 0.4)
    blu, ros = (0.10, 0.22, 0.55), (0.80, 0.12, 0.10)
    cv.rect(0.0, 0.0, 0.55, 0.012, (0.75, 0.76, 0.78))
    cv.text("RISTO", 0.05, 0.86, 0.50, 0.95, ros, font=F_SCRIPT)
    cv.text("LISCHERIA", 0.03, 0.74, 0.52, 0.85, blu, font=F_BOLD)
    # lisca: spina, testa e coda
    cv.line([(0.12, 0.66), (0.40, 0.66)], 0.010, ros)
    cv.circle(0.42, 0.66, 0.030, ros)
    cv.circle(0.43, 0.67, 0.006, (0.95, 0.95, 0.93))
    cv.poly([(0.12, 0.66), (0.07, 0.70), (0.08, 0.66), (0.07, 0.62)], ros)
    for k in range(6):
        x = 0.16 + 0.04 * k
        cv.line([(x, 0.62), (x + 0.015, 0.66), (x, 0.70)], 0.006, ros)
    cv.text("o mangi o porti via", 0.04, 0.53, 0.51, 0.59, blu, font=F_SCRIPT)
    cv.rect(0.06, 0.505, 0.49, 0.51, blu)
    cv.text("SCEGLI IL PESCE", 0.03, 0.36, 0.52, 0.44, blu, font=F_BOLD)
    cv.text("SCEGLI LA COTTURA", 0.03, 0.22, 0.52, 0.30, ros, font=F_BOLD)
    cv.text("fritto - al forno - alla griglia", 0.04, 0.12, 0.51, 0.17, blu, font=F_SANS)
    cv.grime(61, 0.04, 0.05)
    return cv.out(W, H)


def p_lavagna(W, H):
    cv = _cv(W, H, 0, 0.5, 0, 0.75, (0.07, 0.08, 0.08), 0.85)
    gesso = (0.88, 0.88, 0.84)
    sm = np.clip(av.noise(cv.H, cv.W, 5, 71) * 0.5 + 0.2, 0, 1) * 0.10
    cv.paint(sm, gesso)                                           # aloni di gesso cancellato
    cv.text("Menù del giorno", 0.02, 0.64, 0.48, 0.72, gesso, font=F_PRINT)
    righe = [("Muscoli ripieni", "12"), ("Trofie al pesto", "10"), ("Frittura mista", "15"), ("Acciughe fritte", "9"),
             ("Mesciua", "8")]
    for i, (t, p) in enumerate(righe):
        y = 0.55 - 0.085 * i
        cv.text(t, 0.03, y, 0.36, y + 0.055, gesso, align="LEFT", font=F_PRINT)
        cv.text(p + " €", 0.36, y, 0.48, y + 0.055, (0.95, 0.80, 0.45), align="RIGHT", font=F_PRINT)
    cv.text("pesce fresco del golfo", 0.03, 0.04, 0.47, 0.10, (0.70, 0.88, 0.95), font=F_PRINT)
    return cv.out(W, H)


def p_scudo(W, H):
    """Scudo bordeaux 'DAI PESCATORI PIGRI' con un polpo che dorme sull'amaca (parodia dello scudo 'dai pescatori')."""
    cv = _cv(W, H, 0, 0.95, 0, 1.15, (0.42, 0.08, 0.10), 0.45)
    cream = (0.93, 0.88, 0.78)
    pts = _shield_pts(0.95, 1.15)
    cv.poly(pts, (0.36, 0.06, 0.08))
    inner = [(0.475 + (x - 0.475) * 0.93, 0.575 + (y - 0.575) * 0.94) for x, y in pts]
    cv.poly(inner, cream)
    inner2 = [(0.475 + (x - 0.475) * 0.90, 0.575 + (y - 0.575) * 0.915) for x, y in pts]
    cv.poly(inner2, (0.46, 0.09, 0.11))
    cv.text("Risto", 0.30, 1.00, 0.65, 1.07, cream, font=F_SCRIPT)
    cv.text("dai pescatori", 0.08, 0.86, 0.87, 0.98, cream, font=F_SCRIPT)
    # amaca fra due pali
    cv.line([(0.16, 0.42), (0.16, 0.76)], 0.016, cream)
    cv.line([(0.79, 0.42), (0.79, 0.76)], 0.016, cream)
    cv.line([(0.16, 0.70), (0.30, 0.58), (0.475, 0.55), (0.65, 0.58), (0.79, 0.70)], 0.012, cream)
    cv.line([(0.16, 0.66), (0.30, 0.52), (0.475, 0.49), (0.65, 0.52), (0.79, 0.66)], 0.012, cream)
    # polpo sdraiato: testa, occhi chiusi, tentacoli arricciati che pendono
    cv.ellipse(0.40, 0.64, 0.11, 0.075, cream, rot=0.25)
    cv.line([(0.36, 0.655), (0.39, 0.645)], 0.008, (0.46, 0.09, 0.11))
    cv.line([(0.42, 0.665), (0.45, 0.655)], 0.008, (0.46, 0.09, 0.11))
    for k in range(6):
        x0 = 0.42 + 0.045 * k
        sgn = 1 if k % 2 else -1
        cv.line([(x0, 0.57), (x0 + 0.02, 0.50), (x0 + 0.01 + 0.02 * sgn, 0.43), (x0 + 0.04, 0.40), (x0 + 0.06, 0.42)],
                0.012, cream)
    cv.text("z", 0.53, 0.70, 0.58, 0.75, cream, font=F_BOLD)
    cv.text("Z", 0.58, 0.74, 0.65, 0.81, cream, font=F_BOLD)
    cv.text("PIGRI", 0.18, 0.22, 0.77, 0.36, cream, font=F_BOLD)
    cv.text("gastronomia di mare", 0.20, 0.14, 0.75, 0.20, cream, font=F_SERIF)
    cv.grime(62, 0.05, 0.08)
    return cv.out(W, H)


def _shield_pts(w, h, n=10):
    """Contorno dello scudo (antiorario): lati dritti fino a 0,45 h, punta in basso ad arco."""
    pts = [(0.0, h), (0.0, 0.45 * h)]
    for k in range(1, n):
        t = k / n
        a = math.pi * t / 2
        pts.append((w / 2 - w / 2 * math.cos(a), 0.45 * h - 0.45 * h * math.sin(a) ** 1.2))
    pts.append((w / 2, 0.0))
    for k in range(n - 1, 0, -1):
        t = k / n
        a = math.pi * t / 2
        pts.append((w / 2 + w / 2 * math.cos(a), 0.45 * h - 0.45 * h * math.sin(a) ** 1.2))
    pts += [(w, 0.45 * h), (w, h), (0.75 * w, h - 0.04), (0.5 * w, h), (0.25 * w, h - 0.04)]
    return pts


def p_pann_cons(W, H):
    cv = _cv(W, H, 0, 1.30, 0, 0.38, (0.95, 0.95, 0.93), 0.45)
    blu = (0.18, 0.30, 0.55)
    cv.rect(0, 0, 1.30, 0.02, blu)
    cv.rect(0, 0.36, 1.30, 0.38, blu)
    cv.rect(0, 0, 0.02, 0.38, blu)
    cv.rect(1.28, 0, 1.30, 0.38, blu)
    cv.text("CONSORZIO RETI BUCATE", 0.06, 0.195, 1.24, 0.33, blu, font=F_BOLD)
    cv.text("Sapori di Mare e di Tèra", 0.10, 0.05, 1.20, 0.16, (0.70, 0.12, 0.10), font=F_SERIF_B)
    cv.grime(63, 0.04, 0.08)
    return cv.out(W, H)


def p_rete(W, H):
    cv = _cv(W, H, 0, 0.5, 0, 0.5, (0.04, 0.16, 0.12), 0.9)
    X, Y = cv.X, cv.Y
    m = ((np.abs(((X + Y) * 40) % 1 - 0.5) < 0.12) | (np.abs(((X - Y) * 40) % 1 - 0.5) < 0.12)).astype(np.float32)
    cv.paint(m, (0.12, 0.45, 0.32), dh=0.3)
    cv.grime(64, 0.15, 0.0)
    return cv.out(W, H)


def p_sedia(W, H):
    """Trama della seduta e dello schienale: polipropilene nero con fori a rombo."""
    cv = _cv(W, H, 0, 0.5, 0, 0.5, (0.05, 0.05, 0.055), 0.45)
    X, Y = cv.X, cv.Y
    hole = ((np.abs(((X + Y) * 14) % 1 - 0.5) + np.abs(((X - Y) * 14) % 1 - 0.5)) < 0.32).astype(np.float32)
    cv.paint(hole, (0.012, 0.012, 0.012), rough=0.9, dh=-0.4)
    return cv.out(W, H)


def p_targa_thaon(W, H):
    cv = _cv(W, H, 0, 0.9, 0, 0.225, (0.96, 0.96, 0.95), 0.4)
    k = (0.05, 0.05, 0.05)
    for r in ((0, 0, 0.9, 0.012), (0, 0.213, 0.9, 0.225), (0, 0, 0.012, 0.225), (0.888, 0, 0.9, 0.225)):
        cv.rect(*r, k)
    cv.text("banchina", 0.04, 0.13, 0.86, 0.20, k, align="LEFT", font=F_SANS)
    cv.text("G. Thaon di Revel", 0.04, 0.03, 0.86, 0.13, k, align="LEFT", font=F_SANS)
    return cv.out(W, H)


def p_targa_morin(W, H):
    cv = _cv(W, H, 0, 0.6, 0, 0.15, (0.96, 0.96, 0.95), 0.4)
    k = (0.05, 0.05, 0.05)
    cv.line([(0.03, 0.08), (0.055, 0.10), (0.08, 0.085), (0.105, 0.10), (0.13, 0.08)], 0.008, (0.10, 0.25, 0.55))
    cv.text("banchina", 0.15, 0.085, 0.57, 0.135, k, align="LEFT", font=F_SANS)
    cv.text("Costantino Morin", 0.15, 0.02, 0.57, 0.085, k, align="LEFT", font=F_BOLD)
    return cv.out(W, H)


def p_bimbi(W, H):
    cv = _cv(W, H, 0, 0.6, 0, 0.9, (0.96, 0.96, 0.95), 0.4)
    blu, k = (0.10, 0.30, 0.68), (0.05, 0.05, 0.05)
    cv.rect(0.10, 0.44, 0.50, 0.84, blu)
    w = (0.97, 0.97, 0.97)
    cv.circle(0.24, 0.76, 0.035, w)                                      # adulto
    cv.poly([(0.20, 0.71), (0.28, 0.71), (0.30, 0.58), (0.18, 0.58)], w)
    cv.rect(0.195, 0.47, 0.225, 0.58, w)
    cv.rect(0.255, 0.47, 0.285, 0.58, w)
    cv.circle(0.37, 0.67, 0.028, w)                                      # bambino
    cv.poly([(0.34, 0.63), (0.40, 0.63), (0.41, 0.54), (0.33, 0.54)], w)
    cv.rect(0.34, 0.47, 0.362, 0.54, w)
    cv.rect(0.378, 0.47, 0.40, 0.54, w)
    cv.line([(0.29, 0.66), (0.33, 0.60)], 0.016, w)                       # per mano
    cv.text("ATTENZIONE", 0.05, 0.34, 0.55, 0.41, k, font=F_BOLD)
    for i, t in enumerate(("I bambini devono essere", "accompagnati per mano", "lungo la banchina")):
        y = 0.25 - 0.07 * i
        cv.text(t, 0.04, y, 0.56, y + 0.06, k, font=F_SANS)
    return cv.out(W, H)


def p_targhetta(W, H):
    cv = _cv(W, H, 0, 0.6, 0, 0.15, (0.96, 0.82, 0.12), 0.45)
    k = (0.08, 0.07, 0.05)
    for i in range(4):   # testo piccolo illeggibile (scheda §4.2)
        y = 0.115 - 0.028 * i
        cv.line([(0.04, y), (0.56 - 0.07 * (i % 2), y)], 0.010, k)
    return cv.out(W, H)


def p_cest_targhetta(W, H):
    cv = _cv(W, H, 0, 0.06, 0, 0.06, (0.92, 0.92, 0.90), 0.4)
    for i in range(3):
        cv.line([(0.01, 0.045 - 0.013 * i), (0.05, 0.045 - 0.013 * i)], 0.004, (0.2, 0.2, 0.2))
    return cv.out(W, H)


def p_nome(name):
    def fn(W, H):
        cv = _cv(W, H, 0, 2.0, 0, 0.5, CELLS["SCAFO"][0], 0.35)
        cv.text(name, 0.03, 0.06, 1.97, 0.44, (0.05, 0.12, 0.30), font=F_BOLD)
        cv.grime(65, 0.03, 0.10)
        return cv.out(W, H)
    return fn


def p_sigla(W, H):
    cv = _cv(W, H, 0, 1.0, 0, 0.5, CELLS["SCAFO"][0], 0.35)
    cv.text("SP 0000", 0.04, 0.10, 0.96, 0.40, (0.05, 0.05, 0.05), font=F_BOLD)
    return cv.out(W, H)


def p_sirena_targa(W, H):
    cv = _cv(W, H, 0, 0.45, 0, 0.30, (0.33, 0.28, 0.21), 0.35, 0.9)
    lt = (0.72, 0.62, 0.42)
    cv.text("La Sirena", 0.03, 0.19, 0.42, 0.26, lt, font=F_SERIF_B, metal=0.95, rough=0.25, dh=0.3)
    cv.text("del Golfo dei Poeti", 0.03, 0.12, 0.42, 0.18, lt, font=F_SERIF_B, metal=0.95, rough=0.25, dh=0.3)
    cv.text("Aidyn Zeinalov", 0.06, 0.04, 0.39, 0.09, lt, font=F_SERIF, metal=0.95, rough=0.25, dh=0.3)
    cv.grime(66, 0.15, 0.0)
    return cv.out(W, H)


def p_bronzo_ril(W, H):
    """Lastra di bronzo sotto i piedi: sabbia e rete in rilievo (procedurale)."""
    cv = _cv(W, H, 0, 1.0, 0, 1.0, (0.30, 0.28, 0.24), 0.5, 0.85)
    n = av.noise(cv.H, cv.W, 12, 67)
    f = av.fine(cv.H, cv.W, 68, 1.2)
    cv.h = cv.h + 0.15 * n + 0.08 * f
    X, Y = cv.X, cv.Y
    net = ((np.abs(((X + 0.3 * np.sin(Y * 6)) * 12) % 1 - 0.5) < 0.06) |
           (np.abs(((Y + 0.3 * np.sin(X * 5)) * 12) % 1 - 0.5) < 0.06)).astype(np.float32)
    cv.paint(net * (n > -0.2), (0.45, 0.38, 0.26), rough=0.3, dh=0.25)
    cv.rgb = np.clip(cv.rgb * (1 + 0.15 * n[..., None]), 0, 1)
    return cv.out(W, H)


# ---- porzioni di foto ([SV], scheda §10) -----------------------------------------------------------------------------
def p_cest_banda(W, H):
    """Fascia in rilievo del cestino con lo stemma (foto K, x 62-96, y 52-176): ripulita con un leggero de-lighting."""
    rgb = _photo(FA + "cestino.png", [(62, 52), (96, 52), (96, 176), (62, 176)], W, H, sigma=20, strength=0.5)
    return _rhm(rgb, 0.5, 0.3, 0.5, 2.0)


def p_nj_blu(W, H):
    """Plastica blu della barriera: tinta dai pixel blu della foto G (y 220-309, mediana (0,53; 0,65; 0,86), slavata dalla
    foschia: saturata a mano), grana fine dalla stessa porzione (passa-alto), graffi e sporco procedurali."""
    det = _photo(FA + "cartelli_inizio_passegiata.png", [(22, 236), (98, 232), (98, 286), (22, 290)], W, H)
    hp = tp.highpass(tp.lum(det), 3.0)
    base = np.array((0.13, 0.33, 0.74), np.float32)
    n = av.noise(H, W, 5, 91)
    rgb = base[None, None, :] * (1 + 0.05 * n + 0.10 * (hp - 1))[..., None]
    rgb = rgb * (1 - 0.15 * np.clip(av.noise(H, W, 20, 92), 0, 1))[..., None]
    return np.clip(rgb, 0, 1), (0.5 + 0.1 * (hp - 1)).astype(np.float32), np.full((H, W), 0.35, np.float32), \
        np.zeros((H, W), np.float32)


def p_fioriera(W, H):
    """Fianco della fioriera antracite (foto R2 x 575-650, y 318-348), de-lighting e tinta #222B35."""
    rgb = _photo(FV + "ristoranti_visti_da_di_fronte_2.png", [(578, 318), (648, 322), (648, 346), (578, 344)], W, H,
                 sigma=10, strength=0.9)
    rgb = tp.match_color(rgb, np.array((0.133, 0.169, 0.208)), 0.8)        # antracite #222B35 (scheda §2.3)
    rgb = tp.tileable(rgb)
    return _rhm(rgb, 0.7, 0.0, 0.25)


def p_telo(W, H):
    """Telo dell'ombrellone: in R2 (x 760-930, y 95-120) il telo e' bianco saturato (0,97): tinta bianco caldo e trama di
    tessuto acrilico procedurali, cucitura centrale e orlo; niente pixel (la porzione della scheda contiene l'icona di UI)."""
    cv = _cv(W, H, 0, 1.0, 0, 1.0, (0.90, 0.88, 0.82), 0.85)
    X, Y = cv.X, cv.Y
    weave = 0.5 + 0.25 * np.sin(X * 2 * math.pi * 180) * np.sin(Y * 2 * math.pi * 180)
    cv.rgb = np.clip(cv.rgb * (0.97 + 0.04 * weave)[..., None], 0, 1)
    cv.h = cv.h + 0.05 * weave
    cv.rect(0.495, 0.0, 0.505, 1.0, (0.80, 0.78, 0.72), dh=0.1)
    cv.rect(0.0, 0.0, 1.0, 0.02, (0.82, 0.80, 0.74), dh=0.1)
    cv.grime(93, 0.05, 0.08)
    return cv.out(W, H)


def p_basam_fr(W, H):
    """Basamento della Sirena (foto S x 110-360, y 270-405): fronte raddrizzato, pietra bocciardata."""
    rgb = _photo(FA + "scultura_donna_con_pinne_su_sedia.png", [(182, 318), (363, 286), (363, 348), (182, 406)], W, H,
                 sigma=30, strength=0.9)
    return _rhm(rgb, 0.85, 0.0, 0.4, 2.0)


def p_basam_lat(W, H):
    rgb = _photo(FA + "scultura_donna_con_pinne_su_sedia.png", [(107, 286), (178, 318), (178, 404), (108, 372)], W, H,
                 sigma=30, strength=0.9)
    return _rhm(rgb, 0.85, 0.0, 0.4, 2.0)


# ---- arbusti delle fioriere (foto R2 x 490-790, y 215-330) -----------------------------------------------------------
def make_tex_arbusto(size=1024):
    img = tp.load(FV + "ristoranti_visti_da_di_fronte_2.png")[..., :3]
    crop = tp.warp(img, [(500, 222), (780, 222), (780, 318), (500, 318)], 560, 192)
    crop = tp.delight(crop, 20.0, 0.7)
    a = tp.tileable(tp.resize(crop, size, size)[::-1].copy())
    a = np.clip(a * 1.2, 0, 1)                  # la porzione e' in ombra parziale: schiarita verso il verde-giallo della foto
    rgb, h, r, m = _rhm(a, 0.8, 0.0, 0.6, 2.0)
    mass = av.save_set("T_Molo_Arbusto", rgb, h, r, m, TEXDIR, 4.0)
    # card: grappoli di foglie ovali (alfa procedurale), colori presi dalla stessa porzione
    n = 512
    rng = np.random.default_rng(81)
    al = np.zeros((n, n), np.float32)
    col = tp.resize(a, n, n)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    for _ in range(340):
        cx, cy = rng.uniform(30, n - 30, 2)
        if math.hypot(cx - n / 2, cy - n / 2) > n * 0.47:
            continue
        L, Wd, ang = rng.uniform(16, 30), rng.uniform(7, 12), rng.uniform(0, math.pi)
        c, s = math.cos(ang), math.sin(ang)
        x0, x1 = int(max(cx - L, 0)), int(min(cx + L + 1, n))
        y0, y1 = int(max(cy - L, 0)), int(min(cy + L + 1, n))
        u = ((xx[y0:y1, x0:x1] - cx) * c + (yy[y0:y1, x0:x1] - cy) * s) / L
        v = (-(xx[y0:y1, x0:x1] - cx) * s + (yy[y0:y1, x0:x1] - cy) * c) / Wd
        al[y0:y1, x0:x1] = np.maximum(al[y0:y1, x0:x1], (u * u + v * v < 1).astype(np.float32))
    al = np.clip(tp.blur(al, 0.6) * 1.2, 0, 1)
    shade = 0.75 + 0.25 * tp.blur(al, 6) / max(tp.blur(al, 6).max(), 1e-3)
    rgb2 = np.clip(col * shade[..., None] * 1.05, 0, 1)
    h2 = 0.4 + 0.3 * tp.blur(al, 2)
    card = av.save_set("T_Molo_Arbusto_Card", rgb2, h2, np.full((n, n), 0.75, np.float32), np.zeros((n, n), np.float32),
                       TEXDIR, 3.0, alpha=al)
    return mass, card


def make_textures():
    painters = {k: av.color_cell(v, 500 + i) for i, (k, v) in enumerate(CELLS.items())}
    painters.update({
        "CEST_BANDA": p_cest_banda, "CAVALLETTO": p_cavalletto, "LAVAGNA": p_lavagna, "SIGLA": p_sigla, "SCUDO": p_scudo,
        "PANN_CONS": p_pann_cons, "RETE": p_rete, "NJ_BLU": p_nj_blu, "FIORIERA": p_fioriera, "SEDIA_TRAMA": p_sedia,
        "TARGA_THAON": p_targa_thaon, "TARGA_MORIN": p_targa_morin, "TARGHETTA": p_targhetta,
        "CEST_TARGHETTA": p_cest_targhetta, "NOME_A": p_nome(NOMI["A"]), "NOME_B": p_nome(NOMI["B"]),
        "NOME_C": p_nome(NOMI["C"]), "PANN_BIMBI": p_bimbi, "SIRENA_TARGA": p_sirena_targa, "BASAM_FR": p_basam_fr,
        "BASAM_LAT": p_basam_lat, "BRONZO_RIL": p_bronzo_ril, "TELO": p_telo})
    return {"atlas": ATL.bake(painters, TEXDIR, 4.0), "arbusto": make_tex_arbusto()}


def build_materials():
    t = f"{TEXDIR}/"
    for m, n, alpha in ((MAT_A, "T_Molo_Dettagli", False), (MAT_AR, "T_Molo_Arbusto", False),
                        (MAT_AC, "T_Molo_Arbusto_Card", True)):
        pk._pbr_material(m, t + n + "_D.png", t + n + "_N.png", t + n + "_ORM.png", alpha=alpha)
    if bpy.data.materials.get(MAT_W) is None:
        d = PROJ + "/blender/textures/imbarco/T_Morin_Imbarco_Legno"
        pk._pbr_material(MAT_W, d + "_D.png", d + "_N.png", d + "_ORM.png")


# =================================================================================================================
# geometria: utilita'
# =================================================================================================================
def G():
    return av.G2(ATL, MATS)


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


def _fin(g, name, lod, coll, smooth=None):
    o = g.finish(name + _sfx(lod), coll, smooth=smooth)
    for s in o.material_slots:
        m = s.material
        if m is not None and m.library is not None:
            loc = next((x for x in bpy.data.materials if x.name == m.name and x.library is None), None)
            if loc is not None:
                s.material = loc
    return o


def _R(rz=0.0, rx=0.0, ry=0.0, t=(0, 0, 0)):
    return (Matrix.Translation(t) @ Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(ry), 4, "Y")
            @ Matrix.Rotation(math.radians(rx), 4, "X"))


def _panel(g, M, w, h, cell_front, cell_back, cell_edge, t=0.02, z0=0.0):
    """Pannello w x h nel piano XZ locale (x da -w/2 a w/2, z da z0 a z0+h), spessore t lungo Y; fronte verso -Y."""
    g.box(-w / 2, w / 2, -t / 2, t / 2, z0, z0 + h, cell_edge, faces=("xn", "xp", "top", "bot"), mat=M)
    P = lambda x, y, z: tuple(M @ Vector((x, y, z)))
    n_f = (M.to_3x3() @ Vector((0, -1, 0)))
    g.quad([P(-w / 2, -t / 2, z0), P(w / 2, -t / 2, z0), P(w / 2, -t / 2, z0 + h), P(-w / 2, -t / 2, z0 + h)], cell_front,
           out=tuple(n_f))
    g.quad([P(-w / 2, t / 2, z0), P(w / 2, t / 2, z0), P(w / 2, t / 2, z0 + h), P(-w / 2, t / 2, z0 + h)], cell_back,
           out=tuple(-n_f))


def _lathe(g, prof, n, cell, mat=Matrix(), cap_top=True):
    """g.lathe con le normali orientate verso l'esterno rispetto all'asse (fianchi) e alle estremita' (calotte)."""
    before = set(g.bm.faces)
    g.lathe(prof, n, cell, mat=mat, cap_top=cap_top)
    O = mat @ Vector((0, 0, 0))
    A = (mat.to_3x3() @ Vector((0, 0, 1))).normalized()
    zmid = sum(z for _, z in prof) / len(prof)
    for f in [f for f in g.bm.faces if f not in before]:
        f.normal_update()
        c = f.calc_center_median() - O
        ax = c.dot(A)
        if abs(f.normal.dot(A)) > 0.9:
            if f.normal.dot(A) * (ax - zmid) < 0:
                f.normal_flip()
        else:
            rad = c - A * ax
            if f.normal.dot(rad) < 0:
                f.normal_flip()


def _loft(g, centers, radii, cell, sides=8, cap0=True, cap1=True, up=(0, 1, 0)):
    """Tubo a sezione ellittica lungo una polilinea: radii = [(ra, rb)], rb lungo 'up' ortogonalizzato. Calotte a punta."""
    C = [Vector(c) for c in centers]

    def fn(bm):
        rings = []
        for i, c in enumerate(C):
            a = C[max(i - 1, 0)]
            b = C[min(i + 1, len(C) - 1)]
            t = (b - a).normalized()
            u = Vector(up)
            u = (u - t * u.dot(t))
            if u.length < 1e-4:
                u = Vector((1, 0, 0)) - t * t.x
            u.normalize()
            v = t.cross(u)
            ra, rb = radii[i]
            rings.append([bm.verts.new(c + v * ra * math.cos(2 * math.pi * k / sides) + u * rb *
                                       math.sin(2 * math.pi * k / sides)) for k in range(sides)])
        for r0, r1 in zip(rings[:-1], rings[1:]):
            for k in range(sides):
                k1 = (k + 1) % sides
                bm.faces.new([r0[k], r0[k1], r1[k1], r1[k]])
        for flag, ring, c, d in ((cap0, rings[0], C[0], (C[0] - C[1])), (cap1, rings[-1], C[-1], (C[-1] - C[-2]))):
            if not flag:
                continue
            tip = bm.verts.new(c + d.normalized() * min(radii[0 if ring is rings[0] else -1]) * 0.6)
            for k in range(sides):
                bm.faces.new([ring[k], ring[(k + 1) % sides], tip])
        faces = [f for f in bm.faces if any(v in rings[0] or v in rings[-1] for v in f.verts) or True]
        return faces
    before = set(g.bm.faces)
    g.new_faces(fn, cell)
    new = [f for f in g.bm.faces if f not in before]
    # normali verso l'esterno: confronto con l'asse piu' vicino
    for f in new:
        f.normal_update()
        cen = f.calc_center_median()
        best = min(C, key=lambda c: (c - cen).length)
        if f.normal.dot(cen - best) < 0:
            f.normal_flip()


def _blob(g, c, r, cell, mi_=0, seg=10, rings=6, jitter=0.0, seed=0, flat_bottom=None):
    """Ellissoide (r = (rx, ry, rz)) con deformazione casuale opzionale."""
    rng = np.random.default_rng(seed)

    def fn(bm):
        vs = []
        top = bm.verts.new((c[0], c[1], c[2] + r[2]))
        bot_z = c[2] - r[2] if flat_bottom is None else flat_bottom
        bot = bm.verts.new((c[0], c[1], bot_z))
        ringv = []
        for j in range(1, rings):
            ph = math.pi * j / rings
            row = []
            for k in range(seg):
                th = 2 * math.pi * k / seg
                # solo verso l'interno e mai sui punti estremi: la bbox resta uguale in tutti i LOD
                jit = 1.0 if (k % max(seg // 4, 1) == 0 or 2 * j == rings) else 1 - jitter * rng.uniform(0, 1)
                z = c[2] - r[2] * math.cos(ph)
                if flat_bottom is not None:
                    z = max(z, flat_bottom)
                row.append(bm.verts.new((c[0] + r[0] * math.sin(ph) * math.cos(th) * jit,
                                         c[1] + r[1] * math.sin(ph) * math.sin(th) * jit, z)))
            ringv.append(row)
        for k in range(seg):
            k1 = (k + 1) % seg
            bm.faces.new([bot, ringv[0][k1], ringv[0][k]])
            bm.faces.new([top, ringv[-1][k], ringv[-1][k1]])
        for r0, r1 in zip(ringv[:-1], ringv[1:]):
            for k in range(seg):
                k1 = (k + 1) % seg
                bm.faces.new([r0[k], r0[k1], r1[k1], r1[k]])
    before = set(g.bm.faces)
    g.new_faces(fn, cell, mi_)
    cen = Vector(c)
    for f in [f for f in g.bm.faces if f not in before]:
        f.normal_update()
        if f.normal.dot(f.calc_center_median() - cen) < 0:
            f.normal_flip()


# =================================================================================================================
# dehors della fila A
# =================================================================================================================
def build_ombrellone(coll, lod=0, s=3.0, name=None):
    """Ombrellone quadrato a palo centrale: telo s x s, bordo della mantovana a 2,40, cima ~2,95 (3 x 3) / 3,10 (4 x 4)."""
    name = name or ("SM_Molo_Ombrellone4x4" if s > 3.5 else "SM_Molo_Ombrellone3x3")
    g = G()
    h = s / 2
    z_e, z_apex = 2.52, (3.00 if s > 3.5 else 2.85)
    z_top = z_apex + 0.10
    bh, bt = (0.40, 0.10) if s > 3.5 else (0.30, 0.08)
    g.box(-bh, bh, -bh, bh, 0.0, bt, "CEMENTO" if s > 3.5 else "GRANITO", faces=("top", "xn", "xp", "yn", "yp"))
    sides = (8, 6, 4)[lod]
    g.tube([(0, 0, bt), (0, 0, z_top)], 0.03, sides, "BIANCO_PALO")
    _lathe(g, [(0.0, z_top - 0.02), (0.05, z_top - 0.02), (0.05, z_top + 0.02), (0.0, z_top + 0.05)], sides, "BIANCO_PALO")
    zm = z_e + 0.62 * (z_apex - z_e)
    E = [(-h, -h), (h, -h), (h, h), (-h, h)]
    Mi = [(x * 0.55, y * 0.55) for x, y in E]
    for i in range(4):
        (ax, ay), (bx, by) = E[i], E[(i + 1) % 4]
        (cx, cy), (dx, dy) = Mi[i], Mi[(i + 1) % 4]
        out = (ax + bx, ay + by, 0.6)
        g.quad([(ax, ay, z_e), (bx, by, z_e), (dx, dy, zm), (cx, cy, zm)], "TELO", out=out)
        g.quad([(ax, ay, z_e - 0.012), (bx, by, z_e - 0.012), (dx, dy, zm - 0.012), (cx, cy, zm - 0.012)], "TELO",
               out=(-out[0], -out[1], -1))
        f = g.new_faces(lambda bm, p=(cx, cy, dx, dy): bm.faces.new([bm.verts.new((p[0], p[1], zm)),
                                                                    bm.verts.new((p[2], p[3], zm)),
                                                                    bm.verts.new((0, 0, z_apex))]), "TELO")
        for ff in f:
            ff.normal_update()
            if ff.normal.z < 0:
                ff.normal_flip()
        f = g.new_faces(lambda bm, p=(cx, cy, dx, dy): bm.faces.new([bm.verts.new((p[0], p[1], zm - 0.012)),
                                                                    bm.verts.new((p[2], p[3], zm - 0.012)),
                                                                    bm.verts.new((0, 0, z_apex - 0.012))]), "TELO")
        for ff in f:
            ff.normal_update()
            if ff.normal.z > 0:
                ff.normal_flip()
        # mantovana: due facce vicine
        d = Vector((bx - ax, by - ay, 0)).normalized()
        nrm = Vector((d.y, -d.x, 0))
        if nrm.dot(Vector((ax + bx, ay + by, 0))) < 0:
            nrm = -nrm
        o1 = nrm * 0.004
        g.quad([(ax + o1.x, ay + o1.y, z_e - 0.13), (bx + o1.x, by + o1.y, z_e - 0.13), (bx + o1.x, by + o1.y, z_e),
                (ax + o1.x, ay + o1.y, z_e)], "TELO", out=tuple(nrm))
        g.quad([(ax - o1.x, ay - o1.y, z_e - 0.13), (bx - o1.x, by - o1.y, z_e - 0.13), (bx - o1.x, by - o1.y, z_e),
                (ax - o1.x, ay - o1.y, z_e)], "TELO", out=tuple(-nrm))
    # stecche sotto il telo e puntoni dal tirante
    z_run = z_e - 0.45
    if lod < 2:
        g.tube([(0, 0, z_run - 0.06), (0, 0, z_run + 0.06)], 0.05, sides, "BIANCO_PALO")
    ribs = [(x, y) for x, y in E] + ([(0, -h), (h, 0), (0, h), (-h, 0)] if lod == 0 else [])
    for x, y in ribs:
        k = 0.97
        p_end = (x * k, y * k, z_e - 0.03)
        p_mid = (x * 0.55, y * 0.55, zm - 0.03) if abs(x) == abs(y) else (x * 0.55, y * 0.55,
                                                                            z_e + 0.45 * (zm - z_e) - 0.03)
        g.tube([(0, 0, z_apex - 0.04), p_mid, p_end], 0.012, 3 if lod else 4, "BIANCO_PALO")
        if lod < 2:
            g.tube([(0, 0, z_run), (p_mid[0] * 0.8, p_mid[1] * 0.8, p_mid[2] - 0.05)], 0.010, 3, "BIANCO_PALO")
    return _fin(g, name, lod, coll)


def ucx_ombrellone(coll, s=3.0):
    name = "SM_Molo_Ombrellone4x4" if s > 3.5 else "SM_Molo_Ombrellone3x3"
    bh, bt = (0.40, 0.10) if s > 3.5 else (0.30, 0.08)
    pk._ucx(name, [(-bh, bh, -bh, bh, 0.0, bt), (-0.05, 0.05, -0.05, 0.05, bt, 2.30)], coll)


def build_tavolo(coll, lod=0, name="SM_Molo_TavoloNero"):
    g = G()
    sides = (8, 6, 4)[lod]
    g.box(-0.35, 0.35, -0.35, 0.35, 0.72, 0.75, "NERO_MET")
    g.tube([(0, 0, 0.03), (0, 0, 0.72)], 0.03, sides, "NERO_MET")
    for a in (45, 135):
        M = _R(a)
        g.box(-0.30, 0.30, -0.025, 0.025, 0.0, 0.035, "NERO_MET", faces=("top", "xn", "xp", "yn", "yp"), mat=M)
    if lod < 2:
        g.box(-0.16, 0.16, -0.16, 0.16, 0.69, 0.72, "NERO_MET", faces=("bot", "xn", "xp", "yn", "yp"))
    return _fin(g, name, lod, coll)


def ucx_tavolo(coll, name="SM_Molo_TavoloNero"):
    pk._ucx(name, [(-0.35, 0.35, -0.35, 0.35, 0.69, 0.75), (-0.05, 0.05, -0.05, 0.05, 0.0, 0.69),
                   (-0.22, 0.22, -0.22, 0.22, 0.0, 0.035)], coll)


def build_sedia(coll, lod=0, name="SM_Molo_SediaNera"):
    """Sedia in metallo e polipropilene nero (seduta 0,45, schienale 0,85); chi siede guarda +X."""
    g = G()
    sides = (5, 4, 3)[lod]
    hw, d0, d1 = 0.22, -0.22, 0.22
    g.box(d0, d1, -hw, hw, 0.43, 0.46, "SEDIA_TRAMA", faces=("top", "bot"))
    g.box(d0, d1, -hw, hw, 0.43, 0.46, "NERO", faces=("xn", "xp", "yn", "yp"))
    for x in (d0 + 0.02, d1 - 0.02):
        for y in (-hw + 0.02, hw - 0.02):
            top = 0.86 if x < 0 else 0.43
            foot = (x - 0.03 if x < 0 else x + 0.02, y, 0.0)
            g.tube([foot, (x, y, top)], 0.012, sides, "NERO_MET")
    M = _R(0, ry=-8, t=(d0 + 0.03, 0, 0.0))
    g.box(-0.012, 0.012, -hw, hw, 0.55, 0.86, "SEDIA_TRAMA", faces=("xn", "xp"), mat=M)
    g.box(-0.012, 0.012, -hw, hw, 0.55, 0.86, "NERO", faces=("yn", "yp", "top", "bot"), mat=M)
    if lod == 0:
        for y in (-hw + 0.02, hw - 0.02):   # braccioli
            g.tube([(d0 + 0.03, y, 0.64), (d1 - 0.04, y, 0.64), (d1 - 0.04, y, 0.46)], 0.010, 4, "NERO_MET")
    return _fin(g, name, lod, coll)


def ucx_sedia(coll, name="SM_Molo_SediaNera"):
    pk._ucx(name, [(-0.23, 0.23, -0.23, 0.23, 0.0, 0.46), (-0.26, -0.15, -0.23, 0.23, 0.46, 0.86)], coll)


FIO = (0.50, 0.225, 0.45)   # semilunghezza, semilarghezza, altezza


def build_fioriera(coll, lod=0, name="SM_Molo_FiorieraAntracite"):
    """Fioriera antracite 1,0 x 0,45 x 0,45 con un arbusto fitto (massa opaca + card mascherate)."""
    g = G()
    hx, hy, hz = FIO
    g.box(-hx, hx, -hy, hy, 0.0, hz, "FIORIERA", faces=("xn", "xp", "yn", "yp"))
    g.box(-hx, hx, -hy, hy, hz - 0.02, hz, "FIORIERA", faces=("top",))
    g.box(-hx + 0.03, hx - 0.03, -hy + 0.03, hy - 0.03, hz - 0.06, hz - 0.02, "TERRA", faces=("top",))
    # massa dell'arbusto: ellissoide schiacciato e irregolare
    segs, rings = ((16, 8), (12, 6), (8, 4))[lod]
    RX, RY, RZ, CZ = hx + 0.12, hy + 0.16, 0.56, hz + 0.44
    _blob(g, (0, 0, CZ), (RX, RY, RZ), None, AR_, segs, rings, jitter=0.10 if lod < 2 else 0.0,
          seed=5, flat_bottom=hz - 0.04)
    clamp = lambda p: (max(-RX, min(RX, p[0])), max(-RY, min(RY, p[1])), max(hz, min(CZ + RZ, p[2])))
    # card mascherate sulla superficie (sagoma frastagliata)
    rng = np.random.default_rng(7)
    n = (22, 12, 6)[lod]
    for i in range(n):
        th = rng.uniform(0, 2 * math.pi)
        ph = rng.uniform(0.15, 0.85) * math.pi / 2 + 0.3
        cx = RX * math.sin(ph) * math.cos(th) * 0.92
        cy = RY * math.sin(ph) * math.sin(th) * 0.92
        cz = CZ + RZ * math.cos(ph) * 0.92
        s = rng.uniform(0.32, 0.46) * (1.0 if lod < 2 else 1.25)
        nrm = Vector((cx / RX ** 2, cy / RY ** 2, (cz - CZ) / RZ ** 2)).normalized()
        tang = nrm.cross(Vector((0, 0, 1)))
        if tang.length < 1e-3:
            tang = Vector((1, 0, 0))
        tang.normalize()
        tang = Matrix.Rotation(rng.uniform(-0.6, 0.6), 3, nrm) @ tang
        bit = nrm.cross(tang).normalized()
        c = Vector((cx, cy, cz))
        pts = [clamp(tuple(c + (tang * a + bit * b) * s / 2)) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        g.quad(pts, None, AC_, out=tuple(nrm))
    return _fin(g, name, lod, coll)


def ucx_fioriera(coll, name="SM_Molo_FiorieraAntracite"):
    hx, hy, hz = FIO
    pk._ucx(name, [(-hx, hx, -hy, hy, 0.0, hz), (-hx, hx, -hy - 0.05, hy + 0.05, hz, 1.30)], coll)


def _aframe(g, w, h, spread, cell_front, cell_frame, lod, board=None):
    """Cavalletto A: due pannelli incernierati in cima (z h), piedi a +-spread lungo X; fronte verso +X."""
    ang = math.degrees(math.atan2(spread, h))
    for sgn in (1, -1):
        # pannello inclinato: ruota attorno a Y attorno alla cerniera in cima
        M = Matrix.Translation((0, 0, h)) @ Matrix.Rotation(math.radians(-sgn * ang), 4, "Y") @ \
            Matrix.Rotation(math.radians(90 * sgn), 4, "Z")
        # nel riferimento del pannello: x lungo Y mondo, z verso il basso -> pannello da z -h..0
        fw = 0.03
        for (x0, x1, z0, z1) in ((-w / 2, -w / 2 + fw, -h, 0), (w / 2 - fw, w / 2, -h, 0), (-w / 2, w / 2, -fw, 0),
                                 (-w / 2, w / 2, -h + 0.08, -h + 0.08 + fw)):
            g.box(x0, x1, -0.012, 0.012, z0, z1, cell_frame, mat=M)
        bw, bz0, bz1 = (w - 2 * fw, -h + 0.08 + fw, -fw) if board is None else board
        P = lambda x, y, z: tuple(M @ Vector((x, y, z)))
        nf = M.to_3x3() @ Vector((0, -1, 0))
        g.quad([P(-bw / 2, -0.006, bz0), P(bw / 2, -0.006, bz0), P(bw / 2, -0.006, bz1), P(-bw / 2, -0.006, bz1)],
               cell_front, out=tuple(nf))
        g.quad([P(-bw / 2, 0.006, bz0), P(bw / 2, 0.006, bz0), P(bw / 2, 0.006, bz1), P(-bw / 2, 0.006, bz1)],
               cell_frame, out=tuple(-nf))


def build_lavagna(coll, lod=0, name="SM_Molo_Lavagna"):
    g = G()
    _aframe(g, 0.56, 1.08, 0.22, "LAVAGNA", "LEGNO_LAV", lod)
    return _fin(g, name, lod, coll)


def build_cavalletto(coll, lod=0, name="SM_Molo_CavallettoPescheria"):
    g = G()
    _aframe(g, 0.62, 1.10, 0.22, "CAVALLETTO", "BIANCO", lod)
    return _fin(g, name, lod, coll)


def ucx_aframe(coll, name, h=1.1):
    pk._ucx_hull(name, 0, [Vector((x, y, z)) for x, y, z in ((-0.24, -0.33, 0), (0.24, -0.33, 0), (0.24, 0.33, 0),
                                                              (-0.24, 0.33, 0), (-0.03, -0.33, h), (0.03, -0.33, h),
                                                              (0.03, 0.33, h), (-0.03, 0.33, h))], coll)


# ---- insegne in parodia da sovrapporre alle facciate di A1/A2 ---------------------------------------------------------
def build_insegna_scudo(coll, lod=0, name="SM_Molo_Insegna_PescatoriPigri"):
    """Scudo 1,0 x 1,2 m, spessore 4 cm, origine al centro del retro, fronte verso +Y."""
    g = G()
    w, h, t = 1.0, 1.2, 0.04
    pts = _shield_pts(w, h, (10, 6, 4)[lod])
    P = [(x - w / 2, z - h / 2) for x, z in pts]

    def face(bm, y, flip):
        f = bm.faces.new([bm.verts.new((x, y, z)) for x, z in (P[::-1] if flip else P)])
        return f
    g.new_faces(lambda bm: face(bm, t, False), "SCUDO")
    g.new_faces(lambda bm: face(bm, 0.0, True), "BORDEAUX")
    for (xa, za), (xb, zb) in zip(P, P[1:] + P[:1]):
        g.quad([(xa, 0, za), (xb, 0, zb), (xb, t, zb), (xa, t, za)], "BORDEAUX",
               out=(zb - za, 0, -(xb - xa)) if True else None)
    o = _fin(g, name, lod, coll)
    _fix_normals_y(o, t)
    return o


def _fix_normals_y(o, t):
    """Fronte (y = t) verso +Y, retro (y = 0) verso -Y, bordo verso l'esterno del contorno."""
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    c = Vector((0, t / 2, 0))
    for f in bm.faces:
        f.normal_update()
        cen = f.calc_center_median()
        if abs(f.normal.y) > 0.9:
            want = 1 if cen.y > t / 2 else -1
            if f.normal.y * want < 0:
                f.normal_flip()
        else:
            d = Vector((cen.x, 0, cen.z))
            if f.normal.dot(d) < 0:
                f.normal_flip()
    bm.to_mesh(me)
    bm.free()


def build_insegna_pannello(coll, lod=0, name="SM_Molo_Insegna_RetiBucate"):
    """Pannello 1,30 x 0,38 m, spessore 3 cm, origine al centro del retro, fronte verso +Y."""
    g = G()
    w, h, t = 1.30, 0.38, 0.03
    g.box(-w / 2, w / 2, 0, t, -h / 2, h / 2, "BIANCO", faces=("xn", "xp", "top", "bot", "yn"))
    g.quad([(-w / 2, t, -h / 2), (w / 2, t, -h / 2), (w / 2, t, h / 2), (-w / 2, t, h / 2)], "PANN_CONS", out=(0, 1, 0))
    return _fin(g, name, lod, coll)


# =================================================================================================================
# cestino a capsula
# =================================================================================================================
CW, CD, CH = 0.25, 0.19, 0.95       # semilarghezza, semiprofondita', altezza
C_DOME = 0.70                       # inizio della cupola


def _rrect(a, b, r, n):
    """Rettangolo arrotondato (superellisse) con semiassi a, b: n punti, antiorario, partenza da +X."""
    pts = []
    e = 2.0 / r
    for k in range(n):
        th = 2 * math.pi * k / n
        c, s = math.cos(th), math.sin(th)
        x = a * math.copysign(abs(c) ** e, c)
        y = b * math.copysign(abs(s) ** e, s)
        pts.append((x, y))
    return pts


def build_cestino(coll, lod=0, name="SM_Morin_Cestino_v2"):
    """Cestino 'a capsula' grigio grafite 0,50 x 0,38 x 0,95: fianchi diritti, cupola con bocca ovale sul fronte (-Y),
    fascia in rilievo con lo stemma (porzione della foto K), targhetta bianca, zoccolo scuro."""
    g = G()
    n = (24, 16, 12)[lod]
    rr = 3.0                                   # esponente della superellisse (spigoli molto arrotondati)
    zs = [0.0, 0.03, 0.05, C_DOME]
    nd = (6, 4, 2)[lod]
    for k in range(1, nd + 1):
        zs.append(C_DOME + (CH - C_DOME) * math.sin(math.pi / 2 * k / nd))
    rings = []
    for z in zs:
        if z <= 0.031:
            a, b = CW - 0.02, CD - 0.02
        elif z <= C_DOME:
            a, b = CW, CD
        else:
            ph = math.asin(min((z - C_DOME) / (CH - C_DOME), 1.0))
            a, b = CW * math.cos(ph), CD * max(math.cos(ph), 0.0) ** 0.6
        rings.append((z, _rrect(max(a, 0.004), max(b, 0.004), rr, n)))

    def fn(bm):
        R = [[bm.verts.new((x, y, z)) for x, y in pts] for z, pts in rings]
        for r0, r1 in zip(R[:-1], R[1:]):
            for k in range(n):
                k1 = (k + 1) % n
                bm.faces.new([r0[k], r0[k1], r1[k1], r1[k]])
        bm.faces.new(R[-1])
        bm.faces.new(R[0][::-1])
    before = set(g.bm.faces)
    g.new_faces(fn, "GRAFITE")
    for f in [f for f in g.bm.faces if f not in before]:
        f.normal_update()
        cen = f.calc_center_median()
        if f.normal.dot(cen - Vector((0, 0, 0.5))) < 0:
            f.normal_flip()
        if cen.z < 0.04:
            g._set([f], "NERO")
    # bocca ovale sul fronte della cupola (-Y): disco scuro con labbro
    zb, rb = C_DOME + 0.12, (0.11, 0.06)
    ph = math.asin((zb - C_DOME) / (CH - C_DOME))
    yb = -CD * math.cos(ph) ** 0.6 - 0.004
    tilt = 35.0
    M = Matrix.Translation((0, yb, zb)) @ Matrix.Rotation(math.radians(90 + tilt), 4, "X")
    nb = (16, 12, 8)[lod]
    g.new_faces(lambda bm: bm.faces.new([bm.verts.new(M @ Vector((rb[0] * math.cos(2 * math.pi * k / nb),
                                                                   rb[1] * math.sin(2 * math.pi * k / nb), 0)))
                                         for k in range(nb)]), "NERO")
    if True:                                   # labbro anche nei LOD: definisce la bbox in Y
        ring_o = [(M @ Vector(((rb[0] + 0.015) * math.cos(2 * math.pi * k / nb), (rb[1] + 0.015) *
                                math.sin(2 * math.pi * k / nb), 0.0))) for k in range(nb)]
        ring_i = [(M @ Vector((rb[0] * math.cos(2 * math.pi * k / nb), rb[1] * math.sin(2 * math.pi * k / nb), 0.012)))
                  for k in range(nb)]
        for k in range(nb):
            k1 = (k + 1) % nb
            g.quad([tuple(ring_o[k]), tuple(ring_o[k1]), tuple(ring_i[k1]), tuple(ring_i[k])], "GRAFITE",
                   out=tuple(M.to_3x3() @ Vector((0, 0, 1))))
    # fascia in rilievo con lo stemma (sul fianco dritto del fronte)
    bw, z0, z1 = 0.075, 0.08, C_DOME - 0.02
    yf = -CD
    g.box(-bw, bw, yf - 0.012, yf + 0.01, z0, z1, "GRAFITE", faces=("xn", "xp", "top", "bot"))
    g.quad([(-bw, yf - 0.012, z0), (bw, yf - 0.012, z0), (bw, yf - 0.012, z1), (-bw, yf - 0.012, z1)], "CEST_BANDA",
           out=(0, -1, 0))
    # targhetta bianca a destra della bocca (vista dal fronte: +X a destra)
    if lod < 2:
        ph2 = math.asin(min((C_DOME + 0.05 - C_DOME) / (CH - C_DOME), 1))
        yt = -CD * math.cos(ph2) ** 0.6 - 0.006
        g.quad([(0.12, yt, C_DOME - 0.02), (0.18, yt, C_DOME - 0.02), (0.18, yt, C_DOME + 0.04), (0.12, yt, C_DOME + 0.04)],
               "CEST_TARGHETTA", out=(0, -1, 0))
    return _fin(g, name, lod, coll, smooth=50.0)


def ucx_cestino(coll, name="SM_Morin_Cestino_v2"):
    pk._ucx(name, [(-CW, CW, -CD, CD, 0.0, C_DOME), (-CW * 0.8, CW * 0.8, -CD * 0.8, CD * 0.8, C_DOME, CH)], coll)


# =================================================================================================================
# cartelli d'inizio passeggiata e new jersey in plastica
# =================================================================================================================
def build_palo_cartelli(coll, lod=0, name="SM_Morin_PaloCartelli"):
    """Palo zincato 3,2 m; targa a bandiera 'banchina G. Thaon di Revel' a 3,0 m; pannello 0,6 x 0,9 con la testata
    'banchina Costantino Morin', l'avviso dei bambini e la targhetta gialla. Fronte dei pannelli verso -Y locale."""
    g = G()
    sides = (8, 4, 4)[lod]
    g.tube([(0, 0, 0), (0, 0, 3.2)], 0.03, sides, "ZINCO")
    _lathe(g, [(0.0, 3.19), (0.032, 3.19), (0.0, 3.23)], sides, "NERO")
    # targa a bandiera: dal palo verso +X
    M = Matrix.Translation((0.48, 0.0, 2.88))
    _panel(g, M, 0.9, 0.225, "TARGA_THAON", "TARGA_THAON", "BIANCO", 0.02)
    # pannello principale davanti al palo, con fascette
    yp = -0.045
    for z0, h, cell in ((2.62, 0.15, "TARGA_MORIN"), (1.72, 0.90, "PANN_BIMBI"), (1.55, 0.15, "TARGHETTA")):
        _panel(g, Matrix.Translation((0, yp, 0)), 0.6, h, cell, "ZINCO", "ZINCO", 0.012, z0)
    if lod < 2:
        for z in (1.85, 2.45, 2.70):
            g.box(-0.04, 0.04, yp + 0.006, 0.0, z, z + 0.03, "ZINCO")
    return _fin(g, name, lod, coll)


def ucx_palo(coll, name="SM_Morin_PaloCartelli"):
    pk._ucx(name, [(-0.04, 0.04, -0.04, 0.04, 0.0, 3.2), (-0.30, 0.30, -0.06, 0.0, 1.55, 2.77)], coll)


NJ = (0.60, 0.225, 0.75)


def _nj_prof():
    """Profilo trasversale (y, z) della barriera in plastica, dal piede lato -Y in senso antiorario."""
    return [(-0.225, 0.0), (-0.225, 0.10), (-0.17, 0.20), (-0.11, 0.55), (-0.10, 0.70), (-0.06, 0.75), (0.06, 0.75),
            (0.10, 0.70), (0.11, 0.55), (0.17, 0.20), (0.225, 0.10), (0.225, 0.0)]


def build_nj(coll, lod=0, colore="Blu"):
    name = f"SM_Morin_NJPlastica_{colore}"
    cell = "NJ_BLU" if colore == "Blu" else "NJ_BIANCO"
    g = G()
    hx = NJ[0]
    prof = _nj_prof()
    if lod == 2:
        prof = [prof[i] for i in (0, 2, 4, 5, 6, 7, 9, 11)]
    # fianchi e dorso
    for (ya, za), (yb, zb) in zip(prof[:-1], prof[1:]):
        out = (0, (ya + yb), 1.0 if za + zb > 1.3 else 0.0)
        g.quad([(-hx + 0.03, ya, za), (hx - 0.03, ya, za), (hx - 0.03, yb, zb), (-hx + 0.03, yb, zb)], cell, out=out)
    # testate leggermente bombate (incastri maschio/femmina semplificati)
    for sx in (-1, 1):
        x = sx * hx
        xi = sx * (hx - 0.03)

        def fn(bm, x=x):
            return bm.faces.new([bm.verts.new((x, y * 0.9, z * 0.97 + 0.01)) for y, z in prof])
        g.new_faces(fn, cell)
        for (ya, za), (yb, zb) in zip(prof[:-1], prof[1:]):
            g.quad([(xi, ya, za), (x, ya * 0.9, za * 0.97 + 0.01), (x, yb * 0.9, zb * 0.97 + 0.01), (xi, yb, zb)], cell,
                   out=(sx, ya + yb, 0.3))
    o = _fin(g, name, lod, coll)
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for f in bm.faces:
        f.normal_update()
        c = f.calc_center_median()
        if abs(c.x) > hx - 0.031 and abs(f.normal.x) > 0.7 and f.normal.x * c.x < 0:
            f.normal_flip()
    bm.to_mesh(me)
    bm.free()
    if lod < 2:
        pass
    return o


def ucx_nj(coll, colore):
    pk._ucx(f"SM_Morin_NJPlastica_{colore}", [(-NJ[0], NJ[0], -0.225, 0.225, 0.0, 0.20),
                                               (-NJ[0], NJ[0], -0.13, 0.13, 0.20, 0.75)], coll)


# =================================================================================================================
# la Sirena del Golfo dei Poeti (opera pubblica di Aidyn Zeinalov, forma ricreata stilizzata)
# =================================================================================================================
BAS = (0.70, 0.50, 0.75)       # semilunghezza (lungo lo sguardo, +X), semilarghezza, altezza
ZP = BAS[2] + 0.03             # sopra la lastra di bronzo


def build_sirena(coll, lod=0, name="SM_Molo_Sirena"):
    g = G()
    bx, by, bz = BAS
    g.box(-bx, bx, -by, by, 0.0, bz, "GRANITO", faces=("top",))
    for (pts, cell, out) in (
            ([(-bx, -by, 0), (bx, -by, 0), (bx, -by, bz), (-bx, -by, bz)], "BASAM_FR", (0, -1, 0)),
            ([(bx, by, 0), (-bx, by, 0), (-bx, by, bz), (bx, by, bz)], "BASAM_FR", (0, 1, 0)),
            ([(bx, -by, 0), (bx, by, 0), (bx, by, bz), (bx, -by, bz)], "BASAM_LAT", (1, 0, 0)),
            ([(-bx, by, 0), (-bx, -by, 0), (-bx, -by, bz), (-bx, by, bz)], "BASAM_LAT", (-1, 0, 0))):
        g.quad(pts, cell, out=out)
    # lastra di bronzo con rilievo (sabbia e rete)
    g.box(-bx + 0.06, bx - 0.06, -by + 0.06, by - 0.06, bz, ZP, "BRONZO", faces=("xn", "xp", "yn", "yp"))
    g.box(-bx + 0.06, bx - 0.06, -by + 0.06, by - 0.06, bz, ZP, "BRONZO_RIL", faces=("top",))
    # targa sul fianco verso la citta' (-Y locale)
    g.quad([(-0.225, -by - 0.006, 0.30), (0.225, -by - 0.006, 0.30), (0.225, -by - 0.006, 0.60), (-0.225, -by - 0.006, 0.60)],
           "SIRENA_TARGA", out=(0, -1, 0))
    if lod < 2:
        g.box(-0.235, 0.235, -by - 0.005, -by, 0.29, 0.61, "BRONZO", faces=("xn", "xp", "top", "bot"))
    # sedia
    sc = (-0.20, 0.0)
    s = 0.21
    zs = ZP + 0.45
    sides = (6, 4, 4)[lod]
    g.box(sc[0] - s, sc[0] + s, -s, s, zs - 0.035, zs, "BRONZO")
    for x in (sc[0] - s + 0.02, sc[0] + s - 0.02):
        for y in (-s + 0.02, s - 0.02):
            top = zs + 0.52 if x < sc[0] else zs - 0.035
            g.box(x - 0.018, x + 0.018, y - 0.018, y + 0.018, ZP, top, "BRONZO",
                  faces=("xn", "xp", "yn", "yp", "top"))
    xb = sc[0] - s + 0.02
    for z in ((zs + 0.22, zs + 0.36, zs + 0.48) if lod < 2 else (zs + 0.36,)):
        g.box(xb - 0.012, xb + 0.012, -s, s, z, z + 0.06, "BRONZO")
    if lod < 2:
        g.box(sc[0] - s + 0.03, sc[0] + s - 0.03, -s + 0.02, s - 0.02, ZP + 0.15, ZP + 0.17, "BRONZO")   # traverse
    # figura seduta: bacino, busto inclinato in avanti, testa china, braccia sulle ginocchia, pinne ai piedi
    sd = (10, 6, 4)[lod]
    hip = Vector((sc[0] - 0.02, 0, zs + 0.10))
    _loft(g, [hip + Vector((-0.02, 0, -0.06)), hip, hip + Vector((0.05, 0, 0.18)), hip + Vector((0.10, 0, 0.36)),
              hip + Vector((0.14, 0, 0.47))],
          [(0.12, 0.17), (0.13, 0.17), (0.10, 0.13), (0.12, 0.16), (0.09, 0.15)], "BRONZO", sd, up=(0, 1, 0))
    sh = hip + Vector((0.14, 0, 0.47))
    neck = sh + Vector((0.04, 0, 0.08))
    _loft(g, [sh + Vector((0, 0, 0.02)), neck], [(0.045, 0.045), (0.04, 0.04)], "BRONZO", max(sd - 4, 4), cap0=False)
    _blob(g, tuple(neck + Vector((0.06, 0, 0.09))), (0.105, 0.085, 0.115), "BRONZO", 0, (12, 8, 6)[lod], (7, 5, 4)[lod])
    if lod < 2:   # chignon
        _blob(g, tuple(neck + Vector((-0.02, 0, 0.17))), (0.05, 0.05, 0.045), "BRONZO", 0, 8, 4)
    for sy in (-1, 1):
        k_ = Vector((0.24, sy * 0.10, zs + 0.10))
        a_ = Vector((0.30, sy * 0.10, ZP + 0.10))
        h_ = hip + Vector((0.02, sy * 0.09, 0.0))
        _loft(g, [h_, (h_ + k_) / 2, k_], [(0.075, 0.075), (0.068, 0.068), (0.052, 0.052)], "BRONZO", sd)
        _loft(g, [k_, (k_ + a_) / 2 + Vector((-0.01, 0, 0)), a_], [(0.052, 0.052), (0.048, 0.048), (0.032, 0.032)], "BRONZO",
              sd)
        # pinna: lama piatta e larga dal tallone in avanti, appoggiata sulla lastra
        fin = [(0.24, sy * 0.10 - 0.05), (0.62, sy * 0.10 - 0.09 + sy * 0.03), (0.66, sy * 0.10 + sy * 0.03),
               (0.62, sy * 0.10 + 0.09 + sy * 0.03), (0.24, sy * 0.10 + 0.05)]
        g.prism(fin, ZP + 0.005, ZP + 0.035, "BRONZO_LUCE", top=True, bot=False)
        _loft(g, [a_ + Vector((-0.04, 0, -0.03)), a_ + Vector((0.08, 0, -0.07))], [(0.045, 0.035), (0.05, 0.03)], "BRONZO",
              max(sd - 2, 4))
        # braccia: spalla -> gomito -> mano sul ginocchio
        s_ = sh + Vector((0.0, sy * 0.15, -0.03))
        e_ = Vector((0.14, sy * 0.21, zs + 0.30))
        w_ = k_ + Vector((-0.02, sy * 0.02, 0.07))
        _loft(g, [s_, e_, w_], [(0.045, 0.045), (0.036, 0.036), (0.03, 0.03)], "BRONZO", max(sd - 2, 4))
        if lod < 2:
            _blob(g, tuple(w_ + Vector((0.02, 0, -0.02))), (0.05, 0.035, 0.025), "BRONZO", 0, 6, 3)
    return _fin(g, name, lod, coll, smooth=55.0)


def ucx_sirena(coll, name="SM_Molo_Sirena"):
    bx, by, bz = BAS
    pk._ucx(name, [(-bx, bx, -by, by, 0.0, ZP), (-0.42, 0.40, -0.26, 0.26, ZP, ZP + 0.62),
                   (-0.30, 0.20, -0.24, 0.24, ZP + 0.62, ZP + 1.40)], coll)


# =================================================================================================================
# pescherecci (origine alla linea di galleggiamento, prua verso +X, lato d'ormeggio con i copertoni +Y)
# =================================================================================================================
BARCHE = {
    #     L,    B,   puntale libero, pescaggio, fascia, nome, timoniera (x0, x1, semilargh., h), tipo
    "A": dict(L=14.0, B=4.6, fb=1.25, dr=1.3, fascia="FASCIA_AZZ", nome="NOME_A", tim=(0.2, 3.0, 1.15, 2.2), tipo="A",
              name="SM_Molo_Peschereccio14"),
    "B": dict(L=11.0, B=4.0, fb=1.10, dr=1.1, fascia="FASCIA_VERDE", nome="NOME_B", tim=(-0.6, 1.6, 0.95, 1.9), tipo="B",
              name="SM_Molo_Peschereccio11"),
    "C": dict(L=8.5, B=2.8, fb=0.85, dr=0.8, fascia="FASCIA_AZZ", nome="NOME_C", tim=(-0.3, 1.3, 0.70, 1.15), tipo="C",
              name="SM_Molo_GozzoTuga"),
}


def _hb(t, B, tw):
    """Semilarghezza in coperta alla stazione t (0 poppa, 1 prua)."""
    if t < 0.45:
        return B / 2 * (tw + (1 - tw) * math.sin(math.pi / 2 * t / 0.45))
    return max(B / 2 * math.cos((t - 0.45) / 0.55 * math.pi / 2) ** 0.75, 0.025)


def _hull_section(t, P):
    L, B, fb, dr = P["L"], P["B"], P["fb"], P["dr"]
    tw = 0.35 if P["tipo"] == "C" else 0.80
    hb = _hb(t, B, tw)
    zs = fb + 0.35 * (2 * t - 1) ** 2 + (0.25 * max(t - 0.7, 0) / 0.3)        # cavallino: piu' alto a prua
    zk = -dr + (dr + 0.35) * max(t - 0.82, 0) / 0.18 * (t > 0.82)              # dritto di prua
    zk = min(zk, zs - 0.2)
    if P["tipo"] == "C" and t < 0.12:                                          # poppa del gozzo: anche lei stellata
        zk = -dr + (dr - 0.1) * (0.12 - t) / 0.12
    fl = 1.0 + 0.04 * max(t - 0.5, 0)
    # (y, z, cella) dal chiglia verso la falchetta
    return [(0.0, zk, "ANTIVEG"), (hb * 0.45, zk + 0.10, "ANTIVEG"), (hb * 0.86, zk * 0.45, "ANTIVEG"),
            (hb * 0.97, -0.02, "ANTIVEG"), (hb * 0.98, 0.10, "SCAFO"), (hb * (0.98 + 0.02 * fl), zs - 0.32, "SCAFO"),
            (hb * (0.985 + 0.02 * fl), zs - 0.10, P["fascia"]), (hb * (0.99 + 0.02 * fl), zs, "LEGNO_CHIARO" if
                                                                     P["tipo"] == "C" else "SCAFO")]


def _hull(g, P, lod):
    L = P["L"]
    ns = (16, 11, 7)[lod]
    ts = [k / (ns - 1) for k in range(ns)]
    ts = [t ** 0.9 for t in ts]
    secs = [(t, -L / 2 + t * L, _hull_section(t, P)) for t in ts]
    m = len(secs[0][2])
    if lod == 2:
        keep = [0, 2, 3, 4, 6, 7]
        secs = [(t, x, [s[i] for i in keep]) for t, x, s in secs]
        m = len(keep)
    for side in (1, -1):
        for (t0, x0, s0), (t1, x1, s1) in zip(secs[:-1], secs[1:]):
            for j in range(m - 1):
                a, b = s0[j], s0[j + 1]
                c, d = s1[j], s1[j + 1]
                cell = b[2] if b[2] != "LEGNO_CHIARO" else "SCAFO"
                if a[1] < -0.01 and b[1] <= 0.1:
                    cell = "ANTIVEG"
                g.quad([(x0, side * a[0], a[1]), (x1, side * c[0], c[1]), (x1, side * d[0], d[1]), (x0, side * b[0], b[1])],
                       cell, out=(0, side, 0.0) if b[1] > 0 else (0, side * 0.6, -0.8))
    # specchio di poppa
    t0, x0, s0 = secs[0]
    g.new_faces(lambda bm: bm.faces.new([bm.verts.new((x0, -y, z)) for y, z, _ in s0[::-1]] +
                                        [bm.verts.new((x0, y, z)) for y, z, _ in s0[1:]]), "SCAFO")
    for f in g.bm.faces:
        pass
    return secs


def _deck(g, P, secs, lod):
    """Coperta a quota fissa, impavesata interna e capodibanda."""
    zd = P["fb"] - (0.55 if P["tipo"] != "C" else 0.40)
    th = 0.07
    inner = []
    for t, x, s in secs:
        y_out, z_s = s[-1][0], s[-1][1]
        inner.append((x, max(y_out - th, 0.01), z_s))
    # coperta (fino alla penultima stazione per non uscire dalla prua)
    for (xa, ya, za), (xb, yb, zb) in zip(inner[:-1], inner[1:]):
        g.quad([(xa, -ya, zd), (xb, -yb, zd), (xb, yb, zd), (xa, ya, zd)], "COPERTA", out=(0, 0, 1))
    xs0 = inner[0][0]
    for side in (1, -1):
        for (xa, ya, za), (xb, yb, zb) in zip(inner[:-1], inner[1:]):
            # impavesata interna (guarda verso il centro)
            g.quad([(xa, side * ya, zd), (xb, side * yb, zd), (xb, side * yb, zb), (xa, side * ya, za)], "SCAFO",
                   out=(0, -side, 0))
        # capodibanda: dalla linea interna alla falchetta esterna
        for (ta, xa, sa), (tb, xb, sb), (_, ya, za), (_, yb, zb) in zip(secs[:-1], secs[1:], inner[:-1], inner[1:]):
            g.quad([(xa, side * ya, za), (xb, side * yb, zb), (xb, side * sb[-1][0], sb[-1][1]),
                    (xa, side * sa[-1][0], sa[-1][1])], "LEGNO_CHIARO", out=(0, 0, 1))
    # specchio interno
    ya, za = inner[0][1], inner[0][2]
    g.quad([(xs0 + 0.001, -ya, zd), (xs0 + 0.001, ya, zd), (xs0 + 0.001, ya, za), (xs0 + 0.001, -ya, za)], "SCAFO",
           out=(1, 0, 0))
    return zd


def _chord_quad(g, P, secs, x0, x1, z0, z1, side, cell):
    """Quad piano sulla murata fra x0 e x1, staccato dallo scafo quanto basta (sagitta + 1,5 cm)."""
    def hb_at(x, z):
        t = (x + P["L"] / 2) / P["L"]
        s = _hull_section(t, P)
        ys = [p[0] for p in s if p[1] >= z - 0.4]
        return max(ys) if ys else s[-1][0]
    ya, yb = hb_at(x0, z1), hb_at(x1, z1)
    ym = max(hb_at(x0 + (x1 - x0) * k / 6, z1) - (ya + (yb - ya) * k / 6) for k in range(7))
    off = max(ym, 0) + 0.015
    g.quad([(x0, side * (ya + off), z0), (x1, side * (yb + off), z0), (x1, side * (yb + off), z1),
            (x0, side * (ya + off), z1)], cell, out=(0, side, 0))


def build_barca(coll, lod=0, key="A"):
    P = BARCHE[key]
    name = P["name"]
    g = G()
    L, B, fb = P["L"], P["B"], P["fb"]
    secs = _hull(g, P, lod)
    zd = _deck(g, P, secs, lod)
    sides = (8, 6, 4)[lod]
    # nome sulle due murate a prua e sigla a centro barca
    for side in (1, -1):
        zf = fb + 0.1
        xn0 = L / 2 - 1.2 - 0.18 * L
        _chord_quad(g, P, secs, xn0, xn0 + min(2.0, L * 0.16), zf - 0.47, zf - 0.12, side, P["nome"])
        if lod < 2:
            _chord_quad(g, P, secs, -0.6, 0.4, fb - 0.75, fb - 0.42, side, "SIGLA")
    # timoniera / tuga
    tx0, tx1, tw, th = P["tim"]
    zt = zd + th
    g.box(tx0, tx1, -tw, tw, zd, zt, "SCAFO", faces=("xn", "xp", "yn", "yp"))
    g.box(tx0 - 0.08, tx1 + 0.12, -tw - 0.08, tw + 0.08, zt, zt + 0.08, "SCAFO")
    e = 0.006
    wz0, wz1 = zd + th * 0.55, zd + th * 0.88
    g.quad([(tx1 + e, -tw + 0.12, wz0), (tx1 + e, tw - 0.12, wz0), (tx1 + e, tw - 0.12, wz1), (tx1 + e, -tw + 0.12, wz1)],
           "VETRO", out=(1, 0, 0))
    for side in (1, -1):
        y = side * (tw + e)
        g.quad([(tx1 - 0.15, y, wz0), (tx1 - (tx1 - tx0) * 0.55, y, wz0), (tx1 - (tx1 - tx0) * 0.55, y, wz1),
                (tx1 - 0.15, y, wz1)], "VETRO", out=(0, side, 0))
        if P["tipo"] != "C" and lod < 2:   # porta laterale
            g.quad([(tx0 + 0.2, y, zd + 0.05), (tx0 + 0.85, y, zd + 0.05), (tx0 + 0.85, y, zd + th * 0.88),
                    (tx0 + 0.2, y, zd + th * 0.88)], "VETRO" if side > 0 else "ACCIAIO_SCURO", out=(0, side, 0))
    g.quad([(tx0 - e, tw - 0.15, wz0), (tx0 - e, -tw + 0.15, wz0), (tx0 - e, -tw + 0.15, wz1), (tx0 - e, tw - 0.15, wz1)],
           "VETRO", out=(-1, 0, 0))
    # albero con luci e radar
    if P["tipo"] != "C":
        mx = (tx0 + tx1) / 2
        ztop = zt + (2.6 if key == "A" else 1.9)
        g.tube([(mx, 0, zt + 0.08), (mx, 0, ztop)], 0.05, sides, "BIANCO_PALO")
        g.box(mx - 0.45, mx + 0.45, -0.06, 0.06, ztop - 0.75, ztop - 0.68, "BIANCO_PALO")
        g.box(mx - 0.35, mx + 0.35, -0.12, 0.12, zt + 0.08, zt + 0.22, "BIANCO")          # radar
        g.box(mx - 0.06, mx + 0.06, -0.06, 0.06, ztop, ztop + 0.12, "ARANCIO")
        if lod < 2:
            for sy in (-1, 1):
                g.box(mx - 0.05, mx + 0.05, sy * 0.45 - 0.04, sy * 0.45 + 0.04, ztop - 0.75, ztop - 0.62,
                      "FASCIA_VERDE" if sy > 0 else "ROSSO")
    else:
        g.tube([(tx0 + 0.3, 0, zt + 0.08), (tx0 + 0.3, 0, zt + 1.2)], 0.025, sides, "BIANCO_PALO")
    # portale a A di poppa (A), salpareti, reti, cassette, galleggianti
    xs = -L / 2
    if P["tipo"] == "A":
        top = Vector((xs + 1.1, 0, fb + 3.6))
        for sy in (-1, 1):
            g.tube([(xs + 0.7, sy * (B / 2 - 0.45), zd), tuple(top + Vector((0, sy * 0.35, 0)))], 0.07, sides, "SCAFO")
        g.tube([(xs + 1.1, -0.45, top.z), (xs + 1.1, 0.45, top.z)], 0.08, sides, "SCAFO")
        if lod < 2:
            g.tube([tuple(top), (xs + 0.2, 0, zd + 0.8)], 0.012, 3, "CORDA")
            g.box(xs + 1.0, xs + 1.2, -0.08, 0.08, top.z - 0.35, top.z - 0.08, "ACCIAIO_SCURO")
    drum_x = (xs + 2.6) if P["tipo"] == "A" else (tx1 + 0.9)
    dr_r, dr_w = (0.45, 1.0) if P["tipo"] != "C" else (0.22, 0.5)
    Md = Matrix.Translation((drum_x, 0, zd + dr_r + 0.25)) @ Matrix.Rotation(math.radians(90), 4, "X")
    nd_ = (12, 8, 6)[lod]
    _lathe(g, [(0.0, -dr_w / 2 + 0.04), (dr_r, -dr_w / 2 + 0.04), (dr_r, dr_w / 2 - 0.04)], nd_, "RETE", mat=Md)
    for zf in (-dr_w / 2, dr_w / 2 - 0.04):          # flange
        _lathe(g, [(0.0, zf), (dr_r + 0.08, zf), (dr_r + 0.08, zf + 0.04)], nd_, "ACCIAIO_SCURO", mat=Md)
    g.box(drum_x - 0.12, drum_x + 0.12, -dr_w / 2 - 0.06, -dr_w / 2, zd, zd + dr_r + 0.35, "ACCIAIO_SCURO")
    g.box(drum_x - 0.12, drum_x + 0.12, dr_w / 2, dr_w / 2 + 0.06, zd, zd + dr_r + 0.35, "ACCIAIO_SCURO")
    # mucchio di rete a poppa
    rng = np.random.default_rng(ord(key))
    nx = xs + (1.6 if P["tipo"] == "A" else 0.9)
    if P["tipo"] != "A":
        nx = xs + L * 0.18
    rw = min(B / 2 - 0.4, 1.2)
    pts = [(nx + rng.uniform(-0.7, 0.7) * (L / 14), rng.uniform(-rw, rw), zd + rng.uniform(0.0, 0.55))
           for _ in range(18)] + [(nx + dx, dy, zd) for dx in (-0.8 * L / 14, 0.8 * L / 14) for dy in (-rw, rw)]
    g.hull(pts, "RETE")
    # cassette impilate
    cx0 = tx1 + 0.4 if P["tipo"] == "A" else nx + 1.2
    for i in range((5, 3, 2)[lod]):
        cx = cx0 + 0.65 * (i % 2)
        cz = zd + 0.3 * (i // 2)
        cy = (-0.7 if P["tipo"] != "C" else -0.45)
        g.box(cx - 0.3, cx + 0.3, cy - 0.2, cy + 0.2, cz, cz + 0.28, "CASSETTA_BLU" if i % 3 else "BIANCO")
    if lod < 2:
        for i in range(4 if P["tipo"] != "C" else 2):
            p = (nx + 0.3 * i - 0.4, rw * 0.3 * (1 if i % 2 else -1), zd + 0.62)
            pk_s = (6, 4)[lod]
            _blob(g, p, (0.12, 0.12, 0.12), "ARANCIO", 0, pk_s, 3)
    # copertoni sul lato d'ormeggio (+Y)
    if True:
        for k in range(4 if P["tipo"] != "C" else 3):
            x = -L / 2 + L * (0.2 + 0.2 * k)
            t = (x + L / 2) / L
            y = _hull_section(t, P)[-3][0] + 0.12
            M = Matrix.Translation((x, y, fb - 0.45)) @ Matrix.Rotation(math.radians(90), 4, "X")
            if lod < 2:
                g.torus(M, 0.25, 0.10, (10, 8)[lod], (6, 4)[lod], "GOMMA")
            else:
                g.box(x - 0.3, x + 0.3, y - 0.1, y + 0.1, fb - 0.75, fb - 0.15, "GOMMA")
            g.tube([(x, y, fb - 0.2), (x, y - 0.12, fb + 0.05)], 0.01, 3, "CORDA")
    return _fin(g, name, lod, coll)


# =================================================================================================================
# pontiletto lungo il ciglio est del molo (OSM way 1382978940), calpestabile, in coordinate mondo
# =================================================================================================================
PT_W, PT_Z, PT_T = 1.8, -0.35, 0.20


def x_ciglio(y):
    return 6.8 + (y + 79.3) * (3.4 / 150.6)


def build_pontiletto(coll, lod=0, tratto="Nord"):
    y0, y1 = (0.0, 35.0) if tratto == "Nord" else (-77.8, 0.0)
    name = f"SM_Molo_Pontiletto_{tratto}"
    g = G()
    xi0, xi1 = x_ciglio(y0) + 0.05, x_ciglio(y1) + 0.05
    xo0, xo1 = xi0 + PT_W, xi1 + PT_W
    z, zb = PT_Z, PT_Z - PT_T
    g.quad([(xi0, y0, z), (xo0, y0, z), (xo1, y1, z), (xi1, y1, z)], None, W_, out=(0, 0, 1))
    for (xa, xb) in ((xo0, xo1), (xi0, xi1)):
        side = 1 if xa > xi0 + 0.1 else -1
        g.quad([(xa, y0, zb), (xb, y1, zb), (xb, y1, z), (xa, y0, z)], "ACCIAIO_SCURO", out=(side, 0, 0))
    g.quad([(xi0, y0, zb), (xi1, y1, zb), (xo1, y1, zb), (xo0, y0, zb)], "ACCIAIO_SCURO", out=(0, 0, -1))
    for y, xi, xo, o in ((y0, xi0, xo0, -1), (y1, xi1, xo1, 1)):
        g.quad([(xi, y, zb), (xo, y, zb), (xo, y, z), (xi, y, z)], "ACCIAIO_SCURO", out=(0, o, 0))
    # pali in acqua ogni ~5 m sul bordo esterno, bitte basse ogni ~10 m
    n = max(int((y1 - y0) / 5.0), 1)
    step_p = 1 if lod == 0 else (2 if lod == 1 else 4)
    for k in sorted(set(range(0, n + 1, step_p)) | {n}):     # sempre il palo di testa: stessa bbox nei LOD
        y = y0 + (y1 - y0) * k / n
        x = x_ciglio(y) + 0.05 + PT_W - 0.12
        g.tube([(x, y, zb), (x, y, -2.2)], 0.10, (6, 5, 4)[lod], "ACCIAIO_SCURO", cap=False)
        if k % 2 == 0 or k == n:
            _lathe(g, [(0.09, z), (0.07, z + 0.18), (0.10, z + 0.22), (0.0, z + 0.24)], (8, 6, 4)[lod], "NERO",
                   mat=Matrix.Translation((x - 0.15, y, 0)))
    return _fin(g, name, lod, coll)


def ucx_pontiletto(coll, tratto):
    y0, y1 = (0.0, 35.0) if tratto == "Nord" else (-77.8, 0.0)
    xi0, xi1 = x_ciglio(y0) + 0.05, x_ciglio(y1) + 0.05
    pts = [Vector((x, y, z)) for (x, y) in ((xi0, y0), (xi0 + PT_W, y0), (xi1 + PT_W, y1), (xi1, y1))
           for z in (PT_Z - PT_T, PT_Z)]
    pk._ucx_hull(f"SM_Molo_Pontiletto_{tratto}", 0, pts, coll)


# =================================================================================================================
# elenco degli asset, build, verifiche
# =================================================================================================================
def _ins_ucx(name, w, h, t):
    return lambda coll: pk._ucx(name, [(-w / 2, w / 2, 0.0, t, -h / 2, h / 2)], coll)


ASSETS = {
    "SM_Molo_Ombrellone3x3": (lambda c, l: build_ombrellone(c, l, 3.0), lambda c: ucx_ombrellone(c, 3.0)),
    "SM_Molo_Ombrellone4x4": (lambda c, l: build_ombrellone(c, l, 4.0), lambda c: ucx_ombrellone(c, 4.0)),
    "SM_Molo_TavoloNero": (build_tavolo, ucx_tavolo),
    "SM_Molo_SediaNera": (build_sedia, ucx_sedia),
    "SM_Molo_FiorieraAntracite": (build_fioriera, ucx_fioriera),
    "SM_Molo_Lavagna": (build_lavagna, lambda c: ucx_aframe(c, "SM_Molo_Lavagna", 1.08)),
    "SM_Molo_CavallettoPescheria": (build_cavalletto, lambda c: ucx_aframe(c, "SM_Molo_CavallettoPescheria", 1.10)),
    "SM_Molo_Insegna_PescatoriPigri": (build_insegna_scudo, _ins_ucx("SM_Molo_Insegna_PescatoriPigri", 1.0, 1.2, 0.04)),
    "SM_Molo_Insegna_RetiBucate": (build_insegna_pannello, _ins_ucx("SM_Molo_Insegna_RetiBucate", 1.3, 0.38, 0.03)),
    "SM_Morin_Cestino_v2": (build_cestino, ucx_cestino),
    "SM_Morin_PaloCartelli": (build_palo_cartelli, ucx_palo),
    "SM_Morin_NJPlastica_Blu": (lambda c, l: build_nj(c, l, "Blu"), lambda c: ucx_nj(c, "Blu")),
    "SM_Morin_NJPlastica_Bianca": (lambda c, l: build_nj(c, l, "Bianca"), lambda c: ucx_nj(c, "Bianca")),
    "SM_Molo_Sirena": (build_sirena, ucx_sirena),
    "SM_Molo_Peschereccio14": (lambda c, l: build_barca(c, l, "A"), None),
    "SM_Molo_Peschereccio11": (lambda c, l: build_barca(c, l, "B"), None),
    "SM_Molo_GozzoTuga": (lambda c, l: build_barca(c, l, "C"), None),
    "SM_Molo_Pontiletto_Nord": (lambda c, l: build_pontiletto(c, l, "Nord"), lambda c: ucx_pontiletto(c, "Nord")),
    "SM_Molo_Pontiletto_Sud": (lambda c, l: build_pontiletto(c, l, "Sud"), lambda c: ucx_pontiletto(c, "Sud")),
}
BUDGET = {"SM_Molo_Peschereccio14": 6000, "SM_Molo_Peschereccio11": 4000, "SM_Molo_GozzoTuga": 2000,
          "SM_Morin_Cestino_v2": 600, "SM_Molo_Sirena": 4000}
ZMIN = {"SM_Molo_Peschereccio14": 0.05, "SM_Molo_Peschereccio11": 0.05, "SM_Molo_GozzoTuga": 0.05,
        "SM_Molo_Pontiletto_Nord": -0.6, "SM_Molo_Pontiletto_Sud": -0.6}


def build_all(only=None, lod_target=(1.0, 0.5, 0.15)):
    coll = pk._coll(KIT)
    rep = {}
    for nm, (bld, ucx) in ASSETS.items():
        if only and nm not in only:
            continue
        for o in [o for o in coll.objects if o.name.startswith(f"UCX_{nm}_")]:
            bpy.data.objects.remove(o)
        o0 = bld(coll, 0)
        t0 = pk.tri_count(o0)
        objs = [o0]
        for lod in (1, 2):
            o = bld(coll, lod)
            t = pk.tri_count(o)
            want = t0 * lod_target[lod]
            if t > want * 1.25 and t0 >= 300:      # sotto i 300 tri il LOD ricostruito basta (la decimazione deforma)
                ratio = max(0.05, want / t)
                o = mi._decimate(o, ratio, o.name, coll)
                while av.bbox_dev(o0, o) > 0.019 and ratio < 0.95:
                    o = bld(coll, lod)
                    ratio = min(ratio * 1.3, 0.95)
                    o = mi._decimate(o, ratio, o.name, coll)
            objs.append(o)
        if ucx:
            ucx(coll)
        lo, hi = av.vbox(o0)
        rep[nm] = [pk.tri_count(o) for o in objs] + [tuple(round(d, 2) for d in (hi - lo))]
    for o in coll.objects:
        hide = o.name.startswith("UCX") or "_LOD" in o.name
        o.hide_render = hide
        o.hide_viewport = hide
    return rep


def check_all(only=None):
    res = {}
    for nm in ASSETS:
        if only and nm not in only:
            continue
        o0 = bpy.data.objects[nm]
        devs = [round(av.bbox_dev(o0, bpy.data.objects[f"{nm}_LOD{l}"]) * 100, 2) for l in (1, 2)]
        # arredi appoggiati a terra senza faccia inferiore: bersagli sopra Z 0,02 e raggi dall'alto
        hits, back, bad = av.ray_test(o0, zmin=ZMIN.get(nm, 0.02), skip_mats=("Card",))
        nucx = len([o for o in bpy.data.objects if o.name.startswith(f"UCX_{nm}_")])
        lo, hi = av.vbox(o0)
        res[nm] = dict(tri=[pk.tri_count(bpy.data.objects[nm + _sfx(l)]) for l in range(3)], bbox_dev_pct=devs,
                       ray=(back, hits), bad=len(bad), ucx=nucx, dim=tuple(round(d, 2) for d in (hi - lo)))
    return res


# =================================================================================================================
# posa (coordinate di progetto, rz in gradi Blender), CSV in coordinate UE, contesto
# =================================================================================================================
Z_MOLO = 0.01
# dehors della fila A (scheda §2.4; pali dei 3 x 3 spostati verso la facciata perche' il telo resti entro X ~4,2)
OMBRELLONI = [("4x4", 2.6, 103.7, "A1"), ("3x3", 2.4, 98.6, "A2"), ("3x3", 2.7, 94.5, "A3"), ("3x3", 2.7, 90.0, "A3"),
              ("3x3", 2.7, 85.5, "A3"), ("3x3", 2.7, 81.5, "A3"), ("3x3", 2.85, 76.0, "A3giallo"),
              ("3x3", 2.85, 71.5, "A3giallo")]
FIORIERE = [(2.2, 105.6, "A1"), (1.0, 108.0, "A1"), (3.3, 99.7, "A2"), (3.3, 100.9, "A2"), (3.3, 102.1, "A2"),
            (3.8, 84.0, "A3"), (3.8, 85.2, "A3"), (3.8, 86.4, "A3"), (3.8, 91.8, "A3"), (3.8, 93.0, "A3"), (3.8, 94.2, "A3"),
            (3.8, 69.0, "A3giallo"), (3.8, 73.8, "A3giallo"), (3.8, 78.6, "A3giallo"), (3.8, 63.0, "A4"), (3.8, 66.5, "A4")]
TAVOLI = [(1.3, 104.9, "blr", "A1"), (3.45, 104.6, "lr", "A1"), (2.7, 106.9, "bf", "A1"),
          (1.5, 99.9, "blf", "A2"), (1.5, 101.8, "bfr", "A2"),
          (1.6, 80.7, "blf", "A3"), (1.6, 82.9, "bfr", "A3"), (1.6, 84.7, "blf", "A3"), (1.6, 86.7, "bfr", "A3"),
          (1.6, 88.8, "blfr", "A3"), (1.6, 91.0, "blr", "A3"), (1.6, 93.2, "bf", "A3"), (1.6, 96.6, "blfr", "A3"),
          (2.3, 69.6, "blf", "A3giallo"), (2.3, 72.6, "bfr", "A3giallo"), (2.3, 74.8, "blf", "A3giallo"),
          (2.3, 77.6, "bfr", "A3giallo"), (1.4, 64.8, "blr", "A4")]
CHAIR_OFF = {"b": (-0.55, 0.0, 0.0), "f": (0.55, 0.0, 180.0), "l": (0.0, -0.55, 90.0), "r": (0.0, 0.55, -90.0)}
CESTINI_X = [18.55, 36.55, 72.55, 90.55, 126.55, 144.55, 180.55, 198.55, 234.55]
# insegne (calcolate sul modello di A1/A2: morin_molo._poly_A1A2, A1_CURVE_SEGS, FAC_A; vedi insegne_pose())
INSEGNE = [("SM_Molo_Insegna_PescatoriPigri", "Insegna_PescatoriPigri", 0.162, 104.445, 2.025, -62.9),
           ("SM_Molo_Insegna_RetiBucate", "Insegna_RetiBucate", 0.590, 100.80, 3.15, -90.76)]
BARCHE_POS = [("SM_Molo_Peschereccio14", "Peschereccio_A_MugugnoII", 13.9, 28.0), ("SM_Molo_Peschereccio11",
              "Peschereccio_B_AcciugaFelice", 12.2, 42.0), ("SM_Molo_GozzoTuga", "Gozzo_C_NonCeNe", 13.6, 15.0)]


def insegne_pose():
    """Ricalcola INSEGNE: scudo al centro della regione G_scudo (u 1,35) sull'arco di A1, staccato dalla corda della
    sagitta + 2 cm; pannello sulla facciata rosa di A2 fra la tendina (Z 2,95) e il cornicione (Z 3,35)."""
    import morin_molo as mm
    n = mm.ARC_N
    curve = mm._poly_A1A2(n)[2:2 + n + 1] + [(-7.9, 106.7)]
    L = sum((Vector(b) - Vector(a)).length for a, b in zip(curve[:-1], curve[1:]))
    s = 0.0
    for k, l in mm._fit_segs(mm.A1_CURVE_SEGS, L):
        if k == "G_scudo":
            break
        s += l
    sc = s + 1.35
    a, b = mm._polyline_at(curve, sc - 0.5), mm._polyline_at(curve, sc + 0.5)
    d = (b - a).normalized()
    nrm = Vector((d.y, -d.x))
    dev = max((mm._polyline_at(curve, sc + t) - a).dot(nrm) for t in np.linspace(-0.5, 0.5, 21))
    c = (a + b) / 2 + nrm * (dev + 0.02)
    return c, math.degrees(math.atan2(nrm.y, nrm.x)) - 90.0


def layout():
    rng = np.random.default_rng(20261120)
    rows = []
    for i, (t, x, y, sez) in enumerate(OMBRELLONI):
        rows.append((f"SM_Molo_Ombrellone{t}", f"Ombrellone_{i:02d}", x, y, Z_MOLO, float(rng.uniform(-4, 4)), sez))
    for i, (x, y, sez) in enumerate(FIORIERE):
        rows.append(("SM_Molo_FiorieraAntracite", f"FiorieraA_{i:02d}", x, y, Z_MOLO, 90.0, sez))
    k = 0
    for i, (x, y, pat, sez) in enumerate(TAVOLI):
        rows.append(("SM_Molo_TavoloNero", f"TavoloNero_{i:02d}", x, y, Z_MOLO, float(rng.uniform(-6, 6)), sez))
        for c in pat:
            dx, dy, rz = CHAIR_OFF[c]
            j = rng.uniform(-0.05, 0.05, 2)
            rows.append(("SM_Molo_SediaNera", f"SediaNera_{k:02d}", x + dx + j[0], y + dy + j[1], Z_MOLO,
                         rz + float(rng.uniform(-10, 10)), sez))
            k += 1
    rows.append(("SM_Molo_Lavagna", "Lavagna_00", 5.7, 92.8, Z_MOLO, 55.0, "A3"))
    rows.append(("SM_Molo_CavallettoPescheria", "Cavalletto_RistoLischeria", 5.1, 100.4, Z_MOLO, 45.0, "A2"))
    for a, n, x, y, z, rz in INSEGNE:
        rows.append((a, n, x, y, z, rz, "facciata"))
    for i, x in enumerate(CESTINI_X):
        rows.append(("SM_Morin_Cestino_v2", f"Cestino_v2_{i:02d}", x, 92.1, 0.15, 0.0, f"sostituisce Cestino_{i:02d}"))
    rows.append(("SM_Morin_PaloCartelli", "PaloCartelli_00", 19.2, 81.1, 0.0, -120.0, ""))
    for i, (x, y, rz, c) in enumerate(((20.4, 80.65, 0.0, "Blu"), (21.7, 80.65, 0.0, "Bianca"),
                                        (17.6, 79.3, 45.3, "Blu"), (16.5, 78.2, 45.3, "Bianca"))):
        rows.append((f"SM_Morin_NJPlastica_{c}", f"NJPlastica_{i:02d}", x, y, 0.0, rz, c))
    rows.append(("SM_Molo_Sirena", "Sirena_GolfoPoeti", 13.8, 91.9, 0.15, 170.0, ""))
    for a, n, x, y in BARCHE_POS:
        rows.append((a, n, x, y, -1.0, 90.0, "senza collisione"))
    for t in ("Nord", "Sud"):
        rows.append((f"SM_Molo_Pontiletto_{t}", f"Pontiletto_{t}", 0.0, 0.0, 0.0, 0.0, "vertici in posizione mondo"))
    return rows


def check_layout(rows=None, verbose=True):
    """Ingombri in pianta del dehors: nessuna sovrapposizione, niente oltre X 4,2 (salvo lavagna e cavalletto), facciata."""
    rows = rows or layout()
    fp = {"SM_Molo_TavoloNero": (0.35, 0.35), "SM_Molo_SediaNera": (0.20, 0.20), "SM_Molo_FiorieraAntracite": (0.5, 0.225),
          "SM_Molo_Ombrellone3x3": (0.30, 0.30), "SM_Molo_Ombrellone4x4": (0.40, 0.40)}
    boxes = []
    for a, n, x, y, z, rz, v in rows:
        if a in fp:
            hx, hy = fp[a]
            if abs(math.sin(math.radians(rz))) > 0.7:
                hx, hy = hy, hx
            boxes.append((n, x - hx, x + hx, y - hy, y + hy))
    probs = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[1] < b[2] - 1e-3 and b[1] < a[2] - 1e-3 and a[3] < b[4] - 1e-3 and b[3] < a[4] - 1e-3:
                probs.append(("sovrapposti", a[0], b[0]))
        n, x0, x1, y0, y1 = boxes[i]
        if x1 > 4.2 + 1e-3:
            probs.append(("oltre X 4,2", n, round(x1, 2)))
    objs = [bpy.data.objects.get(k) for k in ("SM_Molo_Edificio_A1A2", "SM_Molo_Edificio_A3", "SM_Molo_Edificio_A4A5")]
    objs = [o for o in objs if o is not None]
    for n, x0, x1, y0, y1 in boxes:
        for yy in (y0, (y0 + y1) / 2, y1):
            for o in objs:
                ok, loc, *_ = o.ray_cast(Vector((x1, yy, 0.5)), Vector((-1, 0, 0)))
                if ok and loc.x > x0 - 0.05:
                    probs.append(("facciata", n, round(loc.x, 2)))
    if verbose:
        print(len(boxes), "ingombri,", len(probs), "problemi", probs[:20])
    return probs


def write_csv(path="exports/dettagli/dettagli_posizioni_v1.csv",
              path_cest="exports/dettagli/dettagli_cestini_sostituzione_v1.csv"):
    os.makedirs(f"{PROJ}/exports/dettagli", exist_ok=True)
    rows = layout()
    lines = ["asset,nome,x,y,z,yaw,pitch,roll,variante"]
    for a, n, x, y, z, rz, v in rows:
        yaw = -rz if rz else 0.0
        lines.append(f"{a},{n},{x * 100:.1f},{-y * 100:.1f},{z * 100:.1f},{yaw:.2f},0.00,0.00,{v}")
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    cl = ["attore_vecchio,asset_vecchio,azione,asset_nuovo,nome_nuovo,x,y,z,yaw,pitch,roll"]
    for i, x in enumerate(CESTINI_X):
        cl.append(f"Cestino_{i:02d},SM_Morin_Cestino,nascondere,SM_Morin_Cestino_v2,Cestino_v2_{i:02d},{x * 100:.1f},-9210.0,"
                  f"15.0,0.00,0.00,0.00")
    with open(f"{PROJ}/{path_cest}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(cl) + "\n")
    return len(lines) - 1, len(cl) - 1


def build_context():
    coll = pk._coll(CTX)
    for o in list(coll.objects):
        bpy.data.objects.remove(o)
    for a, n, x, y, z, rz, v in layout():
        o = bpy.data.objects.new(f"DET_{n}", bpy.data.objects[a].data)
        coll.objects.link(o)
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


# =================================================================================================================
# confronti con le foto (docs/qa/arte_dettagli_*.png): render Cycles su CPU (la vista OpenGL di questa macchina e'
# corrotta, vedi PLAN) affiancato alla foto
# =================================================================================================================
CAMERE = {   # nome: (posizione, punto guardato, FOV orizzontale, foto, larghezza, altezza)
    "dehors": ((9.5, 105.0, 2.5), (3.6, 100.7, 1.9), 90.0, FV + "ristoranti_visti_da_di_fronte_2.png", 1150, 519),
    "sirena": ((14.6, 96.4, 1.75), (13.8, 91.9, 1.15), 58.0, FA + "scultura_donna_con_pinne_su_sedia.png", 496, 459),
    "cestino": ((18.62, 90.95, 0.95), (18.55, 92.1, 0.55), 40.0, FA + "cestino.png", 322, 374),
    "cartelli": ((15.9, 83.6, 1.7), (19.2, 81.1, 2.0), 42.0, FA + "cartelli_inizio_passegiata.png", 358, 618),
    "pescherecci": ((4.0, 50.5, 2.6), (13.0, 26.0, 0.5), 62.0, FA + "scultura_donna_con_pinne_su_sedia.png", 900, 520),
}


def _cam(name, loc, tgt, fov):
    c = bpy.data.objects.get(name)
    if c is None:
        c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        pk._coll("MOLO_Camere").objects.link(c)
    c.location = loc
    d = Vector(tgt) - Vector(loc)
    c.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    c.data.sensor_fit = "HORIZONTAL"
    c.data.angle = math.radians(fov)
    c.data.clip_start = 0.05
    c.data.clip_end = 2000
    return c


def confronti(keys=None, samples=24, scale=1.0):
    sc = bpy.context.scene
    try:
        sc.render.engine = "CYCLES"
    except TypeError:
        pass
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    bpy.data.collections[KIT].hide_render = True
    out = {}
    for k, (loc, tgt, fov, foto, W, H) in CAMERE.items():
        if keys and k not in keys:
            continue
        sc.camera = _cam(f"CAM_Dett_{k}", loc, tgt, fov)
        sc.render.resolution_x, sc.render.resolution_y = int(W * scale), int(H * scale)
        sc.render.resolution_percentage = 100
        tmp = f"{PROJ}/docs/qa/_tmp_render.png"
        sc.render.filepath = tmp
        bpy.ops.render.render(write_still=True)
        r = tp.load(tmp)[..., :3]
        f = tp.load(foto)[..., :3]
        h = max(r.shape[0], 400)
        rs = lambda a: tp.resize(a, int(a.shape[1] * h / a.shape[0]), h)
        r2, f2 = rs(r), rs(f)
        sep = np.ones((h, 8, 3), np.float32)
        img = np.concatenate([f2, sep, r2], 1)
        p = f"{PROJ}/docs/qa/arte_dettagli_{k}.png"
        tp.save(img, p)
        os.remove(tmp)
        out[k] = p
    return out
