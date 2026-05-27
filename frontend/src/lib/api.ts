const API_BASE = "/api/v1";

export async function fetchApi(path: string, options?: RequestInit) {
  return fetch(`${API_BASE}${path}`, options);
}
