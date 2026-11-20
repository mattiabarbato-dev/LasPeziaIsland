"""morin_texture_v2.py — passaggio texture per il realismo (2026-11-20).

Rigenera le texture dei materiali peggiori dell'audit (docs/uefn_arte.md §35.D) con nomi nuovi `_v2`
in blender/textures/v2/. Fonti: Poly Haven (CC0) scaricate in blender/textures/src/<asset>/, foto dell'utente
solo come riferimento colore. Elenco, tiling e parametri MI: docs/texture_v2.md.

Uso dalla console Python di Blender (o via MCP):
    import sys, importlib; sys.path.append(r".../blender/scripts")
    import morin_texture_v2 as t2; importlib.reload(t2)
    t2.make_all()            # oppure le singole make_*()

Convenzioni:
- array float32 HxWxC, riga 0 in ALTO, valori come salvati nel PNG (D in sRGB, N e ORM lineari);
- normal map DirectX (verde invertito, come UE), ORM = R AO, G Roughness, B Metallic;
- le altezze sono in millimetri e la normal map si ricava con la pendenza reale (strength = px per mm).
"""
import os

import bpy
import numpy as np

import morin_texphoto as tp

PROJ = r"C:\Users\matti\Documents\LaSpeziaFortnite\LaSpezia-Fortnite"
TEX = PROJ + "/blender/textures"
SRC = TEX + "/src"
OUT = TEX + "/v2"


# =============================================================================================================
# utilita'
# =============================================================================================================
def c8(rgb):
    return np.asarray(rgb, np.float32) / 255.0


def lum(a):
    return tp.lum(a)


def src(asset, m, res="4k"):
    """Mappa Poly Haven (jpg) come float32. diff -> HxWx3 (sRGB), nor_gl -> HxWx3, altre -> HxW."""
    p = f"{SRC}/{asset}/{asset}_{m}_{res}.jpg"
    a = tp.load(p)[..., :3]
    if m in ("diff", "nor_gl"):
        return a
    return a[..., 0].copy()


def resample(a, S, rep=1.0, S2=None):
    """Campiona una texture periodica su una tela S x S2 che ne contiene `rep` ripetizioni (rep puo' essere
    (rx, ry)). Pre-filtro gaussiano periodico se si rimpicciolisce, per non avere aliasing."""
    S2 = S2 or S
    rx, ry = (rep, rep) if np.isscalar(rep) else rep
    h, w = a.shape[:2]
    f = max(w * rx / S, h * ry / S2)
    if f > 1.3:
        a = tp.blur(a, 0.45 * f)
    y = (np.arange(S2, dtype=np.float32) + 0.5) * h * ry / S2 - 0.5
    x = (np.arange(S, dtype=np.float32) + 0.5) * w * rx / S - 0.5
    x = np.mod(x, w); y = np.mod(y, h)
    x0 = np.floor(x).astype(np.int32); y0 = np.floor(y).astype(np.int32)
    x1 = (x0 + 1) % w; y1 = (y0 + 1) % h
    fx = (x - x0)[None, :]; fy = (y - y0)[:, None]
    if a.ndim == 3:
        fx = fx[..., None]; fy = fy[..., None]
    top = a[y0][:, x0] * (1 - fx) + a[y0][:, x1] * fx
    bot = a[y1][:, x0] * (1 - fx) + a[y1][:, x1] * fx
    return (top * (1 - fy) + bot * fy).astype(np.float32)


def gl_to_dx(n):
    n = n.copy()
    n[..., 1] = 1.0 - n[..., 1]
    return n


def blend_normals(base, detail, k=1.0):
    """Whiteout blend di due normal map (stessa convenzione), k scala il dettaglio."""
    a = base * 2 - 1
    b = detail * 2 - 1
    b[..., :2] *= k
    n = np.dstack([a[..., 0] + b[..., 0], a[..., 1] + b[..., 1], a[..., 2] * b[..., 2]])
    n /= np.linalg.norm(n, axis=2, keepdims=True) + 1e-6
    return (n * 0.5 + 0.5).astype(np.float32)


def flat_normal(S, S2=None):
    S2 = S2 or S
    n = np.zeros((S2, S, 3), np.float32)
    n[..., :2] = 0.5
    n[..., 2] = 1.0
    return n


def noise(h, w, sigma, seed):
    r = np.random.default_rng(seed).standard_normal((h, w)).astype(np.float32)
    r = tp.blur(r, sigma)
    return r / (r.std() + 1e-6)


def fbm(h, w, sigmas, seed, weights=None):
    weights = weights or [1.0] * len(sigmas)
    s = sum(wt * noise(h, w, sg, seed + i) for i, (sg, wt) in enumerate(zip(sigmas, weights)))
    return s / (s.std() + 1e-6)


def normal_from_mm(H, ppm, k=1.0):
    """Normal DirectX da altezza in mm con pendenza reale (ppm = pixel per metro)."""
    return tp.normal_dx(H, k * ppm / 1000.0)


def cavity_ao(H, sigma, k, lo=0.4):
    return np.clip(1.0 - k * np.maximum(tp.blur(H, sigma) - H, 0), lo, 1.0).astype(np.float32)


def detail_from(rgb, sigma):
    """Dettaglio di luminanza (media 1) e crominanza relativa di una foto."""
    L = lum(rgb)
    hp = tp.highpass(L, sigma)
    return hp


def recolor(rgb, target, sat=0.35, contrast=1.0):
    """Porta una foto al colore medio `target` (sRGB 0..1): conserva la luminanza relativa (x contrast)
    e una frazione `sat` della sua crominanza, il resto prende la tinta del target. Lavora in lineare."""
    lin = np.clip(rgb, 0, 1) ** 2.2
    L = lum(lin)
    Lm = float(L.mean())
    rel = 1.0 + (L / max(Lm, 1e-5) - 1.0) * contrast
    chroma = lin / np.maximum(L, 1e-4)[..., None]
    cm = chroma.reshape(-1, 3).astype(np.float64).mean(0).astype(np.float32)
    t = np.asarray(target, np.float32) ** 2.2
    tl = float(lum(t[None, None])[0, 0])
    tch = t / tl
    ch = tch[None, None] * (1 - sat) + (chroma / cm[None, None]) * tch[None, None] * sat
    out = tl * rel[..., None] * ch
    return np.clip(out, 0, 1) ** (1 / 2.2)


def set_mean(rgb, target):
    """Scala (in lineare) ogni canale perche' la media sRGB sia `target`."""
    lin = np.clip(rgb, 0, 1) ** 2.2
    t = np.asarray(target, np.float32) ** 2.2
    m = lin.reshape(-1, 3).astype(np.float64).mean(0).astype(np.float32)
    return np.clip(lin * (t / np.maximum(m, 1e-5))[None, None], 0, 1) ** (1 / 2.2)


def save_set(name, D, N, ORM, sub=""):
    d = OUT + (("/" + sub) if sub else "")
    os.makedirs(d, exist_ok=True)
    out = []
    for k, a in (("D", D), ("N", N), ("ORM", ORM)):
        if a is None:
            continue
        p = f"{d}/{name}_{k}.png"
        tp.save(np.clip(a, 0, 1), p)
        out.append(p)
    return out


