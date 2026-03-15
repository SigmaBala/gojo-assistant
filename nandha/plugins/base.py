
import base64
import asyncio
import config
import random


from pyrogram import enums


from telegram import Update, constants, helpers, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from nandha import font, app, MODULE, pbot, SUPPORT_CHAT, LOGS_CHANNEL, UPDATE_CHANNEL, BOT_USERNAME
from nandha.db.users import add_user, get_all_users, check_user_exists
from nandha.db.chats import get_all_chats, add_chat, check_chat_exists
from nandha.db.autofilter import get_file_by_index
from nandha.helpers.decorator import Command
from nandha.helpers.misc import help_button, help_keyboard_data, get_help_button
from nandha.helpers.utils import autofilter_send_file, decode_to_base64, auto_delete, time_formatter
from nandha.helpers.pyro_utils import check_membership



async def deepLink(message, context):
    text = "".join(context.args)
    bot = context.bot
    user = message.from_user
    mention = helpers.mention_markdown(user.id, user.first_name)

    if text.startswith('afFile'):
        decoded_data = decode_to_base64(text.split('-')[1].encode())
        user_id, index = decoded_data.split("&")
        mem_chk = await check_membership(config.AF_SUB_CHAT, user.id)

        if mem_chk:
             file = await get_file_by_index(int(index))
             return await autofilter_send_file(bot, text, user.id, file)
        else:
              buttons = InlineKeyboardMarkup([[
                  InlineKeyboardButton('📢  My ( Channel / Group )', url=f"https://t.me/{config.AF_SUB_CHAT[1:]}")
              ],[
                  InlineKeyboardButton('📁 Get File', url=f"t.me/{config.BOT_USERNAME[1:]}?start={text}")
                
              ]])
          
              return await bot.send_photo(
                user.id,
                photo=config.FORCE_JOIN_IMG,
                caption=config.AF_SUB_TEXT, 
                parse_mode=constants.ParseMode.HTML,
                reply_markup=buttons
              )
          

    elif text.startswith("getmedia"):
        decoded_data = base64.b64decode(text.split('-')[1].encode()).decode()
        type, media = decoded_data.split("&")
        async def send_media(media: str, method):
             try:
                 await method(user.id, media)
             except Exception as e:
                 await bot.send_message(user.id, f"❌ ERROR: {str(e)}")
        if "photo" == type:
             await send_media(media, bot.send_photo)
        elif "video" == type:
             await send_media(media, bot.send_video)
        elif "animation" == type:
             await send_media(media, bot.send_animation)
        elif "audio" == type:
             await send_media(media, bot.send_audio)
        else:
             await bot.send_message(user.id, "❌ Unsupported media type.")
             return True
          
    elif text.startswith("getfile"):
        decoded_data = base64.b64decode(text.split('-')[1].encode()).decode()
        msg_id, unique_id = decoded_data.split("&")
        file_msg = await pbot.get_messages(config.FILE_DB_CHANNEL, int(msg_id))
        if getattr(file_msg, "empty", None):
             await bot.send_message(
                   chat_id=user.id,
                   text="*This file is removed or a invalid link!* 👻",
                   parse_mode=constants.ParseMode.MARKDOWN
              )
             return True
          
        s_media = ["document", "video", "sticker", "photo", "animation", "audio"]
        for kind in s_media:
             media = getattr(file_msg, kind, None)
             if media is not None:
                  file_unique_id = getattr(media, "file_unique_id")
                  break
        if unique_id != file_unique_id:
              await bot.send_message(
                   chat_id=user.id,
                   text="*This is not a valid link!* 🤨",
                   parse_mode=constants.ParseMode.MARKDOWN
              )
              return True
        else:

             button = InlineKeyboardMarkup([[
                    InlineKeyboardButton("⚡ Channel", url=f"t.me/{config.UPDATE_CHANNEL[1:]}"),
                  ],[
                    InlineKeyboardButton("⚡ Try again", url=f"t.me/{bot.username}?start={text}")
                  ]]
             )
             try:
                 member = await pbot.get_chat_member(config.UPDATE_CHANNEL, user.id)
                 if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                      await bot.send_message(
                         chat_id=user.id, 
                         text="*You need to join my channel back for get the file!*",
                         parse_mode=constants.ParseMode.MARKDOWN,
                         reply_markup=button
                        )
                      return True
                 
             except Exception as error:
                  await bot.send_message(
                   chat_id=user.id,
                   text="*In order to access file please Join my channel!*",
                   parse_mode=constants.ParseMode.MARKDOWN,
                   reply_markup=button
              )
                  return True
             file_message = await file_msg.forward(user.id)
             time = config.AF_FILE_DEL_TIME
             await file_message.reply_text(f"✨ **Thank you for using me!**\n```\nThe file will be deleted after {time_formatter(time)}, so please save it somewhere else maybe Saved Messages!```")
             await auto_delete(file_message, time)
             return True
        
    elif text.startswith('help'):
        photo_url = config.HELP_CMD_IMG
        buttons = await get_help_button(message, user)
        if not buttons: return # it will handle itself.
      
        await bot.send_photo(
             chat_id=user.id,
             photo=photo_url,
             caption=f"""
*Hey* {mention}!

*Need help or want to support us?*

• `/donate`: keep our bot alive and kicking!
• `/support`: touch with our official support team.
• `/privacy`: earn how we protect your privacy.

*Ready to explore? Click the button below to discover my commands!*

""",
         parse_mode=constants.ParseMode.MARKDOWN,
         reply_markup=InlineKeyboardMarkup(buttons)
    )
        return True
    
    else:
        await bot.send_message(
           chat_id=user.id,
           text="*No, Deep message detected for this link 🤷*",
           parse_mode=constants.ParseMode.MARKDOWN
        )
        return False


