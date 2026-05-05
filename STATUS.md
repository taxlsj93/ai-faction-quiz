# 📊 STATUS — AI 진영 퀴즈 미디어

> **마지막 업데이트**: 2026-05-06
> **사업 단계**: Phase 1 — 런치 직후
> **메인 제품**: ai-faction-quiz (배포 완료)

---

## 🚦 핵심 상태 한눈에

| 영역 | 상태 | 비고 |
|------|------|------|
| 🌐 라이브 배포   | ✅ 작동 중 | https://ai-faction-quiz.vercel.app/ |
| 🐙 GitHub       | ✅ 연결 완료 | https://github.com/taxlsj93/ai-faction-quiz |
| 🔄 자동배포     | ⚠️ 점검 필요 | Vercel ↔ GitHub 연동 상태 사용자 확인 권장 |
| 📊 분석 도구    | ❌ 미설치 | GA4 / Plausible 도입 필요 |
| 📨 뉴스레터     | ❌ 미설치 | ConvertKit 무료 플랜 권장 |
| 💰 어필리에이트 | ⚠️ 링크만 삽입 | 실제 가입·승인 필요 (Jasper, Copy.ai 등) |

---

## 📂 파일 인벤토리

### ✅ 운영 중 (메인 제품)

| 파일 | 역할 |
|------|------|
| `ai-faction-quiz.html`     | 한국어 메인 퀴즈 |
| `ai-faction-quiz-en.html`  | 영어 메인 퀴즈 |
| `deploy/index.html`        | Vercel 배포 KO |
| `deploy/en.html`           | Vercel 배포 EN |
| `deploy/og-image.svg`      | OG 카드 이미지 |
| `deploy/vercel.json`       | cleanUrls / trailingSlash |

### 📘 문서

| 파일 | 역할 |
|------|------|
| `CLAUDE.md`        | 사업 지시서 v3.0 |
| `README.md`        | 프로젝트 개요 |
| `STATUS.md`        | 이 문서 (실시간 상태) |
| `territory-war-GDD.md` | 보류 게임 GDD |

### 🤖 Claude Code 에이전트 정의

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| `coordinator`       | opus    | 총괄, 작업 분해·라우팅 |
| `code-implementer`  | sonnet  | HTML/CSS/JS 구현 |
| `doc-writer`        | sonnet  | README/카피/문서 |
| `researcher`        | haiku   | 코드·외부 데이터 조사 |
| `reviewer`          | sonnet  | 품질·보안 검증 |

### 📦 보류 (Phase 3 부활 예정)

| 파일/디렉터리 | 상태 |
|---------------|------|
| `phoney-war/`           | Phase 3 커뮤니티 이벤트용 헥사곤 영토전 |
| `phoney-war-mvp.html`   | 일일 배틀 MVP 프로토타입 |
| `war-map.html`          | 영토전 시각화 |
| `territory-war.html`    | Phase 1 프로토타입 |

### 🗑️ 정리 후보 (실험·탐색용 — 미커밋)

| 파일 | 비고 |
|------|------|
| `battle-visual.html`         | 시각 실험 |
| `concept-compare.html`       | 컨셉 비교 |
| `convert-profile.html`       | 프로필 변환 |
| `format-rerank.html`         | 포맷 실험 |
| `game-format-compare.html`   | 게임 포맷 비교 |
| `gameplay-demo.html`         | 게임플레이 데모 |
| `insta-promo.html`, `insta-promo2.html` | 인스타 홍보 시안 |
| `living-tiles.html`          | 타일 실험 |
| `mass-visibility.html`       | 가시성 실험 |
| `team-ops-report.html`       | 팀 작업 리포트 |
| `profile-image.svg`          | 프로필 이미지 시안 |

→ 커밋 안 됨, 실험 끝나면 삭제 또는 `_archive/`로 이동 권장

---

## 📈 진행/완료/보류

### ✅ 완료 (2026-05-05 ~ 05-06)

- 사업 피벗: 헥사곤 게임 → AI 퀴즈 미디어
- 메인 제품 v1.0 한국어/영어 완성
- Vercel 배포 (라이브 URL 작동)
- GitHub 레포 생성 + 초기 커밋 push
- README.md, STATUS.md, .gitignore 정비
- Claude Code 에이전트 구조 (총괄 + 4 전문) 정의

### ⏳ 진행 중

- (없음 — 다음 액션 대기 중)

### 📋 보류

- Phoney War 게임 (Phase 3에서 부활)
- 일일 AI 배틀 투표 기능
- 뉴스레터 시스템

---

## 👉 다음 추천 액션 (우선순위 순)

| # | 액션 | 예상 시간 | 누가 |
|---|------|----------|------|
| 1 | **Vercel ↔ GitHub 자동배포 연결**: vercel.com → 프로젝트 → Settings → Git → Connect Git Repository → `taxlsj93/ai-faction-quiz` 선택 | 5분 | 사용자 (모바일 가능) |
| 2 | **어필리에이트 가입**: Jasper, Copy.ai, Writesonic 가입 후 실제 트래킹 링크로 코드 내 placeholder 교체 | 30분 | 사용자 + code-implementer |
| 3 | **분석 도구 설치**: GA4 또는 Plausible 스니펫을 `ai-faction-quiz*.html` 헤드에 삽입 | 15분 | code-implementer |
| 4 | **첫 5,000회 트래픽 확보**: 에펨코리아·루리웹·Reddit 게시 (Phase 1 마케팅 로드맵) | 1주 | 사용자 |
| 5 | **GA 이벤트 정의**: 퀴즈 시작·완료·CTA 클릭 이벤트 트래킹 | 30분 | code-implementer |

---

## 🔗 주요 링크

- **라이브**: https://ai-faction-quiz.vercel.app/
- **GitHub**: https://github.com/taxlsj93/ai-faction-quiz
- **사업 컨텍스트**: [CLAUDE.md](CLAUDE.md)
- **개요**: [README.md](README.md)

---

## ⚠️ 알려진 이슈 / 점검 필요

1. **Vercel ↔ GitHub 자동배포 미확인** — 현재 `ai-faction-quiz.vercel.app` 가 어떤 소스로 배포되고 있는지(직접 업로드 vs CLI vs GitHub) 확인 필요. 위 액션 #1로 GitHub 연동 권장.
2. **어필리에이트 링크 placeholder** — 실제 트래킹 ID로 교체 전까지 수익 추적 불가.
3. **법률 체크리스트 일부 미완** — 분석 도구 설치 시 개인정보처리방침 추가 필요.
