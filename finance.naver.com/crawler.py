"""
Naver Finance (finance.naver.com) Stock Information Crawler
zavod 프레임워크 기반.

Usage:
    zavod crawl finance.naver.com/finance_naver.yml
"""

import time
from urllib.parse import parse_qs, urlencode, urlparse

from lxml import html
from zavod import Context

BASE_URL = "https://finance.naver.com"
MARKET_SUM_URL = f"{BASE_URL}/sise/sise_market_sum.naver"
REQUEST_DELAY = 1.0


def crawl_page(context: Context, sosok: str, market: str, page: int) -> bool:
    """한 페이지를 크롤링하여 Company 엔티티를 emit합니다.
    종목이 없으면 False 반환."""
    doc = context.fetch_html(
        MARKET_SUM_URL,
        params={"sosok": sosok, "page": page},
    )

    rows = doc.xpath('//table[@class="type_2"]//tr')
    found = False

    for row in rows:
        link = row.xpath('.//a[contains(@href, "/item/main.naver")][1]')
        if not link:
            continue

        href = link[0].get("href", "")
        code = _extract_code(href)
        name = link[0].text_content().strip()

        cells = [" ".join(td.xpath(".//text()")).strip() for td in row.xpath("./td")]
        if len(cells) < 10:
            continue

        current_price = _to_int(cells[2])
        change_rate = _to_float(cells[4])
        market_cap = _to_int(cells[6])
        foreign_ratio = _to_float(cells[8])
        volume = _to_int(cells[9])
        per = _to_float(cells[10]) if len(cells) > 10 else 0.0

        entity = context.make("Company")
        entity.id = context.make_slug(code)
        entity.add("name", name)
        entity.add("country", "kr")
        entity.add("registrationNumber", code)
        entity.add("sector", market)
        entity.add("sourceUrl", f"{BASE_URL}/item/main.naver?code={code}")
        entity.add(
            "notes",
            f"현재가:{current_price}원 등락률:{change_rate}% "
            f"시가총액:{market_cap}억원 거래량:{volume} "
            f"외국인비율:{foreign_ratio}% PER:{per}",
        )
        context.emit(entity)
        found = True

    return found


def crawl(context: Context) -> None:
    market: str = context.dataset.config.get("market", "KOSPI")
    max_pages: int = context.dataset.config.get("max_pages", 1)

    market_map = {"KOSPI": "0", "KOSDAQ": "1"}
    sosok = market_map.get(market.upper(), "0")

    context.log.info("크롤링 시작", market=market, max_pages=max_pages)

    for page in range(1, max_pages + 1):
        context.log.info("페이지 요청", page=page, market=market)
        has_data = crawl_page(context, sosok, market.upper(), page)
        if not has_data:
            context.log.info("더 이상 종목 없음. 종료.", page=page)
            break
        if page < max_pages:
            time.sleep(REQUEST_DELAY)


def _extract_code(href: str) -> str:
    parsed = urlparse(href)
    return parse_qs(parsed.query).get("code", [""])[0]


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
