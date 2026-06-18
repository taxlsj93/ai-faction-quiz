# 🤝 세션 핸드오프 — AI 성향 테스트 / Which AI Type?

> **새 세션 사용법**: 이 파일이 워크스페이스 루트에 있어야 다음 세션이 자동으로 인덱싱.
> 또는 새 세션 첫 메시지로 "HANDOFF.md 읽고 거기 적힌 컨텍스트로 이어서 작업해줘" 라고 말하면 됨.

---

## 🆕 세션 6 (2026-05-28) — v4.3 리뉴얼 (claude.ai 크림 톤 + 환상 + 공유)

ralplan v4.3 합의(Arch ITERATE → Crit ITERATE 2 라운드 → ACCEPT) → 22 커밋 5 Phase
자율 실행. 세션 5(19) + 세션 6(22) = **누적 41 커밋**.

핵심 결과:
- **다크 → claude.ai 크림 톤** 전면 시각 전환 (cream/white/ink/plum, serif 헤딩)
- **8문항 시나리오형 재작성** (AI 단어 0회, 한국 일상)
- **결과 화면 "환상" 3-stack**: 슈퍼파워 3 → 할수있는것 5 → 지금당장 1
- **OG 카드 5장 재생성** + build-og.mjs 200KB hard gate
- **인스타 캔버스 크림 톤** + 한글 자형 안정
- **share-copy.js 단일 소스** (r/4 카피 통합)
- **api/chat.js SYSTEM_PROMPT 동기화** (silent regression 차단)
- **A2 contract assertion** (Phase C 회귀 게이트, type max=24 검증)

신규 GA4 이벤트 5종 (Phase B+C+D):
super_powers_shown / tool_picks_shown / first_action_shown / (기존) secondary_type_shown / friend_compare_row_shown / landing_*

라이브 확인 (E1): / cream 배경 + 8문항 시나리오 + OG PNG 73.6KB image/png 200.

상세 22 커밋·Phase별 효과는 STATUS.md §세션 6 참조.

**남은 작업**: C5b(어필리에이트 매핑·U1 게이트) — 사용자가 실 ID 알려주면 진행.

---

## 🆕 세션 5 (2026-05-27) — 리뉴얼 라이브 완료

`IMPROVEMENT_NOTES.md` 진단 + `DESIGN_AUDIT.md`(designer) + `/ralplan v3.2` consensus 합의
(Planner → Architect→Critic 3 iteration → APPROVE)로 **12 커밋, 14 surface, 8 신규 GA4** 라이브.

**라이브 검증** (curl + WebFetch):
- `/`, `/en`, `/r/{4타입}` 200 · `/og-*.png` image/png 112-122KB
- `/en.html` 308 → `/en` · `/en` body = index.html with EN content
- `result-secondary-badge`·`share-section`·`newsletter-card` DOM 존재 확인

**12 커밋 요약** (Phase 1 → Phase 2):
| Phase | 커밋 | 효과 |
|-------|------|------|
| P1 | C0  `5f148b7` chore | 워크트리 정리 |
| P1 | C1a `43dfe59` feat(og) | SVG→PNG 14 surface (FB·X·카카오 미리보기 부활) |
| P1 | C1b `50f0c1b` chore(build) | build-og.mjs + puppeteer-core devDep |
| P1 | C2  `9fcaf18` fix(a11y) | viewport 핀치줌 (WCAG 1.4.4) |
| P1 | C5a `35fc85b` refactor(affiliate) | window.AFFILIATE 단일 소스 |
| P1 | C9p1 `c9d1c2b` docs | Phase 1 인계 |
| P2 | C8  `edc933e`+`1bc14b8` feat(en) | /en atomic 통일 (rewrite + per-LANG canonical + en.html DELETE) |
| P2 | C7  `b8218d9` feat(quiz) | 옵션 셔플 (백엔드 무손상) + 선택 피드백 |
| P2 | C3  `eff1cca` feat(result) | 보조타입 배지 + 백분위 + 친구비교 + 공유 상단 부상 |
| P2 | C4  `4202508` feat(share) | /r/{4} 재공유 CTA + 모바일 패딩 |
| P2 | C6  `32a0b54` feat(newsletter) | ConvertKit placeholder-gated |

