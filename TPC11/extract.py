import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# URL base
BASE_URL = 'https://revista.spmi.pt'

# Lista para armazenar todos os dados antes de exportar para JSON
dados_coletados = []

# Função 1 - Extrai os links das edições de uma página de arquivo
def get_issue_links(page_number):
    if page_number == 1:
        archive_url = f'{BASE_URL}/index.php/rpmi/issue/archive'
    else:
        archive_url = f'{BASE_URL}/index.php/rpmi/issue/archive/{page_number}'

    print(f'\nA aceder à página de arquivos: {archive_url}')
    response = requests.get(archive_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    div_content = soup.find_all("div", class_="obj_issue_summary")

    for div in div_content:
        titulo_tag = div.find("a", class_='title')
        if titulo_tag:
            titulo_arquivo = titulo_tag.get_text(strip=True)
            url_href = titulo_tag['href']
            url_completo = url_href if url_href.startswith('http') else BASE_URL + url_href

            links.append((titulo_arquivo, url_completo))

    return links

# Função para extrair o título completo da edição
def get_issue_title(issue_url):
    response = requests.get(issue_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('h1')
    return title_tag.get_text(strip=True) if title_tag else "Título não disponível"

# Função para extrair info da página do artigo
def get_artigo_detalhes(artigo_url):
    response = requests.get(artigo_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Abstract (Resumo)
    abstract_tag = soup.find('section', class_='item abstract')
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else "Resumo não disponível"

    # DOI
    doi_tag = soup.find('section', class_='item doi')
    doi = doi_tag.get_text(strip=True) if doi_tag else "DOI não disponível"

    # Palavras-chave
    keywords = "Palavras-chave não disponíveis"
    keywords_tag = soup.find('section', class_='item keywords')
    if keywords_tag:
        # Obter o texto e limpar
        keywords_text = keywords_tag.get_text(strip=True)
        
        # Remover rótulos
        for prefix in ['Keywords:', 'Palavras-chave:', 'Key words:', 'Palavras chave:']:
            keywords_text = keywords_text.replace(prefix, '')
        
        # Normalizar espaços e quebras de linha
        keywords_text = ' '.join(keywords_text.split())
        
        # Separar por vírgulas (tratando múltiplos formatos)
        if ',' in keywords_text:
            # Já está separado por vírgulas - apenas limpar
            keywords_list = [k.strip() for k in keywords_text.split(',')]
        elif ';' in keywords_text:
            # Separado por ponto-e-vírgula
            keywords_list = [k.strip() for k in keywords_text.split(';')]
        else:
            # Tentar separar por espaços quando houver palavras compostas
            keywords_list = [k.strip() for k in keywords_text.split('  ') if k.strip()]
            if len(keywords_list) <= 1:  # Se não separou corretamente
                keywords_list = [keywords_text]
        
        # Juntar com vírgulas e remover espaços extras
        keywords = ', '.join(filter(None, keywords_list)).strip(' ,')
    return abstract, doi, keywords

# Função 2 - Visita a página da edição e extrai info + artigos
def get_artigos_info(issue_title, issue_url):
    # Extrair o título completo da página da edição
    full_issue_title = get_issue_title(issue_url)
    
    print(f'\nA visitar a edição: {issue_title}')
    print(f'Título: {full_issue_title}')
    print(f'URL: {issue_url}')

    response = requests.get(issue_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    sections = soup.find_all('div', class_='section')
    
    issue_data = {
        "titulo_arquivo": issue_title,
        "titulo_completo": full_issue_title,
        "url_edicao": issue_url,
        "secoes": []
    }

    for section in sections:
        tipo = section.find("h2")
        section_name = tipo.get_text(strip=True) if tipo else "Secção desconhecida"

        artigos = section.find_all('div', class_='obj_article_summary')
        num_artigos = len(artigos)
        print(f'\n  Secção: {section_name} — {num_artigos} artigo{"s" if num_artigos != 1 else ""}\n')

        section_data = {
            "nome_secao": section_name,
            "artigos": []
        }

        for artigo in artigos:
            artigo_data = {
                "titulo": "Título não disponível",
                "autores": "Autores não disponíveis",
                "url": "Link não disponível",
                "resumo": "",
                "doi": "",
                "palavras_chave": ""
            }

            # Procurar título
            titulo_tag = artigo.find('h3', class_='title')
            titulo_link = titulo_tag.find('a') if titulo_tag else None

            if titulo_link:
                artigo_data["titulo"] = titulo_link.get_text(strip=True)
                url_href = titulo_link['href']
                artigo_data["url"] = url_href if url_href.startswith('http') else BASE_URL + url_href

            # Procurar autores
            autores_tag = artigo.find('div', class_='authors')
            if autores_tag:
                artigo_data["autores"] = autores_tag.get_text(strip=True)
            else:
                next_tag = titulo_tag.find_next_sibling()
                while next_tag:
                    if next_tag.name in ['p', 'div'] and not next_tag.get('class'):
                        artigo_data["autores"] = next_tag.get_text(strip=True)
                        break
                    next_tag = next_tag.find_next_sibling()

            # Aceder à página do artigo para mais detalhes
            if artigo_data["url"] != "Link não disponível":
                abstract, doi, keywords = get_artigo_detalhes(artigo_data["url"])
                artigo_data["resumo"] = abstract
                artigo_data["doi"] = doi
                artigo_data["palavras_chave"] = keywords

                # Print dos detalhes
                print(f'    Título do artigo: {artigo_data["titulo"]}')
                print(f'    Autores: {artigo_data["autores"]}')
                print(f'    Link do artigo: {artigo_data["url"]}')
                print(f'    Resumo: {artigo_data["resumo"]}')
                print(f'    {artigo_data["doi"]}')
                print(f'    Palavras-chave: {artigo_data["palavras_chave"]}\n')

            section_data["artigos"].append(artigo_data)

        issue_data["secoes"].append(section_data)

    dados_coletados.append(issue_data)

# Função para guardar os dados em JSON
def save_to_json():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"revista_spmi_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dados_coletados, f, ensure_ascii=False, indent=2)
    
    print(f"\nDados guardados em {filename}")

# Função principal
def main():
    total_paginas = 6  # Número total de páginas do arquivo

    for page_number in range(1, total_paginas + 1):
        issue_links = get_issue_links(page_number)

        for title, url in issue_links:
            get_artigos_info(title, url)

    save_to_json()

# Executa
if __name__ == "__main__":
    main()