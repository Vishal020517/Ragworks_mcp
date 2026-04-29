from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

from agents.tool_wrapper import tools
from config import get_llm


llm = get_llm(model_name="llama3-70b-8192")

template = """
You are an advanced financial AI agent.

You have access to the following tools:
{tools}

Follow this format:

Question: {input}
Thought: think step-by-step
Action: one of [{tool_names}]
Action Input: input for the tool
Observation: result of the tool
... (repeat Thought/Action/Observation)
Thought: I now know the final answer
Final Answer: answer to the user

Begin!

Question: {input}
{agent_scratchpad}
"""

prompt = PromptTemplate.from_template(template)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def run():
    while True:
        query = input("Ask: ")
        if query.lower() in ["exit", "quit"]:
            break
        result = agent_executor.invoke({"input": query})
        print("\nFINAL ANSWER:\n")
        print(result["output"])


if __name__ == "__main__":
    run()
