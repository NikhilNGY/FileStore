import asyncio
from aiohttp import web
from plugins import web_server
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message
from datetime import datetime, timedelta
import sys
from config import *
from pymongo import MongoClient

# ---------------------- MongoDB Setup ----------------------
MONGO_CLIENT = MongoClient(DB_URI)
DB = MONGO_CLIENT[DB_NAME]
USER_SETTINGS = DB["user_settings"]  # per-user auto-delete times
DELETED_LOGS = DB["deleted_logs"]    # deleted messages logs

# ---------------------- MongoDB Helpers ----------------------
async def all_users():
    try:
        return [doc["user_id"] for doc in USER_SETTINGS.find({}, {"user_id": 1, "_id": 0})]
    except Exception as e:
        print(f"[Warning] Could not fetch users: {e}")
        return []

async def set_user_delete_time(user_id: int, seconds: int):
    try:
        USER_SETTINGS.update_one(
            {"user_id": user_id},
            {"$set": {"delete_seconds": seconds}},
            upsert=True
        )
    except Exception as e:
        print(f"[Error] Failed to set delete time for {user_id}: {e}")

async def get_user_delete_time(user_id: int, default: int = 30):
    try:
        doc = USER_SETTINGS.find_one({"user_id": user_id}, {"delete_seconds": 1, "_id": 0})
        return doc.get("delete_seconds", default) if doc else default
    except Exception as e:
        print(f"[Warning] Could not get delete time for {user_id}: {e}")
        return default

async def log_deleted_message(user_id: int, chat_id: int, message_id: int, content_preview: str):
    try:
        DELETED_LOGS.insert_one({
            "user_id": user_id,
            "chat_id": chat_id,
            "message_id": message_id,
            "content_preview": content_preview,
            "deleted_at": datetime.utcnow()
        })
    except Exception as e:
        print(f"[Warning] Failed to log deleted message {message_id} for user {user_id}: {e}")

async def cleanup_old_logs(days: int = 30):
    """Delete logs older than `days`."""
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = DELETED_LOGS.delete_many({"deleted_at": {"$lt": cutoff}})
        print(f"[Cleanup] Deleted {result.deleted_count} old log(s) older than {days} days.")
    except Exception as e:
        print(f"[Warning] Failed to cleanup old logs: {e}")

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
        self.last_checked_message = {}

    # ---------------------- Start ----------------------
    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = datetime.now()
        self.username = me.username

        # LOG_CHANNEL check
        try:
            db_chat = await self.get_chat(LOG_CHANNEL)
            self.LOG_CHANNEL = db_chat.id
            test = await self.send_message(chat_id=db_chat.id, text="✅ Bot Started Successfully")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Make sure the bot is admin in LOG_CHANNEL ({LOG_CHANNEL})"
            )
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..! Made by @KR_Picture")   

        # Start background tasks
        self.loop.create_task(self.monitor_private_messages())
        self.loop.create_task(self.periodic_cleanup())

        # Start Web Server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        await web.TCPSite(app_runner, "0.0.0.0", PORT).start()

    # ---------------------- Monitor Private Messages ----------------------
    async def monitor_private_messages(self):
        while True:
            try:
                try:
                    chat_ids = await all_users()
                except Exception as e:
                    self.LOGGER(__name__).warning(f"Could not fetch users: {e}")
                    chat_ids = []

                for chat_id in set(chat_ids):
                    last_msg_id = self.last_checked_message.get(chat_id, 0)
                    delete_seconds = await get_user_delete_time(chat_id) or 30

                    try:
                        async for message in self.get_chat_history(chat_id, limit=1000, reverse=True):
                            if message.message_id <= last_msg_id:
                                break
                            if message.chat.type != ChatType.PRIVATE:
                                continue
                            if message.from_user and message.from_user.id == self.me.id:
                                continue
                            if message.text or message.audio or message.video or message.document or message.photo:
                                asyncio.create_task(
                                    self.delete_message_after(chat_id, message.message_id, delete_seconds)
                                )
                            self.last_checked_message[chat_id] = max(
                                self.last_checked_message.get(chat_id, 0),
                                message.message_id
                            )
                    except Exception as e:
                        self.LOGGER(__name__).warning(f"Failed to process chat {chat_id}: {e}")

                await asyncio.sleep(10)

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
                content_preview = message.text[:500]
            elif message.document:
                content_preview = f"Document: {message.document.file_name}"
            elif message.audio:
                content_preview = f"Audio: {message.audio.file_name}"
            elif message.video:
                content_preview = f"Video: {message.video.file_name}"
            elif message.photo:
                content_preview = f"Photo"

            await message.delete()

            await log_deleted_message(
                message.from_user.id if message.from_user else chat_id,
                chat_id, message_id, content_preview
            )

            await self.send_message(
                self.LOG_CHANNEL,
                f"Deleted message <b>{message_id}</b> in private chat with <b>{chat_id}</b> after {delay} seconds.\n"
                f"Content: <code>{content_preview}</code>"
            )

        except Exception as e:
            self.LOGGER(__name__).warning(f"Failed to delete msg {message_id} in {chat_id}: {e}")

    # ---------------------- /set_delete Command ----------------------
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

    # ---------------------- Cleanup Task ----------------------
    async def periodic_cleanup(self):
        while True:
            await cleanup_old_logs(days=30)
            await asyncio.sleep(24 * 3600)

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
