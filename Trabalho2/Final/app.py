from flask import Flask, render_template, request, redirect, url_for
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
model = SentenceTransformer('pt-mteb/average_fasttext_cc.pt.300')

DATA_FILE = "medical_concepts_with_embeddings.json"

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()
concept_list = []

def normalize_area(area):
    return area.strip().lower()

def build_concept_list():
    global concept_list
    concept_list = []
    for letter, concepts in data.items():
        for term, concept in concepts.items():
            embedding = concept.get("embedding")
            if embedding and isinstance(embedding, list):
                concept_list.append((term, np.array(embedding), concept))

build_concept_list()

def boost_similarity(term, description, query, score, alpha=0.2, beta=0.1):
    query_lower = query.lower()
    term_lower = term.lower()
    description_lower = description.lower() if description else ""
    boost = 0.0
    if query_lower in term_lower:
        boost += alpha
    if query_lower in description_lower:
        boost += beta
    return min(score + boost, 1.0)

def apply_filters(concept, selected_filters):
    for key, selected_vals in selected_filters.items():
        if selected_vals:
            val = concept.get(key, "").lower().strip()
            if not any(val == v.lower().strip() for v in selected_vals):
                return False
    return True

def find_similar_concepts(query, top_k=10, filters=None):
    query_vec = model.encode(query).reshape(1, -1)
    similarities = cosine_similarity(query_vec, [c[1] for c in concept_list])[0]
    boosted_results = []

    for i, (term, _, concept) in enumerate(concept_list):
        if filters and not apply_filters({
            "dicionario": concept.get("dicionario", ""),
            "categoria lexical da designação": concept.get("categoria lexical da designação", ""),
            "area": normalize_area(concept.get("áreas temáticas", {}).get("área", ""))
        }, filters):
            continue
        score = similarities[i]
        description = concept.get("áreas temáticas", {}).get("descrição", "")
        boosted_score = boost_similarity(term, description, query, score)
        boosted_results.append((term, boosted_score, concept))

    return sorted(boosted_results, key=lambda x: x[1], reverse=True)[:top_k]

def search_by_similarity(query, top_k=10):
    query_vec = model.encode(query).reshape(1, -1)
    similarities = cosine_similarity(query_vec, [c[1] for c in concept_list])[0]
    results = []
    for i, (term, _, concept) in enumerate(concept_list):
        description = concept.get("áreas temáticas", {}).get("descrição", "")
        score = similarities[i]
        boosted_score = boost_similarity(term, description, query, score)
        results.append((term, boosted_score, concept))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

def filter_concepts(active_filters):
    filtered = []
    for term, _, concept in concept_list:
        if apply_filters({
            "dicionario": concept.get("dicionario", ""),
            "categoria lexical da designação": concept.get("categoria lexical da designação", ""),
            "area": normalize_area(concept.get("áreas temáticas", {}).get("área", ""))
        }, active_filters):
            filtered.append((term, concept))
    return filtered

def search_with_similarity_and_filters(query, top_k=10, filters=None):
    query_vec = model.encode(query).reshape(1, -1)
    similarities = cosine_similarity(query_vec, [c[1] for c in concept_list])[0]
    results = []
    for i, (term, _, concept) in enumerate(concept_list):
        if filters and not apply_filters({
            "dicionario": concept.get("dicionario", ""),
            "categoria lexical da designação": concept.get("categoria lexical da designação", ""),
            "area": normalize_area(concept.get("áreas temáticas", {}).get("área", ""))
        }, filters):
            continue
        description = concept.get("áreas temáticas", {}).get("descrição", "")
        score = similarities[i]
        boosted_score = boost_similarity(term, description, query, score)
        results.append((term, boosted_score, concept))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

CONCEPTS_PER_PAGE = 10

@app.route("/", methods=["GET"])
def home():
    global data
    data = load_data()

    page = request.args.get('page', 1, type=int)

    selected_filters = {
        "dicionario": request.args.getlist("dicionario"),
        "categoria lexical da designação": request.args.getlist("categoria_lexical"),
        "area": request.args.getlist("area"),
    }

    all_concepts = []
    dictionaries_set = set()
    lexical_categories_set = set()
    areas_set = set()

    for letter, concepts in data.items():
        for term, concept in concepts.items():
            area = concept.get("áreas temáticas", {}).get("\u00e1rea", "")
            categoria = concept.get("categoria lexical da designação", "").strip()
            dic = concept.get("dicionario", "")

            dictionaries_set.add(dic)
            lexical_categories_set.add(categoria)
            areas_set.add(area)

            if apply_filters({
                "dicionario": dic,
                "categoria lexical da designação": categoria,
                "area": area
            }, selected_filters):
                all_concepts.append((term, concept))

    all_concepts.sort(key=lambda x: x[0].lower())
    start = (page - 1) * CONCEPTS_PER_PAGE
    end = start + CONCEPTS_PER_PAGE
    paginated_concepts = all_concepts[start:end]
    has_next = end < len(all_concepts)

    return render_template(
        "index.html",
        concepts=paginated_concepts,
        page=page,
        has_next=has_next,
        selected_filters=request.args,
        dictionaries=sorted(filter(None, dictionaries_set)),
        lexical_categories=sorted(filter(None, lexical_categories_set)),
        areas=sorted(filter(None, areas_set)),
    )



