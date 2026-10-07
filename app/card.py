import uuid
from datetime import datetime, timezone

from . import llm
from .prompts import CARD_SYSTEM, card_user_prompt
from .schemas import CARD_JSON_SCHEMA, CardContent

_COMMON = dict(
    q_noticed="I noticed:",
    q_surprising="Something surprising:",
    q_almost_missed="Something I almost walked past:",
    draw_prompt="Draw something you saw",
    circle_prompt="Circle one",
    circle_options=["peaceful", "strange", "beautiful", "noisy"],
    q_next_time="One thing I'd notice differently next time:",
)
FALLBACKS = {
    "park": dict(title="The Slow Loop", mission="Walk without a destination. Stop at the first thing that makes you slow down, then stop again at something you would normally ignore.", before_you_go="Bring a pen. Wear shoes you can stand in.", **_COMMON),
    "campus": dict(title="The Familiar Place", mission="Take a route you walk every day, but look at it as a stranger would. Find what has been there all along.", before_you_go="Bring a pen. Leave your phone behind.", **_COMMON),
    "neighborhood": dict(title="Your Street, Slowly", mission="Walk a few streets near home. Look up, look low, and listen for what usually fades into the background.", before_you_go="Bring a pen. Keep your keys in a pocket.", **_COMMON),
}


def generate_card(minutes: int, environment: str, goal: str | None) -> dict:
    source, error = "gemma", None
    try:
        raw = llm.chat_json(CARD_SYSTEM, card_user_prompt(minutes, environment, goal), CARD_JSON_SCHEMA)
        content = CardContent(**raw).model_dump()
    except Exception as e:  # LM Studio down, bad JSON, failed validation: never block the user
        source, error = "fallback", f"{type(e).__name__}: {e}"[:300]
        content = FALLBACKS[environment]
    return {
        "id": uuid.uuid4().hex[:8],
        "card_number": 1,
        "minutes": minutes,
        "environment": environment,
        "goal": goal,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "model": llm._model_cache,
        "error": error,
        "uploaded": False,
        "content": content,
    }


def generate_adapted_card(prev_card: dict, image_bytes: bytes) -> dict:
    source, error = "gemma", None
    try:
        from .schemas import INTERPRETATION_JSON_SCHEMA, CardInterpretation
        from .prompts import INTERPRET_SYSTEM, adapt_user_prompt
        
        # 1. Interpret image
        raw_interp = llm.chat_json_vision(
            INTERPRET_SYSTEM, 
            "Extract the information from this filled-out Paperwalk card.", 
            image_bytes, 
            INTERPRETATION_JSON_SCHEMA
        )
        interp = CardInterpretation(**raw_interp).model_dump()
        
        # 2. Generate new card
        raw_card = llm.chat_json(CARD_SYSTEM, adapt_user_prompt(prev_card, interp), CARD_JSON_SCHEMA)
        content = CardContent(**raw_card).model_dump()
    except Exception as e:
        source, error = "fallback", f"{type(e).__name__}: {e}"[:300]
        content = FALLBACKS[prev_card["environment"]]
        
    return {
        "id": uuid.uuid4().hex[:8],
        "card_number": prev_card.get("card_number", 1) + 1,
        "minutes": prev_card["minutes"],
        "environment": prev_card["environment"],
        "goal": prev_card.get("goal"),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "model": llm._model_cache,
        "error": error,
        "uploaded": False,
        "content": content,
    }
