---
name: web-search-zero-handling
description: 当 WebSearch 返回结果为 0 条时的处理策略
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 42e518b8-d51f-47f1-92ce-81395a239b7e
---

# WebSearch 结果为 0 时的处理

**规则：** 如果 WebSearch 搜索结果为 0 条（无有效结果），则停止本次回复，不给用户输出任何内容。

**Why:** 网络搜索结果为空时，说明当前问题无法通过搜索获取有效信息。继续输出基于猜测的信息会误导用户，不如保持沉默。

**How to apply:**
1. 调用 WebSearch 后检查搜索结果数量
2. 如果结果为 0（或所有结果都不相关），使用 `return` 语句提前结束，不产生任何用户可见的输出
3. 不需要向用户解释为什么没有结果，也不需要道歉
4. 用户如果看到空回复会自行判断
