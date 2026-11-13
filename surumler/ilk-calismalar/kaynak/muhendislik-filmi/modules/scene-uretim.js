const { seg, eo, eio, eob, lerp, TextFx } = kit;
const UR = [
  { pre: '', v: 1987, from: 1987, u: '', k: 'KURULUŞ', e: 'Founded' },
  { pre: '', v: 200, from: 100, u: 'M+', k: 'YILLIK FİŞEK KAPASİTESİ', e: 'Cartridges per year' },
  { pre: '%', v: 60, from: 30, u: '', k: 'İHRACAT', e: 'Of production exported' },
  { pre: '', v: 90, from: 45, u: '+', k: 'ÜLKE', e: 'Export countries' },
];
const PT = [
  ['Turaç', 'Proje lideri', 'Project lead'], ['Derya Arms', 'Atış birimi', 'Firing unit'], ['Lasersan', 'Kule ve sensör', 'Turret and sensors'],
  ['Urban Savunma', 'Entegrasyon', 'Integration'], ['İTÜ ARC', 'Yapay zekâ', 'AI algorithms'],
];
kit.scene('uretim', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><div class="grid"></div></div>'));
    kit.stage.append(kit.h('<div class="words" style="left:120px;top:90px;width:1300px"><p class="tag uretim-tag">ORTAK ÜRETİM</p>' +
      '<h2 class="line">Turaç liderliğinde dört firma</h2><p class="en uretim-en">Four companies, led by Turaç</p></div>'));
    kit.stage.append(kit.h('<div class="uretim-logo" style="position:absolute;left:1580px;top:70px;transform-origin:110px 110px">' + DK.trcLogo(220) + '</div>'));
    UR.forEach((d, i) => kit.stage.append(kit.h('<div class="stat uretim-s" style="position:absolute;left:' + (120 + i * 430) + 'px;top:360px;width:380px">' +
      '<div style="display:flex;align-items:baseline"><p class="unit" style="margin:0 6px 0 0">' + d.pre + '</p><p class="num uretim-n" style="font-size:96px">' + d.v + '</p><p class="unit">' + d.u + '</p></div>' +
      '<p class="firm">' + d.k + '</p><p class="en">' + d.e + '</p></div>')));
    PT.forEach((p, i) => kit.stage.append(kit.h('<div class="lab uretim-p" style="left:' + (120 + i * 340) + 'px;top:760px;width:310px"><b>' + p[0] + '</b><p class="firm">' + p[1].toLocaleUpperCase('tr') + '</p><p class="en">' + p[2] + '</p></div>')));
    this.logo = kit.stage.querySelector('.uretim-logo').style;
    this.ss = [...kit.stage.querySelectorAll('.uretim-s')].map(e => e.style);
    this.ns = [...kit.stage.querySelectorAll('.uretim-n')];
    this.ps = [...kit.stage.querySelectorAll('.uretim-p')].map(e => e.style);
    this.tag = kit.stage.querySelector('.uretim-tag').style;
    this.en = kit.stage.querySelector('.uretim-en').style;
    this.line = kit.stage.querySelector('.line');
  },
  render(t) {
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .1);
    this.en.opacity = eo(seg(t, .7, 1.2));
    const lp = seg(t, .3, 1.1);
    this.logo.opacity = eo(seg(t, .3, .5));
    this.logo.transform = 'scale(' + lerp(.3, 1, eob(lp, 1.6)).toFixed(3) + ')';
    UR.forEach((d, i) => {
      const a = .9 + i * .3, p = eo(seg(t, a, a + .5));
      this.ss[i].opacity = p;
      this.ss[i].transform = 'translateY(' + lerp(24, 0, p).toFixed(1) + 'px)';
      const v = Math.round(lerp(d.from, d.v, eio(seg(t, a, a + 1.2))));
      if (this.ns[i].textContent !== String(v)) this.ns[i].textContent = String(v);
    });
    this.ps.forEach((s, i) => {
      const a = 2.5 + i * .18, p = eo(seg(t, a, a + .45));
      s.opacity = p;
      s.transform = 'translateX(' + lerp(20, 0, p).toFixed(1) + 'px)';
    });
  },
});