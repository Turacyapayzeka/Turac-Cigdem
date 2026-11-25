"""Aracı stüdyo render'ının zemininden ayırır: alfa maskesi ve zemine düşen gölgenin haritası.

Girdi:  render/out/urunfilmi/pikap/plaka.png (pikap_studyo.py hazirla çıktısı; rötuşlu, 2 kat büyütülmüş)
Çıktı:  aynı klasörde arac-alfa.png (0–255) ve arac-golge.png (zemin parlaklığının fona oranı; 255 = gölgesiz)

Yöntem: fon, kenarlardan uydurulan düzgün bir yüzeydir. Renksiz, dokusuz ve yumuşak geçişli bölge kenarlardan
başlayarak fon sayılır; sınırın çevresindeki dar bantta her pikselin, dışarıdan tahmin edilen fon rengine uzaklığı
alfayı verir. Teker diplerinde ve yan basamağın altında koyulaşan gölge için bu adım birkaç kez yinelenir.
    python3 render/rotus/arac_maske.py
"""
import os, cv2, numpy as np
KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'); D = os.path.join(KOK, 'render', 'out', 'urunfilmi', 'pikap')
# zemin gölgesinin dik koyulaştığı bölgeler (kaynak pikseli, çokgen): arka teker dibi, ön teker dibi, yan basamağın altı
GOLGE = [[(600, 870), (935, 870), (935, 1015), (600, 1015)], [(1285, 425), (1425, 425), (1425, 575), (1285, 575)],
         [(872, 764), (1200, 515), (1300, 560), (1300, 650), (960, 850), (872, 812)]]
# teker diplerinde zemin gölgesinin araca yapışık kaldığı kutular (2 kat büyütülmüş pikselde x0, y0, x1, y1): arka teker, ön teker
TEKER = [(1420, 1560, 1880, 2010), (2420, 830, 2896, 1150)]

