# AI 성향 테스트 미디어 — 개발 지시서 v3.0

> **사업 피벗 확정 (2026-05-05)**: Phoney War 헥사곤 게임 → AI 성향 테스트 미디어로 전환.
> Phoney War는 Phase 3 커뮤니티 이벤트용으로 보류.

---

## 사업 한 줄 요약

성격·직업 퀴즈로 AI 타입(Claude/GPT/Gemini/Grok)를 배정해 소속감을 만들고,
래퍼툴 어필리에이트 + 광고 + 뉴스레터 스폰서로 수익화하는 AI 성향 테스트 미디어.

---

## 핵심 발견 (사업 결정 근거)

### 어필리에이트 현실
| AI 툴 | 공식 어필리에이트 | 현금 수익 |
|-------|----------------|---------|
| Claude | $10 크레딧 (현금 아님) | ❌ |
| ChatGPT | 프로그램 없음 | ❌ |
| Gemini | 소비자 프로그램 없음 | ❌ |
| Grok | 없음 | ❌ |
| **Jasper** (GPT 래퍼) | **25~30% 리커링** | ✅ |
| **Copy.ai** | **30% 리커링** | ✅ |
| **Writesonic** | **30% 리커링** | ✅ |

→ 직접 AI 어필리에이트는 현금 수익 없음. **래퍼툴 어필리에이트**가 실제 수익원.

### 경쟁 공백
- uQuiz "Which AI Are You?" — 바이럴 있으나 수익화 없음
- Creative Bloq/Bloomberg — 에디토리얼 퀴즈, 타입 소속감 없음
- JustPickAI — 기능성 추천, 재미 없음
- **공백**: 타입 소속감 + 바이럴 구조 + 래퍼툴 어필리에이트 = 아무도 없음

---

## 수익 구조

### 단계별 수익원
| Phase | 수익원 | 예상 월 수익 |
|-------|--------|------------|
| Phase 1 (1~2개월) | 래퍼툴 어필리에이트 (Jasper/Copy.ai) | 50~100만원 |
| Phase 2 (3~4개월) | + 디스플레이 광고 (Mediavine, 10K+ 세션 필요) | 100~200만원 |
| Phase 3 (5~6개월) | + 뉴스레터 스폰서 ($500~1,000/회) | 200~300만원 |

### 수익 계산
```
퀴즈 월 완료: 30,000회
래퍼툴 전환율: 2% → 600명
Jasper 평균 커미션: $12.25/유저/월
월 수익: ~$7,350 (~1,050만원) ← 트래픽 확보 후
```

---

## 현재 파일 현황

| 파일 | 상태 | 설명 |
|------|------|------|
| `ai-faction-quiz.html` | **메인 제품 (완성)** | 8문항 AI 성향 테스트, 실제 통계 기반 |
| `phoney-war-mvp.html` | 보류 | 일일 배틀 MVP (Phase 3 활용) |
| `war-map.html` | 보류 | 헥사곤 영토전 시각화 |
| `territory-war.html` | 아카이브 | Phase 1 프로토타입 |
| `income-strategy-notes.md` | 전략 메모 | 수입 파이프라인 전략 논의 요약 (2026-05-23 세션) |

---

## ai-faction-quiz.html 스펙

### 퀴즈 구조
- 6문항 × 4지선다
- 각 선택지에 Claude/GPT/Gemini/Grok 점수 배분
- 로딩 애니메이션 후 결과 화면

### 결과 화면 구성
1. 타입 아이콘 + 이름 + 태그라인
2. 특성 바 4개 (애니메이션)
3. 타입 통계 카드 (실제 데이터 기반)
4. 타 타입과의 차이 비교
5. 1차 CTA: AI 툴 직접 링크
6. 2차 CTA: 래퍼툴 어필리에이트 링크 (실수익원)
7. 공유 버튼 + 다시 테스트

### 실제 통계 출처
- DemandSage, First Page Sage, fatjoe, Views4You (2025~2026)
- Claude: 18.9M MAU, 34.7분/일 평균세션 (전체 AI 1위), +190% YoY
- GPT: ~1B MAU, 45% 모바일 점유, 25~34세 최다
- Gemini: ~750M MAU, +70.7% 성장, 상품조사 46% 활용
- Grok: 50~64M MAU, +1,343,408% 방문자 YoY

### 어필리에이트 링크 매핑
| 타입 | 2차 CTA | 수익 구조 |
|-------|---------|---------|
| Claude 타입 | jasper.ai | 25~30% 리커링 |
| GPT 타입 | jasper.ai | 25~30% 리커링 |
| Gemini 타입 | writesonic.com | 30% 리커링 |
| Grok 타입 | perplexity.ai | 확인 필요 |

---

## 3단계 마케팅 로드맵

### Phase 1 — 런치 (지금 ~ 2주)
**목표**: 첫 5,000회 퀴즈 완료

배포:
- Vercel 무료 배포 (vercel.com)
- 도메인: whichaitype.com / ai-type.quiz / aitype.kr 등 검토

배포 채널:
- 한국: 에펨코리아, 루리웹, 클리앙 자유게시판
- 영어: Reddit r/artificial, r/ChatGPT, r/MachineLearning
- SNS: X/Twitter, 카카오톡 오픈채팅

