from warnings import filterwarnings

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler
from telegram.warnings import PTBUserWarning

from credentials import ChatGPT_TOKEN, Telegram_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

MAIN, GPT, TALK, QUIZ, TRANSLATE, COMPANION, TALK_WAIT, QUIZ_WAIT, TRANSLATE_WAIT, \
    COMPANION_WAIT = range(10)


# Вывод главного меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start
    Вывод основного меню бота
    """
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'translate': 'Перевести текст 🇬🇧',
        'companion': 'Побеседовать с жителем одной из стран 🤝'
    })
    return MAIN


# Узнать случайный интересный факт
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /random
    Запрос случайного интересного факта от ChatGPT
    """
    prompt = load_prompt('random')
    message = load_message('random')

    await send_image(update, context, 'random')
    message = await send_text(update, context, message)

    answer = await chat_gpt.send_question(prompt, '')
    await message.edit_text(answer)
    return MAIN


# Задать вопрос чату GPT
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /gpt
    Инициализация диалога с ChatGPT
    """
    prompt = load_prompt('gpt')
    message = load_message('gpt')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'gpt')
    await send_text(update, context, message)
    return GPT


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка сообщений от пользователя в режиме диалога с ChatGPT
    """
    text = update.message.text
    message = await send_text(update, context, "Думаю над вопросом...")
    answer = await chat_gpt.add_message(text)
    await message.edit_text(answer)
    return GPT


# Поговорить с известной личностью
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /talk
    Инициализация диалога с ChatGPT от имени известной личности
    """
    message = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, message, {
        'talk_cobain': 'Курт Кобейн',
        'talk_queen': 'Елизавета II',
        'talk_tolkien': 'Джон Толкиен',
        'talk_nietzsche': 'Фридрих Ницше',
        'talk_hawking': 'Стивен Хокинг'
    })
    return TALK_WAIT


async def talk_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Повторный запрос нажатия на кнопку
    """
    message = 'Пожалуйста, выберите известную личность:'
    await send_text_buttons(update, context, message, {
        'talk_cobain': 'Курт Кобейн',
        'talk_queen': 'Елизавета II',
        'talk_tolkien': 'Джон Толкиен',
        'talk_nietzsche': 'Фридрих Ницше',
        'talk_hawking': 'Стивен Хокинг'
    })
    return TALK_WAIT


async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка нажатия кнопки для выбора одного из известных лиц
    """
    await update.callback_query.answer()
    cb = update.callback_query.data

    prompt = load_prompt(cb)
    chat_gpt.set_prompt(prompt)

    await send_image(update, context, cb)
    await send_text(update, context, 'Задай мне вопрос')
    return TALK


async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка сообщений от пользователя в режиме диалога с известной личностью
    """
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)
    return TALK


# Поучаствовать в квизе
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /quiz
    Инициализация викторины от ChatGPT
    """
    context.user_data["quiz_count"] = 0
    context.user_data["quiz_score"] = 0
    message = load_message('quiz')

    prompt = load_prompt('quiz')
    chat_gpt.set_prompt(prompt)

    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, message, {
        'quiz_prog': 'Программирование на Python',
        'quiz_math': 'Теории алгоритмов, множеств и матанализа',
        'quiz_biology': 'Биология'
    })
    return QUIZ_WAIT


async def quiz_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Повторный запрос нажатия на кнопку
    """
    message = 'Пожалуйста, выбери тему для квиза:'
    await send_text_buttons(update, context, message, {
        'quiz_prog': 'Программирование на Python',
        'quiz_math': 'Теории алгоритмов, множеств и матанализа',
        'quiz_biology': 'Биология'
    })
    return QUIZ_WAIT


async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка нажатия кнопки для выбора темы викторины
    """
    await update.callback_query.answer()
    cb = update.callback_query.data
    if cb == 'quiz_more':
        context.user_data["quiz_count"] += 1
    else:
        context.user_data["quiz_count"] = 1
        context.user_data["quiz_score"] = 0
        await send_text(update, context, 'Начинаем игру!')
    answer = await chat_gpt.add_message(cb)
    await send_text(update, context, answer)
    return QUIZ


async def quiz_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка сообщений от пользователя в режиме викторины
    """
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if answer == 'Правильно!':
        context.user_data["quiz_score"] += 1
    await send_text(update, context, answer)
    await send_text_buttons(update, context, f'Количество правильных ответов:'\
                                             f' {context.user_data["quiz_score"]} из'\
                                             f' {context.user_data["quiz_count"]}', \
                            {'quiz_more': 'Следующий вопрос'})
    return QUIZ


