"""
KRX (krx.co.kr) ETF Information Crawler

한국거래소(KRX) 상장 ETF 정보를 수집합니다.
Naver Finance ETF API를 통해 KRX 상장 ETF 전종목 데이터를 가져옵니다.

Usage:
    python crawler.py [--tab TAB] [--output-format FORMAT]

Examples:
    python crawler.py
    python crawler.py --tab 1 --output-format json
    python crawler.py --tab 2 --output-format xml
"""

import argparse
import json
import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urljoin

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("krx.etf.crawler")

NAVER_BASE = "https://finance.naver.com"
ETF_LIST_API = f"{NAVER_BASE}/api/sise/etfItemList.nhn"

# ETF 탭 코드 (1: 국내 주식형, 2: 국내 채권형, 3: 섹터, 4: 해외, 0: 전체)
ETF_TAB_NAMES = {
    0: "전체",
    1: "국내 주식형",
    2: "국내 채권형",
    3: "섹터/테마",
    4: "해외",
}

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://finance.naver.com/",
}

REQUEST_DELAY = 1.0


@dataclass
class StockInfo:
    """KRX 상장 ETF 데이터 모델"""

    code: str = ""
    name: str = ""
    market: str = "KRX-ETF"
    etf_tab: str = ""
    current_price: int = 0
    change_rate: float = 0.0
    nav: float = 0.0
    three_month_earn_rate: float = 0.0
    volume: int = 0
    market_cap: int = 0
    crawled_at: str = ""


