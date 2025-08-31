# fastapi_backend/main.py
import os
import re
from dotenv import load_dotenv

# Carrega .env antes de qualquer uso de variáveis de ambiente
load_dotenv()

from typing import Optional, Set
from datetime import datetime
from uuid import uuid4

from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    BackgroundTasks,
    Response,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr

# Seus módulos
from gerar_desafios import gerar_todos_os_desafios, get_supabase
from avaliador import avaliar_resposta_com_ia


# -----------------------------------------------------------------------------
# App & Docs
# -----------------------------------------------------------------------------
ENV = os.getenv("ENV", "development")
app = FastAPI(
    title="PBL API",
    version="1.0.0",
    docs_url=None if ENV == "production" else "/docs",
    redoc_url=None if ENV == "production" else "/redoc",
    openapi_url="/openapi.json",
)


# -----------------------------------------------------------------------------
# CORS (inclui 5174) — necessário para cookies (allow_credentials=True)
# -----------------------------------------------------------------------------
def _parse_origins():
    raw = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
    )
    origins = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    # Só habilita credenciais se não houver wildcard
    allow_credentials = ("*" not in origins)
    return origins, allow_credentials


_allowed_origins, _allow_creds = _parse_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins if _allowed_origins else ["http://localhost:5173"],
    allow_credentials=_allow_creds,  # precisa ser True para cookies cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conjunto para validar origem do WebSocket (CORS não cobre WS)
ALLOWED_WS_ORIGINS: Set[str] = set(_allowed_origins)


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class UsuarioPayload(BaseModel):
    cpf: str
    cargo: Optional[str] = None
    regiao: Optional[str] = None
    cadeia: Optional[str] = None
    desafios: Optional[str] = None
    observacoes: Optional[str] = None
    # Extras tolerados do front
    nome: Optional[str] = None
    curso: Optional[str] = None
    turma: Optional[str] = None
    formulario_finalizado: Optional[bool] = None


class AvaliacaoRequest(BaseModel):
    cpf: str
    desafio_id: str
    resposta: str
    tentativa: int


class FinalizacaoRequest(BaseModel):
    cpf: str
    desafio_id: str
    tentativa: int


from pydantic import Field

class CpfLogin(BaseModel):
    cpf: str = Field(..., pattern=r"^\d{11}$")


# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------
def only_digits(s: Optional[str]) -> str:
    import re
    return re.sub(r"\D", "", s or "")


# -----------------------------------------------------------------------------
# Sessão via Cookie HttpOnly (simples - troque por JWT/assinatura em produção)
# -----------------------------------------------------------------------------
COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "session")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"  # True em prod HTTPS
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")  # "lax" (dev), "none" (prod cross-site)
COOKIE_MAX_AGE = int(os.getenv("COOKIE_MAX_AGE", str(60 * 60 * 24 * 7)))  # 7 dias


def set_session_cookie(response: Response, cpf: str) -> None:
    # Em produção: use um valor assinado (ex.: JWT) em vez de "cpf:..."
    response.set_cookie(
        key=COOKIE_NAME,
        value=f"cpf:{cpf}",
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )


def get_cpf_from_cookie(request: Request) -> Optional[str]:
    raw = request.cookies.get(COOKIE_NAME)
    if not raw or not raw.startswith("cpf:"):
        return None
    return only_digits(raw[4:])


# -----------------------------------------------------------------------------
# WebSocket
# -----------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)

    async def broadcast(self, message: str):
        for ws in list(self.active):
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(ws)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Validação de origem para WS
    origin = (websocket.headers.get("origin", "") or "").rstrip("/")
    print(f"[WS] origin={origin} allowed={ALLOWED_WS_ORIGINS}")
    if ALLOWED_WS_ORIGINS and origin not in ALLOWED_WS_ORIGINS:
        await websocket.close(code=1008, reason="Origin not allowed")
        return

    await manager.connect(websocket)
    print("connection open")
    try:
        while True:
            data = await websocket.receive_text()
            if data.strip().lower() == "ping":
                await websocket.send_text("pong")
            else:
                await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("connection closed")


