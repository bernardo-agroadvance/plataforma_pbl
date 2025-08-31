// frontend/src/hooks/useBackendWS.ts
import { useEffect, useRef } from "react";

const HEARTBEAT_MS = 15_000;

/**
 * Hook para abrir o WS do backend.
 * - Usa VITE_WS_URL se definida; senão deriva de VITE_API_URL + "/ws".
 * - Heartbeat "ping"/"pong"
 * - Evita conexões duplicadas (OPEN/CONNECTING)
 * - Reconexão com backoff exponencial
 *
 * Passe um onMessage para consumir mensagens do servidor.
 */
export function useBackendWS(onMessage?: (ev: MessageEvent) => void) {
  const wsRef = useRef<WebSocket | null>(null);
  const hbTimerRef = useRef<number | null>(null);
  const closingRef = useRef(false);
  const retryRef = useRef(0); // reconexão exponencial

  useEffect(() => {
    const http = (import.meta.env.VITE_API_URL as string) ?? "http://localhost:8000";
    const overrideWs = import.meta.env.VITE_WS_URL as string | undefined;

    // se VITE_WS_URL for fornecida, usa ela; senão deriva de VITE_API_URL e soma "/ws"
    const base = overrideWs
      ? overrideWs.replace(/\/$/, "")
      : http.replace(/^http(s?):\/\//i, "ws$1://").replace(/\/$/, "") + "/ws";

    function connect() {
      // já existe uma conexão ativa ou conectando? não crie outra
      if (
        wsRef.current &&
        (wsRef.current.readyState === WebSocket.OPEN ||
          wsRef.current.readyState === WebSocket.CONNECTING)
      ) {
        return;
      }

      const ws = new WebSocket(base);
      wsRef.current = ws;

      ws.onopen = () => {
        // reset backoff
        retryRef.current = 0;
        // heartbeat
        if (hbTimerRef.current) window.clearInterval(hbTimerRef.current);
        hbTimerRef.current = window.setInterval(() => {
          try {
            ws.send("ping");
          } catch {}
        }, HEARTBEAT_MS);
        console.log("🌐 WS aberto:", base);
      };

      ws.onmessage = (ev) => {
        onMessage?.(ev);
      };

      ws.onerror = (ev) => {
        if (!closingRef.current) console.error("❌ WS error", ev);
      };

      ws.onclose = (ev) => {
        if (hbTimerRef.current) {
          window.clearInterval(hbTimerRef.current);
          hbTimerRef.current = null;
        }
        if (!closingRef.current && ev.code !== 1000) {
          console.warn("🔌 WS closed", ev.code, ev.reason);
          // backoff exponencial (1s, 2s, 4s, ... máx 30s)
          const delay = Math.min(30_000, 1_000 * Math.pow(2, retryRef.current++));
          window.setTimeout(() => {
            if (!closingRef.current) connect();
          }, delay);
        }
      };
    }

    connect();

    return () => {
      closingRef.current = true;              // <-- fix aqui (era "True")
      try {
        wsRef.current?.close(1000, "component unmount");
      } catch {}
      if (hbTimerRef.current) {
        window.clearInterval(hbTimerRef.current);
        hbTimerRef.current = null;
      }
      // libera a flag logo depois para permitir nova montagem
      setTimeout(() => (closingRef.current = false), 0);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onMessage]); // reanexa handler se mudar
}
