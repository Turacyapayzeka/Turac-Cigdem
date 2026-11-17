"""Ürün filmi için temiz pikap plakası: fotoğraftaki kulenin kalıntılarını (namlu izi, kablolar, taban parçaları) siler.

    python3 render/rotus/pikap_plaka.py     # animasyon/assets/amarok-arka-taret-clean.jpg -> urunfilmi/assets/pikap-plaka.jpg

Filmdeki plaka, kule kesmesinin altında kalan artıkları gizlemiyordu; 3B kule bindirilecek plakada gökyüzü temiz,
tripod başlığının üstü boş olmalı. Gökyüzü, bölgenin sol ve sağ kenarındaki gerçek gökyüzünden satır satır
aradeğerlenir (üst kenardaki bulut dokusu aşağı doğru sönerek taşınır); böylece koyu tripod rengi yukarı bulaşmaz.
Tripod ve araç fotoğraftaki gibi kalır.
"""
import os
import numpy as np, cv2

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
img = cv2.imread(os.path.join(KOK, 'animasyon', 'assets', 'amarok-arka-taret-clean.jpg')).astype(np.float32)
X0, X1, Y0, Y1, XS, YS = 800, 1300, 590, 812, 1205, 804            # bölge; XS'nin sağında alt sınır YS (tepeler başlıyor)
rng = np.random.default_rng(5)

sol = cv2.GaussianBlur(img[:, X0 - 22:X0 - 2].mean(axis=1, keepdims=True), (1, 31), 0)[:, 0]      # satır başına sol kenar rengi
sag = cv2.GaussianBlur(img[:, X1 + 2:X1 + 22].mean(axis=1, keepdims=True), (1, 31), 0)[:, 0]      # satır başına sağ kenar rengi
ust = img[Y0 - 8:Y0 - 1].mean(axis=0)                                                              # üst kenardaki bulut dokusu
u = ((np.arange(X0, X1) - X0) / (X1 - X0))[None, :, None]
dolgu = np.empty((Y1 - Y0, X1 - X0, 3), np.float32)
for y in range(Y0, Y1):
    s, g = sol[y], (sag[y] if y < YS else sag[YS - 1] + (sol[y] - sol[YS - 1]))
    dolgu[y - Y0] = (s[None, :] * (1 - u[0]) + g[None, :] * u[0])
ustfark = ust[X0:X1] - (sol[Y0][None, :] * (1 - u[0]) + sag[Y0][None, :] * u[0])                   # üst kenar ile düz dolgunun farkı
v = ((np.arange(Y0, Y1) - Y0) / (Y1 - Y0))[:, None, None]
dolgu += ustfark[None, :, :] * (1 - v) ** 2
# çevredeki gökyüzünün kumlanması
gri = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32); ince = gri - cv2.GaussianBlur(gri, (0, 0), 2.0)
sigma = float(np.std(ince[Y0 - 60:Y0 - 5, X0:X1]))
dolgu += (cv2.GaussianBlur(rng.standard_normal(dolgu.shape[:2]).astype(np.float32), (0, 0), 0.7) * sigma * 1.5)[..., None]

m = np.zeros(img.shape[:2], np.float32); m[Y0:Y1, X0:XS] = 1; m[Y0:YS, XS:X1] = 1
yum = cv2.GaussianBlur(m, (0, 0), 3.0); yum[Y1:, :] = 0; yum[YS:, XS:] = 0                         # kenarlar yumuşak, alt sınır (tripod, tepe) keskin
tam = img.copy(); tam[Y0:Y1, X0:X1] = dolgu
out = img * (1 - yum[..., None]) + tam * yum[..., None]
# tepelerin önünde kalan kablo halkaları: ince olduğu için çevresinden doldurmak yeter
o8 = np.clip(out, 0, 255).astype(np.uint8); g8 = cv2.cvtColor(o8, cv2.COLOR_BGR2GRAY); kablo = np.zeros(g8.shape, np.uint8)
kablo[YS - 4:860, 1183:1298] = (g8[YS - 4:860, 1183:1298] < 78).astype(np.uint8) * 255
o8 = cv2.inpaint(o8, cv2.dilate(kablo, np.ones((5, 5), np.uint8)), 4, cv2.INPAINT_TELEA)
os.makedirs(os.path.join(KOK, 'urunfilmi', 'assets'), exist_ok=True)
cv2.imwrite(os.path.join(KOK, 'urunfilmi', 'assets', 'pikap-plaka.jpg'), o8, [cv2.IMWRITE_JPEG_QUALITY, 94]); print('yazıldı urunfilmi/assets/pikap-plaka.jpg')
