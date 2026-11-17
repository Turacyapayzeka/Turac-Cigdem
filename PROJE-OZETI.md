# Dron Kalkanı · Drone Shield — Proje Özeti

Son güncelleme: 17 Kasım 2026. Bu belge projeyi başka bir konuşmaya ya da ekibe taşımak için tek başına okunabilir biçimde yazıldı. İki ayrı konuşmanın çalışmasını birleştirir: bu depodaki fotoğraflı film ile "Dron kalkanı simülasyonu" konuşmasındaki filmler ve 3B vitrin.

## Tek bakışta

- **Ne:** Turaç liderliğindeki **Dron Kalkanı** otonom robotik anti-dron kule sistemi için tanıtım filmi.
- **Güncel sürüm:** v10, ortak kurgu ve gerçek kule modeliyle 3B çekim. 88 saniye, 1920×1080, 30 fps, sesli. Türkçe ekran yazıları, altında küçük İngilizce karşılıkları.
- **Yöntem:** Gerçek saha fotoğrafları üzerine tarayıcıda çizilen animasyon katmanları. Sahne 04'te gerçek kule CAD modelinin 3B çekimi. Gemi ve rafineri sahneleri 3B render. Dronlar 3B modelden. Ses sentez.
- **Ürün filmi:** Tanıtım filminden ayrı, fuar ekranı için 35 saniyelik sinematik ürün filmi (17 Kasım). Yazılı ve yazısız iki hâli var. Ayrıntı: `docs/URUN-FILMI.md`.
- **Bekleyen karar:** Ortak kurgunun bundan sonraki yönü: 3B çekim beğenilirse başka sahnelere de taşınsın mı; Vitrin görüntüleri ve teknik çizimler eklensin mi.

## Ürün bilgisi

Kaynak: önceki konuşmanın devir özeti (`surumler/ilk-calismalar/PROJE-OZETI-simulasyon-sohbeti.md`).

| Konu | Bilgi |
|---|---|
| Tespit ve takip menzili | **600–800 m** |
| Angajman menzili | **150 m** |
| Çalışma | Angajman için operatör gerekmez; otonom veya uzaktan kumanda |
| Sensörler | Pasif elektro-optik ve akustik |
| İşlem | Gömülü yapay zekâ, kule üzerinde |
| Silahlar | 2 adet yarı otomatik 12 kalibre tüfek, biri ters monte |
| Mühimmat | Sterling magnum anti-dron mühimmatı (Turaç üretimi) |
| Platformlar | Pikap kasası (tripod üstünde), gemi güvertesi, kule/rafineri |
| Sloganlar | "Son 150 metre bizim." · "Karıştırıcının bittiği yerde başlar." |
| Web | dronkalkani.com.tr |

**Ortak yapım (Turaç liderliğinde):** Turaç (proje lideri, Sterling mühimmatı; 1987'de kuruldu, yılda 200 milyonun üzerinde fişek, %60 ihracat, 90'dan fazla ülke) · Derya Arms (atış birimi, Derya MAX 12 kalibre) · Lasersan (robotik kule ve sensörler) · Urban Savunma (entegrasyon, araç ve güverte montajı) · İTÜ ARC (yapay zekâ).

**Hedef kitle:** Ürünü hiç bilmeyen müşteriler. Anlatım sade ve tanıtıcı.

## Kurallar

Kullanıcının önceki konuşmada koyduğu kurallar. v9 bunların hepsine göre düzeltildi; v10 aynı kuralları korur.

| # | Kural | v9'daki durumu |
|---|---|---|
| 1 | Tespit her yerde 600–800 m, angajman 150 m | Uyuyor. Ürün özetinde olmayan "140 m", "yaklaşık 2 m", "360°", "30×" kaldırıldı. |
| 2 | Başka firma logosu, bayrağı kullanılmaz; fotoğraflarda araç logosu, plaka, Kaiser logosu kadraja girmez. Sterling kalabilir. | Fotoğraflardan araç amblemi, model yazısı, Kaiser logosu ve plaka silindi. Ortak firmalar yalnızca yazıyla anılıyor. |
| 3 | Derya MAX adı yalnızca ortak yapım ve kapanışta geçer; ara sahnelerde "çift 12 kalibre / atış birimi" | Uyuyor. Ad yalnızca 08. sahnede. |
| 4 | İki silahta da dipçik yok | Fotoğraflardaki gerçek kule ve dipçikleri kesilmiş CAD modeli kullanılıyor. |
| 5 | Türkçe metin büyük, İngilizce karşılığı küçük ve silik | Uyuyor. Ürün adı ekranda "DRON KALKANI"; "DRONE SHIELD" küçük. |
| 6 | Video yatay (16:9) | Uyuyor. |
| 7 | Gerçekçilik: ilkel ya da oyuncak görünüm istenmiyor; gerçek fotoğraf ve gerçekçi 3B | Fotoğraf ağırlıklı. Vitrin'in oyun görünümlü kareleri filme alınmadı. |
| 8 | Zemin referansı: atış alanı fotoğrafı | Fotoğraflı sahneler zaten o sahada. |
| 9 | Katmanlı savunma: tehditler bir tarafta, çözümler diğer tarafta; ilk (en iç) katman Dron Kalkanı | 07. sahne buna göre yeniden kuruldu. |

