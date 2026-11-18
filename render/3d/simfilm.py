"""3B simülasyon filminin (simulasyon/) Blender tarafı.

    capa     Yakın plan çekimlerinde kulenin ve namlu uçlarının görüntüdeki yerlerini hesaplar (render almaz):
             araç (stüdyo render'ı üstündeki kule), gemi güvertesi, tesis platformu. Çıktı: sahne.json
    kareler  Kulenin hedefe döndüğü kareleri render eder (--platform arac | gemi | tesis). Çıktı: render/out/simulasyon/<platform>/
    /root/bpyenv/bin/python render/3d/simfilm.py capa --cikti simulasyon/assets
    /root/bpyenv/bin/python render/3d/simfilm.py kareler --platform arac

Koordinatlar görüntünün oranıdır (0–1; x soldan, y üstten). 'ates' namlunun görüntüdeki yönüdür (birim vektör).
"""
import bpy, json, math, os, sys
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGS = sys.argv[1:]; sys.argv = [sys.argv[0], 'sim', '--kalite', 'final']       # urunfilmi kendi seçeneklerini sys.argv'den okur
import urunfilmi, sahneler
from urunfilmi import kule, tripod, malzemeler, R
KOK = os.path.dirname(os.path.abspath(__file__)); DEPO = os.path.join(KOK, '..', '..')
def opt(ad, v): return ARGS[ARGS.index('--' + ad) + 1] if '--' + ad in ARGS else v

def namlu_uclari(dik):
    """İki namlunun ucu ve nişan yönü (dünya koordinatı). Namlular dikey grubun yerel +X yönüne bakar."""
    o = next(c for c in dik.children if c.name.startswith('namlu')); M = dik.matrix_world; Mi = M.inverted(); W = o.matrix_world
    V = np.array([(Mi @ (W @ v.co))[:] for v in o.data.vertices]); orta = np.median(V[:, 1]); uc = []
    for sec in (V[:, 1] > orta, V[:, 1] <= orta):
        P = V[sec]; i = np.argmax(P[:, 0]); on = P[P[:, 0] > P[i, 0] - 0.01].mean(0); uc.append(M @ Vector(on))
    return uc, (M.to_3x3() @ Vector((1, 0, 0))).normalized()

def capa(cikti):
    S = {}
    # araç: stüdyo render'ındaki paralel izdüşüm (render/rotus/pikap_studyo.py)
    kam = json.load(open(os.path.join(DEPO, 'render', 'out', 'urunfilmi', 'pikap', 'kamera.json'))); YAN, UST, ALT = 348, 70, 50
    A = np.array(kam['A']); p0 = np.array(kam['p0']); X0 = np.array(kam['X0'])
    def arac_px(X):
        p = p0 + A @ (np.array(X[:]) - X0); return [round(float((p[0] + YAN) / (kam['W'] + 2 * YAN)), 5), round(float((p[1] + UST) / (kam['H'] + UST + ALT)), 5)]
    sahneler.reset(); c = sahneler.coll('urun'); M = malzemeler(); kok, yat, dik = kule(c, M, 0.0, 8.0)
    kok.location = (X0[0], X0[1], kam['taban_z'] + 0.95); kok.rotation_euler.z = R(140); bpy.context.view_layer.update()
    uc, yon = namlu_uclari(dik); a, b = np.array(arac_px(uc[0])), np.array(arac_px(uc[0] + yon)); v = (b - a) * np.array([16, 9]); v /= np.linalg.norm(v)
    S['arac'] = {'kule': arac_px(dik.matrix_world.translation), 'namlu': [arac_px(u) for u in uc], 'ates': [round(float(v[0]), 4), round(float(v[1]), 4)]}
    # gemi güvertesi ve tesis platformu: ürün filmiyle aynı sahneler ve kamera
    urunfilmi.kare = lambda yol: None
    for ad, hangi in (('gemi', 'deniz'), ('tesis', 'tesis')):
        urunfilmi.ortam(os.path.join(DEPO, 'render', 'out', 'simulasyon'), hangi); sc = bpy.context.scene; dik = bpy.data.objects['dikey']
        def px(X):
            w = world_to_camera_view(sc, sc.camera, Vector(X)); return [round(w.x, 5), round(1 - w.y, 5)]
        uc, yon = namlu_uclari(dik); a, b = np.array(px(uc[0])), np.array(px(uc[0] + yon)); v = (b - a) * np.array([16, 9]); v /= np.linalg.norm(v)
        S[ad] = {'kule': px(dik.matrix_world.translation), 'namlu': [px(u) for u in uc], 'ates': [round(float(v[0]), 4), round(float(v[1]), 4)]}
    json.dump(S, open(os.path.join(cikti, 'sahne.json'), 'w'), indent=1); print(json.dumps(S))

# kule hareketi: (gövde dönüşü, namlu yükselişi) derece. 0 bekleme; 1–22 hedefe dönüş; 23–38 takip; 39–40 geri tepme
def pozlar(y0, e0, e1, e2):
    yum = lambda p: p * p * (3 - 2 * p); P = [(y0, e0)]
    P += [(y0 * (1 - yum((i + 1) / 22)), e0 + (e1 - e0) * yum((i + 1) / 22)) for i in range(22)]
    P += [(0.0, e1 + (e2 - e1) * i / 15) for i in range(16)]
    return P + [(0.0, e2 + 1.3), (0.0, e2 + 0.6)]
