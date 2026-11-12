"""Drone Shield: fotoğraflardan kurulmuş sadeleştirilmiş 3B modeller ve tamamı 3B deneme çekimi (Blender / Cycles).

    python render/3d/taret3b.py model  --cikti KLASOR            # taret modelinin üç açıdan görünümü
    python render/3d/taret3b.py pilot  --cikti KLASOR [--kare 1,60,100] [--kalite taslak|final]

Taret, CAD verisi olmadan yalnızca fotoğraflara bakılarak kutu ve silindirlerden kurulmuştur: tanınır ama birebir değildir.
"""
import bpy, bmesh, math, sys, os, json, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sahneler import reset, coll, put, mat, box, cyl, sphere, torus, point_light, sky, setup, R
from mathutils import Vector, noise
from bpy_extras.object_utils import world_to_camera_view

def empty(name, loc, c, parent=None):
    e = bpy.data.objects.new(name, None); c.objects.link(e); e.location = loc
    if parent: e.parent = parent
    return e
def adopt(objs, parent):
    bpy.context.view_layer.update(); inv = parent.matrix_world.inverted()
    for o in objs: o.parent = parent; o.matrix_parent_inverse = inv
def taper(o, kx=1.0, ky=1.0, shift_x=0.0):
    for v in o.data.vertices:
        if v.co.z > 0: v.co.x = v.co.x * kx + shift_x; v.co.y *= ky
