from agents.market_agent import MarketAgent
from agents.technical_agent import TechnicalAgent
from agents.news_agent import NewsAgent
from agents.fundamental_agent import FundamentalAgent
from agents.risk_agent import RiskAgent


def run_all_agents(symbol: str, query: str):
    print("\n================ TESTING AGENTS ================\n")

    # Initialize agents
    market_agent = MarketAgent()
    technical_agent = TechnicalAgent()
    news_agent = NewsAgent()
    fundamental_agent = FundamentalAgent()
    risk_agent = RiskAgent()

    # ------------------ MARKET ------------------
    print("\n🔵 Running Market Agent...")
    market_output = market_agent.run(symbol)
    print(market_output)

    # ------------------ TECHNICAL ------------------
    print("\n🟡 Running Technical Agent...")
    technical_output = technical_agent.run(symbol)
    print(technical_output)

    # ------------------ NEWS ------------------
    print("\n🟢 Running News Agent...")
    news_output = news_agent.run(symbol)
    print(news_output)

    # ------------------ FUNDAMENTAL ------------------
    print("\n🟣 Running Fundamental Agent...")
    fundamental_output = fundamental_agent.run(query)
    print(fundamental_output)

    # ------------------ RISK ------------------
    print("\n🔴 Running Risk Agent...")
    risk_output = risk_agent.run(
        technical_output["analysis"],
        news_output["analysis"]
    )
    print(risk_output)

    print("\n================ ALL AGENTS COMPLETED ================\n")


if __name__ == "__main__":
    symbol = "AAPL"
    query = "Analyze Apple stock fundamentals and investment potential"

    run_all_agents(symbol, query)