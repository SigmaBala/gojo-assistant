
import time
import asyncio
import html
import os

from telegram.ext import ContextTypes, CallbackContext, filters
from telegram import Update, error, ChatPermissions, constants, ChatMemberOwner, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.helpers import mention_html, escape_markdown, mention_markdown
from pyrogram import filters, Client, types as pyro_types, enums as pyro_enums
from nandha.helpers.utils import extract_user, get_message_link
from nandha.helpers.decorator import Command, admin_check, only_groups
from nandha import BOT_ID, pbot

__module__ = 'Admin'

__help__ = '''
*Commands*:
/invite, /adminlist, /del,
/pin, /unpin, /purge, /kick,
/promote, /demote, /ban, /unban,
/mute, /unmute, /zombies, /warn
/setct, /setcdes, /setcp, /rmcp,
/report

```
/invite: chat invite link.
/adminlist: admins in chat.
/del: delete msg.
/pin or /unpin: pin or unpin a message in the chat.
/purge: delete all messages from the replied message onward.
/kick or /dkick: kick a member from the group.
/promote or lowpromote or fullpromote: promote a member to admin in the chat.
/demote; demote an admin to a regular member.
/ban or /dban: ban a user or channel from the group.
/unban: revoke a ban on a user or channel.
/mute or /dmute: restrict a member ability to send messages ( muted ).
/unmute: revoke muted person to again talk.
/warn or /dwarn: warn a user in group ( dummy cmd ).
/zombies clean: it will remove deleted accounts from chat.
/setct: update chat title.
/setcdes: set chat description.
/setcp: set chat photo.
/rmcp: remove chat photo.
/report: to admins in group.
```
'''



@pbot.on_message(
    (filters.command(["report", "reportar"]) | filters.regex("^@admin(s)?"))
    & filters.group
    & filters.reply & ~filters.forwarded
)
async def ReportAdmins(c: Client, m: pyro_types.Message):
    if not m.reply_to_message.from_user:
        return

    check_admin = await m.chat.get_member(m.reply_to_message.from_user.id)

    ADMIN_STATUSES = (
      pyro_enums.ChatMemberStatus.OWNER,
      pyro_enums.ChatMemberStatus.ADMINISTRATOR,
    )
      
    mention = ""
    async for i in m.chat.get_members(filter=pyro_enums.ChatMembersFilter.ADMINISTRATORS):
        if not (i.user.is_deleted or i.privileges.is_anonymous or i.user.is_bot):
            mention += f"<a href='tg://user?id={i.user.id}'>\u2063</a>"
    await m.reply_to_message.reply_text(
        
"{admins_list}{reported_user} Reported to the admins.".format(
            admins_list=mention,
            reported_user=m.reply_to_message.from_user.mention(),
        ),
    )



@Command(
['setcdes', 'setchatdes']
)
@admin_check('can_change_info')
@only_groups
async def setChatDescription(update, context):
      m = update.effective_message
      bot = context.bot
      description = ' '.join(context.args)
      if not description:
         return await m.reply_text(
            '✋ *Provide some text to set it as chat description*. e.g: `/setcdes Support Chat`',
            parse_mode=constants.ParseMode.MARKDOWN
         )
            
      try:
          await bot.set_chat_description(m.chat.id, description[:254])
          await m.reply_text('✨ *Chat Description Updated!*', parse_mode=constants.ParseMode.MARKDOWN)
      except Exception as e:
         return await m.reply_text('❌ Error: {}'.format(str(e)))
            

@Command(
['setct', 'setchattitle']
)
@admin_check('can_change_info')
@only_groups
async def setChatTitle(update, context):
      m = update.effective_message
      bot = context.bot
      title = ' '.join(context.args)
      if not title:
         return await m.reply_text(
            '✋ *Provide some text to set it as chat title*. e.g: `/setct Support Chat`',
            parse_mode=constants.ParseMode.MARKDOWN
         )
            
      try:
         await bot.set_chat_title(m.chat.id, title[:127])
         await m.reply_text('✨ *Chat title Updated!*', parse_mode=constants.ParseMode.MARKDOWN)
      except Exception as e:
         return await m.reply_text('❌ Error: {}'.format(str(e)))
            

