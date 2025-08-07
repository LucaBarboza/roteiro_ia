import streamlit as st 

paginas = {
    "Home": [ st.Page("paginas/home.py", title="Home", icon='🏠', default=True)],
    
    "Criar Roteiros": [ st.Page("paginas/Criar.py", title="Criar Roteiros", icon='📝')]
}

pg = st.navigation(paginas)
pg.run()

# comentario
