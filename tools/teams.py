"""팀 레코드 [도시 16][팀명 16][약어 NUL] 고정 필드 치환 (로스터/시즌 데이터 파일)."""
import re
FILES = [0x1396c408, 0x13970789, 0x28308260, 0x30b37284, 0x3aea164e, 0x4294e26f, 0x43ef9065,
         0x63163ce7, 0x65023f60, 0x8eb97c5f, 0x9e2c1649, 0xac08628e, 0xd0ae3ed8, 0xf4ae60c2]

def f16(b, p):
    if p < 0: return None
    t = bytes(b[p:p + 16]).split(b'\0')[0]
    return t if re.fullmatch(rb"[A-Z][A-Za-z\.' \-]{1,15}", t) else None

def apply(b, cmap, nmap):
    """cmap/nmap: {영문 bytes: 한글 인코딩 bytes}. 필드 길이 16 유지 (뒤 잔여 바이트는 NUL)."""
    b = bytearray(b)
    for m in re.finditer(rb'(?<=\x00)[A-Z]{2,3}\x00', bytes(b)):
        s = m.start()
        c = f16(b, s - 32); n = f16(b, s - 16)
        if not (c and n): continue
        nc = cmap.get(c); nn = nmap.get(n) or cmap.get(n)
        if nc: b[s - 32:s - 16] = nc.ljust(16, b'\0')[:16]
        if nn: b[s - 16:s] = nn.ljust(16, b'\0')[:16]
    return bytes(b)
