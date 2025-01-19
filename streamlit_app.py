import streamlit as st
import pandas as pd

# Configuração de layout wide e título da página
st.set_page_config(layout="wide", page_title="Análise de Clima Organizacional", page_icon="📊")

# Título da aplicação
st.title("Análise de Pesquisa de Clima Organizacional")

# Upload das planilhas
st.sidebar.header("Carregue as Planilhas")
base_2023_file = st.sidebar.file_uploader("Upload Planilha 2023", type=["xlsx", "csv"])
base_2024_file = st.sidebar.file_uploader("Upload Planilha 2024", type=["xlsx", "csv"])
ficha_file = st.sidebar.file_uploader("Upload Planilha Ficha", type=["xlsx", "csv"])
sentimentos_file = st.sidebar.file_uploader("Upload Planilha de Sentimentos", type=["xlsx", "csv"])
aba_extra_file = st.sidebar.file_uploader("Upload Planilha de Comentários", type=["xlsx", "csv"])

# Variáveis para armazenar os dados
base_2023 = pd.read_excel(base_2023_file) if base_2023_file and base_2023_file.name.endswith('xlsx') else (pd.read_csv(base_2023_file) if base_2023_file else None)
base_2024 = pd.read_excel(base_2024_file) if base_2024_file and base_2024_file.name.endswith('xlsx') else (pd.read_csv(base_2024_file) if base_2024_file else None)
planilha_ficha = pd.read_excel(ficha_file) if ficha_file and ficha_file.name.endswith('xlsx') else (pd.read_csv(ficha_file) if ficha_file else None)
planilha_sentimentos = pd.read_excel(sentimentos_file) if sentimentos_file and sentimentos_file.name.endswith('xlsx') else (pd.read_csv(sentimentos_file) if sentimentos_file else None)
planilha_comentarios = pd.read_excel(aba_extra_file) if aba_extra_file and aba_extra_file.name.endswith('xlsx') else (pd.read_csv(aba_extra_file) if aba_extra_file else None)

# Criação de abas
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Comparação de Índices", "Ficha Resumida", "Resumo de Flutuações", "Comentários", "Sentimentos", "Flutuações Detalhadas"])

# Aba 1: Comparação de Índices
with tab1:
    if base_2023 is not None and base_2024 is not None:
        st.write("### Comparação de Índices")

        gerencias = base_2023.iloc[:, 0].unique()
        afirmativas = base_2023.columns[1:].tolist()

        gerencias_selecionadas = st.multiselect("Selecione Gerências", gerencias, default=gerencias[:2])
        afirmativas_selecionadas = st.multiselect("Selecione Afirmativas", afirmativas, default=afirmativas[:5])

        if gerencias_selecionadas and afirmativas_selecionadas:
            comparacao = pd.DataFrame(columns=["Gerência", "Ano", "Afirmativa", "Valor"])

            for gerencia in gerencias_selecionadas:
                for afirmativa in afirmativas_selecionadas:
                    valor_2023 = base_2023.loc[base_2023.iloc[:, 0] == gerencia, afirmativa].values
                    valor_2024 = base_2024.loc[base_2024.iloc[:, 0] == gerencia, afirmativa].values
                    if len(valor_2023) > 0 and len(valor_2024) > 0:
                        comparacao = pd.concat([
                            comparacao,
                            pd.DataFrame({
                                "Gerência": [gerencia, gerencia],
                                "Ano": ["2023", "2024"],
                                "Afirmativa": [afirmativa, afirmativa],
                                "Valor": [valor_2023[0], valor_2024[0]],
                            })
                        ], ignore_index=True)

            st.dataframe(comparacao)

            # Melhorando visualização
            for afirmativa in afirmativas_selecionadas:
                dados_afirmativa = comparacao[comparacao["Afirmativa"] == afirmativa]
                st.line_chart(dados_afirmativa.pivot(index="Ano", columns="Gerência", values="Valor"))

        else:
            st.write("Selecione pelo menos uma Gerência e uma Afirmativa.")
    else:
        st.write("Carregue as planilhas de 2023 e 2024 para iniciar a análise.")

