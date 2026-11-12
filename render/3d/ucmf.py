"""3MF (Bambu Studio / OrcaSlicer projesi) okuyucu: bpy gerektirmez, yalnızca standart kitaplık + numpy.

Bir 3MF arşivi ya da arşivden çıkarılmış dosyalar okunur:
    parcalar = oku('3dmodel.model', {'/3D/Objects/object_3.model': 'object_3.model'})
Her parça: {'ad', 'v' (N×3, milimetre, tabla koordinatında), 'f' (M×3)}.
3MF dönüşümü satır vektörü düzenindedir: [x y z 1] · M, M = 4×3 (son satır öteleme).
"""
import xml.etree.ElementTree as ET
import numpy as np

NS = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
PP = '{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'

def mat(s):
    a = [float(x) for x in s.split()] if s else [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    m = np.eye(4); m[:3, :3] = np.array(a[:9]).reshape(3, 3); m[3, :3] = a[9:12]; return m      # satır vektörü düzeni

def aglar(yol):
    """bir .model dosyasındaki mesh'li nesneler: {id: (v, f)}"""
    out = {}; oid = None; v = []; f = []
    for ev, el in ET.iterparse(yol, events=('start', 'end')):
        tag = el.tag.replace(NS, '')
        if ev == 'start' and tag == 'object': oid = el.get('id'); v = []; f = []
        elif ev == 'end' and tag == 'vertex': v.append((float(el.get('x')), float(el.get('y')), float(el.get('z')))); el.clear()
        elif ev == 'end' and tag == 'triangle': f.append((int(el.get('v1')), int(el.get('v2')), int(el.get('v3')))); el.clear()
        elif ev == 'end' and tag == 'object':
            if v: out[oid] = (np.array(v, dtype=np.float64), np.array(f, dtype=np.int32))
            el.clear()
    return out

def oku(ana, dosyalar):
    """ana: 3D/3dmodel.model yolu; dosyalar: {p:path -> yerel yol}. Tabla koordinatında parçaları döndürür."""
    kok = ET.parse(ana).getroot(); nesneler = {}; yerel = aglar(ana); onbellek = {}
    for o in kok.iter(NS + 'object'):
        bil = [(c.get(PP + 'path'), c.get('objectid'), mat(c.get('transform'))) for c in o.iter(NS + 'component')]
        nesneler[o.get('id')] = bil
    parcalar = []
    for it in kok.iter(NS + 'item'):
        Mi = mat(it.get('transform')); oid = it.get('objectid')
        for yol, cid, Mc in (nesneler.get(oid) or [(None, oid, np.eye(4))]):
            if yol:
                if yol not in dosyalar: raise FileNotFoundError(f'eksik dosya: {yol}')
                if yol not in onbellek: onbellek[yol] = aglar(dosyalar[yol])
                v, f = onbellek[yol][cid]
            else: v, f = yerel[cid]
            vh = np.hstack([v, np.ones((len(v), 1))]) @ Mc @ Mi
            parcalar.append({'ad': f'nesne{oid}_parca{cid}', 'v': vh[:, :3], 'f': f})
    return parcalar

if __name__ == '__main__':
    import sys
    ps = oku(sys.argv[1], dict(a.split('=', 1) for a in sys.argv[2:]))
    for p in ps:
        lo, hi = p['v'].min(0), p['v'].max(0)
        print(p['ad'], 'köşe', len(p['v']), 'üçgen', len(p['f']), 'boyut mm', np.round(hi - lo, 1), 'alt', np.round(lo, 1))
