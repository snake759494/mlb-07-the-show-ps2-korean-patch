"""MLBPS2.WAD 파일시스템: 해시(h*131, 대문자, 역슬래시) / 엔트리(해시, 크기, 오프셋)."""
import struct, os, sys
sys.path.insert(0, os.path.dirname(__file__)); import wad
BS = bytes([92])
def _ct():
    import edis
    o = edis.v2o(0x199a61 - 128); t = edis.D[o:o + 256]
    return t[128:] + t[:128]          # _CT[바이트값]
_CT = _ct()
def norm(s):
    if isinstance(s, str): s = s.encode('latin1')
    s = bytes(((c - 0x20) & 0xff) if _CT[c] & 2 else c for c in s).replace(b'/', BS)   # 게임 대문자화: 부호 있는 바이트로 ctype 표 참조
    while s[:1] in (b'.', BS): s = s[1:]
    return s
def h131(s):
    h = 0
    for c in norm(s):
        if c >= 128: c -= 256
        h = (h * 131 + c) & 0xffffffff
    return h
_d = wad.head(0x16000)
N = struct.unpack_from('<I', _d)[0]
ENT = [struct.unpack_from('<3I', _d, 8 + 12 * i) for i in range(N)]
FIRST = struct.unpack_from('<I', _d, 4)[0]
BYH = {e[0]: e for e in ENT}
def find(path): return BYH.get(h131(path))
def read(path_or_ent):
    e = path_or_ent if isinstance(path_or_ent, tuple) else find(path_or_ent)
    with wad.f() as f:
        f.seek(wad.WLBA * 2048 + e[2]); return f.read(e[1])
