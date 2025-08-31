# fastapi_backend/tests/test_api.py
from fastapi.testclient import TestClient
# Alteração aqui: import absoluto
from fastapi_backend.main import app

client = TestClient(app)

def test_acesso_negado_sem_token():
    """Verifica se o acesso à rota /api/usuarios é negado sem um token."""
    response = client.get("/api/usuarios")
    assert response.status_code == 401
    # O detalhe da mensagem mudou com o novo esquema de autenticação
    assert response.json()["detail"] == "Not authenticated"

def test_obter_token_e_acessar_rota_protegida():
    """
    Testa o fluxo completo:
    1. Faz login com um CPF válido para obter um token.
    2. Usa o token para acessar a rota protegida de usuários.
    """
    # --- Passo 1: Obter o token ---
    # !!! IMPORTANTE: Substitua 'SEU_CPF_DE_TESTE' por um CPF que exista no seu banco de dados.
    cpf_valido = "44730463897" # <-- Lembre-se de trocar este valor
    
    response_token = client.post(
        "/auth/token",
        data={"username": cpf_valido, "password": ""}
    )
    assert response_token.status_code == 200
    token_data = response_token.json()
    token = token_data["access_token"]
    
    # --- Passo 2: Acessar a rota protegida com o token ---
    headers = {"Authorization": f"Bearer {token}"}
    response_usuarios = client.get("/api/usuarios", headers=headers)
    
    assert response_usuarios.status_code == 200
    assert isinstance(response_usuarios.json(), list)