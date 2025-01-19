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
aba_extra_file = st.sidebar.file_uploader("Upload Planilha de Comentários", type=["xlsx", "csv"])
ficha_file = st.sidebar.file_uploader("Upload Planilha Ficha", type=["xlsx", "csv"])

# Variáveis para armazenar os dados
base_2023 = None
base_2024 = None
planilha_adicional = None
planilha_ficha = None

if base_2023_file:
    base_2023 = pd.read_excel(base_2023_file) if base_2023_file.name.endswith('xlsx') else pd.read_csv(base_2023_file)
if base_2024_file:
    base_2024 = pd.read_excel(base_2024_file) if base_2024_file.name.endswith('xlsx') else pd.read_csv(base_2024_file)
if aba_extra_file:
    planilha_adicional = pd.read_excel(aba_extra_file) if aba_extra_file.name.endswith('xlsx') else pd.read_csv(aba_extra_file)
if ficha_file:
    planilha_ficha = pd.read_excel(ficha_file) if ficha_file.name.endswith('xlsx') else pd.read_csv(ficha_file)

# Função para tratar valores de adesão como porcentagem
def formatar_adesao(valor):
    try:
        if isinstance(valor, str) and '%' in valor:
            return float(valor.replace('%', '').strip())
        return float(valor)
    except:
        return None

# Função para calcular as maiores quedas e melhorias
def calcular_variacoes(base_2023, base_2024):
    try:
        base_2023 = base_2023.set_index(base_2023.columns[0])
        base_2024 = base_2024.set_index(base_2024.columns[0])

        # Garantir que as colunas são compatíveis
        common_columns = base_2023.columns.intersection(base_2024.columns)
        base_2023 = base_2023[common_columns]
        base_2024 = base_2024[common_columns]

        # Garantir que os índices são compatíveis
        base_2023 = base_2023.reindex(base_2024.index).fillna(0)
        base_2024 = base_2024.reindex(base_2023.index).fillna(0)

        variacao = base_2024 - base_2023
        maiores_quedas = variacao.min().sort_values().head(5)
        maiores_melhorias = variacao.max().sort_values(ascending=False).head(5)
        return maiores_quedas, maiores_melhorias
    except Exception as e:
        st.error(f"Erro ao calcular variações: {e}")
        return pd.Series(dtype='float64'), pd.Series(dtype='float64')

# Criação de abas (com "Ficha Resumida" como a segunda aba)
tab1, tab2, tab3, tab4 = st.tabs(["Comparação de Índices", "Ficha Resumida", "Comentários", "Maiores quedas/melhorias"])

# Aba 1: Comparação de Índices
with tab1:
    if base_2023 is not None and base_2024 is not None:
        st.write("### Dados da Comparação de Índices")
        # Código original não modificado aqui

# Aba 2: Ficha Resumida
with tab2:
    if planilha_ficha is not None and base_2024 is not None:
        st.subheader("Ficha Resumida")

        gerencias_ficha = base_2024.iloc[:, 0].unique()
        gerencia_selecionada_ficha = st.selectbox("Selecione a Gerência", [""] + list(gerencias_ficha))

        if gerencia_selecionada_ficha:
            ficha_info = planilha_ficha[planilha_ficha['gerencia'] == gerencia_selecionada_ficha]

            if ficha_info.empty:
                st.warning("Nenhuma informação encontrada para a gerência selecionada.")
            else:
                st.markdown("### Informações da Gerência")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Convidados", int(ficha_info['convidados'].iloc[0]))
                col2.metric("Respondentes", int(ficha_info['Respondentes'].iloc[0]))
                adesao = formatar_adesao(ficha_info['Adesão'].iloc[0])
                col3.metric("Adesão (%)", f"{adesao:.2f}" if adesao is not None else "N/A")
                col4.metric("Feedback", int(ficha_info['Feedback'].iloc[0]))

                st.markdown("### Maiores Quedas e Melhorias na Gerência")
                gerencia_dados_2023 = base_2023[base_2023.iloc[:, 0] == gerencia_selecionada_ficha]
                gerencia_dados_2024 = base_2024[base_2024.iloc[:, 0] == gerencia_selecionada_ficha]

                if not gerencia_dados_2023.empty and not gerencia_dados_2024.empty:
                    quedas, melhorias = calcular_variacoes(gerencia_dados_2023, gerencia_dados_2024)

                    st.markdown("**Maiores Quedas:**")
                    for item, valor in quedas.items():
                        st.markdown(f"<p style='color:red'>{item}: {valor:.2f}</p>", unsafe_allow_html=True)

                    st.markdown("**Maiores Melhorias:**")
                    for item, valor in melhorias.items():
                        st.markdown(f"<p style='color:green'>{item}: {valor:.2f}</p>", unsafe_allow_html=True)

# Aba 3: Comentários
with tab3:
    if planilha_adicional is not None:
        st.write("### Dados dos Comentários")

        # Filtros de gerência, pergunta, palavra-chave e busca livre
        gerencias_extra = planilha_adicional.iloc[:, 0].unique()
        perguntas_extra = planilha_adicional.iloc[:, 1].unique()

        selecionar_todas_gerencias_extra = st.checkbox("Selecionar Todas as Gerências", key="extra_gerencias")
        if selecionar_todas_gerencias_extra:
            gerencia_selecionada_extra = list(gerencias_extra)
        else:
            gerencia_selecionada_extra = st.multiselect("Selecione Gerências", gerencias_extra, default=[])

        selecionar_todas_perguntas_extra = st.checkbox("Selecionar Todas as Perguntas")
        if selecionar_todas_perguntas_extra:
            pergunta_selecionada_extra = list(perguntas_extra)
        else:
            pergunta_selecionada_extra = st.multiselect("Selecione Perguntas", perguntas_extra, default=[])

        busca_livre = st.text_input("Busca Livre por Palavras-Chave", value="")

        # Filtrar os dados
        if gerencia_selecionada_extra and pergunta_selecionada_extra:
            planilha_filtrada = planilha_adicional[
                (planilha_adicional.iloc[:, 0].isin(gerencia_selecionada_extra)) &
                (planilha_adicional.iloc[:, 1].isin(pergunta_selecionada_extra))
            ]

            if busca_livre:
                planilha_filtrada = planilha_filtrada[planilha_filtrada.iloc[:, 2].str.contains(
                    busca_livre, case=False, na=False
                )]

            for index, row in planilha_filtrada.iterrows():
                with st.expander(f"{row[1]} (Gerência: {row[0]})", expanded=True):
                    st.write(row[2])

            @st.cache_data
            def convert_df_extra(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_extra = convert_df_extra(planilha_filtrada)
            st.download_button(
                label="Baixar Planilha Filtrada",
                data=csv_extra,
                file_name="comentarios_filtrados.csv",
                mime="text/csv",
            )
        else:
            st.write("Selecione pelo menos uma Gerência e uma Pergunta para visualizar os dados.")
    else:
        st.write("Carregue a planilha de comentários para começar.")

# Aba 4: Maiores quedas/melhorias
with tab4:
    if base_2023 is not None and base_2024 is not None:
        st.write("### Maiores Quedas e Melhorias Gerais")
        quedas, melhorias = calcular_variacoes(base_2023, base_2024)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Maiores Quedas:**")
            for item, valor in quedas.items():
                st.markdown(f"<p style='color:red'>{item}: {valor:.2f}</p>", unsafe_allow_html=True)

        with col2:
            st.markdown("**Maiores Melhorias:**")
            for item, valor in melhorias.items():
                st.markdown(f"<p style='color:green'>{item}: {valor:.2f}</p>", unsafe_allow_html=True)
