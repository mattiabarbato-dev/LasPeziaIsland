"""morin_fondale.py — fondale delle colline del golfo e della citta (v1, 2026-11-19).

Scheda: ref/fondale.md (§7 proposta tecnica), dati ref/dem/ (Copernicus DEM GLO-30 DSM, CORINE 2018, OSM).
Sorgente: blender/arte_fondale.blend. Coordinate di progetto (CLAUDE.md §3): metri, X lungo la passeggiata
(azimut 41,3 gradi), Y verso la citta, Z 0 = banchina = quota s.l.m. - 1,5 m [S].

Uso (dentro blender/arte_fondale.blend, via MCP o console):
    import sys, importlib
    p = r"C:/Users/matti/Documents/LaSpeziaFortnite/LaSpezia-Fortnite/blender/scripts"
    if p not in sys.path: sys.path.append(p)
    import morin_fondale as F; importlib.reload(F)
    F.build_all()                 # terreno (8 settori x LOD0/1/2), tenda, citta, texture, materiali
    F.export_all()                # FBX in exports/fondale/ (non sovrascrive se overwrite=False)

Parametri principali in P (dizionario). Per avvicinare l'anello lontano senza cambiare gli angoli visti dalla
partenza: P["warp_r0"] (m) e P["warp_k"] (fattore): ogni vertice a distanza orizzontale d > r0 dall'occhio va a
d' = r0 + k (d - r0) e la sua quota relativa all'occhio viene scalata di d'/d (omotetia radiale monotona centrata
sull'occhio: conserva azimut ed elevazione dalla partenza e l'ordine di occlusione lungo ogni raggio).
k = 1 (default) = scala reale. La tenda segue la stessa legge.

Terreno: triangolazione RTIN (stile "Martini") sull'intera griglia 30 m, con errore ammesso funzione della distanza
dalla partenza (tol_m), lato minimo funzione della distanza (minleg_m), vertici di cresta (profili d'orizzonte dei
4 punti di vista) sempre presenti, costa e bordi raffinati. Una sola triangolazione per LOD, poi tagliata in
settori di 45 gradi (azimut dalla partenza): dentro un LOD i bordi dei settori coincidono (niente fessure).
Mare: celle DEM a quota <= 0,3 m portate a -1,0 m s.l.m. (Z -2,5): la costa scende sotto l'acqua di gioco (Z -1);
i triangoli tutti di mare vengono eliminati. Escluso il rettangolo del blockout (fondale + blocco giocabile).
Anello A (< 1,5 km): suolo = minimo 5x5 del DSM sulle sole celle di terra + media 3x3 (tetti e chiome tolti),
raccordo lineare col DSM fra 1,2 e 1,6 km. Edifici OSM (footprint) estrusi su questo suolo.
UV del terreno: polari centrate sulla partenza (u = azimut, v = log della distanza): densita di texel quasi
costante sullo schermo. Texture 1024 per settore dipinta da CORINE + quota + rumore + case sparse.
"""
import json
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

PROJ = r"C:/Users/matti/Documents/LaSpeziaFortnite/LaSpezia-Fortnite"
DEM = PROJ + "/ref/dem"
TEXDIR = PROJ + "/blender/textures/fondale"
EXPDIR = PROJ + "/exports/fondale"
OSM_BUILDINGS = None  # percorso del JSON Overpass degli edifici (impostato da build_city)

# ------------------------------------------------------------------------------------------------------------
# Parametri
# ------------------------------------------------------------------------------------------------------------
P = dict(
    spawn=(240.0, 84.5),          # partenza (m, progetto)
    eye_z=1.8,                    # occhi: Z Blender (3,3 m s.l.m. - 1,5)
    z_off=-1.5,                   # Z = quota s.l.m. + z_off
    sea_h=0.3,                    # celle <= sea_h = mare
    sea_floor_h=-8.5,             # quota assegnata al mare (s.l.m.) -> Z -10: gonna sotto la SkyCubeGroundMesh (UE Z -1000)
    r_terr=9750.0,                # raggio esterno del terreno dalla partenza
    ringA_blend=(1200.0, 1600.0), # raccordo suolo lisciato -> DSM
    excl_rect=(-166.0, 332.0, -305.0, 302.0),  # Xmin, Xmax, Ymin, Ymax: blockout fondale + blocco giocabile
    dsm_smooth_passes=1,
    tol_near=1.0,                 # errore ammesso (m) entro 1,5 km
    tol_B=2.0,                    # 1,5-5 km (richiesta: <= 3 m; 2 m sulle celle visibili, budget permettendo)
    tol_far_slope=0.0025,         # oltre 5 km: 3 m + 2,5 m/km (15,5 m a 10 km ~ 1 pixel a 1080p/90 gradi)
    tol_hidden_mult=4.0,          # celle non visibili dalla partenza (maschera dilatata): tolleranza x4
    vis_dilate=2,
    n_sectors=8,
    sector_offset=-22.5,          # settore 0 = N (337,5..22,5)
    tol_mult=(1.0, 2.0, 5.0),     # moltiplicatore della tolleranza per LOD0/1/2
    leg_mult=(1.0, 1.4, 2.5),     # moltiplicatore del lato minimo per LOD0/1/2
    tenda_r=13000.0,              # raggio della tenda dei crinali lontani
    tenda_step=(1.0, 2.0, 4.0),   # passo in gradi per LOD0/1/2
    warp_r0=5000.0,
    warp_k=1.0,                   # 1 = scala reale
    tex_size=1024,
    uv_margin_deg=10.0,
    uv_d0=1500.0,                 # v = log((d+d0)/(dmin+d0)) / log((dmax+d0)/(dmin+d0))
    uv_dmin=60.0,
    seed=20261119,
    city_r=(250.0, 1500.0),       # anello A degli edifici (distanza dalla partenza)
    city_chunk_tris=5000,
)

SECTOR_NAMES = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
AZ_X = math.radians(41.3)
SA, CA = math.sin(AZ_X), math.cos(AZ_X)
LAT0, LON0 = 44.1016154, 9.8252769

# Colori base CORINE (sRGB 0-255) da ref/fondale.md §5, completati [S]
CLC_RGB = {
    0: (60, 82, 50), 111: (176, 160, 142), 112: (168, 150, 124), 121: (150, 148, 142), 122: (128, 126, 122),
    123: (150, 148, 142), 132: (140, 130, 110), 142: (90, 110, 64), 211: (104, 110, 68), 221: (92, 102, 62),
    223: (90, 102, 68), 242: (80, 98, 58), 243: (74, 94, 54), 311: (62, 86, 48), 312: (48, 70, 44),
    313: (55, 78, 46), 323: (88, 98, 60), 324: (78, 92, 54), 331: (190, 180, 150), 411: (90, 100, 70),
    511: (70, 90, 80), 523: (46, 66, 70),
}
FOREST = (0, 311, 312, 313, 323, 324)
# densita di case dipinte (case per km2) per classe, solo sotto ~300 m s.l.m.
HOUSE_DENS = {112: 700, 111: 900, 242: 160, 243: 110, 221: 60, 223: 70, 211: 40, 142: 40, 324: 12, 313: 6, 311: 4}
HOUSE_COL = [(232, 222, 196), (226, 196, 168), (214, 170, 120), (222, 196, 132), (236, 232, 222), (210, 160, 140)]
ROOF_COL = (152, 84, 62)


# ------------------------------------------------------------------------------------------------------------
# Utilita di coordinate
# ------------------------------------------------------------------------------------------------------------
def xy_to_az(dx, dy):
    """Azimut geografico (gradi, da N in senso orario) di un vettore in coordinate di progetto."""
    E = dx * SA - dy * CA
    N = dx * CA + dy * SA
    return (np.degrees(np.arctan2(E, N)) + 360.0) % 360.0


