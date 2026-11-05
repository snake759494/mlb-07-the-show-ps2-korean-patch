"""한글패치 전체 빌드: 번역 로드/검증 -> 글자셋 -> 폰트 -> WAD(화면세트, 도움말) -> REL(훅+문자열) -> ISO."""
import os, sys, re, json, glob, collections, struct
sys.path.insert(0, os.path.dirname(__file__))
import gtips, facelist, wadfs, scr, legend, notes, helpcsv, career, names, teams, relstr, relcand, codepatch, fontgen, ktext, build
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRD = os.path.join(ROOT, 'translation')
SPARE = {'GHOSTMAN': [0x246330, 0x23f868], 'HRDERBY': [0x28c680, 0x285b28], 'GAME': [0x350bc0, 0x348b48]}
INIT = {'FE': [0x3b8ac2, 0x3b8b42, 0x3ccfd0], 'GAME': [0x319db0, 0x320e10, 0x33bc50], 'HRDERBY': [0x26f5e0]}
# 엔진 내부 키로 쓰이는 단어 (REL 에서 번역 금지)
RELBLOCK = set('''Notice Confirm Global Context Parent Blink Chew Face Name Crowd Update Render Collide Collision System Actor Morph Fade
Swing Popup Shot Prime Dagger Catch Equal And Invalid Criteria Situation Succeeded Failed Offset Wide Tight Waiting
Vibration Warning Speed Power Contact Baseline Dugout Walkability Appeal Appeals Strikes Top Bot Full Simple Game
Other Ready Done Runners Leadoff Outs Inning Playoffs Away Normal Low High Medium None Few Many Auto Off On All East
Turf Grass Shibe Crosley Tampa Minneapolis Arlington Miami Phoenix Denver Tempe Flagstaff'''.split()) | {'Bat Tip', 'Bat Handle', 'FirstBase ', 'SecondBase ', 'ThirdBase '}
INLBLOCK = set('''Home Away Crimson Cobalt American National Player Runner Batter Catcher Pitcher Fielder Undefined Dugout
Step Lift Left Right Center'''.split()) | {'Player 1', 'Player 2', 'Right Field', 'Center Field', 'Left Field', 'Third Base', 'Second Base',
    'First Base', 'Short Stop', 'Base Coach1', 'Base Coach2'}
SINGLE_OK = set('''Rookie Veteran All-Star Legend Default Meter Classic Night Day Assist Manual Enhanced Broadcast Dynamic Arcade Simulation Easy Hard'''.split())
GTSHELL = [0x10b52d4, 0x2b88660e, 0x94ca1258]
CODE = re.compile(r'\^[^^]*\^|%\d')

def load_tr():
    tr = {}
    for p in sorted(glob.glob(os.path.join(TRD, 'ko_*.json'))):
        if re.search(r'ko_\d+\.json$', p): tr.update(json.load(open(p, encoding='utf8')))
    bad = 0; out = {}
    for k, v in tr.items():
        if not isinstance(v, str) or v == k: continue
        if sorted(CODE.findall(k)) != sorted(CODE.findall(v)) or re.search(r'[^\x20-\x7e가-힣]', v):
            bad += 1; continue
        out[k] = v
    print('번역', len(out), '제외', bad)
    return out

def load_extra():
    ex = {}
    for p in sorted(glob.glob(os.path.join(TRD, 'ko_x*.json'))): ex.update(json.load(open(p, encoding='utf8')))
    ex = {k: v for k, v in ex.items() if isinstance(v, str) and v != k and not re.search(r'[^ -~가-힣]', v)
          and sorted(CODE.findall(k)) == sorted(CODE.findall(v))}
    tm = json.load(open(os.path.join(TRD, 'teams_ko.json'), encoding='utf8'))
    for d_ in (tm['city'], tm['nick']):
        for k_, v_ in d_.items(): ex.setdefault(k_, v_)
    print('추가 번역', len(ex), '팀', len(tm['city']), len(tm['nick']))
    return ex, tm