@Command('start')
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    mention = helpers.mention_markdown(user.id, user.first_name)

    await chat.send_sticker(random.choice(config.AF_START_STICKERS)) # random shit for fun.
                            
    if chat.type == constants.ChatType.PRIVATE:
      
              db_user = await check_user_exists(user.id)
              if not db_user:
                  text = (
f"""              
⚡ *New User*:

*🆔 ID*: `{user.id}`
*🙋 User*: {mention}
"""
)
                  await bot.send_message(
                    chat_id=LOGS_CHANNEL,
                    text=text,
                    parse_mode=constants.ParseMode.MARKDOWN
                 )

              obj = user.to_dict()
              await add_user(obj)  

    else:
         db_chat = await check_chat_exists(chat.id)
         if not db_chat:
               text=(
f"""              
⚡ *New Chat*:

*🆔 ID*: `{chat.id}`
*🙋 Chat*: *{chat.title}*
""")
               await add_chat(chat.id) # adding the chat data to database
               await bot.send_message(
                  chat_id=LOGS_CHANNEL,
                  text=text,
                  parse_mode=constants.ParseMode.MARKDOWN
               )

    
               
    if context.args and message.chat.type == constants.ChatType.PRIVATE:
        if await deepLink(message, context): return # for deep link response commands
          
    if message.chat.type != constants.ChatType.PRIVATE:
          return await message.reply_photo(
             config.START_IMG,
             caption="Greetings! Satoru Gojo here. Ready to explore and engage? Type /help for options. Let’s begin!"
          )
        
    else:
         buttons = [[
             InlineKeyboardButton(
                 text='Help commands!', 
                 callback_data=f'help_{user.id}'
             )
         ],[
             InlineKeyboardButton(
                 text='Add me to your chat!',
                 url=f'https://t.me/{bot.username}?startgroup=true&admin=manage_chat+change_info+post_messages+edit_messages+delete_messages+invite_users+restrict_members+pin_messages+promote_members+manage_video_chats+anonymous=false'
             )
         ]]

         photo_url = config.PM_START_IMG
        
         text = (
f"""
Hey there! My name is Gojo - I'm here to help you manage your groups! Use /help to find out more about how to use me to my full potential.

Join my {UPDATE_CHANNEL} to get information on all the latest updates.

Use the /privacy command to view the privacy policy, and interact with your data.
"""

         )             
         return await message.reply_photo(
              photo=photo_url,
              caption=text,
              reply_markup=InlineKeyboardMarkup(buttons)
         )


