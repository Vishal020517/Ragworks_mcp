"""
MCP Client - HTTP client for FastMCP server
Uses the MCP JSON-RPC protocol over HTTP
"""
import requests
import json

MCP_URL = "http://127.0.0.1:8000/mcp"


def call_tool(tool_name: str, args: dict):
    """
    Call a tool via FastMCP HTTP API using MCP JSON-RPC protocol
    """
    
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": args
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        res = requests.post(MCP_URL, json=payload, headers=headers, timeout=30)
        
        if res.status_code == 200:
            data = res.json()
            
            # ✅ Success
            if "result" in data:
                return data["result"]
            
            # ❌ MCP error
            if "error" in data:
                return {"error": data["error"]}
            
            return {"error": "Unknown MCP response", "raw": data}
        else:
            return {"error": f"HTTP {res.status_code}: {res.text}"}
    
    except Exception as e:
        return {"error": str(e)}
