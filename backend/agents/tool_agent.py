from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from agents.tool_wrapper import tools
from config import get_llm


llm = get_llm(model_name="openai/gpt-oss-120b")

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a professional financial AI agent.

STRICT RULES:
- Always use tools before giving a recommendation
- Never guess values
- Combine multiple tools
- If data is missing, say "insufficient data"

{history}

Final output format:

Summary:
...

Recommendation: BUY / HOLD / SELL

Reasoning:
...
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10
)


def run_agent(query: str, history: str = "") -> str:
    result = agent_executor.invoke({
        "input": query,
        "history": f"Conversation so far:\n{history}" if history and history != "No previous conversation." else ""
    })
    return result["output"]