# -----------------------------------------------------------------------------
# Meta / Health
# -----------------------------------------------------------------------------
@app.get("/", tags=["meta"])
def home():
    return {"mensagem": "API de geração de desafios está online ✅", "env": ENV}


# -----------------------------------------------------------------------------
# Auth (cookies) — adiciona /auth/cpf-login e mantém /cpf-login como alias
# -----------------------------------------------------------------------------
@app.post("/auth/cpf-login", tags=["auth"])
def auth_cpf_login(payload: CpfLogin, response: Response):
    cpf = only_digits(payload.cpf)
    if len(cpf) != 11:
        raise HTTPException(status_code=400, detail="CPF inválido")
    # (Opcional) verificar existência no banco antes
    # u = get_supabase().table("PBL - usuarios").select("cpf").eq("cpf", cpf).limit(1).execute()
    # if not u.data: raise HTTPException(401, "CPF não encontrado")

    set_session_cookie(response, cpf)
    return {"ok": True}


# Alias compatível com seu código antigo (se ainda houver algo chamando /cpf-login)
@app.post("/cpf-login", tags=["auth"])
def legacy_cpf_login(body: CpfLogin, response: Response):
    return auth_cpf_login(body, response)


@app.get("/auth/me", tags=["auth"])
def auth_me(request: Request):
    cpf = get_cpf_from_cookie(request)
    if not cpf:
        raise HTTPException(status_code=401, detail="Sem sessão")
    return {"cpf": cpf}


@app.post("/auth/logout", tags=["auth"])
def auth_logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/", samesite=COOKIE_SAMESITE, secure=COOKIE_SECURE)
    return {"ok": True}


# -----------------------------------------------------------------------------
# Usuários
# -----------------------------------------------------------------------------
@app.post("/api/usuarios", tags=["aluno"])
def upsert_usuario(payload: UsuarioPayload):
    import traceback

    sb = get_supabase()

    cpf_clean = only_digits(payload.cpf)
    if not cpf_clean:
        raise HTTPException(status_code=400, detail="CPF ausente.")

    data = payload.model_dump(exclude_none=True)
    data["cpf"] = cpf_clean

    try:
        # 1) existe?
        q = sb.table('PBL - usuarios').select("cpf").eq("cpf", cpf_clean).limit(1).execute()
        if getattr(q, "error", None):
            raise RuntimeError(q.error)

        # 2) update ou insert
        if q.data:
            resp = sb.table('PBL - usuarios').update(data).eq("cpf", cpf_clean).execute()
        else:
            resp = sb.table('PBL - usuarios').insert(data).execute()

        if getattr(resp, "error", None):
            raise RuntimeError(resp.error)

        return {"ok": True, "data": resp.data or []}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar usuário: {e}")
    
# -----------------------------------------------------------------------------
# Consulta de usuários (GET) - usado pelo front para listar cursos/turmas
# -----------------------------------------------------------------------------
from fastapi import Query
from typing import Optional

# whitelist de campos que podem ser retornados pela API
ALLOWED_USER_FIELDS = {
    "id", "nome", "cpf", "curso", "turma", "cargo", "regiao", "cadeia",
    "desafios", "observacoes", "data_cadastro", "formulario_finalizado", "role"
}

