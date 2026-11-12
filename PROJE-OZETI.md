# Drone Shield · Dron Kalkanı — Proje Özeti

Son güncelleme: 12 Kasım 2026. Bu belge projeyi başka bir konuşmaya ya da ekibe taşımak için tek başına okunabilir biçimde yazıldı.

## Tek bakışta

- **Ne:** Turaç / Sterling **Drone Shield (Dron Kalkanı)** anti-dron taret sistemi için tanıtım filmi.
- **Güncel sürüm:** v8. 80 saniye, 1920×1080, 30 fps, sesli, Türkçe ekran yazıları.
- **Yöntem:** Gerçek saha fotoğrafları üzerine tarayıcıda çizilen animasyon katmanları. Gemi ve rafineri sahneleri 3B render. Dronlar 3B modelden. Ses sentez.
- **Bekleyen karar:** Hangi sürümden devam edileceği. Sürümlerin hepsi tek sayfada izlenebiliyor.

## Bağlantılar

| Sayfa | Adres |
|---|---|
| Film (oynatıcı, en güncel sürüm) | https://claude.ai/artifact/7kuDfLUJDfe4NBzaTbQuMY |
| Bütün sürümler (galeri) | https://claude.ai/artifact/77W5miQcDH1NBn82suBKcr |
| Yapay zekâ videosu için çekim listesi | https://claude.ai/artifact/AWbqj5RswtBqgpDqD2Dw7u |

Sayfalar özeldir; yalnızca sahibi ve paylaşılan kişiler açabilir.

## Sürümler

Videolar `surumler/` klasöründe durur (sürüm kontrolüne girmez). Her biri ilgili commit'ten yeniden üretilebilir; tarifi `surumler/README.md` içinde.

| Sürüm | Tarih | Süre | Ses | Commit | Ne değişti |
|---|---|---:|---|---|---|
| v8 | 12 Kasım | 80 sn | var | `a9f3a74` | Katman sahnesi yeniden kuruldu: gökyüzünde dört ağ katmanı, yerde iç içe kubbeler; ardından fotoğrafta en iç kubbe ve angajman. |
| v7 | 12 Kasım | 80 sn | var | `438f4fd` | Dronlar 3B modelden render ediliyor. |
| v6 | 12 Kasım | 80 sn | var | `fbcfdcf` | Gemi güvertesi ve rafineri kulesi 3B render. Ses bandı eklendi. |
| v5 | 12 Kasım | 80 sn | yok | `1d86b82` | Hedef kutuları ve etiketler netleşti. Taret kesmeleri temizlendi. |
| v4 | 8 Kasım | 80 sn | yok | `7451936` | Fotoğraftan kesilmiş dronlar, namlu alevi, duman, enkaz, el kamerası hareketi. |
| v3 | 8 Kasım | 80 sn | yok | `d7195b0` | Taret fotoğraftan kesildi ve dronları izliyor. Araç, gemi, rafineri ve hava katmanları sahneleri. |
| v2 | 8 Kasım | 72 sn | yok | `f0035ca` | İlk fotoğraflı film. Taret sabit, dronlar çizim. |
| v1 | 8 Kasım | 64 sn | yok | kayıtsız | Fotoğrafsız, tamamı çizim ilk taslak. |
| Deneme | 12 Kasım | 5 sn | yok | `c5c0a6d` | Tamamı 3B deneme çekimi (sade taret modeliyle). |

## Güncel filmin sahneleri (v8)

| # | Zaman | Sahne | İçerik |
|---|---|---|---|
| 01 | 0:00–0:07 | Açılış | Amarok üzerindeki taret, Drone Shield logosu, slogan. |
| 02 | 0:07–0:15 | Tehdit | Tesise yaklaşan dron sürüsü; taret öncü dronu izlemeye başlar. |
| 03 | 0:15–0:24 | Tespit ve takip | Sensör başlığı, radar, termal görüntü, sensör füzyonu. |
| 04 | 0:24–0:34 | Robotik taret | Taret yakın planı ve parça açıklamaları. |
| 05 | 0:34–0:48 | Angajman | Üç hedef; 150 m'de atış, metal bulutu, menzil çubuğu. |
| 06 | 0:48–1:02 | Araç · gemi · rafineri | Üç platformda birer angajman. Gemi ve rafineri 3B render. |
| 07 | 1:02–1:12 | Katmanlı hava savunma | Gökyüzünde ağ katmanları ve iç içe kubbeler; en içte Drone Shield. |
| 08 | 1:12–1:20 | Kapanış | Logo, dört rakam, Turaç ve Sterling logoları, web adresi. |

