const { seg, eo, eob, lerp, TextFx } = kit;
const NS = [
  { k: '1 · TESPİT', v: '600–800 m', d: 'Pasif elektro-optik ve akustik sensörler dronu uzaktan fark eder.',
    e: 'Detect: passive electro-optical and acoustic sensors spot the drone from afar.',
    ico: '<path d="M10 60 Q60 8 110 60 Q60 112 10 60 Z"/><circle cx="60" cy="60" r="22"/><circle cx="60" cy="60" r="6"/>' },
  { k: '2 · TAKİP', v: 'Otonom', d: 'Yapay zekâ hedefe kilitlenir; işlem kule üzerindeki gömülü işlemcide yapılır.',
    e: 'Track: AI locks on; processing runs on embedded computers on the turret.',
    ico: '<circle cx="60" cy="60" r="40"/><path d="M60 6 L60 36 M60 84 L60 114 M6 60 L36 60 M84 60 L114 60"/><circle cx="60" cy="60" r="6"/>' },
  { k: '3 · ANGAJMAN', v: '150 m', d: 'Çift 12 kalibre tüfek, Sterling magnum anti-drone mühimmatla ateşler.',
    e: 'Engage: twin 12-gauge shotguns fire Sterling magnum anti-drone ammunition.',
    ico: '<path d="M10 84 L84 30 M22 104 L96 50"/><path d="M96 18 L104 8 M106 34 L118 30 M86 12 L84 0"/>' },
];
kit.scene('nasil', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground">' +
      '<svg class="art" viewBox="0 0 1920 1080"><rect class="sky" width="1920" height="1080"/>' +
      '<path class="hill3 nasil-h" d="' + DK.hills(960, 26, 4.4) + '"/>' +
      '<path class="hill2 nasil-h" d="' + DK.hills(1030, 18, 1.1, 3, 7) + '"/>' +
      '<line class="nasil-ln" x1="260" y1="470" x2="1420" y2="470" style="stroke:var(--main);stroke-width:3;stroke-dasharray:12 12"/></svg>' +
      '<div class="words" style="left:140px;top:100px;width:1660px"><p class="tag nasil-tag">NASIL ÇALIŞIR</p>' +
      '<h2 class="line">Tespit et. Takip et. Etkisiz kıl.</h2><p class="en" data-at="0.8">Detect. Track. Neutralize.</p></div>' +
      NS.map((s, i) => '<div class="words nasil-c" style="left:' + (140 + i * 580) + 'px;top:400px;width:480px;gap:16px">' +
        '<svg viewBox="0 0 120 120" style="width:140px;height:140px;background:var(--ground)"><g class="ico">' + s.ico + '</g></svg>' +
        '<p class="tag">' + s.k + '</p><p class="step-v">' + s.v + '</p><p class="card-txt">' + s.d + '</p><p class="en s">' + s.e + '</p></div>').join('') + '</div>'));
    const q = s => kit.stage.querySelector(s);
    this.hs = [...kit.stage.querySelectorAll('.nasil-h')];
    this.cs = [...kit.stage.querySelectorAll('.nasil-c')].map(e => e.style);
    this.ln = q('.nasil-ln').style;
    this.tag = q('.nasil-tag').style;
    this.line = q('.line');
    this.ens = [...kit.stage.querySelectorAll('.en')];
  },
  render(t) {
    DK.en(this.ens, t);
    this.hs.forEach((h, i) => h.setAttribute('transform', 'translate(' + (-t * (5 + i * 7)) + ',0)'));
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .1);
    // Adımlar sırayla gelir; kesik çizgi onları bağlar
    this.ln.transformOrigin = '260px 470px';
    this.ln.transform = 'scaleX(' + eo(seg(t, .9, 3.6)).toFixed(3) + ')';
    this.cs.forEach((c, i) => {
      const a = 0.9 + i * 1.2, p = seg(t, a, a + .55);
      c.opacity = eo(p);
      c.transform = 'translate(' + lerp(30, 0, eo(p)).toFixed(1) + 'px,' + (-t * 2).toFixed(1) + 'px) scale(' + lerp(.96, 1, eob(p, 1.6)).toFixed(3) + ')';
    });
  },
});