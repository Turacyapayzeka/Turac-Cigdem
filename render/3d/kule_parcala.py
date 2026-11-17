"""Kule CAD modelini parçalara ayırır ve dönüş eksenlerini bulur (ürün filmi ve hareketli sahneler için).

    python3 render/3d/kule_parcala.py        # modeller/taret.glb -> modeller/kule-parcalar.npz

Gerekenler: numpy, scipy.

taret.glb tek gövde ve tek tüfek ağından oluşur; CAD montajındaki katı parçalar ağda ayrı bağlı bileşenlerdir.
Bileşenler şu gruplara ayrılır (çıktı koordinatları Blender: X ileri = namlu yönü, Y sola, Z yukarı, metre):

  taban        sabit taban flanşı
  govde        yatay dönen tahrik gövdesi
  besik        dikey dönen beşik: gövdeyi saran çatal, üst tabla, yan kollar
  silah        beşikle birlikte dönen iki tüfek (gövde, kundak, şarjör)
  namlu        tüfeklerin namlu ve namlu ucu parçaları (çelik)
  vida_*       köşegeni 12 mm'den kısa bağlantı elemanları (taban, govde, besik, silah için ayrı)

Yatay eksen taban flanşının merkezinden (Z'ye paralel), dikey eksen gövdenin iki yanındaki göbek disklerinin
merkezinden (Y'ye paralel) geçer.

AYNALAMA: taret.glb aynalı aktarılmış. Tüfeklerdeki kabartma yazılar ters okunuyor ve ters monte tüfek kulenin
sağında duruyor; saha fotoğraflarında solunda. Bu betik modeli yan eksende aynalayarak (üçgen yönlerini de çevirerek)
fotoğraflardaki yerleşime getirir. taret.glb dosyasının kendisi değişmez.
"""
import json, os, struct
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

KOK = os.path.dirname(os.path.abspath(__file__))
GIRDI = os.path.join(KOK, 'modeller', 'taret.glb'); CIKTI = os.path.join(KOK, 'modeller', 'kule-parcalar.npz')
KAYNAK = 2e4                 # köşe kaynaklama hassasiyeti: 0,05 mm
VIDA = 0.012                 # köşegeni bundan kısa bileşen bağlantı elemanı sayılır

def glb_oku(yol):
    d = open(yol, 'rb').read(); assert d[:4] == b'glTF'
    n = struct.unpack('<I', d[12:16])[0]; js = json.loads(d[20:20 + n]); o = 20 + n
    m = struct.unpack('<I', d[o:o + 4])[0]; ikili = d[o + 8:o + 8 + m]
    def erisim(i):
        a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
        tur = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[a['componentType']]
        k = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
        arr = np.frombuffer(ikili, tur, a['count'] * k, bv.get('byteOffset', 0) + a.get('byteOffset', 0))
        return arr.reshape(-1, k) if k > 1 else arr
    out = {}
    for dugum in js['nodes']:
        if 'mesh' not in dugum: continue
        P, I, taban = [], [], 0
        for pr in js['meshes'][dugum['mesh']]['primitives']:
            p = erisim(pr['attributes']['POSITION']).astype(np.float64); P.append(p)
            I.append(erisim(pr['indices']).astype(np.int64).reshape(-1, 3) + taban); taban += len(p)
        out[dugum['name']] = (np.vstack(P), np.vstack(I))
    return out

def kaynakla(P, I):
    anahtar = np.round(P * KAYNAK).astype(np.int64)
    _, ilk, ters = np.unique(anahtar, axis=0, return_index=True, return_inverse=True); ters = ters.ravel()
    T = ters[I]; T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    return P[ilk], T

def bilesenler(n, T):
    g = coo_matrix((np.ones(len(T) * 2), (np.r_[T[:, 0], T[:, 1]], np.r_[T[:, 1], T[:, 2]])), shape=(n, n))
    return connected_components(g, directed=False)[1][T[:, 0]]