def stats(name):
    p = f"{OUT}/{name}_D.png"
    a = tp.load(p)
    m = a[..., :3].reshape(-1, 3).astype(np.float64).mean(0)
    o = tp.load(f"{OUT}/{name}_ORM.png")[..., :3].reshape(-1, 3).astype(np.float64)
    return f"{name}: {a.shape[1]}x{a.shape[0]} D mean {np.round(m * 255).astype(int)} max {a[..., :3].max():.2f} " \
           f"| R mean {o[:, 1].mean():.2f} [{np.percentile(o[:, 1], 5):.2f}-{np.percentile(o[:, 1], 95):.2f}] AO {o[:, 0].mean():.2f}"


# =============================================================================================================
# macro-variazione
# =============================================================================================================
def make_macrovar(S=2048, seed=777):
    """T_Morin_MacroVar: rumore morbido a 3 ottave + chiazze, scala di grigi, media 0,5, tileable.
    Pensata per 32 m di tile (64 px/m): chiazze da ~2 a ~15 m."""
    n = fbm(S, S, [180, 70, 25, 8], seed, [1.0, 0.7, 0.35, 0.12])
    blot = np.clip(noise(S, S, 45, seed + 10) - 0.8, 0, None)
    v = 0.5 + 0.13 * n - 0.10 * blot / (blot.max() + 1e-6)
    v = np.clip(v, 0.12, 0.88)
    os.makedirs(OUT, exist_ok=True)
    tp.save(np.dstack([v, v, v]), f"{OUT}/T_Morin_MacroVar.png")
    return f"MacroVar mean {v.mean():.3f} p5 {np.percentile(v, 5):.3f} p95 {np.percentile(v, 95):.3f}"


# =============================================================================================================
# 1. lastre del camminamento (MI_Pav_Lastre, world projection)
# =============================================================================================================
def make_lastre(S=4096, seed=4801):
    """T_Pav_Lastre_v2: lastre 40 x 60 cm (lato lungo lungo Y = verso la citta'), corsi continui lungo Y ogni 40 cm,
    teste sfalsate; tile 4,8 m (12 x 8 lastre). Superficie di ogni lastra da rock_surface (Poly Haven, CC0) con
    offset casuale; colore grigio caldo tarato su ref/foto/pavimentazione (pav_1, 'pavimento verso il ponte'):
    albedo medio ~ (150, 145, 135) sRGB. Giunti 6 mm con terra e un po' di muschio (foto), spigoli consumati."""
    rng = np.random.default_rng(seed)
    T, CW, SL = 4.8, 0.40, 0.60
    NC, NR = int(round(T / CW)), int(round(T / SL))
    ppm = S / T
    # sorgente ridotta a ppm (rock_surface: 2 m)
    sd = resample(src("rock_surface", "diff"), int(round(2.0 * ppm)))
    sdisp = resample(src("rock_surface", "disp"), int(round(2.0 * ppm)))
    srough = resample(src("rock_surface", "rough"), int(round(2.0 * ppm)))
    hs, ws = sd.shape[:2]
    sd = recolor(sd, c8((150, 145, 135)), sat=0.25, contrast=0.9)
    sdisp = (sdisp - sdisp.mean()) / (sdisp.std() + 1e-6)
    srough = (srough - srough.mean()) / (srough.std() + 1e-6)

    x = (np.arange(S, dtype=np.float32) + 0.5) / ppm
    U = np.broadcast_to(x[None, :], (S, S))
    V = np.broadcast_to(x[:, None], (S, S))
    col = np.minimum((U / CW).astype(np.int32), NC - 1)
    uin = U - col * CW
    off = (np.arange(NC) % 2) * SL / 2 + rng.uniform(-0.08, 0.08, NC)
    vp = np.mod(V - off[col], T)
    row = np.minimum((vp / SL).astype(np.int32), NR - 1)
    vin = vp - row * SL
    sid = col * NR + row
    del vp
    NS = NC * NR
    # bordo irregolare
    jit = noise(S, S, 25, seed + 1) * 0.0006 + noise(S, S, 3, seed + 6) * 0.00025
    d = np.minimum(np.minimum(uin, CW - uin), np.minimum(vin, SL - vin)) + jit
    joint = d < 0.0026
    # campionamento per lastra con offset e rotazione di 180 gradi casuali
    oy = rng.integers(0, hs, NS); ox = rng.integers(0, ws, NS); fl = rng.random(NS) < 0.5
    yy = np.arange(S, dtype=np.int32)[:, None]; xx = np.arange(S, dtype=np.int32)[None, :]
    sy = np.where(fl[sid], -yy, yy) + oy[sid]
    sx = np.where(fl[sid], -xx, xx) + ox[sid]
    sy %= hs; sx %= ws
    D = sd[sy, sx]
    hd = sdisp[sy, sx]
    rd = srough[sy, sx]
    del sy, sx
    # tinta per lastra: luminosita', caldo/freddo, qualche lastra sostituita piu' chiara
    br = rng.normal(1.0, 0.035, NS).astype(np.float32)
    wm = rng.normal(0.0, 0.018, NS).astype(np.float32)
    new = rng.random(NS) < 0.06
    br[new] *= 1.07
    wm[new] -= 0.02
    lin = D ** 2.2 * (br[sid] ** 2.2)[..., None]
    lin[..., 0] *= 1 + wm[sid]
    lin[..., 2] *= 1 - wm[sid]
    # sporco a bassa frequenza (non si ripete dentro il tile: 4,8 m) e sporco vicino ai giunti
    dirt = fbm(S, S, [140, 40], seed + 2)
    lin *= (1 + 0.06 * dirt)[..., None]
    edge = np.clip(1 - d / 0.025, 0, 1)
    lin *= (1 - 0.18 * edge ** 2)[..., None]
    # macchie (olio, gomme)
    st = np.zeros((S, S), np.float32)
    for _ in range(26):
        cy, cx = rng.integers(0, S, 2); r = rng.uniform(0.015, 0.06) * ppm
        rr = int(r * 2.2)
        ys = (np.arange(cy - rr, cy + rr) % S); xs = (np.arange(cx - rr, cx + rr) % S)
        g = np.exp(-((np.arange(-rr, rr)[:, None]) ** 2 + (np.arange(-rr, rr)[None, :]) ** 2) / (r * r))
        st[np.ix_(ys, xs)] = np.maximum(st[np.ix_(ys, xs)], g * rng.uniform(0.3, 0.8))
    lin *= (1 - 0.35 * st)[..., None]
    # giunti: terra scura + muschio
    moss = np.clip(noise(S, S, 30, seed + 3) * 0.6 - 0.35, 0, 1)
    jc = (c8((74, 69, 60)) ** 2.2)[None, None] * (1 - moss[..., None]) + (c8((82, 88, 54)) ** 2.2)[None, None] * moss[..., None]
    jc = jc * (1 + 0.15 * noise(S, S, 2, seed + 4))[..., None]
    lin = np.where(joint[..., None], jc, lin)
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    # altezza (mm): spigoli consumati 8 mm, giunto -6 mm, inclinazione per lastra +-0,6 mm, grana della pietra
    tx = rng.normal(0, 1.5, NS).astype(np.float32); ty = rng.normal(0, 1.0, NS).astype(np.float32)
    H = 0.7 * hd + tx[sid] * (uin / CW - 0.5) + ty[sid] * (vin / SL - 0.5)
    H -= 2.5 * np.clip(1 - d / 0.008, 0, 1) ** 2
    H = np.where(joint, -6.0, H)
    H = tp.blur(H, 0.7)
    N = normal_from_mm(H, ppm)
    # roughness e AO
    wear = fbm(S, S, [220, 60], seed + 5)
    rgh = 0.84 + rng.normal(0, 0.03, NS).astype(np.float32)[sid] + 0.04 * rd - 0.035 * np.clip(wear, -2, 2) - 0.08 * st
    rgh = np.where(joint, 0.96, rgh)
    ao = cavity_ao(H, 6, 0.08, 0.45) * np.where(joint, 0.6, 1.0)
    ORM = np.dstack([ao, np.clip(rgh, 0.5, 1.0), np.zeros_like(ao)])
    return save_set("T_Pav_Lastre_v2", D, N, ORM)


