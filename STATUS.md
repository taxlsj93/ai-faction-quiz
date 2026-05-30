# 📊 STATUS — AI 성향 테스트 미디어

> **마지막 업데이트**: 2026-05-27 (세션 5 — 리뉴얼 Phase 1 완료)
> **사업 단계**: Phase 1 (리뉴얼 진행 중) — Phase 2 진입 예정
> **메인 제품**: ai-faction-quiz (배포 완료)

---

## 🆕 세션 5 (2026-05-27) — 리뉴얼 Phase 1+2 라이브 완료

진단(IMPROVEMENT_NOTES.md) + designer 진단(DESIGN_AUDIT.md) + ralplan v3.2 consensus 합의
→ **12 커밋, 14 surface, 8 신규 GA4 이벤트** 라이브 반영.

### Phase 1 (어트리뷰션 안전·외부 자격 무의존)
| 커밋 | 의미 | 라이브 |
|------|------|------|
| C0  `5f148b7` chore: 워크트리 정리 | IMPROVEMENT_NOTES + CLAUDE.md(M) + reports archive | ✅ |
| C1a `43dfe59` feat(og): SVG→PNG 14 surface + dead SVG 삭제 | 공유 미리보기 부활 (FB·X·카카오 OG 지원) | ✅ /og-image.png 200, image/png, 112.5KB |
| C1b `50f0c1b` chore(build): build-og.mjs + devDep | 재현성용 puppeteer-core 빌드 | ✅ |
| C2  `9fcaf18` fix(a11y): viewport 핀치줌 | WCAG 1.4.4 해소 | ✅ |
| C5a `35fc85b` refactor(affiliate): window.AFFILIATE 단일 소스 | URL 무변경, U1 받으면 1줄 교체 | ✅ |
| C9p1 `c9d1c2b` docs Phase 1 | STATUS·HANDOFF 갱신 | ✅ |

### Phase 2 (수익·재방문 attribution-safe)
| 커밋 | 의미 | 라이브 |
|------|------|------|
| C8  `edc933e+1bc14b8` feat(en): /en URL atomic 통일 | rewrite + per-LANG canonical + en.html DELETE + launch-copy.md | ✅ /en EN content, /en.html 308 |
| C7  `b8218d9` feat(quiz): 옵션 셔플 + 선택 피드백 | display-only shuffle, 백엔드 contract 보존 | ✅ |
| C3  `eff1cca` feat(result): 보조타입 배지 + 백분위 + 친구비교 + 공유 상단 부상 | designer #2·#6, 시선 1초 단축 | ✅ result-secondary-badge·share-section id 라이브 |
| C4  `4202508` feat(share): /r/{4} 재공유 CTA + 모바일 패딩 | designer #5, 2차 확산 루프 | ✅ "친구는 무슨 타입" 버튼 라이브 |
| C6  `32a0b54` feat(newsletter): ConvertKit form (placeholder-gated) | designer #4, U2 받으면 1줄 활성 | ✅ inert mode 동작 |

### 신규 GA4 이벤트 (사용자 작업 U4에서 전환 표시 권장)
- `secondary_type_shown {faction, secondary, pct}`
- `friend_compare_row_shown {faction}`
- `landing_take_quiz_click {faction}`
- `landing_reshare_click {faction}`
- `newsletter_widget_inert {faction}` (placeholder 상태)
- `newsletter_widget_shown {faction}` (실 ID 활성 시)
- `newsletter_subscribed {faction}`
- `newsletter_failed {faction, reason}`

### 사용자 작업 큐 (모바일에서 모두 가능, 우선순위 순)

