"""Drone Shield filmi için sentezlenmiş ses bandı (müzik yatağı + efektler). Yalnızca numpy gerekir.

    python render/ses/ses.py render/out/ses.wav

Zamanlar animasyon/index.html içindeki sahne ve olay zamanlarıyla aynıdır; film değişirse buradaki tablo da güncellenmeli.
Tüm sesler sentezdir; kayıt ya da telifli malzeme yoktur.
"""
import sys, math, wave
import numpy as np

SR = 48000; DUR = 88.0; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)            # ana çıkış
WL = np.zeros(N); WR = np.zeros(N)          # yankıya giden efekt yolu
rng = np.random.default_rng(7)

# ---- film zaman çizelgesi
CUTS = [7.0, 15.0, 24.0, 34.0, 48.0, 62.0, 74.0, 81.0]
VCUTS = [52.667, 57.333, 69.1]
SHOTS = [(38.3, 'saha'), (41.0, 'saha'), (44.0, 'saha'), (51.4, 'saha'), (56.067, 'gemi'), (60.733, 'rafineri'), (72.4, 'saha')]
DRONES = [(34.3, 38.6), (36.3, 41.3), (39.0, 44.3), (48.4, 51.7), (53.067, 56.367), (57.733, 61.033), (69.7, 72.7)]
CALLOUTS = [24.6, 25.3, 26.0, 26.7, 27.4]
LAYERS = [62.4, 62.7, 63.0, 63.3, 63.5, 64.35, 65.2, 66.05, 66.9]
ORTAK = [75.3, 75.65, 76.0, 76.35, 77.0, 77.7, 77.95, 78.2, 78.45]
STATS = [83.6, 83.9, 84.2, 84.5]

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

# ================================================================ müzik
SECTIONS = [(0.0, 7.0, 73.42), (7.0, 11.0, 73.42), (11.0, 15.0, 58.27), (15.0, 24.0, 49.0), (24.0, 34.0, 58.27), (34.0, 48.0, 73.42),
            (48.0, 52.667, 87.31), (52.667, 57.333, 65.41), (57.333, 62.0, 55.0), (62.0, 69.0, 58.27), (69.0, 74.0, 65.41), (74.0, 81.0, 87.31), (81.0, 88.0, 73.42)]
def root_at(t):
    for a, b, f in SECTIONS:
        if a <= t < b: return f
    return 73.42
# --- pad: akor sesleri, hafif akortsuz testere çiftleri, alçak geçiren
pad = np.zeros(N); t_all = np.arange(N) / SR
for a, b, f in SECTIONS:
    i0 = max(0, int((a - 0.9) * SR)); i1 = min(N, int((b + 0.9) * SR)); t = t_all[i0:i1]; env = ramp(i1 - i0, 1.8, 1.8)
    minor = f not in (58.27, 87.31, 65.41)                       # Bb, F, C majör; diğerleri minör
    tones = [f, f * 1.5, f * 2, f * 2 * (2 ** ((3 if minor else 4) / 12)), f * 3]
    s = np.zeros(i1 - i0)
    for k, tone in enumerate(tones):
        for det in (-0.0035, 0.0035):
            s += saw(tone * (1 + det), t, ph=rng.random()) * (0.5 if k else 0.8) / (1 + 0.35 * k)
    pad[i0:i1] += s * env
pad = filt(pad, lo=40, hi=420, order=2) * (0.82 + 0.18 * np.sin(2 * math.pi * 0.09 * t_all))
sub = np.zeros(N)
for a, b, f in SECTIONS:
    i0 = max(0, int((a - 0.4) * SR)); i1 = min(N, int((b + 0.4) * SR)); sub[i0:i1] += np.sin(2 * math.pi * (f / 2) * t_all[i0:i1]) * ramp(i1 - i0, 0.8, 0.8)
music_gain = np.interp(t_all, [0, 1.5, 7, 34, 48, 62, 74, 81, 86.5, 88], [0.0, 0.8, 0.75, 0.9, 0.85, 0.9, 0.85, 1.0, 0.7, 0.0])
L += (pad * 0.042 + sub * 0.04) * music_gain; R += (np.roll(pad, 311) * 0.042 + sub * 0.04) * music_gain

# --- nabız: sekizlik ostinato
BEAT = 60 / 96; STEP = BEAT / 2
def pluck(f, dur=0.34):
    t = tt(dur); s = np.zeros(len(t))
    for k in range(1, 8): s += np.sin(2 * math.pi * k * f * t) / k * np.exp(-t / (0.22 / k ** 0.8))
    return s * ramp(len(t), 0.004, 0.05)
def pulse_level(t):
    return float(np.interp(t, [7, 9, 15, 24, 33, 34, 48, 52.6, 62, 73.5, 74.2, 80.4, 81.2], [0.0, 0.16, 0.14, 0.17, 0.2, 0.36, 0.3, 0.27, 0.33, 0.36, 0.18, 0.2, 0.0]))
PAT = [0, 0, 7, 0, 0, 12, 7, 0]; VEL = [1.0, 0.55, 0.75, 0.5, 0.9, 0.55, 0.7, 0.5]
k = 0; tcur = 7.0
while tcur < 81.2:
    lv = pulse_level(tcur)
    if lv > 0.01:
        f = root_at(tcur) * 2 * 2 ** (PAT[k % 8] / 12); add(pluck(f), tcur, gain=lv * VEL[k % 8] * 0.5, pan=0.25 if k % 2 else -0.25, wet=0.15)
    k += 1; tcur += STEP
# --- vurmalı: bölümlerde kick, sahne girişlerinde derin vuruş
def kick():
    t = tt(0.32); f = 44 + 72 * np.exp(-t / 0.028); return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11)
for a, b, lv in ((34.0, 48.0, 0.34), (48.0, 62.0, 0.2), (62.0, 74.0, 0.3)):
    tcur = a
    while tcur < b - 0.05: add(kick(), tcur, gain=lv); tcur += BEAT
def boom(level=1.0):
    t = tt(1.9); f = 36 + 26 * np.exp(-t / 0.07); body = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t / 0.55)
    tr = filt(noise(1.9), hi=260) * np.exp(-t / 0.16) * 2.2; return (body + tr) * level
for tb, lv in [(0.5, 0.55), (1.6, 0.4)] + [(c, 0.5) for c in CUTS[:-1]] + [(v, 0.3) for v in VCUTS] + [(81.3, 0.65), (82.0, 0.45)]:
    add(boom(), tb, gain=lv, wet=0.3)
# --- yükselişler ve çanlar
def riser(dur):
    t = tt(dur); n = filt(noise(dur), lo=900, hi=7000) * (t / dur) ** 2.2; sw = np.sin(2 * math.pi * np.cumsum(180 + 620 * (t / dur) ** 2) / SR) * (t / dur) ** 2 * 0.5
    return (n * 0.6 + sw) * ramp(len(t), 0.1, 0.03)
add(riser(2.6), 31.4, gain=0.16, wet=0.3); add(riser(1.5), 79.75, gain=0.14, wet=0.3); add(riser(1.2), 5.8, gain=0.08, wet=0.3)
def bell(f, dur=3.2):
    t = tt(dur); s = np.sin(2 * math.pi * f * t) + 0.45 * np.sin(2 * math.pi * 2.76 * f * t) * np.exp(-t / 0.5) + 0.22 * np.sin(2 * math.pi * 5.4 * f * t) * np.exp(-t / 0.2)
    return s * np.exp(-t / 0.9) * ramp(len(t), 0.003, 0.2)
for tb, f, pn in [(1.6, 587.33, -0.3), (2.6, 880.0, 0.3), (3.8, 698.46, 0.0), (82.0, 587.33, -0.3), (83.6, 880.0, 0.3), (84.5, 698.46, 0.0), (85.2, 1174.66, 0.0)]:
    add(bell(f), tb, gain=0.07, pan=pn, wet=0.5)

# ================================================================ efektler
def drone_buzz(dur, f0, rise=0.06, level_exp=2.0, v0=0.03):
    t = tt(dur); p = t / dur; f = f0 * (1 + rise * p) * (1 + 0.006 * np.sin(2 * math.pi * 5.3 * t + rng.random() * 6)); ph = 2 * math.pi * np.cumsum(f) / SR
    s = np.zeros(len(t))
    for h in range(1, 7): s += np.sin(h * ph + rng.random() * 6) / h ** 1.1
    s *= 1 + 0.45 * np.sin(2 * math.pi * (f0 * 0.47) * t)                       # pervane vuruşu
    s += filt(noise(dur), lo=1800, hi=6500) * 0.25                                # hava sesi
    return s * (v0 + (1 - v0) * p ** level_exp)
