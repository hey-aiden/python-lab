# Agent 长消息列表维护：上下文消息处理

Agent 在连续多轮对话中需要**记住之前的交互**，这就涉及一个核心问题：消息列表越来越长，如何维护和传递上下文？

基于 `langchain` + `langgraph` 的 Agent，有两种消息列表维护方式：**手动拼接**和**框架托管**。

## 问题背景

LLM 本身是无状态的——每次 API 调用都是一次独立的「失忆」对话。要让 Agent 在第二轮还记得第一轮说过什么，必须在每次请求中**把历史消息一起传回去**：

```
第 1 轮：传入 [{user: "今天天气?"}]     → LLM 看到 1 条
第 2 轮：传入 [{user: "今天天气?"}, {assistant: "晴天"}, {user: "明天呢?"}] → LLM 看到 3 条
第 3 轮：传入 [...前 3 条..., {assistant: "..."}, {user: "后天呢?"}] → LLM 看到 5 条
```

消息列表逐轮增长，维护这份上下文就成了关键。

## 方案对比

| | 方案 A：手动消息列表 | 方案 B：MemorySaver 托管 |
|---|---|---|
| **维护方式** | 手动 `list.append()` | 框架自动写 checkpoint |
| **每次 invoke 传参** | 传入全部历史 `[{...}, {...}, ...]` | 只传当前一条 `[{...}]` |
| **上下文来源** | 自己的 `message_list` 变量 | MemorySaver 按 `thread_id` 自动注入 |
| **底层 token 消耗** | 相同——每轮都传完整历史 | 相同——框架内部也是传完整历史 |
| **多会话支持** | 手动维护多个列表 | 不同 `thread_id` 天然隔离 |
| **灵活性** | 高——随时删改、截断、过滤历史 | 低——需理解 checkpoint API 才能干预 |
| **依赖** | 仅 langchain | 额外依赖 langgraph |

## 方案 A：手动维护消息列表

### 原理

在 Agent 外部维护一个 `message_list = []`，每次 `invoke()` 前追加用户消息，传入**全部历史**，LLM 返回后再追加 AI 回复。你完全掌控消息的增删改查。

```
message_list（内存中的普通 Python 列表）
  ├── invoke() 前：append({"role": "user", "content": user_msg})
  ├── invoke() 中：传入全部 message_list → LLM 基于完整上下文回答
  └── invoke() 后：append({"role": "assistant", "content": ai_response})
```

### 代码

```python
def use_message_list():
    agent = create_agent(
        model=ChatDeepSeek(model=os.getenv("DEEPSEEK_MODEL")),
        system_prompt="你是一个友好助人的AI助手",
    )
    message_list = []   # ← 上下文数据的唯一来源

    while True:
        user_msg = input("\n你:")
        if user_msg.lower() in ["exit", "quit", "退出"]:
            break
        if not user_msg.strip():
            continue

        message_list.append({"role": "user", "content": user_msg})

        result = agent.invoke({"messages": message_list})        # 传全部历史
        ai_response = result["messages"][-1].content             # 取最后一条

        message_list.append({"role": "assistant", "content": ai_response})
        print(f"🤖 助手：{ai_response}")
```

### 多轮数据流

```
第 1 轮:
  message_list = [{user: "今天天气?"}]
  → invoke(messages=message_list) → LLM 看到 1 条
  → message_list = [{user: "..."}, {assistant: "晴天"}]

第 2 轮:
  message_list = [{user: "..."}, {assistant: "晴天"}, {user: "明天呢?"}]
  → invoke(messages=message_list) → LLM 看到 3 条（有上下文！）
  → message_list = [...前 3 条..., {assistant: "明天也晴天"}]

第 N 轮:
  message_list = [{...}, {...}, ... N * 2 - 1 条 ...]
  → invoke(messages=message_list) → LLM 看到全部历史
```

### 长列表维护策略

消息越攒越多，可以通过以下方式控制长度：

