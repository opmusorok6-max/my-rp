import asyncio
import os
import hashlib
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SERGEY_ID = 7847573270
GELYA_ID = 6249773677

# Структура: Эмодзи, Действие-М, Действие-Ж, Отказ-М, Отказ-Ж
RP_ACTIONS = {
    "плед": ("🛏️", "заботливо укрыл пледом", "заботливо укрыла пледом", "отказался от пледа", "отказалась от пледа"),
    "поцеловать": ("💋", "нежно поцеловал", "нежно поцеловала", "отказался от поцелуя", "отказалась от поцелуя"),
    "обнять": ("🤗", "крепко обнял", "крепко обняла", "отказался от объятий", "отказалась от объятий"),
    "укусить": ("👀", "слегка укусил за ушко", "мило укусила за ушко", "отказался от укуса", "отказалась от укуса"),
    "трахнуть": ("🔥", "страстно занялся любовью", "нежно занялась любовью", "отказался от близости", "отказалась от близости"),
    "шлепнуть": ("🍑", "игриво шлёпнул по попе", "игриво шлёпнула по попе", "отказался от шлепка", "отказалась от шлепка"),
    "цветочек": ("🌹", "подарил цветочек", "подарила цветочек", "отказался от цветочка", "отказалась от цветочка"),
    "успокоить": ("🧸", "успокоил", "успокоила", "отказался успокаивать", "отказалась успокаивать"),
    "пожалеть": ("🥺", "прижал к груди и пожалел", "нежно погладила и пожалела", "отказался жалеть", "отказалась жалеть"),
    "погладить": ("💆‍♂️", "ласково погладил", "нежно погладила", "отказался гладить", "отказалась гладить"),
    "массаж": ("💆‍♀️", "сделал расслабляющий массаж", "сделала нежный массаж", "отказался от массажа", "отказалась от массажа"),
    "кофе": ("☕", "принёс ароматный кофе", "приготовила самый вкусный кофе", "отказался от кофе", "отказалась от кофе"),
}

@dp.inline_query()
async def inline_rp_handler(inline_query: types.InlineQuery):
    user_id = inline_query.from_user.id
    sender_name = "Серёжа" if user_id == SERGEY_ID else "Геля"
    query = inline_query.query.lower()
    results = []
    
    for act, data in RP_ACTIONS.items():
        if not query or act.startswith(query):
            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="✅ Принять", callback_data=f"y:{act}:{user_id}"),
                        types.InlineKeyboardButton(text="❌ Отказать", callback_data=f"n:{act}:{user_id}"))
            
            # Используем message_text, чтобы избежать ошибки аргументов
            results.append(types.InlineQueryResultArticle(
                id=hashlib.md5(act.encode()).hexdigest(),
                title=f"{data[0]} {act.capitalize()}",
                input_message_content=types.InputTextMessageContent(message_text=f"{data[0]} <b>{sender_name}</b> {data[1 if user_id == SERGEY_ID else 2]}!", parse_mode="HTML"),
                reply_markup=builder.as_markup()
            ))
    await inline_query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    try:
        parts = call.data.split(":")
        choice, action, sender_id = parts[0], parts[1], int(parts[2])
    except: return

    clicker_id = call.from_user.id
    if clicker_id == sender_id:
        return await call.answer("Нельзя ответить на своё же действие!", show_alert=True)
    
    data = RP_ACTIONS[action]
    is_clicker_s = (clicker_id == SERGEY_ID)
    is_sender_s = (sender_id == SERGEY_ID)
    
    clicker_name = "Серёжа" if is_clicker_s else "Геля"
    
    if choice == "y":
        target = "Гелю" if is_sender_s else "Серёжу"
        text = f"{data[0]} <b>{clicker_name}</b> принял(а) действие от {target}! 🥰"
    else:
        # Теперь отказ корректно пишет имя того, кто нажал кнопку
        text = f"💔 <b>{clicker_name}</b> {data[3 if is_clicker_s else 4]}."
    
    await bot.edit_message_text(text=text, inline_message_id=call.inline_message_id, parse_mode="HTML")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Бот онлайн"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 7860).start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
