from backend.db.usuarios import buscar_usuario_por_cpf

cpf_teste = "44184150845"  # coloque aqui um CPF real do Supabase

resposta = buscar_usuario_por_cpf(cpf_teste)
print(resposta)
