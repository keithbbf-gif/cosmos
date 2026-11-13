"use strict";

/*
 * Local stand-in for queue.php plus the N-player ops in LOBBY_API_DESIGN.md.
 * Runs under node and in the browser. It does not open a socket and does not
 * write lmn_match.json or lmn_runs.jsonl.
 *
 * The legacy join (teammate + enemy, no seats count) follows queue.php:
 * four slots a1 a2 b1 b2, b2 always the Novelist AI, either-mode fill at 8s.
 * The N-player join is the extension. It is not what the live PHP does today.
 */

(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
    if (require.main === module) api.runSim();
  }
  root.LMN_MOCK_QUEUE = api;
})(typeof window !== "undefined" ? window : globalThis, function () {
  var FILL_AFTER_S = 8;
  var TICKET_TTL_S = 45;
  var MATCH_TTL_S = 1200;
  var MIN_SEATS = 2;
  var MAX_SEATS = 8;
  var SKILL = { easy: 0.4, medium: 0.58, hard: 0.76 };
  var AI_NAMES = ["Librarian", "Sprinter", "Novelist", "Clerk", "Old Hand", "Understudy"];
  var LEGACY_AI = {
    a2: { name: "Librarian", difficulty: "hard", skill: 0.76 },
    b1: { name: "Sprinter", difficulty: "medium", skill: 0.58 },
    b2: { name: "Novelist", difficulty: "easy", skill: 0.4 }
  };
  var CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

  function createStore(opts) {
    opts = opts || {};
    var frozen = !!opts.frozen;
    var t = typeof opts.now === "number" ? opts.now : 0;
    var wall = Date.now();
    var extra = 0;
    return {
      queue: [],
      matches: [],
      lobbies: [],
      saves: [],
      seq: 1,
      frozen: frozen,
      now: function () {
        if (this.frozen) return t;
        return t + extra + Math.floor((Date.now() - wall) / 1000);
      },
      advance: function (sec) {
        sec = sec || 0;
        if (this.frozen) t += sec;
        else extra += sec;
      }
    };
  }

  function cleanPid(pid) {
    return String(pid || "").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 40);
  }

  function cleanName(name) {
    var n = String(name == null ? "" : name).replace(/[^a-zA-Z0-9 _-]/g, "").slice(0, 16);
    return n === "" ? "Player" : n;
  }

  function cleanGame(game) {
    var g = String(game || "");
    return /^[a-z][a-z0-9]{0,15}$/.test(g) ? g : "";
  }

  function legacyGameOk(game) {
    return game === "higher" || game === "tiles" || game === "derby" || /^[sm][0-9]{2}$/.test(game);
  }

  function tag(text) {
    var h = 2166136261;
    var s = String(text);
    var i;
    for (i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return ("000000" + (h >>> 0).toString(16)).slice(-6);
  }

  function dropPids(state, pids) {
    state.queue = state.queue.filter(function (q) {
      return pids.indexOf(q.pid) < 0;
    });
  }

  function expire(state, now) {
    state.queue = state.queue.filter(function (q) {
      return (now - q.seen) < TICKET_TTL_S;
    });
    state.matches = state.matches.filter(function (m) {
      return (now - m.created) < MATCH_TTL_S;
    });
    state.lobbies = state.lobbies.filter(function (room) {
      if (room.started) return true;
      return (now - room.seen) < TICKET_TTL_S;
    });
  }

  function slotRow(slot, kind, name, pid, skill, difficulty) {
    return {
      slot: slot,
      kind: kind,
      name: name,
      pid: pid,
      skill: skill,
      difficulty: difficulty || ""
    };
  }

  function makeMatch(state, now, game, roster, pids, extra) {
    state.seq += 1;
    extra = extra || {};
    return {
      id: "m" + now + tag(String(pids[0]) + game + state.seq),
      game: game,
      seed: (now % 100000) + (state.seq % 999) + 1,
      roster: roster,
      moves: {},
      created: now,
      pids: pids.slice(),
      legacy: !!extra.legacy,
      layout: extra.layout || "ffa",
      fill: extra.fill || "either",
      seats_n: roster.length
    };
  }

  function publicMoves(moves) {
    if (!moves || typeof moves !== "object" || !Object.keys(moves).length) return {};
    return moves;
  }

  function twoVtwoSeats(match, pid) {
    var by = {};
    match.roster.forEach(function (s) { by[s.slot] = s; });
    var slot = "a1";
    match.roster.forEach(function (s) {
      if (s.pid && s.pid === pid) slot = s.slot;
    });
    var side = slot.charAt(0);
    var other = side === "a" ? "b" : "a";
    var mate = side + (slot.charAt(1) === "1" ? "2" : "1");
    var map = [
      ["you", slot],
      ["teammate", mate],
      ["enemy", other + "1"],
      ["enemy2", other + "2"]
    ];
    return map.map(function (pair) {
      var s = by[pair[1]];
      return {
        role: pair[0],
        slot: s.slot,
        kind: s.kind,
        name: s.name,
        pid: s.pid,
        skill: s.skill,
        difficulty: s.difficulty || ""
      };
    });
  }

  function publicMatch(match, pid) {
    var seats;
    var usePairs = match.layout === "2v2" && match.roster.length === 4 &&
      match.roster.every(function (s) { return /^[ab][12]$/.test(s.slot); });
    if (usePairs) seats = twoVtwoSeats(match, pid);
    else {
      seats = match.roster.map(function (s) {
        return {
          role: s.pid === pid ? "you" : s.slot,
          slot: s.slot,
          kind: s.kind,
          name: s.name,
          pid: s.pid,
          skill: s.skill,
          difficulty: s.difficulty || ""
        };
      });
    }
    return {
      id: match.id,
      game: match.game,
      seed: match.seed,
      seats: seats,
      moves: publicMoves(match.moves),
      you: pid,
      seats_n: match.seats_n,
      layout: match.layout,
      fill: match.fill,
      legacy: !!match.legacy
    };
  }

  function findMatch(state, pid) {
    var i;
    for (i = 0; i < state.matches.length; i++) {
      if (state.matches[i].pids.indexOf(pid) >= 0) return state.matches[i];
    }
    return null;
  }

  function queuedCount(state, game) {
    return state.queue.filter(function (q) { return q.game === game; }).length;
  }

  function waitOf(state, pid, now) {
    var i;
    for (i = 0; i < state.queue.length; i++) {
      if (state.queue[i].pid === pid) return now - state.queue[i].since;
    }
    return 0;
  }

  function touchQueue(state, pid, now) {
    state.queue.forEach(function (q) {
      if (q.pid === pid) q.seen = now;
    });
  }

  function slotIds(n, layout) {
    var out = [];
    var i;
    if (n === 4 && layout === "2v2") return ["a1", "a2", "b1", "b2"];
    for (i = 0; i < n; i++) out.push("s" + (i + 1));
    return out;
  }

  function aiFor(slot, index, tableDifficulty, slotDifficulty) {
    var chosen = slotDifficulty && slotDifficulty[index];
    if (chosen && Object.prototype.hasOwnProperty.call(SKILL, chosen)) {
      return slotRow(slot, "ai", AI_NAMES[index % AI_NAMES.length], "", SKILL[chosen], chosen);
    }
    if (tableDifficulty === "legacy" && LEGACY_AI[slot]) {
      var row = LEGACY_AI[slot];
      return slotRow(slot, "ai", row.name, "", row.skill, row.difficulty);
    }
    var diff = Object.prototype.hasOwnProperty.call(SKILL, tableDifficulty) ? tableDifficulty : "medium";
    return slotRow(slot, "ai", AI_NAMES[index % AI_NAMES.length], "", SKILL[diff], diff);
  }

  function buildRoster(anchor, others) {
    var ids = slotIds(anchor.seats, anchor.layout);
    var people = [anchor].concat(others);
    var roster = [];
    var i;
    for (i = 0; i < ids.length; i++) {
      if (i < people.length) {
        roster.push(slotRow(ids[i], "human", people[i].name, people[i].pid, 0, ""));
      } else {
        roster.push(aiFor(ids[i], i, anchor.difficulty, anchor.slot_difficulty));
      }
    }
    return roster;
  }

  function tryMakeLegacy(state, now) {
    var by = {};
    state.queue.forEach(function (q) {
      if (!q.legacy) return;
      (by[q.game] = by[q.game] || []).push(q);
    });
    var games = Object.keys(by);
    var g, i, j, k;
    for (g = 0; g < games.length; g++) {
      var tickets = by[games[g]];
      var used = {};
      for (i = 0; i < tickets.length; i++) {
        var a = tickets[i];
        if (used[a.pid]) continue;
        var age = now - a.since;
        var enemy = null;
        var mate = null;
        var needEnemy = a.enemy !== "ai";
        var needMate = a.teammate !== "ai";
        if (needEnemy) {
          for (j = 0; j < tickets.length; j++) {
            var b = tickets[j];
            if (b.pid === a.pid || used[b.pid]) continue;
            if (b.enemy === "ai") continue;
            enemy = b;
            break;
          }
        }
        if (needMate) {
          for (k = 0; k < tickets.length; k++) {
            var c = tickets[k];
            if (c.pid === a.pid || used[c.pid]) continue;
            if (enemy && c.pid === enemy.pid) continue;
            if (c.teammate === "ai") continue;
            mate = c;
            break;
          }
        }
        var enemyReady = !needEnemy || !!enemy || (a.enemy === "either" && (age >= FILL_AFTER_S || !!mate));
        var mateReady = !needMate || !!mate || (a.teammate === "either" && (age >= FILL_AFTER_S || !!enemy));
        if (!enemyReady || !mateReady) continue;
        var roster = [
          slotRow("a1", "human", a.name, a.pid, 0, ""),
          mate ? slotRow("a2", "human", mate.name, mate.pid, 0, "") : slotRow("a2", "ai", "Librarian", "", 0.76, "hard"),
          enemy ? slotRow("b1", "human", enemy.name, enemy.pid, 0, "") : slotRow("b1", "ai", "Sprinter", "", 0.58, "medium"),
          slotRow("b2", "ai", "Novelist", "", 0.4, "easy")
        ];
        var pids = [a.pid];
        if (mate) pids.push(mate.pid);
        if (enemy) pids.push(enemy.pid);
        pids.forEach(function (p) { used[p] = 1; });
        dropPids(state, pids);
        var match = makeMatch(state, now, a.game, roster, pids, { legacy: true, layout: "2v2", fill: "either" });
        state.matches.push(match);
        return match;
      }
    }
    return null;
  }

  function tryMakeN(state, now) {
    var groups = {};
    state.queue.forEach(function (q) {
      if (q.legacy) return;
      var key = q.game + "|" + q.seats + "|" + q.layout;
      (groups[key] = groups[key] || []).push(q);
    });
    var keys = Object.keys(groups);
    var g, i, j;
    for (g = 0; g < keys.length; g++) {
      var tickets = groups[keys[g]];
      var used = {};
      for (i = 0; i < tickets.length; i++) {
        var a = tickets[i];
        if (used[a.pid]) continue;
        var age = now - a.since;
        var want = a.seats - 1;
        var humans = [];
        if (a.fill !== "ai") {
          for (j = 0; j < tickets.length && humans.length < want; j++) {
            var b = tickets[j];
            if (b.pid === a.pid || used[b.pid]) continue;
            if (b.fill === "ai") continue;
            if (a.fill === "either" && b.fill === "human") continue;
            humans.push(b);
          }
        }
        var full = humans.length >= want;
        var timed = a.fill === "either" && age >= FILL_AFTER_S;
        var aiNow = a.fill === "ai";
        if (a.fill === "human" && !full) continue;
        if (!(aiNow || full || timed)) continue;
        var take = aiNow ? [] : humans.slice(0, want);
        var roster = buildRoster(a, take);
        var pids = [a.pid].concat(take.map(function (h) { return h.pid; }));
        pids.forEach(function (p) { used[p] = 1; });
        dropPids(state, pids);
        var match = makeMatch(state, now, a.game, roster, pids, {
          legacy: false,
          layout: a.layout,
          fill: a.fill
        });
        state.matches.push(match);
        return match;
      }
    }
    return null;
  }

  function sweep(state, now) {
    var made = tryMakeLegacy(state, now);
    if (made) return made;
    return tryMakeN(state, now);
  }

  function difficultyOk(value, allowLegacy) {
    if (value === "easy" || value === "medium" || value === "hard") return true;
    return allowLegacy && value === "legacy";
  }

  function readSlotDifficulty(raw, seats) {
    if (raw == null) return null;
    if (!Array.isArray(raw)) return false;
    if (raw.length > seats) return false;
    var out = [];
    var i;
    for (i = 0; i < raw.length; i++) {
      if (raw[i] == null || raw[i] === "") {
        out.push("");
        continue;
      }
      if (!difficultyOk(raw[i], false)) return false;
      out.push(raw[i]);
    }
    return out;
  }

  function layoutOf(raw, seats) {
    if (raw === "2v2" && seats === 4) return "2v2";
    return "ffa";
  }

  function readSeats(raw) {
    var n = Number(raw);
    if (!isFinite(n) || Math.floor(n) !== n) return 0;
    if (n < MIN_SEATS || n > MAX_SEATS) return 0;
    return n;
  }

  function immediateLegacy(state, now, ticket) {
    var roster = [
      slotRow("a1", "human", ticket.name, ticket.pid, 0, ""),
      slotRow("a2", "ai", "Librarian", "", 0.76, "hard"),
      slotRow("b1", "ai", "Sprinter", "", 0.58, "medium"),
      slotRow("b2", "ai", "Novelist", "", 0.4, "easy")
    ];
    var match = makeMatch(state, now, ticket.game, roster, [ticket.pid], {
      legacy: true,
      layout: "2v2",
      fill: "ai"
    });
    state.matches.push(match);
    return match;
  }

  function makeCode(state) {
    var n = state.seq;
    state.seq += 1;
    var chars = [];
    var i;
    for (i = 0; i < 4; i++) {
      chars.push(CODE_ALPHABET.charAt(n % CODE_ALPHABET.length));
      n = Math.floor(n / CODE_ALPHABET.length) + i + 1;
    }
    return chars.join("");
  }

  function findLobby(state, code) {
    code = String(code || "").toUpperCase();
    var i;
    for (i = 0; i < state.lobbies.length; i++) {
      if (state.lobbies[i].code === code) return state.lobbies[i];
    }
    return null;
  }

  function findLobbyByPid(state, pid) {
    var i, j;
    for (i = 0; i < state.lobbies.length; i++) {
      var room = state.lobbies[i];
      if (room.started) continue;
      for (j = 0; j < room.members.length; j++) {
        if (room.members[j].pid === pid) return room;
      }
    }
    return null;
  }

  function leaveLobby(state, pid) {
    var next = [];
    state.lobbies.forEach(function (room) {
      if (room.started) {
        next.push(room);
        return;
      }
      if (room.host === pid) return;
      room.members = room.members.filter(function (m) { return m.pid !== pid; });
      if (room.members.length) next.push(room);
    });
    state.lobbies = next;
  }

  function lobbyView(room, now) {
    return {
      status: "lobby",
      code: room.code,
      game: room.game,
      seats: room.seats,
      fill: room.fill,
      layout: room.layout,
      difficulty: room.difficulty,
      have: room.members.length,
      host: room.host,
      wait: now - room.created,
      members: room.members.map(function (m) {
        return { name: m.name, slot: m.slot, kind: "human", pid: m.pid };
      })
    };
  }

  function startLobby(state, room, now) {
    var host = room.members[0];
    var anchor = {
      pid: host.pid,
      name: host.name,
      seats: room.seats,
      layout: room.layout,
      difficulty: room.difficulty,
      slot_difficulty: room.slot_difficulty
    };
    var roster = buildRoster(anchor, room.members.slice(1));
    var pids = room.members.map(function (m) { return m.pid; });
    var match = makeMatch(state, now, room.game, roster, pids, {
      legacy: false,
      layout: room.layout,
      fill: room.fill
    });
    state.matches.push(match);
    room.started = true;
    room.match_id = match.id;
    return match;
  }

  function maybeStartLobby(state, room, now) {
    if (!room || room.started) return null;
    if (room.fill === "ai") return startLobby(state, room, now);
    if (room.members.length >= room.seats) return startLobby(state, room, now);
    if (room.fill === "either" && (now - room.created) >= FILL_AFTER_S) return startLobby(state, room, now);
    return null;
  }

  function answerMatch(state, pid) {
    var existing = findMatch(state, pid);
    if (!existing) return null;
    return { status: "matched", match: publicMatch(existing, pid) };
  }

  function handle(state, input) {
    var now = state.now();
    expire(state, now);
    if (!input || typeof input !== "object") return { error: "bad" };
    var op = input.op || "";
    var pid = cleanPid(input.pid);
    if (!pid) return { error: "pid" };

    if (op === "caps") {
      return {
        status: "ok",
        n_player: true,
        min_seats: MIN_SEATS,
        max_seats: MAX_SEATS,
        fill_after_s: FILL_AFTER_S,
        ticket_ttl_s: TICKET_TTL_S,
        match_ttl_s: MATCH_TTL_S,
        difficulties: { easy: SKILL.easy, medium: SKILL.medium, hard: SKILL.hard },
        ops: ["caps", "join", "poll", "leave", "move", "save", "lobby_open", "lobby_join", "lobby_poll"]
      };
    }

    if (op === "save") {
      var rec = input.record && typeof input.record === "object" ? input.record : null;
      var allow = ["game", "event", "match_id", "seed", "models", "calls", "lanes", "seats", "outcome"];
      var keep = {};
      if (!rec) return { error: "record" };
      allow.forEach(function (key) {
        if (Object.prototype.hasOwnProperty.call(rec, key)) keep[key] = rec[key];
      });
      var line = JSON.stringify(keep);
      if (line.length > 24000) return { error: "record" };
      state.saves.push(keep);
      return { status: "saved" };
    }

    if (op === "leave") {
      state.queue = state.queue.filter(function (q) { return q.pid !== pid; });
      leaveLobby(state, pid);
      return { status: "left" };
    }

    if (op === "move") {
      var mid = String(input.match || "").replace(/[^a-zA-Z0-9]/g, "").slice(0, 24);
      var round = String(parseInt(input.round, 10) || 0);
      var pick = String(input.pick == null ? "" : input.pick).slice(0, 80);
      var mi;
      for (mi = 0; mi < state.matches.length; mi++) {
        var m = state.matches[mi];
        if (m.id !== mid || m.pids.indexOf(pid) < 0) continue;
        if (!m.moves[round] || typeof m.moves[round] !== "object") m.moves[round] = {};
        m.moves[round][pid] = pick;
        return { status: "ok", match: publicMatch(m, pid) };
      }
      return { error: "nomatch" };
    }

    if (op === "lobby_open" || op === "lobby_join") {
      state.queue = state.queue.filter(function (q) { return q.pid !== pid; });
      leaveLobby(state, pid);
      if (op === "lobby_open") {
        var game = cleanGame(input.game);
        var seats = readSeats(input.seats);
        var fill = input.fill === "human" || input.fill === "ai" || input.fill === "either" ? input.fill : "";
        var difficulty = input.difficulty || "medium";
        if (!game || !seats || !fill || !difficultyOk(difficulty, true)) return { error: "mode" };
        var slotDifficulty = readSlotDifficulty(input.slot_difficulty, seats);
        if (slotDifficulty === false) return { error: "mode" };
        var layout = layoutOf(input.layout, seats);
        var name = cleanName(input.name);
        var ids = slotIds(seats, layout);
        var room = {
          code: makeCode(state),
          host: pid,
          game: game,
          seats: seats,
          fill: fill,
          difficulty: difficulty,
          slot_difficulty: slotDifficulty,
          layout: layout,
          created: now,
          seen: now,
          started: false,
          match_id: "",
          members: [{ pid: pid, name: name, slot: ids[0], since: now }]
        };
        state.lobbies.push(room);
        var opened = maybeStartLobby(state, room, now);
        if (opened) return { status: "matched", match: publicMatch(opened, pid) };
        return lobbyView(room, now);
      }
      var code = String(input.code || "").toUpperCase().replace(/[^A-Z2-9]/g, "").slice(0, 6);
      var joined = findLobby(state, code);
      if (!joined || joined.started) return { error: "closed" };
      if (joined.members.length >= joined.seats) return { error: "full" };
      if (joined.fill === "ai") return { error: "full" };
      var memberName = cleanName(input.name);
      var slotList = slotIds(joined.seats, joined.layout);
      joined.members.push({
        pid: pid,
        name: memberName,
        slot: slotList[joined.members.length],
        since: now
      });
      joined.seen = now;
      var started = maybeStartLobby(state, joined, now);
      if (started) return { status: "matched", match: publicMatch(started, pid) };
      return lobbyView(joined, now);
    }

    if (op === "lobby_poll" || op === "poll") {
      touchQueue(state, pid, now);
      var room = findLobbyByPid(state, pid);
      if (room) {
        room.seen = now;
        var began = maybeStartLobby(state, room, now);
        if (began) return { status: "matched", match: publicMatch(began, pid) };
        if (!room.started) return lobbyView(room, now);
      }
      sweep(state, now);
      var matched = answerMatch(state, pid);
      if (matched) return matched;
      var still = false;
      state.queue.forEach(function (q) { if (q.pid === pid) still = true; });
      if (!still) return { status: "none" };
      var gameName = "";
      state.queue.forEach(function (q) { if (q.pid === pid) gameName = q.game; });
      return {
        status: "queued",
        wait: waitOf(state, pid, now),
        queued: queuedCount(state, gameName)
      };
    }

    if (op === "join") {
      state.queue = state.queue.filter(function (q) { return q.pid !== pid; });
      leaveLobby(state, pid);
      var nameJoin = cleanName(input.name);
      var wantsN = input.seats != null && input.seats !== "";
      if (!wantsN) {
        var gameL = String(input.game || "");
        var tm = input.teammate || "ai";
        var en = input.enemy || "ai";
        var modes = { human: 1, ai: 1, either: 1 };
        if (!legacyGameOk(gameL) || !modes[tm] || !modes[en]) return { error: "mode" };
        var ticket = {
          pid: pid,
          name: nameJoin,
          game: gameL,
          teammate: tm,
          enemy: en,
          since: now,
          seen: now,
          legacy: true
        };
        if (tm === "ai" && en === "ai") {
          var quick = immediateLegacy(state, now, ticket);
          return { status: "matched", match: publicMatch(quick, pid) };
        }
        state.queue.push(ticket);
        sweep(state, now);
        var legacyHit = answerMatch(state, pid);
        if (legacyHit) return legacyHit;
        return { status: "queued", wait: waitOf(state, pid, now), queued: queuedCount(state, gameL) };
      }

      var gameN = cleanGame(input.game);
      var seatsN = readSeats(input.seats);
      var fillN = input.fill === "human" || input.fill === "ai" || input.fill === "either" ? input.fill : "";
      var diffN = input.difficulty || "medium";
      if (!gameN || !seatsN || !fillN || !difficultyOk(diffN, true)) return { error: "mode" };
      var slotsN = readSlotDifficulty(input.slot_difficulty, seatsN);
      if (slotsN === false) return { error: "mode" };
      var layoutN = layoutOf(input.layout, seatsN);
      var ticketN = {
        pid: pid,
        name: nameJoin,
        game: gameN,
        seats: seatsN,
        fill: fillN,
        difficulty: diffN,
        slot_difficulty: slotsN,
        layout: layoutN,
        since: now,
        seen: now,
        legacy: false
      };
      state.queue.push(ticketN);
      sweep(state, now);
      var nHit = answerMatch(state, pid);
      if (nHit) return nHit;
      return { status: "queued", wait: 0, queued: queuedCount(state, gameN) };
    }

    return { error: "op" };
  }

  function runSim() {
    var failures = [];
    var passed = 0;
    function check(name, cond) {
      if (!cond) failures.push(name);
      else {
        passed += 1;
        console.log("PASS " + name);
      }
    }
    function store() {
      return createStore({ frozen: true, now: 1700000000 });
    }
    function seat(match, role) {
      var found = null;
      match.seats.forEach(function (s) { if (s.role === role) found = s; });
      return found;
    }

    var caps = handle(store(), { op: "caps", pid: "p1" });
    check("caps n_player", caps.n_player === true && caps.fill_after_s === 8 && caps.max_seats === 8);
    check("caps skills", caps.difficulties.easy === 0.4 && caps.difficulties.medium === 0.58 && caps.difficulties.hard === 0.76);

    var s1 = store();
    var ai = handle(s1, { op: "join", pid: "host", game: "higher", name: "Ada", teammate: "ai", enemy: "ai" });
    check("legacy ai match", ai.status === "matched" && ai.match.seats.length === 4 && ai.match.legacy === true);
    check("legacy names", seat(ai.match, "teammate").name === "Librarian" && seat(ai.match, "enemy").name === "Sprinter" && seat(ai.match, "enemy2").name === "Novelist");
    check("legacy skills", seat(ai.match, "teammate").skill === 0.76 && seat(ai.match, "enemy").skill === 0.58 && seat(ai.match, "enemy2").skill === 0.4);
    check("legacy b2 ai", seat(ai.match, "enemy2").kind === "ai");

    var badGame = handle(store(), { op: "join", pid: "host", game: "c01", teammate: "ai", enemy: "ai" });
    check("legacy rejects c01", badGame.error === "mode");

    var s2 = store();
    var wait = handle(s2, { op: "join", pid: "a", game: "m01", name: "Ann", teammate: "either", enemy: "either" });
    check("legacy either waits", wait.status === "queued");
    s2.advance(8);
    var filled = handle(s2, { op: "poll", pid: "a" });
    check("legacy fill at 8s", filled.status === "matched" && seat(filled.match, "teammate").kind === "ai" && seat(filled.match, "enemy").kind === "ai");

    var s3 = store();
    handle(s3, { op: "join", pid: "a", game: "tiles", name: "Ann", teammate: "either", enemy: "either" });
    var pair = handle(s3, { op: "join", pid: "b", game: "tiles", name: "Bo", teammate: "either", enemy: "either" });
    check("legacy second player starts", pair.status === "matched");
    var viewA = handle(s3, { op: "poll", pid: "a" });
    check("legacy mate is ai when one rival arrives", seat(viewA.match, "teammate").kind === "ai" && seat(viewA.match, "enemy").kind === "human");

    var s4 = store();
    handle(s4, { op: "join", pid: "a", game: "derby", name: "Ann", teammate: "human", enemy: "human" });
    handle(s4, { op: "join", pid: "b", game: "derby", name: "Bo", teammate: "human", enemy: "human" });
    handle(s4, { op: "join", pid: "c", game: "derby", name: "Cy", teammate: "human", enemy: "human" });
    var three = handle(s4, { op: "poll", pid: "a" });
    var humanSeats = three.match.seats.filter(function (s) { return s.kind === "human"; }).length;
    check("legacy three humans still leave b2 ai", three.status === "matched" && humanSeats === 3 && seat(three.match, "enemy2").kind === "ai");

    var s5 = store();
    var nWait = handle(s5, {
      op: "join", pid: "a", game: "c01", name: "Ann", seats: 6, fill: "either", difficulty: "medium", layout: "ffa"
    });
    check("n-player accepts c01", nWait.status === "queued");
    handle(s5, { op: "join", pid: "b", game: "c01", name: "Bo", seats: 6, fill: "either", difficulty: "medium", layout: "ffa" });
    var early = handle(s5, { op: "poll", pid: "a" });
    check("n-player waits before timeout", early.status === "queued");
    s5.advance(8);
    var six = handle(s5, { op: "poll", pid: "a" });
    var sixHumans = six.match.seats.filter(function (s) { return s.kind === "human"; }).length;
    var sixAi = six.match.seats.filter(function (s) { return s.kind === "ai"; }).length;
    check("n-player timeout fills to 6", six.status === "matched" && six.match.seats_n === 6 && sixHumans === 2 && sixAi === 4);

    var s6 = store();
    var ids = ["a", "b", "c", "d"];
    var last;
    ids.forEach(function (id) {
      last = handle(s6, {
        op: "join", pid: id, game: "m01", name: id, seats: 4, fill: "human", difficulty: "medium", layout: "2v2"
      });
    });
    check("all-human 2v2", last.status === "matched" && last.match.seats.every(function (s) { return s.kind === "human"; }));
    check("all-human keeps role names", seat(last.match, "you") && seat(last.match, "teammate") && seat(last.match, "enemy") && seat(last.match, "enemy2"));

    var s7 = store();
    var solo = handle(s7, {
      op: "join",
      pid: "a",
      game: "s01",
      name: "Ann",
      seats: 3,
      fill: "ai",
      difficulty: "hard",
      slot_difficulty: ["", "easy", "hard"]
    });
    check("all-ai starts now", solo.status === "matched" && solo.match.seats.length === 3);
    var aiSeats = solo.match.seats.filter(function (s) { return s.kind === "ai"; });
    check("per-slot difficulty", aiSeats.length === 2 && aiSeats[0].difficulty === "easy" && aiSeats[0].skill === 0.4 && aiSeats[1].difficulty === "hard" && aiSeats[1].skill === 0.76);

    var s8 = store();
    handle(s8, { op: "join", pid: "a", game: "m01", name: "Ann", seats: 2, fill: "either", difficulty: "medium" });
    var other = handle(s8, { op: "join", pid: "b", game: "m15", name: "Bo", seats: 2, fill: "either", difficulty: "medium" });
    check("different games stay apart", other.status === "queued");

    var s9 = store();
    var opened = handle(s9, {
      op: "lobby_open", pid: "host", game: "m30", name: "Ann", seats: 3, fill: "either", difficulty: "legacy", layout: "ffa"
    });
    check("lobby opens with code", opened.status === "lobby" && opened.code.length === 4 && opened.have === 1);
    var guest = handle(s9, { op: "lobby_join", pid: "guest", code: opened.code, name: "Bo" });
    check("lobby guest waits", guest.status === "lobby" && guest.have === 2);
    s9.advance(8);
    var roomMatch = handle(s9, { op: "lobby_poll", pid: "host" });
    check("lobby timeout fills the open seat", roomMatch.status === "matched" && roomMatch.match.seats.filter(function (s) { return s.kind === "ai"; }).length === 1);

    var s10 = store();
    var humanRoom = handle(s10, {
      op: "lobby_open", pid: "host", game: "m50", name: "Ann", seats: 2, fill: "human", difficulty: "medium"
    });
    s10.advance(8);
    var held = handle(s10, { op: "lobby_poll", pid: "host" });
    check("all-human lobby ignores the fill clock", held.status === "lobby" && held.have === 1);
    var both = handle(s10, { op: "lobby_join", pid: "guest", code: humanRoom.code, name: "Bo" });
    check("all-human lobby starts when full", both.status === "matched" && both.match.seats.every(function (s) { return s.kind === "human"; }));

    var s11 = store();
    var made = handle(s11, { op: "join", pid: "a", game: "higher", name: "Ada", teammate: "ai", enemy: "ai" });
    var moved = handle(s11, { op: "move", pid: "a", match: made.match.id, round: 1, pick: "higher" });
    check("move lands on the match", moved.status === "ok" && moved.match.moves["1"].a === "higher");

    var s12 = store();
    handle(s12, { op: "join", pid: "a", game: "m01", name: "Ann", seats: 4, fill: "human", difficulty: "medium" });
    var left = handle(s12, { op: "leave", pid: "a" });
    var gone = handle(s12, { op: "poll", pid: "a" });
    check("leave drops the ticket", left.status === "left" && gone.status === "none");

    check("pid required", handle(store(), { op: "join", game: "m01" }).error === "pid");
    check("seats 9 rejected", handle(store(), { op: "join", pid: "a", game: "m01", seats: 9, fill: "ai" }).error === "mode");
    check("seats 1 rejected", handle(store(), { op: "join", pid: "a", game: "m01", seats: 1, fill: "ai" }).error === "mode");

    var s13 = store();
    var saved = handle(s13, { op: "save", pid: "a", record: { game: "m01", event: "arcade", outcome: { result: "ok" } } });
    check("save stays in memory", saved.status === "saved" && s13.saves.length === 1 && s13.saves[0].game === "m01");

    var s14 = store();
    var legacyTable = handle(s14, {
      op: "join", pid: "a", game: "m01", name: "Ann", seats: 4, fill: "ai", difficulty: "legacy", layout: "2v2"
    });
    check("legacy difficulty names", seat(legacyTable.match, "teammate").name === "Librarian" && seat(legacyTable.match, "enemy2").skill === 0.4);

    var s15 = store();
    handle(s15, { op: "join", pid: "a", game: "s50", name: "Ann", seats: 3, fill: "either", difficulty: "medium" });
    handle(s15, { op: "join", pid: "b", game: "s50", name: "Bo", seats: 3, fill: "human", difficulty: "medium" });
    s15.advance(8);
    var eitherSide = handle(s15, { op: "poll", pid: "a" });
    var humanSide = handle(s15, { op: "poll", pid: "b" });
    var eitherHumans = eitherSide.match && eitherSide.match.seats.filter(function (s) { return s.kind === "human"; }).length;
    check("either timeout does not consume a human-only ticket", eitherSide.status === "matched" && eitherHumans === 1 && humanSide.status === "queued");

    if (failures.length) {
      console.log("FAIL " + failures.length);
      failures.forEach(function (name) { console.log("FAIL " + name); });
      if (typeof process !== "undefined" && process.exitCode !== undefined) process.exitCode = 1;
      return { ok: false, failures: failures };
    }
    console.log("SIM_OK " + passed);
    return { ok: true, failures: [] };
  }

  return {
    createStore: createStore,
    handle: handle,
    runSim: runSim,
    publicMatch: publicMatch,
    FILL_AFTER_S: FILL_AFTER_S,
    TICKET_TTL_S: TICKET_TTL_S,
    MATCH_TTL_S: MATCH_TTL_S,
    MIN_SEATS: MIN_SEATS,
    MAX_SEATS: MAX_SEATS,
    SKILL: SKILL,
    AI_NAMES: AI_NAMES,
    LEGACY_AI: LEGACY_AI
  };
});
