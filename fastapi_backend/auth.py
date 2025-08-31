# app/auth.py
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, constr
import httpx, os, time, hmac, hashlib, base64, json

router = APIRouter(prefix="/auth", tags=["auth"])
SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
APP_JWT_SECRET = os.getenv("APP_JWT_SECRET", "change-me")

from pydantic import Field

class CpfLogin(BaseModel):
    cpf: constr = Field(..., pattern=r"^\d{11}$")

def sign_token(payload: dict, exp_seconds=8*3600):
    header = {"alg":"HS256","typ":"JWT"}
    payload = {**payload, "exp": int(time.time()) + exp_seconds}
    def b64(x): return base64.urlsafe_b64encode(json.dumps(x).encode()).rstrip(b"=")
    def mac(msg): return base64.urlsafe_b64encode(
        hmac.new(APP_JWT_SECRET.encode(), msg, hashlib.sha256).digest()
    ).rstrip(b"=")
    p1 = b".".join([b64(header), b64(payload)])
    return (p1 + b"." + mac(p1)).decode()

@router.post("/cpf-login")
async def cpf_login(body: CpfLogin, request: Request):
    # lookup no Supabase com service_role
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/PBL%20-%20usuarios",
            params={"select":"id,cpf,nome,role,turma,curso", "cpf":f"eq.{body.cpf}"},
            headers={"apikey": SERVICE_ROLE, "Authorization": f"Bearer {SERVICE_ROLE}"}
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Auth store unavailable")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=401, detail="CPF não encontrado")

    user = rows[0]
    # gere um token da SUA app (não expose service_role)
    token = sign_token({"sub": user["id"], "cpf": user["cpf"], "role": user["role"]})
    from fastapi.responses import JSONResponse
    res = JSONResponse({"ok": True, "user": {"nome": user["nome"], "role": user["role"]}})
    res.set_cookie("pbl_session", token, httponly=True, secure=False, samesite="lax", max_age=8*3600, path="/")
    return res
