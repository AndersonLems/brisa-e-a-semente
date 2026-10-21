# Brisa e a Semente Ancestral

Aventura 2D de plataforma (no estilo Super Mario World) com elementos de RPG, feita em
Python + pygame-ce. Roda nativamente no Linux, sem navegador. Todos os gráficos e sons são
gerados por código, então o jogo não precisa de nenhum arquivo de imagem ou áudio.

## Como jogar

```bash
./jogar.sh          # instala o pygame-ce se faltar e abre o jogo
# ou
python3 main.py
```

| Tecla | Ação |
|---|---|
| Setas / A D | Andar |
| Shift | Correr |
| Z / Espaço | Pular (segure para pular mais alto) |
| X | Golpe de cajado (também quebra pedras rachadas e abre baús) |
| C | Rajada de Vento (magia, a partir do nível 2) |
| Baixo + Pulo | Descer de plataformas finas |
| Cima | Conversar com NPCs / abrir a loja |
| 1 / 2 | Poção de Vida / Elixir de Mana |
| Esc / P | Pausa e ficha de status |
| F11 | Tela cheia |

Também dá para jogar com controle (gamepad).

## RPG

- **XP e níveis:** derrotar inimigos e pegar cristais roxos dá experiência. Cada nível aumenta
  HP, MP e ataque; nos níveis ímpares a defesa também sobe.
- **Poderes:** Rajada de Vento (Nv 2), Pulo Duplo (Nv 3), Rajada Tripla (Nv 5).
- **Loja do Seu Tatu:** gaste sementes douradas em poções, vidas e equipamentos permanentes.
- **Totens:** funcionam como checkpoint e restauram HP/MP.
- **Salvamento:** o jogo salva ao concluir cada fase, em `~/.local/share/brisa-jogo/save.json`.

## Estrutura do código

```
main.py                 ponto de entrada
jogo/
  game.py               Game: janela, loop, pilha de cenas, transições
  config.py, util.py    constantes e funções auxiliares
  input.py              teclado/controle -> ações
  audio.py              síntese de efeitos e músicas chiptune
  camera.py             câmera com suavização, limites e tremor
  entities/
    entity.py           Entity -> PhysicsEntity (gravidade e colisão)
    creature.py         Creature (vida, dano, invencibilidade, sprite)
    player.py           Player(Creature): Brisa
    enemies.py          Enemy(Creature) -> Walker -> Sauva, Besouro
                                       -> Lodo -> Brasinha
                                       -> Carcara -> Morcego
                                       -> Espinhoso
    boss.py             Boitata(Enemy): chefe com máquina de estados
    items.py            Item -> SeedCoin, HeartFruit, ManaFlower, XPCrystal, AncestralSeed
    projectiles.py      Projectile -> WindBolt, Thorn, Fireball
    npc.py              NPC -> TreeSpirit, Capybara, Merchant
    objects.py          WorldObject -> Checkpoint, Goal; MovingPlatform
    particles.py        Particle -> Spark, FloatingText; ParticleSystem
  world/
    tiles.py            Tile -> GroundTile, OneWayTile, BumpableTile -> BrickTile, ChestTile,
                                HazardTile -> SpikeTile, LavaTile
    tileset.py          gera os gráficos dos tiles
    background.py       fundos com parallax por bioma
    themes.py           paletas de cores
    levels.py           mapas em ASCII (fácil de editar!) + falas dos NPCs
    level.py            Level: carrega o mapa e resolve colisões/interações
  rpg/
    stats.py            nível, XP, atributos e habilidades
    items.py            RPGItem -> Consumable / Equipment / ExtraLife
    inventory.py        inventário
    progress.py         progresso e save em JSON
  ui/                   HUD, caixa de diálogo, menus
  scenes/               Scene -> Title, Story, Play, Pause, Shop, LevelComplete, GameOver, Victory
```

## Criando fases

Edite os mapas em `jogo/world/levels.py`. Cada caractere é um tile ou uma entidade (a legenda
está no topo do arquivo). Para adicionar uma fase nova, crie outro `LevelData` na lista `LEVELS`.
