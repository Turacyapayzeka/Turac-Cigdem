# Dron Kalkanı Ürün Filmi (35 sn)

Fuar ekranı için kısa, sinematik ürün filmi. Tanıtım filminden (`animasyon/`) ayrı bir çalışmadır: atış, hedefleme ya da angajman göstermez; ürünü ve kullanıldığı platformları tanıtır. **Film yalnızca 3B animasyondan oluşur; gerçek fotoğraf ya da çekim içermez.**

**Süre:** 35 saniye · **Format:** 1920×1080, 24 fps, sesli · **Sayfa:** `urunfilmi/index.html`

## Brif

Kullanıcının 17 Kasım 2026 tarihli brifinin özeti:

- Görsel dil: premium bir savunma teknolojisi fuar filmi; sade, güçlü, teknik, gerçekçi.
- Ürün: gerçek fotoğraflar ana referans. Silüet, ortadaki elektro-optik sensör ünitesi, iki yandaki ekipman, taşıyıcı gövde, renkler ve montaj biçimi korunur. Yeni parça eklenmez. Ürün bütün sahnelerde aynı geometridedir.
- Kaçınılacaklar: enerji kalkanı, lazer, radar dalgası, bilim kurgu hologramı, patlama, savaş sahnesi, bozuk geometri, değişen parça sayısı, fazladan namlu, deforme logo, okunaksız yazı, doğrulanmamış performans iddiası.
- Atış, hedefleme çözümü, mühimmat etkisi ve imha gösterilmez. İç mekanizma, montaj şeması ve teknik parametre gösterilmez.
- Kurguda dört kısa yazı: "DRON KALKANI", "Robotik kule teknolojisi", "Kara • Deniz • Sabit tesis", "Yakın mesafe dron savunması".

## Bölümler

| Zaman | Bölüm | Çekimler | Yazı |
|---|---|---|---|
| 0–7 sn | Ortaya çıkış | Antrasit stüdyo. Kenar ışıkları sırayla açılır, kamera kulenin çevresinde 34 derece döner, kule yavaşça döner ve yükselir (80 kare, gerçek 3B hareket). Ardından iki yakın plan: gövde, göbek ve bağlantı detayları; sensör camındaki yansımalar. | DRON KALKANI |
| 7–14 sn | Tasarım ve teknoloji | Sensör ünitesi üç çeyrek; kule gövdesi arkadan çapraz. Üzerlerinde soyut grafik katmanı: görüntü verisini temsil eden kare ızgara, ses verisini temsil eden dalga çizgisi, akan kesik çizgiler. | Robotik kule teknolojisi |
| 14–23 sn | Platform entegrasyonu | Pikap kasasında (3B araç, açık arazi), sabit tesis platformunda, deniz platformunda. Her birinde yavaş yaklaşma ya da uzaklaşma. | Kara • Deniz • Sabit tesis |
| 23–29 sn | Durumsal farkındalık | Araç sahnesinin alçak ve geniş açısı: kadrajın çoğu gökyüzü; uzakta küçük, temsilî bir dron süzülür. Ayrı grafik katmanında dört köşe işaretinden oluşan algılama simgesi ve soyut veri akışı. Atış ve hedefleme yok. | Yakın mesafe dron savunması |
| 29–35 sn | Final | Antrasit stüdyo, üç çeyrek açı; kamera yavaşça geri çekilir. Ürün sağda, solda logo ve başlık için temiz boşluk. | DRON KALKANI (yazısız sürümde boş) |

Filmin iki hâli vardır: **yazılı** (dört kısa yazıyla) ve **yazısız** (kurguda logo ve başlık eklemek için). Grafik katmanları iki hâlde de durur.

## Nasıl üretildi

