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

def lerDados(nome):
    if not os.path.exists("log.dat"):
        return []
    try:
        with open("log.dat", "r") as f:
            dados = json.load(f)
        return dados.get(nome, [])
    except json.JSONDecodeError:
        return []

def pedir_nome():
    root = tk.Tk()
    root.withdraw()
    nome = None
    while not nome:
        nome = simpledialog.askstring("NOME", "DIGITE SEU NOME:")
    root.destroy()
    return nome

class Botao:
    def __init__(self, x, y, w, h, texto, fonte, corTexto, corBotao, corSombra):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.fonte = fonte
        self.corTexto = corTexto
        self.corBotao = corBotao
        self.corSombra = corSombra
        self.sombraOffset = 5

    def draw(self, tela):
        sombraRect = self.rect.copy()
        sombraRect.x += self.sombraOffset
        sombraRect.y += self.sombraOffset
        pygame.draw.rect(tela, self.corSombra, sombraRect, border_radius=8)
        pygame.draw.rect(tela, self.corBotao, self.rect, border_radius=8)
        textoSurf = self.fonte.render(self.texto, True, self.corTexto)
        textoRect = textoSurf.get_rect(center=self.rect.center)
        tela.blit(textoSurf, textoRect)

    def clicado(self, pos):
        return self.rect.collidepoint(pos)

class Particle:
    def __init__(self, x, y, color, radius, xVel, yVel, decayRate):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.xVel = xVel
        self.yVel = yVel
        self.decayRate = decayRate

    def move(self):
        self.x += self.xVel
        self.y += self.yVel
        self.radius -= self.decayRate
        return self.radius <= 0

    def draw(self, screen):
        if self.radius > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))

particles = []

def create_explosion_particles(x, y, numParticles, colors, minRadius, maxRadius, minVel, maxVel, decay):
    for _ in range(numParticles):
        color = random.choice(colors)
        radius = random.uniform(minRadius, maxRadius)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(minVel, maxVel)
        xVel = speed * math.cos(angle)
        yVel = speed * math.sin(angle)
        particles.append(Particle(x, y, color, radius, xVel, yVel, decay))

