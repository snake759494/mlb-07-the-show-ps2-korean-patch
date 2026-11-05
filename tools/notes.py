"""로스터 파일의 선수 소개 문장(고정 칸, NUL 패딩) 치환. 새 문장은 원래 칸(다음 비영 바이트 전까지) 안에 들어갈 때만."""
import re
FILES = [0x1396c408, 0x28308260, 0x9e2c1649, 0xe32a33cf, 0xe4e4ee40, 0x13970789,
         0x65023f60, 0x8eb97c5f, 0xac08628e, 0x30b37284, 0x43ef9065, 0x63163ce7, 0xd0ae3ed8]
PAT = re.compile(rb'(?<=\x00)[A-Z][A-Za-z0-9\-\.,\'/%()&:! ]{10,80}(?=\x00)')

def apply(b, tm):
    b = bytearray(b)
    for m in list(PAT.finditer(bytes(b))):
        t = m.group(); n = tm.get(t)
        if not n: continue
        s = m.start(); e = m.end()
        while e < len(b) and b[e] == 0: e += 1
        if len(n) + 1 > e - s: continue
        L = max(len(n), m.end() - s)
        b[s:s + L] = n + bytes(L - len(n))     # 길이 불변
    return bytes(b)
