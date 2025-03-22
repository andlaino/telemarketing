import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# Configuração do tema do seaborn
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    return relatorio if 'all' in selecionados else relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    return output.getvalue()

def main():
    st.set_page_config(page_title='Telemarketing Analysis', page_icon='📊', layout="wide")
    st.write('# Telemarketing Analysis')
    st.markdown("---")
    
    st.sidebar.image("Bank-Branding.jpg")
    data_file = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])
    
    if data_file is not None:
        bank_raw = load_data(data_file)
        bank = bank_raw.copy()
        
        st.write('## Antes dos filtros')
        st.write(bank_raw.head())
        
        with st.sidebar.form(key='filter_form'):
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))
            idades = st.slider('Idade', int(bank.age.min()), int(bank.age.max()), (int(bank.age.min()), int(bank.age.max())))
            jobs_selected = st.multiselect("Profissão", bank.job.unique().tolist() + ['all'], ['all'])
            marital_selected = st.multiselect("Estado civil", bank.marital.unique().tolist() + ['all'], ['all'])
            default_selected = st.multiselect("Default", bank.default.unique().tolist() + ['all'], ['all'])
            housing_selected = st.multiselect("Tem financiamento imob?", bank.housing.unique().tolist() + ['all'], ['all'])
            loan_selected = st.multiselect("Tem empréstimo?", bank.loan.unique().tolist() + ['all'], ['all'])
            contact_selected = st.multiselect("Meio de contato", bank.contact.unique().tolist() + ['all'], ['all'])
            month_selected = st.multiselect("Mês do contato", bank.month.unique().tolist() + ['all'], ['all'])
            day_of_week_selected = st.multiselect("Dia da semana", bank.day_of_week.unique().tolist() + ['all'], ['all'])
            
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                    .pipe(multiselect_filter, 'job', jobs_selected)
                    .pipe(multiselect_filter, 'marital', marital_selected)
                    .pipe(multiselect_filter, 'default', default_selected)
                    .pipe(multiselect_filter, 'housing', housing_selected)
                    .pipe(multiselect_filter, 'loan', loan_selected)
                    .pipe(multiselect_filter, 'contact', contact_selected)
                    .pipe(multiselect_filter, 'month', month_selected)
                    .pipe(multiselect_filter, 'day_of_week', day_of_week_selected))
            
            submit_button = st.form_submit_button(label='Aplicar')
        
        st.write('## Após os filtros')
        st.write(bank.head())
        st.download_button('📥 Download tabela filtrada em EXCEL', data=to_excel(bank), file_name='bank_filtered.xlsx')
        st.markdown("---")

        fig, ax = plt.subplots(1, 2, figsize=(8, 4))

        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).mul(100).to_frame()
        bank_target_perc = bank.y.value_counts(normalize=True).mul(100).to_frame()
        
        bank_raw_target_perc.index = bank_raw_target_perc.index.map(lambda x: "Sim" if x == "yes" else "Não")
        bank_target_perc.index = bank_target_perc.index.map(lambda x: "Sim" if x == "yes" else "Não")
        
        col1, col2 = st.columns(2)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button('📥 Download', data=to_excel(bank_raw_target_perc), file_name='bank_raw_y.xlsx')
        
        col2.write('### Proporção da tabela com filtros')
        col2.write(bank_target_perc)
        col2.download_button('📥 Download', data=to_excel(bank_target_perc), file_name='bank_y.xlsx')
        st.markdown("---")
        
        st.write('## Proporção de aceite')
        
        if graph_type == 'Barras':
            sns.barplot(x=bank_raw_target_perc.index, y='y', data=bank_raw_target_perc, ax=ax[0])
            ax[0].bar_label(ax[0].containers[0])
            ax[0].set_title('Dados brutos', fontweight="bold")
            ax[0].set_ylabel('')
            
            sns.barplot(x=bank_target_perc.index, y='y', data=bank_target_perc, ax=ax[1])
            ax[1].bar_label(ax[1].containers[0])
            ax[1].set_title('Dados filtrados', fontweight="bold")
            ax[1].set_ylabel('')
        else:
            bank_raw_target_perc.plot(kind='pie', y='y', autopct='%.2f%%', ax=ax[0], legend=False)
            ax[0].set_title('Dados brutos', fontweight="bold")
            ax[0].set_ylabel('')
            
            bank_target_perc.plot(kind='pie', y='y', autopct='%.2f%%', ax=ax[1], legend=False)
            ax[1].set_title('Dados filtrados', fontweight="bold")
            ax[1].set_ylabel('')
        
        st.pyplot(fig)

if __name__ == '__main__':
    main()
