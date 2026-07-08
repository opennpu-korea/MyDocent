# Usage

Requirements
- Python 3.10+
- `requests` 패키지 (RSS 피드 요청)

Install

```bash
pip install -r requirements.txt  # 프로젝트가 requirements.txt를 제공하는 경우
pip install requests
```

Collect news and update knowledge base

```bash
python run_daily_update.py "AI"
# --db 옵션으로 저장 위치 지정 가능: --db path/to/knowledge_base.json
```

Scheduling (crontab example)

```cron
# 매일 새벽 03:00에 "AI" 주제 갱신
0 3 * * * cd /workspaces/MyDocent && /usr/bin/python3 run_daily_update.py "AI" --db knowledge_base.json
```

Notes
- 뉴스는 RSS를 통해 수집하며, `mydocent/news.py`의 `TRUSTED_DOMAINS`로 소스를 제한합니다.
- 현재 벡터화는 간단한 토큰 카운트 기반이며, 추후 임베딩 기반 벡터 DB(FAISS, Milvus 등)로 교체 가능.
