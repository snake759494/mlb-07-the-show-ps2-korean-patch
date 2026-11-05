"""TX00(8bpp, PSMT8) 폰트 텍스처 읽기/쓰기. 템플릿: 원본 english.tx2 (64x512)."""
import struct, numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__)); import gs

def decode(t):
    w, h = struct.unpack_from('<HH', t, 0x20)
    pal = t[0x2b0:0x2b0 + 1024]
    P = gs.clut_csm1([pal[4 * i:4 * i + 4] for i in range(256)])
    n = w * h
    img = gs.unswz8_from32(t[0x700:0x700 + n], w // 2, h // 2, w, h) if w <= 64 else None
    return w, h, img, P

def _log2(x): return x.bit_length() - 1

def encode(tmpl, img, P=None):
    """tmpl: 원본 64x512 tx2 바이트, img: (H,W) uint8 인덱스, P: CSM1 보정 전 팔레트(None=원본 유지)."""
    t = bytearray(tmpl)
    H, W = img.shape
    old = struct.unpack_from('<HH', t, 0x20); oldn = old[0] * old[1]
    n = W * H; split = n // 16 > 0x7fff
    delta = n - oldn + (16 if split else 0)
    struct.pack_into('<HH', t, 0x20, W, H)
    struct.pack_into('<I', t, 0x0c, struct.unpack_from('<I', t, 0x0c)[0] + delta)
    struct.pack_into('<I', t, 0x4c, struct.unpack_from('<I', t, 0x4c)[0] + delta)
    tbw = max(2, W // 64)
    # VRAM 블록 수 = 텍스처 블록 + CLUT 4
    struct.pack_into('<H', t, 0x5a, n // 256 + 4)
    struct.pack_into('<I', t, 0x68, struct.unpack_from('<I', t, 0x68)[0] + delta)
    tex0 = struct.unpack_from('<Q', t, 0x78)[0]
    tex0 &= ~((0x3f << 14) | (0xf << 26) | (0xf << 30))
    tex0 |= (tbw << 14) | (_log2(W) << 26) | (((H - 1).bit_length()) << 30)
    struct.pack_into('<Q', t, 0x78, tex0)
    # DMA ref qwc
    q = struct.unpack_from('<I', t, 0x110)[0]
    struct.pack_into('<I', t, 0x110, (q & ~0xffff) | (n // 16 + 5 + (1 if split else 0)))
    # BITBLTBUF (텍스처): SBW, DBW
    for o in (0x100, 0x190):      # 밉 디스크립터와 업로드 목록 두 곳
        b = struct.unpack_from('<Q', t, o)[0]
        b &= ~((0x3f << 16) | (0x3f << 48))
        b |= (tbw << 16) | (max(1, W // 128) << 48)
        struct.pack_into('<Q', t, o, b)
    # TRXREG (CT32 업로드 크기)
    struct.pack_into('<II', t, 0x1b0, W // 2, H // 2)
    struct.pack_into('<II', t, 0x6d0, W // 2, H // 2)   # 데이터 직전 GIF 패킷의 TRXREG
    # GIF IMAGE nloop
    g = struct.unpack_from('<Q', t, 0x6f0)[0]
    tag2 = None
    if split:
        n1 = 0x4000
        tag2 = struct.pack('<Q', (g & ~0x7fff) | (n // 16 - n1)) + t[0x6f8:0x700]
        g = (g & ~0x7fff & ~(1 << 15)) | n1
    else: g = (g & ~0x7fff) | (n // 16)
    struct.pack_into('<Q', t, 0x6f0, g)
    if P is not None:
        Pc = gs.clut_csm1(P)            # 교환은 자기역
        t[0x2b0:0x2b0 + 1024] = b''.join(bytes(p) for p in Pc)
    data = gs.swz8_to32(img, W // 2, H // 2) if W > 64 else None
    if tag2: data = data[:0x40000] + tag2 + data[0x40000:]
    return bytes(t[:0x700]) + data + bytes(t[0x700 + oldn:])
