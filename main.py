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

RP_ACTIONS = {
    "поцеловать": ("💋", "хочет нежно поцеловать", "обнял и нежно поцеловал", "нежно поцеловала", "увернулась... 💔", "ответила поцелуем... 🥰", "Гелю", "Серёжу"),
    "обнять": ("🤗", "хочет крепко обнять", "крепко обнял", "уютно обняла", "не дала себя обнять... 😔", "прижалась в ответ! 💕", "Гелю", "Серёжу"),
    "укусить": ("👀", "хочет мило укусить за ушко", "слегка укусил за ушко", "мило укусила за ушко", "увернулась от 'куся'... 😼", "смутилась и спряталась... 😳", "Гелю", "Серёжу"),
    "трахнуть": ("🔥", "горячо желает", "страстно занялся любовью с", "нежно занялась любовью с", "увы, не сейчас... 🙈", "смутилась и спряталась... 😳", "Гелей", "Серёжей"),
    "шлепнуть": ("🍑", "игриво шлёпает по попе", "игриво шлёпнул по попе", "игриво шлёпнула по попе", "сделала вид, что не заметила... 🤨", "погрозила пальчиком! 😤", "Гелю", "Серёжу"),
    "цветочек": ("🌹", "дарит", "подарил цветочек", "подарила цветочек", "сказала, что не любит цветы... 🥀", "улыбнулась, приняв подарок 🌹", "Геле", "Серёже"),
    "успокоить": ("🧸", "хочет успокоить", "крепко обнял и успокоил", "нежно обняла и успокоила", "сказала, что хочет побыть одной... ☁️", "прошептала: 'Я рядом' 🧸", "Гелю", "Серёжу"),
    "пожалеть": ("🥺", "хочет пожалеть", "прижал к груди и пожалел", "нежно погладила и пожалела", "отвернулась, но улыбнулась 🍃", "прижалась в знак благодарности 🥺", "Гелю", "Серёжу"),
    "погладить": ("💆‍♂️", "хочет погладить по голове", "ласково погладил", "нежно погладила", "увернулась... 😼", "замурлыкала от удовольствия! 😺", "Гелю", "Серёжу"),
    "массаж": ("💆‍♀️", "предлагает сделать массаж", "сделал расслабляющий массаж", "сделала нежный массаж", "отказалась, устала... 😴", "сказала: 'Ммм, приятно!' 💆‍♀️", "Геле", "Серёже"),
    "кофе": ("☕", "готовит ароматный кофе для", "принёс ароматный кофе", "приготовила самый вкусный кофе", "сказала, что хочет чай... 🍵", "сделала глоток и просияла! ✨", "Геле", "Серёже"),
    "плед": ("🛏️", "хочет укрыть пледом", "заботливо укрыл", "заботливо укрыла", "сказала, что не холодно... ❄️", "завернулась и обняла тебя! 🛏️", "Гелю", "Серёжу"),
}

@dp.inline_query()
async def inline_rp_handler(inline_query: types.InlineQuery):
    user_id = inline_query.from_user.id
    sender = "Серёжа" if user_id == SERGEY_ID else "Геля"
    query = inline_query.query.lower()
    results = []
    for act, data in RP_ACTIONS.items():
        if not query or act.startswith(query):
            target = data[6] if user_id == SERGEY_ID else data[7]
            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="✅ Принять", callback_data=f"y:{act}:{user_id}"),
                        types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"n:{act}:{user_id}"))
            
            # ВАЖНО: передаем параметры именованными аргументами
            results.append(types.InlineQueryResultArticle(
                id=hashlib.md5(act.encode()).hexdigest(),
                title=f"{data[0]} {act.capitalize()}",
                input_message_content=types.InputTextMessageContent(message_text=f"{data[0]} <b>{sender}</b> {data[1]} <b>{target}</b>!", parse_mode="HTML"),
                reply_markup=builder.as_markup()
            ))
    await inline_query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    try:
        parts = call.data.split(":")
        choice, action, sender_id = parts[0], parts[1], int(parts[2])
    except: return

    if call.from_user.id == sender_id:
        return await call.answer("Нельзя ответить на своё действие!", show_alert=True)
    
    data = RP_ACTIONS[action]
    is_sender_s = (sender_id == SERGEY_ID)
    is_clicker_s = (call.from_user.id == SERGEY_ID)
    target = data[7] if is_clicker_s else data[6]
    
    if choice == "y":
        text = f"{data[0]} <b>{'Серёжа' if is_sender_s else 'Геля'}</b> {data[2] if is_sender_s else data[3]} <b>{target}</b>! 🥰"
    else:
        text = f"💔 <b>{'Серёжа' if is_sender_s else 'Геля'}</b> {data[4] if is_sender_s else data[5]}"
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
