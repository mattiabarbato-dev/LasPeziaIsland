"""morin_texture_v3.py — migliorie rimaste dal passaggio texture v2 (2026-11-20, docs/uefn_arte.md §38).

Texture nuove in blender/textures/v3/ (nomi nuovi, nessuna v1/v2 sovrascritta):
    T_Ponte_Legno_v3          4096, 6 m   doghe TRASVERSALI (come in ref/foto/ponte), usura sulla linea di passaggio
    T_Viale_Segnaletica_v2    2048, 2 m   vernice bianca consumata e screpolata, asfalto che traspare
    T_Pav_Cubetti_v3          4096, 5,6 m 2 x 2 ventagli deformati a mano + tinta per cubetto (rompe la ripetizione)
    T_Morin_Prato_v3          4096, 8 m   variazione a media scala (chiazze, zone fitte, zone rade)
    T_Morin_Prato_MacroVar    2048, 32 m  macro del prato piu' contrastata (si mette nel parametro MacroVar della MI)

Uso (console Python di Blender o MCP):
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_texture_v3 as t3; importlib.reload(t3)
    t3.make_all(); t3.confronto_render()

Convenzioni uguali alla v2 (docs/texture_v2.md): D sRGB, N DirectX, ORM = AO/Roughness/Metallic.
Fonti: Poly Haven (CC0) gia' in blender/textures/src/; foto dell'utente solo per tarare colore e scala.
"""
import os

import bpy
import numpy as np

import morin_texphoto as tp
import morin_texture_v2 as t2
from morin_texture_v2 import c8, lum, src, resample, gl_to_dx, blend_normals, noise, fbm, normal_from_mm, cavity_ao

PROJ = t2.PROJ
TEX = t2.TEX
OUT = TEX + "/v3"


def save_set(name, D, N, ORM):
    os.makedirs(OUT, exist_ok=True)
    out = []
    for k, a in (("D", D), ("N", N), ("ORM", ORM)):
        p = f"{OUT}/{name}_{k}.png"
        tp.save(np.clip(a, 0, 1), p)
        out.append(p)
    return out


def stats(name):
    a = tp.load(f"{OUT}/{name}_D.png")
    m = a[..., :3].reshape(-1, 3).astype(np.float64).mean(0)
    o = tp.load(f"{OUT}/{name}_ORM.png")[..., :3].reshape(-1, 3).astype(np.float64)
    return f"{name}: {a.shape[1]}x{a.shape[0]} D mean {np.round(m * 255).astype(int)} " \
           f"| R mean {o[:, 1].mean():.2f} [{np.percentile(o[:, 1], 5):.2f}-{np.percentile(o[:, 1], 95):.2f}] AO {o[:, 0].mean():.2f}"


def fbm0(h, w, sigmas, seed, weights=None):
    """fbm a media 0 e deviazione 1 (con sigma grandi il rumore sfocato della v2 ha una media non nulla)."""
    f = fbm(h, w, sigmas, seed, weights)
    f = f - f.mean()
    return f / (f.std() + 1e-6)


def noise0(h, w, sigma, seed):
    f = noise(h, w, sigma, seed)
    f = f - f.mean()
    return f / (f.std() + 1e-6)


def psample(a, x, y):
    """Campionamento bilineare PERIODICO (x, y in pixel, array della stessa forma)."""
    h, w = a.shape[:2]
    x = np.mod(x, w); y = np.mod(y, h)
    x0 = np.floor(x).astype(np.int32); y0 = np.floor(y).astype(np.int32)
    x1 = (x0 + 1) % w; y1 = (y0 + 1) % h
    fx = (x - x0).astype(np.float32); fy = (y - y0).astype(np.float32)
    if a.ndim == 3:
        fx = fx[..., None]; fy = fy[..., None]
    top = a[y0, x0] * (1 - fx) + a[y0, x1] * fx
    bot = a[y1, x0] * (1 - fx) + a[y1, x1] * fx
    return (top * (1 - fy) + bot * fy).astype(np.float32)


def disc(D, H, R, M, cy, cx, r, col=None, dh=0.0, h_dome=None, rough=None, metal=None, darken=None, ppm=None):
    """Timbra un dischetto (raggio r px) periodico."""
    S2, S = D.shape[:2]
    rr = int(np.ceil(r)) + 2
    yy, xx = np.ogrid[-rr:rr + 1, -rr:rr + 1]
    dd = np.sqrt(yy * yy + xx * xx)
    m = dd <= r
    ring = (dd > r) & (dd <= r + 1.5)
    sub = np.ix_(np.arange(cy - rr, cy + rr + 1) % S2, np.arange(cx - rr, cx + rr + 1) % S)
    d_ = D[sub]
    if col is not None:
        d_[m] = col
    if darken is not None:
        d_[m] *= darken
    d_[ring] *= 0.7
    D[sub] = d_
    h_ = H[sub]
    if h_dome is not None:
        h_[m] = h_dome * (1 - (dd[m] / r) ** 2) + dh
    else:
        h_[m] += dh
    H[sub] = h_
    if rough is not None:
        x_ = R[sub]; x_[m] = rough; R[sub] = x_
    if metal is not None:
        x_ = M[sub]; x_[m] = metal; M[sub] = x_


