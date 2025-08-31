# backend/ws_server.py

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone

# ✅ Carrega variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Armazena clientes conectados
connected_clients = set()

async def notify_clients():
    """
    Envia uma mensagem para todos os clientes conectados via WebSocket.
    """
    if connected_clients:
        message = json.dumps({
            "evento": "desafio_gerado",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Envia de forma segura e paralela
        await asyncio.gather(*(send_safe(client, message) for client in connected_clients))

async def send_safe(client, message):
    """
    Garante envio seguro da mensagem e remove clientes desconectados.
    """
    try:
        await client.send(message)
    except Exception as e:
        print(f"⚠️ Erro ao enviar para cliente: {e}")
        connected_clients.discard(client)

async def check_updates_periodically():
    """
    Loop que simula eventos a cada 10s.
    Troque essa função para detectar mudanças reais no Supabase.
    """
    while True:
        try:
            await asyncio.sleep(10)
            print("🔔 Notificando todos os clientes conectados...")
            await notify_clients()
        except Exception as e:
            print(f"🚨 Erro ao enviar atualização: {e}")

async def handler(websocket):
    """
    Gerencia conexão de cada cliente individual.
    """
    print("📡 Novo cliente conectado.")
    connected_clients.add(websocket)
    try:
        async for _ in websocket:
            pass  # Pode ser adaptado se quiser receber mensagens
    except websockets.ConnectionClosed:
        print("🔌 Conexão encerrada pelo cliente.")
    finally:
        connected_clients.discard(websocket)
        print("📴 Cliente removido da lista.")

async def main():
    print("🚀 Iniciando servidor WebSocket...")
    async with websockets.serve(handler, "localhost", 8000):
        print("🟢 Servidor WebSocket ativo em ws://localhost:8000")
        await check_updates_periodically()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Servidor WebSocket encerrado manualmente.")