@app.route("/search", methods=["GET"])
def search_redirect():
    query = request.args.get("query", "")
    return redirect(url_for("results", query=query, **request.args.to_dict(flat=False)))

@app.route('/concept/<letter>/<term>')
def concept_detail(letter, term):
    concept = data.get(letter.upper(), {}).get(term)
    return render_template('concept.html', term=term, concept=concept)

@app.route("/add", methods=["GET", "POST"])
def add_concept():
    global data, concept_list

    def clean_list_field(field_value):
        if not field_value or not field_value.strip():
            return []
        return [item.strip() for item in field_value.split(",")]

    def clean_str_field(field_value):
        if field_value and field_value.strip():
            return field_value.strip()
        return ""

    if request.method == "POST":
        term = request.form.get("term")
        letter = term[0].upper()
        description = clean_str_field(request.form.get("descricao", ""))

        new_concept = {
            "dicionario": clean_str_field(request.form.get("dicionario", "")),
            "categoria lexical da designação": clean_str_field(request.form.get("categoria lexical da designação", "")),
            "complementos designação": {
                "siglas": clean_list_field(request.form.get("siglas", "")),
                "sinónimos absolutos": clean_str_field(request.form.get("sinónimos absolutos", "")),
                "sinónimos complementares": clean_list_field(request.form.get("sinónimos complementares", "")),
                "denominação comercial": clean_str_field(request.form.get("denominação comercial", "")),
                "consultar outra entrada": clean_str_field(request.form.get("consultar outra entrada", ""))
            },
            "traduções": {
                "occità": clean_str_field(request.form.get("occità", "")),
                "basc": clean_str_field(request.form.get("basc", "")),
                "gallec": clean_str_field(request.form.get("gallec", "")),
                "castellà": clean_str_field(request.form.get("castellà", "")),
                "anglès": clean_str_field(request.form.get("anglès", "")),
                "francès": clean_str_field(request.form.get("francès", "")),
                "portuguès": clean_str_field(request.form.get("portuguès", "")),
                "[PT]portuguès de Portugal": clean_str_field(request.form.get("[PT]portuguès de Portugal", "")),
                "[BR]portuguès del Brasil": clean_str_field(request.form.get("[BR]portuguès del Brasil", "")),
                "neerlandè": clean_str_field(request.form.get("neerlandè", "")),
                "àrab": clean_str_field(request.form.get("àrab", ""))
            },
            "códigos alternativos": {
                "sbl": clean_str_field(request.form.get("sbl", "")),
                "nc": clean_str_field(request.form.get("nc", "")),
                "CAS": clean_str_field(request.form.get("CAS", ""))
            },
            "áreas temáticas": {
                "área": clean_str_field(request.form.get("área", "")),
                "descrição": clean_str_field(request.form.get("descrição", ""))
            },
            "notas": {
                "informacoes_notas": clean_list_field(request.form.get("informacoes_notas", "")),
                "Informacao_enciclopedica": clean_str_field(request.form.get("Informacao_enciclopedica", "")),
                "Abonacao": clean_str_field(request.form.get("Abonacao", "")),
                "Numero_identificacao": clean_str_field(request.form.get("Numero_identificacao", "")),
                "Marcas_Tipograficas": clean_list_field(request.form.get("Marcas_Tipograficas", "")),
                "remissiva": clean_str_field(request.form.get("remissiva", "")),
                "expandida": clean_str_field(request.form.get("expandida", ""))
            },
            "embedding": model.encode(term).tolist()
        }

        if letter not in data:
            data[letter] = {}
        data[letter][term] = new_concept
        save_data(data)

        concept_list.append((term, np.array(new_concept["embedding"]), new_concept))

        return redirect(url_for("home"))

    return render_template("add.html")

@app.route('/concepts')
def show_all_concepts():
    page = request.args.get('page', 1, type=int)
    concepts_per_page = 20

    all_concepts = []
    for letter, concepts in data.items():
        for term, concept in concepts.items():
            all_concepts.append((letter, term, concept))

    all_concepts.sort(key=lambda x: x[1].lower())

    total = len(all_concepts)
    start = (page - 1) * concepts_per_page
    end = start + concepts_per_page
    paginated = all_concepts[start:end]

    total_pages = (total + concepts_per_page - 1) // concepts_per_page

    return render_template("concept_list.html",
                           concepts=paginated,
                           page=page,
                           total_pages=total_pages)