def az_to_dxdy(az_deg, d):
    a = np.radians(az_deg)
    E, N = d * np.sin(a), d * np.cos(a)
    return E * SA + N * CA, -E * CA + N * SA


def ll_to_xy(lat, lon):
    N = (lat - LAT0) * 111114.2
    E = (lon - LON0) * 80069.2
    return E * SA + N * CA, -E * CA + N * SA


def warp_points(V):
    """Omotetia radiale attorno all'occhio (vedi docstring). V: array (n,3) in metri. Restituisce una copia."""
    k, r0 = P["warp_k"], P["warp_r0"]
    V = np.array(V, dtype=np.float64)
    if abs(k - 1.0) < 1e-9:
        return V
    sx, sy = P["spawn"]
    dx, dy = V[:, 0] - sx, V[:, 1] - sy
    d = np.hypot(dx, dy)
    dn = np.where(d > r0, r0 + k * (d - r0), d)
    f = np.where(d > 1e-6, dn / np.maximum(d, 1e-6), 1.0)
    V[:, 0] = sx + dx * f
    V[:, 1] = sy + dy * f
    V[:, 2] = P["eye_z"] + (V[:, 2] - P["eye_z"]) * f
    return V


# ------------------------------------------------------------------------------------------------------------
# Dati e campi
# ------------------------------------------------------------------------------------------------------------
_C = {}


def grid_xy(n=669):
    j = np.arange(n)
    X = -10020.0 + 30.0 * j
    Y = 10020.0 - 30.0 * j
    return X, Y  # X per colonna, Y per riga


def _shift_stack(a, r, fill):
    n0, n1 = a.shape
    p = np.pad(a, r, mode="constant", constant_values=fill)
    return [p[r + dy:r + dy + n0, r + dx:r + dx + n1] for dy in range(-r, r + 1) for dx in range(-r, r + 1)]


