"""Phase 6 realtime SSE smoke test."""
from django.test import TestCase


class RealtimeStreamTests(TestCase):
    def test_sse_stream_returns_event_stream(self):
        response = self.client.get("/api/v1/realtime/stream/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response["Content-Type"])
