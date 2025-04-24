import fitz  # PyMuPDF
import sys

def extrair_dicionario(pdf_path, output_path):
    """
    Extrai texto de dicionário em 2 colunas mantendo:
    - Ordem correta de leitura (esquerda > direita > página seguinte)
    - Formatação original
    - Divisão por páginas e colunas
    - Número da página lógica (página 1 = terceira página física)
    - Ignora numeração nas 2 primeiras páginas (capa/prefácio)
    """
    try:
        doc = fitz.open(pdf_path)
        
        with open(output_path, "w", encoding="utf-8") as out_file:
            
            for page_num, page in enumerate(doc, start=1):
                # Pular as 2 primeiras páginas (sem numeração)
                if page_num <= 2:
                    continue
                
                # Número lógico (página 1 = terceira página física) - numeração só começa a partir da segunda página
                pagina_logica = page_num - 2
                out_file.write(f"\n=== PÁGINA {pagina_logica} ===\n\n")
                
                # Configuração da página
                width = page.rect.width
                height = page.rect.height
                mid_x = width / 2  # Ponto médio entre as colunas
                
                # Dicionário para armazenar linhas por coluna
                colunas = {
                    "esquerda": [],
                    "direita": []
                }
                
                # Extrair todos os elementos de texto com coordenadas
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" in block:  # Ignorar imagens/gráficos
                        # Calcular centro do bloco
                        x_center = (block["bbox"][0] + block["bbox"][2]) / 2
                        
                        # Determinar coluna
                        coluna = "esquerda" if x_center < mid_x else "direita"
                        
                        # Extrair linhas mantendo quebras naturais
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                line_text += span["text"]
                            colunas[coluna].append((block["bbox"][1], line_text))
                
                # Função para ordenar e formatar uma coluna
                def processar_coluna(itens):
                    # Ordenar por posição vertical (Y)
                    itens.sort(key=lambda x: x[0])
                    # Juntar linhas mantendo quebras naturais
                    return "\n".join([item[1] for item in itens])
                
                # Processar colunas
                texto_esquerda = processar_coluna(colunas["esquerda"])
                texto_direita = processar_coluna(colunas["direita"])
                
                # Escrever no arquivo com formatação limpa
                out_file.write(texto_esquerda + "\n")
                out_file.write(texto_direita + "\n")
                
        return True
    
    except Exception as e:
        print(f"Erro crítico: {str(e)}")
        return False

if __name__ == "__main__":
    input_pdf = "../data/diccionari-multilinguee-de-la-covid-19.pdf"
    output_txt = "dicionario_extraido.txt"
    
    if extrair_dicionario(input_pdf, output_txt):
        print(f"Extração concluída! Arquivo salvo em: {output_txt}")
        print("Dica: Verifique o arquivo em um editor de texto com:")
        print("- Codificação UTF-8")
        print("- Fonte monoespaçada (para melhor visualização)")
    else:
        print("A extração falhou. Possíveis causas:")
        print("- Arquivo PDF corrompido ou protegido")
        print("- Layout complexo não suportado")
        print("- Permissões de arquivo insuficientes")