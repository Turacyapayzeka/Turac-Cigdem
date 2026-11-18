"""DRON KALKANI ürün filmi (35 sn) için 3B çekimler: gerçek kule CAD modeli, fiziksel malzemeler, antrasit stüdyo.

    /root/bpyenv/bin/python render/3d/urunfilmi.py <çekim> --cikti DIR [--kalite taslak|final] [--bas N --son N]

Çekimler
  acilis      stüdyo, kamera kulenin çevresinde döner (kare dizisi; kenar ışıkları sırayla açılır)
  yuzey       stüdyo, yakın plan: beşik, göbek ve bağlantı detayları (tek kare)
  cam         stüdyo, yakın plan: sensör camı ve yansımalar (tek kare)
  sensor      stüdyo, sensör ünitesi üç çeyrek (tek kare + grafik katmanı için çapa noktaları)
  govde       stüdyo, kule gövdesi yandan (tek kare + çapa noktaları)
  final       stüdyo, üç çeyrek geniş plan, solda temiz boşluk (tek kare)
  tesis, deniz   sahneler.py ortamlarında kule (tek kare)
  pikap, gok     tamamı 3B araç sahnesi: açık arazide pikap, kule kasada (tek kare); gok geniş gökyüzü kadrajıdır

Model: modeller/kule-parcalar.npz (kule_parcala.py çıktısı). Kule bütün çekimlerde aynı geometridir.
Montajda bulunmayan elektro-optik sensör ünitesi ve tripod saha fotoğraflarına göre modellenmiştir.
"""
import bpy, bmesh, json, math, os, sys, time
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sahneler
from sahneler import reset, coll, put, box, cyl, R

KOK = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[1:]
def opt(ad, varsayilan): return ARGS[ARGS.index('--' + ad) + 1] if '--' + ad in ARGS else varsayilan
FINAL = opt('kalite', 'taslak') == 'final'
FPS = 24
KENAR = True                                      # kenar yuvarlatma (Bevel); uzun kare dizilerinde süre için kapatılabilir
ACILIS = bool(ARGS) and ARGS[0] == 'acilis'      # kare dizisinde kenar yuvarlatma örneği düşük tutulur (süre)

# ------------------------------------------------------------------ malzemeler
def pbr(ad, renk, rough, metal=0.0, kenar=0.0006, puruz=0.0, puruz_olcek=900.0, oynama=0.0, spec=0.5, kaplama=0.0):
    """Fiziksel malzeme: kenar yuvarlatma (Bevel), ince yüzey pürüzü ve hafif pürüzlülük oynaması."""
    m = bpy.data.materials.new(ad); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*renk, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = spec
    if kaplama and 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = kaplama; b.inputs['Coat Roughness'].default_value = 0.03
        if 'Coat Tint' in b.inputs: b.inputs['Coat Tint'].default_value = (0.42, 0.56, 1.0, 1)      # yansıma önleyici kaplamanın mavi tonu
    tc = nt.nodes.new('ShaderNodeTexCoord'); normal = None
    if puruz > 0:
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = puruz_olcek; nz.inputs['Detail'].default_value = 3
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = puruz; bp.inputs['Distance'].default_value = 0.0004
        nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); normal = bp.outputs['Normal']
    if kenar > 0 and KENAR:
        bv = nt.nodes.new('ShaderNodeBevel'); bv.samples = 4; bv.inputs['Radius'].default_value = kenar
        if normal is not None: nt.links.new(normal, bv.inputs['Normal'])
        normal = bv.outputs['Normal']
    if normal is not None: nt.links.new(normal, b.inputs['Normal'])
    if oynama > 0:
        nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 7.0; nz2.inputs['Detail'].default_value = 5
        nt.links.new(tc.outputs['Object'], nz2.inputs['Vector'])
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = rough - oynama; mr.inputs['To Max'].default_value = rough + oynama
        nt.links.new(nz2.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
    return m

def malzemeler():
    return {
        'kum': pbr('kum', (0.34, 0.245, 0.125), 0.56, puruz=0.12, puruz_olcek=1400, oynama=0.06),             # mat kum rengi boya
        'kum2': pbr('kum-koyu', (0.23, 0.165, 0.085), 0.6, puruz=0.1, puruz_olcek=1400),
        'siyah': pbr('siyah', (0.016, 0.016, 0.018), 0.46, puruz=0.08, puruz_olcek=1800, oynama=0.05),        # polimer ve eloksal gövde
        'celik': pbr('celik', (0.03, 0.03, 0.033), 0.46, metal=1.0, oynama=0.05),                           # namlu çeliği
        'vida': pbr('vida', (0.11, 0.11, 0.115), 0.32, metal=1.0, kenar=0.0003),                              # bağlantı elemanları
        'kaide': pbr('kaide', (0.01, 0.01, 0.011), 0.72, puruz=0.06, puruz_olcek=1200, spec=0.25),                      # tripod
        'oyuk': pbr('oyuk', (0.008, 0.008, 0.009), 0.75, kenar=0.0),
        'cam': pbr('cam', (0.0005, 0.001, 0.003), 0.02, metal=0.0, kenar=0.0, spec=1.0, kaplama=1.0),         # yansıma önleyici kaplamalı sensör camı
    }

# ------------------------------------------------------------------ kule
def ag(ad, V, T, m, c):
    me = bpy.data.meshes.new(ad); me.vertices.add(len(V)); me.vertices.foreach_set('co', np.asarray(V, np.float32).ravel())
    me.loops.add(len(T) * 3); me.loops.foreach_set('vertex_index', np.asarray(T, np.int32).ravel())
    me.polygons.add(len(T)); me.polygons.foreach_set('loop_start', np.arange(0, len(T) * 3, 3, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(len(T), 3, np.int32))
    me.update(calc_edges=True); me.validate()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()   # CAD'den gelen ters yüzler
    me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), bool))
    try: me.set_sharp_from_angle(angle=R(33))
    except Exception: pass
    o = bpy.data.objects.new(ad, me); o.data.materials.append(m); return put(o, c)

