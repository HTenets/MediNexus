/** @type {import('next').NextConfig} */
// 应用部署的子路径前缀（如 htenets.top/programs/medinexus）
const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || "/programs/medinexus";

const nextConfig = {
  // 子路径部署：所有页面路由、静态资源自动带上该前缀
  basePath: BASE_PATH,
  async rewrites() {
    const apiHost = process.env.NEXT_PUBLIC_API_HOST || (process.env.NODE_ENV === "production"
      ? "http://localhost:80"
      : "http://localhost:8000");

    return [
      {
        // source 已显式包含 basePath，需 basePath: false 防止 Next.js 二次拼接；
        // 生产环境由 Nginx 直接路由 /programs/medinexus/api/，此 rewrite 仅本地开发生效
        source: `${BASE_PATH}/api/v1/:path*`,
        destination: `${apiHost}/api/v1/:path*`,
        basePath: false,
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
