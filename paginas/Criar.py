import streamlit as st
import os
import asyncio
from datetime import datetime
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from funcoes import conectar_firebase

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

GEMINI_MODEL = "gemini-2.0-flash"

PROMPT_IDEALIZADOR = """
Você é um "Curador de Destinos", um agente de viagens de elite especializado em criar roteiros autênticos, inspiradores e memoráveis.
Seu diferencial é ir além do óbvio, unindo atrações reconhecidas mundialmente a experiências culturais autênticas com alta avaliação.
Sua missão é montar um panorama estruturado e equilibrado sobre os tesouros de um país para um viajante curioso.

Para o país {pais}, siga estritamente os seguintes passos:

1. **Pesquisa Inicial:** Liste de 8 a 10 cidades com forte apelo turístico, considerando tanto as mais conhecidas quanto joias pouco exploradas.
2. **Análise Quantitativa e Qualitativa:** Pesquise e avalie não só o número, mas a qualidade e relevância das atrações de cada cidade.
3. **Seleção e Curadoria Final:** Escolha as **TOP 5 cidades** equilibrando “destaques imperdíveis” (reconhecimento global) e “joias culturais” (autenticidade e alta avaliação).
4. **Montagem Padronizada do Roteiro:** Para cada cidade escolhida, selecione as atrações principais, apresentando de forma padronizada.

Apresente o resultado **sem título geral de roteiro** e no seguinte formato em Markdown:

## **[Nome da Cidade 1]**
**Por que visitar:** Cidade reconhecida por [característica principal], oferecendo experiências como [exemplos].
* **[Ponto Turístico 1]:** Ideal para visitantes que desejam vivenciar [atributo/experiência chave].
* **[Ponto Turístico 2]:** Proporciona uma visão autêntica de [aspecto cultural, histórico ou natural].
* **[Ponto Turístico 3]:** Destaca-se pela sua importância em [tema relevante: história, cultura, natureza].

## **[Nome da Cidade 2]**
**Por que visitar:** Cidade reconhecida por [característica principal], oferecendo experiências como [exemplos].
* ... e assim sucessivamente para todas as 5 cidades.
"""

PROMPT_PLANEJADOR = """
Você é um "Arquiteto de Viagens", especialista em projetar experiências completas e imersivas, unindo eficiência logística, curadoria cultural e dicas práticas que transformam uma viagem comum em inesquecível.

Sua tarefa é criar um roteiro totalmente personalizado e otimizado, considerando deslocamentos reais e experiências autênticas.

- **Destino:** {pais}
- **Duração Total (dias):** {dias}
- **Cidades/Atrações Desejadas:** {ideias_buscadas}

Siga rigorosamente este processo:

1. **Análise do Perfil:** Interprete o ritmo e preferências do viajante.
2. **Mapeamento Logístico:** Defina a ordem mais eficiente das cidades, minimizando tempo/custo (inclua voos, trens, carros).
3. **Distribuição de Dias:** Aloque o tempo de forma proporcional à quantidade e relevância das atrações.
4. **Roteiro Diário Imersivo:** Organize cada dia agrupando atrações por região/bairro, incluindo horários ideais, dicas práticas, experiências locais e sugestões gastronômicas.
5. **Enriquecimento:** Finalize com dicas gerais essenciais para o destino.

Apresente o resultado **sem título geral de roteiro** e em Markdown no seguinte formato:

### **Visão Geral e Logística**
- **Ordem das Cidades:** [Cidade A] -> [Cidade B] -> [Cidade C]
- **Sugestão de Transporte:** [Ex.: Trem de alta velocidade, aluguel de carro, voo doméstico]

## **Roteiro Detalhado**
### **Dia 1: [Resumo do dia]**
- **Foco:** [Objetivo do dia]
- **[Atividade 1]** — Dica: "..."
- **[Atividade 2]** — Dica: "..."
- **Sugestão Gastronômica:** [Tipo de culinária/prato típico]
- **Sugestão Noturna:** [Atividade cultural ou de lazer]

*(Repita para todos os dias)*

### **Dicas Essenciais**
- **Dinheiro e Pagamentos:** [...]
- [Outras dicas relevantes]
"""