def bagla(o, ebeveyn):
    bpy.context.view_layer.update(); o.parent = ebeveyn; o.matrix_parent_inverse = ebeveyn.matrix_world.inverted()

def bos(ad, loc, c):
    e = bpy.data.objects.new(ad, None); e.location = loc; put(e, c); return e

def kule(c, M, yatay=0.0, dikey=0.0):
    """Kuleyi kurar. Dönen grupları döndürür: kok (yerleştirme), yat (yatay dönüş, +Z), dik (dikey dönüş; + namluyu kaldırır)."""
    d = np.load(os.path.join(KOK, 'modeller', 'kule-parcalar.npz'))
    yx, yy = [float(v) for v in d['yatay_eksen_xy']]; dx, dz = [float(v) for v in d['dikey_eksen_xz']]
    kok = bos('kule', (0, 0, 0), c); yat = bos('yatay', (yx, yy, 0), c); dik = bos('dikey', (dx, yy, dz), c)
    bagla(yat, kok); bagla(dik, yat)
    grup = {'taban': (kok, 'kum'), 'vida_taban': (kok, 'vida'), 'govde': (yat, 'kum'), 'vida_govde': (yat, 'vida'),
            'besik': (dik, 'kum'), 'vida_besik': (dik, 'vida'), 'silah': (dik, 'siyah'), 'namlu': (dik, 'celik'), 'vida_silah': (dik, 'vida')}
    for ad, (eb, mad) in grup.items():
        bagla(ag(ad, d[ad + '_v'], d[ad + '_t'], M[mad], c), eb)
    # elektro-optik sensör ünitesi: montajda yok; saha fotoğraflarına göre (yaklaşık 19 × 19 × 16 cm), beşiğin üst tablasında
    ex, ey, ez = 0.055, 0.02, 0.492; on = ex + 0.095; parca = []
    parca.append(box((0.19, 0.19, 0.16), (ex, ey, ez), M['kum'], c, bevel=0.006, name='eo'))
    parca.append(box((0.2, 0.2, 0.008), (ex, ey, ez + 0.084), M['kum2'], c, bevel=0.002, name='eo-kapak'))
    for y, r, k in ((ey + 0.04, 0.03, 0.078), (ey - 0.045, 0.017, 0.05)):
        parca.append(box((0.006, k, k), (on + 0.001, y, ez + 0.012), M['oyuk'], c, bevel=0.002, name='yuva'))
        parca.append(duz(cyl(r + 0.005, (on, y, ez + 0.012), (on + 0.007, y, ez + 0.012), M['oyuk'], c, verts=64, name='halka')))
        parca.append(mercek(r, (on + 0.0073, y, ez + 0.012), M['cam'], c))
        for sy, sz in ((-1, -1), (-1, 1), (1, -1), (1, 1)):                      # yuva vidaları
            parca.append(duz(cyl(0.0022, (on + 0.003, y + sy * (k / 2 - 0.006), ez + 0.012 + sz * (k / 2 - 0.006)), (on + 0.0052, y + sy * (k / 2 - 0.006), ez + 0.012 + sz * (k / 2 - 0.006)), M['vida'], c, verts=12, name='v')))
    for sy, sz in ((-1, -1), (-1, 1), (1, -1), (1, 1)):                          # ön kapak vidaları
        parca.append(duz(cyl(0.003, (on - 0.001, ey + sy * 0.083, ez + sz * 0.068), (on + 0.0012, ey + sy * 0.083, ez + sz * 0.068), M['vida'], c, verts=12, name='v')))
    parca.append(duz(cyl(0.011, (ex - 0.115, ey - 0.03, ez - 0.02), (ex - 0.095, ey - 0.03, ez - 0.02), M['oyuk'], c, verts=32, name='konnektor')))
    for yan in (-1, 1):
        for i in range(4):
            parca.append(box((0.007, 0.004, 0.085), (ex - 0.05 + i * 0.03, ey + yan * 0.0955, ez + 0.005), M['oyuk'], c, rot=(0, R(14), 0), bevel=0.001, name='yarik'))
    for p in parca: bagla(p, dik)
    yat.rotation_euler.z = R(yatay); dik.rotation_euler.y = -R(dikey)
    bpy.context.view_layer.update()
    return kok, yat, dik

