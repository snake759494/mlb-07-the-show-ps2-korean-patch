"""레전드 선수 소개(탭 구분 텍스트) 번역 적용. 설명 문단은 원래 줄 수로 다시 나눈다."""
FILES = [0x11037017, 0x63a5b464, 0x6e00ac97, 0xd05ef226, 0x1d8b4b2a, 0x3f102a31, 0x91ceaaaa, 0xf163385f]
LIST = 0x6d28ade

def split_lines(s, n):
    """한글 인코딩 bytes s 를 공백 기준으로 n 줄에 균등 분배."""
    words = s.split(b' ')
    if n <= 1: return [s]
    total = len(s); out = []; cur = b''
    for w in words:
        target = total * (len(out) + 1) / n
        if cur and len(b' '.join(out + [cur]).replace(b' ', b'')) + len(w) > target and len(out) < n - 1:
            out.append(cur); cur = w
        else:
            cur = cur + b' ' + w if cur else w
    out.append(cur)
    while len(out) < n: out.append(b'')
    return out

def apply(b, tm):
    """tm: {영문 bytes: 한글 bytes}"""
    lines = b.split(b'\r\n'); res = []
    for ln in lines:
        f = ln.split(b'\t')
        if len(f) >= 7:
            for i in (3, 4, 5):
                if f[i] in tm: f[i] = tm[f[i]]
            p = b' '.join(x.strip() for x in f[6:])
            if p in tm: f[6:] = split_lines(tm[p], len(f) - 6)
        elif len(f) > 3 and f[3] in tm:
            f[3] = tm[f[3]]
        res.append(b'\t'.join(f))
    return b'\r\n'.join(res)
