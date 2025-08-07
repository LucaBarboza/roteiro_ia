# paginas/Criar.py

import streamlit as st
import os
import asyncio
from datetime import datetime

# --- PONTO DE INTEGRAÇÃO CRÍTICO: Usando apenas a biblioteca estável ---
try:
    import google.generativeai as genai
except ImportError as e:
    st.error("Não foi possível importar 'google.generativeai'. Verifique se 'google-generativeai' está no seu requirements.txt.")
    st.stop()


# --- CONFIGURAÇÃO SEGURA DA API KEY ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except (KeyError, FileNotFoundError):
    st.error("A chave GOOGLE_API_KEY não foi encontrada nos segredos do Streamlit.")
    st.info("Por favor, adicione sua chave ao arquivo .streamlit/secrets.toml")
    st.code('GOOGLE_API_KEY="sua_chave_aqui"')
    st.stop()
except Exception as auth_e:
    st.error(f"Ocorreu um erro ao configurar a API do Google: {auth_e}")
    st.stop()


# --- DEFINIÇÃO DOS "AGENTES" COMO PROMPTS ---
# Em vez de usar a biblioteca ADK, definimos cada "agente" como um prompt para o modelo Gemini.
GEMINI_MODEL = "gemini-1.5-flash"

PROMPT_IDEALIZADOR = """
Você é um "Curador de Destinos". Sua missão é montar um panorama inspirador sobre os tesouros de um país.
Para o país {pais}, siga os passos:
1.  Pesquise e liste 8-10 cidades turísticas.
2.  Analise a qualidade das atrações de cada uma.
3.  Selecione as TOP 5 cidades.
4.  Para cada cidade, identifique 3 atrações principais com uma breve justificativa.
Apresente a resposta de forma concisa, focada nos nomes das cidades e atrações.
"""

PROMPT_PLANEJADOR = """
Você é um "Arquiteto de Viagens".
Com base nas seguintes ideias de cidades e atrações:
{ideias_buscadas}

Projete um roteiro para {pais} com {dias} dias.
1.  Determine a ordem mais eficiente para visitar as cidades.
2.  Distribua os dias entre elas.
3.  Crie um rascunho de roteiro diário (manhã, tarde, noite).
Apresente um plano claro e estruturado.
"""

PROMPT_REVISOR = """
Você é um "Auditor de Experiências".
Analise criticamente o rascunho de roteiro a seguir:
{plano_de_roteiro}

Sua tarefa é refinar e otimizar este plano.
1.  Verifique se o ritmo é realista. Agrupe atividades por localização para minimizar deslocamentos.
2.  Adicione dicas práticas (transporte, ingressos, sugestões de restaurantes).
3.  Formate a saída final em Markdown de alta qualidade, como um roteiro profissional pronto para ser entregue ao cliente.
Retorne APENAS o roteiro final e otimizado.
"""

# --- LÓGICA PRINCIPAL ASSÍNCRONA ---
async def gerar_roteiro_completo(pais, dias):
    model = genai.GenerativeModel(GEMINI_MODEL)

    with st.status("Fase 1: Gerando ideias de destinos...", expanded=True) as status:
        prompt = PROMPT_IDEALIZADOR.format(pais=pais)
        response_idealizador = await model.generate_content_async(prompt)
        ideias_buscadas = response_idealizador.text
        status.update(label="Fase 1: Concluída!", state="complete")

    with st.status("Fase 2: Planejando o rascunho do roteiro...", expanded=True) as status:
        prompt = PROMPT_PLANEJADOR.format(pais=pais, dias=dias, ideias_buscadas=ideias_buscadas)
        response_planejador = await model.generate_content_async(prompt)
        plano_de_roteiro = response_planejador.text
        status.update(label="Fase 2: Concluída!", state="complete")

    with st.status("Fase 3: Refinando e finalizando a experiência...", expanded=True) as status:
        prompt = PROMPT_REVISOR.format(plano_de_roteiro=plano_de_roteiro)
        response_revisor = await model.generate_content_async(prompt)
        roteiro_revisado = response_revisor.text
        status.update(label="Fase 3: Concluída!", state="complete")

    return roteiro_revisado

# --- INTERFACE DO STREAMLIT (UI) ---
st.title("📝 Crie Seus Roteiros")
st.write("Preencha os campos abaixo para que nossa IA monte a viagem dos seus sonhos.")

with st.form("form_roteiro"):
    pais = st.text_input("Qual o país que você quer visitar?")
    data_inicio_str = st.date_input("Data de início da viagem", format="DD/MM/YYYY")
    data_fim_str = st.date_input("Data de fim da viagem", format="DD/MM/YYYY")
    submitted = st.form_submit_button("Gerar Roteiro Mágico ✨")
    if submitted:
        if not pais or not data_inicio_str or not data_fim_str:
            st.error("Por favor, preencha todos os campos.")
        elif data_inicio_str >= data_fim_str:
            st.error("A data de fim deve ser posterior à data de início.")
        else:
            dias = (data_fim_str - data_inicio_str).days
            st.info(f"Preparando um roteiro de {dias} dias para {pais}. Isso pode levar um momento...")
            try:
                roteiro_final = asyncio.run(gerar_roteiro_completo(pais, dias))
                st.balloons()
                st.divider()
                st.header("🎉 Seu Roteiro Personalizado está Pronto!")
                st.markdown(roteiro_final)
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o roteiro: {e}")
                st.exception(e)