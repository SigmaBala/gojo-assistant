



import random
import aiohttp
import uuid
import config
import os

from datetime import date
from urllib.parse import quote
from nandha.db.couple import *
from nandha import pbot, LOGGER
from nandha.helpers.decorator import Command, admin_check, only_groups
from telegram import constants, helpers, InputMediaPhoto


__module__ = "Couples"


__help__ = """
*Commands*:
/couple, /divorce, /couples,
/rmcouples

```
/couple: 
A royal couple module that generates a unique couple image. Each day, two people are chosen as a couple. New couples will be selected the next day when the command is used again.
/divorce: 
Ends the marriage of the couple you were assigned.
/couples: 
Shows the couples that are already married in the chat.
/rmcouples: clear all couples in chat.
```
"""


PROMPTS = [
    "anime couple in a playful snowball fight",
    "anime couple watching fireworks",
    "anime couple enjoying a sunset",
    "anime couple riding bicycles together",
    "anime couple sharing a milkshake",
    "anime couple building a sandcastle",
    "anime couple on a ferris wheel",
    "anime couple in a passionate kiss under the moonlight",
    "anime couple reading a book together",
    "anime couple in a cozy blanket fort",
    "anime couple at a music festival",
    "anime couple feeding each other",
    "anime couple walking hand in hand on the beach",
    "anime couple in matching outfits",
    "anime couple sharing headphones",
    "anime couple cooking together",
    "anime couple in a playful pillow fight",
    "anime couple celebrating a birthday",
    "anime couple in a coffee shop date",
    "anime couple in a friendly competition",
    "anime couple having a picnic",
    "anime couple exploring a city",
    "anime couple in a photo booth",
    "anime couple in a heartwarming reunion",
    "anime couple in a touching farewell",
    "anime couple visiting an amusement park",
    "anime couple ice skating",
    "anime couple painting together",
    "anime couple in a magical moment",
    "anime couple sharing a secret",
    "anime couple in a playful wrestling match",
    "anime couple in a surprise gift exchange",
    "anime couple in a warm embrace in winter",
    "anime couple in a forest adventure",
    "anime couple relaxing in a hot spring",
    "anime couple at a rooftop dinner",
    "anime couple in a spontaneous road trip",
    "anime couple watching a movie at home",
    "anime couple in a rainy day cuddle",
    "anime couple stargazing",
    "anime couple in a heartfelt conversation",
    "anime couple enjoying a carnival",
    "anime couple in a cute pet moment",
    "anime couple sharing a cozy moment in front of a fireplace",
    "anime couple in a silly dance",
    "anime couple taking a walk in a park",
    "anime couple enjoying a festival",
    "anime couple sharing a cotton candy",
    "anime couple in a tender forehead kiss",
    "anime couple in a passionate embrace",
    "cute anime couple holding hands",
    "angry anime couple arguing",
    "anime couple sharing a romantic kiss",
    "anime couple laughing together",
    "anime couple in a playful fight",
    "anime couple cuddling on a couch",
    "anime couple dancing under the stars",
    "anime couple in a loving gaze",
    "anime couple in a dramatic breakup",
    "anime couple sharing an umbrella in the rain",
    "anime couple on a cute date",
    "anime couple in a heated argument",
    "anime couple in a tender moment",
    "anime couple with one partner blushing",
    "anime couple in a passionate kiss",
    "anime couple in a cozy hug",
    "anime couple with one partner crying",
    "anime couple in a playful mood",
    "anime couple in a serious conversation",
    "anime couple in a surprise proposal",
    "anime couple in a loving hug",
    "anime couple with one partner comforting the other",
    "anime couple in a cute selfie",
    "anime couple in a passionate dance",
    "anime couple in a sweet kiss",
    "anime couple in a heated debate",
    "anime couple in a loving embrace",
    "anime couple in a playful chase",
    "anime couple in a romantic dinner",
    "anime couple in a cute argument",
    "anime couple in a passionate hug",
    "anime couple in a loving kiss",
    "anime couple in a playful tickle fight",
    "anime couple in a sweet moment",
    "anime couple in a heated discussion",
    "anime couple in a loving cuddle",
    "anime couple in a passionate moment",
    "anime couple in a cute hug",
    "anime couple in a romantic moment"
]


