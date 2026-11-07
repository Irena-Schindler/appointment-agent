import os
from fastapi import FastAPI
from pydantic import BaseModel
from .agent import Agent
from .llm import AnthropicLLM, ScriptedLLM
from .schemas import AgentReply

app = FastAPI(title="appointment-agent")
agent = Agent(AnthropicLLM() if os.getenv("ANTHROPIC_API_KEY") else ScriptedLLM())


class Msg(BaseModel):
    text: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm": type(agent.llm).__name__}


@app.post("/chat", response_model=AgentReply)
def chat(m: Msg) -> AgentReply:
    return agent.handle(m.text)
