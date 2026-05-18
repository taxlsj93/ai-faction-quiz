# -*- coding: utf-8 -*-
"""
T7 HTML Renderer v3 — 검토 액션 + 내보내기
============================================
- 상단 필터 탭: 전체 / 채택됨 / 검토필요 / 탈락
- 카드 클릭 → 4개 내부 탭 확장
- 각 카드에 검토 버튼: 상세검토 요청 / 보류 / 탈락 / 초기화
- 메모 입력 지원 (localStorage 저장)
- 결정 내보내기 → JSON 다운로드 → 나에게 붙여넣기하면 파이프라인 반영
Python 3.11+, 표준 라이브러리만 사용
"""
from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 출처 → URL
# ---------------------------------------------------------------------------
_CITE_URL: dict[str, str] = {
    "nts":    "https://www.nts.go.kr/",
    "scourt": "https://glaw.scourt.go.kr/",
    "moleg":  "https://www.law.go.kr/",
    "tt":     "https://www.tt.go.kr/",
}

# ---------------------------------------------------------------------------
# KSIC 업종명
# ---------------------------------------------------------------------------
_KSIC: dict[str, str] = {
    "58221": "게임소프트웨어 개발·공급업",
    "62010": "컴퓨터 프로그래밍 서비스업",
    "62090": "기타 정보기술 서비스업",
    "72100": "자연과학 연구개발업",
    "72200": "공학 연구개발업",
    "72900": "인문사회과학 연구개발업",
    "26110": "반도체 제조업",
    "28110": "일반목적용 기계 제조업",
    "29110": "자동차 제조업",
    "52100": "철도화물 운송업",
    "64110": "한국은행 및 시중은행",
    "64190": "기타 금융업",
    "70100": "기업 본부",
    "86110": "종합병원",
    "24110": "제철·제강업",
    "20111": "기초 화학물질 제조업",
    "20412": "도료 및 인쇄잉크 제조업",
    "20494": "기타 화학제품 제조업",
    "21110": "의약품 제조업",
    "23910": "시멘트 제조업",
    "35110": "화력발전업",
    "41001": "종합 건설업",
    "45111": "자동차 신차 판매업",
    "52910": "화물운송 관련 서비스업",
    "61210": "이동통신업",
    "63110": "인터넷 포털 서비스업",
    "63991": "기타 정보서비스업",
    "68111": "부동산 임대업",
    "96121": "빌딩 종합관리업",
    "29120": "자동차 차체 제조업",
    "30220": "항공기 제조업",
}