async def create_couple_image(bot):
      prompt = random.choice(PROMPTS)
      url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=1024&height=1024&seed={random.randint(1,10000)}"
      async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                      image_data = await response.read()
                      file_name = f"{uuid.uuid4()}_couple.jpeg"
                      with open(file_name, "wb+") as file:
                            file.write(image_data)
                      # send the photo to log channel
                      msg = await bot.send_photo(config.LOGS_CHANNEL, file_name)
                      os.remove(file_name)
                      return msg.photo[-1].file_id
            except Exception as e:
                  LOGGER.error(f'Error whiling generating couple image: {str(e)}')
                  return 'AgACAgQAAxUHZ1Q2EN9vjvhN07zG-QNGybEl4tsAAq2zMRuVewRRwIHAII7NSzEBAAMCAAN4AAM2BA'



async def send_couple(msg, man, woman, photo):
       today = date.today()
       man_mention = helpers.mention_html(user_id=man['user_id'], name=man['name'])
       woman_mention = helpers.mention_html(user_id=woman['user_id'], name=woman['name'])
       date_str = f"{today.year}-{today.month}-{today.day}"
       text = (
                  f"❣️ <b>Couple of the day (</b><code>{date_str}</code><b>)</b> ❣️\n\n"
                  f"🤵 <b>Husband</b>: <b>{man_mention}</b>\n"
                  f"👰 <b>Fiancée</b>: <b>{woman_mention}</b>\n\n"
                  f"✨ <b>Congrats By {config.BOT_USERNAME}</b>"
       )
       return await msg.edit_media(media=InputMediaPhoto(photo, caption=text, parse_mode=constants.ParseMode.HTML))



def get_opposite_person(couple_dict, user_id):
    """
    Get the opposite person's data from a couple dictionary
    
    :param couple_dict: Dictionary with 'man' and 'woman' keys
    :param user_id: User ID to check
    :return: Dictionary of the opposite person
    """
    if couple_dict['man']['user_id'] == user_id:
        return couple_dict['woman']
    elif couple_dict['woman']['user_id'] == user_id:
        return couple_dict['man']
    else:
        return None  # User not found in the couple




@Command('couples')
@only_groups
async def get_couples(update, context):
     m = update.effective_message
     user = m.from_user
     bot = context.bot
     chat = m.chat
     msg = await chat.send_message('❣️ *Check-ing couples in chat*', parse_mode=constants.ParseMode.MARKDOWN)
     couple = await get_couple(chat.id)
     if couple and len(couples:= couple.get('couples', [])) != 0:
            text = f"<b>💖 Couples in {chat.title} </b>💖\n\n<blockquote>"
            for idx, data in enumerate(couples, start=1):
                 man = data['man']
                 woman = data['woman']
                 man_mention = helpers.mention_html(user_id=man['user_id'], name=man['name'])
                 woman_mention = helpers.mention_html(user_id=woman['user_id'], name=woman['name'])
                 text += f"<b>{idx}, 🧑‍💼 {man_mention} & 👰 {woman_mention}</b>\n"
            text += f"</blockquote><b>\n\nBy {config.BOT_USERNAME}</b>"
            media = "AgACAgQAAxkBAAEBfIFnVIvmG68Wy0PKbrD0q5vmtVG4IgACQ7YxG6hnpFKJAAHfTierp2MBAAMCAAN5AAM2BA"
            if len(text) < 1024:
                 return await msg.edit_media(media=InputMediaPhoto(media, caption=text, parse_mode=constants.ParseMode.HTML))
            else:
                 return await msg.edit_text(text, parse_mode=constants.ParseMode.HTML)

     else:
         return await msg.edit_text('*👀 This chat has no couples yet. use /couple to find them.*', parse_mode=constants.ParseMode.MARKDOWN)
                
            


@Command('divorce')
@only_groups
async def divorce(update, context):
     m = update.effective_message
     user = m.from_user
     bot = context.bot
     chat = m.chat

     couple = await get_user_couple(chat.id, user.id)
     if couple and (await remove_couple_by_user(chat.id, user.id)):
          other = get_opposite_person(couple, user.id)
          mention = helpers.mention_html(user_id=other['user_id'], name=other['name'])
          return await m.reply_text(f'<b>You divorced with {mention} 💔</b>.', parse_mode=constants.ParseMode.HTML)
     else:
          return await m.reply_text("*You didn't married anyone yet. 🤣*", parse_mode=constants.ParseMode.MARKDOWN)
     

