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

            # Garantir alinhamento de índices e colunas
            base_2023_alinhada = base_2023_filtrada.set_index(base_2023_filtrada.columns[0]).sort_index()
            base_2024_alinhada = base_2024_filtrada.set_index(base_2024_filtrada.columns[0]).sort_index()
            colunas_comuns = base_2023_alinhada.columns.intersection(base_2024_alinhada.columns)
            base_2023_alinhada = base_2023_alinhada[colunas_comuns]
            base_2024_alinhada = base_2024_alinhada[colunas_comuns]

            # Cálculo das diferenças entre 2023 e 2024
            deltas = base_2024_alinhada - base_2023_alinhada

            st.write("### Maiores Subidas e Quedas por Gerência")
            for gerencia in gerencias_selecionadas:
                if gerencia in base_2023_alinhada.index:
                    deltas_gerencia = deltas.loc[gerencia]

                    # Garantir que apenas valores numéricos sejam considerados
                    deltas_gerencia = pd.to_numeric(deltas_gerencia, errors='coerce').dropna()

                    # Calcular as 5 maiores subidas e quedas
                    maiores_quedas = deltas_gerencia.nsmallest(5)
                    maiores_subidas = deltas_gerencia.nlargest(5)

                    st.subheader(f"Gerência: {gerencia}")
                    col1, col2 = st.columns(2)

                    # Exibir maiores quedas
                    with col1:
                        st.markdown("#### Maiores Quedas")
                        for afirmativa, delta in maiores_quedas.items():
                            valor_2023 = round(base_2023_alinhada.at[gerencia, afirmativa])
                            valor_2024 = round(base_2024_alinhada.at[gerencia, afirmativa])
                            st.error(f"**{afirmativa}**: -{round(delta)}% (2023: {valor_2023}%, 2024: {valor_2024}%)")

                    # Exibir maiores subidas
                    with col2:
                        st.markdown("#### Maiores Subidas")
                        for afirmativa, delta in maiores_subidas.items():
                            valor_2023 = round(base_2023_alinhada.at[gerencia, afirmativa])
                            valor_2024 = round(base_2024_alinhada.at[gerencia, afirmativa])
                            st.success(f"**{afirmativa}**: +{round(delta)}% (2023: {valor_2023}%, 2024: {valor_2024}%)")

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

                # Afirmativas Selecionadas
                st.markdown("### Afirmativas Selecionadas")
                afirmativas_selecionadas = [
                    "Este é um lugar psicológica e emocionalmente saudável para trabalhar",
                    "Meu Gerente Executivo promove um ambiente seguro psicologicamente e emocionalmente",
                    "A liderança sabe coordenar pessoas e distribuir tarefas adequadamente",
                    "A empresa me oferece treinamento ou outras formas de desenvolvimento para o meu crescimento profissional",
                    "A liderança deixa claras suas expectativas"
                ]

                afirmativas_info = base_2024[base_2024.iloc[:, 0] == gerencia_selecionada_ficha]

                if not afirmativas_info.empty:
                    col1, col2 = st.columns(2)
                    afirmativas_positivas = []
                    afirmativas_negativas = []

                    for afirmativa in afirmativas_selecionadas:
                        if afirmativa in afirmativas_info.columns:
                            valor = afirmativas_info[afirmativa].iloc[0]
                            if valor >= 70:
                                afirmativas_positivas.append(f"**{afirmativa}: {valor:.0f}%**")
                            else:
                                afirmativas_negativas.append(f"**{afirmativa}: {valor:.0f}%**")

                    # Afirmativas Positivas
                    with col1:
                        st.markdown("#### Afirmativas Positivas")
                        for afirmativa in afirmativas_positivas:
                            st.success(afirmativa)

                    # Afirmativas Negativas
                    with col2:
                        st.markdown("#### Afirmativas Negativas")
                        for afirmativa in afirmativas_negativas:
                            st.error(afirmativa)

                # Top 3 Maiores e Menores Pontuações
                st.markdown("### Top 3 Maiores e Menores Pontuações")
                pontuacoes = afirmativas_info.iloc[0, 1:].sort_values()
                menores = pontuacoes.head(3)
                maiores = pontuacoes.tail(3)

                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("#### Maiores Pontuações")
                    for idx, val in maiores.items():
                        st.success(f"**{idx}: {val:.0f}**")
                with col4:
                    st.markdown("#### Menores Pontuações")
                    for idx, val in menores.items():
                        st.error(f"**{idx}: {val:.0f}**")

                # Exibição de todas as afirmativas
                st.markdown("### Todas as Afirmativas da Gerência")
                todas_afirmativas = afirmativas_info.iloc[:, 1:].transpose()
                todas_afirmativas.columns = ["Pontuação"]
                todas_afirmativas["Status"] = todas_afirmativas["Pontuação"].apply(
                    lambda x: "Alta" if x >= 70 else "Média" if x >= 50 else "Baixa"
                )
                st.table(todas_afirmativas.style.format({"Pontuação": "{:.0f}"}).applymap(
                    lambda v: "color: green;" if v == "Alta" else ("color: orange;" if v == "Média" else "color: red;"),
                    subset=["Status"]
                ))


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

        # Filtro por palavra-chave
        palavras_chave = {
            "Assédio": ["assédio", "perseguição", "ameaça", "humilhação", "desrespeito", 
                         "pressão", "discriminação", "abuso", "exploração", "horrível", 
                         "odeio", "ignorado"],
            "Desempenho": ["trabalho", "meta", "produtividade", "resultado"],
        }

        tema_selecionado = st.selectbox("Selecione um Tema de Palavra-Chave", ["Todos"] + list(palavras_chave.keys()))

        # Busca livre por palavras-chave
        busca_livre = st.text_input("Busca Livre por Palavras-Chave", value="")

        # Filtrar os dados
        if gerencia_selecionada_extra and pergunta_selecionada_extra:
            planilha_filtrada = planilha_adicional[
                (planilha_adicional.iloc[:, 0].isin(gerencia_selecionada_extra)) &
                (planilha_adicional.iloc[:, 1].isin(pergunta_selecionada_extra))
            ]

            if tema_selecionado != "Todos":
                palavras = palavras_chave[tema_selecionado]
                planilha_filtrada = planilha_filtrada[planilha_filtrada.iloc[:, 2].str.contains(
                    '|'.join(palavras), case=False, na=False
                )]

            if busca_livre:
                planilha_filtrada = planilha_filtrada[planilha_filtrada.iloc[:, 2].str.contains(
                    busca_livre, case=False, na=False
                )]

            # Exibir comentários como blocos expansíveis abertos
            for index, row in planilha_filtrada.iterrows():
                with st.expander(f"{row[1]} (Gerência: {row[0]})", expanded=True):
                    st.write(row[2])

            # Permitir download
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

