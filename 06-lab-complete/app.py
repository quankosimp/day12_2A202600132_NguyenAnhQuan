import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from agent import run_agent

app = FastAPI(title="TravelBuddy API", version="1.0.0")
BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML_PATH = BASE_DIR / "web" / "index.html"
logger = logging.getLogger("travelbuddy.api")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User input message")


class ChatResponse(BaseModel):
    reply: str
    trace_id: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML_PATH.read_text(encoding="utf-8"))


@app.get("/status")
def status() -> dict[str, str]:
    return {"service": "TravelBuddy API", "status": "ok", "health": "/health", "docs": "/docs"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        user_message = payload.message.strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="message must not be empty")

        result = run_agent(user_message)
        final_message = result["messages"][-1].content if result.get("messages") else ""
        trace_id = result.get("trace_id", "-")
        return ChatResponse(reply=final_message, trace_id=trace_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("POST /chat failed | error=%s", exc)
        raise HTTPException(
            status_code=500, detail=f"Hệ thống đang bị lỗi... ({exc})"
        )
