import streamlit as st
import os
import sys
import pkgutil

st.set_page_config(layout="wide")
st.title("🔬 Diagnóstico Profundo do Ambiente")
st.info("Tentando importar 'google.genai'...")

try:
    # Tenta a importação
    import google.genai as genai
    st.success("🎉 INACREDITÁVEL! A importação funcionou desta vez.")
    st.write("Isso não deveria acontecer com base no erro anterior. Pode ter sido um problema de cache que o Streamlit Cloud resolveu aleatoriamente.")
    st.balloons()

except ImportError as e:
    st.error("❌ A importação falhou como esperado. Iniciando diagnóstico...")
    st.code(f"Erro recebido: {e}")

    st.divider()
    st.subheader("1. Verificando o caminho do sistema (sys.path)")
    st.write("Estes são os locais onde o Python procura por bibliotecas:")
    st.json(sys.path)

    st.divider()
    st.subheader("2. Localizando o pacote 'google'")
    try:
        # Tenta encontrar o caminho para o pacote 'google'
        spec = pkgutil.get_loader("google")
        if spec:
            # Pega o caminho do diretório pai do arquivo do pacote
            google_path = os.path.dirname(spec.get_filename("google"))
            st.success(f"O pacote 'google' foi encontrado em: {google_path}")

            st.subheader("3. Listando o conteúdo da pasta 'google'")
            st.write("Se 'genai' não estiver nesta lista, outra biblioteca está a criar um pacote 'google' incompleto, confirmando o conflito.")
            
            try:
                # Lista todos os arquivos e pastas dentro do diretório 'google'
                contents = os.listdir(google_path)
                st.write(f"Conteúdo de '{google_path}':")
                st.json(contents)

                if "genai" in contents:
                    st.warning("MISTÉRIO: 'genai' está na pasta, mas a importação falha. Isso pode ser um problema de permissões ou um arquivo `__init__.py` corrompido.")
                else:
                    st.error("🎯 CAUSA PROVÁVEL ENCONTRADA: A pasta 'google' existe, mas não contém 'genai'.")
                    st.info("Isso confirma um conflito de namespace. Outra biblioteca (provavelmente uma dependência do Streamlit) está a criar esta pasta 'google'.")

            except Exception as list_e:
                st.error(f"Não foi possível listar o conteúdo da pasta 'google': {list_e}")

        else:
            st.error("Falha Crítica: Não foi possível localizar o pacote 'google' usando pkgutil. O problema é ainda mais fundamental.")

    except Exception as spec_e:
        st.error(f"Ocorreu um erro ao tentar localizar o pacote 'google': {spec_e}")