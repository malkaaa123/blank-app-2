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

        if gerencias_selecionadas and afirmativas_selecionadas:
            base_2023_filtrada = base_2023[base_2023.iloc[:, 0].isin(gerencias_selecionadas)]
            base_2024_filtrada = base_2024[base_2024.iloc[:, 0].isin(gerencias_selecionadas)]

            base_2023_filtrada = base_2023_filtrada[[base_2023.columns[0]] + afirmativas_selecionadas]
            base_2024_filtrada = base_2024_filtrada[[base_2024.columns[0]] + afirmativas_selecionadas]

            base_2023_resumo = base_2023_filtrada.set_index(base_2023_filtrada.columns[0])
            base_2024_resumo = base_2024_filtrada.set_index(base_2024_filtrada.columns[0])

            # Cálculo das diferenças entre os anos
            diferencas = base_2024_resumo.mean() - base_2023_resumo.mean()
            diferencas_ordenadas = diferencas.sort_values()

            # Obter as 5 maiores quedas
            maiores_quedas = diferencas_ordenadas.head(5)

            # Exibir as afirmativas com as maiores quedas
            st.write("### Afirmativas com Maiores Quedas")
            st.markdown("As afirmativas abaixo apresentaram as maiores quedas em comparação entre 2023 e 2024.")

            for afirmativa, delta in maiores_quedas.items():
                st.error(f"**{afirmativa}**: Queda de {delta:.2f}%")

        else:
            st.write("Selecione pelo menos uma Gerência e uma Afirmativa para visualizar os dados.")
    else:
        st.write("Carregue as planilhas de 2023 e 2024 para iniciar a análise.")
