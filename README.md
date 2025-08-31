# Plataforma PBL — Monorepo

```
plataforma_pbl/
  fastapi_backend/     # API (FastAPI)
  frontend/            # Web (Vite/React)
  pbl_admin/           # Admin (Streamlit)
scripts/               # utilitários (PowerShell)
```

Regras:
- **Sem `.env` na raiz**. Cada app tem seu `.env` (commit apenas `.env.example`).
- **Service Role só no backend/admin**; front usa apenas anon.
- **Venv por app**.