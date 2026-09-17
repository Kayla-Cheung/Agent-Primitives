# Agent-Primitives ⚡

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pydantic V2](https://img.shields.io/badge/Contracts-Pydantic%20v2-E92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Concurrency: AsyncIO](https://img.shields.io/badge/Concurrency-AsyncIO-success.svg)](https://docs.python.org/3/library/asyncio.html)
[![Architecture: Zero-Black-Box](https://img.shields.io/badge/Architecture-Zero--Black--Box-orange.svg)](https://github.com/Kayla-Cheung/Agent-Primitives)

> **"Stop building fragile, sprawling framework spaghetti. Build agentic systems with raw physics and deterministic control flow."**  
> Agent-Primitives is a suite of irreducible, low-level architectural building blocks for high-concurrency production AI agents. Zero black-box magic, zero hidden prompts, pure deterministic mechanics.

---

## 🏛️ The Philosophy: Boundary Enforcement

Stochastic Large Language Models are entropy generators. When hundreds of autonomous agents interact simultaneously, naive prompt loops collapse into:
1. **Temporal Chaos**: Uncontrolled API bursts resulting in HTTP 429 rate-limit stampedes.
2. **Schema Rot**: Hallucinated JSON keys, missing fields, and silent payload corruption.
3. **State Mud**: Sprawling `while True` loops with tangled `if/else` routing flags that cannot be serialized, paused, or audited.

**Agent-Primitives eradicates these failure modes at the physical boundary.**

```
[ Stochastic LLM Output ] ──> 🛡️ 01. Semi-Permeable Membrane ──> ⚙️ 02. Kahn's DAG Orchestrator ──> ✅ Deterministic Execution
```

---

## 🔮 The Grimoire (Primitve Tech Tree)

### [01-Async-LLM-Gateway](./01-Async-LLM-Gateway/) — The Semi-Permeable Membrane
A high-throughput, self-healing gateway that acts as a physical boundary between stochastic LLM completions and your core execution engine.

* **Temporal Order**: `asyncio.Semaphore` concurrency funnel prevents rate-limit stamping across swarm agents.
* **Spatial Structure (Pydantic V2 Iron Contract)**: Compiles data schemas directly into the prompt contract.
* **Closed-Loop Self-Correction**: Intercepts raw JSON syntax errors and `ValidationError`, feeding stack traces back into a localized repair loop before returning to caller.

```python
from gateway import AsyncLLMGateway
from pydantic import BaseModel, Field

class ActionIntent(BaseModel):
    internal_thought: str = Field(..., description="CoT reasoning trace")
    observable_action: str = Field(..., description="Action token to execute")

gateway = AsyncLLMGateway()

# Guaranteed to return a valid instance of ActionIntent or raise cleanly after max retries.
# Never crashes from malformed JSON formatting.
intent = await gateway.generate_structured(
    system_prompt="You are an autonomous explorer.",
    user_prompt="Observe the control room.",
    response_model=ActionIntent
)
```

---

### [02-DAG-FSM-Engine](./02-DAG-FSM-Engine/) — The Deterministic Orchestrator
A high-performance state machine and Directed Acyclic Graph (DAG) executor based on **Kahn's Topological Sorting Algorithm**.

* **Topological Concurrency**: Automatically computes independent node batches and executes them concurrently using `asyncio.gather`.
* **Complete State Isolation**: Nodes (`DAGNode`) have zero knowledge of external topology. Routing is strictly managed by `DAGEngine`.
* **Cycle & Deadlock Detection**: Dynamically validates dependency graphs before and during runtime.
* **Snapshot Ready**: State transitions occur at explicit node boundaries, providing clean checkpoints for time-travel debugging.

```python
import asyncio
from dag_engine import DAGEngine, DAGNode, NodeResult

class FetchNode(DAGNode):
    async def execute(self, state):
        return NodeResult(payload={"raw_stream": "events"})

class AnalyzeRedditNode(DAGNode):
    async def execute(self, state):
        return NodeResult(payload={"reddit_score": 90})

class AnalyzeXNode(DAGNode):
    async def execute(self, state):
        return NodeResult(payload={"x_score": 85})

class SynthesizeNode(DAGNode):
    async def execute(self, state):
        print(f"Aggregated: {state['reddit_score']} vs {state['x_score']}")
        return NodeResult()

# 1. Register atomic operators
engine = DAGEngine()
engine.register_node(FetchNode("Fetch"))
engine.register_node(AnalyzeRedditNode("Reddit"))
engine.register_node(AnalyzeXNode("X"))
engine.register_node(SynthesizeNode("Synth"))

# 2. Declare external topology
# Reddit and X run concurrently in parallel once Fetch completes!
engine.add_edge("Fetch", "Reddit")
engine.add_edge("Fetch", "X")
engine.add_edge("Reddit", "Synth")
engine.add_edge("X", "Synth")

# 3. Fire deterministic execution pipeline
await engine.run()
```

---

## 📦 Directory Structure

```text
Agent-Primitives/
├── 01-Async-LLM-Gateway/
│   ├── gateway.py                 # Core gateway with native DeepSeek/OpenAI async pooling
│   ├── pydantic_iron_contract.py  # Self-correcting schema validator
│   └── README.md                  # Deep architectural specifications
│
├── 02-DAG-FSM-Engine/
│   ├── dag_engine.py              # Kahn's algorithm async concurrent DAG executor
│   └── README.md                  # State-machine decoupling manifesto
│
└── README.md                      # High-level primitives documentation
```

---

## 🚀 Quickstart

Clone the repository and explore the standalone primitives:

```bash
git clone https://github.com/Kayla-Cheung/Agent-Primitives.git
cd Agent-Primitives

# Run Primitive 02 DAG concurrency engine test
python 02-DAG-FSM-Engine/dag_engine.py
```

---

## 📄 License

MIT License. Designed to be copy-pasted and adapted directly into production agent pipelines.
