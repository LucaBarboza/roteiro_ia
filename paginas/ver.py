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

st.title("Seus Roteiros")

# --- CONFIGURAÇÃO DAS FONTES (MANTENHA COMO ESTAVA) ---
# Substitua por seu caminho real se for diferente
FONT_DIR = 'arquivos'
FONT_PATH_REGULAR = f'{FONT_DIR}/NotoSans-Regular.ttf'
FONT_PATH_BOLD = f'{FONT_DIR}/NotoSans-Bold.ttf'
FONT_PATH_EMOJI = f'{FONT_DIR}/NotoColorEmoji-Regular.ttf'

# --- FUNÇÃO MÁGICA: RENDERIZA TEXTO COM EMOJI PARA UMA IMAGEM ---
def render_text_to_image(text, font_path, font_size, text_color=(0, 0, 0)):
    """Desenha um texto (com emojis) em uma imagem PNG com fundo transparente."""
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        st.error(f"Fonte não encontrada em: {font_path}")
        return None

    # Calcula o tamanho que a imagem precisa ter
    bbox = font.getbbox(text)
    image_width = bbox[2]
    image_height = bbox[3]

    if image_width == 0 or image_height == 0:
        return None # Retorna nada para texto vazio

    # Cria a imagem com canal Alpha (transparência)
    img = Image.new('RGBA', (image_width, image_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Desenha o texto na imagem
    draw.text((0, 0), text, font=font, fill=text_color)

    # Salva a imagem em um buffer de memória
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

# --- FUNÇÃO PRINCIPAL DO PDF (BASEADA NO SEU CÓDIGO ORIGINAL) ---
def create_final_pdf(markdown_text, title, emoji):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_margins(25, 25, 25)

    # Adiciona as fontes ao FPDF para texto SEM emoji
    pdf.add_font('NotoSans', '', FONT_PATH_REGULAR)
    pdf.add_font('NotoSans', 'B', FONT_PATH_BOLD)
    pdf.add_page()

    # --- TÍTULO PRINCIPAL (COM EMOJI) ---
    title_with_emoji = f"{title} {emoji}"
    # Define um tamanho de fonte grande para o título
    title_font_size_pt = 24
    # Converte de pt para px para a Pillow (aproximação)
    title_font_size_px = int(title_font_size_pt * 1.33)
    
    title_img_buffer = render_text_to_image(title_with_emoji, FONT_PATH_EMOJI, title_font_size_px, text_color=(0,0,0))
    if title_img_buffer:
        # A largura da imagem em mm para o FPDF
        # 1 pt = 0.352778 mm
        img_width_mm = (Image.open(title_img_buffer).width / 1.33) * 0.352778
        title_img_buffer.seek(0) # Reinicia o buffer após leitura
        
        # Centraliza a imagem
        x_pos = (pdf.w - img_width_mm) / 2
        pdf.image(title_img_buffer, x=x_pos, h=title_font_size_pt * 0.352778)
        pdf.ln(15)

    # --- CORPO DO ROTEIRO ---
    # Pré-processamento para unificar tudo em uma lista
    processed_lines = []
    for line in markdown_text.split('\n'):
        stripped_line = line.strip()
        if stripped_line.startswith('## '):
            processed_lines.append(stripped_line)
        elif stripped_line:
            if stripped_line.startswith('### '):
                stripped_line = stripped_line[4:]
            processed_lines.append(f'* {stripped_line}')
    
    is_first_day = True
    for line in processed_lines:
        if line.startswith('## '): # Título do Dia
            if not is_first_day:
                pdf.add_page()
            is_first_day = False
            
            pdf.set_font('NotoSans', 'B', 16)
            pdf.multi_cell(0, 10, line[3:], align='C', ln=True)
            pdf.ln(5)

        elif line.startswith('* '): # Item da lista
            text = line[2:]
            
            # Divide o texto em partes com negrito e sem negrito
            parts = re.split(r'(\*\*.*?\*\*)', text)
            
            pdf.set_x(30) # Recuo do bullet
            pdf.set_font('NotoSans', 'B', 12)
            pdf.cell(5, 8, "•")
            
            # Escreve cada parte com seu estilo
            for part in parts:
                if not part: continue
                
                font_path = FONT_PATH_REGULAR
                font_style = ''
                if part.startswith('**') and part.endswith('**'):
                    part = part[2:-2]
                    font_path = FONT_PATH_BOLD
                    font_style = 'B'

                # Renderiza como imagem para suportar emojis
                line_img_buffer = render_text_to_image(part, font_path, 16, text_color=(0,0,0))
                if line_img_buffer:
                    img = Image.open(line_img_buffer)
                    img_width_mm = (img.width / 1.33) * 0.352778
                    img_height_mm = 8 # Altura fixa da linha
                    line_img_buffer.seek(0)
                    
                    # Verifica se precisa quebrar a linha
                    if pdf.get_x() + img_width_mm > (pdf.w - pdf.r_margin):
                        pdf.ln(img_height_mm)
                        pdf.set_x(35) # Recuo após quebra de linha

                    pdf.image(line_img_buffer, y=pdf.get_y(), h=img_height_mm)
                    # Move o cursor para o lado da imagem
                    pdf.set_x(pdf.get_x() + img_width_mm)

            pdf.ln(8)

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