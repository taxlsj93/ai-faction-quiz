"""
T0 Citation Adapter
===================
결정론적 어댑터. LLM 호출 0회.
- citationToken 발급 (순수 함수)
- Mock registry 조회 (retry 2회, 3s/9s backoff)
- 4개 소스 URL 화이트리스트 검증

Python 3.11+, 표준 라이브러리 + hashlib만 사용
"""

from __future__ import annotations

import hashlib
import time
from copy import deepcopy
from typing import Optional


# ---------------------------------------------------------------------------
# Mock fixture — 파일럿 3개 아이디어 (게임사 R&D, 통합투자세액공제, 장애인고용부담금)
# ---------------------------------------------------------------------------

MOCK_REGISTRY: dict[str, dict] = {
    # 게임사 R&D 세액공제
    "nts:ruling:서면-2023-법규-0142:2023-01-15": {
        "body": "게임소프트웨어 개발업의 연구개발 인건비는 조세특례제한법 제10조 적용 대상이며 사후관리 인건비 포함 가능",
        "docId": "서면-2023-법규-0142",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2023-01-15",
    },
    "scourt:case:2024두12345:2024-08-20": {
        "body": "원심판결을 파기하고 환송한다. 게임 R&D 세액공제 관련 하급심의 판단은 조특법 제10조 해석 오류가 있다",
        "docId": "2024두12345",
        "docType": "case",
        "source": "scourt",
        "publishedDate": "2024-08-20",
    },
    # 통합투자세액공제
    "moleg:law:조특법-24:2024-01-01": {
        "body": "통합투자세액공제 대상 자산에 안전자산 및 족장설비 포함. 2024년 개정으로 범위 확대",
        "docId": "조특법-24",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2024-01-01",
    },
    "nts:ruling:기재부-법인-2023-0088:2023-06-10": {
        "body": "안전자산 취득시 통합투자세액공제 적용 가능 여부: 법령 해석상 포함 가능",
        "docId": "기재부-법인-2023-0088",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2023-06-10",
    },
    # 장애인고용부담금
    "scourt:case:2024두98765:2024-11-15": {
        "body": "장애인 고용부담금은 법인세법 제19조에 따른 손금 해당 여부: 손금 산입을 인정한다",
        "docId": "2024두98765",
        "docType": "case",
        "source": "scourt",
        "publishedDate": "2024-11-15",
    },
    "nts:ruling:법인세과-2019-0445:2019-08-01": {
        "body": "장애인 고용부담금의 손금 산입 불인정. 사업 관련성 없음",
        "docId": "법인세과-2019-0445",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2019-08-01",
    },
    # 고용증대 세액공제 코로나 불가항력
    "nts:ruling:조특제도과-2021-0698:2021-05-18": {
        "body": "코로나19로 인한 고용감소는 불가항력 사유로 인정하여 조특법 제29조의7에 따른 고용증대 세액공제 사후관리 의무를 면제함",
        "docId": "조특제도과-2021-0698",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2021-05-18",
    },
    # R&D 위탁연구 범위 확대
    "moleg:law:조특법시행령-9:2020-02-11": {
        "body": "조세특례제한법 시행령 제9조 개정으로 위탁연구개발 인정기관 범위 확대. 과학기술정보통신부장관이 인정한 민간 연구개발 전문기관 추가 포함",
        "docId": "조특법시행령-9",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2020-02-11",
    },
    # 중소기업 특별세액감면 KSIC 재분류
    "moleg:law:조특법-7-별표:2017-07-01": {
        "body": "조세특례제한법 제7조 감면 대상 업종 별표. KSIC 10차 개정 반영, 소프트웨어 개발·공급업(58221), 컴퓨터 프로그래밍(62010) 등 디지털 서비스업 감면 대상 포함",
        "docId": "조특법-7-별표",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2017-07-01",
    },
    # 외국납부세액공제 간접세액
    "nts:ruling:국제세원-2022-0055:2022-09-01": {
        "body": "간접외국납부세액공제 한도 계산 시 분모인 외국자회사 세후이익은 배당 가능 이익 전체로 계산하며, 해당 사업연도 배당액만으로 한정하지 않음",
        "docId": "국제세원-2022-0055",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2022-09-01",
    },
    # 퇴직급여충당금 DB 전환
    "nts:ruling:서면2팀-2016-0023:2016-03-15": {
        "body": "확정급여형(DB) 퇴직연금 도입 시 과거 근무기간에 해당하는 퇴직급여충당금 추가 설정액은 법인세법 제33조에 따라 손금산입 가능",
        "docId": "서면2팀-2016-0023",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2016-03-15",
    },
    # 중대재해처벌법 안전투자 통합투자세액공제
    "moleg:law:중대재해처벌법-4:2022-01-27": {
        "body": "중대재해처벌법 제4조: 사업주·경영책임자는 안전보건관리체계 구축 및 이행조치 의무. 50인 이상 사업장 2022.01.27 시행. 안전설비 의무투자 근거 조항",
        "docId": "중대재해처벌법-4",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2022-01-27",
    },
    # 화관법 취급시설 개선투자
    "moleg:law:화관법-24:2015-12-01": {
        "body": "화학물질관리법 제24조: 유해화학물질 취급시설 설치·운영 기준. 방류벽, 저장탱크, 누출감지기 등 의무설비 규정. 2015년 이후 수차례 개정으로 기준 강화",
        "docId": "화관법-24",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2015-12-01",
    },
    # 개인정보보호법 전면개정 보안R&D
    "moleg:law:개보법-28의2:2023-09-15": {
        "body": "개인정보보호법 제28조의2(가명정보 처리): 2023년 전면개정으로 개인정보보호책임자(CPO) 의무 강화, 개인정보 보안기술 연구개발 의무화 관련 규정",
        "docId": "개보법-28의2",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2023-09-15",
    },
    "nts:ruling:서면-2024-법규-0033:2024-03-10": {
        "body": "정보보안 기술 연구개발비의 조특법 제10조 R&D 세액공제 적용 여부: 연구활동 해당 여부는 기술혁신성 및 불확실성 기준으로 판단. 암호화·보안알고리즘 개발은 R&D 해당 가능",
        "docId": "서면-2024-법규-0033",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2024-03-10",
    },
    # 탄소중립기본법 감축설비 에너지절약
    "moleg:law:탄소중립법-24:2022-03-25": {
        "body": "탄소중립기본법 제24조: 온실가스 배출권 할당대상 업체의 감축의무. 폐열회수, 고효율설비 투자는 에너지이용합리화법 및 조특법 §25의2 에너지절약시설 세액공제 대상",
        "docId": "탄소중립법-24",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2022-03-25",
    },
    # 공정거래법 전부개정 준법지원
    "moleg:law:공정거래법-22의2:2021-12-30": {
        "body": "독점규제 및 공정거래에 관한 법률 제22조의2: 공정거래 자율준수 프로그램(CP) 및 준법지원인 제도. 2020년 전부개정·2021년 시행으로 대기업집단 의무화",
        "docId": "공정거래법-22의2",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2021-12-30",
    },
    # 건축물관리법 정밀안전점검
    "moleg:law:건축물관리법-11:2020-05-01": {
        "body": "건축물관리법 제11조: 건축물 정기점검 및 정밀안전점검 의무. 2020.05 시행으로 30년 이상 건축물 소유자 정기 의무점검 부과. 점검비용은 수익적지출(즉시손금) 해당",
        "docId": "건축물관리법-11",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2020-05-01",
    },
    # 환경개선부담금 손금산입
    "moleg:law:환경개선비용부담법-9:2019-01-01": {
        "body": "환경개선비용부담법 제9조: 시설물 소유자·건물 부과 환경개선부담금. 연간 납부 의무. 장애인고용부담금 대법원 판례(2024두98765) 유추 시 사업 관련성 있는 손금 해당 여지",
        "docId": "환경개선비용부담법-9",
        "docType": "law",
        "source": "moleg",
        "publishedDate": "2019-01-01",
    },
    # 적격합병 이월결손금 승계
    "scourt:case:2023두41234:2023-09-22": {
        "body": "적격합병 이월결손금 승계 요건 판단: 합병비율 산정 등 형식요건 일부 불비라도 실질적 사업 목적과 고용 승계 요건이 충족되면 조특법 §44 적격합병 인정 가능",
        "docId": "2023두41234",
        "docType": "case",
        "source": "scourt",
        "publishedDate": "2023-09-22",
    },
    "nts:ruling:법인세과-2023-0521:2023-11-15": {
        "body": "적격합병 요건 판단 시 실질요건 우선 해석 원칙. 이월결손금 승계 거부 처분의 취소 가능성 검토",
        "docId": "법인세과-2023-0521",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2023-11-15",
    },
    # 업무용 리스차량 감가상각비 한도
    "nts:ruling:서면-2020-법규-2021:2021-06-01": {
        "body": "업무용승용차 리스 임차료 한도 계산: 법인세법 §27의2 적용 시 감가상각비 상당액만 연 800만원 한도 적용 대상이며, 보험료·수리비·기타 부대비용은 한도 외 별도 처리",
        "docId": "서면-2020-법규-2021",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2021-06-01",
    },
    # SIG-019~050 신규 인용 문서
    "nts:ruling:부가-2023-0055:2023-06-01": {"body":"연예인 미용시술비의 부가세 매입세액공제 적용 여부: 방송 출연을 위한 미용시술이 사업 관련 용역이라면 매입세액공제 대상 가능성 검토","docId":"부가-2023-0055","docType":"ruling","source":"nts","publishedDate":"2023-06-01"},
    "scourt:case:2022두55678:2022-12-01": {"body":"연예인 이미지 관리 비용의 사업 관련성 판단: 방송·광고 출연 계약에 따른 의무적 외모 관리 비용은 사업 관련 비용으로 볼 여지 있음","docId":"2022두55678","docType":"case","source":"scourt","publishedDate":"2022-12-01"},
    "nts:ruling:부가-2022-0133:2022-11-15": {"body":"부동산임대업과 과세사업 겸업 법인의 공통매입세액 안분: 면세사업 비율 산정 시 토지 공급가액 포함 여부 및 정확한 안분 방법 기준","docId":"부가-2022-0133","docType":"ruling","source":"nts","publishedDate":"2022-11-15"},
    "nts:ruling:부가-2021-0077:2021-09-10": {"body":"해외 판매자 국내 판매 대행 플랫폼 수수료의 영세율 적용 여부: 국외 공급 용역에 해당하는 경우 부가가치세법 §24 영세율 적용 가능","docId":"부가-2021-0077","docType":"ruling","source":"nts","publishedDate":"2021-09-10"},
    "moleg:law:환경친화적자동차법-2:2020-11-01": {"body":"환경친화적 자동차의 개발 및 보급 촉진에 관한 법률 §2: 전기차 충전 인프라 의무 설치 규정. 사업장 내 충전기는 업무용 자산으로 부가세 매입세액공제 가능","docId":"환경친화적자동차법-2","docType":"law","source":"moleg","publishedDate":"2020-11-01"},
    "nts:ruling:서면-2022-법규-0211:2022-07-15": {"body":"의약품 임상시험 비용의 R&D 세액공제 적용: 3상 임상시험도 기술적 불확실성이 존재하면 조특법 §10 연구개발 해당 가능. 사업화 단계 일률 배제 불가","docId":"서면-2022-법규-0211","docType":"ruling","source":"nts","publishedDate":"2022-07-15"},
    "moleg:law:약사법-34:2019-01-01": {"body":"약사법 제34조: 임상시험 계획 승인 및 실시 기준. 식약처 승인 임상시험 비용의 연구개발비 해당 여부 판단 근거","docId":"약사법-34","docType":"law","source":"moleg","publishedDate":"2019-01-01"},
    "nts:ruling:서면-2023-법규-0456:2023-08-20": {"body":"금융업 AI 기반 신용평가 모델 개발 비용의 R&D 세액공제 해당 여부: 기술적 불확실성 및 혁신성 기준 충족 시 조특법 §10 적용 가능","docId":"서면-2023-법규-0456","docType":"ruling","source":"nts","publishedDate":"2023-08-20"},
    "nts:ruling:서면-2021-법규-0088:2021-11-01": {"body":"반도체 설계용 EDA 소프트웨어 라이선스비의 R&D 세액공제 포함 여부: 연구개발 전용 도구 구입비는 조특법 시행령 §9 연구개발비 범위에 포함","docId":"서면-2021-법규-0088","docType":"ruling","source":"nts","publishedDate":"2021-11-01"},
    "nts:ruling:서면-2024-법규-0188:2024-05-15": {"body":"AI 학습 데이터셋 구입 및 라벨링 비용의 R&D 세액공제 포함 여부: 2024년 예규 변화로 AI 모델 개발을 위한 데이터 비용의 연구개발비 해당 가능성 인정","docId":"서면-2024-법규-0188","docType":"ruling","source":"nts","publishedDate":"2024-05-15"},
    "moleg:law:건설기술진흥법-62의2:2021-07-01": {"body":"건설기술진흥법 제62조의2: BIM(건물정보모델링) 적용 의무화. 발주 규모 이상 공공공사 BIM 설계 의무화로 건설사 자체 BIM 소프트웨어 개발비 R&D 해당 가능","docId":"건설기술진흥법-62의2","docType":"law","source":"moleg","publishedDate":"2021-07-01"},
    "moleg:law:대규모유통업법-12:2020-01-29": {"body":"대규모유통업에서의 거래 공정화에 관한 법률 §12: 판촉행사 비용 분담 제한. 2020년 개정으로 대형유통업체의 직접 부담 의무화. 강제분담금은 사업 관련 손금 가능","docId":"대규모유통업법-12","docType":"law","source":"moleg","publishedDate":"2020-01-29"},
    "nts:ruling:법인세과-2023-0788:2023-12-15": {"body":"IFRS17 전환 시 보험사 책임준비금 세무 처리: 세무상 인정 한도와 IFRS17 기준 적립액 차이에 따른 세무조정 방법 및 익금산입 기준 명확화","docId":"법인세과-2023-0788","docType":"ruling","source":"nts","publishedDate":"2023-12-15"},
    "moleg:law:보험업법-120:2023-01-01": {"body":"보험업법 제120조: 책임준비금 적립 의무. IFRS17 도입으로 산출방식 변경. 세무상 손금 인정 한도와의 차이 조정 필요","docId":"보험업법-120","docType":"law","source":"moleg","publishedDate":"2023-01-01"},
    "moleg:law:수소경제육성법-5:2021-02-05": {"body":"수소경제 육성 및 수소안전관리에 관한 법률 §5: 수소 충전 인프라 구축 의무. 수소충전소·연료전지 설비는 에너지이용합리화법상 에너지절약시설에 해당 가능","docId":"수소경제육성법-5","docType":"law","source":"moleg","publishedDate":"2021-02-05"},
    "moleg:law:선박평형수관리법-8:2019-09-22": {"body":"선박평형수 관리에 관한 법률 §8: 선박평형수처리장치(BWTS) 의무 설치. 국제협약 이행 의무 설비로 환경보전시설 세액공제 적용 가능","docId":"선박평형수관리법-8","docType":"law","source":"moleg","publishedDate":"2019-09-22"},
    "moleg:law:방위사업법-33:2022-06-10": {"body":"방위사업법 제33조: 방산업체 연구개발 지원. 2022년 개정으로 방산 R&D 세액공제 우대율 적용 근거 강화","docId":"방위사업법-33","docType":"law","source":"moleg","publishedDate":"2022-06-10"},
    "nts:ruling:서면-2022-법규-0339:2022-09-01": {"body":"방위산업체 연구개발비의 조특법 §10 세액공제 적용 방법: 방산 R&D 공제율 우대 조항 적용 시 일반 R&D와 구분 처리 기준","docId":"서면-2022-법규-0339","docType":"ruling","source":"nts","publishedDate":"2022-09-01"},
    "moleg:law:항공안전법-23:2020-05-27": {"body":"항공안전법 제23조: 항공안전관리시스템(SMS) 구축 의무화. 안전 설비·시뮬레이터 투자는 조특법 §24 통합투자세액공제 대상","docId":"항공안전법-23","docType":"law","source":"moleg","publishedDate":"2020-05-27"},
    "moleg:law:근로기준법-76의3:2019-07-16": {"body":"근로기준법 제76조의3: 직장 내 괴롭힘 방지 의무화(2019.07.16 시행). 예방교육·상담 프로그램 비용은 교육훈련비(전액 손금) 또는 업무관련 비용으로 처리 가능","docId":"근로기준법-76의3","docType":"law","source":"moleg","publishedDate":"2019-07-16"},
    "nts:ruling:법인세과-2022-0215:2022-04-18": {"body":"스마트공장 구축 국고보조금 수령 시 압축기장충당금(일시상각충당금) 설정을 통한 과세이연 허용. 법인세법 §36 국고보조금 처리 방법","docId":"법인세과-2022-0215","docType":"ruling","source":"nts","publishedDate":"2022-04-18"},
    "scourt:case:2023두15678:2023-05-12": {"body":"임원 명예퇴직금의 손금산입 한도 판단: 정관 규정 한도를 초과한 경우라도 실질 근로기간·업무 기여도가 명확하면 일부 손금 인정 가능","docId":"2023두15678","docType":"case","source":"scourt","publishedDate":"2023-05-12"},
    "nts:ruling:서면-2021-법규-0455:2021-08-20": {"body":"주식매수선택권(스톡옵션) 행사차익의 법인세 손금 처리: 행사시점 기준 손금 귀속이 원칙. 부여시 비용화 또는 미처리 법인은 경정청구 가능","docId":"서면-2021-법규-0455","docType":"ruling","source":"nts","publishedDate":"2021-08-20"},
    "nts:ruling:국제세원-2021-0122:2021-12-10": {"body":"외국법인 기술사용료 원천징수 세율: 조세조약 제한세율(10~15%) 적용 요건. 5년치 과다납부분 경정청구 가능 요건 및 거주지증명서 제출 절차","docId":"국제세원-2021-0122","docType":"ruling","source":"nts","publishedDate":"2021-12-10"},
    "nts:ruling:서면-2019-법규-0567:2019-09-25": {"body":"기업부설연구소 전용 공간 임차료의 R&D 세액공제 포함 여부: 연구 전용 공간 임차료는 조특법 시행령 §9 연구개발비에 포함 가능","docId":"서면-2019-법규-0567","docType":"ruling","source":"nts","publishedDate":"2019-09-25"},
    "moleg:law:물환경보전법-38의2:2021-01-05": {"body":"물환경보전법 제38조의2: 산업용 폐수 재이용 의무화. 반도체 초순수·폐수 재이용 시스템은 환경보전시설 세액공제 별표 해당 가능","docId":"물환경보전법-38의2","docType":"law","source":"moleg","publishedDate":"2021-01-05"},
    "moleg:law:순환경제촉진법-13:2022-12-30": {"body":"순환경제사회 전환 촉진법 §13: 산업부산물 재활용 의무. 슬래그·잔재물 재활용 설비는 환경보전시설로 세액공제 대상","docId":"순환경제촉진법-13","docType":"law","source":"moleg","publishedDate":"2022-12-30"},
    "moleg:law:해양환경관리법-41의2:2020-01-01": {"body":"해양환경관리법 제41조의2: IMO2020 황산화물 배출 규제 이행. 선박 스크러버 설치 또는 저유황연료 전환 설비는 에너지절약시설 공제 대상 검토 필요","docId":"해양환경관리법-41의2","docType":"law","source":"moleg","publishedDate":"2020-01-01"},
    "nts:ruling:법인세과-2019-0188:2019-03-20": {"body":"IFRS9 도입 금융업 대손충당금 세무처리: 기대손실(ECL) 모형 기준 충당금과 세무상 손금인정 한도의 차이 계산 방법. 과소 손금 처리 시 경정청구 가능","docId":"법인세과-2019-0188","docType":"ruling","source":"nts","publishedDate":"2019-03-20"},
    "moleg:law:폐기물관리법-18:2022-01-01": {"body":"폐기물관리법 제18조: 사업장 폐기물 처리 의무. 의무 처리비용은 사업 관련 비용으로 장애인고용부담금 판례 법리 유추 시 손금산입 가능성","docId":"폐기물관리법-18","docType":"law","source":"moleg","publishedDate":"2022-01-01"},
    "nts:ruling:서면-2022-법규-0512:2022-11-30": {"body":"해외 파견 R&D 인력의 본사 부담 인건비 세액공제: 파견 계약 명확 시 국내 기업부설연구소 인건비로 포함 가능. 조특법 §10 적용 요건","docId":"서면-2022-법규-0512","docType":"ruling","source":"nts","publishedDate":"2022-11-30"},
    "moleg:law:에너지이용합리화법-35:2021-04-20": {"body":"에너지이용합리화법 제35조: 에너지 다소비 사업자 열병합발전·폐열회수 의무. 해당 설비는 조특법 §25의2 에너지절약시설 세액공제 대상","docId":"에너지이용합리화법-35","docType":"law","source":"moleg","publishedDate":"2021-04-20"},
    "nts:ruling:법인세과-2021-0099:2021-02-25": {"body":"부동산 개발 착수 전 지질조사·환경영향평가 비용 처리: 사업 타당성 검토 목적 지출은 수익적지출로 즉시 손금 가능. 자본화(토지원가) 의무 없음","docId":"법인세과-2021-0099","docType":"ruling","source":"nts","publishedDate":"2021-02-25"},
    "nts:ruling:서면-2020-법규-0789:2020-10-15": {"body":"지주회사 완전자회사 청산 시 주식 처분손실 손금산입: 수입배당금 익금불산입 이력 있는 경우 처분손실 손금불산입 범위 산정 방법","docId":"서면-2020-법규-0789","docType":"ruling","source":"nts","publishedDate":"2020-10-15"},
    "moleg:law:항공사업법-61의2:2022-06-10": {"body":"항공사업법 제61조의2: 지속가능항공연료(SAF) 사용 의무화 근거. SAF 혼합·저장 설비는 에너지절약시설 고시 해당 검토 필요","docId":"항공사업법-61의2","docType":"law","source":"moleg","publishedDate":"2022-06-10"},
    # 과징금 손금산입
    "nts:ruling:법인세과-2024-0088:2024-07-01": {
        "body": "공정거래위원회 부과 과징금의 손금 해당 여부: 법인세법 §21 1호 손금불산입 대상은 벌금·과료·가산세에 한하며, 행정목적의 과징금은 개별 검토 필요. 절차위반 과징금의 손금 해당 가능성",
        "docId": "법인세과-2024-0088",
        "docType": "ruling",
        "source": "nts",
        "publishedDate": "2024-07-01",
    },
}

