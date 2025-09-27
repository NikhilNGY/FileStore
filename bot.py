from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
from datetime import datetime, timedelta
import sys
from config import *

TIME_LIMIT = timedelta(hours=4)  # 4 hours threshold

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
        """Efficiently delete user file messages older than 4 hours."""
        while True:
            try:
                async for dialog in self.get_dialogs():
                    if dialog.chat.type != "private":
                        continue

                    last_msg_id = self.last_checked_message.get(dialog.chat.id, 0)
                    async for message in self.get_chat_history(dialog.chat.id, limit=1000, reverse=True):
                        if message.message_id <= last_msg_id:
                            break  # Already processed

                        msg_time = datetime.utcfromtimestamp(message.date)
                        if datetime.utcnow() - msg_time < TIME_LIMIT:
                            break  # Stop if message is newer than 4 hours

                        # Delete user file messages
                        if message.from_user and message.from_user.id != self.me.id:
                            if message.document or message.audio or message.video or message.photo:
                                try:
                                    await message.delete()
                                except:
                                    pass

                        # Update last processed message
                        self.last_checked_message[dialog.chat.id] = max(
                            self.last_checked_message.get(dialog.chat.id, 0),
                            message.message_id
                        )

                await asyncio.sleep(600)  # wait 10 minutes before next cleanup
            except Exception as e:
                self.LOGGER(__name__).warning(f"Cleanup error: {e}")
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
