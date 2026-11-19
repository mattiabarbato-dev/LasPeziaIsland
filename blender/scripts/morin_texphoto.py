"""morin_texphoto.py — strumenti numpy per ricavare texture dalle foto di ref/foto/ (Morin Rush).

Tutti gli array sono float32 HxWxC con la riga 0 in ALTO (come le coordinate pixel di un visualizzatore),
valori sRGB 0..1. load()/save() convertono dall'ordine bottom-up di Blender.

Funzioni principali:
    load(path)                     -> array HxWx4 (sRGB grezzo)
    warp(img, quad, W, H)          raddrizzamento prospettico: quad = [TL, TR, BR, BL] in pixel della foto
    blur(a, sigma)                 gaussiana via FFT (periodica: adatta a texture tileable)
    delight(a, sigma)              toglie gradienti di luce/ombra a bassa frequenza, conserva colore medio
    tileable(a)                    rende ripetibile con dissolvenza su copia traslata di mezzo periodo
    resize(a, W, H)                bilineare
    highpass(gray, sigma)          dettaglio fine normalizzato attorno a 1.0
    normal_dx(height, strength)    normal map DirectX (verde invertito) da mappa di altezza
    save(a, path)                  PNG
"""
import numpy as np
import bpy


def load(path):
    im = bpy.data.images.load(path)
    im.colorspace_settings.name = "Non-Color"
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1].copy()
    bpy.data.images.remove(im)
    return a


def save(a, path):
    a = np.asarray(a, dtype=np.float32)
    if a.ndim == 2:
        a = np.dstack([a, a, a])
    if a.shape[2] == 3:
        a = np.dstack([a, np.ones(a.shape[:2], np.float32)])
    h, w = a.shape[:2]
    im = bpy.data.images.new("_tmp_save", w, h, alpha=True)
    im.colorspace_settings.name = "Non-Color"
    im.pixels = np.clip(a[::-1], 0, 1).astype(np.float32).ravel()
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)


def _homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, vt = np.linalg.svd(np.array(A, dtype=np.float64))
    return vt[-1].reshape(3, 3) / vt[-1][-1]


def sample(img, x, y):
    """Campionamento bilineare, x/y array di coordinate pixel (riga 0 in alto)."""
    h, w = img.shape[:2]
    x = np.clip(x, 0, w - 1.001)
    y = np.clip(y, 0, h - 1.001)
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    fx = (x - x0)[..., None]
    fy = (y - y0)[..., None]
    a = img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx
    b = img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def warp(img, quad, W, H):
    """quad = [TL, TR, BR, BL] nella foto -> rettangolo W x H."""
    dst = [(0, 0), (W - 1, 0), (W - 1, H - 1), (0, H - 1)]
    Hm = _homography(dst, quad)  # da destinazione a sorgente
    v, u = np.mgrid[0:H, 0:W].astype(np.float64)
    p = np.stack([u.ravel(), v.ravel(), np.ones(u.size)])
    q = Hm @ p
    x = (q[0] / q[2]).reshape(H, W)
    y = (q[1] / q[2]).reshape(H, W)
    return sample(img, x, y).astype(np.float32)


def blur(a, sigma):
    a = np.asarray(a, dtype=np.float32)
    h, w = a.shape[:2]
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    g = np.exp(-2 * (np.pi ** 2) * (sigma ** 2) * (fx ** 2 + fy ** 2))
    if a.ndim == 2:
        return np.real(np.fft.ifft2(np.fft.fft2(a) * g)).astype(np.float32)
    return np.dstack([np.real(np.fft.ifft2(np.fft.fft2(a[..., c]) * g)) for c in range(a.shape[2])]).astype(np.float32)


