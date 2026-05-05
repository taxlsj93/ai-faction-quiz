# 📊 STATUS — AI 진영 퀴즈 미디어

> **마지막 업데이트**: 2026-05-06 21:32 UTC
> **사업 단계**: Phase 1 — 런치 직후
> **메인 제품**: ai-faction-quiz (배포 완료)

---

## 🚦 핵심 상태 한눈에

| 영역 | 상태 | 비고 |
|------|------|------|
| 🌐 라이브 배포          | ✅ 작동 중 | https://ai-faction-quiz.vercel.app/ |
| 🐙 GitHub              | ✅ 연결 완료 | https://github.com/taxlsj93/ai-faction-quiz |
| 🔄 Vercel 자동배포     | ✅ **작동 확인** (push→live ~60–90초) | 2026-05-06 21:15 UTC 검증 |
| 📊 분석 도구 (GA4)      | ✅ 작동 중 | `G-HPT1Y41HD8` 설정됨 |
| 📊 분석 도구 (Plausible)| ⚠️ 스캐폴딩만 | 도메인 입력 후 주석 해제 시 활성화 |
| 📊 트래킹 이벤트       | ✅ 구현 | quiz_start / quiz_complete / cta_main_click / cta_secondary_click |
| 💸 광고 (AdSense)      | ✅ 작동 중 | `ca-pub-3036702261797984` |
| 💸 광고 네트워크 (3rd) | ✅ UX 가드 적용 | profitablecpmratenetwork — KO만, 30초 또는 quiz_complete 후 지연 로드, popunder/리다이렉트 차단, 닫기 버튼 |
| 📨 뉴스레터            | ❌ 미설치 | ConvertKit 무료 플랜 권장 |
| 💰 어필리에이트        | ⚠️ 링크 삽입됨 | Jasper / Copy.ai / Writesonic / Perplexity — 실 가입·트래킹 ID 교체 필요 |
| ⚖️ 개인정보처리방침   | ✅ 게재됨 | /privacy (KO), /privacy-en (EN) |
| ⚖️ 어필리에이트 고지  | ✅ 게재됨 | /disclosure (KO+EN, FTC 16 CFR Part 255 준수) |
| 🔍 SEO (robots/sitemap)| ✅ 게재됨 | /robots.txt, /sitemap.xml |
| 🔍 OG / Twitter Cards  | ✅ 완비 | og-image.svg 작동 (1200×630) |
| 🔍 canonical / hreflang| ✅ 완비 | KO/EN/x-default 모두 |

---

## 🛣️ 라이브 라우트 상태표 (검증: 2026-05-06 21:15 UTC)

| 경로 | HTTP | 콘텐츠 |
|------|------|--------|
| `/`            | 200 | KO 메인 퀴즈 (index.html) |
| `/en`          | 200 | EN 메인 퀴즈 (en.html) |
| `/privacy`     | 200 | 개인정보처리방침 KO |
| `/privacy-en`  | 200 | Privacy Policy EN |
| `/disclosure`  | 200 | 어필리에이트 고지 (이중 언어) |
| `/sitemap.xml` | 200 | 검색엔진 사이트맵 |
| `/robots.txt`  | 200 | 크롤러 정책 |
| `/og-image.svg`| 200 | 1200×630 소셜 카드 |

---

## 📂 파일 인벤토리 (정리 후)

### ✅ 운영 중 (메인 제품)

| 파일 | 역할 |
|------|------|
| `index.html`               | 한국어 메인 퀴즈 (구 ai-faction-quiz.html) |
| `en.html`                  | 영어 메인 퀴즈 (구 ai-faction-quiz-en.html) |
| `privacy.html`             | 개인정보처리방침 KO |
| `privacy-en.html`          | Privacy Policy EN |
| `disclosure.html`          | 어필리에이트 고지 (KO + EN) |
| `og-image.svg`             | OG 카드 이미지 |
| `robots.txt`               | 검색엔진 정책 |
| `sitemap.xml`              | 사이트맵 |
| `vercel.json`              | cleanUrls + trailingSlash |

### 📁 deploy/ (백업 — 사용 안 함)

이전 deploy 디렉터리. 현재 Vercel은 **루트 직배포** 사용.
참고용으로 남김.

### 📘 문서

| 파일 | 역할 |
|------|------|
| `CLAUDE.md`        | 사업 지시서 v3.0 |
| `README.md`        | 프로젝트 개요 |
| `STATUS.md`        | 이 문서 (실시간 상태) |

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
| `phoney-war/`           | 헥사곤 영토전 클라이언트/서버 |
| `phoney-war-mvp.html`   | 일일 배틀 MVP |
| `war-map.html`          | 영토전 시각화 |
| `territory-war.html`    | Phase 1 프로토타입 |
| `territory-war-GDD.md`  | 게임 디자인 문서 |

### 🗄️ `_archive/experiments/` (12개 파일 보존)

