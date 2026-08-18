"""Shared Ollama call and tool-execution loop."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Iterator

from tools import TOOLS, TOOL_FUNCTIONS

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
SYSTEM_PROMPT = """너는 사용자의 일을 돕는 한국어 에이전트다. 항상 자연스러운 한국어로 답한다.
사용자의 입력 언어를 따라 답하고, 모르는 값은 지어내지 않는다.
계산이 필요하면 반드시 calculate 도구를 사용한다.
최근 게임 1위처럼 최신 정보가 필요하면 recent_game_winner 도구를 사용한다.
도구 호출이 실패하면 숨기지 말고 무엇을 시도했고 왜 실패했는지 설명한다.
답변은 간결하고 실용적으로 작성한다."""


def _call_ollama(messages: list[dict]) -> dict:
    request = urllib.request.Request(OLLAMA_URL, data=json.dumps({"model": MODEL, "messages": messages, "tools": TOOLS, "stream": False}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Ollama 오류 ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ollama에 연결할 수 없습니다. Ollama 앱 또는 `ollama serve`를 확인하세요. 원인: {exc.reason}") from exc


def run_tool(name: str, args: dict) -> dict:
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return {"ok": False, "error": f"알 수 없는 도구: {name}"}
    try:
        return function(**args)
    except Exception as exc:
        return {"ok": False, "error": f"도구 실행 실패: {exc}"}


def step(messages: list[dict]) -> Iterator[tuple]:
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    for _ in range(5):
        try:
            response = _call_ollama(messages)
        except Exception as exc:
            yield ("error", str(exc))
            return
        message = response.get("message", {})
        messages.append(message)
        calls = message.get("tool_calls", [])
        if not calls:
            yield ("final", message.get("content", "응답을 받았지만 텍스트가 없습니다."))
            return
        for call in calls:
            function = call.get("function", {})
            args = function.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            name = function.get("name", "")
            result = run_tool(name, args)
            yield ("tool_call", name, args, result)
            messages.append({"role": "tool", "content": json.dumps(result, ensure_ascii=False), "tool_call_id": call.get("id", "")})
    yield ("error", "도구 호출이 너무 많이 반복되어 이번 응답을 중단했습니다.")
