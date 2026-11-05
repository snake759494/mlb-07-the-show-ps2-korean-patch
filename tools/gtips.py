"""게임 팁(GT_*) 화면: 본문이 여러 칸(위 칸 n줄 + 그림 옆 칸)으로 나뉜 구조.
영문은 위 칸에 전체 문장을 넣고 줄 수로 잘라, 그림 옆 칸에 잘린 뒷부분을 따로 넣어 둔다.
한글은 게임 줄바꿈 측정이 실제 폭과 달라 넘치므로, 직접 ^n^ 줄바꿈해 칸별로 나눠 넣는다.
요소 머리: x,y,w,h(s-29) / 04 02 01 00 01 / 글자크기, 줄간격, 줄바꿈폭, 최대줄수 (s-14)."""
import re, struct, sys, os
sys.path.insert(0, os.path.dirname(__file__)); import scr

TOK = re.compile(r'\^[^^]*\^|.')
SAFE = float(os.environ.get('GT_SAFE', '0.9'))

def width(t, fs):
    w = 0.0
    for m in TOK.finditer(t):
        c = m.group()
        if c.startswith('^') and len(c) > 1: w += 1.5 * fs if c.startswith('^b') else 0
        elif '가' <= c <= '힣': w += 1.0 * fs
        elif c == ' ': w += 0.5 * fs
        elif c.isupper() or c.isdigit(): w += 0.75 * fs
        elif c.islower(): w += 0.62 * fs
        else: w += 0.45 * fs
    return w

def wrap(text, fs, ww):
    lim = SAFE * ww; lines = []; cur = ''
    for wd in text.split():
        cand = (cur + ' ' + wd) if cur else wd
        if cur and width(cand, fs) > lim: lines.append(cur); cur = wd
        else: cur = cand
    if cur: lines.append(cur)
    return lines

def bodies(b):
    out = []
    for s, e, t in scr.strings(b):
        if b[s - 19:s - 14] != bytes.fromhex('0402010001'): continue
        x, y, w, h = struct.unpack_from('<4h', b, s - 29)
        fs, sp, ww, ml = struct.unpack_from('<4h', b, s - 14)
        if ww > 0 and ml > 0 and len(t) > 15: out.append((y, x, t, fs, ww, ml))
    return sorted(out)

def plan(b, trs):
    """trs: {영문 str: 한글 str} -> {원문 bytes: 새 str}"""
    B = bodies(b)
    if len(B) < 2: return {}
    M = B[0][2].decode('latin1'); T = B[-1][2].decode('latin1')
    best = None
    for k in trs:
        if k.startswith(M[:50]) and k.endswith(T[-30:]) and (best is None or len(k) > len(best)): best = k
    if best is None: return {}
    words = trs[best]
    out = {}; rest = words
    for i, (y, x, t, fs, ww, ml) in enumerate(B):
        L = wrap(rest, fs, ww)
        take = L if i == len(B) - 1 else L[:ml]
        rest = ' '.join(L[len(take):])
        out[t] = '^n^'.join(take) if take else ' '
    return out