def _remove_small_islands(land, min_cells=5):
    """Toglie le isole di terra con meno di min_cells celle (barche, pontili isolati nel DSM)."""
    n0, n1 = land.shape
    lab = np.zeros(land.shape, np.int32)
    out = land.copy()
    cur = 0
    ys, xs = np.nonzero(land)
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]:
            continue
        cur += 1
        stack = [(y0, x0)]
        lab[y0, x0] = cur
        comp = []
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            if len(comp) > min_cells:  # componente grande: basta, la marco e proseguo senza raccogliere
                pass
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < n0 and 0 <= xx < n1 and land[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = cur
                    stack.append((yy, xx))
        if len(comp) < min_cells:
            for y, x in comp:
                out[y, x] = False
    return out


def fields():
    """Campi sulla griglia 669x669 (30 m): h (s.l.m., suolo lavorato), land, clc, dist dalla partenza."""
    if "h" in _C:
        return _C
    h = np.load(DEM + "/morin_local_30m.npy").astype(np.float64)
    clc = np.load(DEM + "/morin_local_30m_clc.npy").astype(np.int32)
    land = h > P["sea_h"]
    land = _remove_small_islands(land, 5)
    X, Y = grid_xy(h.shape[0])
    XX, YY = np.meshgrid(X, Y)
    sx, sy = P["spawn"]
    dist = np.hypot(XX - sx, YY - sy)
    # suolo lisciato (anello A): minimo 5x5 sulle sole celle di terra, poi media 3x3 normalizzata
    hl = np.where(land, h, np.inf)
    mn = np.min(np.stack(_shift_stack(hl, 2, np.inf)), axis=0)
    mn = np.where(np.isfinite(mn), mn, h)
    mn = np.where(land, mn, 0.0)
    w = land.astype(np.float64)
    num = np.sum(np.stack(_shift_stack(mn * w, 1, 0.0)), axis=0)
    den = np.sum(np.stack(_shift_stack(w, 1, 0.0)), axis=0)
    ground = np.where(den > 0, num / np.maximum(den, 1e-9), 0.0)
    ground = np.maximum(ground, P["sea_h"] + 0.4)
    a0, a1 = P["ringA_blend"]
    t = np.clip((dist - a0) / (a1 - a0), 0.0, 1.0)
    # oltre l'anello A: filtro binomiale 3x3 sulle sole celle di terra (toglie il rumore delle chiome del DSM,
    # abbassa le cime di 0-3 m al 95 %, cioe < 0,06 gradi a 3 km) [scelta motivata nel report]
    hs = h
    for _ in range(P["dsm_smooth_passes"]):
        k = np.array([1.0, 2.0, 1.0])
        ww = np.zeros_like(hs)
        acc = np.zeros_like(hs)
        sh = _shift_stack(hs * land, 1, 0.0)
        sw = _shift_stack(land.astype(np.float64), 1, 0.0)
        for i, (a_, b_) in enumerate(zip(sh, sw)):
            wk = k[i // 3] * k[i % 3]
            acc += wk * a_
            ww += wk * b_
        hs = np.where(land, acc / np.maximum(ww, 1e-9), h)
    hw = np.where(land, t * hs + (1 - t) * ground, P["sea_floor_h"])
    _C.update(h_raw=h, h=hw, ground=np.where(land, ground, P["sea_floor_h"]), land=land, clc=clc, XX=XX, YY=YY,
              dist=dist)
    return _C


def sample_bilinear(arr, X, Y):
    """Campiona un campo della griglia 669 in (X, Y) di progetto (array)."""
    n = arr.shape[0]
    c = (np.asarray(X) + 10020.0) / 30.0
    r = (10020.0 - np.asarray(Y)) / 30.0
    c = np.clip(c, 0, n - 1.001)
    r = np.clip(r, 0, n - 1.001)
    c0 = np.floor(c).astype(np.int64)
    r0 = np.floor(r).astype(np.int64)
    fc, fr = c - c0, r - r0
    a = arr[r0, c0] * (1 - fc) + arr[r0, c0 + 1] * fc
    b = arr[r0 + 1, c0] * (1 - fc) + arr[r0 + 1, c0 + 1] * fc
    return a * (1 - fr) + b * fr


def sample_nearest(arr, X, Y):
    n = arr.shape[0]
    c = np.clip(np.rint((np.asarray(X) + 10020.0) / 30.0).astype(np.int64), 0, n - 1)
    r = np.clip(np.rint((10020.0 - np.asarray(Y)) / 30.0).astype(np.int64), 0, n - 1)
    return arr[r, c]


def ground_z(X, Y):
    """Z Blender del suolo lavorato (stesso campo del terreno, prima del warp)."""
    f = fields()
    return sample_bilinear(f["h"], X, Y) + P["z_off"]


# ------------------------------------------------------------------------------------------------------------
# RTIN (Martini) vettorializzato
# ------------------------------------------------------------------------------------------------------------
NPAD = 1025


def _padded():
    f = fields()
    n = f["h"].shape[0]
    H = np.full((NPAD, NPAD), P["sea_floor_h"], np.float64)
    H[:n, :n] = f["h"]
    L = np.zeros((NPAD, NPAD), bool)
    L[:n, :n] = f["land"]
    return H, L


def rtin_tree():
    """Pre-calcolo una tantum: errore locale per vertice, livello del vertice, flag costa."""
    if "E" in _C:
        return _C
    H, L = _padded()
    Hf, Lf = H.ravel(), L.ravel()
    S = NPAD - 1
    A = np.array([[S, S], [0, 0]], np.int32)
    B = np.array([[0, 0], [S, S]], np.int32)
    Cc = np.array([[0, S], [S, 0]], np.int32)
    E = np.zeros(NPAD * NPAD)
    MIX = np.zeros(NPAD * NPAD, bool)
    LEV = np.full(NPAD * NPAD, -1, np.int16)
    mids = []
    lev = 0
    while True:
        M2 = A + B
        if np.any(M2 % 2):
            break
        M = M2 // 2
        ia = A[:, 1] * NPAD + A[:, 0]
        ib = B[:, 1] * NPAD + B[:, 0]
        ic = Cc[:, 1] * NPAD + Cc[:, 0]
        im = M[:, 1] * NPAD + M[:, 0]
        err = np.abs(0.5 * (Hf[ia] + Hf[ib]) - Hf[im])
        np.maximum.at(E, im, err)
        mix = (Lf[ia] != Lf[ib]) | (Lf[ia] != Lf[ic]) | (Lf[ia] != Lf[im])
        np.logical_or.at(MIX, im, mix)
        LEV[im] = lev
        mids.append(im)
        # figli: (C, A, M) e (B, C, M)
        A, B, Cc = np.concatenate([Cc, B]), np.concatenate([A, Cc]), np.concatenate([M, M])
        lev += 1
    # lato (cateto) dei triangoli di ciascun livello: livello 0 = S celle, poi /sqrt2
    _C.update(E=E, MIX=MIX, LEV=LEV, mids=mids, nlev=lev)
    return _C


def visible_padded():
    """Maschera delle celle visibili dalla partenza (ref/dem, 255 = visibile), dilatata di P['vis_dilate'] celle
    per coprire anche gli altri punti di vista della passeggiata e del ponte."""
    if "vis" in _C:
        return _C["vis"]
    img = bpy.data.images.load(DEM + "/morin_local_30m_visibile_spawn.png", check_existing=True)
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    m = a.reshape(h, w, 4)[::-1, :, 0] > 0.5  # riga 0 = Y alto, come la griglia
    for _ in range(P["vis_dilate"]):
        m = np.any(np.stack(_shift_stack(m, 1, False)), axis=0)
    V = np.zeros((NPAD, NPAD), bool)
    V[:h, :w] = m
    _C["vis"] = V
    return V


def leg_of_level(lev):
    return 30.0 * (NPAD - 1) / (math.sqrt(2.0) ** lev)


def tol_m(d):
    """Errore verticale ammesso (m) in funzione della distanza dalla partenza [scelta motivata nel report]."""
    d = np.asarray(d, np.float64)
    a, b, slope = P["tol_near"], P["tol_B"], P["tol_far_slope"]
    return np.where(d <= 1500.0, a, np.where(d <= 5000.0, b, b + (d - 5000.0) * slope))


def minleg_m(d):
    """Lato minimo dei figli (m): 30 m fino a 5 km, 85 m (griglia 85-120 m) oltre."""
    d = np.asarray(d, np.float64)
    return np.where(d <= 5000.0, 29.0, 84.0)


def crest_vertices():
    """Indici (griglia padded) dei punti di cresta dei profili d'orizzonte (4 punti di vista, solo colline)."""
    idx = set()
    for name in ("spawn", "imbocco_ponte", "meta_blocco", "fine_passeggiata"):
        fn = f"{DEM}/orizzonte_{name}_colline.csv"
        with open(fn, encoding="utf-8") as fh:
            hdr = fh.readline().strip().split(",")
            for line in fh:
                r = dict(zip(hdr, line.strip().split(",")))
                if r.get("tipo") != "terra":
                    continue
                X, Y = ll_to_xy(float(r["lat"]), float(r["lon"]))
                c = int(round((X + 10020.0) / 30.0))
                rr = int(round((10020.0 - Y) / 30.0))
                if 0 <= c < 669 and 0 <= rr < 669:
                    idx.add(rr * NPAD + c)
    return np.array(sorted(idx), np.int64)


def triangulate(lod=0):
    """Triangolazione RTIN del LOD dato. Ritorna (tri indici griglia padded (n,3), statistiche)."""
    T = rtin_tree()
    E, MIX, LEV, mids, nlev = T["E"], T["MIX"], T["LEV"], T["mids"], T["nlev"]
    sx, sy = P["spawn"]
    allidx = np.arange(NPAD * NPAD)
    cx = allidx % NPAD
    ry = allidx // NPAD
    VX = -10020.0 + 30.0 * cx
    VY = 10020.0 - 30.0 * ry
    d = np.hypot(VX - sx, VY - sy)
    tm, lm = P["tol_mult"][lod], P["leg_mult"][lod]
    legs = np.array([leg_of_level(l) for l in range(nlev + 1)])
    child_leg = np.where(LEV >= 0, legs[np.clip(LEV + 1, 0, nlev)], 0.0)
    allowed = child_leg >= minleg_m(d) * lm
    vis = visible_padded().ravel()
    tol = tol_m(d) * tm * np.where(vis, 1.0, P["tol_hidden_mult"])
    score = np.where(allowed, E / tol, 0.0)
    # costa: raffina fino al lato minimo
    score = np.where(allowed & MIX, np.maximum(score, 2.0), score)
    # bande attorno al rettangolo escluso (60 m) e al cerchio esterno (150 m)
    x0, x1, y0, y1 = P["excl_rect"]
    band = 60.0 * lm
    in_big = (VX > x0 - band) & (VX < x1 + band) & (VY > y0 - band) & (VY < y1 + band)
    in_small = (VX > x0 + band) & (VX < x1 - band) & (VY > y0 + band) & (VY < y1 - band)
    score = np.where(allowed & in_big & ~in_small, np.maximum(score, 2.0), score)
    ring = np.abs(d - P["r_terr"]) < 150.0 * lm
    score = np.where(allowed & ring, np.maximum(score, 2.0), score)
    # creste (solo LOD0 e LOD1)
    if lod < 2:
        cv = crest_vertices()
        score[cv] = np.maximum(score[cv], 2.0)
    # niente split nel mare aperto lontano dalla costa: errore 0 gia lo garantisce
    # propagazione (dal livello piu fine al piu grossolano)
    s = score.copy()
    # ricostruisco i figli: per il livello l (n triangoli), i figli sono al livello l+1 agli indici i e n+i
    for l in range(nlev - 2, -1, -1):
        im = mids[l]
        ch = mids[l + 1]
        n = im.shape[0]
        cm = np.maximum(s[ch[:n]], s[ch[n:]])
        np.maximum.at(s, im, cm)
    # estrazione
    S = NPAD - 1
    A = np.array([[S, S], [0, 0]], np.int32)
    B = np.array([[0, 0], [S, S]], np.int32)
    Cc = np.array([[0, S], [S, 0]], np.int32)
    out = []
    for l in range(nlev):
        M2 = A + B
        M = M2 // 2
        im = M[:, 1] * NPAD + M[:, 0]
        split = s[im] > 1.0
        keep = ~split
        if keep.any():
            out.append(np.stack([A[keep], B[keep], Cc[keep]], axis=1))
        if not split.any():
            break
        A, B, Cc, M = A[split], B[split], Cc[split], M[split]
        A, B, Cc = np.concatenate([Cc, B]), np.concatenate([A, Cc]), np.concatenate([M, M])
    else:
        out.append(np.stack([A, B, Cc], axis=1))
    tri = np.concatenate(out)  # (n, 3, 2) x,y
    flat = tri[:, :, 1].astype(np.int64) * NPAD + tri[:, :, 0]
    return flat


def terrain_triangles(lod=0):
    """Triangoli filtrati (mare, rettangolo escluso, cerchio) con assegnazione al settore."""
    H, L = _padded()
    Hf, Lf = H.ravel(), L.ravel()
    tri = triangulate(lod)
    cx = tri % NPAD
    ry = tri // NPAD
    VX = -10020.0 + 30.0 * cx
    VY = 10020.0 - 30.0 * ry
    gx, gy = VX.mean(axis=1), VY.mean(axis=1)
    sx, sy = P["spawn"]
    dc = np.hypot(gx - sx, gy - sy)
    x0, x1, y0, y1 = P["excl_rect"]
    inrect = (gx > x0) & (gx < x1) & (gy > y0) & (gy < y1)
    allsea = ~(Lf[tri].any(axis=1))
    keep = ~inrect & ~allsea & (dc < P["r_terr"])
    tri = tri[keep]
    az = xy_to_az(gx[keep] - sx, gy[keep] - sy)
    ns = P["n_sectors"]
    width = 360.0 / ns
    sec = np.floor(((az - P["sector_offset"]) % 360.0) / width).astype(np.int64)
    return tri, sec


def sector_range(i):
    width = 360.0 / P["n_sectors"]
    a0 = P["sector_offset"] + i * width
    return a0, a0 + width


# ------------------------------------------------------------------------------------------------------------
# UV polari
# ------------------------------------------------------------------------------------------------------------
def uv_polar(X, Y, sector):
    sx, sy = P["spawn"]
    a0, a1 = sector_range(sector)
    m = P["uv_margin_deg"]
    az = xy_to_az(np.asarray(X) - sx, np.asarray(Y) - sy)
    rel = (az - (a0 - m)) % 360.0
    rel = np.where(rel > 270.0, rel - 360.0, rel)
    u = rel / (a1 - a0 + 2 * m)
    d = np.hypot(np.asarray(X) - sx, np.asarray(Y) - sy)
    d0, dmin, dmax = P["uv_d0"], P["uv_dmin"], P["r_terr"]
    v = np.log((d + d0) / (dmin + d0)) / math.log((dmax + d0) / (dmin + d0))
    return u, v


def uv_inverse(u, v, sector):
    """(u, v) -> (X, Y) di progetto, per dipingere le texture."""
    sx, sy = P["spawn"]
    a0, a1 = sector_range(sector)
    m = P["uv_margin_deg"]
    az = (a0 - m) + u * (a1 - a0 + 2 * m)
    d0, dmin, dmax = P["uv_d0"], P["uv_dmin"], P["r_terr"]
    d = (dmin + d0) * np.exp(v * math.log((dmax + d0) / (dmin + d0))) - d0
    dx, dy = az_to_dxdy(az, d)
    return sx + dx, sy + dy, d, az


# ------------------------------------------------------------------------------------------------------------
# Rumore
# ------------------------------------------------------------------------------------------------------------
def _noise_grids():
    if "noise" in _C:
        return _C["noise"]
    rng = np.random.default_rng(P["seed"])
    grids = []
    for cell in (400.0, 120.0, 40.0, 14.0):
        n = int(21000 / cell) + 3
        grids.append((cell, rng.random((n, n))))
    _C["noise"] = grids
    return grids


def noise(X, Y, weights=(0.45, 0.3, 0.17, 0.08)):
    out = 0.0
    for (cell, g), w in zip(_noise_grids(), weights):
        n = g.shape[0]
        c = (np.asarray(X) + 10500.0) / cell
        r = (np.asarray(Y) + 10500.0) / cell
        c = np.clip(c, 0, n - 1.001)
        r = np.clip(r, 0, n - 1.001)
        c0 = np.floor(c).astype(np.int64)
        r0 = np.floor(r).astype(np.int64)
        fc, fr = c - c0, r - r0
        fc = fc * fc * (3 - 2 * fc)
        fr = fr * fr * (3 - 2 * fr)
        a = g[r0, c0] * (1 - fc) + g[r0, c0 + 1] * fc
        b = g[r0 + 1, c0] * (1 - fc) + g[r0 + 1, c0 + 1] * fc
        out = out + w * (a * (1 - fr) + b * fr)
    return out / sum(weights)


# ------------------------------------------------------------------------------------------------------------
# Texture
# ------------------------------------------------------------------------------------------------------------
def _save_png(name, rgb, alpha=None):
    """rgb: (H, W, 3) float 0..1 sRGB, riga 0 = basso (convenzione Blender). Salva in TEXDIR e ritorna l'immagine."""
    os.makedirs(TEXDIR, exist_ok=True)
    Hh, Ww = rgb.shape[:2]
    img = bpy.data.images.get(name)
    if img is None or tuple(img.size) != (Ww, Hh):
        if img is not None:
            img.name = name + "_old"
        img = bpy.data.images.new(name, Ww, Hh, alpha=False)
    a = np.ones((Hh, Ww, 4), np.float32)
    a[..., :3] = np.clip(rgb, 0, 1)
    if alpha is not None:
        a[..., 3] = alpha
    img.pixels.foreach_set(a.ravel())
    path = f"{TEXDIR}/{name}.png"
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    img.filepath = path
    img.colorspace_settings.name = "sRGB"
    return img


def _houses_world():
    """Case sparse (punti mondo) dipinte nell'albedo: griglia jitterata 12 m, accettazione per classe e quota."""
    if "houses" in _C:
        return _C["houses"]
    f = fields()
    rng = np.random.default_rng(P["seed"] + 7)
    step = 12.0
    xs = np.arange(-10000, 10000, step)
    X, Y = np.meshgrid(xs, xs)
    X = X.ravel() + rng.uniform(-5, 5, X.size)
    Y = Y.ravel() + rng.uniform(-5, 5, Y.size)
    sx, sy = P["spawn"]
    d = np.hypot(X - sx, Y - sy)
    ok = (d > 1000.0) & (d < P["r_terr"])
    X, Y, d = X[ok], Y[ok], d[ok]
    clc = sample_nearest(f["clc"], X, Y)
    h = sample_bilinear(f["h_raw"], X, Y)
    land = sample_nearest(f["land"], X, Y)
    dens = np.zeros(X.size)
    for k, v in HOUSE_DENS.items():
        dens = np.where(clc == k, v, dens)
    # meno case in alto: piena densita fino a 180 m, zero a 320 m [S dalle foto]
    dens = dens * np.clip((320.0 - h) / 140.0, 0.0, 1.0)
    # raggruppamento a nuclei lungo le strade: modulazione con rumore
    dens = dens * np.clip(noise(X * 1.7 + 300, Y * 1.7 - 200) * 2.2 - 0.5, 0.0, 1.6)
    p = dens * (step * step) / 1e6
    acc = land & (rng.random(X.size) < p)
    col = rng.integers(0, len(HOUSE_COL), acc.sum())
    _C["houses"] = (X[acc], Y[acc], col)
    return _C["houses"]


def paint_sector(sector, size=None):
    """Albedo del settore (size x size) in UV polari."""
    size = size or P["tex_size"]
    f = fields()
    u = (np.arange(size) + 0.5) / size
    v = (np.arange(size) + 0.5) / size
    U, V = np.meshgrid(u, v)  # riga = v (riga 0 = basso)
    X, Y, d, az = uv_inverse(U, V, sector)
    # classe con bordi rotti dal rumore (spostamento +-45 m)
    jx = (noise(X + 777, Y - 333) - 0.5) * 90.0
    jy = (noise(X - 555, Y + 999) - 0.5) * 90.0
    clc = sample_nearest(f["clc"], X + jx, Y + jy)
    land = sample_nearest(f["land"], X, Y)
    clc = np.where(land & (clc == 523), 313, clc)
    h = sample_bilinear(f["h_raw"], X, Y)
    rgb = np.zeros(U.shape + (3,))
    for k, c in CLC_RGB.items():
        m = clc == k
        if m.any():
            rgb[m] = np.array(c) / 255.0
    unknown = ~np.isin(clc, list(CLC_RGB.keys()))
    rgb[unknown] = np.array(CLC_RGB[313]) / 255.0
    n1 = noise(X, Y)
    n2 = noise(X * 3.1 + 50, Y * 3.1 - 70)
    forest = np.isin(clc, FOREST)
    # chiome: macchie scure/chiare
    canopy = 0.78 + 0.42 * (0.6 * n2 + 0.4 * n1)
    rgb = np.where(forest[..., None], rgb * canopy[..., None], rgb)
    # zone agricole/terrazze: variazione e fasce lungo le curve di livello (periodo 12 m di quota)
    agri = np.isin(clc, (211, 221, 223, 242, 243))
    terr = 1.0 + 0.035 * np.sin(2 * math.pi * h / 12.0) * np.clip((300.0 - h) / 100.0, 0, 1)
    patch = 0.88 + 0.22 * n2
    rgb = np.where(agri[..., None], rgb * (terr * patch)[..., None], rgb)
    # alberi sparsi nelle zone agricole (macchie scure)
    dots = (noise(X * 6.0, Y * 6.0) > 0.62) & agri
    rgb = np.where(dots[..., None], rgb * 0.72, rgb)
    # urbano discontinuo: mescola giardini verdi
    urb = np.isin(clc, (112,))
    green = np.array(CLC_RGB[243]) / 255.0
    mixw = np.clip(n2 * 1.3 - 0.25, 0, 1)
    rgb = np.where(urb[..., None], rgb * (1 - mixw[..., None]) + green * mixw[..., None], rgb)
    # tinta per quota: in basso piu caldo/oliva, in alto piu scuro e freddo [S dalle foto]
    hb = np.clip(h / 600.0, 0, 1)[..., None]
    rgb = rgb * (1.04 - 0.12 * hb) + np.array([0.012, 0.010, -0.004]) * (1 - hb)
    # mare sotto l'acqua: blu-verde scuro (si vede solo come fascia sommersa)
    rgb = np.where(~land[..., None], np.array(CLC_RGB[523]) / 255.0, rgb)
    # case dipinte
    hx, hy, hc = _houses_world()
    hu, hv = uv_polar(hx, hy, sector)
    ok = (hu >= 0) & (hu < 1) & (hv >= 0) & (hv < 1)
    hx, hy, hc, hu, hv = hx[ok], hy[ok], hc[ok], hu[ok], hv[ok]
    if hx.size:
        sxp, syp = P["spawn"]
        hd = np.hypot(hx - sxp, hy - syp)
        a0, a1 = sector_range(sector)
        span = math.radians(a1 - a0 + 2 * P["uv_margin_deg"])
        m_per_px_u = hd * span / size
        d0, dmin, dmax = P["uv_d0"], P["uv_dmin"], P["r_terr"]
        m_per_px_v = (hd + d0) * math.log((dmax + d0) / (dmin + d0)) / size
        su = np.clip(np.rint(11.0 / m_per_px_u), 1, 4).astype(int)
        sv = np.clip(np.rint(11.0 / m_per_px_v), 1, 3).astype(int)
        pu = (hu * size).astype(int)
        pv = (hv * size).astype(int)
        cols = np.array(HOUSE_COL, float)[hc] / 255.0
        roof = np.array(ROOF_COL, float) / 255.0
        for dv in range(4):
            for du in range(4):
                m = (du < su) & (dv <= sv)
                if not m.any():
                    continue
                uu = np.clip(pu[m] + du, 0, size - 1)
                vv = np.clip(pv[m] + dv, 0, size - 1)
                is_roof = dv == sv[m]
                c = np.where(is_roof[:, None], roof, cols[m])
                rgb[vv, uu] = c
    return np.clip(rgb, 0, 1)


def paint_facade(size=1024):
    """Facciata generica neutra (da tingere col colore vertice): 4 piani x 4 finestre su 12 x 12,8 m. Ripetibile."""
    rng = np.random.default_rng(P["seed"] + 11)
    y, x = np.mgrid[0:size, 0:size]
    mx, my = 12.0 / size, 12.8 / size
    X, Y = x * mx, y * my  # metri, riga 0 = basso
    base = 0.86 + 0.06 * rng.random((size // 16 + 1, size // 16 + 1))[y // 16, x // 16]
    rgb = np.ones((size, size, 3)) * base[..., None]
    # zoccolo/marcapiano ogni piano (3,2 m): linea leggermente piu scura
    fy = Y % 3.2
    rgb[(fy < 0.18)] *= 0.86
    # finestre: 4 colonne (passo 3 m), apertura 1,1 x 1,5 m, con persiane verdi ai lati
    fx = X % 3.0
    win = (np.abs(fx - 1.5) < 0.55) & (fy > 0.9) & (fy < 2.4)
    shut = ((np.abs(fx - 1.5) >= 0.55) & (np.abs(fx - 1.5) < 0.95)) & (fy > 0.9) & (fy < 2.4)
    # meta delle finestre con persiane chiuse (casuale per cella)
    cell = (np.floor(X / 3.0) + 7 * np.floor(Y / 3.2)).astype(int)
    closed = (rng.random(64)[cell % 64] < 0.35)
    shutter = np.array([0.30, 0.40, 0.30])
    glass = np.array([0.13, 0.14, 0.16])
    rgb[shut & ~closed] = shutter
    rgb[win & closed] = shutter * 0.9
    rgb[win & ~closed] = glass
    # davanzale
    sill = (np.abs(fx - 1.5) < 0.62) & (fy > 0.82) & (fy <= 0.9)
    rgb[sill] = 0.95
    # cornicione in alto alla tessera (ogni 4 piani): banda chiara
    rgb[Y > 12.55] = 0.93
    # macchia per piccola zona uniforme per i tetti: angolo (0..8 px) intonaco puro -> UV dei tetti
    rgb[0:8, 0:8] = 0.9
    return np.clip(rgb, 0, 1)


def paint_tenda(w=1024, h=256):
    """Tenda dei crinali lontani: verde-azzurro di foschia, piu chiaro verso la cresta [S]."""
    y, x = np.mgrid[0:h, 0:w]
    t = y / (h - 1)  # 0 = base, 1 = cresta
    rng = np.random.default_rng(P["seed"] + 3)
    n = rng.random((h // 8 + 1, w // 8 + 1))[y // 8, x // 8]
    low = np.array([0.36, 0.42, 0.40])
    top = np.array([0.55, 0.62, 0.66])
    rgb = low * (1 - t[..., None]) + top * t[..., None]
    rgb *= (0.95 + 0.1 * n)[..., None]
    return np.clip(rgb, 0, 1)


def repaint_terrain_textures(sectors=None):
    """Ridipinge e salva le texture dei settori (le immagini esistenti vengono aggiornate in place)."""
    for s in (sectors if sectors is not None else range(P["n_sectors"])):
        _save_png(f"T_Fondale_Colline_{SECTOR_NAMES[s]}_D", paint_sector(s))


# ------------------------------------------------------------------------------------------------------------
# Materiali
# ------------------------------------------------------------------------------------------------------------
def _material(name, img, use_vcol=False, rough=0.92):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (-300, 0)
    out.location = (0, 0)
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.location = (-900, 100)
    tex.extension = "EXTEND" if not use_vcol else "REPEAT"
    if use_vcol:
        vc = nt.nodes.new("ShaderNodeVertexColor")
        vc.layer_name = "Col"
        vc.location = (-900, -200)
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.location = (-600, 0)
        nt.links.new(tex.outputs["Color"], mix.inputs[6])
        nt.links.new(vc.outputs["Color"], mix.inputs[7])
        nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    else:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    sp = bsdf.inputs.get("Specular IOR Level")
    if sp is not None:
        sp.default_value = 0.2
    return mat


# ------------------------------------------------------------------------------------------------------------
# Costruzione mesh
# ------------------------------------------------------------------------------------------------------------
def _coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def _mesh_object(name, verts, faces, coll, pivot, uvs=None, vcols=None, mat=None):
    """Crea/aggiorna l'oggetto `name`: dati relativi al pivot, oggetto posto al pivot (non cancella nulla:
    se esiste, sostituisce la sola mesh dati; la mesh vecchia resta orfana nel file finche non viene salvato)."""
    V = np.asarray(verts, np.float64) - np.array([pivot[0], pivot[1], 0.0])
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V))
    me.vertices.foreach_set("co", V.astype(np.float32).ravel())
    F = np.asarray(faces, np.int64)
    nl = F.size
    me.loops.add(nl)
    me.loops.foreach_set("vertex_index", F.ravel().astype(np.int32))
    me.polygons.add(len(F))
    me.polygons.foreach_set("loop_start", (np.arange(len(F)) * 3).astype(np.int32))
    me.update()
    if uvs is not None:
        uvl = me.uv_layers.new(name="UVMap")
        uvl.data.foreach_set("uv", np.asarray(uvs, np.float32)[F.ravel()].ravel())
    if vcols is not None:
        ca = me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
        cc = np.ones((nl, 4), np.float32)
        cc[:, :3] = np.asarray(vcols, np.float32)[F.ravel()]
        ca.data.foreach_set("color_srgb", cc.ravel())  # valori = byte sRGB del file (tinta moltiplicativa)
    if mat is not None:
        me.materials.append(mat)
    me.validate()
    obj = bpy.data.objects.get(name)
    if obj is None:
        obj = bpy.data.objects.new(name, me)
        coll.objects.link(obj)
    else:
        obj.data = me
    obj.location = (pivot[0], pivot[1], 0.0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    return obj


def _pivot(V):
    lo, hi = V.min(axis=0), V.max(axis=0)
    return (round(float((lo[0] + hi[0]) / 2), -1), round(float((lo[1] + hi[1]) / 2), -1))


def build_terrain(lods=(0, 1, 2), textures=True):
    H, L = _padded()
    Hf = H.ravel()
    coll = _coll("FONDALE_Terreno")
    report = {}
    imgs = {}
    for lod in lods:
        tri, sec = terrain_triangles(lod)
        for s in range(P["n_sectors"]):
            name = f"SM_Fondale_Colline_{SECTOR_NAMES[s]}" + ("" if lod == 0 else f"_LOD{lod}")
            t = tri[sec == s]
            if t.size == 0:
                continue
            uniq, inv = np.unique(t.ravel(), return_inverse=True)
            faces = inv.reshape(-1, 3)
            cx = uniq % NPAD
            ry = uniq // NPAD
            X = -10020.0 + 30.0 * cx
            Y = 10020.0 - 30.0 * ry
            Z = Hf[uniq] + P["z_off"]
            V = np.stack([X, Y, Z], axis=1)
            u, v = uv_polar(X, Y, s)
            uv = np.stack([u, v], axis=1)
            Vw = warp_points(V)
            # orientamento: normali verso l'alto
            a, b, c = Vw[faces[:, 0]], Vw[faces[:, 1]], Vw[faces[:, 2]]
            nz = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
            flip = nz < 0
            faces[flip] = faces[flip][:, [0, 2, 1]]
            if textures and s not in imgs:
                img = _save_png(f"T_Fondale_Colline_{SECTOR_NAMES[s]}_D", paint_sector(s))
                imgs[s] = img
            img = imgs.get(s) or bpy.data.images.get(f"T_Fondale_Colline_{SECTOR_NAMES[s]}_D")
            mat = _material(f"M_Fondale_Colline_{SECTOR_NAMES[s]}", img) if lod == 0 or \
                bpy.data.materials.get(f"M_Fondale_Colline_{SECTOR_NAMES[s]}") is None else \
                bpy.data.materials[f"M_Fondale_Colline_{SECTOR_NAMES[s]}"]
            # stesso pivot per LOD0/1/2 dello stesso settore (quello del LOD0)
            piv = _C.setdefault("pivots", {}).get(("terr", s)) if lod > 0 else _C.setdefault("pivots", {}).get("_none")
            if piv is None:
                piv = _pivot(Vw)
                _C["pivots"][("terr", s)] = piv
            obj = _mesh_object(name, Vw, faces, coll, piv, uvs=uv, mat=mat)
            if lod > 0:
                obj.hide_set(True)
                obj.hide_render = True
            dist = np.hypot(X - P["spawn"][0], Y - P["spawn"][1])
            report[name] = dict(tris=len(faces), pivot=piv, d_min=float(dist.min()), d_max=float(dist.max()),
                                bbox=(Vw.min(axis=0).round(1).tolist(), Vw.max(axis=0).round(1).tolist()))
    return report


# ------------------------------------------------------------------------------------------------------------
# Tenda dei crinali lontani
# ------------------------------------------------------------------------------------------------------------
def _profile(name="spawn"):
    rows = []
    with open(f"{DEM}/orizzonte_{name}_colline.csv", encoding="utf-8") as fh:
        hdr = fh.readline().strip().split(",")
        for line in fh:
            r = dict(zip(hdr, line.strip().split(",")))
            rows.append((float(r["azimut_deg"]), float(r["elev_deg"]), float(r["dist_m"]), r["tipo"]))
    return rows


def far_horizon(step=1.0):
    """Elevazione massima (gradi) per azimut del terreno OLTRE r_terr, vista dalla partenza: dal GeoTIFF
    cop30 (21,7 x 18,9 km, curvatura e rifrazione k = 0,13) e dai profili CSV quando la cresta e oltre r_terr
    (Appennino, Apuane, Monte Grosso). -1 = niente terra oltre il terreno modellato."""
    key = ("far", step)
    if key in _C:
        return _C[key]
    import struct
    fn = DEM + "/cop30_golfo_spezia_wgs84.tif"
    with open(fn, "rb") as fh:
        raw = fh.read()
    w, h = 972, 612
    a = np.frombuffer(raw, dtype="<f4", count=w * h, offset=8).reshape(h, w).astype(np.float64)
    lon = 9.70 + (np.arange(w) + 0.5) / 3600.0
    lat = 44.19 - (np.arange(h) + 0.5) / 3600.0
    LON, LAT = np.meshgrid(lon, lat)
    X, Y = ll_to_xy(LAT, LON)
    sx, sy = P["spawn"]
    d = np.hypot(X - sx, Y - sy)
    ok = (d > P["r_terr"]) & (a > 1.0)
    z = a[ok] + P["z_off"] - d[ok] ** 2 / (2 * 6371000.0) * (1 - 0.13)
    el = np.degrees(np.arctan2(z - P["eye_z"], d[ok]))
    az = xy_to_az(X[ok] - sx, Y[ok] - sy)
    nb = int(round(360 / step))
    b = np.floor(az / step).astype(int) % nb
    far = np.full(nb, -1.0)
    np.maximum.at(far, b, el)
    # dove il GeoTIFF non arriva oltre r_terr (N-NO) ma il terreno modellato finisce su terra: la tenda prosegue
    # il bordo (angolo delle celle di terra a r_terr - 400 m .. r_terr)
    f = fields()
    m = f["land"] & (f["dist"] > P["r_terr"] - 400) & (f["dist"] <= P["r_terr"])
    de = f["dist"][m]
    ze = f["h"][m] + P["z_off"] - de ** 2 / (2 * 6371000.0) * (1 - 0.13)
    ee = np.degrees(np.arctan2(ze - P["eye_z"], de))
    be = np.floor(xy_to_az(f["XX"][m] - sx, f["YY"][m] - sy) / step).astype(int) % nb
    edge = np.full(nb, -1.0)
    np.maximum.at(edge, be, ee)
    far = np.where(far < 0, edge, far)
    for az_, e, dist, t in _profile("spawn"):
        if t == "terra" and dist > P["r_terr"]:
            i = int(np.floor((az_ % 360) / step)) % nb
            far[i] = max(far[i], e)
    _C[key] = far
    return far


def build_tenda(lods=(0, 1, 2)):
    """Strip verticale a raggio tenda_r con la cresta all'angolo del terreno che sta OLTRE il terreno modellato
    (far_horizon): fisicamente corretta anche dagli altri punti della passeggiata. Niente tenda dove oltre r_terr
    non c'e terra (mare aperto)."""
    coll = _coll("FONDALE_Tenda")
    sx, sy = P["spawn"]
    R = P["tenda_r"]
    img = _save_png("T_Fondale_Tenda_D", paint_tenda())
    mat = _material("M_Fondale_Tenda", img, rough=1.0)
    far1 = far_horizon(1.0)
    rep = {}
    for lod in lods:
        step = P["tenda_step"][lod]
        azs = np.arange(0.0, 360.0, step)
        tops = []
        for a in azs:
            ks = [int(k) % 360 for k in range(int(round(a - step / 2)), int(round(a + step / 2)) + 1)]
            tops.append(max(far1[k] for k in ks))
        tops = np.array(tops)
        verts, faces, uvs = [], [], []
        n = len(azs)
        for i, (a, e) in enumerate(zip(azs, tops)):
            dx, dy = az_to_dxdy(a, R)
            zt = max(P["eye_z"] + R * math.tan(math.radians(max(e, -0.2))), -30.0)
            verts.append((sx + dx, sy + dy, -30.0))
            verts.append((sx + dx, sy + dy, zt))
            uvs += [(a / 360.0 * 8.0, 0.0), (a / 360.0 * 8.0, 1.0)]
        for i in range(n):
            j = (i + 1) % n
            if tops[i] <= 0.0 and tops[j] <= 0.0:
                continue  # mare aperto oltre il terreno: niente tenda
            b0, t0, b1, t1 = 2 * i, 2 * i + 1, 2 * j, 2 * j + 1
            # faccia rivolta verso la partenza (verso l'interno)
            faces.append((b0, t1, t0))
            faces.append((b0, b1, t1))
        V = warp_points(np.array(verts))
        # uv per angolo: ripeto la texture 8 volte sul giro; il seam a 360 resta nel varco del mare
        name = "SM_Fondale_Tenda" + ("" if lod == 0 else f"_LOD{lod}")
        piv = (round(sx, -1), round(sy, -1))
        obj = _mesh_object(name, V, faces, coll, piv, uvs=np.array(uvs), mat=mat)
        if lod > 0:
            obj.hide_set(True)
            obj.hide_render = True
        rep[name] = dict(tris=len(faces), pivot=piv, bbox=(V.min(axis=0).round(1).tolist(),
                                                           V.max(axis=0).round(1).tolist()))
    return rep


# ------------------------------------------------------------------------------------------------------------
# Citta (anello A): edifici OSM estrusi
# ------------------------------------------------------------------------------------------------------------
FACADE_TINTS = [(0.98, 0.90, 0.72), (0.96, 0.80, 0.66), (0.93, 0.72, 0.52), (0.98, 0.86, 0.58),
                (0.97, 0.95, 0.90), (0.92, 0.74, 0.66), (0.88, 0.86, 0.80), (0.95, 0.83, 0.70)]
ROOF_TINTS = [(0.62, 0.36, 0.28), (0.55, 0.33, 0.27), (0.50, 0.48, 0.45), (0.58, 0.40, 0.32)]


def _simplify_ring(pts, tol=1.2):
    """Toglie vertici quasi allineati o troppo vicini (pts chiuso senza ripetizione)."""
    changed = True
    pts = list(pts)
    while changed and len(pts) > 4:
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            ab = math.hypot(b[0] - a[0], b[1] - a[1])
            ac = math.hypot(c[0] - a[0], c[1] - a[1])
            if ac < 1e-6:
                pts.pop(i)
                changed = True
                break
            dist = abs((c[0] - a[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (c[1] - a[1])) / ac
            if dist < tol or ab < tol:
                pts.pop(i)
                changed = True
                break
    return pts


def _area(pts):
    return 0.5 * sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))


def city_buildings(osm_json):
    f = fields()
    data = json.load(open(osm_json, encoding="utf-8"))
    sx, sy = P["spawn"]
    x0, x1, y0, y1 = P["excl_rect"]
    rmin, rmax = P["city_r"]
    rng = np.random.default_rng(P["seed"] + 21)
    out = []
    for e in data["elements"]:
        rings = []
        if e["type"] == "way" and "geometry" in e:
            rings.append(e["geometry"])
        elif e["type"] == "relation":
            for m in e.get("members", []):
                if m.get("role") == "outer" and "geometry" in m:
                    rings.append(m["geometry"])
        t = e.get("tags", {})
        if t.get("building") in ("roof", "construction", "no") or t.get("location") == "underground":
            continue
        for g in rings:
            pts = [ll_to_xy(p["lat"], p["lon"]) for p in g]
            if len(pts) > 1 and math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 0.01:
                pts = pts[:-1]
            if len(pts) < 3:
                continue
            cxm = sum(p[0] for p in pts) / len(pts)
            cym = sum(p[1] for p in pts) / len(pts)
            dd = math.hypot(cxm - sx, cym - sy)
            if not (rmin <= dd <= rmax):
                continue
            if x0 - 5 < cxm < x1 + 5 and y0 - 5 < cym < y1 + 5:
                continue
            if not sample_nearest(f["land"], np.array([cxm]), np.array([cym]))[0]:
                continue
            pts = _simplify_ring(pts, 1.0 if dd < 700 else 1.8)
            if len(pts) < 3:
                continue
            A = _area(pts)
            if abs(A) < 30.0:
                continue
            if A < 0:
                pts = pts[::-1]
            # altezza
            lv = t.get("building:levels")
            hh = None
            try:
                hh = float(t["height"].split()[0]) if "height" in t else None
            except Exception:
                hh = None
            try:
                lvn = float(lv) if lv else None
            except Exception:
                lvn = None
            xs = np.array([p[0] for p in pts])
            ys = np.array([p[1] for p in pts])
            g_c = float(ground_z(np.array([cxm]), np.array([cym]))[0]) - P["z_off"]  # s.l.m.
            dsm = float(max(sample_nearest(f["h_raw"], xs, ys).max(),
                            sample_nearest(f["h_raw"], np.array([cxm]), np.array([cym]))[0]))
            resid = dsm - g_c
            if hh is None and lvn is not None:
                hh = lvn * 3.2 + 1.3
                if lvn >= 12 and resid < 20:  # piani sospetti (ref/fondale.md §6): uso il DSM
                    hh = None
            if hh is None:
                if abs(A) < 60:
                    hh = 4.0
                else:
                    hh = float(np.clip(resid if resid > 5 else 9.0 + rng.uniform(-2, 6), 5.0, 30.0))
            hh = float(min(hh, 40.0))
            gz = ground_z(xs, ys)
            base = float(gz.min()) - 1.0
            top = float(ground_z(np.array([cxm]), np.array([cym]))[0]) + hh
            top = max(top, base + 3.0)
            out.append(dict(id=e["id"], pts=pts, base=base, top=top, h=hh, d=dd,
                            az=float(xy_to_az(cxm - sx, cym - sy)), c=(cxm, cym)))
    return out


def _building_geom(b, tint, roof_tint):
    pts = b["pts"]
    n = len(pts)
    verts, faces, uvs, cols = [], [], [], []
    # pareti: quad indipendenti (UV a metri: 12 m x 12,8 m per ripetizione)
    per = 0.0
    for i in range(n):
        a, c = pts[i], pts[(i + 1) % n]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        k = len(verts)
        verts += [(a[0], a[1], b["base"]), (c[0], c[1], b["base"]), (c[0], c[1], b["top"]), (a[0], a[1], b["top"])]
        u0, u1 = per / 12.0, (per + L) / 12.0
        v0, v1 = 0.0, (b["top"] - b["base"]) / 12.8
        uvs += [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        cols += [tint] * 4
        faces += [(k, k + 1, k + 2), (k, k + 2, k + 3)]
        per += L
    # tetto piano: triangolazione a ventaglio con ear clipping semplice
    k = len(verts)
    for p in pts:
        verts.append((p[0], p[1], b["top"]))
        uvs.append((2.0 / 1024, 2.0 / 1024))
        cols.append(roof_tint)
    idx = list(range(n))
    guard = 0
    while len(idx) > 3 and guard < 10 * n:
        guard += 1
        m = len(idx)
        for j in range(m):
            i0, i1, i2 = idx[j - 1], idx[j], idx[(j + 1) % m]
            a, bb, c = pts[i0], pts[i1], pts[i2]
            cr = (bb[0] - a[0]) * (c[1] - a[1]) - (bb[1] - a[1]) * (c[0] - a[0])
            if cr <= 1e-9:
                continue
            inside = False
            for q in idx:
                if q in (i0, i1, i2):
                    continue
                p = pts[q]
                d1 = (bb[0] - a[0]) * (p[1] - a[1]) - (bb[1] - a[1]) * (p[0] - a[0])
                d2 = (c[0] - bb[0]) * (p[1] - bb[1]) - (c[1] - bb[1]) * (p[0] - bb[0])
                d3 = (a[0] - c[0]) * (p[1] - c[1]) - (a[1] - c[1]) * (p[0] - c[0])
                if d1 > 0 and d2 > 0 and d3 > 0:
                    inside = True
                    break
            if inside:
                continue
            faces.append((k + i0, k + i1, k + i2))
            idx.pop(j)
            break
        else:
            break
    if len(idx) == 3:
        faces.append((k + idx[0], k + idx[1], k + idx[2]))
    return verts, faces, uvs, cols


def build_city(osm_json, lods=(0, 1, 2)):
    """Edifici di fondale dell'anello A in blocchi <= city_chunk_tris, raggruppati per settore e distanza.
    LOD1: edifici >= 250 m2 o >= 18 m, pianta semplificata 3 m; LOD2: >= 700 m2 o >= 22 m, pianta 6 m."""
    blds = city_buildings(osm_json)
    coll = _coll("FONDALE_Citta")
    img = _save_png("T_Fondale_Facciata_D", paint_facade())
    mat = _material("M_Fondale_Facciate", img, use_vcol=True, rough=0.9)
    rng = np.random.default_rng(P["seed"] + 5)
    for b in blds:
        b["tint"] = FACADE_TINTS[int(rng.integers(len(FACADE_TINTS)))]
        b["roof"] = ROOF_TINTS[int(rng.integers(len(ROOF_TINTS)))]
        b["area"] = _area(b["pts"])
        b["sec"] = int(np.floor(((b["az"] - P["sector_offset"]) % 360.0) / (360.0 / P["n_sectors"])))
    # blocchi: per settore, ordinati per distanza, tagliati a city_chunk_tris (sul LOD0)
    chunks = []
    for s in range(P["n_sectors"]):
        bs = sorted([b for b in blds if b["sec"] == s], key=lambda b: b["d"])
        cur, ct = [], 0
        for b in bs:
            tcount = 2 * len(b["pts"]) + len(b["pts"]) - 2
            if ct + tcount > P["city_chunk_tris"] and cur:
                chunks.append((s, cur))
                cur, ct = [], 0
            cur.append(b)
            ct += tcount
        if cur:
            chunks.append((s, cur))
    rep = {}
    cnt = {}
    for s, bs in chunks:
        cnt[s] = cnt.get(s, 0) + 1
        base_name = f"SM_Fondale_Citta_{SECTOR_NAMES[s]}_{cnt[s]:02d}"
        for lod in lods:
            if lod == 0:
                sel = bs
            elif lod == 1:
                sel = [b for b in bs if b["area"] >= 250 or b["h"] >= 18]
            else:
                sel = [b for b in bs if b["area"] >= 700 or b["h"] >= 22]
            if not sel:
                sel = sorted(bs, key=lambda b: -b["area"])[:1]
            V, F, UV, C = [], [], [], []
            for b in sel:
                pts = b["pts"]
                if lod > 0 and len(pts) > 4:
                    pts = _simplify_ring(pts, 3.0 if lod == 1 else 6.0)
                    if len(pts) < 3:
                        pts = b["pts"]
                bb = dict(b, pts=pts)
                v, fc, uv, col = _building_geom(bb, b["tint"], b["roof"])
                off = len(V)
                V += v
                F += [(a + off, c + off, d + off) for a, c, d in fc]
                UV += uv
                C += col
            V = warp_points(np.array(V))
            name = base_name + ("" if lod == 0 else f"_LOD{lod}")
            if lod == 0:
                piv0 = _pivot(V)
            piv = piv0
            obj = _mesh_object(name, V, F, coll, piv, uvs=np.array(UV), vcols=np.array(C), mat=mat)
            if lod > 0:
                obj.hide_set(True)
                obj.hide_render = True
            rep[name] = dict(tris=len(F), n_edifici=len(sel), pivot=piv,
                             bbox=(V.min(axis=0).round(1).tolist(), V.max(axis=0).round(1).tolist()),
                             d=(round(min(b["d"] for b in bs)), round(max(b["d"] for b in bs))))
    return rep, blds


# ------------------------------------------------------------------------------------------------------------
# Export
# ------------------------------------------------------------------------------------------------------------
def export_objects(names, overwrite=False):
    """Esporta ogni oggetto in exports/fondale/<nome>.fbx col preset di progetto (morin_export, mode asset):
    l'oggetto viene portato temporaneamente in (0,0,0) (pivot dell'asset = origine del file) e poi rimesso al pivot.
    LOD1/LOD2 con bake_rotation=True (come gli altri kit). Nessuna collisione (fondale irraggiungibile)."""
    import importlib
    import sys
    p = PROJ + "/blender/scripts"
    if p not in sys.path:
        sys.path.append(p)
    import morin_export
    importlib.reload(morin_export)
    reps = {}
    for nm in names:
        o = bpy.data.objects[nm]
        loc = o.location.copy()
        hid = o.hide_get()
        try:
            o.hide_set(False)
            o.location = (0.0, 0.0, 0.0)
            bpy.context.view_layer.update()
            lod = "_LOD" in nm
            r = morin_export.export_fbx([o], f"{EXPDIR}/{nm}.fbx", mode="asset", overwrite=overwrite,
                                        bake_rotation=lod, verbose=False)
            reps[nm] = dict(file=r["file"], bytes=r["bytes"], tris=r["tris_visible_total"],
                            warnings=[w for w in r["warnings"] if "UCX" not in w])
        finally:
            o.location = loc
            o.hide_set(hid)
    return reps
