import logging
from pyrogram import Client
from Config import Config

logging.basicConfig(level=logging.INFO)

plugins = dict(
    root="mwksub",
    include=[
        "forceSubscribe",
        "help"
    ]
)

app = Client(
     'ForceSubscribe',
      bot_token = Config.BOT_TOKEN,
      api_id = Config.API_ID,
      api_hash = Config.API_HASH,
      plugins = {"mwk": "mwk"}
)

app.run()
