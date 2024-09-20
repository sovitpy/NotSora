from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import uuid
from dotenv import load_dotenv
import os
from inference_server.groq.infer import generate_manim_code, format_manim_code, analyze_error_log
import requests
import logging
import httpx

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

logger = logging.getLogger(__name__) 

async def render_request(id, code):
    async with httpx.AsyncClient(timeout=60.0) as client: 
        response = await client.post(f"{renderer_url}/render", json={
            "id": id,
            "code": code,
        })
        return response

@app.post("/generate")
async def render(req: Query) -> Response:
    query = req.query
    logger.info(f"Request received with query: {query}")
    global_retry_count = 0
    code = generate_manim_code(query)
    logger.info(f"Generated code: {code}")
    formatted_code = format_manim_code(code)
    id = str(uuid.uuid4())
    req = await render_request(id, formatted_code)
    while req.status_code == 400 and global_retry_count < 3:
        global_retry_count += 1
        log_analysis = analyze_error_log(req.text)
        query += f"I tried this:\n{code} and I received an error. Here is the error analysis: {log_analysis}."
        logger.info(f"Retrying {global_retry_count} times with query:\n {query}")
        code = generate_manim_code(query)
        logger.info(f"Generated code: {code}")
        formatted_code = format_manim_code(code)
        req = await render_request(id, formatted_code)
    if req.status_code != 200:
        logger.error(f"Error in rendering: {req.text}")
        raise HTTPException(status_code=400, detail="Error in rendering. Please try again later.")

    video_link = req.json()["video_link"]
    return {"status": "success", "id": id, "video_link": video_link}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
