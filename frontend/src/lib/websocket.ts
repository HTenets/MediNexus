"use client";

import { getToken } from "./auth";
import { BASE_PATH } from "./config";

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

  // Dev: connect directly to the local backend
  if (
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
  ) {
    return "ws://localhost:8000";
  }

  // Production: connect to the same host the page is served from.
  // Nginx reverse-proxies /ws/ -> backend, so no hardcoded external URL.
  const envUrl =
    typeof process !== "undefined" &&
    (process.env as Record<string, string>)["NEXT_PUBLIC_WS_URL"];
  if (envUrl) return envUrl;

  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  // 生产环境：连接与页面同源、且带上子路径前缀（Nginx 反代 /programs/medinexus/ws/ -> backend）
  return `${proto}//${window.location.host}${BASE_PATH}`;
}

export class ConsultationSocket {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private listeners: Map<string, EventCallback[]> = new Map();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private maxRetries = 3;
  private retryCount = 0;
  private onStatusChange?: (connected: boolean) => void;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private pongTimeout: ReturnType<typeof setTimeout> | null = null;
  private static readonly HEARTBEAT_INTERVAL = 30000;

  constructor(sessionId: string) {
    this.sessionId = sessionId;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    const base = getWsBase();
    const token = getToken();
    const tokenQuery = token ? `?token=${encodeURIComponent(token)}` : "";
    const url = `${base}/ws/${this.sessionId}${tokenQuery}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.retryCount = 0;
      this.onStatusChange?.(true);
      this.startHeartbeat();
    };

    this.ws.onmessage = (msg: MessageEvent) => {
      try {
        const event: WsEvent = JSON.parse(msg.data);
        // Any message from server counts as a pong for heartbeat purposes
        this.resetPongTimeout();
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
      this.stopHeartbeat();
      this.scheduleReconnect();
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    this.stopHeartbeat();
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

  // ── Heartbeat to detect stale connections ───────────────────────────── //
  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState !== WebSocket.OPEN) return;
      this.ws.send(JSON.stringify({ type: "ping" }));
      this.pongTimeout = setTimeout(() => {
        // No response within 10s — connection is stale, force reconnect
        this.ws?.close();
      }, 10000);
    }, ConsultationSocket.HEARTBEAT_INTERVAL);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
    if (this.pongTimeout) clearTimeout(this.pongTimeout);
    this.heartbeatTimer = null;
    this.pongTimeout = null;
  }

  private resetPongTimeout(): void {
    if (this.pongTimeout) {
      clearTimeout(this.pongTimeout);
      this.pongTimeout = null;
    }
  }
}

// Factory function
export function createConsultationSocket(sessionId: string): ConsultationSocket {
  return new ConsultationSocket(sessionId);
}
