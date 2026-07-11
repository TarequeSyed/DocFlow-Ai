import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        // Proxy all /api/* requests to the backend Docker service.
        // In Docker: "backend:8000" resolves via Docker DNS.
        // In browser: requests go to Next.js dev server which proxies them.
        source: "/api/:path*",
        destination: "http://backend:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
