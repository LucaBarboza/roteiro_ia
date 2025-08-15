# import streamlit as st
# import firebase_admin
# from firebase_admin import credentials, firestore
# from fpdf import FPDF
# import os
# import re

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# FONT_PATH_REGULAR = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans.ttf')
# FONT_PATH_BOLD = os.path.join(PROJECT_ROOT, 'arquivos', 'DejaVuSans-Bold.ttf')

# st.title("Seus Roteiros")

# def deletar_roteiro(roteiro_para_deletar):
#     """Função para deletar um roteiro do Firestore."""
#     try:
#         doc_ref = db.collection(colecao).document(st.user.email)
#         doc_ref.update({'roteiros': firestore.ArrayRemove([roteiro_para_deletar])})

#         # Se o roteiro deletado era o que estava aberto, fecha ele
#         if st.session_state.get('roteiro_aberto') == roteiro_para_deletar.get('pais'):
#             st.session_state.roteiro_aberto = None
        
#         st.success(f"Roteiro para {roteiro_para_deletar.get('pais')} deletado!")
#         st.rerun()
#     except Exception as e:
#         st.error(f"Erro ao deletar o roteiro: {e}")

# def write_styled_text(pdf, text):
#     """
#     Processa e escreve texto com múltiplos estilos (negrito e itálico).
#     """
#     parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
#     for part in parts:
#         if not part: continue
#         if part.startswith('**') and part.endswith('**'):
#             pdf.set_font('DejaVu', 'B', 11)
#             pdf.write(7, part[2:-2])
#         else:
#             pdf.set_font('DejaVu', '', 11)
#             pdf.write(7, part)

# def create_final_pdf(markdown_text, title):
#     pdf = FPDF()
#     pdf.set_left_margin(20)
#     pdf.set_right_margin(20)
#     pdf.add_page()
#     pdf.set_auto_page_break(auto=True, margin=20)

#     pdf.add_font('DejaVu', '', FONT_PATH_REGULAR, uni=True)
#     pdf.add_font('DejaVu', 'B', FONT_PATH_BOLD, uni=True)

#     pdf.set_font('DejaVu', 'B', 22)
#     title_width = pdf.get_string_width(title)
#     doc_width = pdf.w - pdf.l_margin - pdf.r_margin
#     x_start = pdf.l_margin + (doc_width - title_width) / 2
#     if x_start < pdf.l_margin:
#         x_start = pdf.l_margin
#     pdf.set_x(x_start)
#     pdf.write(12, title)
    
#     pdf.ln(15)

#     is_first_day = True
#     for line in markdown_text.split('\n'):
#         line = line.strip()
#         if not line: continue

#         if 'Dicas Essenciais' in line:
#             pdf.add_page()
#             pdf.ln(8)
#             pdf.set_font('DejaVu', 'B', 16)
#             pdf.set_fill_color(230, 230, 230)
#             # Limpa qualquer marcador de markdown para o título
#             title_text = line.replace('**', '').replace('###', '').replace('##', '').strip()
#             pdf.multi_cell(0, 12, f" {title_text} ", ln=True, fill=True, align='C')
#             pdf.ln(6)
            
#         elif line.startswith('## '):
#             if not is_first_day:
#                 pdf.add_page()
#             is_first_day = False
            
#             pdf.ln(8)
#             pdf.set_font('DejaVu', 'B', 16)
#             pdf.set_fill_color(230, 230, 230)
#             title_text = line[3:].replace('**', '')
#             pdf.multi_cell(0, 12, f" {title_text} ", ln=True, fill=True, align='C')
#             pdf.ln(6)

#         elif line.startswith('### '):
#             pdf.set_font('DejaVu', 'B', 13)
#             pdf.multi_cell(0, 7, line[4:], ln=True, align='C')
#             pdf.ln(4)

#         elif line.startswith('* ') or line.startswith('- '):
#             text = line[2:]
#             pdf.cell(5)
#             pdf.set_font('DejaVu', 'B', 11)
#             pdf.cell(5, 7, "• ")
#             write_styled_text(pdf, text)
#             pdf.ln()
#             pdf.ln(4)
#         else: 
#             pdf.set_font('DejaVu', '', 11)
#             pdf.multi_cell(0, 7, line, ln=True)
#             pdf.ln(4)

#     return bytes(pdf.output())

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

