from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import List
from renderer.utils.render_utils import (
    create_file,
    render_in_docker,
    upload_video_to_bucket,
    cleanup
)
import re
import logging

class ManimCode(BaseModel):
    id: str
    code: List[str]


app = FastAPI()
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__) 

@app.post("/render")
async def render(code: ManimCode):
    filename = create_file(code.id, code.code)
    container_output = render_in_docker(filename)
    output = container_output["output"]

    if container_output["exit_code"] == 124:
        output = "Timeout Error: The code took too long to execute. Please optimize your code and try again. Log before timeout: \n" + output
        cleanup(code.id)
        raise HTTPException(status_code=400, detail=output)

    if container_output["exit_code"] != 0 or "ERROR" in output:
        output = re.sub(" +", " ", output)
        cleanup(code.id)
        raise HTTPException(status_code=400, detail=output)
    
    else: 
        video_link = upload_video_to_bucket(filename)
        cleanup(code.id)
        return {"status": "success", "video_link": video_link}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
