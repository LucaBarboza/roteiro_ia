import streamlit as st

if not st.user.is_logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image('arquivos/teste1.png', width=200, use_container_width=True)
        st.title("GuIA de Viagem") 
        st.markdown("Faça login com sua conta Google para começar.")
        if st.button("Login com Google", type="primary", use_container_width=True, icon=':material/login:'):
            st.login()

else:
    st.write(f"Olá, {st.user.name}!")
    