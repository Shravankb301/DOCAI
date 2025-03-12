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
  }
};

module.exports = nextConfig; 