

import random
import html

from telegram import helpers, constants, MessageEntity
from telegram.ext import filters, ApplicationHandlerStop
from nandha.helpers.decorator import Messages, Command, admin_check
from nandha.db.afk import AFK_USERS, add_user_afk, get_user_afk, remove_user_afk
from nandha.db.users import get_user_id_by_username




__module__ = "Afk"

__help__ = """
*Commands*:
/afk

```
- /afk: for tell  someone in online that
your away from keyboard using bot

Once you return to online in group where bot is. then bot greet you in group (:

```
*Example*:
`/afk I'm studying`
`/afk I'm watching anime`
"""


AFK_BACK_STRING_LIST = [
    "🎉 Welcome back, {}! The cursed spirits can finally relax!",
    "👀 Look who decided to show up! It’s the sorcerer, {}!",
    "🔥 Hot stuff alert! {} has returned to exorcise the vibes!",
    "😎 You missed me, didn’t you? Just kidding, {}! You know I’m unbeatable!",
    "🚀 Blast off! {} is back, ready to unleash some cursed techniques!",
    "🍕 Pizza’s here, and so is the strongest sorcerer, {}!",
    "🎈 Time to celebrate, {} is back to save the day!",
    "💥 Boom! {} has re-entered the chat like a true sorcerer!",
    "🕺 Dance time! {} is back on the battlefield, let’s go!",
    "🤩 Did you miss me? Nah, just kidding, {}! You know I’m always around!",
    "🌟 Shine bright like a cursed technique, {} is here to dazzle!",
    "🎤 Mic check! 1, 2, 3... it’s the legendary sorcerer, {}!",
    "🦸‍♂️ Superhero landing! Welcome back, {}! Time to exorcise some spirits!",
    "🎭 The show can go on, {} is here to dominate the stage!",
    "🍹 Time for some fun, {} is back in the Jujutsu game!"
]


AFK_MESSAGES = [
    "User  {} is currently on a quest for snacks. 🍕",
    "User  {} has entered the realm of the AFK. 💤",
    "User  {} is busy fighting the urge to procrastinate. ⚔️",
    "User  {} is off saving the world... or just their phone battery. 🔋",
    "User  {} has temporarily vanished like a cursed spirit. 👻",
    "User  {} is in a deep meditation... or napping. 🧘‍♂️",
    "User  {} is away, probably plotting world domination. 🌍"
]

AFK_STRING = """
<b>⚡ Yo, {} is chillin' AFK!</b>

<b>🕣 Since</b>: <code>{}</code>
<b>🕣 Now</b>: <code>{}</code>

<b>📑 Reason</b>: 
<code>{}</code>
"""

BACK_AFK_STRING = """
<b>{}</b>

<b>🕣 Since</b>: <code>{}</code>
<b>🕣 Now</b>: <code>{}</code>

<b>📑 Reason</b>: 
<code>{}</code>
"""

@Messages(filters=filters.ChatType.GROUPS, group=1)
async def NoLongerAfk(update, context):
      message = update.effective_message
      user = update.effective_user
     
      if user.id in AFK_USERS:
            afk = await get_user_afk(user.id)
            reason = html.escape(afk.get('reason', '✋ Reason Not Provided.'))
            datetime = afk['datetime']
            await remove_user_afk(user.id)
            mention = helpers.mention_html(user.id, user.first_name)
            afk_string = random.choice(AFK_BACK_STRING_LIST).format(mention)
            await message.reply_text(
                  text=BACK_AFK_STRING.format(afk_string, datetime, str(message.date).split('+')[0], reason),
                  parse_mode=constants.ParseMode.HTML
            )
      


@Messages(filters=filters.ChatType.GROUPS, group=2)
async def ReplyAfk(update, context):
     message = update.effective_message
     reply = message.reply_to_message
     try:
        async def check_afk(message, user_id):
             if user_id not in AFK_USERS: return
             user = await get_user_afk(user_id)
             mention = helpers.mention_html(user['user_id'], user['first_name'])
             datetime = user['datetime']
             reason = html.escape(user['reason'])
             return await message.reply_text(
                text=AFK_STRING.format(mention, datetime, str(message.date).split('+')[0], reason),
                parse_mode=constants.ParseMode.HTML
           )
     except Exception as e:
          print(repr(e))
     entities = message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION])
     if entities:
          for ent in entities:
             if ent.type == MessageEntity.TEXT_MENTION:
                   user_id = ent.user.id         
                   await check_afk(message, user_id)
             elif ent.type == MessageEntity.MENTION:
                   username = message.text[ ent.offset:ent.offset + ent.length ][1:] # for extract username in message text only if message mention entities
                   user_id = await get_user_id_by_username(username)
                   if user_id: 
                       await check_afk(message, user_id)
                    
     elif reply and not reply.sender_chat:
         user_id = reply.from_user.id
         await check_afk(message, user_id)
     
     


@Command('afk', block=True)
async def SetAfk(update, context):
     message = update.effective_message
     if message.sender_chat: return
     first_name = message.from_user.first_name
     user_id = message.from_user.id
     datetime = str(message.date).split('+')[0]
     if len(message.text) >= 100: 
         await message.reply_text('🧏 Your Afk Reason was shortened to 100 characters.')
     
     reason = message.text.split(maxsplit=1)[1][:100] if len(message.text.split()) >= 2 else "✋ Reason Not Provided. "

  
     await add_user_afk(
         user_id=user_id,
         first_name=first_name,
         datetime=datetime,
         reason=reason
     )
  
     mention = helpers.mention_html(user_id, first_name)
  
     await message.reply_text(
          f"<b>{random.choice(AFK_MESSAGES).format(mention)}</b>",
          parse_mode=constants.ParseMode.HTML
     )
     
     raise ApplicationHandlerStop
     
