# FastAPI Backend

## Setup
```powershell
cd plataforma_pbl\fastapi_backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
copy .env.example .env  # edite os valores
pip install -r ..\requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```