# Trabalho Prático 1 - Processamento de Linguagem Natural (PLN) em Engenharia Biomédica

## Objetivo
O objetivo deste trabalho é aplicar técnicas de Processamento de Linguagem Natural (PLN) para extrair informações relevantes de documentos em formato PDF, especialmente focados em terminologia biomédica relacionada à COVID-19 e neologismos em saúde. A informação extraída deve ser estruturada e armazenada em um ficheiro JSON para uso futuro.

## Tarefas Principais
1. **Análise de PDFs**: Selecionar informações relevantes de documentos fornecidos, incluindo os obrigatórios:
   - `diccionari-multilinguee-de-la-covid-19.pdf`
   - `glossario_neologismos_saude.pdf`
   - `m_glossario-tematico-monitoramento-e-avaliacao.pdf`

2. **Definição de Estrutura**: Criar uma sintaxe para organizar os dados extraídos.

3. **Conversão e Limpeza**: Converter os PDFs para um formato manipulável, realizar limpeza de dados e destacar informações úteis.

4. **Extração e Armazenamento**: Extrair as informações relevantes e guardá-las num ficheiro JSON.


## Como Começar
1. Clonar o repositório da disciplina para acessar os PDFs.
2. Análise dos documentos e definação da estrutura de dados.
3. Utilização da biblioteca Python `PyPDF2` para extrair o conteúdo do PDF.
4. Processar e limpar os dados antes de guardá-los em JSON.
