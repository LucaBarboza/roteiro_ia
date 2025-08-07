import streamlit as st

if not st.user.is_logged_in:
  st.login()
  
else:
  st.write(f0."Olá{getattr(st.user, 'name', 'Usuário')}!")
