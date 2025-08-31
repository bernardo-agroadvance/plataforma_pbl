# fastapi_backend/gerar_desafios.py
import os
from openai import OpenAI
from datetime import datetime, date
from .db import get_supabase_client # <-- MUDANÇA AQUI

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_KEY)

def verificar_se_ja_esta_liberado(conteudo_id: str, turma: str) -> bool:
    supabase = get_supabase_client()
    hoje = date.today().isoformat()

    resultado = supabase.table("PBL - liberacoes_agendadas") \
        .select("turmas, data_liberacao, liberado") \
        .eq("conteudo_id", conteudo_id) \
        .eq("liberado", True) \
        .lte("data_liberacao", hoje) \
        .execute().data

    for row in resultado:
        turmas = row.get("turmas", [])
        if turma in turmas:
            return True
    return False

def gerar_titulo_microdesafio(texto_desafio: str, aula: str) -> str:
    prompt = f"""
Você é um assistente educacional. Gere um título curto e atrativo com no máximo 6 palavras para um microdesafio baseado no texto a seguir.

O título deve ser criativo, direto, e engajar o aluno. Evite palavras como 'responda', 'explique', 'desafio' ou frases genéricas. Baseie-se também no nome da aula para contextualizar melhor.

Texto do microdesafio:
{texto_desafio}

Nome da aula: {aula}

Título:
"""
    try:
        resposta = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=20
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERRO] Falha ao gerar título: {e}")
        return "Título não gerado"

def gerar_todos_os_desafios(cpf: str) -> dict:
    supabase = get_supabase_client()
    try:
        usuario = supabase.table("PBL - usuarios").select("*").eq("cpf", cpf).single().execute().data
        if not usuario:
            return {"status": "erro", "mensagem": "Usuário não encontrado"}

        turma = usuario["turma"]
        cargo = usuario.get("cargo", "")
        regiao = usuario.get("regiao", "")
        cadeia = usuario.get("cadeia", "")
        desafios_usuario = usuario.get("desafios", "")
        observacoes = usuario.get("observacoes", "")
        perfil = f"""
- Cargo/função: {cargo}
- Região/cadeia ou cultura: {regiao} / {cadeia}
- Desafios enfrentados: {desafios_usuario}
- Observações complementares: {observacoes}
        """.strip()

        cronogramas = supabase.table("PBL - cronograma") \
            .select("*,conteudo_id") \
            .eq("turma", turma) \
            .order("ordem") \
            .execute().data

        if not cronogramas:
            return {"status": "erro", "mensagem": "Nenhum conteúdo encontrado para a turma"}

        gerados = []
        texto_macro = ""

        for c in cronogramas:
            conteudo_id = c["conteudo_id"]
            conteudo = supabase.table("PBL - conteudo").select("*").eq("id", conteudo_id).single().execute().data

            if not conteudo or not conteudo.get("modulo"):
                continue

            modulo = conteudo["modulo"]
            ementa = conteudo.get("ementa", "")

            existe_macro = supabase.table("PBL - desafios").select("id") \
                .eq("cpf", cpf).eq("conteudo_id", conteudo_id).eq("tipo", "macro") \
                .execute().data
            
            if not existe_macro:
                # Lógica para gerar o MACRODESAFIO...
                # (código omitido para brevidade, mantenha o seu)
                pass # MANTENHA SUA LÓGICA DE GERAR MACRO AQUI
            else:
                macro_existente = supabase.table("PBL - desafios").select("texto_desafio").eq("cpf", cpf).eq("conteudo_id", conteudo_id).eq("tipo", "macro").single().execute().data
                if macro_existente:
                    texto_macro = macro_existente['texto_desafio']
            
            # Lógica para gerar os MICRODESAFIOS...
            # (código omitido para brevidade, mantenha o seu)
            pass # MANTENHA SUA LÓGICA DE GERAR MICRO AQUI

        return {"status": "sucesso", "mensagem": "Desafios gerados", "detalhes": gerados}

    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}