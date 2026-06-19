# MediNexus 前端 UI 设计方案 - 高优补充页面 (Part 1)

> **版本**: v1.1  
> **日期**: 2026-06-12  
> **补充页面**: 智能问诊对话页、问诊完成总结页、登录注册页  
> **基于**: 已有 5 页面设计文档 + 设计参考文档 + 截图分析

---

## 目录

1. [页面 6: 智能问诊对话页 /consultation/chat](#一页面-6-智能问诊对话页-consultationchat)
2. [页面 7: 问诊完成总结页 /consultation/summary](#二页面-7-问诊完成总结页-consultationsummary)
3. [页面 8: 登录注册页 /login](#三页面-8-登录注册页-login)
4. [共享状态与数据流](#四共享状态与数据流)

---

## 一、页面 6: 智能问诊对话页 /consultation/chat

### 1.1 页面定位

这是 **MediNexus 最核心的交互页面**。患者输入症状描述，系统通过 **多 Agent 协作**（Triage 导诊 → Doctor 诊断 → Review 审查 → Follow-up 随访）提供 AI 辅助医疗咨询。支持 WebSocket 流式对话，实时显示各 Agent 的思考过程和输出内容。

### 1.2 页面信息架构

```
ConsultationChat Page
├── ChatHeader (固定顶部, h-16, z-20)
│   ├── Left (flex, align-center, gap: 12px)
│   │   ├── BackButton (icon: arrow-left, w-8 h-8, rounded-full, hover:bg-gray-100)
│   │   ├── TitleStack
│   │   │   ├── "AI 智能问诊" (text-base, font-semibold)
│   │   │   └── SessionID "session_abc123" (text-xs, text-muted, font-mono)
│   ├── Center: empty
│   └── Right (flex, align-center, gap: 8px)
│       ├── EmergencyBadge (hidden by default, bg-danger-light, text-danger, rounded-full, px-3 py-1, animate-pulse)
│       │   └── "紧急模式" + icon: alert-triangle
│       └── CompleteButton (bg-primary, text-white, rounded-xl, px-4 py-2, text-sm)
│           └── "完成问诊"
│
├── ChatContainer (flex-1, overflow-y-auto, padding: 24px, space-y: 24px)
│   ├── WelcomeMessage (AI 系统消息)
│   ├── AgentStartIndicators (多个, 显示当前活跃 Agent)
│   ├── ChatMessages (用户消息 + AI 消息交替)
│   ├── StreamingCursor (当 AI 正在输出时显示)
│   └── DisclaimerBanner (首次 Agent 响应后出现, 固定在消息列表底部上方)
│
├── ChatInputArea (固定底部, h-auto, min-h-16, z-20, bg-white, border-t)
│   ├── InputContainer (flex, align-end, gap: 12px, padding: 16px 24px)
│   │   ├── Textarea (flex-1, auto-resize, max-h-32, rounded-xl, border, p-3, text-sm)
│   │   │   └── Placeholder: "请描述您的症状，如：我头痛两天了，伴有发热..."
│   │   └── SendButton (w-10 h-10, rounded-full, bg-primary, text-white, disabled:opacity-50)
│   │       └── icon: send (w-4 h-4)
│   └── InputHints (padding: 0 24px 8px, text-xs, text-muted)
│       └── "按 Enter 发送，Shift+Enter 换行"
│
└── [无侧边栏, 无顶部栏 - 全屏沉浸式对话]
```

### 1.3 页面布局细节

**整体布局**:
- 无全局侧边栏/顶部栏，沉浸式对话体验
- 背景色: `#F8FAFF` (medical-bg)
- 最大宽度: 800px，居中显示
- 移动端: 全宽，padding 减小为 16px

**ChatHeader**:
- 高度: 64px
- 背景: 白色 + 底部边框 1px solid `#E2E8F0`
- 左侧: 返回按钮 + 标题 + 会话 ID（等宽字体 `font-mono`）
- 右侧: 紧急标记（默认隐藏，检测到紧急情况时显示）+ "完成问诊"按钮
- 紧急标记: 红色脉冲动画，`animate-pulse`，带 `alert-triangle` 图标

### 1.4 ChatMessage 组件

```typescript
interface ChatMessageProps {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  agent?: 'triage' | 'doctor' | 'review' | 'followup';  // AI 消息时必填
  streaming?: boolean;  // 是否正在流式输出
  timestamp: Date;
  manifest?: HandoverManifest;  // Agent 交接数据
}
```

**用户消息 (User)**:
```
UserMessage (flex, justify-end, margin-bottom: 16px)
├── MessageBubble (max-width: 80%, bg-primary, text-white, rounded-2xl, rounded-br-sm, padding: 12px 16px)
│   └── Content (text-sm, leading-relaxed, whitespace-pre-wrap)
└── Timestamp (text-xs, text-muted, margin-top: 4px, text-right)
    └── "14:32"
```

**AI 消息 (Assistant)**:
```
AIMessage (flex, justify-start, margin-bottom: 16px)
├── AvatarSection (flex-shrink-0, margin-right: 12px)
│   └── AgentAvatar (w-8 h-8, rounded-full, flex, items-center, justify-center)
│       └── [triage: bg-blue-100, icon: stethoscope]
│       └── [doctor: bg-green-100, icon: user-md]
│       └── [review: bg-purple-100, icon: shield-check]
│       └── [followup: bg-amber-100, icon: calendar-check]
│
└── ContentSection (flex-1, max-width: calc(100% - 48px))
    ├── AgentLabel (flex, align-center, gap: 6px, margin-bottom: 4px)
    │   ├── AgentName (text-xs, font-medium)
    │   │   └── [triage: "导诊护士", text-blue-600]
    │   │   └── [doctor: "AI 医生", text-green-600]
    │   │   └── [review: "审方药师", text-purple-600]
    │   │   └── [followup: "随访助手", text-amber-600]
    │   └── AgentBadge (text-xs, text-muted)
    │       └── "正在分析..." / "已完成"
    │
    ├── MessageBubble (bg-white, border, border-gray-200, rounded-2xl, rounded-bl-sm, padding: 12px 16px, shadow-sm)
    │   ├── Content (text-sm, text-secondary, leading-relaxed, whitespace-pre-wrap)
    │   └── [streaming: true 时末尾追加 StreamingCursor]
    │
    ├── ManifestCard (margin-top: 8px, bg-gray-50, rounded-xl, p-3, border, border-gray-100)
    │   ├── FactsList (space-y: 2px)
    │   │   └── FactItem (flex, align-center, gap: 4px, text-xs, text-muted)
    │   │       ├── Icon: check (w-3 h-3, text-accent)
    │   │       └── "已确定: 头痛持续2天"
    │   ├── PendingQuestions (margin-top: 4px, space-y: 2px)
    │   │   └── QuestionItem (flex, align-center, gap: 4px, text-xs, text-muted)
    │   │       ├── Icon: help-circle (w-3 h-3, text-warning)
    │   │       └── "待确认: 是否有恶心症状？"
    │   └── RiskFlags (margin-top: 4px, flex, flex-wrap, gap: 4px)
    │       └── RiskBadge (bg-danger-light, text-danger, text-xs, rounded-full, px-2 py-0.5)
    │           └── "EMERGENCY_DETECTED"
    │
    └── Timestamp (text-xs, text-muted, margin-top: 4px)
        └── "14:33"
```

**StreamingCursor**:
```
StreamingCursor (inline-flex, align-center, gap: 2px, margin-left: 2px)
├── Dot1 (w-1.5 h-1.5, bg-primary, rounded-full, animate-bounce)
├── Dot2 (w-1.5 h-1.5, bg-primary, rounded-full, animate-bounce, animation-delay: 150ms)
└── Dot3 (w-1.5 h-1.5, bg-primary, rounded-full, animate-bounce, animation-delay: 300ms)
```

### 1.5 Agent 标签系统

| Agent | 名称 | 颜色 | 图标 | 背景色 | 职责 |
|-------|------|------|------|--------|------|
| `triage` | 导诊护士 | 蓝色 | `stethoscope` | `bg-blue-100` | 症状收集、科室推荐 |
| `doctor` | AI 医生 | 绿色 | `user-md` | `bg-green-100` | 诊断分析、治疗方案 |
| `review` | 审方药师 | 紫色 | `shield-check` | `bg-purple-100` | 用药审查、禁忌检查 |
| `followup` | 随访助手 | 琥珀色 | `calendar-check` | `bg-amber-100` | 随访计划、复诊提醒 |

### 1.6 免责声明条 (DisclaimerBanner)

```
DisclaimerBanner (sticky, bottom: 80px, z-10, margin: 0 24px 16px)
├── StandardMode (bg-warning-light/50, border, border-warning/30, rounded-xl, p-4, flex, gap: 12px)
│   ├── Icon: info (w-5 h-5, text-warning, flex-shrink-0)
│   └── Content
│       ├── Title: "医疗免责声明" (text-sm, font-semibold, text-warning)
│       └── Text: "本系统提供的建议仅供参考，不构成医疗诊断。如有紧急情况，请立即拨打急救电话或前往医院。" (text-xs, text-secondary, margin-top: 2px)
│
└── EmergencyMode (bg-danger-light, border, border-danger, rounded-xl, p-4, flex, gap: 12px, animate-shake)
    ├── Icon: alert-triangle (w-5 h-5, text-danger, flex-shrink-0, fill: currentColor)
    └── Content
        ├── Title: "⚠️ 紧急情况 detected" (text-sm, font-semibold, text-danger)
        ├── Text: "系统检测到可能危及生命的症状。请立即采取以下措施：" (text-xs, text-secondary, margin-top: 2px)
        ├── ActionList (margin-top: 8px, space-y: 4px)
        │   └── ActionItem (flex, align-center, gap: 6px, text-xs)
        │       ├── Icon: phone (w-3 h-3, text-danger)
        │       └── "拨打急救电话: 120"
        └── EmergencyButton (margin-top: 8px, w-full, bg-danger, text-white, rounded-lg, py-2, text-sm, font-medium)
            └── "查看急救指引"
```

**显示逻辑**:
- 首次 Agent 响应后自动出现标准免责声明
- 收到 `emergency` WebSocket 事件时切换为紧急模式
- 紧急模式出现时，整个聊天容器上方覆盖红色半透明遮罩

### 1.7 ChatInput 组件

```
ChatInput (fixed, bottom: 0, left: 0, right: 0, bg-white, border-t, border-gray-200, z-30)
├── InputWrapper (max-width: 800px, mx-auto, padding: 12px 24px)
│   ├── TextareaContainer (flex, align-end, gap: 8px, bg-gray-50, rounded-xl, border, border-gray-200, padding: 8px 12px)
│   │   ├── Textarea (flex-1, bg-transparent, border-none, outline-none, resize-none, max-h-32, text-sm, placeholder:text-muted)
│   │   │   └── Placeholder: "请描述您的症状，如：我头痛两天了，伴有发热..."
│   │   └── SendButton (w-9 h-9, rounded-full, bg-primary, text-white, flex, items-center, justify-center, disabled:opacity-40)
│   │       └── icon: send (w-4 h-4)
│   └── HintText (text-xs, text-muted, margin-top: 6px, text-center)
│       └── "按 Enter 发送，Shift+Enter 换行"
│
└── [移动端: 底部安全区域适配 padding-bottom: env(safe-area-inset-bottom)]
```

**交互**:
- `Enter`: 发送消息（如果内容非空）
- `Shift+Enter`: 插入换行
- 输入时自动增高（最大 128px），超出时滚动
- 发送后清空输入框，聚焦保持
- 禁用态: 输入框 opacity-50, 发送按钮不可点击

### 1.8 紧急模式覆盖层

```
EmergencyOverlay (fixed, inset-0, z-40, bg-danger/10, pointer-events-none)
├── TopAlert (absolute, top: 80px, left: 50%, transform: translateX(-50%), bg-danger, text-white, rounded-xl, px-6 py-3, shadow-lg, flex, align-center, gap: 8px)
│   ├── Icon: alert-triangle (w-5 h-5, fill: currentColor)
│   └── "检测到紧急情况，请立即就医"
│
└── BottomActions (absolute, bottom: 100px, left: 50%, transform: translateX(-50%), flex, gap: 12px)
    ├── Button "拨打 120" (bg-danger, text-white, rounded-xl, px-6 py-3, shadow-lg, icon: phone)
    └── Button "查看急救指引" (bg-white, text-danger, rounded-xl, px-6 py-3, shadow-lg, border, border-danger)
```

### 1.9 WebSocket 状态指示器

```
ConnectionStatus (absolute, top: 72px, left: 50%, transform: translateX(-50%), z-30)
├── Connected (hidden)
├── Connecting (bg-gray-100, text-muted, rounded-full, px-3 py-1, text-xs, flex, align-center, gap: 4px)
│   ├── Spinner (w-3 h-3, border-2, border-primary, border-t-transparent, rounded-full, animate-spin)
│   └── "连接中..."
├── Reconnecting (bg-warning-light, text-warning, rounded-full, px-3 py-1, text-xs, animate-pulse)
│   └── "正在重新连接 (1/3)..."
└── Disconnected (bg-danger-light, text-danger, rounded-full, px-3 py-1, text-xs)
    └── "连接已断开，点击重试"
```

---

## 二、页面 7: 问诊完成总结页 /consultation/summary

### 2.1 页面定位

问诊流程结束后，展示完整的诊断结果、SOAP 记录、用药建议、随访计划。患者可查看、导出、或重新发起问诊。这是问诊流程的终点页面，也是医疗记录的数据来源。

### 2.2 页面信息架构

```
ConsultationSummary Page
├── SummaryHeader (text-center, padding: 40px 24px, bg-gradient-to-b from-primary-light to-transparent)
│   ├── SuccessIcon (w-16 h-16, mx-auto, rounded-full, bg-accent-light, flex, items-center, justify-center, margin-bottom: 16px)
│   │   └── icon: check-circle (w-8 h-8, text-accent, stroke-width: 2)
│   ├── Title: "问诊已完成" (text-2xl, font-bold, text-primary)
│   ├── Subtitle: "您的健康档案已更新，AI 建议仅供参考，请务必咨询专业医生。" (text-sm, text-muted, margin-top: 8px, max-width: 480px, mx-auto)
│   └── ActionButtons (flex, justify-center, gap: 12px, margin-top: 24px)
│       ├── Button "查看就诊记录" (outline, icon: file-text)
│       └── Button "重新问诊" (primary, icon: refresh-cw)
│
├── SessionInfoCard (max-width: 800px, mx-auto, margin-top: 24px, bg-white, rounded-2xl, p-6, shadow-sm, border)
│   ├── Header (flex, justify-between, align-center, margin-bottom: 16px)
│   │   ├── "会话详情" (text-lg, font-semibold)
│   │   └── StatusBadge (bg-accent-light, text-accent, rounded-full, px-3 py-1, text-xs, font-medium)
│   │       └── "已完成"
│   ├── InfoGrid (grid-cols-2, gap: 16px)
│   │   ├── InfoItem
│   │   │   ├── Label: "会话 ID" (text-xs, text-muted)
│   │   │   └── Value: "session_abc123" (text-sm, font-mono, text-primary)
│   │   ├── InfoItem
│   │   │   ├── Label: "完成时间" (text-xs, text-muted)
│   │   │   └── Value: "2026-06-12 14:35" (text-sm, text-primary)
│   │   ├── InfoItem
│   │   │   ├── Label: "参与 Agent" (text-xs, text-muted)
│   │   │   └── Value: "导诊 / 诊断 / 审方 / 随访" (text-sm, text-primary)
│   │   └── InfoItem
│   │       ├── Label: "证据等级" (text-xs, text-muted)
│   │       └── Value: "B 级 (医学共识)" (text-sm, text-primary)
│   └── DisclaimerBar (margin-top: 16px, bg-warning-light/50, rounded-lg, p-3, flex, gap: 8px)
│       ├── Icon: alert-circle (w-4 h-4, text-warning, flex-shrink-0)
│       └── "本结果不构成医疗诊断建议，请咨询专业医生。" (text-xs, text-warning)
│
├── SOAPCard (max-width: 800px, mx-auto, margin-top: 24px, bg-white, rounded-2xl, p-6, shadow-sm)
│   ├── Header (flex, align-center, gap: 8px, margin-bottom: 20px)
│   │   ├── Icon: clipboard-list (w-5 h-5, text-primary)
│   │   └── "SOAP 记录" (text-lg, font-semibold)
│   │
│   └── SOAPGrid (space-y: 16px)
│       ├── SOAPSection
│       │   ├── Header (flex, align-center, gap: 6px, margin-bottom: 8px)
│       │   │   ├── LetterBadge (w-6 h-6, rounded-md, bg-primary, text-white, text-xs, font-bold, flex, items-center, justify-center)
│       │   │   │   └── "S"
│       │   │   └── "主观资料 (Subjective)" (text-sm, font-semibold)
│       │   └── Content (bg-gray-50, rounded-xl, p-4, text-sm, text-secondary, leading-relaxed)
│       │       └── "患者主诉头痛两天，伴有低热（37.8°C），无恶心呕吐，无颈部僵硬。既往有偏头痛病史。"
│       ├── SOAPSection
│       │   ├── LetterBadge "O" (bg-accent, text-white)
│       │   ├── "客观资料 (Objective)" (text-sm, font-semibold)
│       │   └── Content (bg-gray-50, rounded-xl, p-4, text-sm, text-secondary)
│       │       └── "体温: 37.8°C，血压: 118/76 mmHg，心率: 72 bpm。神经系统检查未见明显异常。"
│       ├── SOAPSection
│       │   ├── LetterBadge "A" (bg-warning, text-white)
│       │   ├── "评估 (Assessment)" (text-sm, font-semibold)
│       │   └── Content (bg-gray-50, rounded-xl, p-4, text-sm, text-secondary)
│       │       └── "急性上呼吸道感染伴偏头痛发作。证据等级: B (医学共识)。"
│       └── SOAPSection
│           ├── LetterBadge "P" (bg-purple-500, text-white)
│           ├── "计划 (Plan)" (text-sm, font-semibold)
│           └── Content (bg-gray-50, rounded-xl, p-4, text-sm, text-secondary)
│               └── "1. 对乙酰氨基酚 500mg 每6小时一次；2. 充分休息，多饮水；3. 48小时后复诊，如症状加重立即就医。"
│
├── DiagnosisCard (max-width: 800px, mx-auto, margin-top: 24px, bg-white, rounded-2xl, p-6, shadow-sm)
│   ├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   │   ├── Icon: stethoscope (w-5 h-5, text-primary)
│   │   └── "诊断结果" (text-lg, font-semibold)
│   └── DiagnosisContent
│       ├── PrimaryDiagnosis (flex, align-center, gap: 8px, margin-bottom: 12px)
│       │   ├── Badge (bg-primary-light, text-primary, rounded-full, px-3 py-1, text-sm, font-medium)
│       │   │   └── "主要诊断"
│       │   └── "急性上呼吸道感染" (text-base, font-semibold)
│       ├── SecondaryDiagnoses (space-y: 8px)
│       │   └── DiagnosisItem (flex, align-center, gap: 8px)
│       │       ├── Badge (bg-gray-100, text-gray-600, rounded-full, px-3 py-1, text-xs)
│       │       │   └── "伴随诊断"
│       │       └── "偏头痛发作" (text-sm)
│       └── ConfidenceBar (margin-top: 16px)
│           ├── LabelRow (flex, justify-between, margin-bottom: 4px)
│           │   ├── "诊断置信度" (text-xs, text-muted)
│           │   └── "78%" (text-xs, text-primary, font-medium)
│           └── ProgressBar (h-2, bg-gray-200, rounded-full)
│               └── Fill (h-full, bg-primary, rounded-full, width: 78%)
│
├── MedicationCard (max-width: 800px, mx-auto, margin-top: 24px, bg-white, rounded-2xl, p-6, shadow-sm)
│   ├── Header (flex, justify-between, align-center, margin-bottom: 16px)
│   │   ├── Left (flex, align-center, gap: 8px)
│   │   │   ├── Icon: pill (w-5 h-5, text-primary)
│   │   │   └── "用药建议" (text-lg, font-semibold)
│   │   └── Badge (bg-accent-light, text-accent, rounded-full, px-2 py-0.5, text-xs)
│   │       └── "已审方通过"
│   └── MedicationList (space-y: 12px)
│       ├── MedicationItem (bg-gray-50, rounded-xl, p-4, border, border-gray-100)
│       │   ├── HeaderRow (flex, justify-between, align-center, margin-bottom: 8px)
│       │   │   ├── DrugName (text-sm, font-semibold)
│       │   │   │   └── "对乙酰氨基酚 (Paracetamol)"
│       │   │   └── DosageBadge (bg-primary-light, text-primary, rounded-full, px-2 py-0.5, text-xs)
│       │   │       └── "500mg"
│       │   ├── Instruction (text-xs, text-secondary)
│       │   │   └── "每6小时一次，口服，饭后服用"
│       │   └── Warning (margin-top: 8px, bg-warning-light/50, rounded-lg, p-2, flex, gap: 6px)
│       │       ├── Icon: alert-circle (w-3 h-3, text-warning, flex-shrink-0, margin-top: 1px)
│       │       └── "注意: 24小时内不超过4次，肝肾功能不全者慎用。" (text-xs, text-warning)
│       └── MedicationItem
│           ├── DrugName: "布洛芬 (Ibuprofen)"
│           ├── DosageBadge: "200mg"
│           ├── Instruction: "每8小时一次，口服，必要时使用"
│           └── Warning: "注意: 胃溃疡患者禁用，避免空腹服用。"
│
├── FollowUpCard (max-width: 800px, mx-auto, margin-top: 24px, bg-white, rounded-2xl, p-6, shadow-sm, margin-bottom: 40px)
│   ├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   │   ├── Icon: calendar-check (w-5 h-5, text-primary)
│   │   └── "随访计划" (text-lg, font-semibold)
│   └── FollowUpList (space-y: 12px)
│       ├── FollowUpItem (flex, align-start, gap: 12px)
│       │   ├── DateBadge (flex-shrink-0, w-12, text-center)
│       │   │   ├── Day: "14" (text-lg, font-bold, text-primary)
│       │   │   └── Month: "6月" (text-xs, text-muted)
│       │   └── Content
│       │       ├── Title: "48小时复诊评估" (text-sm, font-semibold)
│       │       └── Description: "评估症状改善情况，如发热不退或头痛加剧需立即就医。" (text-xs, text-secondary, margin-top: 2px)
│       └── FollowUpItem
│           ├── DateBadge: "21日 / 6月"
│           ├── Title: "血常规复查"
│           └── Description: "复查白细胞计数，确认感染控制情况。"
│
└── FloatingExportButton (fixed, bottom: 24px, right: 24px, z-30)
    └── Button (bg-primary, text-white, rounded-full, px-6 py-3, shadow-lg, flex, align-center, gap: 8px, hover:shadow-xl, transition)
        ├── Icon: download (w-4 h-4)
        └── "导出报告"
```

### 2.3 页面布局细节

**整体布局**:
- 无全局侧边栏，简化顶部栏（仅返回按钮 + Logo）
- 背景: `#F8FAFF`
- 内容最大宽度: 800px，居中
- 所有卡片垂直排列，间距 24px

**顶部成功区域**:
- 渐变背景: `from-primary-light to-transparent`
- 大勾号图标: 64px 圆形，绿色背景
- 标题 + 副标题 + 双按钮居中

**SOAP 卡片**:
- 四个区块分别用 S/O/A/P 字母标识
- 每个字母不同颜色: S(蓝) O(绿) A(琥珀) P(紫)
- 内容区使用灰色背景卡片

**导出按钮**:
- 固定右下角，圆形药丸按钮
- 带阴影，悬停时阴影增大
- 点击后展开菜单: PDF / JSON / 分享

---

## 三、页面 8: 登录注册页 /login

### 3.1 页面定位

平台入口页面，支持患者和医生两种角色的登录/注册。设计简洁、专业、可信，符合医疗平台的严肃性。支持邮箱/手机登录、OTP验证、第三方登录（OAuth）。

### 3.2 页面信息架构

```
Login Page
├── LoginContainer (min-h-screen, flex, bg-medical-bg)
│   ├── LeftPanel (hidden lg:flex, flex-1, bg-primary, flex, flex-col, justify-center, align-center, padding: 60px)
│   │   ├── BrandSection (text-center, text-white)
│   │   │   ├── LogoIcon (w-16 h-16, mx-auto, rounded-2xl, bg-white/20, flex, items-center, justify-center, margin-bottom: 24px)
│   │   │   │   └── icon: activity (w-8 h-8, text-white)
│   │   │   ├── BrandName: "MediNexus" (text-3xl, font-bold, margin-bottom: 8px)
│   │   │   └── Tagline: "AI 多智能体医疗诊断平台" (text-lg, text-white/80)
│   │   └── FeatureList (margin-top: 48px, space-y: 24px, max-width: 360px)
│   │       ├── FeatureItem (flex, align-center, gap: 16px)
│   │       │   ├── IconCircle (w-10 h-10, rounded-full, bg-white/20, flex, items-center, justify-center)
│   │       │   │   └── icon: brain (w-5 h-5, text-white)
│   │       │   └── FeatureText
│   │       │       ├── "多 Agent 协作诊断" (text-base, font-medium, text-white)
│   │       │       └── "Triage → Doctor → Review → Follow-up" (text-sm, text-white/70)
│   │       ├── FeatureItem
│   │       │   ├── Icon: shield-check (w-5 h-5, text-white)
│   │       │   └── "本地部署，数据不出设备" (text-base, font-medium, text-white)
│   │       └── FeatureItem
│   │           ├── Icon: lock (w-5 h-5, text-white)
│   │           └── "完全开源，隐私可控" (text-base, font-medium, text-white)
│   │
│   └── RightPanel (flex-1, flex, flex-col, justify-center, align-center, padding: 40px 24px)
│       └── AuthCard (w-full, max-width: 440px, bg-white, rounded-2xl, shadow-lg, padding: 40px)
│           ├── TabSwitch (flex, margin-bottom: 32px, bg-gray-100, rounded-xl, p-1)
│           │   ├── Tab "登录" (flex-1, text-center, py-2.5, rounded-lg, text-sm, font-medium)
│           │   │   └── [Active: bg-white, text-primary, shadow-sm]
│           │   └── Tab "注册" (flex-1, text-center, py-2.5, rounded-lg, text-sm, text-muted)
│           │       └── [Active: bg-white, text-primary, shadow-sm]
│           │
│           ├── RoleSelector (margin-bottom: 24px)
│           │   ├── Label: "选择角色" (text-sm, text-muted, margin-bottom: 8px)
│           │   └── RoleGrid (grid-cols-2, gap: 12px)
│           │       ├── RoleCard (border, rounded-xl, p-4, text-center, cursor-pointer, transition)
│           │       │   ├── Icon: user-circle (w-6 h-6, mx-auto, text-muted)
│           │       │   ├── "我是患者" (text-sm, font-medium, margin-top: 8px)
│           │       │   └── "自助问诊" (text-xs, text-muted, margin-top: 2px)
│           │       │   └── [Selected: border-primary, bg-primary-light, icon:text-primary]
│           │       └── RoleCard
│           │           ├── Icon: stethoscope (w-6 h-6, mx-auto, text-muted)
│           │           ├── "我是医生" (text-sm, font-medium, margin-top: 8px)
│           │           └── "诊断辅助" (text-xs, text-muted, margin-top: 2px)
│           │           └── [Selected: border-primary, bg-primary-light, icon:text-primary]
│           │
│           ├── LoginForm (space-y: 20px)
│           │   ├── InputGroup
│           │   │   ├── Label: "邮箱 / 手机号" (text-sm, font-medium, margin-bottom: 6px)
│           │   │   └── Input (w-full, rounded-xl, border, border-gray-200, px-4, py-3, text-sm, focus:ring-2, focus:ring-primary, focus:border-primary)
│           │   │       └── Placeholder: "请输入邮箱或手机号"
│           │   ├── InputGroup
│           │   │   ├── LabelRow (flex, justify-between, margin-bottom: 6px)
│           │   │   │   ├── "密码" (text-sm, font-medium)
│           │   │   │   └── Link "忘记密码?" (text-xs, text-primary)
│           │   │   └── Input (type: password, w-full, rounded-xl, border, border-gray-200, px-4, py-3, text-sm)
│           │   │       └── Placeholder: "请输入密码"
│           │   ├── RememberRow (flex, justify-between, align-center)
│           │   │   ├── Checkbox (flex, align-center, gap: 6px)
│           │   │   │   └── "记住我" (text-sm, text-secondary)
│           │   │   └── empty
│           │   └── SubmitButton (w-full, bg-primary, text-white, rounded-xl, py-3, text-sm, font-medium, shadow-primary, hover:bg-primary-hover, active:scale-[0.98])
│           │       └── "登录"
│           │
│           ├── Divider (flex, align-center, gap: 12px, margin: 24px 0)
│           │   ├── Line (flex-1, h-px, bg-gray-200)
│           │   ├── "或" (text-xs, text-muted)
│           │   └── Line (flex-1, h-px, bg-gray-200)
│           │
│           ├── OAuthButtons (grid-cols-2, gap: 12px)
│           │   ├── OAuthButton (border, rounded-xl, py-2.5, flex, align-center, justify-center, gap: 8px, text-sm, text-secondary, hover:bg-gray-50)
│           │   │   └── Icon + "微信登录"
│           │   └── OAuthButton
│           │       └── Icon + "Apple ID"
│           │
│           └── FooterText (text-center, margin-top: 24px, text-xs, text-muted)
│               └── "登录即表示您同意我们的 服务条款 和 隐私政策"
│
└── [无全局导航]
```

### 3.3 OTP 验证界面

```
OTPVerification (覆盖在 AuthCard 上方，或作为独立步骤)
├── Header (text-center, margin-bottom: 24px)
│   ├── Icon: mail (w-12 h-12, mx-auto, text-primary, margin-bottom: 12px)
│   ├── Title: "验证您的身份" (text-xl, font-bold)
│   └── Subtitle: "验证码已发送至 +86 138****8888" (text-sm, text-muted, margin-top: 4px)
│
├── OTPInput (flex, justify-center, gap: 8px, margin-bottom: 24px)
│   └── DigitInput (w-12 h-14, text-center, text-xl, font-bold, rounded-xl, border, border-gray-200, focus:ring-2, focus:ring-primary, focus:border-primary)
│       └── [6个输入框，自动聚焦下一个]
│
├── TimerText (text-center, text-sm, text-muted, margin-bottom: 24px)
│   └── "59 秒后重新发送"
│
├── ResendButton (w-full, text-center, py-3, text-sm, text-primary, disabled:text-muted)
│   └── "重新发送验证码"
│
└── BackButton (text-center, margin-top: 16px, text-sm, text-muted, hover:text-primary)
    └── "使用其他方式登录"
```

### 3.4 注册表单界面

```
RegisterForm (切换至"注册"标签时显示)
├── InputGroup
│   ├── Label: "姓名" (text-sm, font-medium, margin-bottom: 6px)
│   └── Input (placeholder: "请输入真实姓名", w-full, rounded-xl, border, px-4, py-3)
├── InputGroup
│   ├── Label: "邮箱" (text-sm, font-medium, margin-bottom: 6px)
│   └── Input (type: email, placeholder: "example@email.com")
├── InputGroup
│   ├── Label: "手机号" (text-sm, font-medium, margin-bottom: 6px)
│   └── Input (type: tel, placeholder: "请输入11位手机号")
├── InputGroup
│   ├── Label: "设置密码" (text-sm, font-medium, margin-bottom: 6px)
│   └── Input (type: password, placeholder: "至少8位，包含字母和数字")
│   └── PasswordStrength (margin-top: 6px, flex, align-center, gap: 4px)
│       ├── StrengthBar (flex-1, h-1, bg-gray-200, rounded-full)
│       │   └── Fill (h-full, bg-accent, rounded-full, width: 60%)
│       └── "中等强度" (text-xs, text-muted)
├── InputGroup
│   ├── Label: "确认密码" (text-sm, font-medium, margin-bottom: 6px)
│   └── Input (type: password, placeholder: "再次输入密码")
├── AgreementCheckbox (flex, align-start, gap: 8px, margin-top: 16px)
│   ├── Checkbox (w-4 h-4, rounded, border, mt-0.5)
│   └── "我已阅读并同意 服务条款 和 隐私政策，并确认我已满18周岁。" (text-xs, text-secondary)
└── SubmitButton (w-full, bg-primary, text-white, rounded-xl, py-3, text-sm, font-medium, margin-top: 24px)
    └── "注册"
```

---

## 四、共享状态与数据流

### 4.1 问诊流程状态机

```typescript
// 问诊完整流程状态
interface ConsultationFlow {
  // 当前阶段
  currentStage: 'triage' | 'diagnosis' | 'analysis' | 'review' | 'treatment' | 'complete';

  // 会话信息
  session: {
    id: string;
    patientId: string;
    status: 'active' | 'completed' | 'aborted';
    createdAt: Date;
    completedAt?: Date;
  };

  // 各阶段数据
  triageData: {
    symptoms: string;
    recommendedDepartment: string;
    priority: 'low' | 'medium' | 'high' | 'emergency';
  };

  diagnosisData: {
    preliminaryDiagnosis: string;
    differentialDiagnoses: string[];
    confidence: number;
  };

  analysisData: {
    knowledgeSources: KnowledgeSource[];
    crossValidationResult: string;
  };

  reviewData: {
    contraindications: Contraindication[];
    guidelineCompliance: GuidelineResult[];
    riskScore: number;
  };

  treatmentData: {
    medications: Medication[];
    followUpPlan: FollowUpItem[];
    soap: SOAPRecord;
  };

  // 全局状态
  isEmergency: boolean;
  emergencyActions: EmergencyAction[];
  messages: ChatMessage[];
  currentAgent: AgentType | null;
  isStreaming: boolean;
}
```

### 4.2 页面间数据流

```
/login ──token──> /dashboard (患者首页)
                └─> /consultation/chat ──WebSocket──> 实时对话
                                    └─> /consultation/analysis (阶段2)
                                    └─> /consultation/review (阶段3)
                                    └─> /consultation/summary (完成)
                └─> /records (查看历史)
                └─> /profile (个人中心)

/login ──token──> /consultation/chat (医生模式)
                └─> /patients (患者列表)
                └─> /consultation/review (合规复核)
```

### 4.3 WebSocket 事件映射

| 事件 | 发送方 | 接收方 | 页面响应 |
|------|--------|--------|---------|
| `agent_start` | Server | Client | 显示 Agent 标签 + 加载指示器 |
| `token` | Server | Client | 追加字符到当前消息，触发滚动 |
| `agent_end` | Server | Client | 隐藏加载指示器，显示 Manifest 卡片 |
| `error` | Server | Client | 显示错误提示，提供重试按钮 |
| `info` | Server | Client | 显示系统通知（Toast） |
| `emergency` | Server | Client | 触发紧急模式覆盖层 + 红色免责声明 |
| `message` | Client | Server | 用户发送症状描述 |
| `complete` | Client | Server | 用户点击"完成问诊"，进入总结页 |

---

> **Part 1 结束**  
> 覆盖 3 个高优先级页面：智能问诊对话页、问诊完成总结页、登录注册页。  
> 包含完整的组件层级、交互规范、状态管理和数据流设计。
