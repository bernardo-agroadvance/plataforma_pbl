# fastapi_backend/routers/admin.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime
from ..db import get_supabase_client
from ..security import get_current_user_cpf # Futuramente, para proteger o admin

router = APIRouter(tags=["admin"])

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
    # cpf: str = Depends(get_current_user_cpf) # Descomente para proteger
    supabase = get_supabase_client()
    r = supabase.table("PBL - conteudo").select("id, modulo, aula, ativo").eq("ativo", True).order("modulo").order("aula").execute()
    return r.data or []

@router.get("/turmas")
def admin_get_turmas():
    # cpf: str = Depends(get_current_user_cpf) # Descomente para proteger
    supabase = get_supabase_client()
    try:
        # Removemos a chamada rpc() e usamos a lógica de fallback diretamente
        r2 = supabase.table('PBL - usuarios').select('turma').execute()
        turmas = sorted({row['turma'] for row in (r2.data or []) if row.get('turma')})
        return turmas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/liberacoes-historico")
def admin_get_historico():
    # cpf: str = Depends(get_current_user_cpf) # Descomente para proteger
    supabase = get_supabase_client()
    r = supabase.table('PBL - liberacoes_agendadas').select('*').order('created_at', desc=True).limit(100).execute()
    return r.data or []

@router.post("/liberar")
def admin_liberar_conteudo(req: LiberarReq):
    # cpf: str = Depends(get_current_user_cpf) # Descomente para proteger
    supabase = get_supabase_client()
    data_liberacao, hora_liberacao = _parse_iso_to_date_time(req.data_iso)
    payload = {
        "conteudo_id": req.conteudo_id, "modulo": req.modulo, "aula": req.aula,
        "turmas": req.turmas, "data_liberacao": data_liberacao,
        "hora_liberacao": hora_liberacao, "liberado": False,
    }
    ins = supabase.table('PBL - liberacoes_agendadas').insert(payload).execute()
    if getattr(ins, "error", None):
        raise HTTPException(status_code=500, detail=str(ins.error))
    return ins.data or []

@router.get("/usuarios/total")
def admin_get_total_usuarios():
    supabase = get_supabase_client()
    try:
        # Usamos `count='exact'` para apenas contar as linhas, o que é mais eficiente
        response = supabase.table("PBL - usuarios").select("id", count="exact").execute()
        return {"total": response.count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))