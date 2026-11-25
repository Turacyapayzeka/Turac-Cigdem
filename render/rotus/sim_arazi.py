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
    arac-uzak.jpg                         açılıştaki dalış çekimi: 100 m'lik arazi karesi, ortasında araç
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

UZAK = dict(kat=4, en=3200, boy=1800)                                  # açılıştaki dalış çekimi: geniş planın 4 katı (100 m) genişliğinde kare

def uzak():
    """Açılıştaki dalış çekiminin 100 metrelik arazi karesi. Araçsız geniş arazi görüntüsünün iz ve taş olmayan üst bölümünden
    alınan parçalar yumuşak kenarlarla örülür; ortasına araçlı geniş plan oturtulur, aracın tekerlek izi kenara kadar uzatılır."""
    U = UZAK; W, H = U['en'], U['boy']; w, h = W // U['kat'], H // U['kat']; rng = np.random.default_rng(8)
    kaynak = cv2.resize(ps.oku(os.path.join(ARAZI, 'genis.jpg')), (w, h), interpolation=cv2.INTER_AREA); ust = kaynak[:int(h * 0.46)].copy()
    tx, ty = int(0.475 * w), int(0.305 * h); ust[ty - 9:ty + 9, tx - 11:tx + 11] = ust[ty - 9:ty + 9, tx + 29:tx + 51]            # üst bölümdeki tek iri taş komşu zeminle örtülür
    isik = np.maximum(cv2.GaussianBlur(kaynak, (0, 0), 40), 1e-3); ort = ust.mean((0, 1)); ust = ust / isik[:ust.shape[0]] * ort - ort                    # ışık geçişi düzlenir; parçalar ortalamadan sapma olarak örülür
    pw, ph, kenar = 260, 110, 30; toplam = np.zeros((H, W, 3), np.float32); agirlik = np.zeros((H, W, 1), np.float32)
    ex = np.clip(np.minimum(np.arange(pw), pw - 1 - np.arange(pw)) / kenar, 0, 1); ey = np.clip(np.minimum(np.arange(ph), ph - 1 - np.arange(ph)) / kenar, 0, 1)
    maske = (np.outer(ey * ey * (3 - 2 * ey), ex * ex * (3 - 2 * ex)) + 1e-4)[..., None].astype(np.float32)
    for gy in range(-1, H // (ph - kenar) + 2):
        for gx in range(-1, W // (pw - kenar) + 2):
            x = gx * (pw - kenar) + int(rng.integers(-12, 12)); y = gy * (ph - kenar) + int(rng.integers(-10, 10)); sx = int(rng.integers(0, ust.shape[1] - pw + 1)); sy = int(rng.integers(0, ust.shape[0] - ph + 1))
            parca = ust[sy:sy + ph, sx:sx + pw]; parca = parca[:, ::-1] if rng.random() < 0.5 else parca
            x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + pw, W), min(y + ph, H)
            if x1 <= x0 or y1 <= y0: continue
            toplam[y0:y1, x0:x1] += parca[y0 - y:y1 - y, x0 - x:x1 - x] * maske[y0 - y:y1 - y, x0 - x:x1 - x]; agirlik[y0:y1, x0:x1] += maske[y0 - y:y1 - y, x0 - x:x1 - x] ** 2
    im = ort + toplam / np.sqrt(np.maximum(agirlik, 1e-8))               # üst üste binen yerlerde doku karşıtlığı korunur
    # tekerlek izi: geniş plandaki izin doğrultusunda, karenin alt kenarına kadar iki koyu şerit
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); a = np.array([W / 2 + (0.335 - 0.5) * w, H / 2 + 0.5 * h]); yon = np.array([-0.36 * 16, 0.45 * 9]); yon /= np.linalg.norm(yon); dik = np.array([-yon[1], yon[0]])
    boyunca = (xx - a[0]) * yon[0] + (yy - a[1]) * yon[1]; enine = (xx - a[0]) * dik[0] + (yy - a[1]) * dik[1]; pm = W / (GENIS['olcek'] * U['kat'])
    iz = sum(np.exp(-((enine - o * pm) / (0.16 * pm)) ** 2) for o in (-0.8, 0.8)) * np.clip(boyunca / 40 + 0.5, 0, 1); im *= (1 - 0.13 * iz)[..., None]
    # ortaya araçlı geniş plan
    arac = cv2.resize(ps.oku(os.path.join(HEDEF, 'arac-genis.jpg')), (w, h), interpolation=cv2.INTER_AREA) / isik * ort; x0, y0 = (W - w) // 2, (H - h) // 2      # aynı ışık düzeltmesi: kenarı belli olmaz
    kx = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / 70, 0, 1); ky = np.clip(np.minimum(np.arange(h), h - 1 - np.arange(h)) / 70, 0, 1); m = np.outer(ky * ky * (3 - 2 * ky), kx * kx * (3 - 2 * kx))[..., None]
    im[y0:y0 + h, x0:x0 + w] = im[y0:y0 + h, x0:x0 + w] * (1 - m) + arac * m
    ton = cv2.resize(rng.random((7, 12)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC) - 0.5; im *= (1 + 0.16 * ton)[..., None]; im += ton[..., None] * np.array([-0.012, 0.0, 0.012], np.float32)    # iri ton farkları: yer yer daha koyu ve daha sarı toprak
    yaz(os.path.join(HEDEF, 'arac-uzak.jpg'), im, 88)
    return {'kat': U['kat']}

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
    adim = sys.argv[1:] or ['arac', 'ufuk', 'dron', 'uzak']               # yalnızca bir adımı yenilemek için: python3 sim_arazi.py uzak
    yol = os.path.join(HEDEF, 'sahne.json'); S = json.load(open(yol)) if os.path.exists(yol) else {}
    if 'arac' in adim: S.update(arac())
    if 'ufuk' in adim: ufuklar()
    if 'dron' in adim: S['dron'] = dronlar()
    if 'uzak' in adim: S['arac_uzak'] = uzak()
    json.dump(S, open(yol, 'w'), indent=1); print({k: (v if k in ('dron', 'arac_uzak') else {a: v[a] for a in ('kule', 'kutu')}) for k, v in S.items() if k in ('arac', 'arac_genis', 'dron', 'arac_uzak')})
