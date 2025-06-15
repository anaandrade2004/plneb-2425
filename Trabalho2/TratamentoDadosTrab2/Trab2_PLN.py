import json
from collections import defaultdict, OrderedDict
import re

##Converter o bd.json
def limpar_texto(texto):
    if isinstance(texto, str):
        return re.sub(r"\s+", " ", texto.replace("\n", " ")).strip()
    return texto

def garantir_string(valor):
    if isinstance(valor, list):
        return limpar_texto(" ".join(map(str, valor)))
    return limpar_texto(str(valor)) if valor is not None else ""

def limpar_categoria(texto):
    return re.sub(r"\s*\(.*?\)", "", texto).strip()

def normalizar_entrada(dados):
    categoria_original = dados.get("categoria lexical da designação", "")
    categoria_limpa = limpar_categoria(categoria_original)

    linguas_padrao = [
        "occità", "basc", "gallec", "castellà", "anglès",
        "francès", "[PT]portuguès de Portugal", "[BR]portuguès do Brasil",
        "neerlandès", "àrab"
    ]

    traducoes_completas = {
        lingua: garantir_string(dados.get("traduções", {}).get(lingua, ""))
        for lingua in linguas_padrao
    }

    descricao = garantir_string(dados.get("áreas temáticas", {}).get("descrição", ""))

    sinonimos_complementares = [
        garantir_string(s) for s in dados.get("complementos designação", {}).get("sinónimos complementares", [])
    ]

    notas_raw = dados.get("notas", {})
    if isinstance(notas_raw, dict):
        informacoes_notas = [garantir_string(n) for n in notas_raw.get("informacoes_notas", [])]
        marcas = [garantir_string(m) for m in notas_raw.get("Marcas_Tipograficas", [])]
        notas_dict = {
            "informacoes_notas": informacoes_notas,
            "Informacao_enciclopedica": garantir_string(notas_raw.get("Informacao_enciclopedica", "")),
            "Abonacao": garantir_string(notas_raw.get("Abonacao", "")),
            "Numero_identificacao": garantir_string(notas_raw.get("Numero_identificacao", "")),
            "Marcas_Tipograficas": marcas,
            "remissiva": garantir_string(notas_raw.get("remissiva", "")),
            "expandida": garantir_string(notas_raw.get("expandida", ""))
        }
    elif isinstance(notas_raw, list):
        notas_dict = {
            "informacoes_notas": [garantir_string(n) for n in notas_raw],
            "Informacao_enciclopedica": "",
            "Abonacao": "",
            "Numero_identificacao": "",
            "Marcas_Tipograficas": [],
            "remissiva": "",
            "expandida": ""
        }
    else:
        notas_dict = {
            "informacoes_notas": [],
            "Informacao_enciclopedica": "",
            "Abonacao": "",
            "Numero_identificacao": "",
            "Marcas_Tipograficas": [],
            "remissiva": "",
            "expandida": ""
        }

    return {
        "dicionario": "diccionari-multilinguee-de-la-covid-19",
        "categoria lexical da designação": categoria_limpa,
        "complementos designação": {
            "siglas": dados.get("complementos designação", {}).get("siglas", []),
            "sinónimos absolutos": garantir_string(dados.get("complementos designação", {}).get("sinónimos absolutos", "")),
            "sinónimos complementares": sinonimos_complementares,
            "denominação comercial": garantir_string(dados.get("complementos designação", {}).get("denominação comercial", "")),
            "consultar outra entrada": garantir_string(dados.get("complementos designação", {}).get("consultar outra entrada", ""))
        },
        "traduções": traducoes_completas,
        "códigos alternativos": {
            "símbolo": garantir_string(dados.get("códigos alternativos", {}).get("símbolo", "")),
            "nome científico": garantir_string(dados.get("códigos alternativos", {}).get("nome científico", "")),
            "número CAS": garantir_string(dados.get("códigos alternativos", {}).get("número CAS", ""))
        },
        "áreas temáticas": {
            "área": garantir_string(dados.get("áreas temáticas", {}).get("área", "")),
            "descrição": descricao
        },
        "notas": notas_dict
    }

def converter_bd_json(input_path, output_path):
    with open(input_path, encoding="utf-8") as f:
        bd_data = json.load(f)

    resultado = {}

    for secao in bd_data.values():
        for item in secao.values():
            termo = item.get("designação", "").strip()
            if not termo:
                continue
            letra = termo[0].upper()
            if letra not in resultado:
                resultado[letra] = {}
            resultado[letra][termo] = normalizar_entrada(item)

    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(resultado, f_out, ensure_ascii=False, indent=2)