def mercek(r, merkez, m, c):
    """Hafif bombeli sensör camı: düz disk yerine küre kesiti, yansımalar kavisli düşer. Kutbu +X'e bakar."""
    Rk = r * 3.2; h = Rk - math.sqrt(Rk * Rk - r * r)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=Rk, segments=96, ring_count=192, location=(merkez[0] - Rk + h, merkez[1], merkez[2]), rotation=(0, R(90), 0))
    o = bpy.context.object; o.name = 'mercek'; bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < Rk - h - 1e-6], context='VERTS'); bm.to_mesh(o.data); bm.free()
    bpy.ops.object.shade_smooth(); o.data.materials.append(m); return put(o, c)

def duz(o):
    for p in o.data.polygons: p.use_smooth = False
    return o

def tripod(c, M, yukseklik=0.95, ebeveyn=None):
    """Siyah tripod: yuvarlak üst tabla, orta kolon, üç kare kesitli ayak ve ara bağlantılar (saha fotoğraflarındaki kurulum).
    ebeveyn verilirse parçalar ona bağlanır (kuleyle birlikte taşınır)."""
    k = M['kaide']; z0 = -yukseklik; p = []
    p.append(duz(cyl(0.125, (0, 0, -0.018), (0, 0, 0.0), k, c, verts=96, name='tabla'))); p.append(duz(cyl(0.06, (0, 0, -0.07), (0, 0, -0.018), k, c, verts=64, name='boyun')))
    p.append(cyl(0.027, (0, 0, z0 + 0.25), (0, 0, -0.06), k, c, verts=48, name='kolon'))
    for a in (90, 210, 330):
        d = Vector((math.cos(R(a)), math.sin(R(a)), 0)); ust = Vector((d.x * 0.05, d.y * 0.05, -0.1)); ayak = Vector((d.x * 0.62, d.y * 0.62, z0 + 0.012))
        orta = (ust + ayak) / 2; yon = ayak - ust
        p.append(box((0.032, 0.032, yon.length), orta, k, c, rot=tuple(yon.to_track_quat('Z', 'Y').to_euler()), bevel=0.003, name='ayak'))
        p.append(duz(cyl(0.035, ayak - Vector((0, 0, 0.012)), ayak + Vector((0, 0, 0.004)), k, c, verts=32, name='pabuc')))
        ara0 = Vector((0, 0, z0 + 0.3)); ara1 = ust + yon * 0.62
        p.append(cyl(0.009, ara0, ara1, k, c, verts=16, name='ara'))
    if ebeveyn is not None:
        for o in p: bagla(o, ebeveyn)

# ------------------------------------------------------------------ stüdyo
def alan(ad, loc, hedef, guc, renk, boyut, c, yayilim=75):
    ld = bpy.data.lights.new(ad, 'AREA'); ld.energy = guc * (yayilim / 180.0) ** 2 * 0.5; ld.color = renk   # dar ışın aynı güçte daha parlaktır; güç buna göre düşürülür
    ld.shape = 'RECTANGLE'; ld.size = boyut[0]; ld.size_y = boyut[1]; ld.spread = R(yayilim)
    o = bpy.data.objects.new(ad, ld); o.location = loc; o.rotation_euler = (Vector(hedef) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    o.visible_camera = False; return put(o, c)

HEDEF = Vector((0.27, 0.0, 0.22))

def studyo(c, zemin_z=-0.95, zemin=True):
    """Antrasit stüdyo: koyu mat zemin ve fon; iki ince kenar ışığı, üst arka şerit, yumuşak ana ışık.
    zemin=False: zemin ve fon kadraja girmeyen çekimler için yalnızca antrasit ortam (kare süresi birkaç kat kısalır)."""
    w = bpy.data.worlds.new('antrasit'); w.use_nodes = True; bpy.context.scene.world = w; nt = w.node_tree; bg = nt.nodes['Background']
    bg.inputs['Color'].default_value = (0.0075, 0.008, 0.0095, 1); bg.inputs['Strength'].default_value = 1.0
    if not zemin:
        tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); mp = nt.nodes.new('ShaderNodeMapRange'); rp = nt.nodes.new('ShaderNodeValToRGB')
        nt.links.new(tc.outputs['Generated'], sp.inputs['Vector']); nt.links.new(sp.outputs['Z'], mp.inputs['Value']); nt.links.new(mp.outputs['Result'], rp.inputs['Fac'])
        mp.inputs['From Min'].default_value = -0.5; mp.inputs['From Max'].default_value = 0.6
        e = rp.color_ramp.elements; e[0].position = 0.0; e[0].color = (0.0035, 0.0037, 0.0045, 1); e[1].position = 1.0; e[1].color = (0.006, 0.0065, 0.0078, 1)
        o = rp.color_ramp.elements.new(0.45); o.color = (0.017, 0.018, 0.021, 1); nt.links.new(rp.outputs['Color'], bg.inputs['Color'])
        return isiklar(c)
    zm = pbr('zemin', (0.011, 0.012, 0.014), 0.5, kenar=0.0, oynama=0.07, spec=0.4)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, zemin_z)); z = bpy.context.object; z.data.materials.append(zm); put(z, c)
    fon = pbr('fon', (0.017, 0.018, 0.021), 0.7, kenar=0.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=11, depth=14, vertices=96, location=(0, 0, zemin_z + 7), end_fill_type='NOTHING'); f = bpy.context.object
    f.data.materials.append(fon); bpy.ops.object.shade_smooth(); put(f, c)
    return isiklar(c)

def isiklar(c):
    L = {}
    L['kenar1'] = alan('kenar1', (-1.9, -1.5, 0.75), HEDEF, 620, (0.80, 0.90, 1.0), (0.22, 2.2), c)      # arkadan soğuk ince şerit
    L['kenar2'] = alan('kenar2', (1.3, -2.3, 1.5), HEDEF, 420, (0.86, 0.93, 1.0), (0.22, 2.2), c)        # namlu boyunca kenar çizgisi
    L['ust'] = alan('ust', (-0.5, -0.6, 2.7), HEDEF, 125, (1.0, 0.97, 0.93), (1.8, 0.5), c, yayilim=60)              # üst arka şerit
    L['ana'] = alan('ana', (1.3, 2.6, 1.9), HEDEF, 330, (1.0, 0.94, 0.86), (1.8, 1.3), c, yayilim=70)                # sıcak ana ışık
    L['dolgu'] = alan('dolgu', (-1.6, 2.4, 0.4), HEDEF, 70, (0.86, 0.91, 1.0), (2.2, 1.2), c, yayilim=80)           # hafif dolgu
    return L

def ayar(en, boy, ornek, pozlama=0.0):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.render.resolution_x, sc.render.resolution_y = en, boy; sc.render.resolution_percentage = 100
    sc.cycles.samples = int(opt('ornek', ornek)); sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.cycles.max_bounces = 5; sc.cycles.sample_clamp_indirect = 6.0; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    sc.view_settings.exposure = pozlama; sc.render.fps = FPS
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 94
    return sc

def kamera(loc, hedef, lens, fstop=None, odak=None):
    sc = bpy.context.scene; cd = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); sc.camera = co
    cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.02; cd.clip_end = 500
    bak(co, loc, hedef)
    if fstop: cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop; cd.dof.focus_distance = odak if odak else (Vector(hedef) - Vector(loc)).length
    return co

def bak(co, loc, hedef):
    co.location = loc; co.rotation_euler = (Vector(hedef) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); bpy.context.view_layer.update()

def yorunge(az, el, d, merkez=HEDEF):
    return Vector(merkez) + Vector((math.cos(R(az)) * math.cos(R(el)), math.sin(R(az)) * math.cos(R(el)), math.sin(R(el)))) * d

def piksel(nokta):
    sc = bpy.context.scene; v = world_to_camera_view(sc, sc.camera, Vector(nokta)); return [round(v.x, 5), round(1 - v.y, 5)]

def kare(yol):
    sc = bpy.context.scene; sc.render.filepath = yol; t0 = time.time(); bpy.ops.render.render(write_still=True)
    print(f'-> {yol}  ({time.time() - t0:.0f} sn)', flush=True)

def yumusak(u): return u * u * (3 - 2 * u)

# ------------------------------------------------------------------ çekimler
def sahne_studyo(yatay=0.0, dikey=0.0, zemin=True):
    reset(); c = coll('urun'); M = malzemeler(); kok, yat, dik = kule(c, M, yatay, dikey); tripod(c, M); L = studyo(c, zemin=zemin)
    return c, M, kok, yat, dik, L

def acilis(cikti):
    """0–3,3 sn: karanlıkta kenar ışıkları sırayla açılır, kamera kulenin çevresinde 34 derece döner (80 kare)."""
    c, M, kok, yat, dik, L = sahne_studyo(yatay=-7, dikey=2, zemin=False)
    sc = ayar(1920, 1080, 28 if FINAL else 12, pozlama=0.15); sc.cycles.max_bounces = 4; cam = kamera(yorunge(104, 7, 3.3), HEDEF, 52, fstop=5.6)
    # açılışın kendi ışık dengesi: üst şerit biraz daha güçlü, tripod biraz daha parlak (kare dizisi bu ayarla render edildi)
    L['ust'].data.energy *= 180.0 / 125.0; kb = M['kaide'].node_tree.nodes['Principled BSDF']
    kb.inputs['Base Color'].default_value = (0.012, 0.012, 0.013, 1); kb.inputs['Roughness'].default_value = 0.5
    if 'Specular IOR Level' in kb.inputs: kb.inputs['Specular IOR Level'].default_value = 0.5
    N = 80; guc = {k: v.data.energy for k, v in L.items()}
    kareler = [int(x) for x in opt('kare', '').split(',')] if opt('kare', '') else range(int(opt('bas', 0)), int(opt('son', N - 1)) + 1)
    if not FINAL: sc.render.resolution_x, sc.render.resolution_y = 960, 540
    for i in kareler:
        yol = os.path.join(cikti, f'a{i:03d}.jpg')
        if os.path.exists(yol): continue
        u = i / (N - 1); t = i / FPS
        az = 104 - 34 * (0.3 * u + 0.7 * yumusak(u)); bak(cam, yorunge(az, 7 - 2 * u, 3.3 - 0.25 * u), HEDEF + Vector((0, 0, 0.02)))
        cam.data.dof.focus_distance = (HEDEF - cam.location).length
        h = yumusak(min(1, max(0, (t - 1.2) / 2.1))); yat.rotation_euler.z = R(-7 + 7 * h); dik.rotation_euler.y = -R(2 + 6 * h)
        ac = lambda t0, t1: yumusak(min(1, max(0, (t - t0) / (t1 - t0))))
        L['kenar1'].data.energy = guc['kenar1'] * ac(0.1, 0.9); L['kenar2'].data.energy = guc['kenar2'] * ac(0.5, 1.4)
        L['ust'].data.energy = guc['ust'] * ac(1.0, 1.9); L['ana'].data.energy = guc['ana'] * (0.02 + 0.98 * ac(1.5, 2.9)); L['dolgu'].data.energy = guc['dolgu'] * ac(1.7, 2.9)
        kare(yol)

def tek(cikti, ad, cam_fn, yatay=0.0, dikey=0.0, capalar=None, en=2880, boy=1620, ornek=72, pozlama=0.15, isik=None, zemin=False):
    c, M, kok, yat, dik, L = sahne_studyo(yatay, dikey, zemin)
    if isik: isik(L)
    if not FINAL: en, boy, ornek = en // 3, boy // 3, 20
    ayar(en, boy, ornek, pozlama); cam_fn()
    bilgi = {'ad': ad, 'en': en, 'boy': boy}
    if capalar:
        bilgi['capa'] = {k: piksel(dik.matrix_world @ Vector(v) if b == 'dik' else yat.matrix_world @ Vector(v) if b == 'yat' else Vector(v)) for k, (b, v) in capalar.items()}
    kare(os.path.join(cikti, ad + '.jpg')); json.dump(bilgi, open(os.path.join(cikti, ad + '.json'), 'w'), indent=1)

# dik (beşik) grubunun yerel koordinatları: beşiğin dönüş ekseni orijindedir
def dik_yerel(x, y, z): return ('dik', (x - 0.0033, y + 0.0021, z - 0.2343))

def yuzey(cikti):
    tek(cikti, 'yuzey', lambda: kamera(yorunge(128, 20, 0.95, (0.0, 0.08, 0.2)), (0.0, 0.08, 0.2), 85, fstop=4.0), dikey=6, ornek=80)
def cam_(cikti):
    tek(cikti, 'cam', lambda: kamera(yorunge(-14, 5, 0.62, (0.15, 0.02, 0.5)), (0.15, 0.02, 0.5), 85, fstop=3.2), dikey=6, ornek=96,
        isik=lambda L: setattr(L['ana'], 'location', (2.2, -1.6, 1.5)) or setattr(L['ana'], 'rotation_euler', (HEDEF - Vector((2.2, -1.6, 1.5))).to_track_quat('-Z', 'Y').to_euler()))
def sensor(cikti):
    tek(cikti, 'sensor', lambda: kamera(yorunge(-58, 12, 1.2, (0.07, -0.01, 0.46)), (0.07, -0.01, 0.46), 70, fstop=4.5), dikey=6,
        isik=lambda L: [setattr(L[k], 'location', (L[k].location.x, -L[k].location.y, L[k].location.z)) or setattr(L[k], 'rotation_euler', (HEDEF - L[k].location).to_track_quat('-Z', 'Y').to_euler()) for k in L],
        capalar={'mercek1': dik_yerel(0.165, 0.06, 0.504), 'mercek2': dik_yerel(0.165, -0.025, 0.504), 'kutu_ust': dik_yerel(0.055, 0.02, 0.58), 'yarik': dik_yerel(0.02, -0.078, 0.5)})
def govde(cikti):
    # gövde arkadan çapraz: tahrik gövdesi, göbek, bağlantılar ve taban flanşı; yandaki ekipman kadrajın kenarında kalır
    tek(cikti, 'govde', lambda: kamera(yorunge(150, 11, 1.2, (-0.02, 0.03, 0.2)), (-0.02, 0.03, 0.2), 70, fstop=4.5), dikey=6,
        capalar={'gobek': ('yat', (0.0, 0.14, 0.2343)), 'taban': ('kok', (-0.05, 0.1, 0.06)), 'baglanti': ('yat', (-0.14, 0.004, 0.19)), 'ust_tabla': dik_yerel(-0.03, 0.06, 0.409)})
def final(cikti):
    # üç çeyrek, ürün sağda; solda logo ve başlık için temiz antrasit boşluk
    tek(cikti, 'final', lambda: kamera(yorunge(42, 7, 3.0, (0.443, -0.214, 0.22)), (0.443, -0.214, 0.22), 60, fstop=6.3, odak=3.05), dikey=8, ornek=96, pozlama=0.2,
        capalar={'kule': ('kok', (0.25, 0.0, 0.3))},
        isik=lambda L: setattr(L['kenar1'].data, 'energy', L['kenar1'].data.energy * 0.3))      # üst yüzeylerde sıyırma parlaması olmasın

# ------------------------------------------------------------------ açık hava
def ortam(cikti, hangi):
    """Kuleyi sahneler.py ortamına yerleştirir: 'deniz' = gemi güvertesi, 'tesis' = rafineri platformu. Tek kare."""
    def kanca(name, out, fg, bg, extra): pass                       # ortamın kendi katman renderı yerine kuleli tek kare alınır
    sahneler.render_layers = kanca
    (sahneler.gemi if hangi == 'deniz' else sahneler.rafineri)('final', cikti)
    sc = bpy.context.scene; cam = sc.camera; ust = cam.location.z + 0.1545; ped = (-0.1, 3.3)      # kaide üstü (sahneler.py ile aynı)
    c = coll('urun'); M = malzemeler(); kok, yat, dik = kule(c, M, yatay=float(opt('yatay', 0)), dikey=float(opt('dikey', 7)))
    kok.location = (ped[0], ped[1], ust - 0.037); kok.rotation_euler.z = R(float(opt('yon', -138))); bpy.context.view_layer.update()
    en, boy, ornek = (2560, 1440, 96) if FINAL else (960, 540, 24)
    sc.render.resolution_x, sc.render.resolution_y = en, boy; sc.cycles.samples = ornek; sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 94
    cam.data.dof.focus_distance = (kok.matrix_world.translation - cam.location).length; cam.data.dof.aperture_fstop = 4.0
    bilgi = {'ad': hangi, 'en': en, 'boy': boy, 'capa': {'kule': piksel(dik.matrix_world.translation), 'taban': piksel(kok.matrix_world.translation)}}
    kare(os.path.join(cikti, hangi + '.jpg')); json.dump(bilgi, open(os.path.join(cikti, hangi + '.json'), 'w'), indent=1)

def arac_sahnesi(yon=48.0, dikey=5.0):
    """Tamamı 3B araç sahnesi: açık arazide pikap; kule kasadaki tripodun üstünde. Alçak güneş, uzun gölgeler."""
    import pikap3b
    reset(); c = coll('urun'); M = malzemeler(); taban = pikap3b.pikap(c); pikap3b.arazi(c)
    kok, yat, dik = kule(c, M, 0.0, dikey); tripod(c, M, ebeveyn=kok)
    kok.location = (-1.86, 0.0, taban + 0.95); kok.rotation_euler.z = R(yon); bpy.context.view_layer.update()
    sahneler.sky(elev_deg=float(opt('gunes', 11)), rot_deg=float(opt('gunes-yon', 295)), strength=float(opt('gok', 0.5)), aerosol=1.3, sun_intensity=0.42)
    if opt('bulut', '1') == '1': pikap3b.bulutlar()
    return c, kok, yat, dik

def _arac_kare(cikti, ad, cam_loc, hedef, lens, fstop, yon, dikey, pozlama):
    c, kok, yat, dik = arac_sahnesi(yon, dikey)
    en, boy, ornek = (2560, 1440, 96) if FINAL else (960, 540, 24); ayar(en, boy, ornek, pozlama=float(opt('pozlama', pozlama)))
    kamera(cam_loc, hedef, lens, fstop=fstop, odak=(dik.matrix_world.translation - Vector(cam_loc)).length)
    bilgi = {'ad': ad, 'en': en, 'boy': boy, 'capa': {'kule': piksel(dik.matrix_world.translation), 'taban': piksel(kok.matrix_world.translation)}}
    kare(os.path.join(cikti, ad + '.jpg')); json.dump(bilgi, open(os.path.join(cikti, ad + '.json'), 'w'), indent=1)

def pikap(cikti):
    """Platform entegrasyonu, kara: kule, aracın stüdyo render'ının kasasında. Araç görüntüsünü ve kamerayı
    render/rotus/pikap_studyo.py hazırlar (hazirla); burada kule o kamerayla (paralel izdüşüm) iki saydam katman olarak
    render edilir: kule-tam (kule, tripod ve kasaya düşen gölge), kule-ust (yalnızca kasa kenarının üstünde kalan kısım).
    Katmanları aynı betiğin birlestir adımı araç görüntüsüne bindirir."""
    d = os.path.join(cikti, 'pikap'); kam = json.load(open(os.path.join(d, 'kamera.json')))
    reset(); c = coll('urun'); M = malzemeler(); X0 = Vector(kam['X0']); taban, kenar = kam['taban_z'], kam['kenar_z']
    kok, yat, dik = kule(c, M, 0.0, float(opt('dikey', 8))); tripod(c, M, ebeveyn=kok)
    kok.location = (X0.x, X0.y, taban + 0.95); kok.rotation_euler.z = R(float(opt('yon', 140))); bpy.context.view_layer.update()
    # gölge tutucular: kasa tabanı, ön ve sol iç duvar
    boy, en = kam['kasa_boy'], kam['kasa_en']; tut = pbr('golge-tutucu', (0.02, 0.02, 0.02), 0.8, kenar=0.0); G = []
    G.append(box((boy, en, 0.02), (X0.x, 0, taban - 0.01), tut, c, bevel=0, name='taban')); G.append(box((0.02, en, kenar - taban), (X0.x + boy / 2 + 0.01, 0, (kenar + taban) / 2), tut, c, bevel=0, name='on-duvar'))
    G.append(box((boy, 0.02, kenar - taban), (X0.x, en / 2 + 0.01, (kenar + taban) / 2), tut, c, bevel=0, name='sol-duvar'))
    for o in G: o.is_shadow_catcher = True
    engel = box((30, 30, 10), (0, 0, kenar - 5.0), tut, c, bevel=0, name='kenar-alti'); engel.is_holdout = True; engel.hide_render = True
    # stüdyo ışığı: üstte, aracın soluna kaymış büyük yumuşak kaynak; kameranın yanından hafif dolgu; düz gri ortam
    def isik(ad, loc, guc, boyut, renk=(1, 1, 1)):
        ld = bpy.data.lights.new(ad, 'AREA'); ld.energy = guc; ld.size = boyut; ld.color = renk; lo = bpy.data.objects.new(ad, ld); c.objects.link(lo)
        lo.location = loc; lo.rotation_euler = (X0 + Vector((0, 0, 0.6)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return lo
    isik('ust', X0 + Vector((-0.6, 3.0, 6.5)), float(opt('ust', 5200)), 7.0); isik('dolgu', X0 + Vector((-5.0, -4.0, 4.0)), float(opt('dolgu', 900)), 5.0, (0.95, 0.97, 1.0))
    w = bpy.data.worlds.new('W'); bpy.context.scene.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.82, 0.82, 0.83, 1); bg.inputs['Strength'].default_value = float(opt('ortam', 0.45))
    sc = ayar(kam['W'] * kam['kat'], kam['H'] * kam['kat'], 128 if FINAL else 24, pozlama=float(opt('pozlama', -0.4)))
    sc.render.film_transparent = True; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'; sc.render.image_settings.color_depth = '8'
    cd = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); sc.camera = co; cd.type = 'ORTHO'; cd.ortho_scale = kam['W'] / kam['s']; cd.clip_start = 0.1; cd.clip_end = 200
    sag, asagi, ileri = Vector(kam['sag']), Vector(kam['asagi']), Vector(kam['ileri'])
    merkez = X0 + sag * ((kam['W'] / 2 - kam['p0'][0]) / kam['s']) + asagi * ((kam['H'] / 2 - kam['p0'][1]) / kam['s']); yer = merkez - ileri * 40
    from mathutils import Matrix
    co.matrix_world = Matrix(((sag.x, -asagi.x, -ileri.x, yer.x), (sag.y, -asagi.y, -ileri.y, yer.y), (sag.z, -asagi.z, -ileri.z, yer.z), (0, 0, 0, 1))); bpy.context.view_layer.update()
    kare(os.path.join(d, 'kule-tam.png'))
    engel.hide_render = False
    for o in G: o.hide_render = True
    kare(os.path.join(d, 'kule-ust.png'))

def gok(cikti):
    """Durumsal farkındalık: alçak ve geniş açı; kule sağ altta, kadrajın çoğu gökyüzü."""
    _arac_kare(cikti, 'gok', (-4.1, -3.0, 1.2), (-2.5, 0.9, 3.3), 32, 5.6, yon=118, dikey=14, pozlama=-0.9)

def arac_model(cikti):
    """Aracın model föyü: arka ve ön çaprazdan iki taslak kare (modeli denetlemek için)."""
    for ad, loc, hedef in (('arac-arka', (-7.2, 4.6, 2.3), (-0.3, 0, 1.0)), ('arac-on', (6.8, 4.9, 1.9), (0.3, 0, 0.95)), ('arac-yan', (-0.4, 8.5, 1.5), (-0.1, 0, 1.0))):
        c, kok, yat, dik = arac_sahnesi(48, 5); ayar(960, 540, 24, pozlama=float(opt('pozlama', -0.6))); kamera(loc, hedef, 40); kare(os.path.join(cikti, ad + '.jpg'))

CEKIM = {'acilis': acilis, 'yuzey': yuzey, 'cam': cam_, 'sensor': sensor, 'govde': govde, 'final': final,
         'deniz': lambda c: ortam(c, 'deniz'), 'tesis': lambda c: ortam(c, 'tesis'), 'pikap': pikap, 'gok': gok, 'arac-model': arac_model}

if __name__ == '__main__':
    ad = ARGS[0] if ARGS else 'final'
    cikti = opt('cikti', os.path.join(KOK, '..', 'out', 'urunfilmi')); os.makedirs(cikti, exist_ok=True)
    CEKIM[ad](cikti)