@app.get("/api/usuarios", tags=["aluno"])
def get_usuarios(
    cpf: str = Query(..., description="CPF com ou sem máscara"),
    fields: Optional[str] = Query(
        None,
        description="Campos separados por vírgula. Ex: 'curso,turma,formulario_finalizado'"
    ),
):
    sb = get_supabase()
    cpf_clean = only_digits(cpf)
    if not cpf_clean or len(cpf_clean) != 11:
        raise HTTPException(status_code=400, detail="CPF inválido.")

    # se 'fields' vier, filtra pelos campos permitidos; senão, usa um default
    if fields:
        req = [f.strip() for f in fields.split(",") if f.strip()]
        cols = [f for f in req if f in ALLOWED_USER_FIELDS]
        if not cols:
            cols = ["cpf", "curso", "turma", "formulario_finalizado"]
    else:
        cols = ["cpf", "curso", "turma", "formulario_finalizado"]

    select_cols = ",".join(sorted(set(cols)))

    try:
        r = (
            sb.table('PBL - usuarios')
              .select(select_cols)
              .eq('cpf', cpf_clean)
              .execute()
        )
        if getattr(r, "error", None):
            raise RuntimeError(r.error)
        return r.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar usuários: {e}")

# -----------------------------------------------------------------------------
# Liberações por turma (GET) - usado no DesafiosPage
# -----------------------------------------------------------------------------
from fastapi import Query
from datetime import datetime, time as dtime

@app.get("/api/liberacoes", tags=["aluno"])
def get_liberacoes(
    turma: str = Query(..., description="Código da turma ex.: '1' ou 'TURMA-A'")
):
    sb = get_supabase()
    try:
        r = (
            sb.table('PBL - liberacoes_agendadas')
              .select('conteudo_id, data_liberacao, hora_liberacao, liberado, turmas')
              .contains('turmas', [turma])
              .execute()
        )
        rows = r.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar liberações: {e}")

    # Agora local (simples/naive) para comparar com data/hora sem timezone
    today = datetime.now().date()
    now_t = datetime.now().time()

    out = []
    for row in rows:
        try:
            d_str = (row.get("data_liberacao") or "").split("T")[0]  # garante 'YYYY-MM-DD'
            t_str = (row.get("hora_liberacao") or "00:00:00")
            d_obj = datetime.fromisoformat(d_str).date()
            try:
                t_obj = dtime.fromisoformat(t_str)
            except Exception:
                t_obj = dtime(hour=0, minute=0, second=0)

            liberado_flag = bool(row.get("liberado"))
            liberado_por_tempo = (d_obj < today) or (d_obj == today and t_obj <= now_t)
            if liberado_flag or liberado_por_tempo:
                out.append({"conteudo_id": row.get("conteudo_id")})
        except Exception:
            # se alguma linha vier malformada, só ignora
            continue

    return out

# -----------------------------------------------------------------------------
# Consulta de desafios por CPF (GET) - polling/contagem no front
# -----------------------------------------------------------------------------
ALLOWED_DESAFIO_FIELDS = {
    "id", "cpf", "texto_desafio", "tipo", "desafio_liberado", "conteudo_id",
    "data_criacao", "titulo", "data_liberacao", "status_gerado"
}

from fastapi import Query

# Set to track CPFs currently being processed for challenge generation
generation_inflight: set = set()

@app.get("/api/desafios")
def listar_desafios(
    cpf: str = Query(..., description="CPF (com ou sem máscara)"),
    fields: str | None = Query(None, description="Colunas para selecionar, separadas por vírgula"),
    background_tasks: BackgroundTasks = None,
):
    import re
    sb = get_supabase()
    cpf_clean = re.sub(r"\D", "", cpf or "")
    if not cpf_clean:
        raise HTTPException(status_code=400, detail="CPF inválido")

    # selecione campos ou o default usado pelo front
    sel = (fields or "id, texto_desafio, tipo, desafio_liberado, conteudo_id").strip()

    try:
        resp = sb.table("PBL - desafios").select(sel).eq("cpf", cpf_clean).execute()
        data = resp.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar desafios: {e}")

    # Se já houver dados, garante que o CPF não fica marcado como "em geração"
    if data:
        generation_inflight.discard(cpf_clean)
        return data

    # Se não há desafios ainda, dispare a geração UMA VEZ para este CPF
    if cpf_clean not in generation_inflight:
        generation_inflight.add(cpf_clean)
        if background_tasks is not None:
            background_tasks.add_task(gerar_todos_os_desafios, cpf_clean)
        else:
            # fallback defensivo
            import threading
            threading.Thread(
                target=gerar_todos_os_desafios, args=(cpf_clean,), daemon=True
            ).start()
        print(f"[AUTO-GERAR] disparado para cpf={cpf_clean}")

    return []


