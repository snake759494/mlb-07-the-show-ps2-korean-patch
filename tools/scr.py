"""WAD 화면세트(UI 레이아웃) 파일의 표시 문자열: [u32 길이][문자열][NUL] 레코드.
표시 문자열만 골라 길이를 바꿔 다시 쓴다 (스트림 파싱이라 길이 변경 허용 확인)."""
import re, struct
REC = re.compile(rb'[\x20-\x7e]{1,700}\x00')
BIND = re.compile(rb'[A-Z_0-9]+[\.\[][A-Z_]')

def core(t): return re.sub(rb'\^[a-z]-?\d*\^', b'', t)

def is_disp(b, s, t):
    if BIND.search(t): return False
    if b'^d' in t:
        # ^d숫자^ 뒤에 고정 라벨이 붙은 형태만 허용 (마커 필수)
        if not re.fullmatch(rb'(\^[a-z]-?\d*\^)*\^d\d+\^ ?[A-Za-z][^^]*', t) or b[s - 8:s - 4] != b'\xff\xff\x01\x00': return False
    c = core(t).strip()
    if not re.search(rb'[A-Za-z]{2}', c): return False
    if re.fullmatch(rb'-+ ?Col \d+ ?-+|aaa|test.*', c, re.I): return False
    marker = b[s - 6:s - 4] == b'\x01\x00' and b[s - 8:s - 6] == b'\xff\xff' or b[s - 8:s - 4] == b'\xff\xff\x01\x00'
    if marker: return True
    if b[s - 6:s - 4] == b'\x01\x00' and b'\x04\x02\x01' in b[s - 26:s - 8] and re.search(rb'[a-z]{2}|[A-Z]{2}', c): return True
    if t.startswith(b'^j') or re.match(rb'(\^t\d+\^)+\^j', t): return True
    return False

def strings(b):
    out = []
    for m in REC.finditer(b):
        s = m.start(); e = m.end() - 1
        if s < 8 or struct.unpack_from('<I', b, s - 4)[0] != e - s: continue
        t = b[s:e]
        if is_disp(b, s, t): out.append((s, e, t))
    # NUL 없는 ^d 레코드: [ffff 0100][u32 길이][문자열]
    seen = {x[0] for x in out}
    for m in re.finditer(rb'\xff\xff\x01\x00(.)\x00\x00\x00\^', b, re.S):
        n = m.group(1)[0]; s = m.end() - 1; e = s + n
        t = b[s:e]
        if s in seen or not re.fullmatch(rb'[\x20-\x7e]+', t): continue
        if re.fullmatch(rb'(\^[a-z]-?\d*\^)*\^d\d+\^ ?[A-Za-z][^^]*', t): out.append((s, e, t))
    out.sort()
    return out

def apply(b, tr):
    """tr: {원문 bytes: 번역 bytes}"""
    out = bytearray(); p = 0
    for s, e, t in strings(b):
        if t not in tr: continue
        n = tr[t]
        out += b[p:s - 4] + struct.pack('<I', len(n)) + n; p = e
    out += b[p:]
    return bytes(out)
