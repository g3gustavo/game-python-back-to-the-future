# Back to the Future: Time Crisis

Jogo em Python inspirado em `Back to the Future`, desenvolvido usando PyGame Community Edition. O projeto implementa mecânicas de plataforma, tiro, fases temáticas, coleta de itens e um sistema simples de pontuação com persistência em SQLite.

## Visão Geral

- `main.py` é o ponto de entrada do jogo.
- Estrutura modular com classes de `Player`, `Enemy`, `Boss`, `Projectile`, `Scenery` e `DatabaseProxy` em `models/`.
- Fases baseadas em épocas de `Back to the Future` com cenários e inimigos diferentes.
- Áudio e efeitos sonoros carregados em tempo de execução via `sons/`.
- Recursos gráficos e sprites esperados em `assets/`.
- Persistência de recordes na base `highscores.db` via SQLite.

## Tecnologias Utilizadas

- Python 3
- PyGame Community Edition (`pygame-ce`)
- SQLite3
- PyInstaller (presente no repositório gerado, já que há `main.spec` e `build/`)

## Instalação

1. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Atualize o pip e instale dependências:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Execute o jogo:

```powershell
python main.py
```

## Estrutura do Projeto

- `main.py` - loop principal do jogo, carregamento de recursos, telas e lógica do jogo.
- `requirements.txt` - dependências do projeto.
- `models/` - classes e lógica de entidades do jogo:
  - `characters.py` - jogador, inimigos e chefe.
  - `database.py` - proxy de banco de dados SQLite para recordes.
  - `entity.py` - classe base de entidade.
  - `factory.py` - fábrica de inimigos.
  - `projectile.py` - tiros do jogador.
  - `scenery.py` - itens colecionáveis e torre do relógio.
- `assets/` - imagens e sprites utilizadas no jogo.
- `sons/` - arquivos de áudio e efeitos sonoros.
- `build/` - saída gerada de pacote/compilação.

## Como Jogar

- `ENTER` - iniciar jogo / reiniciar.
- `A` / `D` - mover para os lados.
- `W` - pular.
- `SPACE` - atirar.

## Observações

- Se usar Windows PowerShell e encontrar erro ao ativar o ambiente virtual, execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

- Se as imagens ou sons não estiverem na pasta `assets/` e `sons/`, o jogo pode exibir mensagens de erro ao carregar recursos.

---

Desfrute do jogo e sinta-se à vontade para expandir novas fases, inimigos e mecânicas de progresso!