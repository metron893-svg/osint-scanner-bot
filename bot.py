
import os
import re
import urllib.parse

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Проверить номер", callback_data="phone")],
        [InlineKeyboardButton(text="👤 Поиск никнейма", callback_data="username")],
        [InlineKeyboardButton(text="🌐 Проверить домен", callback_data="domain")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")]
    ])

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "🔎 <b>OSINT Scanner</b>\n\n"
        "Инструменты для проверки открытой информации "
        "и оценки подозрительных контактов.\n\n"
        "Выбери инструмент:",
        reply_markup=menu()
    )

@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    await call.answer()
    action = call.data

    if action == "phone":
        await call.message.answer(
            "📱 Отправь номер в международном формате, "
            "например +491234567890.\n\n"
            "Я проверю формат и дам ссылку на поиск "
            "публичных жалоб и сообщений о мошенничестве."
        )
    elif action == "username":
        await call.message.answer("👤 Отправь никнейм без символа @.")
    elif action == "domain":
        await call.message.answer("🌐 Отправь домен, например example.com.")
    elif action == "about":
        await call.message.answer(
            "Этот бот помогает проверять форматы и искать "
            "публичные сообщения о мошенничестве.\n"
            "Он не раскрывает личность, адрес или закрытые "
            "данные владельцев контактов."
        )

@dp.message()
async def handle_text(message: types.Message):
    text = (message.text or "").strip()

    if text.startswith("+") and len(re.sub(r"\D", "", text)) >= 7:
        digits = re.sub(r"\D", "", text)
        if not (7 <= len(digits) <= 15):
            await message.answer("❌ Неверная длина номера.")
            return

        encoded = urllib.parse.quote('"' + text + '" scam OR spam')
        url = "https://www.google.com/search?q=" + encoded

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Поиск жалоб", url=url)],
        ])

        await message.answer(
            "📱 <b>Номер принят</b>\n"
            "Формат похож на международный.\n\n"
            "Я не подтверждаю владельца номера. "
            "Посмотри публичные жалобы и будь осторожен "
            "с неизвестными звонками.",
            reply_markup=kb
        )
        return

    if text.startswith("@") or re.fullmatch(r"[A-Za-z0-9_.]{2,32}", text):
        nick = text.lstrip("@")
        encoded = urllib.parse.quote(nick)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔍 Google",
                url="https://www.google.com/search?q=" + encoded
            )],
            [InlineKeyboardButton(
                text="🔍 Bing",
                url="https://www.bing.com/search?q=" + encoded
            )]
        ])
        await message.answer(
            "👤 Поиск публичных упоминаний никнейма:",
            reply_markup=kb
        )
        return

    if "." in text and " " not in text:
        domain = text.lower().replace("https://", "").replace("http://", "").split("/")[0]
        encoded = urllib.parse.quote(domain)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔍 Поиск домена",
                url="https://www.google.com/search?q=" + encoded
            )]
        ])
        await message.answer(
            "🌐 Ссылка для проверки публичных упоминаний домена:",
            reply_markup=kb
        )
        return

    await message.answer("Не распознал запрос. Нажми /start.")

async def main():
    if not TOKEN:
        raise RuntimeError("Установи переменную BOT_TOKEN.")

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
