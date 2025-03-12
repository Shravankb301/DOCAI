/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  compiler: {
    // Enables the styled-components SWC transform
    styledComponents: true
  },
  // Add environment variable for API URL
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
  },
  // Disable source maps in production to reduce bundle size
  productionBrowserSourceMaps: false,
  // Ensure output is optimized for Vercel
  output: 'standalone'
};

module.exports = nextConfig; 