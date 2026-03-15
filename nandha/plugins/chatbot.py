


import os
import re
import urllib
import random

from aiohttp import FormData
from telegram import constants, helpers, error, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters
from nandha import BOT_ID, UPDATE_CHANNEL, BOT_USERNAME, telegraph, LOGGER, aiohttpsession as session, STICKERS

from nandha.helpers.decorator import Command, Messages, admin_check, send_action, only_premium
from nandha.helpers.scripts import AiChats, paste, google_search as search_query
from nandha.helpers.filters import ChatBotReply
from nandha.helpers.utils import UserId, search_text, split_message
from nandha.db.chatbot import add_chat, get_all_chats, remove_chat, CHAT_IDS


MAX_CHAT = 20
ai = AiChats()
temp_data = {}
users = {} 


__module__ = "Gojo AI"


__help__ = f'''
*Commands*:
/chatbot, /gojoclear,
/gojodata, /gojocontinue

```
- /chatbot <mode>: Enable or disable the chatbot in your chat
  Modes: on, off, enable, disable
  Note: The chatbot has access to real-time information for accurate responses

- /gojoclear: Clear your conversation history with Gojo
- /gojodata: Download your conversation history with Gojo
- /gojocontinue: Request a follow-up response to your previous question
```

*Examples*:
`/chatbot on`
`/chatbot off`
`@gojo hi`
`Reply to gojo's any message`

```Look:
The chatbot feature is now available in both
private and public chats. Enjoy talking with Gojo! 😍
```

```Note:
Gojo will automatically clear your conversation history when it reaches {MAX_CHAT} messages.
```
'''


def is_do_search(query: str):
    filters = ['recent', 'current', 'latest', 'news', 'new', '#search', 'update']
    pattern = re.compile(r'|'.join(filters), flags=re.IGNORECASE)
    return pattern.search(query)




async def handle_stickers(r, m, bot):

         if (r and r.sticker) or (r and (r.from_user.id == bot.id)):
              STICKERS.add(m.sticker.file_id)
              if r.sticker:
                  STICKERS.add(r.sticker.file_id)
                
              stickers_list = list(STICKERS)
              random.shuffle(stickers_list)
              sticker = random.choice(stickers_list)
              return await m.reply_sticker(sticker)
           
         return False 
       


