"""3B simülasyon filmi: kulenin hedefe döndüğü kareleri birleştirir ve kurgu sayfasının klasörüne yazar.

Blender tarafı (render/3d/simfilm.py kareler) her platform için poz katmanlarını üretir; bu betik onları
arka plana bindirir. Poz 0 (bekleme) tam kare olarak, öbür pozlar yalnızca kulenin çevresi olarak saklanır.

    python3 render/rotus/sim_kareler.py arac|gemi|tesis [...]

Çıktı: simulasyon/assets/<platform>.jpg, simulasyon/assets/kare/<platform>/pNN.jpg, simulasyon/assets/sahne.json (güncellenir)
"""
import sys, os, json
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pikap_studyo as ps

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'); HEDEF = os.path.join(KOK, 'simulasyon', 'assets')

def yon_vektoru(a, b):
    v = (np.array(b) - np.array(a)) * np.array([16, 9]); v /= np.linalg.norm(v); return [round(float(v[0]), 4), round(float(v[1]), 4)]

def platform(ad):
    d = os.path.join(KOK, 'render', 'out', 'simulasyon', ad); P = json.load(open(os.path.join(d, 'poz.json'))); os.makedirs(os.path.join(HEDEF, 'kare', ad), exist_ok=True)
    if ad == 'arac':
        pd = os.path.join(KOK, 'render', 'out', 'urunfilmi', 'pikap'); kam = json.load(open(os.path.join(pd, 'kamera.json'))); pl = ps.oku(os.path.join(pd, 'plaka.png')); H, W = pl.shape[:2]
        taban = ps.bindir(pl, ps.oku(os.path.join(d, 'kule-sabit.png')), ps.agiz_maskesi(kam, H, W))
        kare = lambda i: ps.cercevele(ps.bindir(taban, ps.oku(os.path.join(d, 'poz', f'p{i:02d}.png'))))
        k = P['kutu']; G, Y = kam['W'] + 2 * ps.YAN, kam['H'] + ps.UST + ps.ALT
        kutu = [(k[0] * kam['W'] + ps.YAN) / G, (k[1] * kam['H'] + ps.UST) / Y, (k[2] * kam['W'] + ps.YAN) / G, (k[3] * kam['H'] + ps.UST) / Y]
        uc = [ps.oran(kam, u) for u in P['uc']]; bilgi = {'kule': ps.oran(kam, P['kule']), 'namlu': uc, 'ates': yon_vektoru(uc[0], ps.oran(kam, np.array(P['uc'][0]) + np.array(P['yon'])))}
    else:
        bos = ps.oku(os.path.join(d, 'bos.jpg'))
        def kare(i):
            return ps.bindir(bos, ps.oku(os.path.join(d, 'poz', f'p{i:02d}.png')))
        kutu = P['kutu']; bilgi = {'kule': P['px']['kule'], 'namlu': P['px']['namlu'], 'ates': yon_vektoru(P['px']['namlu'][0], P['px']['ileri'])}
    var = [i for i in range(P['poz']) if os.path.exists(os.path.join(d, 'poz', f'p{i:02d}.png'))]      # render edilmeyen pozun yerine en yakın önceki poz kullanılır
    for i in range(P['poz']):
        im = kare(max(v for v in var if v <= i)); h, w = im.shape[:2]
        if i == 0: cv2.imwrite(os.path.join(HEDEF, ad + '.jpg'), (np.clip(im, 0, 1) * 255).round().astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
        x0, y0, x1, y1 = int(kutu[0] * w), int(kutu[1] * h), int(np.ceil(kutu[2] * w)), int(np.ceil(kutu[3] * h)); kes = im[y0:y1, x0:x1]
        cv2.imwrite(os.path.join(HEDEF, 'kare', ad, f'p{i:02d}.jpg'), (np.clip(kes, 0, 1) * 255).round().astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    bilgi['kutu'] = [round(x0 / w, 5), round(y0 / h, 5), round(x1 / w, 5), round(y1 / h, 5)]; bilgi['poz'] = P['poz']
    yol = os.path.join(HEDEF, 'sahne.json'); S = json.load(open(yol)) if os.path.exists(yol) else {}; S[ad] = bilgi; json.dump(S, open(yol, 'w'), indent=1); print(ad, bilgi)

if __name__ == '__main__':
    for ad in sys.argv[1:]: platform(ad)
