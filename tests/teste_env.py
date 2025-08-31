import os
from dotenv import load_dotenv

load_dotenv()

print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_API_KEY:", os.getenv("SUPABASE_API_KEY"))
