"""Drone Shield filmi için 3B arka plan plakaları (Blender / Cycles, CPU).

Kullanım (bpy kurulu bir Python ile):
    python render/3d/sahneler.py gemi   --kalite taslak|final [--cikti KLASOR]
    python render/3d/sahneler.py rafineri --kalite taslak|final

Her sahne iki katman üretir:
    <ad>-arka.jpg   gökyüzü, deniz/uzak plan (film motoru bunu hareketlendirir)
    <ad>-on.png     güverte / kule ve yakın plan, saydam zeminli
ve taretin oturacağı noktanın piksel koordinatlarını <ad>-capa.json dosyasına yazar.
Taretin kendisi 3B değildir; gerçek fotoğraf kesmesi film motorunda bu noktaya bindirilir.
"""
import bpy, math, json, sys, os, time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

R = math.radians
SPRITE_PX_PER_M = 756.0      # taret-yakin-cut.png: 1 m ≈ 756 px (tüfek boyu ~1 m)
MOUNT_DROP_M = 0.1455        # dönüş ekseninden taban flanşına mesafe

# ---------------------------------------------------------------- yardımcılar
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene

def coll(name):
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c

def put(obj, c):
    for old in list(obj.users_collection): old.objects.unlink(obj)
    c.objects.link(obj); return obj

def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0, bump=0.0, bump_scale=60.0, spec=0.5, vary=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = spec
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = strength
    if bump > 0 or vary > 0:
        tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = bump_scale; nz.inputs['Detail'].default_value = 6
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        if bump > 0:
            bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.01
            nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
        if vary > 0:   # büyük ölçekli leke: boya eskimesi
            nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 1.3; nz2.inputs['Detail'].default_value = 8
            nt.links.new(tc.outputs['Object'], nz2.inputs['Vector'])
            mix = nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = vary
            mix.inputs['Color1'].default_value = (*color, 1); nt.links.new(nz2.outputs['Fac'], mix.inputs['Color2'])
            nt.links.new(mix.outputs['Color'], b.inputs['Base Color'])
    return m

def box(size, loc, m, c, rot=(0, 0, 0), bevel=0.012, name='box'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new('bev', 'BEVEL'); bv.width = bevel; bv.segments = 2
    o.data.materials.append(m); return put(o, c)

def cyl(r, p0, p1, m, c, verts=20, name='cyl'):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=verts, location=(p0 + p1) / 2); o = bpy.context.object; o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); bpy.ops.object.shade_smooth()
    o.data.materials.append(m); return put(o, c)

def sphere(r, loc, m, c, name='sph'):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=12); o = bpy.context.object; o.name = name
    bpy.ops.object.shade_smooth(); o.data.materials.append(m); return put(o, c)

def torus(R_, r, loc, rot, m, c):
    bpy.ops.mesh.primitive_torus_add(major_radius=R_, minor_radius=r, location=loc, rotation=rot); o = bpy.context.object
    bpy.ops.object.shade_smooth(); o.data.materials.append(m); return put(o, c)

def point_light(loc, power, color, c, radius=0.05):
    l = bpy.data.lights.new('pl', 'POINT'); l.energy = power; l.color = color; l.shadow_soft_size = radius
    o = bpy.data.objects.new('pl', l); c.objects.link(o); o.location = loc; return o

def sky(elev_deg, rot_deg, strength=1.0, aerosol=1.0, sun_intensity=1.0, altitude=0):
    sc = bpy.context.scene; w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; nt = w.node_tree
    s = nt.nodes.new('ShaderNodeTexSky'); s.sky_type = 'MULTIPLE_SCATTERING'
    s.sun_elevation = R(elev_deg); s.sun_rotation = R(rot_deg); s.sun_disc = True; s.sun_intensity = sun_intensity
    s.aerosol_density = aerosol; s.altitude = altitude
    bg = nt.nodes['Background']; bg.inputs['Strength'].default_value = strength; nt.links.new(s.outputs[0], bg.inputs['Color'])

