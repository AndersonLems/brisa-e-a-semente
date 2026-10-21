"""Dados das fases: mapas em ASCII + NPCs + configuração.

Legenda do mapa:
  #  terra/rocha          =  pedra rachada (quebrável)    -  plataforma atravessável
  ?  baú com semente      !  baú com fruta-coração         *  baú com flor-de-mana
  ^  espinhos             ~  lava
  o  semente dourada      h  fruta-coração   m  flor-de-mana   x  cristal de XP
  s  saúva    e  besouro    l  lodo    r  brasinha    b  carcará    v  morcego
  k  espinhoso (cacto)    B  Boitatá (chefe)
  P  início    N  NPC (na ordem da lista "npcs")    $  mercador
  C  totem (checkpoint)   F  portal de saída      M  plataforma móvel
"""


class LevelData:
    def __init__(self, name, subtitle, theme, music, rows, npcs=(), arena=None):
        self.name = name
        self.subtitle = subtitle
        self.theme = theme
        self.music = music
        self.rows = rows
        self.npcs = list(npcs)
        self.arena = arena  # (coluna_inicial, coluna_final) da arena do chefe


FASE_1 = [
    "",
    "",
    "",
    "",
    "",
    "",
    "               ooo",
    "                                                x                                                           b     =?=",
    "                                              -----      oo     b",
    "                                                                                                                 oooo                     o o o",
    "              ?=!=?                                      ##       ooo                   ?*?                          l             x",
    "         ooo                      ooo   -----           ####     -----                                          ##########    x",
    "                          ##                           ######                                  M               ############",
    "  P   N               s   ##  s             l         ########    ^^^   C   $       k                s   s    ##############            s        F",
    "##################################   ########################################################     ################################   #################",
    "##################################   ########################################################     ################################   #################",
    "##################################   ########################################################     ################################   #################",
]

FASE_2 = [
    "################################################################################################################################################################",
    "################################################################################################################################################################",
    "                    ###                   ##############                              #####",
    "                    ###                   ##############                              #####",
    "                     x                    ##############                              #####",
    "                                          ##############                              #####                                         v",
    "                                v         ##############                   v          #####",
    "                                          ##############                              #####                                               v",
    "                                          ##############     x                        #####                           oooh",
    "                                          ##############    ####                      #####                          -----",
    "            ?=?                                             ####                        =        *            M               =!=",
    "                           --                           --- ####         -- --          =                                              x x                F",
    "                                            oooooooo        ####                        =                 M                                    #################",
    "  P  N          e                     l           e         ####    C   ^^^^^^    k     =     e    e                        l   l             ##################",
    "##########################    ##########################################################################         ###############################################",
    "##########################    ##########################################################################         ###############################################",
    "##########################    ##########################################################################         ###############################################",
]

FASE_3 = [
    "                                                                                                                                                              ##",
    "                                                                                                                                                              ##",
    "                                                                                                                                                              ##",
    "                                                                                                                                                              ##",
    "                                                                                                           h                                                  ##",
    "                                                  b                                                       ---                                                 ##",
    "                                                                                                              b                                               ##",
    "                                              x                                                        x                                                      ##",
    "                                                                                   ooo                ---                                   ------            ##",
    "                                              ##                                                                                              B               ##",
    "          ?!?                                 ##                  =?=*=                                                                                       ##",
    "                                        ##    ##    ##                          M     M           ---                              ----                ----   ##",
    "                                        ##    ##    ##                                                                                                        ##",
    "  P   N                 k   r     e     ##    ##    ##    C   $       r   r                   k     e           r     C  N                                    ##",
    "################    ######################    ##    ##########################           ###############################################  ##########  ##########",
    "################~~~~######################~~~~##~~~~##########################~~~~~~~~~~~###############################################~~##########~~##########",
    "################~~~~######################~~~~##~~~~##########################~~~~~~~~~~~###############################################~~##########~~##########",
]


LEVELS = [
    LevelData(
        "Campos do Ipê", "Fase 1", "campo", "campo", FASE_1,
        npcs=[dict(type="espirito", name="Vovó Jacarandá", lines=[
            "Brisa! Que bom que você chegou, minha pequena Guardiã do Vento.",
            "O Boitatá, a serpente de fogo, roubou a Semente Ancestral do coração da Serra dos Ipês.",
            "Sem ela as flores murcham e os rios secam. Só você pode trazê-la de volta.",
            "Use Z ou ESPAÇO para pular, X para golpear com seu cajado e SHIFT para correr.",
            "Pule em cima dos inimigos ou golpeie-os. Cada vitória dá experiência (XP).",
            "Ao subir de nível você fica mais forte e desperta novos poderes do vento!",
            "Bata a cabeça nos baús dourados por baixo... e boa sorte, querida.",
        ])],
    ),
    LevelData(
        "Caverna dos Cristais", "Fase 2", "caverna", "caverna", FASE_2,
        npcs=[dict(type="capivara", name="Dona Capivara", lines=[
            "Psiu! Cuidado por aqui, mocinha. Esta caverna é cheia de surpresas.",
            "Os besouros de casca dura não sentem golpes. Pule neles para virá-los de costas e então ataque!",
            "Mais adiante há uma parede de pedra rachada. Seu cajado (X) dá conta dela.",
            "E dizem que quem tem o Pulo Duplo encontra tesouros nas alturas...",
        ])],
    ),
    LevelData(
        "Vulcão do Boitatá", "Fase 3", "vulcao", "vulcao", FASE_3,
        npcs=[
            dict(type="espirito", name="Vovó Jacarandá", lines=[
                "Brisa! Senti o vento te trazendo até aqui. Este é o lar do Boitatá.",
                "A lava queima, mas te arremessa para cima. Não entre em pânico: saia rápido!",
                "As brasinhas são quentes demais para pisar. Use o cajado ou a Rajada de Vento.",
            ]),
            dict(type="espirito", name="Vovó Jacarandá", lines=[
                "O covil do Boitatá fica logo à frente. Respire fundo.",
                "Depois de cada investida ele fica cansado no chão. É a sua chance de golpear!",
                "Fique de olho nas bolas de fogo. Quando ele se enfurecer, ficará mais rápido.",
                "O vento está com você, Guardiã!",
            ]),
        ],
        arena=(128, 158),
    ),
]
