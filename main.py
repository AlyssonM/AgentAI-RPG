from crewai import Crew, Process
from textwrap import dedent
from agents.game_agents import Agents
from tools.game_tools import TelegramTools, DialogueManager
from tasks.game_tasks import GameMasterTasks, BardTasks, ArchivistTasks
from database import Base, Database, Character, Equipment, Trait
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import environ
import telebot
import json
import re

bot = telebot.TeleBot(environ.get("BOT_TOKEN"))
game_registry = {}

def setup_database(db_url='sqlite:///game.db'):
    engine = create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)  # Cria as tabelas, se não existirem
    Session = sessionmaker(bind=engine)
    return Session  # Retorna a fábrica de sessão, não uma sessão
  
class GameCreation:
  def __init__(self, chat_id, theme, db):
    self.chat_id = chat_id
    self.db = db
    self.game_context = self.db.get_game(chat_id) or {}
    if 'rolling' not in self.game_context:
      self.game_context['rolling'] = ""
    self.characters = self.db.get_characters(chat_id) or {} #
    self.theme = theme
    self.dialog_manager = DialogueManager([])
    self.action_event = False
    
  def setup(self): 
    # Instanciação das ferramentas de Telegram e dos agentes 
    verbose = False
    self.telegram_tools = TelegramTools(bot)
    agents = Agents(verbose)
    self.game_master = agents.creator_agent()
    self.bard = agents.storyteller_agent()
    self.archivist = agents.charmanager_agent()
    
    # Criação das instâncias de tarefas
    self.game_master_task = GameMasterTasks(self.game_master).create_game_world(
      [],
      self.chat_id,
      self.theme,
      [],
      self.on_world_created
    )
    
  def on_world_created(self, output):
    print(f"""
        Task completed!
        Task: {output.description}
        Output: {output.raw_output}
    """)
    self.game_context['world_info'] = output.raw_output
    bot.send_message(self.chat_id, output.raw_output, parse_mode='Markdown')
  
  def on_character_created(self, output):
    json_match = re.search(r'\{.*\}', output.raw_output, re.DOTALL)
    if json_match:
      json_str = json_match.group(0)  # Captura o texto que corresponde ao JSON
      character_data = json.loads(json_str)  # Converte o texto JSON em um dicionário Python
      
      user_id = character_data['user_id']
      background = character_data['background']
      name = character_data['name']
      strength = character_data['initial_stats']['strength']
      agility = character_data['initial_stats']['agility']
      intelligence = character_data['initial_stats']['intelligence']
      magic = character_data['initial_stats']['magic']
      charisma = character_data['initial_stats']['charisma']
  
      character = self.db.create_character(user_id, name, background, strength, intelligence, agility, magic, charisma)
      if character:
          print(f"Character {character.name} created successfully in the database.")
      else:
          print("Failed to create character in the database.")
  
  def on_event_action(self, output):
    self.action_event = True
    self.game_context['rolling'] += "\n" + output.raw_output
    self.db.save_character(self.chat_id, self.game_context, self.characters)
    try:
      bot.send_message(self.chat_id, output.raw_output, parse_mode='Markdown')
    except Exception as error:
      print("An exception occurred:", error)
  
  def on_choice_action(self, output):
    self.game_context['rolling'] += "\n" + output.raw_output
    self.db.save_character(self.chat_id, self.game_context, self.characters)
    try:
      bot.send_message(self.chat_id, output.raw_output, parse_mode='Markdown')
    except Exception as error:
      print("An exception occurred:", error)
      
  def print_game_context(self):
    print(self.game_context['rolling'])  
    
  def get_active_users(self):
        # Retorna a lista de IDs dos usuários que se registraram para jogar
        return self.user_ids

  def add_user(self, user_id, character_info):
    json_match = re.search(r'\{.*\}', character_info, re.DOTALL)
    if json_match:
      json_str = json_match.group(0)  # Captura o texto que corresponde ao JSON
      character_data = json.loads(json_str)  # Converte o texto JSON em um dicionário Python
      print(character_data)
      self.characters[user_id] = character_data #
      self.game_context[f"{user_id}"] = character_data
      self.db.save_character(self.chat_id, self.game_context, self.characters) #
   
  def create(self):
    crew = Crew(
      agents=[self.game_master],
      tasks=[self.game_master_task],
      verbose=True
    )
    result = crew.kickoff()
    return result
  
  
  def join(self, user_id):
    player_info = self.game_context['world_info']  # Informações do mundo
    if user_id not in self.characters:
      self.archivist_task = ArchivistTasks(self.archivist).create_character(
        [],
        user_id,
        player_info,  # Passando world_data como player_info
        [self.game_master_task],
        self.on_character_created,
      )
      crew = Crew(
        agents=[self.archivist],
        tasks=[self.archivist_task],
        process=Process.sequential,
        verbose=True
      )
      result = crew.kickoff()
      self.add_user(user_id, result)
      return result
    else:
      bot.send_message(user_id, f"Usuário {user_id} já registrado no game {self.chat_id}")

  def start(self):
    self.bard_task = BardTasks(self.bard).narrate_event(
      [],
      self.chat_id,
      self.game_context,
      "Start adventure!",
      self.on_event_action,
    )
    crew = Crew(
        agents=[self.bard],
        tasks=[self.bard_task],
        verbose=True
      )
    result = crew.kickoff()
    return result
  
  def event(self):
    self.bard_task = BardTasks(self.bard).narrate_event(
      [],
      self.chat_id,
      self.game_context,
      "New action event",
      self.on_event_action,
    )
    crew = Crew(
        agents=[self.bard],
        tasks=[self.bard_task],
        verbose=True
      )
    result = crew.kickoff()
    return result
  
  def status(self, user_id):
    return self.db.get_character_by_user_id(user_id)
  
  def handle_game_choice(self, choice):
    if self.action_event:
      self.game_context['rolling'] += "\n" + "Choice: " + choice
      self.db.save_character(self.chat_id, self.game_context, self.characters)
      self.bard_task = BardTasks(self.bard).action_event(
        [],
        self.chat_id,
        choice,
        self.game_context,
        self.on_choice_action,
      )
      crew = Crew(
          agents=[self.bard],
          tasks=[self.bard_task],
          verbose=True
        )
      result = crew.kickoff()
      return result
    