# -----------------------------------------------------------------------------
# Lista de conteúdos (GET) - usado no DesafiosPage para mapear modulo/aula
# -----------------------------------------------------------------------------
ALLOWED_CONTEUDO_FIELDS = {"id", "modulo", "aula", "ementa", "ativo"}

@app.get("/api/conteudos", tags=["aluno"])
def get_conteudos(
    fields: Optional[str] = Query(None, description="Campos separados por vírgula, ex.: 'id,modulo,aula'"),
    only_active: bool = Query(True, description="Se true, retorna apenas conteúdos ativos"),
):
    sb = get_supabase()

    if fields:
        req = [f.strip() for f in fields.split(",") if f.strip()]
        cols = [f for f in req if f in ALLOWED_CONTEUDO_FIELDS]
        if not cols:
            cols = ["id", "modulo", "aula"]
    else:
        cols = ["id", "modulo", "aula"]

    select_cols = ",".join(sorted(set(cols)))

    try:
        q = sb.table('PBL - conteudo').select(select_cols)
        if only_active and "ativo" in ALLOWED_CONTEUDO_FIELDS:
            q = q.eq("ativo", True)
        r = q.execute()
        if getattr(r, "error", None):
            raise RuntimeError(r.error)
        return r.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar conteúdos: {e}")

# -----------------------------------------------------------------------------
# Resumo de respostas por CPF (GET) - tentativas/finalização no DesafiosPage
# -----------------------------------------------------------------------------
ALLOWED_RESPOSTA_FIELDS = {
    "id", "desafio_id", "tentativa", "tentativa_finalizada",
    "nota", "feedback", "resposta_ideal", "conteudo_id", "data_envio"
}

@app.get("/api/respostas/resumo", tags=["aluno"])
def get_respostas_resumo(
    cpf: str = Query(..., description="CPF com ou sem máscara"),
    fields: Optional[str] = Query("desafio_id,tentativa,tentativa_finalizada",
                                  description="Campos separados por vírgula"),
):
    import re
    sb = get_supabase()

    cpf_clean = re.sub(r"\D", "", cpf or "")
    if not cpf_clean or len(cpf_clean) != 11:
        raise HTTPException(status_code=400, detail="CPF inválido.")

    req = [f.strip() for f in (fields or "").split(",") if f.strip()]
    cols = [f for f in req if f in ALLOWED_RESPOSTA_FIELDS]
    if not cols:
        cols = ["desafio_id", "tentativa", "tentativa_finalizada"]

    select_cols = ",".join(sorted(set(cols)))

    try:
        r = (
            sb.table('PBL - respostas')
              .select(select_cols)
              .eq('cpf', cpf_clean)
              .execute()
        )
        if getattr(r, "error", None):
            raise RuntimeError(r.error)
        return r.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar respostas: {e}")


# -----------------------------------------------------------------------------
# Geração de Desafios
# -----------------------------------------------------------------------------
@app.post("/gerar-desafios/{cpf}")
def gerar_desafios(cpf: str, background_tasks: BackgroundTasks):
    def task():
        import traceback
        cpf_clean = re.sub(r"\D", "", cpf or "")
        try:
            print(f"[GERAR] iniciando para cpf={cpf_clean}")
            gerar_todos_os_desafios(cpf_clean)  # sua função atual
            print(f"[GERAR] ok para cpf={cpf_clean}")
        except Exception as e:
            print("[GERAR] ERRO:", e)
            traceback.print_exc()
        finally:
            # Importantíssimo: sempre liberar o guarda — sucesso ou erro
            generation_inflight.discard(cpf_clean)

    background_tasks.add_task(task)
    return {"status": "agendado", "mensagem": "Processo iniciado com sucesso."}