# Перевести текст
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /translate
    Инициализация умного переводчика текста
    """
    prompt = load_prompt('translate')
    message = load_message('translate')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'translate')
    await send_text_buttons(update, context, message, {
        'trans_ru': 'Русский',
        'trans_en': 'English',
        'trans_ge': 'Deutsch',
        'trans_fr': 'Français',
        'trans_sp': 'Español'
    })
    return TRANSLATE_WAIT


async def translate_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Повторный запрос нажатия на кнопку
    """
    message = 'Пожалуйста, укажите, на какой язык нужно будет переводить:'
    await send_text_buttons(update, context, message, {
        'trans_ru': 'Русский',
        'trans_en': 'English',
        'trans_ge': 'Deutsch',
        'trans_fr': 'Français',
        'trans_sp': 'Español'
    })
    return TRANSLATE_WAIT


async def translate_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка нажатия кнопки для выбора языка перевода
    """
    await update.callback_query.answer()
    await send_text(update, context, 'Что нужно перевести?')
    cb = update.callback_query.data
    await chat_gpt.add_message(cb)
    return TRANSLATE


async def translate_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка сообщений от пользователя в режиме переводчика
    """
    text = update.message.text
    message = await send_text(update, context, "Перевожу текст...")
    answer = await chat_gpt.add_message(text)
    await message.edit_text(answer)
    return TRANSLATE


# Побеседовать с жителем одной из стран
async def companion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /companion
    Инициализация диалога с иностранным собеседником
    """
    prompt = load_prompt('companion')
    message = load_message('companion')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'companion')
    await send_text_buttons(update, context, message, {
        'comp_ru': 'Россия',
        'comp_us': 'USA',
        'comp_uk': 'United Kingdom',
        'comp_ge': 'Deutschland',
        'comp_sp': 'España'
    })
    return COMPANION_WAIT


async def companion_wait(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Повторный запрос нажатия на кнопку
    """
    message = 'Пожалуйста, выбери страну собеседника:'
    await send_text_buttons(update, context, message, {
        'comp_ru': 'Россия',
        'comp_us': 'USA',
        'comp_uk': 'United Kingdom',
        'comp_ge': 'Deutschland',
        'comp_sp': 'España'
    })
    return COMPANION_WAIT


async def companion_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка нажатия кнопки для выбора страны собеседника
    """
    await update.callback_query.answer()
    cb = update.callback_query.data
    answer = await chat_gpt.add_message(cb)
    await send_text(update, context, answer)
    return COMPANION


async def companion_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка сообщений от пользователя в режиме диалога с иностранным собеседником
    """
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)
    return COMPANION


# Эхо-бот
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик сообщений, повторяющий сообщение от пользователя
    Используется, если не выбран другой режим диалога с ботом
    """
    await send_text(update, context, update.message.text)
    return MAIN

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(Telegram_TOKEN).build()

command_handlers = [
        CommandHandler("start", start),
        CommandHandler('random', random),
        CommandHandler('gpt', gpt),
        CommandHandler('talk', talk),
        CommandHandler('quiz', quiz),
        CommandHandler('translate', translate),
        CommandHandler('companion', companion)
    ]
conv_handler = ConversationHandler(
    entry_points=command_handlers,
    states={
        MAIN: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
        ],
        GPT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog)
        ],
        TALK_WAIT: [
            CallbackQueryHandler(talk_button),
            MessageHandler(filters.TEXT & ~filters.COMMAND, talk_wait)
        ],
        TALK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, talk_dialog)
        ],
        QUIZ_WAIT: [
            CallbackQueryHandler(quiz_button),
            MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_wait)
        ],
        QUIZ: [
            CallbackQueryHandler(quiz_button),
            MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_dialog)
        ],
        TRANSLATE_WAIT: [
            CallbackQueryHandler(translate_button),
            MessageHandler(filters.TEXT & ~filters.COMMAND, translate_wait)
        ],
        TRANSLATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, translate_dialog)
        ],
        COMPANION_WAIT: [
            CallbackQueryHandler(companion_button),
            MessageHandler(filters.TEXT & ~filters.COMMAND, companion_wait)
        ],
        COMPANION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, companion_dialog)
        ],
    },
    fallbacks=command_handlers,
)

app.add_handler(conv_handler)
app.run_polling()
