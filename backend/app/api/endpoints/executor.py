from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import os
import base64

router = APIRouter()


class ExecBody(BaseModel):
    command: str


@router.post("/execute")
async def proxy_execute(body: ExecBody):    
    """Execute xdotool command inside the VNC container via docker exec."""
    try:
        container = os.getenv("VNC_CONTAINER_NAME", "vncagentic-vnc-agent-1")
        cmd = f"DISPLAY=:1; {body.command}"
        completed = subprocess.run(
            [
                "docker",
                "exec",
                container,
                "bash",
                "-lc",
                cmd,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "return_code": completed.returncode,
            "output": completed.stdout,
            "error": completed.stderr,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


