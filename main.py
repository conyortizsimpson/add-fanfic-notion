import requests, json
from bs4 import BeautifulSoup

token = 'secret_JZVt3QbVLzoV9zF3MCUrxyjbZMS8YCVqMsNTIDb9ZA7'
dbid = '2097bfb00d764721b7473a9666320b4f'

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13"
}


def readDatabase(databaseId, headers):
    readUrl = f"https://api.notion.com/v1/databases/{databaseId}/query"

    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()
    print(res.status_code)
    # print(res.text)

    with open('./db.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)


def createPage(databaseId, headers, diccionario):
    createUrl = 'https://api.notion.com/v1/pages'

    newPageData = {
        "parent": {"database_id": databaseId},
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": diccionario['title']
                        }
                    }
                ]
            },
            "Summary": {
                "rich_text": [
                    {
                        "text": {
                            "content": diccionario['summary']
                        }
                    }
                ]
            },
            "Read": {
                "checkbox": diccionario['read']
            },
            "Tags": {
                "multi_select": [{"name": i} for i in diccionario['freeform']]
            },
            "Category": {
                "multi_select": [{"name": i} for i in diccionario['category']]
            },
            "Relationships": {
                "multi_select": [{"name": i} for i in diccionario['relationship']]
            },
            "Rating": {
                "select": {"name": diccionario['rating'][0]}
            },
            "Fandom": {
                "multi_select": [{"name": i} for i in diccionario['fandom']]
            },
            "Completed": {
                "select": {"name": diccionario['completed']}
            },
            "Chapters": {
                "number": int(diccionario['chapters'])
            },
            "Words": {
                "number": int(diccionario['words'])
            },
            "Published": {
                "date": {"start": diccionario['published']}
            },
            "Last Update": {
                "date": {"start": diccionario['status']}
            },
            "Link": {
                "url": diccionario['url']
            },
        }
    }
    
    data = json.dumps(newPageData)
    # print(str(uploadData))

    res = requests.request("POST", createUrl, headers=headers, data=data)

    print(res.status_code)
    print(res.text)


def fanfic_a_dic(url_fanfic, leido):
    dic = {}
    page = requests.get(url_fanfic)
    soup = BeautifulSoup(page.content, "html.parser")

    inicio = soup.find_all("div", class_="preface group")
    for i in inicio:
        titulo = i.find("h2", class_="title heading").text.strip().title()
        sumario = i.find("div", class_="summary module").text.split('Summary:')[1].strip()

    dic['title'] = titulo
    dic['summary'] = sumario
    dic['read'] = leido

    tags = ["rating", "category", "relationship", "fandom", "freeform"]
    lista = []
    for t in tags:
        resultado = soup.find_all("dd", class_=f"{t} tags")
        l = []
        for r in resultado:
            tag = r.find_all("a", class_="tag")
            for ta in tag:
                l.append(ta.text)
        lista.append(l)
    for r in range(len(lista)):
        dic[tags[r]] = lista[r]

    status = soup.find_all("dl", class_="stats")
    for s in status:
        s.find_all("dd")
        for ss in s:
            if "dt" not in str(ss):
                texto = ss.text
                tipo = str(ss).split("\"")[1]
                if "/" in texto:
                    a = texto.split("/")[0]
                    b = texto.split("/")[1]
                    if a == b:
                        dic["completed"] = 'Yes'
                    else:
                        dic["completed"] = 'No'
                    texto = a
                dic[tipo] = texto
    dic['url'] = url_fanfic

    tags_lista = dic["freeform"]
    relaciones = dic["relationship"]
    tags_arreglados = []
    for t in range(len(tags_lista)):
        largo = len(tags_lista[t].split(" "))
        minusculas = tags_lista[t].lower()
        if "minor" in minusculas or "/" in minusculas:
            relaciones.append(tags_lista[t])
        elif largo > 2:
            pass
        else:
            tags_arreglados.append(tags_lista[t].title())

    dic["freeform"] = tags_arreglados
    dic["relationship"] = relaciones

    return dic

url = " "
while url != "":
    url = input("Ingresa el link del primer capítulo en Ao3: ")
    leido = input("¿Lo leíste?\n1) Sí\n) No\n-Respuesta: ")
    while leido not in ["1", "2"]:
        leido = input("¿Lo leíste?\n1) Sí\n2) No\n-Respuesta: ")
    if leido == "1":
        a = fanfic_a_dic(url, True)
    else:
        a = fanfic_a_dic(url, False)
    createPage(dbid, headers, a)
    print("Se ha agregado con éxito\n")