def camera(loc, target, lens, fstop=None, focus=None):
    sc = bpy.context.scene; cd = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); sc.camera = co
    co.location = loc; d = Vector(target) - Vector(loc); co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cd.lens = lens; cd.sensor_width = 36
    cd.clip_start = 0.05; cd.clip_end = 30000
    if fstop: cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop; cd.dof.focus_distance = focus
    bpy.context.view_layer.update(); return co

def setup(kalite, exposure=0.0, look='AgX - Medium High Contrast'):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    final = kalite == 'final'
    sc.render.resolution_x, sc.render.resolution_y = (1920, 1080) if final else (960, 540); sc.render.resolution_percentage = 100
    sc.cycles.samples = 128 if final else 40; sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.cycles.max_bounces = 6; sc.cycles.sample_clamp_indirect = 8.0; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = look
    except Exception: pass
    sc.view_settings.exposure = exposure
    return sc

def px(point):
    sc = bpy.context.scene; v = world_to_camera_view(sc, sc.camera, Vector(point))
    return [round(v.x * 1920, 1), round((1 - v.y) * 1080, 1), round(v.z, 3)]

def px_per_m(point):
    """taretin derinliğinde 1 m'nin (kameraya dik) kaç piksel ettiği, 1920 px genişlikte"""
    sc = bpy.context.scene; cam = sc.camera; right = cam.matrix_world.to_quaternion() @ Vector((1, 0, 0))
    a = world_to_camera_view(sc, cam, Vector(point)); b = world_to_camera_view(sc, cam, Vector(point) + right)
    return abs(b.x - a.x) * 1920

def render_layers(name, out, fg, bg, extra):
    sc = bpy.context.scene; os.makedirs(out, exist_ok=True); t0 = time.time()
    def vis(c, on):
        for o in c.all_objects: o.visible_camera = on
    # arka: ön plan kameraya görünmez (ışığı ve gölgesi kalır)
    vis(fg, False); vis(bg, True); sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 93
    sc.render.filepath = os.path.join(out, f'{name}-arka.jpg'); bpy.ops.render.render(write_still=True)
    # ön: arka plan kameraya görünmez, zemin saydam
    vis(fg, True); vis(bg, False); sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'; sc.render.image_settings.compression = 60
    sc.render.filepath = os.path.join(out, f'{name}-on.png'); bpy.ops.render.render(write_still=True)
    extra['render_sn'] = round(time.time() - t0, 1)
    json.dump(extra, open(os.path.join(out, f'{name}-capa.json'), 'w'), indent=1)
    print('CAPA', json.dumps(extra))

