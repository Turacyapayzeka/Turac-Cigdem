const { seg, eo, eob, lerp, TextFx } = kit;
const OR = [
  ['PROJE LİDERİ', 'Turaç', 'Sterling 12 kalibre magnum anti-drone mühimmat, kendi tesislerinde üretim', 'Project lead: Sterling 12-gauge magnum anti-drone ammunition, made in-house'],
  ['ATIŞ BİRİMİ', 'Derya Arms', '12 kalibre yarı otomatik Derya MAX tüfekler', 'Firing unit: Derya MAX 12-gauge semi-automatic shotguns'],
  ['KULE VE SENSÖR', 'Lasersan', 'Robotik kule ve görüntüleme sistemleri', 'Turret and sensors: robotic turret and imaging systems'],
  ['ENTEGRASYON', 'Urban Savunma', 'Mekanik tasarım ve kulenin araçlara entegrasyonu', 'Integration: mechanical design and vehicle integration'],
];
kit.scene('ortak', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground">' +
      '<svg class="art" viewBox="0 0 1920 1080"><rect class="sky" width="1920" height="1080"/>' +
      '<path class="hill3 ortak-h" d="' + DK.hills(990, 22, 2.8) + '"/></svg>' +
      '<div class="words" style="left:140px;top:90px;width:1150px;gap:16px"><p class="tag ortak-tag">ORTAK YAPIM</p>' +
      '<h2 class="line">Dört firmanın ortak ürünü</h2><p class="en" data-at="0.8">A joint product of four companies</p>' +
      '<p class="sub ortak-sub">Turaç liderliğinde geliştirildi</p><p class="en" data-at="1.3">Developed under the leadership of Turaç</p></div>' +
      '<div class="ortak-logo" style="position:absolute;left:1480px;top:80px">' + DK.trcLogo(300) + '</div>' +
      OR.map((c, i) => '<div class="card ortak-c" style="position:absolute;left:' + (140 + i * 430) + 'px;top:470px;width:390px">' +
        '<p class="tag" style="font-size:22px">' + c[0] + '</p><p class="card-name">' + c[1] + '</p><p class="card-txt">' + c[2] + '</p>' +
        '<p class="en s">' + c[3] + '</p></div>').join('') +
      '<div class="words ortak-ai" style="left:140px;top:880px;width:1640px;gap:10px"><p class="tag" style="font-size:22px">YAPAY ZEKA</p>' +
      '<p class="sub">Takip ve angajman algoritmaları: İTÜ ARC</p><p class="en s">Tracking and engagement algorithms: İTÜ ARC</p></div></div>'));
    const q = s => kit.stage.querySelector(s);
    this.h = q('.ortak-h');
    this.cs = [...kit.stage.querySelectorAll('.ortak-c')].map(e => e.style);
    for (const k of ['tag', 'sub', 'logo', 'ai']) this[k] = q('.ortak-' + k).style;
    this.line = q('.line');
    this.ens = [...kit.stage.querySelectorAll('.en')];
  },
  render(t) {
    DK.en(this.ens, t);
    this.h.setAttribute('transform', 'translate(' + (-t * 6) + ',0)');
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .1);
    this.sub.opacity = eo(seg(t, .8, 1.2));
    // Turaç logosu bir noktadan büyüyüp yerine oturur
    const lp = seg(t, .4, 1.2);
    this.logo.opacity = eo(seg(t, .4, .6));
    this.logo.transform = 'scale(' + (lerp(.2, 1, eob(lp, 1.7)) * kit.breathe(t, .008)).toFixed(4) + ') rotate(' + lerp(-20, 0, eo(lp)).toFixed(2) + 'deg)';
    this.logo.transformOrigin = '150px 150px';
    this.cs.forEach((c, i) => {
      const p = seg(t, 1.1 + i * .3, 1.65 + i * .3);
      c.opacity = eo(p);
      c.transform = 'translateY(' + lerp(28, 0, eo(p)).toFixed(1) + 'px)';
    });
    const a = seg(t, 2.6, 3.1);
    this.ai.opacity = eo(a);
    this.ai.transform = 'translateX(' + lerp(26, 0, eo(a)).toFixed(1) + 'px)';
  },
});