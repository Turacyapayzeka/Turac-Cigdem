"""Gerçekçi çift kabin pikap ve açık arazi (ürün filminin araç sahneleri için). Marka işareti ve plaka yoktur.

Gövde, boy boyunca sık dizilmiş kesitlerden örülen kapalı bir yüzeydir; kesitler ölçü fonksiyonlarından üretilir
(yarım en, kuşak hattı, kaput, tavan, ön ve arka cam düzlemleri). Kabinin içi oyulur, cam açıklıkları gerçek
delikler olarak kesilir; camlar duvarın içinde duran saydam bir kabuktur, içeride koltuklar ve gösterge paneli görünür.
Kasa boşluğu, çamurluk yuvaları, kapı ve kapak aralıkları da kesilerek açılır.

Ölçüler ve oranlar saha fotoğraflarındaki araca göredir: boy 5,37 m, en 1,91 m, yükseklik 1,84 m, dingil açıklığı 3,27 m;
siyah çamurluk kaplamaları, çok kollu koyu jantlar, arazi lastikleri, yan basamaklar, kasa arkasında yelken biçimli bar.

Koordinatlar: X ileri (aracın önü), Y sola, Z yukarı; orijin aracın ortasında, yerde.
    pikap(c)    aracı kurar; kasa tabanının yüksekliğini döndürür
    arazi(c)    çakıllı toprak zemin, taşlar, otlar, uzak tepeler
    bulutlar()  gökyüzüne ince bulut katmanı ekler
"""
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, Matrix, Euler, noise

from sahneler import put, box, cyl, R, mat

ON_DINGIL, ARKA_DINGIL, TEKER_Z, TEKER_Y = 1.72, -1.55, 0.405, 0.805
XA, XO = -2.77, 2.60                       # arka ve ön uç
ZR = 1.375                                 # kasa kenarının üstü
X_AC = -0.945                              # kabin arka duvarının kasa hizasındaki yeri
DUVAR = 0.05                               # kabin duvar kalınlığı
KASA = dict(x0=-2.70, x1=-1.02, y=0.80, taban=0.86)
NG, NK, NT = 14, 6, 14                     # üst kesitte cam, tavan köşesi ve tavan nokta sayıları

# ------------------------------------------------------------------ ölçü fonksiyonları
def egri(noktalar):
    """Verilen noktalardan geçen, salınım yapmayan (tekdüze) kübik eğri."""
    xs = np.array([p[0] for p in noktalar], float); ys = np.array([p[1] for p in noktalar], float)
    h = np.diff(xs); d = np.diff(ys) / h; m = np.zeros_like(xs); m[0] = d[0]; m[-1] = d[-1]
    for i in range(1, len(xs) - 1):
        m[i] = 0.0 if d[i - 1] * d[i] <= 0 else 3 * (h[i - 1] + h[i]) / ((2 * h[i] + h[i - 1]) / d[i - 1] + (h[i] + 2 * h[i - 1]) / d[i])
    def f(x):
        x = min(max(x, xs[0]), xs[-1]); i = max(min(int(np.searchsorted(xs, x, side='right')) - 1, len(xs) - 2), 0)
        t = (x - xs[i]) / h[i]; t2 = t * t; t3 = t2 * t
        return float((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1])
    return f

_en = egri([(XA, 0.948), (-2.3, 0.955), (1.5, 0.955), (1.95, 0.948), (2.25, 0.93), (2.45, 0.905), (XO, 0.875)])
_alt = egri([(XA, 0.62), (-2.10, 0.62), (-1.90, 0.52), (-1.15, 0.48), (2.25, 0.48), (XO, 0.56)])
_kab = egri([(X_AC, 1.305), (0.06, 1.298), (0.90, 1.285), (1.14, 1.27), (1.5, 1.258), (1.9, 1.243), (2.25, 1.218), (2.45, 1.188), (2.55, 1.152), (XO, 1.085)])
_kaput = egri([(0.9, 1.30), (1.14, 1.292), (1.5, 1.283), (1.9, 1.27), (2.25, 1.252), (2.45, 1.226), (2.55, 1.19), (XO, 1.115)])
_tavan = egri([(-0.95, 1.812), (-0.35, 1.835), (0.25, 1.832), (0.75, 1.80)])

def yarim_en(x, d=0.0):
    """Gövdenin yarım eni; uçlarda köşe yuvarlanır."""
    w = _en(x)
    for uc, r in ((XA, 0.05), (XO, 0.17)):
        m = abs(x - uc)
        if m < r: w -= r - math.sqrt(max(r * r - (r - m) ** 2, 0.0))
    return w - d

def kusak(x): return ZR if x < X_AC else _kab(x)

def yan_y(x, z, d=0.0):
    """Gövde yan yüzeyi (alt kenardan kuşağa): hafif bombe, altta içe dönüş, kuşağın altında omuz kırığı."""
    w = yarim_en(x, d); zk = kusak(x); zc = zk - (0.15 if x < X_AC else 0.105)
    def govde(zz):
        y = w - 0.012 * ((zz - 0.98) / 0.30) ** 2
        if zz < 0.72: y -= 0.03 * ((0.72 - zz) / 0.24) ** 2
        return y
    if z <= zc: return govde(z)
    t = min((z - zc) / (zk - zc), 1.0); return govde(zc) - 0.045 * (0.35 * t + 0.65 * t * t)

def cam_cizgisi(x, d=0.0):
    """Yan camın alt (eşik) ve üst (tavan kenarı) noktaları."""
    return (yarim_en(x, d) - 0.057, kusak(x) + 0.004), (0.735 - d, _tavan(x) - d - 0.060)

def yuzey_y(x, z):
    """Yan yüzeyin y değeri: kuşağın altında gövde, üstünde yan cam düzlemi."""
    zk = kusak(x)
    if z <= zk or x < X_AC: return yan_y(x, min(z, zk))
    S, T = cam_cizgisi(x); t = min(max((z - S[1]) / (T[1] - S[1]), 0.0), 1.0)
    return S[0] + (T[0] - S[0]) * t + 0.012 * math.sin(math.pi * t)

def ust_sablon(x, d=0.0):
    """Kabinin kırpılmamış üst kesiti: yan cam çizgisi, tavan köşesi, tavan. (y, z) listesi."""
    S, T = cam_cizgisi(x, d); zt = _tavan(x) - d; C = (0.655 - d, zt - 0.016); P = []
    for i in range(NG + 1):
        t = i / NG; P.append((S[0] + (T[0] - S[0]) * t + 0.012 * math.sin(math.pi * t), S[1] + (T[1] - S[1]) * t))
    for i in range(1, NK + 1):
        a = i / NK * math.pi / 2; P.append((C[0] + (T[0] - C[0]) * math.cos(a), T[1] + (C[1] - T[1]) * math.sin(a)))
    for i in range(1, NT + 1):
        y = C[0] * (1 - i / NT); P.append((y, zt - 0.016 * (y / C[0]) ** 2))
    return P

def on_cam_x(y, z, d=0.0): return 1.14 - 0.22 * (y / 0.85) ** 2 - 1.45 * d - (z - 1.285) / 0.93          # ön cam düzleminde x
def on_cam(x, y, d=0.0): return 1.285 + (1.14 - 0.22 * (y / 0.85) ** 2 - 1.45 * d - x) * 0.93           # ön cam düzleminde z
def arka_cam_x(z, d=0.0): return X_AC + d + (z - 1.305) / 5.67
def arka_cam(x, d=0.0): return 1.305 + (x - X_AC - d) * 5.67

def guverte(x, y):
    """Kaputun (ve kabin altındaki tablanın) yüksekliği; kasa bölgesinde kasa kenarı."""
    if x < X_AC: return ZR
    zk = _kab(x); w = yarim_en(x) - 0.045
    return zk + (_kaput(x) - zk) * (1 - min(abs(y) / w, 1.0) ** 2.2)

