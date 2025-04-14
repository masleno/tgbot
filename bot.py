from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import random
import asyncio

# Токен бота
API_TOKEN = '7678473223:AAGJPYiSN7Vw8XnbXu9G9h8o4_yYF2RHTYU'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список игр
games = {}

# Список слов с подсказками
riddles = {
    "собака": "Это животное, которое лает",
    "машина": "Это ездит по дорогам",
    "яблоко": "Это фрукт, обычно красный или зелёный",
    "книга": "Её читают",
}

# Клавиатура для старта
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать игру")],
        [KeyboardButton(text="Присоединиться к игре")]
    ],
    resize_keyboard=True
)

# Инструкция при запуске
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Это игра 'Кто быстрее угадает'. Я загадаю слово, а ты попробуешь угадать по подсказке.\n"
        "Как играть:\n"
        "1. Нажми 'Создать игру', чтобы начать и пригласить друзей.\n"
        "2. Дай друзьям код игры, они выберут 'Присоединиться к игре' и введут код.\n"
        "3. Когда все готовы, я дам подсказку — угадай слово первым!\n"
        "Начнём?",
        reply_markup=start_keyboard
    )

# Обработка "Создать игру"
@dp.message(lambda message: message.text == "Создать игру")
async def start_game(message: types.Message):
    game_code = f"GAME{random.randint(100, 999)}"
    word = random.choice(list(riddles.keys()))  # Выбираем слово
    hint = riddles[word]  # Подсказка соответствует слову
    games[game_code] = {
        "players": [message.from_user.id],
        "word": word,
        "hint": hint,
        "active": False
    }
    await message.answer(
        f"Игра создана! Код: {game_code}\n"
        "Дай этот код друзьям, чтобы они присоединились.\n"
        "Жду 15 секунд, потом начну!",
        reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    )
    await asyncio.sleep(15)
    if len(games[game_code]["players"]) > 1:
        games[game_code]["active"] = True
        for player_id in games[game_code]["players"]:
            await bot.send_message(player_id, f"Загадка: {games[game_code]['hint']}\nПиши слово!")
    else:
        await message.answer("Никто не подключился, игра отменяется.")
        del games[game_code]

# Обработка "Присоединиться к игре"
@dp.message(lambda message: message.text == "Присоединиться к игре")
async def ask_for_code(message: types.Message):
    await message.answer("Введи код игры (например, GAME123):")

# Подключение по коду
@dp.message(lambda message: message.text.startswith("GAME"))
async def join_game(message: types.Message):
    game_code = message.text.strip()
    if game_code in games and not games[game_code]["active"]:
        if message.from_user.id not in games[game_code]["players"]:
            games[game_code]["players"].append(message.from_user.id)
            await message.answer(f"Ты в игре {game_code}! Жди подсказку.")
        else:
            await message.answer("Ты уже в этой игре!")
    else:
        await message.answer("Игра не найдена или уже началась.")

# Обработка угадывания
@dp.message()
async def guess_word(message: types.Message):
    user_id = message.from_user.id
    for game_code, game in games.items():
        if user_id in game["players"] and game["active"]:
            if message.text.lower() == game["word"]:
                for player_id in game["players"]:
                    await bot.send_message(player_id, f"@{message.from_user.username} угадал слово '{game['word']}' первым! Игра окончена.")
                del games[game_code]
                return
            else:
                await message.answer("Не то, пробуй ещё!")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
