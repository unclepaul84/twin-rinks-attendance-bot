#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""
import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from pysondb import db

games_db = None

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print(update)

    if(query.data.startswith("ga_")):
        query_parts = query.data.split("_")
        game_id = int(query_parts[1])
        yes_no = query_parts[2]

        player_record = games_db.getBy({"chat_id":query.from_user.id})

        if (player_record):
            game_record = next((x for x in player_record[0]["games"] if x["game_id"] == game_id), None)

            if(game_record):
                game_record["going"] = yes_no.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
                games_db.update({"chat_id":query.from_user.id},player_record[0]) # {"going":yes_no.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']})
                await query.edit_message_text(text=f'{game_record["description"]}\n Your response: {yes if game_record["going"] else no}')

    await query.answer()


 
def generateGames(game_record):
    game_record["games"]=[]
    for x in range(6):
        game_record["games"].append({"game_id": x + 1, "description": f'Thur Dec {x + 1} - BLUE VS GRAY', "going": False })

yes = "✅"
no = "❌"
async def list_game_attendance_approval(game_record, update):
    print(game_record)
    for g in game_record["games"]:
        await update.message.reply_text(f'Please confirm attendance: {g["description"]}\ current response: {yes if g["going"] else no}', reply_markup = build_attendance_buttons_markup(g))

def build_attendance_buttons_markup(game):
    keyboard = [
                    [
                        InlineKeyboardButton(yes, callback_data=f'ga_{game["game_id"]}_yes'),
                        InlineKeyboardButton(no, callback_data=f'ga_{game["game_id"]}_no')
                    ]    
                ]

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'{update.message.from_user.first_name}, Welcome to TwinRinks bot!\n Check out the menu for actions.')

async def games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_games = games_db.getBy({"chat_id":update.message.chat.id})
    
    if(user_games):
        await list_game_attendance_approval(user_games[0],update)
    else:
        new_game_record = {"chat_id":update.message.chat.id}
        generateGames(new_game_record)
        games_db.add(new_game_record)  
        await list_game_attendance_approval(new_game_record,update)

command_info = [
    BotCommand("start", "Initialize the bot"),
    BotCommand("games", "List available games"),
]



async def post_init(application: Application) -> None:
    bot = application.bot
    await bot.set_my_commands(commands=command_info)

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("BOT_TOKEN")) .post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("games", games))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    games_db = db.getDb('games_db.json')
    main()