def kesit(x, d=0.0, zemin=None):
    """Yarım kesit: (y, z, tür) listesi; alt ortada başlar, üst ortada biter.
    tür: 0 gövde, 1 kabin şablonu, 2 ön cam düzlemi, 3 arka cam düzlemi, 4 güverte. d: içe öteleme; zemin: iç boşluk tabanı."""
    zb = _alt(x) if zemin is None else zemin; zk = kusak(x); zc = zk - (0.15 if x < X_AC else 0.105)
    P = [(0.0, zb, 0), (yan_y(x, zb, d) - 0.06, zb, 0)]
    for z in list(np.linspace(zb, zc, 15)) + list(np.linspace(zc, zk, 7))[1:]: P.append((yan_y(x, z, d), float(z), 0))
    for y, z0 in ust_sablon(x, d):
        g = guverte(x, y) if zemin is None else zk
        if x >= X_AC:
            a, b = on_cam(x, y, d), arka_cam(x, d); z = min(z0, a, b); tur = 1 if z == z0 else (2 if z == a else 3)
            if z <= g: z, tur = g, 4
        else: z, tur = g, 4
        P.append((y, z, tur))
    return P

def aralik(a, b, adim):
    n = max(1, round((b - a) / adim)); return [a + (b - a) * i / n for i in range(n + 1)]

# ------------------------------------------------------------------ ağ yardımcıları
def nesne(ad, bm, mats, c, aci=32):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    if aci:
        try: me.set_sharp_from_angle(angle=R(aci))
        except Exception: pass
    o = bpy.data.objects.new(ad, me)
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]): o.data.materials.append(m)
    return put(o, c)

def orgu(X, d=0.0, zemin=None):
    """İstasyonlardaki kesitlerden kapalı gövde."""
    bm = bmesh.new(); H = []
    for x in X:
        P = kesit(x, d, zemin); H.append([bm.verts.new((x, y, z)) for y, z, _ in P] + [bm.verts.new((x, -y, z)) for y, z, _ in P[-2:0:-1]])
    n = len(H[0])
    for a, b in zip(H, H[1:]):
        for j in range(n): bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
    bm.faces.new(H[0]); bm.faces.new(H[-1][::-1]); return bm

def izgara(bm, P):
    """P[i][j] noktalarından dörtgen örgü."""
    H = [[bm.verts.new(p) for p in satir] for satir in P]
    for a, b in zip(H, H[1:]):
        for j in range(len(a) - 1): bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
    return H

def boru(kesitler, m, c, kapali=False, ad='oluk'):
    """Art arda kesit halkalarından kapalı katı (aralık kesicileri için)."""
    bm = bmesh.new(); H = [[bm.verts.new(p) for p in k] for k in kesitler]; n = len(H[0])
    for a, b in list(zip(H, H[1:])) + ([(H[-1], H[0])] if kapali else []):
        for j in range(n): bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
    if not kapali: bm.faces.new(H[0]); bm.faces.new(H[-1][::-1])
    return nesne(ad, bm, m, c)

def kutular(ad, liste, m, c, pah=0.0):
    """Tek ağda çok sayıda kutu: (boyut, konum[, dönüş]) listesi."""
    bm = bmesh.new()
    for it in liste:
        rot = it[2] if len(it) > 2 else (0, 0, 0)
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(it[1]) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*it[0], 1)))
    o = nesne(ad, bm, m, c, aci=30)
    if pah:
        bv = o.modifiers.new('pah', 'BEVEL'); bv.width = pah; bv.segments = 2; bv.limit_method = 'ANGLE'
    return o

def yuvarlat(P, r, n=5, kapali=True):
    """Çokgenin köşelerini yuvarlatır; r tek sayı ya da köşe başına liste."""
    out = []; N = len(P)
    for i in range(N):
        ri = r[i] if isinstance(r, (list, tuple)) else r
        if ri <= 0 or (not kapali and i in (0, N - 1)): out.append(tuple(P[i])); continue
        p = Vector(P[i]); a = Vector(P[i - 1]); b = Vector(P[(i + 1) % N]); u = (a - p).normalized(); v = (b - p).normalized()
        dist = min(ri / math.tan(u.angle(v) / 2), (a - p).length * 0.45, (b - p).length * 0.45); p0 = p + u * dist; p1 = p + v * dist
        for k in range(n + 1):
            t = k / n; q = (1 - t) ** 2 * p0 + 2 * t * (1 - t) * p + t * t * p1; out.append((q.x, q.y))
    return out

def otele(P, d, kapali=True):
    """Çokgeni (ya da açık yolu) dışa doğru d kadar öteler."""
    n = len(P); alan = sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)); s = 1 if alan > 0 else -1; out = []
    for i in range(n):
        a = Vector(P[i - 1] if (kapali or i > 0) else P[i]); b = Vector(P[(i + 1) % n] if (kapali or i < n - 1) else P[i]); t = (b - a).normalized()
        out.append((P[i][0] + s * t.y * d, P[i][1] - s * t.x * d))
    return out

def prizma(P, eksen, a, b, m, c, ad='prizma'):
    """2B çokgeni eksen boyunca a'dan b'ye uzatır. eksen 'y': P (x, z); eksen 'x': P (y, z)."""
    bm = bmesh.new(); nk = (lambda p, t: (p[0], t, p[1])) if eksen == 'y' else (lambda p, t: (t, p[0], p[1]))
    A = [bm.verts.new(nk(p, a)) for p in P]; B = [bm.verts.new(nk(p, b)) for p in P]; n = len(P)
    bm.faces.new(A); bm.faces.new(B[::-1])
    for i in range(n): bm.faces.new((A[i], B[i], B[(i + 1) % n], A[(i + 1) % n]))
    return nesne(ad, bm, m, c)

def cerceve(P, d, harita, m, c, ad='conta'):
    """Çokgenin çevresinde d genişliğinde şerit; harita(u, v) yüzeydeki 3B noktayı verir."""
    D = otele(P, d); bm = bmesh.new(); n = len(P); A = [bm.verts.new(harita(*p)) for p in P]; B = [bm.verts.new(harita(*p)) for p in D]
    for i in range(n): bm.faces.new((A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]))
    return nesne(ad, bm, m, c, aci=0)

def _uygula(o, mod):
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=mod.name)

