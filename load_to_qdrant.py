"""
주식 정보 크롤링 → Qdrant 적재 파이프라인

Naver Finance / Daum Finance / KRX 크롤러를 실행하고
수집된 주식 데이터를 Qdrant에 적재합니다.

Usage:
    python load_to_qdrant.py [--sources SOURCE [SOURCE ...]] [--market MARKET]
    python load_to_qdrant.py --sources naver daum krx --market KOSPI
"""

import argparse
import hashlib
import importlib.util
import logging
import sys
import time
from pathlib import Path
from typing import List

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    PointStruct,
    VectorParams,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("qdrant.loader")

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "korean_stocks"
VECTOR_DIM = 128
REQUEST_DELAY = 1.0

ROOT = Path(__file__).parent


# ---------------------------------------------------------------------------
# 모듈 동적 로드 헬퍼
# ---------------------------------------------------------------------------

def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 벡터 생성: 종목명 + 코드의 character n-gram 기반 해시 임베딩
# ---------------------------------------------------------------------------

def _ngrams(text: str, n: int = 2) -> List[str]:
    padded = f"<{text}>"
    return [padded[i:i + n] for i in range(len(padded) - n + 1)]


def make_stock_vector(code: str, name: str, market: str) -> List[float]:
    """종목 코드·이름·시장을 조합한 결정적 128차원 임베딩 벡터를 생성합니다."""
    combined = f"{market}:{code}:{name}"

    vec = np.zeros(VECTOR_DIM, dtype=np.float32)
    for gram in _ngrams(combined, n=2):
        h = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
        idx = h % VECTOR_DIM
        vec[idx] += 1.0

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    return vec.tolist()


# ---------------------------------------------------------------------------
# Qdrant 컬렉션 초기화
# ---------------------------------------------------------------------------

def ensure_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )
        logger.info("컬렉션 생성: %s (dim=%d)", COLLECTION_NAME, VECTOR_DIM)
    else:
        logger.info("기존 컬렉션 사용: %s", COLLECTION_NAME)


# ---------------------------------------------------------------------------
# 포인트 ID: 종목코드 + 소스 기반 결정적 정수 ID
# ---------------------------------------------------------------------------

def make_point_id(source: str, code: str) -> int:
    raw = f"{source}:{code}"
    return int(hashlib.sha256(raw.encode()).hexdigest()[:15], 16)


# ---------------------------------------------------------------------------
# 크롤러별 실행 및 Qdrant 업로드
# ---------------------------------------------------------------------------

def crawl_and_upload_naver(client: QdrantClient, market: str, max_pages: int = 1) -> int:
    mod = _load_module("naver_crawler", ROOT / "finance.naver.com" / "crawler.py")
    logger.info("[Naver Finance] 크롤링 시작: market=%s", market)
    c = mod.NaverStockCrawler()
    stocks = c.crawl_market(market=market, max_pages=max_pages)
    return _upload_stocks(client, stocks, source="naver", code_field="code")


def crawl_and_upload_daum(client: QdrantClient, market: str, max_pages: int = 1) -> int:
    mod = _load_module("daum_crawler", ROOT / "finance.daum.net" / "crawler.py")
    logger.info("[Daum Finance] 크롤링 시작: market=%s", market)
    c = mod.DaumStockCrawler(delay=0.2)
    stocks = c.crawl_market(market=market, max_pages=max_pages)
    return _upload_stocks(client, stocks, source="daum", code_field="symbol_code")


def crawl_and_upload_krx(client: QdrantClient, market: str) -> int:
    mod = _load_module("krx_crawler", ROOT / "krx.co.kr" / "crawler.py")
    logger.info("[KRX] ETF 크롤링 시작")
    c = mod.KRXStockCrawler()
    stocks = c.crawl_market(tab=0)
    return _upload_stocks(client, stocks, source="krx", code_field="code")


