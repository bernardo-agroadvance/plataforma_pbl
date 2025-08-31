from backend.db.gerador_desafio import gerar_desafio_para_aluno

# 🟡 Substitua pelo CPF real cadastrado na tabela "PBL - usuarios"
cpf_teste = "44184150845"

# 🟢 Tipo pode ser "macro" ou "micro"
tipo = "macro"

resultado = gerar_desafio_para_aluno(cpf=cpf_teste, tipo=tipo)

# 📤 Exibe o resultado no terminal
if resultado["status"] == "sucesso":
    print("\n✅ Desafio gerado com sucesso:\n")
    print(resultado["desafio"])
else:
    print("\n❌ Erro ao gerar desafio:")
    print(resultado["mensagem"])
