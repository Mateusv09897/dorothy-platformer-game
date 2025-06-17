# -*- coding: utf-8 -*-
import pgzrun

LARGURA = 800
ALTURA = 600
TITULO = "Dorothy escapa de OZ"
GRAVIDADE = 0.8

estado_jogo = 'menu'
jogador_no_chao = False
temporizador_animacao = 0
som_ligado = True
botao_em_foco = None

jogador = Actor('dorothy_idle_1')
jogador.idle_frames = ['dorothy_idle_1', 'dorothy_idle_2', 'dorothy_idle_3', 'dorothy_idle_4']
jogador.walk_frames = ['dorothy_walk_1', 'dorothy_walk_2', 'dorothy_walk_3', 'dorothy_walk_4', 'dorothy_walk_5', 'dorothy_walk_6', 'dorothy_walk_7', 'dorothy_walk_8']
jogador.jump_frames = ['dorothy_jump_1', 'dorothy_jump_2', 'dorothy_jump_3', 'dorothy_jump_4', 'dorothy_jump_5', 'dorothy_jump_6', 'dorothy_jump_7', 'dorothy_jump_8']

plataformas = []
cristais = []
inimigos = []
objetivo = Actor('balloon') 

botao_iniciar = Rect((LARGURA/2 - 150, 250), (300, 50))
botao_som = Rect((LARGURA/2 - 150, 320), (300, 50))
botao_sair = Rect((LARGURA/2 - 150, 390), (300, 50))
botao_jogar_novamente = Rect((LARGURA/2 - 150, ALTURA/2 + 50), (300, 50))

COR_BOTAO = (210, 180, 140)
COR_BOTAO_FOCO = (245, 222, 179)
COR_BORDA_BOTAO = (139, 69, 19)

def reiniciar_nivel():
    global plataformas, cristais, inimigos, temporizador_animacao

    plataformas.clear(); cristais.clear(); inimigos.clear()
    temporizador_animacao = 0
    jogador.pos = (100, ALTURA - 100); jogador.vy = 0
    jogador.visible = True 

    CHAO_Y = ALTURA - 52 
    for x in range(50, LARGURA, 128):
        plataformas.append(Actor('blocos_terra', (x, ALTURA - 20)))

    plataformas.append(Actor('pedra_grama', (250, 500)))
    plataformas.append(Actor('pedra_grama', (450, 420)))
    plataformas.append(Actor('pedra_grama', (250, 340)))
    plataformas.append(Actor('pedra_grama', (550, 260)))
    plataformas.append(Actor('pedra_grama', (700, 180)))
    
    cristais.append(Actor('diamante_normal', (450, 380)))
    cristais.append(Actor('diamante_normal', (250, 300)))
    cristais.append(Actor('diamante_normal', (700, 140)))
    
    objetivo.image = 'balloon'
    objetivo.x = 700; objetivo.bottom = CHAO_Y 
    
    morcego = Actor('bat_up', (500, 380)); morcego.vx = 2
    inimigos.append(morcego)

    caracol = Actor('caracol_normal')
    caracol.x = 450; caracol.bottom = CHAO_Y 
    caracol.vx = 0.5 
    caracol.patrol_left = 300; caracol.patrol_right = 500
    inimigos.append(caracol)

def atualizar_jogador_e_fisica():
    global jogador_no_chao
    if keyboard.left or keyboard.a: jogador.x -= 5
    elif keyboard.right or keyboard.d: jogador.x += 5

    if jogador.left < 0:
        jogador.left = 0
    if jogador.right > LARGURA:
        jogador.right = LARGURA

    jogador.vy += GRAVIDADE; jogador.y += jogador.vy
    
    jogador_no_chao = False
    for plataforma in plataformas:
        if jogador.colliderect(plataforma) and jogador.vy >= 0:
            jogador.bottom = plataforma.top; jogador.vy = 0; jogador_no_chao = True
    
    if (keyboard.space or keyboard.up) and jogador_no_chao:
        jogador.vy = -15
        if som_ligado: sounds.jump.play()

