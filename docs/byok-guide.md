# BYO Key 配置指南

> 本文档说明如何为 MediNexus 配置 LLM Provider。
> MediNexus **不内置任何 API Key**，用户需自行提供。

---

## 默认配置

无需任何配置即可启动 MediNexus（规则引擎降级模式）：

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

此模式下所有 Agent 使用规则引擎/关键词匹配，输出会标注 `[模式: 规则引擎]`。

---

## 配置 Ollama (推荐，免费)

### 1. 安装 Ollama

下载并安装：[https://ollama.com](https://ollama.com)

### 2. 下载模型

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### 3. 启动 Ollama

```bash
ollama serve
```

### 4. 配置 .env

在项目根目录创建 `.env`：

```env
MEDINEXUS_LLM_PROVIDER=ollama
MEDINEXUS_OLLAMA_BASE_URL=http://localhost:11434
MEDINEXUS_OLLAMA_MODEL=qwen2.5:7b
```

---

## 配置 Anthropic Claude

### 1. 获取 API Key

在 [console.anthropic.com](https://console.anthropic.com) 注册并获取 API Key。

### 2. 配置 .env

```env
MEDINEXUS_LLM_PROVIDER=anthropic
MEDINEXUS_ANTHROPIC_KEY=sk-ant-xxxxxxxxxxxx
MEDINEXUS_ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

---

## 配置 OpenAI

### 1. 获取 API Key

在 [platform.openai.com](https://platform.openai.com) 注册并获取 API Key。

### 2. 配置 .env

```env
MEDINEXUS_LLM_PROVIDER=openai
MEDINEXUS_OPENAI_KEY=sk-xxxxxxxxxxxx
MEDINEXUS_OPENAI_MODEL=gpt-4o
MEDINEXUS_OPENAI_BASE_URL=https://api.openai.com/v1
```

---

## 多 Provider 降级链

MediNexus 支持 Provider 降级。当一个 Provider 不可用时自动切换到下一个：

```env
# 降级链: Ollama → OpenAI → Anthropic
MEDINEXUS_LLM_PROVIDER=ollama
MEDINEXUS_OPENAI_KEY=sk-xxxxx
MEDINEXUS_ANTHROPIC_KEY=sk-ant-xxxxx
```

当所有 LLM 不可用时，自动降级到规则引擎。

---

## 验证配置

```bash
# 验证 LLM 连接
cd backend
python -c "
from llm.client import BaseLLMClient
print('LLM client ready')
"

# 测试 Ollama 连接
curl http://localhost:11434/api/tags

# 验证后端启动
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
