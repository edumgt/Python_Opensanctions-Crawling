"""
Naver Finance (finance.naver.com) Stock Information Crawler v2
Selenium + BeautifulSoup4 기반.

lxml(crawler.py) 대비 변경 사항:
- Selenium headless Chrome으로 페이지 렌더링 후 BS4로 파싱
- _to_int 버그 수정: int(cleaned) → int(float(cleaned))
- StockInfo에 foreign_ratio(cells[8]), per(cells[10]) 필드 추가

Usage:
    python crawler2.py [--market MARKET] [--max-pages MAX_PAGES] [--output-format FORMAT]

Examples:
    python crawler2.py --market KOSPI --max-pages 2
    python crawler2.py --market KOSDAQ --output-format json
"""

import argparse
import json
import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import List
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("finance.naver.crawler2")

BASE_URL = "https://finance.naver.com"
MARKET_SUM_URL = f"{BASE_URL}/sise/sise_market_sum.naver"

REQUEST_DELAY = 1.0
PAGE_LOAD_TIMEOUT = 15


@dataclass
class StockInfo:
    """네이버 금융 주식 데이터 모델"""

    code: str = ""
    name: str = ""
    market: str = ""
    current_price: int = 0
    change_rate: float = 0.0
    volume: int = 0
    market_cap: int = 0
    foreign_ratio: float = 0.0
    per: float = 0.0
    crawled_at: str = ""


def _build_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--mute-audio")
    opts.add_argument("--blink-settings=imagesEnabled=false")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    # DOM ready 시점에 제어 반환 — 이미지·폰트 로드 완료를 기다리지 않음
    opts.page_load_strategy = "eager"

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    # CDP로 CSS·폰트·미디어 차단 (이미지는 --blink-settings으로 처리)
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {
        "urls": ["*.css", "*.woff", "*.woff2", "*.ttf", "*.eot",
                 "*.mp4", "*.webm", "*.mp3", "*.wav"]
    })
    return driver