@Messages(filters=(~filters.COMMAND & ChatBotReply & ~filters.UpdateType.EDITED & ~filters.VIA_BOT)) # group = 0
async def ChatBotReply(update, context):
     message = m = update.effective_message
     reply = message.reply_to_message
     user = update.effective_user
     chat = m.chat
     bot = context.bot

     if message.sticker:               
          return await handle_stickers(reply, message, bot)
          

     await chat.send_chat_action(action=constants.ChatAction.TYPING) # typing action
  
     process = users.get(user.id, False)
     if process: return

     users[user.id] = True
     msg = await message.reply_text(text="✍️")
     user_id = temp_data.setdefault(m.from_user.id, {}).setdefault('user_id', UserId())
     messages = temp_data.setdefault(m.from_user.id, {}).setdefault('messages', [])


     USER_PROMPT = ""
     if reply and (reply.text or reply.caption):
          USER_PROMPT += f"Replied User ({reply.from_user.full_name if reply.from_user else m.from_user.full_name}): {reply.caption if reply.caption else reply.text}\n\n#"

     if reply and (reply.photo or (reply.sticker and not reply.sticker.is_video)):
          await msg.edit_text("🔎 *Analyzing image ...*", parse_mode=constants.ParseMode.MARKDOWN)
          photo = reply.photo[-1] if reply.photo else reply.sticker
          file = await bot.get_file(photo.file_id)
          path = await file.download_to_drive()
          result = await ai.image_to_text(open(path, 'rb'))
          error = result.get('error')
          os.remove(path)
          if error:
              await msg.edit_text('😓 *Failed to process image ...*', parse_mode=constants.ParseMode.MARKDOWN)
          else:
              USER_PROMPT += f"{result}\n\n#"                         
          
     USER_PROMPT += f"From user ({user.full_name}): {message.text}\n\n#"
     if not messages or len(messages) > MAX_CHAT:

         if messages:
             await msg.edit_text(
                f"*Clearing all previous conversation with {user.full_name} due to the max {MAX_CHAT} chat, we have reached through... (:*", 
                parse_mode=constants.ParseMode.MARKDOWN
             )
            
         temp_data[m.from_user.id]['messages'] = []
         temp_data[m.from_user.id]['messages'].extend(
            [
               {"role": "user", "content": USER_PROMPT}
            ]
         )
         messages = temp_data[m.from_user.id]['messages']
     else:
        
         temp_data[m.from_user.id]['messages'].append({"role": "user", "content": USER_PROMPT})
         messages = temp_data[m.from_user.id]['messages']
         

     if is_do_search(m.text):
          await msg.edit_text("*🔎 Searching for latest updates ...*", parse_mode=constants.ParseMode.MARKDOWN)
          result = await search_query(m.text)
          results = result.get('results')
          if results:
               USER_PROMPT += f"\n#Web Search Results By System: {results}"
          else:
               await msg.edit_text("*Couldn't find any results ...*", parse_mode=constants.ParseMode.MARKDOWN)

     response = await ai.groq(messages)
     bot_reply = response['reply'] if response.get('reply') else "I'm Gojo Satoru."
     temp_data[m.from_user.id]['messages'].append({"role": "assistant", "content": bot_reply})

     try:
         await msg.edit_text(
             text=bot_reply,
             parse_mode=constants.ParseMode.MARKDOWN,
             
         )
         users[user.id] = False
     except Exception as e:
          if "Message is too long" == e.message:
               msg_list = split_message(bot_reply)
               
               for idx, text in enumerate(msg_list, start=1):
                     escaped_txt = helpers.escape_markdown(text)
                     if idx == len(msg_list):
                         return await m.reply_text(text=text, parse_mode=constants.ParseMode.MARKDOWN)
                     else:
                         await m.reply_text(text=text, parse_mode=constants.ParseMode.MARKDOWN)
                       
               users[user.id] = False
               return await msg.delete()
                     
          else:
              if "can't find end of the entity" in e.message:
                   try:
                       await msg.edit_text(text=bot_reply)
                       users[user.id] = False
                   except Exception as e:
                        users[user.id] = False
                        return await msg.edit_text(
                            text=f"❌ ERROR:\n {e}"
                        )
              else:
                  users[user.id] = False
                  return await msg.edit_text(
                            text=f"❌ ERROR:\n {e.message}"
                  )
                     
    

@Command("gojocontinue")
async def chatBotContinue(update, context):
     m = update.effective_message
     reply = m.reply_to_message
     user = update.effective_user
     bot = context.bot
     msg = await m.reply_text("✍️")
     if user.id in temp_data and 'messages' in temp_data[user.id] and 'user_id' in temp_data[user.id] and len(temp_data[user.id]['messages']) > 0:
         messages = temp_data[user.id]['messages']
         user_id = temp_data[user.id]['user_id']
         response = await ai.groq(messages)
         try:
             bot_reply = response['reply'] if response.get('reply') else "I'm Gojo Satoru"
             await msg.edit_text(bot_reply, parse_mode=constants.ParseMode.MARKDOWN)
         except error.BadRequest as e:
              if "can't find end of the entity" in str(e):
                    offset = int(str(e).split("byte offset ")[1])
                    LOGGER.error(f"{message.chat.title} | {message.chat.id} ❌ Error parsing entity at offset {offset}: {bot_reply[offset-10:offset+10]}")
           
                    try:
                       await msg.edit_text(text=bot_reply)
                    except Exception as e:
                        if search_text('long', str(e)):
                            paste_src = await paste(bot_reply)
                            await msg.edit_text(paste_src['paste_url'], disable_web_page_preview=False)
                        else:
                           await msg.edit_text(
                             text="❌ ERROR:\n" + str(e), 
                             parse_mode=constants.ParseMode.MARKDOWN
                             )
                     
              elif search_text('long', str(e)):
                    paste_src = await paste(bot_reply)
                    await msg.edit_text(paste_src['paste_url'])
                    return
              else:
                   await msg.edit_text(
                     "❌ ERROR:\n" + str(e),
                     parse_mode=constants.ParseMode.MARKDOWN
                   )
                   return
     else:
         return await msg.edit_text(
            "⚡ *There's no conversation in user data currently.*", 
            parse_mode=constants.ParseMode.MARKDOWN
         )
          
          
