"""3B simülasyon filminin (simulasyon/) Blender tarafı.

    capa     Yakın plan çekimlerinde kulenin ve namlu uçlarının görüntüdeki yerlerini hesaplar (render almaz):
             araç (stüdyo render'ı üstündeki kule), gemi güvertesi, tesis platformu. Çıktı: sahne.json
    kareler  Kulenin hedefe döndüğü kareleri render eder (--platform arac | gemi | tesis). Çıktı: render/out/simulasyon/<platform>/
    zemin    Araç sahnesinin arazi görüntüleri (--hangi yakin | genis). Çıktı: render/out/simulasyon/arazi/
    dron     Dronun saydam zeminli kareleri: üstten ve karşıdan, uçuş ve takla. Çıktı: render/out/simulasyon/dron/
    /root/bpyenv/bin/python render/3d/simfilm.py capa --cikti simulasyon/assets
    /root/bpyenv/bin/python render/3d/simfilm.py kareler --platform arac
    /root/bpyenv/bin/python render/3d/simfilm.py zemin --hangi yakin --ornek 40 --pozlama -0.5
    /root/bpyenv/bin/python render/3d/simfilm.py dron

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
    secim = [int(v) for v in opt('pozlar', '').split(',') if v] or list(range(len(P))); tum = opt('zemin', '1') == '1'      # --pozlar 0,2,4: yalnızca bu pozlar; --zemin 0: arka plan yeniden alınmaz
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
    sc.render.use_persistent_data = opt('kalici', '0') == '1'     # uzun dizilerde kalıcı veri açıkken boya malzemesi siyah çıkabiliyor; kısa dizilerde hız kazandırır
    for i, (y, e) in enumerate(P):
        if i not in secim: continue
        yat.rotation_euler.z = R(y); dik.rotation_euler.y = -R(e); bpy.context.view_layer.update()
        sc.render.filepath = os.path.join(d, 'poz', f'p{i:02d}.png'); bpy.ops.render.render(write_still=True); print('poz', i, flush=True)
    # atış pozundaki namlu uçları ve yönü
    yat.rotation_euler.z = 0.0; dik.rotation_euler.y = -R(P[38][1]); bpy.context.view_layer.update(); uc, yon = namlu_uclari(dik)
    json.dump({'kutu': kutu, 'poz': len(P), 'uc': [list(u) for u in uc], 'yon': list(yon), 'kule': list(dik.matrix_world.translation),
               'px': None if hangi == 'arac' else {'kule': gor(sc, dik.matrix_world.translation), 'namlu': [gor(sc, u) for u in uc], 'ileri': gor(sc, uc[0] + yon)}}, open(os.path.join(d, 'poz.json'), 'w'), indent=1)

def gor(sc, X):
    w = world_to_camera_view(sc, sc.camera, Vector(X)); return [round(w.x, 5), round(1 - w.y, 5)]

# ------------------------------------------------------------------ arazi ve dron (gerçekçi araç sahnesi)
ATIS_YONU = 140.0          # kulenin araç çekimindeki nişan yönü (derece; aracın önü 0, solu 90)
GENIS = dict(olcek=25.0, en=3840, boy=2160, kule=(0.60, 0.60))      # geniş arazi karesi: kadrajın eni (m) ve kulenin kadrajdaki yeri

def studyo_kamerasi():
    return json.load(open(os.path.join(DEPO, 'render', 'out', 'urunfilmi', 'pikap', 'kamera.json')))

def paralel_kamera(sc, kam, merkez, olcek):
    """Aracın stüdyo render'ıyla aynı yönden bakan paralel izdüşüm kamerası; merkez kadrajın ortasına düşer."""
    from mathutils import Matrix
    cd = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); sc.camera = co; cd.type = 'ORTHO'; cd.ortho_scale = olcek; cd.clip_start = 0.1; cd.clip_end = 400
    sag, asagi, ileri = Vector(kam['sag']), Vector(kam['asagi']), Vector(kam['ileri']); yer = Vector(merkez) - ileri * 120
    co.matrix_world = Matrix(((sag.x, -asagi.x, -ileri.x, yer.x), (sag.y, -asagi.y, -ileri.y, yer.y), (sag.z, -asagi.z, -ileri.z, yer.z), (0, 0, 0, 1))); bpy.context.view_layer.update(); return co

def kapali_hava(c, guc=5.0):
    """Kapalıya yakın gün ışığı: açık gri gökyüzü ve geniş, yumuşak güneş. Işık aracın solundan gelir (stüdyo render'ındaki gölgeyle aynı yön)."""
    sahneler.sky(elev_deg=48, rot_deg=0, strength=float(opt('gok', 0.07)), aerosol=4.5, sun_intensity=0.0); nt = bpy.context.scene.world.node_tree
    for n in nt.nodes:
        if n.bl_idname == 'ShaderNodeTexSky': n.sun_disc = False
    ld = bpy.data.lights.new('gunes', 'SUN'); ld.energy = float(opt('gunes', guc)); ld.angle = R(28); ld.color = (1.0, 0.97, 0.93); lo = bpy.data.objects.new('gunes', ld); c.objects.link(lo)
    lo.rotation_euler = Vector((-0.12, -0.62, -0.78)).to_track_quat('-Z', 'Y').to_euler()

