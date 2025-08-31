import os
from supabase import create_client
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai = OpenAI(api_key=OPENAI_KEY)


def gerar_desafio_para_aluno(cpf: str, tipo: str = "macro") -> dict:
    try:
        # 1. Buscar perfil do aluno
        usuario = supabase.table("PBL - usuarios").select("*").eq("cpf", cpf).single().execute().data
        if not usuario:
            return {"status": "erro", "mensagem": "Aluno não encontrado"}

        turma = usuario["turma"]

        # 2. Obter conteúdo do módulo ativo da turma via cronograma
        cronograma = supabase.table("PBL - cronograma").select("*").eq("turma", turma).eq("ativo", True).single().execute().data
        if not cronograma:
            return {"status": "erro", "mensagem": "Nenhum módulo ativo encontrado para a turma"}

        conteudo_id = cronograma["conteudo_id"]

        # 3. Obter ementa e dados do conteúdo
        conteudo = supabase.table("PBL - conteudo").select("*").eq("id", conteudo_id).single().execute().data
        if not conteudo:
            return {"status": "erro", "mensagem": "Conteúdo não encontrado"}

        tema_do_modulo = conteudo["modulo"]
        tema_da_aula = conteudo.get("aula", "")
        ementa = conteudo["ementa"]

        # 4. Buscar macrodesafio anterior (se for micro)
        texto_macro = ""
        if tipo == "micro":
            macro = supabase.table("PBL - desafios").select("texto_desafio").eq("cpf", cpf).eq("tipo", "macro").eq("conteudo_id", conteudo_id).single().execute().data
            texto_macro = macro["texto_desafio"] if macro else ""

        # 5. Montar prompt de acordo com o tipo
        if tipo == "macro":
            prompt = f"""
Você é um gerador de desafios educacionais no modelo Problem-Based Learning (PBL), voltado para profissionais do agronegócio. Sua tarefa é criar um macrodesafio estratégico para um aluno do MBA em Agronegócio, no formato de uma situação-problema realista e desafiadora, que será apresentado no início do módulo.

O desafio será personalizado para um aluno com o seguinte perfil:
- Cargo/função: {usuario.get("cargo", "")}
- Região/cadeia ou cultura: {usuario.get("regiao", "")} / {usuario.get("cadeia", "")}
- Desafios enfrentados: {usuario.get("desafios", "")}
- Observações complementares: {usuario.get("observacoes", "")}

O tema do módulo é: {tema_do_modulo}

Sua resposta deve conter:
1. Um cenário narrativo realista, contextualizado no agronegócio brasileiro, com riqueza de dados, personagens, decisões prévias e ambiente econômico ou climático.
2. Uma situação complexa e verossímil, com múltiplos fatores de tensão interligados: mercadológicos, técnicos, familiares, financeiros, ambientais, operacionais ou institucionais.
3. Uma linha de tempo coerente, com decisões passadas, situação presente e horizonte futuro.
4. O texto deve conter entre 4 a 6 parágrafos, com linguagem técnica acessível.
5. Ao final, apresente um macroproblema claro, multifatorial, que será desdobrado ao longo das aulas do módulo.
6. Não forneça nenhuma sugestão de resposta ou caminho de solução.

Importante: esse macrodesafio será desmembrado em 6 microdesafios semanais. Portanto, a última parte do texto deve apontar, com profundidade, qual será o grande desafio estratégico a ser trabalhado durante o módulo.
            """
        else:
            prompt = f"""
Você é um gerador de microdesafios semanais dentro de um modelo de aprendizagem baseado em problemas (PBL) voltado ao agronegócio. Sua tarefa é criar o microdesafio da aula "{tema_da_aula}", que integra o módulo "{tema_do_modulo}", para um aluno com o seguinte perfil:

- Cargo/função: {usuario.get("cargo", "")}
- Região/cadeia ou cultura: {usuario.get("regiao", "")} / {usuario.get("cadeia", "")}
- Desafios enfrentados: {usuario.get("desafios", "")}
- Observações complementares: {usuario.get("observacoes", "")}

O macrodesafio do módulo é este: {texto_macro}

Sua resposta deve conter:

1. Um texto de 3 a 4 parágrafos, que avance a narrativa do macrodesafio, mantendo coerência com o cenário e papel do aluno.
2. A introdução de novos dados e informações técnicas, com explicação suficiente para que o aluno compreenda o contexto, incluindo:
   - Valores numéricos ou projeções
   - Termos técnicos ou políticas públicas explicadas
   - Comparativos ou simulações
   - Impactos de cada alternativa

3. O último parágrafo deve explicitar a tarefa da semana:
   - O que o aluno deve entregar (proposta, análise, planejamento etc.)
   - Critérios a considerar
   - Aspectos que devem ser justificados tecnicamente

Use linguagem técnica, realista e clara. Não ofereça solução.
            """

        # 6. Chamada ao GPT
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.75
        )

        texto_desafio = response.choices[0].message.content.strip()

        # 7. Salvar desafio
        novo = {
            "cpf": cpf,
            "tipo": tipo,
            "texto_desafio": texto_desafio,
            "conteudo_id": conteudo_id
        }
        supabase.table("PBL - desafios").insert(novo).execute()

        return {"status": "sucesso", "desafio": texto_desafio}

    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
