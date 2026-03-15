
import json
import config
import aiohttp
import random
import base64

from urllib.parse import quote
from pyrogram import types, filters, enums
from nandha import pbot as bot
from nandha.helpers.scripts import Anime


__module__ = "Anime"

__help__ = '''
*Commands*:
/character, /anime, /animequote,
/sauce

```
- /character <query>: Search character info.
- /anime <query>: Search anime info along with characters info.
- /animequote: Get a random anime quote.
- /sauce: Reply to a nime character photo to get name. ( waifu catcher cheating )
```

*Example*:
`/anime jjk`
`/character gojo`
'''

anime = Anime()

characters_cached = {}
anime_cached = {}





@bot.on_callback_query(filters.regex("^pyrodel"))
async def pyro_delete(_, query: types.CallbackQuery):
      user_id = int(query.data.split("#")[1])
      if (user_id == query.from_user.id) or (query.message.chat.type == enums.ChatType.PRIVATE):
            await query.message.delete()
            return await query.answer("Deleted!")
      else:
           info = await query.message.chat.get_member(query.from_user.id)
           if info.privileges:
                  await query.message.delete()
                  return await query.answer("Deleted!")
           else:
                 return await query.answer("❌ You can't delete", show_alert=True)



def convert_to_keyboard(anime_id, data, user_id):
      buttons = []

      buttons.append([
                types.InlineKeyboardButton("Back 🔙", callback_data=f"anime_back#{anime_id}#{user_id}"),
     ])
     
      row = []
      for character in data:
           row.append(types.InlineKeyboardButton(str(character['name']), callback_data=f"chars_info#{anime_id}#{character['character_id']}#{user_id}"))
           if len(row) == 3:
               buttons.append(row)
               row = []
      if row:
           buttons.append(row)
      buttons.append([types.InlineKeyboardButton("❌ Close", callback_data=f"pyrodel#{user_id}")])
      return buttons
          

@bot.on_callback_query(filters.regex("^chars_back"))
async def pyro_chars_back(_, query: types.CallbackQuery):
      _, anime_id, user_id = query.data.split("#")
      user = query.from_user
      if user.id != int(user_id):
          return await query.answer("This is not your request!")
      else:
           characters = characters_cached.get(anime_id)
           if not characters:
                return await query.answer("This query was expired. search again.", show_alert=True)
           else:
                buttons = convert_to_keyboard(anime_id, characters, user.id)
                return await query.edit_message_caption(
                    caption="```\nCharacters information```",
                    reply_markup=types.InlineKeyboardMarkup(buttons)
           )



@bot.on_callback_query(filters.regex("^chars_info"))
async def pyro_chars_info(_, query: types.CallbackQuery):
      _, anime_id, character_id, user_id = query.data.split("#")
      user = query.from_user
      if user.id != int(user_id):
          return await query.answer("This is not your request!")
      character = await anime.get_character(character_id)
      if "error" in character:
            return await query.answer(f"❌ ERROR: {character['error']}", show_alert=True)
      else:
           nicknames = "\n".join(f"—» {name}" for name in character['nicknames'][:5]) if character.get('nicknames') else "Not available"
           caption = \
f"""
⚔️ **Character info**:

**Name**: {character['name']}, {character['name_kanji'] if character['name_kanji'] else "N/A"}
**NickName's**: 
`{nicknames}`

**About**: 
```\n{character['about'] if character['about'] else "N/A" [:350]} ...```
"""

           buttons = []
           buttons.append([
                types.InlineKeyboardButton("Back 🔙", callback_data=f"chars_back#{anime_id}#{user_id}"),
                types.InlineKeyboardButton("❌ Close", callback_data=f"pyrodel#{user_id}")
           ])
           await query.edit_message_media(
                  media=types.InputMediaPhoto(
                       media=character['photo_url'],
                       caption=caption
                  ),
                reply_markup=types.InlineKeyboardMarkup(buttons)
           )
                  

