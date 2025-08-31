from backend.db.desafios import buscar_desafios_liberados

cpf = "12345678900"  # insira um CPF que tenha desafios liberados
resultados = buscar_desafios_liberados(cpf)

print(f"Desafios encontrados: {len(resultados)}")
for desafio in resultados:
    print(f"- Tipo: {desafio['tipo']} | Módulo: {desafio.get('modulo')} | Aula: {desafio.get('aula')}")