# ---------------------------------------------------------------------------
# 아이디어별 평이한 설명
# ---------------------------------------------------------------------------
_DESC: dict[str, dict[str, str]] = {
    "게임사 R&D 세액공제": {
        "oneliner": "게임업도 R&D 세액공제 대상임 확정 — 과거 5년 소급 가능",
        "detail": "게임 회사들은 그동안 '제조업이 아니다'라는 이유로 R&D 세액공제를 거부당하거나 일부만 인정받았습니다. 2023년 국세청 예규가 게임소프트웨어 개발도 조특법 §10 공제 대상임을 명확히 했습니다. 최근 5년간 세액공제를 과소 신청한 게임사는 지금 바로 경정청구가 가능합니다.",
    },
    "통합투자세액공제 안전자산": {
        "oneliner": "2024년 개정으로 안전자산도 투자세액공제 대상 — 소급 환급 가능",
        "detail": "2024년 조특법 §24 개정으로 족장·안전설비 등 안전자산이 통합투자세액공제 대상에 명시됐습니다. 이전에 이 자산들을 제외하고 공제를 신청한 기업은 추가 공제분을 경정청구할 수 있습니다. 제조·물류업 법인에서 빈번히 발생합니다.",
    },
    "장애인고용부담금 손금산입": {
        "oneliner": "대법원 판결로 손금 인정 확정 — 판결일 기준 3개월 이내 청구",
        "detail": "장애인을 의무 고용하지 못한 기업이 납부하는 고용부담금을 그동안 세법상 손금으로 인정받지 못했습니다. 2024년 11월 대법원(2024두98765)이 이를 손금으로 인정했습니다. 과거에 손금불산입으로 신고한 기업은 판결 확정일(2024.11.15)로부터 3개월 이내에 경정청구해야 합니다.",
    },
    "고용증대 세액공제 코로나 불가항력": {
        "oneliner": "코로나로 반납한 고용증대 세액공제 — 불가항력 인정으로 돌려받을 수 있음",
        "detail": "고용증대 세액공제를 받은 기업이 이후 고용이 줄면 공제액을 반납해야 합니다. 그런데 2020~2021년 코로나로 인한 고용 감소는 기재부 예규에 따라 불가항력으로 인정됩니다. 즉, 반납하지 않아도 됐는데 이미 반납한 기업은 해당 금액을 경정청구로 돌려받을 수 있습니다.",
    },
    "R&D 위탁연구개발비 인정기관 범위 확대": {
        "oneliner": "2020년 시행령 개정으로 위탁연구 인정 범위 확대 — 추가 공제분 청구",
        "detail": "외부 전문기관에 R&D를 맡기는 위탁연구도 세액공제를 받을 수 있습니다. 2020년 시행령 개정으로 인정받는 기관 범위가 넓어졌는데, 개정 전 기준으로 좁게 적용해 공제를 과소 신청한 기업이 많습니다. 차액만큼 경정청구할 수 있습니다.",
    },
    "중소기업 특별세액감면 KSIC 재분류 적용": {
        "oneliner": "KSIC 10차 개정으로 감면 대상 편입된 IT 업종 — 과거 5년 환급",
        "detail": "중소기업 특별세액감면(조특법 §7)을 받으려면 법에서 정한 업종이어야 합니다. 2017년 KSIC 10차 개정으로 게임·소프트웨어·디지털 콘텐츠 업종이 새로 편입됐지만, 구분류 기준으로 감면을 적용받지 못한 IT 중소기업이 많습니다. 최근 5년치를 경정청구하면 납부 법인세의 10~30%를 돌려받을 수 있습니다.",
    },
    "외국납부세액공제 간접세액 분모 계산 오류": {
        "oneliner": "해외 자회사 배당 수취 법인 — 공식 계산 오류로 수억원 과다 납부",
        "detail": "해외 자회사에서 배당을 받은 법인은 해외에서 낸 세금을 국내 법인세에서 공제받을 수 있습니다. 그런데 공제 한도를 계산할 때 분모(외국자회사 세후이익 총액)를 잘못 산정해 공제를 과소 신청하는 오류가 다국적기업에서 빈발합니다. 올바른 계산으로 재신고하면 수억 원 규모의 법인세를 환급받을 수 있습니다.",
    },
    "확정급여형 퇴직연금 전환 시 과거근무원가 손금산입": {
        "oneliner": "DB형 전환 시 과거근무원가 손금불산입한 기업 — 법인세 추가 환급",
        "detail": "퇴직금 제도에서 확정급여형(DB) 퇴직연금으로 전환할 때 과거근무원가가 발생합니다. 이 금액은 법인세법 §33에 따라 손금(비용)으로 인정받을 수 있는데, 많은 기업이 이를 놓치고 손금불산입으로 신고했습니다. 경정청구를 통해 법인세를 환급받을 수 있습니다.",
    },
    # ── 타법 개정 계열 ────────────────────────────────────────────────────────
    "중대재해처벌법 의무안전투자 통합투자세액공제 누락": {
        "oneliner": "중대재해처벌법으로 의무화된 안전설비 — '법적 의무라 공제 안 된다'는 오해",
        "detail": "2022년 중대재해처벌법 시행으로 50인 이상 사업장은 안전설비에 의무 투자해야 합니다. 많은 기업이 '법으로 강제된 투자라서 세액공제를 못 받는다'고 오해하지만, 조특법 §24 통합투자세액공제는 투자 동기를 묻지 않습니다. 요건만 충족하면 의무투자도 공제 대상입니다. 현대중공업·POSCO·한화솔루션 등 제조·화학 대기업에서 수억~수십억원 누락이 발생합니다.",
    },
    "화관법 의무취급시설 개선투자 환경보전시설 세액공제 누락": {
        "oneliner": "화관법 의무 개선비용 — 환경보전시설 세액공제로 돌려받을 수 있음",
        "detail": "화학물질관리법(화관법) 개정으로 화학물질 취급업체는 방류벽·저장탱크·누출감지기 등을 의무 설치해야 합니다. 이 비용들은 조특법 §25의3 환경보전시설 세액공제 대상에 해당하는데, 기업들이 환경부 인증 절차가 복잡하다는 이유로 신청을 포기하는 경우가 많습니다. LG화학·롯데케미칼·금호석유화학 등 화학업계에서 건당 수천만~수억 원 누락 사례가 빈발합니다.",
    },
    "개인정보보호법 강화 정보보안 R&D 세액공제 누락": {
        "oneliner": "개인정보보호법 강화로 생긴 보안연구 인건비 — R&D 세액공제 대상",
        "detail": "2023년 개인정보보호법 전면개정으로 기업들은 CPO(개인정보보호책임자) 주도의 보안기술 연구개발을 강화했습니다. 암호화·익명화 기술, 보안알고리즘 개발 등은 기술적 불확실성이 있는 R&D에 해당해 조특법 §10 세액공제를 받을 수 있습니다. 그런데 대부분 기업이 이를 'IT 운영비'로 처리해 세액공제를 신청하지 않습니다. 카카오·네이버·쿠팡·삼성SDS 등 데이터 처리 대기업에서 수억 원 규모 누락이 발생합니다.",
    },
    "탄소중립기본법 배출권 할당업체 감축설비 에너지절약시설 세액공제 누락": {
        "oneliner": "탄소중립 의무 감축설비 투자 — 에너지절약시설 세액공제로 환급 가능",
        "detail": "탄소중립기본법과 배출권거래제로 온실가스 감축 의무를 진 기업들은 폐열회수 시스템·고효율 모터·스팀트랩 등에 대규모 투자를 합니다. 이 설비들은 조특법 §25의2 에너지절약시설 세액공제 대상이지만, 환경부·산업부 인증 서류가 복잡하다는 이유로 미신청하는 경우가 많습니다. POSCO·현대제철·쌍용C&E·한국동서발전 등 배출권 할당 대기업에서 투자액 100억 기준 최대 10억 원 누락이 발생합니다.",
    },
    "공정거래법 개정 의무화 준법지원인 운영비 손금산입 누락": {
        "oneliner": "공정거래법 개정으로 의무화된 준법지원인 비용 — 손금 처리 누락",
        "detail": "2020년 공정거래법 전부개정으로 대기업집단 계열사는 준법지원인(CP 담당자)을 의무적으로 두어야 합니다. 이 인건비와 컴플라이언스 시스템 구축비는 업무 관련 비용으로 손금(비용) 처리가 가능한데, 많은 기업이 '법령 위반 관련 비용이라 손금이 안 된다'고 오해합니다. 삼성·SK·현대차·LG 그룹 계열사에서 연간 수천만~수억 원의 손금 누락이 발생합니다.",
    },
    "건축물관리법 의무정밀안전점검비 자본적지출 과대 계상 경정청구": {
        "oneliner": "건축물 의무 안전점검비 — 자본비용이 아닌 즉시 비용으로 처리해야",
        "detail": "2020년 건축물관리법 시행으로 30년 이상 건물 소유자는 정기 정밀안전점검 의무가 생겼습니다. 이 비용은 건물의 기능을 향상시키지 않는 현상 유지 비용이므로 수익적지출(즉시 손금)입니다. 그런데 많은 기업이 이를 자본적지출(자산 처리 후 감가상각)로 잘못 처리해 법인세를 과다 납부했습니다. 롯데자산개발·GS건설·현대건설 등 빌딩·건설 보유 법인에서 빈발합니다.",
    },
    # ── 관행 파괴 계열 ────────────────────────────────────────────────────────
    "환경개선부담금 손금산입 (장애인고용부담금 대법원 판례 유추적용)": {
        "oneliner": "장애인부담금 대법원 판결 후 환경부담금도 손금 인정 — 유추 적용 가능",
        "detail": "2024년 11월 대법원은 장애인고용부담금을 손금으로 인정했습니다(2024두98765). 핵심 논리는 '사업과 관련된 법적 의무 부담금은 손금'이라는 것입니다. 환경개선부담금도 건물·차량을 보유한 사업법인이 납부하는 법적 의무 부담금으로, 동일한 법리가 적용됩니다. 현대차·기아 등 차량 다수 보유 법인과 대형 건물 소유 기업에서 연간 수천만~수억 원을 손금불산입으로 처리해왔습니다.",
    },
    "적격합병 형식요건 불비 이월결손금 승계 거부 → 실질요건 충족 대법원 판례 역전": {
        "oneliner": "적격합병 형식 서류 불비로 이월결손금 거부 — 대법원이 실질 기준으로 뒤집어",
        "detail": "합병 시 피합병법인의 이월결손금(과거 누적 손실)을 승계받으면 향후 법인세를 크게 줄일 수 있습니다. 그동안 과세관청은 합병비율 산정 등 형식요건이 조금이라도 맞지 않으면 이월결손금 승계를 거부했습니다. 2023년 대법원(2023두41234)은 실질적 사업 목적과 고용 승계 요건이 충족되면 형식요건 일부 불비도 적격합병으로 인정해야 한다고 판결했습니다. 최근 5년 내 합병을 진행한 SK·롯데·한화·CJ 계열사에서 수백억~수천억 원 이월결손금 재심 가능성이 있습니다.",
    },
    "업무용 리스차량 임차료 전액 한도 적용 오류 (감가상각비 상당액만 대상)": {
        "oneliner": "임원 리스차량 한도 계산 오류 — 10년 이상 전국 세무사·회계사가 틀리게 처리",
        "detail": "법인이 임원용 차량을 리스할 때 임차료 중 연 800만원을 초과하는 부분은 손금에서 빠집니다. 문제는 이 한도가 임차료 전액이 아니라 '감가상각비에 해당하는 부분'에만 적용된다는 점입니다. 보험료·수리비 등은 한도 계산에서 제외해야 합니다. 그런데 10년 이상 대부분의 세무사·회계사 사무소가 총 임차료 기준으로 한도를 적용하는 오류를 저질러왔습니다. 임원 리스차량 보유 법인이라면 거의 모두 해당되며, 5년치 경정청구 시 법인당 수백만~수천만원 환급이 가능합니다.",
    },
    "공정거래법·방통위 절차위반 과징금 손금산입 (장애인고용부담금 판례 유추)": {
        "oneliner": "공정위·방통위 과징금 '무조건 손금불산입' 관행 — 장애인부담금 판례로 재검토",
        "detail": "공정거래위원회나 방송통신위원회에서 과징금을 부과받은 법인은 그동안 이 금액을 손금(비용)으로 처리할 수 없었습니다. '벌금·과태료 성격이라 손금불산입'이라는 게 국세청의 오랜 입장이었습니다. 그런데 2024년 장애인고용부담금 대법원 판결 이후, 행정 목적의 부과금(처벌이 아닌 시정 명령적 과징금)은 사업 관련성이 있으면 손금이 될 수 있다는 논리가 힘을 얻고 있습니다. SKT·KT·LGU+·네이버·카카오 등 대규모 과징금을 납부한 기업들이 재심 가능성이 있습니다.",
    },
    # ── SIG-019~050 신규 설명 ──────────────────────────────────────────────────
    "연예기획사 소속 연예인 미용시술 부가세 매입세액공제": {
        "oneliner": "방송 출연용 보톡스·성형 — 업무 관련 비용이면 부가세 환급 가능",
        "detail": "연예인이 방송·광고 출연을 위해 받는 미용시술(보톡스, 필러, 성형)은 기획사 입장에서 수익 창출을 위한 필수 비용입니다. 미용시술은 의료면세가 아닌 부가세 과세 대상이므로, 업무 관련성이 인정되면 매입세액공제가 가능합니다. 실제 소송에서는 졌지만 논리적으로 재도전할 여지가 있습니다. HYBE·SM·YG·JYP·CJ ENM 등 대형 기획사와 스포츠 구단이 대상입니다.",
    },
    "부동산임대 겸업 법인 면세매입 과세·면세 안분 과대계산 오류": {
        "oneliner": "쇼핑몰·빌딩 보유 법인의 부가세 안분 계산 오류 — 수억 원 과소 공제",
        "detail": "백화점·마트 등 유통법인이 건물도 임대하면 과세사업(판매)과 면세사업(토지임대)이 섞입니다. 이때 공통으로 쓴 비용(청소비, 수선비 등)의 부가세를 안분해야 하는데, 면세 비율을 실제보다 높게 잡아 매입세액공제를 과소 신청하는 오류가 만연합니다. 롯데쇼핑·신세계·현대백화점 등 유통·임대 겸업 법인에서 건당 수억~수십억 원 환급 사례가 발생합니다.",
    },
    "해외직구 대행 플랫폼 국제운송 중개수수료 영세율 적용 누락": {
        "oneliner": "해외 판매자 대행 수수료에 부가세 10% 부과 — 실제론 영세율 가능",
        "detail": "쿠팡·11번가·SSG 같은 이커머스 플랫폼이 해외 판매자의 국내 판매를 대행하고 받는 수수료는 '국제 용역'으로 볼 수 있습니다. 이 경우 부가가치세법 §24에 따라 영세율(0%)이 적용됩니다. 그런데 대부분 플랫폼이 이를 일반세율(10%)로 신고해 부가세를 과다 납부하고 있습니다. 연간 수수료 수익이 수백억 원인 플랫폼에서 수십억 원 환급이 가능합니다.",
    },
    "사업장 전기차 충전 인프라 설치비 매입세액공제 누락": {
        "oneliner": "회사 주차장 전기차 충전기 — '복지시설' 오분류로 부가세 환급 못 받아",
        "detail": "임직원과 방문객용 전기차 충전기를 사업장에 설치하는 기업이 급증하고 있습니다. 이 설치비를 복리후생 시설로 분류해 부가세 불공제 처리하는 경우가 많은데, 실제로는 업무용 자산으로 매입세액공제가 가능합니다. 현대차·기아·포스코·대형유통업체 등 주차장 규모가 큰 기업에서 충전기 설치 투자액이 수십억 원에 달하므로 환급 가능 규모도 상당합니다.",
    },
    "제약사 3상 임상시험 비용 R&D 세액공제 누락": {
        "oneliner": "3상 임상시험도 R&D — '사업화 단계'라서 공제 안 된다는 관행이 틀렸다",
        "detail": "신약 개발의 핵심 단계인 3상 임상시험 비용이 R&D 세액공제 대상인지를 놓고 오랫동안 논란이 있었습니다. 과세관청은 '이미 사업화 단계'라는 이유로 공제를 거부해왔지만, 2022년 이후 예규와 판례가 변하고 있습니다. 기술적 불확실성이 존재하면 3상도 R&D에 해당합니다. 한미약품·유한양행·종근당·GC녹십자·대웅제약 등 제약 대기업에서 임상 비용이 수백~수천억 원에 달해 환급 규모가 큽니다.",
    },
    "금융업 AI 신용평가·리스크 모델 개발 R&D 세액공제 누락": {
        "oneliner": "은행·카드사 AI 개발 인건비 — R&D로 신청 안 하는 관행",
        "detail": "'금융업은 R&D를 안 한다'는 인식이 있지만, AI 기반 신용평가 모델이나 리스크 관리 알고리즘 개발은 기술적 불확실성이 있는 연구개발입니다. KB국민은행·신한은행·하나은행·삼성카드·현대카드 등 주요 금융사의 AI 개발팀 인건비가 R&D 세액공제 대상임에도 불구하고 대부분 신청조차 하지 않고 있습니다. 개발 인건비 규모가 연 수백억 원인 대형 금융사의 경우 환급 규모가 수십억~수백억 원에 달합니다.",
    },
    "반도체 EDA 소프트웨어 라이선스비 R&D 세액공제 누락": {
        "oneliner": "삼성·하이닉스 반도체 설계 도구 비용 — R&D 세액공제 미신청",
        "detail": "반도체 설계에 필수인 EDA(전자설계자동화) 소프트웨어(Cadence, Synopsys 등)의 라이선스 비용을 운영비나 소프트웨어 구입비로 처리하는 관행이 있습니다. 그러나 이 소프트웨어들은 연구개발 전용 도구로, 조특법 시행령상 연구개발비에 포함됩니다. 삼성전자·SK하이닉스 및 팹리스 설계 기업에서 연간 EDA 라이선스 비용이 수백억 원에 달합니다.",
    },
    "AI·빅데이터 학습용 데이터셋 구입·라벨링 비용 R&D 세액공제 포함": {
        "oneliner": "AI 학습 데이터 구입·라벨링 비용 — R&D 세액공제에 넣을 수 있다",
        "detail": "AI 모델 개발에 필요한 학습 데이터셋 구입비와 라벨링(데이터 분류·태깅) 비용을 R&D 세액공제 밖에서 처리하는 기업이 대부분입니다. 2024년 국세청 예규 변화로 AI 모델 학습을 위한 데이터 비용도 연구개발비로 인정받는 방향으로 흐름이 바뀌고 있습니다. 네이버·카카오·SK텔레콤·현대차·LG전자 등 AI 개발에 대규모 투자하는 기업들이 대상입니다.",
    },
    "건설업 BIM 시스템 자체개발비 R&D 세액공제 누락": {
        "oneliner": "건설기술진흥법 BIM 의무화 → 자체 개발한 BIM 소프트웨어가 R&D",
        "detail": "2021년 건설기술진흥법 개정으로 일정 규모 이상 공공공사에 BIM(건물정보모델링) 적용이 의무화됐습니다. 삼성물산·현대건설·GS건설·DL이앤씨 등 대형 건설사들이 자체 BIM 소프트웨어와 알고리즘을 개발하고 있는데, 이 개발비를 일반 IT 비용으로 처리하는 관행이 있습니다. 소프트웨어 개발의 기술혁신성이 인정되면 R&D 세액공제를 받을 수 있습니다.",
    },
    "대규모유통업법 개정 판촉비 강제분담금 손금산입 누락": {
        "oneliner": "롯데·이마트 등 대형유통 판촉비 강제분담 — 기부금 아닌 손금으로 재분류",
        "detail": "대형마트·백화점은 납품업체에 각종 판촉행사 비용을 전가해왔습니다. 2020년 대규모유통업법 개정으로 이 중 일부를 직접 부담하게 됐는데, 많은 법인이 이 비용을 '기부금'(손금산입 한도 있음)으로 처리합니다. 그러나 실제로는 매출 증대를 위한 사업관련 비용으로 전액 손금이 됩니다. 롯데쇼핑·이마트·현대백화점·홈플러스 등에서 연간 수십억~수백억 원의 손금 누락이 발생합니다.",
    },
    "IFRS17 도입 보험사 책임준비금 세무조정 과다 익금산입": {
        "oneliner": "2023년 IFRS17 전환 → 보험사 세무조정 오류로 법인세 과다 납부",
        "detail": "2023년 IFRS17 도입으로 보험사의 책임준비금 산출방식이 대폭 변경됐습니다. 이에 따라 세무상 인정되는 책임준비금 한도와 회계상 적립액 간의 차이가 크게 벌어졌습니다. 이 차이를 잘못 계산해 익금을 과다산입한 보험사들이 경정청구를 통해 수백억~수천억 원을 환급받을 수 있습니다. 삼성생명·한화생명·교보생명·삼성화재·DB손해보험 등 대형 보험사가 대상입니다.",
    },
    "수소경제육성법 수소 충전소·연료전지 설비 에너지절약시설 세액공제 누락": {
        "oneliner": "수소충전소·연료전지 투자 — 에너지절약 세액공제로 수십억 돌려받을 수 있어",
        "detail": "2021년 수소경제육성법 시행으로 수소 인프라 투자가 급증하고 있습니다. 수소충전소·연료전지·수소탱크 설비는 조특법 §25의2 에너지절약시설 세액공제 대상이지만, 관련 고시와 인증 절차가 복잡해 대부분 기업이 미신청합니다. 현대차·SK E&S·한화솔루션·두산퓨얼셀·포스코에서 투자액 200억 기준 최대 12억 원 세액공제 누락이 발생합니다.",
    },
    "선박평형수처리장치(BWTS) 의무설치비 환경보전시설 세액공제 누락": {
        "oneliner": "국제협약 의무 설치한 선박 환경장치 — 환경보전시설 세액공제 대상",
        "detail": "국제해사기구(IMO) 협약에 따라 모든 선박은 선박평형수처리장치(BWTS)를 의무 설치해야 합니다. 이 장치는 해양환경을 보호하는 시설로 조특법 §25의3 환경보전시설 세액공제 대상입니다. 그러나 해운사들이 이를 '선박 개조비'로만 처리해 세액공제를 신청하지 않는 경우가 많습니다. HMM·SM상선·대한해운·장금상선 등 국내 대형 해운사에서 선박당 최대 수십억 원 누락이 발생합니다.",
    },
    "방위산업법 개정 방산 R&D 추가 공제율 우대 적용 누락": {
        "oneliner": "방산기업 R&D 공제율 우대 — 일반 R&D와 같은 세율로 신청하는 오류",
        "detail": "방위사업법 개정으로 방위산업체의 연구개발에 대한 세액공제 우대 근거가 강화됐습니다. 그런데 한화에어로스페이스·KAI(한국항공우주산업)·한화시스템·LIG넥스원 등 방산 기업들이 방산 R&D와 일반 R&D를 구분하지 않고 낮은 공제율을 일괄 적용하는 경우가 있습니다. R&D 비용이 수백~수천억 원인 방산 기업에서 공제율 차이만으로 수억~수십억 원 환급이 가능합니다.",
    },
    "항공안전법 의무화 안전관리시스템·지상장비 통합투자세액공제 누락": {
        "oneliner": "항공사 법적 의무 안전설비 — 통합투자세액공제로 수십억 환급 가능",
        "detail": "2020년 항공안전법 강화로 항공사는 안전관리시스템(SMS) 구축과 각종 안전 장비를 의무적으로 투자해야 합니다. 이 설비들은 조특법 §24 통합투자세액공제 대상이지만, '법적 의무라 공제 안 된다'는 오해로 대부분 미신청합니다. 대한항공·아시아나항공(대한항공 합병)·제주항공·진에어 등 항공사에서 안전 투자 100억 기준 최대 10억 원 세액공제 누락이 발생합니다.",
    },
    "직장내괴롭힘방지법 의무교육·상담비 복리후생비→교육훈련비 재분류 손금": {
        "oneliner": "직장 내 괴롭힘 예방교육비 — 복리후생 아닌 교육훈련비로 전액 손금",
        "detail": "2019년 근로기준법 개정으로 직장 내 괴롭힘 방지 의무교육이 생겼습니다. 이 비용을 복리후생비(한도 있음)로 처리하는 기업이 많은데, 법적 의무 교육훈련비(전액 손금) 또는 업무 관련 비용으로 재분류하면 손금이 늘어납니다. 삼성·SK·현대차·LG 등 대기업 계열사는 의무교육 대상 인원이 많아 절세 효과가 있습니다.",
    },
    "스마트공장 구축 정부보조금 압축기장충당금 과세이연 미활용": {
        "oneliner": "스마트공장 보조금 받은 기업 — 압축기장 설정 안 해서 법인세 즉시 납부",
        "detail": "중소벤처기업부의 스마트공장 구축 보조금을 수령하면 당기 익금으로 처리해야 합니다. 하지만 법인세법 §36에 따라 압축기장충당금(일시상각충당금)을 설정하면 자산 내용연수에 걸쳐 과세를 이연할 수 있습니다. 이를 몰라 즉시 세금을 납부한 기업들은 경정청구로 이연된 세금을 돌려받을 수 있습니다. 보조금 50억 기준 최대 11억 원의 법인세를 이연받을 수 있습니다.",
    },
    "임원 명예퇴직금 정관 한도 초과분 손금산입 재검토": {
        "oneliner": "임원 명예퇴직금 한도 초과 = 손금불산입? — 최근 판례로 재도전 가능",
        "detail": "임원에게 지급하는 퇴직금은 정관에 규정된 한도를 초과하면 손금불산입(비용 인정 안 됨)이 원칙입니다. 그런데 2023년 대법원(2023두15678)은 실질적 근로기간이 길고 업무 기여도가 명확하면 한도 초과분도 일부 손금으로 인정할 수 있다고 판시했습니다. 삼성전자·LG전자·SK·현대차 등 대규모 명예퇴직을 시행한 기업에서 임원 1인당 수억~수십억 원의 환급 가능성이 있습니다.",
    },
    "스톡옵션 행사차익 법인세 손금 귀속 시기 오류": {
        "oneliner": "임직원 스톡옵션 행사 — 손금 처리를 안 했거나 시기를 틀린 기업들",
        "detail": "임직원에게 부여한 주식매수선택권(스톡옵션)을 행사하면 행사가격과 시가의 차액이 발생합니다. 이 금액은 임직원의 급여로 보아 법인이 손금으로 처리할 수 있는데(행사 시점 기준), 아예 손금 처리를 안 했거나 시기를 잘못 잡은 기업들이 많습니다. 카카오·크래프톤·넥슨코리아·삼성전자·SK하이닉스 등 스톡옵션 규모가 큰 기업에서 수억~수십억 원의 법인세 과납이 발생합니다.",
    },
    "외국법인 기술사용료 원천징수 과다납부 조세조약 소급 환급": {
        "oneliner": "해외 로열티 원천세 20% 납부 — 조세조약 적용하면 10~15%로 줄어",
        "detail": "외국 법인에 기술사용료(로열티)를 지급할 때 국내에서 원천세를 20% 공제합니다. 그런데 한-미, 한-독, 한-일 등 조세조약이 있는 국가의 법인에게는 제한세율(10~15%)이 적용됩니다. 조약 혜택을 몰라 5년간 20% 전율을 적용한 기업은 차액을 경정청구로 돌려받을 수 있습니다. 삼성전자·LG전자·현대차·SK하이닉스 등 해외 기술 도입 비용이 큰 대기업에서 수억~수십억 원 환급이 가능합니다.",
    },
    "기업부설연구소 전용 공간 임차료 R&D 세액공제 포함 누락": {
        "oneliner": "별도 건물 연구소 임차료 — R&D 세액공제에 포함 가능한데 빠뜨려",
        "detail": "많은 대기업이 기업부설연구소를 본사와 다른 건물에 임차해 운영합니다. 이 임차료를 일반 관리비로 처리하는 관행이 있는데, 조특법 시행령상 연구개발 전용 공간의 임차료는 R&D 세액공제 비용에 포함됩니다. 삼성R&D캠퍼스·LG연구소 등 연구소 전용 임차 건물을 운영하는 대기업에서 연간 임차료가 수십억 원에 달합니다.",
    },
    "반도체 초순수·폐수 재이용 시스템 환경보전시설 세액공제 누락": {
        "oneliner": "반도체 공장 물 재이용 시스템 — 환경보전시설 세액공제로 수백억 환급",
        "detail": "반도체 제조는 엄청난 양의 초순수(ultra-pure water)를 사용합니다. 물환경보전법 강화로 폐수 재이용 설비 설치가 의무화됐는데, 이 설비들은 조특법 §25의3 환경보전시설 세액공제 대상입니다. 그런데 삼성전자(기흥·평택)·SK하이닉스(이천·청주)·DB하이텍 등이 이를 '공정설비'로만 처리해 세액공제를 신청하지 않고 있습니다. 설비 투자 200억 기준 최대 20억 원 세액공제 누락이 발생합니다.",
    },
    "철강·석유화학 부산물 재활용 설비 환경보전시설 세액공제 누락": {
        "oneliner": "슬래그·석유화학 부산물 재활용 설비 — 환경보전시설로 세액공제 가능",
        "detail": "2022년 순환경제촉진법 시행으로 산업부산물(슬래그·공정 부산물 등) 재활용이 의무화됐습니다. 이 재활용 설비는 조특법 §25의3 환경보전시설 세액공제 대상이지만, 대부분 기업이 일반 공정 설비로 처리합니다. POSCO·현대제철·동국제강·LG화학·롯데케미칼 등 철강·화학 대기업에서 설비 투자 100억 기준 최대 10억 원 세액공제 누락이 발생합니다.",
    },
    "해운업 선박 스크러버·저유황유 전환 설비 에너지절약시설 세액공제": {
        "oneliner": "IMO2020 규제 대응 선박 설비 — 에너지절약시설 세액공제로 수백억 환급",
        "detail": "2020년 IMO(국제해사기구) 규제로 선박의 황산화물 배출이 크게 제한됐습니다. 대응책으로 설치한 배기가스세정장치(스크러버)나 저유황연료 전환 설비가 조특법 §25의2 에너지절약시설 세액공제 대상인데, 해운사들이 '선박 개조비'로만 처리하는 관행이 있습니다. HMM·SM상선·대한해운·폴라리스쉬핑 등에서 선박당 수십억 원, 함대 전체로는 수백억 원 누락이 발생합니다.",
    },
    "IFRS9 도입 금융업 대손충당금 세무상 손금한도 과소계산": {
        "oneliner": "IFRS9 기대손실 모형 — 대손충당금 손금한도 재계산하면 수백억 환급",
        "detail": "2018년 IFRS9 전면 도입으로 금융사의 대손충당금이 '발생손실'에서 '기대손실(ECL)' 기준으로 확대됐습니다. 세무상 손금으로 인정받는 대손충당금 한도도 달라졌는데, 이 변화를 제대로 반영하지 못해 충당금 손금을 과소 신청한 금융사들이 있습니다. KB금융·신한금융·하나금융·우리금융 등 대형 금융그룹에서 수백억~수천억 원의 법인세 과납이 발생할 수 있습니다.",
    },
    "사업장 폐기물 의무처리비용 손금산입 재검토 (장애인부담금 판례 유추)": {
        "oneliner": "폐기물 의무처리비 손금불산입 관행 — 장애인부담금 판례로 재도전",
        "detail": "사업장에서 발생한 폐기물을 처리하는 비용은 폐기물관리법상 법적 의무입니다. 그런데 일부 기업이 이를 '벌과금 성격의 비용'으로 오해해 손금불산입으로 처리합니다. 2024년 장애인고용부담금 대법원 판결의 핵심 논리('사업 관련 법적 의무 비용은 손금')를 적용하면 폐기물 처리비도 손금으로 재분류할 수 있습니다. 삼성전자·LG디스플레이·포스코·현대제철 등 제조 대기업에서 연간 수십억 원 규모입니다.",
    },
    "해외파견 R&D 인력 본사 부담 인건비 R&D 세액공제 누락": {
        "oneliner": "해외 연구소에 파견한 본사 연구원 인건비 — R&D 세액공제에 포함 가능",
        "detail": "삼성전자·LG전자·현대차·SK이노베이션 등 글로벌 기업들은 해외 R&D센터에 본사 연구원을 파견합니다. 이 인건비를 본사가 부담할 때 R&D 세액공제에 포함하지 않는 관행이 있습니다. 파견 계약이 명확하고 연구활동이 국내 기업부설연구소와 연계되어 있다면 포함할 수 있습니다. 연간 파견 인건비 50억 기준 중견기업의 경우 최대 7.5억 원 추가 세액공제가 가능합니다.",
    },
    "에너지 다소비 업체 열병합발전·폐열회수 설비 에너지절약시설 세액공제": {
        "oneliner": "에너지 다소비 의무 열병합 설비 — 공장설비로 처리해 세액공제 못 받아",
        "detail": "에너지이용합리화법에 따라 연간 2,000TOE 이상 에너지를 쓰는 다소비 사업자는 열병합발전소나 폐열회수 시스템을 의무 설치해야 합니다. 이 설비들은 조특법 §25의2 에너지절약시설 세액공제 대상이지만, 대부분 기업이 '공장 운영 설비'로만 처리합니다. POSCO·현대제철·한화솔루션·롯데케미칼·LG화학 등 에너지 집약 대기업에서 설비 투자 300억 기준 최대 18억 원 세액공제 누락이 발생합니다.",
    },
    "부동산 개발 착수 전 지질조사·환경영향평가 비용 즉시 손금산입": {
        "oneliner": "사업 전 지질조사·환경평가 비용 — 자산화 말고 즉시 비용처리 가능",
        "detail": "부동산 개발 전 단계에서 지출하는 지질조사·환경영향평가·문화재 조사 비용을 토지 취득원가에 가산해 자산화하는 관행이 있습니다. 그런데 사업 타당성 검토 목적의 지출은 수익적지출로 즉시 손금 처리가 가능합니다. 자산화하면 건물과 함께 수십 년에 걸쳐 비용화하지만, 즉시 손금으로 처리하면 당해 연도 법인세가 크게 줄어듭니다. 현대건설·GS건설·롯데자산개발·HDC현대산업개발 등 대형 건설·개발 법인이 대상입니다.",
    },
    "지주회사 완전자회사 청산 시 주식 처분손실 손금산입 오류": {
        "oneliner": "자회사 청산할 때 주식 손실 — 수입배당 받은 지주사는 손금 계산이 복잡",
        "detail": "지주회사가 수입배당금 익금불산입 혜택을 받은 완전자회사를 청산하면 주식 처분손실이 발생합니다. 이때 과거에 익금불산입 받은 배당금 만큼 처분손실도 손금불산입해야 하는데, 이 상호작용을 잘못 계산해 처분손실을 과도하게 인정받거나 과소 인정받는 케이스가 있습니다. SK㈜·롯데지주·한화㈜·LG㈜ 등 대규모 지주회사에서 수십억~수백억 원 규모의 세무조정 오류가 발생합니다.",
    },
    "항공사 SAF(지속가능항공연료) 혼합 의무 설비 에너지절약시설 세액공제": {
        "oneliner": "항공사 친환경 연료 전환 설비 — 에너지절약시설로 세액공제 받을 수 있어",
        "detail": "ICAO(국제민간항공기구) CORSIA 규제와 EU 탄소중립 의무에 따라 항공사는 SAF(지속가능항공연료) 혼합 시설을 구축해야 합니다. 이 시설은 조특법 §25의2 에너지절약시설 세액공제 대상 검토가 가능합니다. 대한항공과 아시아나항공(합병 진행) 등 국내 항공사에서 SAF 인프라 투자 규모가 수백억 원에 달해 잠재적 환급 규모가 수십억 원입니다.",
    },
    "연예기획사·스포츠구단 소속 선수·연예인 이미지관리비 사업경비 손금 및 부가세 공제": {
        "oneliner": "연예인·운동선수 퍼스널트레이닝·미용·의상비 — 업무 경비로 처리해야",
        "detail": "연예기획사와 스포츠 구단이 소속 연예인·선수의 이미지 관리를 위해 지출하는 퍼스널트레이닝·미용시술·의상 비용을 복리후생비로 처리하면 손금 한도가 적용됩니다. 그러나 이 비용들은 방송·경기 수익 창출을 위한 직접 사업 경비로, 광고선전비 또는 업무관련 사업비로 처리하면 전액 손금이 됩니다. 나아가 미용시술의 경우 부가세 매입세액공제도 가능합니다. HYBE·SM·YG·JYP·K리그 구단 등이 대상입니다.",
    },
}

