"""Gerçekçi çift kabin pikap ve açık arazi (ürün filminin araç sahneleri için). Marka işareti ve plaka yoktur.

Gövde, boy boyunca dizilmiş kesitlerden örülen tek bir yüzeydir (alt bölme yüzeyiyle yumuşatılır); camlar, direkler
ve tavan aynı yüzeyin farklı malzemeli yüzleridir. Kasa boşluğu, çamurluk yuvaları ve kapı aralıkları kesilerek açılır.
Ölçüler orta sınıf bir çift kabin pikaba göredir: boy 5,37 m, en 1,88 m, yükseklik 1,84 m, dingil açıklığı 3,27 m.

Koordinatlar: X ileri (aracın önü), Y sola, Z yukarı; orijin aracın ortasında, yerde.
    pikap(c)   aracı kurar; kasa tabanının yüksekliğini döndürür
    arazi(c)   toprak zemin, taşlar, kuru otlar, uzak tepeler
"""
import bpy, bmesh, math, random
from mathutils import Vector, noise

from sahneler import put, box, cyl, R

ON_DINGIL, ARKA_DINGIL, TEKER_Z, TEKER_Y = 1.72, -1.55, 0.395, 0.80
KASA = dict(x0=-2.635, x1=-1.085, y=0.835, taban=0.88)

# kesitler: x, sonra yarım kesitin sekiz noktası (y, z): alt orta, alt dış, marşpiyel, en geniş, omuz, üst dış, üst iç, üst orta
KESIT = [
    ( 2.66, (0, 0.50), (0.55, 0.50), (0.70, 0.56), (0.78, 0.78), (0.76, 0.96), (0.66, 1.00), (0.35, 1.02), (0, 1.03)),
    ( 2.56, (0, 0.44), (0.74, 0.44), (0.86, 0.52), (0.90, 0.78), (0.88, 1.00), (0.80, 1.04), (0.42, 1.06), (0, 1.07)),
    ( 2.25, (0, 0.40), (0.84, 0.40), (0.92, 0.50), (0.935, 0.80), (0.92, 1.05), (0.84, 1.09), (0.44, 1.11), (0, 1.12)),
    ( 1.72, (0, 0.38), (0.86, 0.38), (0.93, 0.48), (0.94, 0.80), (0.925, 1.10), (0.85, 1.13), (0.45, 1.15), (0, 1.16)),
    ( 1.15, (0, 0.36), (0.87, 0.36), (0.93, 0.46), (0.94, 0.80), (0.925, 1.15), (0.86, 1.17), (0.45, 1.185), (0, 1.19)),
    ( 0.98, (0, 0.36), (0.87, 0.36), (0.93, 0.46), (0.94, 0.80), (0.925, 1.17), (0.84, 1.20), (0.45, 1.215), (0, 1.22)),      # ön cam altı
    ( 0.40, (0, 0.36), (0.87, 0.36), (0.93, 0.46), (0.94, 0.80), (0.925, 1.18), (0.74, 1.72), (0.40, 1.795), (0, 1.81)),      # tavan önü
    (-0.14, (0, 0.36), (0.87, 0.36), (0.93, 0.46), (0.94, 0.80), (0.925, 1.185), (0.745, 1.745), (0.40, 1.82), (0, 1.835)),
    (-0.26, (0, 0.36), (0.87, 0.36), (0.93, 0.46), (0.94, 0.80), (0.925, 1.185), (0.745, 1.745), (0.40, 1.82), (0, 1.835)),
    (-0.78, (0, 0.36), (0.87, 0.36), (0.93, 0.46), (0.94, 0.80), (0.925, 1.19), (0.74, 1.73), (0.40, 1.80), (0, 1.815)),       # tavan arkası
    (-0.98, (0, 0.36), (0.87, 0.36), (0.93, 0.46), (0.94, 0.80), (0.925, 1.20), (0.86, 1.27), (0.45, 1.29), (0, 1.295)),       # arka cam altı
    (-1.03, (0, 0.38), (0.87, 0.38), (0.93, 0.48), (0.94, 0.80), (0.93, 1.20), (0.915, 1.335), (0.855, 1.335), (0, 1.335)),    # kasa önü
    (-1.55, (0, 0.42), (0.87, 0.42), (0.93, 0.52), (0.94, 0.82), (0.93, 1.20), (0.915, 1.335), (0.855, 1.335), (0, 1.335)),
    (-2.50, (0, 0.50), (0.86, 0.50), (0.92, 0.60), (0.935, 0.84), (0.925, 1.20), (0.91, 1.335), (0.85, 1.335), (0, 1.335)),
    (-2.66, (0, 0.54), (0.80, 0.54), (0.87, 0.62), (0.89, 0.84), (0.88, 1.19), (0.865, 1.325), (0.81, 1.33), (0, 1.33)),
    (-2.71, (0, 0.58), (0.68, 0.58), (0.76, 0.66), (0.80, 0.84), (0.79, 1.17), (0.77, 1.30), (0.70, 1.31), (0, 1.31)),
]
I_COWL, I_TAVAN_ON, I_B1, I_B2, I_TAVAN_ARKA, I_CAM_ALT = 5, 6, 7, 8, 9, 10

