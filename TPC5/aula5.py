from flask import Flask, request, render_template
import json

app = Flask(__name__)
#db_file = open("../aula4/conceitos.json", encoding='UTF-8')
db_file = open("conceitos_.json", encoding='utf-8')

#se tiver muitas rotas a depender desta base de dados: db = json.load(db_file), deixamos fora da função; cc metemos na função
db = json.load(db_file)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/conceitos')
def conceitos():
    designacoes = list(db.keys())
    return render_template("conceitos.html", designacoes=designacoes, title="Lista de Conceitos")

@app.route('/api/conceitos')
def conceitos_api():
    return db #fazer render_template


@app.route('/conceitos/<designacao>')
def conceitos_api_desi(designacao):
    designacoes = list(db.keys())
    for i in designacoes:
        if i == designacao:
            descricao = db[designacao]
            return render_template("conceito.html", designacao=designacao, descricao=descricao, title="Conceito")




#NOTA: o browser só faz GETs
#adicionar coisas -> POST
#@app.route("/conceitos", methods=["POST"])
@app.post("/conceitos")
def adicionar_conceito():
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

