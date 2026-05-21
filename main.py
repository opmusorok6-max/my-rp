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

# Теперь бот сам узнает имена
@dp.inline_query()
async def inline_rp_handler(inline_query: types.InlineQuery):
    sender_name = inline_query.from_user.first_name
    results = []
    
    # В инлайне мы не знаем получателя до момента клика, 
    # поэтому пишем просто действие
    for act, data in RP_ACTIONS.items():
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="✅", callback_data=f"y:{act}:{inline_query.from_user.id}"),
                    types.InlineKeyboardButton(text="❌", callback_data=f"n:{act}:{inline_query.from_user.id}"),
                    types.InlineKeyboardButton(text="✨ ИИ", callback_data=f"ai:{act}:{inline_query.from_user.id}"))
        
        results.append(types.InlineQueryResultArticle(
            id=hashlib.md5(f"{act}{inline_query.from_user.id}".encode()).hexdigest(),
            title=f"{data[0]} {act.capitalize()}",
            input_message_content=types.InputTextMessageContent(message_text=f"{data[0]} <b>{sender_name}</b> хочет '{act}'!"),
            reply_markup=builder.as_markup()
        ))
    await inline_query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    parts = call.data.split(":")
    choice, action, sender_id = parts[0], parts[1], int(parts[2])
    
    # Имя отправителя берем из нажатия кнопки
    sender_name = call.from_user.first_name
    
    if choice == "ai":
        # Используем show_alert=True, чтобы точно увидеть, если что-то пошло не так
        await call.answer("Генерирую текст...", show_alert=False)
        
        loop = asyncio.get_running_loop()
        try:
            # Промпт теперь более свободный, так как мы не знаем второе имя
            prompt = f"Напиши короткое милое действие: {sender_name} делает '{action}'. Добавь романтики."
            response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
            text = f"✨ {response.text[:1000]}"
            
            if call.inline_message_id:
                await bot.edit_message_text(inline_message_id=call.inline_message_id, text=text, parse_mode="HTML")
        except Exception as e:
            await call.answer(f"Ошибка ИИ: {str(e)[:50]}", show_alert=True)
        return

    # Обработка обычных кнопок
    data = RP_ACTIONS[action]
    if choice == "y":
        text = f"{data[0]} <b>{sender_name}</b> выбрал(а) '{action}'! 🥰"
    else:
        text = f"💔 <b>{sender_name}</b> хотел(а) '{action}', но что-то пошло не так."

    if call.inline_message_id:
        await bot.edit_message_text(inline_message_id=call.inline_message_id, text=text, parse_mode="HTML")

# Словарь RP (оставь как был)
RP_ACTIONS = {
    "поцеловать": ("💋",), "обнять": ("🤗",), "укусить": ("👀",),
    "трахнуть": ("🔥",), "шлепнуть": ("🍑",), "цветочек": ("🌹",),
    "успокоить": ("🧸",), "пожалеть": ("🥺",), "погладить": ("💆‍♂️",),
    "массаж": ("💆‍♀️",), "кофе": ("☕",), "плед": ("🛏️",)
}

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
