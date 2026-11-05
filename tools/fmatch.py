"""GHOSTMAN.REL(심볼 있음)의 함수를 다른 REL 에서 찾기 (재배치 워드는 마스킹)."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__)); import snr
SRC = os.path.join(os.path.dirname(__file__), '..', 'work', 'ext', 'GHOSTMAN.REL')
_s = None
def src():
    global _s
    if _s is None:
        r = snr.Rel(SRC); r.rset = {o for o, t, a in r.relocs}
        S = sorted((a, n) for n, a, b in r.syms if a)
        r.funcs = S; _s = r
    return _s
def func_range(name):
    r = src()
    for i, (a, n) in enumerate(r.funcs):
        if n == name: return a, r.funcs[i + 1][0]
def find(path, name, maxlen=0x400):
    r = src(); a, b = func_range(name); b = min(b, a + maxlen)
    words = []
    for o in range(a, b, 4):
        w = struct.unpack_from('<I', r.d, o)[0]
        if o in r.rset: words.append(None)
        else: words.append(w)
    t = snr.Rel(path); trel = {o for o, _, _ in t.relocs}
    d = t.d; n = len(words)
    first = next(i for i, w in enumerate(words) if w is not None)
    key = struct.pack('<I', words[first])
    out = []; i = d.find(key)
    while i >= 0:
        s = i - 4 * first
        if s >= 0 and s % 4 == 0:
            ok = True
            for k, w in enumerate(words):
                if w is None: continue
                if struct.unpack_from('<I', d, s + 4 * k)[0] != w: ok = False; break
            if ok: out.append(s)
        i = d.find(key, i + 1)
    return out, b - a
if __name__ == '__main__':
    for nm in sys.argv[2:]:
        print(nm, [hex(x) for x in find(sys.argv[1], nm)[0]])
