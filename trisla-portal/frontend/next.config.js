/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  experimental: {
    serverActions: { allowedOrigins: ['*'] }
  },
  // NEXT_PUBLIC_* são injetadas no build time
  // Para client-side (browser via túnel SSH): localhost:32002
  // Para server-side (SSR no cluster): será sobrescrito via API_URL
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:32002/api/v1',
  },
};

module.exports = nextConfig
