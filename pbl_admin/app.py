import streamlit as st
from backend.db import get_usuarios, get_conteudos
from backend.liberador import liberar_agendamentos_pendentes
from supabase import Client
from backend.db import supabase

st.set_page_config(page_title="Painel PBL", layout="wide")
st.title("📊 Painel Administrativo - Plataforma PBL")

st.markdown("Bem-vindo ao painel de gestão do PBL para o Agronegócio.")

# Resumo de status
col1, col2, col3 = st.columns(3)

with col1:
    usuarios = get_usuarios()
    st.metric("👥 Total de Usuários", len(usuarios))

with col2:
    conteudos = get_conteudos()
    st.metric("📚 Total de Conteúdos", len(conteudos))

with col3:
    agendamentos_pendentes = supabase.table("PBL - liberacoes_agendadas") \
        .select("id").eq("liberado", False).execute().data
    st.metric("⏳ Agendamentos Pendentes", len(agendamentos_pendentes))

st.divider()

# Ações rápidas
st.subheader("⚙️ Ações rápidas")

col4, col5 = st.columns(2)

with col4:
    if st.button("🔄 Forçar liberação de pendentes agora"):
        liberar_agendamentos_pendentes()
        st.success("✅ Liberações aplicadas com sucesso.")

with col5:
    st.info("💡 Use o menu lateral para navegar pelas funcionalidades:\n\n"
            "- Agendar liberações\n"
            "- Visualizar status dos alunos\n"
            "- Gerenciar desafios\n"
            "- Futuras estatísticas de desempenho")