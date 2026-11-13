window.DK = (() => {
  // Çağrı çizgisi: noktadan dirsekle etikete; init'te uzunluğu ölçülür, render'da çizilerek gelir
  const leader = (x, y, lx, ly) => 'M' + x + ' ' + y + ' L' + (lx + (lx > x ? -40 : 40)) + ' ' + ly + ' L' + lx + ' ' + ly;
  const callouts = (kit, list) => {
    const svg = kit.svgLayer();
    svg.innerHTML = list.map(c => '<path class="ink" d="' + leader(c.x, c.y, c.lx, c.ly) + '"/><circle class="dot" r="9" cx="' + c.x + '" cy="' + c.y + '"/>').join('');
    const paths = [...svg.querySelectorAll('path')], dots = [...svg.querySelectorAll('circle')];
    const labs = list.map(c => {
      const el = kit.h('<div class="lab" style="left:' + (c.lx > c.x ? c.lx : c.lx - 0) + 'px;top:' + (c.ly - 26) + 'px' + (c.lx > c.x ? '' : ';transform-origin:100% 0') + '"><p class="firm">' + c.firm + '</p><b>' + c.tr + '</b><p class="en">' + c.en + '</p></div>');
      kit.stage.append(el);
      if (c.lx <= c.x) el.style.left = (c.lx - el.offsetWidth) + 'px';
      return el.style;
    });
    const lens = paths.map(p => p.getTotalLength());
    paths.forEach((p, i) => { p.style.strokeDasharray = lens[i]; });
    return { svg, paths, dots, labs, lens, list };
  };
  // a: başlangıç saniyesi, st: aralık; out: çıkış başlangıcı
  const drawCallouts = (C, t, a, st, kit, out) => {
    const { seg, eo } = kit;
    C.list.forEach((c, i) => {
      const t0 = a + i * st, pd = eo(seg(t, t0, t0 + .5)), pl = eo(seg(t, t0 + .35, t0 + .75));
      const fade = out ? 1 - eo(seg(t, out, out + .4)) : 1;
      C.paths[i].style.strokeDashoffset = (C.lens[i] * (1 - pd)).toFixed(1);
      C.paths[i].style.opacity = fade;
      C.dots[i].style.opacity = Math.min(1, pd * 3) * fade;
      C.labs[i].opacity = pl * fade;
      C.labs[i].transform = 'translateX(' + ((1 - pl) * (c.lx > c.x ? 18 : -18)).toFixed(1) + 'px)';
    });
  };
  // Teknik çerçeve köşeleri
  const corners = (x, y, w, h, l) => ['M' + x + ' ' + (y + l) + ' V' + y + ' H' + (x + l), 'M' + (x + w - l) + ' ' + y + ' H' + (x + w) + ' V' + (y + l), 'M' + (x + w) + ' ' + (y + h - l) + ' V' + (y + h) + ' H' + (x + w - l), 'M' + (x + l) + ' ' + (y + h) + ' H' + x + ' V' + (y + h - l)].join(' ');
  // Dron Kalkanı logosu (gönderilen logodan vektör)
  const prop = (cx, cy, a) => {
    const R = 115, g = 20, p = d => [cx + R * Math.cos(d * Math.PI / 180), cy + R * Math.sin(d * Math.PI / 180)].map(v => v.toFixed(1)).join(' ');
    const arc = (a0, a1) => 'M' + p(a0) + ' A' + R + ' ' + R + ' 0 0 1 ' + p(a1);
    const blade = 'M34 -5 C58 -28 96 -24 106 -10 C110 -3 106 5 97 7 C72 11 52 9 34 6 Z';
    return '<path class="dkl-ring" d="' + arc(a + g, a + 180 - g) + ' ' + arc(a + 180 + g, a + 360 - g) + '"/>' +
      '<path class="dkl-f" transform="translate(' + cx + ',' + cy + ') rotate(' + a + ')" d="' + blade + '"/>' +
      '<path class="dkl-f" transform="translate(' + cx + ',' + cy + ') rotate(' + (a + 180) + ')" d="' + blade + '"/>' +
      '<circle class="dkl-f" cx="' + cx + '" cy="' + cy + '" r="33"/><circle class="dkl-in" cx="' + cx + '" cy="' + cy + '" r="7"/>';
  };
  const dkTop = prop(325, 330, -45) + prop(775, 330, 45) +
    '<path class="dkl-f" d="M372 345 C450 395 500 425 550 438 C600 425 650 395 728 345 C745 352 758 365 762 378 C735 415 718 440 705 465 L398 465 C385 440 368 415 340 378 C344 365 355 352 372 345 Z"/>';
  const dkLogo = w => '<div style="position:relative;width:' + w + 'px;height:' + (w * .704).toFixed(1) + 'px">' +
    '<svg viewBox="60 190 980 690" style="position:absolute;inset:0;width:100%;height:100%;overflow:visible">' + dkTop +
    '<g transform="translate(0,1064) scale(1,-1)">' + dkTop + '</g></svg>' +
    '<p class="dkl-t" style="position:absolute;left:-3%;right:-3%;top:' + (w * .287).toFixed(1) + 'px;font-size:' + (w * .125).toFixed(1) + 'px">DRON KALKANI</p></div>';
  // Turaç logosu
  const trcLogo = w => '<div style="position:relative;width:' + w + 'px;height:' + w + 'px">' +
    '<svg viewBox="0 0 500 500" style="position:absolute;inset:0;width:100%;height:100%">' +
    '<circle class="trc-k" cx="250" cy="250" r="249"/><circle class="dkl-f" cx="250" cy="250" r="234"/><circle class="trc-k" cx="250" cy="250" r="224"/>' +
    '<circle class="trc-r" cx="250" cy="250" r="207"/>' +
    '<polygon class="dkl-f" points="250,60 390,130 250,200 110,130"/><polygon class="hot" points="250,72 366,130 250,188 134,130"/><polygon class="trc-k" points="250,82 346,130 250,178 154,130"/>' +
    '<path class="dkl-f" d="M196 134 C212 120 240 114 262 119 L298 116 C308 114 318 118 322 124 L306 127 C296 129 285 133 277 139 C262 151 236 157 212 151 C224 147 234 141 238 135 C226 138 210 139 196 134 Z"/></svg>' +
    '<div style="position:absolute;left:0;right:0;top:' + (w * .41).toFixed(1) + 'px;display:flex;flex-direction:column;align-items:center;gap:' + (w * .025).toFixed(1) + 'px">' +
    '<p class="trc-name" style="font-size:' + (w * .19).toFixed(1) + 'px">TURAÇ</p>' +
    '<p class="trc-s" style="font-size:' + (w * .05).toFixed(1) + 'px">DIŞ TİCARET LTD. ŞTİ.</p>' +
    '<p class="trc-s" style="font-size:' + (w * .06).toFixed(1) + 'px;margin-top:' + (w * .07).toFixed(1) + 'px">1987’den Beri...</p></div></div>';
  // Sayan sayı: değerin yarısından başlar
  const count = (t, a, b, v) => { const { seg, eo } = window.kit || {}; return v; };
  return { callouts, drawCallouts, corners, dkLogo, trcLogo };
})();