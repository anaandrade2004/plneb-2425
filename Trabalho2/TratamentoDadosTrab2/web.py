import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.oqlf.gouv.qc.ca/ressources/bibliotheque/dictionnaires/vocabulaire-medecine.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def limpar_texto(texto):
    return re.sub(r"\s+", " ", texto).strip()

def extrair_links_por_letra():
    res = requests.get(URL, headers=HEADERS)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    letras_dict = {}

    for letra_li in soup.select("div.langue > ol > li"):
        letra_span = letra_li.find("span", class_="lettrine")
        if not letra_span:
            continue
        letra = letra_span.text.strip()
        letras_dict[letra] = {}

        for termo in letra_li.select("ol > li > a"):
            nome_termo = limpar_texto(termo.text)
            url_termo = termo["href"].strip()
            letras_dict[letra][nome_termo] = url_termo

    return letras_dict

if __name__ == "__main__":
    resultado = extrair_links_por_letra()

    with open("links_termos_por_letra.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print("Termos e URLs extraídos com sucesso.")
