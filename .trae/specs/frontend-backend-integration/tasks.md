# MediNexus 前后端打通 - 实施计划

## [x] Task 1: 重构前端 API 库
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 扩展 `src/lib/api.ts`，添加所有后端 REST API 调用方法
  - 实现统一的请求包装，支持 GET/POST/PUT/DELETE
  - 添加认证 token 自动注入（从 localStorage 获取）
  - 添加统一的错误处理和响应格式化
  - 添加 TypeScript 类型定义
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: API 库导出至少 10 个 API 方法（getConsultation, listPatients, getPatient, createPatient, listRecords, getRecord, healthCheck 等）
  - `programmatic` TR-1.2: 所有方法返回正确的 Promise 类型
  - `human-judgement` TR-1.3: API 调用失败时返回统一格式的错误对象

## [x] Task 2: 实现用户认证与会话管理
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `src/lib/auth.ts`，实现登录、登出、token 管理
  - 创建 `src/hooks/useAuth.ts`，提供登录状态管理
  - 修改登录页面，调用真实登录 API
  - 修改 AppShell，实现未登录重定向
  - 实现 token 过期自动登出
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: useAuth hook 返回 user, isLoggedIn, login, logout 方法
  - `human-judgement` TR-2.2: 未登录时访问受保护页面自动重定向到登录页
  - `human-judgement` TR-2.3: 登录后 token 存储在 localStorage，页面刷新后仍保持登录状态

## [x] Task 3: 仪表盘页面集成
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 替换 `/api/mock/dashboard/{patient_id}` 调用为真实 API
  - 使用 `/api/v1/records/patient/{patient_id}` 获取患者病历数据
  - 使用患者数据展示生命体征、健康风险、AI 建议
  - 添加加载状态和错误处理
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 页面调用 `/api/v1/records/patient/patient_demo_001` API
  - `human-judgement` TR-3.2: 页面显示真实患者数据（心率、血压、血氧等）
  - `human-judgement` TR-3.3: 网络错误时有友好提示

## [x] Task 4: 患者管理页面集成
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 替换 mock 数据为 `/api/v1/patients/` API
  - 实现患者列表分页和搜索功能
  - 实现患者创建表单（调用 POST /api/v1/patients/）
  - 实现患者详情查看（调用 GET /api/v1/patients/{id}）
  - 实现患者编辑和删除功能
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 页面调用 `/api/v1/patients/` 获取患者列表
  - `human-judgement` TR-4.2: 搜索功能正常工作，按姓名过滤患者
  - `human-judgement` TR-4.3: 新建患者后列表实时更新
  - `human-judgement` TR-4.4: 删除患者有确认提示

## [x] Task 5: 健康记录页面集成
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 替换 mock 数据为 `/api/v1/records/patient/{patient_id}` API
  - 从后端获取患者病历记录列表
  - 实现病历详情查看（调用 GET /api/v1/records/{id}）
  - 实现上传报告功能（调用后端文件上传 API）
  - 更新随访计划和健康记忆数据来源
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 页面调用 `/api/v1/records/patient/patient_demo_001` API
  - `human-judgement` TR-5.2: 病历列表显示真实数据（日期、诊断、科室等）
  - `human-judgement` TR-5.3: 点击病历记录跳转到详情页显示完整 SOAP 信息

## [x] Task 6: 问诊流程集成优化
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 确保 WebSocket 连接正常工作（已实现，需要验证）
  - 修改 summary 页面，从 `/api/v1/consult/{session_id}` 获取完整问诊记录
  - 修改 review 页面，从后端获取问诊状态
  - 确保问诊完成后正确跳转到 summary 页面
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-6.1: 开始问诊后 WebSocket 连接成功，收到欢迎消息
  - `human-judgement` TR-6.2: 问诊流程完整（分诊 → 诊断 → 审查 → 随访）
  - `human-judgement` TR-6.3: 问诊完成后正确跳转到 summary 页面，显示完整 SOAP 报告

## [x] Task 7: 系统状态页面集成
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 
  - 替换 `/api/mock/system-status` 为 `/api/v1/health`
  - 根据后端返回的健康状态展示系统信息
  - 添加刷新功能调用真实 API
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 页面调用 `/api/v1/health` API
  - `human-judgement` TR-7.2: 显示真实的系统状态信息（status、mode、version）

## [x] Task 8: 个人中心页面集成
- **Priority**: medium
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 从后端获取用户个人资料
  - 从后端获取健康指标数据
  - AI 分析配置和设备管理暂时保持 mock 数据
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-8.1: 用户信息卡片显示真实数据（姓名、邮箱、年龄等）
  - `human-judgement` TR-8.2: 健康指标概览数据从后端获取

## [x] Task 9: 构建验证和测试
- **Priority**: high
- **Depends On**: Task 1-8
- **Description**: 
  - 运行 TypeScript 类型检查
  - 运行 npm run build 确保构建成功
  - 手动测试各页面 API 调用是否正常
  - 修复发现的问题
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: npm run build 构建成功，无错误
  - `programmatic` TR-9.2: 无 TypeScript 类型错误
  - `human-judgement` TR-9.3: 所有集成页面可正常访问，数据加载正常
