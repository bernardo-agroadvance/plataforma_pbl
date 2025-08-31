# fastapi_backend/security.py
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Carrega as variáveis de ambiente
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET não definido no .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

# Esquema de autenticação OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Contexto para hashing de senhas (embora não estejamos usando senhas, é uma boa prática)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception: HTTPException):
    """Verifica e decodifica um token JWT."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        cpf: str = payload.get("sub")
        if cpf is None:
            raise credentials_exception
        return cpf
    except JWTError:
        raise credentials_exception

def get_current_user_cpf(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependência para obter o CPF do usuário a partir do token JWT.
    Usado para proteger as rotas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

def get_current_admin_user(token: str = Depends(oauth2_scheme)):
    """
    Dependência para rotas que exigem privilégios de administrador.
    (Esta função precisaria de uma lógica para verificar a role do usuário no banco de dados)
    """
    cpf = get_current_user_cpf(token)
    # Exemplo: Adicionar uma verificação de role aqui
    # from .db import get_supabase_client
    # supabase = get_supabase_client()
    # user = supabase.table("PBL - usuarios").select("role").eq("cpf", cpf).single().execute()
    # if not user.data or user.data.get("role") != "admin":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer privilégios de administrador.")
    return cpf