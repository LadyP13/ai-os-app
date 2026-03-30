"""
AI-OS FastAPI Server Entry Point
"""

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, agents, messages, permissions, requests, ws

app = FastAPI(title="AI-OS", description="AI Agent Operating System", version="1.0.0")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# Mount API routers
app.include_router(auth.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(permissions.router, prefix="/api")
app.include_router(requests.router, prefix="/api")

# Convenience alias for agent token endpoint
# Already available at /api/agents/{id}/token, but also expose at /api/agent-token/{id}
from fastapi import Depends
from app.auth import require_human, create_access_token, AGENT_TOKEN_EXPIRE_DAYS
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import Agent
from datetime import timedelta
import fastapi

@app.get("/api/agent-token/{agent_id}", tags=["auth"])
async def get_agent_token_alias(
    agent_id: int,
    current_user=Depends(require_human),
    db: Session = Depends(get_db)
):
    """Alias for /api/agents/{id}/token"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise fastapi.HTTPException(status_code=404, detail="Agent not found")

    token_data = {
        "sub": agent.user.username,
        "role": "agent",
        "agent_id": agent_id
    }
    token = create_access_token(
        data=token_data,
        expires_delta=timedelta(days=AGENT_TOKEN_EXPIRE_DAYS)
    )
    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "access_token": token,
        "token_type": "bearer",
        "expires_days": AGENT_TOKEN_EXPIRE_DAYS
    }


# WebSocket endpoint
app.include_router(ws.router)

# Serve frontend
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/", response_class=FileResponse)
    async def serve_index():
        return FileResponse(str(FRONTEND_DIST / "index.html"))

    @app.get("/{full_path:path}", response_class=FileResponse)
    async def serve_spa(full_path: str):
        """Serve the SPA - any non-API route returns index.html"""
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))

else:
    @app.get("/", response_class=HTMLResponse)
    async def serve_placeholder():
        return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-OS</title>
    <style>
        body {
            font-family: system-ui, sans-serif;
            background: #0f0f14;
            color: #e2e8f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .card {
            background: #1a1a24;
            border: 1px solid #7c3aed44;
            border-radius: 12px;
            padding: 40px;
            max-width: 480px;
            text-align: center;
        }
        h1 { color: #7c3aed; margin-bottom: 8px; }
        p { color: #94a3b8; line-height: 1.6; }
        code {
            background: #0f0f14;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 2px 8px;
            font-family: monospace;
            color: #10b981;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>AI-OS</h1>
        <p>Backend is running! The frontend hasn't been built yet.</p>
        <p>To build the frontend, run:</p>
        <p><code>cd frontend && npm install && npm run build</code></p>
        <p>Then restart the server.</p>
        <p>API docs available at <a href="/docs" style="color:#7c3aed">/docs</a></p>
    </div>
</body>
</html>
        """)
