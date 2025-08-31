// frontend/src/lib/api.ts
const fallback = typeof window !== "undefined" ? "http://localhost:8000" : "http://localhost:8000";
export const API_URL =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") || fallback;

/** fetch básico que já envia cookies e trata base URL */
export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const url = `${API_URL}${path.startsWith("/") ? "" : "/"}${path}`;
  const resp = await fetch(url, {
    credentials: "include", // <- envia cookies HttpOnly
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  return resp;
}

/** atalho para JSON, lançando erro se !ok */
export async function apiJson<T = any>(path: string, init?: RequestInit): Promise<T> {
  const resp = await apiFetch(path, init);
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const msg = (data && (data.detail || data.message)) || `HTTP ${resp.status}`;
    throw new Error(String(msg));
  }
  return data as T;
}

/** monta URL do WebSocket a partir do API_URL (ou usa VITE_WS_URL) */
export function makeWsUrl(path = "/ws") {
  const override = (import.meta.env.VITE_WS_URL as string | undefined)?.replace(/\/$/, "");
  if (override) return override;
  const base = API_URL.replace(/^http/, "ws").replace(/\/$/, "");
  return `${base}${path.startsWith("/") ? "" : "/"}${path}`;
}
