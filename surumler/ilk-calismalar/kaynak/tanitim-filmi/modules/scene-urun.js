const { seg, eo, eio, lerp, TextFx } = kit;
// Gerçek taret fotoğrafı: yavaşça geri çekilir, ürün adı solda yerleşir
kit.scene('urun', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><img class="urun-p" alt="" src="' + kit.assets.url('ph-turret.jpg') + '" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:60% 50%">' +
      '<div style="position:absolute;inset:0;background:linear-gradient(90deg, color-mix(in srgb, var(--ground) 82%, transparent) 0%, color-mix(in srgb, var(--ground) 40%, transparent) 42%, transparent 62%)"></div>' +
      '<div class="words" style="left:140px;top:250px;width:900px"><p class="tag urun-tag">ARAÇ · GEMİ · KULE</p>' +
      '<h1 class="line big urun-name">Dron Kalkanı</h1><p class="en" data-at="1.6">Drone Shield</p>' +
      '<p class="sub urun-sub">Araca, gemiye ya da sabit tesise takılan otonom anti-drone kule</p>' +
      '<p class="en" data-at="2.4">An autonomous anti-drone turret for vehicles, ships and fixed sites</p></div></div>'));
    const q = s => kit.stage.querySelector(s);
    this.p = q('.urun-p').style;
    this.tag = q('.urun-tag').style;
    this.sub = q('.urun-sub').style;
    this.name = q('.urun-name');
    this.ens = [...kit.stage.querySelectorAll('.en')];
  },
  render(t) {
    DK.en(this.ens, t);
    this.p.transform = 'scale(' + lerp(1.1, 1, eio(seg(t, -0.3, 5))).toFixed(4) + ')';
    this.tag.opacity = eo(seg(t, .4, .9));
    this.tag.transform = 'translateX(' + lerp(26, 0, eo(seg(t, .4, .9))) + 'px)';
    TextFx.fadeFromRight(this.name, t, .7);
    this.sub.opacity = eo(seg(t, 1.9, 2.5));
    this.sub.transform = 'translateX(' + lerp(26, 0, eo(seg(t, 1.9, 2.5))) + 'px)';
  },
});