```python
MAX_HISTORY = 20  # 只保留最近 20 条

# 方式 1：截断末尾
if len(message_list) > MAX_HISTORY:
    message_list = message_list[-MAX_HISTORY:]

# 方式 2：保留 system prompt + 最近 N 条
# system_msg = message_list[0]  # 第一轮通常包含 system 消息
# message_list = [system_msg] + message_list[-(MAX_HISTORY - 1):]
```

这就是手动维护的优势——列表在你手里，想怎么截就怎么截。

---

## 方案 B：MemorySaver 托管上下文

### 原理

`langgraph` 的 `MemorySaver` 在每次 `invoke()` 后自动保存对话状态（checkpoint）。同一个 `thread_id` 共享同一份记忆，**只需传入当前用户消息**，框架内部自动注入历史。

```
agent.invoke({"messages": [当前消息]}, config={thread_id: "..."})
  │
  ├─ 1. 根据 thread_id 查找上次保存的 checkpoint
  ├─ 2. 从 checkpoint 恢复历史消息，合并到当前 messages 前面
  ├─ 3. 完整上下文发给 LLM
  ├─ 4. LLM 返回后，自动写回新的 checkpoint
  └─ 5. result["messages"] 包含完整历史 + 本轮回复
```

### 代码

```python
from langgraph.checkpoint.memory import MemorySaver

def use_memory():
    agent = create_agent(
        model=ChatDeepSeek(model=os.getenv("DEEPSEEK_MODEL")),
        system_prompt="你是一个友好助人的AI助手",
        checkpointer=MemorySaver(),    # ← 开启上下文托管
    )

    # 同一 thread_id 共享记忆，不同会话用不同 id
    config = {"configurable": {"thread_id": "session-1"}}

    while True:
        user_msg = input("\n你:")
        if user_msg.lower() in ["exit", "quit", "退出"]:
            break
        if not user_msg.strip():
            continue

        # 只传当前消息，历史由 MemorySaver 自动注入
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_msg}]},
            config=config,
        )
        ai_response = result["messages"][-1].content
        print(f"🤖 助手：{ai_response}")
```

### 内部数据流（两轮示例）

```
第 1 轮:
  invoke({"messages": [{user: "今天天气?"}]}, config={thread_id: "session-1"})
  → MemorySaver: 首次使用 thread_id → 无历史
  → messages = [{user: "今天天气?"}]
  → LLM 返回 "晴天" → MemorySaver 写入 checkpoint

第 2 轮:
  invoke({"messages": [{user: "明天呢?"}]}, config={thread_id: "session-1"})
  → MemorySaver: 找到 session-1 → 从 checkpoint 恢复历史
  → messages = [{user: "今天天气?"}, {assistant: "晴天"}, {user: "明天呢?"}]
  → LLM 看到完整上下文 → 返回 "明天也晴天"
  → MemorySaver 更新 checkpoint
```

### 多会话隔离

不同 `thread_id` 的记忆互不干扰：

```python
# 会话 A
config_a = {"configurable": {"thread_id": "user-alice"}}
agent.invoke({"messages": [{user: "我叫 Alice"}]}, config=config_a)

# 会话 B — 完全独立
config_b = {"configurable": {"thread_id": "user-bob"}}
agent.invoke({"messages": [{user: "我是 Bob"}]}, config=config_b)
```

---

## 选型建议

| 场景 | 推荐方案 |
|------|----------|
| 快速原型、单会话 | MemorySaver，代码最少 |
| 需要对历史做**截断、过滤、摘要** | 手动维护，列表在手里随意改 |
| 多用户/多会话 | MemorySaver + 不同 `thread_id` |
| 不想引入 langgraph 依赖 | 手动维护 |

---

## 上下文压缩

MemorySaver 只存不压——每轮消息原封不动保存，消息列表不断膨胀，最终可能超出模型的上下文窗口（DeepSeek 通常 128K token）。压缩解决的就是「消息太长怎么办」。

本质是一个权衡：**拿细节精度换时间跨度**。

### 三种压缩方式

