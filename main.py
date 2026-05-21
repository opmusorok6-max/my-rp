import asyncio
import os
import hashlib
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SERGEY_ID = 7847573270
GELYA_ID = 6249773677

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
    user_id = inline_query.from_user.id
    sender = "Серёжа" if user_id == SERGEY_ID else "Геля"
    target = "Гелю" if user_id == SERGEY_ID else "Серёжу"
    results = []
    for act, data in RP_ACTIONS.items():
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="✅", callback_data=f"y:{act}:{user_id}"),
                    types.InlineKeyboardButton(text="❌", callback_data=f"n:{act}:{user_id}"),
                    types.InlineKeyboardButton(text="✨ ИИ", callback_data=f"ai:{act}:{user_id}"))
        
        results.append(types.InlineQueryResultArticle(
            id=hashlib.md5(f"{act}{user_id}".encode()).hexdigest(),
            title=f"{data[0]} {act.capitalize()}",
            input_message_content=types.InputTextMessageContent(message_text=f"{data[0]} <b>{sender}</b> хочет '{act}' для <b>{target}</b>!", parse_mode="HTML"),
            reply_markup=builder.as_markup()
        ))
    await inline_query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    parts = call.data.split(":")
    choice, action, sender_id = parts[0], parts[1], int(parts[2])
    is_sender_s = (int(sender_id) == SERGEY_ID)
    sender_name = "Серёжа" if is_sender_s else "Геля"
    target_name = "Гелю" if is_sender_s else "Серёжу"
    
    if choice == "ai":
        await call.answer("Генерирую...", show_alert=False)
        loop = asyncio.get_running_loop()
        try:
            prompt = f"Напиши короткое действие: {sender_name} {action} {target_name}. Имя получателя в винительном падеже."
            response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
            text = f"✨ {response.text[:1000]}"
            if call.inline_message_id:
                await bot.edit_message_text(inline_message_id=call.inline_message_id, text=text, parse_mode="HTML")
            else:
                await call.message.edit_text(text=text, parse_mode="HTML")
        except:
            await call.answer("Ошибка ИИ", show_alert=True)
        return

    data = RP_ACTIONS[action]
    action_text = data[1] if is_sender_s else data[2]
    text = f"{data[0]} <b>{sender_name}</b> {action_text} <b>{target_name}</b>! 🥰" if choice == "y" else f"💔 <b>{sender_name}</b> хотел(а) '{action}', но {target_name} отказался(ась)."
    
    if call.inline_message_id:
        await bot.edit_message_text(inline_message_id=call.inline_message_id, text=text, parse_mode="HTML")
    else:
        await call.message.edit_text(text=text, parse_mode="HTML")

async def main():
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="Бот онлайн"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 10000).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
