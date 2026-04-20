# 네이버 쇼핑 상품 크롤러 (Naver Shopping Crawler)

> `https://shopping.naver.com/ns/home` 의 상품 정보를 수집하는 Python 크롤러 예시

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

가장 간단한 실행 방법입니다. `crawler.py`를 직접 실행하여 상품 데이터를 수집합니다.

```bash
cd shopping.naver.com

# 기본 실행 (키워드: "노트북", 1페이지)
python crawler.py

# 키워드 지정
python crawler.py --keyword "무선이어폰"

# 여러 페이지 수집
python crawler.py --keyword "운동화" --max-pages 3

# 출력 형식 지정
python crawler.py --keyword "노트북" --output-format json
python crawler.py --keyword "노트북" --output-format xml
python crawler.py --keyword "노트북" --output-format both

# 크롤링 방식 지정
python crawler.py --keyword "노트북" --method api    # API만 사용
python crawler.py --keyword "노트북" --method html   # HTML 파싱만 사용
python crawler.py --keyword "노트북" --method auto   # API 우선, 실패 시 HTML
```

### 2. zavod 프레임워크를 통한 실행

이 프로젝트의 표준 방식인 zavod 프레임워크로 실행합니다.

```bash
zavod crawl shopping.naver.com/shopping_naver.yml
```

---

## 📊 출력 데이터

### JSON 출력 예시

```json
{
  "crawled_at": "2026-04-20T07:30:00+00:00",
  "total_count": 40,
  "products": [
    {
      "product_id": "12345678",
      "title": "삼성전자 갤럭시북4 프로 노트북",
      "price": 1890000,
      "image_url": "https://shopping-phinf.pstatic.net/main_xxxx/sample.jpg",
      "product_url": "https://search.shopping.naver.com/gate.nhn?id=12345678",
      "mall_name": "삼성전자 공식스토어",
      "category": "디지털/가전",
      "review_count": 1523,
      "rating": 4.8,
      "delivery_fee": "무료배송",
      "crawled_at": "2026-04-20T07:30:00+00:00",
      "keyword": "노트북"
    }
  ]
}
```

### XML 출력 예시

`shopping_naver.xml` 파일을 참고하세요. 주요 구조:

```xml
<NaverShoppingProducts crawledAt="..." totalCount="...">
  <Product id="12345678">
    <Title>삼성전자 갤럭시북4 프로 노트북</Title>
    <Price>1890000</Price>
    <MallName>삼성전자 공식스토어</MallName>
    <Category>디지털/가전</Category>
    <ReviewCount>1523</ReviewCount>
    <Rating>4.8</Rating>
    ...
  </Product>
</NaverShoppingProducts>
```

---

## 🏗️ 크롤링 방식

### 방식 1: API 기반 크롤링 (권장)

네이버 쇼핑 내부 API 엔드포인트에 HTTP GET 요청을 보내 JSON 응답을 파싱합니다.

- **엔드포인트**: `https://search.shopping.naver.com/api/search/all`
- **장점**: 구조화된 JSON 데이터, 안정적인 필드 구조
- **단점**: API 구조 변경 시 파서 업데이트 필요

### 방식 2: HTML 파싱 기반 크롤링

검색 결과 페이지의 HTML을 다운로드하여 lxml로 파싱합니다.

- **대상**: `https://search.shopping.naver.com/search/all`
- **파싱 순서**:
  1. `__NEXT_DATA__` 스크립트 태그에서 JSON 추출 시도
  2. (fallback) 상품 DOM 요소 직접 XPath 파싱

---

## 📐 데이터 모델

| 필드 | 타입 | 설명 |
|------|------|------|
| `product_id` | str | 상품 고유 ID |
| `title` | str | 상품명 |
| `price` | int | 가격 (원) |
| `image_url` | str | 상품 이미지 URL |
| `product_url` | str | 상품 상세 페이지 URL |
| `mall_name` | str | 판매처(쇼핑몰) 이름 |
| `category` | str | 상품 카테고리 |
| `review_count` | int | 리뷰 수 |
| `rating` | float | 평점 (5점 만점) |
| `delivery_fee` | str | 배송비 정보 |
| `crawled_at` | str | 크롤링 시각 (ISO 8601) |
| `keyword` | str | 검색에 사용된 키워드 |

---

## 🔗 이 프로젝트와의 관계

이 크롤러는 `Python-Crawling-Lab` 프로젝트의 크롤링 패턴을 따릅니다:

| 항목 | 프로젝트 표준 (datasets/) | 이 크롤러 (shopping.naver.com/) |
|------|--------------------------|-------------------------------|
| 설정 파일 | `*.yml` | `shopping_naver.yml` |
| 크롤러 코드 | `crawler.py` | `crawler.py` |
| 진입 함수 | `crawl(context)` | `crawl(context)` + `main()` |
| 출력 형식 | FtM Entity JSON | JSON / XML |
| 프레임워크 | zavod Context | zavod 호환 + 단독 실행 가능 |

---

## ⚠️ 주의사항

1. **이용약관 준수**: 네이버 쇼핑의 이용약관 및 robots.txt를 확인하고 준수해야 합니다.
2. **요청 간격**: 서버에 과도한 부하를 주지 않도록 기본 1.5초의 딜레이를 두고 있습니다.
3. **학습 목적**: 이 크롤러는 학습 및 연구 목적의 예시 코드입니다. 상업적 목적의 대량 크롤링은 네이버의 정책에 따라 제한될 수 있습니다.
4. **API 변경**: 네이버 쇼핑의 내부 API 구조는 사전 공지 없이 변경될 수 있습니다.

---

## 📚 참고

- [네이버 쇼핑 홈](https://shopping.naver.com/ns/home)
- [네이버 개발자 센터 - 쇼핑 검색 API](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md)
- [Python-Crawling-Lab 프로젝트 README](../README.md)
- [zavod 프레임워크 문서](../zavod/README.md)
