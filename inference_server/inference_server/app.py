from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional
import uuid
from dotenv import load_dotenv
import os
# from inference_server.groq.infer import generate_manim_code, format_manim_code, analyze_error_log
from inference_server.groq.infer import CodeGenerator
import requests
import logging
import httpx

load_dotenv()


class Query(BaseModel):
    query: str
    rag: Optional[bool]


class Response(BaseModel):
    status: str
    id: str
    video_link: str


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    code_generator = CodeGenerator(query, enable_rag=req.rag if req.rag else False)
    code = code_generator.generate_manim_code()
    logger.info(f"Generated code: {code}")
    formatted_code = code_generator.format_manim_code(code)
    id = str(uuid.uuid4())
    req = await render_request(id, formatted_code)
    while req.status_code == 400 and global_retry_count < 3:
        global_retry_count += 1
        logger.info(f"Retrying {global_retry_count} times with query:\n {query}")
        code_generator.analyze_error_and_update_messages(req.text, code)
        code = code_generator.generate_manim_code()
        logger.info(f"Generated code: {code}")
        formatted_code = code_generator.format_manim_code(code)
        req = await render_request(id, formatted_code)
    if req.status_code != 200:
        logger.error(f"Error in rendering: {req.text}")
        raise HTTPException(status_code=400, detail="Error in rendering. Please try again later.")

    video_link = req.json()["video_link"]
    logger.info(f"Video Link: {video_link}")
    return {"status": "success", "id": id, "video_link": video_link}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
