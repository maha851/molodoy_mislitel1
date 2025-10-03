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




# --- Глобальный патч удаления исходящих сообщений ---
import asyncio
from aiogram.client.bot import Bot as _CoreBot
from aiogram.types import Message as _Msg

_DELETE_DELAY = 10  # секунды; поставь 10 для теста, потом поменяешь

async def _del_after(_bot: _CoreBot, chat_id: int, mid: int):
    try:
        await asyncio.sleep(_DELETE_DELAY)
        await _bot.delete_message(chat_id, mid)
    except Exception:
        pass  # уже удалено/нет прав/старше 48ч

def _wrap_send(name: str):
    orig = getattr(_CoreBot, name)
    async def patched(self, *args, **kwargs):
        res = await orig(self, *args, **kwargs)
        try:
            # send_media_group -> list[Message]; остальное -> Message
            if isinstance(res, list) and res and isinstance(res[0], _Msg):
                for m in res:
                    asyncio.create_task(_del_after(self, m.chat.id, m.message_id))
            elif isinstance(res, _Msg):
                asyncio.create_task(_del_after(self, res.chat.id, res.message_id))
        except Exception:
            pass
        return res
    setattr(_CoreBot, name, patched)

for _name in [
    "send_message","send_photo","send_document","send_video","send_audio",
    "send_animation","send_sticker","send_media_group",
    "copy_message","forward_message",
    "edit_message_text","edit_message_caption","edit_message_media","edit_message_reply_markup",
]:
    _wrap_send(_name)
# --- /Глобальный патч ---





# bot = Bot(token=os.getenv('TOKEN'))
#
#
# dp = Dispatcher()

# dp.include_router(user_private_router)
# dp.include_router(router)
# dp.include_router(get_students_list_router)
# dp.include_router(photo_router)
default_props = DefaultBotProperties(parse_mode="HTML")
bot = AutoDeleteBot(
        os.getenv("TOKEN"),
        default=default_props,  # <— вместо parse_mode=...
        auto_delete_delay=10,  # как и было
    )


async def main():
    # default_props = DefaultBotProperties(parse_mode="HTML")  # <— НОВОЕ
    #
    # bot = AutoDeleteBot(
    #     os.getenv("TOKEN"),
    #     default=default_props,  # <— вместо parse_mode=...
    #     auto_delete_delay=10,  # как и было
    # )
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