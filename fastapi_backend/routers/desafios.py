# fastapi_backend/routers/desafios.py
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query # Adicione Query
from typing import Optional # Adicione Optional
from ..gerar_desafios import gerar_todos_os_desafios
from ..db import get_supabase_client

router = APIRouter(prefix="/desafios", tags=["desafios"])

# ROTA NOVA - ADICIONE ESTE BLOCO
@router.get("") # Usamos "" para corresponder a GET /api/desafios
def listar_desafios_por_cpf(cpf: str = Query(...)):
    """ Lista todos os desafios gerados para um determinado CPF. """
    supabase = get_supabase_client()
    try:
        resp = supabase.table("PBL - desafios").select("*").eq("cpf", cpf).execute()
        return resp.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar desafios: {e}")


@router.post("/gerar/{cpf}")
def gerar_desafios_endpoint(cpf: str, background_tasks: BackgroundTasks):
    """ Inicia a geração de todos os desafios para um CPF em background. """
    background_tasks.add_task(gerar_todos_os_desafios, cpf)
    return {"status": "agendado", "mensagem": "Processo de geração de desafios iniciado."}

@router.get("/status/{cpf}")
def status_desafios(cpf: str):
    """ Verifica se algum desafio já foi liberado para o aluno. """
    supabase = get_supabase_client()
    try:
        resp = (
            supabase.table("PBL - desafios")
            .select("id", count="exact")
            .eq("cpf", cpf)
            .eq("desafio_liberado", True)
            .limit(1)
            .execute()
        )
        liberado = resp.count > 0 if resp.count is not None else False
        return {"liberado": liberado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar desafios: {e}")