# =============================================================================================================
# 2. cubetti a coda di pavone (MI_Pav_Cubetti, world projection)
# =============================================================================================================
def make_cubetti(S=4096):
    """T_Pav_Cubetti_v2: porfido a ventagli da patterned_cobblestone (Poly Haven, CC0, 2,5 m, cubetti ~8 cm);
    con Tile_m 2,8 il cubetto misura ~9 cm e il ventaglio ~1,3 m, come in ref/foto/pavimentazione/pav_palme.png.
    Colore: grigio-bruno caldo (porfido al sole nella foto), meno magenta della sorgente."""
    d = src("patterned_cobblestone", "diff")
    n = gl_to_dx(src("patterned_cobblestone", "nor_gl"))
    r = src("patterned_cobblestone", "rough")
    ao = src("patterned_cobblestone", "ao")
    if d.shape[0] != S:
        d, n, r, ao = (resample(a, S) for a in (d, n, r, ao))
    D = recolor(d, c8((120, 113, 106)), sat=0.55, contrast=1.15)
    # i giunti della sorgente (scuri e verdastri) restano: recolor conserva la luminanza relativa
    nn = n * 2 - 1
    nn[..., :2] *= 1.25
    nn /= np.linalg.norm(nn, axis=2, keepdims=True)
    N = nn * 0.5 + 0.5
    rn = (r - r.mean()) / (r.std() + 1e-6)
    R = np.clip(0.80 + 0.06 * rn, 0.6, 0.97)
    ORM = np.dstack([np.clip(ao, 0.35, 1), R, np.zeros_like(R)])
    return save_set("T_Pav_Cubetti_v2", D, N, ORM)


# =============================================================================================================
# 3. fascia e cordoli in pietra bianca (MI_Pav_Fascia, world projection)
# =============================================================================================================
def make_fascia(S=2048, seed=2001):
    """T_Pav_Fascia_v2: pietra chiara consumata, tile 2 m. Grana da rock_boulder_dry (Poly Haven, CC0, 1,8 m -> 2 m),
    colore tarato su pav_palme.png (fasce al sole, grigio-crema), albedo medio ~ (176, 171, 160) sRGB, massimo ~0,8;
    sporco scuro a chiazze e a strisce (consumo dei passi), roughness 0,6-0,8 (pietra levigata dall'uso, non plastica)."""
    d = resample(src("rock_boulder_dry", "diff", "2k"), S)
    n = gl_to_dx(resample(src("rock_boulder_dry", "nor_gl", "2k"), S))
    r = resample(src("rock_boulder_dry", "rough", "2k"), S)
    ao = resample(src("rock_boulder_dry", "ao", "2k"), S)
    D = recolor(d, c8((180, 175, 164)), sat=0.3, contrast=0.75)
    dirt = np.clip(fbm(S, S, [90, 30], seed) * 0.5 + 0.1, 0, None)
    spots = np.clip(noise(S, S, 4, seed + 1) - 2.2, 0, None)
    lin = D ** 2.2
    lin *= (1 - 0.16 * np.clip(dirt, 0, 1.5) - 0.25 * np.clip(spots, 0, 1))[..., None]
    lin[..., 2] *= (1 - 0.04 * np.clip(dirt, 0, 1.5))
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    rn = (r - r.mean()) / (r.std() + 1e-6)
    R = np.clip(0.68 + 0.05 * rn + 0.08 * np.clip(dirt, 0, 1.5), 0.5, 0.95)
    nn = n * 2 - 1; nn[..., :2] *= 0.7; nn /= np.linalg.norm(nn, axis=2, keepdims=True); N = nn * 0.5 + 0.5
    ORM = np.dstack([np.clip(ao, 0.5, 1), R, np.zeros_like(R)])
    return save_set("T_Pav_Fascia_v2", D, N, ORM)


# =============================================================================================================
# helper per le texture ritarate (stesso layout UV della v1)
# =============================================================================================================
def old(path_noext, S=None):
    D = tp.load(f"{TEX}/{path_noext}_D.png")
    N = tp.load(f"{TEX}/{path_noext}_N.png")[..., :3]
    O = tp.load(f"{TEX}/{path_noext}_ORM.png")[..., :3]
    if S and D.shape[0] != S:
        D, N, O = (resample(a, S) for a in (D, N, O))
        N = N * 2 - 1; N /= np.linalg.norm(N, axis=2, keepdims=True) + 1e-6; N = N * 0.5 + 0.5
    return D, N, O


def photo_detail(asset, res, S, rep, sigma, S2=None, rep2=None):
    """Luminanza in alta frequenza (media 1), normal DX e roughness normalizzata di una sorgente Poly Haven."""
    r2 = (rep, rep2 if rep2 is not None else rep)
    d = resample(src(asset, "diff", res), S, r2, S2)
    hp = tp.highpass(lum(d), sigma)
    n = gl_to_dx(resample(src(asset, "nor_gl", res), S, r2, S2))
    rr = resample(src(asset, "rough", res), S, r2, S2)
    rr = (rr - rr.mean()) / (rr.std() + 1e-6)
    return hp, n, rr


# =============================================================================================================
# 4. blocchi del ciglio della banchina (MI_Banchina_Blocchi, UV ~2,5 m)
# =============================================================================================================
def make_blocchi(S=2048, seed=2501):
    """T_Banchina_Blocchi_v2: layout della v1 (stesse UV), albedo abbassato da ~0,75 a ~0,68 e piu' variato:
    grana di rock_boulder_dry (CC0), macchie scure larghe, aloni di salsedine, roughness 0,75-0,9."""
    D0, N0, O0 = old("banchina_v2/T_Banchina_Blocchi", S)
    hp, n, rr = photo_detail("rock_boulder_dry", "2k", S, 1, 24)
    base = recolor(D0[..., :3], c8((176, 174, 167)), sat=0.2, contrast=1.5)
    lin = base ** 2.2 * np.clip(hp, 0.6, 1.5)[..., None] ** 0.9
    st = fbm(S, S, [110, 35], seed)
    lin *= (1 + 0.09 * np.clip(st, -2.5, 2.5))[..., None]
    salt = np.clip(noise(S, S, 18, seed + 1) - 1.4, 0, None)
    lin = lin * (1 - 0.2 * salt[..., None]) + 0.2 * salt[..., None] * (c8((200, 198, 190)) ** 2.2)
    lin[..., 2] *= 0.985
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    N = blend_normals(N0, n, 0.8)
    R = np.clip(0.80 + 0.05 * rr - 0.03 * np.clip(st, -2, 2), 0.6, 0.95)
    ORM = np.dstack([O0[..., 0], R, np.zeros_like(R)])
    return save_set("T_Banchina_Blocchi_v2", D, N, ORM)