def malzemeler():
    from urunfilmi import pbr
    M = {}
    # mat kamuflaj kaplama: üç gri ton, alt kısımlarda toz
    k = bpy.data.materials.new('kaplama'); k.use_nodes = True; nt = k.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.46
    tc = nt.nodes.new('ShaderNodeTexCoord'); vr = nt.nodes.new('ShaderNodeTexVoronoi'); vr.inputs['Scale'].default_value = 4.6; vr.inputs['Randomness'].default_value = 1.0
    bozma = nt.nodes.new('ShaderNodeTexNoise'); bozma.inputs['Scale'].default_value = 2.4; bozma.inputs['Detail'].default_value = 1.5
    kar = nt.nodes.new('ShaderNodeMixRGB'); kar.inputs['Fac'].default_value = 0.16; nt.links.new(tc.outputs['Object'], kar.inputs['Color1']); nt.links.new(tc.outputs['Object'], bozma.inputs['Vector']); nt.links.new(bozma.outputs['Color'], kar.inputs['Color2'])
    nt.links.new(kar.outputs['Color'], vr.inputs['Vector']); ay = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(vr.outputs['Color'], ay.inputs['Color'])
    cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'; e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0.16, 0.158, 0.15, 1); e[1].position = 0.34; e[1].color = (0.085, 0.086, 0.088, 1)
    for pos, col in ((0.58, (0.045, 0.046, 0.05, 1)), (0.78, (0.115, 0.112, 0.105, 1))):
        el = e.new(pos); el.color = col
    nt.links.new(ay.outputs[0], cr.inputs['Fac'])
    sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.35; mr.inputs['From Max'].default_value = 1.05; mr.inputs['To Min'].default_value = 0.62; mr.inputs['To Max'].default_value = 0.0
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 5.5; n2.inputs['Detail'].default_value = 6; nt.links.new(tc.outputs['Object'], n2.inputs['Vector'])
    ml = nt.nodes.new('ShaderNodeMath'); ml.operation = 'MULTIPLY'; nt.links.new(sp.outputs['Z'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], ml.inputs[0]); nt.links.new(n2.outputs['Fac'], ml.inputs[1])
    mx = nt.nodes.new('ShaderNodeMixRGB'); mx.inputs['Color2'].default_value = (0.115, 0.095, 0.07, 1); nt.links.new(ml.outputs['Value'], mx.inputs['Fac']); nt.links.new(cr.outputs['Color'], mx.inputs['Color1'])
    nt.links.new(mx.outputs['Color'], b.inputs['Base Color'])
    rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.42; rr.inputs['To Max'].default_value = 0.8; nt.links.new(ml.outputs['Value'], rr.inputs['Value']); nt.links.new(rr.outputs['Result'], b.inputs['Roughness'])
    M['kaplama'] = k
    M['cam'] = pbr('oto-cam', (0.004, 0.005, 0.006), 0.015, kenar=0.0, spec=0.6)
    M['siyah'] = pbr('oto-plastik', (0.017, 0.017, 0.018), 0.58, kenar=0.0, puruz=0.15, puruz_olcek=900)
    M['astar'] = pbr('kasa-astar', (0.014, 0.014, 0.015), 0.82, kenar=0.0, puruz=0.6, puruz_olcek=420)
    M['alt'] = pbr('sasi', (0.01, 0.01, 0.01), 0.9, kenar=0.0)
    M['lastik'] = pbr('lastik', (0.014, 0.014, 0.015), 0.88, kenar=0.0, puruz=0.5, puruz_olcek=160)
    M['jant'] = pbr('jant', (0.05, 0.052, 0.056), 0.34, metal=1.0, kenar=0.0)
    M['disk'] = pbr('fren-diski', (0.2, 0.2, 0.2), 0.45, metal=1.0, kenar=0.0)
    M['tampon'] = pbr('tampon', (0.16, 0.165, 0.17), 0.3, metal=0.9, kenar=0.0, oynama=0.05)
    M['stop'] = pbr('stop', (0.075, 0.002, 0.003), 0.12, kenar=0.0, spec=0.7, kaplama=0.6)
    M['far'] = pbr('far', (0.5, 0.52, 0.55), 0.05, metal=0.6, kenar=0.0, spec=1.0, kaplama=1.0)
    M['plaka'] = pbr('plaka', (0.55, 0.55, 0.54), 0.5, kenar=0.0)
    M['basamak'] = pbr('basamak', (0.42, 0.43, 0.44), 0.42, metal=1.0, kenar=0.0, puruz=0.2, puruz_olcek=700)
    return M

