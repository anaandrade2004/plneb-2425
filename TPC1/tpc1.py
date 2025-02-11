def reverse_s():
    s = input("Introduza o que deseja associar à string: \n")
    s_reverse = s[::-1]
    print(s_reverse)

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

def vowels():
    vogais = "aáàâãeéêiíoóôõuú"
    s = input("Introduza o que deseja associar à string: \n")
    count_vowels = sum(1 for char in s.lower() if char in vogais)
    print(f"A string introduzida apresenta {count_vowels} vogais.")

def lowercase():
    s = input("Introduza o que deseja associar à string: \n")
    low = s.lower()
    print(low)

def uppercase():
    s = input("Introduza o que deseja associar à string: \n")
    upper = s.upper()
    print(upper)

def capicua():
    s = input("Introduza o que deseja associar à string: \n")
    reverse = s[::-1]
    res = False
    if s == reverse:
        res = True
    else: 
        res = False
    print(f"A string é uma Capicua? {res} ")

def balanced():
    s1 = input("Introduza a primeira string: \n")
    s2 = input("Introduza a segunda string: \n")
    res = True
    for char in s1:
        if char not in s2:
            res = False
    
    for char in set(s1):  
        if s1.count(char) > s2.count(char):
            res = False
    
    print(res)

def occur():
    s1 = input("Introduza a primeira string: \n")
    s2 = input("Introduza a segunda string: \n")
    count = 0
    for char in s2:
        if char in s1:
            count += 1
    print(count)

def anagram():
    s1 = input("Introduza a primeira string: \n")
    s2 = input("Introduza a segunda string: \n")
    
    if len(s1) != len(s2):
        print(f'As strings "{s1}" e "{s2}" são anagramas? False')
        return
    
    res = sorted(s1) == sorted(s2)
    print(f'As strings "{s1}" e "{s2}" são anagramas? {res}')

def calcular_classes_anagramas():
    from collections import defaultdict
    dicionario = ["listen", "silent", "enlist", "google", "gogole", "inlets", "banana", "café", "feca"]
    classes = defaultdict(list)
    
    for palavra in dicionario:
        assinatura = ''.join(sorted(palavra.lower()))
        classes[assinatura].append(palavra)
    
    for assinatura, palavras in classes.items():
        print(f"Classe de anagramas '{assinatura}': {palavras}")

def menu():
    while True:
        print("\n--- Menu ---")
        print("1. Inverter string")
        print("2. Contar 'a' e 'A'")
        print("3. Contar vogais")
        print("4. Converter para minúsculas")
        print("5. Converter para maiúsculas")
        print("6. Verificar se é capicua")
        print("7. Verificar se strings são balanceadas")
        print("8. Contar ocorrências de caracteres")
        print("9. Verificar se são anagramas")
        print("10. Calcular classes de anagramas")
        print("0. Sair")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == "1":
            reverse_s()
        elif escolha == "2":
            find_aA()
        elif escolha == "3":
            vowels()
        elif escolha == "4":
            lowercase()
        elif escolha == "5":
            uppercase()
        elif escolha == "6":
            capicua()
        elif escolha == "7":
            balanced()
        elif escolha == "8":
            occur()
        elif escolha == "9":
            anagram()
        elif escolha == "10":
            calcular_classes_anagramas()
        elif escolha == "0":
            print("A Sair ...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Executa o menu
menu()