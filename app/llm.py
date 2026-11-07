"""Provider abstraction. ScriptedLLM makes tests and evals deterministic; AnthropicLLM is the real one."""
from __future__ import annotations
import json, os, re
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class LLMTurn:
    text: str
    tool_calls: list[dict]


class ScriptedLLM:
    """Rule-based stand-in so the agent loop can be tested without an API key."""

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMTurn:
        last = messages[-1]
        if last["role"] == "tool":
            data = json.loads(last["content"])
            if "slots" in data:
                s = data["slots"]
                return LLMTurn(f"Free slots: {', '.join(s[:3])}." if s else "No free slots that day.", [])
            if data.get("booked"):
                return LLMTurn("Your appointment is booked.", [])
            if data.get("callback"):
                return LLMTurn("A colleague will call you back.", [])
            return LLMTurn("That did not work, may I take a callback request?", [])
        user = last["content"].lower()
        day = (date.today() + timedelta(days=1)).isoformat()
        m = re.search(r"\d{4}-\d{2}-\d{2}", user)
        if m:
            day = m.group(0)
        if "book" in user or "buchen" in user:
            t = re.search(r"(\d{1,2}):(\d{2})", user)
            start = f"{int(t.group(1)):02d}:{t.group(2)}" if t else "09:00"
            return LLMTurn("", [{"name": "book_appointment", "input": {
                "day": day, "start": start, "service": "physio",
                "name": "Max Muster", "phone": "+49 151 000000"}}])
        if "callback" in user or "rückruf" in user:
            return LLMTurn("", [{"name": "request_callback", "input": {
                "name": "Max Muster", "phone": "+49 151 000000", "topic": "question"}}])
        if "slot" in user or "termin" in user or "free" in user:
            return LLMTurn("", [{"name": "check_slots", "input": {"day": day, "service": "physio"}}])
        return LLMTurn("I can check free slots, book an appointment or arrange a callback.", [])


class AnthropicLLM:
    def __init__(self, model: str | None = None) -> None:
        import anthropic  # optional dependency
        self.client = anthropic.Anthropic()
        self.model = model or os.getenv("LLM_MODEL", "claude-sonnet-5-5")

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMTurn:
        system = messages[0]["content"]
        conv = []
        for m in messages[1:]:
            if m["role"] == "tool":
                conv.append({"role": "user", "content": [{"type": "tool_result",
                             "tool_use_id": m["tool_use_id"], "content": m["content"]}]})
            elif m["role"] == "assistant_tool":
                conv.append({"role": "assistant", "content": m["blocks"]})
            else:
                conv.append({"role": m["role"], "content": m["content"]})
        r = self.client.messages.create(model=self.model, max_tokens=800, system=system,
                                        tools=tools, messages=conv)
        text = "".join(b.text for b in r.content if b.type == "text")
        calls = [{"id": b.id, "name": b.name, "input": b.input} for b in r.content if b.type == "tool_use"]
        return LLMTurn(text, calls)
