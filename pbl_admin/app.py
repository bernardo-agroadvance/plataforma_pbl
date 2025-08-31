# pbl_admin/app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Painel PBL", layout="wide")

# Centraliza a URL da API
API_URL = os.getenv("FASTAPI_API_URL", "http://localhost:8000/api/admin")

def get_data_from_api(endpoint: str):
    """Função auxiliar para buscar dados da nossa API FastAPI."""
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()  # Lança um erro para status 4xx/5xx
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao conectar com a API: {e}")
        return []

st.title("📊 Painel Administrativo - Plataforma PBL")
st.markdown("Bem-vindo ao painel de gestão do PBL para o Agronegócio.")

# --- Métricas do Dashboard ---
col1, col2, col3 = st.columns(3)

# Os dados agora vêm da API
total_usuarios_data = get_data_from_api("usuarios/total")
conteudos = get_data_from_api("conteudos")
agendamentos = get_data_from_api("liberacoes-historico")

# Tratamento de erro caso a API não retorne dados
total_usuarios = total_usuarios_data.get('total', 0) if total_usuarios_data else 0
agendamentos_pendentes = [a for a in agendamentos if not a.get("liberado")] if agendamentos else []

with col1:
    st.metric("👥 Total de Usuários", total_usuarios)
with col2:
    st.metric("📚 Total de Conteúdos Ativos", len(conteudos) if conteudos else 0)
with col3:
    st.metric("⏳ Agendamentos Pendentes", len(agendamentos_pendentes))

st.divider()
st.info("💡 Use o menu lateral para agendar as liberações de conteúdo para as turmas.")