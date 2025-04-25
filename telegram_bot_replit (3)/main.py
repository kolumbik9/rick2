from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
import logging

API_TOKEN = '7503954652:AAFEHHxKGS25MhxB9wIoJB5wkxLXLnvq048'
ADMIN_ID = 5665368775  # Замени на свой Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
users = {}

# --- Flask сервер для Replit ---
app = Flask('')

@app.route('/')
def home():
    return "✅ Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# -------------------------------

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    users[message.from_user.id] = message.from_user.full_name
    await message.answer("Привет! Напиши сообщение, и админ тебе ответит 😊")

    username = f"@{message.from_user.username}" if message.from_user.username else "(без username)"
    await bot.send_message(
        ADMIN_ID,
        f"👤 Новый пользователь: {message.from_user.full_name} {username}
ID: {message.from_user.id}"
    )

@dp.message_handler(lambda message: message.from_user.id != ADMIN_ID)
async def user_message(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "(без username)"
    users[user_id] = user_name

    reply_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{user_id}")
    )

    await bot.send_message(
        ADMIN_ID,
        f"📨 Сообщение от {user_name} {username} (ID: {user_id}):
{message.text}",
        reply_markup=reply_markup
    )

@dp.callback_query_handler(lambda c: c.data.startswith("reply_"))
async def process_callback_reply(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    await bot.send_message(
        ADMIN_ID,
        f"Введите сообщение для пользователя `{user_id}`:
Используй команду:
`/reply {user_id} ваш текст`",
        parse_mode="Markdown"
    )
    await callback_query.answer("Ожидаю ваш ответ...")

@dp.message_handler(commands=['reply'])
async def reply_to_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            raise ValueError("Формат: /reply ID сообщение")
        user_id = int(parts[1])
        reply_text = parts[2]

        await bot.send_message(user_id, f"✉️ Сообщение от админа:
{reply_text}")
        await message.answer("✅ Отправлено.")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")

if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
