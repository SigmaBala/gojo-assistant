

import io
import os
import sys
import traceback
import time
import subprocess
import asyncio
import datetime as dt
import uuid
import config
import html

from contextlib import redirect_stdout

from nandha import app, pbot, DEV_LIST, BOT_USERNAME, BOT_ID, LOGS_CHANNEL, database
from telegram import Update, constants
from telegram.constants import ParseMode
from telegram.ext import filters, ContextTypes, ApplicationHandlerStop
from telegram.ext import CallbackContext 
from nandha.helpers.decorator import Command, Messages, devs_only
from nandha.helpers.scripts import paste
from nandha.helpers.utils import get_as_document, extract_user
from nandha.db.users import get_all_users, get_user_id_by_username, add_user, update_users_status_to_inactive, update_users_status_to_active, get_all_active_users
from nandha.db.chats import get_all_chats
from nandha import db, LOGGER
from nandha.db import ignore

from pyrogram import StopPropagation

__module__ = 'Devs tool'


__help__ = '''
*Commands*:
/logs, /eval, /peval, 
/sh, /echo, /stats,
/send, /left, /bcast,
/block, /unblock, /blocklist
/mongodb, /restart

```
- /logs: Get current bot logs.
- /eval <code>: Execute code in the bot.
- /peval <code>: Execute pyrogram code in the bot.
- /sh <code>: Execute a shell command in the bot.
- /echo <text>: Echo the given text or reply to a message.
- /stats: Check bot statistics.
- /send <chat_id>: Send a message to a specific chat or user (reply to a message).
- /left <chat_id>: Leave a specific chat.
- /bcast: Broadcast a message to all users.
- /block: Block a user from interacting with the bot.
- /unblock: Unblock a user, allowing them to interact with the bot again.
- /blocklist: View the list of blocked users.
- /mongodb: shows mongodb stats.
- /restart: restart bot
```

```Note:
Required privileges.
```
'''




@Command('mongodb')
@devs_only
async def MongoDBInfo(update, context):
      m = update.effective_message
      result = await database.command({"dbStats": 1})
      LDS = round(result['dataSize']/(1024*1024), 2)
      SS = round(result['storageSize']/(1024*1024), 2)
      IS = round(result['indexSize']/(1024*1024), 2)
      TCC = result['collections']
      text = (
         "📊 <b>MONGO-DATABASE Status</b>:\n\n"
         f"<b>✰ Logical Data Size</b>: <code>{LDS} MB</code>\n"
         f"<b>✰ Storage Size</b>: <code>{SS} MB</code>\n"
         f"<b>✰ Index Size</b>: <code>{IS} MB</code>\n"
         f"<b>✫ Total Collection Count</b>: <code>{TCC}</code>\n"
      )
      return await m.reply_text(text, parse_mode=constants.ParseMode.HTML)
      

@Command('restart')
@devs_only
async def restart(update, context):
    bot = context.bot
    message = update.effective_message
    msg = await bot.send_message(text="*𝖡𝗈𝗍 𝖨𝗌 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀... 🔄*", chat_id=message.chat.id, parse_mode=constants.ParseMode.MARKDOWN)       
    await asyncio.sleep(5)
    await msg.edit_text("*𝖡𝗈𝗍 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 ! 𝖱𝖾𝖺𝖽𝗒 𝖳𝗈 𝖬𝗈𝗏𝖾 𝖮𝗇 🐈*", parse_mode=constants.ParseMode.MARKDOWN)
    os.execl(sys.executable, sys.executable, *sys.argv)



@Command(("ignorelist", "blocklist"))
@devs_only
async def _ignoreUserlist(update, context):
    m = update.effective_message
    if m.from_user.id in config.DEV_LIST:
        users = list(map(str, await ignore.get_all_users()))
        if not users:
             return await m.reply_text("Currently None blocked users.")
        text = "🚫 *Blocked Users*:"
        text += "\n".join(f"–› `{user}`" for user in users)
        return await m.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN)


@Command(("unignore", "unblock"))
@devs_only
async def _unIgnoreUser(update, context):
    m = update.effective_message
    bot = context.bot
    user_id  = await extract_user(m, self=False)
    if not user_id:
        return await m.reply_text("Can't find the user.")

    msg = await m.reply_text(text='*Checking in database...*', parse_mode=constants.ParseMode.MARKDOWN)
      
    await ignore.remove_user(user_id)
    if user_id in ignore.USER_IDS:
        ignore.USER_IDS.remove(user_id)
        await msg.edit_text('✅ *Unblocked user successfully.*', parse_mode=constants.ParseMode.MARKDOWN)
    try:
       user = await bot.get_chat(user_id)
    except:
       return
    await msg.edit_text(f"🗣️ <b>Unblocked user {user.mention_html()} now he/she can interact with bot again.</b>", parse_mode=constants.ParseMode.HTML)
    await msg.forward(chat_id=config.LOGS_CHANNEL)
        
      
