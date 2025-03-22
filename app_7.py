# Função principal da aplicação
def main():
    # Título principal da aplicação
    st.write('# Telemarketing analisys')
    st.markdown("---")
    
    # Apresenta a imagem na barra lateral da aplicação
    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image)

    # Botão para carregar arquivo na aplicação
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type = ['csv','xlsx'])

    # Verifica se há conteúdo carregado na aplicação
    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):

            # SELECIONA O TIPO DE GRÁFICO
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))
        
            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade', 
                                        min_value = min_age,
                                        max_value = max_age, 
                                        value = (min_age, max_age),
                                        step = 1)

            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected =  st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected =  st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT?
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected =  st.multiselect("Default", default_list, ['all'])

            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected =  st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            # TEM EMPRÉSTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected =  st.multiselect("Tem empréstimo?", loan_list, ['all'])

            # MEIO DE CONTATO?
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected =  st.multiselect("Meio de contato", contact_list, ['all'])

            # MÊS DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected =  st.multiselect("Mês do contato", month_list, ['all'])

            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected =  st.multiselect("Dia da semana", day_of_week_list, ['all'])

            # Encadeamento de métodos para filtrar a seleção
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]") 
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
            )

            submit_button = st.form_submit_button(label='Aplicar')
        
        # Botões de download dos dados filtrados
        st.write('## Após os filtros')
        st.write(bank.head())
        
        df_xlsx = to_excel(bank)
        st.download_button(label='📥 Download tabela filtrada em EXCEL',
                            data=df_xlsx ,
                            file_name= 'bank_filtered.xlsx')
        st.markdown("---")

        # PLOTS    
        if graph_type == 'Barras':
            # Gráfico de Barras
            fig, ax = plt.subplots(1, 2, figsize=(12, 6))  # Aumentei o tamanho da figura para mais espaço

            # Gráfico de Barras (dados brutos)
            if 'y' in bank_raw.columns:
                bank_raw_target_perc = bank_raw['y'].value_counts(normalize=True).to_frame() * 100
                bank_raw_target_perc = bank_raw_target_perc.sort_index()
            else:
                st.error("A coluna 'y' não foi encontrada no conjunto de dados.")
                return  # Interrompe a execução se a coluna 'y' não estiver presente

            # Para o caso de dados filtrados
            if 'y' in bank.columns:
                bank_target_perc = bank['y'].value_counts(normalize=True).to_frame() * 100
                bank_target_perc = bank_target_perc.sort_index()
            else:
                st.error("A coluna 'y' não foi encontrada no conjunto de dados filtrados.")
                return  # Interrompe a execução se a coluna 'y' não estiver presente

            # Mapeando os valores 'yes' para 'sim' e 'no' para 'não'
            bank_raw_target_perc.index = bank_raw_target_perc.index.map({'yes': 'sim', 'no': 'não'})
            bank_target_perc.index = bank_target_perc.index.map({'yes': 'sim', 'no': 'não'})

            # Plotando o gráfico de barras (dados brutos)
            ax[0].bar(bank_raw_target_perc.index, bank_raw_target_perc.values.flatten(), color=['#66b3ff', '#99ff99'])
            ax[0].set_title('Gráfico de barras - Dados brutos', fontweight="bold")
            ax[0].set_ylabel('Proporção (%)')

            # Plotando o gráfico de barras (dados filtrados)
            ax[1].bar(bank_target_perc.index, bank_target_perc.values.flatten(), color=['#66b3ff', '#99ff99'])
            ax[1].set_title('Gráfico de barras - Dados filtrados', fontweight="bold")
            ax[1].set_ylabel('Proporção (%)')

            # Ajuste de layout para não sobrepor
            fig.tight_layout()

            # Exibir gráficos de barras
            st.pyplot(fig)

        elif graph_type == 'Pizza':
            # Verifique se a coluna 'y' está presente nos dados brutos e filtrados
            if 'y' in bank_raw.columns:
                bank_raw_target_perc = bank_raw['y'].value_counts(normalize=True).to_frame() * 100
                bank_raw_target_perc = bank_raw_target_perc.sort_index()
            else:
                st.error("A coluna 'y' não foi encontrada no conjunto de dados.")
                return

            if 'y' in bank.columns:
                bank_target_perc = bank['y'].value_counts(normalize=True).to_frame() * 100
                bank_target_perc = bank_target_perc.sort_index()
            else:
                st.error("A coluna 'y' não foi encontrada no conjunto de dados filtrados.")
                return

            # Gráfico de Pizza (para os dados brutos e filtrados)
            fig_pizza, ax_pizza = plt.subplots(1, 2, figsize=(12, 6))  # Ajustando para mostrar os dois gráficos de pizza lado a lado

            # Gráfico de Pizza para dados brutos
            bank_raw_target_perc.plot(kind='pie', 
                                      y=bank_raw_target_perc.columns[0], 
                                      autopct='%.2f', 
                                      ax=ax_pizza[0], 
                                      labels=bank_raw_target_perc.index,
                                      startangle=90,  # Define o ângulo inicial
                                      legend=True,    # Exibe a legenda do lado
                                      colors=['#66b3ff', '#99ff99'])  # Ajuste de cores
            ax_pizza[0].set_title('Dados brutos', fontweight="bold")

            # Gráfico de Pizza para dados filtrados
            bank_target_perc.plot(kind='pie', 
                                  y=bank_target_perc.columns[0], 
                                  autopct='%.2f', 
                                  ax=ax_pizza[1], 
                                  labels=bank_target_perc.index,
                                  startangle=90,  # Define o ângulo inicial
                                  legend=True,    # Exibe a legenda do lado
                                  colors=['#66b3ff', '#99ff99'])  # Ajuste de cores
            ax_pizza[1].set_title('Dados filtrados', fontweight="bold")

            # Ajuste das legendas
            ax_pizza[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Proporção", fontsize=10)
            ax_pizza[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Proporção", fontsize=10)

            # Ajuste para evitar sobreposição
            fig_pizza.tight_layout(pad=4.0)  # Adiciona espaço entre os gráficos

            # Exibir gráficos de pizza
            st.pyplot(fig_pizza)

# Chama a função principal
if __name__ == "__main__":
    main()