# if 'roteiro_aberto' not in st.session_state:
#     st.session_state.roteiro_aberto = None

# if roteiros:
#     for i, roteiro in enumerate(roteiros):
#         with st.container(border=True):
#             pais = roteiro.get('pais', 'País Desconhecido')
#             emojis = roteiro.get('emojis', '')
#             is_open = (st.session_state.roteiro_aberto == pais)

#             st.subheader(f"{pais} {emojis}")

#             if not is_open:
#                 col_ver, col_del = st.columns([3, 0.8])
                
#                 if st.button("Ver Roteiro Completo", key=f"open_{i}", use_container_width=True):
#                     st.session_state.roteiro_aberto = pais
#                     st.rerun()
                
#                 if st.button("🗑️ Deletar", key=f"delete_closed_{i}", help="Deletar este roteiro"):
#                     deletar_roteiro(roteiro)

#             else:
#                 if st.button("Fechar Roteiro", key=f"close_{i}", use_container_width=True):
#                     st.session_state.roteiro_aberto = None
#                     st.rerun()

#                 st.header(f"📍 Roteiro Completo para {pais} {emojis}")
#                 st.markdown(roteiro['texto'])
#                 st.divider()

#                 col_download, col2, col3, col_del_open = st.columns([2, 1, 1, 0.8])

#                 with col_download:
#                     pdf_bytes = create_final_pdf(roteiro['texto'], pais)
#                     if pdf_bytes:
#                         st.download_button(
#                             label="Baixar Roteiro em PDF 📄",
#                             data=pdf_bytes,
#                             file_name=f"roteiro_{pais.replace(' ', '_').lower()}.pdf",
#                             mime="application/pdf",
#                             use_container_width=True
#                         )
                
#                 with col_del_open:
#                     if st.button("🗑️ Deletar", key=f"delete_open_{i}", help="Deletar este roteiro"):
#                         deletar_roteiro(roteiro)
# else:
#     st.info("Você ainda não criou nenhum roteiro de viagem.")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import re
import os

# --- CONFIGURAÇÃO DE ARQUIVOS E FONTES ---
# Usando as fontes Noto para melhor compatibilidade
FONT_DIR = 'arquivos'
FONT_PATH_REGULAR = os.path.join(FONT_DIR, 'NotoSans-Regular.ttf')
FONT_PATH_BOLD = os.path.join(FONT_DIR, 'NotoSans-Bold.ttf')
FONT_PATH_EMOJI = os.path.join(FONT_DIR, 'NotoColorEmoji-Regular.ttf')

st.title("Seus Roteiros")

# --- FUNÇÕES AUXILIARES PARA O PDF ---

def contains_emoji(text):
    """Verifica se um texto contém caracteres emoji."""
    # Regex simples para pegar a maioria dos emojis comuns
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.search(text)

