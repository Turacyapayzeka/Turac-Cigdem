const { seg, eo, eio, lerp } = kit;
const GM = { BX: 360, BY: 866, t0: .2, t1: 3.4, td: 1, ts: 3.4, th: 3.52, sea: 884 };
const gmDrone = t => { const p = seg(t, GM.t0, GM.t1); return { x: lerp(1860, 1290, p), y: lerp(150, 300, p) + Math.sin(t * 2.3) * 5, s: lerp(.4, 1, p) }; };
const gmFall = (h, u) => [h.x + 120 * u, h.y + 400 * u * u];
const GM_HULL = '<path class="body" d="M0 -90 L700 -90 L790 -132 L724 -18 L70 6 L0 -34 Z"/>' +
  '<path class="seam" style="stroke-width:6" d="M30 -46 L740 -60"/>' +
  '<path class="camo1" d="M196 -90 L226 -204 L424 -204 L474 -90 Z"/>' +
  [240, 286, 332, 378].map(x => '<rect class="glass" x="' + x + '" y="-190" width="34" height="26" rx="3"/>').join('') +
  '<rect class="trim" x="318" y="-290" width="8" height="88"/><rect class="trim" x="286" y="-290" width="72" height="9" rx="3"/>' +
  '<rect class="sand2" x="586" y="-152" width="28" height="64"/>' +
  '<g transform="translate(600,-150) scale(.6)">' + DK.turret() + '</g>';
kit.scene('gemi', {
  init(kit) {
    const wave = (y, a, s, cls) => '<path class="' + cls + ' gemi-w" style="stroke:var(--main);stroke-width:2;stroke-opacity:.35" d="' + DK.hills(y, a, s, 8, 13) + '"/>';
    kit.stage.append(kit.h('<div class="ground">' +
      '<svg class="art" viewBox="0 0 1920 1080">' +
      '<rect class="sky" width="1920" height="1080"/>' +
      '<path class="hill3 gemi-c" d="' + DK.hills(800, 18, 1.2, 2, 5) + '"/>' +
      wave(850, 5, 0.3, 'sea') +
      '<g class="gemi-smk">' + '<circle class="smoke"/>'.repeat(5) + '</g>' +
      '<g class="gemi-dr">' + DK.drone() + '</g>' +
      '<path class="hud gemi-br"/><circle class="hot gemi-boom"/><line class="tracer gemi-tc"/>' +
      '<g class="gemi-b">' + GM_HULL + '</g>' +
      '<ellipse class="seam gemi-spl" style="stroke:var(--second);stroke-width:4"/>' +
      wave(884, 9, 2.1, 'sea') + wave(950, 12, 4.4, 'sea') +
      '</svg>' +
      '<div class="words" style="left:120px;top:110px;width:900px"><p class="tag">GEMİDE</p><h2 class="line">Denizde de hedefte</h2><p class="en">On target at sea, too</p></div></div>'));
    const q = s => kit.stage.querySelector(s);
    this.ws = [...kit.stage.querySelectorAll('.gemi-w')];
    for (const k of ['smk', 'dr', 'br', 'boom', 'tc', 'b', 'spl', 'c']) this[k] = q('.gemi-' + k);
    this.pr = q('.gemi-b .dk-pr');
    this.puffs = [...this.smk.children];
  },
  render(t) {
    this.ws.forEach((w, i) => w.setAttribute('transform', 'translate(' + (-((t * (40 + i * 50) + i * 300) % 1920)).toFixed(1) + ',0)'));
    this.c.setAttribute('transform', 'translate(' + (-t * 6) + ',0)');
    // Tekne sallanır; taret bunu dengeleyip hedefte kalır
    const r = Math.sin(t * 1.5) * 3.2, bob = Math.sin(t * 1.5 + .8) * 8, rr = r * Math.PI / 180;
    this.b.setAttribute('transform', 'translate(' + GM.BX + ',' + (GM.BY + bob).toFixed(1) + ') rotate(' + r.toFixed(2) + ',390,-60)');
    const lx = 210, ly = -150;
    const px = GM.BX + 390 + lx * Math.cos(rr) - ly * Math.sin(rr), py = GM.BY + bob - 60 + lx * Math.sin(rr) + ly * Math.cos(rr);
    const h = gmDrone(GM.th), alive = t < GM.th, u = t - GM.th, f = gmFall(h, Math.max(0, u));
    const D = alive ? gmDrone(t) : { x: f[0], y: f[1], s: h.s };
    this.dr.setAttribute('transform', 'translate(' + D.x.toFixed(1) + ',' + D.y.toFixed(1) + ') rotate(' + (alive ? -6 : -6 + u * 240).toFixed(1) + ') scale(' + D.s.toFixed(3) + ')');
    this.dr.style.opacity = D.y < GM.sea ? 1 : 0;
    const scan = -10 + Math.sin(t * 1.3) * 4, track = DK.aim(px, py, alive ? D.x : h.x, alive ? D.y : h.y);
    const aw = lerp(lerp(scan, track, eio(seg(t, GM.td, GM.td + .6))), -10, eio(seg(t, 4, 4.8)));
    this.pr.setAttribute('transform', 'rotate(' + (aw - r).toFixed(2) + ')');
    const k = 46 * D.s + 16, hh = k * lerp(1.7, 1, eo(seg(t, GM.td, GM.td + .6))), c = hh * .4;
    this.br.setAttribute('d', ['M', -hh, -hh + c, 'L', -hh, -hh, 'L', -hh + c, -hh, 'M', hh - c, -hh, 'L', hh, -hh, 'L', hh, -hh + c, 'M', hh, hh - c, 'L', hh, hh, 'L', hh - c, hh, 'M', -hh + c, hh, 'L', -hh, hh, 'L', -hh, hh - c].join(' '));
    this.br.setAttribute('transform', 'translate(' + (alive ? D.x : h.x).toFixed(1) + ',' + (alive ? D.y : h.y).toFixed(1) + ')');
    this.br.style.opacity = eo(seg(t, GM.td, GM.td + .25)) * (1 - seg(t, GM.th + .2, GM.th + .5));
    const m = DK.muzzle(px, py, aw, .6);
    this.tc.setAttribute('x1', m[0].toFixed(1)); this.tc.setAttribute('y1', m[1].toFixed(1));
    this.tc.setAttribute('x2', h.x.toFixed(1)); this.tc.setAttribute('y2', h.y.toFixed(1));
    this.tc.style.opacity = t >= GM.ts && t < GM.ts + .14 ? 1 : 0;
    const b = seg(t, GM.th, GM.th + .35);
    this.boom.setAttribute('cx', h.x); this.boom.setAttribute('cy', h.y); this.boom.setAttribute('r', (60 * eo(b)).toFixed(1));
    this.boom.style.opacity = b > 0 && b < 1 ? 1 - b : 0;
    this.puffs.forEach((cc, i) => {
      const ti = GM.th + i * .18, v = t - ti, ff = gmFall(h, Math.max(0, ti - GM.th));
      cc.setAttribute('cx', ff[0].toFixed(1)); cc.setAttribute('cy', (ff[1] - v * 20).toFixed(1)); cc.setAttribute('r', (12 + Math.max(0, v) * 34).toFixed(1));
      cc.style.opacity = v > 0 && ff[1] < GM.sea ? .7 * (1 - seg(v, 0, 1.4)) : 0;
    });
    // Denize düşüş halkası
    const tw = GM.th + Math.sqrt((GM.sea - h.y) / 400), sp = seg(t, tw, tw + .7);
    this.spl.setAttribute('cx', gmFall(h, tw - GM.th)[0].toFixed(1)); this.spl.setAttribute('cy', GM.sea);
    this.spl.setAttribute('rx', (10 + 90 * eo(sp)).toFixed(1)); this.spl.setAttribute('ry', (4 + 16 * eo(sp)).toFixed(1));
    this.spl.style.opacity = sp > 0 && sp < 1 ? 1 - sp : 0;
  },
});