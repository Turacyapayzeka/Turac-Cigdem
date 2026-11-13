const { seg, eo, eio, lerp } = kit;
const AR = { S: .95, TX: 170, TY: 944, t0: .6, t1: 5.2, ts: 5.2, th: 5.32 };
AR.td = AR.t0 + (400 / 850) * (AR.t1 - AR.t0);
const arDrone = t => { const p = seg(t, AR.t0, AR.t1); return { p, x: lerp(1880, 1390, p), y: lerp(170, 330, p) + Math.sin(t * 2.2) * 5, s: lerp(.38, 1, p), d: lerp(1000, 150, p) }; };
const arFall = (h, u) => [h.x + 140 * u, h.y + 350 * u * u];
kit.scene('arac', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground">' +
      '<svg class="art" viewBox="0 0 1920 1080">' +
      '<rect class="sky" width="1920" height="1080"/>' +
      '<path class="hill3 arac-h" d="' + DK.hills(600, 50, 2.2) + '"/>' +
      '<path class="hill2 arac-h" d="' + DK.hills(720, 45, 0.4, 3, 7) + '"/>' +
      '<path class="hill1 arac-h" d="' + DK.hills(850, 25, 5, 4, 9) + '"/>' +
      '<rect class="road" y="905" width="1920" height="180"/>' +
      '<path class="seam arac-dash" style="stroke-width:8;stroke-dasharray:70 60" d="M0 1020 L1920 1020"/>' +
      '<g class="arac-smk">' + '<circle class="smoke"/>'.repeat(6) + '</g>' +
      '<g class="arac-dr">' + DK.drone() + '</g>' +
      '<path class="hud arac-br"/><circle class="hot arac-boom"/>' +
      '<line class="tracer arac-tc"/>' +
      '<g class="arac-tr">' + DK.truck('arac-camo') + '</g></svg>' +
      '<div class="words" style="left:120px;top:110px;width:900px"><p class="tag">ARAÇTA</p><h2 class="line">Hareket halinde koruma</h2><p class="en">Protection on the move</p></div>' +
      '<div class="words" style="left:1440px;top:640px;width:420px;gap:10px"><p class="tag">MENZİL</p><p class="num arac-num">1000 m</p><p class="chip arac-chip">TESPİT</p></div></div>'));
    const q = s => kit.stage.querySelector(s);
    this.hs = [...kit.stage.querySelectorAll('.arac-h')];
    this.wh = [...kit.stage.querySelectorAll('.arac-tr .dk-wh')];
    for (const k of ['dash', 'smk', 'dr', 'br', 'boom', 'tc', 'tr', 'num', 'chip']) this[k] = q('.arac-' + k);
    this.pr = q('.arac-tr .dk-pr');
    this.puffs = [...this.smk.children];
  },
  render(t) {
    [25, 70, 160].forEach((v, i) => this.hs[i].setAttribute('transform', 'translate(' + (-((t * v) % 1920)) + ',0)'));
    this.dash.style.strokeDashoffset = (t * 900).toFixed(1);
    this.wh.forEach(w => w.setAttribute('transform', 'rotate(' + (t * 420).toFixed(1) + ')'));
    const ty = AR.TY + Math.sin(t * 9) * 1.5;
    this.tr.setAttribute('transform', 'translate(' + AR.TX + ',' + ty.toFixed(1) + ') scale(' + AR.S + ')');
    const px = AR.TX + DK.TPIV[0] * AR.S, py = ty + DK.TPIV[1] * AR.S;
    const h = arDrone(AR.th), alive = t < AR.th, u = t - AR.th;
    const D = alive ? arDrone(t) : { x: arFall(h, u)[0], y: arFall(h, u)[1], s: h.s, d: h.d };
    this.dr.setAttribute('transform', 'translate(' + D.x.toFixed(1) + ',' + D.y.toFixed(1) + ') rotate(' + (alive ? -6 : -6 + u * 220).toFixed(1) + ') scale(' + D.s.toFixed(3) + ')');
    // Taret: tarama → tespitte hedefe dönüş → takip → vuruştan sonra dinlenme
    const scan = -8 + Math.sin(t * 1.4) * 5, track = DK.aim(px, py, alive ? D.x : h.x, alive ? D.y : h.y);
    const a = lerp(lerp(scan, track, eio(seg(t, AR.td, AR.td + .6))), -12, eio(seg(t, 5.9, 6.7)));
    this.pr.setAttribute('transform', 'rotate(' + a.toFixed(2) + ')');
    // Hedef çerçevesi kilitte daralır
    const k = 46 * D.s + 16, hh = k * lerp(1.7, 1, eo(seg(t, AR.td, AR.td + .6))), c = hh * .4;
    this.br.setAttribute('d', ['M', -hh, -hh + c, 'L', -hh, -hh, 'L', -hh + c, -hh, 'M', hh - c, -hh, 'L', hh, -hh, 'L', hh, -hh + c, 'M', hh, hh - c, 'L', hh, hh, 'L', hh - c, hh, 'M', -hh + c, hh, 'L', -hh, hh, 'L', -hh, hh - c].join(' '));
    this.br.setAttribute('transform', 'translate(' + (alive ? D.x : h.x).toFixed(1) + ',' + (alive ? D.y : h.y).toFixed(1) + ')');
    this.br.style.opacity = eo(seg(t, AR.td, AR.td + .25)) * (1 - seg(t, AR.th + .2, AR.th + .5));
    const m = DK.muzzle(px, py, a, DK.TSC * AR.S), on = t >= AR.ts && t < AR.ts + .14;
    this.tc.setAttribute('x1', m[0].toFixed(1)); this.tc.setAttribute('y1', m[1].toFixed(1));
    this.tc.setAttribute('x2', h.x.toFixed(1)); this.tc.setAttribute('y2', h.y.toFixed(1));
    this.tc.style.opacity = on ? 1 : 0;
    const b = seg(t, AR.th, AR.th + .35);
    this.boom.setAttribute('cx', h.x); this.boom.setAttribute('cy', h.y); this.boom.setAttribute('r', (60 * eo(b)).toFixed(1));
    this.boom.style.opacity = b > 0 && b < 1 ? 1 - b : 0;
    this.puffs.forEach((c, i) => {
      const ti = AR.th + i * .18, v = t - ti, f = arFall(h, Math.max(0, ti - AR.th));
      c.setAttribute('cx', f[0].toFixed(1)); c.setAttribute('cy', (f[1] - v * 20).toFixed(1)); c.setAttribute('r', (12 + Math.max(0, v) * 34).toFixed(1));
      c.style.opacity = v > 0 ? .7 * (1 - seg(v, 0, 1.4)) : 0;
    });
    this.num.textContent = Math.round(alive ? D.d : h.d) + ' m';
    const st = t < AR.td + .6 ? 'TESPİT' : t < AR.ts - .5 ? 'KİLİTLENDİ' : t < AR.th ? 'ANGAJMAN' : 'ETKİSİZ';
    if (this.chip.textContent !== st) this.chip.textContent = st;
    const sw = [AR.td + .6, AR.ts - .5, AR.th].reduce((m2, s) => Math.min(m2, Math.abs(t - s)), 9);
    this.chip.style.opacity = eo(seg(t, AR.td, AR.td + .25)) * Math.min(1, sw / .12);
  },
});