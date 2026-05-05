const C = require('../shared/constants.js');
const { hexNeighbors } = require('../shared/hexMath.js');
const { applyPassives, getActionCost, getGatherAmount } = require('./abilities.js');

function createHexKey(q, r) { return `${q},${r}`; }
function getHex(state, q, r) { return state.hexes[createHexKey(q, r)] || null; }

function buildMap(sizeName) {
  const size = C.MAP_SIZES[sizeName] || C.MAP_SIZES[C.DEFAULT_MAP_SIZE];
  const hexes = {};
  for (let r = 0; r < size.rows; r++) {
    for (let q = 0; q < size.cols; q++) {
      const offset = Math.floor(r / 2);
      const adjQ = q - offset;
      const key = createHexKey(adjQ, r);
      hexes[key] = { q: adjQ, r, owner: null, faction: null, strength: 1, isHQ: false };
    }
  }
  return { hexes, cols: size.cols, rows: size.rows };
}

function createGameState(sessionId) {
  const { hexes, cols, rows } = buildMap(C.DEFAULT_MAP_SIZE);
  return {
    sessionId,
    hexes,
    cols,
    rows,
    users: {},      // userId → userObj
    factions: {
      orchard: { sharedResource: C.START_RESOURCE, territoryCount: 0, appleFaceUsed: false, appleFaceCharges: 0, unlockedSkills: [] },
      jungle:  { territoryCount: 0, activeUsers: [] },
    },
    tickCount: 0,
    timeRemaining: C.SESSION_DURATION,
    finalRush: false,
    running: false,
    winner: null,
    changes: [],    // hex keys changed this tick (for delta broadcast)
  };
}

function addUser(state, userId, faction, abilityChoice) {
  const isOrchard = faction === 'orchard';
  state.users[userId] = {
    id: userId,
    faction,
    resource: isOrchard ? 0 : C.START_RESOURCE,
    hq: null,
    isEliminated: false,
    territoryCount: 0,
    ability: isOrchard ? null : (abilityChoice || null),
    redBattActive: false,
    cooldowns: {},
  };

  if (faction === 'jungle') {
    state.users[userId].unlockedSlots = 0;
    state.factions.jungle.activeUsers.push(userId);
  }

  placeHQ(state, userId, faction);
  return state.users[userId];
}

function placeHQ(state, userId, faction) {
  const allHexes = Object.values(state.hexes);

  // Compute q range once to place HQs at true opposite ends (left 12% / right 12%)
  const qs = allHexes.map(h => h.q);
  const qMin = Math.min(...qs);
  const qMax = Math.max(...qs);
  const qSpan = qMax - qMin;
  const leftThreshold  = qMin + qSpan * 0.12;
  const rightThreshold = qMax - qSpan * 0.12;

  if (faction === 'orchard') {
    // Orchard: single HQ at extreme left, vertically centered
    const candidates = allHexes
      .filter(h => h.q <= leftThreshold && !h.isHQ && !h.owner)
      .sort((a, b) => Math.abs(a.r - state.rows / 2) - Math.abs(b.r - state.rows / 2));
    const hex = candidates[0] || allHexes.find(h => !h.isHQ);
    if (hex) {
      hex.owner = 'orchard';
      hex.faction = 'orchard';
      hex.isHQ = true;
      hex.strength = 5;
      state.factions.orchard.territoryCount++;
      claimStarterRing(state, hex, 'orchard', null);
    }
    return;
  }

  // Jungle: each HQ at extreme right, evenly spread vertically
  const jungleCount = state.factions.jungle.activeUsers.length;
  const candidates = allHexes
    .filter(h => h.q >= rightThreshold && !h.isHQ && !h.owner)
    .sort((a, b) => a.r - b.r);
  const step = Math.max(1, Math.floor(candidates.length / 6));
  const idx  = ((jungleCount - 1) * step) % Math.max(candidates.length, 1);
  const hex  = candidates[idx] || allHexes.find(h => !h.isHQ && !h.owner);
  if (hex) {
    hex.owner = userId;
    hex.faction = 'jungle';
    hex.isHQ = true;
    hex.strength = 5;
    state.users[userId].hq = { q: hex.q, r: hex.r };
    state.users[userId].territoryCount = 1;
    state.factions.jungle.territoryCount++;
    claimStarterRing(state, hex, 'jungle', userId);
  }
}

function claimStarterRing(state, hqHex, faction, userId) {
  const neighbors = hexNeighbors(hqHex.q, hqHex.r);
  for (const n of neighbors) {
    const nh = getHex(state, n.q, n.r);
    if (!nh || nh.owner !== null) continue;
    nh.owner = userId || 'orchard';
    nh.faction = faction;
    nh.strength = 1;
    if (faction === 'orchard') {
      state.factions.orchard.territoryCount++;
    } else {
      state.users[userId].territoryCount++;
      state.factions.jungle.territoryCount++;
    }
  }
}

