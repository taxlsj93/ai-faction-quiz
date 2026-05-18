"""
T5b Doctrinal Verifier
======================
LLM 기반 법리 검증 모듈. Anthropic Python SDK (claude-opus-4-7) 사용.
- T5a 통과 신호만 입력으로 받음
- 프롬프트 캐싱 적용 (system 프롬프트 cache_control)
- 출력: confidence, counterExamples, crossEvidence, finalDecision

anthropic 패키지 없을 때 mock_mode로 자동 fallback.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# anthropic 패키지 가용 여부 감지
# ---------------------------------------------------------------------------

try:
    import anthropic as _anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


# ---------------------------------------------------------------------------
# 데이터 클래스
# ---------------------------------------------------------------------------

@dataclass
class T5bResult:
    signal_id: str
    confidence: int              # 0~100
    counter_examples: list[str]
    cross_evidence: bool         # 판례+예규 등 2종 이상 교차 인용 여부
    final_decision: str          # "ADOPTED" | "REVIEW" | "REJECTED"
    reasoning: str               # 법리 판단 근거 요약 (한국어)
    checked_by: str = "T5b"


# ---------------------------------------------------------------------------
# 시스템 프롬프트 (캐싱 대상)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """당신은 대한민국 세법 전문 검증 AI입니다.
경정청구 아이디어의 법리 타당성을 검증합니다.

검증 기준:
1. 인용-주장 정합성: 인용된 판례/예규가 실제로 주장을 뒷받침하는가
2. 반례 탐지: 반대 취지 판례/예규가 존재하는가
3. 교차 증거: 판례+예규 또는 판례+법령 최소 2종 인용이 있는가
4. 갭 진위: 업계 미인지가 그럴듯한 근거가 있는가