# =============================================================================================================
# 13. paramento della banchina (MI_Banchina_Paramento, UV ~3,3 m; anche ponte e Molo Italia)
# =============================================================================================================
def make_paramento(S=2048, seed=3301):
    """T_Banchina_Paramento_v2: layout v1, schiarito da ~0,23 a ~0,38 sRGB (pietra grigio-bruna umida, non nera),
    grana di seaside_rock (CC0), chiazze verdastre di alghe e scolature, roughness 0,65-0,85."""
    D0, N0, O0 = old("T_Banchina_Paramento", S)
    hp, n, rr = photo_detail("seaside_rock", "2k", S, 2, 20)
    base = recolor(D0[..., :3], c8((100, 97, 90)), sat=0.3, contrast=1.25)
    lin = base ** 2.2 * np.clip(hp, 0.6, 1.5)[..., None] ** 0.8
    alg = np.clip(fbm(S, S, [60, 15], seed) * 0.6 - 0.3, 0, 1)
    lin = lin * (1 - 0.45 * alg[..., None]) + 0.45 * alg[..., None] * (c8((62, 70, 48)) ** 2.2)
    lin *= (1 + 0.08 * fbm(S, S, [150], seed + 1))[..., None]
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    N = blend_normals(N0, n, 0.7)
    R = np.clip(0.78 + 0.05 * rr - 0.12 * alg, 0.5, 0.95)
    ORM = np.dstack([O0[..., 0], R, np.zeros_like(R)])
    return save_set("T_Banchina_Paramento_v2", D, N, ORM)


# =============================================================================================================
# 5. prato (MI_Morin_Prato, UV 4 m; MI_Morin_Prato_Mondo Tile_m 4)
# =============================================================================================================
def make_prato(S=2048, seed=4001):
    """T_Morin_Prato_v2: tile 4 m. Struttura dei fili dalla v1 (procedurale) + leafy_grass (CC0, 2 m, x2);
    colore verde naturale tarato su ref/foto/arredi/giardini.webp: tre tinte a chiazze (verde prato, trifoglio piu'
    scuro, zone secche giallo-paglia) e margheritine bianche sparse. Meno saturo della v1 (niente lime)."""
    D0, N0, O0 = old("viale/T_Morin_Prato", S)
    blades = lum(D0[..., :3]); blades = blades / blades.mean()
    hp, n, rr = photo_detail("leafy_grass", "2k", S, 2, 16)
    c_g = c8((84, 108, 46)) ** 2.2
    c_c = c8((62, 92, 40)) ** 2.2
    c_y = c8((124, 120, 66)) ** 2.2
    m1 = np.clip(fbm(S, S, [80, 25], seed) * 0.3 + 0.35, 0, 1) * 0.7     # trifoglio
    m2 = np.clip(fbm(S, S, [140, 40], seed + 1) * 0.6 - 0.55, 0, 1)      # secco
    col = c_g[None, None] * (1 - m1[..., None]) + c_c[None, None] * m1[..., None]
    col = col * (1 - m2[..., None]) + c_y[None, None] * m2[..., None]
    v = np.clip(blades, 0.5, 1.6) ** 0.8 * np.clip(hp, 0.6, 1.5) ** 0.6
    lin = col * v[..., None] * (1 + 0.07 * fbm(S, S, [200], seed + 2))[..., None]
    # margheritine (bianche con cuore giallo), a gruppi
    rng = np.random.default_rng(seed + 3)
    grp = np.clip(noise(S, S, 60, seed + 4) - 0.6, 0, None)
    p = rng.random((S, S)) < (0.0016 * grp / (grp.max() + 1e-6))
    ys, xs = np.nonzero(p)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            w = 0.85 if (dy or dx) else 0.95
            yy = (ys + dy) % S; xx = (xs + dx) % S
            lin[yy, xx] = lin[yy, xx] * (1 - w) + w * (c8((214, 214, 204)) ** 2.2)
    lin[ys, xs] = c8((200, 170, 60)) ** 2.2
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    N = blend_normals(N0, n, 0.6)
    R = np.clip(0.88 + 0.04 * rr, 0.75, 1.0)
    ORM = np.dstack([O0[..., 0], R, np.zeros_like(R)])
    return save_set("T_Morin_Prato_v2", D, N, ORM)


# =============================================================================================================
# 6. asfalti
# =============================================================================================================
def _asfalto(name, asset, src_m, tile_m, target, S, seed, n_patch=3, n_oil=10):
    d = src(asset, "diff"); nrm = src(asset, "nor_gl"); r = src(asset, "rough"); ao = src(asset, "ao")
    rep = max(1, int(round(tile_m / src_m)))
    d, nrm, r, ao = (resample(a, S, rep) for a in (d, nrm, r, ao))
    nrm = gl_to_dx(nrm)
    D = recolor(d, target, sat=0.15, contrast=1.0)
    lin = D ** 2.2
    ppm = S / tile_m
    rng = np.random.default_rng(seed)
    big = fbm(S, S, [S / 12, S / 40], seed)
    lin *= (1 + 0.07 * np.clip(big, -2.5, 2.5))[..., None]
    rough_add = np.zeros((S, S), np.float32)
    # rattoppi: rettangoli morbidi di asfalto piu' nuovo (scuro, piu' liscio)
    yy = np.arange(S)[:, None]; xx = np.arange(S)[None, :]
    for _ in range(n_patch):
        cy, cx = rng.integers(0, S, 2)
        hh, ww = rng.uniform(0.6, 1.8, 2) * ppm
        dy = np.minimum(np.abs(yy - cy), S - np.abs(yy - cy)); dx = np.minimum(np.abs(xx - cx), S - np.abs(xx - cx))
        m = np.clip((hh - dy) / (0.03 * ppm), 0, 1) * np.clip((ww - dx) / (0.03 * ppm), 0, 1)
        lin *= (1 - 0.18 * m)[..., None]
        rough_add -= 0.06 * m
    # macchie d'olio
    oil = np.zeros((S, S), np.float32)
    for _ in range(n_oil):
        cy, cx = rng.integers(0, S, 2); rad = rng.uniform(0.08, 0.35) * ppm
        rr_ = int(rad * 2.5)
        ys = (np.arange(cy - rr_, cy + rr_) % S); xs = (np.arange(cx - rr_, cx + rr_) % S)
        g = np.exp(-((np.arange(-rr_, rr_)[:, None]) ** 2 + (np.arange(-rr_, rr_)[None, :] * 0.8) ** 2) / (rad * rad))
        oil[np.ix_(ys, xs)] = np.maximum(oil[np.ix_(ys, xs)], g * rng.uniform(0.3, 0.7))
    oil = tp.blur(oil, 2) * np.clip(0.75 + 0.25 * noise(S, S, 4, seed + 7), 0, 1)
    lin *= (1 - 0.35 * oil)[..., None]
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    rn = (r - r.mean()) / (r.std() + 1e-6)
    R = np.clip(0.88 + 0.05 * rn + rough_add - 0.10 * oil - 0.03 * np.clip(big, -2, 2), 0.45, 1.0)
    ORM = np.dstack([np.clip(ao, 0.4, 1) ** 0.6, R, np.zeros_like(R)])
    return save_set(name, D, nrm, ORM)


def make_asfalto_parcheggio(S=4096):
    """T_Parcheggio_Asfalto_v2: tile 8 m (come la v1), asphalt_04 (CC0, 4,04 m) x2 (asphalt_02 scartato: crepe ripetute);
    grigio caldo ~ (96, 94, 91) sRGB, 3 rattoppi morbidi, macchie d'olio, variazione larga."""
    return _asfalto("T_Parcheggio_Asfalto_v2", "asphalt_04", 4.04, 8.0, c8((96, 94, 91)), S, 801, 3, 14)