**남은 1 커밋**: C5b (어필리에이트 타입↔툴 재매핑 + CLAUDE.md/disclosure/privacy-en 동기화) — **U1 차단**.

**사용자 작업 큐 (모바일 가능)**:
- 🔴 **U3 (즉시)**: FB·X·카카오 디버거에서 5 URL 강제 캐시 무효화 → 새 PNG 즉시 노출
- 🟠 **U1**: 어필리에이트 실 ID 4종 → C5b 진행 가능
- 🟡 **U2**: ConvertKit form ID → C6 활성 (현재는 inert 가드)
- 🟡 **U4**: GA4 전환 표시 (8 신규 이벤트) + Search Console sitemap
- ⚪ **U5**: GitHub Secrets `ANTHROPIC_API_KEY` → .github/ 별도

상세는 STATUS.md §세션 5 + DESIGN_AUDIT.md (디자인 권고 8개) 참조.

---

## 0. 사용자 운영 원칙 (필독 — 항상 적용)

- **사용자는 거의 항상 모바일** → 결정 부담 주지 말고 합리적 기본값으로 진행, 결과만 보고
- **Auto 모드** 기본 활성 — 자율 실행 우선, 파괴적 작업·계정 자격 필요 작업만 사용자 확인
- **한국어 보고**, 표·체크리스트로 압축
- **사용자 작업 vs 에이전트 작업 분리해서 보고** (모바일에서 직접 해야 하는 것만 따로 묶기)
- 작업 후 STATUS.md 갱신 + 의미 있는 단위로 커밋 분할 + push까지

---

## 1. 프로젝트 정체성

| 항목 | 값 |
|------|-----|
| 사이트명 (KO) | **AI 성향 테스트** |
| 사이트명 (EN) | **AI Personality Quiz / Which AI Type?** |
| 부제 (KO) | 당신의 AI 타입은? |
| 부제 (EN) | Which AI Type Are You? |
| 라이브 URL | https://ai-faction-quiz.vercel.app/ |
| 라이브 URL (EN) | https://ai-faction-quiz.vercel.app/en |
| GitHub | https://github.com/taxlsj93/ai-faction-quiz |
| 메인 브랜치 | `master` |
| 사용자 이메일 | `tax.lsj93@gmail.com` |
| 사용자 GitHub | `taxlsj93` |
| 도메인 (Vercel) | 무료 .vercel.app — 커스텀 도메인 없음 |

### 🚨 용어 정책 (모든 작업 시 반드시 준수)
- **사용자 노출 텍스트**: 반드시 **타입 / Type** 사용 ("진영 / Faction" ❌, "하우스 / House" ❌ 구버전)
- **코드 내부 변수·CSS·URL**: `faction` 유지 (변경 시 버그 + SEO 손실)
  - 예: `resultFaction` JS 변수, `.faction-claude` CSS 클래스, `ai-faction-quiz.vercel.app` 도메인
- SEO meta keywords 태그에는 "진영/faction/house" 병기 허용 (검색 유입)
- 자세한 표는 `CLAUDE.md`의 "브랜드 용어 정책" 섹션 또는 `brand-guide.html` 참고

---

## 2. 현재 상태 스냅샷 (2026-05-09 기준)

### 라이브 라우트 (모두 200 OK 검증됨)
| 경로 | 콘텐츠 |
|------|--------|
| `/` | KO 메인 퀴즈 (index.html) — 8문항 |
| `/en` | EN 메인 퀴즈 (en.html) |
| `/r/claude`, `/r/gpt`, `/r/gemini`, `/r/grok` | 타입별 결과 랜딩 (개별 OG 카드) |
| `/privacy`, `/privacy-en` | 개인정보처리방침 |
| `/disclosure` | 어필리에이트 + AdSense 고지 (이중 언어) |
| `/sitemap.xml`, `/robots.txt` | SEO |
| `/og-image.svg` | 메인 OG 카드 |

### Vercel ↔ GitHub 자동배포
✅ **작동 확인** (push → live ~60–90초)

