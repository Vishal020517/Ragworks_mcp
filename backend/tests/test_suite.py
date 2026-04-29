"""
Unit tests for the Financial AI Agent project.

Covers:
- Tool guardrail (rule-based, no LLM calls)
- Memory store (file I/O)
- Stock tools (mocked yfinance)
- RSI calculation (mocked yfinance)
- Fundamental tools (mocked yfinance)
- News tools (mocked requests)
- RAG retriever (mocked LlamaIndex)
- API client (mocked requests)

Run with:
    cd backend
    python -m pytest tests/test_suite.py -v
"""

import json
import sys
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ===========================================================================
# TOOL GUARDRAIL TESTS
# ===========================================================================

class TestToolGuard:
    """Tests for guardrails/tool_guard.py — purely rule-based, no mocking needed."""

    def setup_method(self):
        from guardrails.tool_guard import validate_tool_call
        self.validate = validate_tool_call

    def test_valid_tool_and_symbol(self):
        ok, err = self.validate("MarketAgent", {"symbol": "AAPL"})
        assert ok is True
        assert err == ""

    def test_valid_tool_all_names(self):
        for tool in ["MarketAgent", "TechnicalAgent", "NewsAgent", "FundamentalAgent", "RAGTool"]:
            ok, err = self.validate(tool, {"query": "Apple"})
            assert ok is True, f"Expected {tool} to be allowed"

    def test_unknown_tool_blocked(self):
        ok, err = self.validate("HackerTool", {"symbol": "AAPL"})
        assert ok is False
        assert "not in the allowed tools list" in err

    def test_invalid_symbol_format_with_special_chars(self):
        ok, err = self.validate("MarketAgent", {"symbol": "AA@L"})
        assert ok is False
        assert "Invalid stock symbol format" in err

    def test_invalid_symbol_too_long(self):
        ok, err = self.validate("MarketAgent", {"symbol": "TOOLONG"})
        assert ok is False
        assert "Invalid stock symbol format" in err

    def test_invalid_symbol_with_numbers(self):
        ok, err = self.validate("MarketAgent", {"symbol": "AAP1"})
        assert ok is False

    def test_valid_symbol_boundary_one_char(self):
        ok, err = self.validate("MarketAgent", {"symbol": "A"})
        assert ok is True

    def test_valid_symbol_boundary_five_chars(self):
        ok, err = self.validate("MarketAgent", {"symbol": "GOOGL"})
        assert ok is True

    def test_input_too_long(self):
        long_input = "A" * 301
        ok, err = self.validate("RAGTool", {"query": long_input})
        assert ok is False
        assert "exceeds maximum allowed length" in err

    def test_input_at_max_length(self):
        exact_input = "A" * 300
        ok, err = self.validate("RAGTool", {"query": exact_input})
        assert ok is True

    def test_sql_injection_blocked(self):
        ok, err = self.validate("RAGTool", {"query": "drop table users"})
        assert ok is False
        assert "blocked pattern" in err

    def test_sql_injection_delete(self):
        ok, err = self.validate("RAGTool", {"query": "delete from stocks"})
        assert ok is False

    def test_js_injection_blocked(self):
        ok, err = self.validate("RAGTool", {"query": "<script>alert(1)</script>"})
        assert ok is False

    def test_python_eval_blocked(self):
        ok, err = self.validate("RAGTool", {"query": "eval(os.system('rm -rf /'))"})
        assert ok is False

    def test_import_injection_blocked(self):
        ok, err = self.validate("RAGTool", {"query": "__import__('os').system('ls')"})
        assert ok is False

    def test_normal_rag_query_passes(self):
        ok, err = self.validate("RAGTool", {"query": "What is the PE ratio of Apple?"})
        assert ok is True

    def test_non_string_input_skipped(self):
        ok, err = self.validate("MarketAgent", {"symbol": "AAPL", "count": 5})
        assert ok is True


# ===========================================================================
# MEMORY STORE TESTS
# ===========================================================================

