# Phoney War
## Game Design Document v2.0

> **대원칙**: Apple / Android / iOS / Android 상표명을 게임 내에서 직접 언급하지 않는다.
> 연상만 시킬 뿐, 명시하지 않는다. 이 원칙은 게임 UI, 마케팅, 카피, 능력명 전체에 적용.

---

## 1. 핵심 컨셉

**한 줄 요약**: Your phone picked a side. Will you fight for it?

**차별화 포인트**
1. **기기 강제 진영 배정** — User Agent 기반 자동 분류. 선택 없음.
2. **진영별 비대칭 게임플레이** — 게임 방식 자체가 다름 (집단 vs 개인)
3. **비대칭 능력 시스템** — Orchard는 모두 같은 능력, Jungle은 개인 선택
4. **실제 점유율 반영** — 인원 균형 안 맞춤. 지역별로 다른 양상이 그 자체로 콘텐츠
5. **시각적 정체성** — Orchard는 통일된 흰/은색, Jungle은 플레이어마다 다른 초록 계열

---

## 2. 진영 정의

### 🍎 The Orchard (집단주의)
- **모티프**: 잘 가꿔진 사유 과수원. 울타리 안, 통제된 아름다움.
- **영토 모델**: 공유 영토 1개 (모든 Orchard 유저가 함께 가꿈)
- **자원 풀**: 진영 전체 공유 (`orchard.sharedResource`)
- **행동 권한**: 누구나 Orchard 영토 어디든 클릭 가능
- **시각**: 흰색~실버 그라데이션 단일 영역. 개인 표시 없음.
- **폰트**: Cormorant Garamond (세리프, 미니멀)
- **HQ**: 1개 공유. 점령되면 진영 즉시 패배.
- **서사**: "The wall holds everything in. And everyone together."

### 🤖 The Jungle (개인주의)
- **모티프**: 통제 없이 뻗어나가는 정글. 다양하고 혼돈스럽고 강인함.
- **영토 모델**: 유저당 개인 영토 (각자 본진 보유)
- **자원 풀**: 개인별 (`user.resource`)
- **행동 권한**: 본인 영토에서만 행동. 다른 Jungle 유저 영토 공격 불가.
- **Jungle끼리 경쟁**: 빈 영토 선점 경쟁만 가능
- **시각**: 능력 선택에 따라 다른 초록 계열 색상 (아래 참조)
- **폰트**: Outfit (산세리프, 다양성)
- **HQ**: 유저 수만큼 존재. 개별 HQ 점령 시 그 유저만 탈락.
- **서사**: "No walls. No rules. Just growth."

### 진영 간 상호작용
- **Orchard → Jungle**: 인접한 어떤 Jungle 유저 영토든 공격 가능
- **Jungle → Orchard**: 인접한 Orchard 공유 영토 공격 가능
- **Jungle → Jungle**: 직접 공격 불가. 빈 영토 선점 경쟁만.

---

## 3. 게임 구조

### 세션 구성 (Phase 2 기준)
- **세션 길이**: 15~20분 고정 타이머
- **시작**: 빈 맵, 양 진영 HQ 배치
- **종료**: 타이머 만료 시 영토 점유율 높은 진영 승리
- **즉시 종료 조건**: Orchard HQ 점령 → Jungle 승리 / 모든 Jungle 유저 탈락 → Orchard 승리

### Final Rush (마지막 3분)
- 세션 종료 3분 전 자동 발동
- 모든 자원 비용 -30%, 공격 데미지 +1
- 화면에 "⚡ FINAL RUSH" 표시 + 카운트다운
- 극적인 결말 연출

### PC 유저 처리 (관전 모드)
- PC/Mac 접속 → 게임 차단 대신 **관전 화면**으로 전환
- 실시간 지도(읽기 전용) + 점유율 바 + 이벤트 피드 표시
- QR코드 + "Join on mobile" CTA
- PC 유저가 SNS에 스크린샷 → 자동 모객

---

## 4. 게임 메커니즘

### 맵
- 헥사곤 그리드 (참여 인원에 따라 가변)
- 6~20명: 12×10 / 50~100명: 25×20 / 100명+: 35×30
- Orchard HQ: 맵 좌측 고정
- Jungle HQ들: 맵 우측 분산 배치 (랜덤)

