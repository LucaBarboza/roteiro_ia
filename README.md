# GuIA de Viagem 🧭✈️

[![Aplicação Online](https://img.shields.io/badge/Acessar-Site-brightgreen)](https://gerador-roteiroia.streamlit.app/)

**GuIA de Viagem** é uma aplicação web inteligente que cria roteiros de viagem personalizados usando o poder da Inteligência Artificial. Com login de usuário, salvamento em base de dados e exportação para PDF.

---

## 🚀 Sobre o Projeto

O GuIA de Viagem é uma aplicação que utiliza um sistema de agentes de IA para entender o seu destino e as datas desejadas, e então constrói um roteiro detalhado, dia a dia, com logística otimizada, sugestões de atividades e dicas culturais.

### ✨ Funcionalidades Principais

-   **Login de Usuários:** Login com contas Google para uma experiência personalizada.
-   **Geração de Roteiros com IA:** Criação de roteiros de viagem informando apenas o país de destino e as datas.
-   **Sistema Multi-Agente:** A IA opera em três fases (Idealizador, Planejador e Revisor) para garantir roteiros criativos, lógicos e otimizados.
-   **Salvamento em Nuvem:** Seus roteiros são salvos de forma segura no Firebase Firestore, associados à sua conta.
-   **Exportação para PDF:** Baixe uma versão em PDF do seu roteiro de viagem com um único clique.

---

## 🤖 Como Funciona

O GuIA de Viagem é um processo de geração em cadeia que utiliza três agentes de IA para refinar o resultado:

1.  **Idealizador:** Recebe o país e seleciona as 5 cidades mais estratégicas, justificando a escolha.
2.  **Planejador:** Com base nas cidades selecionadas, monta um rascunho do roteiro dia a dia, otimizando a logística de transporte e sugerindo atividades e pratos típicos.
3.  **Revisor:** Pega o rascunho, valida os dados, otimiza o ritmo (especialmente para o dia da chegada), enriquece com dicas e formata a versão final.

---

## 🛠️ Tecnologias Utilizadas

-   **Backend & Frontend:** Python, Streamlit
-   **Inteligência Artificial:** Google Gemini AI
-   **Banco de Dados:** Google Firebase Firestore
-   **Geração de PDF:** WeasyPrint
-   **Autenticação:** Login com o Google

## 👤 Autor

**Luca Barboza**

-   GitHub: [@LucaBarboza](https://github.com/LucaBarboza)
