import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'www.camara.leg.br',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