class NaverStockCrawler:
    """네이버 금융 시가총액 페이지 크롤러 (Selenium + BeautifulSoup4)"""

    def __init__(self, delay: float = REQUEST_DELAY):
        self.delay = delay
        self.stocks: List[StockInfo] = []
        self._driver: webdriver.Chrome | None = None

    def _get_driver(self) -> webdriver.Chrome:
        if self._driver is None:
            self._driver = _build_driver()
        return self._driver

    def close(self) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None

    def crawl_market(self, market: str = "KOSPI", max_pages: int = 1) -> List[StockInfo]:
        """시장(KOSPI/KOSDAQ)의 주식 정보를 수집합니다."""
        market_map = {"KOSPI": "0", "KOSDAQ": "1"}
        sosok = market_map.get(market.upper(), "0")

        logger.info("주식 크롤링 시작: market=%s, max_pages=%d", market.upper(), max_pages)
        all_stocks: List[StockInfo] = []
        driver = self._get_driver()

        try:
            for page in range(1, max_pages + 1):
                params = {"sosok": sosok, "page": page}
                url = f"{MARKET_SUM_URL}?{urlencode(params)}"
                logger.info("  페이지 %d/%d 요청: %s", page, max_pages, url)

                driver.get(url)
                try:
                    WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.type_2"))
                    )
                except Exception:
                    logger.warning("  테이블 로드 타임아웃 (page=%d)", page)
                    break

                items = self._extract_stocks_from_html(driver.page_source, market.upper())
                if not items:
                    logger.info("  더 이상 종목이 없습니다. 크롤링 종료.")
                    break

                all_stocks.extend(items)
                logger.info("  %d개 종목 수집 (누적 %d개)", len(items), len(all_stocks))

                if page < max_pages:
                    time.sleep(self.delay)
        finally:
            self.close()

        self.stocks.extend(all_stocks)
        logger.info("크롤링 완료: 총 %d개 종목 수집", len(all_stocks))
        return all_stocks

    def _extract_stocks_from_html(self, html_text: str, market: str) -> List[StockInfo]:
        """시가총액 HTML 테이블에서 주식 정보를 추출합니다.

        컬럼 구조 (cells[0..12]):
          [0] 순위  [1] 종목명  [2] 현재가  [3] 전일비  [4] 등락률
          [5] 액면가  [6] 시가총액(억원)  [7] 상장주식수(천주)
          [8] 외국인비율(%)  [9] 거래량  [10] PER  [11] ROE  [12] (빈칸)
        """
        stocks: List[StockInfo] = []
        now = datetime.now(timezone.utc).isoformat()

        soup = BeautifulSoup(html_text, "html.parser")
        table = soup.find("table", class_="type_2")
        if not table:
            logger.warning("type_2 테이블을 찾을 수 없습니다.")
            return stocks

        for row in table.find_all("tr"):
            link = row.find("a", href=lambda h: h and "/item/main.naver" in h)
            if not link:
                continue

            href = link.get("href", "")
            stock_code = _extract_stock_code(href)
            stock_name = link.get_text(strip=True)

            cells = [td.get_text(separator=" ", strip=True) for td in row.find_all("td")]
            if len(cells) < 10:
                continue

            stock = StockInfo(
                code=stock_code,
                name=stock_name,
                market=market,
                current_price=_to_int(cells[2]),
                change_rate=_to_float(cells[4]),
                market_cap=_to_int(cells[6]),
                foreign_ratio=_to_float(cells[8]),
                volume=_to_int(cells[9]),
                per=_to_float(cells[10]) if len(cells) > 10 else 0.0,
                crawled_at=now,
            )
            stocks.append(stock)

        return stocks

    def export_json(self, filepath: str) -> None:
        data = {
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "total_count": len(self.stocks),
            "stocks": [asdict(s) for s in self.stocks],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("JSON 저장 완료: %s (%d개 종목)", filepath, len(self.stocks))

    def export_xml(self, filepath: str) -> None:
        root = ET.Element("NaverStockInfos")
        root.set("crawledAt", datetime.now(timezone.utc).isoformat())
        root.set("totalCount", str(len(self.stocks)))

        for stock in self.stocks:
            stock_el = ET.SubElement(root, "Stock")
            stock_el.set("code", stock.code)
            _add_xml_element(stock_el, "Name", stock.name)
            _add_xml_element(stock_el, "Market", stock.market)
            _add_xml_element(stock_el, "CurrentPrice", str(stock.current_price))
            _add_xml_element(stock_el, "ChangeRate", str(stock.change_rate))
            _add_xml_element(stock_el, "Volume", str(stock.volume))
            _add_xml_element(stock_el, "MarketCap", str(stock.market_cap))
            _add_xml_element(stock_el, "ForeignRatio", str(stock.foreign_ratio))
            _add_xml_element(stock_el, "PER", str(stock.per))
            _add_xml_element(stock_el, "CrawledAt", stock.crawled_at)
            if stock.code:
                _add_xml_element(stock_el, "StockUrl", urljoin(BASE_URL, f"/item/main.naver?code={stock.code}"))

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
        logger.info("XML 저장 완료: %s (%d개 종목)", filepath, len(self.stocks))


def _extract_stock_code(href: str) -> str:
    parsed = urlparse(href)
    query = parse_qs(parsed.query)
    return query.get("code", [""])[0]


def _add_xml_element(parent: ET.Element, tag: str, text: str) -> ET.Element:
    el = ET.SubElement(parent, tag)
    el.text = text
    return el


def _to_int(text: str) -> int:
    cleaned = text.replace(",", "").replace("원", "").replace("%", "").strip()
    cleaned = cleaned.replace("+", "").replace("-", "")
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def _to_float(text: str) -> float:
    cleaned = text.replace(",", "").replace("%", "").replace("+", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def crawl(context) -> None:
    """zavod 프레임워크 호환 crawl 함수"""
    market = context.dataset.config.get("market", "KOSPI")
    max_pages = context.dataset.config.get("max_pages", 1)

    context.log.info(f"네이버 금융 크롤링 시작: market={market}")

    crawler = NaverStockCrawler()
    stocks = crawler.crawl_market(market=market, max_pages=max_pages)

    for stock in stocks:
        context.log.info(
            f"종목: {stock.name}({stock.code}) | 현재가: {stock.current_price:,}원 | "
            f"등락률: {stock.change_rate}% | PER: {stock.per} | 외국인: {stock.foreign_ratio}%"
        )

    context.log.info(f"크롤링 완료: 총 {len(stocks)}개 종목 수집")


def main():
    parser = argparse.ArgumentParser(
        description="네이버 금융 주식 정보 크롤러 v2 (Selenium)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python crawler2.py --market KOSPI --max-pages 2
  python crawler2.py --market KOSDAQ --output-format json
        """,
    )
    parser.add_argument("--market", type=str, choices=["KOSPI", "KOSDAQ"], default="KOSPI")
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--output-format", type=str, choices=["json", "xml", "both"], default="both")
    parser.add_argument("--output-dir", type=str, default=".")

    args = parser.parse_args()
    crawler = NaverStockCrawler()
    stocks = crawler.crawl_market(market=args.market, max_pages=args.max_pages)

    if not stocks:
        logger.warning("수집된 종목이 없습니다.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    market_name = args.market.lower()

    if args.output_format in ("json", "both"):
        crawler.export_json(f"{args.output_dir}/stocks_{market_name}_{timestamp}.json")
    if args.output_format in ("xml", "both"):
        crawler.export_xml(f"{args.output_dir}/stocks_{market_name}_{timestamp}.xml")

    logger.info("전체 작업 완료: %d개 종목 수집", len(stocks))


if __name__ == "__main__":
    main()
