import streamlit as st

paginas = {
    "Home": [st.Page("paginas/home.py", title="Home", icon='🏠', default=True)]
}

if st.user.is_logged_in:
    paginas["Criar Roteiros"] = [st.Page("paginas/Criar.py", title="Criar Roteiros", icon='📝')]
    paginas["Seus Roteiros"] = [st.Page("paginas/ver.py", title="Seus Roteiros", icon='🗺')]

pg = st.navigation(paginas)
pg.run()