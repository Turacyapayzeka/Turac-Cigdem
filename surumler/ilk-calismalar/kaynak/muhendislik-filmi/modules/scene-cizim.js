const { seg, eo, eio, eob, lerp, TextFx } = kit;
// Katmanlar arkadan öne; dx, dy: parçalara ayrılınca kayma (px)
const CZ = [
  { f: 'ln-gunback.png', dx: 150, dy: -120 },
  { f: 'ln-base.png', dx: 0, dy: 190 },
  { f: 'ln-cross.png', dx: 0, dy: -50 },
  { f: 'ln-eo.png', dx: -30, dy: -200 },
  { f: 'ln-gunfront.png', dx: -60, dy: 150 },
];
kit.scene('cizim', {
  init(kit) {
    const img = (f, cls) => '<img class="' + cls + '" alt="" src="' + kit.assets.url(f) + '" style="position:absolute;left:160px;top:90px;width:1600px;height:900px">';
    kit.stage.append(kit.h('<div class="ground"><div class="grid cizim-g"></div><div class="cizim-w" style="position:absolute;inset:0;transform-origin:960px 540px">' +
      img('ln-all.png', 'cizim-all') + CZ.map(c => img(c.f, 'cizim-l')).join('') + '</div></div>'));
    this.C = DK.callouts(kit, [
      { x: 866, y: 210, lx: 1480, ly: 170, firm: 'LASERSAN', tr: 'Sensör kutusu', en: 'Sensor housing' },
      { x: 1350, y: 322, lx: 1480, ly: 380, firm: 'ATIŞ BİRİMİ', tr: '12 kalibre, düz monte', en: 'Upright mount' },
      { x: 740, y: 680, lx: 540, ly: 640, firm: 'ATIŞ BİRİMİ', tr: '12 kalibre, ters monte', en: 'Inverted mount' },
      { x: 904, y: 905, lx: 1480, ly: 860, firm: 'LASERSAN', tr: 'Robotik kule gövdesi', en: 'Pan-tilt turret body' },
    ]);
    kit.stage.append(kit.h('<div class="words" style="left:120px;top:80px;width:700px"><p class="tag cizim-tag">TEKNİK ÇİZİM</p>' +
      '<h2 class="line">Mühendislik</h2><p class="en cizim-en">Engineering</p></div>'));
    this.g = kit.stage.querySelector('.cizim-g').style;
    this.w = kit.stage.querySelector('.cizim-w').style;
    this.all = kit.stage.querySelector('.cizim-all').style;
    this.ls = [...kit.stage.querySelectorAll('.cizim-l')].map(e => e.style);
    this.tag = kit.stage.querySelector('.cizim-tag').style;
    this.en = kit.stage.querySelector('.cizim-en').style;
    this.line = kit.stage.querySelector('.line');
  },
  render(t, kit) {
    this.g.opacity = eo(seg(t, 0, .8));
    this.w.transform = 'scale(' + lerp(1, 1.025, seg(t, 0, 7)).toFixed(4) + ')';
    // Çizim soldan sağa belirir, sonra parçalarına ayrılır
    const wipe = eio(seg(t, .1, 1.3));
    this.all.clipPath = 'inset(0 ' + ((1 - wipe) * 100).toFixed(2) + '% 0 0)';
    const split = t >= 2;
    this.all.opacity = split ? 0 : 1;
    const k = eob(seg(t, 2, 3.3), 1.5);
    CZ.forEach((c, i) => {
      this.ls[i].opacity = split ? 1 : 0;
      this.ls[i].transform = 'translate(' + (c.dx * k).toFixed(1) + 'px,' + (c.dy * k).toFixed(1) + 'px)';
    });
    DK.drawCallouts(this.C, t, 3.4, .35, kit);
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .1);
    this.en.opacity = eo(seg(t, .7, 1.2));
  },
});