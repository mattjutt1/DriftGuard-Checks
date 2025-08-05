import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  turbopack: {
    // Enable Turbopack for faster builds
  },
  eslint: {
    // Disable ESLint during builds for production deployment
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable type checking during builds for production deployment
    ignoreBuildErrors: true,
  },
  experimental: {
    // Enable modern features
    optimizePackageImports: ['lucide-react'],
  },
}

export default nextConfig