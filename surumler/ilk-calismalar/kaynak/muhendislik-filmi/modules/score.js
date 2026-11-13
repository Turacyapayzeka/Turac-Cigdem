kit.score(function (S, T) {
  // 120 BPM: sahneler vuruş ızgarasına oturur (0, 10, 22, 32, 42, 56, 68, 88, 100; son 110)
  S.tempo(120, { t0: 0 });
  S.program('pad', 'pad', { rev: 0.6 }); S.program('bass', 'bass'); S.program('keys', 'ep', { rev: 0.3 });
  S.program('pl', 'pluck', { pan: -0.2, rev: 0.3 }); S.program('glk', 'glock', { pan: 0.25, rev: 0.4 });
  // Açılış ve platform: sakin pad, nabız gibi bas, pluck arpej
  S.chord('pad', ['D3', 'A3', 'E4'], { beat: 0, beats: 10, vel: 40 });
  S.chord('pad', ['Bb2', 'F3', 'D4'], { beat: 10, beats: 12, vel: 42 });
  S.pattern('bass', 'x...x...', { from: 0, repeat: 5, pitch: ['D2'], vel: 52 });
  S.pattern('pl', 'x.x.x.x.', { from: 4, repeat: 4, pitch: ['D4', 'A4', 'E5', 'A4'], vel: 44 });
  S.pattern('pl', 'x.x.x.x.', { from: 10, repeat: 6, pitch: ['Bb3', 'F4', 'D5', 'F4'], vel: 46 });
  S.drums({ hat: '..o...o.' }, { from: 10, repeat: 6, vel: 38 });
  // Yakın çekimler: ritim girer
  S.drums({ kick: 'x.......', hat: 'oxoxoxox', shaker: 'xoxoxoxo' }, { from: 22, repeat: 10, vel: 56 });
  S.pattern('bass', 'x..x..x.', { from: 22, repeat: 10, pitch: ['C2', 'C2', 'G1', 'A1', 'A1', 'E2'], vel: 66 });
  [['C3', 'G3', 'E4'], ['G2', 'D3', 'B3'], ['A2', 'E3', 'C4'], ['F2', 'C3', 'A3'], ['C3', 'G3', 'E4']].forEach((c, i) => S.chord('keys', c, { beat: 22 + i * 4, beats: 3.6, vel: 46 }));
  // Çağrı çizgileri: her etiket hafif bir tikle gelir
  [[T.parca, .5, .55, 3], [T.kule, .4, .6, 3], [T.sensor, .4, .7, 2], [T.cizim, 3.4, .35, 4]].forEach(([s, a, st, n]) => { for (let i = 0; i < n; i++) S.fx('tick', s + a + i * st + .35, { vel: 50 }); });
  // Teknik çizim: süzülme, parçalar ayrılır, oturur
  S.fx('whoosh', T.cizim + 0.1, { dur: 1.2, vel: 40 });
  S.fx('whoosh', T.cizim + 2, { dur: 0.8, vel: 55 });
  S.fx('pop', T.cizim + 3.3, { vel: 70 });
  S.chord('pad', ['A2', 'E3', 'B3', 'E4'], { beat: 42, beats: 14, vel: 44 });
  S.pattern('glk', 'x...x...', { from: 46, repeat: 2, pitch: ['E5', 'B5', 'A5', 'E6'], vel: 40 });
  // Değerler: rakamlar sayarken kısa yuvarlanmalar
  S.drums({ kick: 'x...x...', sidestick: '..x...x.', hat: 'oxoxoxox' }, { from: 56, repeat: 3, vel: 64 });
  S.pattern('bass', 'x..x..x.', { from: 56, repeat: 3, pitch: ['D2', 'D2', 'F2'], vel: 74 });
  [['D3', 'A3', 'F4'], ['Bb2', 'F3', 'D4'], ['C3', 'G3', 'E4']].forEach((c, i) => S.chord('keys', c, { beat: 56 + i * 4, beats: 3.6, vel: 50 }));
  [0, 1, 2].forEach(i => S.fx('roll', T.degerler + .8 + i * .45, { dur: 1.1, vel: 38 }));
  // Katmanlı savunma: ritim çekilir, her katman yükselen bir notayla gelir, son katmanda vurgu
  S.chord('pad', ['D3', 'A3', 'E4', 'A4'], { beat: 68, beats: 20, vel: 46 });
  S.pattern('bass', 'x.......', { from: 68, repeat: 5, pitch: ['D2', 'D2', 'C2', 'Bb1', 'A1'], vel: 56 });
  S.drums({ hat: '..o...o.' }, { from: 68, repeat: 5, vel: 34 });
  ['A4', 'C5', 'D5', 'E5'].forEach((n, i) => { S.note('glk', n, { t: T.katman + .8 + i * 1.6, dur: 1.4, vel: 46 }); S.fx('whoosh', T.katman + .8 + i * 1.6, { dur: .9, vel: 26 }); });
  S.fx('revswell', T.katman + 7.2, { dur: 1.1 });
  S.chord('keys', ['D3', 'A3', 'D4', 'F#4', 'A4'], { t: T.katman + 7.2, dur: 2.6, vel: 64 });
  S.drum('kick', { t: T.katman + 7.2, vel: 90 });
  S.note('glk', 'A5', { t: T.katman + 7.2, dur: 2, vel: 54 });
  // Üretim: ritim geri gelir, kartlar tikle
  S.drums({ kick: 'x...x...', sidestick: '..x...x.', hat: 'oxoxoxox' }, { from: 88, repeat: 3, vel: 62 });
  [['F3', 'C4', 'A4'], ['G3', 'D4', 'B4'], ['A3', 'E4', 'C5']].forEach((c, i) => S.chord('keys', c, { beat: 88 + i * 4, beats: 3.6, vel: 48 }));
  S.pattern('bass', 'x..x..x.', { from: 88, repeat: 3, pitch: ['F2', 'G2', 'A2'], vel: 70 });
  [0, 1, 2].forEach(i => S.fx('roll', T.uretim + 1.2 + i * .3, { dur: 1.1, vel: 34 }));
  S.fx('sparkle', T.uretim + .4, { vel: 50 });
  [0, 1, 2, 3, 4].forEach(i => S.fx('tick', T.uretim + 2.6 + i * .18, { vel: 44 }));
  // Kapanış: yükselip çözülür
  S.fx('revswell', T.kapanis, { dur: 1.2 });
  S.run('glk', ['D5', 'E5', 'F#5', 'A5', 'B5', 'D6'], { t: T.kapanis - 0.62, step: 0.1, vel: 48, cresc: 8 });
  S.chord('keys', ['D3', 'A3', 'D4', 'F#4', 'A4'], { beat: 100, beats: 10, vel: 70 });
  S.chord('pad', ['D3', 'F#3', 'A3', 'D4'], { beat: 100, beats: 10, vel: 50 });
  S.note('bass', 'D2', { beat: 100, beats: 4, vel: 82 });
  S.drum('crash', { beat: 100, vel: 66 }); S.drum('kick', { beat: 100, vel: 96 });
  S.master({ gain: -6, fadeOut: 1.2 });
});