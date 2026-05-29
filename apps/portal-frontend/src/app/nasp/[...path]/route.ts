'use server';

import { NextRequest } from 'next/server';
import { backendRootUrl } from '../../../lib/api';

async function proxy(req: NextRequest, pathSegments: string[]) {
  const base = backendRootUrl().replace(/\/$/, '');
  const path = pathSegments.join('/');
  const url = new URL(req.url);
  const backendUrl = `${base}/nasp/${path}${url.search}`;

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

  const upstream = await fetch(backendUrl, init);
  const outHeaders = new Headers(upstream.headers);
  outHeaders.delete('location');

  return new Response(upstream.body, {
    status: upstream.status,
    headers: outHeaders,
  });
}

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function POST(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  const { path } = await ctx.params;
  return proxy(req, path);
}
