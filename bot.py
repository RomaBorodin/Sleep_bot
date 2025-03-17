import telebot
import json
import os
from datetime import datetime

TOKEN = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'sleep_data.json'


def load_data():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE):
        with open(DATA_FILE, encoding='utf-8') as file:
            return json.load(file)
    return {}


def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(users, file, indent=4, ensure_ascii=False)


users = load_data()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {}
        save_data()

    greeting = 'Привет, я буду помогать тебе отслеживать параметры сна.'
    command_list = 'Используй команды: \n/sleep для начала отсчета ' \
                   '\n/wake для конца отсчета \n/quality для оценки качества сна ' \
                   '\n/notes для написания заметок \n/show_notes для показа заметок'
    bot.send_message(message.chat.id, greeting)
    bot.send_message(message.chat.id, command_list)


@bot.message_handler(commands=['sleep'])
def sleep(message):
    user_id = str(message.from_user.id)
    today = datetime.now().date().isoformat()

    if user_id in users:
        users[user_id][today] = {}
        users[user_id][today]['notes'] = []
        users[user_id][today]['start_time'] = datetime.now().isoformat()

        save_data()

        reply = 'Спокойной ночи, не забудь сообщить мне, когда проснешься командой /wake'
        bot.reply_to(message, reply)
    else:
        reply = 'Перед началом работы используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['wake'])
def wake(message):
    user_id = str(message.from_user.id)
    today = datetime.now().date().isoformat()

    try:
        if 'duration' not in users[user_id][today]:
            duration_obj = datetime.now() - datetime.fromisoformat(users[user_id][today]['start_time'])
            duration = round(duration_obj.seconds / 3600, 3)
            users[user_id][today]['duration'] = duration

            save_data()

            reply = (f'Доброе утро, ты поспал около {duration} часов. Не забудь оценить качество сна от 1 до 10 '
                     f'командой /quality и оставить заметки командой /notes')
            bot.reply_to(message, reply)
        else:
            reply = 'Я вижу, что ты уже проснулся. Используй команду /sleep, чтобы начать отсчет для нового сна'
            bot.send_message(message.chat.id, reply)
    except KeyError:
        reply = 'Я не вижу, чтобы ты сообщал мне о начале сна. Используй команду /sleep'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['quality'])
def quality(message):
    user_id = str(message.from_user.id)
    today = datetime.now().date().isoformat()

    try:
        if users[user_id][today]['duration']:
            quality_mark = int(list(message.text.split())[1])

            if 1 <= quality_mark <= 10:
                users[user_id][today]['quality'] = quality_mark
                reply = 'Спасибо за оценку качества сна'
                bot.reply_to(message, reply)

                save_data()

            else:
                reply = 'Оценка должна быть в пределах от 1 до 10'
                bot.reply_to(message, reply)
    except KeyError:
        reply = 'Ты не можешь оценить сон, если не спал. Используй команды /sleep и /wake'
        bot.send_message(message.chat.id, reply)
    except ValueError:
        reply = 'Некорректная оценка'
        bot.send_message(message.chat.id, reply)
    except IndexError:
        reply = 'Поставь оценку'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['notes'])
def notes(message):
    user_id = str(message.from_user.id)
    today = datetime.now().date().isoformat()

    try:
        if users[user_id][today]['duration']:
            note_lst = list(message.text.split())[1:]
            note = ' '.join(note_lst)
            users[user_id][today]['notes'].append(note)

            save_data()

            reply = 'Заметка успешно сохранена'
            bot.reply_to(message, reply)
    except KeyError:
        reply = 'Ты не можешь оставить заметку о сне, если не спал. Используй команды /sleep и /wake'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['show_notes'])
def show_notes(message):
    user_id = str(message.from_user.id)
    today = datetime.now().date().isoformat()

    for i in users[user_id][today]['notes']:
        bot.send_message(message.chat.id, i)


bot.polling()
