import os
from dotenv import load_dotenv
load_dotenv()


from supabase import create_client
from functools import lru_cache

@lru_cache
def get_supabase():
    return create_client(os.environ["SUPABASE_URL"], os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_API_KEY"))


from supabase import create_client
from openai import OpenAI
from datetime import datetime, date

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
# supabase client moved to get_supabase()
openai = OpenAI(api_key=OPENAI_KEY)

def verificar_se_ja_esta_liberado(conteudo_id: str, turma: str) -> bool:
    hoje = date.today().isoformat()

    resultado = get_supabase().table("PBL - liberacoes_agendadas") \
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
        usuario = get_supabase().table("PBL - usuarios").select("*").eq("cpf", cpf).single().execute().data
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

        cronogramas = get_supabase().table("PBL - cronograma") \
            .select("*,conteudo_id") \
            .eq("turma", turma) \
            .order("ordem") \
            .execute().data

        if not cronogramas:
            return {"status": "erro", "mensagem": "Nenhum conteúdo encontrado para a turma"}

        gerados = []

        for c in cronogramas:
            conteudo_id = c["conteudo_id"]
            conteudo = get_supabase().table("PBL - conteudo").select("*").eq("id", conteudo_id).single().execute().data

            if not conteudo or not conteudo.get("modulo"):
                continue

            modulo = conteudo["modulo"]
            ementa = conteudo.get("ementa", "")

            existe_macro = get_supabase().table("PBL - desafios").select("id") \
                .eq("cpf", cpf).eq("conteudo_id", conteudo_id).eq("tipo", "macro") \
                .execute().data

            texto_macro = None  # predef to avoid UnboundLocalError when macro already exists
            if not existe_macro:
                prompt_macro = f"""
Você é um gerador de desafios educacionais no modelo Problem-Based Learning (PBL), voltado para profissionais do agronegócio.

Sua tarefa é criar um cenário-problema estratégico para um aluno do MBA em Agronegócio, que servirá como base para atividades posteriores.

Perfil do aluno:
{perfil}

O tema do módulo é: **{modulo}**
Ementa da disciplina:
{ementa}

Regras e Diretrizes para sua resposta:
1. Use as informações fornecidas no perfil, no tema e na ementa como ponto de partida, mas explore também aspectos mais amplos e correlatos que sejam plausíveis e relevantes ao contexto do aluno.
2. Considere o agronegócio brasileiro em 2025, utilizando dados atuais, políticas públicas, regulamentações, tendências de mercado e inovações tecnológicas pertinentes — sempre explicando brevemente cada conceito ou política citada.
3. Crie um cenário narrativo realista, formal e objetivo, evitando elementos lúdicos ou fictícios sem fundamento.
4. Apresente uma situação complexa, multifatorial e interligada, incluindo fatores econômicos, ambientais, regulatórios, logísticos, climáticos e/ou sociais que influenciem direta ou indiretamente o contexto do aluno.
5. Conecte passado, presente e futuro por meio de uma linha de tempo coerente, destacando decisões anteriores, a situação atual e as perspectivas futuras.
6. Escreva entre 3 e 5 parágrafos, em linguagem técnica acessível, mas com profundidade conceitual, podendo incluir termos técnicos acompanhados de explicação.
7. Não utilize tópicos ou listas — o texto deve fluir como narrativa contínua, sem mencionar termos como “macrodesafio” ou qualquer referência à estrutura interna da atividade.
8. Ao final, formule de maneira clara a questão central ou problema, que deve ser multifatorial e provocar reflexão estratégica, alinhado ao contexto construído.
9. **Não forneça soluções** para o problema.
                """

                resposta_macro = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt_macro}],
                    temperature=0.7
                )

                texto_macro = resposta_macro.choices[0].message.content.strip()
                desafio_liberado = verificar_se_ja_esta_liberado(conteudo_id, turma)

                get_supabase().table("PBL - desafios").insert({
                    "cpf": cpf,
                    "tipo": "macro",
                    "conteudo_id": conteudo_id,
                    "texto_desafio": texto_macro,
                    "data_criacao": datetime.utcnow().isoformat(),
                    "desafio_liberado": desafio_liberado,
                    "status_gerado": "ok"
                }).execute()

                gerados.append(f"Macrodesafio: {modulo}")

            aulas = get_supabase().table("PBL - conteudo") \
                .select("*") \
                .eq("modulo", modulo) \
                .not_.is_("aula", "null") \
                .eq("ativo", True) \
                .execute().data

            if texto_macro is None:  # fallback to fetch existing macro (macro já existia)
                _macro_rows = get_supabase().table("PBL - desafios").select("texto_desafio") \
                    .eq("cpf", cpf).eq("conteudo_id", conteudo_id).eq("tipo", "macro") \
                    .limit(1).execute().data
                if _macro_rows:
                    texto_macro = (_macro_rows[0].get("texto_desafio") or "").strip()
                else:
                    texto_macro = ""


                for aula in aulas:
                    aula_nome = aula["aula"]
                    conteudo_aula_id = aula["id"]
                    ementa_aula = aula.get("ementa", "")

                    existe_micro = get_supabase().table("PBL - desafios").select("id") \
                        .eq("cpf", cpf).eq("conteudo_id", conteudo_aula_id).eq("tipo", "micro") \
                        .execute().data

                    if not existe_micro:
                        prompt_micro = f"""
Você é um gerador de desafios semanais dentro do modelo Problem-Based Learning (PBL) para o agronegócio.

Perfil do aluno:
{perfil}

O cenário-problema do módulo é:
{texto_macro}

Módulo: {modulo}
Aula: {aula_nome}
Ementa da aula:
{ementa_aula}

Regras e Diretrizes para sua resposta:
1. Dê continuidade direta à narrativa apresentada no cenário-problema do módulo, mantendo total coerência de contexto, tom e linha de tempo.
2. Use as informações do perfil, do cenário-problema e da ementa como base, mas amplie a abordagem trazendo aspectos correlatos e complementares que sejam plausíveis e relevantes ao tema da aula.
3. Considere o cenário real do agronegócio brasileiro em 2025, utilizando dados atuais, políticas públicas, regulamentações, tendências de mercado e inovações tecnológicas pertinentes — sempre explicando brevemente cada conceito ou dado mencionado.
4. Apresente novos elementos e dados técnicos relevantes ao tema da aula (ex.: projeções de mercado, estudos de caso, análises comparativas, explicações de termos técnicos, mudanças regulatórias recentes).
5. Mantenha o foco em provocar reflexão estratégica e aplicação prática do conteúdo, conectando os impactos das decisões no curto, médio e longo prazo.
6. Escreva entre 3 e 4 parágrafos, em linguagem formal e técnica acessível, podendo incluir termos técnicos acompanhados de explicação.
7. No último parágrafo, formule a tarefa da semana como um desafio prático de **análise crítica**, sem exigir ações externas como entrevistas, pesquisas de campo ou coleta de dados no mundo real.
8. Não utilize listas ou tópicos — a resposta deve fluir como narrativa contínua, sem mencionar termos como “microdesafio” ou qualquer referência à estrutura interna da atividade.
9. **Não forneça soluções** para a tarefa.
                        """

                        resposta_micro = openai.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": prompt_micro}],
                            temperature=0.7
                        )

                        texto_micro = resposta_micro.choices[0].message.content.strip()
                        titulo = gerar_titulo_microdesafio(texto_micro, aula_nome)
                        desafio_liberado = verificar_se_ja_esta_liberado(conteudo_aula_id, turma)

                        get_supabase().table("PBL - desafios").insert({
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
