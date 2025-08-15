import streamlit as st

# CONECTAR COM O FIREBASE

@st.cache_resource
def conectar_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()


# GERADOR DE PDF

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

# DELETAR

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