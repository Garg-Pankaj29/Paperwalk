from typing import List
from pydantic import BaseModel, Field


class CardContent(BaseModel):
    """What Gemma writes. Everything else on the card is owned by the app."""
    title: str = Field(min_length=3, max_length=60)
    mission: str = Field(min_length=10, max_length=220)
    before_you_go: str = Field(min_length=3, max_length=140)
    q_noticed: str = Field(min_length=3, max_length=80)
    q_surprising: str = Field(min_length=3, max_length=80)
    q_almost_missed: str = Field(min_length=3, max_length=80)
    draw_prompt: str = Field(min_length=3, max_length=80)
    circle_prompt: str = Field(min_length=3, max_length=60)
    circle_options: List[str] = Field(min_length=4, max_length=4)
    q_next_time: str = Field(min_length=3, max_length=80)


_S = {"type": "string"}
# Simple JSON schema sent to LM Studio (constrained decoding). Pydantic does the strict checks.
CARD_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "title": _S, "mission": _S, "before_you_go": _S,
        "q_noticed": _S, "q_surprising": _S, "q_almost_missed": _S,
        "draw_prompt": _S, "circle_prompt": _S,
        "circle_options": {"type": "array", "items": _S, "minItems": 4, "maxItems": 4},
        "q_next_time": _S,
    },
    "required": ["title", "mission", "before_you_go", "q_noticed", "q_surprising",
                 "q_almost_missed", "draw_prompt", "circle_prompt", "circle_options", "q_next_time"],
    "additionalProperties": False,
}

class CardInterpretation(BaseModel):
    """What Gemma sees in the uploaded card."""
    noticed: str = Field(description="What the user noticed")
    surprising: str = Field(description="What surprised the user")
    almost_missed: str = Field(description="What the user almost missed")
    drawing: str = Field(description="Description of what they drew")
    reflection: str = Field(description="Their next-time reflection")
    inferred_preference: str = Field(description="A 3-5 word summary of what this user likes observing (e.g., 'tiny plants', 'loud sounds', 'patterns')")

INTERPRETATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "noticed": _S,
        "surprising": _S,
        "almost_missed": _S,
        "drawing": _S,
        "reflection": _S,
        "inferred_preference": _S,
    },
    "required": ["noticed", "surprising", "almost_missed", "drawing", "reflection", "inferred_preference"],
    "additionalProperties": False,
}
