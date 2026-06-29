from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Literal
import json

# ---------------------------------------------------------
# 1. 定义数据契约 (Data Contracts)
# 这些类就是你的“钢铁地基”。任何流经系统的 JSON 必须符合这些形状。
# ---------------------------------------------------------

class ToolCall(BaseModel):
    # Literal 强制规定只允许特定的值
    tool_name: Literal["search_web", "write_file", "execute_python"] = Field(
        ..., description="工具名称，必须是给定的三个之一"
    )
    # 字典格式的参数，可以进一步嵌套 Pydantic Model，这里为了演示保持简单
    arguments: dict = Field(..., description="调用工具的具体参数")

class AgentResponse(BaseModel):
    thought: str = Field(..., description="Agent 的内部推理过程")
    # Optional 代表这个字段可以没有（即返回 null）
    tool_calls: Optional[List[ToolCall]] = Field(default=[], description="需要调用的工具列表")
    final_answer: Optional[str] = Field(default=None, description="最终给用户的回复")

# ---------------------------------------------------------
# 2. 模拟 LLM 吐出的脏数据 (Stochastic Data)
# ---------------------------------------------------------

llm_dirty_json = """
{
    "thought": "我需要搜索一下明天天气，然后写到文件里",
    "tool_calls": [
        {
            "tool_name": "search_google", 
            "arguments": {"query": "weather tomorrow"}
        }
    ],
    "hallucinated_key": "这一行是模型发神经多加的"
}
"""

# ---------------------------------------------------------
# 3. 契约校验与防线拦截 (The Defense Line)
# ---------------------------------------------------------

def parse_llm_output(raw_json_str: str):
    try:
        # LLM 输出的字符串先转为 Python 字典
        raw_dict = json.loads(raw_json_str)
        
        # 绞肉机启动：强行灌入 AgentResponse 契约
        # Pydantic 默认会忽略掉多余的幻觉字段 (hallucinated_key)
        validated_data = AgentResponse(**raw_dict)
        print("✅ 校验通过！提取的数据：")
        print(validated_data.model_dump_json(indent=2))
        
    except ValidationError as e:
        # 拦截：如果 LLM 输出不符合契约（比如 tool_name 名字瞎造）
        print("❌ 契约熔断！拦截到不合法的数据结构。")
        print("将把以下错误信息喂回给 LLM 触发自纠错回路：")
        print(e.json())

if __name__ == "__main__":
    parse_llm_output(llm_dirty_json)
