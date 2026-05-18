# -*- coding: utf-8 -*-
"""
T5a Gate - 결정론적 4단계 게이트
==================================
LLM 호출 0회. Python 3.11+, 표준 라이브러리 + jsonschema 사용.

4단계 순서:
  Step 1  citationToken 형식 + registry 존재 검증
  Step 2  제척기간 산술 검증 (국기법 45조 + 45-2조)
  Step 3  SignalBus 스키마 유효성 (jsonschema)
  Step 4  중복 제거 (sha256 키 기반)

탈락 신호는 폐기하지 않고 review_queue.json에 누적 저장.
"""

from __future__ import annotations

import calendar
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import jsonschema


# ---------------------------------------------------------------------------
# 파일럿 fixture 레지스트리 (T0 없이 standalone 실행용)
# ---------------------------------------------------------------------------

PILOT_REGISTRY: dict[str, bool] = {
    "nts:ruling:서면-2023-법규-0142:2023-01-15:abc12345": True,
    "scourt:case:2024두12345:2024-08-20:def67890": True,
    "moleg:law:조특법-24:2024-01-01:aa112233": True,
    "nts:ruling:기재부-법인-2023-0088:2023-06-10:bb334455": True,
    "scourt:case:2024두98765:2024-11-15:cc556677": True,
    "nts:ruling:법인세과-2019-0445:2019-08-01:dd778899": True,
    "nts:ruling:조특제도과-2021-0698:2021-05-18:ee001122": True,
    "moleg:law:조특법시행령-9:2020-02-11:ff334455": True,
    "moleg:law:조특법-7-별표:2017-07-01:aa556677": True,
    "nts:ruling:국제세원-2022-0055:2022-09-01:bb778899": True,
    "nts:ruling:서면2팀-2016-0023:2016-03-15:cc990011": True,
    # 타법 개정 계열 (SIG-009~014)
    "moleg:law:중대재해처벌법-4:2022-01-27:a1b2c3d4": True,
    "moleg:law:화관법-24:2015-12-01:b1c2d3e4": True,
    "moleg:law:개보법-28의2:2023-09-15:c1d2e3f4": True,
    "nts:ruling:서면-2024-법규-0033:2024-03-10:d1e2f3a4": True,
    "moleg:law:탄소중립법-24:2022-03-25:e1f2a3b4": True,
    "moleg:law:공정거래법-22의2:2021-12-30:f1a2b3c4": True,
    "moleg:law:건축물관리법-11:2020-05-01:a2b3c4d5": True,
    # 관행 파괴 계열 (SIG-015~018)
    "moleg:law:환경개선비용부담법-9:2019-01-01:b2c3d4e5": True,
    "scourt:case:2023두41234:2023-09-22:c2d3e4f5": True,
    "nts:ruling:법인세과-2023-0521:2023-11-15:d2e3f4a5": True,
    "nts:ruling:서면-2020-법규-2021:2021-06-01:e2f3a4b5": True,
    "nts:ruling:법인세과-2024-0088:2024-07-01:f2a3b4c5": True,
    # SIG-019~050 신규 토큰
    "nts:ruling:부가-2023-0055:2023-06-01:a3b4c5d6": True,
    "scourt:case:2022두55678:2022-12-01:b3c4d5e6": True,
    "nts:ruling:부가-2022-0133:2022-11-15:c3d4e5f6": True,
    "nts:ruling:부가-2021-0077:2021-09-10:d3e4f5a6": True,
    "moleg:law:환경친화적자동차법-2:2020-11-01:e3f4a5b6": True,
    "nts:ruling:서면-2022-법규-0211:2022-07-15:f3a4b5c6": True,
    "moleg:law:약사법-34:2019-01-01:a4b5c6d7": True,
    "nts:ruling:서면-2023-법규-0456:2023-08-20:b4c5d6e7": True,
    "nts:ruling:서면-2021-법규-0088:2021-11-01:c4d5e6f7": True,
    "nts:ruling:서면-2024-법규-0188:2024-05-15:d4e5f6a7": True,
    "moleg:law:건설기술진흥법-62의2:2021-07-01:e4f5a6b7": True,
    "moleg:law:대규모유통업법-12:2020-01-29:f4a5b6c7": True,
    "nts:ruling:법인세과-2023-0788:2023-12-15:a5b6c7d8": True,
    "moleg:law:보험업법-120:2023-01-01:b5c6d7e8": True,
    "moleg:law:수소경제육성법-5:2021-02-05:c5d6e7f8": True,
    "moleg:law:선박평형수관리법-8:2019-09-22:d5e6f7a8": True,
    "moleg:law:방위사업법-33:2022-06-10:e5f6a7b8": True,
    "nts:ruling:서면-2022-법규-0339:2022-09-01:f5a6b7c8": True,
    "moleg:law:항공안전법-23:2020-05-27:a6b7c8d9": True,
    "moleg:law:근로기준법-76의3:2019-07-16:b6c7d8e9": True,
    "nts:ruling:법인세과-2022-0215:2022-04-18:c6d7e8f9": True,
    "scourt:case:2023두15678:2023-05-12:d6e7f8a9": True,
    "nts:ruling:서면-2021-법규-0455:2021-08-20:e6f7a8b9": True,
    "nts:ruling:국제세원-2021-0122:2021-12-10:f6a7b8c9": True,
    "nts:ruling:서면-2019-법규-0567:2019-09-25:a7b8c9d0": True,
    "moleg:law:물환경보전법-38의2:2021-01-05:b7c8d9e0": True,
    "moleg:law:순환경제촉진법-13:2022-12-30:c7d8e9f0": True,
    "moleg:law:해양환경관리법-41의2:2020-01-01:d7e8f9a0": True,
    "nts:ruling:법인세과-2019-0188:2019-03-20:f7a8b9c0": True,
    "moleg:law:폐기물관리법-18:2022-01-01:a8b9c0d1": True,
    "nts:ruling:서면-2022-법규-0512:2022-11-30:b8c9d0e1": True,
    "moleg:law:에너지이용합리화법-35:2021-04-20:d8e9f0a1": True,
    "nts:ruling:법인세과-2021-0099:2021-02-25:c8d9e0f1": True,
    "nts:ruling:서면-2020-법규-0789:2020-10-15:e8f9a0b1": True,
    "moleg:law:항공사업법-61의2:2022-06-10:e7f8a9b0": True,
}

