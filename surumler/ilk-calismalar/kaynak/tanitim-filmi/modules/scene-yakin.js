const { seg, eo, eio, lerp } = kit;
// Gerçek saha fotoğrafları: her biri yavaşça yaklaşır, bir sonrakine çapraz geçişle devreder
const YK = [
  { img: 'ph-yan.jpg', a: 0, b: 2.6, o: '76% 32%', s0: 1.0, s1: 1.07, k: 'PİKAP ÜSTÜNDE', tr: 'Kasaya monte, sahaya hazır', en: 'Mounted on the pickup bed, ready for the field' },
  { img: 'ph-arka.jpg', a: 2.3, b: 4.9, o: '50% 36%', s0: 1.0, s1: 1.08, k: 'LASERSAN', tr: 'Robotik kule ve pasif sensörler', en: 'Robotic turret with passive sensors' },
  { img: 'ph-turret.jpg', a: 4.6, b: 7.2, o: '60% 50%', s0: 1.0, s1: 1.06, k: 'ÇİFT NAMLU', tr: 'Çift 12 kalibre, biri ters monte', en: 'Twin 12-gauge shotguns, one mounted inverted' },
];
kit.scene('yakin', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground">' +
      YK.map(p => '<img class="yakin-i" alt="" src="' + kit.assets.url(p.img) + '" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:' + p.o + '">').join('') +
      '<div style="position:absolute;inset:0;background:linear-gradient(0deg, color-mix(in srgb, var(--ground) 90%, transparent) 0%, transparent 50%)"></div>' +
      YK.map(p => '<div class="words yakin-w" style="left:120px;top:690px;width:1560px;gap:14px"><p class="tag">' + p.k + '</p><h2 class="line">' + p.tr + '</h2><p class="en">' + p.en + '</p></div>').join('') + '</div>'));
    this.im = [...kit.stage.querySelectorAll('.yakin-i')].map(e => e.style);
    this.w = [...kit.stage.querySelectorAll('.yakin-w')].map(e => e.style);
  },
  render(t) {
    YK.forEach((p, i) => {
      this.im[i].opacity = i === 0 ? 1 : eio(seg(t, p.a, p.a + .45));
      this.im[i].transform = 'scale(' + lerp(p.s0, p.s1, eio(seg(t, p.a, p.b))).toFixed(4) + ')';
      const a0 = i ? p.a + .35 : -0.5, inn = eo(seg(t, a0, a0 + .45));
      const out = i < YK.length - 1 ? 1 - eo(seg(t, YK[i + 1].a, YK[i + 1].a + .3)) : 1;
      this.w[i].opacity = inn * out;
      this.w[i].transform = 'translateX(' + lerp(26, 0, inn).toFixed(1) + 'px)';
    });
  },
});