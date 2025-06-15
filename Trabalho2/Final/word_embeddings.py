import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Load multilingual sentence transformer
model = SentenceTransformer('pt-mteb/average_fasttext_cc.pt.300')

def extract_concept_text(term, concept, term_weight=2, desc_weight=2):
    parts = []

    # Weight the concept term more
    parts.extend([term] * term_weight)

    # Category
    parts.append(concept.get("categoria lexical da designação", ""))

    # Synonyms and related terms
    comp = concept.get("complementos designação", {})
    parts.append(comp.get("sinónimos absolutos", ""))
    parts.extend(comp.get("sinónimos complementares", []))
    parts.append(comp.get("denominação comercial", ""))

    # Translations
    translations = concept.get("traduções", {})
    parts.extend(translations.values())

    # Weighted description
    thematic = concept.get("áreas temáticas", {})
    desc = thematic.get("descrição", "")
    if desc:
        parts.extend([desc] * desc_weight)

    # Notes and typographical markers
    notas = concept.get("notas", {})
    parts.extend(notas.get("Marcas_Tipograficas", []))
    parts.append(notas.get("Informacao_enciclopedica", ""))
    parts.append(notas.get("expandida", ""))

    return " ".join(filter(None, parts)).strip()

# Load original JSON
with open("dicionario_unificado_finalll.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Compute and attach embeddings
for letter, concepts in tqdm(data.items(), desc="Embedding concepts"):
    for term, concept in concepts.items():
        full_text = extract_concept_text(term, concept)
        embedding = model.encode(full_text).tolist()
        concept["embedding"] = embedding

# Save enriched JSON
with open("medical_concepts_with_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON updated with weighted embeddings!")