def kutular(V, T, et):
    n = et.max() + 1; mn = np.full((n, 3), np.inf); mx = np.full((n, 3), -np.inf)
    for k in range(3):
        np.minimum.at(mn, et, V[T[:, k]]); np.maximum.at(mx, et, V[T[:, k]])
    return mn, mx

def main():
    ag = glb_oku(GIRDI)                                   # glTF: x ileri, y yukarı, z yana
    Vg, Tg = kaynakla(*ag['body']); Vs, Ts = kaynakla(*ag['gun'])
    eg = bilesenler(len(Vg), Tg); es = bilesenler(len(Vs), Ts)
    with np.errstate(invalid='ignore'):
        mn, mx = kutular(Vg, Tg, eg); boy = mx - mn; kos = np.linalg.norm(boy, axis=1)
        flans = np.flatnonzero((mx[:, 1] <= 0.086) & (boy[:, 0] > 0.15) & (boy[:, 2] > 0.15))[0]
        yatay = [(mn[flans, 0] + mx[flans, 0]) / 2, (mn[flans, 2] + mx[flans, 2]) / 2]
        gobek = np.flatnonzero((boy[:, 2] < 0.03) & (boy[:, 0] > 0.07) & (np.abs(boy[:, 0] - boy[:, 1]) < 0.004) & (mn[:, 1] > 0.1))
        dikey = [np.mean((mn[gobek, 0] + mx[gobek, 0]) / 2), np.mean((mn[gobek, 1] + mx[gobek, 1]) / 2)]
        catal = int(np.argmax(np.where(np.isfinite(boy[:, 2]), boy[:, 2], -1)))
        ana = int(np.argmax(np.bincount(eg, minlength=len(boy)) * (np.arange(len(boy)) != catal)))
        gz0, gz1, gy1 = mn[ana, 2], mx[ana, 2], mx[ana, 1]
        sinif = np.full(len(boy), 1)
        sinif[mx[:, 1] <= 0.086] = 0
        sinif[(mn[:, 1] >= gy1 + 0.0005) | (mn[:, 2] >= gz1 + 0.001) | (mx[:, 2] <= gz0 - 0.001)] = 2
        sinif[catal] = 2; sinif[ana] = 1
        vida = kos < VIDA
        mns, mxs = kutular(Vs, Ts, es); koss = np.linalg.norm(mxs - mns, axis=1); vidas = koss < VIDA
        namlu = ((mns[:, 0] + mxs[:, 0]) / 2 > 0.45) & ~vidas
    bl = lambda V: np.c_[V[:, 0], V[:, 2], V[:, 1]].astype(np.float32)       # glTF -> Blender, yan eksende aynalı (bkz. AYNALAMA)
    cikti = {'yatay_eksen_xy': np.array([yatay[0], yatay[1]], np.float32), 'dikey_eksen_xz': np.array(dikey, np.float32)}
    def yaz(ad, V, T):
        kul, yeni = np.unique(T, return_inverse=True)
        cikti[ad + '_v'] = bl(V[kul]); cikti[ad + '_t'] = yeni.reshape(-1, 3)[:, ::-1].astype(np.int32)
        print(f'  {ad:12s} köşe {len(kul):6d}  üçgen {len(T):6d}')
    for ad, s in (('taban', 0), ('govde', 1), ('besik', 2)):
        yaz(ad, Vg, Tg[(sinif[eg] == s) & ~vida[eg]]); yaz('vida_' + ad, Vg, Tg[(sinif[eg] == s) & vida[eg]])
    yaz('silah', Vs, Ts[~vidas[es] & ~namlu[es]]); yaz('namlu', Vs, Ts[namlu[es]]); yaz('vida_silah', Vs, Ts[vidas[es]])
    print('yatay eksen (X, Y):', cikti['yatay_eksen_xy'].round(4), ' dikey eksen (X, Z):', cikti['dikey_eksen_xz'].round(4))
    np.savez_compressed(CIKTI, **cikti); print('yazıldı', CIKTI, round(os.path.getsize(CIKTI) / 1e6, 2), 'MB')

if __name__ == '__main__':
    main()