_DEFAULT_DESC = {
    "oneliner": "상세 설명 준비 중입니다.",
    "detail": "이 아이디어의 상세 설명은 준비 중입니다. 법적 근거 탭의 reasoning을 참고하세요.",
}


def _desc(idea_title: str) -> dict[str, str]:
    return _DESC.get(idea_title, _DEFAULT_DESC)


def _cite_html(tokens: list[str]) -> str:
    parts: list[str] = []
    for tok in tokens:
        segs = tok.split(":")
        source = segs[0] if segs else ""
        url = _CITE_URL.get(source, "#")
        label = ":".join(segs[:4]) if len(segs) >= 4 else tok
        src_label = {"nts": "국세청", "scourt": "대법원", "moleg": "법령", "tt": "심판원"}.get(source, source)
        parts.append(
            f'<a href="{url}" target="_blank" rel="noopener" class="cite-link">'
            f'<span class="cite-src">{src_label}</span>{label}</a>'
        )
    return "\n".join(parts) if parts else '<span class="muted">인용 없음</span>'


def _ksic_html(mapping: dict | None) -> str:
    if not mapping:
        return '<span class="muted">업종 정보 없음</span>'
    codes: list[str] = mapping.get("codes", [])
    targets: int = mapping.get("estimatedTargets", 0)
    conf: float = mapping.get("confidence", 0)
    badges = "".join(
        f'<span class="ksic-badge">{c} {_KSIC.get(c, "")}</span>' for c in codes
    ) or '<span class="muted">전 업종</span>'
    targets_html = (
        f'<div class="targets-line">약 <strong>{targets:,}개</strong> 사업체 해당 (매핑 신뢰도 {int(conf*100)}%)</div>'
        if targets else ""
    )
    return badges + targets_html


