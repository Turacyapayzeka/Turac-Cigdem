const { seg, eo, eio, lerp } = kit;
kit.scene('kule', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><img class="photo kule-p" alt="" src="' + kit.assets.url('ph-turret.jpg') + '" style="transform-origin:60% 50%">' +
      '<div style="position:absolute;inset:0;background:linear-gradient(0deg, color-mix(in srgb, var(--ground) 55%, transparent) 0%, transparent 30%)"></div></div>'));
    // Noktalar fotoğrafın 1,03 ölçeğindeki yerleri
    this.C = DK.callouts(kit, [
      { x: 686, y: 293, lx: 600, ly: 140, firm: 'ATIŞ BİRİMİ', tr: '2× 12 kalibre', en: 'Two semi-automatic 12-gauge shotguns' },
      { x: 1304, y: 519, lx: 1440, ly: 820, firm: 'LASERSAN', tr: 'Robotik kule gövdesi', en: 'Robotic turret body' },
      { x: 1103, y: 721, lx: 760, ly: 860, firm: 'TURAÇ · STERLING', tr: 'Magnum anti-drone mühimmat', en: 'Sterling magnum anti-drone ammunition' },
    ]);
    this.p = kit.stage.querySelector('.kule-p').style;
  },
  render(t, kit) {
    this.p.transform = 'scale(' + lerp(1, 1.06, eio(seg(t, -0.3, 5))).toFixed(4) + ')';
    DK.drawCallouts(this.C, t, .4, .6, kit);
  },
});