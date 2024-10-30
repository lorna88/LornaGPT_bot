from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler
from telegram.warnings import PTBUserWarning

from credentials import ChatGPT_TOKEN, Telegram_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, default_callback_handler
from warnings import filterwarnings

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

MAIN, GPT, TALK, TRANSLATE, QUIZ, COMPANION = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        'companion': 'Побеседовать с чатом GPT на выбранном языке 🤝'
        # Добавить команду в меню можно так:
        # 'command': 'button text'

    })
    return MAIN

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('random')
    message = load_message('random')

    await send_image(update, context, 'random')
    message = await send_text(update, context, message)

    answer = await chat_gpt.send_question(prompt, '')
    await message.edit_text(answer)
    return MAIN

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('gpt')
    message = load_message('gpt')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'gpt')
    await send_text(update, context, message)
    return GPT

async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    message = await send_text(update, context, "Думаю над вопросом...")
    answer = await chat_gpt.add_message(text)
    await message.edit_text(answer)
    return GPT

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, message, {
        'talk_cobain': 'Курт Кобейн',
        'talk_queen': 'Елизавета II',
        'talk_tolkien': 'Джон Толкиен',
        'talk_nietzsche': 'Фридрих Ницше',
        'talk_hawking': 'Стивен Хокинг'
    })
    return TALK

async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    cb = update.callback_query.data

    prompt = load_prompt(cb)
    chat_gpt.set_prompt(prompt)

    await send_image(update, context, cb)
    await send_text(update, context, 'Задай мне вопрос')
    return TALK

async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)
    return TALK

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    return QUIZ

async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if answer == 'Правильно!':
        context.user_data["quiz_score"] += 1
    await send_text(update, context, answer)
    await send_text_buttons(update, context, f'Количество правильных ответов: {context.user_data["quiz_score"]} из {context.user_data["quiz_count"]}', {
        'quiz_more': 'Следующий вопрос'
    })
    return QUIZ

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('translate')
    message = load_message('translate')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'translate')
    await send_text_buttons(update, context, message, {
        'trans_ru': 'Русский',
        'trans_en': 'Английский',
        'trans_ge': 'Немецкий',
        'trans_fr': 'Французский',
        'trans_sp': 'Испанский'
    })
    return TRANSLATE

async def translate_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_text(update, context, 'Что нужно перевести?')
    cb = update.callback_query.data
    await chat_gpt.add_message(cb)
    return TRANSLATE

async def translate_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    message = await send_text(update, context, "Перевожу текст...")
    answer = await chat_gpt.add_message(text)
    await message.edit_text(answer)
    return TRANSLATE

async def companion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt('companion')
    message = load_message('companion')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'companion')
    await send_text_buttons(update, context, message, {
        'comp_ru': 'Русский',
        'comp_en': 'Английский',
        'comp_ge': 'Немецкий',
        'comp_fr': 'Французский',
        'comp_sp': 'Испанский'
    })
    return COMPANION

async def companion_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    cb = update.callback_query.data
    answer = await chat_gpt.add_message(cb)
    await send_text(update, context, answer)
    return COMPANION

async def companion_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)
    return COMPANION

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_text(update, context, update.message.text)

# Переменные можно определить, как атрибуты dialog

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(Telegram_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MAIN: [
            CommandHandler("start", start),
            CommandHandler('random', random),
            CommandHandler('gpt', gpt),
            CommandHandler('talk', talk),
            CommandHandler('quiz', quiz),
            CommandHandler('translate', translate),
            CommandHandler('companion', companion),
            MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
        ],
        GPT: [
            CommandHandler("start", start),
            CommandHandler('random', random),
            CommandHandler('gpt', gpt),
            CommandHandler('talk', talk),
            CommandHandler('quiz', quiz),
            CommandHandler('translate', translate),
            CommandHandler('companion', companion),
            MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog)
        ],
        TALK: [
            CommandHandler("start", start),
            CommandHandler('random', random),
            CommandHandler('gpt', gpt),
            CommandHandler('talk', talk),
            CommandHandler('quiz', quiz),
            CommandHandler('translate', translate),
            CommandHandler('companion', companion),
            CallbackQueryHandler(talk_button),
            CallbackQueryHandler(default_callback_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, talk_dialog)
        ],
        QUIZ: [
            CommandHandler("start", start),
            CommandHandler('random', random),
            CommandHandler('gpt', gpt),
            CommandHandler('talk', talk),
            CommandHandler('quiz', quiz),
            CommandHandler('translate', translate),
            CommandHandler('companion', companion),
            CallbackQueryHandler(quiz_button),
            CallbackQueryHandler(default_callback_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_dialog)
        ],
        TRANSLATE: [
            CommandHandler("start", start),
            CommandHandler('random', random),
            CommandHandler('gpt', gpt),
            CommandHandler('talk', talk),
            CommandHandler('quiz', quiz),
            CommandHandler('translate', translate),
            CommandHandler('companion', companion),
            CallbackQueryHandler(translate_button),
            CallbackQueryHandler(default_callback_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, translate_dialog)
        ],
        COMPANION: [
            CommandHandler("start", start),
            CommandHandler('random', random),
            CommandHandler('gpt', gpt),
            CommandHandler('talk', talk),
            CommandHandler('quiz', quiz),
            CommandHandler('translate', translate),
            CommandHandler('companion', companion),
            CallbackQueryHandler(companion_button),
            CallbackQueryHandler(default_callback_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, companion_dialog)
        ],
    },
    fallbacks=[],
)

app.add_handler(conv_handler)
app.run_polling()
