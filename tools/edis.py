"""SCUS_975.56 디스어셈블 + 심볼."""
import capstone, sys, os, struct
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work', 'ext', 'SCUS_975.56')
D = open(P, 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS64 + capstone.CS_MODE_LITTLE_ENDIAN)
SEG = []
ph = struct.unpack_from('<I', D, 0x1c)[0]
for i in range(struct.unpack_from('<H', D, 0x2c)[0]):
    t, off, va, pa, fs, ms, fl, al = struct.unpack_from('<8I', D, ph + 32 * i)
    SEG.append((va, off, fs, ms))
def v2o(va):
    for v, o, fs, ms in SEG:
        if v <= va < v + fs: return va - v + o
def syms():
    sh = struct.unpack_from('<I', D, 0x20)[0]; n = struct.unpack_from('<H', D, 0x30)[0]
    S = [struct.unpack_from('<10I', D, sh + 40 * i) for i in range(n)]
    out = {}
    for s in S:
        if s[1] == 2:
            st = S[s[6]]; so = st[4]
            for j in range(s[5] // 16):
                nm, val, sz, inf, oth, shn = struct.unpack_from('<IIIBBH', D, s[4] + 16 * j)
                e = D.index(b'\0', so + nm); out[D[so + nm:e].decode('latin1')] = (val, sz)
    return out
def dis(va, n):
    out = []
    for i in range(n):
        a = va + 4 * i; o = v2o(a)
        ins = list(md.disasm(D[o:o + 4], a))
        out.append(f'{a:08x}: ' + (ins[0].mnemonic + ' ' + ins[0].op_str if ins else '.word ' + D[o:o + 4].hex()))
    return '\n'.join(out)
if __name__ == '__main__':
    S = syms()
    a = sys.argv[1]
    if a in S: v, sz = S[a]; print(a, hex(v), sz); print(dis(v, int(sys.argv[2]) if len(sys.argv) > 2 else sz // 4))
    elif a.startswith('?'):
        for k, (v, sz) in S.items():
            if a[1:] in k: print(hex(v), sz, k)
    else: print(dis(int(a, 16), int(sys.argv[2])))
