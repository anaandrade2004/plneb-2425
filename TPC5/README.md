# Dicionário de Conceitos em Flask

Esta é uma aplicação web simples baseada em Flask que funciona como um dicionário de conceitos. Permite aos utilizadores navegar por uma lista de conceitos, ver as descrições detalhadas de cada um e adicionar novos conceitos à base de dados através de um pedido POST.

### Funcionalidades
1. **Lista de Conceitos**:
   - Exibe todos os conceitos armazenados no ficheiro `conceitos_.json`.
   - Cada conceito é um link clicável que redireciona para a sua descrição detalhada.

2. **Detalhes de um Conceito**:
   - Mostra a descrição de um conceito específico quando este é clicado.
   - Inclui um link para voltar à lista de conceitos.

3. **Adicionar Novo Conceito**:
   - Permite aos utilizadores adicionar um novo conceito à base de dados através de um pedido POST.
   - O novo conceito é guardado no ficheiro `conceitos_.json`.

4. **Endpoint da API**:
   - Disponibiliza um endpoint JSON (`/api/conceitos`) para obter toda a base de dados de conceitos.

### Como Funciona
- A aplicação utiliza o Flask para gerir as rotas e renderizar os templates HTML.
- Os conceitos são armazenados num ficheiro JSON (`conceitos_.json`), que funciona como a base de dados.
- A aplicação lê e atualiza dinamicamente o ficheiro JSON.

### Estrutura do Código
- **`aula5.py`**:
  - O ficheiro principal da aplicação Flask.
  - Define as rotas para:
    - `/`: Uma página simples com "Hello, World!".
    - `/conceitos`: Exibe a lista de conceitos.
    - `/conceitos/<designacao>`: Mostra a descrição de um conceito específico.
    - `/api/conceitos`: Retorna toda a base de dados em formato JSON.
    - `/conceitos` (POST): Adiciona um novo conceito à base de dados.

- **`conceitos_.json`**:
  - Um ficheiro JSON que contém as designações e as suas descrições.
  - Exemplo de estrutura:
    ```json
    {
        "desiganção": "vida",
        "descrição": "A vida é bela ..."
    }
    ```

- **Templates**:
  - `layout.html`: O template base para todas as páginas.
  - `conceitos.html`: Renderiza a lista de conceitos.
  - `conceito.html`: Renderiza os detalhes de um conceito específico.

