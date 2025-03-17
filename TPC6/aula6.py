from flask import Flask, request, render_template
import json
import re

app = Flask(__name__)
#db_file = open("../aula4/conceitos.json", encoding='UTF-8')
db_file = open("conceitos_.json", encoding='utf-8')

#se tiver muitas rotas a depender desta base de dados: db = json.load(db_file), deixamos fora da função; cc metemos na função
db = json.load(db_file)

@app.route("/")
def hello_world():
    return render_template("home.html")


@app.route('/conceitos')
def conceitos():
    designacoes = list(db.keys())
    return render_template("conceitos.html", designacoes=designacoes, title="Lista de Conceitos")

@app.post("/conceitos")
def adicionar_conceito():
    descricao = request.form.get("descricao")
    designacao = request.form.get("designacao")
    
    db[designacao]=descricao
    f_out = open("conceitos_.json", "w", encoding='utf-8')
    json.dump(db, f_out, indent=4, ensure_ascii=False)
    f_out.close()
    #form data
    designacoes=sorted(list(db.keys()))
    return render_template("conceitos.html", designacoes=designacoes, title="Lista de Conceitos")



@app.route("/pesquisar")
def pesquisar_conceitos():
    pesquisa = request.args.get("input")  # Obtém o termo pesquisado
    
    if not pesquisa:
        return render_template("pesquisar.html", pesquisa=None, resultados=None, title="Pesquisa de Conceitos")

    # Criar regex para capturar a palavra exata (\b indica limite de palavra)
    regex = rf"\b{re.escape(pesquisa)}\b"

    # Filtrar conceitos onde a palavra aparece na designação ou na descrição
    resultados = {k: v for k, v in db.items() if re.search(regex, k, re.IGNORECASE) or re.search(regex, v, re.IGNORECASE)}

    # Destacar e criar hiperligação nas ocorrências encontradas
    def destacar_texto(texto):
        return re.sub(
            regex, 
            rf'<a href="/conceitos/{pesquisa}" class="text-decoration-none"><u>\g<0></u></a>', 
            texto, 
            flags=re.IGNORECASE
        )

    # Aplicar a função de destaque nas designações e descrições
    resultados_formatados = {destacar_texto(k): destacar_texto(v) for k, v in resultados.items()}

    return render_template("pesquisar.html", pesquisa=pesquisa, resultados=resultados_formatados, title="Pesquisa de Conceitos")


@app.route('/api/conceitos')
def conceitos_api():
    return db #fazer render_template


@app.route('/conceitos/<designacao>')
def conceitos_api_desi(designacao):
    designacoes = list(db.keys())
    
    if designacao in designacoes:
        descricao = db[designacao]
        return render_template("conceito.html", designacao=designacao, descricao=descricao, title="Conceito")
    else:
        return render_template("conceito.html", designacao="Erro", descricao="Descrição não encontrada", title="Conceito")


#NOTA: o browser só faz GETs
#adicionar coisas -> POST
#@app.route("/conceitos", methods=["POST"])
@app.post("/api/conceitos")
def adicionar_conceito_api():
    #json
    data = request.get_json()
    # vamos assumir que o json vem deste formato -> {"designacao": "vida", "descricao": "a vida é ..."}
    db[data["designacao"]] = data["descricao"] #adicionar
    f_out = open("conceitos_.json", "w", encoding='utf-8')
    json.dump(db, f_out, indent=4, ensure_ascii=False)
    f_out.close()
    
    #form data
    return data
 

app.run(host="localhost", port=4002, debug=True)

