import fitz  # PyMuPDF

# =================================================================================================

def extrair_dicionario_formatado(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    with open(output_path, "w", encoding="utf-8") as out_file:
        letra_atual = ""
        letras_escritas = set()
        palavra_atual = ""
        significado = ""
        cor_anterior = None  # Rastrear a cor da última palavra

        for page_num in range(20, 80):  # Páginas internas 21 a 79
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            linha_index = 0  # Rastreamento de linhas para ignorar cabeçalhos
            for block in blocks:
                if "lines" not in block:
                    continue

                for line in block["lines"]:
                    linha_index += 1
                    for span in line["spans"]:
                        texto = span["text"].strip()
                        cor = span["color"]

                        if not texto:
                            continue

                        # Ignorar cabeçalhos e texto irrelevante
                        if linha_index == 1 and page_num == 20:  # Ignora a primeira linha da página 21
                            continue
                        if texto.isdigit() and len(texto) <= 3:
                            continue
                        if len(texto) == 1 and texto.isalpha():
                            continue
                        if texto.lower() in ["onitoramento", "valiação", "lossário", "emático"]:
                            continue
                        if cor == 16777215: # Ignorar palavras na cor branca
                            continue
                        
                        # Detectar continuidade ou nova palavra com base na cor
                        if cor == 8470328:  
                            if cor_anterior == 8470328:
                                palavra_atual += " " + texto
                            else:
                                if palavra_atual:  
                                    entrada = f"{palavra_atual.strip()}: {significado.strip()}"
                                    if palavra_atual[0].upper() != letra_atual:
                                        letra_atual = palavra_atual[0].upper()
                                        if letra_atual not in letras_escritas:
                                            out_file.write(f"\n{letra_atual}\n\n")
                                            letras_escritas.add(letra_atual)
                                    out_file.write(entrada + "\n\n")
                                palavra_atual = texto
                                significado = ""
                        else:
                            significado += texto + " "

                        # Atualizar a cor anterior
                        cor_anterior = cor

        if palavra_atual and significado:
            entrada = f"{palavra_atual.strip()}: {significado.strip()}"
            if palavra_atual[0].upper() != letra_atual and palavra_atual[0].upper() not in letras_escritas:
                out_file.write(f"\n{palavra_atual[0].upper()}\n\n")
                letras_escritas.add(palavra_atual[0].upper())
            out_file.write(entrada + "\n\n")

    print("Dicionário extraído com sucesso.")
    return output_path


if __name__ == "__main__":
    pdf_path = "m_glossario-tematico-monitoramento-e-avaliacao.pdf"
    output_path = "dicionario_formatado.txt"
    extrair_dicionario_formatado(pdf_path, output_path)

# ===========================================================================
# Função para ver as cores utilizadas no PDF

def ver_cores_no_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(20, 79):  # páginas 21 a 79
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    texto = span["text"].strip()
                    cor = span["color"]
                    if texto:
                        print(f"[pág. {page_num+1}] Texto: \"{texto}\" | Cor: {cor}")
    doc.close()


if __name__ == "__main__":
    pdf_path = "m_glossario-tematico-monitoramento-e-avaliacao.pdf"
    ver_cores_no_pdf(pdf_path)
