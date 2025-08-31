# pbl_admin/pages/Agendamentos.py
import streamlit as st
import requests
import os
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")

API_URL = os.getenv("FASTAPI_API_URL", "http://localhost:8000") + "/api/admin"

# Cacheia os dados para não ficar chamando a API toda hora
@st.cache_data(ttl=60)
def get_data_from_api(endpoint: str):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao buscar dados da API: {e}")
        return None

def post_data_to_api(endpoint: str, data: dict):
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=data)
        response.raise_for_status()
        st.cache_data.clear() # Limpa o cache após uma nova liberação
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao enviar dados para a API: {e.response.text if e.response else e}")
        return None

st.title("🗓️ Agendamento de Liberações")

conteudos = get_data_from_api("conteudos")
turmas_disponiveis = get_data_from_api("turmas")

if conteudos is None or turmas_disponiveis is None:
    st.warning("Não foi possível carregar os dados. Verifique se a API está no ar.")
    st.stop()

modulos = sorted(list(set(c["modulo"] for c in conteudos if "modulo" in c)))

with st.form("agendamento_form"):
    st.subheader("Novo Agendamento")

    modulo_selecionado = st.selectbox("📚 Módulo", modulos)

    # Filtra aulas apenas para o módulo selecionado
    aulas_disponiveis = [c for c in conteudos if c.get("modulo") == modulo_selecionado and c.get("aula")]

    if aulas_disponiveis:
        aula_selecionada = st.selectbox(
            "🎯 Aula (Microdesafio)",
            aulas_disponiveis,
            format_func=lambda c: c.get("aula", "Aula sem nome")
        )
        turmas_selecionadas = st.multiselect("👥 Turmas", turmas_disponiveis)
        data_liberacao = st.date_input("📅 Data de Liberação", value=datetime.now())
        hora_liberacao = st.time_input("⏰ Hora de Liberação", value=datetime.now().time())
    else:
        st.info(f"Nenhuma aula encontrada para o módulo '{modulo_selecionado}'.")
        aula_selecionada = None
        turmas_selecionadas = []

    submitted = st.form_submit_button("✅ Agendar Liberação")

    if submitted:
        if not all([aula_selecionada, turmas_selecionadas]):
            st.warning("Por favor, selecione uma aula e pelo menos uma turma.")
        else:
            data_hora_final = datetime.combine(data_liberacao, hora_liberacao)
            payload = {
                "conteudo_id": aula_selecionada["id"],
                "modulo": aula_selecionada["modulo"],
                "aula": aula_selecionada["aula"],
                "turmas": turmas_selecionadas,
                "data_iso": data_hora_final.isoformat(),
            }
            resultado = post_data_to_api("liberar", payload)
            if resultado:
                st.success("🎉 Liberação agendada com sucesso!")
                st.rerun()

st.divider()
st.subheader("Histórico de Agendamentos")
historico = get_data_from_api("liberacoes-historico")
if historico:
    df = pd.DataFrame(historico)
    df_display = df[['modulo', 'aula', 'turmas', 'data_liberacao', 'hora_liberacao', 'liberado']]
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum agendamento encontrado.")