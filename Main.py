import pygame
import random
import os
import time
import tkinter as tk
from tkinter import simpledialog
import json
import math
import speech_recognition as sr
import threading
from datetime import datetime

should_exit_game = False

def listen_for_exit_command():
    global should_exit_game
    r = sr.Recognizer()
    
    r.energy_threshold = 300 
    r.pause_threshold = 0.8 
    r.non_speaking_duration = 0.5 

    print("Iniciando escuta do microfone...")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1) 
        print("Calibrado para o ruído ambiente. Diga 'EXIT' para sair.")
        while not should_exit_game:
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=3) 
                text = sr.recognize_google(audio, language="en-US").lower() 
                print(f"Você disse: {text}")

                if "exit" in text:
                    print("Comando 'EXIT' detectado! Encerrando o jogo...")
                    should_exit_game = True
                    break 
            except sr.UnknownValueError:
                pass 
            except sr.RequestError as e:
                print(f"Erro de serviço de reconhecimento de fala; {e}")
                print("Verifique sua conexão com a internet.")
            except sr.WaitTimeoutError:
                pass 
            except Exception as e:
                print(f"Ocorreu um erro inesperado na escuta: {e}")
                
    print("Thread de escuta finalizada.")

pygame.init()

larguraTela = 1000
alturaTela = 700

pretoSuave = (30, 30, 40)
brancoPuro = (255, 255, 255)
azulNeon = (0, 200, 255)
roxoProfundo = (100, 50, 150)
verdeBrilhante = (50, 255, 50)
amareloVibrante = (255, 255, 50)
laranjaQueimado = (255, 100, 0)
vermelhoVibrante = (255, 0, 0)
cinzaEscuro = (70, 70, 80)
cinzaMedio = (120, 120, 130)

azulSuave = (50, 100, 150)
roxoEscuro = (70, 30, 100)
vermelhoEscuro = (150, 0, 0)
cinzaBotaoSairSombra = (40, 40, 40)

try:
    caminhoFonte = "Arquivos/PressStart2P-Regular.ttf"
    fonteTituloGrande = pygame.font.Font(caminhoFonte, 45)
    fontePrincipal = pygame.font.Font(caminhoFonte, 40)
    fonteSecundaria = pygame.font.Font(caminhoFonte, 25)
    fontePequena = pygame.font.Font(caminhoFonte, 20)
    fonteMenor = pygame.font.Font(caminhoFonte, 16)
    fonte_menu_botoes = pygame.font.Font(caminhoFonte, 24) 
    fonteMunicaoBarra = pygame.font.Font(caminhoFonte, 18) 
except FileNotFoundError:
    print(f"Fonte personalizada '{caminhoFonte}' não encontrada. Usando fonte padrão do sistema.")
    fonteTituloGrande = pygame.font.SysFont("consolas", 45, bold=True)
    fontePrincipal = pygame.font.SysFont("consolas", 40, bold=True)
    fonteSecundaria = pygame.font.SysFont("consolas", 25, bold=True)
    fontePequena = pygame.font.SysFont("consolas", 20, bold=True)
    fonteMenor = pygame.font.SysFont("consolas", 16, bold=True)
    fonte_menu_botoes = pygame.font.SysFont("consolas", 24, bold=True) 
    fonteMunicaoBarra = pygame.font.SysFont("consolas", 18, bold=True)


def inicializarBancoDeDados():
    if not os.path.exists("log.dat"):
        with open("log.dat", "w") as f:
            json.dump({}, f)

def escreverDados(nome, metros, tempo_vivo_segundos): 
    data_hora_agora = datetime.now()
    data_hora_formatada = data_hora_agora.strftime("%d/%m/%Y %H:%M:%S")

