import streamlit as st
import pandas as pd

# Configuração de layout wide e título da página
st.set_page_config(layout="wide", page_title="Análise de Clima Organizacional", page_icon="\U0001F4CA")

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
base_2023 = pd.read_excel(base_2023_file) if base_2023_file and base_2023_file.name.endswith('xlsx') else (pd.read_csv(base_2023_file) if base_2023_file else None)
base_2024 = pd.read_excel(base_2024_file) if base_2024_file and base_2024_file.name.endswith('xlsx') else (pd.read_csv(base_2024_file) if base_2024_file else None)
planilha_adicional = pd.read_excel(aba_extra_file) if aba_extra_file and aba_extra_file.name.endswith('xlsx') else (pd.read_csv(aba_extra_file) if aba_extra_file else None)
planilha_sentimentos = pd.read_excel(sentimentos_file) if sentimentos_file and sentimentos_file.name.endswith('xlsx') else (pd.read_csv(sentimentos_file) if sentimentos_file else None)
planilha_ficha = pd.read_excel(ficha_file) if ficha_file and ficha_file.name.endswith('xlsx') else (pd.read_csv(ficha_file) if ficha_file else None)

# Função para tratar valores de adesão como porcentagem
def formatar_adesao(valor):
    try:
        if isinstance(valor, str) and '%' in valor:
            return float(valor.replace('%', '').strip())
        return float(valor)
    except:
        return None

# Criação de abas
abas = st.tabs([
    "Comparação de Índices", 
    "Ficha Resumida", 
    "Comentários", 
    "Sentimentos", 
    "Flutuações"
])

# Aba 1: Comparação de Índices
with abas[0]:
    if base_2023 is not None and base_2024 is not None:
        st.write("### Comparação de Índices")

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

        if gerencias_selecionadas and afirmativas_selecionadas:
            base_2023_filtrada = base_2023[base_2023.iloc[:, 0].isin(gerencias_selecionadas)]
            base_2023_filtrada = base_2023_filtrada[[base_2023.columns[0]] + afirmativas_selecionadas]

            base_2024_filtrada = base_2024[base_2024.iloc[:, 0].isin(gerencias_selecionadas)]
            base_2024_filtrada = base_2024_filtrada[[base_2024.columns[0]] + afirmativas_selecionadas]

            # Intercalar dados de 2023 e 2024
            comparacao = pd.DataFrame()
            for gerencia in gerencias_selecionadas:
                dados_2023 = base_2023_filtrada[base_2023_filtrada.iloc[:, 0] == gerencia]
                dados_2024 = base_2024_filtrada[base_2024_filtrada.iloc[:, 0] == gerencia]
                if not dados_2023.empty and not dados_2024.empty:
                    for afirmativa in afirmativas_selecionadas:
                        comparacao = pd.concat([
                            comparacao,
                            pd.DataFrame({
                                "Gerência": [gerencia, gerencia],
                                "Ano": ["2023", "2024"],
                                "Afirmativa": [afirmativa, afirmativa],
                                "Valor": [dados_2023[afirmativa].values[0], dados_2024[afirmativa].values[0]]
                            })
                        ], ignore_index=True)

            st.write("### Tabela Intercalada")
            st.dataframe(comparacao)
        else:
            st.write("Selecione pelo menos uma Gerência e uma Afirmativa para visualizar os dados.")
    else:
        st.write("Carregue as planilhas de 2023 e 2024 para iniciar a análise.")

# Aba 2: Ficha Resumida
with abas[1]:
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

                # Maiores Subidas e Quedas
                st.markdown("### Maiores Subidas e Quedas")
                indices = ["ENPS", "IVR"]
                variacoes = pd.DataFrame({
                    "Indicador": indices,
                    "2023": [ficha_info[f"{i} 23"].iloc[0] for i in indices],
                    "2024": [ficha_info[f"{i} 24"].iloc[0] for i in indices]
                })
                variacoes["Variação"] = variacoes["2024"] - variacoes["2023"]
                st.table(variacoes)

# Aba 3: Comentários
with abas[2]:
    if planilha_adicional is not None:
        st.write("### Comentários")
        # Código original mantido para exibição e filtragem

# Aba 4: Sentimentos
with abas[3]:
    if planilha_sentimentos is not None:
        st.write("### Sentimentos")
        # Código original mantido para exibição e filtragem

# Aba 5: Flutuações
with abas[4]:
    if base_2023 is not None and base_2024 is not None:
        st.subheader("Maiores Flutuações de Índices")
        flutuacoes = pd.merge(
            base_2023, base_2024,
            on=base_2023.columns[0],
            suffixes=(" 2023", " 2024")
        )
        flutuacoes.set_index(base_2023.columns[0], inplace=True)
        variacoes = flutuacoes.filter(like=" 2024") - flutuacoes.filter(like=" 2023")
        maiores_subidas = variacoes.max().sort_values(ascending=False).head(5)
        maiores_quedas = variacoes.min().sort_values().head(5)
        
        st.markdown("#### Maiores Subidas")
        st.table(maiores_subidas)

        st.markdown("#### Maiores Quedas")
        st.table(maiores_quedas)
