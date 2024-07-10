from database.database import Database, Character
from tools.game_tools import TelegramTools
from crewai import Crew, Process
from agents.game_agents import Agents
from tasks.game_tasks import GameMasterTasks, ArchivistTasks, BardTasks
import re
import json

class GameManager:
    def __init__(self, db_url):
        self.db = Database(db_url)
        self.game_state = {
            "theme": "",
            "current_chapter_index": 0,
            "game_history": [{
                "chapter_title": "",
                "events": [{
                    "event_id": 1,
                    "user_id": "",
                    "description": "",
                    "choices": [
                        {"choice_id": 1, "text": ""},
                        {"choice_id": 2, "text": ""},
                        {"choice_id": 3, "text": ""},
                    ],
                    "results": [{
                        "decision": "",
                        "consequence": "",
                        "stats_change": {
                            "strength": 0,
                            "intelligence": 0,
                            "agility": 0,
                            "magic": 0
                        }    
                    }]
                }]
            }],
        }  # JSON para o estado do game
        self.game_cache = {}
    
    def get_game_state(self, chat_id):
        # Verifica se o estado já está no cache
        if chat_id in self.game_cache:
            print("Retrieving state from cache.")
            return self.game_cache[chat_id]

        # Se não estiver no cache, carrega do DB e salva no cache
        state = self.db.get_game_state(chat_id)
        if state:
            self.game_cache[chat_id] = state
            print("Loaded state from DB and saved to cache.")
        return state
      
    def initialize_game_state(self, chat_id, theme, title, description):
        game_state = {
            "theme": theme,
            "current_chapter_index": 0,
            "game_history": [{
                "chapter_title": title,
                "events": [{
                    "event_id": 1,
                    "user_id": chat_id,
                    "description": description,
                    "choices": [],
                    "results": []
                }]
            }]
        }
        return game_state
    
    def handle_new_game(self, chat_id, user_id, theme, bot):
        # Implementação da lógica para iniciar um novo jogo
        agents = Agents(True)
        game_master = agents.creator_agent()
        game_master_task = GameMasterTasks(game_master).create_game_world(
            [TelegramTools(bot).group_send_message],
            chat_id,
            theme,
            [],
            []
        )
        crew = Crew(
            agents=[game_master],
            tasks=[game_master_task],
            verbose=True
        )
        result = crew.kickoff()
        
        # Preparar o estado do jogo como um dicionário
        game_state = self.initialize_game_state(chat_id, theme, "The adventure begins!", result)
        # Salvar o estado do jogo no banco de dados
        self.db.save_game(chat_id, theme, game_state)
        # Envia a descrição do game para o chat
        #bot.send_message(chat_id, "Novo jogo iniciado com o tema: " + theme + "\n Descrição do jogo: \n" + result, parse_mode='Markdown')


    def handle_join_game(self, chat_id, user_id, bot):
        game_state = self.get_game_state(chat_id)
        # Implementação da lógica para um usuário entrar em um jogo
        if game_state:
            agents = Agents(True)
            game_archivist = agents.charmanager_agent()
            game_archivist_task = ArchivistTasks(game_archivist).create_character(
                tools=[],
                chat_id=chat_id,
                user_id=user_id,
                game_state=game_state['game_history'],
                callback=[]
            )
            crew = Crew(
                agents=[game_archivist],
                tasks=[game_archivist_task],
                verbose=True
            )
            result = crew.kickoff()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)          # Captura o texto que corresponde ao JSON
                character_data = json.loads(json_str)   # Converte o texto JSON em um dicionário Python
            
                # Criação do personagem e salvando no banco de dados
                character = self.db.create_character(**character_data)
                bot.send_message(chat_id, f"{user_id} entrou no jogo.")
                character_info = "\n".join([f"{key}: {value}" for key, value in character_data.items()])
                #bot.send_message(user_id, f"Dados da personagem:\n{character_info}", parse_mode='Markdown')
            else:
                bot.send_message(user_id, f"Erro ao criar a personagem. Tente novamente.")
        else:
            bot.send_message(chat_id, f"Ainda não existe um game associado a este grupo. Execute o comando /game")
    
    def start_game_history(self, chat_id, user_id, bot):
        game_state = self.get_game_state(chat_id)
        if game_state:
            agents = Agents(True)
            game_bard = agents.storyteller_agent()
            game_bard_task = BardTasks(game_bard).narrate_event(
                tools=[TelegramTools(bot).group_send_message],
                chat_id=chat_id,
                user_id=user_id,
                game_chapter=game_state['game_history'][-1],
                event=f"Start the adventure of {user_id}",
                callback=[]
            )
            crew = Crew(
                agents=[game_bard],
                tasks=[game_bard_task],
                verbose=True
            )
            result = crew.kickoff()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)          # Captura o texto que corresponde ao JSON
                new_event = json.loads(json_str)   # Converte o texto JSON em um dicionário Python
                game_state['game_history'][-1]["events"].append(new_event) 
                self.db.save_game_state(chat_id, game_state)
    
    def new_game_event(self, chat_id, user_id, bot): 
        game_state = self.get_game_state(chat_id)
        if game_state:
            agents = Agents(True)
            game_bard = agents.storyteller_agent()
            game_bard_task = BardTasks(game_bard).narrate_event(
                tools=[TelegramTools(bot).group_send_message],
                chat_id=chat_id,
                user_id=user_id,
                game_chapter=game_state['game_history'][-1],
                event=f"Continue adventure of {user_id}",
                callback=[]
            )
            crew = Crew(
                agents=[game_bard],
                tasks=[game_bard_task],
                verbose=True
            )
            result = crew.kickoff()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)          # Captura o texto que corresponde ao JSON
                new_event = json.loads(json_str)   # Converte o texto JSON em um dicionário Python
                game_state['game_history'][-1]["events"].append(new_event) 
                self.db.save_game_state(chat_id, game_state)
            
    def handle_game_choice(self, chat_id, user_id, choice, bot):
        # Implementação da lógica para processar a escolha do jogador
        game_state = self.get_game_state(chat_id)
        if game_state:
            agents = Agents(True)
            game_bard = agents.storyteller_agent()
            game_bard_task = BardTasks(game_bard).action_event(
                tools=[],
                choice_id=choice,
                event_id=game_state['game_history'][-1]["events"][-1]["event_id"],
                callback=[]
            )
            crew = Crew(
                agents=[game_bard],
                tasks=[game_bard_task],
                verbose=True
            )
            result = crew.kickoff()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)          # Captura o texto que corresponde ao JSON
                new_result = json.loads(json_str)   # Converte o texto JSON em um dicionário Python
                print(new_result)
                game_state['game_history'][-1]["events"][-1]["results"] = new_result
                self.db.save_game_state(chat_id, game_state)
                self.db.update_character_stats(user_id, new_result['stats_change'])
                bot.send_message(chat_id, f"Decisão: {choice}\n{new_result['consequence']}")

    
   
    def send_character_details(self, bot, user_id):
        with self.db.session_scope() as session:
            # Busca os dados do personagem dentro do contexto da sessão
            character = session.query(Character).filter_by(user_id=user_id).first()
            if character:
                # Formata a mensagem
                message = (
                    f"**Personagem: {character.name}**\n"
                    f"Game ID: {character.game_id}\n"
                    f"Background: {character.background}\n"
                    f"Strength: {character.strength}\n"
                    f"Intelligence: {character.intelligence}\n"
                    f"Agility: {character.agility}\n"
                    f"Magic: {character.magic}\n"
                )
                # Envia a mensagem para o chat privado do usuário
                bot.send_message(user_id, message, parse_mode='Markdown')
            else:
                # Envia uma mensagem se nenhum personagem for encontrado
                bot.send_message(user_id, "Nenhum personagem encontrado para seu ID de usuário.")

    def send_game_resume(self, bot, chat_id, user_id):
        game_state = self.get_game_state(chat_id)
        if game_state:
            result_info = game_state['game_history'][-1]['events'][-1]["results"]
            results = (
                f"*Decisão Tomada:* {result_info['decision']}\n"
                f"*Consequência:* {result_info['consequence']}\n"
                f"*Mudança de Status:*\n"
                f"    - *Força:* {result_info['stats_change']['strength']}\n"
                f"    - *Inteligência:* {result_info['stats_change']['intelligence']}\n"
                f"    - *Agilidade:* {result_info['stats_change']['agility']}\n"
                f"    - *Magia:* {result_info['stats_change']['magic']}\n"
            )
            resume_info = (
                f"*Capítulo*: \n{game_state['game_history'][-1]['chapter_title']}\n"
                f"*Evento*: \n{game_state['game_history'][-1]['events'][-1]['description']}\n"
                f"*Resultado*: \n{results}\n"
            )
            print(game_state['game_history'][-1]['events'])
            bot.send_message(user_id, resume_info, parse_mode="Markdown")
            
            
