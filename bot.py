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
    commands_list = 'Используй команды: \n/sleep для начала отсчета ' \
                    '\n/wake для конца отсчета \n/quality для оценки качества сна ' \
                    '\n/notes для написания заметок \n/show_notes для показа заметок'
    bot.send_message(message.chat.id, greeting)
    bot.send_message(message.chat.id, commands_list)


@bot.message_handler(commands=['sleep'])
def sleep(message):
    user_id = str(message.from_user.id)
    today = datetime.now().date().isoformat()

    try:
        if users[user_id]:
            active_sleep_date = max(users[user_id].keys())
            if 'duration' not in users[user_id][active_sleep_date]:
                reply = 'Ты еще не проснулся, чтобы начать новый отсчет, используй команду /wake'
                bot.send_message(message.chat.id, reply)
                return

        users[user_id][today] = {}
        users[user_id][today]['notes'] = []
        users[user_id][today]['start_time'] = datetime.now().isoformat()

        save_data()

        reply = 'Спокойной ночи, не забудь сообщить мне, когда проснешься командой /wake'
        bot.reply_to(message, reply)

    except KeyError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['wake'])
def wake(message):
    user_id = str(message.from_user.id)

    try:
        if not users[user_id]:
            reply = 'Ты ещё не начинал отслеживание сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        last_sleep_date = max(users[user_id].keys())

        if 'duration' in users[user_id][last_sleep_date]:
            reply = 'Я не вижу, чтобы ты сообщал мне о начале сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        start_time = datetime.fromisoformat(users[user_id][last_sleep_date]['start_time'])

        duration_obj = datetime.now() - start_time
        duration = round(duration_obj.total_seconds() / 3600, 3)
        users[user_id][last_sleep_date]['duration'] = duration

        save_data()

        reply = (f'Доброе утро, ты поспал около {duration} часов. Не забудь оценить качество сна от 1 до 10 '
                 f'командой /quality и оставить заметки командой /notes')
        bot.reply_to(message, reply)

    except KeyError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['quality'])
def quality(message):
    user_id = str(message.from_user.id)

    try:
        if not users[user_id]:
            reply = 'Ты ещё не начинал отслеживание сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        # пока оценку можно поставить только за последний сон, можно доработать
        last_sleep_date = max(users[user_id].keys())

        if 'duration' not in users[user_id][last_sleep_date]:
            reply = 'Ты не можешь оценить сон, если не спал. Используй команды /sleep и /wake'
            bot.send_message(message.chat.id, reply)
            return

        try:
            quality_mark = int(message.text.split()[1])
            if 1 <= quality_mark <= 10:
                users[user_id][last_sleep_date]['quality'] = quality_mark

                reply = f'Оценка сна {quality_mark} сохранена за {last_sleep_date}.'
                bot.reply_to(message, reply)

                save_data()

            else:
                reply = 'Оценка должна быть в пределах от 1 до 10'
                bot.reply_to(message, reply)

        except (ValueError, IndexError):
            reply = 'Используй команду в формате "/quality 8"'
            bot.send_message(message.chat.id, reply)

    except KeyError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['notes'])
def notes(message):
    user_id = str(message.from_user.id)

    try:
        if not users[user_id]:
            reply = 'Ты ещё не начинал отслеживание сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        # пока заметки можно оставить только за последний сон, можно доработать
        last_sleep_date = max(users[user_id].keys())

        if 'duration' not in users[user_id][last_sleep_date]:
            reply = 'Ты не можешь оставить заметку о сне, если не спал. Используй команды /sleep и /wake'
            bot.send_message(message.chat.id, reply)
            return

        note_lst = list(message.text.split())[1:]
        note = ' '.join(note_lst)
        users[user_id][last_sleep_date]['notes'].append(note)

        save_data()

        reply = 'Заметка успешно сохранена'
        bot.reply_to(message, reply)

    except KeyError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['show_notes'])
def show_notes(message):
    user_id = str(message.from_user.id)

    try:
        if not users[user_id]:
            reply = 'Ты ещё не начинал отслеживание сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        last_sleep_date = max(users[user_id].keys())

        if users[user_id][last_sleep_date]['notes']:
            for i in users[user_id][last_sleep_date]['notes']:
                bot.send_message(message.chat.id, i)
        else:
            reply = 'У тебя еще нет заметок'
            bot.send_message(message.chat.id, reply)

    except KeyError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


bot.polling()
