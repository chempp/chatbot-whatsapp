from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
from typing import Dict
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

connected_users: Dict[str, WebSocket] = {}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request, username: str):
    return templates.TemplateResponse("chat.html", {"request": request, "username": username})

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    connected_users[username] = websocket
    await notify_users()
    try:
        while True:
            data = await websocket.receive_text()
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            for user, conn in connected_users.items():
                await conn.send_text(f"[{timestamp}] {username}: {data}")
    except WebSocketDisconnect:
        del connected_users[username]
        await notify_users()

async def notify_users():
    user_list = ", ".join(connected_users.keys())
    for conn in connected_users.values():
        await conn.send_text(f"Usuários online: {user_list}")