# =============================================================================================================
# 1. legno del ponte v3 (MI_Ponte_Legno, UV 6 m: u = attraverso l'impalcato, centro u 0,5; v = lungo il ponte)
# =============================================================================================================
def make_ponte_legno(S=4096, seed=313):
    """T_Ponte_Legno_v3. Dalle foto ref/foto/ponte/ponte1.png e ponte_verso_passegiata.png: le doghe sono
    TRASVERSALI (perpendicolari all'asse), larghe ~12 cm, con un giunto sull'asse; due file di borchie metalliche
    corrono lungo il ponte. Grigio-bruno consumato (foto al sole ~118/116/112), doghe di tono diverso, qualche doga
    sostituita piu' scura o piu' bruna, bordi argentati e sporchi verso i cordoli, centro (linea di passaggio)
    piu' liscio, piu' scuro e meno ruvido. Grana di wood_planks_grey (PH, CC0) trasposta lungo la doga."""
    W = 6.0
    ppm = S / W
    rng = np.random.default_rng(seed)
    NPk = 48
    pw = W / NPk                                            # 0,125 m
    u = (np.arange(S, dtype=np.float32) + 0.5) / ppm        # colonne: attraverso
    v = (np.arange(S, dtype=np.float32) + 0.5) / ppm        # righe: lungo il ponte
    pj = np.floor(v / pw).astype(np.int32) % NPk            # indice doga (per riga)
    vin = (v / pw - np.floor(v / pw))                       # 0..1 dentro la doga
    # segmenti di doga lungo u: giunto sull'asse (u 3) e sul bordo (u 0 = 6); il 18 % ha un giunto in piu' (riparazione)
    extra = np.where(rng.random(NPk) < 0.18, rng.uniform(0.6, 5.4, NPk), -1.0).astype(np.float32)
    U = np.broadcast_to(u[None, :], (S, S))
    half = (U >= 3.0).astype(np.int32)
    ex = extra[pj][:, None]
    seg_extra = ((ex > 0) & (U >= ex)).astype(np.int32)
    sid = pj[:, None] * 4 + half * 2 + seg_extra             # id del segmento
    NS = NPk * 4
    # distanza dal giunto lungo u (m)
    dj = np.minimum(np.minimum(np.abs(U - 3.0), np.minimum(U, W - U)), np.where(ex > 0, np.abs(U - ex), 9.0))
    # ---- grana: sorgente trasposta (le doghe della foto diventano orizzontali)
    sd = resample(src("wood_planks_grey", "diff"), int(round(1.5 * ppm)))
    sdisp = resample(src("wood_planks_grey", "disp"), int(round(1.5 * ppm)))
    sd = np.ascontiguousarray(sd.transpose(1, 0, 2)); sdisp = np.ascontiguousarray(sdisp.T)
    hs, ws = sd.shape[:2]
    L = lum(sd ** 2.2)
    rm = L.mean(1)
    bad = rm < rm.mean() - 1.2 * rm.std()                  # righe delle fughe della foto
    badw = np.convolve(np.concatenate([bad, bad[:64]]).astype(np.float32), np.ones(9), "same")[:hs] > 0
    hpx = int(np.ceil(pw * ppm)) + 2
    ok = np.array([not badw[(np.arange(s, s + hpx)) % hs].any() for s in range(hs)])
    starts = np.nonzero(ok)[0]
    G = tp.highpass(L, 40); G = (G - 1.0) / (G.std() + 1e-6)
    hd = (sdisp - sdisp.mean()) / (sdisp.std() + 1e-6)
    sy0 = starts[rng.integers(0, len(starts), NS)]
    sx0 = rng.integers(0, ws, NS)
    fl = rng.random(NS) < 0.5
    row_in = (vin * pw * ppm).astype(np.int32)[:, None]
    xx = np.arange(S, dtype=np.int32)[None, :]
    syy = (sy0[sid] + row_in) % hs
    sxx = (np.where(fl[sid], -xx, xx) + sx0[sid]) % ws
    grain = G[syy, sxx]
    hgr = hd[syy, sxx]
    del syy, sxx
    # ---- tinta per segmento
    tint = rng.normal(1.0, 0.11, NS).astype(np.float32)
    warm = rng.normal(0.0, 0.035, NS).astype(np.float32)
    kind = rng.random(NS)
    dark = kind < 0.12
    brown = (kind >= 0.12) & (kind < 0.20)                  # doghe sostituite, ancora brune
    silver = kind > 0.90
    tint[dark] *= 0.76
    warm[brown] += 0.10; tint[brown] *= 0.92
    tint[silver] *= 1.12
    # ---- usura: linea di passaggio al centro (gauss 1,3 m), bordi argentati e sporchi
    wc = np.exp(-((u - 3.0) / 1.3) ** 2)[None, :]           # 1 al centro
    edge = np.clip(1 - np.minimum(u, W - u) / 0.45, 0, 1)[None, :]   # 1 sul bordo
    traffic = fbm0(S, S, [ppm * 0.06, ppm * 0.25], seed + 5)
    low = fbm0(S, S, [S / 30, S / 120], seed + 3)
    base = c8((108, 105, 100)) ** 2.2
    gk = 0.20 * (1 - 0.45 * wc)                             # grana meno marcata dove si cammina (lucidata)
    t = tint[sid] * (1 + gk * np.clip(grain, -3, 3)) * (1 + 0.05 * low)
    t *= (1 - 0.07 * wc * (0.6 + 0.4 * np.clip(traffic, -1, 2)))          # centro piu' scuro (sporco delle scarpe)
    t *= (1 + 0.06 * (1 - wc) - 0.10 * edge)
    lin = base[None, None, :] * np.clip(t, 0.15, 2.0)[..., None]
    wm = warm[sid] + 0.025 * wc                              # centro un filo piu' caldo
    lin[..., 0] *= 1 + wm
    lin[..., 2] *= 1 - wm
    # argento (desaturato) sui bordi e sulle doghe argentate
    sv = np.clip(0.55 * (1 - wc) + 0.5 * silver[sid], 0, 1) * 0.5
    g = lum(lin)
    lin = lin * (1 - sv[..., None]) + g[..., None] * sv[..., None]
    # sporco verdastro scuro contro i cordoli
    grime = edge * np.clip(0.6 + 0.4 * noise0(S, S, 25, seed + 7), 0, 1)
    lin = lin * (1 - 0.35 * grime[..., None]) + (c8((70, 72, 60)) ** 2.2)[None, None] * 0.35 * grime[..., None]
    # ---- altezza (mm), roughness, metallic
    H = 0.30 * hgr - 0.6 * ((vin[:, None] - 0.5) * 2) ** 2 * (1 - 0.4 * wc)
    R = 0.84 + 0.04 * np.clip(grain, -2, 2) - 0.14 * wc + 0.03 * edge + 0.03 * dark[sid]
    M = np.zeros((S, S), np.float32)
    gv = np.minimum(vin, 1 - vin)[:, None] * pw            # distanza dalla fuga (m)
    gap = gv < 0.0028
    endj = dj < 0.0018
    bev = np.clip(1 - gv / 0.010, 0, 1) * 0.18
    lin *= (1 - bev)[..., None]
    gj = gap | endj
    lin[gj] *= 0.12
    H[gj] = -8.0
    R[gj] = 0.95
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    del U, lin, grain, hgr, traffic, low
    # ---- viti sulle travi (asse e bordi) e borchie nelle due file a +-1,0 m dall'asse
    for p in range(NPk):
        cy = int((p + 0.5) * pw * ppm)
        for cu in (2.955, 3.045, 0.30, 5.70):
            for dv in (-0.032, 0.032):
                disc(D, H, R, M, cy + int(dv * ppm), int(cu * ppm), 2.6, darken=0.45, dh=-0.4)
        for cu in (2.0, 4.0):
            jit = rng.normal(0, 0.004, 2)
            disc(D, H, R, M, cy + int(jit[0] * ppm), int((cu + jit[1]) * ppm), 0.017 * ppm,
                 col=c8((146, 146, 142)) * rng.uniform(0.85, 1.05), h_dome=1.5, dh=0.3, rough=0.38, metal=0.85)
    H = tp.blur(H, 0.7)
    N = normal_from_mm(H, ppm)
    ao = cavity_ao(H, 5, 0.12, 0.4)
    ORM = np.dstack([ao, np.clip(R, 0.3, 1.0), M])
    return save_set("T_Ponte_Legno_v3", D, N, ORM)


