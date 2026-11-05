"""한글 문자열 인코딩: 글자 k -> 0x80|(k>>7), 0x80|(k&0x7f)."""
class Enc:
    def __init__(self, chars): self.chars = list(chars); self.idx = {c: i for i, c in enumerate(self.chars)}
    def enc(self, s):
        out = bytearray()
        for c in s:
            if ord(c) < 0x80: out.append(ord(c))
            else:
                k = self.idx[c]; out += bytes([0x80 | (k >> 7), 0x80 | (k & 0x7f)])
        return bytes(out)
def charset(texts):
    s = set()
    for t in texts:
        for c in t:
            if ord(c) >= 0x80: s.add(c)
    return sorted(s)
