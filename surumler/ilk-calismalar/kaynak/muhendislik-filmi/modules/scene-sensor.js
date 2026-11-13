const { seg, eo, eio, lerp, TextFx } = kit;
kit.scene('sensor', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><img class="photo sensor-p" alt="" src="' + kit.assets.url('ph-eo.jpg') + '" style="transform-origin:54% 76%"><div class="shade"></div></div>'));
    // Noktalar fotoğrafın 1,03 ölçeğindeki yerleri
    this.C = DK.callouts(kit, [
      { x: 1040, y: 732, lx: 1300, ly: 430, firm: 'PASİF ALGILAMA', tr: 'Elektro-optik ve akustik sensörler', en: 'Passive electro-optical and acoustic sensors' },
      { x: 999, y: 861, lx: 760, ly: 520, firm: 'İTÜ ARC', tr: 'Gömülü yapay zekâ', en: 'Embedded AI, processed on the turret' },
    ]);
    kit.stage.append(kit.h('<div class="words" style="left:120px;top:820px;width:780px"><p class="tag sensor-tag">KOMUTA</p>' +
      '<h2 class="line" style="font-size:64px">Otonom ya da uzaktan</h2><p class="en sensor-en">Autonomous, or remotely from a command console</p></div>'));
    this.p = kit.stage.querySelector('.sensor-p').style;
    this.tag = kit.stage.querySelector('.sensor-tag').style;
    this.en = kit.stage.querySelector('.sensor-en').style;
    this.line = kit.stage.querySelector('.line');
  },
  render(t, kit) {
    this.p.transform = 'scale(' + lerp(1, 1.06, eio(seg(t, -0.3, 5))).toFixed(4) + ')';
    DK.drawCallouts(this.C, t, .4, .7, kit);
    this.tag.opacity = eo(seg(t, 1.6, 2));
    TextFx.fadeFromRight(this.line, t, 1.7);
    this.en.opacity = eo(seg(t, 2.4, 2.9));
  },
});