import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from mydocent.config import AppConfig, load_config, resolve_llm_client, save_config
from mydocent.embeddings import DummyEmbeddingProvider
from mydocent.furiosa import FuriosaLLMClient
from mydocent.llm_clients import NvidiaGpuLLMClient
from mydocent.news import crawl_topic, is_trusted_source, parse_rss_feed
from mydocent.rag import RAGIndexer, RAGQueryEngine
from mydocent.vector_store import KnowledgeBase


class NewsPipelineTests(unittest.TestCase):
    def test_trusted_source_detection(self):
        self.assertTrue(is_trusted_source("https://www.reuters.com/world/asia/tech"))
        self.assertTrue(is_trusted_source("https://apnews.com/article/tech"))
        self.assertFalse(is_trusted_source("https://example.com/news"))

    def test_parse_rss_feed_filters_untrusted_sources(self):
        rss_xml = """
        <rss version="2.0">
          <channel>
            <title>Test Feed</title>
            <item>
              <title>Reuters article</title>
              <link>https://www.reuters.com/world/article</link>
              <description>Reuters summary</description>
            </item>
            <item>
              <title>Untrusted article</title>
              <link>https://example.com/news</link>
              <description>Example summary</description>
            </item>
          </channel>
        </rss>
        """

        articles = parse_rss_feed(rss_xml)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Reuters article")

    def test_vector_store_updates_and_searches(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "kb.json"
            kb = KnowledgeBase(db_path)
            kb.update_topic(
                topic="AI",
                articles=[
                    {
                        "title": "AI policy debate intensifies",
                        "summary": "Governments discuss AI regulation and safety.",
                        "url": "https://www.reuters.com/ai-policy",
                        "source": "Reuters",
                    }
                ],
            )
            kb.update_topic(
                topic="AI",
                articles=[
                    {
                        "title": "New AI assistant launches",
                        "summary": "A startup unveils a new assistant for work.",
                        "url": "https://www.reuters.com/ai-assistant",
                        "source": "Reuters",
                    }
                ],
            )

            matches = kb.search("artificial intelligence regulation", top_k=3)
            self.assertGreaterEqual(len(matches), 1)
            self.assertIn("AI policy debate intensifies", matches[0]["title"])

    @patch("mydocent.furiosa.requests.post")
    def test_furiosa_client_posts_chat_completion(self, mock_post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"choices": [{"message": {"content": "서울은 한국의 수도입니다."}}]}
        mock_post.return_value = response

        client = FuriosaLLMClient("http://localhost:8000", api_key="token", model="furiosa-llm")
        answer = client.generate("도시를 말해줘")

        self.assertEqual(answer, "서울은 한국의 수도입니다.")
        self.assertEqual(mock_post.call_count, 1)

    def test_rag_query_engine_builds_answer_from_retrieved_context(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            kb_path = Path(tmp_dir) / "kb.json"
            kb = KnowledgeBase(kb_path)
            kb.update_topic(
                topic="AI",
                articles=[
                    {
                        "title": "AI policy debate intensifies",
                        "summary": "Governments discuss AI regulation and safety.",
                        "url": "https://www.reuters.com/ai-policy",
                        "source": "Reuters",
                    }
                ],
            )

            class FakeKotaemonClient:
                def query_vectors(self, namespace, query_vector, top_k=3):
                    return {
                        "matches": [
                            {
                                "id": "1",
                                "score": 0.95,
                                "metadata": {
                                    "title": "AI policy debate intensifies",
                                    "summary": "Governments discuss AI regulation and safety.",
                                    "source": "Reuters",
                                    "url": "https://www.reuters.com/ai-policy",
                                },
                            }
                        ]
                    }

            class FakeLLMClient:
                def generate(self, prompt, system_prompt=None, **kwargs):
                    return "AI 규제 논의가 활발합니다."

            engine = RAGQueryEngine(
                kb,
                embedding_provider=DummyEmbeddingProvider(dim=16),
                kotaemon_client=FakeKotaemonClient(),
                llm_client=FakeLLMClient(),
            )
            result = engine.answer("AI 규제는 어떻게 진행되나요?", namespace="AI", top_k=1)

            self.assertEqual(result["answer"], "AI 규제 논의가 활발합니다.")
            self.assertEqual(len(result["sources"]), 1)
            self.assertIn("AI policy debate intensifies", result["sources"][0]["title"])

    def test_config_persists_selected_provider(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config = AppConfig(provider="nvidia_gpu", endpoint="http://nvidia:8000", model="mistral")
            save_config(config, config_path)

            loaded = load_config(config_path)
            self.assertEqual(loaded.provider, "nvidia_gpu")
            self.assertEqual(loaded.endpoint, "http://nvidia:8000")
            self.assertEqual(loaded.model, "mistral")

    def test_resolve_llm_client_returns_selected_backend(self):
        config = AppConfig(provider="nvidia_gpu", endpoint="http://gpu:8000", model="llama")
        client = resolve_llm_client(config)
        self.assertIsInstance(client, NvidiaGpuLLMClient)


if __name__ == "__main__":
    unittest.main()
