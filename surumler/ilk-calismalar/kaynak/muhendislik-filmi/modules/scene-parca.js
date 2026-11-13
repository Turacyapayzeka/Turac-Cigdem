const { seg, eo, eio, lerp, TextFx } = kit;
kit.scene('parca', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><img class="photo parca-p" alt="" src="' + kit.assets.url('ph-pickup.jpg') + '" style="transform-origin:24% 18%"><div class="shade"></div></div>'));
    // Noktalar fotoğrafın 1,035 ölçeğindeki yerleri
    this.C = DK.callouts(kit, [
      { x: 522, y: 92, lx: 790, ly: 150, firm: 'LASERSAN', tr: 'Robotik kule', en: 'Robotic turret' },
      { x: 377, y: 324, lx: 790, ly: 360, firm: 'URBAN SAVUNMA', tr: 'Araç entegrasyonu', en: 'Mechanical design and vehicle integration' },
      { x: 1174, y: 480, lx: 1400, ly: 200, firm: 'PLATFORM', tr: 'Pikap kasası', en: 'Pickup bed mount' },
    ]);
    kit.stage.append(kit.h('<div class="words" style="left:120px;top:800px;width:1400px"><p class="tag parca-tag">SAHADA</p>' +
      '<h2 class="line">Kasaya monte, sahaya hazır</h2><p class="en parca-en">Mounted on the pickup bed, ready for the field</p></div>'));
    this.p = kit.stage.querySelector('.parca-p').style;
    this.tag = kit.stage.querySelector('.parca-tag').style;
    this.en = kit.stage.querySelector('.parca-en').style;
    this.line = kit.stage.querySelector('.line');
  },
  render(t, kit) {
    this.p.transform = 'scale(' + lerp(1.02, 1.05, seg(t, 0, 6)).toFixed(4) + ')';
    DK.drawCallouts(this.C, t, .5, .55, kit);
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .1);
    this.en.opacity = eo(seg(t, .8, 1.3));
  },
});