def main(run_build=True):
    tr = load_tr()
    ex, tm = load_extra()
    if os.environ.get('NOEX'): ex = {}
    # 사용 빈도 (큰 서브폰트 우선순위)
    nm = {'first': {}, 'last': {}}
    for p_ in sorted(glob.glob(os.path.join(TRD, 'names_ko_*.json'))):
        j = json.load(open(p_, encoding='utf8'))
        for k in nm:
            for a_, b_ in j[k].items():
                if a_ != b_ and not re.search(r'[^ -~가-힣]', b_) and len(b_.encode('cp949')) <= 15: nm[k].setdefault(a_, b_)
    if True:
        base = set(c for v in list(tr.values()) + list(ex.values()) + list(tm['city'].values()) + list(tm['nick'].values()) for c in v if ord(c) >= 0x80); cap = int(os.environ.get('NAMECAP', 1096)); base |= set('궈홍')
        while True:
            need = collections.Counter(c for k in nm for b in nm[k].values() for c in set(b) - base)
            if not need or len(base) >= cap: break
            base.add(need.most_common(1)[0][0])
        for k in nm: nm[k] = {a: b for a, b in nm[k].items() if set(b) <= base}
    print('이름', len(nm['first']), len(nm['last']))
    freq = collections.Counter(c for v in list(tr.values()) + list(ex.values()) + list(tm['city'].values()) + list(tm['nick'].values()) + list(nm['first'].values()) + list(nm['last'].values()) for c in v if ord(c) >= 0x80)
    chars = sorted(freq)
    print('글자 수', len(chars))
    E = ktext.Enc(chars)
    tb = {k.encode('latin1'): E.enc(v) for k, v in tr.items()}
    prio = {c: i for i, (c, n) in enumerate(freq.most_common())}
    occ = collections.Counter(c for v in list(tr.values()) + list(ex.values()) for c in v if ord(c) >= 0x80)
    for _ in range(8): occ.update(c for v in list(nm['first'].values()) + list(nm['last'].values()) for c in v if ord(c) >= 0x80)
    occ.update({c: 10 ** 6 for c in '닫기둘끄기'})
    prio_g = {c: i for i, (c, n) in enumerate(occ.most_common())}
    wf = {}
    for n in ([] if os.environ.get('ORIGFONT') else os.environ.get('FONTS', 'english,game,game2').split(',')):
        b, t, img = fontgen.build(n, chars, W=int(os.environ.get('GW_'+n, 256 if n == 'game' else 512)), prio=prio_g if n == 'game' else prio)
        wf['frontend/art/fonts/%s.bin' % n] = b; wf['frontend/art/fonts/%s.tx2' % n] = t
    nsc = 0
    exb = {k.encode('latin1'): E.enc(v) for k, v in ex.items()}
    tbx = dict(exb); tbx.update(tb)
    sf = set(json.load(open(os.path.join(TRD, 'scr_files.json'))))
    if not os.environ.get('NOSCR2'):
        s2 = json.load(open(os.path.join(TRD, 'scr_files2.json')))
        if os.environ.get('S2'): lo_, hi_ = map(int, os.environ['S2'].split(':')); s2 = s2[lo_:hi_]
        sf |= set(s2)
    sf3 = set(json.load(open(os.path.join(TRD, 'scr_files3.json'))))
    for h in sorted(sf3):
        b = wadfs.read(wadfs.BYH[h])
        pad = {k_: (v_ + b' ' * (len(k_) - len(v_))) for k_, v_ in tbx.items() if len(v_) <= len(k_)}
        nb = scr.apply(b, pad)
        if nb != b: wf[h] = nb
    trall = dict(ex); trall.update(tr); ngt = 0
    for h in sorted(sf):
        b = wadfs.read(wadfs.BYH[h]); m_ = tbx if h in sf else tb
        if not os.environ.get('NOGT') and b'GT_' in b[:400]:
            g_ = gtips.plan(b, trall)
            if g_: m_ = dict(m_); m_.update({k_: E.enc(v_) for k_, v_ in g_.items()}); ngt += 1
        nb = scr.apply(b, m_)
        if nb != b: wf[h] = nb; nsc += 1
    trs = {k: E.enc(v).decode('latin1') for k, v in tr.items()}
    for h in helpcsv.FILES:
        b = wadfs.read(wadfs.BYH[h]); wf[h] = helpcsv.apply(b, trs)
    b = wadfs.read(wadfs.BYH[career.H]); wf[career.H] = career.apply(b, tb)
    fm = {k.encode('latin1'): E.enc(v) for k, v in nm['first'].items()}
    lm = {k.encode('latin1'): E.enc(v) for k, v in nm['last'].items()}
    if (fm or lm) and not os.environ.get('NONAME'):
        nfl = json.load(open(os.path.join(TRD, 'names_src.json')))['files']
        if os.environ.get('NAMEF'): a_, b_ = map(int, os.environ['NAMEF'].split(':')); nfl = nfl[a_:b_]
        for h in nfl:
            wf[h] = names.apply(wadfs.read(wadfs.BYH[h]), fm, lm)
        if os.environ.get('FACEL'):
            wf[facelist.H] = facelist.apply(wadfs.read(wadfs.BYH[facelist.H]), fm, {k: b'Zzqx' for k in lm} if os.environ.get('N8', '').startswith('a') else lm)
        if os.environ.get('N8', 'fl:0:99999') != 'none':
            md_, lo_, hi_ = os.environ.get('N8', 'fl:0:99999').split(':'); h = 0x8382e1b8
            wf[h] = names.apply(wadfs.read(wadfs.BYH[h]), fm if 'f' in md_ else {}, ({k: b'Zzqx' for k in lm} if 'a' in md_ else lm) if 'l' in md_ or 'a' in md_ else {}, (int(lo_), int(hi_)))
    cm = {k.encode('latin1'): E.enc(v) for k, v in tm['city'].items()}
    tn = {k.encode('latin1'): E.enc(v) for k, v in tm['nick'].items()}
    if not os.environ.get('NOTEAM'):
        for h in teams.FILES:
            wf[h] = teams.apply(wf.get(h) or wadfs.read(wadfs.BYH[h]), cm, tn)
    for h in notes.FILES:
        wf[h] = notes.apply(wf.get(h) or wadfs.read(wadfs.BYH[h]), exb)
    for h in legend.FILES + [legend.LIST]:
        wf[h] = legend.apply(wadfs.read(wadfs.BYH[h]), exb)
    if os.environ.get('WKEEP') is not None:
        cat = {}
        for h in sf3: cat[h] = 'scr3'
        for h in sf: cat[h] = 'scr'
        for h in helpcsv.FILES: cat[h] = 'help'
        cat[career.H] = 'career'
        for h in json.load(open(os.path.join(TRD, 'names_src.json')))['files']: cat[h] = 'names'
        for h in teams.FILES: cat[h] = 'teams'
        for h in notes.FILES: cat[h] = cat.get(h, 'notes')
        for h in legend.FILES + [legend.LIST]: cat[h] = 'legend'
        keep = set(os.environ['WKEEP'].split(','))
        wf = {k: v for k, v in wf.items() if cat.get(k, 'font') in keep}
    # 팁 창 버튼 테두리(PS_ButtonBak)는 영문 아이콘 위치에 고정 -> 숨김(알파 0)
    for h in list(wf) + [x for x in GTSHELL if x not in wf]:
        b = bytearray(wf.get(h) or wadfs.read(wadfs.BYH[h]))
        if b'GameTipsShell4' not in b[:0x60]: continue
        i_ = b.find(b'PS_ButtonBak')
        while i_ >= 0:
            j_ = b.rfind(bytes([0x7f, 0x7f, 0x7f, 0x7f]), i_ - 40, i_)
            if j_ > 0: b[j_ + 3] = 0
            i_ = b.find(b'PS_ButtonBak', i_ + 1)
        wf[h] = bytes(b)
    print('팁 분할', ngt)
    print('WAD 파일', len(wf), '화면세트', nsc)
    rels = {}
    for n in ['FE', 'GAME', 'HRDERBY', 'GHOSTMAN']:
        p = codepatch.Patch(os.path.join(ROOT, 'work', 'ext', n + '.REL'), n)
        p.spare = SPARE.get(n, [])     # 디버그 안내문 자리를 훅 공간으로
        # 이니셜 포맷 '%c. %s' -> '%c<01>%s' (한글 이름 첫 바이트 잘림 방지: 선두 바이트·0x01 은 폭 0)
        for a_ in INIT.get(n, []):
            o_ = p.r.d[a_:p.r.d.index(bytes(1), a_)]
            p.fix[a_] = o_.replace(b'. ', bytes([1])).replace(b'.', bytes([1])) + bytes(1)
        cnt = 0
        if n in relcand.LO:
            r, c = relcand.cand(n, set(tb) | set(exb))
            sel = os.environ.get('SEL')
            for j, (s, t) in enumerate(c):
                ok = True
                if sel:
                    ok = False
                    for part in sel.split(';'):
                        sn, lo, hi = part.split(':')
                        if sn == n and int(lo) <= j < int(hi): ok = True
                if t.decode('latin1') in INLBLOCK or (b' ' not in t and t.decode('latin1') in RELBLOCK): continue
                tt = tb.get(t) or (exb.get(t) if not os.environ.get('NOEXREL') and t.decode('latin1') not in RELBLOCK | INLBLOCK else None)
                if tt and not os.environ.get('NOSTR'): p.add_string(s, tt if ok else t); cnt += 1
        if n in relcand.LO and exb:
            _, out_, _ = relstr.scan(os.path.join(ROOT, 'work', 'ext', n + '.REL'), relcand.LO[n])
            xs = os.environ.get('XSEL', 'NONE:0:0'); j = 0
            for s_, t_, rf_ in out_:
                if rf_ and t_ in exb and s_ not in p.strings and t_.decode('latin1') not in RELBLOCK and not (os.environ.get('BLK2') and (t_.decode('latin1') in tm['city'] or t_.decode('latin1') in tm['nick'] or re.search(r'Park|Field|Stadium|Centre|Coliseum|Grounds|Beach|City|Mountain', t_.decode('latin1')))):
                    ok = True
                    if xs:
                        sn, lo, hi = xs.split(':'); ok = sn == n and int(lo) <= j < int(hi)
                    if os.environ.get('XDUMP'): print('XD', n, j, t_.decode('latin1'))
                    if ok: p.add_string(s_, exb[t_]); cnt += 1
                    j += 1
        if not os.environ.get('NOINL') and n in relcand.LO:
            _, out_, _ = relstr.scan(os.path.join(ROOT, 'work', 'ext', n + '.REL'), relcand.LO[n])
            ni = 0
            for s_, t_, rf_ in out_:
                if s_ in p.strings or t_ not in tbx: continue
                k_ = t_.decode('latin1')
                if rf_ and k_ not in SINGLE_OK: continue
                if k_ in RELBLOCK or k_ in INLBLOCK or k_ in tm['city'] or k_ in tm['nick']: continue
                v_ = tbx[t_]; cap_ = ((s_ + len(t_) + 1 + 3) & ~3) - s_
                if len(v_) + 1 > cap_ or any(p.r.d[s_ + len(t_):s_ + cap_]): continue
                p.fix[s_] = v_ + bytes(cap_ - len(v_)); ni += 1
            print(n, '고정칸', ni)
        rels[n + '.REL'] = p.build(); print(n, '문자열', cnt, '이동/제자리/생략/여유', p.stats)
    # 유니폼 등 이름 비우기: 한글 성은 등 글자 텍스처로 못 그림 (movn s1,v0,v1 -> move s1,zero)
    if not os.environ.get('NOJERSEY'):
        pat = bytes.fromhex('0e0043288000a5270b884300')
        for k_ in list(rels):
            b_ = bytearray(rels[k_]); i_ = b_.find(pat)
            assert i_ > 0 and b_.find(pat, i_ + 1) < 0, k_
            b_[i_ + 8:i_ + 12] = struct.pack('<I', 0x00008821); rels[k_] = bytes(b_)
    if os.environ.get('ORIGREL'): rels = {}
    al = {}
    if (fm or lm) and not os.environ.get('NONAME') and not os.environ.get('NOALIAS'):
        orig = lambda b_: bytes(c for c in b_.split(bytes(1))[0] if c not in b" '.,`-")
        for h in json.load(open(os.path.join(TRD, 'names_src.json')))['files'] + [0x8382e1b8]:
            for s_, f1, f2 in names.pairs(wadfs.read(wadfs.BYH[h])):
                kf = fm.get(f1, f1)[:16]; kl = lm.get(f2, f2)[:16]
                if (kf, kl) == (f1, f2): continue
                eh = wadfs.h131(b'data/heads/' + orig(f2) + b'_' + orig(f1) + b'/PackFile.PS2')
                if eh in wadfs.BYH: al[wadfs.h131(b'data/heads/' + orig(kl) + b'_' + orig(kf) + b'/PackFile.PS2')] = eh
                if os.environ.get('TEXREN') and eh in wadfs.BYH and eh not in wf:
                    pk = wadfs.read(wadfs.BYH[eh]); i_ = pk.find(b'STRGTEXN', max(0, pk.find(b'face.') - 32))
                    if i_ >= 0:
                        n_, sz_ = struct.unpack_from('<II', pk, i_ + 8); body = pk[i_ + 16:i_ + 16 + sz_]
                        parts = body.split(bytes(1))
                        if parts[0].startswith(b'face.') and parts[0].endswith(b'.512'):
                            parts[0] = b'face.' + orig(kl) + b'_' + orig(kf) + b'.512'
                            nb_ = bytes(1).join(parts[:n_]) + bytes(1)
                            if len(nb_) <= sz_:
                                wf[eh] = pk[:i_ + 16] + nb_ + bytes(sz_ - len(nb_)) + pk[i_ + 16 + sz_:]
        if os.environ.get('ALW'):
            w_ = set(os.environ['ALW'].split(','))
            al = {k: v for k, v in al.items() if v in {wadfs.h131(b'data/heads/' + x.encode() + b'/PackFile.PS2') for x in w_}}
        print('얼굴 경로', len(al))
    if run_build: build.build(wf, rels, al)
    return wf, rels

if __name__ == '__main__':
    main('-n' not in sys.argv)
