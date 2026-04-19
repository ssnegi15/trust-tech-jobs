import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/trust-tech-jobs",
  assetPrefix: "/trust-tech-jobs/",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
