"""얼굴 ID 목록(0x4677fdb9, '성 이름\tID\t플래그') 을 로스터와 같은 한글 이름으로 바꾸고 바이트 순 정렬."""
H = 0x4677fdb9
def apply(b, fmap, lmap):
    import re
    nz = lambda k: re.sub(rb'[^A-Za-z0-9]', b'', k)
    nl = {nz(k): v for k, v in lmap.items()}; nf = {nz(k): v for k, v in fmap.items()}
    out = []
    for ln in b.split(b'\r\n'):
        if not ln: continue
        nm, rest = ln.split(b'\t', 1)
        if b' ' in nm:
            l, f = nm.split(b' ', 1)
            l = nl.get(l, l)[:16].rstrip(b'\0'); f = nf.get(f, f)[:16].rstrip(b'\0')
            nm = l + b' ' + f
        out.append(nm + b'\t' + rest)
    return b''.join(x + b'\r\n' for x in out)
