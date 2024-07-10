# AgentAI-RPG

O projeto AgentAI-RPG é um sistema interativo de jogo de RPG (Role-Playing Game) que integra agentes de inteligência artificial para gerenciar e evoluir a narrativa do jogo. Este sistema é projetado para ser executado através do Telegram, proporcionando uma plataforma acessível e fácil de usar para jogadores interagirem com o jogo.

## Funcionalidades

- **Criação Dinâmica de Mundo**: Utiliza agentes AI para criar descrições detalhadas de mundos, incluindo geografia, cultura e história.
- **Interatividade com Jogadores**: Os jogadores podem tomar decisões que influenciam diretamente o desenvolvimento da história.
- **Gestão de Personagens**: Sistema para criar e gerenciar as características dos personagens dos jogadores.
- **Resposta a Escolhas**: O sistema analisa as escolhas dos jogadores e calcula as consequências, balanceando resultados positivos e negativos.

## Tecnologias Utilizadas

- **Python**: Linguagem principal de programação.
- **Telebot**: Biblioteca para criação de bots do Telegram.
- **SQLAlchemy**: ORM para manipulação de banco de dados.
- **CrewAI**: Framework para integração de agentes de AI na lógica do jogo.

## Estrutura do Projeto

O projeto é dividido em várias partes principais:

- **game_logic**: Contém a lógica central do jogo, incluindo a criação do mundo, gestão de personagens e processamento de escolhas.
- **database**: Módulo para manipulação do banco de dados, incluindo definição de modelos e operações de banco de dados.
- **commands**: Handlers para comandos do Telegram que permitem aos jogadores interagir com o jogo.
- **agents**: Define os agentes AI utilizados para diversos aspectos do jogo.

## Configuração e Execução

Para configurar e executar o projeto, siga os passos abaixo:

1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/AlyssonM/AgentAI-RPG.git
   ```
2. **Configuração do Ambiente Virtual**

Recomenda-se criar um ambiente virtual para isolar as dependências do projeto:

# Instalação do ambiente virtual para Python 3
```bash
python -m venv venv
```
# Ativar o ambiente virtual
# No Windows
```bash
venv\Scripts\activate
```
# No Unix ou MacOS
```bash
source venv/bin/activate
```

3. **Instalação de Dependências**
Instale todas as dependências necessárias executando:

```bash
pip install -r requirements.txt
```

4. **Configuração do Bot do Telegram**
Para interagir com o Telegram, você precisa de um token de bot:

* Crie um bot conversando com o BotFather no Telegram e obtenha o token.
* Crie um arquivo .env na raiz do seu projeto e adicione seu token nele:

```bash
BOT_TOKEN='seu_token_aqui'
```

5. **Execução do Bot**
Uma vez configurado, inicie a aplicação com o seguinte comando:

```bash
python app.py
```
Agora o bot deve estar rodando e você pode interagir com ele através do Telegram enviando comandos como /game para iniciar um novo jogo.

**Usando o Bot**
Para interagir com o bot no Telegram:

* Envie /game nome_do_tema para iniciar um novo jogo.
* Use /join para entrar em um jogo existente.
* Envie /choice <escolha> para fazer uma escolha durante o jogo.

**Contribuições**
Contribuições são bem-vindas! Para contribuir, faça um fork do repositório, faça suas alterações e envie um pull request.