def make_asfalto_molo(S=4096):
    """T_Molo_Asfalto_v2: tile 4 m (come la v1), asphalt_04 (CC0, 4,04 m); grigio neutro-caldo ~ (90, 89, 86)."""
    return _asfalto("T_Molo_Asfalto_v2", "asphalt_04", 4.04, 4.0, c8((90, 89, 86)), S, 401, 1, 5)


# =============================================================================================================
# 7. cemento del Molo Italia (MI_MoloItalia_Cemento, UV 4 m)
# =============================================================================================================
def make_cemento(S=4096, seed=4401):
    """T_MoloItalia_Cemento_v2: dirty_concrete (CC0, 3 m -> 4 m), grigio caldo chiaro ~ (164, 161, 153) sRGB
    (albedo <= 0,72), niente griglia di piastrelle, sporco e colature a bassa frequenza."""
    d = src("dirty_concrete", "diff"); nrm = gl_to_dx(src("dirty_concrete", "nor_gl"))
    r = src("dirty_concrete", "rough"); ao = src("dirty_concrete", "ao")
    if d.shape[0] != S:
        d, nrm, r, ao = (resample(a, S) for a in (d, nrm, r, ao))
    D = recolor(d, c8((164, 161, 153)), sat=0.25, contrast=0.85)
    lin = D ** 2.2 * (1 + 0.06 * fbm(S, S, [S / 10, S / 40], seed))[..., None]
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    rn = (r - r.mean()) / (r.std() + 1e-6)
    R = np.clip(0.86 + 0.05 * rn, 0.65, 1.0)
    ORM = np.dstack([np.clip(ao, 0.45, 1) ** 0.6, R, np.zeros_like(R)])
    return save_set("T_MoloItalia_Cemento_v2", D, nrm, ORM)


# =============================================================================================================
# 8. scogliera (MI_Molo_Scogliera, UV ~2,5-2,9 m, v = 0 sull'acqua)
# =============================================================================================================
def make_scogliera(S=2048, seed=2601):
    """T_Molo_Scogliera_v2: seaside_rock (CC0, 2 m -> 2,5 m), calcare grigio-ocra ~ (138, 130, 116) sRGB;
    come la v1 la fascia bassa (v < 0,12) e' scura di alghe e bagnata fino a v ~0,25 (lucida)."""
    d = resample(src("seaside_rock", "diff", "2k"), S); nrm = gl_to_dx(resample(src("seaside_rock", "nor_gl", "2k"), S))
    r = resample(src("seaside_rock", "rough", "2k"), S); ao = resample(src("seaside_rock", "ao", "2k"), S)
    D = recolor(d, c8((138, 130, 116)), sat=0.45, contrast=1.1)
    lin = D ** 2.2
    v = 1 - (np.arange(S, dtype=np.float32)[:, None] + 0.5) / S          # 0 in basso
    jag = 0.025 * noise(1, S, 12, seed)[0][None, :] + 0.01 * noise(S, S, 6, seed + 1)
    alg = np.clip((0.12 + jag - v) / 0.03, 0, 1)
    wet = np.clip((0.26 + jag - v) / 0.08, 0, 1)
    lin *= (1 - 0.35 * wet)[..., None]
    lin = lin * (1 - alg[..., None]) + alg[..., None] * (c8((48, 54, 36)) ** 2.2) * np.clip(tp.highpass(lum(D), 10), 0.5, 1.6)[..., None]
    lin *= (1 + 0.07 * fbm(S, S, [120], seed + 2))[..., None]
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    rn = (r - r.mean()) / (r.std() + 1e-6)
    R = np.clip(0.85 + 0.05 * rn - 0.4 * wet, 0.35, 1.0)
    ORM = np.dstack([np.clip(ao, 0.35, 1), R, np.zeros_like(R)])
    return save_set("T_Molo_Scogliera_v2", D, nrm, ORM)


# =============================================================================================================
# 9. corten (MI_Morin_Corten, UV 1 m)
# =============================================================================================================
def make_corten(S=2048, seed=1001):
    """T_Morin_Corten_v2: rust_coarse_01 (CC0, 2,2 m): ritaglio di 1 m reso tileable, cosi' la grana resta a
    scala reale. Colore mappato su una rampa bruno scuro -> arancio corten, chiazze piu' scure e colature verticali,
    roughness 0,75-0,95."""
    d = src("rust_coarse_01", "diff"); nrm = src("rust_coarse_01", "nor_gl"); r = src("rust_coarse_01", "rough")
    ao = src("rust_coarse_01", "ao")
    px = int(round(d.shape[1] / 2.2))
    d, nrm, r, ao = (tp.tileable(a[:px, :px]) for a in (d, nrm, r, ao))
    d, nrm, r, ao = (resample(a, S) for a in (d, nrm, r, ao))
    nrm = nrm * 2 - 1; nrm /= np.linalg.norm(nrm, axis=2, keepdims=True) + 1e-6; nrm = gl_to_dx(nrm * 0.5 + 0.5)
    L = lum(d ** 2.2)
    t = np.clip((L - np.percentile(L, 2)) / (np.percentile(L, 98) - np.percentile(L, 2)), 0, 1)[..., None]
    dark = c8((74, 40, 24)) ** 2.2; mid = c8((128, 66, 34)) ** 2.2; hi = c8((170, 96, 50)) ** 2.2
    lin = np.where(t < 0.5, dark + (mid - dark) * (t * 2), mid + (hi - mid) * (t * 2 - 1))
    blot = fbm(S, S, [140, 40], seed)
    lin *= (1 + 0.12 * np.clip(blot, -2, 2))[..., None]
    col = np.clip(resample(noise(1, 256, 2, seed + 1), S, 1, 1)[0] * 0.8, 0, None)[None, :]
    streak = col * np.clip(fbm(S, S, [70], seed + 2) + 0.3, 0, 1)
    lin *= (1 - 0.15 * np.clip(streak, 0, 1.5))[..., None]
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    rn = (r - r.mean()) / (r.std() + 1e-6)
    R = np.clip(0.84 + 0.05 * rn + 0.03 * np.clip(blot, -2, 2), 0.65, 1.0)
    ORM = np.dstack([np.clip(ao, 0.4, 1), R, np.zeros_like(R)])
    return save_set("T_Morin_Corten_v2", D, nrm, ORM)


