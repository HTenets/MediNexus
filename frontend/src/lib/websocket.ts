export function createWebSocket(sessionId: string): WebSocket {
  return new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
}
