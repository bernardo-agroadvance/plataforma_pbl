import os
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI
from datetime import datetime, date

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai = OpenAI(api_key=OPENAI_KEY)

def verificar_se_ja_esta_liberado(conteudo_id: str, turma: str) -> bool:
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
    try:
        usuario = supabase.table("PBL - usuarios").select("*").eq("cpf", cpf).single().execute().data
        if not usuario:
            return {"status": "erro", "mensagem": "Usuário não encontrado"}

        turma = usuario["turma"]
        cargo = usuario.get("cargo", "")
        regiao = usuario.get("regiao", "")
        cadeia = usuario.get("cadeia", "")
        desafios = usuario.get("desafios", "")
        observacoes = usuario.get("observacoes", "")
        perfil = f"""
- Cargo/função: {cargo}
- Região/cadeia ou cultura: {regiao} / {cadeia}
- Desafios enfrentados: {desafios}
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
                prompt_macro = f"""
Você é um gerador de desafios educacionais no modelo Problem-Based Learning (PBL), voltado para profissionais do agronegócio.

Sua tarefa é criar um **macrodesafio estratégico** para um aluno do MBA em Agronegócio.

Perfil do aluno:
{perfil}

O tema do módulo é: **{modulo}**
Ementa da disciplina:
{ementa}

Sua resposta deve conter:
1. Um cenário narrativo realista contextualizado no agronegócio brasileiro, de maneira formal e pouco lúdica. Evite criar \"fábulas\".
2. Situação complexa com múltiplos fatores interligados.
3. Linha de tempo coerente.
4. Texto com 3 a 5 parágrafos, linguagem técnica acessível.
5. Ao final, o macroproblema claro e multifatorial.

**Não forneça soluções.**
                """

                resposta_macro = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt_macro}],
                    temperature=0.7
                )

                texto_macro = resposta_macro.choices[0].message.content.strip()
                desafio_liberado = verificar_se_ja_esta_liberado(conteudo_id, turma)

                supabase.table("PBL - desafios").insert({
                    "cpf": cpf,
                    "tipo": "macro",
                    "conteudo_id": conteudo_id,
                    "texto_desafio": texto_macro,
                    "data_criacao": datetime.utcnow().isoformat(),
                    "desafio_liberado": desafio_liberado,
                    "status_gerado": "ok"
                }).execute()

                gerados.append(f"Macrodesafio: {modulo}")

            aulas = supabase.table("PBL - conteudo") \
                .select("*") \
                .eq("modulo", modulo) \
                .not_.is_("aula", "null") \
                .eq("ativo", True) \
                .execute().data

            for aula in aulas:
                aula_nome = aula["aula"]
                conteudo_aula_id = aula["id"]
                ementa_aula = aula.get("ementa", "")

                existe_micro = supabase.table("PBL - desafios").select("id") \
                    .eq("cpf", cpf).eq("conteudo_id", conteudo_aula_id).eq("tipo", "micro") \
                    .execute().data

                if not existe_micro:
                    prompt_micro = f"""
Você é um gerador de microdesafios semanais dentro do modelo PBL para o agronegócio.

Perfil do aluno:
{perfil}

O macrodesafio do módulo é:
{texto_macro}

Módulo: {modulo}
Aula: {aula_nome}
Ementa: {ementa_aula}

Sua resposta deve conter:
1. Texto de 3 a 4 parágrafos que continue a narrativa do macro.
2. Novos dados técnicos, projeções, termos explicados etc.
3. Último parágrafo com a tarefa da semana.

**Não forneça soluções.**
                    """

                    resposta_micro = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt_micro}],
                        temperature=0.7
                    )

                    texto_micro = resposta_micro.choices[0].message.content.strip()
                    titulo = gerar_titulo_microdesafio(texto_micro, aula_nome)
                    desafio_liberado = verificar_se_ja_esta_liberado(conteudo_aula_id, turma)

                    supabase.table("PBL - desafios").insert({
                        "cpf": cpf,
                        "tipo": "micro",
                        "conteudo_id": conteudo_aula_id,
                        "texto_desafio": texto_micro,
                        "data_criacao": datetime.utcnow().isoformat(),
                        "desafio_liberado": desafio_liberado,
                        "titulo": titulo,
                        "status_gerado": "ok"
                    }).execute()

                    gerados.append(f"Microdesafio: {modulo} - {aula_nome}")

        return {"status": "sucesso", "mensagem": "Desafios gerados", "detalhes": gerados}

    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