Ayrıntılı senaryo, zaman kodları ve seslendirme metni: `docs/SENARYO.md`.

## Nasıl üretiliyor

1. **Film motoru** `animasyon/index.html`: zamana bağlı, tekrarlanabilir bir canvas çizimi. Tarayıcıda oynatılır.
2. **Video render** `render/render.mjs`: her kareyi tarayıcıdan alır, ffmpeg ile MP4 yapar, ses bandını ekler. Yaklaşık 13 dakika sürer.
3. **3B plakalar** `render/3d/sahneler.py`: gemi güvertesi ve rafineri kulesi, Blender ile. Taret bu sahnelerde gerçek fotoğraf kesmesidir.
4. **Dron görünümleri** `render/3d/dron3b.py`: 3B dron modelinden saydam zeminli iki görünüm.
5. **Ses** `render/ses/ses.py`: müzik yatağı ve efektler, tamamı sentez.

Komutlar ve kurulum: `README.md`.

## Klasör yapısı

```
animasyon/index.html      Film motoru ve oynatıcı
animasyon/assets/         Fotoğraf plakaları, taret kesmeleri, 3B plakalar, dron görünümleri, logolar, ses
render/render.mjs         MP4 render betiği
render/3d/                Blender betikleri ve 3B modeller (modeller/dron.npz, modeller/taret.glb)
render/ses/ses.py         Ses bandı üreticisi
docs/SENARYO.md           Senaryo, seslendirme metni, üretim notları, storyboard
docs/ai-video/            Yapay zekâ videosu için çekim listesi ve başlangıç kareleri
docs/kaynak-gorseller/    Filmde kullanılmayan referans görseller
surumler/                 Bütün sürümlerin videoları ve dizini; ilk-calismalar/ altında önceki çalışmalar
PROJE-OZETI.md            Bu belge
```

## Kaynak malzeme

- **Fotoğraflar:** Kullanıcının gönderdiği saha fotoğrafları: Amarok yan ve arka görünüş, taret yakın planı, sensör başlığı.
- **Taret 3B modeli:** `render/3d/modeller/taret.glb`. Kullanıcının 6 Kasım tarihli "Dron Kalkanı Vitrin" sayfasından alındı; gövde ve tüfek ayrı ağlar, toplam 233 bin köşe. Henüz filmde kullanılmıyor.
- **Dron 3B modeli:** `render/3d/modeller/dron.npz`. Kullanıcının 3B baskı projesinden geldi.
- **Logolar:** Drone Shield, Turaç ve Sterling logoları etkinlik afişinden ayıklandı.
- **Steeldome görseli:** Katman sahnesinin düzenine esin verdi; görselin kendisi filmde yok.

## Önceki konuşmadan gelen çalışmalar

"Dron kalkanı simülasyonu" başlıklı konuşmada yapılmış beş çalışma bulundu ve `surumler/ilk-calismalar/` altına alındı.

| Çalışma | Tarih | Tür | Bu projedeki hâli | Özgün sayfa |
|---|---|---|---|---|
| Dron Kalkanı Vitrin | 6 Kasım | Etkileşimli 3B sayfa, gerçek taret modeli | Sayfa kopyası; video kaydı bu belge yazılırken sürüyordu | https://claude.ai/artifact/WvuQjkEA245ak96Smsket2 |
| Dron Kalkanı Vitrin, ilk hâli | 2 Kasım | Etkileşimli 3B sayfa | Sayfa kopyası; video kaydı sürüyordu | https://claude.ai/artifact/Gs282H3eU9yvDJu8gMMmWX |
| Dron Kalkanı Mühendislik Filmi | 31 Ekim | Film, 55 sn, sesli | Video dosyası hazır | https://claude.ai/artifact/SqAWM8pSunY6wrp41DJapu |
| Dron Kalkanı Tanıtım Filmi | 28 Ekim | Film, 59 sn, sesli | Video dosyası hazır | https://claude.ai/artifact/4D2J8fx2N9SFVRJHmrajzU |
| Dron Kalkanı Simülasyonu | 28 Ekim | Etkileşimli 3B simülasyon | Sayfa kopyası; video kaydı sürüyordu | https://claude.ai/artifact/7V4VHVvJBVT8fmECVycWLt |