def lum(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def delight(a, sigma, strength=1.0):
    """Divide per la luminanza a bassa frequenza: toglie ombre larghe e gradienti."""
    rgb = a[..., :3]
    L = lum(rgb)
    low = blur(L, sigma)
    target = float(L.mean())
    gain = (target / np.maximum(low, 1e-3)) ** strength
    return np.clip(rgb * gain[..., None], 0, 1)


def tileable(a):
    """Due passate 1D (prima in X poi in Y): in ognuna il bordo viene dalla copia traslata di mezzo
    periodo, il centro dall'originale, quindi nessuna cucitura né ai bordi né al centro."""
    h, w = a.shape[:2]
    ext = (slice(None),) + ((None,) if a.ndim == 3 else ())
    wx = np.clip(np.sin(np.linspace(0, np.pi, w)) ** 2 * 1.4, 0, 1)
    wx = wx[None, :, None] if a.ndim == 3 else wx[None, :]
    a = a * wx + np.roll(a, w // 2, 1) * (1 - wx)
    wy = np.clip(np.sin(np.linspace(0, np.pi, h)) ** 2 * 1.4, 0, 1)
    wy = wy[:, None, None] if a.ndim == 3 else wy[:, None]
    a = a * wy + np.roll(a, h // 2, 0) * (1 - wy)
    return a.astype(np.float32)


def resize(a, W, H):
    h, w = a.shape[:2]
    y = (np.arange(H) + 0.5) * h / H - 0.5
    x = (np.arange(W) + 0.5) * w / W - 0.5
    X, Y = np.meshgrid(x, y)
    # campionamento periodico (texture tileable)
    X = np.mod(X, w)
    Y = np.mod(Y, h)
    x0 = np.floor(X).astype(int); y0 = np.floor(Y).astype(int)
    x1 = (x0 + 1) % w; y1 = (y0 + 1) % h
    fx = X - x0; fy = Y - y0
    if a.ndim == 3:
        fx = fx[..., None]; fy = fy[..., None]
    top = a[y0, x0] * (1 - fx) + a[y0, x1] * fx
    bot = a[y1, x0] * (1 - fx) + a[y1, x1] * fx
    return (top * (1 - fy) + bot * fy).astype(np.float32)


def highpass(gray, sigma):
    g = np.asarray(gray, dtype=np.float32)
    return (g / np.maximum(blur(g, sigma), 1e-3)).astype(np.float32)


def normal_dx(height, strength=1.0):
    h = np.asarray(height, dtype=np.float32)
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5 * strength
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5 * strength  # riga 0 in alto: dy = verso il basso
    # GL: n = (-dh/du, +dh/dv_su) ; con righe verso il basso dh/dv_su = -dy -> GL g = dy ; DX g = -dy
    nx = -dx
    ny = -dy
    nz = np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.dstack([nx / l * 0.5 + 0.5, ny / l * 0.5 + 0.5, nz / l * 0.5 + 0.5]).astype(np.float32)


def splat_synth(src, size, patch, n, seed=0, feather=0.35):
    """Texture stocastica tileable: incolla n pezze quadrate (lato `patch` px) prese a caso da `src`
    in posizioni casuali di una tela periodica `size` x `size`, con bordo sfumato."""
    rng = np.random.default_rng(seed)
    h, w = src.shape[:2]
    C = src.shape[2]
    acc = np.zeros((size, size, C), np.float32)
    wsum = np.zeros((size, size), np.float32)
    t = np.linspace(-1, 1, patch)
    m1 = np.clip((1 - np.abs(t)) / feather, 0, 1)
    mask = np.minimum(m1[:, None], m1[None, :]) + 1e-3
    for _ in range(n):
        sy = rng.integers(0, max(1, h - patch)); sx = rng.integers(0, max(1, w - patch))
        p = src[sy:sy + patch, sx:sx + patch]
        if p.shape[0] < patch or p.shape[1] < patch:
            continue
        if rng.random() < 0.5:
            p = p[:, ::-1]
        dy = rng.integers(0, size); dx = rng.integers(0, size)
        ys = (np.arange(patch) + dy) % size
        xs = (np.arange(patch) + dx) % size
        acc[np.ix_(ys, xs)] += p * mask[..., None]
        wsum[np.ix_(ys, xs)] += mask
    out = acc / np.maximum(wsum, 1e-4)[..., None]
    hole = wsum < 1e-2
    if hole.any():
        out[hole] = src.reshape(-1, C).mean(0)
        out = np.where(hole[..., None], blur(out, 6), out)
    return out


def match_color(rgb, target_mean, target_std_scale=1.0):
    """Porta la media colore a target_mean (sRGB) e scala il contrasto attorno alla media."""
    m = rgb.reshape(-1, rgb.shape[-1]).mean(0)
    return np.clip((rgb - m) * target_std_scale + np.asarray(target_mean, np.float32), 0, 1)
