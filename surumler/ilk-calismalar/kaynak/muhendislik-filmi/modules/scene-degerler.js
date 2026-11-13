const { seg, eo, eio, lerp, TextFx } = kit;
const DG = [
  { v: '600–800', from: 0, u: 'm', k: 'TESPİT VE TAKİP', e: 'Detection and tracking range' },
  { v: 150, from: 75, u: 'm', k: 'ANGAJMAN', e: 'Engagement range' },
  { v: 2, from: 2, u: '×', k: '12 KALİBRE', e: 'Twin shotguns, Sterling ammunition' },
  { v: 0, from: 0, u: '', k: 'OPERATÖR GEREKMEZ', e: 'No operator needed for engagement' },
];
kit.scene('degerler', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><div class="grid"></div>' +
      '<img class="degerler-d" alt="" src="' + kit.assets.url('ln-all.png') + '" style="position:absolute;left:900px;top:250px;width:1100px;height:619px"></div>'));
    kit.stage.append(kit.h('<div class="words" style="left:120px;top:90px;width:900px"><p class="tag degerler-tag">DEĞERLER</p>' +
      '<h2 class="line">Rakamlarla</h2><p class="en degerler-en">In numbers</p></div>'));
    DG.forEach((d, i) => kit.stage.append(kit.h('<div class="stat degerler-s" style="position:absolute;left:' + (120 + (i % 2) * 560) + 'px;top:' + (390 + Math.floor(i / 2) * 320) + 'px;width:500px">' +
      '<div style="display:flex;align-items:baseline"><p class="num degerler-n">' + d.v + '</p><p class="unit">' + d.u + '</p></div>' +
      '<p class="firm">' + d.k + '</p><p class="en">' + d.e + '</p></div>')));
    this.d = kit.stage.querySelector('.degerler-d').style;
    this.ss = [...kit.stage.querySelectorAll('.degerler-s')].map(e => e.style);
    this.ns = [...kit.stage.querySelectorAll('.degerler-n')];
    this.tag = kit.stage.querySelector('.degerler-tag').style;
    this.en = kit.stage.querySelector('.degerler-en').style;
    this.line = kit.stage.querySelector('.line');
  },
  render(t) {
    this.d.opacity = (.3 * eo(seg(t, 0, 1))).toFixed(3);
    this.d.transform = 'translateX(' + lerp(30, 0, eio(seg(t, 0, 6))).toFixed(1) + 'px)';
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .1);
    this.en.opacity = eo(seg(t, .6, 1.1));
    // Değerler sırayla gelir; menziller yarı değerden sayarak dolar
    DG.forEach((d, i) => {
      const a = .8 + i * .45, p = eo(seg(t, a, a + .5));
      this.ss[i].opacity = p;
      this.ss[i].transform = 'translateY(' + lerp(24, 0, p).toFixed(1) + 'px)';
      const v = typeof d.v === 'string' ? d.v : Math.round(lerp(d.from, d.v, eio(seg(t, a, a + 1.2))));
      if (this.ns[i].textContent !== String(v)) this.ns[i].textContent = String(v);
    });
  },
});