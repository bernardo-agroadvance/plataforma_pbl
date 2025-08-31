import os
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client
from fastapi_backend.avaliador import avaliar_resposta_com_ia
from collections import defaultdict

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Variáveis de ambiente SUPABASE_URL ou SUPABASE_API_KEY não definidas.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_desafios_liberados(cpf: str):
    try:
        usuario = (
            supabase
            .table("PBL - usuarios")
            .select("turma")
            .eq("cpf", cpf)
            .single()
            .execute()
        ).data

        if not usuario:
            print("Usuário não encontrado.")
            return {}

        turma = usuario["turma"]

        hoje = date.today().isoformat()

        liberacoes = (
            supabase
            .table("PBL - liberacoes_agendadas")
            .select("conteudo_id")
            .eq("turma", turma)
            .lte("data_liberacao", hoje)
            .execute()
        ).data

        conteudos_liberados = {item["conteudo_id"] for item in liberacoes if item["conteudo_id"]}

        desafios = (
            supabase
            .table("PBL - desafios")
            .select("*")
            .eq("cpf", cpf)
            .in_("conteudo_id", list(conteudos_liberados))
            .execute()
        ).data

        if not desafios:
            return {}

        desafios_por_modulo = defaultdict(list)

        for d in desafios:
            conteudo_id = d["conteudo_id"]
            conteudo = (
                supabase
                .table("PBL - conteudo")
                .select("modulo, aula")
                .eq("id", conteudo_id)
                .single()
                .execute()
            ).data or {}

            modulo = conteudo.get("modulo", "Módulo Desconhecido")

            desafio = {
                "id": d["id"],
                "texto_desafio": d["texto_desafio"],
                "aula": conteudo.get("aula", "Aula não encontrada"),
                "modulo": modulo,
                "titulo": d.get("titulo", ""),
                "status_gerado": d.get("status_gerado", ""),
                "desafio_liberado": d.get("desafio_liberado", False)
            }

            desafios_por_modulo[modulo].append(desafio)

        return dict(desafios_por_modulo)

    except Exception as e:
        print(f"Erro ao buscar desafios liberados: {e}")
        return {}


def buscar_tentativas(cpf: str, desafio_id: str) -> int:
    try:
        resposta = (
            supabase
            .table("PBL - respostas")
            .select("id")
            .eq("cpf", cpf)
            .eq("desafio_id", desafio_id)
            .execute()
        )
        return len(resposta.data)
    except Exception as e:
        print(f"Erro ao buscar tentativas: {e}")
        return 0

def registrar_resposta(cpf: str, desafio_id: str, texto_resposta: str, tentativa: int,
                       nota: float, feedback: str, resposta_ideal: str = "") -> bool:
    try:
        desafio = (
            supabase
            .table("PBL - desafios")
            .select("conteudo_id")
            .eq("id", desafio_id)
            .single()
            .execute()
        ).data

        if not desafio:
            print("Desafio não encontrado.")
            return False

        conteudo_id = desafio["conteudo_id"]

        nova_resposta = {
            "cpf": cpf,
            "desafio_id": desafio_id,
            "tentativa": tentativa,
            "texto_resposta": texto_resposta,
            "nota": round(nota, 1),
            "feedback": feedback,
            "resposta_ideal": resposta_ideal,
            "data_envio": datetime.utcnow().isoformat(),
            "conteudo_id": conteudo_id
        }

        supabase.table("PBL - respostas").insert(nova_resposta).execute()
        return True

    except Exception as e:
        print(f"Erro ao registrar resposta: {e}")
        return False

def finalizar_resposta_com_ia(cpf: str, desafio_id: str) -> bool:
    try:
        resposta = (
            supabase
            .table("PBL - respostas")
            .select("id, texto_resposta")
            .eq("cpf", cpf)
            .eq("desafio_id", desafio_id)
            .order("tentativa", desc=True)
            .limit(1)
            .execute()
        ).data

        if not resposta:
            print("Nenhuma tentativa encontrada.")
            return False

        resposta_id = resposta[0]["id"]
        texto_resposta = resposta[0]["texto_resposta"]

        desafio = (
            supabase
            .table("PBL - desafios")
            .select("texto_desafio")
            .eq("id", desafio_id)
            .single()
            .execute()
        ).data

        texto_desafio = desafio["texto_desafio"]

        nota, feedback, resposta_ideal = avaliar_resposta_com_ia(
            resposta_do_aluno=texto_resposta,
            texto_microdesafio=texto_desafio,
            tentativa=3
        )

        update_data = {
            "nota": round(nota, 1),
            "feedback": feedback,
            "resposta_ideal": resposta_ideal,
            "tentativa_finalizada": True
        }

        supabase.table("PBL - respostas").update(update_data).eq("id", resposta_id).execute()
        return True

    except Exception as e:
        print(f"Erro ao finalizar resposta: {e}")
        return False

def buscar_resposta_mais_recente(cpf: str, desafio_id: str):
    try:
        resposta = (
            supabase
            .table("PBL - respostas")
            .select("tentativa_finalizada, resposta_ideal")
            .eq("cpf", cpf)
            .eq("desafio_id", desafio_id)
            .order("tentativa", desc=True)
            .limit(1)
            .execute()
        ).data

        if resposta:
            return resposta[0].get("tentativa_finalizada", False), resposta[0].get("resposta_ideal", "")
        else:
            return False, ""
    except Exception as e:
        print("Erro ao buscar resposta mais recente:", e)
        return False, ""

def atualizar_desafios_liberados_por_data(cpf: str):
    try:
        usuario = supabase.table("PBL - usuarios").select("turma").eq("cpf", cpf).single().execute().data
        if not usuario:
            return False
        turma = usuario["turma"]
        hoje = datetime.utcnow().date().isoformat()

        liberados = supabase.table("PBL - liberacoes_agendadas") \
            .select("conteudo_id, turmas") \
            .eq("liberado", True) \
            .lte("data_liberacao", hoje) \
            .execute().data

        conteudos_liberados = [item["conteudo_id"] for item in liberados if turma in item.get("turmas", [])]

        if not conteudos_liberados:
            return False

        supabase \
            .table("PBL - desafios") \
            .update({"desafio_liberado": True}) \
            .eq("cpf", cpf) \
            .in_("conteudo_id", conteudos_liberados) \
            .execute()

        return True
    except Exception as e:
        print("Erro ao atualizar desafios liberados:", e)
        return False

def desafios_liberados_esperados(cpf: str) -> int:
    try:
        usuario = supabase.table("PBL - usuarios").select("turma").eq("cpf", cpf).single().execute().data
        if not usuario:
            return 0

        turma = usuario["turma"]
        hoje = datetime.utcnow().date().isoformat()

        liberacoes = supabase.table("PBL - liberacoes_agendadas") \
            .select("conteudo_id, turmas") \
            .eq("liberado", True) \
            .lte("data_liberacao", hoje) \
            .execute().data

        conteudos_liberados = [item["conteudo_id"] for item in liberacoes if turma in item.get("turmas", [])]
        return len(conteudos_liberados)
    except Exception as e:
        print("Erro ao contar desafios esperados:", e)
        return 0

def desafios_liberados_gerados(cpf: str) -> int:
    try:
        resposta = (
            supabase
            .from_("PBL - desafios")
            .select("id")
            .eq("cpf", cpf)
            .eq("desafio_liberado", True)
            .execute()
        )
        return len(resposta.data or [])
    except Exception as e:
        print("Erro ao contar desafios gerados:", e)
        return 0