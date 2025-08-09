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
    
if roteiros:
    colunas = st.columns(1)
    for i, roteiro in enumerate(roteiros):
        with st.container(border=True):
            col_info, col_delete = st.columns([0.85, 0.15])
            with col_info:
                st.subheader(roteiro.get('titulo', roteiro.get('pais')))
                if st.button(f"Ver Roteiro", key=roteiro['pais'], use_container_width=True):
                    st.header(f"📍 {roteiro['pais']}")
                    st.markdown(roteiro['texto'])
                    st.divider()
                    if st.button("Fechar", key=f"close_{roteiro['pais']}"):
                        st.rerun()
            with col_delete:
                if st.button("🗑️ Deletar", key=f"delete_{i}", help="Deletar este roteiro"):
                    doc_ref = db.collection(colecao).document(st.user.email)
                    doc_ref.update({
                        'roteiros': firestore.ArrayRemove([roteiro])
                        })                        
                    st.session_state.roteiros.remove(roteiro)
                    st.success(f"Roteiro para {roteiro['pais']} deletado!")
                    st.rerun()

else:
    st.info("Nenhum roteiro ainda")