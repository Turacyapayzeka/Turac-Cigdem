const { seg, eo, eio, lerp, TextFx } = kit;
kit.scene('acilis', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><img class="photo acilis-p" alt="" src="' + kit.assets.url('ph-pickup.jpg') + '" style="transform-origin:24% 18%"><div class="shade"></div></div>'));
    const svg = kit.svgLayer();
    svg.innerHTML = '<path class="ink-w acilis-c" d="' + DK.corners(60, 60, 1800, 960, 80) + '"/>' +
      '<path class="ink acilis-r" d="M120 1010 H1800"/>' +
      Array.from({ length: 29 }, (_, i) => '<path class="ink acilis-k" d="M' + (120 + i * 60) + ' 1010 V' + (i % 5 ? 998 : 986) + '"/>').join('');
    this.c = svg.querySelector('.acilis-c'); this.r = svg.querySelector('.acilis-r');
    this.ks = [...svg.querySelectorAll('.acilis-k')].map(e => e.style);
    this.cl = this.c.getTotalLength(); this.rl = this.r.getTotalLength();
    this.c.style.strokeDasharray = this.cl; this.r.style.strokeDasharray = this.rl;
    kit.stage.append(kit.h('<div class="words" style="left:120px;top:660px;width:1400px"><p class="tag acilis-tag">OTONOM ROBOTİK ANTİ-DRONE KULE</p>' +
      '<h1 class="line big">Dron Kalkanı</h1><p class="en acilis-en">Autonomous robotic anti-drone turret</p></div>'));
    this.p = kit.stage.querySelector('.acilis-p').style;
    this.tag = kit.stage.querySelector('.acilis-tag').style;
    this.en = kit.stage.querySelector('.acilis-en').style;
    this.line = kit.stage.querySelector('.line');
  },
  render(t) {
    // Fotoğraf yavaşça geri çekilir; teknik çerçeve ve cetvel çizilir
    this.p.transform = 'scale(' + lerp(1.14, 1.02, eio(seg(t, -0.6, 5))).toFixed(4) + ')';
    this.c.style.strokeDashoffset = (this.cl * (1 - eio(seg(t, -0.3, 1.4)))).toFixed(1);
    this.r.style.strokeDashoffset = (this.rl * (1 - eo(seg(t, .6, 2)))).toFixed(1);
    this.ks.forEach((k, i) => { k.opacity = eo(seg(t, .6 + i * .045, .8 + i * .045)); });
    this.tag.opacity = eo(seg(t, -0.8, -0.3));
    TextFx.fadeFromRight(this.line, t, -0.6);
    this.en.opacity = eo(seg(t, .5, 1));
    this.en.transform = 'translateX(' + lerp(20, 0, eo(seg(t, .5, 1))).toFixed(1) + 'px)';
  },
});