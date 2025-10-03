import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from dotenv import find_dotenv, load_dotenv

from handlers.get_months import photo_router
from handlers.user_private import user_private_router
from database.database import router
from common.bot_comands_list  import private
from get_students.get_stdnts import get_students_list_router
load_dotenv(find_dotenv())

async def delete_later(msg: Message, delay: float = 10):
    try:
        await asyncio.sleep(delay)
        await msg.bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    except Exception:
        pass


bot = Bot(token=os.getenv('TOKEN'))


dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(router)
dp.include_router(get_students_list_router)
dp.include_router(photo_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())