### 자원 시스템 (입증된 메커니즘 적용)
- **자동 소득**: 보유 영토 1헥스당 틱마다 +0.1 자원 자동 생성
- **클릭 수집**: 본인/진영 영토 클릭 → 즉시 +1 자원 추가 (Orchard +1.5)
- 영토를 많이 보유할수록 자원이 빠르게 쌓임 → 확장이 경제적으로 의미 있음

### 액션 3가지
| 액션 | Orchard 비용 | Jungle 비용 | 조건 |
|------|------------|------------|------|
| **Expand** (확장) | shared -5 | personal -5 | 인접한 빈 헥스 |
| **Attack** (공격) | shared -12 | personal -12 | 인접한 적 헥스 |
| **Gather** (수집) | +1.5 shared | +1.0 personal | 본인/진영 헥스 클릭 |

### 영토 강도
- 일반 헥스: Strength 1
- HQ: Strength 5
- 공격 1회 = Strength -1 → 0이 되면 점령 전환
- Orchard HQ: 점령 즉시 게임 종료
- Jungle HQ 점령: 해당 유저 탈락, 영토 → neutral, HQ → Orchard 소유

### 탈락 처리
- Jungle HQ 점령 시: 일반 영토는 neutral로 전환, HQ는 Orchard 소유
- 탈락한 Jungle 유저: 새 HQ로 재입장 가능 (Phase 2에서는 허용)

### UI 원칙 (한눈에 위험도 파악)
- 상단 고정: Orchard XX% ████░░ Jungle XX% 실시간 바
- HQ 위협 시: 해당 HQ 헥스 펄싱 애니메이션 + 경고 색상
- 공격 시: 피격 헥스 흔들림 + float "-1" 텍스트
- 확장 시: 색상 fill 애니메이션 (0.3초)
- 세션 타이머: 항상 표시. 마지막 3분은 붉은색으로 전환

---

## 5. 능력 시스템

### 🍎 The Orchard — 공유 능력 3개 (모든 Orchard 유저 동일)

| 능력명 | 효과 | 쿨다운 | 원전 |
|--------|------|--------|------|
| **AirDrop** | 인접 아군에게 자원 즉시 전송 | 30초 | AirDrop 무선 전송 |
| **Ecosystem Lock** | Orchard 헥스 5개 이상 연결 시 경계 Strength +1 자동 (패시브) | 패시브 | Walled Garden = 안으로 갈수록 강해짐 |
| **iCloud Restore** | Orchard HQ Strength 1 위협 시 즉시 Strength 3 복구 (세션당 1회) | 1회 | iCloud 백업 복구 |

### 🤖 The Jungle — 공통 능력 2개 + 선택 능력 5개 중 1개

**공통 능력 (모든 Jungle 유저)**

| 능력명 | 효과 | 원전 |
|--------|------|------|
| **Open Source** | 적 HQ 주변 헥스 Strength 항상 표시 | 오픈소스 = 투명성 |
| **Sideload** | 이벤트 아이템 즉시 사용 가능 | 사이드로딩 = 제한 없는 설치 |

**선택 능력 (게임 시작 시 1개 선택, 변경 불가)**

| # | 능력명 | 효과 | 헥스 색상 | 원전 | 스타일 |
|---|--------|------|---------|------|--------|
| 1 | **Custom ROM** | 자원 수집 +30% | 라임 #22C55E | 커스텀 롬 = 성능 극대화 | 경제형 |
| 2 | **Root** | 맵 전체 모든 헥스 Strength 수치 공개 | 포레스트 #16A34A | 루팅 = 시스템 깊숙이 접근 | 정보형 |
| 3 | **Overclock** | 20초간 자원 2배, 이후 5초 쿨다운 | 네온 #4ADE80 | 오버클럭 = 극한 성능 + 리스크 | 버스트형 |
| 4 | **Stock** | 모든 액션 비용 -15% | 다크 #15803D | Stock Android = 군더더기 없는 효율 | 지구력형 |
| 5 | **Dev Mode** | 마지막 액션 취소 가능 (3분마다 1회) | 청록 #14B8A6 | 개발자 옵션 = 숨겨진 기능 | 컨트롤형 |

