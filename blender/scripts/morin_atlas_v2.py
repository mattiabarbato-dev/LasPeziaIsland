"""morin_atlas_v2.py — atlante a regioni libere + geometria con UV per regione (2026-11-20).

Usato da morin_imbarco_v2.py (biglietteria, pontile, traghetto) e morin_marina_ingresso.py (ufficio, portale, passerella,
bitta arrugginita). Estende morin_imbarco.Geo:
  - ogni faccia porta una REGIONE dell'atlante (cella di colore o pannello dipinto) e un indice di materiale;
  - i materiali hanno un modo UV: "atlas" (la faccia riempie la regione), "world" (UV mondo, ripetibile, passo `tile`),
    "fit" (UV 0..1 sulla faccia: schermo, rete).
Pittura: array float32 sRGB con riga 0 = BASSO (come le UV). Testi rasterizzati dal font (Blender o font di Windows)
via triangolazione della curva di testo: nessun pixel di foto per i testi, nessun logo reale.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import morin_pav_kit as pk
import morin_texphoto as tp
import morin_molo as mm
import morin_imbarco as mi

FONT_DIR = "C:/Windows/Fonts"
F_SANS, F_BOLD, F_BLACK, F_SERIF, F_SERIF_B = "arial.ttf", "arialbd.ttf", "ariblk.ttf", "georgia.ttf", "georgiab.ttf"
_FONTS = {}


def _font(fn):
    if not fn:
        return None
    path = os.path.join(FONT_DIR, fn)
    f = _FONTS.get(fn)
    if f is not None and f.name in bpy.data.fonts:
        return f
    if not os.path.exists(path):
        return None
    f = bpy.data.fonts.load(path, check_existing=True)
    _FONTS[fn] = f
    return f


# =================================================================================================================
# pittura
# =================================================================================================================
def srgb(c):
    return np.array(c, np.float32)


def noise(h, w, cells, seed):
    return mi._smooth_noise(h, w, max(cells, 2), seed)


def fine(h, w, seed, sigma=1.0):
    return mi._fine(h, w, seed, sigma)


def text_mask(body, W_, H_, align="CENTER", font=None, ss=2, base=0.22, em=1.0):
    """Maschera (H_, W_) riga 0 = basso. 1 em = em * H_; linea di base a base * H_; se il testo e' troppo largo si
    riduce mantenendo la linea centrata."""
    Wp, Hp = int(W_ * ss), int(H_ * ss)
    mask = np.zeros((Hp, Wp), np.float32)
    if Wp < 2 or Hp < 2 or not body.strip():
        return np.zeros((H_, W_), np.float32)
    cu = bpy.data.curves.new("_tmp_txt", "FONT")
    cu.body = body
    cu.size = 1.0
    cu.resolution_u = 3
    f = _font(font)
    if f is not None:
        cu.font = f
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
        return np.zeros((H_, W_), np.float32)
    x0, x1 = co[:, 0].min(), co[:, 0].max()
    s = em * Hp
    yb = base * Hp
    if (x1 - x0) * s > 0.98 * Wp:
        s2 = 0.98 * Wp / (x1 - x0)
        yb = yb + (s - s2) * 0.35
        s = s2
    if align == "LEFT":
        px = (co[:, 0] - x0) * s + 0.01 * Wp
    elif align == "RIGHT":
        px = Wp - 0.01 * Wp - (x1 - co[:, 0]) * s
    else:
        px = (co[:, 0] - (x0 + x1) / 2) * s + Wp / 2
    py = co[:, 1] * s + yb
    yy, xx = np.mgrid[0:Hp, 0:Wp].astype(np.float32) + 0.5
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
        ins = (l1 >= -1e-6) & (l2 >= -1e-6) & (l1 + l2 <= 1 + 1e-6)
        mask[j0:j1, i0:i1] = np.maximum(mask[j0:j1, i0:i1], ins.astype(np.float32))
    H2, W2 = Hp // ss, Wp // ss
    m = mask[:H2 * ss, :W2 * ss].reshape(H2, ss, W2, ss).mean(axis=(1, 3))
    out = np.zeros((H_, W_), np.float32)
    out[:H2, :W2] = m
    return out


class Canvas:
    """Tela metrica: x in [x0, x1] m, y in [y0, y1] m, ppm pixel per metro (isotropa). Riga 0 = basso."""

    def __init__(self, x0, x1, y0, y1, ppm, bg=(0.5, 0.5, 0.5), rough=0.5, metal=0.0):
        self.x0, self.x1, self.y0, self.y1, self.ppm = x0, x1, y0, y1, ppm
        self.W = int(round((x1 - x0) * ppm))
        self.H = int(round((y1 - y0) * ppm))
        self.rgb = np.zeros((self.H, self.W, 3), np.float32) + srgb(bg)
        self.h = np.full((self.H, self.W), 0.5, np.float32)
        self.r = np.full((self.H, self.W), rough, np.float32)
        self.m = np.full((self.H, self.W), metal, np.float32)
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32) + 0.5
        self.X = x0 + xx / ppm
        self.Y = y0 + yy / ppm

    def px(self, x, y):
        return (x - self.x0) * self.ppm, (y - self.y0) * self.ppm

    def paint(self, mask, col, rough=None, metal=None, dh=0.0):
        m = np.clip(mask, 0, 1)[..., None]
        self.rgb = self.rgb * (1 - m) + srgb(col) * m
        if rough is not None:
            self.r = self.r * (1 - m[..., 0]) + rough * m[..., 0]
        if metal is not None:
            self.m = self.m * (1 - m[..., 0]) + metal * m[..., 0]
        if dh:
            self.h = self.h + dh * m[..., 0]

    def rect(self, x0, y0, x1, y1, col, **kw):
        m = ((self.X >= x0) & (self.X < x1) & (self.Y >= y0) & (self.Y < y1)).astype(np.float32)
        self.paint(m, col, **kw)

    def circle(self, cx, cy, r, col, r_in=0.0, **kw):
        d = np.hypot(self.X - cx, self.Y - cy)
        aa = 1.0 / self.ppm
        m = np.clip((r - d) / aa + 0.5, 0, 1)
        if r_in > 0:
            m = m * np.clip((d - r_in) / aa + 0.5, 0, 1)
        self.paint(m, col, **kw)

    def ellipse(self, cx, cy, rx, ry, col, rot=0.0, **kw):
        c, s = math.cos(rot), math.sin(rot)
        dx, dy = self.X - cx, self.Y - cy
        u = (dx * c + dy * s) / rx
        v = (-dx * s + dy * c) / ry
        d = np.sqrt(u * u + v * v)
        m = np.clip((1 - d) * min(rx, ry) * self.ppm + 0.5, 0, 1)
        self.paint(m, col, **kw)

    def poly(self, pts, col, **kw):
        X, Y = self.X, self.Y
        ins = np.zeros(X.shape, bool)
        n = len(pts)
        for i in range(n):
            xa, ya = pts[i]
            xb, yb = pts[(i + 1) % n]
            cond = ((ya > Y) != (yb > Y))
            with np.errstate(divide="ignore", invalid="ignore"):
                xi = (xb - xa) * (Y - ya) / (yb - ya + 1e-12) + xa
            ins ^= cond & (X < xi)
        m = tp.blur(ins.astype(np.float32), 0.6) if self.W * self.H < 6e6 else ins.astype(np.float32)
        self.paint(m, col, **kw)

    def line(self, pts, w, col, **kw):
        m = np.zeros(self.X.shape, np.float32)
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
            dx, dy = xb - xa, yb - ya
            L2 = dx * dx + dy * dy + 1e-12
            t = np.clip(((self.X - xa) * dx + (self.Y - ya) * dy) / L2, 0, 1)
            d = np.hypot(self.X - (xa + t * dx), self.Y - (ya + t * dy))
            m = np.maximum(m, np.clip((w / 2 - d) * self.ppm + 0.5, 0, 1))
        self.paint(m, col, **kw)

    def text(self, body, x0, y0, x1, y1, col, align="CENTER", font=F_BOLD, base=0.22, em=1.0, **kw):
        """Testo nel riquadro metrico (x0, y0)-(x1, y1); l'altezza del riquadro e' 1 em."""
        i0, j0 = self.px(x0, y0)
        i1, j1 = self.px(x1, y1)
        i0, j0, i1, j1 = int(round(i0)), int(round(j0)), int(round(i1)), int(round(j1))
        mk = text_mask(body, i1 - i0, j1 - j0, align, font, base=base, em=em)
        m = np.zeros(self.X.shape, np.float32)
        a0, b0 = max(i0, 0), max(j0, 0)
        a1, b1 = min(i1, self.W), min(j1, self.H)
        if a1 > a0 and b1 > b0:
            m[b0:b1, a0:a1] = mk[b0 - j0:b1 - j0, a0 - i0:a1 - i0]
        self.paint(m, col, **kw)

    def grime(self, seed, amount=0.06, streak=0.04):
        n = noise(self.H, self.W, 6, seed)
        f = fine(self.H, self.W, seed + 1, 0.8)
        k = 1.0 + amount * (0.6 * n + 0.4 * f)
        yy = (self.Y - self.y0) / max(self.y1 - self.y0, 1e-6)
        if streak:
            s = np.clip(noise(self.H, self.W, 30, seed + 2) * 0.5, 0, None) * (1 - yy)
            k = k * (1 - streak * s)
        self.rgb = np.clip(self.rgb * k[..., None], 0, 1)
        self.h = self.h + 0.01 * f

    def out(self, W=None, H=None):
        W = W or self.W
        H = H or self.H
        if (W, H) == (self.W, self.H):
            return self.rgb, self.h, self.r, self.m
        rs = lambda a: tp.resize(a if a.ndim == 3 else a[..., None], W, H) if True else None
        return (rs(self.rgb), rs(self.h)[..., 0], rs(self.r)[..., 0], rs(self.m)[..., 0])


# =================================================================================================================
# atlante
# =================================================================================================================
class Atlas:
    def __init__(self, name, npx=2048, unit=128):
        self.name, self.npx, self.unit = name, npx, unit
        self.reg = {}
        self.keys = []

    def add(self, key, cx, cy, w=1, h=1):
        self.reg[key] = (cx, cy, w, h)
        self.keys.append(key)

    def code(self, key):
        return self.keys.index(key)

    def uv_rect(self, key):
        cx, cy, w, h = self.reg[key]
        u = self.unit / self.npx
        ins = 3.0 / self.npx
        return cx * u + ins, cy * u + ins, (cx + w) * u - ins, (cy + h) * u - ins

    def size_px(self, key):
        cx, cy, w, h = self.reg[key]
        return w * self.unit, h * self.unit

    def bake(self, painters, texdir, strength=5.0):
        """painters: key -> fn(W, H) -> (rgb, h, rough, metal). Salva D, N, ORM (riga 0 = alto nei PNG)."""
        n = self.npx
        A = np.zeros((n, n, 3), np.float32) + 0.5
        Hh = np.full((n, n), 0.5, np.float32)
        R = np.full((n, n), 0.6, np.float32)
        M = np.zeros((n, n), np.float32)
        for key in self.keys:
            cx, cy, w, h = self.reg[key]
            W, H = w * self.unit, h * self.unit
            rgb, hh, rr, mm_ = painters[key](W, H)
            sl = (slice(cy * self.unit, cy * self.unit + H), slice(cx * self.unit, cx * self.unit + W))
            A[sl], Hh[sl], R[sl], M[sl] = rgb, hh, rr, mm_
        N, ao = mm._normal_ao(Hh, strength, 3.0, 4.0)
        os.makedirs(texdir, exist_ok=True)
        out = {}
        for suf, arr in (("D", np.clip(A, 0, 1)), ("N", N), ("ORM", mm._orm(ao, np.clip(R, 0.02, 1), M))):
            p = f"{texdir}/{self.name}_{suf}.png"
            tp.save(arr[::-1], p)
            out[suf] = p
        return out


def save_set(name, rgb, h, r, m, texdir, strength=5.0, alpha=None):
    """Texture singola (riga 0 = basso) -> D/N/ORM. alpha opzionale nel canale A della D."""
    N, ao = mm._normal_ao(h, strength, 3.0, 4.0)
    os.makedirs(texdir, exist_ok=True)
    d = np.clip(rgb, 0, 1)
    if alpha is not None:
        d = np.dstack([d, np.clip(alpha, 0, 1)])
    out = {}
    for suf, arr in (("D", d), ("N", N), ("ORM", mm._orm(ao, np.clip(r, 0.02, 1), m))):
        p = f"{texdir}/{name}_{suf}.png"
        tp.save(arr[::-1], p)
        out[suf] = p
    return out


def color_cell(spec, seed):
    """spec = (colore sRGB, variazione, rugosita', metallo[, extra]) -> painter(W, H)."""
    def fn(W, H):
        base, var, rough, metal = spec[:4]
        extra = spec[4] if len(spec) > 4 else None
        big = noise(H, W, 4, seed)
        f = fine(H, W, seed + 1)
        k = 1.0 + var * (0.7 * big + 0.3 * f)
        rgb = np.zeros((H, W, 3), np.float32) + srgb(base)
        rgb = rgb * k[..., None]
        h = 0.5 + 0.02 * f
        R = np.full((H, W), rough, np.float32) + 0.04 * big
        M = np.full((H, W), metal, np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        yy /= H
        xx /= W
        if extra == "vetro":
            rgb *= (0.7 + 0.6 * yy)[..., None]
        elif extra == "interno":
            rgb *= (0.5 + 0.7 * yy)[..., None]
        elif extra == "ondulato":       # lamiera grecata: onde lungo v
            w_ = 0.5 + 0.5 * np.sin(yy * 2 * math.pi * 16)
            rgb *= (0.85 + 0.25 * w_)[..., None]
            h = h + 0.25 * w_
        elif extra == "mandorlato":     # piastra antiscivolo
            p = ((np.sin(xx * 2 * math.pi * 14 + yy * 2 * math.pi * 14) > 0.85) |
                 (np.sin(xx * 2 * math.pi * 14 - yy * 2 * math.pi * 14) > 0.85))
            h = h + 0.2 * p
            rgb[p] *= 1.15
        elif extra == "ruggine":
            r2 = noise(H, W, 12, seed + 3)
            rgb = rgb * (1 + 0.18 * r2[..., None]) * (1 + 0.08 * f[..., None])
            h = h + 0.06 * r2
        elif extra == "venatura":       # legno: venatura lungo u
            g = tp.resize(tp.blur(np.random.default_rng(seed).standard_normal((H, W // 8)).astype(np.float32),
                                  0.8)[..., None], W, H)[..., 0]
            g /= g.std() + 1e-6
            rgb *= (1 + 0.07 * g)[..., None]
            h = h + 0.03 * g
        elif extra == "battistrada":
            t = (np.sin(xx * 2 * math.pi * 10) > 0.3)
            h = h - 0.2 * t
            rgb[t] *= 0.7
        return np.clip(rgb, 0, 1), h, np.clip(R, 0.02, 1), M
    return fn


# =================================================================================================================
# geometria
# =================================================================================================================
class G2(mi.Geo):
    """mats: lista di (nome_materiale, modo, passo). modo: atlas | world | fit."""

    def __init__(self, atlas, mats, ref=None):
        super().__init__(ref)
        self.atl = atlas
        self.mats = mats

    def _set(self, faces, cell, mi_=0):
        code = -1 if cell is None else self.atl.code(cell)
        for f in faces:
            f.material_index = mi_
            f[self.tag] = code
        return faces

    def strip(self, pts_a, pts_b, cell, mi_=0, out=None):
        """Nastro di quad fra due polilinee parallele."""
        res = []
        for a0, a1, b0, b1 in zip(pts_a[:-1], pts_a[1:], pts_b[:-1], pts_b[1:]):
            res += self.quad([a0, a1, b1, b0], cell, mi_, out=out)
        return res

    def prism(self, plan, z0, z1, cell, mi_=0, top=True, bot=False, cell_top=None, mi_top=None):
        """Prisma da pianta (lista xy antioraria)."""
        n = len(plan)
        res = []
        for i in range(n):
            (xa, ya), (xb, yb) = plan[i], plan[(i + 1) % n]
            f = pk._quad(self.bm, [(xa, ya, z0), (xb, yb, z0), (xb, yb, z1), (xa, ya, z1)])
            f.normal_update()
            res += self._set([f], cell, mi_)
        if top:
            f = self.bm.faces.new([self.bm.verts.new((x, y, z1)) for x, y in plan])
            f.normal_update()
            if f.normal.z < 0:
                f.normal_flip()
            res += self._set([f], cell_top or cell, mi_ if mi_top is None else mi_top)
        if bot:
            f = self.bm.faces.new([self.bm.verts.new((x, y, z0)) for x, y in plan[::-1]])
            f.normal_update()
            if f.normal.z > 0:
                f.normal_flip()
            res += self._set([f], cell, mi_)
        return res

    def torus(self, M, R, r, nmaj, nmin, cell):
        def fn(bm):
            rings = []
            for i in range(nmaj):
                a = 2 * math.pi * i / nmaj
                c = Vector((math.cos(a), math.sin(a), 0))
                rings.append([bm.verts.new(M @ (c * (R + r * math.cos(2 * math.pi * j / nmin)) +
                                                Vector((0, 0, r * math.sin(2 * math.pi * j / nmin)))))
                              for j in range(nmin)])
            for i in range(nmaj):
                a, b = rings[i], rings[(i + 1) % nmaj]
                for j in range(nmin):
                    j1 = (j + 1) % nmin
                    bm.faces.new([a[j], b[j], b[j1], a[j1]])
        out = self.new_faces(fn, cell)
        cen = M @ Vector((0, 0, 0))
        ax = (M.to_3x3() @ Vector((0, 0, 1))).normalized()
        for f in out:   # normale verso l'esterno del tubo
            c = f.calc_center_median()
            v = c - cen
            radial = (v - ax * v.dot(ax))
            if radial.length > 1e-6:
                tube_c = cen + radial.normalized() * R
                if f.normal.dot(c - tube_c) < 0:
                    f.normal_flip()
        return out

    def finish(self, name, coll, smooth=None):
        bm = self.bm
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
        bm.normal_update()
        uv = bm.loops.layers.uv.verify()
        for f in bm.faces:
            code = f[self.tag]
            mname, mode, tile = self.mats[f.material_index]
            n = f.normal
            ax = max(range(3), key=lambda i: abs(n[i]))
            a, b = [(1, 2), (0, 2), (0, 1)][ax]
            if mode in ("world", "worldabs"):
                for lp in f.loops:
                    c = lp.vert.co
                    if ax == 2:
                        lp[uv].uv = (c.x / tile, c.y / tile)
                    else:
                        s = c.x if ax == 1 else c.y
                        if mode == "worldabs" and ax == 1:   # specchio in X: righe simmetriche rispetto all'asse
                            s = abs(s)
                        lp[uv].uv = (s / tile, c.z / tile)
                continue
            pts = [(lp.vert.co[a], lp.vert.co[b]) for lp in f.loops]
            u0, u1 = min(p[0] for p in pts), max(p[0] for p in pts)
            v0, v1 = min(p[1] for p in pts), max(p[1] for p in pts)
            du, dv = max(u1 - u0, 1e-6), max(v1 - v0, 1e-6)
            flip = (ax == 0 and n[0] < 0) or (ax == 1 and n[1] > 0)
            if mode == "fit" or code < 0:
                r0, s0, r1, s1 = 0.0, 0.0, 1.0, 1.0
            else:
                r0, s0, r1, s1 = self.atl.uv_rect(self.atl.keys[code])
            for lp, (pu, pv) in zip(f.loops, pts):
                s = (pu - u0) / du
                s = 1 - s if flip else s
                t_ = (pv - v0) / dv
                lp[uv].uv = (r0 + s * (r1 - r0), s0 + t_ * (s1 - s0))
        ngons = [f for f in bm.faces if len(f.verts) > 4]
        if ngons:   # dopo le UV: i triangoli conservano la mappatura della faccia intera
            bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
        bm.faces.layers.int.remove(self.tag)
        used = sorted({f.material_index for f in bm.faces})
        remap = {o: i for i, o in enumerate(used)}
        for f in bm.faces:
            f.material_index = remap[f.material_index]
        names = [self.mats[i][0] for i in used]
        o = pk._finish(name, bm, names, coll, uv=None, smooth_angle=smooth)
        me = o.data
        if len(me.uv_layers) and "UVMap" not in me.uv_layers:
            me.uv_layers[0].name = "UVMap"
        for l in [l for l in me.uv_layers if l.name != "UVMap"]:
            me.uv_layers.remove(l)
        return o


# =================================================================================================================
# verifiche comuni
# =================================================================================================================
def vbox(o):
    """bbox dai vertici (o.bound_box puo' essere vecchio sugli oggetti nascosti)."""
    v = np.array([x.co[:] for x in o.data.vertices])
    return Vector(v.min(0)), Vector(v.max(0))


def bbox_dev(o0, o):
    a0, b0 = vbox(o0)
    a, b = vbox(o)
    d0 = b0 - a0
    return max(max(abs(p[k] - q[k]) / max(d0[k], 1e-3) for k in range(3)) for p, q in ((a, a0), (b, b0)))


def ray_test(o, n_dirs=300, zmin=None, skip_mats=()):
    """Raggi da fuori: il primo impatto deve colpire una faccia vista dal davanti. Facce dei materiali in skip_mats
    (rete masked a doppia faccia) attraversate. zmin: i bersagli sotto zmin si saltano (gusci aperti sotto l'acqua)."""
    from mathutils.bvhtree import BVHTree
    me = o.data
    skip = {i for i, m in enumerate(me.materials) if m and any(s in m.name for s in skip_mats)}
    bvh = BVHTree.FromPolygons([v.co for v in me.vertices], [p.vertices for p in me.polygons])
    lo, hi = vbox(o)
    c = (lo + hi) / 2
    R = (hi - lo).length / 2 + 0.5
    rng = np.random.default_rng(3)
    back = hits = 0
    bad = set()
    for _ in range(n_dirs):
        v = Vector(rng.normal(size=3)).normalized()
        if zmin is not None and v.z < 0.1:
            v.z = abs(v.z) + 0.1
            v.normalize()
        org = c + v * R * 1.6
        t1 = v.orthogonal().normalized()
        t2 = v.cross(t1)
        for jx in np.linspace(-0.6, 0.6, 5):
            for jy in np.linspace(-0.6, 0.6, 5):
                tgt = c + t1 * jx * R + t2 * jy * R
                if zmin is not None and tgt.z < zmin:
                    continue
                d = (tgt - org).normalized()
                p = org
                for _k in range(6):
                    loc, nrm, idx, dist = bvh.ray_cast(p, d)
                    if loc is None:
                        break
                    if me.polygons[idx].material_index in skip:
                        p = loc + d * 1e-3
                        continue
                    hits += 1
                    if me.polygons[idx].normal.dot(d) > 0:
                        back += 1
                        bad.add(idx)
                    break
    return hits, back, sorted(bad)