// ── ACTION PROCESSING ──────────────────────────────────────────

function processAction(state, userId, type, q, r) {
  const user = state.users[userId];
  if (!user || user.isEliminated) return { success: false, error: 'eliminated' };

  const hex = getHex(state, q, r);
  if (!hex) return { success: false, error: 'invalid-hex' };

  switch (type) {
    case 'expand': return doExpand(state, user, hex);
    case 'attack': return doAttack(state, user, hex);
    default: return { success: false, error: 'unknown-action' };
  }
}

function doGather(state, user, hex) {
  if (user.faction === 'orchard') {
    // Orchard can gather on any Orchard hex
    if (hex.faction !== 'orchard') return { success: false, error: 'not-orchard-hex' };
    const gain = getGatherAmount(user.id, state);
    state.factions.orchard.sharedResource = +(state.factions.orchard.sharedResource + gain).toFixed(1);
    return { success: true, gain };
  }

  // Jungle: own hex only
  if (hex.owner !== user.id) return { success: false, error: 'not-own-hex' };
  const gain = getGatherAmount(user.id, state);

  // TwoScreen: gather from 2 adjacent own hexes simultaneously
  if (user.ability === C.ABILITIES.TWO_SCREEN) {
    const neighbors = hexNeighbors(hex.q, hex.r);
    const ownNeighbor = neighbors.find(n => {
      const nh = getHex(state, n.q, n.r);
      return nh && nh.owner === user.id;
    });
    if (ownNeighbor) {
      user.resource = +(user.resource + gain * 2).toFixed(1);
      return { success: true, gain: gain * 2, twoScreen: true };
    }
  }

  user.resource = +(user.resource + gain).toFixed(1);
  return { success: true, gain };
}

function doExpand(state, user, hex) {
  if (hex.owner !== null) return { success: false, error: 'hex-occupied' };

  if (!isAdjacentToFaction(state, hex, user)) {
    return { success: false, error: 'not-adjacent' };
  }

  let cost = getActionCost(C.COST.expand, 'expand', user.id, state);

  // canopy: Orchard expand -1
  if (user.faction === 'orchard' && state.factions.orchard.unlockedSkills.includes('canopy')) {
    cost = Math.max(0, cost - 1);
  }
  // slot 3: Jungle expand -1
  if (user.faction === 'jungle' && user.unlockedSlots >= 3) {
    cost = Math.max(0, cost - 1);
  }

  if (user.faction === 'orchard') {
    if (state.factions.orchard.sharedResource < cost) return { success: false, error: 'insufficient-resource' };
    state.factions.orchard.sharedResource = +(state.factions.orchard.sharedResource - cost).toFixed(1);
  } else {
    if (user.resource < cost) return { success: false, error: 'insufficient-resource' };
    user.resource = +(user.resource - cost).toFixed(1);
  }

  hex.owner = user.faction === 'orchard' ? 'orchard' : user.id;
  hex.faction = user.faction;
  hex.strength = 1;

  // StarPen or overgrowth/slot5: new hexes get strength 2
  if (user.ability === C.ABILITIES.STAR_PEN) {
    hex.strength = 2;
  } else if (user.faction === 'orchard' && state.factions.orchard.unlockedSkills.includes('overgrowth')) {
    hex.strength = 2;
  } else if (user.faction === 'jungle' && user.unlockedSlots >= 5) {
    hex.strength = 2;
  }

  updateTerritoryCount(state, user);
  state.changes.push(createHexKey(hex.q, hex.r));

  return { success: true };
}

function doAttack(state, user, hex) {
  // Jungle cannot attack other Jungle
  if (user.faction === 'jungle' && hex.faction === 'jungle') {
    return { success: false, error: 'cannot-attack-jungle' };
  }
  // Must attack enemy faction
  if (hex.faction === user.faction || hex.faction === null) {
    return { success: false, error: 'invalid-attack-target' };
  }
  if (!isAdjacentToFaction(state, hex, user)) {
    return { success: false, error: 'not-adjacent' };
  }

  let cost = getActionCost(C.COST.attack, 'attack', user.id, state);

  // ecoLock: Jungle attacks on Orchard hexes cost +2
  if (user.faction === 'jungle' && hex.faction === 'orchard' &&
      state.factions.orchard.unlockedSkills.includes('ecoLock')) {
    cost = +(cost + 2).toFixed(1);
  }

  if (user.faction === 'orchard') {
    if (state.factions.orchard.sharedResource < cost) return { success: false, error: 'insufficient-resource' };
    state.factions.orchard.sharedResource = +(state.factions.orchard.sharedResource - cost).toFixed(1);
  } else {
    if (user.resource < cost) return { success: false, error: 'insufficient-resource' };
    user.resource = +(user.resource - cost).toFixed(1);
  }

  let damage = 1 + (state.finalRush ? C.RUSH.attackBonus : 0);
  // Jungle slot 2: attack damage +1
  if (user.faction === 'jungle' && user.unlockedSlots >= 2) damage += 1;

  // AppleFace: block first 2 attacks on Orchard HQ
  if (hex.isHQ && hex.faction === 'orchard' && state.factions.orchard.appleFaceCharges > 0) {
    state.factions.orchard.appleFaceCharges--;
    return { success: true, blocked: true };
  }

  hex.strength -= damage;
  state.changes.push(createHexKey(hex.q, hex.r));

  if (hex.strength <= 0) {
    return captureHex(state, user, hex);
  }

  return { success: true };
}