---

## 6. 언어 지원 (7개)

| 언어 | 국가/지역 | iOS% | Android% | 우선순위 |
|------|---------|------|---------|---------|
| **영어** | 미국, 영국, 캐나다, 호주 | 52~57% | 43~48% | Phase 2 필수 |
| **중국어(간체)** | 중국 | 26% | 74% | Phase 2 필수 |
| **중국어(번체)** | 홍콩, 대만 | 48~50% | 50~52% | Phase 2 필수 |
| **일본어** | 일본 | 68% | 32% | Phase 2 필수 |
| **한국어** | 한국 | 30% | 70% | Phase 2 필수 |
| **스페인어** | 라틴아메리카 20개국 | 16% | 84% | Phase 3 |
| **포르투갈어** | 브라질 | 14% | 86% | Phase 3 |
| **아랍어** | UAE, 사우디 (iOS/Android 42/58 균형) | 42% | 58% | Phase 3 |

### 일본 vs 중국 마케팅 앵글
- 일본 (iOS 68%) → Orchard 진영 압도적 → "Japan is holding the Orchard"
- 중국 (Android 74%) → Jungle 진영 압도적 → "China is the Jungle"
- 두 커뮤니티에서 "기기 문화 대결"로 프레이밍 (국가 갈등이 아닌 기기 문화로 포지셔닝)

---

## 7. 마케팅 원칙

### 상표 회피 대원칙
| 표현하고 싶은 것 | 금지 | 허용 |
|--------------|------|------|
| Apple | "Apple", 공식 로고 | "The Orchard", 🍎 이모지, "Walled Garden" |
| Android | "Android", Bugdroid | "The Jungle", 🤖 이모지, "Open Source" |
| iPhone | "iPhone" | "your device", "the silver side" |
| iOS vs Android | 직접 표기 | "two worlds", "your OS chose your side" |

### 핵심 태그라인
- **메인**: *"Your phone picked a side. Will you fight for it?"*
- **서브**: *"One URL. Two worlds. No choice."*
- **Orchard**: *"The wall holds everything in. And everyone together."*
- **Jungle**: *"No walls. No rules. Just growth."*

### 채널별 전략
- **Reddit**: r/apple + r/Android 동시 포스팅 (각각 다른 톤)
- **Twitter/X**: 실시간 점유율 + FOMO 구조 ("Orchard is losing, get in here")
- **Hacker News**: Show HN으로 기술 미디어 픽업 유도
- **론칭 타이밍**: Apple 신제품 발표 직후 (9월) — iOS/Android 논쟁 최고조 시점

### 도메인
- 1순위: `phoneywar.io`
- 2순위: `playphoneywar.com`

---

## 8. 기술 아키텍처

### 스택
- **클라이언트**: Vanilla JS + HTML5 Canvas
- **서버**: Node.js + Socket.io
- **호스팅**: Fly.io (ICN 서울 리전, 무료 티어)
- **DB**: Phase 2 메모리만. Phase 3에서 Postgres 도입.

### 디렉토리 구조
```
phoney-war/
├── client/
│   ├── index.html
│   ├── style.css
│   ├── game.js           # 게임 로직 + 서버 동기화
│   ├── render.js         # Canvas 렌더링
│   └── network.js        # Socket.io 클라이언트
├── server/
│   ├── index.js          # 서버 진입점
│   ├── gameState.js      # 권위적 게임 상태
│   ├── abilities.js      # 능력 시스템 검증
│   ├── session.js        # 세션 관리
│   └── deviceDetect.js   # UA 검증
├── shared/
│   ├── constants.js      # 공유 상수
│   └── hexMath.js        # 헥사곤 수학 (서버+클라 공용)
├── package.json
├── Dockerfile
├── fly.toml
└── README.md
```

### 핵심 데이터 구조
```javascript
// 헥사곤 셀
{ q, r, owner: 'orchard'|userId|null, faction: 'orchard'|'jungle'|null, strength: 1-5, isHQ: bool }

// 유저
{ id, faction, resource, hq:{q,r}|null, isEliminated: bool, ability: 'customRom'|'root'|'overclock'|'stock'|'devMode'|null }

// 진영
{
  orchard: { sharedResource: number, territoryCount: number },
  jungle:  { territoryCount: number, activeUsers: string[] }
}
```

