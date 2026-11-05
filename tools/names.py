"""로스터 파일의 [이름 16][성 16] 고정 필드 쌍 탐색/치환."""
import re
F16 = re.compile(rb'(?=([A-Za-z][A-Za-z\.\' \-]{0,14})\x00)')
def field(b, p):
    f = b[p:p + 16]
    if len(f) < 16: return None
    t = f.rstrip(b'\0')
    if not t or b'\0' in t or not re.fullmatch(rb"[A-Za-z][A-Za-z\.' \-]{0,14}", t): return None
    return t
def pairs(b):
    out = []; p = 0; n = len(b)
    for m in re.finditer(rb'[A-Za-z][A-Za-z\.\' \-]{0,14}\x00', b):
        s = m.start()
        if s and b[s - 1] not in (0,) and 0x20 <= b[s - 1] < 0x7f: continue
        f1 = field(b, s); f2 = field(b, s + 16)
        if f1 and f2 and f1 == b[s:m.end() - 1]: out.append((s, f1, f2))
    return out
def apply(b, fmap, lmap, rng=None):
    b = bytearray(b)
    for i, (s, f1, f2) in enumerate(pairs(bytes(b))):
        if rng and not rng[0] <= i < rng[1]: continue
        if f1 in fmap: b[s:s + 16] = fmap[f1].ljust(16, b'\0')[:16]
        if f2 in lmap: b[s + 16:s + 32] = lmap[f2].ljust(16, b'\0')[:16]
    return bytes(b)