@bot.on_callback_query(filters.regex("^anime_chars"))
async def pyro_anime_chars(_, query: types.CallbackQuery):
      _, user_id, anime_id = query.data.split("#")
      user = query.from_user
      if user.id != int(user_id):
          return await query.answer("This is not your request!")
      else:
           characters = characters_cached.get(anime_id)
           if not characters:
                characters = await anime.get_characters(anime_id)
                if isinstance(characters, dict):
                     return await query.answer(f"❌ ERROR: {characters['error']}", show_alert=True)  
                     
           characters_cached[anime_id] = characters
           buttons = convert_to_keyboard(anime_id, characters, user.id)
           return await query.edit_message_caption(
                    caption="```\nCharacters information```",
                    reply_markup=types.InlineKeyboardMarkup(buttons)
                )
                                                      

@bot.on_callback_query(filters.regex("^anime_back"))
async def pyro_anime_back(_, query: types.CallbackQuery):
      _, anime_id, user_id = query.data.split("#")
      user = query.from_user
      if user.id != int(user_id):
          return await query.answer("This is not your request!")
      else:
           result = anime_cached.get(anime_id)
           if not result:
                return await query.answer("This query was expired, search again.", show_alert=True)
           else:
              anime_en = result['title_english']
              anime_ja = result['title_japanese']
              source = result['source']
              photo_url = result['photo_url']
              anime_id = result["anime_id"]                
              mal_url = result['mal_url']
              episodes = result['episodes']
              status = result['status']
              aired = result['aired']
              duration = result['duration']
              rating = result["rating"]
              synopsis = result["synopsis"] if result["synopsis"] else "N/A"
              trailer = result["trailer"]
              button = []
              if not trailer:
                 trailer = f"https://www.youtube.com/results?search_query={quote(anime_en+'+trailer')}"
                  
              buttons = types.InlineKeyboardMarkup(
                  [[
                       types.InlineKeyboardButton("🎬 Trailer", url=trailer),
                       types.InlineKeyboardButton("📝 Info", url=mal_url)],[
                       types.InlineKeyboardButton("⚔️ Character", callback_data=f"anime_chars#{user.id}#{anime_id}"),
                       types.InlineKeyboardButton("❌ Close", callback_data=f"pyrodel#{user.id}")
                   ]]
             )
              text = \
f"""
🎬 **Title (English)**: `{anime_en}`
🎥 **Title (Japanese)**: `{anime_ja}`
📚 **Source**: `{source}`
📺 **Episodes**: `{episodes}`
✅ **Status**: `{status}`
🗓️ **Aired**: `{aired}`
⏳ **Duration**: `{duration}`
⭐ **Rating**: `{rating}`

📝 **Synopsis**:
`{synopsis[:450]} ...`
"""
              return await query.edit_message_media(
                  media=types.InputMediaPhoto(
                       media=photo_url,
                       caption=text
                  ),
                     reply_markup=buttons
              )
              

@bot.on_message(filters.command("character") & ~filters.forwarded)
async def search_character(_, m: types.Message):
     if len(m.text.split()) < 2:
            return await m.reply_text("Character name required.")
     else:
        name = m.text.split(maxsplit=1)[1]
        user = m.from_user
        character = await anime.character(name)
        error = character.get('error')
        if error:
            return await m.reply_text(f"❌ ERROR: {error}")
        else:
           nicknames = "\n".join(f"—» {name}" for name in character['nicknames']) if character['nicknames'] else "Not available"
           caption = \
f"""
⚔️ **Character info**[\u200B]({character['photo_url']}):

**Name**: {character['name']}, {character['name_kanji']}
**NickName's**: 
`{nicknames}`

**About**: 
```\n{character['about'] if character['about'] else "N/A" [:2000]} ...```
"""

           buttons = []
           buttons.append([
                types.InlineKeyboardButton("❌ Close", callback_data=f"pyrodel#{user.id}")
           ])
           return await m.reply_text(
                       text=caption,
                       reply_markup=types.InlineKeyboardMarkup(buttons)
           )
        
     