couple_process = {} # for avoid spam.

@Command('couple')
@only_groups
async def couple(update, context):
    m = update.effective_message
    bot = context.bot
    chat = m.chat
    today = date.today()
    msg = await m.reply_text('*👀 Checking couple of the day ...*', parse_mode=constants.ParseMode.MARKDOWN)
    couple = await get_couple(chat.id)
    if couple and len(couple.get('couples', [])) == 30:
        return await m.reply_text('🤯 *Maximum couples for this chat have been chosen, to clear couples in chat use /rmcouples.*')

    day = couple['day'] if couple and couple.get('day') else 0

    if day != today.day:
        # Let's find a new couple for the day
        if couple_process.get(chat.id, False):
            return await msg.edit_text(
                '*Spammer spotted!* 💀',
                parse_mode=constants.ParseMode.MARKDOWN
            )

        couple_process[chat.id] = True
        await msg.edit_text(
            '*💖 Finding new couple of the day ...*',
            parse_mode=constants.ParseMode.MARKDOWN
        )
        members = []
        members_data = []
        async for m in pbot.get_chat_members(chat.id):
            if m.user.is_bot or m.user.is_deleted:  # skip bots and deleted accounts
                continue
            else:
                members.append(m.user.id)
                members_data.append({m.user.id: m.user})

        if not members:
            couple_process.pop(chat.id, None)
            return await msg.edit_text("👀 *I couldn't find anyone here to make a match.*", parse_mode=constants.ParseMode.MARKDOWN)

        users = await get_users_not_in_couples(chat.id, members)
        if len(users) < 2:
            couple_process.pop(chat.id, None)
            return await msg.edit_text("*🤣 We need more people to match a couple since most of them are already coupled!*", parse_mode=constants.ParseMode.MARKDOWN)

        # Choose two persons in chat who are not married yet
        man_id, woman_id = random.sample(users, 2)
        man_info = next(d[man_id] for d in members_data if man_id in d)
        woman_info = next(d[woman_id] for d in members_data if woman_id in d)
        man = {'user_id': man_info.id, 'name': man_info.full_name}
        woman = {'user_id': woman_info.id, 'name': woman_info.full_name}

        await msg.edit_text("😍 *New couple is decided, now making couple's art for them ...*", parse_mode=constants.ParseMode.MARKDOWN)
        photo = await create_couple_image(bot)
        if await update_couple(chat.id, man=man, woman=woman, day=today.day, photo_id=photo):
            try:
                await send_couple(msg, man, woman, photo)
            except Exception as e:
                couple_process.pop(chat.id, None)
                return await msg.edit_text(f"👀 *Looks like we encountered an error when sending couple image*: `{str(e)}`.", parse_mode=constants.ParseMode.MARKDOWN)
        else:
            couple_process.pop(chat.id, None)
            return await msg.edit_text("*Couple are not updated 🤔 what's wrong.*", parse_mode=constants.ParseMode.MARKDOWN)
    else:
        man = couple['man']
        woman = couple['woman']
        photo = couple.get('photo_id', 'AgACAgQAAxUHZ1Q2EN9vjvhN07zG-QNGybEl4tsAAq2zMRuVewRRwIHAII7NSzEBAAMCAAN4AAM2BA')
        try:
            await send_couple(msg, man, woman, photo)
        except Exception as e:
            couple_process.pop(chat.id, None)
            return await msg.edit_text(f"👀 *Looks like we encountered an error when sending couple image*: `{str(e)}`.", parse_mode=constants.ParseMode.MARKDOWN)
        finally:
            couple_process.pop(chat.id, None)




@Command('rmcouples')
@admin_check('can_change_info')
@only_groups
async def removeCouples(update, context):
        m = update.effective_message
        chat = m.chat
        doc = await remove_couple(chat.id)
        if doc:
             await m.reply_text('😼 *Every couples in this chat has been cleaned.*', parse_mode=constants.ParseMode.MARKDOWN)
        else:
             await m.reply_text("✋ *Looks like there's no single couples saved.*", parse_mode=constants.ParseMode.MARKDOWN)
        

               
          
               
          
       
