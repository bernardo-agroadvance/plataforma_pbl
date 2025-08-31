# fastapi_backend/routers/conteudos.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..db import get_supabase_client

router = APIRouter(prefix="/conteudos", tags=["conteudos"])

ALLOWED_CONTEUDO_FIELDS = {"id", "modulo", "aula", "ementa", "ativo"}

@router.get("")
def get_conteudos(
    fields: Optional[str] = Query("id,modulo,aula", description="Campos separados por vírgula"),
    only_active: bool = Query(True, description="Retornar apenas conteúdos ativos"),
):
    supabase = get_supabase_client()
    req = [f.strip() for f in fields.split(",") if f.strip()]
    cols = [f for f in req if f in ALLOWED_CONTEUDO_FIELDS]
    if not cols:
        cols = ["id", "modulo", "aula"] # Default
    
    select_cols = ",".join(sorted(set(cols)))

    try:
        query = supabase.table('PBL - conteudo').select(select_cols)
        if only_active:
            query = query.eq("ativo", True)
        r = query.execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar conteúdos: {e}")