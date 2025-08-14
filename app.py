import streamlit as st

paginas = {
    "Home": [st.Page("paginas/home.py", title="Home", icon='🏠', default=True)]
}

if st.user.is_logged_in:
    paginas["Roteiros"] = [st.Page("paginas/Criar.py", title="Criar Roteiros", icon='📝'), st.Page("paginas/ver.py", title="Seus Roteiros", icon='🗺')]

pg = st.navigation(paginas)
pg.run()

if st.user.is_logged_in:
    with st.sidebar:
        if st.button("Logout", key="logout_button_global", type='secondary', icon=':material/logout:', use_container_width=True):
            st.logout()