| # | 작업 | 어디서 | 효과 |
|---|------|--------|------|
| 🔴 **U3** | FB Sharing Debugger·X Card Validator·카카오 디버거에서 `/`, `/en`, `/r/{claude,gpt,gemini,grok}` 강제 캐시 무효화 | developers.facebook.com/tools/debug · cards-dev.twitter.com/validator · developers.kakao.com | 새 PNG 미리보기 즉시 노출 (현재 캐시는 옛 SVG) |
| 🟠 **U1** | 어필리에이트 실 ID 4종 확인 → `window.AFFILIATE` 1곳 교체 지시 | Writesonic / Perplexity / Copy.ai 대시보드 (Jasper는 옵션) | C5b 진행 가능. 수익 누락 0 |
| 🟡 **U2** | ConvertKit 무료 가입 → form 생성 → form ID → `window.CONVERTKIT_FORM_ID` 1줄 교체 지시 | convertkit.com | C6 즉시 활성, 일회성 트래픽 구독 자산화 |
| 🟡 **U4** | GA4에서 `quiz_complete`·`cta_secondary_click`·`chat_opened`·`landing_take_quiz_click`·`newsletter_subscribed`를 전환 이벤트로 표시 + Search Console에 sitemap 제출 | analytics.google.com · search.google.com | 데이터로 의사결정 가능 |
| ⚪ **U5** | GitHub Settings → Secrets → `ANTHROPIC_API_KEY` 등록 | github.com/taxlsj93/ai-faction-quiz/settings/secrets | .github/ 워크플로 별도 커밋 가능 |

---

## 🆕 세션 6 (2026-05-28) — v4.3 리뉴얼 (claude.ai 크림 톤 + 환상 부여 + 공유 강화)

`/ralplan v4.3` 합의(Architect ITERATE → Critic ITERATE 2 라운드 → ACCEPT)로
22 커밋 5 Phase 자율 실행. 직전 세션 5(19 커밋) → 세션 6 끝 **41 커밋**.

### Phase A — 디자인 시스템 (6 커밋)
| 커밋 | 효과 |
|---|---|
| A1 `6554426` | claude.ai 크림 톤 신규 토큰 (cream/white/ink/plum/serif) |
| A1b `4d49c18` | --muted 36곳 → --ink-secondary rename + snapshot-diff infra |
| A2 `cd25881` | dev-only quiz contract assertion |
| A2-fix `5bc483b` | sum>5 완화 + type max=24 검증 추가 |
| A3 `11f63af` | Google Fonts (Fraunces + Inter) preconnect + display=swap |
| A4 `477af76` | body font-family + form/::selection 토큰화 |

### Phase C — 콘텐츠 + 환상 부여 (5 커밋)
| 커밋 | 효과 |
|---|---|
| C1 `38789ad` | QUESTIONS 8문항 시나리오형 재작성 (AI 단어 0회, 일상) |
| C2 `4ddbe38` | 슈퍼파워 3 카드 + GA4 super_powers_shown |
| C3 `9a4a4a8` | "이 AI로 할 수 있는 5" 카드 + GA4 tool_picks_shown |
| C4 `dd23dd1` | "지금 당장 1가지" 첫 액션 카드 + GA4 first_action_shown |
| C5a `56bb61b` | api/chat.js SYSTEM_PROMPT Q1-Q8 동기화 (silent regression 차단) |

### Phase B — Visual 전환 (6 커밋)
| 커밋 | 효과 |
|---|---|
| B1 `fa6a34f` | :root legacy 다크 → 크림 톤 + intro-title serif (글로벌 한 번에) |
| B2 `b6d4551` | quiz 화면 (option-btn·progress·btn-start·q-text serif) |
| B3 `0fe30f4` | loading 화면 (ring·text serif) |
| B4 `9ee30df` | result 화면 (faction-name serif + CTA shadow + secondary CTA·banner 토큰) |
| B5 `0f9ba0d` | /r/{faction} 4종 크림 톤 (legacy :root 교체 + 카드 border 알파) |
| B6 `eb0b633` | chat·newsletter·analysis 카드 통일 (Phase B 마감) |

