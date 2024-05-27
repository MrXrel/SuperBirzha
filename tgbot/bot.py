import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import database

TOKEN = "6927821667:AAHJvbD646PWsZsn1qSAFQoFNRdyLx_Wc-g"

dbase = database.Database()

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! Мы биржа МАИ инвестиции.\nДля того, чтобы узнать свой Telegram ID, напишите {html.italic('/get_id')}")


@dp.message(Command("get_id"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! Ваш Telegram ID {html.bold(message.from_user.id)}. Введите его, пожалуйста, на сайте в личном кабинете и зайдайте сумму изменения баланса для оповещения.")


@dp.message()
async def echo_handler(message: Message) -> None:
    await message.answer("К сожалению, я не умею отвечать на такие сообщения. Обратитесь в нашу службу поддержки.")


async def scheduled_message():
    user_list = list(dbase.get_all_user_for_tg_bot().values())
    for user in user_list:
        if user['tg_id'] != 0 and abs(user['new_briefcase'] - user['old_briefcase']) >= user['delta_to_note']:
            try:
                dbase.update_old_briefcase_by_id(user['ID'])
                await bot.send_message(chat_id=user['tg_id'],
                                       text=f"{html.bold(user['name'].capitalize())}, стоимость Вашего портфеля изменилась больше, чем вы указывали.\nИзменение портфеля: {html.bold(user['new_briefcase'] - user['old_briefcase'])}")
            except Exception:
                pass


async def main() -> None:
    global bot

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_message, 'interval', minutes=5)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    dbase.update_tg_id(2, 1879727497)
    user_list = list(dbase.get_all_user_for_tg_bot().values())
    print(user_list)
