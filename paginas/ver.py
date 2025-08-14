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

# Caminhos absolutos para as fontes
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FONT_PATH_REGULAR = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans.ttf')
FONT_PATH_BOLD = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans-Bold.ttf')

st.title("Seus Roteiros")

def deletar_roteiro(roteiro_para_deletar):
    """Função para deletar um roteiro do Firestore."""
    try:
        doc_ref = db.collection(colecao).document(st.user.email)
        doc_ref.update({'roteiros': firestore.ArrayRemove([roteiro_para_deletar])})

        # Se o roteiro deletado era o que estava aberto, fecha ele
        if st.session_state.get('roteiro_aberto') == roteiro_para_deletar.get('pais'):
            st.session_state.roteiro_aberto = None
        
        st.success(f"Roteiro para {roteiro_para_deletar.get('pais')} deletado!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao deletar o roteiro: {e}")

def write_styled_text(pdf, text):
    """
    Processa e escreve texto com múltiplos estilos (negrito e itálico).
    """
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
    for part in parts:
        if not part: continue
        if part.startswith('**') and part.endswith('**'):
            pdf.set_font('DejaVu', 'B', 11)
            pdf.write(7, part[2:-2])
        else:
            pdf.set_font('DejaVu', '', 11)
            pdf.write(7, part)

def create_final_pdf(markdown_text, title):
    pdf = FPDF()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.add_font('DejaVu', '', FONT_PATH_REGULAR, uni=True)
    pdf.add_font('DejaVu', 'B', FONT_PATH_BOLD, uni=True)

    pdf.set_font('DejaVu', 'B', 22)
    title_width = pdf.get_string_width(title)
    doc_width = pdf.w - pdf.l_margin - pdf.r_margin
    x_start = pdf.l_margin + (doc_width - title_width) / 2
    if x_start < pdf.l_margin:
        x_start = pdf.l_margin
    pdf.set_x(x_start)
    pdf.write(12, title)
    
    # --- AJUSTE APLICADO AQUI ---
    # Diminuímos o espaçamento após o título de 20 para 15
    pdf.ln(15)

    is_first_day = True
    for line in markdown_text.split('\n'):
        line = line.strip()
        if not line: continue

        if 'Dicas Essenciais' in line:
            pdf.add_page()
            pdf.ln(8)
            pdf.set_font('DejaVu', 'B', 16)
            pdf.set_fill_color(230, 230, 230)
            # Limpa qualquer marcador de markdown para o título
            title_text = line.replace('**', '').replace('###', '').replace('##', '').strip()
            pdf.multi_cell(0, 12, f" {title_text} ", ln=True, fill=True, align='C')
            pdf.ln(6)
            
        elif line.startswith('## '):
            if not is_first_day:
                pdf.add_page()
            is_first_day = False
            
            pdf.ln(8)
            pdf.set_font('DejaVu', 'B', 16)
            pdf.set_fill_color(230, 230, 230)
            title_text = line[3:].replace('**', '')
            pdf.multi_cell(0, 12, f" {title_text} ", ln=True, fill=True, align='C')
            pdf.ln(6)

        elif line.startswith('### '):
            pdf.set_font('DejaVu', 'B', 13)
            pdf.multi_cell(0, 7, line[4:], ln=True, align='C')
            pdf.ln(4)

        elif line.startswith('* ') or line.startswith('- '):
            text = line[2:]
            pdf.cell(5)
            pdf.set_font('DejaVu', 'B', 11)
            pdf.cell(5, 7, "• ")
            write_styled_text(pdf, text)
            pdf.ln()
            pdf.ln(4)
        else: 
            pdf.set_font('DejaVu', '', 11)
            pdf.multi_cell(0, 7, line, ln=True)
            pdf.ln(4)

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

if 'roteiro_aberto' not in st.session_state:
    st.session_state.roteiro_aberto = None

if roteiros:
    for i, roteiro in enumerate(roteiros):
        with st.container(border=True):
            pais = roteiro.get('pais', 'País Desconhecido')
            emojis = roteiro.get('emojis', '')
            is_open = (st.session_state.roteiro_aberto == pais)

            # Cabeçalho (sempre visível)
            st.subheader(f"{pais} {emojis}")

            # --- ESTADO FECHADO ---
            # Se o roteiro NÃO estiver aberto, mostre os botões lado a lado
            if not is_open:
                col_ver, col_del = st.columns([3, 1]) # Dê mais espaço para o botão "Ver"
                
                with col_ver:
                    if st.button("Ver Roteiro Completo", key=f"open_{i}", use_container_width=True):
                        st.session_state.roteiro_aberto = pais
                        st.rerun()
                
                with col_del:
                    # Botão Deletar para o estado FECHADO
                    if st.button("🗑️", key=f"delete_closed_{i}", help="Deletar este roteiro"):
                        deletar_roteiro(roteiro) # Chama a função auxiliar

            # --- ESTADO ABERTO ---
            # Se o roteiro ESTIVER aberto, mostre o conteúdo completo
            else:
                # Botão para fechar (ocupa a largura toda)
                if st.button("Fechar Roteiro", key=f"close_{i}", use_container_width=True):
                    st.session_state.roteiro_aberto = None
                    st.rerun()

                # Conteúdo do roteiro
                st.header(f"📍 Roteiro Completo para {pais} {emojis}")
                st.markdown(roteiro['texto'])
                st.divider()

                # Botões de ação na parte de baixo
                col_download, col_del_open = st.columns([3, 1])

                with col_download:
                    pdf_bytes = create_final_pdf(roteiro['texto'], pais)
                    if pdf_bytes:
                        st.download_button(
                            label="Baixar Roteiro em PDF 📄",
                            data=pdf_bytes,
                            file_name=f"roteiro_{pais.replace(' ', '_').lower()}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                
                with col_del_open:
                    # Botão Deletar para o estado ABERTO (aparece embaixo)
                    if st.button("🗑️ Deletar", key=f"delete_open_{i}", help="Deletar este roteiro"):
                        deletar_roteiro(roteiro) # Chama a mesma função auxiliar
else:
    st.info("Você ainda não criou nenhum roteiro de viagem.")