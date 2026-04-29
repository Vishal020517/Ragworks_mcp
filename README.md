# Financial AI Agent

A multi-agent AI system that fetches real-time stock data, performs technical and fundamental analysis, retrieves financial news, and delivers structured investment recommendations with guardrails protecting every layer of the pipeline.

---

## What This Project Does

A user asks a question like *"Should I buy Apple stock?"* and the system:

1. Validates the query is finance-related (input guardrail)
2. Routes it to a tool-calling agent
3. The agent calls specialized sub-agents — market, technical, news, fundamental, and RAG — each guarded at the tool level
4. Combines all data into a structured analysis
5. Validates the final response before returning it to the user (output guardrail)

---

## Project Structure

```
backend/
├── agents/              # Sub-agents and tool wrappers
├── api/                 # FastAPI server (replaced FastMCP)
├── graph/               # LangGraph state machine
├── guardrails/          # Input, tool, and output guardrails
├── mcp_server/          # FastMCP server (attempted, not in active use)
├── rag/                 # RAG pipeline — ingestion, indexing, retrieval
├── utils/               # Symbol extractor utility
├── api_client.py        # HTTP client for FastAPI server
├── mcp_client.py        # HTTP client for FastMCP (kept for reference)
└── requirements.txt
```

---

## Agent Execution Approaches

This project implements **two distinct agent patterns**, both enabling automatic tool calling. They were built and used at different stages of development.

### ReAct Agent (`agents/risk_agent.py`)

The ReAct (Reasoning + Acting) pattern was the first approach implemented. Built with LangChain's `create_react_agent`, it follows an explicit Thought/Action/Observation loop:

```
Question: Should I buy Tesla?
Thought: I need to check the stock price first
Action: MarketAgent
Action Input: TSLA
Observation: { "price": 245.3, "analysis": "..." }
Thought: Now I need RSI data
Action: TechnicalAgent
...
Final Answer: Based on all data...
```

The agent decides at each step which tool to call next, calls it automatically, observes the result, and continues reasoning until it has enough information to answer. No manual orchestration is needed — the LLM drives the entire tool-calling sequence.

### Tool-Calling Agent (`agents/tool_agent.py`) — Active

The tool-calling agent pattern replaced ReAct as the primary orchestrator. Built with `create_tool_calling_agent`, it uses the LLM's native function-calling capability (structured tool schemas) rather than parsing free-text Thought/Action blocks. The LLM receives all tool definitions upfront and decides which tools to call, in what order, and with what inputs — all automatically. This is more reliable than ReAct because tool inputs are structured JSON rather than free text, which eliminates parsing errors.

### LangGraph (`graph/`)

LangGraph wraps the tool-calling agent inside a stateful graph. The graph manages the shared `GraphState` — carrying the query, symbol, and all intermediate results — and routes execution through nodes. Even with a single active node today, the graph structure makes it straightforward to add parallel data-fetching nodes, conditional routing, or retry logic without rewriting the agent itself.

**Both the ReAct agent and the graph-based tool-calling agent enable fully automatic tool invocation** — the LLM decides which tools to use and when, without any hardcoded routing logic.

---

## Technology Choices

### Why LangChain + LangGraph

LangChain provides the agent framework — tool calling, prompt templates, and agent executors. LangGraph sits on top of it to model the pipeline as a stateful graph, where each node represents a processing step. This makes the flow explicit, debuggable, and easy to extend with new nodes without touching existing logic.

### Why Groq

Groq provides extremely fast LLM inference. Since this system makes multiple LLM calls per query (one per sub-agent plus the orchestrator), latency compounds quickly. Groq's hardware-accelerated inference keeps the total response time acceptable. The models used are `openai/gpt-oss-120b` for the orchestrator and guardrails, and `openai/gpt-oss-20b` for the lighter sub-agents.

### Why FastAPI (and why we moved away from FastMCP)

