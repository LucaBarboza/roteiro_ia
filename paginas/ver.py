import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from fpdf import FPDF

st.title("Seus Roteiros")

@st.cache_resource
def conectar_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

class PDF(FPDF):
    def header(self):
        # Registra a fonte REGULAR (você já tinha essa linha)
        self.add_font('DejaVu', '', 'assets/DejaVuSans.ttf', uni=True)
        
        # ADICIONE ESTA LINHA para registrar a fonte BOLD (NEGRITO)
        self.add_font('DejaVu', 'B', 'assets/DejaVuSans-Bold.ttf', uni=True)

        # O resto do seu método header continua igual...
        self.set_font('DejaVu', '', 24)
        
        emojis = getattr(self, 'emojis', '')
        pais = getattr(self, 'pais', 'Roteiro')
        titulo_pagina = f'{pais} {emojis}'
        
        self.cell(0, 10, titulo_pagina, 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, label):
        self.set_font('DejaVu', 'B', 18)
        self.multi_cell(0, 10, label.replace('## ', ''), 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('DejaVu', '', 12)
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                self.multi_cell(0, 7, f'  •  {line[2:].strip()}')
            elif ':' in line:
                partes = line.split(':', 1)
                self.set_font('DejaVu', 'B', 12)
                self.cell(self.get_string_width(partes[0] + ':') + 1, 7, partes[0] + ':')
                self.set_font('DejaVu', '', 12)
                self.multi_cell(0, 7, partes[1].strip())
            else:
                self.multi_cell(0, 7, line)
        self.ln()

def criar_pdf_roteiro(roteiro_markdown, emojis, pais):
    pdf = PDF()
    
    pdf.emojis = emojis
    pdf.pais = pais
    
    pdf.add_page()
    
    secoes = roteiro_markdown.split('## ')
    
    for i, secao in enumerate(secoes):
        if not secao.strip():
            continue
            
        partes = secao.split('\n', 1)
        titulo = partes[0].strip()
        corpo = partes[1].strip() if len(partes) > 1 else ""
        
        pdf.chapter_title(titulo)
        pdf.chapter_body(corpo)

    return pdf.output(dest='S').encode('latin-1')

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
            st.subheader(f"{pais} {emojis}", )
            is_open = (st.session_state.roteiro_aberto == i)
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
            col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
            pdf_bytes = criar_pdf_roteiro(roteiro['texto'], emojis, pais)
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
            with col1:
                st.download_button(
                label="📥 Baixar em PDF",
                data=pdf_bytes,
                file_name=f"roteiro_{pais.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                key=f"download_{i}",
                use_container_width=True
                )
                
else:
    st.info("Nenhum roteiro ainda")