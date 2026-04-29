import requests

BASE_URL = "http://127.0.0.1:8000"


def call_tool(tool_name: str, payload: dict):
    try:
        res = requests.post(
            f"{BASE_URL}/tool",
            json={
                "tool": tool_name,
                "input": payload
            },
            timeout=10
        )

        data = res.json()

        if "error" in data:
            print(f"[API ERROR] {tool_name} → {data}", flush=True)

        return data

    except Exception as e:
        return {"error": str(e)}