# sahne 2: altı dronluk sürü yaklaşıyor
for i in range(6):
    t0 = 7.3 + i * 0.7; d = 14.85 - t0; s = drone_buzz(d, 175 + i * 17, rise=0.05, level_exp=1.6) * ramp(int(d * SR), 0.6, 0.35)
    add(s, t0, gain=0.035, pan=-0.7 + i * 0.22)
# sahne 3: termal görüntüde hedefin uzaktan vızıltısı
s = drone_buzz(8.4, 205, rise=0.02, level_exp=0.5, v0=0.5) * ramp(int(8.4 * SR), 1.0, 0.5); add(filt(s, hi=1500), 15.4, gain=0.02, pan=0.5)
# tek tek hedefler
for j, (t0, th) in enumerate(DRONES):
    d = th - t0; s = drone_buzz(d, 185 + (j % 3) * 22, rise=0.08) * ramp(int(d * SR), 0.3, 0.02); add(s, t0, gain=0.075, pan=-0.75 + 0.5 * (j % 2))
    # vuruş: çatırtı, kıvılcım, düşerken alçalan vızıltı
    t = tt(0.9); fall = np.sin(2 * math.pi * np.cumsum((190 + (j % 3) * 22) * np.exp(-t / 0.5)) / SR) * np.exp(-t / 0.35) * (1 + 0.5 * np.sin(2 * math.pi * 31 * t))
    add(fall, th, gain=0.06, pan=-0.3)
    crack = filt(noise(0.25), lo=1500) * np.exp(-tt(0.25) / 0.035); add(crack, th, gain=0.22, pan=-0.3, wet=0.5)
    for q in range(7):
        tq = th + 0.05 + rng.random() * 0.5; ting = np.sin(2 * math.pi * (2500 + rng.random() * 4000) * tt(0.09)) * np.exp(-tt(0.09) / 0.018); add(ting, tq, gain=0.03, pan=rng.uniform(-0.6, 0.2), wet=0.4)
# servo: taretin dönüşleri
def servo(dur, f=360):
    t = tt(dur); s = saw(f * (1 + 0.08 * np.sin(2 * math.pi * 1.3 * t)), t) * 0.6 + noise(dur) * 0.25
    return filt(s, lo=280, hi=1700) * ramp(len(t), 0.06, 0.12)
for t0, d in [(9.2, 1.2)] + [(a + 0.02, 0.7) for a, _ in DRONES] + [(38.62, 0.5), (41.32, 0.5)] + [(17.0, 1.6), (20.0, 0.9)]:
    add(servo(d), t0, gain=0.035, pan=0.55)
