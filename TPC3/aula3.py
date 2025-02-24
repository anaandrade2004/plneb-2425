import re

file = open("../plneb-2425/data/dicionario_medico.txt", encoding= 'UTF-8')

texto = file.read()

# 1. Marcar os limites de conceito apenas quando NÃO houver quebra de página em seguida
texto = re.sub(r'\n\n(?!\f)', '\n\n@', texto)

# 2. Remover os tokens de quebra de página (\f)
texto = re.sub(r'\f', '', texto)


def limpa_descricao(descricao):
    descricao = descricao.strip()
    descricao = re.sub(r'\n', ' ', descricao)
    return descricao



#extrair informação
conceitos_raw = re.findall(r'@(.*)\n([^@]*)', texto)

conceitos = [(designacao, limpa_descricao(descricao)) for designacao, descricao in conceitos_raw]


print(conceitos)

#gerar HTML

def gera_html(conceitos):
    html_header = """
        <!DOCTYPE html>
            <head>
            <meta charset="UTF-8"/>
            </head>
            <body> 
            <h3>Dicionário De Conceitos Médicos</h3>
            <p>Este dicionário foi desenvolvido para a aula de PLNEB 2024/2025</p>"""
        
    html_conceitos = ""
    for designacao, descricao in conceitos:
        html_conceitos += f"""
            <div>
            <p><b>{designacao}</b></p>
            <p>{descricao}</p>  
            </div>
            <hr/>
        """
    
    html_footter = """
            </body>
        </html>
    """

    return html_header + html_conceitos + html_footter

html = gera_html(conceitos)

f_out = open("dicionario_medico.html", "w", encoding= "UTF-8")
f_out.write(html)
f_out.close()

file.close()