from pathlib import Path
from fastapi import FastAPI, Form, HTTPException, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import llm, state
from .card import generate_card, generate_adapted_card

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Paperwalk")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/api/health")
def health():
    try:
        return {"lm_studio": "up", "models": llm.list_models(), "will_use": llm.pick_model()}
    except Exception as e:
        return {"lm_studio": "down", "error": str(e)}


@app.post("/generate")
def generate(minutes: int = Form(...), environment: str = Form(...), goal: str = Form("")):
    if minutes not in (20, 40, 60) or environment not in ("park", "campus", "neighborhood"):
        raise HTTPException(400, "bad input")
    card = generate_card(minutes, environment, goal.strip()[:140] or None)
    state.save_card(card)
    return RedirectResponse(f"/card/{card['id']}", status_code=303)


@app.get("/card/{card_id}")
def show_card(request: Request, card_id: str):
    card = state.get_card(card_id)
    if not card:
        raise HTTPException(404, "card not found")
    return templates.TemplateResponse(request, "card.html", {"card": card})

@app.get("/back/{card_id}")
def show_back(request: Request, card_id: str):
    card = state.get_card(card_id)
    if not card:
        raise HTTPException(404, "card not found")
    return templates.TemplateResponse(request, "back.html", {"card": card})


@app.post("/adapt/{card_id}")
async def adapt_card(card_id: str, photo: UploadFile = File(...)):
    prev_card = state.get_card(card_id)
    if not prev_card:
        raise HTTPException(404, "card not found")
        
    prev_card["uploaded"] = True
    state.save_card(prev_card)
    
    image_bytes = await photo.read()
    new_card = generate_adapted_card(prev_card, image_bytes)
    state.save_card(new_card)
    
    return RedirectResponse(f"/card/{new_card['id']}", status_code=303)
