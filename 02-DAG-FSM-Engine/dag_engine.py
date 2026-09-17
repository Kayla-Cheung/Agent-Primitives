import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque

@dataclass
class NodeResult:
    """DAG 节点执行结果 (不再包含 next_node，彻底解耦拓扑)"""
    payload: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None

class DAGNode:
    """DAG 原子节点，只负责纯粹的计算/I/O"""
    def __init__(self, name: str):
        self.name = name

    async def execute(self, state: Dict[str, Any]) -> NodeResult:
        raise NotImplementedError("Subclasses must implement execute()")

class DAGEngine:
    """真正的 DAG 并发引擎 (基于 Kahn 拓扑排序算法)"""
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        self.edges: Dict[str, List[str]] = {}
        self.in_degree: Dict[str, int] = {}
        self.global_state: Dict[str, Any] = {}
        
    def register_node(self, node: DAGNode):
        self.nodes[node.name] = node
        self.edges[node.name] = []
        self.in_degree[node.name] = 0
        
    def add_edge(self, from_node: str, to_node: str):
        """外部声明图的拓扑形状，而不是硬编码在节点内部"""
        if from_node not in self.nodes or to_node not in self.nodes:
            raise ValueError("Nodes must be registered before adding edges.")
        self.edges[from_node].append(to_node)
        self.in_degree[to_node] += 1
        
    async def run(self, initial_state: Dict[str, Any] = None):
        if initial_state:
            self.global_state.update(initial_state)
            
        # 1. 找到所有 入度为 0 的节点 (没有前置依赖，可以立刻并发点火)
        ready_queue = deque([name for name, degree in self.in_degree.items() if degree == 0])
        execution_order = []
        
        print(f"[Engine] DAG Booting. Ready nodes: {list(ready_queue)}")
        
        while ready_queue:
            # 取出当前批次所有入度为 0 的节点
            current_tasks = list(ready_queue)
            ready_queue.clear()
            
            print(f"\n[Engine] ---> Concurrent Batch Firing: {current_tasks}")
            
            # 构造并发协程
            async def run_node(node_name):
                node = self.nodes[node_name]
                return node_name, await node.execute(self.global_state)
                
            # 2. 并发执行当前层级的所有节点！
            results = await asyncio.gather(*(run_node(name) for name in current_tasks))
            
            for node_name, result in results:
                execution_order.append(node_name)
                if result.payload:
                    self.global_state.update(result.payload)
                
                # 3. 任务完成后，像拆除炸弹一样，拆除它下游节点的阻塞 (入度减 1)
                for neighbor in self.edges[node_name]:
                    self.in_degree[neighbor] -= 1
                    if self.in_degree[neighbor] == 0:
                        ready_queue.append(neighbor)
                        
        # 4. 死锁检测
        if len(execution_order) != len(self.nodes):
            print("[Engine] Fatal: Cycle detected! Some nodes were never executed due to deadlock.")
            
        print("\n[Engine] DAG Execution Finished.")
        return self.global_state

# ==========================================
# 测试用例 / 感受并发之美
# ==========================================
if __name__ == "__main__":
    class FetchDataNode(DAGNode):
        async def execute(self, state):
            print("  [Fetch] 开始拉取全网数据...")
            await asyncio.sleep(0.5)
            return NodeResult(payload={"raw_data": "reddit, x, hn"})

    class AnalyzeRedditNode(DAGNode):
        async def execute(self, state):
            print("  [Reddit] 正在深度分析 Reddit 情绪 (需 2 秒)...")
            await asyncio.sleep(2) # 模拟长耗时
            return NodeResult(payload={"reddit_score": 90})

    class AnalyzeXNode(DAGNode):
        async def execute(self, state):
            print("  [X] 正在分析 X 情绪 (需 0.5 秒)...")
            await asyncio.sleep(0.5)
            return NodeResult(payload={"x_score": 85})

    class SynthesizeNode(DAGNode):
        async def execute(self, state):
            print(f"  [Synth] 最终聚合报告 - Reddit: {state.get('reddit_score')}, X: {state.get('x_score')}")
            return NodeResult()

    async def main():
        engine = DAGEngine()
        # 1. 注册纯粹的计算节点
        engine.register_node(FetchDataNode("Fetch"))
        engine.register_node(AnalyzeRedditNode("Reddit"))
        engine.register_node(AnalyzeXNode("X"))
        engine.register_node(SynthesizeNode("Synth"))
        
        # 2. 外部声名 DAG 拓扑 (Edges)
        # Fetch 执行完后，Reddit 和 X 可以 **同时并发** 执行！
        engine.add_edge("Fetch", "Reddit")
        engine.add_edge("Fetch", "X")
        # 只有当 Reddit 和 X 都执行完后 (入度全被拆除)，Synth 才能执行
        engine.add_edge("Reddit", "Synth")
        engine.add_edge("X", "Synth")
        
        await engine.run()

    asyncio.run(main())
