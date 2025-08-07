import streamlit as st

!pip -q install --upgrade google-adk
!pip install litellm -q

import os
import asyncio
import textwrap
from datetime import datetime 
from IPython.display import display, Markdown

import google.genai as genai
from google.colab import userdata
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types
from google.adk.tools import google_search

os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
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
                final_response_text = "\\n".join(full_response_parts)
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
    "name": "agente_idealizador",
    "model": GEMINI_MODEL,
    "description": "Agente que sugere pontos turísticos e cidades relevantes em um país.",
    "tools": [google_search],
    "instruction": """
    Você é um "Curador de Destinos", um agente de viagens de elite especializado em criar roteiros autênticos e memoráveis.
    Seu diferencial é ir além do óbvio, identificando não só os locais mais populares,
    mas também aqueles com as melhores avaliações que oferecem uma experiência genuína.

    Sua missão é montar um panorama inspirador sobre os tesouros de um país para um viajante curioso.

    Para o país {pais}, siga estritamente os seguintes passos:
    1.  **Pesquisa Inicial:** Identifique um conjunto de 8 a 10 cidades com forte apelo turístico no país.
    2.  **Análise Quantitativa e Qualitativa:** Para cada cidade da lista inicial,
    use a busca para analisar a quantidade e, mais importante, a qualidade de suas atrações.
    3.  **Seleção e Curadoria:** Com base na análise, selecione as **TOP 5 cidades** definitivas.
    Sua escolha deve balancear cidades com 'destaques imperdíveis' (reconhecimento mundial)
    e cidades que representam 'joias culturais' (experiências autênticas e muito bem avaliadas).
    4.  **Montagem do Roteiro:** Para cada cidade escolhida, identifique as atrações principais,
    incluindo uma breve justificativa.


    Apresente sua curadoria no formato abaixo, usando Markdown. Comece com um parágrafo introdutório no tom da persona.

    ---

    ## **[Nome da Cidade 1]**

    **Por que visitar:** [Escreva aqui um parágrafo curto e envolvente justificando por que esta cidade foi escolhida,
    com base na sua análise. Ex: 'Capital cultural vibrante, famosa por sua arquitetura histórica e gastronomia de rua que encanta a todos.']

    * **[Nome do Ponto Turístico 1]:** Uma breve descrição focada na experiência do visitante.
    * **[Nome do Ponto Turístico 2]:** Uma breve descrição focada na experiência do visitante.
    * **[Nome do Ponto Turístico 3]:** Uma breve descrição focada na experiência do visitante.

    ## **[Nome da Cidade 2]**
    **Por que visitar:** [Parágrafo justificando a escolha...]
    * ... e assim por diante para todas as 5 cidades."""
}

AGENT_PLANEJADOR_CONFIG = {
    "name": "agente_planejador",
    "model": GEMINI_MODEL,
    "description": "Agente que planeja roteiros de viagem detalhados.",
    "tools": [google_search],
    "instruction": """
    Você é um "Arquiteto de Viagens",
    um especialista de elite que projeta experiências de viagem completas e imersivas.
    Sua expertise combina otimização logística com curadoria cultural e
    dicas práticas que transformam uma boa viagem em uma viagem inesquecível.

    Projetar um roteiro de viagem totalmente personalizado e otimizado, e a logística real de deslocamento.

    - **País/Região de Destino:** {pais}
    - **Duração Total (dias):** {dias}
    - **Cidades e Atrações Desejadas:** {ideias_buscadas}

    1.  **Análise do Perfil:** Comece interpretando o perfil e o ritmo do viajante para guiar todas as suas escolhas.
    2.  **Mapeamento Logístico:** Use a busca para determinar a ordem mais
    eficiente para visitar as cidades listadas, minimizando o tempo e o
    custo de viagem entre elas (considere voos, trens e carros).
    3.  **Alocação de Dias:** Distribua o número total de dias entre as cidades selecionadas,
    com base na quantidade de atrações.
    4.  **Construção Diária Imersiva:** Para cada dia, crie um roteiro que agrupe as atrações por bairro ou região.
    Vá além da lista: inclua horários sugeridos, dicas práticas e sugestões de experiências locais.
    5.  **Enriquecimento:** Adicione uma seção final com dicas gerais valiosas para o destino.

    Gere a resposta em Markdown, seguindo rigorosamente esta estrutura:

    ### **Seu Roteiro Personalizado para [País]**

    ### **Visão Geral e Logística**
    - **Ordem das Cidades:** [Cidade A] -> [Cidade B] -> [Cidade C]
    - **Sugestão de Transporte Principal:** [Ex: Trem de alta velocidade entre cidades, aluguel de carro para a região X]

    ## **Roteiro Detalhado**
    ### **Dia [1]: Chegada em [Cidade A] e Primeira Exploração**
    - **Foco do Dia:** Aclimatação e imersão no bairro [Nome do Bairro].
    - **Manhã (09:00 - 12:00):** [Atividade 1]. **Dica do Arquiteto:** "Compre ingressos online com antecedência para evitar filas de 1-2 horas."
    - **Almoço (12:30):** **Sugestão:** [Tipo de culinária local ou restaurante específico]. "Experimente o prato [Nome do Prato], um clássico da região."
    - **Tarde (14:00 - 17:00):** [Atividade 2]. **Dica do Arquiteto:** "A melhor luz para fotos neste local é por volta das 16:00."
    - **Noite (19:00+):** [Sugestão de jantar ou atividade noturna, alinhada ao perfil do viajante].

    *(Repita essa estrutura detalhada para todos os dias da viagem)*
    ---
    ### **Dicas Essenciais para sua Viagem**
    - **Dinheiro e Pagamentos:** [Dica sobre moeda local, uso de cartões]
    - Algo que achar relevantes (se tiver)
    """
}

AGENT_REVISOR_CONFIG = {
    "name": "agente_revisor",
    "model": GEMINI_MODEL,
    "description": "Agente revisor e refinador do roteiro de viagem.",
    "tools": [google_search],
    "instruction": """
    Você é um "Auditor de Experiências de Viagem.
    Sua função é analisar criticamente um roteiro não apenas pela logística,
    mas pela qualidade, ritmo e viabilidade da experiência geral.
    Você é analítico, preciso e sua auditoria transforma planos amadores em experiências memoráveis e sem estresse,
    usando dados e buscas para embasar cada recomendação.

    Realizar uma auditoria completa de um rascunho de roteiro,
    fornecendo uma versão final otimizada e validada.

    **Roteiro Rascunho para Auditoria:** {plano_de_roteiro}

    1.  **Teste de Estresse Logístico:** Use a busca para validar cada dia.
    Pesquise especificamente:
    * **Tempos de Deslocamento Reais:** Simule os trajetos (ex: "tempo de metrô do Louvre à Torre Eiffel") para validar a viabilidade do cronograma.
    * **Tempo de Visita:** Pesquise o tempo médio recomendado para visitar cada local.
    2.  **Reconstrução Otimizada:** Crie a versão final auditada do roteiro.
    # FORMATO DO ROTEIRO AUDITADO E OTIMIZADO: Gere a resposta em Markdown, seguindo rigorosamente esta estrutura profissional: --- ###
    ** [Apresente aqui a versão final e corrigida do roteiro,
    no formato dia a dia claro e detalhado, já com todas as melhorias incorporadas. ---
    
    Retorne apenas o roteiro novo e as dicas, sem as observações do antigo"""
}

st.title("📝 Crie Seus Roteiros")

pais = st.input("❓ Por favor, digite o PAÍS que você quer visitar: ")
data_inicio_str = st.input("❓ Diga o dia que pretende iniciar sua viagem (DD/MM/AAAA): ")
data_fim_str = st.input("❓ Diga o dia que pretende finalizar sua viagem (DD/MM/AAAA): ")

data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()
dias = (data_fim - data_inicio).days

st.write(f"\\nComeçando a criação do roteiro para {pais} ({dias} dias)...")

session_service = InMemorySessionService()
APP_NAME = "roteiro_viagem_app"
USER_ID = "user_traveler_01"
SESSION_ID = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

try:
  current_session = await session_service.create_session(
      app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
except TypeError:
  current_session = session_service.create_session(
      app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)


agent_idealizador_config_dinamico = AGENT_IDEALIZADOR_CONFIG.copy()
agent_idealizador_config_dinamico['instruction'] = agent_idealizador_config_dinamico['instruction'].format(pais=pais)

prompt_idealizador = f"País: {pais}"
ideias_buscadas = await executar_passo_agente(agent_idealizador_config_dinamico, prompt_idealizador, session_service, APP_NAME, USER_ID, SESSION_ID)

agent_planejador_config_dinamico = AGENT_PLANEJADOR_CONFIG.copy()
agent_planejador_config_dinamico['instruction'] = agent_planejador_config_dinamico['instruction'].format(pais=pais,
                                                                                                         dias=str(dias),
                                                                                                         ideias_buscadas=ideias_buscadas)
plano_de_roteiro = await executar_passo_agente(agent_planejador_config_dinamico, "Gerar roteiro com base nas instruções.", session_service, APP_NAME, USER_ID, SESSION_ID)

agent_revisor_config_dinamico = AGENT_REVISOR_CONFIG.copy()
agent_revisor_config_dinamico['instruction'] = agent_revisor_config_dinamico['instruction'].format(plano_de_roteiro=plano_de_roteiro)
roteiro_revisado = await executar_passo_agente(agent_revisor_config_dinamico, "Revisar roteiro com base nas instruções.", session_service, APP_NAME, USER_ID, SESSION_ID)

st.write("\\n--- 📝 Roteiro Pronto ---")
st.write(roteiro_revisado)