def _kes(o, kesici):
    md = o.modifiers.new('kes', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = kesici; md.solver = 'EXACT'
    if hasattr(md, 'material_mode'): md.material_mode = 'TRANSFER'                      # kesilen yüzler kesicinin malzemesini alır
    _uygula(o, md); bpy.data.objects.remove(kesici, do_unlink=True)

def yan_oluk(yol, yan, m, c, gen=0.005, derin=0.014, kapali=False):
    """Yan yüzeyde (x, z) yolunu izleyen ince aralık kesicisi; derinliği yüzeyi izler."""
    K = []; N = len(yol)
    for i, (x, z) in enumerate(yol):
        a = yol[i - 1] if (kapali or i > 0) else yol[i]; b = yol[(i + 1) % N] if (kapali or i < N - 1) else yol[i]
        t = Vector((b[0] - a[0], b[1] - a[1])).normalized(); n = Vector((-t.y, t.x)) * gen / 2; y = yuzey_y(x, z)
        K.append([(x - n.x, yan * (y + 0.01), z - n.y), (x + n.x, yan * (y + 0.01), z + n.y), (x + n.x, yan * (y - derin), z + n.y), (x - n.x, yan * (y - derin), z - n.y)])
    return boru(K, m, c, kapali)

def ust_oluk(yol, m, c, gen=0.005, derin=0.014):
    """Kaput üstünde (x, y) yolunu izleyen aralık kesicisi."""
    K = []
    for i, (x, y) in enumerate(yol):
        a = yol[max(i - 1, 0)]; b = yol[min(i + 1, len(yol) - 1)]; t = Vector((b[0] - a[0], b[1] - a[1])).normalized(); n = Vector((-t.y, t.x)) * gen / 2; z = guverte(x, y)
        K.append([(x - n.x, y - n.y, z + 0.01), (x + n.x, y + n.y, z + 0.01), (x + n.x, y + n.y, z - derin), (x - n.x, y - n.y, z - derin)])
    return boru(K, m, c)

# cam açıklıkları
ON_PENCERE = yuvarlat([(0.796, 1.318), (0.41, 1.735), (0.135, 1.735), (0.135, 1.325)], [0.02, 0.035, 0.03, 0.025])
ARKA_PENCERE = yuvarlat([(-0.005, 1.327), (-0.005, 1.735), (-0.77, 1.735), (-0.845, 1.335)], [0.025, 0.03, 0.07, 0.03])
ON_CAM = yuvarlat([(-0.815, 1.335), (0.815, 1.335), (0.672, 1.742), (0.35, 1.758), (0.0, 1.762), (-0.35, 1.758), (-0.672, 1.742)], [0.04, 0.04, 0.04, 0, 0, 0, 0.04])
ARKA_CAM = yuvarlat([(-0.61, 1.455), (0.61, 1.455), (0.61, 1.74), (-0.61, 1.74)], 0.05)

# ------------------------------------------------------------------ malzemeler
def _islem(nt, tur, a, b0=None):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = tur
    for i, v in enumerate((a, b0)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs['Value']

def _esle(nt, v, a, b0, c0=0.0, d0=1.0):
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; nt.links.new(v, mr.inputs['Value'])
    for ad, deger in (('From Min', a), ('From Max', b0), ('To Min', c0), ('To Max', d0)): mr.inputs[ad].default_value = deger
    return mr.outputs['Result']

def _karistir(nt, fac, c1, c2, tur='MIX'):
    n = nt.nodes.new('ShaderNodeMixRGB'); n.blend_type = tur
    for i, v in ((0, fac), (1, c1), (2, c2)):
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        elif isinstance(v, tuple): n.inputs[i].default_value = (*v, 1)
        else: nt.links.new(v, n.inputs[i])
    return n.outputs['Color']

def _gurultu(nt, P, olcek, detay, puruz=0.55, bozma=0.0):
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = olcek; n.inputs['Detail'].default_value = detay
    n.inputs['Roughness'].default_value = puruz; n.inputs['Distortion'].default_value = bozma; nt.links.new(P, n.inputs['Vector']); return n

def _vernik(m, agirlik=1.0, puruz=0.03):
    b = m.node_tree.nodes['Principled BSDF']
    if 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value = agirlik; b.inputs['Coat Roughness'].default_value = puruz
    return m

def _kaplama():
    """Mat kamuflaj kaplama: fırça izli üç ton; alt yarıda koyu düz ton; eteklerde toz."""
    import urunfilmi
    m = bpy.data.materials.new('kaplama'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links.new; b = N['Principled BSDF']
    P = N.new('ShaderNodeTexCoord').outputs['Object']
    ince = _gurultu(nt, P, 13, 5); kay = _karistir(nt, 0.03, P, ince.outputs['Color'])                  # fırça izli kenarlar
    ana = _gurultu(nt, kay, 1.75, 3, 0.5, 1.6)
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'; e = cr.color_ramp.elements
    koyu, orta, acik, beyaz = (0.062, 0.057, 0.052), (0.185, 0.17, 0.155), (0.42, 0.395, 0.36), (0.56, 0.54, 0.50)
    tonlar = [(0.0, koyu), (0.415, orta), (0.485, acik), (0.56, beyaz), (0.615, orta), (0.665, koyu)]
    e[0].position, e[0].color = tonlar[0][0], (*tonlar[0][1], 1); e[1].position, e[1].color = tonlar[1][0], (*tonlar[1][1], 1)
    for pos, col in tonlar[2:]:
        el = e.new(pos); el.color = (*col, 1)
    L(ana.outputs['Fac'], cr.inputs['Fac'])
    sp = N.new('ShaderNodeSeparateXYZ'); L(P, sp.inputs['Vector']); z = sp.outputs['Z']
    leke = _gurultu(nt, P, 2.4, 4)
    zz = _islem(nt, 'ADD', z, _islem(nt, 'MULTIPLY', _islem(nt, 'SUBTRACT', leke.outputs['Fac'], 0.5), 0.5))
    alt = _islem(nt, 'MULTIPLY', _esle(nt, zz, 1.10, 0.74), 0.93)                                       # alt yarı: koyu düz ton
    renk = _karistir(nt, alt, cr.outputs['Color'], (0.075, 0.069, 0.064))
    tozn = _gurultu(nt, P, 3.4, 8, 0.65)
    toz = _islem(nt, 'MULTIPLY', _esle(nt, z, 1.02, 0.44), _esle(nt, tozn.outputs['Fac'], 0.36, 0.68))
    renk = _karistir(nt, _islem(nt, 'MULTIPLY', toz, 0.42), renk, (0.155, 0.13, 0.10))
    L(renk, b.inputs['Base Color']); L(_islem(nt, 'ADD', _islem(nt, 'MULTIPLY', toz, 0.38), 0.43), b.inputs['Roughness'])
    if urunfilmi.KENAR:
        bv = N.new('ShaderNodeBevel'); bv.samples = 4; bv.inputs['Radius'].default_value = 0.0035; L(bv.outputs['Normal'], b.inputs['Normal'])
    return m

def _lastik():
    """Lastik: sırtta ve yanakta toz (teker merkezine göre)."""
    m = bpy.data.materials.new('lastik'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links.new; b = N['Principled BSDF']
    P = N.new('ShaderNodeTexCoord').outputs['Object']; sp = N.new('ShaderNodeSeparateXYZ'); L(P, sp.inputs['Vector'])
    cx = N.new('ShaderNodeCombineXYZ'); L(sp.outputs['X'], cx.inputs['X']); L(sp.outputs['Z'], cx.inputs['Z'])
    uz = N.new('ShaderNodeVectorMath'); uz.operation = 'LENGTH'; L(cx.outputs['Vector'], uz.inputs[0])
    nz = _gurultu(nt, P, 9, 7)
    toz = _islem(nt, 'MULTIPLY', _esle(nt, uz.outputs['Value'], 0.29, 0.40), _esle(nt, nz.outputs['Fac'], 0.3, 0.7))
    L(_karistir(nt, _islem(nt, 'MULTIPLY', toz, 0.8), (0.017, 0.017, 0.018), (0.20, 0.165, 0.125)), b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.86
    n2 = _gurultu(nt, P, 260, 3); bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; bp.inputs['Distance'].default_value = 0.0015
    L(n2.outputs['Fac'], bp.inputs['Height']); L(bp.outputs['Normal'], b.inputs['Normal'])
    return m

def _cam(ad, ton, renk=(1.0, 1.0, 1.0)):
    """Tek katmanlı oto camı: renkli geçirgenlik + bakış açısına bağlı yansıma."""
    m = bpy.data.materials.new(ad); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links.new; b = N['Principled BSDF']
    b.inputs['Base Color'].default_value = (1, 1, 1, 1); b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.0
    tr = N.new('ShaderNodeBsdfTransparent'); tr.inputs['Color'].default_value = (ton * renk[0], ton * renk[1], ton * renk[2], 1)
    ge = N.new('ShaderNodeNewGeometry'); dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; L(ge.outputs['Normal'], dot.inputs[0]); L(ge.outputs['Incoming'], dot.inputs[1])
    f = _islem(nt, 'ADD', _islem(nt, 'MULTIPLY', _islem(nt, 'POWER', _islem(nt, 'SUBTRACT', 1.0, _islem(nt, 'ABSOLUTE', dot.outputs['Value'])), 5.0), 0.95), 0.05)
    mx = N.new('ShaderNodeMixShader'); L(f, mx.inputs['Fac']); L(tr.outputs['BSDF'], mx.inputs[1]); L(b.outputs['BSDF'], mx.inputs[2])
    L(mx.outputs['Shader'], N['Material Output'].inputs['Surface']); return m

def malzemeler():
    from urunfilmi import pbr
    M = {'kaplama': _kaplama(), 'lastik': _lastik()}
    M['koyu'] = pbr('kaplama-koyu', (0.055, 0.051, 0.047), 0.5, kenar=0.003, puruz=0.05, puruz_olcek=600)
    M['plastik'] = pbr('oto-plastik', (0.021, 0.021, 0.022), 0.6, kenar=0.0015, puruz=0.3, puruz_olcek=1700)
    M['parlak'] = _vernik(pbr('siyah-parlak', (0.012, 0.012, 0.013), 0.25, kenar=0.0015), 0.6)
    M['jant'] = pbr('jant', (0.05, 0.052, 0.055), 0.38, metal=1.0, kenar=0.001)
    M['disk'] = pbr('fren-diski', (0.22, 0.22, 0.22), 0.4, metal=1.0, kenar=0.0)
    M['krom'] = pbr('saten-krom', (0.60, 0.61, 0.62), 0.22, metal=1.0, kenar=0.002, oynama=0.05)
    M['basamak'] = pbr('basamak', (0.42, 0.43, 0.44), 0.42, metal=1.0, kenar=0.002, puruz=0.25, puruz_olcek=800)
    M['astar'] = pbr('yuva-astari', (0.012, 0.012, 0.013), 0.92, kenar=0.0, puruz=0.5, puruz_olcek=300)
    M['kasa'] = pbr('kasa-astari', (0.017, 0.017, 0.018), 0.74, kenar=0.003, puruz=0.9, puruz_olcek=520)
    M['aralik'] = pbr('aralik', (0.004, 0.004, 0.004), 0.9, kenar=0.0)
    M['ic'] = pbr('kabin-ici', (0.024, 0.024, 0.026), 0.85, kenar=0.0, puruz=0.3, puruz_olcek=900)
    M['koltuk'] = pbr('koltuk', (0.04, 0.04, 0.043), 0.78, kenar=0.004, puruz=0.4, puruz_olcek=1400)
    M['conta'] = pbr('conta', (0.009, 0.009, 0.01), 0.5, kenar=0.0)
    M['alt'] = pbr('sasi', (0.011, 0.011, 0.011), 0.9, kenar=0.0)
    M['stop'] = _vernik(pbr('stop-cami', (0.16, 0.004, 0.005), 0.1, kenar=0.002, spec=0.8), 1.0)
    M['led'] = mat('stop-led', (0.5, 0.01, 0.01), 0.2, emit=(1.0, 0.03, 0.02), strength=5.0)
    M['far'] = _vernik(pbr('far', (0.42, 0.44, 0.47), 0.06, metal=0.8, kenar=0.0, spec=1.0), 1.0)
    M['gunduz'] = mat('gunduz-fari', (0.9, 0.9, 0.9), 0.2, emit=(1.0, 0.97, 0.9), strength=5.0)
    M['sinyal'] = mat('yan-isik', (0.6, 0.25, 0.02), 0.3, emit=(1.0, 0.42, 0.04), strength=2.5)
    M['ayna'] = pbr('ayna-cami', (0.85, 0.87, 0.9), 0.02, metal=1.0, kenar=0.0)
    M['cam_on'] = _cam('on-cam', 0.62, (0.93, 1.0, 0.96)); M['cam_yan'] = _cam('yan-cam', 0.42, (0.95, 1.0, 0.97)); M['cam_koyu'] = _cam('koyu-cam', 0.16)
    return M

# ------------------------------------------------------------------ gövde
def _govde(c, M):
    X = (aralik(XA, XA + 0.06, 0.006) + aralik(XA + 0.06, X_AC - 0.02, 0.045)[1:] + [X_AC - 0.0005] + aralik(X_AC + 0.0005, X_AC + 0.10, 0.004)
         + aralik(X_AC + 0.10, 0.36, 0.035)[1:] + aralik(0.36, 1.18, 0.012)[1:] + aralik(1.18, 2.40, 0.035)[1:] + aralik(2.40, XO, 0.008)[1:])
    g = nesne('pikap-govde', orgu(X), M['kaplama'], c, aci=0); K = KASA
    # kabin içi ve cam açıklıkları
    _kes(g, nesne('kabin-ici', orgu(aralik(X_AC + DUVAR, 0.36, 0.04) + aralik(0.36, 0.82, 0.015)[1:], DUVAR, 0.60), M['ic'], c, aci=0))
    for yan in (1, -1):
        for P in (ON_PENCERE, ARKA_PENCERE): _kes(g, prizma(P, 'y', yan * 0.45, yan * 1.2, M['conta'], c))
    _kes(g, prizma(ON_CAM, 'x', 0.45, 1.6, M['conta'], c)); _kes(g, prizma(ARKA_CAM, 'x', -1.05, -0.75, M['conta'], c))
    # kasa boşluğu, kabin ile kasa arasındaki aralık, çamurluk yuvaları
    _kes(g, box((K['x1'] - K['x0'], 2 * K['y'], 1.0), ((K['x0'] + K['x1']) / 2, 0, K['taban'] + 0.5), M['kasa'], c, bevel=0, name='kasa-bosluk'))
    _kes(g, box((0.018, 2.4, 1.5), (X_AC - 0.003, 0, 0.95), M['aralik'], c, bevel=0, name='kabin-kasa-araligi'))
    for x in (ON_DINGIL, ARKA_DINGIL):
        for yan in (1, -1): _kes(g, cyl(0.472, (x, yan * 0.50, TEKER_Z + 0.01), (x, yan * 1.2, TEKER_Z + 0.01), M['astar'], c, verts=96, name='yuva'))
    # kapı, yakıt kapağı, kaput ve arka kapak aralıkları
    A = M['aralik']
    for yan in (1, -1):
        for x in (1.13, 0.065, -0.905): _kes(g, yan_oluk([(x, 0.50 + (kusak(x) - 0.501) * i / 16) for i in range(17)], yan, A, c))
        _kes(g, yan_oluk([(-0.905 + 2.035 * i / 40, 0.502) for i in range(41)], yan, A, c))
        _kes(g, ust_oluk([(x, yan * (yarim_en(x) - 0.14)) for x in aralik(1.02, 2.50, 0.05)], A, c))
        _kes(g, box((0.03, 0.005, 0.72), (XA, yan * 0.797, 1.02), A, c, bevel=0)); _kes(g, box((0.075, 0.005, 0.06), ((XA + K['x0']) / 2, yan * 0.797, ZR), A, c, bevel=0))
    _kes(g, yan_oluk(yuvarlat([(-1.30, 1.01), (-1.14, 1.01), (-1.14, 1.15), (-1.30, 1.15)], 0.03), 1, A, c, kapali=True))
    _kes(g, ust_oluk([(2.50, y) for y in aralik(-0.78, 0.78, 0.06)], A, c))
    _kes(g, box((0.03, 1.6, 0.005), (XA, 0, 0.665), A, c, bevel=0)); _kes(g, box((0.014, 1.59, 0.006), (XA, 0, 1.205), A, c, bevel=0))
    g.data.polygons.foreach_set('use_smooth', [True] * len(g.data.polygons))
    try: g.data.set_sharp_from_angle(angle=R(30))
    except Exception: pass
    return g

def _camlar(c, M):
    """Camlar: gövde yüzeyinin biraz içinde duran saydam kabuk; yalnızca açıklıklardan görünür."""
    d = 0.012; X = aralik(X_AC + d + 0.002, 0.36, 0.03) + aralik(0.36, 1.16, 0.012)[1:]; nu = NG + NK + NT + 1; bm = bmesh.new(); H = []; T = []
    for x in X:
        P = kesit(x, d)[-nu:]; H.append([bm.verts.new((x, y, z)) for y, z, _ in P] + [bm.verts.new((x, -y, z)) for y, z, _ in P[-2::-1]]); T.append([t for _, _, t in P] + [t for _, _, t in P[-2::-1]])
    sira = list(range(nu)) + list(range(nu - 2, -1, -1))
    for i in range(len(X) - 1):
        for j in range(len(sira) - 1):
            tt = (T[i][j], T[i][j + 1], T[i + 1][j], T[i + 1][j + 1])
            if 4 in tt: continue
            if 2 in tt: mi = 0
            elif 3 in tt: mi = 2
            elif max(sira[j], sira[j + 1]) <= NG: mi = 1 if X[i] > 0.065 else 2
            else: continue
            bm.faces.new((H[i][j], H[i][j + 1], H[i + 1][j + 1], H[i + 1][j])).material_index = mi
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    return nesne('camlar', bm, [M['cam_on'], M['cam_yan'], M['cam_koyu']], c, aci=0)

def _contalar(c, M):
    for yan in (1, -1):
        for P in (ON_PENCERE, ARKA_PENCERE): cerceve(P, 0.017, lambda x, z, yan=yan: (x, yan * (yuzey_y(x, z) + 0.0015), z), M['conta'], c)
    cerceve(ON_CAM, 0.022, lambda y, z: (on_cam_x(y, z) + 0.002, y, z + 0.002), M['conta'], c)
    cerceve(ARKA_CAM, 0.022, lambda y, z: (arka_cam_x(z) - 0.002, y, z), M['conta'], c)

def _kabin_ici(c, M):
    """Camlardan görünen iç: koltuklar, baş dayamalar, gösterge paneli, direksiyon."""
    L = []
    for y in (0.40, -0.40):
        L += [((0.50, 0.50, 0.15), (0.33, y, 0.90)), ((0.13, 0.48, 0.62), (0.07, y, 1.27), (0, R(-14), 0)), ((0.10, 0.25, 0.17), (0.0, y, 1.665), (0, R(-8), 0))]
        L += [((0.09, 0.24, 0.16), (-0.775, y * 1.08, 1.63), (0, R(-8), 0))]
    L += [((0.48, 1.42, 0.15), (-0.50, 0, 0.90)), ((0.13, 1.42, 0.58), (-0.79, 0, 1.25), (0, R(-9), 0))]
    kutular('koltuklar', L, M['koltuk'], c, pah=0.035)
    kutular('panel', [((0.24, 1.66, 0.34), (0.71, 0, 1.165)), ((0.62, 0.22, 0.26), (0.33, 0, 0.78)), ((0.05, 0.19, 0.06), (0.47, 0, 1.70))], M['ic'], c, pah=0.03)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.185, minor_radius=0.016, major_segments=48, minor_segments=10, location=(0.555, 0.40, 1.29), rotation=(0, R(-68), 0))
    t = bpy.context.object; t.name = 'direksiyon'; bpy.ops.object.shade_smooth(); t.data.materials.append(M['ic']); put(t, c)
    cyl(0.03, (0.555, 0.40, 1.29), (0.70, 0.40, 1.22), M['ic'], c, verts=16, name='direksiyon-mili')

# ------------------------------------------------------------------ tekerler ve çamurluk kaplamaları
def _prizma8(bm, P):
    v = [bm.verts.new(p) for p in P]
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([v[i] for i in f])

def _teker(c, M, x, yan):
    """Arazi lastiği (bloklu sırt, omuz dişleri), 18 kollu jant, bijonlar, fren diski."""
    merkez = Vector((x, yan * TEKER_Y, TEKER_Z))
    def yer(bm):
        for v in bm.verts: v.co = Vector((v.co.x + x, yan * (v.co.y + TEKER_Y), v.co.z + TEKER_Z))
    bm = bmesh.new()
    kes = [(0.240, -0.104), (0.262, -0.127), (0.31, -0.139), (0.355, -0.137), (0.381, -0.125), (0.392, -0.108), (0.395, -0.06), (0.395, 0.0),
           (0.395, 0.06), (0.392, 0.108), (0.381, 0.125), (0.355, 0.137), (0.31, 0.139), (0.262, 0.127), (0.240, 0.104)]
    vs = [bm.verts.new((r, y, 0)) for r, y in kes]
    for a, b in zip(vs, vs[1:]): bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0, 0, 0), axis=(0, 1, 0), angle=2 * math.pi, steps=96, use_merge=True)
    NB = 46
    for k in range(NB):
        a = 2 * math.pi * k / NB
        for s, (y, en, boy, kay) in enumerate(((-0.106, 0.038, 0.033, 0.0), (-0.054, 0.036, 0.030, 0.5), (0.0, 0.032, 0.031, 0.0), (0.054, 0.036, 0.030, 0.5), (0.106, 0.038, 0.033, 0.0))):
            egim = R(15) * (1 if s % 2 == 0 else -1) * (1 if k % 2 == 0 else -1)
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Rotation(-(a + kay * 2 * math.pi / NB), 4, 'Y') @ Matrix.Translation((0.3985, y, 0)) @ Matrix.Rotation(egim, 4, 'X') @ Matrix.Diagonal((0.014, en, boy, 1)))
        for s in (-1, 1):
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Rotation(-a, 4, 'Y') @ Matrix.Translation((0.386, s * 0.129, 0)) @ Matrix.Rotation(s * R(52), 4, 'Z') @ Matrix.Diagonal((0.013, 0.032, 0.027, 1)))
    yer(bm); o = nesne('lastik', bm, M['lastik'], c, aci=30)
    o.data.transform(Matrix.Translation(-merkez)); o.location = merkez                    # toz, teker merkezine göre hesaplanır
    bm = bmesh.new()
    prof = [(0.236, -0.108), (0.226, -0.098), (0.214, -0.06), (0.214, 0.045), (0.226, 0.09), (0.238, 0.104), (0.246, 0.108), (0.246, 0.118), (0.236, 0.121), (0.226, 0.113), (0.216, 0.097)]
    vs = [bm.verts.new((r, y, 0)) for r, y in prof]
    for a, b in zip(vs, vs[1:]): bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0, 0, 0), axis=(0, 1, 0), angle=2 * math.pi, steps=72, use_merge=True)
    for k in range(18):
        rot = Matrix.Rotation(2 * math.pi * k / 18, 4, 'Y'); P = []
        for r, y, g in ((0.055, 0.076, 0.013), (0.222, 0.104, 0.021)):
            P += [rot @ Vector((r, y, -g / 2)), rot @ Vector((r, y, g / 2)), rot @ Vector((r, y - 0.03, g / 2)), rot @ Vector((r, y - 0.03, -g / 2))]
        _prizma8(bm, P)
    donus = Matrix.Rotation(math.pi / 2, 4, 'X')                                         # koninin ekseni z'den −y'ye; radius1 dış yüz
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.060, radius2=0.072, depth=0.05, matrix=Matrix.Translation((0, 0.058, 0)) @ donus)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=0.027, radius2=0.032, depth=0.012, matrix=Matrix.Translation((0, 0.089, 0)) @ donus)
    for k in range(5):
        a = 2 * math.pi * (k + 0.5) / 5
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.0105, radius2=0.0105, depth=0.02, matrix=Matrix.Translation((0.047 * math.cos(a), 0.088, 0.047 * math.sin(a))) @ donus)
    yer(bm); nesne('jant', bm, M['jant'], c, aci=28)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=0.172, radius2=0.172, depth=0.028, matrix=Matrix.Translation((0, 0.03, 0)) @ donus)
    yer(bm); nesne('fren-diski', bm, M['disk'], c, aci=30)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=0.213, radius2=0.213, depth=0.012, matrix=donus)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.105, 0.03, 0.105)) @ Matrix.Rotation(R(-45), 4, 'Y') @ Matrix.Diagonal((0.07, 0.07, 0.16, 1)))
    yer(bm); nesne('teker-arkasi', bm, M['alt'], c, aci=30)

