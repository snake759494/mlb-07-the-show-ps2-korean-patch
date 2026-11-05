"""한글패치 ISO 빌드.
1) 원본 ISO 복사  2) SNDPS2/SOUND/FEPXP.SKX 를 ISO 끝으로 옮겨 WAD 오프셋(부호 있는 32비트, 2GB)으로 닿는 빈 영역 확보
3) 수정한 WAD 파일을 그 영역에 쓰고 WAD 디렉터리 갱신  4) REL/ELF 제자리 패치"""
import os, sys, struct, shutil, time
sys.path.insert(0, os.path.dirname(__file__))
import iso, isoedit, wadfs, wad
ROOT = iso.ROOT
SRC = iso.ISO
OUT = os.path.join(ROOT, 'MLB 07 - The Show (USA) (v2.00) (Korean).iso')
SEC = 2048
MOVE = 'SNDPS2/SOUND/FEPXP.SKX'   # 끝으로 옮길 파일 (그 자리가 WAD 확장 영역)
EXT_LIMIT = (wad.WLBA * SEC + 0x7fffffff) // SEC   # WAD 오프셋 한계 섹터 (seek 가 int)

def copy():
    t = time.time()
    with open(SRC, 'rb') as a, open(OUT, 'wb') as b:
        shutil.copyfileobj(a, b, 64 << 20)
    print('copy', round(time.time() - t, 1), 's')

def build(wadfiles=None, relfiles=None, aliases=None):
    """wadfiles: {경로: bytes}, relfiles: {ISO경로: bytes} (크기 같거나 섹터 여유 이내)."""
    copy()
    ent = {p: (l, s, r) for p, l, s, r in iso.walk(SRC)}
    total = os.path.getsize(SRC) // SEC
    with open(OUT, 'r+b') as f:
        anchor = iso.read(total - 1, SEC, SRC)
        # MOVE -> 끝
        il, isz, _ = ent[MOVE]
        new_l = total - 1
        f.seek(new_l * SEC)
        with open(SRC, 'rb') as s:
            s.seek(il * SEC); rem = isz
            while rem > 0:
                b = s.read(min(rem, 32 << 20)); f.write(b); rem -= len(b)
        pad = (-isz) % SEC; f.write(bytes(pad))
        end = new_l + (isz + SEC - 1) // SEC
        isoedit.relocate(f, SRC, MOVE, new_l, isz)
        # 커진 REL 은 ISO 끝에
        big = {}
        for p, data in (relfiles or {}).items():
            l, s_, _ = ent[p]
            nxt = min(x[0] for x in ent.values() if x[0] > l)
            if l + (len(data) + SEC - 1) // SEC > nxt:
                f.seek(end * SEC); f.write(data + bytes((-len(data)) % SEC))
                isoedit.relocate(f, SRC, p, end, len(data)); big[p] = 1
                end += (len(data) + SEC - 1) // SEC
        f.seek(end * SEC); f.write(anchor)
        nsec = end + 1
        isoedit.set_volume_size(f, nsec)
        EXT0 = il
        # 원래 자리 비우기
        f.seek(il * SEC); f.write(bytes(((isz + SEC - 1) // SEC) * SEC))
        # WAD 파일
        cur = EXT0 * SEC
        dirb = bytearray(wad.head(0x16000))
        idx = {struct.unpack_from('<I', dirb, 8 + 12 * i)[0]: i for i in range(wadfs.N)}
        offs = sorted(set(struct.unpack_from('<I', dirb, 8 + 12 * i + 8)[0] for i in range(wadfs.N)))
        import bisect as _bs
        wsz = ent['MLBPS2.WAD'][1]
        def slot(o):
            j = _bs.bisect_right(offs, o)
            return (offs[j] if j < len(offs) else wsz) - o
        for p, data in (wadfiles or {}).items():
            h = p if isinstance(p, int) else wadfs.h131(p); i = idx[h]
            o0 = struct.unpack_from('<I', dirb, 8 + 12 * i + 8)[0]
            if len(data) <= slot(o0):      # 원래 칸에 들어가면 제자리
                f.seek(wad.WLBA * SEC + o0); f.write(data)
                struct.pack_into('<3I', dirb, 8 + 12 * i, h, len(data), o0); continue
            off = cur - wad.WLBA * SEC
            assert cur + len(data) <= (EXT0 * SEC + isz), 'WAD 확장 영역 부족'
            assert cur + len(data) <= EXT_LIMIT * SEC
            f.seek(cur); f.write(data)
            struct.pack_into('<3I', dirb, 8 + 12 * i, h, len(data), off)
            cur = (cur + len(data) + 15) & ~15
        if aliases:
            # 별칭 항목(새 해시 -> 기존 파일). 늘어난 목록과 겹치는 앞쪽 파일은 확장 영역으로 이동
            tab = [list(struct.unpack_from('<3I', dirb, 8 + 12 * i)) for i in range(wadfs.N)]
            have = {e[0] for e in tab}
            aliases = {k: v for k, v in aliases.items() if k not in have and v in have}
            tab_end = 8 + 12 * (len(tab) + len(aliases))
            for e in tab:
                if e[2] < tab_end:
                    f.seek(wad.WLBA * SEC + e[2]); d = f.read(e[1])
                    off = cur - wad.WLBA * SEC
                    assert cur + len(d) <= (EXT0 * SEC + isz)
                    f.seek(cur); f.write(d); e[2] = off; cur = (cur + len(d) + 15) & ~15
            byh = {e[0]: e for e in tab}
            tab += [[k, byh[v][1], byh[v][2]] for k, v in aliases.items()]
            tab.sort(key=lambda e: e[0])
            dirb = bytearray(dirb[:8]); struct.pack_into('<I', dirb, 0, len(tab))
            for e in tab: dirb += struct.pack('<3I', *e)
            print('얼굴 별칭', len(aliases))
        f.seek(wad.WLBA * SEC); f.write(dirb)
        if wadfiles:
            wl, ws, _ = ent['MLBPS2.WAD']
            isoedit.relocate(f, SRC, 'MLBPS2.WAD', wl, max(ws, cur - wl * SEC))
        # REL/ELF
        for p, data in (relfiles or {}).items():
            if p in big: continue
            l, s, _ = ent[p]
            nxt = min(x[0] for x in ent.values() if x[0] > l)
            assert l + (len(data) + SEC - 1) // SEC <= nxt, p
            f.seek(l * SEC); f.write(data)
            if len(data) != s: isoedit.relocate(f, SRC, p, l, len(data))
    print('built', OUT)
