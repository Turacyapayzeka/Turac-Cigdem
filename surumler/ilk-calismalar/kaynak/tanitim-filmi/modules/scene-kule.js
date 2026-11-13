const { seg, eo, eio, eob, lerp } = kit;
const KL = { px: 700, py: 350, R1: 640, R2: 200, t0: .3, t1: 4, ts: 4, th: 4.1 };
const klDrone = t => { const p = seg(t, KL.t0, KL.t1); return { x: lerp(1900, 900, p), y: lerp(250, 320, p) + Math.sin(t * 2.1) * 5, s: lerp(.5, 1, p) }; };
KL.td = KL.t0 + (1900 - 1338) / 1000 * (KL.t1 - KL.t0);
const klFall = (h, u) => [h.x + 110 * u, h.y + 400 * u * u];
const klLeg = (y, side) => side ? 600 + (1080 - y) * 76 / 610 : 800 - (1080 - y) * 76 / 610;
kit.scene('kule', {
  init(kit) {
    let zz = 'M' + klLeg(1040, 1) + ' 1040';
    [960, 880, 800, 720, 640, 560, 490].forEach((y, i) => { zz += ' L' + klLeg(y, i % 2 === 0 ? 0 : 1).toFixed(1) + ' ' + y; });
    const lab = (txt, r) => '<div class="words" style="left:' + (KL.px + r * Math.cos(.35) + 14).toFixed(0) + 'px;top:' + (KL.py + r * Math.sin(.35) - 6).toFixed(0) + 'px"><p class="tag kule-lab">' + txt + '</p></div>';
    kit.stage.append(kit.h('<div class="ground">' +
      '<svg class="art" viewBox="0 0 1920 1080">' +
      '<rect class="sky" width="1920" height="1080"/>' +
      '<path class="hill3 kule-h" d="' + DK.hills(720, 40, 3.1) + '"/>' +
      '<path class="hill2 kule-h" d="' + DK.hills(840, 30, 1.4, 3, 7) + '"/>' +
      '<circle class="ring kule-r1" cx="' + KL.px + '" cy="' + KL.py + '"/>' +
      '<circle class="hud kule-r2" style="stroke-dasharray:10 8" cx="' + KL.px + '" cy="' + KL.py + '"/>' +
      '<rect class="hill1" x="1040" y="880" width="260" height="200"/><rect class="hill1" x="1320" y="820" width="170" height="260"/>' +
      '<rect class="hill1" x="1510" y="900" width="340" height="180"/><rect class="glass" x="1350" y="850" width="110" height="14"/>' +
      '<rect class="road" y="1000" width="1920" height="80"/>' +
      '<path class="trim" d="M600 1080 L676 470 L692 470 L626 1080 Z M800 1080 L724 470 L708 470 L774 1080 Z"/>' +
      '<path class="seam" style="stroke-width:6" d="' + zz + '"/>' +
      '<rect class="trim" x="630" y="448" width="140" height="24" rx="3"/>' +
      '<g transform="translate(700,450)">' + DK.turret() + '</g>' +
      '<g class="kule-smk">' + '<circle class="smoke"/>'.repeat(5) + '</g>' +
      '<g class="kule-dr">' + DK.drone() + '</g>' +
      '<path class="hud kule-br"/><circle class="hot kule-boom"/><line class="tracer kule-tc"/></svg>' +
      lab('600–800 m · TESPİT', KL.R1) + lab('150 m', KL.R2) +
      '<div class="words" style="left:120px;top:120px;width:440px"><p class="tag">KULEDE</p><h2 class="line">Kalıcı kalkan</h2><p class="en">A permanent shield</p>' +
      '<p class="sub">Kritik tesisler için sabit kurulum</p><p class="en">Fixed installation for critical facilities</p></div></div>'));
    const q = s => kit.stage.querySelector(s);
    this.hs = [...kit.stage.querySelectorAll('.kule-h')];
    this.labs = [...kit.stage.querySelectorAll('.kule-lab')].map(e => e.style);
    for (const k of ['r1', 'r2', 'smk', 'dr', 'br', 'boom', 'tc']) this[k] = q('.kule-' + k);
    this.pr = q('.dk-pr');
    this.puffs = [...this.smk.children];
  },
  render(t) {
    this.hs.forEach((h, i) => h.setAttribute('transform', 'translate(' + (-t * (5 + i * 8)) + ',0)'));
    const g1 = eob(seg(t, .1, 1.3), 1.3), g2 = eob(seg(t, .5, 1.5), 1.3);
    this.r1.setAttribute('r', (KL.R1 * g1 * (1 + Math.sin(t * 2) * .004)).toFixed(1));
    this.r2.setAttribute('r', (KL.R2 * g2).toFixed(1));
    this.r1.style.strokeDashoffset = (-t * 30).toFixed(1);
    this.labs[0].opacity = eo(seg(t, 1.1, 1.5)); this.labs[1].opacity = eo(seg(t, 1.4, 1.8));
    const h = klDrone(KL.th), alive = t < KL.th, u = t - KL.th, f = klFall(h, Math.max(0, u));
    const D = alive ? klDrone(t) : { x: f[0], y: f[1], s: h.s };
    this.dr.setAttribute('transform', 'translate(' + D.x.toFixed(1) + ',' + D.y.toFixed(1) + ') rotate(' + (alive ? -6 : -6 + u * 240).toFixed(1) + ') scale(' + D.s.toFixed(3) + ')');
    const scan = -14 + Math.sin(t * 1.5) * 6, track = DK.aim(KL.px, KL.py, alive ? D.x : h.x, alive ? D.y : h.y);
    const a = lerp(lerp(scan, track, eio(seg(t, KL.td, KL.td + .6))), -12, eio(seg(t, 4.4, 5)));
    this.pr.setAttribute('transform', 'rotate(' + a.toFixed(2) + ')');
    const k = 46 * D.s + 16, hh = k * lerp(1.7, 1, eo(seg(t, KL.td, KL.td + .6))), c = hh * .4;
    this.br.setAttribute('d', ['M', -hh, -hh + c, 'L', -hh, -hh, 'L', -hh + c, -hh, 'M', hh - c, -hh, 'L', hh, -hh, 'L', hh, -hh + c, 'M', hh, hh - c, 'L', hh, hh, 'L', hh - c, hh, 'M', -hh + c, hh, 'L', -hh, hh, 'L', -hh, hh - c].join(' '));
    this.br.setAttribute('transform', 'translate(' + (alive ? D.x : h.x).toFixed(1) + ',' + (alive ? D.y : h.y).toFixed(1) + ')');
    this.br.style.opacity = eo(seg(t, KL.td, KL.td + .25)) * (1 - seg(t, KL.th + .2, KL.th + .5));
    const m = DK.muzzle(KL.px, KL.py, a, 1);
    this.tc.setAttribute('x1', m[0].toFixed(1)); this.tc.setAttribute('y1', m[1].toFixed(1));
    this.tc.setAttribute('x2', h.x.toFixed(1)); this.tc.setAttribute('y2', h.y.toFixed(1));
    this.tc.style.opacity = t >= KL.ts && t < KL.ts + .14 ? 1 : 0;
    const b = seg(t, KL.th, KL.th + .35);
    this.boom.setAttribute('cx', h.x); this.boom.setAttribute('cy', h.y); this.boom.setAttribute('r', (60 * eo(b)).toFixed(1));
    this.boom.style.opacity = b > 0 && b < 1 ? 1 - b : 0;
    this.puffs.forEach((cc, i) => {
      const ti = KL.th + i * .16, v = t - ti, ff = klFall(h, Math.max(0, ti - KL.th));
      cc.setAttribute('cx', ff[0].toFixed(1)); cc.setAttribute('cy', (ff[1] - v * 20).toFixed(1)); cc.setAttribute('r', (12 + Math.max(0, v) * 34).toFixed(1));
      cc.style.opacity = v > 0 ? .7 * (1 - seg(v, 0, 1.4)) : 0;
    });
  },
});