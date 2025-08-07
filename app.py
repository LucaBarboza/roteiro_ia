import streamlit as st 

paginas = {
    "Home": [ st.Page("paginas/home.py", title="Home", icon='🏠', default=True)],
    
    "Criar Roteiros": [ st.Page("paginas/Criar.py", title="Criar Roteiros", icon='📝')]
}

# Usa a estrutura de páginas final (com ou sem Admin)
pg = st.navigation(paginas)
pg.run()

# comentario
