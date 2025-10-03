# utils/auto_delete.py
import asyncio
from typing import Any, Callable, Awaitable, Optional, Iterable, Dict, List

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery


async def _delete_after(bot: Bot, chat_id: int, message_id: int, delay: int):
    try:
        await asyncio.sleep(delay)
        await bot.delete_message(chat_id, message_id)
        print(f"[auto_delete] deleted chat={chat_id} mid={message_id} after {delay}s")
    except Exception as e:
        print(f"[auto_delete] FAILED chat={chat_id} mid={message_id}: {e!r}")


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

        # 1) Сообщения пользователя
        if isinstance(event, Message):
            text = (event.text or "").strip()
            if not any(text.startswith(cmd) for cmd in self.skip_commands):
                asyncio.create_task(_delete_after(bot, event.chat.id, event.message_id, self.delay))

        # 2) CallbackQuery — удаляем "карточку" (сообщение с инлайн-кнопками)
        if isinstance(event, CallbackQuery) and event.message:
            asyncio.create_task(_delete_after(bot, event.message.chat.id, event.message.message_id, self.delay))

        return await handler(event, data)


class AutoDeleteBot(Bot):
    def __init__(self, *args, auto_delete_delay: int = 24 * 3600, **kwargs):
        super().__init__(*args, **kwargs)
        self._auto_delete_delay = auto_delete_delay

    async def _ad(self, method_coro):
        """
        Выполняет метод бота; если результат — Message или список Message,
        планирует удаление.
        """
        res = await method_coro
        try:
            if isinstance(res, Message):
                asyncio.create_task(_delete_after(self, res.chat.id, res.message_id, self._auto_delete_delay))
            elif isinstance(res, list) and res and isinstance(res[0], Message):
                # например, send_media_group возвращает список Message
                for m in res:
                    asyncio.create_task(_delete_after(self, m.chat.id, m.message_id, self._auto_delete_delay))
        except Exception:
            pass
        return res

    # --- send_* ---
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

    async def send_animation(self, chat_id: int, animation, **kwargs):
        return await self._ad(super().send_animation(chat_id, animation, **kwargs))

    async def send_sticker(self, chat_id: int, sticker, **kwargs):
        return await self._ad(super().send_sticker(chat_id, sticker, **kwargs))

    async def send_media_group(self, chat_id: int, media: List, **kwargs):
        return await self._ad(super().send_media_group(chat_id, media, **kwargs))

    # --- edit_* ---
    async def edit_message_text(self, text: str, chat_id: Optional[int] = None,
                                message_id: Optional[int] = None, **kwargs):
        return await self._ad(super().edit_message_text(text=text, chat_id=chat_id, message_id=message_id, **kwargs))

    async def edit_message_caption(self, chat_id: Optional[int] = None,
                                   message_id: Optional[int] = None, **kwargs):
        return await self._ad(super().edit_message_caption(chat_id=chat_id, message_id=message_id, **kwargs))

    async def edit_message_media(self, media, chat_id: Optional[int] = None,
                                 message_id: Optional[int] = None, **kwargs):
        return await self._ad(super().edit_message_media(media=media, chat_id=chat_id, message_id=message_id, **kwargs))

    async def edit_message_reply_markup(self, chat_id: Optional[int] = None,
                                        message_id: Optional[int] = None, **kwargs):
        # Иногда Telegram возвращает True/False. Если вернёт Message — тоже удалим.
        return await self._ad(super().edit_message_reply_markup(chat_id=chat_id, message_id=message_id, **kwargs))

    # --- copy/forward ---
    async def copy_message(self, chat_id: int, from_chat_id: int, message_id: int, **kwargs):
        return await self._ad(super().copy_message(chat_id, from_chat_id, message_id, **kwargs))

    async def forward_message(self, chat_id: int, from_chat_id: int, message_id: int, **kwargs):
        return await self._ad(super().forward_message(chat_id, from_chat_id, message_id, **kwargs))
