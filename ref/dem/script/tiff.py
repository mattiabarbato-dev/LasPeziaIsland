"""Minimal GeoTIFF reader (first IFD, tiled, deflate/LZW, predictor 1/2/3, float32)."""
import struct, zlib, numpy as np

TYPES = {1: 'B', 2: 's', 3: 'H', 4: 'I', 5: 'II', 11: 'f', 12: 'd', 16: 'Q'}
SZ = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 11: 4, 12: 8, 16: 8}


def read_ifd(f, off, bo):
    f.seek(off)
    n = struct.unpack(bo + 'H', f.read(2))[0]
    tags = {}
    for _ in range(n):
        tag, typ, cnt = struct.unpack(bo + 'HHI', f.read(8))
        raw = f.read(4)
        size = SZ.get(typ, 1) * cnt
        pos = f.tell()
        if size > 4:
            f.seek(struct.unpack(bo + 'I', raw)[0])
            raw = f.read(size)
            f.seek(pos)
        if typ == 2:
            val = raw[:cnt].decode('latin1')
        elif typ == 5:
            v = struct.unpack(bo + 'I' * (2 * cnt), raw[:size])
            val = [v[i] / v[i + 1] for i in range(0, len(v), 2)]
        else:
            val = list(struct.unpack(bo + TYPES[typ] * cnt, raw[:size]))
        tags[tag] = val
    nxt = struct.unpack(bo + 'I', f.read(4))[0]
    return tags, nxt


def lzw_decode(data):
    # TIFF LZW (MSB first)
    out = bytearray()
    table = [bytes([i]) for i in range(256)] + [b'', b'']
    bitpos, nbits, prev = 0, 9, None
    total = len(data) * 8
    while bitpos + nbits <= total:
        byte = bitpos >> 3
        chunk = int.from_bytes(data[byte:byte + 4].ljust(4, b'\0'), 'big')
        code = (chunk >> (32 - (bitpos & 7) - nbits)) & ((1 << nbits) - 1)
        bitpos += nbits
        if code == 256:
            table = table[:258]; nbits = 9; prev = None; continue
        if code == 257:
            break
        if prev is None:
            entry = table[code]
        elif code < len(table):
            entry = table[code]; table.append(prev + entry[:1])
        else:
            entry = prev + prev[:1]; table.append(entry)
        out += entry
        prev = entry
        if len(table) + 1 >= (1 << nbits) and nbits < 12:
            nbits += 1
    return bytes(out)


def read_geotiff(path):
    with open(path, 'rb') as f:
        bo = '<' if f.read(2) == b'II' else '>'
        magic, off = struct.unpack(bo + 'HI', f.read(6))
        tags, _ = read_ifd(f, off, bo)
        W, H = tags[256][0], tags[257][0]
        comp = tags.get(259, [1])[0]
        pred = tags.get(317, [1])[0]
        bps = tags[258][0]
        fmt = tags.get(339, [1])[0]
        tw, th = tags[322][0], tags[323][0]
        offs, cnts = tags[324], tags[325]
        dt = np.dtype(bo + ('f4' if (fmt == 3 and bps == 32) else 'i2' if bps == 16 else 'f8'))
        arr = np.zeros((H, W), dtype=np.float32)
        tx = (W + tw - 1) // tw
        for i, (o, c) in enumerate(zip(offs, cnts)):
            f.seek(o); raw = f.read(c)
            if comp in (8, 32946):
                raw = zlib.decompress(raw)
            elif comp == 5:
                raw = lzw_decode(raw)
            if pred == 3:
                b = np.frombuffer(raw, np.uint8).reshape(th, dt.itemsize * tw).copy()
                b = np.cumsum(b, axis=1, dtype=np.uint8)
                b = b.reshape(th, dt.itemsize, tw).transpose(0, 2, 1)
                tile = np.ascontiguousarray(b).view(dt.newbyteorder('>')).reshape(th, tw)
            else:
                tile = np.frombuffer(raw, dt).reshape(th, tw).copy()
                if pred == 2:
                    tile = np.cumsum(tile, axis=1).astype(dt)
            r, cidx = divmod(i, tx)
            y0, x0 = r * th, cidx * tw
            hh, ww = min(th, H - y0), min(tw, W - x0)
            arr[y0:y0 + hh, x0:x0 + ww] = tile[:hh, :ww]
        tie = tags.get(33922); scale = tags.get(33550)
        return arr, dict(W=W, H=H, comp=comp, pred=pred, tile=(tw, th), tie=tie, scale=scale,
                         geokeys=tags.get(34735), ascii=tags.get(34737))
