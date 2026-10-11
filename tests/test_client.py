"""Billing-sensitive behavior and observed task response shape."""

import os
import json
import unittest
from unittest.mock import Mock, patch

import client


class SunoClientTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"ACEDATACLOUD_API_KEY": "test-key"})
        self.env.start()
        self.addCleanup(self.env.stop)

    @patch("client.requests.post")
    def test_submit_once_and_preserves_task_id(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = {"success": True, "task_id": "task-123", "trace_id": "trace-123"}
        self.assertEqual(client.submit("piano", "chirp-v6", True), ("task-123", "trace-123"))
        post.assert_called_once()
        args, kwargs = post.call_args
        self.assertEqual(args[0], "https://api.acedata.cloud/suno/audios")
        self.assertTrue(kwargs["json"]["async"])
        self.assertFalse(kwargs["allow_redirects"])

    @patch("client.requests.post")
    def test_submission_network_error_is_not_retried_or_leaked(self, post):
        post.side_effect = client.requests.Timeout("Authorization: Bearer test-key")
        with self.assertRaises(client.SunoError) as caught:
            client.submit("piano", "chirp-v6", True)
        self.assertEqual(post.call_count, 1)
        self.assertNotIn("test-key", str(caught.exception))

    @patch("client.requests.post")
    def test_same_task_pending_then_terminal(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.side_effect = [
            {"id": "task-123", "finished_at": None, "response": None},
            {"id": "task-123", "finished_at": "2026-10-11T01:00:00Z",
             "response": {"success": True, "data": [{"audio_url": "https://cdn.acedata2.cloud/suno/a.mp3"}]}},
        ]
        self.assertEqual(client.retrieve_once("task-123")[0], "pending")
        status, url, _ = client.retrieve_once("task-123")
        self.assertEqual(status, "succeeded")
        self.assertEqual(url, "https://cdn.acedata2.cloud/suno/a.mp3")
        for call in post.call_args_list:
            self.assertEqual(call.kwargs["json"]["id"], "task-123")
            self.assertEqual(call.args[0], "https://api.acedata.cloud/suno/tasks")

    @patch("client.requests.post")
    def test_query_can_retry_transient_connection_without_new_submission(self, post):
        ok = Mock(status_code=200)
        ok.json.return_value = {"id": "task-123", "finished_at": None, "response": None}
        post.side_effect = [client.requests.Timeout(), ok]
        with patch("client.time.sleep"):
            self.assertEqual(client.retrieve_once("task-123")[0], "pending")
        self.assertEqual(post.call_count, 2)
        for call in post.call_args_list:
            self.assertEqual(call.args[0], "https://api.acedata.cloud/suno/tasks")

    @patch("client.requests.post")
    def test_failed_task_does_not_claim_success(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = {
            "id": "task-123", "finished_at": "2026-10-11T01:00:00Z",
            "response": {"success": False, "error": "private upstream detail"},
        }
        with self.assertRaises(client.SunoError) as caught:
            client.retrieve_once("task-123")
        self.assertNotIn("private upstream", str(caught.exception))

    @patch("client.requests.get")
    def test_audio_loader_rejects_arbitrary_host_before_network(self, get):
        for url in ["http://cdn.acedata2.cloud/a.mp3", "https://127.0.0.1/a.mp3",
                    "https://cdn.acedata2.cloud.evil.test/a.mp3"]:
            with self.assertRaises(client.SunoError):
                client.download_audio(url)
        get.assert_not_called()

    @patch("client.requests.get")
    def test_audio_download_can_retry_without_resubmitting(self, get):
        ok = Mock(status_code=200, headers={"Content-Length": "3"})
        ok.__enter__ = Mock(return_value=ok)
        ok.__exit__ = Mock(return_value=False)
        ok.iter_content.return_value = [b"mp3"]
        get.side_effect = [client.requests.exceptions.SSLError(), ok]
        with patch("client.time.sleep"):
            self.assertEqual(client.download_audio("https://cdn.acedata2.cloud/suno/a.mp3"), b"mp3")
        self.assertEqual(get.call_count, 2)

    @patch("client.requests.post")
    def test_legacy_audio_model_is_accepted_once(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = {"task_id": "task-legacy"}
        self.assertEqual(client.submit("piano", "chirp-v3-0", True)[0], "task-legacy")
        self.assertEqual(post.call_count, 1)
        self.assertEqual(post.call_args.kwargs["json"]["model"], "chirp-v3-0")

    @patch("client.requests.post")
    def test_lyrics_model_submits_once_and_reuses_task_id(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.side_effect = [
            {"task_id": "lyrics-123", "trace_id": "trace-123"},
            {"finished_at": "2026-10-12T00:00:00Z", "response": {
                "data": {"title": "Song", "lyrics": "[Verse] Hello", "supplier": "private"}}},
        ]
        self.assertEqual(client.generate_lyrics("hope", "remi-v1"), ("pending", "lyrics-123", "", "trace-123"))
        status, task_id, lyrics_json, _ = client.retrieve_lyrics_once("lyrics-123")
        self.assertEqual((status, task_id), ("succeeded", "lyrics-123"))
        self.assertEqual(json.loads(lyrics_json)["data"]["title"], "Song")
        self.assertNotIn("supplier", lyrics_json)
        self.assertEqual(post.call_args_list[0].args[0], "https://api.acedata.cloud/suno/lyrics")
        self.assertEqual(post.call_args_list[1].kwargs["json"]["id"], "lyrics-123")

    @patch("client.requests.post")
    def test_lyrics_submission_timeout_does_not_retry(self, post):
        post.side_effect = client.requests.Timeout()
        with self.assertRaises(client.SunoError):
            client.generate_lyrics("hope", "default")
        post.assert_called_once()

    @patch("client.requests.post")
    def test_completed_lyrics_task_needs_actual_lyrics(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = {
            "finished_at": "2026-10-12T00:00:00Z", "response": {"status": "succeeded"}
        }
        with self.assertRaises(client.SunoError):
            client.retrieve_lyrics_once("lyrics-123")


if __name__ == "__main__":
    unittest.main()
