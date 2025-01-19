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
base_2023 = pd.read_excel(base_2023_file) if base_2023_file and base_2023_file.name.endswith('xlsx') else (pd.read_csv(base_2023_file) if base_2023_file else None)
base_2024 = pd.read_excel(base_2024_file) if base_2024_file and base_2024_file.name.endswith('xlsx') else (pd.read_csv(base_2024_file) if base_2024_file else None)
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
tab1, tab2, tab3, tab4 = st.tabs(["Comparação de Índices", "Ficha Resumida", "Comentários", "Sentimentos"])

# Aba 1: Comparação de Índices
with tab1:
    if base_2023 is not None and base_2024 is not None:
        st.write("### Comparação de Índices com Visualização Melhorada")

        gerencias = base_2023.iloc[:, 0].unique()
        afirmativas = base_2023.columns[1:].tolist()

        gerencias_selecionadas = st.multiselect("Selecione Gerências", gerencias, default=gerencias[:2])
        afirmativas_selecionadas = st.multiselect("Selecione Afirmativas", afirmativas, default=afirmativas[:5])
        anos_selecionados = st.multiselect("Selecione Anos", ["2023", "2024"], default=["2023", "2024"])

        if gerencias_selecionadas and afirmativas_selecionadas:
            base_2023_filtrada = base_2023[base_2023.iloc[:, 0].isin(gerencias_selecionadas)][[base_2023.columns[0]] + afirmativas_selecionadas]
            base_2024_filtrada = base_2024[base_2024.iloc[:, 0].isin(gerencias_selecionadas)][[base_2024.columns[0]] + afirmativas_selecionadas]

            comparacao = pd.DataFrame()
            for gerencia in gerencias_selecionadas:
                for afirmativa in afirmativas_selecionadas:
                    valor_2023 = base_2023_filtrada[base_2023_filtrada.iloc[:, 0] == gerencia][afirmativa].values[0]
                    valor_2024 = base_2024_filtrada[base_2024_filtrada.iloc[:, 0] == gerencia][afirmativa].values[0]
                    comparacao = pd.concat([comparacao, pd.DataFrame({"Gerência": [gerencia], "Afirmativa": [afirmativa], "2023": [valor_2023], "2024": [valor_2024]})])

            comparacao["Diferença"] = comparacao["2024"] - comparacao["2023"]

            st.dataframe(comparacao)

            st.bar_chart(comparacao.set_index(["Gerência", "Afirmativa"])["Diferença"])
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
                adesao = formatar_adesao(ficha_info['Adesão'].iloc[0])
                col3.metric("Adesão (%)", f"{adesao:.2f}" if adesao is not None else "N/A")
                col4.metric("Feedback", int(ficha_info['Feedback'].iloc[0]))

                st.markdown("### Comparação de Índices Selecionados")
                col5, col6 = st.columns(2)
                col5.metric("ENPS 2023", int(ficha_info['ENPS 23'].iloc[0]))
                col6.metric("ENPS 2024", int(ficha_info['ENPS 24'].iloc[0]))

                st.write("### Maiores Subidas e Quedas de Pontuações")
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
    else:
        st.write("Carregue a planilha Ficha para iniciar a análise.")

