const { seg, eo, eio, eob, lerp, TextFx } = kit;
kit.scene('kapanis', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground">' +
      '<svg class="art" viewBox="0 0 1920 1080"><rect class="sky" width="1920" height="1080"/>' +
      '<path class="hill3 kapanis-h" d="' + DK.hills(930, 30, 5.2) + '"/>' +
      '<path class="hill2 kapanis-h" d="' + DK.hills(1010, 22, 2.7, 3, 7) + '"/></svg>' +
      '<div class="kapanis-logo" style="position:absolute;left:110px;top:240px">' + DK.dkLogo(760) + '</div>' +
      '<div class="words" style="left:960px;top:200px;width:860px;gap:20px">' +
      '<h1 class="line kapanis-name">Son 150 metre bizim.</h1><p class="en" data-at="1.2">The last 150 metres are ours.</p>' +
      '<div class="kapanis-ul" style="height:10px;width:360px;background:var(--accent);transform-origin:0 50%"></div>' +
      '<p class="sub kapanis-sub">Otonom robotik anti-drone kule sistemi</p><p class="en" data-at="1.6">Autonomous robotic anti-drone turret system</p>' +
      '<div class="kapanis-chips" style="display:flex;gap:18px;flex-wrap:wrap"><p class="chip" style="margin:0;border-color:var(--main)">600–800 m TESPİT</p>' +
      '<p class="chip" style="margin:0;border-color:var(--main)">150 m ANGAJMAN</p></div>' +
      '<p class="en" data-at="1.85">600–800 m detection · 150 m engagement</p>' +
      '<p class="tag kapanis-url" style="margin-top:24px;color:var(--second);font-size:34px;letter-spacing:.08em">dronkalkani.com.tr</p></div>' +
      '<div class="kapanis-trc" style="position:absolute;left:1660px;top:840px">' + DK.trcLogo(170) + '</div></div>'));
    const q = s => kit.stage.querySelector(s);
    this.hs = [...kit.stage.querySelectorAll('.kapanis-h')];
    this.name = q('.kapanis-name');
    for (const k of ['logo', 'ul', 'sub', 'chips', 'url', 'trc']) this[k] = q('.kapanis-' + k).style;
    this.logo.transformOrigin = '380px 268px';
    this.trc.transformOrigin = '85px 85px';
    this.ens = [...kit.stage.querySelectorAll('.en')];
  },
  render(t) {
    DK.en(this.ens, t);
    this.hs.forEach((h, i) => h.setAttribute('transform', 'translate(' + (-t * (4 + i * 6)) + ',0)'));
    // Logo bir noktadan büyüyüp yerine oturur, sonra hafifçe nefes alır
    const lp = seg(t, 0, .9);
    this.logo.opacity = eo(seg(t, 0, .2));
    this.logo.transform = 'scale(' + (lerp(.1, 1, eob(lp, 1.6)) * kit.breathe(t, .006)).toFixed(4) + ')';
    TextFx.fadeFromRight(this.name, t, .6);
    this.ul.transform = 'scaleX(' + eo(seg(t, 1.2, 1.7)) + ')';
    const fade = (s, a) => { s.opacity = eo(seg(t, a, a + .45)); s.transform = 'translateX(' + lerp(26, 0, eo(seg(t, a, a + .45))) + 'px)'; };
    fade(this.sub, 1.3); fade(this.chips, 1.55); fade(this.url, 2);
    const tp = seg(t, 2.1, 2.7);
    this.trc.opacity = eo(tp);
    this.trc.transform = 'scale(' + lerp(.6, 1, eob(tp, 1.6)).toFixed(3) + ')';
  },
});