# Exemplo de chamada
converter_bd_json("dicionarios/bd.json", "dicionarios/atualizados/bd_atualizado.json")

#Converter o glossario.json
def map_categoria(tipo, numero):
    tipo = (tipo or "").strip()
    numero = (numero or "").strip()

    if tipo == "fem" and numero == "":
        return "n f"
    elif tipo == "masc" and numero == "":
        return "n m"
    elif tipo == "fem" and numero == "plural":
        return "n f pl"
    elif tipo == "masc" and numero == "plural":
        return "n m pl"
    return ""

def normalizar_glossario_entrada(item):
    return {
        "dicionario": "m_glossario-tematico-monitoramento-e-avaliacao",
        "categoria lexical da designação": map_categoria(item.get("tipo", ""), item.get("número", "")),
        "complementos designação": {
            "siglas": [],
            "sinónimos absolutos": item.get("sinônimo", ""),
            "sinónimos complementares": [],
            "denominação comercial": "",
            "consultar outra entrada": ""
        },
        "traduções": {
            "occità": "",
            "basc": "",
            "gallec": "",
            "castellà": item.get("espanhol", ""),
            "anglès": item.get("inglês", ""),
            "francès": "",
            "portuguès": "",
            "[PT]portuguès de Portugal": "",
            "[BR]portuguès del Brasil": "",
            "neerlandè": "",
            "àrab": ""
        },
        "códigos alternativos": {
            "símbolo": "",
            "nome científico": "",
            "número CAS": ""
        },
        "áreas temáticas": {
            "área": "",
            "descrição": item.get("descrição", "")
        },
        "notas": {
            "informacoes_notas": item.get("notas", []),
            "Informacao_enciclopedica": "",
            "Abonacao": "",
            "Numero_identificacao": "",
            "Marcas_Tipograficas": [],
            "remissiva": item.get("remissiva", ""),
            "expandida": item.get("expandida", "")
        }
    }

def converter_glossario(input_path, output_path):
    with open(input_path, encoding="utf-8") as f:
        glossario = json.load(f)

    resultado = {}

    for letra, termos in glossario.items():
        letra_ajustada = letra.upper().strip()
        resultado[letra_ajustada] = {}
        for termo, dados in termos.items():
            termo_ajustado = termo.strip()
            resultado[letra_ajustada][termo_ajustado] = normalizar_glossario_entrada(dados)

    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(resultado, f_out, ensure_ascii=False, indent=2)


# Exemplo de uso:
converter_glossario("dicionarios/glossario.json", "dicionarios/atualizados/glossario_atualizado.json") # realizei o código e depois coloquei em comentário

# Converter o glossario_completo
def map_referencia_gramatical(ref):
    ref = (ref or "").strip()
    if ref == "s.f.":
        return "n f"
    elif ref == "s.m.":
        return "n m"
    return ""

def normalizar_entrada_glossario_completo(termo, item):
    return termo, {
        "dicionario": "glossario_neologismos_saude",
        "categoria lexical da designação": map_referencia_gramatical(item.get("referencia_gramatical", "")),
        "complementos designação": {
            "siglas": [item["Sigla"]] if item.get("Sigla") else [],
            "sinónimos absolutos": item.get("Sinonimos", ""),
            "sinónimos complementares": [],
            "denominação comercial": "",
            "consultar outra entrada": ""
        },
        "traduções": {
            "occità": "",
            "basc": "",
            "gallec": "",
            "castellà": item.get("equivalencias", {}).get("espanhol", ""),
            "anglès": item.get("equivalencias", {}).get("ingles", ""),
            "francès": "",
            "portuguès": "",
            "[PT]portuguès de Portugal": "",
            "[BR]portuguès del Brasil": "",
            "neerlandè": "",
            "àrab": ""
        },
        "códigos alternativos": {
            "sbl": "",
            "nc": "",
            "CAS": ""
        },
        "áreas temáticas": {
            "área": "",
            "descrição": item.get("Definicao", "")
        },
        "notas": {
            "informacoes_notas": [],
            "Informacao_enciclopedica": item.get("Informacao_enciclopedica", ""),
            "Abonacao": item.get("Abonacao", ""),
            "Numero_identificacao": item.get("Numero_identificacao", ""),
            "Marcas_Tipograficas": item.get("Marcas_Tipograficas", []),
            "remissiva": "",
            "expandida": ""
        }
    }

