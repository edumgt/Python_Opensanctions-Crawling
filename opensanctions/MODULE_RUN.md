# 모듈 실행 가이드

이 문서는 **OpenSanctions 모듈(ETL 및 UI 포함)** 을 로컬 또는 컨테이너 환경에서 실행하는 방법을 정리합니다.

## 1) 빠른 실행 (통합 스크립트)

가장 쉬운 방법은 제공되는 스크립트를 사용하는 것입니다.

### Linux/macOS
```bash
./start.sh
```

### Windows (PowerShell)
```powershell
./start.ps1
```

위 스크립트는 다음 과정을 자동으로 수행합니다.

- 컨테이너 초기화 및 PostgreSQL 시작
- `zavod crawl → export → load-db` 파이프라인 실행
- UI 자동 구동

> 실행 로그 및 결과는 `data/` 디렉터리와 콘솔 출력에서 확인할 수 있습니다.

---

## 1-1) WSL Ubuntu에서 실행

WSL2 환경에서 실행 시 아래 사항을 먼저 확인하세요.

1. **Docker Desktop WSL Integration** 또는 **WSL 내부 Docker Engine** 구동
2. 저장소는 **WSL 홈 디렉터리**에 위치 (예: `/home/<user>/opensanctions3`)
3. Docker 연결 확인
   ```bash
   docker info
   docker compose version
   ```

그 다음 아래 명령으로 실행합니다.

```bash
./start.sh
```

> `start.sh`는 WSL 환경에서 `LOCAL_UID/LOCAL_GID`를 자동 설정하여
> 권한 문제를 최소화합니다.

---

## 2) Docker 기반 실행

### 이미지 빌드
```bash
make build
```

### 컨테이너 내부 쉘 접속
```bash
make shell
```

### 기본 파이프라인 실행
```bash
make crawl
```

---

## 3) 특정 데이터셋만 실행

`datasets/` 내의 YAML 정의 파일을 직접 지정하여 크롤링할 수 있습니다.

```bash
zavod crawl datasets/us/ofac.yml
```

실행 결과는 아래 경로에 저장됩니다.

```
data/datasets/<dataset명>/
```

---

## 4) UI 실행 (로컬 개발)

`ui/` 폴더의 Next.js 기반 UI를 개별적으로 띄우고 싶은 경우:

```bash
cd ui
npm install
npm run dev
```

브라우저에서 `http://localhost:3000` 접속 후 UI를 확인합니다.

---

## 5) 참고 사항

- 데이터셋 정의: `datasets/`
- ETL 프레임워크: `zavod/`
- 보조 스크립트: `contrib/`
- 분석 자료: `analysis/`

필요한 상세 옵션이나 환경 설정은 `README.md`, `Dockerfile`, `docker-compose.yml`을 참고하세요.
