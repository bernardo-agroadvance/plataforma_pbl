# fastapi_backend/main.py
import os
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carrega variáveis de ambiente no início
load_dotenv()

# Importa todos os roteadores
from .routers import auth, usuarios, desafios, respostas, admin, conteudos, liberacoes

# Define a versão e documentação da API
ENV = os.getenv("ENV", "development")
app = FastAPI(
    title="PBL Agroadvance API",
    version="2.0.0-refactored",
    docs_url="/docs" if ENV == "development" else None,
    redoc_url="/redoc" if ENV == "development" else None,
)

# Configuração de CORS (Cross-Origin Resource Sharing)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gerenciador de WebSocket ---
class ConnectionManager:
    # ... (o código dentro da classe ConnectionManager não muda) ...
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Lógica de verificação de origem aprimorada
    origin = websocket.headers.get("origin", "").rstrip("/")
    if not any(allowed.strip("/") == origin for allowed in allowed_origins):
        await websocket.close(code=1008)
        print(f"Conexão WebSocket rejeitada da origem: {origin}")
        return

    await manager.connect(websocket)
    print("Conexão WebSocket aceita")
    try:
        while True:
            data = await websocket.receive_text()
            if data.strip().lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        print("Conexão WebSocket fechada")
        manager.disconnect(websocket)

# --- Inclusão dos Roteadores ---
# Roteadores de Autenticação não precisam do prefixo /api
app.include_router(auth.router)

# Roteadores da API principal
api_prefix = "/api"
app.include_router(usuarios.router, prefix=api_prefix)
app.include_router(desafios.router, prefix=api_prefix)
app.include_router(respostas.router, prefix=api_prefix)
app.include_router(conteudos.router, prefix=api_prefix)
app.include_router(liberacoes.router, prefix=api_prefix)

# Roteadores do Painel Administrativo
app.include_router(admin.router, prefix=f"{api_prefix}/admin")


@app.get("/", tags=["Root"])
def read_root():
    """ Endpoint principal para verificar se a API está online. """
    return {"status": "online", "message": "Bem-vindo à API da Plataforma PBL"}