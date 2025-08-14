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
import io
from PIL import Image, ImageDraw, ImageFont
import regex # <- NOVA IMPORTAÇÃO

# Caminhos absolutos para as fontes
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FONT_PATH_REGULAR = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans.ttf')
FONT_PATH_BOLD = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans-Bold.ttf')
FONT_PATH_ITALIC = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans-Oblique.ttf')

st.title("Seus Roteiros")

def create_emoji_image(emoji_char, font_path, size=64):
    try:
        font = ImageFont.truetype(font_path, size)
        bbox = font.getbbox(emoji_char)
        image_size = (bbox[2], bbox[3])
        if image_size[0] == 0 or image_size[1] == 0: return None # Ignora caracteres sem dimensão
        
        image = Image.new("RGBA", image_size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), emoji_char, font=font, fill=(0, 0, 0, 255))
        
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
    except Exception as e:
        # Silencia o aviso para o usuário final, mas é bom para debug
        # st.warning(f"Não foi possível renderizar o emoji '{emoji_char}': {e}")
        return None

def write_styled_text(pdf, text):
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
    for part in parts:
        if not part: continue
        if part.startswith('**') and part.endswith('**'):
            pdf.set_font('DejaVu', 'B', 11)
            pdf.write(7, part[2:-2])
        elif part.startswith('*') and part.endswith('*'):
            pdf.set_font('DejaVu', 'I', 11)
            pdf.write(7, part[1:-1])
        else:
            pdf.set_font('DejaVu', '', 11)
            pdf.write(7, part)

def create_final_pdf(markdown_text, title_text, emojis_text):
    if not all(os.path.exists(p) for p in [FONT_PATH_REGULAR, FONT_PATH_BOLD, FONT_PATH_ITALIC]):
        st.error("ERRO: Faltando um ou mais arquivos de fonte (Regular, Bold, Italic).")
        return None

    pdf = FPDF()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.add_font('DejaVu', '', FONT_PATH_REGULAR, uni=True)
    pdf.add_font('DejaVu', 'B', FONT_PATH_BOLD, uni=True)
    pdf.add_font('DejaVu', 'I', FONT_PATH_ITALIC, uni=True)

    pdf.set_font('DejaVu', 'B', 22)
    
    text_width = pdf.get_string_width(title_text)
    emoji_width = len(regex.findall(r'\X', emojis_text)) * 10 
    total_width = text_width + emoji_width
    doc_width = pdf.w - pdf.l_margin - pdf.r_margin
    x_start = pdf.l_margin + (doc_width - total_width) / 2
    if x_start < pdf.l_margin: x_start = pdf.l_margin
    
    pdf.set_xy(x_start, pdf.get_y() + 5)
    pdf.write(12, title_text)

    current_x = pdf.get_x() + 2 
    current_y = pdf.get_y() 
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Usando regex.findall para separar os emojis corretamente
    for emoji in regex.findall(r'\X', emojis_text):
        if not emoji.strip(): continue # Ignora espaços em branco
        emoji_img = create_emoji_image(emoji, FONT_PATH_REGULAR)
        if emoji_img:
            pdf.image(emoji_img, x=current_x, y=current_y - 2, h=10)
            current_x += 10 
    pdf.ln(20)

    is_first_day = True
    for line in markdown_text.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('## '):
            if not is_first_day: pdf.add_page()
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

                pdf_bytes = create_final_pdf(roteiro['texto'], pais, emojis)
                
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