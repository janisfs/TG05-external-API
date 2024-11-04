from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.filters import CommandStart, Command
import asyncio
import requests

from config import TOKEN, SPOONACULAR_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Я бот для поиска рецептов. Введи список ингредиентов через запятую, например: курица, картофель, морковь.")

@dp.message(Command("random", "recipe"))
async def get_random_recipe(message: types.Message):
    url = "https://api.spoonacular.com/recipes/random"
    params = {
        'number': 1,
        'apiKey': SPOONACULAR_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        recipe = response.json()['recipes'][0]
        await message.answer_photo(
            recipe['image'],
            caption=f"{recipe['title']}\nВремя приготовления: {recipe['readyInMinutes']} мин.\n"
                    f"Подробнее: {recipe['sourceUrl']}"
        )
    else:
        await message.answer("Извините, не удалось получить случайный рецепт. Попробуйте еще раз позже.")
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())