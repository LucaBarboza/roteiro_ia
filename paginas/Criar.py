import streamlit as st
import os
import sys
import importlib.util

st.set_page_config(layout="wide")
st.title("🔬 Diagnóstico Profundo do Ambiente v2")
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
    st.subheader("2. Inspecionando o Pacote de Namespace 'google'")
    
    try:
        # Usa importlib.util para inspecionar o pacote
        spec = importlib.util.find_spec("google")
        
        if spec is None:
            st.error("Falha Crítica: Não foi possível encontrar nenhuma especificação para o pacote 'google'.")
        
        elif spec.submodule_search_locations:
            st.success("O pacote 'google' foi identificado como um Pacote de Namespace.")
            st.write("Ele é composto pelos seguintes diretórios:")
            st.json(spec.submodule_search_locations)

            st.subheader("3. Listando o conteúdo dos diretórios do Namespace")
            st.write("Vamos verificar se 'genai' existe em algum desses locais.")

            found_genai = False
            for path in spec.submodule_search_locations:
                st.write(f"--- Verificando: `{path}`")
                try:
                    contents = os.listdir(path)
                    st.json(contents)
                    if "genai" in contents:
                        st.success(f"✅ 'genai' foi encontrado dentro de: {path}")
                        found_genai = True
                except Exception as list_e:
                    st.warning(f"Não foi possível listar o conteúdo de '{path}': {list_e}")
            
            st.divider()
            if found_genai:
                st.warning("MISTÉRIO FINAL: O diretório 'genai' existe, mas a importação falha. Isso sugere um problema raro de permissões ou um arquivo `__init__.py` corrompido dentro da pasta 'genai'.")
            else:
                st.error("🎯 CAUSA CONFIRMADA: Nenhum dos diretórios que compõem o pacote 'google' contém o submódulo 'genai'.")
                st.info("Isso significa que a instalação do 'google-generativeai' falhou em adicionar sua parte ao namespace, provavelmente devido a um conflito com outra biblioteca que também usa o namespace 'google'.")

        else:
            st.warning("O pacote 'google' não é um namespace. Tentando método antigo...")
            st.write(f"Local do arquivo __init__.py: {spec.origin}")
            # Código de fallback se não for namespace, improvável de ser executado
            google_path = os.path.dirname(spec.origin)
            st.write(f"Conteúdo de '{google_path}':")
            st.json(os.listdir(google_path))


    except Exception as spec_e:
        st.error(f"Ocorreu um erro ao tentar inspecionar o pacote 'google': {spec_e}")

