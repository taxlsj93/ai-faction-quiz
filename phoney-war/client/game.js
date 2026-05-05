// Game controller — context-sensitive single tap, no mode buttons

const ORCHARD_SKILLS = [
  { id: 'deepRoots',  cost: 40,  name: 'Deep Roots',  desc: '+0.1 income/hex' },
  { id: 'barkShield', cost: 80,  name: 'Bark Shield',  desc: 'HQ +3 strength' },
  { id: 'canopy',     cost: 130, name: 'Canopy',        desc: 'Expand cost -1' },
  { id: 'ecoLock',    cost: 190, name: 'Eco Lock',      desc: 'Enemy attacks cost +2' },
  { id: 'overgrowth', cost: 260, name: 'Overgrowth',    desc: 'New hexes strength 2' },
];
const JUNGLE_SKILL_COSTS = [25, 60, 100, 160, 240];
const JUNGLE_SKILL_DESCS = ['Income ×1.5', 'Attack +1', 'Expand cost -1', 'Income ×2', 'Captured hexes strength 2'];

const Game = (() => {
  let myUserId = null;
  let myFaction = null;
  let myAbility = null;
  let state = null;
  let hoverKey = null;
  let finalRush = false;
  let timerInterval = null;
  let timeRemaining = 0;
  let myResource = 0;
  let abilityTargeting = false;
  let abilityCooldownUntil = 0;

  // Skill system state
  let orchardSkills = [];
  let myUnlockedSlots = 0;
  let skillPanelOpen = false;

  const PASSIVE_ABILITIES = new Set(['secretRoom', 'starPen', 'twoScreen', 'redBatt']);
  const HEX_TARGET_ABILITIES = new Set(['starPay', 'magicCircle']);

  // Drag / pan state
  let isDragging = false;
  let dragStartX = 0, dragStartY = 0;
  let dragMoved = false;
  const DRAG_THRESHOLD = 6; // px — below this is a tap, above is a drag

  const SESSION_ID = new URLSearchParams(location.search).get('s') || 'default';
  const SCENARIO   = new URLSearchParams(location.search).get('scenario') || 'standard';

  const ABILITY_DEFS = [
    { id: 'starPay',     name: 'StarPay',     desc: 'Claim any neutral hex for free (once per 5min)',      color: '#22C55E' },
    { id: 'secretRoom',  name: 'SecretRoom',  desc: 'HQ adjacent hexes hidden from enemy (passive)',        color: '#16A34A' },
    { id: 'moonShot',    name: 'MoonShot',    desc: 'Reveal full map strength info (once per min)',         color: '#4ADE80' },
    { id: 'magicCircle', name: 'MagicCircle', desc: 'Reveal all hex info in tapped area',                  color: '#15803D' },
    { id: 'starPen',     name: 'StarPen',     desc: 'Your claimed hexes gain +1 Strength (passive)',        color: '#14B8A6' },
  ];

  // ── INIT ──────────────────────────────────────────────────────

  function init() {
    Network.connect();
    Network.on('connect',         onConnect);
    Network.on('joined',          onJoined);
    Network.on('rejected',        onRejected);
    Network.on('spectatorJoined', onSpectatorJoined);
    Network.on('stateUpdate',     onStateUpdate);
    Network.on('stateSnapshot',   onStateSnapshot);
    Network.on('actionResult',    onActionResult);
    Network.on('finalRush',       onFinalRush);
    Network.on('sessionEnd',      onSessionEnd);
    Network.on('playerEliminated',onPlayerEliminated);
    Network.on('abilityResult',   onAbilityResult);
    Network.on('abilityEvent',    onAbilityEvent);
    Network.on('skillResult',     onSkillResult);
    Network.on('skillUnlocked',   onSkillUnlocked);

    const canvas = document.getElementById('hex-canvas');
    Render.init(canvas);
    canvas.addEventListener('click',      onCanvasClick);
    canvas.addEventListener('mousemove',  onCanvasMove);
    canvas.addEventListener('mouseleave', () => { hoverKey = null; redraw(); });
    canvas.addEventListener('mousedown',  onDragStart);
    canvas.addEventListener('mouseup',    onDragEnd);
    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove',  onTouchMove,  { passive: false });
    canvas.addEventListener('touchend',   onTouchEnd,   { passive: false });
    canvas.addEventListener('wheel',      onWheel,      { passive: false });

    showScreen('intro');
  }

  function onConnect() {
    hideConnecting();
    const ua = navigator.userAgent.toLowerCase();
    const isIOS = /ipad|iphone|ipod/.test(ua) || (/macintosh/.test(ua) && navigator.maxTouchPoints > 1);
    const isAndroid = /android/.test(ua);
    if (!isIOS && !isAndroid) {
      // PC → spectator, join immediately
      Network.joinSession(SESSION_ID, null, SCENARIO);
    }
  }

  // ── SCREENS ──────────────────────────────────────────────────

  function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('screen-' + id)?.classList.add('active');
  }
  function showConnecting() { document.getElementById('overlay-connecting').style.display = 'flex'; }
  function hideConnecting() { document.getElementById('overlay-connecting').style.display = 'none'; }

  // ── START FLOW ────────────────────────────────────────────────

  function startPressed() {
    showConnecting();
    Network.joinSession(SESSION_ID, null, SCENARIO);
  }

  function renderAbilitySelect() {
    const grid = document.getElementById('ability-grid');
    grid.innerHTML = '';
    let selected = 'starPay';

    ABILITY_DEFS.forEach(a => {
      const card = document.createElement('div');
      card.className = 'ability-card' + (a.id === selected ? ' selected' : '');
      card.innerHTML = `
        <div class="ability-name">
          <span class="dot" style="background:${a.color}"></span>${a.name}
        </div>
        <div class="ability-desc">${a.desc}</div>`;
      card.addEventListener('click', () => {
        grid.querySelectorAll('.ability-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selected = a.id;
        document.getElementById('btn-confirm-ability').dataset.ability = selected;
      });
      grid.appendChild(card);
    });
    document.getElementById('btn-confirm-ability').dataset.ability = selected;
  }

  function confirmAbility() {
    const ability = document.getElementById('btn-confirm-ability').dataset.ability;
    showConnecting();
    Network.joinSession(SESSION_ID, ability, SCENARIO);
  }

  // ── NETWORK EVENTS ────────────────────────────────────────────

  function onJoined({ userId, faction, ability, initialState }) {
    hideConnecting();
    myUserId = userId;
    myFaction = faction;
    myAbility = ability;
    state = initialState;
    timeRemaining = state.timeRemaining;
    myResource = getMyResource();
    orchardSkills = initialState.factions?.orchard?.unlockedSkills || [];
    myUnlockedSlots = initialState.users?.[userId]?.unlockedSlots || 0;

    setupHUD();
    showScreen('game');
    // Wait one frame so #game-board has real dimensions before canvas resize
    requestAnimationFrame(() => {
      Render.resize();
      redraw(); // autoCenter 먼저 실행되도록 한 프레임 그리기
      requestAnimationFrame(() => {
        const hq = getMyHQHex();
        if (hq) Render.centerOnHex(hq.q, hq.r);
        startTimer();
        updateHUD();
        redraw();
      });
    });
  }

  function onRejected({ reason }) {
    hideConnecting();
    if (reason === 'pc-spectator') showScreen('spectator');
    else showToast('Session full — try another session');
  }

  function onSpectatorJoined({ snapshot }) {
    state = snapshot;
    showScreen('spectator');
  }

  function onStateUpdate({ changes, resourcePatch, timeRemaining: tr, finalRush: fr }) {
    if (!state) return;
    if (changes) {
      for (const [key, hex] of Object.entries(changes)) {
        const old = state.hexes[key];
        if (old && old.faction !== hex.faction && hex.faction) {
          Render.flashCapture(key);
        }
      }
      Object.assign(state.hexes, changes);
    }
    if (resourcePatch) {
      if (resourcePatch.orchard !== undefined) state.factions.orchard.sharedResource = resourcePatch.orchard;
      if (resourcePatch.orchardTerritory !== undefined) state.factions.orchard.territoryCount = resourcePatch.orchardTerritory;
      if (resourcePatch.orchardSkills) {
        orchardSkills = resourcePatch.orchardSkills;
        state.factions.orchard.unlockedSkills = resourcePatch.orchardSkills;
      }
      if (resourcePatch.jungleTerritory !== undefined) state.factions.jungle.territoryCount = resourcePatch.jungleTerritory;
      if (resourcePatch.jungle) {
        for (const [uid, patch] of Object.entries(resourcePatch.jungle)) {
          if (state.users[uid]) {
            if (typeof patch === 'object') {
              if (patch.resource !== undefined) state.users[uid].resource = patch.resource;
              if (patch.territoryCount !== undefined) state.users[uid].territoryCount = patch.territoryCount;
              if (patch.unlockedSlots !== undefined) {
                state.users[uid].unlockedSlots = patch.unlockedSlots;
                if (uid === myUserId) myUnlockedSlots = patch.unlockedSlots;
              }
            } else {
              state.users[uid].resource = patch;
            }
          }
        }
      }
    }
    if (tr !== undefined) timeRemaining = tr;
    if (fr && !finalRush) onFinalRush({ timeRemaining: tr });

    const newRes = getMyResource();
    if (newRes > myResource + 0.5) animateResourceTick();
    myResource = newRes;

    updateHUD();
    redraw();
  }

  function onStateSnapshot(snapshot) {
    state = snapshot;
    timeRemaining = snapshot.timeRemaining;
    myResource = getMyResource();
    updateHUD();
    redraw();
  }

  function onActionResult({ success, error, gain, blocked }) {
    if (!success) {
      const msgs = {
        'not-adjacent':           'Expand from your territory first',
        'insufficient-resource':  'Not enough resources',
        'hex-occupied':           'Already occupied',
        'cannot-attack-jungle':   '🌿 No friendly fire',
        'not-own-hex':            'Tap your own territory',
        'not-orchard-hex':        'Tap Orchard territory',
        'rate-limit':             'Too fast!',
        'eliminated':             'You have been eliminated',
      };
      showToast(msgs[error] || error);
    }
    if (blocked) showToast('🛡 Attack blocked by AppleFace!');
  }

  function onFinalRush({ timeRemaining: tr }) {
    finalRush = true;
    document.getElementById('timer').classList.add('rush');
    const rl = document.getElementById('rush-label');
    if (rl) rl.style.display = 'block';
    showToast('⚡ FINAL RUSH — costs −30%, damage +1', 4000);
    redraw();
  }

  function onSessionEnd({ winner, reason, finalStats }) {
    clearInterval(timerInterval);
    const el = document.getElementById('end-winner');
    const isWinner = winner === myFaction;
    el.textContent = winner === 'orchard' ? '🍎 The Orchard Wins' : '🌿 The Jungle Wins';
    el.className = 'end-winner ' + winner;
    document.getElementById('end-result-label').textContent = isWinner ? 'VICTORY' : 'DEFEAT';
    document.getElementById('end-result-label').className = 'end-verdict ' + (isWinner ? 'win' : 'lose');
    if (finalStats) {
      document.getElementById('end-stats').innerHTML =
        `<span style="color:#f1f5f9">🍎 ${finalStats.orchardPct}%</span> &nbsp;·&nbsp; <span style="color:#4ade80">🌿 ${finalStats.junglePct}%</span><br>
         <span style="opacity:0.5;font-size:0.75rem">${reasonText(reason)}</span>`;
    }
    showScreen('end');
  }

  function reasonText(r) {
    if (r === 'hq-captured') return 'HQ Captured';
    if (r === 'all-jungle-eliminated') return 'All Jungle Eliminated';
    return 'Time Up';
  }

  function onPlayerEliminated({ userId }) {
    if (userId === myUserId) showToast('💀 Your HQ was captured!', 4000);
    else showToast('A Jungle player was eliminated');
  }

  function shareResult() {
    const label = document.getElementById('end-result-label')?.textContent || '';
    const stats  = document.getElementById('end-stats')?.innerText || '';
    const text = `Phoney War — ${label}\n${stats}\nPlay at: ${location.origin}`;
    if (navigator.share) {
      navigator.share({ title: 'Phoney War', text }).catch(() => {});
    } else {
      navigator.clipboard?.writeText(text).then(() => showToast('Result copied!')).catch(() => {});
    }
  }

  // ── SMART TAP — CONTEXT-SENSITIVE ────────────────────────────

  function handleTap(q, r, screenX, screenY) {
    if (!state) return;

    // If in ability targeting mode, use this tap for the ability
    if (abilityTargeting) {
      abilityTargeting = false;
      updateAbilityButton();
      Network.sendAbility(myAbility, { q, r });
      spawnFloat(screenX, screenY, myAbility.toUpperCase(), 'orchard');
      return;
    }

    const key = `${q},${r}`;
    const hex = state.hexes[key];
    if (!hex) return;

    const action = resolveAction(hex, q, r);
    if (!action) {
      showToast('Tap adjacent empty or enemy hexes');
      return;
    }
    if (action === 'own') {
      const res = myFaction === 'orchard'
        ? state.factions.orchard.sharedResource
        : state.users[myUserId]?.resource || 0;
      showToast(`STR ${hex.strength}  ·  RES ${res.toFixed(0)}`);
      return;
    }

    // Optimistic float feedback
    if (action === 'expand')  spawnFloat(screenX, screenY, 'EXPAND', myFaction);
    if (action === 'attack')  spawnFloat(screenX, screenY, 'ATTACK!', 'enemy');

    Network.sendAction(action, q, r);
  }

  function resolveAction(hex, q, r) {
    const isOwn = myFaction === 'orchard'
      ? hex.faction === 'orchard'
      : hex.owner === myUserId;

    const isEmpty  = !hex.faction;
    const isEnemy  = hex.faction && hex.faction !== myFaction;
    const adjacent = isAdjacentToMine(q, r);

    if (isOwn)               return 'own';
    if (isEmpty && adjacent)  return 'expand';
    if (isEnemy && adjacent)  return 'attack';
    return null;
  }

  function isAdjacentToMine(q, r) {
    const dirs = [[1,0],[-1,0],[0,1],[0,-1],[1,-1],[-1,1]];
    return dirs.some(([dq, dr]) => {
      const nk = `${q+dq},${r+dr}`;
      const nh = state?.hexes[nk];
      if (!nh) return false;
      return myFaction === 'orchard' ? nh.faction === 'orchard' : nh.owner === myUserId;
    });
  }

  // ── CANVAS INPUT ─────────────────────────────────────────────

  // Mouse drag
  function onDragStart(e) {
    isDragging = true;
    dragMoved = false;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
  }
  function onDragEnd(e) { isDragging = false; }

  function onCanvasClick(e) {
    if (dragMoved) { dragMoved = false; return; } // was a drag, not a tap
    const rect = e.target.getBoundingClientRect();
    const { q, r } = Render.pixelToHexCoord(e.clientX - rect.left, e.clientY - rect.top);
    handleTap(q, r, e.clientX, e.clientY);
  }

  function onCanvasMove(e) {
    if (isDragging) {
      const dx = e.clientX - dragStartX;
      const dy = e.clientY - dragStartY;
      if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) {
        dragMoved = true;
        Render.applyPan(dx, dy);
        dragStartX = e.clientX;
        dragStartY = e.clientY;
        redraw();
      }
      return;
    }
    const rect = e.target.getBoundingClientRect();
    const { q, r } = Render.pixelToHexCoord(e.clientX - rect.left, e.clientY - rect.top);
    const key = `${q},${r}`;
    if (key !== hoverKey) { hoverKey = key; redraw(); }
  }

  // Mouse wheel zoom
  function onWheel(e) {
    e.preventDefault();
    const rect = e.target.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;
    const factor = e.deltaY < 0 ? 1.12 : 0.89;
    Render.applyZoom(factor, cx, cy);
    redraw();
  }

  // Zoom buttons
  function zoomIn()  { Render.applyZoom(1.25, canvasCenterX(), canvasCenterY()); redraw(); }
  function zoomOut() { Render.applyZoom(0.8,  canvasCenterX(), canvasCenterY()); redraw(); }
  function canvasCenterX() { return (document.getElementById('hex-canvas')?.clientWidth  || 300) / 2; }
  function canvasCenterY() { return (document.getElementById('hex-canvas')?.clientHeight || 300) / 2; }

  // Touch — single finger drag, multi-touch pinch zoom
  let touchStartX = 0, touchStartY = 0, touchMoved = false;
  let pinchStartDist = 0;

  function onTouchStart(e) {
    e.preventDefault();
    if (e.touches.length === 2) {
      const t0 = e.touches[0], t1 = e.touches[1];
      pinchStartDist = Math.hypot(t1.clientX - t0.clientX, t1.clientY - t0.clientY);
      touchMoved = true; // prevent tap on touch-end
      return;
    }
    if (e.touches.length !== 1) return;
    const t = e.touches[0];
    touchStartX = t.clientX;
    touchStartY = t.clientY;
    touchMoved = false;
  }

  function onTouchMove(e) {
    e.preventDefault();
    if (e.touches.length === 2) {
      const t0 = e.touches[0], t1 = e.touches[1];
      const dist = Math.hypot(t1.clientX - t0.clientX, t1.clientY - t0.clientY);
      if (pinchStartDist > 0) {
        const factor = dist / pinchStartDist;
        const rect = e.target.getBoundingClientRect();
        const cx = (t0.clientX + t1.clientX) / 2 - rect.left;
        const cy = (t0.clientY + t1.clientY) / 2 - rect.top;
        Render.applyZoom(factor > 1 ? 1.04 : 0.96, cx, cy);
        redraw();
      }
      pinchStartDist = dist;
      touchMoved = true;
      return;
    }
    if (e.touches.length !== 1) return;
    const t = e.touches[0];
    const dx = t.clientX - touchStartX;
    const dy = t.clientY - touchStartY;
    if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) {
      touchMoved = true;
      Render.applyPan(dx, dy);
      touchStartX = t.clientX;
      touchStartY = t.clientY;
      redraw();
    }
  }

  function onTouchEnd(e) {
    if (touchMoved) { touchMoved = false; return; }
    const t = e.changedTouches[0];
    if (!t) return;
    const rect = e.target.getBoundingClientRect();
    const { q, r } = Render.pixelToHexCoord(t.clientX - rect.left, t.clientY - rect.top);
    handleTap(q, r, t.clientX, t.clientY);
  }

  // ── HUD ──────────────────────────────────────────────────────

  function setupHUD() {
    const factionEl = document.getElementById('my-faction-label');
    if (factionEl) {
      factionEl.textContent = myFaction === 'orchard' ? '🍎 The Orchard' : '🌿 The Jungle';
      factionEl.className = 'faction-name ' + myFaction;
    }
    const abilityEl = document.getElementById('my-ability-label');
    if (abilityEl && myAbility) {
      const def = ABILITY_DEFS.find(a => a.id === myAbility);
      abilityEl.textContent = def ? def.name : '';
      abilityEl.style.color = def?.color || '#fff';
    }
    const enemyEl = document.getElementById('enemy-faction-label');
    if (enemyEl) {
      enemyEl.textContent = myFaction === 'orchard' ? '🌿 Jungle' : '🍎 Orchard';
    }
  }

  function updateHUD() {
    const res  = getMyResource();
    const myT  = getMyTerritory();
    const oppT = getOpponentTerritory();
    const total = Object.keys(state?.hexes || {}).length || 1;
    const myPct  = Math.round(myT  / total * 100);
    const oppPct = Math.round(oppT / total * 100);

    document.getElementById('resource-count').textContent     = Math.floor(res);
    document.getElementById('my-territory-count').textContent  = myT;
    document.getElementById('enemy-territory-count').textContent = oppT;
    document.getElementById('my-pct').textContent  = myPct  + '%';
    document.getElementById('opp-pct').textContent = oppPct + '%';

    // Territory bar: always shows Orchard share (left=white, right=green)
    const bar = document.getElementById('territory-bar-fill');
    if (bar) {
      const orchardPct = (state?.factions?.orchard?.territoryCount || 0) / total * 100;
      bar.style.width = orchardPct + '%';
    }

    // Tint resource count by faction
    const resEl = document.getElementById('resource-count');
    if (resEl) resEl.style.color = myFaction === 'jungle' ? '#4ade80' : '#f1f5f9';
  }

  function getMyResource() {
    if (!state) return 0;
    if (myFaction === 'orchard') return state.factions?.orchard?.sharedResource || 0;
    return state.users?.[myUserId]?.resource || 0;
  }

  function getMyTerritory() {
    if (!state) return 0;
    if (myFaction === 'orchard') return state.factions?.orchard?.territoryCount || 0;
    return state.users?.[myUserId]?.territoryCount || 0;
  }

  function getMyHQHex() {
    if (!state) return null;
    const user = state.users?.[myUserId];
    if (myFaction === 'jungle' && user?.hq) return user.hq;
    return Object.values(state.hexes || {}).find(h => h.faction === 'orchard' && h.isHQ) || null;
  }

  function getOpponentTerritory() {
    if (!state) return 0;
    if (myFaction === 'orchard') return state.factions?.jungle?.territoryCount || 0;
    return state.factions?.orchard?.territoryCount || 0;
  }

  function animateResourceTick() {
    const el = document.getElementById('resource-count');
    el.classList.remove('res-tick');
    void el.offsetWidth; // reflow
    el.classList.add('res-tick');
  }

  function startTimer() {
    document.getElementById('timer').textContent = formatTime(timeRemaining);
    timerInterval = setInterval(() => {
      if (timeRemaining > 0) timeRemaining -= 1;
      document.getElementById('timer').textContent = formatTime(timeRemaining);
    }, 1000);
  }

  function formatTime(s) {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
  }

  // ── FLOAT TEXT ───────────────────────────────────────────────

  function spawnFloat(x, y, text, type) {
    const el = document.createElement('div');
    el.className = 'float-text float-' + type;
    el.textContent = text;
    el.style.left = (x - 20) + 'px';
    el.style.top  = (y - 10) + 'px';
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 900);
  }

  // ── TOAST ────────────────────────────────────────────────────

  let toastTimeout = null;
  function showToast(msg, duration = 2500) {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => el.classList.remove('show'), duration);
  }

  // ── ABILITY SYSTEM ───────────────────────────────────────────

  function activateAbility() {
    if (!myAbility || PASSIVE_ABILITIES.has(myAbility)) return;
    if (Date.now() < abilityCooldownUntil) return;

    if (HEX_TARGET_ABILITIES.has(myAbility)) {
      abilityTargeting = !abilityTargeting;
      updateAbilityButton();
    } else {
      Network.sendAbility(myAbility);
    }
  }

  function onAbilityResult({ success, ability, error }) {
    if (!success) {
      const msgs = {
        'already-used':           'Ability already used',
        'insufficient-resource':  'Not enough resources',
        'not-equipped':           'You don\'t have this ability',
        'hex-not-neutral':        'That hex is occupied',
        'eliminated':             'You are eliminated',
      };
      showToast(msgs[error] || error);
      return;
    }
    const C_COOLDOWNS = { appleFace: 180, moonShot: 60, magicCircle: 90, starPay: 300 };
    const cd = C_COOLDOWNS[ability] || 30;
    abilityCooldownUntil = Date.now() + cd * 1000;
    updateAbilityButton();
    showToast('✨ ' + ability + ' activated!');
  }

  function onAbilityEvent({ type, revealed, active }) {
    if (type === 'moonShot') {
      showToast('🔭 Full map revealed for 30s', 3000);
    }
    if (type === 'magicCircle' && revealed) {
      for (const h of revealed) {
        if (state && state.hexes) {
          const key = `${h.q},${h.r}`;
          if (state.hexes[key]) Object.assign(state.hexes[key], h);
        }
      }
      redraw();
      showToast('🔍 Area revealed', 2000);
    }
    if (type === 'appleFace') {
      showToast('🛡 AppleFace shield active!', 3000);
    }
  }

  function updateAbilityButton() {
    const btn = document.getElementById('ability-btn');
    if (!btn) return;
    if (!myAbility || PASSIVE_ABILITIES.has(myAbility)) {
      btn.textContent = 'PASSIVE';
      btn.disabled = true;
      btn.className = 'ability-btn passive';
      return;
    }
    const onCooldown = Date.now() < abilityCooldownUntil;
    if (onCooldown) {
      const sec = Math.ceil((abilityCooldownUntil - Date.now()) / 1000);
      btn.textContent = `${sec}s`;
      btn.disabled = true;
      btn.className = 'ability-btn cooldown';
    } else if (abilityTargeting) {
      btn.textContent = 'TAP HEX';
      btn.disabled = false;
      btn.className = 'ability-btn targeting';
    } else {
      btn.textContent = 'USE';
      btn.disabled = false;
      btn.className = 'ability-btn ready';
    }
  }

  // ── SKILL SYSTEM ─────────────────────────────────────────────

  function onSkillResult({ success, error }) {
    if (!success) {
      showToast(error === 'insufficient-resource' ? 'Not enough resources' : (error || 'Skill failed'));
    }
  }

  function onSkillUnlocked({ faction, skillId, unlockedSkills, unlockedSlots }) {
    if (faction === 'orchard' && unlockedSkills) {
      orchardSkills = unlockedSkills;
      if (state?.factions?.orchard) state.factions.orchard.unlockedSkills = unlockedSkills;
    }
    if (faction === 'jungle' && unlockedSlots !== undefined) {
      myUnlockedSlots = unlockedSlots;
      if (state?.users?.[myUserId]) state.users[myUserId].unlockedSlots = unlockedSlots;
    }
    if (skillPanelOpen) renderSkillPanel();
    showToast(faction === 'orchard' ? '🍎 Skill unlocked!' : `🌿 Slot ${unlockedSlots} unlocked!`);
  }

  function toggleSkillPanel() {
    skillPanelOpen = !skillPanelOpen;
    const panel = document.getElementById('skill-panel');
    if (panel) panel.classList.toggle('open', skillPanelOpen);
    if (skillPanelOpen) renderSkillPanel();
  }

  function renderSkillPanel() {
    const panel = document.getElementById('skill-panel');
    if (!panel) return;

    if (myFaction === 'orchard') {
      const nextIdx = orchardSkills.length;
      let html = '<div class="skill-panel-title">🍎 Skill Tree</div>';
      ORCHARD_SKILLS.forEach((sk, i) => {
        const unlocked = orchardSkills.includes(sk.id);
        const isNext = i === nextIdx;
        html += `<div class="skill-card ${unlocked ? 'unlocked' : isNext ? 'available' : 'locked'}">
          <div class="skill-name">${sk.name}</div>
          <div class="skill-desc">${sk.desc}</div>
          ${isNext ? `<button class="skill-btn" onclick="Game.investSkill()">INVEST ${sk.cost}</button>` : ''}
          ${unlocked ? '<div class="skill-check">✓</div>' : ''}
        </div>`;
      });
      panel.innerHTML = html;
    } else {
      const nextSlot = myUnlockedSlots;
      let html = '<div class="skill-panel-title">🌿 Skills</div>';
      JUNGLE_SKILL_COSTS.forEach((cost, i) => {
        const unlocked = i < myUnlockedSlots;
        const isNext = i === nextSlot;
        html += `<div class="skill-card ${unlocked ? 'unlocked' : isNext ? 'available' : 'locked'}">
          <div class="skill-name">Slot ${i + 1}</div>
          <div class="skill-desc">${JUNGLE_SKILL_DESCS[i] || ''}</div>
          ${isNext ? `<button class="skill-btn" onclick="Game.unlockSkill()">UNLOCK ${cost}</button>` : ''}
          ${unlocked ? '<div class="skill-check">✓</div>' : ''}
        </div>`;
      });
      panel.innerHTML = html;
    }
  }

  function investSkill()  { Network.sendSkill('investOrchard'); }
  function unlockSkill()  { Network.sendSkill('unlockJungle'); }

  // ── RENDER ───────────────────────────────────────────────────

  function redraw() {
    const reachable = getReachableKeys();
    Render.draw(state?.hexes, state, myUserId, myFaction, hoverKey, finalRush, reachable);
  }

  function getReachableKeys() {
    if (!state) return { expand: new Set(), attack: new Set() };
    const expand = new Set(), attack = new Set();
    const dirs = [[1,0],[-1,0],[0,1],[0,-1],[1,-1],[-1,1]];

    for (const [key, hex] of Object.entries(state.hexes)) {
      const isMine = myFaction === 'orchard' ? hex.faction === 'orchard' : hex.owner === myUserId;
      if (!isMine) continue;
      for (const [dq, dr] of dirs) {
        const nk = `${hex.q+dq},${hex.r+dr}`;
        const nh = state.hexes[nk];
        if (!nh) continue;
        if (!nh.faction) expand.add(nk);
        else if (nh.faction !== myFaction) attack.add(nk);
      }
    }
    return { expand, attack };
  }

  return { init, startPressed, confirmAbility, shareResult, activateAbility, zoomIn, zoomOut, toggleSkillPanel, investSkill, unlockSkill };
})();

window.addEventListener('DOMContentLoaded', Game.init);
