import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import re


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

    styles.add(ParagraphStyle(
        name='TituloPrincipal', parent=styles['h1'], fontSize=26, spaceAfter=20, alignment=1, textColor=colors.HexColor('#0d47a1')
    ))
    styles.add(ParagraphStyle(
        name='DiaTitulo', parent=styles['h2'], fontSize=16, spaceBefore=22, spaceAfter=12, textColor=colors.HexColor('#1565c0'), fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='Topico', parent=styles['Normal'], spaceAfter=4, fontName='Helvetica-Bold', textColor=colors.HexColor('#333333')
    ))
    styles.add(ParagraphStyle(
        name='Corpo', parent=styles['Normal'], spaceAfter=12, firstLineIndent=0, leading=15, alignment=4 # Justificado
    ))

    conteudo = []
    conteudo.append(Paragraph(f"🗺️ Roteiro para {pais} {emojis}", styles['TituloPrincipal']))

    paragrafo_atual = ""

    def processar_paragrafo(texto, estilo):
        """Função interna para processar e adicionar um parágrafo."""
        if texto.strip():
            texto_formatado = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)
            conteudo.append(Paragraph(texto_formatado, estilo))
            conteudo.append(Spacer(1, 6)) # Pequeno espaço após cada parágrafo

    linhas = texto_roteiro.strip().split('\n')

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        if linha.startswith('Dia ') or linha.startswith('Foco:') or linha.startswith('Sugestão') or ':' in linha:
            processar_paragrafo(paragrafo_atual, styles['Corpo']) 
            paragrafo_atual = "" 

            if linha.startswith('Dia '):
                processar_paragrafo(linha, styles['DiaTitulo'])
            elif ':' in linha:
                partes = linha.split(':', 1)
                topico = partes[0].strip() + ":"
                resto = partes[1].strip()
                processar_paragrafo(topico, styles['Topico'])
                if resto:
                    paragrafo_atual = resto 
            else:
                 paragrafo_atual = linha 
        else:
            paragrafo_atual += " " + linha

    processar_paragrafo(paragrafo_atual, styles['Corpo'])

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