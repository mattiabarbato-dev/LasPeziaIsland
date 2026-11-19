"""morin_fondale_colle.py — fondale v2: colle cittadino a nord-ovest (2026-11-19).

Scheda: ref/fondale.md §6, §7.7 e §10 (scelte di questa versione). Usa i campi e le utilita di morin_fondale.py.

Perche il colle v1 era basso e piatto: nell'anello A il suolo era il MINIMO 5x5 del DSM (finestra di 150 m) + media 3x3:
su un colle di 300-400 m di diametro il minimo su 150 m prende il piede del versante, e la cima (DSM 92 m s.l.m.) scendeva a
~64 m; gli edifici poggiati su quel suolo davano una sagoma a "muro" di scatole a tetto piano.

v2 (solo nel settore del colle, azimut 295-358 dalla partenza, 280-1500 m, con rampe):
  suolo = max(suolo v1, minimo 3x3 sulle celle di terra + 2 passate di binomiale 3x3)  -> cima ~77 m s.l.m.,
  edifici sopra (piani x 3,2 + 1,3 m da OSM, altrimenti residuo DSM - suolo): sagoma ~90 m come il DSM.
Asset nuovi (in UEFN import da zero, nessuna sostituzione):
  SM_Fondale_Colle_Suolo_01 (+LOD1/LOD2)  pendio del colle, griglia 22,5 m, texture 1024 planare T_Fondale_Colle_Suolo_D
  SM_Fondale_Citta_Colle_NN (+LOD1/LOD2)  TUTTI gli edifici dei settori NO e N (sostituiscono Citta_NO_01..03, N_01..02),
                                          tetti a padiglione in coppi, tinte piu scure (ref/fondale.md §5).
Uso:
    import morin_fondale_colle as C; importlib.reload(C)
    C.apply_ground(); C.build_ground(); C.build_city_colle(); C.export_all(); C.write_csv()
"""
import math

import bpy
import numpy as np

import morin_fondale as F

P = F.P
P.update(
    colle_az=(295.0, 303.0, 350.0, 358.0),   # rampa 0->1, 1, rampa 1->0 (azimut dalla partenza)
    colle_d=(280.0, 380.0, 1250.0, 1500.0),  # rampa in distanza dalla partenza
    colle_step=22.5,                         # passo della griglia del suolo (LOD1 x1,42, LOD2 x2,6)
    colle_min_diff=0.3,                      # rialzo minimo (m) per includere una cella
    colle_sink=0.6,                          # bordo della mesh affondato sotto il suolo v1 (niente z-fighting)
    colle_chunk_tris=4900,
)

# Tinte piu scure della v1 (ref/fondale.md §5: urbano 186,160,132); moltiplicano la facciata (~0,88)
FACADE_TINTS_V2 = [(0.86, 0.77, 0.60), (0.84, 0.68, 0.56), (0.80, 0.62, 0.42), (0.86, 0.74, 0.50),
                   (0.84, 0.81, 0.74), (0.80, 0.62, 0.56), (0.76, 0.72, 0.64), (0.83, 0.70, 0.58),
                   (0.74, 0.52, 0.42), (0.88, 0.80, 0.64)]
ROOF_TINTS_V2 = [(0.56, 0.30, 0.22), (0.50, 0.28, 0.22), (0.60, 0.36, 0.26), (0.46, 0.27, 0.21),
                 (0.54, 0.33, 0.25), (0.47, 0.44, 0.41)]  # l'ultimo: tetto piano/guaina grigia
COLLE_SECTORS = (7, 0)  # NO, N


def _ramp(x, a, b):
    return np.clip((x - a) / (b - a), 0.0, 1.0)


