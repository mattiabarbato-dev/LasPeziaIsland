"""morin_imbarco_v2.py — imbarco v2 dalle foto dell'utente (2026-11-20): biglietteria, pontile d'imbarco, traghetto.

Scheda: ref/foto_nuove_2026-11-20.md §7 (geo-scout) + decisioni dell'orchestratore 2026-11-20:
  traghetto sul lato EST del pontile, rete e ringhiera a ovest; tavolato ~3 m sull'asse OSM (71,7; 80,3) -> (70,8; 52,0);
  casette ~2,3 x 2,3 m, gronda 2,5, colmo 3,0, su una piattaforma oltre il ciglio, centri (74,4; 78,9) e (69,0; 78,9);
  portale largo 2,4 m alto ~3,5 m; righe da ~18 cm (13 per facciata, misurate in T2).
Foto (catture Street View messe dall'utente in ref/foto/vista/, deroga CLAUDE.md §5, marca [SV] in CREDITS):
  T1 traghetto_bigliettaria_azzurra.png     di tre quarti: casette, rete, tettoia a righe, pontile, traghetto
  T2 biglietteria_traghetto_di_fronte.png   fronte: casette a righe, portale con insegna e schermo, cancello, pontile
Dalle foto: proporzioni, colori campionati, numero di righe, sporco delle righe (fascia bassa della casetta ovest in T2,
raddrizzata e divisa per la mediana di classe), tinta e variazione del tavolato (T2). Testi e loghi ridisegnati; nomi privati in
parodia: compagnia "Navigazione Golfo dei Poetastri" (gabbiano con la penna d'oca), traghetto "Piccione Viaggiatore".
Restano i testi generici/pubblici: "Biglietteria / Ticket Office", "Trasporto di linea via mare / Ferry lines",
"Linea 01 Golfo della Spezia".

Asset (nomi nuovi, sostituiscono i v1 in UEFN):
  SM_Morin_Biglietteria_v2   due casette a righe, portale con insegna ad arco e schermo, cancello con l'onda (anta aperta verso il
                             pontile), pannelli fissi, bacheca, tenda, tettoia a righe, rete a ovest, pennone con bandiera.
  SM_Morin_PontileImbarco_v2 piattaforma a quota banchina (X 67,5-76, Y 77,5-80,2), rampa, tavolato 3 m su travi e pali tubolari,
                             copertoni, 4 bitte di testa, ringhiera a ovest, tavolino e sedia. Calpestabile.
  SM_Morin_Traghetto_v2      28 x 6,6 m, scafo bianco con fascia scura e oblo', due ponti, finestrature, zattere rosse,
                             timoniera con salvagente, albero con radar, nome in parodia. Si sale dal varco di poppa (lato pontile).
Biglietteria e pontile: origine sul ciglio all'asse OSM del pontile (X 71,7), +Y verso la citta'; l'asse del pontile e' inclinato
come in OSM (testa a X 70,8) con un taglio x += K_ASSE * y applicato ai vertici. Si posano nello stesso punto con lo yaw della banchina.
Traghetto: origine al galleggiamento al centro, +X = prua, posa parallela al pontile.

Esegui dentro blender/arte_imbarco.blend:
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_atlas_v2 as av, morin_imbarco_v2 as m2; importlib.reload(av); importlib.reload(m2)
    m2.make_textures(); m2.build_materials(); m2.build_all(); m2.check_all()
    m2.write_csv(); m2.build_context(); m2.export_all()
"""
import math
import os

import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_texphoto as tp
import morin_imbarco as mi
import morin_atlas_v2 as av
from morin_atlas_v2 import Canvas, F_BOLD, F_SANS

PROJ = pk.PROJ
TEXDIR = PROJ + "/blender/textures/imbarco_v2"
FOTO = PROJ + "/ref/foto/vista/"
KIT = "IMBARCO_v2_Kit"
CTX = "IMBARCO_v2_Contesto"
EXPDIR = "//../exports/imbarco"

COMPAGNIA = ("NAVIGAZIONE", "GOLFO dei POETASTRI")
NOME_NAVE = "PICCIONE VIAGGIATORE"

MAT_A, MAT_R, MAT_W, MAT_S, MAT_N = ("M_Morin_Imbarco_v2", "M_Morin_Bigl_Righe", "M_Morin_Pontile_Legno_v2",
                                     "M_Morin_Bigl_Schermo", "M_Morin_Bigl_Rete")
RIGA = 0.18                        # larghezza di una riga (13 righe per facciata, T2)
TILE_R, TILE_W, TILE_N = 6 * RIGA, 2.0, 0.5
MATS = [(MAT_A, "atlas", 0), (MAT_R, "worldabs", TILE_R), (MAT_W, "world", TILE_W), (MAT_S, "fit", 0),
        (MAT_N, "world", TILE_N)]
A_, R_, W_, S_, N_ = range(5)

# colori campionati dalle foto (sRGB, un po' scuriti: albedo). Scheda §7.2: blu #2A91F4, bianco #D9E1E7, zoccolo #79C5EA
BLU_RIGA = (0.15, 0.52, 0.90)
BIANCO_RIGA = (0.84, 0.87, 0.89)
AZZURRO = (0.45, 0.74, 0.89)
BLU_SCURO = (0.07, 0.28, 0.66)
NAVY = (0.06, 0.09, 0.17)