# -----------------------------------------------------------------------------
# Avaliador & Respostas
# -----------------------------------------------------------------------------
@app.post("/avaliador", tags=["respostas"])
def avaliar_resposta(payload: AvaliacaoRequest):
    d = (
        get_supabase()
        .table("PBL - desafios")
        .select("texto_desafio")
        .eq("id", payload.desafio_id)
        .single()
        .execute()
        .data
    )
    if not d:
        raise HTTPException(status_code=404, detail="Desafio não encontrado.")

    texto = d["texto_desafio"]
    nota, feedback, sugestao = avaliar_resposta_com_ia(payload.resposta, texto, payload.tentativa)
    return {"nota": nota, "feedback": feedback, "sugestao": sugestao}


@app.post("/registrar-resposta", tags=["respostas"])
def registrar_resposta(payload: AvaliacaoRequest):
    try:
        d = (
            get_supabase()
            .table("PBL - desafios")
            .select("texto_desafio, conteudo_id")
            .eq("id", payload.desafio_id)
            .single()
            .execute()
            .data
        )
        if not d:
            raise HTTPException(status_code=404, detail="Desafio não encontrado.")

        texto = d["texto_desafio"]
        conteudo_id = d["conteudo_id"]

        nota, feedback, sugestao = avaliar_resposta_com_ia(payload.resposta, texto, payload.tentativa)

        resposta_id = str(uuid4())

        get_supabase().table("PBL - respostas").insert(
            {
                "id": resposta_id,
                "cpf": only_digits(payload.cpf),
                "desafio_id": payload.desafio_id,
                "conteudo_id": conteudo_id,
                "tentativa": payload.tentativa,
                "texto_resposta": payload.resposta,
                "nota": nota,
                "feedback": feedback,
                "resposta_ideal": sugestao,
                "data_envio": datetime.utcnow().isoformat(),
                "tentativa_finalizada": payload.tentativa == 3,
            }
        ).execute()

        return {"nota": nota, "feedback": feedback, "sugestao": sugestao}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/finalizar-resposta", tags=["respostas"])