# ---------------------------------------------------------------- gemi
def gemi(kalite, out):
    reset(); sc = setup(kalite, exposure=-0.45)
    FG, BG = coll('FG'), coll('BG')
    gri = mat('gri', (0.27, 0.30, 0.33), rough=0.48, bump=0.25, bump_scale=140, vary=0.35)
    gri2 = mat('gri2', (0.20, 0.225, 0.25), rough=0.55, bump=0.2, bump_scale=140, vary=0.3)
    guverte = mat('guverte', (0.05, 0.055, 0.06), rough=0.8, bump=0.9, bump_scale=900, vary=0.3)
    galvaniz = mat('galvaniz', (0.55, 0.57, 0.6), rough=0.42, metal=0.85)
    sari = mat('sari', (0.62, 0.44, 0.03), rough=0.7)
    kirmizi = mat('kirmizi', (0.45, 0.03, 0.02), rough=0.5)
    turuncu = mat('turuncu', (0.85, 0.22, 0.03), rough=0.6)
    siyah = mat('siyah', (0.02, 0.02, 0.022), rough=0.6)
    cam_isik = mat('cam', (0.02, 0.02, 0.02), rough=0.1, emit=(1.0, 0.72, 0.42), strength=5.0)
    lamba = mat('lamba', (1, 1, 1), emit=(1.0, 0.78, 0.5), strength=60.0)
    deniz = mat('deniz', (0.006, 0.02, 0.034), rough=0.05, spec=0.9, bump=0.35, bump_scale=2.2)

    # deniz: yakında dalgalı okyanus, ufka kadar düz devam
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0)); oc = bpy.context.object; oc.name = 'okyanus'
    m = oc.modifiers.new('Ocean', 'OCEAN'); m.geometry_mode = 'GENERATE'; m.resolution = 18; m.spatial_size = 180; m.size = 1.0
    m.repeat_x = 5; m.repeat_y = 5; m.wave_scale = 1.4; m.choppiness = 0.8; m.wind_velocity = 9; m.wave_alignment = 0.35; m.wave_direction = R(40); m.random_seed = 4; m.time = 2.0
    oc.location = (-450 + 0, -450 + 120, 0); oc.data.materials.append(deniz); bpy.ops.object.shade_smooth(); put(oc, BG)
    bpy.ops.mesh.primitive_plane_add(size=60000, location=(0, 0, -0.35)); far = bpy.context.object; far.data.materials.append(deniz); put(far, BG)

    # uzakta refakat gemisi (silüet)
    sx, sy = -520, 1250
    for size, loc in [((120, 14, 7), (0, 0, 3.5)), ((34, 11, 9), (-6, 0, 11.5)), ((12, 8, 6), (-8, 0, 19)), ((16, 9, 4), (26, 0, 9))]:
        box(size, (sx + loc[0], sy + loc[1], loc[2]), siyah, BG, rot=(0, 0, R(25)), bevel=0)
    cyl(0.5, (sx - 8, sy, 22), (sx - 8, sy, 36), siyah, BG)
    for i in range(5): sphere(0.5, (sx - 40 + i * 18, sy - 7.5, 9), lamba, BG)

    # güverte ve borda
    box((4.5, 90, 0.5), (-0.35, 20, 3.75), guverte, FG, bevel=0)          # yürüme yolu: x -2.6 … 1.9
    box((0.14, 90, 0.2), (-2.55, 20, 4.1), gri2, FG)                       # borda eşiği
    box((0.1, 90, 0.004), (-2.15, 20, 4.003), sari, FG, bevel=0)           # sarı emniyet çizgisi
    # vardavela
    for i in range(-6, 44):
        y = i * 1.5; cyl(0.021, (-2.55, y, 4.0), (-2.55, y, 5.06), galvaniz, FG, verts=12)
    cyl(0.024, (-2.55, -10, 5.06), (-2.55, 66, 5.06), galvaniz, FG, verts=12)
    for z in (4.40, 4.73): cyl(0.008, (-2.55, -10, z), (-2.55, 66, z), galvaniz, FG, verts=8)

    # güverte evi (sancak tarafında duvar) ve üst güverte çıkıntısı
    box((6, 26, 4.6), (4.9, 9, 6.3), gri, FG, bevel=0.02)                  # duvar yüzü x=1.9
    box((1.25, 26.4, 0.16), (1.3, 9, 6.72), gri2, FG)                      # çıkıntı
    for i in range(0, 18):
        y = -3.5 + i * 1.5; cyl(0.019, (0.72, y, 6.8), (0.72, y, 7.75), galvaniz, FG, verts=10)
    cyl(0.022, (0.72, -4, 7.75), (0.72, 22.2, 7.75), galvaniz, FG, verts=10); cyl(0.008, (0.72, -4, 7.3), (0.72, 22.2, 7.3), galvaniz, FG, verts=8)
    # kapı, lombozlar, borular, yangın dolabı, can simidi, armatürler
    box((0.08, 0.95, 1.95), (1.88, 7.2, 5.05), gri2, FG, bevel=0.03); box((0.05, 0.8, 1.8), (1.85, 7.2, 5.05), gri, FG, bevel=0.03)
    torus(0.12, 0.014, (1.80, 7.2, 5.1), (0, R(90), 0), galvaniz, FG)
    for y in (4.6, 10.2, 12.4, 16.0):
        torus(0.2, 0.03, (1.885, y, 5.75), (0, R(90), 0), galvaniz, FG); cyl(0.19, (1.89, y, 5.75), (1.905, y, 5.75), cam_isik, FG)
    for z, r in ((6.45, 0.045), (6.32, 0.03), (6.22, 0.03)): cyl(r, (1.84, -4, z), (1.84, 22, z), gri2, FG, verts=10)
    box((0.22, 0.6, 0.75), (1.79, 9.1, 5.0), kirmizi, FG, bevel=0.02)
    torus(0.3, 0.06, (1.84, 5.6, 5.2), (0, R(90), 0), turuncu, FG)
    for y in (2.5, 6.0, 9.5, 13.0, 16.5, 20.0):
        box((0.16, 0.1, 0.07), (1.72, y, 6.6), gri2, FG, bevel=0.01); sphere(0.045, (1.72, y, 6.55), lamba, FG)
        point_light((1.6, y, 6.45), 55, (1.0, 0.72, 0.42), FG, radius=0.06)
    # baş tarafta uzak ayrıntılar: babalar, havalandırma, sereni
    for y in (11.0, 11.5): cyl(0.11, (-1.9, y, 4.0), (-1.9, y, 4.42), gri2, FG); 
    for y in (11.0, 11.5): cyl(0.15, (-1.9, y, 4.42), (-1.9, y, 4.47), gri2, FG)
    box((1.6, 1.2, 1.3), (-0.6, 30, 4.65), gri, FG); cyl(0.035, (0.2, 44, 4), (0.2, 44, 9), gri2, FG)
    box((5, 0.3, 1.1), (-0.3, 38, 4.55), gri, FG)

    # taret kaidesi
    ped = (-0.1, 3.3); top = 5.2745
    cyl(0.25, (*ped, 4.0), (*ped, 4.035), gri2, FG, verts=32); cyl(0.105, (*ped, 4.0), (*ped, top - 0.02), gri, FG, verts=32); cyl(0.15, (*ped, top - 0.025), (*ped, top), gri2, FG, verts=32)
    for k in range(8):
        a = k * math.pi / 4; cyl(0.014, (ped[0] + 0.2 * math.cos(a), ped[1] + 0.2 * math.sin(a), 4.03), (ped[0] + 0.2 * math.cos(a), ped[1] + 0.2 * math.sin(a), 4.055), galvaniz, FG, verts=6)
    pivot = (*ped, top + MOUNT_DROP_M)

    # gökyüzü ve kamera: baş-iskele yönüne, alçak güneşe doğru
    sky(elev_deg=3.0, rot_deg=-42, strength=0.3, aerosol=1.2, sun_intensity=0.6)
    yaw = R(20); cam_loc = (0.3, 0.0, 5.12); fwd = Vector((-math.sin(yaw), math.cos(yaw), math.tan(R(5.0))))
    camera(cam_loc, Vector(cam_loc) + fwd * 10, lens=32, fstop=5.6, focus=3.3)
    info = {'sahne': 'gemi', 'pivot_px': px(pivot), 'kaide_ust_px': px((*ped, top)), 'px_per_m': round(px_per_m(pivot), 1),
            'sprite_olcek': round(px_per_m(pivot) / SPRITE_PX_PER_M, 3), 'ufuk_y': px((cam_loc[0] + fwd.x * 1e6, cam_loc[1] + fwd.y * 1e6, cam_loc[2]))[1]}
    render_layers('gemi', out, FG, BG, info)

