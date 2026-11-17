"""Gerçek kule CAD modeliyle stüdyo çekimi: kamera kulenin çevresinde döner (film sahne 04).

    /root/bpyenv/bin/python render/3d/kule3b.py onizleme --cikti DIR [--kare 0,76,152]
    /root/bpyenv/bin/python render/3d/kule3b.py cekim --cikti animasyon/assets/kule3b [--bas 0 --son 152]

Model: modeller/kule-parcalar.npz (kule_parcala.py çıktısı: parçalara ayrılmış, aynalaması düzeltilmiş CAD modeli).
Kule, malzemeler, sensör ünitesi ve tripod ürün filmiyle (urunfilmi.py) aynı kurucudan gelir.
Çıktı: 1160×1080 JPEG kareler (k000.jpg …); film motoru bunları sahne 04'ün sağ paneline yerleştirir.
"""
import bpy, math, sys, os, time
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sahneler import reset, coll, put, R
import urunfilmi

KOK = os.path.dirname(os.path.abspath(__file__))
N = 153                      # 5,1 sn × 30 kare
EN, BOY = 1160, 1080
MERKEZ = Vector((0.27, 0.0, 0.20))

def kule(c):
    """Kule, ürün filmiyle aynı kurucudan gelir: parçalara ayrılmış ve aynalaması düzeltilmiş model
    (modeller/kule-parcalar.npz), fiziksel malzemeler, saha fotoğraflarına göre modellenmiş sensör ünitesi ve tripod.
    İlk sürümde taret.glb doğrudan kullanılıyordu; o dosya aynalı olduğu için ters monte tüfek yanlış yanda duruyordu."""
    urunfilmi.KENAR = False                    # 153 karelik dizide kenar yuvarlatma kapalı (süre)
    M = urunfilmi.malzemeler(); urunfilmi.kule(c, M, yatay=0.0, dikey=5.0); urunfilmi.tripod(c, M)

def alan_isik(ad, loc, hedef, guc, renk, boyut, c):
    ld = bpy.data.lights.new(ad, 'AREA'); ld.energy = guc; ld.color = renk; ld.shape = 'RECTANGLE'; ld.size = boyut[0]; ld.size_y = boyut[1]
    o = bpy.data.objects.new(ad, ld); o.location = loc
    o.rotation_euler = (Vector(hedef) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); put(o, c); return o

def dunya():
    """Koyu stüdyo: ufuk çizgisinde hafif aydınlık bant, üstte ve altta kararan zemin (filmin lacivert-siyah paleti)."""
    w = bpy.data.worlds.new('studyo'); w.use_nodes = True; bpy.context.scene.world = w; nt = w.node_tree
    bg = nt.nodes['Background']; tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB'); mp = nt.nodes.new('ShaderNodeMapRange')
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector']); nt.links.new(sep.outputs['Z'], mp.inputs['Value'])
    mp.inputs['From Min'].default_value = -0.45; mp.inputs['From Max'].default_value = 0.6
    nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
    e = ramp.color_ramp.elements; e[0].position = 0.0; e[0].color = (0.004, 0.005, 0.007, 1); e[1].position = 1.0; e[1].color = (0.006, 0.008, 0.012, 1)
    m = ramp.color_ramp.elements.new(0.42); m.color = (0.02, 0.027, 0.038, 1)
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 1.0

def kamera_at(sc, cam, i):
    """Yörünge: arka çaprazdan ön çapraza 95°; namlular hep ekranın solunda. Başta ve sonda yumuşak."""
    u = i / (N - 1); s = u * u * (3 - 2 * u); s = 0.25 * u + 0.75 * s
    az = R(128 - 95 * s); el = R(15 - 8 * s); d = 2.25 - 0.22 * s
    loc = MERKEZ + Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))) * d
    cam.location = loc; hedef = MERKEZ + Vector((0, 0, 0.02))
    cam.rotation_euler = (hedef - loc).to_track_quat('-Z', 'Y').to_euler(); bpy.context.view_layer.update()

def opt_global(ad, varsayilan):
    a = sys.argv[1:]; return a[a.index('--' + ad) + 1] if '--' + ad in a else varsayilan

def sahne(kalite):
    reset(); c = coll('kule'); kule(c); dunya()
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    tam = kalite == 'cekim'
    sc.render.resolution_x, sc.render.resolution_y = (EN, BOY) if tam else (EN // 2, BOY // 2); sc.render.resolution_percentage = 100
    sc.cycles.samples = int(opt_global('ornek', 40)) if tam else 32; sc.render.use_persistent_data = True; sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.cycles.max_bounces = 4; sc.cycles.sample_clamp_indirect = 6.0; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 90
    # ışıklar sahnede sabit; kamera döndükçe parlamalar yüzeylerde gezinir
    alan_isik('ana', (1.5, 2.3, 1.7), MERKEZ, 240, (1.0, 0.93, 0.84), (1.4, 1.0), c)          # sıcak ana ışık, ön sol üst
    alan_isik('kenar', (-2.2, -1.2, 1.3), MERKEZ, 320, (0.72, 0.84, 1.0), (0.9, 1.6), c)       # soğuk kenar ışığı, arka
    alan_isik('kenar2', (1.4, -2.0, 2.1), MERKEZ, 230, (0.8, 0.88, 1.0), (0.6, 1.6), c)        # namlu boyunca kenar çizgisi
    alan_isik('ust', (0.3, 0.0, 2.4), MERKEZ, 45, (1.0, 0.97, 0.92), (1.6, 1.6), c)           # yumuşak üst dolgu
    alan_isik('dolgu', (-0.6, 2.6, 0.2), MERKEZ, 45, (0.85, 0.9, 1.0), (1.8, 1.0), c)          # alttan hafif dolgu
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 62; cd.sensor_width = 36; cd.clip_start = 0.05; cd.clip_end = 200
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 9.0; cd.dof.focus_distance = 2.15
    return sc, cam

if __name__ == '__main__':
    args = sys.argv[1:]; mod = args[0] if args else 'onizleme'
    def opt(ad, varsayilan): return args[args.index('--' + ad) + 1] if '--' + ad in args else varsayilan
    cikti = opt('cikti', os.path.join(KOK, '..', 'out', 'kule3b')); os.makedirs(cikti, exist_ok=True)
    sc, cam = sahne(mod)
    if mod == 'cekim': kareler = range(int(opt('bas', 0)), int(opt('son', N - 1)) + 1)
    else: kareler = [int(x) for x in opt('kare', '0,76,152').split(',')]
    t0 = time.time()
    for i in kareler:
        yol = os.path.join(cikti, f'k{i:03d}.jpg')
        if mod == 'cekim' and os.path.exists(yol): continue        # yarıda kalan çekim kaldığı yerden sürer
        kamera_at(sc, cam, i); sc.render.filepath = yol; bpy.ops.render.render(write_still=True)
        print(f'kare {i} -> {yol}  ({time.time() - t0:.0f} sn)', flush=True)
