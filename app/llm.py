"""The ONLY file that knows about LM Studio. Swap the runtime here later."""
import json
import os
import httpx
import base64

BASE_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1").rstrip("/")
_model_cache: str | None = None


def list_models() -> list[str]:
    r = httpx.get(f"{BASE_URL}/models", timeout=5)
    r.raise_for_status()
    return [m["id"] for m in r.json().get("data", [])]


def pick_model() -> str:
    """Env override > first model with 'gemma' in the id > first non-embedding model."""
    global _model_cache
    if os.getenv("LMSTUDIO_MODEL"):
        return os.environ["LMSTUDIO_MODEL"]
    if _model_cache:
        return _model_cache
    ids = list_models()
    gemma = [i for i in ids if "gemma" in i.lower()]
    usable = gemma or [i for i in ids if "embed" not in i.lower()]
    if not usable:
        raise RuntimeError("No chat model loaded in LM Studio")
    _model_cache = usable[0]
    return _model_cache


def _extract_json(text: str) -> dict:
    text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start:end + 1])


def chat_json(system: str, user: str, schema: dict, temperature: float = 0.8,
              max_tokens: int = 900, timeout: float = 180) -> dict:
    payload = {
        "model": pick_model(),
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "paperwalk", "strict": True, "schema": schema}},
    }
    url = f"{BASE_URL}/chat/completions"
    r = httpx.post(url, json=payload, timeout=timeout)
    if r.status_code == 400:  # runtime rejected structured output -> plain prompt, we parse ourselves
        payload.pop("response_format")
        r = httpx.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return _extract_json(r.json()["choices"][0]["message"]["content"])


def chat_json_vision(system: str, user: str, image_bytes: bytes, schema: dict, temperature: float = 0.2,
                     max_tokens: int = 900, timeout: float = 180) -> dict:
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    content = [
        {"type": "text", "text": user},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
    ]
    payload = {
        "model": pick_model(),
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": content}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "paperwalk", "strict": True, "schema": schema}},
    }
    url = f"{BASE_URL}/chat/completions"
    r = httpx.post(url, json=payload, timeout=timeout)
    if r.status_code == 400:
        payload.pop("response_format")
        r = httpx.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return _extract_json(r.json()["choices"][0]["message"]["content"])
