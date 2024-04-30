from shazamio import Shazam
import asyncio
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from request import *
from colorama import Back
import os
from telegram import ReplyKeyboardMarkup

os.system('cls')

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR
)

logger = logging.getLogger(__name__)


def main():
    global markup, shazam, dialog
    application = Application.builder().token(
        "1718648860:AAGEsVoBXRfgKPumKkLhtKeu-KZr6ZYWzAA").read_timeout(30).write_timeout(30).build()

    # text_handler = MessageHandler(filters.TEXT, echo)

    conv_handler = ConversationHandler(entry_points=[CommandHandler('start_find', start_find)],
                                       states={
                                           1: [MessageHandler(filters.TEXT & ~filters.COMMAND, res_track_name)],
                                           2: [MessageHandler(filters.TEXT & ~filters.COMMAND, download_choosed_track)]},
                                       fallbacks=[CommandHandler('stop', stop)])

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("audio", audio))

    reply_keyboard = [['/start_find']]
    yes_no = [['Yes', 'No']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    dialog = ReplyKeyboardMarkup(yes_no, one_time_keyboard=True)

    voice_handler = MessageHandler(filters.VOICE, voice)
    application.add_handler(voice_handler)

    # recognition_handler = ConversationHandler(entry_points=[voice_handler],
    #                                           states={
    #     1: MessageHandler(filters.TEXT & ~filters.COMMAND, res_track_name)},
    #     fallbacks=[CommandHandler('stop', stop)])

    # Shazam
    shazam = Shazam()

    # Запускаем приложение.
    application.run_polling()


async def start(update, context):
    await update.message.reply_text("Привет! Это бот для скачавания музыки. Введите /start_find для начала.",
                                    reply_markup=markup)
    print(update.message.chat)


async def start_find(update, context):
    await update.message.reply_text("Введите название исполнителя и(или) трека")
    return 1


async def res_track_name(update, context):
    track_name = update.message.text
    print(update.message.chat, track_name)
    await update.message.reply_text(f"Ваш запрос: {track_name}")
    await update.message.reply_text("Поиск вариантов")
    tracks = await find_track(track_name)
    if not tracks:
        await update.message.reply_text("Ничего не найдено")
        return ConversationHandler.END
    tracks = tracks.items()
    context.user_data['tracks'] = tracks
    message = ''''''
    for i, track in enumerate(tracks):
        message += f'{i + 1}. {track[0]}: {track[1][1]}\n'
    await update.message.reply_text(message)
    await update.message.reply_text("Выберете трек для скачивания")
    return 2


async def download_choosed_track(update, context):
    index = update.message.text
    print(index)
    print(type(index))
    print(not index.isdigit())
    if not (index.isdigit()):
        await update.message.reply_text("Введите действительное значение")
        return 2
    elif not (1 <= int(index) <= 5):
        await update.message.reply_text("Введите число от 1 до 5")
        return 2
    try:
        track = list(context.user_data['tracks'])[int(index) - 1]
        await update.message.reply_text("Скачивание...")
        href = track[1][0]
        name = track[0]
        path = f"music/{name}.mp3"
        print(path)
        await dowloand_track(href, name)
        with open(path, 'rb') as music_file:
            await update.message.reply_document(music_file)
        os.remove(path)
        await stop()
    except IndexError:
        await update.message.reply_text("Трека с таким номером нет")
        return 2
    # req = requests.get(href, stream=True)
    # print(req.content)
    # await update.message.reply_document(req.content)
    # del req


async def stop(update, context):
    await update.message.reply_text("Завершение...")
    return ConversationHandler.END


async def audio(update, context):
    with open('music/Валентин Стрыкало - Всёрешено.mp3', 'rb') as music_file:
        # print(dir(update.message))
        await update.message.reply_document(music_file)
    os.remove('music/Валентин Стрыкало - Всёрешено.mp3')


async def voice(update, context):
    print(update.message.chat)
    await update.message.reply_text("Обработка...")
    file = await context.bot.get_file(update.message.voice.file_id)
    await file.download_to_drive("recognition/voice_note.ogg")

    recognition = await shazam.recognize("recognition/voice_note.ogg")

    if not recognition["matches"]:
        await update.message.reply_text("К сожалению, ничего не найдено")
        return

    track_name = f'{recognition["track"]["title"]} - {recognition["track"]["subtitle"]}'
    coverart_url = recognition["track"]["images"]["coverart"]

    coverart = requests.get(coverart_url).content
    await update.message.reply_photo(coverart, caption=track_name)
    print(update.message.chat, track_name)
    # print(type(recognition))
    # print(recognition.keys())
    # pprint(recognition["track"])
    # print(recognition["track"].keys())
    # print(recognition["track"]["title"], recognition["track"]["subtitle"])
    # print(recognition["track"]["images"]["coverart"])

    await update.message.reply_text("Скачать определенный трек?", reply_markup=dialog)


# async def answer(update, context):
#     ans = update.message.text
#     if ans = "No":


if __name__ == '__main__':
    main()
