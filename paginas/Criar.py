import streamlit as st
import os
import asyncio
from datetime import datetime

import google.generativeai as genai
from google.generativeai import types as genai_types
from google.generativeai.client import Client

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import google_search

os.environ['GOOGLE_API_KEY'] = st.secrets["GOOGLE_API_KEY"]
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
genai.Client()

async def call_agent_final_response(
    agent_under_test: Agent,
    message_text: str,
    runner_obj: Runner,
    user_id_val: str,
    session_id_val: str
) -> str:
    content = genai_types.Content(role='user', parts=[genai_types.Part(text=message_text)])
    final_response_text = f"O Agente ({agent_under_test.name}) não produziu uma resposta final."
    full_response_parts = []

    async for event in runner_obj.run_async(user_id=user_id_val, session_id=session_id_val, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                full_response_parts.extend(part.text for part in event.content.parts if part.text)
            elif event.actions and event.actions.escalate:
                full_response_parts.append(f"Agente escalonado: {event.error_message or 'Nenhuma mensagem específica.'}")

            if full_response_parts:
                final_response_text = "\n".join(full_response_parts)
            break
    return final_response_text

async def executar_passo_agente(
    agent_config: dict,
    prompt: str,
    session_service: InMemorySessionService,
    app_name: str,
    user_id: str,
    session_id: str
) -> str:
    agent = Agent(**agent_config)
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
    response = await call_agent_final_response(agent, prompt, runner, user_id, session_id)
    return response

GEMINI_MODEL = "gemini-2.0-flash"

AGENT_IDEALIZADOR_CONFIG = {
    "name": "agente_idealizador", "model": GEMINI_MODEL, "description": "Agente que sugere pontos turísticos e cidades relevantes em um país.", "tools": [google_search],
    "instruction": """Você é um "Curador de Destinos", um agente de viagens de elite especializado em criar roteiros autênticos e memoráveis. Sua missão é montar um panorama inspirador sobre os tesouros de um país para um viajante curioso. Para o país {pais}, siga estritamente os seguintes passos: 1. **Pesquisa Inicial:** Identifique um conjunto de 8 a 10 cidades com forte apelo turístico no país. 2. **Análise Quantitativa e Qualitativa:** Para cada cidade da lista inicial, use a busca para analisar a quantidade e, mais importante, a qualidade de suas atrações. 3. **Seleção e Curadoria:** Com base na análise, selecione as **TOP 5 cidades** definitivas. Sua escolha deve balancear cidades com 'destaques imperdíveis' e 'joias culturais'. 4. **Montagem do Roteiro:** Para cada cidade escolhida, identifique as atrações principais, incluindo uma breve justificativa. Apresente sua curadoria no formato abaixo, usando Markdown. Comece com um parágrafo introdutório no tom da persona. --- ## **[Nome da Cidade 1]** **Por que visitar:** [Escreva aqui um parágrafo curto e envolvente justificando por que esta cidade foi escolhida.] * **[Nome do Ponto Turístico 1]:** Uma breve descrição focada na experiência do visitante. * **[Nome do Ponto Turístico 2]:** Uma breve descrição focada na experiência do visitante. * **[Nome do Ponto Turístico 3]:** Uma breve descrição focada na experiência do visitante. ## **[Nome da Cidade 2]** **Por que visitar:** [Parágrafo justificando a escolha...] * ... e assim por diante para todas as 5 cidades."""
}
AGENT_PLANEJADOR_CONFIG = {
    "name": "agente_planejador", "model": GEMINI_MODEL, "description": "Agente que planeja roteiros de viagem detalhados.", "tools": [google_search],
    "instruction": """Você é um "Arquiteto de Viagens", um especialista de elite que projeta experiências de viagem completas. Projetar um roteiro de viagem totalmente personalizado e otimizado. - **País/Região de Destino:** {pais} - **Duração Total (dias):** {dias} - **Cidades e Atrações Desejadas:** {ideias_buscadas}. 1. **Mapeamento Logístico:** Use a busca para determinar a ordem mais eficiente para visitar as cidades listadas. 2. **Alocação de Dias:** Distribua o número total de dias entre as cidades selecionadas. 3. **Construção Diária Imersiva:** Para cada dia, crie um roteiro que agrupe as atrações por bairro ou região. 4. **Enriquecimento:** Adicione uma seção final com dicas gerais valiosas para o destino. Gere a resposta em Markdown, seguindo rigorosamente esta estrutura: ### **Seu Roteiro Personalizado para [País]** ### **Visão Geral e Logística** - **Ordem das Cidades:** [Cidade A] -> [Cidade B] -> [Cidade C]. - **Sugestão de Transporte Principal:** [Ex: Trem de alta velocidade]. ## **Roteiro Detalhado** ### **Dia [1]: Chegada em [Cidade A]** - **Foco do Dia:** Aclimatação. - **Manhã (09:00 - 12:00):** [Atividade 1]. **Dica:** "Compre ingressos online." - **Almoço (12:30):** **Sugestão:** [Culinária local]. - **Tarde (14:00 - 17:00):** [Atividade 2]. - **Noite (19:00+):** [Sugestão de jantar]. *(Repita para todos os dias)* --- ### **Dicas Essenciais** - **Dinheiro:** [Dica sobre moeda]"""
}
AGENT_REVISOR_CONFIG = {
    "name": "agente_revisor", "model": GEMINI_MODEL, "description": "Agente revisor e refinador do roteiro de viagem.", "tools": [google_search],
    "instruction": """Você é um "Auditor de Experiências de Viagem". Sua função é analisar criticamente um roteiro. **Roteiro Rascunho para Auditoria:** {plano_de_roteiro}. 1. **Teste de Estresse Logístico:** Use a busca para validar cada dia (tempos de deslocamento, tempo de visita). 2. **Reconstrução Otimizada:** Crie a versão final auditada do roteiro. # FORMATO DO ROTEIRO AUDITADO E OTIMIZADO: Gere a resposta em Markdown, apresentando a versão final e corrigida do roteiro. Retorne apenas o roteiro novo e as dicas, sem as observações do antigo."""
}


async def gerar_roteiro_completo(pais, dias):
    session_service = InMemorySessionService()
    APP_NAME = "roteiro_viagem_app"
    USER_ID = "user_traveler_01"
    SESSION_ID = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # As chamadas de criação de sessão podem variar, ajuste se necessário
    try:
        await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    except (TypeError, AttributeError):
         session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    with st.status("Fase 1: Buscando ideias de destinos...", expanded=True) as status:
        agent_idealizador_config_dinamico = AGENT_IDEALIZADOR_CONFIG.copy()
        agent_idealizador_config_dinamico['instruction'] = agent_idealizador_config_dinamico['instruction'].format(pais=pais)
        prompt_idealizador = f"País: {pais}"
        ideias_buscadas = await executar_passo_agente(agent_idealizador_config_dinamico, prompt_idealizador, session_service, APP_NAME, USER_ID, SESSION_ID)
        st.write("Cidades e atrações principais identificadas.")
        status.update(label="Fase 1: Concluída!", state="complete")

    with st.status("Fase 2: Planejando o roteiro dia a dia...", expanded=True) as status:
        agent_planejador_config_dinamico = AGENT_PLANEJADOR_CONFIG.copy()
        agent_planejador_config_dinamico['instruction'] = agent_planejador_config_dinamico['instruction'].format(pais=pais, dias=str(dias), ideias_buscadas=ideias_buscadas)
        plano_de_roteiro = await executar_passo_agente(agent_planejador_config_dinamico, "Gerar roteiro com base nas instruções.", session_service, APP_NAME, USER_ID, SESSION_ID)
        st.write("Logística e cronograma diário definidos.")
        status.update(label="Fase 2: Concluída!", state="complete")

    with st.status("Fase 3: Revisando e otimizando a experiência...", expanded=True) as status:
        agent_revisor_config_dinamico = AGENT_REVISOR_CONFIG.copy()
        agent_revisor_config_dinamico['instruction'] = agent_revisor_config_dinamico['instruction'].format(plano_de_roteiro=plano_de_roteiro)
        roteiro_revisado = await executar_passo_agente(agent_revisor_config_dinamico, "Revisar roteiro com base nas instruções.", session_service, APP_NAME, USER_ID, SESSION_ID)
        st.write("Roteiro final validado.")
        status.update(label="Fase 3: Concluída!", state="complete")

    return roteiro_revisado

st.title("📝 Crie Seus Roteiros")
st.header("Preencha os campos abaixo para que nossa IA monte a viagem dos seus sonhos.")

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
            
            roteiro_final = asyncio.run(gerar_roteiro_completo(pais, dias))
            st.balloons()
            st.divider()
            st.header("🎉 Seu Roteiro Personalizado está Pronto!")
            st.markdown(roteiro_final)
