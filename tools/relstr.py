"""REL 문자열 분석: 재배치로 시작점이 참조되는 문자열(이동 가능)과 구조체 내장 문자열 구분."""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(__file__)); import snr

def scan(path, lo=None, hi=None):
    r = snr.Rel(path); d = r.d
    lo = lo or 0x80; hi = hi or r.h[1]
    refs = collections.defaultdict(list)       # 대상 -> [(재배치 위치, 타입)]
    for i, (o, t, a) in enumerate(r.relocs):
        if t >> 8 == 0 and lo <= a < hi: refs[a].append((i, t & 0xff))
    out = []
    for m in re.finditer(rb'[\x09\x0a\x20-\x7e]{1,}\x00', d[lo:hi]):
        s = lo + m.start(); e = lo + m.end() - 1
        out.append((s, d[s:e], refs.get(s, [])))
    return r, out, refs

if __name__ == '__main__':
    r, out, refs = scan(sys.argv[1])
    n_ref = sum(1 for s, t, rf in out if rf)
    print('strings', len(out), 'referenced', n_ref)
    inner = [(s, t) for s, t, rf in out if not rf and len(t) > 3 and b' ' in t]
    print('unreferenced sentences', len(inner))
    for s, t in inner[:40]: print(hex(s), t[:70])
