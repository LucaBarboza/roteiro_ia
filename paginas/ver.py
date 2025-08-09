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
    with st.container(border=True):
        st.caption(f"Destino: {roteiro['pais']}")                
        if st.button(f"Ver Roteiro", key=roteiro['pais'], use_container_width=True):
            with st.expander(f"Roteiro: {roteiro['pais']}"):
                st.header(f"📍 {roteiro['pais']}")
                st.markdown(roteiro['texto'])
                st.divider()
                if st.button("Fechar", key=f"close_{roteiro['pais']}"):
                    st.rerun()
else:
    st.info("Nenhum roteiro ainda")