def _govde(c, M):
    """Kesitlerden örülen gövde yüzeyi. Malzeme sırası: 0 kaplama, 1 cam, 2 siyah, 3 alt."""
    bm = bmesh.new(); halkalar = []
    for k in KESIT:
        x, pts = k[0], k[1:]
        sol = [bm.verts.new((x, y, z)) for y, z in pts]
        sag = [bm.verts.new((x, -y, z)) for y, z in pts[-2:0:-1]]                     # aynadaki yarım: 6 … 1
        halkalar.append(sol + sag)
    n = len(halkalar[0]); katman = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
    def parca(j): return j if j < 7 else 13 - j                                       # halka parçasının yarım kesitteki sırası (0–6)
    for i in range(len(halkalar) - 1):
        a, b = halkalar[i], halkalar[i + 1]
        for j in range(n):
            f = bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j])); p = parca(j); m = 0
            if p == 0: m = 3
            elif p == 4 and i in (I_TAVAN_ON, I_B2): m = 1                                # yan camlar
            elif p == 4 and i in (I_COWL, I_B1): m = 2                                    # A direği yanı, B direği
            elif p in (5, 6) and i == I_COWL: m = 1                                       # ön cam (arka cam ayrı paneldir)
            f.material_index = m
    for uc in (halkalar[0], halkalar[-1]):                                                # ön ve arka kapak
        orta = bm.verts.new((uc[0].co.x + (0.02 if uc is halkalar[0] else -0.02), 0, 0.8))
        for j in range(n): bm.faces.new((uc[j], uc[(j + 1) % n], orta) if uc is halkalar[-1] else (uc[(j + 1) % n], uc[j], orta))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # keskin kalması gereken hatlar
    def kenar(v1, v2): return bm.edges.get((v1, v2))
    for i in range(len(halkalar) - 1):
        a, b = halkalar[i], halkalar[i + 1]
        for j in range(n):
            e = kenar(a[j], b[j]); p = j if j <= 7 else 14 - j
            if e is None: continue
            if p == 1: e[katman] = 0.75                                                   # alt kenar
            elif p == 4: e[katman] = 0.45                                                 # omuz hattı
            elif p in (5, 6) and i >= 11: e[katman] = 0.9                                 # kasa kenarı
            elif p == 5 and I_COWL <= i <= I_TAVAN_ARKA: e[katman] = 0.85                 # tavan kenarı ve direkler
            elif p == 6 and I_TAVAN_ON <= i < I_TAVAN_ARKA: e[katman] = 0.2
    for i, sertlik in ((I_COWL, 0.6), (I_TAVAN_ON, 0.75), (I_TAVAN_ARKA, 0.85), (I_CAM_ALT, 0.9), (I_CAM_ALT + 1, 0.9), (len(halkalar) - 2, 0.8), (1, 0.5)):
        for j in range(n):
            p = j if j <= 7 else 14 - j
            if i in (I_COWL, I_TAVAN_ON, I_TAVAN_ARKA) and p < 4: continue                 # kabin hatları yalnızca omuzdan yukarıda keskin
            e = kenar(halkalar[i][j], halkalar[i][(j + 1) % n])
            if e is not None: e[katman] = sertlik
    me = bpy.data.meshes.new('govde'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('pikap-govde', me); put(o, c)
    for ad in ('kaplama', 'cam', 'siyah', 'alt', 'astar'): o.data.materials.append(M[ad])
    return o

def _uygula(o, mod):
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=mod.name)

