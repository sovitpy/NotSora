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


class ManimCode(BaseModel):
    id: str
    code: List[str]


app = FastAPI()


@app.post("/render")
async def render(code: ManimCode):
    filename = create_file(code.id, code.code)
    output = render_in_docker(filename)
    print(output)

    if "Traceback" in output or "There are no scenes" in output:
        output = re.sub(" +", " ", output)
        cleanup(code.id)
        raise HTTPException(status_code=400, detail=output)

    video_link = upload_video_to_bucket(filename)
    cleanup(code.id)
    return {"status": "success", "video_link": video_link}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
