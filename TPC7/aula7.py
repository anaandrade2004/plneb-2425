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

def find_conceito(db, query, word_bound, case_sensitive):
    res=[]
    flags = 0
    if word_bound == "on":
        pattern = r"\b(" + query + r")\b"
    else: 
        pattern = r"(" + query + r")"

    if case_sensitive != "on":
        flags = re.IGNORECASE

    for designacao, descricao in db.items():
        if re.search(pattern, designacao, flags) or re.search(pattern, descricao, flags):
            bold_designacao = re.sub(pattern, r"<strong>\1</strong>", designacao, flags )
            bold_descricao = re.sub(pattern, r"<strong>\1</strong>", descricao, flags)
            res.append((designacao, bold_designacao, bold_descricao))
    return res

@app.route("/pesquisa")
def pesquisar_conceitos():
    query = request.args.get("query")
    word_bound = request.args.get("word_bound")
    case_sensitive = request.args.get("case_sensitive")

    if not query:
        return render_template("pesquisa.html", title="Pesquisa")
    
    res = find_conceito(db, query, word_bound, case_sensitive)

    return render_template("pesquisa.html", conceitos=res, query=query, word_bound=word_bound, case_sensitive=case_sensitive, title="Pesquisa")


@app.delete("/conceitos/<designacao>")
def delete_conceito(designacao):
    if designacao in db:
        del db[designacao]
        f_out = open("conceitos_.json", "w", encoding="utf-8")
        json.dump(db,f_out, indent=4, ensure_ascii=False)
        f_out.close()
        return {"success":True, "message" : "Conceito apagado com sucesso", "redirect_url":"/conceitos", "data":designacao}
    return {"success":False, "message" : "O conceito não existe", "redirect_url":"/conceitos", "data":designacao}

@app.get("/conceitos/tabela")
def conceitos_tabela():
    return render_template("tabela.html", conceitos=db.items(), title="Tabela de Conceitos")

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

