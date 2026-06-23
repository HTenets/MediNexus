/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination:
          process.env.NODE_ENV === "production"
            ? "https://medinexus-api.onrender.com/api/v1/:path*"
            : "http://localhost:8000/api/v1/:path*",
      },
    ];
  },
};
module.exports = nextConfig;
