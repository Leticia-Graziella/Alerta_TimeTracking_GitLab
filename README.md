# Alerta_TimeTracking_GitLab

## 🔎 Visão Geral
Uma aplicação para monitorar mudanças de rótulos em Issues. A cada transição de fila, consulta os timelogs da Issue e valida se o último lançamento de tempo está coerente com a etapa.  Em caso de inconsistências, envia alertas direcionados aos responsáveis por meio de um serviço interno de mensagens
---

## 🔄 Fluxo resumido
1. O GitLab envia um webhook quando labels (rótulos) da Issue mudam.  
2. O serviço calcula quais labels entraram e saíram, e identifica fila de origem e destino.  
3. Busca os timelogs da Issue via GraphQL do GitLab e identifica o último **Summary** lançado.  
4. Com base nas regras, decide se precisa notificar alguém e envia a mensagem para o usuário definido.  
5. Responde `200 OK` ao GitLab.  

---

## 📋 Requisitos
- Python **3.10+** (recomendado)  
- Acesso ao **GitLab GraphQL API** com token válido  
- Acesso ao serviço interno de mensagens em `http://10.15.0.5:8088/EnviarMsgTeamsUser`  

### Dependências Python
- `fastapi`  
- `uvicorn`  
- `requests`  
- `re` 
- `datetime` 

---

## ⚙️ Instalação
1. Crie e ative um ambiente virtual (opcional).  
2. Instale dependências:  
   ```bash
   pip install fastapi
   pip install uvicorn
   pip install requests

---

## 🔧 Configuração
Parâmetros principais:

- **GITLAB_URL:** URL do GitLab (ex.: https://gitlab.seudominio.com)

- **ACCESS_TOKEN:** token de acesso do GitLab com escopo read_api

- **PROJECT_PATH:** caminho completo do projeto no GitLab (ex.: grupo/subgrupo/projeto)

- **FILAS monitoradas:** New, Incompleto, Triado, Desenvolvimento, Code Review, Validacao



