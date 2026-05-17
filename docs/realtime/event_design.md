# Realtime Event Design

## Backend (additive)

- `GET /api/v1/realtime/stream/` — Server-Sent Events
- Polls `EventStreamService.consume_event()` every 5 seconds
- Redis pub/sub hook in `EventStreamService._broadcast()` when `REDIS_URL` is set

## Frontend

- `src/realtime/sse-client.ts` — reconnect with exponential backoff
- `useRealtime()` hook — last 100 messages for dashboard refresh triggers

## Future

- Django Channels / WebSocket upgrade path
- Kafka consumer for national-scale fan-out
