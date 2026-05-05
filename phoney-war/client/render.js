/**
 * Render engine — requestAnimationFrame loop, animated HQ, capture flash
 * References: territorial.io (flood color), splix.io (strong faction color),
 *             agar.io (spatial feedback), warzone (strength-on-tile)
 */
const Render = (() => {
  let canvas, ctx;
  let canvasW = 0, canvasH = 0;
  let hexSize = 24;
  let offsetX = 0, offsetY = 0;
  let panX = 0, panY = 0;
  let centered = false;
  let rafId = null;

  // External state reference (set per draw call)
  let _hexes = null, _state = null, _myUserId = null, _myFaction = null;
  let _hoverKey = null, _finalRush = false, _reachable = null;

  // Flash animation: Map<hexKey, timestamp>
  const captureFlash = new Map();
  const FLASH_DURATION = 500;

  // Colors
  const COL = {
    bg:       '#07090c',
    orchard:  { stroke: 'rgba(190,218,255,0.85)', hqFill: '#f0f8ff', hqGlow: '#93c5fd', text: '#0a1628' },
    jungle:   { stroke: '#4ade80', hqFill: '#22c55e', hqGlow: '#4ade80', text: '#022c16' },
    neutral:  { fill: '#0c1210', stroke: '#18201a' },
    expand:   { fill: '#172a1a', stroke: 'rgba(255,255,255,0.55)' },
    attack:   { fill: '#3b0a0a', stroke: '#f87171' },
  };

  const ABILITY_COL = {
    starPay:     { fill: '#14532d', stroke: '#22C55E' },
    secretRoom:  { fill: '#052e16', stroke: '#16A34A' },
    moonShot:    { fill: '#064e3b', stroke: '#6ee7b7' },
    magicCircle: { fill: '#022c22', stroke: '#15803D' },
    starPen:     { fill: '#0c2927', stroke: '#14B8A6' },
  };

  // ── INIT ─────────────────────────────────────────────────────

  function init(el) {
    canvas = el;
    ctx = canvas.getContext('2d');
    resize();
    window.addEventListener('resize', () => { resize(); centered = false; });
    startLoop();
  }

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    canvasW = canvas.parentElement.clientWidth  || window.innerWidth;
    canvasH = canvas.parentElement.clientHeight || window.innerHeight * 0.65;
    canvas.width  = Math.round(canvasW * dpr);
    canvas.height = Math.round(canvasH * dpr);
    canvas.style.width  = canvasW + 'px';
    canvas.style.height = canvasH + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    centered = false;
  }

  // ── ANIMATION LOOP ────────────────────────────────────────────

  function startLoop() {
    function loop() {
      drawFrame();
      rafId = requestAnimationFrame(loop);
    }
    rafId = requestAnimationFrame(loop);
  }

  function stopLoop() {
    if (rafId) cancelAnimationFrame(rafId);
  }

  // ── DRAW ─────────────────────────────────────────────────────

  function drawFrame() {
    ctx.clearRect(0, 0, canvasW, canvasH);
    drawBackground();
    if (!_hexes) return;

    const hexArr = Object.values(_hexes);
    if (!hexArr.length) return;

    if (!centered) autoCenter(hexArr);

    const now = Date.now();
    const expand = _reachable?.expand || new Set();
    const attack = _reachable?.attack || new Set();

    for (const hex of hexArr) {
      const { x, y } = toPixel(hex.q, hex.r);
      if (x < -hexSize * 3 || x > canvasW + hexSize * 3) continue;
      if (y < -hexSize * 3 || y > canvasH + hexSize * 3) continue;
      drawHex(hex, x, y, now, expand, attack);
    }

    // Clean up old flash entries
    for (const [k, t] of captureFlash) {
      if (now - t > FLASH_DURATION) captureFlash.delete(k);
    }
  }

  function drawBackground() {
    ctx.fillStyle = COL.bg;
    ctx.fillRect(0, 0, canvasW, canvasH);

    // Subtle hex grid pattern
    ctx.globalAlpha = 0.04;
    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 0.5;
    const step = hexSize * 2.1;
    for (let x = -step; x < canvasW + step; x += step * Math.sqrt(3) / 2) {
      for (let y = -step; y < canvasH + step; y += step * 1.5) {
        drawHexOutline(x, y, hexSize * 0.9);
      }
    }
    ctx.globalAlpha = 1;
  }

  function drawHexOutline(cx, cy, sz) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 3 * i;
      i === 0 ? ctx.moveTo(cx + sz * Math.cos(a), cy + sz * Math.sin(a))
              : ctx.lineTo(cx + sz * Math.cos(a), cy + sz * Math.sin(a));
    }
    ctx.closePath();
    ctx.stroke();
  }

  function drawHex(hex, x, y, now, expand, attack) {
    const key = `${hex.q},${hex.r}`;
    const isHover = key === _hoverKey;
    const canExp  = expand.has(key) && !hex.faction;
    const canAtk  = attack.has(key);
    const flash   = captureFlash.get(key);
    const flashPct = flash ? Math.max(0, 1 - (now - flash) / FLASH_DURATION) : 0;
    const t = now / 1000; // seconds

    const c = getColors(hex);
    const sz = hexSize - 1.5;

    makePath(x, y, sz);

    // Fill — strength-based opacity gives visual depth
    if (canExp) {
      ctx.fillStyle = COL.expand.fill;
    } else if (canAtk) {
      ctx.fillStyle = COL.attack.fill;
    } else if (hex.isHQ) {
      ctx.fillStyle = c.hqFill;
    } else if (hex.faction === 'orchard') {
      const a = Math.min(0.22 + hex.strength * 0.16, 1.0);
      ctx.fillStyle = `rgba(210,228,252,${a.toFixed(2)})`;
    } else if (hex.faction === 'jungle') {
      const ability = _state?.users?.[hex.owner]?.ability;
      const ac = ability && ABILITY_COL[ability];
      if (ac) {
        ctx.fillStyle = ac.fill;
      } else {
        const a = Math.min(0.28 + hex.strength * 0.15, 1.0);
        ctx.fillStyle = `rgba(22,163,74,${a.toFixed(2)})`;
      }
    } else {
      ctx.fillStyle = COL.neutral.fill;
    }
    ctx.fill();

    // Capture flash overlay
    if (flashPct > 0) {
      ctx.globalAlpha = flashPct * 0.7;
      ctx.fillStyle = hex.faction === 'orchard' ? '#93c5fd' : '#4ade80';
      ctx.fill();
      ctx.globalAlpha = 1;
    }

    // Stroke
    if (isHover) {
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 2.5;
    } else if (canExp) {
      ctx.strokeStyle = COL.expand.stroke;
      ctx.lineWidth = 1.5;
    } else if (canAtk) {
      ctx.strokeStyle = COL.attack.stroke;
      ctx.lineWidth = 2;
    } else if (hex.isHQ) {
      // Pulsing glow on HQ
      const pulse = 0.7 + 0.3 * Math.sin(t * 3);
      ctx.strokeStyle = c.hqGlow;
      ctx.lineWidth = 2.5;
      ctx.save();
      ctx.shadowColor = c.hqGlow;
      ctx.shadowBlur = 16 * pulse;
      ctx.stroke();
      ctx.restore();
      return; // already stroked in shadow context
    } else {
      ctx.strokeStyle = hex.faction ? c.stroke : COL.neutral.stroke;
      ctx.lineWidth = hex.faction ? 1.5 : 0.8;
    }
    ctx.stroke();

    // Final Rush: extra glow on owned hexes
    if (_finalRush && hex.faction) {
      ctx.save();
      ctx.shadowColor = '#ef4444';
      ctx.shadowBlur = 6;
      makePath(x, y, sz);
      ctx.stroke();
      ctx.restore();
    }

    // Labels
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    if (hex.isHQ) {
      const emoji = hex.faction === 'orchard' ? '🍎' : '🌿';
      ctx.font = `${Math.max(10, Math.floor(hexSize * 0.52))}px sans-serif`;
      ctx.fillText(emoji, x, y + 1);
    } else if (hex.faction) {
      // Strength number — white on jungle, dark on orchard
      ctx.fillStyle = hex.faction === 'orchard' ? 'rgba(10,22,40,0.85)' : 'rgba(255,255,255,0.7)';
      ctx.font = `700 ${Math.max(8, Math.floor(hexSize * 0.4))}px JetBrains Mono, monospace`;
      ctx.fillText(hex.strength, x, y);
    } else if (canExp) {
      ctx.fillStyle = 'rgba(255,255,255,0.22)';
      ctx.font = `${Math.floor(hexSize * 0.55)}px sans-serif`;
      ctx.fillText('+', x, y);
    }
  }

  function makePath(cx, cy, sz) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 3 * i + Math.PI / 6;
      i === 0 ? ctx.moveTo(cx + sz * Math.cos(a), cy + sz * Math.sin(a))
              : ctx.lineTo(cx + sz * Math.cos(a), cy + sz * Math.sin(a));
    }
    ctx.closePath();
  }

  function getColors(hex) {
    if (!hex.faction) return COL.neutral;
    if (hex.faction === 'orchard') return { ...COL.orchard };
    const ability = _state?.users?.[hex.owner]?.ability;
    const ac = ability && ABILITY_COL[ability];
    if (ac) return { stroke: ac.stroke, hqFill: ac.stroke, hqGlow: ac.stroke, text: '#052e16' };
    return { ...COL.jungle };
  }

  // ── CENTER ────────────────────────────────────────────────────

  function autoCenter(hexArr) {
    const qs = hexArr.map(h => h.q), rs = hexArr.map(h => h.r);
    const cols = Math.max(...qs) - Math.min(...qs) + 2;
    const rows = Math.max(...rs) - Math.min(...rs) + 2;
    const pad  = 28;
    const byW  = (canvasW - pad * 2) / (cols * Math.sqrt(3));
    const byH  = (canvasH - pad * 2) / (rows * 1.5);
    const fitSize = Math.floor(Math.min(byW, byH));

    if (fitSize >= 14) {
      // 맵이 화면에 들어옴 → 전체 중앙 정렬
      hexSize = Math.min(22, fitSize);
      const gW = hexSize * Math.sqrt(3) * (cols - 0.5);
      const gH = hexSize * 1.5 * (rows - 0.5);
      panX = offsetX = (canvasW - gW) / 2 + hexSize;
      panY = offsetY = (canvasH - gH) / 2 + hexSize * 0.5;
    } else {
      // 대형 맵 → 고정 hexSize, HQ 중심으로 표시 (centerOnHex 호출 대기)
      hexSize = 16;
      panX = offsetX = canvasW / 2;
      panY = offsetY = canvasH / 2;
    }
    centered = true;
  }

  function centerOnHex(q, r) {
    // HQ 헥스를 화면 중앙에 오도록 pan 설정
    const px = hexSize * Math.sqrt(3) * (q + r / 2);
    const py = hexSize * 1.5 * r;
    panX = offsetX = canvasW / 2 - px;
    panY = offsetY = canvasH / 2 - py;
  }

  // ── PAN ──────────────────────────────────────────────────────

  function applyPan(dx, dy) {
    panX += dx; panY += dy;
    offsetX = panX; offsetY = panY;
  }

  function applyZoom(factor, cx, cy) {
    const MIN_HEX = 6, MAX_HEX = 52;
    const oldSize = hexSize;
    hexSize = Math.max(MIN_HEX, Math.min(MAX_HEX, hexSize * factor));
    const scale = hexSize / oldSize;
    offsetX = cx + (offsetX - cx) * scale;
    offsetY = cy + (offsetY - cy) * scale;
    panX = offsetX; panY = offsetY;
  }

  function resetPan() { centered = false; panX = panY = 0; }

  // ── PIXEL ↔ HEX ──────────────────────────────────────────────

  function toPixel(q, r) {
    return {
      x: hexSize * Math.sqrt(3) * (q + r / 2) + offsetX,
      y: hexSize * 1.5 * r + offsetY,
    };
  }

  function pixelToHexCoord(px, py) {
    const x = (px - offsetX) / hexSize;
    const y = (py - offsetY) / hexSize;
    const q = Math.sqrt(3)/3 * x - 1/3 * y;
    const r = 2/3 * y;
    const s = -q - r;
    let rq = Math.round(q), rr = Math.round(r), rs = Math.round(s);
    const dq = Math.abs(rq-q), dr = Math.abs(rr-r), ds = Math.abs(rs-s);
    if (dq > dr && dq > ds) rq = -rr - rs;
    else if (dr > ds) rr = -rq - rs;
    return { q: rq, r: rr };
  }

  // ── PUBLIC API ────────────────────────────────────────────────

  function draw(hexes, state, myUserId, myFaction, hoverKey, finalRush, reachable) {
    _hexes = hexes; _state = state; _myUserId = myUserId; _myFaction = myFaction;
    _hoverKey = hoverKey; _finalRush = finalRush; _reachable = reachable;
  }

  function flashCapture(hexKey) {
    captureFlash.set(hexKey, Date.now());
  }

  return { init, resize, draw, pixelToHexCoord, applyPan, applyZoom, resetPan, flashCapture, centerOnHex };
})();