# =============================================================================================================
# 10. legno del ponte (MI_Ponte_Legno, UV 6 m) — stesso layout della v1 (morin_ponte.make_tex_legno, seed 13)
# =============================================================================================================
def make_ponte_legno(S=4096, seed=13):
    """T_Ponte_Legno_v2: tavolato 6 x 6 m, 44 doghe da 13,6 cm (layout identico alla v1). Grana fotografica da
    wood_planks_grey (CC0, 1,5 m, 5 doghe): ogni segmento di doga preleva una striscia dentro una sola doga della
    sorgente (niente fughe della foto). Grigio-bruno invecchiato tarato su ref/foto/ponte (~ (112, 107, 99) sRGB),
    tinta per doga +-8 %, qualche doga piu' scura o argentata; fughe 6 mm scure, viti e borchie come la v1."""
    WOOD_W = 6.0
    rng = np.random.default_rng(seed)
    ppm = S / WOOD_W
    NP = 44
    pw = WOOD_W / NP
    u = (np.arange(S, dtype=np.float32) + 0.5) / ppm
    U = np.broadcast_to(u[None, :], (S, S)); V = np.broadcast_to(u[:, None], (S, S))
    pi = np.floor(U / pw).astype(np.int32) % NP
    uin = U / pw - np.floor(U / pw)
    nb = rng.choice([2, 3], NP)
    off = rng.uniform(0, WOOD_W, NP).astype(np.float32)
    seg = WOOD_W / nb
    vp = np.mod(V - off[pi], WOOD_W)
    bi = np.floor(vp / seg[pi]).astype(np.int32)
    vin = vp - bi * seg[pi]
    bid = pi * 4 + bi
    del vp
    rng.normal(1.0, 0.05, NP * 4); rng.normal(0.0, 0.015, NP * 4); rng.integers(0, S, NP * 4)   # come la v1
    r2 = np.random.default_rng(seed + 100)
    # sorgente a ppm: 1,5 m -> 1024 px; doghe della foto ogni ~0,3 m
    sd = resample(src("wood_planks_grey", "diff"), int(round(1.5 * ppm)))
    sdisp = resample(src("wood_planks_grey", "disp"), int(round(1.5 * ppm)))
    hs, ws = sd.shape[:2]
    L = lum(sd ** 2.2)
    cm = L.mean(0)
    bad = cm < cm.mean() - 1.2 * cm.std()
    badw = np.convolve(np.concatenate([bad, bad[:64]]).astype(np.float32), np.ones(9), "same")[:ws] > 0
    wpx = int(np.ceil(pw * ppm)) + 2
    ok = np.array([not badw[(np.arange(s, s + wpx)) % ws].any() for s in range(ws)])
    starts = np.nonzero(ok)[0]
    G = tp.highpass(L, 40)
    G = (G - 1.0) / (G.std() + 1e-6)
    hd = (sdisp - sdisp.mean()) / (sdisp.std() + 1e-6)
    NB = NP * 4
    sx0 = starts[r2.integers(0, len(starts), NB)]
    sy0 = r2.integers(0, hs, NB)
    fl = r2.random(NB) < 0.5
    col_in = (uin * pw * ppm).astype(np.int32)
    yy = np.arange(S, dtype=np.int32)[:, None]
    sy = (np.where(fl[bid], -yy, yy) + sy0[bid]) % hs
    sx = (sx0[bid] + col_in) % ws
    grain = G[sy, sx]
    hgr = hd[sy, sx]
    del sy, sx
    tint = r2.normal(1.0, 0.08, NB).astype(np.float32)
    warm = r2.normal(0.0, 0.025, NB).astype(np.float32)
    kind = r2.random(NB)
    tint[kind < 0.10] *= 0.80                                  # doghe piu' scure (sostituite / umide)
    silver = (kind > 0.92)
    tint[silver] *= 1.10
    base = c8((112, 107, 99)) ** 2.2
    low = fbm(S, S, [S / 30, S / 120], seed + 3)
    t = tint[bid] * (1 + 0.16 * np.clip(grain, -3, 3)) * (1 + 0.05 * low)
    lin = base[None, None, :] * np.clip(t, 0.2, 2.0)[..., None]
    lin[..., 0] *= 1 + warm[bid]
    lin[..., 2] *= 1 - warm[bid] + 0.03 * silver[bid]
    H = 0.25 * hgr - 0.5 * ((uin - 0.5) * 2) ** 2           # mm
    R = 0.80 + 0.04 * np.clip(grain, -2, 2) - 0.03 * low + 0.04 * (kind[bid] < 0.10)
    M = np.zeros((S, S), np.float32)
    gu = np.minimum(uin, 1 - uin) * pw
    gap = gu < 0.003
    gv = np.minimum(vin, seg[pi] - vin)
    endj = gv < 0.002
    edge = np.clip(1 - gu / 0.012, 0, 1) * 0.15
    lin *= (1 - edge)[..., None]
    lin[gap | endj] *= 0.10
    H[gap | endj] = -8.0
    R[gap | endj] = 0.95
    del gu, gv, U, V
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    for vt in np.arange(0.0, WOOD_W, 1.5) + 0.4:
        for du in (0.28, 0.72):
            for c in (np.arange(NP) + du) * pw:
                y0, x0 = int(vt * ppm), int(c * ppm)
                r = 3
                yy_, xx_ = np.ogrid[-r:r + 1, -r:r + 1]
                m = (yy_ * yy_ + xx_ * xx_) <= r * r
                sub = np.ix_(np.arange(y0 - r, y0 + r + 1) % S, np.arange(x0 - r, x0 + r + 1) % S)
                d_ = D[sub]; d_[m] *= 0.5; D[sub] = d_
                h_ = H[sub]; h_[m] -= 0.6; H[sub] = h_
    for cu in (1.5, 4.5):
        for vt in np.arange(0.15, WOOD_W, 0.30):
            y0, x0 = int(vt * ppm), int(cu * ppm)
            r = 7
            yy_, xx_ = np.ogrid[-r - 2:r + 3, -r - 2:r + 3]
            dd = np.sqrt(yy_ * yy_ + xx_ * xx_)
            m = dd <= r
            ring = (dd > r) & (dd <= r + 2)
            sub = np.ix_(np.arange(y0 - r - 2, y0 + r + 3) % S, np.arange(x0 - r - 2, x0 + r + 3) % S)
            d_ = D[sub]; d_[m] = c8((150, 150, 146)); d_[ring] *= 0.6; D[sub] = d_
            h_ = H[sub]; h_[m] = 1.2 * (1 - (dd[m] / r) ** 2) + 0.3; H[sub] = h_
            rr = R[sub]; rr[m] = 0.35; R[sub] = rr
            mt = M[sub]; mt[m] = 0.85; M[sub] = mt
    H = tp.blur(H, 0.7)
    N = normal_from_mm(H, ppm)
    ao = cavity_ao(H, 5, 0.12, 0.4)
    ORM = np.dstack([ao, np.clip(R, 0.3, 1.0), M])
    return save_set("T_Ponte_Legno_v2", D, N, ORM)


# =============================================================================================================
# 11. acciaio verniciato del ponte (MI_Ponte_Acciaio, UV ~4 m)
# =============================================================================================================
def make_ponte_acciaio(S=4096, seed=29):
    """T_Ponte_Acciaio_v2: dalla v1 (stesso layout), bianco abbassato a ~0,70 sRGB di media, max 0,80 (era ~0,98), leggera sfumatura
    calda, sporco a colature larghe; roughness 0,28-0,40 (vernice semi-lucida)."""
    D0, N0, O0 = old("ponte/T_Ponte_Acciaio")
    lin = D0[..., :3] ** 2.2
    lin = lin * ((c8((192, 192, 188)) ** 2.2) / lin.reshape(-1, 3).astype(np.float64).mean(0).astype(np.float32))[None, None]
    streak = np.clip(fbm(S, S, [S / 50], seed + 7), 0, None)
    low = fbm(S, S, [S / 8, S / 30], seed + 8)
    lin *= (1 - 0.05 * streak - 0.03 * np.clip(low, -2, 2))[..., None]
    lin[..., 2] *= 0.985
    D = np.clip(lin, 0, 0.62) ** (1 / 2.2)
    r0 = O0[..., 1]
    R = np.clip(0.30 + (r0 - np.median(r0)) * 0.6 + 0.04 * streak + 0.02 * low, 0.2, 0.9)
    ORM = np.dstack([O0[..., 0], R, O0[..., 2]])
    return save_set("T_Ponte_Acciaio_v2", D, N0, ORM)


