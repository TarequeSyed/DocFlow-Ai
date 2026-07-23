import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        // Communicates internally through Docker to your backend service container
        destination: 'http://backend:8000/api/v1/:path*', 
      },
    ];
  },
};

export default nextConfig;