function captureHex(state, user, hex) {
  const wasHQ = hex.isHQ;
  const prevFaction = hex.faction;
  const prevOwner = hex.owner;

  // Decrement previous owner's count
  decrementTerritory(state, prevFaction, prevOwner);

  if (wasHQ) {
    if (prevFaction === 'orchard') {
      // Orchard HQ captured → Jungle wins immediately
      return { success: true, sessionEnd: { winner: 'jungle', reason: 'hq-captured' } };
    } else {
      // Jungle player HQ captured → that player eliminated
      const eliminatedUser = state.users[prevOwner];
      if (eliminatedUser) {
        eliminatedUser.isEliminated = true;
        state.factions.jungle.activeUsers = state.factions.jungle.activeUsers.filter(id => id !== prevOwner);
      }
      // HQ becomes Orchard territory
      hex.owner = 'orchard';
      hex.faction = 'orchard';
      hex.isHQ = false;
      hex.strength = 1;
      state.factions.orchard.territoryCount++;

      // Check if all Jungle eliminated
      if (state.factions.jungle.activeUsers.length === 0) {
        return { success: true, sessionEnd: { winner: 'orchard', reason: 'all-jungle-eliminated' } };
      }
      return { success: true, eliminated: prevOwner };
    }
  }

  // Normal hex capture
  hex.owner = user.faction === 'orchard' ? 'orchard' : user.id;
  hex.faction = user.faction;
  hex.strength = 1;
  if (user.ability === C.ABILITIES.STAR_PEN) {
    hex.strength = 2;
  } else if (user.faction === 'orchard' && state.factions.orchard.unlockedSkills.includes('overgrowth')) {
    hex.strength = 2;
  } else if (user.faction === 'jungle' && user.unlockedSlots >= 5) {
    hex.strength = 2;
  }
  updateTerritoryCount(state, user);

  return { success: true };
}

// ── TICK ──────────────────────────────────────────────────────

function tick(state) {
  if (!state.running) return;

  state.tickCount++;
  state.timeRemaining = Math.max(0, state.timeRemaining - C.TICK_MS / 1000);
  state.changes = [];

  // Final Rush trigger (scenario override via state._finalRushAt)
  const finalRushAt = state._finalRushAt !== undefined ? state._finalRushAt : C.FINAL_RUSH_AT;
  if (!state.finalRush && state.timeRemaining <= finalRushAt) {
    state.finalRush = true;
  }

  // Passive income
  const orchardHexCount = Object.values(state.hexes).filter(h => h.faction === 'orchard').length;
  const orchardIncomePerHex = C.INCOME_PER_HEX +
    (state.factions.orchard.unlockedSkills.includes('deepRoots') ? 0.1 : 0);
  state.factions.orchard.sharedResource = +(
    state.factions.orchard.sharedResource + orchardHexCount * orchardIncomePerHex
  ).toFixed(1);

  for (const [userId, user] of Object.entries(state.users)) {
    if (user.isEliminated || user.faction !== 'jungle') continue;
    const hexCount = Object.values(state.hexes).filter(h => h.owner === userId).length;
    let income = hexCount * C.INCOME_PER_HEX;
    if (user.unlockedSlots >= 4) income *= 2;        // slot 4: ×2 (replaces slot 1)
    else if (user.unlockedSlots >= 1) income *= 1.5; // slot 1: ×1.5
    user.resource = +(user.resource + income).toFixed(1);
  }

  // Underdog bonus: weak side gets +20% income when opponent holds ≥60% of territory
  const totalHexes = Object.keys(state.hexes).length;
  const orchardPct = totalHexes > 0 ? state.factions.orchard.territoryCount / totalHexes : 0;
  const junglePct  = totalHexes > 0 ? state.factions.jungle.territoryCount  / totalHexes : 0;
  if (orchardPct >= 0.6) {
    for (const user of Object.values(state.users)) {
      if (user.faction === 'jungle' && !user.isEliminated)
        user.resource = +(user.resource * 1.2).toFixed(1);
    }
  } else if (junglePct >= 0.6) {
    state.factions.orchard.sharedResource = +(state.factions.orchard.sharedResource * 1.2).toFixed(1);
  }

  // Resource cap (스노볼 방지)
  if (state.factions.orchard.sharedResource > C.RESOURCE_CAP.orchard)
    state.factions.orchard.sharedResource = C.RESOURCE_CAP.orchard;
  for (const user of Object.values(state.users)) {
    if (user.faction === 'jungle' && user.resource > C.RESOURCE_CAP.jungle)
      user.resource = C.RESOURCE_CAP.jungle;
  }

  // Passive abilities
  applyPassives(state);

  // Session end by timer
  if (state.timeRemaining <= 0) {
    state.running = false;
    const winner = calcWinner(state);
    state.winner = winner;
    return { sessionEnd: { winner, reason: 'timer', finalStats: buildFinalStats(state) } };
  }

  return null;
}

