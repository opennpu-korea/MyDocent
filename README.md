# MyDocent
AI 에이전트 기반 RAG 솔루션 개발 연구, 미술관 관광지 등 설명해주는 AI 도슨트

## 뉴스 기반 지식베이스 자동 갱신
특정 주제어를 입력하면, 공신력 있는 매체만을 대상으로 뉴스 크롤링을 수행하고 매일 밤 반복 실행 가능한 형태로 지식베이스를 갱신하는 기본 파이프라인을 추가했습니다.

### 포함 기능
- 공신력 있는 뉴스 소스 필터링
- RSS 기반 뉴스 수집
- 주제별 기사 저장 및 중복 제거
- 검색 가능한 JSON 기반 지식베이스
- 매일 갱신용 실행 스크립트

### 실행 방법
```bash
python run_daily_update.py "AI"
```

### RAG + LLM 백엔드 선택 실행
1. 관리자 UI로 하드웨어 선택
```bash
python run_admin_ui.py
```
이 UI에서 `furiosa_npu` 또는 `nvidia_gpu`를 선택하고, 엔드포인트/모델 정보를 저장하면 이후 실행은 자동으로 해당 백엔드를 사용합니다.

2. 뉴스 지식베이스 수집
```bash
python run_daily_update.py "AI"
```

3. Kotaemon 벡터 저장소와 선택된 LLM을 이용해 질의
```bash
python run_rag_chat.py "AI 규제는 어떻게 진행되나요?" \
  --namespace AI
```

4. 특정 주제를 Kotaemon에 인덱싱
```bash
python run_rag_update.py "AI"
```

### 테스트
```bash
python -m unittest discover -s tests -q
```
