import streamlit as st
from backend.db import get_conteudos, get_turmas, agendar_liberacao
from datetime import date, time
from backend.liberador import forcar_liberacao_agendamento

st.title("🗓️ Agendamento de Liberações")

tipo_liberacao = st.radio("Tipo de Liberação", options=["Microdesafio", "Macrodesafio"], horizontal=True)

conteudos = get_conteudos()
turmas_disponiveis = get_turmas()

modulos = sorted(set(c["modulo"] for c in conteudos))
modulo_selecionado = st.selectbox("📚 Módulo", modulos)

# Filtrar conteúdos do módulo
conteudos_do_modulo = [c for c in conteudos if c["modulo"] == modulo_selecionado]

# AULA — apenas se for micro
aula_selecionada = None
if tipo_liberacao == "Microdesafio":
    aulas = sorted(set(c["aula"] for c in conteudos_do_modulo if c["aula"]))
    aula_selecionada = st.selectbox("🎯 Aula", aulas)

# Selecionar conteúdo
conteudo_correspondente = next(
    (c for c in conteudos_do_modulo if c["aula"] == aula_selecionada) if aula_selecionada else
    (c for c in conteudos_do_modulo if c["aula"] is None),
    None
)

if not conteudo_correspondente:
    st.error("❌ Não foi possível encontrar o conteúdo correspondente.")
else:
    conteudo_id = conteudo_correspondente["id"]

    turmas_selecionadas = st.multiselect("👥 Turmas", turmas_disponiveis)
    data = st.date_input("📅 Data de Liberação", min_value=date.today())
    hora = st.time_input("⏰ Hora de Liberação", value=time(8, 0))

    if st.button("✅ Agendar Liberação"):
        if not turmas_selecionadas:
            st.warning("Você precisa selecionar ao menos uma turma.")
        else:
            novo_agendamento = agendar_liberacao(
                conteudo_id=conteudo_id,
                modulo=modulo_selecionado,
                aula=aula_selecionada,
                turmas=turmas_selecionadas,
                data=str(data),
                hora=str(hora)
            )
            forcar_liberacao_agendamento(novo_agendamento)
            st.success("🎉 Liberação agendada e aplicada com sucesso!")
