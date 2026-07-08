import json
import tempfile
import unittest
from pathlib import Path

from mydocent.news import crawl_topic, is_trusted_source, parse_rss_feed
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


if __name__ == "__main__":
    unittest.main()
