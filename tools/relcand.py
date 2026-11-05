"""REL 번역 후보: 재배치로 참조되는 표시 문자열 (두 단어 이상 또는 ^코드 시작)."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__)); import relstr
LO = {'FE': 0x340000, 'GAME': 0x2f0000, 'HRDERBY': 0x200000}
def cand(name, keep=()):
    r, out, refs = relstr.scan(os.path.join(os.path.dirname(__file__), '..', 'work', 'ext', name + '.REL'), LO[name])
    c = []
    for s, t, rf in out:
        if not rf or len(t) < 3: continue
        if re.search(rb'%[-0-9.]*[sdxpfiuc]|\|/[a-z]|\.(bin|tx2|rel|wad|txt|pss|vag|skx|scr|ini)\b|::|__|[\n\r\t]|\(\)|0x|\$', t, re.I): continue
        cc = re.sub(rb'\^[a-z]-?\d*\^', b'', t)
        if not re.search(rb'[A-Za-z]{2}', cc): continue
        if not (b' ' in cc.strip() or t.startswith(b'^') or (t in keep and os.environ.get('SINGLE') is not None)): continue
        if t not in keep and re.fullmatch(rb'[A-Z][a-z]+ [A-Z][a-z\']+', t): continue      # 사람 이름 등
        c.append((s, t))
    return r, c
if __name__ == '__main__':
    import json
    for n in LO:
        r, c = cand(n)
        L = sorted(set(t.decode('latin1') for s, t in c))
        json.dump(L, open('work/tr/src_%s.json' % n.lower(), 'w'), ensure_ascii=False, indent=0)
        print(n, len(c), len(L), sum(map(len, L)))
