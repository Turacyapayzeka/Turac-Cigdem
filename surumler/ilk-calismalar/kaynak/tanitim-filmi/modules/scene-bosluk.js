const { seg, eo, eio, lerp, TextFx } = kit;
kit.scene('bosluk', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground">' +
      '<svg class="art" viewBox="0 0 1920 1080">' +
      '<rect class="sky" width="1920" height="1080"/>' +
      '<path class="hill3 bosluk-h" d="' + DK.hills(690, 45, 0.9) + '"/>' +
      '<path class="hill2 bosluk-h" d="' + DK.hills(820, 40, 3.6, 3, 7) + '"/>' +
      '<g class="bosluk-ws">' + '<circle cx="298" cy="566" style="fill:none;stroke:var(--main);stroke-width:5"/>'.repeat(4) + '</g>' +
      '<g class="bosluk-dr">' + DK.drone() + '</g>' +
      '<path class="hill1 bosluk-h" d="' + DK.hills(930, 22, 2.2, 2, 6) + '"/>' +
      '<rect class="trim" x="290" y="560" width="16" height="400"/>' +
      '<path class="seam" style="stroke-width:6" d="M268 600 L328 600 M274 640 L322 640 M240 960 L298 700 L356 960"/>' +
      '<rect class="trim" x="262" y="700" width="72" height="54" rx="4"/><circle class="lamp" cx="298" cy="560" r="9"/></svg>' +
      '<div class="words" style="left:120px;top:110px;width:1200px"><p class="tag bosluk-tag">SORUN</p>' +
      '<h2 class="line">Karıştırıcı her dronu durduramaz.</h2><p class="en" data-at="0.9">Jammers cannot stop every drone.</p>' +
      '<p class="sub bosluk-sub">Otonom ve fiber optik dronlar sinyal beklemez.</p>' +
      '<p class="en" data-at="1.7">Autonomous and fiber-optic drones do not wait for a signal.</p></div></div>'));
    const q = s => kit.stage.querySelector(s);
    this.hs = [...kit.stage.querySelectorAll('.bosluk-h')];
    this.ws = [...q('.bosluk-ws').children];
    this.dr = q('.bosluk-dr');
    this.tag = q('.bosluk-tag').style; this.sub = q('.bosluk-sub').style;
    this.line = q('.line');
    this.ens = [...kit.stage.querySelectorAll('.en')];
  },
  render(t) {
    DK.en(this.ens, t);
    this.hs.forEach((h, i) => h.setAttribute('transform', 'translate(' + (-t * (6 + i * 9)) + ',0)'));
    // Karıştırıcı dalgaları sürekli yayılır
    this.ws.forEach((w, i) => {
      const r = (t * 300 + i * 260) % 1040;
      w.setAttribute('r', (30 + r).toFixed(1));
      w.style.opacity = (0.55 * (1 - r / 1040) * eo(seg(t, -0.5, 0.3))).toFixed(3);
    });
    // Dron dalgaların içinden geçer, hiç sapmadan (yazıların altından)
    const p = seg(t, -0.6, 4.4), x = lerp(1960, 700, p), y = lerp(650, 600, p) + Math.sin(t * 2.3) * 6;
    this.dr.setAttribute('transform', 'translate(' + x.toFixed(1) + ',' + y.toFixed(1) + ') rotate(-6) scale(' + lerp(.55, 1.05, p).toFixed(3) + ')');
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .15);
    this.sub.opacity = eo(seg(t, 1.3, 1.8));
    this.sub.transform = 'translateX(' + lerp(26, 0, eo(seg(t, 1.3, 1.8))) + 'px)';
  },
});