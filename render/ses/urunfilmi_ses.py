"""Dron Kalkanı ürün filmi (35 sn) için sentezlenmiş ses bandı: düşük frekanslı sinematik atmosfer ve hafif mekanik sesler.

    python3 render/ses/urunfilmi_ses.py render/out/urunfilmi-ses.wav

Zamanlar urunfilmi/index.html içindeki kurguyla aynıdır. Tamamı sentezdir; kayıt ya da telifli malzeme yoktur.
Atış, patlama ya da alarm sesi yoktur.
"""
import sys, math, wave
import numpy as np

SR = 48000; DUR = 35.0; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N); WL = np.zeros(N); WR = np.zeros(N)
rng = np.random.default_rng(11); t_all = np.arange(N) / SR

KESME = [3.25, 5.1, 6.9, 10.4, 16.9, 19.9, 22.9]      # yumuşak geçişler
BUYUK = [13.8, 28.8]                                   # stüdyodan açık havaya; finale dönüş
ISIK = [0.12, 0.52, 1.02, 1.52]                        # stüdyo ışıklarının açılışı
GRAFIK = [7.8, 8.4, 11.2, 11.8, 24.5, 25.2]            # grafik katmanlarının belirişi

def pan_gains(p): a = (p + 1) * math.pi / 4; return math.cos(a), math.sin(a)
def add(sig, start, gain=1.0, pan=0.0, wet=0.0):
    i = int(round(start * SR))
    if i >= N or i + len(sig) <= 0: return
    if i < 0: sig = sig[-i:]; i = 0
    n = min(len(sig), N - i); gl, gr = pan_gains(pan); s = sig[:n] * gain
    L[i:i + n] += s * gl; R[i:i + n] += s * gr
    if wet: WL[i:i + n] += s * gl * wet; WR[i:i + n] += s * gr * wet
def tt(dur): return np.arange(int(dur * SR)) / SR
def filt(x, lo=None, hi=None, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); H = np.ones_like(f)
    if lo: H *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if hi: H *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    return np.fft.irfft(X * H, len(x))
def noise(dur): return rng.standard_normal(int(dur * SR))
def ramp(n, a, r):
    e = np.ones(n); na = min(n, int(a * SR)); nr = min(n, int(r * SR))
    if na: e[:na] = 0.5 - 0.5 * np.cos(np.linspace(0, math.pi, na))
    if nr: e[-nr:] *= 0.5 + 0.5 * np.cos(np.linspace(0, math.pi, nr))
    return e
def saw(f, t, ph=0.0): return 2 * ((f * t + ph) % 1.0) - 1

# ---- atmosfer: alçak pad (Re), bölümlere göre akor; finalde majöre çözülür
BOLUM = [(0.0, 7.0, 36.71, 'm'), (7.0, 14.0, 43.65, 'M'), (14.0, 23.0, 49.0, 'M'), (23.0, 29.0, 32.7, 'm'), (29.0, 35.0, 36.71, 'M')]
pad = np.zeros(N)
for a, b, f, kip in BOLUM:
    i0 = max(0, int((a - 1.2) * SR)); i1 = min(N, int((b + 1.2) * SR)); t = t_all[i0:i1]; env = ramp(i1 - i0, 2.2, 2.2)
    tonlar = [f, f * 2, f * 3, f * 4 * (2 ** ((4 if kip == 'M' else 3) / 12)) / 2, f * 6]
    s = np.zeros(i1 - i0)
    for k, ton in enumerate(tonlar):
        for det in (-0.003, 0.003): s += saw(ton * (1 + det), t, ph=rng.random()) * (0.9 if k == 0 else 0.5) / (1 + 0.4 * k)
    pad[i0:i1] += s * env
pad = filt(pad, lo=30, hi=340, order=2) * (0.8 + 0.2 * np.sin(2 * math.pi * 0.07 * t_all))
alt = np.zeros(N)
for a, b, f, _ in BOLUM:
    i0 = max(0, int((a - 0.6) * SR)); i1 = min(N, int((b + 0.6) * SR)); alt[i0:i1] += np.sin(2 * math.pi * f * t_all[i0:i1]) * ramp(i1 - i0, 1.2, 1.2)
kazanc = np.interp(t_all, [0, 2.0, 7, 14, 23, 29, 30.5, 33.5, 35], [0.0, 0.7, 0.8, 0.85, 0.8, 0.9, 1.0, 0.8, 0.0])
L += (pad * 0.05 + alt * 0.05) * kazanc; R += (np.roll(pad, 337) * 0.05 + alt * 0.05) * kazanc
# hava: çok hafif, yüksek "nefes"
hava = filt(noise(DUR), lo=2500, hi=9000) * (0.5 + 0.5 * np.sin(2 * math.pi * 0.05 * t_all + 1.0)) * np.interp(t_all, [0, 3, 29, 35], [0, 1, 1, 0])
L += hava * 0.006; R += np.roll(hava, 211) * 0.006

# ---- vuruşlar ve geçişler
def derin(level=1.0):
    t = tt(2.6); f = 34 + 22 * np.exp(-t / 0.09); govde = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t / 0.8)
    return (govde + filt(noise(2.6), hi=220) * np.exp(-t / 0.2) * 1.6) * level
def hisirti(dur=1.0):
    t = tt(dur); a = filt(noise(dur), lo=250, hi=1300) * np.sin(math.pi * t / dur) ** 2; b = filt(noise(dur), lo=1300, hi=5200) * np.sin(math.pi * np.clip(t / dur * 1.3 - 0.3, 0, 1)) ** 2
    return a * 0.8 + b * 0.6
