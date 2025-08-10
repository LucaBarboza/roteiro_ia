import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

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
            st.subheader(roteiro['pais'])
            is_open = (st.session_state.roteiro_aberto == roteiro['pais'])
            button_label = "Fechar" if is_open else "Ver Roteiro"
            if st.button(button_label, key=f"toggle_{roteiro['pais']}", use_container_width=True):
                if is_open:
                    st.session_state.roteiro_aberto = None
                else:
                    st.session_state.roteiro_aberto = roteiro['pais']
                st.rerun()
            if is_open:
                st.header(f"📍 {roteiro['pais']}")
                st.markdown(roteiro['texto'])
                st.divider()
            if st.button("🗑️ Deletar", key=f"delete_{i}", help="Deletar este roteiro"):
                doc_ref = db.collection(colecao).document(st.user.email) 
                doc_ref.update({
                    'roteiros': firestore.ArrayRemove([roteiro])
                })
                st.success(f"Roteiro para {roteiro['pais']} deletado!")
                if st.session_state.roteiro_aberto == roteiro['pais']:
                    st.session_state.roteiro_aberto = None
                st.rerun()
else:
    st.info("Nenhum roteiro ainda")