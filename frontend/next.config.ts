import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    viewTransition: true, // Enable smooth page transitions
  },
};

export default nextConfig;
