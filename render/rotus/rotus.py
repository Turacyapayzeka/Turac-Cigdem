"""Fotoğraf plakalarından başka firmalara ait işaretleri ve araç plakasını siler.

    python3 render/rotus/rotus.py            # animasyon/assets altındaki plakaları yerinde günceller

Kural (PROJE-OZETI.md, "Kurallar"): başka firma logosu, bayrağı ve araç plakası kadraja girmez.
Sterling ve Dron Kalkanı işaretleri Turaç'ın kendi markası olduğu için kalır.
Gerekenler: opencv-python-headless, numpy. Betik aynı dosyada ikinci kez çalıştırılırsa sonucu değiştirmez sayılır
(maskeler zaten temizlenmiş bölgeyi yeniden doldurur).
"""
import os, sys
import numpy as np, cv2

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'animasyon', 'assets')
rng = np.random.default_rng(3)

def doldur(img, mask, r=7):
    """Maskeyi çevresinden doldurur, sonra çevrenin kumlanmasına uyan hafif gren ekler (düz leke görünmesin)."""
    out = cv2.inpaint(img, mask, r, cv2.INPAINT_TELEA)
    halka = cv2.dilate(mask, np.ones((25, 25), np.uint8)) & ~mask
    gri = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    ince = gri - cv2.GaussianBlur(gri, (0, 0), 2.0)
    s = float(np.std(ince[halka > 0])) if np.any(halka) else 2.0
    gren = cv2.GaussianBlur(rng.standard_normal(gri.shape).astype(np.float32), (0, 0), 0.6) * s * 0.55
    yum = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 1.5)[..., None]
    return np.clip(out.astype(np.float32) + gren[..., None] * yum, 0, 255).astype(np.uint8)

def elips(mask, c, rad): cv2.ellipse(mask, c, rad, 0, 0, 360, 255, -1)
def cokgen(mask, pts): cv2.fillPoly(mask, [np.array(pts, np.int32)], 255)

def arka(ad):
    """Aracın arka çapraz görünüşü (1500×2000): VW amblemi, AMAROK kabartması, Kaiser logosu, plaka karakterleri."""
    yol = os.path.join(KOK, ad); img = cv2.imread(yol)
    m = np.zeros(img.shape[:2], np.uint8)
    elips(m, (1400, 1158), (19, 44))                                              # VW amblemi
    cokgen(m, [(1314, 1218), (1447, 1186), (1447, 1236), (1314, 1264)])           # AMAROK
    cokgen(m, [(1279, 1239), (1335, 1239), (1335, 1349), (1279, 1349)])           # Kaiser
    img = doldur(img, m, 9)
    # plaka: beyaz zemin kalır, karakterler ve mavi bant silinir (boş plaka)
    p = np.zeros(img.shape[:2], np.uint8); cokgen(p, [(1323, 1334), (1397, 1298), (1397, 1344), (1325, 1364)])
    gri = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); b, g, r_ = cv2.split(img)
    koyu = ((gri < 150) | (b.astype(int) - r_.astype(int) > 25)).astype(np.uint8) * 255
    k = cv2.dilate(koyu & p, np.ones((3, 3), np.uint8)) & p
    acik = img[(p > 0) & (k == 0)]
    if len(acik) > 20:
        renk = np.median(acik, axis=0); ic = cv2.erode(p, np.ones((3, 3), np.uint8))
        duz = img.copy(); duz[ic > 0] = renk
        yum = cv2.GaussianBlur((ic > 0).astype(np.float32), (0, 0), 1.0)[..., None]
        golge = cv2.GaussianBlur(img, (0, 0), 6).astype(np.float32); golge = golge / (np.mean(golge[ic > 0], axis=0) + 1e-6)   # plakanın kendi ışık geçişi
        img = np.clip(img * (1 - yum) + (duz.astype(np.float32) * np.clip(golge, 0.85, 1.12)) * yum, 0, 255).astype(np.uint8)
    cv2.imwrite(yol, img, [cv2.IMWRITE_JPEG_QUALITY, 93]); print('temizlendi', ad)

def yan(ad):
    """Aracın yan görünüşü (2400×1800): kasa direğindeki yuvarlak amblem."""
    yol = os.path.join(KOK, ad); img = cv2.imread(yol)
    m = np.zeros(img.shape[:2], np.uint8); elips(m, (1547, 920), (22, 22))
    cv2.imwrite(yol, doldur(img, m, 7), [cv2.IMWRITE_JPEG_QUALITY, 93]); print('temizlendi', ad)

if __name__ == '__main__':
    for ad in ('amarok-arka-taret.jpg', 'amarok-arka-taret-clean.jpg'): arka(ad)
    for ad in ('amarok-yan-clean.jpg', 'amarok-yan.jpg'): yan(ad)
