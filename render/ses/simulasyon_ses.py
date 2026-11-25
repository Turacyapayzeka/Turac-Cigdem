"""Dron Kalkanı 3B simülasyon filmi (66 sn) için sentezlenmiş ses bandı.

    python3 render/ses/simulasyon_ses.py render/out/simulasyon-ses.wav
    ffmpeg -i render/out/simulasyon-ses.wav -af loudnorm=I=-17:TP=-1.5:LRA=11 -b:a 192k simulasyon/assets/ses.mp3

Zamanlar simulasyon/index.html içindeki kurguyla aynıdır. Tamamı sentezdir; kayıt ya da telifli malzeme yoktur.
"""
import sys, math, wave
import numpy as np

SR = 48000; DUR = 66.0; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N); WL = np.zeros(N); WR = np.zeros(N)
rng = np.random.default_rng(23); t_all = np.arange(N) / SR

KESME = [6.0, 16.0, 33.0, 41.5, 51.0, 60.5]                # bölüm geçişleri
ARA = [19.0, 20.0, 22.2, 23.0, 23.6, 26.4, 28.9, 43.5, 44.5, 47.0, 48.7, 53.0, 54.0, 56.5, 58.2]      # bölüm içi çekim değişimleri
KUBBE = [6.6 + i * 0.5 for i in range(5)]                   # katman kubbelerinin belirişi (dıştan içe)
DURDUR = [10.3 + i * 0.5 for i in range(5)]                 # her tehdidin kendi katmanında durdurulması
PARCA = [34.2, 35.35, 36.5, 37.65]                          # kule tanıtımında parça yazıları
# platformlar: (ortam, tespit, kule dönüşünün başı, kilit, yaklaşan dron sesinin başı, eş zamanlı atışlar, vuruş, düşüş, saha temiz)
PLATFORM = [('arazi', 19.47, 20.0, 20.9, 19.0, [23.4, 24.15], 24.25, 25.15, 25.35), ('deniz', 43.82, 44.5, 45.4, 43.5, [46.6, 46.85], 47.05, 47.85, 48.15),
            ('tesis', 53.32, 54.0, 54.9, 53.0, [56.1, 56.35], 56.55, 57.4, 57.65)]

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

# ---- atmosfer: alçak, gergin pad; kapanışta majöre çözülür
BOLUM = [(0.0, 6.0, 32.7, 'm'), (6.0, 16.0, 36.71, 'm'), (16.0, 33.0, 32.7, 'm'), (33.0, 41.5, 43.65, 'M'), (41.5, 51.0, 41.2, 'm'), (51.0, 60.5, 32.7, 'm'), (60.5, 66.0, 36.71, 'M')]
pad = np.zeros(N); alt = np.zeros(N)
for a, b, f, kip in BOLUM:
    i0 = max(0, int((a - 1.2) * SR)); i1 = min(N, int((b + 1.2) * SR)); t = t_all[i0:i1]; env = ramp(i1 - i0, 2.2, 2.2)
    tonlar = [f, f * 2, f * 3, f * 4 * (2 ** ((4 if kip == 'M' else 3) / 12)) / 2, f * 6]; s = np.zeros(i1 - i0)
    for k, ton in enumerate(tonlar):
        for det in (-0.003, 0.003): s += saw(ton * (1 + det), t, ph=rng.random()) * (0.9 if k == 0 else 0.5) / (1 + 0.4 * k)
    pad[i0:i1] += s * env
    j0 = max(0, int((a - 0.6) * SR)); j1 = min(N, int((b + 0.6) * SR)); alt[j0:j1] += np.sin(2 * math.pi * f * t_all[j0:j1]) * ramp(j1 - j0, 1.2, 1.2)
