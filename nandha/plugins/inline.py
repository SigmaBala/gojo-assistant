

import config
import re
import random
import logging

from urllib.parse import quote

from nandha.helpers.utils import UserId, file_best_name, encode_to_base64
from telegram import InlineQueryResultsButton, InputTextMessageContent, SwitchInlineQueryChosenChat, InlineQueryResultCachedAudio, InlineQueryResultCachedVideo, InlineQueryResultCachedDocument, InlineQueryResultArticle, InlineQueryResultGif, constants, InlineQueryResultPhoto, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import InlineQueryHandler
from nandha import app
from nandha.db.user_characters import USER_CHARACTERS
from nandha.db.characters import CHARACTERS
from nandha.db.autofilter import get_files_by_name, get_latest_files





MY_INLINE_BTN = InlineKeyboardMarkup(
              [[
                InlineKeyboardButton(text='🔎 Movies', switch_inline_query_current_chat='autofilter #movies'),
                InlineKeyboardButton(text='🔎 Songs', switch_inline_query_current_chat='autofilter #songs'),
                InlineKeyboardButton(text='🔎 Animes', switch_inline_query_current_chat='autofilter #anime'),
                InlineKeyboardButton(text='🔎 Apps', switch_inline_query_current_chat='autofilter #apps'),
              ],[
                InlineKeyboardButton(text=f'✨ {config.BOT_USERNAME}', url=f'https://t.me/{config.BOT_USERNAME[1:]}?start=help'),
]]
)




async def autofilter(user_id: int, query: [str,None] = None, type: [str,None] = None):


       username = config.BOT_USERNAME[1:]
       types = ['anime', 'apps', 'songs', 'movies', 'all']

       def add(user_id: int, username: str, files: list):
            results = []
            id = UserId()
            if not files or len(files) == 0:
                results.append(
                     InlineQueryResultArticle(
                         id=id,
                         title="❌ No Files Found.",
                         input_message_content=InputTextMessageContent(f"❌ No files found for '{query}'"),
                         thumbnail_url="https://i.ibb.co/hFcsjVHk/a0bb20b4-ee74-4e3a-84fd-b838c85da4ca-jpg.jpg"
                 ))
                return results

            text = \
"""
📛 *File Name*: `{name}`
🔗 *Share Link*: `{link}`

*By @{username}*
"""

            for file in files:

                 id = UserId()
                 index = file['index']
                 file_id = file.get('file_id', None)
                 encoded_string = encode_to_base64(f"{user_id}&{index}")
                 link = f"https://t.me/{username}?start=afFile-{encoded_string}"
                 name = file_best_name(file['file_name'])
                 
                 buttons = InlineKeyboardMarkup([[InlineKeyboardButton(text="🔗 Share", url=f"tg://share?text={quote(name)}&url=%60{link}%60"), InlineKeyboardButton('📁 File', url=link)]])
                 
                 results.append(
                 InlineQueryResultArticle(
                         id=id,
                         title=name,
                         input_message_content=InputTextMessageContent(text.format(name=name, link=link, username=username), parse_mode=constants.ParseMode.MARKDOWN),
                         thumbnail_url="https://i.ibb.co/T6KGb4R/f5edc362-cd79-43d4-853f-b46e3769c3da-jpg.jpg",
                         reply_markup=buttons
                         
                 ))

            return results

       if not query and not type:
            files = await get_latest_files()
            results = add(user_id, username, files)
            return results

       else:
            if type and type.lower() not in types:
                 results = []
                 results.append(
                     InlineQueryResultArticle(
                         id=id,
                         title="❌ Incorrect Filter Type:",
                         input_message_content=InputTextMessageContent(f"❗ Only Valid Types: {' ,'.join(types)}"),
                         thumbnail_url="https://i.imgur.com/XNMMScB.jpeg"
                 ))
                 return results

            else:
                files = await get_files_by_name(query, type, limit=45)
                results = add(user_id, username, files)
                return results




async def inline_query(update, context) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    user = update.inline_query.from_user
   
    if not query:  # empty query should be handled
         results = [
           InlineQueryResultArticle(
           id=UserId(),
           title="Hey there! Its Gojo 😎",
           input_message_content=InputTextMessageContent(f"I'm {config.BOT_NAME}"),
           reply_markup=MY_INLINE_BTN
           )
         ]
         return await update.inline_query.answer(results)


    elif query.split()[0].lower() == "autofilter":
          query = query.split(maxsplit=1)[1] if len(query.split()) > 1 else None
          pattern = re.compile(r'#(\w+)', re.IGNORECASE)
          type = None
          if query:
              type = pattern.search(query)
              if type:
                  type = type.group(1)
                  query = pattern.sub('', query).strip()
          results = await autofilter(user.id, query, type)
          try:
              return await update.inline_query.answer(results, cache_time=2, auto_pagination=True)    
          except Exception as e:
                   pass
       
    elif query.split()[0].lower() == "mycharacters":
          results = []

          user_document = next((doc for doc in USER_CHARACTERS if doc.get('user_id', 0) == user.id), None)
          if user_document:
               characters = user_document['characters']
               for _, character in characters.items():
                    name = character['character_name']
                    character_id = character['character_id']
                    health = character['health']
                    attack = character['attack']
                    rarity_type = character['rarity_type']
                    image = random.choice(character['images'])
                    buttons = InlineKeyboardMarkup([[
                         InlineKeyboardButton(text="Shop 🛒", callback_data=f"cshop#{character_id}#{user.id}")
              ]])
                    text = \
f"""
🌀 *Name*: `{name}`
🆔 *Character id*: `{character_id}`

💚 *Health*: `{health} HP`
🏅 *Rarity*: `type {rarity_type}`
"""
                    results.append(
                         InlineQueryResultPhoto(
                          id=UserId(),
                          title = name,
                          thumbnail_url = image,
                          photo_url = image,
                          caption=text,
                          parse_mode = constants.ParseMode.MARKDOWN,
                          reply_markup = buttons,
                   )
              )
               return await update.inline_query.answer(results, cache_time=2, auto_pagination=True)    

          else:
              results.append(
                    InlineQueryResultArticle(
                        id=UserId(),
                        title=f"❌ No characters found for {user.full_name}",
                        input_message_content=InputTextMessageContent(
                        message_text = "🤧 *You don't own any characters.*",
                        parse_mode = constants.ParseMode.MARKDOWN
                      ),
                      
                    )
              )
              return await update.inline_query.answer(results, cache_time=2, auto_pagination=True)    

                   
              
    elif query.split()[0].lower() == "characters":
          results = []
          
          for character in CHARACTERS:
              
              character_id = character['character_id']
              name = character['character_name']
              health = character['health']
              attack = character['attack']
              rarity_type = character['rarity_type']
              cash = character['cash']
              image = random.choice(character['images'])
              buttons = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="Buy 💲", callback_data=f"cbuy#{character_id}#{user.id}"),
              ]])

              
              text = \
f"""
🌀 *Name*: `{name}`
🆔 *Character id*: `{character_id}`

💚 *Health*: `{health} HP`
🏅 *Rarity*: `type {rarity_type}`
💸 *Cash*: `{cash} dollar`
"""
              results.append(
                InlineQueryResultPhoto(
                     id=UserId(),
                     title=name,
                     thumbnail_url=image,
                     photo_url=image,
                     caption=text,
                     parse_mode=constants.ParseMode.MARKDOWN,
                     reply_markup=buttons

                   )
              )
          return await update.inline_query.answer(results, cache_time=2, auto_pagination=True)    





app.add_handler(InlineQueryHandler(inline_query))
