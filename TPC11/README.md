# Web Scraper para Revista SPMI

Este script Python foi desenvolvido para extrair informações de artigos científicos da revista SPMI (https://revista.spmi.pt) e armazená-las em formato JSON.

## Funcionalidades

- Extrai metadados completos de todas as edições e artigos da revista
- Coleta informações como:
  - Títulos completos das edições
  - Autores dos artigos
  - Resumos (abstracts)
  - DOIs
  - Palavras-chave
- Organiza os dados por edição e seção
- Gera um arquivo JSON com timestamp para evitar sobreposição

## Requisitos

- Python 3.x
- Bibliotecas:
  - `requests`
  - `beautifulsoup4`
  - `json` (incluída na biblioteca padrão)
  - `datetime` (incluída na biblioteca padrão)


## Estrutura do JSON Gerado

O arquivo de saída contém uma lista de edições, cada uma com:
```json
{
  "titulo_arquivo": "Título resumido",
  "titulo_completo": "Título completo da edição",
  "url_edicao": "URL da edição",
  "secoes": [
    {
      "nome_secao": "Nome da seção",
      "artigos": [
        {
          "titulo": "Título do artigo",
          "autores": "Lista de autores",
          "url": "URL do artigo",
          "resumo": "Texto do resumo",
          "doi": "DOI do artigo",
          "palavras_chave": "Palavras-chave separadas por vírgulas"
        }
      ]
    }
  ]
}
```

## Personalização

- Para alterar o número de páginas do arquivo a serem processadas, modifique a variável `total_paginas` na função `main()`
- O script já trata casos onde informações podem estar faltando, preenchendo com valores padrão

## Saída no Terminal

Durante a execução, o script exibe:
- O título completo de cada edição sendo processada
- As seções encontradas e quantidade de artigos
- Para cada artigo:
  - Título
  - Autores
  - URL
  - Resumo
  - DOI
  - Palavras-chave
