#!/bin/bash
# =========================================
# OpenSanctions Full Pipeline Starter (bash)
# =========================================
# 실행 흐름:
# 1. DB 초기화 (PostgreSQL)
# 2. Zavod ETL 전체 자동화 (crawl → export → load-db)
# 3. Zavod UI 구동
# =========================================

set -e

DATASET=${1:-datasets/nl/terrorism_list/nl_terrorism_list.yml}

echo "🚀 Starting OpenSanctions full environment..."
echo "--------------------------------------------"
if grep -qi microsoft /proc/version 2>/dev/null; then
  echo "🧩 WSL detected: Docker Desktop WSL integration or Docker Engine must be running."
  echo "   Tip: keep the repo under /home to avoid slow Windows filesystem mounts."
fi

export LOCAL_UID="$(id -u)"
export LOCAL_GID="$(id -g)"

# 1️⃣ 기존 컨테이너 종료 및 정리
echo "🧹 Stopping and removing existing containers..."
docker compose down -v || true

# 2️⃣ DB 컨테이너 빌드 및 실행
echo "🛠️  Building and starting database container..."
docker compose up -d --build db

echo "⏳ Waiting for database to become healthy..."
sleep 15

# 3️⃣ Zavod ETL 전체 자동 실행
echo "⚙️  Running Zavod ETL (crawl → export → load-db)..."

docker compose run --rm zavod bash -c "
  export DATABASE_URL=postgresql://postgres:password@db:5432/dev &&
  echo '🛰️  Crawling dataset: $DATASET' &&
  zavod crawl $DATASET &&
  echo '📦 Exporting dataset...' &&
  zavod export $DATASET &&
  echo '💾 Loading into Postgres...' &&
  zavod load-db $DATASET &&
  echo '✅ ETL pipeline completed successfully!'
"

# 4️⃣ Zavod UI 구동
echo "🌐 Starting Zavod UI..."
docker compose up -d web

# 5️⃣ 상태 표시
echo ""
echo "--------------------------------------------"
echo "✅ All systems are up and running!"
echo "   - PostgreSQL:   localhost:5432"
echo "   - Zavod UI:     http://localhost:3000"
echo "   - Dataset:      $DATASET"
echo "--------------------------------------------"

# 6️⃣ 실시간 로그 보기
echo ""
echo "📜 Showing live logs for Zavod UI..."
docker compose logs -f web
