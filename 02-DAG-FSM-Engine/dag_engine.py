import asyncio
from typing import Dict, Any, Callable, Awaitable, List, Optional
from dataclasses import dataclass, field

@dataclass
class NodeResult:
    """节点执行结果"""
    next_node: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None

class DAGNode:
    """DAG/FSM 独立执行节点，物理隔离状态逻辑"""
    def __init__(self, name: str):
        self.name = name

    async def execute(self, state: Dict[str, Any]) -> NodeResult:
        raise NotImplementedError("Subclasses must implement execute()")

class DAGEngine:
    """
    DAG 状态机引擎 (Orchestrator)
    替代掉传统 while True，接管所有的流转控制权
    """
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        self.global_state: Dict[str, Any] = {}
        
    def register_node(self, node: DAGNode):
        self.nodes[node.name] = node
        
    async def run(self, start_node: str, initial_state: Dict[str, Any] = None):
        if initial_state:
            self.global_state.update(initial_state)
            
        current_node_name = start_node
        
        # 虽然底层还是循环，但控制权已经被抽象，节点内部不再包含路由逻辑
        while current_node_name:
            if current_node_name not in self.nodes:
                raise ValueError(f"Fatal: Node '{current_node_name}' not found in DAG.")
                
            node = self.nodes[current_node_name]
            print(f"[Engine] -> Entering Node: {current_node_name}")
            
            try:
                # 触发原子节点的执行
                result = await node.execute(self.global_state)
                
                # 状态同步
                if result.payload:
                    self.global_state.update(result.payload)
                    
                # 状态流转决定
                current_node_name = result.next_node
                
            except Exception as e:
                print(f"[Engine] Fatal Error in {current_node_name}: {e}")
                # 可以在这里做全局熔断或错误隔离
                break
                
        print("[Engine] Execution Finished. DAG reached a terminal state.")
        return self.global_state

# ==========================================
# 测试用例 / MVP 演示
# ==========================================
if __name__ == "__main__":
    class PerceptionNode(DAGNode):
        async def execute(self, state):
            print("  [Perception] 读取传感器数据...")
            await asyncio.sleep(0.5)
            return NodeResult(next_node="Decision", payload={"sensor_data": "Enemy detected"})

    class DecisionNode(DAGNode):
        async def execute(self, state):
            sensor = state.get("sensor_data")
            print(f"  [Decision] 分析数据: {sensor}")
            await asyncio.sleep(0.5)
            if "Enemy" in sensor:
                return NodeResult(next_node="Action")
            return NodeResult(next_node=None)

    class ActionNode(DAGNode):
        async def execute(self, state):
            print("  [Action] 执行攻击动作！")
            await asyncio.sleep(0.5)
            return NodeResult(next_node=None) # None 代表结束，跳出状态机

    async def main():
        engine = DAGEngine()
        engine.register_node(PerceptionNode("Perception"))
        engine.register_node(DecisionNode("Decision"))
        engine.register_node(ActionNode("Action"))
        
        await engine.run("Perception")

    asyncio.run(main())
