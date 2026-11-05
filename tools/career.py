"""커리어 문자열 바이너리 (0x7a917520): [u32 id][u32 len][문자열]... + 꼬리 4바이트."""
import struct
H = 0x7a917520
def parse(b):
    p = 0; L = []
    while p + 8 <= len(b) - 4 or (p + 8 <= len(b) and not L):
        i, n = struct.unpack_from('<II', b, p)
        if p + 8 + n > len(b): break
        L.append((i, b[p + 8:p + 8 + n])); p += 8 + n
    return L, b[p:]
def apply(b, tr):
    L, tail = parse(b)
    return b''.join(struct.pack('<II', i, len(tr.get(t, t))) + tr.get(t, t) for i, t in L) + tail
