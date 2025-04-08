from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict
import uvicorn
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Simulação de usuários conectados
users: Dict[str, Dict] = {
    "11999999999": {
        "name": "João",
        "step": 3,
        "messages": ["Oi, tudo bem?", "Preciso de ajuda com o pedido"]
    },
    "11888888888": {
        "name": "Maria",
        "step": 2,
        "messages": ["Olá!", "Qual é o prazo de entrega?"]
    }
}

# Conexões WebSocket ativas
active_connections: Dict[str, WebSocket] = {}

# Página principal do dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "users": users
    })

# Página de chat para um número específico
@app.get("/chat/{phone}", response_class=HTMLResponse)
async def open_chat(request: Request, phone: str):
    if phone not in users:
        return HTMLResponse("Usuário não encontrado", status_code=404)
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "phone": phone,
        "name": users[phone]["name"],
        "messages": users[phone]["messages"]
    })

# WebSocket para conversa em tempo real
@app.websocket("/ws/{phone}")
async def websocket_endpoint(websocket: WebSocket, phone: str):
    await websocket.accept()
    active_connections[phone] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            users[phone]["messages"].append(f"Atendente: {data}")
            await websocket.send_text(json.dumps({
                "from": "atendente",
                "message": data
            }))
    except WebSocketDisconnect:
        del active_connections[phone]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
