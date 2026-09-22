from random import randint
from time import sleep

limite = 21
total_usuario = total_computador = 0
parar_usuario = parar_computador = False

while True:
    while total_usuario < limite:
        resposta = input("Deseja cavar uma carta? (s/n) ")
        
        if resposta.lower() == "s":
            carta = randint(1, 10)
            total_usuario += carta
            print(f"Você cavou {carta}. Total: {total_usuario}")

            if total_usuario == limite:
                print(f"Você venceu! Total do usuário: {total_usuario}, Total do computador: {total_computador}")
                break
            elif total_usuario > limite:
                print(f"Estouro! Passou a vez.")
                total_usuario = 0
                break
        elif resposta.lower() == "n":
            parar_usuario = True
            break
        else:
            print("Resposta inválida. Digite 's' para sim ou 'n' para não.")
    if total_usuario == limite:
        break
    
    while total_computador < limite:
        if total_computador < 17:
            carta = randint(1, 10)
            total_computador += carta
            print(f"O computador cavou {carta}. Total: {total_computador}")
            sleep(1.2)

            if total_computador == limite:
                print(f"O computador venceu! Total do usuário: {total_usuario}, Total do computador: {total_computador}")
                break
            elif total_computador > limite:
                print(f"Estouro! Passou a vez.")
                total_computador = 0
                break
        else:
            print("O computador decidiu parar.")
            parar_computador = True
            break
    if total_computador == limite:
            break

    if parar_usuario and parar_computador:
        if total_usuario > total_computador:
            print(f"Você venceu! Total do usuário: {total_usuario}, Total do computador: {total_computador}")
        elif total_computador > total_usuario:
            print(f"O computador venceu! Total do usuário: {total_usuario}, Total do computador: {total_computador}")
        else:
            print(f"Empate! Total do usuário: {total_usuario}, Total do computador: {total_computador}")
        break

    total_usuario = 0
