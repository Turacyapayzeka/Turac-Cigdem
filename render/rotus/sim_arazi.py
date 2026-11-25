"""3B simülasyon filmi: aracı araziye yerleştirir ve dron karelerini hazırlar.

Girdi (render/out/):
    urunfilmi/pikap/   plaka.png, arac-alfa.png, arac-golge.png (arac_maske.py), kamera.json
    simulasyon/arac/   kule-sabit.png, poz/pNN.png, poz.json (simfilm.py kareler)
    simulasyon/arazi/  yakin.jpg, genis.jpg (simfilm.py zemin), ufuk.jpg (sim_ufuk.py)
    simulasyon/dron/   ustNN.png, karsiNN.png (simfilm.py dron)
    simulasyon/gemi/bos.jpg, simulasyon/tesis/bos.jpg
Çıktı (simulasyon/assets/):
    arac.jpg + kare/arac/pNN.jpg          yakın plan: araç arazide; kule pozları
    arac-genis.jpg + kare/arac-genis/     geniş plan: aynı araç, 25 m'lik kadrajda
    ufuk-arac.jpg, ufuk-gemi.jpg, ufuk-tesis.jpg   sensör görüntüsünün arka planları
    dron/ustNN.webp, dron/karsiNN.webp    dron kareleri
    sahne.json (arac, arac_genis güncellenir)

Araç, stüdyo zemininden alfa maskesiyle ayrılır; stüdyo zeminine düşen gölgesi arazi görüntüsüne çarpılarak taşınır.
    python3 render/rotus/sim_arazi.py
"""
import sys, os, json, glob
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pikap_studyo as ps

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'); HEDEF = os.path.join(KOK, 'simulasyon', 'assets'); CIK = os.path.join(KOK, 'render', 'out')
ARAZI = os.environ.get('SIM_ARAZI', os.path.join(CIK, 'simulasyon', 'arazi')); DRON = os.environ.get('SIM_DRON', os.path.join(CIK, 'simulasyon', 'dron'))      # deneme için başka klasör verilebilir
GENIS = dict(olcek=25.0, en=3840, boy=2160, kule=(0.60, 0.60))        # simfilm.py ile aynı
K = ps.K

def yaz(yol, im, q=92): os.makedirs(os.path.dirname(yol), exist_ok=True); cv2.imwrite(yol, (np.clip(im, 0, 1) * 255).round().astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, q])

