"""Tool schemas and implementations used by the agent."""

from __future__ import annotations

import ast
import json
import operator
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

STEAM_TOP_SELLERS_URL = "https://store.steampowered.com/api/featuredcategories?cc=kr&l=koreana"

TOOLS = [
    {"type": "function", "function": {"name": "calculate", "description": "수학식을 안전하게 계산한다.", "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "계산할 수학식. 예: (125 * 48) / 5"}}, "required": ["expression"]}}},
    {"type": "function", "function": {"name": "recent_game_winner", "description": "Steam 한국 스토어의 현재 판매 인기 1위 게임을 조회한다.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}},
]


def calculate(expression: str) -> dict[str, Any]:
    operators = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod, ast.USub: operator.neg, ast.UAdd: operator.pos}

    def visit(node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("거듭제곱 지수가 너무 큽니다")
            return operators[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in operators:
            return operators[type(node.op)](visit(node.operand))
        raise ValueError("지원하지 않는 수식입니다")

    try:
        value = visit(ast.parse(expression, mode="eval").body)
        result = round(value, 10) if isinstance(value, float) and not value.is_integer() else int(value)
        return {"ok": True, "expression": expression, "result": result}
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as exc:
        return {"ok": False, "expression": expression, "error": str(exc)}


def recent_game_winner() -> dict[str, Any]:
    try:
        import certifi
        tls_context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        tls_context = ssl.create_default_context()
    request = urllib.request.Request(STEAM_TOP_SELLERS_URL, headers={"User-Agent": "local-ollama-chatbot/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15, context=tls_context) as response:
            data = json.loads(response.read().decode("utf-8"))
        items = data.get("top_sellers", {}).get("items", [])
        if not items:
            return {"ok": False, "error": "Steam top sellers 데이터를 찾지 못했습니다."}
        game = items[0]
        return {"ok": True, "rank": 1, "game": game.get("name", "이름 없음"), "appid": game.get("id"), "checked_at_utc": datetime.now(timezone.utc).isoformat(), "source": STEAM_TOP_SELLERS_URL, "criteria": "Steam 한국 스토어 top sellers 첫 번째 항목"}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": f"Steam 조회 오류 ({exc.code})"}
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return {"ok": False, "error": f"Steam 데이터에 연결하지 못했습니다: {exc}"}


TOOL_FUNCTIONS = {"calculate": calculate, "recent_game_winner": recent_game_winner}
