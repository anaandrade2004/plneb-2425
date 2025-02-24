# Dicionário de Conceitos Médicos

Este projeto tem como objetivo processar um arquivo de texto contendo um dicionário médico, identificar os conceitos e suas respectivas descrições, e gerar um arquivo HTML formatado para exibição.

## Descrição

O código realiza as seguintes etapas:

1. **Leitura do Arquivo:**
   - Abre o arquivo `dicionario_medico.txt` localizado em `../plneb-2425/data/` com codificação UTF-8.

2. **Processamento do Texto:**
   - **Marcação de Conceitos:**  
     Utiliza a expressão regular `\n\n(?!\f)` para identificar os limites dos conceitos.  
     **Explicação da Expressão `\n\n(?!\f)`:**  
     - **`\n\n`:** Procura duas novas linhas seguidas.  
     - **`(?!\f)`:** Garante que essas duas novas linhas **não** sejam imediatamente seguidas por uma quebra de página (`\f`).  
     Ou seja, se encontrar a sequência `\n\n\f`, isso indica que a definição continua (é apenas uma quebra de página) e, por isso, não insere o marcador `@` para um novo conceito.
     
   - **Remoção de Quebra de Página:**  
     Remove todos os tokens de quebra de página (`\f`) do texto.

3. **Extração e Limpeza dos Conceitos:**
   - Utiliza uma expressão regular para extrair os conceitos e suas descrições, onde cada conceito é marcado pelo símbolo `@`.
   - A função `limpa_descricao` remove espaços desnecessários e substitui as quebras de linha por espaços para formatar corretamente a descrição.

4. **Geração do Arquivo HTML:**
   - Constrói uma página HTML que exibe os conceitos e suas descrições de forma organizada.
   - O HTML é salvo no arquivo `dicionario_medico.html`.