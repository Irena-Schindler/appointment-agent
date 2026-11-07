"""Tiny eval harness: tool choice + guardrail behaviour per case. Uses the real LLM if ANTHROPIC_API_KEY is set."""
import os, sys, yaml
from app.agent import Agent
from app.llm import AnthropicLLM, ScriptedLLM


def main() -> int:
    cases = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "cases.yaml")))
    llm = AnthropicLLM() if os.getenv("ANTHROPIC_API_KEY") else ScriptedLLM()
    passed = 0
    for c in cases:
        r = Agent(llm).handle(c["input"])
        ok = r.blocked if c.get("expect_blocked") else any(t["name"] == c["expect_tool"] for t in r.tool_calls)
        passed += ok
        print(("PASS" if ok else "FAIL"), "|", c["input"])
    print(f"{passed}/{len(cases)} passed with {type(llm).__name__}")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