# source 식별자 → 화이트리스트 도메인 매핑
_SOURCE_DOMAIN: dict[str, str] = {
    "moleg":  "law.go.kr",
    "scourt": "glaw.scourt.go.kr",
    "nts":    "nts.go.kr",
    "tt":     "tt.go.kr",
}


# ---------------------------------------------------------------------------
# CitationAdapter
# ---------------------------------------------------------------------------

class CitationAdapter:
    """결정론적 citation token 발급 및 mock registry 조회 어댑터."""

    WHITELIST: frozenset[str] = frozenset(
        {"law.go.kr", "glaw.scourt.go.kr", "nts.go.kr", "tt.go.kr"}
    )

    # retry 설정
    _RETRY_DELAYS: tuple[int, ...] = (3, 9)  # 초 단위

    def __init__(self) -> None:
        # runtime registry: MOCK_REGISTRY 복사본 + register_mock으로 추가 가능
        self._registry: dict[str, dict] = deepcopy(MOCK_REGISTRY)

    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------

    def issue_token(
        self,
        source: str,
        doc_type: str,
        doc_id: str,
        date: str,
        body: str,
    ) -> str:
        """순수 함수: citationToken 발급.

        형식: {source}:{docType}:{docId}:{YYYY-MM-DD}:{sha256_8chars}

        Parameters
        ----------
        source:   "nts" | "scourt" | "moleg" | "tt"
        doc_type: "ruling" | "case" | "law" | ...
        doc_id:   문서 식별자 (예: "서면-2023-법규-0142")
        date:     발행일 "YYYY-MM-DD"
        body:     본문 텍스트 (앞 500자로 해시 계산)
        """
        digest = hashlib.sha256(body[:500].encode("utf-8")).hexdigest()[:8]
        return f"{source}:{doc_type}:{doc_id}:{date}:{digest}"

    def lookup(self, token_key: str) -> dict:
        """Mock registry에서 문서 조회. retry 2회 (3s / 9s backoff).

        Parameters
        ----------
        token_key: "{source}:{docType}:{docId}:{date}" (해시 없는 4-파트 키)
                   또는 전체 5-파트 token — 앞 4파트만 사용해 조회.

        Returns
        -------
        {"citationStatus": "FOUND", "token": str, "doc": dict}
        또는
        {"citationStatus": "NO_CITATION", "token_key": str}
        """
        lookup_key = self._normalize_key(token_key)

        last_exc: Optional[Exception] = None
        attempts = [None] + list(self._RETRY_DELAYS)  # 첫 시도 + 2회 retry

        for attempt_idx, delay in enumerate(attempts):
            if delay is not None:
                time.sleep(delay)
            try:
                result = self._do_lookup(lookup_key)
                if result is not None:
                    doc = result
                    token = self.issue_token(
                        source=doc["source"],
                        doc_type=doc["docType"],
                        doc_id=doc["docId"],
                        date=doc["publishedDate"],
                        body=doc["body"],
                    )
                    return {"citationStatus": "FOUND", "token": token, "doc": deepcopy(doc)}
                # 등록되지 않은 키 → retry 없이 즉시 NO_CITATION
                break
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                continue

        return {"citationStatus": "NO_CITATION", "token_key": token_key}

    def register_mock(self, token_key: str, doc: dict) -> str:
        """Mock registry에 문서를 등록하고 발급된 token 문자열을 반환.

        Parameters
        ----------
        token_key: "{source}:{docType}:{docId}:{date}"
        doc:       body / docId / docType / source / publishedDate 포함 dict

        Returns
        -------
        발급된 citationToken 문자열
        """
        key = self._normalize_key(token_key)
        self._registry[key] = deepcopy(doc)
        token = self.issue_token(
            source=doc["source"],
            doc_type=doc["docType"],
            doc_id=doc["docId"],
            date=doc["publishedDate"],
            body=doc["body"],
        )
        return token

    def validate_token(self, token: str) -> bool:
        """토큰 형식 검증 + registry 존재 여부 확인.

        유효 조건:
        1. 콜론으로 분리 시 정확히 5파트
        2. source가 화이트리스트 도메인에 매핑 가능
        3. date 파트가 YYYY-MM-DD 형식
        4. sha256 파트가 8자리 소문자 hex
        5. 앞 4파트 키가 registry에 존재하고 body 해시가 일치
        """
        parts = token.split(":")
        if len(parts) != 5:
            return False

        source, doc_type, doc_id, date, sha_part = parts

        # 화이트리스트 검증
        if _SOURCE_DOMAIN.get(source) not in self.WHITELIST:
            return False

        # 날짜 형식 검증
        if not self._is_valid_date(date):
            return False

        # sha256 파트 형식 검증
        if len(sha_part) != 8 or not all(c in "0123456789abcdef" for c in sha_part):
            return False

        # registry 존재 + 해시 일치 검증
        key = f"{source}:{doc_type}:{doc_id}:{date}"
        doc = self._registry.get(key)
        if doc is None:
            return False

        expected = self.issue_token(
            source=doc["source"],
            doc_type=doc["docType"],
            doc_id=doc["docId"],
            date=doc["publishedDate"],
            body=doc["body"],
        )
        return token == expected

    def get_registry_snapshot(self) -> dict:
        """T4용 readOnly 스냅샷 반환 (deep copy)."""
        return deepcopy(self._registry)

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _normalize_key(self, token_key: str) -> str:
        """5파트 token이 들어오면 앞 4파트 key로 정규화."""
        parts = token_key.split(":")
        if len(parts) == 5:
            return ":".join(parts[:4])
        return token_key

    def _do_lookup(self, key: str) -> Optional[dict]:
        """registry 단순 조회. 없으면 None."""
        return self._registry.get(key)

    @staticmethod
    def _is_valid_date(date: str) -> bool:
        """YYYY-MM-DD 형식인지 간단 검증."""
        parts = date.split("-")
        if len(parts) != 3:
            return False
        year, month, day = parts
        return (
            len(year) == 4 and year.isdigit()
            and len(month) == 2 and month.isdigit()
            and len(day) == 2 and day.isdigit()
        )