@bot.on_message(filters.command("anime") & ~filters.forwarded)
async def search_anime(_, m: types.Message):

     global anime_cached
     if len(m.text.split()) < 2:
            return await m.reply_text("Anime name required.")
     else:
        name = m.text.split(maxsplit=1)[1]
        user = m.from_user
          
        result = await anime.search(name)
        if "error" in result:
             return await m.reply_text(f"❌ ERROR: `{result['error']}`")
        else:
             anime_en = result['title_english']
             anime_ja = result['title_japanese']
             source = result['source']
             anime_id = result["anime_id"]
             anime_cached[str(anime_id)] = result
             photo_url = result['photo_url']
             mal_url = result['mal_url']
             episodes = result['episodes']
             status = result['status']
             aired = result['aired']
             duration = result['duration']
             rating = result["rating"]
             synopsis = result["synopsis"] if result["synopsis"] else "N/A"
             trailer = result["trailer"]
             button = []
             if not trailer:
                 trailer = f"https://www.youtube.com/results?search_query={quote((anime_en if anime_en else anime_ja)+'+trailer')}"
                  
             buttons = types.InlineKeyboardMarkup(
                  [[
                       types.InlineKeyboardButton("🎬 Trailer", url=trailer),
                       types.InlineKeyboardButton("📝 Info", url=mal_url)],[
                       types.InlineKeyboardButton("⚔️ Character", callback_data=f"anime_chars#{user.id}#{anime_id}"),
                       types.InlineKeyboardButton("❌ Close", callback_data=f"pyrodel#{user.id}")
                   ]]
             )
             text = \
f"""
🎬 **Title (English)**: `{anime_en}`
🎥 **Title (Japanese)**: `{anime_ja}`
📚 **Source**: `{source}`
📺 **Episodes**: `{episodes}`
✅ **Status**: `{status}`
🗓️ **Aired**: `{aired}`
⏳ **Duration**: `{duration}`
⭐ **Rating**: `{rating}`

📝 **Synopsis**:
`{synopsis[:450]} ...`
"""
             return await m.reply_photo(
                     photo=photo_url,
                     caption=text,
                     reply_markup=buttons
             )
       


@bot.on_message(filters.command("sauce") & ~filters.forwarded)
async def _sauce(_, m: types.Message):
      r = m.reply_to_message
      if r and r.photo:
           photo = await r.download(in_memory=True)
           encoded_string = base64.b64encode(bytes(photo.getbuffer()))
           data = {
               'api_token': 'TEST-API-TOKEN',
               'photo_b64': encoded_string.decode()
           }
           url = "http://cheatbot.twc1.net/getName"

           msg = await m.reply("🔎 **Checking for character info ...**")
           async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:

                        if response.status != 200:
                            return await msg.edit_text("🤧 Api down or something went wrong server side.") 
                              
                        else:
                            result = await response.json()
                            if "message" in result:
                                return await msg.edit_text(result["message"])
                                  
                            name = result['name']
                            prefix = result['prefix']
                            sbot = result['bot_name']
                            text = (
                                  
                                 f"ℹ️ **Character**: {name}\n"
                                 f"🤖 **From bot**: @{sbot}\n\n"
                                 f"⚡ **Copy**: `{prefix} {name}`"
                                  
                            )
                            return await msg.edit_text(
                                      text=text
                            )
                             
      else:
           return await m.reply("*Reply to Anime Character Photo*.")


# Anime Random Quote
@bot.on_message(filters.command("animequote") & ~filters.forwarded)
async def animeQuote(_, message):
     m = message
     with open("./nandha/helpers/data/anime_quote.json") as file:
          data = json.load(file)
     quote = random.choice(data)
  
     text = \
f"""
#AnimeQuote

>{quote['content']}

Anime: **{quote['anime']['name']}**
By: **{quote['character']['name']}**
"""
  
     await m.reply_text(text, quote=True)
         
             