def can(f, dur=4.0):
    t = tt(dur); s = np.sin(2 * math.pi * f * t) + 0.4 * np.sin(2 * math.pi * 2.76 * f * t) * np.exp(-t / 0.6)
    return s * np.exp(-t / 1.3) * ramp(len(t), 0.004, 0.3)
for k in KESME: add(hisirti(0.9), k - 0.2, gain=0.05, wet=0.35)
for k in BUYUK: add(hisirti(1.5), k - 0.5, gain=0.085, wet=0.4); add(derin(), k + 0.35, gain=0.5, wet=0.35)
add(derin(), 0.15, gain=0.4, wet=0.3)
for tb, f, pn in [(3.9, 293.66, -0.25), (13.9 + 0.5, 392.0, 0.2), (29.6, 293.66, -0.2), (30.4, 440.0, 0.25), (31.4, 587.33, 0.0)]:
    add(can(f), tb, gain=0.05, pan=pn, wet=0.6)

# ---- hafif mekanik sesler
def role():                                    # ışık devresi: alçak "tok" ve kısa tık
    t = tt(0.5); tok = np.sin(2 * math.pi * np.cumsum(70 + 60 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.09)
    tik = filt(noise(0.5), lo=1800, hi=6000) * np.exp(-t / 0.006) * 0.5
    ugul = np.sin(2 * math.pi * 100 * t) * np.exp(-t / 0.25) * 0.25
    return tok + tik + ugul
for k, ts in enumerate(ISIK): add(role(), ts, gain=0.16, pan=-0.5 + k * 0.33, wet=0.5)
def servo(dur, f=300):                         # kulenin yavaş dönüşü
    t = tt(dur); s = saw(f * (1 + 0.05 * np.sin(2 * math.pi * 0.9 * t)), t) * 0.6 + noise(dur) * 0.2
    return filt(s, lo=240, hi=1500) * ramp(len(t), 0.35, 0.5)
add(servo(2.1), 1.2, gain=0.02, pan=0.2, wet=0.3)
for ts, d in ((14.4, 1.4), (17.5, 1.2), (20.5, 1.2)): add(servo(d, 270), ts, gain=0.012, pan=0.3, wet=0.3)
def blip(f): t = tt(0.22); return np.sin(2 * math.pi * f * t) * np.exp(-t / 0.05) * ramp(len(t), 0.003, 0.05)
for k, ts in enumerate(GRAFIK): add(blip(1318.5 if k % 2 == 0 else 1760.0), ts, gain=0.022, pan=-0.3 if k % 2 == 0 else 0.3, wet=0.5)

# ---- açık hava ortamları: rüzgâr, tesis uğultusu, deniz; uzakta çok hafif pervane sesi
def ortam(a, b, sig, gain):
    n = int((b - a) * SR); add(sig[:n] * ramp(n, 0.9, 0.9), a, gain=gain)
ruzgar = filt(noise(DUR), lo=70, hi=420) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.11 * t_all + 0.7))
ortam(13.8, 17.4, ruzgar[int(13.8 * SR):], 0.03); ortam(22.6, 29.0, ruzgar[int(22.6 * SR):], 0.03)
th = tt(4.0); ugultu = (np.sin(2 * math.pi * 50 * th) + 0.5 * np.sin(2 * math.pi * 100 * th)) * 0.5 + filt(noise(4.0), lo=90, hi=600) * 0.8; ortam(16.7, 20.3, ugultu, 0.022)
dz = filt(noise(4.0), lo=160, hi=2400) * (0.55 + 0.45 * np.sin(2 * math.pi * 0.25 * tt(4.0) - 1)) ** 2; ortam(19.7, 23.3, dz, 0.045)
t = tt(5.2); f = 190 * (1 + 0.004 * np.sin(2 * math.pi * 4.7 * t)); ph = 2 * math.pi * np.cumsum(f) / SR
pervane = sum(np.sin(h * ph + h) / h ** 1.2 for h in range(1, 6)) * (1 + 0.4 * np.sin(2 * math.pi * 88 * t))
add(filt(pervane, hi=1400) * ramp(len(t), 1.6, 1.4), 23.4, gain=0.012, pan=-0.6, wet=0.5)

# ---- yankı ve ana çıkış
def yanki(x, seed, decay=2.2):
    r = np.random.default_rng(seed); n = int(decay * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t / (decay / 5.5)); ir[:int(0.014 * SR)] = 0
    ir = np.fft.irfft(np.fft.rfft(ir) * (1 / np.sqrt(1 + (np.fft.rfftfreq(n, 1 / SR) / 3600) ** 4)), n)
    m = 1 << int(math.ceil(math.log2(len(x) + n))); y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    return y / (np.sqrt(np.sum(ir ** 2)) + 1e-9)
L += yanki(WL, 1) * 0.6; R += yanki(WR, 2) * 0.6
mix = np.stack([filt(L, lo=24), filt(R, lo=24)])
mix *= np.interp(t_all, [0, 0.3, 33.4, 35.0], [0, 1, 1, 0])
mix = np.tanh(mix * 1.2) / 1.2; mix *= 0.89 / np.max(np.abs(mix))
cikti = sys.argv[1] if len(sys.argv) > 1 else 'urunfilmi-ses.wav'
with wave.open(cikti, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
db = lambda x: round(20 * math.log10(max(1e-9, float(np.sqrt(np.mean(x ** 2))))), 1)
print('tepe', round(float(np.max(np.abs(mix))), 3), '| rms dBFS', {f'{a:g}-{b:g}': db(mix[:, int(a * SR):int(b * SR)]) for a, b in [(0, 7), (7, 14), (14, 23), (23, 29), (29, 35)]})
