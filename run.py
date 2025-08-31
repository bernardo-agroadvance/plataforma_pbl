# run.py
import uvicorn
import os

if __name__ == "__main__":
    # Obtém a porta do .env ou usa 8000 como padrão
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("fastapi_backend.main:app", host="0.0.0.0", port=port, reload=True)