# =============================================================================================================
# 12. New Jersey (MI_Morin_NewJersey, u = 2 m, v = profilo)
# =============================================================================================================
def make_newjersey(S=2048, seed=1302):
    """T_Morin_NewJersey_v2: layout della v1 portato a 2048, cemento grigio caldo ~ (160, 158, 150) sRGB
    (era ~0,72), grana e pori di dirty_concrete (CC0), sporco al piede piu' marcato, roughness 0,85-0,95."""
    D0, N0, O0 = old("parcheggio/T_Morin_NewJersey", S)
    hp, n, rr = photo_detail("dirty_concrete", "4k", S, 1, 30)
    base = recolor(D0[..., :3], c8((160, 158, 150)), sat=0.4, contrast=1.3)
    lin = base ** 2.2 * np.clip(hp, 0.6, 1.4)[..., None] ** 0.8
    lin *= (1 + 0.06 * fbm(S, S, [120, 30], seed))[..., None]
    D = np.clip(lin, 0, 1) ** (1 / 2.2)
    N = blend_normals(N0, n, 0.8)
    R = np.clip(0.88 + 0.04 * rr, 0.7, 1.0)
    ORM = np.dstack([O0[..., 0], R, np.zeros_like(R)])
    return save_set("T_Morin_NewJersey_v2", D, N, ORM)


# =============================================================================================================
# 14. tronco della palma (atlante v1)
# =============================================================================================================
def make_palma_tronco(S=2048):
    """T_Morin_PalmaA_Tronco_v2: atlante della v1 schiarito (era ~ (89, 71, 56) sRGB, quasi nero da lontano) a
    ~ (122, 108, 92), grigio-bruno delle palme in giardini.webp e palma_1.png; meno saturo. N invariata, ORM con
    roughness 0,85-0,95."""
    D0, N0, O0 = old("T_Morin_PalmaA_Tronco", S)
    D = recolor(D0[..., :3], c8((122, 108, 92)), sat=0.6, contrast=1.05)
    if D0.shape[2] == 4:
        D = np.dstack([D, D0[..., 3]])
    R = np.clip(0.90 + (O0[..., 1] - O0[..., 1].mean()) * 0.8, 0.75, 1.0)
    ORM = np.dstack([np.clip(O0[..., 0], 0.5, 1), R, O0[..., 2]])
    return save_set("T_Morin_PalmaA_Tronco_v2", D, N0, ORM)