@Command('gojoclear')
async def chatBotClear(update, context):
     m = update.effective_message
     reply = m.reply_to_message
     user = update.effective_user
     bot = context.bot
     msg = await m.reply_text("⚡")
     if user.id in temp_data:
          del temp_data[user.id]
          return await msg.edit_text(f"⚡ *Cleared all previous chatbot conversation with {user.full_name}*", parse_mode=constants.ParseMode.MARKDOWN)
     else:
         return await msg.edit_text("*You don't have any previous conversation with chatbot 🤷*", parse_mode=constants.ParseMode.MARKDOWN)
     

@Command("gojodata")
async def GetChatBotData(update,  context):
     m = update.effective_message
     user = update.effective_user 
     if user.id in temp_data:
          messages_data = temp_data[user.id]["messages"][1:]  #skipped system prompt     
          path = str(user.full_name) + "_chatbotData.txt"
          with open(path, "w+") as file:
               for msg in messages_data:
                   if msg["role"] == "assistant":
                        file.write(f"Gojo:\n{msg['content']}\n\n")
                   else:
                        file.write(f"You:\n{msg['content']}\n\n")
          return await m.reply_document(
             document=path,
             caption=f"🤖 *Here Your conversion data with gojo AI, plus you have currently {len(messages_data)} chats with Gojo*.", 
             parse_mode=constants.ParseMode.MARKDOWN
          )
     else:
        return await m.reply_text("You don't have any conversation with gojo yet.")
          


@Messages(filters=(~filters.COMMAND & filters.ChatType.GROUPS & (filters.TEXT | filters.CAPTION)), group=4)
async def _HeyGojo(update, context):
    m = update.effective_message
    user = update.effective_user
    text = m.text or m.caption
    pattern = r"(hello|hi|hey).*gojo|gojo.*(hello|hi|hey)"
    
    if re.search(pattern, text, re.IGNORECASE):
        if not m.chat.id in CHAT_IDS:
            response = f"Yo! <b>{user.mention_html()}</b>, wanna chat? Just hit <code>/chatbot on</code> to unleash the *<b>Gojo AI</b>* magic here! <a href='https://i.imgur.com/lV5SUU0.jpeg'>✨</a>"
            return await m.reply_text(response, parse_mode=constants.ParseMode.HTML)
      

@Command("chatbot")
@admin_check()
@only_premium
async def ChatBot(update, context):
  
    message = update.effective_message
    user = message.from_user
    name = message.chat.title if message.chat.title else message.chat.first_name
  
    MOD = [
      'on', 
      'off',
      'enable',
      'disable',
    ]
  
    if len(message.text.split()) == 1 or message.text.split()[1] not in MOD:

         all_chats = await get_all_chats()
         chatbot_str = "*Enabled* ✅" if message.chat.id in all_chats else "❌ *Disabled*" 
      
         return await message.reply_text(
             text=f"⚡ *Only you can turn on or off the chatbot!*\n\n*Currently chatbot*: {chatbot_str}",
             parse_mode=constants.ParseMode.MARKDOWN
         )

    user_mod = message.text.split()[1].lower()
    if user_mod in ('on', 'enable'):
         await add_chat(message.chat.id)
         if message.chat.id not in CHAT_IDS:
              CHAT_IDS.append(message.chat.id)
            
         await message.reply_text(
             f'⚡ *Chatbot Successfully enabled in {name}*!',
            parse_mode=constants.ParseMode.MARKDOWN
         )
    else:
         await remove_chat(message.chat.id)
         if message.chat.id in CHAT_IDS:
              CHAT_IDS.remove(message.chat.id)
            
         await message.reply_text(
             f'⚡ *Chatbot Successfully disabled in {name}*!',
            parse_mode=constants.ParseMode.MARKDOWN
         )
         








      