# citationToken 형식 정규식 (Step 1)
_TOKEN_RE = re.compile(
    r"^(nts|moleg|scourt|tribunal):[a-z_]+:[^:]+:\d{4}-\d{2}-\d{2}:[a-f0-9]{8}$"
)


# ---------------------------------------------------------------------------
# GateResult
# ---------------------------------------------------------------------------

@dataclass
class GateResult:
    passed: bool
    signal_id: str
    fail_reason: Optional[str]   # None이면 통과
    track: Optional[str]         # "5yr_ordinary" | "3mo_posterior" | None
    deadline: Optional[date]


# ---------------------------------------------------------------------------
# 내부 헬퍼
# ---------------------------------------------------------------------------

def _parse_date(s: str) -> date:
    """ISO date 문자열 -> date 객체. 실패 시 ValueError."""
    return date.fromisoformat(s)


def _add_months(d: date, months: int) -> date:
    """월 단위 덧셈. 말일 초과 시 해당 월 말일로 clamp."""
    total_months = d.month - 1 + months
    year = d.year + total_months // 12
    month = total_months % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return d.replace(year=year, month=month, day=min(d.day, last_day))


def check_retroactivity(
    signal: dict,
    today: date,
    filing_deadline: Optional[date] = None,
    trigger_date: Optional[date] = None,
) -> tuple[bool, Optional[str], Optional[str], Optional[date]]:
    """
    제척기간 산술 검증.

    Track A: 신고기한 다음날 + 5년 이내  (국기법 45조)
    Track B: 후발사유 발생일 + 3개월 이내 (국기법 45-2조 2항)
             triggerCitationToken 필수 - 없으면 Track B 차단

    반환: (pass: bool, track: str | None, reason: str | None, deadline: date | None)
    """
    # gateDecisions에서 트랙 정보 추출 시도
    gate_decisions: list[dict] = signal.get("gateDecisions", [])
    g1: Optional[dict] = next(
        (g for g in gate_decisions if g.get("gate") == "G1"), None
    )

    # triggerCitationToken 유무로 Track B 가능 여부 판단
    trigger_token: Optional[str] = None
    if g1 and g1.get("track") == "3mo_posterior":
        trigger_token = g1.get("triggerCitationToken")

    # --- Track B: trigger_date 제공 + triggerCitationToken 존재 ---
    if trigger_date is not None:
        if trigger_token is None:
            # Track B 조건 불충족 - triggerCitationToken 없음
            return False, None, "missing_trigger_citation_token", None
        deadline_b = _add_months(trigger_date, 3)
        if today <= deadline_b:
            return True, "3mo_posterior", None, deadline_b
        else:
            return False, "3mo_posterior", "posterior_period_expired", deadline_b

    # --- Track A: filing_deadline 제공 ---
    if filing_deadline is not None:
        # 신고기한 다음날부터 5년
        start = filing_deadline + timedelta(days=1)
        deadline_a = start.replace(year=start.year + 5)
        if today <= deadline_a:
            return True, "5yr_ordinary", None, deadline_a
        else:
            return False, "5yr_ordinary", "ordinary_period_expired", deadline_a

    # --- 파라미터 없음 - gateDecisions에서 트랙/데드라인 읽어 판단 ---
    if g1 and g1.get("pass") is True:
        track = g1.get("track")
        raw_deadline = g1.get("deadline")
        parsed_deadline: Optional[date] = None
        if raw_deadline:
            try:
                parsed_deadline = _parse_date(raw_deadline)
            except ValueError:
                pass
        if parsed_deadline is not None and today <= parsed_deadline:
            return True, track, None, parsed_deadline
        elif parsed_deadline is not None:
            return False, track, "period_expired_from_gate_decisions", parsed_deadline

    # 판단 불가 -> Track A로 간주하되 filing_deadline 없으므로 통과 불가
    return False, None, "missing_filing_deadline", None