# =================================================================================================================
# atlante
# =================================================================================================================
ATL = av.Atlas("T_Morin_Imbarco_v2", 2048, 128)
CELLS = {
    "BIANCO": ((0.88, 0.89, 0.88), 0.02, 0.35, 0.0), "BIANCO_SPORCO": ((0.78, 0.78, 0.75), 0.04, 0.55, 0.0),
    "BLU_RIGA": (BLU_RIGA, 0.03, 0.40, 0.0), "AZZURRO": (AZZURRO, 0.03, 0.45, 0.0),
    "BLU_SCURO": (BLU_SCURO, 0.03, 0.40, 0.0), "NAVY": (NAVY, 0.03, 0.35, 0.0),
    "VETRO": ((0.10, 0.13, 0.17), 0.02, 0.06, 0.5, "vetro"), "VETRO_INT": ((0.10, 0.09, 0.08), 0.05, 0.70, 0.0, "interno"),
    "ROSSO": ((0.70, 0.09, 0.06), 0.03, 0.40, 0.0), "ANTIVEG": ((0.36, 0.09, 0.07), 0.05, 0.75, 0.0),
    "ACCIAIO": ((0.62, 0.63, 0.64), 0.05, 0.40, 1.0), "GOMMA": ((0.05, 0.05, 0.05), 0.03, 0.88, 0.0, "battistrada"),
    "RUGGINE": ((0.40, 0.27, 0.18), 0.10, 0.85, 0.3, "ruggine"), "GHISA": ((0.11, 0.10, 0.10), 0.05, 0.60, 0.4, "ruggine"),
    "LEGNO_BANCO": ((0.55, 0.33, 0.21), 0.05, 0.60, 0.0, "venatura"),
    "TETTO": ((0.50, 0.58, 0.67), 0.05, 0.50, 0.5, "ondulato"),      # lamiera grigio-azzurra #889CB4 (scheda §7.2)
    "PONTE_GRIGIO": ((0.47, 0.50, 0.49), 0.04, 0.80, 0.0), "TEAK": ((0.45, 0.29, 0.16), 0.06, 0.60, 0.0, "venatura"),
    "GRIGIO": ((0.40, 0.41, 0.42), 0.04, 0.60, 0.0), "PIASTRA": ((0.52, 0.53, 0.54), 0.05, 0.50, 0.9, "mandorlato"),
    "SCURO": ((0.13, 0.13, 0.14), 0.03, 0.50, 0.2), "LETTERE": ((0.93, 0.93, 0.93), 0.01, 0.40, 0.0),
    "SEDIA": ((0.86, 0.86, 0.84), 0.02, 0.45, 0.0), "SCOSSALINA": ((0.33, 0.24, 0.18), 0.04, 0.6, 0.2),
    "CORDA": ((0.80, 0.77, 0.68), 0.06, 0.90, 0.0), "TELAIO_BIANCO": ((0.86, 0.87, 0.86), 0.03, 0.35, 0.3),
    "LEGNO_GRIGIO": ((0.36, 0.35, 0.35), 0.06, 0.80, 0.0, "venatura"), "AZZURRO_INT": ((0.36, 0.58, 0.70), 0.03, 0.6, 0.0),
    "LUCE": ((0.95, 0.95, 0.85), 0.01, 0.2, 0.0), "TAVOLO": ((0.50, 0.27, 0.17), 0.05, 0.6, 0.0, "venatura"),
    "ZINCATO": ((0.58, 0.60, 0.60), 0.06, 0.45, 0.9), "OBLO": ((0.12, 0.15, 0.19), 0.02, 0.08, 0.5, "vetro"),
}
for i, k in enumerate(CELLS):
    ATL.add(k, i % 16, i // 16)
ATL.add("INSEGNA_F", 0, 2, 16, 6)      # 2048 x 768: fronte dell'insegna 2,5 x 1,1 m
ATL.add("INSEGNA_R", 0, 8, 8, 3)       # retro
ATL.add("ZOCCOLO_T", 8, 8, 8, 3)       # zoccolo grafico della casetta est (sportello)
ATL.add("FIANCO", 0, 11, 4, 5)         # fianco verso il camminamento
ATL.add("BACHECA_P", 4, 11, 6, 3)      # pannelli azzurri della casetta ovest
ATL.add("ZOCCOLO_B", 10, 11, 6, 2)     # zoccolo della casetta ovest
ATL.add("ORARI", 10, 13, 2, 2)         # contenuto della bacheca
ATL.add("BANDIERA", 12, 13, 3, 2)      # bandiera della compagnia (parodia)
ATL.add("CARTELLO", 4, 14, 4, 2)       # "BIGLIETTI / TICKETS"
ATL.add("TENDA", 8, 14, 2, 2)          # tenda a righe blu-bianche (13 righe sulla faccia)
ATL.add("TRICOL", 15, 13, 1, 1)        # bandiera italiana (pubblica) sull'albero del traghetto
ATL.add("SALVAG", 15, 14, 1, 1)        # salvagente bianco-rosso


def _cv(W, H, x0, x1, y0, y1, bg, rough=0.45):
    ppm = max(W / (x1 - x0), H / (y1 - y0))
    return Canvas(x0, x1, y0, y1, ppm, bg, rough)


def logo_poetastri(cv, cx, cy, s, col=BLU_SCURO, ring=True):
    """Logo in parodia: gabbiano con la penna d'oca su un timone stilizzato. s = semi-altezza."""
    if ring:
        for k in range(8):
            a = k * math.pi / 4
            cv.line([(cx + 0.55 * s * math.cos(a), cy + 0.55 * s * math.sin(a)),
                     (cx + 0.95 * s * math.cos(a), cy + 0.95 * s * math.sin(a))], 0.09 * s, col)
        cv.circle(cx, cy, 0.62 * s, col, r_in=0.50 * s)
    cv.ellipse(cx - 0.05 * s, cy - 0.05 * s, 0.48 * s, 0.24 * s, col, rot=0.15)            # corpo
    cv.poly([(cx - 0.45 * s, cy - 0.08 * s), (cx - 0.82 * s, cy - 0.18 * s), (cx - 0.78 * s, cy + 0.02 * s)], col)
    cv.circle(cx + 0.36 * s, cy + 0.20 * s, 0.15 * s, col)                                  # testa
    cv.poly([(cx + 0.49 * s, cy + 0.22 * s), (cx + 0.72 * s, cy + 0.17 * s), (cx + 0.49 * s, cy + 0.13 * s)],
            (0.95, 0.70, 0.15))                                                               # becco
    cv.circle(cx + 0.39 * s, cy + 0.24 * s, 0.03 * s, (1, 1, 1))
    cv.poly([(cx - 0.30 * s, cy + 0.05 * s), (cx + 0.10 * s, cy + 0.05 * s), (cx - 0.45 * s, cy + 0.62 * s)], col)  # ala
    cv.line([(cx + 0.62 * s, cy + 0.15 * s), (cx + 0.95 * s, cy + 0.75 * s)], 0.035 * s, col)                     # penna d'oca
    cv.ellipse(cx + 0.86 * s, cy + 0.58 * s, 0.07 * s, 0.22 * s, col, rot=-0.5)


def swoosh(cv, pts_lo, pts_hi, seed, col=(0.96, 0.97, 0.98)):
    """Pennellata bianca diagonale con bordo sfrangiato (come la grafica delle foto)."""
    rng = np.random.default_rng(seed)

    def jag(pts):
        out = []
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
            for t in np.linspace(0, 1, 14, endpoint=False):
                out.append((xa + (xb - xa) * t + rng.normal(0, 0.010), ya + (yb - ya) * t + rng.normal(0, 0.010)))
        out.append(pts[-1])
        return out
    cv.poly(jag(pts_lo) + jag(pts_hi)[::-1], col)


def linea01(cv, x0, x1, ytop, k=1.0, col=(1, 1, 1), sub=True, align="RIGHT"):
    """'LINEA 01 / GOLFO della / SPEZIA / LINE 01 GULF OF LA SPEZIA': descrizione della linea (scheda §9: si tiene)."""
    h = 0.13 * k
    cv.text("LINEA 01", x0, ytop - h, x1, ytop, col, align=align, font=F_BOLD)
    cv.text("GOLFO della", x0, ytop - 2.05 * h, x1, ytop - 1.05 * h, col, align=align, font=F_BOLD)
    cv.text("SPEZIA", x0, ytop - 3.1 * h, x1, ytop - 2.1 * h, col, align=align, font=F_BOLD)
    if sub:
        cv.text("LINE 01", x0, ytop - 3.8 * h, x1, ytop - 3.25 * h, col, align=align, font=F_SANS)
        cv.text("GULF OF LA SPEZIA", x0, ytop - 4.4 * h, x1, ytop - 3.85 * h, col, align=align, font=F_BOLD)


def marchio(cv, cx, cy, s, col=BLU_SCURO):
    logo_poetastri(cv, cx, cy + 0.95 * s, 0.75 * s, col)
    cv.text(COMPAGNIA[0], cx - 2.2 * s, cy - 0.05 * s, cx + 2.2 * s, cy + 0.25 * s, col, font=F_SANS)
    cv.text(COMPAGNIA[1], cx - 2.6 * s, cy - 0.55 * s, cx + 2.6 * s, cy - 0.05 * s, col, font=F_BOLD)


SIGN_X, SIGN_Z0, SIGN_Z1, SIGN_ZT = 1.25, 2.45, 3.30, 3.55     # semilarghezza, base, spalla dell'arco, colmo
Z_HDR = 3.19                                                   # inizio della fascia blu
SCR = (-0.57, 0.45, 2.51, 3.16)                                # schermo (coordinate di vista: x verso destra)


def _arc_z(x):
    c, s = SIGN_X, SIGN_ZT - SIGN_Z1
    R = (c * c + s * s) / (2 * s)
    return SIGN_ZT - R + math.sqrt(max(R * R - x * x, 0.0))


def p_insegna_f(W, H):
    cv = _cv(W, H, -SIGN_X, SIGN_X, SIGN_Z0, SIGN_ZT, AZZURRO)
    X, Y = cv.X, cv.Y
    cv.paint(((X + 0.35 * (Y - 2.45)) > 0.10).astype(np.float32) * 0.25, (0.60, 0.82, 0.95))
    cv.paint((Y > Z_HDR).astype(np.float32), BLU_SCURO)
    cv.paint((Y > 3.36 + (X + SIGN_X) * 0.02).astype(np.float32), (0.05, 0.22, 0.58))
    cv.rect(-SIGN_X, Z_HDR - 0.012, SIGN_X, Z_HDR, (1, 1, 1))
    cv.text("TRASPORTO DI LINEA VIA MARE", -0.98, 3.365, 0.28, 3.445, (1, 1, 1), font=F_BOLD)
    cv.poly([(0.33, 3.36), (0.90, 3.36), (0.94, 3.45), (0.37, 3.45)], (1, 1, 1))
    cv.text("FERRY LINES", 0.35, 3.365, 0.90, 3.445, BLU_SCURO, font=F_BOLD)
    cv.text("Biglietteria / Ticket Office", -1.0, 3.21, 1.0, 3.35, (1, 1, 1), font=F_BOLD)
    linea01(cv, -1.22, -0.60, 3.13, 0.62)
    cv.rect(SCR[0] - 0.02, SCR[2] - 0.02, SCR[1] + 0.02, SCR[3] + 0.02, (0.15, 0.17, 0.2))
    swoosh(cv, [(0.40, 2.45), (1.25, 2.45)], [(0.66, 3.18), (1.25, 3.18)], 7)
    marchio(cv, 0.86, 2.66, 0.068)
    cv.grime(11, 0.03, 0.02)
    out = (Y > np.vectorize(_arc_z)(X) + 0.002)
    cv.paint(out.astype(np.float32), BLU_SCURO)
    return cv.out(W, H)


def p_insegna_r(W, H):
    cv = _cv(W, H, -SIGN_X, SIGN_X, SIGN_Z0, SIGN_ZT, AZZURRO)
    cv.rect(-SIGN_X, Z_HDR, SIGN_X, SIGN_ZT, BLU_SCURO)
    cv.text("Buon viaggio / Have a nice trip", -1.0, 3.24, 1.0, 3.40, (1, 1, 1), font=F_BOLD)
    swoosh(cv, [(-1.25, 2.45), (-0.2, 2.45)], [(-1.25, 2.8), (0.3, 3.18)], 9)
    marchio(cv, -0.55, 2.68, 0.08)
    linea01(cv, 0.35, 1.18, 3.12, 0.6)
    cv.grime(12, 0.03, 0.03)
    return cv.out(W, H)


NRIGHE = 13
CW, CD = NRIGHE * RIGA, 2.30        # casetta: 2,34 x 2,30 m
ZE, ZR = 2.50, 3.00                 # gronda, colmo
Z_ZOC, Z_RIG, Z_PAN = 0.60, 1.20, 2.15   # fasce della casetta ovest (T2)


def p_zoccolo_t(W, H):
    cv = _cv(W, H, 0, CW, 0, Z_ZOC, AZZURRO)
    cv.rect(0, 0, CW, 0.04, BLU_SCURO)
    linea01(cv, 0.04, 0.80, 0.56, 0.72, align="LEFT")
    swoosh(cv, [(0.95, 0.04), (CW, 0.04)], [(1.50, Z_ZOC), (CW, Z_ZOC)], 3)
    marchio(cv, 1.78, 0.20, 0.07)
    cv.grime(13, 0.04, 0.06)
    return cv.out(W, H)


def p_fianco(W, H):
    cv = _cv(W, H, 0, CD, 0, ZE, AZZURRO)
    cv.rect(0, 0, CD, 0.04, BLU_SCURO)
    cv.rect(0, Z_ZOC, CD, Z_ZOC + 0.008, (0.36, 0.60, 0.74), dh=-0.2)
    swoosh(cv, [(0.0, 1.35), (0.6, 1.50), (CD, 1.95)], [(0.0, 1.80), (1.1, 2.30), (CD, ZE)], 5)
    marchio(cv, 1.30, 2.02, 0.075)
    linea01(cv, 0.5, 1.95, 1.32, 0.8)
    zz = [(1.85 + (0.04 if i % 2 else -0.04), 0.12 + 0.06 * i) for i in range(8)]
    cv.line(zz, 0.018, (1, 1, 1))
    cv.grime(14, 0.04, 0.06)
    return cv.out(W, H)


def p_bacheca(W, H):
    cv = _cv(W, H, 0, CW, Z_RIG, Z_PAN, AZZURRO)
    for x in (0.0, 0.78, 1.56, CW - 0.004):
        cv.rect(x - 0.004, Z_RIG, x + 0.004, Z_PAN, (0.33, 0.56, 0.70), dh=-0.2)
    for cx, cy in ((1.17, 1.98), (1.95, 2.03)):
        cv.circle(cx, cy, 0.05, (1, 1, 1), r_in=0.04)
        cv.circle(cx, cy, 0.018, (1, 1, 1))
    lines = ["Informazioni ai passeggeri", "Orari e tariffe", "Animali a bordo", "Bagagli e biciclette"]
    for i, t in enumerate(lines):
        cv.text(t, 1.62, 1.85 - 0.08 * i, 2.30, 1.905 - 0.08 * i, (1, 1, 1), font=F_SANS)
    cv.text("Benvenuti", 0.84, 1.82, 1.50, 1.89, (1, 1, 1), font=F_BOLD)
    cv.rect(0.86, 1.30, 1.10, 1.64, (0.12, 0.30, 0.62))
    cv.rect(0.89, 1.46, 1.07, 1.60, (0.70, 0.85, 0.95))
    for k in range(3):
        cv.circle(1.85 + 0.13 * k, 1.42, 0.03, (1, 1, 1))
        cv.rect(1.82 + 0.13 * k, 1.26, 1.88 + 0.13 * k, 1.39, (1, 1, 1))
    cv.grime(15, 0.03, 0.04)
    return cv.out(W, H)


def p_zoccolo_b(W, H):
    cv = _cv(W, H, 0, CW, 0, Z_ZOC, AZZURRO)
    cv.rect(0, 0, CW, 0.04, BLU_SCURO)
    for x in (0.0, 0.78, 1.56, CW - 0.004):
        cv.rect(x - 0.004, 0.04, x + 0.004, Z_ZOC, (0.33, 0.56, 0.70), dh=-0.2)
    cv.grime(16, 0.04, 0.08)
    return cv.out(W, H)


def p_orari(W, H):
    cv = _cv(W, H, 0, 0.62, 0, 0.78, (0.90, 0.91, 0.90))
    for x0 in (0.03, 0.33):
        cv.rect(x0, 0.40, x0 + 0.26, 0.74, (0.98, 0.98, 0.97))
        cv.rect(x0, 0.68, x0 + 0.26, 0.74, BLU_SCURO)
        cv.text("ORARI", x0, 0.69, x0 + 0.26, 0.735, (1, 1, 1))
        for r in range(9):
            y = 0.64 - 0.026 * r
            cv.rect(x0 + 0.02, y, x0 + 0.24, y + 0.012, (0.55, 0.6, 0.7) if r % 2 else (0.3, 0.35, 0.5))
    cv.rect(0.20, 0.05, 0.42, 0.36, (0.98, 0.98, 0.97))
    cv.rect(0.20, 0.30, 0.42, 0.36, BLU_SCURO)
    for r in range(8):
        cv.rect(0.22, 0.27 - 0.025 * r, 0.40, 0.282 - 0.025 * r, (0.4, 0.45, 0.6))
    return cv.out(W, H)


def p_bandiera(W, H):
    cv = _cv(W, H, 0, 1.5, 0, 1.0, (0.96, 0.96, 0.96), 0.8)
    cv.poly([(0, 0), (1.5, 0), (1.5, 0.22), (1.0, 0.30), (0.5, 0.18), (0, 0.27)], AZZURRO)
    logo_poetastri(cv, 0.75, 0.62, 0.26)
    cv.text(COMPAGNIA[1], 0.1, 0.05, 1.4, 0.19, (1, 1, 1))
    return cv.out(W, H)


def p_cartello(W, H):
    cv = _cv(W, H, 0, 0.60, 0, 0.30, (0.97, 0.97, 0.96))
    cv.rect(0, 0, 0.6, 0.012, BLU_SCURO)
    cv.text("BIGLIETTI", 0.02, 0.16, 0.58, 0.28, BLU_SCURO)
    cv.text("TICKETS", 0.02, 0.04, 0.58, 0.15, BLU_RIGA)
    return cv.out(W, H)


def p_tenda(W, H):
    cv = _cv(W, H, 0, CW, 0, 1.0, (0.92, 0.92, 0.90), 0.85)
    for k in range(NRIGHE):
        if k % 2 == 0:
            cv.rect(k * RIGA, 0, (k + 1) * RIGA, 1.0, (0.10, 0.20, 0.55))
    cv.grime(17, 0.05, 0.10)
    return cv.out(W, H)


def p_salvag(W, H):
    cv = _cv(W, H, -1, 1, -1, 1, (0.85, 0.20, 0.08))
    a = np.arctan2(cv.Y, cv.X)
    cv.paint(((np.mod(a + 0.2, math.pi / 2) < 0.35)).astype(np.float32), (0.95, 0.95, 0.93))
    return cv.out(W, H)


def p_tricol(W, H):
    cv = _cv(W, H, 0, 3, 0, 2, (0.95, 0.95, 0.95), 0.8)
    cv.rect(0, 0, 1, 2, (0.0, 0.55, 0.27))
    cv.rect(2, 0, 3, 2, (0.80, 0.10, 0.15))
    return cv.out(W, H)


# ---- texture ripetibili ---------------------------------------------------------------------------------------------
def _stripe_detail(size):
    """Sporco vero delle righe: fascia bassa della casetta ovest in T2 (x 955-1158, y 401-479, scheda §10; fuori dalla
    maniglia x 915-945 e dalle scritte di UI), raddrizzata; ogni pixel diviso per la mediana della sua classe (blu/bianco)."""
    img = tp.load(FOTO + "biglietteria_traghetto_di_fronte.png")[..., :3]
    crop = tp.warp(img, [(955, 401), (1158, 401), (1158, 479), (955, 479)], 600, 230)
    blue = (crop[..., 2] - crop[..., 0]) > 0.3
    L = tp.lum(crop)
    ratio = np.ones_like(L)
    for cls in (blue, ~blue):
        ratio[cls] = L[cls] / max(float(np.median(L[cls])), 1e-3)
    ratio = tp.blur(np.clip(ratio, 0.86, 1.10), 1.0)
    ratio = tp.tileable(ratio[::-1].copy())
    return tp.resize(ratio[..., None], size, size)[..., 0]


def make_tex_righe(size=1024, seed=31):
    """6 righe da 18 cm per ripetizione (1,08 m). UV = |x| (modo worldabs): blu sulle righe dispari, cosi' ogni facciata
    da 13 righe comincia e finisce col blu (T2: 7 blu e 6 bianche)."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size
    k = np.floor(xx * 6).astype(int)
    blue = (k % 2) == 1
    rgb = np.where(blue[..., None], av.srgb(BLU_RIGA), av.srgb(BIANCO_RIGA)).astype(np.float32)
    det = _stripe_detail(size)
    big = av.noise(size, size, 5, seed)
    rgb = rgb * (det * (1 + 0.025 * big))[..., None]
    u = (xx * 6) % 1.0
    seam = (u < 0.006) | (u > 0.994)
    rgb[seam] *= 0.8
    h = 0.5 - 0.25 * seam + 0.01 * av.fine(size, size, seed + 1)
    R = np.where(blue, 0.40, 0.45).astype(np.float32) + 0.05 * big
    return av.save_set("T_Morin_Bigl_Righe", np.clip(rgb, 0, 1), h, R, np.zeros_like(R), TEXDIR, 4.0)


def make_tex_legno(size=2048, seed=4712):
    """Tavolato del pontile (2 m per ripetizione), doghe trasversali da ~14 cm grigio-brune consumate (T2, scheda #59585B);
    tinta e dispersione campionate dal tavolato di T2 (x 560-660, y 450-560, scheda §10)."""
    img = tp.load(FOTO + "biglietteria_traghetto_di_fronte.png")[..., :3]
    patch = img[450:560, 560:660]
    base = np.median(patch.reshape(-1, 3), 0) * 0.92
    L = tp.lum(patch)
    spread = float(np.clip(L.std() / L.mean(), 0.04, 0.12))
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    rng = np.random.default_rng(seed)
    NT = 14
    idx = np.minimum((yy * NT).astype(int), NT - 1)
    v = (yy * NT) % 1.0
    tint = rng.uniform(1 - 1.5 * spread, 1 + 1.0 * spread, NT).astype(np.float32)
    off = rng.uniform(0, 1, NT).astype(np.float32)
    seg = (xx + off[idx]) % 1.0
    gap = (v < 0.04) | (v > 0.96) | (seg < 0.003)
    grain = tp.blur(rng.standard_normal((n, n)).astype(np.float32), 1.0)
    grain = tp.resize(tp.resize(grain[..., None], n // 16, n), n, n)[..., 0]
    grain /= grain.std() + 1e-6
    big = av.noise(n, n, 8, seed + 1)
    k = tint[idx] * (1 + 0.08 * grain + 0.05 * big)
    rgb = base[None, None, :] * k[..., None]
    rgb[gap] = (0.07, 0.06, 0.05)
    nail = np.zeros((n, n), bool)
    for xs in (0.25, 0.75):
        nail |= (np.hypot((xx - xs) * n, (v - 0.5) * n / NT) < 3.0)
    rgb[nail] *= 0.5
    h = 0.6 + 0.03 * grain - 0.5 * gap
    R = np.clip(0.80 + 0.05 * big, 0, 1)
    return av.save_set("T_Morin_Pontile_Legno_v2", np.clip(rgb, 0, 1), h, R, np.zeros_like(R), TEXDIR, 8.0)


def make_tex_rete(size=512):
    """Rete a maglia romboidale 5 cm (0,5 m per ripetizione) zincata, con alfa (masked a doppia faccia). Passo da T1."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size
    p = 10.0
    a = np.abs(((xx + yy) * p) % 1.0 - 0.5)
    b = np.abs(((xx - yy) * p) % 1.0 - 0.5)
    m = np.clip((np.maximum(a, b) - 0.44) / 0.02, 0, 1)
    rgb = np.zeros((size, size, 3), np.float32) + av.srgb((0.72, 0.73, 0.72))
    h = 0.5 + 0.3 * m
    R = np.full((size, size), 0.4, np.float32)
    M = np.full((size, size), 0.9, np.float32)
    return av.save_set("T_Morin_Bigl_Rete", rgb, h, R, M, TEXDIR, 3.0, alpha=m)


def make_tex_schermo(W=1024, H=512):
    """Schermo: mare, battello e scritta (niente persone). In UEFN va collegata all'emissive."""
    cv = Canvas(0, 2.0, 0, 1.0, W / 2.0, (0.2, 0.4, 0.7))
    cv.paint(np.clip(cv.Y * 1.4, 0, 1), (0.55, 0.78, 0.95))
    cv.rect(0, 0, 2, 0.38, (0.05, 0.30, 0.50))
    cv.poly([(0.0, 0.38), (0.4, 0.55), (0.8, 0.45), (1.2, 0.60), (1.7, 0.47), (2.0, 0.52), (2.0, 0.38)], (0.25, 0.38, 0.30))
    cv.poly([(0.6, 0.30), (1.4, 0.30), (1.33, 0.22), (0.68, 0.22)], (0.96, 0.96, 0.96))
    cv.rect(0.80, 0.30, 1.22, 0.38, (0.96, 0.96, 0.96))
    cv.rect(0.84, 0.32, 1.18, 0.35, (0.1, 0.12, 0.15))
    cv.text("Enjoy the mugugno", 0.2, 0.70, 1.8, 0.86, (1, 1, 1))
    cv.text(COMPAGNIA[1], 0.4, 0.06, 1.6, 0.16, (1, 1, 1), font=F_SANS)
    rgb, h, r, m = cv.out(W, H)
    return av.save_set("T_Morin_Bigl_Schermo", rgb, h * 0 + 0.5, r * 0 + 0.1, m * 0, TEXDIR, 1.0)


def make_textures():
    painters = {k: av.color_cell(v, 100 + i) for i, (k, v) in enumerate(CELLS.items())}
    painters.update({"INSEGNA_F": p_insegna_f, "INSEGNA_R": p_insegna_r, "ZOCCOLO_T": p_zoccolo_t, "FIANCO": p_fianco,
                     "BACHECA_P": p_bacheca, "ZOCCOLO_B": p_zoccolo_b, "ORARI": p_orari, "BANDIERA": p_bandiera,
                     "CARTELLO": p_cartello, "TENDA": p_tenda, "SALVAG": p_salvag, "TRICOL": p_tricol})
    out = {"atlas": ATL.bake(painters, TEXDIR, 5.0)}
    out["righe"] = make_tex_righe()
    out["legno"] = make_tex_legno()
    out["rete"] = make_tex_rete()
    out["schermo"] = make_tex_schermo()
    return out


def build_materials():
    t = f"{TEXDIR}/"
    pk._pbr_material(MAT_A, t + "T_Morin_Imbarco_v2_D.png", t + "T_Morin_Imbarco_v2_N.png", t + "T_Morin_Imbarco_v2_ORM.png")
    pk._pbr_material(MAT_R, t + "T_Morin_Bigl_Righe_D.png", t + "T_Morin_Bigl_Righe_N.png", t + "T_Morin_Bigl_Righe_ORM.png")
    pk._pbr_material(MAT_W, t + "T_Morin_Pontile_Legno_v2_D.png", t + "T_Morin_Pontile_Legno_v2_N.png",
                     t + "T_Morin_Pontile_Legno_v2_ORM.png")
    pk._pbr_material(MAT_N, t + "T_Morin_Bigl_Rete_D.png", t + "T_Morin_Bigl_Rete_N.png", t + "T_Morin_Bigl_Rete_ORM.png",
                     alpha=True)
    m = pk._pbr_material(MAT_S, t + "T_Morin_Bigl_Schermo_D.png", t + "T_Morin_Bigl_Schermo_N.png",
                         t + "T_Morin_Bigl_Schermo_ORM.png")
    nt = m.node_tree
    bsdf = pk._principled(m)
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE" and "Schermo_D" in n.image.name)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 2.0


def G(ref=None):
    return av.G2(ATL, MATS, ref)


def _sfx(lod):
    return "" if lod == 0 else f"_LOD{lod}"


# asse del pontile inclinato come in OSM: da (71,7; 80,3) a (70,8; 52,0) -> x += K_ASSE * y (y < 0)
K_ASSE = 0.9 / 28.3


def shear_obj(o):
    me = o.data
    for v in me.vertices:
        if v.co.y < 0:
            v.co.x += K_ASSE * v.co.y
    me.update()
    return o


# =================================================================================================================
# biglietteria v2 (origine sul ciglio all'asse del pontile X 71,7, +Y = citta')
# =================================================================================================================
PW = 1.50                          # semilarghezza del tavolato (3 m)
XC_IN = 9 * RIGA                   # 1,62: facce interne delle casette (centri a +-2,79 = X 74,49 e 68,91)
Y_C = 78.9 - mi.ciglio_y(71.7)     # -1,31: centro delle casette
CY0, CY1 = Y_C - CD / 2, Y_C + CD / 2
ZB = -0.03
Y_PORT = 79.3 - mi.ciglio_y(71.7)  # -0,91: portale e cancello
POST_X = 1.20                      # montanti del portale (luce 2,4 m)
GATE_H = 0.55                      # anta 1,1 m centrata sull'asse, cerniera a +0,55, aperta di 75 gradi verso il pontile
CAN_Y = (-2.60, -8.20)             # tettoia e rete (Y 78 -> 72)
FENCE_X = -PW + 0.03
POLE = (1.20, -2.25)               # pennone (72,9; 78,0)


def _wall_y(g, x0, x1, y, z0, z1, cell, mi_=A_, out=1):
    g.quad([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], cell, mi_, out=(0, out, 0))


def _wall_x(g, y0, y1, x, z0, z1, cell, mi_=A_, out=1):
    g.quad([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)], cell, mi_, out=(out, 0, 0))


def _casetta(g, kind, lod):
    """T = casetta est (+X) con lo sportello; B = casetta ovest (-X) con porta e bacheca."""
    sgn = 1 if kind == "T" else -1
    x0, x1 = sorted((sgn * XC_IN, sgn * (XC_IN + CW)))
    xc = (x0 + x1) / 2
    y0, y1 = CY0, CY1
    x_out = x1 if kind == "T" else x0
    x_in = x0 if kind == "T" else x1
    if kind == "T":
        _wall_y(g, x0, x1, y1, ZB, Z_ZOC, "ZOCCOLO_T")
        # sportello verso il cancello (in T2 a destra della casetta est): bancone 1,0 x 0,55, mensola a 1,05
        wx0, wx1, wz0, wz1 = x0 + 0.22, x0 + 1.22, 1.05, 1.95
        _wall_y(g, x0, wx0, y1, Z_ZOC, ZE, None, R_)
        _wall_y(g, wx1, x1, y1, Z_ZOC, ZE, None, R_)
        _wall_y(g, wx0, wx1, y1, Z_ZOC, 0.50, None, R_)
        _wall_y(g, wx0, wx1, y1, wz1, ZE, None, R_)
        d = 0.25
        g.quad([(wx0, y1 - d, 0.50), (wx1, y1 - d, 0.50), (wx1, y1 - d, wz1), (wx0, y1 - d, wz1)], "VETRO_INT", out=(0, 1, 0))
        g.quad([(wx0, y1, 0.50), (wx0, y1 - d, 0.50), (wx0, y1 - d, wz1), (wx0, y1, wz1)], "AZZURRO_INT", out=(1, 0, 0))
        g.quad([(wx1, y1 - d, 0.50), (wx1, y1, 0.50), (wx1, y1, wz1), (wx1, y1 - d, wz1)], "AZZURRO_INT", out=(-1, 0, 0))
        g.quad([(wx0, y1, wz1), (wx1, y1, wz1), (wx1, y1 - d, wz1), (wx0, y1 - d, wz1)], "AZZURRO_INT", out=(0, 0, -1))
        g.box(wx0 + 0.02, wx1 - 0.02, y1 - d, y1 + 0.20, 0.50, wz0, "LEGNO_BANCO", faces=("top", "yp", "xn", "xp"))
        g.box(wx0 - 0.04, wx1 + 0.04, y1 + 0.20, y1 + 0.28, wz0 - 0.03, wz0, "LEGNO_BANCO")      # mensola
        g.quad([(x1 - 0.80, y1 + 0.012, 1.45), (x1 - 0.25, y1 + 0.012, 1.45), (x1 - 0.25, y1 + 0.012, 1.72),
                (x1 - 0.80, y1 + 0.012, 1.72)], "CARTELLO", out=(0, 1, 0))
        # tenda a righe sporgente 0,6 m, mantovana 0,20
        ty, tz0, tz1 = y1 + 0.60, 2.22, 1.98
        g.quad([(x0 - 0.04, y1, tz0), (x1 + 0.04, y1, tz0), (x1 + 0.04, ty, tz1), (x0 - 0.04, ty, tz1)], "TENDA",
               out=(0, 0.4, 1))
        g.quad([(x0 - 0.04, y1, tz0 - 0.01), (x1 + 0.04, y1, tz0 - 0.01), (x1 + 0.04, ty, tz1 - 0.01),
                (x0 - 0.04, ty, tz1 - 0.01)], "BIANCO_SPORCO", out=(0, -0.4, -1))
        g.quad([(x0 - 0.04, ty, tz1 - 0.20), (x1 + 0.04, ty, tz1 - 0.20), (x1 + 0.04, ty, tz1), (x0 - 0.04, ty, tz1)],
               "TENDA", out=(0, 1, 0))
        g.quad([(x0 - 0.04, ty - 0.01, tz1 - 0.20), (x1 + 0.04, ty - 0.01, tz1 - 0.20), (x1 + 0.04, ty - 0.01, tz1),
                (x0 - 0.04, ty - 0.01, tz1)], "BIANCO_SPORCO", out=(0, -1, 0))
        for xs, o in ((x0 - 0.04, -1), (x1 + 0.04, 1)):
            g.quad([(xs, y1, tz0), (xs, ty, tz1), (xs, ty, tz1 - 0.20), (xs, y1, tz1 - 0.20)], "TENDA", out=(o, 0, 0))
            g.quad([(xs - 0.005 * o, y1, tz0), (xs - 0.005 * o, ty, tz1), (xs - 0.005 * o, ty, tz1 - 0.20),
                    (xs - 0.005 * o, y1, tz1 - 0.20)], "BIANCO_SPORCO", out=(-o, 0, 0))
    else:
        _wall_y(g, x0, x1, y1, ZB, Z_ZOC, "ZOCCOLO_B")
        _wall_y(g, x0, x1, y1, Z_ZOC, Z_RIG, None, R_)
        _wall_y(g, x0, x1, y1, Z_RIG, Z_PAN, "BACHECA_P")
        _wall_y(g, x0, x1, y1, Z_PAN, ZE, None, R_)
        bx1, bx0 = x1 - 0.08, x1 - 0.68                     # bacheca ~0,6 x 0,8 (T2: in alto verso il cancello)
        g.box(bx0, bx1, y1, y1 + 0.09, 1.28, 2.08, "TELAIO_BIANCO", faces=("xn", "xp", "top", "bot", "yp"))
        g.quad([(bx0 + 0.05, y1 + 0.093, 1.33), (bx1 - 0.05, y1 + 0.093, 1.33), (bx1 - 0.05, y1 + 0.093, 2.03),
                (bx0 + 0.05, y1 + 0.093, 2.03)], "ORARI", out=(0, 1, 0))
        if lod < 2:
            g.box(x1 - 1.10, x1 - 1.06, y1, y1 + 0.06, 0.96, 1.14, "ACCIAIO")              # maniglia a 1,05
            g.box(x1 - 1.10, x1 - 0.94, y1 + 0.04, y1 + 0.07, 1.03, 1.06, "ACCIAIO")
    # frontoni e retro
    for y, o in ((y1, 1), (y0, -1)):
        tri = [(x0, y, ZE), (x1, y, ZE), (xc, y, ZR)]

        def fn(bm, tri=tri, o=o):
            f = bm.faces.new([bm.verts.new(p) for p in tri])
            f.normal_update()
            if f.normal.y * o < 0:
                f.normal_flip()
        g.new_faces(fn, None, R_)
    _wall_y(g, x0, x1, y0, ZB, Z_ZOC, "AZZURRO", out=-1)
    _wall_y(g, x0, x1, y0, Z_ZOC, ZE, None, R_, out=-1)
    # fianchi: esterno grafico (verso il camminamento), interno a righe sopra lo zoccolo
    _wall_x(g, y0, y1, x_out, ZB, ZE, "FIANCO", out=sgn)
    _wall_x(g, y0, y1, x_in, ZB, Z_ZOC, "AZZURRO", out=-sgn)
    _wall_x(g, y0, y1, x_in, Z_ZOC, ZE, None, R_, out=-sgn)
    # spigoli blu
    if lod < 2:
        for xs in (x0, x1):
            for ys in (y0, y1):
                g.box(xs - 0.025, xs + 0.025, ys - 0.025, ys + 0.025, ZB, ZE, "BLU_SCURO", faces=("xn", "xp", "yn", "yp"))
    # tetto in lamiera grigio-azzurra con scossaline brune
    ov = 0.15
    ze = ZE - ov * (ZR - ZE) / (CW / 2)
    ya, yb = y0 - ov, y1 + ov
    for xs in (x0 - ov, x1 + ov):
        o = 1 if xs > xc else -1
        g.quad([(xs, ya, ze), (xc, ya, ZR + 0.03), (xc, yb, ZR + 0.03), (xs, yb, ze)], "TETTO", out=(o * 0.4, 0, 1))
        g.quad([(xs, ya, ze - 0.03), (xc, ya, ZR), (xc, yb, ZR), (xs, yb, ze - 0.03)], "BIANCO", out=(-o * 0.4, 0, -1))
        g.quad([(xs, ya, ze - 0.08), (xs, yb, ze - 0.08), (xs, yb, ze), (xs, ya, ze)], "SCOSSALINA", out=(o, 0, 0))
    for y, o in ((yb + 0.001, 1), (ya - 0.001, -1)):
        for xs in (x0 - ov, x1 + ov):
            g.quad([(xs, y, ze - 0.10), (xc, y, ZR - 0.08), (xc, y, ZR + 0.04), (xs, y, ze + 0.01)], "SCOSSALINA", out=(0, o, 0))
            g.quad([(xs, y - 0.02 * o, ze - 0.10), (xc, y - 0.02 * o, ZR - 0.08), (xc, y - 0.02 * o, ZR + 0.04),
                    (xs, y - 0.02 * o, ze + 0.01)], "SCOSSALINA", out=(0, -o, 0))
    if lod == 0 and kind == "B":   # telecamera sotto la gronda (T2)
        cx_ = x_out + 0.15
        g.box(cx_ - 0.06, cx_ + 0.06, y1 - 0.02, y1 + 0.16, ZE - 0.24, ZE - 0.14, "BIANCO")


def _bars_panel(g, xa, xb, y, z0, z1, n, lod, M=None):
    """Pannello a sbarre bianche (telaio + tondini) nel piano XZ a quota y; M opzionale (anta ruotata)."""
    t = 0.04
    M = M or Matrix()
    boxes = [(xa, xa + t, y - 0.02, y + 0.02, z0, z1), (xb - t, xb, y - 0.02, y + 0.02, z0, z1),
             (xa + t, xb - t, y - 0.02, y + 0.02, z0, z0 + t), (xa + t, xb - t, y - 0.02, y + 0.02, z1 - t, z1),
             (xa + t, xb - t, y - 0.02, y + 0.02, z0 + 0.26, z0 + 0.26 + t)]
    for b in boxes:
        g.box(*b, "TELAIO_BIANCO", mat=M)
    nb = n if lod < 2 else max(2, n // 2)
    for k in range(nb):
        x = xa + t + (xb - xa - 2 * t) * (k + 0.5) / nb
        g.box(x - 0.011, x + 0.011, y - 0.011, y + 0.011, z0 + t, z1 - t, "TELAIO_BIANCO", faces=("xn", "xp", "yn", "yp"), mat=M)


def _portale(g, lod):
    n = 12 if lod == 0 else (8 if lod == 1 else 5)
    yp = Y_PORT
    top = [(SIGN_X - 2 * SIGN_X * i / n, _arc_z(SIGN_X - 2 * SIGN_X * i / n)) for i in range(n + 1)]
    outline = [(-SIGN_X, SIGN_Z0), (SIGN_X, SIGN_Z0)] + top
    yf, yr = yp + 0.09, yp - 0.09

    def face(y, cell, o):
        def fn(bm):
            f = bm.faces.new([bm.verts.new((x, y, z)) for x, z in outline])
            f.normal_update()
            if f.normal.y * o < 0:
                f.normal_flip()
        g.new_faces(fn, cell)
    face(yf, "INSEGNA_F", 1)
    face(yr, "INSEGNA_R", -1)
    for (xa, za), (xb, zb) in zip(outline, outline[1:] + outline[:1]):
        mid = Vector(((xa + xb) / 2, 0, (za + zb) / 2))
        g.quad([(xa, yr, za), (xb, yr, zb), (xb, yf, zb), (xa, yf, za)], "BLU_SCURO", out=tuple(mid - Vector((0, 0, 3.0))))
    # schermo con cornice bianca (vista da +Y: x di vista = -x mondo)
    sx0, sx1, sz0, sz1 = -SCR[1], -SCR[0], SCR[2], SCR[3]
    g.box(sx0, sx1, yf, yf + 0.06, sz0, sz1, "TELAIO_BIANCO", faces=("xn", "xp", "top", "bot", "yp"))
    g.quad([(sx0 + 0.04, yf + 0.062, sz0 + 0.04), (sx1 - 0.04, yf + 0.062, sz0 + 0.04),
            (sx1 - 0.04, yf + 0.062, sz1 - 0.04), (sx0 + 0.04, yf + 0.062, sz1 - 0.04)], None, S_, out=(0, 1, 0))
    # montanti in tubolare bianco
    for x in (-POST_X, POST_X):
        g.box(x - 0.05, x + 0.05, yp - 0.05, yp + 0.05, 0.0, SIGN_Z0, "TELAIO_BIANCO", faces=("xn", "xp", "yn", "yp"))
    # pannelli fissi a sbarre dal cancello alle casette, anta aperta verso il pontile
    for s in (-1, 1):
        xa, xb = sorted((s * (GATE_H + 0.03), s * (POST_X - 0.05)))
        _bars_panel(g, xa, xb, yp, 0.05, 1.95, 6, lod)
        xa, xb = sorted((s * (POST_X + 0.05), s * (XC_IN - 0.01)))
        _bars_panel(g, xa, xb, yp, 0.05, 1.95, 3, lod)
    M = Matrix.Translation((GATE_H, yp, 0)) @ Matrix.Rotation(math.radians(75), 4, "Z")
    _bars_panel(g, -1.10, 0.0, 0.0, 0.05, 1.95, 10, lod, M)
    nw = 14 if lod == 0 else 7
    for zc, amp, hh in ((1.12, 0.06, 0.07), (0.92, 0.045, 0.045)):     # due onde blu a meta' altezza
        xs = np.linspace(-1.02, -0.08, nw + 1)
        lo = [(x, zc + amp * math.sin(x * 2 * math.pi / 0.55) - hh / 2) for x in xs]
        for yo, o in ((0.028, 1), (-0.028, -1)):
            a = [tuple(M @ Vector((x, yo, z))) for x, z in lo]
            b = [tuple(M @ Vector((x, yo, z + hh))) for x, z in lo]
            nrm = (M.to_3x3() @ Vector((0, o, 0)))
            g.strip(a, b, "BLU_RIGA", out=tuple(nrm))
    # piastra di passaggio dalla banchina alla piattaforma
    g.box(-POST_X, POST_X, yp + 0.05, 0.70, 0.0, 0.025, "PIASTRA", faces=("top", "yp", "xn", "xp"))


def _tettoia(g, lod):
    x0, x1, y0, y1 = -PW - 0.05, PW + 0.05, CAN_Y[1], CAN_Y[0]
    z0, z1 = 2.55, 2.60
    g.box(x0, x1, y0, y1, z0, z1, "BIANCO", faces=("top", "bot"))
    ys = np.linspace(y1, y0, 3)
    for xs, o in ((x1, 1), (x0, -1)):
        for ya, yb in zip(ys[:-1], ys[1:]):
            g.quad([(xs, yb, 2.30), (xs, ya, 2.30), (xs, ya, z1), (xs, yb, z1)], "TENDA", out=(o, 0, 0))
            g.quad([(xs - 0.01 * o, yb, 2.30), (xs - 0.01 * o, ya, 2.30), (xs - 0.01 * o, ya, z1), (xs - 0.01 * o, yb, z1)],
                   "BIANCO_SPORCO", out=(-o, 0, 0))
    for yy, o in ((y0, -1), (y1, 1)):
        g.quad([(x0, yy, 2.30), (x1, yy, 2.30), (x1, yy, z1), (x0, yy, z1)], "TENDA", out=(0, o, 0))
        g.quad([(x0, yy - 0.01 * o, 2.30), (x1, yy - 0.01 * o, 2.30), (x1, yy - 0.01 * o, z1), (x0, yy - 0.01 * o, z1)],
               "BIANCO_SPORCO", out=(0, -o, 0))
    sides = 6 if lod == 0 else 4
    for x in (x0 + 0.05, x1 - 0.05):
        for y in (y1 - 0.05, (y0 + y1) / 2, y0 + 0.05):
            g.tube([(x, y, 0.0), (x, y, z0)], 0.035, sides, "TELAIO_BIANCO", cap=False)
    # due paletti con bandierine bianche sulla tettoia (T1)
    if lod < 2:
        for y in (y1 - 1.0, y0 + 1.5):
            g.tube([(x1 - 0.1, y, z1), (x1 - 0.1, y, z1 + 1.8)], 0.02, 4, "TELAIO_BIANCO", cap=False)
            for o in (1, -1):
                g.quad([(x1 - 0.1, y + 0.003 * o, z1 + 1.3), (x1 + 0.45, y + 0.003 * o, z1 + 1.3),
                        (x1 + 0.45, y + 0.003 * o, z1 + 1.75), (x1 - 0.1, y + 0.003 * o, z1 + 1.75)], "BIANCO", out=(0, o, 0))
    # rete chain-link sul lato ovest, h 1,8, telaio zincato
    fx, fy0, fy1, fz1 = FENCE_X, y1 - 0.05, y0 + 0.05, 1.80
    g.tube([(fx, fy0, 0.04), (fx, fy1, 0.04)], 0.025, sides, "ZINCATO")
    g.tube([(fx, fy0, fz1), (fx, fy1, fz1)], 0.025, sides, "ZINCATO")
    for y in np.linspace(fy0, fy1, 4):
        g.tube([(fx, y, 0.04), (fx, y, fz1)], 0.025, sides, "ZINCATO", cap=False)
    for xo, o in ((fx - 0.003, -1), (fx + 0.003, 1)):
        g.quad([(xo, fy0, 0.04), (xo, fy1, 0.04), (xo, fy1, fz1), (xo, fy0, fz1)], None, N_, out=(o, 0, 0))


def _pennone(g, lod):
    px, py = POLE
    g.tube([(px, py, 0.0), (px, py, 8.0)], 0.045, 8 if lod == 0 else 5, "TELAIO_BIANCO")
    g.new_faces(lambda bm: pk._sphere(bm, (px, py, 8.05), 0.07, 6 if lod < 2 else 4, 4 if lod < 2 else 2), "TELAIO_BIANCO")
    xa, xb = px + 0.05, px + 1.55
    for o in (1, -1):
        y = py + 0.004 * o
        g.quad([(xa, y, 7.0), (xb, y, 7.0), (xb, y, 8.0), (xa, y, 8.0)], "BANDIERA", out=(0, o, 0))


def build_biglietteria(coll, lod=0, name="SM_Morin_Biglietteria_v2"):
    g = G()
    _casetta(g, "T", lod)
    _casetta(g, "B", lod)
    _portale(g, lod)
    _tettoia(g, lod)
    _pennone(g, lod)
    return shear_obj(g.finish(name + _sfx(lod), coll))


def ucx_biglietteria(coll, name="SM_Morin_Biglietteria_v2"):
    yp = Y_PORT
    boxes = []
    for sgn in (1, -1):
        x0, x1 = sorted((sgn * XC_IN, sgn * (XC_IN + CW)))
        boxes.append((x0, x1, CY0, CY1, ZB, ZE))
    gx = GATE_H
    a = math.radians(75)
    boxes += [(-SIGN_X, SIGN_X, yp - 0.09, yp + 0.15, SIGN_Z0, SIGN_ZT),                    # insegna
              (-POST_X - 0.05, -POST_X + 0.05, yp - 0.05, yp + 0.05, 0.0, SIGN_Z0),
              (POST_X - 0.05, POST_X + 0.05, yp - 0.05, yp + 0.05, 0.0, SIGN_Z0),
              (-XC_IN, -GATE_H - 0.02, yp - 0.03, yp + 0.03, 0.0, 1.95),                    # pannelli fissi
              (GATE_H + 0.02, XC_IN, yp - 0.03, yp + 0.03, 0.0, 1.95),
              (-PW - 0.05, PW + 0.05, CAN_Y[1], CAN_Y[0], 2.55, 2.60),                      # tettoia
              (FENCE_X - 0.04, FENCE_X + 0.04, CAN_Y[1], CAN_Y[0], 0.0, 1.83),              # rete
              (XC_IN - 0.04, XC_IN + CW + 0.04, CY1, CY1 + 0.62, 1.78, 2.22),               # tenda
              (XC_IN + 0.20, XC_IN + 1.24, CY1, CY1 + 0.28, 0.50, 1.05),                    # bancone
              (POLE[0] - 0.05, POLE[0] + 0.05, POLE[1] - 0.05, POLE[1] + 0.05, 0.0, 8.0),   # pennone
              (-POST_X, POST_X, yp + 0.05, 0.70, 0.0, 0.025)]                               # piastra
    pk._ucx(name, boxes, coll)
    i = len(boxes)
    # anta aperta (convesso ruotato)
    M = Matrix.Translation((gx, yp, 0)) @ Matrix.Rotation(a, 4, "Z")
    pk._ucx_hull(name, i, [M @ Vector((x, y, z)) for x in (-1.10, 0.0) for y in (-0.03, 0.03) for z in (0.0, 1.95)], coll)
    i += 1
    for sgn in (1, -1):                                                                # tetti
        x0, x1 = sorted((sgn * XC_IN, sgn * (XC_IN + CW)))
        xc = (x0 + x1) / 2
        pts = [(x0 - 0.15, y, ZE - 0.05) for y in (CY0 - 0.15, CY1 + 0.15)] + \
              [(x1 + 0.15, y, ZE - 0.05) for y in (CY0 - 0.15, CY1 + 0.15)] + \
              [(xc, y, ZR + 0.03) for y in (CY0 - 0.15, CY1 + 0.15)]
        pk._ucx_hull(name, i, [Vector(p) for p in pts], coll)
        i += 1
    return i


# =================================================================================================================
# pontile d'imbarco v2 (stessa origine della biglietteria): piattaforma, rampa, tavolato su travi e pali tubolari
# =================================================================================================================
Z_IMP = -0.34                       # calpestio del tavolato (0,66 m sull'acqua) [S]
PLAT_A = (-4.25, 4.25, -2.75, 0.0)  # piattaforma di radice (X 67,5-76, Y 77,5-80,2)
Y_LIV = -8.40                       # fine del tratto a quota banchina (sotto la tettoia)
Y_RAMPA = (Y_LIV, -11.40)
Y_TESTA = 52.0 - mi.ciglio_y(71.7)  # -28,21 (testa OSM)
PALI_Y = [-4.5, -8.2] + [-12.0 - 4.0 * k for k in range(4)] + [-27.9]
TIRES_Y = [-12.0 - 2.6 * k for k in range(7)]
BITTE = [(-1.20, -27.75), (1.20, -27.75), (-1.20, -25.4), (1.20, -25.4)]
RAIL_Y = (CAN_Y[1] - 0.05, -13.0)
TAV = (-0.85, -5.2)


def _plat(g, x0, x1, y0, y1, z, faces=("xn", "xp", "yn")):
    g.box(x0, x1, y0, y1, z - 0.001, z, None, W_, faces=("top",))
    g.box(x0, x1, y0, y1, z - 0.36, z - 0.001, "RUGGINE", faces=faces + ("bot",))


def _zf(y):
    ya, yb = Y_RAMPA
    if y >= ya:
        return 0.01
    if y <= yb:
        return Z_IMP
    return Z_IMP + (0.01 - Z_IMP) * (y - yb) / (ya - yb)


def _tavolino(g, lod):
    x, y = TAV
    z = 0.01
    g.box(x - 0.40, x + 0.40, y - 0.30, y + 0.30, z + 0.70, z + 0.73, "TAVOLO")
    for s in (-1, 1):
        g.hull([(x - 0.36, y + s * 0.26, z), (x - 0.33, y + s * 0.26, z), (x + 0.36, y + s * 0.26, z + 0.70),
                (x + 0.33, y + s * 0.26, z + 0.70), (x - 0.36, y + s * 0.24, z), (x - 0.33, y + s * 0.24, z),
                (x + 0.36, y + s * 0.24, z + 0.70), (x + 0.33, y + s * 0.24, z + 0.70)], "SCURO")
        if lod < 2:
            g.hull([(x + 0.36, y + s * 0.26, z), (x + 0.33, y + s * 0.26, z), (x - 0.36, y + s * 0.26, z + 0.70),
                    (x - 0.33, y + s * 0.26, z + 0.70), (x + 0.36, y + s * 0.24, z), (x + 0.33, y + s * 0.24, z),
                    (x - 0.36, y + s * 0.24, z + 0.70), (x - 0.33, y + s * 0.24, z + 0.70)], "SCURO")
    cx, cy = x + 0.05, y - 0.62
    g.box(cx - 0.23, cx + 0.23, cy - 0.22, cy + 0.22, z + 0.42, z + 0.46, "SEDIA")
    g.hull([(cx - 0.23, cy - 0.24, z + 0.46), (cx + 0.23, cy - 0.24, z + 0.46), (cx - 0.25, cy - 0.30, z + 0.88),
            (cx + 0.25, cy - 0.30, z + 0.88), (cx - 0.23, cy - 0.20, z + 0.46), (cx + 0.23, cy - 0.20, z + 0.46),
            (cx - 0.25, cy - 0.26, z + 0.88), (cx + 0.25, cy - 0.26, z + 0.88)], "SEDIA")
    for dx in (-0.2, 0.2):
        for dy in (-0.19, 0.19):
            g.box(cx + dx - 0.02, cx + dx + 0.02, cy + dy - 0.02, cy + dy + 0.02, z, z + 0.42, "SEDIA",
                  faces=("xn", "xp", "yn", "yp"))


def build_pontile(coll, lod=0, name="SM_Morin_PontileImbarco_v2"):
    g = G()
    _plat(g, *PLAT_A, 0.01, faces=("xn", "xp", "yn"))
    _plat(g, -PW, PW, Y_LIV, PLAT_A[2], 0.01, faces=("xn", "xp"))
    ya, yb = Y_RAMPA
    g.quad([(-PW, yb, Z_IMP), (PW, yb, Z_IMP), (PW, ya, 0.01), (-PW, ya, 0.01)], None, W_, out=(0, 0, 1))
    for x, o in ((-PW, -1), (PW, 1)):
        g.quad([(x, yb, Z_IMP - 0.36), (x, ya, -0.35), (x, ya, 0.01), (x, yb, Z_IMP)], "RUGGINE", out=(o, 0, 0))
    g.quad([(-PW, yb, Z_IMP - 0.36), (PW, yb, Z_IMP - 0.36), (PW, ya, -0.35), (-PW, ya, -0.35)], "RUGGINE", out=(0, 0, -1))
    yt = Y_TESTA
    g.box(-PW, PW, yt, yb, Z_IMP - 0.001, Z_IMP, None, W_, faces=("top",))
    g.box(-PW, PW, yt, yb, Z_IMP - 0.06, Z_IMP - 0.001, "LEGNO_GRIGIO", faces=("xn", "xp", "yn"))
    for x in (-PW + 0.08, PW - 0.08):     # travi d'acciaio scure lungo i bordi
        g.box(x - 0.08, x + 0.08, yt + 0.02, yb, Z_IMP - 0.40, Z_IMP - 0.06, "RUGGINE", faces=("xn", "xp", "bot", "yn"))
    g.box(-PW + 0.16, PW - 0.16, yt + 0.02, yb, Z_IMP - 0.25, Z_IMP - 0.06, "RUGGINE", faces=("bot",))
    if lod < 2:
        for y in np.arange(yb - 2.0, yt, -2.0):
            g.box(-PW + 0.16, PW - 0.16, y - 0.06, y + 0.06, Z_IMP - 0.25, Z_IMP - 0.06, "RUGGINE", faces=("yn", "yp", "bot"))
    # pali tubolari in acciaio (T1, articolo La Nazione)
    sides = (10, 6, 5)[lod]
    for y in PALI_Y:
        ztop = (0.01 if y > Y_RAMPA[1] else Z_IMP) - 0.36
        for x in (-1.25, 1.25):
            g.lathe([(0.16, -4.0), (0.16, ztop)], sides, "RUGGINE", mat=Matrix.Translation((x, y, 0)), cap_top=False)
    for x in (-3.9, 3.9):
        g.lathe([(0.16, -4.0), (0.16, -0.35)], sides, "RUGGINE", mat=Matrix.Translation((x, -2.4, 0)), cap_top=False)
    # copertoni sui due lati del tavolato
    nmaj, nmin = ((14, 6), (10, 4), (6, 3))[lod]
    for s in (-1, 1):
        for y in TIRES_Y:
            M = Matrix.Translation((s * (PW + 0.13), y, Z_IMP - 0.30)) @ Matrix.Rotation(math.radians(90), 4, "Y")
            g.torus(M, 0.27, 0.11, nmaj, nmin, "GOMMA")
            if lod < 2:
                g.tube([(s * (PW + 0.13), y, Z_IMP - 0.30 + 0.38), (s * (PW - 0.05), y, Z_IMP)], 0.012, 3, "CORDA", cap=False)
    # 4 bitte nere basse in testa
    nb = (10, 6, 5)[lod]
    for x, y in BITTE:
        g.lathe([(0.11, 0.0), (0.09, 0.03), (0.08, 0.36), (0.12, 0.39), (0.12, 0.44), (0.0, 0.46)], nb, "GHISA",
                mat=Matrix.Translation((x, y, Z_IMP)))
    # ringhiera tubolare bianca a ovest dopo la rete, h 1,1
    sides = 6 if lod == 0 else 4
    xr = -PW + 0.05
    ys = [RAIL_Y[0], Y_RAMPA[0], Y_RAMPA[1], RAIL_Y[1]]
    rail = [(xr, y, _zf(y)) for y in ys]
    g.tube([(x, y, z + 1.1) for x, y, z in rail], 0.03, sides, "TELAIO_BIANCO")
    if lod < 2:
        g.tube([(x, y, z + 0.55) for x, y, z in rail], 0.02, 4, "TELAIO_BIANCO")
    for x, y, z in rail:
        g.tube([(x, y, z), (x, y, z + 1.1)], 0.025, 4, "TELAIO_BIANCO", cap=False)
    _tavolino(g, lod)
    return shear_obj(g.finish(name + _sfx(lod), coll))


def ucx_pontile(coll, name="SM_Morin_PontileImbarco_v2"):
    ya, yb = Y_RAMPA
    boxes = [(PLAT_A[0], PLAT_A[1], PLAT_A[2], PLAT_A[3], -0.35, 0.01),
             (-PW, PW, Y_LIV, PLAT_A[2], -0.35, 0.01),
             (-PW - 0.25, PW + 0.25, Y_TESTA, yb, -1.10, Z_IMP),
             (-PW, -PW + 0.10, RAIL_Y[0], ya, 0.01, 1.13),
             (-PW, -PW + 0.10, RAIL_Y[1], yb, Z_IMP, Z_IMP + 1.13)]
    boxes += [(x - 0.13, x + 0.13, y - 0.13, y + 0.13, Z_IMP, Z_IMP + 0.46) for x, y in BITTE]
    boxes += [(TAV[0] - 0.40, TAV[0] + 0.40, TAV[1] - 0.30, TAV[1] + 0.30, 0.01, 0.74),
              (TAV[0] - 0.20, TAV[0] + 0.30, TAV[1] - 0.92, TAV[1] - 0.38, 0.01, 0.89)]
    pk._ucx(name, boxes, coll)
    i = len(boxes)
    pk._ucx_hull(name, i, [Vector(p) for p in [(-PW, ya, 0.01), (PW, ya, 0.01), (-PW, yb, Z_IMP), (PW, yb, Z_IMP),
                                               (-PW, ya, -0.35), (PW, ya, -0.35), (-PW, yb, Z_IMP - 0.36),
                                               (PW, yb, Z_IMP - 0.36)]], coll)
    i += 1
    pk._ucx_hull(name, i, [Vector(p) for p in [(-PW, ya, 0.01), (-PW + 0.1, ya, 0.01), (-PW, yb, Z_IMP),
                                               (-PW + 0.1, yb, Z_IMP), (-PW, ya, 1.13), (-PW + 0.1, ya, 1.13),
                                               (-PW, yb, Z_IMP + 1.13), (-PW + 0.1, yb, Z_IMP + 1.13)]], coll)
    return i + 1



# =================================================================================================================
# traghetto v2 (+X = prua, galleggiamento a Z 0)
# =================================================================================================================
LOA, HB = 28.0, 3.3
X_ST, X_BO = -14.0, 14.0
STATIONS = [-14.0, -13.4, -10.0, -5.0, 0.0, 4.0, 6.5, 9.0, 11.0, 12.5, 13.4, 13.8, 14.0]
Z_COP = 1.05                                    # coperta
TUGA_X = (-10.5, 8.0, 10.2)                     # poppa, inizio dell'arco di prua, punta dell'arco
TUGA_W = 3.12
Z_SUP = (3.15, 3.30)                            # solaio e calpestio del ponte superiore
SUP_X = (-12.6, 8.5, 10.6)
SUP_W = 3.30
TIM_X = (3.0, 8.2, 9.4)
TIM_W = 2.30
Z_TIM = 5.15
SCALA = (-13.7, -11.1, -2.85, -1.95)            # piede x0, sbarco x1, y0, y1 (lato -Y, lontano dal pontile)
VARCO = (-12.3, -10.7)                          # varco della battagliola sul lato +Y (pontile)
RAFT_X = [-11.9 + 1.0 * k for k in range(5)]


def half_b(x):
    if x <= 4.0:
        return HB - 0.12 * max(0.0, (-x - 10.0) / 4.0)
    t = min((x - 4.0) / (X_BO - 4.0), 1.0)
    return max(HB * math.sqrt(max(1.0 - t ** 1.8, 0.0)), 0.04)


def z_keel(x):
    if x < -9.0:
        return -1.3 + (x + 9.0) / -5.0 * 0.75
    if x > 7.0:
        return -1.3 + ((x - 7.0) / 7.0) ** 1.5 * 1.75
    return -1.3


def z_sheer(x):
    return Z_COP + 0.50 * max(0.0, (x - 5.0) / 9.0) ** 2


def _section(x):
    b, zk, zs = half_b(x), z_keel(x), z_sheer(x)
    z1 = max(-0.05, zk + 0.02)
    z2 = max(0.14, z1 + 0.02)
    zm = zk + 0.55 * (z1 - zk)
    return [(0.0, zk), (0.72 * b, zm), (0.93 * b, z1), (0.985 * b, z2), (b, zs)]


def _plan(x0, xa, xtip, w, n):
    """Pianta con prua arrotondata (antioraria): poppa dritta a x0, fianchi a +-w fino a xa, arco fino a xtip."""
    pts = [(x0, -w), (xa, -w)]
    for k in range(1, n):
        a = -math.pi / 2 + math.pi * k / n
        pts.append((xa + (xtip - xa) * math.cos(a), w * math.sin(a)))
    pts += [(xa, w), (x0, w)]
    return pts


def _hull(g, lod):
    st = STATIONS if lod == 0 else [s for i, s in enumerate(STATIONS) if i % 2 == 0 or s == 14.0]
    rings = []
    for x in st:
        sec = _section(x)
        rings.append(([g.bm.verts.new((x, -y, z)) for y, z in sec], [g.bm.verts.new((x, y, z)) for y, z in sec]))
    cells = ["ANTIVEG", "ANTIVEG", "NAVY", "BIANCO"]
    for (pa, sa), (pb, sb) in zip(rings[:-1], rings[1:]):
        for r in range(4):
            g._set([g.bm.faces.new([pa[r + 1], pa[r], pb[r], pb[r + 1]])], cells[r])
            g._set([g.bm.faces.new([sa[r], sa[r + 1], sb[r + 1], sb[r]])], cells[r])
        g._set([g.bm.faces.new([pa[4], pb[4], sb[4], sa[4]])], "PONTE_GRIGIO")
    p, s = rings[0]
    for r in range(4):
        g._set([g.bm.faces.new([p[r], p[r + 1], s[r + 1], s[r]])], cells[r])
    p, s = rings[-1]
    for r in range(4):
        g._set([g.bm.faces.new([p[r + 1], p[r], s[r], s[r + 1]])], cells[r])
    pk._recalc(g.bm)
    # fascia scura sotto la falchetta (F2) e scritta del nome a prua
    for sgn in (-1, 1):
        xs = [x for x in st if x < 13.6]
        lo = [(x, sgn * (half_b(x) + 0.012), z_sheer(x) - 0.32) for x in xs]
        hi = [(x, sgn * (half_b(x) + 0.012), z_sheer(x) - 0.08) for x in xs]
        g.strip(lo, hi, "NAVY", out=(0, sgn, 0))
        if lod < 2:
            g.tube([(x, sgn * (half_b(x) + 0.03), z_sheer(x) - 0.02) for x in xs], 0.045, 4 if lod == 0 else 3, "SCURO")


def _name(g, x, y_sign, z, size, body, cell="NAVY"):
    if y_sign < 0:
        M = Matrix(((1, 0, 0, x), (0, 0, -1, 0), (0, 1, 0, z), (0, 0, 0, 1)))
    else:
        M = Matrix(((-1, 0, 0, x), (0, 0, 1, 0), (0, 1, 0, z), (0, 0, 0, 1)))
    return M


def _text_on_side(g, body, xc, y, z, size, cell, sgn):
    if sgn < 0:
        M = Matrix(((1, 0, 0, xc), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
    else:
        M = Matrix(((-1, 0, 0, xc), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))
    g.text(body, size, M, cell)


def _tuga(g, lod):
    x0, xa, xt = TUGA_X
    n = (8, 6, 4)[lod]
    plan = _plan(x0, xa, xt, TUGA_W, n)
    g.prism(plan, Z_COP, Z_SUP[0], "BIANCO", top=False)
    e = 0.015
    # fascia vetrata continua sui fianchi (montanti bianchi ogni ~1,9 m) e sull'arco di prua
    nwin = 9 if lod < 2 else 4
    span = (xa - 0.3) - (x0 + 0.6)
    for sgn in (-1, 1):
        for i in range(nwin):
            a = x0 + 0.6 + span * i / nwin + 0.07
            b = x0 + 0.6 + span * (i + 1) / nwin - 0.07
            y = sgn * (TUGA_W + e)
            g.quad([(a, y, 1.90), (b, y, 1.90), (b, y, 2.85), (a, y, 2.85)], "VETRO", out=(0, sgn, 0))
    for k in range(len(plan) - 1):
        (xa_, ya_), (xb_, yb_) = plan[k], plan[k + 1]
        if xa_ < xa - 1e-6 and xb_ < xa - 1e-6:
            continue
        if abs(ya_) > TUGA_W - 1e-6 and abs(yb_) > TUGA_W - 1e-6:
            continue
        mx, my = (xa_ + xb_) / 2 - xa, (ya_ + yb_) / 2
        L = math.hypot(mx, my) + 1e-9
        ox, oy = mx / L * e * 2, my / L * e * 2
        g.quad([(xa_ + ox, ya_ + oy, 1.90), (xb_ + ox, yb_ + oy, 1.90), (xb_ + ox, yb_ + oy, 2.85),
                (xa_ + ox, ya_ + oy, 2.85)], "VETRO", out=(mx, my, 0))
    # poppa della tuga: porta a due ante e due finestre
    g.quad([(x0 - e, 0.7, Z_COP), (x0 - e, -0.7, Z_COP), (x0 - e, -0.7, 2.6), (x0 - e, 0.7, 2.6)], "VETRO", out=(-1, 0, 0))
    for a, b in ((-2.6, -1.1), (1.1, 2.6)):
        g.quad([(x0 - e, b, 1.9), (x0 - e, a, 1.9), (x0 - e, a, 2.85), (x0 - e, b, 2.85)], "VETRO", out=(-1, 0, 0))
    # porte laterali verso il pontile (+Y) e sull'altro lato
    for sgn in (-1, 1):
        y = sgn * (TUGA_W + e * 2)
        g.quad([(-7.4, y, Z_COP), (-6.4, y, Z_COP), (-6.4, y, 2.75), (-7.4, y, 2.75)], "SCURO", out=(0, sgn, 0))


def _ponte_sup(g, lod):
    x0, xa, xt = SUP_X
    n = (10, 6, 4)[lod]
    plan = _plan(x0, xa, xt, SUP_W, n)
    g.prism(plan, Z_SUP[0], Z_SUP[1], "BIANCO", top=True, bot=True, cell_top="PONTE_GRIGIO")
    # pilastrini a poppa del solaio sporgente
    for sgn in (-1, 1):
        g.tube([(x0 + 0.25, sgn * (SUP_W - 0.25), Z_COP), (x0 + 0.25, sgn * (SUP_W - 0.25), Z_SUP[0])], 0.05,
               6 if lod == 0 else 4, "BIANCO", cap=False)
    # parapetti: pannello pieno basso (0,45) + corrimano a 1,0 m, varco per la scala a poppa sul lato -Y
    z = Z_SUP[1]
    t = 0.05
    sx0, sx1, sy0, sy1 = SCALA
    tx0 = TIM_X[0]
    sides_ = 6 if lod == 0 else 4
    for sgn in (-1, 1):
        y = sgn * (SUP_W - t / 2)
        g.box(x0, xa, y - t / 2, y + t / 2, z, z + 0.45, "BIANCO", faces=("yn", "yp", "top", "xn", "xp"))
        g.tube([(x0, y, z + 1.0), (xa, y, z + 1.0)], 0.03, sides_, "ACCIAIO")
        for xp in np.linspace(x0, xa, 8 if lod < 2 else 4):
            g.tube([(xp, y, z + 0.45), (xp, y, z + 1.0)], 0.022, 4, "ACCIAIO", cap=False)
        if lod < 2:
            g.tube([(x0, y, z + 0.72), (xa, y, z + 0.72)], 0.015, 4, "ACCIAIO")
    # poppa: parapetto con varco della scala (y sy0..sy1)
    for (ya, yb) in ((-SUP_W + t, sy0), (sy1, SUP_W - t)):
        g.box(x0, x0 + t, ya, yb, z, z + 0.45, "BIANCO", faces=("xn", "xp", "top", "yn", "yp"))
        g.tube([(x0 + t / 2, ya, z + 1.0), (x0 + t / 2, yb, z + 1.0)], 0.03, sides_, "ACCIAIO")
    # nome e compagnia sui pannelli dei parapetti
    for sgn in (-1, 1):
        _text_on_side(g, NOME_NAVE, -3.0, sgn * (SUP_W + 0.004), z + 0.13, 0.28, "NAVY", sgn)
    # zattere di salvataggio rosse sulla rastrelliera di poppa (F2)
    if lod < 2:
        for sgn in (-1, 1):
            y = sgn * (SUP_W - 0.55)
            g.box(RAFT_X[0] - 0.45, RAFT_X[-1] + 0.45, y - 0.32, y + 0.32, z, z + 0.30, "ACCIAIO",
                  faces=("top", "xn", "xp", "yn", "yp"))
            for xr in RAFT_X:
                M = Matrix.Translation((xr, y, z + 0.62)) @ Matrix.Rotation(math.radians(90), 4, "X") @ \
                    Matrix.Translation((0, 0, -0.55))
                g.lathe([(0.0, 0.0), (0.25, 0.02), (0.30, 0.10), (0.30, 1.00), (0.25, 1.08), (0.0, 1.10)],
                        10 if lod == 0 else 6, "ROSSO", mat=M, cap_top=False)
    else:
        for sgn in (-1, 1):
            y = sgn * (SUP_W - 0.55)
            g.box(RAFT_X[0] - 0.35, RAFT_X[-1] + 0.35, y - 0.30, y + 0.30, z, z + 0.92, "ROSSO")


def _timoniera(g, lod):
    x0, xa, xt = TIM_X
    n = (8, 6, 4)[lod]
    plan = _plan(x0, xa, xt, TIM_W, n)
    z0 = Z_SUP[1]
    g.prism(plan, z0, Z_TIM, "BIANCO", top=False)
    # fascia vetrata: fianchi e prua
    e = 0.015
    for sgn in (-1, 1):
        y = sgn * (TIM_W + e)
        g.quad([(x0 + 1.4, y, 4.20), (xa, y, 4.20), (xa, y, 4.95), (x0 + 1.4, y, 4.95)], "VETRO", out=(0, sgn, 0))
        g.quad([(x0 + 0.3, y, z0), (x0 + 1.1, y, z0), (x0 + 1.1, y, 4.95), (x0 + 0.3, y, 4.95)], "SCURO", out=(0, sgn, 0))
        # salvagente rosso sul fianco (F2)
        if lod < 2:
            M = Matrix.Translation((x0 + 2.4, sgn * (TIM_W + 0.06), 3.85)) @ Matrix.Rotation(math.radians(90), 4, "X")
            g.torus(M, 0.27, 0.07, 12 if lod == 0 else 8, 5 if lod == 0 else 4, "ROSSO")
    for k in range(len(plan) - 1):
        (xa_, ya_), (xb_, yb_) = plan[k], plan[k + 1]
        if xa_ < xa - 1e-6 and xb_ < xa - 1e-6:
            continue
        if abs(ya_) > TIM_W - 1e-6 and abs(yb_) > TIM_W - 1e-6:
            continue
        mx, my = (xa_ + xb_) / 2 - xa, (ya_ + yb_) / 2
        L = math.hypot(mx, my) + 1e-9
        ox, oy = mx / L * e * 2, my / L * e * 2
        g.quad([(xa_ + ox, ya_ + oy, 4.20), (xb_ + ox, yb_ + oy, 4.20), (xb_ + ox, yb_ + oy, 4.95),
                (xa_ + ox, ya_ + oy, 4.95)], "VETRO", out=(mx, my, 0))
    g.quad([(x0 - e, 1.2, 4.2), (x0 - e, -1.2, 4.2), (x0 - e, -1.2, 4.95), (x0 - e, 1.2, 4.95)], "VETRO", out=(-1, 0, 0))
    # tetto con sporto
    roof = _plan(x0 - 0.2, xa, xt + 0.25, TIM_W + 0.25, n)
    g.prism(roof, Z_TIM, Z_TIM + 0.12, "BIANCO", top=True, bot=True)
    # albero con crocetta, radar, fanale e bandierina tricolore (pubblica)
    zr = Z_TIM + 0.12
    if lod < 2:
        mx_ = x0 + 1.2
        g.tube([(mx_, 0, zr), (mx_, 0, zr + 3.4)], 0.06, 6 if lod == 0 else 4, "BIANCO")
        g.box(mx_ - 0.05, mx_ + 0.05, -0.7, 0.7, zr + 2.4, zr + 2.47, "BIANCO")
        g.box(mx_ - 0.4, mx_ + 0.6, -0.08, 0.08, zr + 1.2, zr + 1.28, "SCURO")      # antenna radar
        g.box(mx_ - 0.06, mx_ + 0.06, -0.06, 0.06, zr + 3.4, zr + 3.55, "LUCE")
        for o in (1, -1):
            g.quad([(mx_ - 0.02, 0.003 * o, zr + 2.75), (mx_ - 0.62, 0.003 * o, zr + 2.75), (mx_ - 0.62, 0.003 * o, zr + 3.15),
                    (mx_ - 0.02, 0.003 * o, zr + 3.15)], "TRICOL", out=(0, o, 0))
    else:
        g.tube([(x0 + 1.2, 0, zr), (x0 + 1.2, 0, zr + 3.4)], 0.06, 3, "BIANCO")
        g.box(x0 + 1.14, x0 + 1.26, -0.06, 0.06, zr + 3.4, zr + 3.55, "LUCE")


def _battagliola(g, pts, lod, h=1.0):
    sides = 6 if lod == 0 else 4
    g.tube([(p[0], p[1], p[2] + h) for p in pts], 0.03, sides, "ACCIAIO")
    if lod < 2:
        g.tube([(p[0], p[1], p[2] + h / 2) for p in pts], 0.015, 4, "ACCIAIO")
    for p in pts:
        g.tube([p, (p[0], p[1], p[2] + h)], 0.022, 4, "ACCIAIO", cap=False)


def _rails(g, lod):
    xs = [TUGA_X[2] + 0.2, 11.2, 12.2, 13.0, 13.6]
    for sgn in (-1, 1):
        _battagliola(g, [(x, sgn * max(half_b(x) - 0.08, 0.05), z_sheer(x)) for x in xs], lod)
    xa, xb = X_ST + 0.1, TUGA_X[0] - 0.1
    yb = half_b(-12.0) - 0.08
    _battagliola(g, [(xb, -yb, Z_COP), (xa, -yb + 0.05, Z_COP)], lod)
    _battagliola(g, [(xa, -yb + 0.05, Z_COP), (xa, 0.0, Z_COP), (xa, yb - 0.05, Z_COP)], lod)
    _battagliola(g, [(xa, yb - 0.05, Z_COP), (VARCO[0], yb, Z_COP)], lod)
    _battagliola(g, [(VARCO[1], yb, Z_COP), (xb, yb, Z_COP)], lod)


def _scala(g, lod):
    x0, x1, y0, y1 = SCALA
    z0, z1 = Z_COP, Z_SUP[1]
    n = 11 if lod < 2 else 0
    for i in range(n):
        xa = x0 + (x1 - x0) * i / n
        za = z0 + (z1 - z0) * (i + 1) / n
        g.box(xa, xa + (x1 - x0) / n + 0.02, y0 + 0.05, y1 - 0.05, za - 0.05, za, "PONTE_GRIGIO", faces=("top", "xn", "xp"))
    for y in (y0, y1 - 0.05):
        g.hull([(x0, y, z0), (x0 + 0.25, y, z0), (x1, y, z1 + 0.05), (x1, y, z1 - 0.3),
                (x0, y + 0.05, z0), (x0 + 0.25, y + 0.05, z0), (x1, y + 0.05, z1 + 0.05), (x1, y + 0.05, z1 - 0.3)], "BIANCO")
    if n == 0:
        g.quad([(x0, y0, z0), (x0, y1, z0), (x1, y1, z1), (x1, y0, z1)], "PONTE_GRIGIO", out=(-1, 0, 1))
    for y in (y0, y1):
        g.tube([(x0, y, z0 + 0.9), (x1, y, z1 + 0.9)], 0.025, 4, "ACCIAIO")


def _accessori(g, lod):
    if lod == 2:   # solo i parabordi (definiscono la larghezza fuori tutto)
        for sgn in (-1, 1):
            for x in (-9.0, 1.0):
                g.lathe([(0.0, 0.20), (0.13, 0.40), (0.13, 0.75), (0.0, 0.95)], 4, "BIANCO",
                        mat=Matrix.Translation((x, sgn * (HB + 0.14), 0.0)), cap_top=False)
        return
    for sgn in (-1, 1):
        for x in (-9.0, -4.0, 1.0, 6.0):
            y = sgn * (HB + 0.14)
            g.lathe([(0.0, 0.20), (0.11, 0.25), (0.13, 0.40), (0.13, 0.75), (0.11, 0.90), (0.0, 0.95)],
                    8 if lod == 0 else 5, "BIANCO", mat=Matrix.Translation((x, y, 0.0)), cap_top=False)
            g.tube([(x, y, 0.95), (x, sgn * (HB - 0.05), z_sheer(x) + 0.02)], 0.012, 3, "SCURO", cap=False)
    for x in (-13.2, 12.6):
        for sgn in (-1, 1):
            g.lathe([(0.12, 0.0), (0.09, 0.05), (0.07, 0.25), (0.11, 0.28), (0.11, 0.32), (0.0, 0.33)],
                    8 if lod == 0 else 5, "SCURO", mat=Matrix.Translation((x, sgn * (half_b(x) - 0.4), z_sheer(x))))
    # nome sulle murate (tratto dritto) e fila di oblo' tondi (indicazione dell'utente)
    for sgn in (-1, 1):
        _text_on_side(g, NOME_NAVE, 2.9, sgn * (HB + 0.02), 0.45, 0.30, "NAVY", sgn)
        for k in range(8):
            x = -11.0 + 1.4 * k
            y = sgn * (half_b(x) + 0.012)
            ring = [(x + 0.13 * math.cos(2 * math.pi * j / 8), y, 0.55 + 0.13 * math.sin(2 * math.pi * j / 8))
                    for j in range(8)]

            def fn(bm, ring=ring, sgn=sgn):
                f = bm.faces.new([bm.verts.new(p) for p in ring])
                f.normal_update()
                if f.normal.y * sgn < 0:
                    f.normal_flip()
            g.new_faces(fn, "OBLO")


def build_traghetto(coll, lod=0, name="SM_Morin_Traghetto_v2"):
    g = G()
    _hull(g, lod)
    _tuga(g, lod)
    _ponte_sup(g, lod)
    _timoniera(g, lod)
    _rails(g, lod)
    _scala(g, lod)
    _accessori(g, lod)
    return g.finish(name + _sfx(lod), coll, smooth=35.0)


def ucx_traghetto(coll, name="SM_Morin_Traghetto_v2"):
    hull_pts = []
    for x in STATIONS:
        for y, z in _section(x):
            hull_pts += [Vector((x, -y, z)), Vector((x, y, z))]
    pk._ucx_hull(name, 0, hull_pts, coll)
    i = 1
    for plan, z0, z1 in ((_plan(*TUGA_X, TUGA_W, 6), Z_COP, Z_SUP[0]), (_plan(*SUP_X, SUP_W, 6), Z_SUP[0], Z_SUP[1]),
                         (_plan(TIM_X[0] - 0.2, TIM_X[1], TIM_X[2] + 0.25, TIM_W + 0.25, 6), Z_SUP[1], Z_TIM + 0.12)):
        pk._ucx_hull(name, i, [Vector((x, y, z)) for x, y in plan for z in (z0, z1)], coll)
        i += 1
    x0, xa = SUP_X[0], SUP_X[1]
    z = Z_SUP[1]
    t = 0.06
    sy0, sy1 = SCALA[2], SCALA[3]
    boxes = [(x0, xa, -SUP_W, -SUP_W + t, z, z + 1.03), (x0, xa, SUP_W - t, SUP_W, z, z + 1.03),
             (x0, x0 + t, -SUP_W, sy0, z, z + 1.03), (x0, x0 + t, sy1, SUP_W, z, z + 1.03)]
    for sgn in (-1, 1):
        y = sgn * (SUP_W - 0.55)
        boxes.append((RAFT_X[0] - 0.45, RAFT_X[-1] + 0.45, y - 0.32, y + 0.32, z, z + 0.92))
    yb2 = half_b(-12.0) - 0.08
    boxes += [(X_ST + 0.05, TUGA_X[0] - 0.1, -yb2 - 0.03, -yb2 + 0.03, Z_COP, Z_COP + 1.0),
              (X_ST + 0.05, X_ST + 0.15, -yb2, yb2, Z_COP, Z_COP + 1.0),
              (X_ST + 0.05, VARCO[0], yb2 - 0.03, yb2 + 0.03, Z_COP, Z_COP + 1.0),
              (VARCO[1], TUGA_X[0] - 0.1, yb2 - 0.03, yb2 + 0.03, Z_COP, Z_COP + 1.0)]
    pk._ucx(name, boxes, coll, start=i)
    i += len(boxes)
    x0s, x1s, y0s, y1s = SCALA
    pk._ucx_hull(name, i, [Vector(p) for p in [(x0s, y0s, Z_COP), (x0s, y1s, Z_COP), (x1s, y0s, z), (x1s, y1s, z),
                                               (x1s, y0s, Z_COP), (x1s, y1s, Z_COP)]], coll)
    i += 1
    for sgn in (-1, 1):
        for xa_, xb_ in ((TUGA_X[2] + 0.2, 12.2), (12.2, 13.6)):
            pts = []
            for x in (xa_, xb_):
                y = sgn * max(half_b(x) - 0.08, 0.05)
                for dy in (0.0, -sgn * 0.05):
                    pts += [Vector((x, y + dy, z_sheer(x))), Vector((x, y + dy, z_sheer(x) + 1.0))]
            pk._ucx_hull(name, i, pts, coll)
            i += 1
    return i


# =================================================================================================================
# build, verifiche, CSV, contesto, export
# =================================================================================================================
ASSETS = ["SM_Morin_Biglietteria_v2", "SM_Morin_PontileImbarco_v2", "SM_Morin_Traghetto_v2"]
BUILDERS = {"SM_Morin_Biglietteria_v2": build_biglietteria, "SM_Morin_PontileImbarco_v2": build_pontile,
            "SM_Morin_Traghetto_v2": build_traghetto}
UCX = {"SM_Morin_Biglietteria_v2": ucx_biglietteria, "SM_Morin_PontileImbarco_v2": ucx_pontile,
       "SM_Morin_Traghetto_v2": ucx_traghetto}


def build_all(lod_target=(1.0, 0.5, 0.15)):
    coll = pk._coll(KIT)
    for o in list(coll.objects):
        if o.name.startswith("UCX_"):
            bpy.data.objects.remove(o)       # UCX rigenerati dallo script (oggetti generati, nessun dato utente)
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
                while av.bbox_dev(o0, o) > 0.019:   # sagoma entro il 2 %: si decima meno, al limite LOD ricostruito
                    o = BUILDERS[nm](coll, lod)
                    ratio *= 1.3
                    if ratio >= 0.95:
                        break
                    o = mi._decimate(o, ratio, o.name, coll)
            objs.append(o)
        UCX[nm](coll)
        if nm != "SM_Morin_Traghetto_v2":
            for u in [u for u in coll.objects if u.name.startswith(f"UCX_{nm}_")]:
                shear_obj(u)
        rep[nm] = [pk.tri_count(o) for o in objs] + [tuple(round(d, 2) for d in o0.dimensions)]
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
        zmin = -0.3 if "Traghetto" not in nm else -0.2
        hits, back, bad = av.ray_test(o0, zmin=zmin, skip_mats=("Rete",))
        nucx = len([o for o in bpy.data.objects if o.name.startswith(f"UCX_{nm}_")])
        res[nm] = dict(tri=[pk.tri_count(bpy.data.objects[nm + _sfx(l)]) for l in range(3)], bbox_dev_pct=devs,
                       ray=(back, hits), bad_faces=bad[:12], ucx=nucx, dim=tuple(round(d, 2) for d in o0.dimensions))
    return res


# ---- posa -----------------------------------------------------------------------------------------------------------
PONT_ORIG = (71.7, mi.ciglio_y(71.7), 0.0)
TRAG_POS = (76.65, 64.5, -1.0)              # lato EST del pontile (T1, T2), parallelo all asse OSM inclinato
TRAG_ROTZ = 90.0 - math.degrees(math.atan(K_ASSE))   # 88,18: prua (+X locale) verso la banchina


def layout():
    ox, oy, oz = PONT_ORIG
    return [("SM_Morin_PontileImbarco_v2", "Pontile_Imbarco_v2", ox, oy, oz, None),
            ("SM_Morin_Biglietteria_v2", "Biglietteria_v2", ox, oy, oz, None),
            ("SM_Morin_Traghetto_v2", "Traghetto_v2", *TRAG_POS, TRAG_ROTZ)]


def write_csv(path="exports/imbarco/imbarco_posizioni_v2.csv"):
    lines = ["asset,nome,x,y,z,yaw,pitch,roll"]
    for a, n, x, y, z, rz in layout():
        yaw = mi.YAW_BANCHINA if rz is None else -rz
        lines.append(f"{a},{n},{x * 100:.2f},{-y * 100:.2f},{z * 100:.2f},{yaw:.4f},0.0,0.0")
    with open(f"{PROJ}/{path}", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return lines


def build_context():
    coll = pk._coll(CTX)
    for a, n, x, y, z, rz in layout():
        on = f"IMB2_{n}"
        o = bpy.data.objects.get(on)
        if o is None:
            o = bpy.data.objects.new(on, bpy.data.objects[a].data)
            coll.objects.link(o)
        o.data = bpy.data.objects[a].data
        o.location = (x, y, z)
        o.rotation_euler = (0, 0, math.radians(-mi.YAW_BANCHINA if rz is None else rz))
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
