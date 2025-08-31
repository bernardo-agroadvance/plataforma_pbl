# fastapi_backend/routers/admin.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime
from ..db import get_supabase_client
from ..liberador import forcar_liberacao_imediata
from ..security import get_current_admin_user # Importa a dependência de segurança

router = APIRouter(tags=["admin"], dependencies=[Depends(get_current_admin_user)]) # Protege todas as rotas deste router

class LiberarReq(BaseModel):
    conteudo_id: str
    modulo: str
    aula: str
    turmas: List[str]
    data_iso: str

def _parse_iso_to_date_time(iso_s: str):
    try:
        dt = datetime.fromisoformat(iso_s.strip().replace("Z", "+00:00"))
        d = dt.date().isoformat()
        t = dt.time().replace(microsecond=0).strftime("%H:%M:%S")
        return d, t
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de data_iso inválido")

@router.get("/conteudos")
def admin_get_conteudos():
    supabase = get_supabase_client()
    r = supabase.table("PBL - conteudo").select("id, modulo, aula, ativo").eq("ativo", True).order("modulo").order("aula").execute()
    return r.data or []

@router.get("/turmas")
def admin_get_turmas():
    supabase = get_supabase_client()
    try:
        r2 = supabase.table('PBL - usuarios').select('turma').execute()
        turmas = sorted({row['turma'] for row in (r2.data or []) if row.get('turma')})
        return turmas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/liberacoes-historico")
def admin_get_historico():
    supabase = get_supabase_client()
    r = supabase.table('PBL - liberacoes_agendadas').select('*').order('created_at', desc=True).limit(100).execute()
    return r.data or []

@router.get("/usuarios/total")
def admin_get_total_usuarios():
    supabase = get_supabase_client()
    try:
        response = supabase.table("PBL - usuarios").select("id", count="exact").execute()
        return {"total": response.count if response.count is not None else 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/liberar")
def admin_liberar_conteudo(req: LiberarReq):
    supabase = get_supabase_client()
    data_liberacao, hora_liberacao = _parse_iso_to_date_time(req.data_iso)
    
    # Payload define 'liberado' como True imediatamente
    payload = {
        "conteudo_id": req.conteudo_id, "modulo": req.modulo, "aula": req.aula,
        "turmas": req.turmas, "data_liberacao": data_liberacao,
        "hora_liberacao": hora_liberacao, "liberado": True,
    }

    # Insere o registro de agendamento já como liberado
    ins_res = supabase.table('PBL - liberacoes_agendadas').insert(payload).execute()
    
    if not (ins_res and ins_res.data):
        raise HTTPException(status_code=500, detail="Falha ao criar o registro de agendamento.")

    novo_agendamento = ins_res.data[0]
    
    # Chama a função para forçar a liberação dos desafios associados
    try:
        forcar_liberacao_imediata(novo_agendamento)
    except Exception as e:
        # Retorna um erro informando sobre a falha na liberação imediata.
        raise HTTPException(status_code=500, detail=f"Agendamento criado, mas falha na liberação imediata: {e}")

    return novo_agendamento