@Command(
['rmcp', 'rmchatphoto']
)
@admin_check('can_change_info')
@only_groups
async def removeChatPhoto(update, context):
      m = update.effective_message
      bot = context.bot
      try:
         await bot.delete_chat_photo(m.chat.id)
         await m.reply_text(
               '*✨ Chat Photo Removed!*',
               parse_mode=constants.ParseMode.MARKDOWN
)
      except Exception as e:
         return await m.reply_text('❌ Error: {}'.format(str(e)))



@Command(
['setcp', 'setchatphoto']
)
@admin_check('can_change_info')
@only_groups
async def setChatPhoto(update, context):
      m = update.effective_message
      bot = context.bot
      if m.reply_to_message and m.reply_to_message.photo:
           file = await bot.get_file(m.reply_to_message.photo[-1])
           photo_path = await file.download_to_drive()
           try:
              await bot.set_chat_photo(m.chat.id, photo=photo_path)
              await m.reply_text('*✨ New photo has been updated!*', parse_mode=constants.ParseMode.MARKDOWN)
           except Exception as e:
              return await m.reply_text('❌ Error: {}'.format(str(e)))
           finally:
              os.remove(photo_path)
      else:
          return await m.reply_text('✋ Reply to photo !')



@Command(
["warn", "dwarn"]
)
@admin_check('can_restrict_members')
@only_groups
async def warnings(update, context):
      m = update.effective_message
      reply = m.reply_to_message
      user_id = await extract_user(m, self=False)
      
      command = m.text.split()[0][1:].lower()
      if command.startswith("d"):
            try:
               if reply:
                  await reply.delete()
                  await m.delete()
            except:
               pass
                  
      if not user_id:
          return await m.chat.send_message("*User not found! specific a user!*", parse_mode=constants.ParseMode.MARKDOWN)
          
      member =  await m.chat.get_member(user_id)
      await m.chat.send_message(
              text=f"<b>Hey {member.user.mention_html()}</b>, <code>You have been warned, don't do that again or i will ban you! ⚠️</code>",
              parse_mode=constants.ParseMode.HTML
      )
      

@Command('zombies')
@admin_check('can_restrict_members')
@only_groups
async def zombiesFire(update, context):
       ''' clean deleted accounts from chat '''
       m = update.effective_message
       chat_id = m.chat.id
       chat = m.chat
       users = []

       msg = await m.reply_text("Checking for Zombies ...")
       async for member in pbot.get_chat_members(chat_id):
            if member.user.is_deleted:
                 users.append(member.user.id)        
            else:
               continue

       if len(m.text.split()) < 2:
            return await msg.edit_text(
                  f"<b>Currently {len(users)} Zombies in this chat, do you want kill them? usage:</b><code>/zombies clean</code>",
                    parse_mode=constants.ParseMode.HTML
           )
       elif not users:
            return await msg.edit_text("😉 <b>No Zombies in the chat.</b>", parse_mode=constants.ParseMode.HTML)

       else:
           pattern = m.text.split()[1].lower()
           if pattern != "clean":
                return await msg.edit_text("<b>Its 'clean' buddy isn't it?</b>", parse_mode=constants.ParseMode.HTML)
           else:
               done = 0
               fail = 0
               for user_id in users:
                  try:
                     service = await m.chat.ban_member(user_id)
                     done += 1
                  except Exception as e:
                     fail += 1
                                    
               text = f"⚔️ <b>Killed {done} Zombies in {html.escape(chat.title)}</b> "
               if fail != 0:
                   text += f"<b>and {fail} Zombies are escaped!</b>"
                   
               return await msg.edit_text(
                     text,
                     parse_mode=constants.ParseMode.HTML
               )



