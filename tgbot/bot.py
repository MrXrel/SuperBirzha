import asyncio

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

from db import database

TOKEN = "6927821667:AAHJvbD646PWsZsn1qSAFQoFNRdyLx_Wc-g"

dbase = database.Database()

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Реакция бота на комманду /start
    """
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! Мы биржа МАИ инвестиции.\nДля того, чтобы узнать свой Telegram ID, напишите {html.italic('/get_id')}")


@dp.message(Command("get_id"))
async def command_start_handler(message: Message) -> None:
    """
    Бот возвращает telegram id пользователя для дальнейшей связи с ним
    """
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! Ваш Telegram ID {html.bold(message.from_user.id)}. Введите его, пожалуйста, на сайте в личном кабинете и задайте сумму изменения баланса для оповещения.")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Реакция бота на любое сообщение, кроме команд /start и /get_id
    """
    await message.answer("К сожалению, я не умею отвечать на такие сообщения. Обратитесь в нашу службу поддержки.")


async def scheduled_message():
    """
    Раз в минуту бот проверяет пользователей для оповещения, проверяет их портфели на изменение и проверяет время оповещения
    """
    user_list = list(dbase.get_all_user_for_tg_bot().values())
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M").split(':')
    current_time = datetime.time(hour=int(current_time[0]), minute=int(current_time[1]))
    currency = dbase.get_all_currencies()
    text_to_message_notification = []

    for key, value in currency.items():
        new = f"{key}: {value['price']}"
        text_to_message_notification.append(new)
    text_to_message_notification = '\n'.join(text_to_message_notification)

    for user in user_list:
        if user['time_to_note'] == current_time:
            await bot.send_message(chat_id=user['tg_id'],
                                   text=f"{html.bold(user['name'].capitalize())}, состояние валют на текущий момент:\n"
                                        f"{text_to_message_notification}")

        if user['tg_id'] != 0 and abs(user['new_briefcase'] - user['old_briefcase']) >= user['delta_to_note']:
            try:
                dbase.update_old_briefcase_by_id(user['ID'])
                await bot.send_message(chat_id=user['tg_id'],
                                       text=f"{html.bold(user['name'].capitalize())}, стоимость Вашего портфеля изменилась больше, чем вы указывали.\nИзменение портфеля: {html.bold(round(user['new_briefcase'] - user['old_briefcase'], 2))}")
            except Exception:
                pass


async def main() -> None:
    """
    Запуск бота в ассинхронном виде
    """
    global bot

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_message, 'interval', minutes=1)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
