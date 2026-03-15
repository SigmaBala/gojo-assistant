
import config

from nandha import pbot as bot
from nandha.helpers.utils import Password
from pyrogram import filters, types


__module__ = "PassWords"

__help__ = """
*Commands*:
/password, /passwords

```
- /password: just send to chat and select
which type password you looking for.
```
*Example*:
`/password`
"""


@bot.on_callback_query(filters.regex('^pw_'))
async def GenPasswordCq(_, query):
  
      cmd, user_id = query.data.split('#')
      user = query.from_user
      user_id = int(user_id)
      if user.id != user_id:
           return await query.answer('This is not your request.', show_alert=True)

      async def edit_text(message, password):
            
            text = '\n'.join(f'`{word}`' for word in password)     
            text += (
         "\n\n```\nbelow buttons will generate passwords for you. 😉```"
         f"\n**By {config.BOT_USERNAME}**"
            )
            buttons = [
                 types.InlineKeyboardButton('Digit', callback_data=f"pw_random_digits#{user.id}"),
                 types.InlineKeyboardButton('Strings', callback_data=f"pw_random_strings#{user.id}"),
                 types.InlineKeyboardButton('Random', callback_data=f"pw_random#{user.id}"),
],[   
                 types.InlineKeyboardButton('Normal Noun', callback_data=f"pw_normal_nouns#{user.id}"),
                 types.InlineKeyboardButton('Normal Adjective', callback_data=f"pw_normal_adjectives#{user.id}"),
],[

                 types.InlineKeyboardButton('Easy Noun', callback_data=f"pw_easy_nouns#{user.id}"),
                 types.InlineKeyboardButton('Easy Adjective', callback_data=f"pw_easy_adjectives#{user.id}"),
         
],[
                 types.InlineKeyboardButton('❌ Close', callback_data=f"pyrodel#{user.id}"),  
            ]
            await message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(buttons))
      
      if cmd == "pw_random":
            password = Password.random_password()
            await edit_text(query.message, password)
      elif cmd == "pw_random_digits":
            password = Password.random_password(only_string=False)
            await edit_text(query.message, password)
      elif cmd == "pw_random_strings":
            password = Password.random_password(only_digit=False)
            await edit_text(query.message, password)
      elif cmd == "pw_normal_nouns":
            password = Password.normal_password(only_adjective=False)
            await edit_text(query.message, password)
      elif cmd == "pw_normal_adjectives":
            password = Password.normal_password(only_noun=False)
            await edit_text(query.message, password)
      elif cmd == "pw_easy_nouns":
            password = Password.easy_password(only_adjective=False)
            await edit_text(query.message, password)
      elif cmd == "pw_easy_adjectives":
            password = Password.easy_password(only_noun=False)
            await edit_text(query.message, password)
      
  

@bot.on_message(filters.command(['password', 'passwords']) & ~filters.forwarded)
async def GenPasswordCmd(_, message):
       m = message
       user = m.from_user
       text = (
         "```\nbelow buttons will generate passwords for you. 😉```"
         f"\n**By {config.BOT_USERNAME}**"
       )
  
       buttons = [
           types.InlineKeyboardButton('Digit', callback_data=f"pw_random_digits#{user.id}"),
           types.InlineKeyboardButton('Strings', callback_data=f"pw_random_strings#{user.id}"),
           types.InlineKeyboardButton('Random', callback_data=f"pw_random#{user.id}"),
],[
           types.InlineKeyboardButton('Normal Noun', callback_data=f"pw_normal_nouns#{user.id}"),
           types.InlineKeyboardButton('Normal Adjective', callback_data=f"pw_normal_adjectives#{user.id}"),
],[

           types.InlineKeyboardButton('Easy Noun', callback_data=f"pw_easy_nouns#{user.id}"),
           types.InlineKeyboardButton('Easy Adjective', callback_data=f"pw_easy_adjectives#{user.id}"),
         
],[
           types.InlineKeyboardButton('❌ Close', callback_data=f"pyrodel#{user.id}"),  
]

       await m.reply_text(
           text,
           reply_markup=types.InlineKeyboardMarkup(buttons)
       )