# ---------------------------------------------------------------- rafineri
def rafineri(kalite, out):
    import random; rnd = random.Random(11)
    reset(); sc = setup(kalite, exposure=0.15)
    FG, BG = coll('FG'), coll('BG')
    celik = mat('celik', (0.16, 0.17, 0.185), rough=0.5, metal=0.6, bump=0.3, bump_scale=160, vary=0.3)
    galvaniz = mat('galvaniz', (0.5, 0.52, 0.55), rough=0.42, metal=0.85)
    sari = mat('sari', (0.42, 0.30, 0.02), rough=0.6)
    beyaz = mat('beyaz', (0.55, 0.56, 0.56), rough=0.55, vary=0.35)
    gri = mat('gri', (0.22, 0.235, 0.25), rough=0.5, metal=0.3, vary=0.3)
    boru = mat('boru', (0.33, 0.34, 0.35), rough=0.35, metal=0.7)
    zemin = mat('zemin', (0.035, 0.036, 0.038), rough=0.55, bump=0.4, bump_scale=3, vary=0.4)
    siyah = mat('siyah', (0.015, 0.015, 0.017), rough=0.7)
    sodyum = mat('sodyum', (1, 1, 1), emit=(1.0, 0.58, 0.24), strength=260.0)
    led = mat('led', (1, 1, 1), emit=(0.85, 0.93, 1.0), strength=200.0)
    kirmizi_isik = mat('kirmizi_isik', (1, 1, 1), emit=(1.0, 0.08, 0.05), strength=300.0)
    pencere = mat('pencere', (0.02, 0.02, 0.02), emit=(1.0, 0.8, 0.55), strength=12.0)
    alev = mat('alev', (1, 1, 1), emit=(1.0, 0.45, 0.12), strength=900.0)
    # ızgara zemin: tuğla dokusundan kabartma
    izgara = bpy.data.materials.new('izgara'); izgara.use_nodes = True; nt = izgara.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.07, 0.075, 0.08, 1); b.inputs['Roughness'].default_value = 0.5; b.inputs['Metallic'].default_value = 0.8
    tc = nt.nodes.new('ShaderNodeTexCoord'); br = nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 26; br.inputs['Mortar Size'].default_value = 0.035
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 1.0; bp.inputs['Distance'].default_value = 0.02
    nt.links.new(tc.outputs['Object'], br.inputs['Vector']); nt.links.new(br.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])

    Z = 14.0   # platform kotu
    def lamp(loc, m=sodyum, power=0, c=BG, r=0.14):
        sphere(r, loc, m, c)
        if power: point_light((loc[0], loc[1], loc[2] - 0.3), power, (1.0, 0.6, 0.28) if m is sodyum else (0.85, 0.93, 1.0), c, radius=0.15)
    def rail(p0, p1, c, h=1.06, step=1.25):
        p0, p1 = Vector(p0), Vector(p1); n = max(1, round((p1 - p0).length / step))
        for i in range(n + 1):
            q = p0.lerp(p1, i / n); cyl(0.021, q, q + Vector((0, 0, h)), galvaniz, c, verts=10)
        cyl(0.024, p0 + Vector((0, 0, h)), p1 + Vector((0, 0, h)), galvaniz, c, verts=10); cyl(0.016, p0 + Vector((0, 0, h * 0.5)), p1 + Vector((0, 0, h * 0.5)), galvaniz, c, verts=8)
        box(((p1 - p0).length if abs(p1.x - p0.x) > abs(p1.y - p0.y) else 0.012, 0.012 if abs(p1.x - p0.x) > abs(p1.y - p0.y) else (p1 - p0).length, 0.1), (p0 + p1) / 2 + Vector((0, 0, 0.05)), sari, c, bevel=0)

    # --- ön plan: kule platformu
    box((4.5, 6.6, 0.06), (-0.35, 1.75, Z - 0.03), izgara, FG, bevel=0)
    for x in (-2.6, 1.9):
        box((0.12, 6.6, 0.2), (x, 1.75, Z - 0.16), celik, FG)
    for y in (-1.55, 5.05):
        box((4.6, 0.12, 0.2), (-0.35, y, Z - 0.16), celik, FG)
    rail((-2.6, -1.55, Z), (-2.6, 5.05, Z), FG); rail((-2.6, 5.05, Z), (1.9, 5.05, Z), FG)
    for x, y in ((-2.6, -1.55), (-2.6, 5.05), (1.9, 5.05), (1.9, -1.55)): cyl(0.06, (x, y, Z - 0.2), (x * 1.25, y * 1.1 - 0.3, 0), celik, FG, verts=12)
    box((0.3, 0.2, 0.42), (1.2, 4.85, Z + 0.7), gri, FG, bevel=0.01); cyl(0.02, (1.2, 4.85, Z), (1.2, 4.85, Z + 0.5), boru, FG, verts=10)
    # taret kaidesi
    ped = (-0.1, 3.3); top = Z + 1.2745
    cyl(0.25, (*ped, Z), (*ped, Z + 0.035), celik, FG, verts=32); cyl(0.105, (*ped, Z), (*ped, top - 0.02), gri, FG, verts=32); cyl(0.15, (*ped, top - 0.025), (*ped, top), celik, FG, verts=32)
    pivot = (*ped, top + MOUNT_DROP_M)

    # --- arka plan: tesis
    bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, 0)); g = bpy.context.object; g.data.materials.append(zemin); put(g, BG)
    def kolon(x, y, r, h):
        cyl(r, (x, y, 0), (x, y, h), gri, BG, verts=28); cyl(r * 0.45, (x, y, h), (x, y, h + 3), boru, BG, verts=16)
        z = 8.0
        while z < h - 2:
            cyl(r + 1.1, (x, y, z - 0.08), (x, y, z), celik, BG, verts=28); lamp((x - r - 0.9, y - r - 0.5, z + 1.6), sodyum if rnd.random() < 0.7 else led, power=rnd.choice((0, 220, 320)))
            z += rnd.choice((6.5, 7.5, 9.0))
        cyl(0.12, (x + r + 0.3, y, 0), (x + r + 0.3, y, h - 1), boru, BG, verts=10)
    for x, y, r, h in ((-80, 89, 2.0, 50), (-80, 115, 1.6, 42), (-51, 92, 2.4, 58), (-61, 137, 1.7, 40), (2, 110, 2.1, 52), (14, 134, 1.6, 44), (-118, 120, 1.8, 46), (-150, 150, 1.6, 38)):
        kolon(x, y, r, h)
    def tank(x, y, r, h):
        cyl(r, (x, y, 0), (x, y, h), beyaz, BG, verts=56); cyl(r * 1.005, (x, y, h), (x, y, h + 0.35), celik, BG, verts=56)
        for a in (200, 250, 300, 340): lamp((x + (r + 0.6) * math.cos(R(a)), y + (r + 0.6) * math.sin(R(a)), h + 1.2), sodyum, power=rnd.choice((0, 260)))
    for x, y, r, h in ((-95, 70, 14, 13), (-60, 62, 12, 12), (-128, 96, 16, 14), (-150, 60, 13, 12), (-100, 118, 15, 13), (70, 78, 13, 12), (104, 100, 16, 14), (60, 44, 9, 10)):
        tank(x, y, r, h)
    for i in range(5):   # küresel tanklar
        x, y = -112 + i * 15, 72
        sphere(6.2, (x, y, 8.6), beyaz, BG)
        for a in range(0, 360, 60): cyl(0.22, (x + 5.2 * math.cos(R(a)), y + 5.2 * math.sin(R(a)), 0), (x + 4.6 * math.cos(R(a)), y + 4.6 * math.sin(R(a)), 7.5), celik, BG, verts=10)
        lamp((x, y - 6.6, 4.5), sodyum, power=260)
    def boru_rafi(p0, p1, n=7, h=6.5, w=5.0):
        p0, p1 = Vector(p0), Vector(p1); d = (p1 - p0); L = d.length; u = d.normalized(); v = Vector((-u.y, u.x, 0))
        k = int(L // 7)
        for i in range(k + 1):
            q = p0 + u * (i * 7.0)
            for s_ in (-1, 1): cyl(0.14, q + v * (s_ * w / 2), q + v * (s_ * w / 2) + Vector((0, 0, h + 1.6)), celik, BG, verts=8)
            cyl(0.12, q - v * (w / 2) + Vector((0, 0, h)), q + v * (w / 2) + Vector((0, 0, h)), celik, BG, verts=8)
            cyl(0.12, q - v * (w / 2) + Vector((0, 0, h + 1.5)), q + v * (w / 2) + Vector((0, 0, h + 1.5)), celik, BG, verts=8)
            if i % 3 == 1: lamp(q + v * (w / 2 + 0.3) + Vector((0, 0, h + 1.9)), sodyum, power=rnd.choice((180, 260)))
        for j in range(n):
            off = v * (-w / 2 + 0.4 + j * (w - 0.8) / (n - 1)); rr_ = rnd.choice((0.11, 0.16, 0.2, 0.26))
            cyl(rr_, p0 + off + Vector((0, 0, h + 0.14 + rr_)), p1 + off + Vector((0, 0, h + 0.14 + rr_)), boru, BG, verts=12)
        for j in range(4):
            off = v * (-w / 2 + 0.6 + j * (w - 1.2) / 3); cyl(0.13, p0 + off + Vector((0, 0, h + 1.75)), p1 + off + Vector((0, 0, h + 1.75)), boru, BG, verts=12)
    boru_rafi((-170, 30, 0), (130, 30, 0)); boru_rafi((-12, 30, 0), (-12, 180, 0)); boru_rafi((36, 30, 0), (36, 150, 0), n=5)
    # flare bacası, bacalar, binalar, direkler
    fl = (-170, 271); cyl(0.9, (*fl, 0), (*fl, 78), celik, BG, verts=16)
    for z in range(10, 78, 12): cyl(1.6, (*fl, z - 0.1), (*fl, z), celik, BG, verts=16)
    sphere(2.2, (*fl, 80.5), alev, BG); point_light((*fl, 82), 400000, (1.0, 0.5, 0.18), BG, radius=2.5)
    for x, y, h in ((70, 230, 62), (86, 236, 62), (150, 200, 48)):
        cyl(2.2, (x, y, 0), (x, y, h), gri, BG, verts=24); lamp((x, y, h + 0.6), kirmizi_isik, r=0.5); lamp((x - 2.4, y - 1, h * 0.5), kirmizi_isik, r=0.4)
    for x, y, sx_, sy_, h in ((-30, 58, 16, 9, 5), (52, 64, 12, 8, 4.5), (-118, 44, 20, 10, 6), (88, 52, 14, 9, 5)):
        box((sx_, sy_, h), (x, y, h / 2), gri, BG, bevel=0.05)
        for i in range(int(sx_ // 3)): box((1.3, 0.05, 1.0), (x - sx_ / 2 + 1.6 + i * 3, y - sy_ / 2 - 0.03, h * 0.6), pencere, BG, bevel=0)
    for i in range(26):
        x = -165 + i * 12.5; cyl(0.09, (x, 22, 0), (x, 22, 9), celik, BG, verts=8); lamp((x, 21.4, 9.1), sodyum if i % 4 else led, power=420 if i % 2 == 0 else 0)
    for i in range(14):
        y = 40 + i * 14; cyl(0.09, (-22, y, 0), (-22, y, 9), celik, BG, verts=8); lamp((-21.4, y, 9.1), sodyum, power=420 if i % 2 else 0)

    sky(elev_deg=0.8, rot_deg=-48, strength=0.3, aerosol=1.6, sun_intensity=0.25)
    yaw = R(20); cam_loc = (0.3, 0.0, Z + 1.12); fwd = Vector((-math.sin(yaw), math.cos(yaw), math.tan(R(5.0))))
    camera(cam_loc, Vector(cam_loc) + fwd * 10, lens=32, fstop=5.6, focus=3.3)
    info = {'sahne': 'rafineri', 'pivot_px': px(pivot), 'kaide_ust_px': px((*ped, top)), 'px_per_m': round(px_per_m(pivot), 1),
            'sprite_olcek': round(px_per_m(pivot) / SPRITE_PX_PER_M, 3), 'ufuk_y': px((cam_loc[0] + fwd.x * 1e6, cam_loc[1] + fwd.y * 1e6, cam_loc[2]))[1],
            'alev_px': px((*fl, 81.5)), 'alev_px_per_m': round(px_per_m((*fl, 81.5)), 2)}
    render_layers('rafineri', out, FG, BG, info)

if __name__ == '__main__':
    args = sys.argv[1:]; sahne = args[0] if args else 'gemi'
    kalite = args[args.index('--kalite') + 1] if '--kalite' in args else 'taslak'
    out = args[args.index('--cikti') + 1] if '--cikti' in args else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cikti')
    {'gemi': gemi, 'rafineri': rafineri}[sahne](kalite, out)
