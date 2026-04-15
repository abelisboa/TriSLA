const path = require('path');

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
        source: '/api/v1/:path*',
        destination: 'http://trisla-portal-backend:8001/api/v1/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
