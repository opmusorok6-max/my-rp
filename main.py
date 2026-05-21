import asyncio
import os
import hashlib
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# Настройка Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SERGEY_ID = 7847573270
GELYA_ID = 6249773677

# Твой полный словарь
RP_ACTIONS = {
    "поцеловать": ("💋", "хочет нежно поцеловать", "нежно поцеловал", "нежно поцеловала", "Гелю", "Серёжу"),
    "обнять": ("🤗", "хочет крепко обнять", "крепко обнял", "уютно обняла", "Гелю", "Серёжу"),
    "укусить": ("👀", "хочет мило укусить", "слегка укусил", "мило укусила", "Гелю", "Серёжу"),
    "трахнуть": ("🔥", "горячо желает", "страстно занялся любовью с", "нежно занялась любовью с", "Гелей", "Серёжей"),
    "шлепнуть": ("🍑", "игриво шлёпает по попе", "игриво шлёпнул", "игриво шлёпнула", "Гелю", "Серёжу"),
    "цветочек": ("🌹", "дарит", "подарил цветочек", "подарила цветочек", "Геле", "Серёже"),
    "успокоить": ("🧸", "хочет успокоить", "крепко обнял и успокоил", "нежно обняла и успокоила", "Гелю", "Серёжу"),
    "пожалеть": ("🥺", "хочет пожалеть", "прижал к груди и пожалел", "нежно погладила и пожалела", "Гелю", "Серёжу"),
    "погладить": ("💆‍♂️", "хочет погладить по голове", "ласково погладил", "нежно погладила", "Гелю", "Серёжу"),
    "массаж": ("💆‍♀️", "предлагает сделать массаж", "сделал расслабляющий массаж", "сделала нежный массаж", "Геле", "Серёже"),
    "кофе": ("☕", "готовит ароматный кофе для", "принёс ароматный кофе", "приготовила самый вкусный кофе", "Геле", "Серёже"),
    "плед": ("🛏️", "хочет укрыть пледом", "заботливо укрыл", "заботливо укрыла", "Гелю", "Серёжу"),
}

@dp.inline_query()
async def inline_rp_handler(inline_query: types.InlineQuery):
    user_id = inline_query.from_user.id
    sender = "Серёжа" if user_id == SERGEY_ID else "Геля"
    results = []
    for act, data in RP_ACTIONS.items():
        target = data[4] if user_id == SERGEY_ID else data[5]
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="✅", callback_data=f"y:{act}:{user_id}"),
                    types.InlineKeyboardButton(text="❌", callback_data=f"n:{act}:{user_id}"),
                    types.InlineKeyboardButton(text="✨ ИИ", callback_data=f"ai:{act}:{user_id}"))
        
        results.append(types.InlineQueryResultArticle(
            id=hashlib.md5(f"{act}{user_id}".encode()).hexdigest(),
            title=f"{data[0]} {act.capitalize()}",
            input_message_content=types.InputTextMessageContent(message_text=f"{data[0]} <b>{sender}</b> {data[1]} <b>{target}</b>!", parse_mode="HTML"),
            reply_markup=builder.as_markup()
        ))
    await inline_query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    parts = call.data.split(":")
    choice, action, sender_id = parts[0], parts[1], int(parts[2])
    
    if choice == "ai":
        await call.answer("Генерирую...", show_alert=False)
        prompt = f"Напиши короткое и милое ролевое описание для: {action}. Отправитель {sender_id == SERGEY_ID and 'Серёжа' or 'Геля'}. Используй падежи правильно."
        response = model.generate_content(prompt)
        await call.message.edit_text(text=f"✨ {response.text}", parse_mode="HTML")
        return

    is_sender_s = (int(sender_id) == SERGEY_ID)
    data = RP_ACTIONS[action]
    target = data[5] if is_sender_s else data[4]
    
    text = f"{data[0]} <b>{('Серёжа' if is_sender_s else 'Геля')}</b> {data[2] if is_sender_s else data[3]} <b>{target}</b>! 🥰" if choice == "y" else "💔 Действие отклонено."
    await call.message.edit_text(text=text, parse_mode="HTML")

async def web_server(request):
    return web.Response(text="Бот онлайн")

async def main():
    app = web.Application()
    app.router.add_get("/", web_server)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
