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
import markdown2
from weasyprint import HTML


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
    """
    Cria um PDF de alta qualidade a partir de um texto Markdown
    usando HTML + CSS com a biblioteca WeasyPrint.
    """

    # Converte o texto principal do roteiro de Markdown para HTML
    corpo_html = markdown2.markdown(texto_roteiro, extras=['fenced-code-blocks', 'tables', 'break-on-newline'])

    # CSS para estilizar o PDF exatamente como na sua imagem de referência
    css_style = """
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #1e1e1e; /* Fundo escuro geral */
            color: #e0e0e0;           /* Cor do texto principal */
            line-height: 1.6;
        }
        h1 {
            font-size: 48px;
            color: #ffffff;
            text-align: center;
            margin-bottom: 40px;
        }
        h2 {
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            background-color: #2a2a2a; /* Fundo escuro para o título do dia */
            padding: 15px;
            margin-top: 40px;
            border-left: 5px solid #03a9f4; /* Detalhe azul */
        }
        ul {
            list-style-type: none; /* Remove os marcadores padrão */
            padding-left: 0;
        }
        li {
            padding-left: 1.5em;
            text-indent: -1.5em; /* Cria um marcador personalizado */
            margin-bottom: 15px;
        }
        li::before {
            content: '•'; /* Marcador de bolinha */
            color: #03a9f4; /* Cor do marcador */
            font-size: 20px;
            margin-right: 10px;
            vertical-align: middle;
        }
        strong, b {
            color: #ffffff; /* Deixa o texto em negrito mais branco */
            font-weight: 700;
        }
    """

    # Monta o documento HTML completo
    html_completo = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Roteiro de Viagem</title>
        <style>{css_style}</style>
    </head>
    <body>
        <h1>📍 {pais} {emojis}</h1>
        {corpo_html}
    </body>
    </html>
    """

    # Usa o WeasyPrint para renderizar o HTML e gerar os bytes do PDF
    pdf_bytes = HTML(string=html_completo).write_pdf()
    
    return pdf_bytes

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