### Phase D — 공유 강화 (3 커밋, D1+D2 묶음)
| 커밋 | 효과 |
|---|---|
| D1+D2 `8abc85b` | 새 크림 톤 OG SVG 5장 + PNG 재생성 (73-82KB) + build 200KB hard gate |
| D3 `72ae934` | 인스타 1080×1080 캔버스 크림 톤 + KO 시스템 폰트 폴백 (Arial 제거) |
| D4 `7ff9238` | share-copy.js IIFE 단일 소스 (r/{4} 카피 1곳 통합) |

### Phase E — 검증·문서 (2 커밋)
| 커밋 | 효과 |
|---|---|
| E1 (이 커밋과 통합) | 라이브 헬스체크 — / cream 배경·OG PNG 200·73.6KB 확인 |
| E2 (이 커밋) | STATUS·HANDOFF·DESIGN_AUDIT_v2.md 갱신 |

### 신규 GA4 이벤트 (Phase C/D 추가)
- super_powers_shown {faction}
- tool_picks_shown {faction}
- first_action_shown {faction}

### 시각·기능 변화 요약 (사용자 모바일 체감)
- 다크 → claude.ai 크림 톤 전면 전환 (cream/white/ink + 보라 액센트)
- 헤딩 serif (영어 부분 Fraunces 적용, 한글은 시스템 폰트 — Fraunces 한글 글리프 없어 자동 폴백)
- 8문항 시나리오형 (월요일 아침·새벽 카톡·카페·단톡방 등 일상)
- 결과 화면 환상 3-stack: 슈퍼파워 3 → 할수있는것 5 → 지금당장 1
- OG 카드 새 크림 톤 (FB·X·카카오 미리보기에 적용)
- 인스타 캔버스 톤 일치 + 한글 자형 안정화

### 알려진 제약 (Phase 3 백로그 후보)
- Fraunces serif는 한글 글리프 없음 → 한글 헤딩은 시스템 폰트로 fallback (Apple SD Gothic Neo / Malgun Gothic). claude.ai serif 톤은 영어 부분에서만 충실 적용.
- 한글 serif 헤딩 원할 시 Noto Serif KR 또는 IBM Plex Serif KR 추가 검토 (폰트 ~150KB 추가, LCP 영향)

### 사용자 작업 큐 (모바일에서 모두 가능)

| # | 작업 | 어디서 | 효과 |
|---|------|--------|------|
| 🔴 U3 즉시 | FB Sharing Debugger·X Card Validator·카카오 디버거에서 5 URL 강제 캐시 무효화 | developers.facebook.com/tools/debug<br>cards-dev.twitter.com/validator<br>developers.kakao.com | 새 크림 톤 PNG 즉시 노출 |
| U1 | 어필리에이트 실 ID → C5b 진행 (다음 세션) | Writesonic·Perplexity·Copy.ai | 수익 누락 0 |
| U2 | ConvertKit form ID → C6 활성 (inert 가드 중) | convertkit.com | 뉴스레터 즉시 |
| U4 | GA4 신규 11 이벤트 전환 표시 + Search Console | analytics.google.com | 데이터→의사결정 |
| U5 | GitHub Secrets `ANTHROPIC_API_KEY` | github.com/settings/secrets | .github/ 별도 |

---

### 세션 5 후속 — Codex 리뷰 핫픽스 (F1~F6, 6 커밋 추가)

`/codex` 두 번째 패스 리뷰에서 High 2건 + Medium 3건 + Low 1건 + Missing 3건 발견 → 모두 반영.

