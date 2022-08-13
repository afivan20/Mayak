import os
import csv
import pandas as pd
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from lxml import etree
from dotenv import dotenv_values
from db import init_db, add_data, add_info


temp = dotenv_values(".env")
TOKEN = temp["TOKEN"]


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat = update.effective_chat
    context.bot.send_message(
        text=f'Привет, {user.first_name}!\nПожалуйста загрузи файл в формате csv. С полями - NAME, URL, XPATH',
        chat_id=chat.id,
    )


def parser(item, url, selector, chat, context):
    # html запрос для url из принятого файла .csv сохраняем в файл item
    r = requests.get(f'{url}', headers={'Content-Type': 'text/html', })
    html = r.text
    with open(f'tmp/{item}', 'w') as f:
        f.write(html)
    # создаем дерево для парсинга
    response = open(f'tmp/{item}')
    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)
    # создаем файл для вывода ответа пользователю
    upload = open(f'tmp/upload/{item}.csv', 'w')
    writer = csv.writer(upload)
    writer.writerow([f'{item}'])
    # парсим данные
    items = tree.xpath(f'{selector}')
    # если данные существуют, сохраняем в БД
    if len(items) != 0:
        init_db()
        if not add_data(item):  # если пришел False, значит такое поле в БД уже есть
            os.remove(f'tmp/{item}')
            return False
        for i in items:
            # сохранить в SQLite3
            add_info(item, i)
            # записать в файл для ответа пользователю
            writer.writerow([f'{i}'])
    else:
        os.remove(f'tmp/upload/{item}.csv')
    os.remove(f'tmp/{item}')


def downloader(update, context):
    chat = update.effective_chat
    name = update.message.document.file_name
    try:
        context.bot.get_file(update.message.document).download(f'tmp/files/{name}')
        data = pd.read_csv(f'tmp/files/{name}')
        items = data['NAME']
        urls = data['URL']
        selectors = data['XPATH']
    except Exception as e:
        context.bot.send_message(
            text=f'Неверные данные! ❌ {e}',
            chat_id=chat.id,
            )
        os.remove(f'tmp/files/{name}')
        return

    os.remove(f'tmp/files/{name}')

    context.bot.send_message(
        text='Спасибо! Идет обработка данных ...',
        chat_id=chat.id,
        )

    for item, url, selector in zip(items, urls, selectors):
        try:
            field = parser(item, url, selector, chat, context)
        except Exception as e:
            context.bot.send_message(
                text=f'Ошибка! ❌ {e}',
                chat_id=chat.id,
                )
            return
        if field is False:
            context.bot.send_message(
                text=f'Поле {item} уже существует ❌',
                chat_id=chat.id,
                )
            os.remove(f'tmp/upload/{item}.csv')
            field = True
            continue
        try:
            with open(f'tmp/upload/{item}.csv', 'rb') as file:
                context.bot.send_document(
                    chat_id=chat.id,
                    document=file,
                    filename=f'{item}.csv'
                    )
            os.remove(f'tmp/upload/{item}.csv')
        except:
            context.bot.send_message(chat_id=chat.id, text=f'{item} - нет данных ❌')
    context.bot.send_message(
        text='Выполнено! ✅',
        chat_id=chat.id
        )


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document, downloader))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
