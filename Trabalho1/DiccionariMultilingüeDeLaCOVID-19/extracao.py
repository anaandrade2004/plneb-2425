import re 
import json


# 1. Abrir e ler o arquivo (com encoding UTF-8 para caracteres especiais)
with open('dicionario_extraido.txt', 'r', encoding='utf-8') as file:
    text = file.read()


#códigos de controlo - FF (Form Feed - \x0C); BEL (Bell - \x07)
text = re.sub(r'[\x07\x0C]', '', text)  # Remove BEL e FF

# retira toda a informação irrelavante acima da marca "=== PÁGINA 28 ===",
# a partir dessa marca é quando começam as designações e outros componentes 
# importantes do dicionário
text = re.sub(r'^(.*\n)*?=== PÁGINA 28 ===\n?','', text)

# Elimina tudo a partir de "=== PÁGINA 181 ===" (incluindo essa linha)
text = re.sub(r'=== PÁGINA 181 ===[\s\S]*$', '', text)

# Tirar a numeração das páginas nos casos em que a numeração 
# original da página fica em cima da identificação da página 
# formulada na extração de pdf para text
text = re.sub(r'\d+\n\n===\sPÁGINA\s\d+\s===', '', text)

# caso existam "===\sPÁGINA\s\d+\s===" separadas 
text = re.sub(r'===\sPÁGINA\s\d+\s===','', text)

# retirar o texto de cabeçalho/título que aparece no início da página quando existe mudança para a seguinte página
text = re.sub(r'QUADERNS 50  DICCIONARI MULTILINGÜE DE LA COVID-19','', text)

# tira a numeração original do dicionário
text = re.sub(r'^\d+$', '', text)

# selecionar a designação e respetiva numeração
pattern = r'^(\d+)[ \t]+([a-zA-ZÀ-ÿ0-9\'’·-]+(?:[ \t]+[a-zA-ZÀ-ÿ0-9\'’·-]+)*)[ \t]+(n\s*(?:m|f|m\s*pl|f\s*pl|m,\s*f|m\/f)?|adj|v\s*(?:tr|intr|tr\/intr))\b' #grupos de captura define a estrutura da lista final

selecionar_designacao_num_cl = re.findall(pattern, text, re.MULTILINE)
print(selecionar_designacao_num_cl)
for num, designacao, categoria in selecionar_designacao_num_cl:
    print(f"Núm: {num}, Designação: {designacao}, Categoria: {categoria}")

with open('dicionario_limpo.txt', 'w', encoding='utf-8') as out:
    out.write(text)

print("Texto limpo com sucesso e pronto para processamento!")