Ek olarak ürün özetine göre: sensörler pasif olduğu için "radar" sensör olarak anılmıyor; ürün tanımı "taret" yerine "robotik kule".

## Bağlantılar

| Sayfa | Adres |
|---|---|
| Ürün filmi (35 sn, oynatıcı) | https://claude.ai/artifact/Dxt1RhT3161c7jxyb3rxhN |
| Tanıtım filmi (oynatıcı, en güncel sürüm) | https://claude.ai/artifact/7kuDfLUJDfe4NBzaTbQuMY |
| Bütün videolar (galeri) | https://claude.ai/artifact/77W5miQcDH1NBn82suBKcr |
| Yapay zekâ videosu için çekim listesi | https://claude.ai/artifact/AWbqj5RswtBqgpDqD2Dw7u |

Sayfalar özeldir; yalnızca sahibi ve paylaşılan kişiler açabilir.

## Sürümler

Videolar `surumler/` klasöründe durur (sürüm kontrolüne girmez). Her biri ilgili commit'ten yeniden üretilebilir; tarifi `surumler/README.md` içinde.

| Sürüm | Tarih | Süre | Ses | Commit | Ne değişti |
|---|---|---:|---|---|---|
| v10 | 13 Kasım | 88 sn | var | `d317e20` | Sahne 04'e gerçek kule CAD modeliyle 3B yörünge çekimi eklendi: kamera kulenin çevresinde 95 derece döner. |
| v9 | 13 Kasım | 88 sn | var | `e432c93` | Ortak kurgu: önceki konuşmanın kuralları, sloganları, beş katmanlı savunma şeması, ortak yapım sahnesi ve kapanışı bu filmle birleşti. Fotoğraflardan başka firma işaretleri silindi. |
| v8 | 12 Kasım | 80 sn | var | `a9f3a74` | Katman sahnesi yeniden kuruldu: gökyüzünde dört ağ katmanı, yerde iç içe kubbeler; ardından fotoğrafta en iç kubbe ve angajman. |
| v7 | 12 Kasım | 80 sn | var | `438f4fd` | Dronlar 3B modelden render ediliyor. |
| v6 | 12 Kasım | 80 sn | var | `fbcfdcf` | Gemi güvertesi ve rafineri kulesi 3B render. Ses bandı eklendi. |
| v5 | 12 Kasım | 80 sn | yok | `1d86b82` | Hedef kutuları ve etiketler netleşti. Taret kesmeleri temizlendi. |
| v4 | 8 Kasım | 80 sn | yok | `7451936` | Fotoğraftan kesilmiş dronlar, namlu alevi, duman, enkaz, el kamerası hareketi. |
| v3 | 8 Kasım | 80 sn | yok | `d7195b0` | Taret fotoğraftan kesildi ve dronları izliyor. Araç, gemi, rafineri ve hava katmanları sahneleri. |
| v2 | 8 Kasım | 72 sn | yok | `f0035ca` | İlk fotoğraflı film. Taret sabit, dronlar çizim. |
| v1 | 8 Kasım | 64 sn | yok | kayıtsız | Fotoğrafsız, tamamı çizim ilk taslak. |
| Deneme | 12 Kasım | 5 sn | yok | `c5c0a6d` | Tamamı 3B deneme çekimi (sade taret modeliyle). |

## Ürün filmi (35 sn)

Kullanıcının 17 Kasım tarihli brifine göre yapıldı: premium fuar filmi dili, fotogerçekçi 3B, atış ve angajman yok, doğrulanmamış performans iddiası yok. Videolar `surumler/urun-filmi-35sn.mp4` (yazılı) ve `surumler/urun-filmi-35sn-yazisiz.mp4`.

