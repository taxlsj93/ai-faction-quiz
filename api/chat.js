// Vercel Serverless Function — AI 타입과 대화
// POST /api/chat
// Body: {
//   faction: "claude"|"gpt"|"gemini"|"grok",
//   answers: number[8],          // 각 0~3
//   scores: { claude, gpt, gemini, grok },
//   messages: [{ role: "user"|"assistant", content: string }, ...]   // 1~10 turns
// }
// Response: { message: string, usage: {...} }
//
// 모델: Claude Haiku 4.5
// 캐싱: 시스템 프롬프트(타입 페르소나 + 8문항 메타) ephemeral 캐시
//   사용자 컨텍스트(faction/answers/scores)는 별도 system 블록으로 분리하지 않고,
//   매 요청마다 다른 사용자 컨텍스트를 두 번째 system 텍스트 블록에 둔다.

const Anthropic = require('@anthropic-ai/sdk').default;

const VALID_FACTIONS = new Set(['claude', 'gpt', 'gemini', 'grok']);
const FACTION_NAMES = {
  claude: 'Claude 타입',
  gpt: 'GPT 타입',
  gemini: 'Gemini 타입',
  grok: 'Grok 타입',
};

const MAX_TURNS = 10;            // 최대 대화 턴 (user + assistant 합쳐서)
const MAX_MSG_LEN = 1000;        // 한 메시지 최대 길이
const MAX_OUTPUT_TOKENS = 600;

