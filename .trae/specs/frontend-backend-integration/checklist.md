# MediNexus 前后端打通 - 验证检查清单

## API 库重构
- [x] src/lib/api.ts 包含所有必要的 API 方法（getConsultation, listPatients, getPatient, createPatient, listRecords, getRecord, healthCheck 等）
- [x] API 调用自动注入认证 token
- [x] 统一的错误处理和响应格式化
- [x] TypeScript 类型定义完整

## 用户认证与会话管理
- [x] src/lib/auth.ts 实现登录、登出、token 管理
- [x] src/hooks/useAuth.ts 提供登录状态管理
- [x] 登录页面调用真实登录 API
- [x] 未登录时访问受保护页面自动重定向到登录页
- [x] 登录后 token 存储在 localStorage，页面刷新后仍保持登录状态
- [x] token 过期自动登出

## 仪表盘页面集成
- [x] 页面调用 `/api/v1/records/patient/patient_demo_001` API
- [x] 页面显示真实患者数据（心率、血压、血氧等）
- [x] 网络错误时有友好提示
- [x] 加载状态正常显示

## 患者管理页面集成
- [x] 页面调用 `/api/v1/patients/` 获取患者列表
- [x] 搜索功能正常工作，按姓名过滤患者
- [x] 新建患者后列表实时更新
- [x] 删除患者有确认提示
- [x] 患者详情页面显示完整信息
- [x] 患者编辑功能正常

## 健康记录页面集成
- [x] 页面调用 `/api/v1/records/patient/patient_demo_001` API
- [x] 病历列表显示真实数据（日期、诊断、科室等）
- [x] 点击病历记录跳转到详情页显示完整 SOAP 信息
- [x] 上传报告功能调用后端 API
- [x] 随访计划和健康记忆数据从后端获取

## 问诊流程集成优化
- [x] 开始问诊后 WebSocket 连接成功，收到欢迎消息
- [x] 问诊流程完整（分诊 → 诊断 → 审查 → 随访）
- [x] 问诊完成后正确跳转到 summary 页面
- [x] summary 页面显示完整 SOAP 报告
- [x] review 页面从后端获取问诊状态

## 系统状态页面集成
- [x] 页面调用 `/api/v1/health` API
- [x] 显示真实的系统状态信息（status、mode、version）
- [x] 刷新功能调用真实 API

## 个人中心页面集成
- [x] 用户信息卡片显示真实数据（姓名、邮箱、年龄等）
- [x] 健康指标概览数据从后端获取

## 构建验证和测试
- [x] npm run build 构建成功，无错误
- [x] 无 TypeScript 类型错误
- [x] 所有集成页面可正常访问，数据加载正常
- [x] 页面间跳转逻辑正确
- [x] 无控制台错误
