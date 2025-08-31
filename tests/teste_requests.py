import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

# URL da API REST
endpoint = f"{url}/rest/v1/PBL%20-%20usuarios?select=*"

res = requests.get(endpoint, headers=headers)

print("Status:", res.status_code)
print("Resposta:", res.json())
