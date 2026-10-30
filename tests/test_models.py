import os
import unittest
from unittest.mock import patch

from agent_course.models import ModelConfig, ModelConfigError


class ModelConfigTests(unittest.TestCase):
    def test_openrouter_chat_and_openai_embedding_can_be_split(self):
        values = {
            "AGENT_COURSE_CHAT_PROVIDER": "openrouter",
            "AGENT_COURSE_EMBED_PROVIDER": "openai-compatible",
            "AGENT_COURSE_CHAT_MODEL": "openai/gpt-4o-mini",
            "AGENT_COURSE_EMBED_MODEL": "text-embedding-3-small",
            "AGENT_COURSE_CHAT_API_KEY": "chat-key",
            "AGENT_COURSE_EMBED_API_KEY": "embed-key",
        }
        with patch.dict(os.environ, values, clear=False):
            config = ModelConfig.from_env()
        chat_url, chat_payload, chat_headers = config.chat_request()
        embed_url, embed_payload, embed_headers = config.embed_request()
        self.assertIn("openrouter.ai", chat_url)
        self.assertEqual(chat_payload["model"], "openai/gpt-4o-mini")
        self.assertEqual(chat_headers["Authorization"], "Bearer chat-key")
        self.assertTrue(embed_url.endswith("/embeddings"))
        self.assertEqual(embed_payload["model"], "text-embedding-3-small")
        self.assertEqual(embed_headers["Authorization"], "Bearer embed-key")

    def test_missing_configuration_fails_without_fallback_model(self):
        names = [
            "AGENT_COURSE_PROVIDER", "AGENT_COURSE_CHAT_PROVIDER",
            "AGENT_COURSE_EMBED_PROVIDER", "AGENT_COURSE_CHAT_MODEL",
            "AGENT_COURSE_EMBED_MODEL",
        ]
        with patch.dict(os.environ, {name: "" for name in names}, clear=False):
            with self.assertRaises(ModelConfigError):
                ModelConfig.from_env()


if __name__ == "__main__":
    unittest.main()
