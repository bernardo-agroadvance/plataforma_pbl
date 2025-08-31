from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_API_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def get_usuarios():
    """Retorna todos os usuários cadastrados"""
    response = supabase.table("PBL - usuarios").select("*").execute()
    return response.data

def get_conteudos():
    """Retorna os conteúdos disponíveis (modulo, aula, conteudo_id)"""
    response = supabase.table("PBL - conteudo").select("*").eq("ativo", True).execute()
    return response.data

def get_turmas():
    """Retorna a lista única de turmas existentes"""
    response = supabase.table("PBL - usuarios").select("turma").execute()
    turmas = {row["turma"] for row in response.data if row["turma"]}
    return sorted(turmas)

def agendar_liberacao(conteudo_id, modulo, aula, turmas, data, hora):
    payload = {
        "conteudo_id": conteudo_id,
        "modulo": modulo,
        "aula": aula,  # None se for macro
        "turmas": turmas,
        "data_liberacao": data,
        "hora_liberacao": hora,
        "liberado": False
    }
    result = supabase.table("PBL - liberacoes_agendadas").insert(payload).execute()
    return result.data[0]  # retorna o agendamento recém-criado


