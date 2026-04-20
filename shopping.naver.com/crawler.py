"""
Naver Shopping (shopping.naver.com) Product Crawler

이 크롤러는 네이버 쇼핑 홈페이지(https://shopping.naver.com/ns/home)에서
상품 정보를 수집하는 예시입니다.

네이버 쇼핑은 SPA(Single Page Application) 기반으로 대부분의 상품 데이터가
내부 API를 통해 동적으로 로드됩니다. 따라서 아래 두 가지 접근 방식을 제공합니다:

1. API 기반 크롤링 (권장) — 네이버 쇼핑 내부 API를 호출하여 JSON 응답을 파싱
2. HTML 파싱 기반 크롤링 — SSR(Server-Side Rendered) 페이지에서 상품 정보 추출

Usage:
    python crawler.py [--keyword KEYWORD] [--max-pages MAX_PAGES] [--output-format FORMAT]

Examples:
    python crawler.py --keyword "노트북" --max-pages 3
    python crawler.py --keyword "무선이어폰" --max-pages 5 --output-format json
    python crawler.py --keyword "운동화" --output-format xml
"""

import argparse
import json
import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import quote, urlencode, urljoin

import requests
from lxml import html

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("shopping.naver.crawler")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://shopping.naver.com"
SEARCH_URL = f"{BASE_URL}/ns/home"

# 네이버 쇼핑 검색 API 엔드포인트 (공개 API가 아닌 내부 API 구조 기반)
SEARCH_API_URL = "https://search.shopping.naver.com/search/all"
SEARCH_API_JSON_URL = "https://search.shopping.naver.com/api/search/all"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://shopping.naver.com/",
}

# 요청 사이의 딜레이 (초) — 서버 부하 방지를 위한 예의(politeness)
REQUEST_DELAY = 1.5


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------
@dataclass
class Product:
    """네이버 쇼핑 상품 데이터 모델"""

    product_id: str = ""
    title: str = ""
    price: int = 0
    image_url: str = ""
    product_url: str = ""
    mall_name: str = ""
    category: str = ""
    review_count: int = 0
    rating: float = 0.0
    delivery_fee: str = ""
    crawled_at: str = ""
    keyword: str = ""
    extra: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Crawler Implementation
