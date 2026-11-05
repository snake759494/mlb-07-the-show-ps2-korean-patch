"""소형 R5900 어셈블러 (라벨, REL 재배치 표시 지원).
사용: a = Asm(base)  ;  a.op(...)  ;  a.label('x')  ;  a.b('bnez', 't0', 'x')
재배치: a.jrel('j', 대상오프셋)  -> R4,  a.hi('t0', 대상) / a.lo('addiu','t0','t0', 대상) -> R5/R6"""
import struct
R = {n: i for i, n in enumerate(['zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
                                  's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra'])}
I_OPS = {'addiu': 9, 'slti': 10, 'sltiu': 11, 'andi': 12, 'ori': 13, 'xori': 14,
         'lb': 32, 'lh': 33, 'lw': 35, 'lbu': 36, 'lhu': 37, 'sb': 40, 'sh': 41, 'sw': 43,
         'lwc1': 49, 'swc1': 57, 'ld': 55, 'sd': 63}
R_OPS = {'addu': 0x21, 'subu': 0x23, 'and': 0x24, 'or': 0x25, 'xor': 0x26, 'slt': 0x2a, 'sltu': 0x2b, 'daddu': 0x2d}
SH_OPS = {'sll': 0, 'srl': 2, 'sra': 3}

class Asm:
    def __init__(self, base):
        self.base = base; self.w = []; self.labels = {}; self.fix = []; self.relocs = []
    @property
    def pc(self): return self.base + 4 * len(self.w)
    def label(self, n): self.labels[n] = self.pc
    def word(self, x): self.w.append(x & 0xffffffff)
    def nop(self): self.word(0)
    def i(self, op, rt, rs, imm):
        self.word((I_OPS[op] << 26) | (R[rs] << 21) | (R[rt] << 16) | (imm & 0xffff))
    def mem(self, op, rt, off, base):
        if op in ('lwc1', 'swc1'):
            self.word((I_OPS[op] << 26) | (R[base] << 21) | (rt << 16) | (off & 0xffff))
        else: self.i(op, rt, base, off)
    def r(self, op, rd, rs, rt):
        self.word((R[rs] << 21) | (R[rt] << 16) | (R[rd] << 11) | R_OPS[op])
    def sh(self, op, rd, rt, sa):
        self.word((R[rt] << 16) | (R[rd] << 11) | (sa << 6) | SH_OPS[op])
    def move(self, rd, rs): self.r('daddu', rd, rs, 'zero')
    def lui(self, rt, imm): self.word((15 << 26) | (R[rt] << 16) | (imm & 0xffff))
    def jr(self, rs): self.word((R[rs] << 21) | 8)
    def mult(self, rd, rs, rt):   # R5900 3-operand mult
        self.word((R[rs] << 21) | (R[rt] << 16) | (R[rd] << 11) | 0x18)
    def b(self, kind, *args):
        """beq rs rt L / bne rs rt L / beqz rs L / bnez rs L / bgez rs L / bltz rs L / blez / bgtz / b L"""
        lab = args[-1]; pos = len(self.w)
        if kind == 'b': kind, args = 'beq', ('zero', 'zero', lab)
        if kind == 'beqz': kind, args = 'beq', (args[0], 'zero', lab)
        if kind == 'bnez': kind, args = 'bne', (args[0], 'zero', lab)
        if kind in ('beq', 'bne'):
            w = ((4 if kind == 'beq' else 5) << 26) | (R[args[0]] << 21) | (R[args[1]] << 16)
        elif kind in ('bgez', 'bltz'):
            w = (1 << 26) | (R[args[0]] << 21) | ((1 if kind == 'bgez' else 0) << 16)
        elif kind in ('blez', 'bgtz'):
            w = ((6 if kind == 'blez' else 7) << 26) | (R[args[0]] << 21)
        else: raise ValueError(kind)
        self.word(w); self.fix.append((pos, lab))
    def jrel(self, kind, target):
        """j/jal 절대 대상 -> R4 재배치 (target: 이미지 오프셋)."""
        self.relocs.append((self.pc, 4, target))
        self.word((2 if kind == 'j' else 3) << 26)
    def hi(self, rt, target):
        self.relocs.append((self.pc, 5, target)); self.lui(rt, 0)
    def lo(self, op, rt, rs, target):
        self.relocs.append((self.pc, 6, target))
        if op in ('lwc1', 'swc1'): self.mem(op, rt, 0, rs)
        elif op in I_OPS and op not in ('addiu', 'ori'): self.i(op, rt, rs, 0)
        else: self.i(op, rt, rs, 0)
    # FPU
    def mtc1(self, rt, fs): self.word((17 << 26) | (4 << 21) | (R[rt] << 16) | (fs << 11))
    def mfc1(self, rt, fs): self.word((17 << 26) | (R[rt] << 16) | (fs << 11))
    def cvt_s_w(self, fd, fs): self.word((17 << 26) | (20 << 21) | (fs << 11) | (fd << 6) | 0x20)
    def cvt_w_s(self, fd, fs): self.word((17 << 26) | (16 << 21) | (fs << 11) | (fd << 6) | 0x24)
    def fop(self, fn, fd, fs, ft): self.word((17 << 26) | (16 << 21) | (ft << 16) | (fs << 11) | (fd << 6) | fn)
    def add_s(self, fd, fs, ft): self.fop(0, fd, fs, ft)
    def mul_s(self, fd, fs, ft): self.fop(2, fd, fs, ft)
    def div_s(self, fd, fs, ft): self.fop(3, fd, fs, ft)
    def bytes(self):
        for pos, lab in self.fix:
            off = (self.labels[lab] - (self.base + 4 * pos + 4)) >> 2
            assert -0x8000 <= off < 0x8000
            self.w[pos] = (self.w[pos] & 0xffff0000) | (off & 0xffff)
        return struct.pack('<%dI' % len(self.w), *self.w)
