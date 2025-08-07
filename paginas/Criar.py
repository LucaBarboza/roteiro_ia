import streamlit as st

try:
    import google.genai as genai
    st.success("SUCESSO! A biblioteca 'google.genai' foi importada corretamente.")
    
    # Se a importação funcionar, podemos até tentar configurar a chave
    # para garantir que a conexão também funciona.
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        st.info("A chave de API foi configurada.")
    except Exception as e:
        st.error(f"A importação funcionou, mas falhou ao configurar a chave: {e}")

except ImportError as e:
    st.error("FALHA NA IMPORTAÇÃO! O erro 'ModuleNotFoundError' persiste.")
    st.exception(e)