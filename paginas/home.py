import streamlit as st

if not st.user.is_logged_in:
  if st.button:
    st.login()
  
else:
  st.write(f"Olá {getattr(st.user, 'name', 'Usuário')}!")
