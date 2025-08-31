from backend.db.gerador_em_lote import gerar_todos_os_desafios

resultado = gerar_todos_os_desafios("12345678900")  # use o CPF real

if resultado["status"] == "sucesso":
    print("✅ Sucesso:")
    for item in resultado["detalhes"]:
        print(" -", item)
else:
    print("❌ Erro:", resultado["mensagem"])
