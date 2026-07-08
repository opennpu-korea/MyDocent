# RAG Integration and Kotaemon

이 문서는 로컬 지식베이스(`knowledge_base.json`)에 저장된 기사들을 벡터화하여 Kotaemon 벡터 DB에 적재하는 방법을 설명합니다.

파일
- `mydocent/embeddings.py`: `EmbeddingProvider` 인터페이스와 `DummyEmbeddingProvider`(테스트용)를 포함합니다.
- `mydocent/kotaemon.py`: Kotaemon HTTP API에 벡터를 업서트하는 간단한 클라이언트입니다. 기본적으로 `POST {endpoint}/upsert` 호출을 보냅니다.
- `mydocent/rag.py`: `RAGIndexer`는 `KnowledgeBase`에서 주제별 기사를 읽어 임베딩을 생성하고 Kotaemon에 업서트합니다.
- `run_rag_update.py`: CLI로 특정 주제를 Kotaemon에 인덱싱합니다.

사용 예시

```bash
python run_rag_update.py "AI" --kb knowledge_base.json --endpoint http://localhost:8000 --api-key YOUR_KEY
```

Kotaemon API 기대 계약
- 엔드포인트: `POST {endpoint}/upsert`
- 페이로드: `{"namespace": "<topic>", "vectors": [{"id": "...", "vector": [...], "metadata": {...}}]}`
- 응답: JSON을 기대합니다. 배포 환경에 맞춰 `mydocent/kotaemon.py`를 수정하세요.

향후 작업
- `DummyEmbeddingProvider`를 실제 임베딩 제공자(예: ONNX, Furiosa 런타임 기반 모델)로 교체
- Kotaemon의 실제 API 스펙에 맞춘 client 확장
- 병렬 업서트 및 배치 처리로 성능 개선
