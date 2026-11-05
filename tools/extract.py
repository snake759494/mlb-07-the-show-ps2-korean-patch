"""원본 ISO에서 빌드에 필요한 게임 파일 추출 -> work/ext (실행파일·REL·MLBDAT), work/font (글꼴 bin/tx2).
사용: python tools/extract.py  (원본 ISO는 저장소 루트의 'MLB 07 - The Show (USA) (v2.00).iso')"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); import iso
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, 'work', 'ext'); FONT = os.path.join(ROOT, 'work', 'font')
WANT = {'SCUS_975.56', 'SYSTEM.CNF', 'FE.REL', 'GAME.REL', 'GHOSTMAN.REL', 'HRDERBY.REL', 'INITDLL.REL', 'OLDLL.REL', 'MLBDAT.BIN'}

def main():
    os.makedirs(EXT, exist_ok=True); os.makedirs(FONT, exist_ok=True)
    for p, lba, size, _ in iso.walk():
        nm = p.split('/')[-1]
        if nm in WANT:
            open(os.path.join(EXT, nm), 'wb').write(iso.read(lba, size)); print(p, size)
    import wadfs          # 해시 계산에 실행파일(ctype 표)이 필요해 추출 뒤에 불러옴
    for n in ("english", "game", "game2", "symbols"):
        for e in ('bin', 'tx2'):
            path = 'frontend/art/fonts/%s.%s' % (n, e)
            open(os.path.join(FONT, '%s.%s' % (n, e)), 'wb').write(wadfs.read(path)); print(path)

if __name__ == '__main__':
    main()