@Command('demote')
@admin_check('can_promote_members')
@only_groups
async def demoteChatMember(update, context):
       '''
       Info:
          - Demote Chat Admin
       '''
  
       message = update.effective_message
       bot = context.bot
       reply = message.reply_to_message
       user_id = await extract_user(message, self=False)
  
       if not user_id: 
          return await message.reply_text(
              text="🙋 *Reply to a user or give their telegram ID!*",
              parse_mode=constants.ParseMode.MARKDOWN
            )

       
       
       permissions = (await bot.get_my_default_administrator_rights()).to_dict()
       command = message.text.split()[0][1:].lower()
  
       try:
          member = await message.chat.get_member(user_id)
          mention = mention_html(member.user.id, member.user.first_name)
          await message.chat.promote_member(
             member.user.id, permissions
             )
       except Exception as e:
           return await message.reply_text(
             text="❌ Error: " + str(e)
           )
  
       await message.reply_text(
            text=f"<b>Successfully {command}d {'bot' if member.user.is_bot else 'user'} {mention}!</b>",
            parse_mode=constants.ParseMode.HTML
       )
        

@Command(('promote', 'fullpromote', 'lowpromote'))
@admin_check('can_promote_members')
@only_groups
async def promoteChatMember(update, context):
       '''
       Info:
          - Promote Chat Member
       '''
  
       message = update.effective_message
       
       reply = message.reply_to_message
       user_id = await extract_user(message, False)
  
       if not user_id: return await message.reply_text(
              text="🙋 *Reply to a user or give their telegram ID!*",
              parse_mode=constants.ParseMode.MARKDOWN
            )
         
       permissions = {}
       command = message.text.split()[0][1:].lower()
  
       if command == 'lowpromote':
            user_permission = {
                'can_invite_users': True,
                'can_pin_messages': True
                }
            permissions.update(user_permission)
         
       elif command == 'promote':
              user_permission = {
                'can_invite_users': True,
                'can_pin_messages': True,
                'can_delete_messages': True,
                'can_restrict_members': True,
                'can_manage_video_chats': True
              }  
              permissions.update(user_permission)
         
       else:
           status = await message.chat.get_member(BOT_ID)
           user_permission = {
            'can_change_info': status.can_change_info,
            'can_delete_messages': status.can_delete_messages, 
            'can_delete_stories': status.can_delete_stories, 
            'can_edit_stories': status.can_edit_stories,
            'can_invite_users': status.can_invite_users, 
            'can_manage_chat': status.can_manage_chat, 
            'can_restrict_members': status.can_manage_chat,
            'can_manage_topics': status.can_manage_topics,
            'can_manage_video_chats': status.can_manage_video_chats, 
            'can_pin_messages': status.can_pin_messages,
            'can_post_stories': status.can_post_stories,
            'can_promote_members': status.can_promote_members, 
            'is_anonymous': status.is_anonymous
            }
           permissions.update(user_permission)

       try:
          member = await message.chat.get_member(user_id)
          mention = mention_html(member.user.id, member.user.first_name)
          await message.chat.promote_member(
             member.user.id, **permissions
             )
       except Exception as e:
           return await message.reply_text(
             text="❌ Error: " + str(e)
           )
  
       await message.reply_text(
            text=f"<b>Successfully {command}d {'bot' if member.user.is_bot else 'user'} {mention}!</b>",
            parse_mode=constants.ParseMode.HTML
       )


  


@Command(('pin', 'unpin'))
@admin_check('can_pin_messages')
@only_groups
async def PinChatMsg(update, context):

      '''
      Info:
         pin or unpin a message in chat!
         
      '''
      message = update.effective_message
      reply = message.reply_to_message
      if not reply: return await message.reply_text("🤷 Reply to message!")
        
      command = message.text.split()[0][1:] 
  
      if command == 'pin':
          await reply.pin()
      else:
          await reply.unpin()
        
      link = get_message_link(reply)
  
      await message.reply_text(
       text=f"<b>Successfully <a href='{link}'>Message</a> {command.capitalize()}ed!</b>",
       parse_mode=constants.ParseMode.HTML
)
            