#### ① 截断（Truncation）

只保留最近 N 条，旧的直接丢弃——最简单，代价也最大。

```python
MAX_RECENT = 20

if len(message_list) > MAX_RECENT:
    message_list = message_list[-MAX_RECENT:]  # 旧消息永久丢失
```

#### ② 摘要压缩（Summarization）

用 LLM 把旧对话压缩成一段简短摘要，替换掉冗长的原始消息。

```
压缩前（~5000 token）:
  [20 条原始消息，包括用户自我介绍、多轮推荐讨论...]

压缩后（~200 token）:
  [摘要] 用户是小明，25岁，在北京工作。之前咨询了川菜馆推荐，
  助手推荐了3家，用户对第二家感兴趣并询问了距离。
```

```python
def summarize_history(message_list, llm):
    """把旧消息压缩成一段摘要"""
    old_text = "\n".join([m["content"] for m in message_list])
    summary = llm.invoke(
        f"请用一两句话总结以下对话的关键信息：\n{old_text}"
    )
    return summary.content
```

#### ③ 截断 + 摘要（混合）

近期消息保留原文，远期消息压缩成摘要——兼顾细节和跨度：

```
message_list = [
    {role: "system", content: "[历史摘要]: 用户叫小明，之前讨论过川菜馆..."},  ← 压缩后的远期
    {role: "user", content: "第一家离我多远？"},                              ← 近期原文保留
    {role: "assistant", content: "第一家距离你公司 2.3 公里"},
    {role: "user", content: "人均多少？"},
]
```

```python
WINDOW_SIZE = 10       # 近期保留原文的条数
COMPRESS_TRIGGER = 30  # 超过这个数量触发压缩

if len(message_list) > COMPRESS_TRIGGER:
    # 把前面的压成摘要，后面保留原文
    old_part = message_list[: -WINDOW_SIZE]
    recent_part = message_list[-WINDOW_SIZE:]

    summary = summarize_history(old_part, MODEL)

    # 摘要 + 近期原文
    message_list = [
        {"role": "system", "content": f"[历史对话摘要]: {summary}"}
    ] + recent_part
```

### 框架内置方案

LangChain 直接封装了上述逻辑，开箱即用：

```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=MODEL,
    max_token_limit=2000,   # 总 token 不超这个数
    return_messages=True,
)
```

内部自动执行「截断 + 摘要」：近期保留原文，远期压缩为摘要，总 token 始终控制在 `max_token_limit` 内。

### 对比

| 方式 | 信息保留 | 复杂度 | 适用场景 |
|------|----------|--------|----------|
| 截断 | 旧消息全丢 | 最低 | 只需近期上下文的对话 |
| 摘要 | 保留关键信息，丢细节 | 中等 | 需要长期记忆但不纠结原文 |
| 截断 + 摘要 | 近期原文 + 远期摘要 | 较高 | 既需早期事实又关注最新细节 |

---

## 关键代码细节

### `[-1]` 取最后一条消息

```python
result["messages"][-1].content
```

Python 负数下标 = 从末尾往前数。消息列表长度不确定时，`-1` 始终指向最新一条 = AI 本轮回复。

### `input()` 与空消息过滤

```python
if not user_msg.strip():
    continue
```

`strip()` 去掉首尾空白。用户只按回车或打空格时，过滤掉避免无意义的 API 调用。

### 异常处理分层

```python
except (KeyboardInterrupt, SystemExit):
    raise                     # 用户主动退出，放行
except Exception as e:        # noqa: BLE001
    print(f"❌ 出错了：{e}")  # API 异常兜底，不中断对话
```

第一层放行 `Ctrl+C`，第二层兜住 API 调用异常——长对话中不能让一次请求失败终止整个会话。

---

## 启动

```bash
# robot.py 入口 create_robot()，当前默认使用 MemorySaver
uv run python -m app.robot
```

`.env` 配置：

```env
DEEPSEEK_MODEL="deepseek-chat"
DEEPSEEK_API_KEY="sk-your-key"
```
