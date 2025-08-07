import streamlit as st

paginas = {
    "Home": [st.Page("paginas/home.py", title="Home", icon='🏠', default=True)]
}

if st.user.is_logged_in:
    paginas["Criar Roteiros"] = [st.Page("paginas/Criar.py", title="Criar Roteiros", icon='📝')]

pg = st.navigation(paginas)
pg.run()