def _kes(o, kesici):
    md = o.modifiers.new('kes', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = kesici; md.solver = 'EXACT'
    if hasattr(md, 'material_mode'): md.material_mode = 'TRANSFER'                      # kesilen yüzler kesicinin malzemesini alır
    _uygula(o, md)
    bpy.data.objects.remove(kesici, do_unlink=True)

def _duz(o):
    for p in o.data.polygons: p.use_smooth = False
    return o

def _teker(c, M, x, yan):
    """Lastik (kesiti döndürülerek), çok kollu jant, fren diski."""
    bm = bmesh.new(); kesit = [(0.255, -0.105), (0.30, -0.132), (0.355, -0.135), (0.388, -0.118), (0.397, -0.085), (0.400, 0.0), (0.397, 0.085), (0.388, 0.118), (0.355, 0.135), (0.30, 0.132), (0.255, 0.105)]
    vs = [bm.verts.new((r, y, 0)) for r, y in kesit]
    for a, b in zip(vs, vs[1:]): bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0, 0, 0), axis=(0, 1, 0), angle=2 * math.pi, steps=72, use_merge=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new('lastik'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    parcalar = []; l = bpy.data.objects.new('lastik', me); l.data.materials.append(M['lastik']); put(l, c); parcalar.append(l)
    dis = yan * 0.075                                                                    # jantın dış yüzü
    parcalar.append(cyl(0.258, (0, yan * 0.10, 0), (0, yan * -0.10, 0), M['jant'], c, verts=64, name='jant-yatak'))
    parcalar.append(_duz(cyl(0.262, (0, dis, 0), (0, dis + yan * 0.02, 0), M['jant'], c, verts=64, name='jant-dudak')))
    parcalar.append(_duz(cyl(0.235, (0, dis - yan * 0.03, 0), (0, dis + yan * 0.021, 0), M['alt'], c, verts=64, name='jant-ic')))
    for k in range(10):
        a = k * math.pi / 5
        parcalar.append(box((0.19, 0.028, 0.03), (math.cos(a) * 0.15, dis + yan * 0.012, math.sin(a) * 0.15), M['jant'], c, rot=(0, -a, 0), bevel=0.006, name='kol'))
    parcalar.append(_duz(cyl(0.062, (0, dis, 0), (0, dis + yan * 0.03, 0), M['jant'], c, verts=32, name='gobek')))
    parcalar.append(_duz(cyl(0.17, (0, yan * 0.02, 0), (0, yan * 0.035, 0), M['disk'], c, verts=48, name='disk')))
    for p in parcalar: p.location = Vector(p.location) + Vector((x, yan * TEKER_Y, TEKER_Z))

def pikap(c):
    M = malzemeler(); g = _govde(c, M)
    sd = g.modifiers.new('yumusat', 'SUBSURF'); sd.levels = 2; sd.render_levels = 2; _uygula(g, sd)
    # kesimler: kasa boşluğu, çamurluk yuvaları, kapı aralıkları
    K = KASA
    _kes(g, box((K['x1'] - K['x0'], 2 * K['y'], 1.0), ((K['x0'] + K['x1']) / 2, 0, K['taban'] + 0.5), M['astar'], c, bevel=0, name='kasa-bosluk'))
    for x in (ON_DINGIL, ARKA_DINGIL):
        for yan in (-1, 1):
            _kes(g, _duz(cyl(0.462, (x, yan * 0.52, TEKER_Z), (x, yan * 1.2, TEKER_Z), M['alt'], c, verts=72, name='yuva')))
    for x in (0.99, -0.20, -0.975):
        for yan in (-1, 1):
            _kes(g, box((0.007, 0.5, 0.80), (x, yan * 1.0, 0.79), M['alt'], c, bevel=0, name='aralik'))
    for p in g.data.polygons: p.use_smooth = True
    try: g.data.set_sharp_from_angle(angle=R(38))
    except Exception: pass
    # çamurluk kaplamaları: yuvanın çevresinde siyah plastik yay
    for x in (ON_DINGIL, ARKA_DINGIL):
        for yan in (-1, 1):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.487, minor_radius=0.038, major_segments=72, minor_segments=12, location=(x, yan * 0.94, TEKER_Z), rotation=(R(90), 0, 0))
            t = bpy.context.object; t.name = 'davlumbaz'; bm = bmesh.new(); bm.from_mesh(t.data)
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.06], context='VERTS'); bm.to_mesh(t.data); bm.free()   # yerel y = dünya z
            t.scale = (1, 1, 0.75); bpy.ops.object.shade_smooth(); t.data.materials.append(M['siyah']); put(t, c)
            _teker(c, M, x, yan)
    # kasa: nervürlü taban, yan kenar kapakları, teker davlumbazları
    uz = K['x1'] - K['x0']; ox = (K['x0'] + K['x1']) / 2
    for i in range(int(2 * K['y'] / 0.11)):
        box((uz - 0.02, 0.05, 0.014), (ox, -K['y'] + 0.065 + i * 0.11, K['taban'] + 0.006), M['astar'], c, bevel=0.004, name='nervur')
    for yan in (-1, 1):
        box((uz + 0.06, 0.085, 0.018), (ox, yan * 0.885, 1.345), M['siyah'], c, bevel=0.006, name='kenar-kapak')
        box((0.78, 0.2, 0.2), (ARKA_DINGIL, yan * (K['y'] - 0.09), K['taban'] + 0.1), M['astar'], c, bevel=0.04, name='ic-davlumbaz')
    box((0.085, 1.72, 0.018), (K['x0'] - 0.02, 0, 1.338), M['siyah'], c, bevel=0.006, name='kapak-ustu')
    # arka: stop lambaları, tampon, basamak, boş plaka, kapak kolu
    for yan in (-1, 1):
        box((0.07, 0.12, 0.36), (-2.668, yan * 0.80, 1.03), M['stop'], c, bevel=0.025, name='stop')
        box((0.03, 0.10, 0.07), (-2.72, yan * 0.80, 0.93), M['far'], c, bevel=0.01, name='geri-vites')
    box((0.20, 1.80, 0.17), (-2.74, 0, 0.60), M['tampon'], c, bevel=0.035, name='arka-tampon')
    box((0.13, 1.10, 0.02), (-2.75, 0, 0.693), M['siyah'], c, bevel=0.005, name='basamak-pedi')
    box((0.012, 0.50, 0.11), (-2.722, 0, 0.80), M['plaka'], c, bevel=0.003, name='plaka')
    box((0.03, 0.2, 0.05), (-2.715, 0, 1.2), M['alt'], c, bevel=0.008, name='kapak-kolu')
    box((0.02, 0.24, 0.018), (-0.845, 0, 1.745), M['stop'], c, bevel=0.005, name='ucuncu-stop')
    box((0.014, 1.12, 0.33), (-0.897, 0, 1.53), M['cam'], c, rot=(0, R(21.8), 0), bevel=0.006, name='arka-cam')
    box((0.012, 1.18, 0.39), (-0.889, 0, 1.53), M['siyah'], c, rot=(0, R(21.8), 0), bevel=0.006, name='arka-cam-cercevesi')
    # yanlar: kapı kolları, aynalar, yan basamaklar
    for yan in (-1, 1):
        for x in (0.30, -0.62):
            box((0.15, 0.022, 0.032), (x, yan * 0.935, 1.075), M['siyah'], c, bevel=0.008, name='kol')
        box((0.11, 0.21, 0.135), (1.02, yan * 1.045, 1.265), M['siyah'], c, bevel=0.035, name='ayna'); box((0.05, 0.12, 0.03), (1.0, yan * 0.94, 1.22), M['siyah'], c, bevel=0.008, name='ayna-kolu')
        box((1.95, 0.15, 0.035), (0.12, yan * 0.985, 0.36), M['basamak'], c, bevel=0.01, name='yan-basamak')
        box((0.06, 0.34, 0.11), (2.60, yan * 0.66, 0.90), M['far'], c, bevel=0.015, name='far')
    box((0.05, 1.0, 0.2), (2.655, 0, 0.84), M['siyah'], c, bevel=0.01, name='izgara'); box((0.16, 1.84, 0.2), (2.62, 0, 0.55), M['siyah'], c, bevel=0.04, name='on-tampon')
    box((4.4, 1.5, 0.22), (0.0, 0, 0.42), M['alt'], c, bevel=0.02, name='sasi')
    cyl(0.004, (-0.62, 0.42, 1.80), (-0.86, 0.42, 2.22), M['siyah'], c, verts=8, name='anten'); box((0.09, 0.04, 0.035), (-0.60, 0.42, 1.815), M['siyah'], c, bevel=0.01, name='anten-tabani')
    return K['taban'] + 0.013

