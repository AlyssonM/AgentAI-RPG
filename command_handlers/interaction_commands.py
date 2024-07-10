from game_logic.game_manager import GameManager

def setup_interaction_handlers(bot):
    game_manager = GameManager('sqlite:///game.db')  # Cria uma instância de GameManager
    
    @bot.message_handler(commands=['choice'])
    def choice_game(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        print(message)
        if len(message.text.split()) > 1:
            choice = ' '.join(message.text.split()[1:])  # Extrai a escolha do jogador
            game_manager.handle_game_choice(chat_id, user_id, choice, bot)
        else:
            bot.send_message(chat_id, "Você não especificou uma escolha. Tente novamente com /choice [opção]")

    