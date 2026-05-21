import asyncio
import os
import hashlib
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
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

# Твой словарь (оставил как был)
RP_ACTIONS = {
    "поцеловать": ("💋", "хочет нежно поцеловать", "нежно поцеловал", "нежно поцеловала", "Гелю", "Серёжу"),
    "обнять": ("🤗", "хочет крепко обнять", "крепко обнял", "уютно обняла", "Гелю", "Серёжу"),
}

@dp.inline_query()
async def inline_rp_handler(inline_query: types.InlineQuery):
    user_id = inline_query.from_user.id
    sender = "Серёжа" if user_id == SERGEY_ID else "Геля"
    results = []
    for act, data in RP_ACTIONS.items():
        target = data[4] if user_id == SERGEY_ID else data[5]
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="✅ Принять", callback_data=f"y:{act}:{user_id}"),
                    types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"n:{act}:{user_id}"),
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
        prompt = f"Напиши короткое и милое ролевое действие для пары: {action}. Отправитель {sender_id == SERGEY_ID and 'Серёжа' or 'Геля'}. Согласуй падежи."
        response = model.generate_content(prompt)
        await call.message.edit_text(text=f"✨ {response.text}", parse_mode="HTML")
        return

    if call.from_user.id == int(sender_id):
        return await call.answer("Нельзя ответить на своё действие!", show_alert=True)
    
    data = RP_ACTIONS[action]
    is_sender_s = (int(sender_id) == SERGEY_ID)
    text = f"{data[0]} <b>{('Серёжа' if is_sender_s else 'Геля')}</b> {data[2] if is_sender_s else data[3]} <b>{target}</b>! 🥰" if choice == "y" else "💔 Действие отклонено."
    await call.message.edit_text(text=text, parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
