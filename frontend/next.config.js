/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const apiHost = process.env.NEXT_PUBLIC_API_HOST || process.env.NODE_ENV === "production"
      ? "http://localhost:80"
      : "http://localhost:8000";
    
    return [
      {
        source: "/api/:path*",
        destination: `${apiHost}/api/v1/:path*`,
      },
    ];
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": require("path").resolve(__dirname, "./src"),
    };
    return config;
  },
};

module.exports = nextConfig;
