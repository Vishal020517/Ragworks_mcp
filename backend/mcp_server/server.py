from fastmcp import FastMCP
from mcp_server.registry import register_tools

mcp = FastMCP("financial-agent")

register_tools(mcp)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )