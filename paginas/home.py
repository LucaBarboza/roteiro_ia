import streamlit as st

if not st.user.is_logged_in:
  if st.button:
    st.login()
  
else:
  st.write(f"Olá {getattr(st.user, 'name', 'Usuário')}!")

if st.button("Sair"):
    st.session_state['logged_in'] = False # ou authenticator.logout()
    st.rerun()