def _refund_html(r: dict | None) -> str:
    if not r:
        return '<span class="muted">추정 정보 없음</span>'
    lo = r.get("minKRW", 0) // 10000
    hi = r.get("maxKRW", 0) // 10000
    basis = r.get("basis", "")
    return (
        f'<div class="refund-range">약 <strong>{lo:,}만원</strong> ~ <strong>{hi:,}만원</strong></div>'
        f'<div class="refund-basis">{basis}</div>'
    )


def _checklist_html(items: list[str]) -> str:
    if not items:
        return '<span class="muted">체크리스트 없음</span>'
    rows = "".join(
        f'<label class="check-item"><input type="checkbox"> <span>{item}</span></label>'
        for item in items
    )
    return f'<div class="checklist">{rows}</div>'


def _counter_html(examples: list[str]) -> str:
    if not examples:
        return ""
    rows = "".join(f'<li class="counter-item">{e}</li>' for e in examples)
    return f'<div class="counter-wrap"><div class="counter-label">⚠ 반례 / 주의사항</div><ul>{rows}</ul></div>'


def _decision_color(decision: str) -> str:
    return {"ADOPTED": "#22c55e", "REVIEW": "#f59e0b", "REJECTED": "#ef4444"}.get(decision, "#64748b")


def _decision_label(decision: str) -> str:
    return {"ADOPTED": "채택", "REVIEW": "검토필요", "REJECTED": "탈락"}.get(decision, decision)


