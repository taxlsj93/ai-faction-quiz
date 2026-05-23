# 🤝 세션 핸드오프 — AI 성향 테스트 / Which AI Type?

> **새 세션 사용법**: 이 파일이 워크스페이스 루트에 있어야 다음 세션이 자동으로 인덱싱.
> 또는 새 세션 첫 메시지로 "HANDOFF.md 읽고 거기 적힌 컨텍스트로 이어서 작업해줘" 라고 말하면 됨.

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
| `/r/claude`, `/r/gpt`, `/r/gemini`, `/r/grok` | 하우스별 결과 랜딩 (개별 OG 카드) |
| `/privacy`, `/privacy-en` | 개인정보처리방침 |
| `/disclosure` | 어필리에이트 + AdSense 고지 (이중 언어) |
| `/sitemap.xml`, `/robots.txt` | SEO |
| `/og-image.svg` | 메인 OG 카드 |

### Vercel ↔ GitHub 자동배포
✅ **작동 확인** (push → live ~60–90초)

### 미커밋 변경사항 (working tree)
- `M CLAUDE.md` — "브랜드 용어 정책" 섹션 추가됨, **미커밋** → origin에 반영 안 됨
- `?? .claude/settings.local.json` (개인 설정, 커밋 X)
- `?? audit-report.html` — 이번 세션 생성, 미커밋 (내부 참고용, 배포 불필요)
- `?? brand-guide.html` — 이번 세션 생성, 미커밋 (내부 참고용, 배포 불필요)
- `?? HANDOFF.md` — 이번 세션 갱신, 미커밋

→ **다음 세션 시작 시 CLAUDE.md + HANDOFF.md 커밋 권장 (브랜드 정책 origin 반영)**

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
| `ai_analysis_button_clicked` | "AI에게 분석 받기" 버튼 클릭 | `{faction}` |
| `ai_analysis_shown` | LLM 분석 결과 표시 성공 | `{faction}` |
| `ai_analysis_failed` | LLM 분석 호출 실패 | `{faction, reason}` |

전송 헬퍼: `window.trackEvent(name, params)` — GA4 + Plausible(활성화 시) 동시 전송.

확인 URL (모바일 가능): https://analytics.google.com/ → Realtime → Event count by Event name

---

## 5. LLM 분석 기능 (Haiku 4.5, opt-in)

- 결과 페이지에서 "AI에게 더 자세한 개인 분석 받기" 버튼 — **opt-in 토글** 방식
- 정적 콘텐츠("왜 당신이 X 타입인가" + 일상 시그널 + 보조 타입 비율)는 즉시 표시
- 버튼 클릭 시에만 LLM 호출 → 비용 최적화 (예상 5–20% click-through)
- 관련 커밋: `565de53 refactor(ai): switch LLM analysis from auto-call to opt-in toggle`

---

## 6. 파일 구조 (현재)

```
/                          # repo root (Vercel 빌드 경로)
├── index.html             # KO 메인 (8문항, 2115 lines)
├── en.html                # EN 메인 (1207 lines)
├── r/                     # 하우스별 OG 랜딩
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
| 13 | **Post-Chat AI UI/UX 신규 프로젝트** — 버티컬/도메인 선택 후 generative UI MVP 범위 확정 (상세: §13) | 사용자 결정 → coordinator | 🆕 논의됨 (세션 4), 도메인 미정 |

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

## 13. 신규 프로젝트 아이디어 — "Post-Chat AI UI/UX" (세션 4, 2026-05-23)

> 코드 변경 없는 **전략·아이디어 논의 세션**. 미래 세션이 이어받을 수 있게 기록.

### 발단 (사용자 관점)
- 현재 AI 인터페이스(Claude 등)는 **MS-DOS 수준의 텍스트 대화형**.
- 사람은 글보다 시각적 인지가 빠름 → MS-DOS→Windows급 전환 = **직관적 UI/UX**가 필요.
- **별도 신규 프로젝트**로 탐색 의향 (현 AI 성향 테스트와 독립).

### 검토한 패러다임 (post-chat UI)
| # | 패러다임 | 핵심 | 사례 |
|---|---------|------|------|
| 1 | Generative UI | 응답을 글 대신 실시간 UI 컴포넌트로 렌더 | Vercel AI SDK, OpenAI Canvas, Claude Artifacts |
| 2 | Direct Manipulation + AI | 클릭·드래그로 의도 전달 (프롬프트 X) | Figma AI, Cursor, v0.dev |
| 3 | Spatial / AI-as-OS | 챗창 없는 OS형 (실패 사례 多) | Rabbit R1, Humane, Vision Pro |
| 4 | Embedded Contextual AI | 앱마다 위젯으로 내장 — 가장 성공적 | Notion AI, Cursor, Linear |
| 5 | Multimodal-first | 음성·카메라·스케치·제스처 1차 입력 | GPT-4o voice, Gemini Live |

### 수익화 경로 (1인 개발자 기준)
| 경로 | 모델 | 현실 매출 | 평가 |
|------|------|----------|------|
| **A. 버티컬 SaaS** | 한 도메인 특화 generative UI, $19~49/mo | 100~500명 → 월 $2k~25k | 신규 독립 프로젝트라면 **유일하게 의미있는 경로** |
| **B. 기존 미디어 + generative UI 레이어** | 어필리에이트 (현 모델 유지) | 트래픽 자산 재활용 | **ROI 최고, 가장 안전** |
| C. 위탁 개발/컨설팅 | "챗봇→GUI 전환" 건당 500~5,000만원 | 현금흐름 즉시 | 시간 팔기, 확장 불가 |
| D. 템플릿/컴포넌트 판매 | Gumroad 일회성 $29~99 | 월 $500~3,000 | 대박 아님 |

### 결론 / 다음 결정 포인트
- generative UI 자체는 오픈소스화되어 **기술만으로는 차별화 불가** → "누구의 어떤 페인을 푸는가"가 핵심.
- 완전 신규 독립 프로젝트로 간다면 **A(버티컬 SaaS)** 가 유일하게 의미있음 (단, 트래픽 0에서 시작).
- 가장 빠르고 안전한 길 = **B(현 AI 성향 테스트 사이트에 generative UI 레이어 얹기)** — 기존 트래픽 파이프라인 활용.
- ⏭ **사용자 결정 대기**: 어떤 버티컬/도메인에 전문성·관심이 있는지 → 정해지면 MVP 범위 구체화 가능. (실현 가능 출발점으로 "Generative UI + Tool-as-UI 조합, Vercel AI SDK + Next.js" 제안됨.)

---

**이 핸드오프는 2026-05-23 (세션 4) 기준입니다. 세션 4는 코드 변경 없는 전략 논의이며, 직전 코드 상태는 커밋 `25a32de`(세션 3) 그대로입니다.**
**다음 세션에서 작업 후 이 파일도 함께 갱신해 주세요.**