def _davlumbaz(c, M, x0, yan):
    """Çamurluk kaplaması: yuvanın çevresinde, gövdeden dışa taşan siyah plastik yay."""
    U = [(0.0, -0.06), (0.04, -0.018), (0.10, 0.022), (0.22, 0.034), (0.55, 0.034), (0.82, 0.024), (0.95, 0.010), (1.0, -0.006)]; NA = 84; P = []
    for i in range(NA + 1):
        f = R(7 + 166 * i / NA); satir = []
        for u, dy in U:
            r = 0.462 + 0.108 * u; x = x0 + r * math.cos(f); z = TEKER_Z + r * math.sin(f)
            satir.append((x, yan * (yuzey_y(x, max(z, _alt(x))) + dy), z))
        P.append(satir)
    bm = bmesh.new(); izgara(bm, P); return nesne('davlumbaz', bm, M['plastik'], c, aci=40)

# ------------------------------------------------------------------ uç parçaları: lambalar, tamponlar
def kose_kabuk(c, m, x_bas, uc, y_son, z0, z1, yan, kalin=0.010, dilim=(0.0, 1.0), ad='lamba', nz=12):
    """Gövdenin köşesini saran kapalı kabuk: yan yüzde x_bas'tan uca, oradan uç yüzde y_son'a kadar."""
    yon = 1 if uc > 0 else -1; yol = [('yan', x_bas + (uc - x_bas) * (1 - (1 - i / 26) ** 2)) for i in range(27)]
    yol += [('uc', yarim_en(uc) + (y_son - yarim_en(uc)) * i / 8) for i in range(1, 9)]
    a, b = int(dilim[0] * (len(yol) - 1)), int(dilim[1] * (len(yol) - 1))
    def katman(ofset):
        P = []
        for j in range(nz + 1):
            z = z0 + (z1 - z0) * j / nz; ham = [Vector((v, yuzey_y(v, z), z)) if tur == 'yan' else Vector((uc, v, z)) for tur, v in yol]; satir = []
            for i in range(a, b + 1):
                t = ham[min(i + 1, len(ham) - 1)] - ham[max(i - 1, 0)]; p = ham[i] + Vector((t.y, -t.x, 0)).normalized() * (-yon) * ofset
                satir.append((p.x, yan * p.y, p.z))
            P.append(satir)
        return P
    bm = bmesh.new(); D = izgara(bm, katman(kalin)); I = izgara(bm, katman(-0.02))
    for j in range(len(D[0]) - 1): bm.faces.new((D[0][j], D[0][j + 1], I[0][j + 1], I[0][j])); bm.faces.new((D[-1][j], D[-1][j + 1], I[-1][j + 1], I[-1][j]))
    for i in range(len(D) - 1): bm.faces.new((D[i][0], D[i + 1][0], I[i + 1][0], I[i][0])); bm.faces.new((D[i][-1], D[i + 1][-1], I[i + 1][-1], I[i][-1]))
    return nesne(ad, bm, m, c, aci=40)

