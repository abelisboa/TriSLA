/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  experimental: {
    serverActions: { allowedOrigins: ['*'] }
  },
  async rewrites() {
    // IMPORTANTE:
    // - No cluster: o Next roda dentro do pod, então pode falar com o Service do backend.
    // - Externamente: seu navegador chama /api/v1 no MESMO host do Portal (localhost:3001 via túnel).
    const backendBase =
      process.env.BACKEND_URL || "http://trisla-portal-backend:8001/api/v1";

    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendBase}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig
