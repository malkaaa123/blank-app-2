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

            comparacao = pd.merge(
                base_2023_filtrada.set_index(base_2023_filtrada.columns[0]),
                base_2024_filtrada.set_index(base_2024_filtrada.columns[0]),
                left_index=True,
                right_index=True,
                suffixes=(" (2023)", " (2024)")
            )

            comparacao.reset_index(inplace=True)
            comparacao = comparacao.melt(id_vars=comparacao.columns[0], 
                                         var_name="Ano", 
                                         value_name="Valor")

            comparacao["Ano Base"] = comparacao["Ano"].str.extract(r'\((\d{4})\)')[0]
            comparacao.drop(columns=["Ano"], inplace=True)

            comparacao_pivot = comparacao.pivot(index=comparacao.columns[0], 
                                                columns="Ano Base", 
                                                values="Valor")

            comparacao_pivot.fillna(0, inplace=True)

            # Adicionando coluna de evolução
            comparacao_pivot["Evolução"] = comparacao_pivot["2024"] - comparacao_pivot["2023"]

            # Destaque visual para evolução
            def highlight(val):
                if val > 0:
                    return 'color: green; font-weight: bold;'
                elif val < 0:
                    return 'color: red; font-weight: bold;'
                else:
                    return ''

            st.write("### Tabela Comparativa com Evolução")
            st.dataframe(comparacao_pivot.style.applymap(highlight, subset=["Evolução"]))

            # Permitir download
            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=True).encode('utf-8')

            csv = convert_df(comparacao_pivot)
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


