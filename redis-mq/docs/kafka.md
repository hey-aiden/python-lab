# Kafka 入门

> 一篇 Kafka 的通识介绍,从历史背景、使用场景、分布式关注点三个维度叙述。
> 配合本仓库 `redis-mq` 子项目源码阅读:`src/app/services/kafka_service.py`、
> `src/app/endpoints/log_collector.py`。

## 目录

1. [历史背景](#1-历史背景)
2. [常用使用场景](#2-常用使用场景)
3. [分布式场景下的关注点](#3-分布式场景下的关注点)

---

## 1. 历史背景

### 1.1 诞生:LinkedIn 的数据管道之痛

Kafka 由 **LinkedIn** 于 2010 年前后开发,创始人是 **Jay Kreps、Neha Narkhede、Jun Rao**。

当时的背景是:LinkedIn 需要实时收集、处理海量的**活动流数据**——用户点击、页面浏览、
操作日志、系统指标。已有的做法是各业务团队各自对接、点对点传输(如消息队列 + 自定义
ETL),导致:

- 数据源和下游之间形成网状连接,每加一个消费者都要改生产方;
- 日志、指标、活动流各用一套系统,无法统一;
- 数据量增长后,吞吐和可扩展性跟不上。

Kafka 的解法是把它设计成一个 **分布式提交日志(distributed commit log)**——所有数据
追加写入一个可复用的、分区的、可回放的日志,多个消费者各自订阅同一份数据。这个核心
设计决定了它后来的一切特性:高吞吐、持久化、解耦。

### 1.2 命名

名字取自作家 **Franz Kafka(弗兰兹·卡夫卡)**。创始人的说法是:系统是"为写而优化"的,
用一位作家的名字很合适。

### 1.3 开源与演进时间线

| 时间 | 事件 |
|------|------|
| 2010 | LinkedIn 内部开发 |
| 2011.01 | 开源 |
| 2012.10 | 成为 Apache 顶级项目 |
| 2014 | 创始人创办 **Confluent**,围绕 Kafka 做商业化与生态 |
| 2021 | Kafka 2.8 引入 **KRaft** 模式(去掉 ZooKeeper,见 1.4) |
| 2023 | KRaft 生产就绪,ZooKeeper 逐步废弃 |

### 1.4 架构演进:从 ZooKeeper 到 KRaft

早期 Kafka 依赖 **ZooKeeper** 做元数据协调(存储主题/分区/副本/leader 信息、选举等),
这带来了额外的运维负担,也限制了扩展上限。

**KRaft**(Kafka Raft,由 KIP-500 提出)把元数据管理收敛进 Kafka 自身,用 Raft 共识
协议选出一个 controller 节点维护元数据。好处:

- 去掉一个独立组件,部署更简单;
- 元数据管理性能更好(支持更多分区);
- controller 故障切换更快。

> 现代部署基本都用 KRaft 模式;ZooKeeper 模式仅存量系统还在用。

---

## 2. 常用使用场景

> 一句话概括:凡是要**高吞吐、可持久化、可回放、异步解耦**地搬运数据,都可以考虑 Kafka。

| 场景 | 说明 | 典型例子 |
|------|------|----------|
| **日志收集 / 用户埋点** | 行为事件统一写入 Kafka,下游各自消费 | App 埋点、访问日志、审计日志 |
| **事件驱动 / 事件溯源** | 业务状态变更作为"事件"广播,多系统订阅 | 下单 → 库存/积分/通知/风控各自响应 |
| **数据管道 / CDC** | 数据库变更流同步到数仓、缓存、搜索 | MySQL binlog → Debezium → Kafka → 数仓 |
| **流式处理** | 配合 Flink / Spark Streaming / Kafka Streams 实时计算 | 实时统计、实时风控、实时大屏 |
| **削峰填谷 / 异步解耦** | 洪峰请求先入 Kafka,下游按自己的节奏消费 | 秒杀、抢购、批量任务 |

几个典型场景的要点:

- **日志收集(本仓库实现)**——客户端唯一职责就是上报事件,`POST /log/track` 这种
  专用收集端点本身就是业务,不是"为了调 Kafka 而写的接口"。
- **业务事件(更常见)**——Kafka 藏在业务 service 里当**副作用**:秒杀下单成功后,
  在 `order()` 里顺手 `produce` 一条 `order_created` 事件,外面没有裸露的
  `/kafka/produce` 接口。这才是 Kafka 最常见的形态。
- **削峰填谷**——下游处理能力有限时,Kafka 当缓冲,让生产速度与消费速度解耦,保护
  下游(数据库、慢服务)不被瞬时洪峰打垮。

### 什么时候不适合 Kafka

- **延迟敏感的同步 RPC**——Kafka 为吞吐优化,单条消息毫秒级延迟,不适合做同步调用。
- **点对点即时消息 / 需要复杂路由和优先级的任务队列**——RabbitMQ 更合适。
- **消息量很小**——引入 Kafka 的运维成本(分区、副本、监控)不划算。
- **强事务回执**——Kafka 默认"至少一次",精确一次要靠幂等 + 事务设计。

---

## 3. 分布式场景下的关注点

这是 Kafka 真正复杂的地方。单机是"追加写文件",分布式则要处理顺序、副本、一致性、
消费协调等一系列问题。下面按主题梳理。

### 3.1 分区与顺序(Partition & Ordering)

- **分区(partition)是并行度和顺序的基本单位**。一个主题可拆成多个分区,分布在不同
  broker 上;写入时可并行写多个分区,从而线性扩展吞吐。
- **顺序只保证在单个分区内**;跨分区是无序的。
- 要让"同一个实体"的消息有序,用 **key 分区**:生产者指定 key,按 key 哈希路由到固定
  分区。例如埋点按 `user_id` 做 key,同一用户的事件就落在同一分区、严格有序
  (本仓库 `log_collector.py` 即如此)。

```python
# 同 key → 同分区 → 分区内有序
producer.produce(topic, value=json, key=user_id)
```

### 3.2 副本与高可用(Replication & ISR)

- 每个分区有一个 **leader** 副本和若干 **follower** 副本;**读写都走 leader**,
  follower 只做复制备份。
- leader 宕机后,controller 从 **ISR(In-Sync Replicas,同步副本集合)** 中选一个新
  leader,服务不中断——这是 Kafka 高可用的基础。
- **ISR** 指"追上 leader 进度"的副本集合;落后太多的 follower 会被移出 ISR,从而在
  选举时不被选上,避免数据丢失。

### 3.3 生产端可靠性配置(acks & min.insync.replicas)

`acks` 决定"何时算写成功",是**吞吐与可靠性的直接权衡**:

| acks | 含义 | 可靠性 | 延迟 |
|------|------|--------|------|
| `0` | 不等确认,发出去就算 | 最低,可能丢 | 最低 |
| `1` | leader 写入本地日志即确认 | 中,leader 宕机可能丢 | 中 |
| `all`/`-1` | 所有 ISR 副本写入才确认 | 最高 | 最高 |

配合 **`min.insync.replicas`**:当 `acks=all` 时,ISR 数量低于该值则拒绝写入,防止
"只剩一个副本还继续写、该副本又宕机"导致丢数据。典型生产配置:`acks=all` +
`min.insync.replicas=2`(至少 3 副本)。

### 3.4 消息投递语义(Delivery Semantics)

| 语义 | 含义 | 如何实现 |
|------|------|----------|
| **at-most-once**(至多一次) | 可能丢,不会重复 | `acks=0`,或先提交 offset 再处理 |
| **at-least-once**(至少一次,默认) | 可能重复,不会丢 | 重试 + 处理后再提交 offset |
| **exactly-once**(精确一次) | 不丢不重 | 幂等生产者 + 事务(流处理场景) |

要点:

- 默认是 **at-least-once**——网络超时重试可能造成重复投递,**消费者必须做幂等**
  (靠业务唯一键去重,如订单号)。
- 幂等生产者(`enable.idempotence=true`)用「生产者 ID + 消息序号」在 broker 端去重,
  解决"重试导致同一条消息写两份"的问题。
- exactly-once 主要用于「读-处理-写」的流式处理(如 Kafka Streams 的消费→计算→输出
  作为一个事务),普通应用通常用"at-least-once + 幂等消费"就够。

### 3.5 消费组与再均衡(Consumer Group & Rebalance)

- **消费组**内的多个消费者分摊一个主题的分区;**一个分区同一时刻只能被组内一个
  消费者消费**,因此组内消费者数量超过分区数是浪费(多出来的消费者闲置)。
- 消费者加入/离开/宕机时触发 **rebalance**,分区重新分配:
  - **eager(急切)**:先全部停止消费,再重新分配——有"停摆窗口";
  - **cooperative(协作/粘性,推荐)**:只调整受影响的分区,其余继续消费。

### 3.6 持久化与保留(Retention & Replay)

- Kafka 把消息**落盘**保存(顺序追加 + 页缓存,所以吞吐高)。
- 消息**消费后不删除**,按配置保留一段时间或大小(`retention.ms` / `retention.bytes`,
  默认约 7 天),之后按段清理。这意味着可以**回放**历史数据(新消费者补历史、修复 bug
  后重算),这是它区别于传统队列的核心能力之一。

### 3.7 扩展性与运维关注

- **分区数只能增、不能减**(减分区需要重建主题)。分区数是吞吐上限和消费并行度的
  天花板,扩容前要规划好;也不能为了图省事设太多分区(增加元数据与文件句柄开销)。
- **offset lag(消费滞后)**是核心监控指标:消费者进度落后生产者多少。lag 持续增长
  说明下游处理不过来,需要扩消费者或优化消费逻辑。
- **吞吐调优**靠批量与压缩:`linger.ms` / `batch.size` 攒批、`compression.type` 压缩,
  用一点延迟换吞吐。
- **消费者位移(offset)**可手动或自动提交;手动提交能精确控制"处理完才提交",配合
  幂等消费实现 at-least-once。

### 3.8 一张图记住权衡

```
顺序  ←→  吞吐      分区分区,key 保证分区内有序
可靠性 ←→  延迟      acks / min.insync.replicas
不丢  ←→  不重复     at-least-once + 幂等消费
并行  ←→  顺序      partition 数 vs 全局有序
```

### 3.9 本地开发:advertised.listeners 与 localhost/IPv6 的坑

macOS 上单机跑 Kafka 时的常见连接问题:

- **现象**:consumer 报 `Connect to ipv6#[::1]:9092 failed: Connection refused`,
  连不上 group coordinator,`poll` 一直返回空(producer 因异步投递可能侥幸成功)。
- **根因**:broker 的 `advertised.listeners` 是 `localhost:9092`,而 macOS 上 `localhost`
  会优先解析成 IPv6 `::1`;broker 通常只监听 IPv4,于是客户端按 advertised 地址重连时被拒。
  注意:客户端即便用 `127.0.0.1:9092` 做 bootstrap,拿到元数据后仍会按 advertised 地址重连。
- **诊断**:用 admin 列出 broker 元数据,看到 `broker host = localhost` 即中招。

修法有两种,按推荐顺序:

**① broker 侧(治本):把 advertised 地址改成 IPv4**

在 Kafka `server.properties` 里显式指定,重启 broker:

```properties
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://127.0.0.1:9092
```

要点:`listeners` 是 broker 实际监听的地址,`advertised.listeners` 是它告诉客户端
去连的地址;单机开发时后者务必填一个客户端能解析、且解析结果正确的地址。

**② 客户端侧(兜底):强制 IPv4 解析**

不动 broker,在 confluent-kafka 客户端配置里加 `broker.address.family=v4`,让客户端
解析 hostname 时只走 IPv4,`localhost` 就不会再被解析成 `::1`:

```python
Producer({
    "bootstrap.servers": "127.0.0.1:9092",
    "broker.address.family": "v4",  # any / v4 / v6，默认 any
})
```

本仓库已在 `kafka_service.py` 的 producer / consumer / admin 里统一加上了这行。

---

## 小结

- **历史**:LinkedIn 为统一数据管道而生,核心是"分布式提交日志",现已演进到 KRaft 去
  ZooKeeper。
- **场景**:日志收集、事件驱动、数据管道、流式处理、削峰填谷——凡"高吞吐 + 持久化 +
  可回放 + 异步解耦"皆可。
- **分布式关注点**:分区与顺序、副本与 ISR、acks 可靠性、投递语义、消费组 rebalance、
  持久化保留、扩展与 lag 监控。这些是生产环境真正要下功夫的地方。
