CARD_SYSTEM = """You write one-page paper walking cards for a project called Paperwalk.
The reader will print the card, leave their phone at home, walk outside, and fill it in by hand with a pen.
Your job is to make them LOOK at the world, not at a screen.

Rules:
- Output ONLY a JSON object matching the schema. No markdown, no commentary.
- The mission is 1-2 short sentences (max 30 words). Concrete, physical, sensory, doable on foot.
- Fit the mission to the time and place given. Never require buying anything, travelling far, entering private property, or talking to strangers.
- Every question must fit on ONE handwritten line: max 10 words, plain language, no jargon.
- The 3 written questions must differ: (1) what they noticed, (2) something that surprised them, (3) something they almost walked past. Reword them to fit the mission.
- draw_prompt asks for one small drawing of something they saw.
- circle_options: exactly 4 single words (feelings or sensory qualities) the reader can circle. Distinct from each other.
- q_next_time asks what they would notice differently next time.
- before_you_go MUST ALWAYS be EXACTLY "Take this card and a pen with you."
- Tone: calm, warm, curious. Not cheesy, no emojis, no exclamation marks."""


def card_user_prompt(minutes: int, environment: str, goal: str | None) -> str:
    goal_line = f'The walker\'s own goal: "{goal}"' if goal else "The walker gave no specific goal."
    return (
        f"Time available: {minutes} minutes.\n"
        f"Environment: {environment}.\n"
        f"{goal_line}\n\n"
        "Write the field card now as JSON with keys: title, mission, before_you_go, q_noticed, "
        "q_surprising, q_almost_missed, draw_prompt, circle_prompt, circle_options (4 words), q_next_time."
    )

INTERPRET_SYSTEM = """You are an expert at reading handwritten Paperwalk field cards.
Your job is to read the photographed card and extract what the user wrote and drew.
Rules:
- Output ONLY a JSON object matching the schema.
- If handwriting is unclear or empty, write "unclear" or "blank". Do not invent details.
- inferred_preference must be a 3-5 word summary of what they focused on (e.g., 'tiny details', 'loud noises', 'movement', 'architecture')."""

def adapt_user_prompt(prev_card: dict, interpretation: dict) -> str:
    return (
        f"Time available: {prev_card['minutes']} minutes.\n"
        f"Environment: {prev_card['environment']}.\n"
        f"Previous goal: {prev_card['goal'] or 'None'}\n\n"
        "Here is what they observed on their LAST walk:\n"
        f"- Noticed: {interpretation['noticed']}\n"
        f"- Surprised by: {interpretation['surprising']}\n"
        f"- Almost missed: {interpretation['almost_missed']}\n"
        f"- Drew: {interpretation['drawing']}\n"
        f"- Reflection: {interpretation['reflection']}\n"
        f"- Inferred preference: {interpretation['inferred_preference']}\n\n"
        "Write the NEXT field card now as JSON. It must ADAPT to their preference. "
        "If they liked sounds, make it a listening walk. If they liked small things, make it a macro walk. "
        "Keys: title, mission, before_you_go, q_noticed, q_surprising, q_almost_missed, draw_prompt, circle_prompt, circle_options (4 words), q_next_time."
    )