pad = filt(pad, lo=30, hi=360, order=2) * (0.8 + 0.2 * np.sin(2 * math.pi * 0.07 * t_all))
kazanc = np.interp(t_all, [0, 1.5, 6, 16, 60.5, 62, 64.5, 66], [0.0, 0.75, 0.8, 0.85, 0.85, 1.0, 0.8, 0.0])
L += (pad * 0.05 + alt * 0.05) * kazanc; R += (np.roll(pad, 337) * 0.05 + alt * 0.05) * kazanc
nabiz = np.zeros(N)                                           # katman ve simülasyon bölümlerinde yavaş nabız
for ts in np.arange(6.5, 60.0, 1.5):
    t = tt(0.5); i = int(ts * SR); nabiz[i:i + len(t)] += np.sin(2 * math.pi * np.cumsum(52 + 30 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.12)
L += nabiz * 0.05; R += nabiz * 0.05

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
def blip(f, dur=0.22, tau=0.05): t = tt(dur); return np.sin(2 * math.pi * f * t) * np.exp(-t / tau) * ramp(len(t), 0.003, 0.05)
def servo(dur, f=300):
    t = tt(dur); s = saw(f * (1 + 0.05 * np.sin(2 * math.pi * 0.9 * t)), t) * 0.6 + noise(dur) * 0.2
    return filt(s, lo=240, hi=1500) * ramp(len(t), 0.25, 0.35)
def atis(ortam):
    t = tt(1.4); tik = noise(1.4) * np.exp(-t / 0.0015) * 1.6; govde = filt(noise(1.4), lo=180, hi=5200) * np.exp(-t / 0.045) * 1.4
    vurus = np.sin(2 * math.pi * np.cumsum(46 + 70 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.09) * 1.3
    kuyruk = filt(noise(1.4), lo=150, hi={'arazi': 2600, 'deniz': 3200, 'tesis': 4200}[ortam]) * np.exp(-t / {'arazi': 0.42, 'deniz': 0.5, 'tesis': 0.34}[ortam]) * 0.42
    return tik + govde + vurus + kuyruk
def carpma():
    t = tt(1.2); return filt(noise(1.2), lo=300, hi=3800) * np.exp(-t / 0.07) * 1.2 + np.sin(2 * math.pi * np.cumsum(90 + 120 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.12)
def pervane(dur):
    t = tt(dur); f = 190 * (1 + 0.004 * np.sin(2 * math.pi * 4.7 * t)) * (1 + 0.1 * t / dur); ph = 2 * math.pi * np.cumsum(f) / SR
    s = sum(np.sin(h * ph + h) / h ** 1.2 for h in range(1, 6)) * (1 + 0.4 * np.sin(2 * math.pi * 88 * t)); return filt(s, hi=1800) * (t / dur) ** 1.6 * ramp(len(t), 0.4, 0.04)

# ---- açılış: altı saniyelik geri sayım, yaklaşan FPV dron, yanından geçiş
add(derin(), 0.2, gain=0.36, wet=0.3)
t = tt(5.7); f = 170 * (1 + 0.9 * (t / 5.7) ** 3) * (1 + 0.004 * np.sin(2 * math.pi * 4.7 * t)); ph = 2 * math.pi * np.cumsum(f) / SR
vin = sum(np.sin(h * ph + h) / h ** 1.1 for h in range(1, 7)) * (1 + 0.4 * np.sin(2 * math.pi * 88 * t)); add(filt(vin, hi=2600) * (0.08 + (t / 5.7) ** 2.4) * ramp(len(t), 0.5, 0.05), 0.15, gain=0.085, pan=0.0, wet=0.3)
for k in range(1, 6): add(blip(880.0 if k < 5 else 1318.5, 0.16, 0.035), float(k), gain=0.028, pan=0.5, wet=0.3)
add(hisirti(0.7), 5.45, gain=0.16, wet=0.4)
for k in KESME: add(hisirti(1.3), k - 0.45, gain=0.075, wet=0.4); add(derin(), k + 0.25, gain=0.36, wet=0.35)
for k in ARA: add(hisirti(0.5), k - 0.18, gain=0.035, wet=0.3)
for i, ts in enumerate(KUBBE): add(can([146.83, 174.61, 196.0, 220.0, 293.66][i], 3.0), ts, gain=0.045 if i < 4 else 0.07, pan=-0.4 + i * 0.2, wet=0.6); add(blip(1318.5), ts + 0.3, gain=0.016, pan=0.3, wet=0.5)
for i, ts in enumerate(DURDUR): add(blip(880.0 if i < 4 else 1318.5, 0.3, 0.07), ts, gain=0.03, pan=-0.5, wet=0.5); add(carpma(), ts, gain=0.035, pan=-0.5, wet=0.4)
add(can(587.33), 12.7, gain=0.05, wet=0.6)
for k, ts in enumerate(PARCA): add(blip(1318.5 if k % 2 == 0 else 1760.0), ts, gain=0.024, pan=-0.3, wet=0.5)
add(servo(1.6, 270), 33.4, gain=0.012, pan=0.3, wet=0.3)

# ---- platformlar: tespit sinyali, kulenin dönüşü, kilit, yaklaşan pervane sesi, eş zamanlı atış, vuruş ve düşüş
def ort(a, b, sig, gain):
    n = int((b - a) * SR); add(sig[:n] * ramp(n, 0.7, 0.7), a, gain=gain)
for ortam, tespit, don, kilit, bas, atislar, vur, dus, temiz in PLATFORM:
    add(blip(987.77, 0.5, 0.11), tespit, gain=0.035, pan=-0.3, wet=0.55); add(blip(987.77, 0.5, 0.11), tespit + 0.25, gain=0.03, pan=-0.3, wet=0.55)
    add(servo(0.9, 310), don, gain=0.024, pan=0.35, wet=0.3)
    add(blip(1318.5, 0.18, 0.04), kilit, gain=0.035, wet=0.4); add(blip(1760.0, 0.3, 0.06), kilit + 0.12, gain=0.035, wet=0.4)
    add(pervane(vur - bas), bas, gain=0.034, pan=-0.5, wet=0.4)
    for ta in atislar: add(atis(ortam), ta, gain=0.5, pan=0.3, wet=0.35); add(atis(ortam), ta + 0.012, gain=0.42, pan=-0.1, wet=0.35)       # iki namlu aynı anda
    add(carpma(), vur, gain=0.2, pan=-0.4, wet=0.5); add(derin(0.6), dus, gain=0.22, pan=-0.3, wet=0.4)
    add(can(392.0, 2.5), temiz, gain=0.04, wet=0.6); add(can(587.33, 2.5), temiz + 0.18, gain=0.03, pan=0.2, wet=0.6)
    if ortam == 'arazi': rz = filt(noise(17.0), lo=70, hi=420) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.11 * tt(17.0) + 0.7)); ort(16.2, 33.0, rz, 0.03)
    if ortam == 'deniz': dz = filt(noise(10.0), lo=160, hi=2400) * (0.55 + 0.45 * np.sin(2 * math.pi * 0.25 * tt(10.0) - 1)) ** 2; ort(41.7, 51.2, dz, 0.03)
    if ortam == 'tesis': th = tt(10.0); ug = (np.sin(2 * math.pi * 50 * th) + 0.5 * np.sin(2 * math.pi * 100 * th)) * 0.5 + filt(noise(10.0), lo=90, hi=600) * 0.8; ort(51.2, 60.6, ug, 0.018)

# ---- kapanış
for tb, f, pn in [(61.1, 293.66, -0.2), (61.9, 440.0, 0.25), (62.8, 587.33, 0.0)]: add(can(f), tb, gain=0.055, pan=pn, wet=0.6)

def yanki(x, seed, decay=2.2):
    r = np.random.default_rng(seed); n = int(decay * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t / (decay / 5.5)); ir[:int(0.014 * SR)] = 0
    ir = np.fft.irfft(np.fft.rfft(ir) * (1 / np.sqrt(1 + (np.fft.rfftfreq(n, 1 / SR) / 3600) ** 4)), n)
    m = 1 << int(math.ceil(math.log2(len(x) + n))); y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    return y / (np.sqrt(np.sum(ir ** 2)) + 1e-9)
L += yanki(WL, 1) * 0.6; R += yanki(WR, 2) * 0.6
mix = np.stack([filt(L, lo=24), filt(R, lo=24)])
mix *= np.interp(t_all, [0, 0.3, 64.6, 66.0], [0, 1, 1, 0])
mix = np.tanh(mix * 1.2) / 1.2; mix *= 0.89 / np.max(np.abs(mix))
cikti = sys.argv[1] if len(sys.argv) > 1 else 'simulasyon-ses.wav'
with wave.open(cikti, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
db = lambda x: round(20 * math.log10(max(1e-9, float(np.sqrt(np.mean(x ** 2))))), 1)
print('tepe', round(float(np.max(np.abs(mix))), 3), '| rms dBFS', {f'{a:g}-{b:g}': db(mix[:, int(a * SR):int(b * SR)]) for a, b in [(0, 6), (6, 16), (16, 33), (33, 41.5), (41.5, 51), (51, 60.5), (60.5, 66)]})
