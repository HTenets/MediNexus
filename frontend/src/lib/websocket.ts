"use client";

export type WsEventType =
  | "agent_start"
  | "token"
  | "agent_end"
  | "error"
  | "info";

export interface WsEvent {
  event: WsEventType;
  data: Record<string, unknown>;
}

type EventCallback = (event: WsEvent) => void;

/**
 * ConsultationSocket — manages a WebSocket connection for streaming consultations.
 *
 * In development, connects directly to the backend (localhost:8000).
 * In production, connects to the same host (reverse proxy handles /ws/ -> backend).
 */
function getWsBase(): string {
  if (typeof window === "undefined") return "ws://localhost:8000";

  // Production: connect directly to Render backend
  if (
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
  ) {
    // Use NEXT_PUBLIC_WS_URL env var, or default to Render
    const envUrl =
      typeof process !== "undefined" &&
      (process.env as Record<string, string>)["NEXT_PUBLIC_WS_URL"];
    if (envUrl) return envUrl;
    return "wss://medinexus-api.onrender.com";
  }

  // Development: connect to local backend
  return "ws://localhost:8000";
}

export class ConsultationSocket {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private listeners: Map<string, EventCallback[]> = new Map();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private maxRetries = 3;
  private retryCount = 0;
  private onStatusChange?: (connected: boolean) => void;

  constructor(sessionId: string) {
    this.sessionId = sessionId;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    const base = getWsBase();
    const url = `${base}/ws/${this.sessionId}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.retryCount = 0;
      this.onStatusChange?.(true);
    };

    this.ws.onmessage = (msg: MessageEvent) => {
      try {
        const event: WsEvent = JSON.parse(msg.data);
        // Dispatch to specific event listeners
        const cbs = this.listeners.get(event.event) || [];
        cbs.forEach((cb) => cb(event));
        // Dispatch to wildcard listeners
        const allCbs = this.listeners.get("*") || [];
        allCbs.forEach((cb) => cb(event));
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = () => {
      this.onStatusChange?.(false);
      this.scheduleReconnect();
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    this.retryCount = this.maxRetries;
    this.ws?.close();
    this.ws = null;
  }

  send(data: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  on(event: WsEventType | "*", callback: EventCallback): () => void {
    if (!this.listeners.has(event)) this.listeners.set(event, []);
    this.listeners.get(event)!.push(callback);
    return () => {
      const arr = this.listeners.get(event);
      if (arr) {
        const idx = arr.indexOf(callback);
        if (idx >= 0) arr.splice(idx, 1);
      }
    };
  }

  setConnectionHandler(handler: (connected: boolean) => void): void {
    this.onStatusChange = handler;
  }

  private scheduleReconnect(): void {
    if (this.retryCount >= this.maxRetries) return;
    this.retryCount++;
    const delay = Math.min(1000 * Math.pow(2, this.retryCount), 10000);
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }
}

// Factory function
export function createConsultationSocket(sessionId: string): ConsultationSocket {
  return new ConsultationSocket(sessionId);
}
