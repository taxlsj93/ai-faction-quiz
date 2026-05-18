# Agents — 다중 에이전트 시스템 개요

이 디렉토리는 본 워크스페이스(AI 성향 테스트 미디어 + 화장품 사업 기획 + 세무 도메인 작업)의 **다중 에이전트 운영 정의**입니다.

> **운영 원칙**: 사용자는 한국 세무사(CTA, taxlsj93)이며 모바일 사용 비중이 높음.
> 결정 부담 최소화·합리적 기본값 자율 진행이 기본 모드.
> 위험도 게이트에서는 반드시 사용자 명시 승인.

---

## 라인업

| 에이전트 | 역할 | 모델 | 쓰기 권한 |
|---------|------|-----|----------|
| `coordinator` | 총괄 PM, 4단계(분해→분배→검증→통합) | opus | O |
| `code-implementer` | HTML/CSS/JS·정적 사이트 구현 | sonnet | O |
| `doc-writer` | 사용자 대면 카피·문서·기획서 | sonnet | O |
| `tax-domain-expert` | 세법·조특법·판례·경정청구·세무 데이터 검수 | sonnet | O |
| `deployer` | Vercel·GitHub·git push·도메인·환경변수 | sonnet | (배포 설정만) |
| `researcher` | 코드 검색·외부 조사·문서 lookup | haiku | ❌ 읽기 전용 |
| `reviewer` | 독립 lane 품질·보안·법률 검증 | sonnet | ❌ 읽기 전용 |

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
  ├──▶ researcher           (사실·코드 위치 확인, 읽기 전용)
  ├──▶ tax-domain-expert    (세법 검수, 1차 출처 확인)
  ├──▶ code-implementer     (HTML/JS 편집)
  ├──▶ doc-writer           (카피·문서·면책)
  ├──▶ deployer             (push·배포·env)
  │
  ▼ 산출물
  │  ── 3단계 검증 ──▶ reviewer (독립 lane, PASS/HOLD/FAIL)
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
coordinator → doc-writer → reviewer → coordinator → 사용자 보고
```

### 예시 2 — 세무 리포트 페이지 신설 (복합)
```
사용자: "조특법 7조 적용 가능성 정리해서 HTML 리포트 페이지로 만들고 배포"
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

---

## 위험도 게이트 (reviewer 필수 트리거)

다음 중 **하나라도** 해당하면 coordinator는 reviewer를 반드시 호출:

- 사용자 대면 텍스트 변경 (퀴즈 카피, 결과 페이지, 면책, 어필리에이트 고지)
- 외부 시스템 변경 (git push, Vercel 배포, GitHub PR/머지)
- **세법·조특법·판례 인용 포함** (tax-domain-expert 검수 + reviewer 별도 lane)
- 어필리에이트 링크·트래킹 파라미터 변경
- 보안 영향 (시크릿·인증·CORS·환경변수)

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
| 검증 수행 여부 | — |

---

## 모델 선정 요약

- **opus** (coordinator) — 다중 에이전트 조율·라우팅 판단·통합 추론
- **sonnet** (code-implementer, doc-writer, tax-domain-expert, deployer, reviewer) — 정확한 패턴/정책 적용에 가성비 최적
- **haiku** (researcher) — 검색·압축이 핵심이라 빠른 모델로 충분

특수 케이스(복잡한 다중 조항 동시 적용·전략 설계 등)는 coordinator가 `model` override로 opus 호출 가능.

---

## 참고

- 산출물 품질 평가 기준: `../AGENTS_RUBRIC.md`
- 워크스페이스 사업 컨텍스트·브랜드 용어: `../../CLAUDE.md`
- 글로벌 OMC 원칙: `~/.claude/CLAUDE.md`
