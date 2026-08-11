/**
 * 应用部署的子路径前缀（与 next.config.js 中的 basePath 保持一致）。
 * 通过 NEXT_PUBLIC_BASE_PATH 环境变量在构建时注入覆盖，默认 /programs/medinexus。
 * 前端页面路由、API 请求、WebSocket 连接的地址均以此为基础。
 */
export const BASE_PATH =
  process.env.NEXT_PUBLIC_BASE_PATH || "/programs/medinexus";
