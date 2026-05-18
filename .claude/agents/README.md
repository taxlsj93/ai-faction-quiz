# Agents — 다중 에이전트 시스템 개요

이 디렉토리는 본 워크스페이스(AI 성향 테스트 미디어 + 화장품 사업 기획) 및 자매 프로젝트(tax-recovery-finder 등 세무 도메인)의 **다중 에이전트 운영 정의**입니다.

> **운영 원칙**: 사용자는 한국 세무사(CTA, taxlsj93)이며 모바일 사용 비중이 높음.
> 결정 부담 최소화·합리적 기본값 자율 진행이 기본 모드.
> 위험도 게이트(외부 시스템 변경·세법 인용·종전 신고 추정·시그널 DB 신규 매핑 ★★★)에서는 반드시 사용자 명시 승인.

---

## 라인업 (9개)

| 에이전트 | 역할 | 모델 | 쓰기 권한 |
|---------|------|-----|----------|
| `coordinator` | 총괄 PM, 4단계(분해→분배→검증→통합) | opus | O |
| `code-implementer` | HTML/CSS/JS·정적 사이트 구현 | sonnet | O |
| `doc-writer` | 사용자 대면 카피·문서·기획서 | sonnet | O |
| `tax-domain-expert` | 세법·조특법·판례·경정청구 조문 검수 | sonnet | O |
| **`filing-estimator`** | **종전 신고 추정 (★ 신뢰도) · 카드 R/A/B 트리아지** | **sonnet** | O |
| **`diagnostic-builder`** | **카드별 yes/no 진단 인터뷰 설계 (3문항 + 채점)** | **haiku** | O |
| `deployer` | Vercel·GitHub·git push·도메인·환경변수 | sonnet | (배포 설정만) |
| `researcher` | 코드 검색·외부 조사·5×5 매트릭스 발굴 | haiku | ❌ 읽기 전용 |
| `reviewer` | 독립 lane 품질·보안·법률·P2 게이트 검증 | sonnet | ❌ 읽기 전용 |

---

## 표준 흐름

```
사용자
  │
  ▼
coordinator (opus, PM)
  │  ── 1단계 분해 ──▶ 의도 / 산출물 / 위험도 / 검증기준
  │  ── 2단계 분배 ──▶ (병렬 가능시 단일 메시지 다중 Agent)
  │
  ├──▶ researcher           (사실·코드 위치 / 5×5 매트릭스 발굴)
  ├──▶ filing-estimator     (종전 신고 추정 ★ / 카드 R/A/B 트리아지)
  ├──▶ tax-domain-expert    (조문·판례·요건 정밀 검수)
  ├──▶ diagnostic-builder   (yes/no 3문항 + 채점 매핑)
  ├──▶ code-implementer     (HTML/JS 편집)
  ├──▶ doc-writer           (카피·문서·면책)
  ├──▶ deployer             (push·배포·env)
  │
  ▼ 산출물
  │  ── 3단계 검증 ──▶ reviewer (독립 lane, PASS/HOLD/FAIL)
  │                              + P2 게이트 (가짜·근거 없는 추정 차단)
  ▼
coordinator                 (4단계 통합)
  │
  ▼
사용자에게 한국어 압축 보고
```

---

## 호출 패턴 예시

### 예시 1 — 단순 카피 수정
```
사용자: "결과 페이지 Claude 타입 설명 좀 다듬어줘"
coordinator → doc-writer → reviewer → coordinator → 사용자
```

### 예시 2 — 세무 리포트 페이지 신설
```
사용자: "조특법 §7 적용 가능성 정리해서 HTML 리포트 페이지로 만들고 배포"
coordinator
  ├─ tax-domain-expert (법령·요건·계산)
  ├─ doc-writer (카피·면책)
  └─ code-implementer (HTML 페이지)
        ↓
  reviewer (코드·세법·카피 동시 점검)
        ↓
  deployer (preview)
        ↓
  사용자 검토 → (승인) → deployer (prod) → reviewer
```

### 예시 3 — 빠른 사실 확인
```
사용자: "지금 사이트에 jasper.ai 링크 어디 박혀있어?"
coordinator → researcher → 즉시 보고 (검증 생략)
```

### 예시 4 — 사업 기획서 보강
```
사용자: "화장품 로드맵에 '솔로 운영 1년 차 손익분기' 시나리오 추가"
coordinator → researcher (관련 통계) → doc-writer (본문) → reviewer
```

### 예시 5 — 긴급 롤백
```
사용자: "방금 배포한 거 이상해 — 되돌려"
coordinator → deployer (vercel rollback) → researcher (원인 위치) → 보고
```