The original design used **FastMCP** to expose tools over the MCP JSON-RPC protocol. FastMCP was set up in `mcp_server/server.py` with tools registered via `mcp_server/registry.py`, and a corresponding `mcp_client.py` was written to call them over HTTP using the `tools/call` JSON-RPC method.

**The problem:** FastMCP's HTTP transport had inconsistent behavior — tool calls would time out, return malformed responses, or fail silently depending on how the server was started. The JSON-RPC envelope added complexity without benefit for an internal service. Debugging was difficult because errors were swallowed inside the protocol layer.

**The switch:** We replaced FastMCP with a plain **FastAPI** server (`api/server.py`). Each tool is a direct POST endpoint under `/tool`, with a simple `{"tool": "...", "input": {...}}` request body. The `api_client.py` calls this server. This is simpler, fully transparent, and easier to debug. The FastMCP code is preserved in `mcp_server/` for reference.

### Why LlamaIndex for RAG

LlamaIndex handles the full RAG lifecycle — document loading, chunking, vector indexing, and retrieval. It integrates cleanly with HuggingFace embedding models, allowing the index to be built and queried entirely locally without any external embedding API calls.

### Why yfinance

yfinance provides free, reliable access to Yahoo Finance data — stock prices, historical OHLCV data, and company fundamentals — with no API key required. It is the standard choice for financial data in Python projects at this scale.

---

## Agents

### MarketAgent (`agents/market_agent.py`)

Fetches the latest stock price using `get_stock_price` and passes it to an LLM for a short market condition analysis. Answers questions like whether the current price is high or low relative to recent history.

### TechnicalAgent (`agents/technical_agent.py`)

Fetches the RSI (Relative Strength Index) for a stock using `calculate_rsi` and asks the LLM to interpret it. RSI above 70 signals overbought conditions; below 30 signals oversold. This gives a momentum-based trading signal.

### NewsAgent (`agents/news_agent.py`)

Fetches the five most recent news articles for a stock symbol using the NewsAPI. The LLM summarizes the key themes, identifies overall sentiment (positive, negative, or neutral), and flags any risks or opportunities mentioned in the headlines.

### FundamentalAgent (`agents/fundamental_agent.py`)

Fetches company fundamentals directly from Yahoo Finance via yfinance — market cap, P/E ratio, EPS, revenue, profit margin, and sector. Unlike the other agents, this one does not call an LLM; it formats the data into a structured analysis with interpretation rules (e.g., profit margin above 15% indicates strong profitability). It also includes a dynamic symbol resolver that converts natural language company names into valid ticker symbols using the Yahoo Finance search API.

### RiskAgent (`agents/risk_agent.py`)

