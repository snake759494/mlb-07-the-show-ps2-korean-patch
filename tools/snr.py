"""SNR1 재배치 모듈(.REL) 파서."""
import struct, sys
class Rel:
    def __init__(self, path):
        self.d = d = open(path, 'rb').read()
        h = struct.unpack_from('<12I', d)
        self.h = h
        self.base = 0   # 주소 = 파일 오프셋 (재배치·심볼 모두 파일 오프셋 기준)
        ro, rn = h[1], h[2]
        self.relocs = [struct.unpack_from('<3I', d, ro + 12 * i) for i in range(rn)]
        so, sn = h[3], h[4]
        self.syms = []
        for i in range(sn):
            no, a, b = struct.unpack_from('<3I', d, so + 12 * i)
            e = d.index(b'\0', no)
            self.syms.append((d[no:e].decode('latin1'), a, b))
    def img(self, addr, n):      # 이미지 주소 -> 데이터
        return self.d[self.base + addr:self.base + addr + n]
if __name__ == '__main__':
    r = Rel(sys.argv[1])
    print([hex(x) for x in r.h])
    import collections
    print(collections.Counter(t for _, t, _ in r.relocs))
    pat = sys.argv[2] if len(sys.argv) > 2 else ''
    for s in r.syms:
        if pat in s[0]: print(s[0], hex(s[1]), hex(s[2]))