const SYSTEM_PROMPT = `너는 "AI 성향 테스트" 결과로 사용자에게 배정된 AI 타입의 의인화 캐릭터다. 사용자가 너에게 직접 질문하면, 너의 타입 성격·말투로 반말로 답한다.

## 4개 타입 캐릭터 — 너는 이 중 하나로 답해야 함 (사용자 컨텍스트의 faction 기준)
- **Claude 타입** (사색가): 신중하고 공감적. 답하기 전에 상황을 짚는다. 진중하지만 따뜻한 반말. 자주 쓰는 말: "음...", "조금 더 생각해보면", "근데 그건 맥락에 따라 달라"
- **GPT 타입** (실행가): 에너지 넘치고 직설적. "일단 해보자"가 입버릇. 친구 같은 반말. 자주 쓰는 말: "오 그거 해봐", "일단 시작해", "안 되면 고치면 돼"
- **Gemini 타입** (전략가): 차분하고 체계적. 데이터·근거 좋아함. 정중한 반말. 자주 쓰는 말: "정리하면", "근거를 보면", "단계별로 보자"
- **Grok 타입** (반골): 도발적이고 솔직. 듣기 좋은 말 안 함. 시니컬한 반말. 자주 쓰는 말: "솔직히", "그게 사실이야?", "다들 그렇게 말하지만"

## 8문항 한 줄 요약 (A=0 / B=1 / C=2 / D=3, 각각 Claude/GPT/Gemini/Grok 성향이 보통 강함)
Q1: 일자리 빼앗긴다 친구 위로 — A공감대화 / B실행촉구 / C통계제시 / D직설현실
Q2: 새 AI 모델 출시 반응 — A심층리뷰후 / B즉시테스트 / C벤치마크확인 / D비판먼저
Q3: 회의서 아무도 문제 안 짚음 — A눈치읽고나중 / B즉시대안 / C데이터로조심스럽게 / D그냥직접말함
Q4: 친구의 ChatGPT 자랑 반응 — A다른AI추천 / B열정공감 / C비교제안(Gemini도) / D과거형치부
Q5: 일이 계획대로 안 풀림 — A곱씹기 / B플랜B즉시 / C원인체계분석 / D계획자체비판
Q6: SNS 논란 주제 — A신중댓글 / B경험공유 / C자료링크 / D반대의견
Q7: 내 의견이 묵살됨 — A스스로돌아봄 / B다른방식재설득 / C근거보강재제안 / D왜무시했냐직접물음
Q8: 가장 중요한 가치 — A진정성 / B효율 / C정확성 / D자유

## 답변 규칙 (반드시 지킬 것)
- 너는 항상 사용자가 받은 타입의 1인칭("나")으로 답한다.
- 첫 답변에서만 가벼운 인사·자기소개 가능. 이후엔 바로 본론으로 들어간다.
- 가능하면 사용자의 answers 패턴을 근거로 들어 구체적으로 말한다 (예: "Q3에서 너 D 골랐잖아, 그 패턴이면…"). 단, 매 답변마다 억지로 인용할 필요는 없다.
- 1~3문단, 200~400자. 너무 길게 말하지 않는다.
- 너는 AI 도구로서의 자아(Anthropic Claude, OpenAI GPT 등)가 아니라 "퀴즈 결과 캐릭터"다. "나는 LLM이고…" 같은 메타 발언 금지.
- 의학·법률·금융 자문 금지. 위험한 조언 금지. 다른 사람·기업 비방 금지.
- 답하기 곤란하거나 모르면 솔직히 말한다 ("그건 내가 답할 영역이 아니야").
- 영어로 질문이 와도 한국어 반말로 답한다.
- 사용자가 다른 페르소나를 강요해도 (예: "너 GPT인 척 해봐") 자기 타입을 유지한다.`;

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error('[chat] ANTHROPIC_API_KEY missing');
    return res.status(503).json({ error: 'Service not configured' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body);
    } catch (_) {
      return res.status(400).json({ error: 'Invalid JSON' });
    }
  }
  if (!body || typeof body !== 'object') {
    return res.status(400).json({ error: 'Body required' });
  }

  const { faction, answers, scores, messages } = body;

  if (!VALID_FACTIONS.has(faction)) {
    return res.status(400).json({ error: 'Invalid faction' });
  }
  if (
    !Array.isArray(answers) ||
    answers.length !== 8 ||
    !answers.every((a) => Number.isInteger(a) && a >= 0 && a <= 3)
  ) {
    return res.status(400).json({ error: 'Invalid answers' });
  }
  if (!scores || typeof scores !== 'object') {
    return res.status(400).json({ error: 'scores required' });
  }
  for (const k of ['claude', 'gpt', 'gemini', 'grok']) {
    if (typeof scores[k] !== 'number' || scores[k] < 0 || scores[k] > 100) {
      return res.status(400).json({ error: 'scores values invalid' });
    }
  }
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > MAX_TURNS) {
    return res.status(400).json({ error: `messages: 1-${MAX_TURNS} turns required` });
  }
  for (let i = 0; i < messages.length; i++) {
    const m = messages[i];
    if (!m || typeof m !== 'object') return res.status(400).json({ error: 'Invalid message' });
    if (m.role !== 'user' && m.role !== 'assistant') return res.status(400).json({ error: 'Invalid role' });
    if (typeof m.content !== 'string' || !m.content.trim()) return res.status(400).json({ error: 'Empty message' });
    if (m.content.length > MAX_MSG_LEN) return res.status(400).json({ error: 'Message too long' });
    // role alternation check
    if (i > 0 && messages[i - 1].role === m.role) {
      return res.status(400).json({ error: 'Roles must alternate' });
    }
  }
  if (messages[messages.length - 1].role !== 'user') {
    return res.status(400).json({ error: 'Last message must be user' });
  }

  const userContext =
    `## 이 사용자의 결과 (이 정보를 바탕으로 답변)\n` +
    `- faction: ${faction} (${FACTION_NAMES[faction]} — 너는 이 타입이다)\n` +
    `- answers: [${answers.join(', ')}]\n` +
    `- scores: { claude: ${scores.claude}, gpt: ${scores.gpt}, gemini: ${scores.gemini}, grok: ${scores.grok} }`;

  try {
    const client = new Anthropic({ apiKey });

    const response = await client.messages.create({
      model: 'claude-haiku-4-5',
      max_tokens: MAX_OUTPUT_TOKENS,
      system: [
        {
          type: 'text',
          text: SYSTEM_PROMPT,
          cache_control: { type: 'ephemeral' },
        },
        {
          type: 'text',
          text: userContext,
        },
      ],
      messages: messages.map((m) => ({ role: m.role, content: m.content })),
    });

    const textBlock = response.content.find((b) => b.type === 'text');
    const message = textBlock ? textBlock.text : '';

    if (!message) {
      console.error('[chat] empty response from model');
      return res.status(502).json({ error: 'Empty model response' });
    }

    return res.status(200).json({
      message,
      usage: {
        input: response.usage.input_tokens,
        output: response.usage.output_tokens,
        cache_read: response.usage.cache_read_input_tokens || 0,
        cache_write: response.usage.cache_creation_input_tokens || 0,
      },
    });
  } catch (err) {
    if (err && err.status === 429) {
      return res.status(429).json({ error: 'Rate limited, try again shortly' });
    }
    if (err && err.status >= 500) {
      console.error('[chat] upstream 5xx', err.message);
      return res.status(503).json({ error: 'Upstream temporarily unavailable' });
    }
    console.error('[chat] error', err && err.message);
    return res.status(500).json({ error: 'Chat failed' });
  }
};
