import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/trust-tech-jobs",
  assetPrefix: "/trust-tech-jobs/",
  trailingSlash: true, // Crucial for GitHub Pages sub-pages
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