@app.route('/edit/<letter>/<term>', methods=['GET', 'POST'])
def edit_concept(letter, term):
    global data, concept_list
    
    if request.method == 'POST':
        # Get the existing concept
        concept = data[letter.upper()].get(term)
        if not concept:
            return redirect(url_for('home'))
        
        # Clean form data (reuse your existing cleaning functions)
        def clean_list_field(field_value):
            if not field_value or not field_value.strip():
                return []
            return [item.strip() for item in field_value.split(",")]

        def clean_str_field(field_value):
            if field_value and field_value.strip():
                return field_value.strip()
            return ""

        new_term = request.form.get("term")
        new_letter = new_term[0].upper()
        
        # Create updated concept
        updated_concept = {
            "dicionario": clean_str_field(request.form.get("dicionario", "")),
            "categoria lexical da designação": clean_str_field(request.form.get("categoria lexical da designação", "")),
            "complementos designação": {
                "siglas": clean_list_field(request.form.get("siglas", "")),
                "sinónimos absolutos": clean_str_field(request.form.get("sinónimos absolutos", "")),
                "sinónimos complementares": clean_list_field(request.form.get("sinónimos complementares", "")),
                "denominação comercial": clean_str_field(request.form.get("denominação comercial", "")),
                "consultar outra entrada": clean_str_field(request.form.get("consultar outra entrada", ""))
            },
            "traduções": {
                "occità": clean_str_field(request.form.get("occità", "")),
                "basc": clean_str_field(request.form.get("basc", "")),
                "gallec": clean_str_field(request.form.get("gallec", "")),
                "castellà": clean_str_field(request.form.get("castellà", "")),
                "anglès": clean_str_field(request.form.get("anglès", "")),
                "francès": clean_str_field(request.form.get("francès", "")),
                "portuguès": clean_str_field(request.form.get("portuguès", "")),
                "[PT]portuguès de Portugal": clean_str_field(request.form.get("[PT]portuguès de Portugal", "")),
                "[BR]portuguès del Brasil": clean_str_field(request.form.get("[BR]portuguès del Brasil", "")),
                "neerlandè": clean_str_field(request.form.get("neerlandè", "")),
                "àrab": clean_str_field(request.form.get("àrab", ""))
            },
            "códigos alternativos": {
                "sbl": clean_str_field(request.form.get("sbl", "")),
                "nc": clean_str_field(request.form.get("nc", "")),
                "CAS": clean_str_field(request.form.get("CAS", ""))
            },
            "áreas temáticas": {
                "área": clean_str_field(request.form.get("área", "")),
                "descrição": clean_str_field(request.form.get("descrição", ""))
            },
            "notas": {
                "informacoes_notas": clean_list_field(request.form.get("informacoes_notas", "")),
                "Informacao_enciclopedica": clean_str_field(request.form.get("Informacao_enciclopedica", "")),
                "Abonacao": clean_str_field(request.form.get("Abonacao", "")),
                "Numero_identificacao": clean_str_field(request.form.get("Numero_identificacao", "")),
                "Marcas_Tipograficas": clean_list_field(request.form.get("Marcas_Tipograficas", "")),
                "remissiva": clean_str_field(request.form.get("remissiva", "")),
                "expandida": clean_str_field(request.form.get("expandida", ""))
            },
            "embedding": model.encode(new_term).tolist()
        }

        # If term changed, we need to remove old entry and add new one
        if new_term.lower() != term.lower():
            # Remove old concept
            del data[letter.upper()][term]
            # Remove from concept_list
            concept_list = [c for c in concept_list if c[0].lower() != term.lower()]
            
            # Add to new letter if needed
            if new_letter not in data:
                data[new_letter] = {}
            
            # Add new concept
            data[new_letter][new_term] = updated_concept
            concept_list.append((new_term, np.array(updated_concept["embedding"]), updated_concept))
        else:
            # Just update existing concept
            data[letter.upper()][term] = updated_concept
            # Update in concept_list
            for i, (t, _, _) in enumerate(concept_list):
                if t.lower() == term.lower():
                    concept_list[i] = (term, np.array(updated_concept["embedding"]), updated_concept)
                    break

        save_data(data)
        return redirect(url_for('concept_detail', letter=new_letter, term=new_term))

    # GET request - show edit form
    concept = data.get(letter.upper(), {}).get(term)
    if not concept:
        return redirect(url_for('home'))
    
    return render_template('edit.html', term=term, concept=concept, letter=letter)

@app.route('/results')
def results():
    query = request.args.get('query', '').strip()
    top_k = int(request.args.get('top_k', 10))
    filters = {
        "dicionario": request.args.getlist('dicionario'),
        "categoria lexical da designação": request.args.getlist('categoria_lexical'),
        "area": [normalize_area(v) for v in request.args.getlist('area')]
    }

    active_filters = {k: v for k, v in filters.items() if v}

    results = []
    if query and active_filters:
        results = search_with_similarity_and_filters(query, top_k, active_filters)
    elif query:
        results = search_by_similarity(query, top_k)
    elif active_filters:
        results = filter_concepts(active_filters)
        results = [(term, None, concept) for term, concept in results]
    else:
        results = []

    return render_template(
        "results.html",
        query=query,
        filters=bool(active_filters),
        results=results
    )

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=5000)