@Command(['invite','invitelink', 'grouplink'])
@admin_check('can_invite_users')
@only_groups
async def GetInvite(update, context):
    message = update.effective_message
    bot = context.bot
    chat = await bot.get_chat(message.chat.id)
    link = chat.invite_link
    await message.reply_text(
        text=f"<b>✨ {chat.title} Invite Link</b>:\n{link}",
        parse_mode=constants.ParseMode.HTML
    )
    
  
@Command('purge')
@admin_check('can_delete_messages')
async def PurgeMsg(update, context):
     message = update.message
     reply = message.reply_to_message
     bot = context.bot
   
     if not reply: return await message.reply_text(
            "*Reply to a message for start purge!*",
            parse_mode=constants.ParseMode.MARKDOWN
     )
       
     reply_message_id = reply.id
     message_id = message.id
     message_ids = list(range(reply_message_id, message_id + 1))
     total_msg_count = len(message_ids)
     start = time.perf_counter()
  
     if len(message_ids) > 300: return await message.reply_text("*You cannot delete more than 300 messages at once! but try 299 🧏*", parse_mode=constants.ParseMode.MARKDOWN)

     errors = []
     while message_ids:
         msg_count = 100 if len(message_ids) > 100 else len(message_ids)
         msg_ids = message_ids[:msg_count]
         try:
           await bot.delete_messages(
             chat_id=message.chat.id,
             message_ids=msg_ids
           )
         except Exception as e:
             errors.append(str(e))
         del message_ids[:len(msg_ids)]
     
     ping = round(time.perf_counter() - start, 3)
  
     errors_str = ""
     for error in errors:
         errors_str += error
     errors_msg = f"\n\n❌ Errors: {errors_str}" if errors_str else ""
  
     msg = await bot.send_message(
          chat_id=message.chat.id,
          text=f"`Successfully deleted {total_msg_count - len(message_ids)} within {ping}(s)`.",
          parse_mode=constants.ParseMode.MARKDOWN
         )
     if errors_msg:
          return await message.reply_text(errors_msg)
     await asyncio.sleep(5)
     await msg.delete()




@Command('unban')
@admin_check('can_restrict_members')
@only_groups
async def UnBanChatMember(update, context):
    message = update.effective_message
    reply = message.reply_to_message
    chat = message.chat
    user = message.from_user
    bot = context.bot
    
    if getattr(reply, 'sender_chat', None):
        sender_chat = reply.sender_chat
        try:
           success = await bot.unban_chat_sender_chat(
               chat_id=chat.id,
               sender_chat_id=sender_chat.id
        )
           if success:
                return await message.reply_text(
text=(
f"""
<b>⚡ Channel {sender_chat.title} UnBanned in {chat.title}.</b>
"""), parse_mode=constants.ParseMode.HTML
            )
        except TelegramError as e:
            return await message.reply_text(
              text=f"❌ Error: {str(e)}"
        )

            
               
    user_id = await extract_user(message)
  
    if not user_id or user_id == user.id:
        return await message.reply_text(
           "Reply to a user or provide their id / mention to UnBan !"
        )
      
    try:
      
        member = await bot.get_chat_member(chat.id, user_id)
      
        success = await bot.unban_chat_member(
             chat_id=chat.id,
             user_id=member.user.id
        )
        if success:
            member_mention = mention_html(member.user.id, member.user.first_name)
            return await message.reply_text(
text=(
f"""
<b>⚡ {'Bot' if member.user.is_bot else 'User'} {member_mention} UnBanned in {chat.title}.</b>
"""), parse_mode=constants.ParseMode.HTML
            )
    except error.TelegramError as e:
        return await message.reply_text(
          text=f"❌ Error: {str(e)}"
        )



