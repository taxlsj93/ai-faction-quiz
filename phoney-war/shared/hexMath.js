// Hex grid math — pointy-top orientation, offset coordinates

function hexToPixel(q, r, size, offsetX, offsetY) {
  const x = size * Math.sqrt(3) * (q + r / 2) + offsetX;
  const y = size * 1.5 * r + offsetY;
  return { x, y };
}

function pixelToHex(px, py, size, offsetX, offsetY) {
  const x = (px - offsetX) / size;
  const y = (py - offsetY) / size;
  const q = (Math.sqrt(3) / 3 * x - 1 / 3 * y);
  const r = (2 / 3 * y);
  return hexRound(q, r);
}

function hexRound(q, r) {
  const s = -q - r;
  let rq = Math.round(q), rr = Math.round(r), rs = Math.round(s);
  const dq = Math.abs(rq - q), dr = Math.abs(rr - r), ds = Math.abs(rs - s);
  if (dq > dr && dq > ds) rq = -rr - rs;
  else if (dr > ds) rr = -rq - rs;
  return { q: rq, r: rr };
}

function hexNeighbors(q, r) {
  return [
    { q: q + 1, r: r     },
    { q: q - 1, r: r     },
    { q: q,     r: r + 1 },
    { q: q,     r: r - 1 },
    { q: q + 1, r: r - 1 },
    { q: q - 1, r: r + 1 },
  ];
}

function hexDistance(q1, r1, q2, r2) {
  return (Math.abs(q1 - q2) + Math.abs(q1 + r1 - q2 - r2) + Math.abs(r1 - r2)) / 2;
}

function hexesInRange(q, r, range) {
  const results = [];
  for (let dq = -range; dq <= range; dq++) {
    for (let dr = Math.max(-range, -dq - range); dr <= Math.min(range, -dq + range); dr++) {
      results.push({ q: q + dq, r: r + dr });
    }
  }
  return results;
}

if (typeof module !== 'undefined') {
  module.exports = { hexToPixel, pixelToHex, hexRound, hexNeighbors, hexDistance, hexesInRange };
}