`battle-visual.html`, `concept-compare.html`, `convert-profile.html`, `format-rerank.html`, `game-format-compare.html`, `gameplay-demo.html`, `insta-promo.html`, `insta-promo2.html`, `living-tiles.html`, `mass-visibility.html`, `team-ops-report.html`, `profile-image.svg`

---

## 📈 진행/완료/보류

### ✅ 완료 (2026-05-05 ~ 05-06)

- 사업 피벗: 헥사곤 게임 → AI 퀴즈 미디어
- 메인 제품 v1.0 한국어/영어 완성 + 배포
- GitHub 레포 + description + topics 11개
- Vercel ↔ GitHub 자동배포 검증 ✅
- README.md, STATUS.md, .gitignore 정비
- Claude Code 에이전트 구조 (총괄 + 4 전문)
- 분석 트래킹 (GA4 가동 + Plausible 스캐폴딩 + 이벤트 4종)
- 개인정보처리방침 KO/EN
- 어필리에이트 고지 (이중 언어, FTC 준수)
- robots.txt, sitemap.xml, OG 이미지 정리
- 실험 파일 12개를 `_archive/experiments/`로 정리

### ⏳ 진행 중

- (없음 — 다음 액션 대기 중)

### 📋 보류

- Phoney War 게임 (Phase 3에서 부활)
- 일일 AI 배틀 투표 기능
- 뉴스레터 시스템

---

## 👉 다음 추천 액션 (우선순위 순)

| # | 액션 | 예상 시간 | 누가 | 상태 |
|---|------|----------|------|------|
| 1 | **어필리에이트 가입**: Jasper, Copy.ai, Writesonic, Perplexity 가입 후 본인 트래킹 ID로 코드 내 `?via=aifaction` 같은 placeholder 교체 | 30분 | 사용자 | 🔴 미진행 |
| 2 | **GA4 이벤트 검증**: realtime view에서 `quiz_start`, `quiz_complete`, `cta_main_click` 이벤트 도착 확인 | 5분 | 사용자 (모바일 가능) | ⏳ 대기 |
| 3 | **Plausible 활성화** (선택): plausible.io 가입 후 `index.html`/`en.html` 의 `data-domain` 채우고 주석 해제 | 10분 | 사용자 | 옵션 |
| 4 | **Search Console 등록**: search.google.com/search-console 에 도메인 등록 + sitemap.xml 제출 | 5분 | 사용자 (모바일 가능) | 🔴 미진행 |
| 5 | **첫 5,000회 트래픽 확보**: 에펨코리아·루리웹·Reddit 게시 (Phase 1 마케팅 로드맵) | 1주 | 사용자 | 🔴 미진행 |
| 6 | **뉴스레터 도입**: ConvertKit 무료 플랜 + 결과 화면 가입 폼 | 1시간 | code-implementer | 보류 |

---

## 🔗 주요 링크

- **라이브**: https://ai-faction-quiz.vercel.app/
- **GitHub**: https://github.com/taxlsj93/ai-faction-quiz
- **개인정보처리방침**: https://ai-faction-quiz.vercel.app/privacy
- **어필리에이트 고지**: https://ai-faction-quiz.vercel.app/disclosure
- **사이트맵**: https://ai-faction-quiz.vercel.app/sitemap.xml
- **사업 컨텍스트**: [CLAUDE.md](CLAUDE.md)
- **개요**: [README.md](README.md)

---

## 🧪 분석 이벤트 명세 (코드 내 구현됨)

| 이벤트 | 트리거 | 파라미터 |
|--------|--------|----------|
| `quiz_start`           | 사용자가 퀴즈 시작 버튼 클릭 | `{lang}` |
| `quiz_complete`        | 결과 화면 진입 직전 | `{faction, lang}` |
| `cta_main_click`       | 1차 CTA(AI 툴 직접 링크) 클릭 | `{faction, url}` |
| `cta_secondary_click`  | 2차 CTA(어필리에이트 링크) 클릭 | `{faction, url}` |
| `affiliate_card_click` | 결과 페이지 인라인 어필리에이트 카드 클릭 (loading-ad / ally tools) | `{url, label, faction}` |
| `ad_network_loaded`    | 3rd-party 광고 스크립트 지연 로드 발화 | `{trigger}` |

GA4(`G-HPT1Y41HD8`)와 Plausible(활성화 시) 양쪽 모두로 자동 전송. 헬퍼: `window.trackEvent(name, params)`.

---

## ⚠️ 알려진 이슈 / 점검 필요

1. **어필리에이트 링크 placeholder** — `?via=aifaction` 같은 임시값이 들어있음. 실제 트래킹 ID로 교체 전까지 수익 추적 불가.
2. **`deploy/` 디렉터리 잔존** — 현재 Vercel은 루트 직배포 사용 중이므로 `deploy/`는 미사용. 향후 정리 가능.
3. **ConvertKit 미설치** — 결과 화면에서 이메일 수집 안 됨. Phase 2 작업.
4. **Search Console 미등록** — 사이트맵을 검색엔진에 직접 알리지 않으면 인덱싱 지연 가능.
