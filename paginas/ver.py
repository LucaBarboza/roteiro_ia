# import streamlit as st
# import firebase_admin
# from firebase_admin import credentials, firestore
# from datetime import datetime

# st.title("Seus Roteiros")

# @st.cache_resource
# def conectar_firebase():
#     try:
#         firebase_admin.get_app()
#     except ValueError:
#         cred = credentials.Certificate(dict(st.secrets["firebase"]))
#         firebase_admin.initialize_app(cred)
#     return firestore.client()

# db = conectar_firebase()
# colecao = 'usuarios2'

# doc = db.collection(colecao).document(st.user.email).get()
# dados = doc.to_dict() if doc.exists else {}
# roteiros = dados.get('roteiros', [])
    
# if 'roteiro_aberto' not in st.session_state:
#     st.session_state.roteiro_aberto = None

# if roteiros:
#     for i, roteiro in enumerate(roteiros):
#         with st.container(border=True):
#             pais = roteiro.get('pais', 'País Desconhecido')
#             emojis = roteiro.get('emojis', '')
#             st.subheader(f"{pais} {emojis}", )
#             is_open = (st.session_state.roteiro_aberto == roteiro['pais'])
#             button_label = "Fechar" if is_open else "Ver Roteiro"
#             if st.button(button_label, key=f"toggle_{roteiro['pais']}", use_container_width=True):
#                 if is_open:
#                     st.session_state.roteiro_aberto = None
#                 else:
#                     st.session_state.roteiro_aberto = roteiro['pais']
#                 st.rerun()
#             if is_open:
#                 st.header(f"📍  {pais} {emojis}")
#                 st.markdown(roteiro['texto'])
#                 st.divider()
#             col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
#             with col4:
#                 if st.button("🗑️ Deletar", key=f"delete_{i}", help="Deletar este roteiro"):
#                     doc_ref = db.collection(colecao).document(st.user.email) 
#                     doc_ref.update({
#                         'roteiros': firestore.ArrayRemove([roteiro])
#                     })
#                     st.success(f"Roteiro para {pais} deletado!")
#                     if st.session_state.roteiro_aberto == roteiro['pais']:
#                         st.session_state.roteiro_aberto = None
#                     st.rerun()
                
# else:
#     st.info("Nenhum roteiro ainda")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from fpdf import FPDF
import os

st.title("Seus Roteiros")

# --- NOVO: Função avançada para gerar PDF estilizado ---
def create_styled_pdf(markdown_text, title, font_path='arquivos/DejaVuSans.ttf'):
    """
    Cria um arquivo PDF com estilo a partir de um texto Markdown,
    replicando o formato da imagem fornecida.

    Args:
        markdown_text (str): O conteúdo do roteiro em formato Markdown.
        title (str): O título principal do documento.
        font_path (str): O caminho para o arquivo de fonte .ttf.

    Returns:
        bytes: O conteúdo do PDF gerado como bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Verifica se o arquivo de fonte existe antes de adicioná-lo
    if not os.path.exists(font_path):
        st.error(f"Arquivo de fonte não encontrado em: {font_path}. Faça o download e adicione ao projeto.")
        return None

    # Adiciona a fonte Unicode (essencial para emojis e caracteres especiais)
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.add_font('DejaVu', 'B', font_path, uni=True)  # Estilo Negrito

    # --- Título Principal ---
    pdf.set_font('DejaVu', 'B', 20)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)

    # --- Processa o Roteiro Linha por Linha ---
    for line in markdown_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('## '):
            # Título do Dia (ex: ## Dia 1: ...) -> Fonte Grande e Negrito
            pdf.set_font('DejaVu', 'B', 16)
            pdf.multi_cell(0, 8, line[3:])
            pdf.ln(4)
        elif line.startswith('### '):
            # Subtítulo (ex: ### Visão Geral) -> Fonte Média e Negrito
            pdf.set_font('DejaVu', 'B', 14)
            pdf.multi_cell(0, 7, line[4:])
            pdf.ln(3)
        elif line.startswith('* ') or line.startswith('- '):
            # Item de lista (ex: * Atividade...)
            text = line[2:]
            
            # Adiciona o símbolo de bullet manualmente
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(5, 8, "•")

            # Verifica se há uma parte em negrito (ex: **Foco:** texto)
            if '**' in text and ':' in text:
                parts = text.split(':', 1)
                bold_part = parts[0].replace('**', '').strip() + ':'
                regular_part = parts[1].strip()
                
                # Escreve a parte em negrito
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(pdf.get_string_width(bold_part) + 1, 8, bold_part)
                
                # Escreve o resto da linha com fonte normal
                pdf.set_font('DejaVu', '', 12)
                pdf.multi_cell(0, 8, regular_part)
            else:
                # Caso não tenha negrito, escreve a linha inteira normal
                pdf.set_font('DejaVu', '', 12)
                pdf.multi_cell(0, 8, text)
            pdf.ln(2)
        else:
            # Parágrafo de texto normal
            pdf.set_font('DejaVu', '', 12)
            pdf.multi_cell(0, 8, line)
            pdf.ln(2)

    return pdf.output()


# --- Conexão com Firebase (código original sem alterações) ---
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

doc = db.collection(colecao).document(st.user.email).get()
dados = doc.to_dict() if doc.exists else {}
roteiros = dados.get('roteiros', [])
    
if 'roteiro_aberto' not in st.session_state:
    st.session_state.roteiro_aberto = None

if roteiros:
    for i, roteiro in enumerate(roteiros):
        with st.container(border=True):
            pais = roteiro.get('pais', 'País Desconhecido')
            emojis = roteiro.get('emojis', '')
            st.subheader(f"{pais} {emojis}")
            
            is_open = (st.session_state.roteiro_aberto == roteiro['pais'])
            button_label = "Fechar" if is_open else "Ver Roteiro"
            
            if st.button(button_label, key=f"toggle_{roteiro['pais']}", use_container_width=True):
                if is_open:
                    st.session_state.roteiro_aberto = None
                else:
                    st.session_state.roteiro_aberto = roteiro['pais']
                st.rerun()
                
            if is_open:
                st.header(f"📍  {pais} {emojis}")
                st.markdown(roteiro['texto'])
                st.divider()

                # --- Lógica e Botão de Download (usando a nova função) ---
                pdf_title = f"{pais} {emojis}"
                pdf_bytes = create_styled_pdf(roteiro['texto'], pdf_title)
                
                if pdf_bytes:
                    st.download_button(
                        label="Baixar Roteiro em PDF 📄",
                        data=pdf_bytes,
                        file_name=f"roteiro_{pais.replace(' ', '_').lower()}.pdf",
                        mime="application/pdf"
                    )

            col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
            with col4:
                if st.button("🗑️ Deletar", key=f"delete_{i}", help="Deletar este roteiro"):
                    doc_ref = db.collection(colecao).document(st.user.email) 
                    doc_ref.update({
                        'roteiros': firestore.ArrayRemove([roteiro])
                    })
                    st.success(f"Roteiro para {pais} deletado!")
                    if st.session_state.roteiro_aberto == roteiro['pais']:
                        st.session_state.roteiro_aberto = None
                    st.rerun()
                
else:
    st.info("Nenhum roteiro ainda")