def maske(im):
    H, W = im.shape[:2]; f = im.astype(np.float32); lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32); L = lab[..., 0]; kroma = np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    gy, gx = np.mgrid[0:H, 0:W].astype(np.float32); gx /= W; gy /= H
    kenar = np.zeros((H, W), bool); kenar[:60] = True; kenar[-40:] = True; kenar[:, :60] = True; kenar[:, -40:] = True; kenar &= (L > 190) & (kroma < 8)
    A = np.stack([np.ones(kenar.sum()), gx[kenar], gy[kenar], gx[kenar] ** 2, gy[kenar] ** 2, gx[kenar] * gy[kenar]], 1); fon = np.zeros((H, W, 3), np.float32)
    for k in range(3):
        c, *_ = np.linalg.lstsq(A, f[..., k][kenar], rcond=None); fon[..., k] = c[0] + c[1] * gx + c[2] * gy + c[3] * gx ** 2 + c[4] * gy ** 2 + c[5] * gx * gy
    gri = f.mean(2); oran = gri / fon.mean(2); yerel = cv2.GaussianBlur(gri, (0, 0), 2.0); sapma = np.sqrt(np.maximum(cv2.GaussianBlur(gri ** 2, (0, 0), 2.0) - yerel ** 2, 0))
    gr = np.hypot(cv2.Sobel(yerel, cv2.CV_32F, 1, 0), cv2.Sobel(yerel, cv2.CV_32F, 0, 1))
    aday = cv2.morphologyEx(((kroma < 7) & (sapma < 2.2) & (gr < 5.5)).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    ff = aday * 255; m = np.zeros((H + 2, W + 2), np.uint8)
    for p in [(5, 5), (W - 6, 5), (5, H - 6), (W - 6, H - 6), (W // 2, 5), (5, H // 2), (W - 6, H // 2), (W // 2, H - 6)]:
        if ff[p[1], p[0]] == 255: cv2.floodFill(ff, m, p, 128)
    arka = ff == 128; alfa = (~arka).astype(np.float32)
    n, lb, st, _ = cv2.connectedComponentsWithStats((alfa > 0.5).astype(np.uint8)); alfa = (lb == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.float32)
    n, lb, st, _ = cv2.connectedComponentsWithStats((alfa < 0.5).astype(np.uint8)); alfa = (lb != lb[0, 0]).astype(np.float32)        # iç delikleri doldur
    bolge = np.zeros((H, W), np.uint8)
    for c in GOLGE: cv2.fillPoly(bolge, [np.array(c, np.int32) * 2], 1)
    bolge = bolge > 0
    for tur in range(8):
        dis = alfa < 0.5; w = cv2.GaussianBlur(dis.astype(np.float32), (0, 0), 9); tahmin = cv2.GaussianBlur(np.where(dis, oran, 0).astype(np.float32), (0, 0), 9) / np.maximum(w, 1e-4)      # dışarıdaki zeminin içeri doğru uzatılması
        fark = np.abs(f - fon * tahmin[..., None]).max(2); fark = cv2.GaussianBlur(fark, (0, 0), 0.8)
        bant = (cv2.dilate(dis.astype(np.uint8), np.ones((33, 33), np.uint8)) > 0) & ~dis
        if tur > 0: bant &= bolge                                                    # sonraki turlar yalnızca teker diplerinde
        yeni = np.clip((fark - 7.0) / 11.0, 0, 1); yeni = yeni * yeni * (3 - 2 * yeni)
        if tur > 0: yeni = np.where((kroma < 7) & (sapma < 6) & (L > 70), np.where(L > 150, 0.0, yeni), 1.0)      # gölge renksiz ve dokusuzdur; lastik değildir. Açık renkli olan zemindir
        alfa = np.where(bant, np.minimum(alfa, yeni), alfa)
    alfa = np.where(bolge & (kroma < 7) & (L > 165), 0.0, alfa)                        # gölge bölgelerinde kalan açık renkli, renksiz pikseller zemindir
    # yan basamak: siyah basamak yüzeyi ve hemen altındaki gümüş çıta araçtır; çıtanın altındaki koyu, renksiz zemin gölgesi araç değildir
    z = np.zeros((H, W), np.uint8); cv2.fillPoly(z, [np.array(GOLGE[2], np.int32) * 2], 1); z = z > 0
    basamak = cv2.morphologyEx((z & (L < 75)).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)) > 0; uzak = cv2.distanceTransform((~basamak).astype(np.uint8), cv2.DIST_L2, 5)
    cita = z & ~basamak & (uzak <= 22) & (L > 128); cita = cv2.morphologyEx(cita.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    aday = z & ~basamak & ~cita & (kroma < 7) & (L > 62); dis = alfa < 0.5
    n, lb = cv2.connectedComponents((aday | (dis & (cv2.dilate(z.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0))).astype(np.uint8), connectivity=4); disaridan = np.unique(lb[dis & (lb > 0)])
    alfa = np.where(aday & np.isin(lb, disaridan), 0.0, alfa); alfa = np.where(cita | (basamak & z), 1.0, alfa)
    # teker diplerinde kalan zemin gölgesi: lastikten belirgin açık (L > 118), renksiz ve dışarıdaki zemine bitişik pikseller
    for x0, y0, x1, y1 in TEKER:
        zz = np.zeros((H, W), bool); zz[y0:y1, x0:x1] = True; aday = zz & ~cita & ~basamak & (kroma < 7) & (L > 118); dis = alfa < 0.5; cevre = cv2.dilate(zz.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        n, lb = cv2.connectedComponents((aday | (dis & cevre)).astype(np.uint8), connectivity=4); disaridan = np.unique(lb[dis & cevre & (lb > 0)]); alfa = np.where(aday & np.isin(lb, disaridan), 0.0, alfa)
    # teker diplerinde gövdenin renksiz, düz panellerinde açılan delikler kapatılır
    for c in GOLGE[:2]:
        zz = np.zeros((H, W), np.uint8); cv2.fillPoly(zz, [np.array(c, np.int32) * 2], 1); kapali = cv2.morphologyEx((alfa > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8)); alfa = np.where((zz > 0) & (kapali > 0), np.maximum(alfa, 1.0), alfa)
    n, lb, st, _ = cv2.connectedComponentsWithStats((alfa < 0.5).astype(np.uint8)); alfa = np.where((lb != lb[0, 0]) & (alfa < 0.5), 1.0, alfa)
    n, lb, st, _ = cv2.connectedComponentsWithStats((alfa > 0.5).astype(np.uint8)); ana = lb == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); alfa = np.where(cv2.dilate(ana.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0, alfa, 0)
    alfa = cv2.GaussianBlur(cv2.erode(alfa, np.ones((3, 3), np.uint8)), (0, 0), 0.9)
    # gölge haritası: araç dışındaki zeminin fona oranı. Aracın kenarındaki dar halka (keskinleştirme izi, çıta parlaması) ölçüme katılmaz;
    # değerler halkanın dışından aracın altına doğru yumuşakça uzatılır. Tekerin ve gövdenin dibindeki koyu temas gölgesi arazide ayrıca üretilir
    gecerli = cv2.dilate((alfa > 0.05).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (57, 57))) == 0; o = np.clip(oran, 0, 1.0).astype(np.float32)
    w = cv2.GaussianBlur(gecerli.astype(np.float32), (0, 0), 18); uzat = cv2.GaussianBlur(np.where(gecerli, o, 0).astype(np.float32), (0, 0), 18) / np.maximum(w, 1e-4)
    w2 = cv2.GaussianBlur(gecerli.astype(np.float32), (0, 0), 60); uzat2 = cv2.GaussianBlur(np.where(gecerli, o, 0).astype(np.float32), (0, 0), 60) / np.maximum(w2, 1e-4); uzat = np.where(w > 0.02, uzat, uzat2)
    d = cv2.distanceTransform((alfa <= 0.05).astype(np.uint8), cv2.DIST_L2, 5); g = np.clip((d - 28) / 60, 0, 1); g = g * g * (3 - 2 * g)        # halkanın dışında ölçülen değere yumuşak geçiş
    golge = cv2.GaussianBlur((np.clip(uzat, 0, 1) * (1 - g) + o * g).astype(np.float32), (0, 0), 3.0)
    return alfa, golge

if __name__ == '__main__':
    im = cv2.imread(os.path.join(D, 'plaka.png')); alfa, golge = maske(im)
    cv2.imwrite(os.path.join(D, 'arac-alfa.png'), (alfa * 255).round().astype(np.uint8)); cv2.imwrite(os.path.join(D, 'arac-golge.png'), (golge * 255).round().astype(np.uint8))
    print('alfa ortalaması', round(float(alfa.mean()), 3), '| en koyu gölge', round(float(golge.min()), 2))