### 소켓 프로토콜
```javascript
// Client → Server
socket.emit('joinSession', { sessionId, userAgent, abilityChoice })
socket.emit('action', { type: 'gather'|'expand'|'attack', q, r })

// Server → Client
socket.emit('joined',      { userId, faction, ability, initialState })
socket.emit('rejected',    { reason: 'pc-blocked'|'session-full' })
socket.emit('stateUpdate', { changes:[], resourcePatch, timestamp })
socket.emit('actionResult',{ success: bool, error?: string })
socket.emit('finalRush',   { timeRemaining: 180 })
socket.emit('sessionEnd',  { winner, finalStats })
```

### 동기화
- 200ms 틱: 변경된 셀 + 자원만 broadcast
- 5초마다 전체 스냅샷 (드리프트 방지)
- Rate limit: 소켓당 5 actions/sec

---

## 9. 팀 구성

| 부서 | 역할 | 모델 |
|------|------|------|
| **총괄 (GM)** | 우선순위, 충돌 조율, 최종 승인 | Opus |
| **기획** | GDD 유지, 메커니즘 설계 | Sonnet |
| **마케팅** | 카피, SNS, 바이럴 설계 | Sonnet |
| **디자인** | 헥스 비주얼, 진영 색상, UX | Sonnet |
| **법률** | 상표, 약관, 개인정보 | Opus |
| **코딩** | 서버/클라이언트 구현 | Sonnet |
| **QA** | 기능 테스트, 멀티탭 시뮬 | Haiku |
| **리뷰** | 코드리뷰, 출시 전 검토 | Opus |
| **백오피스** | 배포, 서버 운영, 비용 | Sonnet |
| **보안** | UA 방어, WebSocket 보안 | Opus |
| **현지화** | 7개 언어 번역, 문화 검토 | Sonnet |
| **데이터/분석** | 세션 분석, 이탈 지점 파악 | Sonnet |

---

## 10. 단계별 로드맵

### Phase 1 ✅ 완료
- 헥사곤 프로토타입, AI 상대, 기기 감지

### Phase 2 (지금) — 멀티플레이어 + 비대칭
- Socket.io 서버 구축
- Orchard 공유영토 / Jungle 개인영토 메커니즘
- 능력 시스템 구현
- 15~20분 타이머 + Final Rush
- 관전 모드 (PC)
- 영어 + 한국어 우선
- Fly.io 배포

### Phase 3 — 언어 확장 + 세션 이벤트
- 스페인어, 포르투갈어, 아랍어 추가
- 24~72시간 세션 자동 시작/종료
- 기여도 카드 SNS 공유
- 일본/중국 마케팅 앵글 론칭

### Phase 4 — 스케일
- 100~500명 동접 대응
- 보안 강화
- OG 이미지, SEO

### Phase 5 — 확장
- 시즌제, 누적 통계
- 스폰서십 검토

---

## 11. 리스크 & 완화

| 리스크 | 완화책 |
|--------|--------|
| Jungle 압승 반복 | "열세 진영의 분투" 자체를 컨셉으로 흡수. Final Rush로 역전 가능성 |
| UA 위조 | 서버 재검증, 100% 방지 불가 인정. 일반 유저 기준 충분히 강제됨 |
| Apple 상표 클레임 | 직접 명시 없음 + "팬메이드 패러디" 면책문구 |
| 능력 밸런스 붕괴 | Root/Overclock 조합 OP 시 서버 핫픽스로 수치 조정 |
| 세션 중반 이탈 | 자동 소득 + Final Rush로 중반 유지. 15~20분 단세션으로 이탈 최소화 |

---

## 12. 미결 사항

- [ ] 게임 내 닉네임 vs 익명 ID
- [ ] Jungle 탈락 후 재입장 대기 시간 (즉시 vs 30초 대기)
- [ ] 기여도 카드 디자인 (Phase 3)
- [ ] 인원 불균형 시 능력 수치 자동 조정 여부
- [ ] `phoneywar.io` 도메인 가용 여부 확인