def cevre_yolu(uc, x_bas, ofset):
    """Gövdenin bir ucunu saran plan yolu (sol yandan sağ yana) ve onun dışa ötelenmişi."""
    sol = [(x, yarim_en(x)) for x in [x_bas + (uc - x_bas) * (1 - (1 - i / 30) ** 2) for i in range(31)]]
    w = yarim_en(uc); P = sol + [(uc, w - 2 * w * i / 16) for i in range(1, 16)] + [(x, -y) for x, y in sol[::-1]]
    return P, otele(P, ofset, kapali=False)

def _tampon(c, M, arka=True):
    """Tampon: gövdenin ucunu saran çubuk kesitli parça. Arka: saten köşeler, siyah basamak yüzeyi; ön: koyu üst, siyah alt."""
    if arka: ham, yol = cevre_yolu(XA, -2.42, 0.115); zt, zb = 0.668, 0.455
    else: ham, yol = cevre_yolu(XO, 2.16, 0.075); zt, zb = 0.745, 0.385
    bm = bmesh.new(); H = []
    for i, (px, py) in enumerate(yol):
        n = Vector((px - ham[i][0], py - ham[i][1])).normalized()
        prof = [(-0.17, zt), (-0.016, zt), (0.0, zt - 0.016), (0.0, (zt + zb) / 2 + 0.02), (-0.006, zb + 0.035), (-0.035, zb), (-0.17, zb)]
        H.append([bm.verts.new((px + n.x * o, py + n.y * o, z)) for o, z in prof])
    for i in range(len(H) - 1):
        for j in range(6):
            f = bm.faces.new((H[i][j], H[i][j + 1], H[i + 1][j + 1], H[i + 1][j]))
            if arka: f.material_index = 1 if (j == 0 or abs(yol[i][1]) < 0.60) else 0
            else: f.material_index = 0 if j <= 2 else 1
    bm.faces.new(H[0]); bm.faces.new(H[-1][::-1])
    return nesne('arka-tampon' if arka else 'on-tampon', bm, [M['krom'] if arka else M['koyu'], M['plastik']], c, aci=35)

