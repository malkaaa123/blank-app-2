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

            # Reorganizar as colunas para agrupar gerências com seus anos
            gerencias_colunas = sorted(set(col.split('(')[0].strip() for col in comparacao.columns))
            colunas_ordenadas = []
            for gerencia in gerencias_colunas:
                colunas_ordenadas.extend(
                    [col for col in comparacao.columns if col.startswith(gerencia)]
                )
            comparacao = comparacao[colunas_ordenadas]

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

            # Garantir que os DataFrames tenham os mesmos índices e colunas antes de calcular deltas
            base_2023_alinhada = base_2023_filtrada.set_index(base_2023_filtrada.columns[0]).sort_index()
            base_2024_alinhada = base_2024_filtrada.set_index(base_2024_filtrada.columns[0]).sort_index()

            # Garantir alinhamento das colunas
            colunas_comuns = base_2023_alinhada.columns.intersection(base_2024_alinhada.columns)
            base_2023_alinhada = base_2023_alinhada[colunas_comuns]
            base_2024_alinhada = base_2024_alinhada[colunas_comuns]

            # Cálculo das diferenças entre 2023 e 2024
            deltas = base_2024_alinhada - base_2023_alinhada
            deltas_mean = deltas.mean(axis=0).sort_values()

            # Obter as 5 maiores quedas
            maiores_quedas = deltas_mean.head(5).index
            maiores_quedas_detalhes = pd.DataFrame({
                "Afirmativa": maiores_quedas,
                "Queda (Diferença)": deltas_mean.loc[maiores_quedas].values,
                "Resultado 2023": base_2023_alinhada[maiores_quedas].mean(),
                "Resultado 2024": base_2024_alinhada[maiores_quedas].mean()
            })

            # Exibir a seção com as maiores quedas
            st.write("### Afirmativas com Maiores Quedas")
            st.markdown("Abaixo estão as afirmativas com as maiores quedas, mostrando os resultados de 2023, 2024 e a diferença entre eles.")

            # Formatação visual das maiores quedas
            for _, row in maiores_quedas_detalhes.iterrows():
                st.error(f"**{row['Afirmativa']}**: "
                         f"2023: {row['Resultado 2023']:.2f}% → 2024: {row['Resultado 2024']:.2f}% "
                         f"(Queda de {row['Queda (Diferença)']:.2f}%)")

        else:
            st.write("Selecione pelo menos uma Gerência, uma Afirmativa e um Ano para visualizar os dados.")
    else:
        st.write("Carregue as planilhas de 2023 e 2024 para iniciar a análise.")