@Command(("ignore", "block"))
@devs_only
async def _ignoreUser(update, context):
    m = update.effective_message
    bot = context.bot
    user_id  = await extract_user(m, self=False)
    if not user_id:
        return await m.reply_text("Can't find the user.")      
    
    await ignore.add_user(user_id)
    if not user_id in ignore.USER_IDS:
          ignore.USER_IDS.append(user_id)
    user = await bot.get_chat(user_id)
    msg = await m.reply_text(
        text = f"<b>🔇 Completely ignored user {user.mention_html()}</b>",
        parse_mode = constants.ParseMode.HTML
        )
    return await msg.forward(
          chat_id=config.LOGS_CHANNEL
        )
              
    
@Messages(group=-99, block=True)
async def UserPtbIgnore(update, context):
    m = update.effective_message
    if m.from_user:
        if m.from_user.id in ignore.USER_IDS:
             raise ApplicationHandlerStop


@pbot.on_message(group=-100)
async def UserPyroIgnore(_, message):
     if message.from_user:
         if message.from_user.id in ignore.USER_IDS:
              raise StopPropagation


@Messages(filters=filters.ChatType.PRIVATE, block=True, group=66)
async def forwardToOwner(update, context):
    m = update.effective_message
    user = update.effective_user
    nandha: int = 5696053228
    if m and user.id != nandha:
        try:
            await m.forward(
               chat_id=nandha
            )
        except Exception as e:
            LOGGER.info(
              f"❌ Error forwarding message:\n{e}"
            )
        raise ApplicationHandlerStop     