def arac():
    pd = os.path.join(CIK, 'urunfilmi', 'pikap'); d = os.path.join(CIK, 'simulasyon', 'arac'); kam = json.load(open(os.path.join(pd, 'kamera.json'))); P = json.load(open(os.path.join(d, 'poz.json')))
    pl = ps.oku(os.path.join(pd, 'plaka.png')); H, W = pl.shape[:2]; alfa = ps.oku(os.path.join(pd, 'arac-alfa.png'))[..., None]; golge = ps.oku(os.path.join(pd, 'arac-golge.png'))[..., None]
    # temas gölgesi: aracın alt kenarlarının hemen dibinde zemin koyulaşır (maske aşağı kaydırılıp yumuşatılır; üst kenarlarda etkisizdir)
    kay = cv2.warpAffine(alfa[..., 0], np.float32([[1, 0, -4], [0, 1, 12]]), (W, H)); temas = np.clip((cv2.GaussianBlur(kay, (0, 0), 10) - 0.08) / 0.5, 0, 1); temas = temas * temas * (3 - 2 * temas)
    genis_temas = cv2.GaussianBlur(cv2.warpAffine(alfa[..., 0], np.float32([[1, 0, -10], [0, 1, 34]]), (W, H)), (0, 0), 30)
    golge = golge * (1 - 0.5 * temas[..., None]) * (1 - 0.22 * genis_temas[..., None])
    sabit = ps.oku(os.path.join(d, 'kule-sabit.png')); agiz = ps.agiz_maskesi(kam, H, W); var = [i for i in range(P['poz']) if os.path.exists(os.path.join(d, 'poz', f'p{i:02d}.png'))]
    # ---- yakın plan: arazi görüntüsü kadrajın tamamıdır; araç ve kule onun içine oturur
    zemin = ps.oku(os.path.join(ARAZI, 'yakin.jpg')); Hc, Wc = zemin.shape[:2]; ox, oy = ps.YAN * K, ps.UST * K
    def yerlestir(kat, dolgu):
        t = np.full((Hc, Wc, kat.shape[2]), dolgu, np.float32); t[oy:oy + H, ox:ox + W] = kat; return t
    A = yerlestir(alfa, 0.0); taban = zemin * yerlestir(golge, 1.0) * (1 - A) + yerlestir(pl, 0.0) * A
    taban = ps.bindir(taban, yerlestir(sabit, 0.0), yerlestir(agiz[..., None], 0.0)[..., 0])
    k = P['kutu']; G, Y = kam['W'] + 2 * ps.YAN, kam['H'] + ps.UST + ps.ALT
    kutu = [(k[0] * kam['W'] + ps.YAN) / G, (k[1] * kam['H'] + ps.UST) / Y, (k[2] * kam['W'] + ps.YAN) / G, (k[3] * kam['H'] + ps.UST) / Y]
    x0, y0, x1, y1 = int(kutu[0] * 3840), int(kutu[1] * 2160), int(np.ceil(kutu[2] * 3840)), int(np.ceil(kutu[3] * 2160)); tamlar = {}
    for i in range(P['poz']):
        v = max(j for j in var if j <= i)
        if v not in tamlar: tamlar[v] = cv2.resize(ps.bindir(taban, yerlestir(ps.oku(os.path.join(d, 'poz', f'p{v:02d}.png')), 0.0)), (3840, 2160), interpolation=cv2.INTER_AREA)
        im = tamlar[v]
        if i == 0: yaz(os.path.join(HEDEF, 'arac.jpg'), im, 93)
        yaz(os.path.join(HEDEF, 'kare', 'arac', f'p{i:02d}.jpg'), im[y0:y1, x0:x1])
    uc = [ps.oran(kam, u) for u in P['uc']]; ates = np.array(ps.oran(kam, np.array(P['uc'][0]) + np.array(P['yon']))) - np.array(uc[0]); ates = ates * np.array([16, 9]); ates /= np.linalg.norm(ates)
    S = {'arac': {'kule': ps.oran(kam, P['kule']), 'namlu': uc, 'ates': [round(float(v), 4) for v in ates], 'kutu': [round(x0 / 3840, 5), round(y0 / 2160, 5), round(x1 / 3840, 5), round(y1 / 2160, 5)], 'poz': P['poz']}}
    # ---- geniş plan: aynı katmanlar küçültülerek 25 m'lik arazi karesine yerleştirilir
    Gn = GENIS; zg = ps.oku(os.path.join(ARAZI, 'genis.jpg')); pm = Gn['en'] / Gn['olcek']; f = pm / (kam['s'] * K)       # araç katmanlarının küçültme oranı
    kx, ky = Gn['kule'][0] * Gn['en'], Gn['kule'][1] * Gn['boy']; sx, sy = kx - kam['p0'][0] * K * f, ky - kam['p0'][1] * K * f; M = np.float32([[f, 0, sx], [0, f, sy]])
    kucult = lambda kat, dolgu=0.0: cv2.warpAffine(kat, M, (Gn['en'], Gn['boy']), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=dolgu)
    Ag = kucult(alfa)[..., None]; tg = zg * kucult(golge[..., 0], 1.0)[..., None] * (1 - Ag) + kucult(pl) * Ag; tg = ps.bindir(tg, kucult(sabit), kucult(agiz))
    def gpx(X):                                                       # araç koordinatından geniş karedeki orana
        p = (ps.izdus(kam, X) * K) * f + np.array([sx, sy]); return [round(float(p[0] / Gn['en']), 5), round(float(p[1] / Gn['boy']), 5)]
    gk = [P['kutu'][0] * W * f + sx, P['kutu'][1] * H * f + sy, P['kutu'][2] * W * f + sx, P['kutu'][3] * H * f + sy]; gx0, gy0, gx1, gy1 = int(gk[0]), int(gk[1]), int(np.ceil(gk[2])), int(np.ceil(gk[3])); gtam = {}
    for i in range(P['poz']):
        v = max(j for j in var if j <= i)
        if v not in gtam: gtam[v] = ps.bindir(tg, kucult(ps.oku(os.path.join(d, 'poz', f'p{v:02d}.png'))))
        if i == 0: yaz(os.path.join(HEDEF, 'arac-genis.jpg'), gtam[v], 93)
        yaz(os.path.join(HEDEF, 'kare', 'arac-genis', f'p{i:02d}.jpg'), gtam[v][gy0:gy1, gx0:gx1])
    A3 = np.array(kam['A']) / kam['s'] * pm; guc = [gpx(u) for u in P['uc']]; gates = np.array(gpx(np.array(P['uc'][0]) + np.array(P['yon']))) - np.array(guc[0]); gates = gates * np.array([16, 9]); gates /= np.linalg.norm(gates)
    S['arac_genis'] = {'kule': gpx(P['kule']), 'namlu': guc, 'ates': [round(float(v), 4) for v in gates], 'kutu': [round(gx0 / Gn['en'], 5), round(gy0 / Gn['boy'], 5), round(gx1 / Gn['en'], 5), round(gy1 / Gn['boy'], 5)], 'poz': P['poz'],
                       'kule3': [round(float(v), 4) for v in P['kule']], 'uc3': [[round(float(v), 4) for v in u] for u in P['uc']], 'yon3': [round(float(v), 4) for v in P['yon']],
                       'A': [[round(float(v) / Gn['en'], 7) for v in A3[0]], [round(float(v) / Gn['boy'], 7) for v in A3[1]]], 'pm': pm, 'alev': 0.45}       # alev: namlu alevinin yakın plana göre ölçeği
    return S

