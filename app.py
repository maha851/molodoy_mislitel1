import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from dotenv import find_dotenv, load_dotenv

from auto_delete import AutoDeleteBot, IncomingAutoDeleteMiddleware
from handlers.get_months import photo_router
from handlers.user_private import user_private_router
from database.database import router
from common.bot_comands_list  import private
from get_students.get_stdnts import get_students_list_router
load_dotenv(find_dotenv())


# bot = Bot(token=os.getenv('TOKEN'))
#
#
# dp = Dispatcher()

# dp.include_router(user_private_router)
# dp.include_router(router)
# dp.include_router(get_students_list_router)
# dp.include_router(photo_router)


async def main():
    default_props = DefaultBotProperties(parse_mode="HTML")  # <— НОВОЕ

    bot = AutoDeleteBot(
        os.getenv("TOKEN"),
        default=default_props,  # <— вместо parse_mode=...
        auto_delete_delay=10,  # как и было
    )
    dp = Dispatcher()
    incoming_cleanup = IncomingAutoDeleteMiddleware(delay_seconds=10,skip_commands=("/pin", "/keep"))
    dp.message.middleware(incoming_cleanup)
    dp.callback_query.middleware(incoming_cleanup)
    dp.include_router(user_private_router)
    dp.include_router(router)
    dp.include_router(get_students_list_router)
    dp.include_router(photo_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())