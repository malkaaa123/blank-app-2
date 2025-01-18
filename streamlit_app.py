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
sentimentos_file = st.sidebar.file_uploader("Upload Planilha de Sentimentos", type=["xlsx", "csv"])
ficha_file = st.sidebar.file_uploader("Upload Planilha Ficha", type=["xlsx", "csv"])

# Variáveis para armazenar os dados
base_2023 = None
base_2024 = None
planilha_adicional = None
planilha_sentimentos = None
planilha_ficha = None

if base_2023_file:
    base_2023 = pd.read_excel(base_2023_file) if base_2023_file.name.endswith('xlsx') else pd.read_csv(base_2023_file)
if base_2024_file:
    base_2024 = pd.read_excel(base_2024_file) if base_2024_file.name.endswith('xlsx') else pd.read_csv(base_2024_file)
if aba_extra_file:
    planilha_adicional = pd.read_excel(aba_extra_file) if aba_extra_file.name.endswith('xlsx') else pd.read_csv(aba_extra_file)
if sentimentos_file:
    planilha_sentimentos = pd.read_excel(sentimentos_file) if sentimentos_file.name.endswith('xlsx') else pd.read_csv(sentimentos_file)
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

# Criação de abas (com "Ficha Resumida" como a segunda aba)
tab1, tab2, tab3, tab4 = st.tabs(["Comparação de Índices", "Ficha Resumida", "Comentários", "Sentimentos"])

# Aba 1: Comparação de Índices
with tab1:
    if base_2023 is not None and base_2024 is not None:
        st.write("### Dados da Comparação de Índices")

        gerencias = base_2023.iloc[:, 0].unique()
        afirmativas = base_2023.columns[1:].tolist()

        selecionar_todas_gerencias = st.checkbox("Selecionar Todas as Gerências")
        if selecionar_todas_gerencias:
            gerencias_selecionadas = list(gerencias)
        else:
            gerencias_selecionadas = st.multiselect("Selecione Gerências", gerencias, default=[])

        selecionar_todas_afirmativas = st.checkbox("Selecionar Todas as Afirmativas")
        if selecionar_todas_afirmativas:
            afirmativas_selecionadas = afirmativas
        else:
            afirmativas_selecionadas = st.multiselect("Selecione Afirmativas", afirmativas, default=[])

        anos_disponiveis = ["2023", "2024"]
        anos_selecionados = st.multiselect("Selecione Anos", anos_disponiveis, default=anos_disponiveis)

        if gerencias_selecionadas and afirmativas_selecionadas and anos_selecionados:
            base_2023_filtrada = base_2023[base_2023.iloc[:, 0].isin(gerencias_selecionadas)]
            base_2023_filtrada = base_2023_filtrada[[base_2023.columns[0]] + afirmativas_selecionadas]

            base_2024_filtrada = base_2024[base_2024.iloc[:, 0].isin(gerencias_selecionadas)]
            base_2024_filtrada = base_2024_filtrada[[base_2024.columns[0]] + afirmativas_selecionadas]

            base_2023_transposta = base_2023_filtrada.set_index(base_2023_filtrada.columns[0]).transpose()
            base_2024_transposta = base_2024_filtrada.set_index(base_2024_filtrada.columns[0]).transpose()

            base_2023_transposta.columns = [f"{col} (2023)" for col in base_2023_transposta.columns]
            base_2024_transposta.columns = [f"{col} (2024)" for col in base_2024_transposta.columns]

            comparacao = pd.concat([base_2023_transposta, base_2024_transposta], axis=1)

            colunas_selecionadas = [col for col in comparacao.columns if any(ano in col for ano in anos_selecionados)]
            comparacao = comparacao[colunas_selecionadas]

            comparacao.replace("**", 0, inplace=True)
            comparacao = comparacao.apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

            def highlight_and_center(val):
                color = 'color: red;' if val < 70 else ''
                return f"{color} text-align: center;"

            styled_comparacao = comparacao.style.applymap(highlight_and_center).set_table_styles([
                dict(selector='th', props=[('text-align', 'center')])
            ])

            st.write("### Tabela Comparativa")
            st.dataframe(styled_comparacao, use_container_width=False, height=600)

            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=True).encode('utf-8')

            csv = convert_df(comparacao)
            st.download_button(
                label="Baixar Comparação em CSV",
                data=csv,
                file_name="comparacao_indices.csv",
                mime="text/csv",
            )
        else:
            st.write("Selecione pelo menos uma Gerência, uma Afirmativa e um Ano para visualizar os dados.")
    else:
        st.write("Carregue as planilhas de 2023 e 2024 para iniciar a análise.")

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

                col5, col6, col7, col8 = st.columns(4)
                col5.metric("ENPS 2023", int(ficha_info['ENPS 23'].iloc[0]))
                col6.metric("ENPS 2024", int(ficha_info['ENPS 24'].iloc[0]))
                col7.metric("IVR 2023", int(ficha_info['IVR 23'].iloc[0]))
                col8.metric("IVR 2024", int(ficha_info['IVR 24'].iloc[0]))

                col9, col10 = st.columns(2)
                col9.metric("Retenção (%)", int(ficha_info['Retenção'].iloc[0]))

# Aba 3: Comentários
with tab3:
    if planilha_adicional is not None:
        st.write("### Dados dos Comentários")
    else:
        st.write("Carregue a planilha de comentários para começar.")

# Aba 4: Sentimentos
with tab4:
    if planilha_sentimentos is not None:
        st.write("### Dados de Sentimentos")
    else:
        st.write("Carregue a planilha de sentimentos para começar.")


