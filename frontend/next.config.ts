import type { NextConfig } from "next";

const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*', // For browser local dev
        // OR use 'http://backend:8000/api/v1/:path*' if Next.js handles the proxy entirely server-side
      },
    ];
  },
};

module.exports = nextConfig;