from backend.db.desafios import buscar_tentativas

cpf = "12345678900"
desafio_id = "8a8eec50-b01a-4e9b-a8bf-3396514b51f8"  # pegue de um desafio liberado do teste anterior

tentativas = buscar_tentativas(cpf, desafio_id)
print(f"Você já enviou {tentativas} tentativas para este desafio.")
