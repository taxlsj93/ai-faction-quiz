# -*- coding: utf-8 -*-
"""
TaxRecoveryPipeline — T0 → T5a → T5b E2E 오케스트레이터
=========================================================
파일럿 3개 아이디어를 파이프라인으로 실행하고
output_sample.json 및 SC-1 결과를 출력합니다.
"""
from __future__ import annotations

import io
import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# 경로 설정 — 직접 실행 시 sibling import 지원
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

from t0_citation_adapter import CitationAdapter, MOCK_REGISTRY  # noqa: E402
from t5a_gate import T5aGate, GateResult, PILOT_REGISTRY        # noqa: E402
from t5b_doctrinal import T5bDoctrinal, T5bResult               # noqa: E402


# ---------------------------------------------------------------------------
# 데이터 클래스
# ---------------------------------------------------------------------------

@dataclass
class PipelineRecord:
    signal: dict
    gate_result: GateResult
    doctrinal_result: Optional[T5bResult] = None

    def to_dict(self) -> dict:
        doc = {
            "signalId": self.signal.get("signalId", ""),
            "ideaTitle": self.signal.get("ideaTitle", ""),
            "lawArticle": self.signal.get("lawArticle", ""),
            "citationTokens": self.signal.get("citationTokens", []),
            "estimatedRefundRange": self.signal.get("estimatedRefundRange"),
            "evidenceChecklist": self.signal.get("evidenceChecklist", []),
            "ksicMapping": self.signal.get("ksicMapping"),
            "gateResult": {
                "passed": self.gate_result.passed,
                "track": self.gate_result.track,
                "deadline": str(self.gate_result.deadline) if self.gate_result.deadline else None,
                "failReason": self.gate_result.fail_reason,
            },
        }
        if self.doctrinal_result:
            dr = self.doctrinal_result
            doc["doctrinalResult"] = {
                "confidence": dr.confidence,
                "finalDecision": dr.final_decision,
                "crossEvidence": dr.cross_evidence,
                "counterExamples": dr.counter_examples,
                "reasoning": dr.reasoning,
                "checkedBy": dr.checked_by,
            }
        return doc


@dataclass
class PipelineResult:
    adopted: list[PipelineRecord] = field(default_factory=list)
    review: list[PipelineRecord] = field(default_factory=list)
    rejected: list[PipelineRecord] = field(default_factory=list)
    review_queue_path: str = ""


# ---------------------------------------------------------------------------
# TaxRecoveryPipeline
# ---------------------------------------------------------------------------

class TaxRecoveryPipeline:
    """T0 → T5a → T5b 파이프라인 오케스트레이터.

    Parameters
    ----------
    mock_mode:
        True이면 T5b LLM 호출 없이 mock 결과 사용.
    review_queue_path:
        T5a 탈락 신호 저장 경로. 기본값: tax-finder/review_queue.json
    """

    def __init__(
        self,
        mock_mode: bool = True,
        review_queue_path: Optional[str] = None,
    ) -> None:
        self._adapter = CitationAdapter()

        _review_queue = review_queue_path or str(_HERE / "review_queue.json")
        self._review_queue_path = _review_queue

        self._gate = T5aGate(
            citation_registry=PILOT_REGISTRY,
            schema_path=str(_HERE / "signalbus_schema.json"),
            review_queue_path=_review_queue,
        )
        self._doctrinal = T5bDoctrinal(mock_mode=mock_mode)

    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------

    def run(
        self,
        signals: list[dict],
        today: Optional[date] = None,
        today_overrides: Optional[dict[str, date]] = None,
    ) -> PipelineResult:
        """파이프라인 실행.

        1. 각 signal에 T5a gate 적용
        2. PASS 신호만 T5b 법리 검증
        3. PipelineResult 반환

        Parameters
        ----------
        today:
            모든 신호에 적용할 오늘 날짜 오버라이드 (테스트용).
        today_overrides:
            signalId → date 매핑. 신호별로 다른 today를 지정할 때 사용.
            today보다 우선 적용.
        """
        result = PipelineResult(review_queue_path=self._review_queue_path)
        _overrides = today_overrides or {}

        for signal in signals:
            sig_id = signal.get("signalId", "")
            _today = _overrides.get(sig_id) or today
            filing_deadline, trigger_date = self._extract_gate_params(signal)
            gate_result = self._gate.run(
                signal,
                filing_deadline=filing_deadline,
                trigger_date=trigger_date,
                today=_today,
            )

            if not gate_result.passed:
                result.rejected.append(PipelineRecord(signal=signal, gate_result=gate_result))
                continue

            # T5a 통과 → T5b
            citation_metadata = self._lookup_citations(signal)
            # T5b는 signal_id (snake_case) 키를 사용 — SignalBus의 signalId에서 매핑
            sig_for_t5b = {**signal, "signal_id": signal.get("signalId", "")}
            doctrinal = self._doctrinal.verify(sig_for_t5b, citation_metadata)

            record = PipelineRecord(
                signal=signal,
                gate_result=gate_result,
                doctrinal_result=doctrinal,
            )
            if doctrinal.final_decision == "ADOPTED":
                result.adopted.append(record)
            elif doctrinal.final_decision == "REVIEW":
                result.review.append(record)
            else:
                result.rejected.append(record)

        return result

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _extract_gate_params(
        self, signal: dict
    ) -> tuple[Optional[date], Optional[date]]:
        """gateDecisions에서 filing_deadline / trigger_date 추출.

        Track A: filing_deadline 없이 gateDecisions 폴백 경로 사용.
        Track B: triggerCitationToken 날짜 파트에서 trigger_date 파싱.
        """
        gate_decisions = signal.get("gateDecisions", [])
        g1 = next((g for g in gate_decisions if g.get("gate") == "G1"), None)
        if g1 is None:
            return None, None

        if g1.get("track") == "3mo_posterior":
            trigger_token = g1.get("triggerCitationToken", "")
            parts = trigger_token.split(":")
            if len(parts) == 5:
                try:
                    return None, date.fromisoformat(parts[3])
                except ValueError:
                    pass

        # Track A: T5a 내부 폴백(gateDecisions deadline 직접 참조)이 처리
        return None, None

    def _lookup_citations(self, signal: dict) -> list[dict]:
        """citationTokens를 T0 adapter로 조회해 본문 메타데이터 반환."""
        docs: list[dict] = []
        for token in signal.get("citationTokens", []):
            lookup_result = self._adapter.lookup(token)
            if lookup_result.get("citationStatus") == "FOUND":
                docs.append(lookup_result["doc"])
        return docs