반드시 JSON으로만 응답하라."""


# ---------------------------------------------------------------------------
# finalDecision 임계값 계산
# ---------------------------------------------------------------------------

def _compute_final_decision(confidence: int, cross_evidence: bool) -> str:
    """confidence + cross_evidence 조합으로 finalDecision 결정."""
    if confidence >= 70 and cross_evidence:
        return "ADOPTED"
    elif 50 <= confidence < 70:
        return "REVIEW"
    else:
        return "REJECTED"


# ---------------------------------------------------------------------------
# Mock 결과 (파일럿 3개 아이디어)
# ---------------------------------------------------------------------------

_MOCK_RESULTS: dict[str, T5bResult] = {
    "게임사 R&D": T5bResult(
        signal_id="게임사 R&D",
        confidence=82,
        counter_examples=[],
        cross_evidence=True,
        final_decision="ADOPTED",
        reasoning=(
            "조특법 제10조 적용 가능성을 뒷받침하는 판례(2024두12345)와 "
            "예규(서면-2023-법규-0142)가 모두 확인됨. "
            "게임소프트웨어 개발업 R&D 인건비의 세액공제 적용 근거 충분. "
            "반례 없음."
        ),
    ),
    "통합투자": T5bResult(
        signal_id="통합투자",
        confidence=75,
        counter_examples=[],
        cross_evidence=True,
        final_decision="ADOPTED",
        reasoning=(
            "조특법 제24조(2024년 개정) 및 기재부 예규(기재부-법인-2023-0088)가 "
            "안전자산 포함 통합투자세액공제 적용을 뒷받침함. "
            "법령+예규 교차 인용 충족. 반례 없음."
        ),
    ),
    "장애인고용부담금": T5bResult(
        signal_id="장애인고용부담금",
        confidence=90,
        counter_examples=[
            "법인세과-2019-0445 예규: 장애인 고용부담금 손금 산입 불인정 (사업 관련성 없음으로 판단)"
        ],
        cross_evidence=True,
        final_decision="ADOPTED",
        reasoning=(
            "대법원 판결(2024두98765)이 손금 산입을 명시적으로 인정. "
            "2019년 예규(법인세과-2019-0445)는 반례이나, "
            "이후 대법원 판결이 우선 적용됨. "
            "판례+예규 교차 인용 충족. 최신 판례 기준 ADOPTED."
        ),
    ),
    # ── 타법 개정 계열 ──────────────────────────────────────────────────────
    "중대재해처벌법 의무안전투자": T5bResult(
        signal_id="중대재해처벌법 의무안전투자",
        confidence=72,
        counter_examples=[],
        cross_evidence=True,
        final_decision="ADOPTED",
        reasoning=(
            "조특법 §24는 투자 동기(자발적·의무적)를 불문하고 요건 충족 시 세액공제 가능. "
            "중대재해처벌법상 의무투자도 통합투자세액공제 요건을 충족하면 공제 대상. "
            "법령(조특법-24)+타법(중대재해처벌법-4) 교차 인용 충족. "
            "실무에서 '법적 의무=공제 불가'로 오인하는 갭이 존재함."
        ),
    ),
    "화관법 의무취급시설": T5bResult(
        signal_id="화관법 의무취급시설",
        confidence=70,
        counter_examples=[],
        cross_evidence=True,
        final_decision="ADOPTED",
        reasoning=(
            "화관법 §24 의무 취급시설 개선 투자는 조특법 §25의3 환경보전시설 세액공제 별표 항목에 해당. "
            "법령(조특법-25의3)+타법(화관법-24) 교차 인용 충족. "
            "기업들이 환경부 인증 절차 미비를 이유로 미신청하는 갭 확인."
        ),
    ),
    "개인정보보호법 강화 정보보안 R&D": T5bResult(
        signal_id="개인정보보호법 강화 정보보안 R&D",
        confidence=67,
        counter_examples=[
            "정보보안 비용을 R&D가 아닌 운영비(IT비용)로 처리해야 한다는 실무 관행 존재"
        ],
        cross_evidence=True,
        final_decision="REVIEW",
        reasoning=(
            "개인정보보호법 강화로 CPO 직속 보안연구 활동이 확대됨. "
            "암호화·익명화 기술 연구는 조특법 §10 R&D 정의(불확실성·기술혁신성)를 충족 가능. "
            "예규(서면-2024-법규-0033)+법령(개보법-28의2) 교차 인용 충족. "
            "다만 '운영 목적 보안비 vs 연구개발 목적' 구분이 쟁점 — 사실관계 검토 필요."
        ),
    ),
    "탄소중립기본법 배출권 업체 감축설비": T5bResult(
        signal_id="탄소중립기본법 배출권 업체 감축설비",
        confidence=73,
        counter_examples=[],
        cross_evidence=True,
        final_decision="ADOPTED",
        reasoning=(
            "탄소중립기본법 §24 의무 감축설비 투자는 에너지이용합리화법상 에너지절약시설에 해당. "
            "조특법 §25의2 에너지절약시설 세액공제 적용 가능. "
            "법령(탄소중립법-24)+조특법 교차 인용 충족. "
            "배출권 할당 업체가 환경부 인증 서류 미비로 미신청하는 갭이 대기업에서 빈발."
        ),
    ),
    "공정거래법 개정 준법지원인 운영비": T5bResult(
        signal_id="공정거래법 개정 준법지원인 운영비",
        confidence=63,
        counter_examples=[
            "법인세법 §21 1호: 법령위반 관련 비용은 손금불산입 — 컴플라이언스 비용의 성격 논란"
        ],
        cross_evidence=False,
        final_decision="REVIEW",
        reasoning=(
            "공정거래법 §22의2 의무화된 준법지원인 인건비·시스템 구축비는 예방적 업무비용. "
            "법인세법 §19 업무관련성 요건 충족 시 손금 가능. "
            "다만 '법적 의무 준수 비용 vs 위반 관련 비용' 구분이 쟁점. "
            "판례 축적 중 — 법령 1종만 인용으로 cross_evidence 미충족. 추가 예규 필요."
        ),
    ),
    "건축물관리법 의무정밀안전점검비": T5bResult(
        signal_id="건축물관리법 의무정밀안전점검비",
        confidence=62,
        counter_examples=[
            "국세청 기존 예규: 건물 수선·점검비용을 자본적지출로 광범위하게 처리"
        ],
        cross_evidence=False,
        final_decision="REVIEW",
        reasoning=(
            "건축물관리법 §11 의무 정밀안전점검 비용은 기능 향상 없는 현상 유지 비용으로 수익적지출. "
            "법인세법 §19 손금 해당, §23 자본적지출 대상 아님. "
            "기존 관행(자본적지출 처리)에 반하는 주장 — 사실관계별 판단 필요. cross_evidence 미충족."
        ),
    ),
    # ── 관행 파괴 계열 ──────────────────────────────────────────────────────
    "환경개선부담금 손금산입": T5bResult(
        signal_id="환경개선부담금 손금산입",
        confidence=75,
        counter_examples=[
            "법인세법 §21 1호: 벌금·과태료 성격 부담금은 손금불산입 — 환경부담금 포함 논란"
        ],
        cross_evidence=True,
        final_decision="ADOPTED",
        reasoning=(
            "장애인고용부담금 대법원 판결(2024두98765): '사업 관련성 있는 법적 의무 부담금은 손금'. "
            "환경개선부담금(환경개선비용부담법 §9)은 건물·차량 보유 사업법인에 부과되는 사업관련 의무부담금. "
            "동일한 법리 유추 적용 가능. 판례+법령 교차 인용 충족. "
            "2024년 이후 유사 부담금 손금 인정 흐름의 확장 사례로 평가."
        ),
    ),
    "적격합병 형식요건 불비 이월결손금": T5bResult(
        signal_id="적격합병 형식요건 불비 이월결손금",
        confidence=68,
        counter_examples=[
            "법인세법 §44의3: 적격합병 요건 불충족 시 이월결손금 승계 원칙적 불가",
            "과세관청 기존 입장: 형식요건 불비는 적격합병 인정 불가"
        ],
        cross_evidence=True,
        final_decision="REVIEW",
        reasoning=(
            "대법원 2023두41234: 합병비율 산정 등 일부 형식요건 불비에도 불구하고 "
            "사업계속성·고용승계 등 실질요건 충족 시 적격합병 인정. "
            "판례+예규(법인세과-2023-0521) 교차 인용 충족. "
            "수백억 이월결손금 승계 거부 기업에 경정청구 여지. "
            "사실관계별 판단 필요 — REVIEW 권고."
        ),
    ),
    "업무용 리스차량 임차료 전액 한도 오류": T5bResult(
        signal_id="업무용 리스차량 임차료 전액 한도 오류",
        confidence=78,
        counter_examples=[],
        cross_evidence=True,
        final_decision="ADOPTED",
        reasoning=(
            "법인세법 §27의2 및 예규(서면-2020-법규-2021): 리스 임차료 중 감가상각비 상당액만 "
            "연 800만원 한도 적용 대상이며 보험료·수리비는 별도 처리. "
            "10년 이상 실무에서 총임차료 기준으로 한도 적용하는 오류 만연. "
            "법령+예규 교차 인용 충족. 대부분 법인에서 손금 과소계상 발생. "
            "경정청구 적용 시 건당 수백만~수천만원 환급 가능."
        ),
    ),
    "공정거래법 절차위반 과징금 손금산입": T5bResult(
        signal_id="공정거래법 절차위반 과징금 손금산입",
        confidence=64,
        counter_examples=[
            "법인세법 §21 1호: 벌금·과료·과태료·가산금·강제징수비는 손금불산입 명문 규정",
            "국세청 기존 입장: 공정거래 과징금은 제재 성격으로 손금불산입"
        ],
        cross_evidence=True,
        final_decision="REVIEW",
        reasoning=(
            "예규(법인세과-2024-0088): 행정목적의 과징금은 벌금과 달리 개별 검토 필요. "
            "장애인고용부담금 판례(2024두98765) 법리 연장: 사업 관련 의무적 부과금은 손금 가능. "
            "판례+예규 교차 인용 충족. "
            "단, 법인세법 §21 명문 조항 극복이 쟁점 — 절차위반 과징금의 성격 분석 선행 필요."
        ),
    ),
}


# ---------------------------------------------------------------------------
# T5bDoctrinal 메인 클래스
# ---------------------------------------------------------------------------

class T5bDoctrinal:
    """LLM 기반 법리 검증기.

    Parameters
    ----------
    api_key:
        Anthropic API 키. None이면 환경변수 ANTHROPIC_API_KEY 사용.
    mock_mode:
        True이면 LLM 호출 없이 mock 결과 반환.
        anthropic 패키지 미설치 시 자동으로 True로 전환.
    """

    MODEL = "claude-opus-4-7"

    def __init__(self, api_key: str | None = None, mock_mode: bool = False) -> None:
        if not _ANTHROPIC_AVAILABLE:
            mock_mode = True

        self.mock_mode = mock_mode

        if not mock_mode:
            self._client = _anthropic.Anthropic(api_key=api_key)
        else:
            self._client = None

    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------

    def verify(self, signal: dict, citation_metadata: list[dict]) -> T5bResult:
        """경정청구 아이디어 법리 검증.

        Parameters
        ----------
        signal:
            SignalBus 레코드. 필수 키: signal_id, lawArticle, ideaTitle.
        citation_metadata:
            T0에서 조회한 인용 원문 메타데이터 목록.
            각 항목: {"docId": str, "docType": str, "body": str, ...}

        Returns
        -------
        T5bResult
        """
        if self.mock_mode:
            return self._mock_verify(signal)
        return self._llm_verify(signal, citation_metadata)

    # ------------------------------------------------------------------
    # LLM 검증 (실제 API 호출)
    # ------------------------------------------------------------------

    def _llm_verify(self, signal: dict, citation_metadata: list[dict]) -> T5bResult:
        signal_id = signal.get("signal_id", "unknown")
        law_article = signal.get("lawArticle", "")
        idea_title = signal.get("ideaTitle", "")

        # citation_metadata를 번호 목록으로 포맷
        citation_lines: list[str] = []
        for i, meta in enumerate(citation_metadata, start=1):
            doc_id = meta.get("docId", "")
            doc_type = meta.get("docType", "")
            body = meta.get("body", "")
            citation_lines.append(f"{i}. [{doc_type}] {doc_id}: {body}")
        citation_block = "\n".join(citation_lines) if citation_lines else "(인용 없음)"

        user_content = (
            f"다음 경정청구 아이디어를 검증하라:\n\n"
            f"법령: {law_article}\n"
            f"아이디어: {idea_title}\n"
            f"인용 근거:\n{citation_block}\n\n"
            "JSON 형식으로만 응답:\n"
            "{\n"
            '  "confidence": 0~100,\n'
            '  "counterExamples": ["반례 설명..."],\n'
            '  "crossEvidence": true/false,\n'
            '  "reasoning": "한국어 근거 요약",\n'
            '  "finalDecision": "ADOPTED|REVIEW|REJECTED"\n'
            "}"
        )

        try:
            response = self._client.messages.create(
                model=self.MODEL,
                max_tokens=1024,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[
                    {"role": "user", "content": user_content}
                ],
            )
            raw_text = response.content[0].text.strip()
            return self._parse_response(signal_id, raw_text)

        except Exception as exc:  # noqa: BLE001
            return T5bResult(
                signal_id=signal_id,
                confidence=0,
                counter_examples=[],
                cross_evidence=False,
                final_decision="REJECTED",
                reasoning=f"API 오류: {exc}",
            )

    def _parse_response(self, signal_id: str, raw_text: str) -> T5bResult:
        """LLM 응답 JSON 파싱."""
        try:
            # 코드블록 래핑 제거 (```json ... ```)
            text = raw_text
            if text.startswith("```"):
                lines = text.splitlines()
                text = "\n".join(
                    line for line in lines
                    if not line.strip().startswith("```")
                )

            data = json.loads(text)
            confidence = int(data.get("confidence", 0))
            counter_examples = data.get("counterExamples", [])
            cross_evidence = bool(data.get("crossEvidence", False))
            reasoning = data.get("reasoning", "")

            # LLM이 반환한 finalDecision 대신 임계값 기준으로 재계산 (일관성 보장)
            final_decision = _compute_final_decision(confidence, cross_evidence)

            return T5bResult(
                signal_id=signal_id,
                confidence=confidence,
                counter_examples=counter_examples,
                cross_evidence=cross_evidence,
                final_decision=final_decision,
                reasoning=reasoning,
            )

        except Exception as exc:  # noqa: BLE001
            return T5bResult(
                signal_id=signal_id,
                confidence=0,
                counter_examples=[],
                cross_evidence=False,
                final_decision="REJECTED",
                reasoning=f"JSON 파싱 오류: {exc}",
            )

    # ------------------------------------------------------------------
    # Mock 검증
    # ------------------------------------------------------------------

    def _mock_verify(self, signal: dict) -> T5bResult:
        """파일럿 3개 아이디어에 대한 사전 정의 결과 반환.

        signal에서 ideaTitle 키로 MOCK_RESULTS 조회.
        매칭 없으면 REVIEW(confidence=60) 기본 반환.
        """
        idea_title = signal.get("ideaTitle", "")
        signal_id = signal.get("signal_id", idea_title)

        # 부분 문자열 매칭 (키가 ideaTitle의 일부이거나 그 역)
        for key, result in _MOCK_RESULTS.items():
            if key in idea_title or idea_title in key:
                # signal_id를 실제 입력 값으로 교체
                return T5bResult(
                    signal_id=signal_id,
                    confidence=result.confidence,
                    counter_examples=list(result.counter_examples),
                    cross_evidence=result.cross_evidence,
                    final_decision=result.final_decision,
                    reasoning=result.reasoning,
                )

        # 기본 fallback
        return T5bResult(
            signal_id=signal_id,
            confidence=60,
            counter_examples=[],
            cross_evidence=False,
            final_decision="REVIEW",
            reasoning="Mock 매칭 없음 — 수동 검토 필요.",
        )


# ---------------------------------------------------------------------------
# __main__ — mock_mode=True로 파일럿 3개 아이디어 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    verifier = T5bDoctrinal(mock_mode=True)

    pilot_signals = [
        {
            "signal_id": "SIG-001",
            "ideaTitle": "게임사 R&D",
            "lawArticle": "조세특례제한법 제10조",
        },
        {
            "signal_id": "SIG-002",
            "ideaTitle": "통합투자",
            "lawArticle": "조세특례제한법 제24조",
        },
        {
            "signal_id": "SIG-003",
            "ideaTitle": "장애인고용부담금",
            "lawArticle": "법인세법 제19조",
        },
    ]

    print("=" * 70)
    print("T5b Doctrinal Verifier -- 파일럿 3개 아이디어 법리 검증 (mock)")
    print("=" * 70)

    for sig in pilot_signals:
        result = verifier.verify(sig, citation_metadata=[])
        decision_marker = {
            "ADOPTED":  "[ADOPTED  OK]",
            "REVIEW":   "[REVIEW    ?]",
            "REJECTED": "[REJECTED NG]",
        }.get(result.final_decision, f"[{result.final_decision}]")

        print(f"\n{decision_marker} {sig['ideaTitle']}  (signal_id={result.signal_id})")
        print(f"  법령        : {sig['lawArticle']}")
        print(f"  confidence  : {result.confidence}/100")
        print(f"  crossEvidence: {result.cross_evidence}")
        if result.counter_examples:
            for ce in result.counter_examples:
                print(f"  반례        : {ce}")
        print(f"  reasoning   : {result.reasoning}")
        print(f"  checked_by  : {result.checked_by}")

    print("\n" + "=" * 70)
    print("완료")
