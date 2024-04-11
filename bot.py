import argparse
import logging
import os
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackContext
from telegram.ext.filters import TEXT
from functools import partial


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Функция для загрузки списка ключевых слов
def load_keywords() -> None:
    try:
        with open("keywords.txt", "r") as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()


# Функция для сохранения списка ключевых слов
def save_keywords(keywords) -> None:
    with open("keywords.txt", "w") as file:
        for keyword in keywords:
            file.write(keyword + "\n")


# Функция для загрузки списка авторизованных пользователей
def load_users() -> None:
    try:
        with open("users.txt", "r") as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()


# Функция для сохранения списка авторизованных пользователей (по юзернеймам)
def save_users(users) -> None:
    with open("users.txt", "w") as file:
        for user in users:
            file.write(user + "\n")


# Проверка, является ли пользователь авторизованным
def is_user_authorized(username) -> bool:
    return username.lower() in load_users()


# Команда для добавления ключевого слова
async def add_keyword(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not is_user_authorized(username):
        await update.message.reply_text("У вас нет прав для добавления ключевых слов.")
        return
    print(context.args)
    keyword = ' '.join(context.args)
    if not keyword:
        await update.message.reply_text("Пожалуйста, укажите ключевое слово для добавления.")
        return
    keywords = load_keywords()
    keywords.add(keyword)
    save_keywords(keywords)
    await update.message.reply_text(f"Ключевое слово '{keyword}' добавлено.")


# Команда для удаления ключевого слова
async def remove_keyword(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not is_user_authorized(username):
        await update.message.reply_text("У вас нет прав для удаления ключевых слов.")
        return
    keyword = ' '.join(context.args)
    if not keyword:
        await update.message.reply_text("Пожалуйста, укажите ключевое слово для удаления.")
        return
    keywords = load_keywords()
    if keyword in keywords:
        keywords.remove(keyword)
        save_keywords(keywords)
        await update.message.reply_text(f"Ключевое слово '{keyword}' удалено.")
    else:
        await update.message.reply_text(f"Ключевое слово '{keyword}' не найдено в списке.")


async def list_keywords(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not is_user_authorized(username):
        await update.message.reply_text("У вас нет прав для удаления ключевых слов.")
        return
    keywords = load_keywords()
    if not keywords:
        await update.message.reply_text("Список ключевых слов пуст.")
        return
    await update.message.reply_text("Список ключевых слов:\n" + "\n".join(keywords))


# Функция для обработки всех текстовых сообщений
async def handle_message(update: Update, context: CallbackContext, group_id: str) -> None:
    message_text = update.message.text
    print(update.message)
    keywords = load_keywords()
    print(keywords)
    if any(keyword.lower() in message_text.lower() for keyword in keywords):
        message = f"""Chat name: {update.message.chat.title}\n
From username: {update.message.from_user.username}\n
Message: {update.message.text}"""
        await context.bot.send_message(chat_id=group_id, text=message)


# Команда для добавления ключевого слова
async def add_user(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not is_user_authorized(username):
        await update.message.reply_text("У вас нет прав для добавления пользователей")
        return
    print(context.args)
    user = ' '.join(context.args)
    if not user:
        await update.message.reply_text("Пожалуйста, укажите пользователя для добавления.")
        return
    users = load_users()
    users.add(user)
    save_users(users)
    await update.message.reply_text(f"Пользователь '{user}' добавлен.")


# Команда для удаления ключевого слова
async def remove_user(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not is_user_authorized(username):
        await update.message.reply_text("У вас нет прав для удаления пользователей.")
        return
    user = ' '.join(context.args)
    if not user:
        await update.message.reply_text("Пожалуйста, укажите пользователя для удаления.")
        return
    users = load_keywords()
    if user in users:
        users.remove(user)
        save_keywords(users)
        await update.message.reply_text(f"Пользователь '{user}' удалено.")
    else:
        await update.message.reply_text(f"Пользователь'{user}' не найден в списке.")


async def list_users(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    if not is_user_authorized(username):
        await update.message.reply_text("У вас нет прав для получения списка пользователей.")
        return
    users = load_users()
    if not users:
        await update.message.reply_text("Список пользователей пуст.")
        return
    await update.message.reply_text("Список пользователей:\n" + "\n".join(users))


async def show_help(update: Update, context: CallbackContext) -> None:
    help_message = """
Доступные команды:
- /add_word <ключевое_слово>: Добавить ключевое слово в список.
- /remove_word <ключевое_слово>: Удалить ключевое слово из списка.
- /list_words: Вывести список всех ключевых слов.
- /add_user <имя_пользователя>: Добавить пользователя в список авторизованных.
- /remove_user <имя_пользователя>: Удалить пользователя из списка авторизованных.
- /list_users: Вывести список всех авторизованных пользователей.
- /help: Показать это сообщение справки.

Примечание: Только авторизованные пользователи могут добавлять или удалять ключевые слова и пользователей.
"""
    await update.message.reply_text(help_message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", help="Токен Telegram бота")
    parser.add_argument("--group", help="ID целевой группы")
    args = parser.parse_args()

    token = args.token or os.getenv("TOKEN")
    group_id = args.group or os.getenv("TARGET_GROUP")

    if not token and not group_id:
        sys.exit('Токен или ID группы не указаны. Укажите их в аргументах или переменных окружения.')

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("add_word", add_keyword))
    app.add_handler(CommandHandler("remove_word", remove_keyword))
    app.add_handler(CommandHandler("list_words", list_keywords))
    app.add_handler(CommandHandler("add_user", add_user))
    app.add_handler(CommandHandler("remove_user", remove_user))
    app.add_handler(CommandHandler("list_users", list_users))
    app.add_handler(CommandHandler("help", show_help))
    app.add_handler(MessageHandler(filters=TEXT, callback=partial(handle_message, group_id=group_id)))

    app.run_polling()


if __name__ == '__main__':
    main()
