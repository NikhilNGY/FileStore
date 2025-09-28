from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
from datetime import datetime, timedelta
import sys
from config import *
from database import all_users, all_groups  # make sure these exist

# Time limit for auto-deletion (configurable)
TIME_LIMIT = timedelta(hours=AUTO_DELETE_HOURS)

name = """
 BY KR Picture
"""

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

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        self.username = usr_bot_me.username

        # Check DB channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID ({CHANNEL_ID})"
            )
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/KR_Picture for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..! Made by @KR_Picture")   

        # Start background cleanup task
        self.loop.create_task(self.cleanup_old_files())

        # Start Web Server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        await web.TCPSite(app_runner, "0.0.0.0", PORT).start()

        try:
            await self.send_message(
                OWNER_ID, 
                text="<b><blockquote> Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ by @KR_Picture</blockquote></b>"
            )
        except: 
            pass

    async def cleanup_old_files(self):
        """Delete user file messages older than TIME_LIMIT in DB channel, users, and groups."""
        while True:
            try:
                # Collect all chat IDs: DB channel + users + groups
                chat_ids = [CHANNEL_ID]

                try:
                    chat_ids.extend([g.id for g in await all_groups()])
                except Exception as e:
                    self.LOGGER(__name__).warning(f"Could not fetch groups: {e}")

                try:
                    chat_ids.extend([u.id for u in await all_users()])
                except Exception as e:
                    self.LOGGER(__name__).warning(f"Could not fetch users: {e}")

                for chat_id in set(chat_ids):
                    last_msg_id = self.last_checked_message.get(chat_id, 0)

                    async for message in self.get_chat_history(chat_id, limit=1000, reverse=True):
                        if message.message_id <= last_msg_id:
                            break  # already processed

                        msg_time = datetime.utcfromtimestamp(message.date)
                        if datetime.utcnow() - msg_time < TIME_LIMIT:
                            break  # stop if message is newer than threshold

                        # Delete only user messages (not bot's own)
                        if message.from_user and message.from_user.id != self.me.id:
                            if message.document or message.audio or message.video or message.photo:
                                try:
                                    await message.delete()
                                except Exception as e:
                                    self.LOGGER(__name__).warning(
                                        f"Failed to delete msg {message.message_id} in {chat_id}: {e}"
                                    )

                        # Update last processed message
                        self.last_checked_message[chat_id] = max(
                            self.last_checked_message.get(chat_id, 0),
                            message.message_id
                        )

                await asyncio.sleep(600)  # 10 min pause before next cleanup
            except Exception as e:
                self.LOGGER(__name__).warning(f"Cleanup loop error: {e}")
                await asyncio.sleep(600)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        """Run the bot."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("Bot is now running. Thanks to @nikhil5757h")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())
