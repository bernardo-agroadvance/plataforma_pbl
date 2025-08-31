# fastapi_backend/gerar_desafios.py
import os
import traceback
from datetime import datetime, date
from openai import OpenAI
from .db import get_supabase_client

# --- Configuração Inicial ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("A variável de ambiente OPENAI_API_KEY é necessária.")
openai = OpenAI(api_key=OPENAI_KEY)


# --- Funções Auxiliares ---
def gerar_titulo_microdesafio(texto_desafio: str, aula: str) -> str:
    """Gera um título curto e atrativo para um microdesafio usando a IA."""
    prompt = f"""Gere um título curto e atrativo (máximo 6 palavras) para o microdesafio a seguir, contextualizado pela aula.
Texto do microdesafio: {texto_desafio}
Nome da aula: {aula}
Título:"""
    try:
        resposta = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=20
        )
        return resposta.choices[0].message.content.strip().replace('"', '')
    except Exception as e:
        print(f"[GERADOR_TITULO] Erro ao gerar título: {e}")
        return "Título não gerado"


# --- Função Principal de Geração ---
def gerar_todos_os_desafios(cpf: str):
    """
    Processo completo para gerar todos os desafios (macros e micros) para um usuário
    baseado em seu perfil e nos conteúdos ativos.
    """
    print(f"--- [GERADOR] Iniciando geração COMPLETA para CPF: {cpf} ---")
    supabase = get_supabase_client()
    try:
        # 1. Busca Usuário
        user_res = supabase.table("PBL - usuarios").select("nome, turma, cargo, regiao, cadeia, desafios, observacoes").eq("cpf", cpf).single().execute()
        if not user_res or not user_res.data:
            print(f"[GERADOR] ERRO FATAL: Falha ao buscar usuário {cpf} ou usuário não existe.")
            return
        usuario = user_res.data
        turma = usuario.get("turma")
        print(f"[GERADOR] Usuário encontrado: {usuario.get('nome')}, Turma: {turma}")

        # 2. Monta o Perfil do Aluno para a IA
        perfil = f"""- Cargo/função: {usuario.get("cargo", "N/A")}
- Região/cadeia ou cultura: {usuario.get("regiao", "N/A")} / {usuario.get("cadeia", "N/A")}
- Desafios enfrentados: {usuario.get("desafios", "N/A")}
- Observações: {usuario.get("observacoes", "N/A")}"""

        # 3. Busca Conteúdos Ativos
        conteudos_res = supabase.table("PBL - conteudo").select("*").eq("ativo", True).execute()
        if not conteudos_res or not conteudos_res.data:
            print("[GERADOR] ERRO FATAL: Nenhum conteúdo ativo encontrado no banco.")
            return
        print(f"[GERADOR] {len(conteudos_res.data)} conteúdos ativos encontrados.")

        # 4. Agrupa Conteúdos por Módulo
        modulos = {}
        for c in conteudos_res.data:
            nome_modulo = c.get("modulo")
            if nome_modulo:
                if nome_modulo not in modulos:
                    modulos[nome_modulo] = {"macro_info": None, "micros_info": []}
                if not c.get("aula"): # Se não tem nome de aula, é o macro
                    modulos[nome_modulo]["macro_info"] = c
                else: # Se tem nome de aula, é um micro
                    modulos[nome_modulo]["micros_info"].append(c)

        # 5. Itera sobre cada Módulo para gerar desafios
        for nome_modulo, info_modulo in modulos.items():
            macro_info = info_modulo.get("macro_info")
            if not macro_info:
                print(f"[GERADOR] AVISO: Módulo '{nome_modulo}' pulado (sem conteúdo principal/macro).")
                continue

            # --- GERAÇÃO DO MACRODESAFIO ---
            texto_macro = ""
            macro_existente_res = supabase.table("PBL - desafios").select("texto_desafio").eq("cpf", cpf).eq("conteudo_id", macro_info["id"]).eq("tipo", "macro").maybe_single().execute()
            
            if macro_existente_res and macro_existente_res.data:
                texto_macro = macro_existente_res.data.get("texto_desafio", "")
                print(f"[GERADOR] Macro para '{nome_modulo}' já existe.")
            else:
                print(f"[GERADOR-IA] Criando Macro para '{nome_modulo}'...")
                prompt_macro = f"Você é um gerador de desafios (PBL) para um MBA em Agronegócio. Crie um cenário-problema multifatorial.\nPerfil do Aluno: {perfil}\nTema do Módulo: {nome_modulo}\nEmenta: {macro_info.get('ementa', '')}\nRegras: Crie uma narrativa realista de 3-5 parágrafos no contexto do agro brasileiro em 2025. Apresente uma situação complexa e termine com um problema central claro, sem oferecer soluções."
                resposta_macro = openai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_macro}], temperature=0.7)
                texto_macro = resposta_macro.choices[0].message.content.strip()
                
                # Desafios são criados como NÃO liberados por padrão
                supabase.table("PBL - desafios").insert({
                    "cpf": cpf, "tipo": "macro", "conteudo_id": macro_info["id"], 
                    "texto_desafio": texto_macro, "data_criacao": datetime.utcnow().isoformat(), 
                    "desafio_liberado": False, "status_gerado": "ok"
                }).execute()
                print(f"[GERADOR-IA] Macro para '{nome_modulo}' criado.")

            if not texto_macro:
                print(f"[GERADOR] AVISO: Texto do macro para '{nome_modulo}' está vazio. Pulando micros.")
                continue

            # --- GERAÇÃO DOS MICRODESAFIOS ---
            for aula_info in info_modulo["micros_info"]:
                micro_existente_res = supabase.table("PBL - desafios").select("id").eq("cpf", cpf).eq("conteudo_id", aula_info["id"]).eq("tipo", "micro").maybe_single().execute()
                if not (micro_existente_res and micro_existente_res.data):
                    print(f"[GERADOR-IA] Criando Micro para '{aula_info['aula']}'...")
                    prompt_micro = f"Você é um gerador de desafios semanais (PBL). Continue a narrativa do cenário-problema, focando no tema da aula.\nCenário-Problema: {texto_macro}\nPerfil: {perfil}\nMódulo: {nome_modulo}\nAula: {aula_info['aula']}\nEmenta: {aula_info.get('ementa', '')}\nRegras: Escreva 3-4 parágrafos, com novos dados técnicos. No último parágrafo, formule uma tarefa prática de análise crítica. Não dê soluções."
                    resposta_micro = openai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_micro}], temperature=0.7)
                    texto_micro = resposta_micro.choices[0].message.content.strip()
                    titulo = gerar_titulo_microdesafio(texto_micro, aula_info['aula'])
                    
                    # Desafios são criados como NÃO liberados por padrão
                    supabase.table("PBL - desafios").insert({
                        "cpf": cpf, "tipo": "micro", "conteudo_id": aula_info["id"], 
                        "texto_desafio": texto_micro, "data_criacao": datetime.utcnow().isoformat(), 
                        "desafio_liberado": False, "titulo": titulo, "status_gerado": "ok"
                    }).execute()
                    print(f"[GERADOR-IA] Micro para '{aula_info['aula']}' criado.")

    except Exception as e:
        print(f"[GERADOR] ERRO CRÍTICO no processo de geração:")
        traceback.print_exc()
    
    print(f"--- [GERADOR] Finalizado para CPF: {cpf} ---")