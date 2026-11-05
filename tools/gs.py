"""GS 로컬 메모리 스위즐 (PSMCT32 / PSMT8 / PSMT4) — 블록·컬럼 배치 표."""
import numpy as np
BLK32 = [[0, 1, 4, 5, 16, 17, 20, 21], [2, 3, 6, 7, 18, 19, 22, 23],
         [8, 9, 12, 13, 24, 25, 28, 29], [10, 11, 14, 15, 26, 27, 30, 31]]
COL32 = [[0, 1, 4, 5, 8, 9, 12, 13], [2, 3, 6, 7, 10, 11, 14, 15]]
COL8 = [
    [[0, 4, 16, 20, 32, 36, 48, 52, 2, 6, 18, 22, 34, 38, 50, 54],
     [8, 12, 24, 28, 40, 44, 56, 60, 10, 14, 26, 30, 42, 46, 58, 62],
     [33, 37, 49, 53, 1, 5, 17, 21, 35, 39, 51, 55, 3, 7, 19, 23],
     [41, 45, 57, 61, 9, 13, 25, 29, 43, 47, 59, 63, 11, 15, 27, 31]],
    [[32, 36, 48, 52, 0, 4, 16, 20, 34, 38, 50, 54, 2, 6, 18, 22],
     [40, 44, 56, 60, 8, 12, 24, 28, 42, 46, 58, 62, 10, 14, 26, 30],
     [1, 5, 17, 21, 33, 37, 49, 53, 3, 7, 19, 23, 35, 39, 51, 55],
     [9, 13, 25, 29, 41, 45, 57, 61, 11, 15, 27, 31, 43, 47, 59, 63]]]
def addr32(bp, bw, x, y):
    """PSMCT32 픽셀의 바이트 주소 (bp: 블록 단위 256B, bw: 64픽셀 단위)."""
    page = (y // 32) * bw + (x // 64)
    blk = BLK32[(y % 32) // 8][(x % 64) // 8]
    cy, cx = y % 8, x % 8
    col = cy // 2
    w = COL32[cy % 2][cx]
    return (bp * 64 + page * 2048 + blk * 64 + col * 16 + w) * 4

def addr8(bp, bw, x, y):
    """PSMT8 픽셀 바이트 주소. bw 는 64픽셀 단위(짝수)."""
    pw = bw // 2
    page = (y // 64) * pw + (x // 128)
    blk = BLK32[(y % 64) // 16][(x % 128) // 16]
    by, bx = y % 16, x % 16
    col = by // 4
    cy = by % 4
    b = COL8[col % 2][cy][bx]
    return bp * 256 + page * 8192 + blk * 256 + col * 64 + b

def unswz8_from32(data, w32, h32, w8, h8):
    """CT32 (w32 x h32)로 올린 데이터를 같은 메모리에서 PSMT8 (w8 x h8)로 읽기."""
    mem = bytearray(4 * 1024 * 1024)
    bw32 = max(1, w32 // 64)
    i = 0
    for y in range(h32):
        for x in range(w32):
            a = addr32(0, bw32, x, y); mem[a:a + 4] = data[i:i + 4]; i += 4
    bw8 = max(2, w8 // 64)
    out = np.zeros((h8, w8), np.uint8)
    for y in range(h8):
        for x in range(w8):
            out[y, x] = mem[addr8(0, bw8, x, y)]
    return out

def swz8_to32(img, w32, h32):
    h8, w8 = img.shape
    mem = bytearray(4 * 1024 * 1024)
    bw8 = max(2, w8 // 64)
    for y in range(h8):
        for x in range(w8):
            mem[addr8(0, bw8, x, y)] = int(img[y, x])
    bw32 = max(1, w32 // 64)
    out = bytearray()
    for y in range(h32):
        for x in range(w32):
            a = addr32(0, bw32, x, y); out += mem[a:a + 4]
    return bytes(out)

def clut_csm1(pal):
    """CSM1 팔레트 순서 보정 (8bpp: 0x08-0x0f <-> 0x10-0x17 블록 교환)."""
    out = list(pal)
    for i in range(256):
        j = (i & 0xe7) | ((i & 0x08) << 1) | ((i & 0x10) >> 1)
        out[i] = pal[j]
    return out
