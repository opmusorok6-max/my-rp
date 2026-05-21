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
    "плед": ("🛏️", "заботливо укрыл пледом", "заботливо укрыла пледом", "отказался от пледа", "отказалась от пледа"),
    "поцеловать": ("💋", "нежно поцеловал", "нежно поцеловала", "отказался от поцелуя", "отказалась от поцелуя")
}

@dp.inline_query()
async def inline_rp_handler(inline_query: types.InlineQuery):
    user_id = inline_query.from_user.id
    sender_name = "Серёжа" if user_id == SERGEY_ID else "Геля"
    results = []
    for act, data in RP_ACTIONS.items():
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="✅", callback_data=f"y:{act}:{user_id}"),
                    types.InlineKeyboardButton(text="❌", callback_data=f"n:{act}:{user_id}"))
        results.append(types.InlineQueryResultArticle(
            id=hashlib.md5(act.encode()).hexdigest(),
            title=act.capitalize(),
            input_message_content=types.InputTextMessageContent(message_text=f"{data[0]} {sender_name} {data[1 if user_id == SERGEY_ID else 2]}!", parse_mode="HTML"),
            reply_markup=builder.as_markup()
        ))
    await inline_query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    parts = call.data.split(":")
    choice, action, sender_id = parts[0], parts[1], int(parts[2])
    data = RP_ACTIONS[action]
    is_clicker_s = (call.from_user.id == SERGEY_ID)
    clicker_name = "Серёжа" if is_clicker_s else "Геля"
    if choice == "y":
        await call.answer("Принято!")
    else:
        text = f"💔 {clicker_name} {data[3 if is_clicker_s else 4]}."
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
