# Step1: Setup FastAPI backend
from fastapi import FastAPI, HTTPException, Query as QueryParam
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import requests
import uvicorn

try:
    from .ai_agent import handle_message, stream_message
    from .tools import find_nearby_care
except ImportError:
    from ai_agent import handle_message, stream_message
    from tools import find_nearby_care

app = FastAPI()

# Step2: Receive and validate request from Frontend
class Query(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)


def _validated_message(query: Query) -> str:
    message = query.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    return message



@app.post("/ask")
def ask(query: Query):
    message = _validated_message(query)

    try:
        final_response, tool_called_name = handle_message(message, query.history)
        return {
            "response": final_response,
            "tool_called": tool_called_name,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the message right now.",
        ) from exc


@app.post("/ask-stream")
def ask_stream(query: Query):
    message = _validated_message(query)
    return StreamingResponse(
        stream_message(message, query.history),
        media_type="text/plain; charset=utf-8",
    )


@app.get("/nearby-care")
def nearby_care(
    location: str = QueryParam(min_length=2, max_length=120),
    radius_km: int = QueryParam(default=12, ge=2, le=25),
):
    try:
        return find_nearby_care(location.strip(), radius_km)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail="The nearby-care service is temporarily unavailable.",
        ) from exc


if __name__ == "__main__":
    import os
    import sys
    import uvicorn

    # Add the project root to sys.path for the current process
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=project_root)
