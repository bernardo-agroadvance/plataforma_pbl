# fastapi_backend/db.py
import os
from supabase import create_client, Client
from functools import lru_cache

@lru_cache
def get_supabase_client() -> Client:
    """
    Cria e retorna um cliente Supabase, utilizando cache para evitar
    recriações desnecessárias. As credenciais são lidas das variáveis
    de ambiente.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_API_KEY")

    if not url or not key:
        raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY são necessárias.")

    return create_client(url, key)