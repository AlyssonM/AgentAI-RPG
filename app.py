from telebot import TeleBot
from telebot import apihelper
from os import environ
from command_handlers.game_commands import setup_game_handlers
from command_handlers.interaction_commands import setup_interaction_handlers

apihelper.SESSION_TIME_TO_LIVE = 60*5
bot = TeleBot(environ.get("BOT_TOKEN"))

# Setup command handlers
setup_game_handlers(bot)
setup_interaction_handlers(bot)

def main():
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    main()
