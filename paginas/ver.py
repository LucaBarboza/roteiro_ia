import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from fpdf import FPDF

# --- Definição da Classe e Funções para o PDF ---
# (Coloquei aqui para manter tudo em um arquivo só e simplificar)

class PDF(FPDF):
    def header(self):
        self.add_font('DejaVu', '', 'assets/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'assets/DejaVuSans-Bold.ttf', uni=True)
        self.set_font('DejaVu', '', 24)
        
        emojis = getattr(self, 'emojis', '')
        pais = getattr(self, 'pais', 'Roteiro')
        
        titulo_pagina = f'{pais} {emojis}'.encode('latin-1', 'replace').decode('latin-1')
        
        self.cell(0, 10, titulo_pagina, 0, 1, 'C')
        self.ln(10) 

    def chapter_title(self, label):
        self.set_font('DejaVu', 'B', 18)
        texto_sanitizado = label.replace('## ', '').encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(w=0, h=10, text=texto_sanitizado, align='L', ln=True)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('DejaVu', '', 12)
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                texto_sanitizado = f'  •  {line[2:].strip()}'.encode('latin-1', 'replace').decode('latin-1')
                self.multi_cell(0, 7, texto_sanitizado, ln=True)
            elif ':' in line:
                partes = line.split(':', 1)
                parte1_sanitizada = (partes[0] + ':').encode('latin-1', 'replace').decode('latin-1')
                parte2_sanitizada = partes[1].strip().encode('latin-1', 'replace').decode('latin-1')
                self.set_font('DejaVu', 'B', 12)
                self.cell(self.get_string_width(parte1_sanitizada) + 1, 7, parte1_sanitizada)
                self.set_font('DejaVu', '', 12)
                self.multi_cell(0, 7, parte2_sanitizada, ln=True)
            else:
                texto_sanitizado = line.encode('latin-1', 'replace').decode('latin-1')
                self.multi_cell(0, 7, texto_sanitizado, ln=True)
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

    # CORREÇÃO AQUI: Remova o .encode('latin-1')
    return pdf.output(dest='S')
    
    for i, secao in enumerate(secoes):
        if not secao.strip():
            continue
        partes = secao.split('\n', 1)
        titulo = partes[0].strip()
        corpo = partes[1].strip() if len(partes) > 1 else ""
        pdf.chapter_title(titulo)
        pdf.chapter_body(corpo)
    return pdf.output(dest='S').encode('latin-1')

# --- Conexão com Firebase ---

@st.cache_resource
def conectar_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

# --- Lógica Principal da Página ---

st.title("Seus Roteiros Salvos")

db = conectar_firebase()
colecao = 'usuarios2'

doc = db.collection(colecao).document(st.user.email).get()
dados = doc.to_dict() if doc.exists else {}
roteiros = dados.get('roteiros', [])
    
# Inicializa o estado da sessão para controlar qual roteiro está aberto
if 'roteiro_aberto' not in st.session_state:
    st.session_state.roteiro_aberto = None

if not roteiros:
    st.info("Você ainda não salvou nenhum roteiro.")
else:
    # Itera sobre cada roteiro salvo
    for i, roteiro in enumerate(roteiros):
        with st.container(border=True):
            pais = roteiro.get('pais', 'País Desconhecido')
            emojis = roteiro.get('emojis', '')
            
            st.subheader(f"{pais} {emojis}")
            
            # Lógica para abrir/fechar o roteiro usando seu índice (i)
            is_open = (st.session_state.roteiro_aberto == i)
            button_label = "Fechar Roteiro" if is_open else "Ver Roteiro"
            
            if st.button(button_label, key=f"toggle_{i}", use_container_width=True):
                st.session_state.roteiro_aberto = None if is_open else i
                st.rerun()
            
            # Se o roteiro estiver aberto, mostra os detalhes e os botões de ação
            if is_open:
                st.markdown("---")
                st.markdown(roteiro['texto'])
                st.markdown("---")

                pdf_bytes = criar_pdf_roteiro(roteiro['texto'], emojis, pais)
                
                # Layout para os botões de ação
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.download_button(
                        label="📥 Baixar em PDF",
                        data=pdf_bytes,
                        file_name=f"roteiro_{pais.lower().replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"download_{i}",
                        use_container_width=True
                    )

                with col2:
                    if st.button("🗑️ Deletar", key=f"delete_{i}", help="Deletar este roteiro", use_container_width=True):
                        doc_ref = db.collection(colecao).document(st.user.email) 
                        doc_ref.update({
                            'roteiros': firestore.ArrayRemove([roteiro])
                        })
                        st.success(f"Roteiro para {pais} deletado!")
                        st.session_state.roteiro_aberto = None # Reseta o estado
                        st.rerun()