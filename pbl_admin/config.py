# pbl_admin/config.py (template seguro)
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_API_KEY")
)
SUPABASE_API_KEY = SUPABASE_SERVICE_ROLE_KEY 

FASTAPI_API_URL = os.getenv("FASTAPI_API_URL", "http://localhost:8000")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY em pbl_admin/.env")