# =============================================================================================================
# 2. segnaletica orizzontale (MI_Viale_Segnaletica, UV in metri: con UV_Tiling 0,5 la texture copre 2 m)
# =============================================================================================================
def _voronoi_edges(S, cell_px, seed):
    """Distanza (px) dal bordo della cella di Voronoi piu' vicina (F2 - F1) su griglia periodica, e id cella."""
    rng = np.random.default_rng(seed)
    nc = int(round(S / cell_px))
    cs = S / nc
    pts = rng.random((nc, nc, 2)).astype(np.float32) * cs
    y = np.arange(S, dtype=np.float32)[:, None] + 0.5
    x = np.arange(S, dtype=np.float32)[None, :] + 0.5
    gy = np.floor(y / cs).astype(np.int32); gx = np.floor(x / cs).astype(np.int32)
    f1 = np.full((S, S), 1e9, np.float32); f2 = np.full((S, S), 1e9, np.float32)
    idc = np.zeros((S, S), np.int32)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            cy = (gy + oy) % nc; cx = (gx + ox) % nc
            py = (gy + oy) * cs + pts[cy, cx, 0]
            px = (gx + ox) * cs + pts[cy, cx, 1]
            d = np.sqrt((y - py) ** 2 + (x - px) ** 2)
            cid = cy * nc + cx
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            idc = np.where(closer, cid, idc)
            f1 = np.where(closer, d, f1)
    return f2 - f1, idc


