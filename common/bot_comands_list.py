import asyncio

from aiogram.types import BotCommand, Message

private = [
    BotCommand(command='start', description='начать заного'),
]

async def delete_later(msg: Message, delay: float = 10):
    try:
        await asyncio.sleep(delay)
        await msg.bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    except Exception:
        pass