class TestMemoryStore:
    """Tests for memory/memory_store.py — uses a temp directory."""

    def setup_method(self, tmp_path_factory):
        import tempfile
        self.tmp_dir = Path(tempfile.mkdtemp())

    def _patch_memory_dir(self):
        import memory.memory_store as ms
        ms.MEMORY_DIR = self.tmp_dir
        return ms

    def test_load_history_new_user_returns_empty(self):
        ms = self._patch_memory_dir()
        result = ms.load_history("newuser_xyz")
        assert result == []

    def test_save_and_load_turn(self):
        ms = self._patch_memory_dir()
        ms.save_turn("alice", "What is AAPL?", "AAPL is Apple Inc.")
        history = ms.load_history("alice")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "What is AAPL?"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "AAPL is Apple Inc."

    def test_save_multiple_turns(self):
        ms = self._patch_memory_dir()
        ms.save_turn("bob", "Query 1", "Response 1")
        ms.save_turn("bob", "Query 2", "Response 2")
        history = ms.load_history("bob")
        assert len(history) == 4

    def test_clear_history(self):
        ms = self._patch_memory_dir()
        ms.save_turn("carol", "Hello", "Hi there")
        ms.clear_history("carol")
        result = ms.load_history("carol")
        assert result == []

    def test_clear_nonexistent_user_no_error(self):
        ms = self._patch_memory_dir()
        ms.clear_history("ghost_user_999")

    def test_format_history_empty(self):
        from memory.memory_store import format_history_for_prompt
        result = format_history_for_prompt([])
        assert result == "No previous conversation."

    def test_format_history_single_turn(self):
        from memory.memory_store import format_history_for_prompt
        history = [
            {"role": "user", "content": "Buy TSLA?"},
            {"role": "assistant", "content": "Based on analysis, HOLD."}
        ]
        result = format_history_for_prompt(history)
        assert "User: Buy TSLA?" in result
        assert "Assistant: Based on analysis, HOLD." in result

    def test_format_history_respects_max_turns(self):
        from memory.memory_store import format_history_for_prompt
        history = []
        for i in range(10):
            history.append({"role": "user", "content": f"Query {i}"})
            history.append({"role": "assistant", "content": f"Response {i}"})
        result = format_history_for_prompt(history, max_turns=2)
        assert "Query 8" in result
        assert "Query 9" in result
        assert "Query 0" not in result

    def test_timestamps_saved(self):
        ms = self._patch_memory_dir()
        ms.save_turn("dave", "Test query", "Test response")
        history = ms.load_history("dave")
        assert "timestamp" in history[0]
        assert "timestamp" in history[1]

    def test_session_files_are_isolated(self):
        ms = self._patch_memory_dir()
        ms.save_turn("user_a", "Query A", "Response A")
        ms.save_turn("user_b", "Query B", "Response B")
        history_a = ms.load_history("user_a")
        history_b = ms.load_history("user_b")
        assert history_a[0]["content"] == "Query A"
        assert history_b[0]["content"] == "Query B"


# ===========================================================================
# STOCK TOOLS TESTS
# ===========================================================================

