window.LMN_PACK = window.LMN_PACK || [];
window.LMN_PACK.push({
  id: "t901",
  title: "LLM Chess",
  players: "multi",
  engine: "chess",
  settings: {
    minPlayers: 2,
    maxPlayers: 2,
    mode: "human_llm",
    page: "chess/index.html",
    rules: "chess/chess_rules.js",
    note: "Rules live in site_new/chess/chess_rules.js. engines.js has no chess branch, so the current arcade falls through to idle for engine chess. Play chess/index.html. Local mock only."
  },
  blurb: "After Chess"
});
window.LMN_PACK.push({
  id: "t902",
  title: "Agent Chess Match",
  players: "multi",
  engine: "chess",
  settings: {
    minPlayers: 2,
    maxPlayers: 2,
    mode: "agent_agent",
    page: "chess/index.html",
    spectators: "play-money-mock",
    note: "Two local mocks. Bets are play-money on this page. Not TokenCTR."
  },
  blurb: "After Chess"
});
window.LMN_PACK.push({
  id: "t903",
  title: "Hotseat Chess",
  players: "multi",
  engine: "chess",
  settings: {
    minPlayers: 2,
    maxPlayers: 2,
    mode: "hotseat",
    page: "chess/index.html",
    note: "Two humans, one device. Works in the browser now."
  },
  blurb: "After Chess"
});
window.LMN_PACK.push({
  id: "t904",
  title: "Lobby Chess",
  players: "multi",
  engine: "chess",
  settings: {
    minPlayers: 2,
    maxPlayers: 2,
    mode: "lobby",
    page: "chess/index.html",
    hook: "chess/LOBBY_HOOK.md",
    note: "Uses site_new/lobby_new.js when that file sets LMN_MOUNT_LOBBY. queue.php accepts higher, tiles, derby, and ^[sm][0-9]{2}$ only, so t904 does not match on the live queue."
  },
  blurb: "After Chess"
});