# av tüfeği atışı
def shot(kind):
    t = tt(1.6); click = noise(1.6) * np.exp(-t / 0.0015) * 1.6
    body = filt(noise(1.6), lo=180, hi=5200) * np.exp(-t / 0.045) * 1.4
    thump = np.sin(2 * math.pi * np.cumsum(46 + 70 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.09) * 1.3
    tail = filt(noise(1.6), lo=150, hi={'saha': 2600, 'gemi': 3200, 'rafineri': 4200}[kind]) * np.exp(-t / {'saha': 0.42, 'gemi': 0.55, 'rafineri': 0.34}[kind]) * 0.42
    s = click + body + thump + tail
    for dly, g in {'saha': [(0.31, 0.22), (0.68, 0.1)], 'gemi': [(0.12, 0.2)], 'rafineri': [(0.09, 0.32), (0.19, 0.2), (0.33, 0.12)]}[kind]:   # yankılar
        n = int(dly * SR); e = np.zeros(len(s)); e[n:] = filt(s, hi=1800)[:-n] * g; s = s + e
    return s
for ts, kind in SHOTS:
    add(shot(kind), ts, gain=0.5, pan=0.45, wet=0.35)
# radar ve kilit tonları
def ping(f, dur=0.5, tau=0.11): t = tt(dur); return np.sin(2 * math.pi * f * t) * np.exp(-t / tau) * ramp(len(t), 0.002, 0.05)
tp = 15.9
while tp < 20.2: add(ping(1480), tp, gain=0.045, pan=-0.5, wet=0.6); tp += 1.4
add(ping(1480, 0.2, 0.05), 18.0, gain=0.07, wet=0.3); add(ping(1976, 0.2, 0.05), 18.12, gain=0.07, wet=0.3)
for q in range(3): add(ping(2349, 0.12, 0.04), 20.6 + q * 0.13, gain=0.08, wet=0.3)
for a, _ in DRONES: add(ping(1760, 0.12, 0.03), a + 0.75, gain=0.035, pan=-0.2, wet=0.3)
def tick(): t = tt(0.05); return (filt(noise(0.05), lo=2500) * np.exp(-t / 0.004) + np.sin(2 * math.pi * 3200 * t) * np.exp(-t / 0.012) * 0.6)
for tk in CALLOUTS + LAYERS + ORTAK + STATS + [9.2, 10.4, 29.6]: add(tick(), tk, gain=0.06, pan=-0.2, wet=0.2)
# geçiş hışırtıları
def whoosh(dur=0.8):
    t = tt(dur); a = filt(noise(dur), lo=300, hi=1400) * np.sin(math.pi * t / dur) ** 2; b = filt(noise(dur), lo=1400, hi=6000) * np.sin(math.pi * np.clip(t / dur * 1.3 - 0.3, 0, 1)) ** 2
    return a * 0.7 + b
for c in CUTS: add(whoosh(), c - 0.42, gain=0.08, wet=0.3)
for c in VCUTS: add(whoosh(0.6), c - 0.3, gain=0.05, wet=0.3)
# ortam: rüzgâr (saha), deniz (gemi), tesis uğultusu (rafineri)
def amb(a, b, sig, gain):
    n = int((b - a) * SR); add(sig[:n] * ramp(n, 0.5, 0.5), a, gain=gain)
wind = filt(noise(DUR), lo=60, hi=380) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.13 * t_all + 1) * np.sin(2 * math.pi * 0.047 * t_all))
for a, b in ((0.3, 52.667), (62.0, 74.0)): amb(a, b, wind[int(a * SR):], 0.035)
sea = filt(noise(5.0), lo=180, hi=2600) * (0.55 + 0.45 * np.sin(2 * math.pi * 0.27 * tt(5.0) - 1)) ** 2; amb(52.667, 57.333, sea, 0.05)
th = tt(5.0); hum = (np.sin(2 * math.pi * 50 * th) + 0.5 * np.sin(2 * math.pi * 100 * th) + 0.3 * np.sin(2 * math.pi * 150 * th)) * 0.5 + filt(noise(5.0), lo=90, hi=700) * 0.9
amb(57.333, 62.0, hum, 0.03)

# ================================================================ yankı ve ana çıkış
def reverb(x, seed, decay=1.5):
    r = np.random.default_rng(seed); n = int(decay * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t / (decay / 5.5)); ir[:int(0.012 * SR)] = 0
    ir = np.fft.irfft(np.fft.rfft(ir) * (1 / np.sqrt(1 + (np.fft.rfftfreq(n, 1 / SR) / 4200) ** 4)), n)
    m = 1 << int(math.ceil(math.log2(len(x) + n))); y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    return y / (np.sqrt(np.sum(ir ** 2)) + 1e-9)
L += reverb(WL, 1) * 0.55; R += reverb(WR, 2) * 0.55
mix = np.stack([filt(L, lo=26), filt(R, lo=26)])
mix *= np.interp(t_all, [0, 0.25, 86.8, 88.0], [0, 1, 1, 0])
mix = np.tanh(mix * 1.25) / 1.25                                   # yumuşak sınırlama
mix *= 0.89 / np.max(np.abs(mix))
out = sys.argv[1] if len(sys.argv) > 1 else 'ses.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
# özet: bölüm bölüm RMS (dBFS)
def db(x): return round(20 * math.log10(max(1e-9, float(np.sqrt(np.mean(x ** 2))))), 1)
print('peak', round(float(np.max(np.abs(mix))), 3), '| rms dBFS', {f'{a:g}-{b:g}': db(mix[:, int(a * SR):int(b * SR)]) for a, b in [(0, 7), (7, 15), (15, 24), (24, 34), (34, 48), (48, 62), (62, 74), (74, 81), (81, 88)]})