def make_segnaletica(S=2048, seed=921):
    """T_Viale_Segnaletica_v2: vernice spartitraffico bianca su asfalto, tile 2 m (1024 px/m).
    Asfalto: asphalt_04 (PH, CC0) ritagliato a 2 m e reso tileable. Vernice: copertura ~75 %, consumata a chiazze
    (le punte degli inerti escono scure prima), screpolata a celle (craquelure 2-6 cm) con scaglie mancanti,
    sporco grigio-bruno, bordi delle scaglie in rilievo di 0,4 mm."""
    ppm = S / 2.0
    rng = np.random.default_rng(seed)
    a_d = src("asphalt_04", "diff"); a_h = src("asphalt_04", "disp"); a_r = src("asphalt_04", "rough")
    n = int(round(a_d.shape[0] * 2.0 / 4.04))
    crop = lambda a: tp.tileable(tp.resize(a[:n, :n] if a.ndim == 2 else a[:n, :n], S, S))
    Ad = crop(a_d); Ah = crop(a_h); Ar = crop(a_r)
    Ad = t2.set_mean(Ad, c8((82, 81, 78)))
    Ahn = (Ah - Ah.mean()) / (Ah.std() + 1e-6)
    # usura: chiazze larghe (passaggio delle ruote e dei piedi) + punte degli inerti
    wear = fbm0(S, S, [ppm * 0.25, ppm * 0.08, ppm * 0.02], seed + 1, [1.0, 0.6, 0.3])
    wear = (wear - wear.min()) / (wear.max() - wear.min())
    Ahp = tp.highpass(Ah + 1.0, 6) - 1.0                     # inerti (alta frequenza)
    Ahp = Ahp / (Ahp.std() + 1e-6)
    paint = (wear - 0.10 * Ahp) < 0.70                      # bordo dell'usura frastagliato dagli inerti
    # screpolature: rete larga (celle ~15 cm) solo a tratti, rete fine (~4 cm) solo vicino all'usura
    e1, id1 = _voronoi_edges(S, 0.045 * ppm, seed + 2)
    e2, id2 = _voronoi_edges(S, 0.15 * ppm, seed + 3)
    ej = 1.6 * noise0(S, S, 2.0, seed + 6)                   # bordo delle crepe irregolare
    crack_big = (e2 + ej < 1.4) & (noise0(S, S, 45, seed + 4) > 0.15)
    crack_fine = (e1 + ej < 1.0) & (wear > 0.52) & (noise0(S, S, 25, seed + 7) > 0.0)
    hcell = ((id1.astype(np.int64) * 2654435761) % 4294967296).astype(np.float64) / 4294967296.0
    flake = (hcell < 0.6 * np.clip(wear - 0.55, 0, 1)).astype(np.float32)   # scaglie solo dove gia' consumato
    flake = (tp.blur(flake, 3.0) + 0.22 * noise0(S, S, 1.5, seed + 8)) > 0.5
    paint &= ~flake
    pm = tp.blur(paint.astype(np.float32), 0.8)             # bordi morbidi di 1 px
    crk = tp.blur((crack_big | crack_fine).astype(np.float32), 0.5) * pm * 0.75
    pm = pm * (1 - crk)
    # colore vernice: bianco sporco, piu' grigio dove consumato, macchie di gomma/sporco
    dirt = np.clip(0.5 + 0.5 * fbm0(S, S, [ppm * 0.15, ppm * 0.03], seed + 5), 0, 1)
    pw_ = c8((226, 225, 216)) ** 2.2
    pd = c8((178, 174, 164)) ** 2.2
    k = np.clip(0.18 * dirt + 0.30 * np.clip(wear - 0.50, 0, 1), 0, 1)
    pcol = pw_[None, None] * (1 - k[..., None]) + pd[None, None] * k[..., None]
    pcol *= (1 + 0.04 * np.clip(tp.highpass(lum(Ad), 6) - 1, -1, 1) * 3)[..., None]
    alin = np.clip(Ad, 0, 1) ** 2.2
    # residui di vernice negli avvallamenti dell'asfalto anche fuori dalla vernice
    resid = np.clip((-Ahn - 0.6) * 0.5, 0, 0.5) * (1 - pm) * (wear < 0.9)
    lin = alin * (1 - pm[..., None]) + pcol * pm[..., None]
    lin = lin * (1 - resid[..., None]) + pw_[None, None] * 0.75 * resid[..., None]
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    H = 0.8 * Ahn * (1 - 0.6 * pm) + 0.4 * pm               # mm
    H = tp.blur(H, 0.6)
    N = normal_from_mm(H, ppm)
    rn = (Ar - Ar.mean()) / (Ar.std() + 1e-6)
    R = (0.86 + 0.04 * rn) * (1 - pm) + (0.58 + 0.12 * k) * pm
    ao = cavity_ao(H, 4, 0.25, 0.45)
    ORM = np.dstack([ao, np.clip(R, 0.3, 1), np.zeros_like(R)])
    return save_set("T_Viale_Segnaletica_v2", D, N, ORM)


