# Atlas da Saúde - Web Scraper

## Visão Geral
Este projeto contém um web scraper desenvolvido em Python para extrair informações estruturadas sobre doenças do portal [Atlas da Saúde](https://www.atlasdasaude.pt). O scraper recolhe os dados de A-Z, organizando-os num formato JSON padronizado.

## Funcionalidades Principais

### `get_doenca_info(url_href)`
Função principal que extrai e estrutura os dados de uma página específica de doença:

1. **Recolha de Metadados**:
   - Extrai URL completo e data de publicação
   - Captura a nota informativa do artigo

2. **Estruturação de Conteúdo**:
   - Divide o texto em seções lógicas:
     - `descricao`: Introdução/conceito da doença
     - `causas`: Fatores que provocam a condição
     - `sintomas`: Lista itemizada de manifestações
     - `tratamento`: Abordagens terapêuticas
     - `artigos_relacionados`: Links com títulos

## Estrutura de Saída
Os dados são guardados em `doencas_final.json` com formato:
```json
{
  "Nome da Doença": {
    "url": "link-completo",
    "date": "data-de-publicação",
    "content": {
      "descricao": ["texto1", "texto2"],
      "causas": ["causa1", "causa2"],
      "sintomas": ["item1", "item2"],
      "tratamento": ["método1", "método2"],
      "artigos_relacionados": [{"titulo": "...", "url": "..."}]
    },
    "nota": "texto da nota"
  }
}
```
