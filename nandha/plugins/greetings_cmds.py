
from nandha.db.greetings import (
get_welcome, set_welcome, clear_welcome, set_goodbye_time,
get_goodbye, set_goodbye, clear_goodbye, set_welcome_time
)
from nandha.helpers.decorator import Command, admin_check, Callbacks, only_groups
from nandha.helpers.utils import get_method_by_type, convert_greetings_text
from nandha.helpers.misc import dict_to_keyboard
from telegram import constants, InlineKeyboardButton, InlineKeyboardMarkup, helpers



__module__ = "greetings"

__help__ = """
*Commands*:
/setwelcome, /clearwelcome, /getwelcome
/setwelcometime, /cleargoodbye, /setgoodbyetime,
/setgoodbye, /getgoodbye

```
/setwelcome: reply to the message for set it as group welcome.
/clearwelcome: clear welcome message from group.
/getwelcome: for show the current chat welcome.
/setwelcometime <integer value as seconds>: set welcome auto delete time.

/setgoodbye: reply to the message for set it as group goodbye.
/cleargoodbye: clear goodbye message from group.
/getgoodbye: for show the current chat goodbye.
/setgoodbyetime <integer value as seconds>: set goodbye auto delete time.
```

```Note:
We support only markdown,
and use the following to mention info:

{name} {user_id} {chat_id} 
{chat} {mention} {first_name}
```
"""





def get_media(bot, message):
    media_types = {
        'photo': (message.photo, bot.send_photo),
        'animation': (message.animation, bot.send_animation),
        'document': (message.document, bot.send_document),
        'sticker': (message.sticker, bot.send_sticker),
        'audio': (message.audio, bot.send_audio)
    }
    
    for media_type, media in media_types.items():
        if media[0]:
            if media_type == 'photo':
                return media_type, media[0][-1].file_id, media[1]
            else:
                return media_type, media[0].file_id, media[1]
    
    return None, None, None
  


welcome_temp = {}
goodbye_temp = {}





####################################################################################################

@Command('setgoodbyetime')
@admin_check('can_change_info')
@only_groups
async def SetGoodByeTime(update, context):
     m = update.effective_message
     chat = m.chat
     time = m.text.split()[1] if len(m.text.split()) > 1 and m.text.split()[1].isdigit() else None
     if not time:
         return await m.reply_text('Provide me valid time!')
       
     if (await set_goodbye_time(chat.id, time)):
          return await chat.send_message("✅ * custom goodbye auto delete updated.*", parse_mode=constants.ParseMode.MARKDOWN)
     else:
          return await chat.send_message('ℹ️ *First set goodbye msg then update your auto delete time!*', parse_mode=constants.ParseMode.MARKDOWN)


@Command('setwelcometime')
@admin_check('can_change_info')
@only_groups
async def SetWelcomeTime(update, context):
     m = update.effective_message
     chat = m.chat
     time = m.text.split()[1] if len(m.text.split()) > 1 and m.text.split()[1].isdigit() else None
     if not time:
         return await m.reply_text('Provide me valid time!')
       
     if (await set_welcome_time(chat.id, time)):
          return await chat.send_message("✅ * custom welcome auto delete updated.*", parse_mode=constants.ParseMode.MARKDOWN)
     else:
          return await chat.send_message('ℹ️ *First set welcome msg then update your auto delete time!*', parse_mode=constants.ParseMode.MARKDOWN)
     


####################################################################################################


@Callbacks(r"(^gb_chk|^gb_verify)")
@admin_check('can_change_info')
@only_groups
async def GoodbyeSettings(update, context):
       query = update.callback_query
       user = query.from_user
       m = update.effective_message
       cmd, chat_id = query.data.split('#')
       chat_id = int(chat_id)
       chat = m.chat

       if cmd == "gb_verify":
            data = goodbye_temp.get(chat_id)
            await set_goodbye(
                 chat_id,
                 text=data.get('text'), 
                 file_id=data.get('file_id'),
                 file_type=data.get('file_type'),
                 keyboard=data.get('keyboard')
            )
            return await m.edit_text(f"✅ *Successfully new goodbye message set for chat {m.chat.title}!*", parse_mode=constants.ParseMode.MARKDOWN)
            
       elif cmd == "gb_chk":
            data = goodbye_temp.get(chat_id)
            if not data:
                return await query.answer("This query was expired.", show_alert=True)
            else:
                 text = convert_greetings_text(data['text'], user, m.chat) if data.get('text') else None
                 method = data.get('method')
                 file_id = data.get('file_id')
                 file_type = data.get('file_type')
                 keyboard = dict_to_keyboard(data['keyboard']) if data.get('keyboard') else None
                 if file_type == "text":
                     await method(chat_id, text=text, reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN)
                 else:
                     await method(chat_id, file_id, caption=text, reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN)



@Callbacks(r"(^wel_chk|^wel_verify)")
@admin_check('can_change_info')
@only_groups
async def WelcomeSettings(update, context):
       query = update.callback_query
       user = query.from_user
       m = update.effective_message
       cmd, chat_id = query.data.split('#')
       chat_id = int(chat_id)
       chat = m.chat

       if cmd == "wel_verify":
            data = welcome_temp.get(chat_id)
            await set_welcome(
                 chat_id,
                 text=data.get('text'), 
                 file_id=data.get('file_id'),
                 file_type=data.get('file_type'),
                 keyboard=data.get('keyboard')
            )
            return await m.edit_text(f"✅ *Successfully new welcome message set for chat {m.chat.title}!*", parse_mode=constants.ParseMode.MARKDOWN)
            
       elif cmd == "wel_chk":
            data = welcome_temp.get(chat_id)
            if not data:
                return await query.answer("This query was expired.", show_alert=True)
            else:
                 text = convert_greetings_text(data['text'], user, m.chat) if data.get('text') else None
                 method = data.get('method')
                 file_id = data.get('file_id')
                 file_type = data.get('file_type')
                 keyboard = dict_to_keyboard(data['keyboard']) if data.get('keyboard') else None
                 if file_type == "text":
                     await method(chat_id, text=text, reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN)
                 else:
                     await method(chat_id, file_id, caption=text, reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN)

