import re
import json

# Caminho do ficheiro de entrada
with open("dicionario_formatado.txt", encoding="utf-8") as file:
    texto = file.read()

def criar_json(conteudo):
    dicionario = {}
    letra_atual = ""

    # Expressões regulares
    padrao_palavra = re.compile(r"^(.*?):")
    padrao_tipo = re.compile(r",\s*(\w+)\s*\.")
    padrao_plural = re.compile(r"\bpl\b")
    padrao_notas = re.compile(r"Notas\s*:\s*(.*?)\s*(?=Em espanhol|Em inglês|$)")
    padrao_espanhol = re.compile(r"Em espanhol\s*:\s*(.*?)\s*(?=Em inglês|$)")
    padrao_ingles = re.compile(r"Em inglês\s*:\s*(.*)")
    padrao_sinonimo = re.compile(r"\b(Sin\.|Sin\s+\.)", re.IGNORECASE)
    padrao_ver_sin = re.compile(r"\b(Ver\s+sin\.|Ver\s+sin\s+\.)", re.IGNORECASE)
    padrao_remissiva = re.compile(r"\bVer\s(?!sin)(.*?)(?=(Nota|Notas|Em espanhol|Em inglês|$))", re.IGNORECASE)
    padrao_expandida = re.compile(r"⇒\s*(.*?)(?=(Nota|Notas|Sin\.|Ver|Em espanhol|Em inglês|$))", re.IGNORECASE)

    linhas = conteudo.strip().split("\n")

    for linha in linhas:
        if linha.strip() == "":
            continue

        if len(linha.strip()) == 1 and linha.isalpha():
            letra_atual = linha.strip().upper()
            dicionario[letra_atual] = {}
            continue

        palavra_match = padrao_palavra.search(linha)
        if palavra_match:
            palavra = palavra_match.group(1).strip()
            detalhes = linha[palavra_match.end():].strip()

            tipo_match = padrao_tipo.search(detalhes)
            tipo = tipo_match.group(1).strip() if tipo_match else ""

            plural_match = padrao_plural.search(detalhes)
            numero = "plural" if plural_match else ""

            notas_match = padrao_notas.search(detalhes)
            notas = notas_match.group(1).strip() if notas_match else ""

            espanhol_match = padrao_espanhol.search(detalhes)
            espanhol = espanhol_match.group(1).strip() if espanhol_match else ""

            ingles_match = padrao_ingles.search(detalhes)
            ingles = ingles_match.group(1).strip() if ingles_match else ""

            sinônimo = ""
            inicio_desc = 0

            sinonimo_match = padrao_sinonimo.search(detalhes)
            ver_sin_match = padrao_ver_sin.search(detalhes)

            if sinonimo_match:
                sinônimo = sinonimo_match.group(1).strip()
                inicio_desc = sinonimo_match.end()
            elif ver_sin_match:
                sinônimo = ver_sin_match.group(1).strip()
                inicio_desc = ver_sin_match.end()
            else:
                inicio_desc = max(
                    tipo_match.end() if tipo_match else 0,
                    plural_match.end() if plural_match else 0
                )

            # Capturar descrição a partir do marcador "Sin." ou "Ver sin."
            descricao_temp = detalhes[inicio_desc:].strip()
            fim_desc_match = re.search(r"(Notas\s*:|Em espanhol\s*:|Em inglês\s*:|$)", descricao_temp)
            fim_desc = fim_desc_match.start() if fim_desc_match else len(descricao_temp)
            descricao = descricao_temp[:fim_desc].strip()

            # Limpeza extra (remover remissivas que possam ficar no meio da descrição)
            descricao = re.sub(padrao_remissiva, "", descricao)

            if descricao.startswith("."):
                descricao = descricao[1:].strip()

            expandida_match = padrao_expandida.search(detalhes)
            expandida = expandida_match.group(1).strip() if expandida_match else ""
            if expandida:
                descricao = ""

            remissiva_match = padrao_remissiva.search(detalhes)
            remissiva = remissiva_match.group(1).strip() if remissiva_match else ""

            dicionario[letra_atual][palavra] = {
                "tipo": tipo,
                "número": numero,
                "descrição": descricao,
                "notas": notas,
                "espanhol": espanhol,
                "inglês": ingles,
                "sinônimo": sinônimo,
                "remissiva": remissiva,
                "expandida": expandida
            }

    return dicionario

# Gerar o glossário e guardar como JSON
dicionario_json = criar_json(texto)

with open("glossario.json", "w", encoding="utf-8") as f_out:
    json.dump(dicionario_json, f_out, ensure_ascii=False, indent=4)