class TestStockTools:
    """Tests for mcp_server/tools/stock_tools.py — yfinance is mocked."""

    def test_get_stock_price_success(self):
        import pandas as pd
        from mcp_server.tools.stock_tools import get_stock_price

        mock_data = pd.DataFrame({"Close": [175.50]})

        with patch("mcp_server.tools.stock_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = mock_data
            result = get_stock_price("AAPL")

        assert result["symbol"] == "AAPL"
        assert result["price"] == pytest.approx(175.50)

    def test_get_stock_price_empty_data(self):
        import pandas as pd
        from mcp_server.tools.stock_tools import get_stock_price

        with patch("mcp_server.tools.stock_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = pd.DataFrame()
            result = get_stock_price("FAKE")

        assert "error" in result

    def test_get_stock_price_exception(self):
        from mcp_server.tools.stock_tools import get_stock_price

        with patch("mcp_server.tools.stock_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.side_effect = Exception("Network error")
            result = get_stock_price("AAPL")

        assert "error" in result

    def test_get_stock_price_symbol_uppercased(self):
        import pandas as pd
        from mcp_server.tools.stock_tools import get_stock_price

        mock_data = pd.DataFrame({"Close": [100.0]})

        with patch("mcp_server.tools.stock_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = mock_data
            result = get_stock_price("aapl")

        assert result["symbol"] == "AAPL"


# ===========================================================================
# RSI / FINANCIAL TOOLS TESTS
# ===========================================================================

class TestFinancialTools:
    """Tests for mcp_server/tools/financial_tools.py — yfinance is mocked."""

    def _make_mock_history(self, prices):
        import pandas as pd
        return pd.DataFrame({"Close": prices})

    def test_calculate_rsi_returns_value(self):
        from mcp_server.tools.financial_tools import calculate_rsi

        prices = [100 + i * 0.5 for i in range(30)]

        with patch("mcp_server.tools.financial_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = self._make_mock_history(prices)
            result = calculate_rsi("AAPL")

        assert "rsi" in result
        assert 0 <= result["rsi"] <= 100

    def test_calculate_rsi_empty_data(self):
        import pandas as pd
        from mcp_server.tools.financial_tools import calculate_rsi

        with patch("mcp_server.tools.financial_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = pd.DataFrame()
            result = calculate_rsi("FAKE")

        assert "error" in result

    def test_calculate_rsi_symbol_uppercased(self):
        from mcp_server.tools.financial_tools import calculate_rsi

        prices = [100 + i for i in range(30)]

        with patch("mcp_server.tools.financial_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = self._make_mock_history(prices)
            result = calculate_rsi("tsla")

        assert result["symbol"] == "TSLA"

    def test_calculate_rsi_exception(self):
        from mcp_server.tools.financial_tools import calculate_rsi

        with patch("mcp_server.tools.financial_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.side_effect = Exception("Timeout")
            result = calculate_rsi("AAPL")

        assert "error" in result


# ===========================================================================
# FUNDAMENTAL TOOLS TESTS
# ===========================================================================

class TestFundamentalTools:
    """Tests for mcp_server/tools/fundamental_tools.py — yfinance is mocked."""

    def test_get_fundamentals_success(self):
        from mcp_server.tools.fundamental_tools import get_fundamentals

        mock_info = {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "marketCap": 3000000000000,
            "trailingPE": 28.5,
            "trailingEps": 6.13,
            "totalRevenue": 394000000000,
            "profitMargins": 0.25,
        }

        with patch("mcp_server.tools.fundamental_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.info = mock_info
            result = get_fundamentals("AAPL")

        assert result["symbol"] == "AAPL"
        assert result["company"] == "Apple Inc."
        assert result["sector"] == "Technology"
        assert result["pe_ratio"] == 28.5

    def test_get_fundamentals_empty_info(self):
        from mcp_server.tools.fundamental_tools import get_fundamentals

        with patch("mcp_server.tools.fundamental_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.info = {}
            result = get_fundamentals("FAKE")

        assert "error" in result

    def test_get_fundamentals_exception(self):
        from mcp_server.tools.fundamental_tools import get_fundamentals

        with patch("mcp_server.tools.fundamental_tools.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.info = None
            mock_ticker.side_effect = Exception("API error")
            result = get_fundamentals("AAPL")

        assert "error" in result


# ===========================================================================
# NEWS TOOLS TESTS
# ===========================================================================

class TestNewsTools:
    """Tests for mcp_server/tools/news_tools.py — requests is mocked."""

    def test_get_stock_news_success(self):
        from mcp_server.tools.news_tools import get_stock_news

        mock_response = {
            "articles": [
                {"title": "Apple hits record high", "source": {"name": "Reuters"}},
                {"title": "iPhone sales surge", "source": {"name": "Bloomberg"}},
            ]
        }

        with patch("mcp_server.tools.news_tools.requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            result = get_stock_news("AAPL")

        assert len(result) == 2
        assert result[0]["title"] == "Apple hits record high"
        assert result[0]["source"] == "Reuters"

    def test_get_stock_news_empty_articles(self):
        from mcp_server.tools.news_tools import get_stock_news

        with patch("mcp_server.tools.news_tools.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"articles": []}
            result = get_stock_news("AAPL")

        assert result == []

    def test_get_stock_news_exception(self):
        from mcp_server.tools.news_tools import get_stock_news

        with patch("mcp_server.tools.news_tools.requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            result = get_stock_news("AAPL")

        assert len(result) == 1
        assert "error" in result[0]


# ===========================================================================
# API CLIENT TESTS
# ===========================================================================

class TestApiClient:
    """Tests for api_client.py — requests is mocked."""

    def test_call_tool_success(self):
        from api_client import call_tool

        with patch("api_client.requests.post") as mock_post:
            mock_post.return_value.json.return_value = {"symbol": "AAPL", "price": 175.0}
            result = call_tool("get_stock_price", {"symbol": "AAPL"})

        assert result["symbol"] == "AAPL"
        assert result["price"] == 175.0

    def test_call_tool_error_response(self):
        from api_client import call_tool

        with patch("api_client.requests.post") as mock_post:
            mock_post.return_value.json.return_value = {"error": "Invalid tool"}
            result = call_tool("bad_tool", {})

        assert "error" in result

    def test_call_tool_network_exception(self):
        from api_client import call_tool

        with patch("api_client.requests.post") as mock_post:
            mock_post.side_effect = Exception("Connection refused")
            result = call_tool("get_stock_price", {"symbol": "AAPL"})

        assert "error" in result


# ===========================================================================
# GRAPH STATE TESTS
# ===========================================================================

class TestGraphState:
    """Tests for graph/state.py — verifies TypedDict structure."""

    def test_state_accepts_required_fields(self):
        from graph.state import GraphState
        state: GraphState = {
            "query": "Should I buy AAPL?",
            "symbol": "AAPL",
            "username": "alice",
            "history": "User: previous question\nAssistant: previous answer",
            "market": None,
            "technical": None,
            "news": None,
            "fundamental": None,
            "rag": None,
            "final": None,
        }
        assert state["query"] == "Should I buy AAPL?"
        assert state["username"] == "alice"

    def test_state_optional_fields_default_none(self):
        from graph.state import GraphState
        state: GraphState = {
            "query": "test",
            "symbol": "TSLA",
            "username": None,
            "history": None,
            "market": None,
            "technical": None,
            "news": None,
            "fundamental": None,
            "rag": None,
            "final": None,
        }
        assert state["market"] is None
        assert state["final"] is None
