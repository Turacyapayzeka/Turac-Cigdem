const { seg, eo, eio, eob, lerp, TextFx } = kit;
// Katmanlı hava savunma: arazinin üstünde iç içe kubbeler (dıştan içe 5 → 1); en içteki kubbe Dron Kalkanı.
// Her katmanın bandında solda tehditler, sağda çözümler. Ölçeksiz şema; yalnızca Dron Kalkanı'nın değerleri yazılı.
const CX = 960, BASE = 905;
const DM = [[860, 600], [705, 490], [550, 380], [395, 270], [235, 160]];   // yatay ve dikey yarıçap, dıştan içe
const LY = [
  { n: 5, sol: 'Uzun menzil hava savunma', solEn: 'Long-range air defense', thr: 'Uçak, seyir füzesi', thrEn: 'Aircraft, cruise missiles' },
  { n: 4, sol: 'Orta menzil hava savunma', solEn: 'Medium-range air defense', thr: 'Uçak, helikopter, büyük İHA', thrEn: 'Aircraft, helicopters, large UAVs' },
  { n: 3, sol: 'Kısa menzil hava savunma', solEn: 'Short-range air defense', thr: 'Alçak uçan hedefler, İHA', thrEn: 'Low-flying targets, UAVs' },
  { n: 2, sol: 'Elektronik harp · karıştırıcı', solEn: 'Electronic warfare · jamming', thr: 'Telsizle yönetilen dronlar', thrEn: 'Radio-controlled drones' },
  { n: 1, sol: 'Dron Kalkanı', solEn: '600–800 m tespit · 150 m angajman', thr: 'FPV, fiber optik ve otonom dronlar', thrEn: 'FPV, fiber-optic and autonomous drones', us: 1 },
];
// Etiket bandı: kubbenin tepesiyle bir içteki kubbenin tepesi arası; en içte kubbenin içi
const labelY = i => BASE - DM[i][1] + (i < 4 ? 16 : 34);
const SH = 'text-shadow:0 0 14px var(--ground),0 0 4px var(--ground)';
kit.scene('katman', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><div class="grid"></div></div>'));
    const svg = kit.svgLayer();
    const grad = (id, col, a0, a1) => '<linearGradient id="' + id + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:' + col + ';stop-opacity:' + a0 + '"/><stop offset="1" style="stop-color:' + col + ';stop-opacity:' + a1 + '"/></linearGradient>';
    const dome = (i, l) => {
      const [rx, ry] = DM[i], col = l.us ? 'var(--accent)' : 'var(--main)';
      return '<g class="katman-d" style="transform-origin:' + CX + 'px ' + BASE + 'px">' +
        '<path style="fill:url(#' + (l.us ? 'kd-us' : 'kd') + ');stroke:' + col + ';stroke-width:' + (l.us ? 3 : 2) + ';stroke-opacity:' + (l.us ? 1 : .75) + '" d="M' + (CX - rx) + ' ' + BASE + ' A' + rx + ' ' + ry + ' 0 0 1 ' + (CX + rx) + ' ' + BASE + ' Z"/>' +
        '<ellipse cx="' + CX + '" cy="' + BASE + '" rx="' + rx + '" ry="' + (ry * .08).toFixed(1) + '" style="fill:none;stroke:' + col + ';stroke-width:1.5;stroke-opacity:.45"/></g>';
    };
    // Arazi: ufuk çizgisinin altında koyulaşan zemin
    svg.innerHTML = '<defs>' + grad('kd', 'var(--main)', .2, .04) + grad('kd-us', 'var(--accent)', .42, .1) + grad('kg', 'var(--main)', .14, 0) + '</defs>' +
      '<rect x="0" y="' + BASE + '" width="1920" height="' + (1080 - BASE) + '" style="fill:url(#kg)"/>' +
      '<path class="ink" style="stroke-width:1.5;opacity:.55" d="M60 ' + BASE + ' H1860"/>' +
      LY.map((l, i) => dome(i, l)).join('');
    this.ds = [...svg.querySelectorAll('.katman-d')].map(e => e.style);
    LY.forEach((l, i) => {
      const y = labelY(i), gap = l.us ? 78 : 40;
      kit.stage.append(kit.h('<div class="words katman-t" style="left:' + (CX - gap - 520) + 'px;top:' + y + 'px;width:520px;align-items:flex-end;text-align:right;gap:2px;' + SH + '">' +
        '<p style="font-family:var(--display, var(--sans, system-ui, sans-serif));font-weight:600;font-size:26px;line-height:1.1">' + l.thr + '</p><p class="en" style="margin:0;font-size:17px">' + l.thrEn + '</p></div>'));
      kit.stage.append(kit.h('<div class="words katman-s" style="left:' + (CX + gap) + 'px;top:' + (y - 12) + 'px;width:520px;gap:2px;' + SH + '">' +
        '<p class="firm" style="font-size:13px;color:' + (l.us ? 'var(--accent)' : 'var(--main)') + '">' + l.n + '. KATMAN · LAYER ' + l.n + '</p>' +
        '<p style="font-family:var(--display, var(--sans, system-ui, sans-serif));font-weight:' + (l.us ? 700 : 600) + ';font-size:' + (l.us ? 32 : 26) + 'px;line-height:1.1">' + l.sol + '</p><p class="en" style="margin:0;font-size:17px' + (l.us ? ';color:var(--second)' : '') + '">' + l.solEn + '</p></div>'));
    });
    kit.stage.append(kit.h('<div class="katman-logo" style="position:absolute;left:' + (CX - 60) + 'px;top:' + (BASE - DM[4][1] + 18) + 'px;transform-origin:60px 84px">' + DK.dkLogo(120) + '</div>'));
    kit.stage.append(kit.h('<div class="words" style="left:120px;top:70px;width:1100px"><p class="tag katman-tag">KATMANLI SAVUNMA</p>' +
      '<h2 class="line" style="font-size:60px">Karıştırıcının bittiği yerde</h2><p class="en katman-en">Where jamming ends, the last layer begins</p></div>'));
    kit.stage.append(kit.h('<div class="words katman-h" style="left:120px;top:960px;width:1680px;flex-direction:row;justify-content:space-between"><p class="firm">← TEHDİTLER · THREATS</p><p class="firm">ÇÖZÜMLER · SOLUTIONS →</p></div>'));
    kit.stage.append(kit.h('<div class="words" style="left:1500px;top:1030px;width:300px;align-items:flex-end"><p class="firm katman-n" style="font-size:13px;opacity:.8">ÖLÇEKSİZ ŞEMA · NOT TO SCALE</p></div>'));
    this.ts = [...kit.stage.querySelectorAll('.katman-t')].map(e => e.style);
    this.ss = [...kit.stage.querySelectorAll('.katman-s')].map(e => e.style);
    this.logo = kit.stage.querySelector('.katman-logo').style;
    this.h = kit.stage.querySelector('.katman-h').style;
    this.n = kit.stage.querySelector('.katman-n').style;
    this.tag = kit.stage.querySelector('.katman-tag').style;
    this.en = kit.stage.querySelector('.katman-en').style;
    this.line = kit.stage.querySelector('.line');
  },
  render(t) {
    this.tag.opacity = eo(seg(t, 0, .4));
    TextFx.fadeFromRight(this.line, t, .1);
    this.en.opacity = eo(seg(t, .7, 1.2));
    this.h.opacity = eo(seg(t, .6, 1));
    // Kubbe kubbe: dıştan içe, her biri 1,4 saniyede bir yerden yükselir; tehdit soldan, çözüm sağdan gelir
    LY.forEach((l, i) => {
      const a = 1 + i * 1.4, p = eob(seg(t, a, a + .7), 1.3), q = eo(seg(t, a + .35, a + .85));
      this.ds[i].opacity = eo(seg(t, a, a + .3));
      this.ds[i].transform = 'scale(' + lerp(.92, 1, p).toFixed(3) + ',' + lerp(0, 1, p).toFixed(3) + ')';
      this.ts[i].opacity = q; this.ts[i].transform = 'translateX(' + lerp(-30, 0, q).toFixed(1) + 'px)';
      this.ss[i].opacity = q; this.ss[i].transform = 'translateX(' + lerp(30, 0, q).toFixed(1) + 'px)';
    });
    const lp = seg(t, 1 + 4 * 1.4 + .4, 1 + 4 * 1.4 + 1.2);
    this.logo.opacity = eo(seg(t, 1 + 4 * 1.4 + .4, 1 + 4 * 1.4 + .6));
    this.logo.transform = 'scale(' + (lerp(.2, 1, eob(lp, 1.7)) * (1 + .015 * Math.sin(t * 2.4))).toFixed(4) + ')';
    this.n.opacity = eo(seg(t, 3, 3.5));
  },
});
