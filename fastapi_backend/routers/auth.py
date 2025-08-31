# fastapi_backend/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from ..db import get_supabase_client
from ..security import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str

class CpfLogin(BaseModel):
    cpf: str

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login que recebe CPF no campo 'username' e retorna um token JWT.
    """
    cpf = form_data.username
    supabase = get_supabase_client()

    user_query = supabase.table("PBL - usuarios").select("cpf, nome, role").eq("cpf", cpf).limit(1).execute()
    
    if not user_query.data:
        raise HTTPException(status_code=401, detail="CPF não encontrado ou inválido.")
    
    access_token_expires = timedelta(minutes=60 * 8) # 8 horas
    access_token = create_access_token(
        data={"sub": cpf}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}