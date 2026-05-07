# 네이버 금융 주식 정보 크롤러 (Naver Finance Stock Crawler)

> `https://finance.naver.com/sise/sise_market_sum.naver` 의 주식 정보를 수집하는 Python 크롤러 예시

---

## 📁 디렉토리 구조

```
shopping.naver.com/
├── crawler.py              # 메인 크롤러 소스 코드
├── shopping_naver.yml      # 데이터셋 YAML 설정 파일 (zavod 호환)
├── shopping_naver.xml      # XML 스키마 및 샘플 출력 데이터
└── README.md               # 이 문서
```

---

## 🔧 사전 준비

### 필수 패키지 설치

```bash
pip install requests lxml
```

### (선택) zavod 프레임워크를 통한 실행 시

```bash
cd /path/to/Python-Crawling-Lab
pip install -e zavod/
```

---

## 🚀 실행 방법

### 1. 단독 실행 (Standalone)

```bash
cd shopping.naver.com

# 기본 실행 (시장: KOSPI, 1페이지)
python crawler.py

# 시장 지정
python crawler.py --market KOSDAQ

# 여러 페이지 수집
python crawler.py --market KOSPI --max-pages 3

# 출력 형식 지정
python crawler.py --market KOSPI --output-format json
python crawler.py --market KOSPI --output-format xml
python crawler.py --market KOSPI --output-format both
```

### 2. zavod 프레임워크를 통한 실행

```bash
zavod crawl shopping.naver.com/shopping_naver.yml
```

---

## 📊 출력 데이터

### JSON 출력 예시

```json
{
  "crawled_at": "2026-05-07T11:30:00+00:00",
  "total_count": 2,
  "stocks": [
    {
      "code": "005930",
      "name": "삼성전자",
      "market": "KOSPI",
      "current_price": 84200,
      "change_rate": 1.57,
      "volume": 15432109,
      "market_cap": 5026540,
      "crawled_at": "2026-05-07T11:30:00+00:00"
    }
  ]
}
```

### XML 출력 예시

`shopping_naver.xml` 파일을 참고하세요.

---

## 🏗️ 크롤링 방식

- **HTML 파싱 기반 크롤링**
  - 대상: `https://finance.naver.com/sise/sise_market_sum.naver`
  - 시가총액 테이블(`type_2`)의 종목 행을 파싱
  - 종목 코드, 종목명, 현재가, 등락률, 거래량, 시가총액 추출

---

## 📐 데이터 모델

| 필드 | 타입 | 설명 |
|------|------|------|
| `code` | str | 종목 코드 |
| `name` | str | 종목명 |
| `market` | str | 시장 구분 (`KOSPI`/`KOSDAQ`) |
| `current_price` | int | 현재가 (원) |
| `change_rate` | float | 등락률 (%) |
| `volume` | int | 거래량 |
| `market_cap` | int | 시가총액 |
| `crawled_at` | str | 크롤링 시각 (ISO 8601) |

---

## ⚠️ 주의사항

1. **이용약관 준수**: 네이버 금융의 이용약관 및 robots.txt를 확인하고 준수해야 합니다.
2. **요청 간격**: 서버에 과도한 부하를 주지 않도록 기본 딜레이를 두고 있습니다.
3. **학습 목적**: 이 크롤러는 학습 및 연구 목적의 예시 코드입니다.

---

## 📚 참고

- [네이버 금융](https://finance.naver.com/)
- [시가총액 페이지](https://finance.naver.com/sise/sise_market_sum.naver)
- [Python-Crawling-Lab 프로젝트 README](../README.md)
- [zavod 프레임워크 문서](../zavod/README.md)
