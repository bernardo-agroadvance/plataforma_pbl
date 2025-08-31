# fastapi_backend/routers/respostas.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..avaliador import avaliar_resposta_com_ia
from ..db import get_supabase_client
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/respostas", tags=["respostas"])

class AvaliacaoRequest(BaseModel):
    cpf: str
    desafio_id: str
    resposta: str
    tentativa: int

@router.post("/avaliar")
def avaliar_resposta_endpoint(payload: AvaliacaoRequest):
    """ Rota para avaliação de uma resposta, sem registro no banco. """
    supabase = get_supabase_client()
    desafio = supabase.table("PBL - desafios").select("texto_desafio").eq("id", payload.desafio_id).single().execute().data
    if not desafio:
        raise HTTPException(status_code=404, detail="Desafio não encontrado.")

    texto_desafio = desafio["texto_desafio"]
    nota, feedback, sugestao = avaliar_resposta_com_ia(payload.resposta, texto_desafio, payload.tentativa)

    return {"nota": nota, "feedback": feedback, "sugestao": sugestao}

@router.post("/registrar")
def registrar_resposta_endpoint(payload: AvaliacaoRequest):
    """ Avalia e registra uma nova tentativa de resposta no banco de dados. """
    supabase = get_supabase_client()
    try:
        desafio = supabase.table("PBL - desafios").select("texto_desafio, conteudo_id").eq("id", payload.desafio_id).single().execute().data
        if not desafio:
            raise HTTPException(status_code=404, detail="Desafio não encontrado.")

        texto_desafio = desafio["texto_desafio"]
        conteudo_id = desafio["conteudo_id"]

        nota, feedback, sugestao = avaliar_resposta_com_ia(payload.resposta, texto_desafio, payload.tentativa)

        supabase.table("PBL - respostas").insert({
            "id": str(uuid4()),
            "cpf": payload.cpf,
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