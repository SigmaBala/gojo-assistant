
from pyrogram import Client, idle
#from pytgcalls import PyTgCalls
from telegram.ext import Defaults, ApplicationBuilder, Application, PicklePersistence
from motor.motor_asyncio import AsyncIOMotorClient
from telegram import constants
from telegraph.aio import Telegraph
from nandha.helpers.data.fonts import Fonts
from config import *

import time
import logging
import aiohttp
import asyncio
import random
import pyrogram


LOGGER = logging.getLogger(__name__)
START_TIME = time.perf_counter()


FORMAT = f"[Bot] %(message)s"
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler('logs.txt'), logging.StreamHandler()], format=FORMAT)
logging.getLogger('httpx').setLevel(logging.WARNING)


telegraph = Telegraph(access_token="80e1635aa3308ef9c583dac805436c1b5dc5995ce11d5fceb136650eb77f", domain="graph.org")
async def telegraph_create():
       await telegraph.create_account(
            short_name=BOT_NAME,
            author_name=BOT_NAME,
            author_url=("https://t.me/"+BOT_USERNAME[1:])
    )
  



db_client = AsyncIOMotorClient(DB_URL)
database = db_client['gojo']
db2_client = AsyncIOMotorClient(DB_URL2)
database2 = db2_client['gojo2']



async def send_restart(application: Application) -> None:
    await application.bot.send_message(
        chat_id=LOGS_CHANNEL,
        text="Just restarted yet!"
    )


font = Fonts.sim

ptb_defaults = Defaults(
    #parse_mode=constants.ParseMode.MARKDOWN,
    allow_sending_without_reply=True,
    do_quote=True,
)

# persistence = PicklePersistence(filepath='GojoAssistant') persistence(persistence)
app = ApplicationBuilder().defaults(ptb_defaults).token(TOKEN).post_init(send_restart).build()


pbot = Client("GojoPyroBot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, max_concurrent_transmissions=4)


user_client = Client("GojoUserPyroBot", api_id=API_ID, api_hash=API_HASH, session_string=USER_STRING, max_concurrent_transmissions=4)
#userbot = PyTgCalls(user_client)

multi_clients[0] = pbot
work_loads[0] = 0


async def start_pyro_clients():
     await pbot.start()
     try:
        await user_client.start()
     except Exception as e:
        LOGGER.error(f'❌ ERROR when starting USERBOT: {e}')
     LOGGER.info("Pyrogram [USER, BOT] Started!")

     
aiohttpsession: aiohttp = aiohttp.ClientSession()

async def initialize_database():
    from nandha.db import users, afk, chatbot, ignore, characters, riddle, user_characters, autofilter, notes, fsub
    await afk.initialize_afk_users()
    await users.initialize_db_premium_users()
    #await characters.initialize_characters()
    #await user_characters.initialize_user_characters()
    await autofilter.initialize_db_chats()
    await chatbot.initialize_db_chats()
    await ignore.initialize_db_users()
    await notes.initialize_chats()
    await fsub.initialize_chats()
    await riddle.initialize_db_chats()

    LOGGER.info(
      "Initialized (All) - [riddle, premium, afk, chatbot, blocks, autofilter, notes, fsub] —» DATABASE"
    )
  
