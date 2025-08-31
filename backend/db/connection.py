import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_API_KEY")

    if not url or not key:
        raise ValueError("Verifique se SUPABASE_URL e SUPABASE_API_KEY estão definidos no .env")

    return create_client(url, key)

# Cliente global (pode ser importado em outros módulos)
supabase = get_supabase_client()