class KRXStockCrawler:
    """KRX 상장 ETF 크롤러 (Naver Finance ETF API 사용)"""

    def __init__(self, delay: float = REQUEST_DELAY):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.delay = delay
        self.stocks: List[StockInfo] = []

    def crawl_market(
        self,
        market: str = "KRX",
        tab: int = 0,
    ) -> List[StockInfo]:
        """
        KRX 상장 ETF 목록을 수집합니다.
        market 파라미터는 일관성을 위해 유지되며, 내부적으로 ETF 탭으로 매핑됩니다.
        tab: 0=전체, 1=국내주식형, 2=국내채권형, 3=섹터/테마, 4=해외
        """
        tab_name = ETF_TAB_NAMES.get(tab, "전체")
        logger.info("KRX ETF 크롤링 시작: tab=%d(%s)", tab, tab_name)

        try:
            resp = self.session.get(ETF_LIST_API, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.warning("ETF 목록 요청 실패: %s", exc)
            return []
        except ValueError as exc:
            logger.warning("JSON 파싱 실패: %s", exc)
            return []

        etf_list = data.get("result", {}).get("etfItemList", [])
        logger.info("전체 ETF 수: %d개", len(etf_list))

        # 탭 필터링 (0=전체, 그 외 탭 코드로 필터)
        if tab != 0:
            etf_list = [e for e in etf_list if e.get("etfTabCode") == tab]
            logger.info("탭 %d(%s) 필터링 후: %d개", tab, tab_name, len(etf_list))

        stocks = self._parse_etf_list(etf_list)

        self.stocks.extend(stocks)
        logger.info("크롤링 완료: 총 %d개 ETF 수집", len(stocks))
        return stocks

    def _parse_etf_list(self, etf_list: list) -> List[StockInfo]:
        """ETF 목록 JSON에서 StockInfo 목록을 생성합니다."""
        stocks: List[StockInfo] = []
        now = datetime.now(timezone.utc).isoformat()

        for item in etf_list:
            tab_code = item.get("etfTabCode", 0)
            tab_name = ETF_TAB_NAMES.get(tab_code, str(tab_code))

            risefall = item.get("risefall", "3")
            change_val = item.get("changeRate", 0.0)
            # risefall: 1=상한, 2=상승, 3=보합, 4=하락, 5=하한
            if risefall in ("4", "5"):
                change_val = -abs(change_val)
            else:
                change_val = abs(change_val)

            stock = StockInfo(
                code=item.get("itemcode", ""),
                name=item.get("itemname", ""),
                market="KRX-ETF",
                etf_tab=tab_name,
                current_price=int(item.get("nowVal", 0) or 0),
                change_rate=round(change_val, 2),
                nav=round(float(item.get("nav", 0) or 0), 2),
                three_month_earn_rate=round(float(item.get("threeMonthEarnRate", 0) or 0), 4),
                volume=int(item.get("quant", 0) or 0),
                market_cap=int(item.get("marketSum", 0) or 0),
                crawled_at=now,
            )
            stocks.append(stock)

        return stocks

    def export_json(self, filepath: str) -> None:
        """수집된 ETF 데이터를 JSON 파일로 저장합니다."""
        data = {
            "source": "krx.co.kr (via naver finance etf api)",
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "total_count": len(self.stocks),
            "stocks": [asdict(s) for s in self.stocks],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("JSON 저장 완료: %s (%d개 ETF)", filepath, len(self.stocks))

    def export_xml(self, filepath: str) -> None:
        """수집된 ETF 데이터를 XML 파일로 저장합니다."""
        root = ET.Element("KRXETFInfos")
        root.set("source", "krx.co.kr")
        root.set("crawledAt", datetime.now(timezone.utc).isoformat())
        root.set("totalCount", str(len(self.stocks)))

        for stock in self.stocks:
            el = ET.SubElement(root, "ETF")
            el.set("code", stock.code)
            _add_xml_element(el, "Name", stock.name)
            _add_xml_element(el, "Market", stock.market)
            _add_xml_element(el, "ETFTab", stock.etf_tab)
            _add_xml_element(el, "CurrentPrice", str(stock.current_price))
            _add_xml_element(el, "ChangeRate", str(stock.change_rate))
            _add_xml_element(el, "NAV", str(stock.nav))
            _add_xml_element(el, "ThreeMonthEarnRate", str(stock.three_month_earn_rate))
            _add_xml_element(el, "Volume", str(stock.volume))
            _add_xml_element(el, "MarketCap", str(stock.market_cap))
            _add_xml_element(el, "CrawledAt", stock.crawled_at)
            if stock.code:
                _add_xml_element(
                    el, "StockUrl",
                    urljoin(NAVER_BASE, f"/item/main.naver?code={stock.code}"),
                )

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
        logger.info("XML 저장 완료: %s (%d개 ETF)", filepath, len(self.stocks))


def _add_xml_element(parent: ET.Element, tag: str, text: str) -> ET.Element:
    el = ET.SubElement(parent, tag)
    el.text = text
    return el


def crawl(context) -> None:
    """zavod 프레임워크 호환 crawl 함수"""
    tab = context.dataset.config.get("etf_tab", 0)

    context.log.info(f"KRX ETF 크롤링 시작: tab={tab}")

    crawler = KRXStockCrawler()
    stocks = crawler.crawl_market(tab=tab)

    for stock in stocks[:20]:
        context.log.info(
            f"ETF: {stock.name}({stock.code}) | 현재가: {stock.current_price:,}원 | "
            f"등락률: {stock.change_rate}% | 3개월수익: {stock.three_month_earn_rate}%"
        )

    context.log.info(f"크롤링 완료: 총 {len(stocks)}개 ETF 수집")


def main():
    parser = argparse.ArgumentParser(
        description="KRX 상장 ETF 정보 크롤러",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
탭 코드:
  0: 전체 ETF
  1: 국내 주식형
  2: 국내 채권형
  3: 섹터/테마
  4: 해외

예시:
  python crawler.py
  python crawler.py --tab 1 --output-format json
  python crawler.py --tab 3 --output-format xml
        """,
    )
    parser.add_argument(
        "--market", type=str, default="KRX",
        help="시장 구분 (기본값: KRX, ETF 크롤러에서는 참고용)",
    )
    parser.add_argument(
        "--tab", type=int, choices=[0, 1, 2, 3, 4], default=0,
        help="ETF 탭 코드 (0=전체, 1=국내주식형, 2=채권형, 3=섹터, 4=해외, 기본값: 0)",
    )
    parser.add_argument(
        "--output-format", type=str, choices=["json", "xml", "both"], default="both",
        help="출력 형식 (기본값: both)",
    )
    parser.add_argument(
        "--output-dir", type=str, default=".",
        help="출력 디렉토리 (기본값: 현재 디렉토리)",
    )

    args = parser.parse_args()

    crawler = KRXStockCrawler()
    stocks = crawler.crawl_market(market=args.market, tab=args.tab)

    if not stocks:
        logger.warning("수집된 ETF가 없습니다.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tab_name = ETF_TAB_NAMES.get(args.tab, str(args.tab)).replace("/", "_").replace(" ", "_")

    if args.output_format in ("json", "both"):
        crawler.export_json(f"{args.output_dir}/etf_krx_{tab_name}_{timestamp}.json")
    if args.output_format in ("xml", "both"):
        crawler.export_xml(f"{args.output_dir}/etf_krx_{tab_name}_{timestamp}.xml")

    logger.info("전체 작업 완료: %d개 ETF 수집", len(stocks))


if __name__ == "__main__":
    main()