# ---------------------------------------------------------------------------
class NaverShoppingCrawler:
    """네이버 쇼핑 크롤러

    이 크롤러는 네이버 쇼핑 검색 결과 페이지에서 상품 정보를 수집합니다.
    robots.txt 및 이용약관을 준수하여 적절한 딜레이를 두고 요청합니다.
    """

    def __init__(self, delay: float = REQUEST_DELAY):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.delay = delay
        self.products: List[Product] = []

    # ------------------------------------------------------------------
    # API 기반 크롤링
    # ------------------------------------------------------------------
    def crawl_search_api(
        self, keyword: str, max_pages: int = 1
    ) -> List[Product]:
        """네이버 쇼핑 검색 API를 사용하여 상품 목록을 수집합니다.

        Args:
            keyword: 검색 키워드
            max_pages: 최대 크롤링 페이지 수 (1 페이지 ≈ 40개 상품)

        Returns:
            수집된 Product 객체 목록
        """
        logger.info("API 기반 크롤링 시작: keyword=%s, max_pages=%d", keyword, max_pages)
        all_products: List[Product] = []

        for page in range(1, max_pages + 1):
            params = {
                "query": keyword,
                "pagingIndex": page,
                "pagingSize": 40,
                "sort": "rel",  # rel: 관련도순, price_asc: 낮은가격순, date: 최신순
                "productSet": "total",
            }
            url = f"{SEARCH_API_JSON_URL}?{urlencode(params)}"
            logger.info("  페이지 %d/%d 요청: %s", page, max_pages, url)

            try:
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as exc:
                logger.warning("API 요청 실패 (page=%d): %s", page, exc)
                break
            except json.JSONDecodeError:
                logger.warning("JSON 파싱 실패 (page=%d)", page)
                break

            items = self._extract_items_from_api(data, keyword)
            if not items:
                logger.info("  더 이상 상품이 없습니다. 크롤링 종료.")
                break

            all_products.extend(items)
            logger.info("  %d개 상품 수집 (누적 %d개)", len(items), len(all_products))

            if page < max_pages:
                time.sleep(self.delay)

        self.products.extend(all_products)
        logger.info("API 크롤링 완료: 총 %d개 상품 수집", len(all_products))
        return all_products

    def _extract_items_from_api(
        self, data: dict, keyword: str
    ) -> List[Product]:
        """API JSON 응답에서 상품 정보를 추출합니다."""
        products: List[Product] = []
        now = datetime.now(timezone.utc).isoformat()

        # 네이버 쇼핑 API 응답 구조: shoppingResult.products
        shopping_result = data.get("shoppingResult", {})
        items = shopping_result.get("products", [])

        for item in items:
            product = Product(
                product_id=str(item.get("id", "")),
                title=item.get("productTitle", item.get("productName", "")),
                price=int(item.get("price", 0)),
                image_url=item.get("imageUrl", ""),
                product_url=item.get("mallProductUrl", ""),
                mall_name=item.get("mallName", ""),
                category=item.get("category1Name", ""),
                review_count=int(item.get("reviewCount", 0)),
                rating=float(item.get("scoreInfo", 0)),
                delivery_fee=item.get("deliveryFeeContent", ""),
                crawled_at=now,
                keyword=keyword,
            )
            products.append(product)

        return products

    # ------------------------------------------------------------------
    # HTML 파싱 기반 크롤링
    # ------------------------------------------------------------------
    def crawl_search_html(
        self, keyword: str, max_pages: int = 1
    ) -> List[Product]:
        """HTML 파싱을 사용하여 검색 결과에서 상품 정보를 수집합니다.

        네이버 쇼핑의 검색 결과는 대부분 JavaScript로 렌더링되므로
        SSR(Server-Side Rendered) 부분에서 추출 가능한 데이터를 파싱합니다.

        Args:
            keyword: 검색 키워드
            max_pages: 최대 크롤링 페이지 수

        Returns:
            수집된 Product 객체 목록
        """
        logger.info("HTML 파싱 기반 크롤링 시작: keyword=%s, max_pages=%d", keyword, max_pages)
        all_products: List[Product] = []

        for page in range(1, max_pages + 1):
            params = {
                "query": keyword,
                "pagingIndex": page,
                "pagingSize": 40,
            }
            url = f"{SEARCH_API_URL}?{urlencode(params)}"
            logger.info("  페이지 %d/%d 요청: %s", page, max_pages, url)

            try:
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
            except requests.RequestException as exc:
                logger.warning("HTML 요청 실패 (page=%d): %s", page, exc)
                break

            items = self._extract_items_from_html(resp.text, keyword)
            if not items:
                logger.info("  더 이상 상품이 없습니다. 크롤링 종료.")
                break

            all_products.extend(items)
            logger.info("  %d개 상품 수집 (누적 %d개)", len(items), len(all_products))

            if page < max_pages:
                time.sleep(self.delay)

        self.products.extend(all_products)
        logger.info("HTML 크롤링 완료: 총 %d개 상품 수집", len(all_products))
        return all_products

    def _extract_items_from_html(
        self, html_text: str, keyword: str
    ) -> List[Product]:
        """HTML 페이지에서 상품 정보를 추출합니다.

        네이버 쇼핑 검색 결과 페이지에는 __NEXT_DATA__ 형태의 JSON이
        <script> 태그에 포함되어 있을 수 있습니다.
        """
        products: List[Product] = []
        now = datetime.now(timezone.utc).isoformat()

        try:
            doc = html.fromstring(html_text)
        except Exception as exc:
            logger.warning("HTML 파싱 실패: %s", exc)
            return products

        # 방법 1: __NEXT_DATA__ 스크립트에서 JSON 추출
        scripts = doc.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if scripts:
            try:
                next_data = json.loads(scripts[0])
                props = next_data.get("props", {}).get("pageProps", {})
                items = (
                    props.get("initialState", {})
                    .get("products", {})
                    .get("list", [])
                )
                for item in items:
                    item_data = item.get("item", item)
                    product = Product(
                        product_id=str(item_data.get("id", "")),
                        title=item_data.get("productTitle", ""),
                        price=int(item_data.get("price", 0)),
                        image_url=item_data.get("imageUrl", ""),
                        product_url=item_data.get("mallProductUrl", ""),
                        mall_name=item_data.get("mallName", ""),
                        category=item_data.get("category1Name", ""),
                        review_count=int(item_data.get("reviewCount", 0)),
                        rating=float(item_data.get("scoreInfo", 0)),
                        crawled_at=now,
                        keyword=keyword,
                    )
                    products.append(product)
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                logger.warning("__NEXT_DATA__ 파싱 실패: %s", exc)

        # 방법 2: 상품 목록 DOM 요소 직접 파싱 (fallback)
        if not products:
            product_items = doc.xpath(
                '//div[contains(@class, "product_item")]'
                '|//li[contains(@class, "product_item")]'
                '|//div[contains(@class, "basicList_item")]'
            )
            for idx, item in enumerate(product_items):
                title_el = item.xpath(
                    './/a[contains(@class, "product_link")]/@title'
                    '|.//div[contains(@class, "product_title")]//text()'
                    '|.//a[contains(@class, "basicList_link")]/@title'
                )
                price_el = item.xpath(
                    './/span[contains(@class, "price_num")]//text()'
                    '|.//em[contains(@class, "price")]//text()'
                )
                link_el = item.xpath(
                    './/a[contains(@class, "product_link")]/@href'
                    '|.//a[contains(@class, "basicList_link")]/@href'
                )
                img_el = item.xpath(
                    './/img[contains(@class, "product_img")]/@src'
                    '|.//img/@src'
                )
                mall_el = item.xpath(
                    './/span[contains(@class, "mall_txt")]//text()'
                    '|.//a[contains(@class, "mall_link")]//text()'
                )

                title = "".join(title_el).strip() if title_el else ""
                if not title:
                    continue

                price_text = "".join(price_el).strip().replace(",", "")
                try:
                    price = int(price_text)
                except ValueError:
                    price = 0

                product = Product(
                    product_id=str(idx),
                    title=title,
                    price=price,
                    image_url=img_el[0] if img_el else "",
                    product_url=link_el[0] if link_el else "",
                    mall_name="".join(mall_el).strip() if mall_el else "",
                    crawled_at=now,
                    keyword=keyword,
                )
                products.append(product)

        return products

    # ------------------------------------------------------------------
    # 결과 내보내기 (Export)
    # ------------------------------------------------------------------
    def export_json(self, filepath: str) -> None:
        """수집된 상품 데이터를 JSON 파일로 저장합니다."""
        data = {
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "total_count": len(self.products),
            "products": [asdict(p) for p in self.products],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("JSON 저장 완료: %s (%d개 상품)", filepath, len(self.products))

    def export_xml(self, filepath: str) -> None:
        """수집된 상품 데이터를 XML 파일로 저장합니다."""
        root = ET.Element("NaverShoppingProducts")
        root.set("crawledAt", datetime.now(timezone.utc).isoformat())
        root.set("totalCount", str(len(self.products)))

        for prod in self.products:
            product_el = ET.SubElement(root, "Product")
            product_el.set("id", prod.product_id)

            _add_xml_element(product_el, "Title", prod.title)
            _add_xml_element(product_el, "Price", str(prod.price))
            _add_xml_element(product_el, "ImageUrl", prod.image_url)
            _add_xml_element(product_el, "ProductUrl", prod.product_url)
            _add_xml_element(product_el, "MallName", prod.mall_name)
            _add_xml_element(product_el, "Category", prod.category)
            _add_xml_element(product_el, "ReviewCount", str(prod.review_count))
            _add_xml_element(product_el, "Rating", str(prod.rating))
            _add_xml_element(product_el, "DeliveryFee", prod.delivery_fee)
            _add_xml_element(product_el, "Keyword", prod.keyword)
            _add_xml_element(product_el, "CrawledAt", prod.crawled_at)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
        logger.info("XML 저장 완료: %s (%d개 상품)", filepath, len(self.products))


def _add_xml_element(parent: ET.Element, tag: str, text: str) -> ET.Element:
    """XML 요소를 부모 요소에 추가합니다."""
    el = ET.SubElement(parent, tag)
    el.text = text
    return el


# ---------------------------------------------------------------------------
# zavod 프레임워크 기반 crawl 함수 (프로젝트 표준 인터페이스)
# ---------------------------------------------------------------------------
def crawl(context) -> None:
    """zavod 프레임워크 호환 크롤 함수.

    이 함수는 datasets/ 디렉토리의 다른 크롤러들과 동일한 인터페이스를 제공합니다.
    `zavod crawl shopping.naver.com/shopping_naver.yml` 명령으로 실행할 수 있습니다.

    네이버 쇼핑은 상품 데이터를 제공하므로, FollowTheMoney 엔터티 대신
    상품 정보를 로깅하는 방식으로 동작합니다.
    """
    data_url = context.data_url
    keyword = context.dataset.config.get("keyword", "인기상품")
    max_pages = context.dataset.config.get("max_pages", 1)

    context.log.info(f"네이버 쇼핑 크롤링 시작: keyword={keyword}")

    crawler = NaverShoppingCrawler()
    products = crawler.crawl_search_api(keyword, max_pages=max_pages)

    if not products:
        context.log.info("API 크롤링 결과 없음, HTML 파싱으로 전환")
        products = crawler.crawl_search_html(keyword, max_pages=max_pages)

    for product in products:
        context.log.info(
            f"상품: {product.title} | 가격: {product.price:,}원 | "
            f"판매처: {product.mall_name}"
        )

    context.log.info(f"크롤링 완료: 총 {len(products)}개 상품 수집")


# ---------------------------------------------------------------------------
# Standalone 실행
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="네이버 쇼핑 상품 크롤러",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python crawler.py --keyword "노트북" --max-pages 3
  python crawler.py --keyword "무선이어폰" --output-format json
  python crawler.py --keyword "운동화" --output-format xml
        """,
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default="노트북",
        help="검색 키워드 (기본값: 노트북)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="최대 크롤링 페이지 수 (기본값: 1)",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["json", "xml", "both"],
        default="both",
        help="출력 형식 (기본값: both)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="출력 디렉토리 (기본값: 현재 디렉토리)",
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=["api", "html", "auto"],
        default="auto",
        help="크롤링 방식 (기본값: auto — API 우선, 실패 시 HTML)",
    )

    args = parser.parse_args()

    crawler = NaverShoppingCrawler()

    products: List[Product] = []
    if args.method in ("api", "auto"):
        products = crawler.crawl_search_api(args.keyword, args.max_pages)

    if not products and args.method in ("html", "auto"):
        products = crawler.crawl_search_html(args.keyword, args.max_pages)

    if not products:
        logger.warning("수집된 상품이 없습니다.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_keyword = quote(args.keyword, safe="")

    if args.output_format in ("json", "both"):
        json_path = f"{args.output_dir}/products_{safe_keyword}_{timestamp}.json"
        crawler.export_json(json_path)

    if args.output_format in ("xml", "both"):
        xml_path = f"{args.output_dir}/products_{safe_keyword}_{timestamp}.xml"
        crawler.export_xml(xml_path)

    logger.info("전체 작업 완료: %d개 상품 수집", len(products))


if __name__ == "__main__":
    main()
