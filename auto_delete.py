# utils/auto_delete.py
import asyncio
from typing import Any, Callable, Awaitable, Optional, Iterable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery

# --- базовая утилита удаления c запасом на 48 часов ---
async def _delete_after(bot: Bot, chat_id: int, message_id: int, delay: int):
    try:
        await asyncio.sleep(delay)
        await bot.delete_message(chat_id, message_id)
    except Exception:
        # игнорируем: слишком старое, уже удалено, нет прав и т.д.
        pass


# --- Middleware для входящих событий ---
class IncomingAutoDeleteMiddleware(BaseMiddleware):
    def __init__(self, delay_seconds: int = 24 * 3600,
                 skip_commands: Optional[Iterable[str]] = ("/pin", "/keep")):
        super().__init__()
        self.delay = delay_seconds
        self.skip_commands = set(skip_commands or ())

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data["bot"]

        # 1) Обычные сообщения пользователя
        if isinstance(event, Message):
            text = (event.text or "").strip()
            if not any(text.startswith(cmd) for cmd in self.skip_commands):
                asyncio.create_task(_delete_after(bot, event.chat.id, event.message_id, self.delay))

        # 2) CallbackQuery — удаляем "карточку" с кнопками
        if isinstance(event, CallbackQuery) and event.message:
            asyncio.create_task(_delete_after(bot, event.message.chat.id, event.message.message_id, self.delay))

        return await handler(event, data)


# --- Подкласс Bot, который сам чистит все исходящие сообщения ---
class AutoDeleteBot(Bot):
    def __init__(self, *args, auto_delete_delay: int = 24 * 3600, **kwargs):
        super().__init__(*args, **kwargs)
        self._auto_delete_delay = auto_delete_delay

    # Универсальный помощник
    async def _ad(self, method_coro):
        """
        Запускает оригинальный метод Bot, затем, если вернулся Message,
        планирует его удаление.
        """
        res = await method_coro
        # Многие send_* возвращают Message. Edit-методы возвращают Message либо bool.
        try:
            if isinstance(res, Message):
                asyncio.create_task(_delete_after(self, res.chat.id, res.message_id, self._auto_delete_delay))
        except Exception:
            pass
        return res

    # Переопределяем самые частые методы отправки.
    # При необходимости добавишь сюда другие send_*/edit_*.
    async def send_message(self, chat_id: int, text: str, **kwargs):
        return await self._ad(super().send_message(chat_id, text, **kwargs))

    async def send_photo(self, chat_id: int, photo, **kwargs):
        return await self._ad(super().send_photo(chat_id, photo, **kwargs))

    async def send_document(self, chat_id: int, document, **kwargs):
        return await self._ad(super().send_document(chat_id, document, **kwargs))

    async def send_video(self, chat_id: int, video, **kwargs):
        return await self._ad(super().send_video(chat_id, video, **kwargs))

    async def send_audio(self, chat_id: int, audio, **kwargs):
        return await self._ad(super().send_audio(chat_id, audio, **kwargs))

    async def edit_message_text(self, text: str, chat_id: Optional[int] = None,
                                message_id: Optional[int] = None, **kwargs):
        return await self._ad(super().edit_message_text(text=text, chat_id=chat_id, message_id=message_id, **kwargs))

    async def edit_message_caption(self, chat_id: Optional[int] = None,
                                   message_id: Optional[int] = None, **kwargs):
        return await self._ad(super().edit_message_caption(chat_id=chat_id, message_id=message_id, **kwargs))