# ---------------------------------------------------------------------------
# __main__ — 파일럿 3개 아이디어 토큰 발급 및 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    adapter = CitationAdapter()

    print("=" * 70)
    print("T0 CitationAdapter - 파일럿 fixture 토큰 발급 및 검증")
    print("=" * 70)

    all_pass = True
    for key, doc in MOCK_REGISTRY.items():
        token = adapter.register_mock(key, doc)
        valid = adapter.validate_token(token)
        status = "PASS" if valid else "FAIL"
        if not valid:
            all_pass = False
        print(f"[{status}] {token}")

    print("-" * 70)
    print(f"결과: {'전체 통과' if all_pass else '일부 실패'}")
    print()

    # lookup 테스트 (retry 없이 즉시 조회되는 등록 키)
    print("lookup 테스트 (지연 없음 — 등록된 키):")
    sample_key = "nts:ruling:서면-2023-법규-0142:2023-01-15"
    result = adapter.lookup(sample_key)
    print(f"  citationStatus : {result['citationStatus']}")
    if result["citationStatus"] == "FOUND":
        print(f"  token          : {result['token']}")
        print(f"  docId          : {result['doc']['docId']}")

    print()
    print("lookup 테스트 (미등록 키 → NO_CITATION):")
    missing_result = adapter.lookup("nts:ruling:존재하지않는:2099-01-01")
    print(f"  citationStatus : {missing_result['citationStatus']}")

    print()
    print("get_registry_snapshot 키 목록:")
    snapshot = adapter.get_registry_snapshot()
    for k in snapshot:
        print(f"  {k}")
