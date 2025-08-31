import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API_KEY")

print("URL:", url)
print("KEY começa com:", key[:10])

supabase = create_client(url, key)
resposta = supabase.table("PBL - usuarios").select("*").limit(1).execute()

print("Dados recebidos:", resposta.data)
