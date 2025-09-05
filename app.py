import streamlit as st

st.set_page_config(
    page_title="GuIA",  # Novo Título
    page_icon="arquivos/logo_GuIA.png", # Alterado para usar o avatar do assistente
    layout='wide',                       # Melhor aproveitamento do espaço
    initial_sidebar_state="expanded"
)

paginas = {
    "Home": [st.Page("paginas/home.py", title="Home", icon='🏠', default=True)]
}

if st.user.is_logged_in:
    paginas["Roteiros"] = [st.Page("paginas/Criar.py", title="Criar Roteiros", icon='📝'), st.Page("paginas/ver.py", title="Seus Roteiros", icon='🗺')]

pg = st.navigation(paginas)
pg.run()

if st.user.is_logged_in:
    st.set_page_config(initial_sidebar_state="expanded")
    
    with st.sidebar:
        if st.button("Logout", key="logout_button_global", type='secondary', icon=':material/logout:', use_container_width=True):
            st.logout()