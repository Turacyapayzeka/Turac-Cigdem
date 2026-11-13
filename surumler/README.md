# Film sürümleri

Bu klasör filmin bütün sürümlerinin videolarını bir arada tutar. Videolar büyük olduğu için sürüm kontrolüne girmez;
her biri aşağıdaki commit'ten yeniden üretilebilir:

```
git archive <commit> | tar -x -C /tmp/surum && node /tmp/surum/render/render.mjs --out surumler/<dosya>.mp4
```

| Sürüm | Tarih | Dosya | Süre | Ses | Commit | Ne değişti |
|---|---|---|---:|---|---|---|
| v9 | 13 Kasım | `v9-ortak-kurgu-sesli.mp4` | 88 sn | var | `e432c93` | Ortak kurgu: önceki konuşmanın kuralları, sloganları, beş katmanlı savunma şeması, ortak yapım sahnesi ve kapanışı bu filmle birleşti. Fotoğraflardan başka firma işaretleri ve plaka silindi. **En güncel sürüm.** |
| v8 | 12 Kasım | `v8-sade-katman-sahnesi-sesli.mp4` | 80 sn | var | `a9f3a74` | Katman sahnesi yeniden kuruldu: gökyüzünde dört ağ katmanı, yerde iç içe kubbeler; ardından fotoğrafta en iç kubbe ve angajman. |
| v7 | 12 Kasım | `v7-3b-dron-sesli.mp4` | 80 sn | var | `438f4fd` | Dronlar 3B modelden render ediliyor. |
| v6 | 12 Kasım | `v6-3b-gemi-rafineri-sesli.mp4` | 80 sn | var | `fbcfdcf` | Gemi güvertesi ve rafineri kulesi 3B render. Ses bandı eklendi. |
| v5 | 12 Kasım | `v5-net-isaretler.mp4` | 80 sn | yok | `1d86b82` | Hedef kutuları ve etiketler netleşti. Taret kesmeleri temizlendi, katman lejantı eklendi. |
| v4 | 8 Kasım | `v4-gercekci-dronlar-ve-efektler.mp4` | 80 sn | yok | `7451936` | Fotoğraftan kesilmiş dronlar, sinematik namlu alevi, duman, enkaz, el kamerası hareketi. |
| v3 | 8 Kasım | `v3-takip-eden-taret.mp4` | 80 sn | yok | `d7195b0` | Taret fotoğraftan kesildi ve dronları izliyor. Araç, gemi, rafineri sahneleri ve hava katmanları eklendi. |
| v2 | 8 Kasım | `v2-ilk-surum-fotograf-plakalari.mp4` | 72 sn | yok | `f0035ca` | İlk film: gerçek fotoğraflar üzerine HUD ve yazılar. Taret sabit, dronlar çizim. |
| v1 | 8 Kasım | `v1-yalnizca-cizim.mp4` | 64 sn | yok | kayıtsız | Fotoğraf kullanılmadan, tamamı çizimle yapılmış ilk taslak. Kaynağı oturum kaydından kurtarıldı. |
| Deneme | 12 Kasım | `deneme-tamami-3b.mp4` | 5 sn | yok | `c5c0a6d` | Tamamı 3B deneme çekimi: fotoğraflardan kurulmuş sade taret modeli, dönen kamera. |

## Bu yazışmadan önceki çalışmalar

`ilk-calismalar/` klasöründe, "Dron kalkanı simülasyonu" başlıklı önceki konuşmada yapılmış çalışmalar durur: üç etkileşimli sayfanın kopyası ve iki filmin video dosyası. Filmler, film sayfasının kendi çizicisinden kare kare alınarak üretildi; sayfadaki Dışa Aktar düğmesinin çıktısı değildir. Videolar sürüm kontrolüne girmez.

| Çalışma | Tarih | Tür | Yerel kopya | Bağlantı |
|---|---|---|---|---|
| Dron Kalkanı Vitrin | 6 Kasım | Etkileşimli 3B sayfa, gerçek taret modeli, 60 sn tur | `ilk-calismalar/2026-11-06-vitrin-3b.html` (+ `model/kule.json`), video: `2026-11-06-vitrin-3b.mp4` | https://claude.ai/artifact/WvuQjkEA245ak96Smsket2 |
| Dron Kalkanı Vitrin | 2 Kasım | Etkileşimli 3B sayfa, sade taret | `ilk-calismalar/2026-11-02-vitrin.html`, video: `2026-11-02-vitrin.mp4` | https://claude.ai/artifact/Gs282H3eU9yvDJu8gMMmWX |
| Dron Kalkanı Mühendislik Filmi | 31 Ekim | Film, 9 sahne, 55 sn, sesli | `ilk-calismalar/2026-10-31-muhendislik-filmi.mp4` | https://claude.ai/artifact/SqAWM8pSunY6wrp41DJapu |
| Dron Kalkanı Tanıtım Filmi | 28 Ekim | Film, 11 sahne, 59 sn, sesli | `ilk-calismalar/2026-10-28-tanitim-filmi.mp4` | https://claude.ai/artifact/4D2J8fx2N9SFVRJHmrajzU |
| Dron Kalkanı Simülasyonu | 28 Ekim | Etkileşimli 3B simülasyon | `ilk-calismalar/2026-10-28-simulasyon.html`, video: `2026-10-28-simulasyon.mp4` ve dikey `2026-10-28-simulasyon-dikey.mp4` | https://claude.ai/artifact/7V4VHVvJBVT8fmECVycWLt |

Yerel kopyalar three.js kitaplığını internetten yükler. `model/kule.json` taretin 3B modelidir (12 MB) ve sürüm kontrolüne girmez; aynı model `render/3d/modeller/taret.glb` olarak depoda durur.

`ilk-calismalar/kaynak/` altında iki filmin kaynakları durur: sahne betikleri ile görseller (3B kareler, kırpılmış saha fotoğrafları, teknik çizim katmanları). `ilk-calismalar/PROJE-OZETI-simulasyon-sohbeti.md`, o konuşmanın devir özetidir: ürün bilgileri ve v9'un uyduğu kurallar oradan alındı.
