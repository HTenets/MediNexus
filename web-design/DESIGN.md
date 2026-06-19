---
name: MediNexus
colors:
  surface: '#f8f9ff'
  surface-dim: '#ccdbf3'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d5e3fc'
  on-surface: '#0d1c2e'
  on-surface-variant: '#424656'
  inverse-surface: '#233144'
  inverse-on-surface: '#eaf1ff'
  outline: '#727687'
  outline-variant: '#c2c6d8'
  surface-tint: '#0054d6'
  primary: '#0050cb'
  on-primary: '#ffffff'
  primary-container: '#0066ff'
  on-primary-container: '#f8f7ff'
  inverse-primary: '#b3c5ff'
  secondary: '#585f6a'
  on-secondary: '#ffffff'
  secondary-container: '#dce3f0'
  on-secondary-container: '#5e6570'
  tertiary: '#a33200'
  on-tertiary: '#ffffff'
  tertiary-container: '#cc4204'
  on-tertiary-container: '#fff6f4'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae1ff'
  primary-fixed-dim: '#b3c5ff'
  on-primary-fixed: '#001849'
  on-primary-fixed-variant: '#003fa4'
  secondary-fixed: '#dce3f0'
  secondary-fixed-dim: '#c0c7d3'
  on-secondary-fixed: '#151c25'
  on-secondary-fixed-variant: '#404751'
  tertiary-fixed: '#ffdbd0'
  tertiary-fixed-dim: '#ffb59d'
  on-tertiary-fixed: '#390c00'
  on-tertiary-fixed-variant: '#832600'
  background: '#f8f9ff'
  on-background: '#0d1c2e'
  surface-variant: '#d5e3fc'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 60px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: notoSans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: notoSans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: notoSans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: notoSans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 40px
  gutter: 24px
  section-gap: 64px
  max-width: 1440px
---

## 品牌风格 (Brand & Style)

本设计系统致力于构建一个高端、专业且值得信赖的医疗 AI 平台视觉体系。设计核心在于平衡“临床的严谨性”与“AI 的未来感”。

*   **视觉风格：** 融合了现代医疗 SaaS 的极简主义与 **Glassmorphism (玻璃拟态)** 的轻盈感。参考 Apple Health 的通透感与 Linear 的严谨布局，强调高白空间比例、细腻的阴影和自然的层级关系。
*   **情绪表达：** 传达专业 (Professional)、纯净 (Clinical White)、高效 (Efficient) 与关怀 (Caring) 的情感。
*   **目标受众：** 医疗从业人员、科研人员及需要高精度 AI 辅助决策的机构。
*   **设计原则：** 拒绝冗余装饰，优先保障信息的可读性与辅助决策的清晰度，确保符合 WCAG AA 级对比度标准。

## 色彩方案 (Colors)

色彩配置以克制的医疗蓝与临床白为基调，通过明度的精细变化区分功能区域。

*   **品牌主色 (Primary):** `#0066FF` - 核心行动点与品牌识别色，象征医学的严谨与 AI 的精准。
*   **辅助背景色 (Secondary):** `#EBF2FF` - 用于卡片悬浮、背景分区或强调弱交互区域，提供柔和的视觉过渡。
*   **中性色 (Neutral/Text):** 使用石板灰 (`#475569`) 作为主要正文颜色，避免纯黑带来的视觉疲劳。
*   **功能色：** 
    *   成功 (Success): `#10B981` (翠绿色)
    *   警告 (Warning): `#F59E0B` (琥珀色)
    *   错误 (Error): `#EF4444` (医用红色)
*   **背景 (Background):** 采用极浅的灰蓝 (`#F8FAFC`) 以衬托纯白色的卡片容器。

## 字体排印 (Typography)

字体系统优先考虑长篇医疗数据与 AI 生成内容的阅读舒适度。

*   **标题 (Headings):** 采用 **Plus Jakarta Sans** (作为 Figtree 的优化替代)，其现代化的几何造型能赋予界面高级感，在大字号下具有极佳的张力。
*   **正文 (Body):** 采用 **Noto Sans**，确保在复杂的医学词汇与中文环境下拥有极致的清晰度。
*   **层级策略：** 采用大字号阶梯。移动端标题需向下缩放一档。
*   **对齐：** 文本一律左对齐，保持逻辑的线性连贯。重要数据指标建议加粗处理。

## 布局与间距 (Layout & Spacing)

采用基于 8px 的网格系统，创造宽敞、通透的临床感。

*   **网格模型：** 桌面端使用 12 列响应式流体网格。
*   **呼吸感：** 核心内容容器间距设定为 64px (section-gap)，卡片内边距不低于 32px，通过“负空间”引导用户视线。
*   **响应式适配：**
    *   **Desktop (1440px+):** 固定最大宽度，双侧留白。
    *   **Tablet (768px - 1024px):** 容器边距缩减至 24px，侧边栏折叠。
    *   **Mobile (375px+):** 切换为单列布局，间距缩减至 16px。

## 深度与高度 (Elevation & Depth)

本系统不使用高对比度的深色投影，而是通过模拟自然光照与半透明材质建立层级。

*   **环境阴影 (Ambient Shadows):** 使用超长扩散半径 (30px-50px)、低不透明度 (4%-8%) 的蓝色调阴影 (`rgba(0, 102, 255, 0.05)`)，模拟物体悬浮在水面上的质感。
*   **玻璃拟态 (Glassmorphism):** 顶部导航栏与侧边栏采用背景模糊 (Backdrop Blur: 20px) 处理，配合 0.5px 的半透明白色描边，增强界面的深度与通透感。
*   **层级逻辑：** 
    *   Level 0: 背景底色 (`#F8FAFC`)
    *   Level 1: 基础卡片（无投影，白色填充）
    *   Level 2: 浮动面板/悬浮状态（带柔和投影）

## 形状 (Shapes)

采用大圆角语言以削弱医疗软件常见的冰冷感，增加亲和力。

*   **核心圆角 (Base):** 所有标准卡片、容器统一使用 **24px** 圆角。
*   **组件圆角:** 
    *   输入框与按钮：**12px**。
    *   小标签 (Tags/Chips)：全圆角 (Pill-shaped)。
*   **视觉一致性：** 内部元素的圆角半径应与外部容器形成等距嵌套关系（内圆角 = 外圆角 - 间距）。

## 组件库 (Components)

*   **按钮 (Buttons):** 
    *   Primary: `#0066FF` 填充，白色文字，12px 圆角。
    *   Secondary: `#EBF2FF` 背景，`#0066FF` 文字。
    *   交互：悬浮时增加 4px 模糊投影，禁止使用重渐变。
*   **医疗卡片 (Medical Cards):** 
    *   纯白底色，24px 圆角，带 1px 超浅灰色边框 (`#E2E8F0`)。
    *   内部标题使用 Plus Jakarta Sans 600 字重。
*   **输入字段 (Input Fields):** 
    *   背景采用 `#F1F5F9`，聚焦时边框变为品牌蓝并增加浅蓝发光。
*   **状态标签 (Status Chips):** 
    *   采用浅色背景 (Soft Tint) + 深色文字，例如：待诊 (Pending) 使用浅蓝色调，已完成 (Completed) 使用浅绿色调。
*   **AI 对话流 (AI Chat Bubbles):** 
    *   用户端：深蓝色背景。
    *   AI 端：玻璃拟态透明质感，左侧带有 4px 品牌色装饰条。
*   **列表 (Lists):**
    *   使用宽行距，条目间以 1px 极细线分隔，左侧预留图标间距。