from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import uuid
from dotenv import load_dotenv
import os
from inference_server.groq.infer import generate_manim_code, format_manim_code
import requests
import logging

load_dotenv()


class Query(BaseModel):
    query: str


class Response(BaseModel):
    status: str
    id: str
    video_link: str


app = FastAPI()
renderer_url = os.environ["RENDERER_URL"]

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)  # Create a logger object


@app.post("/generate")
async def render(req: Query) -> Response:
    query = req.query
    logger.info(f"Request received with query: {query}")
    global_retry_count = 0
    code = generate_manim_code(query)
    formatted_code = format_manim_code(code)
    id = str(uuid.uuid4())
    req = requests.post(
        f"{renderer_url}/render",
        json={
            "id": id,
            "code": formatted_code,
        },
    )
    while req.status_code == 400 and global_retry_count < 3:
        global_retry_count += 1
        query += f"I tried this:\n{code}. And I got this error: {req.text}."
        print(f"Retrying {global_retry_count} times.")
        code = generate_manim_code(query)
        formatted_code = format_manim_code(code)
        req = requests.post(
            f"{renderer_url}/render",
            json={
                "id": id,
                "code": formatted_code,
            },
        )

    if req.status_code != 200:
        raise HTTPException(status_code=400, detail=req.text)

    video_link = req.json()["video_link"]
    return {"status": "success", "id": id, "video_link": video_link}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
