# Dron Kalkanı Ürün Filmi (35 sn)

Fuar ekranı için kısa, sinematik ürün filmi. Tanıtım filminden (`animasyon/`) ayrı bir çalışmadır: atış, hedefleme ya da angajman göstermez; ürünü ve kullanıldığı platformları tanıtır. **Film yalnızca bilgisayar üretimi görüntülerden oluşur; gerçek fotoğraf ya da çekim içermez.** Araç çekiminde aracın görüntüsü, kullanıcının gönderdiği stüdyo render'ıdır; kule ona 3B olarak yerleştirilir.

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
| 14–23 sn | Platform entegrasyonu | Pikap kasasında (aracın stüdyo görüntüsü; genel plandan kasadaki kuleye yaklaşma), sabit tesis platformunda, deniz platformunda. Her birinde yavaş yaklaşma ya da uzaklaşma. | Kara • Deniz • Sabit tesis |
| 23–29 sn | Durumsal farkındalık | 3B araç sahnesinin alçak ve geniş açısı: kadrajın çoğu gökyüzü; uzakta küçük, temsilî bir dron süzülür. Ayrı grafik katmanında dört köşe işaretinden oluşan algılama simgesi ve soyut veri akışı. Atış ve hedefleme yok. | Yakın mesafe dron savunması |
| 29–35 sn | Final | Antrasit stüdyo, üç çeyrek açı; kamera yavaşça geri çekilir. Ürün sağda, solda logo ve başlık için temiz boşluk. | DRON KALKANI (yazısız sürümde boş) |

Filmin iki hâli vardır: **yazılı** (dört kısa yazıyla) ve **yazısız** (kurguda logo ve başlık eklemek için). Grafik katmanları iki hâlde de durur.

## Nasıl üretildi

1. **Model.** `render/3d/kule_parcala.py`, kule CAD modelini (`modeller/taret.glb`) parçalara ayırır: sabit taban, yatay dönen gövde, dikey dönen beşik, tüfekler, namlular ve vidalar. Dönüş eksenleri modelden bulunur. Çıktı `modeller/kule-parcalar.npz`.
2. **Aynalama düzeltmesi.** `taret.glb` aynalı aktarılmış: kabartma yazılar ters okunuyor ve ters monte tüfek kulenin sağında duruyordu; saha fotoğraflarında solunda. Betik modeli aynalayarak fotoğraflardaki yerleşime getirir.
3. **3B çekimler.** `render/3d/urunfilmi.py`, Blender (Cycles) ile render eder. Malzemeler fizikseldir: mat kum rengi boya, siyah polimer ve eloksal, çelik namlu, çinko vida, yansıma önleyici kaplamalı bombeli sensör camı; kenarlar yuvarlatılmıştır. Stüdyo: iki ince kenar ışığı, üst şerit, yumuşak ana ışık, hafif dolgu.
4. **Araç çekimi.** Aracın görüntüsü, kullanıcının gönderdiği fotoğraf gerçekliğindeki stüdyo render'ıdır (`docs/kaynak-gorseller/amarok-ust-render.jpg`; araç üstten arka çaprazdan, kasa boş). `render/rotus/pikap_studyo.py` bu görüntüden başka firma işaretlerini (arka kapak amblemi ve yazısı, ikinci firma işareti, lastik ve jant yazıları) ve plaka yazısını temizler, görüntüyü iki kat büyütür ve kamerasını çözer. `render/3d/urunfilmi.py pikap`, kuleyi ve tripodu aynı kamerayla, stüdyo ışığında iki saydam katman olarak render eder; betiğin `birlestir` adımı katmanları araca bindirir: tripodun kasa kenarının altında kalan kısmı yalnızca kasa ağzından görünür, gölgesi kasa tabanına düşer. Kadraj yanlardan 16:9'a tamamlanır.
   Bu çekim üç kez değişti: önce gerçek fotoğrafa bindirmeydi (kullanıcı gerçek görüntü istemedi), sonra kodla kurulan 3B pikaptı (kullanıcı ilkel buldu), şimdi kullanıcının onayladığı stüdyo render'ıdır.
5. **Gökyüzü çekimi.** `render/3d/pikap3b.py` bir çift kabin pikabı ve açık araziyi kodla kurar; durumsal farkındalık çekimi bu sahnenin alçak açısıdır. Kadrajda araçtan yalnızca anten görünür.
6. **Tesis ve deniz sahneleri.** `render/3d/sahneler.py` ortamlarına aynı kule yerleştirilir.
7. **Kurgu.** `urunfilmi/index.html`: çekimleri sıraya dizer, geçişleri, yavaş kamera hareketlerini, grafik katmanlarını ve yazıları çizer. `render/3d/urunfilmi_topla.py` renderları sayfanın klasörüne toplar.
8. **Ses.** `render/ses/urunfilmi_ses.py`: alçak frekanslı atmosfer, ışık devresi tıkırtıları, hafif servo sesi, geçiş hışırtıları, ortam sesleri. Tamamı sentez. Atış ya da patlama sesi yoktur.

