"""3B simülasyon filmi: arazi sahnesinin ufuk görüntüsü (sensör kamerasının ve açılış çekiminin arka planı).

Kule uzaktaki drona çok dar açılı bir mercekle bakar; arka plan bu yüzden puslu ve yumuşaktır. Görüntü katman katman
üretilir: kapalı gök, pus içinde iki dağ sırası, yakın tepeler, bozkır düzlüğü; üstüne çalı kümeleri ve tarla izleri.
Blender'daki arazi sahnesi bu uzaklıkta ayrıntısız kaldığı için ufuk görüntüsü burada, iki boyutlu olarak kurulur.

Çıktı: render/out/simulasyon/arazi/ufuk.jpg (1920×1080)
    python3 render/rotus/sim_ufuk.py
"""
import os, sys
import cv2, numpy as np

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'); CIKTI = os.path.join(KOK, 'render', 'out', 'simulasyon', 'arazi', 'ufuk.jpg')
K = 2; W, H = 1920 * K, 1080 * K                                     # iki kat büyük üretilir, sonda küçültülür

def gurultu(h, w, ox, oy, oktav=5, tohum=0, kazanc=0.5):
    """Kesirli gürültü (0–1): rastgele ızgaralar yumuşakça büyütülüp üst üste toplanır. ox, oy: en iri ayrıntının piksel boyu."""
    rng = np.random.default_rng(tohum); t = np.zeros((h, w), np.float32); a = 1.0; top = 0.0
    for o in range(oktav):
        gx = max(2, int(np.ceil(w / (ox / 2 ** o))) + 3); gy = max(2, int(np.ceil(h / (oy / 2 ** o))) + 3)
        t += a * cv2.resize(rng.random((gy, gx)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC); top += a; a *= kazanc
    return t / top

def sirt(taban, genlik, olcek, tohum, oktav=6):
    """Bir dağ ya da tepe sırasının üst çizgisi (her sütun için y)."""
    return taban * K - genlik * K * (gurultu(1, W, olcek * K, 1, oktav, tohum, 0.52)[0] - 0.5) * 2

def renk(r, g, b): return np.array([b, g, r], np.float32)            # OpenCV sırası

def uret():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); v = yy / H
    # ---- gök: tepede gri mavi, ufka doğru açılan kapalı hava; iri ve ince bulut dokusu
    ust, alt = renk(150, 160, 172), renk(214, 217, 216); g = np.clip(v / 0.62, 0, 1) ** 0.8; im = ust * (1 - g[..., None]) + alt * g[..., None]
    b1 = gurultu(H, W, 1500 * K, 300 * K, 5, 11) - 0.5; b2 = gurultu(H, W, 420 * K, 110 * K, 5, 12) - 0.5; b3 = gurultu(H, W, 120 * K, 40 * K, 4, 13) - 0.5
    bulut = (b1 * 1.0 + b2 * 0.55 + b3 * 0.2) * (1.0 - 0.55 * g); im += bulut[..., None] * renk(62, 58, 52)
    # ---- katmanlar: uzaktan yakına. (üst çizgi, renk, doku şiddeti, doku ölçeği, çalı yoğunluğu, çalı boyu)
    pus = renk(205, 209, 210)
    katman = [(sirt(585, 40, 760, 21), renk(183, 190, 197), 5, 220, 0, 0), (sirt(628, 34, 430, 22), renk(164, 172, 177), 9, 160, 0, 0),
              (sirt(676, 26, 560, 23), renk(148, 152, 146), 13, 130, 0.9, 0.55), (sirt(742, 22, 900, 24), renk(156, 150, 134), 17, 110, 1.8, 0.85),
              (sirt(826, 9, 1500, 25), renk(170, 162, 143), 20, 90, 3.0, 1.25)]
    rng = np.random.default_rng(5)
    for i, (ys, c, sid, olc, yog, boy) in enumerate(katman):
        m = np.clip((yy - ys[None, :]) / (1.5 * K) + 0.5, 0, 1)[..., None]; alt_y = katman[i + 1][0] if i + 1 < len(katman) else np.full(W, H, np.float32)
        d = np.clip((yy - ys[None, :]) / np.maximum(alt_y[None, :] - ys[None, :], 1), 0, 1)                  # katman içinde yukarıdan aşağı 0–1
        dk = gurultu(H, W, olc * 3.2 * K, olc * K, 5, 40 + i) - 0.5; ince = gurultu(H, W, olc * 0.9 * K, olc * 0.22 * K, 4, 60 + i) - 0.5
        egim = dk - np.roll(np.roll(dk, 5 * K, 1), 3 * K, 0)                                                 # yamaçların ışık alan ve almayan yüzleri
        tane = gurultu(H, W, 26 * K, 5 * K, 3, 70 + i) - 0.5                                                   # ot ve toprak dokusu: ince, yatay uzamış
        kat = c + (dk * 1.3 + ince * 0.8 + egim * 5.0 + tane * (0.5 if yog > 0 else 0.15))[..., None] * sid * renk(1.0, 0.97, 0.86) + (d[..., None] - 0.4) * renk(-7, -7, -9)
        if yog > 0:                                                                                          # bozkır: daha yeşil ve daha sarı yamalar
            yama = gurultu(H, W, 900 * K, 120 * K, 4, 80 + i) - 0.5; kat += yama[..., None] * renk(-16, -6, -26) * 1.3
            cali = np.zeros((H, W), np.float32); n = int(5200 * yog); yogunluk = gurultu(H, W, 420 * K, 70 * K, 5, 90 + i)
            for _ in range(n * 3):
                x = int(rng.integers(0, W)); yb = float(ys[x]); ya = float(alt_y[x]); y = int(yb + (ya - yb) * rng.random() ** 0.8)
                if y >= H or rng.random() > (yogunluk[min(y, H - 1), x] - 0.42) * 4.2: continue
                t = (y - yb) / max(ya - yb, 1); r = boy * K * (0.6 + 1.5 * t) * (0.5 + 1.0 * rng.random() ** 2)
                cv2.ellipse(cali, (x, y), (max(1, int(round(r * 1.9))), max(1, int(round(r)))), 0, 0, 360, float(0.45 + 0.55 * rng.random()), -1, cv2.LINE_AA)
            cali = np.clip(cv2.GaussianBlur(cali, (0, 0), 0.45 * K), 0, 1); kat = kat * (1 - 0.7 * cali[..., None]) + renk(82, 86, 70) * 0.7 * cali[..., None]
        im = im * (1 - m) + kat * m
    # ---- düzlükte tarla sınırları ve toprak yol: ufka doğru sıklaşan yatay izler
    duz = katman[-1][0]; iz = np.zeros((H, W), np.float32)
    for k in range(9):
        y0 = 840 + 240 * (k / 8.0) ** 1.7; egim = (rng.random() - 0.5) * 0.03; ys = (y0 * K + (xx[0] - W / 2) * egim + 8 * K * (gurultu(1, W, 700 * K, 1, 4, 120 + k)[0] - 0.5)).astype(np.float32)
        kalin = (0.8 + 2.4 * (k / 8.0)) * K; iz += np.exp(-((yy - ys[None, :]) / kalin) ** 2) * (0.35 + 0.4 * rng.random()) * (1 if k % 3 else -0.8)
    im -= np.clip(iz, -1, 1)[..., None] * renk(15, 14, 12) * (yy > duz[None, :])[..., None]
    # ---- pus: ufuk çizgisinin çevresinde açık renkli bant; yakına indikçe azalır
    ufuk = 640 * K; bant = np.exp(-((yy - ufuk) / (95 * K)) ** 2) * 0.34 + np.clip(1 - (yy - ufuk) / (330 * K), 0, 1) * (yy > ufuk) * 0.16
    im = im * (1 - bant[..., None]) + pus * bant[..., None]
    # ---- mercek: uzak katmanlar net, yakın zemin hafif odak dışı
    im = np.clip(im, 0, 255); keskin = cv2.GaussianBlur(im, (0, 0), 0.7 * K); yumusak = cv2.GaussianBlur(im, (0, 0), 2.0 * K); a = np.clip((v - 0.8) / 0.2, 0, 1)[..., None]
    im = keskin * (1 - a) + yumusak * a
    return cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA)

if __name__ == '__main__':
    cikti = sys.argv[1] if len(sys.argv) > 1 else CIKTI; os.makedirs(os.path.dirname(cikti), exist_ok=True)
    cv2.imwrite(cikti, np.clip(uret(), 0, 255).round().astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94]); print('->', cikti)