# ---------------------------------------------------------------------------
# __main__ — 파일럿 3개 아이디어 E2E 테스트
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    _FIXTURES_PATH = _HERE / "pilot_fixtures.json"
    _OUTPUT_PATH = _HERE / "output_sample.json"
    _REVIEW_QUEUE_PATH = _HERE / "review_queue.json"

    # 이전 테스트 결과 초기화
    if _REVIEW_QUEUE_PATH.exists():
        _REVIEW_QUEUE_PATH.unlink()

    # 파일럿 신호 로드
    with _FIXTURES_PATH.open("r", encoding="utf-8") as fp:
        fixture_data = json.load(fp)
    signals = fixture_data["signals"]

    # 파이프라인 실행 (mock_mode=True)
    pipeline = TaxRecoveryPipeline(
        mock_mode=True,
        review_queue_path=str(_REVIEW_QUEUE_PATH),
    )
    # sig3 (Track B): triggerCitationToken 발생일 2024-11-15 기준
    # deadline = 2025-02-15. 오늘(2026-05-18)은 이미 만료 → 파일럿 검증용 날짜 고정
    SIG3_ID = "01900000-0000-7000-8000-000000000003"
    result = pipeline.run(
        signals,
        today_overrides={SIG3_ID: date(2025, 2, 14)},
    )

    # SC-1 검증: 파일럿 3개 전부 ADOPTED → PASS
    sc1_pass = len(result.adopted) >= 3

    # 콘솔 요약 출력
    print("=" * 70)
    print("TaxRecoveryPipeline — 파일럿 3개 아이디어 E2E 테스트 (mock)")
    print("=" * 70)

    _DECISION_LABEL = {
        "ADOPTED": "[ADOPTED  OK]",
        "REVIEW":  "[REVIEW    ?]",
        "REJECTED": "[REJECTED NG]",
    }

    all_records: list[PipelineRecord] = (
        result.adopted + result.review + result.rejected
    )
    # 입력 순서로 정렬 (signalId 기준)
    signal_order = {sig["signalId"]: i for i, sig in enumerate(signals)}
    all_records.sort(key=lambda r: signal_order.get(r.signal.get("signalId", ""), 99))

    for rec in all_records:
        idea = rec.signal.get("ideaTitle", "")
        sig_id = rec.signal.get("signalId", "")

        if rec.doctrinal_result:
            dr = rec.doctrinal_result
            label = _DECISION_LABEL.get(dr.final_decision, f"[{dr.final_decision}]")
            print(f"\n{label} {idea}  (signalId={sig_id})")
            print(f"  법령        : {rec.signal.get('lawArticle', '')}")
            print(f"  track       : {rec.gate_result.track}")
            print(f"  deadline    : {rec.gate_result.deadline}")
            print(f"  confidence  : {dr.confidence}/100")
            print(f"  crossEvidence: {dr.cross_evidence}")
            if dr.counter_examples:
                for ce in dr.counter_examples:
                    print(f"  반례        : {ce}")
            print(f"  reasoning   : {dr.reasoning}")
        else:
            print(f"\n[GATE FAIL ] {idea}  (signalId={sig_id})")
            print(f"  failReason  : {rec.gate_result.fail_reason}")

    print("\n" + "-" * 70)
    print(f"ADOPTED : {len(result.adopted)}건")
    print(f"REVIEW  : {len(result.review)}건")
    print(f"REJECTED: {len(result.rejected)}건")
    print("-" * 70)
    sc1_label = "PASS" if sc1_pass else "FAIL"
    print(f"SC-1 파일럿 재발견: {sc1_label} ({len(result.adopted)}/3)")
    print("=" * 70)

    # output_sample.json 저장
    output = {
        "runAt": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mockMode": True,
        "sc1Pass": sc1_pass,
        "sc1Detail": f"{len(result.adopted)}/3 ADOPTED",
        "adopted": [r.to_dict() for r in result.adopted],
        "review": [r.to_dict() for r in result.review],
        "rejected": [r.to_dict() for r in result.rejected],
        "reviewQueuePath": str(_REVIEW_QUEUE_PATH),
    }
    with _OUTPUT_PATH.open("w", encoding="utf-8") as fp:
        json.dump(output, fp, ensure_ascii=False, indent=2)

    print(f"\noutput_sample.json 저장 완료: {_OUTPUT_PATH}")
    if _REVIEW_QUEUE_PATH.exists():
        with _REVIEW_QUEUE_PATH.open("r", encoding="utf-8") as fp:
            queue_items = json.load(fp)
        print(f"review_queue.json: {len(queue_items)}건 탈락")

    sys.exit(0 if sc1_pass else 1)
