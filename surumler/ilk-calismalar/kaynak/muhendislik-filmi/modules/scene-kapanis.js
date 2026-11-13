const { seg, eo, eob, lerp, TextFx } = kit;
kit.scene('kapanis', {
  init(kit) {
    kit.stage.append(kit.h('<div class="ground"><div class="grid kapanis-g"></div></div>'));
    kit.stage.append(kit.h('<div class="kapanis-logo" style="position:absolute;left:130px;top:290px;transform-origin:350px 246px">' + DK.dkLogo(700) + '</div>'));
    kit.stage.append(kit.h('<div class="words" style="left:960px;top:310px;width:860px;gap:18px">' +
      '<h1 class="line kapanis-name">Son 150 metre bizim.</h1><p class="en kapanis-e1">The last 150 metres are ours.</p>' +
      '<div class="kapanis-ul" style="height:8px;width:320px;background:var(--accent);transform-origin:0 50%"></div>' +
      '<p class="tag kapanis-url" style="font-size:34px;letter-spacing:.06em;color:var(--second);margin-top:26px">dronkalkani.com.tr</p>' +
      '<p class="firm kapanis-pt" style="margin-top:8px">TURAÇ · DERYA ARMS · LASERSAN · URBAN SAVUNMA · İTÜ ARC</p></div>'));
    this.g = kit.stage.querySelector('.kapanis-g').style;
    this.logo = kit.stage.querySelector('.kapanis-logo').style;
    this.name = kit.stage.querySelector('.kapanis-name');
    for (const k of ['e1', 'ul', 'url', 'pt']) this[k] = kit.stage.querySelector('.kapanis-' + k).style;
  },
  render(t) {
    this.g.opacity = (.6 * (1 - eo(seg(t, 0, 1.2))) + .25).toFixed(3);
    // Logo bir noktadan büyüyüp yerine oturur, sonra hafifçe nefes alır
    this.logo.opacity = eo(seg(t, 0, .2));
    this.logo.transform = 'scale(' + (lerp(.1, 1, eob(seg(t, 0, .9), 1.6)) * kit.breathe(t, .006)).toFixed(4) + ')';
    TextFx.fadeFromRight(this.name, t, .6);
    const f = (s, a) => { s.opacity = eo(seg(t, a, a + .45)); s.transform = 'translateX(' + lerp(20, 0, eo(seg(t, a, a + .45))).toFixed(1) + 'px)'; };
    f(this.e1, 1.1); f(this.url, 1.6); f(this.pt, 1.9);
    this.ul.transform = 'scaleX(' + eo(seg(t, 1.2, 1.7)).toFixed(3) + ')';
  },
});