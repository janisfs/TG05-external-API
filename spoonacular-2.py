from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.filters import CommandStart, Command
import asyncio
import requests
from googletrans import Translator
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


def translate_ingredients(ingredients):
    translator = Translator()
    translated_ingredients = []
    for ingredient in ingredients:
        translated_ingredient = translator.translate(ingredient, dest='en').text
        translated_ingredients.append(translated_ingredient)
    # Объединяем переведенные ингредиенты в строку через запятую
    return ','.join(translated_ingredients)



def search_recipes(ingredients):
    translated_ingredients = translate_ingredients(ingredients.split(','))
    # Отправка запроса к API с переведенными ингредиентами
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        'ingredients': translated_ingredients,
        'number': 5,  # Укажем, сколько рецептов хотим получить
        'apiKey': SPOONACULAR_API_KEY
    }
    response = requests.get(url, params=params)
    # Отладочный вывод для проверки запроса
    print(f"API response status: {response.status_code}")
    print("API response data:", response.json())

    if response.status_code == 200:
        return response.json()  # findByIngredients возвращает список рецептов
    else:
        return []


def get_recipe_details(recipe_id):
    """Функция для получения полной информации о рецепте по ID."""
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {
        'apiKey': SPOONACULAR_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@dp.message(Command("ingredients"))
async def get_recipe_by_ingredients(message: types.Message):
    ingredients = message.text.replace('/ingredients ', '').replace(' ', '')
    recipes = search_recipes(ingredients)
    if recipes:
        recipe_id = recipes[0]['id']
        recipe_details = get_recipe_details(recipe_id)
        if recipe_details:
            await message.answer_photo(
                recipe_details['image'],
                caption=f"{recipe_details['title']}\nВремя приготовления: {recipe_details['readyInMinutes']} мин.\n"
                        f"Подробнее: {recipe_details['sourceUrl']}"
            )
        else:
            await message.answer("Извините, не удалось получить полную информацию о рецепте.")
    else:
        await message.answer("Извините, не удалось найти рецепт по заданным ингредиентам.")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