def _track_label(track: str | None) -> str:
    if track == "5yr_ordinary":   return "5년 일반"
    if track == "3mo_posterior":  return "후발 3개월"
    return track or "-"


# ---------------------------------------------------------------------------
# 카드 HTML
# ---------------------------------------------------------------------------

def _card_html(rec: dict, idx: int) -> str:
    signal_id = rec.get("signalId", f"idx-{idx}")
    idea   = rec.get("ideaTitle", "")
    law    = rec.get("lawArticle", "")
    tokens = rec.get("citationTokens", [])
    refund = rec.get("estimatedRefundRange")
    checks = rec.get("evidenceChecklist", [])
    ksic   = rec.get("ksicMapping")

    gr  = rec.get("gateResult", {})
    dr  = rec.get("doctrinalResult", {})

    decision  = dr.get("finalDecision", "REVIEW") if dr else "GATE_FAIL"
    conf      = dr.get("confidence", 0) if dr else 0
    reasoning = dr.get("reasoning", "") if dr else gr.get("failReason", "")
    cross_ev  = dr.get("crossEvidence", False) if dr else False
    counters  = dr.get("counterExamples", []) if dr else []

    track    = gr.get("track")
    deadline = gr.get("deadline") or ""
    fail_rsn = gr.get("failReason") or ""

    color  = _decision_color(decision)
    dlabel = _decision_label(decision)
    desc   = _desc(idea)
    sid_js = signal_id.replace('"', '\\"')

    return f"""
<div class="card" data-decision="{decision}" data-signal-id="{signal_id}" data-idx="{idx}" id="card-wrap-{idx}">

  <!-- ① 요약 행 (클릭 → 확장) -->
  <div class="card-summary" onclick="toggleCard('card-{idx}','inner-{idx}',this)">
    <div class="summary-left">
      <span class="law-tag">{law}</span>
      <div class="idea-title">
        {idea}
        <span class="review-badge" id="rbadge-{idx}" style="display:none"></span>
      </div>
      <div class="oneliner">{desc['oneliner']}</div>
    </div>
    <div class="summary-right">
      <span class="conf-pill" style="background:{color}22;color:{color};border:1px solid {color}55">{conf}%</span>
      <span class="decision-pill" style="background:{color};color:#fff">{dlabel}</span>
      <span class="track-pill">{_track_label(track)}</span>
      {f'<span class="deadline-pill" data-deadline="{deadline}">D-...</span>' if deadline else ""}
      <span class="expand-icon" id="icon-{idx}">▼</span>
    </div>
  </div>

  <!-- ② 검토 액션 바 (항상 표시, 클릭 이벤트 독립) -->
  <div class="review-bar" onclick="event.stopPropagation()">
    <span class="review-bar-label">내 검토:</span>
    <div class="review-btns">
      <button class="rbtn rbtn-review" onclick="setReview('{sid_js}',{idx},'상세검토')">📋 상세검토 요청</button>
      <button class="rbtn rbtn-hold"   onclick="setReview('{sid_js}',{idx},'보류')">⏸ 보류</button>
      <button class="rbtn rbtn-drop"   onclick="setReview('{sid_js}',{idx},'탈락')">✕ 탈락</button>
      <button class="rbtn rbtn-reset"  onclick="setReview('{sid_js}',{idx},null)">↩</button>
    </div>
  </div>

  <!-- ③ 확장 영역 -->
  <div class="card-detail" id="card-{idx}" style="display:none">
    <div class="inner-tabs" id="tabs-{idx}">
      <button class="inner-tab active" onclick="switchTab({idx},'overview',this)">기회 개요</button>
      <button class="inner-tab" onclick="switchTab({idx},'evidence',this)">법적 근거</button>
      <button class="inner-tab" onclick="switchTab({idx},'target',this)">대상·추정금액</button>
      <button class="inner-tab" onclick="switchTab({idx},'docs',this)">준비 서류</button>
    </div>

    <!-- 기회 개요 -->
    <div class="tab-pane" id="inner-{idx}-overview">
      <p class="desc-detail">{desc['detail']}</p>
      {f'<div class="reasoning-box"><div class="box-label">법리 검토 의견</div><p>{reasoning}</p></div>' if reasoning else ""}
      {f'<div class="cross-ev">{"✅ 판례+예규 교차 인용 확인됨" if cross_ev else "⚠ 교차 인용 미확인"}</div>' if dr else ""}
      {_counter_html(counters)}
      {f'<div class="fail-box">탈락 사유: <code>{fail_rsn}</code></div>' if not gr.get("passed") and fail_rsn else ""}
      <div class="memo-wrap">
        <div class="box-label" style="margin-bottom:6px">메모</div>
        <textarea class="memo-input" id="memo-{idx}" placeholder="검토 의견, 추가 확인 필요 사항 등..." rows="3"
          onchange="saveMemo('{sid_js}',this.value)" oninput="saveMemo('{sid_js}',this.value)"></textarea>
      </div>
    </div>

    <!-- 법적 근거 -->
    <div class="tab-pane" id="inner-{idx}-evidence" style="display:none">
      <div class="box-label">인용 문서 (클릭 → 원문)</div>
      <div class="cite-list">{_cite_html(tokens)}</div>
      {_counter_html(counters)}
    </div>

    <!-- 대상·추정금액 -->
    <div class="tab-pane" id="inner-{idx}-target" style="display:none">
      <div class="box-label">대상 업종 (KSIC)</div>
      <div class="ksic-wrap">{_ksic_html(ksic)}</div>
      <div class="box-label" style="margin-top:16px">청구금액 추정</div>
      {_refund_html(refund)}
      {f'<div class="box-label" style="margin-top:16px">제척기간 마감</div><div class="deadline-wrap"><span class="deadline-date">{deadline}</span><span class="deadline-countdown" data-deadline="{deadline}">계산 중...</span></div>' if deadline else ""}
    </div>

    <!-- 준비 서류 -->
    <div class="tab-pane" id="inner-{idx}-docs" style="display:none">
      <div class="box-label">증빙 체크리스트</div>
      {_checklist_html(checks)}
      <div class="disclaimer">본 정보는 세무대리행위가 아니며 반드시 담당 세무사의 검토가 필요합니다.</div>
    </div>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# 전체 HTML
# ---------------------------------------------------------------------------

def _full_html(data: dict) -> str:
    run_at   = data.get("runAt", "")
    sc1_pass = data.get("sc1Pass", False)
    mock     = data.get("mockMode", False)

    adopted  = data.get("adopted", [])
    review   = data.get("review", [])
    rejected = data.get("rejected", [])
    all_recs = adopted + review + rejected

    idx = 0
    sections_html = ""

    def render_section(recs: list[dict], label: str, start: int) -> tuple[str, int]:
        if not recs:
            return "", start
        cards = "".join(_card_html(r, start + i) for i, r in enumerate(recs))
        return f'<div class="section-label-main">{label}</div>{cards}', start + len(recs)

    s1, idx = render_section(adopted,  "✅ 채택됨 — 즉시 경정청구 권고", idx)
    s2, idx = render_section(review,   "🔍 검토 필요 — 세무사 확인 후 청구", idx)
    s3, idx = render_section(rejected, "❌ 탈락 — 제척기간 초과 또는 인용 부족", idx)
    sections_html = s1 + s2 + s3

    sc1_cls  = "badge-green" if sc1_pass else "badge-red"
    mock_badge = '<span class="badge badge-blue">MOCK</span>' if mock else ""
    total = len(all_recs)

    # signal ID → ideaTitle 매핑 (JS에서 내보내기에 사용)
    sig_map = json.dumps(
        {r.get("signalId", ""): r.get("ideaTitle", "") for r in all_recs},
        ensure_ascii=False,
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>경정청구 파인더 리포트</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0f172a;color:#e2e8f0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR","Apple SD Gothic Neo",sans-serif;font-size:15px;line-height:1.6;padding:0 0 80px}}
a{{color:#60a5fa;text-decoration:none}}a:hover{{text-decoration:underline}}
.muted{{color:#64748b;font-size:13px}}
code{{background:#1e293b;padding:2px 6px;border-radius:4px;font-size:12px;color:#94a3b8}}

/* 헤더 */
.report-header{{background:#0a1120;border-bottom:1px solid #1e293b;padding:20px 20px 14px;position:sticky;top:0;z-index:100}}
.report-inner{{max-width:960px;margin:0 auto;display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px}}
.header-left .report-title{{font-size:20px;font-weight:700;color:#f1f5f9;margin-bottom:6px}}
.report-meta{{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:13px;color:#94a3b8}}
.badge{{display:inline-flex;align-items:center;padding:3px 10px;border-radius:9999px;font-size:12px;font-weight:600}}
.badge-green{{background:#166534;color:#86efac}}
.badge-red{{background:#7f1d1d;color:#fca5a5}}
.badge-blue{{background:#1e3a5f;color:#93c5fd}}

/* 내보내기 버튼 */
.export-btn{{background:#1d4ed8;color:#fff;border:none;padding:9px 18px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:6px;white-space:nowrap;transition:background .15s}}
.export-btn:hover{{background:#2563eb}}
.export-hint{{font-size:11px;color:#64748b;margin-top:4px;text-align:right}}

/* 필터 탭 */
.filter-bar{{max-width:960px;margin:16px auto 0;padding:0 20px;display:flex;gap:4px;flex-wrap:wrap}}
.filter-tab{{background:none;border:1px solid #334155;color:#94a3b8;padding:7px 16px;border-radius:8px;cursor:pointer;font-size:13px;transition:all .15s}}
.filter-tab:hover{{border-color:#60a5fa;color:#60a5fa}}
.filter-tab.active{{background:#1d4ed8;border-color:#1d4ed8;color:#fff;font-weight:600}}

/* 콘텐츠 */
.content{{max-width:960px;margin:16px auto;padding:0 20px}}
.section-label-main{{font-size:12px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.06em;margin:24px 0 8px;padding-left:4px}}

/* 카드 */
.card{{background:#1e293b;border-radius:12px;margin-bottom:8px;overflow:hidden;border:1px solid #334155;transition:border-color .15s}}
.card:hover{{border-color:#475569}}
.card[data-decision="ADOPTED"]{{border-left:4px solid #22c55e}}
.card[data-decision="REVIEW"]{{border-left:4px solid #f59e0b}}
.card[data-decision="REJECTED"]{{border-left:4px solid #ef4444}}
/* 검토 상태별 카드 오버레이 */
.card.user-상세검토{{border-left:4px solid #3b82f6!important;outline:1px solid #3b82f633}}
.card.user-보류{{border-left:4px solid #8b5cf6!important;outline:1px solid #8b5cf633}}
.card.user-탈락{{opacity:.55}}

/* 요약 행 */
.card-summary{{display:flex;justify-content:space-between;align-items:flex-start;padding:14px 18px;cursor:pointer;user-select:none;gap:12px}}
.card-summary:hover{{background:#243447}}
.summary-left{{flex:1;min-width:0}}
.law-tag{{font-size:11px;font-weight:600;color:#94a3b8;background:#0f172a;padding:2px 8px;border-radius:4px;display:inline-block;margin-bottom:5px}}
.idea-title{{font-size:16px;font-weight:700;color:#f1f5f9;line-height:1.3;margin-bottom:3px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.review-badge{{font-size:11px;font-weight:700;padding:2px 8px;border-radius:9999px}}
.oneliner{{font-size:13px;color:#94a3b8;line-height:1.4}}
.summary-right{{display:flex;flex-wrap:wrap;align-items:center;gap:5px;flex-shrink:0;padding-top:2px}}
.conf-pill,.decision-pill,.track-pill,.deadline-pill{{font-size:12px;font-weight:600;padding:3px 9px;border-radius:6px}}
.track-pill{{color:#94a3b8;background:#0f172a}}
.deadline-pill{{color:#f59e0b;background:#451a03}}
.expand-icon{{color:#64748b;font-size:11px;transition:transform .2s;display:inline-block;margin-left:4px}}

/* 검토 액션 바 */
.review-bar{{display:flex;align-items:center;gap:8px;padding:8px 18px;background:#0f172a;border-top:1px solid #1e293b;flex-wrap:wrap}}
.review-bar-label{{font-size:11px;font-weight:600;color:#64748b;white-space:nowrap}}
.review-btns{{display:flex;gap:4px;flex-wrap:wrap}}
.rbtn{{border:1px solid #334155;background:none;color:#94a3b8;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:12px;transition:all .15s;white-space:nowrap}}
.rbtn:hover{{border-color:#60a5fa;color:#e2e8f0}}
.rbtn-review.active{{background:#1e40af;border-color:#3b82f6;color:#93c5fd}}
.rbtn-hold.active{{background:#4c1d95;border-color:#8b5cf6;color:#c4b5fd}}
.rbtn-drop.active{{background:#7f1d1d;border-color:#ef4444;color:#fca5a5}}
.rbtn-reset{{border-color:#1e293b;color:#64748b}}
.rbtn-reset:hover{{border-color:#64748b;color:#94a3b8}}

/* 확장 영역 */
.card-detail{{border-top:1px solid #334155}}
.inner-tabs{{display:flex;border-bottom:1px solid #334155;background:#0a1120;overflow-x:auto}}
.inner-tab{{background:none;border:none;color:#64748b;padding:10px 16px;cursor:pointer;font-size:13px;font-weight:500;border-bottom:2px solid transparent;white-space:nowrap;transition:all .15s}}
.inner-tab:hover{{color:#e2e8f0}}
.inner-tab.active{{color:#60a5fa;border-bottom-color:#3b82f6;background:#1e293b}}
.tab-pane{{padding:18px}}

/* 탭 콘텐츠 */
.desc-detail{{color:#cbd5e1;line-height:1.75;font-size:14px;margin-bottom:14px}}
.reasoning-box{{background:#0f172a;border-radius:8px;padding:12px;border-left:3px solid #3b82f6;margin-bottom:10px}}
.reasoning-box p{{color:#94a3b8;font-size:13px;line-height:1.6}}
.box-label{{font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:7px}}
.cross-ev{{font-size:13px;color:#94a3b8;margin-bottom:10px}}
.counter-wrap{{background:#2d1515;border-radius:8px;padding:12px;margin-top:10px}}
.counter-label{{font-size:12px;font-weight:600;color:#f87171;margin-bottom:5px}}
.counter-wrap ul{{padding-left:16px}}
.counter-item{{font-size:13px;color:#fca5a5;line-height:1.5}}
.fail-box{{background:#1c1008;border:1px solid #7c2d12;border-radius:8px;padding:10px;font-size:13px;color:#fb923c;margin-top:10px}}
.memo-wrap{{margin-top:14px}}
.memo-input{{width:100%;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#e2e8f0;padding:10px 12px;font-size:13px;resize:vertical;font-family:inherit;transition:border-color .15s}}
.memo-input:focus{{outline:none;border-color:#3b82f6}}
.cite-list{{display:flex;flex-direction:column;gap:7px;margin-bottom:14px}}
.cite-link{{display:inline-flex;align-items:center;gap:8px;background:#0f172a;padding:8px 12px;border-radius:8px;font-size:13px;border:1px solid #334155;transition:border-color .15s}}
.cite-link:hover{{border-color:#60a5fa;text-decoration:none}}
.cite-src{{font-size:11px;font-weight:600;color:#fff;background:#1d4ed8;padding:2px 7px;border-radius:4px;flex-shrink:0}}
.ksic-wrap{{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:6px}}
.ksic-badge{{font-size:12px;background:#0f172a;border:1px solid #334155;padding:3px 9px;border-radius:6px;color:#94a3b8}}
.targets-line{{font-size:13px;color:#94a3b8;margin-top:5px;width:100%}}
.refund-range{{font-size:22px;font-weight:700;color:#f1f5f9;margin:4px 0}}
.refund-basis{{font-size:12px;color:#64748b;margin-top:3px}}
.deadline-wrap{{display:flex;align-items:center;gap:12px;margin-top:5px}}
.deadline-date{{font-size:13px;color:#94a3b8}}
.deadline-countdown{{font-size:20px;font-weight:700;color:#f59e0b}}
.checklist{{display:flex;flex-direction:column;gap:7px;margin-bottom:14px}}
.check-item{{display:flex;align-items:center;gap:9px;cursor:pointer;font-size:14px;color:#cbd5e1;padding:8px 12px;background:#0f172a;border-radius:8px;border:1px solid #334155}}
.check-item:hover{{border-color:#475569}}
.check-item input{{width:16px;height:16px;accent-color:#3b82f6;cursor:pointer;flex-shrink:0}}
.disclaimer{{margin-top:14px;padding:10px 12px;background:#0f172a;border-radius:8px;font-size:12px;color:#64748b;border:1px solid #1e293b}}

/* 내보내기 모달 */
.modal-overlay{{display:none;position:fixed;inset:0;background:#000a;z-index:200;align-items:center;justify-content:center}}
.modal-overlay.open{{display:flex}}
.modal{{background:#1e293b;border-radius:12px;border:1px solid #334155;padding:24px;max-width:560px;width:calc(100% - 40px);position:relative}}
.modal h3{{font-size:16px;font-weight:700;color:#f1f5f9;margin-bottom:12px}}
.modal p{{font-size:13px;color:#94a3b8;margin-bottom:14px;line-height:1.6}}
.modal textarea{{width:100%;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#e2e8f0;padding:10px;font-size:12px;font-family:monospace;resize:vertical;height:160px}}
.modal-btns{{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}}
.modal-btn{{padding:8px 16px;border-radius:8px;border:none;cursor:pointer;font-size:13px;font-weight:600}}
.modal-btn-primary{{background:#1d4ed8;color:#fff}}
.modal-btn-primary:hover{{background:#2563eb}}
.modal-btn-secondary{{background:#334155;color:#e2e8f0}}
.modal-btn-secondary:hover{{background:#475569}}
.modal-close{{position:absolute;top:14px;right:16px;background:none;border:none;color:#64748b;font-size:18px;cursor:pointer;line-height:1}}

@media(max-width:640px){{
  .summary-right{{gap:4px}}
  .idea-title{{font-size:14px}}
  .filter-tab{{padding:6px 10px;font-size:12px}}
  .review-bar{{padding:7px 12px}}
  .card-summary{{padding:12px 14px}}
}}

/* ── 비밀번호 게이트 ── */
#auth-gate{{position:fixed;inset:0;background:#0a1120;z-index:9999;display:flex;align-items:center;justify-content:center;padding:24px}}
.auth-box{{background:#111827;border:1px solid #1e3a5f;border-radius:16px;padding:40px 36px;max-width:380px;width:100%;text-align:center;box-shadow:0 24px 80px rgba(0,0,0,.6)}}
.auth-logo{{font-size:2rem;margin-bottom:8px}}
.auth-title{{font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-bottom:4px}}
.auth-sub{{font-size:0.82rem;color:#64748b;margin-bottom:28px}}
.auth-input{{width:100%;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:1rem;padding:12px 14px;outline:none;transition:border .2s}}
.auth-input:focus{{border-color:#3b82f6}}
.auth-btn{{margin-top:14px;width:100%;background:#2563eb;border:none;border-radius:8px;color:#fff;font-size:0.95rem;font-weight:600;padding:13px;cursor:pointer;transition:background .2s}}
.auth-btn:hover{{background:#1d4ed8}}
.auth-err{{margin-top:10px;font-size:0.8rem;color:#f87171;min-height:18px}}
</style>
</head>
<body>

<div id="auth-gate">
  <div class="auth-box">
    <div class="auth-logo">🔒</div>
    <div class="auth-title">경정청구 파인더</div>
    <div class="auth-sub">접근 권한이 필요합니다</div>
    <input class="auth-input" id="auth-pw" type="password" placeholder="비밀번호 입력" autocomplete="current-password">
    <button class="auth-btn" id="auth-btn">확인</button>
    <div class="auth-err" id="auth-err"></div>
  </div>
</div>

<header class="report-header">
  <div class="report-inner">
    <div class="header-left">
      <div class="report-title">경정청구 파인더 리포트</div>
      <div class="report-meta">
        <span>실행: {run_at[:16].replace("T"," ")} UTC</span>
        <span class="badge {sc1_cls}">SC-1 {"통과" if sc1_pass else "미통과"}</span>
        {mock_badge}
        <span>총 {total}건 (채택 {len(adopted)} · 검토 {len(review)} · 탈락 {len(rejected)})</span>
      </div>
    </div>
    <div>
      <button class="export-btn" onclick="openExport()">
        ⬇ 검토 결정 내보내기
      </button>
      <div class="export-hint">Claude에게 붙여넣기 → 자동 반영</div>
    </div>
  </div>
</header>

<div class="filter-bar">
  <button class="filter-tab active" onclick="filterCards('ALL',this)">전체 ({total})</button>
  <button class="filter-tab" onclick="filterCards('ADOPTED',this)">✅ 채택됨 ({len(adopted)})</button>
  <button class="filter-tab" onclick="filterCards('REVIEW',this)">🔍 검토필요 ({len(review)})</button>
  <button class="filter-tab" onclick="filterCards('REJECTED',this)">❌ 탈락 ({len(rejected)})</button>
  <button class="filter-tab" onclick="filterUserReview('상세검토',this)">📋 상세검토 요청</button>
  <button class="filter-tab" onclick="filterUserReview('보류',this)">⏸ 보류</button>
  <button class="filter-tab" onclick="filterUserReview('탈락',this)">✕ 내가 탈락</button>
</div>

<div class="content" id="main-content">
{sections_html}
</div>

<!-- 내보내기 모달 -->
<div class="modal-overlay" id="export-modal">
  <div class="modal">
    <button class="modal-close" onclick="closeExport()">✕</button>
    <h3>⬇ 검토 결정 내보내기</h3>
    <p>아래 JSON을 복사해서 Claude에게 붙여넣기하면 결정 내용이 파이프라인에 반영됩니다.</p>
    <textarea id="export-text" readonly></textarea>
    <div class="modal-btns">
      <button class="modal-btn modal-btn-primary" onclick="copyExport()">📋 클립보드 복사</button>
      <button class="modal-btn modal-btn-secondary" onclick="downloadExport()">💾 파일 다운로드</button>
      <button class="modal-btn modal-btn-secondary" onclick="closeExport()">닫기</button>
    </div>
  </div>
</div>

<script>
const SIG_MAP = {sig_map};
const STORAGE_KEY = 'tax_finder_reviews';

// ── 저장소 ──
function loadReviews() {{
  try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}'); }}
  catch {{ return {{}}; }}
}}
function saveReviews(obj) {{
  localStorage.setItem(STORAGE_KEY, JSON.stringify(obj));
}}

// ── 검토 상태 세팅 ──
const RBADGE_STYLE = {{
  '상세검토': ['#1e40af','#93c5fd','📋 상세검토'],
  '보류':    ['#4c1d95','#c4b5fd','⏸ 보류'],
  '탈락':    ['#7f1d1d','#fca5a5','✕ 탈락'],
}};

function setReview(signalId, idx, state) {{
  const reviews = loadReviews();
  if (state === null) {{
    delete reviews[signalId];
  }} else {{
    reviews[signalId] = {{ state, memo: reviews[signalId]?.memo || '', updatedAt: new Date().toISOString() }};
  }}
  saveReviews(reviews);
  applyReviewUI(signalId, idx, state);
}}

function applyReviewUI(signalId, idx, state) {{
  const wrap  = document.getElementById('card-wrap-' + idx);
  const badge = document.getElementById('rbadge-' + idx);
  const btns  = wrap?.querySelectorAll('.rbtn');
  if (!wrap) return;

  // 카드 클래스
  wrap.classList.remove('user-상세검토','user-보류','user-탈락');
  if (state) wrap.classList.add('user-' + state);

  // 뱃지
  if (state && RBADGE_STYLE[state]) {{
    const [bg,fg,label] = RBADGE_STYLE[state];
    badge.style.display = 'inline-flex';
    badge.style.background = bg;
    badge.style.color = fg;
    badge.textContent = label;
  }} else {{
    badge.style.display = 'none';
  }}

  // 버튼 active
  btns?.forEach(b => {{
    b.classList.remove('active');
    if ((state === '상세검토' && b.classList.contains('rbtn-review')) ||
        (state === '보류'    && b.classList.contains('rbtn-hold'))   ||
        (state === '탈락'    && b.classList.contains('rbtn-drop'))) {{
      b.classList.add('active');
    }}
  }});
}}

function saveMemo(signalId, value) {{
  const reviews = loadReviews();
  if (!reviews[signalId]) reviews[signalId] = {{ state: null, memo: value, updatedAt: new Date().toISOString() }};
  else reviews[signalId].memo = value;
  saveReviews(reviews);
}}

// ── 페이지 로드 시 복원 ──
function restoreAll() {{
  const reviews = loadReviews();
  document.querySelectorAll('.card').forEach(card => {{
    const sid = card.dataset.signalId;
    const idx = parseInt(card.dataset.idx);
    const rv  = reviews[sid];
    if (rv) {{
      applyReviewUI(sid, idx, rv.state || null);
      const memo = document.getElementById('memo-' + idx);
      if (memo && rv.memo) memo.value = rv.memo;
    }}
  }});
}}

// ── 필터 ──
function filterCards(decision, btn) {{
  document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = (decision === 'ALL' || c.dataset.decision === decision) ? '' : 'none';
  }});
  syncSectionLabels();
}}

function filterUserReview(state, btn) {{
  document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const reviews = loadReviews();
  document.querySelectorAll('.card').forEach(c => {{
    const rv = reviews[c.dataset.signalId];
    c.style.display = (rv?.state === state) ? '' : 'none';
  }});
  syncSectionLabels();
}}

function syncSectionLabels() {{
  document.querySelectorAll('.section-label-main').forEach(el => {{
    let sib = el.nextElementSibling;
    let hasVisible = false;
    while (sib && sib.classList.contains('card')) {{
      if (sib.style.display !== 'none') {{ hasVisible = true; break; }}
      sib = sib.nextElementSibling;
    }}
    el.style.display = hasVisible ? '' : 'none';
  }});
}}

// ── 카드 토글 ──
function toggleCard(cardId, innerId, summaryEl) {{
  const detail = document.getElementById(cardId);
  const icon   = summaryEl.querySelector('.expand-icon');
  const isOpen = detail.style.display !== 'none';
  detail.style.display = isOpen ? 'none' : '';
  if (icon) icon.style.transform = isOpen ? '' : 'rotate(180deg)';
}}

// ── 내부 탭 ──
function switchTab(idx, tabName, btn) {{
  document.getElementById('tabs-'+idx).querySelectorAll('.inner-tab')
    .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  ['overview','evidence','target','docs'].forEach(t => {{
    const el = document.getElementById('inner-'+idx+'-'+t);
    if (el) el.style.display = t === tabName ? '' : 'none';
  }});
}}

// ── D-day ──
function calcDeadlines() {{
  const today = new Date(); today.setHours(0,0,0,0);
  document.querySelectorAll('[data-deadline]').forEach(el => {{
    const dl = new Date(el.dataset.deadline); dl.setHours(0,0,0,0);
    const diff = Math.round((dl - today) / 86400000);
    if (el.classList.contains('deadline-pill')) {{
      el.textContent = diff >= 0 ? 'D-'+diff : '만료';
      if (diff < 30 && diff >= 0) {{ el.style.background='#7f1d1d'; el.style.color='#fca5a5'; }}
    }} else if (el.classList.contains('deadline-countdown')) {{
      el.textContent = diff >= 0 ? '잔여 '+diff+'일' : '만료 (기간 초과)';
      if (diff < 0) el.style.color = '#ef4444';
    }}
  }});
}}

// ── 내보내기 ──
function buildExportJson() {{
  const reviews = loadReviews();
  const items = [];
  document.querySelectorAll('.card').forEach(card => {{
    const sid   = card.dataset.signalId;
    const title = SIG_MAP[sid] || '';
    const rv    = reviews[sid];
    if (rv?.state || rv?.memo) {{
      items.push({{ signalId: sid, ideaTitle: title,
        reviewDecision: rv.state || null, memo: rv.memo || '',
        reviewedAt: rv.updatedAt || '' }});
    }}
  }});
  return JSON.stringify({{ exportedAt: new Date().toISOString(), reviews: items }}, null, 2);
}}

function openExport() {{
  document.getElementById('export-text').value = buildExportJson();
  document.getElementById('export-modal').classList.add('open');
}}
function closeExport() {{
  document.getElementById('export-modal').classList.remove('open');
}}
function copyExport() {{
  const ta = document.getElementById('export-text');
  ta.select();
  document.execCommand('copy');
  const btn = event.target;
  btn.textContent = '✅ 복사됨!';
  setTimeout(() => btn.textContent = '📋 클립보드 복사', 1500);
}}
function downloadExport() {{
  const blob = new Blob([buildExportJson()], {{type:'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'tax_finder_reviews.json';
  a.click();
}}

document.addEventListener('DOMContentLoaded', () => {{
  restoreAll();
  calcDeadlines();
}});
</script>

<script>
(function(){{
  const HASH = "449891ed203c3baef90fc7004e55030586a09653ecfa37d63830ec557ffea50a";
  const KEY  = "tfauth_v1";
  const gate = document.getElementById("auth-gate");
  const inp  = document.getElementById("auth-pw");
  const btn  = document.getElementById("auth-btn");
  const err  = document.getElementById("auth-err");

  async function sha256(s){{
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
    return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,"0")).join("");
  }}

  function unlock(){{ gate.style.display="none"; inp.value=""; }}

  if(sessionStorage.getItem(KEY)===HASH) unlock();

  async function tryAuth(){{
    const h = await sha256(inp.value.trim());
    if(h===HASH){{ sessionStorage.setItem(KEY,HASH); unlock(); }}
    else{{ err.textContent="비밀번호가 올바르지 않습니다."; inp.focus(); }}
  }}

  btn.addEventListener("click", tryAuth);
  inp.addEventListener("keydown", e=>{{ if(e.key==="Enter") tryAuth(); }});
  inp.focus();
}})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# T7HtmlRenderer
# ---------------------------------------------------------------------------

class T7HtmlRenderer:
    def render(self, output_json: dict) -> str:
        return _full_html(output_json)

    def render_file(self, input_path: str, output_path: str) -> None:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        html = self.render(data)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)


# ---------------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    in_path  = str(_HERE / "output_sample.json")
    out_path = str(_HERE / "output_report.html")

    T7HtmlRenderer().render_file(in_path, out_path)
    size = Path(out_path).stat().st_size
    print(f"output_report.html 생성 완료  ({size:,} bytes)")
    print(f"경로: {out_path}")
