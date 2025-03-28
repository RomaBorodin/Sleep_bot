import telebot
import sqlite3 as sq
import bot_queries as bq
from os import getenv
from datetime import datetime

TOKEN = getenv('TG_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = int(message.from_user.id)
    user_name = str(message.from_user.first_name)

    bq.tables_creation()

    if not bq.find_user(user_id):
        bq.add_user(user_id, user_name)

    greeting = 'Привет, я буду помогать тебе отслеживать параметры сна.'
    commands_list = 'Используй команды: \n/sleep для начала отсчета ' \
                    '\n/wake для конца отсчета \n/quality для оценки качества сна ' \
                    '\n/notes для написания заметок \n/show_notes для показа заметок'
    bot.send_message(message.chat.id, greeting)
    bot.send_message(message.chat.id, commands_list)


@bot.message_handler(commands=['sleep'])
def sleep(message):
    user_id = int(message.from_user.id)
    start_time = datetime.now().isoformat()

    try:
        if bq.get_last_record(user_id):
            if bq.get_last_record(user_id)['duration'] is None:
                reply = 'Ты еще не проснулся, чтобы начать новый отсчет, используй команду /wake'
                bot.send_message(message.chat.id, reply)
                return

        bq.add_start_time(user_id, start_time)

        reply = 'Спокойной ночи, не забудь сообщить мне, когда проснешься командой /wake'
        bot.reply_to(message, reply)

    except sq.OperationalError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['wake'])
def wake(message):
    user_id = int(message.from_user.id)

    try:
        if not bq.get_last_record(user_id):
            reply = 'Ты ещё не начинал отслеживание сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        if bq.get_last_record(user_id)['duration'] is not None:
            reply = 'Я не вижу, чтобы ты сообщал мне о начале сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        last_record_id = bq.get_last_record(user_id)['id']

        start_time = datetime.fromisoformat(bq.get_last_record(user_id)['start_time'])

        duration_obj = datetime.now() - start_time
        duration = round(duration_obj.total_seconds() / 3600, 3)
        bq.add_duration(duration, last_record_id)

        reply = (f'Доброе утро, ты поспал около {duration} часов. Не забудь оценить качество сна от 1 до 10 '
                 f'командой /quality и оставить заметки командой /notes')
        bot.reply_to(message, reply)

    except sq.OperationalError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['quality'])
def quality(message):
    user_id = int(message.from_user.id)

    try:
        if not bq.get_last_record(user_id):
            reply = 'Ты ещё не начинал отслеживание сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        # пока оценку можно поставить только за последний сон, можно доработать
        last_record_id = bq.get_last_record(user_id)['id']

        if bq.get_last_record(user_id)['duration'] is None:
            reply = 'Ты не можешь оценить сон, если не спал. Используй команды /sleep и /wake'
            bot.send_message(message.chat.id, reply)
            return

        try:
            quality_mark = int(message.text.split()[1])
            if 1 <= quality_mark <= 10:
                bq.add_quality(quality_mark, last_record_id)

                reply = f'Оценка {quality_mark} сохранена.'
                bot.reply_to(message, reply)

            else:
                reply = 'Оценка должна быть в пределах от 1 до 10'
                bot.reply_to(message, reply)

        except (ValueError, IndexError):
            reply = 'Используй команду в формате "/quality 8"'
            bot.send_message(message.chat.id, reply)

    except sq.OperationalError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['notes'])
def notes(message):
    user_id = int(message.from_user.id)

    try:
        if not bq.get_last_record(user_id):
            reply = 'Ты ещё не начинал отслеживание сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        # пока заметки можно оставить только за последний сон, можно доработать
        last_record_id = bq.get_last_record(user_id)['id']

        if bq.get_last_record(user_id)['duration'] is None:
            reply = 'Ты не можешь оставить заметку о сне, если не спал. Используй команды /sleep и /wake'
            bot.send_message(message.chat.id, reply)
            return

        note_lst = list(message.text.split())[1:]
        note = ' '.join(note_lst)

        if not note.strip():
            reply = 'Напиши в заметке хоть что-то'
            bot.send_message(message.chat.id, reply)
            return

        bq.add_note(last_record_id, note)

        reply = 'Заметка успешно сохранена'
        bot.reply_to(message, reply)

    except sq.OperationalError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['show_notes'])
def show_notes(message):
    user_id = int(message.from_user.id)

    try:
        if not bq.get_last_record(user_id):
            reply = 'Ты ещё не начинал отслеживание сна. Используй /sleep.'
            bot.send_message(message.chat.id, reply)
            return

        last_record_id = bq.get_last_record(user_id)['id']

        if bq.check_notes(last_record_id) is not None:
            for i in bq.get_notes(last_record_id):
                bot.send_message(message.chat.id, i)
        else:
            reply = 'У тебя еще нет заметок'
            bot.send_message(message.chat.id, reply)

    except sq.OperationalError:
        reply = 'Для начала используй команду /start'
        bot.send_message(message.chat.id, reply)


bot.polling()