### 커밋 상태 (2026-05-09 갱신)
- ✅ `CLAUDE.md` 브랜드 용어 정책 — 커밋됨 (`3043a8d`)
- ✅ `brand-guide.html` — 커밋됨 (`3043a8d`)
- ✅ PR #5 (하우스→타입 리브랜드 + 멀티턴 챗) — master 머지 완료 (`25a32de`), 프로덕션 라이브
- `?? .claude/settings.local.json` (개인 설정, 커밋 X)

---

## 3. 광고 시스템 현황

| 시스템 | 상태 | 비고 |
|--------|------|------|
| Google AdSense (`ca-pub-3036702261797984`) | ✅ **재심사 요청 완료 (2026-05-09)** | 결과 대기 중 (예상 3일~2주). 승인 시 popunder 재활성화 검토 |
| profitablecpmratenetwork (popunder) | 🔒 **DISABLED 2026-05-06** | UX 가드 코드 보존, AdSense 승인 후 재활성화 검토 |
| 인라인 어필리에이트 카드 | ✅ 가동 중 | `?via=aifaction` 트래킹 모든 링크 적용 (Writesonic, Perplexity, Copy.ai) |

### UX 가드 코드 (현재 주석 처리, 재활성화 시 사용)
- (a) 지연 로드: `quiz_complete_signal` OR 30s 타임아웃
- (b) CSS `!important` — 60px 하단 띠로 강제
- (c) `window.open` 후킹 (사용자 클릭 1.5초 외 차단), `beforeunload`/`unload` 차단
- (d) 자동 닫기 X 버튼 오버레이 (1.5초 주기 스캔)

### 어필리에이트 매핑 (CTA 2차)
| 타입 | URL | 트래킹 |
|------|-----|--------|
| Claude | `writesonic.com/?via=aifaction` | ✅ |
| GPT | `writesonic.com/?via=aifaction` | ✅ |
| Gemini | `writesonic.com/?via=aifaction` | ✅ |
| Grok | `perplexity.ai/?via=aifaction` | ✅ |

---

## 4. GA4 이벤트 카탈로그 (`G-HPT1Y41HD8`)

| 이벤트 | 트리거 | 파라미터 |
|--------|--------|----------|
| `quiz_start` | 시작 버튼 클릭 | `{lang}` |
| `quiz_complete` | 결과 화면 진입 직전 | `{faction, lang}` |
| `cta_main_click` | 1차 CTA(AI 툴 직접) 클릭 | `{faction, url}` |
| `cta_secondary_click` | 2차 CTA(어필리에이트) 클릭 | `{faction, url}` |
| `affiliate_card_click` | 결과 페이지 인라인 카드 클릭 | `{url, label, faction}` |
| `ad_network_loaded` | 광고망 지연 로드 발화 | `{trigger}` (현재 미발화 — 광고망 비활성) |
| `chat_opened` | "내 AI에게 직접 질문하기" 버튼 클릭 → 챗 패널 오픈 | `{faction}` |
| `chat_message_sent` | 사용자가 챗 메시지 전송 | `{faction, turn}` |
| `chat_response_shown` | AI 캐릭터 응답 표시 성공 | `{faction}` |
| `chat_failed` | 챗 호출 실패 | `{faction, reason}` |

> ⚠️ 구버전 `ai_analysis_button_clicked` / `ai_analysis_shown` / `ai_analysis_failed` 이벤트는 **PR #5에서 멀티턴 챗으로 교체되며 제거됨**. 위 `chat_*` 이벤트로 대체됨.

전송 헬퍼: `window.trackEvent(name, params)` — GA4 + Plausible(활성화 시) 동시 전송.

확인 URL (모바일 가능): https://analytics.google.com/ → Realtime → Event count by Event name

---

## 5. LLM 기능 — 멀티턴 챗 (Haiku 4.5, opt-in) ★ PR #5에서 변경됨

**흐름**: 결과 페이지 → 정적 분석 즉시 표시 → "💬 내 AI에게 직접 질문하기" 버튼 → 멀티턴 챗 패널 오픈

