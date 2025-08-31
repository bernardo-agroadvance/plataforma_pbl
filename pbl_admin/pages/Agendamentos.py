# pbl_admin/pages/Agendamentos.py
import streamlit as st
import requests
import os
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")

# Garante que a URL da API seja carregada do .env
API_URL = os.getenv("FASTAPI_API_URL", "http://localhost:8000") + "/api/admin"

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
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao enviar dados para a API: {e.response.text if e.response else e}")
        return None

st.title("🗓️ Agendamento de Liberações")

# Carrega dados iniciais da API
conteudos = get_data_from_api("conteudos")
turmas_disponiveis = get_data_from_api("turmas")
historico = get_data_from_api("liberacoes-historico")

if conteudos is None or turmas_disponiveis is None:
    st.warning("Não foi possível carregar os dados iniciais. Verifique se a API está no ar e se o .env está correto.")
    st.stop()

modulos = sorted(list(set(c["modulo"] for c in conteudos)))

with st.form("agendamento_form"):
    st.subheader("Novo Agendamento")
    col1, col2 = st.columns(2)
    
    with col1:
        modulo_selecionado = st.selectbox("📚 Módulo", modulos)
        conteudos_do_modulo = [c for c in conteudos if c["modulo"] == modulo_selecionado and c.get("aula")]

        # --- CORREÇÃO AQUI ---
        # Só mostra o selectbox de aulas se houver aulas para o módulo
        if conteudos_do_modulo:
            aula_selecionada_obj = st.selectbox(
                "🎯 Aula (Microdesafio)",
                conteudos_do_modulo,
                format_func=lambda c: c.get("aula", "Aula sem nome")
            )
        else:
            st.warning("Nenhuma aula (microdesafio) encontrada para este módulo.")
            aula_selecionada_obj = None # Define como None se não houver aulas
    
    with col2:
        turmas_selecionadas = st.multiselect("👥 Turmas", turmas_disponiveis)
        data_liberacao = st.date_input("📅 Data de Liberação", value=datetime.now())
        hora_liberacao = st.time_input("⏰ Hora de Liberação", value=datetime.now().time())

    # O botão de submit do formulário
    submitted = st.form_submit_button("✅ Agendar Liberação")

    if submitted:
        # Verifica se todos os dados necessários foram selecionados
        if not all([modulo_selecionado, aula_selecionada_obj, turmas_selecionadas]):
            st.warning("Todos os campos são obrigatórios.")
        else:
            data_hora_final = datetime.combine(data_liberacao, hora_liberacao)
            payload = {
                "conteudo_id": aula_selecionada_obj["id"],
                "modulo": modulo_selecionado,
                "aula": aula_selecionada_obj["aula"],
                "turmas": turmas_selecionadas,
                "data_iso": data_hora_final.isoformat(),
            }
            resultado = post_data_to_api("liberar", payload)
            if resultado:
                st.success("🎉 Liberação agendada com sucesso!")
                st.rerun()

st.divider()

st.subheader("Histórico de Agendamentos")
if historico:
    df = pd.DataFrame(historico)
    df_display = df[['modulo', 'aula', 'turmas', 'data_liberacao', 'hora_liberacao', 'liberado']]
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum agendamento encontrado.")