def finalizar_resposta(payload: FinalizacaoRequest):
    try:
        resp = (
            get_supabase()
            .table("PBL - respostas")
            .select("id, texto_resposta, desafio_id")
            .eq("cpf", only_digits(payload.cpf))
            .eq("desafio_id", payload.desafio_id)
            .eq("tentativa", payload.tentativa)
            .single()
            .execute()
        )
        if not resp.data:
            raise HTTPException(status_code=404, detail="Tentativa não encontrada.")

        resposta_id = resp.data["id"]
        texto_resposta = resp.data["texto_resposta"]

        desafio = (
            get_supabase()
            .table("PBL - desafios")
            .select("texto_desafio")
            .eq("id", payload.desafio_id)
            .single()
            .execute()
        )
        if not desafio.data:
            raise HTTPException(status_code=404, detail="Desafio não encontrado.")

        texto_desafio = desafio.data["texto_desafio"]

        # Gera sugestão final
        _, _, sugestao = avaliar_resposta_com_ia(texto_resposta, texto_desafio, tentativa=3)

        get_supabase().table("PBL - respostas").update(
            {"resposta_ideal": sugestao, "tentativa_finalizada": True}
        ).eq("id", resposta_id).execute()

        return {"status": "sucesso", "mensagem": "Resposta marcada como definitiva."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# Status dos desafios
# -----------------------------------------------------------------------------
@app.get("/desafios/status/{cpf}", tags=["desafios"])
def status_desafios(cpf: str):
    cpf_clean = only_digits(cpf)
    try:
        resp = (
            get_supabase()
            .table("PBL - desafios")
            .select("id")
            .eq("cpf", cpf_clean)
            .in_("desafio_liberado", [True, "true"])
            .limit(1)
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar desafios: {e}")

    if getattr(resp, "error", None):
        raise HTTPException(status_code=500, detail=str(resp.error))

    liberado = bool(getattr(resp, "data", []) or [])
    return {"liberado": liberado}


# ============================== ADMIN ========================================
from typing import List
from pydantic import BaseModel

class LiberarReq(BaseModel):
    conteudo_id: str
    modulo: str
    aula: str
    turmas: List[str]
    data_iso: str  # ex: "2025-08-31T13:00:00-03:00"

def _parse_iso_to_date_time(iso_s: str):
    # aceita "Z" e offsets
    s = (iso_s or "").strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        raise HTTPException(status_code=400, detail="data_iso inválido")
    # campos separados (DATE e TIME) conforme sua tabela
    d = dt.date().isoformat()
    t = dt.time().replace(microsecond=0).strftime("%H:%M:%S")
    return d, t

async def _admin_guard(request: Request):
    """Valida sessão e confere se o usuário é admin/professor no banco."""
    cpf = get_cpf_from_cookie(request)
    if not cpf:
        raise HTTPException(status_code=401, detail="Sem sessão")

    sb = get_supabase()
    try:
        u = (
            sb.table('PBL - usuarios')
            .select('role')
            .eq('cpf', cpf)
            .limit(1)
            .execute()
        )
        role = (u.data[0]['role'] if u.data else None)
    except Exception:
        role = None

    if role not in ("admin", "professor"):
        raise HTTPException(status_code=403, detail="Acesso restrito")
    return cpf

@app.get("/api/admin/conteudos", tags=["admin"])
def admin_conteudos(request: Request):
    # await _admin_guard(request)  # descomente para exigir admin no dev também
    r = (
        get_supabase()
        .table("PBL - conteudo")
        .select("id, modulo, aula, ativo")
        .eq("ativo", True)
        .order("modulo", desc=False)
        .order("aula", desc=False)
        .execute()
    )
    return r.data or []

@app.get("/api/admin/turmas", tags=["admin"])
def admin_turmas(request: Request):
    # await _admin_guard(request)
    r = (
        get_supabase()
        .rpc("distinct_turmas")  # se não existir, usamos fallback abaixo
        .execute()
    )
    if getattr(r, "data", None) is None:
        # fallback: distinct manual
        r2 = (
            get_supabase()
            .table('PBL - usuarios')
            .select('turma')
            .execute()
        )
        turmas = sorted({row['turma'] for row in (r2.data or []) if row.get('turma')})
        return turmas
    return r.data

@app.get("/api/admin/liberacoes-historico", tags=["admin"])
def admin_liberacoes_hist(request: Request):
    # await _admin_guard(request)
    r = (
        get_supabase()
        .table('PBL - liberacoes_agendadas')
        .select('id, conteudo_id, modulo, aula, turmas, data_liberacao, hora_liberacao, liberado, created_at')
        .order('created_at', desc=True)
        .limit(100)
        .execute()
    )
    return r.data or []

@app.post("/api/admin/liberar", tags=["admin"])
def admin_liberar(req: LiberarReq, request: Request):
    # await _admin_guard(request)
    data_liberacao, hora_liberacao = _parse_iso_to_date_time(req.data_iso)

    payload = {
        "conteudo_id": req.conteudo_id,
        "modulo": req.modulo,
        "aula": req.aula,
        "turmas": req.turmas,
        "data_liberacao": data_liberacao,
        "hora_liberacao": hora_liberacao,
        "liberado": False,
    }

    ins = get_supabase().table('PBL - liberacoes_agendadas').insert(payload).execute()
    if getattr(ins, "error", None):
        raise HTTPException(status_code=500, detail=str(ins.error))
    return ins.data or []
# ============================ /ADMIN =========================================
