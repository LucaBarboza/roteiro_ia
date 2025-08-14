# import streamlit as st
# import firebase_admin
# from firebase_admin import credentials, firestore
# from datetime import datetime

# st.title("Seus Roteiros")

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

# if roteiros:
#     for i, roteiro in enumerate(roteiros):
#         with st.container(border=True):
#             pais = roteiro.get('pais', 'País Desconhecido')
#             emojis = roteiro.get('emojis', '')
#             st.subheader(f"{pais} {emojis}", )
#             is_open = (st.session_state.roteiro_aberto == roteiro['pais'])
#             button_label = "Fechar" if is_open else "Ver Roteiro"
#             if st.button(button_label, key=f"toggle_{roteiro['pais']}", use_container_width=True):
#                 if is_open:
#                     st.session_state.roteiro_aberto = None
#                 else:
#                     st.session_state.roteiro_aberto = roteiro['pais']
#                 st.rerun()
#             if is_open:
#                 st.header(f"📍  {pais} {emojis}")
#                 st.markdown(roteiro['texto'])
#                 st.divider()
#             col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
#             with col4:
#                 if st.button("🗑️ Deletar", key=f"delete_{i}", help="Deletar este roteiro"):
#                     doc_ref = db.collection(colecao).document(st.user.email) 
#                     doc_ref.update({
#                         'roteiros': firestore.ArrayRemove([roteiro])
#                     })
#                     st.success(f"Roteiro para {pais} deletado!")
#                     if st.session_state.roteiro_aberto == roteiro['pais']:
#                         st.session_state.roteiro_aberto = None
#                     st.rerun()
                
# else:
#     st.info("Nenhum roteiro ainda")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from fpdf import FPDF
import traceback # Para capturar detalhes completos do erro

st.title("Seus Roteiros")

def sanitize_text(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf_diagnostico(markdown_text, title):
    # Envolvemos toda a função em um try/except para capturar QUALQUER erro
    try:
        st.write("**(A) Dentro da Função:** Iniciando a criação do PDF.")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, sanitize_text(title), ln=True, align='C')
        pdf.ln(10)
        
        for line in markdown_text.split('\n'):
            line = line.strip()
            if not line: continue
            if line.startswith('## '):
                pdf.set_font('Helvetica', 'B', 14)
                pdf.write(8, sanitize_text(line[3:])); pdf.ln(12)
            elif line.startswith('### '):
                pdf.set_font('Helvetica', 'B', 12)
                pdf.write(8, sanitize_text(line[4:])); pdf.ln(10)
            elif line.startswith('* ') or line.startswith('- '):
                pdf.cell(5, 8, "*"); text = line[2:]
                if '**' in text and ':' in text:
                    parts = text.split(':', 1); bold_part = parts[0].replace('**', '').strip() + ':'; regular_part = parts[1].strip()
                    pdf.set_font('Helvetica', 'B', 10)
                    pdf.cell(pdf.get_string_width(sanitize_text(bold_part)) + 1, 8, sanitize_text(bold_part))
                    pdf.set_font('Helvetica', '', 10)
                    pdf.write(8, sanitize_text(regular_part)); pdf.ln(10)
                else:
                    pdf.set_font('Helvetica', '', 10)
                    pdf.write(8, sanitize_text(text)); pdf.ln(10)
            else:
                pdf.set_font('Helvetica', '', 10)
                pdf.write(8, sanitize_text(line)); pdf.ln(10)
        
        st.write("**(B) Dentro da Função:** Comandos de desenho concluídos.")
        output_bytes = pdf.output()
        st.write(f"**(C) Dentro da Função:** `pdf.output()` gerou {len(output_bytes)} bytes. Retornando os bytes.")
        return output_bytes
        
    except Exception as e:
        st.error(f"❌ (D) Dentro da Função: Ocorreu uma exceção INESPERADA ao criar o PDF.")
        st.code(traceback.format_exc())
        return None # Retorna None explicitamente em caso de QUALQUER falha

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
            pais = roteiro.get('pais', 'País Desconhecido'); emojis = roteiro.get('emojis', '')
            st.subheader(f"{pais} {emojis}")
            is_open = (st.session_state.roteiro_aberto == roteiro['pais'])
            button_label = "Fechar" if is_open else "Ver Roteiro"
            
            if st.button(button_label, key=f"toggle_{roteiro['pais']}", use_container_width=True):
                st.session_state.roteiro_aberto = None if is_open else roteiro['pais']
                st.rerun()
                
            if is_open:
                st.header(f"📍  {pais} {emojis}"); st.markdown(roteiro['texto']); st.divider()
                st.warning("--- MODO DE DIAGNÓSTICO ATIVADO ---")

                pdf_title = pais
                st.write(f"**1. Chamando `create_pdf_diagnostico`...**")
                pdf_bytes = create_pdf_diagnostico(roteiro['texto'], pdf_title)

                st.write(f"**2. Função retornou. O tipo de `pdf_bytes` é:** `{type(pdf_bytes)}`")
                if pdf_bytes is not None:
                    st.write(f"**3. Tamanho dos bytes recebidos:** `{len(pdf_bytes)}`")
                else:
                    st.write(f"**3. A variável `pdf_bytes` é:** `None`")

                st.write("**4. Verificando a condição `if pdf_bytes:`...**")
                if pdf_bytes:
                    st.success("**5. CONDIÇÃO VERDADEIRA.** Tentando renderizar o botão.")
                    st.download_button("Baixar PDF (Diagnóstico)", pdf_bytes, f"diag_{pais}.pdf", "application/pdf")
                else:
                    st.error("**5. CONDIÇÃO FALSA.** Botão de download NÃO será renderizado.")
                st.warning("--- FIM DO MODO DE DIAGNÓSTICO ---")

            col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
            with col4:
                if st.button("🗑️", key=f"delete_{i}", help="Deletar este roteiro"):
                    db.collection(colecao).document(st.user.email).update({'roteiros': firestore.ArrayRemove([roteiro])})
                    st.success(f"Roteiro para {pais} deletado!")
                    if st.session_state.roteiro_aberto == roteiro['pais']:
                        st.session_state.roteiro_aberto = None
                    st.rerun()
else:
    st.info("Nenhum roteiro ainda")