| 커밋 | 의미 |
|------|------|
| F1+F3 `d21d549` fix(share+affiliate) | **자해 차단**: /r/{faction} 재공유가 root URL을 트윗하던 버그 → 각 faction URL로 (faction OG 회복). EN Grok CTA raw URL → AFFILIATE.PERPLEXITY |
| F2 `cc2229a` fix(newsletter) | 버튼 배경 대비 버그 (`currentColor` × `color:#fff` → 흰=흰) → CSS 변수 `--faction-color`로 분리 |
| F4 `07cb6fa` fix(en) | **/en SEO 회귀 차단**: JS 미실행 크롤러(Bing/Naver/Yandex/일부 봇)가 KO 메타 받던 문제 → en.html 정적 EN 메타 페이지로 부활, 사용자는 JS replace로 /?lang=en 이동 |
| F5 `4cbce36` fix(chat) | C7 셔플 후 챗이 letter(A/B/C/D) 인용 시 사용자 화면과 불일치 → SYSTEM_PROMPT에서 letter 매핑 제거, 성향(0=Claude/1=GPT/2=Gemini/3=Grok)+요지로만 인용 강제 |
| F6 `0c9b209` refine | 로딩 700→500ms + 결과 타입 컬러 ring (designer #3) / 챗 진입 버튼 alpha 0.15→0.25 (designer #7) / 친구비교 "(추정)" 명시 (Codex Low) |

이제 master는 **19 커밋**으로 안정화. 남은 작업은 C5b(U1 게이트) 단 1개.

### Phase 3 백로그 (별도 세션)
1. window.AFFILIATE에서 click-delegation regex 자동 파생
2. @vercel/og 동적 OG (점수·MBTI 카드에 박기)
3. 비교/블로그 콘텐츠 엔진 ("Claude vs ChatGPT 차이" 등)
4. Phoney War 게임 부활 (커뮤니티 이벤트)
5. AdSense 수동 유닛 (승인 후)
6. 인스타 캔버스 한글 폰트 폴백
7. per-LANG /r/{faction} 4종 (EN bounce 관측 시)
8. (designer #8) 인트로 "현재 쓰는 AI 선택" 가치 전달 강화
9. 친구비교 baseline을 GA4 실데이터로 교체 (quiz_complete 분포 누적 후)

### 무손상 보존 확인
- profitablecpm 주석 (index.html:37-102): 미접촉 ✅
- GA4 `G-HPT1Y41HD8`: 무변경 ✅
- Plausible 스캐폴딩: 무변경 ✅
- 데스크톱 max-width:480px 컨테이너: 무변경 ✅

---

> ⚠️ **세션 4 메모**: 제품과 무관한 **개인 요청(기초화장품 사업 로드맵)** 작업.
> 산출물 `cosmetics-business-plan.md` / `cosmetics-roadmap.html` / `cosmetics-roadmap.pdf` 가 master에 추가됨(제품 아님). 상세는 `HANDOFF.md` §13.

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
| 💰 어필리에이트        | ⚠️ 단일 소스 리팩 완료 (URL 무변경) | `window.AFFILIATE` 1곳 — U1 받으면 1줄로 전체 교체 |
| ⚖️ 개인정보처리방침   | ✅ 게재됨 | /privacy (KO), /privacy-en (EN) |
| ⚖️ 어필리에이트 고지  | ✅ 게재됨 | /disclosure (KO+EN, FTC 16 CFR Part 255 준수) |
| 🔍 SEO (robots/sitemap)| ✅ 게재됨 | /robots.txt, /sitemap.xml |
| 🔍 OG / Twitter Cards  | ✅ **PNG로 전환** (세션 5) | og-image.png + og/{4}.png (1200×630, ≤200KB) — FB·X·카카오 미리보기 정상 |
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

### 🧾 별도 산출물 — 제품 외 (세션 4, 개인 요청)

| 파일 | 역할 |
|------|------|
| `cosmetics-business-plan.md`  | 기초화장품 브랜드 창업 로드맵 (텍스트 원본) |
| `cosmetics-roadmap.html`      | 위 내용 반응형 HTML (다운로드/인쇄 버튼) |
| `cosmetics-roadmap.pdf`       | 위 내용 PDF (8쪽) |

> AI 성향 테스트 제품과 무관. PDF 재생성·상세는 `HANDOFF.md` §13.

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
