# MediNexus 前端页面逻辑优化 - 实施计划

## [ ] Task 1: 修复 Tooltip 组件显示问题
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 删除 Tooltip 组件中的菱形箭头元素
  - 修正 Tooltip 定位样式，确保在左侧边栏折叠时显示位置准确
  - 保留圆角矩形提示框和文字提示功能
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: Tooltip 组件代码中不再包含菱形箭头相关的 DOM 元素和样式
  - `human-judgement` TR-1.2: 左侧边栏折叠时，鼠标悬停导航项显示纯圆角矩形 Tooltip，位置准确，无错位
- **Notes**: 修改文件 src/components/ui/Tooltip.tsx

## [ ] Task 2: 调整左侧边栏导航项
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 从 navItems 数组中移除"系统状态"导航项
  - 保留 6 个导航项：控制台、AI 问诊、健康记录、患者管理、个人中心、设置
  - 检查用户下拉菜单，确保链接正确
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: AppShell.tsx 中 navItems 数组长度为 6，不包含系统状态项
  - `human-judgement` TR-2.2: 左侧边栏显示 6 个导航项，顺序合理，点击均可正常跳转
- **Notes**: 修改文件 src/components/layout/AppShell.tsx

## [ ] Task 3: 重构个人中心页面
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 保留用户基本信息卡片
  - 优化健康指标概览模块（4 个统计卡片）
  - 新增 AI 分析配置模块：模型选择、分析强度、诊断偏好等设置项
  - 新增设备授权管理模块：已授权设备列表、设备状态、添加新设备入口
  - 重构功能菜单为医疗相关功能：健康档案、健康报告、AI 分析配置、设备管理
  - 移除"开始问诊"快捷操作
  - 移除功能菜单中的通知设置、隐私安全、系统设置等入口
  - 移除底部"关于 MediNexus"模块中的系统状态按钮
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 页面包含 AI 分析配置和设备授权管理两个新模块
  - `human-judgement` TR-3.2: 页面无"开始问诊"按钮，无系统设置相关入口
  - `human-judgement` TR-3.3: 功能菜单只包含医疗相关选项，跳转链接正确
  - `human-judgement` TR-3.4: 整体布局与现有页面风格一致，视觉效果良好
- **Notes**: 修改文件 src/app/profile/page.tsx；使用 mock 数据展示 AI 配置和设备列表

## [ ] Task 4: 重构设置页面
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 保留账户信息、通知偏好、隐私与安全、语言与地区模块
  - 将原"设备管理"（登录设备）合并到"隐私与安全"模块中
  - 移除"数据管理"模块（健康数据导出等功能归个人中心）
  - 新增"系统状态"模块，展示服务运行状态
  - 移除顶部的"查看个人中心"按钮
  - 更新左侧导航菜单，只保留 5 个设置分类
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 设置页面 sections 数组包含 5 项（账户信息、通知偏好、隐私与安全、语言与地区、系统状态）
  - `human-judgement` TR-4.2: 无数据管理模块，登录设备管理在隐私与安全中
  - `human-judgement` TR-4.3: 系统状态模块正常展示服务列表和运行状态
  - `human-judgement` TR-4.4: 各模块切换正常，表单元素样式统一
- **Notes**: 修改文件 src/app/settings/page.tsx；系统状态数据可复用原 system-status 页面的 mock 数据

## [ ] Task 5: 验证页面跳转与构建
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**: 
  - 检查所有页面的导航链接是否正确
  - 检查个人中心与设置页面之间的跳转逻辑
  - 运行 TypeScript 类型检查
  - 运行项目构建，确保无错误
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: npm run build 构建成功，无错误
  - `programmatic` TR-5.2: 无 TypeScript 类型错误
  - `human-judgement` TR-5.3: 所有页面跳转链接正确，无死链
  - `human-judgement` TR-5.4: 页面间跳转逻辑符合预期定位
- **Notes**: 需要手动测试各页面跳转
