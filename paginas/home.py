import streamlit as st

if not st.user.is_logged_in:
  st.login()
  
else:
  st.write("Olá{getattr(st.user, 'name', 'Usuário')}!")
