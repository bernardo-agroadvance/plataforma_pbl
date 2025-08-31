# fastapi_backend/avaliador.py
import os
import openai
import re
from .db import get_supabase_client # <-- MUDANÇA AQUI

openai.api_key = os.getenv("OPENAI_API_KEY")

def avaliar_resposta_com_ia(resposta_do_aluno: str, texto_microdesafio: str, tentativa: int) -> tuple:
    prompt = f"""
Você é um avaliador automático de microdesafios do modelo Problem-Based Learning (PBL), aplicado ao MBA em Agronegócio. Avalie a resposta do aluno com rigor técnico e consistência, atuando como um professor experiente que busca o desenvolvimento do estudante.

Critérios de avaliação (analise todos com atenção):
1. Clareza da resposta — a estrutura está lógica e a mensagem é compreensível?
2. Uso dos dados apresentados — as informações do enunciado foram utilizadas de forma correta e relevante?
3. Raciocínio técnico — as decisões fazem sentido do ponto de vista técnico e estratégico no contexto do agronegócio?
4. Coerência com o conteúdo da aula — a resposta está alinhada com os conceitos ensinados na semana?
5. Profundidade analítica — há justificativas, previsões, análise de impactos, riscos ou conexões relevantes?

Regras importantes para atribuição de nota:
- Nota mínima de aprovação: 7,0. 
- Se o aluno demonstrar compreensão do problema e apresentar uma resposta lógica, realista e baseada nos dados fornecidos, deve ser aprovado, mesmo que não seja exaustiva.
- Seja tolerante com abordagens criativas e diferentes, desde que atendam aos critérios.
- Não aprove respostas vagas ou claramente automatizadas que não demonstrem raciocínio próprio.
- Justifique claramente a nota atribuída.

Microdesafio:
{texto_microdesafio}

Resposta do aluno:
{resposta_do_aluno}

Sua tarefa é retornar:
- Uma nota de 0 a 10 (com 1 casa decimal).
- Um feedback construtivo e formal, mas motivador, que:
  - Explique por que a nota foi atribuída.
  - Destaque pontos positivos.
  - Indique lacunas, erros conceituais ou aspectos que poderiam ser melhorados.
  - Dê orientações para que o aluno desenvolva uma resposta mais completa, sem entregar soluções prontas (a não ser que seja a última tentativa).
- Se esta for a última tentativa do aluno (ou tentativa definitiva), ao final do feedback inclua também **uma resposta ideal**:
  - Essa resposta ideal deve atender a todos os critérios e ser um exemplo que receberia nota 10.
  - Use linguagem clara e acessível.
  - Lembre que existem diferentes formas corretas de responder; forneça uma entre as possíveis, construída exclusivamente com base nos dados do desafio e nos conceitos da aula.
{"- Inclua essa resposta ideal ao final." if tentativa >= 3 else ""}
"""

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        resposta_modelo = completion.choices[0].message.content or ""

        nota_match = re.search(r"nota[:\-]?\s*(\d+(?:[.,]\d+)?)", resposta_modelo, re.IGNORECASE)
        nota = float(nota_match.group(1).replace(",", ".")) if nota_match else 0.0

        resposta_sem_nota = re.sub(r"(?i)^nota[:\-]?\s*\d+(?:[.,]\d+)?\s*", "", resposta_modelo, flags=re.MULTILINE)

        resposta_ideal = ""
        feedback = resposta_sem_nota.strip()

        if "resposta ideal" in feedback.lower():
            partes = re.split(r"resposta ideal[:\-]?", feedback, flags=re.IGNORECASE)
            feedback = partes[0].strip()
            resposta_ideal = partes[1].strip() if len(partes) > 1 else ""

        return nota, feedback, resposta_ideal

    except Exception as e:
        print("Erro na avaliação com IA:", e)
        return 0.0, "Não foi possível gerar feedback neste momento.", ""