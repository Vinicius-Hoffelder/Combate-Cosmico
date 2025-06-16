import os, time
import json
from datetime import datetime

def limpar_tela():
    os.system("cls")
    
def aguarde(segundos):
    time.sleep(segundos)
    
def inicializarBancoDeDados():
    if not os.path.exists("log.dat"):
        with open("log.dat", "w") as f:
            json.dump([], f)

def escreverDados(nome, metros, tempo_total_segundos):
    horas = int(tempo_total_segundos // 3600)
    minutos = int((tempo_total_segundos % 3600) // 60)
    segundos = int(tempo_total_segundos % 60)

    with open("log.dat", "r") as f:
        dados = json.load(f)

    dados.append({
        "nome": nome,
        "metros": metros,
        "tempo": f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    })

    with open("log.dat", "w") as f:
        json.dump(dados, f, indent=4)