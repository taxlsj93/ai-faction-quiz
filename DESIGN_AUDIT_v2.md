# DESIGN_AUDIT_v2.md — ai-faction-quiz 리뉴얼 후 디자인 변화 명세

> 작성일: 2026-05-28
> 대상: 세션 6 v4.3 리뉴얼 후 라이브 상태
> 비교: v1 (DESIGN_AUDIT.md, 세션 5 designer 진단) → v2 (이 문서)

---

## 1. 디자인 시스템 변화 요약

| 항목 | v1 (다크) | v2 (크림, claude.ai 톤) |
|------|----------|----------------------|
| 배경 | `#0A0A0F` | `#F5EFE6` (cream) |
| 카드 | `#13131A` | `#FFFFFF` (white) |
| 본문 텍스트 | `#F0F0F8` | `#1F1F1F` (ink, 12.6:1 AAA) |
| 보조 텍스트 | `#8888AA` (4.6:1, 다크 위) | `#5C5C5C` (6.5:1, 크림 위 AA) |
| 액센트 | 보라/파랑 그라디언트 #6C3FA8→#3B5FD4 | `#6F3D9E` 솔리드 (claude.ai plum) |
| 헤드라인 폰트 | sans-serif 시스템 | Fraunces serif (영어), 한글 시스템 폴백 |
| 본문 폰트 | sans-serif 시스템 | Inter (영어), 한글 시스템 폴백 |
| 카드 라운드 | 14-16px 혼재 | 16px 표준 + pill 999px |
| 카드 섀도우 | 없음 (다크는 border만) | `0 1px 3px + 0 4px 16px` soft |

---

## 2. v1 designer 진단 8개 권고 — v2에서 처리 현황

| # | v1 권고 | v2 처리 | 후속 |
|---|---------|---------|------|
| 1 | 옵션 선택 즉시 피드백 (selectPop 애니메이션 + ✓) | ✅ 세션 5 C7에 포함 | — |
| 2 | 보조 타입 헤더로 승격 | ✅ 세션 5 C3 + 세션 6 C2 슈퍼파워 카드로 강화 | — |
| 3 | 로딩 700→500ms + 타입 컬러 ring | ✅ 세션 5 F6 + B3에 적용 (500ms + var(--accent-plum)) | — |
| 4 | 결과 화면 뉴스레터 폼 | ✅ 세션 5 C6 + 세션 6 B6에 크림 톤 적용 | U2 form ID |
| 5 | /r/{faction} 재공유 CTA + 모바일 패딩 | ✅ 세션 5 C4 + 세션 6 B5 크림 톤 + D4 단일 소스 | — |
| 6 | 공유 섹션 헤더 직후로 부상 | ✅ 세션 5 C3에 DOM 이동 완료 | — |
| 7 | 챗 진입 버튼 노출 강화 | ✅ 세션 5 F6 alpha 0.15→0.25 + 세션 6 B6 솔리드 보라 | — |
| 8 | 인트로 "현재 쓰는 AI 선택" 가치 전달 | ⏸️ 미반영 (정보 밀도·플로우 영향 — Phase 3 #8) | — |

---

## 3. v4.3에서 새로 도입된 환상 부여 디자인 (사용자 §3 요청)

### 3.1 슈퍼파워 3 카드 (C2)
- 위치: result 화면 헤더·공유 직후
- 구조: faction 컬러 border-left 3px + icon + title + desc
- 4 타입 × 3 슈퍼파워 = 12 narrative
- 효과: "이 결과 정확하다 → 내 강점 인정" 입증

### 3.2 할수있는것 5 카드 (C3)
- 위치: 슈퍼파워 직후
- 구조: cream-soft 배경 카드 + dashed divider list 5개
- 4 타입 × 5 활용 예시 = 20 utility
- 효과: "이 AI 쓰면 이런 거 가능" 환상

### 3.3 지금 당장 1가지 (C4)
- 위치: 할수있는것 직후
- 구조: faction 컬러 border 1.5px + soft shadow + title + 1줄 desc
- 4 타입 × 1 첫 액션
- 효과: 1분 내 실행 욕구 자극

---

## 4. 새 결과 화면 흐름 (v4.3)

```
타입 헤더 (serif faction-name + 보조타입 배지 + percentile + friend-compare)
↓
공유 섹션 (X·카카오·인스타·링크복사 4 버튼, 감정 고조 순간)
↓
슈퍼파워 3 (faction 컬러, 강점 narrative)
↓
할수있는것 5 (utility list)
↓
지금당장 1가지 (faction 컬러 CTA card)
↓
AI 분석 (cream-soft + 보라 border-left, opt-in chat)
↓
traits 4 bar + stats 4 card + matchup + score-dist
↓
allies + cross-allies
↓
뉴스레터 (placeholder-gated)
↓
CTA 1차 (faction 컬러 솔리드) + 2차 (cream outline)
```

이 순서는 designer v1 #6 권고("공유 상단 부상") 우선 + 사용자 §3 환상 부여 후속 배치.

---

## 5. 시각 일관성 검증

| 항목 | 라이브 확인 (2026-05-28) |
|------|-------------------------|
| / 메인 cream 배경 | ✅ WebFetch 확인 |
| /og-image.png 새 톤 | ✅ 200, image/png, 73.6KB |
| /og/{4}.png faction 컬러 | ✅ 80-82KB each |
| /en cream 자동 적용 | ✅ index.html 공유 → cream 자동 |
| /r/{4} cream + faction border | ✅ B5에서 4 파일 sed |
| 챗 입력·send 보라 솔리드 | ✅ B6 적용 |
| 뉴스레터 form 크림 input | ✅ B6 적용 (placeholder 가드 중) |

---

## 6. 알려진 제약 (Phase 3 후보)

1. **한글 serif 헤딩 부재** — Fraunces는 한글 글리프 없어 시스템 sans-serif(Malgun Gothic 등)로 폴백. 영어 헤딩만 진짜 serif. 한글 serif 원할 시 Noto Serif KR(~150KB) 추가 검토.
2. **인트로 "현재 쓰는 AI 선택" 강조 부재** (designer #8) — 정보 밀도 영향. 별도 세션 검토.
3. **인스타 캔버스 한글 폰트** — 시스템 폰트 폴백 체인 사용 중. 더 안정적인 자형 위해 Noto Sans KR 웹폰트 캔버스 직접 로드도 검토 가능.

---

## 7. 측정 가능한 KPI (라이브 후 GA4)

22 신규 이벤트 추가 후 추적 가능:
- `quiz_start` → `quiz_complete` 완료율
- `quiz_complete` → 공유율 (`shareTwitter/shareKakao/shareInsta/copyLink`)
- `quiz_complete` → `super_powers_shown` 도달율 (=결과 도달율)
- `super_powers_shown` → `tool_picks_shown` (스크롤 깊이)
- `tool_picks_shown` → `first_action_shown` (스크롤 깊이)
- `first_action_shown` → `cta_main_click` (행동 전환)
- `landing_take_quiz_click` (/r 랜딩 → 메인 전환)
- `landing_reshare_click` (2차 확산 계수)
- `secondary_type_shown` (희소도 노출)
- `friend_compare_row_shown` (소셜 프루프 노출)
- `newsletter_widget_inert`/`shown`/`subscribed`/`failed` (구독 funnel)

목표 KPI 베이스라인은 U3(캐시 무효화) 후 첫 2주 누적치로 설정.