SEO 타겟 키워드:
- "어떤 AI가 나한테 맞아"
- "Claude vs ChatGPT 차이"
- "which AI should I use quiz"
- "AI 성격 테스트"

### Phase 2 — 콘텐츠 엔진 (1~2개월)
**목표**: 월 10,000+ 세션 (광고 수익 기준점)

- SEO 블로그 5~10편 (AI 작성 + 인간 편집)
- 결과 공유 이미지 OG 카드 생성 기능 추가
- 뉴스레터 수집 시작 (ConvertKit 무료 플랜)

### Phase 3 — 커뮤니티화 (3~4개월)
**목표**: 뉴스레터 1,000명, 스폰서 첫 계약

- 일일 AI 배틀 투표 기능 ("오늘의 타입 대결")
- Phoney War 게임을 커뮤니티 이벤트로 부활
- AI 회사 직접 스폰서십 접촉

---

## 법률 체크리스트

- [ ] "Claude", "ChatGPT", "Gemini", "Grok" 명칭 — 설명적 언급은 허용, 상표로 오인될 소지 없게
- [ ] 통계 데이터 출처 표기 (푸터에 "Based on publicly available data")
- [ ] 어필리에이트 관계 고지 ("이 페이지는 제휴 링크를 포함합니다")
- [ ] 개인정보처리방침 (분석 도구 사용 시)
- [ ] 면책 문구: "This quiz is for entertainment. Not affiliated with Anthropic, OpenAI, Google, or xAI."

---

## 기술 스택

- **프론트엔드**: Vanilla JS + HTML/CSS (단일 파일)
- **배포**: Vercel (무료)
- **분석**: Google Analytics 또는 Plausible (무료)
- **뉴스레터**: ConvertKit (무료 1,000명까지)
- **서버**: 없음 (정적 파일)

---

## Phoney War (보류)

기존 헥사곤 영토전 게임. Phase 3에서 AI 성향 테스트 미디어의 커뮤니티 이벤트로 부활 예정.
기기 감지(iOS/Android) 대신 퀴즈 타입 결과를 활용하는 방향 검토.

`phoney-war/` 디렉토리 및 관련 파일은 삭제하지 않고 보존.

---

## 브랜드 용어 정책 (모든 에이전트 필독)

> **이 섹션은 모든 에이전트·작업자가 반드시 준수해야 하는 용어 기준입니다.**
> 코드 작성, 카피 작성, 게시글 초안, 문서 작성 등 모든 작업에 적용됩니다.

### 핵심 원칙
- **사용자 노출 텍스트**: 반드시 **타입 / Type** 사용
- **코드 내부 변수·CSS 클래스·URL**: `faction` 유지 (변경 금지 — 버그·SEO 손실)
- **SEO 메타 keywords 태그**: "진영 / faction / house" 병기 허용 (검색 유입 목적)

### 확정 용어표

| 구분 | 한국어 ✅ | 영어 ✅ | 금지 한국어 ❌ | 금지 영어 ❌ |
|------|---------|--------|------------|-----------|
| 사이트명 | AI 성향 테스트 | AI Personality Quiz | AI 진영 퀴즈 | AI Faction Quiz |
| 부제 | 당신의 AI 타입은? | Which AI Type Are You? | 당신의 AI 진영은? / 당신의 AI 하우스는? | Which AI Faction Are You? / Which AI House Are You? |
| 소속 단위 | 타입 | Type | 진영/하우스 | Faction/House |
| Claude | Claude 타입 | Claude Type | Claude 진영/Claude 하우스 | Claude Faction/Claude House |
| GPT | GPT 타입 | GPT Type | GPT 진영/GPT 하우스 | GPT Faction/GPT House |
| Gemini | Gemini 타입 | Gemini Type | Gemini 진영/Gemini 하우스 | Gemini Faction/Gemini House |
| Grok | Grok 타입 | Grok Type | Grok 진영/Grok 하우스 | Grok Faction/Grok House |
| 메인 해시태그 | #AI타입테스트 | #AITypeTest | #AI진영테스트 / #AI하우스테스트 | #AIFactionQuiz / #AIHouseTest |
| 결과 해시태그 | #Claude타입 등 | #ClaudeType 등 | #Claude진영 / #Claude하우스 등 | #ClaudeFaction / #ClaudeHouse 등 |
| CTA 버튼 | 내 AI 타입 알아보기 → | Find My AI Type → | 내 AI 진영/하우스 알아보기 | Find My Faction/House |

### 변경 불필요 항목 (코드 내부)
아래 항목은 사용자에게 노출되지 않으므로 `faction` 유지:
- JS 변수: `resultFaction`, `faction:` 파라미터
- CSS 클래스: `.faction-chip`, `.faction-claude` 등
- GA4 이벤트 파라미터: `faction:`
- Vercel URL: `ai-faction-quiz.vercel.app`

### 어필리에이트 링크 현황 (2026-05-09 기준)
| 타입 | CTA 2차 URL | 트래킹 |
|------|------------|--------|
| Claude 타입 | writesonic.com/?via=aifaction | ✅ |
| GPT 타입 | writesonic.com/?via=aifaction | ✅ |
| Gemini 타입 | writesonic.com/?via=aifaction | ✅ |
| Grok 타입 | perplexity.ai/?via=aifaction | ✅ |

> 상세 가이드: `brand-guide.html` 참조
