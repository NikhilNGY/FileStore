# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import os
from os import environ,getenv
import logging
from logging.handlers import RotatingFileHandler

#rohit_1888 on Tg
#--------------------------------------------
#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
APP_ID = int(os.environ.get("APP_ID", "2468192")) #Your API ID from my.telegram.org
API_HASH = os.environ.get("API_HASH", "4906b3f8f198ec0e24edb2c197677678") #Your API Hash from my.telegram.org
#--------------------------------------------

CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1001683081282")) #Your db channel Id
OWNER = os.environ.get("OWNER", "nikhil5757h") # Owner username without @
OWNER_ID = int(os.environ.get("OWNER_ID", "2068233407")) # Owner id
#--------------------------------------------
PORT = os.environ.get("PORT", "8080")
#--------------------------------------------
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://Filter01:ei62heT4O81OyNyl@Filter01.6kyybcz.mongodb.net/?retryWrites=true&w=majority&appName=Filter01")
DB_NAME = os.environ.get("DATABASE_NAME", "Filter1")
#--------------------------------------------
FSUB_LINK_EXPIRY = int(os.getenv("FSUB_LINK_EXPIRY", "10"))  # 0 means no expiry
BAN_SUPPORT = os.environ.get("BAN_SUPPORT", "https://t.me/Nikhil5757h")
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "200"))
#--------------------------------------------
START_PIC = os.environ.get("START_PIC", "")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg")
#--------------------------------------------

#--------------------------------------------
HELP_TXT = "<b><blockquote>Aɴʏ Iꜱꜱᴜᴇꜱ Mᴏᴠɪᴇ Fɪʟᴇꜱ Cᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ\n      \n🍁 Oᴡɴᴇʀ: <a href=https://t.me/Nikhil5757h>Ｄ Ｉ Ｃ Ｔ Ａ ＴＯ Ｒ</a></blockquote></b>"
ABOUT_TXT = "<b><blockquote>Aɴʏ Iꜱꜱᴜᴇꜱ Mᴏᴠɪᴇ Fɪʟᴇꜱ Cᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ\n      \n🍁 Oᴡɴᴇʀ: <a href=https://t.me/Nikhil5757h>D Ｉ Ｃ Ｔ Ａ Ｔ Ｏ Ｒ</a></blockquote></b>"
#--------------------------------------------
#--------------------------------------------
START_MSG = os.environ.get("START_MESSAGE", "<b><blockquote>Fʀɪᴇɴᴅꜱ.......🖤\n  Wᴇ Hᴀᴠᴇ Aʟʀᴇᴀᴅʏ Lᴏꜱᴛ Mᴀɴʏ Cʜᴀɴɴᴇʟꜱ Dᴜᴇ Tᴏ Cᴏᴘʏʀɪɢʜᴛ... Sᴏ Jᴏɪɴ Uꜱ Bʏ Gɪᴠɪɴɢ Yᴏᴜʀ Sᴜᴘᴘᴏʀᴛ, Cᴏᴏᴘᴇʀᴀᴛɪᴏɴ Aɴᴅ Bʟᴇꜱꜱɪɴɢꜱ Tᴏ Tʜɪꜱ Nᴇᴡ Cʜᴀɴɴᴇʟ Oꜰ Oᴜʀꜱ 🙏🙏 Tᴇᴀᴍ: @KR_Picture</blockquote></b>")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {mention}\n\n<b><blockquote>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b></blockquote>")

CMD_TXT = """<b><blockquote>Aɴʏ Iꜱꜱᴜᴇꜱ Mᴏᴠɪᴇ Fɪʟᴇꜱ Cᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ\n      \n🍁 Oᴡɴᴇʀ: <a href=https://t.me/Nikhil5757h>Ｄ Ｉ Ｃ Ｔ Ａ ＴＯ Ｒ</a></blockquote></b>"""
#--------------------------------------------
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>• ʙʏ @KR_Picture</b>") #set your Custom Caption here, Keep None for Disable Custom Caption
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False #set True if you want to prevent users from forwarding files from bot
#--------------------------------------------
#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'
#--------------------------------------------
BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"
#--------------------------------------------


LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
   