# Aba 2: Ficha Resumida
with tab2:
    if planilha_ficha is not None and base_2024 is not None:
        st.subheader("Ficha Resumida")

        gerencias_ficha = base_2024.iloc[:, 0].unique()
        gerencia_selecionada_ficha = st.selectbox("Selecione a Gerência", gerencias_ficha)

        if gerencia_selecionada_ficha:
            ficha_info = planilha_ficha[planilha_ficha['gerencia'] == gerencia_selecionada_ficha]
            if not ficha_info.empty:
                st.write("### Indicadores da Gerência")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Convidados", int(ficha_info['convidados'].iloc[0]))
                col2.metric("Respondentes", int(ficha_info['Respondentes'].iloc[0]))
                adesao = ficha_info['Adesão'].iloc[0]
                col3.metric("Adesão (%)", adesao)
                col4.metric("Feedback", int(ficha_info['Feedback'].iloc[0]))

                st.markdown("### Maiores Subidas e Quedas de Pontuações")
                comparacao_ficha = pd.DataFrame({
                    "Indicador": ["ENPS", "IVR"],
                    "2023": [ficha_info['ENPS 23'].iloc[0], ficha_info['IVR 23'].iloc[0]],
                    "2024": [ficha_info['ENPS 24'].iloc[0], ficha_info['IVR 24'].iloc[0]],
                })
                comparacao_ficha["Variação"] = comparacao_ficha["2024"] - comparacao_ficha["2023"]

                maiores_subidas = comparacao_ficha.sort_values(by="Variação", ascending=False).head(3)
                maiores_quedas = comparacao_ficha.sort_values(by="Variação").head(3)

                st.write("#### Maiores Subidas")
                st.table(maiores_subidas)

                st.write("#### Maiores Quedas")
                st.table(maiores_quedas)

# Aba 3: Resumo de Flutuações
with tab3:
    if base_2023 is not None and base_2024 is not None:
        st.subheader("Resumo de Flutuações")

        comparacao_geral = pd.merge(
            base_2023, base_2024, on=base_2023.columns[0], suffixes=("_2023", "_2024")
        )
        comparacao_geral["Variação Média"] = comparacao_geral.iloc[:, 1:].mean(axis=1)
        maiores_subidas_geral = comparacao_geral.sort_values(by="Variação Média", ascending=False).head(5)
        maiores_quedas_geral = comparacao_geral.sort_values(by="Variação Média").head(5)

        col1, col2 = st.columns(2)
        with col1:
            st.write("### Maiores Subidas Gerais")
            st.table(maiores_subidas_geral)

        with col2:
            st.write("### Maiores Quedas Gerais")
            st.table(maiores_quedas_geral)

# Aba 4: Comentários
with tab4:
    if planilha_comentarios is not None:
        st.write("### Dados dos Comentários")

        gerencias_comentarios = planilha_comentarios.iloc[:, 0].unique()
        perguntas_comentarios = planilha_comentarios.iloc[:, 1].unique()

        gerencias_selecionadas = st.multiselect("Selecione Gerências", gerencias_comentarios)
        perguntas_selecionadas = st.multiselect("Selecione Perguntas", perguntas_comentarios)

        if gerencias_selecionadas and perguntas_selecionadas:
            comentarios_filtrados = planilha_comentarios[
                (planilha_comentarios.iloc[:, 0].isin(gerencias_selecionadas)) &
                (planilha_comentarios.iloc[:, 1].isin(perguntas_selecionadas))
            ]

            for _, row in comentarios_filtrados.iterrows():
                with st.expander(f"{row[1]} (Gerência: {row[0]})"):
                    st.write(row[2])

            st.download_button(
                label="Baixar Planilha Filtrada",
                data=comentarios_filtrados.to_csv(index=False).encode('utf-8'),
                file_name="comentarios_filtrados.csv",
                mime="text/csv",
            )
    else:
        st.write("Carregue a planilha de Comentários para começar.")

# Aba 5: Sentimentos
with tab5:
    if planilha_sentimentos is not None:
        st.write("### Dados de Sentimentos")

        gerencias_sentimentos = planilha_sentimentos['gerencia'].unique()
        gerencias_selecionadas = st.multiselect("Selecione Gerências", gerencias_sentimentos)

        if gerencias_selecionadas:
            dados_filtrados = planilha_sentimentos[planilha_sentimentos['gerencia'].isin(gerencias_selecionadas)]
            st.dataframe(dados_filtrados)

            st.download_button(
                label="Baixar Dados de Sentimentos",
                data=dados_filtrados.to_csv(index=False).encode('utf-8'),
                file_name="sentimentos.csv",
                mime="text/csv",
            )
    else:
        st.write("Carregue a planilha de Sentimentos para começar.")
