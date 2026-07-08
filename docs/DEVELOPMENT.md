# Development Notes

현재 개발 이력과 향후 작업 항목들을 기록합니다.

현재 상태
- `run_daily_update.py`: 주제어 입력 받아 `crawl_topic` 호출 후 `KnowledgeBase.update_topic`로 갱신합니다.
- `mydocent/news.py`: RSS 파싱 및 `TRUSTED_DOMAINS` 기반 필터링, Google News 검색 RSS 사용 기본값.
- `mydocent/vector_store.py`: JSON 저장, 중복 병합, 토큰 카운트 기반 벡터 및 코사인 유사도 검색을 제공합니다.

테스트
- 기본 단위 테스트는 `tests/test_pipeline.py`에 있습니다. 로컬에서 실행하려면:

```bash
python -m unittest discover -s tests -q
```

향후 개선 아이디어
- 신뢰성 향상: 더 많은 공신력 있는 도메인 추가 및 신뢰도 점수 도입
- 크롤링 개선: RSS 외에 사이트 직접 스크래핑 또는 뉴스 API 연동 (비용/정책 고려)
- 벡터 DB 교체: 임베딩 모델(semantic) 도입 후 FAISS/Milvus 같은 벡터 저장소로 교체
- 장애복구: 네트워크 실패 대비 백오프/재시도, 로깅 및 모니터링 추가
- 스케줄러: 시스템d 타이머 또는 Kubernetes CronJob으로 이전

- RAG 인덱싱: `mydocent/rag.py`, `mydocent/embeddings.py`, `mydocent/kotaemon.py` 및 `run_rag_update.py` 추가
	- `DummyEmbeddingProvider`로 기본 동작을 제공하며, 향후 Furiosa/ONNX 기반 임베딩으로 교체 가능
	- Kotaemon HTTP API로 벡터 업서트하는 클라이언트 포함

문서 업데이트 규칙
- 주요 변경사항은 `docs/CHANGELOG.md`에 항목 추가
- 아키텍처 변경은 `docs/ARCHITECTURE.md` 갱신
- 사용 방법 변경은 `docs/USAGE.md` 갱신
