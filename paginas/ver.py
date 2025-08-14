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
import re

# Caminhos absolutos e seguros para AMBAS as fontes
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FONT_PATH_REGULAR = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans.ttf')
FONT_PATH_BOLD = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans-Bold.ttf')

st.title("Seus Roteiros")

def write_styled_text(pdf, text):
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if not part: continue
        if part.startswith('**') and part.endswith('**'):
            pdf.set_font('DejaVu', 'B', 11) # Pede o estilo Negrito
            pdf.write(8, part[2:-2])
        else:
            pdf.set_font('DejaVu', '', 11) # Pede o estilo Regular
            pdf.write(8, part)

def create_final_pdf(markdown_text, title):
    # Verificação de segurança para AMBOS os arquivos de fonte
    if not os.path.exists(FONT_PATH_REGULAR):
        st.error(f"ERRO: Fonte Regular não encontrada em: {FONT_PATH_REGULAR}")
        return None
    if not os.path.exists(FONT_PATH_BOLD):
        st.error(f"ERRO: Fonte Negrito não encontrada em: {FONT_PATH_BOLD}")
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- REGISTRO CORRETO DAS FONTES ---
    # Registra a fonte regular para o estilo '' (normal)
    pdf.add_font('DejaVu', '', FONT_PATH_REGULAR, uni=True)
    # Registra a fonte bold para o estilo 'B' (negrito)
    pdf.add_font('DejaVu', 'B', FONT_PATH_BOLD, uni=True)

    # --- Título Principal ---
    pdf.set_font('DejaVu', 'B', 22) # Pede o estilo Negrito
    pdf.multi_cell(0, 12, title, align='C', ln=True)

    is_first_day = True

    # --- Processa o Roteiro ---
    for line in markdown_text.split('\n'):
        line = line.strip()
        if not line: continue

        if line.startswith('## '):
            if not is_first_day:
                pdf.add_page()
            is_first_day = False
            
            pdf.ln(5)
            pdf.set_font('DejaVu', 'B', 16) # Pede o estilo Negrito
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(0, 12, f" {line[3:]}", ln=True, fill=True)
            pdf.ln(5)

        elif line.startswith('### '):
            pdf.set_font('DejaVu', 'B', 13) # Pede o estilo Negrito
            pdf.multi_cell(0, 7, line[4:], ln=True)
            pdf.ln(4)

        elif line.startswith('* ') or line.startswith('- '):
            text = line[2:]
            
            pdf.cell(5)
            pdf.set_font('DejaVu', 'B', 11) # Pede o estilo Negrito
            pdf.cell(5, 8, "• ")

            write_styled_text(pdf, text)
            pdf.ln()
            pdf.ln(3)

        else: 
            pdf.set_font('DejaVu', '', 11) # Pede o estilo Regular
            pdf.multi_cell(0, 7, line, ln=True)
            pdf.ln(3)

    return bytes(pdf.output())


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
                st.session_state.roteiro_aberto = None if is_open else roteiro['pais']
                st.rerun()
                
            if is_open:
                st.header(f"📍  {pais} {emojis}")
                st.markdown(roteiro['texto'])
                st.divider()

                pdf_title = f"{pais} {emojis}"
                pdf_bytes = create_final_pdf(roteiro['texto'], pdf_title)
                
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
                    doc_ref.update({'roteiros': firestore.ArrayRemove([roteiro])})
                    st.success(f"Roteiro para {pais} deletado!")
                    if st.session_state.roteiro_aberto == roteiro['pais']:
                        st.session_state.roteiro_aberto = None
                    st.rerun()
else:
    st.info("Nenhum roteiro ainda")