# Aba 4: Sentimentos
with tab4:
    if planilha_sentimentos is not None:
        st.write("### Dados de Sentimentos")

        # Filtro de gerências
        gerencias_sentimentos = planilha_sentimentos['gerencia'].unique()

        selecionar_todas_gerencias_sentimentos = st.checkbox("Selecionar Todas as Gerências", key="sentimentos_gerencias")
        if selecionar_todas_gerencias_sentimentos:
            gerencias_selecionadas_sentimentos = list(gerencias_sentimentos)
        else:
            gerencias_selecionadas_sentimentos = st.multiselect("Selecione Gerências", gerencias_sentimentos, default=[])

        if gerencias_selecionadas_sentimentos:
            # Filtrar dados por gerências selecionadas
            sentimentos_filtrados = planilha_sentimentos[
                planilha_sentimentos['gerencia'].isin(gerencias_selecionadas_sentimentos)
            ]

            # Exibir tabela
            st.dataframe(sentimentos_filtrados, use_container_width=True)

            # Permitir download
            @st.cache_data
            def convert_df_sentimentos(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_sentimentos = convert_df_sentimentos(sentimentos_filtrados)
            st.download_button(
                label="Baixar Dados Filtrados de Sentimentos",
                data=csv_sentimentos,
                file_name="sentimentos_filtrados.csv",
                mime="text/csv",
            )
        else:
            st.write("Selecione pelo menos uma Gerência para visualizar os dados de sentimentos.")
    else:
        st.write("Carregue a planilha de sentimentos para começar.")

    
