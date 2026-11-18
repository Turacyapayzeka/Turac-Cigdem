"""Ürün filminin pikap çekimi: aracın stüdyo render'ı (docs/kaynak-gorseller/amarok-ust-render.jpg) + kasaya yerleştirilen 3B kule.

Adımlar:
    hazirla   Render'dan başka firma işaretlerini ve plaka yazısını temizler, 2 kat büyütür, kamerayı çözer.
              Çıktı: plaka.png (temiz, büyütülmüş araç görüntüsü), kamera.json
    birlestir Blender'ın ürettiği kule katmanlarını (kule-tam.png, kule-ust.png) araç görüntüsüne bindirir,
              kadrajı 16:9'a tamamlar. Çıktı: pikap.jpg, pikap.json

Kamera: render'ın geometrisi ölçülü değildir (yapay üretim), bu yüzden kasa çevresinde paralel izdüşümle eşlenir:
kasa ağzının dört köşesi görüntüde işaretlenir; boy ve en yönlerinin piksel karşılıkları buradan, düşey yön
dik izdüşüm koşulundan bulunur.

    python3 render/rotus/pikap_studyo.py hazirla   --cikti render/out/urunfilmi/pikap [--model EDSR_x2.pb]
    python3 render/rotus/pikap_studyo.py birlestir --cikti render/out/urunfilmi/pikap
"""
import sys, os, json
import cv2, numpy as np

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
KAYNAK = os.path.join(KOK, 'docs', 'kaynak-gorseller', 'amarok-ust-render.jpg')
K = 2                                                    # büyütme katı
# kasa ağzının köşeleri (kenar kapaklarının iç üst kenarı), kaynak pikselinde: arka sol, arka sağ, ön sağ, ön sol
AGIZ = [(213, 541), (536, 722), (795, 553), (500, 372)]
KASA_BOY, KASA_EN, KENAR_Z, TABAN_Z = 1.66, 1.58, 1.39, 0.86   # kasa ağzı ölçüleri (m), kenar ve taban yükseklikleri
KASA_ORTA = (-1.86, 0.0, KENAR_Z)                        # kasa ağzının ortası (araç koordinatı: x ileri, y sola, z yukarı)
UST, ALT, YAN = 70, 50, 348                              # 16:9 için eklenen kenar payları (kaynak pikseli)

def arg(ad, varsayilan=None):
    return sys.argv[sys.argv.index('--' + ad) + 1] if '--' + ad in sys.argv else varsayilan

def kamera_coz():
    """Paralel izdüşüm: p = p0 + A (X − X0). A'nın sütunları boy, en ve düşey yönün piksel karşılıklarıdır."""
    al, ar, onr, onl = [np.array(p, float) for p in AGIZ]
    ex = ((onl - al) + (onr - ar)) / 2 / KASA_BOY                      # x: arkadan öne
    ey = -((ar - al) + (onr - onl)) / 2 / KASA_EN                      # y: sağdan sola
    M = np.outer(ex, ex) + np.outer(ey, ey); w, v = np.linalg.eigh(M)  # dik izdüşüm: ex exᵀ + ey eyᵀ + ez ezᵀ = s² I
    s = float(np.sqrt(w[1])); ez = np.sqrt(w[1] - w[0]) * v[:, 0]
    if ez[1] > 0: ez = -ez                                             # yukarı yön görüntüde yukarı bakar
    A = np.stack([ex, ey, ez], 1); sag = A[0] / s; asagi = A[1] / s; ileri = np.cross(sag, asagi)
    p0 = np.mean([al, ar, onr, onl], 0)
    return {'A': A.tolist(), 'p0': p0.tolist(), 'X0': list(KASA_ORTA), 's': s, 'sag': sag.tolist(), 'asagi': asagi.tolist(), 'ileri': ileri.tolist(),
            'W': 1448, 'H': 1086, 'kat': K, 'agiz': AGIZ, 'kenar_z': KENAR_Z, 'taban_z': TABAN_Z, 'kasa_boy': KASA_BOY, 'kasa_en': KASA_EN}

def izdus(kam, X):
    return np.array(kam['p0']) + (np.asarray(X, float) - np.array(kam['X0'])) @ np.array(kam['A']).T

