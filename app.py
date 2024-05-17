import json
import os
import pandas as pd
import streamlit as st
import altair as alt

from jira_utils import JiraIssue, download_jira_issues


########## Dialog


@st.experimental_dialog("Download das issues do Jira")
def download():
    jira_url = st.text_input("URL do Jira", value='https://zerumbr.atlassian.net')
    username = st.text_input("Usuário", '')
    password = st.text_input("Auth Token", type="password", value='')
    max_results = st.number_input("Quantidade de resultados", value=100, help='0 significa todos os resultados')
    jql_query = st.text_input("JQL Query", value="project in ('WEB', 'QA', 'OPSEC', 'UX', 'CORE', 'Lynx PM', 'Lynx App', 'DevOps') AND NOT type in subTaskIssueTypes()")
    filename = st.text_input("Nome do arquivo")

    if st.button("Baixar issues"):
        if jira_url and username and password and jql_query:
            with st.spinner(text='Baixando arquivo JSON com issues...'):
                opts = (
                    jira_url, username, password, jql_query, max_results,
                    filename
                )
                download_jira_issues(*opts)
        else:
            st.error("Por favor, preencha todos os campos.")


########## MAIN

### Page config

st.set_page_config(
    page_title='Zerum Goals',
    page_icon=':bar_chart:',
    layout='wide',
)
st.title('Zerum Goals')
st.markdown("_v0.0.1_")

### SIDEBAR

with st.sidebar:
    def file_selector(folder_path='./data'):
        filenames = os.listdir(folder_path)
        selected_filename = st.selectbox('Selecione um arquivo', [''] + filenames)
        return os.path.join(folder_path, selected_filename)

    filename = file_selector()
    st.write('Arquivo selecionado`%s`' % filename)

    if "download" not in st.session_state:
        if st.button("Download das issues do Jira"):
            download()
 

if filename == './data/':
    st.info("Selecione um arquivo na barra lateral")
    st.stop()

with open(filename) as f:
    issues_raw = json.load(f)

issues = [JiraIssue(i) for i in issues_raw]

df = pd.DataFrame([i.as_dict() for i in issues])

zerum_goals = df['zerum_goal'].dropna().unique().tolist()
zerum_metrics = df['zerum_metric'].dropna().unique().tolist()

selected_goal = st.multiselect('Zerum Goal', [''] + zerum_goals)
selected_metric = st.multiselect('Zerum Metric', [''] + zerum_metrics)

if selected_goal:
    df = df[df['zerum_goal'].isin(selected_goal)]

if selected_metric:
    df = df[df['zerum_metric'].isin(selected_metric)]

### Percentual dos status de atividade por Equipe

# Agrupamento por 'project' e 'status', e contagem dos itens em cada grupo
count_by_status = df.groupby(['project', 'status']).size().reset_index(name='count')

# Transformação do DataFrame para que os status sejam colunas
count_by_status_pivot = count_by_status.pivot_table(index='project', columns='status', values='count', fill_value=0)

# Calcular o percentual de cada status em relação ao total de cada projeto
count_by_status_pivot_percentage = count_by_status_pivot.div(count_by_status_pivot.sum(axis=1), axis=0) * 100

# Reset do índice para um formato mais amigável de exibição
count_by_status_pivot_percentage = count_by_status_pivot_percentage.reset_index()

count_by_status_pivot_percentage = count_by_status_pivot_percentage.set_index('project')

container1 = st.container()

with container1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Percentual de status de atividade por Equipe")
        # Inicialização do Streamlit e criação do gráfico de barras
        st.bar_chart(count_by_status_pivot_percentage)

    with col2:
        st.markdown(f"## Total de itens: {df.count()['key']}")
        st.markdown(f"### Aberto: {df[df['status']=='3 - Aberto'].count()['key']}")
        st.markdown(f"### Em andamento: {df[df['status']=='2 - Em andamento'].count()['key']}")
        st.markdown(f"### Pronto: {df[df['status']=='1 - Pronto'].count()['key']}")
        pass

container2 = st.container()
with container2:
    with st.expander('Dados dos itens'):
        st.dataframe(df)