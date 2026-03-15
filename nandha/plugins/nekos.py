
from telegram import constants, helpers
from nandha import aiohttpsession as session
from nandha.helpers.decorator import Command



__module__ = "Nekobest"

__help__ = """
*Commands:*
/neko, /waifu, /husbando, /kitsune,
/lurk, /shoot, /sleep, /shrug, 
/stare, /wave, /poke, /smile, /peck,
/wink, /blush, /smug, /tickle, /yeet, 
/think, /highfive, /feed, /bite,
/bored, /nom, /yawn, /facepalm,
/cuddle, /kick, /happy, /hug, 
/baka, /pat, /nod, /nope, /kiss, 
/dance, /punch, /handshake, /slap, 
/cry, /pout, /handhold, /thumbsup,
/laugh.

```
This are all available endpoints in nekos.best api
use this module to get random anime photos and gifs.
```
"""


endpoint_names = [
  
    "neko",
    "waifu",
    "husbando",
    "kitsune",
    "lurk",
    "shoot",
    "sleep",
    "shrug",
    "stare",
    "wave",
    "poke",
    "smile",
    "peck",
    "wink",
    "blush",
    "smug",
    "tickle",
    "yeet",
    "think",
    "highfive",
    "feed",
    "bite",
    "bored",
    "nom",
    "yawn",
    "facepalm",
    "cuddle",
    "kick",
    "happy",
    "hug",
    "baka",
    "pat",
    "nod",
    "nope",
    "kiss",
    "dance",
    "punch",
    "handshake",
    "slap",
    "cry",
    "pout",
    "handhold",
    "thumbsup",
    "laugh"
]




@Command(endpoint_names)
async def nekoBest(update, context):
     m = update.effective_message
     command = m.text.split()[0][1:].lower()
     api_url = "https://nekos.best/api/v2/" + command
     media, anime = (lambda data: (data['results'][0].get('url'), data['results'][0].get('anime_name', f'{command.capitalize()} UWU!')))(await ((await session.get(api_url))).json())
     reply = m.reply_to_message
     if reply:
         ruser = reply.from_user
         user = m.from_user
         m = reply
         text = f"<b>{helpers.mention_html(user_id=user.id, name=user.full_name)} {command} {helpers.mention_html(user_id=ruser.id, name=ruser.full_name)}</b>\n\n<b>✨ Source</b>: <code>{anime}</code>"
     else:
         user = context.bot
         ruser = m.from_user
         text = f"<b>{helpers.mention_html(user_id=user.id, name=user.first_name)} {command} {helpers.mention_html(user_id=ruser.id, name=ruser.full_name)}</b>\n\n<b>✨ Source</b>: <code>{anime}</code>"
    
     if media.endswith('png'):
         return await m.reply_photo(
             media, 
             caption=text,
             parse_mode=constants.ParseMode.HTML
         )
     elif media.endswith('gif'):
         return await m.reply_animation(
             media,
             caption=text, 
             parse_mode=constants.ParseMode.HTML
         )
     else:
         return await m.reply_document(
              media,
              caption=text, 
              parse_mode=constants.ParseMode.HTML
         )        

