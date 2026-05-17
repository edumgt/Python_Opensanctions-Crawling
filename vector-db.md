# RAG 시스템 데이터 관리 및 CDC 구현 가이드

## 1. Vector DB 데이터 관리 기본 원칙

Vector Database에서는 **데이터가 지속적으로 추가**되는 것이 기본이며, 필요 시 **업데이트**와 **삭제**를 수행합니다.

### 주요 작업
- **추가 (Insert)**: 새로운 데이터 → 임베딩 생성 후 신규 엔트리 저장
- **업데이트 (Update)**: 동일 ID 기준으로 벡터 및 메타데이터 교체
- **삭제 (Delete)**: ID 단위 삭제

### 데이터 괴리(Drift) 발생 시 문제점
- 검색 정확도 저하
- 오래된 정보 제공
- RAG Hallucination 증가

### 괴리 대응 전략
- ID 기반 업데이트
- Timestamp / Version Metadata Filtering
- 주기적 Re-indexing
- TTL (Time To Live)
- Hybrid Search 적용

---

## 2. RAG 시스템의 데이터 드리프트 대응 전략

### 데이터 드리프트 주요 유형
- Data Drift (데이터 내용 변화)
- Concept Drift (의미 변화)
- Embedding Drift
- Temporal Drift (최신성 문제)

### 핵심 대응 전략

**A. Freshness 관리**
- CDC 기반 Incremental Update
- Timestamp / Version Metadata 활용
- Recency Prioritization

**B. 모니터링**
- Retrieval 품질 지표 지속 관찰
- LLM-as-Judge 평가
- Drift Detection (PSI, KL Divergence 등)

**C. 검색 강화**
- Hybrid Search (Vector + Keyword + Metadata)
- Re-ranking
- Multi-Index / Namespace 분리

**D. 거버넌스**
- Source of Truth 명확화
- Human-in-the-Loop
- 주기적 Re-embedding

**추천 로드맵**
1. 단기: Metadata Filtering + 모니터링
2. 중기: CDC + Hybrid Search
3. 장기: Drift-Aware RAG + Observability

---

## 3. CDC (Change Data Capture) 구현 상세

### CDC 아키텍처
**Source DB → CDC Connector → Message Broker → Stream Processor → Embedding → Vector DB**

### 추천 스택
- **Source DB**: PostgreSQL, MySQL 등
- **CDC Tool**: Debezium (권장)
- **Broker**: Apache Kafka / Redpanda
- **Vector DB**: Pinecone, Weaviate, Qdrant 등

### Debezium + PostgreSQL 구현 단계
1. PostgreSQL logical replication 설정 (`wal_level = logical`)
2. Debezium Connector 배포 및 설정
3. Kafka Topic 이벤트 소비
4. 이벤트 처리 (CREATE/UPDATE → Embedding → Upsert, DELETE → Delete)
5. Idempotency 및 Error Handling (DLQ)

### Best Practices
- Idempotent 처리 필수
- Schema Evolution 대응
- Monitoring (Lag, Latency, Success Rate)
- Incremental Embedding으로 비용 최적화
- Exactly-Once Semantics 적용

### 잠재적 도전
- 대규모 Snapshot 부하 관리
- Embedding 비용 제어
- DELETE Propagation

---

이 문서는 Vector DB 데이터 관리 → 데이터 드리프트 대응 → CDC 구현까지의 전체 대화를 정리한 것입니다.