# ------------------------------------------------------------------ ayrıntılar
def _kasa(c, M):
    """Kasa içi: nervürlü taban, teker davlumbazları, kenar kapakları, arkadaki yelken biçimli bar."""
    K = KASA; uz = K['x1'] - K['x0']; ox = (K['x0'] + K['x1']) / 2
    kutular('kasa-nervurleri', [((uz - 0.03, 0.036, 0.012), (ox, -K['y'] + 0.05 + i * 0.0715, K['taban'] + 0.006)) for i in range(22)], M['kasa'], c, pah=0.004)
    kutular('kasa-davlumbazlari', [((0.88, 0.14, 0.25), (ARKA_DINGIL, yan * (K['y'] - 0.07), K['taban'] + 0.125)) for yan in (1, -1)], M['kasa'], c, pah=0.04)
    L = [((uz + 0.1, 0.165, 0.03), (ox, yan * 0.878, ZR + 0.011)) for yan in (1, -1)] + [((0.085, 1.60, 0.03), (x, 0, ZR + 0.011)) for x in (K['x0'] - 0.033, K['x1'] + 0.035)]
    kutular('kasa-kenar-kapaklari', L, M['plastik'], c, pah=0.012)
    yelken = yuvarlat([(-0.985, 1.40), (-0.915, 1.795), (-1.10, 1.80), (-1.82, 1.40)], [0.01, 0.03, 0.06, 0.02])
    for yan in (1, -1):
        o = prizma(yelken, 'y', yan * 0.845, yan * 0.905, M['koyu'], c, ad='yelken'); bv = o.modifiers.new('pah', 'BEVEL'); bv.width = 0.014; bv.segments = 3; bv.limit_method = 'ANGLE'
    cyl(0.028, (-1.03, -0.84, 1.765), (-1.03, 0.84, 1.765), M['koyu'], c, verts=32, name='bar')

def _arka(c, M):
    """Stop lambaları, tampon, kapak kolu, çeki demiri, çamurluklar."""
    for yan in (1, -1):
        kose_kabuk(c, M['stop'], -2.655, XA, 0.80, 0.935, 1.357, yan, ad='stop')
        for z0, z1, dl in ((1.285, 1.33, (0.0, 1.0)), (0.965, 1.01, (0.0, 1.0)), (1.01, 1.285, (0.50, 0.68))):
            kose_kabuk(c, M['led'], -2.655, XA, 0.80, z0, z1, yan, kalin=0.0125, dilim=dl, ad='stop-led', nz=4)
    _tampon(c, M, arka=True)
    L = [((0.012, 0.21, 0.065), (XA - 0.003, 0, 1.275)), ((0.07, 0.07, 0.07), (XA - 0.06, 0, 0.40)), ((0.16, 0.05, 0.03), (XA - 0.14, 0, 0.41)), ((0.035, 0.035, 0.07), (XA - 0.20, 0, 0.45))]
    kutular('kapak-kolu-ve-ceki', L, M['plastik'], c, pah=0.006)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, location=(XA - 0.20, 0, 0.50), segments=24, ring_count=12); s = bpy.context.object; bpy.ops.object.shade_smooth(); s.data.materials.append(M['krom']); put(s, c)
    kutular('arka-yansitici', [((0.008, 0.11, 0.028), (XA - 0.118, yan * 0.72, 0.555)) for yan in (1, -1)], M['stop'], c, pah=0.003)
    kutular('camurluklar', [((0.014, 0.27, 0.30), (x - 0.535, yan * 0.815, 0.37), (0, R(6), 0)) for x in (ON_DINGIL, ARKA_DINGIL) for yan in (1, -1)], M['plastik'], c, pah=0.004)
    kutular('ucuncu-stop', [((0.02, 0.30, 0.016), (arka_cam_x(1.782) - 0.008, 0, 1.782))], M['stop'], c, pah=0.004)

def _yan(c, M):
    """Yan basamaklar, aynalar, kapı kolları."""
    for yan in (1, -1):
        kutular('yan-basamak', [((2.02, 0.155, 0.04), (0.11, yan * 1.0, 0.405))], M['basamak'], c, pah=0.014)
        L = [((1.90, 0.10, 0.008), (0.11, yan * 1.005, 0.428))] + [((0.05, 0.22, 0.045), (x, yan * 0.86, 0.40)) for x in (-0.70, 0.11, 0.92)]
        L += [((0.03, 0.16, 0.045), (x, yan * 1.0, 0.405)) for x in (-0.905, 1.125)]
        kutular('basamak-pedi', L, M['plastik'], c, pah=0.004)
        kutular('yan-isiklar', [((0.05, 0.008, 0.016), (x, yan * 1.079, 0.405)) for x in (-0.55, 0.11, 0.77)], M['sinyal'], c, pah=0.002)
        kutular('ayna', [((0.10, 0.215, 0.15), (0.865, yan * 1.085, 1.40)), ((0.05, 0.14, 0.035), (0.87, yan * 0.95, 1.345))], M['parlak'], c, pah=0.03)
        kutular('ayna-cami', [((0.004, 0.18, 0.115), (0.813, yan * 1.085, 1.40))], M['ayna'], c)
        for x in (0.26, -0.71):
            y = yuzey_y(x, 1.16)
            kutular('kapi-kolu', [((0.185, 0.02, 0.034), (x, yan * (y + 0.019), 1.16))], M['krom'], c, pah=0.008)
            kutular('kol-yuvasi', [((0.20, 0.006, 0.058), (x, yan * (y + 0.001), 1.158))], M['aralik'], c, pah=0.002)

