const { seg, eo, eio, lerp, TextFx } = kit;
const TEH_DR = [
  { x0: 1880, y0: 250, x1: 1460, y1: 400, s0: .42, s1: 1.15, d: 0 },
  { x0: 1960, y0: 150, x1: 1240, y1: 260, s0: .3, s1: .78, d: .35 },
  { x0: 1900, y0: 400, x1: 1690, y1: 560, s0: .5, s1: 1.4, d: .7 },
  { x0: 2060, y0: 110, x1: 1620, y1: 190, s0: .24, s1: .55, d: 1 },
  { x0: 2080, y0: 330, x1: 1360, y1: 520, s0: .3, s1: .95, d: .5 },
];
kit.scene('tehdit', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground">' +
      '<svg class="art" viewBox="0 0 1920 1080">' +
      '<rect class="sky" width="1920" height="1080"/>' +
      '<path class="hill3 tehdit-h3" d="' + DK.hills(660, 55, 1) + '"/>' +
      '<path class="hill2 tehdit-h2" d="' + DK.hills(790, 60, 2.3, 3, 7) + '"/>' +
      TEH_DR.map(() => '<g class="tehdit-d">' + DK.drone() + '</g>').join('') +
      '<path class="hill1 tehdit-h1" d="' + DK.hills(930, 40, 4.1, 2, 6) + '"/>' +
      '</svg>' +
      '<div class="words" style="left:140px;top:200px;width:1150px"><p class="tag tehdit-tag">TEHDİT</p>' +
      '<h1 class="line big">Dron tehdidi artık her yerde.</h1><p class="en" data-at="0.2">Drone threats are now everywhere.</p></div></div>'));
    const q = s => kit.stage.querySelector(s);
    this.h = [q('.tehdit-h3'), q('.tehdit-h2'), q('.tehdit-h1')];
    this.dr = [...kit.stage.querySelectorAll('.tehdit-d')];
    this.tag = q('.tehdit-tag').style;
    this.line = q('.line');
    this.ens = [...kit.stage.querySelectorAll('.en')];
  },
  render(t) {
    DK.en(this.ens, t);
    [7, 15, 26].forEach((v, i) => this.h[i].setAttribute('transform', 'translate(' + (-(t + 1) * v) + ',0)'));
    TEH_DR.forEach((d, i) => {
      const p = eio(seg(t, d.d - 1.2, 4.6));
      const x = lerp(d.x0, d.x1, p), y = lerp(d.y0, d.y1, p) + Math.sin(t * 2.4 + i * 1.7) * 6;
      const s = lerp(d.s0, d.s1, p), tilt = -8 + Math.sin(t * 1.9 + i) * 2;
      this.dr[i].setAttribute('transform', 'translate(' + x.toFixed(1) + ',' + y.toFixed(1) + ') rotate(' + tilt.toFixed(2) + ') scale(' + s.toFixed(3) + ')');
    });
    this.tag.opacity = eo(seg(t, -0.8, -0.3));
    this.tag.transform = 'translateX(' + lerp(26, 0, eo(seg(t, -0.8, -0.3))) + 'px)';
    TextFx.fadeFromRight(this.line, t, -0.7);
  },
});