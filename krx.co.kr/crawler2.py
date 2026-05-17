"""
KRX (krx.co.kr) ETF Information Crawler v2
Standalone requests 기반. zavod 의존성 없음.

Usage:
    python crawler2.py [--tab TAB] [--output-format FORMAT]

Examples:
    python crawler2.py --tab 0
    python crawler2.py --tab 1 --output-format json
"""

import argparse
import json
import logging
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import List

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("krx.crawler2")

NAVER_BASE = "https://finance.naver.com"
ETF_LIST_API = f"{NAVER_BASE}/api/sise/etfItemList.nhn"

ETF_TAB_NAMES = {
    0: "전체",
    1: "국내주식형",
    2: "국내채권형",
    3: "섹터/테마",
    4: "해외",
}

API_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://finance.naver.com/",
}


@dataclass
class ETFInfo:
    """KRX ETF 데이터 모델"""

    code: str = ""
    name: str = ""
    market: str = ""              # ETF 분류(섹터/테마 등)
    current_price: int = 0        # 현재가(원)
    change_rate: float = 0.0      # 등락률(%)
    volume: int = 0               # 거래량
    trading_value: int = 0        # 거래대금(원)
    market_cap: int = 0           # 순자산총액(억원)
    nav: float = 0.0              # 순자산가치(NAV)
    nav_diff: float = 0.0         # 현재가 - NAV 괴리율(%)
    three_month_earn_rate: float = 0.0   # 3개월 수익률(%)
    six_month_earn_rate: float = 0.0    # 6개월 수익률(%)
    one_year_earn_rate: float = 0.0     # 1년 수익률(%)
    crawled_at: str = ""


class KRXStockCrawler:
    """KRX ETF 크롤러 (Naver Finance ETF API 기반)"""

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(API_HEADERS)
        self.stocks: List[ETFInfo] = []

    def crawl_market(self, tab: int = 0) -> List[ETFInfo]:
        """ETF 목록을 수집합니다. tab=0이면 전체."""
        tab_name = ETF_TAB_NAMES.get(tab, "전체")
        logger.info("KRX ETF 크롤링 시작: tab=%d (%s)", tab, tab_name)

        try:
            resp = self._session.get(ETF_LIST_API, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("ETF API 호출 실패: %s", exc)
            return []

        etf_list = (data or {}).get("result", {}).get("etfItemList", [])
        if not etf_list:
            logger.warning("ETF 목록이 비어 있습니다.")
            return []

        logger.info("전체 ETF 수신: %d개", len(etf_list))

        if tab != 0:
            etf_list = [e for e in etf_list if e.get("etfTabCode") == tab]
            logger.info("탭 필터링 후: %d개 (%s)", len(etf_list), tab_name)

        now = datetime.now(timezone.utc).isoformat()
        result: List[ETFInfo] = []

        for item in etf_list:
            code = item.get("itemcode", "")
            name = item.get("itemname", "")
            if not code or not name:
                continue

            item_tab = item.get("etfTabCode", 0)
            sector = ETF_TAB_NAMES.get(item_tab, str(item_tab))

            risefall = item.get("risefall", "3")
            change_rate = float(item.get("changeRate", 0) or 0)
            if risefall in ("4", "5"):
                change_rate = -abs(change_rate)
            else:
                change_rate = abs(change_rate)

            current_price = int(item.get("nowVal", 0) or 0)
            nav = round(float(item.get("nav", 0) or 0), 2)

            # NAV 괴리율: (현재가 - NAV) / NAV * 100
            nav_diff = 0.0
            if nav > 0:
                nav_diff = round((current_price - nav) / nav * 100, 4)

            etf = ETFInfo(
                code=code,
                name=name,
                market=sector,
                current_price=current_price,
                change_rate=round(change_rate, 4),
                volume=int(item.get("quant", 0) or 0),
                trading_value=int(item.get("amonut", 0) or 0),  # Naver API 오타 유지
                market_cap=int(item.get("marketSum", 0) or 0),
                nav=nav,
                nav_diff=nav_diff,
                three_month_earn_rate=round(float(item.get("threeMonthEarnRate", 0) or 0), 4),
                six_month_earn_rate=round(float(item.get("sixMonthEarnRate", 0) or 0), 4),
                one_year_earn_rate=round(float(item.get("oneYearEarnRate", 0) or 0), 4),
                crawled_at=now,
            )
            result.append(etf)

        self.stocks.extend(result)
        logger.info("KRX ETF 크롤링 완료: %d개", len(result))
        return result

    def export_json(self, filepath: str) -> None:
        data = {
            "source": "krx.co.kr (via naver finance etf api)",
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "total_count": len(self.stocks),
            "etfs": [asdict(s) for s in self.stocks],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("JSON 저장 완료: %s (%d개)", filepath, len(self.stocks))

    def export_xml(self, filepath: str) -> None:
        root = ET.Element("KRXETFInfos")
        root.set("source", "krx.co.kr")
        root.set("crawledAt", datetime.now(timezone.utc).isoformat())
        root.set("totalCount", str(len(self.stocks)))

        for etf in self.stocks:
            el = ET.SubElement(root, "ETF")
            el.set("code", etf.code)
            for tag, val in [
                ("Name", etf.name), ("Market", etf.market),
                ("CurrentPrice", str(etf.current_price)),
                ("ChangeRate", str(etf.change_rate)),
                ("Volume", str(etf.volume)),
                ("TradingValue", str(etf.trading_value)),
                ("MarketCap", str(etf.market_cap)),
                ("NAV", str(etf.nav)),
                ("NAVDiff", str(etf.nav_diff)),
                ("ThreeMonthEarnRate", str(etf.three_month_earn_rate)),
                ("SixMonthEarnRate", str(etf.six_month_earn_rate)),
                ("OneYearEarnRate", str(etf.one_year_earn_rate)),
                ("CrawledAt", etf.crawled_at),
            ]:
                child = ET.SubElement(el, tag)
                child.text = val

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
        logger.info("XML 저장 완료: %s (%d개)", filepath, len(self.stocks))


def main():
    parser = argparse.ArgumentParser(description="KRX ETF 크롤러 v2")
    parser.add_argument("--tab", type=int, default=0, choices=list(ETF_TAB_NAMES.keys()),
                        help="ETF 탭 (0=전체, 1=국내주식형, 2=국내채권형, 3=섹터/테마, 4=해외)")
    parser.add_argument("--output-format", type=str, choices=["json", "xml", "both"], default="both")
    parser.add_argument("--output-dir", type=str, default=".")

    args = parser.parse_args()
    crawler = KRXStockCrawler()
    stocks = crawler.crawl_market(tab=args.tab)

    if not stocks:
        logger.warning("수집된 ETF가 없습니다.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output_format in ("json", "both"):
        crawler.export_json(f"{args.output_dir}/krx_etf_{timestamp}.json")
    if args.output_format in ("xml", "both"):
        crawler.export_xml(f"{args.output_dir}/krx_etf_{timestamp}.xml")

    logger.info("전체 작업 완료: %d개 ETF 수집", len(stocks))


if __name__ == "__main__":
    main()
