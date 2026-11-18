# Dron Kalkanı 3B Simülasyon Filmi (60 sn)

Hava savunma katmanlarını ve Dron Kalkanı'nın üç platformdaki çalışmasını (araç üstü, gemi güvertesi, rafineri) gösteren simülasyon filmi. Önceki filmlerden ayrı, sıfırdan kurulmuş bir çalışmadır (18 Kasım 2026).

**Süre:** 60 saniye · **Format:** 1920×1080, 24 fps, sesli · **Sayfa:** `simulasyon/index.html`

## İstek

Kullanıcının 18 Kasım 2026 tarihli isteği, kendi sözleriyle:

- "yeni bir film yapacağız", "tamamen 3d simülasyon"
- "hava savunma katmanları olacak"
- "araç üstü", "gemi güvertesi ve rafineride 3 boyutlu simülasyon olacak"
- "en son araç render'ın uygundu" (araç için kullanıcının stüdyo render'ı, kasasında 3B kule)
- "tekrar videoları ve web sitelerini inceleyerek yeniden kurgula"

Süre, kadraj ve görünüm sorulduğunda seçim yapılmadı; 60 saniye, yatay 16:9 ve aşağıdaki görünüm benim kararımdır.

## İncelenen önceki çalışmalar

Kurgudan önce depodaki videolar ve web sayfaları yeniden incelendi (`surumler/ilk-calismalar/`):

| Çalışma | Alınan |
|---|---|
| Simülasyon (28 Ekim; web sayfası ve video) | Durum akışı: arama, tespit ve kilitlenme, takip, angajman, etkisiz, saha temiz. Gösterge paneli (menzil, irtifa, kule açıları), elektro-optik pencere, menzil çubuğu. |
| 3B Vitrin (2 ve 6 Kasım; web sayfaları ve videolar) | Üç platform sırası (araç, gemi, tesis), 600–800 m tespit ve 150 m angajman kubbeleri, platform cümleleri, kapanış sloganı ve ortak yapım satırı. |
| Tanıtım filmi v10 | Beş hava savunma katmanı: solda tehdit, sağda çözüm, en içte Dron Kalkanı; metinleri. |
| Ürün filmi | Aracın stüdyo render'ı üstüne kurulan araç çekimi; gemi güvertesi ve tesis platformu sahneleri. |

`dronkalkani.com.tr` ve `sterling.com.tr` bu ortamdan açılamadı (ağ ayarı izin vermiyor); bu siteler incelenemedi.

## Bölümler

| Zaman | Bölüm | Görüntü | Yazı |
|---|---|---|---|
| 0–5 sn | Açılış | Koyu taktik zemin; dronlar yaklaşır. | DRON KALKANI · Katmanlı hava savunma · 3B simülasyon |
| 5–17,5 sn | Katmanlar | Beş kubbe dıştan içe belirir. Solda tehditler, sağda çözümler. Her tehdit kendi katmanında durdurulur; küçük dronlar karıştırıcıyı da geçer ve son katmanda durur. | Hava savunması katmanlıdır. · Karıştırıcı her dronu durduramaz. · Son katman: Dron Kalkanı. |
| 17,5–31 sn | Araç üstü | Aracın yakın planı; ardından taktik görünüm: 600–800 m tespit halkası, 150 m angajman kubbesi, yaklaşan dron. Yakın plan köşede kule kamerası olarak sürer; kule hedefe döner ve ateş eder. | PLATFORM 1 / 3 · ARAÇ ÜSTÜ · Pikap kasasında, tripod üstünde. |
| 31–43 sn | Gemi güvertesi | Aynı akış denizde; taktik görünümde gemi. | PLATFORM 2 / 3 · GEMİ GÜVERTESİ · Kargo gemisi ve tanker güvertesinde. |
| 43–55 sn | Rafineri | Aynı akış tesiste; iki dron art arda. | PLATFORM 3 / 3 · RAFİNERİ · Rafinerilerde ve kritik tesislerde sabit kurulum. |
| 55–60 sn | Kapanış | 150 m kubbesi, logo. | Son 150 metre bizim. · dronkalkani.com.tr · ortak yapım satırı |

Her platformda simülasyon aynı sırayla ilerler: **arama → tespit ve kilitlenme → takip → 150 metrede angajman → etkisiz → saha temiz**. Türkçe yazılar büyük, İngilizceleri altında küçüktür.

## Görünüm

Filmde iki tür görüntü vardır:

- **Yakın plan (fotoğraf gerçekliğinde 3B):** araçta kullanıcının stüdyo render'ı ve kasasına yerleştirilen gerçek kule modeli; gemide ve tesiste Blender sahneleri. Kulenin hedefe dönüşü, takibi ve geri tepmesi önceden render edilmiş pozlardır (platform başına 41 poz).
- **Taktik görünüm (3B şema):** koyu zemin üstünde paralel izdüşümlü bir 3B uzay. Kubbeler, halkalar, dronların uçuş yolu, gemi ve tesis gövdeleri metre ölçüsünde hesaplanıp çizilir. Tespit halkası (600–800 m) ve angajman kubbesi (150 m) ölçeklidir.

## Nasıl üretildi

1. **Kule ve namlu konumları.** `render/3d/simfilm.py capa`: yakın planlarda kulenin ve namlu uçlarının görüntüdeki yerleri (`simulasyon/assets/sahne.json`).
2. **Kule hareketi.** `render/3d/simfilm.py kareler --platform arac|gemi|tesis`: her poz için kule katmanı. Araçta sabit kısım (tripod, kaide) bir kez, dönen kısım her pozda render edilir; gemi ve tesiste önce kulesiz arka plan, sonra saydam kule katmanları alınır. `render/rotus/sim_kareler.py` katmanları arka plana bindirir ve sayfanın klasörüne yazar.
3. **Kurgu ve simülasyon.** `simulasyon/index.html`: zaman çizelgesi, taktik görünümün 3B izdüşümü, dronların hareketi, göstergeler ve yazılar. Aynı sayfa hem oynatıcıdır hem de videonun kaynağıdır.
4. **Ses.** `render/ses/simulasyon_ses.py`: alçak atmosfer, tespit ve kilit sinyalleri, kule dönüşü, yaklaşan pervane sesi, atışlar. Tamamı sentezdir.

```
/root/bpyenv/bin/python render/3d/simfilm.py capa --cikti simulasyon/assets
for p in arac gemi tesis; do /root/bpyenv/bin/python render/3d/simfilm.py kareler --platform $p; done
python3 render/rotus/sim_kareler.py arac gemi tesis
python3 render/ses/simulasyon_ses.py render/out/simulasyon-ses.wav
ffmpeg -i render/out/simulasyon-ses.wav -af loudnorm=I=-17:TP=-1.5:LRA=11 -b:a 192k simulasyon/assets/ses.mp3
node render/render.mjs --sayfa simulasyon --out surumler/simulasyon-filmi-60sn.mp4
node render/render.mjs --sayfa simulasyon --sorgu temiz=1 --out surumler/simulasyon-filmi-60sn-yazisiz.mp4
```

Araç pozları, ürün filminin araç çekimi için hazırlanan dosyaları kullanır (`render/out/urunfilmi/pikap/`: `plaka.png`, `kamera.json`); önce `render/rotus/pikap_studyo.py hazirla` çalışmış olmalıdır.

## Bilinmesi gerekenler

- **Simülasyon hızlandırılmıştır.** Dron 830 metreden 150 metreye yaklaşık dört saniyede gelir; gerçek hızın birkaç katıdır. Ekranda "Hızlandırılmış simülasyon" notu durur.
- **Katman kubbeleri ölçekli değildir.** Beş katman şematiktir; ekranda not vardır. Platform bölümlerindeki 600–800 m halkası ve 150 m kubbesi ölçeklidir.
- **Araç tek açıdan görünür.** Aracın 3B modeli yok; yakın plan kullanıcının stüdyo render'ına dayanır. Taktik görünümde araç küçük bir gövdeyle temsil edilir.
- **Taktik görünüm şematiktir.** Gemi ve tesis gövdeleri sade hacimlerdir; fotoğraf gerçekliği yakın planlardadır.
- **Vuruş mesafesi, irtifa ve açı değerleri temsilîdir.** Göstergelerdeki sayılar simülasyonun kendi hesabıdır; ölçüm değildir. Ürün değerleri olarak yalnızca 600–800 m tespit ve 150 m angajman kullanıldı.
- **Sensör ünitesi ve tripod temsilîdir** (ürün filmindeki gibi).
- **Ses** ölçümle doğrulandı, kulakla dinlenmedi.
