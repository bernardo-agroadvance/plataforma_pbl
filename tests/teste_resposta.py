from backend.db.desafios import registrar_resposta

cpf = "12345678900"
desafio_id = "8a8eec50-b01a-4e9b-a8bf-3396514b51f8"
resposta = "Essa é minha resposta de teste."

sucesso = registrar_resposta(cpf, desafio_id, resposta)
print("✅ Resposta registrada com sucesso!" if sucesso else "❌ Erro ao registrar.")
