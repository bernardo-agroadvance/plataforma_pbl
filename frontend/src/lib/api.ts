// frontend/src/lib/api.ts
const fallback = typeof window !== "undefined" ? "http://localhost:8000" : "http://localhost:8000";
export const API_URL =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") || fallback;

/** fetch básico que adiciona o Token JWT no cabeçalho e trata a base URL */
export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const url = `${API_URL}${path.startsWith("/") ? "" : "/"}${path}`;

  const token = localStorage.getItem('token');

  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string>),
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const resp = await fetch(url, {
    ...init,
    headers,
  });

  if (resp.status === 401 && window.location.pathname !== '/') {
    localStorage.clear();
    window.location.href = '/';
  }

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