| Zaman | Bölüm | İçerik |
|---|---|---|
| 0–7 sn | Ortaya çıkış | Antrasit stüdyo; kenar ışıkları sırayla açılır, kamera kulenin çevresinde döner; gövde ve sensör camı yakın planları. |
| 7–14 sn | Tasarım ve teknoloji | Sensör ünitesi ve kule gövdesi; görüntü ve ses verisini temsil eden soyut çizgiler. |
| 14–23 sn | Platform entegrasyonu | Pikap kasası (gerçek fotoğraf + 3B kule), sabit tesis platformu, deniz platformu. |
| 23–29 sn | Durumsal farkındalık | Geniş gökyüzü, uzakta temsilî dron, sade algılama simgesi ve soyut veri akışı. |
| 29–35 sn | Final | Stüdyo, üç çeyrek açı, kamera geri çekilir; solda logo ve başlık için temiz boşluk. |

Brife göre sapmalar: çözünürlük 4K değil 1080p; gerçek 3B kamera hareketi yalnızca açılışta, diğer çekimler yüksek çözünürlüklü tek kare üzerinde yavaş kamera; sensör ünitesi ve tripod temsilî.

## Kule modeli: aynalama düzeltmesi

`render/3d/modeller/taret.glb` aynalı aktarılmış: tüfeklerdeki kabartma yazı ters okunuyor ve ters monte tüfek kulenin sağında duruyordu; saha fotoğraflarında solunda. `render/3d/kule_parcala.py` modeli parçalara ayırırken (sabit taban, yatay dönen gövde, dikey dönen beşik, tüfekler, namlular, vidalar) aynalamayı da düzeltir; çıktı `modeller/kule-parcalar.npz`. Ürün filmi ve tanıtım filminin sahne 04 çekimi bu düzeltilmiş modeli kullanır. Önceki konuşmadaki 3B Vitrin hâlâ aynalı modeli kullanıyor.

## Güncel filmin sahneleri (v10)

| # | Zaman | Sahne | İçerik |
|---|---|---|---|
| 01 | 0:00–0:07 | Açılış | Pikap üzerindeki kule, DRON KALKANI, "Karıştırıcının bittiği yerde başlar." |
| 02 | 0:07–0:15 | Sorun | "Karıştırıcı her dronu durduramaz": tesise yaklaşan sürü, kule öncü dronu izlemeye başlar. |
| 03 | 0:15–0:24 | Tespit ve takip | Pasif elektro-optik ve akustik sensörler, termal görüntü, gömülü yapay zekâ; 600–800 m. |
| 04 | 0:24–0:34 | Robotik kule | Fotoğrafta yakın plan ve beş parça açıklaması; ardından gerçek CAD modeliyle 3B yörünge çekimi ve "Otonom çalışır, operatör gerekmez". |
| 05 | 0:34–0:48 | Angajman | Üç hedef; son 150 metrede atış, metal bulutu, menzil çubuğu. |
| 06 | 0:48–1:02 | Araçta · gemide · kulede | Üç platformda birer angajman. Gemi ve rafineri 3B render. |
| 07 | 1:02–1:14 | Katmanlı savunma | Gökyüzünde ağ katmanları; yerde beş kubbe, solda tehditler, sağda çözümler; en içte Dron Kalkanı. Ardından fotoğrafta en iç kubbe ve angajman. |
| 08 | 1:14–1:21 | Ortak yapım | Turaç, Derya Arms, Lasersan, Urban Savunma kartları; İTÜ ARC; Turaç'ın üretim rakamları. |
| 09 | 1:21–1:28 | Kapanış | "Son 150 metre bizim.", dört değer, Turaç ve Sterling logoları, dronkalkani.com.tr. |

Ayrıntılı senaryo, zaman kodları ve seslendirme metni: `docs/SENARYO.md`.

## Ortak kurguda hangi çalışmadan ne var

