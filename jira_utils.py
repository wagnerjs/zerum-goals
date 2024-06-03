import json
import streamlit as st

from datetime import datetime

from jira import JIRA


class JiraIssue():
    OPEN_STATUS = [
        'Aberto', 'Blocked', 'Backlog',
        'Tarefas pendentes', 'Priorizado', 'Preparado', 'Priorizadas',
        'Open Lower Issues'
    ]
    DOING_STATUS = [
        'Em Refinamento', 'Em Revisão', 'Missing Fix', 'Pronto para revisão',
        'Ready to Review', 'Validação', 'Rejeitada', 'Em análise',
        'Homologação', 'Em andamento', 'Em desenvolvimento'
    ]
    CLOSED_STATUS = ['Concluído', 'Cancelado', 'Pronto', 'UPDATE TESTCASE']

    def __init__(self, raw: dict) -> None:
        self.raw = raw

        self.project = self._get_attr('fields.project.key')
        self.zerum_goal = self._get_attr('fields.customfield_10128.value')
        self.zerum_metric = self._get_attr('fields.customfield_10129.value')
        self.key = self._get_attr('key')

        self.setup_status()

    def print(self):
        print(json.dumps(self.raw, indent=2))

    def as_dict(self):
        d = self.__dict__.copy()
        d.pop('raw')
        return d

    def setup_status(self):
        status = self._get_attr('fields.status.name')

        if status in self.OPEN_STATUS:
            self.status = '3 - Aberto'
        elif status in self.DOING_STATUS:
            self.status = '2 - Em andamento'
        elif status in self.CLOSED_STATUS:
            self.status = '1 - Pronto'
        else:
            self.status = f'{status} - FIXME'
    
    def _get_attr(self, path: str):
        res = self.raw
        for subpath in path.split('.'):
            if res:
                res = res.get(subpath, None)  
        return res


# Função para baixar as issues do Jira
def download_jira_issues(jira_url, username, password, jql_query, max_results,
                         filename):
    try:
        # Conectar ao Jira
        jira = JIRA(server=jira_url, basic_auth=(username, password))
        
        # Buscar issues usando JQL
        issues = jira.search_issues(jql_query, maxResults=max_results)
        
        # Processar e salvar issues em JSON
        issues_list = []
        for issue in issues:
            issues_list.append(issue.raw)
        
        # Salvar issues em um arquivo JSON
        now = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
        fname = filename if filename else f'issues-{now}.json'
        with open(f'./data/{fname}', 'w', encoding='utf-8') as f:
            json.dump(issues_list, f, ensure_ascii=False, indent=4)
        
        st.success(f"Issues baixadas e salvas com sucesso em {fname}")
    except Exception as e:
        st.error(f"Erro ao baixar issues do Jira: {e}")