def ufuklar():
    yaz(os.path.join(HEDEF, 'ufuk-arac.jpg'), ps.oku(os.path.join(ARAZI, 'ufuk.jpg')), 92)
    for ad, (x, y, w) in {'gemi': (0.02, 0.08, 0.60), 'tesis': (0.33, 0.05, 0.50)}.items():
        im = ps.oku(os.path.join(CIK, 'simulasyon', ad, 'bos.jpg')); H, W = im.shape[:2]; x0, y0, ww = int(x * W), int(y * H), int(w * W); hh = ww * 9 // 16
        yaz(os.path.join(HEDEF, f'ufuk-{ad}.jpg'), cv2.resize(im[y0:y0 + hh, x0:x0 + ww], (1920, 1080), interpolation=cv2.INTER_CUBIC), 90)

def dronlar():
    os.makedirs(os.path.join(HEDEF, 'dron'), exist_ok=True); n = {}
    for tur, boyut in (('ust', 192), ('karsi', 512)):
        fs = sorted(glob.glob(os.path.join(DRON, tur + '*.png'))); n[tur] = len(fs)
        for i, f in enumerate(fs):
            im = cv2.imread(f, cv2.IMREAD_UNCHANGED); im = cv2.resize(im, (boyut, boyut), interpolation=cv2.INTER_AREA) if im.shape[0] != boyut else im
            cv2.imwrite(os.path.join(HEDEF, 'dron', f'{tur}{i:02d}.webp'), im, [cv2.IMWRITE_WEBP_QUALITY, 88])
    return n

if __name__ == '__main__':
    yol = os.path.join(HEDEF, 'sahne.json'); S = json.load(open(yol)) if os.path.exists(yol) else {}
    S.update(arac()); ufuklar(); S['dron'] = dronlar(); json.dump(S, open(yol, 'w'), indent=1); print({k: (v if k == 'dron' else {a: v[a] for a in ('kule', 'kutu')}) for k, v in S.items() if k in ('arac', 'arac_genis', 'dron')})
