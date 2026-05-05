const CONSTANTS = {
  // Map sizes (select via DEFAULT_MAP_SIZE or per-session config)
  MAP_SIZES: {
    small:  { cols: 22, rows: 16 },   // testing / 1~10명
    medium: { cols: 62, rows: 46 },   // 50vs50 기준 (~2850 헥스)
    large:  { cols: 92, rows: 70 },   // 100명+ (~6440 헥스)
  },
  DEFAULT_MAP_SIZE: 'medium',

  // Fixed hex size for large maps (px). Auto-scales only on small maps.
  HEX_SIZE_DEFAULT: 22,

  // Resource cap (스노볼 방지)
  RESOURCE_CAP: {
    orchard: 200,
    jungle:  100,
  },

  // Session timing (seconds)
  SESSION_DURATION: 420,    // 7 minutes
  FINAL_RUSH_AT:    60,     // last 1 minute

  // Tick rate
  TICK_MS:          200,
  SNAPSHOT_EVERY:   25,     // ticks → 5 seconds

  // Base costs (simplified — no gather cost)
  COST: {
    expand:  3,
    attack:  8,
  },

  // Passive income per hex per tick (3× original for faster gameplay)
  INCOME_PER_HEX: 0.3,

  // Final Rush multipliers
  RUSH: {
    costMultiplier:   0.6,
    attackBonus:      1,    // extra strength damage
  },

  // Rate limit
  MAX_ACTIONS_PER_SEC: 5,

  // Hex strength range
  MIN_STRENGTH: 1,
  MAX_STRENGTH: 5,

  // Starting resource
  START_RESOURCE: 20,

  // Abilities
  ABILITIES: {
    // Orchard (shared by all Orchard players)
    BUBBLE_LOCK:  'bubbleLock',
    AIR_SHARE:    'airShare',
    FACE_SHIELD:  'faceShield',

    // Jungle common
    TWO_SCREEN: 'twoScreen',
    RED_BATT:   'redBatt',

    // Jungle choice (pick 1)
    STAR_PAY:     'starPay',
    SECRET_ROOM:  'secretRoom',
    MOON_SHOT:    'moonShot',
    MAGIC_CIRCLE: 'magicCircle',
    STAR_PEN:     'starPen',
  },

  JUNGLE_CHOICE_ABILITIES: ['starPay', 'secretRoom', 'moonShot', 'magicCircle', 'starPen'],

  // ── GAME SCENARIOS (select via ?scenario=<key> URL param) ──────
  // Each scenario overrides the base constants above.
  SCENARIOS: {
    // Standard 20-minute session (default)
    standard: {},

    // Rush Mode: short 5-min session, attack costs halved, Final Rush from start
    rush: {
      SESSION_DURATION: 300,
      FINAL_RUSH_AT:    300,  // immediate
      COST: { gather: 0, expand: 3, attack: 6 },
      RUSH: { costMultiplier: 0.5, attackBonus: 2 },
    },

    // Siege Mode: HQ has 10 strength, longer session
    siege: {
      SESSION_DURATION: 1800,  // 30 min
      FINAL_RUSH_AT:    300,
      // NOTE: HQ strength override is applied in placeHQ (see gameState.js)
      HQ_STRENGTH: 10,
    },

    // Blitz Mode: ultra-fast 3-min burst, very cheap expand
    blitz: {
      SESSION_DURATION: 180,
      FINAL_RUSH_AT:    180,
      COST: { gather: 0, expand: 2, attack: 5 },
      TICK_MS: 150,
    },
  },

  DEFAULT_SCENARIO: 'standard',

  // ── SKILL SYSTEM ──────────────────────────────────────────────
  // Orchard: shared faction upgrade tree (invest in order)
  ORCHARD_SKILLS: [
    { id: 'deepRoots',  cost: 40,  name: 'Deep Roots',  desc: '+0.1 income per hex' },
    { id: 'barkShield', cost: 80,  name: 'Bark Shield',  desc: 'HQ +3 strength' },
    { id: 'canopy',     cost: 130, name: 'Canopy',        desc: 'Expand cost -1' },
    { id: 'ecoLock',    cost: 190, name: 'Eco Lock',      desc: 'Enemy attacks cost +2' },
    { id: 'overgrowth', cost: 260, name: 'Overgrowth',    desc: 'New hexes start at strength 2' },
  ],

  // Jungle: personal slot unlock costs (slots 1–5 in order)
  JUNGLE_SKILL_COSTS: [25, 60, 100, 160, 240],
  JUNGLE_SKILL_DESCS: [
    'Income ×1.5',
    'Attack damage +1',
    'Expand cost -1',
    'Income ×2',
    'Captured hexes start at strength 2',
  ],

  // Ability hex colors (Jungle choice abilities tint player hexes)
  ABILITY_COLORS: {
    starPay:     '#22C55E',
    secretRoom:  '#16A34A',
    moonShot:    '#4ADE80',
    magicCircle: '#15803D',
    starPen:     '#14B8A6',
  },

  // Cooldowns (seconds)
  COOLDOWNS: {
    appleDrop:   25,
    appleFace:   180,
    twoScreen:   0,    // passive
    redBatt:     0,    // passive / auto
    starPay:     300,
    secretRoom:  0,    // passive
    moonShot:    60,
    magicCircle: 90,
    starPen:     0,    // passive
  },
};

if (typeof module !== 'undefined') module.exports = CONSTANTS;
