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
            json.dump({}, f)

def escreverDados(nome, metros, tempo_vivo_segundos): 
    data_hora_agora = datetime.now()
    data_hora_formatada = data_hora_agora.strftime("%d/%m/%Y %H:%M:%S")

    try:
        with open("log.dat", "r") as f:
            dados = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        dados = {}

    if nome not in dados:
        dados[nome] = []
    
    dados[nome].append((metros, tempo_vivo_segundos, data_hora_formatada))

    with open("log.dat", "w") as f:
        json.dump(dados, f, indent=4)