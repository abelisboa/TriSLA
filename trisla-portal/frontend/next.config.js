/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  experimental: {
    serverActions: { allowedOrigins: ['*'] }
  },
  // NEXT_PUBLIC_* são injetadas no build time
  // A variável deve ser passada via ARG no Dockerfile ou via env durante o build
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://trisla-portal-backend:8001/api/v1',
  },
};

module.exports = nextConfig