def render_text_as_image(text, font_path, font_size_px, is_bold=False):
    """Renderiza uma linha de texto em uma imagem PNG com fundo transparente."""
    font_to_use = FONT_PATH_BOLD if is_bold else font_path
    try:
        # Usamos a fonte de Emoji como base e a Pillow se encarrega de usar as outras se precisar
        font = ImageFont.truetype(FONT_PATH_EMOJI, font_size_px)
        text_font = ImageFont.truetype(font_to_use, font_size_px)
    except IOError as e:
        st.error(f"Erro ao carregar fonte: {e}")
        return None

    # Calcula o tamanho da imagem
    bbox = text_font.getbbox(text)
    image_width, image_height = bbox[2], bbox[3]
    if image_width == 0 or image_height == 0: return None

    img = Image.new('RGBA', (image_width, image_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=text_font, fill=(0, 0, 0))

    buffer = BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    return buffer, image_width

def write_line(pdf, text, font_size_pt, is_bold=False, is_multicell=False, align='L'):
    """Escreve uma linha no PDF, usando imagem se tiver emoji, ou texto normal caso contrário."""
    if contains_emoji(text):
        font_size_px = int(font_size_pt * 1.33) # Conversão aproximada pt -> px
        img_buffer, img_width_px = render_text_as_image(text, FONT_PATH_REGULAR, font_size_px, is_bold)
        
        if img_buffer:
            img_width_mm = (img_width_px / 1.33) * 0.352778
            img_height_mm = font_size_pt * 0.352778

            # Centraliza se necessário
            x_pos = pdf.get_x()
            if align == 'C':
                x_pos = (pdf.w - pdf.l_margin - pdf.r_margin - img_width_mm) / 2 + pdf.l_margin

            pdf.image(img_buffer, x=x_pos, h=img_height_mm)
            pdf.ln(img_height_mm + (2 if is_multicell else 0))
    else:
        font_style = 'B' if is_bold else ''
        pdf.set_font('NotoSans', font_style, font_size_pt)
        if is_multicell:
            pdf.multi_cell(0, font_size_pt * 0.5, text, align=align, ln=True)
        else:
            pdf.write(font_size_pt * 0.5, text)

# --- FUNÇÃO PRINCIPAL DE CRIAÇÃO DO PDF (BASEADA NO SEU CÓDIGO) ---
def create_final_pdf(markdown_text, title, emoji):
    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.add_font('NotoSans', '', FONT_PATH_REGULAR)
    pdf.add_font('NotoSans', 'B', FONT_PATH_BOLD)
    pdf.add_page()

    # Título principal (com emoji)
    write_line(pdf, f"{title} {emoji}", 22, is_bold=True, is_multicell=True, align='C')
    pdf.ln(10)

    is_first_day = True
    for line in markdown_text.split('\n'):
        line = line.strip()
        if not line: continue

        if 'Dicas Essenciais' in line or line.startswith('## '):
            if not is_first_day or 'Dicas Essenciais' in line:
                pdf.add_page()
            is_first_day = False
            
            title_text = line.replace('**', '').replace('###', '').replace('##', '').strip()
            pdf.set_font('NotoSans', 'B', 16)
            pdf.set_fill_color(230, 230, 230)
            pdf.multi_cell(0, 12, f" {title_text} ", ln=True, fill=True, align='C')
            pdf.ln(6)
        
        elif line.startswith('### '):
            pdf.set_font('NotoSans', 'B', 13)
            pdf.multi_cell(0, 7, line[4:], ln=True, align='C')
            pdf.ln(4)

        elif line.startswith('* ') or line.startswith('- '):
            text = line[2:]
            pdf.set_x(25) # Recuo
            pdf.set_font('NotoSans', 'B', 11)
            pdf.cell(5, 7, "• ")
            
            # Divide em partes negrito/normal
            parts = re.split(r'(\*\*.*?\*\*)', text)
            for part in parts:
                if not part: continue
                is_bold_part = part.startswith('**') and part.endswith('**')
                clean_part = part[2:-2] if is_bold_part else part
                write_line(pdf, clean_part, 11, is_bold=is_bold_part)
            pdf.ln(8)

        else: 
            pdf.set_font('NotoSans', '', 11)
            pdf.multi_cell(0, 7, line, ln=True)
            pdf.ln(4)

    return pdf.output()

# --- FUNÇÕES DE CONEXÃO E LÓGICA DO APP ---

@st.cache_resource
def conectar_firebase():
    """Conecta-se ao Firebase, inicializando o app se necessário."""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

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

# --- LÓGICA PRINCIPAL DA INTERFACE ---

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
            is_open = (st.session_state.roteiro_aberto == pais)

            st.subheader(f"{pais} {emojis}")

            # Se o roteiro estiver fechado
            if not is_open:
                if st.button("Ver Roteiro Completo", key=f"open_{i}", use_container_width=True):
                    st.session_state.roteiro_aberto = pais
                    st.rerun()
            
            # Se o roteiro estiver aberto
            else:
                if st.button("Fechar Roteiro", key=f"close_{i}", use_container_width=True):
                    st.session_state.roteiro_aberto = None
                    st.rerun()

                st.header(f"📍 Roteiro Completo para {pais} {emojis}")
                st.markdown(roteiro['texto'])
                st.divider()

                col_download, col_delete = st.columns([3, 0.8])

                with col_download:
                    pdf_bytes = create_final_pdf(roteiro['texto'], pais, emojis)
                    if pdf_bytes:
                        st.download_button(
                            label="Baixar Roteiro em PDF 📄",
                            data=pdf_bytes,
                            file_name=f"roteiro_{pais.replace(' ', '_').lower()}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                
                with col_delete:
                    if st.button("🗑️ Deletar", key=f"delete_open_{i}", help="Deletar este roteiro"):
                        deletar_roteiro(roteiro)
else:
    st.info("Você ainda não criou nenhum roteiro de viagem.")