### 예시 6 — tax-recovery-finder 카드 트리아지 + 진단 (신규 패턴)
```
사용자: "조특법 §10 R&D 세액공제 카드 트리아지하고 진단 인터뷰까지 붙여줘"
coordinator
  ├─ filing-estimator     (회계·공시 단서로 종전 신고 ★ 추정 + R/A/B 등급)
  ├─ tax-domain-expert    (조문·판례·요건 정밀 검수 — R 등급만)
  └─ diagnostic-builder   (R/A 등급 카드별 yes/no 3문항 + 채점 매핑)
        ↓
  reviewer (P2 게이트 — ★ 신뢰도·단서 출처·진단 채점 가능성)
        ↓
  doc-writer (카드 표시용 카피)
        ↓
  code-implementer (카드 마크업)
        ↓
  deployer (preview → 사용자 → prod)
```

### 예시 7 — 5×5 매트릭스 빈 칸 채우기 (신규 패턴)
```
사용자: "트리거 5종 × 청구근거 5종 매트릭스 빈 셀 발굴해줘"
coordinator
  └─ researcher (셀별 발굴, 셀당 임계 3건)
        ↓
  tax-domain-expert (셀별 조문 정합성 검증, ✅/⚠️/❌)
        ↓
  reviewer (매트릭스 정합성·빈 셀 식별)
        ↓
  보고 + 다음 발굴 우선순위 추천
```

---

## 위험도 게이트 (reviewer 필수 트리거)

다음 중 **하나라도** 해당하면 coordinator는 reviewer를 반드시 호출:

- 사용자 대면 텍스트 변경 (퀴즈 카피, 결과 페이지, 면책, 어필리에이트 고지)
- 외부 시스템 변경 (git push, Vercel 배포, GitHub PR/머지)
- **세법·조특법·판례 인용 포함** (tax-domain-expert 검수 + reviewer 별도 lane)
- **종전 신고 추정·★ 신뢰도 산출** (filing-estimator 산출 + reviewer P2 게이트)
- **카드 진단 인터뷰 (yes/no 채점 매핑)** (diagnostic-builder 산출 + reviewer 채점 가능성 점검)
- 어필리에이트 링크·트래킹 파라미터 변경
- 보안 영향 (시크릿·인증·CORS·환경변수)
- 시그널 DB 신규 매핑 등록 (★★★ 부여는 사용자 confirm 필요)

---

## 자율 결정 vs 사용자 확인

| 자율 결정 | 사용자 확인 필수 |
|----------|----------------|
| 파일명·경로 | production 배포 |
| 커밋 메시지 | 외부 결제·신규 API 키 발급 |
| 한·영 분기 처리 | 파괴적 git (force push, reset --hard, branch -D) |
| 모델 선택 | 기존 사업 방향과 다른 신규 기획 도입 |
| 병렬 vs 직렬 | 어필리에이트 신규 파트너 등록 |
| preview 배포 | 세무 자문 결과를 사이트에 공개 게시 |
| 검증 lane 호출 여부 | **시그널 DB 신규 매핑을 ★★★로 부여** |
| DB 업데이트 권고 첨부 여부 | — |

---

## 모델 선정 요약

- **opus** (coordinator) — 다중 에이전트 조율·라우팅·통합 추론
- **sonnet** (code-implementer, doc-writer, tax-domain-expert, filing-estimator, deployer, reviewer) — 정확한 패턴/정책/추정 추론에 가성비 최적
- **haiku** (researcher, diagnostic-builder) — 검색·압축·템플릿 기반 작업

특수 케이스(복잡한 다중 조항 동시 적용·전략 설계·5단계+ 진단 트리)는 coordinator가 `model` override로 sonnet/opus 호출 가능.

---

## P2 게이트 — 가짜 데이터 차단

`.claude/AGENTS_RUBRIC.md` 의 **P2 (Priority 2 품질 게이트)** 는 모든 세무 추정·진단·카드 데이터에 적용되는 강제 규칙:

- ★ 신뢰도 없는 단정 금지
- 단서(evidence) 출처 없는 추정 금지
- 가짜·창작 수치 절대 금지
- 위반 시 reviewer 즉시 FAIL

---

## 참고

- 산출물 품질 평가 기준: `../AGENTS_RUBRIC.md`
- 시그널 DB 메타 운영 스펙: `../SIGNAL_DB.md`
- 워크스페이스 사업 컨텍스트·브랜드 용어: `../../CLAUDE.md`
- 글로벌 OMC 원칙: `~/.claude/CLAUDE.md`