- **정적 분석** (LLM 호출 없음, 즉시): "왜 당신이 X 타입인가" + 일상 시그널 + 보조 타입 비율
- **멀티턴 챗** (`/api/chat.js`, Vercel serverless):
  - 사용자가 받은 타입의 의인화 캐릭터(Claude 사색 / GPT 실행 / Gemini 전략 / Grok 반골)와 반말 대화
  - 시스템 프롬프트(타입 페르소나 + 8문항 메타) **ephemeral 캐싱** → 입력 비용 ~90% 절감
  - 제한: 세션당 사용자 메시지 5턴(`CHAT_LIMIT=5`), 한 메시지 1000자, 출력 600토큰, role 교차 검증
  - 실패 시 user 메시지 history 롤백 + 에러 버블 표시
  - 타입별 starter 칩 3종 제공
- **구버전 1회성 분석(`/api/analyze.js`)은 제거됨** — 8문항 고정 입력이라 사람마다 결과가 거의 동일해 LLM 가치 없었음
- 관련 커밋: `f0fe4b3 feat(chat): replace one-shot analyze with multi-turn house chat` (PR #5)
- ⚙️ Vercel 환경변수 `ANTHROPIC_API_KEY` 필요 (설정됨)

---

## 6. 파일 구조 (현재)

```
/                          # repo root (Vercel 빌드 경로)
├── index.html             # KO 메인 (8문항) — 정적 분석 + 멀티턴 챗 UI
├── en.html                # EN 메인 (챗 기능 없음 — KO 전용)
├── api/
│   └── chat.js            # 멀티턴 챗 serverless 엔드포인트 (Haiku 4.5)
├── launch-copy.md         # KO/EN 배포 채널 카피 초안 (PR #5)
├── r/                     # 타입별 OG 랜딩
│   ├── claude.html
│   ├── gpt.html
│   ├── gemini.html
│   └── grok.html
├── privacy.html, privacy-en.html
├── disclosure.html        # 어필리에이트 + AdSense 고지
├── og-image.svg
├── robots.txt, sitemap.xml
├── vercel.json            # cleanUrls + trailingSlash
├── README.md, STATUS.md, CLAUDE.md, HANDOFF.md
├── brand-guide.html       # 브랜드 가이드 별도 페이지
├── audit-report.html      # 실험
├── _archive/experiments/  # Phase 0 실험 12개 보존
├── phoney-war/            # 보류 (Phase 3 부활 예정)
└── .claude/agents/        # 5개 에이전트 정의
    ├── coordinator.md     # opus, 총괄
    ├── code-implementer.md
    ├── doc-writer.md
    ├── researcher.md      # haiku
    └── reviewer.md
```

---

## 7. 최근 커밋 히스토리 (최신 → 과거)

```
25a32de Merge PR #5: 하우스 → 타입 리브랜딩 + 멀티턴 채팅
3043a8d docs: 브랜드 용어 정책 추가 + 세션2 핸드오프 갱신
dfb5684 fix: 어필리에이트 트래킹 파라미터 추가 + AdSense 재심사 준비
9eef6c2 Merge: opt-in AI analysis toggle
565de53 refactor(ai): switch LLM analysis from auto-call to opt-in toggle
9db65e0 Merge pull request #4
982b68d feat(ai): personalized LLM analysis on result page (Haiku 4.5)
23733e3 Merge pull request #3
0bb7e6b feat(share): per-house OG cards and result landing pages
461b9eb Merge pull request #2
5c6b02c fix(ads): prep site for AdSense review  ← popunder 광고망 DISABLE
8757656 Merge pull request #1
960d2c2 feat(brand): rebrand to AI 성향 테스트 / Which AI House?
aefad38 docs(status): record ad UX guards + new tracking events
350d508 feat(ads): restore network ad with UX guards
857db80 fix(ads): remove profitablecpmratenetwork popunder script
081bd11 docs(status): refresh after Vercel verify, analytics, legal, SEO landed
dd4371d fix(deploy): rename to standard index.html, simplify vercel.json
ff155e9 fix(deploy): add root vercel.json with cleanUrls and rewrites
d3dfd5a chore: archive Phase 0 experiments
02ea619 feat(analytics): scaffold GA4/Plausible event tracking
89720fb feat(seo): add robots.txt and sitemap.xml
17d5241 feat(legal): add privacy policy and affiliate disclosure pages
750195f docs: add README, STATUS, agents structure
b949348 Initial commit — AI Faction Quiz v1.0
```

---

## 8. 다음 액션 후보 (사용자 결정 대기 — 우선순위 순)

| # | 액션 | 누가 | 상태 |
|---|------|------|------|
| 1 | **AdSense 심사 결과 모니터링** — adsense.google.com 또는 모바일 앱 | 사용자 (모바일 ✅) | ✅ 요청 완료 (2026-05-09), 결과 대기 |
| 2 | **CLAUDE.md + HANDOFF.md + brand-guide.html 타입 리브랜딩** — 완료 | coordinator | ✅ 완료 (2026-05-09) |
| 3 | **`audit-report.html` 처리** — 커밋·삭제·_archive 이동 중 결정 | coordinator | 대기 |
| 4 | **TikTok / Instagram Reels 영상** — 컨셉·스크립트·해시태그 확정 후 제작·업로드 | 사용자 + coordinator | 🆕 논의 시작, 미완 |
| 5 | **에펨코리아 게시** — brand-guide.html 한국어 카피 사용, 결과 스크린샷 첨부 권장 | 사용자 | 대기 |
| 6 | **X(트위터) 게시** — brand-guide.html X 카피 사용 | 사용자 | 대기 |
| 7 | **Reddit** — 카르마 부족으로 당장 불가. r/FreeKarma4U 등으로 카르마 50+ 쌓은 후 r/SideProject → r/ChatGPT 순으로 도전 | 사용자 | 🚫 보류 (카르마 부족) |
| 8 | **GA4 이벤트 검증** — realtime view에서 신규 `ai_analysis_*` 이벤트 도착 확인 | 사용자 (모바일 ✅) | 대기 |
| 9 | **Search Console 사이트맵 제출** — search.google.com/search-console | 사용자 (모바일 ✅) | 대기 |
| 10 | **어필리에이트 실 트래킹 ID 확인** — `?via=aifaction` 가 실제 가입한 ID와 일치하는지 | 사용자 | 대기 |
| 11 | **Plausible Analytics 활성화** (선택) — 코드 주석 해제만 하면 됨 | code-implementer | 옵션 |
| 12 | **AdSense 승인 후 popunder 재활성화 검토** | 사용자 + coordinator | AdSense 승인 후 |

---

## 9. 알려진 이슈 / 점검 필요

1. **AdSense 재심사 요청 완료 (2026-05-09)** — 결과 대기 중 (3일~2주). 승인 전까지 광고 수익 없음
2. **CLAUDE.md + HANDOFF.md 미커밋** — 브랜드 정책·세션2 갱신이 origin에 미반영. 다음 세션 시작 시 커밋 필요
3. **`deploy/` 디렉터리** — 현재 미사용, 추후 정리 가능
4. **ConvertKit/뉴스레터** — 미설치 (Phase 2)
5. **Phoney War 게임** — 보류 (Phase 3 부활 예정)

---

## 10. 자주 쓰는 명령

```bash
# 라이브 라우트 헬스체크
for p in / /en /privacy /disclosure /sitemap.xml /robots.txt /r/claude /r/gpt /r/gemini /r/grok; do
  echo "$p: $(curl -sS -o /dev/null -w '%{http_code}' https://ai-faction-quiz.vercel.app$p)"
done

# Vercel 자동배포 트리거 + 검증
git -C "C:/Users/USER/Documents/Claude/apple vs android" push origin master
sleep 90 && curl -sS -I https://ai-faction-quiz.vercel.app/ | grep -i "Last-Modified\|Etag"

# GitHub API (description/topics 변경 시)
TOKEN=$(printf "protocol=https\nhost=github.com\n\n" | git credential fill 2>/dev/null | grep ^password= | cut -d= -f2-)
# 그 후 curl ... -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/taxlsj93/ai-faction-quiz
```

---

## 11. 에이전트 라우팅 (이 프로젝트)

| 작업 유형 | 라우팅 | 모델 |
|----------|--------|------|
| 사용자 명령 1차 진입 | `coordinator` | opus |
| HTML/JS/CSS 편집 | `code-implementer` | sonnet |
| README/STATUS/카피 | `doc-writer` | sonnet |
| grep/lookup/외부 데이터 | `researcher` | haiku |
| 완료 직전 검증 | `reviewer` | sonnet |

`/oh-my-claudecode:` 스킬도 활용 가능 (autopilot, ralph, ultrawork, team 등).

---

## 12. 작업 시작 체크리스트 (새 세션이 따라야 할 순서)

1. ✅ 이 파일(HANDOFF.md) 통독
2. ✅ `CLAUDE.md`의 "브랜드 용어 정책" 섹션 확인 (타입/Type 일관성)
3. ✅ `git status`로 미커밋 상태 확인 (위 §2 항목)
4. ✅ `git log --oneline master -5`로 최근 커밋 확인
5. ✅ 라이브 라우트 헬스체크 (위 §10)
6. ✅ STATUS.md 통독해 사업 단계 인지
7. ▶ 사용자 명령 받으면 → coordinator 모델로 분해 → 적합 에이전트에 분배

---

## 13. 별도 산출물 — 기초화장품 사업 로드맵 (⚠️ AI 퀴즈 제품과 무관 / 개인 요청)

> **세션 4 (2026-05-12 ~ 2026-05-23)** 작업. AI 성향 테스트 제품과 **무관한 개인 요청**으로,
> 사용자 아내의 **기초화장품(스킨케어) 브랜드 창업** 로드맵 문서를 작성한 것. 제품 로드맵·마케팅과 섞지 말 것.

### 무엇을 했나
- 기초 스킨케어 브랜드 창업 로드맵 작성: 단계별(Phase 0~3, 12개월) · 자본 계획 · 인허가(화장품책임판매업 등록) · 정부지원 한도 · 1인 운영 가능성 · 세럼 1종 비용 예시
- 동일 내용을 **3개 포맷**으로 산출: 마크다운 / 반응형 HTML / PDF(8쪽)
- HTML에 다운로드 버튼(PDF·HTML·MD) + 인쇄용 print CSS 추가
- PR #6, #7로 master 머지 완료 → Vercel 라이브 반영

### 산출 파일 (master 반영됨)
| 파일 | 설명 |
|------|------|
| `cosmetics-business-plan.md` | 텍스트 원본 (GitHub에서 렌더링해 보기 가장 편함) |
| `cosmetics-roadmap.html` | 반응형 HTML (다운로드/인쇄 버튼 포함) |
| `cosmetics-roadmap.pdf` | 생성된 PDF, 8쪽 |

### 라이브 URL (Vercel)
- https://ai-faction-quiz.vercel.app/cosmetics-roadmap.html
- https://ai-faction-quiz.vercel.app/cosmetics-roadmap.pdf
- https://ai-faction-quiz.vercel.app/cosmetics-business-plan.md

### PDF 재생성 방법 (내용 수정 시)
Playwright(Chromium)로 HTML → PDF 렌더. 글로벌 설치 사용:
```bash
cat > /tmp/gen_pdf.js <<'JS'
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage();
  await p.goto('file:///home/user/ai-faction-quiz/cosmetics-roadmap.html', { waitUntil: 'networkidle' });
  await p.emulateMedia({ media: 'print' });
  await p.pdf({ path: '/home/user/ai-faction-quiz/cosmetics-roadmap.pdf', format: 'A4', printBackground: true,
    margin: { top: '12mm', bottom: '14mm', left: '10mm', right: '10mm' } });
  await b.close();
})();
JS
NODE_PATH=/opt/node22/lib/node_modules node /tmp/gen_pdf.js
```

### 미해결/주의
- 금액·정부지원 제도는 2025~2026 추정치 → 신청 전 K-Startup·기업마당·식약처 최신 공고 확인 필요(문서에 면책 명시).
- 사용자 아내 프로필: **디자이너 + 화장품 업계 인맥** → 디자인 인하우스로 린 스타트 1,000만원대 가능(문서 §8·§2-D 반영).
- 다음 단계 후보(미진행): ① ODM 견적 비교 체크리스트 ② 정부지원 신청용 사업계획서 초안 템플릿.
- ⚠️ master 직접 push는 **403(브랜치 보호)** — 변경은 브랜치 push 후 **PR 생성→머지**로만 가능.

---

**이 핸드오프는 세션 4(2026-05-23)에 갱신됨. AI 퀴즈 제품 상태는 §1~§12(세션 3, 커밋 `25a32de` 기준)가 유효하고, §13은 별도 개인 산출물 기록입니다.**
**다음 세션에서 작업 후 이 파일도 함께 갱신해 주세요.**
