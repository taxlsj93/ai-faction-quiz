# Signal DB — 메타 운영 스펙

> **Signal DB(신호 데이터베이스)** 는 회계·공시·계약·업종 단서와 추정 신고 내용을 연결하는 누적 자산입니다.
> 본 파일은 **운영 규칙(meta-spec)** 만 정의합니다. 실제 DB 컨텐츠는 자매 프로젝트(tax-recovery-finder 등) 디렉토리에 위치합니다.

---

## 정의

- **Signal (신호)** — 회계·공시·계약·업종 데이터의 특정 패턴
- **Mapping (매핑)** — 신호 ↔ 추정 신고 내용 (또는 추정 청구 가능성)
- **Confidence (★ 신뢰도)** — ★ / ★★ / ★★★ 3단계 (filing-estimator 기준 일치)

**예시**
- 신호: "손익계산서 R&D비 0원 + 기업부설연구소 인증 없음"
- 매핑: "R&D 세액공제 미적용 ★★ — 일반적 패턴"

---

## 권장 스키마 (YAML)

```yaml
- id: signal-001
  pattern: "손익 R&D비 0원 + 기업부설연구소 미인증"
  domain: 조특법 §10 (R&D 세액공제)
  estimated_filing: 미적용
  confidence_default: ★★
  evidence_sources:
    - 재무제표 (감사보고서)
    - 한국산업기술진흥협회 인증 목록
  counter_signals:
    - 별도 세무조정 명세서에 R&D 공제 표기 (매핑 무효)
  validation_record:
    - { date: 2026-MM-DD, case_id: CARD-XXX, outcome: 채택, reason: ... }
    - { date: 2026-MM-DD, case_id: CARD-YYY, outcome: 탈락, reason: ... }
  last_updated: YYYY-MM-DD
```

---

## 운영 사이클

### 참조 (Read)
| 에이전트 | 참조 시점 |
|---------|----------|
| `filing-estimator` | **1차 참조** — 매핑 있으면 ★ 신뢰도 디폴트 적용 |
| `tax-domain-expert` | 청구 가능성 검토 시 신호 강도 참조 |
| `diagnostic-builder` | 진단 문항이 어떤 신호를 확인하려는지 명시 |
| `researcher` | 5×5 매트릭스 발굴 시 기존 매핑된 셀 vs 빈 셀 식별 |

### 업데이트 (Write)
- **새 패턴 발견 시**: 보고에 "DB 업데이트 권고" 섹션 추가 (id 후보 + 패턴 + 매핑 초안 + 신뢰도 디폴트)
- **사용자 결정 기록**: 카드 채택/탈락 시 `validation_record`에 누적 → ★ 신뢰도 자동 조정 근거
- **반례 발견 시**: `counter_signals`에 추가 (매핑 부정 조건)

### 검증 규칙
- **3건 룰** — 새 매핑은 `validation_record` 3건 이상 누적 후 ★ 상향 검토
- **반례 발견 시** — ★ 신뢰도 즉시 1단계 하향
- **연 1회 재검수** — 매핑이 1년간 사용 0건이면 폐기 검토

---

## 자매 프로젝트 위치

| 프로젝트 | DB 위치 | 비고 |
|---------|---------|------|
| tax-recovery-finder | 해당 repo 내 `signals/` (예시) | 신고 추정 + 경정청구 발굴 |
| ai-faction-quiz (본 워크스페이스) | 메타 스펙만 보유 | 실제 DB 없음 |

---

## 절대 금지

- **단서 없는 매핑 추가** — `evidence_sources` 비어있는 매핑 금지
- **개인 식별정보 DB 저장** — 사업자번호·이름·연락처 저장 금지 (`case_id`는 익명 카드 ID만)
- **검증 없이 ★★★ 부여** — 최소 3건 검증 후
- **반례 무시** — 반례 단서 발견 시 즉시 신뢰도 하향
- **DB 우회** — filing-estimator·tax-domain-expert는 새 매핑 발견 시 DB 업데이트 권고 누락 금지

---

## reviewer 점검 항목

`reviewer`는 세무 산출물 검증 시 다음을 점검:
- [ ] 추정에 시그널 DB 참조 흔적 있음 (기존 매핑 사용 또는 신규 권고)
- [ ] 새 매핑이면 `evidence_sources` 비어있지 않음
- [ ] `case_id` 외 개인 식별정보 없음
- [ ] `validation_record` 누적 결과가 신뢰도와 정합

---

## 참고

- `.claude/agents/filing-estimator.md` — 시그널 DB 1차 참조자
- `.claude/agents/tax-domain-expert.md` — 청구 가능성 검토 시 참조
- `.claude/AGENTS_RUBRIC.md` — P2 정의·평가 항목
