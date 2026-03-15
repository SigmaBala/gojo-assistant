

import html

from telegram import constants, helpers
from nandha.helpers.decorator import Command
from nandha.helpers.utils import get_media_id, find_registration_time, get_as_document, extract_user



__module__ = 'Info'


__help__ = '''
*Commands*:
/user, /info
/chat, /id, /ginfo

```
- /user <user_id or username>: Get user information
- /chat <chat_id or chat name>: Get chat information
- /id <user_id>: Get all possible file, user, and chat IDs
```

*Usage*:
- You can reply to a message with these commands or provide an ID/username
- For /user and /id, you can also mention a user

*Examples*:
`/user @username`
`/chat -1001234567890`
Reply to a message with `/id`
'''


@Command(['chat', 'ginfo'])
async def ChatInfo(update, context):

      chat = update.effective_chat
      m = update.effective_message
      chat_id = chat.id
      bot = context.bot


      if chat.type == constants.ChatType.PRIVATE and len(m.text.split()) < 2:
           return await m.reply_text("🌚 *To check user info kindly use /user command instead and this command need a chatId argument.*\n*Example:* `/chat chat_id`", parse_mode=constants.ParseMode.MARKDOWN)

      msg = await m.reply_text("*⚡ Getting chat info...*", parse_mode=constants.ParseMode.MARKDOWN)
      
      if len(m.text.split()) > 1: 
          chat_id = m.text.split()[1]
          is_chat = True if (str(chat_id).startswith("@") or str(chat_id).startswith("-100")) else False
          if not is_chat: 
               return await msg.edit_text("🙋 Give only valid chat username or chat_id")
      try:
          chat = await bot.get_chat(chat_id)
      except Exception as e:
          return await msg.edit_text(f"❌ ERROR: `{e}`", parse_mode=constants.ParseMode.MARKDOWN)

      string = (
        f"*👁️‍🗨️ Chat id*: `{chat.id}`\n"
        f"*✨ Chat title*: `{html.escape(chat.title)}`\n"
        f"*🔍 Chat username*: `{chat.username if chat.username else 'Not available.'}`\n"
        f"*⚡ Chat description*: \n\n`{html.escape(chat.description if chat.description else 'Not available.')}`\n"
      )

      if chat.photo:
            photo = await (await bot.get_file(chat.photo.big_file_id)).download_to_drive()
            await m.reply_photo(
                photo=photo,
                caption=string,
                parse_mode=constants.ParseMode.MARKDOWN
            )
            await msg.delete()
      else:
            await msg.edit_text(
               text=string,
               parse_mode=constants.ParseMode.MARKDOWN
      )
            
            
      

@Command(['user', 'info'])
async def UserInfo(update, context):
     message = update.effective_message
     bot = context.bot
     user_id = await extract_user(message)
  
     if not user_id:
          return await message.reply_text(
               "Can't access by username, reply to the user or give their telegram id"
          )
          
     if message.reply_to_message and message.reply_to_message.forward_origin and getattr(message.reply_to_message.forward_origin, 'sender_user', None): # to get forward user info
           user_id = message.reply_to_message.forward_origin.sender_user.id
          
     check = lambda x: x if x else 'Null'

     msg = await message.reply_text("*Getting user info...*", parse_mode=constants.ParseMode.MARKDOWN)

     try:
        user = await bot.get_chat(user_id)
     except Exception as e:
          return await msg.edit_text(
               text=f"❌ ERROR: `{e}`",
               parse_mode=constants.ParseMode.MARKDOWN
          )
     
     text = "<b>🌐 User info</b>:"
     text += f"\n\n👤 <b>First Name</b>: {html.escape(user.first_name)}"
     text += f"\n🌌 <b>Last Name</b>: {check(user.last_name)}"
     text += f"\n🆔 <b>ID</b>: <code>{user.id}</code>"
     text += f"\n⚡ <b>Username</b>: {check(user.username)}"
     text += f"\n❤️ <b>Mention</b>: {helpers.mention_html(user.id, user.first_name)}"
     text += f"\n\n🌠 <b>Bio</b>: <code>{html.escape(check(user.bio))}</code>\n"
     
     if user.personal_chat:
          text += f"\n💬 <b>Channel</b>: <code>{user.personal_chat.title}</code>"

     _, date = find_registration_time(user.id)
     text += f"\n🔎 <b>Account</b>: <code>~ {date}</code>"
          
     if user.photo:
          file = await bot.get_file(user.photo.big_file_id)
          path = await file.download_to_drive()
          await message.reply_photo(
               photo=path, 
               caption=text, 
               parse_mode=constants.ParseMode.HTML
          )
          await msg.delete()
     else:
          await msg.edit_text(
               text=text, 
               parse_mode=constants.ParseMode.HTML
          )
     


@Command('id')
async def _getTelegramID(update, context):
     bot = context.bot
     message = update.effective_message
     reply = message.reply_to_message

     if len(message.text.split()) > 1:
             try:
                user_id = await extract_user(message)
                if not user_id:
                    return await message.reply_text("Couldn't find the user...")
                  
                user = await bot.get_chat(user_id)
                text = f"*User {user.first_name}'s ID*: `{user.id}`"
                return await message.reply_text(
                      text, parse_mode=constants.ParseMode.MARKDOWN
                )
             except Exception as e:
                    return await message.reply_text(
                          text=f"❌ Error: {str(e)}"
                    )
             
          
     text = (
f"""
*🚹 Your Tg ID*: `{message.sender_chat.id if message.sender_chat else message.from_user.id}`
*🗨️ Chat ID*: `{message.chat.id}`
*📝 Msg ID*: `{message.message_id}`
"""
)  
     if reply:
          text += f"*🚹 Replied Tg ID*: `{reply.sender_chat.id if reply.sender_chat else reply.from_user.id}`"
          text += f"\n*📝 Replied Msg ID*: `{reply.message_id}`"
          if reply.forward_origin:
               
               if getattr(reply.forward_origin, 'sender_user', None):
                     text += f"\n*🧑‍🦱 Forward Tg ID*: `{reply.forward_origin.sender_user.id}`"
               elif getattr(reply.forward_origin, 'chat', None):
                     text += f"\n*📢 Forward Chat ID*: `{reply.forward_origin.chat.id}`"
              
          media_type, media_id = get_media_id(reply)
          if media_type and media_id:
               text += f"\n*📁 Replied {media_type.capitalize()} ID*: `{media_id}`"
     return await message.reply_text(
         text=text, parse_mode=constants.ParseMode.MARKDOWN
     )
          
       
     
     