####################################################################################################


@Command('cleargoodbye')
@admin_check('can_change_info')
@only_groups
async def ClearGoodbye(update, context):
     m = update.effective_message
     chat = m.chat
     if await clear_goodbye(chat.id):
         return await chat.send_message("✅ *Cleared custom goodbye message.*", parse_mode=constants.ParseMode.MARKDOWN)
     else:
         return await chat.send_message("🤷 *No custom goodbye message setted yet.*", parse_mode=constants.ParseMode.MARKDOWN)


@Command('clearwelcome')
@admin_check('can_change_info')
@only_groups
async def ClearWelcome(update, context):
     m = update.effective_message
     chat = m.chat
     if await clear_welcome(chat.id):
         return await chat.send_message("✅ *Cleared custom welcome message.*", parse_mode=constants.ParseMode.MARKDOWN)
     else:
         return await chat.send_message("🤷 *No custom welcome message setted yet.*", parse_mode=constants.ParseMode.MARKDOWN)


####################################################################################################



@Command('getgoodbye')
@admin_check('can_change_info')
@only_groups
async def GetGoodbye(update, context):
     m = update.effective_message
     chat_id = m.chat.id
     user = m.from_user
     chat = m.chat
       
     data = await get_goodbye(chat_id)
     if not data:
          return await m.reply_text("🤷 *No custom goodbye set yet.*", parse_mode=constants.ParseMode.MARKDOWN)
     else:
         text = convert_greetings_text(data['text'], user, m.chat) if data.get('text') else None
         file_type = data.get('file_type')
         file_id = data.get('file_id')
         keyboard = dict_to_keyboard(data['keyboard']) if data.get('keyboard') else None
         method = get_method_by_type(context.bot, file_type)
         if file_type == "text":
             await method(chat_id, text=text, reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN)
         else:
             await method(chat_id, file_id, caption=text, reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN)



@Command('getwelcome')
@admin_check('can_change_info')
@only_groups
async def GetWelcome(update, context):
     m = update.effective_message
     chat_id = m.chat.id
     user = m.from_user
     chat = m.chat
       
     data = await get_welcome(chat_id)
     if not data:
          return await m.reply_text("🤷 *No custom welcome set yet.*", parse_mode=constants.ParseMode.MARKDOWN)
     else:
         text = convert_greetings_text(data['text'], user, m.chat) if data.get('text') else None
         file_type = data.get('file_type')
         file_id = data.get('file_id')
         keyboard = dict_to_keyboard(data['keyboard']) if data.get('keyboard') else None
         method = get_method_by_type(context.bot, file_type)
         if file_type == "text":
             await method(chat_id, text=text, reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN)
         else:
             await method(chat_id, file_id, caption=text, reply_markup=keyboard, parse_mode=constants.ParseMode.MARKDOWN)


####################################################################################################

@Command('setgoodbye')
@admin_check('can_change_info')
@only_groups
async def SetGoodbye(update, context):
     m = update.effective_message
     r = m.reply_to_message
     chat = m.chat
     bot = context.bot
       
     if not r:
         return await m.reply_text("Reply to the message!")
     text = (r.caption or r.text) if (r.caption or r.text) else None
     file_type, file_id, method = get_media(context.bot, r)
     if not file_type or not file_id:
         file_type = "text"
         method = bot.send_message
     keyboard = r.reply_markup.to_dict() if r.reply_markup else None
     buttons = InlineKeyboardMarkup([[
           InlineKeyboardButton('👀 Check', callback_data=f'gb_chk#{m.chat.id}'),
           InlineKeyboardButton('✅ Verify', callback_data=f'gb_verify#{m.chat.id}'),
]])
     goodbye_temp[m.chat.id] = {
          'text': text,
          'keyboard': keyboard,
          'file_type': file_type,
          'file_id': file_id,
          'method': method
     }
     
     await chat.send_message(
          text = "```\n⚠️ Verify your goodbye message! In some cases it may have bugs so.```",
          parse_mode = constants.ParseMode.MARKDOWN,
          reply_markup = buttons
     )
     

@Command('setwelcome')
@admin_check('can_change_info')
@only_groups
async def SetWelcome(update, context):
     m = update.effective_message
     r = m.reply_to_message
     chat = m.chat
     bot = context.bot
       
     if not r:
         return await m.reply_text("Reply to the message!")
     text = (r.caption or r.text) if (r.caption or r.text) else None
     file_type, file_id, method = get_media(context.bot, r)
     if not file_type or not file_id:
         file_type = "text"
         method = bot.send_message
     keyboard = r.reply_markup.to_dict() if r.reply_markup else None
     buttons = InlineKeyboardMarkup([[
           InlineKeyboardButton('👀 Check', callback_data=f'wel_chk#{m.chat.id}'),
           InlineKeyboardButton('✅ Verify', callback_data=f'wel_verify#{m.chat.id}'),
]])
     welcome_temp[m.chat.id] = {
          'text': text,
          'keyboard': keyboard,
          'file_type': file_type,
          'file_id': file_id,
          'method': method
     }
     
     await chat.send_message(
          text = "```\n⚠️ Verify your welcome message! In some cases it may have bugs so.```",
          parse_mode = constants.ParseMode.MARKDOWN,
          reply_markup = buttons
     )
     

####################################################################################################
