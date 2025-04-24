import re
import json

def cleaner_html():
    ficheiro_entrada = "glossario.html"
    ficheiro_saida = "glossario_limpo.html"

    with open(ficheiro_entrada, "r", encoding="utf-8") as f:
        conteudo = f.read()
    conteudo_limpo = re.sub(r'<text[^>]*>', '', conteudo)
    conteudo_limpo = re.sub(r'</text>', '', conteudo_limpo)

    with open(ficheiro_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_limpo)

    print(f"Conteúdo limpo guardado em '{ficheiro_saida}' com sucesso!")

#Marcas tipográficas##
def marcas_retiradas_html():
   with open("glossario_limpo.html", encoding="utf-8") as f:
    linhas = f.read().splitlines()

    resultado = {}
    i = 0

    while i < len(linhas):
        linha = linhas[i].strip()

        if i + 1 < len(linhas) and re.match(r'<i>s\.[fm]\.[\s]*</i>', linhas[i + 1].strip()):
            termo = linha
            i += 2
            bloco = []
            while i < len(linhas):
                if  i + 1 < len(linhas) and re.match(r'<i>s\.[fm]\.[\s]*</i>', linhas[i + 1].strip()):
                    break
                bloco.append(linhas[i].strip())
                i += 1
            texto_bloco = ' '.join(bloco)
            m_esp = re.search(r'\[esp\]', texto_bloco)
            inicio = m_esp.end() if m_esp else 0
            m_fim = re.search(r'(Inf\.|“)', texto_bloco[inicio:])
            fim = inicio + m_fim.start() if m_fim else len(texto_bloco)
            definicao = texto_bloco[inicio:fim]
            print (definicao)
            definicao = re.sub(r'\s*<i>\s*$', '', definicao)
            definicao = re.sub(r'(?m)^\s*Sigla:\s*<i>\s*[A-Z]+\s*</i>\s*', '', definicao)
            definicao = re.sub(r'(?m)Ver este termo.*$', '', definicao)
            definicao = re.sub(r'</i>\s*<i>', ' ', definicao)
            marcas = re.findall(r'<i>([^<]+)</i>', definicao)
            marcas = [re.sub(r'\s+', ' ', m).strip() for m in marcas]
            marcas = [m for m in marcas
                    if m
                    and not re.search(r'(\.{3}|…|&#34;)', m)
                    and len(m.split()) <= 5
                    and not re.fullmatch(r'\W+', m)]

            resultado[termo] = {
                "Marcas Tipográficas": marcas
            }
        else:
            i += 1
    with open("glossario_marcas.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)

    print(f"Exportado com {len(resultado)} entradas válidas.")

## Restantes informações ##
def rest():
    with open("glossario.txt", encoding="utf-8") as f:
        texto = f.read().replace('\r\n', '\n').replace('\f', '\n')

    header_pat = re.compile(r'^(?P<conceito>.+?)\s+(?P<ref>s\.[fm]\.)\s*$', flags=re.MULTILINE)
    headers = list(header_pat.finditer(texto))
    resultado = {}
    for idx, h in enumerate(headers):
        conceito = h.group('conceito').strip()
        ref_gram  = h.group('ref')

        body_start = texto.find('\n', h.end()) + 1

        body_end = headers[idx+1].start() if idx+1 < len(headers) else len(texto)
        body = texto[body_start:body_end].strip()

        sin_match = re.search(r'Ver este termo\s+(.+?)\.', body)
        sinonimos = sin_match.group(1).strip() if sin_match else ""
        body = re.sub(r'^Ver este termo\s+.+?\.\s*', '', body, flags=re.MULTILINE)

        ab_m = re.search(r'[“"’]\s*(?:\.\.\.|\.\s\.\s\.|…)\s*(.*?)["”’]?\s*\(([\d,\s]+)\)', body, flags=re.DOTALL)
        
        if ab_m:
            abonacao = re.sub(r'\s+', ' ', ab_m.group(1).strip())
            num_id    = ab_m.group(2).replace(' ', '') 
        else:
            abonacao = ""
            num_id    = ""

        info_m = re.search(r'Inf\.\s*(Encl|encicl|ecicl)\.\s*:(.+)', body, flags=re.DOTALL) 
        if info_m:
            raw_info = info_m.group(2).strip() 
            info = raw_info.split('“', 1)[0].strip()
        else:
            info = ""

        trad_pat = re.compile(
            r'(?P<en>.+?)\s*\[ing\];\s*(?P<es>[\s\S]+?)\s*(?:\[esp\]|\[es)', 
            flags=re.MULTILINE
        )
        trad_m = trad_pat.search(body)
        if trad_m:
            ingles   = re.sub(r'\s+', ' ', trad_m.group('en')).strip().rstrip('.') 
            espanhol = re.sub(r'\s+', ' ', trad_m.group('es')).strip().rstrip('.')
        else:
            ingles = espanhol = ""

        defin = body
        defin = trad_pat.sub('', defin)
        defin = re.sub(r'Sigla:\s*\S+', '', defin)

        defin = re.sub(r'Inf\.\s*(Encl|encicl|ecicl)\.\s*:.*', '', defin, flags=re.DOTALL)

        defin = re.sub(r'[“"’]\s*(?:\.\.\.|\.\s\.\s\.|…)\s*(.*?)["”’]?\s*\(([\d,\s]+)\)', '', defin, flags=re.DOTALL)
        
        if defin.strip().lower().startswith("ver este termo"):
            sinonimos = re.sub(r'^ver este termo\s+', '', defin.strip(), flags=re.IGNORECASE)
            defin = "" 
        defin = re.sub(r'\s+', ' ', defin).strip()

        sigla_m = re.search(r'Sigla:\s*(\S+)', body)
        sigla = sigla_m.group(1).strip() if sigla_m else ""

        def clean(text):
            return re.sub(r'\s+', ' ', text.strip())
        
        ingles     = clean(ingles)
        espanhol   = clean(espanhol)
        defin      = clean(defin)
        info       = clean(info)
        abonacao   = clean(abonacao)
        sinonimos  = clean(sinonimos)
        num_id     = clean(num_id)

        resultado[conceito] = {
        
            "referencia_gramatical": ref_gram,
            "equivalencias": {"ingles": ingles, "espanhol": espanhol},
            "Sigla": sigla,
            "Definicao": defin,
            "Informacao_enciclopedica": info,
            "Abonacao": abonacao,
            "Sinonimos": sinonimos,
            "Numero_identificacao": num_id,   
        }

    with open("glossario_convertido.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)

    print(f"Glossário convertido com sucesso! Total de entradas: {len(resultado)}")

def join():
    with open("glossario_convertido.json", "r", encoding="utf-8") as f:
        resultado = json.load(f)

    with open("glossario_marcas.json", "r", encoding="utf-8") as f:
        marcas_dict = json.load(f)

    for conceito in resultado:
        marcas = marcas_dict.get(conceito, {}).get("Marcas Tipográficas", [])
        resultado[conceito]["Marcas_Tipograficas"] = marcas

    with open("glossario_completo.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)

    print(f"Glossário final com marcas incluídas! Total de entradas: {len(resultado)}")


cleaner_html()
marcas_retiradas_html()
rest()  
join()

