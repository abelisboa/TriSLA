'use server';

import { NextRequest } from 'next/server';

// Root do backend (sem /api/v1). Em K8s: BACKEND_URL=http://trisla-portal-backend:8001
const BACKEND_ROOT = (process.env.BACKEND_URL || 'http://trisla-portal-backend:8001').replace(/\/api\/v1\/?$/, '');

function backendUrlFromPath(path: string): string {
  const base = BACKEND_ROOT.endsWith('/') ? BACKEND_ROOT.slice(0, -1) : BACKEND_ROOT;
  const p = path.startsWith('/') ? path.slice(1) : path;
  // Backend expõe /nasp/diagnostics na raiz; o resto sob /api/v1
  if (p.startsWith('nasp/')) return `${base}/${p}`;
  return `${base}/api/v1/${p}`;
}

async function proxy(req: NextRequest) {
  const url = new URL(req.url);
  const path = url.pathname.replace(/^\/api\/v1\/?/, '');
  const backendUrl = backendUrlFromPath(path);

  const headers = new Headers(req.headers);
  headers.delete('host');
  headers.delete('connection');

  const init: RequestInit = {
    method: req.method,
    headers,
    redirect: 'follow',
  };

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    init.body = await req.text();
  }

  const upstream = await fetch(backendUrl + url.search, init);
  const outHeaders = new Headers(upstream.headers);
  outHeaders.delete('location');

  return new Response(upstream.body, {
    status: upstream.status,
    headers: outHeaders,
  });
}

export async function GET(req: NextRequest) {
  return proxy(req);
}

export async function POST(req: NextRequest) {
  return proxy(req);
}