def converter_glossario_completo(input_path, output_path):
    with open(input_path, encoding="utf-8") as f:
        glossario = json.load(f)

    resultado = {}

    for termo, item in glossario.items():
        termo = termo.strip()
        if not termo:
            continue
        letra = termo[0].upper()
        if letra not in resultado:
            resultado[letra] = {}
        _, dados = normalizar_entrada_glossario_completo(termo, item)
        resultado[letra][termo] = dados

    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(resultado, f_out, ensure_ascii=False, indent=2)
        
# Exemplo de uso:
converter_glossario_completo("dicionarios/glossario_completo.json", "dicionarios/atualizados/glossario_completo_atualizado.json")
        
def normalizar_webscraping_entrada(termo, item):
    return termo, {
        "dicionario": "vocabulaire-de-la-medecine-oqlf",
        "categoria lexical da designação": "",  
        "complementos designação": {
            "siglas": [],
            "sinónimos absolutos": "",
            "sinónimos complementares": [],
            "denominação comercial": "",
            "consultar outra entrada": ""
        },
        "traduções": {
            "castellà": "",
            "anglès": ", ".join(item.get("ingles", [])),
            "anglès_associado": ", ".join(item.get("ingles_associado", [])),
            "francès": ", ".join(item.get("termos_privilegiados", [])),
            "francès_contexte": ", ".join(item.get("termos_em_contexto", []))
        },
        "códigos alternativos": {
            "símbolo": "",
            "nome científico": "",
            "número CAS": ""
        },
        "áreas temáticas": {
            "área": ", ".join(item.get("dominio", [])),
            "descrição": item.get("Definição:", "")
        },
        "notas": {
            "informacoes_notas": [item.get("Notas:", "")],
            "Informacao_enciclopedica": "",
            "Abonacao": "",
            "Numero_identificacao": "",
            "Marcas_Tipograficas": [],
            "remissiva": "",
            "expandida": ""
        }
    }
    

def converter_webscraping_json(input_path, output_path):
    with open(input_path, encoding="utf-8") as f:
        scraping_data = json.load(f)

    resultado = {}

    for letra, termos in scraping_data.items():
        for termo, dados in termos.items():
            termo_norm, entrada = normalizar_webscraping_entrada(termo, dados)
            letra_termo = termo_norm[0].upper()
            if letra_termo not in resultado:
                resultado[letra_termo] = {}
            resultado[letra_termo][termo_norm] = entrada

    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(resultado, f_out, ensure_ascii=False, indent=2)

# Exemplo de chamada
# converter_webscraping_json("output1.json", "oqlf_atualizado.json")


#Junção de todos num gigante:

def merge_ordenado_dicionarios(input_paths, output_path):
    combinado = defaultdict(dict)

    # Função para mesclar conteúdos por letra
    def juntar(destino, novo):
        for letra, termos in novo.items():
            if letra not in destino:
                destino[letra] = {}
            destino[letra].update(termos)

    # Lê todos os ficheiros e junta os dados
    for path in input_paths:
        with open(path, encoding="utf-8") as f:
            dados = json.load(f)
            juntar(combinado, dados)

    # Ordena os termos de cada letra
    resultado_final = OrderedDict()
    for letra in sorted(combinado.keys()):
        termos_ordenados = OrderedDict(
            sorted(combinado[letra].items(), key=lambda x: x[0].lower())
        )
        resultado_final[letra] = termos_ordenados

    # Grava o ficheiro unificado
    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(resultado_final, f_out, ensure_ascii=False, indent=2)

ficheiros_entrada = [
    "dicionarios/atualizados/bd_atualizado.json",
    "dicionarios/atualizados/glossario_atualizado.json",
    "dicionarios/atualizados/glossario_completo_atualizado.json"
]

ficheiro_saida = "dicionario_unificado.json"

merge_ordenado_dicionarios(ficheiros_entrada, ficheiro_saida)

# Exemplo de uso:
ficheiros_entrada = [
    "dicionario_unificado.json",
    "oqlf_atualizado.json"
]

ficheiro_saida = "dicionario_unificado1.json"

merge_ordenado_dicionarios(ficheiros_entrada, ficheiro_saida)