def colle_weight(X, Y):
    sx, sy = P["spawn"]
    az = F.xy_to_az(np.asarray(X) - sx, np.asarray(Y) - sy)
    d = np.hypot(np.asarray(X) - sx, np.asarray(Y) - sy)
    a0, a1, a2, a3 = P["colle_az"]
    d0, d1, d2, d3 = P["colle_d"]
    wa = _ramp(az, a0, a1) * (1.0 - _ramp(az, a2, a3))
    wd = _ramp(d, d0, d1) * (1.0 - _ramp(d, d2, d3))
    w = wa * wd
    return w * w * (3 - 2 * w)


def _blur(a, w):
    k = (1.0, 2.0, 1.0)
    acc = np.zeros_like(a)
    ww = np.zeros_like(a)
    sh = F._shift_stack(a * w, 1, 0.0)
    sw = F._shift_stack(w.astype(np.float64), 1, 0.0)
    for i, (x, y) in enumerate(zip(sh, sw)):
        kk = k[i // 3] * k[i % 3]
        acc += kk * x
        ww += kk * y
    return np.where(w, acc / np.maximum(ww, 1e-9), a)


def apply_ground():
    """Sostituisce nella cache di morin_fondale il campo h con il suolo v2 (solo nel settore del colle).
    Il suolo v1 resta in _C['h_v1']. Idempotente."""
    f = F.fields()
    if "h_v1" in F._C:
        return F._C
    h, land = f["h_raw"], f["land"]
    hl = np.where(land, h, np.inf)
    mn3 = np.min(np.stack(F._shift_stack(hl, 1, np.inf)), axis=0)
    mn3 = np.where(np.isfinite(mn3), mn3, h)
    g = _blur(_blur(mn3, land), land)
    old = f["h"].copy()
    w = colle_weight(f["XX"], f["YY"])
    new = np.where(land, old + w * np.maximum(g - old, 0.0), old)
    F._C["h_v1"] = old
    F._C["h"] = new
    F._C["colle_w"] = w
    return F._C


def _ground_v1_z(X, Y):
    return F.sample_bilinear(F._C["h_v1"], X, Y) + P["z_off"]


# ------------------------------------------------------------------------------------------------------------
# Suolo del colle
# ------------------------------------------------------------------------------------------------------------
def paint_ground(x0, y0, S, size=1024):
    """Albedo planare del pendio: giardini/alberi e muri/strade fra le case, case dipinte fitte (riempiono i vuoti
    fra le mesh degli edifici), piu verde e bosco verso la cima (parco del castello [S])."""
    px = (np.arange(size) + 0.5) / size
    U, V = np.meshgrid(px, px)  # riga 0 = basso (v)
    X = x0 + U * S
    Y = y0 + V * S
    f = F._C
    hz = F.sample_bilinear(f["h"], X, Y)
    n1 = F.noise(X * 2.0 + 91, Y * 2.0 - 17)
    n2 = F.noise(X * 5.0 - 40, Y * 5.0 + 33)
    green = np.array((72, 92, 52)) / 255.0
    tree = np.array((44, 62, 38)) / 255.0
    urban = np.array((138, 126, 108)) / 255.0
    # quota alta = piu verde (parco), bassa = piu costruito
    gw = np.clip(0.35 + (hz - 40.0) / 60.0 + (n1 - 0.5) * 0.9, 0.0, 1.0)
    rgb = urban * (1 - gw[..., None]) + green * gw[..., None]
    trees = (n2 > 0.56 - 0.12 * gw)
    rgb = np.where(trees[..., None], tree * (0.85 + 0.3 * n1[..., None]), rgb)
    # case dipinte: rettangoli 8 x 10 m con fascia di coppo, dove gw basso
    rng = np.random.default_rng(P["seed"] + 41)
    m_px = S / size
    nh = int(S * S / 300.0)
    hx = rng.uniform(0, S, nh)
    hy = rng.uniform(0, S, nh)
    hzz = F.sample_bilinear(f["h"], x0 + hx, y0 + hy)
    gwh = np.clip(0.35 + (hzz - 40.0) / 60.0 + (F.noise((x0 + hx) * 2.0 + 91, (y0 + hy) * 2.0 - 17) - 0.5) * 0.9, 0, 1)
    keep = rng.random(nh) > gwh * 1.1
    hx, hy = hx[keep], hy[keep]
    cols = np.array(FACADE_TINTS_V2)[rng.integers(0, len(FACADE_TINTS_V2), hx.size)] * 0.9
    roofs = np.array(ROOF_TINTS_V2[:5])[rng.integers(0, 5, hx.size)]
    w_px = max(2, int(round(8.0 / m_px)))
    h_px = max(3, int(round(10.0 / m_px)))
    for i in range(hx.size):
        c0 = int(hx[i] / m_px)
        r0 = int(hy[i] / m_px)
        r1, c1 = min(r0 + h_px, size), min(c0 + w_px, size)
        rgb[r0:r1, c0:c1] = cols[i]
        rgb[max(r1 - max(1, h_px // 3), r0):r1, c0:c1] = roofs[i]
    return np.clip(rgb, 0, 1)


def _ground_grid(step):
    """Vertici e quad della griglia del suolo v2 (solo dove il rialzo e > colle_min_diff, +1 quad di bordo)."""
    f = apply_ground()
    sx, sy = P["spawn"]
    m = (f["h"] - f["h_v1"]) > P["colle_min_diff"]
    xs, ys = f["XX"][m], f["YY"][m]
    x0, x1 = xs.min() - 2 * step, xs.max() + 2 * step
    y0, y1 = ys.min() - 2 * step, ys.max() + 2 * step
    gx = np.arange(x0, x1 + step, step)
    gy = np.arange(y0, y1 + step, step)
    GX, GY = np.meshgrid(gx, gy)
    hn = F.sample_bilinear(f["h"], GX, GY)
    ho = F.sample_bilinear(f["h_v1"], GX, GY)
    land = F.sample_nearest(f["land"], GX, GY)
    up = (hn - ho) > P["colle_min_diff"]
    ny, nx = GX.shape
    # quad (j, i) usa i vertici (j,i),(j,i+1),(j+1,i+1),(j+1,i)
    qup = up[:-1, :-1] | up[:-1, 1:] | up[1:, 1:] | up[1:, :-1]
    qland = land[:-1, :-1] & land[:-1, 1:] & land[1:, 1:] & land[1:, :-1]
    cx = 0.5 * (GX[:-1, :-1] + GX[1:, 1:])
    cy = 0.5 * (GY[:-1, :-1] + GY[1:, 1:])
    ex0, ex1, ey0, ey1 = P["excl_rect"]
    inrect = (cx > ex0) & (cx < ex1) & (cy > ey0) & (cy < ey1)
    q = qup & qland & ~inrect
    Z = np.where(up, hn + P["z_off"], ho + P["z_off"] - P["colle_sink"])
    return GX, GY, Z, q, (x0, y0, max(x1 - x0, y1 - y0))


def build_ground(lods=(0, 1, 2)):
    coll = F._coll("FONDALE_Colle")
    rep = {}
    piv = None
    img = None
    for lod in lods:
        step = P["colle_step"] * (1.0, 1.42, 2.6)[lod]
        GX, GY, Z, q, (x0, y0, S) = _ground_grid(step)
        if lod == 0:
            S0 = (x0, y0, S)
            img = F._save_png("T_Fondale_Colle_Suolo_D", paint_ground(x0, y0, S))
            mat = F._material("M_Fondale_Colle_Suolo", img, rough=0.95)
        ny, nx = GX.shape
        vid = np.arange(ny * nx).reshape(ny, nx)
        js, is_ = np.nonzero(q)
        a = vid[js, is_]
        b = vid[js, is_ + 1]
        c = vid[js + 1, is_ + 1]
        d = vid[js + 1, is_]
        Zf = Z.ravel()
        # diagonale piu corta in quota (meno pieghe)
        diag_ac = np.abs(Zf[a] - Zf[c]) <= np.abs(Zf[b] - Zf[d])
        t1 = np.where(diag_ac[:, None], np.stack([a, b, c], 1), np.stack([a, b, d], 1))
        t2 = np.where(diag_ac[:, None], np.stack([a, c, d], 1), np.stack([b, c, d], 1))
        tri = np.concatenate([t1, t2])
        uniq, inv = np.unique(tri.ravel(), return_inverse=True)
        faces = inv.reshape(-1, 3)
        V = np.stack([GX.ravel()[uniq], GY.ravel()[uniq], Zf[uniq]], 1)
        # normali in alto
        A, B, Cc = V[faces[:, 0]], V[faces[:, 1]], V[faces[:, 2]]
        nz = (B[:, 0] - A[:, 0]) * (Cc[:, 1] - A[:, 1]) - (B[:, 1] - A[:, 1]) * (Cc[:, 0] - A[:, 0])
        faces[nz < 0] = faces[nz < 0][:, [0, 2, 1]]
        sx0, sy0, SS = S0
        uv = np.stack([(V[:, 0] - sx0) / SS, (V[:, 1] - sy0) / SS], 1)
        name = "SM_Fondale_Colle_Suolo_01" + ("" if lod == 0 else f"_LOD{lod}")
        if piv is None:
            piv = F._pivot(V)
        obj = F._mesh_object(name, V, faces, coll, piv, uvs=uv, mat=bpy.data.materials["M_Fondale_Colle_Suolo"])
        if lod > 0:
            obj.hide_set(True)
            obj.hide_render = True
        rep[name] = dict(tris=len(faces), pivot=piv, bbox=(V.min(0).round(1).tolist(), V.max(0).round(1).tolist()))
    return rep


# ------------------------------------------------------------------------------------------------------------
# Edifici del colle
# ------------------------------------------------------------------------------------------------------------
def _convex(pts):
    n = len(pts)
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) < -1e-6:
            return False
    return True


def _building_geom_v2(b, pts, tint, roof_tint, pitched):
    """Pareti come v1; tetto a padiglione (piramide sul baricentro) se pitched, altrimenti piano."""
    if not pitched:
        return F._building_geom(dict(b, pts=pts), tint, roof_tint)
    n = len(pts)
    verts, faces, uvs, cols = [], [], [], []
    per = 0.0
    for i in range(n):
        a, c = pts[i], pts[(i + 1) % n]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        k = len(verts)
        verts += [(a[0], a[1], b["base"]), (c[0], c[1], b["base"]), (c[0], c[1], b["top"]), (a[0], a[1], b["top"])]
        uvs += [(per / 12.0, 0.0), ((per + L) / 12.0, 0.0), ((per + L) / 12.0, (b["top"] - b["base"]) / 12.8),
                (per / 12.0, (b["top"] - b["base"]) / 12.8)]
        cols += [tint] * 4
        faces += [(k, k + 1, k + 2), (k, k + 2, k + 3)]
        per += L
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    k = len(verts)
    for p in pts:
        verts.append((p[0], p[1], b["top"]))
        uvs.append((2.0 / 1024, 2.0 / 1024))
        cols.append(roof_tint)
    verts.append((cx, cy, b["top"] + b["roof_h"]))
    uvs.append((2.0 / 1024, 2.0 / 1024))
    cols.append(tuple(0.85 * v for v in roof_tint))  # colmo un po' piu scuro: legge la falda anche senza ombra
    for i in range(n):
        faces.append((k + i, k + (i + 1) % n, k + n))
    return verts, faces, uvs, cols


def colle_buildings():
    apply_ground()
    blds = F.city_buildings(F.OSM_BUILDINGS or (F.DEM + "/edifici_osm_footprint_1600m.json"))
    out = []
    rng = np.random.default_rng(P["seed"] + 77)
    for b in blds:
        sec = int(np.floor(((b["az"] - P["sector_offset"]) % 360.0) / (360.0 / P["n_sectors"])))
        if sec not in COLLE_SECTORS:
            continue
        b["sec"] = sec
        b["area"] = F._area(b["pts"])
        b["tint"] = FACADE_TINTS_V2[int(rng.integers(len(FACADE_TINTS_V2)))]
        b["pitched"] = (len(b["pts"]) <= 10 and b["area"] < 1500 and _convex(b["pts"])) or \
                       (len(b["pts"]) <= 6 and b["area"] < 2500)
        b["roof"] = ROOF_TINTS_V2[int(rng.integers(5))] if b["pitched"] or rng.random() < 0.6 else ROOF_TINTS_V2[5]
        span = math.sqrt(max(b["area"], 1.0))
        b["roof_h"] = float(np.clip(0.22 * span, 1.2, 4.0))
        out.append(b)
    return out


def build_city_colle(lods=(0, 1, 2)):
    blds = colle_buildings()
    coll = F._coll("FONDALE_Colle")
    mat = bpy.data.materials.get("M_Fondale_Facciate")
    if mat is None:
        img = F._save_png("T_Fondale_Facciata_D", F.paint_facade())
        mat = F._material("M_Fondale_Facciate", img, use_vcol=True, rough=0.9)

    def tcount(b):
        n = len(b["pts"])
        return 2 * n + (n if b["pitched"] else n - 2)

    # blocchi compatti: ordinati per azimut a fasce di distanza (<= colle_chunk_tris)
    bs = sorted(blds, key=lambda b: (0 if b["d"] < 650 else (1 if b["d"] < 1000 else 2), (b["az"] - 280) % 360))
    band = lambda b: 0 if b["d"] < 650 else (1 if b["d"] < 1000 else 2)
    chunks, cur, ct = [], [], 0
    for b in bs:
        t = tcount(b)
        if cur and (ct + t > P["colle_chunk_tris"] or band(b) != band(cur[-1])):
            chunks.append(cur)
            cur, ct = [], 0
        cur.append(b)
        ct += t
    if cur:
        chunks.append(cur)
    rep = {}
    for ci, cb in enumerate(chunks, 1):
        base_name = f"SM_Fondale_Citta_Colle_{ci:02d}"
        piv0 = None
        for lod in lods:
            if lod == 0:
                sel = cb
            else:
                # edifici piu "visibili" (area x altezza) finche il LOD arriva a ~50 % / ~15 % del LOD0
                target = (0.5 if lod == 1 else 0.15) * sum(tcount(b) for b in cb)
                sel, acc = [], 0
                for b in sorted(cb, key=lambda b: -b["area"] * b["h"]):
                    n = min(len(b["pts"]), 8 if lod == 1 else 5)
                    t = 2 * n + (n if (b["pitched"] and lod == 1) else n - 2)
                    if acc + t > target and sel:
                        break
                    sel.append(b)
                    acc += t
            V, Fc, UV, C = [], [], [], []
            for b in sel:
                pts = b["pts"]
                if lod > 0 and len(pts) > 4:
                    p2 = F._simplify_ring(pts, 3.0 if lod == 1 else 6.0)
                    pts = p2 if len(p2) >= 3 else pts
                pitched = b["pitched"] and lod < 2 and _convex(pts)
                v, fc, uv, col = _building_geom_v2(b, pts, b["tint"], b["roof"], pitched)
                off = len(V)
                V += v
                Fc += [(a + off, c + off, d + off) for a, c, d in fc]
                UV += uv
                C += col
            V = np.array(V)
            name = base_name + ("" if lod == 0 else f"_LOD{lod}")
            if piv0 is None:
                piv0 = F._pivot(V)
            obj = F._mesh_object(name, V, Fc, coll, piv0, uvs=np.array(UV), vcols=np.array(C), mat=mat)
            if lod > 0:
                obj.hide_set(True)
                obj.hide_render = True
            rep[name] = dict(tris=len(Fc), n_edifici=len(sel), pivot=piv0,
                             bbox=(V.min(0).round(1).tolist(), V.max(0).round(1).tolist()),
                             d=(round(min(b["d"] for b in cb)), round(max(b["d"] for b in cb))),
                             az=(round(min(b["az"] for b in cb)), round(max(b["az"] for b in cb))))
    return rep, blds


# ------------------------------------------------------------------------------------------------------------
# Alberi del colle (macchie di chiome: lecci, pini [S dalla foto dal ponte])
# ------------------------------------------------------------------------------------------------------------
TREE_TINTS = [(0.22, 0.31, 0.17), (0.18, 0.27, 0.15), (0.26, 0.34, 0.19), (0.20, 0.29, 0.20)]


def _clump(cx, cy, z0, r, h, rot, sides):
    """Chioma low-poly: anello alla base (affondato), anello a 0,55 h ruotato, colmo. 3 x sides triangoli."""
    v = []
    for i in range(sides):
        a = rot + 2 * math.pi * i / sides
        v.append((cx + 0.75 * r * math.cos(a), cy + 0.75 * r * math.sin(a), z0 - 1.0))
    for i in range(sides):
        a = rot + 2 * math.pi * (i + 0.5) / sides
        rr = r * (0.9 + 0.2 * ((i * 37) % 5) / 4)
        v.append((cx + rr * math.cos(a), cy + rr * math.sin(a), z0 + 0.55 * h))
    v.append((cx, cy, z0 + h))
    f = []
    for i in range(sides):
        j = (i + 1) % sides
        f += [(i, j, sides + i), (j, sides + j, sides + i), (sides + i, sides + j, 2 * sides)]
    return v, f


def build_trees(lods=(0, 1, 2), budget=4800):
    """Macchie d'albero sul pendio dove non ci sono edifici: piu fitte in alto (parco del castello [S])."""
    apply_ground()
    blds = colle_buildings()
    rng = np.random.default_rng(P["seed"] + 91)
    GX, GY, Z, q, (x0, y0, S) = _ground_grid(P["colle_step"])
    n_try = 6000
    X = rng.uniform(x0, x0 + S, n_try)
    Y = rng.uniform(y0, y0 + S, n_try)
    w = colle_weight(X, Y)
    hz = F.sample_bilinear(F._C["h"], X, Y)
    land = F.sample_nearest(F._C["land"], X, Y)
    ex0, ex1, ey0, ey1 = P["excl_rect"]
    ok = land & (w > 0.25) & ~((X > ex0 - 10) & (X < ex1 + 10) & (Y > ey0 - 10) & (Y < ey1 + 10))
    p = np.clip(0.15 + (hz - 25.0) / 60.0, 0.1, 1.0) * np.clip(F.noise(X * 3 + 11, Y * 3 - 5) * 2.0 - 0.5, 0.05, 1.0)
    ok &= rng.random(n_try) < p
    # niente alberi dentro/attaccati agli edifici (cerchio equivalente + 2 m)
    bc = np.array([b["c"] for b in blds])
    br = np.array([math.sqrt(b["area"] / math.pi) + 2.0 for b in blds])
    cand = []
    for x, y in zip(X[ok], Y[ok]):
        dd = np.hypot(bc[:, 0] - x, bc[:, 1] - y)
        if np.all(dd > br + 3.0) and all(math.hypot(x - a, y - b) > 9.0 for a, b, _ in cand[-200:]):
            cand.append((x, y, float(rng.random())))
    sides0 = 5
    nmax = budget // (3 * sides0)
    cand = cand[:nmax]
    coll = F._coll("FONDALE_Colle")
    mat = bpy.data.materials["M_Fondale_Facciate"]
    rep = {}
    piv = None
    for lod in lods:
        sides = (5, 4, 3)[lod]
        sel = cand if lod == 0 else [c for k, c in enumerate(cand) if k % (2 if lod == 1 else 4) == 0]
        V, Fc, UV, C = [], [], [], []
        for k, (x, y, rr) in enumerate(sel):
            z0 = float(F.ground_z(np.array([x]), np.array([y]))[0])
            r = 4.0 + 3.0 * rr
            h = 7.0 + 6.0 * ((k * 0.618) % 1.0)
            if lod > 0:  # le chiome superstiti si allargano per tenere la massa verde
                r *= 1.25 if lod == 1 else 1.6
            v, fc = _clump(x, y, z0, r, h, rr * 6.28, sides)
            off = len(V)
            V += v
            Fc += [(a + off, b + off, c + off) for a, b, c in fc]
            UV += [(2.0 / 1024, 2.0 / 1024)] * len(v)
            t = TREE_TINTS[k % len(TREE_TINTS)]
            C += [t] * (len(v) - 1) + [tuple(min(1.0, 1.15 * c) for c in t)]
        V = np.array(V)
        name = "SM_Fondale_Colle_Alberi_01" + ("" if lod == 0 else f"_LOD{lod}")
        if piv is None:
            piv = F._pivot(V)
        obj = F._mesh_object(name, V, Fc, coll, piv, uvs=np.array(UV), vcols=np.array(C), mat=mat)
        if lod > 0:
            obj.hide_set(True)
            obj.hide_render = True
        rep[name] = dict(tris=len(Fc), n=len(sel), pivot=piv, bbox=(V.min(0).round(1).tolist(), V.max(0).round(1).tolist()))
    return rep


# ------------------------------------------------------------------------------------------------------------
# Export e CSV
# ------------------------------------------------------------------------------------------------------------
REPLACED_V1 = ("SM_Fondale_Citta_NO_01", "SM_Fondale_Citta_NO_02", "SM_Fondale_Citta_NO_03",
               "SM_Fondale_Citta_N_01", "SM_Fondale_Citta_N_02")


def colle_names(lod=None):
    names = sorted(o.name for o in bpy.data.collections["FONDALE_Colle"].objects)
    if lod == 0:
        names = [n for n in names if "_LOD" not in n]
    return names


def export_all(overwrite=False):
    return F.export_objects(colle_names(), overwrite=overwrite)


def _tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def _bbox_uu(o):
    V = np.array([v.co[:] for v in o.data.vertices])
    lo, hi = V.min(0), V.max(0)
    return (f"X {lo[0]*100:.0f}..{hi[0]*100:.0f} Y {-hi[1]*100:.0f}..{-lo[1]*100:.0f} "
            f"Z {lo[2]*100:.0f}..{hi[2]*100:.0f}")


def write_csv(path=None):
    """fondale_posizioni_v2.csv: righe v1 (stato invariato / sostituito) + asset nuovi. Non tocca il v1."""
    path = path or (F.EXPDIR + "/fondale_posizioni_v2.csv")
    import os
    if os.path.exists(path):
        raise FileExistsError(path)
    with open(F.EXPDIR + "/fondale_posizioni.csv", encoding="utf-8") as fh:
        hdr = fh.readline().strip()
        rows = [ln.rstrip("\n") for ln in fh if ln.strip()]
    lines = [hdr + ",stato_v2"]
    for r in rows:
        nm = r.split(",")[0]
        st = "da_nascondere_sostituito_da_Colle_v2" if nm in REPLACED_V1 else "invariato"
        lines.append(r + "," + st)
    sx, sy = P["spawn"]
    for nm in colle_names(lod=0):
        o = bpy.data.objects[nm]
        l1, l2 = bpy.data.objects.get(nm + "_LOD1"), bpy.data.objects.get(nm + "_LOD2")
        V = np.array([v.co[:] for v in o.data.vertices]) + np.array(o.location[:])
        dd = np.hypot(V[:, 0] - sx, V[:, 1] - sy)
        lines.append(",".join([nm, f"{o.location.x*100:.0f}", f"{-o.location.y*100:.0f}", "0", "0", "1",
                               str(_tris(o)), str(_tris(l1) if l1 else ""), str(_tris(l2) if l2 else ""),
                               _bbox_uu(o), f"{dd.min():.0f}-{dd.max():.0f}", "nuovo_v2"]))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return path, lines