def atualizar_animacoes():
    global temporizador_animacao
    temporizador_animacao += 1

    if not jogador_no_chao:
        if jogador.vy < 0: 
            total_frames_pulo = len(jogador.jump_frames)
            vy_normalizado = min(1, abs(jogador.vy) / 15)
            progresso_frame = 1 - vy_normalizado
            indice_frame = int(progresso_frame * (total_frames_pulo - 1))
            jogador.image = jogador.jump_frames[indice_frame]
        else: 
            jogador.image = jogador.jump_frames[-1]
    elif keyboard.left or keyboard.right or keyboard.a or keyboard.d:
        indice_frame = (temporizador_animacao // 6) % len(jogador.walk_frames)
        jogador.image = jogador.walk_frames[indice_frame]
    else:
        indice_frame = (temporizador_animacao // 15) % len(jogador.idle_frames)
        jogador.image = jogador.idle_frames[indice_frame]

    for inimigo in inimigos:
        indice_frame_rapido = (temporizador_animacao // 10) % 2
        if 'bat_up' in inimigo.image or 'bat_down' in inimigo.image:
            inimigo.image = 'bat_up' if indice_frame_rapido == 0 else 'bat_down'
        elif 'caracol_normal' in inimigo.image or 'caracol_movimento' in inimigo.image:
            inimigo.image = 'caracol_normal' if indice_frame_rapido == 0 else 'caracol_movimento'

    for cristal in cristais:
        indice_frame_lento = (temporizador_animacao // 20) % 2
        cristal.image = 'diamante_normal' if indice_frame_lento == 0 else 'diamante_brilho'

def atualizar_logica_jogo():
    global estado_jogo
    
    for inimigo in inimigos:
        inimigo.x += inimigo.vx
        if hasattr(inimigo, 'patrol_left'):
            if inimigo.left < inimigo.patrol_left or inimigo.right > inimigo.patrol_right: inimigo.vx *= -1
        else:
            if inimigo.right > LARGURA or inimigo.left < 0: inimigo.vx *= -1

    for cristal in cristais[:]:
        if jogador.colliderect(cristal):
            cristais.remove(cristal)
            if som_ligado: sounds.pickupcoin.play()

    if not cristais:
        if jogador.colliderect(objetivo):
            estado_jogo = 'victory_sequence'
            objetivo.image = 'voando' 
            jogador.visible = False 
            music.stop()
            if som_ligado: sounds.victory.play()

    for inimigo in inimigos:
        if jogador.colliderect(inimigo):
            if som_ligado: sounds.hithurt.play()
            reiniciar_nivel()

def atualizar_sequencia_vitoria():
    global estado_jogo
    objetivo.y -= 2
    if objetivo.bottom < 0:
        estado_jogo = 'win'

def desenhar_botao(rect, texto, nome):
    cor_preenchimento = COR_BOTAO_FOCO if botao_em_foco == nome else COR_BOTAO
    screen.draw.filled_rect(rect, cor_preenchimento)
    screen.draw.rect(rect, COR_BORDA_BOTAO)
    screen.draw.text(texto, center=rect.center, fontsize=35, color=COR_BORDA_BOTAO, bold=True)

def desenhar_menu():
    screen.clear(); screen.blit('background', (0, 0))
    screen.draw.text("Dorothy escapa de OZ", center=(LARGURA/2, 80), fontsize=70, color="yellow", owidth=1.5, ocolor="black", shadow=(2,2))
    frame_diamante = 'diamante_brilho' if (temporizador_animacao // 20) % 2 == 1 else 'diamante_normal'
    screen.blit(frame_diamante, (LARGURA/2 - 300, 55))
    jogador.image = jogador.idle_frames[(temporizador_animacao // 15) % len(jogador.idle_frames)]
    jogador.pos = (LARGURA/2, 200); jogador.draw()
    
    desenhar_botao(botao_iniciar, "Comecar Jogo", 'start')
    texto_som = "Som: LIGADO" if som_ligado else "Som: DESLIGADO"
    desenhar_botao(botao_som, texto_som, 'sound')
    desenhar_botao(botao_sair, "Sair", 'exit')

def desenhar_jogo():
    screen.clear(); screen.blit('background', (0, 0)) 
    for lista_objetos in [plataformas, cristais, inimigos]:
        for objeto in lista_objetos: objeto.draw()
    objetivo.draw()
    if jogador.visible:
        jogador.draw()
    if estado_jogo == 'win':
        screen.draw.text("Boa viagem de volta pra casa!", center=(LARGURA/2, ALTURA/2), fontsize=60, color="yellow", owidth=1.5, ocolor="darkred")
        desenhar_botao(botao_jogar_novamente, "Jogar Novamente", 'play_again')

def draw():
    if estado_jogo == 'menu':
        global temporizador_animacao
        temporizador_animacao += 1
        desenhar_menu()
    else: 
        desenhar_jogo()

def on_mouse_down(pos):
    global estado_jogo, som_ligado
    if estado_jogo == 'menu':
        if botao_iniciar.collidepoint(pos):
            estado_jogo = 'playing'; reiniciar_nivel()
            if som_ligado:
                music.play('cave_echoes'); music.set_volume(0.3)
        elif botao_som.collidepoint(pos):
            som_ligado = not som_ligado
            if som_ligado: sounds.pickupcoin.play()
        elif botao_sair.collidepoint(pos):
            exit()
    elif estado_jogo == 'win':
        if botao_jogar_novamente.collidepoint(pos):
            estado_jogo = 'menu'

def on_mouse_move(pos):
    global botao_em_foco
    if estado_jogo == 'menu':
        if botao_iniciar.collidepoint(pos): botao_em_foco = 'start'
        elif botao_som.collidepoint(pos): botao_em_foco = 'sound'
        elif botao_sair.collidepoint(pos): botao_em_foco = 'exit'
        else: botao_em_foco = None
    elif estado_jogo == 'win':
        if botao_jogar_novamente.collidepoint(pos):
            botao_em_foco = 'play_again'
        else:
            botao_em_foco = None
    else:
        botao_em_foco = None

def update():
    if estado_jogo == 'playing':
        atualizar_jogador_e_fisica()
        atualizar_animacoes()
        atualizar_logica_jogo()
    elif estado_jogo == 'victory_sequence':
        atualizar_sequencia_vitoria()
