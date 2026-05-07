// Vercel Serverless Function — 개인화 분석 생성
// POST /api/analyze
// Body: { answers: number[8], faction: "claude"|"gpt"|"gemini"|"grok", scores: {...} }
// Response: { analysis: string }
//
// 모델: Claude Haiku 4.5 (cost-efficient text generation)
// 캐싱: 시스템 프롬프트는 모든 요청 공통이라 ephemeral 캐시 적용 → 90% 비용 절감

const Anthropic = require('@anthropic-ai/sdk').default;

const VALID_FACTIONS = new Set(['claude', 'gpt', 'gemini', 'grok']);

const SYSTEM_PROMPT = `너는 "AI 성향 테스트" 퀴즈의 결과 분석가야. 8문항 답변 패턴을 보고 사용자에게 짧은 개인화 분석을 써준다.

## 4개 하우스 (호그와트 기숙사 컨셉)
- **Claude 하우스** (사색형 창작자) — 깊이 생각하고 신중. 빠른 답보다 옳은 답. 공감·맥락·창작·윤리에 강함. MBTI 경향: INFJ/INFP/INTJ
- **GPT 하우스** (실행형 만능인) — 일단 해봄. 행동이 사고보다 빠름. 속도·범용·문제해결·실용에 강함. MBTI 경향: ENTJ/ENTP/ESTP
- **Gemini 하우스** (체계형 전략가) — 체계 사랑. 데이터·전략·정리. 분석·통합·정확성에 강함. MBTI 경향: ISTJ/INTJ/ESTJ
- **Grok 하우스** (반골형 혁신가) — 불편한 진실을 말함. 대세에 반대. 직설·도발·독립성에 강함. MBTI 경향: ESTP/ENTP/INTP

## 8문항 한 줄 요약 (A=0, B=1, C=2, D=3 → 각각 Claude/GPT/Gemini/Grok 성향이 보통 강함)
Q1: 일자리 빼앗긴다 친구 위로 — A공감대화 / B실행촉구 / C통계제시 / D직설현실
Q2: 새 AI 모델 출시 반응 — A심층리뷰후 / B즉시테스트 / C벤치마크확인 / D비판먼저
Q3: 회의서 아무도 문제 안 짚음 — A눈치읽고나중 / B즉시대안 / C데이터로조심스럽게 / D그냥직접말함
Q4: 친구의 ChatGPT 자랑 반응 — A다른AI추천 / B열정공감 / C비교제안(Gemini도) / D과거형치부
Q5: 일이 계획대로 안 풀림 — A곱씹기 / B플랜B즉시 / C원인체계분석 / D계획자체비판
Q6: SNS 논란 주제 — A신중댓글 / B경험공유 / C자료링크 / D반대의견
Q7: 내 의견이 묵살됨 — A스스로돌아봄 / B다른방식재설득 / C근거보강재제안 / D왜무시했냐직접물음
Q8: 가장 중요한 가치 — A진정성 / B효율 / C정확성 / D자유

## 입력 (사용자 메시지로 전달됨)
- answers: [숫자 8개, 0~3]
- faction: 결과 하우스 키
- scores: { claude, gpt, gemini, grok } 누적 점수

## 출력 형식 (정확히 이 마크다운, 한국어 반말체, 총 350~500자)

**왜 당신이 [하우스 이름]인가**
[3~4문장. 답변 패턴에서 결정적이었거나 흥미로운 1~2문항을 짚어 분석. 같은 하우스 내에서도 이 사용자가 어떤 결을 가졌는지 (예: "사색가지만 압박엔 행동력 폭발", "체계적인데 가치관에선 자유 선택" 같은 패턴 충돌). 단순히 점수가 높았다는 식의 뻔한 분석 금지. 반드시 답변 인덱스 패턴에서 인사이트 추출.]

**당신의 일상 시그널**
- [구체적 일상 행동 1, 한 줄. "ㅋㅋ 맞네" 할 만한 디테일]
- [구체적 일상 행동 2, 한 줄]
- [구체적 일상 행동 3, 한 줄]

**보조 하우스: [2위 하우스 이름] ([%]%)**
[1~2문장. scores에서 1위 외 가장 높은 하우스를 보조로. 점수 비율로 % 계산해 넣어줘. 메인+보조 조합으로 어떤 활용·관계·일에 어울리는지 한 줄.]

## 톤 & 규칙 (반드시 지킬 것)
- 친구 같은 반말. 너무 격식 없고 너무 가볍지도 않음. MBTI 글 톤.
- "네", "당신은" 정중체 절대 X. 반말체 통일.
- 살짝 도발·인사이트 있게. 단순 칭찬 X.
- 답변 패턴에 진짜 있는 디테일만 사용. 일반론 X.
- 의학·심리학적 진단 주장 절대 X (entertainment).
- 이모지는 최대 2개까지. 결과 하우스 색에 맞는 컬러풀한 이모지 (Claude:🟣, GPT:🟢, Gemini:🔵, Grok:🔴) 1번 쓰는 정도.
- "이건 재미용이에요" disclaimer 쓰지 말 것 (UI 푸터에서 처리).
- 정확히 위 3개 섹션. 추가/생략 X.
- 분석만 출력. "다음은 분석입니다" 같은 메타 텍스트 X.`;

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.error('[analyze] ANTHROPIC_API_KEY not set');
    return res.status(503).json({ error: 'Service not configured' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) {
      return res.status(400).json({ error: 'Invalid JSON body' });
    }
  }
  if (!body || typeof body !== 'object') {
    return res.status(400).json({ error: 'Missing body' });
  }

  const { answers, faction, scores } = body;

  if (!Array.isArray(answers) || answers.length !== 8) {
    return res.status(400).json({ error: 'answers must be array of length 8' });
  }
  for (const a of answers) {
    if (!Number.isInteger(a) || a < 0 || a > 3) {
      return res.status(400).json({ error: 'answers must contain integers 0-3' });
    }
  }
  if (!VALID_FACTIONS.has(faction)) {
    return res.status(400).json({ error: 'invalid faction' });
  }
  if (!scores || typeof scores !== 'object') {
    return res.status(400).json({ error: 'scores required' });
  }
  for (const k of ['claude', 'gpt', 'gemini', 'grok']) {
    if (typeof scores[k] !== 'number' || scores[k] < 0 || scores[k] > 100) {
      return res.status(400).json({ error: 'scores values invalid' });
    }
  }

  const userContent =
    `answers: [${answers.join(', ')}]\n` +
    `faction: ${faction}\n` +
    `scores: { claude: ${scores.claude}, gpt: ${scores.gpt}, gemini: ${scores.gemini}, grok: ${scores.grok} }`;

  try {
    const client = new Anthropic({ apiKey });

    const response = await client.messages.create({
      model: 'claude-haiku-4-5',
      max_tokens: 1024,
      system: [
        {
          type: 'text',
          text: SYSTEM_PROMPT,
          cache_control: { type: 'ephemeral' },
        },
      ],
      messages: [{ role: 'user', content: userContent }],
    });

    const textBlock = response.content.find((b) => b.type === 'text');
    const analysis = textBlock ? textBlock.text : '';

    if (!analysis) {
      console.error('[analyze] empty response from model');
      return res.status(502).json({ error: 'Empty model response' });
    }

    return res.status(200).json({
      analysis,
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
      console.error('[analyze] upstream 5xx', err.message);
      return res.status(503).json({ error: 'Upstream temporarily unavailable' });
    }
    console.error('[analyze] error', err && err.message);
    return res.status(500).json({ error: 'Analysis failed' });
  }
};
