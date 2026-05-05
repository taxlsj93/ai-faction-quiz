const C = require('../shared/constants.js');
const { hexNeighbors, hexesInRange } = require('../shared/hexMath.js');

// Returns { ok, error } — pure validation, no side effects on state
function validateAbilityUse(ability, userId, state, extra = {}) {
  const user = state.users[userId];
  if (!user || user.isEliminated) return { ok: false, error: 'eliminated' };

  switch (ability) {
    case C.ABILITIES.APPLE_DROP: {
      const { targetUserId, amount } = extra;
      if (user.faction !== 'orchard') return { ok: false, error: 'wrong-faction' };
      const target = state.users[targetUserId];
      if (!target || target.faction !== 'orchard') return { ok: false, error: 'invalid-target' };
      if (state.factions.orchard.sharedResource < amount) return { ok: false, error: 'insufficient-resource' };
      return { ok: true };
    }

    case C.ABILITIES.APPLE_FACE: {
      if (user.faction !== 'orchard') return { ok: false, error: 'wrong-faction' };
      if (state.factions.orchard.appleFaceUsed) return { ok: false, error: 'already-used' };
      return { ok: true };
    }

    case C.ABILITIES.STAR_PAY: {
      if (user.ability !== C.ABILITIES.STAR_PAY) return { ok: false, error: 'not-equipped' };
      const { q, r } = extra;
      const hex = getHex(state, q, r);
      if (!hex || hex.owner !== null) return { ok: false, error: 'hex-not-neutral' };
      return { ok: true };
    }

    case C.ABILITIES.MOON_SHOT: {
      if (user.ability !== C.ABILITIES.MOON_SHOT) return { ok: false, error: 'not-equipped' };
      return { ok: true };
    }

    case C.ABILITIES.MAGIC_CIRCLE: {
      if (user.ability !== C.ABILITIES.MAGIC_CIRCLE) return { ok: false, error: 'not-equipped' };
      return { ok: true };
    }

    default:
      return { ok: false, error: 'unknown-ability' };
  }
}

// Apply ability effects — mutates state, returns event list for broadcast
function applyAbility(ability, userId, state, extra = {}) {
  const events = [];
  const user = state.users[userId];

  switch (ability) {
    case C.ABILITIES.APPLE_DROP: {
      const { amount } = extra;
      const capped = Math.min(amount, 10);
      state.factions.orchard.sharedResource = +(state.factions.orchard.sharedResource - capped).toFixed(1);
      events.push({ type: 'appleDrop', from: userId, amount: capped });
      break;
    }

    case C.ABILITIES.APPLE_FACE: {
      state.factions.orchard.appleFaceUsed = true;
      state.factions.orchard.appleFaceCharges = 2;
      events.push({ type: 'appleFace', active: true });
      break;
    }

    case C.ABILITIES.STAR_PAY: {
      const { q, r } = extra;
      const hex = getHex(state, q, r);
      if (hex) {
        hex.owner = userId;
        hex.faction = 'jungle';
        hex.strength = 1;
        user.territoryCount = (user.territoryCount || 0) + 1;
        state.factions.jungle.territoryCount++;
        const key = `${q},${r}`;
        if (!state.changes) state.changes = [];
        state.changes.push(key);
        events.push({ type: 'starPay', userId, q, r });
      }
      break;
    }

    case C.ABILITIES.MOON_SHOT: {
      // Reveal all hex info in entire map for this user (sent privately)
      events.push({ type: 'moonShot', userId, reveal: 'all' });
      break;
    }

    case C.ABILITIES.MAGIC_CIRCLE: {
      const { q, r, range = 3 } = extra;
      const revealed = hexesInRange(q, r, range).map(({ q: hq, r: hr }) => {
        const h = getHex(state, hq, hr);
        return h ? { q: hq, r: hr, owner: h.owner, faction: h.faction, strength: h.strength } : null;
      }).filter(Boolean);
      events.push({ type: 'magicCircle', userId, revealed });
      break;
    }
  }

  return events;
}

// Passive ability effects applied during tick
function applyPassives(state) {
  for (const [userId, user] of Object.entries(state.users)) {
    if (user.isEliminated || user.faction !== 'jungle') continue;

    // RedBatt: auto cost reduction when resource <= 20
    if (user.ability === C.ABILITIES.RED_BATT && !user.redBattActive) {
      user.redBattActive = user.resource <= 20;
    } else if (user.redBattActive && user.resource > 20) {
      user.redBattActive = false;
    }
  }

  // EcosystemLock (BlueBubble passive): Orchard connected clusters >= 5 get border strength +1
  applyBlueBubble(state);
}

function applyBlueBubble(state) {
  // Reset all bonuses before recomputing
  for (const hex of Object.values(state.hexes)) {
    hex.blueBubbleBonus = false;
  }
  const orchardHexes = Object.values(state.hexes).filter(h => h.faction === 'orchard');
  const visited = new Set();
  for (const hex of orchardHexes) {
    const key = `${hex.q},${hex.r}`;
    if (visited.has(key)) continue;
    const cluster = floodFill(state, hex.q, hex.r, 'orchard', visited);
    if (cluster.length >= 5) {
      for (const h of cluster) {
        if (h.strength < C.MAX_STRENGTH) h.blueBubbleBonus = true;
      }
    }
  }
}

function floodFill(state, startQ, startR, faction, visited) {
  const startKey = `${startQ},${startR}`;
  const startHex = getHex(state, startQ, startR);
  if (!startHex || startHex.faction !== faction) return [];
  const queue = [startHex];
  const cluster = [];
  visited.add(startKey);
  while (queue.length > 0) {
    const hex = queue.shift();
    cluster.push(hex);
    for (const n of hexNeighbors(hex.q, hex.r)) {
      const key = `${n.q},${n.r}`;
      if (visited.has(key)) continue;
      const nh = getHex(state, n.q, n.r);
      if (!nh || nh.faction !== faction) continue;
      visited.add(key);
      queue.push(nh);
    }
  }
  return cluster;
}

function getHex(state, q, r) {
  return state.hexes[`${q},${r}`] || null;
}

// Cost modifier for a user's action considering abilities + Final Rush
function getActionCost(baseCost, actionType, userId, state) {
  const user = state.users[userId];
  let cost = baseCost;

  if (state.finalRush) cost = +(cost * C.RUSH.costMultiplier).toFixed(1);

  if (user.faction === 'jungle') {
    if (user.redBattActive) cost = +(cost * 0.7).toFixed(1);
  }

  return Math.max(0, cost);
}

function getGatherAmount(userId, state) {
  const user = state.users[userId];
  if (user.faction === 'orchard') return C.GATHER.orchard;
  return C.GATHER.jungle;
}

module.exports = { validateAbilityUse, applyAbility, applyPassives, getActionCost, getGatherAmount };
