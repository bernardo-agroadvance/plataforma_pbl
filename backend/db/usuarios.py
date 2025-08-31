from .connection import supabase

def buscar_usuario_por_cpf(cpf: str) -> dict:
    """
    Retorna os dados do usuário com base no CPF.
    Se não encontrado, retorna erro.
    """
    try:
        resultado = supabase.table("PBL - usuarios").select("*").eq("cpf", cpf).limit(1).execute()

        if not resultado.data:
            return {"status": "erro", "mensagem": "CPF não encontrado. Acesso não autorizado."}

        return {"status": "sucesso", "dados": resultado.data[0]}

    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
    

def atualizar_usuario(cpf: str, novos_dados: dict) -> dict:
    """
    Atualiza os dados de um usuário identificado por CPF.
    Define 'formulario_finalizado' como True.
    """
    try:
        novos_dados["formulario_finalizado"] = True
        resultado = supabase.table("PBL - usuarios").update(novos_dados).eq("cpf", cpf).execute()
        return {"status": "sucesso", "dados": resultado.data}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

