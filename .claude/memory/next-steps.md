---
name: next-steps
description: 项目后续开发优先级和待办事项
metadata: 
  node_type: memory
  type: project
  originSessionId: 42e518b8-d51f-47f1-92ce-81395a239b7e
---

# 后续开发优先级

## 已完成 (W3-W8)

- W3: Skill 系统 + Doctor Agent ✅
- W4: 多源 RAG + KG + Review Agent ✅
- W5: 记忆系统 + 病历管理 + Follow-up Agent ✅
- W6: 前端完整产品 ✅
- W7: 安全 + Guardrail + Coordinator ✅
- W8: 部署 + 文档 + v0.1.0 ✅

## 2026-06-22 修复与完善 (测试修复 + Demo 级模块完成)

### 测试修复 (3 个文件)
- **test_coordinator.py** — 添加 COMPLEXITY_TRIGGERS (4 种会诊触发器) + consultation_protocol.py 数据类
- **test_review_rules.py** — 实现 contraindication.py (check_allergy/check_age_restriction/check_all_contraindications + 完整数据)
- **test_followup_agent.py** — 重写 FollowupAgent.run() 为中文输出 + scheduler.py 添加 get_plan_for_diagnosis/generate_schedule

### Guardrail 重写 (连带修复)
- **emergency_detector.py** — Async 支持 + 6 类紧急类型 + 正则 + get_emergency_response
- **pii_sanitizer.py** — 正则脱敏 (手机/座机/身份证/邮箱) + 掩码 + 检测
- **identity_verifier.py** — 返回 (bool, str) + verify_session

### Demo 级模块完成 (🏗/📋→✅)
- **Patient API** — 完整 CRUD + 搜索分页 + 2 条 demo 数据
- **Medical Records API** — get/list/create + 3 条 demo 记录
- **JWT Auth** — create_access_token/refresh/decode/get_current_user/optional
- **Security** — PII 检测/脱敏/掩码 (4 种模式)
- **Dependencies** — get_session_id/patient_id/pagination
- **Review prompt** — 8 维完整审查提示词 + JSON 输出格式
- **Review checkers** — 可插拔检查器框架 + drug_interaction + contraindication 两个检查器
- **Rate Limit** — 60 req/min per IP (已接入 main.py)
- **Workers** — Celery 任务 (send_followup_reminder/process_async_analysis/cleanup) + lazy init

### 测试状态
- 快速测试: 129 passed ✅
- 集成测试: 27 passed ✅
- 总计: 156 测试通过

## 待定项

- RAG 真实数据入库 (爬取真实病例/指南/论文)
- Neo4j 生产接入 (当前内存兜底)
- 程序性记忆 (Agent 总结经验能力)
- Plugin SDK 市场 (v0.3.0+)
- 英文 i18n (v0.2.0+)
- Human-in-the-loop 专家审核 (v0.2.0+)
- AppShell 前端路由优化
- 前端状态管理 Zustand 集成 (v0.2.0+)