@Command(('mute', 'dmute'))
@admin_check('can_restrict_members')
@only_groups
async def MuteChatMember(update, context):
    message = update.effective_message
    reply = message.reply_to_message
    chat = message.chat
    user = message.from_user
    bot = context.bot
    
    if getattr(reply, 'sender_chat', None): return
               
    user_id = await extract_user(message, False)
  
    if not user_id:
        return await message.reply_text(
           "Reply to a user or provide their id / mention to Mute !"
        )
      
    try:
        command = message.text.split()[0][1:].lower()
        if command.startswith("d"):
            try:
                if reply:
                   await reply.delete()
                await message.delete()
            except:
               pass
                  
        member = await bot.get_chat_member(chat.id, user_id)
        permissions = ChatPermissions.no_permissions()
        success = await bot.restrict_chat_member(
             chat_id=chat.id,
             user_id=member.user.id,
             permissions=permissions
        )
        if success:
            member_mention = mention_html(member.user.id, member.user.first_name)
            button = InlineKeyboardMarkup([[
              InlineKeyboardButton('🙋 UnMute!', callback_data=f"unmute_{user_id}"),
              InlineKeyboardButton('❌ Delete!', callback_data=f"delete#{user.id}")
            ]])
            return await chat.send_message(
              text=f"""<b>⚡ {'Bot' if member.user.is_bot else 'User'} {member_mention} Muted in {chat.title}.</b>""",
              parse_mode=constants.ParseMode.HTML,
              reply_markup=button          
            )
    except error.TelegramError as e:
        return await message.reply_text(
          text=f"❌ Error: {str(e)}"
        )


@Command('unmute')
@admin_check('can_restrict_members')
@only_groups
async def UnMuteChatMember(update, context):
    message = update.effective_message
    reply = message.reply_to_message
    chat = message.chat
    user = message.from_user
    bot = context.bot
    
    if getattr(reply, 'sender_chat', None): return
               
    user_id = await extract_user(message)
  
    if not user_id or user_id == user.id:
        return await message.reply_text(
           "Reply to a user or provide their id / mention to UnMute !"
        )
      
    try:
      
        member = await bot.get_chat_member(chat.id, user_id)
        permissions = ChatPermissions.all_permissions()
        success = await bot.restrict_chat_member(
             chat_id=chat.id,
             user_id=member.user.id,
             permissions=permissions
        )
        if success:
            member_mention = mention_html(member.user.id, member.user.first_name)
            return await message.reply_text(
              text=f"""<b>⚡ {'Bot' if member.user.is_bot else 'User'} {member_mention} UnMuted in {chat.title}.</b>""",
              parse_mode=constants.ParseMode.HTML          
            )
    except error.TelegramError as e:
        return await message.reply_text(
          text=f"❌ Error: {str(e)}"
        )


@Command(('ban', 'dban'))
@admin_check('can_restrict_members')
@only_groups
async def BanChatMember(update, context):
    message = update.effective_message
    reply = message.reply_to_message
    chat = message.chat
    user = message.from_user
    bot = context.bot

    command = message.text.split()[0][1:].lower()
    if command.startswith("d"):
         try:
            if reply:
               await reply.delete()
            await message.delete()
         except:
            pass
                
    if reply and getattr(reply, 'sender_chat', None):
        sender_chat = reply.sender_chat
        try:
           success = await bot.ban_chat_sender_chat(
               chat_id=chat.id,
               sender_chat_id=sender_chat.id
        )
           if success:
                return await chat.send_message(
                   text=(f"""<b>⚡ Channel {sender_chat.title} Banned in {chat.title}.</b>"""), 
                   parse_mode=constants.ParseMode.HTML,
          
         
            )
        except TelegramError as e:
            return await chat.send_message(
              text=f"❌ Error: {str(e)}"
        )

            
               
    user_id = await extract_user(message, self=False)
  
    if not user_id:
        return await chat.send_message(
           "Reply to a user or provide their id / mention to BAN from group!"
        )
      
    try:
      
        member = await bot.get_chat_member(chat.id, user_id)
      
        success = await bot.ban_chat_member(
             chat_id=chat.id,
             user_id=member.user.id
        )
        if success:
            member_mention = mention_html(member.user.id, member.user.first_name)
            button = InlineKeyboardMarkup([[
              InlineKeyboardButton('🙋 Unban!', callback_data=f"unban_{user_id}"),
              InlineKeyboardButton('❌ Delete!', callback_data=f"delete#{user.id}")
            ]])
            return await chat.send_message(
              text=f"""<b>⚡ {'Bot' if member.user.is_bot else 'User'} {member_mention} Banned in {chat.title}.</b>""",
              parse_mode=constants.ParseMode.HTML,
              reply_markup=button          
            )
    except error.TelegramError as e:
        return await chat.send_message(
            text=f"❌ ERROR: {str(e)}"
        )

