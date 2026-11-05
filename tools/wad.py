"""MLBPS2.WAD 읽기 도우미."""
import struct, os, sys
sys.path.insert(0, os.path.dirname(__file__)); import iso
WLBA = 14661
def f():
    return open(iso.ISO, 'rb')
def head(n=0x20000):
    with f() as h:
        h.seek(WLBA * 2048); return h.read(n)
if __name__ == '__main__':
    d = head()
    n = struct.unpack_from('<I', d)[0]
    print('count', n)
    for i in range(12):
        print(i, ' '.join('%08x' % x for x in struct.unpack_from('<4I', d, 4 + i * 16)))