def zemin(cikti):
    """Araç sahnesinin arazi görüntüleri: aracın stüdyo render'ıyla aynı yönden paralel izdüşüm (araç sonradan bindirilir).
    yakin: aracın yakın plan kadrajı; genis: 25 metrelik kadraj. Ufuk görüntüsü burada üretilmez (render/rotus/sim_ufuk.py)."""
    import pikap3b
    hangi = opt('hangi', 'yakin'); d = os.path.join(DEPO, 'render', 'out', 'simulasyon', 'arazi'); os.makedirs(d, exist_ok=True); kam = studyo_kamerasi()
    sahneler.reset(); c = sahneler.coll('arazi'); pikap3b.arazi(c); kapali_hava(c); X0 = Vector(kam['X0']); sag, asagi = Vector(kam['sag']), Vector(kam['asagi']); s = kam['s']
    if hangi == 'yakin':
        YAN, UST, ALT = 348, 70, 50; en, boy = (kam['W'] + 2 * YAN) * kam['kat'], (kam['H'] + UST + ALT) * kam['kat']
        sc = urunfilmi.ayar(en, boy, int(opt('ornek', 64)), pozlama=float(opt('pozlama', -0.9)))
        merkez = X0 + sag * ((kam['W'] / 2 - kam['p0'][0]) / s) + asagi * (((kam['H'] + ALT - UST) / 2 - kam['p0'][1]) / s); paralel_kamera(sc, kam, merkez, (kam['W'] + 2 * YAN) / s)
    elif hangi == 'genis':
        G = GENIS; sc = urunfilmi.ayar(G['en'], G['boy'], int(opt('ornek', 64)), pozlama=float(opt('pozlama', -0.9)))
        pm = G['en'] / G['olcek']; merkez = X0 - sag * ((G['kule'][0] - 0.5) * G['en'] / pm) - asagi * ((G['kule'][1] - 0.5) * G['boy'] / pm); paralel_kamera(sc, kam, merkez, G['olcek'])
    else: raise SystemExit('--hangi yakin|genis')
    sc.render.resolution_percentage = int(opt('yuzde', 100)); sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 95; urunfilmi.kare(os.path.join(d, hangi + ('-deneme' if opt('yuzde', '100') != '100' else '') + '.jpg'))

def dron(cikti):
    """Dronun saydam zeminli kareleri. ust: araç sahnesinin paralel kamerasından (uçuş + vurulduktan sonra takla);
    karsi: kulenin gözünden, yaklaşan dron (uçuş + takla). Işık kapalı havadır; alacakaranlık sahnelerinde kurguda koyulaştırılır."""
    import dron3b
    d = os.path.join(DEPO, 'render', 'out', 'simulasyon', 'dron'); os.makedirs(d, exist_ok=True); kam = studyo_kamerasi(); rnd = np.random.default_rng(5)
    for tur in ('ust', 'karsi'):
        sahneler.reset(); c = sahneler.coll('dron'); kok, ledler = dron3b.dron_yukle(c); kapali_hava(c, 3.0)
        sc = urunfilmi.ayar(384, 384, int(opt('ornek', 48)), pozlama=float(opt('pozlama', -0.6))); sc.render.film_transparent = True; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
        if tur == 'ust': paralel_kamera(sc, kam, (0, 0, 0), 0.9); bas = R(ATIS_YONU + 180)            # dron kuleye doğru uçar
        else: sc.render.resolution_x = sc.render.resolution_y = 512; urunfilmi.kamera((2.3, 0.0, -0.42), (0, 0, 0.0), 105); bas = R(9)     # burun kameraya dönük, hafif yandan
        pozlar = [(0.0, R(-17), bas)] + [(R(40 * i + 15 * rnd.random()), R(-17 + 33 * i), bas + R(24 * i)) for i in range(1, 17)]
        if tur == 'karsi': pozlar = [(R(-7), R(-17), bas), (0.0, R(-17), bas), (R(7), R(-17), bas)] + pozlar[1:]
        for i, e in enumerate(pozlar):
            kok.rotation_euler = e; bpy.context.view_layer.update(); sc.render.filepath = os.path.join(d, f'{tur}{i:02d}.png'); bpy.ops.render.render(write_still=True)
        print(tur, len(pozlar), flush=True)

if __name__ == '__main__':
    cikti = opt('cikti', os.path.join(DEPO, 'simulasyon', 'assets')); os.makedirs(cikti, exist_ok=True); os.makedirs(os.path.join(DEPO, 'render', 'out', 'simulasyon'), exist_ok=True)
    {'capa': capa, 'kareler': kareler, 'zemin': zemin, 'dron': dron}[ARGS[0]](cikti)
