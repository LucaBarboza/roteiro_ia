import streamlit as st
import os
import asyncio
from datetime import datetime
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

GEMINI_MODEL = "gemini-2.0-flash"

PROMPT_IDEALIZADOR = """Você é um "Curador de Destinos", um agente de viagens de elite especializado em criar roteiros autênticos e memoráveis.
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

PROMPT_PLANEJADOR = """
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
    - ** [Atividade 1]. ** Dica: **"Compre ingressos online com antecedência para evitar filas de 1-2 horas."
    - **Sugestão:** [Tipo de culinária local]. "Experimente o prato [Nome do Prato], um clássico da região."
    - **[Atividade 2]. ** Dica: ** "A melhor luz para fotos neste local é por volta das 16:00."
    - ** [Sugestão de comida e/ou atividade noturna, alinhada ao perfil do viajante].
    - ** continue...
    
    *(Repita essa estrutura detalhada para todos os dias da viagem)*
    ---
    ### **Dicas Essenciais para sua Viagem**
    - **Dinheiro e Pagamentos:** [Dica sobre moeda local, uso de cartões]
    - Algo que achar relevantes (se tiver)
    """

PROMPT_REVISOR = """
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
    3.  Formate a saída final em Markdown de alta qualidade, como um roteiro profissional pronto para ser entregue ao cliente.
    
    Retorne APENAS o roteiro final e otimizado.
    """

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

###################
@st.cache_resource
def conectar_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = conectar_firebase()
colecao = 'usuarios2'
##############

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

            novo_roteiro = roteiro_final
            user_ref = db.collection(colecao).document(st.user.email)
            doc = user_ref.get()
            dados = doc.to_dict() if doc.exists else {}
    
            if 'roteiros' not in dados:
                dados['roteiros'] = []
    
            dados['roteiros'].append({
            'texto': novo_roteiro,
            'pais': pais
            })
            user_ref.set(dados)
            st.success("Roteiro salvo!")