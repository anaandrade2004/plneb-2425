import re
import json
from collections import defaultdict

def processar_documento(texto):
    dicionario = defaultdict(dict)
    letra_atual = None
    num_conceito_atual = None
    em_traducao_ar = False
    em_traducao_outra = False
    lingua_atual = None
    buffer_traducao = []

    linhas = texto.split('\n')
    i = 0
    n = len(linhas)

    while i < n:
        linha = linhas[i].strip()

        if re.match(r'^[A-ZÀ-Ý]\s*$', linha):
            finalizar_traducoes_pendentes(dicionario, letra_atual, num_conceito_atual,
                                          em_traducao_ar, em_traducao_outra, lingua_atual, buffer_traducao)
            em_traducao_ar = False
            em_traducao_outra = False
            lingua_atual = None
            buffer_traducao = []
            letra_atual = linha.strip().lower()
            i += 1
            continue

        if not letra_atual:
            i += 1
            continue

        match_conceito = re.match(r'^(\d+)\s+([^\t\n]+?)\s+(n\s*(?:m|f|m\spl|f\spl|m,\sf|m\/f)?|adj|v\s*(?:tr|intr|tr\/intr))\b', linha)
        if match_conceito:
            finalizar_traducoes_pendentes(dicionario, letra_atual, num_conceito_atual,
                                          em_traducao_ar, em_traducao_outra, lingua_atual, buffer_traducao)
            em_traducao_ar = False
            em_traducao_outra = False
            lingua_atual = None
            buffer_traducao = []
            num_conceito_atual = match_conceito.group(1)
            designacao = match_conceito.group(2)
            categoria = match_conceito.group(3)

            categoria_map = {
                'n': 'n (nom)',
                'n m': 'n m (nom masculí)',
                'n f': 'n f (nom femení)',
                'n m pl': 'n m pl (nom masculí plural)',
                'n f pl': 'n f pl (nom femení plural)',
                'n m, f': 'n m, f (nom masculí i femení)',
                'n m/f': 'n m/f (nom masculí o femení)',
                'adj': 'adj (adjectiu)',
                'v tr': 'v tr (verb transitiu)',
                'v intr': 'v intr (verb intransitiu)',
                'v tr/intr': 'v tr/intr (verb transitiu o intransitiu)'
            }

            dicionario[letra_atual][num_conceito_atual] = {
                "designação": designacao,
                "categoria lexical da designação": categoria_map.get(categoria, categoria),
                "complementos designação": {
                    "siglas": [],
                    "sinónimos absolutos": "",
                    "sinónimos complementares": [],
                    "denominação comercial": "",
                    "consultar outra entrada": ""
                },
                "traduções": {},
                "códigos alternativos": {
                    "símbolo": "",
                    "nome científico": "",
                    "número CAS": ""
                },
                "áreas temáticas": {
                    "área": "",
                    "descrição": ""
                },
                "notas": []
            }
            i += 1
            continue

        if not num_conceito_atual:
            i += 1
            continue

        if em_traducao_ar:
            if nova_secao(linha):
                finalizar_traducao_arabe(dicionario, letra_atual, num_conceito_atual, buffer_traducao)
                em_traducao_ar = False
                buffer_traducao = []
                continue
            else:
                buffer_traducao.append(linhas[i].rstrip())
                i += 1
                continue

        if em_traducao_outra:
            if nova_secao(linha):
                finalizar_outra_traducao(dicionario, letra_atual, num_conceito_atual, lingua_atual, buffer_traducao)
                em_traducao_outra = False
                lingua_atual = None
                buffer_traducao = []
                continue
            else:
                buffer_traducao.append(linhas[i].rstrip())
                i += 1
                continue

        match_ar = re.match(r'^ar\t?(.*)', linha)
        if match_ar:
            em_traducao_ar = True
            texto = match_ar.group(1).strip()
            if texto:
                buffer_traducao.append(texto)
            i += 1
            continue

        match_lang = re.match(r'^(oc|eu|gl|es|en|fr|pt|nl)\s*$', linha)
        if match_lang:
            em_traducao_outra = True
            lingua_atual = match_lang.group(1)
            i += 1
            continue

        match_pt_var = re.match(r'^\[(PT|BR)\]\s*(.*)', linha)
        if match_pt_var:
            em_traducao_outra = True
            lingua_atual = f"[{match_pt_var.group(1)}]pt"
            texto = match_pt_var.group(2).strip()
            if texto:
                buffer_traducao.append(texto)
            i += 1
            continue

        match_cas = re.match(r'^CAS\t(.+)', linha)
        if match_cas:
            dicionario[letra_atual][num_conceito_atual]["códigos alternativos"]["número CAS"] = match_cas.group(1).strip()
            i += 1
            continue

        match_area = re.match(r'^(CONCEPTES GENERALS|EPIDEMIOLOGIA|ETIOPATOGÈNIA|DIAGNÒSTIC|CLÍNICA|PREVENCIÓ|TRACTAMENT|PRINCIPIS ACTIUS|ENTORN SOCIAL)\.\s+(.+)', linha, re.IGNORECASE)
        if match_area:
            area = match_area.group(1).title()
            descricao = match_area.group(2)
            dicionario[letra_atual][num_conceito_atual]["áreas temáticas"]["área"] = area
            dicionario[letra_atual][num_conceito_atual]["áreas temáticas"]["descrição"] = descricao
            i += 1
            continue

        match_nota = re.match(r'^Nota:\s+(.+)', linha)
        if match_nota:
            nota = match_nota.group(1)
            dicionario[letra_atual][num_conceito_atual]["notas"].append(nota)
            i += 1
            continue

        match_sigla = re.match(r'^sigla\s+(.+)', linha)
        if match_sigla:
            siglas = [s.strip() for s in match_sigla.group(1).split(';')]
            dicionario[letra_atual][num_conceito_atual]["complementos designação"]["siglas"] = siglas
            i += 1
            continue

        match_sin = re.match(r'^sin\.\s+(.+)', linha)
        if match_sin:
            sinonimos = [s.strip() for s in match_sin.group(1).split(';')]
            if "sin. compl." in linha:
                dicionario[letra_atual][num_conceito_atual]["complementos designação"]["sinónimos complementares"] = sinonimos
            else:
                dicionario[letra_atual][num_conceito_atual]["complementos designação"]["sinónimos absolutos"] = sinonimos[0] if sinonimos else ""
            i += 1
            continue

        match_veg = re.match(r'^veg\.\s+(.+)', linha)
        if match_veg:
            referencia = match_veg.group(1).strip()
            dicionario[letra_atual][num_conceito_atual]["complementos designação"]["consultar outra entrada"] = referencia
            i += 1
            continue

        if num_conceito_atual:
            if dicionario[letra_atual][num_conceito_atual]["notas"]:
                dicionario[letra_atual][num_conceito_atual]["notas"][-1] += "\n" + linha
            elif dicionario[letra_atual][num_conceito_atual]["áreas temáticas"]["descrição"]:
                dicionario[letra_atual][num_conceito_atual]["áreas temáticas"]["descrição"] += "\n" + linha

        i += 1

    finalizar_traducoes_pendentes(dicionario, letra_atual, num_conceito_atual,
                                  em_traducao_ar, em_traducao_outra, lingua_atual, buffer_traducao)
    return dicionario