def _upload_stocks(client: QdrantClient, stocks, source: str, code_field: str) -> int:
    if not stocks:
        logger.warning("[%s] 수집된 종목 없음", source)
        return 0

    points: List[PointStruct] = []
    for stock in stocks:
        code = getattr(stock, code_field, "") or ""
        name = stock.name or ""
        market = stock.market or ""

        point = PointStruct(
            id=make_point_id(source, code),
            vector=make_stock_vector(code, name, market),
            payload={
                "source": source,
                "code": code,
                "name": name,
                "market": market,
                "current_price": getattr(stock, "current_price", 0),
                "change_rate": getattr(stock, "change_rate", 0.0),
                "volume": getattr(stock, "volume", 0),
                "market_cap": getattr(stock, "market_cap", 0),
                "crawled_at": getattr(stock, "crawled_at", ""),
            },
        )
        points.append(point)

    batch_size = 100
    uploaded = 0
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        uploaded += len(batch)
        logger.info("[%s] %d/%d 포인트 업로드 완료", source, uploaded, len(points))

    logger.info("[%s] 총 %d개 종목 Qdrant 업로드 완료", source, len(points))
    return len(points)


# ---------------------------------------------------------------------------
# 결과 검증
# ---------------------------------------------------------------------------

def verify_collection(client: QdrantClient) -> None:
    info = client.get_collection(COLLECTION_NAME)
    count = client.count(COLLECTION_NAME).count
    logger.info(
        "=== Qdrant 컬렉션 현황 ===\n"
        "  컬렉션: %s\n"
        "  총 포인트 수: %d\n"
        "  벡터 차원: %d\n"
        "  거리 메트릭: %s",
        COLLECTION_NAME,
        count,
        info.config.params.vectors.size,
        info.config.params.vectors.distance,
    )

    # 유사 종목 검색 테스트 (삼성전자 벡터 기준)
    sample_vec = make_stock_vector("005930", "삼성전자", "KOSPI")
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=sample_vec,
        limit=5,
    ).points

    logger.info("=== 유사 종목 검색 테스트 (삼성전자 기준) ===")
    for hit in results:
        p = hit.payload
        logger.info(
            "  [%.4f] %s(%s) | %s | 현재가: %s원",
            hit.score,
            p.get("name", ""),
            p.get("code", ""),
            p.get("source", ""),
            f"{p.get('current_price', 0):,}",
        )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="주식 크롤링 → Qdrant 적재 파이프라인")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["naver", "daum", "krx"],
        default=["naver", "daum", "krx"],
        help="크롤링 소스 (기본값: naver daum krx)",
    )
    parser.add_argument(
        "--market",
        type=str,
        choices=["KOSPI", "KOSDAQ"],
        default="KOSPI",
        help="수집할 시장 (기본값: KOSPI)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Naver/Daum 최대 크롤링 페이지 수 (기본값: 1)",
    )
    parser.add_argument(
        "--qdrant-url",
        type=str,
        default=QDRANT_URL,
        help=f"Qdrant URL (기본값: {QDRANT_URL})",
    )

    args = parser.parse_args()

    client = QdrantClient(url=args.qdrant_url)
    logger.info("Qdrant 연결: %s", args.qdrant_url)
    ensure_collection(client)

    total = 0
    for source in args.sources:
        try:
            if source == "naver":
                n = crawl_and_upload_naver(client, args.market, args.max_pages)
            elif source == "daum":
                daum_market = "KOSDAQ" if args.market == "KOSPI" else "KOSPI"
                n = crawl_and_upload_daum(client, daum_market, args.max_pages)
            elif source == "krx":
                n = crawl_and_upload_krx(client, args.market)
            total += n
            time.sleep(REQUEST_DELAY)
        except Exception as exc:
            logger.error("[%s] 오류 발생: %s", source, exc, exc_info=True)

    logger.info("전체 완료: 총 %d개 포인트 적재", total)
    verify_collection(client)


if __name__ == "__main__":
    main()