| Kaynak | Filme girenler | Henüz girmeyenler |
|---|---|---|
| Bu konuşma (v1–v8) | Fotoğraflı sahneler, dronu izleyen kule, angajman efektleri, 3B gemi ve rafineri, gökyüzü ağ katmanları, ses bandı | |
| Tanıtım Filmi (28 Ekim) | "Karıştırıcı her dronu durduramaz" sahnesi, ortak yapım kartları, kapanış sloganı, değerler ve web adresi | 3B Vitrin kareleri (pikap, kule, tüfekler, kubbeler, gemi, kule) |
| Mühendislik Filmi (31 Ekim) | Beş katmanlı savunma şeması ve metinleri, "Rakamlarla" değerleri, Turaç üretim rakamları | Teknik çizim katmanları |
| 3B Vitrin (6 Kasım) | Gerçek kule CAD modeli (sahne 04'teki 3B çekim), anlatım metinleri (araçta, gemide, kulede) | Pikap, tanker ve rafineri turu |

## Nasıl üretiliyor

1. **Film motoru** `animasyon/index.html`: zamana bağlı, tekrarlanabilir bir canvas çizimi. Tarayıcıda oynatılır.
2. **Video render** `render/render.mjs`: her kareyi tarayıcıdan alır, ffmpeg ile MP4 yapar, ses bandını ekler. Yaklaşık 15 dakika sürer.
3. **3B plakalar** `render/3d/sahneler.py`: gemi güvertesi ve rafineri kulesi, Blender ile. Kule bu sahnelerde gerçek fotoğraf kesmesidir.
   **3B kule çekimi** `render/3d/kule3b.py`: gerçek CAD modelinden 153 karelik yörünge; yaklaşık 40 dakika sürer.
4. **Dron görünümleri** `render/3d/dron3b.py`: 3B dron modelinden saydam zeminli iki görünüm.
5. **Ses** `render/ses/ses.py`: müzik yatağı ve efektler, tamamı sentez.
6. **Rötuş** `render/rotus/rotus.py`: fotoğraflardan başka firma işaretlerini ve plakayı siler.

Komutlar ve kurulum: `README.md`.

## Klasör yapısı

```
animasyon/index.html      Film motoru ve oynatıcı
animasyon/assets/         Fotoğraf plakaları, kule kesmeleri, 3B plakalar, 3B kule çekimi kareleri (kule3b/), dron görünümleri, logolar, ses
render/render.mjs         MP4 render betiği
render/3d/                Blender betikleri ve 3B modeller (modeller/dron.npz, taret.glb, kule-parcalar.npz)
urunfilmi/                Ürün filmi: kurgu sayfası ve render görüntüleri
docs/URUN-FILMI.md        Ürün filminin brifi, bölümleri, üretimi ve sapmaları
render/ses/ses.py         Ses bandı üreticisi
render/rotus/rotus.py     Fotoğraf rötuşu
docs/SENARYO.md           Senaryo, kurallar, seslendirme metni, üretim notları
docs/ai-video/            Yapay zekâ videosu için çekim listesi ve başlangıç kareleri
docs/kaynak-gorseller/    Filmde kullanılmayan referans görseller
surumler/                 Bütün sürümlerin videoları ve dizini
surumler/ilk-calismalar/  Önceki konuşmanın çalışmaları: sayfa kopyaları, videolar, film kaynakları, devir özeti
PROJE-OZETI.md            Bu belge
```

## Önceki konuşmadan gelen çalışmalar

"Dron kalkanı simülasyonu" başlıklı konuşmada yapılmış beş çalışma `surumler/ilk-calismalar/` altına alındı.

| Çalışma | Tarih | Tür | Bu projedeki hâli | Özgün sayfa |
|---|---|---|---|---|
| Dron Kalkanı Vitrin | 6 Kasım | Etkileşimli 3B sayfa, gerçek kule modeli | Sayfa kopyası ve 60 sn'lik tur videosu | https://claude.ai/artifact/WvuQjkEA245ak96Smsket2 |
| Dron Kalkanı Vitrin, ilk hâli | 2 Kasım | Etkileşimli 3B sayfa | Sayfa kopyası ve 60 sn'lik tur videosu | https://claude.ai/artifact/Gs282H3eU9yvDJu8gMMmWX |
| Dron Kalkanı Mühendislik Filmi | 31 Ekim | Film, 55 sn, sesli | Video ve kaynak: `kaynak/muhendislik-filmi/` | https://claude.ai/artifact/SqAWM8pSunY6wrp41DJapu |
| Dron Kalkanı Tanıtım Filmi | 28 Ekim | Film, 59 sn, sesli | Video ve kaynak: `kaynak/tanitim-filmi/` | https://claude.ai/artifact/4D2J8fx2N9SFVRJHmrajzU |
| Dron Kalkanı Simülasyonu | 28 Ekim | Etkileşimli 3B simülasyon | Sayfa kopyası, 45 sn'lik yatay ve 30 sn'lik dikey kayıt | https://claude.ai/artifact/7V4VHVvJBVT8fmECVycWLt |

Kaynak klasörlerinde sahne betikleri ile görseller durur: 3B kareler (hero, turret, guns, domes, ship, tower), kırpılmış saha fotoğrafları (ph-*) ve teknik çizim katmanları (ln-*). O konuşmanın devir özeti: `surumler/ilk-calismalar/PROJE-OZETI-simulasyon-sohbeti.md`.

## Kullanıcının bilgisayarındaki klasör

`C:\Users\user\Documents\Dron Kalkani Animasyon`. Bulut oturumu bu klasöre erişemiyor. Yayınlanmış sayfalar üzerinden zaten alınanlar: `vitrin.html` (yayınlanan hâli), `model/kule.json`, filmlerde kullanılan `renders/` görselleri.

Yalnızca bilgisayarda duran ve işe yarayacak dosyalar:

| Dosya | Neden gerekli |
|---|---|
| `video/dron-kalkani-vitrin.mp4` | Vitrin turunun özgün, müzikli kaydı. Buradaki kayıt sessiz ve yeniden çekim. |
| `vitrin.html`, `vitrin-cap.html` | En güncel vitrin ve kare alma sürümü: istenen andan temiz kare ve video almak için. |
| `studio-cap.html` | Teknik çizim katmanlarını gerçek CAD modelinden yeniden üretmek için. |
| `dron-kalkani.html`, `dron-kalkani-3d.html` | İlk denemeler. Aranan dikey video bunlardan biri olabilir. |

`model/kule.step` (83 MB) gerekmiyor: aynı model `render/3d/modeller/taret.glb` olarak burada.

## Açık konular

1. **Sıradaki adım kararı.** 3B kule çekimi başka sahnelere de taşınsın mı (açılış, kapanış); Vitrin görüntüleri ve teknik çizimler ortak kurguya eklensin mi.
2. **Bilgisayardaki dosyalar.** Yukarıdaki tablo. Sohbete yüklenirse projeye eklenir.
3. **Dikey video.** Hangisi olduğu hâlâ belli değil. Önceki iki film yatay. Simülasyon sayfasının telefon görünümü dikey olarak kaydedildi.
4. **GitHub.** Bağlantı kuruldu; commit'ler `claude/dron-kalkani-animation-film-vpq9ox` dalına gönderiliyor. Pull request açılmadı.
5. **Ses.** Ses bandı ölçümle doğrulandı, kulakla dinlenmedi. Seslendirme kaydı yok; metni senaryoda.
6. **Yapay zekâ videosu başlangıç kareleri.** `docs/ai-video/kareler/` eski, rötuşsuz fotoğraflardan üretilmişti; içlerinde araç amblemi ve plaka görünüyor. Yeniden üretilmeli.
7. **"MAX" yazısı.** CAD modelindeki şarjörlerde ve gövdede kabartma "MAX" var (modelde aynalı duruyor); 3B çekimde seçilebiliyor. Aynı yazı gerçek fotoğrafta da görünüyor.
8. **Temsilî parçalar.** 3B çekimdeki sensör kutusu, kaide ve tripod CAD montajında yok; saha fotoğraflarına bakılarak yaklaşık ölçüyle modellendi. Gerçek parçaların modeli gelirse değiştirilmeli.
9. **Logolar.** Afişten ayıklandı; yayın için vektör logolarla değiştirilmeli. Ürün logosunun kendisi İngilizce "DRONE SHIELD" yazıyor; Türkçe bir logo varsa onunla değiştirilmeli.
10. **Lisans.** Dron modeli büyük olasılıkla bir paylaşım sitesinden indirilmiş ve ticari bir dronu andırıyor.

## Bilinen sınırlar

- Tanıtım filminin fotoğraflı sahnelerinde kule iki boyutlu kesmedir; yalnızca yukarı aşağı döner. CAD modeli artık yatay ve dikey dönen parçalara ayrıldı; 3B çekimlerde kule döndürülebilir.
- Gemi ve rafineri ortamları bilgisayar üretimidir, gerçek çekim değildir.
- Rötuş yakından bakıldığında fark edilebilir: silinen yerlerde kamuflaj deseni düzleşti, plaka boş beyaz.
- Bu ortamda ekran kartı yok. Tamamı 3B, 1080p bir film için kare başına 2–3 dakika gerekir.

## Başka bir konuşmada devam etmek için

1. Depo GitHub'da: `Turacyapayzeka/Turac-Cigdem`, dal `claude/dron-kalkani-animation-film-vpq9ox`. Yeni konuşmayı bu depo ve dal ile başlatın.
2. Bu belgeyi o konuşmaya ekleyin.
3. Yukarıdaki üç sayfa bağlantısını verin; sayfalar oradan okunabilir.
