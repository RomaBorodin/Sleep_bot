import telebot
import os
from datetime import datetime

TOKEN = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(TOKEN)

data = {}


@bot.message_handler(commands=['start'])
def start(message):
    data[message.from_user.id] = {}

    greeting = 'Привет, я буду помогать тебе отслеживать параметры сна.'
    commands_list = 'Используй команды: \n/sleep для начала отсчета ' \
                    '\n/wake для конца отсчета \n/quality для оценки качества сна ' \
                    '\n/notes для написания заметок \n/show_notes для показа заметок'
    bot.send_message(message.chat.id, greeting)
    bot.send_message(message.chat.id, commands_list)


@bot.message_handler(commands=['sleep'])
def sleep(message):
    if message.from_user.id in data:
        data[message.from_user.id].clear()
        data[message.from_user.id]['notes'] = []

        data[message.from_user.id]['start_time'] = datetime.now()

        reply = 'Спокойной ночи, не забудь сообщить мне, когда проснешься командой /wake'
        bot.reply_to(message, reply)
    else:
        reply = 'Перед началом работы используй команду /start'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['wake'])
def wake(message):
    try:
        if 'duration' not in data[message.from_user.id]:
            duration_obj = datetime.now() - data[message.from_user.id]['start_time']
            duration = round(duration_obj.seconds / 3600, 3)
            data[message.from_user.id]['duration'] = duration

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
    try:
        if data[message.from_user.id]['duration']:
            quality_mark = int(list(message.text.split())[1])

            if 1 <= quality_mark <= 10:
                data[message.from_user.id]['quality'] = quality_mark
                reply = 'Спасибо за оценку качества сна'
                bot.reply_to(message, reply)
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
    try:
        if data[message.from_user.id]['duration']:
            note_lst = list(message.text.split())[1:]
            note = ' '.join(note_lst)
            data[message.from_user.id]['notes'].append(note)

            reply = 'Заметка успешно сохранена'
            bot.reply_to(message, reply)
    except KeyError:
        reply = 'Ты не можешь оставить заметку о сне, если не спал. Используй команды /sleep и /wake'
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['show_notes'])
def show_notes(message):
    for i in data[message.from_user.id]['notes']:
        bot.send_message(message.chat.id, i)


bot.polling()
