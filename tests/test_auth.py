# fastapi_backend/tests/test_auth.py
from fastapi.testclient import TestClient
# Alteração aqui: import absoluto
from fastapi_backend.main import app 

client = TestClient(app)

# fastapi_backend/tests/test_auth.py

def test_login_for_access_token():
    # Substitua pelo CPF real e válido do seu banco
    valid_cpf = "44730463897"  # <--- COLOQUE UM CPF VÁLIDO AQUI
    
    response = client.post(
        "/auth/token",
        data={"username": valid_cpf, "password": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_with_invalid_cpf():
    response = client.post(
        "/auth/token",
        data={"username": "44730463890", "password": ""}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "CPF não encontrado ou inválido."