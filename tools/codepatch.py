"""REL 한글 패치 (모듈 크기 불변).
모듈을 키우면 메모리 배치가 깨져 멈추므로, 번역 문자열은 원래 문자열 영역(슬롯) 안에 다시 채워 넣고
훅 코드도 그 빈 공간에 둔다. 훅은 bal 로 자기 위치를 구해 AddGlyph 로 점프 (재배치 추가 없음).
- 이동 가능 슬롯: 시작 주소만 재배치로 참조되고(내부 참조 없음), 여유 패딩 < 8 (쓰기 버퍼 아님)
- 이동 불가 문자열은 제자리에 들어갈 때만 번역"""
import struct, sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
import snr, asm

MODS = {
    'FE': (0x296be8, 0x297168),
    'GAME': (0x24d530, 0x24dab0),
    'HRDERBY': (0x1831b8, 0x183738),
    'GHOSTMAN': (0x13fa60, 0x13ffe0),
}
SITES = [(0xe8, 0), (0x200, 1), (0x324, 0)]   # (HT 오프셋, s1 이미 증가 여부)

def hook_one(base, off, inc, ag):
    """사이트 하나용 자립형 훅."""
    a = asm.Asm(base)
    a.i('addiu', 't9', 'a1', -1)
    a.b('beqz', 't9', 'zw'); a.nop()           # 코드 0x01 = 폭 0
    a.b('bgez', 'a1', 'go'); a.nop()
    a.mem('lbu', 't8', 0 if inc else 1, 's1')
    a.i('sltiu', 't9', 't8', 0x80)
    a.b('bnez', 't9', 'zw'); a.nop()           # 짝 없는 선두 바이트 = 폭 0
    a.i('andi', 't9', 'a1', 0x7f)
    a.sh('sll', 't9', 't9', 7)
    a.i('andi', 't8', 't8', 0x7f)
    a.r('or', 't9', 't9', 't8')
    a.i('addiu', 'a1', 't9', 0x100)
    a.i('addiu', 's1', 's1', 1)
    a.b('b', 'go'); a.nop()
    a.label('zw')
    a.i('addiu', 'a1', 'zero', 0x90)           # 빈 레코드(인덱스 0x70)
    a.label('go')
    a.move('t9', 'ra')
    a.word((1 << 26) | (0x11 << 16) | 1)      # bal +1 (ra = L)
    a.nop()
    L = a.pc
    delta = (ag - L) & 0xffffffff
    a.lui('t8', delta >> 16)
    a.i('ori', 't8', 't8', delta & 0xffff)
    a.r('addu', 't8', 't8', 'ra')
    a.move('ra', 't9')
    a.jr('t8'); a.nop()
    return a.bytes()

class Patch:
    def __init__(self, path, mod):
        self.r = snr.Rel(path); self.mod = mod
        self.strings = {}
        self.spare = []          # 강제로 비울 (debug) 문자열 시작 주소
        self.fix = {}            # 주소 -> bytes 제자리 덮기

    def add_string(self, start, data): self.strings[start] = data

    def build(self):
        r = self.r; d = bytearray(r.d); h1 = r.h[1]
        for a_, b_ in self.fix.items(): d[a_:a_ + len(b_)] = b_
        ht, ag = MODS[self.mod]
        refs = collections.defaultdict(list)
        for i, (o, t, v) in enumerate(r.relocs):
            if t >> 8 == 0: refs[v].append(i)
        tgt = sorted(refs)
        import bisect
        def slot(s):
            e = d.index(b'\0', s)
            ln = e - s
            while e < h1 and d[e] == 0: e += 1
            return ln, e - s
        def interior(s, cap):
            j = bisect.bisect_right(tgt, s)
            return j < len(tgt) and tgt[j] < s + cap
        moving = {}; inplace = {}; free = []
        for s, data in self.strings.items():
            ln, cap = slot(s)
            movable = cap - (ln + 1) < 8 and not interior(s, cap)
            if movable:
                moving[s] = data; free.append((s, cap))
            elif len(data) + 1 <= cap:
                inplace[s] = data
        # 훅 공간이 없으면 디버그 문자열 슬롯을 비움 (참조는 슬롯 마지막 NUL = 빈 문자열)
        empty_redirect = {}
        for s in self.spare:
            ln, cap = slot(s)
            if interior(s, cap): continue
            free.append((s, cap - 1)); empty_redirect[s] = s + cap - 1
        for s, cap in free: d[s:s + cap] = bytes(cap)
        free = [[ (s + 3) & ~3, s + cap] for s, cap in free]
        free = [f for f in free if f[1] > f[0]]
        free.sort(key=lambda f: f[0] - f[1])
        # 훅 코드 (사이트별)
        entries = {}
        for off, inc in SITES:
            need = len(hook_one(0, off, inc, ag))
            fi = next((k for k, f in enumerate(free) if f[1] - f[0] >= need), None)
            assert fi is not None, (self.mod, 'no space for hook')
            hb = free[fi][0]
            code = hook_one(hb, off, inc, ag)
            d[hb:hb + len(code)] = code; free[fi][0] = (hb + len(code) + 3) & ~3
            entries[off] = hb
        # 문자열 배치 (큰 것부터 first-fit)
        spos = {}
        for s, data in sorted(moving.items(), key=lambda x: -len(x[1])):
            n = len(data) + 1
            for f in free:
                if f[1] - f[0] >= n:
                    p = f[0]; d[p:p + len(data)] = data; d[p + len(data)] = 0
                    spos[s] = p; f[0] = p + n; break
            else:
                raise RuntimeError('pool overflow %s' % self.mod)
        for s, data in inplace.items():
            ln, cap = slot(s)
            d[s:s + cap] = data + bytes(cap - len(data))
        # 재배치 갱신
        ro = r.h[1]
        idx = {o: i for i, (o, t, v) in enumerate(r.relocs)}
        for off, _ in SITES:
            i = idx[ht + off]; o, t, v = r.relocs[i]
            assert t & 0xff == 4 and v == ag, hex(ht + off)
            struct.pack_into('<3I', d, ro + 12 * i, o, t, entries[off])
        for s, p in list(spos.items()) + list(empty_redirect.items()):
            for i in refs[s]:
                o, t, v = r.relocs[i]
                if (t & 0xff) in (2, 5, 6):
                    struct.pack_into('<3I', d, ro + 12 * i, o, t, p)
        self.stats = (len(spos), len(inplace), len(self.strings) - len(spos) - len(inplace),
                      sum(f[1] - f[0] for f in free))
        assert len(d) == len(r.d)
        return bytes(d)
