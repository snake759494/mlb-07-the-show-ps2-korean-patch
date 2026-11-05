"""REL 이미지 디스어셈블 (이미지 주소 기준, 재배치 주석)."""
import capstone, sys, os
sys.path.insert(0, os.path.dirname(__file__)); import snr
md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS64 + capstone.CS_MODE_LITTLE_ENDIAN)
_cache = {}
def rel(path):
    if path not in _cache:
        r = snr.Rel(path); r.rmap = {o: (t, a) for o, t, a in r.relocs}
        _cache[path] = r
    return _cache[path]
def dis(path, addr, n):
    r = rel(path); out = []
    for i in range(n):
        a = addr + 4 * i; b = r.img(a, 4)
        ins = list(md.disasm(b, a))
        s = f'{a:08x}: ' + (ins[0].mnemonic + ' ' + ins[0].op_str if ins else '.word ' + b.hex())
        if a in r.rmap:
            t, v = r.rmap[a]
            sym = r.syms[t >> 8][0] if t >> 8 else ''
            s += f'    ; R{t & 0xff} {v:#x} {sym}'
        out.append(s)
    return '\n'.join(out)
if __name__ == '__main__':
    print(dis(sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3])))
