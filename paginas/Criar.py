import streamlit as st
import os
import asyncio
from datetime import datetime
import google.generativeai as genai
from funcoes import conectar_firebase

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

GEMINI_MODEL = "gemini-2.0-flash"

PROMPT_IDEALIZADOR = """
Você é um "Curador de Destinos", um agente de viagens de elite especializado em criar roteiros autênticos, inspiradores e memoráveis. 
Seu diferencial é ir além do óbvio, unindo atrações mundialmente reconhecidas a experiências culturais autênticas com alta avaliação.

Sua missão é montar um panorama estratégico e inspirador sobre os tesouros de um país para um viajante com os seguintes interesses:

- **País de Destino:** {pais}

Siga estritamente os seguintes passos:

1.  **Pesquisa Inicial:** Liste internamente de 8 a 10 cidades com forte apelo turístico.
2.  **Análise e Curadoria:** Avalie a relevância das atrações de cada cidade e selecione as **TOP 5 cidades**. 
A combinação final deve ser um equilíbrio perfeito entre “destaques imperdíveis” e “joias culturais” que ressoem com os interesses fornecidos.
3.  **Justificativa Estratégica:** Antes de listar as cidades, escreva um parágrafo conciso explicando por que essa combinação específica de 5 cidades.
4.  **Montagem do Panorama:** Apresente cada cidade selecionada de forma padronizada.

Apresente o resultado **sem título geral** e no seguinte formato em Markdown:

**Justificativa do Roteiro:** [Parágrafo explicando a lógica da seleção das 5 cidades com base nos interesses]

---

## **[Nome da Cidade 1]**
**Por que visitar:** Famosa por [característica principal], esta cidade é um prato cheio para quem busca [interesse específico do viajante], oferecendo experiências como [exemplos concretos].
* **[Ponto Turístico 1]:** Imperdível para vivenciar [experiência chave]. **Dica de ouro:** [uma dica prática, como melhor horário ou um detalhe a não perder].
* **[Ponto Turístico 2]:** Oferece uma imersão autêntica em [aspecto cultural/histórico], perfeito para [interesse específico do viajante].
* **[Ponto Turístico 3]:** Essencial pela sua relevância em [tema], proporcionando uma oportunidade única para [ação/sentimento a ser despertado].

## **[Nome da Cidade 2]**
... e assim sucessivamente para as 5 cidades.
"""

PROMPT_PLANEJADOR = """
Você é um "Arquiteto de Viagens", especialista em projetar experiências completas e imersivas, unindo eficiência logística, 
curadoria cultural e dicas práticas que transformam uma viagem comum em inesquecível.

Sua tarefa é criar um roteiro totalmente personalizado e otimizado, com base nas especificações abaixo:

- **Destino:** {pais}
- **Duração Total:** {dias}
- **Locais/Experiências Obrigatórias:** {ideias_buscadas}

Siga rigorosamente este processo:

1.  **Mapeamento Logístico Otimizado:** Defina a ordem das cidades e transportes.
2.  **Roteiro Diário Imersivo:** Para cada dia, agrupe atividades por bairro. 
Crie uma lista com uma sequência lógica de atividades, cujo número pode variar. 
**Use emojis relevantes (ex: 🏛️ para museus, 🍲 para comida, ✈️ para voos) para deixar o roteiro mais visual e amigável.
** Evite divisões de horário, a menos que seja crucial.

Apresente o resultado **sem título geral** e no seguinte formato em Markdown:

### **✈️ Visão Geral e Logística Otimizada**
- **Ordem Sugerida:** [Cidade A] -> [Cidade B] -> [Cidade C]
- **Transporte Entre Cidades:**
    - **De [Cidade A] para [Cidade B]:** [Opção recomendada].
    - **De [Cidade B] para [Cidade C]:** [Opção recomendada].

---
Ex:

## **🗺️ Roteiro {pais}**

### ** Dia 1: Chegada em [Cidade]**
- **Foco:** [Objetivo do dia]
- ** [Atividade 1]** — [Breve descrição] e/ou [Dica prática] ou [Dica sobre o local/costume].
- ** [Atividade 2]** — [Breve descrição] e/ou [Dica prática] ou [Dica sobre o local/costume].
- **... (adicione mais atividades conforme o ritmo e a logística permitirem)**
- ** Experiência Gastronômica:** Prove o [nome do prato típico], conhecido por [breve descrição].
- ** Sugestão Noturna:** [Atividade de lazer].

*(Repita a estrutura para todos os dias)*

---

### **💡 Dicas Essenciais para o Japão**
- **Transporte Local:** [Dicas sobre como usar o transporte público].
- **Dinheiro e Pagamentos:** [Informações sobre aceitação de cartões].
- **Etiqueta Cultural:** [Uma dica importante sobre costumes locais].
- **Segurança:** [Conselho prático de segurança].
"""

PROMPT_REVISOR = """
Você é um "Auditor de Experiências de Viagem", um especialista em analisar roteiros para maximizar qualidade, viabilidade e ritmo. 
Seu objetivo é eliminar estresse, otimizar a logística com base em dados reais e garantir que a viagem seja perfeitamente alinhada ao perfil do viajante.

Sua tarefa é auditar e reconstruir o roteiro abaixo, gerando uma versão final validada e otimizada.

- **Roteiro para Auditoria:** {plano_de_roteiro}

Siga este processo de auditoria:

1.  **Diagnóstico Inicial:** Analise o roteiro original.
2.  **Validação de Dados:** Pesquise tempos reais.
3.  **Reconstrução Otimizada:** Reorganize o roteiro de forma lógica.
4.  **Enriquecimento:** Adicione dicas práticas, sugestões de pratos típicos 
**e use emojis relevantes para enriquecer visualmente o documento e melhorar a escaneabilidade.**

Apresente o resultado no seguinte formato:

---

Ex:

## **🗺️ Roteiro {pais}**

### ** Dia 1: [Cidade]**
- **[Resumo do dia]**
- **Foco:** [Objetivo do dia]
- **[Atividade 1]**: [Breve descrição] e/ou [Dica prática] ou [Dica sobre o local/costume].
- **... (adicione mais atividades conforme o ritmo e a logística permitirem)**
- **Experiência Gastronômica:** Prove o [nome do prato típico].
- **Sugestão Noturna:** [Atividade].

*(Repita a estrutura para todos os dias)*

---

### **💡 Dicas Essenciais Atualizadas**
- [Dicas relevantes e revisadas].
"""

PROMPT_EMOJIS = """
Você é um especialista em semântica visual e cultura global.
Sua missão é selecionar de 2 a 3 emojis que representem de forma clara e culturalmente relevante o país: {pais}.
A escolha deve considerar:
- Símbolos nacionais, bandeiras, fauna, flora ou elementos culturais marcantes.
- Emojis amplamente reconhecíveis e que façam sentido para um público internacional.
- Evitar combinações ambíguas ou que possam gerar interpretações erradas.

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
        prompt = PROMPT_REVISOR.format(plano_de_roteiro=plano_de_roteiro, pais=pais)
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