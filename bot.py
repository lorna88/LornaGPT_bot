from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes

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
        'quiz': 'Поучаствовать в квизе ❓'
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
    # await  send_text_buttons(update, context, answer, {
    #     'random_more': 'Хочу ещё рандомный факт',
    #     'random_end': 'Хочу закончить',
    #     'blabla': 'Случайная кнопка'
    # })

# async def random_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.callback_query.answer()
#     cb = update.callback_query.data
#     if cb == 'random_more':
#         await send_text(update, context, 'Нажмите /random')
#     else:
#         await send_text(update, context, 'Нажмите /start')

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

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    else:
        await send_text(update, context, update.message.text)

dialog = Dialog()
dialog.mode = None
# Переменные можно определить, как атрибуты dialog

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(Telegram_TOKEN).build()

# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
# app.add_handler(CallbackQueryHandler(random_button, pattern='^random_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