def klonla(im, cokgen, kayma):
    """Çokgenin içini, kayma kadar ötedeki dokuyla doldurur (Poisson harmanı): kamuflaj üstündeki amblem için."""
    m = np.zeros(im.shape[:2], np.uint8); cv2.fillPoly(m, [(np.array(cokgen) * K).astype(np.int32)], 255); m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    x, y, w, h = cv2.boundingRect(m); kaynak = np.roll(im, (-kayma[1] * K, -kayma[0] * K), (0, 1))
    return cv2.seamlessClone(kaynak[y:y + h, x:x + w], im, m[y:y + h, x:x + w], (x + w // 2, y + h // 2), cv2.NORMAL_CLONE)

def yazi_sil(im, cokgen, esik, cevre_esik=None, genis=3):
    """Çokgenin içindeki açık renkli yazıyı siler: koyu zemin üstündeki ince işaretler çevresinden doldurulur."""
    gri = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY); alan = np.zeros(gri.shape, np.uint8); cv2.fillPoly(alan, [(np.array(cokgen) * K).astype(np.int32)], 255)
    m = (gri > esik) & (alan > 0)
    if cevre_esik is not None: m &= cv2.medianBlur(gri, 31 * K + 1) < cevre_esik
    m = cv2.dilate(m.astype(np.uint8) * 255, np.ones((genis * K, genis * K), np.uint8)); return cv2.inpaint(im, m, 4 * K, cv2.INPAINT_TELEA)

def rotus(im):
    """Başka firma işaretleri ve plaka yazısı (K kat büyütülmüş görüntüde; koordinatlar kaynak pikselidir). Sterling işaretleri kalır."""
    cember = lambda cx, cy, r: [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 24, endpoint=False)]
    def bant(a, b, g):
        a, b = np.array(a, float), np.array(b, float); t = (b - a) / np.linalg.norm(b - a); n = np.array([-t[1], t[0]]) * g; return [a - n, b - n, b + n, a + n]
    im = yazi_sil(im, bant((286, 707), (409, 788), 13), 100)                          # arka kapak yazısı
    im = yazi_sil(im, [(198, 632), (258, 632), (258, 704), (198, 704)], 105)           # sol alttaki firma işareti
    im = klonla(im, cember(343, 702, 27), (74, 40))                                    # arka kapak amblemi
    im = klonla(im, cember(846, 489, 13), (0, 30))                                     # yelken panelindeki küçük amblem
    # plaka: yazı ve renkli bant yerine boş beyaz plaka
    rnd = np.random.default_rng(3); ic = (np.array([(276, 739), (416, 822), (416, 850), (278, 779)]) * K).astype(np.int32); pl = np.zeros(im.shape[:2], np.uint8); cv2.fillPoly(pl, [ic], 255, cv2.LINE_AA)
    xx = np.tile(np.arange(im.shape[1], dtype=np.float32) / K, (im.shape[0], 1)); beyaz = (226 + 10 * np.clip((xx - 282) / 134, 0, 1))[..., None] + rnd.normal(0, 1.2, im.shape[:2] + (1,))
    a = (cv2.GaussianBlur(pl, (0, 0), 0.6).astype(np.float32) / 255)[..., None]; im = (im * (1 - a) + np.clip(beyaz, 0, 255) * a).astype(np.uint8)
    # lastik ve jant göbeği yazıları
    for x0, y0, x1, y1 in ((655, 715, 905, 985), (1185, 330, 1360, 545)): im = yazi_sil(im, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 105, 62, genis=5)
    return im

def hazirla(cikti):
    """Kaynağı bir kez büyütür (sonuç saklanır), rötuşu büyütülmüş görüntüde yapar."""
    ham = os.path.join(cikti, 'kaynak-%dx.png' % K); model = arg('model')
    if not os.path.exists(ham):
        im = cv2.imread(KAYNAK)
        if model and hasattr(cv2, 'dnn_superres'):
            sr = cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(model); sr.setModel('edsr', K); buyuk = sr.upsample(im)
        else: buyuk = cv2.resize(im, None, fx=K, fy=K, interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(ham, buyuk)
    buyuk = rotus(cv2.imread(ham)); cv2.imwrite(os.path.join(cikti, 'plaka.png'), buyuk); kam = kamera_coz(); json.dump(kam, open(os.path.join(cikti, 'kamera.json'), 'w'), indent=1)
    print('ölçek', round(kam['s'], 1), 'piksel/m; yükseklik açısı', round(float(np.degrees(np.arcsin(-kam['ileri'][2]))), 1), 'derece; plaka', buyuk.shape)

def bindir(alt, kat, maske=None):
    """Saydam katmanı alttaki görüntüye bindirir; maske verilirse yalnızca onun içinde."""
    on = np.dstack([kat[..., :3] * kat[..., 3:4], kat[..., 3:4]]); on = cv2.GaussianBlur(on, (0, 0), 0.7)      # PNG düz alfa taşır: önce alfa ile çarp
    m = maske[..., None] if maske is not None else 1.0; return alt * (1 - on[..., 3:4] * m) + on[..., :3] * m

def agiz_maskesi(kam, H, W):
    m = np.zeros((H, W), np.float32); cv2.fillPoly(m, [(np.array(kam['agiz'], np.float64) * K).astype(np.int32)], 1.0); return cv2.GaussianBlur(m, (0, 0), 1.5)

def cercevele(sonuc):
    """Kadrajı 16:9'a tamamlar (kenarlardaki fon uzatılır ve yumuşatılır), kenarları karartır, 3840×2160'a getirir."""
    H, W = sonuc.shape[:2]; u, a, y = UST * K, ALT * K, YAN * K; genis = cv2.copyMakeBorder(sonuc, u, a, y, y, cv2.BORDER_REPLICATE)
    yumusak = cv2.GaussianBlur(genis, (0, 0), 40); fon = np.median(sonuc[:40 * K].reshape(-1, 3), 0)
    xx = np.arange(genis.shape[1], dtype=np.float32); uzak = np.clip(np.maximum(y - xx, xx - (y + W - 1)) / y, 0, 1)[None, :, None]; yy = np.arange(genis.shape[0], dtype=np.float32); uzak_y = np.clip(np.maximum(u - yy, yy - (u + H - 1)) / max(u, a), 0, 1)[:, None, None]
    dis = np.maximum(uzak, uzak_y); kenar = (dis > 0).astype(np.float32); karisim = yumusak * (1 - dis ** 0.7) + fon * dis ** 0.7; genis = genis * (1 - kenar) + karisim * kenar
    hh, ww = genis.shape[:2]; gy, gx = np.mgrid[0:hh, 0:ww].astype(np.float32); r = np.sqrt(((gx - ww * 0.48) / (ww * 0.5)) ** 2 + ((gy - hh * 0.5) / (hh * 0.95)) ** 2)
    genis *= (1 - 0.62 * np.clip((r - 0.42) / 0.58, 0, 1) ** 1.3)[..., None]
    return cv2.resize(np.clip(genis, 0, 1), (3840, 2160), interpolation=cv2.INTER_AREA)

def oran(kam, X):
    """Araç koordinatındaki noktanın 16:9 kadrajdaki yeri (0–1)."""
    p = izdus(kam, X); return [round(float((p[0] + YAN) / (kam['W'] + 2 * YAN)), 5), round(float((p[1] + UST) / (kam['H'] + UST + ALT)), 5)]

def oku(yol): return cv2.imread(yol, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255

def birlestir(cikti):
    kam = json.load(open(os.path.join(cikti, 'kamera.json'))); pl = oku(os.path.join(cikti, 'plaka.png')); H, W = pl.shape[:2]
    sonuc = bindir(pl, oku(os.path.join(cikti, 'kule-tam.png')), agiz_maskesi(kam, H, W)); sonuc = bindir(sonuc, oku(os.path.join(cikti, 'kule-ust.png')))   # kenarın altı yalnızca kasa ağzından görünür; üstü her yerde
    cv2.imwrite(os.path.join(cikti, 'pikap.jpg'), (cercevele(sonuc) * 255).round().astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
    json.dump({'ad': 'pikap', 'en': 3840, 'boy': 2160, 'capa': {'kule': oran(kam, (-1.86, 0, TABAN_Z + 1.17)), 'taban': oran(kam, (-1.86, 0, TABAN_Z + 0.95))}}, open(os.path.join(cikti, 'pikap.json'), 'w'), indent=1)
    print('->', os.path.join(cikti, 'pikap.jpg'))

if __name__ == '__main__':
    cikti = arg('cikti', os.path.join(KOK, 'render', 'out', 'urunfilmi', 'pikap')); os.makedirs(cikti, exist_ok=True)
    {'hazirla': hazirla, 'birlestir': birlestir}[sys.argv[1]](cikti)
