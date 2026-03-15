


import asyncio, sys

from typing import Union
from functools import wraps
from telegram import ChatMemberOwner, ChatMemberAdministrator, constants, CallbackQuery, helpers, Update
from telegram.ext import CommandHandler, ChatMemberHandler, MessageHandler, PrefixHandler, CallbackQueryHandler, filters
from nandha import app, DEV_LIST, BOT_ID, BOT_USERNAME, PREFIX, SPAM_USERS, PREMIUM_USERS

import pyrogram



def only_premium(func): # premium user's gojo subscriptions
    async def wrapper(client, *args, **kwargs):
        if isinstance(client, Update):  # PTB
            user = client.effective_user
            message = client.effective_message
        elif isinstance(client, pyrogram.Client):  # Pyrogram
            message = args[0]
            user = message.from_user
        else:
            return  # Unsupported update type

        if not user.id in PREMIUM_USERS:
            return await message.reply_text("⚠️ This command only work for 'Gojo Premium' Users!")
        
        else:
            return await func(client, *args, **kwargs)
        
    return wrapper


def unavailable(func):
    async def wrapper(client, *args, **kwargs):
        if isinstance(client, Update):  # PTB
            user = client.effective_user
            message = client.effective_message
        elif isinstance(client, pyrogram.Client):
            message = args[0]
            user = message.from_user
        else:
            return  # Unsupported update type

        if not user.id in DEV_LIST:
            return await message.reply_text('⚠️ This command is temporarily unavailable for everyone!')
        
        else:
            return await func(client, *args, **kwargs)
        
    return wrapper


def spam_control(func):
    async def wrapper(client, *args, **kwargs):
        if isinstance(client, Update):  # PTB
            user = client.effective_user
            message = client.effective_message
        elif isinstance(client, pyrogram.Client):  # Pyrogram
            message = args[0]
            user = message.from_user
        else:
            return  # Unsupported update type

        if SPAM_USERS.get(user.id, None):
            return await message.reply_text('⚠️ Wait!, Don\'t spam commands!')

        SPAM_USERS[user.id] = True  # Mark user as spamming

        try:
            # Execute the original function
            return await func(client, *args, **kwargs)
        finally:
            # Ensure the user is removed from the spam list after execution
            SPAM_USERS.pop(user.id, None)

    return wrapper




prefix_cmds = ['!', '?', '$', '/', '\\']


def Command(command, filters= None, block = False):
    def decorator(func):
        if PREFIX:
            
            def convert(cmd: Union[str, list]):
                if isinstance(cmd, tuple):
                    cmd = list(cmd)
                if not isinstance(cmd, (str, list)):
                    print(f"Wrong command data type detected: {cmd} and ignored!!")
                    return
                commands = [cmd] if isinstance(cmd, str) else cmd
                return [f"{c}{BOT_USERNAME}" for c in commands] + commands
                
            handler = PrefixHandler(
                  prefix=prefix_cmds,
                  command=convert(command),
                  callback=func, 
                  filters=filters, 
                  block=block
                  )
        else:
            
            handler = CommandHandler(
                  command=command,
                  callback=func, 
                  filters=filters, 
                  block=block
        )
        app.add_handler(handler)
        return func
    return decorator


def Callbacks(pattern, block = True):
   def decorator(func):
         handler = CallbackQueryHandler(
              callback=func, pattern=pattern,
              block=block
         )
         app.add_handler(handler)
         return func
   return decorator



def Messages(filters=None, group = 0, block = False):
   def decorator(func):
         handler = MessageHandler(
              callback=func,
              filters=filters,
              block=block
         )
         app.add_handler(handler, group=group)
         return func
   return decorator


def ChatMembers(chat_member_types = -1, group = 0, block = True):
   def decorator(func):
         handler = ChatMemberHandler(
              callback=func,
              chat_member_types=chat_member_types,
              block=block
         )
         app.add_handler(handler, group=group)
         return func
   return decorator
  


def only_private(func):
      async def wrapper(update, context):
           msg = update.effective_message
           if msg.chat.type != constants.ChatType.PRIVATE:
                await msg.reply_text("This command only work in private!")
                return
           return await func(update, context)
      return wrapper


def with_args(value: int = 1):
     def decorator(func):
         async def wrapper(update, context):
                args = context.args
                if len(args) != value:
                     await m.reply_text(f"🙋‍♂️ Not enough argument please provide {value}!")            
                else: 
                     return await func(update, context)
         return wrapper
     return decorator
                



def devs_only(func):
    """ Only Devs can access the command! """
  
    async def wrapper(update, context, *args, **kwargs):
        message = update.effective_message
        if (getattr(message, 'from_user') is not None) and message.from_user.id in DEV_LIST:
             return await func(update, context, *args, **kwargs)
    return wrapper


def only_users(users: list = []):
     def decorator(func):
          async def wrapper(update, context):
               user = update.effective_user
               if user.id in users:
                    return await func(update, context)
          return wrapper
     return decorator


def only_groups(func):
      async def wrapper(update, context):
           msg = update.effective_message
           if msg.chat.type not in (constants.ChatType.GROUP, constants.ChatType.SUPERGROUP):
                await msg.reply_text("This command only work in groups!")
                return
           return await func(update, context)
      return wrapper
 



def admin_check(permission: str = None):
    """ check for members admin permission """
  
    def decorator(func):
        async def wrapper(update, context, *args, **kwargs):
            chat = update.effective_chat
            user = update.effective_user
            message = update.effective_message

            if getattr(update, 'callback_query', None):
                query = update.callback_query

                async def send_response(text):
                    await query.answer(text, show_alert=True)
            else:
                async def send_response(text):
                    text = helpers.escape_markdown(text)
                    await message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN)

            if message.chat.type == constants.ChatType.PRIVATE:
                  return await func(update, context, *args, **kwargs)
              
            elif getattr(message, 'sender_chat', None):
                  return await message.reply_text("You cannot access this command!")

            user_member = await chat.get_member(user.id)
            bot_member = await chat.get_member(context.bot.id)
                

            if bot_member.status not in [constants.ChatMemberStatus.ADMINISTRATOR, constants.ChatMemberStatus.OWNER]:
                await send_response("The bot is not an admin in this chat.")
                return
 
            if (user_member.status not in [constants.ChatMemberStatus.ADMINISTRATOR, constants.ChatMemberStatus.OWNER]) and (not user.id in DEV_LIST):
                return await send_response("You are not an admin in this chat.")

            
            if (permission and not isinstance(user_member, ChatMemberOwner)) and (not user.id in DEV_LIST):
                if not getattr(user_member, permission, False):
                    return await send_response(f"You are missing the {permission} permission.")
                    
                if not getattr(bot_member, permission, False):
                    return await send_response(f"The bot is missing the {permission} permission.")
                    

            return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator
    
        

# send_typing_action = send_action(ChatAction.TYPING)
# send_upload_video_action = send_action(ChatAction.UPLOAD_VIDEO)
# send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            bot = context.bot
            chat = update.effective_chat
            
            await bot.send_chat_action(
                chat_id=chat.id,
                action=action
            )
            
            return await func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator
