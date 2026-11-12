"""Hedef dron: kullanıcının 3B baskı projesinden gelen ağ (render/3d/modeller/dron.npz) ile kurulur.

    python render/3d/dron3b.py sprite --cikti KLASOR     # film için saydam zeminli dron görüntüleri + tanıtım karesi

Ağ milimetre cinsinden ve yaklaşık 1:2,6 ölçeklidir; ön taraf −y, motorlar (±61, −34.5) ve (±47, +36).
dron_yukle() ağı gerçek boyuta getirir (açıklık ≈ 0,35 m), önü +x yapar ve dönen pervane diskleri ekler.
"""
import bpy, math, os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sahneler import reset, coll, put, mat, cyl, sphere, sky, setup, R
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modeller', 'dron.npz')
GERCEK = 0.00263                      # model mm → gerçek metre
MOTOR = [(-61.2, -34.5, 5.2), (61.2, -34.5, 5.2), (-47.2, 36.0, 9.2), (47.2, 36.0, 9.2)]   # model mm

def dron_yukle(c, olcek=1.0, pervane=True):
    d = np.load(MODEL); v = d['v'].astype(np.float64); f = d['f']
    k = GERCEK * olcek; w = np.stack([-v[:, 1] * k, v[:, 0] * k, v[:, 2] * k], axis=1)          # önü +x'e çevir
    me = bpy.data.meshes.new('dron'); me.from_pydata(w.tolist(), [], f.tolist()); me.update()
    o = bpy.data.objects.new('dron_govde', me); c.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    try:
        bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.shade_auto_smooth(angle=math.radians(38)); o.select_set(False)
    except Exception: pass
    o.data.materials.append(mat('dron_gri', (0.105, 0.11, 0.118), rough=0.42, spec=0.6))
    root = bpy.data.objects.new('dron', None); c.objects.link(root); o.parent = root
    led = mat('dron_led', (1, 1, 1), emit=(1.0, 0.05, 0.03), strength=30.0); ledler = []
    for (mx, my, mz) in MOTOR[:2]:                                    # ön kollarda kırmızı ışık
        s = sphere(3.0 * k, (-my * k - 4 * k, mx * k * 0.93, (mz - 9) * k), led, c); s.parent = root; ledler.append(s)
    if pervane:
        pm = bpy.data.materials.new('pervane'); pm.use_nodes = True; b = pm.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (0.03, 0.03, 0.03, 1); b.inputs['Alpha'].default_value = 0.16; b.inputs['Roughness'].default_value = 0.3
        for (mx, my, mz) in MOTOR:
            p = (-my * k, mx * k, (mz + 2.5) * k); disk = cyl(37 * k, p, (p[0], p[1], p[2] + 0.6 * k), pm, c, verts=40); disk.parent = root
            gob = cyl(4.5 * k, (p[0], p[1], p[2] - 2 * k), (p[0], p[1], p[2] + 2 * k), o.data.materials[0], c, verts=16); gob.parent = root
    return root, ledler

def sprite(out):
    """Film için saydam zeminli iki görünüm ve bir tanıtım karesi."""
    os.makedirs(out, exist_ok=True)
    from PIL import Image
    bilgi = {}
    for ad, az, el in (('a', -38, -14), ('b', -26, -5)):                 # burun görüntünün sağına bakar: filmde dronlar soldan sağa uçar
        reset(); sc = setup('taslak', exposure=-0.5); sc.cycles.samples = 96; sc.render.resolution_x, sc.render.resolution_y = 1100, 800; sc.render.film_transparent = True
        C = coll('D'); root, ledler = dron_yukle(C)
        for l in ledler: l.hide_render = True                           # ışığı film motoru yakıp söndürür
        sky(elev_deg=35, rot_deg=160, strength=0.13, aerosol=6.0, sun_intensity=0.15)    # kapalı hava: yumuşak ışık, koyu siluet
        cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 85
        a, e = R(az), R(el); p = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))) * 1.9
        cam.location = p; cam.rotation_euler = (-p).to_track_quat('-Z', 'Y').to_euler(); bpy.context.view_layer.update()
        sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'; ham = os.path.join(out, f'_ham-{ad}.png'); sc.render.filepath = ham; bpy.ops.render.render(write_still=True)
        im = Image.open(ham); bb = im.getbbox(); kirp = im.crop(bb); k = 640 / kirp.width; kirp = kirp.resize((640, round(kirp.height * k)), Image.LANCZOS); kirp.save(os.path.join(out, f'dron-3b-{ad}.png'), optimize=True)
        l = world_to_camera_view(sc, cam, ledler[0].matrix_world.translation); lx, ly = l.x * 1100, (1 - l.y) * 800
        bilgi[ad] = {'en': 640, 'boy': kirp.height, 'led': [round((lx - (bb[0] + bb[2]) / 2) / (bb[2] - bb[0]), 3), round((ly - (bb[1] + bb[3]) / 2) / (bb[3] - bb[1]), 3)]}
        os.remove(ham)
    json.dump(bilgi, open(os.path.join(out, 'dron-3b.json'), 'w'), indent=1); print('SPRITE', json.dumps(bilgi))
    # tanıtım karesi: alacakaranlıkta yakın plan
    reset(); sc = setup('taslak', exposure=-0.2); sc.cycles.samples = 128; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    C = coll('D'); root, ledler = dron_yukle(C); root.rotation_euler = (R(6), R(9), R(-18))
    sky(elev_deg=5, rot_deg=205, strength=0.32, aerosol=1.6, sun_intensity=0.6)
    cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 70
    p = Vector((1.25, 0.55, -0.22)); cam.location = p; cam.rotation_euler = (Vector((0, 0, 0.02)) - p).to_track_quat('-Z', 'Y').to_euler()
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 93; sc.render.filepath = os.path.join(out, 'dron-3b-tanitim.jpg'); bpy.ops.render.render(write_still=True)

if __name__ == '__main__':
    args = sys.argv[1:]; out = args[args.index('--cikti') + 1] if '--cikti' in args else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cikti')
    sprite(out)
