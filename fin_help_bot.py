import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from config import TOKEN
import sqlite3
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
import logging
from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import requests

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

button_registr = KeyboardButton(text='Регистрация')
button_exchange_rates = KeyboardButton(text='Курсы валют')
button_tips = KeyboardButton(text='Советы')
button_finances = KeyboardButton(text='Финансы')

keyboards = ReplyKeyboardMarkup(keyboard=[[button_registr, button_exchange_rates],
                                          [button_tips, button_finances]], resize_keyboard=True)

conn = sqlite3.connect('users.db')
cursor = conn.cursor()


# Создание таблицы, если она не существует
cursor.execute('''
   CREATE TABLE IF NOT EXISTS users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       telegram_id INTEGER UNIQUE,
       name TEXT,
       category1 TEXT,
       category2 TEXT,
       category3 TEXT,
       expanses1 REAl
       expanses2 REAL,
       expanses3 REAL
   )
''')
conn.commit()

#
class FinanceForm(StatesGroup):
    category1 = State()
    expanses1 = State()
    category2 = State()
    expanses2 = State()
    category3 = State()
    expanses3 = State()


# Обработчик команды /start
@dp.message(Command('start'))
async def start(message: Message):
    await message.answer("Привет! Я ваш личный финансовый помощник. Выберите действие из меню ниже:", reply_markup=keyboards)


# Обработчик кнопки "Регистрация"
@dp.message(F.text == 'Регистрация')
async def registration(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    if user:
        await message.answer("Вы уже зарегистрированы. Выберите действие из меню ниже:", reply_markup=keyboards)
    else:
        cursor.execute("INSERT INTO users (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
        conn.commit()
        await message.answer("Вы успешно зарегистрированы. Выберите действие из меню ниже:", reply_markup=keyboards)


@dp.message(F.text == 'Курсы валют')
async def exchange_rates(message: Message):
    url = 'https://v6.exchangerate-api.com/v6/f7e7dfc77b4f348254a68f6a/latest/USD'
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer('Не удалось получить данные о курсах валют.')
            return
        usd_to_rub = data['conversion_rates']['RUB']
        eur_to_usd = data['conversion_rates']['EUR']

        eur_to_rub = data['conversion_rates']['RUB'] / data['conversion_rates']['EUR']
        await message.answer(f'1 USD = {usd_to_rub:.2f} RUB\n'
                             f'1 EUR = {eur_to_rub:.2f} RUB')


    except:
        await message.answer('Произошла ошибка при получении данных о курсах валют.')






async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())