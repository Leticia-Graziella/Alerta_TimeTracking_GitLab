import requests 
import re
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime

gitlab_url =  #URL DO GIT-LAB
access_token = #Token do GitLab
project_path =  #Nome do projeto do GitLab
app = FastAPI()
 
filas = {"New","Incompleto", "Triado","Desenvolvimento", "Code Review","Validacao"}

def buscar_timelogs_todas_issues(issue_iid):
    headers = {"Authorization": f"Bearer {access_token}"}

    query = f"""
    query {{
      project(fullPath: "{project_path}") {{
        issues(iid: "{issue_iid}") {{
          nodes {{
            iid
            title
            assignees{{
                edges{{
                    node{{
                        id
                        username
                    }}
                }}
            }}
            timelogs{{
              totalSpentTime
              nodes {{
                id
                spentAt
                timeSpent
                summary
                user {{
                  name
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

    response = requests.post(
        f"{gitlab_url}/api/graphql",
        json={"query": query},
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Erro {response.status_code}: {response.text}")

    data = response.json()
    issues = data["data"]["project"]["issues"]["nodes"]

    linhas = []
    for issue in issues:
        linhas.append({
                "Chamado": issue.get("title")
            })
        for edge in issue.get("assignees", {}).get("edges", []):
            nome = edge.get("node", {}).get("username", "")
            linhas.append({
                "Integrador": nome
            })

        for t in issue["timelogs"]["nodes"]:    
            linhas.append({
                "Issue IID": issue["iid"],
                "Timelog ID" : t.get("id",0),
                "Summary": t.get("summary","").strip(),
                "spentAt": t.get("spentAt", "")               
            })

    return linhas


def parse_data(data_str):
    try:
        return datetime.fromisoformat(data_str)
    except:
        return datetime.min

def get_added_items(previous, current,filtro):
    prev_titles = {item["title"] for item in previous}
    curr_titles = {item["title"] for item in current}
    added = curr_titles - prev_titles
    return list(added & filtro)

def get_removed_items(previous, current):
    prev_titles = {item["title"] for item in previous}
    curr_titles = {item["title"] for item in current}
    removed = prev_titles - curr_titles
    return list(removed & filas)


@app.post("/webhook/gitlab")
async def gitlab_webhook(request: Request):
    payload = await request.json()
    changes = payload.get("changes", {})
    id_issues = payload.get("object_attributes", {}).get("iid")
 
    if "labels" in changes:
        previous = changes["labels"].get("previous", [])
        current = changes["labels"].get("current", [])
        fila_destino = get_added_items(previous, current, filas)
        fila_anterior = get_removed_items(previous, current)
 
        #por_nota = buscar_lancamentos_por_nota(id_issues)
        timelogs = buscar_timelogs_todas_issues(str(id_issues))
        
        timelogs_ordenados = sorted(timelogs, key=lambda x: int(re.search(r'\d+', x.get("Timelog ID", "")).group())if re.search(r'\d+', x.get("Timelog ID", "")) else 0)
        ultimo_summary = timelogs_ordenados[-1].get("Summary", "Sem summary") if timelogs_ordenados else "Sem summary"

        chamado = timelogs[0]["Chamado"]

        if fila_anterior and fila_destino:
            if fila_destino[0] =="Triado" or fila_anterior[0] =="New"  :
                integrador = #Responsavel da triagem
            elif fila_anterior[0] =="Desenvolvimento"  :
                 integrador = next((item.get("Integrador") for item in timelogs if item.get("Integrador")), "Sem integrador") 
            elif fila_anterior[0] =="Code Review":
                integrador = #Responsavel do review1
                integrador2 = #Responsavel do review2
                integrador3 = #Responsavel do review3
            else:
                 integrador = next((item.get("Integrador") for item in timelogs if item.get("Integrador")), "Sem integrador") 

            if (fila_destino[0] =="Triado" or fila_anterior[0] =="New") and ultimo_summary != "Triagem"  :
                alerta = f"Lançar tempo de triagem no chamado: {chamado}"
                requests.post(
                    f"http://10.15.0.5:8088/EnviarMsgTeamsUser",
                    json={"user": integrador,"content":alerta}              
                )
                print(f"Alerta! {alerta}" )
            elif fila_anterior[0] =="Desenvolvimento"  and not(ultimo_summary == "Desenvolvimento" or ultimo_summary == "Especificação" or ultimo_summary == "Teste") :
                alerta = f"Lançar tempo de Desenvolvimento, Especificação ou Teste no chamado: {chamado}!"
                requests.post(
                    f"http://10.15.0.5:8088/EnviarMsgTeamsUser",
                    json={"user": integrador,"content":alerta} )
                print(f"Alerta! {alerta}" )
          
            elif fila_anterior[0] =="Code Review"  and ultimo_summary != "Review" :
                alerta = f"Lançar tempo de Review no chamado: {chamado}"
                requests.post(
                    f"http://10.15.0.5:8088/EnviarMsgTeamsUser",
                    json={"user": integrador,"content":alerta} )
                   
                requests.post(
                    f"http://10.15.0.5:8088/EnviarMsgTeamsUser",
                    json={"user": integrador2,"content":alerta} )
                    
                requests.post(
                    f"http://10.15.0.5:8088/EnviarMsgTeamsUser",
                    json={"user": integrador3,"content":alerta} )
                
                print(f"\n \nAlerta! {alerta}" )
            else:
                print(f"\n \n Sem alerta!")
      
            print(f"|Movido de: {fila_anterior[0] if fila_anterior else 'Desconhecida'} \n|Para: {fila_destino[0]} \n| Último Sumary: {ultimo_summary} \n| Receber o alerta:{integrador}\n \n" )
      
        else:
            print("\n \n Ação não monitorada. Nenhum processamento necessário.\n \n ")
       

  
    return JSONResponse(content={"status": "OK"}, status_code=200)

