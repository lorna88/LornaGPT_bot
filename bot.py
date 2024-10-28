from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ChatMemberHandler

from credentials import ChatGPT_TOKEN, Telegram_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'main'
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

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'random'
    prompt = load_prompt('random')
    message = load_message('random')

    await send_image(update, context, 'random')
    message = await send_text(update, context, message)

    answer = await chat_gpt.send_question(prompt, '')
    await message.edit_text(answer)

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'gpt'
    prompt = load_prompt('gpt')
    message = load_message('gpt')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, 'gpt')
    await send_text(update, context, message)

async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    message = await send_text(update, context, "Думаю над вопросом...")
    answer = await chat_gpt.add_message(text)
    await message.edit_text(answer)

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'talk'
    message = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, message, {
        'talk_cobain': 'Курт Кобейн',
        'talk_queen': 'Елизавета II',
        'talk_tolkien': 'Джон Толкиен',
        'talk_nietzsche': 'Фридрих Ницше',
        'talk_hawking': 'Стивен Хокинг'
    })

async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    cb = update.callback_query.data

    prompt = load_prompt(cb)
    chat_gpt.set_prompt(prompt)

    await send_image(update, context, cb)
    await send_text(update, context, 'Задай мне вопрос')

async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'quiz'
    message = load_message('quiz')

    prompt = load_prompt('quiz')
    chat_gpt.set_prompt(prompt)

    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, message, {
        'quiz_prog': 'Программирование на Python',
        'quiz_math': 'Теории алгоритмов, множеств и матанализа',
        'quiz_biology': 'Биология'
    })

async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    cb = update.callback_query.data
    if cb == 'quiz_more':
        dialog.quiz_count += 1
    else:
        dialog.quiz_count = 0
        dialog.quiz_score = 0
        await send_text(update, context, 'Начинаем игру!')
    answer = await chat_gpt.add_message(cb)
    await send_text(update, context, answer)

async def quiz_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if answer == 'Правильно!':
        dialog.quiz_score += 1
    await send_text(update, context, answer)
    await send_text_buttons(update, context, f'Количество правильных ответов: {dialog.quiz_score} из {dialog.quiz_count}', {
        'quiz_more': 'Следующий вопрос'
    })

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'translate'
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

async def translate_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_text(update, context, 'Что нужно перевести?')
    cb = update.callback_query.data
    await chat_gpt.add_message(cb)

async def translate_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    message = await send_text(update, context, "Перевожу текст...")
    answer = await chat_gpt.add_message(text)
    await message.edit_text(answer)

async def companion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = 'companion'
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

async def companion_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    cb = update.callback_query.data
    answer = await chat_gpt.add_message(cb)
    await send_text(update, context, answer)

async def companion_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'talk':
        await talk_dialog(update, context)
    elif dialog.mode == 'quiz':
        await quiz_dialog(update, context)
    elif dialog.mode == 'translate':
        await translate_dialog(update, context)
    elif dialog.mode == 'companion':
        await companion_dialog(update, context)
    else:
        await send_text(update, context, update.message.text)

dialog = Dialog()
dialog.mode = None
dialog.quiz_score = 0
dialog.quiz_count = 0
# Переменные можно определить, как атрибуты dialog

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(Telegram_TOKEN).build()

# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('translate', translate))
app.add_handler(CommandHandler('companion', companion))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(talk_button, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(quiz_button, pattern='^quiz_.*'))
app.add_handler(CallbackQueryHandler(translate_button, pattern='^trans_.*'))
app.add_handler(CallbackQueryHandler(companion_button, pattern='^comp_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
