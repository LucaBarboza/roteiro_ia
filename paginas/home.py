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
    st.image("arquivos/teste1.png", use_column_width=True)
    st.title("🌎 GuIA de Viagem 🌎")
    st.write(f"""Olá, {st.user.name}! \n Planeje sua próxima viagem em segundos com o GuIA de Viagem, 
    o aplicativo que cria roteiros por Inteligência Artificial. 
    Apenas informe o país de destino e as datas da sua viagem, 
    e nossa tecnologia gera instantaneamente um plano de viagem otimizado e sob medida. 
    Ao analisar o período exato, 
    nossa IA considera os melhores dias para visitar cada atração, entregando um roteiro completo e inteligente. 
    Ideal para quem busca inspiração e praticidade, 
    o GuIA transforma o planejamento em uma experiência simples.""")
    