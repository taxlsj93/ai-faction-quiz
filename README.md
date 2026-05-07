# AI 성향 테스트 (Which AI House?)

성격·직업 기반 8문항 퀴즈로 사용자의 **AI 타입(Claude / GPT / Gemini / Grok)** 를 배정해주는 미디어형 웹 제품입니다.
타입 소속감 + 실제 통계 기반 결과 화면 + 래퍼툴 어필리에이트 수익 구조를 결합했습니다.

🌐 **Live**: https://ai-faction-quiz.vercel.app/

---

## 핵심 특징

- **8문항 × 4지선다** — 각 선택지에 4개 타입 점수 가중치
- **실제 통계 기반 결과 화면** — DemandSage / First Page Sage / Views4You (2025–2026) 데이터 활용
- **이중 CTA 구조** — 1차: AI 툴 직접 링크 / 2차: 래퍼툴 어필리에이트 (Jasper, Copy.ai, Writesonic 등)
- **이중 언어** — 한국어 / 영어 동시 운영
- **경량 정적 사이트** — Vanilla JS + HTML/CSS, 단일 파일 구조

---

## 빠른 실행

### 로컬에서 열기
```bash
# 한국어 버전
start ai-faction-quiz.html        # Windows
open  ai-faction-quiz.html        # macOS

# 영어 버전
start ai-faction-quiz-en.html
```

### 배포 (Vercel)
```bash
# deploy/ 디렉터리를 Vercel에 연결하면 됨 (정적 호스팅)
# 자동배포는 main/master 브랜치 push 시 트리거되도록 GitHub 연동 권장
```

---

## 파일 구조

| 경로 | 상태 | 설명 |
|------|------|------|
| `ai-faction-quiz.html`     | ✅ 메인 (KO) | 한국어 퀴즈 |
| `ai-faction-quiz-en.html`  | ✅ 메인 (EN) | 영어 퀴즈 |
| `deploy/index.html`        | ✅ 배포본 KO | Vercel용 cleanUrls 구성 |
| `deploy/en.html`           | ✅ 배포본 EN | |
| `deploy/og-image.svg`      | ✅ | OG 카드 이미지 |
| `deploy/vercel.json`       | ✅ | `cleanUrls`, `trailingSlash:false` |
| `CLAUDE.md`                | 📘 | 사업 지시서 v3.0 |
| `STATUS.md`                | 📊 | 사업/배포 상태 대시보드 |
| `territory-war-GDD.md`     | 📦 보류 | Phoney War 게임 디자인 문서 |
| `phoney-war/`              | 📦 보류 | Phase 3 커뮤니티 이벤트용 헥사곤 영토전 |
| `phoney-war-mvp.html`      | 📦 보류 | 일일 배틀 MVP 프로토타입 |
| `war-map.html`             | 📦 보류 | 헥사곤 영토전 시각화 |
| `territory-war.html`       | 📦 아카이브 | Phase 1 프로토타입 |
| `.claude/agents/`          | 🤖 | Claude Code 에이전트 정의 (총괄 + 전문) |

---

## 수익 구조 요약

| Phase | 수익원 | 예상 월 수익 |
|-------|--------|------------|
| 1 (1–2개월)  | 래퍼툴 어필리에이트 (Jasper / Copy.ai)         | 50–100만원   |
| 2 (3–4개월)  | + 디스플레이 광고 (Mediavine, 10K+ 세션 필요)   | 100–200만원  |
| 3 (5–6개월)  | + 뉴스레터 스폰서 ($500–1,000/회)             | 200–300만원  |

자세한 사업 컨텍스트는 [`CLAUDE.md`](CLAUDE.md), 실시간 상태는 [`STATUS.md`](STATUS.md) 참고.

---

## 면책 / 라이선스

This quiz is for entertainment. Not affiliated with Anthropic, OpenAI, Google, or xAI.
통계 데이터는 공개된 출처(DemandSage 등) 기반입니다.

이 페이지는 제휴 링크를 포함합니다.
