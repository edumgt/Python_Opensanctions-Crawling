"""
KRX (krx.co.kr) ETF Information Crawler
zavod 프레임워크 기반.

finance.daum.net API는 Kakao 인증이 필요하므로,
Naver Finance ETF API(etfItemList.nhn)를 통해 KRX 상장 ETF 전종목을 수집합니다.

Usage:
    zavod crawl krx.co.kr/krx_etf.yml
"""

from zavod import Context

NAVER_BASE = "https://finance.naver.com"
ETF_LIST_API = f"{NAVER_BASE}/api/sise/etfItemList.nhn"

ETF_TAB_NAMES = {
    0: "전체",
    1: "국내주식형",
    2: "국내채권형",
    3: "섹터/테마",
    4: "해외",
}


def crawl(context: Context) -> None:
    etf_tab: int = context.dataset.config.get("etf_tab", 0)
    tab_name = ETF_TAB_NAMES.get(etf_tab, "전체")

    context.log.info("KRX ETF 크롤링 시작", etf_tab=etf_tab, tab_name=tab_name)

    data = context.fetch_json(ETF_LIST_API)
    etf_list = (data or {}).get("result", {}).get("etfItemList", [])

    if not etf_list:
        context.log.warning("ETF 목록이 비어 있습니다.")
        return

    context.log.info("전체 ETF 수신", count=len(etf_list))

    if etf_tab != 0:
        etf_list = [e for e in etf_list if e.get("etfTabCode") == etf_tab]
        context.log.info("탭 필터링 후", tab_name=tab_name, count=len(etf_list))

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
        three_month_earn_rate = round(float(item.get("threeMonthEarnRate", 0) or 0), 4)
        volume = int(item.get("quant", 0) or 0)
        market_cap = int(item.get("marketSum", 0) or 0)

        entity = context.make("Company")
        entity.id = context.make_slug(code)
        entity.add("name", name)
        entity.add("country", "kr")
        entity.add("registrationNumber", code)
        entity.add("sector", sector)
        entity.add("sourceUrl", f"{NAVER_BASE}/item/main.naver?code={code}")
        entity.add(
            "notes",
            f"현재가:{current_price}원 등락률:{change_rate}% "
            f"NAV:{nav} 3개월수익:{three_month_earn_rate}% "
            f"거래량:{volume} 시가총액:{market_cap}억원",
        )
        context.emit(entity)

    context.log.info("크롤링 완료", emitted=len(etf_list))
