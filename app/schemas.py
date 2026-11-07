"""Typed tool schemas. Every tool call from the model is validated before it touches a backend."""
from datetime import date, time
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class CheckSlots(BaseModel):
    day: date = Field(description="Requested day, ISO format")
    service: Literal["physio", "massage", "consultation"]


class BookAppointment(BaseModel):
    day: date
    start: time
    service: Literal["physio", "massage", "consultation"]
    name: str = Field(min_length=2, max_length=80)
    phone: str = Field(pattern=r"^\+?[0-9 ]{6,20}$")

    @field_validator("name")
    @classmethod
    def no_markup(cls, v: str) -> str:
        if any(c in v for c in "<>{}"):
            raise ValueError("name contains markup")
        return v.strip()


class RequestCallback(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    phone: str = Field(pattern=r"^\+?[0-9 ]{6,20}$")
    topic: str = Field(max_length=200)


TOOLS: dict[str, type[BaseModel]] = {
    "check_slots": CheckSlots,
    "book_appointment": BookAppointment,
    "request_callback": RequestCallback,
}


def tool_specs() -> list[dict]:
    """JSON schema definitions in the format most LLM APIs accept for tool use."""
    docs = {
        "check_slots": "List free appointment slots for a day and service.",
        "book_appointment": "Book a slot that check_slots returned as free.",
        "request_callback": "Ask staff to call the person back.",
    }
    return [
        {"name": n, "description": docs[n], "input_schema": m.model_json_schema()}
        for n, m in TOOLS.items()
    ]


class AgentReply(BaseModel):
    text: str
    tool_calls: list[dict] = []
    sources: list[str] = []
    blocked: bool = False