def desenhar_barra_municao(tela, municaoRestante, maxMunicao, municaoRecarregando, tempoRecarregando, tempoEspera):
    barraLargura = 200
    barraAltura = 20  
    barraX = larguraTela - barraLargura - 50 
    barraY = 50

    corBarra = verdeBrilhante

    if municaoRecarregando:
        tempoPassado = time.time() - tempoRecarregando
        progressoRecarregar = min(tempoPassado / tempoEspera, 1)
        larguraPreenchida = int(progressoRecarregar * barraLargura)
        corBarra = laranjaQueimado
    else:
        if maxMunicao > 0:
            percentagemMunicao = (municaoRestante / maxMunicao) * 100
            if percentagemMunicao > 75:
                corBarra = verdeBrilhante
            elif percentagemMunicao > 50:
                corBarra = amareloVibrante
            elif percentagemMunicao > 25:
                corBarra = laranjaQueimado
            else:
                corBarra = vermelhoVibrante
        larguraPreenchida = int((municaoRestante / maxMunicao) * barraLargura)

    pygame.draw.rect(tela, cinzaEscuro, (barraX, barraY, barraLargura, barraAltura), border_radius=8) 
    pygame.draw.rect(tela, corBarra, (barraX, barraY, larguraPreenchida, barraAltura), border_radius=8)
    pygame.draw.rect(tela, brancoPuro, (barraX, barraY, barraLargura, barraAltura), 2, border_radius=8)

    textoMunicaoStr = f"MUNICAO: {municaoRestante}/{maxMunicao}"
    textoRender = fonteMunicaoBarra.render(textoMunicaoStr, True, brancoPuro)
    textoRect = textoRender.get_rect(center=(barraX + barraLargura // 2, barraY - textoRender.get_height() // 2 - 2))
    tela.blit(textoRender, textoRect)
    
    if municaoRecarregando:
        textoRecarregandoStr = "RECARREGANDO..."
        textoRecarregandoRender = fonteMenor.render(textoRecarregandoStr, True, brancoPuro)
        textoRecarregandoRect = textoRecarregandoRender.get_rect(center=(barraX + barraLargura // 2, barraY + barraAltura + textoRecarregandoRender.get_height() // 2 + 2))
        tela.blit(textoRecarregandoRender, textoRecarregandoRect)

def tela_morte(tela, nome, metros):
    global should_exit_game 
    if should_exit_game: 
        return False 

    try:
        fundoMorte = pygame.image.load("Arquivos/TelaMorte.png")
        fundoMorte = pygame.transform.scale(fundoMorte, (larguraTela, alturaTela))
    except Exception as e:
        print("Erro ao carregar TelaMorte.png:", e)
        fundoMorte = pygame.Surface((larguraTela, alturaTela))
        fundoMorte.fill(pretoSuave)

    corTituloMorte = vermelhoVibrante
    corPontuacaoMorte = brancoPuro
    corHistoricoMorte = brancoPuro
    corTextoLista = brancoPuro
    
    x_pos_botoes = larguraTela // 2 - 50 
    y_retry = alturaTela - 100 
    y_exit = y_retry + 50 

    dadosPartidasComDetalhes = lerDados(nome)
    
    dadosPartidasComDetalhes.sort(key=lambda x: x[0], reverse=True) 
    
    top5Partidas = dadosPartidasComDetalhes[:5]

    rodando = True
    
    tempo_piscar_morte = time.time()
    estado_piscar_morte = True 
    intervalo_piscar = 0.4 

    texto_retry_surf_base = fonte_menu_botoes.render("RETRY", True, brancoPuro)
    texto_retry_rect_base = texto_retry_surf_base.get_rect(center=(x_pos_botoes, y_retry))
    
    texto_exit_surf_base = fonte_menu_botoes.render("EXIT", True, brancoPuro)
    texto_exit_rect_base = texto_exit_surf_base.get_rect(center=(x_pos_botoes, y_exit))
    
    while rodando and not should_exit_game: 
        pos_mouse_hover = pygame.mouse.get_pos() 
        
        tempo_atual = time.time()
        if tempo_atual - tempo_piscar_morte >= intervalo_piscar:
            estado_piscar_morte = not estado_piscar_morte
            tempo_piscar_morte = tempo_atual

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                should_exit_game = True 
                break 
            elif evento.type == pygame.KEYDOWN: 
                if evento.key == pygame.K_ESCAPE:
                    should_exit_game = True 
                    break 
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if texto_retry_rect_base.collidepoint(evento.pos): 
                    return True
                if texto_exit_rect_base.collidepoint(evento.pos): 
                    should_exit_game = True 
                    break 
        
        if should_exit_game: 
            break

        tela.blit(fundoMorte, (0, 0))

        textoTitulo = fonteTituloGrande.render("GAME OVER", True, corTituloMorte)
        textoTituloRect = textoTitulo.get_rect(center=(larguraTela // 2, 100))
        tela.blit(textoTitulo, textoTituloRect)

        textoMetros = fontePrincipal.render(f"PONTUACAO: {int(metros)} METROS", True, corPontuacaoMorte)
        textoMetrosRect = textoMetros.get_rect(center=(larguraTela // 2, 200))
        tela.blit(textoMetros, textoMetrosRect)

        textoHist = fonteSecundaria.render("ULTIMAS 5 PARTIDAS", True, corHistoricoMorte)
        textoHistRect = textoHist.get_rect(center=(larguraTela // 2, 280))
        tela.blit(textoHist, textoHistRect)

        yLista = 330
        if not top5Partidas:
            textoNenhum = fontePequena.render("NENHUMA PONTUACAO AINDA", True, corTextoLista)
            textoNenhumRect = textoNenhum.get_rect(center=(larguraTela // 2, yLista))
            tela.blit(textoNenhum, textoNenhumRect)
        else:
            for i, partida_info in enumerate(top5Partidas, start=1):
                pontuacao = partida_info[0]
                data_hora = partida_info[2]
                
                textoPartida = fontePequena.render(f"#{i}: {pontuacao}m - {data_hora.split(' ')[1]}", True, corTextoLista)
                textoPartidaRect = textoPartida.get_rect(center=(larguraTela // 2, yLista))
                tela.blit(textoPartida, textoPartidaRect)
                yLista += 40

        prefixo_retry = " "
        if texto_retry_rect_base.collidepoint(pos_mouse_hover): 
            prefixo_retry = ">"
            texto_final_retry_surf = fonte_menu_botoes.render(f"{prefixo_retry} RETRY", True, brancoPuro)
            texto_final_retry_rect = texto_final_retry_surf.get_rect(center=(x_pos_botoes, y_retry))
            tela.blit(texto_final_retry_surf, texto_final_retry_rect)
        elif estado_piscar_morte: 
            texto_final_retry_surf = fonte_menu_botoes.render(f"{prefixo_retry} RETRY", True, brancoPuro)
            texto_final_retry_rect = texto_final_retry_surf.get_rect(center=(x_pos_botoes, y_retry))
            tela.blit(texto_final_retry_surf, texto_final_retry_rect)

        prefixo_exit = " "
        if texto_exit_rect_base.collidepoint(pos_mouse_hover): 
            prefixo_exit = ">"
            texto_final_exit_surf = fonte_menu_botoes.render(f"{prefixo_exit} EXIT", True, brancoPuro)
            texto_final_exit_rect = texto_final_exit_surf.get_rect(center=(x_pos_botoes, y_exit))
            tela.blit(texto_final_exit_surf, texto_final_exit_rect)
        elif estado_piscar_morte: 
            texto_final_exit_surf = fonte_menu_botoes.render(f"{prefixo_exit} EXIT", True, brancoPuro)
            texto_final_exit_rect = texto_final_exit_surf.get_rect(center=(x_pos_botoes, y_exit))
            tela.blit(texto_final_exit_surf, texto_final_exit_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    return False 
