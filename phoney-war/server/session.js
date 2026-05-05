const { createGameState, addUser, processAction, tick, buildSnapshot, buildDelta } = require('./gameState.js');
const { detectFaction } = require('./deviceDetect.js');
const { fillBots, BOT_ID, isBot } = require('./bot.js');
const C = require('../shared/constants.js');
const { validateAbilityUse, applyAbility } = require('./abilities.js');

const sessions = new Map();         // sessionId → sessionObj
const userToSession = new Map();    // userId(socketId) → sessionId

const MAX_PLAYERS = 200;

function getOrCreateSession(sessionId) {
  if (!sessions.has(sessionId)) {
    const state = createGameState(sessionId);
    const session = {
      id: sessionId,
      state,
      tickInterval: null,
      snapshotCounter: 0,
      io: null,           // set when first player joins
    };
    sessions.set(sessionId, session);
  }
  return sessions.get(sessionId);
}

function joinSession(io, socket, { sessionId, userAgent, abilityChoice, scenario }) {
  const faction = detectFaction(userAgent);

  if (faction === 'spectator') {
    socket.emit('rejected', { reason: 'pc-spectator' });
    socket.join(`spectator:${sessionId}`);
    const session = getOrCreateSession(sessionId);
    socket.emit('spectatorJoined', { snapshot: buildSnapshot(session.state) });
    return;
  }

  const session = getOrCreateSession(sessionId);

  // Apply scenario overrides once, when the session is first created
  if (!session.scenarioApplied) {
    session.scenarioApplied = true;
    const overrides = C.SCENARIOS?.[scenario] || {};
    if (overrides.SESSION_DURATION) session.state.timeRemaining = overrides.SESSION_DURATION;
    if (overrides.FINAL_RUSH_AT)    session.state._finalRushAt  = overrides.FINAL_RUSH_AT;
    if (overrides.TICK_MS)          session._tickMs             = overrides.TICK_MS;
    if (overrides.COST)             session.state._costOverride = overrides.COST;
    if (overrides.RUSH)             session.state._rushOverride = overrides.RUSH;
    if (overrides.HQ_STRENGTH)      session.state._hqStrength   = overrides.HQ_STRENGTH;
  }
  const state = session.state;

  const totalPlayers = Object.keys(state.users).length;
  if (totalPlayers >= MAX_PLAYERS) {
    socket.emit('rejected', { reason: 'session-full' });
    return;
  }

  // Validate ability choice for Jungle
  let ability = null;
  if (faction === 'jungle') {
    ability = C.JUNGLE_CHOICE_ABILITIES.includes(abilityChoice) ? abilityChoice : C.JUNGLE_CHOICE_ABILITIES[0];
  }

  const userId = socket.id;
  const user = addUser(state, userId, faction, ability);
  userToSession.set(userId, sessionId);
  session.io = io;

  socket.join(sessionId);
  socket.emit('joined', {
    userId,
    faction,
    ability: user.ability,
    initialState: buildSnapshot(state),
  });

  // Fill both sides to 3 players with bots, then start game
  if (!state.running) {
    fillBots(session, io, 3);
    startSession(session);
  }
}

function startSession(session) {
  session.state.running = true;
  session.tickInterval = setInterval(() => runTick(session), session._tickMs || C.TICK_MS);
}

function runTick(session) {
  const result = tick(session.state);
  const { state, io } = session;

  // Full snapshot every 5 seconds
  session.snapshotCounter++;
  if (session.snapshotCounter >= C.SNAPSHOT_EVERY) {
    session.snapshotCounter = 0;
    io.to(session.id).emit('stateSnapshot', buildSnapshot(state));
  } else if (state.changes.length > 0) {
    io.to(session.id).emit('stateUpdate', buildDelta(state));
  }

  if (state.finalRush && !session._rushBroadcast) {
    session._rushBroadcast = true;
    io.to(session.id).emit('finalRush', { timeRemaining: state.timeRemaining });
  }

  if (result?.sessionEnd) {
    clearInterval(session.tickInterval);
    clearInterval(session._botInterval);
    io.to(session.id).emit('sessionEnd', result.sessionEnd);
    sessions.delete(session.id);
  }
}