The first orchestrator implementation, built with `create_react_agent`. Uses the ReAct pattern — Thought/Action/Observation loop — to automatically decide which tools to call and in what order. It has access to the same five tools as the main agent. This was the original approach before the tool-calling agent pattern was adopted. Kept in the codebase as a working reference for the ReAct execution style. See the [Agent Execution Approaches](#agent-execution-approaches) section for a detailed comparison.

### ToolAgent — Main Orchestrator (`agents/tool_agent.py`)

The active orchestrator. Built with `create_tool_calling_agent`, it uses the LLM's native function-calling capability to automatically select and invoke tools. It has access to all five tools (MarketAgent, TechnicalAgent, NewsAgent, FundamentalAgent, RAGTool) and is instructed to always use tools before forming a recommendation. Produces a structured output with a Summary, a Recommendation (BUY / HOLD / SELL), and Reasoning. See the [Agent Execution Approaches](#agent-execution-approaches) section for how this differs from the ReAct agent.

---

## Tools

All tools are defined as `StructuredTool` instances in `agents/tool_wrapper.py` and are passed to the agent executor. Each tool wraps a sub-agent or API call and enforces the tool guardrail before execution.

| Tool | Input | What It Does |
|---|---|---|
| `MarketAgent` | stock symbol | Returns price and market condition analysis |
| `TechnicalAgent` | stock symbol | Returns RSI value and momentum interpretation |
| `NewsAgent` | stock symbol | Returns news summary and sentiment |
| `FundamentalAgent` | stock symbol | Returns P/E, EPS, revenue, margin, sector |
| `RAGTool` | natural language query | Retrieves relevant financial knowledge from the local vector index |

---

## MCP Server Tools (FastMCP layer — preserved, not active)

These are the tool implementations that were originally registered with FastMCP. They are still used directly by the FastAPI server and the sub-agents.

| Function | File | What It Does |
|---|---|---|
| `get_stock_price(symbol)` | `mcp_server/tools/stock_tools.py` | Fetches latest closing price via yfinance |
| `calculate_rsi(symbol)` | `mcp_server/tools/financial_tools.py` | Computes 14-period RSI from 1-month historical data |
| `get_stock_news(query)` | `mcp_server/tools/news_tools.py` | Fetches 5 articles from NewsAPI |
| `get_fundamentals(symbol)` | `mcp_server/tools/fundamental_tools.py` | Fetches company info from Yahoo Finance |
| `retrieve_knowledge(query)` | `mcp_server/tools/rag_tool.py` | Queries the local LlamaIndex vector store |

---

## RAG Pipeline

The RAG (Retrieval-Augmented Generation) system provides the agent with deep background knowledge on financial concepts that live data sources cannot answer — things like how RSI works, what MACD signals mean, or how to interpret P/E ratios.

### Scraper (`rag/ingestion/scraper.py`)

Scrapes Wikipedia articles for four financial topics: RSI, MACD, P/E ratio, and fundamental analysis. Uses BeautifulSoup to extract clean paragraph text and saves each article as a `.txt` file under `rag/data/raw/articles/`.

### Ingestion Pipeline (`rag/ingestion/pipeline.py`)

Loads the scraped text files, splits them into 300-token chunks with 50-token overlap using LlamaIndex's `SimpleNodeParser`, builds a `VectorStoreIndex` using the `sentence-transformers/all-MiniLM-L6-v2` embedding model (runs locally, no API key needed), and persists the index to `rag/index/`.

### Retriever (`rag/retriever/retriever.py`)

Loads the persisted index from disk at startup and exposes a `query(text)` method. Retrieves the top 3 most semantically similar chunks for any query. Does not call an LLM — returns raw text chunks that the agent can reason over.

---

## Graph (`graph/`)

The LangGraph state machine defines the execution flow.

### State (`graph/state.py`)

A `TypedDict` that carries all data through the graph:

```python
class GraphState(TypedDict):
    query: str
    symbol: str
    market: Optional[dict]
    technical: Optional[dict]
    news: Optional[dict]
    fundamental: Optional[dict]
    rag: Optional[str]
    final: Optional[str]
```

### Agent Node (`graph/agent_node.py`)

The single active node in the graph. It runs the full guardrail pipeline:

1. Calls the input guardrail to validate the query
2. Runs the tool-calling agent
3. Calls the output guardrail to validate the response

### Main Graph (`graph/main_graph.py`)

Builds and compiles the LangGraph with a single `agent` node as both the entry point and terminal node.

### Nodes (`graph/nodes.py`)

Individual node functions for market, technical, news, fundamental, and RAG steps. These were part of an earlier multi-node graph design and are kept for reference. The current active graph uses the single `agent_node` instead.

---

## Guardrails

Three guardrails protect the pipeline at different layers.

### Input Guardrail (`guardrails/input_guard.py`)

Runs before the agent processes anything. Uses an LLM to classify the user's query as `SAFE` (finance-related) or `UNSAFE` (off-topic, harmful, or unrelated). If the query is unsafe, it is rejected immediately with an explanation and the agent never runs.

**Why LLM-based:** Rule-based keyword filtering is easy to bypass and produces false positives. An LLM classifier understands context — "What is the best drug stock?" is safe; "How do I make drugs?" is not.

### Tool Guardrail (`guardrails/tool_guard.py`)

Runs inside each tool function before any external call is made. Performs four checks:

- **Allowlist check:** The tool name must be one of the five registered tools.
- **Input length check:** No input field may exceed 300 characters.
- **Injection pattern check:** Inputs are scanned for SQL injection, JavaScript injection, and Python code execution patterns.
- **Symbol format check:** If the input contains a `symbol` field, it must match the pattern `^[A-Z]{1,5}$`.

This guardrail is purely rule-based — fast, deterministic, and zero-cost.

### Output Guardrail (`guardrails/output_guard.py`)

Runs after the agent produces its final response. First checks that the response is non-empty and at least 20 characters. Then uses an LLM to classify the response as `VALID` (contains a financial summary, recommendation, and reasoning) or `INVALID` (off-topic, hallucinated, or missing required structure). Invalid responses are blocked and replaced with an error message.

### Guardrail Flow

```
User Query
    |
[Input Guardrail]   — LLM classifies query as SAFE / UNSAFE
    |
[Agent Executor]    — Tool-calling agent runs
    |
[Tool Guardrail]    — Validates each tool call before execution (allowlist, length, injection, symbol format)
    |
[Output Guardrail]  — LLM validates final response as VALID / INVALID
    |
User Response
```

---

## FastAPI Server (`api/server.py`)

Exposes a single `/tool` POST endpoint. The request body specifies the tool name and its input parameters. The server dispatches to the appropriate tool function and returns the result. This replaced the FastMCP server as the active tool-serving layer.

```
POST /tool
{
  "tool": "get_stock_price",
  "input": { "symbol": "AAPL" }
}
```

---

## FastMCP Attempt (`mcp_server/`)

FastMCP was the original approach for exposing tools. The server (`mcp_server/server.py`) used `FastMCP` from the `fastmcp` package and registered tools via `mcp_server/registry.py`. A dedicated client (`mcp_client.py`) was written to call tools using the MCP JSON-RPC protocol over HTTP.

This approach was abandoned due to reliability issues with the HTTP transport — inconsistent responses, silent failures, and difficult debugging. The code is preserved in the repository as a record of the attempt. The `fastmcp` package remains in `requirements.txt`.

---

## Memory System (`memory/`)

The memory system gives every user a persistent conversation history that survives across sessions. When the agent answers a question, the exchange is saved to disk and injected into the LLM's system prompt on the next query, so the agent can refer back to what was discussed before.

### How It Works

Sessions are stored as JSON files at `memory/sessions/<username>.json`. Each file is a list of user/assistant turns with timestamps. There are no external databases or services required.

```json
[
  { "role": "user",      "content": "Should I buy AAPL?", "timestamp": "2026-04-29T10:00:00" },
  { "role": "assistant", "content": "Summary: ...\nRecommendation: BUY\n...", "timestamp": "2026-04-29T10:00:05" }
]
```

### Key Functions (`memory/memory_store.py`)

`load_history(username)` — reads the session file for a user and returns the full history list. Returns an empty list for new users.

`save_turn(username, query, response)` — appends a user/assistant pair to the session file after every successful agent response.

`format_history_for_prompt(history, max_turns=6)` — formats the last 6 conversation turns into a plain-text block that is injected into the agent's system prompt. Keeping it to 6 turns avoids bloating the context window.

`clear_history(username)` — deletes the session file. Exposed as the `clear memory` command in the CLI.

### Session Isolation

Each username gets its own file. Two users running the agent simultaneously have completely separate histories and never see each other's data.

### CLI Behaviour

When the CLI starts, it asks for a username:

```
Enter your username to start (or press Enter for 'guest'):
```

Returning users see how many previous conversations are on record. New users get a fresh session. During a session, typing `clear memory` wipes the history for that user.

---

## How to Run the Project

### 1. Install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set environment variables

Create a `.env` file inside `backend/` or export these in your shell:

```bash
export GROQ_API_KEY=your_groq_api_key_here
export LANGCHAIN_API_KEY=your_langsmith_key_here   # optional
export LANGCHAIN_PROJECT=financial-agent            # optional
```

### 3. Build the RAG index (run once)

This scrapes Wikipedia articles and builds the local vector index. Only needs to be run once, or again if you want to refresh the knowledge base.

```bash
python -m rag.ingestion.scraper
python -m rag.ingestion.pipeline
```

### 4. Start the FastAPI tool server

Open a terminal and keep this running in the background. The agent calls this server to execute tools.

```bash
uvicorn api.server:app --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 5. Start the CLI agent

Open a second terminal and run:

```bash
python graph/test_run_graph.py
```

You will be prompted for a username, then you can start asking questions:

```
Financial AI Agent
============================================================
Enter your username to start (or press Enter for 'guest'): john

Welcome, john. Starting a new session.

Type 'exit' to quit | 'clear memory' to reset your history
============================================================

[john] Ask: Should I buy Apple stock?
```

### Available CLI commands

| Command | What it does |
|---|---|
| Any financial question | Runs the full agent pipeline |
| `clear memory` | Deletes your conversation history |
| `exit` or `quit` | Exits the CLI |

---

## Unit Tests

Tests are in `backend/tests/test_suite.py` and cover all rule-based and I/O components without making real network or LLM calls. LLM-dependent guardrails (input and output guards) are excluded from unit tests since they require a live Groq API key and are better validated through integration testing.

### What is tested

| Test Class | What it covers |
|---|---|
| `TestToolGuard` | Allowlist, symbol format, input length, injection patterns (17 tests) |
| `TestMemoryStore` | Save/load/clear history, formatting, session isolation, timestamps (10 tests) |
| `TestStockTools` | Price fetch success, empty data, exceptions, symbol casing (4 tests) |
| `TestFinancialTools` | RSI calculation, empty data, exceptions, symbol casing (4 tests) |
| `TestFundamentalTools` | Fundamentals fetch success, empty info, exceptions (3 tests) |
| `TestNewsTools` | News fetch success, empty articles, network exceptions (3 tests) |
| `TestApiClient` | Successful call, error response, network exception (3 tests) |
| `TestGraphState` | TypedDict structure with all fields including username and history (2 tests) |

**Total: 46 tests**

### Running the tests

Make sure the virtual environment is active and you are inside the `backend/` directory:

```bash
python -m pytest tests/test_suite.py -v
```

Run a specific test class:

```bash
python -m pytest tests/test_suite.py::TestToolGuard -v
```

Run a specific test:

```bash
python -m pytest tests/test_suite.py::TestMemoryStore::test_save_and_load_turn -v
```

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Required for all LLM calls via LangChain-Groq |
| `LANGCHAIN_API_KEY` | Optional — enables LangSmith tracing |
| `LANGCHAIN_PROJECT` | Optional — LangSmith project name |

---

## Dependencies

| Package | Purpose |
|---|---|
| `langchain`, `langchain-groq` | Agent framework and Groq LLM integration |
| `langgraph` | State machine for the agent pipeline |
| `fastapi`, `uvicorn` | Tool-serving HTTP API |
| `fastmcp` | FastMCP server (attempted, preserved) |
| `yfinance` | Stock price and fundamental data |
| `llama-index` | RAG pipeline — indexing and retrieval |
| `llama-index-embeddings-huggingface` | Local embedding model for RAG |
| `sentence-transformers` | Underlying model for embeddings |
| `requests`, `beautifulsoup4` | Web scraping for RAG data |
| `pandas` | RSI calculation |
| `langsmith` | LLM call tracing and observability |
| `pytest` | Unit testing |