// ── HELPERS ──────────────────────────────────────────────────

function isAdjacentToFaction(state, hex, user) {
  const neighbors = hexNeighbors(hex.q, hex.r);
  return neighbors.some(n => {
    const nh = getHex(state, n.q, n.r);
    if (!nh) return false;
    if (user.faction === 'orchard') return nh.faction === 'orchard';
    return nh.owner === user.id;
  });
}

function updateTerritoryCount(state, user) {
  if (user.faction === 'orchard') {
    state.factions.orchard.territoryCount = Object.values(state.hexes)
      .filter(h => h.faction === 'orchard').length;
  } else {
    user.territoryCount = Object.values(state.hexes)
      .filter(h => h.owner === user.id).length;
    state.factions.jungle.territoryCount = Object.values(state.hexes)
      .filter(h => h.faction === 'jungle').length;
  }
}

function decrementTerritory(state, faction, owner) {
  if (faction === 'orchard') {
    state.factions.orchard.territoryCount = Math.max(0, state.factions.orchard.territoryCount - 1);
  } else if (owner && state.users[owner]) {
    state.users[owner].territoryCount = Math.max(0, (state.users[owner].territoryCount || 1) - 1);
    state.factions.jungle.territoryCount = Math.max(0, state.factions.jungle.territoryCount - 1);
  }
}

function calcWinner(state) {
  const orchardPct = state.factions.orchard.territoryCount;
  const junglePct = state.factions.jungle.territoryCount;
  return orchardPct >= junglePct ? 'orchard' : 'jungle';
}

function buildFinalStats(state) {
  const total = Object.keys(state.hexes).length;
  return {
    orchardTerritory: state.factions.orchard.territoryCount,
    jungleTerritory: state.factions.jungle.territoryCount,
    totalHexes: total,
    orchardPct: Math.round(state.factions.orchard.territoryCount / total * 100),
    junglePct: Math.round(state.factions.jungle.territoryCount / total * 100),
  };
}

function buildSnapshot(state) {
  return {
    hexes: state.hexes,
    factions: state.factions,
    users: Object.fromEntries(
      Object.entries(state.users).map(([id, u]) => [id, {
        id: u.id, faction: u.faction, resource: u.resource,
        isEliminated: u.isEliminated, ability: u.ability,
        territoryCount: u.territoryCount, hq: u.hq,
        unlockedSlots: u.unlockedSlots || 0,
      }])
    ),
    timeRemaining: state.timeRemaining,
    finalRush: state.finalRush,
  };
}

function buildDelta(state) {
  const changedHexes = {};
  for (const key of state.changes) {
    changedHexes[key] = state.hexes[key];
  }
  return {
    changes: changedHexes,
    resourcePatch: {
      orchard: state.factions.orchard.sharedResource,
      orchardTerritory: state.factions.orchard.territoryCount,
      orchardSkills: state.factions.orchard.unlockedSkills,
      jungleTerritory: state.factions.jungle.territoryCount,
      jungle: Object.fromEntries(
        Object.entries(state.users)
          .filter(([, u]) => u.faction === 'jungle' && !u.isEliminated)
          .map(([id, u]) => [id, { resource: u.resource, territoryCount: u.territoryCount, unlockedSlots: u.unlockedSlots || 0 }])
      ),
    },
    timeRemaining: state.timeRemaining,
    finalRush: state.finalRush,
    timestamp: Date.now(),
  };
}

module.exports = {
  createGameState, addUser, processAction, tick,
  buildSnapshot, buildDelta, getHex,
};
