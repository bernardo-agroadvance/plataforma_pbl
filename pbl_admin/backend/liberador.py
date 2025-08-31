from backend.db import supabase
from datetime import datetime

def liberar_agendamentos_pendentes():
    """Processa agendamentos vencidos e atualiza os desafios correspondentes"""
    agora = datetime.now()

    agendamentos = supabase.table("PBL - liberacoes_agendadas") \
        .select("*") \
        .eq("liberado", False) \
        .execute().data

    print(f"🔍 Encontrados {len(agendamentos)} agendamentos pendentes.")

    for agendamento in agendamentos:
        try:
            # Monta datetime da liberação
            data_str = agendamento["data_liberacao"]
            hora_str = agendamento["hora_liberacao"]

            try:
                liberacao_datetime = datetime.strptime(f"{data_str} {hora_str}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                liberacao_datetime = datetime.strptime(f"{data_str} {hora_str}", "%Y-%m-%d %H:%M")

            if agora < liberacao_datetime:
                continue  # ainda não é hora

            conteudo_id = agendamento["conteudo_id"]
            turma_lista = agendamento.get("turmas", [])
            aula = agendamento.get("aula")  # se for None, é macro

            # Buscar CPFs das turmas
            alunos = supabase.table("PBL - usuarios").select("cpf").in_("turma", turma_lista).execute().data
            cpfs = [a["cpf"] for a in alunos]

            if not cpfs:
                print(f"⚠️ Nenhum aluno encontrado para turmas {turma_lista}")
                continue

            tipo_desejado = "macro" if aula is None else "micro"

            for cpf in cpfs:
                # Atualiza apenas os desafios relevantes
                supabase.table("PBL - desafios").update({"desafio_liberado": True}) \
                    .eq("cpf", cpf) \
                    .eq("conteudo_id", conteudo_id) \
                    .eq("tipo", tipo_desejado) \
                    .execute()

            # Marca agendamento como processado
            supabase.table("PBL - liberacoes_agendadas").update({"liberado": True}) \
                .eq("id", agendamento["id"]).execute()

            print(f"✅ Liberado {tipo_desejado} para {len(cpfs)} usuários (Agendamento ID {agendamento['id']})")

        except Exception as e:
            print(f"❌ Erro ao processar agendamento {agendamento.get('id')}: {e}")

def forcar_liberacao_agendamento(agendamento):
    """Libera os desafios de um único agendamento, independente da data"""
    conteudo_id = agendamento["conteudo_id"]
    turma_lista = agendamento.get("turmas", [])
    aula = agendamento.get("aula")
    tipo_desejado = "macro" if aula is None else "micro"

    alunos = supabase.table("PBL - usuarios").select("cpf").in_("turma", turma_lista).execute().data
    cpfs = [a["cpf"] for a in alunos]

    if not cpfs:
        print(f"⚠️ Nenhum aluno encontrado para turmas {turma_lista}")
        return

    for cpf in cpfs:
        supabase.table("PBL - desafios").update({"desafio_liberado": True}) \
            .eq("cpf", cpf) \
            .eq("conteudo_id", conteudo_id) \
            .eq("tipo", tipo_desejado) \
            .execute()

    supabase.table("PBL - liberacoes_agendadas").update({"liberado": True}) \
        .eq("id", agendamento["id"]) \
        .execute()

    print(f"✅ Desafios {tipo_desejado} liberados para {len(cpfs)} CPFs")

