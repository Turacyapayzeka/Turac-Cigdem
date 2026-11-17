"""Ürün filmi renderlarını kurgu sayfasının klasörüne toplar ve çapa noktalarını tek dosyada birleştirir.

    python3 render/3d/urunfilmi_topla.py [kaynak=render/out/urunfilmi] [hedef=urunfilmi/assets]

Kaynakta beklenenler: acilis/a000…a079.jpg; yuzey, cam, sensor, govde, final, pikap, tesis, deniz, gok için .jpg ve .json.
Dron görüntüsü filmin ortak varlığından (animasyon/assets/dron-3b-a.png) kopyalanır.
"""
import json, os, shutil, sys
KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
kaynak = sys.argv[1] if len(sys.argv) > 1 else os.path.join(KOK, 'render', 'out', 'urunfilmi')
hedef = sys.argv[2] if len(sys.argv) > 2 else os.path.join(KOK, 'urunfilmi', 'assets')
os.makedirs(os.path.join(hedef, 'acilis'), exist_ok=True); capa = {}; eksik = []
for ad in ('yuzey', 'cam', 'sensor', 'govde', 'final', 'pikap', 'tesis', 'deniz', 'gok'):
    j = os.path.join(kaynak, ad + '.json'); g = os.path.join(kaynak, ad + '.jpg')
    if not os.path.exists(g): eksik.append(ad + '.jpg'); continue
    shutil.copyfile(g, os.path.join(hedef, ad + '.jpg'))
    if os.path.exists(j): capa[ad] = json.load(open(j))
n = 0
for i in range(80):
    g = os.path.join(kaynak, 'acilis', f'a{i:03d}.jpg')
    if os.path.exists(g): shutil.copyfile(g, os.path.join(hedef, 'acilis', f'a{i:03d}.jpg')); n += 1
if n < 80: eksik.append(f'acilis: {n}/80 kare')
shutil.copyfile(os.path.join(KOK, 'animasyon', 'assets', 'dron-3b-a.png'), os.path.join(hedef, 'dron.png'))
json.dump(capa, open(os.path.join(hedef, 'capa.json'), 'w'), indent=1)
print('toplandı ->', hedef, '| eksik:', eksik or 'yok')
