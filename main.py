import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Здесь все 12 команд, ничего не вырезано
RP_ACTIONS = {
    "поцеловать": "💋", 
    "обнять": "🤗", 
    "укусить": "👀", 
    "трахнуть": "🔥", 
    "шлепнуть": "🍑", 
    "цветочек": "🌹", 
    "успокоить": "🧸", 
    "пожалеть": "🥺", 
    "погладить": "💆‍♂️", 
    "массаж": "💆‍♀️", 
    "кофе": "☕", 
    "плед": "🛏️"
}

@dp.inline_query()
async def inline_rp_handler(inline_query: types.InlineQuery):
    sender = inline_query.from_user.first_name
    results = []
    for act, emoji in RP_ACTIONS.items():
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text=f"{emoji} {act.capitalize()}", callback_data=f"ai:{act}"))
        
        results.append(types.InlineQueryResultArticle(
            id=str(hash(act + str(inline_query.from_user.id))),
            title=f"{emoji} {act.capitalize()}",
            input_message_content=types.InputTextMessageContent(
                message_text=f"<i>{sender} задумал(а) сделать '{act}'...</i>", 
                parse_mode="HTML"
            ),
            reply_markup=builder.as_markup()
        ))
    await inline_query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    action = call.data.split(":")[1]
    sender = call.from_user.first_name
    
    # ИИ генерирует результат сразу при выборе
    try:
        prompt = f"Напиши короткое, нежное и романтическое действие от лица '{sender}' для действия '{action}'. Не выдумывай имена получателя."
        response = model.generate_content(prompt)
        text = f"{RP_ACTIONS[action]} <b>{response.text.strip()}</b>"
        await bot.edit_message_text(inline_message_id=call.inline_message_id, text=text, parse_mode="HTML")
    except:
        text = f"{RP_ACTIONS[action]} <b>{sender}</b> {action}!"
        await bot.edit_message_text(inline_message_id=call.inline_message_id, text=text, parse_mode="HTML")

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

def main():
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    main()
