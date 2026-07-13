# MediNexus 前后端打通 - Product Requirement Document

## Overview
- **Summary**: 将前端页面与后端 REST API 进行全面集成，替换现有的 mock 数据调用，建立完整的数据链路和用户会话管理，确保用户在各页面间的交互能够正确调用后端服务。
- **Purpose**: 解决当前前端大部分页面使用 mock 数据的问题，实现真实的数据加载、存储和交互，使整个系统能够端到端运行。
- **Target Users**: MediNexus 平台的所有终端用户（患者、医生）

## Goals
- 重构前端 API 库，支持完整的 REST API 调用
- 将仪表盘页面连接到后端患者数据接口
- 将患者管理页面连接到后端患者 CRUD 接口
- 将健康记录页面连接到后端病历接口
- 确保问诊流程（consultation → analysis → review → summary）通过 WebSocket 正常工作
- 实现用户认证和会话管理
- 建立统一的错误处理和加载状态

## Non-Goals (Out of Scope)
- 不修改后端 API 接口定义（保持现有接口不变）
- 不修改后端业务逻辑和数据模型
- 不修改问诊流程的 Agent 逻辑
- 不新增后端 API 端点
- 不进行数据库迁移或数据初始化

## Background & Context

### 当前架构
- **后端**: FastAPI 服务，运行在 localhost:8000
  - REST API: `/api/v1/consult/*`, `/api/v1/patients/*`, `/api/v1/records/*`, `/api/v1/health`
  - Mock API: `/api/mock/*`（开发阶段使用）
  - WebSocket: `/ws/{session_id}`（问诊实时通信）

- **前端**: Next.js 14 App Router，运行在 localhost:3000
  - API 代理: 通过 next.config.js 将 `/api/*` 代理到后端
  - 当前状态: 大部分页面使用 `/api/mock/*` 端点

### 现有 API 使用情况
| 前端页面 | 当前 API | 目标 API |
|----------|----------|----------|
| dashboard | `/api/mock/dashboard/{patient_id}` | `/api/v1/records/patient/{patient_id}` |
| patients | Mock 数据 | `/api/v1/patients/` |
| records | Mock 数据 | `/api/v1/records/patient/{patient_id}` |
| consultation | WebSocket `/ws/{session_id}` | 保持不变 |
| consultation/analysis | `/api/mock/knowledge-*` | 保持 mock（知识库查询） |
| consultation/review | `/api/mock/consultation/{id}` | `/api/v1/consult/{id}` |
| summary | `/api/mock/consultation/{id}` | `/api/v1/consult/{id}` |
| system-status | `/api/mock/system-status` | `/api/v1/health` |

## Functional Requirements

### FR-1: 重构前端 API 库
- 扩展 `src/lib/api.ts`，添加所有后端 REST API 调用方法
- 支持 GET/POST/PUT/DELETE 请求
- 添加请求拦截器，自动处理认证 token
- 添加响应处理，统一错误格式化

### FR-2: 用户认证与会话管理
- 实现登录 API 调用（POST /api/v1/auth/login）
- 实现 token 存储和自动注入（localStorage）
- 实现登录状态管理（useAuth hook）
- 实现自动登出和 token 过期处理

### FR-3: 仪表盘页面集成
- 替换 mock 数据调用为真实 API
- 从后端获取患者生命体征数据
- 从后端获取健康风险和 AI 建议
- 实现加载状态和错误处理

### FR-4: 患者管理页面集成
- 替换 mock 数据为真实 API
- 实现患者列表分页和搜索
- 实现患者详情查看
- 实现患者创建/编辑/删除

### FR-5: 健康记录页面集成
- 替换 mock 数据为真实 API
- 从后端获取患者病历记录
- 实现病历详情查看
- 实现上传报告功能

### FR-6: 问诊流程集成
- 确保 WebSocket 连接正常（已实现）
- 问诊完成后正确跳转到 summary 页面
- Summary 页面从后端获取完整问诊记录
- Review 页面从后端获取问诊状态

### FR-7: 系统状态页面集成
- 替换 mock 数据为真实 `/api/v1/health` 接口

### FR-8: 个人中心页面集成
- 从后端获取用户个人资料
- 从后端获取健康指标数据

## Non-Functional Requirements

### NFR-1: 错误处理
- 所有 API 调用必须有错误处理
- 网络错误、4xx、5xx 错误必须显示友好提示
- 加载状态必须清晰可见

### NFR-2: 响应式设计
- 所有集成页面必须保持响应式布局
- 移动端和桌面端都必须正常显示

### NFR-3: 代码质量
- 遵循现有代码风格和组件使用模式
- 保持 TypeScript 类型安全
- 使用统一的 API 调用方式

### NFR-4: 性能优化
- API 调用必须有加载状态
- 避免不必要的重复请求
- 使用 React Query 或类似机制进行数据缓存

## Constraints
- **技术栈**: Next.js 14 (App Router), React 18, TypeScript, TailwindCSS 3
- **后端**: FastAPI, Python
- **API 路径**: `/api/v1/*`（通过 next.config.js 代理）
- **WebSocket**: `ws://localhost:8000/ws/{session_id}`
- **认证**: JWT Token（localStorage 存储）

## Assumptions
- 后端服务运行在 localhost:8000
- 前端通过 next.config.js 的 rewrites 配置代理 API 请求
- 后端 API 接口定义保持不变
- 开发环境使用 mock 模式运行后端

## Acceptance Criteria

### AC-1: API 库重构完成
- **Given**: 前端代码需要调用后端 API
- **When**: 导入并使用 api.ts 中的方法
- **Then**: 能够成功发起 GET/POST/PUT/DELETE 请求，自动处理认证，统一错误处理
- **Verification**: `programmatic`

### AC-2: 用户认证功能正常
- **Given**: 用户访问需要认证的页面
- **When**: 用户登录或未登录
- **Then**: 登录后获取 token 并存储，未登录时重定向到登录页
- **Verification**: `human-judgment`

### AC-3: 仪表盘页面集成完成
- **Given**: 用户访问仪表盘页面
- **When**: 页面加载
- **Then**: 从后端获取真实患者数据，显示生命体征、健康风险、AI 建议
- **Verification**: `human-judgment`

### AC-4: 患者管理页面集成完成
- **Given**: 用户访问患者管理页面
- **When**: 查看、搜索、创建、编辑、删除患者
- **Then**: 所有操作通过后端 API 完成，数据实时更新
- **Verification**: `human-judgment`

### AC-5: 健康记录页面集成完成
- **Given**: 用户访问健康记录页面
- **When**: 查看病历记录、上传报告
- **Then**: 病历数据从后端获取，上传报告调用后端 API
- **Verification**: `human-judgment`

### AC-6: 问诊流程完整
- **Given**: 用户开始问诊
- **When**: 完成问诊流程（triage → doctor → review → followup）
- **Then**: 各阶段数据正确传递，最终跳转到 summary 页面显示完整报告
- **Verification**: `human-judgment`

### AC-7: 项目构建成功
- **Given**: 完成所有集成工作
- **When**: 执行 npm run build
- **Then**: 项目构建成功，无 TypeScript 错误
- **Verification**: `programmatic`

## Open Questions
- [ ] 后端是否已经实现登录认证 API？需要确认 `/api/v1/auth/login` 接口是否存在
- [ ] 是否需要使用 React Query 进行数据缓存？当前项目未使用状态管理库
- [ ] 用户角色如何区分（患者/医生）？是否需要权限控制
- [ ] 上传报告的后端 API 是否已实现？需要确认文件上传接口