@Command('help')
async def help_commands(update, context):
    photo_url = config.HELP_CMD_IMG
    bot = context.bot
    message = update.effective_message
    reply = message.reply_to_message
    user = message.from_user
    mention = helpers.mention_markdown(user.id, user.first_name)
    if len(message.text.split()) == 2:
         help = message.text.split(maxsplit=1)[1].strip().lower()
         if help in MODULE:
              help_msg = MODULE[help]
              photo = config.HELP_MODULE_IMG
              return await bot.send_photo(
                    chat_id = message.chat.id,
                    photo = photo,
                    caption = help_msg,
                    parse_mode = constants.ParseMode.MARKDOWN,
                    reply_to_message_id= reply.id if reply else message.id                    
              )
    
    if message.chat.type != constants.ChatType.PRIVATE:
          return await message.reply_text(
            "🧏 *Check my all commands in private chat!*",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                  "🆘 Commands", url=f"t.me/{bot.username}?start=help"
                )
            ]]), parse_mode=constants.ParseMode.MARKDOWN
        )
    
    buttons = await get_help_button(message, user)
    if not buttons: return # it will handle itself.
      
    await message.reply_photo(
         photo=photo_url,
         caption=f"""
*Hey* {mention}!

*Need help or want to support us?*

• `/donate`: keep our bot alive and kicking!
• `/support`: touch with our official support team.
• `/privacy`: earn how we protect your privacy.

*Ready to explore? Click the button below to discover my commands!*

""",
         parse_mode=constants.ParseMode.MARKDOWN,
         reply_markup=InlineKeyboardMarkup(buttons)
    )


privacy_text = (
f"""
*🗨️ Privacy Policy*:

We care about your privacy. 

*Here's what you need to know*:

*📥 Data Collection*:

We only collect your unique Telegram User ID, 
necessary for our bot to function properly.

*🔎 Data Use*:

We don't share your User ID with third-party apps or services.
Your data is stored securely to improve our bot's performance and provide better responses.

*🙋 Your Rights*:

You have the right to request access, correction,
or deletion of your data. Reach out to us if you have any concerns.

*🤷 Changes to this Policy*

We may update this policy. If we make significant changes, we'll notify you through this chat.

*By using our bot, you acknowledge that you've read, understood, and 
agree to our privacy policy. If you have any questions, feel free to ask! {SUPPORT_CHAT}*
"""
)


DONATION_TEXT = (
f"""
🙏 *Thank you for considering donating to help keep this Bot alive and functioning! Your support ensures continuous improvements and enhancements 🥰*.

*🔴 Recommended (international payment via UPI)*:
——————————————————
- IPPB: `nandhaxd-1@okicici`
- BOB: `nandhaxd@okicici`


*🔵 Crypto currency*:
——————————————————
- *Tether USD Address*: `UQCZRZCDy3d5Kyw26kOJv2PIaFp5iTk1_NOqEE4ett-Z22IT`
- *Ton Address*: `UQCZRZCDy3d5Kyw26kOJv2PIaFp5iTk1_NOqEE4ett-Z22IT`

*⚫ You can also donate telegram stars using /pay command.*


*🙋 I'm very grateful for every contribution. If you've made a donation, please reach me out {SUPPORT_CHAT} for let me know. ( : Thank you! 🕺*
"""
)    


support_text = f"""
👮 Click below buttons to reach out to the official Support for *{BOT_USERNAME}*. 
"""

@Command('support')
async def Support(update, context):
    if update.message.chat.type != constants.ChatType.PRIVATE:
          return await update.message.reply_text(
        text="*This commands only work in PM ⚡*",
        parse_mode=constants.ParseMode.MARKDOWN
          )
      
    def convert_to_link(text: str):
         ''' For convert a username to tg link '''
         return 'https://t.me/' + text[1:]
      
    button = InlineKeyboardMarkup(
      [[
       InlineKeyboardButton('⚡ Support Chat', url=convert_to_link(SUPPORT_CHAT)),
      ],[
       InlineKeyboardButton('⚡ Support Channel', url=convert_to_link(UPDATE_CHANNEL))
      ]]
    )
    return await update.message.reply_text(
          text=support_text, 
          reply_markup=button,
          parse_mode=constants.ParseMode.MARKDOWN
    )
  

  
@Command('donate')
async def Donation(update, context):
    if update.message.chat.type != constants.ChatType.PRIVATE:
          return await update.message.reply_text(
        text="*👮 I'd appreciate that please use this command in my PRIVATE.*",
        parse_mode=constants.ParseMode.MARKDOWN
          )
    return await update.message.reply_text(
          text=DONATION_TEXT, 
          parse_mode=constants.ParseMode.MARKDOWN
    )
  
@Command('privacy')
async def Privacy(update, context):
    if update.message.chat.type != constants.ChatType.PRIVATE:
          return await update.message.reply_text(
        text="*👮 I'd appreciate that please use this command in my PRIVATE.*",
        parse_mode=constants.ParseMode.MARKDOWN
          )
    return await update.message.reply_text(
          text=privacy_text, 
          parse_mode=constants.ParseMode.MARKDOWN
    )
