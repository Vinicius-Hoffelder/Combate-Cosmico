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

def explosão_particulas(x, y, numParticles, colors, minRadius, maxRadius, minVel, maxVel, decay):
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

def tela_regras(tela):
    global should_exit_game
    if should_exit_game:
        return

    try:
        fundoRegras = pygame.image.load("Arquivos/TelaMorte.png") 
        fundoRegras = pygame.transform.scale(fundoRegras, (larguraTela, alturaTela))
    except Exception as e:
        print("Erro ao carregar TelaMorte.png para tela de regras:", e)
        fundoRegras = pygame.Surface((larguraTela, alturaTela))
        fundoRegras.fill(pretoSuave)

    rodando = True
    
    x_pos_botao = larguraTela // 2
    y_pos_botao = alturaTela - 60
    botao_voltar = Botao(x_pos_botao - 100, y_pos_botao - 20, 200, 50, "VOLTAR", fonte_menu_botoes, brancoPuro, azulSuave, cinzaBotaoSairSombra)

    while rodando and not should_exit_game:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                should_exit_game = True
                break
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False 
                    break
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao_voltar.clicado(evento.pos):
                    rodando = False 
                    break

        if should_exit_game:
            break

        tela.blit(fundoRegras, (0, 0))

        textoTitulo = fontePrincipal.render("REGRAS DO JOGO", True, brancoPuro) 
        textoTituloRect = textoTitulo.get_rect(center=(larguraTela // 2, 70))
        tela.blit(textoTitulo, textoTituloRect)

        y_offset_texto = 150
        linha_altura = 30 

        regras_texto = [
            "COMO JOGAR:",
            "  MOVER: SETAS LATERAIS (ESQUERDA/DIREITA)",
            "  ATIRAR: SETA PARA CIMA (UP)",
            "  PAUSAR: TECLA ESPACO",
            "",
            "PODER ESPECIAL:",
            "  COLETE CAIXAS MISTERIOSAS para ativar!",
            "  UMA VEZ COLETADO: Aperte SETA PARA BAIXO (DOWN)",
            "  Efeito: DOBRA A CAPACIDADE DE MUNICAO POR 7s.",
            "  Tempo de Recarga da Municao: 2s (quando acaba)",
            "",
            "OBJETIVO:",
            "  DESTRUA INIMIGOS E AVANCE O MAIOR NUMERO DE METROS!",
            "  EVITE COLISOES. VOCE TEM 2 VIDAS.",
            "  A cada 100m, capacidade de municao aumenta."
        ]

        for linha in regras_texto:
            if "COMO JOGAR:" in linha or "PODER ESPECIAL:" in linha or "OBJETIVO:" in linha:
                fonte_linha = fontePequena 
            else:
                fonte_linha = fonteMenor 
            
            cor_linha = brancoPuro 

            texto_surf = fonte_linha.render(linha, True, cor_linha)
            
            texto_rect = texto_surf.get_rect(center=(larguraTela // 2, y_offset_texto + texto_surf.get_height() // 2))
            tela.blit(texto_surf, texto_rect)
            y_offset_texto += linha_altura

        botao_voltar.draw(tela)

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def tela_capa(tela):
    global should_exit_game 
    if should_exit_game: 
        return None 

    try:
        capaImg = pygame.image.load("Arquivos/Capa.jpg")
        capaImg = pygame.transform.scale(capaImg, (larguraTela, alturaTela))
    except Exception as e:
        print("Erro ao carregar Capa.jpg:", e)
        capaImg = pygame.Surface((larguraTela, alturaTela))
        capaImg.fill(pretoSuave)

    estrelasCapa = []
    for _ in range(100):
        x = random.randint(0, larguraTela)
        y = random.randint(0, alturaTela)
        raio = random.randint(1, 3)
        estrelasCapa.append({"x": x, "y": y, "raio": raio})

    x_pos_botoes = larguraTela // 2 - 50
    y_jogar = alturaTela - 150 
    y_regras = y_jogar + 50     
    y_sair = y_regras + 50      

    rodando = True
    
    tempo_piscar_capa = time.time()
    estado_piscar_capa = True 
    intervalo_piscar = 0.4 

    texto_jogar_surf_base = fonte_menu_botoes.render("JOGAR", True, brancoPuro)
    texto_jogar_rect_base = texto_jogar_surf_base.get_rect(center=(x_pos_botoes, y_jogar))
    
    texto_regras_surf_base = fonte_menu_botoes.render("REGRAS", True, brancoPuro) 
    texto_regras_rect_base = texto_regras_surf_base.get_rect(center=(x_pos_botoes, y_regras)) 
    
    texto_sair_surf_base = fonte_menu_botoes.render("SAIR", True, brancoPuro)
    texto_sair_rect_base = texto_sair_surf_base.get_rect(center=(x_pos_botoes, y_sair))

    while rodando and not should_exit_game: 
        pos_mouse_hover = pygame.mouse.get_pos()
        
        tempo_atual = time.time()
        if tempo_atual - tempo_piscar_capa >= intervalo_piscar:
            estado_piscar_capa = not estado_piscar_capa
            tempo_piscar_capa = tempo_atual

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                should_exit_game = True 
                break
            elif evento.type == pygame.K_ESCAPE: 
                should_exit_game = True 
                break
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if texto_jogar_rect_base.collidepoint(evento.pos):
                    nome = pedir_nome()
                    return nome
                
                if texto_regras_rect_base.collidepoint(evento.pos):
                    tela_regras(tela) 
                    if should_exit_game: 
                        break
                    
                if texto_sair_rect_base.collidepoint(evento.pos):
                    should_exit_game = True 
                    break
        
        if should_exit_game: 
            break

        tela.blit(capaImg, (0, 0))

        for estrela in estrelasCapa:
            pygame.draw.circle(tela, brancoPuro, (estrela["x"], estrela["y"]), estrela["raio"])

        texto_sombra = fonteTituloGrande.render("COMBATE COSMICO", True, cinzaEscuro)
        texto_sombra_rect = texto_sombra.get_rect(center=(larguraTela // 2 + 3, 150 + 3))
        tela.blit(texto_sombra, texto_sombra_rect)

        textoTitulo = fonteTituloGrande.render("COMBATE COSMICO", True, brancoPuro)
        textoTituloRect = textoTitulo.get_rect(center=(larguraTela // 2, 150))
        tela.blit(textoTitulo, textoTituloRect)

        prefixo_jogar = " "
        if texto_jogar_rect_base.collidepoint(pos_mouse_hover): 
            prefixo_jogar = ">"
            tela.blit(fonte_menu_botoes.render(f"{prefixo_jogar} JOGAR", True, brancoPuro), texto_jogar_rect_base)
        elif estado_piscar_capa: 
            tela.blit(fonte_menu_botoes.render(f"{prefixo_jogar} JOGAR", True, brancoPuro), texto_jogar_rect_base)

        prefixo_regras = " "
        if texto_regras_rect_base.collidepoint(pos_mouse_hover):
            prefixo_regras = ">"
            tela.blit(fonte_menu_botoes.render(f"{prefixo_regras} REGRAS", True, brancoPuro), texto_regras_rect_base)
        elif estado_piscar_capa:
            tela.blit(fonte_menu_botoes.render(f"{prefixo_regras} REGRAS", True, brancoPuro), texto_regras_rect_base)

        prefixo_sair = " "
        if texto_sair_rect_base.collidepoint(pos_mouse_hover): 
            prefixo_sair = ">"
            tela.blit(fonte_menu_botoes.render(f"{prefixo_sair} SAIR", True, brancoPuro), texto_sair_rect_base)
        elif estado_piscar_capa: 
            tela.blit(fonte_menu_botoes.render(f"{prefixo_sair} SAIR", True, brancoPuro), texto_sair_rect_base)

        pygame.display.flip()
        pygame.time.Clock().tick(60)
    
    if should_exit_game:
        return None 

    return None 

def jogo(nome):
    global should_exit_game 
    if should_exit_game: 
        return 

    tela = pygame.display.set_mode((larguraTela, alturaTela))
    pygame.display.set_caption("Combate Cósmico")
    relogio = pygame.time.Clock()

    tempo_inicio_jogo = time.time()

    fundoJogo = pygame.image.load("Arquivos/fundo_Jogo.jpeg")
    fundoAltura = fundoJogo.get_height()
    fundoY = 0

    inimigoImg = pygame.image.load("Arquivos/naveInimigo.png")
    naveJogador = pygame.image.load("Arquivos/navePlayer.png")
    tiroImagem = pygame.image.load("Arquivos/Tiro.png")
    etImagem = pygame.image.load("Arquivos/Et.png")
    caixaMisteriosa = pygame.image.load("Arquivos/CaixaMisteriosa.png")

    somTiro = pygame.mixer.Sound("Arquivos/SomTiro.mp3")
    somExplosao = pygame.mixer.Sound("Arquivos/Explosao.mp3")
    pygame.mixer.music.load("Arquivos/Soundtrack.mp3")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
    somTiro.set_volume(0.1)
    somExplosao.set_volume(0.3)

    posicaoNaveX = 450
    posicaoNaveY = 550
    movimentoNaveX = 0
    vidas = 2
    invencivel = False
    tempoInvencivel = 0

    tiros = []
    ladoTiroDireito = True

    tirosEspecial = False
    tempoEspecial = 0
    temEspecial = False

    maxMunicao = 6
    maxMunicaoBase = maxMunicao
    municaoRestante = maxMunicao
    municaoLimite = 24
    ultimoTempoTiro = 0
    tempoEspera = 2
    ultimoMetroMunicao = 0
    municaoRecarregando = False


    metros = 0.0
    velocidadeMetros = 0.07
    ultimoMetroInimigo = 0
    ultimoMetroCaixa = 0

    numInimigos = 10
    inimigos = []
    for _ in range(numInimigos):
        x = random.randint(0, larguraTela - inimigoImg.get_width())
        y = random.randint(-800, -100)
        vel = random.uniform(1.5, 4.5)
        vida = 3
        inimigos.append({"x": x, "y": y, "vel": vel, "vida": vida})

    caixas = []

    etVisivel = False
    etX = larguraTela
    etY = random.randint(100, 600)
    etVel = 3

    estrelas = []
    for _ in range(150):
        x = random.randint(0, larguraTela)
        y = random.randint(0, alturaTela)
        raio = random.randint(1, 2)
        velocidade = random.uniform(0.5, 2)
        estrelas.append({"x": x, "y": y, "raio": raio, "vel": velocidade})


    def toque_exato(rect1, rect2):
        return rect1.colliderect(rect2)

    rodando = True
    pausado = False
    clock = pygame.time.Clock()

    while rodando and not should_exit_game: 
        tempoAtual = time.time()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                tempo_fim_jogo = time.time()
                duracao_jogo = tempo_fim_jogo - tempo_inicio_jogo
                escreverDados(nome, int(metros), duracao_jogo)
                should_exit_game = True 
                break
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    pausado = not pausado
                elif evento.key == pygame.K_ESCAPE: 
                    tempo_fim_jogo = time.time()
                    duracao_jogo = tempo_fim_jogo - tempo_inicio_jogo
                    escreverDados(nome, int(metros), duracao_jogo)
                    should_exit_game = True 
                    break
                elif evento.key == pygame.K_DOWN and temEspecial:
                    tirosEspecial = True
                    tempoEspecial = tempoAtual
                    temEspecial = False
                    maxMunicao = maxMunicaoBase * 2
                    municaoRestante = min(municaoRestante * 2, maxMunicao)
        
        if should_exit_game: 
            break

        if pausado:
            tela.fill(pretoSuave)
            textoPausa = fontePrincipal.render("PAUSADO", True, azulNeon)
            textoPausaRect = textoPausa.get_rect(center=(larguraTela//2, alturaTela//2 - 30))
            tela.blit(textoPausa, textoPausaRect)

            textoInstrucao = fonteSecundaria.render("APERTE ESPACO PARA CONTINUAR", True, brancoPuro)
            textoInstrucaoRect = textoInstrucao.get_rect(center=(larguraTela//2, alturaTela//2 + 20))
            tela.blit(textoInstrucao, textoInstrucaoRect)
            pygame.display.flip()
            clock.tick(60)
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: movimentoNaveX = 5
        elif keys[pygame.K_LEFT]: movimentoNaveX = -5
        else: movimentoNaveX = 0

        if keys[pygame.K_UP]:
            if municaoRestante > 0 and (len(tiros) == 0 or tiros[-1].y < posicaoNaveY - 30):
                tiroX = posicaoNaveX + (57 if ladoTiroDireito else 0)
                tiros.append(pygame.Rect(tiroX, posicaoNaveY, tiroImagem.get_width(), tiroImagem.get_height()))
                ladoTiroDireito = not ladoTiroDireito
                somTiro.play()
                municaoRestante -= 1
                explosão_particulas(tiroX + tiroImagem.get_width() / 2, posicaoNaveY, 5, [(255, 255, 0), (255, 100, 0)], 1, 3, 0.5, 1.5, 0.1)

                if municaoRestante == 0:
                    ultimoTempoTiro = tempoAtual
                    municaoRecarregando = True
            elif municaoRestante == 0 and not municaoRecarregando:
                    ultimoTempoTiro = tempoAtual
                    municaoRecarregando = True

        if tirosEspecial and tempoAtual - tempoEspecial > 7:
            tirosEspecial = False
            maxMunicao = maxMunicaoBase
            municaoRestante = min(municaoRestante, maxMunicao)

        if municaoRecarregando and tempoAtual - ultimoTempoTiro >= tempoEspera:
            municaoRestante = maxMunicao
            municaoRecarregando = False

        posicaoNaveX += movimentoNaveX
        posicaoNaveX = max(0, min(posicaoNaveX, larguraTela - naveJogador.get_width()))

        for tiro in tiros: tiro.y -= 8
        tiros = [tiro for tiro in tiros if tiro.y > -10]

        rectJogador = pygame.Rect(posicaoNaveX + 20, posicaoNaveY + 20, 60, 60)
        
        caixas_a_remover = [] 
        for caixa in caixas:
            caixa["y"] += caixa["vel"]
            caixaRect = pygame.Rect(caixa["x"], caixa["y"], caixaMisteriosa.get_width(), caixaMisteriosa.get_height())

            if toque_exato(caixaRect, rectJogador):
                temEspecial = True 
                caixas_a_remover.append(caixa) 
                
            if caixa["y"] > alturaTela:
                caixas_a_remover.append(caixa) 

        for caixa in caixas_a_remover:
            if caixa in caixas: 
                caixas.remove(caixa)


        for inimigo in inimigos:
            inimigo["y"] += inimigo["vel"]
            inimigoRect = pygame.Rect(inimigo["x"] + 10, inimigo["y"] + 10, 60, 60)

            for tiro in tiros[:]:
                if tiro.colliderect(inimigoRect):
                    inimigo["vida"] -= 1
                    tiros.remove(tiro)
                    if inimigo["vida"] <= 0:
                        somExplosao.play()
                        explosão_particulas(inimigoRect.centerx, inimigoRect.centery, 20, 
                                                     [(255, 100, 0), (255, 200, 0), (255, 255, 100), (100, 100, 100)],
                                                     2, 8, 1, 4, 0.2)
                        inimigo["x"] = random.randint(0, larguraTela - inimigoImg.get_width())
                        inimigo["y"] = random.randint(-800, -100)
                        inimigo["vel"] = random.uniform(1.5, 4.5)
                        inimigo["vida"] = 3
                    break

            if inimigo["y"] > alturaTela:
                inimigo["x"] = random.randint(0, larguraTela - inimigoImg.get_width())
                inimigo["y"] = random.randint(-800, -100)
                inimigo["vel"] = random.uniform(1.5, 4.5)
                inimigo["vida"] = 3

            if toque_exato(inimigoRect, rectJogador):
                if not invencivel:
                    vidas -= 1
                    inimigo["y"] = -100
                    invencivel = True
                    tempoInvencivel = tempoAtual
                    if vidas <= 0:
                        rodando = False 
                        tempo_fim_jogo = time.time()
                        duracao_jogo = tempo_fim_jogo - tempo_inicio_jogo
                        escreverDados(nome, int(metros), duracao_jogo)
                        break 
        
        if should_exit_game: 
            break

        if invencivel and tempoAtual - tempoInvencivel >= 2: invencivel = False

        metros += velocidadeMetros

        if int(metros) - ultimoMetroMunicao >= 100:
            ultimoMetroMunicao = int(metros)
            if maxMunicaoBase < municaoLimite:
                maxMunicaoBase += 1
                if not tirosEspecial:
                    maxMunicao = maxMunicaoBase
                municaoRestante = min(municaoRestante, maxMunicao)

        if int(metros) - ultimoMetroInimigo >= 400:
            ultimoMetroInimigo = int(metros)
            x = random.randint(0, larguraTela - inimigoImg.get_width())
            y = random.randint(-800, -100)
            vel = random.uniform(1.5, 4.5)
            vida = 3
            inimigos.append({"x": x, "y": y, "vel": vel, "vida": vida})

        if int(metros) - ultimoMetroCaixa >= 150:
            ultimoMetroCaixa = int(metros)
            caixaX = random.randint(50, larguraTela - 50)
            caixaY = random.randint(-400, -100)
            caixas.append({"x": caixaX, "y": caixaY, "vel": 3})

        if metros >= 400: etVisivel = True

        if etVisivel:
            etX -= etVel
            if etX < -etImagem.get_width():
                etVisivel = False
                etX = larguraTela
                etY = random.randint(100, 600)

        tela.fill(pretoSuave)
        for estrela in estrelas:
            estrela["y"] += estrela["vel"]
            if estrela["y"] > alturaTela:
                estrela["y"] = random.randint(-10, 0)
                estrela["x"] = random.randint(0, larguraTela)
            pygame.draw.circle(tela, brancoPuro, (int(estrela["x"]), int(estrela["y"])), estrela["raio"])

        fundoY += velocidadeMetros * 5
        if fundoY >= fundoAltura:
            fundoY = 0
        tela.blit(fundoJogo, (0, fundoY - fundoAltura))
        tela.blit(fundoJogo, (0, fundoY))

        for inimigo in inimigos: tela.blit(inimigoImg, (inimigo["x"], inimigo["y"]))
        for tiro in tiros: tela.blit(tiroImagem, (tiro.x, tiro.y))
        for caixa in caixas: tela.blit(caixaMisteriosa, (caixa["x"], caixa["y"]))

        if etVisivel: tela.blit(etImagem, (etX, etY))

        for particle in particles[:]:
            if particle.move():
                particles.remove(particle)
            else:
                particle.draw(tela)

        if invencivel and int((tempoAtual*5)%2) == 0:
            tempSurf = pygame.Surface(naveJogador.get_size(), pygame.SRCALPHA)
            tempSurf.blit(naveJogador, (0,0))
            tempSurf.set_alpha(100 + 50 * (math.sin(tempoAtual * 10) + 1))
            tela.blit(tempSurf, (posicaoNaveX, posicaoNaveY))
        else:
            tela.blit(naveJogador, (posicaoNaveX, posicaoNaveY))

        textoMetros = fontePequena.render(f"METROS: {int(metros)}", True, brancoPuro)
        tela.blit(textoMetros, (10, 10))

        textoVidas = fontePequena.render(f"VIDAS: {vidas}", True, brancoPuro)
        tela.blit(textoVidas, (10, 40))

        if temEspecial:
            textoEspecial = fonteMenor.render("ESPECIAL PRONTO", True, brancoPuro) 
            tela.blit(textoEspecial, (10, 70))

        desenhar_barra_municao(tela, municaoRestante, maxMunicao, municaoRecarregando, ultimoTempoTiro, tempoEspera)

        pygame.display.flip()
        clock.tick(60)

    if not should_exit_game:
        tempo_fim_jogo = time.time()
        duracao_jogo = tempo_fim_jogo - tempo_inicio_jogo
        
        escreverDados(nome, int(metros), duracao_jogo)

        jogarNovamente = tela_morte(tela, nome, int(metros))
        if jogarNovamente:
            jogo(nome)


if __name__ == "__main__":
    inicializarBancoDeDados()
    tela = pygame.display.set_mode((larguraTela, alturaTela))
    try:
        pygame.font.Font(caminhoFonte, 10)
    except FileNotFoundError:
        print(f"Certifique-se de que '{caminhoFonte}' está na pasta 'Arquivos'.")

    mic_thread = threading.Thread(target=listen_for_exit_command, daemon=True)
    mic_thread.start()

    nomeJogador = tela_capa(tela)
    
    if not should_exit_game:
        if nomeJogador: 
            jogo(nomeJogador)
        else:
            print("Jogo encerrado a partir da tela de capa (nome não fornecido ou saída precoce).") 
    else:
        print("Jogo encerrado por comando de voz ou ESC/QUIT.") 

    if should_exit_game:
        pygame.quit()
        exit()