def nova_secao(linha):
    return (re.match(r'^(oc|eu|gl|es|en|fr|pt|nl|ar|\[PT\]|\[BR\]|CAS|PRINCIPIS ACTIUS|Nota:|sigla|sin\.|veg\.|\d+\s+\w+)', linha) or
            re.match(r'^[A-ZÀ-Ý]\s*$', linha) or
            re.match(r'^(CONCEPTES GENERALS|EPIDEMIOLOGIA|ETIOPATOGÈNIA|DIAGNÒSTIC|CLÍNICA|PREVENCIÓ|TRACTAMENT|PRINCIPIS ACTIUS|ENTORN SOCIAL)\.', linha, re.IGNORECASE))

def finalizar_traducoes_pendentes(dicionario, letra, num_conceito, em_ar, em_outra, lingua, buffer):
    if em_ar and buffer:
        finalizar_traducao_arabe(dicionario, letra, num_conceito, buffer)
    if em_outra and buffer and lingua:
        finalizar_outra_traducao(dicionario, letra, num_conceito, lingua, buffer)

def finalizar_traducao_arabe(dicionario, letra, num_conceito, buffer):
    texto_ar = '\n'.join(buffer).strip()
    if texto_ar and letra and num_conceito:
        dicionario[letra][num_conceito]["traduções"]["àrab"] = texto_ar

def finalizar_outra_traducao(dicionario, letra, num_conceito, lingua, buffer):
    texto_trad = '\n'.join(buffer).strip()
    if not texto_trad or not letra or not num_conceito:
        return

    lang_map = {
        'oc': 'occità',
        'eu': 'basc',
        'gl': 'gallec',
        'es': 'castellà',
        'en': 'anglès',
        'fr': 'francès',
        'pt': 'portuguès',
        'nl': 'neerlandès',
        '[PT]pt': '[PT]portuguès de Portugal',
        '[BR]pt': '[BR]portuguès do Brasil'
    }

    chave = lang_map.get(lingua, lingua)

    if chave in dicionario[letra][num_conceito]["traduções"]:
        if isinstance(dicionario[letra][num_conceito]["traduções"][chave], list):
            dicionario[letra][num_conceito]["traduções"][chave].append(texto_trad)
        else:
            dicionario[letra][num_conceito]["traduções"][chave] = [
                dicionario[letra][num_conceito]["traduções"][chave],
                texto_trad
            ]
    else:
        dicionario[letra][num_conceito]["traduções"][chave] = texto_trad


# Carregar e processar o arquivo
with open('dicionario_limpo.txt', 'r', encoding='utf-8') as f:
    texto = f.read()

dicionario_final = processar_documento(texto)

# Salvar em JSON
with open('bd.json', 'w', encoding='utf-8') as f:
    json.dump(dicionario_final, f, ensure_ascii=False, indent=4)

print("Processamento concluído com sucesso!")
