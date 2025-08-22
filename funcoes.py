import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from fpdf import FPDF
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH_REGULAR = os.path.join(SCRIPT_DIR, 'arquivos', 'DejaVuSans.ttf')
FONT_PATH_BOLD = os.path.join(SCRIPT_DIR, 'arquivos', 'DejaVuSans-Bold.ttf')


# --- CONECTAR COM O FIREBASE ---
@st.cache_resource
def conectar_firebase():
    """Initializes the Firebase app and returns a Firestore client."""
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()


# --- GERADOR DE PDF ---
def write_styled_text(pdf, text):
    """
    Processes and writes text with multiple styles (bold).
    """
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if not part: continue
        if part.startswith('**') and part.endswith('**'):
            pdf.set_font('DejaVu', 'B', 9)
            pdf.write(7, part[2:-2])
        else:
            pdf.set_font('DejaVu', '', 9)
            pdf.write(7, part)

def create_final_pdf(markdown_text, title):
    """Creates and returns the bytes for a PDF file from markdown text."""
    pdf = FPDF()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.add_font('DejaVu', '', FONT_PATH_REGULAR, uni=True)
    pdf.add_font('DejaVu', 'B', FONT_PATH_BOLD, uni=True)

    pdf.set_font('DejaVu', 'B', 22)
    pdf.multi_cell(0, 12, title, align='C', ln=True)
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
            pdf.set_font('DejaVu', 'B', 9)
            pdf.cell(5, 7, "• ")
            write_styled_text(pdf, text)
            pdf.ln()
            pdf.ln(4)
        else: 
            pdf.set_font('DejaVu', '', 9)
            pdf.multi_cell(0, 7, line, ln=True)
            pdf.ln(4)

    return bytes(pdf.output())

# --- DELETAR ---
def deletar_roteiro(db, colecao, roteiro_para_deletar):
    """
    Deletes a travel itinerary from Firestore.
    Now requires 'db' and 'colecao' to be passed as arguments.
    """
    try:
        doc_ref = db.collection(colecao).document(st.user.email)
        doc_ref.update({'roteiros': firestore.ArrayRemove([roteiro_para_deletar])})

        # If the deleted itinerary was the open one, close it
        if st.session_state.get('roteiro_aberto') == roteiro_para_deletar.get('pais'):
            st.session_state.roteiro_aberto = None
        
        st.success(f"Roteiro para {roteiro_para_deletar.get('pais')} deletado!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao deletar o roteiro: {e}")