# Drone Shield · Dron Kalkanı — Tanıtım Filmi

Turaç / Sterling **Drone Shield** (Dron Kalkanı) anti-dron taret sistemi için 80 saniyelik tanıtım filmi. Film, gerçek saha fotoğrafları üzerine tarayıcıda çizilen animasyon katmanlarından oluşur; tarayıcıda oynatılır veya MP4 olarak render edilir.

```
animasyon/index.html     Film (HTML5 Canvas). Tarayıcıda açın; oynatıcı ve sahne çipleri içerir.
animasyon/assets/        Fotoğraf plakaları, temiz plakalar, alfa kanallı taret kesmeleri ve logolar.
render/render.mjs        Playwright + ffmpeg ile 1080p MP4 render betiği.
docs/SENARYO.md          Sahne sahne senaryo, zaman kodları, seslendirme metni, üretim notları.
docs/ai-video/           Yapay zekâ videosu için çekim listesi, temiz başlangıç kareleri ve ürün referans fotoğrafları.
docs/kaynak-gorseller/   Referans görseller (afiş, maket).
```

## Filmi izlemek

`animasyon/index.html` dosyasını bir yerel HTTP sunucusundan açın (fotoğraflar `file://` altında da görünür, ancak bazı tarayıcılar kısıtlar):

```
python3 -m http.server 8000 --directory animasyon
# http://localhost:8000
```

Kısayollar: Boşluk oynat/duraklat, ← → 5 sn, sahne çipleri ile atlama.

## MP4 render

Gereksinimler: Node 18+, Playwright (Chromium) ve ffmpeg.

```
npm i -g playwright && npx playwright install chromium   # bir kez
node render/render.mjs                                   # render/out/drone-shield.mp4
node render/render.mjs --stills 2.5,9,17,26,38.55,50,60,67   # tek kareler (render/out/stills/)
node render/render.mjs --start 34 --end 48 --crf 16       # yalnızca bir aralık
node render/render.mjs --clean 1 --stills 13.5,38.2 --stillsdir docs/ai-video/kareler   # HUD'suz temiz kareler
```

Render çıktıları `render/out/` altındadır ve sürüm kontrolüne girmez.

## Sahneler

| # | Zaman | Sahne |
|---|------:|-------|
| 01 | 0:00 | Açılış · logo, DRON KALKANI |
| 02 | 0:07 | Tehdit · tesise yaklaşan dron sürüsü |
| 03 | 0:15 | Tespit ve takip · radar, termal EO/IR, sensör füzyonu |
| 04 | 0:24 | Robotik taret · parça açıklamaları |
| 05 | 0:34 | Angajman · dronu izleyen taret, 150 m'de atış, metal bulutu, 3 hedef |
| 06 | 0:48 | Araç üstü · gemi güvertesi · rafineri kulesi |
| 07 | 1:02 | Hava katmanları · en içteki katman, son savunma hattı |
| 08 | 1:12 | Kapanış · rakamlar, logolar |

Rakamlar basına yansıyan açıklamalardan alınmıştır; yayın öncesi doğrulanmalıdır. Ayrıntı için `docs/SENARYO.md`.
