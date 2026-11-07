# appointment-agent

A small, production-minded LLM agent that books appointments for a (fictional) physiotherapy practice.
It shows the parts that decide whether an agent survives real customers: **typed tool schemas,
guardrails against prompt injection, PII-safe logging and a regression eval suite.**

```
user ──► guardrail ──► LLM ──► tool call ──► schema validation ──► calendar
             │                     ▲                                   │
             └── blocked           └──── sanitised tool result ◄───────┘
```

## What it demonstrates

| Concern | How |
|---|---|
| Tool calling | Model proposes `check_slots`, `book_appointment`, `request_callback`; specs generated from Pydantic models |
| Safe execution | Every tool call is validated (`pydantic`) before it reaches the backend; invalid calls are returned to the model as errors |
| Prompt injection | Heuristic filter on user input (EN/DE) and on tool output, which is treated as data, never as instructions |
| Privacy | Phone numbers and e-mail addresses are redacted before logging |
| Bounded loops | Max. 4 tool steps, then a safe fallback (callback) |
| Testability | `ScriptedLLM` makes the loop deterministic; `AnthropicLLM` is the real provider behind the same interface |
| Regression evals | `evals/cases.yaml` checks tool choice and guardrails after every prompt or model change |

## Run

```bash
pip install -r requirements.txt
pytest -q                       # unit tests, no API key needed
python -m evals.run             # eval suite (uses the real model if ANTHROPIC_API_KEY is set)
uvicorn app.main:app --reload   # POST /chat {"text": "..."}
```

Docker: `docker build -t appointment-agent . && docker run -p 8000:8000 appointment-agent`

## Background

Distilled from building voice and chat agents that handle real customer calls in DACH.
The domain and data here are fictional; the patterns are the ones that mattered in production.