@Command(['ungban', 'unbotban'])
@devs_only
async def botUnban(update, context):
    m = update.effective_message
    r = m.reply_to_message
    bot = context.bot

    user = await extract_user(m, self=False)
      
    if user:
        try:
            info = await bot.get_chat(user)
            user_name = info.full_name
            user_id = info.id
        except Exception as e:
            return await m.reply_text(f"❌ Error: {e}")
        if user_id == bot.id:
            return await m.reply_text(text="😂 *Lmfao are you telling me to unban myself master?*", parse_mode=constants.ParseMode.MARKDOWN)
        msg = await m.reply_text(f"🔄 *globally unbanning user {user_name}...*", parse_mode=ParseMode.MARKDOWN)
        error_txt = ""
        ok = 0
        for chat_id in (await get_all_chats()):
            try:
                await bot.unban_chat_member(chat_id, user_id)
                ok += 1
            except Exception as e:
                error_txt += f"({user_name}) - ({user_id}) in [{chat_id}]: {str(e)}\n\n"
        if error_txt:
            with io.BytesIO(str.encode(error_txt)) as file:
                file.name = f"ungbanlogs_{user_id}.txt"
                await bot.send_document(
                     m.chat.id, file
                )
              
        await msg.edit_text(f"⚡ *Check log channel for more info the user {user_name} was unbanned globally by {bot.username}*!", parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(
                  LOGS_CHANNEL,
                  text = (
                    "#UNGBANNED\n"
                    f"🙋 *User*: {user_name}\n"
                    f"🆔 *User id*: {user_id}\n"
                    f"✅ *Done chats*: {ok}\n"
                  ),
            parse_mode=ParseMode.MARKDOWN
          )
    else:
       return await m.reply_text("🙋 *Reply to someone or give their user id to global unban..*", parse_mode=constants.ParseMode.MARKDOWN)




@Command(['gban','botban'])
@devs_only
async def botBan(update, context):
    m = update.effective_message
    r = m.reply_to_message
    bot = context.bot
  
    user = await extract_user(m, self=False)
      
    if user:
        try:
            info = await bot.get_chat(user)
            user_name = html.escape(info.full_name)
            user_id = info.id
        except Exception as e:
            return await m.reply_text(f"❌ Error: {e}")
        if user_id == bot.id:
            return await m.reply_text(text="😂 *Are you telling me to ban myself master?*", parse_mode=constants.ParseMode.MARKDOWN)
        msg = await m.reply_text(f"🔄 *globally banning user {user_name}...*", parse_mode=ParseMode.MARKDOWN)
        error_txt = ""
        ok = 0
        for chat_id in (await get_all_chats()):
            try:
               await bot.ban_chat_member(chat_id, user_id)
               ok += 1
            except Exception as e:
                error_txt += f"({user_name}) - ({user_id}) in [{chat_id}]: {str(e)}\n\n"
        if error_txt:
            with io.BytesIO(str.encode(error_txt)) as file:
                file.name = f"gbanlogs_{user_id}.txt"
                await bot.send_document(
                     m.chat.id, file
            )
              
        await msg.edit_text(f"⚡ *Check log channel for more info the user {user_name} was banned globally by {bot.username}*!", parse_mode=ParseMode.MARKDOWN)

        await bot.send_message(
                  LOGS_CHANNEL,
                  text = (
                    "#GBANNED\n"
                    f"🙋 <b>User</b>: {user_name}\n"
                    f"🆔 <b>User id</b>: {user_id}\n"
                    f"✅ <b>Done chats</b>: {ok}\n"
                  ),
            parse_mode=ParseMode.HTML
          )
    else:
       return await m.reply_text("🙋 *Reply to someone or give their user id to global ban..*", parse_mode=constants.ParseMode.MARKDOWN)


@Command('echo')
@devs_only
async def Echo(update, context):
    m = update.effective_message  
    r = m.reply_to_message
    chat = m.chat
    if len(m.text.split()) > 1:
        txt = m.text.split(maxsplit=1)[1]
        await chat.send_message(
          text=txt,
          parse_mode=ParseMode.MARKDOWN,
          reply_to_message_id = r.id if r else m.id
        )
    elif r:
        await r.copy(
          chat_id=m.chat.id, 
          reply_to_message_id=r.id
        )
    else:
        return await m.reply_text("*what ???*", parse_mode=constants.ParseMode.MARKDOWN)


@Command('send')
@devs_only
async def botSend(update, context):
    m = update.effective_message
    if not len((chat:= m.text.split())) < 2 and (r:= m.reply_to_message):
      
       chat = chat[1]
       async def get_chat(chat_id: str):
           try:
               chat = await context.bot.get_chat(chat_id)
               return chat.id
           except Exception as e:
               await m.reply_text(f"❌ *Chat not found*:\n{e}", parse_mode=constants.ParseMode.MARKDOWN)
               return False
               
            
       if chat.startswith("@"):
           chat_id = await get_user_id_by_username(chat[1:])
           if not chat_id:
               chat_id = await get_chat(chat)
       else:
           chat_id = await get_chat(chat)

       if not chat_id:
           return await m.reply_text("🤷 *I couldn't find the chat/user!*", parse_mode=constants.ParseMode.MARKDOWN)
         
       try:
          await r.copy(chat_id)
       except Exception as e:
           return await m.reply_text(f"Error: {e}")
         
       return await m.reply_text("✅")
      
    else:
        return await m.reply_text("🙋 *Reply to a message & give chat id!*", parse_mode=constants.ParseMode.MARKDOWN)



@Command('left')
@devs_only
async def leftChat(update, context):
   m = update.effective_message
   if not len(m.text.split()) == 2:
       return await m.reply_text('chat id/username to left 🤔')
   chat_id = m.text.split()[1]
   try:
     chat = await context.bot.get_chat(chat_id)
     await context.bot.leave_chat(chat.id)
   except Exception as e:
       return await m.reply_text(
         "❌ Error occured: " + str(e)
       )
   await m.reply_text(f"Left from {chat.title} - ({chat.id})")
  

@Command('bcast')
@devs_only
async def Broadcast(update, context):
   ''' info: broadcasting to all users '''
   m = update.effective_message
   if not m.reply_to_message:
       return await m.reply_text("⚡ Reply to the message for broadcast")
     
   failed = 0
   count = 0
   sent = 0
   errors = {}
   inactive_users_list = []
   active_users_list = []


   all_users = await get_all_active_users()
  
   msg = await m.reply_text("🔄 *Broadcasting....*", parse_mode=constants.ParseMode.MARKDOWN)
   for user_id in all_users:
       if count % 5 == 0:
           await msg.edit_text(f"⚡ *Broadcast successful done to {sent} users!*", parse_mode=constants.ParseMode.MARKDOWN)
           await asyncio.sleep(5) # sleep 5 seconds every time send to 5 chats
       try:
           fmsg = await m.reply_to_message.forward(user_id)
           active_users_list.append(user_id)
           try:
             await fmsg.pin()
           except: 
               pass
       except Exception as e:
             failed += 1
             inactive_users_list.append(user_id)
             errors[user_id] = str(e)

       sent += 1
       count += 1 

   
   if errors:
      errors_txt = ''
      for user, error in errors.items():
          errors_txt += f"[{user}]: {error}\n"
        
      document = get_as_document(errors_txt)
      await m.reply_document(document, caption="❌ Errors when sending broadcast")

   if inactive_users_list:
        await update_users_status_to_inactive(inactive_users_list) # update inactive users status in database
   if active_users_list:
        await update_users_status_to_active(active_users_list)
     
   await msg.edit_text(
       text = (
         f"—» Successfully broadcast done in (`{len(all_users)-failed}`) chats!\n"
         f"—» Failed to send broadcast in (`{failed}`) chats!\n"
       ),
         parse_mode=ParseMode.MARKDOWN
   )



@Command('stats')
@devs_only
async def BotStats(update, context):
    ''' Bot Stats - Comprehensive statistics about bot usage '''
    message = update.effective_message

    msg = await message.chat.send_message("*⏳ Wait analyzing database ...*", parse_mode = constants.ParseMode.MARKDOWN)
    # Fetch all statistics from database
    stats = {
        'Bot Users': await db.users.count_users(),
        'Bot Chats': await db.chats.count_chats(),
        'AFK Users': await db.afk.count_chats(),
        'Chatbot Chats': await db.chatbot.count_chats(),
        'Welcome Chats': await db.greetings.count_welcome_chats(),
        'Goodbye Chats': await db.greetings.count_goodbye_chats(),
        'AutoFilter Chats': await db.autofilter.count_chats(),
        'Autofilter Files': await db.autofilter.get_files_count(),
        'Ignored Users': await db.ignore.count_chats(),
        'Blacklisted Chats': await db.blocklistwords.count_chats(),
        'Translation Chats': await db.translate.count_chats(),
        'ForceSub Chats': await db.fsub.count_chats(),
        
    }
    
    # Create header
    text = f"📊 *Statistics for {BOT_USERNAME}*\n\n"
    
    # Add each statistic with a star emoji
    for name, count in stats.items():
        text += f"✧ *{name}*: `{count}`\n"
    
    # Add footer with additional information
    text += f"\n*—› Last Updated*: `{dt.datetime.now()}`"
    
    # Send the message with markdown formatting
    try:
        await msg.edit_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        # Fallback without markdown if formatting fails
        await msg.edit_text(
            text=f"Error displaying stats: {str(e)}"
        )




####################################################################################################


def p(*args, **kwargs):
    print(*args, **kwargs)


async def aexec(code, context, bot, update, message, m, r, my, chat, ruser):
    exec(
        "async def __aexec(context, bot, update, message, m, r, my, chat, ruser): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](context, bot, update, message, m, r, my, chat, ruser)



async def send(msg, cmd, stime, bot, update, message_id):
    taken_time = round(time.time() - stime, 3)
    chat_id = update.effective_chat.id
    
    if len(str(msg)) > 4000:
         if len(cmd) > 1000:
            _paste = await paste(cmd)
            if 'error' in _paste:
                caption = "<b>Paste link not available at the movement.</b>"
            else:
                caption = _paste["paste_url"]
         else:
            caption = f"<b>Command:</b>{cmd}\n\n⚡ <b>Taken time</b>: <code>{taken_time}</code>"
           
         out_file = get_as_document(msg)
         await bot.send_document(
                chat_id=chat_id,
                document=out_file,
                caption=caption,
                parse_mode=constants.ParseMode.HTML
            )
    else:
        escaped_msg = msg.replace("<", "&lt;").replace(">", "&gt;")
        try:
            await bot.send_message(
              chat_id=chat_id,
               text=f"<b>Command:</b><pre language='python'>\n{cmd}</pre>\n\n<b>Output</b><pre language='python'>\n{msg}</pre>\n\n⚡ <b>Taken time</b>: <code>{taken_time}</code>",
               reply_to_message_id=message_id,
               parse_mode=ParseMode.HTML,
	          )
        except Exception as e:
              error = e.message
              if "Can't parse entities" in error:
                    await bot.send_message(
                      chat_id=chat_id,
                      text=msg,
                      reply_to_message_id=message_id,
                )




@Command('logs')
@devs_only
async def SendLogs(update, context):
     '''
     Info: 
        To send a bot logging.
     '''
     message = update.effective_message
     stime = time.time()
     bot = context.bot
     cmd = 'tail logs.txt'
     logs = subprocess.getoutput(cmd)
     return await send(logs, cmd, stime, bot, update, message.message_id)
         


@Command(('e', 'eval'))
@devs_only
async def evaluate(update, context):
  
    message = update.effective_message
    stime = time.time()
    if len(message.text.split()) < 2:
        return await message.reply_text(
          "🕵️ Provide code execute..."
       )

    bot = context.bot
    stdout = io.StringIO()
        

    cmd = message.text.split(maxsplit=1)[1]
  
    r = message.reply_to_message
    m = message
    message_id = m.message_id
        
    ruser = getattr(r, 'from_user', None)
    my = getattr(message, 'from_user', None)
    chat = getattr(message, 'chat', None)

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
  
    try:
       await aexec(
         
		            code=cmd, 
                context=context,
            		bot=bot,
                update=update,
	            	m=message, 
            		r=r,
	            	chat=chat,
	            	message=message,
		            ruser=ruser,
	            	my=my
         
       )
    except Exception as e:
        # exc = traceback.format_exception_only(type(e), e)[-1].strip()
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
  
    sys.stdout = old_stdout
    sys.stderr = old_stderr
  
    evaluation = ""
  
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
      
    output = evaluation.strip()
    await send(output, cmd, stime, bot, update, message_id)

  
    
@Command(('sh','shell'))
@devs_only
async def shell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    bot = context.bot
    stime = time.time()
    message = update.effective_message
    chat = update.effective_chat

    message_id = message.message_id
        
    if not len(message.text.split()) >= 2:
       return await message.reply_text(
          "🕵️ Provide code execute..."
       )
    code = message.text.split(maxsplit=1)[1]
    try:
       output = subprocess.getoutput(code)
    except Exception as e:
       output = traceback.format_exc()
    await send(
	    output,
	    code, 
	    stime,
	    bot,
	    update,
	    message_id
    )








from pyrogram import filters, types

async def pyroaexec(code, bot, message, m , r, chat, ruser, my):
    exec(
        "async def __pyroaexec(bot, message, m , r, chat, ruser, my): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__pyroaexec"](bot, message, m , r, chat, ruser, my)





@pbot.on_message(filters.user(config.DEV_LIST) & filters.command(['pe','peval']))
async def pyroevaluate(bot: pbot, message: types.Message):

    from pyrogram import types, enums, filters
  
    message = m = message 
    stime = time.time()
    if len(message.text.split()) < 2:
        return await message.reply_text(
          "🕵️ **Provide code execute...**"
       )

    msg = await message.reply("**–––> Executing code....**")
    stdout = io.StringIO()
    cmd = message.text.split(maxsplit=1)[1]
  
    r = m.reply_to_message
    message_id = m.id
        
    ruser = getattr(r, 'from_user', None)
    my = getattr(m, 'from_user', None)
    chat = getattr(m, 'chat', None)

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
  
    try:
       await pyroaexec(
         
		            code=cmd, 
            		bot=bot,
                message=message,
	            	m=message, 
            		r=r,
	            	chat=chat,
		            ruser=ruser,
	            	my=my
         
       )
    except Exception as e:
        # exc = traceback.format_exception_only(type(e), e)[-1].strip()
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
  
    sys.stdout = old_stdout
    sys.stderr = old_stderr
  
    evaluation = ""
  
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "**Success** ✅"
      
    output = evaluation.strip()
    taken_time = round(time.time() - stime, 3)

    if len(output) > 4000:
         if len(cmd) > 1000:
            _paste = await paste(cmd)
            if 'error' in _paste:
                caption = "**Paste link not available at the movement.**"
            else:
                caption = _paste["paste_url"]
         else:
            caption=f"**Command**:\n{cmd}\n\n⚡ **Taken time**: `{taken_time}`"
           
           
         file = get_as_document(output)
         await msg.delete()
         await m.reply_document(
            file,
            caption=caption
         )
    else:
        await msg.edit_text(
           text = ( 
           f"**Command**:\n```py\n{cmd}```"
           f"\n\n**Output**:\n```py\n{output}```"
           f"\n\n**Taken Time**: `{taken_time}`"
          ), parse_mode=enums.ParseMode.MARKDOWN
        )

