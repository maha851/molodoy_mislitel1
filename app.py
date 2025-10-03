import asyncio
import os

from aiogram import Bot, Dispatcher, types
from dotenv import find_dotenv, load_dotenv

from auto_delete import AutoDeleteBot, IncomingAutoDeleteMiddleware
from handlers.get_months import photo_router
from handlers.user_private import user_private_router
from database.database import router
from common.bot_comands_list  import private
from get_students.get_stdnts import get_students_list_router
load_dotenv(find_dotenv())


bot = Bot(token=os.getenv('TOKEN'))


dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(router)
dp.include_router(get_students_list_router)
dp.include_router(photo_router)


async def main():
    bot = AutoDeleteBot(os.getenv('TOKEN'), parse_mode="HTML", auto_delete_delay=24 * 3600)
    dp = Dispatcher()
    incoming_cleanup = IncomingAutoDeleteMiddleware(delay_seconds=24 * 3600,skip_commands=("/pin", "/keep"))
    dp.message.middleware(incoming_cleanup)
    dp.callback_query.middleware(incoming_cleanup)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())