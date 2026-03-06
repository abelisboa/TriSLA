const BASE_URL =
  typeof window !== 'undefined'
    ? (window as any).__ENV__?.BACKEND_URL || '/api/v1'
    : process.env.BACKEND_URL || 'http://trisla-portal-backend:8001/api/v1';

export async function apiFetch(path: string, options: RequestInit = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
