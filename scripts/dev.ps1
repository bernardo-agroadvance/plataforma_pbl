# Abre 3 janelas: backend (FastAPI), frontend (Vite) e admin (Streamlit)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Backend
Start-Process powershell -ArgumentList `
  'cd ..\fastapi_backend; `
   .\.venv\Scripts\Activate.ps1 2>$null; `
   if (-not (Test-Path .venv)) { py -3.11 -m venv .venv }; `
   .\.venv\Scripts\Activate.ps1; `
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000' `
  -WorkingDirectory $ScriptDir

# Frontend
Start-Process powershell -ArgumentList `
  'cd ..\frontend; `
   if (-not (Test-Path node_modules)) { npm install }; `
   npm run dev' `
  -WorkingDirectory $ScriptDir

# Admin
Start-Process powershell -ArgumentList `
  'cd ..\pbl_admin; `
   .\.venv\Scripts\Activate.ps1 2>$null; `
   if (-not (Test-Path .venv)) { py -3.11 -m venv .venv }; `
   .\.venv\Scripts\Activate.ps1; `
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501' `
  -WorkingDirectory $ScriptDir
