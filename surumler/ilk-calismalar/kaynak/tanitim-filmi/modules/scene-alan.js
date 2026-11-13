const { seg, eo, eio, lerp, TextFx } = kit;
// Koruma alanı kubbeleri üç platformda; başlık sabit kalır, platform etiketi değişir
const AL = [
  { img: 'domes.jpg', a: 0, o: '50% 52%', c: 'PİKAP', e: 'Vehicle' },
  { img: 'ship.jpg', a: 2, o: '52% 45%', c: 'GEMİ', e: 'Ship' },
  { img: 'tower.jpg', a: 4, o: '50% 40%', c: 'RAFİNERİ', e: 'Refinery' },
];
kit.scene('alan', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground">' +
      AL.map(p => '<img class="alan-i" alt="" src="' + kit.assets.url(p.img) + '" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:' + p.o + '">').join('') +
      '<div style="position:absolute;inset:0;background:linear-gradient(0deg, color-mix(in srgb, var(--ground) 90%, transparent) 0%, transparent 46%)"></div>' +
      AL.map(p => '<div class="words alan-c" style="left:1500px;top:90px;width:320px;align-items:flex-end;gap:2px"><p class="chip" style="border-color:var(--main)">' + p.c + '</p><p class="en" style="margin-top:6px">' + p.e + '</p></div>').join('') +
      '<div class="words" style="left:120px;top:760px;width:1600px;gap:14px"><p class="tag alan-tag">KORUMA ALANI</p>' +
      '<h2 class="line">600–800 m tespit · 150 m angajman</h2><p class="en alan-en">Detection at 600–800 m · engagement at 150 m</p></div></div>'));
    this.im = [...kit.stage.querySelectorAll('.alan-i')].map(e => e.style);
    this.cs = [...kit.stage.querySelectorAll('.alan-c')].map(e => e.style);
    this.tag = kit.stage.querySelector('.alan-tag').style;
    this.en = kit.stage.querySelector('.alan-en').style;
    this.line = kit.stage.querySelector('.line');
  },
  render(t) {
    AL.forEach((p, i) => {
      this.im[i].opacity = i === 0 ? 1 : eio(seg(t, p.a, p.a + .45));
      this.im[i].transform = 'scale(' + lerp(1.02, 1.09, seg(t, p.a, p.a + 2.6)).toFixed(4) + ')';
      const inn = eo(seg(t, p.a + .2, p.a + .6)), out = i < AL.length - 1 ? 1 - eo(seg(t, AL[i + 1].a, AL[i + 1].a + .25)) : 1;
      this.cs[i].opacity = inn * out;
      this.cs[i].transform = 'translateY(' + lerp(-14, 0, inn).toFixed(1) + 'px)';
    });
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .15);
    this.en.opacity = eo(seg(t, .9, 1.4));
  },
});