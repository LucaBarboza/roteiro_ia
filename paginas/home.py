import streamlit as st

if not st.user.is_logged_in:
    st.write("Faça o login para continuar.")
    if st.button("Login"):
        st.login()

else:
    st.write(f"Olá, {st.user.name}!")
    
    if st.button("Sair"):
        st.logout()