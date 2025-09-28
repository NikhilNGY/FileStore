import asyncio
from aiohttp import web
from plugins import web_server
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message
from datetime import datetime
import sys
from config import *
from pymongo import MongoClient

# ---------------------- MongoDB Setup ----------------------
MONGO_CLIENT = MongoClient(MONGO_URI)
DB = MONGO_CLIENT[DB_NAME]
USER_SETTINGS = DB["user_settings"]  # Store per-user delete time

async def set_user_delete_time(user_id: int, seconds: int):
    """Set auto-delete time for a user in MongoDB."""
    USER_SETTINGS.update_one(
        {"user_id": user_id},
        {"$set": {"delete_seconds": seconds}},
        upsert=True
    )

async def get_user_delete_time(user_id: int):
    """Get auto-delete time for a user from MongoDB."""
    doc = USER_SETTINGS.find_one({"user_id": user_id})
    return doc.get("delete_seconds") if doc else None

# ---------------------- Bot Class ----------------------
class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER
        self.last_checked_message = {}  # Stores last processed message_id per chat

    # ---------------------- Start Bot ----------------------
    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = datetime.now()
        self.username = me.username

        # Check LOG_CHANNEL
        try:
            db_chat = await self.get_chat(LOG_CHANNEL)
            self.LOG_CHANNEL = db_chat.id
            test = await self.send_message(chat_id=db_chat.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Make sure the bot is admin in LOG_CHANNEL ({LOG_CHANNEL})"
            )
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..! Made by @KR_Picture")   

        # Start background message monitor
        self.loop.create_task(self.monitor_private_messages())

        # Start Web Server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        await web.TCPSite(app_runner, "0.0.0.0", PORT).start()

    # ---------------------- Monitor Private Messages ----------------------
    async def monitor_private_messages(self):
        """Monitor private chats with users for auto-delete."""
        while True:
            try:
                chat_ids = []
                try:
                    chat_ids.extend([u.id for u in await all_users()])
                except Exception as e:
                    self.LOGGER(__name__).warning(f"Could not fetch users: {e}")

                for chat_id in set(chat_ids):
                    last_msg_id = self.last_checked_message.get(chat_id, 0)
                    delete_seconds = await get_user_delete_time(chat_id) or 30  # default 30s

                    async for message in self.get_chat_history(chat_id, limit=1000, reverse=True):
                        if message.message_id <= last_msg_id:
                            break

                        # Only private chats
                        if message.chat.type != ChatType.PRIVATE:
                            continue

                        # Skip bot's own messages
                        if message.from_user and message.from_user.id == self.me.id:
                            continue

                        # Only delete relevant messages
                        if message.text or message.audio or message.video or message.document or message.photo:
                            asyncio.create_task(
                                self.delete_message_after(chat_id, message.message_id, delete_seconds)
                            )

                        # Update last processed
                        self.last_checked_message[chat_id] = max(
                            self.last_checked_message.get(chat_id, 0),
                            message.message_id
                        )

                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                self.LOGGER(__name__).warning(f"Monitor loop error: {e}")
                await asyncio.sleep(10)

    # ---------------------- Delete Message After Delay ----------------------
    async def delete_message_after(self, chat_id, message_id, delay):
        await asyncio.sleep(delay)
        try:
            message = await self.get_messages(chat_id, message_id)

            content_preview = ""
            if message.text:
                content_preview = message.text[:500]  # Limit text preview
            elif message.document:
                content_preview = f"Document: {message.document.file_name}"
            elif message.audio:
                content_preview = f"Audio: {message.audio.file_name}"
            elif message.video:
                content_preview = f"Video: {message.video.file_name}"
            elif message.photo:
                content_preview = f"Photo"

            await message.delete()

            # Log deleted message content to LOG_CHANNEL
            await self.send_message(
                self.LOG_CHANNEL,
                f"Deleted message <b>{message_id}</b> in private chat with <b>{chat_id}</b> after {delay} seconds.\n"
                f"Content: <code>{content_preview}</code>"
            )
        except Exception as e:
            self.LOGGER(__name__).warning(f"Failed to delete msg {message_id} in {chat_id}: {e}")

    # ---------------------- Command: /set_delete ----------------------
    @Client.on_message(filters.private & filters.command("set_delete") & filters.user(OWNER_ID))
    async def set_delete_time_cmd(self, bot: Client, message: Message):
        try:
            args = message.text.split()
            if len(args) != 2 or not args[1].isdigit():
                await message.reply("Usage: /set_delete <seconds>")
                return

            seconds = int(args[1])
            if seconds < 5 or seconds > 86400:
                await message.reply("Please choose a time between 5 seconds and 24 hours.")
                return

            await set_user_delete_time(message.chat.id, seconds)
            await message.reply(f"✅ Auto-delete time set to {seconds} seconds for your private chat.")
        except Exception as e:
            await message.reply(f"❌ Failed to set delete time: {e}")

    # ---------------------- Stop & Run ----------------------
    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())
