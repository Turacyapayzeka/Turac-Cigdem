# Drone Shield — Yapay zekâ videosu için çekim listesi

Bu paket, filmi **üretken video** (Higgsfield, Seedance, Kling, Veo vb.) ile gerçekçi hareketli görüntüye taşımak için hazırlandı.
Fikir şu: yapay zekâ modeli **gerçek görüntüyü ve hareketi** üretir; mevcut film motoru (`animasyon/index.html`) HUD'u, hedef kutularını, katman lejantını, başlıkları ve logoları **sonradan üzerine bindirir** ve kurguyu toplar. Böylece ürün gerçek fotoğraftan gelir, yazılar ise net ve doğru kalır (üretken modeller yazıyı bozar).

## Paketin içeriği

| Dosya | Ne işe yarar |
|---|---|
| `kareler/C01…C07-*.jpg` | **Başlangıç kareleri** (1920×1080). Filmin HUD'suz, yazısız, renk düzeni uygulanmamış kareleri: gerçek fotoğraf + nişan almış taret + dronlar. "Image-to-video" için ilk kare olarak verilir. |
| `kareler/R1…R4-*.jpg` | **Ürün referans fotoğrafları** (kırpılmamış). Modelin taretin gerçek tasarımını korumasını sağlar. |
| Bu dosya | Her çekim için süre, kamera, İngilizce komut (prompt) ve sonradan bindirilecek katmanlar. |

Yeni kare üretmek için: `node render/render.mjs --clean 1 --stills 13.5,38.2 --stillsdir docs/ai-video/kareler`

## Tüm çekimler için ortak kurallar

- **Mod:** image-to-video, ilk kare = belirtilen `C…` dosyası. 16:9, mümkünse 1080p, 5–8 sn.
- **Her çekimden 2–3 varyasyon** üretin; taretin şekli en az bozulanı seçin.
- **Ses:** modelin kendi ortam sesi (rüzgâr, pervane, atış) açık olabilir; müzik istemeyin, kurguda eklenir.
- Her komutun sonuna şu **ortak eki** ekleyin:

```
Photorealistic live-action footage, natural colours, soft overcast daylight, 16:9.
Keep the turret exactly as in the first frame: black semi-automatic shotgun with muzzle brake,
beige pan-tilt mount, beige electro-optical sensor box on top, black box magazine.
Do not add people, text, subtitles, logos, extra weapons or extra vehicles. No slow motion.
```

## Çekimler

| Kod | Filmdeki yeri | İlk kare | Süre | Sonradan bindirilecek |
|---|---|---|---:|---|
| K01 | 0:00–0:07 Açılış | `C01-acilis-arac.jpg` | 6 sn | Logo, DRON KALKANI başlığı, slogan |
| K02 | 0:07–0:15 Tehdit | `C02-tehdit-suru.jpg` | 7 sn | Kırmızı hedef kutusu, "OTOMATİK TAKİP" çizgisi, başlık |
| K03 | 0:15–0:24 Tespit | `C03-sensor-basligi.jpg` | 6 sn | Radar, termal pencere, füzyon şeridi |
| K04 | 0:24–0:34 Robotik taret | `R1` üzerinden üretilecek 16:9 kare | 6 sn | Parça açıklamaları |
| K05 | 0:34–0:48 Angajman | `C05-angajman.jpg` | 6–8 sn | Menzil çubuğu, hedef kutuları, sayaç |
| K06a | 0:48–0:53 Araç üstü | `C06a-arac-ustu.jpg` | 5 sn | Vinyet başlığı |
| K06b | 0:53–0:57 Gemi | `C06b-gemi.jpg` (3B render + gerçek taret) | 6 sn | Vinyet başlığı |
| K06c | 0:57–1:02 Rafineri | `C06c-rafineri.jpg` (3B render + gerçek taret) | 6 sn | Vinyet başlığı |
| K07 | 1:02–1:12 Hava katmanları | `C07-son-katman.jpg` | 7 sn | Dört katman kubbesi, lejant, tehdit ikonları |
| K08 | 1:12–1:20 Kapanış | yok (grafik) | — | Tamamı mevcut film motorundan |

### K01 · Açılış
```
Slow cinematic push-in toward a robotic counter-drone turret mounted on a tripod in the bed of a
camouflage-wrapped pickup truck parked on a gravel track. Dry grass on the hillside moves in a light
wind, thin dust drifts across the ground, clouds move slowly. The turret is completely still.
35 mm lens, shallow depth of field, stabilised handheld feel.
```

### K02 · Tehdit: sürü yaklaşıyor
```
A swarm of six small quadcopter drones flies in from the upper left across the overcast sky toward the
industrial buildings on the hill, growing larger as they approach. In the right foreground the robotic
turret on the pickup truck smoothly tilts up and pans left to follow the lead drone. The turret does
not fire. Locked-off camera with a slight handheld sway.
```

### K03 · Tespit: sensör başlığı tarıyor
```
The beige multi-sensor head on the tripod slowly pans from left to right, scanning the sky; the lenses
catch faint reflections and the black cables sway slightly. Slow push-in toward the sensor head.
Wind in the dry grass behind it.
```

### K04 · Robotik taret yakın planı
Önce görüntü modeliyle `R1-taret-yakin-plan.jpg` referansından 16:9 bir kare üretin, sonra o kareyi hareketlendirin.

Kare komutu:
```
Low-angle close-up product photograph of the same robotic turret as in the reference image: black
semi-automatic 12-gauge shotgun with muzzle brake on a beige pan-tilt mount, beige electro-optical
sensor box on top, black box magazine, camouflage netting below. Overcast sky background, 85 mm lens,
16:9, photorealistic. Same design, same colours, no changes to the product.
```
Hareket komutu:
```
The turret pans slowly from left to right and tilts up a few degrees with precise, servo-driven,
mechanical motion. The camera orbits about 15 degrees around the turret. Camouflage netting moves
slightly in the wind.
```

### K05 · Angajman
```
The turret tracks an incoming small quadcopter drone and fires a single shot: a brief muzzle flash,
a puff of grey smoke from the barrel and a short recoil. About 150 metres away the drone is hit by a
cloud of shot pellets, breaks apart with a small spark and falls, trailing thin smoke. A second drone
stays far away in the background. Locked-off camera with a short shake at the moment of the shot.
```

### K06a · Araç üstü
```
The turret on the tripod in the truck bed swivels and tilts upward, following a small quadcopter drone
that crosses the sky from left to right. Slow dolly-in toward the rear of the truck. Wind in the grass.
```

### K06b · Gemi güvertesi
```
Dusk at sea. On the aft deck of a grey naval patrol vessel, the same robotic turret as in the reference
image is bolted to a steel pedestal beside the deck railing. It pans and tilts, tracking a small
quadcopter drone flying low over the water toward the ship. Orange sunset glow on the horizon, dark
blue swell, light sea spray, a slight roll of the deck. Wide shot from chest height on deck, slow
push-in. Photorealistic, no crew visible.
```
(Ortak ekteki "overcast daylight" yerine bu çekimde "dusk light" bırakın.)

### K06c · Rafineri kulesi
```
Blue hour at an oil refinery. The same robotic turret as in the reference image is mounted on the
railed steel platform of a lattice tower overlooking distillation columns, storage tanks and pipe
racks lit by warm sodium lamps; a flare stack burns in the distance. The turret pans and elevates,
tracking a small quadcopter drone approaching over the tanks. Low-angle shot from below the platform,
slow crane up. Light industrial haze. Photorealistic, no workers visible.
```
(Bu çekimde de "overcast daylight" yerine "blue-hour light" kullanın.)

### K07 · En iç katman
```
Wide side view of the camouflage-wrapped pickup truck with the turret on its tripod. Two small
quadcopter drones dive in from the upper left. The turret tracks the first one and fires once (muzzle
flash, grey smoke); the first drone bursts and falls. The turret immediately swings toward the second
drone. Locked-off camera with a subtle shake on the shot.
```

## Üretimden sonra

1. Seçilen klipleri `animasyon/klipler/K01.mp4 … K07.mp4` adlarıyla kaydedin (klasör henüz yok; klipler gelince açılacak).
2. Film motoruna klip oynatma desteği eklenecek: her sahnenin fotoğraf plakası yerine ilgili klip oynatılır, HUD ve başlıklar üstte kalır. **Bu destek henüz yazılmadı;** klipler gelmeden yazmak, hangi sahnede takip noktalarının nasıl eşleneceğini tahmin etmek olurdu.
3. Kurgu ve son render yine `render/render.mjs` ile yapılır.

## Bilinmesi gereken riskler

- **İçerik denetimi.** Üretken video platformları silah ve atış içeren komutları reddedebilir veya yumuşatabilir. K05 ve K07 bu açıdan en riskli çekimler; reddedilirse atış anı mevcut film motorundaki namlu alevi ve vuruş efektleriyle bindirilebilir, model yalnızca takibi üretir.
- **Ürün sadakati.** Model taretin ayrıntılarını (namlu ağzı, sensör kutusu, şarjör) değiştirebilir. Bu yüzden ilk kare ve "keep exactly as in the first frame" eki her çekimde kullanılıyor; yine de her klip gerçek fotoğrafla karşılaştırılmalı.
- **Rakamlar ve yazı.** Menzil, mühimmat ve marka yazıları hiçbir zaman modele bırakılmıyor; hepsi film motorundan geliyor.
