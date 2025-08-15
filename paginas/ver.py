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
import markdown2
from io import BytesIO
# A importação da 'pisa' foi removida e a 'HTML' da WeasyPrint foi adicionada
from weasyprint import HTML

# Título da aplicação
st.title("Seus Roteiros de Viagem 🗺️")

# --- FUNÇÃO DE GERAÇÃO DE PDF ATUALIZADA PARA WEASYPRINT ---
def create_final_pdf(markdown_text, title, emoji):
    """
    Cria um PDF com emojis coloridos usando WeasyPrint e CSS aprimorado
    para um layout profissional.
    """
    html_body = markdown2.markdown(markdown_text, extras=["break-on-newline"])

    html_string = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            /* --- CSS APRIMORADO PARA UM LAYOUT PROFISSIONAL --- */

            body {{
                font-family: 'Noto Sans', 'Noto Color Emoji', sans-serif;
                margin: 1in;
                font-size: 11pt;
                line-height: 1.6; /* Aumenta o espaço entre linhas para melhor leitura */
                color: #333; /* Cinza escuro é mais suave para os olhos que preto puro */
            }}

            /* --- CONTROLE DE LAYOUT E PAGINAÇÃO --- */
            h2 {{
                /* A regra mágica: todo título de "Dia" começará em uma página nova */
                page-break-before: always;
                /* Evita que a página quebre logo depois de um título */
                page-break-after: avoid;
            }}
            p, ul {{
                /* Evita que uma única linha de um parágrafo fique isolada
                   no início ou no fim de uma página (viúvas e órfãs) */
                widows: 2;
                orphans: 2;
            }}

            /* --- ESTILOS DOS ELEMENTOS --- */
            h1 {{
                font-size: 26pt; /* Um pouco maior para mais destaque */
                font-weight: 700;
                text-align: center;
                color: #000;
                margin-bottom: 25px;
                page-break-after: avoid;
            }}
            h2 {{
                font-size: 18pt;
                font-weight: 700;
                text-align: center;
                color: #111;
                margin-top: 0; /* Como está no topo da pág, não precisa de margem */
                margin-bottom: 30px; /* Mais espaço depois do título do dia */
                padding-bottom: 10px; /* Espaço entre o texto e a linha */
                /* Uma linha divisória elegante no lugar do fundo cinza */
                border-bottom: 2px solid #E6E6E6;
            }}
            h3 {{
                font-size: 14pt;
                font-weight: 700;
                text-align: left; /* Alinhado à esquerda para subtítulos fica mais legível */
                color: #111;
                margin-top: 24px; /* Mais espaço antes de cada subtítulo */
                margin-bottom: 8px;
            }}
            ul {{
                padding-left: 25px;
                list-style-type: '•  '; /* Bullet personalizado com mais espaço */
            }}
            li {{
                margin-bottom: 10px; /* Mais espaço entre os itens da lista */
                padding-left: 5px;
            }}
            p {{
                 margin-bottom: 12px;
            }}
            strong {{
                font-weight: 700;
            }}
        </style>
    </head>
    <body>
        <h1>{title} {emoji}</h1>
        {html_body}
    </body>
    </html>
    """

    try:
        pdf_bytes = HTML(string=html_string).write_pdf()
        return pdf_bytes
    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar o PDF com WeasyPrint: {e}")
        return None

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