"""한글 글리프를 원본 폰트(bin+tx2)에 추가.
코드 0x100+k -> 글리프 인덱스 0xE0+k (first=0x20). 0x61~0xDF 는 빈 레코드.
각 서브폰트 레코드 0 (공백, 미사용) 은 '앞 서브폰트 한글 반 폭' 대체 글리프로,
마지막 서브폰트 뒤에는 그 반 폭 레코드를 하나 더 붙인다 (측정 함수의 대체 인덱스=count 용)."""
import struct, os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__)); import tx2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, 'work', 'font')
NANUM = os.path.join(ROOT, 'NanumSquareNeo-eHv.ttf')
GAL = os.path.join(ROOT, 'Galmuri11-Bold.ttf')
FIRST = 0x20; KBASE = 0xE0

# 서브폰트 스타일: (렌더키, 가로배율)
STYLE = {
    'english': [('gal', 1.0), ('gal', 1.5), ('nanum17', 1.0)],
    'game': [('gal', 1.0), ('gal', 1.4)],
    'game2': [('gal', 1.0)],
}

def read_bin(d):
    n = struct.unpack_from('<I', d)[0]
    cs = list(struct.unpack_from('<%dI' % n, d, 4))
    off = 16 if n == 3 else 4 + 4 * n
    subs = []
    for c in cs:
        subs.append([list(struct.unpack_from('<4f6h', d, off + 28 * k)) for k in range(c)]); off += 28 * c
    return off - 28 * sum(cs), subs

def render(key, ch):
    """(알파 0~1 배열) 반환. 내용 상자로 잘림 없이 고정 셀."""
    if key == 'gal':
        f = ImageFont.truetype(GAL, 12); size = (12, 13); sh = 0
    else:
        f = ImageFont.truetype(NANUM, 17); size = (18, 19); sh = 0.18
    im = Image.new('L', (size[0] * 2, size[1] * 2), 0)
    dr = ImageDraw.Draw(im)
    if key == 'gal': dr.fontmode = '1'
    dr.text((size[0] // 2, size[1] // 2), ch, 255, font=f)
    if sh:
        W, H = im.size
        im = im.transform(im.size, Image.AFFINE, (1, sh, -sh * H / 2, 0, 1, 0), Image.BICUBIC)
    a = np.asarray(im, dtype=np.float32) / 255
    return a

def boxes(key, chars):
    """모든 글자 공통 세로 범위와 글자별 가로 범위로 잘라냄."""
    al = [render(key, c) for c in chars]
    S = np.maximum.reduce(al) if al else None
    rows = np.where(S.max(1) > 0.05)[0]; cols = np.where(S.max(0) > 0.05)[0]
    y0, y1 = rows[0], rows[-1] + 1; x0, x1 = cols[0], cols[-1] + 1
    return [a[y0:y1, x0:x1] for a in al]

def nearest(P, rgba):
    P = np.array([list(p) for p in P], dtype=np.float32)
    return int(np.argmin(((P - np.array(rgba, np.float32)) ** 2 * [1, 1, 1, 3]).sum(1)))

def build(name, chars, W=1024, prio=None):
    d = open(os.path.join(FONT, name + '.bin'), 'rb').read()
    hdr, subs = read_bin(d)
    t = open(os.path.join(FONT, name + '.tx2'), 'rb').read()
    w0, h0, img0, P = tx2.decode(t)
    H = int(os.environ.get('GH_'+name, 512))
    img = np.zeros((H, W), np.uint8); img[:h0, :w0] = img0
    lv = [nearest(P, (0x2d, 0x2d, 0x2d, int(0x60 * a))) for a in np.linspace(0, 1, 9)]
    lw = [nearest(P, (0xfe, 0xfe, 0xfe, int(0x80 * a))) for a in np.linspace(0, 1, 9)]
    lw[0] = lv[0] = nearest(P, (0, 0, 0, 0))
    # 렌더 키별 글리프 그림 -> 텍스처 배치 (같은 키는 공유)
    keys = sorted(set(k for k, _ in STYLE[name]))
    place = {}
    x, y, rowh = 64, 0, 0
    for key in keys:
        gl = boxes(key, chars); pos = [None] * len(chars)
        order = range(len(chars)) if not prio else sorted(range(len(chars)), key=lambda i: prio.get(chars[i], 1 << 30))
        for i in order:
            g = gl[i]
            gh, gw = g.shape
            cw, chh = gw + 2, gh + 2       # 1px 외곽선 테두리
            if x + cw > W: x, y, rowh = 64, y + rowh, 0
            if y + chh > H:
                assert key != 'gal' or W < 512 or os.environ.get('GH_'+name), (name, 'texture full')
                break
            # 외곽선(어두운) + 본체(흰색)
            from scipy.ndimage import maximum_filter
            pad = np.zeros((chh, cw), np.float32); pad[1:-1, 1:-1] = g
            sh = maximum_filter(pad, 3)
            q = np.where(pad > 0.12, np.take(lw, np.clip((pad * 8 + .5).astype(int), 0, 8)),
                         np.take(lv, np.clip((sh * 8 + .5).astype(int), 0, 8)))
            img[y:y + chh, x:x + cw] = q
            pos[i] = (x + 1, y + 1, gw, gh)
            x += cw; rowh = max(rowh, chh)
        place[key] = pos
    # 레코드
    newsubs = []; halfs = []
    for si, (key, xs) in enumerate(STYLE[name]):
        recs = subs[si][:0x61] + [[0.0] * 4 + [0] * 6 for _ in range(KBASE - 0x61)]
        A = subs[si][0x21]; ah = A[5]
        adv_all = []
        ref = next((p for p in place[key] if p), None)
        gref = next(p for p in place['gal'] if p)
        sc = (ref[3] + 2) / (gref[3] + 2)
        for k, p in enumerate(place[key]):
            s2 = xs
            if p is None: p = place['gal'][k]; s2 = sc * xs
            if p is None: p = (0, 0, 0, 0)
            u, v, gw, g_h = p
            qw = int(round((gw + 2) * s2))
            qh = int(round((g_h + 2) * (sc if s2 != xs else 1)))
            yoff = A[6] - (qh - ah) // 2
            adv = qw + 0
            if adv % 2: qw += 1
            recs.append([float(u), float(v), float(u + gw), float(v + g_h), qw, qh, yoff, 0, 0, 0])
            adv_all.append(qw)
        halfs.append(max(adv_all) // 2 if adv_all else 0)
        newsubs.append(recs)
    # 레코드 0 = 앞 서브폰트 반 폭
    for si in range(1, len(newsubs)):
        newsubs[si][0] = [0.0] * 4 + [halfs[si - 1], 0, 0, 0, 0, 0]
    tail = [0.0] * 4 + [halfs[-1], 0, 0, 0, 0, 0]
    # 한글 글자 폭 통일 (반 폭 x2) - 측정과 렌더 일치
    for si, recs in enumerate(newsubs):
        for r in recs[KBASE:]:
            r[8] = halfs[si] * 2 - r[4]
    out = bytearray(struct.pack('<I', len(newsubs)) + struct.pack('<%dI' % len(newsubs), *[len(r) for r in newsubs]))
    out += bytes(hdr - len(out))
    for recs in newsubs:
        for r in recs: out += struct.pack('<4f6h', *r[:4], *[int(v) for v in r[4:]]) + b'\0\0' if False else struct.pack('<4f6h', *r[:4], *[int(v) for v in r[4:]])
    out += struct.pack('<4f6h', *tail[:4], *[int(v) for v in tail[4:]])
    return bytes(out), tx2.encode(t, img), img
