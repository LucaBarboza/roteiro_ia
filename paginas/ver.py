import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.title("Seus Roteiros")

@st.cache_resource
def conectar_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

def gerar_pdf(pais, emojis, texto_roteiro):
    buffer = io.BytesIO()
    documento = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()

    titulo_principal_style = ParagraphStyle(
        'TituloPrincipal', parent=styles['h1'], fontSize=24, spaceAfter=20, alignment=1, textColor=colors.HexColor('#2E7D32')
    )
    dia_style = ParagraphStyle(
        'DiaTitulo', parent=styles['h2'], fontSize=16, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor('#1976D2')
    )
    topico_style = ParagraphStyle(
        'Topico', parent=styles['Normal'], spaceAfter=2, fontName='Helvetica-Bold'
    )
    corpo_style = ParagraphStyle(
        'Corpo', parent=styles['Normal'], spaceAfter=10, firstLineIndent=15, leading=14
    )
    
    conteudo = []
    
    conteudo.append(Paragraph(f"🗺️ Roteiro para {pais} {emojis}", titulo_principal_style))

    linhas = texto_roteiro.strip().split('\n')

    for linha in linhas:
        if not linha.strip():
            continue

        if linha.strip().startswith('Dia '):
            conteudo.append(Paragraph(linha, dia_style))
        
        elif ': — Dica:' in linha:
            partes = linha.split(': — Dica:', 1)
            topico_texto = partes[0].strip() + ":"
            dica_texto = "<b>Dica:</b> " + partes[1].strip().replace('"', '')

            conteudo.append(Paragraph(topico_texto, topico_style))
            conteudo.append(Paragraph(dica_texto, corpo_style))

        elif ':' in linha and len(linha.split(':', 1)[0]) < 40: 
            partes = linha.split(':', 1)
            topico_texto = partes[0].strip() + ":"
            descricao_texto = partes[1].strip()

            conteudo.append(Paragraph(topico_texto, topico_style))
            conteudo.append(Paragraph(descricao_texto, corpo_style))
            
        else:
            conteudo.append(Paragraph(linha, corpo_style))

    documento.build(conteudo)
    return buffer.getvalue()

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
            col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
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
            if is_open:
                with col1:
                    # Remova o 'if' e apenas chame a função diretamente
                    st.download_button(
                        label="Baixar PDF",
                        data = gerar_pdf(
                            pais=roteiro.get('pais', 'País Desconhecido'),
                            emojis=roteiro.get('emojis', ''),
                            texto_roteiro=roteiro.get('texto', 'Conteúdo não disponível.')
                        ),
                        file_name=f"roteiro_{roteiro.get('pais', 'roteiro')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
else:
    st.info("Nenhum roteiro ainda")