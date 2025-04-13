import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# === НАСТРОЙКИ ===
BOT_TOKEN = "8081264714:AAF2TrtHQPCqMFE7ZILufvEoRmcc4ZbO9oI"
CRYPTOBOT_API_KEY = "365909:AAtJ1Ee0m6tJGtWKfPY5jmmxx7XJZ4Cyz5E"
TUTORIAL_LINK = "https://docs.google.com/document/d/1qtZd3Iu5tFR1GUIiE3zTL9aCFP7cQ9FP0mUPXm1d-WU/edit?usp=sharing"
SCRIPT_PATH = "script.py"
ADMIN_ID = 7249427313
ADMIN_PASSWORD = "871289012038"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище пользователей (можно заменить на базу)
user_ids = set()

# Кнопки
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🛒 Купить автопиар")]],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="📢 Рассылка")],
        [KeyboardButton(text="🔓 Получить автопиар")],
        [KeyboardButton(text="🚪 Выйти")]
    ],
    resize_keyboard=True
)

# Состояния админа
class AdminState(StatesGroup):
    waiting_for_password = State()
    admin_authenticated = State()

# Функции оплаты
async def create_invoice(user_id: int):
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_API_KEY}
    data = {
        "asset": "USDT",
        "amount": "1.78",  # 👈 строка, как требует API
        "description": "Покупка автопиара",
        "hidden_message": "Спасибо за оплату!",
        "paid_btn_name": "openBot",
        "paid_btn_url": "https://t.me/AutoPiarKerral_bot",
        "payload": str(user_id)
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as resp:
            result = await resp.json()
            return result["result"]["pay_url"]

async def check_paid(user_id: int):
    url = "https://pay.crypt.bot/api/getInvoices"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            result = await resp.json()
            for inv in result["result"]["items"]:
                if inv["status"] == "paid" and inv["payload"] == str(user_id):
                    return True
    return False

# Обработчики команд
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_ids.add(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔐 Введите пароль для входа в админ-панель:")
        await state.set_state(AdminState.waiting_for_password)
    else:
        await message.answer("""
☺️☺️Здравствуй, это бот покупки автопиара для различных ситуаций☺️

😇Сейчас мы тебе расскажем что ты получаешь при покупке нашего автопиара😇

❤️‍🔥Автоматическая рассылка твоего текста без бана❤️‍🔥
👾Настройка за 5 минут👾
✅Туториал и готовый скрипт в комплекте✅

💲Цена — всего 150 и 1.78 USDT💲
🔴Ты окупаешь это уже с первых клиентов!🔴

🤗Нажми кнопку ниже, чтобы начать прямо сейчас🤗

⬇️Купить автопиар⬇️️""", reply_markup=main_kb)

@dp.message(AdminState.waiting_for_password)
async def admin_check_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await message.answer("✅ Доступ разрешён. Вы вошли как админ.", reply_markup=admin_kb)
        await state.set_state(AdminState.admin_authenticated)
    else:
        await message.answer("❌ Неверный пароль.")

@dp.message(AdminState.admin_authenticated)
async def admin_panel(message: types.Message, state: FSMContext):
    if message.text == "📊 Статистика":
        await message.answer(f"📈 Всего пользователей: {len(user_ids)}")
    elif message.text == "📢 Рассылка":
        await message.answer("✍️ Напиши текст для рассылки:")
    elif message.text == "🔓 Получить автопиар":
        await message.answer("✅ Вы получили автопиар (бесплатно).")
        await message.answer(f"📘 Туториал: {TUTORIAL_LINK}")
        await message.answer_document(InputFile(SCRIPT_PATH))
    elif message.text == "🚪 Выйти":
        await message.answer("🚪 Вы вышли из админ-панели.", reply_markup=main_kb)
        await state.clear()
    else:
        for user_id in user_ids:
            try:
                await bot.send_message(user_id, message.text)
            except Exception:
                continue
        await message.answer("✅ Рассылка завершена.")

@dp.message(F.text == "🛒 Купить автопиар")
async def buy(message: types.Message):
    url = await create_invoice(message.from_user.id)
    await message.answer(f"💸 Оплати 1.78 USDT по ссылке:\n{url}")

@dp.message(F.text.lower().contains("оплат"))
async def check(message: types.Message):
    is_paid = await check_paid(message.from_user.id)
    if is_paid:
        await message.answer("✅ Оплата найдена!")
        await message.answer(f"📘 Туториал: {TUTORIAL_LINK}")
        await message.answer_document(InputFile(SCRIPT_PATH))
    else:
        await message.answer("❌ Платёж не найден. Подожди пару минут и попробуй ещё.")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

