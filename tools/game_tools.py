from crewai_tools import tool
from langchain.agents import tool
import google.generativeai as genai
import telebot
from telebot import apihelper
from os import environ
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')
chat = model.start_chat(history=[])
apihelper.SESSION_TIME_TO_LIVE = 60*5

class TelegramTools:
    def __init__(self, bot):
        self.bot = bot
        
    @tool
    def group_send_message(self, chat_id:str, response:str) -> str:
        """function to interact with players in the telegram chat. must be passed two arguments chat_id and response. """
        try:
            self.bot.send_message(chat_id, response, parse_mode='Markdown')
        except Exception as inst:
            print(inst)
        return response
            
    @tool
    def private_send_message(self, user_id, response:str) -> str:
        """function to send messages to players in the telegram chat."""
        try:
            self.bot.send_message(user_id, response, parse_mode='Markdown')
        except Exception as inst:
            print(inst)
        return response
    
class DialogueManager:
    def __init__(self, user_character_map):
        self.conversation_history = []
        self.responses = []
        self.current_question_index = 0
        self.user_character_map = user_character_map
    
    def add_conversation_message(self, chat_id, message):
        character = self.get_character_by_chat_id(chat_id)
        self.conversation_history.append({'role': character, 'message': message})

    def get_full_context(self):
        # Concatena todas as mensagens para formar o contexto completo
        return "\n".join(f"{msg['role'].title()}: {msg['message']}" for msg in self.conversation_history)
     
class StorytellerTools:
    def __init__(self, llm):
        self.llm = llm  # Langchain LLM ou qualquer outra ferramenta de geração de linguagem que você está usando

    def describe_environment(self, description):
        """ Generate a detailed description of the current environment. """
        #description = self.llm.generate(f"Descreva um {location} em um mundo de fantasia RPG.")
        return description

    def react_to_action(self, action):
        """ Generate a narrative based on player action. """
        reaction = self.llm.generate(f"Descreva a consequência de {action} em um mundo de fantasia RPG.")
        return reaction

    def character_dialogue(self, character, player_input):
        """ Generate dialogue for an NPC based on their personality and player input. """
        dialogue = self.llm.generate(f"Como {character['name']}, um {character['type']}, responderia a '{player_input}'?")
        return dialogue

    def dynamic_event(self, event):
        """ Create a description for a dynamic event that affects the course of the game. """
        event_description = self.llm.generate(f"Narrar um evento de {event} em um mundo de fantasia RPG.")
        return event_description
              