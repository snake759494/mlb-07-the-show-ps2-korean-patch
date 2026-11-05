"""도움말 CSV: 키,버튼1..5,설명. 0열(화면 키)은 그대로, 1~6열 번역. 헤더 'N SIZE' 있는 파일은 SIZE 갱신.
원래 따옴표 여부를 필드별로 보존."""
import re
FILES = [0x979f7850, 0xbd3c4959, 0x8fbb43bb, 0xba458361, 0xcc96c224, 0x428f3536]

def parse(b):
    hdr = None; body = b
    m = re.match(rb'(\d+) (\d+)\n', b)
    if m: hdr = m.group(0); body = b[m.end():]
    return hdr, body

def split_line(l):
    out = []; i = 0; n = len(l)
    while True:
        if i < n and l[i] == '"':
            j = i + 1; v = ''
            while j < n:
                if l[j] == '"':
                    if j + 1 < n and l[j + 1] == '"': v += '"'; j += 2; continue
                    break
                v += l[j]; j += 1
            out.append((v, True)); i = j + 1
        else:
            j = l.find(',', i); j = n if j < 0 else j
            out.append((l[i:j], False)); i = j
        if i >= n: break
        i += 1
        if i == n: out.append(('', False)); break
    return out

def rows(b):
    hdr, body = parse(b)
    for l in body.decode('latin1').split('\n'):
        cr = l.endswith('\r'); l2 = l[:-1] if cr else l
        yield l, cr, (split_line(l2) if l2 else None)

def fields(b):
    out = []
    for l, cr, fs in rows(b):
        if fs: out += [v for v, q in fs[1:] if re.search('[A-Za-z]{2}', v)]
    return out

def apply(b, tr):
    hdr, body = parse(b)
    res = []
    for l, cr, fs in rows(b):
        if not fs: res.append(l); continue
        o = []
        for k, (v, q) in enumerate(fs):
            if k: v = tr.get(v, v)
            o.append('"' + v.replace('"', '""') + '"' if q else v)
        res.append(','.join(o) + ('\r' if cr else ''))
    nb = '\n'.join(res).encode('latin1')
    if hdr:
        n, sz = hdr.split()
        nb = n + b' ' + str(int(sz) + len(nb) - len(body)).encode() + b'\n' + nb
    return nb