# =============================================================================================================
# 3. cubetti a ventaglio v3 (MI_Pav_Cubetti, Tile_m 5,6)
# =============================================================================================================
def _flood_max(lbl, mask, iters):
    """Propaga il massimo dentro le regioni connesse di `mask` (4-vicini): id costante per cubetto."""
    lbl = np.where(mask, lbl, 0)
    for _ in range(iters):
        m = lbl.copy()
        for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
            np.maximum(m, np.roll(lbl, sh, ax), out=m)
        lbl = np.where(mask, m, 0)
    return lbl


def make_cubetti(S=4096, seed=2801):
    """T_Pav_Cubetti_v3: 2 x 2 ventagli di patterned_cobblestone (PH, CC0) su 5,6 m (stessa scala della v2: cubetto
    ~9 cm, ventaglio ~1,3 m), deformati con un campo morbido periodico (+-6 cm, posa a mano: i quattro quadranti
    non sono piu' uguali), tinta e roughness per cubetto (segmentazione dei cubetti dall'altezza), chiazze a media
    scala (0,5-2 m), sporco variabile nelle fughe, qualche macchia scura. Tile 4096 su 5,6 m (731 px/m)."""
    rng = np.random.default_rng(seed)
    d = src("patterned_cobblestone", "diff")
    nn = src("patterned_cobblestone", "nor_gl")
    r = src("patterned_cobblestone", "rough")
    ao = src("patterned_cobblestone", "ao")
    h = src("patterned_cobblestone", "disp")
    # campo di deformazione periodico (in px della tela S): due ottave
    ppm = S / 5.6
    wx = noise0(S, S, 0.45 * ppm, seed + 1) * 0.045 * ppm + noise0(S, S, 0.12 * ppm, seed + 2) * 0.012 * ppm
    wy = noise0(S, S, 0.45 * ppm, seed + 3) * 0.045 * ppm + noise0(S, S, 0.12 * ppm, seed + 4) * 0.012 * ppm
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    k = d.shape[0] * 2.0 / S                                  # 2 ripetizioni della sorgente
    sx = (xs + wx) * k; sy = (ys + wy) * k
    del xs, ys
    if k < 1.3 and k > 0.7:
        pass
    D0 = psample(d, sx, sy); N0 = gl_to_dx(psample(nn, sx, sy)); R0 = psample(r, sx, sy)
    A0 = psample(ao, sx, sy); H0 = psample(h, sx, sy)
    del sx, sy, wx, wy
    D0 = t2.recolor(D0, c8((120, 113, 106)), sat=0.55, contrast=1.15)
    # segmentazione: interno del cubetto = altezza sopra la media locale
    hl = H0 - tp.blur(H0, 0.03 * ppm)
    mask = (hl > -0.004) & (A0 > np.percentile(A0, 30))
    lbl = rng.integers(1, 2 ** 31 - 1, (S, S), dtype=np.int64).astype(np.int32)
    lbl = _flood_max(lbl, mask, 40)
    hsh = ((lbl.astype(np.int64) * 2654435761) % 4294967296).astype(np.float64) / 4294967296.0
    hsh2 = ((lbl.astype(np.int64) * 40503 + 12345) % 65536).astype(np.float64) / 65536.0
    inside = lbl > 0
    ct = np.where(inside, 1 + 0.26 * (hsh.astype(np.float32) - 0.5), 1.0).astype(np.float32)   # +-8 %
    cw = np.where(inside, 0.07 * (hsh2.astype(np.float32) - 0.5), 0.0).astype(np.float32)     # rosso/grigio
    cr = np.where(inside, 0.08 * (hsh2.astype(np.float32) - 0.5), 0.0).astype(np.float32)
    del lbl, hsh, hsh2
    lin = np.clip(D0, 0, 1) ** 2.2
    mid = fbm0(S, S, [0.35 * ppm, 0.9 * ppm, 2.0 * ppm], seed + 6, [0.5, 0.8, 1.0])
    lin *= (ct * (1 + 0.07 * mid))[..., None]
    lin[..., 0] *= 1 + cw; lin[..., 2] *= 1 - cw
    # fughe: sporco variabile (piu' scure e terrose a chiazze)
    joint = ~mask
    jd = np.clip(0.5 + 0.5 * noise0(S, S, 0.3 * ppm, seed + 7), 0, 1)
    soil = c8((60, 54, 46)) ** 2.2
    jm = (joint * (0.25 + 0.45 * jd)).astype(np.float32)
    jm = tp.blur(jm, 1.0)
    lin = lin * (1 - jm[..., None]) + soil[None, None] * jm[..., None]
    # macchie scure sparse (olio, chewing gum) e zone impolverate piu' chiare
    stains = np.clip(noise0(S, S, 0.10 * ppm, seed + 8) - 2.2, 0, None)
    stains = stains / (stains.max() + 1e-6)
    dust = np.clip(noise0(S, S, 0.6 * ppm, seed + 9) - 1.0, 0, None) * 0.08
    lin *= (1 - 0.35 * stains)[..., None]
    lin = lin * (1 - dust[..., None]) + (c8((150, 142, 130)) ** 2.2)[None, None] * dust[..., None]
    print("cubetti: frazione interno", float(inside.mean()), "maschera", float(mask.mean()))
    lin = np.clip(lin, 0, 1)
    D = t2.set_mean(lin ** (1 / 2.2), c8((118, 109, 101)))
    n = N0 * 2 - 1
    n[..., :2] *= 1.25
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    N = n * 0.5 + 0.5
    rn = (R0 - R0.mean()) / (R0.std() + 1e-6)
    R = np.clip(0.80 + 0.05 * rn + cr - 0.12 * stains + 0.03 * mid, 0.55, 0.97)
    ORM = np.dstack([np.clip(A0, 0.35, 1), R, np.zeros_like(R)])
    return save_set("T_Pav_Cubetti_v3", D, N, ORM)


