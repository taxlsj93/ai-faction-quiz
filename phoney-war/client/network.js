// Network layer — Socket.io wrapper
// Exposes: Network.connect(), Network.joinSession(), Network.sendAction(), Network.on()

const Network = (() => {
  let socket = null;
  const handlers = {};

  function on(event, fn) {
    handlers[event] = handlers[event] || [];
    handlers[event].push(fn);
  }

  function emit(event, data) {
    if (handlers[event]) handlers[event].forEach(fn => fn(data));
  }

  function connect(serverUrl) {
    socket = io(serverUrl || window.location.origin);

    socket.on('connect', () => emit('connect'));
    socket.on('disconnect', () => emit('disconnect'));
    socket.on('joined',          d => emit('joined', d));
    socket.on('rejected',        d => emit('rejected', d));
    socket.on('spectatorJoined', d => emit('spectatorJoined', d));
    socket.on('stateUpdate',     d => emit('stateUpdate', d));
    socket.on('stateSnapshot',   d => emit('stateSnapshot', d));
    socket.on('actionResult',    d => emit('actionResult', d));
    socket.on('finalRush',       d => emit('finalRush', d));
    socket.on('sessionEnd',      d => emit('sessionEnd', d));
    socket.on('playerEliminated',d => emit('playerEliminated', d));
    socket.on('playerLeft',      d => emit('playerLeft', d));
    socket.on('abilityResult',   d => emit('abilityResult', d));
    socket.on('abilityEvent',    d => emit('abilityEvent',  d));
    socket.on('skillResult',     d => emit('skillResult',   d));
    socket.on('skillUnlocked',   d => emit('skillUnlocked', d));
  }

  function joinSession(sessionId, abilityChoice, scenario) {
    socket.emit('joinSession', {
      sessionId,
      userAgent: navigator.userAgent,
      abilityChoice,
      scenario: scenario || 'standard',
    });
  }

  function sendAction(type, q, r) {
    socket.emit('action', { type, q, r });
  }

  function sendAbility(ability, extra = {}) {
    socket.emit('useAbility', { ability, ...extra });
  }

  function sendSkill(action, payload = {}) {
    socket.emit('useSkill', { action, payload });
  }

  return { connect, joinSession, sendAction, sendAbility, sendSkill, on };
})();
