# 전세안심 (Jeonse Safety Analyzer)

한국 부동산 전/월세 계약 전 위험 분석 웹 서비스.

## 기능

- 주소 검색 → 전세/월세 선택 → 금액 입력 → 자동 위험 분석
- **전세가율 검사**: 시세 대비 전세금 비율 분석 (안전 <70% / 주의 70-85% / 위험 >85%)
- **건축물대장 검사**: 건물 용도 및 위반 여부 확인
- 종합 판정 + 항목별 상세 리포트 + 실행 지침 제공

## 기술 스택

- **프론트엔드**: Next.js (App Router) + Tailwind CSS
- **백엔드**: Python / FastAPI
- **데이터베이스**: PostgreSQL (API 응답 캐싱)
- **배포**: Vercel
- **주소 검색**: 카카오 우편번호 서비스
- **공공 데이터**: 공공데이터포털 (국토교통부 실거래가, 건축물대장)

## 시작하기

### 필수 조건

- Node.js 18+
- Python 3.10+
- 공공데이터포털 서비스 키 ([발급](https://www.data.go.kr))

### 환경 설정

```bash
cp .env.example .env
# .env 파일에 공공데이터포털 서비스 키 입력
```

### 프론트엔드 실행

```bash
cd frontend
bun install
bun dev
```

### 백엔드 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

## 공공데이터포털 서비스 키 발급

1. [공공데이터포털](https://www.data.go.kr) 회원가입
2. "아파트 매매 실거래가 상세 자료" API 활용 신청
3. "건축물대장 정보" API 활용 신청
4. 마이페이지에서 인증키 확인 (승인 1-3일 소요 가능)

## 면책 고지

본 서비스는 공공 데이터를 기반으로 한 **참고용 정보**이며, 법적 자문이 아닙니다.