def _on(c, M):
    """Ön yüz: tampon, ızgara, farlar. Sade tutulmuştur; çekimler aracı arkadan ve yandan gösterir."""
    _tampon(c, M, arka=False)
    kutular('izgara', [((0.03, 1.0, 0.31), (XO + 0.008, 0, 0.915))], M['plastik'], c, pah=0.006)
    kutular('izgara-citalari', [((0.02, 0.96, 0.022), (XO + 0.026, 0, 0.80 + i * 0.056)) for i in range(5)], M['jant'], c, pah=0.004)
    kutular('koruma-sac', [((0.10, 0.80, 0.05), (XO + 0.03, 0, 0.385))], M['basamak'], c, pah=0.012)
    for yan in (1, -1):
        kose_kabuk(c, M['far'], 2.36, XO, 0.50, 0.935, 1.068, yan, ad='far')
        kose_kabuk(c, M['gunduz'], 2.36, XO, 0.50, 0.94, 0.956, yan, kalin=0.0125, ad='gunduz-fari', nz=2)

def _ust(c, M):
    kutular('anten-tabani', [((0.10, 0.045, 0.03), (-0.60, 0, _tavan(-0.60) + 0.008))], M['plastik'], c, pah=0.012)
    cyl(0.0035, (-0.62, 0, _tavan(-0.6) + 0.01), (-0.83, 0, 2.22), M['plastik'], c, verts=8, name='anten')

def _alt_takim(c, M):
    kutular('sasi', [((4.5, 1.08, 0.16), (0.0, 0, 0.46)), ((1.30, 0.07, 0.03), (ARKA_DINGIL, 0.56, 0.35)), ((1.30, 0.07, 0.03), (ARKA_DINGIL, -0.56, 0.35))], M['alt'], c)
    cyl(0.05, (ARKA_DINGIL, -0.70, TEKER_Z), (ARKA_DINGIL, 0.70, TEKER_Z), M['alt'], c, verts=24, name='arka-dingil'); cyl(0.045, (ON_DINGIL, -0.70, TEKER_Z), (ON_DINGIL, 0.70, TEKER_Z), M['alt'], c, verts=24, name='on-dingil')
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(ARKA_DINGIL, 0, TEKER_Z), segments=24, ring_count=12); s = bpy.context.object; s.scale = (1.15, 0.9, 1); bpy.ops.object.shade_smooth(); s.data.materials.append(M['alt']); put(s, c)
    cyl(0.375, (-2.27, 0, 0.44), (-2.27, 0, 0.64), M['lastik'], c, verts=48, name='yedek-teker')
    cyl(0.03, (-1.9, -0.56, 0.43), (-2.74, -0.56, 0.43), M['basamak'], c, verts=20, name='egzoz')

def pikap(c):
    M = malzemeler(); _govde(c, M); _camlar(c, M); _contalar(c, M); _kabin_ici(c, M)
    for x in (ON_DINGIL, ARKA_DINGIL):
        for yan in (1, -1): _davlumbaz(c, M, x, yan); _teker(c, M, x, yan)
    _kasa(c, M); _arka(c, M); _yan(c, M); _on(c, M); _ust(c, M); _alt_takim(c, M)
    return KASA['taban'] + 0.012

# ------------------------------------------------------------------ arazi ve gökyüzü
def yukseklik(x, y):
    d = math.hypot(x, y); k = min(1.0, max(0.0, (d - 60) / 240)); k = k * k * (3 - 2 * k)
    return k * (30 * noise.fractal(Vector((x / 260, y / 260, 0.7)), 1.0, 2.0, 5) + 10) + 0.022 * noise.noise(Vector((x / 2.6, y / 2.6, 0))) + 0.006 * noise.noise(Vector((x / 0.45, y / 0.45, 3.1)))

