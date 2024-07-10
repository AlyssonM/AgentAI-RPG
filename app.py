from telebot import TeleBot
from os import environ
from command_handlers.game_commands import setup_game_handlers
from command_handlers.interaction_commands import setup_interaction_handlers

bot = TeleBot(environ.get("BOT_TOKEN"))

# Setup command handlers
setup_game_handlers(bot)
setup_interaction_handlers(bot)

def main():
    bot.polling()

if __name__ == "__main__":
    main()