# =============================================================================================================
# 15. corteccia del pino domestico (UV: u 1 m attorno, v 2 m lungo il tronco)
# =============================================================================================================
def make_pino_corteccia(S=2048):
    """T_Morin_PinoDomestico_Corteccia_v2: 2048 (era 1024) da pine_bark (CC0, 2 m): u = 1 m (ritaglio reso
    tileable), v = 2 m. Placche bruno-rossicce e fessure grigio-scure del pino domestico, media ~ (112, 88, 72)."""
    out = []
    maps = {}
    for m in ("diff", "nor_gl", "rough", "ao"):
        a = src("pine_bark", m, "2k")
        a = a[:, : a.shape[1] // 2]
        a = tp.tileable(a)
        maps[m] = resample(a, S)
    n = maps["nor_gl"] * 2 - 1; n /= np.linalg.norm(n, axis=2, keepdims=True) + 1e-6
    N = gl_to_dx(n * 0.5 + 0.5)
    D = recolor(maps["diff"], c8((112, 88, 72)), sat=0.7, contrast=1.1)
    r = maps["rough"]; rn = (r - r.mean()) / (r.std() + 1e-6)
    R = np.clip(0.88 + 0.05 * rn, 0.7, 1.0)
    ORM = np.dstack([np.clip(maps["ao"], 0.4, 1), R, np.zeros_like(R)])
    return save_set("T_Morin_PinoDomestico_Corteccia_v2", D, N, ORM)


# =============================================================================================================
# 16. chioma delle latifoglie (atlante di card RGBA)
# =============================================================================================================
def _pushpull(rgb, mask, levels=10):
    """Riempie i pixel fuori maschera con il colore medio dei vicini (piramide), cosi' le mip non portano nero
    sul bordo delle card."""
    w = mask.astype(np.float32)
    acc = rgb * w[..., None]
    out = rgb.copy()
    fill = np.zeros_like(rgb)
    sig = 1.0
    filled = np.zeros(mask.shape, bool)
    for _ in range(levels):
        a = tp.blur(acc, sig); ww = tp.blur(w, sig)
        good = (ww > 1e-3) & ~filled & ~mask
        fill[good] = a[good] / ww[good][..., None]
        filled |= good
        sig *= 2
    out[~mask] = fill[~mask]
    rest = ~mask & ~filled
    if rest.any():
        out[rest] = (rgb[mask].mean(0) if mask.any() else 0.3)
    return out


def make_chioma_latifoglia(S=2048, seed=101):
    """T_Albero_Latifoglia_Chioma_v2: atlante v1 (alfa invariata), colore delle foglie schiarito e variato
    (verde medio con riflessi giallo-verdi, ombre interne meno nere), RGB esteso fuori dall'alfa (push-pull)
    per eliminare il bordo scuro delle card nelle mip."""
    D0, N0, O0 = old("molo/T_Albero_Latifoglia_Chioma", S)
    a = D0[..., 3]
    mask = a > 0.33
    lin = D0[..., :3] ** 2.2
    L = lum(lin)
    Lm = float(L[mask].mean())
    rel = np.clip(L / Lm, 0, 4) ** 0.65                     # meno contrasto: grumi scuri piu' leggibili
    hue = np.clip(fbm(S, S, [40, 12], seed) * 0.5 + 0.5, 0, 1)[..., None]
    c1 = c8((74, 98, 44)) ** 2.2; c2 = c8((104, 116, 52)) ** 2.2
    col = c1 * (1 - hue) + c2 * hue
    out = col * rel[..., None]
    out = np.clip(out, 0, 1) ** (1 / 2.2)
    out = _pushpull(out, mask)
    D = np.dstack([out, a])
    N = N0.copy()
    N[~mask] = np.array([0.5, 0.5, 1.0], np.float32)
    ORM = np.dstack([np.clip(O0[..., 0], 0.55, 1), np.full((S, S), 0.75, np.float32), np.zeros((S, S), np.float32)])
    return save_set("T_Albero_Latifoglia_Chioma_v2", D, N, ORM)


# =============================================================================================================
# 17. auto v2 (atlante): vernice piu' lucida, bianchi meno lattiginosi
# =============================================================================================================
def make_auto(S=2048, seed=931):
    """T_Morin_Auto_v3_{D,ORM}: stesso atlante. Nelle zone di vernice (roughness v1 0,24-0,30) roughness 0,12-0,16
    e metallic x0,35 (una vernice con trasparente e' un dielettrico lucido: con metallic alto e senza riflessi nitidi
    sembrava lattiginosa); albedo compresso sopra 0,72 (bianchi ~0,78 invece di 0,93). N ed E invariate."""
    D0, N0, O0 = old("auto/T_Morin_Auto_v2")
    r = O0[..., 1]; m = O0[..., 2]
    paint = (r > 0.225) & (r < 0.31)
    R = r.copy()
    R[paint] = 0.13 + 0.03 * np.clip(noise(S, S, 3, seed)[paint], -1, 1)
    M = m.copy(); M[paint] *= 0.35
    rgb = D0[..., :3]
    k = 0.72
    rgb = np.where(rgb > k, k + (rgb - k) * 0.3, rgb)
    D = np.dstack([rgb, D0[..., 3]]) if D0.shape[2] == 4 else rgb
    ORM = np.dstack([O0[..., 0], R, M])
    print("auto: pixel vernice", round(float(paint.mean()) * 100, 1), "%")
    return save_set("T_Morin_Auto_v3", D, None, ORM)


def make_all():
    out = [make_macrovar()]
    for f in (make_lastre, make_cubetti, make_fascia, make_blocchi, make_paramento, make_prato,
              make_asfalto_parcheggio, make_asfalto_molo, make_cemento, make_scogliera, make_corten,
              make_ponte_legno, make_ponte_acciaio, make_newjersey, make_palma_tronco, make_pino_corteccia,
              make_chioma_latifoglia, make_auto):
        out += f()
    return out


# =============================================================================================================
# render di confronto prima/dopo (docs/qa/arte_texture_v2_confronto.png)
# =============================================================================================================
CONFRONTO = [
    # etichetta, (texture v1, tile m), (texture v2, tile m), macro-variazione consigliata
    ("MI_Pav_Lastre", ("T_Pav_Lastre", 3.2), ("v2/T_Pav_Lastre_v2", 4.8), 0.35),
    ("MI_Pav_Cubetti", ("T_Pav_Cubetti", 3.2), ("v2/T_Pav_Cubetti_v2", 2.8), 0.30),
    ("MI_Pav_Fascia", ("T_Pav_Fascia", 1.0), ("v2/T_Pav_Fascia_v2", 2.0), 0.25),
    ("MI_Banchina_Blocchi", ("banchina_v2/T_Banchina_Blocchi", 2.5), ("v2/T_Banchina_Blocchi_v2", 2.5), 0.25),
    ("MI_Morin_Prato", ("viale/T_Morin_Prato", 4.0), ("v2/T_Morin_Prato_v2", 4.0), 0.45),
    ("MI_Parcheggio_Asfalto", ("parcheggio/T_Parcheggio_Asfalto", 8.0), ("v2/T_Parcheggio_Asfalto_v2", 8.0), 0.35),
]
MACRO_TILE = 32.0


def _img(path, noncolor):
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = "Non-Color" if noncolor else "sRGB"
    return im


def _mat(name, base, tile, macro=0.0):
    """Principled con D/N/ORM come il master UEFN: UV in metri / tile, normal DX -> GL (verde invertito),
    ORM: G roughness, B metallic, R AO sul colore; macro-variazione in coordinate mondo (tile 32 m)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / tile, 1 / tile, 1 / tile)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    texs = {}
    for k, nc in (("D", False), ("N", True), ("ORM", True)):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(f"{TEX}/{base}_{k}.png", nc)
        nt.links.new(mp.outputs[0], t.inputs[0])
        texs[k] = t
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(texs["ORM"].outputs[0], sep.inputs[0])
    col = texs["D"].outputs[0]
    ao = nt.nodes.new("ShaderNodeMix"); ao.data_type = "RGBA"; ao.blend_type = "MULTIPLY"
    ao.inputs["Factor"].default_value = 1.0
    nt.links.new(col, ao.inputs["A"]); nt.links.new(sep.outputs[0], ao.inputs["B"])
    col = ao.outputs["Result"]
    if macro > 0:
        mp2 = nt.nodes.new("ShaderNodeMapping")
        mp2.inputs["Scale"].default_value = (1 / MACRO_TILE,) * 3
        nt.links.new(tc.outputs["Object"], mp2.inputs["Vector"])
        mt = nt.nodes.new("ShaderNodeTexImage")
        mt.image = _img(f"{OUT}/T_Morin_MacroVar.png", True)
        nt.links.new(mp2.outputs[0], mt.inputs[0])
        k2 = nt.nodes.new("ShaderNodeMath"); k2.operation = "MULTIPLY_ADD"     # 1 + (M - 0,5) * 2 * k
        k2.inputs[1].default_value = 2 * macro; k2.inputs[2].default_value = 1 - macro
        nt.links.new(mt.outputs[0], k2.inputs[0])
        mm_ = nt.nodes.new("ShaderNodeMix"); mm_.data_type = "RGBA"; mm_.blend_type = "MULTIPLY"
        mm_.inputs["Factor"].default_value = 1.0
        nt.links.new(col, mm_.inputs["A"]); nt.links.new(k2.outputs[0], mm_.inputs["B"])
        col = mm_.outputs["Result"]
    nt.links.new(col, bsdf.inputs["Base Color"])
    nt.links.new(sep.outputs[1], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs[2], bsdf.inputs["Metallic"])
    # normal DX -> GL
    sn = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(texs["N"].outputs[0], sn.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(sn.outputs[1], inv.inputs[1])
    cn = nt.nodes.new("ShaderNodeCombineColor")
    nt.links.new(sn.outputs[0], cn.inputs[0]); nt.links.new(inv.outputs[0], cn.inputs[1]); nt.links.new(sn.outputs[2], cn.inputs[2])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(cn.outputs[0], nm.inputs["Color"])
    nt.links.new(nm.outputs[0], bsdf.inputs["Normal"])
    return m


def confronto_setup():
    sc = bpy.context.scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError:
        pass
    bpy.ops.mesh.primitive_plane_add(size=1)
    pl = bpy.context.active_object
    pl.name = "CMP_Piano"
    pl.scale = (40, 40, 1)
    bpy.ops.object.transform_apply(scale=True)
    cam = bpy.data.cameras.new("CMP_Cam"); cam.lens = 24
    co = bpy.data.objects.new("CMP_Cam", cam); sc.collection.objects.link(co)
    co.location = (0.0, -7.0, 1.7)
    co.rotation_euler = (np.radians(72), 0, 0)
    sc.camera = co
    sun = bpy.data.lights.new("CMP_Sole", "SUN"); sun.energy = 4.0; sun.color = (1.0, 0.86, 0.70); sun.angle = np.radians(1.5)
    so = bpy.data.objects.new("CMP_Sole", sun); sc.collection.objects.link(so)
    so.rotation_euler = (np.radians(90 - 23), 0, np.radians(-60))      # elevazione 23 gradi, radente di traverso
    w = sc.world or bpy.data.worlds.new("CMP_World"); sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.42, 0.55, 0.75, 1); bg.inputs["Strength"].default_value = 0.8
    sc.render.resolution_x, sc.render.resolution_y = 640, 400
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in type(sc.view_settings).bl_rna.properties["view_transform"].enum_items] else "Standard"
    return pl


def confronto_render(out_png=PROJ + "/docs/qa/arte_texture_v2_confronto.png", tmp=None):
    import tempfile
    tmp = tmp or tempfile.gettempdir()
    pl = bpy.data.objects.get("CMP_Piano") or confronto_setup()
    sc = bpy.context.scene
    rows = []
    for lab, (o_b, o_t), (n_b, n_t), mac in CONFRONTO:
        pair = []
        for tag, b, t, mc in (("prima", o_b, o_t, 0.0), ("dopo", n_b, n_t, mac)):
            m = _mat(f"CMP_{lab}_{tag}", b, t, mc)
            pl.data.materials.clear(); pl.data.materials.append(m)
            p = f"{tmp}/cmp_{lab}_{tag}.png"
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            pair.append(tp.load(p)[..., :3])
        row = np.concatenate([pair[0], np.ones((pair[0].shape[0], 6, 3), np.float32), pair[1]], 1)
        rows.append(row)
        rows.append(np.ones((6, row.shape[1], 3), np.float32))
    img = np.concatenate(rows[:-1], 0)
    tp.save(img, out_png)
    return out_png, img.shape
