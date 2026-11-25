# Dron Kalkanı · Drone Shield — Tanıtım Filmi

Turaç liderliğindeki **Dron Kalkanı** (Drone Shield) otonom robotik anti-dron kule sistemi için 88 saniyelik tanıtım filmi. Film, gerçek saha fotoğrafları üzerine tarayıcıda çizilen animasyon katmanlarından oluşur; tarayıcıda oynatılır veya MP4 olarak render edilir. Güncel sürüm v10, iki ayrı çalışmanın ortak kurgusudur ve gerçek kule modeliyle bir 3B çekim içerir; ürün bilgileri ve uyulan kurallar `PROJE-OZETI.md` içindedir.

```
PROJE-OZETI.md           Projenin tek sayfalık özeti: sürümler, bağlantılar, açık konular.
animasyon/index.html     Film (HTML5 Canvas). Tarayıcıda açın; oynatıcı ve sahne çipleri içerir.
animasyon/assets/        Fotoğraf plakaları, temiz plakalar, alfa kanallı taret kesmeleri ve logolar.
render/render.mjs        Playwright + ffmpeg ile 1080p MP4 render betiği.
render/3d/sahneler.py    Gemi güvertesi ve rafineri kulesi için 3B arka plan plakaları (Blender bpy, Cycles).
render/3d/dron3b.py      3B dron modeli: film için dron görünümleri ve 3B sahnelerde hedef dron.
render/3d/kule_parcala.py   Kule CAD modelini parçalara ayırır, dönüş eksenlerini bulur, aynalamayı düzeltir (modeller/kule-parcalar.npz).
render/3d/urunfilmi.py      Ürün filminin 3B çekimleri; urunfilmi_topla.py renderları kurgu sayfasına toplar.
render/3d/pikap3b.py        Kodla kurulan çift kabin pikap ve açık arazi (ürün filminin gökyüzü çekimi).
render/rotus/pikap_studyo.py   Ürün filminin araç çekimi: aracın stüdyo render'ını temizler, kamerasını çözer, 3B kule katmanlarını bindirir.
urunfilmi/                  Ürün filmi (35 sn): kurgu sayfası ve görüntüleri. Ayrıntı: docs/URUN-FILMI.md
simulasyon/                 3B simülasyon filmi (70 sn): tehdit, katmanlar; arazide araç, gemi, rafineri. Ayrıntı: docs/SIMULASYON-FILMI.md
render/3d/simfilm.py        Simülasyon filminin Blender tarafı: kule ve namlu konumları, kulenin dönüş kareleri.
render/rotus/sim_kareler.py Kule dönüş karelerini arka plana bindirir.
render/ses/simulasyon_ses.py   Simülasyon filminin sentez ses bandı.
render/3d/kule3b.py      Gerçek kule CAD modeliyle stüdyo çekimi: sahne 04'teki 3B yörünge kareleri (animasyon/assets/kule3b/).
render/3d/taret3b.py     Tamamı 3B deneme: fotoğraflardan sadeleştirilmiş taret, pikap ve arazi; pilot çekim.
render/3d/ucmf.py        Bambu Studio 3MF proje dosyalarını okur (parça ağları ve yerleşimleri).
render/3d/modeller/      3B ağlar (dron.npz, taret.glb).
surumler/                Bütün film sürümlerinin dizini; videolar burada durur ama sürüm kontrolüne girmez.
render/ses/ses.py        Sentezlenmiş ses bandı: müzik yatağı ve efektler (yalnızca numpy).
render/rotus/rotus.py    Fotoğraflardan başka firma işaretlerini ve plakayı siler (opencv).
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

## 3B plakalar ve ses

Gemi ve rafineri sahnelerinin ortamı Blender ile render edilir; taretin kendisi gerçek fotoğraf kesmesidir ve film motorunda render'ın verdiği noktaya oturtulur.

```
python3 -m venv /root/bpyenv && /root/bpyenv/bin/pip install bpy numpy     # bir kez (~1 GB)
/root/bpyenv/bin/python render/3d/sahneler.py gemi --kalite final --cikti animasyon/assets
/root/bpyenv/bin/python render/3d/sahneler.py rafineri --kalite final --cikti animasyon/assets
```

Ses bandı sentezdir (kayıt ya da telifli malzeme yok). Zamanlar film motorundaki olaylarla eşlidir.

```
python3 render/ses/ses.py render/out/ses.wav
ffmpeg -y -i render/out/ses.wav -af "volume=4.4dB,lowpass=f=15500,alimiter=limit=0.66:attack=2:release=80:level=disabled" -c:a libmp3lame -b:a 160k animasyon/assets/ses.mp3
node render/render.mjs            # ses bandı otomatik eklenir; --sessiz ile eklenmez
```

## Sahneler

| # | Zaman | Sahne |
|---|------:|-------|
| 01 | 0:00 | Açılış · DRON KALKANI, "Karıştırıcının bittiği yerde başlar." |
| 02 | 0:07 | Sorun · karıştırıcıyı aşan dron sürüsü |
| 03 | 0:15 | Tespit ve takip · pasif elektro-optik ve akustik sensörler, gömülü yapay zekâ |
| 04 | 0:24 | Robotik kule · parça açıklamaları, gerçek CAD modeliyle 3B yörünge çekimi, otonom çalışma |
| 05 | 0:34 | Angajman · dronu izleyen kule, son 150 metrede atış, 3 hedef |
| 06 | 0:48 | Araçta (fotoğraf) · gemide ve kulede (3B render) |
| 07 | 1:02 | Katmanlı savunma · gökyüzü ağ katmanları ve beş kubbe, en içte Dron Kalkanı |
| 08 | 1:14 | Ortak yapım · dört firma ve İTÜ ARC |
| 09 | 1:21 | Kapanış · "Son 150 metre bizim.", değerler, dronkalkani.com.tr |

Ürün değerleri: tespit ve takip 600–800 m, angajman 150 m. Ayrıntı için `docs/SENARYO.md`.