def yukseklik(x, y):
    d = math.hypot(x, y); k = min(1.0, max(0.0, (d - 55) / 220)); k = k * k * (3 - 2 * k)
    return k * (26 * noise.fractal(Vector((x / 260, y / 260, 0.7)), 1.0, 2.0, 5) + 9) + 0.035 * noise.noise(Vector((x / 3.0, y / 3.0, 0)))

def arazi(c):
    """Kuru toprak ve çakıl zemin, dağınık taşlar, seyrek kuru ot, ufukta tepeler."""
    m = bpy.data.materials.new('toprak'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.94
    tc = nt.nodes.new('ShaderNodeTexCoord'); n1 = nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.22; n1.inputs['Detail'].default_value = 9; n1.inputs['Roughness'].default_value = 0.6
    cr = nt.nodes.new('ShaderNodeValToRGB'); e = cr.color_ramp.elements; e[0].position = 0.32; e[0].color = (0.075, 0.06, 0.042, 1); e[1].position = 0.7; e[1].color = (0.19, 0.16, 0.115, 1)
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 38; n2.inputs['Detail'].default_value = 7
    n3 = nt.nodes.new('ShaderNodeTexVoronoi'); n3.inputs['Scale'].default_value = 55
    ad = nt.nodes.new('ShaderNodeMath'); ad.operation = 'ADD'; bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.9; bp.inputs['Distance'].default_value = 0.03
    for nd in (n1, n2, n3): nt.links.new(tc.outputs['Object'], nd.inputs['Vector'])
    nt.links.new(n1.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(n2.outputs['Fac'], ad.inputs[0]); nt.links.new(n3.outputs['Distance'], ad.inputs[1]); nt.links.new(ad.outputs['Value'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    me = bpy.data.meshes.new('arazi'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=220, y_segments=220, size=700)
    for v in bm.verts: v.co.z = yukseklik(v.co.x, v.co.y)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('arazi', me); o.data.materials.append(m); put(o, c)
    from urunfilmi import pbr
    tas = pbr('tas', (0.16, 0.145, 0.12), 0.9, kenar=0.0, puruz=0.8, puruz_olcek=60); ot = pbr('kuru-ot', (0.3, 0.24, 0.1), 0.85, kenar=0.0)
    rnd = random.Random(4)
    for i in range(260):
        x, y = rnd.uniform(-14, 14), rnd.uniform(-14, 14)
        if abs(x) < 3.2 and abs(y) < 1.4: continue
        r = rnd.uniform(0.012, 0.05) * (1 + 2.5 * (rnd.random() < 0.06))
        bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=2, location=(x, y, yukseklik(x, y) + r * 0.3)); s = bpy.context.object
        s.scale = (rnd.uniform(0.8, 1.5), rnd.uniform(0.8, 1.3), rnd.uniform(0.45, 0.8)); s.rotation_euler = (0, 0, rnd.uniform(0, 6.28)); s.data.materials.append(tas); bpy.ops.object.shade_smooth(); put(s, c)
    for i in range(170):
        x, y = rnd.uniform(-22, 22), rnd.uniform(-22, 22)
        if abs(x) < 3.6 and abs(y) < 1.8: continue
        for k in range(rnd.randint(5, 9)):
            a = rnd.uniform(0, 6.28); h = rnd.uniform(0.12, 0.34); e = rnd.uniform(0.15, 0.6)
            ust = (x + math.cos(a) * h * e, y + math.sin(a) * h * e, yukseklik(x, y) + h)
            cyl(0.0035, (x + rnd.uniform(-0.04, 0.04), y + rnd.uniform(-0.04, 0.04), yukseklik(x, y)), ust, ot, c, verts=4, name='ot')
    return o
