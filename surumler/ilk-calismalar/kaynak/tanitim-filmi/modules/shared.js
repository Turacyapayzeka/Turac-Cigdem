window.DK = (() => {
  const GUN = c => '<g class="' + c + '">' +
    '<rect x="-72" y="6" width="118" height="24" rx="3"/>' +
    '<rect x="44" y="10" width="84" height="16" rx="2"/>' +
    '<rect x="126" y="14" width="80" height="8"/>' +
    '<rect x="198" y="9" width="22" height="18" rx="2"/>' +
    '<path d="M-30 30 L-17 30 L-22 62 L-37 62 Z"/>' +
    '<path d="M4 30 L26 30 Q30 60 46 86 L24 96 Q10 66 4 30 Z"/>' +
    '<rect x="-44" y="0" width="44" height="8" rx="2"/></g>';
  const BOLTS = [-28, -14, 0, 14, 28].map(x => '<circle class="trim" cx="' + x + '" cy="-82" r="2.5"/>').join('');
  // Taret yandan: öndeki silah düz, arkadaki silah ters (şarjörü yukarıda)
  const turret = () => '<g>' +
    '<rect class="sand2" x="-34" y="-12" width="68" height="12" rx="3"/>' +
    '<rect class="sand" x="-22" y="-54" width="44" height="44"/>' +
    '<rect class="sand" x="-42" y="-94" width="84" height="44" rx="4"/>' +
    '<rect class="sand2" x="-42" y="-62" width="84" height="6"/>' + BOLTS +
    '<g transform="translate(0,-100)"><g class="dk-pr">' +
    '<g transform="translate(8,-6) scale(1,-1)">' + GUN('gun2') + '</g>' +
    '<rect class="sand2" x="-18" y="-14" width="36" height="30" rx="3"/>' +
    '<rect class="sand" x="-36" y="-68" width="80" height="56" rx="4"/>' +
    '<rect class="sand2" x="-36" y="-72" width="80" height="8" rx="2"/>' +
    '<rect class="lens" x="44" y="-60" width="10" height="40" rx="3"/>' +
    '<g transform="translate(0,10)">' + GUN('gun') + '</g>' +
    '</g></g></g>';
  const drone = () => '<g>' +
    '<ellipse class="rotor" cx="-40" cy="-30" rx="26" ry="5"/><ellipse class="rotor" cx="40" cy="-30" rx="26" ry="5"/>' +
    '<path class="dr-dark" d="M-60 -18 L-8 -3 L8 -3 L60 -18 L60 -11 L8 4 L-8 4 L-60 -11 Z"/>' +
    '<rect class="dr-dark" x="-64" y="-26" width="9" height="12" rx="2"/><rect class="dr-dark" x="55" y="-26" width="9" height="12" rx="2"/>' +
    '<path class="dr-body" d="M-28 -6 Q0 -24 28 -6 L23 10 Q0 17 -23 10 Z"/>' +
    '<circle class="dr-dark" cx="0" cy="14" r="7"/><rect class="hot" x="-6" y="18" width="12" height="18" rx="3"/>' +
    '<ellipse class="rotor" cx="-60" cy="-26" rx="34" ry="7"/><ellipse class="rotor" cx="60" cy="-26" rx="34" ry="7"/></g>';
  // Periyodik sırt hattı: 3840 px geniş, her 1920 px'de tekrarlar (kaydırmada dikisş yok)
  const hills = (y, a, s, k1 = 2, k2 = 5) => {
    let d = 'M0 1200';
    for (let x = 0; x <= 3840; x += 40) { const w = 2 * Math.PI * x / 1920; d += ' L' + x + ' ' + (y + a * (Math.sin(k1 * w + s) + .5 * Math.sin(k2 * w + 2 * s))).toFixed(1); }
    return d + ' L3840 1200 Z';
  };
  const wheel = cx => '<g transform="translate(' + cx + ',-72)"><circle class="trim" r="72"/><g class="dk-wh"><circle class="gun2" r="46"/>' +
    [0, 60, 120].map(a => '<rect class="body" x="-44" y="-5" width="88" height="10" transform="rotate(' + a + ')"/>').join('') +
    '<circle class="trim" r="12"/></g></g>';
  // Çift kabin pikap, yandan, sağa bakar; zemin y=0, boy 954 px
  const truck = id => '<g>' +
    '<defs><pattern id="' + id + '" patternUnits="userSpaceOnUse" width="260" height="170">' +
    '<rect class="body" width="260" height="170"/>' +
    '<path class="camo1" d="M8 22 L74 6 L104 44 L56 70 L10 58 Z"/><path class="camo2" d="M130 10 L200 26 L186 62 L128 54 Z"/>' +
    '<path class="camo1" d="M150 90 L236 80 L250 130 L170 150 L140 120 Z"/><path class="camo2" d="M20 100 L90 96 L100 140 L40 160 Z"/>' +
    '<path class="trim" d="M200 140 L252 150 L240 168 L196 162 Z"/></pattern></defs>' +
    '<path class="net" d="M112 -196 L224 -196 L192 -320 L144 -320 Z"/>' +
    '<path class="seam" style="stroke-width:10" d="M350 -210 L338 -268 L292 -274"/>' +
    '<path fill="url(#' + id + ')" d="M10 -62 L6 -198 L14 -208 L338 -208 L352 -216 L368 -326 Q374 -340 396 -340 L618 -340 Q640 -340 654 -328 L764 -236 L898 -222 Q942 -216 950 -192 L954 -120 L950 -68 L930 -44 L862 -44 A90 90 0 1 0 690 -44 L274 -44 A90 90 0 1 0 102 -44 L30 -44 Z"/>' +
    '<path class="glass" d="M384 -322 L500 -322 L500 -242 L376 -242 Z"/>' +
    '<path class="glass" d="M516 -324 L622 -324 Q632 -324 640 -317 L724 -244 L516 -244 Z"/>' +
    '<rect class="trim" x="404" y="-348" width="196" height="8" rx="4"/>' +
    '<path class="seam" d="M512 -322 L512 -52 M742 -232 L738 -52 M360 -212 L356 -52 M6 -150 L338 -150"/>' +
    '<rect class="trim" x="466" y="-224" width="34" height="8" rx="4"/><rect class="trim" x="698" y="-224" width="34" height="8" rx="4"/>' +
    '<path class="trim" d="M716 -250 L758 -256 L764 -234 L722 -230 Z"/>' +
    '<path class="lamp" d="M902 -214 L944 -206 L950 -192 L906 -199 Z"/>' +
    '<path class="trim" d="M954 -120 L950 -68 L930 -44 L906 -44 L928 -70 L934 -120 Z"/>' +
    '<rect class="hot" x="6" y="-198" width="12" height="52" rx="3"/>' +
    '<rect class="trim" x="282" y="-60" width="402" height="14" rx="5"/>' +
    '<path class="flare" d="M98 -48 A94 94 0 1 1 278 -48"/><path class="flare" d="M686 -48 A94 94 0 1 1 866 -48"/>' +
    wheel(188) + wheel(776) +
    '<g transform="translate(168,-318) scale(.72)">' + turret() + '</g></g>';
  // Dron Kalkanı logosu: dört pervane, üst ve alt gövde, ortada yazı (gönderilen logodan vektör olarak)
  const prop = (cx, cy, a) => {
    const R = 115, g = 20, p = d => [cx + R * Math.cos(d * Math.PI / 180), cy + R * Math.sin(d * Math.PI / 180)].map(v => v.toFixed(1)).join(' ');
    const arc = (a0, a1) => 'M' + p(a0) + ' A' + R + ' ' + R + ' 0 0 1 ' + p(a1);
    const blade = 'M34 -5 C58 -28 96 -24 106 -10 C110 -3 106 5 97 7 C72 11 52 9 34 6 Z';
    return '<path class="dkl-ring" d="' + arc(a + g, a + 180 - g) + ' ' + arc(a + 180 + g, a + 360 - g) + '"/>' +
      '<path class="dkl-f" transform="translate(' + cx + ',' + cy + ') rotate(' + a + ')" d="' + blade + '"/>' +
      '<path class="dkl-f" transform="translate(' + cx + ',' + cy + ') rotate(' + (a + 180) + ')" d="' + blade + '"/>' +
      '<circle class="dkl-f" cx="' + cx + '" cy="' + cy + '" r="33"/>' +
      '<path class="dkl-hi" d="M' + (cx + 8) + ' ' + (cy - 20) + ' A20 20 0 0 1 ' + (cx + 20) + ' ' + (cy - 6) + '"/>' +
      '<circle class="dkl-in" cx="' + cx + '" cy="' + cy + '" r="7"/>';
  };
  const dkTop = prop(325, 330, -45) + prop(775, 330, 45) +
    '<path class="dkl-f" d="M372 345 C450 395 500 425 550 438 C600 425 650 395 728 345 C745 352 758 365 762 378 C735 415 718 440 705 465 L398 465 C385 440 368 415 340 378 C344 365 355 352 372 345 Z"/>';
  const dkLogo = w => '<div style="position:relative;width:' + w + 'px;height:' + (w * .704).toFixed(1) + 'px">' +
    '<svg viewBox="60 190 980 690" style="position:absolute;inset:0;width:100%;height:100%;overflow:visible">' + dkTop +
    '<g transform="translate(0,1064) scale(1,-1)">' + dkTop + '</g></svg>' +
    '<p class="dkl-t" style="position:absolute;left:-2%;right:-2%;top:' + (w * .287).toFixed(1) + 'px;font-size:' + (w * .125).toFixed(1) + 'px">DRON KALKANI</p></div>';
  // Turaç logosu: halkalar, baklava içinde kuş, ad ve alt satırlar
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
  return {
    turret, drone, hills, truck, dkLogo, trcLogo,
    // İngilizce satırlar: data-at saniyesinde soldan süzülerek gelir; data-at yoksa dokunulmaz
    en: (els, t) => els.forEach(e => { if (!e.dataset.at) return; const p = Math.min(1, Math.max(0, (t - +e.dataset.at) / .5)), q = 1 - Math.pow(1 - p, 3); e.style.opacity = q; e.style.transform = 'translateX(' + ((1 - q) * 20).toFixed(1) + 'px)'; }),
    MUZ: [220, 28],          // düz silahın namlu ucu, dk-pr içinde
    TPIV: [168, -390],       // pikapta taret yükseliş pivotu
    TSC: 0.72,
    aim: (px, py, x, y) => Math.atan2(y - py, x - px) * 180 / Math.PI,
    muzzle: (px, py, deg, sc) => { const r = deg * Math.PI / 180, mx = 220 * sc, my = 28 * sc; return [px + mx * Math.cos(r) - my * Math.sin(r), py + mx * Math.sin(r) + my * Math.cos(r)]; },
  };
})();