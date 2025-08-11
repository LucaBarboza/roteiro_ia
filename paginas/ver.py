import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from pypdf import PdfWriter


st.title("Seus Roteiros")

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
            col1, col2, col3 = st.columns([2, 2, 2]) 
            pais = roteiro.get('pais', 'País Desconhecido')
            emojis = roteiro.get('emojis', '')
            st.subheader(f"{pais} {emojis}", )
            is_open = (st.session_state.roteiro_aberto == roteiro['pais'])
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
            with col3:
                if st.button("🗑️ Deletar", key=f"delete_{i}", help="Deletar este roteiro"):
                    doc_ref = db.collection(colecao).document(st.user.email) 
                    doc_ref.update({
                        'roteiros': firestore.ArrayRemove([roteiro])
                    })
                    st.success(f"Roteiro para {pais} deletado!")
                    if st.session_state.roteiro_aberto == roteiro['pais']:
                        st.session_state.roteiro_aberto = None
                    st.rerun()
            if is_open:
                with col1:
                    if st.button("Baixar como PDF", key=f"PDF_{i}"):
                        buffer = io.BytesIO()
                        documentos = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
                        styles = getSampleStyleSheet()
                        titulo_style = ParagraphStyle(
                            'CustomTitle',
                            parent=styles['Heading1'],
                            fontSize=24,
                            spaceAfter=30,
                            textColor=colors.HexColor('#2E7D32'),
                            alignment=1
                            )
                        subtitulo_style = ParagraphStyle(
                            'CustomSubtitle',
                            parent=styles['Heading2'],
                            fontSize=14,
                            spaceAfter=12,
                            textColor=colors.HexColor('#1976D2')
                            )
                            
                        story = []
                        
                        story.append(Paragraph(f"🗺 Roteiro para {pais} {emojis}", titulo_style))
                        story.append(Spacer(1, 20))
                        story.append(roteiro['texto'], subtitulo_style)
                
else:
    st.info("Nenhum roteiro ainda")