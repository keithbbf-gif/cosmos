/* APPLY_SETTINGS.js
   NOTE: this file does not modify site/engines.js.
   The live LMN_PLAY reads def.goal, def.speed, def.lives, def.inspired, and def.better.
   Packs in site_new also carry settings, and blurb when the named game is a real
   title this engine's loop can follow. Load this file after engines.js.
   It copies missing top-level knobs from settings, and a fair blurb onto inspired
   when inspired is empty. It does not replace LMN_PLAY's own cap clamp.
   LMN_LEVELS and LMN_MODES are data. They apply only when settings.level or
   settings.mode_name is set on the def passed to LMN_PLAY. Arcade does not set those. */
(function () {
  var caps = {
    match3: 12, blast: 8, runner: 24, stack: 8, merge: 6, memory: 8, snake: 10,
    breakout: 18, whack: 10, slide: 1, word: 1, idle: 80, cards: 5, lane: 20,
    board: 12, rhythm: 10, farm: 4, quiz: 5
  };
  var prev = window.LMN_PLAY;
  if (typeof prev !== "function") return;

  function findRow(list, base) {
    if (!list) return null;
    for (var i = 0; i < list.length; i++) {
      if (list[i] && list[i].base_id === base) return list[i];
    }
    return null;
  }

  window.LMN_PLAY = function (def, root) {
    var play = {};
    var src = def || {};
    Object.keys(src).forEach(function (k) { play[k] = src[k]; });
    var s = play.settings || {};
    if (s.level && window.LMN_LEVELS) {
      var lrow = findRow(window.LMN_LEVELS, s.base_id || play.id);
      var lv = lrow && lrow.levels && lrow.levels[(s.level | 0) - 1];
      if (lv) {
        if (lv.goal != null) play.goal = lv.goal;
        if (lv.speed != null) play.speed = lv.speed;
        if (lv.lives != null) play.lives = lv.lives;
      }
    }
    if (s.mode_name && window.LMN_MODES) {
      var mrow = findRow(window.LMN_MODES, s.base_id || play.id);
      var modes = (mrow && mrow.modes) || [];
      for (var i = 0; i < modes.length; i++) {
        if (modes[i].name === s.mode_name) {
          if (modes[i].goal != null) play.goal = modes[i].goal;
          if (modes[i].speed != null) play.speed = modes[i].speed;
          if (modes[i].lives != null) play.lives = modes[i].lives;
        }
      }
    }
    ["goal", "speed", "lives"].forEach(function (k) {
      if (play[k] == null && s[k] != null) play[k] = s[k];
    });
    if (!play.inspired && typeof play.blurb === "string" && play.blurb.indexOf("After ") === 0) {
      play.inspired = play.blurb.slice(6);
    }
    if (!play.better && s.change) play.better = s.change;
    var cap = caps[play.engine];
    if (typeof play.goal === "number" && cap && play.goal > cap) play.goal = cap;
    if (typeof play.speed === "number" && play.speed > 4) play.speed = 3;
    return prev(play, root);
  };
})();
