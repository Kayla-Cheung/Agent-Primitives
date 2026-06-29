import asyncio
import json
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar, Optional

# 使用泛型 T，代表任何继承自 BaseModel 的 Pydantic 契约
T = TypeVar('T', bound=BaseModel)

class AsyncLLMGateway:
    def __init__(self, max_concurrent_requests: int = 10, max_retries: int = 3):
        # 1. 物理滤纸：时间阀门 (Semaphore)
        # 无论多少个 Agent 同时发起请求，最多只有 10 个能进入网络层
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.max_retries = max_retries

    async def _mock_network_call_to_llm(self, prompt: str, is_retry: bool = False) -> str:
        """
        模拟一次极不稳定的底层大模型网络请求。
        """
        await asyncio.sleep(1) # 模拟网络延迟
        if not is_retry:
            # 第一次调用，大模型必定发神经，吐出破损的数据（或者少传必填字段）
            return '{"tool_name": "search", "hallucination": "我忘了写thought字段"}'
        else:
            # 第二次调用（被网关骂了之后），大模型老实了，吐出符合契约的干净数据
            return '{"thought": "发现之前的错误，现在重试", "tool_name": "search_web", "arguments": {}}'

    async def generate(self, prompt: str, contract: Type[T]) -> T:
        """
        核心网关出口：吃进 Prompt，吐出绝对符合 contract（Pydantic 契约）的晶体。
        """
        # 限制并发，排队进入
        async with self._semaphore:
            current_prompt = prompt
            
            # 双层自纠错回路 (The Self-Correction Loop)
            for attempt in range(self.max_retries):
                try:
                    print(f"🔄 [尝试 {attempt+1}/{self.max_retries}] 正在请求大模型...")
                    
                    # 1. 获取网络传输回来的死字符串 (JSON)
                    raw_json_string = await self._mock_network_call_to_llm(
                        current_prompt, 
                        is_retry=(attempt > 0)
                    )
                    
                    # 2. 转为内存中的字典
                    raw_dict = json.loads(raw_json_string)
                    
                    # 3. 结构滤纸打桩：尝试强转为 Pydantic 对象
                    # 如果这一步不抛出异常，说明数据纯净！
                    validated_object = contract(**raw_dict)
                    
                    print(f"✅ 提取成功！获得纯净对象。")
                    return validated_object
                    
                except json.JSONDecodeError:
                    error_msg = "你的输出连合法的 JSON 都不是，请重新输出标准 JSON。"
                    print(f"⚠️ [熔断] JSON格式彻底损坏。将原路打回...")
                    current_prompt += f"\n\nSystem Error: {error_msg}"
                    
                except ValidationError as e:
                    # 获取 Pydantic 极其精准的机器报错
                    error_msg = e.json()
                    print(f"⚠️ [熔断] 数据不符合契约！拦截到的错误：\n{error_msg}\n将原路打回...")
                    # 把报错塞进 Prompt 再次发送
                    current_prompt += f"\n\nSystem Error: 你的输出不符合 Pydantic Schema，报错如下。请修正：\n{error_msg}"

            raise Exception(f"❌ 大模型简直不可理喻，重试 {self.max_retries} 次后仍然无法符合契约。系统抛弃该请求。")

# --- 运行测试 ---
# 定义一份契约
class MockAgentResponse(BaseModel):
    thought: str
    tool_name: str

async def main():
    gateway = AsyncLLMGateway(max_concurrent_requests=5)
    
    # 向网关发起请求。我们要求它最后必须返还给我们一个 MockAgentResponse 对象。
    result = await gateway.generate("请输出当前天气", contract=MockAgentResponse)
    
    print("\n--- 最终 SINA 引擎收到的数据 (内存对象) ---")
    print("Type:", type(result))
    print("Content:", result)

if __name__ == "__main__":
    asyncio.run(main())
