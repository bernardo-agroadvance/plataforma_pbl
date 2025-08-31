# fastapi_backend/routers/respostas.py
from fastapi import APIRouter, HTTPException, Depends # Adicione Depends
from typing import Optional # Adicione Optional
from pydantic import BaseModel
from ..avaliador import avaliar_resposta_com_ia
from ..db import get_supabase_client
from ..security import get_current_user_cpf # Importe a função de segurança
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/respostas", tags=["respostas"])

class AvaliacaoRequest(BaseModel):
    # Removido cpf, pois virá do cabeçalho
    desafio_id: str
    resposta: str
    tentativa: int

# ROTA NOVA - ADICIONE ESTE BLOCO
@router.get("/resumo")
def get_respostas_resumo(cpf: str = Depends(get_current_user_cpf)):
    """ Retorna um resumo de todas as respostas enviadas pelo usuário logado. """
    supabase = get_supabase_client()
    try:
        data = supabase.table("PBL - respostas").select("*").eq("cpf", cpf).execute()
        return data.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/registrar")
def registrar_resposta_endpoint(payload: AvaliacaoRequest, cpf: str = Depends(get_current_user_cpf)):
    """ Avalia e registra uma nova tentativa de resposta no banco de dados. """
    supabase = get_supabase_client()
    try:
        # ... (o resto da função registrar_resposta_endpoint permanece igual)
        desafio = supabase.table("PBL - desafios").select("texto_desafio, conteudo_id").eq("id", payload.desafio_id).single().execute().data
        if not desafio:
            raise HTTPException(status_code=404, detail="Desafio não encontrado.")

        texto_desafio = desafio["texto_desafio"]
        conteudo_id = desafio["conteudo_id"]

        nota, feedback, sugestao = avaliar_resposta_com_ia(payload.resposta, texto_desafio, payload.tentativa)

        supabase.table("PBL - respostas").insert({
            "id": str(uuid4()),
            "cpf": cpf, # Usa o CPF do cabeçalho seguro
            "desafio_id": payload.desafio_id,
            "conteudo_id": conteudo_id,
            "tentativa": payload.tentativa,
            "texto_resposta": payload.resposta,
            "nota": nota,
            "feedback": feedback,
            "resposta_ideal": sugestao,
            "data_envio": datetime.utcnow().isoformat(),
            "tentativa_finalizada": payload.tentativa >= 3
        }).execute()

        return {"nota": nota, "feedback": feedback, "sugestao": sugestao}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))