def _toprak(uzak=False):
    m = bpy.data.materials.new('toprak-uzak' if uzak else 'toprak'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links.new; b = N['Principled BSDF']; b.inputs['Roughness'].default_value = 0.95
    P = N.new('ShaderNodeTexCoord').outputs['Object']
    buyuk = _gurultu(nt, P, 0.18, 8, 0.6); cr = N.new('ShaderNodeValToRGB'); e = cr.color_ramp.elements
    e[0].position = 0.34; e[0].color = (0.19, 0.145, 0.10, 1); e[1].position = 0.68; e[1].color = (0.40, 0.32, 0.225, 1)
    L(buyuk.outputs['Fac'], cr.inputs['Fac']); renk = cr.outputs['Color']
    if uzak:
        orta = _gurultu(nt, P, 0.035, 6, 0.6); renk = _karistir(nt, orta.outputs['Fac'], renk, (0.16, 0.15, 0.085))                  # uzakta kuru ot lekeleri
        cd = N.new('ShaderNodeCameraData'); pus = _esle(nt, cd.outputs['View Distance'], 90, 520, 0.0, 0.62)
        L(_karistir(nt, pus, renk, (0.42, 0.47, 0.55)), b.inputs['Base Color']); return m                                           # hava perspektifi
    # çakıl: her hücre ayrı bir taş tonu (koyu kahve, bej, açık gri); iri taşlar seyrek
    orta = _gurultu(nt, P, 1.4, 5, 0.6); renk = _karistir(nt, _esle(nt, orta.outputs['Fac'], 0.42, 0.68, 0.0, 0.55), renk, (0.30, 0.285, 0.26))          # yer yer grileşen çakıl öbekleri
    cakil = N.new('ShaderNodeTexVoronoi'); cakil.inputs['Scale'].default_value = 72; L(P, cakil.inputs['Vector']); ince = _gurultu(nt, P, 60, 6, 0.6)
    ton = N.new('ShaderNodeSeparateColor'); L(cakil.outputs['Color'], ton.inputs['Color'])
    tas = N.new('ShaderNodeValToRGB'); t = tas.color_ramp.elements; t[0].position = 0.0; t[0].color = (0.10, 0.075, 0.055, 1); t[1].position = 1.0; t[1].color = (0.66, 0.64, 0.60, 1)
    for pos, col in ((0.3, (0.27, 0.21, 0.15)), (0.55, (0.40, 0.33, 0.24)), (0.8, (0.47, 0.45, 0.42))):
        el = t.new(pos); el.color = (*col, 1)
    L(ton.outputs[0], tas.inputs['Fac']); renk = _karistir(nt, _esle(nt, ton.outputs[1], 0.25, 0.75, 0.25, 0.7), renk, tas.outputs['Color'])
    iri = N.new('ShaderNodeTexVoronoi'); iri.inputs['Scale'].default_value = 21; L(P, iri.inputs['Vector']); iton = N.new('ShaderNodeSeparateColor'); L(iri.outputs['Color'], iton.inputs['Color'])
    iri_var = _islem(nt, 'MULTIPLY', _esle(nt, iton.outputs[0], 0.82, 0.86), _esle(nt, iri.outputs['Distance'], 0.34, 0.22))                                  # hücrelerin yaklaşık altıda biri, ortası
    renk = _karistir(nt, iri_var, renk, _karistir(nt, iton.outputs[1], (0.30, 0.27, 0.23), (0.58, 0.56, 0.53)))
    renk = _karistir(nt, 0.3, renk, ince.outputs['Color'], 'OVERLAY')
    sp = N.new('ShaderNodeSeparateXYZ'); L(P, sp.inputs['Vector'])                                                                    # teker izleri: aracın arkasında iki koyu, sıkışmış şerit
    iz = _islem(nt, 'MULTIPLY', _esle(nt, _islem(nt, 'ABSOLUTE', _islem(nt, 'SUBTRACT', _islem(nt, 'ABSOLUTE', sp.outputs['Y']), TEKER_Y)), 0.21, 0.10), _esle(nt, sp.outputs['X'], 2.3, 1.6))
    dis = N.new('ShaderNodeTexWave'); dis.inputs['Scale'].default_value = 26; dis.inputs['Distortion'].default_value = 0.6; L(P, dis.inputs['Vector'])           # lastik dişinin bıraktığı enine çizgiler
    L(_karistir(nt, _islem(nt, 'MULTIPLY', iz, _islem(nt, 'ADD', 0.34, _islem(nt, 'MULTIPLY', dis.outputs['Fac'], 0.22))), renk, (0.50, 0.47, 0.44), 'MULTIPLY'), b.inputs['Base Color'])
    engebe = _gurultu(nt, P, 2.3, 5, 0.6)
    yuk = _islem(nt, 'ADD', _islem(nt, 'ADD', _islem(nt, 'MULTIPLY', _islem(nt, 'SUBTRACT', 1.0, cakil.outputs['Distance']), 0.35), _islem(nt, 'MULTIPLY', iri_var, 0.9)), _islem(nt, 'MULTIPLY', engebe.outputs['Fac'], 2.2))
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 1.0; bp.inputs['Distance'].default_value = 0.02; L(yuk, bp.inputs['Height']); L(bp.outputs['Normal'], b.inputs['Normal'])
    return m

def _rastgele_renk(ad, renkler, rough=0.9):
    """Her ada (taş, ot) için ayrı ton seçen malzeme."""
    m = bpy.data.materials.new(ad); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; b = N['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    ge = N.new('ShaderNodeNewGeometry'); cr = N.new('ShaderNodeValToRGB'); e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (*renkler[0], 1); e[1].position = 1.0; e[1].color = (*renkler[-1], 1)
    for i, col in enumerate(renkler[1:-1]):
        el = e.new((i + 1) / (len(renkler) - 1)); el.color = (*col, 1)
    nt.links.new(ge.outputs['Random Per Island'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color']); return m

def arazi(c):
    """Çakıllı toprak zemin (teker izleriyle), dağınık taşlar, ot öbekleri, ufukta puslu tepeler."""
    for ad, boyut, bolme, m in (('zemin', 70, 420, _toprak()), ('arazi', 1500, 240, _toprak(uzak=True))):
        me = bpy.data.meshes.new(ad); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=bolme, y_segments=bolme, size=boyut / 2)
        for v in bm.verts:
            v.co.z = yukseklik(v.co.x, v.co.y) - (0.06 if ad == 'arazi' and max(abs(v.co.x), abs(v.co.y)) < 33 else 0.0)
        bm.to_mesh(me); bm.free(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
        o = bpy.data.objects.new(ad, me); o.data.materials.append(m); put(o, c)
    rnd = random.Random(7); bm = bmesh.new()
    for i in range(5200):
        d = 2.0 + 26 * rnd.random() ** 1.6; a = rnd.uniform(0, 6.2832); x, y = -2.0 + d * math.cos(a), 1.0 + d * math.sin(a)
        if abs(x) < 3.1 and abs(y) < 1.25: continue
        r = rnd.uniform(0.005, 0.018) * (1 + 3.0 * (rnd.random() < 0.025)) * (1 + 2.0 * (rnd.random() < 0.006))
        olcek = Matrix.Diagonal((rnd.uniform(0.8, 1.5), rnd.uniform(0.8, 1.3), rnd.uniform(0.45, 0.8), 1))
        donus = Euler((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, 6.28))).to_matrix().to_4x4()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation((x, y, yukseklik(x, y) + r * 0.25)) @ donus @ olcek)
    nesne('taslar', bm, _rastgele_renk('tas', [(0.11, 0.10, 0.085), (0.21, 0.19, 0.16), (0.30, 0.285, 0.26), (0.16, 0.135, 0.105)]), c, aci=50)
    bm = bmesh.new()
    for i in range(1500):
        d = 5.5 + 55 * rnd.random() ** 1.3; a = rnd.uniform(0, 6.2832); x, y = d * math.cos(a), d * math.sin(a)
        if abs(y) < 1.6 and x < 3: continue                                                                    # aracın geldiği iz
        z0 = yukseklik(x, y)
        for k in range(rnd.randint(7, 16)):
            b = rnd.uniform(0, 6.2832); h = rnd.uniform(0.10, 0.36); e = rnd.uniform(0.1, 0.55); g = rnd.uniform(0.003, 0.006)
            kok = Vector((x + rnd.uniform(-0.05, 0.05), y + rnd.uniform(-0.05, 0.05), z0 - 0.01)); yon = Vector((math.cos(b), math.sin(b), 0)); yan = Vector((-yon.y, yon.x, 0)) * g
            p1 = kok + yon * h * e * 0.35 + Vector((0, 0, h * 0.6)); p2 = kok + yon * h * e + Vector((0, 0, h))
            v = [bm.verts.new(q) for q in (kok - yan, kok + yan, p1 + yan * 0.7, p1 - yan * 0.7, p2)]
            bm.faces.new((v[0], v[1], v[2], v[3])); bm.faces.new((v[3], v[2], v[4]))
    for i in range(900):                                                                                         # yakın çevrede seyrek, alçak ot
        d = 3.8 + 14 * rnd.random(); a = rnd.uniform(0, 6.2832); x, y = d * math.cos(a), d * math.sin(a)
        if abs(y) < 1.5 and x < 3.2: continue
        z0 = yukseklik(x, y)
        for k in range(rnd.randint(4, 9)):
            b = rnd.uniform(0, 6.2832); h = rnd.uniform(0.04, 0.16); e = rnd.uniform(0.2, 0.7); g = rnd.uniform(0.002, 0.004)
            kok = Vector((x + rnd.uniform(-0.03, 0.03), y + rnd.uniform(-0.03, 0.03), z0 - 0.005)); yon = Vector((math.cos(b), math.sin(b), 0)); yan = Vector((-yon.y, yon.x, 0)) * g
            p1 = kok + yon * h * e * 0.35 + Vector((0, 0, h * 0.6)); p2 = kok + yon * h * e + Vector((0, 0, h))
            v = [bm.verts.new(q) for q in (kok - yan, kok + yan, p1 + yan * 0.7, p1 - yan * 0.7, p2)]
            bm.faces.new((v[0], v[1], v[2], v[3])); bm.faces.new((v[3], v[2], v[4]))
    nesne('otlar', bm, _rastgele_renk('ot', [(0.33, 0.27, 0.11), (0.25, 0.22, 0.09), (0.15, 0.17, 0.06), (0.36, 0.30, 0.14)], rough=0.8), c, aci=0)
    _cali_ekle(c)

def bulutlar(yogunluk=0.45):
    """Gökyüzüne ince, uzamış bulut katmanı ekler (sahneler.sky ile kurulan dünyanın üstüne)."""
    nt = bpy.context.scene.world.node_tree; N = nt.nodes; L = nt.links.new; bg = N['Background']; gok = bg.inputs['Color'].links[0].from_socket
    tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L(tc.outputs['Generated'], sp.inputs['Vector'])
    pay = _islem(nt, 'ADD', _islem(nt, 'MAXIMUM', sp.outputs['Z'], 0.0), 0.12)
    cx = N.new('ShaderNodeCombineXYZ'); L(_islem(nt, 'DIVIDE', sp.outputs['X'], pay), cx.inputs['X']); L(_islem(nt, 'MULTIPLY', _islem(nt, 'DIVIDE', sp.outputs['Y'], pay), 0.32), cx.inputs['Y'])
    nz = _gurultu(nt, cx.outputs['Vector'], 0.9, 7, 0.62, 0.6)
    fac = _islem(nt, 'MULTIPLY', _islem(nt, 'MULTIPLY', _esle(nt, nz.outputs['Fac'], 0.50, 0.74), _esle(nt, sp.outputs['Z'], 0.015, 0.16)), yogunluk)
    bw = N.new('ShaderNodeRGBToBW'); L(gok, bw.inputs['Color']); par = _islem(nt, 'MINIMUM', _islem(nt, 'MULTIPLY', bw.outputs['Val'], 2.3), 60.0)
    renk = N.new('ShaderNodeCombineColor'); L(par, renk.inputs[0]); L(_islem(nt, 'MULTIPLY', par, 0.95), renk.inputs[1]); L(_islem(nt, 'MULTIPLY', par, 0.9), renk.inputs[2])
    L(_karistir(nt, fac, gok, renk.outputs['Color']), bg.inputs['Color'])

def _cali_ekle(c):
    """Uzakta dağınık alçak çalılar: düzlüğe ölçek verir."""
    rnd = random.Random(11); bm = bmesh.new()
    for i in range(420):
        d = 26 + 330 * rnd.random() ** 1.5; a = rnd.uniform(0, 6.2832); x, y = d * math.cos(a), d * math.sin(a); r = rnd.uniform(0.25, 0.8)
        olcek = Matrix.Diagonal((rnd.uniform(0.9, 1.6), rnd.uniform(0.9, 1.6), rnd.uniform(0.45, 0.8), 1))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=Matrix.Translation((x, y, yukseklik(x, y) + r * 0.2)) @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, 'Z') @ olcek)
    for v in bm.verts: v.co += Vector((noise.noise(v.co * 4.0), noise.noise(v.co * 4.0 + Vector((7, 0, 0))), noise.noise(v.co * 4.0 + Vector((0, 7, 0))))) * 0.12
    nesne('calilar', bm, _rastgele_renk('cali', [(0.06, 0.075, 0.035), (0.10, 0.10, 0.045), (0.14, 0.125, 0.06), (0.07, 0.065, 0.035)], rough=0.9), c, aci=0)
