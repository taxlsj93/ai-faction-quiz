# 런치 카피 모음

> Phase 1 목표: 첫 5,000회 퀴즈 완료
> 메인 URL: https://ai-faction-quiz.vercel.app/ (도메인 확정 후 교체)

---

## 한국어 (Korean)

### 에펨코리아 / 루리웹 / 클리앙 자유게시판

**제목**: 8문항으로 너랑 맞는 AI 찾아주는 성향테스트 만듦

```
요즘 Claude / ChatGPT / Gemini / Grok 다 써보면서 어디가 나랑 제일 맞나
궁금해서 8문항 짜리 테스트로 만들어봤다.

각 AI 회사가 쓰는 사람 통계도 같이 박아놨음 — 예를 들면 Claude
유저가 평균 세션 34.7분으로 AI 중에 1위라 하더라. 의외였음.

해보고 결과 공유해주면 어떤 타입 분포 나오는지 볼 수 있을듯.
👉 https://ai-faction-quiz.vercel.app/

광고 없고 가입 없음. 결과 공유 카드도 자동 생성됨.
```

---

### X(Twitter) / Threads — 한국어

```
8문항으로 너랑 맞는 AI(Claude·ChatGPT·Gemini·Grok) 찾아줌.

결과 페이지에 답변 패턴 기반 개인 분석 + AI한테 직접 채팅 기능까지 붙어있음.

너는 어떤 타입?
👉 https://ai-faction-quiz.vercel.app/

#AI성향테스트 #Claude #ChatGPT #Gemini #Grok
```

---

### 카카오톡 오픈채팅 / 슬랙

```
🧠 AI 성향 테스트 만들었어요
8문항으로 Claude / GPT / Gemini / Grok 중 어떤 타입인지 알려줍니다.
실제 사용자 통계 + 결과 캐릭터랑 채팅 기능까지 붙어있어요.
👉 https://ai-faction-quiz.vercel.app/
```

---

## English

### Reddit r/artificial / r/ChatGPT / r/ArtificialInteligence

**Title**: I built an 8-question quiz to figure out which AI matches your personality (Claude/ChatGPT/Gemini/Grok)

```
Hey folks — I kept noticing people defaulting to one AI tool and wondering
if they'd actually click better with another, so I built a quick personality
test that maps your answers to Claude / ChatGPT / Gemini / Grok.

What's in it:
- 8 questions, ~2 minutes
- Real usage stats per AI (e.g. Claude users average 34.7 min/session,
  highest of any AI tool — was surprised)
- Result page has a personalized breakdown ("why YOU specifically got
  this result") + you can chat with the AI persona you matched
- Per-type share cards if you want to compare with friends

No ads, no signup, no email gate.

👉 https://ai-faction-quiz.vercel.app/?lang=en

Curious which one you get — drop your result in the comments?
```

---

### r/MachineLearning (more measured tone)

**Title**: Personality quiz that maps user answers to Claude/GPT/Gemini/Grok — built with Haiku 4.5 for personalized post-quiz analysis

```
Built a quick consumer-facing project that uses an LLM at the result step
rather than during the quiz itself. Quiz is deterministic (8 questions,
fixed weights → top-scoring AI). After result is shown, optional Haiku 4.5
call generates a personalized analysis based on the specific answer pattern.

Tech notes:
- Vanilla JS / single-page, deployed on Vercel
- Serverless function for analyze + chat endpoints
- Ephemeral prompt caching (~90% input cost reduction)
- Multi-turn chat with the matched AI's persona, capped at 5 messages

Stats embedded in results pulled from public sources (DemandSage, First Page
Sage, Views4You — 2025/2026).

👉 https://ai-faction-quiz.vercel.app/?lang=en

Open to feedback on the persona prompts especially — keeping each character
distinct in 200~400 chars per turn was the trickiest part.
```

---

### X(Twitter) — English

```
Built an 8-question quiz that tells you which AI matches you:
Claude / ChatGPT / Gemini / Grok.

Includes real usage stats + you can chat with your matched AI's
persona right on the result page.

Which one are you?
👉 https://ai-faction-quiz.vercel.app/?lang=en

#WhichAIType #Claude #ChatGPT #Gemini #Grok
```

---

## SEO 타겟 검색어 (참고)

**한국어**:
- 어떤 AI가 나한테 맞아
- AI 성향 테스트
- Claude vs ChatGPT 차이
- AI 성격 테스트

**English**:
- which AI should I use quiz
- which AI matches my personality
- Claude vs ChatGPT personality test
- AI personality quiz

---

## 배포 시점 체크리스트

- [ ] PR 생성 → master 머지 → 프로덕션 배포 확인
- [ ] 도메인 연결 (`whichaitype.com` 권장, $11.25/년)
- [ ] OG 카드 4종 + 메인 OG 실제 공유 시 미리보기 확인
- [ ] AdSense 승인 상태 확인
- [ ] 첫 채널 1곳에 1회 포스팅 → 24h 후 트래픽·이탈률 측정
