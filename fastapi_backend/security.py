# fastapi_backend/security.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader

# Vamos ler o CPF de um cabeçalho customizado chamado 'X-User-CPF'
cpf_header_scheme = APIKeyHeader(name="X-User-CPF", auto_error=False)

def get_current_user_cpf(cpf: str = Depends(cpf_header_scheme)):
    """
    Dependência para rotas protegidas. Valida a presença do CPF no cabeçalho.
    Retorna o CPF se ele existir, caso contrário, lança HTTPException.
    """
    if cpf is None:
        raise HTTPException(
            status_code=401,
            detail="Não autenticado. Cabeçalho X-User-CPF ausente.",
        )
    return cpf