def handle_game_command(message):
    chat_id = message.chat.id
    command, *args = message.text.split()
    theme = ' '.join(args)
    if chat_id not in game_registry:
        game = GameCreation(chat_id, theme, db)
        saved_game = db.get_game(chat_id)
        if not saved_game:  # Verifica se há um jogo salvo
            game.setup()  # Configura o jogo apenas se não existir um salvo
            game.create()
            game.db.save_game(chat_id, game.game_context)
        game_registry[chat_id] = game
    else:
       game = game_registry[chat_id]

    
# Configuração do comando /game
@bot.message_handler(commands=['game'])
def game_command(message):
    handle_game_command(message)

# Configuração do comando /join
@bot.message_handler(commands=['join'])
def join_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    saved_character = db.get_character_by_user_id(user_id) #
    if not saved_character:
        game = game_registry.get(chat_id)
        game.setup()
        game.join(user_id)
    else:
        bot.send_message(user_id, f"user {user_id} already joined the game!")
    
# Configuração do comando /start
@bot.message_handler(commands=['start'])
def start_game(message):
  chat_id = message.chat.id
  user_id = message.from_user.id
  game = game_registry.get(chat_id)
  if game:
    game.setup()
    game.start()

# Configuração do comando /status        
@bot.message_handler(commands=['status'])
def status_game(message):
  chat_id = message.chat.id
  user_id = message.from_user.id
  game = game_registry.get(chat_id)
  game.print_game_context()
  if game:
    character = game.status(user_id)
    if character:
            # Formata a mensagem de status usando Markdown
            status_msg = (f"*ID:* `{character.id}`\n"
                          f"*User ID:* `{character.user_id}`\n"
                          f"*Name:* `{character.name}`\n"
                          f"*Background:* `{character.background}`\n"
                          f"*Strength:* `{character.strength}`\n"
                          f"*Intelligence:* `{character.intelligence}`\n"
                          f"*Agility:* `{character.agility}`\n"
                          f"*Magic:* `{character.magic}`\n"
                          f"*Charisma:* `{character.charisma}`\n")
            bot.send_message(user_id, status_msg, parse_mode='Markdown')
    else:
            bot.send_message(user_id, "No character found with that user ID.")
  else:
      bot.send_message(user_id, "No game found for this chat. Start a game using /game.")

# Configuração do comando /choice
@bot.message_handler(commands=['choice'])
def choice_game(message):
  chat_id = message.chat.id
  user_id = message.from_user.id
  command, *args = message.text.split()
  choice = ' '.join(args)
  game = game_registry.get(chat_id)
  if game:
    game.setup()
    game.handle_game_choice(choice)
  
# Configuração do comando /event
@bot.message_handler(commands=['event'])  
def new_event_game(message):
  chat_id = message.chat.id
  user_id = message.from_user.id
  game = game_registry.get(chat_id)
  if game:
    game.setup()
    game.event()

def main():
  Session = setup_database()  # Recebe a fábrica de sessão
  session = Session()  # Cria uma instância de sessão usando a fábrica
  global db
  db = Database(session)  # Passa a sessão para o construtor de Database
  bot.polling()

if __name__ == "__main__":
  main()

  