def cable(points, r, m, c):
    cu = bpy.data.curves.new('kablo', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('NURBS'); sp.points.add(len(points) - 1)
    for p, q in zip(sp.points, points): p.co = (*q, 1)
    sp.use_endpoint_u = True; sp.order_u = 3
    o = bpy.data.objects.new('kablo', cu); c.objects.link(o); o.data.materials.append(m); return o

def malzemeler():
    return {'bej': mat('bej', (0.36, 0.25, 0.125), rough=0.62, bump=0.12, bump_scale=300), 'siyah': mat('siyah_pol', (0.018, 0.018, 0.02), rough=0.46, bump=0.1, bump_scale=400),
            'namlu': mat('namlu', (0.03, 0.03, 0.033), rough=0.3, metal=0.8), 'cam': mat('mercek', (0.01, 0.03, 0.07), rough=0.04, spec=1.0, metal=0.3),
            'galvaniz': mat('galv', (0.5, 0.52, 0.55), rough=0.4, metal=0.85), 'ayak': mat('ayak', (0.025, 0.025, 0.027), rough=0.5, metal=0.4)}

# ---------------------------------------------------------------- taret
# Ölçüler fotoğraflardan (yan ve arka görünüş) oranlanarak çıkarıldı: tüfek boyu ~1 m, namlu ekseni tabandan ~0,27 m,
# tüfekler eksenin iki yanında ±0,19 m, sensör kutusu üstte ortada, tetik eyleyici kutuları arkada üstte.
def tufek(y, ters, M, c):
    o = []; s = -1 if ters else 1; z = 0.27; dis = 1 if y > 0 else -1
    o.append(box((0.30, 0.052, 0.085), (-0.06, y, z), M['siyah'], c, bevel=0.006))                                  # gövde (büyük kısmı kelepçe bloğunun içinde)
    o.append(cyl(0.033, (0.13, y, z + 0.004 * s), (0.46, y, z + 0.004 * s), M['siyah'], c, verts=8))               # el kundağı
    o.append(box((0.36, 0.024, 0.012), (0.29, y, z + 0.046 * s), M['siyah'], c, bevel=0.002))                       # ray
    for k in range(5): o.append(box((0.03, 0.068, 0.012), (0.18 + k * 0.055, y, z - 0.004 * s), M['namlu'], c, bevel=0.002))   # M-LOK yarıkları
    o.append(cyl(0.012, (0.46, y, z), (0.585, y, z), M['namlu'], c, verts=16))                                     # namlu
    o.append(cyl(0.026, (0.57, y, z), (0.645, y, z), M['siyah'], c, verts=20))                                     # namlu ağzı freni
    for k in range(3): o.append(cyl(0.0275, (0.584 + k * 0.02, y, z), (0.590 + k * 0.02, y, z), M['namlu'], c, verts=20))
    o.append(box((0.055, 0.036, 0.16), (0.045, y, z - 0.15 * s), M['siyah'], c, rot=(0, R(-8) * s, 0), bevel=0.006))   # şarjör (üst parça)
    o.append(box((0.055, 0.036, 0.13), (0.075, y, z - 0.275 * s), M['siyah'], c, rot=(0, R(-24) * s, 0), bevel=0.006)) # şarjör (kavisli alt parça)
    o.append(box((0.042, 0.036, 0.10), (-0.16, y, z - 0.085 * s), M['siyah'], c, rot=(0, R(18) * s, 0), bevel=0.006))  # kabza
    o.append(cyl(0.017, (-0.20, y, z + 0.005 * s), (-0.31, y, z + 0.005 * s), M['siyah'], c, verts=12))             # dipçik borusu
    o.append(box((0.04, 0.038, 0.12), (-0.315, y, z - 0.015 * s), M['siyah'], c, bevel=0.006))                      # dipçik
    return o

def taret(c, M, ayak_boyu=1.05):
    root = empty('taret', (0, 0, 0), c); pan = empty('pan', (0, 0, 0), c, root); tilt = empty('tilt', (0, 0, 0.26), c, pan)
    bej, siyah = M['bej'], M['siyah']
    sabit = [cyl(0.092, (0, 0, 0), (0, 0, 0.014), bej, c, verts=40), cyl(0.076, (0, 0, 0.014), (0, 0, 0.075), bej, c, verts=40)]
    sabit += [cyl(0.115, (0, 0, -0.03), (0, 0, 0), M['ayak'], c, verts=32), cyl(0.034, (0, 0, -0.55), (0, 0, -0.03), M['ayak'], c, verts=20)]
    for k in range(3):
        a = R(90 + k * 120); p = (0.52 * math.cos(a), 0.52 * math.sin(a), -ayak_boyu)
        sabit.append(cyl(0.021, (0.07 * math.cos(a), 0.07 * math.sin(a), -0.05), p, M['ayak'], c, verts=12)); sabit.append(cyl(0.012, (0, 0, -0.52), (p[0] * 0.55, p[1] * 0.55, -0.05 - (ayak_boyu - 0.05) * 0.55), M['ayak'], c, verts=8))
        sabit.append(cyl(0.03, p, (p[0], p[1], p[2] + 0.02), M['ayak'], c, verts=12))
    # yatay dönen kısım: tahrik kutusu ve çatal
    catal = [box((0.20, 0.185, 0.125), (-0.02, 0, 0.138), bej, c, bevel=0.01), box((0.14, 0.02, 0.15), (0, 0.105, 0.255), bej, c, bevel=0.004), box((0.14, 0.02, 0.15), (0, -0.105, 0.255), bej, c, bevel=0.004)]
    for sy in (-1, 1):
        catal.append(cyl(0.02, (-0.12, sy * 0.045, 0.14), (-0.135, sy * 0.045, 0.14), M['namlu'], c, verts=16))                       # arka konnektörler
        for k in range(4): catal.append(cyl(0.006, (-0.121, sy * 0.08, 0.09 + k * 0.03), (-0.124, sy * 0.08, 0.09 + k * 0.03), M['galvaniz'], c, verts=8))
    catal += [cable([(-0.135, 0.045, 0.14), (-0.24, 0.09, 0.16), (-0.27, 0.12, 0.33), (-0.16, 0.06, 0.47), (-0.09, 0.03, 0.43)], 0.007, siyah, c),
              cable([(-0.135, -0.045, 0.14), (-0.25, -0.12, 0.13), (-0.3, -0.22, 0.26), (-0.2, -0.19, 0.38)], 0.006, siyah, c),
              cable([(-0.2, 0.19, 0.38), (-0.3, 0.24, 0.3), (-0.27, 0.16, 0.12), (-0.12, 0.09, 0.1)], 0.006, siyah, c)]
    # dikey dönen beşik: taşıyıcı plaka, iki kelepçe bloğu, sensör kutusu, eyleyici kutuları, iki tüfek
    besik = [box((0.36, 0.50, 0.03), (-0.03, 0, 0.345), bej, c, bevel=0.006), cyl(0.024, (0, -0.105, 0.26), (0, 0.105, 0.26), M['namlu'], c, verts=20),
             box((0.17, 0.135, 0.125), (0.0, 0, 0.4225), bej, c, bevel=0.008),
             cyl(0.037, (0.08, 0.028, 0.425), (0.092, 0.028, 0.425), M['cam'], c, verts=32), torus(0.039, 0.005, (0.089, 0.028, 0.425), (0, R(90), 0), siyah, c),
             cyl(0.019, (0.08, -0.04, 0.438), (0.09, -0.04, 0.438), M['cam'], c, verts=24), torus(0.021, 0.004, (0.088, -0.04, 0.438), (0, R(90), 0), siyah, c)]
    for k in range(4):
        for sy in (-1, 1): besik.append(box((0.012, 0.005, 0.09), (-0.05 + k * 0.03, sy * 0.069, 0.4225), bej, c, bevel=0.001))
    for sy in (-1, 1):
        besik.append(box((0.34, 0.085, 0.105), (-0.04, sy * 0.19, 0.1925), bej, c, bevel=0.008))                                        # alt kelepçe kutusu
        besik.append(box((0.28, 0.004, 0.07), (-0.04, sy * 0.234, 0.1925), bej, c, bevel=0.001))                                        # yan kapak
        besik.append(box((0.11, 0.09, 0.075), (0.07, sy * 0.19, 0.3), bej, c, bevel=0.006))                                             # ön üst kelepçe
        besik.append(box((0.05, 0.09, 0.085), (-0.17, sy * 0.19, 0.29), bej, c, bevel=0.005))                                           # arka kelepçe
        besik.append(box((0.135, 0.075, 0.11), (-0.145, sy * 0.19, 0.415), siyah, c, bevel=0.006))                                      # tetik eyleyici kutusu
        for k in range(4): besik.append(cyl(0.007, (-0.19 + k * 0.03, sy * 0.228, 0.43), (-0.19 + k * 0.03, sy * 0.2285, 0.43), M['galvaniz'], c, verts=10))
    besik += tufek(0.19, False, M, c) + tufek(-0.19, True, M, c)
    # namlu alevleri (yalnızca atış karelerinde görünür)
    alev_m = mat('alev3b', (1, 0.5, 0.15), emit=(1.0, 0.36, 0.07), strength=6.5); alevler = []
    for y in (0.19, -0.19):
        bpy.ops.mesh.primitive_cone_add(radius1=0.075, radius2=0.0, depth=0.42, vertices=9, location=(0.87, y, 0.27), rotation=(0, R(90), 0)); a = bpy.context.object; a.data.materials.append(alev_m); put(a, c)
        b = sphere(0.055, (0.68, y, 0.27), alev_m, c); l = point_light((0.78, y, 0.3), 2500, (1.0, 0.6, 0.25), c, radius=0.1); alevler += [a, b, l]
    adopt(sabit, root); adopt(catal, pan); adopt(besik + alevler, tilt)
    for a in alevler: a.hide_render = True
    return root, pan, tilt, alevler

# ---------------------------------------------------------------- pikap
def pikap(c):
    kamo = bpy.data.materials.new('kamo'); kamo.use_nodes = True; nt = kamo.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.42
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.7; nz.inputs['Detail'].default_value = 2.5; nz.inputs['Roughness'].default_value = 0.45
    cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'
    e = cr.color_ramp.elements; e[0].position = 0.0; e[0].color = (0.025, 0.025, 0.027, 1); e[1].position = 0.43; e[1].color = (0.07, 0.07, 0.072, 1)
    for pos, col in ((0.52, (0.17, 0.16, 0.145, 1)), (0.61, (0.07, 0.07, 0.072, 1)), (0.68, (0.12, 0.115, 0.11, 1))):
        el = e.new(pos); el.color = col
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    cam_m = mat('oto_cam', (0.012, 0.014, 0.016), rough=0.03, spec=1.0); siyah = mat('oto_siyah', (0.02, 0.02, 0.022), rough=0.6); lastik = mat('lastik', (0.016, 0.016, 0.017), rough=0.9, bump=0.5, bump_scale=120)
    jant = mat('jant', (0.1, 0.1, 0.11), rough=0.35, metal=0.9); krom = mat('krom', (0.6, 0.6, 0.62), rough=0.18, metal=1.0)
    far = mat('far', (1, 1, 1), emit=(1.0, 0.95, 0.85), strength=6.0); stop = mat('stop', (0.3, 0.0, 0.0), rough=0.2, emit=(1.0, 0.03, 0.02), strength=3.0)
    o = []
    o.append(box((5.25, 1.86, 0.55), (-0.02, 0, 0.72), kamo, c, bevel=0.07))
    kaput = box((1.28, 1.80, 0.30), (1.98, 0, 1.10), kamo, c, bevel=0.09); taper(kaput, 0.96, 0.97, shift_x=-0.02); o.append(kaput)
    o.append(box((2.38, 1.86, 0.30), (0.22, 0, 1.11), kamo, c, bevel=0.06))
    sera = box((2.26, 1.74, 0.52), (0.2, 0, 1.51), cam_m, c, bevel=0.05); taper(sera, 0.74, 0.88, shift_x=-0.06); o.append(sera)
    o.append(box((1.62, 1.50, 0.05), (0.12, 0, 1.775), kamo, c, bevel=0.02))
    for sy in (-1, 1):
        o.append(box((0.07, 0.05, 0.5), (0.08, sy * 0.80, 1.5), kamo, c, bevel=0.01))                          # B direği
        o.append(box((1.78, 0.07, 0.5), (-1.80, sy * 0.895, 1.10), kamo, c, bevel=0.03))                        # kasa yanı
        o.append(box((0.22, 0.1, 0.12), (1.12, sy * 1.0, 1.30), siyah, c, bevel=0.03))                          # ayna
        o.append(box((0.05, 0.36, 0.10), (2.635, sy * 0.68, 1.02), far, c, bevel=0.01)); o.append(box((0.05, 0.13, 0.36), (-2.705, sy * 0.86, 1.1), stop, c, bevel=0.01))
        for ax in (1.62, -1.62):
            o.append(cyl(0.47, (ax, sy * 0.72, 0.43), (ax, sy * 0.945, 0.43), siyah, c, verts=40))             # davlumbaz
            o.append(cyl(0.40, (ax, sy * 0.70, 0.40), (ax, sy * 0.98, 0.40), lastik, c, verts=40)); o.append(cyl(0.25, (ax, sy * 0.9, 0.40), (ax, sy * 0.985, 0.40), jant, c, verts=24)); o.append(cyl(0.07, (ax, sy * 0.98, 0.40), (ax, sy * 0.995, 0.40), krom, c, verts=16))
    o.append(box((0.07, 1.86, 0.5), (-2.66, 0, 1.10), kamo, c, bevel=0.03)); o.append(box((0.07, 1.86, 0.55), (-0.93, 0, 1.12), kamo, c, bevel=0.03))
    o.append(box((1.75, 1.8, 0.05), (-1.80, 0, 0.875), siyah, c, bevel=0))
    o.append(box((0.18, 1.9, 0.28), (2.66, 0, 0.60), siyah, c, bevel=0.05)); o.append(box((0.16, 1.9, 0.2), (-2.72, 0, 0.62), krom, c, bevel=0.04)); o.append(box((0.05, 1.05, 0.24), (2.635, 0, 0.9), siyah, c, bevel=0.01))
    o.append(cyl(0.006, (-0.55, 0.5, 1.78), (-0.75, 0.5, 2.25), siyah, c, verts=6))
    root = empty('pikap', (0, 0, 0), c); adopt(o, root); return root

# ---------------------------------------------------------------- dron
def dron(c):
    govde = mat('dron_govde', (0.1, 0.1, 0.105), rough=0.5); per = bpy.data.materials.new('pervane'); per.use_nodes = True
    b = per.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1); b.inputs['Alpha'].default_value = 0.22
    led = mat('dron_led', (1, 1, 1), emit=(1.0, 0.05, 0.03), strength=40.0); cam_m = mat('dron_cam', (0.01, 0.01, 0.012), rough=0.05)
    o = [box((0.20, 0.10, 0.055), (0, 0, 0), govde, c, bevel=0.012), sphere(0.03, (0.1, 0, -0.03), cam_m, c), sphere(0.012, (-0.1, 0, 0.01), led, c)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = (sx * 0.15, sy * 0.15, 0.02); o.append(cyl(0.008, (sx * 0.06, sy * 0.03, 0.0), p, govde, c, verts=8)); o.append(cyl(0.016, (p[0], p[1], 0.0), (p[0], p[1], 0.045), govde, c, verts=12))
            o.append(cyl(0.115, (p[0], p[1], 0.048), (p[0], p[1], 0.05), per, c, verts=28)); o.append(cyl(0.004, (sx * 0.07, sy * 0.05, -0.02), (sx * 0.09, sy * 0.07, -0.09), govde, c, verts=6))
    root = empty('dron', (0, 0, 0), c); adopt(o, root); root.scale = (2.6, 2.6, 2.6); return root

# ---------------------------------------------------------------- arazi
def yukseklik(x, y):
    d = math.hypot(x + 2, y); k = min(1.0, max(0.0, (d - 28) / 150)); k = k * k * (3 - 2 * k)
    return k * (16 * noise.fractal(Vector((x / 170, y / 170, 0.3)), 1.0, 2.0, 5) + 7)
def arazi(c):
    m = bpy.data.materials.new('arazi'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.92
    tc = nt.nodes.new('ShaderNodeTexCoord'); n1 = nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.035; n1.inputs['Detail'].default_value = 8
    cr = nt.nodes.new('ShaderNodeValToRGB'); e = cr.color_ramp.elements; e[0].position = 0.34; e[0].color = (0.035, 0.028, 0.02, 1); e[1].position = 0.62; e[1].color = (0.09, 0.075, 0.04, 1)
    el = e.new(0.48); el.color = (0.05, 0.05, 0.028, 1)
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 9; n2.inputs['Detail'].default_value = 6; bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.8; bp.inputs['Distance'].default_value = 0.05
    nt.links.new(tc.outputs['Object'], n1.inputs['Vector']); nt.links.new(n1.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(tc.outputs['Object'], n2.inputs['Vector']); nt.links.new(n2.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    me = bpy.data.meshes.new('arazi'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=170, y_segments=170, size=450)
    for v in bm.verts: v.co.z = yukseklik(v.co.x, v.co.y)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('arazi', me); c.objects.link(o); o.data.materials.append(m)
    # çakıllı yol: aracın altında açık renkli şerit
    yol = mat('yol', (0.085, 0.08, 0.072), rough=0.95, bump=1.0, bump_scale=60, vary=0.4); box((60, 5.2, 0.02), (4, 0, 0.012), yol, c, bevel=0)
    cali = mat('cali', (0.03, 0.035, 0.018), rough=1.0); rnd0 = random.Random(9)
    for i in range(170):
        x, y = rnd0.uniform(-70, 90), rnd0.uniform(-40, 130)
        if abs(y) < 4 and -8 < x < 34: continue
        b = sphere(rnd0.uniform(0.25, 0.7), (x, y, yukseklik(x, y) + 0.12), cali, c); b.scale = (1.0, rnd0.uniform(0.7, 1.3), rnd0.uniform(0.45, 0.8))
    direk = mat('direk', (0.1, 0.1, 0.1), rough=0.8)
    for i in range(40):
        x = -60 + i * 4.0; cyl(0.05, (x, 14, yukseklik(x, 14)), (x, 14, yukseklik(x, 14) + 1.6), direk, c, verts=6)
    # uzakta tesis binaları
    duvar = mat('duvar', (0.2, 0.21, 0.22), rough=0.7, vary=0.2); cati = mat('cati', (0.07, 0.09, 0.12), rough=0.5); isik = mat('bina_isik', (1, 1, 1), emit=(1.0, 0.7, 0.4), strength=30.0)
    rnd = random.Random(3)
    for i in range(9):
        x = rnd.uniform(-60, 150); y = 150 + rnd.uniform(0, 170); L = rnd.uniform(22, 55); z = yukseklik(x, y)
        box((L, 12, 6.5), (x, y, z + 3.0), duvar, c, bevel=0.05); box((L + 0.6, 12.6, 0.5), (x, y, z + 6.4), cati, c, bevel=0)
        for k in range(int(L // 6)): sphere(0.35, (x - L / 2 + 3 + k * 6, y - 6.4, z + 5.2), isik, c)
    return o

# ---------------------------------------------------------------- model föyü
def model(out):
    reset(); sc = setup('taslak', exposure=-0.9); sc.render.resolution_x, sc.render.resolution_y = 900, 700; sc.cycles.samples = 64
    C = coll('M'); M = malzemeler(); root, pan, tilt, alevler = taret(C, M)
    zemin = mat('zemin_m', (0.45, 0.46, 0.47), rough=0.8); bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -1.05)); g = bpy.context.object; g.data.materials.append(zemin); put(g, C)
    sky(elev_deg=38, rot_deg=140, strength=0.22, aerosol=1.0, sun_intensity=0.6)
    tilt.rotation_euler = (0, R(-18), 0)
    cd = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); sc.camera = co; cd.lens = 60
    os.makedirs(out, exist_ok=True)
    for name, loc, hedef in (('yakin', (1.75, 1.35, -0.35), (0.02, 0, 0.26)), ('yan', (0.1, 3.0, 0.3), (0.1, 0, 0.2)), ('arka', (-2.6, -0.25, 0.45), (0, 0, 0.2))):
        co.location = loc; d = Vector(hedef) - Vector(loc); co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92; sc.render.filepath = os.path.join(out, f'model-{name}.jpg'); bpy.ops.render.render(write_still=True)

# ---------------------------------------------------------------- deneme çekimi
def pilot(out, kareler=None, kalite='taslak'):
    FPS = 24; N = 120; ATIS = 84; VURUS = 91
    reset(); sc = setup('taslak', exposure=-0.25)
    sc.render.resolution_x, sc.render.resolution_y = {'final': (960, 540), 'kare': (1280, 720)}.get(kalite, (640, 360)); sc.cycles.samples = {'final': 24, 'kare': 96}.get(kalite, 20)
    sc.render.use_persistent_data = True; sc.cycles.max_bounces = 4; sc.render.fps = FPS
    C = coll('S'); M = malzemeler()
    arazi(C); pikap(C); root, pan, tilt, alevler = taret(C, M, ayak_boyu=1.06); root.location = (-1.8, 0, 1.96); hedef = dron(C)
    sky(elev_deg=4.5, rot_deg=-28, strength=0.3, aerosol=1.5, sun_intensity=0.5)          # alçak güneş, hedef yönünde: arkadan ışık
    bpy.context.view_layer.update(); pivot = Vector((-1.8, 0, 1.96 + 0.26))
    def yon(az, el, d): return pivot + Vector((math.cos(R(el)) * math.cos(R(az)), math.cos(R(el)) * math.sin(R(az)), math.sin(R(el)))) * d
    A = yon(84, 17, 150); B = yon(88, 13, 34)                                              # dron: uzaktan dalış, vuruş tarete 34 m
    def dron_konum(f): p = min(1.0, (f - 1) / (VURUS - 1)); return A.lerp(B, p) + Vector((0, 0, math.sin(f * 0.35) * 0.2))
    rnd = random.Random(5); parcalar = []
    par_m = mat('parca', (0.08, 0.08, 0.085), rough=0.5); patlama_m = mat('patlama', (1, 0.45, 0.12), emit=(1.0, 0.33, 0.06), strength=5.5); duman_m = mat('duman', (0.09, 0.09, 0.095), rough=1.0)
    patlama = empty('patlama', B, C); adopt([sphere(0.5, B, patlama_m, C), sphere(0.34, B + Vector((0.35, -0.1, 0.2)), patlama_m, C), sphere(0.3, B + Vector((-0.3, 0.1, -0.15)), patlama_m, C), sphere(0.24, B + Vector((0.1, 0.0, 0.42)), patlama_m, C)], patlama)
    duman = empty('duman', B, C); adopt([sphere(0.55, B, duman_m, C), sphere(0.42, B + Vector((0.4, 0, 0.3)), duman_m, C), sphere(0.38, B + Vector((-0.35, 0, 0.25)), duman_m, C)], duman)
    pl = point_light(B, 40000, (1.0, 0.5, 0.2), C, radius=0.5); pl.hide_render = True
    for i in range(12): parcalar.append((box((rnd.uniform(0.1, 0.3), rnd.uniform(0.05, 0.14), 0.03), B, par_m, C, bevel=0), Vector((rnd.uniform(-6, 6), rnd.uniform(-9, -2), rnd.uniform(-1, 6))), Vector((rnd.uniform(-9, 9), rnd.uniform(-9, 9), rnd.uniform(-9, 9)))))
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 32; cd.clip_end = 5000
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0; netlik = empty('netlik', pivot, C); cd.dof.focus_object = netlik
    bakis = empty('bakis', (0, 0, 0), C); tr = cam.constraints.new('TRACK_TO'); tr.target = bakis; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    def ease(p): return p * p * (3 - 2 * p)
    for f in range(1, N + 1):
        p = ease((f - 1) / (N - 1)); ang = R(-126 + 16 * p); rad = 4.7 - 0.6 * p
        cam.location = (-1.8 + rad * math.cos(ang), rad * math.sin(ang), 2.55 + 0.1 * p); cam.keyframe_insert('location', frame=f)
        bakis.location = pivot + Vector((-0.75 + 0.25 * p, 1.2, 0.35)); bakis.keyframe_insert('location', frame=f)       # taret kadrajın sağ üçte birinde kalır
        q = dron_konum(min(f, VURUS)) - pivot; az = math.atan2(q.y, q.x); el = math.atan2(q.z, math.hypot(q.x, q.y))
        w = ease(min(1.0, max(0.0, (f - 10) / 30))); az0 = R(20); tepme = R(1.8) if f == ATIS else R(0.8) if f == ATIS + 1 else 0
        pan.rotation_euler = (0, 0, az0 + (az - az0) * w); pan.keyframe_insert('rotation_euler', frame=f)
        tilt.rotation_euler = (0, -(el * w + tepme), 0); tilt.keyframe_insert('rotation_euler', frame=f)
        hedef.location = dron_konum(f); hedef.rotation_euler = (R(6), R(16), math.atan2(B.y - A.y, B.x - A.x)); hedef.keyframe_insert('location', frame=f)
        dt = (f - VURUS) / FPS
        for o, v, wv in parcalar:
            o.hide_render = f < VURUS; o.keyframe_insert('hide_render', frame=f)
            if dt >= 0: o.location = B + v * dt + Vector((0, 0, -4.9 * dt * dt)); o.rotation_euler = (wv.x * dt, wv.y * dt, wv.z * dt); o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
        for a in alevler: a.hide_render = f not in (ATIS, ATIS + 1); a.keyframe_insert('hide_render', frame=f)
        pl.hide_render = f not in (VURUS, VURUS + 1, VURUS + 2); pl.keyframe_insert('hide_render', frame=f)
        k = 1.0 + 0.7 * (f - VURUS) if f >= VURUS else 1.0; patlama.scale = (k, k, k); patlama.keyframe_insert('scale', frame=f)
        g = max(0, f - VURUS - 1); duman.scale = (1 + 0.16 * g,) * 3; duman.location = B + Vector((0.03 * g, 0, 0.05 * g)); duman.keyframe_insert('scale', frame=f); duman.keyframe_insert('location', frame=f)
    def dron_gizle(f):
        for o in [hedef] + list(hedef.children): o.hide_render = f >= VURUS
        for o in patlama.children: o.hide_render = f not in (VURUS, VURUS + 1, VURUS + 2)
        for o in duman.children: o.hide_render = f < VURUS + 2
    os.makedirs(out, exist_ok=True); sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 95
    liste = kareler or list(range(1, N + 1)); t0 = time.time()
    for i, f in enumerate(liste):
        yol = os.path.join(out, f'k{f:04d}.jpg')
        if os.path.exists(yol): continue
        sc.frame_set(f); dron_gizle(f); sc.render.filepath = yol; bpy.ops.render.render(write_still=True)
        v = world_to_camera_view(sc, cam, hedef.matrix_world.translation); t = world_to_camera_view(sc, cam, pivot)
        print(f'KARE {f} {i + 1}/{len(liste)} sn={time.time() - t0:.0f} dron=({v.x:.2f},{1 - v.y:.2f}) taret=({t.x:.2f},{1 - t.y:.2f})', flush=True)

if __name__ == '__main__':
    args = sys.argv[1:]; ne = args[0] if args else 'model'
    out = args[args.index('--cikti') + 1] if '--cikti' in args else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cikti')
    if ne == 'model': model(out)
    else: pilot(out, [int(x) for x in args[args.index('--kare') + 1].split(',')] if '--kare' in args else None, args[args.index('--kalite') + 1] if '--kalite' in args else 'taslak')
