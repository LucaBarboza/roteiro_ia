import streamlit as st

if not st.user.is_logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image('arquivos/Generated Image September 05, 2025 - 12_27AM.jpeg', width=200, use_container_width=True)
        st.title("GuIA de Viagem") 
        st.markdown("Faça login com sua conta Google para começar.")
        if st.button("Login com Google", type="primary", use_container_width=True, icon=':material/login:'):
            st.login()

else:
    st.title("🌎 GuIA de Viagem 🌎")
    st.markdown(f"""
    Olá, **{st.user.name}**!

    Planeje sua próxima viagem em segundos com o GuIA de Viagem, o aplicativo que cria roteiros com Inteligência Artificial. 
    
    Basta informar o país de destino e as datas, e nossa tecnologia gera um plano de viagem sob medida.

    Com o GuIA, sua única preocupação é fazer as malas!
    """)