1. **Model.** `render/3d/kule_parcala.py`, kule CAD modelini (`modeller/taret.glb`) parçalara ayırır: sabit taban, yatay dönen gövde, dikey dönen beşik, tüfekler, namlular ve vidalar. Dönüş eksenleri modelden bulunur. Çıktı `modeller/kule-parcalar.npz`.
2. **Aynalama düzeltmesi.** `taret.glb` aynalı aktarılmış: kabartma yazılar ters okunuyor ve ters monte tüfek kulenin sağında duruyordu; saha fotoğraflarında solunda. Betik modeli aynalayarak fotoğraflardaki yerleşime getirir.
3. **3B çekimler.** `render/3d/urunfilmi.py`, Blender (Cycles) ile render eder. Malzemeler fizikseldir: mat kum rengi boya, siyah polimer ve eloksal, çelik namlu, çinko vida, yansıma önleyici kaplamalı bombeli sensör camı; kenarlar yuvarlatılmıştır. Stüdyo: iki ince kenar ışığı, üst şerit, yumuşak ana ışık, hafif dolgu.
4. **Araç sahneleri.** `render/3d/pikap3b.py` gerçekçi bir çift kabin pikap kurar: kesitlerden örülen yumuşak gövde, camlar, kapı aralıkları, çamurluk kaplamaları, çok kollu jantlar ve lastikler, nervürlü kasa, stop lambaları, tampon, tozlu mat kamuflaj kaplama. Araçta marka işareti ve plaka yoktur. Arazi: kuru toprak, taşlar, kuru ot, uzak tepeler, alçak güneş. İlk sürümde bu sahne gerçek fotoğrafa bindirmeydi; kullanıcının isteğiyle tamamı 3B yapıldı.
5. **Tesis ve deniz sahneleri.** `render/3d/sahneler.py` ortamlarına aynı kule yerleştirilir.
6. **Kurgu.** `urunfilmi/index.html`: çekimleri sıraya dizer, geçişleri, yavaş kamera hareketlerini, grafik katmanlarını ve yazıları çizer. `render/3d/urunfilmi_topla.py` renderları sayfanın klasörüne toplar.
7. **Ses.** `render/ses/urunfilmi_ses.py`: alçak frekanslı atmosfer, ışık devresi tıkırtıları, hafif servo sesi, geçiş hışırtıları, ortam sesleri. Tamamı sentez. Atış ya da patlama sesi yoktur.

```
python3 render/3d/kule_parcala.py
/root/bpyenv/bin/python render/3d/urunfilmi.py acilis --kalite final --ornek 24 --cikti render/out/urunfilmi/acilis
for c in final sensor govde cam yuzey tesis deniz; do /root/bpyenv/bin/python render/3d/urunfilmi.py $c --kalite final --cikti render/out/urunfilmi; done
for c in pikap gok; do /root/bpyenv/bin/python render/3d/urunfilmi.py $c --kalite final --cikti render/out/urunfilmi; done
python3 render/3d/urunfilmi_topla.py
python3 render/ses/urunfilmi_ses.py render/out/urunfilmi-ses.wav   # ardından ffmpeg ile urunfilmi/assets/ses.mp3
node render/render.mjs --sayfa urunfilmi --out surumler/urun-filmi-35sn.mp4
node render/render.mjs --sayfa urunfilmi --sorgu temiz=1 --out surumler/urun-filmi-35sn-yazisiz.mp4
```

## Brife göre sapmalar ve bilinmesi gerekenler

- **Çözünürlük 4K değil, 1080p.** Bu ortamda ekran kartı yok; 4K render süresi günlerle ölçülür. Tek kare çekimler 2880 piksel genişliğinde render edildi, film 1920×1080 çıktı verir.
- **Gerçek 3B kamera hareketi yalnızca açılışta.** Diğer çekimler yüksek çözünürlüklü tek karedir; kamera hareketi kurguda verilir (yavaş yaklaşma, kayma, geri çekilme). Bu çekimlerde bakış açısı değişmez.
- **Sensör ünitesi ve tripod temsilîdir.** CAD montajında yoklar; saha fotoğraflarına bakılarak modellendi (sensör ünitesi yaklaşık 19 × 19 × 16 cm, iki camlı, yanlarda yarıklı). Gerçek parçaların modeli gelirse değiştirilmeli.
- **CAD modeli ile sahadaki kule birebir aynı değil.** Fotoğraftaki kule daha basık duruyor; kablolar ve tüfek üzerindeki ek kutu modelde yok. Film bütün sahnelerde CAD modelini kullanır.
- **Araç, elle kurulmuş genel bir pikap modelidir.** Belirli bir markanın modeli değildir; ölçüler orta sınıf bir çift kabin pikaba göredir. Ön yüzü sadedir; çekimler aracı arkadan ve yandan gösterir.
- **Bütün ortamlar bilgisayar üretimidir:** arazi, tesis, deniz.
- **Şarjörlerdeki "MAX" kabartması** modelin kendi geometrisidir ve bazı çekimlerde seçilir. Yakın planlar bu yazıyı kadraj dışında bırakacak biçimde kuruldu.
- **Dron temsilîdir:** filmin ortak 3B dron görüntüsü, uzakta ve küçük.
- **Ses** ölçümle doğrulandı, kulakla dinlenmedi.
