# Film sürümleri

Bu klasör filmin bütün sürümlerinin videolarını bir arada tutar. Videolar büyük olduğu için sürüm kontrolüne girmez;
her biri aşağıdaki commit'ten yeniden üretilebilir:

```
git archive <commit> | tar -x -C /tmp/surum && node /tmp/surum/render/render.mjs --out surumler/<dosya>.mp4
```

| Sürüm | Tarih | Dosya | Süre | Ses | Commit | Ne değişti |
|---|---|---|---:|---|---|---|
| v7 | 12 Kasım | `v7-3b-dron-sesli.mp4` | 80 sn | var | `438f4fd` | Dronlar 3B modelden render ediliyor. **En güncel sürüm.** |
| v6 | 12 Kasım | `v6-3b-gemi-rafineri-sesli.mp4` | 80 sn | var | `fbcfdcf` | Gemi güvertesi ve rafineri kulesi 3B render. Ses bandı eklendi. |
| v5 | 12 Kasım | `v5-net-isaretler.mp4` | 80 sn | yok | `1d86b82` | Hedef kutuları ve etiketler netleşti. Taret kesmeleri temizlendi, katman lejantı eklendi. |
| v4 | 8 Kasım | `v4-gercekci-dronlar-ve-efektler.mp4` | 80 sn | yok | `7451936` | Fotoğraftan kesilmiş dronlar, sinematik namlu alevi, duman, enkaz, el kamerası hareketi. |
| v3 | 8 Kasım | `v3-takip-eden-taret.mp4` | 80 sn | yok | `d7195b0` | Taret fotoğraftan kesildi ve dronları izliyor. Araç, gemi, rafineri sahneleri ve hava katmanları eklendi. |
| v2 | 8 Kasım | `v2-ilk-surum-fotograf-plakalari.mp4` | 72 sn | yok | `f0035ca` | İlk film: gerçek fotoğraflar üzerine HUD ve yazılar. Taret sabit, dronlar çizim. |
| Deneme | 12 Kasım | `deneme-tamami-3b.mp4` | 5 sn | yok | `c5c0a6d` | Tamamı 3B deneme çekimi: fotoğraflardan kurulmuş sade taret modeli, dönen kamera. |

v1 yalnızca çizimden oluşan ilk taslaktı; fotoğraflar gelince v2 ile değiştirildi ve kaydedilmedi.
