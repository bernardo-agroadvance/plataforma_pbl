# fastapi_backend/routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from ..db import get_supabase_client
from ..security import get_current_user_cpf

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

class UsuarioPayload(BaseModel):
    cargo: Optional[str] = None
    regiao: Optional[str] = None
    cadeia: Optional[str] = None
    desafios: Optional[str] = None
    observacoes: Optional[str] = None
    formulario_finalizado: Optional[bool] = None

@router.post("")
def update_usuario_form(payload: UsuarioPayload, cpf: str = Depends(get_current_user_cpf)):
    """ Atualiza os dados do formulário do usuário logado. """
    supabase = get_supabase_client()
    try:
        data_to_update = payload.model_dump(exclude_unset=True)
        if not data_to_update:
            raise HTTPException(status_code=400, detail="Nenhum dado para atualizar.")

        response = supabase.table("PBL - usuarios").update(data_to_update).eq("cpf", cpf).execute()
        return {"ok": True, "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_usuario_details(
    cpf: str = Depends(get_current_user_cpf), # Renomeado para 'cpf' para clareza
    fields: Optional[str] = Query(None, description="Campos a serem retornados, separados por vírgula")
):
    """ Retorna detalhes do usuário logado. """
    supabase = get_supabase_client()
    
    select_fields = "*"
    if fields:
        allowed_fields = {"nome", "cpf", "curso", "turma", "cargo", "regiao", "cadeia", "desafios", "observacoes", "formulario_finalizado"}
        select_fields = ",".join([f for f in fields.split(',') if f.strip() in allowed_fields])
        if not select_fields:
            select_fields = "cpf,curso,turma,formulario_finalizado"

    try:
        # AQUI ESTÁ A MUDANÇA:
        # Trocamos .single() por .execute() para garantir que o resultado seja sempre uma lista.
        user_res = supabase.table("PBL - usuarios").select(select_fields).eq("cpf", cpf).execute()
        
        # Se a consulta falhar ou não retornar dados, retornamos uma lista vazia.
        if not user_res or not user_res.data:
            return []
            
        return user_res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))