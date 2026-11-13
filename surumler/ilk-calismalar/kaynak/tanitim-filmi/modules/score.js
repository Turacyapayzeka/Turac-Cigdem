kit.score(function (S, T) {
  // 120 BPM: sahne başlangıçları vuruş ızgarasına oturur (0, 8, 16, 26, 40, 52, 66, 76, 86, 98, 108; son 118)
  S.tempo(120, { t0: 0 });
  S.program('pad', 'pad', { rev: 0.6 }); S.program('bass', 'bass'); S.program('keys', 'ep', { rev: 0.3 }); S.program('mallet', 'marimba', { pan: 0.2 });
  // Tehdit ve sorun: alçak, gergin zemin
  S.chord('pad', ['D2', 'A2', 'F3'], { beat: 0, beats: 8, vel: 34 });
  S.chord('pad', ['Bb1', 'F2', 'D3'], { beat: 8, beats: 8, vel: 38 });
  S.pattern('bass', 'x.......', { from: 0, repeat: 4, pitch: ['D2', 'D2', 'Bb1', 'Bb1'], vel: 50 });
  S.drums({ hat: '..o...o.' }, { from: 8, repeat: 2, vel: 40 });
  // Ürün: taret yükselir, marimba motifi girer
  S.fx('revswell', T.urun, { dur: 1 });
  S.fx('thud', T.urun + 1.45, { vel: 90 });
  S.chord('pad', ['D3', 'A3', 'E4'], { beat: 16, beats: 10, vel: 42 });
  S.pattern('mallet', 'x.x.X.x.', { from: 18, repeat: 2, pitch: ['D5', 'A4', 'F5', 'A4'], vel: 52 });
  // Yakından: sıcak akorlar, her kare geçişinde hafif bir süzülme
  [['D3', 'A3', 'F4', 'C5'], ['Bb2', 'F3', 'D4', 'A4'], ['C3', 'G3', 'E4', 'G4'], ['A2', 'E3', 'C4', 'E4']].forEach((c, i) => S.chord('keys', c, { beat: 26 + i * 3.5, beats: 3.2, vel: 50 }));
  S.chord('pad', ['F3', 'A3', 'D4'], { beat: 26, beats: 14, vel: 36 });
  S.drums({ shaker: 'xoxoxoxo' }, { from: 28, repeat: 3, vel: 34 });
  [2.3, 4.6].forEach(d => S.fx('whoosh', T.yakin + d, { dur: 0.5, vel: 36 }));
  // Nasıl çalışır: hafif bir nabız, her adımda bir pop
  S.drums({ sidestick: '..x...x.', hat: 'oxoxoxox' }, { from: 40, repeat: 3, vel: 55 });
  S.pattern('bass', 'x...x...', { from: 40, repeat: 3, pitch: ['D2', 'C2', 'Bb1'], vel: 62 });
  [['D3', 'A3', 'F4'], ['C3', 'G3', 'E4'], ['Bb2', 'F3', 'D4']].forEach((c, i) => S.chord('keys', c, { beat: 40 + i * 4, beats: 3.5, vel: 46 }));
  [0.9, 2.1, 3.3].forEach(d => S.fx('pop', T.nasil + d, { vel: 70 }));
  // Platformlar: tam ritim
  S.drums({ kick: 'x...x...', sidestick: '..x...x.', hat: 'oxoxoxox' }, { from: 52, repeat: 8, vel: 70 });
  S.pattern('bass', 'x..x..x.', { from: 52, repeat: 8, pitch: ['D2', 'D2', 'F2'], vel: 78 });
  const prog = [['D3', 'A3', 'F4'], ['Bb2', 'F3', 'D4'], ['C3', 'G3', 'E4'], ['A2', 'E3', 'C4']];
  for (let i = 0; i < 8; i++) S.chord('keys', prog[i % 4], { beat: 52 + i * 4, beats: 3.5, vel: 50 });
  S.pattern('mallet', 'x...x.x.', { from: 68, repeat: 4, pitch: ['A5', 'F5', 'D5'], vel: 40 });
  [[T.arac, 2.77, 3.37, 5.2], [T.gemi, 1, 1.6, 3.4], [T.kule, 2.38, 2.98, 4]].forEach(([s, d, l, f]) => {
    S.fx('ding', s + d, { vel: 60 });
    S.fx('pop', s + l, { vel: 70 });
    S.fx('thud', s + f, { vel: 110 });
    S.fx('click', s + f, { vel: 100 });
    S.fx('whoosh', s + f + 0.2, { dur: 0.6, vel: 50 });
  });
  // Koruma alanı: ritim çekilir, geniş bir pad ve parlak notalar
  S.fx('sparkle', T.alan + 0.2, { vel: 55 });
  S.chord('pad', ['D3', 'F#3', 'A3', 'E4'], { beat: 86, beats: 12, vel: 46 });
  S.chord('keys', ['D3', 'A3', 'F#4', 'B4'], { beat: 86, beats: 6, vel: 50 });
  S.chord('keys', ['G2', 'D3', 'B3', 'F#4'], { beat: 92, beats: 6, vel: 50 });
  S.pattern('mallet', 'x.x.x...', { from: 86, repeat: 3, pitch: ['F#5', 'A5', 'D6'], vel: 38 });
  [2, 4].forEach(d => S.fx('whoosh', T.alan + d, { dur: 0.5, vel: 34 }));
  // Ortak yapım: sıcak, sakin; kartlar geldikçe hafif tik
  S.chord('pad', ['F3', 'A3', 'C4', 'E4'], { beat: 98, beats: 10, vel: 44 });
  S.chord('keys', ['F3', 'C4', 'E4', 'A4'], { beat: 98, beats: 4, vel: 48 });
  S.chord('keys', ['G3', 'D4', 'F4', 'B4'], { beat: 102, beats: 4, vel: 48 });
  S.note('bass', 'F2', { beat: 98, beats: 4, vel: 64 }); S.note('bass', 'G2', { beat: 102, beats: 4, vel: 64 });
  S.fx('sparkle', T.ortak + 0.5, { vel: 50 });
  [1.1, 1.4, 1.7, 2].forEach(d => S.fx('tick', T.ortak + d, { vel: 45 }));
  // Kapanış: yükselir, logo inerken çözülür ve çınlar
  S.fx('revswell', T.kapanis, { dur: 1.2 });
  S.run('mallet', ['D5', 'E5', 'F#5', 'A5', 'B5', 'D6'], { t: T.kapanis - 0.62, step: 0.1, vel: 52, cresc: 8 });
  S.chord('keys', ['D3', 'A3', 'D4', 'F#4', 'A4'], { beat: 108, beats: 10, vel: 72 });
  S.chord('pad', ['D3', 'F#3', 'A3', 'D4'], { beat: 108, beats: 10, vel: 50 });
  S.note('bass', 'D2', { beat: 108, beats: 4, vel: 84 });
  S.drum('crash', { beat: 108, vel: 70 });
  S.drum('kick', { beat: 108, vel: 100 });
  S.master({ gain: -6, fadeOut: 1.2 });
});