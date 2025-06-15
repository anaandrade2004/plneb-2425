import requests
from bs4 import BeautifulSoup
import json
import time
import re
from deep_translator import GoogleTranslator

# Carrega os links
with open("links_termos_por_letra.json", encoding="utf-8") as f:
    dados_links = json.load(f)

def limpar_texto(texto):
    return re.sub(r'\s+', ' ', texto).strip()

def traduzir(texto):
    try:
        return GoogleTranslator(source='fr', target='pt').translate(texto)
    except:
        return texto
    
def extrair_termos_por_categoria(section, ignorar_com_pill=False):
    termos = []
    for dt in section.select("dt.terme"):
        # Ignorar termos com <small class="pill"> se for pedido
        if ignorar_com_pill and dt.select_one("small.pill"):
            continue
        partes = []
        strong = dt.find("strong")
        abbr = dt.find("abbr")
        if strong:
            partes.append(limpar_texto(strong.text))
        if abbr:
            partes.append(limpar_texto(abbr.text))
        termo_completo = " ".join(partes)
        if termo_completo:
            termos.append(termo_completo)
    return termos

def extrair_pagina(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Erro ao aceder {url}: {e}")
        return None

    soup = BeautifulSoup(res.content, "html.parser")
    main = soup.find("main", class_="main--narrow")
    if not main:
        return None

    item = {"fonte": url}
    ingles = []
    ingles_associado = []

    # Domínio(s)
    item["dominio"] = []
    for field in main.select("div.about-card__field"):
        dt = field.find("dt")
        if dt and dt.get_text(strip=True).lower() == "domaines":
            for li in field.select("dd ol li"):
                partes = [limpar_texto(span.get_text()) for span in li.find_all("span")]
                if partes:
                    # Traduzir cada parte do domínio
                    item["dominio"].append(" > ".join([traduzir(p) for p in partes]))

    # Autor e data
    if autor := main.select_one(".about-card__author dd"):
        item["autor"] = traduzir(limpar_texto(autor.get_text()))
    if data := main.select_one(".about-card__update time"):
        item["data_ultima_atualizacao"] = limpar_texto(data.get_text())

    # Secções com <h2> até termos_privilegiados (sem incluí-lo)
    for h2 in main.find_all("h2"):
        chave_original = limpar_texto(h2.get_text().rstrip(":"))
        chave_inferior = chave_original.lower()

        # Ignorar blocos irrelevantes
        if chave_inferior in ["anglais", "traductions", "partager cette page", "termes privilégiés"]:
            break

        textos = []
        nxt = h2.find_next_sibling()
        while nxt and nxt.name != "h2":
            if nxt.name in ["p", "ul", "ol", "div"]:
                textos.append(limpar_texto(nxt.get_text(" ")))
            nxt = nxt.find_next_sibling()

        if textos:
            chave_traduzida = traduzir(chave_original)
            valor_traduzido = traduzir(" ".join(textos))
            item[chave_traduzida] = valor_traduzido

    # Termes privilégiés (não traduzir)
    sec_priv = main.select_one("div.terms--recommended")
    if sec_priv:
        termos_priv = extrair_termos_por_categoria(sec_priv)
        if termos_priv:
            item["termos_privilegiados"] = termos_priv

    # Termes utilisés dans certains contextes (não traduzir)
    sec_contexto = main.select_one("div.terms--in-between")
    if sec_contexto:
        termos_ctx = extrair_termos_por_categoria(sec_contexto, ignorar_com_pill=False)
        if termos_ctx:
            item["termos_em_contexto"] = termos_ctx

    # Traduções: Inglês e Inglês associado (não traduzir)
    bloco_eng = main.select_one('div[data-indexlang="eng"]')
    if bloco_eng:
        for h4 in bloco_eng.find_all("h4"):
            titulo = limpar_texto(h4.get_text().lower())
            lista = h4.find_next("ol")
            if not lista:
                continue
            termos = [
                limpar_texto(strong.get_text())
                for li in lista.find_all("li")
                if (strong := li.find("strong"))
            ]
            if "terme associé" in titulo:
                ingles_associado += termos
            elif "termes" in titulo or "terme" in titulo:
                ingles += termos

    if ingles:
        item["ingles"] = ingles
    if ingles_associado:
        item["ingles_associado"] = ingles_associado

    return item

# Execução principal
resultado = {}
for letra, termos in dados_links.items():
    resultado[letra] = {}
    print(f"\nLetra: {letra}")
    for palavra, url in termos.items():
        print(f"A processar: {palavra}")
        dado = extrair_pagina(url)
        if dado:
            palavra_traduzida = traduzir(palavra)
            resultado[letra][palavra_traduzida] = dado
        time.sleep(0.5) 

# Guardar JSON
with open("output1.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print("\n Extração concluída! Ficheiro salvo como 'output.json'")