PROMPT_REVISOR = """
Você é um "Auditor de Experiências de Viagem", especialista em analisar roteiros para maximizar qualidade, viabilidade e ritmo, eliminando estresse e otimizando a logística com base em dados reais.

Sua tarefa é revisar e reconstruir o roteiro abaixo para gerar uma versão final validada, detalhada e otimizada.

**Roteiro para Auditoria:** {plano_de_roteiro}

Processo:

1. **Validação Logística:** Pesquise tempos reais de deslocamento entre atrações e cidades, considerando transporte disponível. Verifique também tempo médio necessário para visitar cada local.
2. **Reconstrução Otimizada:** Reorganize atividades para evitar deslocamentos excessivos e manter um fluxo natural e agradável.
3. **Refinamento de Conteúdo:** Acrescente dicas práticas, sugestões gastronômicas e experiências complementares.

Apresente o resultado **sem título geral de roteiro** e em Markdown, seguindo o formato:

## **Dia 1: [Resumo do dia]**
- **Foco:** [Objetivo do dia]
- **[Atividade 1]** — Dica: "..."
- **[Atividade 2]** — Dica: "..."
- **Sugestão Gastronômica:** [Tipo de culinária/prato típico]
- **Sugestão Noturna:** [Atividade cultural ou de lazer]

*(Repita para todos os dias)*

### **Dicas Essenciais**
- **Dinheiro e Pagamentos:** [...]
- [Outras dicas relevantes]
"""

PROMPT_EMOJIS = """
Você é um especialista em semântica visual e cultura global.
Sua missão é selecionar de 2 a 3 emojis que representem de forma clara e culturalmente relevante o país: {pais}.
A escolha deve considerar:
- Símbolos nacionais, fauna, flora ou elementos culturais marcantes.
- Emojis amplamente reconhecíveis e que façam sentido para um público internacional.
- Evitar combinações ambíguas ou que possam gerar interpretações erradas.
- Evitar usar bandeiras, usar emojis disponíveis para windows.

Retorne apenas os emojis, separados por espaço, sem explicações adicionais.
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
        
        prompt_emojis = PROMPT_EMOJIS.format(pais=pais)
        emojis_pesquisa = await model.generate_content_async(prompt_emojis)
        emojis_gerados = emojis_pesquisa.text.strip()
        status.update(label="Fase 3: Concluída!", state="complete")

    return roteiro_revisado, emojis_gerados

###################

db = conectar_firebase()
colecao = 'usuarios2'
##############

st.title("📝 Crie Seus Roteiros")
st.header("Preencha os campos abaixo para que nossa IA monte a viagem dos seus sonhos.")

with st.form("form_roteiro"):
    pais = st.text_input("Qual o país que você quer visitar?")
    data_inicio_str = st.date_input("Data de início da viagem", format="DD/MM/YYYY")
    data_fim_str = st.date_input("Data de fim da viagem", format="DD/MM/YYYY")
    submitted = st.form_submit_button("Gerar Roteiro ✨")
    if submitted:
        if not pais or not data_inicio_str or not data_fim_str:
            st.error("Por favor, preencha todos os campos.")
        elif data_inicio_str >= data_fim_str:
            st.error("A data de fim deve ser posterior à data de início.")
        else:
            dias = (data_fim_str - data_inicio_str).days
            st.info(f"Preparando um roteiro de {dias} dias para {pais}. Isso pode levar um momento...")
            roteiro_final, emojis_gerados = asyncio.run(gerar_roteiro_completo(pais, dias))
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
            'pais': pais,
            'emojis': emojis_gerados
            })
            user_ref.set(dados)
            st.success("Roteiro salvo!")