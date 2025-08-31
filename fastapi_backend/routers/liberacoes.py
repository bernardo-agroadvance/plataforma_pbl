# fastapi_backend/routers/liberacoes.py
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, time as dtime
from ..db import get_supabase_client

router = APIRouter(prefix="/liberacoes", tags=["liberacoes"])

@router.get("")
def get_liberacoes_por_turma(turma: str = Query(..., description="Código da turma")):
    supabase = get_supabase_client()
    try:
        r = (
            supabase.table('PBL - liberacoes_agendadas')
              .select('conteudo_id, data_liberacao, hora_liberacao, liberado')
              .contains('turmas', [turma]) # Verifica se a turma está no array
              .execute()
        )
        rows = r.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar liberações: {e}")

    # Processa para ver o que já deveria estar liberado
    today = datetime.now().date()
    now_t = datetime.now().time()
    out = []
    for row in rows:
        try:
            d_obj = datetime.fromisoformat(row.get("data_liberacao", "").split("T")[0]).date()
            t_obj = dtime.fromisoformat(row.get("hora_liberacao", "00:00:00"))
            
            liberado_flag = bool(row.get("liberado"))
            liberado_por_tempo = (d_obj < today) or (d_obj == today and t_obj <= now_t)
            
            if liberado_flag or liberado_por_tempo:
                out.append({"conteudo_id": row.get("conteudo_id")})
        except Exception:
            continue
    return out