# ---------------------------------------------------------------------------
# T5aGate
# ---------------------------------------------------------------------------

class T5aGate:
    """
    4단계 결정론적 게이트.

    Parameters
    ----------
    citation_registry : dict
        {token_str: True} 형태의 citation 레지스트리.
    schema_path : str
        signalbus_schema.json 경로.
    review_queue_path : str
        탈락 신호를 누적 저장할 JSON 파일 경로.
    """

    def __init__(
        self,
        citation_registry: dict,
        schema_path: str,
        review_queue_path: str,
    ) -> None:
        self._registry = citation_registry
        self._schema = self._load_schema(schema_path)
        self._review_queue_path = Path(review_queue_path)
        self._seen_keys: set[str] = set()

    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------

    def run(
        self,
        signal: dict,
        filing_deadline: Optional[date] = None,
        trigger_date: Optional[date] = None,
        *,
        today: Optional[date] = None,
    ) -> GateResult:
        """
        4단계 순차 실행. 첫 실패에서 중단 후 review_queue에 저장.

        Parameters
        ----------
        signal          : SignalBus 딕셔너리
        filing_deadline : Track A 계산용 신고기한 (date)
        trigger_date    : Track B 계산용 후발사유 발생일 (date)
        today           : 오늘 날짜 오버라이드 (테스트용, 기본 date.today())
        """
        _today = today if today is not None else date.today()
        signal_id: str = signal.get("signalId", "<unknown>")

        # Step 1: citationToken 검증
        result = self._step1_citation(signal, signal_id)
        if result is not None:
            self._enqueue(signal, result.fail_reason)
            return result

        # Step 2: 제척기간 산술 검증
        passed, track, reason, deadline = check_retroactivity(
            signal, _today, filing_deadline, trigger_date
        )
        if not passed:
            gr = GateResult(
                passed=False,
                signal_id=signal_id,
                fail_reason=reason or "retroactivity_check_failed",
                track=track,
                deadline=deadline,
            )
            self._enqueue(signal, gr.fail_reason)
            return gr

        # Step 3: 스키마 유효성
        result = self._step3_schema(signal, signal_id)
        if result is not None:
            self._enqueue(signal, result.fail_reason)
            return result

        # Step 4: 중복 제거
        dup_key = self._dedup_key(signal)
        if dup_key in self._seen_keys:
            gr = GateResult(
                passed=False,
                signal_id=signal_id,
                fail_reason="duplicate",
                track=track,
                deadline=deadline,
            )
            self._enqueue(signal, gr.fail_reason)
            return gr
        self._seen_keys.add(dup_key)

        return GateResult(
            passed=True,
            signal_id=signal_id,
            fail_reason=None,
            track=track,
            deadline=deadline,
        )

    def batch_run(
        self,
        signals: list[dict],
        filing_deadlines: Optional[list[Optional[date]]] = None,
        trigger_dates: Optional[list[Optional[date]]] = None,
        *,
        today: Optional[date] = None,
    ) -> list[GateResult]:
        """
        복수 신호 처리.

        filing_deadlines / trigger_dates 는 signals와 같은 인덱스 순서.
        None이면 각 신호에 None 전달.
        """
        n = len(signals)
        fds: list[Optional[date]] = filing_deadlines or [None] * n
        tds: list[Optional[date]] = trigger_dates or [None] * n
        results: list[GateResult] = []
        for sig, fd, td in zip(signals, fds, tds):
            results.append(self.run(sig, filing_deadline=fd, trigger_date=td, today=today))
        return results

    # ------------------------------------------------------------------
    # 내부 단계
    # ------------------------------------------------------------------

    def _step1_citation(self, signal: dict, signal_id: str) -> Optional[GateResult]:
        """Step 1: citationTokens 배열 검증."""
        tokens: list = signal.get("citationTokens", [])

        # 빈 배열
        if not tokens:
            return GateResult(
                passed=False,
                signal_id=signal_id,
                fail_reason="no_citation",
                track=None,
                deadline=None,
            )

        for token in tokens:
            # 형식 검증
            if not _TOKEN_RE.match(token):
                return GateResult(
                    passed=False,
                    signal_id=signal_id,
                    fail_reason=f"invalid_token_format:{token}",
                    track=None,
                    deadline=None,
                )
            # registry 존재 검증
            if token not in self._registry:
                return GateResult(
                    passed=False,
                    signal_id=signal_id,
                    fail_reason="missing_citation_token",
                    track=None,
                    deadline=None,
                )

        return None  # 통과

    def _step3_schema(self, signal: dict, signal_id: str) -> Optional[GateResult]:
        """Step 3: jsonschema 검증."""
        try:
            jsonschema.validate(instance=signal, schema=self._schema)
        except jsonschema.ValidationError as exc:
            # 실패 필드를 path에서 추출
            if exc.absolute_path:
                path = ".".join(str(p) for p in exc.absolute_path)
            else:
                path = str(exc.validator_value)
            return GateResult(
                passed=False,
                signal_id=signal_id,
                fail_reason=f"schema_invalid:{path}",
                track=None,
                deadline=None,
            )
        return None  # 통과

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    @staticmethod
    def _dedup_key(signal: dict) -> str:
        """sha256(lawArticle + ideaTitle) 기반 중복 키."""
        raw = (signal.get("lawArticle", "") + signal.get("ideaTitle", "")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _enqueue(self, signal: dict, fail_reason: Optional[str]) -> None:
        """탈락 신호를 review_queue.json에 누적 저장."""
        entry = {
            "signalId": signal.get("signalId", "<unknown>"),
            "ideaTitle": signal.get("ideaTitle", ""),
            "lawArticle": signal.get("lawArticle", ""),
            "failReason": fail_reason,
            "rejectedAt": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        queue: list[dict] = []
        if self._review_queue_path.exists():
            try:
                with self._review_queue_path.open("r", encoding="utf-8") as f:
                    queue = json.load(f)
            except (json.JSONDecodeError, OSError):
                queue = []

        queue.append(entry)

        with self._review_queue_path.open("w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _load_schema(schema_path: str) -> dict:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)


# ---------------------------------------------------------------------------
# __main__ - 파일럿 3개 신호 T5a 통과 테스트
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    _HERE = Path(__file__).parent
    _SCHEMA_PATH = str(_HERE / "signalbus_schema.json")
    _FIXTURES_PATH = _HERE / "pilot_fixtures.json"
    _QUEUE_PATH = _HERE / "review_queue.json"

    # 기존 review_queue 초기화 (테스트 반복 실행 대비)
    if _QUEUE_PATH.exists():
        _QUEUE_PATH.unlink()

    # fixture 로드
    with _FIXTURES_PATH.open("r", encoding="utf-8") as fp:
        fixture_data = json.load(fp)
    signals = fixture_data["signals"]

    gate = T5aGate(
        citation_registry=PILOT_REGISTRY,
        schema_path=_SCHEMA_PATH,
        review_queue_path=str(_QUEUE_PATH),
    )

    print("=" * 70)
    print("T5a Gate - 파일럿 fixture 3개 신호 게이트 테스트")
    print("=" * 70)

    # 신호 1: 게임사 R&D -> PASS (Track A)
    # gateDecisions deadline = "2026-12-31" -> filing_deadline = 2021-12-31
    # (filing_deadline + 1일 + 5년 = 2027-01-01 >= today 2026-05-18)
    sig1 = signals[0]
    r1 = gate.run(
        sig1,
        filing_deadline=date(2021, 12, 31),
        today=date(2026, 5, 18),
    )
    status1 = "PASS" if r1.passed else "FAIL({})".format(r1.fail_reason)
    print("[{}] {}".format(status1, sig1["ideaTitle"]))
    print("         track={}  deadline={}".format(r1.track, r1.deadline))

    # 신호 2: 통합투자 -> PASS (Track A)
    # gateDecisions deadline = "2027-03-31" -> filing_deadline = 2022-03-31
    # (filing_deadline + 1일 + 5년 = 2027-04-01 >= today 2026-05-18)
    sig2 = signals[1]
    r2 = gate.run(
        sig2,
        filing_deadline=date(2022, 3, 31),
        today=date(2026, 5, 18),
    )
    status2 = "PASS" if r2.passed else "FAIL({})".format(r2.fail_reason)
    print("[{}] {}".format(status2, sig2["ideaTitle"]))
    print("         track={}  deadline={}".format(r2.track, r2.deadline))

    # 신호 3: 장애인고용부담금 -> PASS (Track B)
    # triggerCitationToken: "scourt:case:2024두98765:2024-11-15:cc556677"
    # trigger_date = 2024-11-15 -> deadline = 2025-02-15
    # today를 deadline 전날로 설정해 PASS 확인
    sig3 = signals[2]
    r3 = gate.run(
        sig3,
        trigger_date=date(2024, 11, 15),
        today=date(2025, 2, 14),   # deadline(2025-02-15) 전날
    )
    status3 = "PASS" if r3.passed else "FAIL({})".format(r3.fail_reason)
    print("[{}] {}".format(status3, sig3["ideaTitle"]))
    print("         track={}  deadline={}".format(r3.track, r3.deadline))

    print("-" * 70)
    all_passed = r1.passed and r2.passed and r3.passed
    print("결과: {}".format("전체 통과" if all_passed else "일부 실패"))

    # review_queue 확인 (탈락 없으면 파일 없음)
    if _QUEUE_PATH.exists():
        with _QUEUE_PATH.open("r", encoding="utf-8") as fp:
            queue_items = json.load(fp)
        print("\nreview_queue.json: {}건 탈락".format(len(queue_items)))
        for item in queue_items:
            print("  - {} / {}".format(item["signalId"], item["failReason"]))
    else:
        print("\nreview_queue.json: 탈락 없음 (파일 생성 안됨)")

    sys.exit(0 if all_passed else 1)