@Command(('kick', 'punch', 'dkick', 'dpunch'))
@admin_check('can_restrict_members')
@only_groups
async def BanChatMember(update, context):
    message = update.effective_message
    reply = message.reply_to_message
    chat = message.chat
    user = message.from_user
    bot = context.bot

    command = message.text.split()[0][1:].lower()
    if command.startswith("d"):
          try:
              if reply:
                  await reply.delete()
              await message.delete()
          except:
              pass
    
    if reply and getattr(reply, 'sender_chat', None):
        sender_chat = reply.sender_chat
        try:
           await bot.ban_chat_sender_chat(
               chat_id=chat.id,
               sender_chat_id=sender_chat.id
        )
           await bot.unban_chat_sender_chat(
               chat_id=chat.id,
               sender_chat_id=sender_chat.id
           )
          
           return await chat.send_message(
                text=f"<b>⚡ Channel {sender_chat.title} Kicked in {chat.title}.</b>", 
                  parse_mode=constants.ParseMode.HTML
            )
        except TelegramError as e:
            return await message.reply_text(
              text=f"❌ ERROR: {str(e)}"
        )

            
               
    user_id = await extract_user(message, self=False)
  
    if not user_id:
        return await chat.send_message(
           "Reply to a user or provide their id / mention to KICK from group!"
        )
      
    try:
      
        member = await bot.get_chat_member(chat.id, user_id)
      
        success = await bot.ban_chat_member(
             chat_id=chat.id,
             user_id=member.user.id
        )
        await bot.unban_chat_member(
             chat_id=chat.id,
             user_id=member.user.id
        )
        if success:
            member_mention = mention_html(member.user.id, member.user.first_name)
            return await chat.send_message(
                 text=(f"""<b>⚡ {'Bot' if member.user.is_bot else 'User'} {member_mention} Kicked in {chat.title}.</b>"""), parse_mode=constants.ParseMode.HTML
            )
    except error.TelegramError as e:
        return await chat.send_message(
          text=f"❌ ERROR: {str(e)}"
        )


@Command(('adminlist','admins'))
@admin_check()
@only_groups
async def AdminList(update, context):
    message = update.effective_message
    chat = message.chat

    msg = await message.reply_text("⚡ Fetching Admins...")
    try:
        admins = await chat.get_administrators()
    except error.TelegramError as e:
        return await msg.edit_text(
            text=f"❌ Error: {str(e)}"
        )      

    owner = next((mem for mem in admins if isinstance(mem, ChatMemberOwner)), None)
      
    if owner:
        text = f"🧑‍✈️ <b>Staff's in {chat.title}</b>:\n\n👑 <b>Owner</b>: {mention_html(owner.user.id, owner.user.first_name)}\n\n👮 <b>Admins</b>:\n\n"
    else:
        text = f"👮 <b>Admins in {chat.title}</b>:\n\n"


    for mem in admins:
        if isinstance(mem, ChatMemberOwner):
             continue
        text += f"➣ <b>{mention_html(mem.user.id, mem.user.first_name)}</b>\n"

    return await msg.edit_text(
        text=text,
        parse_mode=constants.ParseMode.HTML
    )
  


@Command('del')
@admin_check('can_delete_messages')
async def delete_msg(update, context):
    message = update.effective_message
    reply = message.reply_to_message
    if reply:
        try:
            await reply.delete()
            await message.delete()
        except error.TelegramError as e:
            return await message.reply_text("❌ Error: {}".format(e))
    else:
        return await message.reply_text("What should I delete?")
