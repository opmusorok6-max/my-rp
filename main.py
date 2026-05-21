import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import google.generativeai as genai

# Настройка
logging.basicConfig(level=logging.INFO)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Все RP команды сохранены
RP_ACTIONS = {
    "поцеловать": ("💋", "нежно поцеловал", "нежно поцеловала"),
    "обнять": ("🤗", "крепко обнял", "уютно обняла"),
    "укусить": ("👀", "слегка укусил", "мило укусила"),
    "трахнуть": ("🔥", "страстно занялся любовью с", "нежно занялась любовью с"),
    "шлепнуть": ("🍑", "игриво шлёпнул", "игриво шлёпнула"),
    "цветочек": ("🌹", "подарил цветочек", "подарила цветочек"),
    "успокоить": ("🧸", "крепко обнял и успокоил", "нежно обняла и успокоила"),
    "пожалеть": ("🥺", "прижал к груди и пожалел", "нежно погладила и пожалела"),
    "погладить": ("💆‍♂️", "ласково погладил", "нежно погладила"),
    "массаж": ("💆‍♀️", "сделал расслабляющий массаж", "сделала нежный массаж"),
    "кофе": ("☕", "принёс ароматный кофе", "приготовила самый вкусный кофе"),
    "плед": ("🛏️", "заботливо укрыл", "заботливо укрыла"),
}

@dp.inline_query()
async def inline_rp_handler(inline_query: types.InlineQuery):
    sender = inline_query.from_user.first_name
    results = []
    for act, data in RP_ACTIONS.items():
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="✅", callback_data=f"y:{act}:{inline_query.from_user.id}"),
                    types.InlineKeyboardButton(text="✨ ИИ", callback_data=f"ai:{act}:{inline_query.from_user.id}"))
        results.append(types.InlineQueryResultArticle(
            id=str(hash(act + str(inline_query.from_user.id))),
            title=f"{data[0]} {act.capitalize()}",
            input_message_content=types.InputTextMessageContent(message_text=f"{data[0]} <b>{sender}</b> хочет '{act}'!"),
            reply_markup=builder.as_markup()
        ))
    await inline_query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    parts = call.data.split(":")
    choice, action, sender_id = parts[0], parts[1], parts[2]
    sender = call.from_user.first_name
    
    if choice == "ai":
        await call.answer("Генерирую...", show_alert=False)
        try:
            response = model.generate_content(f"Напиши короткое и милое действие: {sender} {action}. Добавь романтики.")
            await bot.edit_message_text(inline_message_id=call.inline_message_id, text=f"✨ {response.text[:1000]}", parse_mode="HTML")
        except:
            await call.answer("Ошибка ИИ", show_alert=True)
        return

    data = RP_ACTIONS[action]
    text = f"{data[0]} <b>{sender}</b> выбрал(а) '{action}'! 🥰"
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
