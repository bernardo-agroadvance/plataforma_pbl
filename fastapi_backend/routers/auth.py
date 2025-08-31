# fastapi_backend/routers/auth.py
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from ..db import get_supabase_client

router = APIRouter(prefix="/auth", tags=["auth"])

class CpfLogin(BaseModel):
    cpf: str = Field(..., pattern=r"^\d{11}$")

@router.post("/cpf-login")
def auth_cpf_login(payload: CpfLogin):
    cpf = payload.cpf
    supabase = get_supabase_client()

    user_query = supabase.table("PBL - usuarios").select("cpf, nome, role").eq("cpf", cpf).limit(1).execute()
    if not user_query.data:
        raise HTTPException(status_code=401, detail="CPF não encontrado.")
    
    user = user_query.data[0]
    return {"ok": True, "user": {"nome": user.get("nome"), "role": user.get("role")}}