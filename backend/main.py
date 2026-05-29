from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil, os
from dotenv import load_dotenv

load_dotenv()

from core.loader import load_and_split
from core.vectorstore import get_vectorstore, reset_vectorstore
from core.keywords import extract_keywords
from core.flashcard import generate_flashcard
from core.qa import ask_document
from core.evaluator import evaluate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend HTML as static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Global state (single user — sufficient for demo/resume)
store = {"vectorstore": None, "cards": []}

# ── Routes ──────────────────────────────────────────────────

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("./doc", exist_ok=True)
    path = f"./doc/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks = load_and_split(path)
    store["vectorstore"] = get_vectorstore(chunks)
    keywords = extract_keywords(store["vectorstore"])
    return {"status": "ok", "keywords": keywords}


class GenerateRequest(BaseModel):
    topics: list[str]
    num_questions: int = 1

@app.post("/generate")
def generate(req: GenerateRequest):
    if not store["vectorstore"]:
        return {"error": "No document loaded"}

    all_cards = []
    for topic in req.topics:
        result = generate_flashcard(
            topic, store["vectorstore"], req.num_questions
        )
        for block in result.strip().split("\n\n"):
            lines = block.strip().split("\n")
            q = next((l.replace("Q:", "").strip() for l in lines if l.startswith("Q:")), "")
            a = next((l.replace("A:", "").strip() for l in lines if l.startswith("A:")), "")
            if q and a:
                all_cards.append({"topic": topic, "q": q, "a": a})

    store["cards"] = all_cards
    return {"cards": all_cards}


class EvalRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str

@app.post("/evaluate")
def evaluate(req: EvalRequest):
    if not store["vectorstore"]:
        return {"error": "No document loaded"}
    result = evaluate_answer(
        req.question,
        req.user_answer,
        req.correct_answer,
        store["vectorstore"]
    )
    return result


class QARequest(BaseModel):
    question: str
    chat_history: list = []

@app.post("/qa")
def qa(req: QARequest):
    if not store["vectorstore"]:
        return {"error": "No document loaded"}
    result = ask_document(
        req.question,
        store["vectorstore"],
        req.chat_history
    )
    return result