# 02-DAG-FSM-Engine (Agent Primitives)

## 架构宣言 (Architecture Manifesto)
本原语旨在彻底摧毁智能体（Agent）开发中泛滥的“状态泥潭（State Mud）”。
在原生的 Agent 循环中，感知、推理、行动往往被硬编码在一个巨大的 `while True` 内部，通过脆弱的 `if/else` 标志位进行路由。这种**执行逻辑与控制流的物理缠绕**，使得系统无法进行中断、快照、或者时序追踪。

`02-DAG-FSM-Engine` 的核心哲学是**控制权解耦与物理隔离**。

## 物理设计 (Physical Design)

引擎将系统强行撕裂为三个绝对隔离的物理层：

1. **工作间 (DAGNode)**: 
   绝对隔离的沙盒算子。Node 内部完全不知道外部世界长什么样，也看不见其他 Node。它只做三件事：通电执行（`execute`）、读取全局只读记忆、将计算结果打包装箱。
2. **标准物流箱 (NodeResult)**: 
   强类型的通信信封。包含 `payload`（业务数据）和 `next_node`（路由标签）。这是节点与系统对话的唯一合法凭证。
3. **中央履带与厂长 (DAGEngine)**: 
   唯一的全局控制台。剥夺所有节点的路由决定权，由 Engine 在外层通过 `while` 循环统一接管。Engine 负责拆箱、更新全局账本（`global_state`），并根据路由标签将执行权移交给下一个节点。

## 核心特性 (Features)
- **Topological & State Isolation**: 节点崩溃不会波及全局引擎，便于实现精准的单节点熔断与重试。
- **Pause & Resume Ready**: 控制流在 Engine 手中，随时可以在 Node 切换间隙进行状态快照（Snapshot）和序列化存盘，完美支持长时间跨度的 Agent 挂起与恢复。
- **No Black Boxes**: 所有的状态流转完全暴露在 `Engine.run()` 的表层循环中，为引入全链路追踪（Tracing）和关联 ID（Correlation ID）打下基础设施。

## 使用契约 (Contract)
任何接入本引擎的 Agent 算子，必须严格继承 `DAGNode`，并返回 `NodeResult` 结构。禁止在 Node 内部私自拉起其他 Node。

```python
# 示例定义
class PerceptionNode(DAGNode):
    async def execute(self, state):
        # 纯粹的局部执行
        return NodeResult(next_node="Decision", payload={"sensor": "data"})
```
