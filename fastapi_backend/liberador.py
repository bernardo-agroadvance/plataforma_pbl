# fastapi_backend/liberador.py
from .db import get_supabase_client

def forcar_liberacao_imediata(agendamento: dict):
    """
    Recebe um registro de agendamento e força a liberação dos desafios
    correspondentes para os alunos das turmas especificadas.
    """
    print(f"[LIBERADOR] Forçando liberação para agendamento ID: {agendamento.get('id')}")
    supabase = get_supabase_client()
    
    conteudo_id = agendamento.get("conteudo_id")
    turmas = agendamento.get("turmas", [])
    aula = agendamento.get("aula")
    tipo_desejado = "micro" if aula else "macro"

    if not turmas or not conteudo_id:
        print("[LIBERADOR] Aviso: Turmas ou ID do conteúdo ausentes. Nenhuma liberação forçada.")
        return

    # 1. Encontrar os CPFs dos alunos nas turmas
    alunos_res = supabase.table("PBL - usuarios").select("cpf").in_("turma", turmas).execute()
    if not (alunos_res and alunos_res.data):
        print(f"[LIBERADOR] Nenhum aluno encontrado para as turmas {turmas}.")
        return
    
    cpfs = [aluno['cpf'] for aluno in alunos_res.data]
    print(f"[LIBERADOR] Encontrados {len(cpfs)} alunos para liberar o desafio.")

    # 2. Atualizar o status 'desafio_liberado' na tabela de desafios para esses alunos
    update_res = supabase.table("PBL - desafios") \
        .update({"desafio_liberado": True}) \
        .in_("cpf", cpfs) \
        .eq("conteudo_id", conteudo_id) \
        .eq("tipo", tipo_desejado) \
        .execute()

    print(f"[LIBERADOR] {len(update_res.data)} desafios do tipo '{tipo_desejado}' foram liberados para o conteúdo '{conteudo_id}'.")