const path = require('path');

const backendRoot =
  process.env.TRISLA_BACKEND_INTERNAL_URL ||
  process.env.TRISLA_API_BASE_URL ||
  'http://trisla-portal-backend:8001';

const backendBase = backendRoot.replace(/\/api\/v1\/?$/, '').replace(/\/$/, '');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  outputFileTracingRoot: path.join(__dirname),
  skipTrailingSlashRedirect: true,
  skipMiddlewareUrlNormalize: true,
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/nasp/:path*',
        destination: `${backendBase}/nasp/:path*`,
      },
      {
        source: '/api/v1/:path*',
        destination: `${backendBase}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
