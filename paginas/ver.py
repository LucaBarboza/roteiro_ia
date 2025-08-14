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

# paginas/ver.py (Versão Final Corrigida)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from fpdf import FPDF
import os

# 1. Lógica para construir um caminho absoluto e seguro para a fonte
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FONT_PATH = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans.ttf')

st.title("Seus Roteiros")

def create_pdf_with_font(markdown_text, title):
    """
    Cria um PDF de alta qualidade usando a fonte DejaVu para suportar
    todos os caracteres especiais e emojis.
    """
    # Verificação de segurança para o arquivo da fonte
    if not os.path.exists(FONT_PATH):
        st.error(f"ERRO: Fonte DejaVu não encontrada no caminho: {FONT_PATH}")
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 2. Adicionando a fonte DejaVu Unicode
    pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
    pdf.add_font('DejaVu', 'B', FONT_PATH, uni=True)

    # --- Título Principal ---
    pdf.set_font('DejaVu', 'B', 20)
    # O texto agora é passado diretamente, sem sanitização
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)

    # --- Processa o Roteiro Linha por Linha ---
    for line in markdown_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('## '):
            pdf.set_font('DejaVu', 'B', 16)
            pdf.write(8, line[3:])
            pdf.ln(12)
        elif line.startswith('### '):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.write(8, line[4:])
            pdf.ln(10)
        elif line.startswith('* ') or line.startswith('- '):
            text = line[2:]
            
            # 3. Restaurando o bullet original "•"
            pdf.cell(5, 8, "•")

            if '**' in text and ':' in text:
                parts = text.split(':', 1)
                bold_part = parts[0].replace('**', '').strip() + ':'
                regular_part = parts[1].strip()
                
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(pdf.get_string_width(bold_part) + 1, 8, bold_part)
                
                pdf.set_font('DejaVu', '', 12)
                pdf.write(8, regular_part)
                pdf.ln(10)
            else:
                pdf.set_font('DejaVu', '', 12)
                pdf.write(8, text)
                pdf.ln(10)
        else:
            pdf.set_font('DejaVu', '', 12)
            pdf.write(8, line)
            pdf.ln(10)

    # 4. Mantendo a conversão para 'bytes' que resolveu o problema
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

                # 5. Voltando a usar os emojis no título do PDF
                pdf_title = f"{pais} {emojis}"
                pdf_bytes = create_pdf_with_font(roteiro['texto'], pdf_title)
                
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
