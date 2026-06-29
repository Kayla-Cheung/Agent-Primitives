# AsyncLLMGateway: The Semi-Permeable Membrane of Agentic Systems

> *"Order is not found in the chaotic output of stochastic models; it must be enforced at the physical boundary."*

## The Philosophy
In multi-agent sociologically simulated systems, the LLM is an inherently stochastic engine. It hallucinates keys, breaks schema structures, and causes systemic collapse when generating logic for simulated societies. 

**AsyncLLMGateway** is a structural defense line. It is not an LLM framework (like LangChain); it is a raw, physical "semi-permeable membrane" built for high-concurrency systems.

It enforces two absolute laws:
1. **Temporal Order (via `asyncio`)**: Controls the concurrency funnel to prevent API rate-limit stamping (HTTP 429) when hundreds of agents act simultaneously.
2. **Spatial Structure (via `pydantic`)**: Acts as an "Iron Contract". If the LLM generates a JSON that violates the structural blueprint, the gateway intercepts the `ValidationError` and forces the LLM into a closed self-correction loop. 

Only pure, structurally deterministic Python objects are permitted to enter the core execution engine.

## Usage
Provide any Pydantic schema to the gateway. The gateway will compile it into JSON Schema, prompt the LLM, and return a guaranteed valid instance.

```python
from gateway import AsyncLLMGateway
from pydantic import BaseModel

class ActionIntent(BaseModel):
    internal_thought: str
    observable_action: str

# The system will never crash from malformed JSON.
# It will self-correct until the contract is fulfilled.
gateway = AsyncLLMGateway(max_concurrent_requests=10)
intent = await gateway.generate(prompt="Observe the room.", contract=ActionIntent)
```

## Architecture
- **Time/Flow Control**: `asyncio.Semaphore`
- **Data Contract**: `Pydantic` (`BaseModel`)
- **Self-Correction Circuit**: Native `ValidationError` feedback loop.