İki konuşma tek konuşmada birleştirilemiyor. Bu yüzden o konuşmanın yayınlanmış sayfaları buraya kopyalandı.

## Filmdeki rakamlar ve doğrulanması gerekenler

Aşağıdaki değerler basına yansıyan şirket açıklamalarından alındı. Yayın öncesi Turaç tarafından doğrulanmalı.

| Değer | Filmde nerede |
|---|---|
| Tespit ve takip 600–800 m | Sahne 03, 05, 08 |
| Angajman mesafesi 150 m | Sahne 05, 07, 08 |
| Yaklaşık 140 m'de yaklaşık 2 m çapında metal bulutu | Sahne 05, 08 |
| 360° koruma | Sahne 08 |
| "Yerli ve milli üretim · 1987'den beri" | Sahne 08 |

Kaynak haberler: [Uzmanpara, sahaya çıkış](https://uzmanpara.milliyet.com.tr/uzmanpara/yurt-disindan-buyuk-ilgi-drone-kalkani-ilk-kez-sahaya-cikti-7681723), [Foreks / AA](https://www.foreks.com/haber/detay/6ab0f8e295016b5817e5d82d/AA/tr/turk-savunma-sanayisindeki-yetenekler-drone-kalkanina-donustu-21-09-26/), [İstiklal](https://www.istiklal.com.tr/teknoloji/turk-savunmasinin-yeni-kozu-drone-kalkani-suru-saldirilarina-karsi-hazir-1105961h), [Militarnyi](https://militarnyi.com/en/news/turkey-dron-kalkan-turret-12-gauge-shotguns/).

## Açık konular

1. **Sürüm seçimi.** Kullanıcı sürümlerden birini seçip ondan devam edecek.
2. **Dikey video.** Kullanıcının hatırladığı dikey video bu projede yok. Önceki iki film yatay çıktı. Video başka bir konuşmada dosya olarak duruyorsa oradan indirilip buraya eklenmeli.
3. **GitHub.** Push reddediliyor (403): depo, oturumun GitHub kimliğine bağlı değil. Commit'ler yerelde ve `drone-shield-commits.bundle` dosyasında. Çözüm: GitHub bağlantısını yenileyip yeni oturum açmak ya da bundle ile elle push etmek.
4. **Ses.** Ses bandı ölçümle doğrulandı, kulakla dinlenmedi. Seslendirme kaydı yok; metni senaryoda.
5. **Yapay zekâ videosu.** Higgsfield hesabı açılmadı. Canva ile video üretimi mümkün ama kullanıcı onayı bekliyor. Çekim paketi hazır.
6. **Taret 3B modeli.** Filmde kullanılması için ağın yatay ve dikey dönen parçalara ayrılması gerekiyor.
7. **Logolar.** Afişten ayıklandı; yayın için vektör logolarla değiştirilmeli.
8. **Lisans ve marka.** Dron modeli büyük olasılıkla bir paylaşım sitesinden indirilmiş ve ticari bir dronu andırıyor. Steeldome görselinin kendisi kullanılmadı. Fotoğraflarda araç plakası okunuyor.

## Bilinen sınırlar

- Fotoğraflı sahnelerde taret iki boyutlu kesmedir; yalnızca yukarı aşağı döner.
- Gemi ve rafineri ortamları bilgisayar üretimidir, gerçek çekim değildir.
- Bu ortamda ekran kartı yok. Tamamı 3B, 1080p bir film için kare başına 2–3 dakika gerekir.

## Sıradaki olası adımlar

- Seçilen sürümü cilalamak: seslendirme, vektör logolar, rakamların doğrulanması.
- Taret 3B modelini parçalara ayırıp tamamı 3B çekimler eklemek: örneğin 360 derece tanıtım dönüşü.
- Önceki Tanıtım Filmi ya da Mühendislik Filmi ile bu filmi tek kurguda birleştirmek.
- Dikey (9:16) bir sosyal medya kurgusu çıkarmak.

## Başka bir konuşmada devam etmek için

1. Bu belgeyi ve `drone-shield-commits.bundle` dosyasını o konuşmaya ekleyin.
2. Yukarıdaki üç sayfa bağlantısını verin; sayfalar oradan okunabilir.
3. Depo GitHub'a gönderildiyse dal adı: `claude/dron-kalkani-animation-film-vpq9ox`.
