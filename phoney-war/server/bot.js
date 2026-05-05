const { addUser, processAction } = require('./gameState.js');
const { hexNeighbors } = require('../shared/hexMath.js');

const BOT_ORCHARD_PREFIX = 'bot-orchard-';
const BOT_JUNGLE_PREFIX  = 'bot-jungle-';
const BOT_THINK_MS = 1800;

// Keep for backwards compat
const BOT_ID = BOT_ORCHARD_PREFIX + '1';

function makeBotId(faction, index) {
  return (faction === 'orchard' ? BOT_ORCHARD_PREFIX : BOT_JUNGLE_PREFIX) + index;
}

function isBot(userId) {
  return userId.startsWith(BOT_ORCHARD_PREFIX) || userId.startsWith(BOT_JUNGLE_PREFIX);
}

// Fill each side up to targetPerSide with bots
function fillBots(session, io, targetPerSide = 5) {
  if (session._botInterval) return; // already running
  const { state } = session;

  const orchardCount = Object.values(state.users).filter(u => u.faction === 'orchard').length;
  const jungleCount  = Object.values(state.users).filter(u => u.faction === 'jungle').length;

  const orchardBots = Math.max(0, targetPerSide - orchardCount);
  const jungleBots  = Math.max(0, targetPerSide - jungleCount);

  for (let i = 0; i < orchardBots; i++) {
    const botId = makeBotId('orchard', orchardCount + i + 1);
    if (!state.users[botId]) {
      addUser(state, botId, 'orchard', null);
      console.log(`[bot] Orchard bot spawned: ${botId}`);
    }
  }

  for (let i = 0; i < jungleBots; i++) {
    const botId = makeBotId('jungle', jungleCount + i + 1);
    if (!state.users[botId]) {
      addUser(state, botId, 'jungle', null);
      console.log(`[bot] Jungle bot spawned: ${botId}`);
    }
  }

  // Start AI loop for all bots
  const interval = setInterval(() => {
    if (!state.running || state.winner) { clearInterval(interval); return; }
    for (const user of Object.values(state.users)) {
      if (isBot(user.id) && !user.isEliminated) {
        botThink(state, user.id, user.faction);
      }
    }
  }, BOT_THINK_MS);

  session._botInterval = interval;
}

// Legacy single-bot spawn (still used if called directly)
function spawnOrcardBot(session, io) {
  fillBots(session, io, 1);
}

function botThink(state, botId, faction) {
  if (faction === 'orchard') {
    orchardBotThink(state, botId);
  } else {
    jungleBotThink(state, botId);
  }
}

// ── ORCHARD BOT ───────────────────────────────────────────────

function orchardBotThink(state, botId) {
  const res = state.factions.orchard.sharedResource;
  const myHexes = Object.values(state.hexes).filter(h => h.faction === 'orchard');
  if (!myHexes.length) return;

  if (res >= 8) {
    const target = findAdjacentEnemy(state, myHexes, 'orchard');
    if (target) {
      const r = processAction(state, botId, 'attack', target.q, target.r);
      if (r.success) return;
    }
  }

  if (res >= 3) {
    const target = findAdjacentEmpty(state, myHexes);
    if (target) {
      const r = processAction(state, botId, 'expand', target.q, target.r);
      if (r.success) return;
    }
  }
}

// ── JUNGLE BOT ────────────────────────────────────────────────

function jungleBotThink(state, botId) {
  const user = state.users[botId];
  if (!user) return;
  const res = user.resource;
  const myHexes = Object.values(state.hexes).filter(h => h.owner === botId);
  if (!myHexes.length) return;

  if (res >= 8) {
    const target = findAdjacentEnemy(state, myHexes, 'jungle');
    if (target) {
      const r = processAction(state, botId, 'attack', target.q, target.r);
      if (r.success) return;
    }
  }

  if (res >= 3) {
    const target = findAdjacentEmpty(state, myHexes);
    if (target) {
      const r = processAction(state, botId, 'expand', target.q, target.r);
      if (r.success) return;
    }
  }
}

// ── HELPERS ───────────────────────────────────────────────────

function findAdjacentEnemy(state, myHexes, myFaction) {
  const candidates = [];
  for (const hex of myHexes) {
    for (const n of hexNeighbors(hex.q, hex.r)) {
      const nh = state.hexes[`${n.q},${n.r}`];
      if (nh && nh.faction && nh.faction !== myFaction) candidates.push(nh);
    }
  }
  if (!candidates.length) return null;
  return candidates.sort((a, b) => a.strength - b.strength)[0];
}

function findAdjacentEmpty(state, myHexes) {
  const seen = new Set();
  const candidates = [];
  for (const hex of myHexes) {
    for (const n of hexNeighbors(hex.q, hex.r)) {
      const key = `${n.q},${n.r}`;
      if (seen.has(key)) continue;
      seen.add(key);
      const nh = state.hexes[key];
      if (nh && !nh.faction) candidates.push(nh);
    }
  }
  if (!candidates.length) return null;
  return candidates[Math.floor(Math.random() * candidates.length)];
}

module.exports = { fillBots, spawnOrcardBot, BOT_ID, isBot };
