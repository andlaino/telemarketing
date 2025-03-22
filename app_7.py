import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# Configuração do Seaborn
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Função para carregar dados
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

# Função para filtros de multiseleção
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função para converter DataFrame em CSV
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter DataFrame em Excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    return output.getvalue()

# Função principal
def main():
    st.set_page_config(page_title='Telemarketing Analysis', 
                       page_icon='📊',
                       layout="wide")

    st.write('# Telemarketing Analysis')
    st.markdown("---")

    # Carregar imagem na barra lateral
    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image)

    # Upload de arquivo
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    # Processamento dos dados
    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))

            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider('Idade', min_value=min_age, max_value=max_age, value=(min_age, max_age))

            # Filtros
            filters = {
                "Profissão": "job",
                "Estado civil": "marital",
                "Default": "default",
                "Tem financiamento imob?": "housing",
                "Tem empréstimo?": "loan",
                "Meio de contato": "contact",
                "Mês do contato": "month",
                "Dia da semana": "day_of_week"
            }

            selections = {}
            for label, col in filters.items():
                values = bank[col].unique().tolist()
                values.append('all')
                selections[col] = st.multiselect(label, values, ['all'])

            bank = (bank.query("age >= @idades[0] and age <= @idades[1]") 
                        .pipe(multiselect_filter, 'job', selections["job"])
                        .pipe(multiselect_filter, 'marital', selections["marital"])
                        .pipe(multiselect_filter, 'default', selections["default"])
                        .pipe(multiselect_filter, 'housing', selections["housing"])
                        .pipe(multiselect_filter, 'loan', selections["loan"])
                        .pipe(multiselect_filter, 'contact', selections["contact"])
                        .pipe(multiselect_filter, 'month', selections["month"])
                        .pipe(multiselect_filter, 'day_of_week', selections["day_of_week"])
            )

            submit_button = st.form_submit_button(label='Aplicar')

        # Exibir tabela filtrada
        st.write('## Após os filtros')
        st.write(bank.head())

        df_xlsx = to_excel(bank)
        st.download_button(label='📥 Download tabela filtrada em EXCEL',
                           data=df_xlsx,
                           file_name='bank_filtered.xlsx')
        st.markdown("---")

        # Criando proporção de aceite
        fig, ax = plt.subplots(1, 2, figsize=(5, 3))

        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame() * 100
        bank_raw_target_perc.columns = ['y']
        bank_raw_target_perc = bank_raw_target_perc.sort_index()

        try:
            bank_target_perc = bank.y.value_counts(normalize=True).to_frame() * 100
            bank_target_perc.columns = ['y']
            bank_target_perc = bank_target_perc.sort_index()
        except:
            st.error('Erro no filtro')

        # Botões de download dos dados dos gráficos
        col1, col2 = st.columns(2)

        df_xlsx = to_excel(bank_raw_target_perc)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button(label='📥 Download',
                             data=df_xlsx,
                             file_name='bank_raw_y.xlsx')

        df_xlsx = to_excel(bank_target_perc)
        col2.write('### Proporção da tabela com filtros')
        col2.write(bank_target_perc)
        col2.download_button(label='📥 Download',
                             data=df_xlsx,
                             file_name='bank_y.xlsx')

        st.markdown("---")
        st.write('## Proporção de aceite')

        # PLOTS    
        if graph_type == 'Barras':
            sns.barplot(x=bank_raw_target_perc.index, 
                        y='y',
                        data=bank_raw_target_perc, 
                        ax=ax[0])
            ax[0].bar_label(ax[0].containers[0])
            ax[0].set_title('Dados brutos', fontweight="bold")

            sns.barplot(x=bank_target_perc.index, 
                        y='y', 
                        data=bank_target_perc, 
                        ax=ax[1])
            ax[1].bar_label(ax[1].containers[0])
            ax[1].set_title('Dados filtrados', fontweight="bold")
        else:
            bank_raw_target_perc.plot(kind='pie', autopct='%.2f%%', ax=ax[0], y='y', labels=bank_raw_target_perc.index)
            ax[0].set_title('Dados brutos', fontweight="bold")

            bank_target_perc.plot(kind='pie', autopct='%.2f%%', ax=ax[1], y='y', labels=bank_target_perc.index)
            ax[1].set_title('Dados filtrados', fontweight="bold")

        st.pyplot(plt)

if __name__ == '__main__':
    main()
