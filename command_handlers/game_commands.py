from game_logic.game_manager import GameManager
from tools.game_tools import TelegramTools

def setup_game_handlers(bot):
    game_manager = GameManager('sqlite:///game.db')  # Cria uma instância de GameManager
    
    @bot.message_handler(commands=['game'])
    def game_command(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        theme = ' '.join(message.text.split()[1:])  # Assume que tema é o primeiro argumento após o comando
        game_manager.handle_new_game(chat_id, user_id, theme, bot)

    @bot.message_handler(commands=['join'])
    def join_game(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        game_manager.handle_join_game(chat_id, user_id, bot)
    
    
    @bot.message_handler(commands=['status'])
    def status_game(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        game_manager.send_character_details(bot, user_id)
        
    @bot.message_handler(commands=['resume'])
    def resume_game(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        game_manager.send_game_resume(bot, chat_id, user_id)
        
        
    @bot.message_handler(commands=['start'])
    def start_game(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        game_manager.start_game_history(chat_id, user_id, bot)
    
    @bot.message_handler(commands=['event'])
    def new_event(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        game_manager.new_game_event(chat_id, user_id, bot)
        
    # @bot.message_handler(func=lambda message: True)
    # def player_message(message):
    #     TelegramTools(bot).handle_text(message)