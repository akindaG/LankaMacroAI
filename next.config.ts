import type { NextConfig } from 'next';
const config: NextConfig = {
  agentRules: false,
  distDir: process.env.NODE_ENV === 'development' ? '.next-dev' : '.next',
  poweredByHeader: false,
  async rewrites() {
    const backend = process.env.BACKEND_URL || 'http://127.0.0.1:8008';
    return [{ source: '/api/:path*', destination: `${backend}/api/:path*` }];
  },
};
export default config;
