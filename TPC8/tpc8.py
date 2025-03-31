import requests
from bs4 import BeautifulSoup
import json

def get_doenca_info(url_href):
    url_doenca = 'https://www.atlasdasaude.pt' + url_href
    response = requests.get(url_doenca)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    div_content = soup.find("div", class_="node-doencas")
    
    # Extrair data
    data_div = div_content.find("div", class_="field-name-post-date")
    data_hora = data_div.div.text.strip() if data_div else "Data não disponível"

    # Extrair conteúdo principal
    content_div = div_content.find("div", class_="field-type-text-with-summary")
    if not content_div:
        return {"url": url_doenca, "date": data_hora, "content": {}}

    # Processar o conteúdo
    content_data = {
        "introducao": [],
        "causas": [],
        "sintomas": [],
        "tratamento": [],
        "artigos_relacionados": []
    }

    current_section = "introducao"
    field_item = content_div.find("div", class_="field-item")
    
    for element in field_item.children:
        if not element.name:
            continue
            
        # Detectar seções principais
        if element.name == 'h2':
            text = element.get_text(strip=True).lower()
            if "causas" in text:
                current_section = "causas"
            elif "sintomas" in text:
                current_section = "sintomas"
            elif "tratamento" in text:
                current_section = "tratamento"
            elif "artigos relacionados" in text.lower():
                current_section = "artigos_relacionados"
        
        # Processar conteúdo conforme a seção atual
        if element.name == 'p':
            content_data[current_section].append(element.get_text(strip=True))
        elif element.name == 'ul' and current_section == "sintomas":
            content_data[current_section] = [li.get_text(strip=True) for li in element.find_all('li')]
        elif element.name == 'h3' and current_section == "artigos_relacionados":
            link = element.find('a')
            if link:
                content_data[current_section].append({
                    "titulo": link.get_text(strip=True),
                    "url": link['href']
                })

    # Extrair nota
    nota_div = div_content.find("div", class_="field-name-field-nota")
    nota = nota_div.get_text(strip=True) if nota_div else ""

    return {
        "url": url_doenca,
        "date": data_hora,
        "content": {
            "descricao": content_data["introducao"],
            "causas": content_data["causas"],
            "sintomas": content_data["sintomas"],
            "tratamento": content_data["tratamento"],
            "artigos_relacionados": content_data["artigos_relacionados"]
        },
        "nota": nota
    }


def doencas_letra(letra):
    url = 'https://www.atlasdasaude.pt/doencasaaz/' + letra
    print(url)
    response = requests.get(url)
   
    html_content=response.text
   
    soup=BeautifulSoup(html_content,'html.parser')

    doencas={}
    for div_row in soup.find_all("div", class_="views-row"):
        designacao=div_row.div.h3.a.text
        doenca_url = div_row.div.h3.a["href"]

        doenca_info = get_doenca_info(doenca_url)

        desc_div=div_row.find("div", class_="views-field-body")
        desc=desc_div.div.text

        doenca_info["resumo"] = desc.strip().replace(" ", " ")

        doencas[designacao]=doenca_info
    
    return doencas


    
res = {}    
for a in range(ord("a"),ord("z")+1):
    letra = chr(a)
    res = res | doencas_letra(letra)



f_out=open("doencas_final.json","w", encoding="utf-8")

json.dump(res,f_out, indent=4, ensure_ascii=False)
f_out.close()