# =============================================================================================================
# 4. prato v3 (MI_Morin_Prato UV_Tiling 0,5 / MI_Morin_Prato_Mondo Tile_m 8) + macro del prato
# =============================================================================================================
def make_prato(S=4096, seed=4101):
    """T_Morin_Prato_v3: 8 m (512 px/m, densita' della v2). Base: la v2 (4 m) ripetuta 2 x 2 e mescolata con se'
    stessa traslata di 2 m attraverso una maschera morbida (niente ripetizione esatta a 4 m). Sopra, variazione
    a media scala unica sugli 8 m: zone fitte (piu' scure e sature, rilievo piu' forte), zone rade (piu' chiare,
    giallo-verdi, con terra che affiora a puntini), chiazze di trifoglio, macchie secche."""
    ppm = S / 8.0
    vD = tp.load(f"{t2.OUT}/T_Morin_Prato_v2_D.png")[..., :3]
    vN = tp.load(f"{t2.OUT}/T_Morin_Prato_v2_N.png")[..., :3]
    vO = tp.load(f"{t2.OUT}/T_Morin_Prato_v2_ORM.png")[..., :3]
    s = vD.shape[0]

    def tile2(a):
        return np.tile(a, (S // s, S // s, 1))
    D1, N1, O1 = tile2(vD), tile2(vN), tile2(vO)
    sh = s // 2
    D2, N2, O2 = (np.roll(np.roll(a[::-1, ::-1] if False else a, sh, 0), sh, 1) for a in (D1, N1, O1))
    mk = np.clip(0.5 + 0.9 * noise0(S, S, 0.5 * ppm, seed), 0, 1)[..., None]
    lin = (np.clip(D1, 0, 1) ** 2.2) * (1 - mk) + (np.clip(D2, 0, 1) ** 2.2) * mk
    N = N1 * (1 - mk) + N2 * mk
    O = O1 * (1 - mk) + O2 * mk
    # media scala
    dens = fbm0(S, S, [0.35 * ppm, 1.0 * ppm, 2.2 * ppm], seed + 1, [0.5, 1.0, 0.8])     # + fitto, - rado
    dry = np.clip(fbm0(S, S, [0.6 * ppm, 1.6 * ppm], seed + 2) - 0.9, 0, None)
    dry = np.clip(dry / (dry.max() + 1e-6) * 1.6, 0, 1)
    clov = np.clip(fbm0(S, S, [0.25 * ppm, 0.6 * ppm], seed + 3) - 1.0, 0, None)
    clov = np.clip(clov / (clov.max() + 1e-6) * 1.8, 0, 1)
    g = lum(lin)[..., None]
    # fitto: piu' scuro e saturo; rado: piu' chiaro e giallo
    sat = 1 + 0.22 * np.clip(dens, -0.7, 2)[..., None]
    lin = g + (lin - g) * sat
    lin *= (1 - 0.13 * np.clip(dens, -2.5, 2.5))[..., None]
    yel = c8((150, 146, 80)) ** 2.2
    kd = np.clip(-dens * 0.14, 0, 0.28)[..., None] + 0.45 * dry[..., None]
    lin = lin * (1 - kd) + yel[None, None] * g / (lum(yel[None, None])[..., None] + 1e-6) * kd * 1.05
    cc = c8((52, 86, 36)) ** 2.2
    kc = 0.45 * clov[..., None]
    lin = lin * (1 - kc) + cc[None, None] * (g / (lum(cc[None, None])[..., None] + 1e-6)) * kc * 0.9
    # terra che affiora nelle zone rade
    rng = np.random.default_rng(seed + 4)
    soilp = (rng.random((S, S)) < 0.04 * np.clip(-dens - 0.6, 0, 1.5))
    soilp = tp.blur(soilp.astype(np.float32), 0.8) * 2.5
    soilp = np.clip(soilp, 0, 0.8)[..., None]
    lin = lin * (1 - soilp) + (c8((96, 80, 60)) ** 2.2)[None, None] * soilp
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    nn = N * 2 - 1
    nn[..., :2] *= (1 + 0.35 * np.clip(dens, -1.5, 2))[..., None]
    nn /= np.linalg.norm(nn, axis=2, keepdims=True) + 1e-6
    N = nn * 0.5 + 0.5
    ao = np.clip(O[..., 0] * (1 - 0.10 * np.clip(dens, 0, 2)), 0.3, 1)
    R = np.clip(O[..., 1] + 0.03 * dry - 0.02 * np.clip(dens, 0, 2), 0.6, 1)
    ORM = np.dstack([ao, R, np.zeros_like(R)])
    return save_set("T_Morin_Prato_v3", D, N, ORM)


def make_prato_macro(S=2048, seed=4201):
    """T_Morin_Prato_MacroVar: come T_Morin_MacroVar (32 m, media 0,5, coordinate mondo) ma piu' contrastata e con
    chiazze da 3-12 m ben leggibili da lontano (prati irrigati in modo non uniforme, ombra degli alberi)."""
    n = fbm0(S, S, [130, 50, 18, 6], seed, [1.0, 0.8, 0.4, 0.12])
    blot = np.clip(noise0(S, S, 35, seed + 10) - 0.7, 0, None)
    lite = np.clip(noise0(S, S, 50, seed + 11) - 1.1, 0, None)
    v = 0.5 + 0.17 * n - 0.16 * blot / (blot.max() + 1e-6) + 0.14 * lite / (lite.max() + 1e-6)
    v = np.clip(v - (v.mean() - 0.5), 0.08, 0.92)
    os.makedirs(OUT, exist_ok=True)
    tp.save(np.dstack([v, v, v]), f"{OUT}/T_Morin_Prato_MacroVar.png")
    return f"Prato_MacroVar mean {v.mean():.3f} p5 {np.percentile(v, 5):.3f} p95 {np.percentile(v, 95):.3f}"


def make_all():
    out = []
    for f in (make_ponte_legno, make_segnaletica, make_cubetti, make_prato, make_prato_macro):
        out.append(f())
    return out


# =============================================================================================================
# render di confronto v2 -> v3 (blender/arte_texture_v3.blend, docs/qa/arte_texture_v3_confronto.png)
# =============================================================================================================
def _mat(name, base, tile, macro=0.0, macro_tex=None, macro_tile=32.0):
    """Come morin_texture_v2._mat, con texture macro a scelta (percorso completo) e tile in metri (tuple: u, v)."""
    m = t2._mat(name, base, 1.0, 0.0)
    nt = m.node_tree
    mp = next(n for n in nt.nodes if n.type == "MAPPING")
    tu, tv = (tile, tile) if np.isscalar(tile) else tile
    mp.inputs["Scale"].default_value = (1 / tu, 1 / tv, 1)
    if macro > 0:
        tc = next(n for n in nt.nodes if n.type == "TEX_COORD")
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        link = next(l for l in nt.links if l.to_node == bsdf and l.to_socket.name == "Base Color")
        col = link.from_socket
        mp2 = nt.nodes.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (1 / macro_tile,) * 3
        nt.links.new(tc.outputs["Object"], mp2.inputs["Vector"])
        mt = nt.nodes.new("ShaderNodeTexImage")
        mt.image = t2._img(macro_tex or f"{t2.OUT}/T_Morin_MacroVar.png", True)
        nt.links.new(mp2.outputs[0], mt.inputs[0])
        k2 = nt.nodes.new("ShaderNodeMath"); k2.operation = "MULTIPLY_ADD"
        k2.inputs[1].default_value = 2 * macro; k2.inputs[2].default_value = 1 - macro
        nt.links.new(mt.outputs[0], k2.inputs[0])
        mm_ = nt.nodes.new("ShaderNodeMix"); mm_.data_type = "RGBA"; mm_.blend_type = "MULTIPLY"
        mm_.inputs["Factor"].default_value = 1.0
        nt.links.new(col, mm_.inputs["A"]); nt.links.new(k2.outputs[0], mm_.inputs["B"])
        nt.links.new(mm_.outputs["Result"], bsdf.inputs["Base Color"])
    return m


V2 = t2.OUT + "/T_Morin_MacroVar.png"
V3P = OUT + "/T_Morin_Prato_MacroVar.png"
# (riga, camera (pos, rot gradi), prima, dopo); ogni lato: (base relativa a TEX, tile, macro, texture macro)
CONFRONTO = [
    ("legno", ((0.0, -4.0, 1.7), (80, 0, 0)), ("v2/T_Ponte_Legno_v2", 6.0, 0.20, V2), ("v3/T_Ponte_Legno_v3", 6.0, 0.20, V2)),
    ("segnaletica", ((0.0, -6.0, 1.7), (74, 0, 0)), ("viale/T_Viale_Segnaletica", 1.0, 0.0, None),
     ("v3/T_Viale_Segnaletica_v2", 2.0, 0.0, None)),
    ("cubetti", ((0.0, -9.0, 3.5), (68, 0, 0)), ("v2/T_Pav_Cubetti_v2", 2.8, 0.30, V2), ("v3/T_Pav_Cubetti_v3", 5.6, 0.30, V2)),
    ("prato", ((0.0, -14.0, 5.0), (72, 0, 0)), ("v2/T_Morin_Prato_v2", 4.0, 0.45, V2), ("v3/T_Morin_Prato_v3", 8.0, 0.60, V3P)),
]


def confronto_setup():
    sc = bpy.context.scene
    pl = t2.confronto_setup()
    pl.scale = (3, 3, 1)                         # 120 x 120 m
    bpy.context.view_layer.objects.active = pl
    pl.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    # strisce pedonali: 9 strisce 0,5 x 4 m (passo 1 m) a 3 mm sopra il piano
    import bmesh
    me = bpy.data.meshes.new("CMP_Strisce")
    bm = bmesh.new()
    for i in range(9):
        y0 = -2.0 + i * 1.0
        vs = [bm.verts.new((x, y, 0.003)) for x, y in ((-2, y0), (2, y0), (2, y0 + 0.5), (-2, y0 + 0.5))]
        bm.faces.new(vs)
    bm.to_mesh(me); bm.free()
    st = bpy.data.objects.new("CMP_Strisce", me); sc.collection.objects.link(st)
    sc.render.resolution_x, sc.render.resolution_y = 720, 450
    return pl, st


def confronto_render(out_png=PROJ + "/docs/qa/arte_texture_v3_confronto.png", tmp=None, only=None):
    """only = indici delle righe da (ri)renderizzare; le altre si rileggono dai png in tmp."""
    import tempfile
    tmp = tmp or tempfile.gettempdir()
    sc = bpy.context.scene
    pl = bpy.data.objects.get("CMP_Piano")
    st = bpy.data.objects.get("CMP_Strisce")
    if pl is None or st is None:
        pl, st = confronto_setup()
    cam = sc.camera
    asf = _mat("CMP_Asfalto", "v2/T_Molo_Asfalto_v2", 4.0, 0.35, V2)
    rows = []
    for lab, (cpos, crot), a, b in CONFRONTO:
        cam.location = cpos
        cam.rotation_euler = tuple(np.radians(crot))
        pair = []
        if only is not None and CONFRONTO.index((lab, (cpos, crot), a, b)) not in only:
            pair = [tp.load(f"{tmp}/cmp3_{lab}_{t}.png")[..., :3] for t in ("prima", "dopo")]
        for tag, (base, tile, mac, mtex) in (() if pair else (("prima", a), ("dopo", b))):
            m = _mat(f"CMP3_{lab}_{tag}", base, tile, mac, mtex)
            if lab == "segnaletica":
                pl.data.materials.clear(); pl.data.materials.append(asf)
                st.data.materials.clear(); st.data.materials.append(m)
                st.hide_render = False
            else:
                pl.data.materials.clear(); pl.data.materials.append(m)
                st.hide_render = True
            p = f"{tmp}/cmp3_{lab}_{tag}.png"
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            pair.append(tp.load(p)[..., :3])
        row = np.concatenate([pair[0], np.ones((pair[0].shape[0], 6, 3), np.float32), pair[1]], 1)
        rows.append(row)
        rows.append(np.ones((6, row.shape[1], 3), np.float32))
    img = np.concatenate(rows[:-1], 0)
    tp.save(img, out_png)
    return out_png, img.shape
