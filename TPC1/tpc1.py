#TPC1

#1. 
def reverse_s():
    s = input("Introduza o que deseja associar à string: \n")
    s_reverse = s[::-1]
    print(s_reverse)

reverse_s()

#2.
def find_aA():
    s = input("Introduza o que deseja associar à string: \n")
    count_a = 0
    count_A = 0
    for i in s:
        if i == "a":
            count_a +=1
        elif i == "A":
            count_A += 1
    print(f"A string introduzida apresenta {count_a} caracteres -a- e {count_A} caracteres -A- .")

find_aA()

#3. 
def vowels():
    vogais = "aáàâãeéêiíoóôõuú"
    s = input("Introduza o que deseja associar à string: \n")
    count_vowels = sum(1 for char in s.lower() if char in vogais)
    print(f"A string introduzida apresenta {count_vowels} vogais.")

vowels()

#4.
def lowercase():
    s = input("Introduza o que deseja associar à string: \n")
    low = s.lower()
    print(low)

lowercase()

#5.
def uppercase():
    s = input("Introduza o que deseja associar à string: \n")
    upper = s.upper()
    print(upper)
        
uppercase()

#6.
def capicua():
    s = input("Introduza o que deseja associar à string: \n")
    reverse = s[::-1]
    res = False
    if s == reverse:
        res = True
    else: 
        res = False
    print(f"A string é uma Capicua? {res} ")

capicua()


#7.
s1 = "abc"
s2 = "aabbcc"
def balanced(s1, s2):
    res = True
    for char in s1:
        if char not in s2:
            res = False
    
    for char in set(s1):  
        if s1.count(char) > s2.count(char):
            res = False
    
    print(res)
        
balanced(s1,s2)

#8.
s1 = "abc"
s2 = "aabbcc"
def occur(s1,s2):
    count = 0
    for char in s2:
        if char in s1:
            count += 1
    return print(count)

occur(s1,s2)

#9.
def anagram(s1, s2):
    
    if len(s1) != len(s2):
        return False
    
    return sorted(s1) == sorted(s2)


# s1 = "listen"
# s2 = "silent"

s3 = "hello"
s4 = "world"

resultado = anagram(s3, s4)
print(f'As strings "{s3}" e "{s4}" são anagramas? {resultado}')


#10.
from collections import defaultdict

def calcular_classes_anagramas(dicionario):

    classes = defaultdict(list)  # Dicionário para armazenar as classes de anagramas
    
    for palavra in dicionario:
        assinatura = ''.join(sorted(palavra.lower()))
        classes[assinatura].append(palavra)
    
    return classes

# Exemplo de uso
dicionario = ["listen", "silent", "enlist", "google", "gogole", "inlets", "banana", "café", "feca"]
tabela_anagramas = calcular_classes_anagramas(dicionario)

for assinatura, palavras in tabela_anagramas.items():
    print(f"Classe de anagramas '{assinatura}': {palavras}")