import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  trailingSlash: true,
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "127.0.0.1:3000","www.godblessedme.com"],
    },
  },
};

export default nextConfig;