```
python3 render/3d/kule_parcala.py
/root/bpyenv/bin/python render/3d/urunfilmi.py acilis --kalite final --ornek 24 --cikti render/out/urunfilmi/acilis
for c in final sensor govde cam yuzey tesis deniz; do /root/bpyenv/bin/python render/3d/urunfilmi.py $c --kalite final --cikti render/out/urunfilmi; done
python3 render/rotus/pikap_studyo.py hazirla --cikti render/out/urunfilmi/pikap [--model EDSR_x2.pb]   # rötuş, büyütme, kamera
/root/bpyenv/bin/python render/3d/urunfilmi.py pikap --kalite final --cikti render/out/urunfilmi         # kule katmanları
python3 render/rotus/pikap_studyo.py birlestir --cikti render/out/urunfilmi/pikap                       # araç + kule
/root/bpyenv/bin/python render/3d/urunfilmi.py gok --kalite final --cikti render/out/urunfilmi
python3 render/3d/urunfilmi_topla.py
python3 render/ses/urunfilmi_ses.py render/out/urunfilmi-ses.wav   # ardından ffmpeg ile urunfilmi/assets/ses.mp3
node render/render.mjs --sayfa urunfilmi --out surumler/urun-filmi-35sn.mp4
node render/render.mjs --sayfa urunfilmi --sorgu temiz=1 --out surumler/urun-filmi-35sn-yazisiz.mp4
```

Büyütme için `--model` ile OpenCV'nin süper çözünürlük modeli verilebilir (EDSR ×2; `opencv-contrib` gerekir). Verilmezse görüntü Lanczos ile büyütülür. Büyütülmüş kaynak `render/out/urunfilmi/pikap/kaynak-2x.png` olarak saklanır; rötuş değişince yeniden büyütülmez.

## Brife göre sapmalar ve bilinmesi gerekenler

- **Çözünürlük 4K değil, 1080p.** Bu ortamda ekran kartı yok; 4K render süresi günlerle ölçülür. Tek kare çekimler 2880 piksel genişliğinde render edildi, film 1920×1080 çıktı verir.
- **Gerçek 3B kamera hareketi yalnızca açılışta.** Diğer çekimler yüksek çözünürlüklü tek karedir; kamera hareketi kurguda verilir (yavaş yaklaşma, kayma, geri çekilme). Bu çekimlerde bakış açısı değişmez.
- **Sensör ünitesi ve tripod temsilîdir.** CAD montajında yoklar; saha fotoğraflarına bakılarak modellendi (sensör ünitesi yaklaşık 19 × 19 × 16 cm, iki camlı, yanlarda yarıklı). Gerçek parçaların modeli gelirse değiştirilmeli.
- **CAD modeli ile sahadaki kule birebir aynı değil.** Fotoğraftaki kule daha basık duruyor; kablolar ve tüfek üzerindeki ek kutu modelde yok. Film bütün sahnelerde CAD modelini kullanır.
- **Aracın 3B modeli yok; tek bir görüntüsü var.** Araç çekimi kullanıcının stüdyo render'ına dayanır, bu yüzden aracı yalnızca o açıdan gösterir; kamera aracın çevresinde dönemez. Başka açılar için aracın gerçek 3B modeli (GLB, FBX ya da OBJ) gerekir. Bu ortamdan model sitelerine (Sketchfab, Hugging Face ve benzeri) erişim kapalı olduğu için hazır model indirilemedi.
- **Stüdyo render'ı ölçülü değil.** Görüntü yapay üretim izleri taşıyor (lastik yazıları bozuk, perspektif kendi içinde tutarsız). Kamera bu yüzden kasanın çevresinde paralel izdüşümle eşlendi: kasa ağzının dört köşesi görüntüde işaretlendi, boy ve en yönleri buradan, düşey yön dik izdüşüm koşulundan bulundu. Kule kasaya doğru ölçekte oturur; aracın uzak köşelerinde aynı eşleme geçerli değildir.
- **Araç görüntüsünde rötuş var.** Arka kapaktaki amblem ve model yazısı, ikinci firma işareti, lastik ve jant yazıları silindi; plaka boş bırakıldı. Sterling işaretleri duruyor.
- **Araç çekimi açık renk stüdyoda geçer;** filmin öbür stüdyo çekimleri koyu antrasittir. Görüntünün kenarları karartıldı, altına yazı için koyu geçiş eklendi.
- **Bütün ortamlar bilgisayar üretimidir:** arazi, tesis, deniz.
- **Şarjörlerdeki "MAX" kabartması** modelin kendi geometrisidir ve bazı çekimlerde seçilir. Yakın planlar bu yazıyı kadraj dışında bırakacak biçimde kuruldu.
- **Dron temsilîdir:** filmin ortak 3B dron görüntüsü, uzakta ve küçük.
- **Ses** ölçümle doğrulandı, kulakla dinlenmedi.