POZ = {'arac': pozlar(-48, 2, 6, 12), 'gemi': pozlar(42, 6, 4, 3), 'tesis': pozlar(42, 4, 7, 11)}

def sinir(sc, merkez, yaricap, pay=0.0):
    """Render'ı kulenin çevresindeki dikdörtgenle sınırlar. Döner: (x0, y0, x1, y1) oran olarak, y üstten."""
    cam = sc.camera; M = cam.matrix_world.to_3x3(); u = []
    for dx in (-1, 1):
        for dy in (-1, 1):
            w = world_to_camera_view(sc, cam, merkez + M @ Vector((dx * yaricap, dy * yaricap, 0))); u.append((w.x, w.y))
    x0, x1 = max(0.0, min(p[0] for p in u) - pay), min(1.0, max(p[0] for p in u) + pay); y0, y1 = max(0.0, min(p[1] for p in u) - pay), min(1.0, max(p[1] for p in u) + pay)
    sc.render.use_border = True; sc.render.use_crop_to_border = False; sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = x0, x1, y0, y1
    return [round(x0, 5), round(1 - y1, 5), round(x1, 5), round(1 - y0, 5)]

def torun(o):
    for c in o.children: yield c; yield from torun(c)

def kareler(cikti):
    """Kulenin hedefe döndüğü kareler. Araç: sabit katman (tripod, kaide) + her poz için kasa kenarının üstündeki katman.
    Gemi ve tesis: kulesiz arka plan + her poz için saydam kule katmanı. Birleştirme: render/rotus/sim_kareler.py"""
    hangi = opt('platform', 'arac'); d = os.path.join(DEPO, 'render', 'out', 'simulasyon', hangi); os.makedirs(os.path.join(d, 'poz'), exist_ok=True); P = POZ[hangi]; ornek = int(opt('ornek', 64))
    bas, son = int(opt('bas', 0)), int(opt('son', len(P) - 1)); tum = bas == 0 and son == len(P) - 1      # aralık verilirse yalnızca o pozlar yeniden alınır
    if hangi == 'arac':
        kok, yat, dik, G, engel, sc = urunfilmi.pikap_sahne(os.path.join(DEPO, 'render', 'out', 'urunfilmi', 'pikap'), ornek=128)
        donen = list(torun(yat))
        if tum:
            for o in donen: o.hide_render = True
            urunfilmi.kare(os.path.join(d, 'kule-sabit.png'))                       # tripod, kaide ve kasaya düşen gölgeleri
            for o in donen: o.hide_render = False
        engel.hide_render = False
        for o in G: o.hide_render = True
    else:
        urunfilmi.kare = lambda yol: None
        urunfilmi.ortam(d, 'deniz' if hangi == 'gemi' else 'tesis'); sc = bpy.context.scene; kok = bpy.data.objects['kule']; yat = bpy.data.objects['yatay']; dik = bpy.data.objects['dikey']
        kule_parcalari = set(torun(kok))
        if tum:
            for o in kule_parcalari: o.hide_render = True
            sc.render.filepath = os.path.join(d, 'bos.jpg'); bpy.ops.render.render(write_still=True); print('->', sc.render.filepath, flush=True)   # kulesiz arka plan
            for o in kule_parcalari: o.hide_render = False
        for o in bpy.data.objects:
            if o.type == 'MESH' and o not in kule_parcalari: o.visible_camera = False                                   # ışığa ve yansımaya katkısı sürer
        sc.render.film_transparent = True; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    sc.cycles.samples = ornek; kutu = sinir(sc, dik.matrix_world.translation.copy(), 0.98, 0.01)
    sc.render.use_persistent_data = False        # uzun dizilerde kalıcı veri açıkken boya malzemesi siyah çıkabiliyor
    for i, (y, e) in enumerate(P):
        if not bas <= i <= son: continue
        yat.rotation_euler.z = R(y); dik.rotation_euler.y = -R(e); bpy.context.view_layer.update()
        sc.render.filepath = os.path.join(d, 'poz', f'p{i:02d}.png'); bpy.ops.render.render(write_still=True); print('poz', i, flush=True)
    # atış pozundaki namlu uçları ve yönü
    yat.rotation_euler.z = 0.0; dik.rotation_euler.y = -R(P[38][1]); bpy.context.view_layer.update(); uc, yon = namlu_uclari(dik)
    if not tum: return
    json.dump({'kutu': kutu, 'poz': len(P), 'uc': [list(u) for u in uc], 'yon': list(yon), 'kule': list(dik.matrix_world.translation),
               'px': None if hangi == 'arac' else {'kule': gor(sc, dik.matrix_world.translation), 'namlu': [gor(sc, u) for u in uc], 'ileri': gor(sc, uc[0] + yon)}}, open(os.path.join(d, 'poz.json'), 'w'), indent=1)

def gor(sc, X):
    w = world_to_camera_view(sc, sc.camera, Vector(X)); return [round(w.x, 5), round(1 - w.y, 5)]

if __name__ == '__main__':
    cikti = opt('cikti', os.path.join(DEPO, 'simulasyon', 'assets')); os.makedirs(cikti, exist_ok=True); os.makedirs(os.path.join(DEPO, 'render', 'out', 'simulasyon'), exist_ok=True)
    {'capa': capa, 'kareler': kareler}[ARGS[0]](cikti)