function handleAction(io, socket, { type, q, r }) {
  const userId = socket.id;
  const sessionId = userToSession.get(userId);
  if (!sessionId) { socket.emit('actionResult', { success: false, error: 'not-in-session' }); return; }

  const session = sessions.get(sessionId);
  if (!session) { socket.emit('actionResult', { success: false, error: 'session-not-found' }); return; }

  const result = processAction(session.state, userId, type, q, r);
  socket.emit('actionResult', result);

  if (result.success) {
    if (result.sessionEnd) {
      clearInterval(session.tickInterval);
      clearInterval(session._botInterval);
      io.to(sessionId).emit('sessionEnd', result.sessionEnd);
      sessions.delete(sessionId);
    } else {
      // Broadcast hex changes immediately instead of waiting for tick
      if (session.state.changes.length > 0) {
        io.to(sessionId).emit('stateUpdate', buildDelta(session.state));
        session.state.changes = [];
      }
      if (result.eliminated) {
        io.to(sessionId).emit('playerEliminated', { userId: result.eliminated });
      }
    }
  }
}

function handleAbility(io, socket, { ability, q, r }) {
  const userId = socket.id;
  const sessionId = userToSession.get(userId);
  if (!sessionId) return;
  const session = sessions.get(sessionId);
  if (!session) return;

  const validation = validateAbilityUse(ability, userId, session.state, { q, r });
  if (!validation.ok) {
    socket.emit('abilityResult', { success: false, error: validation.error });
    return;
  }

  const events = applyAbility(ability, userId, session.state, { q, r, range: 3 });
  socket.emit('abilityResult', { success: true, ability, events });

  for (const evt of events) {
    // moonShot and magicCircle reveal data is private to the user
    if (evt.type === 'moonShot' || evt.type === 'magicCircle') {
      socket.emit('abilityEvent', evt);
    } else {
      io.to(sessionId).emit('abilityEvent', evt);
    }
  }

  // starPay captures a hex — broadcast state update
  if (session.state.changes && session.state.changes.length > 0) {
    io.to(sessionId).emit('stateUpdate', buildDelta(session.state));
    session.state.changes = [];
  }
}

function handleSkill(io, socket, { action, payload }) {
  const userId = socket.id;
  const sessionId = userToSession.get(userId);
  if (!sessionId) return;
  const session = sessions.get(sessionId);
  if (!session) return;
  const state = session.state;
  const user = state.users[userId];
  if (!user || user.isEliminated) return;

  if (action === 'investOrchard') {
    if (user.faction !== 'orchard') return;
    const skills = C.ORCHARD_SKILLS;
    const nextIdx = state.factions.orchard.unlockedSkills.length;
    if (nextIdx >= skills.length) return;
    const skill = skills[nextIdx];
    if (state.factions.orchard.sharedResource < skill.cost) {
      socket.emit('skillResult', { success: false, error: 'insufficient-resource' });
      return;
    }
    state.factions.orchard.sharedResource = +(state.factions.orchard.sharedResource - skill.cost).toFixed(1);
    state.factions.orchard.unlockedSkills.push(skill.id);

    // Immediate effects
    if (skill.id === 'barkShield') {
      const hqHex = Object.values(state.hexes).find(h => h.isHQ && h.faction === 'orchard');
      if (hqHex) hqHex.strength = Math.min(hqHex.strength + 3, 10);
    }

    socket.emit('skillResult', { success: true, action, skillId: skill.id });
    io.to(sessionId).emit('skillUnlocked', {
      faction: 'orchard',
      skillId: skill.id,
      unlockedSkills: state.factions.orchard.unlockedSkills,
    });

  } else if (action === 'unlockJungle') {
    if (user.faction !== 'jungle') return;
    const costs = C.JUNGLE_SKILL_COSTS;
    const nextSlot = user.unlockedSlots;
    if (nextSlot >= costs.length) return;
    const cost = costs[nextSlot];
    if (user.resource < cost) {
      socket.emit('skillResult', { success: false, error: 'insufficient-resource' });
      return;
    }
    user.resource = +(user.resource - cost).toFixed(1);
    user.unlockedSlots++;

    socket.emit('skillResult', { success: true, action, slotIndex: user.unlockedSlots });
    socket.emit('skillUnlocked', { faction: 'jungle', userId, unlockedSlots: user.unlockedSlots });
  }
}

function handleDisconnect(socket) {
  const userId = socket.id;
  const sessionId = userToSession.get(userId);
  if (!sessionId) return;
  userToSession.delete(userId);

  const session = sessions.get(sessionId);
  if (!session) return;

  const user = session.state.users[userId];
  if (user) {
    user.isEliminated = true;
    session.state.factions.jungle.activeUsers =
      session.state.factions.jungle.activeUsers.filter(id => id !== userId);
    if (session.io) {
      session.io.to(sessionId).emit('playerLeft', { userId });
    }
  }
}

module.exports = { joinSession, handleAction, handleAbility, handleSkill, handleDisconnect };
